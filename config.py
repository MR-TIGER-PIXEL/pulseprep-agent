from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

AED_SAMPLE_CSV = DATA_DIR / "aed_locations_sample.csv"
FACILITY_SAMPLE_CSV = DATA_DIR / "emergency_facilities_sample.csv"
DEMO_DEFAULT_LATITUDE = 41.5600
DEMO_DEFAULT_LONGITUDE = -90.4800
GOOGLE_PLACES_CONFIG_NOTE = "Optional: set GOOGLE_MAPS_API_KEY to enable live Google Places lookup."
GOOGLE_PLACES_FALLBACK_NOTE = "Google Places lookup is not configured, so PulsePrep is showing fallback planning data."

EMERGENCY_RESPONSE = """\
**Possible emergency detected. Call emergency services now.**

1. Call 911 or your local emergency number immediately.
2. Send someone to get the nearest AED.
3. Follow the emergency dispatcher’s instructions.
4. If you are trained and it is safe, begin CPR.
5. When the AED arrives, turn it on and follow the voice prompts.

This app is educational and cannot replace emergency services or professional responders.
"""

STANDARD_SAFETY_NOTE = """\
**Safety note:** PulsePrep is for education and preparedness. It does not replace emergency services, certified CPR/AED training, or professional medical guidance.
"""

LOCATION_SAFETY_NOTE = """\
**Location safety note:** Location results are for preparedness planning only. They do not replace 911, emergency dispatch, ambulance routing, medical triage, EMS, clinicians, CPR/AED certification, or local emergency instructions. AED locations, access, signage, maintenance status, hours, and emergency facility availability can change. Verify locally. In a real emergency, call 911 or local emergency services first and follow dispatcher instructions.
"""

AED_CANDIDATE_SAFETY_NOTE = """\
**AED awareness note:** These are candidate AED-awareness planning locations, not verified AED locations. Confirm AED presence, access, signage, maintenance status, and hours with the facility. In a real emergency, call 911 or local emergency services and follow dispatcher instructions.
"""

LIVE_FACILITY_SAFETY_NOTE = """\
**Facility planning note:** This uses live place lookup for preparedness planning only. It is not a substitute for 911, emergency dispatch, ambulance routing, medical triage, EMS, clinicians, CPR/AED certification, or local emergency instructions. In a real emergency, call 911 or local emergency services and follow dispatcher instructions.
"""

FALLBACK_FACILITY_SAFETY_NOTE = """\
**Facility planning note:** These fallback planning results are for preparedness planning only. They are not a substitute for 911, emergency dispatch, ambulance routing, medical triage, EMS, clinicians, CPR/AED certification, or local emergency instructions. In a real emergency, call 911 or local emergency services and follow dispatcher instructions.
"""
