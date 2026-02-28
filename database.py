"""Database connection and access helpers for the crypto analytics project."""

import psycopg2
from psycopg2 import pool
import logging
from config import DATABASE_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection pool (min 1, max 10 connections)
connection_pool = None


def init_connection_pool(minconn=1, maxconn=10):
    """Initialize the connection pool."""
    global connection_pool
    try:
        connection_pool = pool.ThreadedConnectionPool(
            minconn,
            maxconn,
            host=DATABASE_CONFIG["host"],
            port=DATABASE_CONFIG["port"],
            database=DATABASE_CONFIG["database"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"],
            sslmode="require"
        )
        logger.info("Connection pool created successfully")
    except Exception as e:
        logger.error(f"Error creating connection pool: {e}")
        raise


def get_connection():
    """Get a connection from the pool or create a new one."""
    global connection_pool
    if connection_pool:
        return connection_pool.getconn()
    return psycopg2.connect(
        host=DATABASE_CONFIG["host"],
        port=DATABASE_CONFIG["port"],
        database=DATABASE_CONFIG["database"],
        user=DATABASE_CONFIG["user"],
        password=DATABASE_CONFIG["password"],
        sslmode="require"
    )


def release_connection(conn):
    """Return a connection to the pool."""
    global connection_pool
    if connection_pool:
        connection_pool.putconn(conn)
    else:
        conn.close()


def create_tables():
    """Create the crypto_market table if it doesn't exist."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create crypto_market table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS crypto_market (
            id SERIAL PRIMARY KEY,
            coin_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            current_price FLOAT,
            market_cap BIGINT,
            total_volume BIGINT,
            price_change_24h FLOAT,
            market_cap_rank INTEGER,
            volatility_score FLOAT,
            extracted_at TIMESTAMP NOT NULL,
            UNIQUE(coin_id, extracted_at)
        );
        """
        cursor.execute(create_table_sql)
        
        # Create indexes for better query performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_coin_id ON crypto_market(coin_id);",
            "CREATE INDEX IF NOT EXISTS idx_extracted_at ON crypto_market(extracted_at);",
            "CREATE INDEX IF NOT EXISTS idx_market_cap_rank ON crypto_market(market_cap_rank);"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        logger.info("Tables and indexes created successfully")
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creating tables: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


def test_connection():
    """Test the database connection."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"Connected successfully! PostgreSQL version: {version[0]}")
        cursor.close()
        release_connection(conn)
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


def setup_database():
    """Initialize database with tables and indexes."""
    logger.info("Setting up database...")
    if test_connection():
        return create_tables()
    return False


if __name__ == "__main__":
    setup_database()


