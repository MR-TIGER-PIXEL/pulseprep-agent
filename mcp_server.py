"""MCP-style tool server for PulsePrep.

If the optional `mcp` package is installed, this file exposes PulsePrep tools
with FastMCP. If not installed, it falls back to a simple JSON-lines server.

Fallback request format:
{"tool":"classify_emergency_intent","args":{"message":"Someone collapsed"}}
"""

import json
import sys
from typing import Any, Dict

from agents.emergency_classifier import EmergencySafetyClassifier
from agents.cpr_aed_coach import CPRAEDLearningCoach
from agents.scenario_quiz_agent import ScenarioQuizAgent
from agents.aed_locator_agent import AEDLocatorAgent
from agents.emergency_facility_agent import EmergencyFacilityAwarenessFinderAgent
from agents.outreach_agent import OutreachMaterialGenerator
from agents.safety_review_agent import SafetyReviewAgent

classifier = EmergencySafetyClassifier()
coach = CPRAEDLearningCoach()
quiz = ScenarioQuizAgent()
aed = AEDLocatorAgent()
facility = EmergencyFacilityAwarenessFinderAgent()
outreach = OutreachMaterialGenerator()
safety = SafetyReviewAgent()


def classify_emergency_intent(message: str) -> Dict[str, Any]:
    result = classifier.classify(message)
    return {
        "is_possible_emergency": result.is_possible_emergency,
        "risk_level": result.risk_level,
        "score": result.score,
        "reasons": result.reasons,
    }


def generate_cpr_lesson(topic: str, audience: str = "middle school student") -> str:
    return coach.create_lesson(topic, audience)


def create_practice_scenario(setting: str = "basketball") -> str:
    return quiz.create_question(setting)


def score_quiz_response(answer: str, setting: str = "basketball") -> str:
    return quiz.evaluate_answer(answer, setting)


def find_nearby_aeds(latitude: float, longitude: float, limit: int = 5) -> str:
    return aed.find_nearby_markdown(latitude, longitude, limit)


def find_nearest_emergency_facilities(latitude: float, longitude: float, limit: int = 5) -> str:
    return facility.find_nearby_markdown(latitude, longitude, limit)


def create_outreach_material(material_type: str, audience: str, locations: str, event_name: str = "community event") -> str:
    return outreach.create_material(material_type, audience, locations, event_name)


def review_cpr_aed_safety(text: str, include_location_warning: bool = False) -> Dict[str, Any]:
    result = safety.review(text, include_location_warning=include_location_warning)
    return {"text": result.text, "changed": result.changed, "issues": result.issues}


TOOLS = {
    "classify_emergency_intent": classify_emergency_intent,
    "generate_cpr_lesson": generate_cpr_lesson,
    "create_practice_scenario": create_practice_scenario,
    "score_quiz_response": score_quiz_response,
    "find_nearby_aeds": find_nearby_aeds,
    "find_nearest_emergency_facilities": find_nearest_emergency_facilities,
    "create_outreach_material": create_outreach_material,
    "review_cpr_aed_safety": review_cpr_aed_safety,
}


def run_json_lines_server() -> None:
    for line in sys.stdin:
        try:
            request = json.loads(line)
            tool_name = request.get("tool")
            args = request.get("args", {})
            if tool_name not in TOOLS:
                response = {"ok": False, "error": f"Unknown tool: {tool_name}"}
            else:
                response = {"ok": True, "result": TOOLS[tool_name](**args)}
        except Exception as exc:  # noqa: BLE001 - CLI fallback should report any error cleanly.
            response = {"ok": False, "error": str(exc)}
        print(json.dumps(response), flush=True)


def run_fastmcp_server() -> bool:
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore
    except Exception:
        return False

    mcp = FastMCP("PulsePrep Agent Tools")

    for name, func in TOOLS.items():
        mcp.tool(name=name)(func)

    mcp.run()
    return True


if __name__ == "__main__":
    if not run_fastmcp_server():
        run_json_lines_server()
