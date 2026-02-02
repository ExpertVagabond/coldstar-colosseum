#!/usr/bin/env python3
"""
Test script to verify TUI setup is working
"""

import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    dependencies = {
        'textual': 'Textual TUI framework',
        'rich': 'Rich text formatting',
        'questionary': 'Interactive prompts'
    }

    missing = []
    for dep, desc in dependencies.items():
        try:
            __import__(dep)
            print(f"✅ {dep:15} - {desc}")
        except ImportError:
            print(f"❌ {dep:15} - {desc} (MISSING)")
            missing.append(dep)

    return len(missing) == 0

def check_tui_files():
    """Check if TUI files can be imported"""
    files = {
        'flash_usb_tui': 'Flash USB Interface',
        'vault_dashboard_tui': 'Vault Dashboard',
        'launch_tui': 'Interactive Launcher'
    }

    print("\n" + "="*50)
    print("TUI FILES CHECK")
    print("="*50)

    all_ok = True
    for module, desc in files.items():
        try:
            __import__(module)
            print(f"✅ {module:25} - {desc}")
        except Exception as e:
            print(f"❌ {module:25} - {desc}")
            print(f"   Error: {e}")
            all_ok = False

    return all_ok

def main():
    print("="*50)
    print("COLDSTAR TUI SETUP CHECK")
    print("="*50)
    print()

    # Check dependencies
    deps_ok = check_dependencies()

    # Check TUI files
    files_ok = check_tui_files()

    print("\n" + "="*50)
    if deps_ok and files_ok:
        print("✅ ALL CHECKS PASSED!")
        print("="*50)
        print("\nYou can now run the TUI interfaces:")
        print("\n1. Flash USB Interface:")
        print("   python3 flash_usb_tui.py")
        print("\n2. Vault Dashboard:")
        print("   python3 vault_dashboard_tui.py")
        print("\n3. Interactive Launcher:")
        print("   python3 launch_tui.py")
        print("\n4. Demo Script:")
        print("   ./demo_tui.sh")
        print("\n" + "="*50)
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("="*50)
        print("\nInstall missing dependencies with:")
        print("   pip install -e .")
        print("\nOr manually:")
        print("   pip install textual rich questionary")
        return 1

if __name__ == "__main__":
    sys.exit(main())
