# -*- coding: utf-8 -*-
import sys

def apply_patch():
    with open('funciones.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Reemplazo de cargardat y guardardat
    target_start = 'def cargardat(anc, alt):'
    target_end = 'def creahit(spr, pos):'

    idx1 = content.find(target_start)
    idx2 = content.find(target_end)

    if idx1 == -1 or idx2 == -1:
        print("ERROR: No se encontró la sección cargardat/guardardat")
        sys.exit(1)

    nuevo_bloque_datos = '''def rutapartida(slot):
    return f"F/Partida_{slot}.txt"

def migrar_datos_si_corresponde():
    os.makedirs("F", exist_ok=True)
    hay_partida = any(os.path.exists(rutapartida(s)) for s in range(1, 5))
    if not hay_partida and os.path.exists("F/Datos.txt"):
        try:
            with open("F/Datos.txt", "r", encoding="utf-8") as f:
                contenido = f.read()
            with open(rutapartida(1), "w", encoding="utf-8") as f:
                f.write("nombre=Partida 1\\n" + contenido)
        except Exception:
            pass

def listarpartidas(anc, alt):
    migrar_datos_si_corresponde()
    partidas = []
    for s in range(1, 5):
        ruta = rutapartida(s)
        if os.path.exists(ruta):
            info = {
                "slot": s,
                "existe": True,
                "nombre": f"Partida {s}",
                "oleada": 1,
                "puntos": 0,
                "pesos": 0,
                "vida": 5,
                "mapa": 1
            }
            try:
                with open(ruta, "r", encoding="utf-8") as arch:
                    for lin in arch:
                        if "=" not in lin:
                            continue
                        k, v = lin.strip().split("=", 1)
                        if k == "nombre":
                            info["nombre"] = v.strip() or f"Partida {s}"
                        elif k == "oleada":
                            info["oleada"] = max(1, int(v))
                        elif k in ("puntos", "pts"):
                            info["puntos"] = max(0, int(v))
                        elif k == "pesos":
                            info["pesos"] = max(0, int(v))
                        elif k == "vida":
                            info["vida"] = max(0, int(v))
                        elif k == "mapa":
                            info["mapa"] = v.strip()
            except Exception:
                pass
            partidas.append(info)
        else:
            partidas.append({
                "slot": s,
                "existe": False,
                "nombre": f"Partida {s}",
                "oleada": 1,
                "puntos": 0,
                "pesos": 0,
                "vida": 5,
                "mapa": 1
            })
    return partidas

def cargardat(anc, alt, slot=1):
    migrar_datos_si_corresponde()
    vida = 5
    esc = 0
    pts = 0
    ole = 1
    pesos = 0
    panchos = 0
    spds = 0
    pist = False
    posmc = (anc // 2, int(alt * 0.50))
    mapa = 1
    ruta = rutapartida(slot)
    if not os.path.exists(ruta) and slot == 1 and os.path.exists("F/Datos.txt"):
        ruta = "F/Datos.txt"

    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as arch:
            for lin in arch:
                if "=" not in lin:
                    continue
                k, v = lin.strip().split("=", 1)
                try:
                    if k == "vida":
                        vida = max(0, min(5, int(v)))
                    elif k in ("escudo", "esc"):
                        esc = max(0, min(3, int(v)))
                    elif k in ("puntos", "pts"):
                        pts = max(0, int(v))
                    elif k == "oleada":
                        ole = max(1, min(20, int(v)))
                    elif k == "pesos":
                        pesos = max(0, int(v))
                    elif k == "panchos":
                        panchos = max(0, int(v))
                    elif k in ("speeds", "spds"):
                        spds = max(0, int(v))
                    elif k == "pistola":
                        pist = v == "1"
                    elif k in ("posicion_mc", "posmc"):
                        x, y = v.split(",", 1)
                        posmc = (int(x), int(y))
                    elif k == "mapa":
                        mapa = "bazar" if v.lower() == "bazar" else max(1, min(2, int(v)))
                except ValueError:
                    continue

    return vida, esc, pts, ole, pesos, panchos, spds, pist, posmc, mapa

def guardardat(vida, pts, ole, pesos, panchos, pist, posmc, mapa, esc=0, spds=0, slot=1, nombre=""):
    os.makedirs("F", exist_ok=True)
    ruta = rutapartida(slot)
    nom_final = (nombre or "").strip()
    if not nom_final:
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as arch:
                    for lin in arch:
                        if lin.startswith("nombre="):
                            nom_final = lin.strip().split("=", 1)[1].strip()
                            break
            except Exception:
                pass
        if not nom_final:
            nom_final = f"Partida {slot}"

    with open(ruta, "w", encoding="utf-8") as arch:
        arch.write(f"nombre={nom_final}\\n")
        arch.write(f"vida={vida}\\n")
        arch.write(f"escudo={esc}\\n")
        arch.write(f"puntos={pts}\\n")
        arch.write(f"oleada={ole}\\n")
        arch.write(f"pesos={pesos}\\n")
        arch.write(f"panchos={panchos}\\n")
        arch.write(f"speeds={spds}\\n")
        arch.write(f"pistola={int(pist)}\\n")
        arch.write(f"posicion_mc={posmc[0]},{posmc[1]}\\n")
        arch.write(f"mapa={mapa}\\n")

    try:
        with open("F/Datos.txt", "w", encoding="utf-8") as arch:
            arch.write(f"nombre={nom_final}\\n")
            arch.write(f"vida={vida}\\n")
            arch.write(f"escudo={esc}\\n")
            arch.write(f"puntos={pts}\\n")
            arch.write(f"oleada={ole}\\n")
            arch.write(f"pesos={pesos}\\n")
            arch.write(f"panchos={panchos}\\n")
            arch.write(f"speeds={spds}\\n")
            arch.write(f"pistola={int(pist)}\\n")
            arch.write(f"posicion_mc={posmc[0]},{posmc[1]}\\n")
            arch.write(f"mapa={mapa}\\n")
    except Exception:
        pass

def crear_nueva_partida(slot, nombre, anc, alt):
    guardardat(
        vida=5, pts=0, ole=1, pesos=0, panchos=0, pist=False,
        posmc=(anc // 2, int(alt * 0.50)), mapa=1, esc=0, spds=0,
        slot=slot, nombre=nombre
    )

def borrarpartida(slot):
    ruta = rutapartida(slot)
    if os.path.exists(ruta):
        try:
            os.remove(ruta)
        except Exception:
            pass

'''

    content = content[:idx1] + nuevo_bloque_datos + content[idx2:]

    # Funciones de UI para slots al final
    ui_slots_code = '''

def layout_slots(anc, alt, modal_crear=None, modal_borrar=None):
    w_card = int(anc * 0.72)
    h_card = int(alt * 0.125)
    x_card = (anc - w_card) // 2
    y_ini = int(alt * 0.185)
    esp_y = int(alt * 0.145)

    slots_rects = []
    for s in range(1, 5):
        y_c = y_ini + (s - 1) * esp_y
        rcard = pygame.Rect(x_card, y_c, w_card, h_card)
        w_btn = int(w_card * 0.15)
        h_btn = int(h_card * 0.62)
        y_b = y_c + (h_card - h_btn) // 2
        rjugar = pygame.Rect(x_card + w_card - w_btn * 2 - int(w_card * 0.03), y_b, w_btn, h_btn)
        rborrar = pygame.Rect(x_card + w_card - w_btn - int(w_card * 0.015), y_b, w_btn, h_btn)
        slots_rects.append({
            "slot": s,
            "rect_card": rcard,
            "rect_jugar": rjugar,
            "rect_borrar": rborrar
        })

    w_volver = int(w_card * 0.28)
    h_volver = int(alt * 0.07)
    rvolver = pygame.Rect((anc - w_volver) // 2, int(alt * 0.88), w_volver, h_volver)

    mcrear_rects = None
    if modal_crear:
        w_mod = int(anc * 0.52)
        h_mod = int(alt * 0.38)
        x_mod = (anc - w_mod) // 2
        y_mod = (alt - h_mod) // 2
        rmod = pygame.Rect(x_mod, y_mod, w_mod, h_mod)
        w_inp = int(w_mod * 0.82)
        h_inp = int(h_mod * 0.24)
        rinp = pygame.Rect(x_mod + (w_mod - w_inp) // 2, y_mod + int(h_mod * 0.38), w_inp, h_inp)
        w_b = int(w_mod * 0.36)
        h_b = int(h_mod * 0.20)
        y_b = y_mod + int(h_mod * 0.70)
        raceptar = pygame.Rect(x_mod + int(w_mod * 0.10), y_b, w_b, h_b)
        rcancelar = pygame.Rect(x_mod + int(w_mod * 0.54), y_b, w_b, h_b)
        mcrear_rects = {
            "rect_modal": rmod,
            "rect_input": rinp,
            "rect_aceptar": raceptar,
            "rect_cancelar": rcancelar
        }

    mborrar_rects = None
    if modal_borrar:
        w_mod = int(anc * 0.48)
        h_mod = int(alt * 0.34)
        x_mod = (anc - w_mod) // 2
        y_mod = (alt - h_mod) // 2
        rmod = pygame.Rect(x_mod, y_mod, w_mod, h_mod)
        w_b = int(w_mod * 0.38)
        h_b = int(h_mod * 0.22)
        y_b = y_mod + int(h_mod * 0.68)
        rconfirmar = pygame.Rect(x_mod + int(w_mod * 0.08), y_b, w_b, h_b)
        rcancelar = pygame.Rect(x_mod + int(w_mod * 0.54), y_b, w_b, h_b)
        mborrar_rects = {
            "rect_modal": rmod,
            "rect_confirmar": rconfirmar,
            "rect_cancelar": rcancelar
        }

    return {
        "slots": slots_rects,
        "rect_volver": rvolver,
        "modal_crear": mcrear_rects,
        "modal_borrar": mborrar_rects
    }

def dibujarslots(pant, fsurf, anc, alt, partidas, mouse, modal_crear=None, modal_borrar=None):
    if fsurf:
        pant.blit(fsurf, (0, 0))
    s_oscura = pygame.Surface((anc, alt), pygame.SRCALPHA)
    s_oscura.fill((0, 0, 0, 190))
    pant.blit(s_oscura, (0, 0))

    ruta_fnt = "F/minecraft.ttf" if os.path.exists("F/minecraft.ttf") else "minecraft.ttf"
    f_tit = pygame.font.Font(ruta_fnt, max(20, int(alt * 0.052)))
    f_med = pygame.font.Font(ruta_fnt, max(16, int(alt * 0.030)))
    f_chi = pygame.font.Font(ruta_fnt, max(13, int(alt * 0.022)))

    t_tit = grosor(f_tit, "PARTIDAS GUARDADAS", (255, 255, 255), 2)
    pant.blit(t_tit, t_tit.get_rect(center=(anc // 2, int(alt * 0.075))))

    t_sub = f_chi.render("Elige una partida para jugar o crea una nueva (Max. 4)", True, (200, 200, 200))
    pant.blit(t_sub, t_sub.get_rect(center=(anc // 2, int(alt * 0.135))))

    layout = layout_slots(anc, alt, modal_crear, modal_borrar)

    for p in partidas:
        s_idx = p["slot"] - 1
        s_layout = layout["slots"][s_idx]
        rcard = s_layout["rect_card"]
        hover_card = rcard.collidepoint(mouse) and not modal_crear and not modal_borrar

        if p["existe"]:
            col_bg = (55, 58, 68) if hover_card else (38, 40, 48)
            col_bor = (180, 190, 220) if hover_card else (85, 90, 110)
            pygame.draw.rect(pant, col_bg, rcard, border_radius=8)
            pygame.draw.rect(pant, col_bor, rcard, width=2, border_radius=8)

            txt_slot = f_chi.render(f"SLOT {p['slot']}", True, (255, 215, 0))
            pant.blit(txt_slot, (rcard.x + int(rcard.w * 0.025), rcard.y + int(rcard.h * 0.18)))

            txt_nom = f_med.render(str(p["nombre"])[:18], True, (255, 255, 255))
            pant.blit(txt_nom, (rcard.x + int(rcard.w * 0.025), rcard.y + int(rcard.h * 0.48)))

            nom_mapa = f"Mapa {p['mapa']}" if str(p['mapa']) in ('1', '2') else str(p['mapa']).capitalize()
            txt_info = f_chi.render(f"Oleada: {p['oleada']}  |  Pts: {p['puntos']}  |  ${p['pesos']}", True, (220, 220, 220))
            txt_map = f_chi.render(f"{nom_mapa}", True, (160, 200, 240))
            pant.blit(txt_info, (rcard.x + int(rcard.w * 0.33), rcard.y + int(rcard.h * 0.28)))
            pant.blit(txt_map, (rcard.x + int(rcard.w * 0.33), rcard.y + int(rcard.h * 0.58)))

            rj = s_layout["rect_jugar"]
            hj = rj.collidepoint(mouse) and not modal_crear and not modal_borrar
            col_j = (45, 140, 60) if hj else (35, 105, 45)
            pygame.draw.rect(pant, col_j, rj, border_radius=6)
            pygame.draw.rect(pant, (90, 230, 110) if hj else (50, 160, 70), rj, width=2, border_radius=6)
            tj = f_chi.render("JUGAR", True, (255, 255, 255))
            pant.blit(tj, tj.get_rect(center=rj.center))

            rb = s_layout["rect_borrar"]
            hb = rb.collidepoint(mouse) and not modal_crear and not modal_borrar
            col_b = (170, 45, 45) if hb else (125, 35, 35)
            pygame.draw.rect(pant, col_b, rb, border_radius=6)
            pygame.draw.rect(pant, (240, 90, 90) if hb else (170, 60, 60), rb, width=2, border_radius=6)
            tb = f_chi.render("BORRAR", True, (255, 255, 255))
            pant.blit(tb, tb.get_rect(center=rb.center))
        else:
            col_bg = (42, 44, 52) if hover_card else (28, 29, 36)
            col_bor = (140, 150, 175) if hover_card else (65, 70, 85)
            pygame.draw.rect(pant, col_bg, rcard, border_radius=8)
            pygame.draw.rect(pant, col_bor, rcard, width=2, border_radius=8)

            txt_vacio = f_med.render(f"+ NUEVA PARTIDA (SLOT {p['slot']})", True, (130, 220, 150) if hover_card else (110, 175, 130))
            sub_vacio = f_chi.render("Click aqui para crear una partida con tu nombre", True, (160, 160, 170))
            pant.blit(txt_vacio, txt_vacio.get_rect(center=(rcard.centerx, rcard.y + int(rcard.h * 0.38))))
            pant.blit(sub_vacio, sub_vacio.get_rect(center=(rcard.centerx, rcard.y + int(rcard.h * 0.70))))

    rv = layout["rect_volver"]
    hv = rv.collidepoint(mouse) and not modal_crear and not modal_borrar
    col_v = (85, 85, 95) if hv else (60, 60, 70)
    pygame.draw.rect(pant, col_v, rv, border_radius=6)
    pygame.draw.rect(pant, (150, 150, 170) if hv else (100, 100, 120), rv, width=2, border_radius=6)
    tv = f_med.render("VOLVER", True, (255, 255, 255))
    pant.blit(tv, tv.get_rect(center=rv.center))

    if modal_crear and layout["modal_crear"]:
        mc = layout["modal_crear"]
        s_extra = pygame.Surface((anc, alt), pygame.SRCALPHA)
        s_extra.fill((0, 0, 0, 160))
        pant.blit(s_extra, (0, 0))

        rmod = mc["rect_modal"]
        pygame.draw.rect(pant, (30, 32, 40), rmod, border_radius=10)
        pygame.draw.rect(pant, (100, 150, 220), rmod, width=3, border_radius=10)

        t_m = grosor(f_med, f"NUEVA PARTIDA - RANURA {modal_crear['slot']}", (255, 255, 255), 2)
        pant.blit(t_m, t_m.get_rect(center=(rmod.centerx, rmod.y + int(rmod.h * 0.16))))

        t_lbl = f_chi.render("Ingresa un nombre para tu partida:", True, (210, 210, 210))
        pant.blit(t_lbl, t_lbl.get_rect(center=(rmod.centerx, rmod.y + int(rmod.h * 0.30))))

        rinp = mc["rect_input"]
        pygame.draw.rect(pant, (15, 17, 22), rinp, border_radius=6)
        pygame.draw.rect(pant, (80, 180, 255), rinp, width=2, border_radius=6)

        cursor = "|" if (pygame.time.get_ticks() % 1000 < 500) else " "
        txt_show = (modal_crear.get("texto", "") + cursor)
        t_inp = f_med.render(txt_show, True, (255, 255, 255))
        pant.blit(t_inp, (rinp.x + 14, rinp.y + (rinp.h - t_inp.get_height()) // 2))

        ra = mc["rect_aceptar"]
        ha = ra.collidepoint(mouse)
        pygame.draw.rect(pant, (45, 140, 60) if ha else (35, 110, 48), ra, border_radius=6)
        pygame.draw.rect(pant, (100, 230, 120) if ha else (60, 165, 80), ra, width=2, border_radius=6)
        ta = f_chi.render("CREAR Y JUGAR", True, (255, 255, 255))
        pant.blit(ta, ta.get_rect(center=ra.center))

        rc = mc["rect_cancelar"]
        hc = rc.collidepoint(mouse)
        pygame.draw.rect(pant, (130, 45, 45) if hc else (95, 38, 38), rc, border_radius=6)
        pygame.draw.rect(pant, (220, 85, 85) if hc else (160, 60, 60), rc, width=2, border_radius=6)
        tc = f_chi.render("CANCELAR", True, (255, 255, 255))
        pant.blit(tc, tc.get_rect(center=rc.center))

    elif modal_borrar and layout["modal_borrar"]:
        mb = layout["modal_borrar"]
        s_extra = pygame.Surface((anc, alt), pygame.SRCALPHA)
        s_extra.fill((0, 0, 0, 160))
        pant.blit(s_extra, (0, 0))

        rmod = mb["rect_modal"]
        pygame.draw.rect(pant, (35, 25, 25), rmod, border_radius=10)
        pygame.draw.rect(pant, (220, 80, 80), rmod, width=3, border_radius=10)

        t_m = grosor(f_med, "BORRAR PARTIDA", (255, 100, 100), 2)
        pant.blit(t_m, t_m.get_rect(center=(rmod.centerx, rmod.y + int(rmod.h * 0.20))))

        t_lbl = f_chi.render(f"¿Deseas borrar '{modal_borrar['nombre']}'?", True, (230, 230, 230))
        t_sub = f_chi.render("Se perdera todo el progreso guardado.", True, (190, 150, 150))
        pant.blit(t_lbl, t_lbl.get_rect(center=(rmod.centerx, rmod.y + int(rmod.h * 0.40))))
        pant.blit(t_sub, t_sub.get_rect(center=(rmod.centerx, rmod.y + int(rmod.h * 0.52))))

        rcf = mb["rect_confirmar"]
        hcf = rcf.collidepoint(mouse)
        pygame.draw.rect(pant, (180, 45, 45) if hcf else (140, 35, 35), rcf, border_radius=6)
        pygame.draw.rect(pant, (255, 95, 95) if hcf else (190, 60, 60), rcf, width=2, border_radius=6)
        tcf = f_chi.render("CONFIRMAR", True, (255, 255, 255))
        pant.blit(tcf, tcf.get_rect(center=rcf.center))

        rc = mb["rect_cancelar"]
        hc = rc.collidepoint(mouse)
        pygame.draw.rect(pant, (75, 75, 85) if hc else (55, 55, 65), rc, border_radius=6)
        pygame.draw.rect(pant, (140, 140, 160) if hc else (100, 100, 120), rc, width=2, border_radius=6)
        tc = f_chi.render("CANCELAR", True, (255, 255, 255))
        pant.blit(tc, tc.get_rect(center=rc.center))
'''

    content = content + ui_slots_code

    with open('funciones.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("funciones.py parcheado con éxito.")

if __name__ == '__main__':
    apply_patch()

