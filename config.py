"""
Solana Cold Wallet USB Tool - Configuration

B - Love U 3000
"""

SOLANA_RPC_URL = "https://api.devnet.solana.com"

LAMPORTS_PER_SOL = 1_000_000_000

WALLET_DIR = "/wallet"
INBOX_DIR = "/inbox"
OUTBOX_DIR = "/outbox"

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

# FairScale FairScore Configuration
FAIRSCORE_API_URL = "https://api2.fairscale.xyz"
FAIRSCORE_API_KEY = ""  # Set via env FAIRSCORE_API_KEY or here
FAIRSCORE_ENABLED = True
FAIRSCORE_MIN_TIER = 2  # Minimum tier to allow transactions without warning

APP_VERSION = "1.1.0"
APP_NAME = "Solana Cold Wallet USB Tool"
