import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
    df      = pd.read_csv("data/processed/analysis_dataset.csv")
    summary = pd.read_csv("data/processed/summary_stats.csv")
    reg     = pd.read_csv("data/processed/regression_results.csv")
    bbref   = pd.read_csv("data/raw/bbref_advanced_stats.csv")
    return df, summary, reg, bbref

df, summary, reg, bbref_raw = load_data()

PICK_BIN_ORDER = ["Top 5", "Picks 6-14", "Picks 15-30", "Second Round"]
ERA_COLORS     = {"Pre-Analytics": "#4878CF", "Post-Analytics": "#E07B39"}
df["pick_bin"] = pd.Categorical(df["pick_bin"], categories=PICK_BIN_ORDER, ordered=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🏀 NBA Draft Pick Value Analysis")
st.caption("Surplus Value and the Analytics Revolution | Waseda Business School — Sports Finance")

st.markdown("""
**Research question:** How has the analytics era changed the distribution of surplus value
across NBA draft positions?

> Under the rookie scale, **all first-round picks generate surplus value** — teams pay
> below-market rates. Top picks (1–5) deliver the *most* value per dollar. Post-2010,
> analytics narrowed the gap across bins (interaction p = 0.024).
""")

st.divider()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

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

filtered = df[df["era"].isin(era_filter) & df["pick_bin"].isin(bin_filter)].copy()

if filtered.empty:
    st.warning("⚠️ No data matches the current filters. Please select at least one Era and one Pick Bin.")
    st.stop()

# Compute BPM_per_1M on the fly if needed
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

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Value by Pick Bin",
    "🔵 Pick # vs Value",
    "📈 Era Convergence",
    "🔍 Player Lookup",
])

# ── Tab 1: Bar chart ────────────────────────────────────────────────────────
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
        barmode="group",
        error_y="ci",
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

# ── Tab 2: Scatter ──────────────────────────────────────────────────────────
with tab2:
    st.subheader(f"Pick Number vs. {metric_label}")
    st.caption("LOWESS trend lines show smoothed relationship per era")

    fig = px.scatter(
        filtered, x="OVERALL_PICK", y=metric,
        color="era",
        color_discrete_map=ERA_COLORS,
        opacity=0.35,
        hover_data=["PLAYER_NAME", "DRAFT_YEAR", "SEASON_END_YEAR", "SALARY_USD"],
        labels={"OVERALL_PICK": "Overall Draft Pick", metric: metric_label, "era": "Era"},
        title=f"Draft Pick Value vs. Position",
    )

    # Add LOWESS trend lines
    from statsmodels.nonparametric.smoothers_lowess import lowess
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

# ── Tab 3: Era convergence ───────────────────────────────────────────────────
with tab3:
    st.subheader("Did the Analytics Era Flatten the Value Curve?")

    era_agg = (
        filtered.groupby(["pick_bin", "era"], observed=True)[metric]
        .mean().reset_index()
    )
    fig = px.line(
        era_agg, x="pick_bin", y=metric, color="era",
        markers=True,
        color_discrete_map=ERA_COLORS,
        category_orders={"pick_bin": PICK_BIN_ORDER},
        labels={"pick_bin": "Draft Position Bin", metric: f"Mean {metric_label}", "era": "Era"},
        title="Mean Value per Dollar Across Draft Bins: Pre vs. Post Analytics",
    )
    fig.update_traces(marker_size=10, line_width=3)
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **Interpretation:** The gap between the Pre-Analytics (blue) and Post-Analytics (orange)
    lines narrows from left to right — the analytics era compressed surplus value across bins.
    This is confirmed by the significant interaction term in the OLS regression (p = 0.024 at
    the 2010 breakpoint).
    """)

    st.subheader("Regression Results")
    reg_display = reg[["model", "n", "r2", "coef_pick", "pval_pick", "coef_interact", "pval_interact"]].copy()
    reg_display.columns = ["Model", "N", "R²", "β(pick)", "p(pick)", "β(pick×era)", "p(interact)"]

    def highlight_main(row):
        if row["Model"] == "M3_interaction":
            return ["background-color: #fff3cd; color: black"] * len(row)
        return [""] * len(row)

    st.dataframe(
        reg_display.style.apply(highlight_main, axis=1),
        use_container_width=True,
    )
    st.caption("M3 (highlighted) is the main model. HC3 robust standard errors throughout.")

# ── Tab 4: Player lookup ─────────────────────────────────────────────────────
with tab4:
    st.subheader("Player Career Value Lookup")

    player_names = sorted(df["PLAYER_NAME"].dropna().unique())
    selected     = st.selectbox("Search player", player_names)

    # Also check raw BBRef for total seasons before filtering
    import unicodedata
    def normalize_name(name):
        name = str(name).strip().lower()
        name = unicodedata.normalize("NFD", name)
        name = "".join(c for c in name if unicodedata.category(c) != "Mn")
        for s in [" jr.", " sr.", " iii", " ii", " iv"]:
            name = name.replace(s, "")
        return name.strip()
    name_key = normalize_name(selected)
    raw_seasons = bbref_raw[bbref_raw["Player"].apply(normalize_name) == name_key]
    filtered_out = len(raw_seasons) - len(df[df["PLAYER_NAME"] == selected])

    player_df = df[df["PLAYER_NAME"] == selected].sort_values("SEASON_END_YEAR").copy()

    if not player_df.empty:
        n_seasons = len(player_df)
        if n_seasons <= 2:
            st.warning(
                f"⚠️ **Limited data:** {selected} has only {n_seasons} season(s) in the analysis dataset. "
                f"{filtered_out} additional season(s) were excluded because the player did not meet the "
                f"minimum thresholds (≥20 games played, ≥200 total minutes). "
                f"This is common for players with short or injury-affected careers."
            )
        elif filtered_out > 0:
            st.info(
                f"ℹ️ {filtered_out} season(s) for {selected} were excluded from analysis "
                f"(below ≥20 GP / ≥200 MP thresholds)."
            )

        info = player_df.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Draft Year",   int(info["DRAFT_YEAR"]))
        c2.metric("Pick #",       int(info["OVERALL_PICK"]))
        c3.metric("Pick Bin",     info["pick_bin"])
        c4.metric("Era",          info["era"])

        if "BPM_per_1M" not in player_df.columns:
            player_df["BPM_per_1M"] = player_df["BPM"] / (player_df["SALARY_USD"] / 1_000_000)

        fig = go.Figure()
        for col, name, color in [
            ("VORP_per_1M", "VORP/$1M",  "#2196F3"),
            ("WS_per_1M",   "WS/$1M",    "#4CAF50"),
        ]:
            fig.add_trace(go.Scatter(
                x=player_df["SEASON_END_YEAR"], y=player_df[col],
                mode="lines+markers", name=name, line=dict(color=color, width=2),
            ))

        fig.update_layout(
            title=f"{selected} — Value per $1M Over Career",
            xaxis_title="Season", yaxis_title="Value per $1M",
            height=380,
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
