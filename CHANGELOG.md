# Changelog

## 0.1.2 (2026-11-24)
- SKILL.md step 9: when a mod is republished, update the description, screenshots and previews, videos, change note, changelog, version, README, wiki and release with it, and report each. Garry's Mod gmad/gmpublish route and a Steamworks UGC updater for what gmpublish cannot set.
- README: link the People Playground portal kit as a worked example, so readers can see a full run from scan to Workshop.

## 0.1.1 (2026-11-21)
- Fix: `publish-prep workshop` without `--visibility` wrote "None"; it now defaults to 2 (private), as SKILL.md says.
- Fix: `proof` matched the mod name as a substring, so `--mod Missing` hit another mod's `MissingMethodException`; it now matches whole identifiers.
- Regression tests for both.

## 0.1.0 (2026-11-21)
- First release: hub skill `modwright` and `mw.py` (scan for engine, runtime, anti-cheat and loaders; backup and restore with SHA-256 manifests; proof from loader logs; publish-prep for Workshop VDF and Thunderstore manifest).
- Eval suite of four cases on fake installs, with no-skill baselines.
