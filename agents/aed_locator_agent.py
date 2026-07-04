import pandas as pd

from config import AED_CANDIDATE_SAFETY_NOTE, AED_SAMPLE_CSV, GOOGLE_PLACES_FALLBACK_NOTE
from tools.google_places_tools import google_places_configured, search_candidate_aed_locations
from tools.location_tools import find_nearest, results_to_dataframe


class AEDLocatorAgent:
    """Finds candidate AED-awareness locations and creates awareness materials."""

    def lookup_source_label(self) -> str:
        return "Live Google Places lookup" if google_places_configured() else "Fallback planning data"

    def find_nearby(self, latitude: float, longitude: float, limit: int = 5):
        return find_nearest(AED_SAMPLE_CSV, latitude, longitude, limit)

    def find_nearby_markdown(self, latitude: float, longitude: float, limit: int = 5) -> str:
        live_configured = google_places_configured()
        if google_places_configured():
            results = search_candidate_aed_locations(latitude, longitude, limit=limit)
            if results:
                return self._candidate_results_to_markdown(results, live=True)

        results = self.find_nearby(latitude, longitude, limit)
        source_note = GOOGLE_PLACES_FALLBACK_NOTE
        if live_configured:
            source_note = "Live Google Places lookup did not return results, so PulsePrep is showing fallback planning data."
        return self._fallback_results_to_markdown(results, source_note)

    def find_nearby_dataframe(self, latitude: float, longitude: float, limit: int = 5):
        if google_places_configured():
            results = search_candidate_aed_locations(latitude, longitude, limit=limit)
            if results:
                return self._candidate_results_to_dataframe(results)

        df = results_to_dataframe(self.find_nearby(latitude, longitude, limit))
        if df.empty:
            return df
        df["verification_action"] = "Confirm AED presence, access, signage, maintenance status, and hours with the facility."
        return df

    def create_awareness_checklist(self, known_locations: str = "main office, gym entrance, cafeteria") -> str:
        return f"""
## AED Awareness Checklist

Known AED locations to verify:

{self._format_locations(known_locations)}

### Readiness steps

- Confirm each AED location with school or facility leaders.
- Make sure signs are visible from nearby hallways or event areas.
- Ask staff, coaches, and event volunteers whether they know the nearest AED location.
- Assign roles during events: one person calls emergency services, one person gets the AED, and one person guides responders.
- Include AED reminders in event briefings, coach meetings, and school announcements.
- Encourage official CPR/AED training for staff, coaches, students, and community volunteers.
""".strip()

    @staticmethod
    def _format_locations(known_locations: str) -> str:
        items = [item.strip() for item in known_locations.replace(";", ",").split(",") if item.strip()]
        return "\n".join([f"- {item}" for item in items]) if items else "- Add known AED locations here."

    @staticmethod
    def _candidate_results_to_markdown(results, live: bool) -> str:
        source = "Live Google Places lookup" if live else "Fallback planning data"
        lines = [
            "## Candidate AED-Awareness Planning Locations",
            "",
            f"Source: **{source}**",
            "",
            "| Candidate place name | Address or vicinity | Category/type | Distance from search point | Verification action |",
            "| --- | --- | --- | --- | --- |",
        ]
        for result in results:
            lines.append(
                "| "
                f"{result.name} | "
                f"{result.address} | "
                f"{result.category} | "
                f"{result.distance_miles} miles | "
                f"{result.verification_action or 'Call facility, check signage, and confirm access hours.'} |"
            )
        lines.extend(["", AED_CANDIDATE_SAFETY_NOTE.strip()])
        return "\n".join(lines)

    @staticmethod
    def _candidate_results_to_dataframe(results):
        return pd.DataFrame(
            [
                {
                    "name": result.name,
                    "address": result.address,
                    "category": result.category,
                    "distance_miles": result.distance_miles,
                    "verification_action": result.verification_action,
                    "latitude": result.latitude,
                    "longitude": result.longitude,
                }
                for result in results
            ]
        )

    @staticmethod
    def _fallback_results_to_markdown(results, source_note: str) -> str:
        if not results:
            return f"## Nearby AED Awareness Fallback Results\n\n{source_note}\n\nNo fallback planning data found.\n\n{AED_CANDIDATE_SAFETY_NOTE}".strip()

        lines = [
            "## Nearby AED Awareness Fallback Results",
            "",
            f"{source_note} These are candidate planning records to verify locally.",
            "",
            "| Candidate place name | Address or vicinity | Category/type | Distance from search point | Verification action |",
            "| --- | --- | --- | --- | --- |",
        ]
        for result in results:
            lines.append(
                "| "
                f"{result.name} | "
                f"{result.address} | "
                f"{result.category} | "
                f"{result.distance_miles} miles | "
                "Confirm AED presence, access, signage, maintenance status, and hours with the facility. |"
            )
        lines.extend(["", AED_CANDIDATE_SAFETY_NOTE.strip()])
        return "\n".join(lines)
