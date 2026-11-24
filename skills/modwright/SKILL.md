---
name: modwright
description: "Mod any PC game safely and prove it works: find the install, engine and runtime (Unity Mono/IL2CPP, Unreal, Godot, GameMaker, Source...), stop at anti-cheat, back up saves with SHA-256 hashes first, decompile before naming a patch target, pick the loader (BepInEx, MelonLoader, UE4SS, Harmony), prove the mod loaded from the loader log, check EULA and mod policy, prepare a Workshop VDF or Thunderstore manifest without uploading. mw.py scan, backup, restore, proof, publish-prep. Use on 'mod this game', 'make a BepInEx plugin', 'which mod loader', 'did my mod load', 'back up my saves before modding', 'upload my mod to the Workshop'. Not for Minecraft (minewright), Roblox (roblox-agent), MADNESS Project Nexus (madnesswright) or mod art (artwright, pixelwright, polywright)."
---

# Modwright

The safety and proof layer every game mod needs. A mod is done only when a loader log line names it and the owner has seen it work in game.

`MW` means `python "<this folder>/scripts/mw.py"` (Python 3.9+, stdlib). Commands print JSON. Exit 0 ok, 1 check failed, 2 anti-cheat (stop), 3 bad input.

## Route first

- Minecraft (Forge, Fabric, NeoForge): minewright. Roblox: roblox-agent. MADNESS Project Nexus: madnesswright (the worked per-game recipe this skill generalises).
- Textures, sprites, models for the mod: artwright, pixelwright, polywright.

## Steps

1. **Find the install and the branch.** Steam: `steamapps/common/<Game>`, build id in `steamapps/appmanifest_<appid>.acf` (`buildid`); note a beta branch. Mods break on updates, so record the build.
2. **Scan.** `MW scan "<install>"`. Exit 2 means anti-cheat (EAC, BattlEye, Vanguard...): stop. No DLL proxy, injection or memory patching; only the game's official mod route, offline or single player, and say why. Online multiplayer cheats are refused outright.
3. **Legality.** Read the EULA or mod policy before shipping anything: modding for personal use is usually tolerated; redistributing game assets or code is not. Ship patches and your own files, never the game's DLLs or ripped assets.
4. **Back up before touching anything.** `MW backup <out> <savesdir> <file-you-will-touch>... --build <buildid>`. `MW restore <out> --verify` shows what changed; `MW restore <out>` puts it back. Saves often live outside the install (`%USERPROFILE%/AppData/LocalLow/<Company>/<Game>`, `Documents/My Games`); find them first.
5. **Decompile before naming a patch target.** Never guess a class or method name. Unity Mono: ILSpy/dnSpyEx on `<Game>_Data/Managed/Assembly-CSharp.dll`. IL2CPP: Il2CppDumper or Cpp2IL first. Unreal: FModel, UE4SS header dump. Godot: gdsdecomp. Quote the signature you patch.
6. **Loader.** Take `recommended_loader` from the scan. BepInEx 5 for Unity Mono, BepInEx 6 or MelonLoader for IL2CPP, UE4SS (plus pak mods in `Content/Paks/~mods`) for Unreal, Harmony alone when the game has its own loader. Pin the loader version in the mod's README.
7. **Prove it loaded.** Have the owner run the game, then `MW proof "<install>" --mod <Name>`. `loaded` needs a log line naming the mod; `errored` shows the lines; `not-seen` or `no-log` means it did not load, whatever the build said. A log over a day old is stale. Then ask what they saw in game.
8. **Publish only on a go.** `MW publish-prep workshop <folder> --appid N --changenote "..."` writes a VDF (`--item` to update, visibility 2 private by default); `MW publish-prep thunderstore <folder> --version 1.0.0 --title Name` writes `manifest.json` and lists missing `icon.png`/`README.md`. The upload itself (steamcmd login, `tcli publish`, Nexus, mod.io) needs the owner's account and explicit go-ahead.
9. **Republish the page, not just the files.** Every update of a published mod also updates what players read: description (what's new, what it needs, credits and licences for photos, models and AI tools), screenshots and preview images (current build; Steam appends previews, so remove stale ones), videos or GIFs if any show old content, the change note on the upload, the changelog in the repository and on the page, version number, tags, the README and wiki, and a tagged release where the source lives. List each one as updated or unchanged in the report. Garry's Mod: `gmad create -folder <addon> -out x.gma`, `gmpublish update -id N -addon x.gma -changes "..."`; gmpublish cannot set description, visibility or previews, so use the Steamworks UGC API (worked example: `tools/workshop_update.py` in m4bwav/gcs-gmod).

## Rules

- No claim of "works" without step 7.
- Restore the backup before telling the owner to verify the game files through Steam; never delete saves.
- One mod change per test run, so a failing log points at one thing.

## Maintenance

Evergreen unit at the repository root: `evergreen.json`, RESEARCH.md, CHANGELOG.md, LEARNINGS.md, TESTS.md (evals in `evals/`). Refresh every 30 days; check volatile loader facts against their docs before relying on them.
