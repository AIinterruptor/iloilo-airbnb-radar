"""
Iloilo Airbnb Radar — Booking.com Price Scraper
Fetches competitor pricing near Festive Walk / SMDC Style Residences.
Uses Booking.com's structured API via rapid/affiliate endpoint.
Designed to run daily via GitHub Actions.
"""

import json
import os
import csv
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Booking.com Rapid API (free tier via RapidAPI or affiliate)
# For GitHub Actions, we use the MCP-compatible approach:
# The GH Action will call this script to process pre-fetched data.

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

HISTORY_FILE = DATA_DIR / "price_history.csv"
LATEST_FILE = DATA_DIR / "latest.json"
STATS_FILE = DATA_DIR / "stats.json"

CSV_HEADERS = [
    "date", "property_name", "property_id", "price_per_night", "price_per_stay",
    "currency", "stars", "review_score", "review_count", "latitude", "longitude",
    "address", "checkin_date", "checkout_date", "tier"
]


def classify_tier(name: str) -> str:
    name_lower = name.lower()
    direct_tags = ["smdc", "style residen", "megaworld", "palladium", "festive walk", "saint honore"]
    budget_tags = ["dormitel", "pallet", "pension", "hostel"]
    premium_tags = ["seda", "belmont", "richmonde", "courtyard"]

    for tag in direct_tags:
        if tag in name_lower:
            return "direct_competitor"
    for tag in budget_tags:
        if tag in name_lower:
            return "budget"
    for tag in premium_tags:
        if tag in name_lower:
            return "premium"
    return "midrange"


def process_booking_data(raw_data: list, checkin: str, checkout: str) -> list:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = []

    for acc in raw_data:
        price_total = acc.get("price", {}).get("book")
        if price_total is None:
            continue

        nights = max(1, (datetime.strptime(checkout, "%Y-%m-%d") - datetime.strptime(checkin, "%Y-%m-%d")).days)
        price_per_night = round(price_total / nights, 2)

        rating = acc.get("rating", {})
        location = acc.get("location", {})
        coords = location.get("coordinates", {})

        row = {
            "date": today,
            "property_name": acc.get("name", "Unknown"),
            "property_id": str(acc.get("id", "")),
            "price_per_night": price_per_night,
            "price_per_stay": price_total,
            "currency": acc.get("price", {}).get("currency", "PHP"),
            "stars": rating.get("stars", ""),
            "review_score": rating.get("review_score", ""),
            "review_count": rating.get("number_of_reviews", ""),
            "latitude": coords.get("latitude", ""),
            "longitude": coords.get("longitude", ""),
            "address": location.get("address", ""),
            "checkin_date": checkin,
            "checkout_date": checkout,
            "tier": classify_tier(acc.get("name", ""))
        }
        rows.append(row)

    return rows


def append_to_history(rows: list):
    file_exists = HISTORY_FILE.exists()

    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def save_latest(rows: list, checkin: str, checkout: str):
    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "search_params": {
            "checkin": checkin,
            "checkout": checkout,
            "adults": 2,
            "rooms": 1,
            "radius_km": 3,
            "center": "Festive Walk, Iloilo City"
        },
        "properties": sorted(rows, key=lambda r: r["price_per_night"]),
        "count": len(rows)
    }
    with open(LATEST_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def compute_stats():
    if not HISTORY_FILE.exists():
        return

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    if not all_rows:
        return

    dates = sorted(set(r["date"] for r in all_rows))
    properties = sorted(set(r["property_name"] for r in all_rows))

    by_property = {}
    for row in all_rows:
        name = row["property_name"]
        if name not in by_property:
            by_property[name] = []
        by_property[name].append(row)

    stats = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_snapshots": len(dates),
        "date_range": {"first": dates[0], "last": dates[-1]},
        "properties_tracked": len(properties),
        "summary": []
    }

    for name, rows in by_property.items():
        prices = [float(r["price_per_night"]) for r in rows if r["price_per_night"]]
        if not prices:
            continue

        latest = rows[-1]
        entry = {
            "name": name,
            "tier": latest.get("tier", "unknown"),
            "stars": latest.get("stars", ""),
            "review_score": latest.get("review_score", ""),
            "current_price": prices[-1],
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": round(sum(prices) / len(prices), 2),
            "data_points": len(prices)
        }

        if len(prices) >= 2:
            entry["price_change"] = round(prices[-1] - prices[-2], 2)
            entry["price_change_pct"] = round((prices[-1] - prices[-2]) / prices[-2] * 100, 1)

        stats["summary"].append(entry)

    stats["summary"].sort(key=lambda s: s["current_price"])

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_prices.py <raw_booking_data.json>")
        print("  The JSON file should contain the Booking.com API response array.")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    raw_data = payload.get("accommodations", payload if isinstance(payload, list) else [])
    checkin = payload.get("checkin", (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d"))
    checkout = payload.get("checkout", (datetime.now(timezone.utc) + timedelta(days=32)).strftime("%Y-%m-%d"))

    rows = process_booking_data(raw_data, checkin, checkout)
    print(f"Processed {len(rows)} properties")

    append_to_history(rows)
    save_latest(rows, checkin, checkout)
    compute_stats()

    print(f"History: {HISTORY_FILE}")
    print(f"Latest:  {LATEST_FILE}")
    print(f"Stats:   {STATS_FILE}")


if __name__ == "__main__":
    main()
