"""Data loading utilities to persist transformed data to storage."""

import logging
from typing import List, Dict
from database import get_connection, release_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_upsert_query():
    """Create the INSERT query."""
    return """
    INSERT INTO crypto_market (
        coin_id, symbol, name, current_price, market_cap,
        total_volume, price_change_24h, market_cap_rank,
        volatility_score, extracted_at
    ) VALUES (
        %(coin_id)s, %(symbol)s, %(name)s, %(current_price)s, %(market_cap)s,
        %(total_volume)s, %(price_change_24h)s, %(market_cap_rank)s,
        %(volatility_score)s, %(extracted_at)s
    )
    ON CONFLICT (coin_id, extracted_at) DO UPDATE SET
        current_price   = EXCLUDED.current_price,
        market_cap      = EXCLUDED.market_cap,
        total_volume    = EXCLUDED.total_volume,
        price_change_24h = EXCLUDED.price_change_24h,
        market_cap_rank = EXCLUDED.market_cap_rank,
        volatility_score = EXCLUDED.volatility_score;
    """


def load_single_record(cursor, record: Dict) -> bool:
    """Load a single record into the database."""
    try:
        query = create_upsert_query()
        cursor.execute(query, record)
        return True
    except Exception as e:
        logger.error(f"Error loading record {record.get('coin_id')}: {e}")
        return False


def load_batch(data: List[Dict], batch_size: int = 100) -> Dict:
    """
    Load transformed data into PostgreSQL using batch inserts.
    
    Args:
        data: List of transformed records
        batch_size: Number of records per batch
        
    Returns:
        Dict with success count and error count
    """
    conn = None
    cursor = None
    success_count = 0
    error_count = 0
    
    logger.info(f"Starting batch load of {len(data)} records...")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Process in batches
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            for record in batch:
                if load_single_record(cursor, record):
                    success_count += 1
                else:
                    error_count += 1
            
            # Commit after each batch
            conn.commit()
            logger.info(f"Batch {i // batch_size + 1} committed: {len(batch)} records")
        
        logger.info(f"Load complete: {success_count} success, {error_count} errors")
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Batch load failed: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)
    
    return {
        'success_count': success_count,
        'error_count': error_count,
        'total': len(data)
    }


def load_data(transformed_data: List[Dict]) -> Dict:
    """
    Main load function - entry point for loading transformed data.
    
    Args:
        transformed_data: List of transformed records
        
    Returns:
        Load statistics
    """
    if not transformed_data:
        logger.warning("No data to load")
        return {'success_count': 0, 'error_count': 0, 'total': 0}
    
    return load_batch(transformed_data)


if __name__ == "__main__":
    from database import setup_database
    from transform import transform_data
    
    # Setup database first
    setup_database()
    
    # Test with sample data
    sample = [{
        'coin_id': 'test-coin',
        'symbol': 'TEST',
        'name': 'Test Coin',
        'current_price': 100.0,
        'market_cap': 1000000,
        'total_volume': 50000,
        'price_change_24h': 5.0,
        'market_cap_rank': 999,
        'volatility_score': 250000.0,
        'extracted_at': '2024-01-01 12:00:00'
    }]
    
    result = load_data(sample)
    print(f"Load result: {result}")


