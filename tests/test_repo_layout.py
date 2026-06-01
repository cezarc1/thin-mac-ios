import unittest
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepoLayoutTests(unittest.TestCase):
    def test_python_package_uses_src_layout(self) -> None:
        self.assertTrue((ROOT / "src/ios_linux_harness/__init__.py").exists())
        self.assertFalse((ROOT / "harness").exists())

    def test_swift_fixture_lives_under_fixtures(self) -> None:
        self.assertTrue((ROOT / "fixtures/ios-app/Sources/ExampleApp/ExampleApp.swift").exists())
        self.assertTrue((ROOT / "fixtures/ios-app/Tests/AccessibilityProbeUITests.swift").exists())
        self.assertFalse((ROOT / "Sources/ExampleApp/ExampleApp.swift").exists())
        self.assertFalse((ROOT / "Tests/AccessibilityProbeUITests.swift").exists())

    def test_public_docs_are_normalized(self) -> None:
        expected = {
            "docs/prior-art.md",
            "docs/runtime-boundary.md",
            "docs/publishing.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            ".editorconfig",
        }
        for path in expected:
            self.assertTrue((ROOT / path).exists(), path)
        self.assertFalse((ROOT / "docs/CLAIM_DISCIPLINE.md").exists())

    def test_readme_keeps_succinct_research_boundary(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(readme.splitlines()), 100)
        self.assertEqual("# thin-mac-ios", readme.splitlines()[0])
        self.assertIn("How far can iOS build and verification work move off Macs?", readme)
        self.assertIn("UIKit does not run on Linux here", readme)
        self.assertIn("Macs are still required", readme)
        self.assertIn("## Non-Claims", readme)

    def test_makefile_has_publish_ready_verification_target(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("verify:", makefile)
        self.assertIn("PYTHONPATH_VALUE ?= src", makefile)
        self.assertIn("PYTHONPATH=$(PYTHONPATH_VALUE)", makefile)
        self.assertIn("fixtures/ios-app", (ROOT / "scripts/linux_build.sh").read_text(encoding="utf-8"))

    def test_pyproject_metadata_uses_buildable_src_layout(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual("thin-mac-ios", pyproject["project"]["name"])
        self.assertEqual({"text": "MIT"}, pyproject["project"]["license"])
        self.assertIn("wheel", pyproject["build-system"]["requires"])
        self.assertEqual(["src"], pyproject["tool"]["setuptools"]["packages"]["find"]["where"])
        for script_name, entry_point in pyproject["project"]["scripts"].items():
            self.assertTrue(script_name.startswith("thin-mac-ios-"))
            self.assertTrue(entry_point.startswith("ios_linux_harness.cli."))


if __name__ == "__main__":
    unittest.main()
