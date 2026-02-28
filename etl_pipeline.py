"""Orchestration entrypoint for the end-to-end ETL pipeline."""

import logging
import os
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import ETL_INTERVAL_MINUTES, LOGS_DIR
from database import setup_database
from extract import extract_crypto_data
from transform import transform_data
from load import load_data

# Ensure logs directory exists
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configure logging
log_file = os.path.join(LOGS_DIR, f'etl_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_etl_pipeline():
    """
    Execute the complete ETL pipeline.
    
    Steps:
    1. Extract data from CoinGecko API
    2. Transform and clean the data
    3. Load into PostgreSQL database
    """
    start_time = datetime.now()
    logger.info("="*50)
    logger.info(f"ETL Pipeline started at {start_time}")
    logger.info("="*50)
    
    try:
        # Step 1: Extract
        logger.info("STEP 1: Extracting data...")
        raw_data = extract_crypto_data(save_raw=True)
        logger.info(f"Extracted {len(raw_data)} records")
        
        # Step 2: Transform
        logger.info("STEP 2: Transforming data...")
        transformed_data = transform_data(raw_data)
        logger.info(f"Transformed {len(transformed_data)} records")
        
        # Step 3: Load
        logger.info("STEP 3: Loading data...")
        load_result = load_data(transformed_data)
        logger.info(f"Load result: {load_result}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("="*50)
        logger.info(f"ETL Pipeline completed successfully!")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Records processed: {load_result['success_count']}")
        logger.info("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"ETL Pipeline failed: {e}")
        logger.exception("Full traceback:")
        return False


def run_scheduled_pipeline():
    """
    Run the ETL pipeline on a schedule using APScheduler.
    Runs every ETL_INTERVAL_MINUTES (default: 5 minutes).
    """
    logger.info(f"Starting scheduled ETL pipeline (every {ETL_INTERVAL_MINUTES} minutes)")
    
    # Setup database tables first
    logger.info("Setting up database...")
    setup_database()
    
    # Run once immediately
    run_etl_pipeline()
    
    # Create scheduler
    scheduler = BlockingScheduler()
    
    # Add job to run every X minutes
    scheduler.add_job(
        run_etl_pipeline,
        trigger=IntervalTrigger(minutes=ETL_INTERVAL_MINUTES),
        id='etl_job',
        name='Crypto ETL Pipeline',
        replace_existing=True
    )
    
    logger.info(f"Scheduler started. Press Ctrl+C to stop.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user.")
        scheduler.shutdown()


def run_once():
    """Run the ETL pipeline once (no scheduling)."""
    logger.info("Running ETL pipeline once...")
    setup_database()
    return run_etl_pipeline()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Crypto ETL Pipeline')
    parser.add_argument('--once', action='store_true', help='Run once without scheduling')
    parser.add_argument('--schedule', action='store_true', help='Run with scheduling')
    args = parser.parse_args()
    
    if args.schedule:
        run_scheduled_pipeline()
    else:
        # Default: run once
        run_once()


