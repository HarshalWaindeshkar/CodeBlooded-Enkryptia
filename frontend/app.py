import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import re
import time

API_URL = "http://127.0.0.1:8000/analyze"

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="Finfluencer AI Intelligence",
    page_icon="🚀",
    layout="wide"
)

# ==========================
# NEXT LEVEL UI STYLE
# ==========================
st.markdown("""
<style>

/* Background */
.stApp {
background: linear-gradient(135deg,#05060a,#0b0f19,#111827);
color:white;
}

/* Fix heading cut */
.block-container {
padding-top:2rem !important;
}

/* Neon title */
.big-title {
font-size:46px;
font-weight:900;
background: linear-gradient(90deg,#00ffd5,#5f7cff,#ff00ff);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
}

/* Glass cards */
.glass {
background: rgba(255,255,255,0.05);
backdrop-filter: blur(15px);
border-radius:18px;
padding:20px;
box-shadow:0px 0px 25px rgba(0,0,0,0.4);
}

/* KPI cards */
.metric-box {
background: rgba(255,255,255,0.08);
border-radius:14px;
padding:15px;
text-align:center;
font-size:18px;
}

/* Video fix — supports shorts + reels */
video {
width:100% !important;
height:auto !important;
object-fit:contain !important;
border-radius:12px;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# SIDEBAR
# ==========================
with st.sidebar:

    st.title("🧠 AI Control Panel")

    url = st.text_input("YouTube Video URL")

    analyze_btn = st.button("🚀 Run AI Analysis", use_container_width=True)

    st.divider()
    st.caption("Modules Active")
    st.success("Whisper Transcription")
    st.success("FinBERT Analysis")
    st.success("Risk Detection Engine")

# ==========================
# HEADER
# ==========================
st.markdown('<div class="big-title">🚀 Finfluencer Intelligence Dashboard</div>', unsafe_allow_html=True)
st.caption("Real-time AI risk analytics powered by Whisper + FinBERT")

st.divider()

# ==========================
# ANALYSIS
# ==========================
if analyze_btn:

    with st.spinner("Launching AI pipeline..."):

        response = requests.post(API_URL, json={"url": url}, timeout=300)
        data = response.json()

        score = data['risk_score']
        sentiment = data.get('finbert_sentiment','neutral')
        confidence = data.get('finbert_confidence',0)

        # ==========================
        # VIDEO + KPI GRID
        # ==========================
        left, right = st.columns([2,3])

        # -------- VIDEO PLAYER --------
        with left:

            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.subheader("▶️ Video Preview")

            if "youtube.com" in url or "youtu.be" in url:
                st.video(url)
            else:
                st.warning("Video preview available only for YouTube links.")

            st.markdown('</div>', unsafe_allow_html=True)

        # -------- KPI DASHBOARD --------
        with right:

            st.markdown('<div class="glass">', unsafe_allow_html=True)

            k1,k2,k3,k4 = st.columns(4)

            k1.metric("🔥 Risk Score", f"{score}/10")
            k2.metric("📊 Sentiment", sentiment.upper())
            k3.metric("🎯 Confidence", f"{int(confidence*100)}%")
            k4.metric("📝 Words", data['word_count'])

            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        # ==========================
        # MAIN ANALYTICS GRID
        # ==========================
        col1, col2 = st.columns([2,1])

        # -------- SPEEDOMETER GAUGE --------
        with col1:

            st.markdown('<div class="glass">', unsafe_allow_html=True)

            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={'text': "AI Risk Meter"},
                gauge={
                    'axis': {'range':[0,10]},
                    'steps':[
                        {'range':[0,4],'color':'green'},
                        {'range':[4,7],'color':'orange'},
                        {'range':[7,10],'color':'red'}
                    ]
                }
            ))

            st.plotly_chart(gauge, use_container_width=True)

            sentiment_data = {
                "Positive": confidence if sentiment=="positive" else 0,
                "Neutral": confidence if sentiment=="neutral" else 0,
                "Negative": confidence if sentiment=="negative" else 0
            }

            sentiment_fig = px.bar(
                x=list(sentiment_data.keys()),
                y=list(sentiment_data.values()),
                title="FinBERT Sentiment Intelligence"
            )

            st.plotly_chart(sentiment_fig, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # -------- LIVE AI INSIGHTS --------
        with col2:

            st.markdown('<div class="glass">', unsafe_allow_html=True)

            st.subheader("🧠 Live AI Insights")

            insight_box = st.empty()

            for reason in data['reasons']:
                insight_box.info(reason)
                time.sleep(0.4)

            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        # ==========================
        # KEYWORD INTELLIGENCE
        # ==========================
        st.markdown('<div class="glass">', unsafe_allow_html=True)

        st.subheader("⚡ Keyword Risk Intelligence")

        text = data['full_transcript'].lower()

        keywords = ["profit","crypto","buy","sell","guaranteed","secret","fast","millionaire"]

        counts = {}

        for word in keywords:
            counts[word] = len(re.findall(r'\b'+word+r'\b', text))

        keyword_fig = px.bar(
            x=list(counts.keys()),
            y=list(counts.values()),
            title="Risk Keyword Frequency"
        )

        st.plotly_chart(keyword_fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ==========================
        # TRANSCRIPT
        # ==========================
        with st.expander("📜 Full AI Transcript"):
            st.write(data['full_transcript'])

st.divider()
st.caption("Educational only — Not financial advice.")
