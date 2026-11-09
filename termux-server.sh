
#!/data/data/com.termux/files/usr/bin/bash

# ========================================================
#       MYDAILY - ANDROID TERMUX SERVER CONTROLLER
# ========================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR" || exit 1

PID_FILE_BACKEND="$DIR/.termux_backend.pid"
PID_FILE_FRONTEND="$DIR/.termux_frontend.pid"

LOG_BACKEND="$DIR/server-backend.log"
LOG_FRONTEND="$DIR/server-frontend.log"

BACKEND_DIR="$DIR/backend"
FRONTEND_DIR="$DIR/frontend"

BACKEND_PORT=8000
FRONTEND_PORT=3000
DATABASE_PORT=3306

# Detect Python
if [ -x "$DIR/venv/bin/python" ]; then
    PYTHON="$DIR/venv/bin/python"
elif [ -x "$BACKEND_DIR/venv/bin/python" ]; then
    PYTHON="$BACKEND_DIR/venv/bin/python"
else
    PYTHON="$(command -v python3 || command -v python)"
fi

# Detect Android Wi-Fi IP
get_phone_ip() {
    local ip=""

    ip=$(ip -4 addr show wlan0 2>/dev/null |
        grep -oP '(?<=inet\s)\d+(\.\d+){3}' |
        head -n 1)

    if [ -z "$ip" ]; then
        ip=$(ifconfig 2>/dev/null |
            grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' |
            grep -Eo '([0-9]*\.){3}[0-9]*' |
            grep -v '127.0.0.1' |
            head -n 1)
    fi

    echo "${ip:-<your-android-ip>}"
}

# Check whether a port is active
port_is_active() {
    nc -z 127.0.0.1 "$1" >/dev/null 2>&1
}

# Acquire process wake lock
acquire_wake_lock() {
    if command -v termux-wake-lock >/dev/null 2>&1; then
        termux-wake-lock
        echo "Wake lock acquired."
    fi
}

# Start MariaDB
start_database() {
    if port_is_active "$DATABASE_PORT"; then
        echo "[1/3] MariaDB is already running."
        return 0
    fi

    if ! command -v mariadbd-safe >/dev/null 2>&1; then
        echo "ERROR: mariadbd-safe not found."
        return 1
    fi

    echo "[1/3] Starting MariaDB..."

    mariadbd-safe >/dev/null 2>&1 &

    local count=0

    while ! port_is_active "$DATABASE_PORT"; do
        sleep 1
        count=$((count + 1))

        if [ "$count" -ge 30 ]; then
            echo "ERROR: MariaDB failed to start."
            echo "Check MariaDB configuration and data directory."
            return 1
        fi
    done

    echo "MariaDB started successfully."
    return 0
}

# Start Django backend
start_backend() {
    if port_is_active "$BACKEND_PORT"; then
        echo "[2/3] Django backend is already running."
        return 0
    fi

    echo "[2/3] Starting Django backend..."

    if [ ! -f "$BACKEND_DIR/manage.py" ]; then
        echo "ERROR: backend/manage.py not found."
        return 1
    fi

    cd "$BACKEND_DIR" || return 1

    "$PYTHON" manage.py check >> "$LOG_BACKEND" 2>&1

    if [ $? -ne 0 ]; then
        echo "ERROR: Django check failed. See $LOG_BACKEND"
        cd "$DIR"
        return 1
    fi

    "$PYTHON" manage.py runserver 0.0.0.0:"$BACKEND_PORT" \
        >> "$LOG_BACKEND" 2>&1 &

    echo $! > "$PID_FILE_BACKEND"

    cd "$DIR" || return 1

    sleep 2

    if port_is_active "$BACKEND_PORT"; then
        echo "Django backend started."
        return 0
    fi

    echo "ERROR: Django backend failed to start."
    return 1
}

# Start Nuxt frontend
start_frontend() {
    if port_is_active "$FRONTEND_PORT"; then
        echo "[3/3] Nuxt frontend is already running."
        return 0
    fi

    echo "[3/3] Starting Nuxt frontend..."

    if [ ! -d "$FRONTEND_DIR" ]; then
        echo "ERROR: frontend directory not found."
        return 1
    fi

    cd "$FRONTEND_DIR" || return 1

    export HOST="0.0.0.0"
    export NITRO_HOST="0.0.0.0"
    export PORT="$FRONTEND_PORT"
    export NITRO_PORT="$FRONTEND_PORT"

    if [ -f ".output/server/index.mjs" ]; then
        node .output/server/index.mjs \
            >> "$LOG_FRONTEND" 2>&1 &
    else
        npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" \
            >> "$LOG_FRONTEND" 2>&1 &
    fi

    echo $! > "$PID_FILE_FRONTEND"

    cd "$DIR" || return 1

    sleep 3

    if port_is_active "$FRONTEND_PORT"; then
        echo "Nuxt frontend started."
        return 0
    fi

    echo "ERROR: Nuxt frontend failed to start."
    return 1
}

# Display server information
show_info() {
    local phone_ip
    phone_ip="$(get_phone_ip)"

    echo ""
    echo "========================================================"
    echo "              MYDAILY SERVER STATUS                    "
    echo "========================================================"

    echo ""
    echo "Android phone:"
    echo "http://localhost:$FRONTEND_PORT"

    echo ""
    echo "Other devices on the same Wi-Fi:"
    echo "http://$phone_ip:$FRONTEND_PORT"

    echo ""
    echo "Backend API:"
    echo "http://$phone_ip:$BACKEND_PORT"

    echo ""
    echo "Server commands:"
    echo "./termux-server.sh start"
    echo "./termux-server.sh stop"
    echo "./termux-server.sh restart"
    echo "./termux-server.sh status"
    echo "./termux-server.sh logs"

    echo ""
    echo "========================================================"
}

# Start all services
start_server() {
    echo "========================================================"
    echo "          STARTING MYDAILY ON TERMUX                    "
    echo "========================================================"

    acquire_wake_lock

    if ! start_database; then
        echo "Startup aborted: MariaDB is unavailable."
        return 1
    fi

    if ! start_backend; then
        echo "WARNING: Backend did not start successfully."
    fi

    if ! start_frontend; then
        echo "WARNING: Frontend did not start successfully."
    fi

    show_info
}

# Stop a process using its PID file
stop_process() {
    local pid_file="$1"
    local service_name="$2"

    if [ -f "$pid_file" ]; then
        local pid
        pid="$(cat "$pid_file")"

        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $service_name..."
            kill "$pid" 2>/dev/null || true

            local count=0
            while kill -0 "$pid" 2>/dev/null && [ "$count" -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done

            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi

        rm -f "$pid_file"
    else
        echo "$service_name PID file not found."
    fi
}

# Stop application services
stop_server() {
    echo "Stopping MyDaily application..."

    stop_process "$PID_FILE_FRONTEND" "Nuxt frontend"
    stop_process "$PID_FILE_BACKEND" "Django backend"

    if command -v termux-wake-unlock >/dev/null 2>&1; then
        termux-wake-unlock
    fi

    echo "Application services stopped."
    echo "MariaDB is intentionally left running."
}

# Show status

status_server() {
    echo "========================================"
    echo "             MYDAILY STATUS"
    echo "========================================"

    if port_is_active "$FRONTEND_PORT"; then
        echo "Frontend: RUNNING (port $FRONTEND_PORT)"
    else
        echo "Frontend: STOPPED"
    fi

    if port_is_active "$BACKEND_PORT"; then
        echo "Backend: RUNNING (port $BACKEND_PORT)"
    else
        echo "Backend: STOPPED"
    fi

    if port_is_active "$DATABASE_PORT"; then
        echo "Database: RUNNING (MariaDB)"
    else
        echo "Database: STOPPED"
    fi

    if port_is_active "$FRONTEND_PORT"; then
        echo ""
        echo "Wi-Fi URL: http://$(get_phone_ip):$FRONTEND_PORT"
    fi

    echo "========================================"
}


# Display live logs
logs_server() {
    touch "$LOG_BACKEND" "$LOG_FRONTEND"

    echo "Showing MyDaily logs. Press CTRL+C to exit."

    tail -n 40 -f "$LOG_BACKEND" "$LOG_FRONTEND"
}

# Command handler
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
        echo "Usage:"
        echo "./termux-server.sh start"
        echo "./termux-server.sh stop"
        echo "./termux-server.sh restart"
        echo "./termux-server.sh status"
        echo "./termux-server.sh logs"
        ;;
esac
