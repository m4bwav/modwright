# GitHub wiki (2026-11-21)

## Summary
How the GitHub wiki was written and verified, and how to update it.

- Wiki: https://github.com/m4bwav/modwright/wiki (local clone of the .wiki.git repo, master, pushed over the placeholder by fast-forward).
- Pages: Home, Getting-Started, Commands, How-Detection-Works, Exit-Codes-And-Errors, Recipes, FAQ, Versions-And-Upgrading, Development, _Sidebar, _Footer. Pages naming the version: _Footer, Versions-And-Upgrading, FAQ (known issues), Getting-Started, Commands.
- Verified against tag v0.1.0 (git archive into scratch) with `2026-11-21-wiki-verify.sh`; output saved as `2026-11-21-wiki-verify.out.txt` (scratch path masked `<scratch>`). wikiwright check, outputs (12 checked, 0 missing) and live (9 pages, 0 failures) all passed. 16 pytest tests pass.
- Update: bump the tag in the script, rerun, `wikiwright.py diffout` old vs new, fix each changed page, bump the footer.

## Facts the README lacked
- `scan` prints text, not JSON, unless `--json` (SKILL.md says "Commands print JSON").
- `proof --log`, `publish-prep --item/--preview/--visibility/--description/--url/--dep`, exit codes.
- Workshop VDF is written next to the folder, not inside.

## Inaccuracies / bugs found (not fixed in code)
1. README install line said "add its parent folder as a local marketplace" but the repo had no marketplace.json (fixed: added).
2. `publish-prep workshop` without `--visibility` writes `"visibility" "None"` (argparse passes None, so `kw.get("visibility","2")` never defaults). SKILL.md claims default 2.
3. `proof` substring match: `--mod Missing` returns errored on another mod's `MissingMethodException` line. Needs word boundaries.
4. SKILL.md "Commands print JSON" is wrong for scan.
