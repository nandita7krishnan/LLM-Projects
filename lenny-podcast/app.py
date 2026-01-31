"""Lenny's Podcast Intelligence Engine - Vintage Pixel UI"""

import streamlit as st
import sys
sys.path.insert(0, 'src')

from retriever import retrieve_chunks, get_episodes_by_topic, get_all_guests
from synthesizer import synthesize_answer, quick_answer, recommend_episodes

# Page config
st.set_page_config(
    page_title="LENNY.EXE",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Vintage Pixel Game Aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&family=Press+Start+2P&display=swap');
    
    :root {
        --teal: #66B3A6;
        --cream: #E9D5CA;
        --purple: #827397;
        --coral: #F48981;
    }
    
    .stApp {
        background-color: var(--cream);
    }
    
    /* Hide streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Main title */
    .pixel-title {
        font-family: 'Press Start 2P', monospace;
        font-size: 2rem;
        color: var(--purple);
        text-align: center;
        padding: 2rem 0;
        text-shadow: 4px 4px 0px var(--teal);
        letter-spacing: 2px;
    }
    
    .pixel-subtitle {
        font-family: 'VT323', monospace;
        font-size: 1.5rem;
        color: var(--purple);
        text-align: center;
        margin-top: -1rem;
        opacity: 0.8;
    }
    
    /* Cards */
    .result-card {
        background: white;
        border: 4px solid var(--purple);
        border-radius: 0;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 8px 8px 0px var(--teal);
        font-family: 'VT323', monospace;
    }
    
    .result-card h3 {
        font-family: 'Press Start 2P', monospace;
        font-size: 0.8rem;
        color: var(--coral);
        margin-bottom: 0.5rem;
    }
    
    .result-card .timestamp {
        font-size: 1rem;
        color: var(--teal);
        font-weight: bold;
    }
    
    .result-card .content {
        font-size: 1.2rem;
        color: #333;
        line-height: 1.6;
    }
    
    .result-card .meta {
        font-size: 1rem;
        color: var(--purple);
        margin-top: 0.5rem;
    }
    
    /* Answer box */
    .answer-box {
        background: var(--purple);
        color: var(--cream);
        border: 4px solid var(--coral);
        padding: 2rem;
        margin: 1.5rem 0;
        font-family: 'VT323', monospace;
        font-size: 1.4rem;
        line-height: 1.8;
        box-shadow: 8px 8px 0px var(--teal);
    }
    
    .answer-box h1, .answer-box h2, .answer-box h3, 
    .answer-box strong, .answer-box b {
        font-family: 'Press Start 2P', monospace;
        color: var(--coral);
        display: block;
        margin: 1.2rem 0 0.6rem 0;
        padding: 0.5rem 0.8rem;
        background: rgba(0,0,0,0.2);
        border-left: 4px solid var(--teal);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        animation: glitch 0.3s ease-in-out;
    }
    
    .answer-box h1:first-child, .answer-box h2:first-child, 
    .answer-box h3:first-child, .answer-box strong:first-child {
        margin-top: 0;
    }
    
    .answer-box ul, .answer-box ol {
        margin: 0.8rem 0 0.8rem 1.5rem;
    }
    
    .answer-box li {
        margin: 0.4rem 0;
        position: relative;
    }
    
    .answer-box li::marker {
        color: var(--coral);
    }
    
    @keyframes glitch {
        0%, 100% { transform: translateX(0); }
        20% { transform: translateX(-2px); }
        40% { transform: translateX(2px); }
        60% { transform: translateX(-1px); }
        80% { transform: translateX(1px); }
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        font-family: 'VT323', monospace;
        font-size: 1.3rem;
        border: 4px solid var(--purple);
        border-radius: 0;
        padding: 1rem;
        background: white;
        color: #333 !important;
        caret-color: var(--purple);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #999 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--coral);
        box-shadow: 4px 4px 0px var(--teal);
        color: #333 !important;
    }
    
    /* Buttons */
    .stButton > button {
        font-family: 'Press Start 2P', monospace;
        font-size: 0.7rem;
        background: var(--coral);
        color: white;
        border: 4px solid var(--purple);
        border-radius: 0;
        padding: 1rem 2rem;
        box-shadow: 4px 4px 0px var(--teal);
        transition: all 0.1s;
    }
    
    .stButton > button:hover {
        transform: translate(2px, 2px);
        box-shadow: 2px 2px 0px var(--teal);
    }
    
    .stButton > button:active {
        transform: translate(4px, 4px);
        box-shadow: none;
    }
    
    /* Mode selector */
    .mode-btn {
        display: inline-block;
        font-family: 'VT323', monospace;
        font-size: 1.2rem;
        padding: 0.8rem 1.5rem;
        margin: 0.5rem;
        cursor: pointer;
        border: 3px solid var(--purple);
        background: white;
        transition: all 0.1s;
    }
    
    .mode-btn:hover {
        background: var(--teal);
        color: white;
    }
    
    .mode-btn.active {
        background: var(--purple);
        color: var(--cream);
        box-shadow: 4px 4px 0px var(--coral);
    }
    
    /* Decorative elements */
    .pixel-divider {
        height: 4px;
        background: repeating-linear-gradient(
            90deg,
            var(--teal) 0px,
            var(--teal) 8px,
            var(--cream) 8px,
            var(--cream) 16px
        );
        margin: 2rem 0;
    }
    
    /* Stats bar */
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 3rem;
        padding: 1rem;
        font-family: 'VT323', monospace;
        font-size: 1.2rem;
        color: var(--purple);
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        font-family: 'Press Start 2P', monospace;
        font-size: 1.5rem;
        color: var(--coral);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--coral) !important;
    }
    
    /* Source pills */
    .source-pill {
        display: inline-block;
        background: var(--teal);
        color: white;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        font-family: 'VT323', monospace;
        font-size: 1rem;
        border: 2px solid var(--purple);
    }
    
    /* ═══ QUIRKY STUFF ═══ */
    
    /* Floating pixels background */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            radial-gradient(var(--teal) 1px, transparent 1px),
            radial-gradient(var(--coral) 1px, transparent 1px);
        background-size: 50px 50px, 80px 80px;
        background-position: 0 0, 25px 25px;
        opacity: 0.15;
        pointer-events: none;
        z-index: -1;
        animation: float 20s linear infinite;
    }
    
    @keyframes float {
        0% { transform: translate(0, 0); }
        50% { transform: translate(-10px, -10px); }
        100% { transform: translate(0, 0); }
    }
    
    /* Blink cursor effect on title */
    .pixel-title::after {
        content: "_";
        animation: blink 1s step-end infinite;
    }
    
    @keyframes blink {
        50% { opacity: 0; }
    }
    
    /* Scanline effect on answer box */
    .answer-box::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0,0,0,0.03) 2px,
            rgba(0,0,0,0.03) 4px
        );
        pointer-events: none;
    }
    
    .answer-box {
        position: relative;
        overflow: hidden;
    }
    
    /* Wiggle on hover for cards */
    .result-card {
        transition: transform 0.2s ease;
    }
    
    .result-card:hover {
        animation: wiggle 0.3s ease;
    }
    
    @keyframes wiggle {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(-1deg); }
        75% { transform: rotate(1deg); }
    }
    
    /* Rainbow shimmer on buttons */
    .stButton > button::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.3),
            transparent
        );
        transition: 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button {
        position: relative;
        overflow: hidden;
    }
    
    /* Typing effect pulse on input */
    .stTextInput > div > div > input:focus {
        animation: pulse-border 2s ease-in-out infinite;
    }
    
    @keyframes pulse-border {
        0%, 100% { border-color: var(--coral); }
        50% { border-color: var(--teal); }
    }
    
    /* Fun tooltip on divider hover */
    .pixel-divider {
        cursor: crosshair;
        transition: height 0.2s ease;
    }
    
    .pixel-divider:hover {
        height: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="pixel-title">🎮 LENNY.EXE 🎮</div>', unsafe_allow_html=True)
st.markdown('<div class="pixel-subtitle">[ INSERT COIN... jk it\'s free • 284 episodes of wisdom ]</div>', unsafe_allow_html=True)
st.markdown('<div class="pixel-divider"></div>', unsafe_allow_html=True)

# Mode selection
col1, col2, col3 = st.columns(3)
with col1:
    quick_mode = st.button("⚡ QUICK", use_container_width=True)
with col2:
    deep_mode = st.button("🔮 DEEP DIVE", use_container_width=True)
with col3:
    recs_mode = st.button("📺 RECOMMEND", use_container_width=True)

# Determine mode
if 'mode' not in st.session_state:
    st.session_state.mode = 'quick'

if quick_mode:
    st.session_state.mode = 'quick'
elif deep_mode:
    st.session_state.mode = 'deep'
elif recs_mode:
    st.session_state.mode = 'recommend'

# Query input
st.markdown("<br>", unsafe_allow_html=True)

placeholders = {
    'quick': "What's the secret to saying no without crying?",
    'deep': "How do galaxy-brain PMs think about pricing?",
    'recommend': "I'm a confused PM at a chaotic Series A startup..."
}

query = st.text_input(
    label="",
    placeholder=placeholders.get(st.session_state.mode, "Ask anything..."),
    key="query_input"
)

# Process query
if query:
    st.markdown('<div class="pixel-divider"></div>', unsafe_allow_html=True)
    
    if st.session_state.mode == 'quick':
        with st.spinner("🕹️ CONSULTING THE ORACLE..."):
            answer = quick_answer(query)
        
        st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)
        
        # Show sources
        results = retrieve_chunks(query, n_results=3)
        if results:
            st.markdown("### 📼 SOURCES")
            for r in results:
                st.markdown(f"""
                <div class="result-card">
                    <h3>{r.guest_name}</h3>
                    <div class="timestamp">⏱️ {r.start_timestamp}</div>
                    <div class="meta">{r.guest_role} • Tactical: {r.tactical_score}/10</div>
                    <div class="content">{r.text[:300]}...</div>
                </div>
                """, unsafe_allow_html=True)
    
    elif st.session_state.mode == 'deep':
        with st.spinner("🧠 BRAIN CELLS ACTIVATING..."):
            result = synthesize_answer(query, n_chunks=5)
        
        st.markdown(f'<div class="answer-box">{result.answer}</div>', unsafe_allow_html=True)
        
        if result.sources:
            st.markdown("### 📼 SOURCES")
            cols = st.columns(2)
            for i, s in enumerate(result.sources):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="result-card">
                        <h3>{s['guest']}</h3>
                        <div class="timestamp">⏱️ {s['timestamp']}</div>
                        <div class="meta">{s['role']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    elif st.session_state.mode == 'recommend':
        with st.spinner("📼 REWINDING THE TAPES..."):
            result = recommend_episodes(query, n_chunks=10)
        
        st.markdown(f'<div class="answer-box">{result.answer}</div>', unsafe_allow_html=True)
        
        if result.sources:
            st.markdown("### 📺 EPISODES")
            for s in result.sources[:5]:
                st.markdown(f"""
                <div class="result-card">
                    <h3>{s['guest']}</h3>
                    <div class="meta">{s['role']}</div>
                    <div class="content">{s.get('summary', '')}</div>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="pixel-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; font-family: 'VT323', monospace; color: #827397; font-size: 1.2rem;">
    [ PRESS START TO LEARN ] • 284 episodes • 13,014 chunks • ∞ wisdom
    <br><span style="font-size: 0.9rem; opacity: 0.7;">⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️🅱️🅰️ for secret mode (jk)</span>
</div>
""", unsafe_allow_html=True)

