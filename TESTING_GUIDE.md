# Yochi Price Monitor Testing Guide

## Quick Test Checklist

### 1. Basic Setup Test
```bash
# Install dependencies
pip3 install -r requirements.txt

# Create config from template
cp config.template.json config.json

# Test script runs without errors
python3 price_monitor.py --test
```

### 2. Notification System Tests

#### macOS Notification Test
```bash
python3 price_monitor.py --test-notifications
```
**Expected Result**: You should see a macOS notification appear.

**Troubleshooting**:
- If no notification appears, check System Preferences → Notifications → Terminal
- Ensure notifications are allowed for Terminal app

#### Email Notification Test
1. Set up Gmail app password:
```bash
export GMAIL_APP_PASSWORD="your-16-char-password"
```

2. Enable email in `config.json`:
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

3. Run test:
```bash
python3 price_monitor.py --test-notifications
```

**Expected Result**: Email should be sent to your Gmail account.

### 3. Web Scraping Test

#### Test with Mock Data
```bash
python3 price_monitor.py --test
```
**Expected Result**: Should complete without errors, showing mock price data.

#### Test Real Web Scraping
```bash
python3 price_monitor.py
```
**Expected Result**: Should attempt to scrape real Coles website.

## Detailed Testing Scenarios

### Scenario 1: First Run (No Price History)

**Setup**:
- Delete `price_history.json` if it exists
- Set `regular_price: null` in config

**Test**:
```bash
python3 price_monitor.py --test
```

**Expected Behavior**:
- Creates new `price_history.json`
- Logs warning about no regular price for comparison
- Records price but doesn't trigger discount alert

### Scenario 2: Discount Detection

**Setup**:
1. Set a high regular price in config:
```json
{
  "regular_price": 10.00,
  "discount_threshold": 0.30
}
```

2. Run with test mode (mock price is $4.50):
```bash
python3 price_monitor.py --test
```

**Expected Behavior**:
- Detects 55% discount (4.50 vs 10.00)
- Sends both macOS and email notifications
- Logs discount information

### Scenario 3: Network Error Handling

**Test**: Disconnect internet and run:
```bash
python3 price_monitor.py
```

**Expected Behavior**:
- Logs network error
- Doesn't crash
- No notifications sent

### Scenario 4: Malformed Website Response

**Test**: This is harder to simulate, but script should handle:
- Invalid HTML structure
- Missing price elements
- Changed CSS selectors

**Expected Behavior**:
- Logs warning about price extraction failure
- Returns gracefully without crashing

## Configuration Testing

### Test Different Discount Thresholds

1. Set threshold to 10% (0.10):
```json
{"discount_threshold": 0.10}
```

2. Test with mock data:
```bash
python3 price_monitor.py --test
```

### Test Email Configuration

Test invalid email settings:

1. Wrong SMTP server:
```json
{"email": {"smtp_server": "invalid.server.com"}}
```

2. Wrong credentials:
```bash
export GMAIL_APP_PASSWORD="wrong-password"
```

**Expected**: Should log errors but not crash.

## Cron Job Testing

### Test Cron Entry Syntax

Before adding to crontab, test the command manually:

```bash
cd /path/to/script && /usr/bin/python3 price_monitor.py >> cron.log 2>&1
```

### Monitor Cron Execution

1. Add cron job with short interval (every 2 minutes):
```
*/2 * * * * cd /path/to/script && /usr/bin/python3 price_monitor.py >> cron.log 2>&1
```

2. Monitor execution:
```bash
tail -f cron.log
tail -f price_monitor.log
```

3. Remove test cron job after verification:
```bash
crontab -e
# Remove or comment out the test line
```

## Performance Testing

### Memory Usage Test
```bash
# Run with memory monitoring
/usr/bin/time -l python3 price_monitor.py --test
```

### Response Time Test
```bash
# Time the web scraping
time python3 price_monitor.py
```

**Expected**: Should complete within 30 seconds under normal conditions.

## Error Condition Testing

### Test with Invalid Configuration

1. **Invalid JSON syntax**:
```bash
echo '{invalid json' > config.json
python3 price_monitor.py
```

2. **Missing required fields**:
```json
{"url": ""}
```

3. **Invalid URL**:
```json
{"url": "not-a-valid-url"}
```

**Expected**: Script should handle errors gracefully and log appropriate messages.

## Log Analysis

### Check Log Levels

Test different log levels in config:
```json
{"logging": {"level": "DEBUG"}}
```

**Expected**: More verbose output in logs.

### Verify Log Rotation

Run script multiple times and verify:
- Log file doesn't grow infinitely
- Old entries are maintained appropriately

## Integration Testing

### End-to-End Test

1. **Setup**: Clean environment with no history
2. **Run**: Multiple executions over time
3. **Verify**:
   - Price history is building
   - Regular price calculation improves
   - Discount detection becomes more accurate

### Real-World Test

1. **Temporary high regular price**: Set unrealistically high regular price
2. **Real scraping**: Disable test mode
3. **Verify notifications**: Should trigger on first real run
4. **Reset**: Restore normal configuration

## Verification Steps

### ✅ Successful Test Indicators

- [ ] Script runs without Python errors
- [ ] Configuration file loads correctly
- [ ] macOS notifications appear
- [ ] Email notifications are received
- [ ] Price history file is created and updated
- [ ] Log file contains appropriate entries
- [ ] Cron job executes successfully
- [ ] Network errors are handled gracefully
- [ ] Discount detection logic works correctly

### 🚨 Failure Indicators

- Python exceptions or stack traces
- No notifications despite discount conditions
- Empty or corrupted price history file
- Cron jobs not executing
- Email authentication failures
- Infinite loops or hanging processes

## Troubleshooting Common Test Failures

### "ImportError: No module named 'requests'"
```bash
pip3 install -r requirements.txt
```

### "Permission denied" for osascript
- Check macOS privacy settings
- Allow Terminal to send notifications

### "Authentication failed" for email
- Verify Gmail app password is correct
- Check 2FA is enabled on Gmail account
- Ensure environment variable is set correctly

### Cron job not running
- Use full paths in cron entries
- Check cron service is running: `sudo launchctl list | grep cron`
- Verify environment variables are available to cron

### No price found from website
- Check if Coles website structure changed
- Verify URL is accessible
- Test with --test flag to use mock data