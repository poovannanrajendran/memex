#!/usr/bin/env bash
set -euo pipefail

# Configuration
PROJECT_DIR="/home/labadmin/memex"
VENV_DIR="$PROJECT_DIR/.venv"
SERVICE_NAME="memex-runner"
USER_NAME="labadmin"

echo "Deploying systemd service: $SERVICE_NAME..."

# Create service file
sudo tee /etc/systemd/system/${SERVICE_NAME}.service >/dev/null <<EOF
[Unit]
Description=Memex Automation Runner API (FastAPI)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${USER_NAME}
Group=${USER_NAME}
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=${VENV_DIR}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
EnvironmentFile=${PROJECT_DIR}/.env
ExecStart=${VENV_DIR}/bin/python scripts/runner_api.py
Restart=always
RestartSec=5
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl restart ${SERVICE_NAME}

echo "✅ Service deployed and restarted."
sudo systemctl status ${SERVICE_NAME} --no-pager -l
