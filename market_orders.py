"""
Market order execution module
Market orders are executed immediately at the best available price
"""
import sys
import logging
from logger_config import setup_logging
from binance_client import BinanceFuturesClient, BinanceClientError
from validators import OrderValidator, ValidationError

logger = logging.getLogger(__name__)

class MarketOrderExecutor:
    """Execute market orders on Binance Futures"""
    
    def __init__(self):
        """Initialize market order executor"""
        self.client = BinanceFuturesClient()
        logger.info("Market order executor initialized")
    
    def execute(self, symbol: str, side: str, quantity: float) -> dict:
        """
        Execute a market order
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            
        Returns:
            Order response from Binance API
        """
        try:
            # Validate inputs
            symbol = OrderValidator.validate_symbol(symbol)
            side = OrderValidator.validate_side(side)
            quantity = OrderValidator.validate_quantity(quantity)
            
            # Prepare order parameters
            order_params = {
                'symbol': symbol,
                'side': side,
                'type': 'MARKET',
                'quantity': quantity
            }
            
            logger.info(f"Executing market order", extra=order_params)
            
            # Place order
            result = self.client.place_order(order_params)
            
            logger.info(f"Market order executed successfully", extra={
                'orderId': result.get('orderId'),
                'executedQty': result.get('executedQty'),
                'avgPrice': result.get('avgPrice')
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
    """CLI entry point for market orders"""
    setup_logging()
    
    if len(sys.argv) != 4:
        print("Usage: python market_orders.py <SYMBOL> <SIDE> <QUANTITY>")
        print("Example: python market_orders.py BTCUSDT BUY 0.01")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = sys.argv[3]
    
    try:
        executor = MarketOrderExecutor()
        result = executor.execute(symbol, side, float(quantity))
        
        print("\n✓ Market Order Executed Successfully!")
        print(f"Order ID: {result.get('orderId')}")
        print(f"Symbol: {result.get('symbol')}")
        print(f"Side: {result.get('side')}")
        print(f"Executed Quantity: {result.get('executedQty')}")
        print(f"Average Price: {result.get('avgPrice')}")
        print(f"Status: {result.get('status')}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
