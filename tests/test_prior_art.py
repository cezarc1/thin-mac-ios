import tempfile
import unittest
from pathlib import Path

from ios_linux_harness.prior_art import run_audit


class PriorArtAuditTests(unittest.TestCase):
    def test_known_applecross_xctestrun_surface_is_not_novel(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "rules_applecross/testing").mkdir(parents=True)
            (root / "rules_applecross/testing/BUILD").write_text(
                "ios_xctestrun_runner(name = \"ios_xctestrun_ordered_runner\")\n",
                encoding="utf-8",
            )
            (root / "xctestrunner-bash/lib").mkdir(parents=True)
            (root / "xctestrunner-bash/lib/session.sh").write_text(
                "xcodebuild test-without-building\n"
                "plist_set_bool \"$xctestrun_file\" \"Runner.IsUITestBundle\" true\n",
                encoding="utf-8",
            )
            (root / "xtool").mkdir()
            (root / "xtool/README.md").write_text("Build and install iOS apps from SwiftPM.\n", encoding="utf-8")
            (root / "linux-app").mkdir()
            (root / "linux-app/README.md").write_text("An iOS app that builds on Linux.\n", encoding="utf-8")

            audit = run_audit(prior_art_root=root)
            surfaces = {surface.key: surface for surface in audit.surfaces}

            self.assertEqual("not_novel", surfaces["linux_cross_compile"].verdict)
            self.assertEqual("not_novel", surfaces["xctestrun_ui_test_handoff"].verdict)
            self.assertTrue(surfaces["xctestrun_ui_test_handoff"].prior_art_found)

    def test_publish_gate_requires_audited_sources_and_candidate_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for project in ["rules_applecross", "xctestrunner-bash", "xtool", "linux-app"]:
                (root / project).mkdir()
                (root / project / "README.md").write_text("ordinary source\n", encoding="utf-8")

            audit = run_audit(prior_art_root=root)

            self.assertEqual("pass", audit.publish_gate)
            self.assertGreaterEqual(len(audit.candidate_deltas), 2)
            self.assertIn("visual_accessibility_payload", audit.candidate_deltas)
            self.assertIn("binary_framework_runtime_evidence", audit.candidate_deltas)

    def test_swift_testing_marker_downgrades_swift_testing_novelty_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for project in ["rules_applecross", "xctestrunner-bash", "xtool", "linux-app"]:
                (root / project).mkdir()
                (root / project / "README.md").write_text("ordinary source\n", encoding="utf-8")
            (root / "xtool/README.md").write_text("Links @rpath/Testing.framework/Testing\n", encoding="utf-8")

            audit = run_audit(prior_art_root=root)
            surfaces = {surface.key: surface for surface in audit.surfaces}

            self.assertEqual("not_novel", surfaces["swift_testing_ios_bundle"].verdict)
            self.assertNotIn("swift_testing_ios_bundle", audit.candidate_deltas)


if __name__ == "__main__":
    unittest.main()
