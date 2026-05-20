from __future__ import annotations
import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import get_logger

logger = get_logger(__name__)

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised when the Binance API returns an error response."""


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        logger.debug(f"BinanceClient initialised — base_url={self.base_url}")

    # ── Signing ──────────────────────────────────────────────────────────────

    def _sign(self, params: Dict[str, Any]) -> str:
        query = urlencode(params)
        return hmac.new(
            self.api_secret.encode(), query.encode(), hashlib.sha256
        ).hexdigest()

    def _signed_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = 5000
        params["signature"] = self._sign(params)
        return params

    # ── HTTP helpers ─────────────────────────────────────────────────────────

    def _request(self, method: str, path: str, params: Dict[str, Any]) -> Dict:
        url = f"{self.base_url}{path}"
        logger.debug(f"→ {method.upper()} {url} | params={params}")
        try:
            resp = self.session.request(method, url, params=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error(f"Network error reaching {url}: {exc}")
            raise BinanceClientError(f"Network error: {exc}") from exc
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out: {url}")
            raise BinanceClientError("Request timed out.") from None

        logger.debug(f"← {resp.status_code} {resp.text[:500]}")

        try:
            data = resp.json()
        except ValueError:
            logger.error(f"Non-JSON response: {resp.text[:200]}")
            raise BinanceClientError(f"Non-JSON response: {resp.text[:200]}")

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            msg = data.get("msg", "Unknown API error")
            logger.error(f"API error {data['code']}: {msg}")
            raise BinanceClientError(f"API error {data['code']}: {msg}")

        return data

    def _post(self, path: str, params: Dict[str, Any]) -> Dict:
        return self._request("POST", path, self._signed_params(params))

    def _get(self, path: str, params: Dict[str, Any]) -> Dict:
        return self._request("GET", path, self._signed_params(params))

    # ── Public API ────────────────────────────────────────────────────────────

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC",
    ) -> Dict:
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force

        if order_type == "STOP_MARKET":
            params["stopPrice"] = stop_price

        logger.info(
            f"Placing {order_type} {side} order | symbol={symbol} qty={quantity}"
            + (f" price={price}" if price else "")
            + (f" stopPrice={stop_price}" if stop_price else "")
        )

        response = self._post("/fapi/v1/order", params)
        logger.info(f"Order placed successfully | orderId={response.get('orderId')} status={response.get('status')}")
        return response

    def get_order(self, symbol: str, order_id: int) -> Dict:
        params = {"symbol": symbol, "orderId": order_id}
        return self._get("/fapi/v1/order", params)

    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("DELETE", "/fapi/v1/order", self._signed_params(params))
