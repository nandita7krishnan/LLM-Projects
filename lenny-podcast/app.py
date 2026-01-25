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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="pixel-title">🎮 LENNY.EXE 🎮</div>', unsafe_allow_html=True)
st.markdown('<div class="pixel-subtitle">[ 284 episodes of PM wisdom at your fingertips ]</div>', unsafe_allow_html=True)
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
    'quick': "What's the best way to say no?",
    'deep': "How do top PMs think about pricing?",
    'recommend': "I'm a new PM at a Series A startup..."
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
        with st.spinner("LOADING..."):
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
        with st.spinner("SYNTHESIZING..."):
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
        with st.spinner("FINDING EPISODES..."):
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
</div>
""", unsafe_allow_html=True)

