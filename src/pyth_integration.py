"""
Pyth Network Price Feed Integration
Real-time price data for vault dashboard and portfolio valuation

B - Love U 3000
"""

import httpx
from typing import Optional, Dict, List, Any
from decimal import Decimal

from src.ui import print_success, print_error, print_info, print_warning


# Pyth Hermes API endpoint
PYTH_HERMES_API = "https://hermes.pyth.network"

# Common Pyth price feed IDs (mainnet)
PYTH_PRICE_FEEDS = {
    "SOL/USD": "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    "BTC/USD": "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    "ETH/USD": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
    "USDC/USD": "0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a",
    "USDT/USD": "0x2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca9ce04b0fd7f2e971688e2e53b",
    "BONK/USD": "0x72b021217ca3fe68922a19aaf990109cb9d84e9ad004b4d2025ad6f529314419",
    "JUP/USD": "0x0a0408d619e9380abad35060f9192039ed5042fa6f82301d0e48bb52be830996",
    "RAY/USD": "0x91568baa8beb53db23eb3fb7f22c6e8b1a9f0e489b46d6a12411b49e8b60cd1e",
    "ORCA/USD": "0x4b8b9e2c5e4c2e9e7a7c1c8e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a",
}

# Supported tokens for price lookup
SUPPORTED_TOKENS = list(PYTH_PRICE_FEEDS.keys())


class PythPriceClient:
    """Client for fetching real-time price data from Pyth Network"""

    def __init__(self):
        self.client = httpx.Client(timeout=10.0)
        self.cache = {}  # Simple price cache
        self.cache_ttl = 5  # Cache for 5 seconds

    def get_price(
        self,
        symbol: str,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get current price for a token

        Args:
            symbol: Token symbol (e.g., "SOL/USD")
            use_cache: Use cached price if available

        Returns:
            Price data dictionary or None on error
        """
        try:
            # Normalize symbol
            symbol_upper = symbol.upper()
            if not symbol_upper.endswith("/USD"):
                symbol_upper = f"{symbol_upper}/USD"

            # Check if symbol is supported
            if symbol_upper not in PYTH_PRICE_FEEDS:
                print_warning(f"Price feed not available for {symbol}")
                return None

            # Check cache
            if use_cache and symbol_upper in self.cache:
                cached_data = self.cache[symbol_upper]
                import time
                if time.time() - cached_data["timestamp"] < self.cache_ttl:
                    return cached_data["data"]

            # Get price feed ID
            feed_id = PYTH_PRICE_FEEDS[symbol_upper]

            # Fetch latest price
            response = self.client.get(
                f"{PYTH_HERMES_API}/api/latest_price_feeds",
                params={"ids[]": feed_id}
            )
            response.raise_for_status()

            data = response.json()

            if not data or len(data) == 0:
                print_error(f"No price data returned for {symbol}")
                return None

            price_feed = data[0]
            price_data = price_feed.get("price", {})

            # Parse price data
            price_raw = int(price_data.get("price", 0))
            expo = int(price_data.get("expo", 0))
            conf = int(price_data.get("conf", 0))

            # Calculate actual price
            price = price_raw * (10 ** expo)
            confidence = conf * (10 ** expo)

            result = {
                "symbol": symbol_upper,
                "price": price,
                "confidence": confidence,
                "expo": expo,
                "publish_time": price_data.get("publish_time", 0),
                "raw": price_feed
            }

            # Update cache
            import time
            self.cache[symbol_upper] = {
                "data": result,
                "timestamp": time.time()
            }

            return result

        except httpx.HTTPError as e:
            print_error(f"HTTP error fetching price for {symbol}: {e}")
            return None
        except Exception as e:
            print_error(f"Failed to get price for {symbol}: {e}")
            return None

    def get_multiple_prices(
        self,
        symbols: List[str]
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Get prices for multiple tokens

        Args:
            symbols: List of token symbols

        Returns:
            Dictionary mapping symbols to price data
        """
        try:
            # Normalize symbols and get feed IDs
            feed_ids = []
            symbol_map = {}

            for symbol in symbols:
                symbol_upper = symbol.upper()
                if not symbol_upper.endswith("/USD"):
                    symbol_upper = f"{symbol_upper}/USD"

                if symbol_upper in PYTH_PRICE_FEEDS:
                    feed_id = PYTH_PRICE_FEEDS[symbol_upper]
                    feed_ids.append(feed_id)
                    symbol_map[feed_id] = symbol_upper

            if not feed_ids:
                return {}

            # Build request with multiple IDs
            params = [("ids[]", fid) for fid in feed_ids]

            # Fetch all prices at once
            response = self.client.get(
                f"{PYTH_HERMES_API}/api/latest_price_feeds",
                params=params
            )
            response.raise_for_status()

            data = response.json()

            # Parse results
            results = {}
            for price_feed in data:
                feed_id = price_feed.get("id")
                if feed_id not in symbol_map:
                    continue

                symbol = symbol_map[feed_id]
                price_data = price_feed.get("price", {})

                price_raw = int(price_data.get("price", 0))
                expo = int(price_data.get("expo", 0))
                conf = int(price_data.get("conf", 0))

                price = price_raw * (10 ** expo)
                confidence = conf * (10 ** expo)

                results[symbol] = {
                    "symbol": symbol,
                    "price": price,
                    "confidence": confidence,
                    "expo": expo,
                    "publish_time": price_data.get("publish_time", 0),
                    "raw": price_feed
                }

            return results

        except Exception as e:
            print_error(f"Failed to get multiple prices: {e}")
            return {}

    def get_portfolio_value(
        self,
        holdings: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate total portfolio value in USD

        Args:
            holdings: Dictionary mapping token symbols to amounts
                     e.g., {"SOL": 10.5, "USDC": 1000}

        Returns:
            Portfolio valuation data or None on error
        """
        try:
            # Get all prices
            symbols = list(holdings.keys())
            prices = self.get_multiple_prices(symbols)

            # Calculate total value
            total_usd = 0.0
            breakdown = {}

            for symbol, amount in holdings.items():
                symbol_key = symbol.upper()
                if not symbol_key.endswith("/USD"):
                    symbol_key = f"{symbol_key}/USD"

                if symbol_key in prices:
                    price_data = prices[symbol_key]
                    token_value = amount * price_data["price"]
                    total_usd += token_value

                    breakdown[symbol] = {
                        "amount": amount,
                        "price": price_data["price"],
                        "value_usd": token_value,
                        "percentage": 0  # Will calculate after total
                    }
                else:
                    print_warning(f"No price data for {symbol}")

            # Calculate percentages
            for symbol in breakdown:
                if total_usd > 0:
                    breakdown[symbol]["percentage"] = (
                        breakdown[symbol]["value_usd"] / total_usd * 100
                    )

            return {
                "total_usd": total_usd,
                "breakdown": breakdown,
                "timestamp": int(__import__("time").time())
            }

        except Exception as e:
            print_error(f"Failed to calculate portfolio value: {e}")
            return None

    def format_price_display(
        self,
        symbol: str,
        price_data: Dict[str, Any],
        show_confidence: bool = False
    ) -> str:
        """Format price data for display"""
        price = price_data["price"]

        # Format based on price magnitude
        if price >= 1000:
            price_str = f"${price:,.2f}"
        elif price >= 1:
            price_str = f"${price:.4f}"
        else:
            price_str = f"${price:.8f}"

        result = f"{symbol}: {price_str}"

        if show_confidence:
            conf_pct = (price_data["confidence"] / price * 100) if price > 0 else 0
            result += f" (±{conf_pct:.2f}%)"

        return result

    def __del__(self):
        """Cleanup HTTP client"""
        try:
            self.client.close()
        except:
            pass


def format_usd(amount: float) -> str:
    """Format USD amount for display"""
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.2f}K"
    else:
        return f"${amount:.2f}"
