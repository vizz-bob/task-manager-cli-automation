#!/usr/bin/env python3
"""
Bangalore Ads — Full Combined Report
======================================
Searches ALL ad/marketing categories in Bangalore in one run,
removes duplicates, and saves one big CSV + JSON report.

Usage:
    python3 bangalore_ads_all.py
    python3 bangalore_ads_all.py --max 10     # 10 per category
    python3 bangalore_ads_all.py --max 20     # 20 per category (default)
"""

import requests
import json
import csv
import os
import sys
import time
import argparse
from datetime import datetime

# ── Config ────────────────────────────────────────────────────
BASE_URL    = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
JSON_OUTPUT = "bangalore_all_companies.json"
CSV_OUTPUT  = "bangalore_all_companies.csv"
LOG_FILE    = "bangalore_all_fetch.log"

# All categories to search
CATEGORIES = [
    "advertising agency in Bangalore",
    "digital marketing company in Bangalore",
    "social media marketing Bangalore",
    "SEO company Bangalore",
    "online advertising Bangalore",
    "brand marketing agency Bangalore",
    "media buying agency Bangalore",
]


# ── Helpers ───────────────────────────────────────────────────
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def get_api_key():
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        print("\n" + "=" * 60)
        print("  Google API Key Required")
        print("  Get one free at: https://console.cloud.google.com")
        print("=" * 60)
        key = input("\n  Paste your Google API Key: ").strip()
        if not key:
            print("Error: No API key provided.")
            sys.exit(1)
    return key


def search_places(query, api_key, page_token=None):
    params = {"query": query, "key": api_key, "language": "en", "region": "in"}
    if page_token:
        params["pagetoken"] = page_token
    r = requests.get(BASE_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def get_details(place_id, api_key):
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,business_status",
        "key": api_key,
    }
    r = requests.get(DETAILS_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("result", {})


# ── Fetch one category ────────────────────────────────────────
def fetch_category(query, api_key, max_results):
    companies = []
    seen_ids = set()
    page_token = None
    page = 1

    while len(companies) < max_results:
        data = search_places(query, api_key, page_token)
        status = data.get("status")

        if status in ("ZERO_RESULTS", "INVALID_REQUEST"):
            break
        if status != "OK":
            log(f"  API error: {status}")
            break

        for place in data.get("results", []):
            if len(companies) >= max_results:
                break
            pid = place.get("place_id")
            if pid in seen_ids:
                continue
            # Keep all results (city is already in the search query)
            address = place.get("formatted_address", "")
            seen_ids.add(pid)

            company = {
                "name":            place.get("name", ""),
                "address":         address,
                "place_id":        pid,
                "rating":          place.get("rating"),
                "total_ratings":   place.get("user_ratings_total"),
                "business_status": place.get("business_status", ""),
                "category":        query,
                "phone":           None,
                "website":         None,
            }
            time.sleep(0.2)
            details = get_details(pid, api_key)
            company["phone"]   = details.get("formatted_phone_number")
            company["website"] = details.get("website")
            companies.append(company)
            print(f"    ✓ {company['name'][:45]:<45} ⭐{company['rating'] or 'N/A'}")

        page_token = data.get("next_page_token")
        if not page_token:
            break
        page += 1
        time.sleep(2)

    return companies


# ── Deduplicate ───────────────────────────────────────────────
def deduplicate(all_companies):
    seen = {}
    for c in all_companies:
        pid = c["place_id"]
        if pid not in seen:
            seen[pid] = c
        else:
            # Merge categories
            existing_cat = seen[pid]["category"]
            new_cat = c["category"]
            if new_cat not in existing_cat:
                seen[pid]["category"] = existing_cat + " | " + new_cat
    return list(seen.values())


# ── Save ──────────────────────────────────────────────────────
def save_json(companies, categories):
    out = {
        "generated_at":     datetime.now().isoformat(),
        "city":             "Bangalore",
        "categories_searched": categories,
        "total_unique":     len(companies),
        "companies":        companies,
    }
    with open(JSON_OUTPUT, "w") as f:
        json.dump(out, f, indent=2)


def save_csv(companies):
    fields = ["name", "address", "rating", "total_ratings",
              "phone", "website", "category", "business_status"]
    with open(CSV_OUTPUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(companies, key=lambda x: x.get("rating") or 0, reverse=True))


# ── Print final summary ───────────────────────────────────────
def print_summary(companies):
    print("\n" + "=" * 70)
    print("  BANGALORE ADS COMPANIES — FULL REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"  Total unique companies : {len(companies)}")

    rated = [c for c in companies if c.get("rating")]
    if rated:
        avg = sum(c["rating"] for c in rated) / len(rated)
        top = [c for c in rated if c["rating"] >= 4.5]
        print(f"  Average rating         : {avg:.1f} ⭐")
        print(f"  Top rated (≥4.5★)      : {len(top)}")

    print(f"  Have phone number      : {sum(1 for c in companies if c.get('phone'))}")
    print(f"  Have website           : {sum(1 for c in companies if c.get('website'))}")
    print("\n  Top 10 Companies by Rating:")
    print("  " + "-" * 66)
    top10 = sorted(companies, key=lambda x: x.get("rating") or 0, reverse=True)[:10]
    for i, c in enumerate(top10, 1):
        name    = (c.get("name") or "")[:38]
        rating  = f"{c.get('rating')}⭐" if c.get("rating") else "N/A"
        phone   = (c.get("phone") or "N/A")[:16]
        print(f"  {i:>2}. {name:<40} {rating:<7} {phone}")
    print("=" * 70)
    print(f"\n  JSON saved : {JSON_OUTPUT}")
    print(f"  CSV saved  : {CSV_OUTPUT}  ← Open this in Excel!")
    print("=" * 70 + "\n")


# ── Main ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Fetch all ad/marketing companies in Bangalore across multiple categories."
    )
    parser.add_argument("--max", type=int, default=20,
                        help="Max results per category (default: 20)")
    args = parser.parse_args()

    api_key = get_api_key()

    print("\n" + "=" * 70)
    print("  Bangalore Ads — Full Combined Fetch")
    print("=" * 70)
    print(f"  Categories  : {len(CATEGORIES)}")
    print(f"  Max per cat : {args.max}")
    print(f"  Est. total  : up to {len(CATEGORIES) * args.max} companies")
    print("=" * 70)

    all_companies = []

    for i, category in enumerate(CATEGORIES, 1):
        print(f"\n  [{i}/{len(CATEGORIES)}] Searching: {category}")
        print("  " + "-" * 50)
        log(f"Fetching category: {category}")
        results = fetch_category(category, api_key, args.max)
        all_companies.extend(results)
        log(f"  Got {len(results)} results. Total so far: {len(all_companies)}")
        time.sleep(1)

    # Remove duplicates (same company appearing in multiple categories)
    unique = deduplicate(all_companies)
    log(f"Deduplication: {len(all_companies)} → {len(unique)} unique companies")

    save_json(unique, CATEGORIES)
    save_csv(unique)
    print_summary(unique)


if __name__ == "__main__":
    main()
