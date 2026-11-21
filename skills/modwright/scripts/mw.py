#!/usr/bin/env python3
"""modwright mw.py: read-only checks for modding a game install. Stdlib only.

  mw.py scan <install> [--json]   engine, runtime, anti-cheat, installed loader, recommended loader
Exit codes: 0 ok, 2 anti-cheat present (stop gate), 3 bad path.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ANTICHEAT = {  # marker (dir or file name, lower case) -> name
    "easyanticheat": "Easy Anti-Cheat", "easyanticheat_eos": "Easy Anti-Cheat",
    "battleye": "BattlEye", "mhypbase.dll": "miHoYo protect", "vgk.sys": "Riot Vanguard",
    "xigncode": "XIGNCODE3", "gameguard": "nProtect GameGuard",
    "pnkbstra.exe": "PunkBuster", "equ8.dll": "EQU8",
}
LOADERS = [  # (relative path that proves it, name)
    ("BepInEx/core/BepInEx.Unity.IL2CPP.dll", "BepInEx 6 (IL2CPP)"),
    ("BepInEx/core/BepInEx.Unity.Mono.dll", "BepInEx 6 (Mono)"),
    ("BepInEx/core/BepInEx.dll", "BepInEx 5"),
    ("MelonLoader", "MelonLoader"),
    ("UnityModManager", "Unity Mod Manager"),
    ("ue4ss", "UE4SS"),
    ("smapi-internal", "SMAPI"),
]
LOGS = {
    "BepInEx 5": "BepInEx/LogOutput.log",
    "BepInEx 6 (Mono)": "BepInEx/LogOutput.log",
    "BepInEx 6 (IL2CPP)": "BepInEx/LogOutput.log",
    "MelonLoader": "MelonLoader/Latest.log",
    "Unity Mod Manager": "UnityModManager/Log.txt",
    "UE4SS": "UE4SS.log (next to ue4ss dll)",
    "SMAPI": "%APPDATA%/StardewValley/ErrorLogs/SMAPI-latest.txt",
}
RECOMMEND = {
    ("Unity", "Mono"): "BepInEx 5 (or MelonLoader)",
    ("Unity", "IL2CPP"): "BepInEx 6 (or MelonLoader)",
    ("Unity", None): "check runtime, then BepInEx or MelonLoader",
    ("Unreal", None): "UE4SS (+ pak mods)",
    ("Godot", None): "pck override; gdsdecomp to inspect",
    ("XNA/FNA/MonoGame", None): "Harmony / BepInEx 6 .NET",
    ("Minecraft", None): "route to minewright (Forge/Fabric)",
    ("Bethesda Creation", None): "SKSE/F4SE + plugins.txt",
    ("GameMaker", None): "UndertaleModTool",
    ("Ren'Py", None): "unrpa/unrpyc, game/ overrides",
    ("RPG Maker MV/MZ", None): "js/plugins",
    ("Source", None): "addons/ or VPK",
}


def _entries(root, depth=4):
    names, rels = set(), []
    for dirpath, dirs, files in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        if len(rel.parts) >= depth:
            dirs[:] = []
        for n in dirs + files:
            names.add(n.lower())
            rels.append((rel / n).as_posix().lower())
    return names, rels


def scan(install):
    root = Path(install)
    names, rels = _entries(root)

    def has(n):
        return n.lower() in names

    def ext(*e):
        return any(n.endswith(e) for n in names)

    engine, runtime = "unknown", None
    if has("unityplayer.dll") or any(r.endswith("_data") and "/" not in r for r in rels):
        engine = "Unity"
        if has("gameassembly.dll") or has("global-metadata.dat"):
            runtime = "IL2CPP"
        elif has("assembly-csharp.dll"):
            runtime = "Mono"
    elif ext("-shipping.exe", ".utoc") or any(r.endswith(".pak") and "content/paks" in r for r in rels):
        engine = "Unreal"
    elif ext(".pck"):
        engine = "Godot"
    elif has("data.win"):
        engine = "GameMaker"
    elif ext(".rpa") or has("renpy"):
        engine = "Ren'Py"
    elif any(n.startswith(("rpg_", "rmmz_")) and n.endswith(".js") for n in names):
        engine = "RPG Maker MV/MZ"
    elif has("gameinfo.txt") or ext(".vpk"):
        engine = "Source"
    elif ext(".esm", ".ba2", ".bsa"):
        engine = "Bethesda Creation"
    elif has("fna.dll") or has("monogame.framework.dll") or ext(".xnb"):
        engine = "XNA/FNA/MonoGame"
    elif has(".minecraft") or (ext(".jar") and has("versions")):
        engine = "Minecraft"

    anticheat = sorted({v for k, v in ANTICHEAT.items() if has(k)})
    loaders = []
    for p, name in LOADERS:
        if (root / p).exists() and name not in loaders:
            loaders.append(name)
    notes = []
    if anticheat:
        notes.append("Anti-cheat present: stop. No injection or memory patching; "
                     "only official mod routes, single-player or offline.")
    if not loaders:
        notes.append("No mod loader installed yet. Back up saves before installing one.")
    return {
        "install": str(root), "engine": engine, "runtime": runtime, "anticheat": anticheat,
        "loaders_installed": loaders,
        "recommended_loader": RECOMMEND.get((engine, runtime), "unknown: inspect by hand"),
        "loader_logs": [LOGS[x] for x in loaders if x in LOGS], "notes": notes,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(prog="mw.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan", help="identify engine, runtime, anti-cheat and loaders")
    s.add_argument("install")
    s.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not Path(a.install).is_dir():
        print(f"not a directory: {a.install}", file=sys.stderr)
        return 3
    r = scan(a.install)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        for k in ("engine", "runtime", "anticheat", "loaders_installed",
                  "recommended_loader", "loader_logs", "notes"):
            print(f"{k}: {r[k]}")
    return 2 if r["anticheat"] else 0


if __name__ == "__main__":
    sys.exit(main())
