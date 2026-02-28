"""Data transformation and cleaning functions for crypto datasets."""

import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_null_values(data: List[Dict]) -> List[Dict]:
    """Remove or replace null/None values in the data."""
    cleaned = []
    for coin in data:
        cleaned_coin = {}
        for key, value in coin.items():
            if value is None:
                # Replace nulls with appropriate defaults based on field type
                if key in ['current_price', 'price_change_24h', 'price_change_percentage_24h']:
                    cleaned_coin[key] = 0.0
                elif key in ['market_cap', 'total_volume']:
                    cleaned_coin[key] = 0
                elif key in ['market_cap_rank']:
                    cleaned_coin[key] = 9999  # High rank for missing
                else:
                    cleaned_coin[key] = value
            else:
                cleaned_coin[key] = value
        cleaned.append(cleaned_coin)
    logger.info(f"Cleaned null values for {len(cleaned)} records")
    return cleaned


def convert_numeric_fields(data: List[Dict]) -> List[Dict]:
    """Ensure numeric fields are properly typed."""
    for coin in data:
        # Convert price to float
        if 'current_price' in coin:
            coin['current_price'] = float(coin['current_price'] or 0)
        
        # Convert market cap and volume to int
        if 'market_cap' in coin:
            coin['market_cap'] = int(coin['market_cap'] or 0)
        if 'total_volume' in coin:
            coin['total_volume'] = int(coin['total_volume'] or 0)
        
        # Convert price change to float
        if 'price_change_24h' in coin:
            coin['price_change_24h'] = float(coin['price_change_24h'] or 0)
        
        # Convert rank to int
        if 'market_cap_rank' in coin:
            coin['market_cap_rank'] = int(coin['market_cap_rank'] or 9999)
    
    logger.info("Converted numeric fields")
    return data


def add_volatility_score(data: List[Dict]) -> List[Dict]:
    """
    Add volatility_score feature.
    volatility_score = abs(price_change_24h) * total_volume
    """
    for coin in data:
        price_change = abs(float(coin.get('price_change_24h', 0) or 0))
        volume = int(coin.get('total_volume', 0) or 0)
        coin['volatility_score'] = price_change * volume
    
    logger.info("Added volatility scores")
    return data


def add_extraction_timestamp(data: List[Dict]) -> List[Dict]:
    """Add extracted_at timestamp to all records."""
    timestamp = datetime.now()
    for coin in data:
        coin['extracted_at'] = timestamp
    logger.info(f"Added extraction timestamp: {timestamp}")
    return data


def select_required_fields(data: List[Dict]) -> List[Dict]:
    """Select only the required fields for database storage."""
    required_fields = [
        'id',  # This is coin_id from API
        'symbol',
        'name',
        'current_price',
        'market_cap',
        'total_volume',
        'price_change_24h',
        'market_cap_rank',
        'volatility_score',
        'extracted_at'
    ]
    
    transformed = []
    for coin in data:
        record = {
            'coin_id': coin.get('id', ''),
            'symbol': coin.get('symbol', '').upper(),
            'name': coin.get('name', ''),
            'current_price': coin.get('current_price', 0),
            'market_cap': coin.get('market_cap', 0),
            'total_volume': coin.get('total_volume', 0),
            'price_change_24h': coin.get('price_change_24h', 0),
            'market_cap_rank': coin.get('market_cap_rank', 9999),
            'volatility_score': coin.get('volatility_score', 0),
            'extracted_at': coin.get('extracted_at')
        }
        transformed.append(record)
    
    logger.info(f"Selected required fields for {len(transformed)} records")
    return transformed


def transform_data(raw_data: List[Dict]) -> List[Dict]:
    """
    Main transformation pipeline.
    
    Steps:
    1. Clean null values
    2. Convert numeric fields
    3. Add volatility score (feature engineering)
    4. Add extraction timestamp
    5. Select required fields
    
    Args:
        raw_data: Raw data from extraction
        
    Returns:
        Transformed data ready for loading
    """
    logger.info(f"Starting transformation of {len(raw_data)} records...")
    
    # Step 1: Clean null values
    data = clean_null_values(raw_data)
    
    # Step 2: Convert numeric fields
    data = convert_numeric_fields(data)
    
    # Step 3: Add volatility score
    data = add_volatility_score(data)
    
    # Step 4: Add extraction timestamp
    data = add_extraction_timestamp(data)
    
    # Step 5: Select required fields
    data = select_required_fields(data)
    
    logger.info(f"Transformation complete: {len(data)} records ready for loading")
    return data


if __name__ == "__main__":
    # Test with sample data
    sample_data = [
        {
            'id': 'bitcoin',
            'symbol': 'btc',
            'name': 'Bitcoin',
            'current_price': 50000.0,
            'market_cap': 1000000000000,
            'total_volume': 50000000000,
            'price_change_24h': 1500.0,
            'market_cap_rank': 1
        }
    ]
    
    result = transform_data(sample_data)
    print("Transformed data:")
    for record in result:
        print(f"  {record}")


