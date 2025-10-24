import sys
import time
import logging
from logger_config import setup_logging
from binance_client import BinanceFuturesClient, BinanceClientError
from validators import OrderValidator, ValidationError

logger = logging.getLogger(__name__)

class TWAPExecutor:
    
    def __init__(self):
        self.client = BinanceFuturesClient()
        logger.info("TWAP executor initialized")
    
    def execute(self, symbol: str, side: str, total_quantity: float,
                num_orders: int, interval_seconds: int) -> list:
        try:
            symbol = OrderValidator.validate_symbol(symbol)
            side = OrderValidator.validate_side(side)
            total_quantity = OrderValidator.validate_quantity(total_quantity)
            
            if num_orders < 1:
                raise ValidationError("Number of orders must be at least 1")
            
            if interval_seconds < 1:
                raise ValidationError("Interval must be at least 1 second")
            
            order_size = total_quantity / num_orders
            
            logger.info(f"Starting TWAP execution", extra={
                'symbol': symbol,
                'total_quantity': total_quantity,
                'num_orders': num_orders,
                'order_size': order_size,
                'interval': interval_seconds
            })
            
            results = []
            
            for i in range(num_orders):
                try:
                    logger.info(f"Executing TWAP slice {i+1}/{num_orders}")
                    
                    order_params = {
                        'symbol': symbol,
                        'side': side,
                        'type': 'MARKET',
                        'quantity': round(order_size, 8)
                    }
                    
                    result = self.client.place_order(order_params)
                    results.append(result)
                    
                    logger.info(f"TWAP slice {i+1} executed", extra={
                        'orderId': result.get('orderId'),
                        'executedQty': result.get('executedQty')
                    })
                    
                    if i < num_orders - 1:
                        time.sleep(interval_seconds)
                    
                except Exception as e:
                    logger.error(f"Error on TWAP slice {i+1}: {str(e)}", exc_info=True)
                    results.append({'error': str(e), 'slice': i+1})
            
            logger.info(f"TWAP execution completed", extra={
                'total_orders': len(results),
                'successful': len([r for r in results if 'orderId' in r])
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing TWAP: {str(e)}", exc_info=True)
            raise

def main():
    setup_logging()
    
    if len(sys.argv) < 6:
        print("Usage: python twap.py <SYMBOL> <SIDE> <TOTAL_QUANTITY> <NUM_ORDERS> <INTERVAL_SECONDS>")
        print("Example: python twap.py BTCUSDT BUY 0.1 10 60")
        print("  - Splits 0.1 BTC into 10 orders executed every 60 seconds")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    total_quantity = float(sys.argv[3])
    num_orders = int(sys.argv[4])
    interval = int(sys.argv[5])
    
    try:
        executor = TWAPExecutor()
        results = executor.execute(symbol, side, total_quantity, num_orders, interval)
        
        print(f"\n✓ TWAP Execution Completed!")
        print(f"Total Orders Placed: {len(results)}")
        
        total_executed = sum(float(r.get('executedQty', 0)) for r in results if 'orderId' in r)
        avg_price = sum(float(r.get('avgPrice', 0)) for r in results if 'avgPrice' in r) / len(results)
        
        print(f"Total Executed Quantity: {total_executed}")
        print(f"Average Execution Price: {avg_price:.2f}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
