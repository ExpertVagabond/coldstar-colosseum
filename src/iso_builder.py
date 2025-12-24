"""
ISO Builder - Create bootable Alpine Linux USB with Solana signing tools
"""

import subprocess
import os
import shutil
import tempfile
import json
from pathlib import Path
from typing import Optional, Tuple

from solders.keypair import Keypair

from src.ui import (
    print_success, print_error, print_info, print_warning,
    print_step, create_progress_bar, confirm_dangerous_action,
    print_wallet_info
)
from config import ALPINE_MINIROOTFS_URL, NETWORK_BLACKLIST_MODULES


class ISOBuilder:
    def __init__(self):
        self.work_dir: Optional[Path] = None
        self.rootfs_dir: Optional[Path] = None
        self.iso_path: Optional[Path] = None
        self.generated_pubkey: Optional[str] = None
    
    def download_alpine_rootfs(self, work_dir: str) -> Optional[Path]:
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        tarball_path = self.work_dir / "alpine-minirootfs.tar.gz"
        
        print_step(1, 6, "Downloading Alpine Linux minirootfs...")
        
        try:
            result = subprocess.run(
                ['wget', '-q', '--show-progress', '-O', str(tarball_path), ALPINE_MINIROOTFS_URL],
                capture_output=False,
                timeout=300
            )
            
            if result.returncode != 0:
                result = subprocess.run(
                    ['curl', '-L', '-o', str(tarball_path), ALPINE_MINIROOTFS_URL],
                    capture_output=True,
                    timeout=300
                )
            
            if tarball_path.exists():
                print_success("Alpine Linux rootfs downloaded")
                return tarball_path
            else:
                print_error("Failed to download Alpine rootfs")
                return None
                
        except subprocess.TimeoutExpired:
            print_error("Download timed out")
            return None
        except FileNotFoundError:
            print_error("wget/curl not found. Please install wget or curl.")
            return None
        except Exception as e:
            print_error(f"Download error: {e}")
            return None
    
    def extract_rootfs(self, tarball_path: Path) -> Optional[Path]:
        print_step(2, 6, "Extracting filesystem...")
        
        self.rootfs_dir = self.work_dir / "rootfs"
        self.rootfs_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            result = subprocess.run(
                ['tar', '-xzf', str(tarball_path), '-C', str(self.rootfs_dir)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print_success("Filesystem extracted")
                return self.rootfs_dir
            else:
                print_error(f"Extraction failed: {result.stderr}")
                return None
                
        except Exception as e:
            print_error(f"Extraction error: {e}")
            return None
    
    def configure_offline_os(self) -> bool:
        if not self.rootfs_dir:
            print_error("No rootfs directory set")
            return False
        
        print_step(3, 6, "Configuring offline OS...")
        
        try:
            wallet_dir = self.rootfs_dir / "wallet"
            inbox_dir = self.rootfs_dir / "inbox"
            outbox_dir = self.rootfs_dir / "outbox"
            
            for d in [wallet_dir, inbox_dir, outbox_dir]:
                d.mkdir(parents=True, exist_ok=True)
            
            modprobe_dir = self.rootfs_dir / "etc" / "modprobe.d"
            modprobe_dir.mkdir(parents=True, exist_ok=True)
            blacklist_conf = modprobe_dir / "blacklist-network.conf"
            
            with open(blacklist_conf, 'w') as f:
                f.write("# Network modules blacklisted for offline cold wallet\n")
                f.write("# Ethernet drivers\n")
                for module in NETWORK_BLACKLIST_MODULES:
                    f.write(f"blacklist {module}\n")
                f.write("# Additional wireless drivers\n")
                f.write("blacklist cfg80211\n")
                f.write("blacklist mac80211\n")
                f.write("blacklist rfkill\n")
                f.write("blacklist bluetooth\n")
                f.write("blacklist btusb\n")
                f.write("# USB network adapters\n")
                f.write("blacklist usbnet\n")
                f.write("blacklist cdc_ether\n")
                f.write("blacklist rndis_host\n")
                f.write("blacklist ax88179_178a\n")
            
            print_success("Network drivers blacklisted")
            
            self._disable_network_services()
            self._create_network_lockdown_script()
            self._create_signing_script()
            self._create_boot_profile()
            self._generate_embedded_keypair()
            
            print_success("Offline OS configured")
            return True
            
        except Exception as e:
            print_error(f"Configuration error: {e}")
            return False
    
    def _disable_network_services(self):
        init_dir = self.rootfs_dir / "etc" / "init.d"
        init_dir.mkdir(parents=True, exist_ok=True)
        
        rclocal = self.rootfs_dir / "etc" / "local.d" / "disable-network.start"
        rclocal.parent.mkdir(parents=True, exist_ok=True)
        
        network_lockdown = '''#!/bin/sh
# Ensure no network interfaces come up
for iface in $(ls /sys/class/net/ 2>/dev/null | grep -v lo); do
    ip link set "$iface" down 2>/dev/null
done

# Drop all network traffic via iptables if available
if command -v iptables >/dev/null 2>&1; then
    iptables -P INPUT DROP 2>/dev/null
    iptables -P OUTPUT DROP 2>/dev/null
    iptables -P FORWARD DROP 2>/dev/null
fi

# Kill any networking daemons that might have started
for proc in dhcpcd udhcpc wpa_supplicant NetworkManager; do
    pkill -9 "$proc" 2>/dev/null
done
'''
        
        with open(rclocal, 'w') as f:
            f.write(network_lockdown)
        os.chmod(rclocal, 0o755)
        
        interfaces_file = self.rootfs_dir / "etc" / "network" / "interfaces"
        interfaces_file.parent.mkdir(parents=True, exist_ok=True)
        with open(interfaces_file, 'w') as f:
            f.write("# Network interfaces disabled for cold wallet security\n")
            f.write("auto lo\n")
            f.write("iface lo inet loopback\n")
        
        print_success("Network services disabled")
    
    def _create_network_lockdown_script(self):
        script_path = self.rootfs_dir / "usr" / "local" / "bin" / "verify_offline.sh"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        script_content = '''#!/bin/sh
# Verify system is truly offline

echo "NETWORK STATUS CHECK"
echo "===================="

ONLINE=0

for iface in $(ls /sys/class/net/ 2>/dev/null); do
    if [ "$iface" != "lo" ]; then
        state=$(cat /sys/class/net/$iface/operstate 2>/dev/null)
        if [ "$state" = "up" ]; then
            echo "WARNING: Interface $iface is UP!"
            ONLINE=1
        fi
    fi
done

if command -v ping >/dev/null 2>&1; then
    if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
        echo "WARNING: Network connectivity detected!"
        ONLINE=1
    fi
fi

if [ $ONLINE -eq 0 ]; then
    echo "VERIFIED: System is OFFLINE"
    echo "Safe for transaction signing."
else
    echo ""
    echo "WARNING: NETWORK ACCESS DETECTED!"
    echo "Do NOT sign transactions on this system!"
fi
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
    
    def _create_signing_script(self):
        script_dir = self.rootfs_dir / "usr" / "local" / "bin"
        script_dir.mkdir(parents=True, exist_ok=True)
        
        sign_script = script_dir / "sign_tx.sh"
        
        script_content = '''#!/bin/sh
# Solana Offline Transaction Signing Script

WALLET_DIR="/wallet"
INBOX_DIR="/inbox"
OUTBOX_DIR="/outbox"
KEYPAIR_FILE="$WALLET_DIR/keypair.json"
PUBKEY_FILE="$WALLET_DIR/pubkey.txt"

echo "=============================================="
echo "    SOLANA OFFLINE TRANSACTION SIGNER"
echo "=============================================="
echo ""

if [ ! -f "$KEYPAIR_FILE" ]; then
    echo "ERROR: No wallet found at $KEYPAIR_FILE"
    echo "Please initialize wallet first."
    exit 1
fi

if [ -f "$PUBKEY_FILE" ]; then
    echo "Wallet Public Key:"
    cat "$PUBKEY_FILE"
    echo ""
fi

UNSIGNED_TX=$(find "$INBOX_DIR" -name "*.json" -type f | head -1)

if [ -z "$UNSIGNED_TX" ]; then
    echo "No unsigned transaction found in $INBOX_DIR"
    echo ""
    echo "Instructions:"
    echo "1. Copy unsigned transaction file to $INBOX_DIR"
    echo "2. Run this script again"
    exit 0
fi

echo "Found unsigned transaction: $UNSIGNED_TX"
echo ""
echo "WARNING: You are about to sign this transaction."
echo "Review the transaction details carefully."
echo ""
read -p "Type 'SIGN' to confirm: " confirm

if [ "$confirm" != "SIGN" ]; then
    echo "Signing cancelled."
    exit 0
fi

BASENAME=$(basename "$UNSIGNED_TX" .json)
SIGNED_TX="$OUTBOX_DIR/${BASENAME}_signed.json"

python3 /usr/local/bin/offline_sign.py "$UNSIGNED_TX" "$KEYPAIR_FILE" "$SIGNED_TX"

if [ $? -eq 0 ]; then
    echo ""
    echo "SUCCESS: Transaction signed!"
    echo "Signed transaction saved to: $SIGNED_TX"
    echo ""
    echo "Next steps:"
    echo "1. Copy $SIGNED_TX to your online host"
    echo "2. Broadcast the transaction"
else
    echo "ERROR: Signing failed"
    exit 1
fi
'''
        
        with open(sign_script, 'w') as f:
            f.write(script_content)
        
        os.chmod(sign_script, 0o755)
        
        python_sign_script = script_dir / "offline_sign.py"
        
        python_content = '''#!/usr/bin/env python3
"""Offline transaction signing script for cold wallet"""

import sys
import json
import base64

def main():
    if len(sys.argv) != 4:
        print("Usage: offline_sign.py <unsigned_tx> <keypair> <output>")
        sys.exit(1)
    
    unsigned_path = sys.argv[1]
    keypair_path = sys.argv[2]
    output_path = sys.argv[3]
    
    try:
        from solders.keypair import Keypair
        from solders.transaction import Transaction
        
        with open(keypair_path, 'r') as f:
            secret_list = json.load(f)
        keypair = Keypair.from_bytes(bytes(secret_list))
        
        with open(unsigned_path, 'r') as f:
            tx_data = json.load(f)
        
        tx_bytes = base64.b64decode(tx_data['data'])
        tx = Transaction.from_bytes(tx_bytes)
        
        tx.sign([keypair], tx.message.recent_blockhash)
        
        signed_data = {
            "type": "signed_transaction",
            "version": "1.0",
            "data": base64.b64encode(bytes(tx)).decode('utf-8')
        }
        
        with open(output_path, 'w') as f:
            json.dump(signed_data, f, indent=2)
        
        print("Transaction signed successfully")
        
    except ImportError:
        print("ERROR: solders library not installed")
        print("Install with: pip install solders")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        with open(python_sign_script, 'w') as f:
            f.write(python_content)
        
        os.chmod(python_sign_script, 0o755)
        print_success("Signing scripts created")
    
    def _create_boot_profile(self):
        profile_path = self.rootfs_dir / "etc" / "profile.d" / "wallet-welcome.sh"
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        
        profile_content = '''#!/bin/sh
# Wallet boot message

clear
echo ""
echo "=============================================="
echo "     SOLANA COLD WALLET - OFFLINE MODE"
echo "=============================================="
echo ""

if [ -f /wallet/pubkey.txt ]; then
    echo "Wallet Public Key:"
    echo "--------------------------------------------"
    cat /wallet/pubkey.txt
    echo ""
    echo "--------------------------------------------"
else
    echo "ERROR: No wallet found!"
    echo "This USB may be corrupted. Please re-flash."
fi

echo ""
echo "SECURITY: This device has NO network access."
echo ""
echo "Commands:"
echo "  sign_tx.sh    - Sign a transaction"
echo ""
echo "Directories:"
echo "  /wallet       - Wallet keypair storage"
echo "  /inbox        - Place unsigned transactions here"
echo "  /outbox       - Signed transactions appear here"
echo ""
echo "=============================================="
echo ""
'''
        
        with open(profile_path, 'w') as f:
            f.write(profile_content)
        
        os.chmod(profile_path, 0o755)
        print_success("Boot profile created")
    
    def _generate_embedded_keypair(self) -> Tuple[str, str]:
        wallet_dir = self.rootfs_dir / "wallet"
        wallet_dir.mkdir(parents=True, exist_ok=True)
        
        keypair_path = wallet_dir / "keypair.json"
        pubkey_path = wallet_dir / "pubkey.txt"
        
        keypair = Keypair()
        public_key = str(keypair.pubkey())
        
        secret_bytes = bytes(keypair)
        secret_list = list(secret_bytes)
        
        with open(keypair_path, 'w') as f:
            json.dump(secret_list, f)
        
        with open(pubkey_path, 'w') as f:
            f.write(public_key)
        
        os.chmod(keypair_path, 0o600)
        
        self.generated_pubkey = public_key
        
        print_success("Wallet keypair generated and embedded")
        print_wallet_info(public_key)
        print_warning("IMPORTANT: This public key is your wallet address!")
        print_warning("Record it now - you'll need it to receive funds.")
        
        return public_key, str(keypair_path)
    
    def get_generated_pubkey(self) -> Optional[str]:
        return self.generated_pubkey
    
    def build_iso(self, output_path: str = None) -> Optional[Path]:
        if not self.rootfs_dir:
            print_error("No rootfs configured")
            return None
        
        print_step(4, 6, "Building bootable ISO...")
        
        self.iso_path = Path(output_path) if output_path else self.work_dir / "solana-cold-wallet.iso"
        
        try:
            result = subprocess.run(['which', 'grub-mkrescue'], capture_output=True)
            if result.returncode != 0:
                result = subprocess.run(['which', 'grub2-mkrescue'], capture_output=True)
                grub_cmd = 'grub2-mkrescue' if result.returncode == 0 else None
            else:
                grub_cmd = 'grub-mkrescue'
            
            if not grub_cmd:
                print_warning("grub-mkrescue not found, creating simple bootable image")
                return self._create_simple_image()
            
            grub_dir = self.rootfs_dir / "boot" / "grub"
            grub_dir.mkdir(parents=True, exist_ok=True)
            
            grub_cfg = grub_dir / "grub.cfg"
            grub_content = '''
set timeout=5
set default=0

menuentry "Solana Cold Wallet (Offline)" {
    linux /boot/vmlinuz root=/dev/ram0 quiet
    initrd /boot/initramfs
}
'''
            with open(grub_cfg, 'w') as f:
                f.write(grub_content)
            
            result = subprocess.run(
                [grub_cmd, '-o', str(self.iso_path), str(self.rootfs_dir)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0 and self.iso_path.exists():
                print_success(f"ISO created: {self.iso_path}")
                return self.iso_path
            else:
                print_warning("ISO creation with grub failed, using simple image")
                return self._create_simple_image()
                
        except Exception as e:
            print_warning(f"ISO creation failed: {e}, using simple image")
            return self._create_simple_image()
    
    def _create_simple_image(self) -> Optional[Path]:
        print_info("Creating portable wallet filesystem...")
        
        archive_path = self.work_dir / "solana-cold-wallet.tar.gz"
        
        try:
            result = subprocess.run(
                ['tar', '-czf', str(archive_path), '-C', str(self.rootfs_dir), '.'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print_success(f"Wallet filesystem created: {archive_path}")
                self.iso_path = archive_path
                return archive_path
            else:
                print_error(f"Failed to create archive: {result.stderr}")
                return None
                
        except Exception as e:
            print_error(f"Archive creation failed: {e}")
            return None
    
    def flash_to_usb(self, device_path: str, image_path: str = None) -> bool:
        image = Path(image_path) if image_path else self.iso_path
        
        if not image or not image.exists():
            print_error("No image file to flash")
            return False
        
        print_step(5, 6, f"Flashing to {device_path}...")
        print_warning(f"This will ERASE ALL DATA on {device_path}")
        
        if not confirm_dangerous_action(
            f"All data on {device_path} will be permanently destroyed!",
            "FLASH"
        ):
            print_info("Flash operation cancelled")
            return False
        
        try:
            if str(image).endswith('.iso'):
                result = subprocess.run(
                    ['dd', f'if={image}', f'of={device_path}', 'bs=4M', 'status=progress', 'oflag=sync'],
                    capture_output=False,
                    timeout=600
                )
            else:
                print_info("Formatting USB device...")
                subprocess.run(['mkfs.ext4', '-F', device_path], capture_output=True, timeout=60)
                
                mount_point = f"/tmp/usb_flash_{os.getpid()}"
                os.makedirs(mount_point, exist_ok=True)
                
                subprocess.run(['mount', device_path, mount_point], capture_output=True, timeout=30)
                
                result = subprocess.run(
                    ['tar', '-xzf', str(image), '-C', mount_point],
                    capture_output=True,
                    timeout=300
                )
                
                subprocess.run(['umount', mount_point], capture_output=True, timeout=30)
            
            if result.returncode == 0:
                print_success("USB flash completed successfully!")
                return True
            else:
                print_error("Flash operation failed")
                return False
                
        except subprocess.TimeoutExpired:
            print_error("Flash operation timed out")
            return False
        except PermissionError:
            print_error("Permission denied. Run with sudo.")
            return False
        except Exception as e:
            print_error(f"Flash error: {e}")
            return False
    
    def cleanup(self):
        print_step(6, 6, "Cleaning up temporary files...")
        
        if self.work_dir and self.work_dir.exists():
            try:
                if self.rootfs_dir and self.rootfs_dir.exists():
                    shutil.rmtree(self.rootfs_dir, ignore_errors=True)
                
                tarball = self.work_dir / "alpine-minirootfs.tar.gz"
                if tarball.exists():
                    tarball.unlink()
                
                print_success("Cleanup completed")
            except Exception as e:
                print_warning(f"Cleanup warning: {e}")
    
    def get_iso_path(self) -> Optional[Path]:
        return self.iso_path
