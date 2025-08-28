#!/bin/bash

APP_NAME="Drools API"
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
LOG_FILE="drools_api.log"
PID_FILE="drools_api.pid"
APP_COMMAND="uvicorn api_drools:app --host 0.0.0.0 --port 8503 --reload"
GIT_REPO_URL="https://github.com/Lakshya-serigor/Drools-api.git"
PROJECT_DIR="$(pwd)"

function activate_env() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "❌ Virtual environment '$VENV_DIR' not found."
        exit 1
    fi
    source "$VENV_DIR/bin/activate"
    echo "✅ Virtual environment activated."
}

function install_dependencies() {
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        echo "❌ requirements.txt not found."
        exit 1
    fi
    echo "📦 Checking/installing required Python packages..."
    pip install --quiet --upgrade pip
    pip install --quiet -r "$REQUIREMENTS_FILE"
}

function start_app() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "⚠️ $APP_NAME is already running (PID $(cat $PID_FILE))."
        exit 0
    fi
    echo "🚀 Starting $APP_NAME..."
    nohup $APP_COMMAND > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "✅ $APP_NAME started (PID $!)"
}

function stop_app() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "🛑 Stopping $APP_NAME (PID $PID)..."
            kill "$PID" && rm -f "$PID_FILE"
            echo "✅ $APP_NAME stopped."
        else
            echo "⚠️ PID file exists but process is not running. Cleaning up."
            rm -f "$PID_FILE"
        fi
    else
        echo "⚠️ $APP_NAME is not running or PID file not found."
    fi
}

function status_app() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "✅ $APP_NAME is running (PID $PID)."
        else
            echo "⚠️ PID file exists but process is not running."
        fi
    else
        echo "❌ $APP_NAME is not running."
    fi
}

function update_code() {
    echo "🔄 Updating source code from GitHub..."
    if [ -d .git ]; then
        git pull origin main || git pull origin master
    else
        echo "⚠️ This directory is not a Git repository."
        echo "Cloning into new directory: ./drools_project_clone"
        git clone "$GIT_REPO_URL" drools_project_clone
    fi
}

case "$1" in
    start)
        activate_env
        install_dependencies
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        stop_app
        sleep 1
        activate_env
        install_dependencies
        start_app
        ;;
    status)
        status_app
        ;;
    update)
        update_code
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|update}"
        exit 1
        ;;
esac
