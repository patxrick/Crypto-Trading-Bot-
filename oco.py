import sys
import logging
from logger_config import setup_logging
from binance_client import BinanceFuturesClient, BinanceClientError
from validators import OrderValidator, ValidationError

logger = logging.getLogger(__name__)

class OCOOrderExecutor:
    def __init__(self):
        self.client = BinanceFuturesClient()
        logger.info("OCO order executor initialized")
    
    def execute(self, symbol: str, side: str, quantity: float,
                take_profit_price: float, stop_loss_price: float,
                stop_limit_price: float) -> dict:
        try:
            symbol = OrderValidator.validate_symbol(symbol)
            side = OrderValidator.validate_side(side)
            quantity = OrderValidator.validate_quantity(quantity)
            
            logger.info(f"Executing OCO order strategy", extra={
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'take_profit': take_profit_price,
                'stop_loss': stop_loss_price
            })
            
            tp_params = {
                'symbol': symbol,
                'side': side,
                'type': 'TAKE_PROFIT',
                'quantity': quantity,
                'price': take_profit_price,
                'stopPrice': take_profit_price,
                'timeInForce': 'GTC'
            }
            
            tp_result = self.client.place_order(tp_params)
            logger.info(f"Take-profit order placed", extra={'orderId': tp_result.get('orderId')})
            
            sl_params = {
                'symbol': symbol,
                'side': side,
                'type': 'STOP',
                'quantity': quantity,
                'price': stop_limit_price,
                'stopPrice': stop_loss_price,
                'timeInForce': 'GTC'
            }
            
            sl_result = self.client.place_order(sl_params)
            logger.info(f"Stop-loss order placed", extra={'orderId': sl_result.get('orderId')})
            
            result = {
                'take_profit_order': tp_result,
                'stop_loss_order': sl_result,
                'status': 'SUCCESS',
                'message': 'OCO strategy orders placed. Monitor and cancel manually when one fills.'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing OCO order: {str(e)}", exc_info=True)
            raise

def main():
    setup_logging()
    if len(sys.argv) < 7:
        print("Usage: python oco.py <SYMBOL> <SIDE> <QUANTITY> <TAKE_PROFIT_PRICE> <STOP_LOSS_PRICE> <STOP_LIMIT_PRICE>")
        print("Example: python oco.py BTCUSDT SELL 0.01 52000 49000 48800")
        sys.exit(1)
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = float(sys.argv[3])
    tp_price = float(sys.argv[4])
    sl_price = float(sys.argv[5])
    sl_limit = float(sys.argv[6])
    try:
        executor = OCOOrderExecutor()
        result = executor.execute(symbol, side, quantity, tp_price, sl_price, sl_limit)
        print("\n✓ OCO Orders Placed Successfully!")
        print(f"Take-Profit Order ID: {result['take_profit_order'].get('orderId')}")
        print(f"Stop-Loss Order ID: {result['stop_loss_order'].get('orderId')}")
        print(f"\nNote: Monitor orders and cancel the other when one executes")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
