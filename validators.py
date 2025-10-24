import re
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    pass

class OrderValidator:
    VALID_SIDES = ['BUY', 'SELL']
    VALID_ORDER_TYPES = ['MARKET', 'LIMIT', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET']
    VALID_TIME_IN_FORCE = ['GTC', 'IOC', 'FOK', 'GTX']
    
    @staticmethod
    def validate_symbol(symbol: str) -> str:
        if not symbol or not isinstance(symbol, str):
            raise ValidationError("Symbol must be a non-empty string")
        symbol = symbol.upper()
        if not re.match(r'^[A-Z0-9]+$', symbol):
            raise ValidationError(f"Invalid symbol format: {symbol}")
        logger.debug(f"Symbol validated: {symbol}")
        return symbol
    
    @staticmethod
    def validate_side(side: str) -> str:
        side = side.upper()
        if side not in OrderValidator.VALID_SIDES:
            raise ValidationError(f"Side must be one of {OrderValidator.VALID_SIDES}")
        logger.debug(f"Side validated: {side}")
        return side
    
    @staticmethod
    def validate_quantity(quantity: float) -> float:
        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            raise ValidationError(f"Quantity must be a number, got: {quantity}")
        if quantity <= 0:
            raise ValidationError(f"Quantity must be positive, got: {quantity}")
        logger.debug(f"Quantity validated: {quantity}")
        return quantity
    
    @staticmethod
    def validate_price(price: float) -> float:
        try:
            price = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price must be a number, got: {price}")
        if price <= 0:
            raise ValidationError(f"Price must be positive, got: {price}")
        logger.debug(f"Price validated: {price}")
        return price
    
    @staticmethod
    def validate_order_type(order_type: str) -> str:
        order_type = order_type.upper()
        if order_type not in OrderValidator.VALID_ORDER_TYPES:
            raise ValidationError(f"Order type must be one of {OrderValidator.VALID_ORDER_TYPES}")
        logger.debug(f"Order type validated: {order_type}")
        return order_type
