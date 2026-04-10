import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import threading
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
GAMES_DIR = BASE_DIR / "games"
VERSION_FILE = BASE_DIR / "version.json"

# ── Palette colori ──────────────────────────────────────────
BG_DARK    = "#0d0d1a"
BG_CARD    = "#16213e"
BG_HEADER  = "#0f1b35"
ACCENT     = "#e94560"
ACCENT2    = "#0f3460"
TXT_WHITE  = "#e8e8f0"
TXT_GREY   = "#7777aa"
TXT_GREEN  = "#50fa7b"
FONT_MAIN  = ("Consolas", 11)


def leggi_versione() -> dict:
    if VERSION_FILE.exists():
        try:
            with open(VERSION_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"version": "1.0.0", "github_user": "TUO_USERNAME", "github_repo": "noia-games"}


def scopri_giochi() -> list:
    giochi = []
    if not GAMES_DIR.exists():
        return giochi
    for cartella in sorted(GAMES_DIR.iterdir()):
        if cartella.is_dir():
            py_files = list(cartella.glob("*.py"))
            if py_files:
                giochi.append({"nome": cartella.name, "script": py_files[0]})
    return giochi


def avvia_gioco(script: Path):
    subprocess.Popen([sys.executable, str(script)],
                     cwd=str(script.parent))


def installa_pygame_se_manca():
    try:
        import pygame  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pygame", "--quiet"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )


# ── App principale ───────────────────────────────────────────
class LauncherApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.versione_info = leggi_versione()
        self._configura_finestra()
        self._costruisci_ui()
        self._aggiorna_lista_giochi()
        # Controlla aggiornamenti in background (non blocca la UI)
        threading.Thread(target=self._check_update_bg, daemon=True).start()

    # ── Setup finestra ───────────────────────────────────────
    def _configura_finestra(self):
        self.root.title("Noia — Catalogo giochi")
        self.root.geometry("480x560")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)
        # Centra la finestra
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"+{x}+{y}")

    # ── Costruzione UI ───────────────────────────────────────
    def _costruisci_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=BG_HEADER, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="🎮  NOIA", font=("Consolas", 30, "bold"),
                 fg=ACCENT, bg=BG_HEADER).pack()
        tk.Label(header, text="Il tuo catalogo anti-noia",
                 font=("Consolas", 11), fg=TXT_GREY, bg=BG_HEADER).pack()

        # SEPARATORE
        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill="x")

        # AREA GIOCHI (scrollabile)
        container = tk.Frame(self.root, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=18, pady=12)

        self.canvas = tk.Canvas(container, bg=BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical",
                                  command=self.canvas.yview)
        self.frame_giochi = tk.Frame(self.canvas, bg=BG_DARK)

        self.frame_giochi.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.frame_giochi, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        # scrollbar visibile solo se necessario
        self.canvas.bind("<MouseWheel>",
                         lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # FOOTER
        footer = tk.Frame(self.root, bg=BG_HEADER, pady=8)
        footer.pack(fill="x", side="bottom")
        tk.Frame(self.root, bg=ACCENT2, height=2).pack(fill="x", side="bottom")

        ver = self.versione_info.get("version", "1.0.0")
        self.lbl_status = tk.Label(footer, text=f"v{ver}",
                                    font=("Consolas", 9), fg=TXT_GREY, bg=BG_HEADER)
        self.lbl_status.pack(side="left", padx=12)

        btn_upd = tk.Button(
            footer, text="⟳  Aggiornamenti",
            font=("Consolas", 10), bg=ACCENT2, fg=TXT_WHITE,
            activebackground=ACCENT, activeforeground="white",
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=self._check_update_manuale
        )
        btn_upd.pack(side="right", padx=12)

    # ── Lista giochi ─────────────────────────────────────────
    def _aggiorna_lista_giochi(self):
        for w in self.frame_giochi.winfo_children():
            w.destroy()

        giochi = scopri_giochi()
        if not giochi:
            tk.Label(self.frame_giochi,
                     text="Nessun gioco trovato.\nAggiungi cartelle in  games/",
                     font=FONT_MAIN, fg=TXT_GREY, bg=BG_DARK,
                     justify="center").pack(pady=40)
            return

        ICONE = {
            "Snake": "🐍", "Tetris": "🟦", "Pong": "🏓",
            "Breakout": "🧱", "Pacman": "👾", "Asteroids": "🚀"
        }

        for g in giochi:
            self._crea_card(g["nome"], g["script"], ICONE)

    def _crea_card(self, nome: str, script: Path, icone: dict):
        icona = icone.get(nome, "🎮")
        card = tk.Frame(self.frame_giochi, bg=BG_CARD, pady=10, padx=14)
        card.pack(fill="x", pady=5, ipady=2)

        tk.Label(card, text=f"{icona}  {nome}",
                 font=("Consolas", 14, "bold"), fg=TXT_WHITE,
                 bg=BG_CARD, anchor="w").pack(side="left", fill="x", expand=True)

        tk.Button(
            card, text="▶  Gioca",
            font=("Consolas", 11, "bold"), bg=ACCENT, fg="white",
            activebackground="#c73652", activeforeground="white",
            relief="flat", cursor="hand2", padx=12, pady=5,
            command=lambda s=script: avvia_gioco(s)
        ).pack(side="right")

    # ── Aggiornamenti ────────────────────────────────────────
    def _check_update_bg(self):
        try:
            import updater
            info = updater.controlla_aggiornamento(self.versione_info)
            if info:
                self.root.after(0, lambda: self._notifica_aggiornamento(info))
            else:
                ver = self.versione_info.get("version", "1.0.0")
                self.root.after(0, lambda: self.lbl_status.config(
                    text=f"v{ver}  ✓", fg=TXT_GREEN))
        except Exception:
            pass

    def _check_update_manuale(self):
        self.lbl_status.config(text="Controllo in corso…", fg=TXT_GREY)
        threading.Thread(target=self._check_update_bg, daemon=True).start()

    def _notifica_aggiornamento(self, info):
        self.lbl_status.config(
            text=f"🔔  v{info['version']} disponibile!", fg=ACCENT)
        risposta = messagebox.askyesno(
            "Aggiornamento disponibile",
            f"È disponibile la versione {info['version']}.\n\n"
            f"Vuoi scaricarla adesso?\n"
            f"(I nuovi giochi verranno aggiunti automaticamente)"
        )
        if risposta:
            threading.Thread(
                target=self._scarica_e_installa, args=(info,), daemon=True
            ).start()

    def _scarica_e_installa(self, info):
        try:
            import updater
            self.root.after(0, lambda: self.lbl_status.config(
                text="⬇  Download in corso…", fg=TXT_GREY))
            updater.scarica_e_installa(info, BASE_DIR)
            self.root.after(0, self._post_aggiornamento)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Errore", f"Aggiornamento fallito:\n{e}"))

    def _post_aggiornamento(self):
        self.versione_info = leggi_versione()
        ver = self.versione_info.get("version", "?")
        self.lbl_status.config(text=f"v{ver}  ✓ aggiornato!", fg=TXT_GREEN)
        self._aggiorna_lista_giochi()
        messagebox.showinfo("Aggiornamento completato",
                             "Tutti i nuovi giochi sono stati installati!")


# ── Entry point ──────────────────────────────────────────────
def main():
    # Installa pygame silenziosamente se non presente
    threading.Thread(target=installa_pygame_se_manca, daemon=True).start()
    root = tk.Tk()
    LauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
