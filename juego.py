import pygame
import sys
import cv2
import funciones as fn

pygame.init()

pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
ancho, alto = pantalla.get_size()
pygame.display.set_caption("La Matanza Avanza")

video = cv2.VideoCapture("F/trenfondo.mp4" if cv2.VideoCapture("F/trenfondo.mp4").isOpened() else "trenfondo.mp4")
anchopanel = int(ancho * 0.32)

panelizq, panelder = fn.capas(ancho, alto, anchopanel)
fuentetit, fuentebtn = fn.fuentes(alto)
t1, t2, rect1, rect2 = fn.titulos(fuentetit, anchopanel, alto)
botones = fn.btnlista(anchopanel, alto)

mapagraf = fn.cargarmapa(ancho, alto)
mapagraf2 = fn.cargarmapa2(ancho, alto)
jugdatos = fn.crearjugador(ancho, alto)
vidas = fn.cargarvidas(alto)
bfuentetitulo, bfontederrota, botonesderrota = fn.bderrota(ancho, alto)
bloque_temporal = pygame.Rect(
    int(ancho * 0.78),
    int(alto * 0.55),
    int(ancho * 0.08),
    int(alto * 0.12)
)
enemigos = [bloque_temporal]
# C
icontinuara = fn.ccontinuara(ancho, alto)
# C

reloj = pygame.time.Clock()
estado = "menu"
tramo = 1
jugando = True

while jugando:
    mouse = pygame.mouse.get_pos()
    teclas = pygame.key.get_pressed()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jugando = False
        elif evento.type == pygame.KEYDOWN:
            # C
            if evento.key == pygame.K_ESCAPE:
                if estado in ("juego", "continuara", "derrota"):
                    estado = "menu"
                else:
                    jugando = False
            # C
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if estado == "menu":
                for b in botones:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            # C
                            jugdatos = fn.crearjugador(ancho, alto)
                            tramo = 1
                            estado = "juego"
                            # C
                        elif b["accion"] == "salir":
                            jugando = False
            elif estado == "derrota":
                for b in botonesderrota:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            jugdatos = fn.crearjugador(ancho, alto)
                            tramo = 1
                            estado = "juego"
                        elif b["accion"] == "menu":
                            estado = "menu"

    if estado == "menu":
        fondosurf = fn.framevideo(video, ancho, alto)
        fn.dibujar(pantalla, fondosurf, panelizq, panelder, anchopanel, t1, t2, rect1, rect2, botones, fuentebtn, mouse)
    elif estado == "juego":
        # C
        fn.moverjugador(jugdatos, teclas, ancho, alto)
        fn.recibirdaño(jugdatos, enemigos)
        if jugdatos["vida"] <= 0:
            estado = "derrota"
        else:
            if tramo == 1 and jugdatos["rect"].right >= ancho:
                tramo = 2
                jugdatos["rect"].left = 0
            elif tramo == 2 and jugdatos["rect"].left <= 0 and (teclas[pygame.K_a] or teclas[pygame.K_LEFT]):
                tramo = 1
                jugdatos["rect"].right = ancho

            if tramo == 1:
                fn.dibujarjuego(pantalla, mapagraf, jugdatos, vidas, enemigos)
            else:
                fn.dibujarjuego2(pantalla, mapagraf2, jugdatos, vidas)
        # C
    elif estado == "continuara":
        # C
        fn.dcontinuara(pantalla, icontinuara)
        # C
    elif estado == "derrota":
        mapactual = mapagraf if tramo == 1 else mapagraf2
        fn.dibujarperdida(pantalla, jugdatos, mapactual, bfuentetitulo, bfontederrota, botonesderrota, mouse)

    pygame.display.flip()
    reloj.tick(60)

video.release()
pygame.quit()
sys.exit()
