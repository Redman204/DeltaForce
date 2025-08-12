#!/usr/bin/env python3
"""
Simple launcher for the AFK Automation Script
This script handles dependency checking and provides a user-friendly interface.
"""

import sys
import subprocess
import importlib.util

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = ['pydirectinput', 'pyautogui', 'pynput']
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nTo install missing packages, run:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("=" * 60)
    print("         AFK Automation Script Launcher")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ All dependencies are installed.")
    print()
    
    # Check config file
    try:
        import config
        print("✓ Configuration file loaded.")
    except ImportError:
        print("✗ Configuration file (config.py) not found!")
        print("Please ensure config.py is in the same directory.")
        sys.exit(1)
    
    print()
    print("IMPORTANT WARNINGS:")
    print("- Use this script responsibly and in accordance with game terms of service")
    print("- Some games prohibit automation tools")
    print("- This script may trigger anti-cheat systems")
    print("- Use at your own risk")
    print()
    
    response = input("Do you understand and accept these risks? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("Script cancelled.")
        sys.exit(0)
    
    print()
    print("Starting AFK Automation...")
    print("Controls:")
    print("- Right Shift: Pause/Resume")
    print("- Ctrl+C: Stop completely")
    if config.FAILSAFE_ENABLED:
        print("- Move mouse to top-left corner: Emergency stop (PyAutoGUI failsafe)")
    print()
    
    try:
        from afk_automation import AFKAutomation
        afk_bot = AFKAutomation()
        afk_bot.run()
    except KeyboardInterrupt:
        print("\nScript stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()