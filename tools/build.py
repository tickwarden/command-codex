#!/usr/bin/env python3
"""Builds dist/<pack>.zip for every folder in packs/.

Packaging rule: README.md, LICENSE, version.json and dependencies.json never go into a datapack zip.
The zip file name is the datapack id Minecraft shows (file/<name>.zip); the trial's self-disable
relies on the names command-codex-trial.zip and command-codex-pro.zip.
"""
import os
import sys
import zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
EXCLUDE = {"README.md", "LICENSE", "version.json", "dependencies.json"}


def main():
    out = os.path.join(ROOT, "dist")
    os.makedirs(out, exist_ok=True)
    for pack in sorted(os.listdir(os.path.join(ROOT, "packs"))):
        src = os.path.join(ROOT, "packs", pack)
        if not os.path.isdir(src):
            continue
        target = os.path.join(out, pack + ".zip")
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
            for dp, dn, fs in os.walk(src):
                dn.sort()
                for f in sorted(fs):
                    if f in EXCLUDE:
                        continue
                    full = os.path.join(dp, f)
                    z.write(full, os.path.relpath(full, src).replace(os.sep, "/"))
        print("built", os.path.relpath(target, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
