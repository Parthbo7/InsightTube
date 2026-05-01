import re
import altair as alt
import streamlit as st
from streamlit_lottie import st_lottie
from services import load_lottieurl, run_full_channel_analysis
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
 
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InsightTube – Channel Compare",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# ── Global Styles (mirrors Channel Analysis theme) ────────────────────────────
st.markdown("""
<style>
/* ── base ── */
.block-container { padding-top: 2rem; }
[data-testid="stSidebar"] { background-color: #111827; }
.stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; }

/* ── Metric Label and Value Styles ── */
[data-testid="metric-container"] label {
    font-size: 0.95rem !important;
}
[data-testid="metric-container"] > div > div > div:nth-child(2) {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}
 
/* ── section header cards ── */
.section-header {
    display: flex; align-items: center; gap: 10px;
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    border-left: 4px solid #CC0000;
    padding: 10px 16px; border-radius: 8px;
    margin: 16px 0 8px 0;
}
.section-header h4 { margin: 0; color: #f9fafb; font-size: 1rem; }
 
/* ── channel card ── */
.channel-card {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    border: 1px solid #374151;
    border-top: 3px solid #CC0000;
    border-radius: 12px;
    padding: 20px; margin-bottom: 8px;
}
.channel-name { font-size: 1.3rem; font-weight: 700; color: #f9fafb; margin: 0; }
.channel-sub  { font-size: 0.82rem; color: #9ca3af; margin-top: 2px; }
 
/* ── stat pill ── */
.stat-pill {
    display: inline-block;
    background: #0E1117; border: 1px solid #374151;
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.8rem; color: #d1d5db; margin: 3px 3px 0 0;
}
 
/* ── vs badge ── */
.vs-badge {
    text-align: center; font-size: 2.8rem; font-weight: 900;
    color: #CC0000; letter-spacing: 2px;
    text-shadow: 0 0 20px rgba(204,0,0,0.5);
    padding: 24px 0;
}
 
/* ── winner banner ── */
.winner-banner {
    background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 40%, #7f1d1d 100%);
    border: 2px solid #EF4444;
    border-radius: 16px; padding: 36px 24px; text-align: center;
    margin: 24px 0; position: relative; overflow: hidden;
}
.winner-banner::before {
    content: "🏆"; position: absolute; font-size: 8rem;
    opacity: 0.07; top: -10px; right: 20px;
}
.winner-crown  { font-size: 3.5rem; display: block; margin-bottom: 6px; }
.winner-label  { font-size: 0.95rem; color: #fca5a5; letter-spacing: 3px;
                 text-transform: uppercase; margin-bottom: 6px; }
.winner-name   { font-size: 2.2rem; font-weight: 900; color: #ffffff;
                 margin: 0 0 10px 0; }
.winner-reason { font-size: 0.9rem; color: #fcd34d; margin-top: 6px; }
 
/* ── score card ── */
.score-card {
    background: #1f2937; border: 1px solid #374151;
    border-radius: 10px; padding: 14px 18px; text-align: center;
    margin: 6px 0;
}
.score-label { font-size: 0.75rem; color: #9ca3af; margin-bottom: 4px; }
.score-value { font-size: 1.4rem; font-weight: 700; color: #f87171; }
.score-winner { color: #4ade80 !important; }
 
/* ── comparison bar ── */
.cmp-bar-wrap  { margin: 8px 0; }
.cmp-bar-label { font-size: 0.78rem; color: #9ca3af; margin-bottom: 3px; }
.cmp-bar-outer { background:#374151; border-radius:6px; height:12px; overflow:hidden; }
.cmp-bar-inner { height:12px; border-radius:6px;
                 background: linear-gradient(90deg,#FF6666,#CC0000); }
 
/* ── tie badge ── */
.tie-badge {
    background: linear-gradient(135deg,#1d4ed8,#1e40af);
    border: 2px solid #3b82f6; border-radius: 16px;
    padding: 28px 24px; text-align: center; margin: 24px 0;
}
.tie-label { font-size: 1.8rem; font-weight: 900; color: #93c5fd; }
 
/* ── insight pill ── */
.insight-win  { background:#052e16; border:1px solid #16a34a; border-radius:8px;
                padding:10px 14px; margin:5px 0; color:#86efac; font-size:0.85rem; }
.insight-lose { background:#1c1917; border:1px solid #57534e; border-radius:8px;
                padding:10px 14px; margin:5px 0; color:#a8a29e; font-size:0.85rem; }
 
/* ── footer ── */
.footer {
    position: fixed; left: 0; bottom: 0; width: 100%;
    background-color: #0E1117; color: white;
    text-align: right; padding: 10px; font-size: 14px; z-index: 999;
}
</style>
""", unsafe_allow_html=True)
 
# ── Hide default sidebar nav ──────────────────────────────────────────────────
st.markdown("""
    <style>[data-testid="stSidebarNav"] {display: none;}</style>
""", unsafe_allow_html=True)
 
# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" width="40">
        <h3 style="margin:0; color:white;">InsightTube</h3>
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
 
# ── Page Header ───────────────────────────────────────────────────────────────
st.divider()
hc1, hc2 = st.columns([1, 10])
hc1.image("https://cdn-icons-png.flaticon.com/128/934/934478.png", width=80)
hc2.title("Channel Comparison")
st.divider()
 
 
# ═════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def format_number_to_millions(num):
    """Convert numbers to millions format (1.46M, 554.66M, etc.)"""
    try:
        num = float(num)
        if num >= 1_000_000:
            return f"{num/1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{int(num)}"
    except:
        return "0"

def parse_iso_duration(duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, str(duration))
    if not match:
        return 0
    h  = int(match.group(1)) if match.group(1) else 0
    mn = int(match.group(2)) if match.group(2) else 0
    s  = int(match.group(3)) if match.group(3) else 0
    return h * 3600 + mn * 60 + s
 
 
def classify_creator(freq):
    if freq < 1:   return "😴 Inactive"
    elif freq < 4: return "🎥 Casual"
    elif freq < 8: return "📈 Consistent"
    else:          return "🔥 Highly Active"
 
 
def compute_channel_stats(info, data):
    """Return a dict of derived metrics used throughout the page."""
    df = pd.DataFrame(data) if data else pd.DataFrame()
    stats = {}
 
    # Basic counts
    stats["subscriber_count"] = int(info.get("subscriber_count", 0))
    stats["view_count"]       = int(info.get("view_count", 0))
    stats["video_count"]      = int(info.get("video_count", 0))
 
    # Always initialise every derived key with a safe default first
    defaults = {
        "avg_views":      0.0,
        "avg_likes":      0.0,
        "avg_comments":   0.0,
        "avg_engagement": 0.0,
        "avg_eng_1000":   0.0,
        "avg_vsr":        0.0,
    }
    stats.update(defaults)
 
    if not df.empty:
        def _col_mean(col):
            if col in df.columns:
                try:
                    return float(pd.to_numeric(df[col], errors="coerce").mean())
                except Exception:
                    return 0.0
            return 0.0
 
        stats["avg_views"]      = _col_mean("view_count")
        stats["avg_likes"]      = _col_mean("like_count")
        stats["avg_comments"]   = _col_mean("comment_count")
        stats["avg_engagement"] = _col_mean("total_engagement_rate")
        stats["avg_eng_1000"]   = _col_mean("engagement_per_1000")
        stats["avg_vsr"]        = _col_mean("view_subscriber_ratio")
 
    # Subscriber watch %
    subs = stats["subscriber_count"]
    stats["sub_watch_pct"] = (
        (stats["avg_views"] / subs * 100) if subs > 0 else 0.0
    )
 
    # Upload frequency
    try:
        pub_date = datetime.strptime(info["published_at"][:10], "%Y-%m-%d").date()
        today    = datetime.now().date()
        months   = (today.year - pub_date.year) * 12 + (today.month - pub_date.month)
        months   = max(months, 1)
        stats["upload_freq"] = stats["video_count"] / months
    except Exception:
        stats["upload_freq"] = 0.0
 
    stats["creator_type"] = classify_creator(stats["upload_freq"])
    return stats, df
 
 
def compute_overall_score(stats):
    """Weighted composite score for winner determination."""
    score  = 0.0
    score += min(stats.get("sub_watch_pct",  0.0), 100) * 0.20
    score += min(stats.get("avg_engagement", 0.0), 50)  * 0.25
    score += min(stats.get("avg_eng_1000",   0.0), 200) * 0.20
    score += min(stats.get("upload_freq",    0.0), 20)  * 0.15
    score += min(stats.get("avg_vsr",        0.0), 100) * 0.20
    return round(score, 3)
 
 
def section_header(icon_url, title):
    st.markdown(f"""
    <div class="section-header">
        <img src="{icon_url}" width="32">
        <h4>{title}</h4>
    </div>""", unsafe_allow_html=True)
 
 
def gauge_chart(value, max_val, title, suffix="", color="red", key="gauge"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix},
        title={"text": title, "font": {"color": "#f9fafb"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#9ca3af"},
            "bar": {"color": "#CC0000"},
            "bgcolor": "#1f2937",
            "bordercolor": "#374151",
            "steps": [
                {"range": [0,   max_val * 0.20], "color": "#ffcccc"},
                {"range": [max_val * 0.20, max_val * 0.40], "color": "#ff9999"},
                {"range": [max_val * 0.40, max_val * 0.60], "color": "#ff6666"},
                {"range": [max_val * 0.60, max_val * 0.80], "color": "#ff3333"},
                {"range": [max_val * 0.80, max_val],        "color": "#cc0000"},
            ],
        }
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=80, b=10),
        height=280,
        paper_bgcolor="#111827",
        font={"color": "#f9fafb"}
    )
    st.plotly_chart(fig, use_container_width=True, key=key)
 
 
def comparison_bar_html(label, val1, val2, name1, name2, fmt=".0f"):
    total = val1 + val2
    if total == 0:
        p1, p2 = 50, 50
    else:
        p1 = round(val1 / total * 100)
        p2 = 100 - p1
    
    # Format values - use millions format for large numbers
    if fmt == ",":
        v1_str = format_number_to_millions(val1)
        v2_str = format_number_to_millions(val2)
    else:
        v1_str = f"{val1:{fmt}}"
        v2_str = f"{val2:{fmt}}"
    
    winner_cls1 = "color:#4ade80;font-weight:700;" if val1 >= val2 else ""
    winner_cls2 = "color:#4ade80;font-weight:700;" if val2 >= val1 else ""
    st.markdown(f"""
    <div style="margin:10px 0;">
        <div style="font-size:0.9rem;color:#9ca3af;margin-bottom:6px;">{label}</div>
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="min-width:90px;text-align:right;font-size:1.1rem;font-weight:700;{winner_cls1}">{v1_str}</span>
            <div style="flex:1;background:#374151;border-radius:6px;height:14px;overflow:hidden;display:flex;">
                <div style="width:{p1}%;background:linear-gradient(90deg,#FF6666,#CC0000);height:14px;"></div>
                <div style="width:{p2}%;background:linear-gradient(90deg,#4B5563,#374151);height:14px;"></div>
            </div>
            <span style="min-width:90px;font-size:1.1rem;font-weight:700;{winner_cls2}">{v2_str}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#6b7280;margin-top:4px;">
            <span>{name1}</span><span>{name2}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
 
def render_channel_column(info, stats, df, col_id):
    """Render all per-channel charts & metrics inside a column."""
    name = info["channel_name"]
 
    # ── Card header ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="channel-card">
        <p class="channel-name">📌 {name}</p>
        <p class="channel-sub">Since {info['published_at'][:10]}</p>
    </div>
    """, unsafe_allow_html=True)
 
    # ── Key metrics ──────────────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric("👥 Subscribers",  format_number_to_millions(stats['subscriber_count']))
    m2.metric("👁️ Total Views",  format_number_to_millions(stats['view_count']))
    m3.metric("🎬 Total Videos", f"{stats['video_count']:,}")
 
    if df.empty:
        st.warning("No video data available.")
        return
 
    # ── Views per Video ───────────────────────────────────────────────────────
    st.divider()
    section_header(
        "https://cdn-icons-png.flaticon.com/128/2088/2088617.png",
        "Views per Video"
    )
    fig_views = px.bar(df.sort_values("view_count", ascending=False), 
                       x="title", y="view_count", color_discrete_sequence=["#CC0000"])
    fig_views.update_layout(height=400, template="plotly_dark", xaxis_title=None)
    st.plotly_chart(fig_views, use_container_width=True, key=f"views_{col_id}")
 
    # ── Likes & Comments ─────────────────────────────────────────────────────
    st.divider()
    section_header(
        "https://cdn-icons-png.flaticon.com/128/1077/1077035.png",
        "Likes & Comments per Video"
    )
    fig_lc = go.Figure()
    fig_lc.add_trace(go.Scatter(x=df["title"], y=df["like_count"], name="Likes", line=dict(color="#FF0000", width=3)))
    fig_lc.add_trace(go.Scatter(x=df["title"], y=df["comment_count"], name="Comments", line=dict(color="#8B0000", width=3)))
    fig_lc.update_layout(height=400, template="plotly_dark", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_lc, use_container_width=True, key=f"lc_{col_id}")
 
    # ── Engagement Rate ───────────────────────────────────────────────────────
    st.divider()
    section_header(
        "https://cdn-icons-png.flaticon.com/128/3135/3135715.png",
        "Engagement Analytics"
    )
    fig_eng = px.line(df, x="title", y="total_engagement_rate", markers=True, 
                      color_discrete_sequence=["#CC0000"])
    fig_eng.update_layout(height=400, template="plotly_dark", yaxis_title="Eng. Rate (%)")
    st.plotly_chart(fig_eng, use_container_width=True, key=f"eng_line_{col_id}")
 
    # ── Video Duration Distribution ────────────────────────────────────────────
    st.divider()
    section_header(
        "https://cdn-icons-png.flaticon.com/128/2469/2469822.png",
        "Video Duration"
    )
    df_dur = df.copy()
    df_dur["duration_sec"] = df_dur.get("duration", "PT0S").apply(parse_iso_duration)
    df_dur["duration_min"] = df_dur["duration_sec"] / 60
    
    pie_fig = px.pie(df_dur, values="duration_min", names="title", hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Reds_r)
    pie_fig.update_layout(height=400, template="plotly_dark", showlegend=False)
    st.plotly_chart(pie_fig, use_container_width=True, key=f"dur_pie_{col_id}")
 
    # ── Top Performing Video ──────────────────────────────────────────────────
    st.divider()
    section_header(
        "https://cdn-icons-png.flaticon.com/128/4302/4302106.png",
        "Best Performing Video"
    )
    df_bp = df.copy()
    df_bp["perf_score"] = (
        df_bp["total_engagement_rate"] * 0.4 +
        df_bp["engagement_per_1000"]   * 0.3 +
        df_bp["view_subscriber_ratio"] * 0.3
    )
    best = df_bp.loc[df_bp["perf_score"].idxmax()]
    st.markdown(f"""
    <div style="background:#1f2937;border:1px solid #374151;border-left:3px solid #CC0000;
                border-radius:8px;padding:14px;margin:4px 0;">
        <p style="font-weight:700;color:#f9fafb;margin:0 0 6px 0;">🥇 {best['title']}</p>
        <p style="font-size:0.9rem;color:#9ca3af;margin:0;">
            Published: {str(best['published_at'])[:10]} &nbsp;|&nbsp;
            Views: {format_number_to_millions(best['view_count'])}
        </p>
    </div>
    """, unsafe_allow_html=True)
    bp1, bp2 = st.columns(2)
    bp1.metric("Eng. Rate", f"{best['total_engagement_rate']:.2f}%")
    bp2.metric("Perf. Score", f"{best['perf_score']:.2f}")
 
    # ── Recent Video Analytics Table ──────────────────────────────────────────
    st.divider()
    section_header(
        "https://cdn-icons-png.flaticon.com/128/9858/9858369.png",
        "Recent Video Analytics"
    )
    st.data_editor(
        df[["title","view_count","like_count","comment_count","total_engagement_rate"]].reset_index(drop=True),
        column_config={
            "title": "Video Title",
            "view_count": st.column_config.NumberColumn("Views", format="%d"),
            "like_count": st.column_config.NumberColumn("Likes", format="%d"),
            "comment_count": st.column_config.NumberColumn("Comments", format="%d"),
            "total_engagement_rate": st.column_config.NumberColumn("Eng %", format="%.2f%%"),
        },
        hide_index=True,
        use_container_width=True,
        disabled=True,
        key=f"data_grid_{col_id}"
    )
 
 
def render_head_to_head(info1, stats1, info2, stats2):
    """Render the head-to-head comparison metrics section."""
    st.divider()
    section_header(
        "https://cdn-icons-png.flaticon.com/128/6586/6586210.png",
        "Head-to-Head Comparison"
    )
 
    n1 = info1["channel_name"]
    n2 = info2["channel_name"]
 
    comparison_bar_html("👥 Subscribers",
        stats1.get("subscriber_count", 0), stats2.get("subscriber_count", 0), n1, n2, fmt=",")
    comparison_bar_html("👁️ Total Views",
        stats1.get("view_count", 0), stats2.get("view_count", 0), n1, n2, fmt=",")
    comparison_bar_html("🎬 Total Videos",
        stats1.get("video_count", 0), stats2.get("video_count", 0), n1, n2, fmt=",")
    comparison_bar_html("📈 Avg Engagement Rate (%)",
        stats1.get("avg_engagement", 0.0), stats2.get("avg_engagement", 0.0), n1, n2, fmt=".2f")
    comparison_bar_html("💡 Avg Eng. per 1000 Views",
        stats1.get("avg_eng_1000", 0.0), stats2.get("avg_eng_1000", 0.0), n1, n2, fmt=".2f")
    comparison_bar_html("🔗 Avg View/Sub Ratio",
        stats1.get("avg_vsr", 0.0), stats2.get("avg_vsr", 0.0), n1, n2, fmt=".2f")
    comparison_bar_html("👁️‍🗨️ Subscriber Watch %",
        stats1.get("sub_watch_pct", 0.0), stats2.get("sub_watch_pct", 0.0), n1, n2, fmt=".1f")
    comparison_bar_html("🗓️ Uploads per Month",
        stats1.get("upload_freq", 0.0), stats2.get("upload_freq", 0.0), n1, n2, fmt=".1f")
 
 
def render_radar_chart(stats1, stats2, name1, name2):
    """Plotly radar / spider chart comparing both channels."""
    categories = [
        "Subscriber\nWatch %",
        "Avg\nEngagement",
        "Eng / 1000",
        "Upload\nFrequency",
        "View/Sub\nRatio",
    ]
 
    # Normalise each metric to 0-100 for radar
    def normalise(v, mx): return min(v / mx * 100, 100) if mx > 0 else 0
 
    maxes = [100, 50, 200, 20, 100]
    keys  = ["sub_watch_pct", "avg_engagement", "avg_eng_1000",
             "upload_freq", "avg_vsr"]
 
    vals1 = [normalise(stats1.get(k, 0.0), m) for k, m in zip(keys, maxes)]
    vals2 = [normalise(stats2.get(k, 0.0), m) for k, m in zip(keys, maxes)]
 
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals1 + [vals1[0]], theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(204,0,0,0.2)",
        line=dict(color="#CC0000", width=2.5),
        name=name1
    ))
    fig.add_trace(go.Scatterpolar(
        r=vals2 + [vals2[0]], theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(99,102,241,0.2)",
        line=dict(color="#818CF8", width=2.5),
        name=name2
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#1f2937",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#374151",
                            tickfont=dict(color="#9ca3af"), linecolor="#374151"),
            angularaxis=dict(gridcolor="#374151", linecolor="#374151",
                             tickfont=dict(color="#d1d5db"))
        ),
        legend=dict(font=dict(color="#d1d5db"), bgcolor="#111827",
                    bordercolor="#374151"),
        paper_bgcolor="#111827",
        margin=dict(l=50, r=50, t=50, b=50),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True, key="radar_chart")
 
 
def render_score_summary(stats1, stats2, name1, name2):
    """Metric-by-metric scorecard."""
    st.divider()
    section_header(
        "https://cdn-icons-png.flaticon.com/128/1705/1705312.png",
        "Category Scorecard"
    )
 
    categories = [
        ("👥 Subscribers",         stats1.get("subscriber_count", 0),  stats2.get("subscriber_count", 0),  ",d"),
        ("👁️ Total Views",         stats1.get("view_count", 0),         stats2.get("view_count", 0),         ",d"),
        ("📈 Avg Engagement Rate", stats1.get("avg_engagement", 0.0),   stats2.get("avg_engagement", 0.0),   ".2f"),
        ("💡 Eng. / 1000 Views",   stats1.get("avg_eng_1000", 0.0),     stats2.get("avg_eng_1000", 0.0),     ".2f"),
        ("🔗 View / Sub Ratio",    stats1.get("avg_vsr", 0.0),          stats2.get("avg_vsr", 0.0),          ".2f"),
        ("👁️‍🗨️ Sub Watch %",       stats1.get("sub_watch_pct", 0.0),    stats2.get("sub_watch_pct", 0.0),    ".1f"),
        ("🗓️ Uploads / Month",     stats1.get("upload_freq", 0.0),      stats2.get("upload_freq", 0.0),      ".1f"),
    ]
 
    hdr0, hdr1, hdr2, hdr3 = st.columns([3.5, 2, 2, 2])
    hdr0.markdown(f"<span style='color:#9ca3af;font-size:0.9rem;font-weight:700;'>Category</span>",
                  unsafe_allow_html=True)
    hdr1.markdown(f"<span style='color:#f87171;font-size:0.9rem;font-weight:700;'>{name1}</span>",
                  unsafe_allow_html=True)
    hdr2.markdown(f"<span style='color:#818cf8;font-size:0.9rem;font-weight:700;'>{name2}</span>",
                  unsafe_allow_html=True)
    hdr3.markdown(f"<span style='color:#9ca3af;font-size:0.9rem;font-weight:700;'>Winner</span>",
                  unsafe_allow_html=True)
 
    wins1 = wins2 = 0
    for cat, v1, v2, fmt in categories:

        try:
            v1 = float(v1)
        except:
            v1 = 0

        try:
            v2 = float(v2)
        except:
            v2 = 0

        # convert to int if format expects integer
        if fmt == ",d":
            v1 = int(v1)
            v2 = int(v2)
            v1_str = format_number_to_millions(v1)
            v2_str = format_number_to_millions(v2)
        else:
            v1_str = f"{v1:{fmt}}"
            v2_str = f"{v2:{fmt}}"
        
        c0, c1, c2, c3 = st.columns([3.5, 2, 2, 2])
        c0.markdown(f"<span style='font-size:0.95rem;color:#d1d5db;'>{cat}</span>",
                    unsafe_allow_html=True)
        if v1 > v2:
            c1.markdown(f"<span style='color:#4ade80;font-weight:700;font-size:1.05rem;'>{v1_str}</span>",
                        unsafe_allow_html=True)
            c2.markdown(f"<span style='color:#9ca3af;font-size:1.05rem;'>{v2_str}</span>",
                        unsafe_allow_html=True)
            c3.markdown("<span style='color:#4ade80;font-size:1rem;'>✅ " + name1[:14] + "</span>",
                        unsafe_allow_html=True)
            wins1 += 1
        elif v2 > v1:
            c1.markdown(f"<span style='color:#9ca3af;font-size:1.05rem;'>{v1_str}</span>",
                        unsafe_allow_html=True)
            c2.markdown(f"<span style='color:#4ade80;font-weight:700;font-size:1.05rem;'>{v2_str}</span>",
                        unsafe_allow_html=True)
            c3.markdown("<span style='color:#4ade80;font-size:1rem;'>✅ " + name2[:14] + "</span>",
                        unsafe_allow_html=True)
            wins2 += 1
        else:
            c1.markdown(f"<span style='color:#9ca3af;font-size:1.05rem;'>{v1_str}</span>",
                        unsafe_allow_html=True)
            c2.markdown(f"<span style='color:#9ca3af;font-size:1.05rem;'>{v2_str}</span>",
                        unsafe_allow_html=True)
            c3.markdown("<span style='color:#a8a29e;font-size:1rem;'>⚖️ Tie</span>",
                        unsafe_allow_html=True)

    return wins1, wins2


def channel_insights(info, stats, is_winner):
    """Generate insight bullets for a channel."""
    insights = []
    
    if is_winner:
        if stats.get("avg_engagement", 0) > 5:
            insights.append(f"🔥 Exceptional engagement at {stats['avg_engagement']:.1f}% — stands out in crowded space")
        if stats.get("sub_watch_pct", 0) > 20:
            insights.append(f"👀 Strong subscriber watch: {stats['sub_watch_pct']:.1f}% watch each video")
        if stats.get("upload_freq", 0) > 2:
            insights.append(f"📅 Consistent uploads: {stats['upload_freq']:.1f}/mo keeps audience engaged")
        if stats.get("avg_vsr", 0) > 30:
            insights.append(f"🚀 Viral potential: View/subscriber ratio of {stats['avg_vsr']:.1f}")
        if not insights:
            insights.append("✨ Overall strong channel performance")
    else:
        if stats.get("avg_engagement", 0) < 3:
            insights.append(f"⚡ Engagement opportunity: {stats['avg_engagement']:.1f}% vs competitor — increase calls-to-action")
        if stats.get("sub_watch_pct", 0) < 10:
            insights.append(f"👥 Subscriber retention: {stats['sub_watch_pct']:.1f}% watch — improve video relevance")
        if stats.get("upload_freq", 0) < 1:
            insights.append(f"📈 Upload frequency: {stats['upload_freq']:.1f}/mo — more consistent releases drive growth")
        if stats.get("avg_vsr", 0) < 10:
            insights.append(f"📊 View velocity: {stats['avg_vsr']:.1f} — optimize thumbnails & titles for CTR")
        if not insights:
            insights.append("💡 Focus on engagement metrics")
    
    return insights


def render_winner(info1, stats1, info2, stats2, winner_wins, loser_wins):
    """Determine and render the overall winner with detailed reasoning."""
    st.divider()
    section_header(
        "https://cdn-icons-png.flaticon.com/128/1995/1995467.png",
        "🏆 Overall Winner Analysis"
    )

    w_score = compute_overall_score(stats1)
    l_score = compute_overall_score(stats2)
    
    if abs(w_score - l_score) < 0.5:
        st.markdown(f"""
        <div class="tie-badge">
            <span class="tie-label">⚖️ Virtual Tie</span>
            <p style="color:#93c5fd;margin:8px 0 0 0;font-size:0.95rem;">
                Both channels excel in different areas. {info1['channel_name']} ({w_score:.1f}) vs {info2['channel_name']} ({l_score:.1f})
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    is_ch1_winner = w_score >= l_score
    w_name = info1["channel_name"] if is_ch1_winner else info2["channel_name"]
    l_name = info2["channel_name"] if is_ch1_winner else info1["channel_name"]
    winner_stats = stats1 if is_ch1_winner else stats2
    loser_stats = stats2 if is_ch1_winner else stats1
    winner_wins = winner_wins if is_ch1_winner else loser_wins
    loser_wins = loser_wins if is_ch1_winner else winner_wins
    
    margin_pct = abs(w_score - l_score) / ((w_score + l_score) / 2) * 100 if (w_score + l_score) > 0 else 0
    
    # Determine primary winning reason
    reason = "📊 Balanced excellence across all metrics"
    if winner_stats["subscriber_count"] > loser_stats["subscriber_count"] * 1.5:
        reason = f"👥 Significantly larger audience ({format_number_to_millions(winner_stats['subscriber_count'])} vs {format_number_to_millions(loser_stats['subscriber_count'])})"
    elif winner_stats["avg_engagement"] > loser_stats["avg_engagement"] * 1.3:
        reason = f"📈 Superior engagement rate ({winner_stats['avg_engagement']:.1f}% vs {loser_stats['avg_engagement']:.1f}%)"
    elif winner_stats["sub_watch_pct"] > loser_stats["sub_watch_pct"] * 1.2:
        reason = f"💪 Higher subscriber watch rate ({winner_stats['sub_watch_pct']:.1f}% vs {loser_stats['sub_watch_pct']:.1f}%)"
    elif winner_stats["upload_freq"] > loser_stats["upload_freq"] * 1.2:
        reason = f"📅 More consistent uploads ({winner_stats['upload_freq']:.1f}/mo vs {loser_stats['upload_freq']:.1f}/mo)"
    elif winner_stats["avg_vsr"] > loser_stats["avg_vsr"] * 1.2:
        reason = f"🔗 Better view-to-subscriber ratio ({winner_stats['avg_vsr']:.2f} vs {loser_stats['avg_vsr']:.2f})"
    else:
        reason = f"📊 Overall composite score advantage ({w_score:.1f} vs {l_score:.1f})"
 
    st.markdown(f"""
    <div class="winner-banner">
        <span class="winner-crown">🏆</span>
        <p class="winner-label">🎉 &nbsp; Overall Winner &nbsp; 🎉</p>
        <p class="winner-name">{w_name}</p>
        <p style="color:#fca5a5;font-size:1rem;margin:2px 0;">
            Score: <b>{w_score:.1f}</b> &nbsp;|&nbsp; Category Wins: <b>{winner_wins}</b> / {winner_wins + loser_wins}
        </p>
        <p class="winner-reason">⭐ Key Advantage: {reason}</p>
        <p style="color:#d1fae5;font-size:0.9rem;margin-top:6px;">
            Winning by <b>{margin_pct:.1f}%</b> overall performance margin
        </p>
    </div>
    """, unsafe_allow_html=True)
 
    # ── Channel-specific insight cards ────────────────────────────────────
    ins_c1, ins_c2 = st.columns(2)
    with ins_c1:
        st.markdown(f"<p style='color:#4ade80;font-weight:700;margin-bottom:6px;font-size:1rem;'>✅ {w_name} — Strengths</p>",
                    unsafe_allow_html=True)
        for ins in channel_insights(info1 if is_ch1_winner else info2, winner_stats, True):
            st.markdown(f"<div class='insight-win'>{ins}</div>", unsafe_allow_html=True)
 
    with ins_c2:
        st.markdown(f"<p style='color:#f87171;font-weight:700;margin-bottom:6px;font-size:1rem;'>💡 {l_name} — Areas to Improve</p>",
                    unsafe_allow_html=True)
        for ins in channel_insights(info2 if is_ch1_winner else info1, loser_stats, False):
            st.markdown(f"<div class='insight-lose'>{ins}</div>", unsafe_allow_html=True)
 
 
# ═════════════════════════════════════════════════════════════════════════════
#  INPUT SECTION
# ═════════════════════════════════════════════════════════════════════════════
 
col1, col2 = st.columns(2, gap="large")
with col1:
    channel_1_input = st.text_input(
        "🔴 Enter First Channel Name or URL",
        placeholder="e.g. MrBeast or youtube.com/@MrBeast"
    )
with col2:
    channel_2_input = st.text_input(
        "🟣 Enter Second Channel Name or URL",
        placeholder="e.g. PewDiePie or youtube.com/@PewDiePie"
    )
 
compare_btn = st.button("⚡ Compare Channels", use_container_width=True, type="primary")
 
# ── VS badge preview ──────────────────────────────────────────────────────
if channel_1_input and channel_2_input and not compare_btn:
    n1_preview = channel_1_input[:20]
    n2_preview = channel_2_input[:20]
    st.markdown(f"""
    <div class="vs-badge">{n1_preview} ⚔️ VS ⚔️ {n2_preview}</div>
    """, unsafe_allow_html=True)
 
# ─────────────────────────────────────────────────────────────────────────────
if compare_btn:
    if channel_1_input and channel_2_input:
        lottie_compare = load_lottieurl("https://lottie.host/5405494d-2b7e-41b9-9686-347472099395/35798741.json")
        with st.spinner("Analyzing both channels... ⏳"):
            if lottie_compare:
                st_lottie(lottie_compare, height=200, key="compare_lottie")
            info1, data1 = run_full_channel_analysis(channel_1_input)
            info2, data2 = run_full_channel_analysis(channel_2_input)
 
            if info1 and info2:
                st.session_state["info1"] = info1
                st.session_state["data1"] = data1
                st.session_state["info2"] = info2
                st.session_state["data2"] = data2
                st.toast("Analysis complete! ✅")
            else:
                st.error("❌ Failed to analyze one or both channels. Check the names / URLs and retry.")
    else:
        st.warning("⚠️ Please enter both channel names or URLs.")
 
# ═════════════════════════════════════════════════════════════════════════════
#  RESULTS
# ═════════════════════════════════════════════════════════════════════════════
 
if "info1" in st.session_state and "info2" in st.session_state:
 
    info1 = st.session_state["info1"]
    data1 = st.session_state["data1"]
    info2 = st.session_state["info2"]
    data2 = st.session_state["data2"]
 
    stats1, df1 = compute_channel_stats(info1, data1)
    stats2, df2 = compute_channel_stats(info2, data2)
 
    # Safety net
    _stat_defaults = {
        "avg_views": 0.0, "avg_likes": 0.0, "avg_comments": 0.0,
        "avg_engagement": 0.0, "avg_eng_1000": 0.0, "avg_vsr": 0.0,
        "sub_watch_pct": 0.0, "upload_freq": 0.0, "creator_type": "N/A",
        "subscriber_count": 0, "view_count": 0, "video_count": 0,
    }
    for _k, _v in _stat_defaults.items():
        stats1.setdefault(_k, _v)
        stats2.setdefault(_k, _v)
 
    name1 = info1["channel_name"]
    name2 = info2["channel_name"]

    # ── TABS ────────────────────────────────────────────────────────────────
    tab_sum, tab_det, tab_score = st.tabs(["🥊 Comparison Summary", "📊 Detailed Breakdown", "🎯 Category Scorecard"])

    with tab_sum:
        # ── Section: Side-by-side VS banner ──────────────────────────────────────
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:center;gap:24px;
                    background:linear-gradient(135deg,#1f2937,#111827);
                    border:1px solid #374151;border-radius:14px;padding:18px;margin:16px 0;">
            <div style="text-align:center;">
                <p style="font-size:1.4rem;font-weight:900;color:#f87171;margin:0;">{name1}</p>
                <p style="font-size:0.95rem;color:#9ca3af;margin:4px 0;">
                    {format_number_to_millions(stats1['subscriber_count'])} subscribers
                </p>
            </div>
            <div style="font-size:2.4rem;font-weight:900;color:#CC0000;
                        text-shadow:0 0 18px rgba(204,0,0,0.6);">⚔️ VS ⚔️</div>
            <div style="text-align:center;">
                <p style="font-size:1.4rem;font-weight:900;color:#818cf8;margin:0;">{name2}</p>
                <p style="font-size:0.95rem;color:#9ca3af;margin:4px 0;">
                    {format_number_to_millions(stats2['subscriber_count'])} subscribers
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
        # ── Head-to-Head comparison bars ─────────────────────────────────────────
        render_head_to_head(info1, stats1, info2, stats2)
    
        # ── Radar Chart ───────────────────────────────────────────────────────────
        st.divider()
        section_header(
            "https://cdn-icons-png.flaticon.com/128/9098/9098312.png",
            "Performance Radar"
        )
        render_radar_chart(stats1, stats2, name1, name2)

        # ── Winner Section ────────────────────────────────────────────────────────
        # We need wins1/wins2 here too, but they are calculated in score summary.
        # Let's calculate them upfront or just render winner based on overall score.
        w1, w2 = 0, 0
        cats = [("subscriber_count", 0), ("view_count", 0), ("avg_engagement", 0), ("avg_eng_1000", 0), ("avg_vsr", 0), ("sub_watch_pct", 0), ("upload_freq", 0)]
        for k, _ in cats:
            if stats1.get(k, 0) > stats2.get(k, 0): w1 += 1
            elif stats2.get(k, 0) > stats1.get(k, 0): w2 += 1
        
        render_winner(info1, stats1, info2, stats2, w1, w2)

    with tab_det:
        # ── Per-channel detailed analysis (side by side) ──────────────────────────
        st.markdown(f"""
        <div class="section-header">
            <img src="https://cdn-icons-png.flaticon.com/128/9858/9858369.png" width="32">
            <h4>Detailed Channel Breakdown</h4>
        </div>
        """, unsafe_allow_html=True)
    
        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            render_channel_column(info1, stats1, df1, col_id="ch1")
        with col_b:
            render_channel_column(info2, stats2, df2, col_id="ch2")
 
    with tab_score:
        # ── Score Summary Table ───────────────────────────────────────────────────
        wins1, wins2 = render_score_summary(stats1, stats2, name1, name2)
 
    st.divider()
    st.markdown(
        "<p style='color:#6b7280;font-size:0.88rem;text-align:center;'>"
        "📊 Analysis based on the 10 most recent videos &nbsp;|&nbsp; "
        "Composite score weights: Engagement 25%, Sub Watch 20%, Eng/1000 20%, VSR 20%, Upload Freq 15%"
        "</p>",
        unsafe_allow_html=True
    )
 
# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.footer {
    position: fixed; left: 0; bottom: 0; width: 100%;
    background-color: #0E1117; color: white;
    text-align: right; padding: 10px; font-size: 14px; z-index: 999;
}
</style>
<div class="footer">© 2026 InsightTube | Built with Streamlit 💙 | Pbo7</div>
""", unsafe_allow_html=True)