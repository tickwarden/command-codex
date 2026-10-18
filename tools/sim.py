#!/usr/bin/env python3
"""Tiny mcfunction interpreter used to test the packs' logic (not a Minecraft replacement).

Models only the command subset the packs use. Semantics assumed (documented Minecraft behaviour):
  * a macro line is instantiated per call; an unparsable instantiated line fails the call
  * `data modify ... set string` fails (target untouched) when indices are out of range
  * `execute store success` stores 1/0, `return` ends only the current function
Run: python tools/sim.py
"""
import copy
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint import SNBT, tokenize  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PACKS = os.path.join(HERE, "..", "packs")


def py(v):
    k, x = v
    if k == "compound":
        return {a: py(b) for a, b in x.items()}
    if k == "list":
        return [py(b) for b in x]
    if k == "str":
        return x
    m = re.fullmatch(r"(-?\d+)[bBsSlL]?", x)
    if m:
        return int(m.group(1))
    return x


def parse_snbt(s):
    return py(SNBT(s).parse())


class Return(Exception):
    def __init__(self, v):
        self.v = v


class Fail(Exception):
    pass


class World:
    def __init__(self, pack):
        self.pack = pack
        self.fn = {}
        base = os.path.join(PACKS, pack, "data")
        for ns in os.listdir(base):
            fdir = os.path.join(base, ns, "function")
            for dp, _, fs in os.walk(fdir):
                for f in fs:
                    rel = os.path.relpath(os.path.join(dp, f), fdir)[:-11].replace(os.sep, "/")
                    self.fn[f"{ns}:{rel}"] = open(os.path.join(dp, f), encoding="utf-8").read().splitlines()
        self.obj = {}      # name -> {holder: value}
        self.storage = {}  # id -> dict
        self.players = {}  # name -> dict(tags, item, inv)
        self.log = []
        self.disabled = []
        self.gametick = 0

    # ---- paths
    def path_get(self, root, path):
        cur = root
        for kind, key in self.path_parts(path):
            if kind == "key":
                if not isinstance(cur, dict) or key not in cur:
                    return None
                cur = cur[key]
            elif kind == "idx":
                if not isinstance(cur, list) or key >= len(cur):
                    return None
                cur = cur[key]
            elif kind == "filter":
                if not isinstance(cur, dict) or any(cur.get(a) != b for a, b in key.items()):
                    return None
        return cur

    @staticmethod
    def path_parts(path):
        parts, i = [], 0
        while i < len(path):
            c = path[i]
            if c == ".":
                i += 1
            elif c == "{":
                depth, j = 0, i
                while True:
                    depth += path[j] == "{"
                    depth -= path[j] == "}"
                    j += 1
                    if depth == 0:
                        break
                parts.append(("filter", parse_snbt(path[i:j])))
                i = j
            elif c == "[":
                j = path.index("]", i)
                parts.append(("idx", int(path[i + 1:j])))
                i = j + 1
            elif c == '"':
                j = path.index('"', i + 1)
                parts.append(("key", path[i + 1:j]))
                i = j + 1
            else:
                m = re.match(r"[A-Za-z0-9_+\-]+", path[i:])
                parts.append(("key", m.group(0)))
                i += len(m.group(0))
        return parts

    def path_set(self, root, path, value):
        parts = self.path_parts(path)
        cur = root
        for n, (kind, key) in enumerate(parts):
            last = n == len(parts) - 1
            if kind == "key":
                if last:
                    cur[key] = value
                else:
                    cur = cur.setdefault(key, {})
            elif kind == "idx":
                if last:
                    cur[key] = value
                else:
                    cur = cur[key]

    def path_remove(self, root, path):
        parts = self.path_parts(path)
        cur = root
        for n, (kind, key) in enumerate(parts):
            last = n == len(parts) - 1
            if kind == "key":
                if not isinstance(cur, dict) or key not in cur:
                    raise Fail()
                if last:
                    del cur[key]
                    return
                cur = cur[key]
            elif kind == "idx":
                if not isinstance(cur, list) or key >= len(cur):
                    raise Fail()
                if last:
                    del cur[key]
                    return
                cur = cur[key]

    # ---- scoreboard
    def score(self, obj, holder):
        if obj not in self.obj:
            raise Fail(f"unknown objective {obj}")
        return self.obj[obj].get(holder)

    def holders(self, tok, ctx):
        if tok == "@s":
            return [ctx["name"]] if ctx["name"] else []
        if tok.startswith("@a"):
            return [p for p in self.select(tok)]
        return [tok]

    def select(self, tok, ctx=None):
        names = list(self.players)
        if tok.startswith("@s") and ctx is not None:
            names = [ctx["name"]] if ctx["name"] in self.players else []
            tok = "@a" + tok[2:]
        m = re.fullmatch(r"@a(?:\[(.*)\])?", tok)
        if not m:
            return []
        out = []
        for n in names:
            ok = True
            for opt in (m.group(1) or "").split(",") if m.group(1) and "{" not in m.group(1) else self.split_opts(m.group(1) or ""):
                if not opt:
                    continue
                k, v = opt.split("=", 1)
                if k == "tag":
                    neg = v.startswith("!")
                    has = v.lstrip("!") in self.players[n]["tags"]
                    ok &= (not has) if neg else has
                elif k == "scores":
                    for nm, rng in re.findall(r"([\w.+\-]+)=([-\d.]*)", v):
                        val = self.obj.get(nm, {}).get(n)
                        ok &= val is not None and self.in_range(val, rng)
            if ok:
                out.append(n)
        return out

    @staticmethod
    def split_opts(s):
        parts, depth, cur = [], 0, ""
        for c in s:
            depth += c in "{["
            depth -= c in "}]"
            if c == "," and depth == 0:
                parts.append(cur)
                cur = ""
            else:
                cur += c
        parts.append(cur)
        return parts

    @staticmethod
    def in_range(v, rng):
        if ".." in rng:
            lo, hi = rng.split("..")
            return (lo == "" or v >= int(lo)) and (hi == "" or v <= int(hi))
        return v == int(rng)

    # ---- function calls
    def call(self, name, ctx, macro=None):
        if name not in self.fn:
            raise Fail(f"no function {name}")
        try:
            for raw in self.fn[name]:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("$"):
                    if macro is None:
                        raise Fail("macro function called without arguments")
                    line = re.sub(r"\$\(([A-Za-z0-9_]+)\)", lambda m: self.macro_val(macro, m.group(1)), line[1:])
                try:
                    self.run_line(line, ctx)
                except Return:
                    raise
                except Fail:
                    pass
        except Return as r:
            return r.v
        return 0

    @staticmethod
    def macro_val(macro, key):
        if key not in macro:
            raise Fail(f"missing macro arg {key}")
        v = macro[key]
        return v if isinstance(v, str) else str(v)

    # ---- command execution; returns result int, raises Fail
    def run_line(self, line, ctx):
        toks = tokenize(line)
        return self.cmd(toks, ctx)

    def cmd(self, t, ctx):
        c = t[0]
        if c == "execute":
            return self.execute(t[1:], ctx, [])
        if c == "return":
            if t[1] == "run":
                r = self.cmd(t[2:], ctx)
                raise Return(r)
            if t[1] == "fail":
                raise Return(0)
            raise Return(int(t[1]))
        if c == "function":
            args = None
            if len(t) > 2 and t[2] == "with":
                assert t[3] == "storage"
                args = self.path_get(self.storage.setdefault(t[4], {}), t[5])
                if not isinstance(args, dict):
                    raise Fail("macro args not a compound")
            return self.call(t[1], ctx, args)
        if c == "scoreboard":
            return self.scoreboard(t[1:], ctx)
        if c == "data":
            return self.data(t[1:], ctx)
        if c == "tag":
            hs = self.target_names(t[1], ctx)
            for h in hs:
                tags = self.players[h]["tags"]
                if t[2] == "add":
                    tags.add(t[3])
                else:
                    tags.discard(t[3])
            return len(hs)
        if c == "clear":
            return self.clear(t[1:], ctx)
        if c == "give":
            for h in self.target_names(t[1], ctx):
                self.players[h]["inv"].append(self.parse_item(t[2]))
            return 1
        if c == "item":
            # item replace entity @s weapon.mainhand with <item>
            for h in self.target_names(t[3], ctx):
                self.players[h]["main"] = self.parse_item(t[6])
            return 1
        if c in ("tellraw", "title", "playsound", "say", "particle"):
            self.log.append((ctx["name"], " ".join(t)))
            return 1
        if c == "datapack":
            self.disabled.append(t[2].strip('"'))
            return 1
        raise Fail(f"sim: unsupported command {c}")

    def target_names(self, tok, ctx):
        if tok == "@s":
            return [ctx["name"]]
        if tok.startswith("@a"):
            return self.select(tok)
        return [tok] if tok in self.players else []

    def parse_item(self, tok):
        m = re.fullmatch(r"([\w:]+)\[(.*)\]", tok, re.S)
        comps = {}
        if m:
            for part in Linter_split(m.group(2)):
                k, v = part.split("=", 1)
                comps["minecraft:" + k.replace("minecraft:", "")] = parse_snbt(v)
        return {"id": tok.split("[")[0], "components": comps}

    def item_matches(self, item, pred):
        m = re.fullmatch(r"([\w:*]+)\[(.*)\]", pred, re.S)
        iid = (m.group(1) if m else pred)
        if iid != "*" and item["id"].replace("minecraft:", "") != iid.replace("minecraft:", ""):
            return False
        if m:
            for part in Linter_split(m.group(2)):
                k, v = part.split("~", 1)
                want = parse_snbt(v)
                have = item["components"].get("minecraft:" + k.replace("minecraft:", ""), {})
                if any(have.get(a) != b for a, b in want.items()):
                    return False
        return True

    def clear(self, t, ctx):
        n = 0
        for h in self.target_names(t[0], ctx):
            p = self.players[h]
            allitems = p["inv"] + ([p["main"]] if p["main"] else [])
            hit = [i for i in allitems if self.item_matches(i, t[1])]
            n += len(hit)
            if len(t) > 2 and t[2] == "0":
                continue
            p["inv"] = [i for i in p["inv"] if i not in hit]
            if p["main"] in hit:
                p["main"] = None
        return n

    def scoreboard(self, t, ctx):
        if t[0] == "objectives":
            if t[1] == "add":
                if t[2] in self.obj:
                    raise Fail("exists")
                self.obj[t[2]] = {}
            elif t[1] == "remove":
                if t[2] not in self.obj:
                    raise Fail("unknown")
                del self.obj[t[2]]
            return 1
        sub, hs_tok, ob = t[1], t[2], t[3]
        if sub == "enable":
            return 1
        hs = self.holders(hs_tok, ctx)
        if ob not in self.obj:
            raise Fail("unknown objective")
        d = self.obj[ob]
        if sub == "set":
            for h in hs:
                d[h] = int(t[4])
            return int(t[4])
        if sub == "add":
            for h in hs:
                d[h] = d.get(h, 0) + int(t[4])
            return 1
        if sub == "remove":
            for h in hs:
                d[h] = d.get(h, 0) - int(t[4])
            return 1
        if sub == "reset":
            for h in hs:
                d.pop(h, None)
            return 1
        if sub == "operation":
            op, src_tok, src_ob = t[4], t[5], t[6]
            src = self.holders(src_tok, ctx)[0]
            sv = self.score(src_ob, src)
            if sv is None:
                raise Fail("src unset")
            for h in hs:
                tv = d.get(h, 0)
                if op == "=":
                    d[h] = sv
                elif op == "+=":
                    d[h] = tv + sv
                elif op == "-=":
                    d[h] = tv - sv
                elif op == "/=":
                    d[h] = int(tv / sv) if sv else tv
                elif op == "%=":
                    d[h] = tv % sv if sv else tv
            return 1
        raise Fail("sim scoreboard " + sub)

    def data(self, t, ctx):
        if t[0] != "modify" and t[0] != "remove":
            raise Fail("sim data")
        if t[0] == "remove":
            assert t[1] == "storage"
            self.path_remove(self.storage.setdefault(t[2], {}), t[3])
            return 1
        assert t[1] == "storage"
        root = self.storage.setdefault(t[2], {})
        path, mode = t[3], t[4]
        assert mode == "set"
        src = t[5]
        if src == "value":
            val = parse_snbt(" ".join(t[6:]))
        elif src == "from":
            val = self.read_source(t[6], t[7], t[8], ctx)
        elif src == "string":
            s = self.read_source(t[6], t[7], t[8], ctx)
            if not isinstance(s, str):
                raise Fail("not a string")
            start = int(t[9]) if len(t) > 9 else 0
            end = int(t[10]) if len(t) > 10 else len(s)
            if start < 0 or end > len(s) or start >= end:
                raise Fail("invalid substring")
            val = s[start:end]
        else:
            raise Fail("sim data src")
        if self.path_get(root, path) == val and src != "value":
            raise Fail("nothing changed")
        self.path_set(root, path, val)
        return 1

    def read_source(self, kind, ident, path, ctx):
        if kind == "storage":
            v = self.path_get(self.storage.setdefault(ident, {}), path)
        elif kind == "entity":
            ent = {"SelectedItem": self.players[ctx["name"]]["main"]}
            v = self.path_get(ent, path)
        else:
            raise Fail("sim source")
        if v is None:
            raise Fail("no such data")
        return copy.deepcopy(v)

    # ---- execute
    def execute(self, t, ctx, stores):
        ctx = dict(ctx)
        i = 0
        while i < len(t):
            w = t[i]
            if w in ("as", "at"):
                if w == "as":
                    names = self.target_names(t[i + 1], ctx)
                    res = 0
                    for n in names:
                        c2 = dict(ctx)
                        c2["name"] = n
                        res += self.execute(t[i + 2:], c2, stores) or 0
                    return res
                i += 2
                continue
            if w == "store":
                kind, tgt_kind, holder, ob = t[i + 1], t[i + 2], t[i + 3], t[i + 4]
                stores = stores + [(kind, holder, ob, ctx)]
                i += 5
                continue
            if w in ("if", "unless"):
                ok, used = self.condition(t[i + 1:], ctx)
                if ok != (w == "if"):
                    self.apply_stores(stores, 0, 0)
                    raise Fail("condition false") if False else Return(0) if False else Fail("cond")
                i += 1 + used
                if i >= len(t):
                    self.apply_stores(stores, 1, 1)
                    return 1
                continue
            if w == "run":
                try:
                    r = self.cmd(t[i + 1:], ctx)
                except Fail:
                    self.apply_stores(stores, 0, 0)
                    raise
                succ = 1 if (r is None or r != 0 or True) else 0
                self.apply_stores(stores, r if isinstance(r, int) else 1, 1)
                return r
            raise Fail(f"sim execute {w}")
        return 1

    def apply_stores(self, stores, result, success):
        for kind, holder, ob, ctx in stores:
            v = success if kind == "success" else result
            hs = self.holders(holder, ctx)
            for h in hs:
                self.obj[ob][h] = v

    def condition(self, t, ctx):
        kind = t[0]
        if kind == "score":
            h = self.holders(t[1], ctx)[0]
            ob = t[2]
            v = self.score(ob, h)
            if t[3] == "matches":
                return (v is not None and self.in_range(v, t[4])), 5
            other = self.score(t[5], self.holders(t[4], ctx)[0])
            if v is None or other is None:
                return False, 6
            return {">": v > other, "<": v < other, ">=": v >= other, "<=": v <= other, "=": v == other}[t[3]], 6
        if kind == "data":
            assert t[1] == "storage"
            root = self.storage.setdefault(t[2], {})
            return self.path_get(root, t[3]) is not None, 4
        if kind == "items":
            names = self.target_names(t[2], ctx)
            item = self.players[names[0]]["main"] if names else None
            return bool(item and self.item_matches(item, t[4])), 5
        if kind == "entity":
            return len(self.select(t[1], ctx)) > 0, 2
        raise Fail("sim condition " + kind)


def Linter_split(body):
    parts, depth, cur, in_str = [], 0, "", None
    for ch in body:
        if in_str:
            cur += ch
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
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts]


# ----------------------------------------------------------------------------- tests
def player(world, name, tags=()):
    world.players[name] = {"tags": set(tags), "main": None, "inv": []}
    return {"name": name}


def hold_book(world, name, tagkey, pages):
    world.players[name]["main"] = {"id": "minecraft:writable_book", "components": {
        "minecraft:custom_data": {tagkey: 1}, "minecraft:writable_book_content": {"pages": [{"raw": p} for p in pages]}}}


SERVER = {"name": None}
passed, failed = 0, 0


def check(label, cond):
    global passed, failed
    print(("  ok   " if cond else "  FAIL ") + label)
    if cond:
        passed += 1
    else:
        failed += 1


def execs(w, who):
    return [l for n, l in w.log if n == who and l.startswith(("say", "particle", "playsound", "tellraw", "title")) is False]


def test_pro():
    print("PRO")
    w = World("command-codex-pro")
    w.call("ccx:load", SERVER)
    a = player(w, "Alice", ["ccx.allow"])
    b = player(w, "Bob")
    # book request gate
    w.obj["ccx.book"]["Alice"] = 1
    w.obj["ccx.book"]["Bob"] = 1
    w.call("ccx:book/request", a)
    w.call("ccx:book/request", b)
    check("authorized player receives a Codex", len(w.players["Alice"]["inv"]) == 1)
    check("unauthorized player receives nothing", len(w.players["Bob"]["inv"]) == 0)
    # second request does not duplicate
    w.obj["ccx.book"]["Alice"] = 1
    w.call("ccx:book/request", a)
    check("no duplicate Codex", len(w.players["Alice"]["inv"]) == 1)

    pages = ["# comment", "say one", "", "bogus nonsense line", "say after-fail", "scoreboard players set #probe ccx.tmp 7"]
    hold_book(w, "Alice", "ccx", pages)
    hold_book(w, "Bob", "ccx", pages)
    # unauthorized run
    w.obj["ccx.run"]["Bob"] = 1
    w.call("ccx:run/request", b)
    check("unauthorized run is refused (no left score)", w.obj["ccx.left"].get("Bob", 0) == 0)
    # authorized single run
    w.log.clear()
    w.obj["ccx.run"]["Alice"] = 1
    w.call("ccx:run/request", a)
    check("run request sets ccx.left", w.obj["ccx.left"]["Alice"] == 1)
    w.call("ccx:run/step", a)
    says = [l for n, l in w.log if l.startswith("say")]
    check("comment and empty page skipped, normal lines run", w.obj["ccx.tmp"].get("#probe") == 7)
    check("ran count = 4 (empty/comment excluded)", w.obj["ccx.tmp"]["#ran"] == 4)
    check("exactly 1 unparsable line counted as failed", w.obj["ccx.tmp"]["#fail"] == 1)
    check("run finished (ccx.left back to 0)", w.obj["ccx.left"]["Alice"] == 0)
    # stop on fail
    w.obj["ccx.cond"]["Alice"] = 1
    w.obj["ccx.tmp"].pop("#probe")
    w.obj["ccx.left"]["Alice"] = 1
    w.call("ccx:run/step", a)
    check("stop-on-fail ends the pass at the bad line", "#probe" not in w.obj["ccx.tmp"])
    check("stop-on-fail ran 2 lines (say one + bad)", w.obj["ccx.tmp"]["#ran"] == 2)
    # repeat clamp
    w.obj["ccx.run"]["Alice"] = 99999
    w.call("ccx:run/request", a)
    check("repeat count clamped to #max_repeat", w.obj["ccx.left"]["Alice"] == 200)
    w.obj["ccx.left"]["Alice"] = 0
    w.obj["ccx.run"]["Alice"] = 3
    w.call("ccx:run/request", a)
    for _ in range(3):
        if w.obj["ccx.left"]["Alice"] >= 1:
            w.call("ccx:run/step", a)
    check("repeat x3 counted down to 0", w.obj["ccx.left"]["Alice"] == 0)
    # clear-after-run
    w.obj["ccx.cond"]["Alice"] = 0
    w.obj["ccx.clear"]["Alice"] = 1
    w.obj["ccx.left"]["Alice"] = 1
    w.call("ccx:run/step", a)
    pgs = w.players["Alice"]["main"]["components"]["minecraft:writable_book_content"]["pages"]
    check("clear-after-run blanks the book", len(pgs) == 1 and pgs[0]["raw"] == "# cleared")
    # swap away aborts
    w.players["Alice"]["main"] = None
    w.obj["ccx.left"]["Alice"] = 5
    w.call("ccx:run/step", a)
    check("run aborts when the Codex leaves the main hand", w.obj["ccx.left"]["Alice"] == 0)
    # stale pages protection: book without content
    w.players["Alice"]["main"] = {"id": "minecraft:writable_book", "components": {"minecraft:custom_data": {"ccx": 1}}}
    w.storage["ccx:run"]["pages"] = [{"raw": "say STALE"}]
    w.log.clear()
    w.obj["ccx.left"]["Alice"] = 1
    w.call("ccx:run/step", a)
    check("contentless book does not replay stale pages", not any("STALE" in l for _, l in w.log))
    # admin
    w.call("ccx:admin/allow", SERVER, {"player": "Bob"})
    check("admin allow tags player", "ccx.allow" in w.players["Bob"]["tags"])
    w.call("ccx:admin/deny", SERVER, {"player": "Bob"})
    check("admin deny removes tag", "ccx.allow" not in w.players["Bob"]["tags"])
    w.call("ccx:admin/uninstall", SERVER)
    check("uninstall removes all objectives", not w.obj)
    check("uninstall tries both disable ids", w.disabled == ["file/command-codex-pro.zip", "file/command-codex-pro"])


def test_trial():
    print("TRIAL")
    w = World("command-codex-trial")
    w.call("ccx_trial:load", SERVER)
    a = player(w, "Alice")
    check("first load tells players about the trial", any("Trial active" in l for _, l in w.log))
    w.call("ccx_trial:load", SERVER)
    check("reload does not restart the clock", w.obj["cxt.state"]["#clock"] == 0)
    w.obj["cxt.book"]["Alice"] = 1
    w.call("ccx_trial:book/request", a)
    check("anyone can get a trial book", len(w.players["Alice"]["inv"]) == 1)
    pages = ["# c", "say hi", "execute run say sneaky", "give @s diamond 64", "particle minecraft:heart ~ ~ ~ 0 0 0 0 1", "playsound minecraft:x master @s ~ ~ ~ 1 1", "say", "gamemode creative @s"]
    pages += ["say extra%d" % k for k in range(8)]
    hold_book(w, "Alice", "ccx_trial", pages)
    w.log.clear()
    w.obj["cxt.run"]["Alice"] = 1
    w.call("ccx_trial:run/request", a)
    ran = w.obj["cxt.tmp"]["#ran"]
    deny = w.obj["cxt.tmp"]["#deny"]
    executed = [l for n, l in w.log if l.startswith(("say", "particle", "playsound")) and "tellraw" not in l]
    check("execute/give/gamemode are blocked", not any(("sneaky" in l) for l in executed) and deny >= 3)
    check("10-page cap: at most 10 pages processed", ran + deny + 1 <= 10 + 1 and ran + deny <= 9)
    check("cooldown score set", w.obj["cxt.cd"]["Alice"] == 100)
    # expiry
    start_log = len(w.log)
    ticks = 0
    limit = w.obj["cxt.state"]["#limit"]
    warned = []
    while "cxt.done" in w.obj and w.obj["cxt.done"].get("#done") != 1 and ticks < limit + 5:
        before = len(w.log)
        w.call("ccx_trial:tick", SERVER)
        ticks += 1
        for _, l in w.log[before:]:
            if "Trial ends in" in l:
                warned.append((ticks, re.search(r"Trial ends in ([^\"]+)\.", l).group(1)))
    check(f"trial expires after exactly {limit} ticks", ticks == limit)
    check("warnings at 10 min / 1 min / 10 s", [x[1] for x in warned] == ["10 minutes", "1 minute", "10 seconds"])
    check("warning ticks are correct", [limit - x[0] for x in warned] == [12000, 1200, 200])
    check("expiry announced", any("trial has ended" in l for _, l in w.log))
    check("books removed from inventory", not w.players["Alice"]["inv"])
    check("only the done-marker objective survives", list(w.obj) == ["cxt.done"])
    check("datapack disable attempted (zip + folder id)", w.disabled == ["file/command-codex-trial.zip", "file/command-codex-trial"])
    # post-expiry reload (disable failed): only retries disable, creates nothing
    w.disabled.clear()
    w.call("ccx_trial:load", SERVER)
    check("reload after expiry creates no objectives", list(w.obj) == ["cxt.done"])
    check("reload after expiry retries disable", len(w.disabled) == 2)
    w.call("ccx_trial:tick", SERVER)
    check("tick after expiry is inert", list(w.obj) == ["cxt.done"])
    # tamper: wiping the clock must expire, not restart
    w2 = World("command-codex-trial")
    w2.call("ccx_trial:load", SERVER)
    player(w2, "Eve")
    for _ in range(10):
        w2.call("ccx_trial:tick", SERVER)
    del w2.obj["cxt.state"]
    w2.call("ccx_trial:load", SERVER)
    check("wiped clock ends the trial instead of restarting it", w2.obj["cxt.done"].get("#done") == 1)


if __name__ == "__main__":
    test_pro()
    test_trial()
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
