#!/usr/bin/env python3
"""Lints a Minecraft Java datapack against the real command tree of one game version.

Usage:  python tools/lint.py <pack_dir> [<pack_dir> ...] [--version 26.3]

The command tree and the registries come from the misode/mcmeta repository
(summary branch for the given version). They are cached in tools/.cache/.

What is checked
  * every command line is walked against the real Brigadier tree (literals, argument counts,
    argument types, executable end nodes, redirects such as `execute ... run <command>`)
  * SNBT payloads (components, items, selectors' nbt, text components) are parsed
  * house rules: fake players start with '#', SNBT booleans are 1b/0b (never true/false),
    macro variables are never nested, comments and in-game text are plain ASCII English
  * scoreboard objectives used by commands are declared in the same pack
  * every `function ns:path` target exists, tag files point at existing functions
  * pack.mcmeta and all .json files parse
Macro lines ($...) are checked with $(var) replaced by a wildcard token.
"""
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
RAW = "https://raw.githubusercontent.com/misode/mcmeta/{v}-summary/{f}/data.json"


def load_ref(version):
    os.makedirs(CACHE, exist_ok=True)
    out = {}
    for key, folder in (("tree", "commands"), ("reg", "registries")):
        path = os.path.join(CACHE, f"{version}-{key}.json")
        if not os.path.exists(path):
            with urllib.request.urlopen(RAW.format(v=version, f=folder), timeout=60) as r:
                data = r.read()
            with open(path, "wb") as fh:
                fh.write(data)
        with open(path, encoding="utf-8") as fh:
            out[key] = json.load(fh)
    return out["tree"], out["reg"]


# --------------------------------------------------------------------------- SNBT
class SNBTError(Exception):
    pass


class SNBT:
    BARE = re.compile(r"[A-Za-z0-9_.+\-]+")

    def __init__(self, s):
        self.s, self.i = s, 0
        self.flags = []

    def ws(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def parse(self):
        v = self.value()
        self.ws()
        if self.i != len(self.s):
            raise SNBTError(f"trailing data at {self.i}: {self.s[self.i:self.i + 20]!r}")
        return v

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else ""

    def string(self):
        q = self.s[self.i]
        self.i += 1
        out = []
        while self.i < len(self.s):
            c = self.s[self.i]
            if c == "\\":
                self.i += 2
                out.append("?")
                continue
            if c == q:
                self.i += 1
                return "".join(out)
            out.append(c)
            self.i += 1
        raise SNBTError("unterminated string")

    def value(self):
        self.ws()
        c = self.peek()
        if c == "{":
            return self.compound()
        if c == "[":
            return self.lst()
        if c in "\"'":
            return ("str", self.string())
        m = self.BARE.match(self.s, self.i)
        if not m:
            raise SNBTError(f"unexpected {c!r} at {self.i}")
        self.i = m.end()
        tok = m.group(0)
        if tok in ("true", "false"):
            self.flags.append(f"boolean literal '{tok}' (use 1b/0b)")
        return ("bare", tok)

    def compound(self):
        self.i += 1
        d = {}
        self.ws()
        if self.peek() == "}":
            self.i += 1
            return ("compound", d)
        while True:
            self.ws()
            if self.peek() in "\"'":
                k = self.string()
            else:
                m = self.BARE.match(self.s, self.i)
                if not m:
                    raise SNBTError(f"bad key at {self.i}")
                self.i = m.end()
                k = m.group(0)
            self.ws()
            if self.peek() != ":":
                raise SNBTError(f"expected ':' after key {k!r} at {self.i}")
            self.i += 1
            d[k] = self.value()
            self.ws()
            c = self.peek()
            self.i += 1
            if c == "}":
                return ("compound", d)
            if c != ",":
                raise SNBTError(f"expected ',' or '}}' at {self.i - 1}")

    def lst(self):
        self.i += 1
        items = []
        self.ws()
        # typed arrays [B;..] [I;..] [L;..]
        if re.match(r"[BIL];", self.s[self.i:self.i + 2]):
            self.i += 2
        self.ws()
        if self.peek() == "]":
            self.i += 1
            return ("list", items)
        while True:
            items.append(self.value())
            self.ws()
            c = self.peek()
            self.i += 1
            if c == "]":
                return ("list", items)
            if c != ",":
                raise SNBTError(f"expected ',' or ']' at {self.i - 1}")


# --------------------------------------------------------------------------- tokenizer
def tokenize(line):
    toks, cur, depth, quote = [], [], 0, None
    for ch in line:
        if quote:
            cur.append(ch)
            if ch == quote and (len(cur) < 2 or cur[-2] != "\\"):
                quote = None
            continue
        if ch in "\"'" and depth > 0:
            quote = ch
            cur.append(ch)
            continue
        if ch == '"' and not cur:
            quote = ch
            cur.append(ch)
            continue
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        if ch == " " and depth == 0:
            if cur:
                toks.append("".join(cur))
                cur = []
            continue
        cur.append(ch)
    if quote or depth != 0:
        raise ValueError("unbalanced quotes or brackets")
    if cur:
        toks.append("".join(cur))
    return toks


MACRO = re.compile(r"\$\(([A-Za-z0-9_]+)\)")
MARK = "MACROVAR"


class Linter:
    def __init__(self, tree, reg, pack_dir):
        self.tree, self.reg, self.pack = tree, reg, pack_dir
        self.items = set(reg["item"])
        self.components = set(reg["data_component_type"])
        self.predicates = set(reg["data_component_predicate_type"])
        self.entity_types = set(reg["entity_type"])
        self.errors = []
        self.functions = set()
        self.objectives = set()
        self.unknown_parsers = set()

    # ---- helpers
    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    @staticmethod
    def is_macro(tok):
        return MARK in tok

    def resolve(self, node):
        if "redirect" in node:
            tgt = self.tree
            for p in node["redirect"]:
                tgt = tgt["children"][p]
            return tgt
        return node

    # ---- argument validators: return number of tokens consumed or an error string
    def consume(self, name, node, toks, i):
        parser = node.get("parser")
        props = node.get("properties") or {}
        tok = toks[i]
        mac = self.is_macro(tok)
        if parser in ("brigadier:integer", "brigadier:long"):
            if mac:
                return 1
            if not re.fullmatch(r"-?\d+", tok):
                return f"expected integer, got {tok!r}"
            v = int(tok)
            if "min" in props and v < props["min"]:
                return f"{v} below min {props['min']}"
            if "max" in props and v > props["max"]:
                return f"{v} above max {props['max']}"
            return 1
        if parser in ("brigadier:float", "brigadier:double"):
            if mac or re.fullmatch(r"-?\d+(\.\d+)?", tok):
                return 1
            return f"expected number, got {tok!r}"
        if parser == "brigadier:bool":
            return 1 if mac or tok in ("true", "false") else f"expected bool, got {tok!r}"
        if parser == "brigadier:string":
            kind = props.get("type", "word")
            if kind == "greedy":
                return len(toks) - i
            if kind == "word":
                return 1 if mac or re.fullmatch(r"[A-Za-z0-9_.+\-]+", tok) else f"bad word {tok!r}"
            return 1
        if parser == "minecraft:message":
            return len(toks) - i
        if parser in ("minecraft:component", "minecraft:nbt_compound_tag", "minecraft:nbt_tag"):
            if mac:
                return 1
            text = tok
            if parser == "minecraft:nbt_compound_tag" and not text.startswith("{"):
                return f"expected compound, got {tok!r}"
            try:
                p = SNBT(text)
                p.parse()
            except SNBTError as e:
                return f"bad SNBT ({e}) in {tok[:60]!r}"
            if p.flags:
                return "; ".join(p.flags) + f" in {tok[:60]!r}"
            return 1
        if parser == "minecraft:nbt_path":
            return 1 if tok else "empty nbt path"
        if parser == "minecraft:objective":
            if mac:
                return 1
            if tok not in self.objectives:
                return f"objective {tok!r} is never declared in this pack"
            return 1
        if parser == "minecraft:score_holder":
            if mac or tok == "*":
                return 1
            if tok.startswith("@"):
                return self.selector(tok)
            if not tok.startswith("#"):
                return f"fake player {tok!r} must start with '#'"
            return 1
        if parser in ("minecraft:entity", "minecraft:game_profile"):
            if mac:
                return 1
            if tok.startswith("@"):
                return self.selector(tok)
            return 1
        if parser in ("minecraft:function", "minecraft:resource_location"):
            if mac:
                return 1
            if not re.fullmatch(r"#?([a-z0-9_.\-]+:)?[a-z0-9_./\-]+", tok):
                return f"bad resource location {tok!r}"
            if parser == "minecraft:function" and not tok.startswith("#"):
                full = tok if ":" in tok else "minecraft:" + tok
                if full not in self.functions:
                    return f"function {full!r} does not exist in this pack"
            return 1
        if parser in ("minecraft:vec3", "minecraft:block_pos"):
            if len(toks) - i < 3:
                return "needs 3 coordinates"
            for k in range(3):
                if not (self.is_macro(toks[i + k]) or re.fullmatch(r"[~^]?-?\d*\.?\d*", toks[i + k])):
                    return f"bad coordinate {toks[i + k]!r}"
            return 3
        if parser in ("minecraft:vec2", "minecraft:rotation", "minecraft:column_pos"):
            if len(toks) - i < 2:
                return "needs 2 coordinates"
            return 2
        if parser == "minecraft:int_range":
            return 1 if mac or re.fullmatch(r"-?\d*(\.\.)?-?\d*", tok) and tok else f"bad range {tok!r}"
        if parser == "minecraft:time":
            return 1 if mac or re.fullmatch(r"\d+(\.\d+)?[dst]?", tok) else f"bad time {tok!r}"
        if parser == "minecraft:item_stack":
            return self.item(tok, predicate=False)
        if parser == "minecraft:item_predicate":
            return self.item(tok, predicate=True)
        if parser == "minecraft:operation":
            return 1 if tok in ("=", "+=", "-=", "*=", "/=", "%=", "<", ">", "><") else f"bad operation {tok!r}"
        if parser == "minecraft:resource":
            reg = props.get("registry", "").replace("minecraft:", "")
            if mac or reg not in self.reg:
                return 1
            full = tok if ":" in tok else "minecraft:" + tok
            return 1 if full.replace("minecraft:", "") in self.reg[reg] or full in self.reg[reg] else f"{tok!r} not in registry {reg}"
        known = {"minecraft:slot_source", "minecraft:objective_criteria", "minecraft:scoreboard_slot",
                 "minecraft:color", "minecraft:entity_anchor", "minecraft:swizzle", "minecraft:dimension",
                 "minecraft:gamemode", "minecraft:heightmap", "minecraft:team", "minecraft:uuid"}
        if parser not in known:
            self.unknown_parsers.add(parser)
        return 1

    def selector(self, tok):
        m = re.fullmatch(r"@([aepsrn])(\[(.*)\])?", tok, re.S)
        if not m:
            return f"bad selector {tok!r}"
        body = m.group(3)
        if body is None:
            return 1
        valid = {"name", "distance", "x", "y", "z", "dx", "dy", "dz", "scores", "tag", "team", "limit", "sort",
                 "level", "gamemode", "type", "nbt", "predicate", "advancements", "x_rotation", "y_rotation"}
        depth, cur, parts = 0, [], []
        for ch in body:
            if ch in "{[(":
                depth += 1
            elif ch in "}])":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append("".join(cur))
                cur = []
            else:
                cur.append(ch)
        parts.append("".join(cur))
        for part in parts:
            if "=" not in part:
                return f"bad selector option {part!r}"
            key, val = part.split("=", 1)
            if key not in valid:
                return f"unknown selector option {key!r}"
            if key == "scores":
                if not re.fullmatch(r"\{([A-Za-z0-9_.+\-]+=(-?\d+)?(\.\.)?(-?\d+)?)(,[A-Za-z0-9_.+\-]+=(-?\d+)?(\.\.)?(-?\d+)?)*\}", val):
                    return f"bad scores in selector {val!r}"
                for nm in re.findall(r"([A-Za-z0-9_.+\-]+)=", val):
                    if nm not in self.objectives:
                        return f"objective {nm!r} in selector is never declared"
        return 1

    def item(self, tok, predicate):
        if self.is_macro(tok):
            return 1
        m = re.fullmatch(r"(#?[a-z0-9_.:/*\-]+)(\[(.*)\])?", tok, re.S)
        if not m:
            return f"bad item {tok!r}"
        iid, body = m.group(1), m.group(3)
        if iid != "*" and not iid.startswith("#"):
            short = iid.replace("minecraft:", "")
            if short not in self.items and iid not in self.items:
                return f"unknown item {iid!r}"
        if body is None:
            return 1
        depth, cur, parts = 0, [], []
        in_str = None
        for ch in body:
            if in_str:
                cur.append(ch)
                if ch == in_str:
                    in_str = None
                continue
            if ch in "\"'":
                in_str = ch
            elif ch in "{[(":
                depth += 1
            elif ch in "}])":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append("".join(cur))
                cur = []
            else:
                cur.append(ch)
        parts.append("".join(cur))
        for part in parts:
            part = part.strip()
            mm = re.fullmatch(r"(!?)([a-z0-9_.:]+)(?:([=~])(.*))?", part, re.S)
            if not mm:
                return f"bad component test {part[:50]!r}"
            neg, comp, op, val = mm.groups()
            short = comp.replace("minecraft:", "")
            if op == "~":
                if not predicate:
                    return "'~' only valid in item predicates"
                if short not in self.predicates and short not in self.components:
                    return f"unknown component predicate {comp!r}"
            elif short not in self.components and not (predicate and short in ("count",)):
                return f"unknown component {comp!r}"
            if val is not None:
                try:
                    p = SNBT(val)
                    p.parse()
                except SNBTError as e:
                    return f"bad SNBT for component {comp} ({e})"
                if p.flags:
                    return "; ".join(p.flags) + f" in component {comp}"
        return 1

    # ---- tree walk with backtracking
    def walk(self, node, toks, i, last):
        if i == len(toks):
            if node.get("executable"):
                return None
            return "command is incomplete"
        target = self.resolve(node)
        children = target.get("children") or {}
        tok = toks[i]
        if self.is_macro(tok) and children and all(c["type"] == "literal" for c in children.values()):
            return None  # a whole command supplied by a macro variable
        first_err = None
        for name, ch in children.items():
            if ch["type"] == "literal" and name == tok:
                if name == "run" and (target is self.tree["children"]["execute"] or node is self.tree["children"]["return"]):
                    r = self.walk(self.tree, toks, i + 1, last)
                    if r is None:
                        return None
                    first_err = first_err or r
                    continue
                r = self.walk(ch, toks, i + 1, last)
                if r is None:
                    return None
                first_err = first_err or r
        for name, ch in children.items():
            if ch["type"] == "argument":
                n = self.consume(name, ch, toks, i)
                if isinstance(n, str):
                    first_err = first_err or f"<{name}> {n}"
                    continue
                r = self.walk(ch, toks, i + n, last)
                if r is None:
                    return None
                first_err = first_err or r
        if first_err:
            return first_err
        exp = ", ".join(sorted(children)) or "end of command"
        return f"unexpected {tok!r}, expected one of: {exp}"

    def check_line(self, where, raw):
        line = raw.rstrip("\n").rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            if not line.isascii():
                self.err(where, "comment contains non-ASCII characters (comments must be English)")
            return
        if not line.isascii():
            self.err(where, "line contains non-ASCII characters (keep code and in-game text plain English)")
        if line != line.lstrip():
            self.err(where, "command lines must not be indented")
        if line.startswith("/"):
            self.err(where, "commands in function files must not start with '/'")
            return
        macro = line.startswith("$")
        if macro:
            line = line[1:]
        if re.search(r"\$\([^)]*\$\(", line):
            self.err(where, "nested macro variable syntax")
        if not macro and "$(" in line:
            self.err(where, "macro variable used on a line that does not start with '$'")
        if macro and "$(" not in line:
            self.err(where, "macro line without any $(variable)")
        line = MACRO.sub(MARK, line)
        try:
            toks = tokenize(line)
        except ValueError as e:
            self.err(where, f"{e}: {line[:80]}")
            return
        msg = self.walk(self.tree, toks, 0, None)
        if msg:
            self.err(where, f"{msg}\n        -> {line[:160]}")

    # ---- pack level
    def run(self):
        pack = self.pack
        mc = os.path.join(pack, "pack.mcmeta")
        if not os.path.isfile(mc):
            self.err(pack, "pack.mcmeta missing")
        else:
            try:
                meta = json.load(open(mc, encoding="utf-8"))["pack"]
                for k in ("description", "min_format", "max_format"):
                    if k not in meta:
                        self.err(mc, f"pack.{k} missing")
                if "supported_formats" in meta:
                    self.err(mc, "supported_formats must be absent for packs targeting data pack format >= 82")
            except Exception as e:
                self.err(mc, f"invalid JSON: {e}")
        fn_files = []
        for dp, _, fs in os.walk(os.path.join(pack, "data")):
            for f in fs:
                full = os.path.join(dp, f)
                rel = os.path.relpath(full, os.path.join(pack, "data")).replace(os.sep, "/")
                ns, rest = rel.split("/", 1)
                if f.endswith(".mcfunction") and rest.startswith("function/"):
                    self.functions.add(f"{ns}:{rest[len('function/'):-len('.mcfunction')]}")
                    fn_files.append((full, rel))
                elif f.endswith(".json"):
                    try:
                        json.load(open(full, encoding="utf-8"))
                    except Exception as e:
                        self.err(rel, f"invalid JSON: {e}")
        # pass 1: declared objectives
        for full, rel in fn_files:
            for ln in open(full, encoding="utf-8"):
                m = re.match(r"scoreboard objectives add (\S+) (\S+)", ln)
                if m:
                    self.objectives.add(m.group(1))
        # pass 2: every line
        for full, rel in fn_files:
            for n, ln in enumerate(open(full, encoding="utf-8"), 1):
                self.check_line(f"{rel}:{n}", ln)
        # tags
        for dp, _, fs in os.walk(os.path.join(pack, "data")):
            for f in fs:
                full = os.path.join(dp, f)
                rel = os.path.relpath(full, os.path.join(pack, "data")).replace(os.sep, "/")
                if "/tags/function/" in "/" + rel and f.endswith(".json"):
                    for v in json.load(open(full, encoding="utf-8")).get("values", []):
                        v = v if isinstance(v, str) else v.get("id", "")
                        if not v.startswith("#") and v not in self.functions:
                            self.err(rel, f"tag references missing function {v!r}")
        return len(fn_files)


def main(argv):
    version = "26.3"
    packs = []
    it = iter(argv)
    for a in it:
        if a == "--version":
            version = next(it)
        else:
            packs.append(a)
    if not packs:
        print(__doc__)
        return 2
    tree, reg = load_ref(version)
    bad = 0
    for p in packs:
        lt = Linter(tree, reg, p)
        n = lt.run()
        print(f"[{os.path.basename(p.rstrip('/'))}] {n} functions, {len(lt.errors)} problem(s)")
        for e in lt.errors:
            print("  -", e)
        if lt.unknown_parsers:
            print("  (note: unchecked argument types:", ", ".join(sorted(lt.unknown_parsers)) + ")")
        bad += len(lt.errors)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
