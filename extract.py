"""Data extraction routines for pulling crypto data from external sources."""

import requests
import json
import os
import logging
from datetime import datetime
from config import COINGECKO_API_URL, COINGECKO_PARAMS, RAW_DATA_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_raw_data_dir():
    """Create raw_data directory if it doesn't exist."""
    if not os.path.exists(RAW_DATA_DIR):
        os.makedirs(RAW_DATA_DIR)
        logger.info(f"Created directory: {RAW_DATA_DIR}")


def save_raw_json(data, filename=None):
    """Save raw JSON response locally for logging/debugging."""
    ensure_raw_data_dir()
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crypto_data_{timestamp}.json"
    
    filepath = os.path.join(RAW_DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Raw data saved to {filepath}")
    return filepath


def validate_response(data):
    """Validate the API response structure."""
    if not isinstance(data, list):
        raise ValueError("Expected a list of coins from API")
    
    if len(data) == 0:
        raise ValueError("No coins returned from API")
    
    required_fields = ['id', 'symbol', 'name', 'current_price', 'market_cap']
    for coin in data:
        for field in required_fields:
            if field not in coin:
                raise ValueError(f"Missing required field: {field}")
    
    logger.info(f"Response validated: {len(data)} coins received")
    return True


def extract_crypto_data(save_raw=True):
    """
    Extract top 20 cryptocurrencies from CoinGecko API.
    
    Args:
        save_raw: Whether to save raw JSON locally
        
    Returns:
        List of coin data dictionaries
    """
    logger.info("Starting data extraction from CoinGecko API...")
    
    try:
        # Make API request with timeout and rate limiting consideration
        response = requests.get(
            COINGECKO_API_URL,
            params=COINGECKO_PARAMS,
            timeout=30,
            headers={'Accept': 'application/json'}
        )
        
        # Check for rate limiting
        if response.status_code == 429:
            logger.warning("Rate limited by CoinGecko API. Please wait.")
            raise Exception("Rate limited - please try again later")
        
        # Raise exception for bad status codes
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Validate response structure
        validate_response(data)
        
        # Save raw JSON for logging
        if save_raw:
            save_raw_json(data)
        
        logger.info(f"Successfully extracted {len(data)} coins")
        return data
        
    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        raise
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise


if __name__ == "__main__":
    # Test extraction
    data = extract_crypto_data()
    print(f"Extracted {len(data)} coins")
    for coin in data[:3]:
        print(f"  - {coin['name']} ({coin['symbol']}): ${coin['current_price']}")


