import pygame
import sys
import cv2
import funciones as fn

pygame.init()

vent = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
anc, alt = vent.get_size()
pant = pygame.Surface((anc, alt))
pant_vent = pygame.Surface(vent.get_size())
pygame.display.set_caption("La Matanza Avanza")

vid = cv2.VideoCapture("F/trenfondo.mp4")
if not vid.isOpened():
    vid.release()
    vid = cv2.VideoCapture("trenfondo.mp4")
wpan = int(anc * 0.32)

pizq, pder = fn.capas(anc, alt, wpan)
ftit, fbtn = fn.fuentes(alt)
t1, t2, r1, r2 = fn.titulos(ftit, wpan, alt)
btns = fn.btnlista(wpan, alt)

mgraf = fn.cargarmapa(anc, alt)
mgraf2 = fn.cargarmapa2(anc, alt)
anc_m2 = mgraf2.get_width()
alt_m2 = mgraf2.get_height()
camx, camy = 0, 0
andy00, andy01, andy02, andy03 = fn.cargabazar(anc, alt)
mira = fn.cargarmira(alt)
icons = fn.cargariconos(alt)
t_pan = int(alt * 0.11)
pan_tienda = pygame.transform.smoothscale(icons["pancho"], (t_pan, t_pan))
img_spd_f = icons["speed_full"]
h_spd_t = int(alt * 0.135)
w_spd_t = max(24, int(img_spd_f.get_width() * (h_spd_t / img_spd_f.get_height())))
spd_tienda = pygame.transform.smoothscale(img_spd_f, (w_spd_t, h_spd_t))
f_comp = pygame.font.Font(None, max(24, int(alt * 0.035)))
f_comp_ch = pygame.font.Font(None, max(18, int(alt * 0.026)))
pbazar = fn.crearpuerta(anc, alt)
trans = {"estado": "ninguno", "inicio": 0}
msg_comp = ""
car_pist = 0
car_pan = 0
car_spd = 0
msg_pan = ""
msg_pan_hasta = 0
PRECIO_PISTOLA = 10
PRECIO_PANCHO = 75
PRECIO_SPEED = 250
BMAX = 10
balas = BMAX
rec_hasta = 0
slot_actual = 1
nombre_partida = "Partida 1"
partidas = fn.listarpartidas(anc, alt)
modal_crear = None
modal_borrar = None
vida, esc, pts, ole, pesos, panchos, spds, pist, posmc, mapa = fn.cargardat(anc, alt, slot=slot_actual)
jdat = fn.crearjug(anc, alt)
jdat["vida"] = vida
jdat["escudo"] = esc
jdat["pesos"] = pesos
jdat["puntos"] = pts
jdat["pistola"] = pist
fn.escjug(jdat, anc, alt, mapa=mapa)
wini = anc_m2 if mapa == 2 else anc
hini = alt_m2 if mapa == 2 else alt
fn.ajustapos(jdat, posmc, wini, hini, mapa)
vidas = fn.cargarvidas(alt)
escudos = fn.cargarescudos(alt)
bftit, bfontder, bder = fn.bderrota(anc, alt)
enes = fn.crearene(anc_m2, alt_m2, min(8 + ole * 3, 40), ole, alt_p=alt, jdat=jdat) if mapa == 2 else []
proys = []
r_pan_hud = None
r_spd_hud = None
clk = pygame.time.Clock()
estado = "menu"
ult_guardado = pygame.time.get_ticks()
jugando = True

while jugando:
    ahora = pygame.time.get_ticks()
    if rec_hasta and ahora >= rec_hasta:
        balas = BMAX
        rec_hasta = 0

    if jdat.get("panchos_extra", 0) > 0:
        panchos += jdat["panchos_extra"]
        jdat["panchos_extra"] = 0
    if jdat.get("balas_extra", 0) > 0:
        balas = min(BMAX, balas + jdat["balas_extra"])
        if balas > 0:
            rec_hasta = 0
        jdat["balas_extra"] = 0
    jdat["pistola"] = pist

    mvent = pygame.mouse.get_pos()
    mouse = (mvent[0] * anc // vent.get_width(), mvent[1] * alt // vent.get_height())
    teclas = pygame.key.get_pressed()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            fn.guardardat(jdat["vida"], jdat.get("puntos", pts), ole, pesos, panchos, pist, jdat["rect"].topleft, mapa, esc=jdat.get("escudo", 0), spds=spds, slot=slot_actual, nombre=nombre_partida)
            jugando = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                if estado == "slots":
                    if modal_crear:
                        modal_crear = None
                    elif modal_borrar:
                        modal_borrar = None
                    else:
                        estado = "menu"
                elif estado in ("juego", "continuara", "bazar", "derrota", "victoria"):
                    fn.guardardat(jdat["vida"], jdat.get("puntos", pts), ole, pesos, panchos, pist, jdat["rect"].topleft, mapa, esc=jdat.get("escudo", 0), spds=spds, slot=slot_actual, nombre=nombre_partida)
                    estado = "menu"
                elif estado == "menu":
                    jugando = False
            elif estado == "slots":
                if modal_crear:
                    if ev.key == pygame.K_RETURN:
                        nom_f = modal_crear["texto"].strip() or f"Partida {modal_crear['slot']}"
                        fn.crear_nueva_partida(modal_crear["slot"], nom_f, anc, alt)
                        slot_actual = modal_crear["slot"]
                        nombre_partida = nom_f
                        vida, esc, pts, ole, pesos, panchos, spds, pist, posmc, mapa = fn.cargardat(anc, alt, slot=slot_actual)
                        jdat = fn.crearjug(anc, alt)
                        jdat["vida"] = vida
                        jdat["escudo"] = esc
                        jdat["pesos"] = pesos
                        jdat["puntos"] = pts
                        jdat["pistola"] = pist
                        fn.escjug(jdat, anc, alt, mapa=mapa)
                        wm = anc_m2 if mapa == 2 else anc
                        hm = alt_m2 if mapa == 2 else alt
                        fn.ajustapos(jdat, posmc, wm, hm, mapa)
                        estado = "juego" if mapa == 1 else ("continuara" if mapa == 2 else "bazar")
                        enes = fn.crearene(anc_m2, alt_m2, min(8 + ole * 3, 40), ole, alt_p=alt, jdat=jdat) if mapa == 2 else []
                        proys = []
                        trans = {"estado": "andy01" if mapa == "bazar" else "ninguno", "inicio": pygame.time.get_ticks()}
                        mgraf = fn.cargarmapa(anc, alt)
                        modal_crear = None
                        partidas = fn.listarpartidas(anc, alt)
                    elif ev.key == pygame.K_BACKSPACE:
                        modal_crear["texto"] = modal_crear["texto"][:-1]
                    else:
                        if len(modal_crear["texto"]) < 18 and ev.unicode.isprintable():
                            modal_crear["texto"] += ev.unicode
            elif ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_k):
                if estado in ("juego", "continuara"):
                    fn.inidash(jdat, teclas)
            elif ev.key == pygame.K_j:
                if estado == "juego":
                    if fn.iniataq(jdat, mouse):
                        proys.append(fn.crearproy(jdat))
                elif estado == "continuara":
                    mmundo = (mouse[0] + camx, mouse[1] + camy)
                    if fn.iniataq(jdat, mmundo, enes=enes):
                        proys.append(fn.crearproy(jdat))
            elif ev.key == pygame.K_SPACE:
                if estado == "juego" and mapa == 1 and jdat["hitbox"].colliderect(pbazar):
                    estado = "bazar"
                    mapa = "bazar"
                    trans["estado"] = "negro"
                    trans["inicio"] = pygame.time.get_ticks()
                elif estado == "bazar":
                    estado = "juego"
                    mapa = 1
                    trans["estado"] = "ninguno"
                    mgraf = fn.cargarmapa(anc, alt)
                    jdat["rect"].centerx = pbazar.centerx
                    jdat["rect"].top = int(alt * 0.36)
                    fn.ajustapos(jdat, jdat["rect"].topleft, anc, alt, mapa)
                elif estado == "juego":
                    if fn.iniataq(jdat, mouse):
                        proys.append(fn.crearproy(jdat))
                elif estado == "continuara":
                    mmundo = (mouse[0] + camx, mouse[1] + camy)
                    if fn.iniataq(jdat, mmundo, enes=enes):
                        proys.append(fn.crearproy(jdat))
            elif ev.key == pygame.K_BACKSPACE and estado == "bazar" and trans["estado"] == "andy03":
                trans["estado"] = "andy02"
                trans["inicio"] = pygame.time.get_ticks()
                car_pist = 0
                car_pan = 0
                car_spd = 0

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
            mvent = ev.pos
            mouse = (mvent[0] * anc // vent.get_width(), mvent[1] * alt // vent.get_height())
            if estado == "bazar" and trans["estado"] == "andy03":
                s_pist = pygame.Rect(int(anc * 0.145), int(alt * 0.210), int(anc * 0.115), int(alt * 0.175))
                s_pan = pygame.Rect(int(anc * 0.334), int(alt * 0.210), int(anc * 0.121), int(alt * 0.178))
                s_spd = pygame.Rect(int(anc * 0.529), int(alt * 0.210), int(anc * 0.128), int(alt * 0.178))
                if s_pan.collidepoint(mouse) and car_pan > 0:
                    car_pan -= 1
                    msg_comp = ""
                elif s_spd.collidepoint(mouse) and car_spd > 0:
                    car_spd -= 1
                    msg_comp = ""
                elif s_pist.collidepoint(mouse) and car_pist > 0:
                    car_pist = 0
                    msg_comp = ""
            elif estado == "juego":
                if fn.iniataq(jdat, mouse):
                    proys.append(fn.crearproy(jdat))
            elif estado == "continuara":
                mmundo = (mouse[0] + camx, mouse[1] + camy)
                if fn.iniataq(jdat, mmundo, enes=enes):
                    proys.append(fn.crearproy(jdat))

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mvent = ev.pos
            mouse = (mvent[0] * anc // vent.get_width(), mvent[1] * alt // vent.get_height())
            if estado in ("juego", "continuara") and r_pan_hud and r_pan_hud.collidepoint(mouse):
                if panchos > 0 and jdat["vida"] < 5:
                    panchos -= 1
                    jdat["vida"] = 5
                    jdat["daño_acum"] = 0.0
                    msg_pan = "Vida restaurada"
                    fn.guardardat(jdat["vida"], pts, ole, pesos, panchos, pist, jdat["rect"].topleft, mapa, esc=jdat.get("escudo", 0), spds=spds, slot=slot_actual, nombre=nombre_partida)
                elif jdat["vida"] >= 5:
                    msg_pan = "Vida completa"
                else:
                    msg_pan = "No tienes panchos"
                msg_pan_hasta = pygame.time.get_ticks() + 1400
            elif estado in ("juego", "continuara") and r_spd_hud and r_spd_hud.collidepoint(mouse):
                if spds > 0 and jdat.get("escudo", 0) < 3:
                    spds -= 1
                    jdat["escudo"] = min(3, jdat.get("escudo", 0) + 1)
                    msg_pan = "+1 Barra de Escudo"
                    fn.guardardat(jdat["vida"], pts, ole, pesos, panchos, pist, jdat["rect"].topleft, mapa, esc=jdat.get("escudo", 0), spds=spds, slot=slot_actual, nombre=nombre_partida)
                elif jdat.get("escudo", 0) >= 3:
                    msg_pan = "Escudo al maximo"
                else:
                    msg_pan = "No tienes Speed"
                msg_pan_hasta = pygame.time.get_ticks() + 1400
            elif estado == "slots":
                lay = fn.layout_slots(anc, alt, modal_crear, modal_borrar)
                if modal_crear and lay["modal_crear"]:
                    if lay["modal_crear"]["rect_aceptar"].collidepoint(mouse):
                        nom_f = modal_crear["texto"].strip() or f"Partida {modal_crear['slot']}"
                        fn.crear_nueva_partida(modal_crear["slot"], nom_f, anc, alt)
                        slot_actual = modal_crear["slot"]
                        nombre_partida = nom_f
                        vida, esc, pts, ole, pesos, panchos, spds, pist, posmc, mapa = fn.cargardat(anc, alt, slot=slot_actual)
                        jdat = fn.crearjug(anc, alt)
                        jdat["vida"] = vida
                        jdat["escudo"] = esc
                        jdat["pesos"] = pesos
                        jdat["puntos"] = pts
                        jdat["pistola"] = pist
                        fn.escjug(jdat, anc, alt, mapa=mapa)
                        wm = anc_m2 if mapa == 2 else anc
                        hm = alt_m2 if mapa == 2 else alt
                        fn.ajustapos(jdat, posmc, wm, hm, mapa)
                        estado = "juego" if mapa == 1 else ("continuara" if mapa == 2 else "bazar")
                        enes = fn.crearene(anc_m2, alt_m2, min(8 + ole * 3, 40), ole, alt_p=alt, jdat=jdat) if mapa == 2 else []
                        proys = []
                        trans = {"estado": "andy01" if mapa == "bazar" else "ninguno", "inicio": pygame.time.get_ticks()}
                        mgraf = fn.cargarmapa(anc, alt)
                        modal_crear = None
                        partidas = fn.listarpartidas(anc, alt)
                    elif lay["modal_crear"]["rect_cancelar"].collidepoint(mouse):
                        modal_crear = None
                elif modal_borrar and lay["modal_borrar"]:
                    if lay["modal_borrar"]["rect_confirmar"].collidepoint(mouse):
                        fn.borrarpartida(modal_borrar["slot"])
                        modal_borrar = None
                        partidas = fn.listarpartidas(anc, alt)
                    elif lay["modal_borrar"]["rect_cancelar"].collidepoint(mouse):
                        modal_borrar = None
                else:
                    if lay["rect_volver"].collidepoint(mouse):
                        estado = "menu"
                    else:
                        for s_inf in lay["slots"]:
                            s_num = s_inf["slot"]
                            p = next((x for x in partidas if x["slot"] == s_num), None)
                            if p and p["existe"]:
                                if s_inf["rect_borrar"].collidepoint(mouse):
                                    modal_borrar = {"slot": s_num, "nombre": p["nombre"]}
                                    break
                                elif s_inf["rect_jugar"].collidepoint(mouse) or s_inf["rect_card"].collidepoint(mouse):
                                    slot_actual = s_num
                                    nombre_partida = p["nombre"]
                                    vida, esc, pts, ole, pesos, panchos, spds, pist, posmc, mapa = fn.cargardat(anc, alt, slot=slot_actual)
                                    jdat = fn.crearjug(anc, alt)
                                    jdat["vida"] = vida
                                    jdat["escudo"] = esc
                                    jdat["pesos"] = pesos
                                    jdat["puntos"] = pts
                                    jdat["pistola"] = pist
                                    fn.escjug(jdat, anc, alt, mapa=mapa)
                                    wm = anc_m2 if mapa == 2 else anc
                                    hm = alt_m2 if mapa == 2 else alt
                                    fn.ajustapos(jdat, posmc, wm, hm, mapa)
                                    estado = "juego" if mapa == 1 else ("continuara" if mapa == 2 else "bazar")
                                    enes = fn.crearene(anc_m2, alt_m2, min(8 + ole * 3, 40), ole, alt_p=alt, jdat=jdat) if mapa == 2 else []
                                    proys = []
                                    trans = {"estado": "andy01" if mapa == "bazar" else "ninguno", "inicio": pygame.time.get_ticks()}
                                    mgraf = fn.cargarmapa(anc, alt)
                                    break
                            elif p and not p["existe"]:
                                if s_inf["rect_card"].collidepoint(mouse):
                                    modal_crear = {"slot": s_num, "texto": f"Partida {s_num}"}
                                    break
            elif estado == "menu":
                for b in btns:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            partidas = fn.listarpartidas(anc, alt)
                            modal_crear = None
                            modal_borrar = None
                            estado = "slots"
                        elif b["accion"] == "reiniciar":
                            vida, esc, pts, ole, pesos, panchos, spds, pist, mapa = 5, 0, 0, 1, 0, 0, 0, False, 1
                            jdat = fn.crearjug(anc, alt)
                            posmc = jdat["rect"].topleft
                            enes, proys = [], []
                            trans = {"estado": "ninguno", "inicio": 0}
                            mgraf = fn.cargarmapa(anc, alt)
                            fn.guardardat(vida, pts, ole, pesos, panchos, pist, posmc, mapa, esc=esc, spds=spds, slot=slot_actual, nombre=nombre_partida)
                            estado = "juego"
                        elif b["accion"] == "ventana":
                            vent = fn.modopant(anc, alt, vent)
                            pant_vent = pygame.Surface(vent.get_size())
                            b["texto"] = "VENTANA" if vent.get_flags() & pygame.FULLSCREEN else "PANTALLA COMPLETA"
                        elif b["accion"] == "salir":
                            jugando = False
            elif estado == "bazar":
                if trans["estado"] == "andy02":
                    comprar = pygame.Rect(int(anc * 0.62), int(alt * 0.56), int(anc * 0.22), int(alt * 0.18))
                    salir = pygame.Rect(int(anc * 0.62), int(alt * 0.78), int(anc * 0.22), int(alt * 0.18))
                    if salir.collidepoint(mouse):
                        estado = "juego"
                        mapa = 1
                        trans["estado"] = "ninguno"
                        mgraf = fn.cargarmapa(anc, alt)
                        jdat["rect"].centerx = pbazar.centerx
                        jdat["rect"].top = int(alt * 0.36)
                        fn.ajustapos(jdat, jdat["rect"].topleft, anc, alt, mapa)
                    elif comprar.collidepoint(mouse):
                        trans["estado"] = "andy03"
                        trans["inicio"] = pygame.time.get_ticks()
                        msg_comp = ""
                        car_pist = 0
                        car_pan = 0
                        car_spd = 0
                elif trans["estado"] == "andy03":
                    s_pist = pygame.Rect(int(anc * 0.145), int(alt * 0.210), int(anc * 0.115), int(alt * 0.175))
                    s_pan = pygame.Rect(int(anc * 0.334), int(alt * 0.210), int(anc * 0.121), int(alt * 0.178))
                    s_spd = pygame.Rect(int(anc * 0.529), int(alt * 0.210), int(anc * 0.128), int(alt * 0.178))
                    btn_conf = pygame.Rect(int(anc * 0.713), int(alt * 0.605), int(anc * 0.145), int(alt * 0.173))
                    btn_vac = pygame.Rect(int(anc * 0.56), int(alt * 0.65), int(anc * 0.13), int(alt * 0.08))
                    volver = pygame.Rect(int(anc * 0.02), int(alt * 0.02), int(anc * 0.18), int(alt * 0.14))

                    if s_pist.collidepoint(mouse):
                        if pist:
                            msg_comp = "Ya tienes la pistola (solo 1 vez)"
                        else:
                            car_pist = 0 if car_pist else 1
                            msg_comp = ""
                    elif s_pan.collidepoint(mouse):
                        car_pan += 1
                        msg_comp = ""
                    elif s_spd.collidepoint(mouse):
                        car_spd += 1
                        msg_comp = ""
                    elif btn_vac.collidepoint(mouse):
                        car_pist = 0
                        car_pan = 0
                        car_spd = 0
                        msg_comp = "Seleccion vaciada"
                    elif btn_conf.collidepoint(mouse):
                        ctot = (PRECIO_PISTOLA if car_pist else 0) + car_pan * PRECIO_PANCHO + car_spd * PRECIO_SPEED
                        if car_pist == 0 and car_pan == 0 and car_spd == 0:
                            msg_comp = "Toca los iconos para agregar items"
                        elif pesos >= ctot:
                            pesos -= ctot
                            jdat["pesos"] = pesos
                            if car_pist:
                                pist = True
                                jdat["pistola"] = True
                            panchos += car_pan
                            spds += car_spd
                            car_pist, car_pan, car_spd = 0, 0, 0
                            msg_comp = "¡Compra confirmada!"
                            fn.guardardat(jdat["vida"], pts, ole, pesos, panchos, pist, jdat["rect"].topleft, mapa, esc=jdat.get("escudo", 0), spds=spds, slot=slot_actual, nombre=nombre_partida)
                        else:
                            msg_comp = f"Necesitas {ctot} pesos (tienes {pesos})"
                    elif volver.collidepoint(mouse):
                        trans["estado"] = "andy02"
                        trans["inicio"] = pygame.time.get_ticks()
                        car_pist, car_pan, car_spd = 0, 0, 0
            elif estado == "juego" and trans["estado"] == "ninguno":
                if pist:
                    if balas > 0:
                        p = fn.proypist(jdat, mouse)
                        if p is not None:
                            proys.append(p)
                            balas -= 1
                            if balas == 0:
                                rec_hasta = pygame.time.get_ticks() + 2000
                elif fn.iniataq(jdat, mouse):
                    proys.append(fn.crearproy(jdat))
            elif estado == "continuara":
                mmundo = (mouse[0] + camx, mouse[1] + camy)
                if pist:
                    if balas > 0:
                        p = fn.proypist(jdat, mmundo)
                        if p is not None:
                            proys.append(p)
                            balas -= 1
                            if balas == 0:
                                rec_hasta = pygame.time.get_ticks() + 2000
                elif fn.iniataq(jdat, mmundo, enes=enes):
                    proys.append(fn.crearproy(jdat))
            elif estado == "derrota":
                for b in bder:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            jdat = fn.crearjug(anc, alt)
                            fn.escjug(jdat, anc, alt, mapa=1)
                            vida, esc, pts, ole, pesos, panchos, spds, pist, mapa = jdat["vida"], 0, 0, 1, 0, 0, 0, False, 1
                            enes, proys = [], []
                            trans = {"estado": "ninguno", "inicio": 0}
                            mgraf = fn.cargarmapa(anc, alt)
                            fn.guardardat(vida, pts, ole, pesos, panchos, pist, jdat["rect"].topleft, mapa, esc=esc, spds=spds, slot=slot_actual, nombre=nombre_partida)
                            estado = "juego"
                        elif b["accion"] == "menu":
                            estado = "menu"

    if estado == "menu":
        fsurf = fn.framevideo(vid, anc, alt)
        fn.dibujar(pant, fsurf, pizq, pder, wpan, t1, t2, r1, r2, btns, fbtn, mouse)
    elif estado == "slots":
        fsurf = fn.framevideo(vid, anc, alt)
        fn.dibujarslots(pant, fsurf, anc, alt, partidas, mouse, modal_crear, modal_borrar)
    elif estado == "juego":
        fn.actataq(jdat)
        fn.moverjug(jdat, teclas, anc, alt, mapa=1)
        fn.moverproy(proys, [], anc, alt, jdat)
        fn.recibirdaño(jdat, [])
        fn.actefectos(jdat)
        pesos = jdat.get("pesos", pesos)
        pts = jdat.get("puntos", pts)

        if jdat["vida"] <= 0:
            estado = "derrota"
            fn.dibujarperdida(pant, jdat, mgraf, bftit, bfontder, bder, mouse)
        elif jdat["rect"].right >= anc:
            estado = "continuara"
            mapa = 2
            fn.escjug(jdat, anc, alt, mapa=2)
            proys = []
            jdat["rect"].left = max(0, int(anc_m2 * 0.02))
            # Limitamos la posicion Y al rango caminable del mapa 2 (entre 20% y 80% de la altura)
            jdat["rect"].centery = max(int(alt_m2 * 0.20), min(int(alt_m2 * 0.80), int(jdat["rect"].centery * (alt_m2 / alt))))
            fn.ajustapos(jdat, jdat["rect"].topleft, anc_m2, alt_m2, mapa)
            enes = fn.crearene(anc_m2, alt_m2, min(8 + ole * 3, 40), ole, alt_p=alt, jdat=jdat)
        else:
            fn.dibujarjuego(pant, mgraf, jdat, vidas, [], proys=proys, escudos=escudos)
            if jdat["hitbox"].colliderect(pbazar):
                txt_b = f_comp.render("[ESPACIO] BAZAR", True, (255, 255, 255))
                rtb = txt_b.get_rect(center=(pbazar.centerx, pbazar.top - 14))
                pygame.draw.rect(pant, (0, 0, 0, 180), rtb.inflate(14, 8), border_radius=4)
                pant.blit(txt_b, rtb)
            r_pan_hud, r_spd_hud = fn.dibujarrecursos(pant, icons, pesos, panchos, balas if pist else None, BMAX, spds=spds)
            fn.dibujaroleada(pant, ole, None, jdat)
            if pygame.time.get_ticks() < msg_pan_hasta:
                tuso = f_comp.render(msg_pan, True, (255, 255, 255))
                pant.blit(tuso, tuso.get_rect(topright=(anc - int(alt * 0.02), r_pan_hud.bottom + 4)))
    elif estado == "bazar":
        ahora = pygame.time.get_ticks()
        if trans["estado"] == "negro":
            pant.fill((0, 0, 0))
            if ahora - trans["inicio"] >= 250:
                trans["estado"] = "andy00"
                trans["inicio"] = ahora
        elif trans["estado"] == "andy00":
            if ahora - trans["inicio"] >= 700:
                trans["estado"] = "fade_andy01"
                trans["inicio"] = ahora
            pant.blit(andy00, (0, 0))
        elif trans["estado"] == "fade_andy01":
            prog = min(1.0, (ahora - trans["inicio"]) / 350.0)
            pant.blit(andy00, (0, 0))
            andy01.set_alpha(int(prog * 255))
            pant.blit(andy01, (0, 0))
            if prog >= 1.0:
                trans["estado"] = "andy01"
                trans["inicio"] = ahora
        elif trans["estado"] == "andy01":
            andy01.set_alpha(255)
            pant.blit(andy01, (0, 0))
            if ahora - trans["inicio"] >= 1000:
                trans["estado"] = "andy02"
                trans["inicio"] = ahora
        elif trans["estado"] == "andy02":
            pant.blit(andy02, (0, 0))
        elif trans["estado"] == "andy03":
            pant.blit(andy03, (0, 0))
            s_pist = pygame.Rect(int(anc * 0.145), int(alt * 0.210), int(anc * 0.115), int(alt * 0.175))
            s_pan = pygame.Rect(int(anc * 0.334), int(alt * 0.210), int(anc * 0.121), int(alt * 0.178))
            s_spd = pygame.Rect(int(anc * 0.529), int(alt * 0.210), int(anc * 0.128), int(alt * 0.178))
            btn_conf = pygame.Rect(int(anc * 0.713), int(alt * 0.605), int(anc * 0.145), int(alt * 0.173))
            btn_vac = pygame.Rect(int(anc * 0.56), int(alt * 0.65), int(anc * 0.13), int(alt * 0.08))

            pant.blit(pan_tienda, pan_tienda.get_rect(center=s_pan.center))
            pant.blit(spd_tienda, spd_tienda.get_rect(center=s_spd.center))

            if pist:
                ov_comp = pygame.Surface(s_pist.size, pygame.SRCALPHA)
                ov_comp.fill((0, 0, 0, 150))
                pant.blit(ov_comp, s_pist.topleft)
                pygame.draw.rect(pant, (120, 120, 120), s_pist, 3, border_radius=6)
                t_comp = f_comp_ch.render("COMPRADA", True, (255, 200, 100))
                pant.blit(t_comp, t_comp.get_rect(center=s_pist.center))
            elif car_pist > 0:
                pygame.draw.rect(pant, (80, 255, 100), s_pist, 4, border_radius=6)
                bp = f_comp.render("x1", True, (80, 255, 100))
                pant.blit(bp, bp.get_rect(bottomright=(s_pist.right - 6, s_pist.bottom - 4)))
            elif s_pist.collidepoint(mouse):
                pygame.draw.rect(pant, (255, 255, 140), s_pist, 3, border_radius=6)

            if car_pan > 0:
                pygame.draw.rect(pant, (80, 255, 100), s_pan, 4, border_radius=6)
                bpan = f_comp.render(f"x{car_pan}", True, (80, 255, 100))
                pant.blit(bpan, bpan.get_rect(bottomright=(s_pan.right - 6, s_pan.bottom - 4)))
            elif s_pan.collidepoint(mouse):
                pygame.draw.rect(pant, (255, 255, 140), s_pan, 3, border_radius=6)

            if car_spd > 0:
                pygame.draw.rect(pant, (80, 255, 100), s_spd, 4, border_radius=6)
                bspd = f_comp.render(f"x{car_spd}", True, (80, 255, 100))
                pant.blit(bspd, bspd.get_rect(bottomright=(s_spd.right - 6, s_spd.bottom - 4)))
            elif s_spd.collidepoint(mouse):
                pygame.draw.rect(pant, (255, 255, 140), s_spd, 3, border_radius=6)

            lbl_pist = f_comp_ch.render("PISTOLA (Única)", True, (255, 255, 255))
            pr_pist_t = f_comp_ch.render("AGOTADO" if pist else f"${PRECIO_PISTOLA}", True, (200, 200, 200) if pist else (255, 230, 100))
            pant.blit(lbl_pist, lbl_pist.get_rect(center=(s_pist.centerx, s_pist.bottom + int(alt * 0.03))))
            pant.blit(pr_pist_t, pr_pist_t.get_rect(center=(s_pist.centerx, s_pist.bottom + int(alt * 0.065))))

            lbl_pan = f_comp_ch.render("PANCHO (+Vida)", True, (255, 255, 255))
            pr_pan_t = f_comp_ch.render(f"${PRECIO_PANCHO} c/u", True, (255, 230, 100))
            ay_pan = f_comp_ch.render("(Clic izq +1 / der -1)", True, (210, 210, 210))
            pant.blit(lbl_pan, lbl_pan.get_rect(center=(s_pan.centerx, s_pan.bottom + int(alt * 0.03))))
            pant.blit(pr_pan_t, pr_pan_t.get_rect(center=(s_pan.centerx, s_pan.bottom + int(alt * 0.065))))
            pant.blit(ay_pan, ay_pan.get_rect(center=(s_pan.centerx, s_pan.bottom + int(alt * 0.098))))

            lbl_spd = f_comp_ch.render("SPEED (+1 Escudo)", True, (255, 255, 255))
            pr_spd_t = f_comp_ch.render(f"${PRECIO_SPEED} c/u", True, (255, 230, 100))
            ay_spd = f_comp_ch.render("(Clic izq +1 / der -1)", True, (210, 210, 210))
            pant.blit(lbl_spd, lbl_spd.get_rect(center=(s_spd.centerx, s_spd.bottom + int(alt * 0.03))))
            pant.blit(pr_spd_t, pr_spd_t.get_rect(center=(s_spd.centerx, s_spd.bottom + int(alt * 0.065))))
            pant.blit(ay_spd, ay_spd.get_rect(center=(s_spd.centerx, s_spd.bottom + int(alt * 0.098))))

            ctot = car_pist * PRECIO_PISTOLA + car_pan * PRECIO_PANCHO + car_spd * PRECIO_SPEED
            tsaldo = f_comp.render(f"Tus Pesos: ${pesos}", True, (255, 255, 255))
            pant.blit(tsaldo, tsaldo.get_rect(center=(int(anc * 0.78), int(alt * 0.25))))

            tresum = f_comp_ch.render(f"Pistola x{car_pist} | Panchos x{car_pan} | Speed x{car_spd}", True, (230, 230, 230))
            pant.blit(tresum, tresum.get_rect(center=(int(anc * 0.75), int(alt * 0.46))))

            coltot = (255, 110, 110) if ctot > pesos else (120, 255, 140)
            ttot = f_comp.render(f"Total a confirmar: ${ctot}", True, coltot)
            pant.blit(ttot, ttot.get_rect(center=(int(anc * 0.75), int(alt * 0.53))))

            if btn_conf.collidepoint(mouse):
                pygame.draw.rect(pant, (255, 255, 255), btn_conf, 3, border_radius=10)

            if car_pist > 0 or car_pan > 0 or car_spd > 0:
                colvac = (170, 60, 60) if btn_vac.collidepoint(mouse) else (120, 40, 40)
                pygame.draw.rect(pant, colvac, btn_vac, border_radius=8)
                pygame.draw.rect(pant, (255, 200, 200), btn_vac, 2, border_radius=8)
                tvac = f_comp_ch.render("VACIAR", True, (255, 255, 255))
                pant.blit(tvac, tvac.get_rect(center=btn_vac.center))

            if msg_comp:
                es_err = any(msg_comp.startswith(pfx) for pfx in ("Necesitas", "Selecciona", "Toca", "Ya "))
                tmsg = f_comp.render(msg_comp, True, (255, 120, 120) if es_err else (130, 255, 130))
                rmsg = tmsg.get_rect(center=(int(anc * 0.50), int(alt * 0.85)))
                pygame.draw.rect(pant, (0, 0, 0, 190), rmsg.inflate(20, 10), border_radius=6)
                pant.blit(tmsg, rmsg)
    elif estado == "continuara":
        fn.actataq(jdat)
        obs_m2 = fn.obstaculos(2, anc_m2, alt_m2)
        fn.moverjug(jdat, teclas, anc_m2, alt_m2, mapa=2, obs_l=obs_m2)
        fn.actualizaene(enes, jdat, proys, obs_l=obs_m2, anc=anc_m2, alt=alt_m2)
        fn.moverproy(proys, enes, anc_m2, alt_m2, jdat)
        pesos = jdat.get("pesos", pesos)
        pts = jdat.get("puntos", pts)

        camx = max(0, min(jdat["rect"].centerx - anc // 2, anc_m2 - anc))
        camy = max(0, min(jdat["rect"].centery - alt // 2, alt_m2 - alt))

        btns_m = pygame.mouse.get_pressed()
        en_hud = (r_pan_hud and r_pan_hud.collidepoint(mouse)) or (r_spd_hud and r_spd_hud.collidepoint(mouse))
        if btns_m[0] and pist and balas > 0 and not en_hud:
            mmundo = (mouse[0] + camx, mouse[1] + camy)
            p = fn.proypist(jdat, mmundo)
            if p is not None:
                proys.append(p)
                balas -= 1
                if balas == 0:
                    rec_hasta = pygame.time.get_ticks() + 2000

        cola_vac = not jdat.get("ole_inf") or len(jdat["ole_inf"].get("cola", [])) == 0
        if jdat["rect"].right >= anc_m2 and cola_vac and len([e for e in enes if e["vida"] > 0]) == 0:
            ole_fin = ole >= 20
            if ole < 20:
                ole += 1
            mapa = 1
            estado = "victoria" if ole_fin else "juego"
            fn.escjug(jdat, anc, alt, mapa=1)
            jdat["rect"].left = max(0, int(anc * 0.02))
            # Limitamos la posicion Y al rango caminable del mapa 1 (entre 42% y 54% de la altura)
            jdat["rect"].centery = max(int(alt * 0.42), min(int(alt * 0.54), int(jdat["rect"].centery * (alt / alt_m2))))
            enes, proys, jdat["drops"] = [], [], []
            mgraf = fn.cargarmapa(anc, alt)
            fn.ajustapos(jdat, jdat["rect"].topleft, anc, alt, mapa)
        elif jdat["vida"] <= 0:
            estado = "derrota"
            fn.dibujarperdida(pant, jdat, mgraf2, bftit, bfontder, bder, mouse, cam=(camx, camy))
        else:
            fn.dibujarjuego(pant, mgraf2, jdat, vidas, enes, proys=proys, cam=(camx, camy), escudos=escudos)
            r_pan_hud, r_spd_hud = fn.dibujarrecursos(pant, icons, pesos, panchos, balas if pist else None, BMAX, spds=spds)
            fn.dibujaroleada(pant, ole, enes, jdat)
            if pygame.time.get_ticks() < msg_pan_hasta:
                tuso = f_comp.render(msg_pan, True, (255, 255, 255))
                pant.blit(tuso, tuso.get_rect(topright=(anc - int(alt * 0.02), r_pan_hud.bottom + 4)))
    elif estado == "derrota":
        mder = mgraf if mapa == 1 else mgraf2
        cder = (camx, camy) if mapa == 2 else (0, 0)
        fn.dibujarperdida(pant, jdat, mder, bftit, bfontder, bder, mouse, cam=cder)
    elif estado == "victoria":
        fn.dibujarjuego(pant, mgraf, jdat, vidas, [], proys=proys, escudos=escudos)
        capa = pygame.Surface(pant.get_size(), pygame.SRCALPHA)
        capa.fill((0, 0, 0, 150))
        pant.blit(capa, (0, 0))
        txt = bftit.render("COMPLETASTE LAS 20 OLEADAS", True, (255, 255, 255))
        pant.blit(txt, txt.get_rect(center=(anc // 2, alt // 2)))
        subv = bfontder.render("GG fucking Easy", True, (255, 255, 255))
        pant.blit(subv, subv.get_rect(center=(anc // 2, int(alt * 0.60))))

    ver_mira = pist and estado in ("juego", "continuara")
    pygame.mouse.set_visible(not ver_mira)
    if ver_mira:
        pant.blit(mira, mira.get_rect(center=mouse))

    posmc = jdat["rect"].topleft
    if vent.get_size() == pant.get_size():
        vent.blit(pant, (0, 0))
    else:
        pygame.transform.scale(pant, vent.get_size(), pant_vent)
        vent.blit(pant_vent, (0, 0))
    pygame.display.flip()
    clk.tick(60)

    pesos = jdat.get("pesos", pesos)
    if ahora - ult_guardado >= 5000:
        fn.guardardat(jdat["vida"], jdat.get("puntos", pts), ole, pesos, panchos, pist, posmc, mapa, esc=jdat.get("escudo", 0), spds=spds, slot=slot_actual, nombre=nombre_partida)
        ult_guardado = ahora

vid.release()
pygame.quit()
sys.exit()
