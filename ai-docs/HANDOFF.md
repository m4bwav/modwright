# modwright handoff

Status: released 0.1.0 (chain state: D:/m4bwa/Claude/Projects/Ai/plugin-backlog/ai-docs/new5/modwright/HANDOFF.md)

## Done
- mw.py scan (PR #1).
- Session 3 (2026-11-21): mw.py backup/restore (SHA-256 manifest, build id), proof (BepInEx, MelonLoader, UMM, UE4SS, mods.log, latest.log; loaded/errored/not-seen/no-log, stale over 24 h), publish-prep (Workshop VDF needs changenote, Thunderstore manifest checks); 16 tests; hub SKILL.md; plugin.json 0.1.0.

- Session 4 (2026-11-21): evergreen unit, 4 evals with baselines (4/4, 4/4), README banner, LICENSE, SECURITY.md; v0.1.0 tagged and released; installed modwright@mark-local. Secret scan clean.
- Session 5 (2026-11-21): GitHub wiki written and live (9 pages, verified at v0.1.0; note ai-docs/notes/2026-11-21-github-wiki.md); README: marketplace.json added for the install line, undocumented options and exit codes, wiki link; pytest.ini limits collection to tests/.

## Next
- Fix bugs found by the wiki run: publish-prep visibility defaults to None, proof substring match (see the wiki note).
- Repo is public; wiki done. Backlog: plugin-backlog existing-plugins.md, modwright section.

Tests: python -m unittest tests/test_mw.py (no CI on the private repo).
