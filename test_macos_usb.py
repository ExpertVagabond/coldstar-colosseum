#!/usr/bin/env python3
"""
Test macOS USB Detection

This script tests the USB detection functionality on macOS.
Run this to verify that USB drives are being detected properly.

Usage:
    python3 test_macos_usb.py
"""

import sys
import platform

def test_usb_detection():
    """Test USB device detection"""
    print("=" * 60)
    print("macOS USB Detection Test")
    print("=" * 60)
    
    # Check OS
    current_os = platform.system()
    print(f"\nCurrent OS: {current_os}")
    
    if current_os != 'Darwin':
        print("⚠️  Warning: Not running on macOS (Darwin)")
        print("   This test is designed for macOS")
    
    # Import USB manager
    try:
        from src.usb import USBManager
        print("✓ Successfully imported USBManager")
    except ImportError as e:
        print(f"✗ Failed to import USBManager: {e}")
        return False
    
    # Create manager instance
    try:
        usb = USBManager()
        print(f"✓ Created USBManager instance")
        print(f"  - System: {usb.system}")
        print(f"  - is_windows: {usb.is_windows}")
        print(f"  - is_macos: {usb.is_macos}")
        print(f"  - is_linux: {usb.is_linux}")
    except Exception as e:
        print(f"✗ Failed to create USBManager: {e}")
        return False
    
    # Check permissions
    print("\n" + "-" * 60)
    print("Checking permissions...")
    try:
        has_perms = usb.check_permissions()
        if has_perms:
            print("✓ Have necessary permissions")
        else:
            print("⚠️  May need elevated permissions for some operations")
    except Exception as e:
        print(f"✗ Error checking permissions: {e}")
    
    # Detect USB devices
    print("\n" + "-" * 60)
    print("Detecting USB devices...")
    try:
        devices = usb.detect_usb_devices()
        print(f"✓ Detection completed")
        print(f"  Found {len(devices)} USB device(s)")
        
        if devices:
            print("\nDetected Devices:")
            for i, dev in enumerate(devices, 1):
                print(f"\n  Device {i}:")
                print(f"    Path:       {dev.get('device', 'Unknown')}")
                print(f"    Size:       {dev.get('size', 'Unknown')}")
                print(f"    Model:      {dev.get('model', 'Unknown')}")
                print(f"    Mountpoint: {dev.get('mountpoint', 'Not mounted')}")
                
                partitions = dev.get('partitions', [])
                if partitions:
                    print(f"    Partitions: {len(partitions)}")
                    for j, part in enumerate(partitions, 1):
                        print(f"      {j}. {part.get('device', 'Unknown')} - {part.get('size', 'Unknown')}")
                        if part.get('mountpoint'):
                            print(f"         Mounted at: {part['mountpoint']}")
        else:
            print("\n⚠️  No USB devices detected")
            print("   Please plug in a USB drive and try again")
            
    except Exception as e:
        print(f"✗ Error detecting USB devices: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    
    return True


def test_diskutil_available():
    """Test if diskutil is available"""
    import subprocess
    
    print("\n" + "-" * 60)
    print("Testing diskutil availability...")
    
    try:
        result = subprocess.run(
            ['diskutil', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ diskutil is available and working")
            
            # Count disks
            disk_count = result.stdout.count('/dev/disk')
            print(f"  Found {disk_count} disk(s) in system")
            return True
        else:
            print(f"⚠️  diskutil returned error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("✗ diskutil not found - not running on macOS?")
        return False
    except Exception as e:
        print(f"✗ Error running diskutil: {e}")
        return False


if __name__ == "__main__":
    print("\n")
    
    # Test diskutil
    diskutil_ok = test_diskutil_available()
    
    if not diskutil_ok and platform.system() == 'Darwin':
        print("\n⚠️  WARNING: diskutil not working properly")
        print("   USB detection may not work")
    
    # Test USB detection
    print("\n")
    success = test_usb_detection()
    
    sys.exit(0 if success else 1)
