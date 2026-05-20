from __future__ import annotations
from typing import Optional
from bot.logging_config import get_logger

logger = get_logger(__name__)

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(ValueError):
    pass


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s:
        raise ValidationError("Symbol cannot be empty.")
    if not s.isalnum():
        raise ValidationError(f"Symbol '{s}' must be alphanumeric (e.g. BTCUSDT).")
    logger.debug(f"Symbol validated: {s}")
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(f"Side must be one of {VALID_SIDES}, got '{s}'.")
    logger.debug(f"Side validated: {s}")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(f"Order type must be one of {VALID_ORDER_TYPES}, got '{t}'.")
    logger.debug(f"Order type validated: {t}")
    return t


def validate_quantity(quantity: str | float) -> float:
    try:
        q = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if q <= 0:
        raise ValidationError(f"Quantity must be positive, got {q}.")
    logger.debug(f"Quantity validated: {q}")
    return q


def validate_price(price: Optional[str | float], order_type: str) -> Optional[float]:
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price must be a number, got '{price}'.")
        if p <= 0:
            raise ValidationError(f"Price must be positive, got {p}.")
        logger.debug(f"Price validated: {p}")
        return p
    if order_type == "STOP_MARKET":
        if price is None:
            raise ValidationError("Stop price is required for STOP_MARKET orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Stop price must be a number, got '{price}'.")
        if p <= 0:
            raise ValidationError(f"Stop price must be positive, got {p}.")
        logger.debug(f"Stop price validated: {p}")
        return p
    return None
