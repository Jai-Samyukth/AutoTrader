# Scripts Documentation

Utility scripts for AutoTrader development and operations.

## Installation & Setup

### `install.sh`
Install dependencies and setup environment.

```bash
bash scripts/install.sh
```

What it does:
- Checks for `uv` installation
- Syncs all dependencies
- Creates `.env` from template
- Creates logs directory

### `validate_env.sh`
Validate environment configuration.

```bash
bash scripts/validate_env.sh
```

What it checks:
- `.env` file exists
- Required API keys are set
- MT5 configuration is present
- Trading parameters are configured

## Running the Bot

### `start_mt5_server.sh` / `start_mt5_server.ps1`
Start the MetaTrader 5 MCP server (REQUIRED before running the bot).

```bash
# Bash (Git Bash, Linux, macOS)
bash scripts/start_mt5_server.sh

# PowerShell (Windows)
.\scripts\start_mt5_server.ps1
```

**IMPORTANT**: 
- You MUST start this server before running the trading bot
- Make sure MetaTrader 5 is running and logged in
- Server runs on `http://localhost:8001`
- Keep this terminal open while trading
- Press Ctrl+C to stop the server

Requirements:
- `uvx` must be installed (comes with `uv`)
- MetaTrader 5 must be installed and running
- MT5 must be logged into a trading account

### `run_once.sh`
Run a single analysis cycle (test mode).

```bash
bash scripts/run_once.sh
```

Use this to:
- Test configuration
- Verify API connections
- Debug issues
- See one complete cycle

### `run.sh`
Run AutoTrader in continuous mode.

```bash
bash scripts/run.sh
```

Features:
- Checks for `.env` file
- Warns if live trading is enabled
- Runs continuous analysis cycles
- Press Ctrl+C to stop

## Development

### `format.sh`
Format and auto-fix code.

```bash
bash scripts/format.sh
```

What it does:
- Runs Ruff formatter
- Auto-fixes linting issues
- Formats all Python files

### `lint.sh`
Lint code without fixing.

```bash
bash scripts/lint.sh
```

Use this to:
- Check code quality
- Find potential issues
- Verify before commit

### `test.sh`
Run all tests.

```bash
bash scripts/test.sh
```

Runs:
- All pytest tests
- Verbose output
- Short traceback format

### `check.sh`
Run all checks (format + lint + test).

```bash
bash scripts/check.sh
```

Complete validation:
1. Format code
2. Lint code
3. Run tests

Use before committing!

### `pre_commit.sh`
Pre-commit checks and requirements export.

```bash
bash scripts/pre_commit.sh
```

What it does:
- Exports requirements.txt
- Exports requirements.dev.txt
- Runs linter
- Runs tests

## Monitoring

### `logs.sh`
View and filter logs.

```bash
# Show last 50 lines
bash scripts/logs.sh

# Show decisions only
bash scripts/logs.sh decisions

# Show trade executions
bash scripts/logs.sh trades

# Show errors only
bash scripts/logs.sh errors

# Follow logs in real-time
bash scripts/logs.sh follow
```

Log filters:
- `decisions` - Trading decisions (EXECUTE/WATCH/SKIP)
- `trades` - Trade executions and orders
- `errors` - Error messages only
- `follow` - Real-time log streaming

## Maintenance

### `clean.sh`
Clean build artifacts and cache.

```bash
bash scripts/clean.sh
```

Removes:
- `__pycache__` directories
- `*.pyc` files
- `.pytest_cache`
- `.ruff_cache`
- Build directories

## Quick Reference

```bash
# First time setup
bash scripts/install.sh
bash scripts/validate_env.sh

# Start MT5 MCP server (REQUIRED - keep running in separate terminal)
bash scripts/start_mt5_server.sh        # Bash
.\scripts\start_mt5_server.ps1          # PowerShell

# Development workflow
bash scripts/format.sh      # Format code
bash scripts/test.sh        # Run tests
bash scripts/check.sh       # Run all checks

# Testing the bot
bash scripts/run_once.sh    # Single cycle

# Running the bot
bash scripts/run.sh         # Continuous mode

# Monitoring
bash scripts/logs.sh follow # Watch logs
bash scripts/logs.sh trades # Check trades

# Maintenance
bash scripts/clean.sh       # Clean cache
```

## Troubleshooting

### Script won't execute
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### uv not found
```bash
# Install uv (includes uvx)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or on Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```

### MT5 MCP server not connecting
```bash
# 1. Make sure MT5 is running and logged in
# 2. Start the MCP server in a separate terminal
bash scripts/start_mt5_server.sh

# 3. Check if server is running
curl http://localhost:8001/health

# 4. If port 8001 is in use, kill the process
# Windows: netstat -ano | findstr :8001
# Linux/Mac: lsof -i :8001
```

### .env not found
```bash
# Create from template
cp .env.example .env
# Edit with your API keys
```

### Tests failing
```bash
# Check environment
bash scripts/validate_env.sh

# Clean and reinstall
bash scripts/clean.sh
bash scripts/install.sh
```

## CI/CD Integration

These scripts are designed for CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Install
  run: bash scripts/install.sh

- name: Validate
  run: bash scripts/validate_env.sh

- name: Check
  run: bash scripts/check.sh
```

## Notes

- All scripts use `set -e` to exit on error
- Scripts are designed for bash shell
- Compatible with Windows Git Bash
- Use `uv run` for Python commands
- Logs are written to `logs/trader_ai.log`
