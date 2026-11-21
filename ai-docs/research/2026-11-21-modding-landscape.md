# Modding landscape for modwright (2026-11-21)

Research for a general "mod any PC game" agent plugin, generalised from madnesswright
(the sibling madnesswright plugin: one game, MADNESS: Project Nexus. Its skills are madnesswright
(official mod folder + info.txt + MadCards, save backup first, prove load via Mods/mods.log, Steam Workshop),
madnesswright-modtools (Unity 2019 ModTools AssetBundles + Harmony 2.4.2 assemblies) and madnesswright-scenes (SceneTools levels)).
Minecraft goes to the sibling `minewright`, Roblox to `roblox-agent`.

Confidence tags: [web] = seen in a web search on 2026-11-21 (URL given). [known] = stable prior knowledge,
not re-verified today, so check it before codifying.

## 1. Existing agent skills / MCP servers (do not duplicate)

| Project | What | Overlap |
|---|---|---|
| **rehan-remade/universal-modder** | MIT Claude Code plugin, about 9-9.6K stars, 12 engine playbooks (Unity, Unreal, Bethesda, Source, Godot, Minecraft, AoE2...), skills `mod-any-game`, `game-recon`, `asset-pipeline`. Tests in the running game. Uses fal.ai art (FAL_KEY), Blender and ffmpeg. Has a `um` CLI via uv and also works with Codex/Gemini/Cursor | **Direct competitor, HIGH overlap.** Read its README and skills before scoping. [web] https://claudemarketplaces.com/plugins/rehan-remade-universal-modder , https://vgtimes.com/news/169424-universal-modder-gives-claude-code-a-workflow-for-creating-and-testing-pc-game-mods.html , https://enterprisedna.co/resources/ai-pulse/ai-pulse-2026-09-30-claude-skill-mods-any-pc-game (2026-09-30) |
| josiahsiegel `unity-modding` skill | Unity architecture guide: mod APIs, asset loading, Harmony via BepInEx/MelonLoader, distribution | Medium (a guide, no tooling) [web] https://skills.sh/josiahsiegel/claude-plugin-marketplace/unity-modding |
| jord-jd `game-modding` skill | Generic. Contents not verified | Unknown [web] https://www.skills.sh/jord-jd/jord-skills/game-modding |
| viktor-ferenczi `se-dev-skills` | Space Engineers 1 plugins, mods and scripts | Single game [web] https://agskills.dev/viktor-ferenczi/se-dev-skills/se-dev-mod |
| Orinks/unity-scope | BepInEx 5 plugin that exposes a running Mono Unity game's scene graph over local HTTP as an MCP server. IL2CPP planned | Complement (runtime inspection). Recommend it, don't rebuild it [web] https://github.com/Orinks/unity-scope |
| nowsprinting gameplay-mcp | MCP embedded in a player build you own | Not modding [web] https://nowsprinting.github.io/gameplay-mcp/ |
| CoplayDev/unity-mcp, ivanmurzak/unity-mcp, Signal-Loop UnityCodeMCPServer | Unity **Editor** bridges | Not modding. the unity-agent plugin covers the editor [web] |
| EpicGames unreal-engine-skills-for-claude-code | For building UE projects, not modding shipped games | None [web] https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin |
| Nexus GitHub Action (upload) | Official CI push of new files to an existing mod page | Use it, don't rebuild it [web] (see section 4) |

No UE4SS-specific skill was found. Gaps against universal-modder still to verify: strict "prove it loaded" log
checks, save and backup safety gates, an anti-cheat refusal list, host upload automation (Workshop VDF,
tcli, Nexus API), and per-game recipe files that build up over time (madnesswright would be recipe #1).

## 2. Loaders and how each proves a mod loaded

| Loader | Reach | Install | Proof of load (log) |
|---|---|---|---|
| **BepInEx 5.4.x** (stable) | Unity Mono (most pre-2020 games and many indie games) | Unzip winhttp.dll + doorstop_config.ini + BepInEx/ next to the exe. Plugins go in `BepInEx/plugins/` | `BepInEx/LogOutput.log` ("Chainloader startup complete", "Loading [Name x.y]"). Console is enabled in `BepInEx/config/BepInEx.cfg` [known] |
| **BepInEx 6** (bleeding edge, builds.bepinex.dev) | Unity Mono + **IL2CPP** (via Il2CppInterop), also .NET (XNA/FNA) | Same layout. The first IL2CPP run generates `BepInEx/interop/` (slow) | `BepInEx/LogOutput.log`. BE builds are not compatible with 6.0.0-pre.1. The newest IL2CPP metadata (v39) needs pinned BE builds (#785/#788 seen on Thunderstore) [web] https://thunderstore.io/c/aska/p/BepInEx/BepInExPack_IL2CPP/v/6.0.788/ , https://www.github.com/BepInEx/BepInEx/discussions/704 |
| **MelonLoader** (0.6/0.7) | Unity Mono + IL2CPP | Installer or version.dll proxy. Folders `Mods/`, `Plugins/`, `UserLibs/` | `MelonLoader/Latest.log` (+ `MelonLoader/Logs/`) lists each loaded Melon assembly [known] |
| **Harmony 2.x standalone** | Any .NET game with its own mod loader (RimWorld, madnesswright, Stardew via SMAPI) | Reference 0Harmony.dll and patch from the loader's entry point | The game or loader log. `Harmony.DEBUG=true` writes `harmony.log.txt` to the Desktop [known] |
| **Unity Mod Manager** | Unity Mono, older titles (Pathfinder, Rogue Trader). Injects through its installer. Mods live in `Mods/<id>/Info.json` | | `UnityModManager/Log.txt` + the in-game Ctrl+F10 panel [known] |
| **UE4SS (RE-UE4SS)** | UE4/UE5 Win64. Lua + C++ mods, live property viewer, header/USMAP dump | dwmapi.dll/UE4SS.dll + `ue4ss/` next to `<Game>/Binaries/Win64/*-Shipping.exe`. Mods go in `ue4ss/Mods/` and are enabled via `mods.txt` (`Name : 1`) or `enabled.txt`. mods.txt is being phased out | `ue4ss/UE4SS.log` ("Starting Lua mod 'X'"). Use the latest non-experimental release. An experimental-latest tag also exists [web] https://github.com/UE4SS-RE/RE-UE4SS/releases , https://docs.ue4ss.com/dev/installation-guide.html |
| UE pak mods (no loader) | Asset replacement | `Content/Paks/~mods/Name_P.pak` (UE5 IoStore: .pak+.utoc+.ucas) | No log. Verify in-game or through UE4SS |
| Fabric / NeoForge | Minecraft only, so **route to minewright** | | `logs/latest.log` |
| Data/Lua mods | Factorio (`mods/` + `factorio-current.log`), Paradox (`.mod` descriptor, `Documents/Paradox Interactive/<game>/logs/error.log`), Bethesda (plugins.txt, SKSE/F4SE logs in Documents/My Games/...), Source (`addons/`, `-condebug` console.log), Godot (`res://` overrides via .pck, `--main-pack`), RPG Maker (js/plugins) | Official mod folders | Game-specific logs [known] |

Rule for the skill: never claim "it works" without a log line naming the mod (madnesswright's
mods.log rule, generalised), followed by an in-game observation.

## 3. Engine identification from install files [known]

| Evidence in install dir | Engine / runtime | Decompile / inspect |
|---|---|---|
| `UnityPlayer.dll`, `<Game>_Data/` | Unity | Version from `<Game>_Data/globalgamemanagers` or the exe's file properties |
| `<Game>_Data/Managed/Assembly-CSharp.dll` | Unity **Mono**: BepInEx 5 / MelonLoader | `ilspycmd -p -o out Assembly-CSharp.dll` (dotnet tool). dnSpyEx for debugging |
| `GameAssembly.dll` + `<Game>_Data/il2cpp_data/Metadata/global-metadata.dat` | Unity **IL2CPP**: BepInEx 6 / MelonLoader | Cpp2IL (`--output-as dummydll`), Il2CppDumper (fails on new metadata or obfuscation). Ghidra/IDA for method bodies |
| `<Game>/Binaries/Win64/*-Shipping.exe`, `Content/Paks/*.pak`, `.utoc/.ucas` | Unreal 4/5 | FModel (needs the AES key if encrypted, plus a USMAP from UE4SS for UE5), UAssetGUI / UAssetAPI, repak/retoc. UE version from the exe's properties |
| `*.pck` or an exe with an embedded pck, `godot` strings | Godot | gdsdecomp (GDRE Tools) recovers the project and GDScript |
| Managed exe, `Content/*.xnb`, FNA.dll/MonoGame.Framework.dll | XNA/FNA/MonoGame | ILSpy. BepInEx 6 .NET or Harmony |
| `*.rpa`, `renpy/` | Ren'Py | unrpa, unrpyc |
| `data.win` | GameMaker | UndertaleModTool |
| `www/js/rpg_*.js` or `js/rmmz_*.js` | RPG Maker MV/MZ | Plain JS |
| `*.vpk`, `gameinfo.txt` | Source / Source 2 | VPKEdit, Source 2 Viewer |
| `*.bsa/*.ba2`, `*.esm` | Bethesda Creation | xEdit, BSArch. SKSE/F4SE |
| `EasyAntiCheat/`, `BattlEye/`, `mhypbase.dll`, `vgk.sys` | **Anti-cheat present: stop gate** | - |
| `*.jar` + `.minecraft` | Minecraft: minewright | - |

A small stdlib `scan` script that prints the engine, runtime, recommended loader, anti-cheat flag and any
installed mod loader is the core tool (cheap, testable, deterministic).

## 4. Hosts and upload automation

- **Steam Workshop** [known]: `steamcmd +login <user> +workshop_build_item item.vdf +quit`. VDF keys:
  `appid`, `publishedfileid` (0 = new item), `contentfolder`, `previewfile`, `visibility` (0 public,
  1 friends, 2 private, 3 unlisted), `title`, `description`, `changenote`. It only works if the game
  allows Workshop uploads through steamcmd. Many games ship their own uploader instead (madnesswright uses the game's own).
  It needs the user's Steam login and Steam Guard, so the agent prepares the VDF and the user runs or approves it.
  A new uploader must accept the Workshop legal agreement once in a browser.
- **Nexus Mods** [web]: the Upload API is in open beta for **updating existing mods** (new file versions) with
  per-user API keys, plus an official GitHub Action. There is no full create flow yet, so mod pages are
  still created by hand. https://www.nexusmods.com/spaceengineers/news/15454 (the date was not visible in results;
  check the Nexus API docs before codifying).
- **Thunderstore** [web]: `dotnet tool install -g tcli`. Config is `thunderstore.toml` ([package], [build],
  [publish] communities). Run `tcli build`, then `tcli publish --token` or set `TCLI_AUTH_TOKEN` (a service-account
  token from the team settings). `--file` publishes a prebuilt zip. A package needs manifest.json, a 256x256 icon.png and
  README.md. https://github.com/thunderstore-io/thunderstore-cli , https://www.nuget.org/packages/tcli
- **mod.io** [web]: REST `POST /games/{game}/mods/{mod}/files` (multipart; large files use a multipart session
  with 50 MiB parts). Writes need an OAuth2 access token, and the user must be a team manager or admin on the mod.
  Content falls under the mod.io Terms of Use. https://docs.mod.io/restapi/docs/add-modfile
- **CurseForge** [web]: an author API token (X-Api-Token header) from the API Tokens page, then
  `POST https://<game>.curseforge.com/api/projects/{id}/upload-file` as multipart (metadata JSON + file). It
  returns the file id. Mostly Minecraft and WoW (Minecraft goes to minewright).
  https://support.curseforge.com/support/solutions/articles/9000197321-curseforge-api
- Terms on automated upload: every host above offers token-based author uploads, so scripted uploads
  of the user's own mods are allowed. None permits scraping or re-uploading other people's mods. Policy for
  modwright: build the package and the exact command, and publish only on the user's explicit go-ahead
  (registry publishing always needs the owner's OK).

## 5. Safety and legality [known unless marked]

- **Anti-cheat**: EAC, BattlEye, Vanguard, Ricochet, nProtect, mhyprot. Injecting DLLs (the winhttp/
  version.dll proxies that BepInEx, MelonLoader and UE4SS use) into a protected game can trigger
  **permanent account bans**, in some titles even offline. The skill must detect `EasyAntiCheat/`,
  `BattlEye/` and the like, and refuse loader injection unless the game documents an offline or modded mode
  (for example Elden Ring's EAC-off offline launch used by Seamless Co-op). Never mod competitive
  multiplayer clients. Multiplayer is limited to server-side or officially supported modding.
- **EULA**: most EULAs forbid reverse engineering but tolerate single-player mods. Publishers vary
  (Take-Two/Rockstar and Nintendo are hostile; Bethesda, Paradox and Factorio are friendly). The interop exception
  (DMCA 1201(f), EU Software Directive art. 6) is narrow. Never redistribute game assets or
  decompiled code in a mod package. Ship patches and the user's own assets only.
- **Defender/AV**: proxy DLLs (winhttp.dll, version.dll, dwmapi.dll, dinput8.dll) and
  doorstop loaders are often flagged as false-positive trojans. Advise downloading loaders
  only from official GitHub releases and checking the hash, and adding a narrow folder exclusion only if the user
  chooses to. Never disable Defender globally.
- **Backups**: before any change, copy the saves (Steam: `<userdata>/<id>/<appid>/remote`, Unity:
  `%USERPROFILE%/AppData/LocalLow/<Company>/<Game>`, UE: `%LOCALAPPDATA%/<Game>/Saved/SaveGames`,
  Documents/My Games). Record vanilla file hashes so an uninstall restores the game exactly. Steam
  "Verify integrity" is the last resort. Rule: don't walk AppData beyond the one game's
  save folder without approval.
- Game updates break mods: patches change the IL2CPP metadata and UE versions. Record the game build id
  (Steam `appmanifest_<appid>.acf` buildid) with each recipe.

## Scope recommendations

1. **Set modwright apart from universal-modder instead of cloning it.** Read its repo first. Position modwright
   as the verification-and-safety layer: `mw.py scan` (engine, runtime, anti-cheat gate, loader
   pick), backup and restore with hashes, and per-loader log checks that prove a mod loaded. Skip AI art
   generation (artwright, pixelwright and polywright already cover it).
2. **Cover the loaders with the widest reach first**: BepInEx 5/6 (+Harmony), MelonLoader,
   UE4SS (+pak), and official data/Lua mod folders. Route Minecraft to minewright and Roblox to
   roblox-agent, and keep madnesswright as the first per-game recipe file (recipes/<game>.md).
3. **Publishing is prepare-then-ask**: generate the Workshop VDF, Thunderstore toml/manifest, Nexus
   update-API call and mod.io/CurseForge payloads, and run them only on the user's explicit go-ahead. Hard-refuse
   games protected by anti-cheat in multiplayer.
