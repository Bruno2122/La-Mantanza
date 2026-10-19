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
vida, puntos, oleada, posicion_mc, mapa = fn.cargardat(ancho, alto)
jugdatos = fn.crearjugador(ancho, alto)
jugdatos["vida"] = vida
fn.ajustapos(jugdatos, posicion_mc, ancho, alto, mapa)
vidas = fn.cargarvidas(alto)
bfuentetitulo, bfontederrota, botonesderrota = fn.bderrota(ancho, alto)
enemigos = fn.crearene(ancho, alto) if mapa == 2 else []
proys = []
reloj = pygame.time.Clock()
estado = "menu"
jugando = True

while jugando:
    mouse = pygame.mouse.get_pos()
    teclas = pygame.key.get_pressed()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            vida = jugdatos["vida"]
            posicion_mc = jugdatos["rect"].topleft
            fn.guardardat(vida, puntos, oleada, posicion_mc, mapa)
            jugando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if estado in ("juego", "continuara", "derrota"):
                    estado = "menu"
                else:
                    jugando = False
                vida = jugdatos["vida"]
                posicion_mc = jugdatos["rect"].topleft
                fn.guardardat(vida, puntos, oleada, posicion_mc, mapa)

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
                            vida, puntos, oleada, posicion_mc, mapa = fn.cargardat(ancho, alto)
                            jugdatos = fn.crearjugador(ancho, alto)
                            jugdatos["vida"] = vida
                            fn.ajustapos(jugdatos, posicion_mc, ancho, alto, mapa)
                            estado = "juego" if mapa == 1 else "continuara"
                            enemigos = fn.crearene(ancho, alto) if mapa == 2 else []
                            proys = []
                        elif b["accion"] == "reiniciar":
                            vida = 5
                            puntos = 0
                            oleada = 1
                            mapa = 1
                            jugdatos = fn.crearjugador(ancho, alto)
                            posicion_mc = jugdatos["rect"].topleft
                            enemigos = []
                            proys = []
                            fn.guardardat(vida, puntos, oleada, posicion_mc, mapa)
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
                if fn.iniciarataq(jugdatos):
                    proys.append(fn.crearproy(jugdatos))
            elif estado == "derrota":
                for b in botonesderrota:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            jugdatos = fn.crearjugador(ancho, alto)
                            vida = jugdatos["vida"]
                            puntos = 0
                            oleada = 1
                            mapa = 1
                            enemigos = []
                            proys = []
                            posicion_mc = jugdatos["rect"].topleft
                            estado = "juego"
                        elif b["accion"] == "menu":
                            estado = "menu"

    if estado == "menu":
        fondosurf = fn.framevideo(video, ancho, alto)
        fn.dibujar(pantalla, fondosurf, panelizq, panelder, anchopanel, t1, t2, rect1, rect2, botones, fuentebtn, mouse)
    elif estado == "juego":
        fn.actualizarataq(jugdatos)
        fn.moverjugador(jugdatos, teclas, ancho, alto)
        fn.moverproy(proys, [], ancho, alto)
        fn.recibirdaño(jugdatos, [])
        if jugdatos["vida"] <= 0:
            estado = "derrota"
            fn.dibujarperdida(pantalla, jugdatos, mapagraf, bfuentetitulo, bfontederrota, botonesderrota, mouse)
        elif jugdatos["rect"].right >= ancho:
            estado = "continuara"
            mapa = 2
            enemigos = fn.crearene(ancho, alto)
            proys = []
            jugdatos["rect"].left = 0
        else:
            fn.dibujarjuego(pantalla, mapagraf, jugdatos, vidas, [])
    elif estado == "continuara":
        fn.actualizarataq(jugdatos)
        fn.moverjugador(jugdatos, teclas, ancho, alto, (0.29, 0.72))
        fn.actualizaene(enemigos, jugdatos, proys)
        fn.moverproy(proys, enemigos, ancho, alto, jugdatos)
        if jugdatos["vida"] <= 0:
            estado = "derrota"
            fn.dibujarperdida(pantalla, jugdatos, mapagraf2, bfuentetitulo, bfontederrota, botonesderrota, mouse)
        else:
            fn.dibujarjuego(pantalla, mapagraf2, jugdatos, vidas, enemigos)
    elif estado == "derrota":
        mapaderrota = mapagraf if mapa == 1 else mapagraf2
        fn.dibujarperdida(pantalla, jugdatos, mapaderrota, bfuentetitulo, bfontederrota, botonesderrota, mouse)

    vida = jugdatos["vida"]
    posicion_mc = jugdatos["rect"].topleft
    ventana.blit(pygame.transform.smoothscale(pantalla, ventana.get_size()), (0, 0))
    pygame.display.flip()
    reloj.tick(60)

video.release()
pygame.quit()
sys.exit()
