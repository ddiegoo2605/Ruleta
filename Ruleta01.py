#!/usr/bin/env python3
import pygame
import random
import math

# Constants del joc
NUMEROS = list(range(37))  # De 0 a 36
COLORS = {0: "verd", **{n: "vermell" if n % 2 else "negre" for n in range(1, 37)}}
COLUMNES = {1: [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
            2: [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
            3: [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]}
FITXES_VALORS = [5, 10, 20, 50, 100]
AMPLADA, ALCADA = 800, 600
# Ordre i colors dels números de la ruleta
NOMBRES_RUETA = [
    (0, "verd"), (32, "vermell"), (15, "negre"), (19, "vermell"), (4, "negre"),
    (21, "vermell"), (2, "negre"), (25, "vermell"), (17, "negre"), (34, "vermell"),
    (6, "negre"), (27, "vermell"), (13, "negre"), (36, "vermell"), (11, "negre"),
    (30, "vermell"), (8, "negre"), (23, "vermell"), (10, "negre"), (5, "vermell"),
    (24, "negre"), (16, "vermell"), (33, "negre"), (1, "vermell"), (20, "negre"),
    (14, "vermell"), (31, "negre"), (9, "vermell"), (22, "negre"), (18, "vermell"),
    (29, "negre"), (7, "vermell"), (28, "negre"), (12, "vermell"), (35, "negre"),
    (3, "vermell"), (26, "negre")
]

pygame.init()
clock = pygame.time.Clock()

# Definir la finestra
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Window Title')

class Jugador:
    def __init__(self, nom, saldo=100):
        self.nom = nom
        self.saldo = saldo
        self.fitxes = {val: 0 for val in FITXES_VALORS}
        self._distribuir_fitxes()
        self.apostes = []  # Ex. [(tipus, valor)]

    def _distribuir_fitxes(self):
        restant = self.saldo
        for val in sorted(FITXES_VALORS, reverse=True):
            self.fitxes[val], restant = divmod(restant, val)

    def apostar(self, quantitat, tipus_aposta):
        if quantitat > self.saldo:
            raise ValueError(f"{self.nom} no té saldo suficient!")
        self.saldo -= quantitat
        self.apostes.append((tipus_aposta, quantitat))

    def afegir_guanys(self, quantitat):
        self.saldo += quantitat
        self._distribuir_fitxes()

class Ruleta:
    def __init__(self):
        self.resultat = None

    def girar(self):
        self.resultat = random.choice(NUMEROS)
        return self.resultat, COLORS[self.resultat]

class Partida:
    def __init__(self):
        self.ruleta = Ruleta()
        self.jugadors = [Jugador("Taronja"), Jugador("Lila"), Jugador("Blau")]
        self.historial = []

    def calcular_guanys(self, resultat):
        for jugador in self.jugadors:
            for tipus, quantitat in jugador.apostes:
                # Número exacte
                if tipus == "numero" and resultat[0] == tipus:
                    jugador.afegir_guanys(quantitat * 35)
                # Color (vermell/negre)
                elif tipus == "color" and resultat[1] == tipus:
                    jugador.afegir_guanys(quantitat * 2)
                # Parell/Senar
                elif tipus == "parell" and resultat[0] != 0 and resultat[0] % 2 == 0:
                    jugador.afegir_guanys(quantitat * 2)
                elif tipus == "senar" and resultat[0] % 2 != 0:
                    jugador.afegir_guanys(quantitat * 2)
                # Columna
                elif tipus in ["columna1", "columna2", "columna3"]:
                    columna = COLUMNES[int(tipus[-1])]
                    if resultat[0] in columna:
                        jugador.afegir_guanys(quantitat * 3)
            jugador.apostes.clear()


    def jugar_tirada(self):
        resultat = self.ruleta.girar()
        self.calcular_guanys(resultat)
        self.historial.append({"resultat": resultat, "jugadors": [(j.nom, j.saldo) for j in self.jugadors]})


def dibuixar_fitxes(screen, jugador, pos_x, pos_y):
    # Exemple per dibuixar les fitxes d'un jugador
    font = pygame.font.Font(None, 24)
    for valor, quantitat in jugador.fitxes.items():
        for i in range(quantitat):
            # Dibuixar una fitxa de color (per exemple, color taronja per al jugador Taronja)
            pygame.draw.circle(screen, (255, 165, 0), (pos_x, pos_y), 15)
            pos_y += 30  # Espai entre fitxes
            text = font.render(f"{valor} x {quantitat}", True, (0, 0, 0))
            screen.blit(text, (pos_x + 20, pos_y))


# Funció per mostrar moviment de fitxes
def moure_fitxes(screen, origen, desti, color):
    x1, y1 = origen
    x2, y2 = desti
    passos = 20
    for i in range(passos):
        x = x1 + (x2 - x1) * i / passos
        y = y1 + (y2 - y1) * i / passos
        pygame.draw.circle(screen, color, (int(x), int(y)), 10)
        pygame.display.flip()
        pygame.time.delay(30)

def moure_fitxa(screen, jugador, mouse_x, mouse_y, valor_fitxa):
    if jugador.fitxes[valor_fitxa] > 0:  # Si el jugador té fitxes de valor
        pygame.draw.circle(screen, (255, 165, 0), (mouse_x, mouse_y), 15)


def verificar_final_partida(jugadors):
    for jugador in jugadors:
        if jugador.saldo <= 0:
            return True  # Finalitzar partida si algun jugador s'ha quedat sense saldo
    return False

def mostrar_historial(screen, historial):
    font = pygame.font.Font(None, 24)
    for i, tirada in enumerate(historial):
        text = font.render(f"Tirada {i+1}: {tirada['resultat']} - Jugadors: {tirada['jugadors']}", True, (255, 255, 255))
        screen.blit(text, (50, 100 + i * 30))



# Interfície gràfica
def dibuixar_ruleta(screen, resultat=None):
    # Dibuixem el cercle principal de la ruleta
    pygame.draw.circle(screen, (200, 200, 200), (400, 300), 200, 0)
    font = pygame.font.Font(None, 24)
    
    for i, (num, color) in enumerate(NOMBRES_RUETA):
        angle = math.radians(i * (360 / len(NOMBRES_RUETA)))
        x = 400 + 180 * math.cos(angle)
        y = 300 - 180 * math.sin(angle)
        text = font.render(str(num), True, (255, 0, 0) if color == "vermell" else (0, 0, 0) if color == "negre" else (0, 255, 0))
        screen.blit(text, (x - text.get_width() / 2, y - text.get_height() / 2))
        # Línia divisòria
        x_final = 400 + 180 * math.cos(angle)
        y_final = 300 - 180 * math.sin(angle)
        pygame.draw.line(screen, (0, 0, 0), (400, 300), (x_final, y_final), 1)

    if resultat:
     # Determinem l'angle del número guanyador
        index = next(i for i, (num, _) in enumerate(NOMBRES_RUETA) if num == resultat[0])
        resultat_angle = math.radians(index * (360 / len(NOMBRES_RUETA)))
        x_final = 400 + 150 * math.cos(resultat_angle)
        y_final = 300 - 150 * math.sin(resultat_angle)
        # Dibuixem la línia que assenyala el número guanyador
        pygame.draw.line(screen, (255, 0, 0), (400, 300), (x_final, y_final), 3)


      # Dibuixem línies per als pals
    for i in range(len(NOMBRES_RUETA)):
        angle = math.radians(i * (360 / len(NOMBRES_RUETA)))
        x_final = 400 + 180 * math.cos(angle)
        y_final = 300 - 180 * math.sin(angle)
        pygame.draw.line(screen, (0, 0, 0), (400, 300), (x_final, y_final), 1)
    

    # Dibuixem els números i les línies divisòries
    

    # Afegim una línia per escollir el número guanyador
    

def dibuixar_taula_apostes(screen):
    # Espais per apostes
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(50, 450, 100, 50))  # Espai "vermell"
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(150, 450, 100, 50))  # Espai "negre"
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(250, 450, 100, 50))  # Espai "parell"
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(350, 450, 100, 50))  # Espai "senar"
    pygame.draw.rect(screen, (0, 128, 0), pygame.Rect(450, 450, 100, 50))  # Espai "columna1"
    pygame.draw.rect(screen, (0, 128, 0), pygame.Rect(550, 450, 100, 50))  # Espai "columna2"
    pygame.draw.rect(screen, (0, 128, 0), pygame.Rect(650, 450, 100, 50))  # Espai "columna3"
    pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(50, 520, 700, 50))  # Espai "Banca"
    
    # Afegir textos explicatius
    font = pygame.font.Font(None, 24)
    text_vermell = font.render("Vermell", True, (255, 255, 255))
    screen.blit(text_vermell, (60, 460))
    text_negre = font.render("Negre", True, (255, 255, 255))
    screen.blit(text_negre, (160, 460))
    text_parell = font.render("Parell", True, (0, 0, 0))
    screen.blit(text_parell, (260, 460))
    text_senar = font.render("Senar", True, (0, 0, 0))
    screen.blit(text_senar, (360, 460))
    text_columna1 = font.render("Columna 1", True, (255, 255, 255))
    screen.blit(text_columna1, (460, 460))
    text_columna2 = font.render("Columna 2", True, (255, 255, 255))
    screen.blit(text_columna2, (560, 460))
    text_columna3 = font.render("Columna 3", True, (255, 255, 255))
    screen.blit(text_columna3, (660, 460))
    text_banca = font.render("Banca", True, (0, 0, 0))
    screen.blit(text_banca, (60, 530))

def moure_fitxes_cap_a_banca(screen, origen, banc):
    pygame.draw.circle(screen, (0, 0, 0), banc, 15)  # Moure la fitxa cap a la banca


def joc_grafic():
    pygame.init()
    screen = pygame.display.set_mode((AMPLADA, ALCADA))
    pygame.display.set_caption("Ruleta de Casino")
    clock = pygame.time.Clock()
    partida = Partida()
    resultat = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Girem la ruleta i obtenim el resultat
                resultat = partida.ruleta.girar()
                partida.calcular_guanys(resultat)

        screen.fill((0, 128, 0))  # Color verd de fons
        dibuixar_ruleta(screen, resultat)  # Dibuixa la ruleta amb la línia guanyadora
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    joc_grafic()

