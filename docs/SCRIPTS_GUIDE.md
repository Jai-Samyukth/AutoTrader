# Complete Scripts Guide

## Overview

AutoTrader includes comprehensive bash scripts for all development and operational tasks. All scripts are located in the `scripts/` directory and are designed to work on Windows (Git Bash), Linux, and macOS.

## Quick Reference Card

```bash
# 🚀 Getting Started
bash scripts/dev.sh setup          # First-time setup
bash scripts/validate_env.sh       # Check configuration

# 🧪 Testing
bash scripts/dev.sh test           # Single test cycle
bash scripts/test.sh               # Run unit tests

# 🤖 Running
bash scripts/dev.sh run            # Continuous mode
bash scripts/run_once.sh           # Single cycle

# 📊 Monitoring
bash scripts/dev.sh logs           # Follow logs
bash scripts/logs.sh decisions     # View decisions
bash scripts/logs.sh trades        # View trades

# 🔧 Development
bash scripts/format.sh             # Format code
bash scripts/lint.sh               # Lint code
bash scripts/check.sh              # All checks

# 📈 Status
bash scripts/dev.sh status         # Show config & activity

# 🧹 Maintenance
bash scripts/clean.sh              # Clean cache
bash scripts/pre_commit.sh         # Pre-commit checks
```

## Detailed Guide

### 1. Initial Setup

#### Step 1: Install Dependencies
```bash
bash scripts/install.sh
```

What happens:
- Checks for `uv` installation
- Syncs all Python dependencies
- Creates `.env` from template
- Creates `logs/` directory
- Shows next steps

#### Step 2: Configure Environment
```bash
# Edit .env with your settings
nano .env  # or your preferred editor

# Required settings:
# - ANTHROPIC_API_KEY or OPENAI_API_KEY
# - MT5_BASE_URL
# - SYMBOLS
```

#### Step 3: Validate Configuration
```bash
bash scripts/validate_env.sh
```

Checks:
- ✅ .env file exists
- ✅ API keys are set
- ✅ MT5 configuration
- ✅ Trading parameters
- ✅ Risk management settings

### 2. Development Workflow

#### Format Code
```bash
bash scripts/format.sh
```

Runs:
1. Ruff formatter (auto-format)
2. Ruff linter with auto-fix

#### Lint Code
```bash
bash scripts/lint.sh
```

Checks code quality without modifying files.

#### Run Tests
```bash
bash scripts/test.sh
```

Runs all pytest tests with verbose output.

#### Run All Checks
```bash
bash scripts/check.sh
```

Complete validation:
1. Format code
2. Lint code
3. Run tests

Use this before committing!

### 3. Testing the Bot

#### Single Cycle Test
```bash
bash scripts/run_once.sh
```

Perfect for:
- Testing configuration
- Verifying API connections
- Debugging issues
- Seeing one complete analysis cycle

Output shows:
- Data fetching
- SMC analysis
- LLM decision
- Risk validation
- Execution (if applicable)

#### Using Dev Helper
```bash
bash scripts/dev.sh test
```

Same as `run_once.sh` but with prettier output.

### 4. Running the Bot

#### Continuous Mode
```bash
bash scripts/run.sh
```

Features:
- Checks for `.env` file
- Warns if live trading enabled (5 second countdown)
- Runs analysis cycles every 15 minutes (configurable)
- Press Ctrl+C to stop gracefully

#### Using Dev Helper
```bash
bash scripts/dev.sh run
```

Same as `run.sh` with additional status info.

### 5. Monitoring

#### Follow Logs in Real-Time
```bash
bash scripts/logs.sh follow
```

Shows live log stream. Press Ctrl+C to stop.

#### View Recent Logs
```bash
bash scripts/logs.sh
```

Shows last 50 lines.

#### Filter by Type
```bash
# Trading decisions only
bash scripts/logs.sh decisions

# Trade executions only
bash scripts/logs.sh trades

# Errors only
bash scripts/logs.sh errors
```

#### Check Status
```bash
bash scripts/dev.sh status
```

Shows:
- Current configuration
- Paper trading mode
- Risk settings
- Last 5 decisions

### 6. Pre-Commit Workflow

#### Before Committing
```bash
bash scripts/pre_commit.sh
```

Runs:
1. Export requirements.txt
2. Export requirements.dev.txt
3. Lint code
4. Run tests

All must pass before committing!

#### Quick Check
```bash
bash scripts/check.sh
```

Faster alternative (no requirements export).

### 7. Maintenance

#### Clean Cache
```bash
bash scripts/clean.sh
```

Removes:
- `__pycache__` directories
- `*.pyc` files
- `.pytest_cache`
- `.ruff_cache`
- Build artifacts

Run this if you encounter import issues.

### 8. Development Helper

The `dev.sh` script is a convenience wrapper:

```bash
# Show help
bash scripts/dev.sh help

# Setup (install + validate)
bash scripts/dev.sh setup

# Test (single cycle)
bash scripts/dev.sh test

# Run (continuous)
bash scripts/dev.sh run

# Check (format + lint + test)
bash scripts/dev.sh check

# Logs (follow mode)
bash scripts/dev.sh logs

# Status (show config)
bash scripts/dev.sh status

# Clean (remove cache)
bash scripts/dev.sh clean
```

## Common Workflows

### First Time Setup
```bash
# 1. Install
bash scripts/install.sh

# 2. Configure
nano .env

# 3. Validate
bash scripts/validate_env.sh

# 4. Test
bash scripts/run_once.sh

# 5. Run
bash scripts/run.sh
```

### Daily Development
```bash
# 1. Pull latest code
git pull

# 2. Sync dependencies
uv sync

# 3. Make changes
# ... edit code ...

# 4. Format and check
bash scripts/check.sh

# 5. Test
bash scripts/run_once.sh

# 6. Commit
bash scripts/pre_commit.sh
git add .
git commit -m "Your message"
```

### Debugging Issues
```bash
# 1. Check configuration
bash scripts/validate_env.sh

# 2. Clean cache
bash scripts/clean.sh

# 3. Reinstall
bash scripts/install.sh

# 4. Run test cycle
bash scripts/run_once.sh

# 5. Check logs
bash scripts/logs.sh errors
```

### Monitoring Production
```bash
# Terminal 1: Run bot
bash scripts/run.sh

# Terminal 2: Follow logs
bash scripts/logs.sh follow

# Terminal 3: Monitor decisions
watch -n 60 'bash scripts/logs.sh decisions | tail -n 10'
```

## Troubleshooting

### Scripts Won't Execute

**Problem**: Permission denied

**Solution**:
```bash
chmod +x scripts/*.sh
```

### uv Not Found

**Problem**: `uv: command not found`

**Solution**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or on Windows with PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### .env Not Found

**Problem**: `.env file not found`

**Solution**:
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

### Tests Failing

**Problem**: Tests fail after changes

**Solution**:
```bash
# 1. Clean cache
bash scripts/clean.sh

# 2. Reinstall
bash scripts/install.sh

# 3. Validate config
bash scripts/validate_env.sh

# 4. Run tests
bash scripts/test.sh
```

### Logs Not Showing

**Problem**: No logs in `logs/trader_ai.log`

**Solution**:
```bash
# 1. Check if bot has run
bash scripts/run_once.sh

# 2. Check log configuration in .env
# LOG_TO_FILE=true
# LOG_FILE_PATH=./logs/trader_ai.log

# 3. Create logs directory
mkdir -p logs
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: bash scripts/install.sh
      
      - name: Run checks
        run: bash scripts/check.sh
```

### GitLab CI Example

```yaml
test:
  script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - bash scripts/install.sh
    - bash scripts/check.sh
```

## Best Practices

1. **Always validate before running**
   ```bash
   bash scripts/validate_env.sh
   ```

2. **Use dev helper for common tasks**
   ```bash
   bash scripts/dev.sh [command]
   ```

3. **Check status regularly**
   ```bash
   bash scripts/dev.sh status
   ```

4. **Run checks before committing**
   ```bash
   bash scripts/check.sh
   ```

5. **Monitor logs in production**
   ```bash
   bash scripts/logs.sh follow
   ```

6. **Clean cache periodically**
   ```bash
   bash scripts/clean.sh
   ```

## Script Locations

All scripts are in `scripts/`:

```
scripts/
├── README.md           # Script documentation
├── dev.sh             # Development helper
├── install.sh         # Install dependencies
├── validate_env.sh    # Validate configuration
├── run.sh             # Run continuous mode
├── run_once.sh        # Run single cycle
├── logs.sh            # View logs
├── format.sh          # Format code
├── lint.sh            # Lint code
├── test.sh            # Run tests
├── check.sh           # Run all checks
├── clean.sh           # Clean cache
└── pre_commit.sh      # Pre-commit checks
```

## Getting Help

```bash
# Show dev helper commands
bash scripts/dev.sh help

# Show logs usage
bash scripts/logs.sh

# Check script documentation
cat scripts/README.md
```

## Summary

The scripts provide a complete development and operational workflow:

- ✅ Easy setup and installation
- ✅ Configuration validation
- ✅ Code quality checks
- ✅ Testing and debugging
- ✅ Running and monitoring
- ✅ Log viewing and filtering
- ✅ Maintenance and cleanup
- ✅ CI/CD integration

Use `bash scripts/dev.sh` as your main entry point for all common tasks!
