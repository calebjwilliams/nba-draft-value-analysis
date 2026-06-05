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
    return results


# ---------------------------------------------------------------------------
# 4. Sensitivity: alternative era breakpoints
# ---------------------------------------------------------------------------

def sensitivity_era_breakpoints(df: pd.DataFrame):
    rows = []
    for bp in [2010, 2012, 2014]:
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
    sens.to_csv("data/processed/sensitivity_breakpoints.csv", index=False)
    print("\n=== Sensitivity: Era Breakpoints ===")
    print(sens.to_string(index=False))


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

    print("\n=== OLS Regression ===")
    run_regressions(df)

    print("\n=== Sensitivity Analysis ===")
    sensitivity_era_breakpoints(df)

    print("\nDone. All outputs in data/processed/")
