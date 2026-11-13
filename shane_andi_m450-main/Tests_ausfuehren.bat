@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Smart Parking - Tests
where python >nul 2>nul && (set PY=python) || (set PY=py)
%PY% -m pytest --version >nul 2>nul || (
    echo pytest wird installiert ...
    %PY% -m pip install pytest
)
%PY% -m pytest tests -v
pause
