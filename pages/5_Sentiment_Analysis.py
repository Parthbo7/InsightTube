import re
import io
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from video import get_10_recent_videos
from videodata import fetch_video_analytics
from comments import fetch_top_comments
from sentiment import analyze_with_groq


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

.sentiment-card {
    padding: 14px 16px;
    border-radius: 10px;
    margin-bottom: 10px;
    font-size: 0.88rem;
    line-height: 1.5;
    word-break: break-word;
}
.s-positive { background: rgba(16,185,129,0.12); border-left: 4px solid #10b981; }
.s-negative { background: rgba(239,68,68,0.12);  border-left: 4px solid #ef4444; }
.s-neutral  { background: rgba(107,114,128,0.12); border-left: 4px solid #6b7280; }

.theme-tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    background: #374151;
    color: #e5e7eb;
    font-size: 0.8rem;
    margin: 4px 4px 4px 0;
}

.verdict-box {
    padding: 20px 24px;
    border-radius: 12px;
    text-align: center;
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 20px;
}
.v-positive { background: rgba(16,185,129,0.18); border: 1px solid #10b981; color: #10b981; }
.v-negative { background: rgba(239,68,68,0.18);  border: 1px solid #ef4444; color: #ef4444; }
.v-neutral  { background: rgba(107,114,128,0.18); border: 1px solid #6b7280; color: #9ca3af; }
.v-mixed    { background: rgba(251,191,36,0.18);  border: 1px solid #fbbf24; color: #fbbf24; }
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

# ── Header ────────────────────────────────────────────────────────────────────
st.divider()
col1, col2 = st.columns([1, 10])
col1.image("https://cdn-icons-png.flaticon.com/128/2593/2593453.png", width=80)
col2.title("Comment Sentiment Analysis")
st.caption("Understand what your audience truly feels — powered by Llama 3.1 8B (Groq)")
st.divider()

# ── Session state ─────────────────────────────────────────────────────────────
for key in ["videos_data", "last_channel", "sentiment_results", "analyzed_comments", "analyzed_video"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── Step 1 — Channel input ────────────────────────────────────────────────────
channel_input = st.text_input("Enter YouTube Channel Name or URL")

if channel_input and channel_input != st.session_state.last_channel:
    with st.spinner("Fetching recent videos…"):
        try:
            links = get_10_recent_videos(channel_input)
            if not links:
                st.error("Channel not found or has no public videos.")
            else:
                video_data = fetch_video_analytics(links)
                if not video_data:
                    st.error("Could not retrieve video details.")
                else:
                    st.session_state.videos_data = video_data
                    st.session_state.last_channel = channel_input
                    st.session_state.sentiment_results = None
                    st.session_state.analyzed_comments = None
                    st.session_state.analyzed_video = None
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
    run_clicked = st.button("Run Analysis", type="primary", use_container_width=True)

    if run_clicked:
        with st.spinner("Fetching up to 100 comments…"):
            comments, fetch_err = fetch_top_comments(vid_id, max_results=100)

        if fetch_err:
            st.error(f"Could not fetch comments: {fetch_err}")
        elif not comments:
            st.warning("No comments were returned for this video.")
        else:
            with st.spinner("Analyzing with Llama 3.1 8B (Groq) — this takes a few seconds…"):
                try:
                    groq_key = st.secrets["GROQ_API_KEY"]
                except KeyError:
                    st.error(
                        "**GROQ_API_KEY** not found in `.streamlit/secrets.toml`.\n\n"
                        "Add it to use sentiment analysis."
                    )
                    st.stop()
                results, err = analyze_with_groq(comments, chosen["title"], groq_key)

            if err:
                st.error(f"Analysis failed: {err}")
            else:
                st.session_state.sentiment_results = results
                st.session_state.analyzed_comments = comments
                st.session_state.analyzed_video = chosen

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
        f'<div class="verdict-box {verdict_cls}">{verdict_text}</div>',
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
    col_chart, col_summary = st.columns([1, 1])

    with col_chart:
        fig = go.Figure(data=[go.Pie(
            labels=["Positive", "Negative", "Neutral"],
            values=[counts["positive"], counts["negative"], counts["neutral"]],
            hole=0.55,
            marker=dict(colors=["#10b981", "#ef4444", "#6b7280"]),
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} comments<extra></extra>",
        )])
        fig.update_layout(
            showlegend=True,
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font=dict(color="white"),
            margin=dict(t=30, b=30),
            annotations=[dict(
                text=overall.upper(),
                x=0.5, y=0.5,
                font_size=13, font_color="white",
                showarrow=False,
            )],
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_summary:
        if r.get("summary"):
            st.markdown("**What the audience is saying:**")
            st.info(r["summary"])

        if r.get("key_themes"):
            st.markdown("**Key Themes:**")
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
        }
        wc = WordCloud(
            width=1200,
            height=400,
            background_color="#111827",
            colormap="RdYlGn",
            stopwords=stopwords,
            max_words=80,
            prefer_horizontal=0.8,
        ).generate(raw_corpus)

        fig_wc, ax = plt.subplots(figsize=(14, 5))
        fig_wc.patch.set_facecolor("#111827")
        ax.set_facecolor("#111827")
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        plt.tight_layout(pad=0)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", facecolor="#111827")
        buf.seek(0)
        st.image(buf, use_container_width=True)
        plt.close(fig_wc)

    except ImportError:
        st.info("Install **wordcloud** (`pip install wordcloud`) to see the word cloud.")
    except Exception as e:
        st.warning(f"Could not generate word cloud: {e}")

    # Top positive / negative comments
    st.markdown("---")
    col_pos, col_neg = st.columns(2)

    with col_pos:
        st.markdown("### Top Positive Comments")
        top_pos = r["positive"][:5]
        if top_pos:
            for entry in top_pos:
                text = _clean_display(entry["text"])
                st.markdown(
                    f'<div class="sentiment-card s-positive">{text}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No strongly positive comments found.")

    with col_neg:
        st.markdown("### Top Negative Comments")
        top_neg = r["negative"][:5]
        if top_neg:
            for entry in top_neg:
                text = _clean_display(entry["text"])
                st.markdown(
                    f'<div class="sentiment-card s-negative">{text}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("No significantly negative comments found.")

    # Full comment table
    with st.expander(f"See all {total} analyzed comments"):
        rows = []
        for label, bucket in [("Positive", r["positive"]), ("Negative", r["negative"]), ("Neutral", r["neutral"])]:
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
    text-align: right; padding: 10px; font-size: 14px;
}
</style>
<div class="footer">© 2026 InsightTube | Built with Streamlit 💙 | Pbo7</div>
""", unsafe_allow_html=True)
