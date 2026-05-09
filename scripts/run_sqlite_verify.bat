@echo off
setlocal
cd /d "%~dp0.."
echo Instalando dependencias desde requirements.txt ...
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
python scripts\verify_db.py --sqlite
exit /b %ERRORLEVEL%
