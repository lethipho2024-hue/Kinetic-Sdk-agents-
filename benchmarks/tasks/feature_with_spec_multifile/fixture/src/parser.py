from datetime import date

def parse_iso(value: str) -> date:
    return date.fromisoformat(value)
