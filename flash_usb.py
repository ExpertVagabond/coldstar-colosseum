#!/usr/bin/env python3
"""
Flash Solana Cold Wallet image to USB drive

Usage:
    sudo python3 flash_usb.py                    # Interactive mode
    sudo python3 flash_usb.py /dev/sdX           # Flash to specific device
    sudo python3 flash_usb.py --build            # Build ISO then flash
    sudo python3 flash_usb.py --build-only       # Only build ISO, don't flash

B - Love U 3000
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    class Console:
        def print(self, *args, **kwargs):
            text = str(args[0]) if args else ""
            text = text.replace("[bold]", "").replace("[/bold]", "")
            text = text.replace("[green]", "").replace("[/green]", "")
            text = text.replace("[red]", "").replace("[/red]", "")
            text = text.replace("[yellow]", "").replace("[/yellow]", "")
            text = text.replace("[cyan]", "").replace("[/cyan]", "")
            print(text)
    console = Console()


def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════╗
║         SOLANA COLD WALLET - USB FLASH TOOL               ║
╠═══════════════════════════════════════════════════════════╣
║  Flash the cold wallet image to a USB drive               ║
║  WARNING: This will erase ALL data on the target device!  ║
╚═══════════════════════════════════════════════════════════╝
"""
    console.print(banner)


def check_root():
    # On macOS, diskutil can work without root for some operations
    if platform.system() == 'Darwin':
        # Just warn but don't exit
        if os.geteuid() != 0:
            console.print("[yellow]Note: Running without root. Some operations may require sudo.[/yellow]")
        return
    
    # On Linux, require root
    if os.geteuid() != 0:
        console.print("[red]ERROR: This script must be run as root (sudo)[/red]")
        console.print("Usage: sudo python3 flash_usb.py")
        sys.exit(1)


def find_image() -> Path:
    """Find the cold wallet image file"""
    search_paths = [
        Path("./output/solana-cold-wallet.img"),
        Path("./output/solana-cold-wallet.tar.gz"),
        Path("./solana-cold-wallet.img"),
        Path("./solana-cold-wallet.tar.gz"),
    ]
    
    for path in search_paths:
        if path.exists():
            return path
    
    return None


def list_usb_devices() -> list:
    """List available USB block devices"""
    devices = []
    
    # macOS support using diskutil
    if platform.system() == 'Darwin':
        try:
            result = subprocess.run(
                ['diskutil', 'list'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                console.print("[yellow]Warning: Could not list devices with diskutil[/yellow]")
                return devices
            
            # Parse diskutil output
            lines = result.stdout.split('\n')
            current_disk = None
            
            for line in lines:
                # Look for disk identifiers
                if '/dev/disk' in line and '(external' in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith('/dev/disk'):
                            disk_name = part.rstrip(':')
                            
                            # Get detailed info
                            info_result = subprocess.run(
                                ['diskutil', 'info', disk_name],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            
                            if info_result.returncode == 0:
                                size = "Unknown"
                                model = "USB Device"
                                
                                for info_line in info_result.stdout.split('\n'):
                                    if 'Disk Size:' in info_line:
                                        # Extract size (e.g., "32.0 GB")
                                        parts = info_line.split()
                                        for i, p in enumerate(parts):
                                            if 'GB' in p or 'MB' in p:
                                                if i > 0:
                                                    size = f"{parts[i-1]} {p}"
                                                break
                                    elif 'Device / Media Name:' in info_line:
                                        model = info_line.split(':', 1)[1].strip()
                                
                                devices.append({
                                    'name': disk_name.replace('/dev/', ''),
                                    'path': disk_name,
                                    'size': size,
                                    'model': model
                                })
                            break
            
            return devices
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not list devices: {e}[/yellow]")
            return devices
    
    # Linux support using lsblk
    try:
        result = subprocess.run(
            ['lsblk', '-d', '-o', 'NAME,SIZE,TYPE,TRAN,MODEL', '-n'],
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 4:
                name, size, dtype, tran = parts[0], parts[1], parts[2], parts[3]
                model = ' '.join(parts[4:]) if len(parts) > 4 else 'Unknown'
                
                if tran == 'usb' and dtype == 'disk':
                    devices.append({
                        'name': name,
                        'path': f'/dev/{name}',
                        'size': size,
                        'model': model
                    })
    except Exception as e:
        console.print(f"[yellow]Warning: Could not list devices: {e}[/yellow]")
    
    return devices


def select_device(devices: list) -> str:
    """Let user select a USB device"""
    if not devices:
        console.print("[red]No USB devices found![/red]")
        console.print("Please insert a USB drive and try again.")
        sys.exit(1)
    
    console.print("\n[bold]Available USB Devices:[/bold]\n")
    
    if HAS_RICH:
        table = Table()
        table.add_column("#", style="cyan")
        table.add_column("Device", style="green")
        table.add_column("Size", style="yellow")
        table.add_column("Model", style="white")
        
        for i, dev in enumerate(devices, 1):
            table.add_row(str(i), dev['path'], dev['size'], dev['model'])
        
        console.print(table)
    else:
        for i, dev in enumerate(devices, 1):
            print(f"  {i}. {dev['path']} - {dev['size']} - {dev['model']}")
    
    console.print()
    
    while True:
        try:
            choice = input("Select device number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                sys.exit(0)
            
            idx = int(choice) - 1
            if 0 <= idx < len(devices):
                return devices[idx]['path']
            else:
                console.print("[red]Invalid selection[/red]")
        except ValueError:
            console.print("[red]Please enter a number[/red]")


def confirm_flash(device: str, image: Path) -> bool:
    """Confirm the flash operation"""
    console.print(f"\n[bold][red]WARNING: DESTRUCTIVE OPERATION[/red][/bold]")
    console.print(f"\nImage:  {image}")
    console.print(f"Target: {device}")
    console.print(f"\n[yellow]ALL DATA ON {device} WILL BE PERMANENTLY ERASED![/yellow]")
    console.print()
    
    confirm = input("Type 'FLASH' to confirm: ").strip()
    return confirm == 'FLASH'


def flash_image(device: str, image: Path) -> bool:
    """Flash the image to the USB device"""
    console.print(f"\n[bold]Flashing {image.name} to {device}...[/bold]")
    console.print("This may take several minutes.\n")
    
    is_macos = platform.system() == 'Darwin'
    
    try:
        # On macOS, unmount the disk first (but don't eject)
        if is_macos:
            console.print(f"Unmounting {device}...")
            subprocess.run(['diskutil', 'unmountDisk', device], timeout=30)
        
        if str(image).endswith('.img') or str(image).endswith('.iso'):
            # For macOS, use rdisk for faster writes
            target_device = device
            if is_macos and 'disk' in device:
                target_device = device.replace('/dev/disk', '/dev/rdisk')
            
            cmd = ['dd', f'if={image}', f'of={target_device}', 'bs=4m' if is_macos else 'bs=4M']
            
            # Add status on macOS if supported
            if not is_macos:
                cmd.extend(['status=progress', 'oflag=sync'])
            
            console.print(f"Writing image to {target_device}...")
            result = subprocess.run(cmd, timeout=600)
        else:
            console.print("Formatting USB as ext4...")
            subprocess.run(['mkfs.ext4', '-F', device], timeout=60)
            
            mount_point = f"/tmp/usb_flash_{os.getpid()}"
            os.makedirs(mount_point, exist_ok=True)
            
            subprocess.run(['mount', device, mount_point], timeout=30)
            
            console.print("Extracting filesystem...")
            result = subprocess.run(
                ['tar', '-xzf', str(image), '-C', mount_point],
                timeout=300
            )
            
            subprocess.run(['sync'])
            subprocess.run(['umount', mount_point], timeout=30)
            
            if result.returncode == 0:
                console.print("\n[bold][green]SUCCESS! USB cold wallet created![/green][/bold]")
                return True
            return False
        
        # Sync to ensure all data is written
        console.print("Syncing...")
        subprocess.run(['sync'])
        
        # On macOS, eject the disk
        if is_macos:
            console.print("Ejecting disk...")
            subprocess.run(['diskutil', 'eject', device], timeout=30)
        
        if result.returncode == 0:
            console.print("\n[bold][green]SUCCESS! USB cold wallet created![/green][/bold]")
            console.print("\nNext steps:")
            console.print("1. Remove the USB drive")
            console.print("2. Boot an air-gapped computer from this USB")
            console.print("3. The wallet will be generated on first boot")
            return True
        else:
            console.print("\n[red]Flash operation failed[/red]")
            return False
            
    except subprocess.TimeoutExpired:
        console.print("\n[red]Operation timed out[/red]")
        return False
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        return False


def build_iso() -> Path:
    """Build the cold wallet ISO"""
    console.print("\n[bold]Building cold wallet ISO...[/bold]\n")
    
    try:
        from src.iso_builder import ISOBuilder
        
        builder = ISOBuilder()
        image_path = builder.build_complete_iso("./output")
        
        if image_path and image_path.exists():
            return image_path
        else:
            console.print("[red]Failed to build ISO[/red]")
            sys.exit(1)
            
    except ImportError as e:
        console.print(f"[red]Import error: {e}[/red]")
        console.print("Make sure you're running from the project directory")
        sys.exit(1)


def main():
    print_banner()
    
    build_only = '--build-only' in sys.argv
    do_build = '--build' in sys.argv or build_only
    
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    
    if do_build:
        image = build_iso()
        if build_only:
            console.print(f"\n[green]Image created: {image}[/green]")
            console.print("\nTo flash to USB, run:")
            console.print(f"  sudo python3 flash_usb.py {image}")
            sys.exit(0)
    else:
        image = find_image()
        if not image:
            console.print("[yellow]No cold wallet image found.[/yellow]")
            console.print("Building new image...\n")
            image = build_iso()
    
    check_root()
    
    if args:
        device = args[0]
        if not device.startswith('/dev/'):
            console.print(f"[red]Invalid device path: {device}[/red]")
            sys.exit(1)
    else:
        devices = list_usb_devices()
        device = select_device(devices)
    
    if not confirm_flash(device, image):
        console.print("\n[yellow]Flash cancelled[/yellow]")
        sys.exit(0)
    
    success = flash_image(device, image)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
