import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ScriptContractTests(unittest.TestCase):
    def test_linux_build_checks_clang_stage_before_find(self) -> None:
        script = (ROOT / "scripts/linux_build.sh").read_text(encoding="utf-8")

        check_index = script.index('if [[ ! -d "$STAGE/xcode/clang" ]]')
        find_index = script.index('CLANG_VERSION_DIR="$(find "$STAGE/xcode/clang"')

        self.assertLess(check_index, find_index)

    def test_mac_verify_extracts_accessibility_tree_from_xcodebuild_log(self) -> None:
        script = (ROOT / "scripts/mac_verify.sh").read_text(encoding="utf-8")

        self.assertIn("test-without-building.log", script)
        self.assertIn("ios_linux_harness.cli.extract_accessibility_tree", script)
        self.assertIn("accessibility-tree.txt", script)

    def test_makefile_has_xtool_toolset_staging_target(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("stage-xtool-toolset:", makefile)
        self.assertIn("scripts/stage_xtool_toolset.sh", makefile)


if __name__ == "__main__":
    unittest.main()
