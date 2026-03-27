#!/usr/bin/env python3
"""
Bangalore Ads Report Generator
================================
Reads bangalore_companies.json and produces:
  1. A summary report in the terminal
  2. A CSV file you can open in Excel
  3. A filtered list of top-rated companies

Usage:
    python3 bangalore_ads_report.py
    python3 bangalore_ads_report.py --min-rating 4.0
    python3 bangalore_ads_report.py --output my_report.csv
"""

import json
import csv
import os
import sys
import argparse
from datetime import datetime


INPUT_FILE = "bangalore_companies.json"
DEFAULT_CSV  = "bangalore_ads_report.csv"
REPORTS_DIR  = "reports_archive"


# ── Load ──────────────────────────────────────────────────────
def load_companies(filepath: str) -> dict:
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        print("Run bangalore_ads_fetch.py first to download company data.")
        sys.exit(1)
    with open(filepath) as f:
        return json.load(f)


# ── Filter ────────────────────────────────────────────────────
def filter_companies(companies: list, min_rating: float = None) -> list:
    filtered = companies
    if min_rating:
        filtered = [c for c in filtered if c.get("rating") and c["rating"] >= min_rating]
    return sorted(filtered, key=lambda x: x.get("rating") or 0, reverse=True)


# ── Print terminal report ─────────────────────────────────────
def print_report(data: dict, companies: list, min_rating: float):
    print("\n" + "=" * 70)
    print("  BANGALORE ADS COMPANIES REPORT")
    print(f"  Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Fetched   : {data.get('fetched_at', 'unknown')}")
    print(f"  Search    : {data.get('search_query', '')}")
    print("=" * 70)
    print(f"  Total companies found : {data.get('total_found', 0)}")
    print(f"  After filter (≥{min_rating}★)  : {len(companies)}")

    # Rating breakdown
    rated = [c for c in companies if c.get("rating")]
    if rated:
        avg = sum(c["rating"] for c in rated) / len(rated)
        top = [c for c in rated if c["rating"] >= 4.5]
        print(f"  Average rating        : {avg:.1f} ⭐")
        print(f"  Top rated (≥4.5★)     : {len(top)} companies")

    # Has website
    with_web = [c for c in companies if c.get("website")]
    with_phone = [c for c in companies if c.get("phone")]
    print(f"  Have website          : {len(with_web)}")
    print(f"  Have phone number     : {len(with_phone)}")

    print("\n" + "-" * 70)
    print(f"  {'#':<3} {'Company Name':<35} {'Rating':<8} {'Phone':<18} {'Website'}")
    print("-" * 70)

    for i, company in enumerate(companies, 1):
        name = (company.get("name") or "")[:34]
        rating = f"{company.get('rating', 'N/A')}⭐" if company.get("rating") else "N/A"
        phone = (company.get("phone") or "N/A")[:17]
        website = company.get("website") or "N/A"
        if website != "N/A":
            website = website.replace("https://", "").replace("http://", "")[:30]
        print(f"  {i:<3} {name:<35} {rating:<8} {phone:<18} {website}")

    print("=" * 70)


# ── Save CSV ──────────────────────────────────────────────────
def save_csv(companies: list, output_path: str):
    fields = ["name", "address", "rating", "total_ratings",
              "phone", "website", "business_status", "place_id"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(companies)

    print(f"\n  CSV saved to: {output_path}")
    print(f"  Open in Excel / Google Sheets to analyse")


# ── Main ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Generate a report of Bangalore ad companies."
    )
    parser.add_argument(
        "--input", default=INPUT_FILE,
        help=f"Input JSON file (default: {INPUT_FILE})"
    )
    parser.add_argument(
        "--min-rating", type=float, default=0.0,
        help="Minimum star rating to include (default: 0 = all)"
    )
    parser.add_argument(
        "--output", default=DEFAULT_CSV,
        help=f"Output CSV filename (default: {DEFAULT_CSV})"
    )
    args = parser.parse_args()

    data = load_companies(args.input)
    companies = filter_companies(data.get("companies", []), args.min_rating)
    print_report(data, companies, args.min_rating)

    # Always save the latest report (overwrites)
    save_csv(companies, args.output)

    # Also save a timestamped copy so old data is never lost
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    query_slug = data.get("search_query", "report").lower()
    query_slug = "".join(c if c.isalnum() else "_" for c in query_slug)[:40]
    archive_path = os.path.join(REPORTS_DIR, f"{timestamp}_{query_slug}.csv")
    save_csv(companies, archive_path)
    print(f"\n  Archive copy saved to: {archive_path}")
    print(f"  All reports kept in  : {REPORTS_DIR}/")

    # List all saved reports
    all_reports = sorted(os.listdir(REPORTS_DIR))
    print(f"\n  Reports archive ({len(all_reports)} total):")
    for r in all_reports[-5:]:  # show last 5
        fpath = os.path.join(REPORTS_DIR, r)
        size = os.path.getsize(fpath)
        print(f"    {r}  ({size:,} bytes)")


if __name__ == "__main__":
    main()
