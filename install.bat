@echo off
echo ========================================================
echo Installing LegalLens Dependencies...
echo ========================================================
echo.
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo ========================================================
echo Installation completed!
echo You can now start LegalLens by running: start_app.bat
echo ========================================================
pause
