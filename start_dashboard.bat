@echo off
echo =====================================================================
echo  Electoral Forensics Research Dashboard - BML Munjal University
echo  Universal Statistical Patterns of Indian General Elections
echo =====================================================================
echo.

echo [1/2] Starting Python FastAPI Backend on http://localhost:8000 ...
start "FastAPI Backend" cmd /k "cd /d %~dp0 && python start_backend.py"

timeout /t 2 /nobreak > nul

echo [2/2] Starting React Vite Dashboard on http://localhost:3000 ...
start "React Vite Dashboard" cmd /k "cd /d %~dp0election-dashboard && npm run dev"

echo.
echo =====================================================================
echo Dashboard is launching!
echo Frontend: http://localhost:3000
echo Backend API & Docs: http://localhost:8000/docs
echo =====================================================================
timeout /t 5
