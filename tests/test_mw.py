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


class Safety(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = Path(self.d.name)

    def tearDown(self):
        self.d.cleanup()

    def w(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def test_backup_restore_roundtrip(self):
        save = self.w("saves/slot1.sav", "hp=10")
        cfg = self.w("game/config.ini", "a=1")
        r = mw.backup(self.root / "bk", [str(self.root / "saves"), str(cfg)], build="123")
        self.assertEqual(r["files"], 2)
        save.write_text("hp=0", encoding="utf-8")
        cfg.unlink()
        v = mw.restore(self.root / "bk", verify_only=True)
        self.assertEqual(len(v["live_differs"]), 2)
        self.assertEqual(save.read_text(encoding="utf-8"), "hp=0")
        r = mw.restore(self.root / "bk")
        self.assertEqual(r["restored"], 2)
        self.assertEqual(save.read_text(encoding="utf-8"), "hp=10")
        self.assertTrue(cfg.is_file())
        self.assertEqual(r["build"], "123")

    def test_backup_corruption_detected(self):
        self.w("saves/a.sav", "x")
        mw.backup(self.root / "bk", [str(self.root / "saves")])
        (self.root / "bk/files/0/a.sav").write_text("tampered", encoding="utf-8")
        self.assertFalse(mw.restore(self.root / "bk")["backup_ok"])

    def test_backup_refuses_nonempty(self):
        self.w("bk/x", "1")
        self.w("s/a", "1")
        with self.assertRaises(ValueError):
            mw.backup(self.root / "bk", [str(self.root / "s")])

    def test_proof_bepinex_loaded(self):
        self.w("BepInEx/LogOutput.log", "[Info   :   BepInEx] Loading [CoolMod 1.2.0]\n"
               "[Message:   BepInEx] Chainloader startup complete\n")
        self.assertEqual(mw.proof(self.root, "CoolMod")["verdict"], "loaded")
        self.assertEqual(mw.proof(self.root, "OtherMod")["verdict"], "not-seen")

    def test_proof_errored(self):
        self.w("MelonLoader/Latest.log", "[12:00] Failed to load Melon Assembly CoolMod.dll\n")
        self.assertEqual(mw.proof(self.root, "CoolMod")["verdict"], "errored")

    def test_proof_name_is_whole_identifier(self):
        # 0.1.0 bug: --mod Missing matched another mod's MissingMethodException
        self.w("BepInEx/LogOutput.log", "[Info   :   BepInEx] Loading [Missing 1.0.0]\n"
               "[Error  : Other] System.MissingMethodException: Other.Missing.Run\n")
        self.assertEqual(mw.proof(self.root, "Missing")["verdict"], "loaded")

    def test_publish_workshop_cli_default_visibility(self):
        # 0.1.0 bug: CLI without --visibility wrote "None"
        self.w("mod/a.txt", "1")
        self.assertEqual(mw.main(["publish-prep", "workshop", str(self.root / "mod"),
                                  "--appid", "1", "--changenote", "x"]), 0)
        vdf = (self.root / "mod.workshop.vdf").read_text(encoding="utf-8")
        self.assertIn('"visibility"\t\t"2"', vdf)

    def test_proof_ue4ss_and_nolog(self):
        self.assertEqual(mw.proof(self.root, "X")["verdict"], "no-log")
        self.w("Game/Binaries/Win64/ue4ss/UE4SS.log", "Starting Lua mod 'FastTravel'\n")
        self.assertEqual(mw.proof(self.root, "FastTravel")["verdict"], "loaded")

    def test_publish_workshop_needs_changenote(self):
        self.w("mod/a.txt", "1")
        with self.assertRaises(ValueError):
            mw.publish_prep("workshop", self.root / "mod", appid="1")
        r = mw.publish_prep("workshop", self.root / "mod", appid="1", changenote="first")
        vdf = Path(r["wrote"]).read_text(encoding="utf-8")
        self.assertIn('"changenote"\t\t"first"', vdf)
        self.assertIn('"publishedfileid"\t\t"0"', vdf)

    def test_publish_thunderstore(self):
        self.w("pkg/README.md", "hi")
        with self.assertRaises(ValueError):
            mw.publish_prep("thunderstore", self.root / "pkg", version="1.0")
        r = mw.publish_prep("thunderstore", self.root / "pkg", version="1.0.0", title="Cool_Mod")
        self.assertEqual(r["missing"], ["icon.png"])


if __name__ == "__main__":
    unittest.main()
