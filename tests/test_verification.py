import tempfile
import unittest
from pathlib import Path

from ios_linux_harness.verification import extract_accessibility_tree, write_accessibility_tree


class VerificationTests(unittest.TestCase):
    def test_extract_accessibility_tree_reads_marked_xctest_output(self) -> None:
        log = """noise before
ACCESSIBILITY_TREE_BEGIN
Application, pid: 123
  StaticText, identifier: 'ProbeBinaryFrameworkValue', label: 'ProbeBinaryKit: 4096'
ACCESSIBILITY_TREE_END
noise after
"""

        tree = extract_accessibility_tree(log)

        self.assertIn("ProbeBinaryFrameworkValue", tree)
        self.assertIn("ProbeBinaryKit: 4096", tree)
        self.assertNotIn("noise before", tree)

    def test_write_accessibility_tree_requires_real_probe_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "xcodebuild.log"
            output = root / "accessibility-tree.txt"
            log.write_text(
                "ACCESSIBILITY_TREE_BEGIN\n"
                "StaticText, identifier: 'ProbeBinaryFrameworkValue', label: 'ProbeBinaryKit: 4096'\n"
                "ACCESSIBILITY_TREE_END\n",
                encoding="utf-8",
            )

            extracted = write_accessibility_tree(log, output)

            self.assertTrue(extracted)
            self.assertEqual(
                "StaticText, identifier: 'ProbeBinaryFrameworkValue', label: 'ProbeBinaryKit: 4096'\n",
                output.read_text(encoding="utf-8"),
            )

    def test_write_accessibility_tree_rejects_marker_only_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "xcodebuild.log"
            output = root / "accessibility-tree.txt"
            log.write_text(
                "ACCESSIBILITY_TREE_BEGIN\nApplication, pid: 123\nACCESSIBILITY_TREE_END\n",
                encoding="utf-8",
            )

            extracted = write_accessibility_tree(log, output)

            self.assertFalse(extracted)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
