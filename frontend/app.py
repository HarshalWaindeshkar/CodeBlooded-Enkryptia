import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(
    page_title="Finfluencer Risk Detector",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 Finfluencer Risk Detector")
st.markdown("**Paste a financial YouTube video URL to detect risky or misleading investment content.**")
st.divider()

url = st.text_input("🔗 YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
analyze_btn = st.button("🚀 Analyze Video", use_container_width=True)

if analyze_btn:
    if not url:
        st.error("Please enter a YouTube URL first.")
    else:
        with st.spinner("⏳ Downloading and analyzing video... this may take 1-2 minutes"):
            try:
                response = requests.post(
                    API_URL,
                    json={"url": url},
                    timeout=300
                )
                data = response.json()

                if response.status_code != 200:
                    st.error(f"API Error: {data.get('detail', 'Unknown error')}")
                else:
                    st.divider()

                    # Video info
                    st.subheader(f"📹 {data['video_title']}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Duration", f"{data['duration_seconds']}s")
                    col2.metric("Words", data['word_count'])
                    col3.metric("Language", data['language'].upper())

                    st.divider()

                    # Risk Score
                    score = data['risk_score']
                    label = data['risk_label']

                    if score >= 7:
                        st.error(f"## {label} — {score}/10")
                    elif score >= 4:
                        st.warning(f"## {label} — {score}/10")
                    else:
                        st.success(f"## {label} — {score}/10")

                    st.progress(score / 10)
                    st.divider()

                    # Reasons
                    st.subheader("📋 Risk Breakdown")
                    for reason in data['reasons']:
                        st.markdown(f"- {reason}")

                    st.divider()

                    # Hype keywords
                    st.subheader("🚨 Hype Keywords Detected")
                    if data['hype_keywords_found']:
                        cols = st.columns(3)
                        for i, kw in enumerate(data['hype_keywords_found']):
                            cols[i % 3].error(f"**{kw['keyword']}** (x{kw['count']})")
                    else:
                        st.success("✅ No hype keywords found")

                    st.divider()

                    # Disclaimer
                    st.subheader("⚖️ Disclaimer Check")
                    if data['disclaimer_found']:
                        st.success(f"✅ Disclaimer found: *{', '.join(data['found_disclaimers'])}*")
                    else:
                        st.error("🚨 No financial disclaimer detected in this video")

                    st.divider()

                    # Transcript preview
                    with st.expander("📝 Transcript Preview"):
                        st.write(data['transcript_preview'] + "...")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running in Terminal 1.")
            except requests.exceptions.Timeout:
                st.error("⏰ Timeout — video took too long. Try a shorter video (under 5 mins).")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

st.divider()
st.caption("⚠️ This tool is for educational purposes only and does not constitute financial advice.")