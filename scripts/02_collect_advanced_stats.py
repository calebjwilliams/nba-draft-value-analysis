"""
Scrape per-season advanced stats (VORP, WS, BPM, WS/48, PER) from Basketball Reference
using Playwright to bypass Cloudflare protection.

URL pattern: https://www.basketball-reference.com/leagues/NBA_{year}_advanced.html
Table id: #advanced

Outputs: data/raw/bbref_advanced_stats.csv
"""

import time
from io import StringIO
from pathlib import Path

import pandas as pd
from tqdm import tqdm
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

SEASONS = range(1997, 2024)  # end year: 1997 = 1996-97, covers all draft cohorts through 2023
DELAY   = 3.0  # seconds between pages — be polite to BBRef

COLS_KEEP = [
    "Player", "Age", "Team", "Pos", "G", "MP",
    "PER", "WS", "WS/48", "OWS", "DWS",
    "BPM", "OBPM", "DBPM", "VORP",
    "TS%", "USG%",
]


def scrape_season(page, year: int) -> pd.DataFrame | None:
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_advanced.html"
    try:
        page.goto(url, timeout=30_000, wait_until="domcontentloaded")
        page.wait_for_selector("table#advanced", timeout=15_000)
        time.sleep(1.5)
    except PWTimeout:
        print(f"  Timeout on {year}")
        return None

    try:
        tables = pd.read_html(StringIO(page.content()), attrs={"id": "advanced"})
        df = tables[0].copy()
    except Exception as e:
        print(f"  Parse error {year}: {e}")
        return None

    # Drop repeated header rows BBRef embeds mid-table
    df = df[df["Player"] != "Player"].copy()
    if df.empty:
        return None

    # Numeric coercion
    for col in df.columns:
        if col not in ("Player", "Team", "Pos", "Awards"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["SEASON_END_YEAR"] = year
    df["SEASON_LABEL"]    = f"{year - 1}-{str(year)[2:]}"

    keep = [c for c in COLS_KEEP if c in df.columns] + ["SEASON_END_YEAR", "SEASON_LABEL"]
    return df[keep]


if __name__ == "__main__":
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    frames = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        for year in tqdm(SEASONS, desc="BBRef advanced seasons"):
            df = scrape_season(page, year)
            if df is not None:
                frames.append(df)
            time.sleep(DELAY)

        browser.close()

    if frames:
        result = pd.concat(frames, ignore_index=True)
        result.to_csv("data/raw/bbref_advanced_stats.csv", index=False)
        print(f"\nSaved {len(result)} rows → data/raw/bbref_advanced_stats.csv")
        print(f"Seasons: {result['SEASON_END_YEAR'].min()}–{result['SEASON_END_YEAR'].max()}")
        print(f"Sample:\n{result[['Player','SEASON_LABEL','WS','VORP','BPM']].head(3).to_string()}")
    else:
        print("No data collected.")
