# Command Codex

Three Minecraft Java datapack variants turn pages of a specially marked
writable book into commands. Each page is treated as a command; empty pages
and pages whose first character is `#` are skipped. The source declares
Minecraft **26.3** and datapack format **121** in each `pack.mcmeta`; these
are project targets, not a guarantee that the packs work in every environment.

> **High trust required:** Pro and Ultra execute book text through function
> macros with datapack-function authority. A permitted player can run commands
> that affect the world or server according to its configuration. A player
> allowed to use these variants must be trusted accordingly. The Trial uses
> a limited prefix list but can still send chat, sounds and particles; it is
> not a general-purpose security sandbox. Test only in a disposable world and
> preserve a backup before installing, using clear-after-run or uninstalling.

## Variants

| | Trial | Pro | Ultra |
| --- | --- | --- | --- |
| Folder | [`command-codex-trial`](packs/command-codex-trial/) | [`command-codex-pro`](packs/command-codex-pro/) | [`command-codex-ultra`](packs/command-codex-ultra/) |
| Namespace | `ccx_trial` | `ccx` | `ccxu` |
| Player gate | No player-tag gate | `ccx.allow` | `ccxu.allow` |
| Commands | Prefixes `say `, `playsound `, `particle ` | Arbitrary book commands | Arbitrary book commands |
| Page limit | First 10 pages per request | No separate page cap in the shown traversal | Configurable `#max_lines`, default 100 |
| Repeat / options | No repeated-run option | Repeat, stop-on-fail, clear and quiet | Pro-like options plus page-count dry run and an audit record |
| Duration | `144000` active ticks by default | No trial timer | No trial timer |

At a steady 20 ticks per second, 144000 ticks is about two hours. This is
server/pack tick time, not a guaranteed wall-clock deadline. The Trial's code
warns near expiry and then attempts cleanup and disablement; see the data-loss
warning below.

## Install and use

The repository contains source pack folders. The builder requests ZIP files
named `command-codex-trial.zip`, `command-codex-pro.zip` and
`command-codex-ultra.zip`. Minecraft can load a compatible pack from a world's
`datapacks/` directory, but check the actual output, target version, privileges
and world backup before `/reload`. Names matter because the uninstall and
Trial expiry routines attempt specific `file/<name>` and `file/<name>.zip`
identifiers; renamed packs may not be disabled by those commands.

### Trial

`/trigger cxt.book` requests a marked book. Hold it in the main hand, write
one command per page, then use `/trigger cxt.run`. The source permits only
lines beginning with the configured `say `, `playsound ` or `particle ` prefix,
processes at most 10 pages and sets a 100-tick player cooldown. Comments and
empty pages are skipped but still participate in page traversal. Prefix
filtering is not a proof that the allowed commands are harmless.

The limit is set by `#limit cxt.state` in `ccx_trial:load` and defaults to
144000 ticks. It is a configurable courtesy limit, not DRM. **At expiry**, the
pack attempts to clear matching Trial writable books from online players,
remove its objectives and selected storage, and disable its own pack ID. The
books can contain user-written pages, so expiry is destructive. A completion
marker objective remains. Do not install it in a world where this cleanup
would be unacceptable.

### Pro

An operator can manage the gate and request a book for an online player using
the named functions, for example:

```mcfunction
/function ccx:admin/allow {player:"Name"}
/function ccx:admin/allow_self
/function ccx:admin/deny {player:"Name"}
/function ccx:admin/give {player:"Name"}
/function ccx:admin/list
```

An authorized player uses `/trigger ccx.book`, holds the book and uses
`/trigger ccx.run set <n>`; a run can repeat over consecutive ticks. The
configured repeat ceiling is `#max_repeat ccx.cfg`, default `200`.
`/trigger ccx.opt` displays options: `set 1` toggles stop-on-fail, `set 2`
toggles clear-after-run, `set 3` toggles quiet output and `set 4` stops the
current run. Clear-after-run **replaces book pages**, so keep copies of anything
important. The source gate operates on player tags; a datapack cannot list or
remove tags from offline players through `@a`.

### Ultra

Ultra uses its own `ccxu` namespace, `ccxu.allow` tag and `ccxu.book`,
`ccxu.run`, `ccxu.opt` triggers; it does not share Pro's permission tag.
Administrative `allow`, `allow_self`, `deny`, `give` and `list` functions have
corresponding `ccxu:admin/...` names. `#max_repeat ccxu.cfg` defaults to 200;
`#max_lines ccxu.cfg` defaults to 100 pages per execution pass.

`/trigger ccxu.opt set 5` requests a dry run: it counts pages, non-comment
commands and skipped entries without executing their command text. It is not a
syntax check, permission check or safety analysis. The intended audit record
stores UUID, game tick and repeat count, not the full command text, and the
source attempts to retain the newest 50 entries. The initial audit-list
creation and end-to-end behavior have not been validated in Minecraft; do not
rely on it as a durable or tamper-proof security log.

`/function ccxu:admin/audit` reads the audit storage;
`/function ccxu:admin/audit_clear` **deletes** its log. Ultra's uninstall also
removes audit storage.

## Removal and world effects

`ccx:admin/uninstall` and `ccxu:admin/uninstall` remove their named objectives,
selected storage paths and the corresponding tag from online players, then
attempt to disable their specifically named pack IDs. Ultra additionally
removes its audit data. These operations are destructive and do not prove that
all books or offline-player tags were removed. Review the source and back up
world data before choosing to run them. The separate Trial expiry automatically
attempts its own cleanup as described above.

## Development and verification

[`tools/lint.py`](tools/lint.py) checks pack functions and JSON against a
versioned command-tree/registry reference downloaded from `misode/mcmeta`, and
writes a local `tools/.cache/`. [`tools/sim.py`](tools/sim.py) implements a
limited in-memory simulator, not Minecraft. [`tools/build.py`](tools/build.py)
writes `dist/<pack>.zip`, overwriting an existing output of the same name; it
omits `README.md`, `LICENSE`, `version.json` and `dependencies.json` from the
pack ZIPs. Use an empty disposable copy before running a build.

The following checks were performed in an isolated copy for this README
update; no Minecraft server or world was run:

- `tools/lint.py` with `--version 26.3`: Trial 16, Pro 29 and Ultra 34
  functions, **0 reported problems**. The reference data was fetched from
  the project's configured external source.
- `tools/sim.py`: **37 passed, 0 failed**, covering Pro and Trial only; the
  simulator does not establish Ultra or real-game behavior.
- `tools/build.py`: three ZIPs were created in a fresh `dist/` and passed ZIP
  CRC checks. This verifies packaging, not loading or execution in Minecraft.

The source is an independent implementation of the command-book idea; the
original README credits PALKIP's older Command Book as an inspiration and says
its code, names and assets are not used.

## License

[MIT](LICENSE); see the file for copyright and conditions.
