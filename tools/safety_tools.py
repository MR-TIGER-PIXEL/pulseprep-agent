from typing import List

UNSAFE_PHRASES = [
    "do not call 911",
    "don't call 911",
    "wait before calling 911",
    "wait to call 911",
    "drive them to the hospital instead of calling 911",
    "the aed will always shock",
    "you are certified after this lesson",
]

REQUIRED_EDUCATIONAL_LIMITATION = (
    "PulsePrep is for education and preparedness and does not replace emergency services, "
    "certified CPR/AED training, or professional medical guidance."
)

REQUIRED_LOCATION_LIMITATION = (
    "Location results are for preparedness planning only. They do not replace 911, emergency dispatch, "
    "ambulance routing, medical triage, EMS, clinicians, CPR/AED certification, or local emergency "
    "instructions. AED locations, access, signage, maintenance status, hours, and emergency facility "
    "availability can change. Verify locally. In a real emergency, call 911 or local emergency services "
    "first and follow dispatcher instructions."
)


def find_unsafe_phrases(text: str) -> List[str]:
    lowered = (text or "").lower()
    return [phrase for phrase in UNSAFE_PHRASES if phrase in lowered]


def ensure_safety_language(text: str, include_location_warning: bool = False) -> str:
    """Adds safety language if it is missing."""
    output = text.strip()
    lower = output.lower()

    if "call 911" not in lower and "emergency services" not in lower:
        output += (
            "\n\n**Emergency reminder:** In a real emergency, call 911 or your local "
            "emergency number immediately and follow dispatcher instructions."
        )

    if "does not replace" not in lower and "certified cpr" not in lower:
        output += f"\n\n**Education note:** {REQUIRED_EDUCATIONAL_LIMITATION}"

    if include_location_warning and "preparedness planning only" not in lower:
        output += f"\n\n**Location note:** {REQUIRED_LOCATION_LIMITATION}"

    return output


def revise_unsafe_text(text: str) -> str:
    output = text
    output = output.replace("do not call 911", "call 911")
    output = output.replace("don't call 911", "call 911")
    output = output.replace("wait before calling 911", "call 911 immediately")
    output = output.replace("wait to call 911", "call 911 immediately")
    output = output.replace(
        "drive them to the hospital instead of calling 911",
        "call 911 or local emergency services and follow dispatcher instructions",
    )
    output = output.replace("the AED will always shock", "the AED analyzes the rhythm and only advises a shock when appropriate")
    output = output.replace("you are certified after this lesson", "this lesson does not provide certification")
    return output
