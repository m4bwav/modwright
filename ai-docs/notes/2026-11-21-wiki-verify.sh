#!/usr/bin/env bash
# Runs every wiki example against modwright at tag v0.1.0 in a fresh scratch copy.
# Usage: bash 2026-11-21-wiki-verify.sh <modwright clone> <scratch dir>
set -u
REPO="$1"; S="$2"; rm -rf "$S"; mkdir -p "$S"
git -C "$REPO" archive v0.1.0 | tar x -C "$S"
cd "$S/evals/fixtures"; MW="python ../../skills/modwright/scripts/mw.py"
run() { echo "## $*"; "$@"; echo "exit $?"; echo; }
run $MW scan farm
run $MW scan arena
run $MW scan rpg
run $MW scan farm --json
run $MW scan nope
run $MW proof farm --mod FastHarvest
run $MW proof farm --mod MoreSeeds
run $MW proof farm --mod CoolMod
run $MW proof farm --mod Missing
run $MW proof rpg --mod CoolMod
run $MW backup bk farm/saves --build 123456
echo x >> farm/saves/slot1.sav
run $MW restore bk --verify
run $MW restore bk
run $MW restore bk --verify
run $MW backup bk farm/saves
mkdir -p mymod ws
run $MW publish-prep thunderstore mymod --version 1.0.0 --title CoolMod
cat mymod/manifest.json; echo
run $MW publish-prep thunderstore mymod --version 1.0 --title CoolMod
run $MW publish-prep workshop ws --changenote First
run $MW publish-prep workshop ws --appid 480 --changenote First
cat ws.workshop.vdf
