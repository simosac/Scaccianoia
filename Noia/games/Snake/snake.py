import pygame
import random
import sys

# --- Costanti ---
LARGHEZZA = 600
ALTEZZA = 600
DIMENSIONE_CELLA = 20
COLONNE = LARGHEZZA // DIMENSIONE_CELLA
RIGHE = ALTEZZA // DIMENSIONE_CELLA
FPS = 10

# Colori
NERO       = (0, 0, 0)
BIANCO     = (255, 255, 255)
VERDE      = (50, 200, 50)
VERDE_SCURO = (30, 140, 30)
ROSSO      = (220, 50, 50)
GRIGIO     = (30, 30, 30)
GIALLO     = (255, 220, 0)

# Direzioni
SU    = (0, -1)
GIU   = (0, 1)
SINIS = (-1, 0)
DEST  = (1, 0)


def disegna_griglia(schermo):
    for x in range(0, LARGHEZZA, DIMENSIONE_CELLA):
        pygame.draw.line(schermo, (40, 40, 40), (x, 0), (x, ALTEZZA))
    for y in range(0, ALTEZZA, DIMENSIONE_CELLA):
        pygame.draw.line(schermo, (40, 40, 40), (0, y), (LARGHEZZA, y))


def disegna_serpente(schermo, serpente):
    for i, (x, y) in enumerate(serpente):
        rect = pygame.Rect(x * DIMENSIONE_CELLA + 1, y * DIMENSIONE_CELLA + 1,
                           DIMENSIONE_CELLA - 2, DIMENSIONE_CELLA - 2)
        colore = VERDE if i == 0 else VERDE_SCURO
        pygame.draw.rect(schermo, colore, rect, border_radius=4)
        # Occhi sulla testa
        if i == 0:
            pygame.draw.circle(schermo, BIANCO,
                               (x * DIMENSIONE_CELLA + 6, y * DIMENSIONE_CELLA + 6), 3)
            pygame.draw.circle(schermo, BIANCO,
                               (x * DIMENSIONE_CELLA + 14, y * DIMENSIONE_CELLA + 6), 3)
            pygame.draw.circle(schermo, NERO,
                               (x * DIMENSIONE_CELLA + 6, y * DIMENSIONE_CELLA + 6), 1)
            pygame.draw.circle(schermo, NERO,
                               (x * DIMENSIONE_CELLA + 14, y * DIMENSIONE_CELLA + 6), 1)


def disegna_cibo(schermo, cibo):
    x, y = cibo
    cx = x * DIMENSIONE_CELLA + DIMENSIONE_CELLA // 2
    cy = y * DIMENSIONE_CELLA + DIMENSIONE_CELLA // 2
    pygame.draw.circle(schermo, ROSSO, (cx, cy), DIMENSIONE_CELLA // 2 - 2)
    # Fogliolina
    pygame.draw.line(schermo, VERDE,
                     (cx, cy - DIMENSIONE_CELLA // 2 + 2),
                     (cx + 4, cy - DIMENSIONE_CELLA // 2 - 2), 2)


def genera_cibo(serpente):
    while True:
        pos = (random.randint(0, COLONNE - 1), random.randint(0, RIGHE - 1))
        if pos not in serpente:
            return pos


def schermata_game_over(schermo, font_grande, font_piccolo, punteggio):
    schermo.fill(GRIGIO)
    testo = font_grande.render("GAME OVER", True, ROSSO)
    punt = font_piccolo.render(f"Punteggio: {punteggio}", True, BIANCO)
    riprova = font_piccolo.render("Premi R per rigiocare  |  ESC per uscire", True, GIALLO)
    schermo.blit(testo, testo.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 - 60)))
    schermo.blit(punt, punt.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 + 10)))
    schermo.blit(riprova, riprova.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 + 60)))
    pygame.display.flip()


def schermata_inizio(schermo, font_grande, font_piccolo):
    schermo.fill(GRIGIO)
    titolo = font_grande.render("SNAKE", True, VERDE)
    istr = font_piccolo.render("Usa le frecce per muoverti", True, BIANCO)
    avvia = font_piccolo.render("Premi INVIO per iniziare", True, GIALLO)
    schermo.blit(titolo, titolo.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 - 60)))
    schermo.blit(istr, istr.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 + 10)))
    schermo.blit(avvia, avvia.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 + 60)))
    pygame.display.flip()


def gioca():
    pygame.init()
    schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
    pygame.display.set_caption("Snake - Progetto Noia")
    orologio = pygame.time.Clock()

    font_grande = pygame.font.SysFont("consolas", 56, bold=True)
    font_piccolo = pygame.font.SysFont("consolas", 22)
    font_hud = pygame.font.SysFont("consolas", 18)

    # --- Schermata iniziale ---
    schermata_inizio(schermo, font_grande, font_piccolo)
    attesa = True
    while attesa:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    attesa = False
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    # --- Loop principale ---
    while True:
        # Inizializza stato partita
        serpente = [(COLONNE // 2, RIGHE // 2)]
        direzione = DEST
        prossima_dir = DEST
        cibo = genera_cibo(serpente)
        punteggio = 0
        in_gioco = True

        while in_gioco:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP and direzione != GIU:
                        prossima_dir = SU
                    elif evento.key == pygame.K_DOWN and direzione != SU:
                        prossima_dir = GIU
                    elif evento.key == pygame.K_LEFT and direzione != DEST:
                        prossima_dir = SINIS
                    elif evento.key == pygame.K_RIGHT and direzione != SINIS:
                        prossima_dir = DEST
                    elif evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            direzione = prossima_dir
            testa_x, testa_y = serpente[0]
            nuova_testa = (testa_x + direzione[0], testa_y + direzione[1])

            # Collisione con i muri
            if not (0 <= nuova_testa[0] < COLONNE and 0 <= nuova_testa[1] < RIGHE):
                in_gioco = False
                break

            # Collisione con se stesso
            if nuova_testa in serpente:
                in_gioco = False
                break

            serpente.insert(0, nuova_testa)

            if nuova_testa == cibo:
                punteggio += 10
                cibo = genera_cibo(serpente)
            else:
                serpente.pop()

            # Disegno
            schermo.fill(GRIGIO)
            disegna_griglia(schermo)
            disegna_cibo(schermo, cibo)
            disegna_serpente(schermo, serpente)

            # HUD punteggio
            testo_punt = font_hud.render(f"Punteggio: {punteggio}", True, BIANCO)
            schermo.blit(testo_punt, (8, 6))

            pygame.display.flip()
            orologio.tick(FPS)

        # --- Game Over ---
        schermata_game_over(schermo, font_grande, font_piccolo, punteggio)
        attesa_go = True
        while attesa_go:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        attesa_go = False  # Rigioca
                    elif evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()


if __name__ == "__main__":
    gioca()
