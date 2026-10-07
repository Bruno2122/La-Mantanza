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
andy00, andy01 = fn.cargabazar(ancho, alto)
puertabazar = pygame.Rect(int(ancho * 0.78), int(alto * 0.15), int(ancho * 0.18), int(alto * 0.35))
transicion = {"estado": "ninguno", "inicio": 0}
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
                            mapagraf = fn.cargarmapa(ancho, alto)
                            transicion = {"estado": "ninguno", "inicio": 0}
                            estado = "juego"
                        elif b["accion"] == "salir":
                            jugando = False
            elif estado == "derrota":
                for b in botonesderrota:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            jugdatos = fn.crearjugador(ancho, alto)
                            mapagraf = fn.cargarmapa(ancho, alto)
                            transicion = {"estado": "ninguno", "inicio": 0}
                            estado = "juego"
                        elif b["accion"] == "menu":
                            estado = "menu"
    if estado == "menu":
        fondosurf = fn.framevideo(video, ancho, alto)
        fn.dibujar(pantalla, fondosurf, panelizq, panelder, anchopanel, t1, t2, rect1, rect2, botones, fuentebtn, mouse)
    elif estado == "juego":
        ahora = pygame.time.get_ticks()
        if transicion["estado"] == "negro":
            pantalla.fill((0, 0, 0))
            if ahora - transicion["inicio"] >= 500:
                transicion["estado"] = "andy00"
                transicion["inicio"] = ahora
                mapagraf = andy00
        elif transicion["estado"] == "andy00":
            if ahora - transicion["inicio"] >= 1000:
                transicion["estado"] = "andy01"
                mapagraf = andy01
            fn.dibujarjuego(pantalla, mapagraf, jugdatos, vidas, enemigos)
        else:
            fn.moverjugador(jugdatos, teclas, ancho, alto)
            fn.recibirdaño(jugdatos, enemigos)

            if transicion["estado"] == "ninguno" and jugdatos["rect"].colliderect(puertabazar):
                transicion["estado"] = "negro"
                transicion["inicio"] = ahora
            else:
                if jugdatos["vida"] <= 0:
                    estado = "derrota"
                elif jugdatos["rect"].right >= ancho:
                    estado = "continuara"
                else:
                    fn.dibujarjuego(pantalla, mapagraf, jugdatos, vidas, enemigos)
    elif estado == "continuara":
        fn.dcontinuara(pantalla, icontinuara)
    elif estado == "derrota":
        fn.dibujarperdida(pantalla, jugdatos, mapagraf, bfuentetitulo, bfontederrota, botonesderrota, mouse)
    pygame.display.flip()
    reloj.tick(60)
video.release()
pygame.quit()
sys.exit()
