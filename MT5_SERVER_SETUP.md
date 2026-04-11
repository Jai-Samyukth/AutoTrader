# MetaTrader 5 MCP Server Setup

## What is the MT5 MCP Server?

The MT5 MCP (Model Context Protocol) server is a bridge between AutoTrader and MetaTrader 5. It provides an HTTP API that allows the bot to:
- Get account information
- Fetch current positions
- Get symbol information (prices, spreads, etc.)
- Place market orders
- Close positions
- Modify stop-loss and take-profit levels

## Why Do You Need It?

AutoTrader cannot directly communicate with MetaTrader 5. The MCP server acts as a translator:

```
AutoTrader Bot → HTTP API (port 8001) → MCP Server → MetaTrader 5
```

**Without the MCP server running, you'll see this error:**
```
ERROR: 404 Client Error: Not Found for url: http://localhost:8001/api/v1/account
```

## Installation

### Step 1: Install UV (includes uvx)

UV is a fast Python package manager that includes `uvx` for running packages.

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Verify installation:**
```bash
uvx --version
```

### Step 2: Install MetaTrader 5

1. Download from [metatrader5.com](https://www.metatrader5.com/)
2. Install and create/login to a trading account
3. Keep MT5 running while using AutoTrader

## Starting the Server

### Prerequisites

Before starting the server, you need your MT5 account credentials:
- **Login ID**: Your MT5 account number
- **Password**: Your MT5 account password  
- **Server**: Your broker's server name

**To find these in MetaTrader 5:**
1. Open MT5
2. Go to: Tools → Options → Server tab
3. Note your Login, Server name
4. Password is what you use to login

### Configure Credentials

Add your MT5 credentials to `.env` file:

```env
# MetaTrader 5 Credentials
MT5_LOGIN=12345678
MT5_PASSWORD=YourPassword123
MT5_SERVER=MetaQuotes-Demo

# Common server examples:
# MT5_SERVER=MetaQuotes-Demo
# MT5_SERVER=ICMarkets-Demo
# MT5_SERVER=Pepperstone-Demo
# MT5_SERVER=YourBroker-Live
```

### Option 1: Using the Script (Recommended)

**Bash (Git Bash, Linux, macOS):**
```bash
bash scripts/start_mt5_server.sh
```

**PowerShell (Windows):**
```powershell
.\scripts\start_mt5_server.ps1
```

The script will:
1. Check if `uvx` is installed
2. Load credentials from `.env` file
3. Start the server on port 8001
4. Display connection information

### Option 2: Manual Start

```bash
uvx metatrader-mcp-server \
    --login YOUR_LOGIN_ID \
    --password YOUR_PASSWORD \
    --server YOUR_SERVER_NAME \
    --transport sse \
    --host 127.0.0.1 \
    --port 8001
```

**Example:**
```bash
uvx metatrader-mcp-server \
    --login 12345678 \
    --password MyPassword123 \
    --server MetaQuotes-Demo \
    --transport sse \
    --host 127.0.0.1 \
    --port 8001
```

## What You Should See

When the server starts successfully:

```
============================================================
Starting MetaTrader 5 MCP Server
============================================================
MT5 Login: 12345678
MT5 Server: MetaQuotes-Demo
Starting server on http://localhost:8001...

Press Ctrl+C to stop the server
============================================================

Connecting to MT5...
Connected successfully!
Server running on http://localhost:8001
```

**Keep this terminal open!** The server must run continuously while AutoTrader is running.

**Note:** The server connects directly to MT5 servers - you don't need MT5 terminal running locally (though it's recommended for monitoring).

## Testing the Connection

### Option 1: Using the Test Script

```bash
bash scripts/test_mt5_connection.sh
```

### Option 2: Manual Test

```bash
# Test if server is running
curl http://localhost:8001/health

# Test account endpoint
curl http://localhost:8001/api/v1/account
```

## Troubleshooting

### Error: "Missing option '--login'"

**Solution:** Add MT5 credentials to `.env` file

```env
MT5_LOGIN=your_login_id
MT5_PASSWORD=your_password
MT5_SERVER=your_server_name
```

Then run the script again:
```bash
bash scripts/start_mt5_server.sh
```

### Error: "Invalid credentials" or "Authorization failed"

**Possible causes:**
1. Wrong login ID, password, or server name
2. Account is locked or disabled
3. Server name is incorrect

**Solution:**
1. Verify credentials in MT5: Tools → Options → Server
2. Try logging into MT5 terminal first to verify credentials work
3. Check server name exactly matches (case-sensitive)
4. Common server formats:
   - `BrokerName-Demo`
   - `BrokerName-Live`
   - `BrokerName-Server01`

### Error: "uvx: command not found"

**Solution:** Install UV first
```bash
# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Error: "Port 8001 already in use"

**Solution:** Kill the process using port 8001

**Windows:**
```bash
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

**Linux/macOS:**
```bash
lsof -i :8001
kill -9 <PID>
```

### Error: "Connection refused" or "404 Not Found"

**Possible causes:**
1. MT5 MCP server is not running
2. MetaTrader 5 is not running
3. MetaTrader 5 is not logged in

**Solution:**
1. Start MetaTrader 5 and login
2. Start the MCP server: `bash scripts/start_mt5_server.sh`
3. Wait a few seconds for the server to initialize
4. Test connection: `bash scripts/test_mt5_connection.sh`

### Server starts but AutoTrader can't connect

**Check:**
1. Is MT5 running? (must be open and logged in)
2. Is the server running on port 8001? (check terminal output)
3. Is there a firewall blocking localhost connections?

**Test manually:**
```bash
curl http://localhost:8001/api/v1/account
```

If this works but AutoTrader doesn't connect, check your `.env` file:
```env
MT5_API_URL=http://localhost:8001/api/v1
```

## Running AutoTrader with MT5 Server

### Two-Terminal Setup

You need TWO terminals running simultaneously:

**Terminal 1: MT5 MCP Server**
```bash
bash scripts/start_mt5_server.sh
# Keep this running!
```

**Terminal 2: AutoTrader Bot**
```bash
bash scripts/run_once.sh  # Test mode
# or
bash scripts/run.sh       # Continuous mode
```

### Monitoring

**Terminal 3: Logs (optional)**
```bash
bash scripts/logs.sh follow
```

## Server Endpoints

The MCP server provides these endpoints:

- `GET /health` - Health check
- `GET /api/v1/account` - Get account information
- `GET /api/v1/positions` - Get open positions
- `GET /api/v1/symbol/{symbol}` - Get symbol information
- `POST /api/v1/order/market` - Place market order
- `POST /api/v1/position/close` - Close position
- `POST /api/v1/position/modify` - Modify position SL/TP

## Security Notes

- The server runs on `localhost` only (not accessible from other machines)
- No authentication is required (assumes trusted local environment)
- Never expose port 8001 to the internet
- Use paper trading mode for testing

## Advanced Configuration

### Custom Port

If you need to use a different port:

```bash
# Set environment variable
export MT5_SERVER_PORT=8002

# Start server
uvx metatrader-mcp-server --port 8002
```

Update `.env`:
```env
MT5_API_URL=http://localhost:8002/api/v1
```

### Running as Background Service

**Linux (systemd):**
```bash
# Create service file
sudo nano /etc/systemd/system/mt5-mcp.service

[Unit]
Description=MetaTrader 5 MCP Server
After=network.target

[Service]
Type=simple
User=youruser
ExecStart=/home/youruser/.local/bin/uvx metatrader-mcp-server
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable mt5-mcp
sudo systemctl start mt5-mcp
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
5. Program: `uvx`
6. Arguments: `metatrader-mcp-server`

## FAQ

**Q: Do I need to restart the server when I restart MT5?**
A: Yes, restart the MCP server after restarting MT5.

**Q: Can I run multiple instances?**
A: Yes, but use different ports for each instance.

**Q: Does the server work with MT4?**
A: No, only MetaTrader 5 is supported.

**Q: Can I use this on a VPS?**
A: Yes, install UV and MT5 on the VPS, then start the server.

**Q: Is this safe?**
A: The server only accepts local connections. Never expose it to the internet.

**Q: What if MT5 crashes?**
A: Restart MT5, then restart the MCP server.

## Summary

1. Install UV: `irm https://astral.sh/uv/install.ps1 | iex` (Windows)
2. Install and login to MetaTrader 5
3. Start server: `bash scripts/start_mt5_server.sh`
4. Test connection: `bash scripts/test_mt5_connection.sh`
5. Run AutoTrader: `bash scripts/run.sh`

**Remember:** Keep the MCP server running in a separate terminal while AutoTrader is running!

## Getting Help

If you're still having issues:

1. Check MT5 is running and logged in
2. Check server terminal for error messages
3. Test connection: `curl http://localhost:8001/health`
4. Check AutoTrader logs: `bash scripts/logs.sh errors`
5. Review this guide again

---

For more information, see:
- [Startup Guide](docs/STARTUP_GUIDE.md)
- [MCP Integration Documentation](docs/MCP_INTEGRATION.md)
- [MetaTrader MCP Server GitHub](https://github.com/ariadng/metatrader-mcp-server)
