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
jugdatos = fn.crearjugador(ancho, alto)
# C
icontinuara = fn.ccontinuara(ancho, alto)
# C

reloj = pygame.time.Clock()
estado = "menu"
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
                if estado in ("juego", "continuara"):
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
                            estado = "juego"
                            # C
                        elif b["accion"] == "salir":
                            jugando = False

    if estado == "menu":
        fondosurf = fn.framevideo(video, ancho, alto)
        fn.dibujar(pantalla, fondosurf, panelizq, panelder, anchopanel, t1, t2, rect1, rect2, botones, fuentebtn, mouse)
    elif estado == "juego":
        # C
        fn.moverjugador(jugdatos, teclas, ancho, alto)
        if jugdatos["rect"].right >= ancho:
            estado = "continuara"
        else:
            fn.dibujarjuego(pantalla, mapagraf, jugdatos)
        # C
    elif estado == "continuara":
        # C
        fn.dcontinuara(pantalla, icontinuara)
        # C

    pygame.display.flip()
    reloj.tick(60)

video.release()
pygame.quit()
sys.exit()
