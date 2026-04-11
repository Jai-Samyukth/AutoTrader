# Start MetaTrader 5 MCP Server (PowerShell version)
# This script starts the MT5 MCP server on port 8001

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting MetaTrader 5 MCP Server" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if uvx is installed
$uvxExists = Get-Command uvx -ErrorAction SilentlyContinue
if (-not $uvxExists) {
    Write-Host "ERROR: uvx is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install uv first:" -ForegroundColor Yellow
    Write-Host "  PowerShell: irm https://astral.sh/uv/install.ps1 | iex" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or install via pip: pip install uv" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "ERROR: .env file not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create .env file with your MT5 credentials:" -ForegroundColor Yellow
    Write-Host "  cp .env.example .env" -ForegroundColor Yellow
    Write-Host "  notepad .env" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Required variables:" -ForegroundColor Yellow
    Write-Host "  MT5_LOGIN=your_login_id" -ForegroundColor Yellow
    Write-Host "  MT5_PASSWORD=your_password" -ForegroundColor Yellow
    Write-Host "  MT5_SERVER=your_broker_server" -ForegroundColor Yellow
    exit 1
}

# Load environment variables
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
    }
}

# Check required variables
if (-not $env:MT5_LOGIN -or -not $env:MT5_PASSWORD -or -not $env:MT5_SERVER) {
    Write-Host "ERROR: Missing MT5 credentials in .env file" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please add these to your .env file:" -ForegroundColor Yellow
    Write-Host "  MT5_LOGIN=your_login_id" -ForegroundColor Yellow
    Write-Host "  MT5_PASSWORD=your_password" -ForegroundColor Yellow
    Write-Host "  MT5_SERVER=your_broker_server" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Example:" -ForegroundColor Yellow
    Write-Host "  MT5_LOGIN=12345678" -ForegroundColor Yellow
    Write-Host "  MT5_PASSWORD=YourPassword123" -ForegroundColor Yellow
    Write-Host "  MT5_SERVER=MetaQuotes-Demo" -ForegroundColor Yellow
    exit 1
}

Write-Host "MT5 Login: $env:MT5_LOGIN" -ForegroundColor Green
Write-Host "MT5 Server: $env:MT5_SERVER" -ForegroundColor Green
Write-Host "Starting server on http://localhost:8001..." -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Start the MT5 MCP server
# The server will connect to MT5 and provide HTTP API on port 8001
uvx metatrader-mcp-server `
    --login $env:MT5_LOGIN `
    --password $env:MT5_PASSWORD `
    --server $env:MT5_SERVER `
    --transport sse `
    --host 127.0.0.1 `
    --port 8001
