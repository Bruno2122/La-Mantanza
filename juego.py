import pygame
import sys
import cv2
import funciones as fn

pygame.init()

pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
ancho, alto = pantalla.get_size()
pygame.display.set_caption("La Matanza Avanza")

video = cv2.VideoCapture("trenfondo.mp4")
anchopanel = int(ancho * 0.32)

panelizq, panelder = fn.capas(ancho, alto, anchopanel)
fuentetit, fuentebtn = fn.fuentes(alto)
t1, t2, rect1, rect2 = fn.titulos(fuentetit, anchopanel, alto)
botones = fn.btnlista(anchopanel, alto)

reloj = pygame.time.Clock()
jugando = True

while jugando:
    mouse = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
            jugando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for b in botones:
                if b["rect"].collidepoint(mouse) and b["accion"] == "salir":
                    jugando = False

    fondosurf = fn.framevideo(video, ancho, alto)
    fn.dibujar(pantalla, fondosurf, panelizq, panelder, anchopanel, t1, t2, rect1, rect2, botones, fuentebtn, mouse)

    pygame.display.flip()
    reloj.tick(60)

video.release()
pygame.quit()
sys.exit()
