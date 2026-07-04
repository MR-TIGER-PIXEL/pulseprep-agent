from dataclasses import dataclass, field
from typing import List
from tools.safety_tools import find_unsafe_phrases, revise_unsafe_text, ensure_safety_language


@dataclass
class SafetyReviewResult:
    text: str
    changed: bool
    issues: List[str] = field(default_factory=list)


class SafetyReviewAgent:
    """Reviews generated content before returning it to the user."""

    def review(self, text: str, include_location_warning: bool = False) -> SafetyReviewResult:
        issues = find_unsafe_phrases(text)
        revised = revise_unsafe_text(text) if issues else text
        with_safety = ensure_safety_language(revised, include_location_warning=include_location_warning)
        changed = bool(issues) or (with_safety != text)
        return SafetyReviewResult(text=with_safety, changed=changed, issues=issues)
