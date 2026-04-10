@echo off
setlocal enabledelayedexpansion
title Noia — Avvio launcher
cd /d "%~dp0"

REM ── Cerca una versione di Python compatibile (3.11 / 3.12 / 3.13) ──
set PYTHON_CMD=

REM Prima prova il comando 'python' standard
python --version >nul 2>&1
if !errorlevel! == 0 (
    for /f "tokens=2 delims= " %%V in ('python --version 2^>^&1') do set PY_VER=%%V
    REM Accetta 3.11, 3.12, 3.13 — rifiuta 3.14+
    for %%M in (3.11 3.12 3.13) do (
        if "!PY_VER:~0,4!"=="%%M." set PYTHON_CMD=python
    )
)

REM Se non trovato, prova il py launcher con versioni specifiche
if "!PYTHON_CMD!"=="" (
    for %%V in (3.13 3.12 3.11) do (
        if "!PYTHON_CMD!"=="" (
            py -%%V --version >nul 2>&1
            if !errorlevel! == 0 set PYTHON_CMD=py -%%V
        )
    )
)

REM Se ancora niente, mostra istruzioni
if "!PYTHON_CMD!"=="" (
    echo.
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║   Python compatibile non trovato!                   ║
    echo  ║                                                      ║
    echo  ║   Scarica Python 3.12 da:                           ║
    echo  ║   https://www.python.org/downloads/                 ║
    echo  ║                                                      ║
    echo  ║   Durante l'installazione spunta:                   ║
    echo  ║   [✓] Add Python to PATH                            ║
    echo  ║                                                      ║
    echo  ║   Poi riesegui questo file.                         ║
    echo  ╚══════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

echo  [OK] Python trovato: !PYTHON_CMD!

REM ── Avvia il launcher ──
!PYTHON_CMD! launcher.py
if !errorlevel! neq 0 (
    echo.
    echo  [ERRORE] Il launcher si e' chiuso con un errore.
    pause
)
