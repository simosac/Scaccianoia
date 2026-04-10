#!/usr/bin/env bash
# avvia.sh — Launcher Noia per Linux e macOS
# Uso: bash avvia.sh  oppure  ./avvia.sh (dopo chmod +x avvia.sh)

cd "$(dirname "$0")"

# ── Cerca Python 3 compatibile ─────────────────────────────
PYTHON_CMD=""
for cmd in python3.13 python3.12 python3.11 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        # Controlla che sia >= 3.11 e < 3.14
        VER=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [ "$MAJOR" = "3" ] && [ "$MINOR" -ge 11 ] && [ "$MINOR" -le 13 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

# ── Se non trovato, suggerisci installazione ──────────────
if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "  Python 3.11-3.13 non trovato sul sistema."
    echo ""
    # Rileva OS e dai le istruzioni giuste
    OS="$(uname -s)"
    if [ "$OS" = "Darwin" ]; then
        echo "  macOS — Installa con Homebrew:"
        echo "    brew install python@3.12"
        echo ""
        echo "  Oppure scarica da: https://www.python.org/downloads/"
    else
        echo "  Linux — Installa con il tuo package manager, es:"
        echo "    sudo apt install python3.12   # Ubuntu/Debian"
        echo "    sudo dnf install python3.12   # Fedora"
        echo ""
        echo "  Oppure scarica da: https://www.python.org/downloads/"
    fi
    echo ""
    read -r -p "  Premi INVIO per uscire..."
    exit 1
fi

echo "  [OK] Python trovato: $PYTHON_CMD ($VER)"

# ── Installa pygame se mancante ───────────────────────────
"$PYTHON_CMD" -c "import pygame" &>/dev/null
if [ $? -ne 0 ]; then
    echo "  Installazione pygame..."
    "$PYTHON_CMD" -m pip install pygame --quiet
fi

# ── Avvia il launcher ─────────────────────────────────────
"$PYTHON_CMD" launcher.py
