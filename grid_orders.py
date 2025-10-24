import sys
import logging
from logger_config import setup_logging
from binance_client import BinanceFuturesClient, BinanceClientError
from validators import OrderValidator, ValidationError

logger = logging.getLogger(__name__)

class GridOrderExecutor:
    def __init__(self):
        self.client = BinanceFuturesClient()
        logger.info("Grid order executor initialized")
    
    def execute(self, symbol: str, lower_price: float, upper_price: float,
                num_grids: int, quantity_per_grid: float) -> dict:
        try:
            symbol = OrderValidator.validate_symbol(symbol)
            lower_price = OrderValidator.validate_price(lower_price)
            upper_price = OrderValidator.validate_price(upper_price)
            quantity_per_grid = OrderValidator.validate_quantity(quantity_per_grid)
            
            if upper_price <= lower_price:
                raise ValidationError("Upper price must be greater than lower price")
            
            if num_grids < 2:
                raise ValidationError("Number of grids must be at least 2")
            
            price_step = (upper_price - lower_price) / (num_grids - 1)
            
            logger.info(f"Starting grid order placement", extra={
                'symbol': symbol,
                'lower_price': lower_price,
                'upper_price': upper_price,
                'num_grids': num_grids,
                'price_step': price_step
            })
            
            buy_orders = []
            sell_orders = []
            mid_price = (lower_price + upper_price) / 2
            
            for i in range(num_grids):
                grid_price = round(lower_price + (i * price_step), 2)
                try:
                    if grid_price < mid_price:
                        order_params = {
                            'symbol': symbol,
                            'side': 'BUY',
                            'type': 'LIMIT',
                            'quantity': quantity_per_grid,
                            'price': grid_price,
                            'timeInForce': 'GTC'
                        }
                        result = self.client.place_order(order_params)
                        buy_orders.append(result)
                        logger.info(f"Buy grid order placed at {grid_price}", 
                                    extra={'orderId': result.get('orderId')})
                    
                    elif grid_price > mid_price:
                        order_params = {
                            'symbol': symbol,
                            'side': 'SELL',
                            'type': 'LIMIT',
                            'quantity': quantity_per_grid,
                            'price': grid_price,
                            'timeInForce': 'GTC'
                        }
                        result = self.client.place_order(order_params)
                        sell_orders.append(result)
                        logger.info(f"Sell grid order placed at {grid_price}",
                                    extra={'orderId': result.get('orderId')})
                except Exception as e:
                    logger.error(f"Error placing grid at {grid_price}: {str(e)}", exc_info=True)
            
            logger.info(f"Grid orders placed", extra={
                'buy_orders': len(buy_orders),
                'sell_orders': len(sell_orders)
            })
            
            return {
                'buy_orders': buy_orders,
                'sell_orders': sell_orders,
                'total_orders': len(buy_orders) + len(sell_orders)
            }
            
        except Exception as e:
            logger.error(f"Error executing grid strategy: {str(e)}", exc_info=True)
            raise

def main():
    setup_logging()
    if len(sys.argv) < 6:
        print("Usage: python grid_orders.py <SYMBOL> <LOWER_PRICE> <UPPER_PRICE> <NUM_GRIDS> <QUANTITY_PER_GRID>")
        print("Example: python grid_orders.py BTCUSDT 48000 52000 10 0.001")
        sys.exit(1)
    symbol = sys.argv[1]
    lower_price = float(sys.argv[2])
    upper_price = float(sys.argv[3])
    num_grids = int(sys.argv[4])
    quantity = float(sys.argv[5])
    try:
        executor = GridOrderExecutor()
        result = executor.execute(symbol, lower_price, upper_price, num_grids, quantity)
        print(f"\n✓ Grid Orders Placed Successfully!")
        print(f"Buy Orders: {len(result['buy_orders'])}")
        print(f"Sell Orders: {len(result['sell_orders'])}")
        print(f"Total Orders: {result['total_orders']}")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
