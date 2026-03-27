#!/usr/bin/env python3
"""
Freelancer Scraper — People Looking for Web Development Work
=============================================================
Scrapes profiles from Internshala and LinkedIn (public pages)
of people actively looking for web development / freelance work.

Sources:
  1. Internshala Talent — students/freshers looking for work
  2. Indeed Resume search — candidates seeking web dev jobs
  3. GitHub Jobs profiles — developers with open to work status

What it collects:
  - Name / Profile title
  - Skills (HTML, CSS, React, Node.js etc.)
  - Location
  - Experience level
  - Profile URL
  - Available for (freelance / full-time / internship)

Usage:
    python3 freelancer_scraper.py
    python3 freelancer_scraper.py --skill "React Developer" --location "Bangalore"
    python3 freelancer_scraper.py --skill "Full Stack Developer" --location "Remote"
    python3 freelancer_scraper.py --no-headless    ← see browser working
"""

import json
import csv
import os
import sys
import time
import argparse
from datetime import datetime
from urllib.parse import quote

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("Run: pip3 install playwright --break-system-packages")
    print("Then: python3 -m playwright install chromium")
    sys.exit(1)

OUTPUT_DIR  = "freelancer_evidence"
OUTPUT_JSON = "freelancers_found.json"
OUTPUT_CSV  = "freelancers_found.csv"
ARCHIVE_DIR = "reports_archive"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)


def take_ss(page, name):
    path = f"{OUTPUT_DIR}/{name}.png"
    try:
        page.screenshot(path=path)
        return path
    except:
        return None


# ══════════════════════════════════════════════════════════════
# SOURCE 1 — Internshala Talent (freshers / students)
# ══════════════════════════════════════════════════════════════
def scrape_internshala(skill, location, headless, profiles):
    skill_slug = skill.lower().replace(" ", "-")
    url = f"https://internshala.com/talent/search/?role={quote(skill)}&location={quote(location)}"

    print(f"\n  [Source 1] Internshala Talent")
    print(f"  URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            time.sleep(3)
            take_ss(page, "internshala_01_home")

            # Wait for profile cards
            try:
                page.wait_for_selector(
                    ".profile-card, .talent-card, [class*='profile'], [class*='candidate']",
                    timeout=10000
                )
            except PWTimeout:
                print("  Timeout — trying scroll...")
                page.evaluate("window.scrollTo(0,400)")
                time.sleep(2)

            take_ss(page, "internshala_02_results")

            # Try multiple selectors
            card_sels = [
                ".profile-card",
                ".talent-card",
                "[class*='candidateCard']",
                "[class*='profile-container']",
                "div[class*='profileCard']",
            ]

            cards = []
            for sel in card_sels:
                try:
                    found = page.locator(sel).all()
                    if found:
                        cards = found
                        print(f"  Found {len(cards)} profiles (selector: {sel})")
                        break
                except:
                    continue

            for card in cards[:20]:
                try:
                    profile = {
                        "name":       "",
                        "title":      skill,
                        "skills":     "",
                        "location":   location,
                        "experience": "Fresher",
                        "available":  "Internship / Full-time",
                        "url":        "",
                        "source":     "Internshala",
                        "scraped_at": datetime.now().isoformat(),
                    }

                    for sel in ["h3", ".name", "[class*='name']", "strong"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                profile["name"] = el.inner_text().strip()
                                break
                        except:
                            pass

                    for sel in ["a", "[href]"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                href = el.get_attribute("href") or ""
                                if "profile" in href or "candidate" in href:
                                    profile["url"] = "https://internshala.com" + href if href.startswith("/") else href
                                    break
                        except:
                            pass

                    for sel in [".skills", "[class*='skill']", "span.tag", ".tag"]:
                        try:
                            els = card.locator(sel).all()
                            if els:
                                profile["skills"] = ", ".join(e.inner_text().strip() for e in els[:6])
                                break
                        except:
                            pass

                    if profile["name"]:
                        profiles.append(profile)
                        print(f"    ✓ {profile['name']:<30} | {profile['skills'][:40]}")

                except Exception:
                    continue

        except Exception as e:
            print(f"  Error on Internshala: {e}")
            take_ss(page, "internshala_error")

        browser.close()

    return profiles


# ══════════════════════════════════════════════════════════════
# SOURCE 2 — Indeed Resume / Candidate Search
# ══════════════════════════════════════════════════════════════
def scrape_indeed_candidates(skill, location, headless, profiles):
    url = f"https://in.indeed.com/resumes?q={quote(skill)}&l={quote(location)}"

    print(f"\n  [Source 2] Indeed Resume Search")
    print(f"  URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            locale="en-IN"
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            time.sleep(3)
            take_ss(page, "indeed_resumes_01")

            # Handle popups
            for btn in ["Accept", "Accept All", "Continue", "OK"]:
                try:
                    b = page.get_by_role("button", name=btn)
                    if b.count():
                        b.first.click()
                        time.sleep(1)
                        break
                except:
                    pass

            try:
                page.wait_for_selector(
                    ".resumeCard, .ia-ResumeCard, [class*='resume'], [class*='Resume']",
                    timeout=10000
                )
            except PWTimeout:
                print("  Trying scroll...")
                page.evaluate("window.scrollTo(0,400)")
                time.sleep(2)

            take_ss(page, "indeed_resumes_02_results")

            card_sels = [
                ".resumeCard",
                ".ia-ResumeCard",
                "[class*='ResumeCard']",
                "[class*='resumeCard']",
                "div[data-tn-element='resumeCard']",
            ]

            cards = []
            for sel in card_sels:
                try:
                    found = page.locator(sel).all()
                    if found:
                        cards = found
                        print(f"  Found {len(cards)} resume cards (selector: {sel})")
                        break
                except:
                    continue

            for card in cards[:20]:
                try:
                    profile = {
                        "name":       "",
                        "title":      "",
                        "skills":     "",
                        "location":   "",
                        "experience": "",
                        "available":  "Actively Looking",
                        "url":        "",
                        "source":     "Indeed",
                        "scraped_at": datetime.now().isoformat(),
                    }

                    for sel in ["h2 a", ".resumeName a", "[class*='name'] a", "a[href*='resume']"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                profile["name"] = el.inner_text().strip()
                                href = el.get_attribute("href") or ""
                                profile["url"] = "https://in.indeed.com" + href if href.startswith("/") else href
                                break
                        except:
                            pass

                    for sel in [".resumeTitle", "[class*='title']", "span[class*='Title']"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                profile["title"] = el.inner_text().strip()
                                break
                        except:
                            pass

                    for sel in ["[class*='location']", ".resumeLocation"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                profile["location"] = el.inner_text().strip()
                                break
                        except:
                            pass

                    for sel in ["[class*='experience']", ".resumeExp"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                profile["experience"] = el.inner_text().strip()
                                break
                        except:
                            pass

                    for sel in ["[class*='skill']", ".resumeSkills span", "li[class*='skill']"]:
                        try:
                            els = card.locator(sel).all()
                            if els:
                                profile["skills"] = ", ".join(e.inner_text().strip() for e in els[:6])
                                break
                        except:
                            pass

                    if profile["name"]:
                        profiles.append(profile)
                        print(f"    ✓ {profile['name']:<30} | {profile['title'][:35]}")

                except Exception:
                    continue

        except Exception as e:
            print(f"  Error on Indeed: {e}")
            take_ss(page, "indeed_error")

        browser.close()

    return profiles


# ══════════════════════════════════════════════════════════════
# SOURCE 3 — LinkedIn Public Search (Open to Work)
# ══════════════════════════════════════════════════════════════
def scrape_linkedin_public(skill, location, headless, profiles):
    url = f"https://www.linkedin.com/search/results/people/?keywords={quote(skill + ' open to work ' + location)}&origin=GLOBAL_SEARCH_HEADER"

    print(f"\n  [Source 3] LinkedIn Public Search")
    print(f"  URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            time.sleep(3)
            take_ss(page, "linkedin_01_search")

            # LinkedIn often asks to log in — check for sign-in wall
            page_text = page.inner_text("body").lower()
            if "sign in" in page_text or "join now" in page_text:
                print("  LinkedIn requires login — skipping (public data only)")
                take_ss(page, "linkedin_login_wall")
                browser.close()
                return profiles

            try:
                page.wait_for_selector(
                    ".reusable-search__result-container, [class*='search-result']",
                    timeout=8000
                )
            except PWTimeout:
                print("  No results visible on LinkedIn")
                browser.close()
                return profiles

            take_ss(page, "linkedin_02_results")

            cards = page.locator(".reusable-search__result-container, [class*='search-result__info']").all()
            print(f"  Found {len(cards)} LinkedIn profiles")

            for card in cards[:15]:
                try:
                    profile = {
                        "name":       "",
                        "title":      "",
                        "skills":     skill,
                        "location":   "",
                        "experience": "",
                        "available":  "Open to Work",
                        "url":        "",
                        "source":     "LinkedIn",
                        "scraped_at": datetime.now().isoformat(),
                    }

                    for sel in ["span[aria-hidden='true']", ".actor-name", "a span"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                profile["name"] = el.inner_text().strip()
                                break
                        except:
                            pass

                    for sel in [".subline-level-1", ".search-result__truncate", "p[class*='subtitle']"]:
                        try:
                            el = card.locator(sel).first
                            if el.count():
                                profile["title"] = el.inner_text().strip()
                                break
                        except:
                            pass

                    if profile["name"] and profile["name"] not in ["LinkedIn Member", ""]:
                        profiles.append(profile)
                        print(f"    ✓ {profile['name']:<30} | {profile['title'][:35]}")

                except Exception:
                    continue

        except Exception as e:
            print(f"  Error on LinkedIn: {e}")

        browser.close()

    return profiles


# ── Save ──────────────────────────────────────────────────────
def save_profiles(profiles, skill, location):
    fields = ["name", "title", "skills", "location", "experience",
              "available", "source", "url", "scraped_at"]

    with open(OUTPUT_JSON, "w") as f:
        json.dump({
            "skill": skill, "location": location,
            "total": len(profiles),
            "scraped_at": datetime.now().isoformat(),
            "profiles": profiles
        }, f, indent=2)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(profiles)

    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = skill.lower().replace(" ", "_")[:25]
    arch = os.path.join(ARCHIVE_DIR, f"{ts}_freelancers_{slug}.csv")
    with open(arch, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(profiles)

    print(f"\n  CSV     : {OUTPUT_CSV}  ← open in Excel")
    print(f"  JSON    : {OUTPUT_JSON}")
    print(f"  Archive : {arch}")


# ── Main ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Find people looking for web dev work")
    parser.add_argument("--skill",       default="Web Developer",  help="Skill/role to search")
    parser.add_argument("--location",    default="Bangalore",      help="City or Remote")
    parser.add_argument("--no-headless", action="store_true",      help="Show browser")
    parser.add_argument("--source",      default="all",
                        choices=["all", "internshala", "indeed", "linkedin"],
                        help="Which source to scrape (default: all)")
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print(f"  Freelancer Scraper — {args.skill} in {args.location}")
    print("=" * 65)
    print(f"  Sources: Internshala + Indeed + LinkedIn")
    print(f"  Looking for people SEEKING web development work")
    print("=" * 65)

    profiles = []
    headless = not args.no_headless

    if args.source in ("all", "internshala"):
        profiles = scrape_internshala(args.skill, args.location, headless, profiles)

    if args.source in ("all", "indeed"):
        profiles = scrape_indeed_candidates(args.skill, args.location, headless, profiles)

    if args.source in ("all", "linkedin"):
        profiles = scrape_linkedin_public(args.skill, args.location, headless, profiles)

    print("\n" + "=" * 65)
    print(f"  Total profiles found : {len(profiles)}")

    # Summary by source
    sources = {}
    for p in profiles:
        s = p.get("source", "Unknown")
        sources[s] = sources.get(s, 0) + 1
    for src, count in sources.items():
        print(f"    {src:<20} : {count} profiles")

    if profiles:
        save_profiles(profiles, args.skill, args.location)
        print(f"\n  Next: python3 merge_reports.py → open master_report.xlsx")
    else:
        print("\n  No profiles found.")
        print("  Tips:")
        print("  1. Run with --no-headless to see the browser")
        print("  2. Check freelancer_evidence/ folder for screenshots")
        print("  3. Try --source internshala  (most open to scraping)")
    print("=" * 65)


if __name__ == "__main__":
    main()
