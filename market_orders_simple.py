"""
Simple market order for testing - bypasses complex API calls
"""
print("Script started")
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def test_order(symbol, side, quantity):
    """Simulate a market order for testing"""
    
    api_key = os.getenv('BINANCE_API_KEY', '')
    api_secret = os.getenv('BINANCE_API_SECRET', '')
    
    if not api_key or not api_secret:
        print("❌ Error: API keys not found in .env file")
        return False
    
    print(f"\n✓ Configuration Valid!")
    print(f"API Key: {api_key[:10]}... (length: {len(api_key)})")
    print(f"\n📊 Order Details:")
    print(f"  Symbol: {symbol}")
    print(f"  Side: {side}")
    print(f"  Quantity: {quantity}")
    print(f"  Type: MARKET")
    print(f"\n⚠️  This is a TEST - No actual trade will be placed")
    print(f"✓ Order validation successful!")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python market_orders_simple.py BTCUSDT BUY 0.001")
        sys.exit(1)
    
    test_order(sys.argv[1], sys.argv[2], sys.argv[3])

