import logging
from db import get_collection

logger = logging.getLogger(__name__)

HOST_CITIES = [
    ("Atlanta", "Mercedes-Benz Stadium", "USA"),
    ("Boston", "Gillette Stadium", "USA"),
    ("Dallas", "AT&T Stadium", "USA"),
    ("Houston", "NRG Stadium", "USA"),
    ("Kansas City", "Arrowhead Stadium", "USA"),
    ("Los Angeles", "SoFi Stadium", "USA"),
    ("Miami", "Hard Rock Stadium", "USA"),
    ("New York/New Jersey", "MetLife Stadium", "USA"),
    ("Philadelphia", "Lincoln Financial Field", "USA"),
    ("San Francisco Bay Area", "Levi's Stadium", "USA"),
    ("Seattle", "Lumen Field", "USA"),
    ("Toronto", "BMO Field", "Canada"),
    ("Vancouver", "BC Place", "Canada"),
    ("Guadalajara", "Estadio Akron", "Mexico"),
    ("Mexico City", "Estadio Azteca", "Mexico"),
    ("Monterrey", "Estadio BBVA", "Mexico"),
]

MATCHES = [
    {"match_id": "WC-001", "home_team": "Brazil", "away_team": "Croatia", "date": "2026-06-11", "time": "16:00", "venue": "Mercedes-Benz Stadium", "city": "Atlanta", "country": "USA", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-002", "home_team": "Argentina", "away_team": "Japan", "date": "2026-06-12", "time": "14:00", "venue": "Gillette Stadium", "city": "Boston", "country": "USA", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-003", "home_team": "France", "away_team": "Senegal", "date": "2026-06-12", "time": "18:00", "venue": "AT&T Stadium", "city": "Dallas", "country": "USA", "stage": "Group Stage", "group": "C"},
    {"match_id": "WC-004", "home_team": "England", "away_team": "Iran", "date": "2026-06-13", "time": "15:00", "venue": "NRG Stadium", "city": "Houston", "country": "USA", "stage": "Group Stage", "group": "D"},
    {"match_id": "WC-005", "home_team": "Germany", "away_team": "Australia", "date": "2026-06-13", "time": "20:00", "venue": "Arrowhead Stadium", "city": "Kansas City", "country": "USA", "stage": "Group Stage", "group": "E"},
    {"match_id": "WC-006", "home_team": "Spain", "away_team": "Morocco", "date": "2026-06-14", "time": "13:00", "venue": "SoFi Stadium", "city": "Los Angeles", "country": "USA", "stage": "Group Stage", "group": "F"},
    {"match_id": "WC-007", "home_team": "Netherlands", "away_team": "Ecuador", "date": "2026-06-14", "time": "17:00", "venue": "Hard Rock Stadium", "city": "Miami", "country": "USA", "stage": "Group Stage", "group": "G"},
    {"match_id": "WC-008", "home_team": "Portugal", "away_team": "Ghana", "date": "2026-06-15", "time": "16:00", "venue": "MetLife Stadium", "city": "New York/New Jersey", "country": "USA", "stage": "Group Stage", "group": "H"},
    {"match_id": "WC-009", "home_team": "Belgium", "away_team": "Canada", "date": "2026-06-15", "time": "19:00", "venue": "Lincoln Financial Field", "city": "Philadelphia", "country": "USA", "stage": "Group Stage", "group": "I"},
    {"match_id": "WC-010", "home_team": "Italy", "away_team": "South Korea", "date": "2026-06-16", "time": "14:00", "venue": "Levi's Stadium", "city": "San Francisco Bay Area", "country": "USA", "stage": "Group Stage", "group": "J"},
    {"match_id": "WC-011", "home_team": "Switzerland", "away_team": "Cameroon", "date": "2026-06-16", "time": "18:00", "venue": "Lumen Field", "city": "Seattle", "country": "USA", "stage": "Group Stage", "group": "K"},
    {"match_id": "WC-012", "home_team": "Uruguay", "away_team": "New Zealand", "date": "2026-06-17", "time": "15:00", "venue": "BMO Field", "city": "Toronto", "country": "Canada", "stage": "Group Stage", "group": "L"},
    {"match_id": "WC-013", "home_team": "USA", "away_team": "Nigeria", "date": "2026-06-12", "time": "20:00", "venue": "SoFi Stadium", "city": "Los Angeles", "country": "USA", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-014", "home_team": "Mexico", "away_team": "Egypt", "date": "2026-06-13", "time": "17:00", "venue": "Estadio Azteca", "city": "Mexico City", "country": "Mexico", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-015", "home_team": "Colombia", "away_team": "Saudi Arabia", "date": "2026-06-14", "time": "19:00", "venue": "BC Place", "city": "Vancouver", "country": "Canada", "stage": "Group Stage", "group": "C"},
    {"match_id": "WC-016", "home_team": "Denmark", "away_team": "Tunisia", "date": "2026-06-15", "time": "14:00", "venue": "Estadio Akron", "city": "Guadalajara", "country": "Mexico", "stage": "Group Stage", "group": "D"},
    {"match_id": "WC-017", "home_team": "Croatia", "away_team": "Nigeria", "date": "2026-06-17", "time": "20:00", "venue": "Mercedes-Benz Stadium", "city": "Atlanta", "country": "USA", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-018", "home_team": "Japan", "away_team": "Egypt", "date": "2026-06-18", "time": "14:00", "venue": "Estadio Azteca", "city": "Mexico City", "country": "Mexico", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-019", "home_team": "Brazil", "away_team": "USA", "date": "2026-06-19", "time": "21:00", "venue": "MetLife Stadium", "city": "New York/New Jersey", "country": "USA", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-020", "home_team": "Argentina", "away_team": "Mexico", "date": "2026-06-20", "time": "16:00", "venue": "NRG Stadium", "city": "Houston", "country": "USA", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-021", "home_team": "France", "away_team": "Colombia", "date": "2026-06-21", "time": "15:00", "venue": "AT&T Stadium", "city": "Dallas", "country": "USA", "stage": "Group Stage", "group": "C"},
    {"match_id": "WC-022", "home_team": "England", "away_team": "Denmark", "date": "2026-06-22", "time": "18:00", "venue": "Gillette Stadium", "city": "Boston", "country": "USA", "stage": "Group Stage", "group": "D"},
    {"match_id": "WC-023", "home_team": "Germany", "away_team": "Switzerland", "date": "2026-06-23", "time": "20:00", "venue": "Arrowhead Stadium", "city": "Kansas City", "country": "USA", "stage": "Group Stage", "group": "E"},
    {"match_id": "WC-024", "home_team": "Spain", "away_team": "Portugal", "date": "2026-06-24", "time": "17:00", "venue": "Levi's Stadium", "city": "San Francisco Bay Area", "country": "USA", "stage": "Group Stage", "group": "F"},
    {"match_id": "WC-025", "home_team": "Netherlands", "away_team": "Belgium", "date": "2026-06-25", "time": "19:00", "venue": "Hard Rock Stadium", "city": "Miami", "country": "USA", "stage": "Group Stage", "group": "G"},
    {"match_id": "WC-026", "home_team": "Italy", "away_team": "Uruguay", "date": "2026-06-26", "time": "14:00", "venue": "Lincoln Financial Field", "city": "Philadelphia", "country": "USA", "stage": "Group Stage", "group": "J"},
    {"match_id": "WC-027", "home_team": "Canada", "away_team": "Morocco", "date": "2026-06-18", "time": "16:00", "venue": "BMO Field", "city": "Toronto", "country": "Canada", "stage": "Group Stage", "group": "I"},
    {"match_id": "WC-028", "home_team": "Senegal", "away_team": "Colombia", "date": "2026-06-19", "time": "14:00", "venue": "BC Place", "city": "Vancouver", "country": "Canada", "stage": "Group Stage", "group": "C"},
    {"match_id": "WC-029", "home_team": "South Korea", "away_team": "New Zealand", "date": "2026-06-20", "time": "18:00", "venue": "Estadio BBVA", "city": "Monterrey", "country": "Mexico", "stage": "Group Stage", "group": "J"},
    {"match_id": "WC-030", "home_team": "Morocco", "away_team": "Canada", "date": "2026-06-21", "time": "20:00", "venue": "Estadio Akron", "city": "Guadalajara", "country": "Mexico", "stage": "Group Stage", "group": "F"},
    {"match_id": "WC-031", "home_team": "Ecuador", "away_team": "Belgium", "date": "2026-06-22", "time": "15:00", "venue": "Lumen Field", "city": "Seattle", "country": "USA", "stage": "Group Stage", "group": "G"},
    {"match_id": "WC-032", "home_team": "Australia", "away_team": "Switzerland", "date": "2026-06-23", "time": "17:00", "venue": "Estadio BBVA", "city": "Monterrey", "country": "Mexico", "stage": "Group Stage", "group": "E"},
    {"match_id": "WC-033", "home_team": "Ghana", "away_team": "Cameroon", "date": "2026-06-24", "time": "19:00", "venue": "Estadio Akron", "city": "Guadalajara", "country": "Mexico", "stage": "Group Stage", "group": "H"},
    {"match_id": "WC-034", "home_team": "Iran", "away_team": "Tunisia", "date": "2026-06-25", "time": "14:00", "venue": "Estadio BBVA", "city": "Monterrey", "country": "Mexico", "stage": "Group Stage", "group": "D"},
    {"match_id": "WC-035", "home_team": "Saudi Arabia", "away_team": "Senegal", "date": "2026-06-26", "time": "18:00", "venue": "BC Place", "city": "Vancouver", "country": "Canada", "stage": "Group Stage", "group": "C"},
    {"match_id": "WC-036", "home_team": "Nigeria", "away_team": "Croatia", "date": "2026-06-27", "time": "16:00", "venue": "Mercedes-Benz Stadium", "city": "Atlanta", "country": "USA", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-037", "home_team": "Egypt", "away_team": "Japan", "date": "2026-06-27", "time": "20:00", "venue": "Estadio Azteca", "city": "Mexico City", "country": "Mexico", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-038", "home_team": "Cameroon", "away_team": "Australia", "date": "2026-06-28", "time": "15:00", "venue": "Lumen Field", "city": "Seattle", "country": "USA", "stage": "Group Stage", "group": "K"},
    {"match_id": "WC-039", "home_team": "New Zealand", "away_team": "South Korea", "date": "2026-06-28", "time": "19:00", "venue": "BMO Field", "city": "Toronto", "country": "Canada", "stage": "Group Stage", "group": "L"},
    {"match_id": "WC-040", "home_team": "Tunisia", "away_team": "England", "date": "2026-06-29", "time": "14:00", "venue": "NRG Stadium", "city": "Houston", "country": "USA", "stage": "Group Stage", "group": "D"},
    {"match_id": "WC-041", "home_team": "Ecuador", "away_team": "Netherlands", "date": "2026-06-29", "time": "18:00", "venue": "Hard Rock Stadium", "city": "Miami", "country": "USA", "stage": "Group Stage", "group": "G"},
    {"match_id": "WC-042", "home_team": "Portugal", "away_team": "Germany", "date": "2026-06-30", "time": "17:00", "venue": "Arrowhead Stadium", "city": "Kansas City", "country": "USA", "stage": "Group Stage", "group": "H"},
    {"match_id": "WC-043", "home_team": "Belgium", "away_team": "Ecuador", "date": "2026-06-30", "time": "21:00", "venue": "SoFi Stadium", "city": "Los Angeles", "country": "USA", "stage": "Group Stage", "group": "G"},
    {"match_id": "WC-044", "home_team": "Italy", "away_team": "New Zealand", "date": "2026-07-01", "time": "15:00", "venue": "Lincoln Financial Field", "city": "Philadelphia", "country": "USA", "stage": "Group Stage", "group": "J"},
    {"match_id": "WC-045", "home_team": "Uruguay", "away_team": "South Korea", "date": "2026-07-01", "time": "20:00", "venue": "Levi's Stadium", "city": "San Francisco Bay Area", "country": "USA", "stage": "Group Stage", "group": "L"},
    {"match_id": "WC-046", "home_team": "Mexico", "away_team": "Argentina", "date": "2026-07-02", "time": "16:00", "venue": "Estadio Azteca", "city": "Mexico City", "country": "Mexico", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-047", "home_team": "USA", "away_team": "Brazil", "date": "2026-07-02", "time": "21:00", "venue": "AT&T Stadium", "city": "Dallas", "country": "USA", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-048", "home_team": "Canada", "away_team": "France", "date": "2026-07-03", "time": "19:00", "venue": "BMO Field", "city": "Toronto", "country": "Canada", "stage": "Group Stage", "group": "I"},
]


def seed_matches():
    matches_col = get_collection("matches")
    existing = matches_col.count_documents({})
    if existing > 0:
        logger.info("Database already contains %d matches — skipping seed", existing)
        return

    matches_col.insert_many(MATCHES)
    for city_name, venue, country in HOST_CITIES:
        matches_col.update_many(
            {"city": city_name},
            {"$set": {"venue": venue, "country": country}},
        )
    logger.info("Seeded %d World Cup 2026 matches across %d host cities", len(MATCHES), len(HOST_CITIES))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
    seed_matches()
    logger.info("Seeding complete.")
