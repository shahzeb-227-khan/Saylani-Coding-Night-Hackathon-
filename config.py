"""Configuration settings for the crypto analytics project."""

import os

# Supabase PostgreSQL connection settings (using pooler)
DATABASE_CONFIG = {
    "host": "aws-1-ap-southeast-2.pooler.supabase.com",
    "port": "5432",
    "database": "postgres",
    "user": "postgres.vjobjdfdfnpydtvcbdem",
    "password": "9/$Uxs3tN&H#83@",
}

# Supabase API settings
SUPABASE_URL = "https://vjobjdfdfnpydtvcbdem.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZqb2JqZGZkZm5weWR0dmNiZGVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIyOTYwOTIsImV4cCI6MjA4Nzg3MjA5Mn0._htJhUmNYC4XTZnKrZX-tPC-aHe9xy0FZYajPiNBY60"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZqb2JqZGZkZm5weWR0dmNiZGVtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjI5NjA5MiwiZXhwIjoyMDg3ODcyMDkyfQ.Aqm8w0UzpzROngWpVvSkYKxapNp_zMsQpi6lWW8mxHI"

# CoinGecko API settings
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 20,
    "page": 1,
    "sparkline": "false"
}

# ETL Settings
ETL_INTERVAL_MINUTES = 5
RAW_DATA_DIR = "raw_data"
LOGS_DIR = "logs"


