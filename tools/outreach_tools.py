def normalize_audience(audience: str) -> str:
    return (audience or "community members").strip()


def clean_locations(locations: str) -> str:
    return (locations or "the main office, gym entrance, or other posted AED locations").strip()
