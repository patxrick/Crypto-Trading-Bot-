import sys
import logging
from logger_config import setup_logging
from binance_client import BinanceFuturesClient, BinanceClientError
from validators import OrderValidator, ValidationError

logger = logging.getLogger(__name__)

class StopLimitOrderExecutor:
    
    def __init__(self):
        self.client = BinanceFuturesClient()
        logger.info("Stop-limit order executor initialized")
    
    def execute(self, symbol: str, side: str, quantity: float, 
                stop_price: float, limit_price: float, 
                time_in_force: str = 'GTC') -> dict:
        try:
            symbol = OrderValidator.validate_symbol(symbol)
            side = OrderValidator.validate_side(side)
            quantity = OrderValidator.validate_quantity(quantity)
            stop_price = OrderValidator.validate_price(stop_price)
            limit_price = OrderValidator.validate_price(limit_price)
            
            order_params = {
                'symbol': symbol,
                'side': side,
                'type': 'STOP',
                'quantity': quantity,
                'price': limit_price,
                'stopPrice': stop_price,
                'timeInForce': time_in_force
            }
            
            logger.info(f"Executing stop-limit order", extra=order_params)
            
            result = self.client.place_order(order_params)
            
            logger.info(f"Stop-limit order placed successfully", extra={
                'orderId': result.get('orderId'),
                'stopPrice': result.get('stopPrice'),
                'price': result.get('price')
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing stop-limit order: {str(e)}", exc_info=True)
            raise

def main():
    setup_logging()
    
    if len(sys.argv) < 6:
        print("Usage: python stop_limit.py <SYMBOL> <SIDE> <QUANTITY> <STOP_PRICE> <LIMIT_PRICE> [TIME_IN_FORCE]")
        print("Example: python stop_limit.py BTCUSDT SELL 0.01 51000 50800 GTC")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = float(sys.argv[3])
    stop_price = float(sys.argv[4])
    limit_price = float(sys.argv[5])
    time_in_force = sys.argv[6] if len(sys.argv) > 6 else 'GTC'
    
    try:
        executor = StopLimitOrderExecutor()
        result = executor.execute(symbol, side, quantity, stop_price, limit_price, time_in_force)
        
        print("\n✓ Stop-Limit Order Placed Successfully!")
        print(f"Order ID: {result.get('orderId')}")
        print(f"Stop Price: {result.get('stopPrice')}")
        print(f"Limit Price: {result.get('price')}")
        print(f"Status: {result.get('status')}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
