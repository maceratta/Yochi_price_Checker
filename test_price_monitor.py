#!/usr/bin/env python3
"""
Test script for Yochi Price Monitor
Run this to verify all components are working correctly.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

def test_dependencies():
    """Test that all required dependencies are available."""
    print("Testing dependencies...")
    
    try:
        import requests
        import bs4
        print("✅ All dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip3 install -r requirements.txt")
        return False

def test_config_creation():
    """Test configuration file creation."""
    print("Testing configuration creation...")
    
    # Create temporary config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            "url": "https://www.coles.com.au/search/products?q=yochi",
            "discount_threshold": 0.30,
            "regular_price": 6.00,
            "notifications": {"macos_enabled": True, "email_enabled": False},
            "email": {"sender_email": "test@example.com"},
            "logging": {"level": "INFO", "file": "test.log"}
        }
        json.dump(config, f, indent=2)
        temp_config = f.name
    
    try:
        # Test loading config
        cmd = [sys.executable, "price_monitor.py", "--config", temp_config, "--test"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        os.unlink(temp_config)  # Clean up
        
        if result.returncode == 0:
            print("✅ Configuration and basic functionality working")
            return True
        else:
            print(f"❌ Script failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Script timed out")
        return False
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False

def test_notifications():
    """Test notification systems."""
    print("Testing macOS notifications...")
    
    try:
        # Test osascript availability
        result = subprocess.run(
            ["osascript", "-e", 'display notification "Test" with title "Test"'],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ macOS notifications working")
            return True
        else:
            print("❌ macOS notifications failed - check System Preferences")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Notification test timed out")
        return False
    except FileNotFoundError:
        print("❌ osascript not found - not on macOS?")
        return False
    except Exception as e:
        print(f"❌ Error testing notifications: {e}")
        return False

def test_email_setup():
    """Test email configuration."""
    print("Testing email setup...")
    
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_password:
        print("⚠️  GMAIL_APP_PASSWORD not set - email notifications won't work")
        print("   Set with: export GMAIL_APP_PASSWORD='your-app-password'")
        return False
    
    if len(gmail_password) != 16:
        print("⚠️  GMAIL_APP_PASSWORD should be 16 characters")
        return False
    
    print("✅ Gmail app password is configured")
    return True

def test_telegram_setup():
    """Test Telegram configuration."""
    print("Testing Telegram setup...")
    
    # Check if config exists and has Telegram settings
    try:
        if not os.path.exists("config.json"):
            print("⚠️  config.json not found - create from config.template.json")
            return False
            
        with open("config.json", "r") as f:
            config = json.load(f)
        
        telegram_config = config.get("telegram", {})
        bot_token = telegram_config.get("bot_token", "")
        chat_id = telegram_config.get("chat_id", "")
        
        if not bot_token or bot_token == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz":
            print("⚠️  Telegram bot_token not configured")
            print("   Get token from @BotFather in Telegram")
            return False
        
        if not chat_id or chat_id == "987654321":
            print("⚠️  Telegram chat_id not configured")
            print("   Get your chat ID from @userinfobot in Telegram")
            return False
        
        # Validate token format
        if not bot_token.count(":") == 1 or len(bot_token.split(":")[0]) < 8:
            print("⚠️  Bot token format looks incorrect")
            print("   Should be like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            return False
        
        # Validate chat ID format
        if not chat_id.isdigit():
            print("⚠️  Chat ID should be numeric")
            print("   Should be like: 987654321")
            return False
        
        print("✅ Telegram configuration looks good")
        return True
        
    except Exception as e:
        print(f"❌ Error checking Telegram config: {e}")
        return False

def test_file_permissions():
    """Test file creation permissions."""
    print("Testing file permissions...")
    
    try:
        # Test creating log file
        with open("test_permissions.log", "w") as f:
            f.write("test")
        os.unlink("test_permissions.log")
        
        # Test creating JSON file
        with open("test_permissions.json", "w") as f:
            json.dump({"test": True}, f)
        os.unlink("test_permissions.json")
        
        print("✅ File permissions OK")
        return True
        
    except Exception as e:
        print(f"❌ File permission error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Yochi Price Monitor Test Suite")
    print("=" * 40)
    
    tests = [
        test_dependencies,
        test_file_permissions,
        test_config_creation,
        test_notifications,
        test_email_setup,
        test_telegram_setup,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
        print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your price monitor is ready to use.")
        print("\nNext steps:")
        print("1. Copy config.template.json to config.json")
        print("2. Set up notifications:")
        print("   • For Telegram (recommended): Follow Telegram setup in README_SETUP.md")
        print("   • For Email: Set GMAIL_APP_PASSWORD and edit config.json")
        print("3. Set up cron job (see README_SETUP.md)")
        print("4. Run: python3 price_monitor.py --test")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()