"""
Collect NBA draft history (1995-2018) and advanced career stats via nba_api.
Outputs: data/raw/draft_history.csv, data/raw/player_stats.csv
"""

import time
import pandas as pd
from tqdm import tqdm
from nba_api.stats.endpoints import drafthistory, playercareerstats
from nba_api.stats.static import players

DRAFT_START = 1995
DRAFT_END = 2018
DELAY = 0.7  # seconds between API calls to avoid rate limiting

# ---------------------------------------------------------------------------
# 1. Draft history
# ---------------------------------------------------------------------------

def fetch_draft_history() -> pd.DataFrame:
    frames = []
    for year in tqdm(range(DRAFT_START, DRAFT_END + 1), desc="Draft years"):
        try:
            dh = drafthistory.DraftHistory(league_id="00", season_year_nullable=str(year))
            df = dh.get_data_frames()[0]
            df["DRAFT_YEAR"] = year
            frames.append(df)
        except Exception as e:
            print(f"  Error fetching {year}: {e}")
        time.sleep(DELAY)
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# 2. Advanced career stats (Win Shares, VORP, BPM live in per-season totals
#    from leaguedashplayerstats; career totals from playercareerstats)
# ---------------------------------------------------------------------------

def fetch_player_career_stats(player_ids: list[int]) -> pd.DataFrame:
    """
    Fetches per-season totals for each player. We get:
    - Regular season totals (MIN, GP, etc.) from playercareerstats SeasonTotalsRegularSeason
    Advanced metrics (WS, VORP, BPM) are on Basketball Reference, NOT in nba_api.
    We pull what we can here; advanced metrics come from the BBRef scraper (script 02).
    """
    frames = []
    for pid in tqdm(player_ids, desc="Player career stats"):
        try:
            cs = playercareerstats.PlayerCareerStats(
                player_id=pid,
                per_mode36="PerGame",
            )
            df = cs.get_data_frames()[0]  # SeasonTotalsRegularSeason
            df["PLAYER_ID"] = pid
            frames.append(df)
        except Exception as e:
            print(f"  Error for player {pid}: {e}")
        time.sleep(DELAY)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Step 1: Draft history ===")
    draft_df = fetch_draft_history()
    draft_df.to_csv("data/raw/draft_history.csv", index=False)
    print(f"  Saved {len(draft_df)} rows → data/raw/draft_history.csv")
    print(f"  Columns: {list(draft_df.columns)}")

    print("\n=== Step 2: Per-game career stats ===")
    # Only first two rounds; filter down further during cleaning
    player_ids = draft_df["PERSON_ID"].dropna().astype(int).unique().tolist()
    print(f"  Fetching stats for {len(player_ids)} players…")
    stats_df = fetch_player_career_stats(player_ids)
    stats_df.to_csv("data/raw/player_career_stats.csv", index=False)
    print(f"  Saved {len(stats_df)} rows → data/raw/player_career_stats.csv")
