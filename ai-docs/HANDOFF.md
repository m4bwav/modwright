# modwright handoff

Status: 0.1.0 released 2026-11-21. Public repo with a GitHub wiki (9 pages, verified at v0.1.0; [wiki note](notes/2026-11-21-github-wiki.md)).

## Done
- mw.py scan, backup/restore (SHA-256 manifest, build id), proof (BepInEx, MelonLoader, UMM, UE4SS, mods.log, latest.log), publish-prep (Workshop VDF, Thunderstore manifest checks); hub SKILL.md.
- Evergreen unit, 4 evals with baselines (4/4 with skill, 4/4 bare), README banner, LICENSE, SECURITY.md, marketplace.json, pytest.ini.

## Next
- Fix bugs found by the wiki run: publish-prep visibility defaults to None, proof substring match (see the wiki note).

Tests: python -m unittest tests/test_mw.py (no CI).
