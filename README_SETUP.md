# Yochi Price Monitor Setup Guide

## Prerequisites

yochitest@gmail.com
"Yoch1t3st$2"

- macOS system
- Python 3.7 or higher
- Internet connection
- Gmail account (for email notifications)

## Installation

### 1. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Setup Configuration

1. Copy the configuration template:
```bash
cp config.template.json config.json
```

2. Edit `config.json` with your preferences:
   - Set `regular_price` if you know the normal price (optional - will be learned from history)
   - Adjust `discount_threshold` (0.30 = 30% discount)
   - Configure email settings if desired

### 3. Setup Gmail App Password (for email notifications)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Set environment variable:
```bash
export GMAIL_APP_PASSWORD="your-16-character-app-password"
```

To make this permanent, add to your `~/.zshrc` or `~/.bash_profile`:
```bash
echo 'export GMAIL_APP_PASSWORD="your-16-character-app-password"' >> ~/.zshrc
```

### 4. Setup Telegram Notifications (Recommended - Easiest Option!)

#### Why Telegram?
- ✅ **Instant mobile notifications** (faster than email)
- ✅ **Completely free** (no server costs)
- ✅ **More reliable** than email (no spam folders)
- ✅ **Easy 3-minute setup** (easier than Gmail)
- ✅ **Works worldwide**

#### Step-by-Step Telegram Setup:

1. **Install Telegram App** (if you don't have it)
   - Download from App Store/Google Play
   - Create account with your phone number

2. **Create Your Bot** (1 minute)
   - Open Telegram, search for `@BotFather`
   - Send: `/newbot`
   - Choose bot name: `Yochi Price Alert`
   - Choose username: `yochi_price_bot_` + random numbers (must be unique)
   - **Copy the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

3. **Get Your Chat ID** (30 seconds)
   - Search for `@userinfobot` in Telegram
   - Send it any message
   - **Copy your chat ID** (looks like: `987654321`)

4. **Update Configuration**
   - Edit `config.json`:
   ```json
   {
     "notifications": {
       "telegram_enabled": true
     },
     "telegram": {
       "bot_token": "your-bot-token-here",
       "chat_id": "your-chat-id-here"
     }
   }
   ```

5. **Test Telegram** (30 seconds)
   ```bash
   python3 price_monitor.py --test-notifications
   ```
   You should receive a test message in Telegram!

### 5. Setup Gmail Email Notifications (Alternative)

If you prefer email over Telegram, follow these steps:

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Set environment variable:
```bash
export GMAIL_APP_PASSWORD="your-16-character-app-password"
```

4. Update `config.json`:
```json
{
  "notifications": {
    "email_enabled": true
  },
  "email": {
    "sender_email": "your-email@gmail.com"
  }
}
```

### 6. Test All Notifications

Test basic functionality:
```bash
python3 price_monitor.py --test
```

Test all notification systems:
```bash
python3 price_monitor.py --test-notifications
```

## Cron Job Setup

### Option 1: Using crontab (Recommended)

1. Make the script executable:
```bash
chmod +x price_monitor.py
```

2. Edit crontab:
```bash
crontab -e
```

3. Add entry to check every hour:
```bash
0 * * * * cd /path/to/your/script && /usr/bin/python3 price_monitor.py >> cron.log 2>&1
```

Or every 30 minutes:
```bash
*/30 * * * * cd /path/to/your/script && /usr/bin/python3 price_monitor.py >> cron.log 2>&1
```

### Option 2: Using launchd (macOS native)

1. Create a plist file `~/Library/LaunchAgents/com.user.yochi-monitor.plist`:

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
    <key>StandardOutPath</key>
    <string>/full/path/to/script/directory/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/full/path/to/script/directory/launchd_error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>GMAIL_APP_PASSWORD</key>
        <string>your-app-password-here</string>
    </dict>
</dict>
</plist>
```

2. Load the job:
```bash
launchctl load ~/Library/LaunchAgents/com.user.yochi-monitor.plist
```

3. Start the job:
```bash
launchctl start com.user.yochi-monitor
```

## Configuration Options

### config.json Parameters

- `url`: Coles search URL for Yochi products
- `discount_threshold`: Minimum discount percentage to trigger alerts (0.30 = 30%)
- `regular_price`: Known regular price (null to auto-detect from history)
- `check_interval_minutes`: Not used in cron mode
- `price_history_file`: JSON file to store price history
- `notifications.macos_enabled`: Enable/disable macOS notifications
- `notifications.email_enabled`: Enable/disable email notifications
- `notifications.telegram_enabled`: Enable/disable Telegram notifications
- `email.sender_email`: Your Gmail address
- `telegram.bot_token`: Your Telegram bot token from @BotFather
- `telegram.chat_id`: Your Telegram chat ID from @userinfobot
- `logging.level`: Log level (DEBUG, INFO, WARNING, ERROR)

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure you've installed requirements: `pip3 install -r requirements.txt`

2. **macOS notifications not working**
   - Check System Preferences → Notifications → Terminal (allow notifications)

3. **Email not sending**
   - Verify `GMAIL_APP_PASSWORD` environment variable is set
   - Check that 2FA is enabled on Gmail
   - Verify app password is correct (16 characters, no spaces)

4. **Telegram not working**
   - Verify bot token is correct (should have format: `123456789:ABC...`)
   - Check chat ID is your personal chat ID (numeric, like `987654321`)
   - Make sure you've sent at least one message to your bot first
   - Test with: `python3 price_monitor.py --test-notifications`

5. **Price not found**
   - Website structure may have changed
   - Check logs for specific error messages
   - Test with `--test` flag to use mock data

6. **Cron job not running**
   - Check cron logs: `tail -f cron.log`
   - Verify full paths in cron entries
   - Ensure environment variables are available to cron

### Debug Mode

Run with verbose logging:
```bash
python3 price_monitor.py --config config.json
```

Check log file:
```bash
tail -f price_monitor.log
```

## Security Notes

- Store Gmail app password securely as environment variable
- Don't commit `config.json` with sensitive information to version control
- Consider using macOS Keychain for password storage in production

## File Structure

```
yochi-price-monitor/
├── price_monitor.py          # Main script
├── config.json              # Your configuration (create from template)
├── config.template.json     # Configuration template
├── requirements.txt         # Python dependencies
├── price_history.json       # Price history (auto-generated)
├── price_monitor.log        # Log file (auto-generated)
└── README_SETUP.md          # This file
```