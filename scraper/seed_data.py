"""Seed the dashboard with the initial Booking.com spike data."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fetch_prices import process_booking_data, append_to_history, save_latest, compute_stats

SPIKE_DATA = {
    "checkin": "2026-07-31",
    "checkout": "2026-08-02",
    "accommodations": [
        {"id": 1108701, "name": "Injap Tower Hotel", "price": {"book": 3439.47, "currency": "PHP"}, "rating": {"number_of_reviews": 1599, "review_score": 7.8, "stars": 3}, "location": {"address": "West Diversion Road, Mandurriao", "coordinates": {"latitude": 10.714051, "longitude": 122.552732}}},
        {"id": 12019279, "name": "Hop Inn Hotel Iloilo", "price": {"book": 3600, "currency": "PHP"}, "rating": {"number_of_reviews": 381, "review_score": 8.2, "stars": 3}, "location": {"address": "2 Donato Pison Avenue, Atria Park District", "coordinates": {"latitude": 10.707865, "longitude": 122.545542}}},
        {"id": 255114, "name": "Hotel Del Rio", "price": {"book": 4400, "currency": "PHP"}, "rating": {"number_of_reviews": 184, "review_score": 8.5, "stars": 3}, "location": {"address": "M.H. Del Pilar Street, Molo", "coordinates": {"latitude": 10.70007, "longitude": 122.552164}}},
        {"id": 11373274, "name": "Pallet Homes - Megaworld", "price": {"book": 2084.4, "currency": "PHP"}, "rating": {}, "location": {"address": "208 Villa Alegre Road", "coordinates": {"latitude": 10.719647, "longitude": 122.551206}}},
        {"id": 1482909, "name": "Seda Atria Ilo-ilo", "price": {"book": 6601.5, "currency": "PHP"}, "rating": {"number_of_reviews": 278, "review_score": 8.6, "stars": 4}, "location": {"address": "Pison Avenue, Atria Park District, Mandurriao", "coordinates": {"latitude": 10.7077, "longitude": 122.548617}}},
        {"id": 15336137, "name": "Belmont Hotel Iloilo", "price": {"book": 7702.8, "currency": "PHP"}, "rating": {}, "location": {"address": "Iloilo Business Park", "coordinates": {"latitude": 10.713513, "longitude": 122.545422}}},
        {"id": 3558116, "name": "GT Hotel Jaro", "price": {"book": 2700, "currency": "PHP"}, "rating": {}, "location": {"address": "Mc Arthur Drive Tabuc Suba Jaro", "coordinates": {"latitude": 10.733207, "longitude": 122.559997}}},
        {"id": 13802214, "name": "Casa de Vera Iloilo SMDC Style Residences", "price": {"book": 3851.78, "currency": "PHP"}, "rating": {"number_of_reviews": 30, "review_score": 9.4, "stars": 3}, "location": {"address": "SMDC Style Residences Tower B", "coordinates": {"latitude": 10.715384, "longitude": 122.548984}}},
        {"id": 15478355, "name": "MARY & NICK'S STYLE RESIDENCE Iloilo City", "price": {"book": 2975, "currency": "PHP"}, "rating": {"number_of_reviews": 6, "review_score": 8.0, "stars": 3}, "location": {"address": "SM Iloilo SMDC Style residences B1707", "coordinates": {"latitude": 10.715613, "longitude": 122.549087}}},
        {"id": 1411618, "name": "One Lourdes Dormitel", "price": {"book": 1964.28, "currency": "PHP"}, "rating": {"number_of_reviews": 133, "review_score": 8.2, "stars": 2}, "location": {"address": "JTS Building Corner Ledesma Fuentes Street", "coordinates": {"latitude": 10.694307, "longitude": 122.563383}}}
    ]
}

rows = process_booking_data(SPIKE_DATA["accommodations"], SPIKE_DATA["checkin"], SPIKE_DATA["checkout"])
print(f"Seeding {len(rows)} properties...")
append_to_history(rows)
save_latest(rows, SPIKE_DATA["checkin"], SPIKE_DATA["checkout"])
compute_stats()
print("Done! Data seeded to data/ directory.")
