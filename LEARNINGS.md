# Learnings

- L-001 `strong-baseline` (2026-11-21): on fake installs the bare model already stops at anti-cheat, reads BepInEx logs and recommends UE4SS. The skill's gain is routing and repeatability: a hash manifest with `restore --verify` instead of an ad hoc sha256sum file, a stale-log check, and exit codes a calling agent can act on.
- L-002 `proof-skips-decompile-hint` (2026-11-21): with the skill, the errored-mod eval reported the MissingMethodException but did not suggest decompiling to find the new signature. Candidate edit for step 7 if it repeats.
