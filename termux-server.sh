#!/data/data/com.termux/files/usr/bin/bash
# ========================================================
#   MYDAILY - ANDROID TERMUX SERVER CONTROLLER
#   Runs MyDaily as a 24/7 productivity server on Android
# ========================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

PID_FILE_BACKEND="$DIR/.termux_backend.pid"
PID_FILE_FRONTEND="$DIR/.termux_frontend.pid"
LOG_BACKEND="$DIR/server-backend.log"
LOG_FRONTEND="$DIR/server-frontend.log"

# Detect Python
if [ -f "$DIR/venv/bin/python" ]; then
    PYTHON="$DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
else
    PYTHON="python"
fi

# Detect Wi-Fi IP address on Android
get_phone_ip() {
    local ip=""
    ip=$(ip -4 addr show wlan0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1)
    if [ -z "$ip" ]; then
        ip=$(ifconfig 2>/dev/null | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)
    fi
    if [ -z "$ip" ]; then
        ip="<your-android-ip>"
    fi
    echo "$ip"
}

# Start MariaDB service if not active
start_database() {
    if ! nc -z 127.0.0.1 3306 >/dev/null 2>&1; then
        echo "[1/3] Starting MariaDB server..."
        mysqld_safe -u root >/dev/null 2>&1 &
        local count=0
        while ! nc -z 127.0.0.1 3306 >/dev/null 2>&1; do
            sleep 1
            count=$((count + 1))
            if [ $count -ge 10 ]; then
                echo "WARNING: MariaDB took longer than expected to start."
                break
            fi
        done
    else
        echo "[1/3] MariaDB server is active."
    fi
}

# Start server processes
start_server() {
    echo "========================================================"
    echo "       STARTING MYDAILY SERVER ON ANDROID (TERMUX)      "
    echo "========================================================"

    # Acquire wake-lock so Android does not sleep or kill Termux in background
    if command -v termux-wake-lock >/dev/null 2>&1; then
        termux-wake-lock
        echo ">> Termux wake-lock acquired (server stays alive in background)"
    fi

    # Check if already running
    if [ -f "$PID_FILE_FRONTEND" ] && kill -0 "$(cat "$PID_FILE_FRONTEND")" 2>/dev/null; then
        echo "MyDaily server is already running!"
        show_info
        return 0
    fi

    start_database

    # Set server environment variables
    export DJANGO_DEBUG=False
    export DJANGO_ALLOWED_HOSTS="*"
    export CORS_ALLOW_ALL=True
    export DB_ENGINE="mysql"
    export DB_NAME="mydailyapp"
    export DB_USER="root"
    export DB_PASSWORD="1012"
    export DB_HOST="127.0.0.1"
    export DB_PORT="3306"
    export NUXT_PUBLIC_API_BASE="/api"
    export HOST="0.0.0.0"
    export NITRO_HOST="0.0.0.0"
    export PORT="3000"

    # Start Backend
    echo "[2/3] Starting Django API server on 0.0.0.0:8000..."
    cd "$DIR/backend"
    $PYTHON manage.py collectstatic --noinput >/dev/null 2>&1 || true
    $PYTHON manage.py runserver 0.0.0.0:8000 > "$LOG_BACKEND" 2>&1 &
    echo $! > "$PID_FILE_BACKEND"
    cd "$DIR"

    sleep 2

    # Start Frontend
    echo "[3/3] Starting Nuxt Web server on 0.0.0.0:3000..."
    cd "$DIR/frontend"
    if [ -f ".output/server/index.mjs" ]; then
        node .output/server/index.mjs > "$LOG_FRONTEND" 2>&1 &
    else
        npm run dev > "$LOG_FRONTEND" 2>&1 &
    fi
    echo $! > "$PID_FILE_FRONTEND"
    cd "$DIR"

    sleep 2
    show_info
}

# Display access URLs
show_info() {
    PHONE_IP=$(get_phone_ip)
    echo ""
    echo "========================================================"
    echo "         MYDAILY SERVER IS RUNNING ON ANDROID!          "
    echo "========================================================"
    echo ""
    echo "  1. On THIS Android phone:"
    echo "     -> Open: http://localhost:3000"
    echo ""
    echo "  2. From LAPTOP / PC / OTHER DEVICES on your Wi-Fi:"
    echo "     -> Open: http://${PHONE_IP}:3000"
    echo ""
    echo "  Default Demo Login:"
    echo "     Username: demo"
    echo "     Password: password123"
    echo ""
    echo "  Server Commands:"
    echo "     ./termux-server.sh status   (check server status)"
    echo "     ./termux-server.sh logs     (view live logs)"
    echo "     ./termux-server.sh stop     (stop server)"
    echo "========================================================"
}

# Stop server processes
stop_server() {
    echo "Stopping MyDaily server..."

    if [ -f "$PID_FILE_FRONTEND" ]; then
        kill "$(cat "$PID_FILE_FRONTEND")" 2>/dev/null || true
        rm -f "$PID_FILE_FRONTEND"
    fi

    if [ -f "$PID_FILE_BACKEND" ]; then
        kill "$(cat "$PID_FILE_BACKEND")" 2>/dev/null || true
        rm -f "$PID_FILE_BACKEND"
    fi

    # Release wake-lock
    if command -v termux-wake-unlock >/dev/null 2>&1; then
        termux-wake-unlock
        echo ">> Termux wake-lock released"
    fi

    echo "MyDaily server has been stopped."
}

# Status
status_server() {
    local running=0
    if [ -f "$PID_FILE_FRONTEND" ] && kill -0 "$(cat "$PID_FILE_FRONTEND")" 2>/dev/null; then
        echo "Frontend: RUNNING (PID $(cat "$PID_FILE_FRONTEND")) on port 3000"
        running=1
    else
        echo "Frontend: STOPPED"
    fi

    if [ -f "$PID_FILE_BACKEND" ] && kill -0 "$(cat "$PID_FILE_BACKEND")" 2>/dev/null; then
        echo "Backend:  RUNNING (PID $(cat "$PID_FILE_BACKEND")) on port 8000"
        running=1
    else
        echo "Backend:  STOPPED"
    fi

    if nc -z 127.0.0.1 3306 >/dev/null 2>&1; then
        echo "Database: RUNNING (MariaDB on port 3306)"
    else
        echo "Database: STOPPED"
    fi

    if [ $running -eq 1 ]; then
        PHONE_IP=$(get_phone_ip)
        echo ""
        echo "Accessible on your Wi-Fi network at: http://${PHONE_IP}:3000"
    fi
}

# Show live logs
logs_server() {
    echo "Showing recent logs (Press Ctrl+C to exit)..."
    tail -f "$LOG_BACKEND" "$LOG_FRONTEND"
}

# Command dispatch
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 2
        start_server
        ;;
    status)
        status_server
        ;;
    logs)
        logs_server
        ;;
    *)
        # Default behavior: run in foreground and shut down cleanly on Ctrl+C
        start_server
        echo ""
        echo "Running in foreground. Press Ctrl+C anytime to stop."
        trap "echo ''; stop_server; exit 0" SIGINT SIGTERM
        while true; do
            sleep 1
        done
        ;;
esac

