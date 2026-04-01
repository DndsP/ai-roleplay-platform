$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root ".venv\\Scripts\\python.exe"
$uvicorn = Join-Path $root ".venv\\Scripts\\uvicorn.exe"
$streamlit = Join-Path $root ".venv\\Scripts\\streamlit.exe"

$envFile = Join-Path $root ".env"

if (-not (Test-Path $envFile)) {
    Write-Error "Missing .env file. Create it from .env.example and add your real API keys first."
    exit 1
}

if (-not (Test-Path $python)) {
    Write-Host "Creating virtual environment..."
    python -m venv (Join-Path $root ".venv")
}

if (-not (Test-Path $python)) {
    Write-Error "Failed to create the virtual environment at .venv"
    exit 1
}

Write-Host "Installing backend and frontend dependencies..."
& $python -m pip install --upgrade pip
& $python -m pip install -r (Join-Path $root "requirements.txt")

Write-Host "Installing LiveKit agent dependencies..."
& $python -m pip install -r (Join-Path $root "livekit_agent\\requirements-livekit.txt")

if (-not (Test-Path $uvicorn) -or -not (Test-Path $streamlit)) {
    Write-Error "Expected uvicorn and streamlit in the virtual environment, but they were not found after install."
    exit 1
}

Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", "cd `"$root`"; & `"$uvicorn`" backend.app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", "cd `"$root`"; & `"$python`" livekit_agent/agent.py dev"
Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", "cd `"$root`"; & `"$streamlit`" run frontend/app.py"

Write-Host "Started backend, LiveKit agent, and Streamlit frontend in separate PowerShell windows."
