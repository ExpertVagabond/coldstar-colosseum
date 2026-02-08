"""
FairScale FairScore Integration
Wallet reputation scoring and transaction gating via on-chain reputation tiers

Real API: GET https://api2.fairscale.xyz/score?wallet=<address>
Auth: fairkey header
Response: { wallet, fairscore (0-100), tier (string), badges[], features{} }

B - Love U 3000
"""

import os
import time
import httpx
from typing import Optional, Dict, Any, Tuple

from rich.panel import Panel
from rich.table import Table

from src.ui import print_success, print_error, print_info, print_warning, console


# FairScale API Configuration
FAIRSCORE_API_BASE = os.environ.get("FAIRSCORE_API_URL", "https://api2.fairscale.xyz")
FAIRSCORE_API_KEY = os.environ.get("FAIRSCORE_API_KEY", "")

# Map FairScale string tiers to our numeric tier system (1-5)
TIER_MAP = {
    "bronze": 1,
    "silver": 2,
    "gold": 3,
    "platinum": 4,
    "diamond": 5,
}

# Score-based fallback tier mapping (if string tier is missing)
def score_to_tier(score: float) -> int:
    """Convert fairscore (0-100) to tier (1-5)."""
    if score < 20:
        return 1
    elif score < 40:
        return 2
    elif score < 60:
        return 3
    elif score < 80:
        return 4
    else:
        return 5

# Tier definitions for display and gating
TIER_DEFINITIONS = {
    1: {
        "label": "UNTRUSTED",
        "api_tier": "bronze",
        "color": "red",
        "icon": "!!!",
        "action": "BLOCK",
        "description": "High-risk wallet - likely sybil or malicious",
    },
    2: {
        "label": "LOW TRUST",
        "api_tier": "silver",
        "color": "yellow",
        "icon": "(!)",
        "action": "WARN",
        "description": "New or unverified wallet - proceed with caution",
    },
    3: {
        "label": "TRUSTED",
        "api_tier": "gold",
        "color": "green",
        "icon": "[+]",
        "action": "ALLOW",
        "description": "Verified wallet with on-chain reputation",
    },
    4: {
        "label": "HIGH TRUST",
        "api_tier": "platinum",
        "color": "cyan",
        "icon": "[++]",
        "action": "ALLOW",
        "description": "Established wallet with strong reputation",
    },
    5: {
        "label": "EXCELLENT",
        "api_tier": "diamond",
        "color": "magenta",
        "icon": "[***]",
        "action": "ALLOW",
        "description": "Top-tier reputation - verified entity",
    },
}

# Dynamic transaction limits by tier (SOL)
TIER_LIMITS = {
    1: 0,          # Blocked
    2: 10,         # 10 SOL max
    3: 100,        # 100 SOL max
    4: 500,        # 500 SOL max
    5: float("inf"),  # Unlimited
}


class FairScoreClient:
    """Client for FairScale reputation scoring API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or FAIRSCORE_API_KEY
        self.client = httpx.Client(timeout=15.0)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutes - reputation changes slowly

    def _query_api(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Raw API call to FairScale /score endpoint."""
        headers = {}
        if self.api_key:
            headers["fairkey"] = self.api_key

        response = self.client.get(
            f"{FAIRSCORE_API_BASE}/score",
            params={"wallet": wallet_address},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def get_tier(self, wallet_address: str, use_cache: bool = True) -> Optional[int]:
        """
        Get FairScore tier for a wallet address.

        Returns:
            Tier (1-5) or None on error
        """
        try:
            # Check cache
            if use_cache and wallet_address in self.cache:
                cached = self.cache[wallet_address]
                if time.time() - cached["timestamp"] < self.cache_ttl:
                    return cached["tier"]

            data = self._query_api(wallet_address)
            if data is None:
                return None

            # Extract tier from API response
            api_tier_str = data.get("tier", "")
            fairscore = data.get("fairscore", 0)

            # Map string tier to numeric, fall back to score-based
            tier = TIER_MAP.get(api_tier_str.lower(), score_to_tier(fairscore))

            self.cache[wallet_address] = {
                "tier": tier,
                "fairscore": fairscore,
                "api_tier": api_tier_str,
                "badges": data.get("badges", []),
                "timestamp": time.time(),
                "raw": data,
            }
            return tier

        except httpx.HTTPError as e:
            print_warning(f"FairScore API unavailable: {e}")
            return None
        except Exception as e:
            print_warning(f"FairScore check failed: {e}")
            return None

    def get_risk_assessment(self, wallet_address: str) -> Dict[str, Any]:
        """
        Get full risk assessment for a wallet.

        Returns:
            Dict with tier, label, color, icon, action, description, fairscore, badges, available
        """
        tier = self.get_tier(wallet_address)

        if tier is None:
            return {
                "tier": None,
                "fairscore": None,
                "label": "UNKNOWN",
                "color": "dim",
                "icon": "(?)",
                "action": "WARN",
                "description": "Reputation check unavailable - proceed with caution",
                "badges": [],
                "available": False,
            }

        cached = self.cache.get(wallet_address, {})
        info = TIER_DEFINITIONS.get(tier, TIER_DEFINITIONS[2])
        return {
            "tier": tier,
            "fairscore": cached.get("fairscore", 0),
            "api_tier": cached.get("api_tier", ""),
            "label": info["label"],
            "color": info["color"],
            "icon": info["icon"],
            "action": info["action"],
            "description": info["description"],
            "badges": cached.get("badges", []),
            "available": True,
        }

    def should_block_transaction(self, wallet_address: str) -> Tuple[bool, str]:
        """
        Check if a transaction to this wallet should be blocked.

        Returns:
            (should_block, reason)
        """
        assessment = self.get_risk_assessment(wallet_address)

        if assessment["action"] == "BLOCK":
            return (
                True,
                f"Recipient has {assessment['label']} reputation "
                f"(FairScore: {assessment['fairscore']:.1f}, Tier: {assessment.get('api_tier', 'bronze')}) "
                f"- transaction blocked",
            )

        return (False, "")

    def get_transfer_limit(self, wallet_address: str) -> float:
        """
        Get maximum transfer limit for a recipient based on reputation.

        Returns:
            Maximum SOL amount (float('inf') for unlimited)
        """
        tier = self.get_tier(wallet_address)
        if tier is None:
            return 10  # Conservative default when API unavailable
        return TIER_LIMITS.get(tier, 10)

    def display_reputation_badge(self, wallet_address: str, verbose: bool = False):
        """Display reputation badge for a wallet using Rich."""
        assessment = self.get_risk_assessment(wallet_address)
        color = assessment["color"]
        icon = assessment["icon"]
        label = assessment["label"]

        if verbose:
            table = Table.grid(padding=(0, 1))
            table.add_column(style="dim", width=14)
            table.add_column(style="white")

            table.add_row(
                "Address:",
                f"[cyan]{wallet_address[:12]}...{wallet_address[-8:]}[/cyan]",
            )
            table.add_row("Reputation:", f"[{color}]{icon} {label}[/{color}]")

            if assessment["tier"] is not None:
                table.add_row("Tier:", f"[white]{assessment.get('api_tier', '').title()} ({assessment['tier']}/5)[/white]")
                table.add_row("FairScore:", f"[white]{assessment.get('fairscore', 0):.1f}/100[/white]")
                limit = TIER_LIMITS.get(assessment["tier"], 0)
                if limit == float("inf"):
                    table.add_row("TX Limit:", "[green]Unlimited[/green]")
                elif limit == 0:
                    table.add_row("TX Limit:", "[red]BLOCKED[/red]")
                else:
                    table.add_row("TX Limit:", f"[yellow]{limit} SOL max[/yellow]")

            # Show badges if present
            badges = assessment.get("badges", [])
            if badges:
                badge_str = " ".join(f"[cyan]{b['label']}[/cyan]" for b in badges[:3])
                table.add_row("Badges:", badge_str)

            table.add_row(
                "Status:",
                f"[{color}]{assessment['description']}[/{color}]",
            )

            panel = Panel(
                table,
                title="[bold cyan]FairScore Reputation[/bold cyan]",
                border_style=color,
                padding=(1, 2),
            )
            console.print(panel)
        else:
            score_str = ""
            if assessment.get("fairscore") is not None:
                score_str = f" ({assessment['fairscore']:.0f}/100)"
            console.print(f"  Reputation: [{color}]{icon} {label}{score_str}[/{color}]")

    def display_tier_legend(self):
        """Display legend explaining all FairScore tiers."""
        table = Table(
            title="FairScore Reputation Tiers",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Tier", style="white", width=6)
        table.add_column("API Tier", style="bold", width=10)
        table.add_column("Label", style="bold", width=14)
        table.add_column("Score", width=10)
        table.add_column("Action", width=8)
        table.add_column("TX Limit", width=12)
        table.add_column("Description", style="dim")

        score_ranges = {1: "0-19", 2: "20-39", 3: "40-59", 4: "60-79", 5: "80-100"}

        for tier in sorted(TIER_DEFINITIONS.keys()):
            info = TIER_DEFINITIONS[tier]
            limit = TIER_LIMITS.get(tier, 0)
            limit_str = "Unlimited" if limit == float("inf") else f"{limit} SOL" if limit > 0 else "BLOCKED"

            table.add_row(
                str(tier),
                f"[{info['color']}]{info['api_tier']}[/{info['color']}]",
                f"[{info['color']}]{info['label']}[/{info['color']}]",
                score_ranges[tier],
                f"[{info['color']}]{info['action']}[/{info['color']}]",
                limit_str,
                info["description"],
            )

        console.print()
        console.print(table)
        console.print()

    def close(self):
        """Cleanup HTTP client."""
        try:
            self.client.close()
        except Exception:
            pass


def format_reputation_badge(tier: Optional[int]) -> str:
    """Format a compact reputation badge for inline display."""
    if tier is None:
        return "[dim](?) UNKNOWN[/dim]"

    info = TIER_DEFINITIONS.get(tier, TIER_DEFINITIONS[2])
    return f"[{info['color']}]{info['icon']} {info['label']}[/{info['color']}]"
