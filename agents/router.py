from dataclasses import dataclass
from typing import Optional

from config import DEMO_DEFAULT_LATITUDE, DEMO_DEFAULT_LONGITUDE
from agents.emergency_classifier import EmergencySafetyClassifier
from agents.cpr_aed_coach import CPRAEDLearningCoach
from agents.scenario_quiz_agent import ScenarioQuizAgent
from agents.aed_locator_agent import AEDLocatorAgent
from agents.emergency_facility_agent import EmergencyFacilityAwarenessFinderAgent
from agents.outreach_agent import OutreachMaterialGenerator
from agents.safety_review_agent import SafetyReviewAgent


@dataclass
class AgentResponse:
    mode: str
    text: str
    possible_emergency: bool = False
    include_location_warning: bool = False


class PulsePrepRouter:
    """Routes user requests to the right specialized agent."""

    def __init__(self) -> None:
        self.classifier = EmergencySafetyClassifier()
        self.coach = CPRAEDLearningCoach()
        self.quiz = ScenarioQuizAgent()
        self.aed_locator = AEDLocatorAgent()
        self.facility_finder = EmergencyFacilityAwarenessFinderAgent()
        self.outreach = OutreachMaterialGenerator()
        self.safety = SafetyReviewAgent()

    def handle(
        self,
        message: str,
        audience: str = "middle school student",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        known_aed_locations: str = "main office and gym",
    ) -> AgentResponse:
        classification = self.classifier.classify(message)
        if classification.is_possible_emergency:
            return AgentResponse(mode="emergency", text=self._build_emergency_response(message), possible_emergency=True)

        intent = self._detect_intent(message)
        text: str
        include_location_warning = False

        if intent == "quiz":
            text = self.quiz.create_question(setting=message)
            mode = "scenario_quiz"
        elif intent == "aed_locator":
            if latitude is not None and longitude is not None:
                text = self.aed_locator.find_nearby_markdown(latitude, longitude)
            else:
                text = self.aed_locator.create_awareness_checklist(known_aed_locations)
            include_location_warning = True
            mode = "aed_locator"
        elif intent == "facility_finder":
            lat_to_use = latitude if latitude is not None else DEMO_DEFAULT_LATITUDE
            lon_to_use = longitude if longitude is not None else DEMO_DEFAULT_LONGITUDE
            text = self.facility_finder.find_nearby_markdown(lat_to_use, lon_to_use)
            include_location_warning = True
            mode = "facility_finder"
        elif intent == "outreach":
            text = self.outreach.create_material(
                material_type=message,
                audience=audience,
                locations=known_aed_locations,
                event_name="community event",
            )
            include_location_warning = True
            mode = "outreach"
        else:
            text = self.coach.create_lesson(topic=message, audience=audience)
            mode = "learning_coach"

        reviewed = self.safety.review(text, include_location_warning=include_location_warning)
        return AgentResponse(mode=mode, text=reviewed.text, possible_emergency=False, include_location_warning=include_location_warning)

    @staticmethod
    def _detect_intent(message: str) -> str:
        text = (message or "").lower()
        if any(word in text for word in ["quiz", "practice", "scenario", "question"]):
            return "quiz"
        if any(word in text for word in ["nearest hospital", "hospital", "emergency department", "emergency facility"]):
            return "facility_finder"
        # Treat ER as a standalone term only, not as letters inside words like 'grader'.
        tokens = set(text.replace("/", " " ).replace(".", " " ).replace(",", " " ).split())
        if "er" in tokens:
            return "facility_finder"
        if any(word in text for word in ["aed locator", "find aed", "nearest aed", "aed map", "aed location"]):
            return "aed_locator"
        if any(word in text for word in ["poster", "announcement", "newsletter", "blurb", "script", "outreach", "checklist"]):
            return "outreach"
        return "lesson"

    @staticmethod
    def _build_emergency_response(message: str) -> str:
        text = (message or "").lower()
        context_parts = []

        if "basketball" in text:
            context_parts.append("at basketball practice")
        elif "gym" in text:
            context_parts.append("in the gym")
        elif "school" in text:
            context_parts.append("at school")

        if "student" in text or "player" in text:
            person = "student/player"
        elif "person" in text or "someone" in text:
            person = "person"
        else:
            person = "individual"

        context = f" {context_parts[0]}" if context_parts else ""
        not_breathing = "not breathing" in text or "not breathing normally" in text or "no breathing" in text
        collapsed = "collapsed" in text or "collapse" in text

        first_action = "Tell a coach, adult, or bystander to call 911 or the local emergency number immediately."
        if "coach" in text:
            first_action = "Have the coach call 911 or the local emergency number immediately, or do it yourself if no one else can."
        elif "school" in text or "student" in text:
            first_action = "Tell a teacher, coach, school staff member, or bystander to call 911 or the local emergency number immediately."

        situation = f"**Possible emergency detected{context}. Act now.**"
        if collapsed and not_breathing:
            situation += f"\n\nIf the {person}{context} collapsed and is not breathing normally, treat this as a possible cardiac emergency."
        elif collapsed:
            situation += f"\n\nIf the {person}{context} collapsed or is not responding, get emergency help right away."
        elif not_breathing:
            situation += f"\n\nIf the {person}{context} is not breathing normally, get emergency help right away."

        return f"""
{situation}

1. {first_action}
2. Send someone else to get the nearest AED and bring it back fast.
3. Stay with the {person} and follow the emergency dispatcher's instructions.
4. If the {person} is not breathing normally, begin CPR if you are trained and it is safe to do so.
5. When the AED arrives, turn it on and follow its voice prompts. It will check the heart rhythm and tell you whether a shock is advised.

PulsePrep is educational and does not replace emergency services, emergency dispatchers, CPR/AED certification, or professional responders.
""".strip()
