import pygame
import cv2
import os
import math
import random
import numpy as np

_fnt_rec = {}
_SOMBRAS = {}
_CSPRS_ENE = {}
_CDROPS = {}
_CBALAS = {}

daño_PUNO = 16
daño_BALA = 28

TIPOS_ENE = {
    "hincha": {
        "hp": 30, "vel_mult": 1.0, "daño": 0.5, "esc": 1.0, "tint": None,
        "pts": 10, "pesos": (15, 30), "alc_m": 1.15, "esp": 900
    },
    "barra": {
        "hp": 20, "vel_mult": 1.45, "daño": 0.5, "esc": 0.92, "tint": ("add", (55, 0, 0)),
        "pts": 15, "pesos": (20, 40), "alc_m": 1.05, "esp": 650
    },
    "tanque": {
        "hp": 90, "vel_mult": 0.72, "daño": 1.0, "esc": 1.35, "tint": ("mult", (255, 205, 120)),
        "pts": 30, "pesos": (45, 75), "alc_m": 1.25, "esp": 1150
    },
    "jefe": {
        "hp": 320, "vel_mult": 0.85, "daño": 1.0, "esc": 2.1, "tint": ("add", (45, 5, 0)),
        "pts": 200, "pesos": (180, 260), "alc_m": 1.35, "esp": 1050
    },
}

def cargardat(anc, alt):
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

def guardardat(vida, pts, ole, pesos, panchos, pist, posmc, mapa, esc=0, spds=0):
    with open("F/Datos.txt", "w", encoding="utf-8") as arch:
        arch.write(f"vida={vida}\n")
        arch.write(f"escudo={esc}\n")
        arch.write(f"puntos={pts}\n")
        arch.write(f"oleada={ole}\n")
        arch.write(f"pesos={pesos}\n")
        arch.write(f"panchos={panchos}\n")
        arch.write(f"speeds={spds}\n")
        arch.write(f"pistola={int(pist)}\n")
        arch.write(f"posicion_mc={posmc[0]},{posmc[1]}\n")
        arch.write(f"mapa={mapa}\n")

def creahit(spr, pos):
    hitbox = spr.get_bounding_rect().move(pos)
    hitbox.inflate_ip(-max(2, int(hitbox.width * 0.25)), -max(2, int(hitbox.height * 0.20)))
    return hitbox

def colpies(r):
    w = max(4, int(r.width * 0.38))
    h = max(4, int(r.height * 0.16))
    return pygame.Rect(r.centerx - w // 2, r.bottom - h, w, h)

def obstaculos(mapa, anc, alt):
    if mapa == 2:
        return [
            pygame.Rect(0, 0, anc, int(alt * 0.095)),
            pygame.Rect(int(anc * 0.595), int(alt * 0.148), int(anc * 0.215), int(alt * 0.200)),
            pygame.Rect(int(anc * 0.870), int(alt * 0.070), int(anc * 0.130), int(alt * 0.170)),
            pygame.Rect(int(anc * 0.895), int(alt * 0.380), int(anc * 0.105), int(alt * 0.400)),
            pygame.Rect(0, int(alt * 0.890), anc, int(alt * 0.110)),
            pygame.Rect(int(anc * 0.112), int(alt * 0.445), int(anc * 0.100), int(alt * 0.075)),
            pygame.Rect(int(anc * 0.082), int(alt * 0.805), int(anc * 0.098), int(alt * 0.065)),
            pygame.Rect(int(anc * 0.238), int(alt * 0.100), int(anc * 0.030), int(alt * 0.115)),
            pygame.Rect(int(anc * 0.450), int(alt * 0.482), int(anc * 0.015), int(alt * 0.012)),
            pygame.Rect(int(anc * 0.283), int(alt * 0.377), int(anc * 0.015), int(alt * 0.012)),
        ]
    return [
        pygame.Rect(0, 0, anc, int(alt * 0.335)),
        pygame.Rect(0, int(alt * 0.335), int(anc * 0.070), int(alt * 0.13)),
        pygame.Rect(0, int(alt * 0.56), int(anc * 0.05), int(alt * 0.44)),
        pygame.Rect(int(anc * 0.05), int(alt * 0.70), int(anc * 0.10), int(alt * 0.30)),
        pygame.Rect(int(anc * 0.15), int(alt * 0.83), int(anc * 0.275), int(alt * 0.17)),
        pygame.Rect(int(anc * 0.575), int(alt * 0.83), int(anc * 0.425), int(alt * 0.17)),
        pygame.Rect(int(anc * 0.875), int(alt * 0.56), int(anc * 0.125), int(alt * 0.27)),
    ]

def ajustapos(jdat, posmc, anc, alt, mapa):
    r = jdat["rect"]
    r.left = max(0, min(posmc[0], anc - r.width))
    r.top = max(0, min(posmc[1], alt - r.height))

    obs_l = obstaculos(mapa, anc, alt)
    pies = colpies(r)
    for obs in obs_l:
        if pies.colliderect(obs):
            if obs.top <= 0:
                r.top = obs.bottom
            elif obs.bottom >= alt:
                r.bottom = obs.top
            elif obs.left <= 0:
                r.left = obs.right
            elif obs.right >= anc:
                r.right = obs.left
            pies = colpies(r)

    spr = jdat["sprs"][jdat["dir"]][0]
    jdat["hitbox"] = creahit(spr, r.topleft)

def crearpuerta(anc, alt):
    return pygame.Rect(int(anc * 0.435), int(alt * 0.30), int(anc * 0.06), int(alt * 0.09))

def cargarmapa2(anc, alt, esc=2.4):
    img = pygame.image.load("Sprites/mapa2n.jpeg")
    return pygame.transform.scale(img, (int(anc * esc), int(alt * esc))).convert()

def _recortafondo(ruta):
    bgr = cv2.imread(ruta)
    if bgr is None:
        return pygame.image.load(ruta).convert_alpha()
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    bg_cand = ((hsv[:, :, 1] < 28) & (hsv[:, :, 2] > 215)).astype("uint8") * 255
    _, lbl = cv2.connectedComponents(bg_cand)
    bordes = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    bordes.discard(0)
    m_fondo = np.isin(lbl, list(bordes))
    m_fg = ~m_fondo
    ys, xs = np.where(m_fg)
    if len(xs) > 0 and len(ys) > 0:
        x0, x1 = xs.min(), xs.max() + 1
        y0, y1 = ys.min(), ys.max() + 1
    else:
        x0, y0, x1, y1 = 0, 0, bgr.shape[1], bgr.shape[0]
    rgb = cv2.cvtColor(bgr[y0:y1, x0:x1], cv2.COLOR_BGR2RGB)
    alpha = (m_fg[y0:y1, x0:x1].astype("uint8") * 255)
    rgba = np.dstack((rgb, alpha))
    return pygame.image.frombuffer(rgba.tobytes(), (x1 - x0, y1 - y0), "RGBA").convert_alpha()

def cargarvidas(alt):
    vidas = []
    h = int(alt * 0.14)
    for n in range(6):
        img = pygame.image.load(f"Sprites/Vida/vida{n:02d}.png").convert_alpha()
        prop = img.get_width() / img.get_height()
        vidas.append(pygame.transform.scale(img, (int(h * prop), h)))
    return vidas

def cargarescudos(alt):
    escudos = []
    hesc = int(alt * 0.115)
    wesc = int(alt * 0.14 * 3.0)
    for n in range(1, 5):
        ruta = f"Sprites/escudo/escudo{n}.jpg"
        if not os.path.exists(ruta):
            ruta = f"escudo{n}.jpg"
        surf = _recortafondo(ruta)
        escudos.append(pygame.transform.smoothscale(surf, (wesc, hesc)))
    return escudos

def tintarsurf(surf, tinte):
    if not tinte:
        return surf
    modo, col = tinte
    copia = surf.copy()
    flag = pygame.BLEND_RGB_ADD if modo == "add" else pygame.BLEND_RGB_MULT
    copia.fill(col, special_flags=flag)
    return copia

def blancsurf(surf):
    copia = surf.copy()
    copia.fill((110, 110, 110), special_flags=pygame.BLEND_RGB_ADD)
    return copia

def addtxtflot(jdat, txt, x, y, col=(255, 255, 255)):
    if jdat is None:
        return
    jdat.setdefault("textos", []).append({
        "texto": str(txt),
        "x": float(x),
        "y": float(y),
        "inicio": pygame.time.get_ticks(),
        "dur": 850,
        "color": col
    })

def addchispas(jdat, x, y, col=(255, 215, 60), cant=6, fuerza=4.5):
    if jdat is None:
        return
    ahora = pygame.time.get_ticks()
    chispas = jdat.setdefault("chispas", [])
    for _ in range(cant):
        ang = random.uniform(0, math.tau)
        v = random.uniform(0.35, 1.0) * fuerza
        chispas.append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(ang) * v,
            "vy": math.sin(ang) * v,
            "inicio": ahora,
            "vida": random.randint(200, 420),
            "color": col,
            "radio": random.choice((2, 3, 3, 4)),
        })

def setbanner(jdat, txt, sub="", dur_ms=2400):
    if jdat is None:
        return
    jdat["banner"] = {
        "texto": txt,
        "sub": sub,
        "inicio": pygame.time.get_ticks(),
        "dur": dur_ms
    }

def dibujarvida(pant, vidas, jdat, escudos=None):
    vida = max(0, min(jdat["vida"], 5))
    sprv = 5 - vida
    rvida = vidas[sprv].get_rect(bottomleft=(0, pant.get_height()))
    if escudos:
        nesc = max(0, min(jdat.get("escudo", 0), 3))
        iesc = 3 - nesc
        resc = escudos[iesc].get_rect(bottomleft=(0, rvida.top - max(2, int(pant.get_height() * 0.005))))
        pant.blit(escudos[iesc], resc)
    pant.blit(vidas[sprv], rvida)

    ahora = pygame.time.get_ticks()
    alt = pant.get_height()
    tam_f = max(18, int(alt * 0.024))
    if tam_f not in _fnt_rec:
        _fnt_rec[tam_f] = pygame.font.Font(None, tam_f)
    fdash = _fnt_rec[tam_f]
    xdash = rvida.right + max(14, int(alt * 0.02))
    ydash = alt - max(22, int(alt * 0.032))
    barra = pygame.Rect(xdash, ydash, int(alt * 0.18), max(8, int(alt * 0.014)))
    cd_fin = jdat.get("dash_cd_hasta", 0)
    cd_dur = max(1, jdat.get("dash_cd_dur", 950))
    carga = max(0.0, min(1.0, 1.0 - max(0, cd_fin - ahora) / cd_dur))
    lbldash = fdash.render("DASH [SHIFT]", True, (255, 255, 255))
    pant.blit(lbldash, (barra.x, barra.y - lbldash.get_height() - 2))
    pygame.draw.rect(pant, (30, 30, 30), barra, border_radius=4)
    colb = (90, 220, 110) if carga >= 1.0 else (255, 215, 60)
    if carga > 0:
        pygame.draw.rect(pant, colb, pygame.Rect(barra.x, barra.y, int(barra.width * carga), barra.height), border_radius=4)
    pygame.draw.rect(pant, (255, 255, 255), barra, 1, border_radius=4)

def dañojug(jdat, ahora, cant=0.5, orig=None, anc_m=None, alt_m=None, obs_l=None):
    if ahora < jdat.get("dash_invul_hasta", 0):
        return False

    c = float(cant)
    tot = jdat.get("daño_acum", 0.0) + c
    quitar = int(tot)
    jdat["daño_acum"] = round(tot - quitar, 4)

    consesc = False
    if quitar > 0:
        rest = quitar
        while rest > 0:
            if jdat.get("escudo", 0) > 0:
                jdat["escudo"] -= 1
                consesc = True
            else:
                jdat["vida"] = max(0, jdat["vida"] - 1)
                consesc = False
            rest -= 1

    jdat["ultdaño"] = ahora
    jdat["golpe_hasta"] = ahora + 220
    jdat["shake_hasta"] = ahora + 220

    t_esc = jdat.get("escudo", 0) > 0 or consesc
    if quitar > 0:
        txt = f"-{quitar} ESCUDO" if consesc else f"-{quitar} VIDA"
        colt = (120, 200, 255) if consesc else (235, 65, 65)
    else:
        txt = "-0.5 ESCUDO" if t_esc else "-0.5 VIDA"
        colt = (160, 220, 255) if t_esc else (255, 130, 130)

    addtxtflot(jdat, txt, jdat["rect"].centerx, jdat["rect"].top - 10, colt)
    addchispas(jdat, jdat["rect"].centerx, jdat["rect"].centery, (230, 60, 60), cant=8, fuerza=5.0)

    if orig is not None and anc_m and alt_m:
        ox, oy = orig["rect"].center if isinstance(orig, dict) and "rect" in orig else (orig.centerx, orig.centery)
        dx = jdat["rect"].centerx - ox
        dy = jdat["rect"].centery - oy
        dist = math.hypot(dx, dy)
        if dist > 0:
            emp = max(10, int(jdat["rect"].height * 0.35))
            ex = round((dx / dist) * emp)
            ey = round((dy / dist) * emp)
            jdat["rect"].x = max(0, min(anc_m - jdat["rect"].width, jdat["rect"].x + ex))
            if obs_l and any(colpies(jdat["rect"]).colliderect(o) for o in obs_l):
                jdat["rect"].x -= ex
            jdat["rect"].y = max(0, min(alt_m - jdat["rect"].height, jdat["rect"].y + ey))
            if obs_l and any(colpies(jdat["rect"]).colliderect(o) for o in obs_l):
                jdat["rect"].y -= ey
    return True

def recibirdaño(jdat, objs):
    ahora = pygame.time.get_ticks()
    if ahora - jdat.get("ultdaño", -1000) < 900 or ahora < jdat.get("dash_invul_hasta", 0):
        return

    for o in objs:
        if isinstance(o, dict) and o["vida"] <= 0:
            continue
        h = o["hitbox"] if isinstance(o, dict) else o
        if jdat["hitbox"].colliderect(h):
            d = o.get("daño", 0.5) if isinstance(o, dict) else 0.5
            dañojug(jdat, ahora, cant=d, orig=o)
            return

def rojospr(spr):
    img = spr.copy()
    img.fill((255, 70, 70, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return img

def _sprsene(tipo, alt_p):
    k = (tipo, alt_p)
    if k in _CSPRS_ENE:
        return _CSPRS_ENE[k]

    cfg = TIPOS_ENE.get(tipo, TIPOS_ENE["hincha"])
    hj = max(16, int(alt_p * 0.075 * cfg["esc"]))
    wj = max(12, int(hj * (52 / 96)))
    sec = {
        "abajo": [0, 1, 2],
        "arriba": [4, 5, 6],
        "izquierda": [8, 9, 10],
        "derecha": [12, 13, 14]
    }
    sprs = {}
    sprat = {}
    for d, nums in sec.items():
        sprs[d] = []
        sprat[d] = []
        for n in nums:
            img = pygame.image.load(f"Sprites/Boca/Boca{n:03d}.png").convert_alpha()
            img_e = tintarsurf(pygame.transform.scale(img, (wj, hj)), cfg["tint"])
            sprs[d].append(img_e)
            imga = pygame.image.load(f"Sprites/Boca/BA/BA{n:02d}.png").convert_alpha()
            imga_e = tintarsurf(pygame.transform.scale(imga, (wj, hj)), cfg["tint"])
            sprat[d].append(imga_e)

    sprr = {d: [blancsurf(rojospr(img)) for img in imgs] for d, imgs in sprs.items()}
    spratr = {d: [blancsurf(rojospr(img)) for img in imgs] for d, imgs in sprat.items()}
    dat = (wj, hj, sprs, sprr, sprat, spratr)
    _CSPRS_ENE[k] = dat
    return dat

def colaoleada(ole):
    tot = min(45, 5 + 3 * ole)
    p_tanq = 0.0 if ole < 4 else min(0.30, 0.10 + 0.02 * (ole - 4))
    p_barr = 0.0 if ole < 2 else min(0.40, 0.20 + 0.03 * (ole - 2))
    cola = []
    for _ in range(tot):
        r = random.random()
        if r < p_tanq:
            cola.append("tanque")
        elif r < p_tanq + p_barr:
            cola.append("barra")
        else:
            cola.append("hincha")
    jefes = ole // 5 if ole % 5 == 0 else 0
    for _ in range(jefes):
        cola.insert(len(cola) // 3, "jefe")
    return {
        "num": ole,
        "cola": cola,
        "tot": len(cola),
        "jefe": jefes > 0,
        "ultspawn": pygame.time.get_ticks(),
        "interv_ms": max(420, int((1.35 - 0.06 * ole) * 1000)),
        "max_sim": min(24, 7 + ole),
        "fin": False,
    }

def instene(tipo, ole, anc, alt, alt_p, exis, jdat=None, idx=0, tot_esp=10):
    cfg = TIPOS_ENE.get(tipo, TIPOS_ENE["hincha"])
    wj, hj, sprs, sprr, sprat, spratr = _sprsene(tipo, alt_p)
    minx = min(int(anc * 0.10), max(0, anc - wj))
    maxx = max(minx, int(anc * 0.88) - wj)
    miny = min(int(alt * 0.14), max(0, alt - hj))
    maxy = max(miny, int(alt * 0.84) - hj)
    esp = max(12, int(wj * 0.65))
    obs_l = obstaculos(2, anc, alt)

    r = sprs["abajo"][0].get_rect()
    jx = jdat["rect"].centerx if jdat else anc // 4
    jy = jdat["rect"].centery if jdat else alt // 2
    dmin_jug = max(260, int(alt_p * 0.42))

    for intent in range(55):
        if intent < 35 and jdat is not None:
            lado = random.choice(("der", "arr", "aba", "azar"))
            if lado == "der":
                rx = random.randint(max(minx, int(anc * 0.65)), maxx)
                ry = random.randint(miny, maxy)
            elif lado == "arr":
                rx = random.randint(minx, maxx)
                ry = random.randint(miny, min(maxy, int(alt * 0.30)))
            elif lado == "aba":
                rx = random.randint(minx, maxx)
                ry = random.randint(max(miny, int(alt * 0.68)), maxy)
            else:
                rx = random.randint(minx, maxx)
                ry = random.randint(miny, maxy)
            r.topleft = (rx, ry)
        else:
            r.topleft = (random.randint(minx, maxx), random.randint(miny, maxy))

        if math.hypot(r.centerx - jx, r.centery - jy) < dmin_jug and intent < 40:
            continue
        pies = colpies(r)
        if any(pies.colliderect(o) for o in obs_l):
            continue
        if all(not r.inflate(esp, esp).colliderect(o["rect"]) for o in exis):
            break

    hp_m = round(cfg["hp"] * (1 + 0.10 * (ole - 1)))
    vbase = alt_p * 0.0040 * cfg["vel_mult"] * min(1.35, 1 + 0.015 * (ole - 1)) * random.uniform(0.92, 1.08)
    angbase = (idx / max(1, tot_esp)) * 2 * math.pi + random.uniform(-0.2, 0.2)

    return {
        "nom": f"enemigo {tipo}",
        "tipo": tipo,
        "esc": cfg["esc"],
        "daño": cfg["daño"],
        "pts": cfg["pts"],
        "pesos_r": cfg["pesos"],
        "alc_m": cfg["alc_m"],
        "esp_ms": cfg["esp"],
        "rect": r,
        "hitbox": creahit(sprs["abajo"][0], r.topleft),
        "sprs": sprs,
        "sprrojos": sprr,
        "sprataq": sprat,
        "sprataqrojos": spratr,
        "vida": hp_m,
        "vida_max": hp_m,
        "golpe_hasta": 0,
        "kx": 0.0,
        "ky": 0.0,
        "dir": "abajo",
        "frame": random.random() * 3,
        "ataq": False,
        "golpe_hecho": False,
        "fraataq": 0,
        "ultfra": 0,
        "ultmov": 0,
        "proximoataq": pygame.time.get_ticks() + random.randint(250, 700),
        "vel": max(1, round(vbase)),
        "ang_at": angbase,
        "rad_m": random.uniform(0.9, 1.35)
    }

def crearene(anc, alt, cant=1, ole=1, alt_p=None, jdat=None):
    if alt_p is None:
        alt_p = int(alt / 2.4)

    infole = colaoleada(ole)
    enes = []
    ini = min(len(infole["cola"]), max(4, min(infole["max_sim"] // 2, 8)))
    for i in range(ini):
        t = infole["cola"].pop(0)
        e = instene(t, ole, anc, alt, alt_p, enes, jdat=jdat, idx=i, tot_esp=infole["tot"])
        enes.append(e)

    if jdat is not None:
        jdat["ole_inf"] = infole
        jdat["drops"] = []
        jdat["textos"] = []
        jdat["chispas"] = []
        sub = "¡Cuidado, viene EL JEFE!" if infole["jefe"] else f"{infole['tot']} enemigos en camino"
        setbanner(jdat, f"OLEADA {ole}", sub, dur_ms=2500)

    return enes

def danarene(ene, cant, emp_x=0.0, emp_y=0.0, jdat=None):
    ahora = pygame.time.get_ticks()
    d_real = cant if ene.get("vida_max", 3) > 5 else max(1, round(cant / 14))
    res = 0.3 if ene.get("tipo") == "jefe" else 1.0
    esc = ene.get("esc", 1.0)

    ene["vida"] = max(0, ene["vida"] - d_real)
    ene["golpe_hasta"] = ahora + 160
    ene["kx"] = ene.get("kx", 0.0) + (emp_x * res / esc)
    ene["ky"] = ene.get("ky", 0.0) + (emp_y * res / esc)

    addtxtflot(jdat, str(int(d_real)), ene["rect"].centerx, ene["rect"].top - 6, (255, 255, 255))
    addchispas(jdat, ene["hitbox"].centerx, ene["hitbox"].centery, (255, 215, 60), cant=5, fuerza=4.2)

def crearproy(jdat):
    r = jdat["hitbox"]
    da = jdat["dirataq"]
    wz = max(24, int(r.width * 1.65))
    hz = max(24, int(r.height * 1.15))
    proy = pygame.Rect(0, 0, wz, hz)
    v = max(7, int(r.height * 0.20))
    alc = max(wz // 2, int(r.height * 0.70))
    dx, dy = 0, 0

    if da == "arriba":
        proy.midbottom = (r.centerx, r.centery)
        dy = -v
    elif da == "abajo":
        proy.midtop = (r.centerx, r.centery)
        dy = v
    elif da == "izquierda":
        proy.midright = (r.centerx, r.centery)
        dx = -v
    else:
        proy.midleft = (r.centerx, r.centery)
        dx = v

    return {
        "rect": proy,
        "dx": dx,
        "dy": dy,
        "alcance": alc,
        "recorrido": 0,
        "tocados": set(),
        "lado": "puno",
        "invisible": True
    }

def proypist(jdat, dest):
    ahora = pygame.time.get_ticks()
    if ahora < jdat.get("cd_disp_hasta", 0):
        return None
    orig = (jdat["hitbox"].centerx, jdat["hitbox"].centery - int(jdat["hitbox"].height * 0.12))
    dx = dest[0] - orig[0]
    dy = dest[1] - orig[1]
    dist = math.hypot(dx, dy)
    if dist == 0:
        return None
    ux, uy = dx / dist, dy / dist
    if abs(ux) >= abs(uy):
        jdat["dir"] = "derecha" if ux > 0 else "izquierda"
    else:
        jdat["dir"] = "abajo" if uy > 0 else "arriba"
    if ux != 0:
        jdat["lado_x"] = 1 if ux > 0 else -1

    jdat["cd_disp_hasta"] = ahora + 220
    tam = max(8, int(jdat["hitbox"].height * 0.14))
    proy = pygame.Rect(0, 0, tam, tam)
    proy.center = (int(orig[0] + ux * 16), int(orig[1] + uy * 16))
    vbala = max(20, int(jdat["hitbox"].height * 0.42))
    ang = math.degrees(math.atan2(-uy, ux))
    addchispas(jdat, proy.centerx, proy.centery, (255, 215, 60), cant=3, fuerza=3.2)

    return {
        "rect": proy,
        "dx": ux * vbala,
        "dy": uy * vbala,
        "alcance": max(dist, jdat["hitbox"].height * 9.5),
        "recorrido": 0,
        "destino": dest,
        "angulo": ang,
        "lado": "pistola"
    }

def proyene(ene, jdat):
    dx = jdat["hitbox"].centerx - ene["hitbox"].centerx
    dy = jdat["hitbox"].centery - ene["hitbox"].centery
    d = "derecha" if dx >= 0 else "izquierda"
    if abs(dy) > abs(dx):
        d = "abajo" if dy >= 0 else "arriba"
    ene["dir"] = d
    ene["ataq"] = True
    ene["golpe_hecho"] = False
    ene["fraataq"] = 0
    ene["ultfra"] = pygame.time.get_ticks()
    ene["proximoataq"] = pygame.time.get_ticks() + ene.get("esp_ms", 850)

    h = ene["hitbox"]
    tam = max(8, int(h.height * 0.16))
    v = max(6, int(h.height * 0.18))
    proy = pygame.Rect(0, 0, tam, tam)
    if d == "arriba":
        proy.center = (h.centerx, h.top)
        mx, my = 0, -v
    elif d == "abajo":
        proy.center = (h.centerx, h.bottom)
        mx, my = 0, v
    elif d == "izquierda":
        proy.center = (h.left, h.centery)
        mx, my = -v, 0
    else:
        proy.center = (h.right, h.centery)
        mx, my = v, 0
    return {
        "rect": proy,
        "dx": mx,
        "dy": my,
        "alcance": max(tam, int(h.height * 0.85)),
        "recorrido": 0,
        "lado": "enemigo",
        "daño": ene.get("daño", 0.5),
        "orig": ene
    }

def gendrops(jdat, ene):
    if jdat is None:
        return
    ahora = pygame.time.get_ticks()
    drops = jdat.setdefault("drops", [])
    ex, ey = ene["rect"].centerx, ene["rect"].bottom
    rpesos = ene.get("pesos_r", (15, 30))

    if ene.get("tipo") == "jefe":
        tot = random.randint(*rpesos)
        for _ in range(6):
            drops.append({
                "tipo": "peso",
                "x": ex + random.uniform(-35, 35),
                "y": ey + random.uniform(-18, 18),
                "val": max(5, tot // 6),
                "inicio": ahora,
                "vida_ms": 16000,
                "iman": False
            })
        drops.append({
            "tipo": "pancho",
            "x": ex,
            "y": ey,
            "val": 1,
            "inicio": ahora,
            "vida_ms": 16000,
            "iman": False
        })
        return

    if random.random() < 0.85:
        drops.append({
            "tipo": "peso",
            "x": ex + random.uniform(-12, 12),
            "y": ey + random.uniform(-6, 6),
            "val": random.randint(*rpesos),
            "inicio": ahora,
            "vida_ms": 14000,
            "iman": False
        })
    if random.random() < 0.12:
        drops.append({
            "tipo": "pancho",
            "x": ex + random.uniform(-10, 10),
            "y": ey + random.uniform(-6, 6),
            "val": 1,
            "inicio": ahora,
            "vida_ms": 14000,
            "iman": False
        })
    if jdat.get("pistola") and random.random() < 0.18:
        drops.append({
            "tipo": "balas",
            "x": ex + random.uniform(-10, 10),
            "y": ey + random.uniform(-6, 6),
            "val": 3,
            "inicio": ahora,
            "vida_ms": 14000,
            "iman": False
        })

def actefectos(jdat):
    if jdat is None:
        return
    ahora = pygame.time.get_ticks()
    jx, jy = jdat["rect"].centerx, jdat["rect"].centery

    ndrops = []
    for d in jdat.get("drops", []):
        if ahora - d["inicio"] >= d["vida_ms"]:
            continue
        dx = jx - d["x"]
        dy = jy - d["y"]
        dist = math.hypot(dx, dy)
        rad_im = max(90, int(jdat["rect"].height * 1.45))
        if d.get("iman") or dist < rad_im:
            v_im = 11.0 if d.get("iman") else 5.5
            if dist > 0:
                d["x"] += (dx / dist) * v_im
                d["y"] += (dy / dist) * v_im
        if dist < max(26, int(jdat["rect"].width * 0.75)):
            if d["tipo"] == "peso":
                jdat["pesos"] = jdat.get("pesos", 0) + d["val"]
                addtxtflot(jdat, f"+${d['val']}", jx, jdat["rect"].top - 12, (255, 215, 60))
            elif d["tipo"] == "pancho":
                if jdat["vida"] < 5:
                    jdat["vida"] = min(5, jdat["vida"] + 1)
                    jdat["daño_acum"] = 0.0
                    addtxtflot(jdat, "+1 VIDA", jx, jdat["rect"].top - 12, (90, 220, 110))
                else:
                    jdat["panchos_extra"] = jdat.get("panchos_extra", 0) + 1
                    addtxtflot(jdat, "+1 PANCHO", jx, jdat["rect"].top - 12, (90, 220, 110))
            elif d["tipo"] == "balas":
                jdat["balas_extra"] = jdat.get("balas_extra", 0) + d["val"]
                addtxtflot(jdat, f"+{d['val']} BALAS", jx, jdat["rect"].top - 12, (120, 200, 255))
            continue
        ndrops.append(d)
    jdat["drops"] = ndrops

    nchisp = []
    for c in jdat.get("chispas", []):
        if ahora - c["inicio"] >= c["vida"]:
            continue
        c["x"] += c["vx"]
        c["y"] += c["vy"]
        c["vy"] += 0.22
        nchisp.append(c)
    jdat["chispas"] = nchisp

    ntxt = []
    for t in jdat.get("textos", []):
        if ahora - t["inicio"] >= t["dur"]:
            continue
        t["y"] -= 0.75
        ntxt.append(t)
    jdat["textos"] = ntxt

    banner = jdat.get("banner")
    if banner and ahora - banner["inicio"] >= banner["dur"]:
        jdat["banner"] = None

def actualizaene(enes, jdat, proys, obs_l=None, anc=None, alt=None):
    ahora = pygame.time.get_ticks()
    actefectos(jdat)

    infole = jdat.get("ole_inf") if jdat else None
    vivos = [e for e in enes if e["vida"] > 0]
    if infole and infole["cola"]:
        if len(vivos) < infole["max_sim"] and (ahora - infole["ultspawn"] >= infole["interv_ms"] or len(vivos) == 0):
            infole["ultspawn"] = ahora
            t_nuevo = infole["cola"].pop(0)
            wm = anc or 2400
            hm = alt or 1400
            hp = int(hm / 2.4)
            idx_sp = infole["tot"] - len(infole["cola"])
            nene = instene(t_nuevo, infole["num"], wm, hm, hp, enes, jdat=jdat, idx=idx_sp, tot_esp=infole["tot"])
            enes.append(nene)
            vivos.append(nene)
            if t_nuevo == "jefe":
                setbanner(jdat, "¡LLEGÓ EL JEFE!", "Derrotalo para despejar la zona", dur_ms=2400)

    tot_v = len(vivos)
    if tot_v == 0:
        if infole and not infole["cola"] and not infole.get("fin"):
            infole["fin"] = True
            n = infole["num"]
            bon = 25 * n
            jdat["pesos"] = jdat.get("pesos", 0) + bon
            jdat["puntos"] = jdat.get("puntos", 0) + 50 * n
            for d in jdat.get("drops", []):
                d["iman"] = True
            setbanner(jdat, f"¡OLEADA {n} COMPLETADA!", f"+${bon} de bonus - Avanza a la derecha ->", dur_ms=3500)
        return

    jcent = jdat["hitbox"].center
    alc_base = jdat["hitbox"].height * 1.25

    for idx, ene in enumerate(vivos):
        if "ang_at" not in ene:
            ene["ang_at"] = (idx / max(1, tot_v)) * 2 * math.pi
            ene["rad_m"] = random.uniform(0.9, 1.35)

        kx = ene.get("kx", 0.0)
        ky = ene.get("ky", 0.0)
        if abs(kx) > 0.4 or abs(ky) > 0.4:
            rx = round(kx)
            ry = round(ky)
            if rx != 0:
                ene["rect"].x += rx
                if obs_l and any(colpies(ene["rect"]).colliderect(o) for o in obs_l):
                    ene["rect"].x -= rx
            if ry != 0:
                ene["rect"].y += ry
                if obs_l and any(colpies(ene["rect"]).colliderect(o) for o in obs_l):
                    ene["rect"].y -= ry
            ene["kx"] = kx * 0.78
            ene["ky"] = ky * 0.78

        dx_j = jcent[0] - ene["hitbox"].centerx
        dy_j = jcent[1] - ene["hitbox"].centery
        dist_j = math.hypot(dx_j, dy_j)
        alc_e = alc_base * ene.get("alc_m", 1.15)

        if ene["ataq"]:
            if ahora - ene["ultfra"] >= 110:
                ene["fraataq"] += 1
                ene["ultfra"] = ahora
                if ene["fraataq"] == 1 and not ene.get("golpe_hecho", False):
                    ene["golpe_hecho"] = True
                    if dist_j <= alc_e * 1.25 and ahora - jdat.get("ultdaño", -1000) >= 900:
                        dañojug(jdat, ahora, cant=ene.get("daño", 0.5), orig=ene, anc_m=anc, alt_m=alt, obs_l=obs_l)
                if ene["fraataq"] >= 3:
                    ene["ataq"] = False
                    ene["fraataq"] = 0
        elif dist_j <= alc_e and ahora >= ene["proximoataq"]:
            proys.append(proyene(ene, jdat))
        else:
            rad_fl = alc_e * ene.get("rad_m", 1.1)
            tx = jcent[0] + math.cos(ene["ang_at"]) * rad_fl
            ty = jcent[1] + math.sin(ene["ang_at"]) * rad_fl

            vx = tx - ene["rect"].centerx
            vy = ty - ene["rect"].centery
            dtarg = math.hypot(vx, vy)

            dirx = (vx / dtarg) if dtarg > 4 else 0.0
            diry = (vy / dtarg) if dtarg > 4 else 0.0

            rsep = max(ene["rect"].width, ene["rect"].height) * 1.35
            sepx = 0.0
            sepy = 0.0

            for otro in vivos:
                if otro is ene:
                    continue
                ox = ene["rect"].centerx - otro["rect"].centerx
                oy = ene["rect"].centery - otro["rect"].centery
                dsq = ox * ox + oy * oy
                if 0 < dsq < (rsep * rsep):
                    d = math.sqrt(dsq)
                    f = (rsep - d) / rsep
                    sepx += (ox / d) * f
                    sepy += (oy / d) * f
                elif dsq == 0:
                    rang = random.uniform(0, 2 * math.pi)
                    sepx += math.cos(rang)
                    sepy += math.sin(rang)

            totx = dirx + sepx * 1.8
            toty = diry + sepy * 1.8
            mag = math.hypot(totx, toty)

            if mag > 0.08:
                vel = ene["vel"]
                paso = min(float(vel), max(1.0, dtarg))
                movx = round((totx / mag) * paso)
                movy = round((toty / mag) * paso)

                if abs(movx) > abs(movy):
                    ene["dir"] = "derecha" if movx > 0 else "izquierda"
                elif abs(movy) > 0:
                    ene["dir"] = "abajo" if movy > 0 else "arriba"
                else:
                    ene["dir"] = ("derecha" if dx_j > 0 else "izquierda") if abs(dx_j) >= abs(dy_j) else ("abajo" if dy_j > 0 else "arriba")

                if obs_l:
                    if movx != 0:
                        ene["rect"].x += movx
                        if any(colpies(ene["rect"]).colliderect(o) for o in obs_l):
                            ene["rect"].x -= movx
                    if movy != 0:
                        ene["rect"].y += movy
                        if any(colpies(ene["rect"]).colliderect(o) for o in obs_l):
                            ene["rect"].y -= movy
                else:
                    ene["rect"].move_ip(movx, movy)

                for otro in vivos:
                    if otro is ene:
                        continue
                    if ene["rect"].colliderect(otro["rect"]):
                        pdx = ene["rect"].centerx - otro["rect"].centerx
                        pdy = ene["rect"].centery - otro["rect"].centery
                        if pdx == 0 and pdy == 0:
                            pdx = random.choice([-1, 1])
                        px = 1 if pdx > 0 else -1
                        ene["rect"].x += px
                        if obs_l and any(colpies(ene["rect"]).colliderect(o) for o in obs_l):
                            ene["rect"].x -= px
                        py_ = 1 if pdy > 0 else -1
                        ene["rect"].y += py_
                        if obs_l and any(colpies(ene["rect"]).colliderect(o) for o in obs_l):
                            ene["rect"].y -= py_

                if ahora - ene["ultmov"] >= 140 and (movx != 0 or movy != 0):
                    ene["frame"] = (ene["frame"] + 1) % 3
                    ene["ultmov"] = ahora
            else:
                ene["dir"] = ("derecha" if dx_j > 0 else "izquierda") if abs(dx_j) >= abs(dy_j) else ("abajo" if dy_j > 0 else "arriba")

        spr = ene["sprataq"][ene["dir"]][ene["fraataq"]] if ene["ataq"] else ene["sprs"][ene["dir"]][int(ene["frame"])]
        ene["hitbox"] = creahit(spr, ene["rect"].topleft)

def moverproy(proys, enes, anc, alt, jdat=None):
    ahora = pygame.time.get_ticks()
    for ene in enes[:]:
        if ene["vida"] <= 0 and ahora >= ene["golpe_hasta"]:
            enes.remove(ene)
            if jdat is not None:
                oact = jdat.get("ole_inf", {}).get("num", 1)
                pts = round(ene.get("pts", 10) * (1 + 0.1 * (oact - 1)))
                jdat["puntos"] = jdat.get("puntos", 0) + pts
                gendrops(jdat, ene)
                addchispas(jdat, ene["rect"].centerx, ene["rect"].centery, (230, 60, 60), cant=12, fuerza=5.5)

    for p in proys[:]:
        if p.get("lado") == "pistola":
            ant = p["rect"].center
            v = math.hypot(p["dx"], p["dy"])
            rest = max(0, p["alcance"] - p["recorrido"])
            paso = min(v, rest)
            if paso >= rest:
                p["rect"].move_ip(round(p["dx"]), round(p["dy"]))
            else:
                p["rect"].move_ip(round(p["dx"] / v * paso), round(p["dy"] / v * paso))
            mx = p["rect"].centerx - ant[0]
            my = p["rect"].centery - ant[1]
            p["recorrido"] = min(p["alcance"], p["recorrido"] + math.hypot(mx, my))
            act = p["rect"].center
            ux = p["dx"] / v if v > 0 else 0
            uy = p["dy"] / v if v > 0 else 0
            for ene in enes:
                if ene["vida"] > 0 and (ene["hitbox"].clipline(ant, act) or ene["hitbox"].colliderect(p["rect"])):
                    danarene(ene, daño_BALA, emp_x=ux * 11.0, emp_y=uy * 11.0, jdat=jdat)
                    proys.remove(p)
                    break
            if p not in proys:
                continue
            if p["recorrido"] >= p["alcance"] or not pygame.Rect(-40, -40, anc + 80, alt + 80).colliderect(p["rect"]):
                proys.remove(p)
            continue

        paso = min(abs(p["dx"] or p["dy"]), p["alcance"] - p["recorrido"])
        mx = paso if p["dx"] > 0 else -paso if p["dx"] < 0 else 0
        my = paso if p["dy"] > 0 else -paso if p["dy"] < 0 else 0
        p["rect"].move_ip(mx, my)
        p["recorrido"] += paso
        if p.get("lado") == "enemigo":
            if jdat is not None and p["rect"].colliderect(jdat["hitbox"]):
                if ahora - jdat.get("ultdaño", -1000) >= 900:
                    dañojug(jdat, ahora, cant=p.get("daño", 0.5), orig=p.get("orig"), anc_m=anc, alt_m=alt)
                proys.remove(p)
                continue
        else:
            vx = 1 if p["dx"] > 0 else (-1 if p["dx"] < 0 else 0)
            vy = 1 if p["dy"] > 0 else (-1 if p["dy"] < 0 else 0)
            for ene in enes:
                if ene["vida"] <= 0:
                    continue
                iene = id(ene)
                if iene not in p["tocados"] and p["rect"].colliderect(ene["hitbox"]):
                    p["tocados"].add(iene)
                    danarene(ene, daño_PUNO, emp_x=vx * 14.0, emp_y=vy * 14.0, jdat=jdat)
        if p["recorrido"] >= p["alcance"] or not pygame.Rect(0, 0, anc, alt).colliderect(p["rect"]):
            proys.remove(p)

def bderrota(anc, alt):
    ruta = "F/minecraft.ttf" if os.path.exists("F/minecraft.ttf") else "minecraft.ttf"
    ftit = pygame.font.Font(ruta, int(alt * 0.065))
    fbtn = pygame.font.Font(ruta, int(alt * 0.038))
    wpan = int(anc * 0.32)
    wbtn = int(wpan * 0.78 * 1.5)
    hbtn = int(alt * 0.08 * 1.5)
    xb = (anc - wbtn) // 2
    return ftit, fbtn, [
        {"texto": "VOLVER A JUGAR", "rect": pygame.Rect(xb, int(alt * 0.52), wbtn, hbtn), "accion": "jugar"},
        {"texto": "MENU", "rect": pygame.Rect(xb, int(alt * 0.68), wbtn, hbtn), "accion": "menu"}
    ]

def dibujarperdida(pant, jdat, mgraf, ftit, fbtn, btns, mouse, cam=(0, 0)):
    dibujarjuego(pant, mgraf, jdat, [], [], False, cam=cam)

    capa = pygame.Surface(pant.get_size(), pygame.SRCALPHA)
    capa.fill((180, 0, 0, 77))
    pant.blit(capa, (0, 0))

    t1 = grosor(ftit, "PERDISTE,", (255, 255, 255), 2)
    t2 = grosor(ftit, "ALTO BOT", (255, 255, 255), 2)
    pant.blit(t1, t1.get_rect(center=(pant.get_width() // 2, int(pant.get_height() * 0.20))))
    pant.blit(t2, t2.get_rect(center=(pant.get_width() // 2, int(pant.get_height() * 0.32))))

    for b in btns:
        act = b["rect"].collidepoint(mouse)
        pygame.draw.rect(pant, (95, 95, 95) if act else (75, 75, 75), b["rect"], border_radius=6)
        pygame.draw.rect(pant, (130, 130, 130) if act else (45, 45, 45), b["rect"], width=3, border_radius=6)
        txt = fbtn.render(b["texto"], True, (255, 255, 255))
        pant.blit(txt, txt.get_rect(center=b["rect"].center))

def capas(anc, alt, wpan):
    pizq = pygame.Surface((wpan, alt))
    pizq.fill((0, 0, 0))
    pizq.set_alpha(170)

    pder = pygame.Surface((anc - wpan, alt))
    pder.fill((0, 0, 0))
    pder.set_alpha(128)
    return pizq, pder

def fuentes(alt):
    ruta = "F/minecraft.ttf" if os.path.exists("F/minecraft.ttf") else "minecraft.ttf"
    return pygame.font.Font(ruta, int(alt * 0.065)), pygame.font.Font(ruta, int(alt * 0.038))

def grosor(fuente, txt, col, g=2):
    surf = fuente.render(txt, True, col)
    wt, ht = surf.get_size()
    surfg = pygame.Surface((wt + g * 2, ht + g * 2), pygame.SRCALPHA)
    for dx in range(-g, g + 1):
        for dy in range(-g, g + 1):
            surfg.blit(surf, (dx + g, dy + g))
    return surfg

def titulos(ftit, wpan, alt):
    t1 = grosor(ftit, "La Matanza,", (255, 255, 255), 2)
    t2 = grosor(ftit, "Avanza", (255, 255, 255), 2)
    return t1, t2, t1.get_rect(center=(wpan // 2, int(alt * 0.12))), t2.get_rect(center=(wpan // 2, int(alt * 0.20)))

def btnlista(wpan, alt):
    wbtn = int(wpan * 0.78)
    hbtn = int(alt * 0.08)
    posx = (wpan - wbtn) // 2
    posy = int(alt * 0.36)
    esp = int(alt * 0.12)
    return [
        {"texto": "JUGAR", "rect": pygame.Rect(posx, posy, wbtn, hbtn), "accion": "jugar"},
        {"texto": "VENTANA", "rect": pygame.Rect(posx, posy + esp, wbtn, hbtn), "accion": "ventana"},
        {"texto": "REINICIAR", "rect": pygame.Rect(posx, posy + esp * 2, wbtn, hbtn), "accion": "reiniciar"},
        {"texto": "SALIR", "rect": pygame.Rect(posx, posy + esp * 3, wbtn, hbtn), "accion": "salir"}
    ]

def modopant(anc, alt, vent):
    if vent.get_flags() & pygame.FULLSCREEN:
        return pygame.display.set_mode((int(anc * 0.8), int(alt * 0.8)), pygame.RESIZABLE)
    return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

def framevideo(vid, anc, alt):
    ok, frame = vid.read()
    if not ok:
        vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ok, frame = vid.read()
    if ok:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (anc, alt))
        return pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    return None

def dibujar(pant, fsurf, pizq, pder, wpan, t1, t2, r1, r2, btns, fbtn, mouse):
    if fsurf:
        pant.blit(fsurf, (0, 0))
    pant.blit(pizq, (0, 0))
    pant.blit(pder, (wpan, 0))
    pant.blit(t1, r1)
    pant.blit(t2, r2)
    for b in btns:
        act = b["rect"].collidepoint(mouse)
        pygame.draw.rect(pant, (95, 95, 95) if act else (75, 75, 75), b["rect"], border_radius=6)
        pygame.draw.rect(pant, (130, 130, 130) if act else (45, 45, 45), b["rect"], width=3, border_radius=6)
        tsurf = fbtn.render(b["texto"], True, (255, 255, 255))
        pant.blit(tsurf, tsurf.get_rect(center=b["rect"].center))

def cargarmapa(anc, alt):
    ruta = "Sprites/mapa1n.jpeg" if os.path.exists("Sprites/mapa1n.jpeg") else ("F/Mapa.png" if os.path.exists("F/Mapa.png") else "Mapa.png")
    return pygame.transform.scale(pygame.image.load(ruta), (anc, alt)).convert()

def cargabazar(anc, alt):
    imgs = []
    for nom in ("andy00", "andy01", "andy02", "andy03"):
        ruta = f"Sprites/Andy/{nom}.png" if os.path.exists(f"Sprites/Andy/{nom}.png") else f"{nom}.png"
        imgs.append(pygame.transform.scale(pygame.image.load(ruta).convert(), (anc, alt)))
    return imgs

def cargarmira(alt):
    img = pygame.image.load("Sprites/Botones/mira.png").convert_alpha()
    for y in range(img.get_height()):
        for x in range(img.get_width()):
            px = img.get_at((x, y))
            if px.a:
                img.set_at((x, y), (255, 255, 255, px.a))
    tam = max(32, int(alt * 0.055))
    return pygame.transform.scale(img, (tam, tam))

def cargariconos(alt):
    icons = {}
    tam = max(28, int(alt * 0.045))
    for nom in ("pancho", "peso"):
        img = pygame.image.load(f"Sprites/Botones/{nom}.png").convert_alpha()
        esc = tam / img.get_height()
        icons[nom] = pygame.transform.smoothscale(img, (int(img.get_width() * esc), tam))

    ruta_spd = "Sprites/speed.png" if os.path.exists("Sprites/speed.png") else "speed.png"
    img_spd = _recortafondo(ruta_spd)
    esc_spd = tam / img_spd.get_height()
    icons["speed"] = pygame.transform.smoothscale(img_spd, (max(12, int(img_spd.get_width() * esc_spd)), tam))
    icons["speed_full"] = img_spd
    return icons

def dibujarrecursos(pant, icons, pesos, panchos, balas=None, bmax=0, spds=0):
    alt = pant.get_height()
    tamf = max(24, int(alt * 0.035))
    if tamf not in _fnt_rec:
        _fnt_rec[tamf] = pygame.font.Font(None, tamf)
    f = _fnt_rec[tamf]

    tspd = f.render(str(spds), True, (255, 255, 255))
    tpan = f.render(str(panchos), True, (255, 255, 255))
    tpes = f.render(str(pesos), True, (255, 255, 255))
    tbal = f.render(f"Balas: {balas}/{bmax}" if balas is not None else "Balas: --", True, (255, 255, 255))
    marg = max(12, int(alt * 0.02))
    esp = max(6, int(alt * 0.01))
    der = pant.get_width() - marg

    rtspd = tspd.get_rect(midright=(der, marg + icons["pancho"].get_height() // 2))
    rspd = icons["speed"].get_rect(midright=(rtspd.left - esp, rtspd.centery))
    rtpan = tpan.get_rect(midright=(rspd.left - esp * 2, rspd.centery))
    rpan = icons["pancho"].get_rect(midright=(rtpan.left - esp, rtpan.centery))
    rtpes = tpes.get_rect(midright=(rpan.left - esp * 2, rpan.centery))
    rpes = icons["peso"].get_rect(midright=(rtpes.left - esp, rtpes.centery))
    rbal = tbal.get_rect(midright=(rpes.left - esp * 2, rpes.centery))
    fondo = pygame.Rect(rbal.left - esp, marg // 2, der - rbal.left + esp * 2, icons["pancho"].get_height() + marg)

    pygame.draw.rect(pant, (0, 0, 0, 170), fondo, border_radius=5)
    pant.blit(tbal, rbal)
    pant.blit(icons["peso"], rpes)
    pant.blit(tpes, rtpes)
    pant.blit(icons["pancho"], rpan)
    pant.blit(tpan, rtpan)
    pant.blit(icons["speed"], rspd)
    pant.blit(tspd, rtspd)
    return rpan.union(rtpan).inflate(6, 6), rspd.union(rtspd).inflate(6, 6)

def dibujaroleada(pant, ole, enes=None, jdat=None):
    alt = pant.get_height()
    anc = pant.get_width()
    tamf = max(28, int(alt * 0.045))
    tamch = max(20, int(alt * 0.028))
    if tamf not in _fnt_rec:
        _fnt_rec[tamf] = pygame.font.Font(None, tamf)
    if tamch not in _fnt_rec:
        _fnt_rec[tamch] = pygame.font.Font(None, tamch)
    f = _fnt_rec[tamf]
    fch = _fnt_rec[tamch]

    marg = max(12, int(alt * 0.02))
    inf = jdat.get("ole_inf") if jdat else None
    cola_len = len(inf["cola"]) if inf else 0
    vivos = len([e for e in (enes or []) if e.get("vida", 0) > 0])
    pts = jdat.get("puntos", 0) if jdat else 0

    txt = f.render(f"Oleada {ole}", True, (255, 255, 255))
    sub_txt = f"Restantes: {cola_len + vivos}  |  Puntos: {pts}" if enes is not None else f"Puntos: {pts}"
    sub = fch.render(sub_txt, True, (215, 215, 215))

    rt = txt.get_rect(topleft=(marg * 2, marg))
    rs = sub.get_rect(topleft=(marg * 2, rt.bottom + 2))
    fondo = rt.union(rs).inflate(marg * 2, marg)
    pygame.draw.rect(pant, (0, 0, 0, 175), fondo, border_radius=6)
    pant.blit(txt, rt)
    pant.blit(sub, rs)

    banner = jdat.get("banner") if jdat else None
    if banner:
        ahora = pygame.time.get_ticks()
        trans = ahora - banner["inicio"]
        dur = max(1, banner["dur"])
        if 0 <= trans < dur:
            tb = max(48, int(alt * 0.085))
            if tb not in _fnt_rec:
                _fnt_rec[tb] = pygame.font.Font(None, tb)
            fban = _fnt_rec[tb]
            alfa = int(255 * max(0.0, min(1.0, trans / 280.0, (dur - trans) / 450.0)))
            imgb = fban.render(banner["texto"], True, (255, 215, 60))
            somb = fban.render(banner["texto"], True, (0, 0, 0))
            imgb.set_alpha(alfa)
            somb.set_alpha(alfa)
            rb = imgb.get_rect(center=(anc // 2, int(alt * 0.24)))
            pant.blit(somb, rb.move(3, 3))
            pant.blit(imgb, rb)
            if banner.get("sub"):
                isub = f.render(banner["sub"], True, (255, 255, 255))
                ssub = f.render(banner["sub"], True, (0, 0, 0))
                isub.set_alpha(alfa)
                ssub.set_alpha(alfa)
                rsb = isub.get_rect(center=(anc // 2, int(alt * 0.31)))
                pant.blit(ssub, rsb.move(2, 2))
                pant.blit(isub, rsb)

def cargarsprs(wj, hj):
    dic = {
        "abajo": [0, 1, 2],
        "arriba": [4, 5, 6],
        "derecha": [12, 13, 14],
        "izquierda": [8, 9, 10]
    }
    sprs = {}
    for d, nums in dic.items():
        sprs[d] = [pygame.transform.scale(pygame.image.load(f"sprites/Mc/MC{n:03d}.png").convert_alpha(), (wj, hj)) for n in nums]
    return sprs

def cargarsprat(wj, hj):
    dic = {
        "abajo": [0, 1, 2, 3],
        "arriba": [4, 5, 6, 7],
        "izquierda": [8, 9, 10, 11],
        "derecha": [12, 13, 14, 15]
    }
    sprs = {}
    for d, nums in dic.items():
        sprs[d] = [pygame.transform.scale(pygame.image.load(f"Sprites/Mc/Ataque_Mc/AMC{n:03d}.png").convert_alpha(), (wj, hj)) for n in nums]
    return sprs

def cargarsprdash(hj):
    der = []
    izq = []
    for i in range(8):
        img = pygame.image.load(f"Sprites/Mc/Dash_Normal/dash_{i:02d}.png").convert_alpha()
        rec = img.subsurface(img.get_bounding_rect()).copy()
        esc = hj / max(1, rec.get_height())
        wd = max(12, int(rec.get_width() * esc))
        sprd = pygame.transform.scale(rec, (wd, hj))
        der.append(sprd)
        izq.append(pygame.transform.flip(sprd, True, False))
    return {"derecha": der, "izquierda": izq}

def inidash(jdat, teclas=None):
    ahora = pygame.time.get_ticks()
    if jdat.get("dash") or ahora < jdat.get("dash_cd_hasta", 0):
        return False

    dx, dy = 0, 0
    if teclas is not None:
        dx = int(teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_a] or teclas[pygame.K_LEFT])
        dy = int(teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - int(teclas[pygame.K_w] or teclas[pygame.K_UP])

    if dx == 0 and dy == 0:
        d = jdat.get("dir", "abajo")
        dx = 1 if d == "derecha" else (-1 if d == "izquierda" else 0)
        dy = -1 if d == "arriba" else (1 if d == "abajo" else 0)

    mag = math.hypot(dx, dy)
    ux, uy = (dx / mag, dy / mag) if mag > 0 else (1.0, 0.0)
    if ux != 0:
        jdat["lado_x"] = 1 if ux > 0 else -1

    dur_ms = 230
    cd_ms = 950
    jdat["ataq"] = False
    jdat["dash"] = True
    jdat["dash_ini"] = ahora
    jdat["dash_hasta"] = ahora + dur_ms
    jdat["dash_dur"] = dur_ms
    jdat["dash_cd_hasta"] = ahora + cd_ms
    jdat["dash_cd_dur"] = cd_ms
    jdat["dash_invul_hasta"] = ahora + dur_ms + 80
    jdat["dash_vec"] = (ux, uy)
    return True

def iniataq(jdat, dest=None, enes=None):
    ahora = pygame.time.get_ticks()
    if jdat.get("dash") or jdat["ataq"] or ahora < jdat.get("cd_golpe_hasta", 0):
        return False

    cercano = None
    mdist = jdat["rect"].height * 2.1
    if enes:
        jx, jy = jdat["hitbox"].center
        for e in enes:
            if e.get("vida", 0) <= 0:
                continue
            d = math.hypot(e["hitbox"].centerx - jx, e["hitbox"].centery - jy)
            if d < mdist:
                mdist = d
                cercano = e

    if cercano is not None:
        dx = cercano["hitbox"].centerx - jdat["hitbox"].centerx
        dy = cercano["hitbox"].centery - jdat["hitbox"].centery
        jdat["dir"] = ("derecha" if dx > 0 else "izquierda") if abs(dx) >= abs(dy) else ("abajo" if dy > 0 else "arriba")
        if dx != 0:
            jdat["lado_x"] = 1 if dx > 0 else -1
    elif dest is not None:
        dx = dest[0] - jdat["hitbox"].centerx
        dy = dest[1] - jdat["hitbox"].centery
        if dx != 0 or dy != 0:
            jdat["dir"] = ("derecha" if dx > 0 else "izquierda") if abs(dx) >= abs(dy) else ("abajo" if dy > 0 else "arriba")
            if dx != 0:
                jdat["lado_x"] = 1 if dx > 0 else -1

    jdat["ataq"] = True
    jdat["dirataq"] = jdat["dir"]
    jdat["fraataq"] = 0
    jdat["ultfraataq"] = ahora
    return True

def actataq(jdat):
    ahora = pygame.time.get_ticks()
    if jdat.get("dash") and ahora >= jdat.get("dash_hasta", 0):
        jdat["dash"] = False

    if not jdat["ataq"]:
        return

    if ahora - jdat["ultfraataq"] < 85:
        return

    jdat["fraataq"] += 1
    jdat["ultfraataq"] = ahora
    if jdat["fraataq"] >= len(jdat["sprataq"][jdat["dirataq"]]):
        jdat["ataq"] = False
        jdat["fraataq"] = 0
        jdat["cd_golpe_hasta"] = ahora + 110

def crearjug(anc, alt):
    hj1 = int(alt * 0.1125)
    wj1 = int(hj1 * (52 / 96))
    r1 = pygame.Rect(anc // 2, int(alt * 0.50), wj1, hj1)
    v1 = int(alt * 0.0085)

    sprs1 = cargarsprs(wj1, hj1)
    sprat1 = cargarsprat(wj1, hj1)
    sprd1 = cargarsprdash(hj1)
    sprr1 = {d: [rojospr(s) for s in lst] for d, lst in sprs1.items()}
    spratr1 = {d: [rojospr(s) for s in lst] for d, lst in sprat1.items()}

    hj2 = int(alt * 0.075)
    wj2 = int(hj2 * (52 / 96))
    v2 = max(2, int(alt * 0.007))
    sprs2 = cargarsprs(wj2, hj2)
    sprat2 = cargarsprat(wj2, hj2)
    sprd2 = cargarsprdash(hj2)
    sprr2 = {d: [rojospr(s) for s in lst] for d, lst in sprs2.items()}
    spratr2 = {d: [rojospr(s) for s in lst] for d, lst in sprat2.items()}

    return {
        "rect": r1,
        "hitbox": creahit(sprs1["abajo"][0], r1.topleft),
        "vel": v1,
        "sprs": sprs1,
        "sprrojos": sprr1,
        "sprataq": sprat1,
        "sprataqrojos": spratr1,
        "sprdash": sprd1,
        "_escalas": {
            1: {"w": wj1, "h": hj1, "vel": v1, "sprs": sprs1, "sprrojos": sprr1, "sprataq": sprat1, "sprataqrojos": spratr1, "sprdash": sprd1},
            2: {"w": wj2, "h": hj2, "vel": v2, "sprs": sprs2, "sprrojos": sprr2, "sprataq": sprat2, "sprataqrojos": spratr2, "sprdash": sprd2},
        },
        "mapa_esc": 1,
        "dir": "abajo",
        "lado_x": 1,
        "frame": 1.0,
        "ataq": False,
        "dirataq": "abajo",
        "fraataq": 0,
        "ultfraataq": 0,
        "cd_golpe_hasta": 0,
        "cd_disp_hasta": 0,
        "dash": False,
        "dash_ini": 0,
        "dash_hasta": 0,
        "dash_dur": 230,
        "dash_cd_hasta": 0,
        "dash_cd_dur": 950,
        "dash_invul_hasta": 0,
        "dash_vec": (1.0, 0.0),
        "vida": 5,
        "escudo": 0,
        "daño_acum": 0.0,
        "pesos": 0,
        "pistola": False,
        "panchos_extra": 0,
        "balas_extra": 0,
        "puntos": 0,
        "ultdaño": -1000,
        "golpe_hasta": 0,
        "shake_hasta": 0,
        "drops": [],
        "chispas": [],
        "textos": [],
        "banner": None,
        "ole_inf": None,
    }

def escjug(jdat, anc, alt, mapa=1):
    id_m = 2 if mapa == 2 else 1
    if jdat.get("mapa_esc") == id_m:
        return
    esc = jdat["_escalas"][id_m]
    c = jdat["rect"].center
    jdat["rect"].size = (esc["w"], esc["h"])
    jdat["rect"].center = c
    jdat["vel"] = esc["vel"]
    jdat["sprs"] = esc["sprs"]
    jdat["sprrojos"] = esc["sprrojos"]
    jdat["sprataq"] = esc["sprataq"]
    jdat["sprataqrojos"] = esc["sprataqrojos"]
    jdat["sprdash"] = esc["sprdash"]
    jdat["mapa_esc"] = id_m

    spr = jdat["sprs"][jdat["dir"]][0]
    jdat["hitbox"] = creahit(spr, jdat["rect"].topleft)

def moverjug(jdat, teclas, anc, alt, mapa=1, obs_l=None):
    ahora = pygame.time.get_ticks()
    if isinstance(mapa, (tuple, list)):
        mapa = 2 if (anc > 2000 or alt > 1200 or mapa == (0.29, 0.72)) else 1

    if obs_l is None:
        obs_l = obstaculos(mapa, anc, alt)

    r = jdat["rect"]
    v = jdat["vel"]
    mov = False
    dx, dy = 0, 0

    if jdat.get("dash") and ahora < jdat.get("dash_hasta", 0):
        ux, uy = jdat.get("dash_vec", (1.0, 0.0))
        vdash = max(v * 2.6, 8)
        dx = round(ux * vdash)
        dy = round(uy * vdash)
        mov = True
    else:
        jdat["dash"] = False
        v_act = max(1, int(v * 0.35)) if jdat["ataq"] else v

        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dy -= v_act
            if not jdat["ataq"]:
                jdat["dir"] = "arriba"
            mov = True
        elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dy += v_act
            if not jdat["ataq"]:
                jdat["dir"] = "abajo"
            mov = True

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            dx -= v_act
            if not jdat["ataq"]:
                jdat["dir"] = "izquierda"
            jdat["lado_x"] = -1
            mov = True
        elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            dx += v_act
            if not jdat["ataq"]:
                jdat["dir"] = "derecha"
            jdat["lado_x"] = 1
            mov = True

    if dx != 0:
        px = 1 if dx > 0 else -1
        for _ in range(abs(dx)):
            r.x += px
            if r.left < 0:
                r.left = 0
                break
            if r.right > anc:
                r.right = anc
                break
            if any(colpies(r).colliderect(o) for o in obs_l):
                r.x -= px
                break

    if dy != 0:
        py = 1 if dy > 0 else -1
        for _ in range(abs(dy)):
            r.y += py
            if r.top < 0:
                r.top = 0
                break
            if r.bottom > alt:
                r.bottom = alt
                break
            if any(colpies(r).colliderect(o) for o in obs_l):
                r.y -= py
                break

    if jdat["ataq"]:
        spr = jdat["sprataq"][jdat["dirataq"]][jdat["fraataq"]]
    else:
        idx = [0, 1, 2, 1][int(jdat["frame"]) % 4]
        spr = jdat["sprs"][jdat["dir"]][idx]
    jdat["hitbox"] = creahit(spr, r.topleft)

    if mov and not jdat.get("dash"):
        jdat["frame"] = (jdat["frame"] + 0.15) % 4
    elif not mov:
        jdat["frame"] = 1.0

def dibsombra(pant, x, y, anc):
    anc = max(8, int(anc))
    somb = _SOMBRAS.get(anc)
    if somb is None:
        somb = pygame.Surface((anc, max(5, anc // 3)), pygame.SRCALPHA)
        pygame.draw.ellipse(somb, (0, 0, 0, 90), somb.get_rect())
        _SOMBRAS[anc] = somb
    pant.blit(somb, (int(x - anc / 2), int(y - somb.get_height() / 2)))

def _icondropsbalas(alt_p):
    if alt_p not in _CDROPS:
        tam = max(18, int(alt_p * 0.032))
        dic = {}
        for nom in ("peso", "pancho", "bala"):
            img = pygame.image.load(f"Sprites/Botones/{nom}.png").convert_alpha()
            rec = img.subsurface(img.get_bounding_rect()).copy()
            esc = tam / max(1, rec.get_height())
            dic[nom] = pygame.transform.smoothscale(rec, (max(10, int(rec.get_width() * esc)), tam))
        dic["balas"] = dic["bala"]
        _CDROPS[alt_p] = dic

    if alt_p not in _CBALAS:
        img_b = pygame.image.load("Sprites/Botones/bala.png").convert_alpha()
        rec_b = img_b.subsurface(img_b.get_bounding_rect()).copy()
        tb = max(16, int(alt_p * 0.028))
        esc_b = tb / max(1, max(rec_b.get_width(), rec_b.get_height()))
        base = pygame.transform.smoothscale(rec_b, (max(8, int(rec_b.get_width() * esc_b)), max(8, int(rec_b.get_height() * esc_b))))
        base = pygame.transform.rotate(base, -63)
        _CBALAS[alt_p] = {i: pygame.transform.rotate(base, i * 5) for i in range(72)}

    return _CDROPS[alt_p], _CBALAS[alt_p]

def dibujarjuego(pant, mgraf, jdat, vidas, objs, mvida=True, proys=None, cam=(0, 0), escudos=None):
    ahora = pygame.time.get_ticks()
    alt_p = pant.get_height()
    cx, cy = cam
    if ahora < jdat.get("shake_hasta", 0):
        cx += random.randint(-5, 5)
        cy += random.randint(-5, 5)

    pant.blit(mgraf, (-cx, -cy))
    icondrops, balasrot = _icondropsbalas(alt_p)

    for d in jdat.get("drops", []):
        edad = ahora - d["inicio"]
        rest = d["vida_ms"] - edad
        if rest < 2500 and (ahora // 100) % 2 == 0:
            continue
        ic = icondrops.get(d["tipo"], icondrops["peso"])
        reb = math.sin(edad * 0.006) * 3.5
        dxp = int(d["x"] - cx)
        dyp = int(d["y"] - cy)
        dibsombra(pant, dxp, dyp, ic.get_width() * 0.9)
        pant.blit(ic, ic.get_rect(midbottom=(dxp, int(dyp - 4 + reb))))

    ents = [(jdat["rect"].bottom, "jugador", jdat)]
    for o in objs:
        ents.append((o["rect"].bottom if isinstance(o, dict) else o.bottom, "enemigo" if isinstance(o, dict) else "rect", o))
    ents.sort(key=lambda it: it[0])

    tam_txt = max(18, int(alt_p * 0.025))
    if tam_txt not in _fnt_rec:
        _fnt_rec[tam_txt] = pygame.font.Font(None, tam_txt)
    fent = _fnt_rec[tam_txt]

    for _, tent, o in ents:
        if tent == "rect":
            pygame.draw.rect(pant, (120, 55, 35), o.move(-cx, -cy), border_radius=6)
        elif tent == "enemigo":
            dibsombra(pant, o["rect"].centerx - cx, o["rect"].bottom - cy, o["rect"].width * 0.85)
            if o["ataq"]:
                spr = (o["sprataqrojos"] if ahora < o["golpe_hasta"] else o["sprataq"])[o["dir"]][o["fraataq"]]
            else:
                spr = (o["sprrojos"] if ahora < o["golpe_hasta"] else o["sprs"])[o["dir"]][int(o["frame"]) % 3]
            rx = o["rect"].x - cx
            ry = o["rect"].y - cy
            pant.blit(spr, (rx, ry))

            vmax = o.get("vida_max", 3)
            vact = max(0, o.get("vida", 0))
            es_jefe = o.get("tipo") == "jefe"
            if (vact < vmax or es_jefe) and vact > 0:
                wb = max(28, int(o["rect"].width * 0.95))
                barra = pygame.Rect(int(o["rect"].centerx - cx - wb // 2), int(ry - 9), wb, 5)
                pygame.draw.rect(pant, (40, 0, 0), barra)
                rell = barra.copy()
                rell.width = max(0, int(wb * (vact / max(1, vmax))))
                pygame.draw.rect(pant, (230, 60, 60), rell)
                pygame.draw.rect(pant, (0, 0, 0), barra, 1)
                if es_jefe:
                    lblj = fent.render("EL JEFE", True, (255, 215, 60))
                    somj = fent.render("EL JEFE", True, (0, 0, 0))
                    rj = lblj.get_rect(midbottom=(barra.centerx, barra.top - 2))
                    pant.blit(somj, rj.move(1, 1))
                    pant.blit(lblj, rj)
        elif tent == "jugador":
            dibsombra(pant, o["rect"].centerx - cx, o["rect"].bottom - cy, o["rect"].width * 0.85)
            if o.get("dash") and ahora < o.get("dash_hasta", 0) and "sprdash" in o:
                ld = "derecha" if o.get("lado_x", 1) >= 0 else "izquierda"
                prog = (ahora - o.get("dash_ini", ahora)) / max(1, o.get("dash_dur", 230))
                sprj = o["sprdash"][ld][max(0, min(7, int(prog * 8)))]
                pant.blit(sprj, sprj.get_rect(midbottom=(o["rect"].centerx - cx, o["rect"].bottom - cy)))
            else:
                if o["ataq"]:
                    sprj = (o["sprataqrojos"] if ahora < o["golpe_hasta"] else o["sprataq"])[o["dirataq"]][o["fraataq"]]
                else:
                    d = o["dir"]
                    idx = [0, 1, 2, 1][int(o["frame"]) % 4]
                    sprj = (o["sprrojos"] if ahora < o["golpe_hasta"] else o["sprs"])[d][idx]
                pant.blit(sprj, (o["rect"].x - cx, o["rect"].y - cy))

    for p in proys or []:
        if p.get("invisible"):
            continue
        rp = p["rect"].move(-cx, -cy)
        if p.get("lado") == "pistola" and "angulo" in p:
            s_bala = balasrot[round(p["angulo"] / 5) % 72]
            pant.blit(s_bala, s_bala.get_rect(center=rp.center))
        else:
            col = (255, 230, 90) if p.get("lado") == "pistola" else ((235, 85, 75) if p.get("lado") == "enemigo" else (250, 250, 150))
            pygame.draw.ellipse(pant, col, rp)
            pygame.draw.ellipse(pant, (35, 30, 20), rp, 1)

    for c in jdat.get("chispas", []):
        pygame.draw.circle(pant, c["color"], (int(c["x"] - cx), int(c["y"] - cy)), c["radio"])

    for t in jdat.get("textos", []):
        it = fent.render(t["texto"], True, t["color"])
        st = fent.render(t["texto"], True, (0, 0, 0))
        rt = it.get_rect(midbottom=(int(t["x"] - cx), int(t["y"] - cy)))
        pant.blit(st, rt.move(1, 1))
        pant.blit(it, rt)

    if mvida:
        dibujarvida(pant, vidas, jdat, escudos=escudos)
