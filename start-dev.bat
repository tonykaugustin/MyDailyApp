@echo off
echo ========================================================
echo         MYDAILY - STARTING IN DEVELOPMENT MODE
echo ========================================================

set DJANGO_DEBUG=True
set DJANGO_ALLOWED_HOSTS=*
set CORS_ALLOW_ALL=True
set NUXT_PUBLIC_API_BASE=/api
set HOST=0.0.0.0
set NITRO_HOST=0.0.0.0

echo [1/2] Starting Django Development Server on 0.0.0.0:8000...
start "MyDaily Backend (Dev)" cmd /k "cd backend && ..\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000"

echo [2/2] Starting Nuxt Development Server on 0.0.0.0:3000...
start "MyDaily Frontend (Dev)" cmd /k "cd frontend && npm run dev"

echo ========================================================
echo   MyDaily Dev Server is starting!
echo.
echo   Local access:       http://localhost:3000
echo   Network / Wi-Fi IP: http://10.168.166.52:3000
echo ========================================================
pause
