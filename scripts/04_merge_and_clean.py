"""
Merge draft history + BBRef advanced stats + ESPN salary data.

Primary metrics: VORP, WS (from BBRef)
Robustness:     NET_RATING, PIE (from NBA API — nba_advanced_stats.csv)

Join strategy: normalized player name + season end year
(BBRef and ESPN both use season end year; draft history uses draft year)

Outputs:
  data/processed/master_dataset.csv    — all drafted-player seasons
  data/processed/analysis_dataset.csv — rows with salary data (for regression)
"""

import unicodedata
import pandas as pd
import numpy as np
from pathlib import Path

DRAFT_START  = 1995
DRAFT_END    = 2018
MIN_GP       = 20
MIN_MP_TOTAL = 200  # total minutes in season (BBRef MP column = total, not per game)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assign_pick_bin(pick) -> str:
    pick = int(pick)
    if pick <= 5:   return "Top 5"
    if pick <= 14:  return "Picks 6-14"
    if pick <= 30:  return "Picks 15-30"
    return "Second Round"

def assign_era(draft_year: int) -> str:
    return "Post-Analytics" if draft_year >= 2010 else "Pre-Analytics"

def normalize_name(name: str) -> str:
    name = str(name).strip().lower()
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    for suffix in [" jr.", " sr.", " iii", " ii", " iv"]:
        name = name.replace(suffix, "")
    return name.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # ------------------------------------------------------------------
    # Load raw files
    # ------------------------------------------------------------------
    draft    = pd.read_csv("data/raw/draft_history.csv")
    bbref    = pd.read_csv("data/raw/bbref_advanced_stats.csv")
    salaries = pd.read_csv("data/raw/salaries.csv")

    print(f"Draft rows:    {len(draft)}")
    print(f"BBRef rows:    {len(bbref)}")
    print(f"Salary rows:   {len(salaries)}")

    # ------------------------------------------------------------------
    # Clean draft data
    # ------------------------------------------------------------------
    # nba_api gives SEASON = draft year int; script 01 also added DRAFT_YEAR = same
    if "DRAFT_YEAR" in draft.columns and "SEASON" in draft.columns:
        draft = draft.drop(columns=["SEASON"])
    elif "SEASON" in draft.columns:
        draft = draft.rename(columns={"SEASON": "DRAFT_YEAR"})

    draft = draft[
        (draft["DRAFT_YEAR"].astype(int) >= DRAFT_START) &
        (draft["DRAFT_YEAR"].astype(int) <= DRAFT_END)
    ].copy()
    draft["OVERALL_PICK"] = pd.to_numeric(draft["OVERALL_PICK"], errors="coerce")
    draft = draft[draft["OVERALL_PICK"].notna()].copy()
    draft["name_key"] = draft["PLAYER_NAME"].apply(normalize_name)
    draft["pick_bin"] = draft["OVERALL_PICK"].apply(assign_pick_bin)
    draft["era"]      = draft["DRAFT_YEAR"].astype(int).apply(assign_era)
    print(f"\nDraft after filter: {len(draft)} picks ({DRAFT_START}–{DRAFT_END})")

    # ------------------------------------------------------------------
    # Clean BBRef advanced stats
    # ------------------------------------------------------------------
    bbref["name_key"] = bbref["Player"].apply(normalize_name)
    bbref["G"]  = pd.to_numeric(bbref["G"],  errors="coerce")
    bbref["MP"] = pd.to_numeric(bbref["MP"], errors="coerce")

    # Filter low-sample seasons
    bbref = bbref[(bbref["G"] >= MIN_GP) & (bbref["MP"] >= MIN_MP_TOTAL)].copy()

    # BBRef lists traded players once per team + once as "TOT" (total row)
    # Keep TOT if it exists, otherwise keep the row with most games played
    tot_rows   = bbref[bbref["Team"] == "TOT"]
    other_rows = bbref[bbref["Team"] != "TOT"]
    # For players NOT in TOT, keep the single row (or highest-GP if multiple teams)
    other_dedup = (
        other_rows
        .sort_values("G", ascending=False)
        .drop_duplicates(subset=["name_key", "SEASON_END_YEAR"], keep="first")
    )
    # Players in TOT: use TOT row; drop their individual team rows from other_dedup
    tot_keys = set(zip(tot_rows["name_key"], tot_rows["SEASON_END_YEAR"]))
    other_dedup = other_dedup[
        ~other_dedup.apply(lambda r: (r["name_key"], r["SEASON_END_YEAR"]) in tot_keys, axis=1)
    ]
    bbref = pd.concat([tot_rows, other_dedup], ignore_index=True)

    numeric_cols = ["PER", "WS", "WS/48", "OWS", "DWS", "BPM", "OBPM", "DBPM", "VORP", "TS%", "USG%"]
    for col in numeric_cols:
        if col in bbref.columns:
            bbref[col] = pd.to_numeric(bbref[col], errors="coerce")

    print(f"BBRef after filter: {len(bbref)} player-seasons")

    # ------------------------------------------------------------------
    # Clean salaries (ESPN)
    # ------------------------------------------------------------------
    # columns: player_name, team, salary_usd, season_end_year, season_label
    salaries["name_key"] = salaries["player_name"].apply(normalize_name)
    salaries = salaries[salaries["salary_usd"] > 0].copy()
    sal_seasons = f"{salaries['season_end_year'].min()}–{salaries['season_end_year'].max()}"
    print(f"Salaries: {len(salaries)} rows, {sal_seasons}")

    # ------------------------------------------------------------------
    # Merge: BBRef stats × draft metadata
    # ------------------------------------------------------------------
    draft_meta = draft[[
        "name_key", "PERSON_ID", "PLAYER_NAME", "DRAFT_YEAR", "OVERALL_PICK",
        "ROUND_NUMBER", "TEAM_CITY", "ORGANIZATION", "pick_bin", "era",
    ]].rename(columns={"TEAM_CITY": "DRAFT_TEAM"})

    merged = bbref.merge(draft_meta, on="name_key", how="inner")
    merged = merged[merged["SEASON_END_YEAR"] >= merged["DRAFT_YEAR"]].copy()
    merged["years_pro"] = merged["SEASON_END_YEAR"] - merged["DRAFT_YEAR"]

    print(f"\nAfter draft merge: {len(merged)} player-seasons, "
          f"{merged['name_key'].nunique()} unique players")

    # ------------------------------------------------------------------
    # Merge salaries
    # ------------------------------------------------------------------
    sal_keyed = salaries[["name_key", "season_end_year", "salary_usd", "season_label"]].rename(
        columns={"season_end_year": "SEASON_END_YEAR",
                 "salary_usd":      "SALARY_USD",
                 "season_label":    "SALARY_SEASON_LABEL"}
    )
    merged = merged.merge(sal_keyed, on=["name_key", "SEASON_END_YEAR"], how="left")

    salary_coverage = merged["SALARY_USD"].notna().mean()
    print(f"Salary coverage: {salary_coverage:.1%}")

    # ------------------------------------------------------------------
    # Derived metrics
    # ------------------------------------------------------------------
    sal_M = merged["SALARY_USD"] / 1_000_000
    merged["VORP_per_1M"] = merged["VORP"] / sal_M
    merged["WS_per_1M"]   = merged["WS"]   / sal_M

    # Winsorize at 1st/99th percentile (low salaries inflate ratios)
    for col in ["VORP_per_1M", "WS_per_1M"]:
        q01 = merged[col].quantile(0.01)
        q99 = merged[col].quantile(0.99)
        merged[col] = merged[col].clip(lower=q01, upper=q99)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    merged.to_csv("data/processed/master_dataset.csv", index=False)

    analysis = merged[merged["SALARY_USD"].notna()].copy()
    analysis.to_csv("data/processed/analysis_dataset.csv", index=False)

    print(f"\nAnalysis rows (with salary): {len(analysis)}")
    print(f"Unique players:              {analysis['name_key'].nunique()}")
    print(f"Draft years covered:         {sorted(analysis['DRAFT_YEAR'].unique())}")
    print(f"\nPick bin distribution:\n{analysis['pick_bin'].value_counts().to_string()}")
    print(f"\nEra distribution:\n{analysis['era'].value_counts().to_string()}")
    print("\nSaved:")
    print("  data/processed/master_dataset.csv")
    print("  data/processed/analysis_dataset.csv")
