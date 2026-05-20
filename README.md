# Trading Bot — Binance Futures Testnet

A minimal, well-structured Python CLI bot that places **MARKET**, **LIMIT**, and **STOP_MARKET** orders on the [Binance Futures Testnet (USDT-M)](https://testnet.binancefuture.com).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (signing, requests, error handling)
│   ├── orders.py          # Order placement logic + response formatting
│   ├── validators.py      # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py  # Structured logging to file + console
├── logs/
│   ├── market_order_sample.log
│   └── limit_order_sample.log
├── cli.py                 # CLI entry point (argparse)
├── requirements.txt
└── README.md
```

---

## Setup

### 1 — Get Testnet API credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Click **"Get Started"** → log in / register
3. Go to **API Management** and create an API key pair
4. Copy your **API Key** and **Secret Key**

### 2 — Install dependencies

```bash
cd trading_bot
pip install -r requirements.txt
```

### 3 — Set your credentials as environment variables

**macOS / Linux:**
```bash
export BINANCE_API_KEY=your_api_key_here
export BINANCE_API_SECRET=your_api_secret_here
```

**Windows (Command Prompt):**
```cmd
set BINANCE_API_KEY=your_api_key_here
set BINANCE_API_SECRET=your_api_secret_here
```

**Windows (PowerShell):**
```powershell
$env:BINANCE_API_KEY="your_api_key_here"
$env:BINANCE_API_SECRET="your_api_secret_here"
```

---

## How to Run

All commands are run from inside the `trading_bot/` directory.

### Place a MARKET order

```bash
# Buy 0.01 BTC at market price
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --qty 0.01

# Sell 0.05 ETH at market price
python cli.py place --symbol ETHUSDT --side SELL --type MARKET --qty 0.05
```

### Place a LIMIT order

```bash
# Sell 0.01 BTC at $99,000
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --qty 0.01 --price 99000

# Buy 1 ETH at $3,200
python cli.py place --symbol ETHUSDT --side BUY --type LIMIT --qty 1 --price 3200
```

### Place a STOP_MARKET order (bonus order type)

```bash
# Stop-loss: sell 0.01 BTC if price drops to $60,000
python cli.py place --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.01 --price 60000
```

### Help

```bash
python cli.py --help
python cli.py place --help
```

---

## Sample Output

```
──────────────────────────────────────────
  ORDER REQUEST SUMMARY
──────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01
──────────────────────────────────────────

┌─────────────────────────────────────────┐
│           ORDER PLACED SUCCESSFULLY      │
└─────────────────────────────────────────┘
  Order ID    : 4751823049
  Symbol      : BTCUSDT
  Side        : BUY
  Type        : MARKET
  Status      : FILLED
  Quantity    : 0.01
  Executed    : 0.01
  Avg Price   : 97423.50000
  Time        : 1752311733124

✅  Order submitted successfully.
```

---

## Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log` automatically.

- **Console**: INFO level and above
- **Log file**: DEBUG level (full request/response detail)

Sample log files for a market and a limit order are included in `logs/`.

---

## Error Handling

| Error type | Behaviour |
|---|---|
| Missing/empty symbol | Validation error with message, exit code 2 |
| Invalid side/type | Validation error with message, exit code 2 |
| Non-positive qty/price | Validation error with message, exit code 2 |
| LIMIT order without price | Validation error with message, exit code 2 |
| Missing API credentials | Clear instructions printed, exit code 1 |
| Binance API error (4xx) | Error code + message printed, exit code 3 |
| Network timeout/failure | Human-readable message printed, exit code 3 |

---

## Assumptions

- Targets **USDT-M Futures Testnet** only (`https://testnet.binancefuture.com`)
- Uses `positionSide=BOTH` (one-way mode, the testnet default)
- `timeInForce` defaults to `GTC` for LIMIT orders
- No external library required beyond `requests` — standard REST calls with HMAC-SHA256 signing
- Credentials are passed via environment variables (never hard-coded)
