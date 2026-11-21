# AGENTS.md

Rules for any AI agent working in this repository. `CLAUDE.md` imports this file; `.github/copilot-instructions.md` points here.

## What this is

modwright: one hub skill, `skills/modwright/`, with `scripts/mw.py` (standard library only: scan, backup, restore, proof, publish-prep). `evals/` holds the skill eval suite (fake game installs), `ai-docs/` the notes, plans and handoff (start with `ai-docs/HANDOFF.md`).

## Rules

- Python 3.9+, standard library only. UTF-8, LF. Exit 2 from scan means anti-cheat: stop.
- Every change gets a test: `python -m unittest discover -s tests`.
- Evergreen unit at the root: read `evergreen.json` before editing; changes go in CHANGELOG with the reason, lessons in LEARNINGS.
- A release bumps `.claude-plugin/plugin.json` and CHANGELOG together.
- Never help bypass anti-cheat or cheat in online play. Plain short sentences, no em dashes, relative links. No AI attribution anywhere.
