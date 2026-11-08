@echo off
echo ========================================================
echo         MYDAILY - STARTING IN PRODUCTION MODE
echo ========================================================

REM Set Production Environment Variables
set DJANGO_DEBUG=False
set DJANGO_ALLOWED_HOSTS=*
set CORS_ALLOW_ALL=True
set NODE_ENV=production
set HOST=0.0.0.0
set NITRO_HOST=0.0.0.0
set PORT=3000
set NUXT_PUBLIC_API_BASE=/api

echo [1/3] Verifying Backend Static Files...
cd backend
..\venv\Scripts\python.exe manage.py collectstatic --noinput
cd ..

echo [2/3] Starting Backend Production WSGI Server on 0.0.0.0:8000...
start "MyDaily Backend (Production)" cmd /k "cd backend && ..\venv\Scripts\waitress-serve.exe --listen=0.0.0.0:8000 mydaily_backend.wsgi:application"

echo [3/3] Starting Frontend Production Server on 0.0.0.0:3000...
start "MyDaily Frontend (Production)" cmd /k "cd frontend && node .output/server/index.mjs"

echo ========================================================
echo   MyDaily is now accessible from your laptop and LAN!
echo.
echo   On this laptop:
echo     Frontend: http://localhost:3000
echo     Backend:  http://localhost:8000
echo.
echo   From Android / phone (Your Wi-Fi IP):
echo     Frontend: http://10.168.166.52:3000
echo     Backend:  http://10.168.166.52:8000
echo ========================================================
pause
