# MetaTrader 5 Credentials Guide

## Quick Setup

The MT5 MCP server requires your MetaTrader 5 account credentials to connect and execute trades.

### Step 1: Find Your MT5 Credentials

1. **Open MetaTrader 5**
2. **Go to:** Tools → Options
3. **Click:** Server tab
4. **Note down:**
   - **Login:** Your account number (e.g., 12345678)
   - **Server:** Your broker's server name (e.g., MetaQuotes-Demo)
   - **Password:** The password you use to login to MT5

### Step 2: Add to .env File

Open your `.env` file and add:

```env
# MetaTrader 5 Credentials
MT5_LOGIN=12345678
MT5_PASSWORD=YourPassword123
MT5_SERVER=MetaQuotes-Demo
```

### Step 3: Start the Server

```bash
bash scripts/start_mt5_server.sh
```

## Common Server Names

Different brokers use different server naming conventions:

### Demo Accounts
```
MetaQuotes-Demo
ICMarkets-Demo
Pepperstone-Demo
XM-Demo
FXCM-Demo
Exness-Demo
```

### Live Accounts
```
BrokerName-Live
BrokerName-Real
BrokerName-Server01
BrokerName-Server02
```

**Important:** Server names are case-sensitive and must match exactly!

## Finding Your Server Name

### Method 1: In MT5 Terminal
1. Tools → Options → Server tab
2. Look at "Server:" field
3. Copy the exact name

### Method 2: In Account Details
1. Right-click on account in "Navigator" panel
2. Select "Properties"
3. Look at "Server" field

### Method 3: From Broker Email
Check your account confirmation email from your broker - it usually contains:
- Login ID
- Server name
- Initial password

## Security Best Practices

### 1. Use Demo Account First
```env
# Start with demo account
MT5_LOGIN=demo_account_id
MT5_PASSWORD=demo_password
MT5_SERVER=BrokerName-Demo
```

### 2. Keep .env Secure
```bash
# Make sure .env is in .gitignore
echo ".env" >> .gitignore

# Set proper permissions (Linux/Mac)
chmod 600 .env
```

### 3. Never Commit Credentials
```bash
# Check before committing
git status

# .env should NOT appear in git status
# If it does, add to .gitignore immediately
```

### 4. Use Environment Variables (Production)
For production deployments, use environment variables instead of .env file:

```bash
export MT5_LOGIN=12345678
export MT5_PASSWORD=YourPassword123
export MT5_SERVER=BrokerName-Live
```

## Troubleshooting

### Error: "Missing option '--login'"

**Cause:** MT5 credentials not in .env file

**Solution:**
```bash
# Add to .env
MT5_LOGIN=your_login_id
MT5_PASSWORD=your_password
MT5_SERVER=your_server_name
```

### Error: "Authorization failed"

**Possible causes:**
1. Wrong login ID
2. Wrong password
3. Wrong server name
4. Account locked/disabled
5. Server name typo (case-sensitive!)

**Solution:**
1. Verify credentials by logging into MT5 terminal
2. Check server name exactly matches (copy-paste from MT5)
3. Try resetting password in MT5
4. Contact broker if account is locked

### Error: "Connection timeout"

**Possible causes:**
1. No internet connection
2. Broker server is down
3. Firewall blocking connection
4. Wrong server name

**Solution:**
1. Check internet connection
2. Try logging into MT5 terminal
3. Check broker's website for server status
4. Temporarily disable firewall to test

### Error: "Invalid server"

**Cause:** Server name doesn't exist or is misspelled

**Solution:**
1. Copy server name exactly from MT5: Tools → Options → Server
2. Check for typos (case-sensitive)
3. Verify with broker if unsure

## Testing Your Credentials

### Test 1: Login to MT5 Terminal
Before using the MCP server, verify credentials work in MT5:

1. Open MetaTrader 5
2. File → Login to Trade Account
3. Enter your credentials
4. If login succeeds, credentials are correct

### Test 2: Start MCP Server
```bash
bash scripts/start_mt5_server.sh
```

Should see:
```
MT5 Login: 12345678
MT5 Server: MetaQuotes-Demo
Starting server on http://localhost:8001...
Connecting to MT5...
Connected successfully!
```

### Test 3: Test API Connection
```bash
bash scripts/test_mt5_connection.sh
```

Should see:
```
✓ Server is running and responding
✓ Account endpoint is accessible
```

## Multiple Accounts

If you have multiple MT5 accounts, you can switch between them:

### Option 1: Update .env
```env
# Switch to different account
MT5_LOGIN=87654321
MT5_PASSWORD=DifferentPassword
MT5_SERVER=DifferentBroker-Demo
```

### Option 2: Use Environment Variables
```bash
# Override .env for this session
export MT5_LOGIN=87654321
export MT5_PASSWORD=DifferentPassword
export MT5_SERVER=DifferentBroker-Demo

bash scripts/start_mt5_server.sh
```

### Option 3: Multiple .env Files
```bash
# Create separate env files
cp .env .env.demo
cp .env .env.live

# Use specific env file
source .env.demo
bash scripts/start_mt5_server.sh
```

## Password Management

### Changing Your Password

If you change your MT5 password:

1. Update password in MT5 terminal
2. Update `.env` file:
   ```env
   MT5_PASSWORD=NewPassword123
   ```
3. Restart MCP server:
   ```bash
   # Stop current server (Ctrl+C)
   # Start with new password
   bash scripts/start_mt5_server.sh
   ```

### Forgotten Password

1. Use MT5 terminal: Tools → Options → Server → Change Password
2. Or contact your broker for password reset
3. Update `.env` with new password

## Demo vs Live Accounts

### Demo Account (Recommended for Testing)
```env
MT5_LOGIN=demo_account_id
MT5_PASSWORD=demo_password
MT5_SERVER=BrokerName-Demo
PAPER_TRADING_MODE=true
```

**Benefits:**
- No real money at risk
- Test strategies safely
- Learn the system
- Unlimited practice

### Live Account (Production)
```env
MT5_LOGIN=live_account_id
MT5_PASSWORD=live_password
MT5_SERVER=BrokerName-Live
PAPER_TRADING_MODE=false  # Only after thorough testing!
```

**Requirements:**
- Tested in demo for at least 1 week
- Understand all risks
- Start with minimum position sizes
- Have stop-loss strategy
- Monitor closely

## FAQ

**Q: Do I need MT5 terminal running?**
A: No, the MCP server connects directly to broker servers. However, it's recommended to have MT5 open for monitoring.

**Q: Can I use MT4 credentials?**
A: No, only MetaTrader 5 is supported.

**Q: What if my broker uses a different port?**
A: The MCP server connects to standard MT5 ports automatically.

**Q: Can I use investor password?**
A: No, you need the main account password for trading operations.

**Q: Is it safe to store password in .env?**
A: Yes, if .env is in .gitignore and not committed to version control. For production, use environment variables or secrets management.

**Q: Can I run multiple servers with different accounts?**
A: Yes, use different ports:
```bash
uvx metatrader-mcp-server --login 123 --password pass1 --server Server1 --port 8001
uvx metatrader-mcp-server --login 456 --password pass2 --server Server2 --port 8002
```

## Summary Checklist

- [ ] Found MT5 credentials in: Tools → Options → Server
- [ ] Added credentials to `.env` file
- [ ] Verified `.env` is in `.gitignore`
- [ ] Tested login in MT5 terminal
- [ ] Started MCP server successfully
- [ ] Tested API connection
- [ ] Using demo account for testing
- [ ] Paper trading mode enabled

## Getting Help

If you're still having credential issues:

1. **Verify in MT5:** Can you login to MT5 terminal with these credentials?
2. **Check server name:** Copy-paste exactly from MT5 (case-sensitive)
3. **Test connection:** `bash scripts/test_mt5_connection.sh`
4. **Check logs:** Look for specific error messages
5. **Contact broker:** If account is locked or credentials don't work

---

**Remember:** Always start with a demo account and paper trading mode enabled!
