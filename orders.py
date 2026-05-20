from __future__ import annotations
from typing import Optional

from bot.client import BinanceClient, BinanceClientError
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    ValidationError,
)
from bot.logging_config import get_logger

logger = get_logger(__name__)


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: Optional[str | float] = None,
) -> dict:
    """Validate inputs and place an order. Returns the API response dict."""

    # --- validate ---
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)

    stop_price = None
    limit_price = None

    if order_type == "STOP_MARKET":
        stop_price = validate_price(price, "STOP_MARKET")
    else:
        limit_price = validate_price(price, order_type)

    # --- place ---
    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=limit_price,
            stop_price=stop_price,
        )
    except BinanceClientError:
        raise  # let the CLI layer handle display

    return response


def format_response(response: dict) -> str:
    """Return a human-readable summary of an order response."""
    lines = [
        "┌─────────────────────────────────────────┐",
        "│           ORDER PLACED SUCCESSFULLY      │",
        "└─────────────────────────────────────────┘",
        f"  Order ID    : {response.get('orderId', 'N/A')}",
        f"  Symbol      : {response.get('symbol', 'N/A')}",
        f"  Side        : {response.get('side', 'N/A')}",
        f"  Type        : {response.get('type', 'N/A')}",
        f"  Status      : {response.get('status', 'N/A')}",
        f"  Quantity    : {response.get('origQty', 'N/A')}",
        f"  Executed    : {response.get('executedQty', 'N/A')}",
        f"  Avg Price   : {response.get('avgPrice') or response.get('price') or 'N/A'}",
        f"  Time        : {response.get('updateTime', 'N/A')}",
    ]
    return "\n".join(lines)
