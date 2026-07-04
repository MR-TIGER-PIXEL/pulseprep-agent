from agents.emergency_classifier import EmergencySafetyClassifier
from agents.aed_locator_agent import AEDLocatorAgent
from agents.emergency_facility_agent import EmergencyFacilityAwarenessFinderAgent
from agents.router import PulsePrepRouter
from agents.safety_review_agent import SafetyReviewAgent


def test_emergency_classifier_detects_collapse():
    classifier = EmergencySafetyClassifier()
    result = classifier.classify("Someone collapsed and is not breathing. What should I do?")
    assert result.is_possible_emergency is True


def test_educational_question_not_high_risk():
    classifier = EmergencySafetyClassifier()
    result = classifier.classify("Teach a 7th grader what an AED does for a class demo.")
    assert result.is_possible_emergency is False


def test_safety_review_adds_emergency_language():
    reviewer = SafetyReviewAgent()
    result = reviewer.review("AEDs provide voice prompts.")
    assert "call 911" in result.text.lower() or "emergency services" in result.text.lower()


def test_planning_poster_prompt_is_not_classified_as_emergency():
    classifier = EmergencySafetyClassifier()
    result = classifier.classify("Help me create an AED awareness poster for AEDs near the gym and main office.")
    assert result.is_possible_emergency is False


def test_emergency_facility_planning_prompt_is_not_classified_as_emergency():
    classifier = EmergencySafetyClassifier()
    result = classifier.classify("Help identify nearby emergency departments for planning a community sports event.")
    assert result.is_possible_emergency is False


def test_poster_prompt_routes_to_outreach_with_location_warning():
    router = PulsePrepRouter()
    response = router.handle(
        "Help me create an AED awareness poster for AEDs near the gym and main office.",
        known_aed_locations="gym and main office",
    )
    assert response.mode == "outreach"
    assert "gym and main office" in response.text.lower()
    assert "location" in response.text.lower()
    assert "signage" in response.text.lower()


def test_facility_planning_prompt_uses_fallback_results_without_coordinates(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    router = PulsePrepRouter()
    response = router.handle("Help identify nearby emergency departments for planning a community sports event.")
    assert response.mode == "facility_finder"
    assert "Nearby Emergency Facility Awareness Fallback Results" in response.text
    assert "Google Places lookup is not configured, so PulsePrep is showing fallback planning data." in response.text
    assert "preparedness planning only" in response.text.lower()
    assert "911" in response.text.lower()
    assert "emergency dispatch" in response.text.lower()
    assert "ambulance routing" in response.text.lower()
    assert "medical triage" in response.text.lower()


def test_emergency_response_uses_basketball_practice_context():
    router = PulsePrepRouter()
    response = router.handle("Someone collapsed at basketball practice and is not breathing. What should I do?")
    text = response.text.lower()
    assert response.mode == "emergency"
    assert response.possible_emergency is True
    assert "basketball practice" in text
    assert "coach" in text or "bystander" in text
    assert "call 911 or the local emergency number immediately" in text
    assert "nearest aed" in text
    assert "dispatcher" in text
    assert "cpr" in text
    assert "not breathing normally" in text
    assert "voice prompts" in text
    assert "does not replace emergency services" in text
    assert "dispatchers" in text
    assert "cpr/aed certification" in text
    assert "professional responders" in text


def test_emergency_responses_are_context_aware_not_identical():
    router = PulsePrepRouter()
    basketball = router.handle("Someone collapsed at basketball practice and is not breathing. What should I do?")
    gym = router.handle("A person is unconscious in the gym and not breathing. Help!")
    assert basketball.text != gym.text
    assert "basketball practice" in basketball.text.lower()
    assert "gym" in gym.text.lower()


def test_aed_locator_fallback_without_google_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    agent = AEDLocatorAgent()
    text = agent.find_nearby_markdown(41.56, -90.48)
    assert "Google Places lookup is not configured, so PulsePrep is showing fallback planning data." in text
    assert "candidate AED-awareness planning locations" in text or "candidate planning records" in text
    assert "not verified AED locations" in text
    assert "Confirm AED presence, access, signage, maintenance status, and hours with the facility." in text


def test_aed_locator_dataframe_fallback_without_google_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    agent = AEDLocatorAgent()
    df = agent.find_nearby_dataframe(41.56, -90.48)
    assert not df.empty
    assert "verification_action" in df.columns


def test_emergency_facility_fallback_without_google_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    agent = EmergencyFacilityAwarenessFinderAgent()
    text = agent.find_nearby_markdown(41.56, -90.48)
    assert "Google Places lookup is not configured, so PulsePrep is showing fallback planning data." in text
    assert "preparedness planning only" in text.lower()
    assert "not a substitute for 911" in text.lower()
    assert "emergency dispatch" in text.lower()
    assert "ambulance routing" in text.lower()
    assert "medical triage" in text.lower()
