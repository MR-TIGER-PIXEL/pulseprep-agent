from dataclasses import dataclass
from typing import List


@dataclass
class QuizScenario:
    setting: str
    scenario: str
    question: str
    expected_steps: List[str]


SCENARIOS = [
    QuizScenario(
        setting="basketball",
        scenario="You are at a school basketball game. A player suddenly collapses and does not respond when people call their name.",
        question="What should you do first, and what should others do?",
        expected_steps=["call emergency services", "send someone for the AED", "start CPR if trained", "follow AED prompts"],
    ),
    QuizScenario(
        setting="school hallway",
        scenario="A student falls in the hallway and is not responding. A teacher is nearby, and an AED is located near the main office.",
        question="What is a safe response plan?",
        expected_steps=["alert an adult", "call emergency services", "get the AED", "follow dispatcher instructions"],
    ),
    QuizScenario(
        setting="community event",
        scenario="During a community event, an adult suddenly collapses near the registration table and appears not to be breathing normally.",
        question="What should bystanders do right away?",
        expected_steps=["call emergency services", "get the AED", "begin CPR if trained", "follow AED prompts"],
    ),
]


def get_scenario(setting: str = "basketball") -> QuizScenario:
    setting_lower = (setting or "").lower()
    for scenario in SCENARIOS:
        if scenario.setting in setting_lower or setting_lower in scenario.setting:
            return scenario
    return SCENARIOS[0]


def score_response(answer: str, expected_steps: List[str]) -> dict:
    answer_lower = (answer or "").lower()
    hits = []

    checks = {
        "call emergency services": ["911", "emergency", "ambulance", "call for help", "call"],
        "send someone for the AED": ["aed", "defibrillator"],
        "start CPR if trained": ["cpr", "compressions", "chest compressions"],
        "follow AED prompts": ["prompts", "voice", "instructions", "turn it on"],
        "alert an adult": ["adult", "teacher", "coach", "nurse", "staff"],
        "follow dispatcher instructions": ["dispatcher", "operator", "instructions"],
        "get the AED": ["aed", "defibrillator"],
        "begin CPR if trained": ["cpr", "compressions", "chest compressions"],
    }

    for step in expected_steps:
        keywords = checks.get(step, [step])
        if any(keyword in answer_lower for keyword in keywords):
            hits.append(step)

    missing = [step for step in expected_steps if step not in hits]
    return {
        "score": len(hits),
        "possible": len(expected_steps),
        "matched_steps": hits,
        "missing_steps": missing,
    }
