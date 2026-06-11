"""
Core analysis:
  1. Summary stats: VORP per $1M by pick bin and era
  2. Charts: bar plots, scatter with LOWESS trend, era comparison line
  3. OLS regression: draft position → performance per dollar
  4. Pre/post analytics era comparison (interaction term)
  5. Sensitivity: alternative era breakpoints (2010, 2012, 2014)

Primary metric:   VORP_per_1M  (Value Over Replacement Player per $1M salary)
Robustness check: WS_per_1M    (Win Shares per $1M salary)
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
from pathlib import Path

FIGURES_DIR = Path("data/processed/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="colorblind")
PICK_BIN_ORDER = ["Top 5", "Picks 6-14", "Picks 15-30", "Second Round"]
ERA_COLORS     = {"Pre-Analytics": "#4878CF", "Post-Analytics": "#E07B39"}


def load_data() -> pd.DataFrame:
    df = pd.read_csv("data/processed/analysis_dataset.csv")
    df["pick_bin"] = pd.Categorical(df["pick_bin"], categories=PICK_BIN_ORDER, ordered=True)
    df["era"]      = pd.Categorical(df["era"], categories=["Pre-Analytics", "Post-Analytics"])
    return df


# ---------------------------------------------------------------------------
# 1. Summary statistics
# ---------------------------------------------------------------------------

def compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["pick_bin", "era"], observed=True)
        .agg(
            n_player_seasons  =("VORP_per_1M", "count"),
            VORP_per_1M_mean  =("VORP_per_1M", "mean"),
            VORP_per_1M_med   =("VORP_per_1M", "median"),
            VORP_per_1M_std   =("VORP_per_1M", "std"),
            WS_per_1M_mean    =("WS_per_1M",   "mean"),
            WS_per_1M_med     =("WS_per_1M",   "median"),
            avg_salary_M      =("SALARY_USD",   lambda x: x.mean() / 1e6),
            avg_VORP          =("VORP",         "mean"),
            avg_WS            =("WS",           "mean"),
            avg_BPM           =("BPM",          "mean"),
            bust_rate         =("VORP",         lambda x: (x < 0).mean()),
        )
        .reset_index()
    )
    # Sharpe analog: mean return / std dev (higher = better risk-adjusted return)
    summary["sharpe_analog"] = summary["VORP_per_1M_mean"] / summary["VORP_per_1M_std"]
    return summary


# ---------------------------------------------------------------------------
# 2. Charts
# ---------------------------------------------------------------------------

def plot_performance_per_dollar(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, metric, label in [
        (axes[0], "VORP_per_1M", "VORP per $1M Salary"),
        (axes[1], "WS_per_1M",   "Win Shares per $1M Salary"),
    ]:
        sns.barplot(
            data=df, x="pick_bin", y=metric, hue="era",
            order=PICK_BIN_ORDER, palette=ERA_COLORS,
            ax=ax, errorbar="ci", capsize=0.05,
        )
        ax.set_title(label, fontsize=12, fontweight="bold")
        ax.set_xlabel("Draft Position Bin")
        ax.set_ylabel(label)
        ax.tick_params(axis="x", rotation=15)
        ax.legend(title="Era")

    fig.suptitle(
        "NBA Draft Pick Value: Performance per $1M Salary\nby Position Bin and Analytics Era",
        fontsize=14, fontweight="bold", y=1.02,
    )
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig1_performance_per_dollar.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved fig1_performance_per_dollar.png")


def plot_pick_vs_vorp_scatter(df: pd.DataFrame):
    from statsmodels.nonparametric.smoothers_lowess import lowess

    fig, ax = plt.subplots(figsize=(12, 6))
    for era, color in ERA_COLORS.items():
        sub = df[df["era"] == era]
        ax.scatter(sub["OVERALL_PICK"], sub["VORP_per_1M"],
                   alpha=0.25, s=10, color=color, label=era)
        if len(sub) > 20:
            smooth = lowess(sub["VORP_per_1M"], sub["OVERALL_PICK"], frac=0.3)
            ax.plot(smooth[:, 0], smooth[:, 1], color=color, linewidth=2.5)

    ax.axvline(5.5,  color="gray", linestyle="--", alpha=0.5, label="Top-5 boundary")
    ax.axvline(14.5, color="gray", linestyle=":",  alpha=0.5, label="Mid-first boundary")
    ax.set_xlabel("Overall Draft Pick", fontsize=11)
    ax.set_ylabel("VORP per $1M Salary", fontsize=11)
    ax.set_title("Draft Pick Value vs. Position: Pre vs. Post Analytics Era",
                 fontweight="bold", fontsize=13)
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig2_pick_vs_vorp_scatter.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved fig2_pick_vs_vorp_scatter.png")


def plot_era_comparison_line(df: pd.DataFrame):
    summary = df.groupby(["pick_bin", "era"], observed=True)["VORP_per_1M"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(9, 5))
    for era, color in ERA_COLORS.items():
        sub = summary[summary["era"] == era]
        ax.plot(sub["pick_bin"].astype(str), sub["VORP_per_1M"],
                marker="o", color=color, label=era, linewidth=2, markersize=8)

    ax.set_xlabel("Draft Position Bin", fontsize=11)
    ax.set_ylabel("Mean VORP per $1M", fontsize=11)
    ax.set_title("Did the Analytics Era Flatten the Draft Value Curve?",
                 fontweight="bold", fontsize=13)
    ax.legend(title="Era")
    ax.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig3_era_comparison_line.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved fig3_era_comparison_line.png")


def plot_risk_return(summary: pd.DataFrame):
    """
    Risk-return scatter: each point is a pick bin * era combination.
    X = std dev of VORP/dollar (risk), Y = mean VORP/dollar (return).
    Analogous to a mean-variance plot in portfolio theory.
    """
    fig, ax = plt.subplots(figsize=(9, 6))

    markers = {"Pre-Analytics": "o", "Post-Analytics": "s"}
    for _, row in summary.iterrows():
        color  = ERA_COLORS[row["era"]]
        marker = markers[row["era"]]
        ax.scatter(row["VORP_per_1M_std"], row["VORP_per_1M_mean"],
                   color=color, marker=marker, s=180, zorder=3)
        ax.annotate(
            f"{row['pick_bin']}\n({row['era'][:4]})",
            (row["VORP_per_1M_std"], row["VORP_per_1M_mean"]),
            textcoords="offset points", xytext=(8, 4), fontsize=8,
        )

    # Legend proxies
    for era, color in ERA_COLORS.items():
        ax.scatter([], [], color=color, marker=markers[era], label=era, s=100)

    ax.set_xlabel("Risk — Std Dev of VORP per $1M", fontsize=11)
    ax.set_ylabel("Return — Mean VORP per $1M", fontsize=11)
    ax.set_title("Risk-Return Profile of NBA Draft Pick Bins\n(Mean-Variance Framework)",
                 fontweight="bold", fontsize=13)
    ax.legend(title="Era")
    ax.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig4_risk_return.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved fig4_risk_return.png")


# ---------------------------------------------------------------------------
# 3. OLS regression
# ---------------------------------------------------------------------------

def run_regressions(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["post_analytics"] = (df["era"] == "Post-Analytics").astype(int)
    df["log_pick"]       = np.log(df["OVERALL_PICK"])

    # BPM is a pure rate stat (per 100 possessions) — unaffected by games missed.
    # BPM_per_1M robustness check addresses the injury availability concern:
    # if results hold with BPM, the injury channel is not driving VORP findings.
    df["BPM_per_1M"] = df["BPM"] / (df["SALARY_USD"] / 1_000_000)
    # Winsorize BPM_per_1M same as other metrics
    q01, q99 = df["BPM_per_1M"].quantile(0.01), df["BPM_per_1M"].quantile(0.99)
    df["BPM_per_1M"] = df["BPM_per_1M"].clip(lower=q01, upper=q99)

    models = {
        "M1_baseline":    smf.ols("VORP_per_1M ~ OVERALL_PICK", data=df),
        "M2_era":         smf.ols("VORP_per_1M ~ OVERALL_PICK + post_analytics", data=df),
        "M3_interaction": smf.ols("VORP_per_1M ~ OVERALL_PICK * post_analytics", data=df),
        "M4_log_pick":    smf.ols("VORP_per_1M ~ log_pick * post_analytics", data=df),
        "M5_WS_robust":   smf.ols("WS_per_1M   ~ OVERALL_PICK * post_analytics", data=df),
        "M6_BPM_injury":  smf.ols("BPM_per_1M  ~ OVERALL_PICK * post_analytics", data=df),
    }
    results = {name: m.fit(cov_type="HC3") for name, m in models.items()}

    rows = []
    for name, res in results.items():
        rows.append({
            "model":         name,
            "n":             int(res.nobs),
            "r2":            round(res.rsquared, 4),
            "r2_adj":        round(res.rsquared_adj, 4),
            "coef_pick":     round(res.params.get("OVERALL_PICK", np.nan), 5),
            "pval_pick":     round(res.pvalues.get("OVERALL_PICK", np.nan), 4),
            "coef_post":     round(res.params.get("post_analytics", np.nan), 5),
            "pval_post":     round(res.pvalues.get("post_analytics", np.nan), 4),
            "coef_interact": round(res.params.get("OVERALL_PICK:post_analytics", np.nan), 6),
            "pval_interact": round(res.pvalues.get("OVERALL_PICK:post_analytics", np.nan), 4),
        })

    pd.DataFrame(rows).to_csv("data/processed/regression_results.csv", index=False)

    print("\n=== Model 3 (main): VORP/1M ~ Pick × Era ===")
    print(results["M3_interaction"].summary2())

    # Cluster standard errors by player to account for repeated observations
    # (same player appears across multiple seasons — HC3 treats them as independent)
    m3_clustered = smf.ols("VORP_per_1M ~ OVERALL_PICK * post_analytics", data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df["name_key"]}
    )
    interact_coef = m3_clustered.params.get("OVERALL_PICK:post_analytics", np.nan)
    interact_pval = m3_clustered.pvalues.get("OVERALL_PICK:post_analytics", np.nan)
    print("\n=== M3 with Player-Clustered Standard Errors ===")
    print(f"  Interaction coef : {interact_coef:.6f}")
    print(f"  p-value (HC3)    : {results['M3_interaction'].pvalues.get('OVERALL_PICK:post_analytics', np.nan):.4f}")
    print(f"  p-value (cluster): {interact_pval:.4f}")

    return results


# ---------------------------------------------------------------------------
# 4. Player-level collapse + OLS
# ---------------------------------------------------------------------------

def collapse_to_player_level(df: pd.DataFrame, max_years: int = 4) -> pd.DataFrame:
    """Collapse to one row per player using cumulative VORP / total salary
    over the rookie contract window (years_pro <= max_years).

    Cumulative rather than average captures total value delivered at the
    fixed CBA price — the right measure for surplus value under the rookie scale.

    Pass max_years=None to use full career (robustness / extension check).
    """
    d = df.copy()
    if max_years is not None:
        d = d[d["years_pro"] <= max_years]

    # Cumulative VORP and total salary per player over the window
    agg = (
        d.groupby("name_key", observed=True)
        .agg(
            PLAYER_NAME  =("PLAYER_NAME",  "first"),
            OVERALL_PICK =("OVERALL_PICK", "first"),
            pick_bin     =("pick_bin",      "first"),
            era          =("era",           "first"),
            DRAFT_YEAR   =("DRAFT_YEAR",    "first"),
            ROUND_NUMBER =("ROUND_NUMBER",  "first"),
            n_seasons    =("VORP",          "count"),
            total_VORP   =("VORP",          "sum"),
            total_WS     =("WS",            "sum"),
            total_salary =("SALARY_USD",    "sum"),
        )
        .reset_index()
    )

    # Cumulative value per $1M total salary paid over the window
    total_salary_1M = agg["total_salary"] / 1_000_000
    agg["VORP_per_1M"] = agg["total_VORP"] / total_salary_1M
    agg["WS_per_1M"]   = agg["total_WS"]   / total_salary_1M

    # Winsorize at 1st / 99th percentile
    for col in ["VORP_per_1M", "WS_per_1M"]:
        q01, q99 = agg[col].quantile(0.01), agg[col].quantile(0.99)
        agg[col] = agg[col].clip(lower=q01, upper=q99)

    agg["post_analytics"] = (agg["era"] == "Post-Analytics").astype(int)
    agg["log_pick"]       = np.log(agg["OVERALL_PICK"])
    return agg


def run_player_level_regressions(player_df: pd.DataFrame) -> dict:
    """OLS on player-level data — each observation is one player's career average."""
    models = {
        "P1_baseline":    smf.ols("VORP_per_1M ~ OVERALL_PICK", data=player_df),
        "P2_era":         smf.ols("VORP_per_1M ~ OVERALL_PICK + post_analytics", data=player_df),
        "P3_interaction": smf.ols("VORP_per_1M ~ OVERALL_PICK * post_analytics", data=player_df),
        "P4_log_pick":    smf.ols("VORP_per_1M ~ log_pick * post_analytics", data=player_df),
        "P5_WS":          smf.ols("WS_per_1M   ~ OVERALL_PICK * post_analytics", data=player_df),
    }
    results = {name: m.fit(cov_type="HC3") for name, m in models.items()}

    # Pick / interaction terms differ by model spec (P4 uses log_pick, not OVERALL_PICK)
    pick_terms     = {"P1_baseline": "OVERALL_PICK", "P2_era": "OVERALL_PICK",
                      "P3_interaction": "OVERALL_PICK", "P5_WS": "OVERALL_PICK"}
    interact_terms = {"P3_interaction": "OVERALL_PICK:post_analytics",
                      "P4_log_pick": "log_pick:post_analytics",
                      "P5_WS": "OVERALL_PICK:post_analytics"}

    rows = []
    for name, res in results.items():
        pick_term  = pick_terms.get(name)
        inter_term = interact_terms.get(name)
        rows.append({
            "model":         name,
            "n":             int(res.nobs),
            "r2":            round(res.rsquared, 4),
            "coef_pick":     round(res.params.get(pick_term, np.nan), 5) if pick_term else np.nan,
            "pval_pick":     round(res.pvalues.get(pick_term, np.nan), 4) if pick_term else np.nan,
            "coef_post":     round(res.params.get("post_analytics", np.nan), 4),
            "pval_post":     round(res.pvalues.get("post_analytics", np.nan), 4),
            "coef_interact": round(res.params.get(inter_term, np.nan), 6) if inter_term else np.nan,
            "pval_interact": round(res.pvalues.get(inter_term, np.nan), 4) if inter_term else np.nan,
        })

    reg_df = pd.DataFrame(rows)
    reg_df.to_csv("data/processed/regression_results_player_level.csv", index=False)

    print("\n=== Player-Level OLS (N = one row per player) ===")
    print(reg_df.to_string(index=False))
    print("\n=== P3 detail (main interaction, player-level) ===")
    print(results["P3_interaction"].summary2())
    return results


def run_check1_nseasons(player_df: pd.DataFrame) -> pd.DataFrame:
    """Check 1: add n_seasons (rookie-window data coverage) as a control to P3.
    Tests whether the P3 interaction is an artifact of differential
    rookie-window completeness across eras (Section 5.4)."""
    res = smf.ols(
        "VORP_per_1M ~ OVERALL_PICK * post_analytics + n_seasons", data=player_df
    ).fit(cov_type="HC3")

    row = {
        "model":         "P3_check1_nseasons",
        "n":             int(res.nobs),
        "r2":            round(res.rsquared, 4),
        "coef_interact": round(res.params.get("OVERALL_PICK:post_analytics", np.nan), 4),
        "pval_interact": round(res.pvalues.get("OVERALL_PICK:post_analytics", np.nan), 4),
        "coef_nseasons": round(res.params.get("n_seasons", np.nan), 4),
        "pval_nseasons": round(res.pvalues.get("n_seasons", np.nan), 4),
    }
    out = pd.DataFrame([row])
    out.to_csv("data/processed/regression_results_check1_nseasons.csv", index=False)

    print("\n=== Check 1: P3 + n_seasons control ===")
    print(out.to_string(index=False))
    return out


# ---------------------------------------------------------------------------
# 5. Quantile regression (player-level)
# ---------------------------------------------------------------------------

def run_quantile_regression(player_df: pd.DataFrame):
    """Quantile regression at 25th, 50th, 75th percentiles.
    Tests whether the pick effect is consistent across the distribution
    or driven by stars at the top."""
    quantiles = [0.25, 0.50, 0.75]
    rows = []
    for q in quantiles:
        res = smf.quantreg(
            "VORP_per_1M ~ OVERALL_PICK * post_analytics", data=player_df
        ).fit(q=q)
        rows.append({
            "quantile":      q,
            "n":             int(res.nobs),
            "coef_pick":     round(res.params.get("OVERALL_PICK", np.nan), 5),
            "pval_pick":     round(res.pvalues.get("OVERALL_PICK", np.nan), 4),
            "coef_interact": round(res.params.get("OVERALL_PICK:post_analytics", np.nan), 6),
            "pval_interact": round(res.pvalues.get("OVERALL_PICK:post_analytics", np.nan), 4),
        })

    qr_df = pd.DataFrame(rows)
    qr_df.to_csv("data/processed/regression_results_quantile.csv", index=False)

    print("\n=== Quantile Regression (player-level, 25th / 50th / 75th pct) ===")
    print(qr_df.to_string(index=False))
    return qr_df


# ---------------------------------------------------------------------------
# 6. Bin dummy × era interaction (player-level)
# ---------------------------------------------------------------------------

def run_bin_interaction_regression(
    player_df: pd.DataFrame,
    output_path: str = "data/processed/regression_results_bin_interaction.csv",
):
    """Use pick bins as dummies instead of continuous pick number.
    Top 5 is the reference category. Interaction terms directly test
    whether each bin's gap relative to Top 5 shrank post-2010."""
    df = player_df.copy()

    # Ensure Top 5 is the reference category
    bin_order = ["Top 5", "Picks 6-14", "Picks 15-30", "Second Round"]
    df["pick_bin"] = pd.Categorical(df["pick_bin"], categories=bin_order, ordered=False)

    res = smf.ols(
        "VORP_per_1M ~ C(pick_bin, Treatment('Top 5')) * post_analytics",
        data=df
    ).fit(cov_type="HC3")

    print("\n=== Bin Dummy × Era Interaction (player-level, Top 5 = reference) ===")
    print(res.summary2())

    # Extract key interaction terms cleanly
    rows = []
    for bin_label in ["Picks 6-14", "Picks 15-30", "Second Round"]:
        base_key    = f"C(pick_bin, Treatment('Top 5'))[T.{bin_label}]"
        inter_key   = f"C(pick_bin, Treatment('Top 5'))[T.{bin_label}]:post_analytics"
        rows.append({
            "bin":             bin_label,
            "gap_pre":         round(res.params.get(base_key, np.nan), 4),
            "gap_pre_pval":    round(res.pvalues.get(base_key, np.nan), 4),
            "gap_change_post": round(res.params.get(inter_key, np.nan), 4),
            "gap_change_pval": round(res.pvalues.get(inter_key, np.nan), 4),
        })

    summary = pd.DataFrame(rows)
    summary.to_csv(output_path, index=False)
    print("\n=== Key: Gap vs Top 5 and whether it shrank post-2010 ===")
    print("(gap_pre = how much worse than Top 5 pre-analytics; gap_change_post = did that gap shrink?)")
    print(summary.to_string(index=False))
    return res


# ---------------------------------------------------------------------------
# 7. Sensitivity: alternative era breakpoints
# ---------------------------------------------------------------------------

def sensitivity_era_breakpoints_full(df: pd.DataFrame):
    """Original approach: full dataset, breakpoint shifts post dummy only."""
    rows = []
    for bp in [2006, 2008, 2010, 2012, 2014]:
        df_s = df.copy()
        df_s["post_analytics"] = (df_s["DRAFT_YEAR"] >= bp).astype(int)
        res = smf.ols(
            "VORP_per_1M ~ OVERALL_PICK * post_analytics", data=df_s
        ).fit(cov_type="HC3")
        rows.append({
            "breakpoint":       bp,
            "n":                int(res.nobs),
            "r2":               round(res.rsquared, 4),
            "interaction_coef": round(res.params.get("OVERALL_PICK:post_analytics", np.nan), 6),
            "interaction_pval": round(res.pvalues.get("OVERALL_PICK:post_analytics", np.nan), 4),
        })

    sens = pd.DataFrame(rows)
    print("\n=== Sensitivity: Era Breakpoints (full dataset, original) ===")
    print(sens.to_string(index=False))
    return sens


def sensitivity_era_breakpoints(df: pd.DataFrame, window: int = 5):
    """Symmetric window approach: use ±window years around each breakpoint
    so pre/post sample sizes are balanced and p-values are comparable."""
    rows = []
    for bp in [2006, 2008, 2010, 2012, 2014]:
        pre_years  = range(bp - window, bp)
        post_years = range(bp, bp + window)
        df_s = df[df["DRAFT_YEAR"].isin(list(pre_years) + list(post_years))].copy()
        df_s["post_analytics"] = (df_s["DRAFT_YEAR"] >= bp).astype(int)
        if df_s["post_analytics"].nunique() < 2:
            continue
        res = smf.ols(
            "VORP_per_1M ~ OVERALL_PICK * post_analytics", data=df_s
        ).fit(cov_type="HC3")
        rows.append({
            "breakpoint":       bp,
            "window":           f"{bp - window}–{bp + window - 1}",
            "n":                int(res.nobs),
            "r2":               round(res.rsquared, 4),
            "interaction_coef": round(res.params.get("OVERALL_PICK:post_analytics", np.nan), 6),
            "interaction_pval": round(res.pvalues.get("OVERALL_PICK:post_analytics", np.nan), 4),
        })

    sens = pd.DataFrame(rows)
    sens.to_csv("data/processed/sensitivity_breakpoints.csv", index=False)
    print(f"\n=== Sensitivity: Era Breakpoints (symmetric ±{window}-year window) ===")
    print(sens.to_string(index=False))
    return sens


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Loading data…")
    df = load_data()
    print(f"  {len(df)} player-seasons, {df['name_key'].nunique()} unique players")

    print("\n=== Summary Statistics ===")
    summary = compute_summary(df)
    summary.to_csv("data/processed/summary_stats.csv", index=False)
    print(summary.to_string(index=False))

    print("\n=== Generating Charts ===")
    plot_performance_per_dollar(df)
    plot_pick_vs_vorp_scatter(df)
    plot_era_comparison_line(df)
    plot_risk_return(summary)

    print("\n=== OLS Regression (season-level, original) ===")
    run_regressions(df)

    print("\n=== Player-Level Analysis: Rookie Contract (years 1-4) ===")
    player_df = collapse_to_player_level(df, max_years=4)
    print(f"  {len(player_df)} unique players")
    run_player_level_regressions(player_df)
    run_quantile_regression(player_df)
    run_bin_interaction_regression(player_df)
    run_check1_nseasons(player_df)

    print("\n=== Player-Level Analysis: Full Career (robustness / extension) ===")
    player_df_career = collapse_to_player_level(df, max_years=None)
    print(f"  {len(player_df_career)} unique players")
    run_bin_interaction_regression(
        player_df_career,
        output_path="data/processed/regression_results_bin_interaction_fullcareer.csv",
    )

    print("\n=== Sensitivity Analysis ===")
    sensitivity_era_breakpoints_full(df)
    sensitivity_era_breakpoints(df)

    print("\nDone. All outputs in data/processed/")
