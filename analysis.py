"""Analytical functions and models for crypto data."""

import logging
from typing import List, Dict, Any, Optional
from database import get_connection, release_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def execute_query(query: str, params: tuple = None) -> List[Dict]:
    """Execute a query and return results as list of dicts."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


def get_latest_extraction_time() -> Optional[str]:
    """Get the most recent extraction timestamp."""
    query = "SELECT MAX(extracted_at) as latest FROM crypto_market;"
    result = execute_query(query)
    return result[0]['latest'] if result else None


def get_top_gainers(limit: int = 5) -> List[Dict]:
    """
    Get top N gainers by 24h price change.
    Uses the most recent extraction data.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT 
        coin_id, symbol, name, current_price, 
        price_change_24h, market_cap_rank
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time
    WHERE price_change_24h IS NOT NULL
    ORDER BY price_change_24h DESC
    LIMIT %s;
    """
    return execute_query(query, (limit,))


def get_top_losers(limit: int = 5) -> List[Dict]:
    """
    Get top N losers by 24h price change.
    Uses the most recent extraction data.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT 
        coin_id, symbol, name, current_price, 
        price_change_24h, market_cap_rank
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time
    WHERE price_change_24h IS NOT NULL
    ORDER BY price_change_24h ASC
    LIMIT %s;
    """
    return execute_query(query, (limit,))


def get_top_by_market_cap(limit: int = 5) -> List[Dict]:
    """
    Get top N coins by market cap.
    Uses the most recent extraction data.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT 
        coin_id, symbol, name, current_price, 
        market_cap, market_cap_rank
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time
    ORDER BY market_cap DESC
    LIMIT %s;
    """
    return execute_query(query, (limit,))


def get_average_market_cap() -> float:
    """
    Calculate average market cap from latest data.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT AVG(market_cap) as avg_market_cap
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time;
    """
    result = execute_query(query)
    return float(result[0]['avg_market_cap'] or 0)


def get_total_market_value() -> float:
    """
    Calculate total crypto market value from DB.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT SUM(market_cap) as total_value
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time;
    """
    result = execute_query(query)
    return float(result[0]['total_value'] or 0)


def get_volatility_ranking(limit: int = 10) -> List[Dict]:
    """
    Get coins ranked by volatility score.
    volatility_score = abs(price_change_24h) * total_volume
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT 
        coin_id, symbol, name, current_price,
        price_change_24h, total_volume, volatility_score,
        RANK() OVER (ORDER BY volatility_score DESC) as volatility_rank
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time
    ORDER BY volatility_score DESC
    LIMIT %s;
    """
    return execute_query(query, (limit,))


def get_all_latest_data() -> List[Dict]:
    """
    Get all coins from the latest extraction.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT *
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time
    ORDER BY market_cap_rank ASC;
    """
    return execute_query(query)


def get_market_summary() -> Dict:
    """
    Get a comprehensive market summary.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT 
        COUNT(*) as total_coins,
        SUM(market_cap) as total_market_cap,
        AVG(market_cap) as avg_market_cap,
        AVG(current_price) as avg_price,
        SUM(total_volume) as total_volume,
        AVG(price_change_24h) as avg_price_change,
        MAX(price_change_24h) as max_price_change,
        MIN(price_change_24h) as min_price_change,
        MAX(extracted_at) as last_updated
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time;
    """
    result = execute_query(query)
    return result[0] if result else {}


def get_price_history(coin_id: str, limit: int = 100) -> List[Dict]:
    """
    Get historical price data for a specific coin.
    """
    query = """
    SELECT 
        coin_id, symbol, name, current_price,
        market_cap, total_volume, price_change_24h,
        extracted_at
    FROM crypto_market
    WHERE coin_id = %s
    ORDER BY extracted_at DESC
    LIMIT %s;
    """
    return execute_query(query, (coin_id, limit))


def get_market_dominance() -> List[Dict]:
    """
    Calculate market dominance percentage for each coin.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    ),
    total AS (
        SELECT SUM(market_cap) as total_cap
        FROM crypto_market cm
        JOIN latest l ON cm.extracted_at = l.max_time
    )
    SELECT 
        coin_id, symbol, name, market_cap,
        ROUND((market_cap::numeric / total_cap::numeric * 100), 2) as dominance_pct
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time
    CROSS JOIN total
    ORDER BY market_cap DESC;
    """
    return execute_query(query)


def get_price_tiers() -> Dict:
    """
    Categorize coins by price tier.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT 
        CASE 
            WHEN current_price >= 10000 THEN 'Premium ($10K+)'
            WHEN current_price >= 1000 THEN 'High ($1K-$10K)'
            WHEN current_price >= 100 THEN 'Mid ($100-$1K)'
            WHEN current_price >= 1 THEN 'Low ($1-$100)'
            ELSE 'Micro (<$1)'
        END as tier,
        COUNT(*) as count,
        AVG(current_price) as avg_price,
        SUM(market_cap) as total_cap
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time
    GROUP BY 
        CASE 
            WHEN current_price >= 10000 THEN 'Premium ($10K+)'
            WHEN current_price >= 1000 THEN 'High ($1K-$10K)'
            WHEN current_price >= 100 THEN 'Mid ($100-$1K)'
            WHEN current_price >= 1 THEN 'Low ($1-$100)'
            ELSE 'Micro (<$1)'
        END
    ORDER BY avg_price DESC;
    """
    return execute_query(query)


def get_volume_to_mcap_ratio() -> List[Dict]:
    """
    Calculate volume to market cap ratio (liquidity indicator).
    Higher ratio = more liquid/actively traded.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT 
        coin_id, symbol, name, current_price,
        market_cap, total_volume,
        ROUND((total_volume::numeric / NULLIF(market_cap, 0)::numeric * 100), 4) as vol_mcap_ratio
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time
    WHERE market_cap > 0
    ORDER BY vol_mcap_ratio DESC;
    """
    return execute_query(query)


def get_market_sentiment() -> Dict:
    """
    Calculate overall market sentiment based on price changes.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT 
        COUNT(*) FILTER (WHERE price_change_24h > 0) as gainers_count,
        COUNT(*) FILTER (WHERE price_change_24h < 0) as losers_count,
        COUNT(*) FILTER (WHERE price_change_24h = 0) as unchanged_count,
        COUNT(*) as total_count,
        ROUND(AVG(price_change_24h)::numeric, 2) as avg_change,
        ROUND(STDDEV(price_change_24h)::numeric, 2) as change_stddev
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time;
    """
    result = execute_query(query)
    return result[0] if result else {}


def get_top_by_volume(limit: int = 10) -> List[Dict]:
    """
    Get top coins by trading volume.
    """
    query = """
    WITH latest AS (
        SELECT MAX(extracted_at) as max_time FROM crypto_market
    )
    SELECT 
        coin_id, symbol, name, current_price,
        market_cap, total_volume, price_change_24h
    FROM crypto_market cm
    JOIN latest l ON cm.extracted_at = l.max_time
    ORDER BY total_volume DESC
    LIMIT %s;
    """
    return execute_query(query, (limit,))


if __name__ == "__main__":
    print("\n=== Crypto Market Analysis ===")
    
    print("\n--- Market Summary ---")
    summary = get_market_summary()
    if summary:
        print(f"Total Coins: {summary.get('total_coins', 0)}")
        print(f"Total Market Cap: ${summary.get('total_market_cap', 0):,.0f}")
        print(f"Average Price: ${summary.get('avg_price', 0):,.2f}")
        print(f"Last Updated: {summary.get('last_updated')}")
    
    print("\n--- Top 5 Gainers (24h) ---")
    for coin in get_top_gainers(5):
        print(f"  {coin['symbol']}: +${coin['price_change_24h']:.2f}")
    
    print("\n--- Top 5 by Market Cap ---")
    for coin in get_top_by_market_cap(5):
        print(f"  {coin['name']}: ${coin['market_cap']:,}")
    
    print("\n--- Volatility Ranking ---")
    for coin in get_volatility_ranking(5):
        print(f"  {coin['symbol']}: Score={coin['volatility_score']:,.0f}")


