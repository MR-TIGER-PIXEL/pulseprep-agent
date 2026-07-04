from dataclasses import dataclass, field
from typing import List


@dataclass
class EmergencyClassification:
    is_possible_emergency: bool
    risk_level: str
    score: int
    reasons: List[str] = field(default_factory=list)


class EmergencySafetyClassifier:
    """Rule-based first-pass emergency detector.

    In a production system, this could be combined with an LLM or clinical review,
    but this deterministic layer is intentionally simple, auditable, and fast.
    """

    HIGH_RISK_PHRASES = [
        "not breathing",
        "no breathing",
        "isn't breathing",
        "is not breathing",
        "unconscious",
        "collapsed",
        "collapse",
        "cardiac arrest",
        "no pulse",
        "needs cpr",
        "need cpr",
        "aed now",
        "need an aed",
        "needs an aed",
        "turning blue",
        "can't wake",
        "cannot wake",
        "not responding",
        "unresponsive",
    ]

    EMERGENCY_CONTEXT = [
        "right now",
        "now",
        "help",
        "urgent",
        "emergency",
        "basketball practice",
        "game",
        "gym",
        "school",
        "field",
        "pool",
    ]

    EDUCATIONAL_CONTEXT = [
        "teach",
        "explain",
        "lesson",
        "quiz",
        "practice question",
        "scenario",
        "for a class",
        "for school",
        "poster",
        "announcement",
        "writeup",
        "demo",
        "capstone",
        "planning",
        "plan",
        "create",
        "identify",
        "awareness",
        "locator",
        "locations",
    ]

    def classify(self, message: str) -> EmergencyClassification:
        text = (message or "").lower().strip()
        score = 0
        reasons: List[str] = []
        high_risk_detected = False

        for phrase in self.HIGH_RISK_PHRASES:
            if phrase in text:
                score += 3
                high_risk_detected = True
                reasons.append(f"High-risk phrase detected: '{phrase}'")

        for phrase in self.EMERGENCY_CONTEXT:
            if phrase in text:
                score += 1
                reasons.append(f"Emergency context detected: '{phrase}'")

        for phrase in self.EDUCATIONAL_CONTEXT:
            if phrase in text:
                score -= 2
                reasons.append(f"Educational/planning context detected: '{phrase}'")

        # If a high-risk phrase appears with direct first-person immediacy, bias safer.
        if high_risk_detected and any(token in text for token in ["what do i do", "what should i do", "help me"]):
            score += 2
            reasons.append("Direct immediate-help phrasing detected")

        if high_risk_detected and score >= 4:
            return EmergencyClassification(True, "high", score, reasons)
        if high_risk_detected and score >= 2:
            return EmergencyClassification(True, "medium", score, reasons)
        return EmergencyClassification(False, "low", score, reasons)
