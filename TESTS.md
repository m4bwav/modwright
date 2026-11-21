# Tests

- Unit: `python -m unittest discover -s tests` (16 tests, fake installs built in temp folders).
- Skill evals: `evals/evals.json` (4 cases: anticheat, proof, backup, loader; fixtures in `evals/fixtures`). Each run works on a fresh copy.
- T-001 2026-11-21, one run each, graded by the parent session on evergreen-tester reports: with skill 4/4, bare baseline 4/4. With the skill, agents ran `mw.py scan` (exit 2 on arena), `mw.py proof`, `mw.py backup` and `restore --verify`. No trigger proxy run: the plugin was not installed during the run.
