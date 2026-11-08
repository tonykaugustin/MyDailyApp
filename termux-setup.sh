#!/data/data/com.termux/files/usr/bin/bash
# ========================================================
#   MYDAILY - TERMUX ONE-TIME INSTALLATION & SETUP
# ========================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "========================================================"
echo "          MYDAILY - TERMUX SETUP SCRIPT                 "
echo "========================================================"

echo "[1/6] Updating packages & installing system dependencies..."
pkg update -y
pkg install -y python python-pip nodejs-lts mariadb clang libffi openssl git netcat-openbsd

echo "[2/6] Setting up MariaDB (MySQL)..."
if [ ! -d "/data/data/com.termux/files/usr/var/lib/mysql/mysql" ]; then
    mysql_install_db
fi

# Ensure MariaDB is running
if ! nc -z 127.0.0.1 3306 >/dev/null 2>&1; then
    mysqld_safe -u root >/dev/null 2>&1 &
    sleep 3
fi

# Configure database & root user with password 1012
mariadb -u root -e "CREATE DATABASE IF NOT EXISTS mydailyapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || true
mariadb -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '1012'; FLUSH PRIVILEGES;" 2>/dev/null || \
mariadb -u root -p1012 -e "CREATE DATABASE IF NOT EXISTS mydailyapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || true

echo "[3/6] Setting up Python virtual environment..."
if [ ! -d "$DIR/venv" ]; then
    python -m venv "$DIR/venv"
fi
source "$DIR/venv/bin/activate"

echo "[4/6] Installing Python backend packages..."
pip install --upgrade pip
pip install -r "$DIR/backend/requirements.txt"

echo "[5/6] Applying Django database migrations..."
export DB_ENGINE="mysql"
export DB_NAME="mydailyapp"
export DB_USER="root"
export DB_PASSWORD="1012"
export DB_HOST="127.0.0.1"
export DB_PORT="3306"
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS="*"
export CORS_ALLOW_ALL=True

cd "$DIR/backend"
python manage.py migrate

echo "Seeding starter data..."
python manage.py shell -c "
from django.contrib.auth.models import User
from accounts.seed_data import seed_user_data
user, created = User.objects.get_or_create(username='demo', defaults={'email': 'demo@mydaily.local'})
user.set_password('password123')
user.first_name = 'Alex'
user.last_name = 'Morgan'
user.save()
seed_user_data(user)
print('Demo account initialized (demo / password123)')
"
cd "$DIR"

echo "[6/6] Installing frontend dependencies & building..."
cd "$DIR/frontend"
npm install
npm run build
cd "$DIR"

echo "========================================================"
echo "  Setup Complete! You can now run MyDaily anytime with:"
echo "    ./termux-run.sh"
echo "========================================================"

