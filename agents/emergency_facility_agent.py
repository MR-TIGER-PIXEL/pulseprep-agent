import pandas as pd

from config import (
    FACILITY_SAMPLE_CSV,
    FALLBACK_FACILITY_SAFETY_NOTE,
    GOOGLE_PLACES_FALLBACK_NOTE,
    LIVE_FACILITY_SAFETY_NOTE,
)
from tools.google_places_tools import google_places_configured, search_nearby_emergency_facilities
from tools.location_tools import find_nearest, results_to_dataframe


class EmergencyFacilityAwarenessFinderAgent:
    """Finds nearby emergency facilities for preparedness planning."""

    def lookup_source_label(self) -> str:
        return "Live Google Places lookup" if google_places_configured() else "Fallback planning data"

    def find_nearby(self, latitude: float, longitude: float, limit: int = 5):
        return find_nearest(FACILITY_SAMPLE_CSV, latitude, longitude, limit)

    def find_nearby_markdown(self, latitude: float, longitude: float, limit: int = 5) -> str:
        live_configured = google_places_configured()
        if live_configured:
            results = search_nearby_emergency_facilities(latitude, longitude, limit=limit)
            if results:
                return self._live_results_to_markdown(results)

        results = self.find_nearby(latitude, longitude, limit)
        source_note = GOOGLE_PLACES_FALLBACK_NOTE
        if live_configured:
            source_note = "Live Google Places lookup did not return results, so PulsePrep is showing fallback planning data."
        return self._fallback_results_to_markdown(results, source_note)

    def find_nearby_dataframe(self, latitude: float, longitude: float, limit: int = 5):
        if google_places_configured():
            results = search_nearby_emergency_facilities(latitude, longitude, limit=limit)
            if results:
                return self._live_results_to_dataframe(results)

        return results_to_dataframe(self.find_nearby(latitude, longitude, limit))

    @staticmethod
    def _live_results_to_markdown(results) -> str:
        lines = [
            "## Nearby Emergency Facility Planning Results",
            "",
            "Source: **Live Google Places lookup**",
            "",
            "| Name | Address or vicinity | Category/type | Distance from search point | Google Maps link | Planning note |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for result in results:
            maps_link = f"[Open map]({result.google_maps_link})" if result.google_maps_link else "Unavailable"
            lines.append(
                "| "
                f"{result.name} | "
                f"{result.address} | "
                f"{result.category} | "
                f"{result.distance_miles} miles | "
                f"{maps_link} | "
                "Verify services and event planning assumptions locally; call 911 in a real emergency. |"
            )
        lines.extend(["", LIVE_FACILITY_SAFETY_NOTE.strip()])
        return "\n".join(lines)

    @staticmethod
    def _live_results_to_dataframe(results):
        return pd.DataFrame(
            [
                {
                    "name": result.name,
                    "address": result.address,
                    "category": result.category,
                    "distance_miles": result.distance_miles,
                    "google_maps_link": result.google_maps_link,
                    "planning_note": "Verify services locally; not for dispatch, routing, or triage.",
                    "latitude": result.latitude,
                    "longitude": result.longitude,
                }
                for result in results
            ]
        )

    @staticmethod
    def _fallback_results_to_markdown(results, source_note: str) -> str:
        if not results:
            return f"## Nearby Emergency Facility Awareness Fallback Results\n\n{source_note}\n\nNo fallback planning data found.\n\n{FALLBACK_FACILITY_SAFETY_NOTE}".strip()

        lines = [
            "## Nearby Emergency Facility Awareness Fallback Results",
            "",
            f"{source_note} These records are for preparedness planning only.",
            "",
            "| Name | Address or vicinity | Category/type | Distance from search point | Google Maps link | Planning note |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for result in results:
            lines.append(
                "| "
                f"{result.name} | "
                f"{result.address} | "
                f"{result.category} | "
                f"{result.distance_miles} miles | "
                "Unavailable in fallback mode | "
                f"{result.notes or 'Verify locally; not for dispatch, routing, or triage.'} |"
            )
        lines.extend(["", FALLBACK_FACILITY_SAFETY_NOTE.strip()])
        return "\n".join(lines)
