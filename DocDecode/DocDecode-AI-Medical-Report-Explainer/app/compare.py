"""
Report comparison utilities.

Provides side-by-side diff, textual similarity metrics, and
AI-powered change analysis between two medical reports.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DiffBlock:
    """Represents a single diff hunk between two reports."""
    tag: str            # "equal", "replace", "insert", "delete"
    old_lines: List[str] = field(default_factory=list)
    new_lines: List[str] = field(default_factory=list)


@dataclass
class ComparisonResult:
    """Container for all comparison metrics and diffs."""
    similarity_ratio: float
    added_lines: List[str]
    removed_lines: List[str]
    changed_sections: List[DiffBlock]
    summary_stats: Dict[str, int]


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Lower-case, collapse whitespace, strip."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def compute_similarity(text_a: str, text_b: str) -> float:
    """
    Return a 0-1 similarity ratio using SequenceMatcher.
    """
    return difflib.SequenceMatcher(
        None,
        _normalise(text_a),
        _normalise(text_b),
    ).ratio()


def compute_diff(text_a: str, text_b: str) -> ComparisonResult:
    """
    Compute a structured diff between two report texts.

    Parameters
    ----------
    text_a : str  – the *older* report
    text_b : str  – the *newer* report

    Returns
    -------
    ComparisonResult
    """
    lines_a = text_a.splitlines(keepends=False)
    lines_b = text_b.splitlines(keepends=False)

    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    similarity = matcher.ratio()

    added: List[str] = []
    removed: List[str] = []
    blocks: List[DiffBlock] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        old = lines_a[i1:i2]
        new = lines_b[j1:j2]

        blocks.append(DiffBlock(tag=tag, old_lines=old, new_lines=new))

        if tag == "insert":
            added.extend(new)
        elif tag == "delete":
            removed.extend(old)
        elif tag == "replace":
            removed.extend(old)
            added.extend(new)

    stats = {
        "total_lines_old": len(lines_a),
        "total_lines_new": len(lines_b),
        "lines_added": len(added),
        "lines_removed": len(removed),
        "lines_unchanged": sum(
            len(b.old_lines) for b in blocks if b.tag == "equal"
        ),
    }

    return ComparisonResult(
        similarity_ratio=similarity,
        added_lines=added,
        removed_lines=removed,
        changed_sections=blocks,
        summary_stats=stats,
    )


def generate_unified_diff(text_a: str, text_b: str,
                          label_a: str = "Previous Report",
                          label_b: str = "Current Report") -> str:
    """Return a unified-diff string suitable for displaying in a code block."""
    diff = difflib.unified_diff(
        text_a.splitlines(keepends=True),
        text_b.splitlines(keepends=True),
        fromfile=label_a,
        tofile=label_b,
        lineterm="",
    )
    return "\n".join(diff)


def build_comparison_prompt(text_a: str, text_b: str) -> str:
    """
    Build an LLM prompt that requests an AI-driven summary of the
    differences between two radiology reports.
    """
    return f"""
You are a radiology report comparison assistant.

Compare the following two radiology reports and provide:
1. **Key Changes**: significant differences between the two reports
2. **New Findings**: findings present in the new report but absent from the old
3. **Resolved Findings**: findings that were in the old report but are no longer mentioned
4. **Progression/Improvement**: whether findings have worsened, improved, or stayed stable
5. **Summary**: a concise 2–3 sentence overall summary of the changes

PREVIOUS REPORT:
{text_a}

CURRENT REPORT:
{text_b}

Important: I am not a doctor and this is not medical advice.
This explanation is for informational purposes only.
""".strip()
