#!/usr/bin/env python3
"""modwright mw.py: safety and proof checks for modding a game install. Stdlib only.

  mw.py scan <install> [--json]                     engine, runtime, anti-cheat, loaders
  mw.py backup <out> <path>... [--build ID]         copy files/dirs + SHA-256 manifest.json
  mw.py restore <backup> [--verify]                 copy back (or only check hashes)
  mw.py proof <install> --mod NAME [--log FILE]     loader log: loaded / errored / not-seen
  mw.py publish-prep workshop|thunderstore <dir> ... write the upload file; never uploads
Exit codes: 0 ok, 1 check failed (proof not loaded, hash mismatch), 2 anti-cheat present
(stop gate), 3 bad path or input.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
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
    "UE4SS": "ue4ss/UE4SS.log",
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


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def backup(out, paths, build=None):
    """Copy each path (file or dir) into out/files/<n>/ and write a hash manifest."""
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"backup folder not empty: {out}")
    items = []
    for i, src in enumerate(paths):
        src = Path(src).resolve()
        if not src.exists():
            raise ValueError(f"missing: {src}")
        files = [src] if src.is_file() else sorted(p for p in src.rglob("*") if p.is_file())
        base = src.parent if src.is_file() else src
        for f in files:
            rel = f.relative_to(base).as_posix()
            dst = out / "files" / str(i) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            items.append({"slot": i, "rel": rel, "sha256": _sha(f), "size": f.stat().st_size})
    sources = [str(Path(p).resolve()) for p in paths]
    man = {"made": time.strftime("%Y-%m-%dT%H:%M:%S"), "build": build,
           "sources": sources, "kinds": ["file" if Path(p).is_file() else "dir" for p in sources],
           "files": items}
    (out / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    return {"backup": str(out), "files": len(items), "build": build}


def restore(bdir, verify_only=False):
    bdir = Path(bdir)
    man = json.loads((bdir / "manifest.json").read_text(encoding="utf-8"))
    bad, changed, restored = [], [], 0
    for it in man["files"]:
        copy = bdir / "files" / str(it["slot"]) / it["rel"]
        if not copy.is_file() or _sha(copy) != it["sha256"]:
            bad.append(it["rel"])
            continue
        src = Path(man["sources"][it["slot"]])
        live = (src.parent if man["kinds"][it["slot"]] == "file" else src) / it["rel"]
        if not live.is_file() or _sha(live) != it["sha256"]:
            changed.append(live.as_posix())
            if not verify_only:
                live.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(copy, live)
                restored += 1
    return {"backup_ok": not bad, "corrupt_in_backup": bad,
            "live_differs": changed, "restored": restored, "build": man.get("build")}


LOAD_LINES = [r"Loading \[{m}", r"Starting Lua mod '{m}'", r"Mod '{m}' loaded",
              r"\b{m}\b.*\b(loaded|initiali[sz]ed|by )", r"^\s*\d+\)\s*{m}\b", r"Melon.*{m}"]
ERR_RE = r"(error|exception|failed|could not load).*{m}|{m}.*(error|exception|failed)"


def proof(install, mod, log=None):
    root = Path(install)
    logs = [Path(log)] if log else []
    if not logs:
        for rel in ("BepInEx/LogOutput.log", "MelonLoader/Latest.log", "UnityModManager/Log.txt",
                    "ue4ss/UE4SS.log", "UE4SS.log", "Mods/mods.log", "logs/latest.log"):
            logs += [p for p in root.rglob(rel.split("/")[-1]) if p.as_posix().endswith(rel)][:1]
    logs = [p for p in logs if p.is_file()]
    if not logs:
        return {"mod": mod, "verdict": "no-log", "logs": [],
                "note": "No loader log found. Run the game once with the loader, or pass --log."}
    # whole-identifier match: "Missing" must not hit "MissingMethodException" or "Other.Missing"
    m = r"(?<![\w.])" + re.escape(mod) + r"(?![\w])"
    hits, errs = [], []
    for p in logs:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if re.search(ERR_RE.format(m=m), line, re.I):
                errs.append(line.strip()[:200])
            elif any(re.search(x.format(m=m), line, re.I) for x in LOAD_LINES):
                hits.append(line.strip()[:200])
    age = min(time.time() - p.stat().st_mtime for p in logs)
    verdict = "errored" if errs else "loaded" if hits else "not-seen"
    r = {"mod": mod, "verdict": verdict, "logs": [str(p) for p in logs],
         "load_lines": hits[:5], "error_lines": errs[:5], "log_age_hours": round(age / 3600, 1)}
    if age > 86400:
        r["note"] = "Log is over a day old: run the game again before trusting it."
    return r


def publish_prep(kind, folder, **kw):
    folder = Path(folder).resolve()
    if kind == "workshop":
        if not kw.get("changenote"):
            raise ValueError("--changenote is required for a Workshop item")
        q = lambda s: str(s).replace("\\", "/").replace('"', "'")  # noqa: E731
        vals = {"appid": kw["appid"], "publishedfileid": kw.get("item") or "0",
                "contentfolder": str(folder), "previewfile": kw.get("preview") or "",
                "visibility": kw.get("visibility") or "2", "title": kw.get("title") or folder.name,
                "description": kw.get("description") or "", "changenote": kw["changenote"]}
        body = "".join(f'\t"{k}"\t\t"{q(v)}"\n' for k, v in vals.items())
        out = folder.parent / f"{folder.name}.workshop.vdf"
        out.write_text('"workshopitem"\n{\n' + body + "}\n", encoding="utf-8")
        cmd = f'steamcmd +login <user> +workshop_build_item "{out.as_posix()}" +quit'
    elif kind == "thunderstore":
        ver = kw.get("version") or ""
        if not re.fullmatch(r"\d+\.\d+\.\d+", ver):
            raise ValueError("--version must be MAJOR.MINOR.PATCH")
        name = kw.get("title") or folder.name
        if not re.fullmatch(r"[A-Za-z0-9_]+", name):
            raise ValueError("Thunderstore name: letters, digits, underscore only")
        man = {"name": name, "version_number": ver, "website_url": kw.get("url") or "",
               "description": (kw.get("description") or "")[:250], "dependencies": kw.get("deps") or []}
        out = folder / "manifest.json"
        out.write_text(json.dumps(man, indent=2), encoding="utf-8")
        missing = [f for f in ("icon.png", "README.md") if not (folder / f).is_file()]
        cmd = "tcli build, then tcli publish (needs TCLI_AUTH_TOKEN)"
        if missing:
            return {"wrote": str(out), "missing": missing, "next": cmd,
                    "note": "Thunderstore also needs a 256x256 icon.png and README.md."}
    else:
        raise ValueError(f"unknown kind: {kind}")
    return {"wrote": str(out), "next": cmd,
            "note": "Prepared only. Upload needs the owner's login and explicit go-ahead."}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="mw.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan", help="identify engine, runtime, anti-cheat and loaders")
    s.add_argument("install")
    s.add_argument("--json", action="store_true")
    b = sub.add_parser("backup", help="copy saves/game files with a hash manifest")
    b.add_argument("out")
    b.add_argument("paths", nargs="+")
    b.add_argument("--build", help="game build id (Steam buildid) to record")
    r = sub.add_parser("restore", help="restore a backup, or --verify only")
    r.add_argument("backup")
    r.add_argument("--verify", action="store_true")
    p = sub.add_parser("proof", help="did the loader log the mod?")
    p.add_argument("install")
    p.add_argument("--mod", required=True)
    p.add_argument("--log")
    q = sub.add_parser("publish-prep", help="write a Workshop VDF or Thunderstore manifest")
    q.add_argument("kind", choices=["workshop", "thunderstore"])
    q.add_argument("folder")
    for o in ("appid", "item", "preview", "visibility", "title", "description",
              "changenote", "version", "url"):
        q.add_argument("--" + o)
    q.add_argument("--dep", action="append", dest="deps")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "backup":
            return _out(backup(a.out, a.paths, a.build), 0)
        if a.cmd == "restore":
            res = restore(a.backup, a.verify)
            return _out(res, 0 if res["backup_ok"] and (not a.verify or not res["live_differs"]) else 1)
        if a.cmd == "proof":
            res = proof(a.install, a.mod, a.log)
            return _out(res, 0 if res["verdict"] == "loaded" else 1)
        if a.cmd == "publish-prep":
            if a.kind == "workshop" and not a.appid:
                raise ValueError("--appid is required")
            kw = {k: v for k, v in vars(a).items() if k not in ("cmd", "kind", "folder")}
            return _out(publish_prep(a.kind, a.folder, **kw), 0)
    except (ValueError, OSError, KeyError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 3
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


def _out(res, code):
    print(json.dumps(res, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
