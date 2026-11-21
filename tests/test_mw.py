import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "modwright" / "scripts"))
import mw  # noqa: E402


class Tree:
    def __init__(self, paths):
        self.d = tempfile.TemporaryDirectory()
        for p in paths:
            f = Path(self.d.name) / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(b"")

    def __enter__(self):
        return self.d.name

    def __exit__(self, *a):
        self.d.cleanup()


class Scan(unittest.TestCase):
    def check(self, paths, **want):
        with Tree(paths) as d:
            r = mw.scan(d)
        for k, v in want.items():
            self.assertEqual(r[k], v, (k, r))
        return r

    def test_unity_mono(self):
        self.check(["Game.exe", "UnityPlayer.dll", "Game_Data/Managed/Assembly-CSharp.dll"],
                   engine="Unity", runtime="Mono", recommended_loader="BepInEx 5 (or MelonLoader)")

    def test_unity_il2cpp_bepinex6(self):
        self.check(["UnityPlayer.dll", "GameAssembly.dll",
                    "Game_Data/il2cpp_data/Metadata/global-metadata.dat",
                    "BepInEx/core/BepInEx.Unity.IL2CPP.dll"],
                   runtime="IL2CPP", loaders_installed=["BepInEx 6 (IL2CPP)"])

    def test_bepinex5_log(self):
        r = self.check(["UnityPlayer.dll", "BepInEx/core/BepInEx.dll"], loaders_installed=["BepInEx 5"])
        self.assertEqual(r["loader_logs"], ["BepInEx/LogOutput.log"])

    def test_unreal(self):
        self.check(["Game/Binaries/Win64/Game-Win64-Shipping.exe", "Game/Content/Paks/Game.pak"],
                   engine="Unreal")

    def test_godot(self):
        self.check(["game.exe", "game.pck"], engine="Godot")

    def test_anticheat_exit_code(self):
        with Tree(["UnityPlayer.dll", "EasyAntiCheat/settings.json"]) as d:
            self.assertEqual(mw.main(["scan", d]), 2)
            self.assertEqual(mw.scan(d)["anticheat"], ["Easy Anti-Cheat"])

    def test_other_engines(self):
        self.check(["data.win"], engine="GameMaker")
        self.check(["www/js/rpg_core.js"], engine="RPG Maker MV/MZ")
        self.check(["Skyrim.esm"], engine="Bethesda Creation")

    def test_unknown_and_bad_path(self):
        self.check(["readme.txt"], engine="unknown", loaders_installed=[])
        self.assertEqual(mw.main(["scan", "Z:/no/such/dir"]), 3)


if __name__ == "__main__":
    unittest.main()
