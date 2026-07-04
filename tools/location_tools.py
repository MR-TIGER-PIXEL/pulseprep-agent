from __future__ import annotations

from dataclasses import dataclass
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path
from typing import List
import pandas as pd


@dataclass
class LocationResult:
    name: str
    category: str
    address: str
    latitude: float
    longitude: float
    distance_miles: float
    notes: str = ""


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_miles = 3958.8
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return radius_miles * c


def load_locations(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def find_nearest(csv_path: Path, latitude: float, longitude: float, limit: int = 5) -> List[LocationResult]:
    df = load_locations(csv_path)
    results: List[LocationResult] = []

    for _, row in df.iterrows():
        distance = haversine_miles(latitude, longitude, float(row["latitude"]), float(row["longitude"]))
        results.append(
            LocationResult(
                name=str(row["name"]),
                category=str(row.get("category", "location")),
                address=str(row["address"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                distance_miles=round(distance, 2),
                notes=str(row.get("notes", "")),
            )
        )

    return sorted(results, key=lambda item: item.distance_miles)[:limit]


def results_to_markdown(results: List[LocationResult], title: str, source_note: str = "These are fallback planning results:") -> str:
    if not results:
        return f"## {title}\n\nNo results found in the fallback planning data."

    lines = [f"## {title}", "", source_note, ""]
    for idx, result in enumerate(results, start=1):
        lines.extend(
            [
                f"### {idx}. {result.name}",
                f"- Category: {result.category}",
                f"- Address: {result.address}",
                f"- Approximate distance: {result.distance_miles} miles",
                f"- Notes: {result.notes or 'Verify locally.'}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def results_to_dataframe(results: List[LocationResult]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "name": r.name,
                "category": r.category,
                "address": r.address,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "distance_miles": r.distance_miles,
                "notes": r.notes,
            }
            for r in results
        ]
    )
