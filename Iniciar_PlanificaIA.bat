@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo No se encontro Python. Instala Python 3 y vuelve a intentarlo.
  pause
  exit /b 1
)
echo Iniciando PlanificaIA...
echo Cuando aparezca la URL, abre http://127.0.0.1:8000 en el navegador.
echo Para apagar el servidor, vuelve aqui y pulsa Ctrl+C.
python web_app.py
pause

