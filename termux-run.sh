#!/data/data/com.termux/files/usr/bin/bash
# ========================================================
#   MYDAILY - TERMUX RUNNER (ANDROID)
# ========================================================

# Resolve application directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "========================================================"
echo "          MYDAILY - STARTING IN TERMUX                  "
echo "========================================================"

# Locate Python
if [ -f "$DIR/venv/bin/python" ]; then
    PYTHON="$DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
else
    echo "ERROR: Python not found. Run ./termux-setup.sh first."
    exit 1
fi

# Locate Node
if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: Node.js not found. Run ./termux-setup.sh first."
    exit 1
fi

# Check / Start MariaDB
echo "[1/3] Checking MySQL / MariaDB service..."
if ! nc -z 127.0.0.1 3306 >/dev/null 2>&1; then
    echo "Starting MariaDB in background..."
    mysqld_safe -u root >/dev/null 2>&1 &
    sleep 3
fi

# Export Environment Variables
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

# Start Django Backend
echo "[2/3] Starting Django backend on 0.0.0.0:8000..."
cd "$DIR/backend"
$PYTHON manage.py runserver 0.0.0.0:8000 > "$DIR/termux-backend.log" 2>&1 &
BACKEND_PID=$!
cd "$DIR"

# Wait for backend port
sleep 2

# Start Nuxt Frontend
echo "[3/3] Starting Nuxt frontend on 0.0.0.0:3000..."
cd "$DIR/frontend"
if [ -f ".output/server/index.mjs" ]; then
    node .output/server/index.mjs > "$DIR/termux-frontend.log" 2>&1 &
    FRONTEND_PID=$!
else
    npm run dev > "$DIR/termux-frontend.log" 2>&1 &
    FRONTEND_PID=$!
fi
cd "$DIR"

# Cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down MyDaily..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "========================================================"
echo "  MyDaily is now running on your Android device!"
echo ""
echo "  Open your Android browser and go to:"
echo "    http://localhost:3000"
echo "    or http://127.0.0.1:3000"
echo ""
echo "  Logs: termux-backend.log & termux-frontend.log"
echo "  Press Ctrl+C to stop both servers."
echo "========================================================"

# Keep script running
wait

