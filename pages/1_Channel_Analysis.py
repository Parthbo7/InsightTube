import re
import io
import altair as alt
import streamlit as st
from streamlit_lottie import st_lottie
from services import load_lottieurl, run_full_channel_analysis
from video import get_10_recent_videos
from channel import get_channel_id_from_url, fetch_channel_data
from videodata import fetch_video_analytics
from supabase import create_client
from analytics import calculate_video_metrics, update_channel_avg_engagement
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from sklearn.linear_model import LinearRegression

# ── ReportLab imports ────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, HRFlowable, PageBreak, KeepTogether
)

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InsightTube",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.block-container { padding-top: 2rem; }
[data-testid="stSidebar"] { background-color: #111827; }
.stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; }

/* ── Hero & Input Card ── */
.input-card {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 40px;
    margin: 20px auto;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}
.hero-header {
    font-size: 3rem !important;
    font-weight: 800;
    margin-bottom: 5px;
    background: linear-gradient(135deg, #F8FAFC 0%, #94A3B8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    color: #94A3B8;
    font-size: 1.1rem;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

from components import apply_tab_styling
apply_tab_styling()

subscriber_watch_percent = 0
upload_frequency         = 0
duration_counts          = pd.DataFrame()

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase     = create_client(supabase_url, supabase_key)

st.markdown("""
<div style="text-align: center; margin-top: 20px; animation: fadeIn 0.8s ease-out;">
    <img src="https://cdn-icons-png.flaticon.com/128/7172/7172401.png" width="80" style="margin-bottom: 10px;">
    <h1 class="hero-header">Channel Analysis</h1>
    <p class="hero-subtitle">Analyze channel growth, engagement, and performance insights instantly</p>
</div>
""", unsafe_allow_html=True)

# Main Input Section
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    channel_input = st.text_input("🔍 Enter YouTube Channel Name or URL", placeholder="e.g. 'MrBeast' or UCX6OQ3DkcsbYNE6H8uQQuVA")
    
    st.markdown("""
    <p style="color: #64748B; font-size: 0.9rem; margin-top: -10px; margin-bottom: 20px; text-align: center;">
        <i>Suggestions: MrBeast, Netflix, CarryMinati</i>
    </p>
    """, unsafe_allow_html=True)
    
    analyze_btn = st.button("🚀 Analyze Channel", use_container_width=True, type="primary")

hide_default_sidebar = """
    <style>[data-testid="stSidebarNav"] {display: none;}</style>
"""
st.markdown(hide_default_sidebar, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" width="40">
        <h3 style="margin:0;">InsightTube</h3>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/10307/10307931.png", width=40)
    col2.page_link("Home.py", label="Home")
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/404/404672.png", width=40)
    col2.page_link("pages/1_Channel_Analysis.py", label="Channel Analysis")
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/2593/2593453.png", width=40)
    col2.page_link("pages/5_Sentiment_Analysis.py", label="Sentiment Analysis")
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/934/934478.png", width=40)
    col2.page_link("pages/2_Channel_Compare.py", label="Channel Compare")
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/9227/9227001.png", width=40)
    col2.page_link("pages/4_Trending.py", label="Trending Videos")
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/9985/9985768.png", width=40)
    col2.page_link("pages/3_About_Us.py", label="About Us")


# ═════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def parse_iso_duration(duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match   = re.match(pattern, str(duration))
    if not match:
        return 0
    h  = int(match.group(1)) if match.group(1) else 0
    mn = int(match.group(2)) if match.group(2) else 0
    s  = int(match.group(3)) if match.group(3) else 0
    return h * 3600 + mn * 60 + s


def predict_subscriber_growth(df, current_subscribers):
    if df.empty:
        return current_subscribers, 0
    df = df.sort_values("published_at").reset_index(drop=True)
    df["time_index"] = df.index
    conversion_rate  = 0.005
    df["estimated_sub_growth"] = df["view_count"] * conversion_rate
    X = df["time_index"].values.reshape(-1, 1)
    y = df["estimated_sub_growth"].values
    model = LinearRegression()
    model.fit(X, y)
    future_index      = np.array([[df["time_index"].max() + 5]])
    predicted_growth  = model.predict(future_index)[0]
    predicted_subs    = current_subscribers + predicted_growth
    growth_rate       = (predicted_growth / current_subscribers) * 100
    return int(predicted_subs), growth_rate


def run_full_channel_analysis(channel_input):
    channel_id   = get_channel_id_from_url(channel_input)
    channel_info = fetch_channel_data(channel_id)
    if not channel_info:
        return None, None

    channel_data = {
        "channel_id":       channel_info["channel_id"],
        "channel_name":     channel_info["channel_name"],
        "description":      channel_info["description"],
        "published_at":     channel_info["published_at"],
        "subscriber_count": int(channel_info["subscriber_count"]),
        "view_count":       int(channel_info["view_count"]),
        "video_count":      int(channel_info["video_count"])
    }
    supabase.table("channel_info").upsert(channel_data).execute()

    videos    = get_10_recent_videos(channel_input)
    analytics = fetch_video_analytics(videos)

    subscriber_count = int(channel_info["subscriber_count"])
    cleaned_data     = []
    for video in analytics:
        metrics = calculate_video_metrics(video, subscriber_count)
        cleaned_data.append({
            "video_id":              video["video_id"],
            "channel_id":            channel_id,
            "title":                 video["title"],
            "published_at":          video["published_at"],
            "duration":              video["duration"],
            "view_count":            int(video.get("view_count", 0)),
            "like_count":            int(video.get("like_count", 0)),
            "comment_count":         int(video.get("comment_count", 0)),
            "like_ratio":            metrics["like_ratio"],
            "comment_ratio":         metrics["comment_ratio"],
            "total_engagement_rate": metrics["total_engagement_rate"],
            "view_subscriber_ratio": metrics["view_subscriber_ratio"],
            "engagement_per_1000":   metrics["engagement_per_1000"],
            "like_comment_ratio":    metrics["like_comment_ratio"]
        })

    supabase.table("video_analytics").upsert(cleaned_data).execute()
    update_channel_avg_engagement(supabase, channel_id)

    stored_data = (
        supabase.table("video_analytics")
        .select("*").eq("channel_id", channel_id).execute()
    )
    return channel_info, stored_data.data


# ═════════════════════════════════════════════════════════════════════════════
#  PDF REPORT GENERATOR
# ═════════════════════════════════════════════════════════════════════════════

# ── Colour palette ────────────────────────────────────────────────────────────
_RED        = colors.HexColor("#CC0000")
_RED_MED    = colors.HexColor("#FF6666")
_RED_PALE   = colors.HexColor("#FFCCCC")
_DARK       = colors.HexColor("#0E1117")
_GREY_BG    = colors.HexColor("#F5F5F5")
_GREY_ALT   = colors.HexColor("#FAFAFA")
_GREY_LINE  = colors.HexColor("#DDDDDD")
_TEXT       = colors.HexColor("#1A1A1A")
_TEXT_MID   = colors.HexColor("#555555")
_WHITE      = colors.white
_ACCENT     = colors.HexColor("#FF3333")


def _fig_to_image(fig, w_cm=15, h_cm=7):
    """Save a matplotlib figure to a ReportLab Image object."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return RLImage(buf, width=w_cm * cm, height=h_cm * cm)


def _styles():
    return {
        "h_cover": ParagraphStyle(
            "h_cover", fontSize=30, textColor=_WHITE,
            fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4),
        "sub_cover": ParagraphStyle(
            "sub_cover", fontSize=14, textColor=_RED_PALE,
            fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4),
        "date_cover": ParagraphStyle(
            "date_cover", fontSize=9, textColor=colors.HexColor("#AAAAAA"),
            fontName="Helvetica", alignment=TA_CENTER),
        "section": ParagraphStyle(
            "section", fontSize=13, textColor=_RED,
            fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4),
        "body": ParagraphStyle(
            "body", fontSize=9, textColor=_TEXT,
            fontName="Helvetica", spaceAfter=3, leading=14),
        "body_b": ParagraphStyle(
            "body_b", fontSize=9, textColor=_TEXT,
            fontName="Helvetica-Bold", spaceAfter=3),
        "insight": ParagraphStyle(
            "insight", fontSize=9, textColor=_TEXT,
            fontName="Helvetica", leading=14,
            leftIndent=8, rightIndent=8,
            spaceAfter=5, spaceBefore=3,
            backColor=colors.HexColor("#FFF5F5"),
            borderColor=_RED_MED, borderWidth=1, borderPad=6),
        "footer": ParagraphStyle(
            "footer", fontSize=7, textColor=_TEXT_MID,
            fontName="Helvetica", alignment=TA_CENTER),
        "th": ParagraphStyle(
            "th", fontSize=8, textColor=_WHITE,
            fontName="Helvetica-Bold", alignment=TA_CENTER),
        "td": ParagraphStyle(
            "td", fontSize=7.5, textColor=_TEXT,
            fontName="Helvetica"),
        "td_r": ParagraphStyle(
            "td_r", fontSize=7.5, textColor=_TEXT,
            fontName="Helvetica", alignment=TA_RIGHT),
    }


def _metric_row(pairs, ncols=3):
    """Render a row of metric boxes."""
    rows  = [pairs[i:i+ncols] for i in range(0, len(pairs), ncols)]
    tdata = []
    for row in rows:
        cells = []
        for label, value in row:
            cells.append(Paragraph(
                f"<font size='8' color='#555555'>{label}</font><br/>"
                f"<font size='14' color='#CC0000'><b>{value}</b></font>",
                ParagraphStyle("mc", alignment=TA_CENTER, fontName="Helvetica")))
        while len(cells) < ncols:
            cells.append(Paragraph("", ParagraphStyle("mc")))
        tdata.append(cells)
    cw = 16 * cm / ncols
    t  = Table(tdata, colWidths=[cw] * ncols)
    t.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.5, _GREY_LINE),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, _GREY_LINE),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [_GREY_BG, _GREY_ALT]),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def _hr():
    return HRFlowable(width="100%", thickness=1, color=_RED_MED, spaceAfter=6)


# ── matplotlib chart builders ────────────────────────────────────────────────

def _chart_views(df):
    sdf    = df.sort_values("view_count", ascending=False).head(20)
    labels = [t[:28] + "…" if len(t) > 28 else t for t in sdf["title"]]
    fig, ax = plt.subplots(figsize=(12, 4.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")
    bars = ax.bar(range(len(labels)), sdf["view_count"],
                  color="#CC0000", edgecolor="#8B0000", linewidth=0.6, width=0.65)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h * 1.01,
                f"{int(h):,}", ha="center", va="bottom", fontsize=5.5, color="#333")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=6.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_ylabel("Views", fontsize=9)
    ax.set_title("Views per Video", fontsize=11, fontweight="bold", color="#CC0000", pad=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _fig_to_image(fig, 15, 6.5)


def _chart_likes_comments(df):
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")
    x = range(len(df))
    ax.fill_between(x, df["like_count"], alpha=0.15, color="#FF0000")
    ax.plot(x, df["like_count"],    color="#FF0000", linewidth=2.2, label="Likes",    marker="o", markersize=4)
    ax.fill_between(x, df["comment_count"], alpha=0.12, color="#8B0000")
    ax.plot(x, df["comment_count"], color="#8B0000", linewidth=2.2, label="Comments", marker="s", markersize=4)
    ax.set_xlabel("Video Index", fontsize=9)
    ax.set_ylabel("Count", fontsize=9)
    ax.set_title("Likes & Comments per Video", fontsize=11, fontweight="bold", color="#CC0000", pad=10)
    ax.legend(fontsize=8, framealpha=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _fig_to_image(fig, 15, 5.5)


def _chart_engagement_gauge(value, max_val, title, suffix=""):
    fig, ax = plt.subplots(figsize=(5, 3.2), subplot_kw=dict(aspect="equal"))
    fig.patch.set_facecolor("white")
    theta_bg  = np.linspace(np.pi, 0, 300)
    ax.plot(np.cos(theta_bg), np.sin(theta_bg), color="#FFCCCC", linewidth=18, solid_capstyle="round", zorder=1)
    frac     = min(max(value / max_val, 0), 1.0)
    end_ang  = np.pi - frac * np.pi
    theta_v  = np.linspace(np.pi, end_ang, 300)
    grad_cols = ["#FF6666", "#CC0000"]
    for i in range(len(theta_v) - 1):
        t = i / max(len(theta_v) - 1, 1)
        r, g, b = [int(a + (b - a) * t) for a, b in
                   zip((255, 102, 102), (204, 0, 0))]
        ax.plot(np.cos(theta_v[i:i+2]), np.sin(theta_v[i:i+2]),
                color=f"#{r:02x}{g:02x}{b:02x}", linewidth=18, solid_capstyle="butt", zorder=2)
    needle_angle = np.pi - frac * np.pi
    ax.annotate("", xy=(0.7 * np.cos(needle_angle), 0.7 * np.sin(needle_angle)),
                xytext=(0, 0), zorder=3,
                arrowprops=dict(arrowstyle="-|>", color="#1A1A1A", lw=2.2))
    ax.plot(0, 0, "o", color="#1A1A1A", markersize=9, zorder=4)
    ax.text(0, -0.3, f"{value:.1f}{suffix}", ha="center", va="center",
            fontsize=20, fontweight="bold", color="#CC0000")
    ax.text(0, -0.52, title, ha="center", va="center", fontsize=8, color="#555555")
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-0.7, 1.3); ax.axis("off")
    fig.tight_layout(pad=0.3)
    return _fig_to_image(fig, 7.5, 5.5)


def _chart_duration_pie(df):
    def cat(d):
        s = parse_iso_duration(d)
        return "Short (<2 min)" if s < 120 else ("Medium (2–10 min)" if s <= 600 else "Long (>10 min)")
    df = df.copy(); df["_c"] = df["duration"].apply(cat)
    counts  = df["_c"].value_counts()
    palette = ["#FFCCCC", "#FF6666", "#CC0000", "#8B0000"]
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    fig.patch.set_facecolor("white")
    wedges, texts, autos = ax.pie(
        counts.values, labels=counts.index, autopct="%1.1f%%",
        colors=palette[:len(counts)], startangle=140,
        wedgeprops=dict(edgecolor="white", linewidth=2),
        pctdistance=0.75)
    for t in texts:  t.set_fontsize(8)
    for a in autos:  a.set_fontsize(8); a.set_color("white"); a.set_fontweight("bold")
    # donut
    centre = plt.Circle((0, 0), 0.45, color="white")
    ax.add_patch(centre)
    ax.set_title("Duration Distribution", fontsize=11, fontweight="bold", color="#CC0000", pad=10)
    fig.tight_layout()
    return _fig_to_image(fig, 7.5, 5.5)


def _chart_duration_bar(df):
    df = df.copy().sort_values("published_at").reset_index(drop=True)
    df["dur_min"] = df["duration"].apply(lambda x: parse_iso_duration(x) / 60)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    fig.patch.set_facecolor("white"); ax.set_facecolor("#FAFAFA")
    cmap  = plt.cm.Reds
    norms = (df["dur_min"] - df["dur_min"].min()) / (df["dur_min"].max() - df["dur_min"].min() + 1e-9)
    cols  = [cmap(0.4 + 0.6 * n) for n in norms]
    ax.bar(df.index + 1, df["dur_min"], color=cols, edgecolor="#8B0000", linewidth=0.4)
    ax.set_xlabel("Video Index", fontsize=9); ax.set_ylabel("Duration (min)", fontsize=9)
    ax.set_title("Duration by Upload Order", fontsize=11, fontweight="bold", color="#CC0000", pad=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _fig_to_image(fig, 7.5, 5.5)


def _chart_upload_freq(upload_freq):
    fig, ax = plt.subplots(figsize=(8, 3.5), subplot_kw=dict(aspect="equal"))
    fig.patch.set_facecolor("white")
    theta_bg = np.linspace(np.pi, 0, 300)
    ax.plot(np.cos(theta_bg), np.sin(theta_bg), color="#FFCCCC", linewidth=18, solid_capstyle="round")
    frac    = min(upload_freq / 20, 1.0)
    end_ang = np.pi - frac * np.pi
    theta_v = np.linspace(np.pi, end_ang, 300)
    ax.plot(np.cos(theta_v), np.sin(theta_v), color="#CC0000", linewidth=18, solid_capstyle="round")
    needle = np.pi - frac * np.pi
    ax.annotate("", xy=(0.7 * np.cos(needle), 0.7 * np.sin(needle)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="#1A1A1A", lw=2.2))
    ax.plot(0, 0, "o", color="#1A1A1A", markersize=9)
    ax.text(0, -0.3, f"{upload_freq:.1f}", ha="center", va="center",
            fontsize=20, fontweight="bold", color="#CC0000")
    ax.text(0, -0.52, "Uploads / Month", ha="center", fontsize=8, color="#555")
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-0.7, 1.3); ax.axis("off")
    fig.tight_layout(pad=0.3)
    return _fig_to_image(fig, 9, 5.5)


def _chart_revenue(df):
    df = df.copy()
    avg_cpm = (3 + 10) / 2 * 90
    df["_rev"] = df["view_count"].apply(lambda v: round(v * 0.55 / 1000 * avg_cpm, 2))
    sdf    = df.sort_values("_rev", ascending=False).head(20)
    labels = [t[:28] + "…" if len(t) > 28 else t for t in sdf["title"]]
    fig, ax = plt.subplots(figsize=(12, 4.5))
    fig.patch.set_facecolor("white"); ax.set_facecolor("#FAFAFA")
    bars = ax.bar(range(len(labels)), sdf["_rev"],
                  color="#CC0000", edgecolor="#8B0000", linewidth=0.6, width=0.65)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h * 1.01,
                f"₹{int(h):,}", ha="center", va="bottom", fontsize=5.5, color="#333")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=6.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{int(x):,}"))
    ax.set_ylabel("Revenue (INR)", fontsize=9)
    ax.set_title("Estimated Revenue per Video (INR)", fontsize=11,
                 fontweight="bold", color="#CC0000", pad=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _fig_to_image(fig, 15, 6.5)


def _chart_growth(current_subs, predicted_subs):
    stages = ["Current Subscribers", "Predicted (30 Days)"]
    vals   = [current_subs, predicted_subs]
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor("white"); ax.set_facecolor("#FAFAFA")
    bars = ax.bar(stages, vals, color=["#FF6666", "#CC0000"], width=0.45,
                  edgecolor="#8B0000", linewidth=0.8)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(vals) * 0.015,
                f"{v:,}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_title("Subscriber Growth Prediction", fontsize=11,
                 fontweight="bold", color="#CC0000", pad=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _fig_to_image(fig, 9, 5.5)


def _video_table(df, S):
    cols = ["title", "view_count", "like_count", "comment_count",
            "total_engagement_rate", "engagement_per_1000", "estimated_revenue"]
    hdrs = ["Video Title", "Views", "Likes", "Comments", "Eng. Rate %", "Eng./1000", "Rev. (₹)"]
    tdata = [[Paragraph(f"<b><font color='white'>{h}</font></b>",
                        ParagraphStyle("th", alignment=TA_CENTER,
                                       fontName="Helvetica-Bold", fontSize=7))
              for h in hdrs]]
    for _, row in df.iterrows():
        title = str(row.get("title", ""))
        title = title[:38] + "…" if len(title) > 38 else title
        rev   = row.get("estimated_revenue", 0)
        tdata.append([
            Paragraph(title, ParagraphStyle("td", fontSize=7, fontName="Helvetica")),
            Paragraph(f"{int(row.get('view_count',0)):,}",
                      ParagraphStyle("tdr", fontSize=7, fontName="Helvetica", alignment=TA_RIGHT)),
            Paragraph(f"{int(row.get('like_count',0)):,}",
                      ParagraphStyle("tdr", fontSize=7, fontName="Helvetica", alignment=TA_RIGHT)),
            Paragraph(f"{int(row.get('comment_count',0)):,}",
                      ParagraphStyle("tdr", fontSize=7, fontName="Helvetica", alignment=TA_RIGHT)),
            Paragraph(f"{float(row.get('total_engagement_rate',0)):.2f}%",
                      ParagraphStyle("tdr", fontSize=7, fontName="Helvetica", alignment=TA_RIGHT)),
            Paragraph(f"{float(row.get('engagement_per_1000',0)):.2f}",
                      ParagraphStyle("tdr", fontSize=7, fontName="Helvetica", alignment=TA_RIGHT)),
            Paragraph(f"₹{float(rev):,.0f}",
                      ParagraphStyle("tdr", fontSize=7, fontName="Helvetica", alignment=TA_RIGHT)),
        ])
    cw = [5.8*cm, 1.9*cm, 1.7*cm, 1.8*cm, 1.8*cm, 1.7*cm, 1.7*cm]
    t  = Table(tdata, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  _RED),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [_WHITE, _GREY_BG]),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, _GREY_LINE),
        ("BOX",           (0, 0), (-1, -1), 0.5, _GREY_LINE),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ]))
    return t


def _section(title, S):
    return [
        Paragraph(title, S["section"]),
        _hr(),
    ]


def _side_by_side(left, right):
    t = Table([[left, right]], colWidths=[8 * cm, 8 * cm])
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


# ── Main PDF builder ─────────────────────────────────────────────────────────

def generate_pdf_report(channel_info, video_analytics, df, predicted_subs,
                         growth_rate, upload_frequency, duration_counts,
                         subscriber_watch_percent, avg_engagement,
                         low_estimate, high_estimate, rpm, insights):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2.5*cm,
        title=f"YouTube Analytics — {channel_info.get('channel_name','')}",
        author="InsightTube"
    )
    S     = _styles()
    story = []

    # ── PAGE 1: Cover ─────────────────────────────────────────────────────────
    banner = Table([[
        Paragraph(
            "<br/><br/>"
            "<font size='11' color='#FF6666'>INSIGHTTUBE  •  YOUTUBE ANALYTICS</font><br/><br/>"
            f"<font size='26'><b>{channel_info.get('channel_name','Channel')}</b></font><br/><br/>"
            "<font size='11' color='#FFCCCC'>Channel Performance Report</font><br/><br/>",
            ParagraphStyle("cv", fontSize=24, textColor=_WHITE,
                           fontName="Helvetica-Bold", alignment=TA_CENTER))
    ]], colWidths=[16*cm])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _DARK),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 28),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 28),
        ("ROUNDEDCORNERS", [10]),
    ]))
    story.append(banner)
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y  •  %H:%M')}",
        S["date_cover"]))
    story.append(Spacer(1, 0.8*cm))

    story += _section("Channel Overview", S)
    story.append(_metric_row([
        ("Subscribers",  f"{int(channel_info['subscriber_count']):,}"),
        ("Total Views",  f"{int(channel_info['view_count']):,}"),
        ("Total Videos", str(channel_info['video_count'])),
    ]))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        f"<b>Channel ID:</b>  {channel_info.get('channel_id','—')}  &nbsp;&nbsp; "
        f"<b>Published:</b>  {channel_info.get('published_at','—')[:10]}", S["body"]))
    desc = str(channel_info.get("description",""))[:280]
    if desc:
        story.append(Paragraph(f"<b>Description:</b> {desc}…", S["body"]))

    story.append(PageBreak())

    # ── PAGE 2: Views + Likes/Comments ────────────────────────────────────────
    story += _section("1.  Views per Video", S)
    story.append(_chart_views(df))
    story.append(Spacer(1, 0.5*cm))

    story += _section("2.  Likes & Comments per Video", S)
    story.append(_chart_likes_comments(df))
    story.append(PageBreak())

    # ── PAGE 3: Engagement gauges ─────────────────────────────────────────────
    story += _section("3.  Engagement Metrics", S)
    g1 = _chart_engagement_gauge(avg_engagement, 200, "Avg Engagement / 1000 Views")
    g2 = _chart_engagement_gauge(subscriber_watch_percent, 100,
                                  "Subscriber Watch %", suffix="%")
    story.append(_side_by_side(g1, g2))
    story.append(Spacer(1, 0.3*cm))
    story.append(_metric_row([
        ("Avg Engagement / 1000", f"{avg_engagement:.2f}"),
        ("Subscriber Watch %",    f"{subscriber_watch_percent:.1f}%"),
    ], ncols=2))
    story.append(Spacer(1, 0.5*cm))

    # ── Duration ──────────────────────────────────────────────────────────────
    story += _section("4.  Video Duration Analysis", S)
    dp = _chart_duration_pie(df)
    db = _chart_duration_bar(df)
    story.append(_side_by_side(dp, db))
    story.append(PageBreak())

    # ── PAGE 4: Upload Frequency ──────────────────────────────────────────────
    story += _section("5.  Upload Frequency", S)
    uf_img = _chart_upload_freq(upload_frequency)

    def _classify(f):
        if f < 1:   return "😴 Inactive"
        elif f < 4: return "🎥 Casual"
        elif f < 8: return "📈 Consistent"
        else:       return "🔥 Highly Active"

    story.append(_metric_row([
        ("Uploads / Month", f"{upload_frequency:.2f}"),
        ("Creator Type",    _classify(upload_frequency)),
    ], ncols=2))
    story.append(Spacer(1, 0.3*cm))
    uf_tbl = Table([[uf_img]], colWidths=[16*cm])
    uf_tbl.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(uf_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── Revenue ───────────────────────────────────────────────────────────────
    story += _section("6.  Revenue Estimation (INR)", S)
    story.append(_metric_row([
        ("Revenue Estimate (Low)",  f"₹{low_estimate:,.0f}"),
        ("Revenue Estimate (High)", f"₹{high_estimate:,.0f}"),
        ("RPM per 1000 Views",      f"₹{rpm:,.0f}"),
    ]))
    story.append(Spacer(1, 0.3*cm))
    story.append(_chart_revenue(df))
    story.append(PageBreak())

    # ── PAGE 5: Best Video + Growth ───────────────────────────────────────────
    story += _section("7.  Best Performing Video", S)
    df2 = df.copy()
    for col in ["total_engagement_rate","engagement_per_1000","view_subscriber_ratio"]:
        if col not in df2.columns: df2[col] = 0.0
    df2["_perf"] = (
        df2["total_engagement_rate"] * 0.4 +
        df2["engagement_per_1000"]   * 0.3 +
        df2["view_subscriber_ratio"] * 0.3
    )
    best = df2.loc[df2["_perf"].idxmax()]
    bdata = [
        [Paragraph("<b>Metric</b>",
                   ParagraphStyle("th2", fontName="Helvetica-Bold", fontSize=9)),
         Paragraph("<b>Value</b>",
                   ParagraphStyle("th2", fontName="Helvetica-Bold", fontSize=9))],
        ["Title",            str(best.get("title",""))],
        ["Published",        str(best.get("published_at",""))[:10]],
        ["Views",            f"{int(best.get('view_count',0)):,}"],
        ["Likes",            f"{int(best.get('like_count',0)):,}"],
        ["Comments",         f"{int(best.get('comment_count',0)):,}"],
        ["Engagement Rate",  f"{float(best.get('total_engagement_rate',0)):.2f}%"],
        ["Performance Score",f"{float(best.get('_perf',0)):.2f}"],
    ]
    bt = Table(bdata, colWidths=[4.5*cm, 11.5*cm])
    bt.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), _RED),
        ("TEXTCOLOR",     (0, 0), (-1, 0), _WHITE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [_WHITE, _GREY_BG]),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, _GREY_LINE),
        ("BOX",           (0, 0), (-1, -1), 0.5, _GREY_LINE),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(bt)
    story.append(Spacer(1, 0.5*cm))

    # Growth
    story += _section("8.  Subscriber Growth Prediction (30 Days)", S)
    current_subs = int(channel_info["subscriber_count"])
    story.append(_metric_row([
        ("Current Subscribers",   f"{current_subs:,}"),
        ("Predicted (30 Days)",   f"{predicted_subs:,}"),
        ("Estimated Growth Rate", f"{growth_rate:.2f}%"),
    ]))
    story.append(Spacer(1, 0.3*cm))
    gc     = _chart_growth(current_subs, predicted_subs)
    gc_tbl = Table([[gc]], colWidths=[16*cm])
    gc_tbl.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")]))
    story.append(gc_tbl)
    story.append(PageBreak())

    # ── PAGE 6: Insights + Table ──────────────────────────────────────────────
    story += _section("9.  Channel Insights & Strategy", S)
    for ins in insights:
        story.append(Paragraph(ins, S["insight"]))
        story.append(Spacer(1, 0.1*cm))
    story.append(Spacer(1, 0.4*cm))

    story += _section("10.  Video Analytics Data", S)
    story.append(_video_table(df, S))

    # Footer
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=_GREY_LINE))
    story.append(Paragraph(
        "Report generated by InsightTube  •  "
        f"Data as of {datetime.now().strftime('%Y-%m-%d')}  •  "
        "Revenue estimates use industry average CPM. For informational purposes only.",
        S["footer"]))

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN DISPLAY FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

def run_full_channel_analysis_and_display(channel_input):
    import plotly.express as px
    import plotly.graph_objects as go
    
    # shared state variables captured for PDF
    _sub_watch_pct   = 0
    _upload_freq     = 0
    _dur_counts      = pd.DataFrame()
    _avg_engagement  = 0
    _low_est         = 0
    _high_est        = 0
    _rpm             = 0
    _insights        = []
    _predicted_subs  = 0
    _growth_rate     = 0.0

    lottie_loading = load_lottieurl("https://lottie.host/85265451-f761-4696-8566-733d0144f6f4/1p1Y6Y6p1p.json")
    
    with st.spinner("Analyzing channel... This may take a moment."):
        if lottie_loading:
            st_lottie(lottie_loading, height=200, key="loading")
        channel_info, video_analytics = run_full_channel_analysis(channel_input)

    if not channel_info:
        st.error("Failed to fetch channel data. Please check the URL or ID and try again.")
        return

    channel_name = channel_info["channel_name"]
    channel_id   = channel_info["channel_id"]
    channel_url  = f"https://www.youtube.com/channel/{channel_id}"

    st.title(f"Channel: [{channel_name}]({channel_url})")

    # ── Build dataframe ───────────────────────────────────────────────────────
    if video_analytics:
        df = pd.DataFrame(video_analytics)
    else:
        st.warning("No video analytics data found.")
        return

    if df.empty:
        st.warning("No video analytics data found.")
        return

    # Data prep
    df["published_at"] = pd.to_datetime(df["published_at"])
    df = df.sort_values("published_at").reset_index(drop=True)
    
    # ── Tabbed Layout ─────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🎬 Video Performance", "💰 Revenue & Growth", "🧠 AI Insights"])

    with tab1:
        # Original Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Subscribers", f"{int(channel_info['subscriber_count']):,}")
        col2.metric("Total Views",  f"{int(channel_info['view_count']):,}")
        col3.metric("Total Videos", channel_info["video_count"])

        st.divider()
        col_desc, col_date = st.columns(2)
        with col_desc:
            st.markdown(f"""
            <div style="background-color: #1f2937; padding: 20px; border-radius: 10px; height: 100%;">
                <h4 style="margin-top: 0;">📝 Description</h4>
                <p style="font-size: 0.9rem;">{channel_info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        with col_date:
            st.markdown(f"""
            <div style="background-color: #1f2937; padding: 20px; border-radius: 10px; height: 100%;">
                <h4 style="margin-top: 0;">📅 Channel Info</h4>
                <p><b>Published At:</b> {channel_info['published_at'].strftime('%Y-%m-%d') if hasattr(channel_info['published_at'], 'strftime') else channel_info['published_at']}</p>
                <p><b>Channel ID:</b> {channel_id}</p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        
        # Original Engagement Gauges
        top_10_df        = df.sort_values(by="view_count", ascending=False).head(10)
        _avg_engagement  = top_10_df["engagement_per_1000"].mean()
        
        try:
            average_views    = float(df["view_count"].mean())
            total_subs       = int(channel_info["subscriber_count"])
            _sub_watch_pct   = (average_views / total_subs * 100) if total_subs > 0 else 0
        except (ValueError, TypeError):
            _sub_watch_pct = 0

        st.subheader("Gauge Metrics (Original)")
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            fig_eng = go.Figure(go.Indicator(
                mode="gauge+number", value=_avg_engagement,
                title={"text": "Engagement / 1000 Views", "font": {"size": 18, "color": "#E2E8F0"}},
                gauge={"axis": {"range": [0, 200]}, "bar": {"color": "#6366F1"},
                       "steps": [{"range": [0,50], "color": "rgba(99, 102, 241, 0.1)"},
                                  {"range": [50,100], "color": "rgba(99, 102, 241, 0.3)"},
                                  {"range": [100,150], "color": "rgba(99, 102, 241, 0.6)"},
                                  {"range": [150,200], "color": "rgba(99, 102, 241, 0.9)"}]}))
            fig_eng.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=300, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_eng, use_container_width=True)

        with g_col2:
            fig_subs = go.Figure(go.Indicator(
                mode="gauge+number", value=_sub_watch_pct,
                number={"suffix": "%"},
                title={"text": "Subscriber Watch %", "font": {"size": 18, "color": "#E2E8F0"}},
                gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#10B981"},
                       "steps": [{"range": [0,20], "color": "rgba(16, 185, 129, 0.1)"},
                                  {"range": [20,40], "color": "rgba(16, 185, 129, 0.3)"},
                                  {"range": [40,60], "color": "rgba(16, 185, 129, 0.6)"},
                                  {"range": [60,80], "color": "rgba(16, 185, 129, 0.9)"},
                                  {"range": [80,100], "color": "#10B981"}]}))
            fig_subs.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=300, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_subs, use_container_width=True)

        st.divider()
        # New Chart: Viewer Journey Funnel 
        st.subheader("Viewer Journey Funnel ")
        total_views_f = df["view_count"].sum()
        total_engagements_f = df["like_count"].sum() + df["comment_count"].sum()
        impressions_f = total_views_f / 0.05 if total_views_f > 0 else 0
        fig_funnel = go.Figure(go.Funnel(
            y=["Estimated Impressions", "Views", "Engagements"],
            x=[impressions_f, total_views_f, total_engagements_f],
            textinfo="value+percent initial",
            marker={"color": ["#4F46E5", "#6366F1", "#818CF8"]}
        ))
        fig_funnel.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=20, b=0), height=300)
        st.plotly_chart(fig_funnel, use_container_width=True)


    with tab2:
        st.subheader("📊 Performance Trends")
        
        # New Chart: Views Over Time Area Chart
        st.markdown("##### Views Over Time ")
        fig_area = px.area(
            df, x="published_at", y="view_count",
            hover_data={"title": True},
            color_discrete_sequence=["#6366F1"],
        )
        fig_area.update_traces(fillcolor="rgba(99, 102, 241, 0.2)", line=dict(width=3, shape="spline"))
        fig_area.update_layout(
            xaxis_title="", yaxis_title="Views",
            template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=300,
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_area, use_container_width=True)
        st.divider()

        # Original Views per Video Chart (Enhanced styling)
        st.markdown("##### Top 15 Most Viewed Videos (Original)")
        df_views = df.sort_values(by="view_count", ascending=False).head(15).copy()
        df_views["short_title"] = df_views["title"].apply(lambda x: x[:40] + "..." if len(x) > 40 else x)
        df_views = df_views.iloc[::-1]  # Reverse for Plotly horizontal sorting
        
        avg_views = df["view_count"].mean()

        fig_views = px.bar(
            df_views,
            x="view_count",
            y="short_title",
            orientation="h",
            hover_data={"title": True, "short_title": False, "view_count": ":,"},
            color="view_count",
            color_continuous_scale=px.colors.sequential.Teal,
            text_auto=".2s"
        )
        
        fig_views.add_vline(
            x=avg_views, 
            line_dash="dash", 
            line_color="#10B981", 
            annotation_text="Avg Views", 
            annotation_position="bottom right"
        )
        
        fig_views.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
        fig_views.update_layout(
            xaxis_title="Total Views",
            yaxis_title="",
            height=500,
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            margin=dict(l=10, r=40, t=10, b=20),
            font=dict(size=13, color="#e2e8f0"),
            bargap=0.2
        )
        st.plotly_chart(fig_views, use_container_width=True)
        
        # Original Likes and Comments Chart (Enhanced styling)
        st.markdown("##### Likes & Comments (Original)")
        df_lc = df.sort_values(by="published_at", ascending=False).head(20).copy().reset_index(drop=True)
        fig_lc = go.Figure()
        fig_lc.add_trace(go.Scatter(x=df_lc.index + 1, y=df_lc["like_count"], name="Likes", line=dict(color="#10B981", width=3, shape="spline"), mode='lines+markers', text=df_lc["title"], hoverinfo="text+y+name"))
        fig_lc.add_trace(go.Scatter(x=df_lc.index + 1, y=df_lc["comment_count"], name="Comments", line=dict(color="#6366F1", width=3, shape="spline"), mode='lines+markers', text=df_lc["title"], hoverinfo="text+y+name"))
        fig_lc.update_layout(xaxis_title="Recent Video Order (1 = Newest)", yaxis_title="Count", height=400, template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_lc, use_container_width=True)

        st.divider()
        
        # Original Duration Insights Section
        st.subheader("⏳ Duration Insights")
        
        def categorize_duration(d):
            s = parse_iso_duration(d)
            if s < 120:   return "Short (<2 min)"
            elif s <= 600: return "Medium (1–10 min)"
            else:          return "Long (>10 min)"

        df["duration_category"] = df["duration"].apply(categorize_duration)
        _dur_counts = df["duration_category"].value_counts().reset_index()
        _dur_counts.columns = ["Category", "Count"]

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            # Original Pie Chart (Enhanced to Donut)
            fig_pie = go.Figure(data=[go.Pie(
                labels=_dur_counts["Category"], values=_dur_counts["Count"],
                hole=0.6,
                marker=dict(colors=["#14B8A6", "#0EA5E9", "#6366F1"]))])
            fig_pie.update_layout(title="Duration Distribution (Original)", height=350, template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with d_col2:
            # Original Line Chart (Enhanced curves)
            df_dur = df.sort_values("published_at", ascending=False).head(20).copy().reset_index(drop=True)
            df_dur["duration_minutes"] = df_dur["duration"].apply(lambda x: parse_iso_duration(x) / 60 if pd.notnull(x) else 0)
            fig_dur = go.Figure(data=[
                go.Scatter(x=df_dur.index + 1, y=df_dur["duration_minutes"], marker_color="#8B5CF6", line=dict(shape="spline", width=3), mode='lines+markers', text=df_dur["title"], hoverinfo="text+y")
            ])
            fig_dur.update_layout(title="Duration Trend (Last 20 Videos - Original)", xaxis_title="Recent Video Order (1 = Newest)", yaxis_title="Minutes", height=350, template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_dur, use_container_width=True)

        # New Chart: Duration vs Engagement Scatter
        st.markdown("##### Duration vs Engagement Correlation")
        df_scatter = df.copy()
        df_scatter["duration_minutes"] = df_scatter["duration"].apply(lambda x: parse_iso_duration(x) / 60 if pd.notnull(x) else 0)
        fig_scatter = px.scatter(
            df_scatter, x="duration_minutes", y="total_engagement_rate",
            size="view_count", color="total_engagement_rate",
            hover_data={"title": True},
            color_continuous_scale=px.colors.sequential.Teal,
            size_max=30
        )
        fig_scatter.update_layout(
            xaxis_title="Duration (Minutes)", yaxis_title="Engagement Rate (%)",
            template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False,
            height=350,
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.divider()
        st.subheader("📜 Recent Video Analytics")
        st.data_editor(
            df.reset_index(drop=True),
            column_config={
                "title": "Video Title",
                "published_at": st.column_config.DateColumn("Published Date", format="MMM DD, YYYY"),
                "view_count": st.column_config.NumberColumn("Views", format="%d 👀"),
                "like_count": st.column_config.NumberColumn("Likes", format="%d 👍"),
                "comment_count": st.column_config.NumberColumn("Comments", format="%d 💬"),
                "total_engagement_rate": st.column_config.ProgressColumn("Eng. Rate (%)", format="%.2f", min_value=0, max_value=20),
                "engagement_per_1000": st.column_config.NumberColumn("Eng./1000", format="%.2f"),
                "view_subscriber_ratio": st.column_config.NumberColumn("VSR", format="%.2f %%"),
            },
            hide_index=True,
            use_container_width=True,
            disabled=True
        )

    with tab3:
        st.subheader("💰 Revenue Estimation (INR)")
        
        def estimate_revenue(views, cpm, rate=0.55):
            return round(views * rate / 1000 * cpm, 2)

        USD_TO_INR   = 90
        cpm_low      = 3  * USD_TO_INR
        cpm_high     = 10 * USD_TO_INR
        avg_cpm      = (cpm_low + cpm_high) / 2

        if not df.empty and "view_count" in df.columns:
            total_views   = df["view_count"].sum()
            _low_est      = estimate_revenue(total_views, cpm_low)
            _high_est     = estimate_revenue(total_views, cpm_high)
            _rpm          = avg_cpm * 0.55
            df["estimated_revenue"] = df["view_count"].apply(lambda v: estimate_revenue(v, avg_cpm))

            r_col1, r_col2, r_col3 = st.columns(3)
            r_col1.metric("Revenue Estimate (Low)", f"₹ {_low_est:,.2f}")
            r_col2.metric("Revenue Estimate (High)", f"₹ {_high_est:,.2f}")
            r_col3.metric("RPM (Avg)", f"₹ {_rpm:,.2f}")
            
            df_rev = df.sort_values("estimated_revenue", ascending=False).head(15).copy()
            df_rev["short_title"] = df_rev["title"].apply(lambda x: x[:35] + "..." if len(x) > 35 else x)
            df_rev = df_rev.iloc[::-1]

            # Original Revenue Chart (Enhanced colors)
            fig_rev = px.bar(
                df_rev, 
                x="estimated_revenue", 
                y="short_title", 
                orientation="h",
                hover_data={"title": True, "short_title": False, "estimated_revenue": ":,.2f"},
                color="estimated_revenue",
                color_continuous_scale=px.colors.sequential.Purples,
                text_auto=".2s"
            )
            fig_rev.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
            fig_rev.update_layout(
                title="Top 15 Videos by Revenue (₹) (Original)", 
                xaxis_title="Estimated Revenue (₹)", 
                yaxis_title="", 
                height=500, 
                template="plotly_dark", 
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                margin=dict(l=10, r=40, t=50, b=20),
                font=dict(size=13)
            )
            st.plotly_chart(fig_rev, use_container_width=True)

        st.divider()
        st.subheader("📈 Subscriber Growth Prediction")
        current_subs = int(channel_info["subscriber_count"])
        _predicted_subs, _growth_rate = predict_subscriber_growth(df, current_subs)

        g_col1, g_col2, g_col3 = st.columns(3)
        g_col1.metric("Current", f"{current_subs:,}")
        g_col2.metric("Predicted (30 Days)", f"{_predicted_subs:,}")
        g_col3.metric("Growth Rate", f"{_growth_rate:.2f}%")
        
        # Original Growth Chart
        fig_growth = go.Figure(data=[
            go.Bar(x=["Current", "Predicted (30 Days)"], y=[current_subs, _predicted_subs], marker_color=["#6366F1", "#10B981"], marker_line_width=0)
        ])
        fig_growth.update_layout(title="Growth Prediction (Original)", height=400, template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_growth, use_container_width=True)

    with tab4:
        st.subheader("🧠 AI Insights & Strategy")
        
        # Calculate insights
        avg_engagement_rate = df["total_engagement_rate"].mean()
        avg_views_val       = df["view_count"].mean()
        top_views_val       = df["view_count"].max()
        
        # Upload Frequency
        try:
            total_videos  = int(channel_info["video_count"])
            published_dt  = pd.to_datetime(channel_info["published_at"][:10]).date()
            current_date  = datetime.now().date()
            channel_age_months = max(1, (current_date.year - published_dt.year) * 12 + (current_date.month - published_dt.month))
            _upload_freq = total_videos / channel_age_months
        except: _upload_freq = 0

        if avg_engagement_rate > 8: _insights.append("🔥 Excellent engagement rate. Audience is highly interactive.")
        elif avg_engagement_rate > 4: _insights.append("📈 Good engagement. There is room for stronger CTAs.")
        else: _insights.append("⚠️ Low engagement. Improve thumbnails, hooks, and call-to-actions.")

        if _sub_watch_pct > 40: _insights.append("💪 Strong subscriber loyalty. Majority of subscribers actively watch.")
        elif _sub_watch_pct > 20: _insights.append("🤝 Moderate subscriber watching pattern.")
        else: _insights.append("❗ Many subscribers are inactive. Focus on retention strategies.")

        if _upload_freq >= 8: _insights.append("🔥 Highly active creator. Algorithm favors this consistency.")
        elif _upload_freq >= 4: _insights.append("📅 Good upload consistency.")
        else: _insights.append("😴 Upload frequency is low. Increase consistency to grow faster.")

        for insight in _insights:
            st.info(insight)
            
        st.divider()
        # Original Best Performing Video
        df_bp = df.copy()
        df_bp["performance_score"] = (df_bp["total_engagement_rate"] * 0.4 + df_bp["engagement_per_1000"] * 0.3 + df_bp["view_subscriber_ratio"] * 0.3)
        best_video = df_bp.loc[df_bp["performance_score"].idxmax()]
        
        st.subheader("🥇 Best Performing Video")
        bv_col1, bv_col2 = st.columns([2, 1])
        with bv_col1:
            st.markdown(f"""
            <div style="background-color: #1f2937; padding: 20px; border-radius: 10px;">
                <h4>{best_video['title']}</h4>
                <p><b>Views:</b> {best_video['view_count']:,} | <b>Likes:</b> {best_video['like_count']:,}</p>
                <p><b>Published:</b> {best_video['published_at'].strftime('%Y-%m-%d') if hasattr(best_video['published_at'], 'strftime') else best_video['published_at']}</p>
            </div>
            """, unsafe_allow_html=True)
        with bv_col2:
            st.metric("Performance Score", f"{best_video['performance_score']:.2f}")
            st.metric("Engagement Rate", f"{best_video['total_engagement_rate']:.2f}%")

    # ── PDF Download Button ───────────────────────────────────────────────────
    st.divider()
    with st.expander("📥 Download Report"):
        with st.spinner("Preparing PDF report…"):
            pdf_bytes = generate_pdf_report(
                channel_info=channel_info, video_analytics=video_analytics, df=df,
                predicted_subs=_predicted_subs, growth_rate=_growth_rate,
                upload_frequency=_upload_freq, duration_counts=_dur_counts,
                subscriber_watch_percent=_sub_watch_pct, avg_engagement=_avg_engagement,
                low_estimate=_low_est, high_estimate=_high_est, rpm=_rpm, insights=_insights
            )
        st.download_button(label="Download Professional PDF Report", data=pdf_bytes, 
                           file_name=f"InsightTube_{channel_name.replace(' ', '_')}.pdf", 
                           mime="application/pdf", use_container_width=True, type="primary")


# ═════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

if analyze_btn:
    if channel_input:
        with st.spinner("🔍 Analyzing channel data... This may take a few moments."):
            run_full_channel_analysis_and_display(channel_input)
            st.toast("Channel analysis completed!", icon="✅")
    else:
        st.warning("Please enter a valid channel URL or ID.")
elif not channel_input:
    # Empty preview state
    st.markdown("""
    <div style="text-align: center; margin-top: 60px; padding: 40px; border: 2px dashed #334155; border-radius: 20px; opacity: 0.6; animation: fadeIn 1s ease-out;">
        <img src="https://cdn-icons-png.flaticon.com/128/404/404672.png" width="60" style="filter: grayscale(100%); opacity: 0.5;">
        <h3 style="color: #64748B; margin-top: 15px;">Your insights will appear here</h3>
        <p style="color: #475569;">Enter a channel name or URL above to generate a comprehensive analytics report.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
.footer {
    position: fixed; left: 0; bottom: 0; width: 100%;
    background-color: #0E1117; color: white;
    text-align: right; padding: 10px; font-size: 14px;
}
</style>
<div class="footer">
    © 2026 InsightTube | Built with Streamlit 💙 | Pbo7
</div>
""", unsafe_allow_html=True)
