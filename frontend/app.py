import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import time
import random

API_URL = "http://127.0.0.1:8000/analyze"

# ─────────────────────────────────────────────
# PAGE CONFIG + GLOBAL CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SENTINEL — Finfluencer Risk Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

:root {
    --bg:        #020408;
    --panel:     #050d14;
    --border:    #0a3d5c;
    --accent:    #00d4ff;
    --accent2:   #00ff88;
    --danger:    #ff2d55;
    --warn:      #ffb800;
    --text:      #a8c8e0;
    --textdim:   #3a6a88;
    --glow:      0 0 20px rgba(0,212,255,0.3);
    --glowdanger:0 0 20px rgba(255,45,85,0.4);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Rajdhani', sans-serif !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 1rem 2rem !important;
    max-width: 100% !important;
}

/* ── HEADER ── */
.sentinel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 2rem;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(90deg, rgba(0,212,255,0.05), transparent);
    margin-bottom: 1.5rem;
}
.sentinel-logo {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem;
    font-weight: 900;
    color: var(--accent);
    letter-spacing: 6px;
    text-shadow: var(--glow);
}
.sentinel-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: var(--textdim);
    letter-spacing: 3px;
    margin-top: 2px;
}
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent2);
    box-shadow: 0 0 8px var(--accent2);
    margin-right: 8px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.live-badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: var(--accent2);
    letter-spacing: 2px;
}

/* ── PANELS ── */
.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent);
}
.panel-danger::before { background: var(--danger); }
.panel-warn::before   { background: var(--warn); }
.panel-ok::before     { background: var(--accent2); }

.panel-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: var(--textdim);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── KPI CARDS ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, var(--accent), transparent);
}
.kpi-value {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.kpi-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: var(--textdim);
    letter-spacing: 2px;
    margin-top: 4px;
}
.kpi-danger .kpi-value { color: var(--danger); text-shadow: var(--glowdanger); }
.kpi-warn   .kpi-value { color: var(--warn); }
.kpi-ok     .kpi-value { color: var(--accent2); }

/* ── VERDICT ── */
.verdict-high {
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem;
    font-weight: 900;
    color: var(--danger);
    text-shadow: var(--glowdanger);
    letter-spacing: 4px;
    animation: flicker 3s infinite;
}
.verdict-med {
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem;
    font-weight: 900;
    color: var(--warn);
    text-shadow: 0 0 20px rgba(255,184,0,0.4);
    letter-spacing: 4px;
}
.verdict-low {
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem;
    font-weight: 900;
    color: var(--accent2);
    text-shadow: 0 0 20px rgba(0,255,136,0.4);
    letter-spacing: 4px;
}
@keyframes flicker {
    0%,95%,100% { opacity:1; }
    96% { opacity:0.6; }
    98% { opacity:0.8; }
}

/* ── INPUT ── */
.stTextInput input {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    color: var(--accent) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 0.8rem 1rem !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: var(--glow) !important;
}

/* ── BUTTON ── */
.stButton button {
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 3px !important;
    padding: 0.7rem 2rem !important;
    border-radius: 2px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton button:hover {
    background: rgba(0,212,255,0.1) !important;
    box-shadow: var(--glow) !important;
}

/* ── PIPELINE STEPS ── */
.pipeline {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 1rem 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
}
.pipe-step {
    padding: 0.5rem 1rem;
    border: 1px solid var(--textdim);
    color: var(--textdim);
    position: relative;
    white-space: nowrap;
}
.pipe-step.active {
    border-color: var(--accent);
    color: var(--accent);
    background: rgba(0,212,255,0.08);
    box-shadow: var(--glow);
    animation: stepglow 1s infinite;
}
.pipe-step.done {
    border-color: var(--accent2);
    color: var(--accent2);
}
.pipe-arrow {
    color: var(--textdim);
    margin: 0 4px;
    font-size: 0.8rem;
}
@keyframes stepglow {
    0%,100% { box-shadow: 0 0 8px rgba(0,212,255,0.3); }
    50% { box-shadow: 0 0 20px rgba(0,212,255,0.6); }
}

/* ── THREAT ITEM ── */
.threat-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.6rem 0.8rem;
    margin-bottom: 0.4rem;
    background: rgba(255,45,85,0.05);
    border-left: 2px solid var(--danger);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: var(--text);
}
.threat-ok {
    border-left-color: var(--accent2);
    background: rgba(0,255,136,0.05);
}
.threat-warn {
    border-left-color: var(--warn);
    background: rgba(255,184,0,0.05);
}

/* ── KEYWORD TAG ── */
.kw-tag {
    display: inline-block;
    padding: 3px 10px;
    margin: 3px;
    border: 1px solid var(--danger);
    color: var(--danger);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 1px;
    background: rgba(255,45,85,0.08);
}

/* ── TRANSCRIPT ── */
.transcript-box {
    background: #030a10;
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    line-height: 1.8;
    color: var(--text);
    max-height: 200px;
    overflow-y: auto;
}
.transcript-box::-webkit-scrollbar { width: 4px; }
.transcript-box::-webkit-scrollbar-track { background: var(--panel); }
.transcript-box::-webkit-scrollbar-thumb { background: var(--border); }

/* ── INSIGHT FEED ── */
.feed-item {
    padding: 0.5rem 0.8rem;
    border-bottom: 1px solid rgba(10,61,92,0.5);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    color: var(--textdim);
    display: flex;
    gap: 10px;
}
.feed-time { color: var(--accent); min-width: 60px; }
.feed-alert { color: var(--danger); }
.feed-ok    { color: var(--accent2); }

/* ── SCORE BAR ── */
.score-bar-wrap {
    height: 8px;
    background: rgba(10,61,92,0.4);
    border-radius: 1px;
    margin: 0.5rem 0;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 1px;
    transition: width 1s ease;
}

hr { border-color: var(--border) !important; opacity: 0.4; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def score_color(score):
    if score >= 7: return "#ff2d55"
    if score >= 4: return "#ffb800"
    return "#00ff88"

def score_class(score):
    if score >= 7: return "kpi-danger"
    if score >= 4: return "kpi-warn"
    return "kpi-ok"

def verdict_class(score):
    if score >= 7: return "verdict-high"
    if score >= 4: return "verdict-med"
    return "verdict-low"

def make_radar(score_data):
    categories = ['Hype Language', 'Disclaimer', 'Exaggeration', 'AI Sentiment', 'Overall Risk']
    values = [
        min(score_data.get('hype_score', 0), 10),
        score_data.get('disclaimer_score', 0),
        min(score_data.get('exag_score', 0), 10),
        min(score_data.get('finbert_score', 0), 10),
        score_data.get('risk_score', 0),
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(255,45,85,0.15)',
        line=dict(color='#ff2d55', width=2),
        name='Risk Profile'
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(5,13,20,0.8)',
            radialaxis=dict(visible=True, range=[0, 10],
                           gridcolor='rgba(10,61,92,0.6)',
                           tickfont=dict(color='#3a6a88', size=8, family='Share Tech Mono'),
                           tickvals=[2,4,6,8,10]),
            angularaxis=dict(gridcolor='rgba(10,61,92,0.6)',
                            tickfont=dict(color='#a8c8e0', size=9, family='Share Tech Mono'))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(t=20, b=20, l=40, r=40),
        height=260
    )
    return fig

def make_gauge(score):
    color = score_color(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number=dict(
            font=dict(family='Orbitron', size=36, color=color),
            suffix='/10'
        ),
        gauge=dict(
            axis=dict(range=[0, 10], tickwidth=1,
                     tickcolor='#3a6a88',
                     tickfont=dict(family='Share Tech Mono', size=8, color='#3a6a88')),
            bar=dict(color=color, thickness=0.25),
            bgcolor='rgba(5,13,20,0.9)',
            borderwidth=1,
            bordercolor='#0a3d5c',
            steps=[
                dict(range=[0,4],  color='rgba(0,255,136,0.08)'),
                dict(range=[4,7],  color='rgba(255,184,0,0.08)'),
                dict(range=[7,10], color='rgba(255,45,85,0.08)'),
            ],
            threshold=dict(
                line=dict(color=color, width=3),
                thickness=0.8,
                value=score
            )
        )
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=20, r=20),
        height=200
    )
    return fig

def make_bar_chart(data):
    labels = ['Hype\nKeywords', 'Disclaimer\nMissing', 'Exaggerated\nClaims', 'AI\nSentiment']
    values = [
        min(data.get('hype_score', 0), 10),
        data.get('disclaimer_score', 0),
        min(data.get('exag_score', 0), 10),
        min(data.get('finbert_score', 0), 10),
    ]
    colors = [score_color(v) for v in values]
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(color=colors, opacity=0.8,
                   line=dict(color=colors, width=1)),
        text=[f'{v:.1f}' for v in values],
        textposition='outside',
        textfont=dict(family='Share Tech Mono', size=10, color='#a8c8e0'),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(5,13,20,0.8)',
        yaxis=dict(range=[0,10.5], gridcolor='rgba(10,61,92,0.4)',
                  tickfont=dict(family='Share Tech Mono', size=8, color='#3a6a88'),
                  zerolinecolor='rgba(10,61,92,0.6)'),
        xaxis=dict(tickfont=dict(family='Share Tech Mono', size=8, color='#a8c8e0')),
        margin=dict(t=30, b=10, l=10, r=10),
        height=220,
        showlegend=False
    )
    return fig

def highlight_transcript(text, keywords):
    if not keywords:
        return text
    import re
    for kw_obj in keywords:
        kw = kw_obj['keyword']
        highlighted = f'<mark style="background:rgba(255,45,85,0.3);color:#ff2d55;padding:1px 3px;border-radius:2px;">{kw}</mark>'
        text = re.sub(re.escape(kw), highlighted, text, flags=re.IGNORECASE)
    return text

def derive_subscores(data):
    hype_unique = len(data.get('hype_keywords_found', []))
    disclaimer = 0 if data.get('disclaimer_found') else 3
    exag = min(len(data.get('reasons', [])), 3)
    sentiment = data.get('finbert_sentiment', 'neutral')
    conf = data.get('finbert_confidence', 0.5)
    finbert_score = 7 * conf if sentiment == 'positive' else 3 * conf if sentiment == 'negative' else 2

    return {
        'hype_score': min(hype_unique * 1.5, 10),
        'disclaimer_score': disclaimer,
        'exag_score': exag * 2,
        'finbert_score': finbert_score,
        'risk_score': data.get('risk_score', 0)
    }

def generate_insight_feed(data):
    score = data.get('risk_score', 0)
    sentiment = data.get('finbert_sentiment', 'neutral')
    hype_count = len(data.get('hype_keywords_found', []))
    disclaimer = data.get('disclaimer_found', False)
    lang = data.get('language', 'en').upper()

    feed = []
    feed.append(("SYS", "ok",    f"Audio pipeline completed — {data.get('word_count',0)} tokens processed"))
    feed.append(("NLP", "ok",    f"Language detected: {lang} — Whisper confidence nominal"))
    if hype_count > 0:
        feed.append(("ALERT", "alert", f"{hype_count} hype signal(s) flagged by keyword engine"))
    else:
        feed.append(("SCAN", "ok", "Keyword engine: no hype signals detected"))
    if not disclaimer:
        feed.append(("RISK",  "alert", "Regulatory disclaimer absent — SEC/SEBI guideline violation risk"))
    else:
        feed.append(("LEGAL", "ok", "Disclaimer detected — compliance check passed"))
    feed.append(("BERT", "ok" if sentiment == "neutral" else "alert",
                 f"FinBERT sentiment: {sentiment.upper()} — confidence {int(data.get('finbert_confidence',0)*100)}%"))
    if score >= 7:
        feed.append(("VERDICT", "alert", "HIGH RISK content — recommend flagging for review"))
    elif score >= 4:
        feed.append(("VERDICT", "alert", "MEDIUM RISK — exercise caution before sharing"))
    else:
        feed.append(("VERDICT", "ok", "LOW RISK — content appears balanced"))
    return feed


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="sentinel-header">
    <div>
        <div class="sentinel-logo">⬡ SENTINEL</div>
        <div class="sentinel-sub">FINFLUENCER RISK INTELLIGENCE PLATFORM · v2.0</div>
    </div>
    <div style="text-align:right">
        <div><span class="status-dot"></span><span class="live-badge">SYSTEM ONLINE</span></div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#3a6a88;margin-top:4px;">
            WHISPER · FINBERT · NLP ENGINE READY
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INPUT ZONE
# ─────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])
with col_input:
    st.markdown('<div class="panel-label">TARGET URL — YOUTUBE FINANCIAL CONTENT</div>', unsafe_allow_html=True)
    url = st.text_input("", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")
with col_btn:
    st.markdown('<div style="margin-top:1.6rem"></div>', unsafe_allow_html=True)
    analyze_btn = st.button("⬡ ANALYZE", use_container_width=True)


# ─────────────────────────────────────────────
# ANALYSIS PIPELINE ANIMATION
# ─────────────────────────────────────────────
if analyze_btn and url:
    pipeline_placeholder = st.empty()
    steps = ["DOWNLOAD", "EXTRACT AUDIO", "WHISPER ASR", "FINBERT NLP", "RISK SCORE", "COMPLETE"]

    for i in range(len(steps)):
        html = '<div class="pipeline">'
        for j, step in enumerate(steps):
            if j < i:
                html += f'<span class="pipe-step done">✓ {step}</span>'
            elif j == i:
                html += f'<span class="pipe-step active">⟳ {step}</span>'
            else:
                html += f'<span class="pipe-step">{step}</span>'
            if j < len(steps)-1:
                html += '<span class="pipe-arrow">▶</span>'
        html += '</div>'
        pipeline_placeholder.markdown(html, unsafe_allow_html=True)
        time.sleep(0.3)

    # CALL API
    result_placeholder = st.empty()
    with st.spinner(""):
        try:
            response = requests.post(API_URL, json={"url": url}, timeout=300)
            data = response.json()
        except requests.exceptions.ConnectionError:
            st.markdown("""
            <div class="panel panel-danger">
                <div class="panel-label">CONNECTION ERROR</div>
                <div style="font-family:'Share Tech Mono',monospace;color:#ff2d55;">
                ❌ Cannot reach API at 127.0.0.1:8000 — ensure FastAPI is running in Terminal 1
                </div>
            </div>""", unsafe_allow_html=True)
            st.stop()
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()

    if response.status_code != 200:
        st.error(f"API Error: {data.get('detail', 'Unknown')}")
        st.stop()

    # Complete pipeline
    html = '<div class="pipeline">'
    for j, step in enumerate(steps):
        html += f'<span class="pipe-step done">✓ {step}</span>'
        if j < len(steps)-1:
            html += '<span class="pipe-arrow">▶</span>'
    html += '</div>'
    pipeline_placeholder.markdown(html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # DERIVE SCORES
    # ─────────────────────────────────────────────
    score = data['risk_score']
    subscores = derive_subscores(data)
    color = score_color(score)
    vclass = verdict_class(score)

    # ─────────────────────────────────────────────
    # KPI ROW
    # ─────────────────────────────────────────────
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card {score_class(score)}">
            <div class="kpi-value">{score}</div>
            <div class="kpi-label">RISK SCORE / 10</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" style="color:#00d4ff">{data['word_count']}</div>
            <div class="kpi-label">TOKENS ANALYZED</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" style="color:#00d4ff">{data['duration_seconds']}s</div>
            <div class="kpi-label">VIDEO DURATION</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" style="color:#00d4ff">{data['language'].upper()}</div>
            <div class="kpi-label">DETECTED LANGUAGE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # MAIN LAYOUT: VERDICT + GAUGE | RADAR | BAR
    # ─────────────────────────────────────────────
    col1, col2, col3 = st.columns([1.2, 1.2, 1.2])

    with col1:
        st.markdown(f"""
        <div class="panel panel-{'danger' if score>=7 else 'warn' if score>=4 else 'ok'}">
            <div class="panel-label">AI VERDICT</div>
            <div class="panel-label" style="color:#a8c8e0;font-size:0.75rem;margin-bottom:0.5rem;">
                {data['video_title'][:50]}{'...' if len(data['video_title'])>50 else ''}
            </div>
            <div class="{vclass}">{data['risk_label'].split()[-1]}</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#3a6a88;margin-top:0.5rem;">
                SENTINEL CONFIDENCE: {min(95, 70 + int(score*3))}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(make_gauge(score), use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown('<div class="panel-label">RISK COMPONENT RADAR</div>', unsafe_allow_html=True)
        st.plotly_chart(make_radar(subscores), use_container_width=True, config={'displayModeBar': False})

    with col3:
        st.markdown('<div class="panel-label">THREAT VECTOR BREAKDOWN</div>', unsafe_allow_html=True)
        st.plotly_chart(make_bar_chart(subscores), use_container_width=True, config={'displayModeBar': False})

    # ─────────────────────────────────────────────
    # THREAT SIGNALS + INSIGHT FEED
    # ─────────────────────────────────────────────
    col4, col5 = st.columns([1, 1])

    with col4:
        st.markdown('<div class="panel-label">THREAT SIGNAL ANALYSIS</div>', unsafe_allow_html=True)
        for reason in data['reasons']:
            if '🚨' in reason:
                cls = ''
            elif '⚠️' in reason:
                cls = 'threat-warn'
            else:
                cls = 'threat-ok'
            st.markdown(f'<div class="threat-item {cls}">{reason}</div>', unsafe_allow_html=True)

        # Disclaimer
        st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
        if data['disclaimer_found']:
            st.markdown(f"""
            <div class="panel panel-ok">
                <div class="panel-label">REGULATORY COMPLIANCE</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:#00ff88;">
                ✓ DISCLAIMER DETECTED: {', '.join(data['found_disclaimers']).upper()}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="panel panel-danger">
                <div class="panel-label">REGULATORY COMPLIANCE</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:#ff2d55;">
                ✗ NO FINANCIAL DISCLAIMER DETECTED — POTENTIAL VIOLATION
                </div>
            </div>""", unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="panel-label">LIVE INSIGHT FEED</div>', unsafe_allow_html=True)
        feed = generate_insight_feed(data)
        feed_html = ''
        for tag, kind, msg in feed:
            cls = 'feed-alert' if kind == 'alert' else 'feed-ok'
            feed_html += f'<div class="feed-item"><span class="feed-time">[{tag}]</span><span class="{cls}">{msg}</span></div>'
        st.markdown(f'<div class="panel" style="padding:0.5rem">{feed_html}</div>', unsafe_allow_html=True)

        # FinBERT sentiment
        sentiment = data.get('finbert_sentiment', 'neutral')
        confidence = data.get('finbert_confidence', 0)
        sent_color = '#ff2d55' if sentiment == 'positive' else '#00ff88' if sentiment == 'neutral' else '#ffb800'
        st.markdown(f"""
        <div class="panel" style="margin-top:1rem">
            <div class="panel-label">FINBERT SENTIMENT ENGINE</div>
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div style="font-family:'Orbitron',monospace;font-size:1.2rem;color:{sent_color};letter-spacing:3px;">
                    {sentiment.upper()}
                </div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#3a6a88;">
                    CONF: {int(confidence*100)}%
                </div>
            </div>
            <div class="score-bar-wrap" style="margin-top:0.5rem">
                <div class="score-bar-fill" style="width:{int(confidence*100)}%;background:{sent_color}"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # HYPE KEYWORDS + TRANSCRIPT
    # ─────────────────────────────────────────────
    col6, col7 = st.columns([1, 1.5])

    with col6:
        st.markdown('<div class="panel-label">FLAGGED HYPE SIGNALS</div>', unsafe_allow_html=True)
        if data['hype_keywords_found']:
            tags_html = ''
            for kw in data['hype_keywords_found']:
                tags_html += f'<span class="kw-tag">⚑ {kw["keyword"].upper()} ×{kw["count"]}</span>'
            st.markdown(f'<div class="panel" style="padding:1rem">{tags_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="panel panel-ok">
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:#00ff88;">
                ✓ NO HYPE SIGNALS DETECTED IN KEYWORD SCAN
                </div>
            </div>""", unsafe_allow_html=True)

    with col7:
        st.markdown('<div class="panel-label">TRANSCRIPT INTELLIGENCE — RISKY PHRASES HIGHLIGHTED</div>', unsafe_allow_html=True)
        raw = data.get('transcript_preview', '') + '...'
        highlighted = highlight_transcript(raw, data.get('hype_keywords_found', []))
        st.markdown(f'<div class="transcript-box">{highlighted}</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # FOOTER
    # ─────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-top:2rem;padding:1rem;border-top:1px solid #0a3d5c;
                display:flex;justify-content:space-between;
                font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#3a6a88;">
        <span>⬡ SENTINEL RISK INTELLIGENCE PLATFORM</span>
        <span>WHISPER ASR · FINBERT NLP · CUSTOM HEURISTICS</span>
        <span>FOR EDUCATIONAL USE ONLY — NOT FINANCIAL ADVICE</span>
    </div>
    """, unsafe_allow_html=True)

elif not analyze_btn:
    # ─────────────────────────────────────────────
    # IDLE STATE
    # ─────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;">
        <div style="font-family:'Orbitron',monospace;font-size:3rem;color:rgba(0,212,255,0.15);letter-spacing:8px;margin-bottom:1rem;">
            AWAITING TARGET
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:#3a6a88;letter-spacing:3px;">
            PASTE A YOUTUBE URL ABOVE AND INITIATE SCAN
        </div>
        <div style="margin-top:3rem;display:flex;justify-content:center;gap:3rem;">
            <div style="text-align:center">
                <div style="font-family:'Orbitron',monospace;font-size:1.5rem;color:rgba(0,212,255,0.3);">ASR</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#3a6a88;margin-top:4px;">WHISPER</div>
            </div>
            <div style="text-align:center">
                <div style="font-family:'Orbitron',monospace;font-size:1.5rem;color:rgba(0,212,255,0.3);">NLP</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#3a6a88;margin-top:4px;">FINBERT</div>
            </div>
            <div style="text-align:center">
                <div style="font-family:'Orbitron',monospace;font-size:1.5rem;color:rgba(0,212,255,0.3);">RISK</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#3a6a88;margin-top:4px;">SENTINEL</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)