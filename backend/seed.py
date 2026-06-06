import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from db import get_collection

logger = logging.getLogger(__name__)

ET = ZoneInfo("America/New_York")

# The 16 host cities -> (stadium, country, IANA timezone). One stadium per city.
CITY_INFO = {
    "Atlanta": ("Mercedes-Benz Stadium", "USA", "America/New_York"),
    "Boston": ("Gillette Stadium", "USA", "America/New_York"),
    "Dallas": ("AT&T Stadium", "USA", "America/Chicago"),
    "Houston": ("NRG Stadium", "USA", "America/Chicago"),
    "Kansas City": ("Arrowhead Stadium", "USA", "America/Chicago"),
    "Los Angeles": ("SoFi Stadium", "USA", "America/Los_Angeles"),
    "Miami": ("Hard Rock Stadium", "USA", "America/New_York"),
    "New York/New Jersey": ("MetLife Stadium", "USA", "America/New_York"),
    "Philadelphia": ("Lincoln Financial Field", "USA", "America/New_York"),
    "San Francisco Bay Area": ("Levi's Stadium", "USA", "America/Los_Angeles"),
    "Seattle": ("Lumen Field", "USA", "America/Los_Angeles"),
    "Toronto": ("BMO Field", "Canada", "America/Toronto"),
    "Vancouver": ("BC Place", "Canada", "America/Vancouver"),
    "Guadalajara": ("Estadio Akron", "Mexico", "America/Mexico_City"),
    "Mexico City": ("Estadio Azteca", "Mexico", "America/Mexico_City"),
    "Monterrey": ("Estadio BBVA", "Mexico", "America/Monterrey"),
}

# Real 2026 FIFA World Cup group-stage fixtures from the final draw (5 Dec 2025).
# Source kickoff times are US Eastern (ET); they are converted to each venue's
# local time at build time below. Tuple: (et_date, et_hour, group, home, away, city)
RAW_FIXTURES = [
    ("2026-06-11", 15, "A", "Mexico", "South Africa", "Mexico City"),
    ("2026-06-11", 21, "A", "South Korea", "Czechia", "Guadalajara"),
    ("2026-06-12", 15, "B", "Canada", "Bosnia and Herzegovina", "Toronto"),
    ("2026-06-12", 21, "D", "USA", "Paraguay", "Los Angeles"),
    ("2026-06-13", 0, "D", "Australia", "Turkey", "Vancouver"),
    ("2026-06-13", 15, "B", "Qatar", "Switzerland", "San Francisco Bay Area"),
    ("2026-06-13", 18, "C", "Brazil", "Morocco", "New York/New Jersey"),
    ("2026-06-13", 21, "C", "Haiti", "Scotland", "Boston"),
    ("2026-06-14", 13, "E", "Germany", "Curaçao", "Houston"),
    ("2026-06-14", 16, "F", "Netherlands", "Japan", "Dallas"),
    ("2026-06-14", 19, "E", "Ivory Coast", "Ecuador", "Philadelphia"),
    ("2026-06-14", 21, "F", "Sweden", "Tunisia", "Monterrey"),
    ("2026-06-15", 12, "H", "Spain", "Cape Verde", "Atlanta"),
    ("2026-06-15", 15, "G", "Belgium", "Egypt", "Seattle"),
    ("2026-06-15", 18, "H", "Saudi Arabia", "Uruguay", "Miami"),
    ("2026-06-15", 21, "G", "Iran", "New Zealand", "Los Angeles"),
    ("2026-06-16", 15, "I", "France", "Senegal", "New York/New Jersey"),
    ("2026-06-16", 18, "I", "Iraq", "Norway", "Boston"),
    ("2026-06-16", 21, "J", "Argentina", "Algeria", "Kansas City"),
    ("2026-06-17", 0, "J", "Austria", "Jordan", "San Francisco Bay Area"),
    ("2026-06-17", 13, "K", "Portugal", "DR Congo", "Houston"),
    ("2026-06-17", 16, "L", "England", "Croatia", "Dallas"),
    ("2026-06-17", 19, "L", "Ghana", "Panama", "Toronto"),
    ("2026-06-17", 22, "K", "Uzbekistan", "Colombia", "Mexico City"),
    ("2026-06-18", 12, "A", "Czechia", "South Africa", "Atlanta"),
    ("2026-06-18", 15, "B", "Switzerland", "Bosnia and Herzegovina", "Los Angeles"),
    ("2026-06-18", 21, "A", "Mexico", "South Korea", "Guadalajara"),
    ("2026-06-18", 21, "B", "Canada", "Qatar", "Vancouver"),
    ("2026-06-19", 15, "D", "USA", "Australia", "Seattle"),
    ("2026-06-19", 18, "C", "Scotland", "Morocco", "Boston"),
    ("2026-06-19", 21, "C", "Brazil", "Haiti", "Philadelphia"),
    ("2026-06-19", 21, "D", "Turkey", "Paraguay", "San Francisco Bay Area"),
    ("2026-06-20", 13, "F", "Netherlands", "Sweden", "Houston"),
    ("2026-06-20", 16, "E", "Germany", "Ivory Coast", "Toronto"),
    ("2026-06-20", 20, "E", "Ecuador", "Curaçao", "Kansas City"),
    ("2026-06-21", 0, "F", "Tunisia", "Japan", "Monterrey"),
    ("2026-06-21", 12, "H", "Spain", "Saudi Arabia", "Atlanta"),
    ("2026-06-21", 15, "G", "Belgium", "Iran", "Los Angeles"),
    ("2026-06-21", 18, "H", "Uruguay", "Cape Verde", "Miami"),
    ("2026-06-21", 21, "G", "New Zealand", "Egypt", "Vancouver"),
    ("2026-06-22", 13, "J", "Argentina", "Austria", "Dallas"),
    ("2026-06-22", 17, "I", "France", "Iraq", "Philadelphia"),
    ("2026-06-22", 20, "I", "Norway", "Senegal", "New York/New Jersey"),
    ("2026-06-22", 23, "J", "Jordan", "Algeria", "San Francisco Bay Area"),
    ("2026-06-23", 13, "K", "Portugal", "Uzbekistan", "Houston"),
    ("2026-06-23", 22, "K", "Colombia", "DR Congo", "Guadalajara"),
    ("2026-06-23", 16, "L", "England", "Ghana", "Boston"),
    ("2026-06-23", 19, "L", "Panama", "Croatia", "Toronto"),
    ("2026-06-24", 18, "C", "Scotland", "Brazil", "Miami"),
    ("2026-06-24", 18, "C", "Morocco", "Haiti", "Atlanta"),
    ("2026-06-24", 21, "A", "Czechia", "Mexico", "Mexico City"),
    ("2026-06-24", 21, "A", "South Africa", "South Korea", "Monterrey"),
    ("2026-06-24", 21, "B", "Switzerland", "Canada", "Vancouver"),
    ("2026-06-24", 15, "B", "Bosnia and Herzegovina", "Qatar", "Seattle"),
    ("2026-06-25", 16, "E", "Ecuador", "Germany", "New York/New Jersey"),
    ("2026-06-25", 16, "E", "Curaçao", "Ivory Coast", "Philadelphia"),
    ("2026-06-25", 19, "F", "Japan", "Sweden", "Dallas"),
    ("2026-06-25", 19, "F", "Tunisia", "Netherlands", "Kansas City"),
    ("2026-06-25", 22, "D", "Turkey", "USA", "Los Angeles"),
    ("2026-06-25", 22, "D", "Paraguay", "Australia", "San Francisco Bay Area"),
    ("2026-06-26", 20, "H", "Cape Verde", "Saudi Arabia", "Houston"),
    ("2026-06-26", 20, "H", "Uruguay", "Spain", "Guadalajara"),
    ("2026-06-26", 23, "G", "Egypt", "Iran", "Seattle"),
    ("2026-06-26", 23, "G", "New Zealand", "Belgium", "Vancouver"),
    ("2026-06-26", 15, "I", "Norway", "France", "Boston"),
    ("2026-06-26", 15, "I", "Senegal", "Iraq", "Toronto"),
    ("2026-06-27", 17, "L", "Panama", "England", "New York/New Jersey"),
    ("2026-06-27", 17, "L", "Croatia", "Ghana", "Philadelphia"),
    ("2026-06-27", 19, "K", "Colombia", "Portugal", "Miami"),
    ("2026-06-27", 19, "K", "DR Congo", "Uzbekistan", "Atlanta"),
    ("2026-06-27", 22, "J", "Algeria", "Austria", "Kansas City"),
    ("2026-06-27", 22, "J", "Jordan", "Argentina", "Dallas"),
]


def _build_matches() -> list[dict]:
    matches = []
    for i, (et_date, et_hour, group, home, away, city) in enumerate(RAW_FIXTURES, 1):
        venue, country, tz = CITY_INFO[city]
        et_dt = datetime.strptime(et_date, "%Y-%m-%d").replace(hour=et_hour, tzinfo=ET)
        local = et_dt.astimezone(ZoneInfo(tz))
        matches.append({
            "match_id": f"WC-{i:03d}",
            "home_team": home,
            "away_team": away,
            "date": local.strftime("%Y-%m-%d"),
            "time": local.strftime("%H:%M"),
            "venue": venue,
            "city": city,
            "country": country,
            "stage": "Group Stage",
            "group": group,
        })
    return matches


MATCHES = _build_matches()


def seed_matches():
    """Sync the real 2026 World Cup group-stage fixtures into MongoDB.

    Idempotent: upserts by match_id, so re-running updates existing docs in place
    rather than duplicating or requiring a destructive wipe.
    """
    matches_col = get_collection("matches")
    for m in MATCHES:
        matches_col.replace_one({"match_id": m["match_id"]}, m, upsert=True)
    logger.info("Synced %d real World Cup 2026 group-stage matches across 16 host cities", len(MATCHES))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
    seed_matches()
    logger.info("Seeding complete.")
