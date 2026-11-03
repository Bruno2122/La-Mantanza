import pygame
import sys
import cv2
import funciones as fn

pygame.init()

ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
ancho, alto = ventana.get_size()
pantalla = pygame.Surface((ancho, alto))
pantalla_ventana = pygame.Surface(ventana.get_size())
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
ancho_mapa2 = mapagraf2.get_width()
alto_mapa2 = mapagraf2.get_height()
cam_x = 0
cam_y = 0
andy00, andy01, andy02, andy03 = fn.cargabazar(ancho, alto)
mira = fn.cargarmira(alto)
iconos_recursos = fn.cargariconosrecursos(alto)
tam_pancho = int(alto * 0.11)
pancho_tienda = pygame.transform.smoothscale(iconos_recursos["pancho"], (tam_pancho, tam_pancho))
img_speed_full = iconos_recursos["speed_full"]
alto_speed_tienda = int(alto * 0.135)
ancho_speed_tienda = max(24, int(img_speed_full.get_width() * (alto_speed_tienda / img_speed_full.get_height())))
speed_tienda = pygame.transform.smoothscale(img_speed_full, (ancho_speed_tienda, alto_speed_tienda))
fuente_compra = pygame.font.Font(None, max(24, int(alto * 0.035)))
fuente_compra_chica = pygame.font.Font(None, max(18, int(alto * 0.026)))
puertabazar = fn.crearpuerta(ancho, alto)
transicion = {"estado": "ninguno", "inicio": 0}
mensaje_compra = ""
carrito_pistola = 0
carrito_panchos = 0
carrito_speeds = 0
mensaje_pancho = ""
mensaje_pancho_hasta = 0
PRECIO_PISTOLA = 10
PRECIO_PANCHO = 75
PRECIO_SPEED = 250
BALAS_MAXIMAS =10
balas = BALAS_MAXIMAS
recarga_hasta = 0
vida, escudo, puntos, oleada, pesos, panchos, speeds, pistola, posicion_mc, mapa = fn.cargardat(ancho, alto)
jugdatos = fn.crearjugador(ancho, alto)
jugdatos["vida"] = vida
jugdatos["escudo"] = escudo
jugdatos["pesos"] = pesos
fn.cambiar_escala_jugador(jugdatos, ancho, alto, mapa=mapa)
w_ini = ancho_mapa2 if mapa == 2 else ancho
h_ini = alto_mapa2 if mapa == 2 else alto
fn.ajustapos(jugdatos, posicion_mc, w_ini, h_ini, mapa)
vidas = fn.cargarvidas(alto)
escudos = fn.cargarescudos(alto)
bfuentetitulo, bfontederrota, botonesderrota = fn.bderrota(ancho, alto)
enemigos = fn.crearene(ancho_mapa2, alto_mapa2, min(8 + oleada * 3, 40), oleada, alto_pantalla=alto) if mapa == 2 else []
proys = []
rect_pancho_hud = None
rect_speed_hud = None
reloj = pygame.time.Clock()
estado = "menu"
ultimo_guardado = pygame.time.get_ticks()
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
            escudo = jugdatos.get("escudo", 0)
            posicion_mc = jugdatos["rect"].topleft
            fn.guardardat(vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa, escudo=escudo, speeds=speeds)
            jugando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if estado in ("juego", "continuara", "bazar", "derrota", "victoria"):
                    estado = "menu"
                else:
                    jugando = False
                vida = jugdatos["vida"]
                escudo = jugdatos.get("escudo", 0)
                posicion_mc = jugdatos["rect"].topleft
                fn.guardardat(vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa, escudo=escudo, speeds=speeds)
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
                    jugdatos["rect"].centerx = puertabazar.centerx
                    jugdatos["rect"].top = int(alto * 0.36)
                    fn.ajustapos(jugdatos, jugdatos["rect"].topleft, ancho, alto, mapa)
            elif evento.key == pygame.K_BACKSPACE and estado == "bazar" and transicion["estado"] == "andy03":
                transicion["estado"] = "andy02"
                transicion["inicio"] = pygame.time.get_ticks()
                carrito_pistola = 0
                carrito_panchos = 0
                carrito_speeds = 0

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 3:
            mouseventana = evento.pos
            mouse = (
                mouseventana[0] * ancho // ventana.get_width(),
                mouseventana[1] * alto // ventana.get_height()
            )
            if estado == "bazar" and transicion["estado"] == "andy03":
                slot_pistola = pygame.Rect(int(ancho * 0.145), int(alto * 0.210), int(ancho * 0.115), int(alto * 0.175))
                slot_pancho = pygame.Rect(int(ancho * 0.334), int(alto * 0.210), int(ancho * 0.121), int(alto * 0.178))
                slot_speed = pygame.Rect(int(ancho * 0.529), int(alto * 0.210), int(ancho * 0.128), int(alto * 0.178))
                if slot_pancho.collidepoint(mouse) and carrito_panchos > 0:
                    carrito_panchos -= 1
                    mensaje_compra = ""
                elif slot_speed.collidepoint(mouse) and carrito_speeds > 0:
                    carrito_speeds -= 1
                    mensaje_compra = ""
                elif slot_pistola.collidepoint(mouse) and carrito_pistola > 0:
                    carrito_pistola = 0
                    mensaje_compra = ""

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
                    fn.guardardat(jugdatos["vida"], puntos, oleada, pesos, panchos, pistola, jugdatos["rect"].topleft, mapa, escudo=jugdatos.get("escudo", 0), speeds=speeds)
                elif jugdatos["vida"] >= 5:
                    mensaje_pancho = "Vida completa"
                else:
                    mensaje_pancho = "No tienes panchos"
                mensaje_pancho_hasta = pygame.time.get_ticks() + 1400
            elif estado in ("juego", "continuara") and rect_speed_hud and rect_speed_hud.collidepoint(mouse):
                if speeds > 0 and jugdatos.get("escudo", 0) < 3:
                    speeds -= 1
                    jugdatos["escudo"] = min(3, jugdatos.get("escudo", 0) + 1)
                    mensaje_pancho = "+1 Barra de Escudo"
                    fn.guardardat(jugdatos["vida"], puntos, oleada, pesos, panchos, pistola, jugdatos["rect"].topleft, mapa, escudo=jugdatos.get("escudo", 0), speeds=speeds)
                elif jugdatos.get("escudo", 0) >= 3:
                    mensaje_pancho = "Escudo al maximo"
                else:
                    mensaje_pancho = "No tienes Speed"
                mensaje_pancho_hasta = pygame.time.get_ticks() + 1400
            elif estado == "menu":
                for b in botones:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            vida, escudo, puntos, oleada, pesos, panchos, speeds, pistola, posicion_mc, mapa = fn.cargardat(ancho, alto)
                            jugdatos = fn.crearjugador(ancho, alto)
                            jugdatos["vida"] = vida
                            jugdatos["escudo"] = escudo
                            jugdatos["pesos"] = pesos
                            fn.cambiar_escala_jugador(jugdatos, ancho, alto, mapa=mapa)
                            w_mapa = ancho_mapa2 if mapa == 2 else ancho
                            h_mapa = alto_mapa2 if mapa == 2 else alto
                            fn.ajustapos(jugdatos, posicion_mc, w_mapa, h_mapa, mapa)
                            estado = "juego" if mapa == 1 else "continuara" if mapa == 2 else "bazar"
                            enemigos = fn.crearene(ancho_mapa2, alto_mapa2, min(8 + oleada * 3, 40), oleada, alto_pantalla=alto) if mapa == 2 else []
                            proys = []
                            transicion = {"estado": "andy01" if mapa == "bazar" else "ninguno", "inicio": pygame.time.get_ticks()}
                            mapagraf = fn.cargarmapa(ancho, alto)
                        elif b["accion"] == "reiniciar":
                            vida = 5
                            escudo = 0
                            puntos = 0
                            oleada = 1
                            pesos = 0
                            panchos = 0
                            speeds = 0
                            pistola = False
                            mapa = 1
                            jugdatos = fn.crearjugador(ancho, alto)
                            jugdatos["escudo"] = escudo
                            jugdatos["pesos"] = pesos
                            posicion_mc = jugdatos["rect"].topleft
                            enemigos = []
                            proys = []
                            transicion = {"estado": "ninguno", "inicio": 0}
                            mapagraf = fn.cargarmapa(ancho, alto)
                            fn.guardardat(vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa, escudo=escudo, speeds=speeds)
                            estado = "juego"
                        elif b["accion"] == "ventana":
                            ventana = fn.modopant(ancho, alto, ventana)
                            pantalla_ventana = pygame.Surface(ventana.get_size())
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
                        jugdatos["rect"].centerx = puertabazar.centerx
                        jugdatos["rect"].top = int(alto * 0.36)
                        fn.ajustapos(jugdatos, jugdatos["rect"].topleft, ancho, alto, mapa)
                    elif comprar.collidepoint(mouse):
                        transicion["estado"] = "andy03"
                        transicion["inicio"] = pygame.time.get_ticks()
                        mensaje_compra = ""
                        carrito_pistola = 0
                        carrito_panchos = 0
                        carrito_speeds = 0
                elif transicion["estado"] == "andy03":
                    slot_pistola = pygame.Rect(int(ancho * 0.145), int(alto * 0.210), int(ancho * 0.115), int(alto * 0.175))
                    slot_pancho = pygame.Rect(int(ancho * 0.334), int(alto * 0.210), int(ancho * 0.121), int(alto * 0.178))
                    slot_speed = pygame.Rect(int(ancho * 0.529), int(alto * 0.210), int(ancho * 0.128), int(alto * 0.178))
                    btn_confirmar = pygame.Rect(int(ancho * 0.713), int(alto * 0.605), int(ancho * 0.145), int(alto * 0.173))
                    btn_vaciar = pygame.Rect(int(ancho * 0.56), int(alto * 0.65), int(ancho * 0.13), int(alto * 0.08))
                    volver = pygame.Rect(int(ancho * 0.02), int(alto * 0.02), int(ancho * 0.18), int(alto * 0.14))

                    if slot_pistola.collidepoint(mouse):
                        if pistola:
                            mensaje_compra = "Ya tienes la pistola (solo 1 vez)"
                        else:
                            carrito_pistola = 0 if carrito_pistola else 1
                            mensaje_compra = ""
                    elif slot_pancho.collidepoint(mouse):
                        carrito_panchos += 1
                        mensaje_compra = ""
                    elif slot_speed.collidepoint(mouse):
                        carrito_speeds += 1
                        mensaje_compra = ""
                    elif btn_vaciar.collidepoint(mouse):
                        carrito_pistola = 0
                        carrito_panchos = 0
                        carrito_speeds = 0
                        mensaje_compra = "Seleccion vaciada"
                    elif btn_confirmar.collidepoint(mouse):
                        costo_total = (PRECIO_PISTOLA if carrito_pistola else 0) + carrito_panchos * PRECIO_PANCHO + carrito_speeds * PRECIO_SPEED
                        if carrito_pistola == 0 and carrito_panchos == 0 and carrito_speeds == 0:
                            mensaje_compra = "Toca los iconos para agregar items"
                        elif pesos >= costo_total:
                            pesos -= costo_total
                            jugdatos["pesos"] = pesos
                            if carrito_pistola:
                                pistola = True
                            panchos += carrito_panchos
                            speeds += carrito_speeds
                            carrito_pistola = 0
                            carrito_panchos = 0
                            carrito_speeds = 0
                            mensaje_compra = "¡Compra confirmada!"
                            fn.guardardat(jugdatos["vida"], puntos, oleada, pesos, panchos, pistola, jugdatos["rect"].topleft, mapa, escudo=jugdatos.get("escudo", 0), speeds=speeds)
                        else:
                            mensaje_compra = f"Necesitas {costo_total} pesos (tienes {pesos})"
                    elif volver.collidepoint(mouse):
                        transicion["estado"] = "andy02"
                        transicion["inicio"] = pygame.time.get_ticks()
                        carrito_pistola = 0
                        carrito_panchos = 0
                        carrito_speeds = 0
            elif estado == "juego" and transicion["estado"] == "ninguno":
                if pistola:
                    if balas > 0:
                        proy = fn.crearproypistola(jugdatos, mouse)
                        if proy is not None:
                            proys.append(proy)
                            balas -= 1
                            if balas == 0:
                                recarga_hasta = pygame.time.get_ticks() + 2000
                elif fn.iniciarataq(jugdatos, mouse):
                    proys.append(fn.crearproy(jugdatos))
            elif estado == "continuara":
                mouse_mundo = (mouse[0] + cam_x, mouse[1] + cam_y)
                if pistola:
                    if balas > 0:
                        proy = fn.crearproypistola(jugdatos, mouse_mundo)
                        if proy is not None:
                            proys.append(proy)
                            balas -= 1
                            if balas == 0:
                                recarga_hasta = pygame.time.get_ticks() + 2000
                elif fn.iniciarataq(jugdatos, mouse_mundo):
                    proys.append(fn.crearproy(jugdatos))
            elif estado == "derrota":
                for b in botonesderrota:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            jugdatos = fn.crearjugador(ancho, alto)
                            fn.cambiar_escala_jugador(jugdatos, ancho, alto, mapa=1)
                            vida = jugdatos["vida"]
                            escudo = 0
                            jugdatos["escudo"] = escudo
                            puntos = 0
                            oleada = 1
                            pesos = 0
                            panchos = 0
                            speeds = 0
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
        fn.moverjugador(jugdatos, teclas, ancho, alto, mapa=1)
        fn.moverproy(proys, [], ancho, alto)
        fn.recibirdaño(jugdatos, [])

        if jugdatos["vida"] <= 0:
            estado = "derrota"
            fn.dibujarperdida(pantalla, jugdatos, mapagraf, bfuentetitulo, bfontederrota, botonesderrota, mouse)
        elif jugdatos["rect"].right >= ancho:
            estado = "continuara"
            mapa = 2
            fn.cambiar_escala_jugador(jugdatos, ancho, alto, mapa=2)
            enemigos = fn.crearene(ancho_mapa2, alto_mapa2, min(8 + oleada * 3, 40), oleada, alto_pantalla=alto)
            proys = []
            jugdatos["rect"].left = 0
            jugdatos["rect"].centery = int(jugdatos["rect"].centery * (alto_mapa2 / alto))
            fn.ajustapos(jugdatos, jugdatos["rect"].topleft, ancho_mapa2, alto_mapa2, mapa)
        else:
            fn.dibujarjuego(pantalla, mapagraf, jugdatos, vidas, [], proys=proys, escudos=escudos)
            if jugdatos["hitbox"].colliderect(puertabazar):
                txt_bazar = fuente_compra.render("[ESPACIO] BAZAR", True, (255, 255, 255))
                rect_tb = txt_bazar.get_rect(center=(puertabazar.centerx, puertabazar.top - 14))
                pygame.draw.rect(pantalla, (0, 0, 0, 180), rect_tb.inflate(14, 8), border_radius=4)
                pantalla.blit(txt_bazar, rect_tb)
            rect_pancho_hud, rect_speed_hud = fn.dibujarrecursos(pantalla, iconos_recursos, pesos, panchos, balas if pistola else None, BALAS_MAXIMAS, speeds=speeds)
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

            slot_pistola = pygame.Rect(int(ancho * 0.145), int(alto * 0.210), int(ancho * 0.115), int(alto * 0.175))
            slot_pancho = pygame.Rect(int(ancho * 0.334), int(alto * 0.210), int(ancho * 0.121), int(alto * 0.178))
            slot_speed = pygame.Rect(int(ancho * 0.529), int(alto * 0.210), int(ancho * 0.128), int(alto * 0.178))
            btn_confirmar = pygame.Rect(int(ancho * 0.713), int(alto * 0.605), int(ancho * 0.145), int(alto * 0.173))
            btn_vaciar = pygame.Rect(int(ancho * 0.56), int(alto * 0.65), int(ancho * 0.13), int(alto * 0.08))

            # Dibujar iconos de pancho y speed en la segunda y tercera casilla de la tienda
            pantalla.blit(pancho_tienda, pancho_tienda.get_rect(center=slot_pancho.center))
            pantalla.blit(speed_tienda, speed_tienda.get_rect(center=slot_speed.center))

            # Bordes interactivos / selección en las casillas
            if pistola:
                overlay_comprada = pygame.Surface(slot_pistola.size, pygame.SRCALPHA)
                overlay_comprada.fill((0, 0, 0, 150))
                pantalla.blit(overlay_comprada, slot_pistola.topleft)
                pygame.draw.rect(pantalla, (120, 120, 120), slot_pistola, 3, border_radius=6)
                txt_comp = fuente_compra_chica.render("COMPRADA", True, (255, 200, 100))
                pantalla.blit(txt_comp, txt_comp.get_rect(center=slot_pistola.center))
            elif carrito_pistola > 0:
                pygame.draw.rect(pantalla, (80, 255, 100), slot_pistola, 4, border_radius=6)
                badge_p = fuente_compra.render("x1", True, (80, 255, 100))
                pantalla.blit(badge_p, badge_p.get_rect(bottomright=(slot_pistola.right - 6, slot_pistola.bottom - 4)))
            elif slot_pistola.collidepoint(mouse):
                pygame.draw.rect(pantalla, (255, 255, 140), slot_pistola, 3, border_radius=6)

            if carrito_panchos > 0:
                pygame.draw.rect(pantalla, (80, 255, 100), slot_pancho, 4, border_radius=6)
                badge_pan = fuente_compra.render(f"x{carrito_panchos}", True, (80, 255, 100))
                pantalla.blit(badge_pan, badge_pan.get_rect(bottomright=(slot_pancho.right - 6, slot_pancho.bottom - 4)))
            elif slot_pancho.collidepoint(mouse):
                pygame.draw.rect(pantalla, (255, 255, 140), slot_pancho, 3, border_radius=6)

            if carrito_speeds > 0:
                pygame.draw.rect(pantalla, (80, 255, 100), slot_speed, 4, border_radius=6)
                badge_spd = fuente_compra.render(f"x{carrito_speeds}", True, (80, 255, 100))
                pantalla.blit(badge_spd, badge_spd.get_rect(bottomright=(slot_speed.right - 6, slot_speed.bottom - 4)))
            elif slot_speed.collidepoint(mouse):
                pygame.draw.rect(pantalla, (255, 255, 140), slot_speed, 3, border_radius=6)

            # Precios y etiquetas debajo de cada casilla
            lbl_pistola = fuente_compra_chica.render("PISTOLA (Única)", True, (255, 255, 255))
            precio_pistola_txt = fuente_compra_chica.render("AGOTADO" if pistola else f"${PRECIO_PISTOLA}", True, (200, 200, 200) if pistola else (255, 230, 100))
            pantalla.blit(lbl_pistola, lbl_pistola.get_rect(center=(slot_pistola.centerx, slot_pistola.bottom + int(alto * 0.03))))
            pantalla.blit(precio_pistola_txt, precio_pistola_txt.get_rect(center=(slot_pistola.centerx, slot_pistola.bottom + int(alto * 0.065))))

            lbl_pancho = fuente_compra_chica.render("PANCHO (+Vida)", True, (255, 255, 255))
            precio_pancho_txt = fuente_compra_chica.render(f"${PRECIO_PANCHO} c/u", True, (255, 230, 100))
            ayuda_pancho = fuente_compra_chica.render("(Clic izq +1 / der -1)", True, (210, 210, 210))
            pantalla.blit(lbl_pancho, lbl_pancho.get_rect(center=(slot_pancho.centerx, slot_pancho.bottom + int(alto * 0.03))))
            pantalla.blit(precio_pancho_txt, precio_pancho_txt.get_rect(center=(slot_pancho.centerx, slot_pancho.bottom + int(alto * 0.065))))
            pantalla.blit(ayuda_pancho, ayuda_pancho.get_rect(center=(slot_pancho.centerx, slot_pancho.bottom + int(alto * 0.098))))

            lbl_speed = fuente_compra_chica.render("SPEED (+1 Escudo)", True, (255, 255, 255))
            precio_speed_txt = fuente_compra_chica.render(f"${PRECIO_SPEED} c/u", True, (255, 230, 100))
            ayuda_speed = fuente_compra_chica.render("(Clic izq +1 / der -1)", True, (210, 210, 210))
            pantalla.blit(lbl_speed, lbl_speed.get_rect(center=(slot_speed.centerx, slot_speed.bottom + int(alto * 0.03))))
            pantalla.blit(precio_speed_txt, precio_speed_txt.get_rect(center=(slot_speed.centerx, slot_speed.bottom + int(alto * 0.065))))
            pantalla.blit(ayuda_speed, ayuda_speed.get_rect(center=(slot_speed.centerx, slot_speed.bottom + int(alto * 0.098))))

            # Panel de resumen de compra y saldo a la derecha
            costo_total = carrito_pistola * PRECIO_PISTOLA + carrito_panchos * PRECIO_PANCHO + carrito_speeds * PRECIO_SPEED
            texto_saldo = fuente_compra.render(f"Tus Pesos: ${pesos}", True, (255, 255, 255))
            pantalla.blit(texto_saldo, texto_saldo.get_rect(center=(int(ancho * 0.78), int(alto * 0.25))))

            resumen_items = f"Pistola x{carrito_pistola} | Panchos x{carrito_panchos} | Speed x{carrito_speeds}"
            txt_resumen = fuente_compra_chica.render(resumen_items, True, (230, 230, 230))
            pantalla.blit(txt_resumen, txt_resumen.get_rect(center=(int(ancho * 0.75), int(alto * 0.46))))

            color_total = (255, 110, 110) if costo_total > pesos else (120, 255, 140)
            txt_total = fuente_compra.render(f"Total a confirmar: ${costo_total}", True, color_total)
            pantalla.blit(txt_total, txt_total.get_rect(center=(int(ancho * 0.75), int(alto * 0.53))))

            # Resaltar botón COMPRAR al pasar el mouse o tener items
            if btn_confirmar.collidepoint(mouse):
                pygame.draw.rect(pantalla, (255, 255, 255), btn_confirmar, 3, border_radius=10)

            # Botón para vaciar selección si hay items acumulados
            if carrito_pistola > 0 or carrito_panchos > 0 or carrito_speeds > 0:
                color_vaciar = (170, 60, 60) if btn_vaciar.collidepoint(mouse) else (120, 40, 40)
                pygame.draw.rect(pantalla, color_vaciar, btn_vaciar, border_radius=8)
                pygame.draw.rect(pantalla, (255, 200, 200), btn_vaciar, 2, border_radius=8)
                txt_vaciar = fuente_compra_chica.render("VACIAR", True, (255, 255, 255))
                pantalla.blit(txt_vaciar, txt_vaciar.get_rect(center=btn_vaciar.center))

            if mensaje_compra:
                es_error = mensaje_compra.startswith("Necesitas") or mensaje_compra.startswith("Selecciona") or mensaje_compra.startswith("Toca") or mensaje_compra.startswith("Ya ")
                color_mensaje = (255, 120, 120) if es_error else (130, 255, 130)
                texto_mensaje = fuente_compra.render(mensaje_compra, True, color_mensaje)
                rect_msg = texto_mensaje.get_rect(center=(int(ancho * 0.50), int(alto * 0.85)))
                pygame.draw.rect(pantalla, (0, 0, 0, 190), rect_msg.inflate(20, 10), border_radius=6)
                pantalla.blit(texto_mensaje, rect_msg)
    elif estado == "continuara":
        fn.actualizarataq(jugdatos)
        obstaculos_m2 = fn.obtener_obstaculos(2, ancho_mapa2, alto_mapa2)
        fn.moverjugador(jugdatos, teclas, ancho_mapa2, alto_mapa2, mapa=2, obstaculos=obstaculos_m2)
        fn.actualizaene(enemigos, jugdatos, proys, obstaculos=obstaculos_m2)
        fn.moverproy(proys, enemigos, ancho_mapa2, alto_mapa2, jugdatos)

        cam_x = max(0, min(jugdatos["rect"].centerx - ancho // 2, ancho_mapa2 - ancho))
        cam_y = max(0, min(jugdatos["rect"].centery - alto // 2, alto_mapa2 - alto))

        # La siguiente oleada empieza al cruzar mapa 1 y regresar al mapa 2.
        if jugdatos["rect"].right >= ancho_mapa2 and len([e for e in enemigos if e["vida"] > 0]) == 0:
            oleada_completada = oleada >= 20
            if oleada < 20:
                oleada += 1
            mapa = 1
            estado = "victoria" if oleada_completada else "juego"
            fn.cambiar_escala_jugador(jugdatos, ancho, alto, mapa=1)
            jugdatos["rect"].left = 0
            jugdatos["rect"].centery = int(jugdatos["rect"].centery * (alto / alto_mapa2))
            enemigos = []
            proys = []
            mapagraf = fn.cargarmapa(ancho, alto)
            fn.ajustapos(jugdatos, jugdatos["rect"].topleft, ancho, alto, mapa)
        elif jugdatos["vida"] <= 0:
            estado = "derrota"
            fn.dibujarperdida(pantalla, jugdatos, mapagraf2, bfuentetitulo, bfontederrota, botonesderrota, mouse, camara=(cam_x, cam_y))
        else:
            fn.dibujarjuego(pantalla, mapagraf2, jugdatos, vidas, enemigos, proys=proys, camara=(cam_x, cam_y), escudos=escudos)
            rect_pancho_hud, rect_speed_hud = fn.dibujarrecursos(pantalla, iconos_recursos, pesos, panchos, balas if pistola else None, BALAS_MAXIMAS, speeds=speeds)
            fn.dibujaroleada(pantalla, oleada)
            if pygame.time.get_ticks() < mensaje_pancho_hasta:
                texto_uso = fuente_compra.render(mensaje_pancho, True, (255, 255, 255))
                pantalla.blit(texto_uso, texto_uso.get_rect(topright=(ancho - int(alto * 0.02), rect_pancho_hud.bottom + 4)))
    elif estado == "derrota":
        mapaderrota = mapagraf if mapa == 1 else mapagraf2
        cam_derrota = (cam_x, cam_y) if mapa == 2 else (0, 0)
        fn.dibujarperdida(pantalla, jugdatos, mapaderrota, bfuentetitulo, bfontederrota, botonesderrota, mouse, camara=cam_derrota)
    elif estado == "victoria":
        fn.dibujarjuego(pantalla, mapagraf, jugdatos, vidas, [], proys=proys, escudos=escudos)
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
    escudo = jugdatos.get("escudo", 0)
    posicion_mc = jugdatos["rect"].topleft
    if ventana.get_size() == pantalla.get_size():
        ventana.blit(pantalla, (0, 0))
    else:
        pygame.transform.scale(pantalla, ventana.get_size(), pantalla_ventana)
        ventana.blit(pantalla_ventana, (0, 0))
    pygame.display.flip()
    reloj.tick(60)

    pesos = jugdatos.get("pesos", pesos)
    if ahora - ultimo_guardado >= 5000:
        fn.guardardat(vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa, escudo=escudo, speeds=speeds)
        ultimo_guardado = ahora

video.release()
pygame.quit()
sys.exit()
