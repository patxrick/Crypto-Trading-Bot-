"""
Configuration module for Binance Futures Trading Bot
Handles API credentials and global settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Binance API configuration"""
    
    # API Credentials (NEVER hardcode these!)
    API_KEY = os.getenv('BINANCE_API_KEY', '')
    API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    
    # API Endpoints
    TESTNET = os.getenv('USE_TESTNET', 'True').lower() == 'true'
    # For Spot Testnet
    BASE_URL = 'https://testnet.binance.vision/api' if TESTNET else 'https://api.binance.com/api'

    
    # Trading Parameters
    DEFAULT_RECV_WINDOW = 60000
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    # Logging
    LOG_FILE = 'bot.log'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.API_KEY or not cls.API_SECRET:
            raise ValueError("API_KEY and API_SECRET must be set in .env file")
        return True
