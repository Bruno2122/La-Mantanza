import os
import sys
import pygame
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

import funciones as fn

pygame.init()

vent = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
anc, alt = vent.get_size()
pant = pygame.Surface((anc, alt))
pant_vent = pygame.Surface(vent.get_size())
pygame.display.set_caption("La Matanza Avanza")

r_vid1 = os.path.join(BASE_DIR, "F", "trenfondo.mp4")
r_vid2 = os.path.join(BASE_DIR, "trenfondo.mp4")
vid = cv2.VideoCapture(r_vid1)
if not vid.isOpened():
    vid.release()
    vid = cv2.VideoCapture(r_vid2)
wpan = int(anc * 0.32)

pizq, pder = fn.capas(anc, alt, wpan)
ftit, fbtn = fn.fuentes(alt)
t1, t2, r1, r2 = fn.titulos(ftit, wpan, alt)
btns = fn.btnlista(wpan, alt)

mgraf = fn.cargarmapa(anc, alt)
mgraf2 = fn.carmapa2(anc, alt)
anc_m2 = mgraf2.get_width()
alt_m2 = mgraf2.get_height()
camx, camy = 0, 0
andy00, andy01 = fn.cargabazar(anc, alt)
mira = fn.cargarmira(alt)
icons = fn.cariconos(alt)
f_comp = fn.fuente(fn.tam_f(alt, 0.035, 16))
pbazar = fn.crepuerta(anc, alt)
lay_bazar = fn.laytienda(anc, alt)
icons_baz = fn.cariconbaz(anc, alt, icons)

trans = {"estado": "ninguno", "inicio": 0}
msg_comp = ""
car_pist = 0
car_mol = 0
car_pan = 0
car_spd = 0
msg_pan = ""
msg_pan_h = 0
PRE_PIST = fn.PRE_PIST
PRE_MOL = fn.PRE_MOL
PRE_PAN = fn.PRE_PAN
PRE_SPD = fn.PRE_SPD
BMAX = 10

vida, esc, pts, ole, pesos, panchos, spds, pist, posmc, mapa, slot, molotovs = fn.cargardat(anc, alt)
jdat = fn.crearjug(anc, alt)
jdat.update({
    "vida": vida,
    "escudo": esc,
    "pesos": pesos,
    "puntos": pts,
    "oleada": ole,
    "panchos": panchos,
    "spds": spds,
    "pistola": pist,
    "balas": BMAX,
    "bmax": BMAX,
    "rec_hasta": 0,
    "mapa": mapa,
    "slot": slot,
    "molotovs": molotovs,
})
fn.escjug(jdat, anc, alt, mapa=mapa)
wini = anc_m2 if mapa == 2 else anc
hini = alt_m2 if mapa == 2 else alt
fn.ajustapos(jdat, posmc, wini, hini, mapa)
vidas = fn.carvidas(alt)
escudos = fn.carescudos(alt)
bftit, bfontder, bder = fn.bderrota(anc, alt)
enes = fn.crearene(anc_m2, alt_m2, min(8 + ole * 3, 40), ole, alt_p=alt, jdat=jdat) if mapa == 2 else []
proys = []
hb = fn.carhotbar(alt, icons)
clk = pygame.time.Clock()
estado = "menu"
ses_activa = False
part_carg = True
est_pausa = "juego" if mapa == 1 else ("continuara" if mapa == 2 else "bazar")
ult_guard = pygame.time.get_ticks()
jugando = True

def _aplinueva():
    global jdat, car_pist, car_mol, car_pan, car_spd, msg_comp, msg_pan, msg_pan_h, trans, enes, proys
    st = fn.nuevapart(anc, alt, jdat=jdat, bmax=BMAX, guardar=True)
    jdat = st["jdat"]
    car_pist, car_mol, car_pan, car_spd = st.get("car_pist", 0), st.get("car_mol", 0), st.get("car_pan", 0), st.get("car_spd", 0)
    msg_comp, msg_pan, msg_pan_h = st["msg_comp"], st["msg_pan"], st["msg_pan_hasta"]
    trans, enes, proys = st["trans"], st["enes"], st["proys"]

def _golpe():
    if estado == "juego" and trans["estado"] == "ninguno":
        if fn.iniataq(jdat, mouse):
            proys.append(fn.crearproy(jdat))
    elif estado == "continuara":
        mmundo = (mouse[0] + camx, mouse[1] + camy)
        if fn.iniataq(jdat, mmundo, enes=enes):
            proys.append(fn.crearproy(jdat))

def _disparar():
    if estado == "juego" and trans["estado"] == "ninguno":
        p = fn.disppist(jdat, mouse, 1)
    elif estado == "continuara":
        p = fn.disppist(jdat, (mouse[0] + camx, mouse[1] + camy), 2)
    else:
        p = None
    if p is not None:
        proys.append(p)

def _lanzmol():
    if estado == "juego" and trans["estado"] == "ninguno":
        fn.lanzmol(jdat, mouse, 1, anc, alt, obs_l=fn.obstaculos(1, anc, alt))
    elif estado == "continuara":
        p = fn.lanzmol(jdat, (mouse[0] + camx, mouse[1] + camy), 2, anc_m2, alt_m2, obs_l=fn.obstaculos(2, anc_m2, alt_m2))
        if p is not None:
            proys.append(p)

def _clic_izq():
    a = fn.accionclic(jdat)
    if a == "golpe":
        _golpe()
    elif a == "disparo":
        _disparar()
    elif a == "molotov":
        _lanzmol()

while jugando:
    ahora = pygame.time.get_ticks()
    if jdat.get("rec_hasta", 0) and ahora >= jdat["rec_hasta"]:
        jdat["balas"] = BMAX
        jdat["rec_hasta"] = 0

    mvent = pygame.mouse.get_pos()
    mouse = (mvent[0] * anc // vent.get_width(), mvent[1] * alt // vent.get_height())
    teclas = pygame.key.get_pressed()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            if ses_activa and estado in ("juego", "continuara", "bazar") and jdat["vida"] > 0:
                fn.guardjdat(jdat)
            jugando = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                if estado in ("juego", "continuara", "bazar"):
                    fn.inipausa(jdat)
                    est_pausa = estado
                    ses_activa = True
                    estado = "menu"
                    if jdat["vida"] > 0:
                        fn.guardjdat(jdat)
                elif estado in ("derrota", "victoria"):
                    ses_activa = False
                    part_carg = False
                    estado = "menu"
                elif estado == "menu":
                    if ses_activa:
                        fn.reanpausa(jdat, proys, enes)
                        if msg_pan_h > 0 and jdat.get("pausa_ini") is None:
                            pass
                        estado = est_pausa
                    else:
                        jugando = False
            elif ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_k):
                if estado in ("juego", "continuara"):
                    fn.inidash(jdat, teclas)
            elif ev.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                if estado in ("juego", "continuara"):
                    fn.selslot(jdat, ev.key - pygame.K_1 + 1)
            elif ev.key == pygame.K_e:
                if estado in ("juego", "continuara"):
                    msg_pan = fn.usarpancho(jdat)
                    msg_pan_h = pygame.time.get_ticks() + 1400
            elif ev.key == pygame.K_q:
                if estado in ("juego", "continuara"):
                    msg_pan = fn.usarspeed(jdat)
                    msg_pan_h = pygame.time.get_ticks() + 1400
            elif ev.key == pygame.K_j:
                _golpe()
            elif ev.key == pygame.K_SPACE:
                if estado == "juego" and jdat["mapa"] == 1 and jdat["hitbox"].colliderect(pbazar):
                    estado = "bazar"
                    jdat["mapa"] = "bazar"
                    trans["estado"] = "negro"
                    trans["inicio"] = pygame.time.get_ticks()
                elif estado == "bazar":
                    estado = "juego"
                    jdat["mapa"] = 1
                    trans["estado"] = "ninguno"
                    mgraf = fn.cargarmapa(anc, alt)
                    jdat["rect"].centerx = pbazar.centerx
                    jdat["rect"].top = int(alt * 0.36)
                    fn.ajustapos(jdat, jdat["rect"].topleft, anc, alt, 1)
                else:
                    _golpe()
            elif ev.key == pygame.K_BACKSPACE and estado == "bazar" and trans["estado"] == "andy03":
                trans["estado"] = "andy02"
                trans["inicio"] = pygame.time.get_ticks()
                car_pist, car_mol, car_pan, car_spd = 0, 0, 0, 0

        elif ev.type == pygame.MOUSEWHEEL:
            if estado in ("juego", "continuara") and ev.y != 0:
                fn.ciclarslot(jdat, -1 if ev.y > 0 else 1)

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
            mvent = ev.pos
            mouse = (mvent[0] * anc // vent.get_width(), mvent[1] * alt // vent.get_height())
            if estado == "bazar" and trans["estado"] == "andy03":
                t_pist, t_mol, t_pan, t_spd = lay_bazar["tarjetas"]
                if t_pan["rect"].collidepoint(mouse) and car_pan > 0:
                    car_pan -= 1
                    msg_comp = ""
                elif t_spd["rect"].collidepoint(mouse) and car_spd > 0:
                    car_spd -= 1
                    msg_comp = ""
                elif t_mol["rect"].collidepoint(mouse) and car_mol > 0:
                    car_mol -= 1
                    msg_comp = ""
                elif t_pist["rect"].collidepoint(mouse) and car_pist > 0:
                    car_pist = 0
                    msg_comp = ""
            else:
                _golpe()

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mvent = ev.pos
            mouse = (mvent[0] * anc // vent.get_width(), mvent[1] * alt // vent.get_height())
            if estado == "menu":
                for b in btns:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            if ses_activa:
                                fn.reanpausa(jdat, proys, enes)
                                estado = est_pausa
                            elif part_carg and jdat["vida"] > 0:
                                part_carg = False
                                ses_activa = True
                                m_act = jdat["mapa"]
                                estado = "juego" if m_act == 1 else ("continuara" if m_act == 2 else "bazar")
                                est_pausa = estado
                                trans = {"estado": "andy01" if m_act == "bazar" else "ninguno", "inicio": pygame.time.get_ticks()}
                            else:
                                _aplinueva()
                                ses_activa = True
                                estado = "juego"
                                est_pausa = "juego"
                        elif b["accion"] == "reiniciar":
                            _aplinueva()
                            part_carg = False
                            ses_activa = True
                            estado = "juego"
                            est_pausa = "juego"
                        elif b["accion"] == "ventana":
                            vent = fn.modopant(anc, alt, vent)
                            pant_vent = pygame.Surface(vent.get_size())
                            b["texto"] = "VENTANA" if vent.get_flags() & pygame.FULLSCREEN else "PANTALLA COMPLETA"
                        elif b["accion"] == "salir":
                            jugando = False
            elif estado == "bazar":
                if trans["estado"] == "andy02":
                    if lay_bazar["btn_salir_diag"].collidepoint(mouse):
                        estado = "juego"
                        jdat["mapa"] = 1
                        trans["estado"] = "ninguno"
                        mgraf = fn.cargarmapa(anc, alt)
                        jdat["rect"].centerx = pbazar.centerx
                        jdat["rect"].top = int(alt * 0.36)
                        fn.ajustapos(jdat, jdat["rect"].topleft, anc, alt, 1)
                    elif lay_bazar["btn_comprar_diag"].collidepoint(mouse):
                        trans["estado"] = "andy03"
                        trans["inicio"] = pygame.time.get_ticks()
                        msg_comp = ""
                        car_pist, car_mol, car_pan, car_spd = 0, 0, 0, 0
                elif trans["estado"] == "andy03":
                    t_pist, t_mol, t_pan, t_spd = lay_bazar["tarjetas"]
                    if lay_bazar["btn_volver"].collidepoint(mouse):
                        trans["estado"] = "andy02"
                        trans["inicio"] = pygame.time.get_ticks()
                        car_pist, car_mol, car_pan, car_spd = 0, 0, 0, 0
                        msg_comp = ""
                    elif lay_bazar["btn_vaciar"].collidepoint(mouse):
                        car_pist, car_mol, car_pan, car_spd = 0, 0, 0, 0
                        msg_comp = "Seleccion vaciada"
                    elif lay_bazar["btn_comprar"].collidepoint(mouse):
                        ctot = (PRE_PIST if car_pist else 0) + car_mol * PRE_MOL + car_pan * PRE_PAN + car_spd * PRE_SPD
                        if car_pist == 0 and car_mol == 0 and car_pan == 0 and car_spd == 0:
                            msg_comp = "Toca los iconos para agregar items"
                        elif jdat["pesos"] >= ctot:
                            jdat["pesos"] -= ctot
                            if car_pist:
                                jdat["pistola"] = True
                            jdat["molotovs"] = jdat.get("molotovs", 0) + car_mol
                            jdat["panchos"] += car_pan
                            jdat["spds"] += car_spd
                            car_pist, car_mol, car_pan, car_spd = 0, 0, 0, 0
                            msg_comp = "¡Compra confirmada!"
                            fn.guardjdat(jdat)
                        else:
                            msg_comp = f"Necesitas {ctot} pesos (tienes {jdat['pesos']})"
                    elif t_pist["btn_menos"].collidepoint(mouse):
                        car_pist = 0
                        msg_comp = ""
                    elif t_pist["btn_mas"].collidepoint(mouse) or t_pist["rect"].collidepoint(mouse):
                        if jdat.get("pistola", False):
                            msg_comp = "Ya tienes la pistola (solo 1 vez)"
                        else:
                            car_pist = 0 if car_pist else 1
                            msg_comp = ""
                    elif t_mol["btn_menos"].collidepoint(mouse):
                        if car_mol > 0:
                            car_mol -= 1
                            msg_comp = ""
                    elif t_mol["btn_mas"].collidepoint(mouse) or t_mol["rect"].collidepoint(mouse):
                        if jdat.get("molotovs", 0) + car_mol >= 99:
                            msg_comp = "Maximo 99 unidades"
                        else:
                            car_mol += 1
                            msg_comp = ""
                    elif t_pan["btn_menos"].collidepoint(mouse):
                        if car_pan > 0:
                            car_pan -= 1
                            msg_comp = ""
                    elif t_pan["btn_mas"].collidepoint(mouse) or t_pan["rect"].collidepoint(mouse):
                        if jdat.get("panchos", 0) + car_pan >= 99:
                            msg_comp = "Maximo 99 unidades"
                        else:
                            car_pan += 1
                            msg_comp = ""
                    elif t_spd["btn_menos"].collidepoint(mouse):
                        if car_spd > 0:
                            car_spd -= 1
                            msg_comp = ""
                    elif t_spd["btn_mas"].collidepoint(mouse) or t_spd["rect"].collidepoint(mouse):
                        if jdat.get("spds", 0) + car_spd >= 99:
                            msg_comp = "Maximo 99 unidades"
                        else:
                            car_spd += 1
                            msg_comp = ""
            elif estado in ("juego", "continuara"):
                n_hb = fn.slot_en(anc, alt, mouse)
                if n_hb is not None:
                    if n_hb <= 3:
                        fn.selslot(jdat, n_hb)
                    elif n_hb == 4:
                        msg_pan = fn.usarpancho(jdat)
                        msg_pan_h = pygame.time.get_ticks() + 1400
                    elif n_hb == 5:
                        msg_pan = fn.usarspeed(jdat)
                        msg_pan_h = pygame.time.get_ticks() + 1400
                else:
                    _clic_izq()
            elif estado in ("derrota", "victoria"):
                for b in bder:
                    if b["rect"].collidepoint(mouse):
                        if b["accion"] == "jugar":
                            _aplinueva()
                            part_carg = False
                            ses_activa = True
                            estado = "juego"
                            est_pausa = "juego"
                        elif b["accion"] == "menu":
                            ses_activa = False
                            part_carg = False
                            estado = "menu"

    if estado == "menu":
        fsurf = fn.framevideo(vid, anc, alt)
        fn.dibujar(pant, fsurf, pizq, pder, wpan, t1, t2, r1, r2, btns, fbtn, mouse)
    elif estado == "juego":
        fn.actataq(jdat)
        obs_m1 = fn.obstaculos(1, anc, alt)
        fn.moverjug(jdat, teclas, anc, alt, mapa=1, obs_l=obs_m1)
        fn.moverproy(proys, [], anc, alt, jdat, obs_l=obs_m1)
        fn.actefectos(jdat)

        if jdat["vida"] <= 0:
            estado = "derrota"
            ses_activa = False
            part_carg = False
            fn.limpmol(jdat, proys, enes)
            fn.resetguard(anc, alt)
            fn.dibperdida(pant, jdat, mgraf, bftit, bfontder, bder, mouse)
        elif jdat["rect"].right >= anc:
            estado = "continuara"
            jdat["mapa"] = 2
            fn.limpmol(jdat, proys, enes)
            fn.escjug(jdat, anc, alt, mapa=2)
            proys = []
            jdat["rect"].left = max(0, int(anc_m2 * 0.02))
            # Limitamos la posicion Y al rango caminable del mapa 2 (entre 20% y 80% de la altura)
            jdat["rect"].centery = max(int(alt_m2 * 0.20), min(int(alt_m2 * 0.80), int(jdat["rect"].centery * (alt_m2 / alt))))
            fn.ajustapos(jdat, jdat["rect"].topleft, anc_m2, alt_m2, 2)
            ole_act = jdat["oleada"]
            enes = fn.crearene(anc_m2, alt_m2, min(8 + ole_act * 3, 40), ole_act, alt_p=alt, jdat=jdat)
        else:
            fn.dibjuego(pant, mgraf, jdat, vidas, [], proys=proys, escudos=escudos)
            if jdat["hitbox"].colliderect(pbazar):
                txt_b = f_comp.render("[ESPACIO] BAZAR", False, (255, 255, 255))
                rtb = txt_b.get_rect(center=(pbazar.centerx, pbazar.top - 14))
                fn.dibrectalp(pant, (0, 0, 0, 180), rtb.inflate(14, 8), radius=4)
                pant.blit(txt_b, rtb)
            fn.dibrecur(pant, icons, jdat["pesos"])
            fn.diboleada(pant, jdat["oleada"], None, jdat)
            fn.dibhotbar(pant, hb, jdat, BMAX)
            if pygame.time.get_ticks() < msg_pan_h:
                tuso = f_comp.render(msg_pan, False, (255, 255, 255))
                pant.blit(tuso, tuso.get_rect(topright=(anc - int(alt * 0.02), int(alt * 0.02) + icons["peso"].get_height() + int(alt * 0.016))))
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
            pant.blit(andy01, (0, 0))
            fn.dibdiagbaz(pant, lay_bazar, mouse)
        elif trans["estado"] == "andy03":
            pant.blit(andy01, (0, 0))
            car = {"pistola": car_pist, "molotov": car_mol, "pancho": car_pan, "speed": car_spd}
            fn.dibtienda(pant, lay_bazar, jdat, car, mouse, icons_baz, msg_comp)
    elif estado == "continuara":
        fn.actataq(jdat)
        obs_m2 = fn.obstaculos(2, anc_m2, alt_m2)
        fn.moverjug(jdat, teclas, anc_m2, alt_m2, mapa=2, obs_l=obs_m2)
        camx = max(0, min(jdat["rect"].centerx - anc // 2, anc_m2 - anc))
        camy = max(0, min(jdat["rect"].centery - alt // 2, alt_m2 - alt))
        r_cam = pygame.Rect(camx, camy, anc, alt)
        fn.actene(enes, jdat, proys, obs_l=obs_m2, anc=anc_m2, alt=alt_m2, cam_rect=r_cam)
        fn.moverproy(proys, enes, anc_m2, alt_m2, jdat, obs_l=obs_m2)

        btns_m = pygame.mouse.get_pressed()
        if btns_m[0] and jdat.get("slot") == 2 and jdat.get("pistola") and jdat["balas"] > 0 and fn.slot_en(anc, alt, mouse) is None:
            _disparar()

        cola_vac = not jdat.get("ole_inf") or len(jdat["ole_inf"].get("cola", [])) == 0
        if jdat["rect"].right >= anc_m2 and cola_vac and len([e for e in enes if e["vida"] > 0]) == 0:
            ole_fin = jdat["oleada"] >= 20
            if jdat["oleada"] < 20:
                jdat["oleada"] += 1
            jdat["mapa"] = 1
            estado = "victoria" if ole_fin else "juego"
            fn.limpmol(jdat, proys, enes)
            if ole_fin:
                ses_activa = False
                part_carg = False
                fn.resetguard(anc, alt)
            fn.escjug(jdat, anc, alt, mapa=1)
            jdat["rect"].left = max(0, int(anc * 0.02))
            # Limitamos la posicion Y al rango caminable del mapa 1 (entre 42% y 54% de la altura)
            jdat["rect"].centery = max(int(alt * 0.42), min(int(alt * 0.54), int(jdat["rect"].centery * (alt / alt_m2))))
            enes, proys, jdat["drops"] = [], [], []
            mgraf = fn.cargarmapa(anc, alt)
            fn.ajustapos(jdat, jdat["rect"].topleft, anc, alt, 1)
        elif jdat["vida"] <= 0:
            estado = "derrota"
            ses_activa = False
            part_carg = False
            fn.limpmol(jdat, proys, enes)
            fn.resetguard(anc, alt)
            fn.dibperdida(pant, jdat, mgraf2, bftit, bfontder, bder, mouse, cam=(camx, camy))
        else:
            fn.dibjuego(pant, mgraf2, jdat, vidas, enes, proys=proys, cam=(camx, camy), escudos=escudos, mouse=mouse)
            fn.dibrecur(pant, icons, jdat["pesos"])
            fn.diboleada(pant, jdat["oleada"], enes, jdat)
            fn.dibhotbar(pant, hb, jdat, BMAX)
            if pygame.time.get_ticks() < msg_pan_h:
                tuso = f_comp.render(msg_pan, False, (255, 255, 255))
                pant.blit(tuso, tuso.get_rect(topright=(anc - int(alt * 0.02), int(alt * 0.02) + icons["peso"].get_height() + int(alt * 0.016))))
    elif estado == "derrota":
        mder = mgraf if jdat["mapa"] == 1 else mgraf2
        cder = (camx, camy) if jdat["mapa"] == 2 else (0, 0)
        fn.dibperdida(pant, jdat, mder, bftit, bfontder, bder, mouse, cam=cder)
    elif estado == "victoria":
        fn.dibvic(pant, jdat, mgraf, bftit, bfontder, bder, mouse, vidas=vidas, escudos=escudos)

    ver_mira = ((jdat.get("slot") == 2 and jdat.get("pistola")) or jdat.get("slot") == 3) and estado in ("juego", "continuara")
    pygame.mouse.set_visible(not ver_mira)
    if ver_mira:
        pant.blit(mira, mira.get_rect(center=mouse))

    if vent.get_size() == pant.get_size():
        vent.blit(pant, (0, 0))
    else:
        pygame.transform.scale(pant, vent.get_size(), pant_vent)
        vent.blit(pant_vent, (0, 0))
    pygame.display.flip()
    clk.tick(60)

    if ahora - ult_guard >= 5000:
        if ses_activa and estado in ("juego", "continuara", "bazar") and jdat["vida"] > 0:
            fn.guardjdat(jdat)
        ult_guard = ahora

vid.release()
pygame.quit()
sys.exit()
