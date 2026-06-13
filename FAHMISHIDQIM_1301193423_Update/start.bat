@echo off
echo ============================================
echo   Starting Fake News Detector
echo ============================================
echo.

echo Starting Backend Server...
start cmd /k "cd backend && venv\Scripts\activate && python app.py"

timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start cmd /k "cd frontend && npm run dev"

echo.
echo ============================================
echo   Servers Started!
echo ============================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Press any key to open frontend in browser...
pause > nul

start http://localhost:5173

echo.
echo Application is running!
echo Close the terminal windows to stop the servers.
echo.
