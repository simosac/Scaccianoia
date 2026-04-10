@echo off
title Build Snake.exe
color 0A
echo ============================================
echo   CREAZIONE Snake.exe - Progetto Noia
echo ============================================
echo.

REM pygame non supporta ancora Python 3.14.
REM Cerchiamo una versione compatibile: 3.13, 3.12, 3.11
set PYTHON_CMD=
set PYTHON_VER=

for %%V in (3.13 3.12 3.11) do (
    if "!PYTHON_CMD!"=="" (
        py -%%V --version >nul 2>&1
        if !errorlevel! == 0 (
            set PYTHON_CMD=py -%%V
            set PYTHON_VER=%%V
        )
    )
)

REM Abilita delayed expansion per i blocchi if/for
setlocal enabledelayedexpansion
set PYTHON_CMD=
set PYTHON_VER=

for %%V in (3.13 3.12 3.11) do (
    if "!PYTHON_CMD!"=="" (
        py -%%V --version >nul 2>&1
        if !errorlevel! == 0 (
            set PYTHON_CMD=py -%%V
            set PYTHON_VER=%%V
        )
    )
)

if "!PYTHON_CMD!"=="" (
    echo [ATTENZIONE] Python 3.14 rilevato, ma pygame non lo supporta ancora.
    echo.
    echo Soluzione: installa Python 3.12 da https://www.python.org/downloads/
    echo Durante l'installazione spunta "Add Python to PATH".
    echo Poi esegui di nuovo questo file build.bat.
    echo.
    pause
    exit /b 1
)

echo [OK] Trovato Python !PYTHON_VER! - uso: !PYTHON_CMD!
echo.
echo Installazione dipendenze...
!PYTHON_CMD! -m pip install pygame pyinstaller --quiet
if !errorlevel! neq 0 (
    echo [ERRORE] Installazione dipendenze fallita.
    pause
    exit /b 1
)
echo [OK] Dipendenze installate.
echo.
echo Compilazione Snake.exe in corso (potrebbe volerci un minuto)...
!PYTHON_CMD! -m PyInstaller --onefile --windowed --name "Snake" snake.py
if !errorlevel! neq 0 (
    echo [ERRORE] Compilazione fallita.
    pause
    exit /b 1
)

echo.
echo [OK] Snake.exe creato!
echo.
echo Copia Snake.exe nella cartella Noia...
copy /Y "dist\Snake.exe" "..\Snake.exe" >nul
echo [OK] Snake.exe copiato in: Noia\Snake.exe
echo.
echo ============================================
echo   FATTO! Apri la cartella Noia e clicca
echo   Snake.exe per giocare!
echo ============================================
echo.
pause
