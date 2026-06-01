from __future__ import annotations

from pathlib import Path


ACCESSIBILITY_BEGIN = "ACCESSIBILITY_TREE_BEGIN"
ACCESSIBILITY_END = "ACCESSIBILITY_TREE_END"
REQUIRED_ACCESSIBILITY_TERMS = ("ProbeBinaryFrameworkValue", "ProbeBinaryKit: 4096")


def extract_accessibility_tree(log_text: str) -> str:
    start = log_text.find(ACCESSIBILITY_BEGIN)
    if start == -1:
        return ""
    start += len(ACCESSIBILITY_BEGIN)
    end = log_text.find(ACCESSIBILITY_END, start)
    if end == -1:
        return ""
    tree = log_text[start:end].strip("\n")
    return f"{tree}\n" if tree else ""


def write_accessibility_tree(
    log_path: Path,
    output_path: Path,
    required_terms: tuple[str, ...] = REQUIRED_ACCESSIBILITY_TERMS,
) -> bool:
    tree = extract_accessibility_tree(log_path.read_text(encoding="utf-8", errors="ignore"))
    if not tree or any(term not in tree for term in required_terms):
        if output_path.exists():
            output_path.unlink()
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(tree, encoding="utf-8")
    return True
