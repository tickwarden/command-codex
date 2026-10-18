# Command Codex

A writable book that stores one command per page and runs them on demand.
Minecraft Java **26.3** (data pack format 121). Two independent datapacks:

| | `command-codex-trial` | `command-codex-pro` |
|---|---|---|
| Who can use it | everyone (no gate) | only players tagged `ccx.allow` (the gate) |
| Allowed commands | `say`, `playsound`, `particle` only | any command |
| Lines per run | 10 | 100 |
| Repeat / stop-on-fail / clear-after-run | no | yes |
| Lifetime | 2 h of pack uptime, then it announces, cleans up and disables itself | permanent |

## Install
Put the zip into `<world>/datapacks/` (keep the file name) and run `/reload`.

## Trial
`/trigger cxt.book` gives a book. Write commands, one per page, hold it, `/trigger cxt.run`.
Lines starting with `#` are skipped. At the end the pack removes its books, objectives and storage
and runs `datapack disable` on `file/command-codex-trial.zip` (and the folder id).
Change the length in `ccx_trial:load` (`#limit`, ticks). The limit is a courtesy, not DRM:
anyone with access to the files can edit it.

## Pro
Operators authorize players (`/function` needs permission level 2):

    /function ccx:admin/allow {player:"Name"}
    /function ccx:admin/allow_self
    /function ccx:admin/deny {player:"Name"}
    /function ccx:admin/give {player:"Name"}
    /function ccx:admin/list
    /function ccx:admin/uninstall

Authorized players: `/trigger ccx.book`, `/trigger ccx.run set <n>` (n = executions on consecutive
ticks), `/trigger ccx.opt` (menu: stop-on-fail, clear-after-run, quiet, stop).
Cap for `n`: `/scoreboard players set #max_repeat ccx.cfg <ticks>` (default 200).

**Security model.** Book lines run through a function macro with the permission level of data pack
functions (server property `function-permission-level`). Treat `ccx.allow` as "trusted operator".
There is deliberately no ungated arbitrary-command path: the trial is limited to harmless verbs.
Tags of offline players cannot be listed or removed by a datapack.

## Dev tools
    python tools/lint.py packs/command-codex-pro packs/command-codex-trial   # checks against the 26.3 command tree
    python tools/sim.py                                                        # behaviour tests (mini interpreter)
    python tools/build.py                                                      # dist/*.zip (no README/LICENSE inside)

Status: lint + simulator pass. The simulator models documented semantics, it is not Minecraft,
so run the pack in a 26.3 world once before releasing.

Independent implementation of the "book that holds commands" idea (see PALKIP's older Command Book).
No code, names or assets from it are used.
