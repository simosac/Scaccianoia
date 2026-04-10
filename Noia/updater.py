"""
updater.py — Gestione aggiornamenti automatici via GitHub Releases
Controlla la versione più recente e scarica i nuovi giochi.
"""

import json
import urllib.request
import urllib.error
import zipfile
import shutil
import tempfile
import os
from pathlib import Path

GITHUB_API = "https://api.github.com/repos/{user}/{repo}/releases/latest"
TIMEOUT = 8  # secondi


# ── Controllo versione ───────────────────────────────────────
def controlla_aggiornamento(versione_info: dict) -> dict | None:
    """
    Chiama l'API GitHub e restituisce le info del nuovo release
    se esiste una versione più recente, altrimenti None.
    """
    user = versione_info.get("github_user", "")
    repo = versione_info.get("github_repo", "")
    versione_attuale = versione_info.get("version", "0.0.0")

    if not user or not repo or user in ("TUO_USERNAME", ""):
        return None  # GitHub non ancora configurato

    url = GITHUB_API.format(user=user, repo=repo)
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "NoiaLauncher/1.0",
                          "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None  # Nessuna connessione o risposta non valida

    tag = data.get("tag_name", "v0.0.0").lstrip("v")

    if not _e_piu_nuova(tag, versione_attuale):
        return None  # Già aggiornato

    # Cerca l'asset ZIP tra gli allegati del release
    zip_url = None
    for asset in data.get("assets", []):
        if asset.get("name", "").endswith(".zip"):
            zip_url = asset["browser_download_url"]
            break

    if not zip_url:
        return None  # Release senza ZIP allegato

    return {
        "version": tag,
        "zip_url": zip_url,
        "descrizione": data.get("body", "").strip()
    }


# ── Download e installazione ─────────────────────────────────
def scarica_e_installa(info: dict, base_dir: Path):
    """
    Scarica lo ZIP del release e aggiorna games/ e version.json.
    Non tocca launcher.py o updater.py (evita di sovrascrivere file in uso).
    """
    zip_url = info["zip_url"]
    nuova_versione = info["version"]

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "update.zip")

        # 1. Download con barra di avanzamento (console)
        urllib.request.urlretrieve(zip_url, zip_path)

        # 2. Estrazione
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(tmpdir)

        # 3. Trova la root del contenuto estratto
        # (può essere nella root del tmpdir o in una sotto-cartella)
        estratto_root = _trova_root_estratta(tmpdir, zip_path)

        # 4. Copia solo games/ e version.json (file sicuri da aggiornare a caldo)
        _copia_se_esiste(estratto_root, base_dir, "games")
        _copia_se_esiste(estratto_root, base_dir, "version.json")

    # 5. Aggiorna il numero di versione nel file locale
    _aggiorna_numero_versione(base_dir / "version.json", nuova_versione)


# ── Utilità interne ──────────────────────────────────────────
def _e_piu_nuova(nuova: str, attuale: str) -> bool:
    """Confronta versioni semver (x.y.z). Gestisce anche 'x.y'."""
    try:
        def normalizza(v):
            parti = v.split(".")
            while len(parti) < 3:
                parti.append("0")
            return tuple(int(p) for p in parti[:3])
        return normalizza(nuova) > normalizza(attuale)
    except Exception:
        return False


def _trova_root_estratta(tmpdir: str, zip_path: str) -> str:
    """
    Restituisce il percorso della root del contenuto estratto.
    Se tutto è in una sotto-cartella (es. 'noia-games-v1.1.0/'), entra dentro.
    """
    elementi = [e for e in os.listdir(tmpdir)
                if e != os.path.basename(zip_path)]
    if len(elementi) == 1:
        candidato = os.path.join(tmpdir, elementi[0])
        if os.path.isdir(candidato):
            return candidato
    return tmpdir


def _copia_se_esiste(src_dir: str, dst_dir: Path, nome: str):
    src = os.path.join(src_dir, nome)
    dst = dst_dir / nome
    if not os.path.exists(src):
        return
    if os.path.isdir(src):
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def _aggiorna_numero_versione(ver_file: Path, nuova_versione: str):
    if not ver_file.exists():
        return
    try:
        with open(ver_file, encoding="utf-8") as f:
            data = json.load(f)
        data["version"] = nuova_versione
        with open(ver_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
