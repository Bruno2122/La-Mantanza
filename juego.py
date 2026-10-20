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
andy00, andy01, andy02, andy03 = fn.cargabazar(ancho, alto)
mira = fn.cargarmira(alto)
iconos_recursos = fn.cargariconosrecursos(alto)
fuente_compra = pygame.font.Font(None, max(24, int(alto * 0.035)))
puertabazar = fn.crearpuerta(ancho, alto)
transicion = {"estado": "ninguno", "inicio": 0}
mensaje_compra = ""
mensaje_pancho = ""
mensaje_pancho_hasta = 0
PRECIO_PISTOLA = 10
PRECIO_PANCHO = 5
BALAS_MAXIMAS = 6
balas = BALAS_MAXIMAS
recarga_hasta = 0
vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa = fn.cargardat(ancho, alto)
jugdatos = fn.crearjugador(ancho, alto)
jugdatos["vida"] = vida
jugdatos["pesos"] = pesos
fn.ajustapos(jugdatos, posicion_mc, ancho, alto, mapa)
vidas = fn.cargarvidas(alto)
bfuentetitulo, bfontederrota, botonesderrota = fn.bderrota(ancho, alto)
enemigos = fn.crearene(ancho, alto, min(oleada + 2, 20), oleada) if mapa == 2 else []
proys = []
rect_pancho_hud = None
reloj = pygame.time.Clock()
estado = "menu"
jugando = True

while jugando:
    ahora = pygame.time.get_ticks()
    if recarga_hasta and ahora >= recarga_hasta:
        balas = BALAS_MAXIMAS
        recarga_hasta = 0

    mouseventana = pygame.mouse.get_pos()
    mouse = (
        mouseventana[0] * ancho // ventana.get_width(),
        mouseventana[1] * alto // ventana.get_height()
    )
    teclas = pygame.key.get_pressed()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            vida = jugdatos["vida"]
            posicion_mc = jugdatos["rect"].topleft
            fn.guardardat(vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa)
            jugando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if estado in ("juego", "continuara", "bazar", "derrota", "victoria"):
                    estado = "menu"
                else:
                    jugando = False
                vida = jugdatos["vida"]
                posicion_mc = jugdatos["rect"].topleft
                fn.guardardat(vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa)
            elif evento.key == pygame.K_SPACE:
                if estado == "juego" and mapa == 1 and jugdatos["hitbox"].colliderect(puertabazar):
                    estado = "bazar"
                    mapa = "bazar"
                    transicion["estado"] = "negro"
                    transicion["inicio"] = pygame.time.get_ticks()
                elif estado == "bazar":
                    estado = "juego"
                    mapa = 1
                    transicion["estado"] = "ninguno"
                    mapagraf = fn.cargarmapa(ancho, alto)
                    jugdatos["rect"].top = puertabazar.bottom + int(alto * 0.02)
                    fn.ajustapos(jugdatos, jugdatos["rect"].topleft, ancho, alto, mapa)
            elif evento.key == pygame.K_BACKSPACE and estado == "bazar" and transicion["estado"] == "andy03":
                transicion["estado"] = "andy02"
                transicion["inicio"] = pygame.time.get_ticks()

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            mouseventana = evento.pos
            mouse = (
                mouseventana[0] * ancho // ventana.get_width(),
                mouseventana[1] * alto // ventana.get_height()
            )
            if estado in ("juego", "continuara") and rect_pancho_hud and rect_pancho_hud.collidepoint(mouse):
                if panchos > 0 and jugdatos["vida"] < 5:
                    panchos -= 1
                    jugdatos["vida"] = 5
                    mensaje_pancho = "Vida restaurada"
                elif jugdatos["vida"] >= 5:
                    mensaje_pancho = "Vida completa"
                else:
                    mensaje_pancho = "No tienes panchos"
                mensaje_pancho_hasta = pygame.time.get_ticks() + 1400
            elif estado == "menu":
                for b in botones:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa = fn.cargardat(ancho, alto)
                            jugdatos = fn.crearjugador(ancho, alto)
                            jugdatos["vida"] = vida
                            jugdatos["pesos"] = pesos
                            fn.ajustapos(jugdatos, posicion_mc, ancho, alto, mapa)
                            estado = "juego" if mapa == 1 else "continuara" if mapa == 2 else "bazar"
                            enemigos = fn.crearene(ancho, alto, min(oleada + 2, 20), oleada) if mapa == 2 else []
                            proys = []
                            transicion = {"estado": "andy01" if mapa == "bazar" else "ninguno", "inicio": pygame.time.get_ticks()}
                            mapagraf = fn.cargarmapa(ancho, alto)
                        elif b["accion"] == "reiniciar":
                            vida = 5
                            puntos = 0
                            oleada = 1
                            pesos = 0
                            panchos = 0
                            pistola = False
                            mapa = 1
                            jugdatos = fn.crearjugador(ancho, alto)
                            jugdatos["pesos"] = pesos
                            posicion_mc = jugdatos["rect"].topleft
                            enemigos = []
                            proys = []
                            transicion = {"estado": "ninguno", "inicio": 0}
                            mapagraf = fn.cargarmapa(ancho, alto)
                            fn.guardardat(vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa)
                            estado = "juego"
                        elif b["accion"] == "ventana":
                            ventana = fn.modopant(ancho, alto, ventana)
                            if ventana.get_flags() & pygame.FULLSCREEN:
                                b["texto"] = "VENTANA"
                            else:
                                b["texto"] = "PANTALLA COMPLETA"
                        elif b["accion"] == "salir":
                            jugando = False
            elif estado == "bazar":
                if transicion["estado"] == "andy02":
                    comprar = pygame.Rect(int(ancho * 0.62), int(alto * 0.56), int(ancho * 0.22), int(alto * 0.18))
                    salir = pygame.Rect(int(ancho * 0.62), int(alto * 0.78), int(ancho * 0.22), int(alto * 0.18))
                    if salir.collidepoint(mouse):
                        estado = "juego"
                        mapa = 1
                        transicion["estado"] = "ninguno"
                        mapagraf = fn.cargarmapa(ancho, alto)
                        jugdatos["rect"].top = puertabazar.bottom + int(alto * 0.02)
                        fn.ajustapos(jugdatos, jugdatos["rect"].topleft, ancho, alto, mapa)
                    elif comprar.collidepoint(mouse):
                        transicion["estado"] = "andy03"
                        transicion["inicio"] = pygame.time.get_ticks()
                        mensaje_compra = ""
                elif transicion["estado"] == "andy03":
                    comprar_pistola = pygame.Rect(int(ancho * 0.70), int(alto * 0.63), int(ancho * 0.17), int(alto * 0.20))
                    comprar_pancho = pygame.Rect(int(ancho * 0.69), int(alto * 0.31), int(ancho * 0.21), int(alto * 0.23))
                    volver = pygame.Rect(int(ancho * 0.02), int(alto * 0.02), int(ancho * 0.18), int(alto * 0.14))
                    if comprar_pancho.collidepoint(mouse):
                        if pesos >= PRECIO_PANCHO:
                            pesos -= PRECIO_PANCHO
                            panchos += 1
                            jugdatos["pesos"] = pesos
                            mensaje_compra = "Pancho comprado"
                        else:
                            mensaje_compra = f"Necesitas {PRECIO_PANCHO} pesos"
                    elif comprar_pistola.collidepoint(mouse):
                        if pistola:
                            mensaje_compra = "Ya tienes la pistola"
                        elif pesos >= PRECIO_PISTOLA:
                            pesos -= PRECIO_PISTOLA
                            pistola = True
                            jugdatos["pesos"] = pesos
                            mensaje_compra = "Pistola comprada"
                        else:
                            mensaje_compra = f"Necesitas {PRECIO_PISTOLA} pesos"
                    elif volver.collidepoint(mouse):
                        transicion["estado"] = "andy02"
                        transicion["inicio"] = pygame.time.get_ticks()
            elif estado == "juego" and transicion["estado"] == "ninguno":
                if pistola:
                    if balas > 0:
                        proy = fn.crearproypistola(jugdatos, mouse)
                        if proy is not None:
                            proys.append(proy)
                            balas -= 1
                            if balas == 0:
                                recarga_hasta = pygame.time.get_ticks() + 2000
                elif fn.iniciarataq(jugdatos):
                    proys.append(fn.crearproy(jugdatos))
            elif estado == "continuara":
                if pistola:
                    if balas > 0:
                        proy = fn.crearproypistola(jugdatos, mouse)
                        if proy is not None:
                            proys.append(proy)
                            balas -= 1
                            if balas == 0:
                                recarga_hasta = pygame.time.get_ticks() + 2000
                elif fn.iniciarataq(jugdatos):
                    proys.append(fn.crearproy(jugdatos))
            elif estado == "derrota":
                for b in botonesderrota:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            jugdatos = fn.crearjugador(ancho, alto)
                            vida = jugdatos["vida"]
                            puntos = 0
                            oleada = 1
                            pesos = 0
                            panchos = 0
                            pistola = False
                            mapa = 1
                            enemigos = []
                            proys = []
                            jugdatos["pesos"] = pesos
                            posicion_mc = jugdatos["rect"].topleft
                            transicion = {"estado": "ninguno", "inicio": 0}
                            mapagraf = fn.cargarmapa(ancho, alto)
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
            enemigos = fn.crearene(ancho, alto, min(oleada + 2, 20), oleada)
            proys = []
            jugdatos["rect"].left = 0
        else:
            fn.dibujarjuego(pantalla, mapagraf, jugdatos, vidas, [], proys=proys)
            rect_pancho_hud = fn.dibujarrecursos(pantalla, iconos_recursos, pesos, panchos, balas if pistola else None, BALAS_MAXIMAS)
            fn.dibujaroleada(pantalla, oleada)
            if pygame.time.get_ticks() < mensaje_pancho_hasta:
                texto_uso = fuente_compra.render(mensaje_pancho, True, (255, 255, 255))
                pantalla.blit(texto_uso, texto_uso.get_rect(topright=(ancho - int(alto * 0.02), rect_pancho_hud.bottom + 4)))
    elif estado == "bazar":
        ahora = pygame.time.get_ticks()

        if transicion["estado"] == "negro":
            pantalla.fill((0, 0, 0))
            if ahora - transicion["inicio"] >= 250:
                transicion["estado"] = "andy00"
                transicion["inicio"] = ahora
        elif transicion["estado"] == "andy00":
            if ahora - transicion["inicio"] >= 700:
                transicion["estado"] = "fade_andy01"
                transicion["inicio"] = ahora
            pantalla.blit(andy00, (0, 0))
        elif transicion["estado"] == "fade_andy01":
            progreso = min(1.0, (ahora - transicion["inicio"]) / 350.0)
            alpha = int(progreso * 255)

            pantalla.blit(andy00, (0, 0))
            andy01.set_alpha(alpha)
            pantalla.blit(andy01, (0, 0))

            if progreso >= 1.0:
                transicion["estado"] = "andy01"
                transicion["inicio"] = ahora
        elif transicion["estado"] == "andy01":
            andy01.set_alpha(255)
            pantalla.blit(andy01, (0, 0))
            if ahora - transicion["inicio"] >= 1000:
                transicion["estado"] = "andy02"
                transicion["inicio"] = ahora
        elif transicion["estado"] == "andy02":
            pantalla.blit(andy02, (0, 0))
        elif transicion["estado"] == "andy03":
            pantalla.blit(andy03, (0, 0))
            texto_saldo = fuente_compra.render(f"Pesos: {pesos}", True, (255, 255, 255))
            pantalla.blit(texto_saldo, texto_saldo.get_rect(center=(int(ancho * 0.80), int(alto * 0.22))))
            imagen_pancho = pygame.transform.smoothscale(iconos_recursos["pancho"], (int(alto * 0.075), int(alto * 0.075)))
            pantalla.blit(imagen_pancho, imagen_pancho.get_rect(center=(int(ancho * 0.80), int(alto * 0.39))))
            texto_pancho = fuente_compra.render(f"PANCHO - {PRECIO_PANCHO} PESOS", True, (255, 255, 255))
            pantalla.blit(texto_pancho, texto_pancho.get_rect(center=(int(ancho * 0.80), int(alto * 0.48))))
            texto_pistola = fuente_compra.render(f"PISTOLA - {PRECIO_PISTOLA} PESOS", True, (255, 255, 255))
            pantalla.blit(texto_pistola, texto_pistola.get_rect(center=(int(ancho * 0.79), int(alto * 0.60))))
            if mensaje_compra:
                color_mensaje = (255, 120, 120) if mensaje_compra.startswith("Necesitas") else (130, 255, 130)
                texto_mensaje = fuente_compra.render(mensaje_compra, True, color_mensaje)
                pantalla.blit(texto_mensaje, texto_mensaje.get_rect(center=(int(ancho * 0.50), int(alto * 0.86))))
    elif estado == "continuara":
        fn.actualizarataq(jugdatos)
        fn.moverjugador(jugdatos, teclas, ancho, alto, (0.29, 0.72))
        fn.actualizaene(enemigos, jugdatos, proys)
        fn.moverproy(proys, enemigos, ancho, alto, jugdatos)
        # La siguiente oleada empieza al cruzar mapa 1 y regresar al mapa 2.
        if jugdatos["rect"].right >= ancho and len([e for e in enemigos if e["vida"] > 0]) == 0:
            oleada_completada = oleada >= 20
            if oleada < 20:
                oleada += 1
            mapa = 1
            estado = "victoria" if oleada_completada else "juego"
            jugdatos["rect"].left = 0
            enemigos = []
            proys = []
            mapagraf = fn.cargarmapa(ancho, alto)
            fn.ajustapos(jugdatos, jugdatos["rect"].topleft, ancho, alto, mapa)
        elif jugdatos["vida"] <= 0:
            estado = "derrota"
            fn.dibujarperdida(pantalla, jugdatos, mapagraf2, bfuentetitulo, bfontederrota, botonesderrota, mouse)
        else:
            fn.dibujarjuego(pantalla, mapagraf2, jugdatos, vidas, enemigos, proys=proys)
            rect_pancho_hud = fn.dibujarrecursos(pantalla, iconos_recursos, pesos, panchos, balas if pistola else None, BALAS_MAXIMAS)
            fn.dibujaroleada(pantalla, oleada)
            if pygame.time.get_ticks() < mensaje_pancho_hasta:
                texto_uso = fuente_compra.render(mensaje_pancho, True, (255, 255, 255))
                pantalla.blit(texto_uso, texto_uso.get_rect(topright=(ancho - int(alto * 0.02), rect_pancho_hud.bottom + 4)))
    elif estado == "derrota":
        mapaderrota = mapagraf if mapa == 1 else mapagraf2
        fn.dibujarperdida(pantalla, jugdatos, mapaderrota, bfuentetitulo, bfontederrota, botonesderrota, mouse)
    elif estado == "victoria":
        fn.dibujarjuego(pantalla, mapagraf, jugdatos, vidas, [], proys=proys)
        capa = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
        capa.fill((0, 0, 0, 150))
        pantalla.blit(capa, (0, 0))
        texto = bfuentetitulo.render("COMPLETASTE LAS 20 OLEADAS", True, (255, 255, 255))
        pantalla.blit(texto, texto.get_rect(center=(ancho // 2, alto // 2)))
        subvictoria = bfontederrota.render("GG fucking Easy", True, (255, 255, 255))
        pantalla.blit(subvictoria, subvictoria.get_rect(center=(ancho // 2, int(alto * 0.60))))

    mostrar_mira = pistola and estado in ("juego", "continuara")
    pygame.mouse.set_visible(not mostrar_mira)
    if mostrar_mira:
        pantalla.blit(mira, mira.get_rect(center=mouse))

    vida = jugdatos["vida"]
    posicion_mc = jugdatos["rect"].topleft
    ventana.blit(pygame.transform.smoothscale(pantalla, ventana.get_size()), (0, 0))
    pygame.display.flip()
    reloj.tick(60)

    # Guardar datos en cada ciclo (opcional, puedes moverlo a eventos importantes)
    pesos = jugdatos.get("pesos", pesos)
    fn.guardardat(vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa)

video.release()
pygame.quit()
sys.exit()
