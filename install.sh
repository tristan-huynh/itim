#!/usr/bin/env bash
set -euo pipefail

PYTHON=${PYTHON:-python3}
VENV_DIR=".venv"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="itim"
SERVICE_USER="${SUDO_USER:-$(whoami)}"
GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
GUNICORN_BIND=${GUNICORN_BIND:-"127.0.0.1:8000"}

check_python() {
    if ! command -v "$PYTHON" &>/dev/null; then
        echo "Error: Python 3 not found. Install it or set PYTHON=<path>." >&2
        exit 1
    fi
    local ver
    ver=$("$PYTHON" -c "import sys; print(sys.version_info.major)")
    if [[ "$ver" -lt 3 ]]; then
        echo "Error: Python 3 required (found $("$PYTHON" --version))." >&2
        exit 1
    fi
}

setup_env() {
    if [[ ! -f ".env" ]]; then
        cp .env.example .env
        echo "Created .env from .env.example — fill in your OIDC credentials before running."
    else
        echo ".env already exists, skipping."
    fi
}

setup_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        echo "Creating virtual environment..."
        "$PYTHON" -m venv "$VENV_DIR"
    else
        echo "Virtual environment already exists, skipping."
    fi
}

install_deps() {
    echo "Installing dependencies..."
    "$VENV_DIR/bin/pip" install --upgrade pip --quiet
    "$VENV_DIR/bin/pip" install -r requirements.txt --quiet
    echo "Dependencies installed."
}

setup_db() {
    echo "Applying database migrations..."
    FLASK_APP=app "$VENV_DIR/bin/flask" db upgrade
    echo "Database ready."
}

install_systemd_service() {
    if [[ ! -d /etc/systemd/system ]]; then
        echo "Skipping systemd setup (not a systemd system)."
        return
    fi

    if [[ "$EUID" -ne 0 ]]; then
        echo "Skipping systemd service install (run with sudo to enable it)."
        return
    fi

    local service_file="/etc/systemd/system/${SERVICE_NAME}.service"

    echo "Installing systemd service to $service_file..."
    cat > "$service_file" <<EOF
[Unit]
Description=ITIM Inventory Management
After=network.target

[Service]
User=${SERVICE_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/${VENV_DIR}/bin/gunicorn \\
    --workers ${GUNICORN_WORKERS} \\
    --bind ${GUNICORN_BIND} \\
    --access-logfile - \\
    --error-logfile - \\
    app:app
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    systemctl restart "$SERVICE_NAME"
    echo "Service started. Check status with: systemctl status $SERVICE_NAME"
}

main() {
    echo "=== ITIM Install ==="

    check_python
    setup_env
    setup_venv
    install_deps
    setup_db
    install_systemd_service

    echo ""
    if [[ "$EUID" -eq 0 ]]; then
        echo "Setup complete. App is running via systemd on $GUNICORN_BIND"
        echo "  Logs:    journalctl -u $SERVICE_NAME -f"
        echo "  Restart: systemctl restart $SERVICE_NAME"
    else
        echo "Setup complete. To start manually:"
        echo "  $VENV_DIR/bin/gunicorn --workers $GUNICORN_WORKERS --bind $GUNICORN_BIND app:app"
        echo ""
        echo "To install as a systemd service, re-run with sudo:"
        echo "  sudo bash install.sh"
    fi
}

main "$@"
