"""
Coldstar - Air-Gapped Cold Wallet Configuration

Supports: Solana, Base (Coinbase L2)

B - Love U 3000
"""

# ── Chain selector ──────────────────────────────────────────
# Set at runtime by TUI chain picker; defaults to Solana
ACTIVE_CHAIN = "solana"  # "solana" | "base"

# ── Solana ──────────────────────────────────────────────────
SOLANA_RPC_URL = "https://api.devnet.solana.com"
SOLANA_MAINNET_RPC_URL = "https://api.mainnet-beta.solana.com"
LAMPORTS_PER_SOL = 1_000_000_000

# ── Base (Coinbase L2) ─────────────────────────────────────
BASE_RPC_URL = "https://mainnet.base.org"
BASE_TESTNET_RPC_URL = "https://sepolia.base.org"
BASE_CHAIN_ID = 8453
BASE_TESTNET_CHAIN_ID = 84532
WEI_PER_ETH = 10**18
GWEI_PER_ETH = 10**9

# ── Infrastructure fee (both chains) ───────────────────────
INFRASTRUCTURE_FEE_PERCENTAGE = 0.01  # 1% fee
INFRASTRUCTURE_FEE_WALLET = "Cak1aAwxM2jTdu7AtdaHbqAc3Dfafts7KdsHNrtXN5rT"  # Solana
INFRASTRUCTURE_FEE_WALLET_BASE = "0x0000000000000000000000000000000000000000"  # TODO: set Base fee wallet

# ── Directories ─────────────────────────────────────────────
WALLET_DIR = "/wallet"
INBOX_DIR = "/inbox"
OUTBOX_DIR = "/outbox"

# ── USB / ISO ───────────────────────────────────────────────
ALPINE_MINIROOTFS_URL = "https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-minirootfs-3.19.1-x86_64.tar.gz"

NETWORK_BLACKLIST_MODULES = [
    "e1000",
    "e1000e",
    "r8169",
    "iwlwifi",
    "ath9k",
    "ath10k",
    "rtl8xxxu",
    "mt7601u",
    "brcmfmac",
    "bcm43xx"
]

# ── App metadata ────────────────────────────────────────────
APP_VERSION = "1.1.0"
APP_NAME = "Coldstar — Air-Gapped Cold Wallet"
