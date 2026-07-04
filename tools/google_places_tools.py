from __future__ import annotations

from dataclasses import dataclass
import json
from math import radians, sin, cos, sqrt, atan2
import os
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
PLACES_FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.location,"
    "places.types,"
    "places.primaryTypeDisplayName,"
    "places.googleMapsUri"
)


@dataclass
class PlaceLookupResult:
    name: str
    address: str
    category: str
    latitude: float
    longitude: float
    distance_miles: float
    google_maps_link: str = ""
    planning_note: str = ""
    verification_action: str = ""


def google_places_configured() -> bool:
    return bool(os.getenv("GOOGLE_MAPS_API_KEY", "").strip())


def search_nearby_emergency_facilities(
    latitude: float,
    longitude: float,
    radius_meters: int = 25000,
    limit: int = 8,
) -> List[PlaceLookupResult]:
    queries = ["emergency room", "hospital emergency department", "urgent care"]
    results = _search_queries(queries, latitude, longitude, radius_meters)
    return sorted(results, key=lambda item: item.distance_miles)[:limit]


def search_candidate_aed_locations(
    latitude: float,
    longitude: float,
    radius_meters: int = 10000,
    limit: int = 8,
) -> List[PlaceLookupResult]:
    queries = [
        "school",
        "gym",
        "community center",
        "library",
        "recreation center",
        "sports complex",
    ]
    results = _search_queries(queries, latitude, longitude, radius_meters)
    for result in results:
        result.planning_note = "Candidate place to contact; not a verified AED location."
        result.verification_action = _verification_action(result.category)
    return sorted(results, key=lambda item: item.distance_miles)[:limit]


def _search_queries(
    queries: Iterable[str],
    latitude: float,
    longitude: float,
    radius_meters: int,
) -> List[PlaceLookupResult]:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    if not api_key:
        return []

    deduped: Dict[str, PlaceLookupResult] = {}
    for query in queries:
        for place in _text_search(api_key, query, latitude, longitude, radius_meters):
            result = _place_to_result(place, latitude, longitude, default_category=query)
            key = _dedupe_key(place, result)
            if key not in deduped or result.distance_miles < deduped[key].distance_miles:
                deduped[key] = result

    return list(deduped.values())


def _text_search(
    api_key: str,
    query: str,
    latitude: float,
    longitude: float,
    radius_meters: int,
) -> List[Dict[str, Any]]:
    body = {
        "textQuery": query,
        "locationBias": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": float(radius_meters),
            }
        },
    }
    request = Request(
        PLACES_TEXT_SEARCH_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": PLACES_FIELD_MASK,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return []

    return payload.get("places", [])


def _place_to_result(
    place: Dict[str, Any],
    origin_latitude: float,
    origin_longitude: float,
    default_category: str,
) -> PlaceLookupResult:
    location = place.get("location", {})
    latitude = float(location.get("latitude", origin_latitude))
    longitude = float(location.get("longitude", origin_longitude))
    display_name = place.get("displayName", {})
    category_name = place.get("primaryTypeDisplayName", {})

    category = category_name.get("text") if isinstance(category_name, dict) else ""
    if not category:
        category = _category_from_types(place.get("types", [])) or default_category

    return PlaceLookupResult(
        name=display_name.get("text", "Unnamed place") if isinstance(display_name, dict) else "Unnamed place",
        address=place.get("formattedAddress", "Address unavailable"),
        category=category,
        latitude=latitude,
        longitude=longitude,
        distance_miles=round(_haversine_miles(origin_latitude, origin_longitude, latitude, longitude), 2),
        google_maps_link=place.get("googleMapsUri", ""),
        planning_note="Live place result; verify locally before relying on it for planning.",
    )


def _dedupe_key(place: Dict[str, Any], result: PlaceLookupResult) -> str:
    place_id = place.get("id")
    if place_id:
        return str(place_id)
    return f"{result.name.lower()}|{result.address.lower()}"


def _category_from_types(types: Iterable[str]) -> str:
    labels = {
        "hospital": "Hospital",
        "doctor": "Medical facility",
        "health": "Health",
        "school": "School",
        "gym": "Gym",
        "library": "Library",
        "community_center": "Community center",
        "sports_complex": "Sports complex",
    }
    for item in types:
        if item in labels:
            return labels[item]
    return ""


def _verification_action(category: str) -> str:
    lowered = category.lower()
    if "school" in lowered:
        return "Call facility or ask the main office to confirm AED presence, access, signage, maintenance, and hours."
    if "gym" in lowered or "sports" in lowered or "recreation" in lowered:
        return "Ask front desk or event staff and check signage; confirm access hours and maintenance status."
    if "library" in lowered or "community" in lowered:
        return "Call facility or ask front desk; confirm AED presence, access, signage, maintenance, and hours."
    return "Call facility, check signage, and confirm AED presence, access, maintenance status, and hours."


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_miles = 3958.8
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return radius_miles * c
