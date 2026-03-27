# How to Get a Free Google API Key

You need this to fetch company data from Google Maps / Places.
**Free tier: $200 credit/month — enough for ~10,000 searches.**

---

## Step 1 — Go to Google Cloud Console

Open: https://console.cloud.google.com

Sign in with your Google account.

---

## Step 2 — Create a Project

1. Click the project dropdown at the top (next to "Google Cloud")
2. Click **"New Project"**
3. Name it: `bangalore-ads-tracker`
4. Click **Create**

---

## Step 3 — Enable the Places API

1. In the left menu go to: **APIs & Services → Library**
2. Search for **"Places API"**
3. Click it → Click **Enable**

---

## Step 4 — Create an API Key

1. Go to: **APIs & Services → Credentials**
2. Click **"+ Create Credentials" → API Key**
3. Your key will appear — copy it (looks like: `AIzaSyD...`)

---

## Step 5 — Restrict the Key (Recommended)

1. Click on your new API key
2. Under **"API restrictions"** → select **"Restrict key"**
3. Choose: **Places API**
4. Click **Save**

---

## Step 6 — Use the Key

**Option A — Set as environment variable (recommended):**
```bash
export GOOGLE_API_KEY="AIzaSyD_your_key_here"
python3 bangalore_ads_fetch.py
```

**Option B — The script will ask you to paste it when you run it.**

---

## Cost & Free Tier

| API Call | Cost | Free tier |
|----------|------|-----------|
| Text Search | $0.032 per call | ~6,000 free/month |
| Place Details | $0.017 per call | ~11,000 free/month |

Fetching 20 companies = ~20 Text Search + 20 Details = ~$1.00
**Well within the $200/month free credit.**

---

## Run the Scripts

```bash
# Step 1: Fetch companies
python3 bangalore_ads_fetch.py --category "advertising agency in Bangalore" --max 20

# Step 2: Generate report + CSV
python3 bangalore_ads_report.py

# Step 3: Filter only top rated
python3 bangalore_ads_report.py --min-rating 4.0 --output top_companies.csv

# Step 4: Try different categories
python3 bangalore_ads_fetch.py --category "digital marketing company in Bangalore"
python3 bangalore_ads_fetch.py --category "social media marketing Bangalore"
python3 bangalore_ads_fetch.py --category "SEO company Bangalore"
```
