"""
USB Device Detection and Management
"""

import subprocess
import os
import json
from pathlib import Path
from typing import List, Optional, Dict

from src.ui import print_success, print_error, print_info, print_warning, print_device_list


class USBManager:
    def __init__(self):
        self.detected_devices: List[Dict] = []
        self.selected_device: Optional[Dict] = None
        self.mount_point: Optional[str] = None
    
    def detect_usb_devices(self) -> List[Dict]:
        devices = []
        
        try:
            result = subprocess.run(
                ['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,TRAN,MODEL,RM'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print_warning("Could not run lsblk, trying alternative method")
                return self._detect_via_sys()
            
            data = json.loads(result.stdout)
            
            for device in data.get('blockdevices', []):
                if device.get('tran') == 'usb' or device.get('rm') == '1':
                    if device.get('type') == 'disk':
                        dev_info = {
                            'device': f"/dev/{device['name']}",
                            'size': device.get('size', 'Unknown'),
                            'model': device.get('model', 'USB Device').strip() if device.get('model') else 'USB Device',
                            'mountpoint': None,
                            'partitions': []
                        }
                        
                        for child in device.get('children', []):
                            partition = {
                                'device': f"/dev/{child['name']}",
                                'size': child.get('size', 'Unknown'),
                                'mountpoint': child.get('mountpoint')
                            }
                            dev_info['partitions'].append(partition)
                            if partition['mountpoint']:
                                dev_info['mountpoint'] = partition['mountpoint']
                        
                        devices.append(dev_info)
            
            self.detected_devices = devices
            return devices
            
        except subprocess.TimeoutExpired:
            print_error("Device detection timed out")
            return []
        except json.JSONDecodeError:
            print_warning("Could not parse lsblk output")
            return self._detect_via_sys()
        except FileNotFoundError:
            print_warning("lsblk not found, trying alternative method")
            return self._detect_via_sys()
        except Exception as e:
            print_error(f"Error detecting USB devices: {e}")
            return []
    
    def _detect_via_sys(self) -> List[Dict]:
        devices = []
        
        try:
            block_path = Path("/sys/block")
            if not block_path.exists():
                return devices
            
            for device_dir in block_path.iterdir():
                device_name = device_dir.name
                
                if device_name.startswith('sd') or device_name.startswith('nvme'):
                    removable_path = device_dir / "removable"
                    if removable_path.exists():
                        with open(removable_path) as f:
                            if f.read().strip() == '1':
                                size_path = device_dir / "size"
                                size = "Unknown"
                                if size_path.exists():
                                    with open(size_path) as f:
                                        sectors = int(f.read().strip())
                                        size_bytes = sectors * 512
                                        size = self._format_size(size_bytes)
                                
                                devices.append({
                                    'device': f"/dev/{device_name}",
                                    'size': size,
                                    'model': 'USB Device',
                                    'mountpoint': None,
                                    'partitions': []
                                })
            
            self.detected_devices = devices
            return devices
            
        except Exception as e:
            print_error(f"Alternative detection failed: {e}")
            return []
    
    def _format_size(self, size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}PB"
    
    def select_device(self, index: int) -> Optional[Dict]:
        if 0 <= index < len(self.detected_devices):
            self.selected_device = self.detected_devices[index]
            print_success(f"Selected device: {self.selected_device['device']}")
            return self.selected_device
        print_error("Invalid device selection")
        return None
    
    def mount_device(self, device_path: str = None, mount_point: str = None) -> Optional[str]:
        device = device_path or (self.selected_device['device'] if self.selected_device else None)
        if not device:
            print_error("No device specified")
            return None
        
        if self.selected_device and self.selected_device.get('partitions'):
            partition = self.selected_device['partitions'][0]
            device = partition['device']
            if partition.get('mountpoint'):
                self.mount_point = partition['mountpoint']
                print_info(f"Device already mounted at: {self.mount_point}")
                return self.mount_point
        
        if not mount_point:
            mount_point = f"/tmp/solana_usb_{os.getpid()}"
        
        try:
            os.makedirs(mount_point, exist_ok=True)
            
            result = subprocess.run(
                ['mount', device, mount_point],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.mount_point = mount_point
                print_success(f"Mounted {device} at {mount_point}")
                return mount_point
            else:
                if "already mounted" in result.stderr:
                    print_info(f"Device is already mounted")
                    return mount_point
                print_error(f"Mount failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print_error("Mount operation timed out")
            return None
        except PermissionError:
            print_error("Permission denied. Run with sudo for USB operations.")
            return None
        except Exception as e:
            print_error(f"Mount error: {e}")
            return None
    
    def unmount_device(self, mount_point: str = None) -> bool:
        target = mount_point or self.mount_point
        if not target:
            print_warning("No mount point to unmount")
            return True
        
        try:
            result = subprocess.run(
                ['umount', target],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_success(f"Unmounted {target}")
                if target == self.mount_point:
                    self.mount_point = None
                return True
            else:
                print_error(f"Unmount failed: {result.stderr}")
                return False
                
        except Exception as e:
            print_error(f"Unmount error: {e}")
            return False
    
    def check_wallet_exists(self, mount_point: str = None) -> bool:
        target = mount_point or self.mount_point
        if not target:
            return False
        
        wallet_path = Path(target) / "wallet" / "keypair.json"
        return wallet_path.exists()
    
    def get_wallet_paths(self, mount_point: str = None) -> Dict[str, str]:
        target = mount_point or self.mount_point
        if not target:
            return {}
        
        base = Path(target)
        return {
            'wallet': str(base / 'wallet'),
            'keypair': str(base / 'wallet' / 'keypair.json'),
            'pubkey': str(base / 'wallet' / 'pubkey.txt'),
            'inbox': str(base / 'inbox'),
            'outbox': str(base / 'outbox')
        }
    
    def is_root(self) -> bool:
        return os.geteuid() == 0
    
    def check_permissions(self) -> bool:
        if not self.is_root():
            print_warning("USB operations require root privileges")
            print_info("Please run with: sudo python main.py")
            return False
        return True
