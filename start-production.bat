@echo off
echo ========================================================
echo         MYDAILY - STARTING IN PRODUCTION MODE
echo ========================================================

REM Set Production Environment Variables
set DJANGO_DEBUG=False
set DJANGO_ALLOWED_HOSTS=*
set CORS_ALLOW_ALL=True
set NODE_ENV=production
set PORT=3000
set NUXT_PUBLIC_API_BASE=http://127.0.0.1:8000/api

echo [1/3] Verifying Backend Static Files...
cd backend
..\venv\Scripts\python.exe manage.py collectstatic --noinput
cd ..

echo [2/3] Starting Backend Production WSGI Server (Waitress on http://127.0.0.1:8000)...
start "MyDaily Backend (Production)" cmd /k "cd backend && ..\venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8000 mydaily_backend.wsgi:application"

echo [3/3] Starting Frontend Production Server (Nuxt on http://localhost:3000)...
start "MyDaily Frontend (Production)" cmd /k "cd frontend && node .output/server/index.mjs"

echo ========================================================
echo   MyDaily is now running in PRODUCTION mode!
echo   Frontend: http://localhost:3000
echo   Backend:  http://127.0.0.1:8000
echo ========================================================
pause

