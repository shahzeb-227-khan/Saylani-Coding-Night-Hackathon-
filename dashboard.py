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
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #12121a 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* KPI Card Styling */
    .kpi-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16162a 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
    }
    
    .kpi-label {
        font-size: 12px;
        font-weight: 500;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
    }
    
    .kpi-value-large {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .kpi-subtitle {
        font-size: 13px;
        color: #9ca3af;
    }
    
    .kpi-positive {
        color: #10b981 !important;
    }
    
    .kpi-negative {
        color: #ef4444 !important;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 18px;
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .section-icon {
        font-size: 20px;
    }
    
    /* Chart Container */
    .chart-container {
        background: linear-gradient(145deg, #1a1a2e 0%, #16162a 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Data Table Styling */
    .dataframe {
        background: #1a1a2e !important;
        border-radius: 12px;
    }
    
    /* Divider */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
        margin: 30px 0;
    }
    
    /* Title Styling */
    .dashboard-title {
        font-size: 36px;
        font-weight: 700;
        background: linear-gradient(90deg, #ffffff, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
    }
    
    .dashboard-subtitle {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 30px;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10b981;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Gainer/Loser Badge */
    .gainer-badge {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .loser-badge {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #374151;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4b5563;
    }
    
    /* Remove Streamlit elements padding */
    .stPlotlyChart {
        background: transparent;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e5e7eb;
    }
    
    /* Social Button Styling */
    .social-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 14px;
        font-weight: 500;
        text-decoration: none;
        transition: all 0.3s ease;
        margin: 4px;
        width: 100%;
    }
    
    .linkedin-btn {
        background: linear-gradient(135deg, #0077b5, #005885);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .linkedin-btn:hover {
        background: linear-gradient(135deg, #005885, #004466);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 119, 181, 0.4);
    }
    
    .github-btn {
        background: linear-gradient(135deg, #333, #1a1a1a);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .github-btn:hover {
        background: linear-gradient(135deg, #444, #222);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    
    /* Insight Card */
    .insight-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16162a 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .insight-title {
        font-size: 11px;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    
    .insight-value {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
    }
    
    .insight-subtitle {
        font-size: 11px;
        color: #9ca3af;
        margin-top: 4px;
    }
    
    /* Sentiment Indicator */
    .sentiment-bullish {
        color: #10b981;
    }
    
    .sentiment-bearish {
        color: #ef4444;
    }
    
    .sentiment-neutral {
        color: #f59e0b;
    }
    
    /* Mini Stats */
    .mini-stat {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .mini-stat:last-child {
        border-bottom: none;
    }
    
    .mini-stat-label {
        color: #6b7280;
        font-size: 12px;
    }
    
    .mini-stat-value {
        color: #e5e7eb;
        font-size: 12px;
        font-weight: 600;
    }
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
        title=dict(text=title, font=dict(size=14, color='#9ca3af'), x=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color='#9ca3af'),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.03)',
            zerolinecolor='rgba(255,255,255,0.05)',
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.03)',
            zerolinecolor='rgba(255,255,255,0.05)',
        ),
        hoverlabel=dict(
            bgcolor='#1a1a2e',
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
        st.markdown('<p class="dashboard-title">📊 Crypto Analytics</p>', unsafe_allow_html=True)
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
                <p style="color: #6b7280; font-size: 11px; margin-top: 8px;">
                    Last Update: {last_update.strftime("%H:%M:%S") if hasattr(last_update, 'strftime') else str(last_update)[:19]}
                </p>
            </div>
            ''', unsafe_allow_html=True)


def render_kpi_cards(summary, top_gainer, most_volatile):
    """Render the 4 KPI cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cap = format_number(summary.get('total_market_cap', 0))
        st.markdown(f'''
        <div class="kpi-card">
            <p class="kpi-label">💰 Total Market Cap</p>
            <p class="kpi-value kpi-value-large">{total_cap}</p>
            <p class="kpi-subtitle">Top 20 Cryptocurrencies</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        avg_price = summary.get('avg_price', 0)
        avg_price = float(avg_price) if avg_price else 0
        st.markdown(f'''
        <div class="kpi-card">
            <p class="kpi-label">📈 Average Price</p>
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
                <p class="kpi-label">🚀 Highest Gainer (24h)</p>
                <p class="kpi-value kpi-positive">{gainer['symbol'].upper()}</p>
                <p class="kpi-subtitle">
                    <span class="gainer-badge">+${change:,.2f} ({pct_change:+.2f}%)</span>
                </p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="kpi-card">
                <p class="kpi-label">🚀 Highest Gainer (24h)</p>
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
                <p class="kpi-label">⚡ Most Volatile</p>
                <p class="kpi-value" style="color: #f59e0b;">{vol['symbol'].upper()}</p>
                <p class="kpi-subtitle">Score: {format_number(vol_score, prefix="")}</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="kpi-card">
                <p class="kpi-label">⚡ Most Volatile</p>
                <p class="kpi-value">N/A</p>
                <p class="kpi-subtitle">No data available</p>
            </div>
            ''', unsafe_allow_html=True)


def render_market_cap_chart(data):
    """Render market cap bar chart using Plotly."""
    df = pd.DataFrame(data)
    df['market_cap_billions'] = df['market_cap'].astype(float) / 1e9
    df = df.sort_values('market_cap_billions', ascending=True)
    
    # Create gradient colors
    colors = px.colors.sequential.Purples[-len(df):]
    
    fig = go.Figure(go.Bar(
        x=df['market_cap_billions'],
        y=df['symbol'].str.upper(),
        orientation='h',
        marker=dict(
            color=df['market_cap_billions'],
            colorscale='Purples',
            line=dict(width=0)
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
    
    # Color based on positive/negative
    colors = ['#10b981' if x >= 0 else '#ef4444' for x in df['price_change_24h']]
    
    fig = go.Figure(go.Bar(
        x=df['price_change_24h'],
        y=df['symbol'].str.upper(),
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
    
    fig = go.Figure(go.Bar(
        x=df['volatility_score'],
        y=df['symbol'].str.upper(),
        orientation='h',
        marker=dict(
            color=df['volatility_score'],
            colorscale='Reds',
            line=dict(width=0)
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
    
    fig = go.Figure(go.Pie(
        labels=df['symbol'].str.upper(),
        values=df['total_volume'],
        hole=0.6,
        marker=dict(
            colors=px.colors.sequential.Viridis,
            line=dict(color='#1a1a2e', width=2)
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
        st.markdown('<p class="section-header"><span class="section-icon">🟢</span> Top 5 Gainers (24h)</p>', unsafe_allow_html=True)
        if gainers:
            for i, coin in enumerate(gainers[:5]):
                change = float(coin.get('price_change_24h', 0) or 0)
                price = float(coin.get('current_price', 0) or 0)
                pct = (change / price * 100) if price > 0 else 0
                st.markdown(f'''
                <div style="display: flex; justify-content: space-between; align-items: center; 
                            padding: 12px 16px; background: rgba(16, 185, 129, 0.05); 
                            border-radius: 10px; margin-bottom: 8px; border-left: 3px solid #10b981;">
                    <div>
                        <span style="font-weight: 600; color: #e5e7eb;">{coin['symbol'].upper()}</span>
                        <span style="color: #6b7280; font-size: 12px; margin-left: 8px;">{coin['name']}</span>
                    </div>
                    <div>
                        <span class="gainer-badge">+${change:,.2f}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No data available")
    
    with col2:
        st.markdown('<p class="section-header"><span class="section-icon">🔴</span> Top 5 Losers (24h)</p>', unsafe_allow_html=True)
        if losers:
            for i, coin in enumerate(losers[:5]):
                change = float(coin.get('price_change_24h', 0) or 0)
                st.markdown(f'''
                <div style="display: flex; justify-content: space-between; align-items: center; 
                            padding: 12px 16px; background: rgba(239, 68, 68, 0.05); 
                            border-radius: 10px; margin-bottom: 8px; border-left: 3px solid #ef4444;">
                    <div>
                        <span style="font-weight: 600; color: #e5e7eb;">{coin['symbol'].upper()}</span>
                        <span style="color: #6b7280; font-size: 12px; margin-left: 8px;">{coin['name']}</span>
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
    st.markdown('<p class="section-header"><span class="section-icon">📋</span> Market Overview</p>', unsafe_allow_html=True)
    
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
            <div style="font-size: 40px; margin-bottom: 8px;">📊</div>
            <h2 style="color: #e5e7eb; margin: 0; font-size: 18px;">Crypto Analytics</h2>
            <p style="color: #6b7280; font-size: 11px; margin-top: 4px;">Real-Time Market Intelligence</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Dashboard Controls
        st.markdown("### ⚙️ Dashboard Controls")
        
        auto_refresh = st.toggle("🔄 Auto-Refresh (60s)", value=True, help="Automatically refresh data every 60 seconds")
        
        if st.button("🔃 Refresh Now", use_container_width=True, type="primary"):
            st.rerun()
        
        st.markdown("---")
        
        # Market Sentiment
        st.markdown("### 📈 Market Sentiment")
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
                sentiment_emoji = "🟢"
            elif losers > gainers:
                sentiment_text = "BEARISH"
                sentiment_class = "sentiment-bearish"
                sentiment_emoji = "🔴"
            else:
                sentiment_text = "NEUTRAL"
                sentiment_class = "sentiment-neutral"
                sentiment_emoji = "🟡"
            
            st.markdown(f'''
            <div class="insight-card">
                <div class="insight-title">Overall Sentiment</div>
                <div class="insight-value {sentiment_class}">{sentiment_emoji} {sentiment_text}</div>
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
        st.markdown("### 📊 Quick Stats")
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
                <p style="color: #6b7280; font-size: 11px; margin-bottom: 4px;">Last Data Update</p>
                <p style="color: #a5b4fc; font-size: 12px; font-weight: 500;">{update_str}</p>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Social Links
        st.markdown("### 🔗 Connect With Me")
        
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
            <p style="color: #4b5563; font-size: 10px;">
                Built with ❤️ by Shahzeb Alam<br>
                Powered by Streamlit & PostgreSQL
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        return auto_refresh


def render_dominance_chart(data):
    """Render market dominance treemap."""
    df = pd.DataFrame(data)
    df['dominance_pct'] = df['dominance_pct'].astype(float)
    
    fig = px.treemap(
        df,
        path=['symbol'],
        values='market_cap',
        color='dominance_pct',
        color_continuous_scale='Purples',
        custom_data=['name', 'dominance_pct']
    )
    
    fig.update_traces(
        texttemplate='<b>%{label}</b><br>%{customdata[1]:.1f}%',
        hovertemplate='<b>%{customdata[0]}</b><br>Dominance: %{customdata[1]:.2f}%<extra></extra>'
    )
    
    fig.update_layout(
        **get_chart_layout(),
        height=350,
        coloraxis_showscale=False
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
            colorscale='Teal',
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
    
    colors = ['#8b5cf6', '#6366f1', '#3b82f6', '#06b6d4', '#10b981']
    
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
    
    # Render header
    render_header()
    
    # Divider
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Check for data
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
    
    # ========== KPI CARDS ==========
    render_kpi_cards(summary, top_gainers, volatility_data)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ========== ADDITIONAL KPI ROW ==========
    st.markdown('<p class="section-header"><span class="section-icon">💡</span> Market Insights</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vol = float(summary.get('total_volume', 0) or 0)
        st.markdown(f'''
        <div class="kpi-card">
            <p class="kpi-label">🔄 24h Volume</p>
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
                <p class="kpi-label">📊 Green Ratio</p>
                <p class="kpi-value" style="color: {color};">{ratio:.0f}%</p>
                <p class="kpi-subtitle">{gainers}/{total} Coins Up</p>
            </div>
            ''', unsafe_allow_html=True)
    
    with col4:
        if liquidity_data and len(liquidity_data) > 0:
            most_liquid = liquidity_data[0]
            st.markdown(f'''
            <div class="kpi-card">
                <p class="kpi-label">💧 Most Liquid</p>
                <p class="kpi-value" style="color: #06b6d4;">{most_liquid['symbol'].upper()}</p>
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
        st.markdown('<p class="section-header"><span class="section-icon">📊</span> Market Cap Distribution</p>', unsafe_allow_html=True)
        if market_cap_data:
            fig = render_market_cap_chart(market_cap_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<p class="section-header"><span class="section-icon">🌐</span> Market Dominance</p>', unsafe_allow_html=True)
        if dominance_data:
            fig = render_dominance_chart(dominance_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # ========== CHARTS SECTION ROW 2 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header"><span class="section-icon">📉</span> 24h Price Changes</p>', unsafe_allow_html=True)
        if all_data:
            fig = render_price_change_chart(all_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<p class="section-header"><span class="section-icon">⚡</span> Volatility Ranking</p>', unsafe_allow_html=True)
        if volatility_data:
            fig = render_volatility_chart(volatility_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # ========== CHARTS SECTION ROW 3 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header"><span class="section-icon">💧</span> Liquidity Ranking (Vol/MCap)</p>', unsafe_allow_html=True)
        if liquidity_data:
            fig = render_liquidity_chart(liquidity_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<p class="section-header"><span class="section-icon">🔄</span> Volume Distribution</p>', unsafe_allow_html=True)
        if all_data:
            fig = render_volume_chart(all_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ========== PRICE TIERS & ADDITIONAL INSIGHTS ==========
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<p class="section-header"><span class="section-icon">💰</span> Price Tiers</p>', unsafe_allow_html=True)
        if price_tiers:
            fig = render_price_tier_chart(price_tiers)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<p class="section-header"><span class="section-icon">🏆</span> Top Performers Summary</p>', unsafe_allow_html=True)
        
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
                    <div class="insight-card" style="border-left: 3px solid #10b981;">
                        <div class="insight-title">🥇 Best Gainer</div>
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
                    <div class="insight-card" style="border-left: 3px solid #ef4444;">
                        <div class="insight-title">📉 Biggest Loser</div>
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
                    <div class="insight-card" style="border-left: 3px solid #f59e0b;">
                        <div class="insight-title">⚡ Most Volatile</div>
                        <div class="insight-value" style="color: #f59e0b;">{most_vol['symbol'].upper()}</div>
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
    <div style="text-align: center; padding: 30px 0; color: #4b5563; font-size: 12px;">
        <p>Data sourced from CoinGecko API • Auto-refreshes every 60 seconds</p>
        <p style="margin-top: 4px;">Built with ❤️ by <a href="https://www.linkedin.com/in/shahzeb-alam-759b992a4/" target="_blank" style="color: #a5b4fc;">Shahzeb Alam</a></p>
        <p style="margin-top: 8px;">
            <a href="https://www.linkedin.com/in/shahzeb-alam-759b992a4/" target="_blank" style="color: #6b7280; margin: 0 10px;">LinkedIn</a>
            <a href="https://github.com/shahzeb-227-khan" target="_blank" style="color: #6b7280; margin: 0 10px;">GitHub</a>
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(60)
        st.rerun()


if __name__ == "__main__":
    main()


