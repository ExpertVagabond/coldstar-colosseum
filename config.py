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

# DEPRECATED: Blacklist approach is incomplete — unknown drivers bypass it.
# Kept for reference only. Use NETWORK_WHITELIST_MODULES instead.
NETWORK_BLACKLIST_MODULES = [
    "e1000", "e1000e", "r8169", "iwlwifi", "ath9k", "ath10k",
    "rtl8xxxu", "mt7601u", "brcmfmac", "bcm43xx",
]

# WHITELIST: Only these kernel modules are allowed to load in air-gapped mode.
# Everything else (including ALL network drivers) is blocked by default.
# This is the Apple Secure Enclave approach: deny-by-default, allow only what's needed.
NETWORK_WHITELIST_MODULES = [
    # Storage (USB mass storage for transaction shuttle)
    "usb_storage",
    "uas",
    "sd_mod",
    "sg",
    # Filesystem (for reading USB transaction files)
    "vfat",
    "fat",
    "nls_cp437",
    "nls_utf8",
    "ext4",
    # HID (keyboard/mouse for TUI interaction)
    "usbhid",
    "hid",
    "hid_generic",
    # Core (required for boot)
    "loop",
    "overlay",
    "squashfs",
]

# ── App metadata ────────────────────────────────────────────
APP_VERSION = "1.1.0"
APP_NAME = "Coldstar — Air-Gapped Cold Wallet"
