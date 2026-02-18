import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(
    page_title="Finfluencer Risk Detector",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 AI Finfluencer Risk Detector")
st.markdown("**Powered by OpenAI Whisper + FinBERT Financial AI Model**")
st.divider()

url = st.text_input("🔗 YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
analyze_btn = st.button("🚀 Analyze Video", use_container_width=True)

if analyze_btn:
    if not url:
        st.error("Please enter a YouTube URL first.")
    else:
        with st.spinner("⏳ Transcribing and running AI analysis... please wait"):
            try:
                response = requests.post(API_URL, json={"url": url}, timeout=300)
                data = response.json()

                if response.status_code != 200:
                    st.error(f"API Error: {data.get('detail', 'Unknown error')}")
                else:
                    st.divider()

                    # ── SECTION 1: Video Info ──
                    st.subheader(f"📹 {data['video_title']}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric(
                        label="⏱️ Duration",
                        value=f"{data['duration_seconds']}s",
                        help="Total length of the video"
                    )
                    col2.metric(
                        label="📝 Words Transcribed",
                        value=data['word_count'],
                        help="Total words extracted from audio by Whisper AI"
                    )
                    col3.metric(
                        label="🌐 Language",
                        value=data['language'].upper(),
                        help="Language detected by Whisper AI"
                    )
                    st.divider()

                    # ── SECTION 2: Overall Risk Score ──
                    st.markdown("### 🎯 Overall Risk Score")
                    st.caption("A score from 0–10 calculated by combining FinBERT sentiment analysis, hype language detection, and disclaimer checking.")

                    score = data['risk_score']
                    label = data['risk_label']

                    if score >= 7:
                        st.error(f"## {label}")
                        st.error(f"### {score} / 10")
                        st.error("⛔ This video shows strong signs of misleading or high-risk financial content.")
                    elif score >= 4:
                        st.warning(f"## {label}")
                        st.warning(f"### {score} / 10")
                        st.warning("⚠️ This video shows some signs of risky or unbalanced financial content. Watch with caution.")
                    else:
                        st.success(f"## {label}")
                        st.success(f"### {score} / 10")
                        st.success("✅ This video appears to contain relatively balanced financial content.")

                    st.progress(score / 10)
                    st.divider()

                    # ── SECTION 3: FinBERT AI Analysis ──
                    st.markdown("### 🤖 FinBERT AI Sentiment Analysis")
                    st.caption("""
                    **What is FinBERT?**  
                    FinBERT is an AI model trained on thousands of financial documents.
                    It reads the video transcript and detects whether the financial tone
                    is **Positive** (hyped/overconfident), **Negative** (fear-mongering),
                    or **Neutral** (balanced and objective).
                    """)

                    sentiment = data.get('finbert_sentiment', 'unknown')
                    confidence = data.get('finbert_confidence', 0)

                    col1, col2 = st.columns(2)
                    col1.metric(
                        label="📊 Sentiment Detected",
                        value=sentiment.upper(),
                        help="The overall financial tone FinBERT detected in this video"
                    )
                    col2.metric(
                        label="🎯 AI Confidence",
                        value=f"{int(confidence * 100)}%",
                        help="How confident FinBERT is in its sentiment classification"
                    )

                    if sentiment == 'positive':
                        st.warning("""
                        **🔴 What this means for you:**  
                        FinBERT found the video has an **overwhelmingly positive financial tone**.  
                        Credible financial content always mentions risks alongside rewards.  
                        A video that sounds too good to be true — often is.
                        """)
                    elif sentiment == 'negative':
                        st.info("""
                        **🔵 What this means for you:**  
                        FinBERT detected a **negative financial tone**.  
                        This could mean the creator is using fear tactics to push
                        alternative investments like gold, crypto, or specific stocks.
                        """)
                    else:
                        st.success("""
                        **🟢 What this means for you:**  
                        FinBERT detected a **neutral, balanced tone**.  
                        The content appears to discuss financial topics objectively
                        without excessive hype or fear — a sign of credible advice.
                        """)
                    st.divider()

                    # ── SECTION 4: Score Breakdown ──
                    st.markdown("### 📋 Why Did It Get This Score?")
                    st.caption("Each factor below contributed to the final risk score.")
                    for reason in data['reasons']:
                        st.markdown(f"- {reason}")
                    st.divider()

                    # ── SECTION 5: Disclaimer Check ──
                    st.markdown("### ⚖️ Legal Disclaimer Check")
                    st.caption("Legitimate financial creators must disclose that their content is not professional financial advice.")
                    if data['disclaimer_found']:
                        st.success(f"✅ Disclaimer found: *{', '.join(data['found_disclaimers'])}*")
                    else:
                        st.error("🚨 No financial disclaimer detected — this is a red flag for unregulated financial advice.")
                    st.divider()

                    # ── SECTION 6: Full Transcript ──
                    with st.expander("📝 View Full AI-Generated Transcript (by OpenAI Whisper)"):
                        st.caption("This transcript was automatically generated from the video audio using OpenAI Whisper")
                        st.write(data['full_transcript'])

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure FastAPI is running in Terminal 1.")
            except requests.exceptions.Timeout:
                st.error("⏰ Timeout — try a shorter video (under 5 mins).")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

st.divider()
st.caption("⚠️ This tool is for educational purposes only and does not constitute financial advice.")