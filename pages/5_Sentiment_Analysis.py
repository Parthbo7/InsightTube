import re
import io
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from video import get_10_recent_videos
from videodata import fetch_video_analytics
from comments import fetch_top_comments
from sentiment import analyze_with_groq

# ── Caching API calls ────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=3600)
def cached_get_videos(channel):
    return get_10_recent_videos(channel)

@st.cache_data(show_spinner=False, ttl=3600)
def cached_get_analytics(links):
    return fetch_video_analytics(links)

@st.cache_data(show_spinner=False, ttl=3600)
def cached_get_comments(vid_id, max_results=100):
    return fetch_top_comments(vid_id, max_results)

@st.cache_data(show_spinner=False, ttl=3600)
def cached_analyze(comments, title, api_key):
    return analyze_with_groq(comments, title, api_key)

def _clean_display(text, max_chars=300):
    """Strip HTML tags and truncate for safe rendering inside HTML cards."""
    return re.sub(r'<[^>]+>', '', text)[:max_chars]

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InsightTube – Sentiment Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container { padding-top: 2rem; }
[data-testid="stSidebar"] { background-color: #111827; }
.stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; }

/* ── Hero ── */
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
    margin-bottom: 10px;
}
.ai-badge {
    background: linear-gradient(90deg, #3B82F6, #8B5CF6);
    color: white;
    padding: 6px 14px;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 25px;
    box-shadow: 0 0 15px rgba(139, 92, 246, 0.5);
}

.sentiment-card {
    padding: 16px;
    border-radius: 10px;
    margin-bottom: 12px;
    font-size: 0.95rem;
    line-height: 1.5;
    word-break: break-word;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.s-positive { background: rgba(16,185,129,0.12); border-left: 4px solid #10b981; }
.s-negative { background: rgba(239,68,68,0.12);  border-left: 4px solid #ef4444; }
.s-neutral  { background: rgba(107,114,128,0.12); border-left: 4px solid #6b7280; }

.theme-tag {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    background: #374151;
    color: #e5e7eb;
    font-size: 0.85rem;
    margin: 4px 6px 4px 0;
    border: 1px solid #4b5563;
}

.verdict-box {
    padding: 24px;
    border-radius: 12px;
    text-align: center;
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 24px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}
.v-positive { background: rgba(16,185,129,0.18); border: 1px solid #10b981; color: #10b981; }
.v-negative { background: rgba(239,68,68,0.18);  border: 1px solid #ef4444; color: #ef4444; }
.v-neutral  { background: rgba(107,114,128,0.18); border: 1px solid #6b7280; color: #9ca3af; }
.v-mixed    { background: rgba(251,191,36,0.18);  border: 1px solid #fbbf24; color: #fbbf24; }

.scrollable-comments {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 10px;
}
.scrollable-comments::-webkit-scrollbar { width: 6px; }
.scrollable-comments::-webkit-scrollbar-track { background: #1f2937; border-radius: 4px; }
.scrollable-comments::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 4px; }
.scrollable-comments::-webkit-scrollbar-thumb:hover { background: #6b7280; }
</style>
""", unsafe_allow_html=True)

st.markdown('<style>[data-testid="stSidebarNav"]{display:none;}</style>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;">
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

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; margin-top: 20px; animation: fadeIn 0.8s ease-out;">
    <img src="https://cdn-icons-png.flaticon.com/128/2593/2593453.png" width="80" style="margin-bottom: 10px;">
    <h1 class="hero-header">Comment Sentiment Analysis</h1>
    <p class="hero-subtitle">Understand what your audience really thinks using AI-powered sentiment analysis</p>
    <div class="ai-badge">✨ Powered by Llama 3.1 8B (Groq)</div>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key in ["videos_data", "last_channel", "sentiment_results", "analyzed_comments", "analyzed_video", "is_analyzing", "analyze_clicked"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── Step 1 — Channel input ────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    channel_input = st.text_input("🔍 Enter YouTube Channel Name or URL", placeholder="e.g., 'MrBeast' or UCX6OQ3DkcsbYNE6H8uQQuVA")
    
    st.markdown("""
    <p style="color: #64748B; font-size: 0.9rem; margin-top: -10px; margin-bottom: 20px; text-align: center;">
        <i>Suggestions: Netflix, MrBeast, CarryMinati</i>
    </p>
    """, unsafe_allow_html=True)
    
    fetch_btn = st.button("🚀 Fetch Recent Videos", use_container_width=True, type="primary")

if not channel_input and not st.session_state.videos_data:
    st.markdown("""
    <div style="text-align: center; margin-top: 60px; padding: 40px; border: 2px dashed #334155; border-radius: 20px; opacity: 0.6; animation: fadeIn 1s ease-out;">
        <img src="https://cdn-icons-png.flaticon.com/128/404/404672.png" width="60" style="filter: grayscale(100%); opacity: 0.5;">
        <h3 style="color: #64748B; margin-top: 15px;">Your sentiment insights will appear here</h3>
        <p style="color: #475569;">Enter a channel name or URL above to load videos and analyze comments.</p>
    </div>
    """, unsafe_allow_html=True)

if fetch_btn or (channel_input and channel_input != st.session_state.last_channel):
    if channel_input:
        with st.spinner("Fetching recent videos…"):
            try:
                links = cached_get_videos(channel_input)
                if not links:
                    st.error("Channel not found or has no public videos.")
                else:
                    video_data = cached_get_analytics(links)
                    if not video_data:
                        st.error("Could not retrieve video details.")
                    else:
                        st.session_state.videos_data = video_data
                        st.session_state.last_channel = channel_input
                        st.session_state.sentiment_results = None
                        st.session_state.analyzed_comments = None
                        st.session_state.analyzed_video = None
                        st.session_state.is_analyzing = False
            except Exception as e:
                st.error(f"Error fetching channel: {e}")

# ── Step 2 — Video selection ──────────────────────────────────────────────────
if st.session_state.videos_data:
    videos = st.session_state.videos_data
    titles = [v["title"] for v in videos]

    col_sel, col_thumb = st.columns([3, 1])
    with col_sel:
        chosen_title = st.selectbox("Select a video to analyze", titles)

    chosen = next(v for v in videos if v["title"] == chosen_title)
    vid_id = chosen["video_id"]

    with col_thumb:
        st.image(f"https://img.youtube.com/vi/{vid_id}/mqdefault.jpg", use_container_width=True)

    comment_count = int(chosen.get("comment_count", 0))
    st.markdown(f"**Comments on this video:** {comment_count:,}")
    if comment_count == 0:
        st.warning("This video has 0 comments recorded. It may have comments disabled.")

    # ── Step 3 — Trigger ─────────────────────────────────────────────────────
    st.markdown("---")
    
    def trigger_analysis():
        st.session_state.is_analyzing = True
        st.session_state.sentiment_results = None

    if st.button("Run Analysis", type="primary", use_container_width=True, on_click=trigger_analysis, disabled=st.session_state.is_analyzing):
        pass

    if st.session_state.is_analyzing:
        # Check API key gracefully
        try:
            groq_key = st.secrets.get("GROQ_API_KEY")
            if not groq_key:
                raise KeyError
        except (KeyError, FileNotFoundError):
            st.error(
                "**GROQ_API_KEY** not found in `.streamlit/secrets.toml`.\n\n"
                "Please add it to use the AI sentiment analysis feature."
            )
            st.session_state.is_analyzing = False
            st.stop()
            
        with st.spinner("Fetching top comments from YouTube..."):
            comments, fetch_err = cached_get_comments(vid_id, max_results=100)

        if fetch_err:
            st.error(f"Could not fetch comments: {fetch_err}")
            st.session_state.is_analyzing = False
        elif not comments:
            st.warning("No comments were returned for this video.")
            st.session_state.is_analyzing = False
        else:
            with st.spinner("Analyzing sentiments with Llama 3.1 8B (Groq) — this takes a few seconds…"):
                results, err = cached_analyze(comments, chosen["title"], groq_key)

            if err:
                st.error(f"Analysis failed: {err}")
                st.session_state.is_analyzing = False
            else:
                st.session_state.sentiment_results = results
                st.session_state.analyzed_comments = comments
                st.session_state.analyzed_video = chosen
                st.session_state.is_analyzing = False
                st.rerun()

# ── Step 4 — Results ─────────────────────────────────────────────────────────
if st.session_state.sentiment_results:
    r      = st.session_state.sentiment_results
    counts = r["counts"]
    total  = counts["total"]

    st.markdown("---")
    st.subheader("Analysis Results")

    # Verdict banner
    overall = r["overall_sentiment"]
    VERDICTS = {
        "positive": ("This audience LOVES this video", "v-positive"),
        "negative": ("The audience is not happy with this video", "v-negative"),
        "neutral":  ("Audience reaction is mostly neutral", "v-neutral"),
        "mixed":    ("The audience has mixed feelings about this video", "v-mixed"),
    }
    verdict_text, verdict_cls = VERDICTS.get(overall, ("Mixed reaction", "v-mixed"))
    st.markdown(
        f'<div class="verdict-box {verdict_cls}">Verdict: {verdict_text}</div>',
        unsafe_allow_html=True,
    )

    # Metric cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Comments Analyzed", total)
    c2.metric("Positive", f"{counts['positive']}  ({round(counts['positive'] / total * 100)}%)")
    c3.metric("Negative", f"{counts['negative']}  ({round(counts['negative'] / total * 100)}%)")
    c4.metric("Neutral",  f"{counts['neutral']}  ({round(counts['neutral']  / total * 100)}%)")

    st.markdown("---")

    # Donut chart + Summary
    col_chart, col_summary = st.columns([1.2, 1])

    with col_chart:
        labels = ["Positive", "Negative", "Neutral"]
        values = [counts["positive"], counts["negative"], counts["neutral"]]
        colors = ["#10b981", "#ef4444", "#6b7280"]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color='#111827', width=2)),
            textinfo="label+percent",
            textfont=dict(size=14, color="white"),
            hovertemplate="%{label}: %{value} comments<extra></extra>",
            pull=[0.05 if v == max(values) else 0 for v in values] # Pull out the largest slice slightly
        )])
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font=dict(color="white"),
            margin=dict(t=20, b=40, l=20, r=20),
            annotations=[dict(
                text=overall.upper(),
                x=0.5, y=0.5,
                font_size=16, font_color="white",
                showarrow=False,
            )],
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_summary:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if r.get("summary"):
            st.markdown("### 🗣️ What the audience is saying:")
            st.info(r["summary"], icon="ℹ️")

        if r.get("key_themes"):
            st.markdown("### 🏷️ Key Themes:")
            tags = "".join(f'<span class="theme-tag">{t}</span>' for t in r["key_themes"])
            st.markdown(tags, unsafe_allow_html=True)

        if not r.get("summary") and not r.get("key_themes"):
            st.info("No summary or key themes were returned for this video.")

    # Word cloud
    st.markdown("---")
    st.subheader("Comment Word Cloud")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from wordcloud import WordCloud, STOPWORDS

        raw_corpus = " ".join(
            re.sub(r'<[^>]+>', ' ', c["text"])
            for c in st.session_state.analyzed_comments
        )
        stopwords = STOPWORDS | {
            "video", "channel", "youtube", "like", "comment",
            "subscribe", "please", "one", "will", "get", "watch",
            "videos", "good", "great", "awesome", "love", "really"
        }
        wc = WordCloud(
            width=1200,
            height=500,
            background_color="#111827",
            colormap="Set2",
            stopwords=stopwords,
            max_words=100,
            prefer_horizontal=0.85
        ).generate(raw_corpus)

        fig_wc, ax = plt.subplots(figsize=(14, 6))
        fig_wc.patch.set_facecolor("#111827")
        ax.set_facecolor("#111827")
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        plt.tight_layout(pad=0)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", facecolor="#111827", dpi=150)
        buf.seek(0)
        st.image(buf, use_container_width=True, caption="Most frequently used words in comments")
        plt.close(fig_wc)

    except ImportError:
        st.info("Install **wordcloud** (`pip install wordcloud`) to see the word cloud.")
    except Exception as e:
        st.warning(f"Could not generate word cloud: {e}")

    # Top positive / negative comments
    st.markdown("---")
    col_pos, col_neg = st.columns(2, gap="large")

    with col_pos:
        st.markdown("### 🟢 Top Positive Comments")
        top_pos = r.get("positive", [])[:15]
        if top_pos:
            st.markdown('<div class="scrollable-comments">', unsafe_allow_html=True)
            for entry in top_pos:
                text = _clean_display(entry["text"])
                st.markdown(
                    f'<div class="sentiment-card s-positive">{text}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No strongly positive comments found.")

    with col_neg:
        st.markdown("### 🔴 Top Negative Comments")
        top_neg = r.get("negative", [])[:15]
        if top_neg:
            st.markdown('<div class="scrollable-comments">', unsafe_allow_html=True)
            for entry in top_neg:
                text = _clean_display(entry["text"])
                st.markdown(
                    f'<div class="sentiment-card s-negative">{text}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("No significantly negative comments found.")

    # Full comment table
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(f"See all {total} analyzed comments", expanded=False):
        rows = []
        for label, bucket in [("Positive", r.get("positive", [])), ("Negative", r.get("negative", [])), ("Neutral", r.get("neutral", []))]:
            for entry in bucket:
                rows.append({
                    "Sentiment": label,
                    "Comment": re.sub(r'<[^>]+>', '', entry["text"])[:250],
                })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.footer {
    position: fixed; left: 0; bottom: 0; width: 100%;
    background-color: #0E1117; color: white;
    text-align: right; padding: 10px; font-size: 14px; z-index: 1000;
}
</style>
<div class="footer">© 2026 InsightTube | Built with Streamlit 💙 | Pbo7</div>
""", unsafe_allow_html=True)
