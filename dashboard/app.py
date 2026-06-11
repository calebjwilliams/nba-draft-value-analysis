import unicodedata
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

st.set_page_config(
    page_title="NBA Draft Pick Value",
    page_icon="🏀",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

@st.cache_data
def load_data():
    df         = pd.read_csv("data/processed/analysis_dataset.csv")
    summary    = pd.read_csv("data/processed/summary_stats.csv")
    reg        = pd.read_csv("data/processed/regression_results.csv")
    player_reg = pd.read_csv("data/processed/regression_results_player_level.csv")
    bin_reg    = pd.read_csv("data/processed/regression_results_bin_interaction.csv")
    check1     = pd.read_csv("data/processed/regression_results_check1_nseasons.csv")
    bbref      = pd.read_csv("data/raw/bbref_advanced_stats.csv")
    return df, summary, reg, player_reg, bin_reg, check1, bbref

df, summary, reg, player_reg, bin_reg, check1, bbref_raw = load_data()

PICK_BIN_ORDER = ["Top 5", "Picks 6-14", "Picks 15-30", "Second Round"]
ERA_COLORS     = {"Pre-Analytics": "#4878CF", "Post-Analytics": "#E07B39"}
BIN_COLORS     = {"Top 5": "#2ecc71", "Picks 6-14": "#3498db",
                   "Picks 15-30": "#e67e22", "Second Round": "#e74c3c"}
df["pick_bin"] = pd.Categorical(df["pick_bin"], categories=PICK_BIN_ORDER, ordered=True)

def normalize_name(name):
    name = str(name).strip().lower()
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    for s in [" jr.", " sr.", " iii", " ii", " iv"]:
        name = name.replace(s, "")
    return name.strip()

# ---------------------------------------------------------------------------
# View state
# ---------------------------------------------------------------------------

if "view" not in st.session_state:
    st.session_state.view = "dashboard"

# ---------------------------------------------------------------------------
# Paper view (full page)
# ---------------------------------------------------------------------------

if st.session_state.view == "paper":
    import re

    def _slug(heading_text):
        t = heading_text.lower()
        t = re.sub(r'[^\w\s-]', '', t)
        t = re.sub(r'\s+', '-', t.strip())
        return t

    try:
        with open("paper/draft.md", "r") as f:
            paper_text = f.read()
    except FileNotFoundError:
        paper_text = None

    # Sidebar: return button + navigation
    if st.sidebar.button("← Return to Dashboard", use_container_width=True):
        st.session_state.view = "dashboard"
        st.rerun()
    st.sidebar.divider()
    st.sidebar.markdown("**Contents**")

    if paper_text:
        headings = re.findall(r'^(#{1,3})\s+(.+)$', paper_text, re.MULTILINE)
        toc_lines = []
        for level, title in headings:
            slug = _slug(title)
            indent = "&ensp;&ensp;" * (len(level) - 1)
            toc_lines.append(f"{indent}[{title}](#{slug})")
        st.sidebar.markdown("<br>".join(toc_lines), unsafe_allow_html=True)

        # Render paper body
        parts = re.split(r'(!\[.*?\]\(.*?\))', paper_text)
        for part in parts:
            img_match = re.match(r'!\[(.*?)\]\((.*?)\)', part)
            if img_match:
                caption, path = img_match.group(1), img_match.group(2)
                resolved = path.replace("../", "")
                try:
                    st.image(resolved, caption=caption, use_container_width=True)
                except Exception:
                    st.warning(f"Could not load image: {resolved}")
            else:
                if part.strip():
                    st.markdown(part)
    else:
        st.error("paper/draft.md not found.")
    st.stop()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🏀 NBA Draft Pick Value Analysis")
st.caption("Surplus Value and the Analytics Revolution")

st.markdown("""
**The question:** Are NBA teams getting good value for money on their draft picks? And has that changed since teams started using data analytics?

> NBA rookies are locked into cheap contracts for 4 years. That means teams are essentially
> buying player value at a fixed low price. **This dashboard shows who gets the best deal.**
> Spoiler: top picks are not overpriced. They are actually the *safest* investment. But since 2010,
> smarter teams have started finding value deeper in the draft too.
""")

st.divider()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

if st.sidebar.button("📄 View Paper", use_container_width=True):
    st.session_state.view = "paper"
    st.rerun()

st.sidebar.divider()
st.sidebar.header("Filters")
era_filter = st.sidebar.multiselect(
    "Era", ["Pre-Analytics", "Post-Analytics"],
    default=["Pre-Analytics", "Post-Analytics"]
)
bin_filter = st.sidebar.multiselect(
    "Pick Bin", PICK_BIN_ORDER, default=PICK_BIN_ORDER
)
metric = st.sidebar.radio(
    "Performance metric",
    ["VORP_per_1M", "WS_per_1M", "BPM_per_1M"],
    format_func=lambda x: {
        "VORP_per_1M": "VORP per $1M (primary)",
        "WS_per_1M":   "Win Shares per $1M (robustness)",
        "BPM_per_1M":  "BPM per $1M (injury check)",
    }[x],
)

with st.sidebar.expander("What do these metrics mean?"):
    st.markdown("""
**VORP** (primary): how much value a player adds compared to a replacement-level player,
adjusted for minutes played. Higher = more valuable per dollar.

**Win Shares**: estimates how many wins a player contributed to their team in a season.
Used as a cross-check against VORP.

**BPM** (injury check): a per-possession efficiency rating unaffected by games missed.
Used to verify results are not driven by injury patterns.
""")

filtered = df[df["era"].isin(era_filter) & df["pick_bin"].isin(bin_filter)].copy()

if filtered.empty:
    st.warning("⚠️ No data matches the current filters. Please select at least one Era and one Pick Bin.")
    st.stop()

if "BPM_per_1M" not in filtered.columns:
    filtered["BPM_per_1M"] = filtered["BPM"] / (filtered["SALARY_USD"] / 1_000_000)
    q01, q99 = filtered["BPM_per_1M"].quantile(0.01), filtered["BPM_per_1M"].quantile(0.99)
    filtered["BPM_per_1M"] = filtered["BPM_per_1M"].clip(q01, q99)

metric_label = {
    "VORP_per_1M": "VORP per $1M",
    "WS_per_1M":   "Win Shares per $1M",
    "BPM_per_1M":  "BPM per $1M",
}[metric]

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)
col1.metric("Player-Seasons", f"{len(filtered):,}")
col2.metric("Unique Players", f"{filtered['name_key'].nunique():,}")
col3.metric("Draft Years", f"{int(filtered['DRAFT_YEAR'].min())}–{int(filtered['DRAFT_YEAR'].max())}")
col4.metric("Avg Salary", f"${filtered['SALARY_USD'].mean()/1e6:.1f}M")

st.divider()

# ---------------------------------------------------------------------------
# Tab layout
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Value by Pick Bin",
    "📉 Risk-Return",
    "🔵 Pick # vs Value",
    "📈 Era Convergence",
    "🔍 Player Lookup",
])

# ── Tab 1: Bar chart ─────────────────────────────────────────────────────────
with tab1:
    st.subheader(f"{metric_label} by Draft Position Bin")

    agg = (
        filtered.groupby(["pick_bin", "era"], observed=True)[metric]
        .agg(["mean", "sem", "count"])
        .reset_index()
    )
    agg["ci"] = 1.96 * agg["sem"]

    fig = px.bar(
        agg, x="pick_bin", y="mean", color="era",
        barmode="group", error_y="ci",
        color_discrete_map=ERA_COLORS,
        category_orders={"pick_bin": PICK_BIN_ORDER},
        labels={"mean": metric_label, "pick_bin": "Draft Position Bin", "era": "Era"},
        title=f"{metric_label} by Pick Bin and Analytics Era",
    )
    fig.update_layout(height=450, legend_title="Era")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Summary statistics table"):
        st.dataframe(
            agg.rename(columns={"mean": "Mean", "sem": "Std Error", "count": "N", "ci": "95% CI"}),
            use_container_width=True,
        )

# ── Tab 2: Risk-Return ───────────────────────────────────────────────────────
with tab2:
    st.subheader("Risk-Return Profile of Draft Pick Bins")
    st.caption("Each point is a pick bin in a given era. Upper-left is where you want to be: high return, low risk.")

    fin = (
        filtered.groupby(["pick_bin", "era"], observed=True)[metric]
        .agg(mean="mean", std="std")
        .reset_index()
    )
    bust = (
        filtered.groupby(["pick_bin", "era"], observed=True)["VORP"]
        .apply(lambda x: (x < 0).mean())
        .reset_index(name="bust_rate")
    )
    fin = fin.merge(bust, on=["pick_bin", "era"])
    fin["sharpe"] = fin["mean"] / fin["std"]
    fin["label"]  = fin["pick_bin"].astype(str) + "\n(" + fin["era"].str[:4] + ")"

    fig = px.scatter(
        fin, x="std", y="mean",
        color="pick_bin", symbol="era",
        color_discrete_map=BIN_COLORS,
        size=[14] * len(fin),
        text="label",
        hover_data={"bust_rate": ":.1%", "sharpe": ":.2f", "std": ":.3f", "mean": ":.3f"},
        labels={
            "std":  "Risk (Std Dev of " + metric_label + ")",
            "mean": "Return (Mean " + metric_label + ")",
            "pick_bin": "Pick Bin", "era": "Era",
        },
        title="Risk-Return by Draft Position Bin and Era (Mean-Variance Framework)",
    )
    fig.update_traces(textposition="top center", marker_size=16)
    fig.update_layout(height=520)
    st.plotly_chart(fig, use_container_width=True)

    # Bust rate + Sharpe table
    st.subheader("Finance Metrics by Pick Bin")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Sharpe Analog** (return ÷ risk, higher is better)")
        sharpe_tbl = fin.pivot(index="pick_bin", columns="era", values="sharpe").reindex(PICK_BIN_ORDER)
        st.dataframe(sharpe_tbl.style.format("{:.2f}").background_gradient(cmap="RdYlGn", axis=None),
                     use_container_width=True)

    with col_b:
        st.markdown("**Bust Rate** (% seasons with VORP < 0, lower is better)")
        bust_tbl = fin.pivot(index="pick_bin", columns="era", values="bust_rate").reindex(PICK_BIN_ORDER)
        st.dataframe(bust_tbl.style.format("{:.1%}").background_gradient(cmap="RdYlGn_r", axis=None),
                     use_container_width=True)

    st.markdown("""
    **How to read this:** Think of each draft slot like a stock. The further **left** a dot is,
    the more consistent the player (less variance in outcomes). The further **up**, the better
    the average return per dollar spent. You want upper-left: high return, low risk.

    Top picks (green) sit upper-left. They are the most reliable bang for your buck.
    Second-rounders (red) sit lower-right. Cheap contracts, but a much larger share
    of these picks bust. About **1 in 3** second-round picks produces *negative* value
    in a given season, vs. roughly **1 in 8** for lottery picks.
    """)

# ── Tab 3: Scatter ───────────────────────────────────────────────────────────
with tab3:
    st.subheader(f"Pick Number vs. {metric_label}")
    st.caption("LOWESS trend lines show smoothed relationship per era")

    fig = px.scatter(
        filtered, x="OVERALL_PICK", y=metric,
        color="era", color_discrete_map=ERA_COLORS,
        opacity=0.35,
        hover_data=["PLAYER_NAME", "DRAFT_YEAR", "SEASON_END_YEAR", "SALARY_USD"],
        labels={"OVERALL_PICK": "Overall Draft Pick", metric: metric_label, "era": "Era"},
        title="Draft Pick Value vs. Position",
    )
    for era, color in ERA_COLORS.items():
        sub = filtered[filtered["era"] == era].dropna(subset=[metric])
        if len(sub) > 20:
            smooth = lowess(sub[metric], sub["OVERALL_PICK"], frac=0.3)
            fig.add_trace(go.Scatter(
                x=smooth[:, 0], y=smooth[:, 1],
                mode="lines", name=f"{era} trend",
                line=dict(color=color, width=3),
            ))
    fig.add_vline(x=5.5,  line_dash="dash", line_color="gray", annotation_text="Top 5")
    fig.add_vline(x=14.5, line_dash="dot",  line_color="gray", annotation_text="Pick 14")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# ── Tab 4: Era convergence ───────────────────────────────────────────────────
with tab4:
    st.subheader("Did the Analytics Era Flatten the Value Curve?")

    era_agg = (
        filtered.groupby(["pick_bin", "era"], observed=True)[metric]
        .mean().reset_index()
    )
    fig = px.line(
        era_agg, x="pick_bin", y=metric, color="era",
        markers=True, color_discrete_map=ERA_COLORS,
        category_orders={"pick_bin": PICK_BIN_ORDER},
        labels={"pick_bin": "Draft Position Bin", metric: f"Mean {metric_label}", "era": "Era"},
        title="Mean Value per Dollar Across Draft Bins: Pre vs. Post Analytics",
    )
    fig.update_traces(marker_size=10, line_width=3)
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

    if metric == "VORP_per_1M":
        st.markdown("""
        **What's happening here:** Before 2010, there was a huge drop-off in value as you went
        deeper in the draft. Teams were terrible at finding hidden gems. After 2010, that gap
        shrunk. Teams got smarter. Mid-round and late picks started delivering closer to what
        lottery picks delivered. The regression below confirms this shift is statistically
        significant (P3, p = 0.031), and it lines up with when front offices started seriously
        investing in analytics departments.
        """)
    elif metric == "WS_per_1M":
        st.markdown("""
        **What's happening here:** On Win Shares, the same general pattern is visible in the
        chart, but it is **not statistically significant** (P5, p = 0.398; M5, p = 0.566) --
        see the robustness tables below. VORP and Win Shares diverge here because VORP adjusts
        for replacement level and Win Shares does not; the paper discusses this divergence
        as a limitation rather than as a confirming result.
        """)
    else:
        st.markdown("""
        **What's happening here:** On BPM (a per-possession rate stat used as an injury
        check), the convergence pattern is **not statistically significant** (M6, p = 0.931)
        -- see the season-level table below. This suggests the VORP-based flattening may
        partly reflect playing-time allocation changes rather than pure efficiency gains.
        """)

    st.subheader("Primary Model: Player-Level, Rookie Contract Window (N = 839)")
    st.markdown("""
    The paper's main specification collapses each player to **one observation**: cumulative
    VORP over their first four seasons (the rookie contract window) divided by total salary
    paid over that same window. This is the cleanest test of the rookie-scale surplus, since
    it matches the period when the CBA price is fixed.

    - **β(pick):** how much cumulative value per dollar drops with each additional pick slot
    - **β(post):** did overall value per dollar shift after 2010?
    - **β(pick×post):** the key number. Did the pick penalty get smaller after 2010? Positive = yes, the gap narrowed
    - **p(interact):** confidence level. Below 0.05 means we can be 95% confident the change is real, not random noise

    **P3 is the main model.** P1/P2 build up to it, P4 checks the result on a log scale, and
    P5 swaps in Win Shares as an alternative performance metric.
    """)

    player_display = player_reg[
        ["model", "n", "r2", "coef_pick", "pval_pick", "coef_post", "pval_post", "coef_interact", "pval_interact"]
    ].copy()
    player_display.columns = ["Model", "N", "R²", "β(pick)", "p(pick)", "β(post)", "p(post)", "β(pick×post)", "p(interact)"]
    player_display = player_display.fillna("--")

    def highlight_p3(row):
        if row["Model"] == "P3_interaction":
            return ["background-color: #fff3cd; color: black"] * len(row)
        return [""] * len(row)

    st.dataframe(player_display.style.apply(highlight_p3, axis=1), use_container_width=True)
    st.caption(
        "P3 (highlighted) is the main model: β(pick×post) = "
        f"{player_reg.loc[player_reg['model'] == 'P3_interaction', 'coef_interact'].iloc[0]:.5f} "
        f"(p = {player_reg.loc[player_reg['model'] == 'P3_interaction', 'pval_interact'].iloc[0]:.3f}). "
        "The pick penalty got smaller after 2010 -- the value curve flattened."
    )

    st.markdown("**Robustness check: pick bins instead of a continuous pick number**")
    st.markdown("""
    Instead of treating pick number as a straight line, this version compares each bin
    to Top 5 directly. "Pre gap" is how far behind Top 5 a bin was before 2010;
    "Post change" is how much that gap closed afterward.
    """)
    bin_display = bin_reg.copy()
    bin_display.columns = ["Bin", "Pre Gap vs Top 5", "p(pre gap)", "Post Change", "p(post change)"]
    st.dataframe(bin_display, use_container_width=True)
    st.caption(
        "All three bins below Top 5 narrowed their gap significantly after 2010 "
        "(Picks 6-14: p = 0.043, Picks 15-30: p = 0.031, Second Round: p = 0.003)."
    )

    st.markdown("**Robustness check: controlling for rookie-window data coverage**")
    c1, c2, c3 = st.columns(3)
    c1.metric("β(pick×post)", f"{check1['coef_interact'].iloc[0]:.4f}", help="Same interaction as P3, with n_seasons added as a control")
    c2.metric("p(interact)", f"{check1['pval_interact'].iloc[0]:.3f}")
    c3.metric("p(pick×post), P3 alone", "0.031")
    st.caption(
        "Some players have fewer than 4 seasons of rookie-window data (mostly pre-2010 players, "
        "due to a 2001 salary-data floor). Controlling for the number of seasons captured "
        "(`n_seasons`) doesn't weaken the flattening result -- it *strengthens* it, from "
        "p = 0.031 to p = 0.007. This suggests the convergence isn't an artifact of uneven data coverage."
    )

    st.subheader("Season-Level Robustness Checks (M1-M6, N = 6,095)")
    st.markdown("""
    As a cross-check, we also ran the same style of regression on the full season-by-season
    panel (every player-season, not collapsed to the rookie window). M3 here is the
    season-level analog of P3 above and points the same direction. M5 (Win Shares) and
    M6 (BPM, a rate stat unaffected by games missed) are discussed in the paper's
    limitations -- the convergence is weaker on these alternative metrics.
    """)
    reg_display = reg[["model", "n", "r2", "coef_pick", "pval_pick", "coef_interact", "pval_interact"]].copy()
    reg_display.columns = ["Model", "N", "R²", "β(pick)", "p(pick)", "β(pick×era)", "p(interact)"]
    st.dataframe(reg_display, use_container_width=True)
    st.caption("These season-level models support the player-level finding above but are not the paper's primary specification.")

# ── Tab 5: Player lookup ─────────────────────────────────────────────────────
with tab5:
    st.subheader("Player Career Value Lookup")

    player_names = sorted(df["PLAYER_NAME"].dropna().unique())
    selected     = st.selectbox("Search player", player_names)

    name_key     = normalize_name(selected)
    raw_seasons  = bbref_raw[bbref_raw["Player"].apply(normalize_name) == name_key]
    filtered_out = len(raw_seasons) - len(df[df["PLAYER_NAME"] == selected])
    player_df    = df[df["PLAYER_NAME"] == selected].sort_values("SEASON_END_YEAR").copy()

    if not player_df.empty:
        n_seasons = len(player_df)
        if n_seasons <= 2:
            st.warning(
                f"⚠️ **Limited data:** {selected} has only {n_seasons} season(s) in the analysis dataset. "
                f"{filtered_out} additional season(s) were excluded (below ≥20 GP / ≥200 MP thresholds). "
                f"Common for players with short or injury-affected careers."
            )
        elif filtered_out > 0:
            st.info(f"ℹ️ {filtered_out} season(s) excluded (below ≥20 GP / ≥200 MP thresholds).")

        info = player_df.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Draft Year",  int(info["DRAFT_YEAR"]))
        c2.metric("Pick #",      int(info["OVERALL_PICK"]))
        c3.metric("Pick Bin",    info["pick_bin"])
        c4.metric("Era",         info["era"])
        c5.metric("Avg VORP/$1M", f"{player_df['VORP_per_1M'].mean():.2f}")

        if "BPM_per_1M" not in player_df.columns:
            player_df["BPM_per_1M"] = player_df["BPM"] / (player_df["SALARY_USD"] / 1_000_000)

        fig = go.Figure()
        for col, name, color in [
            ("VORP_per_1M", "VORP/$1M", "#2196F3"),
            ("WS_per_1M",   "WS/$1M",   "#4CAF50"),
        ]:
            fig.add_trace(go.Scatter(
                x=player_df["SEASON_END_YEAR"], y=player_df[col],
                mode="lines+markers", name=name, line=dict(color=color, width=2),
            ))
        fig.add_hline(y=0, line_dash="dash", line_color="red",
                      annotation_text="Bust threshold (VORP < 0)")
        fig.update_layout(
            title=f"{selected}: Value per $1M Over Career",
            xaxis_title="Season", yaxis_title="Value per $1M", height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            player_df[["SEASON_END_YEAR", "SALARY_USD", "VORP", "WS", "BPM",
                        "VORP_per_1M", "WS_per_1M"]].rename(columns={
                "SEASON_END_YEAR": "Season", "SALARY_USD": "Salary ($)",
                "VORP_per_1M": "VORP/$1M", "WS_per_1M": "WS/$1M",
            }),
            use_container_width=True,
        )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.markdown(
    "<div style='text-align: center; color: grey; font-size: 0.85em;'>"
    "Created by <strong>Sharodeep Kuar</strong> and <strong>Caleb Williams</strong> &nbsp;|&nbsp; "
    "Msc Finance, Waseda Business School &nbsp;|&nbsp; "
    "Data: Basketball Reference, ESPN, NBA API"
    "</div>",
    unsafe_allow_html=True,
)
