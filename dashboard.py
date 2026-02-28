"""Dashboard and visualization entrypoint for crypto analytics."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

from analysis import (
    get_market_summary,
    get_top_gainers,
    get_top_losers,
    get_top_by_market_cap,
    get_volatility_ranking,
    get_all_latest_data,
    get_latest_extraction_time,
    get_market_dominance,
    get_price_tiers,
    get_volume_to_mcap_ratio,
    get_market_sentiment,
    get_top_by_volume
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Crypto Analytics | Real-Time Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING - Bloomberg/TradingView Inspired
# ============================================================================
st.markdown("""
<style>
    /* Import Google Fonts — Poppins (headings), Inter (body), JetBrains Mono (numbers) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --dark-coffee: #352208;
        --soft-fawn: #E1BB80;
        --olive-wood: #7B6B43;
        --olive-bark: #685634;
        --olive-wood-2: #806443;
    }

    /* Global Styles */
    .stApp {
        background: linear-gradient(180deg, var(--dark-coffee) 0%, var(--olive-bark) 45%, var(--olive-wood-2) 100%);
        font-family: 'Inter', sans-serif;
        color: #fdf6e9;
    }

    /* Typography system */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Poppins', sans-serif !important;
        color: #fdf6e9;
    }

    /* Hide Streamlit branding — keep sidebar toggle visible */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: none !important;
    }
    /* Hide the header decoration but keep the collapse arrow */
    [data-testid="stHeader"]::after { display: none; }
    /* Ensure sidebar expand arrow is always reachable */
    [data-testid="collapsedControl"] {
        color: #E1BB80 !important;
        z-index: 999 !important;
    }

    /* Main container */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Dashboard Title */
    .dashboard-title {
        font-family: 'Poppins', sans-serif;
        font-size: 36px;
        font-weight: 700;
        letter-spacing: -0.01em;
        background: linear-gradient(90deg, #fffaf0, var(--soft-fawn));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 6px;
    }

    .dashboard-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        font-weight: 400;
        color: rgba(249, 243, 233, 0.65);
        text-transform: uppercase;
        letter-spacing: 0.16em;
        margin-bottom: 24px;
    }

    /* KPI Cards */
    .kpi-card {
        background: radial-gradient(circle at top left, rgba(225, 187, 128, 0.12), transparent 55%),
                    linear-gradient(145deg, #3e2b12 0%, #241509 55%, #140b05 100%);
        border-radius: 18px;
        padding: 20px 22px;
        border: 1px solid rgba(225, 187, 128, 0.35);
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.8);
        transition: all 0.25s ease;
    }

    .kpi-card:hover {
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 26px 70px rgba(0, 0, 0, 0.9);
        border-color: rgba(225, 187, 128, 0.7);
    }

    .kpi-label {
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: rgba(249, 243, 233, 0.55);
        margin-bottom: 8px;
    }

    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 26px;
        font-weight: 600;
        color: #fdf6e9;
        margin-bottom: 2px;
    }

    .kpi-value-large {
        font-family: 'JetBrains Mono', monospace;
        font-size: 28px;
        font-weight: 600;
        background: linear-gradient(90deg, var(--soft-fawn), #fff2ce);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 4px;
    }

    .kpi-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-weight: 400;
        color: rgba(249, 243, 233, 0.55);
        margin-top: 4px;
    }

    .kpi-positive { color: #74d99c !important; }
    .kpi-negative { color: #f28f79 !important; }

    /* Section Headers */
    .section-header {
        font-family: 'Poppins', sans-serif;
        font-size: 17px;
        font-weight: 600;
        color: #fdf6e9;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(225, 187, 128, 0.28);
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: -0.01em;
    }

    .section-icon {
        font-size: 18px;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(225, 187, 128, 0.8), transparent);
        margin: 26px 0;
    }

    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(225, 187, 128, 0.08);
        border: 1px solid rgba(225, 187, 128, 0.6);
        color: var(--soft-fawn);
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.06em;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: var(--soft-fawn);
        box-shadow: 0 0 0 4px rgba(225, 187, 128, 0.18);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.35); opacity: 0.4; }
        100% { transform: scale(1); opacity: 1; }
    }

    /* Ticker */
    .ticker {
        position: relative;
        overflow: hidden;
        width: 100%;
        border-radius: 999px;
        border: 1px solid rgba(225, 187, 128, 0.4);
        background: radial-gradient(circle at top left, rgba(225, 187, 128, 0.35), transparent 60%),
                    linear-gradient(90deg, rgba(26, 16, 6, 0.96), rgba(48, 31, 11, 0.98));
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.85);
        margin-bottom: 22px;
        white-space: nowrap;
    }

    .ticker__inner {
        display: inline-block;
        white-space: nowrap;
        padding: 9px 0;
        animation: ticker-scroll 32s linear infinite;
    }

    .ticker-item {
        display: inline-flex;
        align-items: baseline;
        gap: 8px;
        padding: 0 24px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #fdf6e9;
        border-right: 1px solid rgba(225, 187, 128, 0.35);
    }

    .ticker-item span { font-weight: 500; }

    .ticker-up span:last-child { color: #74d99c; }
    .ticker-down span:last-child { color: #f28f79; }

    @keyframes ticker-scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    /* Gainer / Loser badges */
    .gainer-badge {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(116, 217, 156, 0.14);
        color: #74d99c;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 500;
    }

    .loser-badge {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(242, 143, 121, 0.14);
        color: #f28f79;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 500;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #1f1308; }
    ::-webkit-scrollbar-thumb {
        background: #3b2610;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #4a3116; }

    /* Plotly background */
    .stPlotlyChart { background: transparent; }

    div[data-testid="stMetricValue"] { font-size: 26px; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #201207 0%, #3b2610 55%, #251509 100%);
        border-right: 1px solid rgba(225, 187, 128, 0.25);
    }

    [data-testid="stSidebar"] .stMarkdown { color: #fdf6e9; }

    /* Social Buttons */
    .social-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 9px 18px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 500;
        text-decoration: none;
        transition: all 0.25s ease;
        margin: 4px 0;
        width: 100%;
    }

    .linkedin-btn {
        background: linear-gradient(135deg, #0a66c2, #084077);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 25px rgba(8, 64, 119, 0.65);
    }

    .linkedin-btn:hover { transform: translateY(-2px); filter: brightness(1.05); }

    .github-btn {
        background: linear-gradient(135deg, #24292f, #15181b);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.75);
    }

    .github-btn:hover { transform: translateY(-2px); filter: brightness(1.08); }

    /* Insight Cards */
    .insight-card {
        background: linear-gradient(145deg, #3e2b12 0%, #241509 55%, #140b05 100%);
        border-radius: 14px;
        padding: 14px 14px;
        border: 1px solid rgba(225, 187, 128, 0.35);
        margin-bottom: 10px;
    }

    .insight-title {
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        color: rgba(249, 243, 233, 0.6);
        margin-bottom: 4px;
    }

    .insight-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 19px;
        font-weight: 600;
        color: #fdf6e9;
    }

    .insight-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-weight: 400;
        color: rgba(249, 243, 233, 0.55);
        margin-top: 3px;
    }

    .sentiment-bullish { color: #74d99c; }
    .sentiment-bearish { color: #f28f79; }
    .sentiment-neutral { color: var(--soft-fawn); }

    /* Mini Stats */
    .mini-stat {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(225, 187, 128, 0.22);
    }
    .mini-stat:last-child { border-bottom: none; }
    .mini-stat-label { font-family: 'Inter', sans-serif; color: rgba(249, 243, 233, 0.6); font-size: 11px; }
    .mini-stat-value { font-family: 'JetBrains Mono', monospace; color: #fdf6e9; font-size: 11px; font-weight: 500; }

    /* DataFrame */
    .dataframe {
        background: #1b1007 !important;
        border-radius: 12px;
    }

    /* ---- Streamlit widget overrides (multiselect / selectbox / sidebar inputs) ---- */
    /* Multiselect container */
    div[data-baseweb="select"] {
        background: #2b1b0b !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] > div {
        background: #2b1b0b !important;
        border: 1px solid rgba(225,187,128,0.35) !important;
        border-radius: 10px !important;
        color: #fdf6e9 !important;
    }
    div[data-baseweb="select"] > div:focus-within {
        border-color: #E1BB80 !important;
        box-shadow: 0 0 0 1px #E1BB80 !important;
    }
    /* Tags / pills */
    span[data-baseweb="tag"] {
        background: linear-gradient(135deg, #685634, #806443) !important;
        border: none !important;
        color: #fdf6e9 !important;
        border-radius: 999px !important;
    }
    span[data-baseweb="tag"] span { color: #fdf6e9 !important; }
    span[data-baseweb="tag"] svg { fill: rgba(253,246,233,0.7) !important; }
    span[data-baseweb="tag"]:hover { filter: brightness(1.1); }
    /* Dropdown menu */
    ul[role="listbox"] {
        background: #2b1b0b !important;
        border: 1px solid rgba(225,187,128,0.3) !important;
        border-radius: 10px !important;
    }
    li[role="option"] { color: #fdf6e9 !important; }
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background: rgba(225,187,128,0.15) !important;
    }
    /* Clear / chevron icons */
    div[data-baseweb="select"] svg { fill: rgba(225,187,128,0.6) !important; }
    /* Toggle */
    div[data-testid="stToggle"] label span { color: #fdf6e9 !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def format_number(value, prefix="$", suffix=""):
    """Format large numbers with K, M, B, T suffixes."""
    if value is None:
        return "N/A"
    value = float(value)
    if abs(value) >= 1e12:
        return f"{prefix}{value/1e12:.2f}T{suffix}"
    elif abs(value) >= 1e9:
        return f"{prefix}{value/1e9:.2f}B{suffix}"
    elif abs(value) >= 1e6:
        return f"{prefix}{value/1e6:.2f}M{suffix}"
    elif abs(value) >= 1e3:
        return f"{prefix}{value/1e3:.2f}K{suffix}"
    else:
        return f"{prefix}{value:,.2f}{suffix}"


def format_percentage(value):
    """Format percentage with color indicator."""
    if value is None:
        return "N/A", "neutral"
    value = float(value)
    if value >= 0:
        return f"+{value:.2f}%", "positive"
    return f"{value:.2f}%", "negative"


def get_chart_layout(title=""):
    """Get consistent Plotly chart layout."""
    return dict(
        title=dict(text=title, font=dict(size=14, color='#d0bfa3'), x=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color='#f7f2e9'),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            gridcolor='rgba(249, 243, 233, 0.06)',
            zerolinecolor='rgba(249, 243, 233, 0.12)',
        ),
        yaxis=dict(
            gridcolor='rgba(249, 243, 233, 0.06)',
            zerolinecolor='rgba(249, 243, 233, 0.12)',
        ),
        hoverlabel=dict(
            bgcolor='#2b1b0b',
            font_size=12,
            font_family="Inter"
        )
    )


# ============================================================================
# COMPONENT FUNCTIONS
# ============================================================================
def render_header():
    """Render dashboard header with title and status."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<p class="dashboard-title">Crypto Analytics</p>', unsafe_allow_html=True)
        st.markdown('<p class="dashboard-subtitle">Real-time cryptocurrency market intelligence powered by CoinGecko</p>', unsafe_allow_html=True)
    
    with col2:
        last_update = get_latest_extraction_time()
        if last_update:
            st.markdown(f'''
            <div style="text-align: right; padding-top: 10px;">
                <div class="status-badge">
                    <span class="status-dot"></span>
                    Live Data
                </div>
                <p style="color: rgba(249,243,233,0.45); font-size: 11px; margin-top: 8px;">
                    Last Update: {last_update.strftime("%H:%M:%S") if hasattr(last_update, 'strftime') else str(last_update)[:19]}
                </p>
            </div>
            ''', unsafe_allow_html=True)


def render_ticker(data):
    """Render an animated market ticker strip."""
    if not data:
        return

    df = pd.DataFrame(data)
    if df.empty:
        return

    df = df.sort_values('market_cap_rank')

    items_html = []
    for _, row in df.iterrows():
        symbol = str(row.get('symbol', '')).upper()
        price = float(row.get('current_price', 0) or 0)
        change = float(row.get('price_change_24h', 0) or 0)
        direction_class = "ticker-up" if change >= 0 else "ticker-down"
        items_html.append(
            f'<div class="ticker-item {direction_class}">{symbol}<span>${price:,.2f}</span><span>{change:+.2f}</span></div>'
        )

    if not items_html:
        return

    ticker_html = f"""
    <div class="ticker">
        <div class="ticker__inner">
            {''.join(items_html)}
        </div>
    </div>
    """

    st.markdown(ticker_html, unsafe_allow_html=True)


def render_kpi_cards(summary, top_gainer, most_volatile):
    """Render the 4 KPI cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cap = format_number(summary.get('total_market_cap', 0))
        st.markdown(f'''
        <div class="kpi-card">
            <p class="kpi-label">Total Market Cap</p>
            <p class="kpi-value kpi-value-large">{total_cap}</p>
            <p class="kpi-subtitle">Top 20 Cryptocurrencies</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        avg_price = summary.get('avg_price', 0)
        avg_price = float(avg_price) if avg_price else 0
        st.markdown(f'''
        <div class="kpi-card">
            <p class="kpi-label">Average Price</p>
            <p class="kpi-value">${avg_price:,.2f}</p>
            <p class="kpi-subtitle">Across all tracked coins</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        if top_gainer:
            gainer = top_gainer[0]
            change = float(gainer.get('price_change_24h', 0) or 0)
            price = float(gainer.get('current_price', 0) or 0)
            pct_change = (change / price * 100) if price > 0 else 0
            st.markdown(f'''
            <div class="kpi-card">
                <p class="kpi-label">Top Gainer · 24h</p>
                <p class="kpi-value kpi-positive">{gainer['symbol'].upper()}</p>
                <p class="kpi-subtitle">
                    <span class="gainer-badge">+${change:,.2f} ({pct_change:+.2f}%)</span>
                </p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="kpi-card">
                <p class="kpi-label">Top Gainer · 24h</p>
                <p class="kpi-value">N/A</p>
                <p class="kpi-subtitle">No data available</p>
            </div>
            ''', unsafe_allow_html=True)
    
    with col4:
        if most_volatile:
            vol = most_volatile[0]
            vol_score = float(vol.get('volatility_score', 0) or 0)
            st.markdown(f'''
            <div class="kpi-card">
                <p class="kpi-label">Most Volatile</p>
                <p class="kpi-value" style="color: #E1BB80;">{vol['symbol'].upper()}</p>
                <p class="kpi-subtitle">Score: {format_number(vol_score, prefix="")}</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="kpi-card">
                <p class="kpi-label">Most Volatile</p>
                <p class="kpi-value">N/A</p>
                <p class="kpi-subtitle">No data available</p>
            </div>
            ''', unsafe_allow_html=True)


def render_market_cap_chart(data):
    """Render market cap bar chart using Plotly."""
    df = pd.DataFrame(data)
    df['market_cap_billions'] = df['market_cap'].astype(float) / 1e9
    df = df.sort_values('market_cap_billions', ascending=True)

    watchlist = set(s.upper() for s in st.session_state.get('watchlist_symbols', []))
    labels = [f"{sym.upper()} ★" if sym.upper() in watchlist else sym.upper() for sym in df['symbol']]

    bar_colors = ['#E1BB80' if sym.upper() in watchlist else '#685634' for sym in df['symbol']]

    fig = go.Figure(go.Bar(
        x=df['market_cap_billions'],
        y=labels,
        orientation='h',
        marker=dict(
            color=bar_colors,
            line=dict(color='#352208', width=1)
        ),
        hovertemplate='<b>%{y}</b><br>Market Cap: $%{x:.2f}B<extra></extra>'
    ))
    
    fig.update_layout(
        **get_chart_layout(),
        height=350,
        xaxis_title="Market Cap (Billions USD)",
        yaxis_title="",
        showlegend=False
    )
    
    return fig


def render_price_change_chart(data):
    """Render price change bar chart with positive/negative colors."""
    df = pd.DataFrame(data)
    df['price_change_24h'] = df['price_change_24h'].astype(float)
    df = df.sort_values('price_change_24h', ascending=True)

    watchlist = set(s.upper() for s in st.session_state.get('watchlist_symbols', []))
    labels = [f"{sym.upper()} ★" if sym.upper() in watchlist else sym.upper() for sym in df['symbol']]
    
    # Color based on positive/negative within the warm palette
    colors = ['#E1BB80' if x >= 0 else '#806443' for x in df['price_change_24h']]
    
    fig = go.Figure(go.Bar(
        x=df['price_change_24h'],
        y=labels,
        orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate='<b>%{y}</b><br>Change: $%{x:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        **get_chart_layout(),
        height=350,
        xaxis_title="Price Change (USD)",
        yaxis_title="",
        showlegend=False
    )
    
    # Add zero line
    fig.add_vline(x=0, line_width=1, line_color='rgba(255,255,255,0.2)')
    
    return fig


def render_volatility_chart(data):
    """Render volatility ranking chart."""
    df = pd.DataFrame(data)
    df['volatility_score'] = df['volatility_score'].astype(float) / 1e9  # Scale to billions
    df = df.sort_values('volatility_score', ascending=True)

    watchlist = set(s.upper() for s in st.session_state.get('watchlist_symbols', []))
    labels = [f"{sym.upper()} ★" if sym.upper() in watchlist else sym.upper() for sym in df['symbol']]

    fig = go.Figure(go.Bar(
        x=df['volatility_score'],
        y=labels,
        orientation='h',
        marker=dict(
            color='#806443',
            line=dict(color='#E1BB80', width=1)
        ),
        hovertemplate='<b>%{y}</b><br>Volatility: %{x:.2f}B<extra></extra>'
    ))
    
    fig.update_layout(
        **get_chart_layout(),
        height=350,
        xaxis_title="Volatility Score (Billions)",
        yaxis_title="",
        showlegend=False
    )
    
    return fig


def render_volume_chart(data):
    """Render volume distribution donut chart."""
    df = pd.DataFrame(data[:10])  # Top 10
    df['total_volume'] = df['total_volume'].astype(float)
    
    watchlist = set(s.upper() for s in st.session_state.get('watchlist_symbols', []))
    labels = [f"{sym.upper()} ★" if sym.upper() in watchlist else sym.upper() for sym in df['symbol']]
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=df['total_volume'],
        hole=0.6,
        marker=dict(
            colors=['#352208', '#685634', '#7B6B43', '#806443', '#E1BB80'] * 2,
            line=dict(color='#1a1007', width=2)
        ),
        textinfo='percent',
        textfont=dict(size=11, color='white'),
        hovertemplate='<b>%{label}</b><br>Volume: $%{value:,.0f}<br>Share: %{percent}<extra></extra>'
    ))
    
    fig.update_layout(
        **get_chart_layout(),
        height=350,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=10)
        ),
        annotations=[dict(
            text='Volume<br>Share',
            x=0.5, y=0.5,
            font_size=14,
            font_color='#9ca3af',
            showarrow=False
        )]
    )
    
    return fig


def render_gainers_losers(gainers, losers):
    """Render top gainers and losers section."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">Top 5 Gainers · 24h</p>', unsafe_allow_html=True)
        if gainers:
            for i, coin in enumerate(gainers[:5]):
                change = float(coin.get('price_change_24h', 0) or 0)
                price = float(coin.get('current_price', 0) or 0)
                pct = (change / price * 100) if price > 0 else 0
                st.markdown(f'''
                <div style="display: flex; justify-content: space-between; align-items: center; 
                            padding: 12px 16px; background: rgba(116, 217, 156, 0.06); 
                            border-radius: 10px; margin-bottom: 8px; border-left: 3px solid #74d99c;">
                    <div>
                        <span style="font-weight: 600; color: #fdf6e9;">{coin['symbol'].upper()}</span>
                        <span style="color: rgba(249,243,233,0.55); font-size: 12px; margin-left: 8px;">{coin['name']}</span>
                    </div>
                    <div>
                        <span class="gainer-badge">+${change:,.2f}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No data available")
    
    with col2:
        st.markdown('<p class="section-header">Top 5 Losers · 24h</p>', unsafe_allow_html=True)
        if losers:
            for i, coin in enumerate(losers[:5]):
                change = float(coin.get('price_change_24h', 0) or 0)
                st.markdown(f'''
                <div style="display: flex; justify-content: space-between; align-items: center; 
                            padding: 12px 16px; background: rgba(242, 143, 121, 0.06); 
                            border-radius: 10px; margin-bottom: 8px; border-left: 3px solid #f28f79;">
                    <div>
                        <span style="font-weight: 600; color: #fdf6e9;">{coin['symbol'].upper()}</span>
                        <span style="color: rgba(249,243,233,0.55); font-size: 12px; margin-left: 8px;">{coin['name']}</span>
                    </div>
                    <div>
                        <span class="loser-badge">${change:,.2f}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No data available")


def render_data_table(data):
    """Render the interactive data table."""
    st.markdown('<p class="section-header">Market Overview</p>', unsafe_allow_html=True)
    
    df = pd.DataFrame(data)
    
    # Format columns
    df_display = df[[
        'market_cap_rank', 'symbol', 'name', 'current_price',
        'market_cap', 'total_volume', 'price_change_24h', 'volatility_score'
    ]].copy()
    
    df_display.columns = [
        'Rank', 'Symbol', 'Name', 'Price', 'Market Cap', 'Volume 24h', 'Change 24h', 'Volatility'
    ]
    
    # Format numeric columns
    df_display['Symbol'] = df_display['Symbol'].str.upper()
    df_display['Price'] = df_display['Price'].apply(lambda x: f"${float(x):,.2f}")
    df_display['Market Cap'] = df_display['Market Cap'].apply(lambda x: format_number(x))
    df_display['Volume 24h'] = df_display['Volume 24h'].apply(lambda x: format_number(x))
    df_display['Change 24h'] = df_display['Change 24h'].apply(
        lambda x: f"+${float(x):,.2f}" if float(x) >= 0 else f"${float(x):,.2f}"
    )
    df_display['Volatility'] = df_display['Volatility'].apply(lambda x: format_number(float(x), prefix=""))
    
    # Display with styling
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Symbol": st.column_config.TextColumn("Symbol", width="small"),
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Price": st.column_config.TextColumn("Price", width="medium"),
            "Market Cap": st.column_config.TextColumn("Market Cap", width="medium"),
            "Volume 24h": st.column_config.TextColumn("Volume 24h", width="medium"),
            "Change 24h": st.column_config.TextColumn("Change 24h", width="medium"),
            "Volatility": st.column_config.TextColumn("Volatility", width="medium"),
        }
    )


# ============================================================================
# MAIN DASHBOARD
# ============================================================================
def render_sidebar():
    """Render the sidebar with controls, insights, and social links."""
    with st.sidebar:
        # Logo/Brand Section
        st.markdown('''
        <div style="text-align: center; padding: 20px 0; margin-bottom: 20px;">
            <h2 style="font-family: 'Poppins', sans-serif; color: #fdf6e9; margin: 0; font-size: 20px; font-weight: 600; letter-spacing: -0.01em;">Crypto Analytics</h2>
            <p style="font-family: 'Inter', sans-serif; color: rgba(249,243,233,0.50); font-size: 10px; margin-top: 6px; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 400;">Real-Time Market Intelligence</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Dashboard Controls
        st.markdown("### Dashboard Controls")
        
        auto_refresh = st.toggle("Auto-Refresh (60s)", value=True, help="Automatically refresh data every 60 seconds")
        
        if st.button("Refresh Now", use_container_width=True, type="primary"):
            st.rerun()
        
        st.markdown("---")
        
        # Market Sentiment
        st.markdown("### Market Sentiment")
        sentiment = get_market_sentiment()
        
        if sentiment:
            gainers = int(sentiment.get('gainers_count', 0) or 0)
            losers = int(sentiment.get('losers_count', 0) or 0)
            total = int(sentiment.get('total_count', 1) or 1)
            avg_change = float(sentiment.get('avg_change', 0) or 0)
            
            # Sentiment indicator
            if gainers > losers:
                sentiment_text = "BULLISH"
                sentiment_class = "sentiment-bullish"
                sentiment_icon = "▲"
            elif losers > gainers:
                sentiment_text = "BEARISH"
                sentiment_class = "sentiment-bearish"
                sentiment_icon = "▼"
            else:
                sentiment_text = "NEUTRAL"
                sentiment_class = "sentiment-neutral"
                sentiment_icon = "●"
            
            st.markdown(f'''
            <div class="insight-card">
                <div class="insight-title">Overall Sentiment</div>
                <div class="insight-value {sentiment_class}">{sentiment_icon} {sentiment_text}</div>
                <div class="insight-subtitle">Avg Change: ${avg_change:+.2f}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Gainers vs Losers
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'''
                <div class="insight-card" style="text-align: center;">
                    <div class="insight-title">Gainers</div>
                    <div class="insight-value sentiment-bullish">{gainers}</div>
                </div>
                ''', unsafe_allow_html=True)
            with col2:
                st.markdown(f'''
                <div class="insight-card" style="text-align: center;">
                    <div class="insight-title">Losers</div>
                    <div class="insight-value sentiment-bearish">{losers}</div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### Quick Stats")
        summary = get_market_summary()
        
        if summary:
            total_vol = float(summary.get('total_volume', 0) or 0)
            max_change = float(summary.get('max_price_change', 0) or 0)
            min_change = float(summary.get('min_price_change', 0) or 0)
            
            st.markdown(f'''
            <div class="insight-card">
                <div class="mini-stat">
                    <span class="mini-stat-label">Total Volume (24h)</span>
                    <span class="mini-stat-value">{format_number(total_vol)}</span>
                </div>
                <div class="mini-stat">
                    <span class="mini-stat-label">Best Performer</span>
                    <span class="mini-stat-value sentiment-bullish">+${max_change:,.2f}</span>
                </div>
                <div class="mini-stat">
                    <span class="mini-stat-label">Worst Performer</span>
                    <span class="mini-stat-value sentiment-bearish">${min_change:,.2f}</span>
                </div>
                <div class="mini-stat">
                    <span class="mini-stat-label">Coins Tracked</span>
                    <span class="mini-stat-value">{summary.get('total_coins', 0)}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Last Update
        last_update = get_latest_extraction_time()
        if last_update:
            update_str = last_update.strftime("%Y-%m-%d %H:%M:%S") if hasattr(last_update, 'strftime') else str(last_update)[:19]
            st.markdown(f'''
            <div style="text-align: center; padding: 10px 0;">
                <p style="color: rgba(249,243,233,0.55); font-size: 11px; margin-bottom: 4px;">Last Data Update</p>
                <p style="color: #E1BB80; font-size: 12px; font-weight: 500;">{update_str}</p>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Social Links
        st.markdown("### Connect")
        
        st.markdown('''
        <a href="https://www.linkedin.com/in/shahzeb-alam-759b992a4/" target="_blank" class="social-btn linkedin-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854V1.146zm4.943 12.248V6.169H2.542v7.225h2.401zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248-.822 0-1.359.54-1.359 1.248 0 .694.521 1.248 1.327 1.248h.016zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016a5.54 5.54 0 0 1 .016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225h2.4z"/>
            </svg>
            LinkedIn
        </a>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <a href="https://github.com/shahzeb-227-khan" target="_blank" class="social-btn github-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            GitHub
        </a>
        ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # About Section
        st.markdown('''
        <div style="text-align: center; padding: 10px 0;">
            <p style="color: rgba(249,243,233,0.35); font-size: 10px;">
                Built by Shahzeb Alam<br>
                Powered by Streamlit & PostgreSQL
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        return auto_refresh


def render_dominance_chart(data):
    """Render market dominance as an elegant horizontal bar chart."""
    df = pd.DataFrame(data)
    df['dominance_pct'] = df['dominance_pct'].astype(float)
    df = df.sort_values('dominance_pct', ascending=True)

    # Build a warm gradient palette from dark coffee to soft fawn
    n = len(df)
    palette = []
    for i in range(n):
        t = i / max(n - 1, 1)
        r = int(53 + t * (225 - 53))
        g = int(34 + t * (187 - 34))
        b = int(8 + t * (128 - 8))
        palette.append(f'rgb({r},{g},{b})')

    fig = go.Figure(go.Bar(
        x=df['dominance_pct'],
        y=df['symbol'].str.upper(),
        orientation='h',
        marker=dict(
            color=palette,
            line=dict(color='rgba(225,187,128,0.25)', width=1)
        ),
        text=df['dominance_pct'].apply(lambda v: f'{v:.1f}%'),
        textposition='outside',
        textfont=dict(size=11, color='#E1BB80'),
        hovertemplate='<b>%{y}</b><br>Dominance: %{x:.2f}%<extra></extra>'
    ))

    layout = get_chart_layout()
    layout['xaxis'] = dict(
        gridcolor='rgba(249,243,233,0.06)',
        zerolinecolor='rgba(249,243,233,0.12)',
        range=[0, df['dominance_pct'].max() * 1.18],
        title='Dominance %',
    )
    fig.update_layout(
        **layout,
        height=350,
        yaxis_title='',
        showlegend=False,
    )

    return fig


def render_liquidity_chart(data):
    """Render volume to market cap ratio chart."""
    df = pd.DataFrame(data[:10])
    df['vol_mcap_ratio'] = df['vol_mcap_ratio'].astype(float)
    df = df.sort_values('vol_mcap_ratio', ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df['vol_mcap_ratio'],
        y=df['symbol'].str.upper(),
        orientation='h',
        marker=dict(
            color=df['vol_mcap_ratio'],
            colorscale=[[0, '#352208'], [0.35, '#685634'], [0.65, '#806443'], [1, '#E1BB80']],
            line=dict(width=0)
        ),
        hovertemplate='<b>%{y}</b><br>Liquidity Ratio: %{x:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        **get_chart_layout(),
        height=350,
        xaxis_title="Volume/MCap Ratio (%)",
        yaxis_title="",
        showlegend=False
    )
    
    return fig


def render_price_tier_chart(data):
    """Render price tier distribution chart."""
    df = pd.DataFrame(data)

    colors = ['#352208', '#685634', '#7B6B43', '#806443', '#E1BB80']
    
    fig = go.Figure(go.Pie(
        labels=df['tier'],
        values=df['count'],
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='#1a1a2e', width=2)),
        textinfo='label+value',
        textfont=dict(size=10, color='white'),
        hovertemplate='<b>%{label}</b><br>Coins: %{value}<extra></extra>'
    ))
    
    fig.update_layout(
        **get_chart_layout(),
        height=300,
        showlegend=False,
        annotations=[dict(
            text='Price<br>Tiers',
            x=0.5, y=0.5,
            font_size=12,
            font_color='#9ca3af',
            showarrow=False
        )]
    )
    
    return fig


def main():
    """Main dashboard function."""
    
    # Render sidebar and get auto_refresh setting
    auto_refresh = render_sidebar()
    
    # Check for data and load everything up-front
    with st.spinner("Loading market data..."):
        summary = get_market_summary()
        
        if not summary or not summary.get('total_coins'):
            st.warning("⚠️ No data in database. Please run the ETL pipeline first: `python etl_pipeline.py --once`")
            return
        
        # Fetch all required data
        all_data = get_all_latest_data()
        top_gainers = get_top_gainers(5)
        top_losers = get_top_losers(5)
        volatility_data = get_volatility_ranking(10)
        market_cap_data = get_top_by_market_cap(10)
        dominance_data = get_market_dominance()
        liquidity_data = get_volume_to_mcap_ratio()
        price_tiers = get_price_tiers()

    # Watchlist controls (after data is available)
    if all_data:
        symbols = sorted({str(row['symbol']).upper() for row in all_data})
        with st.sidebar:
            st.markdown("### Watchlist")
            default_watch = st.session_state.get('watchlist_symbols', symbols[:5])
            st.multiselect(
                "Coins to focus on",
                options=symbols,
                default=default_watch,
                key="watchlist_symbols",
            )
    
    # Header & ticker
    render_header()
    render_ticker(all_data)
    
    # Divider
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ========== KPI CARDS ==========
    render_kpi_cards(summary, top_gainers, volatility_data)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ========== ADDITIONAL KPI ROW ==========
    st.markdown('<p class="section-header">Market Insights</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vol = float(summary.get('total_volume', 0) or 0)
        st.markdown(f'''
        <div class="kpi-card">
            <p class="kpi-label">24h Volume</p>
            <p class="kpi-value">{format_number(total_vol)}</p>
            <p class="kpi-subtitle">Total Trading Activity</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        if dominance_data and len(dominance_data) > 0:
            btc_dom = float(dominance_data[0].get('dominance_pct', 0) or 0)
            st.markdown(f'''
            <div class="kpi-card">
                <p class="kpi-label">₿ BTC Dominance</p>
                <p class="kpi-value" style="color: #f7931a;">{btc_dom:.1f}%</p>
                <p class="kpi-subtitle">Market Share</p>
            </div>
            ''', unsafe_allow_html=True)
    
    with col3:
        sentiment = get_market_sentiment()
        if sentiment:
            gainers = int(sentiment.get('gainers_count', 0) or 0)
            total = int(sentiment.get('total_count', 1) or 1)
            ratio = (gainers / total * 100) if total > 0 else 0
            color = "#10b981" if ratio >= 50 else "#ef4444"
            st.markdown(f'''
            <div class="kpi-card">
                <p class="kpi-label">Green Ratio</p>
                <p class="kpi-value" style="color: {color};">{ratio:.0f}%</p>
                <p class="kpi-subtitle">{gainers}/{total} Coins Up</p>
            </div>
            ''', unsafe_allow_html=True)
    
    with col4:
        if liquidity_data and len(liquidity_data) > 0:
            most_liquid = liquidity_data[0]
            st.markdown(f'''
            <div class="kpi-card">
                <p class="kpi-label">Most Liquid</p>
                <p class="kpi-value" style="color: #E1BB80;">{most_liquid['symbol'].upper()}</p>
                <p class="kpi-subtitle">Ratio: {float(most_liquid['vol_mcap_ratio']):.2f}%</p>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ========== GAINERS & LOSERS ==========
    render_gainers_losers(top_gainers, top_losers)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ========== CHARTS SECTION ROW 1 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">Market Cap Distribution</p>', unsafe_allow_html=True)
        if market_cap_data:
            fig = render_market_cap_chart(market_cap_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<p class="section-header">Market Dominance</p>', unsafe_allow_html=True)
        if dominance_data:
            fig = render_dominance_chart(dominance_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # ========== CHARTS SECTION ROW 2 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">24h Price Changes</p>', unsafe_allow_html=True)
        if all_data:
            fig = render_price_change_chart(all_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<p class="section-header">Volatility Ranking</p>', unsafe_allow_html=True)
        if volatility_data:
            fig = render_volatility_chart(volatility_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # ========== CHARTS SECTION ROW 3 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">Liquidity Ranking</p>', unsafe_allow_html=True)
        if liquidity_data:
            fig = render_liquidity_chart(liquidity_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<p class="section-header">Volume Distribution</p>', unsafe_allow_html=True)
        if all_data:
            fig = render_volume_chart(all_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ========== PRICE TIERS & ADDITIONAL INSIGHTS ==========
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<p class="section-header">Price Tiers</p>', unsafe_allow_html=True)
        if price_tiers:
            fig = render_price_tier_chart(price_tiers)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<p class="section-header">Top Performers Summary</p>', unsafe_allow_html=True)
        
        # Create a summary card
        if top_gainers and top_losers and volatility_data:
            top_gainer = top_gainers[0] if top_gainers else None
            top_loser = top_losers[0] if top_losers else None
            most_vol = volatility_data[0] if volatility_data else None
            
            tcol1, tcol2, tcol3 = st.columns(3)
            
            with tcol1:
                if top_gainer:
                    change = float(top_gainer.get('price_change_24h', 0) or 0)
                    st.markdown(f'''
                    <div class="insight-card" style="border-left: 3px solid #74d99c;">
                        <div class="insight-title">Best Gainer</div>
                        <div class="insight-value sentiment-bullish">{top_gainer['symbol'].upper()}</div>
                        <div class="insight-subtitle">{top_gainer['name']}</div>
                        <div style="margin-top: 8px;">
                            <span class="gainer-badge">+${change:,.2f}</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            with tcol2:
                if top_loser:
                    change = float(top_loser.get('price_change_24h', 0) or 0)
                    st.markdown(f'''
                    <div class="insight-card" style="border-left: 3px solid #f28f79;">
                        <div class="insight-title">Biggest Loser</div>
                        <div class="insight-value sentiment-bearish">{top_loser['symbol'].upper()}</div>
                        <div class="insight-subtitle">{top_loser['name']}</div>
                        <div style="margin-top: 8px;">
                            <span class="loser-badge">${change:,.2f}</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            with tcol3:
                if most_vol:
                    vol_score = float(most_vol.get('volatility_score', 0) or 0)
                    st.markdown(f'''
                    <div class="insight-card" style="border-left: 3px solid #E1BB80;">
                        <div class="insight-title">Most Volatile</div>
                        <div class="insight-value" style="color: #E1BB80;">{most_vol['symbol'].upper()}</div>
                        <div class="insight-subtitle">{most_vol['name']}</div>
                        <div style="margin-top: 8px; color: #9ca3af; font-size: 11px;">
                            Score: {format_number(vol_score, prefix="")}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ========== DATA TABLE ==========
    if all_data:
        render_data_table(all_data)
    
    # ========== FOOTER ==========
    st.markdown('''
    <div style="text-align: center; padding: 30px 0; color: rgba(249,243,233,0.35); font-size: 12px;">
        <p>Data sourced from CoinGecko API &middot; Auto-refreshes every 60 seconds</p>
        <p style="margin-top: 4px;">Built by <a href="https://www.linkedin.com/in/shahzeb-alam-759b992a4/" target="_blank" style="color: #E1BB80;">Shahzeb Alam</a></p>
        <p style="margin-top: 8px;">
            <a href="https://www.linkedin.com/in/shahzeb-alam-759b992a4/" target="_blank" style="color: rgba(249,243,233,0.4); margin: 0 10px;">LinkedIn</a>
            <a href="https://github.com/shahzeb-227-khan" target="_blank" style="color: rgba(249,243,233,0.4); margin: 0 10px;">GitHub</a>
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(60)
        st.rerun()


if __name__ == "__main__":
    main()


