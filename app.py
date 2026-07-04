import streamlit as st
import pandas as pd

from agents.router import PulsePrepRouter
from agents.scenario_quiz_agent import ScenarioQuizAgent
from agents.aed_locator_agent import AEDLocatorAgent
from agents.emergency_facility_agent import EmergencyFacilityAwarenessFinderAgent
from agents.outreach_agent import OutreachMaterialGenerator
from agents.safety_review_agent import SafetyReviewAgent
from config import GOOGLE_PLACES_CONFIG_NOTE, LOCATION_SAFETY_NOTE, STANDARD_SAFETY_NOTE

st.set_page_config(
    page_title="PulsePrep Agent",
    page_icon="❤️",
    layout="wide",
)

router = PulsePrepRouter()
quiz_agent = ScenarioQuizAgent()
aed_agent = AEDLocatorAgent()
facility_agent = EmergencyFacilityAwarenessFinderAgent()
outreach_agent = OutreachMaterialGenerator()
safety_agent = SafetyReviewAgent()

st.title("PulsePrep Agent")
st.caption("CPR/AED readiness education for communities")

st.warning(
    "If this is a real emergency, call 911 or your local emergency number now. "
    "This prototype is for education and preparedness only."
)

with st.sidebar:
    st.header("Mode")
    mode = st.radio(
        "Choose a demo mode",
        [
            "Ask PulsePrep: Emergency + AED Coach",
            "Scenario Practice Quiz",
            "AED Locator / Awareness Demo",
            "Emergency Facility Finder Demo",
            "Outreach Generator",
            "About",
        ],
    )
    audience = st.selectbox(
        "Audience",
        [
            "elementary student",
            "middle school student",
            "high school student",
            "parent",
            "teacher",
            "coach",
            "workplace team",
            "community volunteer",
        ],
        index=1,
    )
    st.caption(GOOGLE_PLACES_CONFIG_NOTE)


def show_map(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No map results available.")
        return
    map_df = df.rename(columns={"latitude": "lat", "longitude": "lon"})
    st.map(map_df[["lat", "lon"]])
    st.dataframe(df, use_container_width=True)


if mode == "Ask PulsePrep: Emergency + AED Coach":
    st.subheader("Ask PulsePrep")
    st.write("Use this mode for Demo 1 Emergency Safety Classifier and Demo 2 AED Learning Coach.")
    st.write("Try: `Teach a 7th grader what an AED does` or `Someone collapsed and is not breathing. What should I do?`")
    message = st.text_area("Your message", height=120)
    known_locations = st.text_input("Known AED locations, if relevant", "main office and gym")
    use_demo_location = st.checkbox("Include demo location for map-related requests", value=False)
    lat = lon = None
    if use_demo_location:
        col1, col2 = st.columns(2)
        lat = col1.number_input("Latitude", value=41.5600, format="%.6f")
        lon = col2.number_input("Longitude", value=-90.4800, format="%.6f")

    if st.button("Run Agent", type="primary"):
        if not message.strip():
            st.error("Please enter a message.")
        else:
            response = router.handle(
                message,
                audience=audience,
                latitude=lat,
                longitude=lon,
                known_aed_locations=known_locations,
            )
            st.markdown(response.text)
            st.caption(f"Routed mode: {response.mode}")

elif mode == "Scenario Practice Quiz":
    st.subheader("Scenario-Based CPR/AED Practice Quiz")
    setting = st.selectbox("Scenario setting", ["basketball", "school hallway", "community event"])
    question = quiz_agent.create_question(setting)
    st.markdown(question)
    answer = st.text_area("Your answer", height=100)
    if st.button("Evaluate My Answer", type="primary"):
        feedback = quiz_agent.evaluate_answer(answer, setting)
        reviewed = safety_agent.review(feedback)
        st.markdown(reviewed.text)

elif mode == "AED Locator / Awareness Demo":
    st.subheader("AED Locator / Awareness Demo")
    st.info("These are candidate AED-awareness planning locations, not verified AED locations.")
    st.caption(f"Using: {aed_agent.lookup_source_label()}")
    col1, col2, col3 = st.columns(3)
    lat = col1.number_input("Latitude", value=41.5600, format="%.6f")
    lon = col2.number_input("Longitude", value=-90.4800, format="%.6f")
    limit = col3.slider("Number of results", 1, 10, 5)
    if st.button("Find Demo AEDs", type="primary"):
        df = aed_agent.find_nearby_dataframe(lat, lon, limit)
        st.markdown(aed_agent.find_nearby_markdown(lat, lon, limit))
        show_map(df)

    st.divider()
    st.subheader("Create AED Awareness Checklist")
    known_locations = st.text_input("Known AED locations", "main office, gym entrance, cafeteria")
    if st.button("Generate Awareness Checklist"):
        text = aed_agent.create_awareness_checklist(known_locations)
        reviewed = safety_agent.review(text, include_location_warning=True)
        st.markdown(reviewed.text)

elif mode == "Emergency Facility Finder Demo":
    st.subheader("Emergency Facility Awareness Finder Demo")
    st.info("Emergency facility results are for preparedness planning only.")
    st.caption(f"Using: {facility_agent.lookup_source_label()}")
    col1, col2, col3 = st.columns(3)
    lat = col1.number_input("Latitude", value=41.5600, format="%.6f")
    lon = col2.number_input("Longitude", value=-90.4800, format="%.6f")
    limit = col3.slider("Number of results", 1, 10, 5)
    if st.button("Find Demo Emergency Facilities", type="primary"):
        df = facility_agent.find_nearby_dataframe(lat, lon, limit)
        st.markdown(facility_agent.find_nearby_markdown(lat, lon, limit))
        st.markdown(LOCATION_SAFETY_NOTE)
        show_map(df)

elif mode == "Outreach Generator":
    st.subheader("Community Outreach Material Generator")
    material_type = st.selectbox("Material type", ["morning announcement", "poster", "newsletter blurb", "event checklist"])
    locations = st.text_input("AED locations to include", "main office and gym entrance")
    event_name = st.text_input("Event name", "community sports event")
    if st.button("Generate Material", type="primary"):
        text = outreach_agent.create_material(material_type, audience, locations, event_name)
        reviewed = safety_agent.review(text, include_location_warning=True)
        st.markdown(reviewed.text)

elif mode == "About":
    st.subheader("About PulsePrep")
    st.markdown(
        """
PulsePrep Agent is a capstone prototype for CPR/AED readiness education. It demonstrates:

- A multi-agent architecture.
- Emergency intent classification.
- Scenario-based learning.
- Location-aware preparedness planning with optional live lookup or fallback planning data.
- Community outreach generation.
- Safety review before final output.

The project is designed for the **Agents for Good** track.
        """
    )
    st.markdown(STANDARD_SAFETY_NOTE)
