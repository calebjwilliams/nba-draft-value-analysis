"""
Scrape historical NBA salary data from ESPN using Playwright (JS-rendered pages).
URL pattern: https://www.espn.com/nba/salaries/_/year/{year}/page/{page}/seasontype/3

Covers seasons 2001-2024 (end year).
Outputs: data/raw/salaries.csv
"""

import time
import pandas as pd
from io import StringIO
from tqdm import tqdm
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

SEASONS = list(range(2001, 2025))  # end year; 2001 = 2000-01 season
MAX_PAGES = 15
PAGE_TIMEOUT = 15_000  # ms


def parse_salary(val) -> float | None:
    s = str(val).replace("$", "").replace(",", "").strip()
    try:
        v = float(s)
        return v if v > 0 else None
    except ValueError:
        return None


def scrape_season(page, year: int) -> pd.DataFrame:
    frames = []
    for p in range(1, MAX_PAGES + 1):
        url = f"https://www.espn.com/nba/salaries/_/year/{year}/page/{p}/seasontype/3"
        try:
            page.goto(url, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
            page.wait_for_selector("table", timeout=10_000)
            time.sleep(2)  # let JS fully render table rows
        except PWTimeout:
            break  # no more pages for this season

        try:
            tables = pd.read_html(StringIO(page.content()))
        except Exception as e:
            print(f"    parse error {url}: {e}")
            break

        if not tables:
            break

        df = tables[0].copy()
        if df.empty or len(df.columns) < 4:
            break

        # ESPN returns integer column names; first data row may be the header
        df.columns = range(len(df.columns))
        df = df.rename(columns={0: "rank", 1: "name", 2: "team", 3: "salary"})
        # Drop embedded header rows (where rank == "RK")
        df = df[df["rank"].apply(lambda x: str(x).strip().isdigit())].copy()
        if df.empty:
            break

        df["salary_usd"] = df["salary"].apply(parse_salary)
        df = df[df["salary_usd"].notna()].copy()
        df["player_name"] = df["name"].str.split(",").str[0].str.strip()
        frames.append(df[["player_name", "team", "salary_usd"]])
        time.sleep(0.5)

    if not frames:
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    result["season_end_year"] = year
    result["season_label"] = f"{year - 1}-{str(year)[2:]}"
    return result


if __name__ == "__main__":
    all_frames = []

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

        for year in tqdm(SEASONS, desc="ESPN salary seasons"):
            df = scrape_season(page, year)
            if not df.empty:
                all_frames.append(df)
                print(f"  {year - 1}-{str(year)[2:]}: {len(df)} players")
            else:
                print(f"  {year}: no data")

        browser.close()

    if all_frames:
        result = pd.concat(all_frames, ignore_index=True)
        result.to_csv("data/raw/salaries.csv", index=False)
        print(f"\nSaved {len(result)} rows → data/raw/salaries.csv")
        print(result.head())
    else:
        print("No salary data collected.")
