#!/usr/bin/env python3
"""
Job Scraper — DevOps / Any Role in Bangalore
=============================================
Scrapes job listings from Indeed.in using Playwright.
Saves to CSV and JSON with a timestamped archive copy.

Usage:
    python3 job_scraper.py
    python3 job_scraper.py --role "DevOps" --exp "0-1"
    python3 job_scraper.py --role "Python Developer" --exp "fresher"
    python3 job_scraper.py --role "AWS Cloud Engineer" --exp "1"
    python3 job_scraper.py --no-headless    ← see browser working
"""

import json
import csv
import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("Run: pip3 install playwright --break-system-packages")
    print("Then: python3 -m playwright install chromium")
    sys.exit(1)

OUTPUT_DIR  = "job_evidence"
JOBS_JSON   = "jobs_found.json"
JOBS_CSV    = "jobs_found.csv"
ARCHIVE_DIR = "reports_archive"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)


def ss(page, name):
    path = f"{OUTPUT_DIR}/{name}.png"
    try:
        page.screenshot(path=path)
        return path
    except:
        return None


def scrape_indeed(role="DevOps", location="Bangalore", exp="0-1", headless=True):
    jobs = []
    query = f"{role} {exp} years experience"
    url   = f"https://in.indeed.com/jobs?q={quote(query)}&l={quote(location)}&sort=date"

    print("\n" + "=" * 65)
    print(f"  Job Scraper — {role} | {location} | {exp} yrs exp")
    print("=" * 65)
    print(f"  Source : Indeed India (in.indeed.com)")
    print(f"  URL    : {url}")
    print("=" * 65 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="en-IN",
        )
        page = context.new_page()

        try:
            # Navigate
            print("  Opening Indeed.in ...")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            ss(page, "01_indeed_search")

            # Handle cookie/consent popup if present
            for btn_text in ["Accept", "Accept All", "I agree", "OK"]:
                try:
                    btn = page.get_by_role("button", name=btn_text)
                    if btn.count():
                        btn.first.click()
                        time.sleep(1)
                        break
                except:
                    pass

            # Wait for job cards
            print("  Waiting for job listings...")
            try:
                page.wait_for_selector(
                    "div.job_seen_beacon, .jobsearch-ResultsList li, .tapItem, [data-testid='job-result']",
                    timeout=12000
                )
            except PWTimeout:
                print("  Timeout waiting for cards — trying scroll...")
                page.evaluate("window.scrollTo(0, 300)")
                time.sleep(2)

            ss(page, "02_job_listings")

            # Try multiple card selectors
            card_selectors = [
                "div.job_seen_beacon",
                ".tapItem",
                "li.css-1ac2h1w",
                "[data-testid='job-result']",
                ".jobsearch-ResultsList > li",
                "div[class*='job_seen']",
                "td.resultContent",
            ]

            cards = []
            used_sel = ""
            for sel in card_selectors:
                try:
                    found = page.locator(sel).all()
                    if found and len(found) > 0:
                        cards = found
                        used_sel = sel
                        break
                except:
                    continue

            print(f"  Found {len(cards)} job cards (selector: {used_sel or 'none'})")

            if not cards:
                # Last resort: get all text from page
                print("  No cards found — extracting from page text...")
                body_text = page.inner_text("body")
                ss(page, "03_page_fallback")
                print("  Screenshot saved. Page may have changed layout or requires JS.")
                browser.close()
                return jobs

            # Extract from each card
            for i, card in enumerate(cards[:30]):
                try:
                    job = {
                        "title":       "",
                        "company":     "",
                        "location":    "",
                        "salary":      "Not disclosed",
                        "experience":  exp + " years",
                        "skills":      "",
                        "posted":      "",
                        "url":         "",
                        "role_searched": role,
                        "scraped_at":  datetime.now().isoformat(),
                    }

                    # Title
                    for sel in ["h2.jobTitle a", "h2 a span", ".jobTitle span", "h2 span[id]", "a[data-jk]"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                job["title"] = el.inner_text().strip()
                                href = el.get_attribute("href") or ""
                                if href:
                                    job["url"] = "https://in.indeed.com" + href if href.startswith("/") else href
                                break
                        except:
                            pass

                    # Company
                    for sel in ["[data-testid='company-name']", ".companyName", "span.companyName a",
                                ".css-1h7lukg", "[class*='companyName']"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                job["company"] = el.inner_text().strip()
                                break
                        except:
                            pass

                    # Location
                    for sel in ["[data-testid='text-location']", ".companyLocation",
                                "div[class*='location']", ".css-1p0sjhy"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                job["location"] = el.inner_text().strip()
                                break
                        except:
                            pass

                    # Salary
                    for sel in [".salary-snippet-container", "[data-testid='attribute_snippet_testid']",
                                ".metadata.salary-snippet", "div[class*='salary']"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                job["salary"] = el.inner_text().strip()
                                break
                        except:
                            pass

                    # Posted date
                    for sel in ["[data-testid='myJobsStateDate']", "span.date", ".date",
                                "[class*='postedDate']", "table.jobCardShelfContainer span"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                job["posted"] = el.inner_text().strip()
                                break
                        except:
                            pass

                    if job["title"]:
                        jobs.append(job)
                        sal = f" | {job['salary'][:20]}" if job["salary"] != "Not disclosed" else ""
                        print(f"    {len(jobs):>2}. {job['title'][:42]:<44} {job['company'][:25]:<27}{sal}")

                except Exception:
                    continue

            ss(page, "03_extracted")
            browser.close()

        except Exception as e:
            print(f"\n  Error: {e}")
            try:
                ss(page, "error_state")
                browser.close()
            except:
                pass

    return jobs


def save_jobs(jobs, role, exp, location):
    fields = ["title", "company", "location", "salary",
              "experience", "skills", "posted", "url", "scraped_at"]

    # Latest file (always overwritten)
    with open(JOBS_JSON, "w") as f:
        json.dump({"role": role, "location": location, "exp": exp,
                   "total": len(jobs), "scraped_at": datetime.now().isoformat(),
                   "jobs": jobs}, f, indent=2)

    with open(JOBS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(jobs)

    # Archived copy with timestamp
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = role.lower().replace(" ", "_")[:25]
    arch = os.path.join(ARCHIVE_DIR, f"{ts}_jobs_{slug}_{location.lower()}.csv")
    with open(arch, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(jobs)

    print(f"\n  Latest CSV  : {JOBS_CSV}  ← open in Excel")
    print(f"  JSON        : {JOBS_JSON}")
    print(f"  Archived as : {arch}")


def main():
    parser = argparse.ArgumentParser(description="Scrape jobs from Indeed India")
    parser.add_argument("--role",        default="DevOps",     help="Job role")
    parser.add_argument("--location",    default="Bangalore",  help="City")
    parser.add_argument("--exp",         default="0-1",        help="Experience in years")
    parser.add_argument("--no-headless", action="store_true",  help="Show browser window")
    args = parser.parse_args()

    jobs = scrape_indeed(
        role     = args.role,
        location = args.location,
        exp      = args.exp,
        headless = not args.no_headless,
    )

    print("\n" + "=" * 65)
    if jobs:
        save_jobs(jobs, args.role, args.exp, args.location)
        print(f"\n  Done! {len(jobs)} {args.role} jobs found in {args.location}")
        print(f"  Run: python3 merge_reports.py → open master_report.xlsx")
    else:
        print(f"\n  No jobs found. Tips:")
        print(f"  1. Run with --no-headless to see what's happening")
        print(f"  2. Check job_evidence/ folder for screenshots")
        print(f"  3. Indeed may show a CAPTCHA — try again in a few minutes")
    print("=" * 65)


if __name__ == "__main__":
    main()
