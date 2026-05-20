#!/usr/bin/env python3
"""
Trading Bot CLI
Usage examples:
  python cli.py place --symbol BTCUSDT --side BUY  --type MARKET --qty 0.01
  python cli.py place --symbol BTCUSDT --side SELL --type LIMIT  --qty 0.01 --price 80000
  python cli.py place --symbol BTCUSDT --side BUY  --type STOP_MARKET --qty 0.01 --price 60000
"""
from __future__ import annotations
import argparse
import os
import sys

from bot.client import BinanceClient, BinanceClientError
from bot.orders import place_order, format_response
from bot.validators import ValidationError
from bot.logging_config import get_logger

logger = get_logger("cli")


# ── Credentials ──────────────────────────────────────────────────────────────

def _get_credentials() -> tuple[str, str]:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        print("\n❌  Missing API credentials.")
        print("    Set them as environment variables before running:\n")
        print("    export BINANCE_API_KEY=your_key_here")
        print("    export BINANCE_API_SECRET=your_secret_here\n")
        sys.exit(1)
    return api_key, api_secret


# ── Subcommand: place ─────────────────────────────────────────────────────────

def cmd_place(args: argparse.Namespace) -> None:
    print("\n──────────────────────────────────────────")
    print("  ORDER REQUEST SUMMARY")
    print("──────────────────────────────────────────")
    print(f"  Symbol     : {args.symbol.upper()}")
    print(f"  Side       : {args.side.upper()}")
    print(f"  Type       : {args.type.upper()}")
    print(f"  Quantity   : {args.qty}")
    if args.price is not None:
        label = "Stop Price" if args.type.upper() == "STOP_MARKET" else "Price"
        print(f"  {label:10s} : {args.price}")
    print("──────────────────────────────────────────\n")

    logger.info(
        f"CLI order request | symbol={args.symbol} side={args.side} "
        f"type={args.type} qty={args.qty} price={args.price}"
    )

    api_key, api_secret = _get_credentials()
    client = BinanceClient(api_key=api_key, api_secret=api_secret)

    try:
        response = place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.qty,
            price=args.price,
        )
        print(format_response(response))
        print("\n✅  Order submitted successfully.\n")
        logger.info("Order submitted successfully.")

    except ValidationError as exc:
        print(f"\n❌  Validation error: {exc}\n")
        logger.warning(f"Validation error: {exc}")
        sys.exit(2)

    except BinanceClientError as exc:
        print(f"\n❌  API error: {exc}\n")
        logger.error(f"API error: {exc}")
        sys.exit(3)


# ── Arg parser ────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet — simple trading bot",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # place
    p = sub.add_parser("place", help="Place a new order")
    p.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    p.add_argument("--side",   required=True, choices=["BUY", "SELL", "buy", "sell"], help="BUY or SELL")
    p.add_argument("--type",   required=True, choices=["MARKET", "LIMIT", "STOP_MARKET",
                                                        "market", "limit", "stop_market"],
                   dest="type", help="MARKET | LIMIT | STOP_MARKET")
    p.add_argument("--qty",    required=True, type=float, help="Order quantity")
    p.add_argument("--price",  type=float, default=None,
                   help="Limit price (LIMIT) or stop price (STOP_MARKET)")
    p.set_defaults(func=cmd_place)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
