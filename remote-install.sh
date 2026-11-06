#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="/opt/kspconnect"
ARCHIVE="/tmp/kspconnect-deploy.tar.gz"
ENV_FILE="/tmp/kspconnect.env"

echo "=========================================="
echo "🏥 Installing KSP Connect on 192.168.2.202"
echo "=========================================="

# Check root / sudo
if [[ $EUID -ne 0 ]]; then
    SUDO="sudo"
else
    SUDO=""
fi

# 1. Prepare directory
echo "[1/5] Setting up target directory $APP_DIR..."
$SUDO mkdir -p "$APP_DIR"
$SUDO tar -xzf "$ARCHIVE" -C "$APP_DIR"
$SUDO chown -R "$USER":"$USER" "$APP_DIR"

# 2. Setup Python Virtual Environment
echo "[2/5] Creating Python virtual environment..."
cd "$APP_DIR"
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "ERROR: Python 3 is not installed on this server!" >&2
    exit 1
fi

$PYTHON_BIN -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 3. Environment Config
echo "[3/5] Configuring environment variables..."
if [[ -f "$ENV_FILE" ]]; then
    cp "$ENV_FILE" "$APP_DIR/.env"
elif [[ ! -f "$APP_DIR/.env" ]]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
fi

# 4. Setup Systemd Service
echo "[4/5] Registering systemd service (kspconnect.service)..."
cat <<SERVICE | $SUDO tee /etc/systemd/system/kspconnect.service > /dev/null
[Unit]
Description=KSP Hospital Intelligence Gateway & Skill API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/run_api.py
Restart=always
RestartSec=5
Environment=REST_HOST=0.0.0.0
Environment=REST_PORT=8000

[Install]
WantedBy=multi-user.target
SERVICE

$SUDO systemctl daemon-reload
$SUDO systemctl enable kspconnect.service
$SUDO systemctl restart kspconnect.service

# 5. Verification
echo "[5/5] Verifying API status..."
sleep 3
if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo "=========================================="
    echo "🎉 SUCCESS: KSP Connect is running on 192.168.2.202:8000"
    echo "👉 Test URL: http://192.168.2.202:8000/api/v1/overview"
    echo "=========================================="
else
    echo "WARNING: Service started, but health check did not respond yet. Check: sudo systemctl status kspconnect"
fi

# Cleanup
rm -f "$ARCHIVE" "$ENV_FILE" /tmp/remote-install.sh || true
