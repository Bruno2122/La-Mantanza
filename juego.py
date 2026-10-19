import pygame
import sys
import cv2
import funciones as fn

pygame.init()

ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
ancho, alto = ventana.get_size()
pantalla = pygame.Surface((ancho, alto))
pygame.display.set_caption("La Matanza Avanza")

video = cv2.VideoCapture("F/trenfondo.mp4")
if not video.isOpened():
    video.release()
    video = cv2.VideoCapture("trenfondo.mp4")
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
            if evento.key == pygame.K_ESCAPE:
                if estado in ("juego", "continuara", "derrota"):
                    estado = "menu"
                else:
                    jugando = False

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            mouseventana = evento.pos
            mouse = (
                mouseventana[0] * ancho // ventana.get_width(),
                mouseventana[1] * alto // ventana.get_height()
            )
            if estado == "menu":
                for b in botones:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            jugdatos = fn.crearjugador(ancho, alto)
                            estado = "juego"
                        elif b["accion"] == "ventana":
                            ventana = fn.modopant(ancho, alto, ventana)
                            if ventana.get_flags() & pygame.FULLSCREEN:
                                b["texto"] = "VENTANA"
                            else:
                                b["texto"] = "PANTALLA COMPLETA"
                        elif b["accion"] == "salir":
                            jugando = False
            elif estado in ("juego", "continuara"):
                fn.iniciarataq(jugdatos)
            elif estado == "derrota":
                for b in botonesderrota:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            jugdatos = fn.crearjugador(ancho, alto)
                            estado = "juego"
                        elif b["accion"] == "menu":
                            estado = "menu"

    if estado == "menu":
        fondosurf = fn.framevideo(video, ancho, alto)
        fn.dibujar(pantalla, fondosurf, panelizq, panelder, anchopanel, t1, t2, rect1, rect2, botones, fuentebtn, mouse)
    elif estado == "juego":
        fn.actualizarataq(jugdatos)
        fn.moverjugador(jugdatos, teclas, ancho, alto)
        fn.recibirdaño(jugdatos, enemigos)
        if jugdatos["vida"] <= 0:
            estado = "derrota"
        elif jugdatos["rect"].right >= ancho:
            estado = "continuara"
            jugdatos["rect"].left = 0
        else:
            fn.dibujarjuego(pantalla, mapagraf, jugdatos, vidas, enemigos)
    elif estado == "continuara":
        fn.actualizarataq(jugdatos)
        fn.moverjugador(jugdatos, teclas, ancho, alto, (0.29, 0.72))
        fn.dibujarjuego(pantalla, mapagraf2, jugdatos, vidas, [])
    elif estado == "derrota":
        fn.dibujarperdida(pantalla, jugdatos, mapagraf, bfuentetitulo, bfontederrota, botonesderrota, mouse)

    ventana.blit(pygame.transform.smoothscale(pantalla, ventana.get_size()), (0, 0))
    pygame.display.flip()
    reloj.tick(60)

video.release()
pygame.quit()
sys.exit()
