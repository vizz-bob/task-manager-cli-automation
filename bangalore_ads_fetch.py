#!/usr/bin/env python3
"""
Bangalore Ads Fetcher
=====================
Fetches advertising and digital marketing companies in Bangalore
using the Google Places API (free tier — $200 credit/month).

What it does:
- Searches Google Maps for ad/marketing companies in Bangalore
- Saves company name, address, phone, website, rating
- Saves results to bangalore_companies.json

Setup (one time):
    1. Get a free Google API key (see GOOGLE_API_KEY_SETUP.md)
    2. pip install requests

Usage:
    python3 bangalore_ads_fetch.py
    python3 bangalore_ads_fetch.py --category "digital marketing"
    python3 bangalore_ads_fetch.py --category "advertising agency"
    python3 bangalore_ads_fetch.py --category "social media marketing"
"""

import requests
import json
import os
import sys
import time
import argparse
from datetime import datetime


# ── Config ───────────────────────────────────────────────────
BASE_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
OUTPUT_FILE = "bangalore_companies.json"
LOG_FILE = "bangalore_fetch.log"

# Categories to search
CATEGORIES = [
    "advertising agency in Bangalore",
    "digital marketing company in Bangalore",
    "social media marketing Bangalore",
    "SEO company Bangalore",
    "online advertising Bangalore",
]


# ── Helpers ───────────────────────────────────────────────────
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def get_api_key():
    """Get API key from environment variable or prompt user."""
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        print("\n" + "=" * 60)
        print("  Google API Key Required")
        print("=" * 60)
        print("  Get a free key at: https://console.cloud.google.com")
        print("  Enable: Places API")
        print("  Free tier: $200 credit/month (covers ~10,000 searches)")
        print("=" * 60)
        key = input("\n  Paste your Google API Key here: ").strip()
        if not key:
            print("Error: No API key provided.")
            sys.exit(1)
    return key


# ── Fetch one page of results ─────────────────────────────────
def search_places(query: str, api_key: str, page_token: str = None) -> dict:
    params = {
        "query": query,
        "key": api_key,
        "language": "en",
        "region": "in",
    }
    if page_token:
        params["pagetoken"] = page_token

    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


# ── Get extra details (phone, website) for one place ─────────
def get_place_details(place_id: str, api_key: str) -> dict:
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,business_status",
        "key": api_key,
    }
    response = requests.get(DETAILS_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    return data.get("result", {})


# ── Main fetch loop ───────────────────────────────────────────
def fetch_companies(query: str, api_key: str, max_results: int = 20) -> list:
    companies = []
    page_token = None
    page = 1

    while len(companies) < max_results:
        log(f"  Fetching page {page} for: '{query}'")
        data = search_places(query, api_key, page_token)
        status = data.get("status")

        if status == "ZERO_RESULTS":
            log(f"  No results found for: {query}")
            break
        elif status != "OK":
            log(f"  API error: {status} — {data.get('error_message', '')}")
            break

        results = data.get("results", [])
        log(f"  Found {len(results)} results on page {page}")

        for place in results:
            if len(companies) >= max_results:
                break

            # Keep all results (city is already in the search query)
            address = place.get("formatted_address", "")

            company = {
                "name": place.get("name", ""),
                "address": address,
                "place_id": place.get("place_id", ""),
                "rating": place.get("rating"),
                "total_ratings": place.get("user_ratings_total"),
                "business_status": place.get("business_status", ""),
                "types": place.get("types", []),
                "phone": None,
                "website": None,
            }

            # Get phone + website (costs 1 API call per company)
            if place.get("place_id"):
                time.sleep(0.2)  # Be polite to the API
                details = get_place_details(place["place_id"], api_key)
                company["phone"] = details.get("formatted_phone_number")
                company["website"] = details.get("website")

            companies.append(company)
            print(f"    ✓ {company['name']} | ⭐{company['rating']} | {company['phone'] or 'no phone'}")

        # Next page
        page_token = data.get("next_page_token")
        if not page_token:
            break
        page += 1
        time.sleep(2)  # Google requires a short wait before using next_page_token

    return companies


# ── Save results ─────────────────────────────────────────────
def save_results(companies: list, query: str):
    output = {
        "fetched_at": datetime.now().isoformat(),
        "search_query": query,
        "city": "Bangalore",
        "total_found": len(companies),
        "companies": companies,
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    log(f"  Saved {len(companies)} companies to {OUTPUT_FILE}")


# ── Main ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Fetch advertising companies in Bangalore from Google Places."
    )
    parser.add_argument(
        "--category",
        default="advertising agency in Bangalore",
        help="Search query (default: 'advertising agency in Bangalore')"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=20,
        help="Max companies to fetch (default: 20)"
    )
    args = parser.parse_args()

    api_key = get_api_key()

    print("\n" + "=" * 60)
    print("  Bangalore Ads Company Fetcher")
    print("=" * 60)
    print(f"  Search : {args.category}")
    print(f"  Max    : {args.max} companies")
    print(f"  Output : {OUTPUT_FILE}")
    print("=" * 60 + "\n")

    log(f"Starting fetch: '{args.category}'")
    companies = fetch_companies(args.category, api_key, args.max)
    save_results(companies, args.category)

    print(f"\n  Done! {len(companies)} companies saved to {OUTPUT_FILE}")
    print("  Next: python3 bangalore_ads_report.py")


if __name__ == "__main__":
    main()
