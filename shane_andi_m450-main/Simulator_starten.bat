@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Smart Parking - Simulator
where python >nul 2>nul && (set PY=python) || (set PY=py)
%PY% --version >nul 2>nul || (
    echo Python ist nicht installiert. Bitte von https://www.python.org installieren
    echo und beim Installieren "Add python.exe to PATH" anhaken.
    pause
    exit /b 1
)
echo Simulator startet ... die Seiten oeffnen sich im Browser.
echo Zum Beenden dieses Fenster schliessen.
echo.
%PY% simulator\sim.py %*
pause
