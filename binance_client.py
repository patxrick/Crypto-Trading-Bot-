"""
Binance API client wrapper with error handling and retry logic
Implements HMAC SHA256 signature authentication
"""
import time
import hmac
import hashlib
import requests
import logging
from urllib.parse import urlencode
from typing import Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class BinanceClientError(Exception):
    """Custom exception for Binance API errors"""
    pass

class BinanceFuturesClient:
    """Client for Binance USDT-M Futures API"""
    
    def __init__(self):
        """Initialize Binance Futures client"""
        Config.validate()
        self.api_key = Config.API_KEY
        self.api_secret = Config.API_SECRET
        self.base_url = Config.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        logger.info("Binance Futures client initialized", extra={'testnet': Config.TESTNET})
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature for signed endpoints"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, signed: bool = False) -> Dict:
        """Make HTTP request to Binance API with retry logic"""
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        if signed:
    # Subtract 2 seconds to account for time ahead of server
            params['timestamp'] = int(time.time() * 1000) - 2000
            params['recvWindow'] = Config.DEFAULT_RECV_WINDOW
            params['signature'] = self._generate_signature(params)
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                logger.debug(f"API Request: {method} {endpoint}", extra={'attempt': attempt + 1})
                
                if method == 'GET':
                    response = self.session.get(url, params=params, timeout=10)
                elif method == 'POST':
                    response = self.session.post(url, params=params, timeout=10)
                elif method == 'DELETE':
                    response = self.session.delete(url, params=params, timeout=10)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Log rate limit headers
                if 'X-MBX-USED-WEIGHT-1M' in response.headers:
                    logger.debug(f"Rate limit used: {response.headers['X-MBX-USED-WEIGHT-1M']}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"API Success: {method} {endpoint}", extra={'status': response.status_code})
                    return data
                
                # Handle specific error codes
                elif response.status_code == 429:
                    logger.warning("Rate limit exceeded, backing off", extra={'retry_after': Config.RETRY_DELAY})
                    time.sleep(Config.RETRY_DELAY * (attempt + 1))
                    continue
                
                elif response.status_code in [418, 403]:
                    logger.critical("IP banned or WAF limit violated", extra={'status': response.status_code})
                    raise BinanceClientError(f"IP banned: {response.text}")
                
                else:
                    error_data = response.json()
                    logger.error(f"API Error: {error_data}", extra={'status': response.status_code})
                    raise BinanceClientError(f"API Error {response.status_code}: {error_data}")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}", extra={'attempt': attempt + 1}, exc_info=True)
                if attempt == Config.MAX_RETRIES - 1:
                    raise BinanceClientError(f"Max retries exceeded: {str(e)}")
                time.sleep(Config.RETRY_DELAY)
        
        raise BinanceClientError("Request failed after all retries")
    
    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict:
        """Get exchange trading rules and symbol information"""
        endpoint = "/fapi/v1/exchangeInfo"
        params = {'symbol': symbol} if symbol else {}
        return self._request('GET', endpoint, params, signed=False)
    
    def place_order(self, params: Dict) -> Dict:
        """Place a new order"""
        endpoint = "/fapi/v1/order"
        logger.info(f"Placing order", extra={'symbol': params.get('symbol'), 'side': params.get('side')})
        return self._request('POST', endpoint, params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an active order"""
        endpoint = "/fapi/v1/order"
        params = {'symbol': symbol, 'orderId': order_id}
        logger.info(f"Cancelling order", extra={'symbol': symbol, 'orderId': order_id})
        return self._request('DELETE', endpoint, params, signed=True)
    
    def get_order(self, symbol: str, order_id: int) -> Dict:
        """Query order status"""
        endpoint = "/fapi/v1/order"
        params = {'symbol': symbol, 'orderId': order_id}
        return self._request('GET', endpoint, params, signed=True)
    
    def get_account_info(self) -> Dict:
        """Get current account information"""
        endpoint = "/fapi/v2/account"
        return self._request('GET', endpoint, signed=True)
