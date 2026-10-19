from __future__ import annotations

from math import ceil, floor
from pathlib import Path
from typing import Any

from math import isfinite

import pandas as pd
import plotly.express as px
import streamlit as st


# PayGuard AI remains a local, rules-based educational prototype. The existing
# score weights and thresholds are intentionally preserved below.
DATA_PATH = Path(__file__).with_name("sample_transactions.csv")
RISK_ORDER = ["High", "Medium", "Low"]
RISK_COLORS = {"High": "#e56d7d", "Medium": "#f0b94c", "Low": "#48b99a"}
EMPTY_COLUMNS = [
    "transaction_id", "amount", "country_mismatch", "failed_attempts", "channel",
    "risk_score", "risk_level", "explanation", "_source_order",
]

st.set_page_config(
    page_title="PayGuard AI · Risk Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
:root {
  --ink: #201a38;
  --muted: #77748a;
  --purple: #7156d9;
  --purple-dark: #24194f;
  --line: #eceaf3;
  --canvas: #f7f7fb;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: var(--canvas); color: var(--ink); }
.block-container { max-width: 1580px; padding-top: 1.45rem; padding-bottom: 2.2rem; }
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #251951 0%, #1c153e 100%);
  border-right: 1px solid rgba(255,255,255,.07);
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span { color: #f5f2ff !important; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
  padding: .42rem .65rem; border-radius: 11px; margin: .08rem 0;
  transition: background .16s ease;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: rgba(255,255,255,.09); }
section[data-testid="stSidebar"] [data-testid="stRadio"] label p { font-weight: 600; font-size: .92rem; }
section[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + div p { color: #f5d969 !important; }
section[data-testid="stSidebar"] [data-testid="stRadio"] input { accent-color: #8c72f0; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.14); }
section[data-testid="stSidebar"] .stCaption { color: #bbb3d8 !important; }
section[data-testid="stSidebar"] [data-testid="stAlert"] { background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.13); }
.topline { display:flex; justify-content:space-between; align-items:center; margin-bottom: .6rem; }
.eyebrow { color:#7e76a1; text-transform:uppercase; letter-spacing:.12em; font-size:.69rem; font-weight:800; }
.page-title { font-family:'Manrope',sans-serif; color:#211a3a; font-size:1.78rem; line-height:1.15; font-weight:800; margin:.1rem 0 .3rem; }
.page-subtitle { color:#77748a; font-size:.94rem; margin:0 0 1.1rem; }
.demo-pill { display:inline-flex; align-items:center; gap:.45rem; padding:.38rem .7rem; border-radius:999px; background:#f1edff; color:#6c53cc; font-size:.72rem; font-weight:800; letter-spacing:.04em; }
.demo-dot { width:7px; height:7px; border-radius:50%; background:#8e74ea; display:inline-block; }
.brand-mark { width:40px; height:40px; display:flex; justify-content:center; align-items:center; border-radius:13px; background:linear-gradient(145deg,#947bf2,#6545ce); color:white; font-size:1.15rem; box-shadow:0 8px 20px rgba(97,67,201,.28); }
.brand-wrap { display:flex; align-items:center; gap:.72rem; padding:.6rem .25rem 1.15rem; }
.brand-name { color:#fff; font-family:'Manrope',sans-serif; font-size:1.03rem; font-weight:800; line-height:1.05; }
.brand-caption { color:#c1b9e1; font-size:.69rem; margin-top:.24rem; }
.sidebar-section { color:#a69cc9; text-transform:uppercase; font-size:.66rem; font-weight:800; letter-spacing:.14em; margin:.25rem 0 .5rem .25rem; }
.welcome-card {
  position:relative; overflow:hidden; min-height:202px; border-radius:23px; padding:1.65rem 2rem;
  background:linear-gradient(110deg,#f0edff 0%,#f6f3ff 62%,#eee9ff 100%);
  border:1px solid #e9e3ff; display:flex; align-items:center; justify-content:space-between;
  box-shadow:0 10px 28px rgba(42,29,85,.045); margin:.2rem 0 1.35rem;
}
.welcome-copy { max-width:68%; position:relative; z-index:2; }
.welcome-copy h2 { color:#251b50; font-family:'Manrope',sans-serif; font-size:1.85rem; font-weight:800; margin:0 0 .45rem; }
.welcome-copy p { color:#615b7a; font-size:.95rem; max-width:540px; margin:0 0 1rem; line-height:1.55; }
.welcome-copy .welcome-tag { color:#7156d9; text-transform:uppercase; font-size:.66rem; letter-spacing:.12em; font-weight:800; margin-bottom:.4rem; }
.welcome-art { width:190px; min-width:150px; height:160px; position:absolute; right:2.5%; top:50%; transform:translateY(-50%); opacity:.98; }
.welcome-action { display:inline-flex; align-items:center; gap:.45rem; background:#7257da; color:white !important; padding:.64rem 1rem; border-radius:10px; font-size:.83rem; font-weight:700; text-decoration:none; }
.metric-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.85rem; margin:.15rem 0 1.25rem; }
.metric-card { background:white; border:1px solid #eeecf4; border-radius:17px; padding:1rem 1.05rem .92rem; min-height:112px; box-shadow:0 4px 15px rgba(35,25,70,.035); }
.metric-top { display:flex; justify-content:space-between; align-items:center; gap:.5rem; }
.metric-label { color:#77748a; font-size:.77rem; font-weight:600; }
.metric-icon { height:31px; width:31px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:.9rem; }
.metric-value { color:#26203e; font-family:'Manrope',sans-serif; font-size:1.72rem; line-height:1.15; font-weight:800; margin:.55rem 0 .18rem; }
.metric-help { color:#9692a3; font-size:.69rem; }
.section-heading { color:#29233f; font-family:'Manrope',sans-serif; font-size:1.08rem; font-weight:800; margin:.2rem 0 .2rem; }
.section-note { color:#8a8798; font-size:.78rem; margin:0 0 .65rem; }
.panel { background:white; border:1px solid #eeecf4; border-radius:17px; padding:1rem 1.1rem; box-shadow:0 4px 15px rgba(35,25,70,.03); }
.alert-row { display:flex; gap:.7rem; padding:.75rem 0; border-bottom:1px solid #f0eef5; align-items:flex-start; }
.alert-row:last-child { border-bottom:0; padding-bottom:.1rem; }
.alert-icon { width:31px; height:31px; flex:none; display:flex; align-items:center; justify-content:center; border-radius:10px; font-weight:800; }
.alert-title { color:#312b47; font-size:.8rem; font-weight:700; margin:.04rem 0 .18rem; }
.alert-text { color:#817d91; font-size:.73rem; line-height:1.4; }
.risk-chip { display:inline-block; padding:.22rem .55rem; border-radius:999px; font-weight:800; font-size:.72rem; }
.disclaimer { background:#fbf8eb; border:1px solid #f2e8bf; color:#756235; border-radius:12px; padding:.72rem .9rem; font-size:.76rem; line-height:1.45; margin:.7rem 0; }
.rule-card { border:1px solid #eeecf4; background:#fff; border-radius:15px; padding:1rem 1.1rem; height:100%; }
.rule-number { color:#7156d9; font-family:'Manrope',sans-serif; font-size:.8rem; font-weight:800; letter-spacing:.08em; }
.rule-card h4 { color:#2b2542; margin:.4rem 0 .25rem; font-family:'Manrope',sans-serif; font-size:.95rem; }
.rule-card p { color:#817d91; font-size:.79rem; line-height:1.45; margin:0; }
.result-card { padding:1rem 1.1rem; border:1px solid #eeecf4; background:white; border-radius:15px; margin:.8rem 0; }
.result-score { font-family:'Manrope',sans-serif; font-size:2.1rem; font-weight:800; line-height:1; }
.result-bar { height:8px; background:#f0eef5; border-radius:99px; overflow:hidden; margin:.7rem 0 .25rem; }
.result-fill { height:100%; border-radius:99px; }
.footer-note { color:#9793a3; font-size:.7rem; text-align:center; padding:1rem 0 .1rem; }
@media (max-width: 900px) {
  .metric-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .welcome-art { right:0; opacity:.38; }
  .welcome-copy { max-width:100%; }
}
@media (max-width: 560px) {
  .block-container { padding-left:1rem; padding-right:1rem; }
  .metric-grid { gap:.55rem; }
  .metric-card { padding:.8rem; min-height:102px; }
  .metric-value { font-size:1.45rem; }
  .welcome-card { padding:1.2rem; }
  .welcome-copy h2 { font-size:1.45rem; }
  .welcome-art { display:none; }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _number(value: Any) -> float | None:
    """Convert a possibly missing or formatted value to a finite float."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    try:
        text = str(value).strip().replace(",", "").replace("$", "")
        if not text:
            return None
        number = float(text)
        return number if isfinite(number) else None
    except (TypeError, ValueError, OverflowError):
        return None


def assess_risk(row: Any) -> pd.Series:
    """Apply the original transparent demo rules; absent values do not trigger rules."""
    if not hasattr(row, "get"):
        row = {}

    score = 0
    reasons: list[str] = []

    amount = _number(row.get("amount"))
    mismatch_value = row.get("country_mismatch", "")
    try:
        mismatch_missing = mismatch_value is None or pd.isna(mismatch_value)
    except (TypeError, ValueError):
        mismatch_missing = False
    mismatch = "" if mismatch_missing else str(mismatch_value).strip().casefold()
    attempts = _number(row.get("failed_attempts"))

    if amount is not None and amount >= 1000:
        score += 40
        reasons.append("High transaction amount")
    if mismatch in {"yes", "true", "1", "y"}:
        score += 35
        reasons.append("Country mismatch")
    if attempts is not None and attempts >= 3:
        score += 25
        reasons.append("Multiple failed attempts")

    score = min(score, 100)
    level = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
    explanation = "; ".join(reasons) if reasons else "No demo rules triggered"
    return pd.Series([int(score), level, explanation])


def load_transactions(path: Path = DATA_PATH) -> tuple[pd.DataFrame, list[str]]:
    """Load the sample CSV defensively, removing repeated headers and exact duplicates."""
    notes: list[str] = []
    try:
        raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    except FileNotFoundError:
        return pd.DataFrame(columns=EMPTY_COLUMNS), [f"Dataset not found: {path.name}"]
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        return pd.DataFrame(columns=EMPTY_COLUMNS), [f"Could not read the dataset: {exc}"]

    if raw.empty:
        return pd.DataFrame(columns=EMPTY_COLUMNS), ["The dataset is empty."]

    raw.columns = [str(column).strip().lower() for column in raw.columns]
    required = {"transaction_id", "amount", "country_mismatch", "failed_attempts"}
    missing_columns = sorted(required.difference(raw.columns))
    if missing_columns:
        return pd.DataFrame(columns=EMPTY_COLUMNS), ["Required columns missing: " + ", ".join(missing_columns)]

    raw["transaction_id"] = raw["transaction_id"].astype(str).str.strip()
    embedded_headers = raw["transaction_id"].str.casefold().eq("transaction_id")
    header_count = int(embedded_headers.sum())
    raw = raw.loc[~embedded_headers].copy()
    raw = raw.loc[raw["transaction_id"].ne("")].copy()

    # Exact repeated records in the provided CSV are treated as accidental copies.
    duplicate_count = int(raw.duplicated(keep="first").sum())
    raw = raw.drop_duplicates(keep="first").copy()

    if raw.empty:
        if header_count:
            notes.append(f"Ignored {header_count} repeated CSV header row{'s' if header_count != 1 else ''}.")
        return pd.DataFrame(columns=EMPTY_COLUMNS), notes or ["The dataset contains no transaction rows."]

    raw["amount"] = raw["amount"].map(_number)
    raw["failed_attempts"] = raw["failed_attempts"].map(_number)
    raw["country_mismatch"] = raw["country_mismatch"].astype(str).str.strip()
    if "channel" in raw.columns:
        raw["channel"] = raw["channel"].astype(str).str.strip().replace("", "Unknown")
    else:
        raw["channel"] = "Unknown"

    scored = raw.apply(assess_risk, axis=1)
    scored.columns = ["risk_score", "risk_level", "explanation"]
    raw[["risk_score", "risk_level", "explanation"]] = scored
    raw["risk_score"] = pd.to_numeric(raw["risk_score"], errors="coerce").fillna(0).astype(int)
    raw["_source_order"] = range(len(raw))

    if header_count:
        notes.append(f"Ignored {header_count} repeated CSV header row{'s' if header_count != 1 else ''}.")
    if duplicate_count:
        notes.append(
            f"Ignored {duplicate_count} exact duplicate record{'s' if duplicate_count != 1 else ''}; "
            "each distinct source row is counted once."
        )
    missing_amount_count = int(raw["amount"].isna().sum())
    if missing_amount_count:
        notes.append(
            f"{missing_amount_count} transaction{'s' if missing_amount_count != 1 else ''} "
            "have missing or invalid amounts; those values do not trigger the amount rule."
        )
    return raw.reset_index(drop=True), notes


def page_header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="topline"><div class="eyebrow">{eyebrow}</div>'
        '<div class="demo-pill"><span class="demo-dot"></span> DEMO ENVIRONMENT</div></div>'
        f'<div class="page-title">{title}</div><div class="page-subtitle">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def format_money(value: Any) -> str:
    number = _number(value)
    return "—" if number is None else f"${number:,.2f}"


def risk_counts(data: pd.DataFrame) -> pd.DataFrame:
    counts = data["risk_level"].value_counts().reindex(RISK_ORDER, fill_value=0)
    return pd.DataFrame({"Risk level": RISK_ORDER, "Transactions": counts.values})


def chart_layout(fig: Any, height: int = 290) -> Any:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#77748a", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#eeecf4")
    fig.update_yaxes(gridcolor="#f0eef5", zeroline=False)
    return fig


def show_distribution_chart(data: pd.DataFrame, key: str) -> None:
    counts = risk_counts(data)
    fig = px.pie(
        counts,
        names="Risk level",
        values="Transactions",
        hole=0.72,
        color="Risk level",
        color_discrete_map=RISK_COLORS,
        category_orders={"Risk level": RISK_ORDER},
        custom_data=["Transactions"],
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(size=12, color="white"),
        hovertemplate="%{label}: %{customdata[0]} transactions<extra></extra>",
        marker=dict(line=dict(color="white", width=3)),
    )
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-.08, x=.03))
    fig = chart_layout(fig, 300)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "responsive": True}, key=key)


def show_channel_chart(data: pd.DataFrame, key: str) -> None:
    if data.empty:
        st.info("No channel data is available for this view.")
        return
    summary = (
        data.groupby(["channel", "risk_level"], dropna=False)
        .size()
        .rename("Transactions")
        .reset_index()
    )
    fig = px.bar(
        summary,
        x="channel",
        y="Transactions",
        color="risk_level",
        barmode="stack",
        category_orders={"risk_level": RISK_ORDER},
        color_discrete_map=RISK_COLORS,
        labels={"channel": "Channel", "risk_level": "Risk level"},
    )
    fig.update_traces(hovertemplate="%{x}<br>%{fullData.name}: %{y}<extra></extra>")
    st.plotly_chart(
        chart_layout(fig, 300),
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
        key=key,
    )


def display_transactions(data: pd.DataFrame, max_rows: int | None = None) -> pd.DataFrame:
    columns = ["transaction_id", "amount", "risk_score", "risk_level"]
    if "status" in data.columns:
        columns.append("status")
    if "channel" in data.columns:
        columns.append("channel")
    visible = data.sort_values("_source_order", ascending=False).head(max_rows) if max_rows else data
    visible = visible.loc[:, [column for column in columns if column in visible.columns]].copy()
    visible = visible.rename(
        columns={
            "transaction_id": "Transaction ID",
            "amount": "Amount",
            "risk_score": "Risk score",
            "risk_level": "Risk level",
            "status": "Status",
            "channel": "Channel",
        }
    )
    if "Amount" in visible.columns:
        visible["Amount"] = visible["Amount"].map(lambda value: "—" if pd.isna(value) else f"${value:,.2f}")
    return visible


def alert_items(data: pd.DataFrame) -> list[tuple[str, str, str, str]]:
    if data.empty:
        return [("·", "No transaction insights", "Load a valid CSV dataset to see risk alerts.", "#f1edff")]
    items: list[tuple[str, str, str, str]] = []
    high = data.loc[data["risk_level"].eq("High")]
    mismatches = data["country_mismatch"].astype(str).str.casefold().isin({"yes", "true", "1", "y"})
    if len(high):
        items.append(("!", f"{len(high)} high-risk transaction{'s' if len(high) != 1 else ''}",
                      f"{len(high) / len(data):.0%} of the cleaned sample score 60 or higher under the demo rules.", "#fff0f1"))
    else:
        items.append(("✓", "No high-risk records in this sample", "No transaction reached the demo high-risk threshold.", "#eaf8f3"))
    mismatch_count = int(mismatches.sum())
    if mismatch_count:
        items.append(("↔", f"{mismatch_count} country mismatch{'es' if mismatch_count != 1 else ''}",
                      "Country mismatch contributes 35 points to the existing demo score.", "#f2efff"))
    valid_amounts = data.dropna(subset=["amount"])
    if not valid_amounts.empty:
        biggest = valid_amounts.loc[valid_amounts["amount"].idxmax()]
        items.append(("↑", f"Largest amount: {format_money(biggest['amount'])}",
                      f"{biggest['transaction_id']} is the largest transaction in the loaded sample.", "#fff7e8"))
    max_attempts = data["failed_attempts"].dropna()
    if not max_attempts.empty:
        max_value = int(max_attempts.max())
        items.append(("↻", f"{max_value} max failed attempts", "Three or more attempts trigger the existing 25-point demo rule.", "#edf4ff"))
    return items[:4]


def show_alerts(data: pd.DataFrame) -> None:
    for icon, title, text, background in alert_items(data):
        st.markdown(
            '<div class="alert-row">'
            f'<div class="alert-icon" style="background:{background};color:#6651c6">{icon}</div>'
            f'<div><div class="alert-title">{title}</div><div class="alert-text">{text}</div></div>'
            '</div>',
            unsafe_allow_html=True,
        )


def metric_card(label: str, value: int, helper: str, icon: str, tint: str, icon_color: str) -> str:
    return (
        '<div class="metric-card"><div class="metric-top">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-icon" style="background:{tint};color:{icon_color}">{icon}</div>'
        f'</div><div class="metric-value">{value:,}</div>'
        f'<div class="metric-help">{helper}</div></div>'
    )


def render_dashboard(data: pd.DataFrame, cleaning_notes: list[str]) -> None:
    page_header("PAYMENT SECURITY OVERVIEW", "Dashboard", "A clear, data-backed view of the sample payment risk profile.")
    art = """<svg class="welcome-art" viewBox="0 0 210 170" role="img" aria-label="Shield illustration">
      <circle cx="132" cy="83" r="73" fill="#e2dcff" opacity=".72"/><circle cx="44" cy="132" r="22" fill="#d8cffb" opacity=".65"/>
      <path d="M104 24 154 42v35c0 34-20 53-50 68-30-15-50-34-50-68V42z" fill="#765bdd"/>
      <path d="M104 35 143 49v28c0 27-15 42-39 55-24-13-39-28-39-55V49z" fill="#fff" opacity=".97"/>
      <path d="m84 83 14 14 28-31" fill="none" stroke="#49b99c" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="171" cy="34" r="12" fill="#f4cb58"/><path d="M171 27v14M164 34h14" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
      <circle cx="33" cy="59" r="5" fill="#a491f0"/><circle cx="177" cy="119" r="6" fill="#f1b4bd"/>
    </svg>"""
    st.markdown(
        '<div class="welcome-card"><div class="welcome-copy">'
        '<div class="welcome-tag">Your payment security workspace</div>'
        '<h2>Welcome to PayGuard AI</h2>'
        '<p>Review transaction patterns, explore demo risk signals, and check a sample payment using the project’s transparent rule-based score.</p>'
        '<span class="welcome-action">◈ &nbsp;Rules-based demo</span>'
        '</div>' + art + '</div>',
        unsafe_allow_html=True,
    )
    if cleaning_notes:
        st.info("Dataset preparation: " + " ".join(cleaning_notes), icon="ℹ️")

    if data.empty:
        st.warning("No usable transaction records were found. Check the CSV path and required columns.")
        return

    total = len(data)
    counts = data["risk_level"].value_counts()
    cards = [
        metric_card("Total transactions", total, "Distinct usable records in the sample", "▤", "#f0edff", "#7156d9"),
        metric_card("High risk", int(counts.get("High", 0)), "Score 60–100 under demo rules", "!", "#fff0f1", "#d65b6b"),
        metric_card("Medium risk", int(counts.get("Medium", 0)), "Score 30–59 under demo rules", "◒", "#fff7e8", "#c28c18"),
        metric_card("Low risk", int(counts.get("Low", 0)), "Score 0–29 under demo rules", "✓", "#eaf8f3", "#299276"),
    ]
    st.markdown('<div class="metric-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)

    chart_col, summary_col = st.columns([1.05, 1.25], gap="medium")
    with chart_col:
        st.markdown('<div class="section-heading">Transaction risk distribution</div><div class="section-note">Risk levels calculated from the sample CSV</div>', unsafe_allow_html=True)
        with st.container(border=True):
            show_distribution_chart(data, "risk_distribution")
    with summary_col:
        st.markdown('<div class="section-heading">Risk summary by channel</div><div class="section-note">Transaction counts segmented by payment channel</div>', unsafe_allow_html=True)
        with st.container(border=True):
            show_channel_chart(data, "risk_by_channel")

    table_col, alerts_col = st.columns([1.5, 1], gap="medium")
    with table_col:
        st.markdown('<div class="section-heading">Recent transactions</div><div class="section-note">Latest rows in the source file; timestamps are not included in this dataset.</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.dataframe(display_transactions(data, 7), width="stretch", hide_index=True)
            st.caption("Status is shown only when present in the source CSV; no status field is included in this sample.")
    with alerts_col:
        st.markdown('<div class="section-heading">Risk alerts</div><div class="section-note">Insights derived from the loaded sample</div>', unsafe_allow_html=True)
        with st.container(border=True):
            show_alerts(data)

    st.markdown('<div class="footer-note">Educational prototype · fictional sample data · not for real payment decisions</div>', unsafe_allow_html=True)


def render_transactions(data: pd.DataFrame) -> None:
    page_header("DATA EXPLORER", "Transactions", "Filter the sample records and inspect each rules-based risk result.")
    if data.empty:
        st.warning("No usable transactions are available.")
        return

    risk_col, channel_col, search_col = st.columns([1, 1, 1.3])
    with risk_col:
        selected_risks = st.multiselect("Risk level", RISK_ORDER, default=RISK_ORDER, key="transaction_risks")
    channels = sorted(data["channel"].dropna().astype(str).unique().tolist())
    with channel_col:
        selected_channels = st.multiselect("Channel", channels, default=channels, key="transaction_channels")
    with search_col:
        search = st.text_input("Find transaction ID", placeholder="e.g. TXN1008", key="transaction_search")

    amount_values = data["amount"].dropna()
    if not amount_values.empty:
        lower = floor(float(amount_values.min()))
        upper = ceil(float(amount_values.max()))
        if upper <= lower:
            upper = lower + 1
        amount_range = st.slider(
            "Amount range",
            min_value=float(lower),
            max_value=float(upper),
            value=(float(lower), float(upper)),
            step=1.0,
            format="$%.0f",
            key="transaction_amount_range",
        )
    else:
        amount_range = None
        st.caption("No valid amount values are available to filter.")

    filtered = data.copy()
    filtered = filtered.loc[filtered["risk_level"].isin(selected_risks)]
    filtered = filtered.loc[filtered["channel"].astype(str).isin(selected_channels)]
    if search.strip():
        filtered = filtered.loc[
            filtered["transaction_id"].astype(str).str.contains(search.strip(), case=False, na=False, regex=False)
        ]
    if amount_range is not None:
        filtered = filtered.loc[
            filtered["amount"].isna()
            | filtered["amount"].between(amount_range[0], amount_range[1], inclusive="both")
        ]

    st.markdown(f"<div class='section-heading'>{len(filtered):,} matching transaction{'s' if len(filtered) != 1 else ''}</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.dataframe(display_transactions(filtered), width="stretch", hide_index=True, height=430)
    csv_data = filtered.drop(columns=["_source_order"], errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered CSV",
        data=csv_data,
        file_name="payguard_filtered_transactions.csv",
        mime="text/csv",
        type="primary",
    )


def render_risk_analysis(data: pd.DataFrame) -> None:
    page_header("RULE EXPLANATION", "Risk analysis", "Understand what contributes to each score. This is a transparent demo, not a trained fraud model.")
    rule_cols = st.columns(3, gap="medium")
    rules = [
        ("01 · AMOUNT", "High transaction amount", "Amount of $1,000 or more adds 40 points to the demo score."),
        ("02 · COUNTRY", "Country mismatch", "A “Yes” country mismatch adds 35 points."),
        ("03 · ATTEMPTS", "Repeated failed attempts", "Three or more failed attempts add 25 points."),
    ]
    for col, (number, title, body) in zip(rule_cols, rules):
        with col:
            st.markdown(f'<div class="rule-card"><div class="rule-number">{number}</div><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    chart_col, detail_col = st.columns([1.2, 1], gap="medium")
    with chart_col:
        st.markdown('<div class="section-heading">Risk distribution</div><div class="section-note">Calculated across distinct cleaned records</div>', unsafe_allow_html=True)
        with st.container(border=True):
            if not data.empty:
                show_distribution_chart(data, "analysis_distribution")
            else:
                st.info("No transactions to chart.")
    with detail_col:
        st.markdown('<div class="section-heading">Score interpretation</div><div class="section-note">Existing score bands retained from the original app</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("""
            - **High · 60–100:** elevated demo signal; review the triggered rules.
            - **Medium · 30–59:** one or more demo rules triggered.
            - **Low · 0–29:** no rule combination reached the medium threshold.

            Scores are capped at 100. Missing values do not trigger a rule. The score is not validated for production fraud detection.
            """)

    st.markdown('<div class="section-heading">Amount and failed-attempt patterns</div><div class="section-note">Each point is a source transaction; hover to inspect its demo score.</div>', unsafe_allow_html=True)
    with st.container(border=True):
        plot_data = data.dropna(subset=["amount", "failed_attempts"])
        if not plot_data.empty:
            fig = px.scatter(
                plot_data,
                x="amount",
                y="failed_attempts",
                color="risk_level",
                color_discrete_map=RISK_COLORS,
                category_orders={"risk_level": RISK_ORDER},
                hover_name="transaction_id",
                hover_data={"risk_score": True, "channel": True, "amount": ":$,.2f"},
                labels={"amount": "Amount ($)", "failed_attempts": "Failed attempts", "risk_level": "Risk level"},
            )
            fig.update_traces(marker=dict(size=12, opacity=.85, line=dict(width=1, color="white")))
            fig = chart_layout(fig, 340)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "responsive": True}, key="risk_scatter")
        else:
            st.info("There are no rows with both a valid amount and failed-attempt count.")


def render_check_transaction() -> None:
    page_header("DEMO TOOL", "Check a transaction", "Enter sample values to see the existing PayGuard AI demo score and rule explanation.")
    left, right = st.columns([1.15, .85], gap="large")
    with left:
        with st.container(border=True):
            st.markdown('<div class="section-heading">Transaction details</div><div class="section-note">These values are evaluated locally using the existing demo rules.</div>', unsafe_allow_html=True)
            with st.form("check_transaction_form", clear_on_submit=False):
                amount = st.number_input("Transaction amount ($)", min_value=0.0, max_value=1_000_000_000.0, value=250.0, step=25.0, format="%.2f")
                mismatch = st.selectbox("Country mismatch?", ["No", "Yes"])
                attempts = st.number_input("Failed attempts", min_value=0, max_value=100_000, value=0, step=1)
                submitted = st.form_submit_button("Check demo risk", type="primary", width="stretch")
    with right:
        with st.container(border=True):
            st.markdown('<div class="section-heading">How the score works</div><div class="section-note">Rules and thresholds from the current project</div>', unsafe_allow_html=True)
            st.markdown("""
            - Amount **≥ $1,000**: +40 points
            - Country mismatch **Yes**: +35 points
            - Failed attempts **≥ 3**: +25 points
            - Maximum score: **100**
            """)
            st.caption("High ≥ 60 · Medium ≥ 30 · otherwise Low")

    if submitted:
        score, level, explanation = assess_risk(
            {"amount": amount, "country_mismatch": mismatch, "failed_attempts": attempts}
        )
        colors = {"High": ("#d95b6c", "#fff0f1"), "Medium": ("#c28c18", "#fff7e8"), "Low": ("#299276", "#eaf8f3")}
        color, tint = colors[level]
        st.markdown(
            f'<div class="result-card"><div class="eyebrow">DEMO RESULT</div>'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:.4rem">'
            f'<div><div class="result-score" style="color:{color}">{int(score)}<span style="font-size:1rem;color:#938fa0"> / 100</span></div>'
            f'<div style="font-size:.78rem;color:#77748a;margin-top:.35rem">{explanation}</div></div>'
            f'<span class="risk-chip" style="color:{color};background:{tint}">{level} risk</span></div>'
            f'<div class="result-bar"><div class="result-fill" style="width:{int(score)}%;background:{color}"></div></div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div class="disclaimer"><strong>Educational demo only.</strong> This score is produced by a few hand-written rules, not a validated AI model. Do not use it to approve or decline real payments.</div>', unsafe_allow_html=True)


def render_reports(data: pd.DataFrame) -> None:
    page_header("EXPORTS", "Reports", "Download the cleaned transaction sample with the existing demo scores and explanations.")
    if data.empty:
        st.warning("There are no usable records to include in a report.")
        return
    counts = data["risk_level"].value_counts().reindex(RISK_ORDER, fill_value=0)
    total = len(data)
    col1, col2 = st.columns([1.1, .9], gap="large")
    with col1:
        st.markdown('<div class="section-heading">Sample summary</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"**Distinct transactions:** {total:,}")
            st.markdown(f"**High risk:** {int(counts['High']):,} ({int(counts['High']) / total:.0%})")
            st.markdown(f"**Medium risk:** {int(counts['Medium']):,} ({int(counts['Medium']) / total:.0%})")
            st.markdown(f"**Low risk:** {int(counts['Low']):,} ({int(counts['Low']) / total:.0%})")
            st.markdown("**Data source:** `sample_transactions.csv`")
    with col2:
        st.markdown('<div class="section-heading">Export</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.write("The export includes the cleaned sample rows plus `risk_score`, `risk_level`, and `explanation`.")
            export = data.drop(columns=["_source_order"], errors="ignore").to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download scored transactions CSV",
                data=export,
                file_name="payguard_scored_transactions.csv",
                mime="text/csv",
                type="primary",
                width="stretch",
            )
            st.caption("Exact duplicate records and embedded header rows are excluded from the export.")


def render_about(cleaning_notes: list[str]) -> None:
    page_header("PROJECT NOTES", "About PayGuard AI", "A beginner-friendly payment-risk analysis prototype.")
    left, right = st.columns([1.2, .8], gap="large")
    with left:
        with st.container(border=True):
            st.markdown('<div class="section-heading">What this project does</div>', unsafe_allow_html=True)
            st.write("PayGuard AI reads a local CSV, calculates a demo risk score from a small set of explicit rules, and visualizes the results. The dashboard preserves the original project’s Streamlit, Pandas, and Plotly stack.")
            st.markdown('<div class="section-heading">What it does not do</div>', unsafe_allow_html=True)
            st.write("It does not connect to a bank or payment provider, run real-time fraud monitoring, or use a trained or validated AI model. Its risk labels are educational examples only.")
    with right:
        with st.container(border=True):
            st.markdown('<div class="section-heading">Data preparation</div>', unsafe_allow_html=True)
            st.write("The sample CSV is read from the project directory. Repeated header lines and exact duplicate rows are ignored; missing or invalid numeric inputs are handled without raising the score.")
            if cleaning_notes:
                for note in cleaning_notes:
                    st.caption("• " + note)
            st.markdown('<div class="disclaimer"><strong>Use limitation:</strong> Educational prototype only. Do not use for real payment decisions.</div>', unsafe_allow_html=True)


# The data is loaded once on each Streamlit rerun. All metrics and charts derive
# from this cleaned copy of the project's actual CSV.
transactions, data_notes = load_transactions()

with st.sidebar:
    st.markdown(
        '<div class="brand-wrap"><div class="brand-mark">⌑</div>'
        '<div><div class="brand-name">PayGuard AI</div><div class="brand-caption">PAYMENT RISK ANALYSIS</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-section">Workspace</div>', unsafe_allow_html=True)
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "Dashboard"
    page = st.radio(
        "Navigation",
        ["Dashboard", "Transactions", "Risk Analysis", "Check Transaction", "Reports", "About"],
        key="nav_page",
        label_visibility="collapsed",
    )
    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption("DATA SOURCE")
    st.markdown("**sample_transactions.csv**")
    if transactions.empty:
        st.caption("No usable rows loaded")
    else:
        st.caption(f"{len(transactions):,} distinct transaction records")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="disclaimer" style="background:rgba(255,255,255,.07);border-color:rgba(255,255,255,.12);color:#d1cae7">'
        '<strong>Demo only.</strong> Fictional data and hand-written rules; no bank connection or validated fraud model.</div>',
        unsafe_allow_html=True,
    )

if page == "Dashboard":
    render_dashboard(transactions, data_notes)
elif page == "Transactions":
    render_transactions(transactions)
elif page == "Risk Analysis":
    render_risk_analysis(transactions)
elif page == "Check Transaction":
    render_check_transaction()
elif page == "Reports":
    render_reports(transactions)
else:
    render_about(data_notes)
