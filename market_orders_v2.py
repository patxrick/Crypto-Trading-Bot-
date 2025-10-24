import os
import sys
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
print("Script started - debug")

def main():
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    use_testnet = os.getenv("USE_TESTNET", "True").lower() == "true"

    if not api_key or not api_secret:
        print("❌ Error: API key and secret must be set in .env file!")
        sys.exit(1)

    if len(sys.argv) != 4:
        print("Usage: python market_orders_v2.py SYMBOL SIDE QUANTITY")
        print("Example: python market_orders_v2.py BTCUSDT BUY 0.001")
        sys.exit(1)

    symbol = sys.argv[1]
    side = sys.argv[2].upper()
    quantity = float(sys.argv[3])

    try:
        client = Client(api_key, api_secret, testnet=use_testnet)
        client.FUTURES_API_URL = "https://testnet.binancefuture.com/fapi"
        print(f"\n✓ Connected to Binance USDT-M Futures {'Testnet' if use_testnet else 'Production'}!")
    except Exception as e:
        print(f"❌ Error initializing Binance client: {e}")
        sys.exit(1)

    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        print("\n✓ Market Order Executed Successfully!")
        print(f"Order ID: {order['orderId']}")
        print(f"Symbol: {order['symbol']}")
        print(f"Side: {order['side']}")
        print(f"Status: {order['status']}")
        print(f"Executed Qty: {order.get('executedQty', 'N/A')}")
        print(f"Response: {order}")
    except BinanceAPIException as e:
        print(f"\n❌ Binance API Error!")
        print(f"Status Code: {e.status_code}")
        print(f"Message: {e.message}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
