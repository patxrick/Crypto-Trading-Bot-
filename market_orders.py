import sys
import logging
from logger_config import setup_logging
from binance_client import BinanceFuturesClient, BinanceClientError
from validators import OrderValidator, ValidationError

logger = logging.getLogger(__name__)

class MarketOrderExecutor:
    def __init__(self):
        self.client = BinanceFuturesClient()
        logger.info("Market order executor initialized")
    
    def execute(self, symbol: str, side: str, quantity: float) -> dict:
        try:
            symbol = OrderValidator.validate_symbol(symbol)
            side = OrderValidator.validate_side(side)
            quantity = OrderValidator.validate_quantity(quantity)
            
            order_params = {
                'symbol': symbol,
                'side': side,
                'type': 'MARKET',
                'quantity': quantity
            }
            
            logger.info(f"Executing market order", extra=order_params)
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
