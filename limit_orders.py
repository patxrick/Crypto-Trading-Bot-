"""
Limit order execution module
Limit orders are placed at a specific price and executed when market reaches that price
"""
import sys
import logging
from logger_config import setup_logging
from binance_client import BinanceFuturesClient, BinanceClientError
from validators import OrderValidator, ValidationError

logger = logging.getLogger(__name__)

class LimitOrderExecutor:
    """Execute limit orders on Binance Futures"""
    
    def __init__(self):
        """Initialize limit order executor"""
        self.client = BinanceFuturesClient()
        logger.info("Limit order executor initialized")
    
    def execute(self, symbol: str, side: str, quantity: float, price: float, 
                time_in_force: str = 'GTC') -> dict:
        """
        Execute a limit order
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price
            time_in_force: GTC (Good Till Cancel), IOC (Immediate or Cancel), FOK (Fill or Kill)
            
        Returns:
            Order response from Binance API
        """
        try:
            # Validate inputs
            symbol = OrderValidator.validate_symbol(symbol)
            side = OrderValidator.validate_side(side)
            quantity = OrderValidator.validate_quantity(quantity)
            price = OrderValidator.validate_price(price)
            
            # Prepare order parameters
            order_params = {
                'symbol': symbol,
                'side': side,
                'type': 'LIMIT',
                'quantity': quantity,
                'price': price,
                'timeInForce': time_in_force
            }
            
            logger.info(f"Executing limit order", extra=order_params)
            
            # Place order
            result = self.client.place_order(order_params)
            
            logger.info(f"Limit order placed successfully", extra={
                'orderId': result.get('orderId'),
                'price': result.get('price'),
                'origQty': result.get('origQty')
            })
            
            return result
            
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            raise
        except BinanceClientError as e:
            logger.error(f"Binance API error: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
            raise

def main():
    """CLI entry point for limit orders"""
    setup_logging()
    
    if len(sys.argv) < 5:
        print("Usage: python limit_orders.py <SYMBOL> <SIDE> <QUANTITY> <PRICE> [TIME_IN_FORCE]")
        print("Example: python limit_orders.py BTCUSDT BUY 0.01 50000 GTC")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = sys.argv[3]
    price = sys.argv[4]
    time_in_force = sys.argv[5] if len(sys.argv) > 5 else 'GTC'
    
    try:
        executor = LimitOrderExecutor()
        result = executor.execute(symbol, side, float(quantity), float(price), time_in_force)
        
        print("\n✓ Limit Order Placed Successfully!")
        print(f"Order ID: {result.get('orderId')}")
        print(f"Symbol: {result.get('symbol')}")
        print(f"Side: {result.get('side')}")
        print(f"Quantity: {result.get('origQty')}")
        print(f"Price: {result.get('price')}")
        print(f"Time in Force: {result.get('timeInForce')}")
        print(f"Status: {result.get('status')}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
