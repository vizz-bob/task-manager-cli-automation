#!/usr/bin/env python3
"""
Step 5 — Playwright browser automation.

Opens https://jsonplaceholder.typicode.com in a headless browser,
takes a screenshot, extracts the heading text, and saves everything to disk.

Setup:
    pip install playwright
    playwright install chromium

Usage:
    python3 step5_playwright.py
    python3 step5_playwright.py --screenshot my_screenshot.png
    python3 step5_playwright.py --no-headless   (shows browser window)
"""

import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
except ImportError:
    print("Error: 'playwright' is not installed.")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)


TARGET_URL = "https://jsonplaceholder.typicode.com"
DEFAULT_SCREENSHOT = "screenshot_jsonplaceholder.png"
RESULTS_FILE = "step5_results.json"


def run_automation(headless: bool, screenshot_path: str):
    """Main Playwright automation routine."""
    results = {
        "url": TARGET_URL,
        "timestamp": datetime.now().isoformat(),
        "headless": headless,
        "screenshot": screenshot_path,
        "headings": [],
        "page_title": "",
        "status": "pending",
        "error": None
    }

    print("\n" + "=" * 60)
    print("  Step 5 — Playwright Browser Automation")
    print("=" * 60)
    print(f"  Target URL  : {TARGET_URL}")
    print(f"  Headless    : {headless}")
    print(f"  Screenshot  : {screenshot_path}")
    print("-" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) TaskManagerBot/1.0"
        )
        page = context.new_page()

        try:
            # ── Navigate ───────────────────────────────────────────────────
            print(f"\n  [1/4] Navigating to {TARGET_URL} ...")
            response = page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            print(f"        HTTP Status: {response.status}")

            # ── Wait for content ───────────────────────────────────────────
            page.wait_for_selector("h1, h2, h3", timeout=10000)

            # ── Extract page title ─────────────────────────────────────────
            print("  [2/4] Extracting page title and headings ...")
            results["page_title"] = page.title()
            print(f"        Page title: {results['page_title']}")

            # Extract all heading text
            for tag in ["h1", "h2", "h3"]:
                elements = page.locator(tag).all()
                for el in elements:
                    text = el.inner_text().strip()
                    if text:
                        results["headings"].append({"tag": tag, "text": text})
                        print(f"        <{tag}>: {text}")

            # ── Take screenshot ────────────────────────────────────────────
            print(f"  [3/4] Taking screenshot → {screenshot_path} ...")
            page.screenshot(path=screenshot_path, full_page=True)
            screenshot_size = Path(screenshot_path).stat().st_size
            print(f"        Saved ({screenshot_size:,} bytes)")

            # ── Save results ───────────────────────────────────────────────
            print(f"  [4/4] Saving results → {RESULTS_FILE} ...")
            results["status"] = "success"
            with open(RESULTS_FILE, "w") as f:
                json.dump(results, f, indent=2)
            print(f"        Done.")

        except PWTimeoutError as e:
            results["status"] = "error"
            results["error"] = f"Timeout: {str(e)}"
            print(f"\n  ERROR: Page timed out — {e}")
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            print(f"\n  ERROR: {e}")
            raise
        finally:
            browser.close()

    print("\n" + "=" * 60)
    print(f"  Status    : {results['status'].upper()}")
    print(f"  Headings  : {len(results['headings'])} found")
    print(f"  Screenshot: {screenshot_path}")
    print(f"  Results   : {RESULTS_FILE}")
    print("=" * 60 + "\n")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Playwright automation: screenshot + heading extraction."
    )
    parser.add_argument(
        "--screenshot",
        default=DEFAULT_SCREENSHOT,
        help=f"Output screenshot path (default: {DEFAULT_SCREENSHOT})"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show the browser window (default: headless)"
    )
    args = parser.parse_args()

    run_automation(
        headless=not args.no_headless,
        screenshot_path=args.screenshot
    )


if __name__ == "__main__":
    main()
