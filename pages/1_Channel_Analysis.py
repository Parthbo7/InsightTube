import re
import io
import altair as alt
import streamlit as st
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
</style>
""", unsafe_allow_html=True)

subscriber_watch_percent = 0
upload_frequency         = 0
duration_counts          = pd.DataFrame()

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase     = create_client(supabase_url, supabase_key)

st.divider()
col1, col2 = st.columns([1, 10])
col1.image("https://cdn-icons-png.flaticon.com/128/7172/7172401.png", width=80)
col2.title("Channel Analysis")
st.divider()

channel_input = st.text_input("Enter YouTube Channel Name ")

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
    col1.image("https://cdn-icons-png.flaticon.com/128/934/934478.png", width=40)
    col2.page_link("pages/2_Channel_Compare.py", label="Channel Compare")
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/9227/9227001.png", width=40)
    col2.page_link("pages/4_Trending.py", label="Trending Videos")
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/9985/9985768.png", width=40)
    col2.page_link("pages/3_About_Us.py", label="About Us")
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/2593/2593453.png", width=40)
    col2.page_link("pages/5_Sentiment_Analysis.py", label="Sentiment Analysis")


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

    with st.spinner("Analyzing channel... This may take a moment."):
        channel_info, video_analytics = run_full_channel_analysis(channel_input)

    if not channel_info:
        st.error("Failed to fetch channel data. Please check the URL or ID and try again.")
        return

    channel_name = channel_info["channel_name"]
    channel_id   = channel_info["channel_id"]
    channel_url  = f"https://www.youtube.com/channel/{channel_id}"

    st.title(f"Channel: [{channel_name}]({channel_url})")

    col1, col2, col3 = st.columns(3)
    col1.metric("Subscribers", f"{int(channel_info['subscriber_count']):,}")
    col2.metric("Total Views",  f"{int(channel_info['view_count']):,}")
    col3.metric("Total Videos", channel_info["video_count"])

    st.divider()
    col1, col2 = st.columns([1, 15])
    col1.image("https://cdn-icons-png.flaticon.com/128/7739/7739187.png", width=50)
    col2.subheader("Channel Description")
    st.markdown(f"**Description:** {channel_info['description']}")
    st.divider()
    col1, col2 = st.columns([1, 15])
    col1.image("https://cdn-icons-png.flaticon.com/128/10691/10691802.png", width=50)
    col2.subheader("Channel Published Date")
    st.markdown(f"**Published At:** {channel_info['published_at']}")
    st.divider()

    # ── Build dataframe ───────────────────────────────────────────────────────
    if video_analytics:
        df = pd.DataFrame(video_analytics)
    else:
        st.warning("No video analytics data found.")
        return

    if df.empty:
        st.warning("No video analytics data found.")
        return

    # ── Views per Video ───────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 15])
    col1.image("https://cdn-icons-png.flaticon.com/128/404/404672.png", width=50)
    col2.subheader("Views per Video")
    chart_df = df.sort_values(by="view_count", ascending=False)
    st.bar_chart(chart_df, x="title", y="view_count",
                 color="#FF0000FF", use_container_width=True)
    st.divider()

    # ── Likes & Comments ──────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 15])
    col1.image("https://cdn-icons-png.flaticon.com/128/2285/2285636.png", width=50)
    col2.subheader("Likes and Comments per Video")
    chart_df2 = pd.DataFrame({
        "Video Index": range(1, len(df) + 1),
        "Likes":    df["like_count"].values,
        "Comments": df["comment_count"].values,
    })
    base          = alt.Chart(chart_df2).encode(x=alt.X("Video Index:Q"))
    likes_line    = base.mark_line(color="#FF0000", size=3).encode(
        y=alt.Y("Likes:Q", title="Count"), tooltip=["Video Index", "Likes"])
    comments_line = base.mark_line(color="#8B0000", size=3).encode(
        y=alt.Y("Comments:Q"), tooltip=["Video Index", "Comments"])
    st.altair_chart(likes_line + comments_line, use_container_width=True)
    st.divider()

    # ── Engagement Gauges ─────────────────────────────────────────────────────
    top_10_df        = df.sort_values(by="view_count", ascending=False).head(10)
    _avg_engagement  = top_10_df["engagement_per_1000"].mean()

    left_col, right_col = st.columns([1, 1], gap="large")
    with left_col:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/2257/2257295.png" width="35">
            <h4 style="margin:0;">Average Engagement per 1000 Views</h4>
        </div>""", unsafe_allow_html=True)
        fig_eng = go.Figure(go.Indicator(
            mode="gauge+number", value=_avg_engagement,
            title={"text": "Engagement / 1000"},
            gauge={"axis": {"range": [0, 200]}, "bar": {"color": "red"},
                   "steps": [{"range": [0,50], "color": "#ffcccc"},
                              {"range": [50,100], "color": "#ff9999"},
                              {"range": [100,150], "color": "#ff6666"},
                              {"range": [150,200], "color": "#cc0000"}]}))
        fig_eng.update_layout(margin=dict(l=10, r=10, t=80, b=10), height=300)
        st.plotly_chart(fig_eng, use_container_width=True)

    with right_col:
        try:
            average_views    = float(df["view_count"].mean())
            total_subs       = int(channel_info["subscriber_count"])
            _sub_watch_pct   = (average_views / total_subs * 100) if total_subs > 0 else 0
        except (ValueError, TypeError):
            _sub_watch_pct = 0

        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/3369/3369157.png" width="35">
            <h4 style="margin:0;">Subscriber Watch Percentage</h4>
        </div>""", unsafe_allow_html=True)
        fig_subs = go.Figure(go.Indicator(
            mode="gauge+number", value=_sub_watch_pct,
            number={"suffix": "%"},
            title={"text": "Subscribers Who Watch (%)"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "red"},
                   "steps": [{"range": [0,20], "color": "#ffcccc"},
                              {"range": [20,40], "color": "#ff9999"},
                              {"range": [40,60], "color": "#ff6666"},
                              {"range": [60,80], "color": "#ff3333"},
                              {"range": [80,100], "color": "#cc0000"}]}))
        fig_subs.update_layout(margin=dict(l=10, r=10, t=80, b=10), height=300)
        st.plotly_chart(fig_subs, use_container_width=True)

    # ── Duration ──────────────────────────────────────────────────────────────
    def categorize_duration(d):
        s = parse_iso_duration(d)
        if s < 120:   return "Short (<2 min)"
        elif s <= 600: return "Medium (1–10 min)"
        else:          return "Long (>10 min)"

    df["duration_category"] = df["duration"].apply(categorize_duration)
    _dur_counts = df["duration_category"].value_counts().reset_index()
    _dur_counts.columns = ["Category", "Count"]

    st.divider()
    left_col, right_col = st.columns([1, 1], gap="large")
    with left_col:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/12670/12670512.png" width="35">
            <h4 style="margin:0;">Video Duration Distribution</h4>
        </div>""", unsafe_allow_html=True)
        red_palette = ["#ffcccc", "#ff6666", "#cc0000"]
        fig_pie = go.Figure(data=[go.Pie(
            labels=_dur_counts["Category"], values=_dur_counts["Count"],
            hole=0.5,
            marker=dict(colors=red_palette, line=dict(color="#111111", width=2)),
            textinfo="percent+label")])
        fig_pie.update_layout(
            height=400, width=400, margin=dict(t=30, b=10, l=10, r=10),
            showlegend=True, paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117", font=dict(color="white"))
        st.plotly_chart(fig_pie, use_container_width=False)

    with right_col:
        df = df.sort_values("published_at").reset_index(drop=True)
        df["video_index"]    = df.index + 1
        df["duration_minutes"] = df["duration"].apply(
            lambda x: parse_iso_duration(x) / 60 if pd.notnull(x) else 0)
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/670/670816.png" width="35">
            <h4 style="margin:0;">Video Duration by Upload Order</h4>
        </div>""", unsafe_allow_html=True)
        duration_chart = alt.Chart(df).mark_bar(color="#cc0000").encode(
            x=alt.X("video_index:O", title="Video Index"),
            y=alt.Y("duration_minutes:Q", title="Duration (Minutes)"),
            tooltip=["video_index", "duration_minutes"]).properties(height=400)
        st.altair_chart(duration_chart, use_container_width=True)

    # ── Upload Frequency ──────────────────────────────────────────────────────
    st.divider()
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/12822/12822821.png" width="35">
            <h4 style="margin:0;">Upload Frequency Analysis</h4>
        </div>""", unsafe_allow_html=True)
    try:
        total_videos  = int(channel_info["video_count"])
        published_dt  = datetime.strptime(channel_info["published_at"][:10], "%Y-%m-%d").date()
        current_date  = datetime.now().date()
        channel_age_months = max(1,
            (current_date.year  - published_dt.year)  * 12 +
            (current_date.month - published_dt.month))
        _upload_freq = total_videos / channel_age_months
    except Exception:
        channel_age_months = 1
        _upload_freq = 0

    def classify_creator(freq):
        if freq < 1:   return "😴 Inactive"
        elif freq < 4: return "🎥 Casual"
        elif freq < 8: return "📈 Consistent"
        else:          return "🔥 Highly Active"

    creator_type = classify_creator(_upload_freq)
    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("Channel Age (Months)", channel_age_months)
    fc2.metric("Uploads per Month",    f"{_upload_freq:.2f}")
    fc3.metric("Creator Type",         creator_type)

    fig_freq = go.Figure(go.Indicator(
        mode="gauge+number", value=_upload_freq,
        title={"text": "Uploads per Month"},
        gauge={"axis": {"range": [0, 20]}, "bar": {"color": "red"},
               "steps": [{"range": [0,1],   "color": "#ffcccc"},
                          {"range": [1,4],   "color": "#ff9999"},
                          {"range": [4,8],   "color": "#ff6666"},
                          {"range": [8,12],  "color": "#ff3333"},
                          {"range": [12,20], "color": "#cc0000"}]}))
    fig_freq.update_layout(margin=dict(l=10, r=10, t=80, b=10), height=300)
    st.plotly_chart(fig_freq, use_container_width=True)

    # ── Revenue ───────────────────────────────────────────────────────────────
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
        df["estimated_revenue"] = df["view_count"].apply(
            lambda v: estimate_revenue(v, avg_cpm))

        st.divider()
        st.markdown("""
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="https://cdn-icons-png.flaticon.com/128/10384/10384161.png" width="45">
                <h4 style="margin:0;">Revenue Estimation Dashboard (INR)</h4>
            </div>""", unsafe_allow_html=True)
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Estimated Revenue (Low)",       f"₹ {_low_est:,.2f}")
        rc2.metric("Estimated Revenue (High)",      f"₹ {_high_est:,.2f}")
        rc3.metric("Revenue per 1000 Views (RPM)", f"₹ {_rpm:,.2f}")
    else:
        st.warning("Insufficient data to estimate revenue.")

    st.divider()
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/13502/13502705.png" width="45">
            <h4 style="margin:0;">Estimated Revenue per Video (INR)</h4>
        </div>""", unsafe_allow_html=True)
    revenue_df    = df.sort_values(by="estimated_revenue", ascending=False)
    revenue_chart = alt.Chart(revenue_df).mark_bar(color="#cc0000").encode(
        x=alt.X("title:N", sort="-y", title="Video Title"),
        y=alt.Y("estimated_revenue:Q", title="Revenue (₹)"),
        tooltip=[alt.Tooltip("title", title="Video"),
                 alt.Tooltip("estimated_revenue", title="Revenue (₹)", format=",.2f")]
    ).properties(height=400)
    st.altair_chart(revenue_chart, use_container_width=True)

    # ── Best Performing Video ─────────────────────────────────────────────────
    st.divider()
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/4302/4302106.png" width="45">
            <h4 style="margin:0;">Best Performing Recent Video Analyzer</h4>
        </div>""", unsafe_allow_html=True)

    df_bp = pd.DataFrame(video_analytics)
    if not df_bp.empty:
        df_bp["performance_score"] = (
            df_bp["total_engagement_rate"] * 0.4 +
            df_bp["engagement_per_1000"]   * 0.3 +
            df_bp["view_subscriber_ratio"] * 0.3)
        best_video = df_bp.loc[df_bp["performance_score"].idxmax()]
        st.subheader("🥇 Best Performing Video")
        bv1, bv2 = st.columns(2)
        with bv1:
            st.markdown(f"""
            **Title:** {best_video['title']}  
            **Published At:** {best_video['published_at']}  
            **Views:** {best_video['view_count']}  
            **Likes:** {best_video['like_count']}  
            **Comments:** {best_video['comment_count']}
            """)
        with bv2:
            st.metric("Engagement Rate",       f"{best_video['total_engagement_rate']:.2f}%")
            st.metric("Views / Subscriber Ratio", f"{best_video['view_subscriber_ratio']:.2f}")
            st.metric("Performance Score",     f"{best_video['performance_score']:.2f}")

    # ── Growth Prediction ─────────────────────────────────────────────────────
    st.divider()
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="https://cdn-icons-png.flaticon.com/128/2920/2920349.png" width="40">
        <h4 style="margin:0;">Subscriber Growth Prediction (Next 30 Days)</h4>
    </div>""", unsafe_allow_html=True)

    current_subs           = int(channel_info["subscriber_count"])
    _predicted_subs, _growth_rate = predict_subscriber_growth(df, current_subs)

    gc1, gc2, gc3 = st.columns(3)
    gc1.metric("Current Subscribers", f"{current_subs:,}")
    gc2.metric("Predicted (30 Days)", f"{_predicted_subs:,}")
    gc3.metric("Growth Rate",         f"{_growth_rate:.2f}%")

    growth_chart = alt.Chart(pd.DataFrame({
        "Stage":       ["Current", "Predicted (30 Days)"],
        "Subscribers": [current_subs, _predicted_subs]
    })).mark_bar(color="#cc0000").encode(x="Stage", y="Subscribers")
    st.altair_chart(growth_chart, use_container_width=True)

    # ── AI Insights ───────────────────────────────────────────────────────────
    st.divider()
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/16835/16835765.png" width="45">
            <h4 style="margin:0;">Channel Insights & Strategy Suggestions</h4>
        </div>""", unsafe_allow_html=True)

    avg_engagement_rate = df["total_engagement_rate"].mean()
    avg_views_val       = df["view_count"].mean()
    top_views_val       = df["view_count"].max()

    if avg_engagement_rate > 8:
        _insights.append("🔥 Excellent engagement rate. Audience is highly interactive.")
    elif avg_engagement_rate > 4:
        _insights.append("📈 Good engagement. There is room for stronger CTAs.")
    else:
        _insights.append("⚠️ Low engagement. Improve thumbnails, hooks, and call-to-actions.")

    if _sub_watch_pct > 40:
        _insights.append("💪 Strong subscriber loyalty. Majority of subscribers actively watch.")
    elif _sub_watch_pct > 20:
        _insights.append("🤝 Moderate subscriber watching pattern.")
    else:
        _insights.append("❗ Many subscribers are inactive. Focus on retention strategies.")

    if _upload_freq >= 8:
        _insights.append("🔥 Highly active creator. Algorithm favors this consistency.")
    elif _upload_freq >= 4:
        _insights.append("📅 Good upload consistency.")
    else:
        _insights.append("😴 Upload frequency is low. Increase consistency to grow faster.")

    if not _dur_counts.empty:
        most_common = _dur_counts.iloc[0]["Category"]
        if most_common == "Short (<2 min)":
            _insights.append("📱 Channel focuses on short-form content. Shorts strategy detected.")
        elif most_common == "Medium (1–10 min)":
            _insights.append("🎬 Balanced content length. Optimized for regular YouTube videos.")
        else:
            _insights.append("🎥 Long-form content dominant. Great for deep audience retention.")

    if top_views_val > avg_views_val * 1.8:
        _insights.append("🚀 One video significantly outperformed others. Analyze and replicate its format.")

    if _growth_rate > 4:
        st.success("🚀 Channel is experiencing strong growth momentum.")
    elif _growth_rate > 1:
        st.info("📈 Channel is showing steady growth.")
    else:
        st.warning("⚠️ Growth is currently slow.")

    for insight in _insights:
        st.success(insight)

    # ── Video Analytics Table ─────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Recent Video Analytics")
    df_display = df.reset_index(drop=True)
    df_display.insert(0, "S.No", df_display.index + 1)
    st.dataframe(
        df_display,
        column_config={
            "S.No":                  st.column_config.NumberColumn("S.No", width="small"),
            "title":                 "Video Title",
            "published_at":          "Published Date",
            "view_count":            st.column_config.NumberColumn("Views",    format="%d 👀"),
            "like_count":            st.column_config.NumberColumn("Likes",    format="%d 👍"),
            "comment_count":         st.column_config.NumberColumn("Comments", format="%d 💬"),
            "like_ratio":            st.column_config.NumberColumn("Like Ratio",    format="%.2f %%"),
            "comment_ratio":         st.column_config.NumberColumn("Comment Ratio", format="%.2f %%"),
            "total_engagement_rate": st.column_config.NumberColumn("Engagement Rate", format="%.2f %%"),
            "view_subscriber_ratio": st.column_config.NumberColumn("View/Sub Ratio",  format="%.2f %%"),
            "engagement_per_1000":   st.column_config.NumberColumn("Engagement / 1000", format="%.2f"),
            "like_comment_ratio":    st.column_config.NumberColumn("Like-Comment Ratio", format="%.2f"),
        },
        hide_index=True,
        use_container_width=True
    )

    # ── PDF Download Button ───────────────────────────────────────────────────
    st.divider()
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
        <img src="https://cdn-icons-png.flaticon.com/128/337/337946.png" width="35">
        <h4 style="margin:0;">Download Full Analytics Report</h4>
    </div>""", unsafe_allow_html=True)

    with st.spinner("Preparing PDF report with all charts and visualizations…"):
        pdf_bytes = generate_pdf_report(
            channel_info     = channel_info,
            video_analytics  = video_analytics,
            df               = df,
            predicted_subs   = _predicted_subs,
            growth_rate      = _growth_rate,
            upload_frequency = _upload_freq,
            duration_counts  = _dur_counts,
            subscriber_watch_percent = _sub_watch_pct,
            avg_engagement   = _avg_engagement,
            low_estimate     = _low_est,
            high_estimate    = _high_est,
            rpm              = _rpm,
            insights         = _insights
        )

    channel_slug = channel_name.replace(" ", "_")
    filename     = f"InsightTube_{channel_slug}_{datetime.now().strftime('%Y%m%d')}.pdf"

    st.download_button(
        label           = "📥  Download Professional PDF Report",
        data            = pdf_bytes,
        file_name       = filename,
        mime            = "application/pdf",
        use_container_width = True,
        type            = "primary"
    )


# ═════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

if st.button("Analyze Channel"):
    if channel_input:
        run_full_channel_analysis_and_display(channel_input)
        st.toast("Channel analysis completed!", icon="✅")
    else:
        st.warning("Please enter a valid channel URL or ID.")

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
