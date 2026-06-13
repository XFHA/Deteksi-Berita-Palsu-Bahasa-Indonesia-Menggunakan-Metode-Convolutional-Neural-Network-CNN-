@echo off
echo ============================================
echo   Training CNN Model
echo ============================================
echo.

cd backend
call venv\Scripts\activate

echo Starting model training...
echo This may take several minutes...
echo.

python train_model.py

echo.
echo ============================================
echo   Training Complete!
echo ============================================
echo.
echo Model saved to: backend/models/
echo.
pause
