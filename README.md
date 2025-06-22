# Yochi Price Monitor

Automated price monitoring for Yochi products at Coles Australia with multi-product scanning and instant notifications.

## 🎯 Features

- **🔍 Multi-Product Scanning** - Finds cheapest Yochi flavor and shows alternatives
- **📱 Triple Notifications** - Telegram (recommended), macOS alerts, and email
- **🤖 Smart Price Tracking** - Learns regular prices and detects 30%+ discounts
- **🛡️ Robust Scraping** - Multiple fallback selectors for website changes
- **📊 Price History** - JSON-based tracking with trend analysis
- **⚙️ Easy Setup** - 3-minute Telegram setup or Gmail integration

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Setup Configuration
```bash
cp config.template.json config.json
# Edit config.json with your notification preferences
```

### 3. Test Installation
```bash
python3 price_monitor.py --test
python3 price_monitor.py --test-notifications
```

## 📱 Notification Setup

### Telegram (Recommended - Easiest!)

**Why Telegram?**
- ✅ Instant mobile notifications (faster than email)
- ✅ Completely free (no server costs)
- ✅ More reliable (no spam folders)
- ✅ 3-minute setup

**Setup Steps:**
1. **Install Telegram** and create account
2. **Create bot**: Message `@BotFather` → `/newbot` → choose name/username
3. **Get Chat ID**: Message `@userinfobot` → copy your chat ID
4. **Update config.json**:
   ```json
   {
     "notifications": {"telegram_enabled": true},
     "telegram": {
       "bot_token": "your-bot-token-here",
       "chat_id": "your-chat-id-here"
     }
   }
   ```
5. **Test**: `python3 price_monitor.py --test-notifications`

### Email (Alternative)

1. **Enable Gmail 2FA** and generate App Password
2. **Set environment variable**: 
   ```bash
   export GMAIL_APP_PASSWORD="your-16-char-password"
   ```
3. **Update config.json**:
   ```json
   {
     "notifications": {"email_enabled": true},
     "email": {"sender_email": "your-email@gmail.com"}
   }
   ```

### macOS Notifications

**Fix if not working:**
```bash
python3 price_monitor.py --request-permissions
```
Then check System Preferences → Notifications → Allow Terminal

## 🔄 Automation Setup

### Option 1: Crontab (Recommended)
```bash
# Check every hour
crontab -e
# Add: 0 * * * * cd /path/to/script && python3 price_monitor.py >> cron.log 2>&1
```

### Option 2: macOS launchd
Create `~/Library/LaunchAgents/com.user.yochi-monitor.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.yochi-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/full/path/to/price_monitor.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/full/path/to/script/directory</string>
    <key>StartInterval</key>
    <integer>3600</integer>
</dict>
</plist>
```

Load with: `launchctl load ~/Library/LaunchAgents/com.user.yochi-monitor.plist`

## 🧪 Testing

### Quick Tests
```bash
# Test with mock data
python3 price_monitor.py --test

# Test notifications
python3 price_monitor.py --test-notifications

# Test real scraping
python3 price_monitor.py

# Run test suite
python3 test_price_monitor.py
```

### Test Scenarios

**Discount Detection Test:**
1. Set high regular price in config: `"regular_price": 10.00`
2. Run: `python3 price_monitor.py --test`
3. Should detect 55% discount and send notifications

**First Run Test:**
1. Delete `price_history.json`
2. Set `"regular_price": null`
3. Run test - should create history but no discount alert

## 📋 Configuration Options

| Parameter | Description | Example |
|-----------|-------------|---------|
| `discount_threshold` | Minimum discount to trigger alerts | `0.30` (30%) |
| `regular_price` | Known regular price (null = auto-detect) | `6.50` or `null` |
| `notifications.telegram_enabled` | Enable Telegram notifications | `true` |
| `notifications.email_enabled` | Enable email notifications | `false` |
| `notifications.macos_enabled` | Enable macOS notifications | `true` |
| `telegram.bot_token` | Bot token from @BotFather | `"123456:ABC..."` |
| `telegram.chat_id` | Your chat ID from @userinfobot | `"987654321"` |
| `logging.level` | Log verbosity | `"INFO"` |

## 🛠 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **"Module not found"** | Run `pip3 install -r requirements.txt` |
| **macOS notifications not working** | Run `python3 price_monitor.py --request-permissions` |
| **Telegram not working** | Ensure you messaged your bot first |
| **Email not sending** | Check `GMAIL_APP_PASSWORD` environment variable |
| **No price found** | Website may have changed; check logs |
| **Cron not running** | Use full paths in cron entries |

### Debug Commands
```bash
# Verbose logging
tail -f price_monitor.log

# Test permissions
python3 price_monitor.py --request-permissions

# Manual run (like cron)
cd /path/to/script && python3 price_monitor.py
```

## 📧 Notification Examples

**Telegram Message:**
```
🎉 Best Yochi Deal Found!

🏆 BEST DEAL: Wild Berry Yoghurt
💰 Price: $3.80
🔥 Discount: 60% off!

📋 Other options:
• Vanilla Yoghurt $4.00
• Mango Yoghurt $4.20
• Natural Yoghurt $4.50

🛒 Shop Now at Coles
```

## 📁 File Structure

```
yochi-price-monitor/
├── price_monitor.py          # Main monitoring script
├── config.json              # Your configuration (create from template)
├── config.template.json     # Configuration template  
├── requirements.txt         # Python dependencies
├── test_price_monitor.py    # Test suite
├── price_history.json       # Price history (auto-generated)
├── price_monitor.log        # Log file (auto-generated)
└── README.md               # This file
```

## 🔒 Security

- **Sensitive files excluded** from git via `.gitignore`
- **Environment variables** for passwords (not in config)
- **Private repository** recommended
- **App-specific passwords** for Gmail (not main password)

## 🤝 Contributing

This project was created with Claude Code. To contribute:

1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

## 📄 License

Private use only. Not for redistribution.

---

🤖 **Generated with [Claude Code](https://claude.ai/code)**

Co-Authored-By: Claude <noreply@anthropic.com>