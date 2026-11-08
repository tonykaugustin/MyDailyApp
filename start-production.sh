#!/bin/bash
set -e

echo "========================================================"
echo "        MYDAILY - STARTING IN PRODUCTION MODE"
echo "========================================================"

export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS="*"
export CORS_ALLOW_ALL=True
export NODE_ENV=production
export PORT=3000
export NUXT_PUBLIC_API_BASE=http://127.0.0.1:8000/api

echo "[1/3] Collecting Django static assets..."
cd backend
python manage.py collectstatic --noinput
cd ..

echo "[2/3] Launching Gunicorn WSGI Server on port 8000..."
cd backend
gunicorn --bind 0.0.0.0:8000 --workers 3 --threads 2 mydaily_backend.wsgi:application &
BACKEND_PID=$!
cd ..

echo "[3/3] Launching Nuxt Production Server on port 3000..."
cd frontend
node .output/server/index.mjs &
FRONTEND_PID=$!
cd ..

echo "========================================================"
echo "  MyDaily is now running in PRODUCTION mode!"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://0.0.0.0:8000"
echo "========================================================"

# Trap SIGINT to kill background services cleanly
trap "kill $BACKEND_PID $FRONTEND_PID" SIGINT SIGTERM
wait

