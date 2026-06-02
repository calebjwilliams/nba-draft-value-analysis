# NBA Draft Pick Value Analysis

**Surplus Value and the Analytics Revolution: How NBA Draft Pick Pricing Changed Post-2010**

Sports Finance | Waseda Business School

---

## Research Question

How has the introduction of advanced analytics changed the distribution of surplus value across NBA draft positions?

Under the NBA rookie scale, all first-round picks generate surplus value — teams pay below-market rates and receive positive VORP across the board. Top picks (1–5) deliver the *most* value per dollar because the salary cap is most binding at the top. The key finding: the analytics era (post-2010) compressed this value curve, narrowing the gap between lottery picks and mid-first-rounders (interaction p = 0.024).

---

## Dashboard

```bash
uv run streamlit run dashboard/app.py
```

Opens at `http://localhost:8501`. Four tabs:
- **Value by Pick Bin** — VORP/WS/BPM per $1M by draft position and era
- **Pick # vs Value** — scatter with LOWESS trend lines, pre/post analytics
- **Era Convergence** — line chart + full regression results table
- **Player Lookup** — search any drafted player, view career value trajectory

---

## Data

| File | Contents |
|------|----------|
| `data/raw/draft_history.csv` | 1,418 picks, draft cohorts 1995–2018 (NBA API) |
| `data/raw/bbref_advanced_stats.csv` | VORP, WS, BPM, WS/48 per season 1996–2023 (Basketball Reference) |
| `data/raw/salaries.csv` | Player salaries 2001–2024 (ESPN) |
| `data/raw/nba_advanced_stats.csv` | NET_RATING, PIE, USG% per season (NBA API — robustness backup) |
| `data/processed/analysis_dataset.csv` | Merged, cleaned, 6,163 player-seasons with salary |
| `data/processed/regression_results.csv` | OLS results for models M1–M6 |
| `data/processed/summary_stats.csv` | Mean VORP/WS/BPM per $1M by pick bin × era |
| `data/processed/figures/` | Static charts (PNG, 150 dpi) |

---

## Reproducing the Analysis

```bash
# Install dependencies
uv sync

# Collect data (only needed once — takes ~20 min total)
uv run python scripts/01_collect_draft_and_stats.py   # ~3 min
uv run python scripts/02_collect_advanced_stats.py    # ~3 min (Playwright)
uv run python scripts/03_collect_salaries.py          # ~15 min (Playwright)

# Build analysis dataset
uv run python scripts/04_merge_and_clean.py

# Run regression + generate charts
uv run python scripts/05_analysis_and_regression.py

# Launch dashboard
uv run streamlit run dashboard/app.py
```

> **Note:** Scripts 02 and 03 use Playwright (headless Chromium) to scrape Basketball Reference and ESPN. Run `uv run playwright install chromium` if Chromium is not already installed.

---

## Key Results

| Pick Bin | Pre-Analytics VORP/$1M | Post-Analytics VORP/$1M |
|----------|----------------------|------------------------|
| Top 5 | 0.251 | 0.136 |
| Picks 6–14 | 0.192 | 0.146 |
| Picks 15–30 | 0.180 | 0.149 |
| Second Round | 0.132 | 0.125 |

OLS interaction term (pick × post-2010): **β = +0.0018, p = 0.024** — the value curve flattened significantly in the analytics era. Breakpoints at 2012 and 2014 are not significant, supporting 2010 as the structural break.

---

## Stack

- Python 3.14, managed by `uv`
- pandas, statsmodels, matplotlib, seaborn, plotly, streamlit
- Playwright (headless Chromium) for web scraping
- nba_api for official NBA stats
