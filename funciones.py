import pygame
import cv2
import os
import math
import random

_fuentes_recursos = {}

def cargardat(ancho, alto):
    vida = 5
    escudo = 0
    puntos = 0
    oleada = 1
    pesos = 0
    panchos = 0
    speeds = 0
    pistola = False
    posicion_mc = (ancho // 2, int(alto * 0.50))
    mapa = 1
    ruta = "F/Datos.txt"

    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                if "=" not in linea:
                    continue
                clave, valor = linea.strip().split("=", 1)
                try:
                    if clave == "vida":
                        vida = max(0, min(5, int(valor)))
                    elif clave == "escudo":
                        escudo = max(0, min(3, int(valor)))
                    elif clave == "puntos":
                        puntos = max(0, int(valor))
                    elif clave == "oleada":
                        oleada = max(1, min(20, int(valor)))
                    elif clave == "pesos":
                        pesos = max(0, int(valor))
                    elif clave == "panchos":
                        panchos = max(0, int(valor))
                    elif clave == "speeds":
                        speeds = max(0, int(valor))
                    elif clave == "pistola":
                        pistola = valor == "1"
                    elif clave == "posicion_mc":
                        x, y = valor.split(",", 1)
                        posicion_mc = (int(x), int(y))
                    elif clave == "mapa":
                        mapa = "bazar" if valor.lower() == "bazar" else max(1, min(2, int(valor)))
                except ValueError:
                    continue

    return vida, escudo, puntos, oleada, pesos, panchos, speeds, pistola, posicion_mc, mapa

def guardardat(vida, puntos, oleada, pesos, panchos, pistola, posicion_mc, mapa, escudo=0, speeds=0):
    with open("F/Datos.txt", "w", encoding="utf-8") as archivo:
        archivo.write(f"vida={vida}\n")
        archivo.write(f"escudo={escudo}\n")
        archivo.write(f"puntos={puntos}\n")
        archivo.write(f"oleada={oleada}\n")
        archivo.write(f"pesos={pesos}\n")
        archivo.write(f"panchos={panchos}\n")
        archivo.write(f"speeds={speeds}\n")
        archivo.write(f"pistola={int(pistola)}\n")
        archivo.write(f"posicion_mc={posicion_mc[0]},{posicion_mc[1]}\n")
        archivo.write(f"mapa={mapa}\n")

def creahit(spr, pos):
    hitbox = spr.get_bounding_rect().move(pos)
    hitbox.inflate_ip(-max(2, int(hitbox.width * 0.25)), -max(2, int(hitbox.height * 0.20)))
    return hitbox

def colision_pies(rect):
    ancho_pies = max(4, int(rect.width * 0.38))
    alto_pies = max(4, int(rect.height * 0.16))
    return pygame.Rect(rect.centerx - ancho_pies // 2, rect.bottom - alto_pies, ancho_pies, alto_pies)

def obtener_obstaculos(mapa, ancho, alto):
    if mapa == 2:
        return [
            # Vías de tren y muro superior
            pygame.Rect(0, 0, ancho, int(alto * 0.095)),
            # Cancha de fútbol (alambrado perimetral)
            pygame.Rect(int(ancho * 0.595), int(alto * 0.148), int(ancho * 0.215), int(alto * 0.200)),
            # Torre de agua y galpón superior derecho
            pygame.Rect(int(ancho * 0.870), int(alto * 0.070), int(ancho * 0.130), int(alto * 0.170)),
            # Almacén La Matanza (edificio, contenedor y alambrado inferior derecho)
            pygame.Rect(int(ancho * 0.895), int(alto * 0.380), int(ancho * 0.105), int(alto * 0.400)),
            # Canal / zanjón de agua inferior
            pygame.Rect(0, int(alto * 0.890), ancho, int(alto * 0.110)),
            # Cartel de Argentina a la izquierda
            pygame.Rect(int(ancho * 0.112), int(alto * 0.445), int(ancho * 0.100), int(alto * 0.075)),
            # Valla de chapa inferior izquierda
            pygame.Rect(int(ancho * 0.082), int(alto * 0.805), int(ancho * 0.098), int(alto * 0.065)),
            # Torre pequeña superior izquierda
            pygame.Rect(int(ancho * 0.238), int(alto * 0.100), int(ancho * 0.030), int(alto * 0.115)),
            # Árbol central solitario (tronco mínimo)
            pygame.Rect(int(ancho * 0.450), int(alto * 0.482), int(ancho * 0.015), int(alto * 0.012)),
            # Árbol medio-izquierda (tronco mínimo)
            pygame.Rect(int(ancho * 0.283), int(alto * 0.377), int(ancho * 0.015), int(alto * 0.012)),
        ]
    else:
        return [
            # Hilera superior de locales y paredón (deja toda la vereda libre para caminar)
            pygame.Rect(0, 0, ancho, int(alto * 0.335)),
            # Base del árbol izquierdo
            pygame.Rect(0, int(alto * 0.335), int(ancho * 0.070), int(alto * 0.13)),
            # Torre de ladrillo esquina inferior izquierda
            pygame.Rect(0, int(alto * 0.56), int(ancho * 0.05), int(alto * 0.44)),
            # Casita inferior izquierda
            pygame.Rect(int(ancho * 0.05), int(alto * 0.70), int(ancho * 0.10), int(alto * 0.30)),
            # Muro y casas inferiores izquierda (alineado a la base donde toca la tierra)
            pygame.Rect(int(ancho * 0.15), int(alto * 0.83), int(ancho * 0.275), int(alto * 0.17)),
            # Muro de ladrillo y casas inferiores derecha (alineado a la base)
            pygame.Rect(int(ancho * 0.575), int(alto * 0.83), int(ancho * 0.425), int(alto * 0.17)),
            # Casa gris de la derecha (solo el edificio, dejando el camino libre)
            pygame.Rect(int(ancho * 0.875), int(alto * 0.56), int(ancho * 0.125), int(alto * 0.27)),
        ]

def ajustapos(jugdatos, posicion_mc, ancho, alto, mapa):
    rect = jugdatos["rect"]
    rect.left = max(0, min(posicion_mc[0], ancho - rect.width))
    rect.top = max(0, min(posicion_mc[1], alto - rect.height))

    obstaculos = obtener_obstaculos(mapa, ancho, alto)
    pies = colision_pies(rect)
    for obs in obstaculos:
        if pies.colliderect(obs):
            if obs.top <= 0:
                rect.top = obs.bottom
            elif obs.bottom >= alto:
                rect.bottom = obs.top
            elif obs.left <= 0:
                rect.left = obs.right
            elif obs.right >= ancho:
                rect.right = obs.left
            pies = colision_pies(rect)

    spr = jugdatos["sprs"][jugdatos["dir"]][0]
    jugdatos["hitbox"] = creahit(spr, rect.topleft)

def crearpuerta(ancho, alto):
    return pygame.Rect(int(ancho * 0.435), int(alto * 0.30), int(ancho * 0.06), int(alto * 0.09))

def cargarmapa2(ancho, alto, escala=2.4):
    img = pygame.image.load("Sprites/mapa2n.jpeg")
    w = int(ancho * escala)
    h = int(alto * escala)
    return pygame.transform.scale(img, (w, h)).convert()

def _recortar_fondo_claro(ruta):
    im_bgr = cv2.imread(ruta)
    if im_bgr is None:
        surf = pygame.image.load(ruta).convert_alpha()
        return surf
    hsv = cv2.cvtColor(im_bgr, cv2.COLOR_BGR2HSV)
    bg_candidates = ((hsv[:, :, 1] < 28) & (hsv[:, :, 2] > 215)).astype("uint8") * 255
    _, labels = cv2.connectedComponents(bg_candidates)
    bordes = set(labels[0, :]) | set(labels[-1, :]) | set(labels[:, 0]) | set(labels[:, -1])
    bordes.discard(0)
    es_fondo = cv2.inRange(labels, 0, 0) == 0
    # Marcar como fondo únicamente las componentes conectadas a los bordes
    import numpy as np
    mask_fondo = np.isin(labels, list(bordes))
    mask_fg = ~mask_fondo
    ys, xs = np.where(mask_fg)
    if len(xs) > 0 and len(ys) > 0:
        x0, x1 = xs.min(), xs.max() + 1
        y0, y1 = ys.min(), ys.max() + 1
    else:
        x0, y0, x1, y1 = 0, 0, im_bgr.shape[1], im_bgr.shape[0]
    im_rgb = cv2.cvtColor(im_bgr[y0:y1, x0:x1], cv2.COLOR_BGR2RGB)
    alpha = (mask_fg[y0:y1, x0:x1].astype("uint8") * 255)
    rgba = np.dstack((im_rgb, alpha))
    return pygame.image.frombuffer(rgba.tobytes(), (x1 - x0, y1 - y0), "RGBA").convert_alpha()

def cargarvidas(alto):
    vidas = []
    altovida = int(alto * 0.14)
    for numero in range(6):
        ruta = f"Sprites/Vida/vida{numero:02d}.png"
        img = pygame.image.load(ruta).convert_alpha()
        proporcion = img.get_width() / img.get_height()
        vidas.append(pygame.transform.scale(img, (int(altovida * proporcion), altovida)))
    return vidas

def cargarescudos(alto):
    escudos = []
    # Escala proporcional a la barra de vida para ubicarse justo arriba de ella
    altoescudo = int(alto * 0.115)
    anchoescudo = int(alto * 0.14 * 3.0)
    for numero in range(1, 5):
        ruta = f"Sprites/escudo/escudo{numero}.jpg"
        if not os.path.exists(ruta):
            ruta = f"escudo{numero}.jpg"
        surf = _recortar_fondo_claro(ruta)
        escudos.append(pygame.transform.smoothscale(surf, (anchoescudo, altoescudo)))
    return escudos

_SOMBRAS = {}
_CACHE_SPRITES_ENEMIGOS = {}
_CACHE_DROPS = {}
_CACHE_BALAS = {}

DANO_PUNO = 16
DANO_BALA = 28

TIPOS_ENEMIGO = {
    "hincha": {
        "hp": 30, "vel_mult": 1.0, "dano": 0.5, "escala": 1.0, "tinte": None,
        "puntos": 10, "pesos": (15, 30), "alcance_mult": 1.15, "espera": 900
    },
    "barra": {
        "hp": 20, "vel_mult": 1.45, "dano": 0.5, "escala": 0.92, "tinte": ("add", (55, 0, 0)),
        "puntos": 15, "pesos": (20, 40), "alcance_mult": 1.05, "espera": 650
    },
    "tanque": {
        "hp": 90, "vel_mult": 0.72, "dano": 1.0, "escala": 1.35, "tinte": ("mult", (255, 205, 120)),
        "puntos": 30, "pesos": (45, 75), "alcance_mult": 1.25, "espera": 1150
    },
    "jefe": {
        "hp": 320, "vel_mult": 0.85, "dano": 1.0, "escala": 2.1, "tinte": ("add", (45, 5, 0)),
        "puntos": 200, "pesos": (180, 260), "alcance_mult": 1.35, "espera": 1050
    },
}

def tintar_superficie(superficie, tinte):
    if not tinte:
        return superficie
    modo, color = tinte
    copia = superficie.copy()
    bandera = pygame.BLEND_RGB_ADD if modo == "add" else pygame.BLEND_RGB_MULT
    copia.fill(color, special_flags=bandera)
    return copia

def blanquear_superficie(superficie):
    copia = superficie.copy()
    copia.fill((110, 110, 110), special_flags=pygame.BLEND_RGB_ADD)
    return copia

def agregar_texto_flotante(jugdatos, texto, x, y, color=(255, 255, 255)):
    if jugdatos is None:
        return
    jugdatos.setdefault("textos", []).append({
        "texto": str(texto),
        "x": float(x),
        "y": float(y),
        "inicio": pygame.time.get_ticks(),
        "duracion": 850,
        "color": color
    })

def agregar_chispas(jugdatos, x, y, color=(255, 215, 60), cantidad=6, fuerza=4.5):
    if jugdatos is None:
        return
    ahora = pygame.time.get_ticks()
    chispas = jugdatos.setdefault("chispas", [])
    for _ in range(cantidad):
        ang = random.uniform(0, math.tau)
        vel = random.uniform(0.35, 1.0) * fuerza
        chispas.append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(ang) * vel,
            "vy": math.sin(ang) * vel,
            "inicio": ahora,
            "vida": random.randint(200, 420),
            "color": color,
            "radio": random.choice((2, 3, 3, 4)),
        })

def configurar_banner(jugdatos, texto, sub="", duracion_ms=2400):
    if jugdatos is None:
        return
    jugdatos["banner"] = {
        "texto": texto,
        "sub": sub,
        "inicio": pygame.time.get_ticks(),
        "dur": duracion_ms
    }

def dibujarvida(pantalla, vidas, jugdatos, escudos=None):
    vida = max(0, min(jugdatos["vida"], 5))
    spritevida = 5 - vida
    rectvida = vidas[spritevida].get_rect(bottomleft=(0, pantalla.get_height()))
    if escudos:
        nivel_escudo = max(0, min(jugdatos.get("escudo", 0), 3))
        # escudo4.jpg (índice 3) es sin escudo (0), y sube a escudo3 (idx 2), escudo2 (idx 1), escudo1 (idx 0)
        idx_escudo = 3 - nivel_escudo
        rectescudo = escudos[idx_escudo].get_rect(bottomleft=(0, rectvida.top - max(2, int(pantalla.get_height() * 0.005))))
        pantalla.blit(escudos[idx_escudo], rectescudo)
    pantalla.blit(vidas[spritevida], rectvida)

    # Barra de recarga del DASH arriba de las barras o a la derecha de la vida
    ahora = pygame.time.get_ticks()
    alto = pantalla.get_height()
    tam_f = max(18, int(alto * 0.024))
    if tam_f not in _fuentes_recursos:
        _fuentes_recursos[tam_f] = pygame.font.Font(None, tam_f)
    fuente_d = _fuentes_recursos[tam_f]
    x_dash = rectvida.right + max(14, int(alto * 0.02))
    y_dash = alto - max(22, int(alto * 0.032))
    barra = pygame.Rect(x_dash, y_dash, int(alto * 0.18), max(8, int(alto * 0.014)))
    cd_fin = jugdatos.get("dash_cd_hasta", 0)
    cd_dur = max(1, jugdatos.get("dash_cd_dur", 950))
    restante = max(0, cd_fin - ahora)
    carga = max(0.0, min(1.0, 1.0 - restante / cd_dur))
    lbl_dash = fuente_d.render("DASH [SHIFT]", True, (255, 255, 255))
    pantalla.blit(lbl_dash, (barra.x, barra.y - lbl_dash.get_height() - 2))
    pygame.draw.rect(pantalla, (30, 30, 30), barra, border_radius=4)
    color_barra = (90, 220, 110) if carga >= 1.0 else (255, 215, 60)
    if carga > 0:
        pygame.draw.rect(pantalla, color_barra, pygame.Rect(barra.x, barra.y, int(barra.width * carga), barra.height), border_radius=4)
    pygame.draw.rect(pantalla, (255, 255, 255), barra, 1, border_radius=4)

def aplicar_daño_jugador(jugdatos, ahora, cantidad=0.5, origen=None, ancho_mapa=None, alto_mapa=None, obstaculos=None):
    if ahora < jugdatos.get("dash_invul_hasta", 0):
        return False

    cant = float(cantidad)
    dano_total = jugdatos.get("dano_acumulado", 0.0) + cant
    puntos_a_quitar = int(dano_total)
    jugdatos["dano_acumulado"] = round(dano_total - puntos_a_quitar, 4)

    consumio_escudo = False
    if puntos_a_quitar > 0:
        dano_restante = puntos_a_quitar
        while dano_restante > 0:
            if jugdatos.get("escudo", 0) > 0:
                jugdatos["escudo"] -= 1
                consumio_escudo = True
            else:
                jugdatos["vida"] = max(0, jugdatos["vida"] - 1)
                consumio_escudo = False
            dano_restante -= 1

    jugdatos["ultimo_daño"] = ahora
    jugdatos["golpe_hasta"] = ahora + 220
    jugdatos["shake_hasta"] = ahora + 220

    tiene_escudo = jugdatos.get("escudo", 0) > 0 or consumio_escudo
    if puntos_a_quitar > 0:
        txt = f"-{puntos_a_quitar} ESCUDO" if consumio_escudo else f"-{puntos_a_quitar} VIDA"
        color_txt = (120, 200, 255) if consumio_escudo else (235, 65, 65)
    else:
        txt = "-0.5 ESCUDO" if tiene_escudo else "-0.5 VIDA"
        color_txt = (160, 220, 255) if tiene_escudo else (255, 130, 130)

    agregar_texto_flotante(jugdatos, txt, jugdatos["rect"].centerx, jugdatos["rect"].top - 10, color_txt)
    agregar_chispas(jugdatos, jugdatos["rect"].centerx, jugdatos["rect"].centery, (230, 60, 60), cantidad=8, fuerza=5.0)

    if origen is not None and ancho_mapa and alto_mapa:
        ox, oy = origen["rect"].center if isinstance(origen, dict) and "rect" in origen else (origen.centerx, origen.centery)
        dx = jugdatos["rect"].centerx - ox
        dy = jugdatos["rect"].centery - oy
        dist = math.hypot(dx, dy)
        if dist > 0:
            empuje = max(10, int(jugdatos["rect"].height * 0.35))
            ex = round((dx / dist) * empuje)
            ey = round((dy / dist) * empuje)
            jugdatos["rect"].x = max(0, min(ancho_mapa - jugdatos["rect"].width, jugdatos["rect"].x + ex))
            if obstaculos and any(colision_pies(jugdatos["rect"]).colliderect(obs) for obs in obstaculos):
                jugdatos["rect"].x -= ex
            jugdatos["rect"].y = max(0, min(alto_mapa - jugdatos["rect"].height, jugdatos["rect"].y + ey))
            if obstaculos and any(colision_pies(jugdatos["rect"]).colliderect(obs) for obs in obstaculos):
                jugdatos["rect"].y -= ey
    return True

def recibirdaño(jugdatos, objetivos):
    ahora = pygame.time.get_ticks()
    if ahora - jugdatos["ultimo_daño"] < 900 or ahora < jugdatos.get("dash_invul_hasta", 0):
        return

    for objetivo in objetivos:
        if isinstance(objetivo, dict) and objetivo["vida"] <= 0:
            continue
        hitbox = objetivo["hitbox"] if isinstance(objetivo, dict) else objetivo
        if jugdatos["hitbox"].colliderect(hitbox):
            dano = objetivo.get("dano", 0.5) if isinstance(objetivo, dict) else 0.5
            aplicar_daño_jugador(jugdatos, ahora, cantidad=dano, origen=objetivo)
            return

def rojospr(spr):
    img = spr.copy()
    img.fill((255, 70, 70, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return img

def _obtener_sprites_enemigo_tipo(tipo, alto_pantalla):
    clave = (tipo, alto_pantalla)
    if clave in _CACHE_SPRITES_ENEMIGOS:
        return _CACHE_SPRITES_ENEMIGOS[clave]

    cfg = TIPOS_ENEMIGO.get(tipo, TIPOS_ENEMIGO["hincha"])
    hjug = max(16, int(alto_pantalla * 0.075 * cfg["escala"]))
    wjug = max(12, int(hjug * (52 / 96)))
    sec = {
        "abajo": [0, 1, 2],
        "arriba": [4, 5, 6],
        "izquierda": [8, 9, 10],
        "derecha": [12, 13, 14]
    }
    sprs = {}
    sprataq = {}
    for d, nums in sec.items():
        sprs[d] = []
        sprataq[d] = []
        for n in nums:
            img = pygame.image.load(f"Sprites/Boca/Boca{n:03d}.png").convert_alpha()
            img_esc = tintar_superficie(pygame.transform.scale(img, (wjug, hjug)), cfg["tinte"])
            sprs[d].append(img_esc)
            img_a = pygame.image.load(f"Sprites/Boca/BA/BA{n:02d}.png").convert_alpha()
            img_a_esc = tintar_superficie(pygame.transform.scale(img_a, (wjug, hjug)), cfg["tinte"])
            sprataq[d].append(img_a_esc)

    sprrojos = {d: [blanquear_superficie(rojospr(img)) for img in imgs] for d, imgs in sprs.items()}
    sprataqrojos = {d: [blanquear_superficie(rojospr(img)) for img in imgs] for d, imgs in sprataq.items()}
    datos_spr = (wjug, hjug, sprs, sprrojos, sprataq, sprataqrojos)
    _CACHE_SPRITES_ENEMIGOS[clave] = datos_spr
    return datos_spr

def armar_cola_oleada(oleada):
    total = min(45, 5 + 3 * oleada)
    p_tanque = 0.0 if oleada < 4 else min(0.30, 0.10 + 0.02 * (oleada - 4))
    p_barra = 0.0 if oleada < 2 else min(0.40, 0.20 + 0.03 * (oleada - 2))
    cola = []
    for _ in range(total):
        r = random.random()
        if r < p_tanque:
            cola.append("tanque")
        elif r < p_tanque + p_barra:
            cola.append("barra")
        else:
            cola.append("hincha")
    jefes = oleada // 5 if oleada % 5 == 0 else 0
    for _ in range(jefes):
        cola.insert(len(cola) // 3, "jefe")
    return {
        "numero": oleada,
        "cola": cola,
        "total": len(cola),
        "jefe": jefes > 0,
        "ultimo_spawn": pygame.time.get_ticks(),
        "intervalo_ms": max(420, int((1.35 - 0.06 * oleada) * 1000)),
        "max_sim": min(24, 7 + oleada),
        "completada": False,
    }

def instanciar_enemigo(tipo, oleada, ancho, alto, alto_pantalla, existentes, jugdatos=None, indice=0, total_esperado=10):
    cfg = TIPOS_ENEMIGO.get(tipo, TIPOS_ENEMIGO["hincha"])
    wjug, hjug, sprs, sprrojos, sprataq, sprataqrojos = _obtener_sprites_enemigo_tipo(tipo, alto_pantalla)
    minx = min(int(ancho * 0.10), max(0, ancho - wjug))
    maxx = max(minx, int(ancho * 0.88) - wjug)
    miny = min(int(alto * 0.14), max(0, alto - hjug))
    maxy = max(miny, int(alto * 0.84) - hjug)
    espacio = max(12, int(wjug * 0.65))
    obstaculos = obtener_obstaculos(2, ancho, alto)

    rect = sprs["abajo"][0].get_rect()
    jx = jugdatos["rect"].centerx if jugdatos else ancho // 4
    jy = jugdatos["rect"].centery if jugdatos else alto // 2
    dist_min_jug = max(260, int(alto_pantalla * 0.42))

    for intento in range(55):
        if intento < 35 and jugdatos is not None:
            # Preferir bordes de la zona caminable o puntos alejados del jugador
            lado = random.choice(("der", "arr", "aba", "azar"))
            if lado == "der":
                rx = random.randint(max(minx, int(ancho * 0.65)), maxx)
                ry = random.randint(miny, maxy)
            elif lado == "arr":
                rx = random.randint(minx, maxx)
                ry = random.randint(miny, min(maxy, int(alto * 0.30)))
            elif lado == "aba":
                rx = random.randint(minx, maxx)
                ry = random.randint(max(miny, int(alto * 0.68)), maxy)
            else:
                rx = random.randint(minx, maxx)
                ry = random.randint(miny, maxy)
            rect.topleft = (rx, ry)
        else:
            rect.topleft = (random.randint(minx, maxx), random.randint(miny, maxy))

        if math.hypot(rect.centerx - jx, rect.centery - jy) < dist_min_jug and intento < 40:
            continue
        pies_ene = colision_pies(rect)
        if any(pies_ene.colliderect(obs) for obs in obstaculos):
            continue
        if all(not rect.inflate(espacio, espacio).colliderect(otro["rect"]) for otro in existentes):
            break

    hp_max = round(cfg["hp"] * (1 + 0.10 * (oleada - 1)))
    vel_base = alto_pantalla * 0.0040 * cfg["vel_mult"] * min(1.35, 1 + 0.015 * (oleada - 1)) * random.uniform(0.92, 1.08)
    angulo_base = (indice / max(1, total_esperado)) * 2 * math.pi + random.uniform(-0.2, 0.2)

    return {
        "nombre": f"enemigo {tipo}",
        "tipo": tipo,
        "escala": cfg["escala"],
        "dano": cfg["dano"],
        "puntos": cfg["puntos"],
        "pesos_rango": cfg["pesos"],
        "alcance_mult": cfg["alcance_mult"],
        "espera_ms": cfg["espera"],
        "rect": rect,
        "hitbox": creahit(sprs["abajo"][0], rect.topleft),
        "sprs": sprs,
        "sprrojos": sprrojos,
        "sprataq": sprataq,
        "sprataqrojos": sprataqrojos,
        "vida": hp_max,
        "vida_max": hp_max,
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
        "vel": max(1, round(vel_base)),
        "angulo_ataque": angulo_base,
        "radio_mult": random.uniform(0.9, 1.35)
    }

def crearene(ancho, alto, cantidad=1, oleada=1, alto_pantalla=None, jugdatos=None):
    if alto_pantalla is None:
        alto_pantalla = int(alto / 2.4)

    info_oleada = armar_cola_oleada(oleada)
    enemigos = []
    iniciales = min(len(info_oleada["cola"]), max(4, min(info_oleada["max_sim"] // 2, 8)))
    for i in range(iniciales):
        tipo = info_oleada["cola"].pop(0)
        ene = instanciar_enemigo(tipo, oleada, ancho, alto, alto_pantalla, enemigos, jugdatos=jugdatos, indice=i, total_esperado=info_oleada["total"])
        enemigos.append(ene)

    if jugdatos is not None:
        jugdatos["oleada_info"] = info_oleada
        jugdatos["drops"] = []
        jugdatos["textos"] = []
        jugdatos["chispas"] = []
        sub = "¡Cuidado, viene EL JEFE!" if info_oleada["jefe"] else f"{info_oleada['total']} enemigos en camino"
        configurar_banner(jugdatos, f"OLEADA {oleada}", sub, duracion_ms=2500)

    return enemigos

def danar_enemigo(enemigo, cantidad, empuje_x=0.0, empuje_y=0.0, jugdatos=None):
    ahora = pygame.time.get_ticks()
    es_escala_nueva = enemigo.get("vida_max", 3) > 5
    dano_real = cantidad if es_escala_nueva else max(1, round(cantidad / 14))
    resistencia = 0.3 if enemigo.get("tipo") == "jefe" else 1.0
    escala = enemigo.get("escala", 1.0)

    enemigo["vida"] = max(0, enemigo["vida"] - dano_real)
    enemigo["golpe_hasta"] = ahora + 160
    enemigo["kx"] = enemigo.get("kx", 0.0) + (empuje_x * resistencia / escala)
    enemigo["ky"] = enemigo.get("ky", 0.0) + (empuje_y * resistencia / escala)

    agregar_texto_flotante(jugdatos, str(int(dano_real)), enemigo["rect"].centerx, enemigo["rect"].top - 6, (255, 255, 255))
    agregar_chispas(jugdatos, enemigo["hitbox"].centerx, enemigo["hitbox"].centery, (255, 215, 60), cantidad=5, fuerza=4.2)

def crearproy(jugdatos):
    rect = jugdatos["hitbox"]
    dir_a = jugdatos["dirataq"]
    w_zona = max(24, int(rect.width * 1.65))
    h_zona = max(24, int(rect.height * 1.15))
    proy = pygame.Rect(0, 0, w_zona, h_zona)
    vel = max(7, int(rect.height * 0.20))
    alcance = max(w_zona // 2, int(rect.height * 0.70))
    dx, dy = 0, 0

    if dir_a == "arriba":
        proy.midbottom = (rect.centerx, rect.centery)
        dy = -vel
    elif dir_a == "abajo":
        proy.midtop = (rect.centerx, rect.centery)
        dy = vel
    elif dir_a == "izquierda":
        proy.midright = (rect.centerx, rect.centery)
        dx = -vel
    else:
        proy.midleft = (rect.centerx, rect.centery)
        dx = vel

    return {
        "rect": proy,
        "dx": dx,
        "dy": dy,
        "alcance": alcance,
        "recorrido": 0,
        "tocados": set(),
        "lado": "puno",
        "invisible": True
    }

def crearproypistola(jugdatos, destino):
    ahora = pygame.time.get_ticks()
    if ahora < jugdatos.get("cd_disparo_hasta", 0):
        return None
    origen = (jugdatos["hitbox"].centerx, jugdatos["hitbox"].centery - int(jugdatos["hitbox"].height * 0.12))
    dx = destino[0] - origen[0]
    dy = destino[1] - origen[1]
    distancia = math.hypot(dx, dy)
    if distancia == 0:
        return None
    ux, uy = dx / distancia, dy / distancia
    if abs(ux) >= abs(uy):
        jugdatos["dir"] = "derecha" if ux > 0 else "izquierda"
    else:
        jugdatos["dir"] = "abajo" if uy > 0 else "arriba"
    if ux != 0:
        jugdatos["lado_x"] = 1 if ux > 0 else -1

    jugdatos["cd_disparo_hasta"] = ahora + 220
    tam = max(8, int(jugdatos["hitbox"].height * 0.14))
    proy = pygame.Rect(0, 0, tam, tam)
    proy.center = (int(origen[0] + ux * 16), int(origen[1] + uy * 16))
    vel_bala = max(20, int(jugdatos["hitbox"].height * 0.42))
    angulo = math.degrees(math.atan2(-uy, ux))
    agregar_chispas(jugdatos, proy.centerx, proy.centery, (255, 215, 60), cantidad=3, fuerza=3.2)

    return {
        "rect": proy,
        "dx": ux * vel_bala,
        "dy": uy * vel_bala,
        "alcance": max(distancia, jugdatos["hitbox"].height * 9.5),
        "recorrido": 0,
        "destino": destino,
        "angulo": angulo,
        "lado": "pistola"
    }

def crearproyene(enemigo, jugdatos):
    dx = jugdatos["hitbox"].centerx - enemigo["hitbox"].centerx
    dy = jugdatos["hitbox"].centery - enemigo["hitbox"].centery
    dir = "derecha" if dx >= 0 else "izquierda"
    if abs(dy) > abs(dx):
        dir = "abajo" if dy >= 0 else "arriba"
    enemigo["dir"] = dir
    enemigo["ataq"] = True
    enemigo["golpe_hecho"] = False
    enemigo["fraataq"] = 0
    enemigo["ultfra"] = pygame.time.get_ticks()
    enemigo["proximoataq"] = pygame.time.get_ticks() + enemigo.get("espera_ms", 850)

    hitbox = enemigo["hitbox"]
    tam = max(8, int(hitbox.height * 0.16))
    vel = max(6, int(hitbox.height * 0.18))
    proy = pygame.Rect(0, 0, tam, tam)
    if dir == "arriba":
        proy.center = (hitbox.centerx, hitbox.top)
        movx, movy = 0, -vel
    elif dir == "abajo":
        proy.center = (hitbox.centerx, hitbox.bottom)
        movx, movy = 0, vel
    elif dir == "izquierda":
        proy.center = (hitbox.left, hitbox.centery)
        movx, movy = -vel, 0
    else:
        proy.center = (hitbox.right, hitbox.centery)
        movx, movy = vel, 0
    alcance = max(tam, int(hitbox.height * 0.85))
    return {
        "rect": proy,
        "dx": movx,
        "dy": movy,
        "alcance": alcance,
        "recorrido": 0,
        "lado": "enemigo",
        "dano": enemigo.get("dano", 0.5),
        "origen": enemigo
    }

def generar_drops_enemigo(jugdatos, enemigo):
    if jugdatos is None:
        return
    ahora = pygame.time.get_ticks()
    drops = jugdatos.setdefault("drops", [])
    ex, ey = enemigo["rect"].centerx, enemigo["rect"].bottom
    rango_pesos = enemigo.get("pesos_rango", (15, 30))

    if enemigo.get("tipo") == "jefe":
        total = random.randint(*rango_pesos)
        for _ in range(6):
            drops.append({
                "tipo": "peso",
                "x": ex + random.uniform(-35, 35),
                "y": ey + random.uniform(-18, 18),
                "valor": max(5, total // 6),
                "inicio": ahora,
                "vida_ms": 16000,
                "iman": False
            })
        drops.append({
            "tipo": "pancho",
            "x": ex,
            "y": ey,
            "valor": 1,
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
            "valor": random.randint(*rango_pesos),
            "inicio": ahora,
            "vida_ms": 14000,
            "iman": False
        })
    if random.random() < 0.12:
        drops.append({
            "tipo": "pancho",
            "x": ex + random.uniform(-10, 10),
            "y": ey + random.uniform(-6, 6),
            "valor": 1,
            "inicio": ahora,
            "vida_ms": 14000,
            "iman": False
        })
    if jugdatos.get("pistola") and random.random() < 0.18:
        drops.append({
            "tipo": "balas",
            "x": ex + random.uniform(-10, 10),
            "y": ey + random.uniform(-6, 6),
            "valor": 3,
            "inicio": ahora,
            "vida_ms": 14000,
            "iman": False
        })

def actualizar_drops_y_efectos(jugdatos):
    if jugdatos is None:
        return
    ahora = pygame.time.get_ticks()
    jx, jy = jugdatos["rect"].centerx, jugdatos["rect"].centery

    # Actualizar drops en el suelo
    nuevos_drops = []
    for d in jugdatos.get("drops", []):
        edad = ahora - d["inicio"]
        if edad >= d["vida_ms"]:
            continue
        dx = jx - d["x"]
        dy = jy - d["y"]
        dist = math.hypot(dx, dy)
        radio_iman = max(90, int(jugdatos["rect"].height * 1.45))
        if d.get("iman") or dist < radio_iman:
            vel_iman = 11.0 if d.get("iman") else 5.5
            if dist > 0:
                d["x"] += (dx / dist) * vel_iman
                d["y"] += (dy / dist) * vel_iman
        if dist < max(26, int(jugdatos["rect"].width * 0.75)):
            if d["tipo"] == "peso":
                jugdatos["pesos"] = jugdatos.get("pesos", 0) + d["valor"]
                agregar_texto_flotante(jugdatos, f"+${d['valor']}", jx, jugdatos["rect"].top - 12, (255, 215, 60))
            elif d["tipo"] == "pancho":
                if jugdatos["vida"] < 5:
                    jugdatos["vida"] = min(5, jugdatos["vida"] + 1)
                    jugdatos["dano_acumulado"] = 0.0
                    agregar_texto_flotante(jugdatos, "+1 VIDA", jx, jugdatos["rect"].top - 12, (90, 220, 110))
                else:
                    jugdatos["panchos_extra"] = jugdatos.get("panchos_extra", 0) + 1
                    agregar_texto_flotante(jugdatos, "+1 PANCHO", jx, jugdatos["rect"].top - 12, (90, 220, 110))
            elif d["tipo"] == "balas":
                jugdatos["balas_extra"] = jugdatos.get("balas_extra", 0) + d["valor"]
                agregar_texto_flotante(jugdatos, f"+{d['valor']} BALAS", jx, jugdatos["rect"].top - 12, (120, 200, 255))
            continue
        nuevos_drops.append(d)
    jugdatos["drops"] = nuevos_drops

    # Actualizar chispas
    nuevas_chispas = []
    for c in jugdatos.get("chispas", []):
        if ahora - c["inicio"] >= c["vida"]:
            continue
        c["x"] += c["vx"]
        c["y"] += c["vy"]
        c["vy"] += 0.22
        nuevas_chispas.append(c)
    jugdatos["chispas"] = nuevas_chispas

    # Actualizar textos flotantes
    nuevos_textos = []
    for t in jugdatos.get("textos", []):
        if ahora - t["inicio"] >= t["duracion"]:
            continue
        t["y"] -= 0.75
        nuevos_textos.append(t)
    jugdatos["textos"] = nuevos_textos

    # Actualizar banner
    banner = jugdatos.get("banner")
    if banner and ahora - banner["inicio"] >= banner["dur"]:
        jugdatos["banner"] = None

def actualizaene(enemigos, jugdatos, proys, obstaculos=None, ancho=None, alto=None):
    ahora = pygame.time.get_ticks()
    actualizar_drops_y_efectos(jugdatos)

    # Spawner progresivo de la oleada
    info_oleada = jugdatos.get("oleada_info") if jugdatos else None
    vivos = [e for e in enemigos if e["vida"] > 0]
    if info_oleada and info_oleada["cola"]:
        if len(vivos) < info_oleada["max_sim"] and (ahora - info_oleada["ultimo_spawn"] >= info_oleada["intervalo_ms"] or len(vivos) == 0):
            info_oleada["ultimo_spawn"] = ahora
            tipo_nuevo = info_oleada["cola"].pop(0)
            w_m = ancho or 2400
            h_m = alto or 1400
            h_pant = int(h_m / 2.4)
            idx_spawn = info_oleada["total"] - len(info_oleada["cola"])
            nuevo_ene = instanciar_enemigo(tipo_nuevo, info_oleada["numero"], w_m, h_m, h_pant, enemigos, jugdatos=jugdatos, indice=idx_spawn, total_esperado=info_oleada["total"])
            enemigos.append(nuevo_ene)
            vivos.append(nuevo_ene)
            if tipo_nuevo == "jefe":
                configurar_banner(jugdatos, "¡LLEGÓ EL JEFE!", "Derrotalo para despejar la zona", duracion_ms=2400)

    total_vivos = len(vivos)
    if total_vivos == 0:
        if info_oleada and not info_oleada["cola"] and not info_oleada.get("completada"):
            info_oleada["completada"] = True
            n = info_oleada["numero"]
            bonus = 25 * n
            jugdatos["pesos"] = jugdatos.get("pesos", 0) + bonus
            jugdatos["puntos"] = jugdatos.get("puntos", 0) + 50 * n
            for d in jugdatos.get("drops", []):
                d["iman"] = True
            configurar_banner(jugdatos, f"¡OLEADA {n} COMPLETADA!", f"+${bonus} de bonus - Avanza a la derecha ->", duracion_ms=3500)
        return

    jug_center = jugdatos["hitbox"].center
    alcance_base = jugdatos["hitbox"].height * 1.25

    for idx, enemigo in enumerate(vivos):
        if "angulo_ataque" not in enemigo:
            enemigo["angulo_ataque"] = (idx / max(1, total_vivos)) * 2 * math.pi
            enemigo["radio_mult"] = random.uniform(0.9, 1.35)

        # Aplicar retroceso (knockback) si recibió un golpe o disparo
        kx = enemigo.get("kx", 0.0)
        ky = enemigo.get("ky", 0.0)
        if abs(kx) > 0.4 or abs(ky) > 0.4:
            rx = round(kx)
            ry = round(ky)
            if rx != 0:
                enemigo["rect"].x += rx
                if obstaculos and any(colision_pies(enemigo["rect"]).colliderect(obs) for obs in obstaculos):
                    enemigo["rect"].x -= rx
            if ry != 0:
                enemigo["rect"].y += ry
                if obstaculos and any(colision_pies(enemigo["rect"]).colliderect(obs) for obs in obstaculos):
                    enemigo["rect"].y -= ry
            enemigo["kx"] = kx * 0.78
            enemigo["ky"] = ky * 0.78

        dx_jug = jug_center[0] - enemigo["hitbox"].centerx
        dy_jug = jug_center[1] - enemigo["hitbox"].centery
        dist_jug = math.hypot(dx_jug, dy_jug)
        alcance_ene = alcance_base * enemigo.get("alcance_mult", 1.15)

        if enemigo["ataq"]:
            if ahora - enemigo["ultfra"] >= 110:
                enemigo["fraataq"] += 1
                enemigo["ultfra"] = ahora
                if enemigo["fraataq"] == 1 and not enemigo.get("golpe_hecho", False):
                    enemigo["golpe_hecho"] = True
                    if dist_jug <= alcance_ene * 1.25 and ahora - jugdatos["ultimo_daño"] >= 900:
                        aplicar_daño_jugador(jugdatos, ahora, cantidad=enemigo.get("dano", 0.5), origen=enemigo, ancho_mapa=ancho, alto_mapa=alto, obstaculos=obstaculos)
                if enemigo["fraataq"] >= 3:
                    enemigo["ataq"] = False
                    enemigo["fraataq"] = 0
        elif dist_jug <= alcance_ene and ahora >= enemigo["proximoataq"]:
            proys.append(crearproyene(enemigo, jugdatos))
        else:
            # Objetivo envolvente alrededor del jugador
            radio_flanco = alcance_ene * enemigo.get("radio_mult", 1.1)
            target_x = jug_center[0] + math.cos(enemigo["angulo_ataque"]) * radio_flanco
            target_y = jug_center[1] + math.sin(enemigo["angulo_ataque"]) * radio_flanco

            vx = target_x - enemigo["rect"].centerx
            vy = target_y - enemigo["rect"].centery
            dist_target = math.hypot(vx, vy)

            dir_x = (vx / dist_target) if dist_target > 4 else 0.0
            dir_y = (vy / dist_target) if dist_target > 4 else 0.0

            # Fuerza de separación para evitar que se apilen todos en una sola masa
            radio_sep = max(enemigo["rect"].width, enemigo["rect"].height) * 1.35
            sep_x = 0.0
            sep_y = 0.0

            for otro in vivos:
                if otro is enemigo:
                    continue
                ox = enemigo["rect"].centerx - otro["rect"].centerx
                oy = enemigo["rect"].centery - otro["rect"].centery
                dist_sq = ox * ox + oy * oy
                if 0 < dist_sq < (radio_sep * radio_sep):
                    d = math.sqrt(dist_sq)
                    fuerza = (radio_sep - d) / radio_sep
                    sep_x += (ox / d) * fuerza
                    sep_y += (oy / d) * fuerza
                elif dist_sq == 0:
                    rnd_ang = random.uniform(0, 2 * math.pi)
                    sep_x += math.cos(rnd_ang)
                    sep_y += math.sin(rnd_ang)

            total_x = dir_x + sep_x * 1.8
            total_y = dir_y + sep_y * 1.8
            mag = math.hypot(total_x, total_y)

            if mag > 0.08:
                vel = enemigo["vel"]
                paso = min(float(vel), max(1.0, dist_target))
                movx = round((total_x / mag) * paso)
                movy = round((total_y / mag) * paso)

                if abs(movx) > abs(movy):
                    enemigo["dir"] = "derecha" if movx > 0 else "izquierda"
                elif abs(movy) > 0:
                    enemigo["dir"] = "abajo" if movy > 0 else "arriba"
                else:
                    if abs(dx_jug) >= abs(dy_jug):
                        enemigo["dir"] = "derecha" if dx_jug > 0 else "izquierda"
                    else:
                        enemigo["dir"] = "abajo" if dy_jug > 0 else "arriba"

                if obstaculos:
                    if movx != 0:
                        enemigo["rect"].x += movx
                        pies_e = colision_pies(enemigo["rect"])
                        if any(pies_e.colliderect(obs) for obs in obstaculos):
                            enemigo["rect"].x -= movx
                    if movy != 0:
                        enemigo["rect"].y += movy
                        pies_e = colision_pies(enemigo["rect"])
                        if any(pies_e.colliderect(obs) for obs in obstaculos):
                            enemigo["rect"].y -= movy
                else:
                    enemigo["rect"].move_ip(movx, movy)

                # Separación física directa si dos enemigos colisionan sus cajas
                for otro in vivos:
                    if otro is enemigo:
                        continue
                    if enemigo["rect"].colliderect(otro["rect"]):
                        pdx = enemigo["rect"].centerx - otro["rect"].centerx
                        pdy = enemigo["rect"].centery - otro["rect"].centery
                        if pdx == 0 and pdy == 0:
                            pdx = random.choice([-1, 1])
                        push_x = 1 if pdx > 0 else -1
                        enemigo["rect"].x += push_x
                        if obstaculos and any(colision_pies(enemigo["rect"]).colliderect(obs) for obs in obstaculos):
                            enemigo["rect"].x -= push_x
                        push_y = 1 if pdy > 0 else -1
                        enemigo["rect"].y += push_y
                        if obstaculos and any(colision_pies(enemigo["rect"]).colliderect(obs) for obs in obstaculos):
                            enemigo["rect"].y -= push_y

                if ahora - enemigo["ultmov"] >= 140 and (movx != 0 or movy != 0):
                    enemigo["frame"] = (enemigo["frame"] + 1) % 3
                    enemigo["ultmov"] = ahora
            else:
                if abs(dx_jug) >= abs(dy_jug):
                    enemigo["dir"] = "derecha" if dx_jug > 0 else "izquierda"
                else:
                    enemigo["dir"] = "abajo" if dy_jug > 0 else "arriba"

        if enemigo["ataq"]:
            spr = enemigo["sprataq"][enemigo["dir"]][enemigo["fraataq"]]
        else:
            spr = enemigo["sprs"][enemigo["dir"]][int(enemigo["frame"])]
        enemigo["hitbox"] = creahit(spr, enemigo["rect"].topleft)

def moverproy(proys, enemigos, ancho, alto, jugdatos=None):
    ahora = pygame.time.get_ticks()
    for enemigo in enemigos[:]:
        if enemigo["vida"] <= 0 and ahora >= enemigo["golpe_hasta"]:
            enemigos.remove(enemigo)
            if jugdatos is not None:
                oleada_actual = jugdatos.get("oleada_info", {}).get("numero", 1)
                pts = round(enemigo.get("puntos", 10) * (1 + 0.1 * (oleada_actual - 1)))
                jugdatos["puntos"] = jugdatos.get("puntos", 0) + pts
                jugdatos["kills"] = jugdatos.get("kills", 0) + 1
                generar_drops_enemigo(jugdatos, enemigo)
                agregar_chispas(jugdatos, enemigo["rect"].centerx, enemigo["rect"].centery, (230, 60, 60), cantidad=12, fuerza=5.5)

    for proy in proys[:]:
        if proy.get("lado") == "pistola":
            anterior = proy["rect"].center
            velocidad = math.hypot(proy["dx"], proy["dy"])
            restante = max(0, proy["alcance"] - proy["recorrido"])
            paso = min(velocidad, restante)
            if paso >= restante:
                proy["rect"].move_ip(round(proy["dx"]), round(proy["dy"]))
            else:
                movx = round(proy["dx"] / velocidad * paso)
                movy = round(proy["dy"] / velocidad * paso)
                proy["rect"].move_ip(movx, movy)
            movx = proy["rect"].centerx - anterior[0]
            movy = proy["rect"].centery - anterior[1]
            proy["recorrido"] = min(proy["alcance"], proy["recorrido"] + math.hypot(movx, movy))
            actual = proy["rect"].center
            ux = proy["dx"] / velocidad if velocidad > 0 else 0
            uy = proy["dy"] / velocidad if velocidad > 0 else 0
            for enemigo in enemigos:
                if enemigo["vida"] > 0 and (enemigo["hitbox"].clipline(anterior, actual) or enemigo["hitbox"].colliderect(proy["rect"])):
                    danar_enemigo(enemigo, DANO_BALA, empuje_x=ux * 11.0, empuje_y=uy * 11.0, jugdatos=jugdatos)
                    proys.remove(proy)
                    break
            if proy not in proys:
                continue
            if proy["recorrido"] >= proy["alcance"] or not pygame.Rect(-40, -40, ancho + 80, alto + 80).colliderect(proy["rect"]):
                proys.remove(proy)
            continue

        paso = min(abs(proy["dx"] or proy["dy"]), proy["alcance"] - proy["recorrido"])
        movx = paso if proy["dx"] > 0 else -paso if proy["dx"] < 0 else 0
        movy = paso if proy["dy"] > 0 else -paso if proy["dy"] < 0 else 0
        proy["rect"].move_ip(movx, movy)
        proy["recorrido"] += paso
        if proy.get("lado") == "enemigo":
            if jugdatos is not None and proy["rect"].colliderect(jugdatos["hitbox"]):
                if ahora - jugdatos["ultimo_daño"] >= 900:
                    aplicar_daño_jugador(jugdatos, ahora, cantidad=proy.get("dano", 0.5), origen=proy.get("origen"), ancho_mapa=ancho, alto_mapa=alto)
                proys.remove(proy)
                continue
        else:
            vx = 1 if proy["dx"] > 0 else (-1 if proy["dx"] < 0 else 0)
            vy = 1 if proy["dy"] > 0 else (-1 if proy["dy"] < 0 else 0)
            for enemigo in enemigos:
                if enemigo["vida"] <= 0:
                    continue
                idene = id(enemigo)
                if idene not in proy["tocados"] and proy["rect"].colliderect(enemigo["hitbox"]):
                    proy["tocados"].add(idene)
                    danar_enemigo(enemigo, DANO_PUNO, empuje_x=vx * 14.0, empuje_y=vy * 14.0, jugdatos=jugdatos)
        if proy["recorrido"] >= proy["alcance"] or not pygame.Rect(0, 0, ancho, alto).colliderect(proy["rect"]):
            proys.remove(proy)

def bderrota(ancho, alto):
    ruta = "F/minecraft.ttf" if os.path.exists("F/minecraft.ttf") else "minecraft.ttf"
    fuentetitulo = pygame.font.Font(ruta, int(alto * 0.065))
    fuente = pygame.font.Font(ruta, int(alto * 0.038))
    anchopanel = int(ancho * 0.32)
    anchoboton = int(anchopanel * 0.78 * 1.5)
    altoboton = int(alto * 0.08 * 1.5)
    xboton = (ancho - anchoboton) // 2
    return fuentetitulo, fuente, [
        {"texto": "VOLVER A JUGAR", "rect": pygame.Rect(xboton, int(alto * 0.52), anchoboton, altoboton), "accion": "jugar"},
        {"texto": "MENU", "rect": pygame.Rect(xboton, int(alto * 0.68), anchoboton, altoboton), "accion": "menu"}
    ]

def dibujarperdida(pantalla, jugdatos, mapagraf, fuentetitulo, fuente, botones, mouse, camara=(0, 0)):
    dibujarjuego(pantalla, mapagraf, jugdatos, [], [], False, camara=camara)

    capa = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
    capa.fill((180, 0, 0, 77))
    pantalla.blit(capa, (0, 0))

    titulo = grosor(fuentetitulo, "PERDISTE,", (255, 255, 255), 2)
    subtitulo = grosor(fuentetitulo, "ALTO BOT", (255, 255, 255), 2)
    pantalla.blit(titulo, titulo.get_rect(center=(pantalla.get_width() // 2, int(pantalla.get_height() * 0.20))))
    pantalla.blit(subtitulo, subtitulo.get_rect(center=(pantalla.get_width() // 2, int(pantalla.get_height() * 0.32))))

    for boton in botones:
        activo = boton["rect"].collidepoint(mouse)
        colorf = (95, 95, 95) if activo else (75, 75, 75)
        colorb = (130, 130, 130) if activo else (45, 45, 45)
        pygame.draw.rect(pantalla, colorf, boton["rect"], border_radius=6)
        pygame.draw.rect(pantalla, colorb, boton["rect"], width=3, border_radius=6)
        texto = fuente.render(boton["texto"], True, (255, 255, 255))
        pantalla.blit(texto, texto.get_rect(center=boton["rect"].center))

def capas(ancho, alto, anchopanel):
    panelizq = pygame.Surface((anchopanel, alto))
    panelizq.fill((0, 0, 0))
    panelizq.set_alpha(170)

    panelder = pygame.Surface((ancho - anchopanel, alto))
    panelder.fill((0, 0, 0))
    panelder.set_alpha(128)

    return panelizq, panelder

def fuentes(alto):
    ruta = "F/minecraft.ttf" if os.path.exists("F/minecraft.ttf") else "minecraft.ttf"
    fuentetit = pygame.font.Font(ruta, int(alto * 0.065))
    fuentebtn = pygame.font.Font(ruta, int(alto * 0.038))
    return fuentetit, fuentebtn

def grosor(fuente, texto, color, g=2):
    surf = fuente.render(texto, True, color)
    wt, ht = surf.get_size()
    surfg = pygame.Surface((wt + g * 2, ht + g * 2), pygame.SRCALPHA)
    for dx in range(-g, g + 1):
        for dy in range(-g, g + 1):
            surfg.blit(surf, (dx + g, dy + g))
    return surfg

def titulos(fuentetit, anchopanel, alto):
    t1 = grosor(fuentetit, "La Matanza,", (255, 255, 255), 2)
    t2 = grosor(fuentetit, "Avanza", (255, 255, 255), 2)
    rect1 = t1.get_rect(center=(anchopanel // 2, int(alto * 0.12)))
    rect2 = t2.get_rect(center=(anchopanel // 2, int(alto * 0.20)))
    return t1, t2, rect1, rect2

def btnlista(anchopanel, alto):
    anchobtn = int(anchopanel * 0.78)
    altobtn = int(alto * 0.08)
    posx = (anchopanel - anchobtn) // 2
    posy = int(alto * 0.36)
    espacio = int(alto * 0.12)

    return [
        {"texto": "JUGAR", "rect": pygame.Rect(posx, posy, anchobtn, altobtn), "accion": "jugar"},
        {"texto": "VENTANA", "rect": pygame.Rect(posx, posy + espacio, anchobtn, altobtn), "accion": "ventana"},
        {"texto": "REINICIAR", "rect": pygame.Rect(posx, posy + espacio * 2, anchobtn, altobtn), "accion": "reiniciar"},
        {"texto": "SALIR", "rect": pygame.Rect(posx, posy + espacio * 3, anchobtn, altobtn), "accion": "salir"}
    ]

def modopant(ancho, alto, ventana):
    if ventana.get_flags() & pygame.FULLSCREEN:
        return pygame.display.set_mode((int(ancho * 0.8), int(alto * 0.8)), pygame.RESIZABLE)
    return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

def framevideo(video, ancho, alto):
    exito, frame = video.read()
    if not exito:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        exito, frame = video.read()

    if exito:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (ancho, alto))
        return pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    return None

def dibujar(pantalla, fondosurf, panelizq, panelder, anchopanel, t1, t2, rect1, rect2, botones, fuentebtn, mouse):
    if fondosurf:
        pantalla.blit(fondosurf, (0, 0))

    pantalla.blit(panelizq, (0, 0))
    pantalla.blit(panelder, (anchopanel, 0))

    pantalla.blit(t1, rect1)
    pantalla.blit(t2, rect2)

    for b in botones:
        activo = b["rect"].collidepoint(mouse)
        colorf = (95, 95, 95) if activo else (75, 75, 75)
        colorb = (130, 130, 130) if activo else (45, 45, 45)

        pygame.draw.rect(pantalla, colorf, b["rect"], border_radius=6)
        pygame.draw.rect(pantalla, colorb, b["rect"], width=3, border_radius=6)

        txtsurf = fuentebtn.render(b["texto"], True, (255, 255, 255))
        txtrect = txtsurf.get_rect(center=b["rect"].center)
        pantalla.blit(txtsurf, txtrect)

def cargarmapa(ancho, alto):
    ruta = "Sprites/mapa1n.jpeg" if os.path.exists("Sprites/mapa1n.jpeg") else ("F/Mapa.png" if os.path.exists("F/Mapa.png") else "Mapa.png")
    img = pygame.image.load(ruta)
    return pygame.transform.scale(img, (ancho, alto)).convert()

def cargabazar(ancho, alto):
    imagenes = []
    for nombre in ("andy00", "andy01", "andy02", "andy03"):
        ruta = f"Sprites/Andy/{nombre}.png"
        if not os.path.exists(ruta):
            ruta = f"{nombre}.png"
        imagen = pygame.image.load(ruta).convert()
        imagenes.append(pygame.transform.scale(imagen, (ancho, alto)))
    return imagenes

def cargarmira(alto):
    imagen = pygame.image.load("Sprites/Botones/mira.png").convert_alpha()
    for y in range(imagen.get_height()):
        for x in range(imagen.get_width()):
            pixel = imagen.get_at((x, y))
            if pixel.a:
                imagen.set_at((x, y), (255, 255, 255, pixel.a))
    tamano = max(32, int(alto * 0.055))
    return pygame.transform.scale(imagen, (tamano, tamano))

def cargariconosrecursos(alto):
    iconos = {}
    tamano = max(28, int(alto * 0.045))
    for nombre in ("pancho", "peso"):
        imagen = pygame.image.load(f"Sprites/Botones/{nombre}.png").convert_alpha()
        escala = tamano / imagen.get_height()
        dimensiones = (int(imagen.get_width() * escala), tamano)
        iconos[nombre] = pygame.transform.smoothscale(imagen, dimensiones)

    ruta_speed = "Sprites/speed.png" if os.path.exists("Sprites/speed.png") else "speed.png"
    img_speed = _recortar_fondo_claro(ruta_speed)
    escala_speed = tamano / img_speed.get_height()
    dim_speed = (max(12, int(img_speed.get_width() * escala_speed)), tamano)
    iconos["speed"] = pygame.transform.smoothscale(img_speed, dim_speed)
    iconos["speed_full"] = img_speed
    return iconos

def dibujarrecursos(pantalla, iconos, pesos, panchos, balas=None, balas_maximas=0, speeds=0):
    alto = pantalla.get_height()
    tamfuente = max(24, int(alto * 0.035))
    if tamfuente not in _fuentes_recursos:
        _fuentes_recursos[tamfuente] = pygame.font.Font(None, tamfuente)
    fuente = _fuentes_recursos[tamfuente]
    texto_speeds = fuente.render(str(speeds), True, (255, 255, 255))
    texto_panchos = fuente.render(str(panchos), True, (255, 255, 255))
    texto_pesos = fuente.render(str(pesos), True, (255, 255, 255))
    texto_balas = fuente.render(f"Balas: {balas}/{balas_maximas}" if balas is not None else "Balas: --", True, (255, 255, 255))
    margen = max(12, int(alto * 0.02))
    espacio = max(6, int(alto * 0.01))
    derecha = pantalla.get_width() - margen

    rect_texto_speeds = texto_speeds.get_rect(midright=(derecha, margen + iconos["pancho"].get_height() // 2))
    rect_speed = iconos["speed"].get_rect(midright=(rect_texto_speeds.left - espacio, rect_texto_speeds.centery))
    rect_texto_panchos = texto_panchos.get_rect(midright=(rect_speed.left - espacio * 2, rect_speed.centery))
    rect_pancho = iconos["pancho"].get_rect(midright=(rect_texto_panchos.left - espacio, rect_texto_panchos.centery))
    rect_texto_pesos = texto_pesos.get_rect(midright=(rect_pancho.left - espacio * 2, rect_pancho.centery))
    rect_peso = iconos["peso"].get_rect(midright=(rect_texto_pesos.left - espacio, rect_texto_pesos.centery))
    rect_balas = texto_balas.get_rect(midright=(rect_peso.left - espacio * 2, rect_peso.centery))
    fondo = pygame.Rect(rect_balas.left - espacio, margen // 2, derecha - rect_balas.left + espacio * 2, iconos["pancho"].get_height() + margen)
    pygame.draw.rect(pantalla, (0, 0, 0, 170), fondo, border_radius=5)
    pantalla.blit(texto_balas, rect_balas)
    pantalla.blit(iconos["peso"], rect_peso)
    pantalla.blit(texto_pesos, rect_texto_pesos)
    pantalla.blit(iconos["pancho"], rect_pancho)
    pantalla.blit(texto_panchos, rect_texto_panchos)
    pantalla.blit(iconos["speed"], rect_speed)
    pantalla.blit(texto_speeds, rect_texto_speeds)
    # Expandir levemente las áreas clicables para incluir el icono y su número
    area_pancho = rect_pancho.union(rect_texto_panchos).inflate(6, 6)
    area_speed = rect_speed.union(rect_texto_speeds).inflate(6, 6)
    return area_pancho, area_speed

def dibujaroleada(pantalla, oleada, enemigos=None, jugdatos=None):
    alto = pantalla.get_height()
    ancho = pantalla.get_width()
    tamfuente = max(28, int(alto * 0.045))
    tamchica = max(20, int(alto * 0.028))
    if tamfuente not in _fuentes_recursos:
        _fuentes_recursos[tamfuente] = pygame.font.Font(None, tamfuente)
    if tamchica not in _fuentes_recursos:
        _fuentes_recursos[tamchica] = pygame.font.Font(None, tamchica)
    fuente = _fuentes_recursos[tamfuente]
    fuente_chica = _fuentes_recursos[tamchica]

    margen = max(12, int(alto * 0.02))
    info = jugdatos.get("oleada_info") if jugdatos else None
    en_cola = len(info["cola"]) if info else 0
    vivos = len([e for e in (enemigos or []) if e.get("vida", 0) > 0])
    restantes = en_cola + vivos
    puntos = jugdatos.get("puntos", 0) if jugdatos else 0

    texto = fuente.render(f"Oleada {oleada}", True, (255, 255, 255))
    sub_txt = f"Restantes: {restantes}  |  Puntos: {puntos}" if enemigos is not None else f"Puntos: {puntos}"
    sub = fuente_chica.render(sub_txt, True, (215, 215, 215))

    rect_t = texto.get_rect(topleft=(margen * 2, margen))
    rect_s = sub.get_rect(topleft=(margen * 2, rect_t.bottom + 2))
    fondo = rect_t.union(rect_s).inflate(margen * 2, margen)
    pygame.draw.rect(pantalla, (0, 0, 0, 175), fondo, border_radius=6)
    pantalla.blit(texto, rect_t)
    pantalla.blit(sub, rect_s)

    # Banner central de oleada / jefe / victoria de oleada
    banner = jugdatos.get("banner") if jugdatos else None
    if banner:
        ahora = pygame.time.get_ticks()
        trans = ahora - banner["inicio"]
        dur = max(1, banner["dur"])
        if 0 <= trans < dur:
            tam_banner = max(48, int(alto * 0.085))
            if tam_banner not in _fuentes_recursos:
                _fuentes_recursos[tam_banner] = pygame.font.Font(None, tam_banner)
            f_ban = _fuentes_recursos[tam_banner]
            alfa = max(0.0, min(1.0, trans / 280.0, (dur - trans) / 450.0))
            img_b = f_ban.render(banner["texto"], True, (255, 215, 60))
            sombra_b = f_ban.render(banner["texto"], True, (0, 0, 0))
            img_b.set_alpha(int(255 * alfa))
            sombra_b.set_alpha(int(255 * alfa))
            rect_b = img_b.get_rect(center=(ancho // 2, int(alto * 0.24)))
            pantalla.blit(sombra_b, rect_b.move(3, 3))
            pantalla.blit(img_b, rect_b)
            if banner.get("sub"):
                img_sub = fuente.render(banner["sub"], True, (255, 255, 255))
                sombra_sub = fuente.render(banner["sub"], True, (0, 0, 0))
                img_sub.set_alpha(int(255 * alfa))
                sombra_sub.set_alpha(int(255 * alfa))
                rect_sb = img_sub.get_rect(center=(ancho // 2, int(alto * 0.31)))
                pantalla.blit(sombra_sub, rect_sb.move(2, 2))
                pantalla.blit(img_sub, rect_sb)

def cargarsprites(wjug, hjug):
    dic = {
        "abajo": [0, 1, 2],
        "arriba": [4, 5, 6],
        "derecha": [12, 13, 14],
        "izquierda": [8, 9, 10]
    }
    sprs = {}
    for d, numsf in dic.items():
        sprs[d] = []
        for n in numsf:
            img = pygame.image.load(f"sprites/Mc/MC{n:03d}.png").convert_alpha()
            img = pygame.transform.scale(img, (wjug, hjug))
            sprs[d].append(img)
    return sprs

def cargarsprataq(wjug, hjug):
    dic = {
        "abajo": [0, 1, 2, 3],
        "arriba": [4, 5, 6, 7],
        "izquierda": [8, 9, 10, 11],
        "derecha": [12, 13, 14, 15]
    }
    sprs = {}
    for d, numsf in dic.items():
        sprs[d] = []
        for n in numsf:
            img = pygame.image.load(f"Sprites/Mc/Ataque_Mc/AMC{n:03d}.png").convert_alpha()
            img = pygame.transform.scale(img, (wjug, hjug))
            sprs[d].append(img)
    return sprs

def cargarsprdash(hjug):
    derecha = []
    izquierda = []
    for i in range(8):
        ruta = f"Sprites/Mc/Dash_Normal/dash_{i:02d}.png"
        img = pygame.image.load(ruta).convert_alpha()
        caja = img.get_bounding_rect()
        recorte = img.subsurface(caja).copy()
        escala = hjug / max(1, recorte.get_height())
        w_d = max(12, int(recorte.get_width() * escala))
        spr_d = pygame.transform.scale(recorte, (w_d, hjug))
        derecha.append(spr_d)
        izquierda.append(pygame.transform.flip(spr_d, True, False))
    return {"derecha": derecha, "izquierda": izquierda}

def iniciardash(jugdatos, teclas=None):
    ahora = pygame.time.get_ticks()
    if jugdatos.get("dash") or ahora < jugdatos.get("dash_cd_hasta", 0):
        return False

    dx, dy = 0, 0
    if teclas is not None:
        dx = int(teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_a] or teclas[pygame.K_LEFT])
        dy = int(teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - int(teclas[pygame.K_w] or teclas[pygame.K_UP])

    if dx == 0 and dy == 0:
        d = jugdatos.get("dir", "abajo")
        if d == "derecha":
            dx = 1
        elif d == "izquierda":
            dx = -1
        elif d == "arriba":
            dy = -1
        else:
            dy = 1

    mag = math.hypot(dx, dy)
    ux, uy = (dx / mag, dy / mag) if mag > 0 else (1.0, 0.0)
    if ux != 0:
        jugdatos["lado_x"] = 1 if ux > 0 else -1

    dur_ms = 230
    cd_ms = 950
    jugdatos["ataq"] = False
    jugdatos["dash"] = True
    jugdatos["dash_inicio"] = ahora
    jugdatos["dash_hasta"] = ahora + dur_ms
    jugdatos["dash_dur"] = dur_ms
    jugdatos["dash_cd_hasta"] = ahora + cd_ms
    jugdatos["dash_cd_dur"] = cd_ms
    jugdatos["dash_invul_hasta"] = ahora + dur_ms + 80
    jugdatos["dash_vec"] = (ux, uy)
    return True

def iniciarataq(jugdatos, destino=None, enemigos=None):
    ahora = pygame.time.get_ticks()
    if jugdatos.get("dash") or jugdatos["ataq"] or ahora < jugdatos.get("cd_golpe_hasta", 0):
        return False

    # Asistencia de apuntado cuerpo a cuerpo hacia el enemigo más cercano en rango
    cercano = None
    mejor_dist = jugdatos["rect"].height * 2.1
    if enemigos:
        jx, jy = jugdatos["hitbox"].center
        for e in enemigos:
            if e.get("vida", 0) <= 0:
                continue
            d = math.hypot(e["hitbox"].centerx - jx, e["hitbox"].centery - jy)
            if d < mejor_dist:
                mejor_dist = d
                cercano = e

    if cercano is not None:
        dx = cercano["hitbox"].centerx - jugdatos["hitbox"].centerx
        dy = cercano["hitbox"].centery - jugdatos["hitbox"].centery
        if abs(dx) >= abs(dy):
            jugdatos["dir"] = "derecha" if dx > 0 else "izquierda"
        else:
            jugdatos["dir"] = "abajo" if dy > 0 else "arriba"
        if dx != 0:
            jugdatos["lado_x"] = 1 if dx > 0 else -1
    elif destino is not None:
        dx = destino[0] - jugdatos["hitbox"].centerx
        dy = destino[1] - jugdatos["hitbox"].centery
        if dx != 0 or dy != 0:
            if abs(dx) >= abs(dy):
                jugdatos["dir"] = "derecha" if dx > 0 else "izquierda"
            else:
                jugdatos["dir"] = "abajo" if dy > 0 else "arriba"
            if dx != 0:
                jugdatos["lado_x"] = 1 if dx > 0 else -1

    jugdatos["ataq"] = True
    jugdatos["dirataq"] = jugdatos["dir"]
    jugdatos["fraataq"] = 0
    jugdatos["ultfraataq"] = ahora
    return True

def actualizarataq(jugdatos):
    ahora = pygame.time.get_ticks()
    if jugdatos.get("dash") and ahora >= jugdatos.get("dash_hasta", 0):
        jugdatos["dash"] = False

    if not jugdatos["ataq"]:
        return

    if ahora - jugdatos["ultfraataq"] < 85:
        return

    jugdatos["fraataq"] += 1
    jugdatos["ultfraataq"] = ahora
    if jugdatos["fraataq"] >= len(jugdatos["sprataq"][jugdatos["dirataq"]]):
        jugdatos["ataq"] = False
        jugdatos["fraataq"] = 0
        jugdatos["cd_golpe_hasta"] = ahora + 110

def crearjugador(ancho, alto):
    # Escala para mapa 1 (Bazar, ciudad: 10% más chico que antes)
    hjug1 = int(alto * 0.1125)
    wjug1 = int(hjug1 * (52 / 96))
    xjug = ancho // 2
    yjug = int(alto * 0.50)
    rectjug = pygame.Rect(xjug, yjug, wjug1, hjug1)
    vel1 = int(alto * 0.0085)

    sprs1 = cargarsprites(wjug1, hjug1)
    sprataq1 = cargarsprataq(wjug1, hjug1)
    sprdash1 = cargarsprdash(hjug1)
    sprrojos1 = {d: [rojospr(spr) for spr in lista] for d, lista in sprs1.items()}
    sprataqrojos1 = {d: [rojospr(spr) for spr in lista] for d, lista in sprataq1.items()}

    # Escala reducida para mapa 2 (zona de oleadas grande con mayor zoom)
    hjug2 = int(alto * 0.075)
    wjug2 = int(hjug2 * (52 / 96))
    vel2 = max(2, int(alto * 0.007))
    sprs2 = cargarsprites(wjug2, hjug2)
    sprataq2 = cargarsprataq(wjug2, hjug2)
    sprdash2 = cargarsprdash(hjug2)
    sprrojos2 = {d: [rojospr(spr) for spr in lista] for d, lista in sprs2.items()}
    sprataqrojos2 = {d: [rojospr(spr) for spr in lista] for d, lista in sprataq2.items()}

    hitbox = creahit(sprs1["abajo"][0], rectjug.topleft)

    jugdatos = {
        "rect": rectjug,
        "hitbox": hitbox,
        "vel": vel1,
        "sprs": sprs1,
        "sprrojos": sprrojos1,
        "sprataq": sprataq1,
        "sprataqrojos": sprataqrojos1,
        "sprdash": sprdash1,
        "_escalas": {
            1: {"w": wjug1, "h": hjug1, "vel": vel1, "sprs": sprs1, "sprrojos": sprrojos1, "sprataq": sprataq1, "sprataqrojos": sprataqrojos1, "sprdash": sprdash1},
            2: {"w": wjug2, "h": hjug2, "vel": vel2, "sprs": sprs2, "sprrojos": sprrojos2, "sprataq": sprataq2, "sprataqrojos": sprataqrojos2, "sprdash": sprdash2},
        },
        "mapa_escala": 1,
        "dir": "abajo",
        "lado_x": 1,
        "frame": 1.0,
        "ataq": False,
        "dirataq": "abajo",
        "fraataq": 0,
        "ultfraataq": 0,
        "cd_golpe_hasta": 0,
        "cd_disparo_hasta": 0,
        "dash": False,
        "dash_inicio": 0,
        "dash_hasta": 0,
        "dash_dur": 230,
        "dash_cd_hasta": 0,
        "dash_cd_dur": 950,
        "dash_invul_hasta": 0,
        "dash_vec": (1.0, 0.0),
        "vida": 5,
        "escudo": 0,
        "dano_acumulado": 0.0,
        "pesos": 0,
        "pistola": False,
        "panchos_extra": 0,
        "balas_extra": 0,
        "puntos": 0,
        "kills": 0,
        "ultimo_daño": -1000,
        "golpe_hasta": 0,
        "shake_hasta": 0,
        "drops": [],
        "chispas": [],
        "textos": [],
        "banner": None,
        "oleada_info": None,
    }
    return jugdatos

def cambiar_escala_jugador(jugdatos, ancho, alto, mapa=1):
    id_mapa = 2 if mapa == 2 else 1
    if jugdatos.get("mapa_escala") == id_mapa:
        return
    esc = jugdatos["_escalas"][id_mapa]
    centro = jugdatos["rect"].center
    jugdatos["rect"].size = (esc["w"], esc["h"])
    jugdatos["rect"].center = centro
    jugdatos["vel"] = esc["vel"]
    jugdatos["sprs"] = esc["sprs"]
    jugdatos["sprrojos"] = esc["sprrojos"]
    jugdatos["sprataq"] = esc["sprataq"]
    jugdatos["sprataqrojos"] = esc["sprataqrojos"]
    jugdatos["sprdash"] = esc["sprdash"]
    jugdatos["mapa_escala"] = id_mapa

    spr = jugdatos["sprs"][jugdatos["dir"]][0]
    jugdatos["hitbox"] = creahit(spr, jugdatos["rect"].topleft)

def moverjugador(jugdatos, teclas, ancho, alto, mapa=1, obstaculos=None):
    ahora = pygame.time.get_ticks()
    if isinstance(mapa, (tuple, list)):
        mapa = 2 if (ancho > 2000 or alto > 1200 or mapa == (0.29, 0.72)) else 1

    if obstaculos is None:
        obstaculos = obtener_obstaculos(mapa, ancho, alto)

    rect = jugdatos["rect"]
    vel = jugdatos["vel"]
    mov = False
    dx = 0
    dy = 0

    if jugdatos.get("dash") and ahora < jugdatos.get("dash_hasta", 0):
        ux, uy = jugdatos.get("dash_vec", (1.0, 0.0))
        vel_dash = max(vel * 2.6, 8)
        dx = round(ux * vel_dash)
        dy = round(uy * vel_dash)
        mov = True
    else:
        jugdatos["dash"] = False
        vel_actual = max(1, int(vel * 0.35)) if jugdatos["ataq"] else vel

        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dy -= vel_actual
            if not jugdatos["ataq"]:
                jugdatos["dir"] = "arriba"
            mov = True
        elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dy += vel_actual
            if not jugdatos["ataq"]:
                jugdatos["dir"] = "abajo"
            mov = True

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            dx -= vel_actual
            if not jugdatos["ataq"]:
                jugdatos["dir"] = "izquierda"
            jugdatos["lado_x"] = -1
            mov = True
        elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            dx += vel_actual
            if not jugdatos["ataq"]:
                jugdatos["dir"] = "derecha"
            jugdatos["lado_x"] = 1
            mov = True

    # Movimiento en eje X con colisiones y deslizamiento pixel-perfect
    if dx != 0:
        paso_x = 1 if dx > 0 else -1
        for _ in range(abs(dx)):
            rect.x += paso_x
            if rect.left < 0:
                rect.left = 0
                break
            if rect.right > ancho:
                rect.right = ancho
                break
            pies = colision_pies(rect)
            if any(pies.colliderect(obs) for obs in obstaculos):
                rect.x -= paso_x
                break

    # Movimiento en eje Y con colisiones y deslizamiento pixel-perfect
    if dy != 0:
        paso_y = 1 if dy > 0 else -1
        for _ in range(abs(dy)):
            rect.y += paso_y
            if rect.top < 0:
                rect.top = 0
                break
            if rect.bottom > alto:
                rect.bottom = alto
                break
            pies = colision_pies(rect)
            if any(pies.colliderect(obs) for obs in obstaculos):
                rect.y -= paso_y
                break

    if jugdatos["ataq"]:
        spr = jugdatos["sprataq"][jugdatos["dirataq"]][jugdatos["fraataq"]]
    else:
        secuencia = [0, 1, 2, 1]
        idx = secuencia[int(jugdatos["frame"]) % 4]
        spr = jugdatos["sprs"][jugdatos["dir"]][idx]
    jugdatos["hitbox"] = creahit(spr, rect.topleft)

    if mov and not jugdatos.get("dash"):
        jugdatos["frame"] = (jugdatos["frame"] + 0.15) % 4
    elif not mov:
        jugdatos["frame"] = 1.0

def dibujar_sombra_entidad(pantalla, x, y, ancho):
    ancho = max(8, int(ancho))
    sombra = _SOMBRAS.get(ancho)
    if sombra is None:
        sombra = pygame.Surface((ancho, max(5, ancho // 3)), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 90), sombra.get_rect())
        _SOMBRAS[ancho] = sombra
    pantalla.blit(sombra, (int(x - ancho / 2), int(y - sombra.get_height() / 2)))

def _obtener_iconos_drops_y_balas(alto_pantalla):
    if alto_pantalla not in _CACHE_DROPS:
        tam = max(18, int(alto_pantalla * 0.032))
        drops_ic = {}
        for nombre in ("peso", "pancho", "bala"):
            img = pygame.image.load(f"Sprites/Botones/{nombre}.png").convert_alpha()
            rec = img.subsurface(img.get_bounding_rect()).copy()
            esc = tam / max(1, rec.get_height())
            drops_ic[nombre] = pygame.transform.smoothscale(rec, (max(10, int(rec.get_width() * esc)), tam))
        drops_ic["balas"] = drops_ic["bala"]
        _CACHE_DROPS[alto_pantalla] = drops_ic

    if alto_pantalla not in _CACHE_BALAS:
        img_b = pygame.image.load("Sprites/Botones/bala.png").convert_alpha()
        rec_b = img_b.subsurface(img_b.get_bounding_rect()).copy()
        tam_b = max(16, int(alto_pantalla * 0.028))
        esc_b = tam_b / max(1, max(rec_b.get_width(), rec_b.get_height()))
        base_b = pygame.transform.smoothscale(rec_b, (max(8, int(rec_b.get_width() * esc_b)), max(8, int(rec_b.get_height() * esc_b))))
        base_b = pygame.transform.rotate(base_b, -63)
        _CACHE_BALAS[alto_pantalla] = {i: pygame.transform.rotate(base_b, i * 5) for i in range(72)}

    return _CACHE_DROPS[alto_pantalla], _CACHE_BALAS[alto_pantalla]

def dibujarjuego(pantalla, mapagraf, jugdatos, vidas, objetivos, mostrarvida=True, proys=None, camara=(0, 0), escudos=None):
    ahora = pygame.time.get_ticks()
    alto_pant = pantalla.get_height()
    cx, cy = camara
    if ahora < jugdatos.get("shake_hasta", 0):
        cx += random.randint(-5, 5)
        cy += random.randint(-5, 5)

    pantalla.blit(mapagraf, (-cx, -cy))
    iconos_drops, balas_rot = _obtener_iconos_drops_y_balas(alto_pant)

    # Dibujar drops en el suelo con sombra y rebote
    for d in jugdatos.get("drops", []):
        edad = ahora - d["inicio"]
        restante = d["vida_ms"] - edad
        if restante < 2500 and (ahora // 100) % 2 == 0:
            continue
        ic = iconos_drops.get(d["tipo"], iconos_drops["peso"])
        rebote = math.sin(edad * 0.006) * 3.5
        dx_p = int(d["x"] - cx)
        dy_p = int(d["y"] - cy)
        dibujar_sombra_entidad(pantalla, dx_p, dy_p, ic.get_width() * 0.9)
        pantalla.blit(ic, ic.get_rect(midbottom=(dx_p, int(dy_p - 4 + rebote))))

    # Ordenar entidades por profundidad (Y-sorting por la base de los pies)
    entidades = [(jugdatos["rect"].bottom, "jugador", jugdatos)]
    for obj in objetivos:
        if isinstance(obj, dict):
            entidades.append((obj["rect"].bottom, "enemigo", obj))
        else:
            entidades.append((obj.bottom, "rect", obj))
    entidades.sort(key=lambda item: item[0])

    tam_txt = max(18, int(alto_pant * 0.025))
    if tam_txt not in _fuentes_recursos:
        _fuentes_recursos[tam_txt] = pygame.font.Font(None, tam_txt)
    fuente_ent = _fuentes_recursos[tam_txt]

    for _, tipo_ent, obj in entidades:
        if tipo_ent == "rect":
            rect_dibujo = obj.move(-cx, -cy)
            pygame.draw.rect(pantalla, (120, 55, 35), rect_dibujo, border_radius=6)
        elif tipo_ent == "enemigo":
            dibujar_sombra_entidad(pantalla, obj["rect"].centerx - cx, obj["rect"].bottom - cy, obj["rect"].width * 0.85)
            if obj["ataq"]:
                spr = obj["sprataq"][obj["dir"]][obj["fraataq"]]
                if ahora < obj["golpe_hasta"]:
                    spr = obj["sprataqrojos"][obj["dir"]][obj["fraataq"]]
            else:
                spr = obj["sprs"][obj["dir"]][int(obj["frame"]) % 3]
                if ahora < obj["golpe_hasta"]:
                    spr = obj["sprrojos"][obj["dir"]][int(obj["frame"]) % 3]
            rx = obj["rect"].x - cx
            ry = obj["rect"].y - cy
            pantalla.blit(spr, (rx, ry))

            # Barra de vida sobre el enemigo (si fue dañado o si es el jefe)
            v_max = obj.get("vida_max", 3)
            v_act = max(0, obj.get("vida", 0))
            es_jefe = obj.get("tipo") == "jefe"
            if (v_act < v_max or es_jefe) and v_act > 0:
                ancho_b = max(28, int(obj["rect"].width * 0.95))
                barra = pygame.Rect(int(obj["rect"].centerx - cx - ancho_b // 2), int(ry - 9), ancho_b, 5)
                pygame.draw.rect(pantalla, (40, 0, 0), barra)
                relleno = barra.copy()
                relleno.width = max(0, int(ancho_b * (v_act / max(1, v_max))))
                pygame.draw.rect(pantalla, (230, 60, 60), relleno)
                pygame.draw.rect(pantalla, (0, 0, 0), barra, 1)
                if es_jefe:
                    lbl_j = fuente_ent.render("EL JEFE", True, (255, 215, 60))
                    sombra_j = fuente_ent.render("EL JEFE", True, (0, 0, 0))
                    rj = lbl_j.get_rect(midbottom=(barra.centerx, barra.top - 2))
                    pantalla.blit(sombra_j, rj.move(1, 1))
                    pantalla.blit(lbl_j, rj)
        elif tipo_ent == "jugador":
            dibujar_sombra_entidad(pantalla, obj["rect"].centerx - cx, obj["rect"].bottom - cy, obj["rect"].width * 0.85)
            if obj.get("dash") and ahora < obj.get("dash_hasta", 0) and "sprdash" in obj:
                lado_d = "derecha" if obj.get("lado_x", 1) >= 0 else "izquierda"
                progreso_d = (ahora - obj.get("dash_inicio", ahora)) / max(1, obj.get("dash_dur", 230))
                idx_d = max(0, min(7, int(progreso_d * 8)))
                spr_j = obj["sprdash"][lado_d][idx_d]
                rj = spr_j.get_rect(midbottom=(obj["rect"].centerx - cx, obj["rect"].bottom - cy))
                pantalla.blit(spr_j, rj)
            else:
                if obj["ataq"]:
                    if ahora < obj["golpe_hasta"]:
                        spr_j = obj["sprataqrojos"][obj["dirataq"]][obj["fraataq"]]
                    else:
                        spr_j = obj["sprataq"][obj["dirataq"]][obj["fraataq"]]
                else:
                    d = obj["dir"]
                    secuencia = [0, 1, 2, 1]
                    idx = secuencia[int(obj["frame"]) % 4]
                    if ahora < obj["golpe_hasta"]:
                        spr_j = obj["sprrojos"][d][idx]
                    else:
                        spr_j = obj["sprs"][d][idx]
                pantalla.blit(spr_j, (obj["rect"].x - cx, obj["rect"].y - cy))

    # Dibujar proyectiles / balas rotadas
    for proy in proys or []:
        if proy.get("invisible"):
            continue
        rect_proy = proy["rect"].move(-cx, -cy)
        if proy.get("lado") == "pistola" and "angulo" in proy:
            spr_bala = balas_rot[round(proy["angulo"] / 5) % 72]
            pantalla.blit(spr_bala, spr_bala.get_rect(center=rect_proy.center))
        else:
            color = (255, 230, 90) if proy.get("lado") == "pistola" else (235, 85, 75) if proy.get("lado") == "enemigo" else (250, 250, 150)
            pygame.draw.ellipse(pantalla, color, rect_proy)
            pygame.draw.ellipse(pantalla, (35, 30, 20), rect_proy, 1)

    # Dibujar chispas de impacto
    for c in jugdatos.get("chispas", []):
        pygame.draw.circle(pantalla, c["color"], (int(c["x"] - cx), int(c["y"] - cy)), c["radio"])

    # Dibujar textos flotantes (-daño, +$pesos, +vida, etc.)
    for t in jugdatos.get("textos", []):
        img_t = fuente_ent.render(t["texto"], True, t["color"])
        sombra_t = fuente_ent.render(t["texto"], True, (0, 0, 0))
        rt = img_t.get_rect(midbottom=(int(t["x"] - cx), int(t["y"] - cy)))
        pantalla.blit(sombra_t, rt.move(1, 1))
        pantalla.blit(img_t, rt)

    if mostrarvida:
        dibujarvida(pantalla, vidas, jugdatos, escudos=escudos)
