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

# Real FIFA World Cup 2026 group stage fixtures (72 matches across 12 groups of 4)
MATCHES = [
    # Group A — Mexico, South Korea, Czech Republic, South Africa
    {"match_id": "WC-001", "home_team": "Mexico", "away_team": "South Africa", "date": "2026-06-11", "time": "13:00", "venue": "Estadio Azteca", "city": "Mexico City", "country": "Mexico", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-002", "home_team": "Korea Republic", "away_team": "Czechia", "date": "2026-06-12", "time": "10:00", "venue": "Estadio Akron", "city": "Guadalajara", "country": "Mexico", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-003", "home_team": "Czechia", "away_team": "South Africa", "date": "2026-06-18", "time": "17:00", "venue": "Mercedes-Benz Stadium", "city": "Atlanta", "country": "USA", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-004", "home_team": "Mexico", "away_team": "Korea Republic", "date": "2026-06-19", "time": "09:00", "venue": "Estadio Akron", "city": "Guadalajara", "country": "Mexico", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-005", "home_team": "South Africa", "away_team": "Korea Republic", "date": "2026-06-25", "time": "09:00", "venue": "Estadio BBVA", "city": "Monterrey", "country": "Mexico", "stage": "Group Stage", "group": "A"},
    {"match_id": "WC-006", "home_team": "Czechia", "away_team": "Mexico", "date": "2026-06-25", "time": "09:00", "venue": "Estadio Azteca", "city": "Mexico City", "country": "Mexico", "stage": "Group Stage", "group": "A"},
    # Group B — Canada, Qatar, Switzerland, Bosnia & Herzegovina
    {"match_id": "WC-007", "home_team": "Canada", "away_team": "Bosnia and Herzegovina", "date": "2026-06-12", "time": "20:00", "venue": "BMO Field", "city": "Toronto", "country": "Canada", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-008", "home_team": "Qatar", "away_team": "Switzerland", "date": "2026-06-13", "time": "20:00", "venue": "Levi's Stadium", "city": "San Francisco Bay Area", "country": "USA", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-009", "home_team": "Switzerland", "away_team": "Bosnia and Herzegovina", "date": "2026-06-18", "time": "20:00", "venue": "SoFi Stadium", "city": "Los Angeles", "country": "USA", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-010", "home_team": "Canada", "away_team": "Qatar", "date": "2026-06-18", "time": "23:00", "venue": "BC Place", "city": "Vancouver", "country": "Canada", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-011", "home_team": "Switzerland", "away_team": "Canada", "date": "2026-06-24", "time": "20:00", "venue": "BC Place", "city": "Vancouver", "country": "Canada", "stage": "Group Stage", "group": "B"},
    {"match_id": "WC-012", "home_team": "Bosnia and Herzegovina", "away_team": "Qatar", "date": "2026-06-24", "time": "20:00", "venue": "Lumen Field", "city": "Seattle", "country": "USA", "stage": "Group Stage", "group": "B"},
    # Group C — Brazil, Morocco, Haiti, Scotland
    {"match_id": "WC-013", "home_team": "Brazil", "away_team": "Morocco", "date": "2026-06-13", "time": "23:00", "venue": "MetLife Stadium", "city": "New York/New Jersey", "country": "USA", "stage": "Group Stage", "group": "C"},
    {"match_id": "WC-014", "home_team": "Haiti", "away_team": "Scotland", "date": "2026-06-14", "time": "02:00", "venue": "Gillette Stadium", "city": "Boston", "country": "USA", "stage": "Group Stage", "group": "C"},
    {"match_id": "WC-015", "home_team": "Scotland", "away_team": "Morocco", "date": "2026-06-19", "time": "23:00", "venue": "Gillette Stadium", "city": "Boston", "country": "USA", "stage": "Group Stage", "group": "C"},
    {"match_id": "WC-016", "home_team": "Brazil", "away_team": "Haiti", "date": "2026-06-20", "time": "01:30", "venue": "Lincoln Financial Field", "city": "Philadelphia", "country": "USA", "stage": "Group Stage", "group": "C"},
    {"match_id": "WC-017", "home_team": "Morocco", "away_team": "Haiti", "date": "2026-06-24", "time": "23:00", "venue": "Mercedes-Benz Stadium", "city": "Atlanta", "country": "USA", "stage": "Group Stage", "group": "C"},
    {"match_id": "WC-018", "home_team": "Scotland", "away_team": "Brazil", "date": "2026-06-24", "time": "23:00", "venue": "Hard Rock Stadium", "city": "Miami", "country": "USA", "stage": "Group Stage", "group": "C"},
    # Group D — USA, Australia, Türkiye, Paraguay
    {"match_id": "WC-019", "home_team": "USA", "away_team": "Paraguay", "date": "2026-06-13", "time": "02:00", "venue": "SoFi Stadium", "city": "Los Angeles", "country": "USA", "stage": "Group Stage", "group": "D"},
    {"match_id": "WC-020", "home_team": "Australia", "away_team": "Türkiye", "date": "2026-06-14", "time": "05:00", "venue": "BC Place", "city": "Vancouver", "country": "Canada", "stage": "Group Stage", "group": "D"},
    {"match_id": "WC-021", "home_team": "Türkiye", "away_team": "Paraguay", "date": "2026-06-20", "time": "04:00", "venue": "Levi's Stadium", "city": "San Francisco Bay Area", "country": "USA", "stage": "Group Stage", "group": "D"},
    {"match_id": "WC-022", "home_team": "USA", "away_team": "Australia", "date": "2026-06-19", "time": "20:00", "venue": "Lumen Field", "city": "Seattle", "country": "USA", "stage": "Group Stage", "group": "D"},
    {"match_id": "WC-023", "home_team": "Türkiye", "away_team": "USA", "date": "2026-06-26", "time": "03:00", "venue": "SoFi Stadium", "city": "Los Angeles", "country": "USA", "stage": "Group Stage", "group": "D"},
    {"match_id": "WC-024", "home_team": "Paraguay", "away_team": "Australia", "date": "2026-06-26", "time": "03:00", "venue": "Levi's Stadium", "city": "San Francisco Bay Area", "country": "USA", "stage": "Group Stage", "group": "D"},
    # Group E — Germany, Ecuador, Curaçao, Côte d'Ivoire
    {"match_id": "WC-025", "home_team": "Germany", "away_team": "Curaçao", "date": "2026-06-14", "time": "18:00", "venue": "NRG Stadium", "city": "Houston", "country": "USA", "stage": "Group Stage", "group": "E"},
    {"match_id": "WC-026", "home_team": "Côte d'Ivoire", "away_team": "Ecuador", "date": "2026-06-15", "time": "00:00", "venue": "Lincoln Financial Field", "city": "Philadelphia", "country": "USA", "stage": "Group Stage", "group": "E"},
    {"match_id": "WC-027", "home_team": "Ecuador", "away_team": "Curaçao", "date": "2026-06-21", "time": "01:00", "venue": "Arrowhead Stadium", "city": "Kansas City", "country": "USA", "stage": "Group Stage", "group": "E"},
    {"match_id": "WC-028", "home_team": "Germany", "away_team": "Côte d'Ivoire", "date": "2026-06-20", "time": "21:00", "venue": "BMO Field", "city": "Toronto", "country": "Canada", "stage": "Group Stage", "group": "E"},
    {"match_id": "WC-029", "home_team": "Curaçao", "away_team": "Côte d'Ivoire", "date": "2026-06-25", "time": "21:00", "venue": "Lincoln Financial Field", "city": "Philadelphia", "country": "USA", "stage": "Group Stage", "group": "E"},
    {"match_id": "WC-030", "home_team": "Ecuador", "away_team": "Germany", "date": "2026-06-25", "time": "21:00", "venue": "MetLife Stadium", "city": "New York/New Jersey", "country": "USA", "stage": "Group Stage", "group": "E"},
    # Group F — Netherlands, Japan, Sweden, Tunisia
    {"match_id": "WC-031", "home_team": "Netherlands", "away_team": "Japan", "date": "2026-06-14", "time": "21:00", "venue": "AT&T Stadium", "city": "Dallas", "country": "USA", "stage": "Group Stage", "group": "F"},
    {"match_id": "WC-032", "home_team": "Sweden", "away_team": "Tunisia", "date": "2026-06-15", "time": "03:00", "venue": "Estadio BBVA", "city": "Monterrey", "country": "Mexico", "stage": "Group Stage", "group": "F"},
    {"match_id": "WC-033", "home_team": "Netherlands", "away_team": "Sweden", "date": "2026-06-20", "time": "18:00", "venue": "NRG Stadium", "city": "Houston", "country": "USA", "stage": "Group Stage", "group": "F"},
    {"match_id": "WC-034", "home_team": "Tunisia", "away_team": "Japan", "date": "2026-06-21", "time": "05:00", "venue": "Estadio BBVA", "city": "Monterrey", "country": "Mexico", "stage": "Group Stage", "group": "F"},
    {"match_id": "WC-035", "home_team": "Tunisia", "away_team": "Netherlands", "date": "2026-06-26", "time": "00:00", "venue": "Arrowhead Stadium", "city": "Kansas City", "country": "USA", "stage": "Group Stage", "group": "F"},
    {"match_id": "WC-036", "home_team": "Japan", "away_team": "Sweden", "date": "2026-06-26", "time": "00:00", "venue": "AT&T Stadium", "city": "Dallas", "country": "USA", "stage": "Group Stage", "group": "F"},
    # Group G — Belgium, IR Iran, New Zealand, Egypt
    {"match_id": "WC-037", "home_team": "Belgium", "away_team": "Egypt", "date": "2026-06-15", "time": "20:00", "venue": "Lumen Field", "city": "Seattle", "country": "USA", "stage": "Group Stage", "group": "G"},
    {"match_id": "WC-038", "home_team": "IR Iran", "away_team": "New Zealand", "date": "2026-06-16", "time": "02:00", "venue": "SoFi Stadium", "city": "Los Angeles", "country": "USA", "stage": "Group Stage", "group": "G"},
    {"match_id": "WC-039", "home_team": "Belgium", "away_team": "IR Iran", "date": "2026-06-21", "time": "20:00", "venue": "SoFi Stadium", "city": "Los Angeles", "country": "USA", "stage": "Group Stage", "group": "G"},
    {"match_id": "WC-040", "home_team": "New Zealand", "away_team": "Egypt", "date": "2026-06-22", "time": "02:00", "venue": "BC Place", "city": "Vancouver", "country": "Canada", "stage": "Group Stage", "group": "G"},
    {"match_id": "WC-041", "home_team": "New Zealand", "away_team": "Belgium", "date": "2026-06-27", "time": "04:00", "venue": "BC Place", "city": "Vancouver", "country": "Canada", "stage": "Group Stage", "group": "G"},
    {"match_id": "WC-042", "home_team": "Egypt", "away_team": "IR Iran", "date": "2026-06-27", "time": "04:00", "venue": "Lumen Field", "city": "Seattle", "country": "USA", "stage": "Group Stage", "group": "G"},
    # Group H — Spain, Saudi Arabia, Uruguay, Cabo Verde
    {"match_id": "WC-043", "home_team": "Spain", "away_team": "Cabo Verde", "date": "2026-06-15", "time": "17:00", "venue": "Mercedes-Benz Stadium", "city": "Atlanta", "country": "USA", "stage": "Group Stage", "group": "H"},
    {"match_id": "WC-044", "home_team": "Saudi Arabia", "away_team": "Uruguay", "date": "2026-06-15", "time": "23:00", "venue": "Hard Rock Stadium", "city": "Miami", "country": "USA", "stage": "Group Stage", "group": "H"},
    {"match_id": "WC-045", "home_team": "Spain", "away_team": "Saudi Arabia", "date": "2026-06-21", "time": "17:00", "venue": "Mercedes-Benz Stadium", "city": "Atlanta", "country": "USA", "stage": "Group Stage", "group": "H"},
    {"match_id": "WC-046", "home_team": "Uruguay", "away_team": "Cabo Verde", "date": "2026-06-21", "time": "23:00", "venue": "Hard Rock Stadium", "city": "Miami", "country": "USA", "stage": "Group Stage", "group": "H"},
    {"match_id": "WC-047", "home_team": "Cabo Verde", "away_team": "Saudi Arabia", "date": "2026-06-27", "time": "01:00", "venue": "NRG Stadium", "city": "Houston", "country": "USA", "stage": "Group Stage", "group": "H"},
    {"match_id": "WC-048", "home_team": "Uruguay", "away_team": "Spain", "date": "2026-06-27", "time": "01:00", "venue": "Estadio Akron", "city": "Guadalajara", "country": "Mexico", "stage": "Group Stage", "group": "H"},
    # Group I — France, Senegal, Iraq, Norway
    {"match_id": "WC-049", "home_team": "France", "away_team": "Senegal", "date": "2026-06-16", "time": "20:00", "venue": "MetLife Stadium", "city": "New York/New Jersey", "country": "USA", "stage": "Group Stage", "group": "I"},
    {"match_id": "WC-050", "home_team": "Iraq", "away_team": "Norway", "date": "2026-06-16", "time": "23:00", "venue": "Gillette Stadium", "city": "Boston", "country": "USA", "stage": "Group Stage", "group": "I"},
    {"match_id": "WC-051", "home_team": "France", "away_team": "Iraq", "date": "2026-06-22", "time": "22:00", "venue": "Lincoln Financial Field", "city": "Philadelphia", "country": "USA", "stage": "Group Stage", "group": "I"},
    {"match_id": "WC-052", "home_team": "Norway", "away_team": "Senegal", "date": "2026-06-23", "time": "01:00", "venue": "BMO Field", "city": "Toronto", "country": "Canada", "stage": "Group Stage", "group": "I"},
    {"match_id": "WC-053", "home_team": "Norway", "away_team": "France", "date": "2026-06-26", "time": "20:00", "venue": "Gillette Stadium", "city": "Boston", "country": "USA", "stage": "Group Stage", "group": "I"},
    {"match_id": "WC-054", "home_team": "Senegal", "away_team": "Iraq", "date": "2026-06-26", "time": "20:00", "venue": "BMO Field", "city": "Toronto", "country": "Canada", "stage": "Group Stage", "group": "I"},
    # Group J — Argentina, Algeria, Austria, Jordan
    {"match_id": "WC-055", "home_team": "Argentina", "away_team": "Algeria", "date": "2026-06-17", "time": "02:00", "venue": "Arrowhead Stadium", "city": "Kansas City", "country": "USA", "stage": "Group Stage", "group": "J"},
    {"match_id": "WC-056", "home_team": "Austria", "away_team": "Jordan", "date": "2026-06-17", "time": "05:00", "venue": "Levi's Stadium", "city": "San Francisco Bay Area", "country": "USA", "stage": "Group Stage", "group": "J"},
    {"match_id": "WC-057", "home_team": "Argentina", "away_team": "Austria", "date": "2026-06-22", "time": "18:00", "venue": "AT&T Stadium", "city": "Dallas", "country": "USA", "stage": "Group Stage", "group": "J"},
    {"match_id": "WC-058", "home_team": "Jordan", "away_team": "Algeria", "date": "2026-06-23", "time": "04:00", "venue": "Levi's Stadium", "city": "San Francisco Bay Area", "country": "USA", "stage": "Group Stage", "group": "J"},
    {"match_id": "WC-059", "home_team": "Algeria", "away_team": "Austria", "date": "2026-06-28", "time": "03:00", "venue": "Arrowhead Stadium", "city": "Kansas City", "country": "USA", "stage": "Group Stage", "group": "J"},
    {"match_id": "WC-060", "home_team": "Jordan", "away_team": "Argentina", "date": "2026-06-28", "time": "03:00", "venue": "AT&T Stadium", "city": "Dallas", "country": "USA", "stage": "Group Stage", "group": "J"},
    # Group K — Portugal, Congo DR, Uzbekistan, Colombia
    {"match_id": "WC-061", "home_team": "Portugal", "away_team": "Congo DR", "date": "2026-06-17", "time": "18:00", "venue": "NRG Stadium", "city": "Houston", "country": "USA", "stage": "Group Stage", "group": "K"},
    {"match_id": "WC-062", "home_team": "Uzbekistan", "away_team": "Colombia", "date": "2026-06-18", "time": "03:00", "venue": "Estadio Azteca", "city": "Mexico City", "country": "Mexico", "stage": "Group Stage", "group": "K"},
    {"match_id": "WC-063", "home_team": "Portugal", "away_team": "Uzbekistan", "date": "2026-06-23", "time": "18:00", "venue": "NRG Stadium", "city": "Houston", "country": "USA", "stage": "Group Stage", "group": "K"},
    {"match_id": "WC-064", "home_team": "Colombia", "away_team": "Congo DR", "date": "2026-06-24", "time": "03:00", "venue": "Estadio Akron", "city": "Guadalajara", "country": "Mexico", "stage": "Group Stage", "group": "K"},
    {"match_id": "WC-065", "home_team": "Colombia", "away_team": "Portugal", "date": "2026-06-28", "time": "00:30", "venue": "Hard Rock Stadium", "city": "Miami", "country": "USA", "stage": "Group Stage", "group": "K"},
    {"match_id": "WC-066", "home_team": "Congo DR", "away_team": "Uzbekistan", "date": "2026-06-28", "time": "00:30", "venue": "Mercedes-Benz Stadium", "city": "Atlanta", "country": "USA", "stage": "Group Stage", "group": "K"},
    # Group L — England, Croatia, Ghana, Panama
    {"match_id": "WC-067", "home_team": "England", "away_team": "Croatia", "date": "2026-06-17", "time": "21:00", "venue": "AT&T Stadium", "city": "Dallas", "country": "USA", "stage": "Group Stage", "group": "L"},
    {"match_id": "WC-068", "home_team": "Ghana", "away_team": "Panama", "date": "2026-06-18", "time": "00:00", "venue": "BMO Field", "city": "Toronto", "country": "Canada", "stage": "Group Stage", "group": "L"},
    {"match_id": "WC-069", "home_team": "England", "away_team": "Ghana", "date": "2026-06-23", "time": "21:00", "venue": "Gillette Stadium", "city": "Boston", "country": "USA", "stage": "Group Stage", "group": "L"},
    {"match_id": "WC-070", "home_team": "Panama", "away_team": "Croatia", "date": "2026-06-24", "time": "00:00", "venue": "Gillette Stadium", "city": "Boston", "country": "USA", "stage": "Group Stage", "group": "L"},
    {"match_id": "WC-071", "home_team": "Panama", "away_team": "England", "date": "2026-06-27", "time": "22:00", "venue": "MetLife Stadium", "city": "New York/New Jersey", "country": "USA", "stage": "Group Stage", "group": "L"},
    {"match_id": "WC-072", "home_team": "Croatia", "away_team": "Ghana", "date": "2026-06-27", "time": "22:00", "venue": "Lincoln Financial Field", "city": "Philadelphia", "country": "USA", "stage": "Group Stage", "group": "L"},
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
