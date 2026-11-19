import pygame
import cv2
import os
import math
import random
import numpy as np
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    os.chdir(BASE_DIR)
except OSError:
    pass

_SOMBRAS = {}
_CSPRS_ENE = {}
_CDROPS = {}
_CBALAS = {}
_CMAPAS = {}
_COBS = {}
_CESCJUG = {}
_CMIRA = {}
_CRECTALP = {}
_CMOL_LANZ = {}
_CFUEGO = {}
_MOLBASE = None
_FUEGOBASE = None
_PIEDRA = None
_CARGPIED = False

def dibrectalp(pant, col_rgba, rect, border_radius=0, radius=None):
    if radius is not None:
        border_radius = radius
    if rect.width <= 0 or rect.height <= 0:
        return
    k = (rect.width, rect.height, tuple(col_rgba), border_radius)
    surf = _CRECTALP.get(k)
    if surf is None:
        surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, col_rgba, surf.get_rect(), border_radius=border_radius)
        if len(_CRECTALP) > 128:
            _CRECTALP.clear()
        _CRECTALP[k] = surf
    pant.blit(surf, rect.topleft)

RUTA_TTF = os.path.join(BASE_DIR, "F", "minecraft.ttf")
if not os.path.exists(RUTA_TTF):
    RUTA_TTF = os.path.join(BASE_DIR, "minecraft.ttf")
_FUENTES = {}
_REEMPL = {"→": ">"}

class Fuente(pygame.font.Font):
    # Fuente Minecraft: unico punto de render. Sin antialias y con texto limpiado
    # (los glifos que la TTF no tiene se reemplazan por su version sin acento).
    def __init__(self, tam):
        super().__init__(RUTA_TTF, tam)
        self.tam = tam
        nd = super().metrics("\u4e2d")
        self._nd = nd[0] if nd else None
        self._ok = {}

    def soporta(self, ch):
        if ch in " \t":
            return True
        r = self._ok.get(ch)
        if r is None:
            m = super().metrics(ch)
            r = bool(m) and m[0] is not None and m[0] != self._nd
            self._ok[ch] = r
        return r

    def limpiar(self, txt):
        sal = []
        for ch in str(txt):
            if self.soporta(ch):
                sal.append(ch)
            elif ch in _REEMPL:
                sal.append(_REEMPL[ch])
            else:
                b = unicodedata.normalize("NFD", ch)[0]
                sal.append(b if self.soporta(b) else "?")
        return "".join(sal)

    def render(self, texto, antialias=False, color=(255, 255, 255), bg=None):
        s = super().render(self.limpiar(texto), False, color)
        try:
            return s.convert_alpha()
        except pygame.error:
            return s

    def size(self, texto):
        return super().size(self.limpiar(texto))

def tam_f(alt, frac, minimo=12):
    return max(minimo, int(round(alt * frac / 4.0)) * 4)

def fuente(tam):
    f = _FUENTES.get(tam)
    if f is None:
        f = _FUENTES[tam] = Fuente(tam)
    return f

def txtfit(tam, texto, col, maxw=None):
    # Renderiza con la fuente 'tam'; si no entra en maxw, baja de a 4 px.
    while True:
        s = fuente(tam).render(texto, False, col)
        if maxw is None or s.get_width() <= maxw or tam <= 8:
            return s
        tam -= 4 if tam > 12 else 2

dano_PUNO = 16
dano_BALA = 28

BAL_PIEDRA = {
    "hp": 24,
    "vel_mult": 0.95,
    "daño": 0.25,
    "esc": 1.0,
    "pts": 15,
    "pesos": (20, 35),
    "alc_m": 2.95,
    "rad_min": 0.78,
    "rad_max": 0.92,
    "esp_ms": 3350,
    "jitter_ms": 300,
    "windup_fra_ms": 230,
    "fra_lanz": 2,
    "vel_piedra_mult": 0.145,
    "vel_piedra_min": 5.2,
    "tam_piedra_mult": 0.22,
    "tam_piedra_min": 10,
    "alc_piedra_extra": 65,
    "alc_piedra_mult": 3.5,
    "emp_max": 4,
    "max_lanz_baja": 2,
    "max_lanz_alta": 3,
    "ole_lanz_alta": 10,
    "ole_min": 3,
    "max_vivos_base": 3,
    "max_vivos_div": 6,
    "max_vivos_tope": 5,
    "prob_base": 0.10,
    "prob_inc": 0.012,
    "prob_max": 0.20,
    "tope_cola_frac": 0.20,
}

BAL_MOL = {
    "cd_ms": 1500,
    "alc_mult": 6.0,
    "vuelo_ms": 450,
    "arco_alt_mult": 1.35,
    "vel_rot": 720.0,
    "tam_proy_mult": 0.55,
    "tam_proy_min": 20,
    "radio_mult": 2.2,
    "dur_ms": 4000,
    "fade_ms": 600,
    "fra_fuego_ms": 100,
    "tick_ms": 350,
    "daño_tick": 10,
    "jefe_mult": 0.5,
    "quem_dur_ms": 1500,
    "quem_daño_tick": 6,
    "quem_chispa_ms": 220,
    "max_zonas": 6,
}

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
    "barracas": {
        "hp": BAL_PIEDRA["hp"], "vel_mult": BAL_PIEDRA["vel_mult"],
        "daño": BAL_PIEDRA["daño"], "esc": BAL_PIEDRA["esc"], "tint": None,
        "pts": BAL_PIEDRA["pts"], "pesos": BAL_PIEDRA["pesos"],
        "alc_m": BAL_PIEDRA["alc_m"], "esp": BAL_PIEDRA["esp_ms"]
    },
}

PRE_PIST = 400
PRE_MOL = 120
PRE_PAN = 75
PRE_SPD = 250

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
    slot = 1
    molotovs = 0
    ruta = os.path.join("F", "Datos.txt")

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
                    elif k == "slot":
                        slot = max(1, min(3, int(v)))
                    elif k == "molotovs":
                        molotovs = max(0, int(v))
                except ValueError:
                    continue

    if vida <= 0:
        vida, esc, pts, ole, pesos, panchos, spds, pist = 5, 0, 0, 1, 0, 0, 0, False
        posmc = (anc // 2, int(alt * 0.50))
        mapa = 1
        slot, molotovs = 1, 0

    if slot == 2 and not pist:
        slot = 1

    return vida, esc, pts, ole, pesos, panchos, spds, pist, posmc, mapa, slot, molotovs

def resetguard(anc, alt):
    pos_ini = (anc // 2, int(alt * 0.50))
    guardardat(5, 0, 1, 0, 0, False, pos_ini, 1, esc=0, spds=0)
    return pos_ini

def nuevapart(anc, alt, jdat=None, bmax=10, guardar=True):
    if jdat is None:
        jdat = crearjug(anc, alt)
    escjug(jdat, anc, alt, mapa=1)
    pos_ini = (anc // 2, int(alt * 0.50))
    jdat.update({
        "dir": "abajo",
        "lado_x": 1,
        "frame": 1.0,
        "ataq": False,
        "dirataq": "abajo",
        "fraataq": 0,
        "ultfraataq": 0,
        "cd_golpe_hasta": 0,
        "cd_disp_hasta": 0,
        "cd_mol_hasta": 0,
        "cd_mol_dur": BAL_MOL["cd_ms"],
        "zonas_fuego": [],
        "dash": False,
        "dash_ini": 0,
        "dash_hasta": 0,
        "dash_cd_hasta": 0,
        "dash_invul_hasta": 0,
        "dash_vec": (1.0, 0.0),
        "vida": 5,
        "escudo": 0,
        "daño_acum": 0.0,
        "pesos": 0,
        "pistola": False,
        "panchos": 0,
        "spds": 0,
        "puntos": 0,
        "oleada": 1,
        "slot": 1,
        "molotovs": 0,
        "slot_msg": "",
        "slot_msg_hasta": 0,
        "mapa": 1,
        "balas": bmax,
        "bmax": bmax,
        "rec_hasta": 0,
        "ultdaño": -1000,
        "golpe_hasta": 0,
        "shake_hasta": 0,
        "drops": [],
        "chispas": [],
        "textos": [],
        "banner": None,
        "ole_inf": None,
    })
    ajustapos(jdat, pos_ini, anc, alt, 1)
    if guardar:
        guardardat(5, 0, 1, 0, 0, False, jdat["rect"].topleft, 1, esc=0, spds=0)
    return {
        "jdat": jdat,
        "vida": 5,
        "esc": 0,
        "pts": 0,
        "ole": 1,
        "pesos": 0,
        "panchos": 0,
        "spds": 0,
        "pist": False,
        "posmc": jdat["rect"].topleft,
        "mapa": 1,
        "balas": bmax,
        "rec_hasta": 0,
        "car_pist": 0,
        "car_mol": 0,
        "car_pan": 0,
        "car_spd": 0,
        "msg_comp": "",
        "msg_pan": "",
        "msg_pan_hasta": 0,
        "trans": {"estado": "ninguno", "inicio": 0},
        "enes": [],
        "proys": [],
    }

def guardardat(vida, pts, ole, pesos, panchos, pist, posmc, mapa, esc=0, spds=0, slot=1, molotovs=0):
    carp = "F"
    os.makedirs(carp, exist_ok=True)
    ruta = os.path.join(carp, "Datos.txt")
    ruta_tmp = os.path.join(carp, "Datos.txt.tmp")
    with open(ruta_tmp, "w", encoding="utf-8") as arch:
        arch.write(f"vida={vida}\n")
        arch.write(f"escudo={esc}\n")
        arch.write(f"puntos={pts}\n")
        arch.write(f"oleada={ole}\n")
        arch.write(f"pesos={pesos}\n")
        arch.write(f"panchos={panchos}\n")
        arch.write(f"speeds={spds}\n")
        arch.write(f"pistola={int(bool(pist))}\n")
        arch.write(f"posicion_mc={posmc[0]},{posmc[1]}\n")
        arch.write(f"mapa={mapa}\n")
        arch.write(f"slot={slot}\n")
        arch.write(f"molotovs={molotovs}\n")
    os.replace(ruta_tmp, ruta)

def guardjdat(jdat, ole=None, mapa=None):
    guardardat(
        jdat.get("vida", 5),
        jdat.get("puntos", 0),
        ole if ole is not None else jdat.get("oleada", 1),
        jdat.get("pesos", 0),
        jdat.get("panchos", 0),
        jdat.get("pistola", False),
        jdat["rect"].topleft,
        mapa if mapa is not None else jdat.get("mapa", 1),
        esc=jdat.get("escudo", 0),
        spds=jdat.get("spds", 0),
        slot=jdat.get("slot", 1),
        molotovs=jdat.get("molotovs", 0),
    )

_CBOUND = {}

def creahit(spr, pos):
    br = _CBOUND.get(spr)
    if br is None:
        if len(_CBOUND) >= 512:
            _CBOUND.clear()
        br = spr.get_bounding_rect()
        br.inflate_ip(-max(2, int(br.width * 0.25)), -max(2, int(br.height * 0.20)))
        _CBOUND[spr] = br
    return br.move(pos)

def colpies(r):
    w = max(4, int(r.width * 0.38))
    h = max(4, int(r.height * 0.16))
    return pygame.Rect(r.centerx - w // 2, r.bottom - h, w, h)

def obstaculos(mapa, anc, alt):
    m = 2 if mapa == 2 else 1
    k = (m, anc, alt)
    if k in _COBS:
        return _COBS[k]
    if m == 2:
        res = (
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
        )
    else:
        res = (
            pygame.Rect(0, 0, anc, int(alt * 0.335)),
            pygame.Rect(0, int(alt * 0.335), int(anc * 0.070), int(alt * 0.13)),
            pygame.Rect(0, int(alt * 0.56), int(anc * 0.05), int(alt * 0.44)),
            pygame.Rect(int(anc * 0.05), int(alt * 0.70), int(anc * 0.10), int(alt * 0.30)),
            pygame.Rect(int(anc * 0.15), int(alt * 0.83), int(anc * 0.275), int(alt * 0.17)),
            pygame.Rect(int(anc * 0.575), int(alt * 0.83), int(anc * 0.425), int(alt * 0.17)),
            pygame.Rect(int(anc * 0.875), int(alt * 0.56), int(anc * 0.125), int(alt * 0.27)),
        )
    _COBS[k] = res
    return res

def _resolvobs(anc, alt, obs_l=None, mapa=None, ent=None):
    if obs_l is not None:
        return obs_l
    m = mapa
    if m not in (1, 2) and isinstance(ent, dict):
        m = ent.get("mapa_esc") if ent.get("mapa_esc") in (1, 2) else ent.get("mapa")
    if m not in (1, 2):
        raise ValueError("Se requiere obs_l o un id de mapa explicito (1 o 2)")
    return obstaculos(m, anc, alt)

def _posvalida(r, anc, alt, obs_l):
    if r.left < 0 or r.top < 0 or r.right > anc or r.bottom > alt:
        return False
    return not obs_l or colpies(r).collidelist(obs_l) == -1

def _acthitent(ent):
    if not isinstance(ent, dict) or "rect" not in ent or "sprs" not in ent:
        return
    r = ent["rect"]
    d = ent.get("dir", "abajo")
    if ent.get("ataq") and "sprataq" in ent:
        da = ent.get("dirataq", d)
        lst = ent["sprataq"].get(da) or ent["sprs"][d]
        spr = lst[min(ent.get("fraataq", 0), len(lst) - 1)]
    else:
        lst = ent["sprs"][d]
        idx = int(ent.get("frame", 0)) % len(lst)
        spr = lst[idx]
    ent["hitbox"] = creahit(spr, r.topleft)

def desatascar(jdat, anc, alt, obs_l=None, mapa=None):
    r = jdat["rect"] if isinstance(jdat, dict) else jdat
    obs_l = _resolvobs(anc, alt, obs_l=obs_l, mapa=mapa, ent=jdat)

    if _posvalida(r, anc, alt, obs_l):
        if isinstance(jdat, dict):
            _acthitent(jdat)
        return False

    max_x = max(0, anc - r.width)
    max_y = max(0, alt - r.height)
    bx = max(0, min(r.x, max_x))
    by = max(0, min(r.y, max_y))
    r.topleft = (bx, by)
    if _posvalida(r, anc, alt, obs_l):
        _acthitent(jdat)
        return True

    # Candidatos directos por proyeccion ortogonal fuera de obstaculos que colisionan
    cands = []
    pies_b = colpies(r)
    off_px = pies_b.x - r.x
    off_py = pies_b.y - r.y
    pw, ph = pies_b.width, pies_b.height
    for o in obs_l:
        if pies_b.colliderect(o):
            proys_o = [
                (bx, o.top - ph - off_py),
                (bx, o.bottom - off_py),
                (o.left - pw - off_px, by),
                (o.right - off_px, by),
            ]
            for cx, cy in proys_o:
                cx = max(0, min(cx, max_x))
                cy = max(0, min(cy, max_y))
                cands.append(((cx - bx) ** 2 + (cy - by) ** 2, cx, cy))

    mejor = None
    for d2, cx, cy in sorted(cands):
        r.topleft = (cx, cy)
        if _posvalida(r, anc, alt, obs_l):
            mejor = (d2, cx, cy)
            break

    max_rad = int(math.sqrt(mejor[0])) + 2 if mejor else max(anc, alt)
    paso = 1
    rad = 1
    while rad <= max_rad:
        paso = 1 if rad <= 12 else (2 if rad <= 48 else (4 if rad <= 160 else 8))
        anillo = []
        for dx in range(-rad, rad + 1, paso):
            for dy in (-rad, rad):
                anillo.append((dx * dx + dy * dy, bx + dx, by + dy))
        for dy in range(-rad + paso, rad, paso):
            for dx in (-rad, rad):
                anillo.append((dx * dx + dy * dy, bx + dx, by + dy))
        anillo.sort(key=lambda it: it[0])
        for d2, nx, ny in anillo:
            if mejor and d2 >= mejor[0]:
                break
            if 0 <= nx <= max_x and 0 <= ny <= max_y:
                r.topleft = (nx, ny)
                if _posvalida(r, anc, alt, obs_l):
                    mejor = (d2, nx, ny)
                    max_rad = int(math.sqrt(d2)) + paso
                    break
        rad += paso

    if mejor is not None:
        r.topleft = (mejor[1], mejor[2])
        _acthitent(jdat)
        return True

    # Fallback exhaustivo en grilla por si el mapa estuviera muy congestionado
    for gy in range(0, max_y + 1, 8):
        for gx in range(0, max_x + 1, 8):
            r.topleft = (gx, gy)
            if _posvalida(r, anc, alt, obs_l):
                _acthitent(jdat)
                return True

    r.topleft = (bx, by)
    _acthitent(jdat)
    return False

def _movpaso(r, dx, dy, anc, alt, obs_l):
    ix = int(round(dx))
    iy = int(round(dy))
    if ix != 0:
        px = 1 if ix > 0 else -1
        for _ in range(abs(ix)):
            r.x += px
            if r.left < 0 or r.right > anc or (obs_l and colpies(r).collidelist(obs_l) != -1):
                r.x -= px
                break
    if iy != 0:
        py = 1 if iy > 0 else -1
        for _ in range(abs(iy)):
            r.y += py
            if r.top < 0 or r.bottom > alt or (obs_l and colpies(r).collidelist(obs_l) != -1):
                r.y -= py
                break

def empujarjug(jdat, ex, ey, anc, alt, obs_l=None, mapa=None):
    obs_l = _resolvobs(anc, alt, obs_l=obs_l, mapa=mapa, ent=jdat)
    desatascar(jdat, anc, alt, obs_l)
    _movpaso(jdat["rect"], ex, ey, anc, alt, obs_l)
    desatascar(jdat, anc, alt, obs_l)
    _acthitent(jdat)

def ajustapos(jdat, posmc, anc, alt, mapa, obs_l=None):
    r = jdat["rect"]
    r.left = max(0, min(posmc[0], anc - r.width))
    r.top = max(0, min(posmc[1], alt - r.height))

    if obs_l is None:
        obs_l = obstaculos(2 if mapa == 2 else 1, anc, alt)
    desatascar(jdat, anc, alt, obs_l)
    spr = jdat["sprs"][jdat["dir"]][0]
    jdat["hitbox"] = creahit(spr, r.topleft)

def crepuerta(anc, alt):
    return pygame.Rect(int(anc * 0.435), int(alt * 0.30), int(anc * 0.06), int(alt * 0.09))

def carmapa2(anc, alt, esc=2.4):
    w, h = int(anc * esc), int(alt * esc)
    k = (2, w, h)
    if k not in _CMAPAS:
        img = pygame.image.load(os.path.join("Sprites", "mapa2n.jpeg"))
        _CMAPAS[k] = pygame.transform.scale(img, (w, h)).convert()
    return _CMAPAS[k]

def _recfondo(ruta):
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

def carvidas(alt):
    vidas = []
    h = int(alt * 0.14)
    for n in range(6):
        img = pygame.image.load(f"Sprites/Vida/vida{n:02d}.png").convert_alpha()
        prop = img.get_width() / img.get_height()
        vidas.append(pygame.transform.scale(img, (int(h * prop), h)))
    return vidas

def carescudos(alt):
    escudos = []
    hesc = int(alt * 0.115)
    wesc = int(alt * 0.14 * 3.0)
    for n in range(1, 5):
        ruta = f"Sprites/escudo/escudo{n}.jpg"
        if not os.path.exists(ruta):
            ruta = f"escudo{n}.jpg"
        surf = _recfondo(ruta)
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

_CBLANC = {}

def blancsurf(surf):
    res = _CBLANC.get(surf)
    if res is None:
        if len(_CBLANC) >= 256:
            _CBLANC.clear()
        res = surf.copy()
        res.fill((110, 110, 110), special_flags=pygame.BLEND_RGB_ADD)
        _CBLANC[surf] = res
    return res

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

def dibvida(pant, vidas, jdat, escudos=None):
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
    tam_d = tam_f(alt, 0.024, 12)
    fdash = fuente(tam_d)
    xdash = rvida.right + max(14, int(alt * 0.02))
    ydash = alt - max(22, int(alt * 0.032))
    barra = pygame.Rect(xdash, ydash, int(alt * 0.18), max(8, int(alt * 0.014)))
    cd_fin = jdat.get("dash_cd_hasta", 0)
    cd_dur = max(1, jdat.get("dash_cd_dur", 950))
    carga = max(0.0, min(1.0, 1.0 - max(0, cd_fin - ahora) / cd_dur))
    lbldash = fdash.render("DASH [SHIFT]", False, (255, 255, 255))
    pant.blit(lbldash, (barra.x, barra.y - lbldash.get_height() - 2))
    pygame.draw.rect(pant, (30, 30, 30), barra, border_radius=4)
    colb = (90, 220, 110) if carga >= 1.0 else (255, 215, 60)
    if carga > 0:
        pygame.draw.rect(pant, colb, pygame.Rect(barra.x, barra.y, int(barra.width * carga), barra.height), border_radius=4)
    pygame.draw.rect(pant, (255, 255, 255), barra, 1, border_radius=4)

def danojug(jdat, ahora, cant=0.5, orig=None, anc_m=None, alt_m=None, obs_l=None, emp_max=None):
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
        txt = f"-{c:g} ESCUDO" if t_esc else f"-{c:g} VIDA"
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
            if emp_max is not None:
                emp = min(emp, int(emp_max))
            if emp > 0:
                ex = round((dx / dist) * emp)
                ey = round((dy / dist) * emp)
                empujarjug(jdat, ex, ey, anc_m, alt_m, obs_l)
    return True

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

    if tipo == "barracas":
        # Cargar sprites de caminar propios de Barracas
        for d, nums in sec.items():
            sprs[d] = []
            for n in nums:
                img = pygame.image.load(f"Sprites/Barracas/Barracas{n:03d}.png").convert_alpha()
                sprs[d].append(pygame.transform.scale(img, (wj, hj)))

        # Cargar animacion de ataque (4 frames de lanzamiento de piedra)
        sprat_der = [pygame.image.load(f"Sprites/Barracas/BA/BA_der_{i}.png").convert_alpha() for i in range(4)]
        sprat_izq = [pygame.image.load(f"Sprites/Barracas/BA/BA_izq_{i}.png").convert_alpha() for i in range(4)]
        spat_der = [pygame.transform.scale(im, (max(10, int(im.get_width() * (hj / 79))), hj)) for im in sprat_der]
        spat_izq = [pygame.transform.scale(im, (max(10, int(im.get_width() * (hj / 79))), hj)) for im in sprat_izq]

        sprat["derecha"] = spat_der
        sprat["izquierda"] = spat_izq
        sprat["abajo"] = spat_der
        sprat["arriba"] = spat_izq
    else:
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

def maxbarr(ole):
    bp = BAL_PIEDRA
    return 0 if ole < bp["ole_min"] else min(bp["max_vivos_tope"], bp["max_vivos_base"] + ole // bp["max_vivos_div"])

def colaoleada(ole):
    bp = BAL_PIEDRA
    tot = min(45, 5 + 3 * ole)
    p_tanq = 0.0 if ole < 4 else min(0.25, 0.08 + 0.02 * (ole - 4))
    p_barr = 0.0 if ole < 2 else min(0.35, 0.15 + 0.03 * (ole - 2))
    p_barracas = 0.0 if ole < bp["ole_min"] else min(bp["prob_max"], bp["prob_base"] + bp["prob_inc"] * (ole - bp["ole_min"]))
    tope_barr = 0 if ole < bp["ole_min"] else max(1, int(tot * bp["tope_cola_frac"]))
    n_barr = 0
    cola = []
    for _ in range(tot):
        r = random.random()
        if r < p_tanq:
            cola.append("tanque")
        elif r < p_tanq + p_barr:
            cola.append("barra")
        elif r < p_tanq + p_barr + p_barracas and n_barr < tope_barr:
            cola.append("barracas")
            n_barr += 1
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
        if not _posvalida(r, anc, alt, obs_l):
            continue
        if all(not r.inflate(esp, esp).colliderect(o["rect"]) for o in exis):
            break
    else:
        # Fallback garantizado dentro del mapa y fuera de obstaculos
        enc = False
        paso_x = max(16, (maxx - minx) // 18)
        paso_y = max(16, (maxy - miny) // 14)
        mejor_fb = None
        mejor_d = -1.0
        for gy in range(miny, maxy + 1, paso_y):
            for gx in range(minx, maxx + 1, paso_x):
                r.topleft = (gx, gy)
                if _posvalida(r, anc, alt, obs_l):
                    dj = math.hypot(r.centerx - jx, r.centery - jy)
                    libre_e = all(not r.colliderect(o["rect"]) for o in exis)
                    punt = dj + (1000.0 if libre_e else 0.0)
                    if punt > mejor_d:
                        mejor_d = punt
                        mejor_fb = (gx, gy)
                        enc = True
        if enc and mejor_fb is not None:
            r.topleft = mejor_fb
        else:
            desatascar(r, anc, alt, obs_l)

    if not _posvalida(r, anc, alt, obs_l):
        desatascar(r, anc, alt, obs_l)

    hp_m = round(cfg["hp"] * (1 + 0.10 * (ole - 1)))
    vbase = alt_p * 0.0040 * cfg["vel_mult"] * min(1.35, 1 + 0.015 * (ole - 1)) * random.uniform(0.92, 1.08)
    angbase = (idx / max(1, tot_esp)) * 2 * math.pi + random.uniform(-0.2, 0.2)

    return {
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
        "rad_m": random.uniform(BAL_PIEDRA["rad_min"], BAL_PIEDRA["rad_max"]) if tipo == "barracas" else random.uniform(0.9, 1.35)
    }

def _obtpiedra():
    global _PIEDRA, _CARGPIED
    if not _CARGPIED:
        _CARGPIED = True
        try:
            _PIEDRA = pygame.image.load(os.path.join("Sprites", "Barracas", "piedra.png")).convert_alpha()
        except Exception:
            _PIEDRA = None
    return _PIEDRA

def _carmolbas():
    global _MOLBASE, _FUEGOBASE
    if _MOLBASE is None:
        img = pygame.image.load(os.path.join("Sprites", "Molotov", "molotov_lanzada.png")).convert_alpha()
        br = img.get_bounding_rect()
        _MOLBASE = img.subsurface(br).copy() if (br.width > 0 and br.height > 0) else img
    if _FUEGOBASE is None:
        frames = []
        for i in range(6):
            imf = pygame.image.load(os.path.join("Sprites", "Fuego", f"fuego_{i}.png")).convert_alpha()
            brf = imf.get_bounding_rect()
            frames.append(imf.subsurface(brf).copy() if (brf.width > 0 and brf.height > 0) else imf)
        _FUEGOBASE = tuple(frames)
    return _MOLBASE, _FUEGOBASE

def _molrot(tam):
    tam = max(BAL_MOL["tam_proy_min"], int(tam))
    if tam not in _CMOL_LANZ:
        base_m, _ = _carmolbas()
        esc = tam / max(1, max(base_m.get_width(), base_m.get_height()))
        w = max(8, int(round(base_m.get_width() * esc)))
        h = max(8, int(round(base_m.get_height() * esc)))
        esc_m = pygame.transform.smoothscale(base_m, (w, h))
        _CMOL_LANZ[tam] = tuple(pygame.transform.rotate(esc_m, i * 5) for i in range(72))
    return _CMOL_LANZ[tam]

def _fuegofr(diam):
    diam = max(24, int(round(diam)))
    if diam not in _CFUEGO:
        _, bases_f = _carmolbas()
        _CFUEGO[diam] = tuple(pygame.transform.smoothscale(im, (diam, diam)) for im in bases_f)
    return _CFUEGO[diam]

def precmol(alt_p):
    _carmolbas()
    hj2 = max(16, int(alt_p * 0.075))
    hbh = max(12, int(hj2 * 0.80))
    tam = max(BAL_MOL["tam_proy_min"], int(round(hbh * BAL_MOL["tam_proy_mult"])))
    rad = max(24, int(round(hbh * BAL_MOL["radio_mult"])))
    _molrot(tam)
    _fuegofr(rad * 2)

def precenes(alt_p):
    for t in TIPOS_ENE:
        _sprsene(t, alt_p)
    _obtpiedra()
    precmol(alt_p)

def crearene(anc, alt, cant=1, ole=1, alt_p=None, jdat=None):
    if alt_p is None:
        alt_p = int(alt / 2.4)
    precenes(alt_p)

    infole = colaoleada(ole)
    enes = []
    tope_b = maxbarr(ole)
    ini = min(len(infole["cola"]), max(4, min(infole["max_sim"] // 2, 8)))
    for i in range(ini):
        t = infole["cola"].pop(0)
        if t == "barracas":
            vivos_b = sum(1 for e in enes if e.get("vida", 0) > 0 and e.get("tipo") == "barracas")
            if vivos_b >= tope_b:
                t = "hincha"
        e = instene(t, ole, anc, alt, alt_p, enes, jdat=jdat, idx=i, tot_esp=infole["tot"])
        enes.append(e)

    if jdat is not None:
        jdat["ole_inf"] = infole
        jdat["drops"] = []
        jdat["textos"] = []
        jdat["chispas"] = []
        jdat["zonas_fuego"] = []
        sub = "¡Cuidado, viene EL JEFE!" if infole["jefe"] else f"{infole['tot']} enemigos en camino"
        setbanner(jdat, f"OLEADA {ole}", sub, dur_ms=2500)

    return enes

def danarene(ene, cant, emp_x=0.0, emp_y=0.0, jdat=None):
    ahora = pygame.time.get_ticks()
    d_real = cant
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

def limpmol(jdat, proys=None, enes=None):
    if isinstance(jdat, dict):
        jdat["zonas_fuego"] = []
        jdat["cd_mol_hasta"] = 0
        jdat.pop("pausa_ini", None)
    if proys is not None:
        for p in proys[:]:
            if p.get("es_molotov"):
                proys.remove(p)
    if enes is not None:
        for e in enes:
            if isinstance(e, dict):
                e["quem_hasta"] = 0

def desptimers(jdat, proys=None, enes=None, dt_ms=0):
    dt = int(round(dt_ms))
    if dt <= 0:
        return
    if isinstance(jdat, dict):
        for z in jdat.get("zonas_fuego", []):
            z["inicio"] += dt
            z["ult_tick"] += dt
        for k in ("cd_mol_hasta", "cd_mol_ini", "rec_hasta", "cd_disp_hasta", "cd_golpe_hasta",
                  "dash_ini", "dash_hasta", "dash_cd_hasta", "dash_invul_hasta", "slot_msg_hasta"):
            if jdat.get(k, 0) > 0:
                jdat[k] += dt
        for d in jdat.get("drops", []):
            d["inicio"] += dt
        for c in jdat.get("chispas", []):
            c["inicio"] += dt
        for t in jdat.get("textos", []):
            t["inicio"] += dt
        if jdat.get("banner"):
            jdat["banner"]["inicio"] += dt
    if proys is not None:
        for p in proys:
            if isinstance(p, dict) and "t_ini" in p:
                p["t_ini"] += dt
    if enes is not None:
        for e in enes:
            if isinstance(e, dict):
                if e.get("quem_hasta", 0) > 0:
                    e["quem_hasta"] += dt
                if "quem_ult_tick" in e:
                    e["quem_ult_tick"] += dt
                if "quem_ult_chispa" in e:
                    e["quem_ult_chispa"] += dt

def inipausa(jdat, ahora=None):
    if isinstance(jdat, dict):
        jdat["pausa_ini"] = pygame.time.get_ticks() if ahora is None else ahora

def reanpausa(jdat, proys=None, enes=None, ahora=None):
    if not isinstance(jdat, dict):
        return 0
    t_ini = jdat.pop("pausa_ini", None)
    if t_ini is None:
        return 0
    act = pygame.time.get_ticks() if ahora is None else ahora
    dt = max(0, act - t_ini)
    desptimers(jdat, proys=proys, enes=enes, dt_ms=dt)
    return dt

def _crezfuego(jdat, x, y, radio=None, ahora=None):
    if jdat is None:
        return None
    if ahora is None:
        ahora = pygame.time.get_ticks()
    bm = BAL_MOL
    if radio is None:
        radio = max(24, int(round(jdat["hitbox"].height * bm["radio_mult"])))
    addchispas(jdat, x, y, (255, 140, 35), cant=14, fuerza=5.5)
    zonas = jdat.setdefault("zonas_fuego", [])
    z = {
        "x": int(round(x)),
        "y": int(round(y)),
        "radio": int(round(radio)),
        "inicio": ahora,
        "dur": bm["dur_ms"],
        "ult_tick": ahora - bm["tick_ms"],
    }
    zonas.append(z)
    while len(zonas) > bm["max_zonas"]:
        zonas.pop(0)
    return z

def destmol(jdat, dest, anc, alt, obs_l=None, mapa=2):
    obs_l = _resolvobs(anc, alt, obs_l=obs_l, mapa=mapa, ent=jdat)
    pies = colpies(jdat["rect"])
    ox, oy = float(pies.centerx), float(pies.centery)
    if any(o.collidepoint(int(ox), int(oy)) for o in obs_l):
        desatascar(jdat, anc, alt, obs_l=obs_l, mapa=mapa)
        pies = colpies(jdat["rect"])
        ox, oy = float(pies.centerx), float(pies.centery)

    dx = dest[0] - ox
    dy = dest[1] - oy
    dist = math.hypot(dx, dy)
    alc_max = jdat["hitbox"].height * BAL_MOL["alc_mult"]
    d_obj = min(dist, alc_max)
    ux, uy = (dx / dist, dy / dist) if dist > 0 else (1.0, 0.0)

    ult_x = max(2, min(anc - 3, int(round(ox))))
    ult_y = max(2, min(alt - 3, int(round(oy))))
    pasos = int(math.ceil(d_obj))
    for i in range(1, pasos + 1):
        s = min(float(i), d_obj)
        px = int(round(ox + ux * s))
        py = int(round(oy + uy * s))
        if px < 2 or px >= anc - 2 or py < 2 or py >= alt - 2:
            break
        if any(o.collidepoint(px, py) for o in obs_l):
            break
        ult_x, ult_y = px, py
    return ult_x, ult_y

def lanzmol(jdat, dest, mapa, anc=None, alt=None, obs_l=None):
    ahora = pygame.time.get_ticks()
    if mapa != 2:
        jdat["slot_msg"] = "SOLO EN COMBATE"
        jdat["slot_msg_hasta"] = ahora + 1400
        return None
    if jdat.get("molotovs", 0) <= 0:
        jdat["slot_msg"] = "SIN MOLOTOVS"
        jdat["slot_msg_hasta"] = ahora + 1400
        return None
    if jdat.get("dash") and ahora < jdat.get("dash_hasta", 0):
        return None
    if ahora < jdat.get("cd_mol_hasta", 0):
        return None

    wm = anc or 2400
    hm = alt or 1400
    obs_l = _resolvobs(wm, hm, obs_l=obs_l, mapa=2, ent=jdat)

    orig_hb = jdat["hitbox"].center
    dx_o = dest[0] - orig_hb[0]
    dy_o = dest[1] - orig_hb[1]
    if dx_o == 0 and dy_o == 0:
        dx_o = 1
    if abs(dx_o) >= abs(dy_o):
        jdat["dir"] = "derecha" if dx_o > 0 else "izquierda"
    else:
        jdat["dir"] = "abajo" if dy_o > 0 else "arriba"
    if dx_o != 0:
        jdat["lado_x"] = 1 if dx_o > 0 else -1

    pies = colpies(jdat["rect"])
    ox, oy = float(pies.centerx), float(pies.centery)
    tx, ty = destmol(jdat, dest, wm, hm, obs_l=obs_l, mapa=2)

    bm = BAL_MOL
    jdat["molotovs"] -= 1
    jdat["cd_mol_dur"] = bm["cd_ms"]
    jdat["cd_mol_hasta"] = ahora + bm["cd_ms"]

    hbh = jdat["hitbox"].height
    tam = max(bm["tam_proy_min"], int(round(hbh * bm["tam_proy_mult"])))
    proy = pygame.Rect(0, 0, tam, tam)
    proy.center = (int(round(ox)), int(round(oy)))
    dist_real = math.hypot(tx - ox, ty - oy)
    ux, uy = ((tx - ox) / dist_real, (ty - oy) / dist_real) if dist_real > 0 else (1.0, 0.0)
    dur_vuelo = bm["vuelo_ms"]
    v_aprox = dist_real / max(1.0, dur_vuelo / 16.0)
    arco_max = max(18.0, hbh * bm["arco_alt_mult"] * max(0.35, min(1.0, dist_real / max(1.0, hbh * bm["alc_mult"]))))
    return {
        "rect": proy,
        "lado": "molotov",
        "es_molotov": True,
        "x0": float(ox),
        "y0": float(oy),
        "tx": float(tx),
        "ty": float(ty),
        "fx": float(ox),
        "fy": float(oy),
        "dx": ux * v_aprox,
        "dy": uy * v_aprox,
        "alcance": dist_real,
        "recorrido": 0.0,
        "t_ini": ahora,
        "dur_vuelo": dur_vuelo,
        "arco_max": arco_max,
        "arco_y": 0.0,
        "angulo": 0.0,
        "tam": tam,
        "radio_fuego": max(24, int(round(hbh * bm["radio_mult"]))),
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
        "rect_ini": proy.copy(),
        "orig_hb": jdat["hitbox"].copy(),
        "orig_pies": colpies(jdat["rect"]).center,
        "dx": ux * vbala,
        "dy": uy * vbala,
        "alcance": max(dist, jdat["hitbox"].height * 9.5),
        "recorrido": 0,
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

    h = ene["hitbox"]
    if ene.get("tipo") == "barracas":
        bp = BAL_PIEDRA
        dist = math.hypot(dx, dy)
        ux, uy = (dx / dist, dy / dist) if dist > 0 else (1.0, 0.0)
        v = max(bp["vel_piedra_min"], h.height * bp["vel_piedra_mult"])
        tam = max(bp["tam_piedra_min"], int(h.height * bp["tam_piedra_mult"]))
        proy = pygame.Rect(0, 0, tam, tam)
        proy.center = (int(h.centerx + ux * 12), int(h.centery + uy * 12))
        return {
            "rect": proy,
            "rect_ini": proy.copy(),
            "orig_hb": h.copy(),
            "orig_pies": colpies(ene["rect"]).center,
            "dx": ux * v,
            "dy": uy * v,
            "alcance": max(dist + bp["alc_piedra_extra"], int(h.height * bp["alc_piedra_mult"])),
            "recorrido": 0,
            "lado": "enemigo",
            "es_piedra": True,
            "angulo": math.degrees(math.atan2(-uy, ux)),
            "daño": ene.get("daño", bp["daño"]),
            "orig": ene
        }

    ene["ataq"] = True
    ene["golpe_hecho"] = False
    ene["fraataq"] = 0
    ene["ultfra"] = pygame.time.get_ticks()
    ene["proximoataq"] = pygame.time.get_ticks() + ene.get("esp_ms", 850)
    return None

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
                    jdat["panchos"] = jdat.get("panchos", 0) + 1
                    addtxtflot(jdat, "+1 PANCHO", jx, jdat["rect"].top - 12, (90, 220, 110))
            elif d["tipo"] == "balas":
                bmax = jdat.get("bmax", 10)
                jdat["balas"] = min(bmax, jdat.get("balas", bmax) + d["val"])
                if jdat["balas"] > 0:
                    jdat["rec_hasta"] = 0
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

def actene(enes, jdat, proys, obs_l=None, anc=None, alt=None, cam_rect=None):
    ahora = pygame.time.get_ticks()
    actefectos(jdat)

    infole = jdat.get("ole_inf") if jdat else None
    ole_act = infole["num"] if infole else 1
    vivos = [e for e in enes if e["vida"] > 0]
    if infole and infole["cola"]:
        if len(vivos) < infole["max_sim"] and (ahora - infole["ultspawn"] >= infole["interv_ms"] or len(vivos) == 0):
            infole["ultspawn"] = ahora
            t_nuevo = infole["cola"].pop(0)
            if t_nuevo == "barracas":
                vivos_b = sum(1 for e in vivos if e.get("tipo") == "barracas")
                if vivos_b >= maxbarr(ole_act):
                    t_nuevo = "hincha"
            wm = anc or 2400
            hm = alt or 1400
            hp = int(hm / 2.4)
            idx_sp = infole["tot"] - len(infole["cola"])
            nene = instene(t_nuevo, infole["num"], wm, hm, hp, enes, jdat=jdat, idx=idx_sp, tot_esp=infole["tot"])
            enes.append(nene)
            vivos.append(nene)
            if t_nuevo == "jefe":
                setbanner(jdat, "¡LLEGO EL JEFE!", "Derrotalo para despejar la zona", dur_ms=2400)

    tot_v = len(vivos)
    if tot_v == 0:
        if infole and not infole["cola"] and not infole.get("fin"):
            infole["fin"] = True
            limpmol(jdat, proys)
            n = infole["num"]
            bon = 25 * n
            jdat["pesos"] = jdat.get("pesos", 0) + bon
            jdat["puntos"] = jdat.get("puntos", 0) + 50 * n
            for d in jdat.get("drops", []):
                d["iman"] = True
            setbanner(jdat, f"¡OLEADA {n} COMPLETADA!", f"+${bon} de bonus - Avanza a la derecha ->", dur_ms=3500)
        return

    wm = anc or 2400
    hm = alt or 1400
    if obs_l is None:
        obs_l = obstaculos(2, wm, hm)
    if cam_rect is None:
        cw = int(wm / 2.4)
        ch = int(hm / 2.4)
        cx = max(0, min(jdat["rect"].centerx - cw // 2, wm - cw))
        cy = max(0, min(jdat["rect"].centery - ch // 2, hm - ch))
        cam_rect = pygame.Rect(cx, cy, cw, ch)

    bp = BAL_PIEDRA
    max_lanz = bp["max_lanz_baja"] if ole_act < bp["ole_lanz_alta"] else bp["max_lanz_alta"]
    lanz_ids = {id(e) for e in vivos if e.get("tipo") == "barracas" and e.get("ataq")}
    for p in proys:
        if p.get("es_piedra") and p.get("orig") is not None:
            lanz_ids.add(id(p["orig"]))

    jcent = jdat["hitbox"].center
    alc_base = jdat["hitbox"].height * 1.25

    for idx, ene in enumerate(vivos):
        if "ang_at" not in ene:
            ene["ang_at"] = (idx / max(1, tot_v)) * 2 * math.pi
            ene["rad_m"] = random.uniform(bp["rad_min"], bp["rad_max"]) if ene.get("tipo") == "barracas" else random.uniform(0.9, 1.35)

        desatascar(ene, wm, hm, obs_l)

        kx = ene.get("kx", 0.0)
        ky = ene.get("ky", 0.0)
        if abs(kx) > 0.4 or abs(ky) > 0.4:
            rx = round(kx)
            ry = round(ky)
            _movpaso(ene["rect"], rx, ry, wm, hm, obs_l)
            ene["kx"] = kx * 0.78
            ene["ky"] = ky * 0.78

        dx_j = jcent[0] - ene["hitbox"].centerx
        dy_j = jcent[1] - ene["hitbox"].centery
        dist_j = math.hypot(dx_j, dy_j)
        alc_e = alc_base * ene.get("alc_m", 1.15)
        es_barr = ene.get("tipo") == "barracas"
        en_cam = cam_rect.contains(ene["hitbox"])

        if ene["ataq"]:
            interv_fra = bp["windup_fra_ms"] if es_barr else 110
            tot_fra = len(ene["sprataq"][ene["dir"]])
            if ahora - ene["ultfra"] >= interv_fra:
                ene["fraataq"] += 1
                ene["ultfra"] = ahora
                if es_barr:
                    # Lanza la piedra en el frame configurado del lanzamiento
                    if ene["fraataq"] == bp["fra_lanz"] and not ene.get("golpe_hecho", False):
                        ene["golpe_hecho"] = True
                        if en_cam:
                            proys.append(proyene(ene, jdat))
                else:
                    if ene["fraataq"] == 1 and not ene.get("golpe_hecho", False):
                        ene["golpe_hecho"] = True
                        if dist_j <= alc_e * 1.25 and ahora - jdat.get("ultdaño", -1000) >= 900:
                            danojug(jdat, ahora, cant=ene.get("daño", 0.5), orig=ene, anc_m=wm, alt_m=hm, obs_l=obs_l)
                if ene["fraataq"] >= tot_fra:
                    ene["ataq"] = False
                    ene["fraataq"] = 0
                    if es_barr:
                        ene["proximoataq"] = ahora + ene.get("esp_ms", bp["esp_ms"]) + random.randint(-bp["jitter_ms"], bp["jitter_ms"])
        elif dist_j <= alc_e and ahora >= ene["proximoataq"] and (not es_barr or (en_cam and len(lanz_ids) < max_lanz)):
            if es_barr:
                dx = jcent[0] - ene["hitbox"].centerx
                dy = jcent[1] - ene["hitbox"].centery
                d = "derecha" if dx >= 0 else "izquierda"
                if abs(dy) > abs(dx):
                    d = "abajo" if dy >= 0 else "arriba"
                ene["dir"] = d
                ene["ataq"] = True
                ene["golpe_hecho"] = False
                ene["fraataq"] = 0
                ene["ultfra"] = ahora
                lanz_ids.add(id(ene))
            else:
                proyene(ene, jdat)
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

                _movpaso(ene["rect"], movx, movy, wm, hm, obs_l)

                for otro in vivos:
                    if otro is ene:
                        continue
                    if ene["rect"].colliderect(otro["rect"]):
                        pdx = ene["rect"].centerx - otro["rect"].centerx
                        pdy = ene["rect"].centery - otro["rect"].centery
                        if pdx == 0 and pdy == 0:
                            pdx = random.choice([-1, 1])
                        px = 1 if pdx > 0 else -1
                        py_ = 1 if pdy > 0 else -1
                        _movpaso(ene["rect"], px, py_, wm, hm, obs_l)

                if ahora - ene["ultmov"] >= 140 and (movx != 0 or movy != 0):
                    ene["frame"] = (ene["frame"] + 1) % 3
                    ene["ultmov"] = ahora
            else:
                ene["dir"] = ("derecha" if dx_j > 0 else "izquierda") if abs(dx_j) >= abs(dy_j) else ("abajo" if dy_j > 0 else "arriba")

        desatascar(ene, wm, hm, obs_l)
        spr = ene["sprataq"][ene["dir"]][ene["fraataq"]] if ene["ataq"] else ene["sprs"][ene["dir"]][int(ene["frame"])]
        ene["hitbox"] = creahit(spr, ene["rect"].topleft)

def _ignobsnac(p, obs_l):
    if "obs_ign" not in p:
        r0 = p.get("rect_ini", p["rect"])
        ohb = p.get("orig_hb")
        p["obs_ign"] = {
            i for i, o in enumerate(obs_l)
            if r0.colliderect(o) or (ohb is not None and ohb.colliderect(o))
        } if obs_l else set()
    return p["obs_ign"]

def _chocaobs(p, ant, act, obs_l, targ_hb=None, targ_pies=None):
    if not obs_l:
        return False
    ign = _ignobsnac(p, obs_l)
    orig_pies = p.get("orig_pies")
    choca = False
    for i, o in enumerate(obs_l):
        if i in ign:
            continue
        if o.clipline(ant, act) or p["rect"].colliderect(o):
            if targ_hb is not None and o.colliderect(targ_hb):
                if orig_pies is not None and targ_pies is not None and not o.clipline(orig_pies, targ_pies):
                    d_ant = math.hypot(targ_hb.centerx - ant[0], targ_hb.centery - ant[1])
                    d_act = math.hypot(targ_hb.centerx - act[0], targ_hb.centery - act[1])
                    if d_act <= d_ant + 1.0:
                        continue
            choca = True
            break
    if ign:
        ign.difference_update({i for i in list(ign) if i >= len(obs_l) or not p["rect"].colliderect(obs_l[i])})
    return choca

def _limpenes(enes, jdat, ahora):
    for ene in enes[:]:
        if ene["vida"] <= 0 and ahora >= ene["golpe_hasta"]:
            enes.remove(ene)
            if jdat is not None:
                oact = jdat.get("ole_inf", {}).get("num", jdat.get("oleada", 1))
                pts = round(ene.get("pts", 10) * (1 + 0.1 * (oact - 1)))
                jdat["puntos"] = jdat.get("puntos", 0) + pts
                gendrops(jdat, ene)
                addchispas(jdat, ene["rect"].centerx, ene["rect"].centery, (230, 60, 60), cant=12, fuerza=5.5)

def actfuego(jdat, enes, ahora=None):
    if jdat is None:
        return
    if ahora is None:
        ahora = pygame.time.get_ticks()
    bm = BAL_MOL
    zonas = jdat.get("zonas_fuego")
    en_zona = set()
    if zonas:
        nzonas = []
        for z in zonas:
            if ahora - z["inicio"] >= z["dur"]:
                continue
            nzonas.append(z)
            zx, zy, zr = z["x"], z["y"], z["radio"]
            hacer_tick = (ahora - z["ult_tick"] >= bm["tick_ms"])
            if hacer_tick:
                z["ult_tick"] += bm["tick_ms"]
                if ahora - z["ult_tick"] >= bm["tick_ms"]:
                    z["ult_tick"] = ahora
            for ene in enes:
                if ene.get("vida", 0) <= 0:
                    continue
                hx, hy = ene["hitbox"].center
                if math.hypot(hx - zx, hy - zy) <= zr:
                    en_zona.add(id(ene))
                    ene["quem_hasta"] = ahora + bm["quem_dur_ms"]
                    if "quem_ult_tick" not in ene:
                        ene["quem_ult_tick"] = ahora
                    if hacer_tick:
                        mult = bm["jefe_mult"] if ene.get("tipo") == "jefe" else 1.0
                        d_z = bm["daño_tick"] * mult
                        danarene(ene, d_z, emp_x=0.0, emp_y=0.0, jdat=jdat)
                        ene["quem_hasta"] = ahora + bm["quem_dur_ms"]
                        ene["quem_ult_tick"] = ahora
        jdat["zonas_fuego"] = nzonas

    for ene in enes:
        if ene.get("vida", 0) <= 0:
            continue
        if ahora < ene.get("quem_hasta", 0):
            if ahora - ene.get("quem_ult_chispa", 0) >= bm["quem_chispa_ms"]:
                ene["quem_ult_chispa"] = ahora
                addchispas(jdat, ene["hitbox"].centerx, ene["hitbox"].centery, (255, 145, 35), cant=2, fuerza=2.8)
            if id(ene) not in en_zona and ahora - ene.get("quem_ult_tick", 0) >= bm["tick_ms"]:
                ene["quem_ult_tick"] += bm["tick_ms"]
                if ahora - ene["quem_ult_tick"] >= bm["tick_ms"]:
                    ene["quem_ult_tick"] = ahora
                mult = bm["jefe_mult"] if ene.get("tipo") == "jefe" else 1.0
                d_q = bm["quem_daño_tick"] * mult
                danarene(ene, d_q, emp_x=0.0, emp_y=0.0, jdat=jdat)

def moverproy(proys, enes, anc, alt, jdat=None, obs_l=None, mapa=None):
    ahora = pygame.time.get_ticks()
    obs_l = _resolvobs(anc, alt, obs_l=obs_l, mapa=mapa, ent=jdat)
    _limpenes(enes, jdat, ahora)

    for p in proys[:]:
        if p.get("es_molotov"):
            dur_v = max(1, p.get("dur_vuelo", BAL_MOL["vuelo_ms"]))
            prog = min(1.0, max(0.0, (ahora - p.get("t_ini", ahora)) / dur_v))
            ant_x, ant_y = p.get("fx", float(p["rect"].centerx)), p.get("fy", float(p["rect"].centery))
            cand_x = p["x0"] + (p["tx"] - p["x0"]) * prog
            cand_y = p["y0"] + (p["ty"] - p["y0"]) * prog
            tramo = math.hypot(cand_x - ant_x, cand_y - ant_y)
            ult_x, ult_y = int(round(ant_x)), int(round(ant_y))
            choco_obs = False
            if tramo > 0:
                ux_t = (cand_x - ant_x) / tramo
                uy_t = (cand_y - ant_y) / tramo
                for s_i in range(1, int(math.ceil(tramo)) + 1):
                    s_d = min(float(s_i), tramo)
                    px = int(round(ant_x + ux_t * s_d))
                    py = int(round(ant_y + uy_t * s_d))
                    if px < 2 or px >= anc - 2 or py < 2 or py >= alt - 2 or (obs_l and any(o.collidepoint(px, py) for o in obs_l)):
                        choco_obs = True
                        break
                    ult_x, ult_y = px, py
                if choco_obs:
                    cand_x, cand_y = float(ult_x), float(ult_y)
                    prog = 1.0
            p["fx"], p["fy"] = cand_x, cand_y
            p["rect"].center = (int(round(cand_x)), int(round(cand_y)))
            p["recorrido"] = math.hypot(cand_x - p["x0"], cand_y - p["y0"])
            p["arco_y"] = p.get("arco_max", 36.0) * 4.0 * prog * (1.0 - prog)
            p["angulo"] = ((ahora - p.get("t_ini", ahora)) * BAL_MOL["vel_rot"] / 1000.0) % 360.0
            if prog >= 1.0:
                proys.remove(p)
                _crezfuego(jdat, p["rect"].centerx, p["rect"].centery, p.get("radio_fuego"), ahora=ahora)
            continue

        if p.get("lado") == "pistola":
            _ignobsnac(p, obs_l)
            ant = p["rect"].center
            if "fx" not in p:
                p["fx"], p["fy"] = float(ant[0]), float(ant[1])
            v = math.hypot(p["dx"], p["dy"])
            rest = max(0.0, p["alcance"] - p["recorrido"])
            paso = min(v, rest)
            if v > 0:
                p["fx"] += (p["dx"] / v) * paso
                p["fy"] += (p["dy"] / v) * paso
                p["rect"].center = (round(p["fx"]), round(p["fy"]))
            p["recorrido"] = min(p["alcance"], p["recorrido"] + paso)
            act = p["rect"].center
            ux = p["dx"] / v if v > 0 else 0
            uy = p["dy"] / v if v > 0 else 0
            for ene in enes:
                if ene["vida"] > 0 and (ene["hitbox"].clipline(ant, act) or ene["hitbox"].colliderect(p["rect"])):
                    danarene(ene, dano_BALA, emp_x=ux * 11.0, emp_y=uy * 11.0, jdat=jdat)
                    proys.remove(p)
                    break
            if p not in proys:
                continue
            if _chocaobs(p, ant, act, obs_l):
                proys.remove(p)
                continue
            if p["recorrido"] >= p["alcance"] or not pygame.Rect(-40, -40, anc + 80, alt + 80).colliderect(p["rect"]):
                proys.remove(p)
            continue

        if p.get("es_piedra"):
            _ignobsnac(p, obs_l)
            ant = p["rect"].center
            if "fx" not in p:
                p["fx"], p["fy"] = float(ant[0]), float(ant[1])
            v = math.hypot(p["dx"], p["dy"])
            rest = max(0.0, p["alcance"] - p["recorrido"])
            paso = min(v, rest)
            if v > 0:
                p["fx"] += (p["dx"] / v) * paso
                p["fy"] += (p["dy"] / v) * paso
                p["rect"].center = (round(p["fx"]), round(p["fy"]))
            p["recorrido"] += paso
            act = p["rect"].center
            if jdat is not None and ahora >= jdat.get("dash_invul_hasta", 0) and (jdat["hitbox"].clipline(ant, act) or p["rect"].colliderect(jdat["hitbox"])):
                if ahora - jdat.get("ultdaño", -1000) >= 900:
                    danojug(jdat, ahora, cant=p.get("daño", BAL_PIEDRA["daño"]), orig=p.get("orig"), anc_m=anc, alt_m=alt, obs_l=obs_l, emp_max=BAL_PIEDRA["emp_max"])
                proys.remove(p)
                continue
            j_hb = jdat["hitbox"] if jdat is not None else None
            j_pies = colpies(jdat["rect"]).center if jdat is not None else None
            if _chocaobs(p, ant, act, obs_l, targ_hb=j_hb, targ_pies=j_pies):
                proys.remove(p)
                continue
            if p["recorrido"] >= p["alcance"] or not pygame.Rect(0, 0, anc, alt).colliderect(p["rect"]):
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
                    emp_m = 4 if p.get("es_piedra") else None
                    danojug(jdat, ahora, cant=p.get("daño", 0.5), orig=p.get("orig"), anc_m=anc, alt_m=alt, obs_l=obs_l, emp_max=emp_m)
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
                    danarene(ene, dano_PUNO, emp_x=vx * 14.0, emp_y=vy * 14.0, jdat=jdat)
        if p["recorrido"] >= p["alcance"] or not pygame.Rect(0, 0, anc, alt).colliderect(p["rect"]):
            proys.remove(p)

    actfuego(jdat, enes, ahora=ahora)
    _limpenes(enes, jdat, ahora)

def bderrota(anc, alt):
    ftit = fuente(tam_f(alt, 0.065, 16))
    fbtn = fuente(tam_f(alt, 0.038, 12))
    wpan = int(anc * 0.32)
    wbtn = int(wpan * 0.78 * 1.5)
    hbtn = int(alt * 0.08 * 1.5)
    xb = (anc - wbtn) // 2
    return ftit, fbtn, [
        {"texto": "VOLVER A JUGAR", "rect": pygame.Rect(xb, int(alt * 0.52), wbtn, hbtn), "accion": "jugar"},
        {"texto": "MENU", "rect": pygame.Rect(xb, int(alt * 0.68), wbtn, hbtn), "accion": "menu"}
    ]

def dibperdida(pant, jdat, mgraf, ftit, fbtn, btns, mouse, cam=(0, 0)):
    dibjuego(pant, mgraf, jdat, [], [], False, cam=cam)

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
        txt = fbtn.render(b["texto"], False, (255, 255, 255))
        pant.blit(txt, txt.get_rect(center=b["rect"].center))

def dibvic(pant, jdat, mgraf, ftit, fbtn, btns, mouse, vidas=None, escudos=None):
    dibjuego(pant, mgraf, jdat, vidas or [], [], mvida=bool(vidas), escudos=escudos)
    capa = pygame.Surface(pant.get_size(), pygame.SRCALPHA)
    capa.fill((0, 0, 0, 150))
    pant.blit(capa, (0, 0))
    anc = pant.get_width()
    alt = pant.get_height()
    txt = ftit.render("COMPLETASTE LAS 20 OLEADAS", False, (255, 255, 255))
    pant.blit(txt, txt.get_rect(center=(anc // 2, int(alt * 0.25))))
    subv = fbtn.render("GG fucking Easy", False, (255, 255, 255))
    pant.blit(subv, subv.get_rect(center=(anc // 2, int(alt * 0.36))))
    for b in btns:
        act = b["rect"].collidepoint(mouse)
        pygame.draw.rect(pant, (95, 95, 95) if act else (75, 75, 75), b["rect"], border_radius=6)
        pygame.draw.rect(pant, (130, 130, 130) if act else (45, 45, 45), b["rect"], width=3, border_radius=6)
        tb = fbtn.render(b["texto"], False, (255, 255, 255))
        pant.blit(tb, tb.get_rect(center=b["rect"].center))

def capas(anc, alt, wpan):
    pizq = pygame.Surface((wpan, alt))
    pizq.fill((0, 0, 0))
    pizq.set_alpha(170)

    pder = pygame.Surface((anc - wpan, alt))
    pder.fill((0, 0, 0))
    pder.set_alpha(128)
    return pizq, pder

def fuentes(alt):
    return fuente(tam_f(alt, 0.065, 16)), fuente(tam_f(alt, 0.038, 12))

def grosor(fte, txt, col, g=2):
    surf = fte.render(txt, False, col)
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
        tsurf = fbtn.render(b["texto"], False, (255, 255, 255))
        pant.blit(tsurf, tsurf.get_rect(center=b["rect"].center))

def cargarmapa(anc, alt):
    k = (1, anc, alt)
    if k not in _CMAPAS:
        r1 = os.path.join("Sprites", "mapa1n.jpeg")
        r2 = os.path.join("F", "Mapa.png")
        ruta = r1 if os.path.exists(r1) else (r2 if os.path.exists(r2) else "Mapa.png")
        _CMAPAS[k] = pygame.transform.scale(pygame.image.load(ruta), (anc, alt)).convert()
    return _CMAPAS[k]

def cargabazar(anc, alt):
    imgs = []
    for nom in ("andy00", "andy01"):
        r1 = os.path.join("Sprites", "Andy", f"{nom}.png")
        ruta = r1 if os.path.exists(r1) else f"{nom}.png"
        imgs.append(pygame.transform.scale(pygame.image.load(ruta).convert(), (anc, alt)))
    return imgs

_CLAYTIEN = {}

def laytienda(anc, alt):
    k = (anc, alt)
    if k in _CLAYTIEN:
        return _CLAYTIEN[k]

    pw = int(anc * 0.84)
    ph = int(alt * 0.74)
    px = (anc - pw) // 2
    py = (alt - ph) // 2
    panel_tienda = pygame.Rect(px, py, pw, ph)

    w_vol = int(pw * 0.13)
    h_vol = int(ph * 0.075)
    btn_volver = pygame.Rect(px + int(pw * 0.025), py + int(ph * 0.025), w_vol, h_vol)
    r_titulo = pygame.Rect(px + int(pw * 0.16), py + int(ph * 0.025), int(pw * 0.68), h_vol)

    gap_x = max(6, int(pw * 0.016))
    margin_x = max(10, int(pw * 0.025))
    w_card = (pw - 2 * margin_x - 3 * gap_x) // 4
    y_card = py + int(ph * 0.115)
    h_card = int(ph * 0.62)

    items_cfg = [
        ("pistola", "PISTOLA", PRE_PIST, "Pistola del Papu: hace mas daño que el puño y tiene mas alcance"),
        ("molotov", "MOLOTOV", PRE_MOL, "Fuego en area. Quema a los enemigos"),
        ("pancho", "PANCHO", PRE_PAN, "Restaura toda la vida (tecla E)"),
        ("speed", "SPEED", PRE_SPD, "+1 barra de escudo (tecla Q)")
    ]
    tarjetas = []
    for i, (cid, cnom, cpre, cdesc) in enumerate(items_cfg):
        cx = px + margin_x + i * (w_card + gap_x)
        cr = pygame.Rect(cx, y_card, w_card, h_card)
        r_nom = pygame.Rect(cr.left + 4, cr.top + int(h_card * 0.02), w_card - 8, int(h_card * 0.08))
        r_pre = pygame.Rect(cr.left + 4, cr.top + int(h_card * 0.10), w_card - 8, int(h_card * 0.07))
        isz = min(int(w_card * 0.55), int(h_card * 0.27))
        r_ic = pygame.Rect(cr.centerx - isz // 2, cr.top + int(h_card * 0.18), isz, isz)
        r_desc = pygame.Rect(cr.left + 6, cr.top + int(h_card * 0.48), w_card - 12, int(h_card * 0.22))
        r_ten = pygame.Rect(cr.left + 6, cr.top + int(h_card * 0.72), w_card - 12, int(h_card * 0.08))
        btn_h = int(h_card * 0.11)
        btn_w = int(w_card * 0.26)
        btn_y = cr.bottom - btn_h - max(6, int(h_card * 0.03))
        btn_menos = pygame.Rect(cr.left + int(w_card * 0.08), btn_y, btn_w, btn_h)
        btn_mas = pygame.Rect(cr.right - int(w_card * 0.08) - btn_w, btn_y, btn_w, btn_h)
        r_badge = pygame.Rect(btn_menos.right, btn_y, btn_mas.left - btn_menos.right, btn_h)
        tarjetas.append({
            "id": cid, "nombre": cnom, "precio": cpre, "desc": cdesc,
            "rect": cr, "r_nom": r_nom, "r_precio": r_pre, "r_icon": r_ic,
            "r_desc": r_desc, "r_tenes": r_ten,
            "btn_menos": btn_menos, "btn_mas": btn_mas, "r_badge": r_badge
        })

    y_bot = y_card + h_card + int(ph * 0.02)
    h_bot = py + ph - y_bot - max(6, int(ph * 0.02))
    r_pesos = pygame.Rect(px + int(pw * 0.03), y_bot + int(h_bot * 0.08), int(pw * 0.26), int(h_bot * 0.42))
    r_total = pygame.Rect(px + int(pw * 0.03), y_bot + int(h_bot * 0.52), int(pw * 0.26), int(h_bot * 0.42))
    w_bbtn = int(pw * 0.14)
    h_bbtn = int(h_bot * 0.75)
    btn_comprar = pygame.Rect(px + pw - int(pw * 0.03) - w_bbtn, y_bot + (h_bot - h_bbtn) // 2, w_bbtn, h_bbtn)
    btn_vaciar = pygame.Rect(btn_comprar.left - int(pw * 0.02) - w_bbtn, y_bot + (h_bot - h_bbtn) // 2, w_bbtn, h_bbtn)
    r_msg = pygame.Rect(r_pesos.right + int(pw * 0.02), y_bot + int(h_bot * 0.10), btn_vaciar.left - r_pesos.right - int(pw * 0.04), int(h_bot * 0.80))

    pw_d = int(anc * 0.78)
    ph_d = int(alt * 0.24)
    px_d = (anc - pw_d) // 2
    py_d = int(alt * 0.70)
    panel_diag = pygame.Rect(px_d, py_d, pw_d, ph_d)
    w_dbtn = int(pw_d * 0.22)
    h_dbtn = int(ph_d * 0.35)
    btn_comprar_diag = pygame.Rect(panel_diag.right - int(pw_d * 0.04) - w_dbtn, panel_diag.top + int(ph_d * 0.12), w_dbtn, h_dbtn)
    btn_salir_diag = pygame.Rect(panel_diag.right - int(pw_d * 0.04) - w_dbtn, panel_diag.top + int(ph_d * 0.53), w_dbtn, h_dbtn)
    r_tit_diag = pygame.Rect(panel_diag.left + int(pw_d * 0.04), panel_diag.top + int(ph_d * 0.15), panel_diag.width - w_dbtn - int(pw_d * 0.08), int(ph_d * 0.30))
    r_cpo_diag = pygame.Rect(panel_diag.left + int(pw_d * 0.04), panel_diag.top + int(ph_d * 0.50), panel_diag.width - w_dbtn - int(pw_d * 0.08), int(ph_d * 0.35))

    res = {
        "dialogo": {
            "panel": panel_diag, "titulo": r_tit_diag, "texto": r_cpo_diag,
            "btn_comprar": btn_comprar_diag, "btn_salir": btn_salir_diag
        },
        "tienda": {
            "panel": panel_tienda, "titulo": r_titulo, "btn_volver": btn_volver,
            "tarjetas": tarjetas, "pesos": r_pesos, "total": r_total,
            "msg": r_msg, "btn_vaciar": btn_vaciar, "btn_comprar": btn_comprar
        },
        "panel_diag": panel_diag, "btn_comprar_diag": btn_comprar_diag, "btn_salir_diag": btn_salir_diag,
        "panel": panel_tienda, "titulo": r_titulo, "btn_volver": btn_volver, "tarjetas": tarjetas,
        "pesos": r_pesos, "total": r_total, "msg": r_msg, "btn_vaciar": btn_vaciar, "btn_comprar": btn_comprar
    }
    _CLAYTIEN[k] = res
    return res

def dibpanelmc(pant, rect, fill=(22, 22, 26, 230), b_ext=(198, 198, 198), b_int=(48, 48, 52)):
    dibrectalp(pant, fill, rect)
    pygame.draw.rect(pant, b_ext, rect, width=2)
    in_r = rect.inflate(-4, -4)
    if in_r.width > 0 and in_r.height > 0:
        pygame.draw.rect(pant, b_int, in_r, width=2)

def dibbtnmc(pant, rect, texto, hover=False, deshab=False, col_txt=None, tam=None):
    alt = pant.get_height()
    if deshab:
        bg = (50, 50, 55, 220)
        b_ext = (90, 90, 95)
        b_int = (35, 35, 40)
        t_col = (130, 130, 130)
    elif hover:
        bg = (100, 100, 115, 240)
        b_ext = (255, 255, 180)
        b_int = (65, 65, 75)
        t_col = (255, 255, 255)
    else:
        bg = (70, 70, 78, 230)
        b_ext = (180, 180, 185)
        b_int = (45, 45, 50)
        t_col = (230, 230, 230)

    if col_txt is not None:
        t_col = col_txt

    dibrectalp(pant, bg, rect)
    pygame.draw.rect(pant, b_ext, rect, width=2)
    in_r = rect.inflate(-4, -4)
    if in_r.width > 0 and in_r.height > 0:
        pygame.draw.rect(pant, b_int, in_r, width=1)

    if texto:
        t_tam = tam if tam is not None else tam_f(alt, 0.028, 12)
        tsurf = txtfit(t_tam, texto, t_col, max(8, rect.width - 8))
        pant.blit(tsurf, tsurf.get_rect(center=rect.center))

def dibtxtwrap(pant, rect, texto, tam, color=(200, 200, 205), max_lineas=3):
    f = fuente(tam)
    palabras = texto.split(" ")
    lineas = []
    actual = ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        w, _ = f.size(prueba)
        if w <= rect.width:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)

    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]

    lh = f.get_linesize()
    tot_h = len(lineas) * lh
    y_start = rect.top + (rect.height - tot_h) // 2
    for i, lin in enumerate(lineas):
        tsurf = txtfit(tam, lin, color, rect.width)
        pant.blit(tsurf, tsurf.get_rect(centerx=rect.centerx, top=y_start + i * lh))

_CICONSBAZ = {}

def cariconbaz(anc, alt, icons=None):
    k = (anc, alt)
    if k in _CICONSBAZ:
        return _CICONSBAZ[k]
    lay = laytienda(anc, alt)
    isz = lay["tarjetas"][0]["r_icon"].width
    b_icons = {}

    p_pist = os.path.join("Sprites", "Botones", "pistola.png")
    if os.path.exists(p_pist):
        img_p = pygame.image.load(p_pist).convert_alpha()
        br = img_p.get_bounding_rect()
        if br.width > 0 and br.height > 0:
            img_p = img_p.subsurface(br).copy()
        esc = min(isz / img_p.get_width(), isz / img_p.get_height())
        b_icons["pistola"] = pygame.transform.smoothscale(img_p, (max(1, int(img_p.get_width() * esc)), max(1, int(img_p.get_height() * esc))))
    else:
        b_icons["pistola"] = pygame.Surface((isz, isz), pygame.SRCALPHA)

    p_mol = os.path.join("Sprites", "Molotov", "molotov_icono.png")
    if os.path.exists(p_mol):
        img_m = pygame.image.load(p_mol).convert_alpha()
        br = img_m.get_bounding_rect()
        if br.width > 0 and br.height > 0:
            img_m = img_m.subsurface(br).copy()
        esc = min(isz / img_m.get_width(), isz / img_m.get_height())
        b_icons["molotov"] = pygame.transform.smoothscale(img_m, (max(1, int(img_m.get_width() * esc)), max(1, int(img_m.get_height() * esc))))
    else:
        b_icons["molotov"] = pygame.Surface((isz, isz), pygame.SRCALPHA)

    p_pan = os.path.join("Sprites", "Botones", "pancho.png")
    if os.path.exists(p_pan):
        img_pa = pygame.image.load(p_pan).convert_alpha()
        br = img_pa.get_bounding_rect()
        if br.width > 0 and br.height > 0:
            img_pa = img_pa.subsurface(br).copy()
        esc = min(isz / img_pa.get_width(), isz / img_pa.get_height())
        b_icons["pancho"] = pygame.transform.smoothscale(img_pa, (max(1, int(img_pa.get_width() * esc)), max(1, int(img_pa.get_height() * esc))))
    else:
        b_icons["pancho"] = pygame.Surface((isz, isz), pygame.SRCALPHA)

    if icons is not None and "speed_full" in icons:
        img_s = icons["speed_full"]
    else:
        r_spd = os.path.join("Sprites", "speed.png")
        img_s = _recfondo(r_spd) if os.path.exists(r_spd) else pygame.Surface((isz, isz), pygame.SRCALPHA)
    br = img_s.get_bounding_rect()
    if br.width > 0 and br.height > 0:
        img_s = img_s.subsurface(br).copy()
    esc = min(isz / img_s.get_width(), isz / img_s.get_height())
    b_icons["speed"] = pygame.transform.smoothscale(img_s, (max(1, int(img_s.get_width() * esc)), max(1, int(img_s.get_height() * esc))))

    _CICONSBAZ[k] = b_icons
    return b_icons

def dibdiagbaz(pant, lay, mouse):
    alt = pant.get_height()
    d = lay["dialogo"]
    dibpanelmc(pant, d["panel"])

    t_tit = txtfit(tam_f(alt, 0.038, 16), "ANDY EL MAGO:", (255, 215, 0), d["titulo"].width)
    pant.blit(t_tit, t_tit.get_rect(midleft=(d["titulo"].left, d["titulo"].centery)))

    t_cpo = txtfit(tam_f(alt, 0.026, 12), "BIENVENIDO A MI BAZAR. QUE DESEA HACER?", (235, 235, 235), d["texto"].width)
    pant.blit(t_cpo, t_cpo.get_rect(midleft=(d["texto"].left, d["texto"].centery)))

    dibbtnmc(pant, d["btn_comprar"], "COMPRAR", hover=d["btn_comprar"].collidepoint(mouse))
    dibbtnmc(pant, d["btn_salir"], "SALIR", hover=d["btn_salir"].collidepoint(mouse))

def dibtienda(pant, lay, jdat, car, mouse, icons_baz, msg_comp=""):
    alt = pant.get_height()
    t = lay["tienda"]
    dibpanelmc(pant, t["panel"])

    # Titulo y Volver
    t_tit = txtfit(tam_f(alt, 0.040, 16), "BAZAR DE ANDY", (255, 215, 0), t["titulo"].width)
    pant.blit(t_tit, t_tit.get_rect(center=t["titulo"].center))
    dibbtnmc(pant, t["btn_volver"], "VOLVER", hover=t["btn_volver"].collidepoint(mouse))

    # Tarjetas
    for c in t["tarjetas"]:
        cid = c["id"]
        cr = c["rect"]
        is_hov = cr.collidepoint(mouse)
        pist_comp = (cid == "pistola" and jdat.get("pistola", False))
        en_car = car.get(cid, 0) > 0

        if pist_comp:
            fill = (18, 18, 20, 225)
            b_ext = (75, 75, 80)
            b_int = (35, 35, 40)
        elif en_car:
            fill = (24, 34, 26, 235)
            b_ext = (80, 220, 100)
            b_int = (35, 70, 40)
        elif is_hov:
            fill = (32, 32, 38, 235)
            b_ext = (255, 255, 180)
            b_int = (65, 65, 75)
        else:
            fill = (24, 24, 28, 225)
            b_ext = (140, 140, 145)
            b_int = (45, 45, 50)
        dibpanelmc(pant, cr, fill=fill, b_ext=b_ext, b_int=b_int)

        # Nombre
        col_nom = (160, 160, 165) if pist_comp else (255, 255, 255)
        tnom = txtfit(tam_f(alt, 0.028, 12), c["nombre"], col_nom, c["r_nom"].width)
        pant.blit(tnom, tnom.get_rect(center=c["r_nom"].center))

        # Precio
        if pist_comp:
            tpre = txtfit(tam_f(alt, 0.026, 12), "AGOTADO", (140, 140, 140), c["r_precio"].width)
        else:
            p_str = f"${c['precio']}" if cid == "pistola" else f"${c['precio']} c/u"
            tpre = txtfit(tam_f(alt, 0.026, 12), p_str, (255, 225, 90), c["r_precio"].width)
        pant.blit(tpre, tpre.get_rect(center=c["r_precio"].center))

        # Icono
        ic = icons_baz.get(cid)
        if ic is not None:
            ric = ic.get_rect(center=c["r_icon"].center)
            if pist_comp:
                ic_d = ic.copy()
                ic_d.fill((100, 100, 100, 255), special_flags=pygame.BLEND_RGBA_MULT)
                pant.blit(ic_d, ric)
            else:
                pant.blit(ic, ric)

        # Descripcion multilinea
        col_desc = (140, 140, 145) if pist_comp else (205, 205, 210)
        dibtxtwrap(pant, c["r_desc"], c["desc"], tam_f(alt, 0.020, 10), color=col_desc)

        # Tienes
        if cid == "pistola":
            t_ten_str = "Tienes: SI" if jdat.get("pistola", False) else "Tienes: NO"
        elif cid == "molotov":
            t_ten_str = f"Tienes: {jdat.get('molotovs', 0)}"
        elif cid == "pancho":
            t_ten_str = f"Tienes: {jdat.get('panchos', 0)}"
        elif cid == "speed":
            t_ten_str = f"Tienes: {jdat.get('spds', 0)}"
        col_ten = (140, 170, 190) if pist_comp else (180, 215, 240)
        tten = txtfit(tam_f(alt, 0.022, 10), t_ten_str, col_ten, c["r_tenes"].width)
        pant.blit(tten, tten.get_rect(center=c["r_tenes"].center))

        # Botones / Badge
        if pist_comp:
            r_badge_c = c["btn_menos"].union(c["btn_mas"])
            dibrectalp(pant, (35, 30, 20, 220), r_badge_c)
            pygame.draw.rect(pant, (150, 120, 50), r_badge_c, width=1)
            t_comp = txtfit(tam_f(alt, 0.024, 10), "COMPRADA", (255, 200, 80), r_badge_c.width - 6)
            pant.blit(t_comp, t_comp.get_rect(center=r_badge_c.center))
        else:
            dibbtnmc(pant, c["btn_menos"], "-", hover=c["btn_menos"].collidepoint(mouse))

            cnt = car.get(cid, 0)
            col_cnt = (80, 255, 100) if cnt > 0 else (140, 140, 145)
            dibrectalp(pant, (15, 15, 20, 220), c["r_badge"])
            pygame.draw.rect(pant, (70, 70, 75), c["r_badge"], width=1)
            t_cnt = txtfit(tam_f(alt, 0.026, 12), f"x{cnt}", col_cnt, c["r_badge"].width - 4)
            pant.blit(t_cnt, t_cnt.get_rect(center=c["r_badge"].center))

            dibbtnmc(pant, c["btn_mas"], "+", hover=c["btn_mas"].collidepoint(mouse))

    # Panel inferior
    ctot = (PRE_PIST if car.get("pistola", 0) else 0) + car.get("molotov", 0) * PRE_MOL + car.get("pancho", 0) * PRE_PAN + car.get("speed", 0) * PRE_SPD
    tpesos = txtfit(tam_f(alt, 0.030, 14), f"Tus pesos: ${jdat['pesos']}", (255, 255, 255), t["pesos"].width)
    pant.blit(tpesos, tpesos.get_rect(midleft=(t["pesos"].left, t["pesos"].centery)))

    col_tot = (255, 110, 110) if ctot > jdat["pesos"] else (120, 255, 140)
    ttot = txtfit(tam_f(alt, 0.030, 14), f"Total carrito: ${ctot}", col_tot, t["total"].width)
    pant.blit(ttot, ttot.get_rect(midleft=(t["total"].left, t["total"].centery)))

    if msg_comp:
        es_err = any(msg_comp.startswith(pfx) for pfx in ("Necesitas", "Selecciona", "Toca", "Ya ", "Maximo"))
        col_m = (255, 120, 120) if es_err else (130, 255, 130)
        t_m = txtfit(tam_f(alt, 0.026, 12), msg_comp, col_m, t["msg"].width - 12)
        rm = t_m.get_rect(center=t["msg"].center)
        dibrectalp(pant, (15, 15, 20, 220), rm.inflate(16, 10))
        pygame.draw.rect(pant, (70, 70, 75), rm.inflate(16, 10), width=1)
        pant.blit(t_m, rm)

    hay_items = any(v > 0 for v in car.values())
    dibbtnmc(pant, t["btn_vaciar"], "VACIAR", hover=t["btn_vaciar"].collidepoint(mouse) and hay_items, deshab=not hay_items)
    dibbtnmc(pant, t["btn_comprar"], "COMPRAR", hover=t["btn_comprar"].collidepoint(mouse))

def cargarmira(alt):
    if alt in _CMIRA:
        return _CMIRA[alt]
    img = pygame.image.load(os.path.join("Sprites", "Botones", "mira.png")).convert_alpha()
    img.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGB_ADD)
    tam = max(32, int(alt * 0.055))
    res = pygame.transform.scale(img, (tam, tam))
    _CMIRA[alt] = res
    return res

def cariconos(alt):
    icons = {}
    tam = max(28, int(alt * 0.045))
    for nom in ("pancho", "peso"):
        img = pygame.image.load(f"Sprites/Botones/{nom}.png").convert_alpha()
        esc = tam / img.get_height()
        icons[nom] = pygame.transform.smoothscale(img, (int(img.get_width() * esc), tam))

    ruta_spd = "Sprites/speed.png" if os.path.exists("Sprites/speed.png") else "speed.png"
    img_spd = _recfondo(ruta_spd)
    esc_spd = tam / img_spd.get_height()
    icons["speed"] = pygame.transform.smoothscale(img_spd, (max(12, int(img_spd.get_width() * esc_spd)), tam))
    icons["speed_full"] = img_spd
    return icons

def dibrecur(pant, icons, pesos):
    alt = pant.get_height()
    f = fuente(tam_f(alt, 0.035, 16))
    tpes = f.render(str(pesos), False, (255, 255, 255))
    marg = max(12, int(alt * 0.02))
    esp = max(6, int(alt * 0.01))
    der = pant.get_width() - marg
    rtpes = tpes.get_rect(midright=(der - esp, marg + icons["peso"].get_height() // 2))
    rpes = icons["peso"].get_rect(midright=(rtpes.left - esp, rtpes.centery))
    fondo = rpes.union(rtpes).inflate(esp * 3, esp * 2)
    dibrectalp(pant, (0, 0, 0, 170), fondo, border_radius=5)
    pant.blit(icons["peso"], rpes)
    pant.blit(tpes, rtpes)

NOM_SLOT = ("PUÑO", "PISTOLA", "MOLOTOV", "PANCHO", "SPEED")
_CHB = {}

def geomhotbar(anc, alt):
    s = max(40, int(round(alt * 0.075 / 4.0)) * 4)
    gap = max(4, int(alt * 0.006))
    x0 = (anc - (s * 5 + gap * 4)) // 2
    y = alt - s - max(8, int(alt * 0.02))
    return [pygame.Rect(x0 + i * (s + gap), y, s, s) for i in range(5)]

def carhotbar(alt, icons):
    if alt in _CHB:
        return _CHB[alt]
    inner = int(geomhotbar(alt, alt)[0].width * 0.72)
    rutas = [
        os.path.join("Sprites", "Botones", "puno_icono.png"),
        os.path.join("Sprites", "Botones", "pistola.png"),
        os.path.join("Sprites", "Molotov", "molotov_icono.png"),
        os.path.join("Sprites", "Botones", "pancho.png"),
        None,
    ]
    nor, dim = [], []
    for ruta in rutas:
        img = icons["speed_full"] if ruta is None else pygame.image.load(ruta).convert_alpha()
        br = img.get_bounding_rect()
        if br.width > 0 and br.height > 0:
            img = img.subsurface(br).copy()
        esc = inner / max(img.get_width(), img.get_height())
        img = pygame.transform.smoothscale(img, (max(1, int(img.get_width() * esc)), max(1, int(img.get_height() * esc))))
        d = img.copy()
        d.fill((85, 85, 85, 255), special_flags=pygame.BLEND_RGBA_MULT)
        nor.append(img)
        dim.append(d)
    _CHB[alt] = {"n": nor, "dim": dim}
    return _CHB[alt]

def slots_disp(jdat):
    return [1] + ([2] if jdat.get("pistola") else []) + [3]

def selslot(jdat, n, ahora=None):
    if n not in slots_disp(jdat):
        return False
    if ahora is None:
        ahora = pygame.time.get_ticks()
    jdat["slot"] = n
    jdat["slot_msg"] = NOM_SLOT[n - 1]
    jdat["slot_msg_hasta"] = ahora + 1500
    return True

def ciclarslot(jdat, paso, ahora=None):
    d = slots_disp(jdat)
    i = d.index(jdat.get("slot", 1)) if jdat.get("slot", 1) in d else 0
    return selslot(jdat, d[(i + paso) % len(d)], ahora)

def slot_en(anc, alt, pos):
    for i, r in enumerate(geomhotbar(anc, alt)):
        if r.collidepoint(pos):
            return i + 1
    return None

def accionclic(jdat):
    s = jdat.get("slot", 1)
    if s == 2:
        return "disparo" if jdat.get("pistola") else "golpe"
    if s == 3:
        return "molotov"
    return "golpe"

def usarpancho(jdat):
    if jdat.get("panchos", 0) > 0 and jdat["vida"] < 5:
        jdat["panchos"] -= 1
        jdat["vida"] = 5
        jdat["daño_acum"] = 0.0
        guardjdat(jdat)
        return "Vida restaurada"
    if jdat["vida"] >= 5:
        return "Vida completa"
    return "No tienes panchos"

def usarspeed(jdat):
    if jdat.get("spds", 0) > 0 and jdat.get("escudo", 0) < 3:
        jdat["spds"] -= 1
        jdat["escudo"] = min(3, jdat.get("escudo", 0) + 1)
        guardjdat(jdat)
        return "+1 Barra de Escudo"
    if jdat.get("escudo", 0) >= 3:
        return "Escudo al maximo"
    return "No tienes Speed"

def disppist(jdat, dest, mapa):
    # En mapa 1 se dispara gratis (sin gastar balas ni iniciar recarga)
    if not jdat.get("pistola"):
        return None
    if mapa == 2 and jdat.get("balas", 0) <= 0:
        return None
    p = proypist(jdat, dest)
    if p is not None and mapa == 2:
        jdat["balas"] -= 1
        if jdat["balas"] == 0:
            jdat["rec_hasta"] = pygame.time.get_ticks() + 2000
    return p

def dibhotbar(pant, hb, jdat, bmax=10):
    anc, alt = pant.get_size()
    ahora = pygame.time.get_ticks()
    rs = geomhotbar(anc, alt)
    sel = jdat.get("slot", 1)
    pist = bool(jdat.get("pistola"))
    cants = [None, f"{jdat.get('balas', bmax)}/{bmax}" if pist else None,
             str(jdat.get("molotovs", 0)), str(jdat.get("panchos", 0)), str(jdat.get("spds", 0))]
    libre = [True, pist, jdat.get("molotovs", 0) > 0, jdat.get("panchos", 0) > 0, jdat.get("spds", 0) > 0]
    s = rs[0].width
    gb = max(2, s // 28)
    bh = max(4, s // 12)
    for i, r in enumerate(rs):
        dibrectalp(pant, (0, 0, 0, 150), r)
        ic = hb["n"][i] if libre[i] else hb["dim"][i]
        pant.blit(ic, ic.get_rect(center=r.center))
        pygame.draw.rect(pant, (255, 255, 255) if i + 1 == sel else (170, 170, 170), r, gb * 2 if i + 1 == sel else gb)
        tn = fuente(tam_f(alt, 0.02, 12)).render(("1", "2", "3", "E", "Q")[i], False, (210, 210, 210))
        pant.blit(tn, (r.x + gb * 2 + 1, r.y + gb * 2))
        yb = r.bottom - gb * 2
        if i == 1 and pist:
            rec = jdat.get("rec_hasta", 0)
            if rec > ahora:
                fr, col = max(0.0, min(1.0, 1.0 - (rec - ahora) / 2000.0)), (90, 170, 255)
            elif jdat.get("balas", bmax) < bmax:
                fr = max(0.0, min(1.0, jdat.get("balas", bmax) / max(1, bmax)))
                col = (90, 220, 110) if fr > 0.5 else ((255, 215, 60) if fr > 0.25 else (235, 65, 65))
            else:
                fr = None
            if fr is not None:
                rb = pygame.Rect(r.x + gb * 2, r.bottom - gb * 2 - bh, s - gb * 4, bh)
                pygame.draw.rect(pant, (0, 0, 0), rb)
                pygame.draw.rect(pant, col, pygame.Rect(rb.x, rb.y, int(rb.width * fr), rb.height))
                yb = rb.top - 1
        if i == 2:
            cd_h = jdat.get("cd_mol_hasta", 0)
            if cd_h > ahora:
                cd_d = max(1, jdat.get("cd_mol_dur", BAL_MOL["cd_ms"]))
                fr_rest = max(0.0, min(1.0, (cd_h - ahora) / cd_d))
                hov = max(1, int((s - gb * 2) * fr_rest))
                dibrectalp(pant, (10, 10, 14, 165), pygame.Rect(r.x + gb, r.bottom - gb - hov, s - gb * 2, hov))
                rb = pygame.Rect(r.x + gb * 2, r.bottom - gb * 2 - bh, s - gb * 4, bh)
                pygame.draw.rect(pant, (0, 0, 0), rb)
                pygame.draw.rect(pant, (255, 150, 45), pygame.Rect(rb.x, rb.y, int(rb.width * (1.0 - fr_rest)), rb.height))
                yb = rb.top - 1
        if cants[i] is not None:
            tc = fuente(tam_f(alt, 0.024, 12))
            mw = s - gb * 4
            tx = txtfit(tc.tam, cants[i], (255, 255, 255), mw)
            sh = txtfit(tc.tam, cants[i], (0, 0, 0), mw)
            rt = tx.get_rect(bottomright=(r.right - gb * 2, yb))
            pant.blit(sh, rt.move(2, 2))
            pant.blit(tx, rt)
    msg, col = None, (255, 255, 255)
    if sel == 3 and jdat.get("molotovs", 0) <= 0:
        msg, col = "SIN MOLOTOVS", (255, 90, 90)
    elif ahora < jdat.get("slot_msg_hasta", 0):
        msg = jdat.get("slot_msg", "")
    if msg:
        mw = rs[-1].right - rs[0].left
        tm = fuente(tam_f(alt, 0.03, 16)).tam
        t1 = txtfit(tm, msg, col, mw)
        t2 = txtfit(tm, msg, (0, 0, 0), mw)
        rm = t1.get_rect(midbottom=(rs[2].centerx, rs[0].top - max(6, int(alt * 0.012))))
        pant.blit(t2, rm.move(2, 2))
        pant.blit(t1, rm)

def diboleada(pant, ole, enes=None, jdat=None):
    alt = pant.get_height()
    anc = pant.get_width()
    f = fuente(tam_f(alt, 0.045, 16))
    fch = fuente(tam_f(alt, 0.028, 12))

    marg = max(12, int(alt * 0.02))
    inf = jdat.get("ole_inf") if jdat else None
    cola_len = len(inf["cola"]) if inf else 0
    vivos = len([e for e in (enes or []) if e.get("vida", 0) > 0])
    pts = jdat.get("puntos", 0) if jdat else 0

    txt = f.render(f"Oleada {ole}", False, (255, 255, 255))
    sub_txt = f"Restantes: {cola_len + vivos}  |  Puntos: {pts}" if enes is not None else f"Puntos: {pts}"
    sub = txtfit(fch.tam, sub_txt, (215, 215, 215), int(anc * 0.4))

    rt = txt.get_rect(topleft=(marg * 2, marg))
    rs = sub.get_rect(topleft=(marg * 2, rt.bottom + 2))
    fondo = rt.union(rs).inflate(marg * 2, marg)
    dibrectalp(pant, (0, 0, 0, 175), fondo, border_radius=6)
    pant.blit(txt, rt)
    pant.blit(sub, rs)

    banner = jdat.get("banner") if jdat else None
    if banner:
        ahora = pygame.time.get_ticks()
        trans = ahora - banner["inicio"]
        dur = max(1, banner["dur"])
        if 0 <= trans < dur:
            tb = tam_f(alt, 0.085, 24)
            alfa = int(255 * max(0.0, min(1.0, trans / 280.0, (dur - trans) / 450.0)))
            mw = int(anc * 0.92)
            imgb = txtfit(tb, banner["texto"], (255, 215, 60), mw)
            somb = txtfit(tb, banner["texto"], (0, 0, 0), mw)
            imgb.set_alpha(alfa)
            somb.set_alpha(alfa)
            rb = imgb.get_rect(center=(anc // 2, int(alt * 0.24)))
            pant.blit(somb, rb.move(3, 3))
            pant.blit(imgb, rb)
            if banner.get("sub"):
                isub = txtfit(f.tam, banner["sub"], (255, 255, 255), mw)
                ssub = txtfit(f.tam, banner["sub"], (0, 0, 0), mw)
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
        sprs[d] = [pygame.transform.scale(pygame.image.load(os.path.join("Sprites", "Mc", f"MC{n:03d}.png")).convert_alpha(), (wj, hj)) for n in nums]
    return sprs

def carsprat(wj, hj):
    dic = {
        "abajo": [0, 1, 2, 3],
        "arriba": [4, 5, 6, 7],
        "izquierda": [8, 9, 10, 11],
        "derecha": [12, 13, 14, 15]
    }
    sprs = {}
    for d, nums in dic.items():
        sprs[d] = [pygame.transform.scale(pygame.image.load(os.path.join("Sprites", "Mc", "Ataque_Mc", f"AMC{n:03d}.png")).convert_alpha(), (wj, hj)) for n in nums]
    return sprs

def carsprdash(hj):
    der = []
    izq = []
    for i in range(8):
        img = pygame.image.load(os.path.join("Sprites", "Mc", "Dash_Normal", f"dash_{i:02d}.png")).convert_alpha()
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
    if (anc, alt) not in _CESCJUG:
        hj1 = int(alt * 0.1125)
        wj1 = int(hj1 * (52 / 96))
        v1 = int(alt * 0.0085)

        sprs1 = cargarsprs(wj1, hj1)
        sprat1 = carsprat(wj1, hj1)
        sprd1 = carsprdash(hj1)
        sprr1 = {d: [rojospr(s) for s in lst] for d, lst in sprs1.items()}
        spratr1 = {d: [rojospr(s) for s in lst] for d, lst in sprat1.items()}

        hj2 = int(alt * 0.075)
        wj2 = int(hj2 * (52 / 96))
        v2 = max(2, int(alt * 0.007))
        sprs2 = cargarsprs(wj2, hj2)
        sprat2 = carsprat(wj2, hj2)
        sprd2 = carsprdash(hj2)
        sprr2 = {d: [rojospr(s) for s in lst] for d, lst in sprs2.items()}
        spratr2 = {d: [rojospr(s) for s in lst] for d, lst in sprat2.items()}

        _CESCJUG[(anc, alt)] = {
            1: {"w": wj1, "h": hj1, "vel": v1, "sprs": sprs1, "sprrojos": sprr1, "sprataq": sprat1, "sprataqrojos": spratr1, "sprdash": sprd1},
            2: {"w": wj2, "h": hj2, "vel": v2, "sprs": sprs2, "sprrojos": sprr2, "sprataq": sprat2, "sprataqrojos": spratr2, "sprdash": sprd2},
        }
        precmol(alt)

    escalas = _CESCJUG[(anc, alt)]
    e1 = escalas[1]
    r1 = pygame.Rect(anc // 2, int(alt * 0.50), e1["w"], e1["h"])

    return {
        "rect": r1,
        "hitbox": creahit(e1["sprs"]["abajo"][0], r1.topleft),
        "vel": e1["vel"],
        "sprs": e1["sprs"],
        "sprrojos": e1["sprrojos"],
        "sprataq": e1["sprataq"],
        "sprataqrojos": e1["sprataqrojos"],
        "sprdash": e1["sprdash"],
        "_escalas": escalas,
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
        "cd_mol_hasta": 0,
        "cd_mol_dur": BAL_MOL["cd_ms"],
        "zonas_fuego": [],
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
        "panchos": 0,
        "spds": 0,
        "pistola": False,
        "oleada": 1,
        "mapa": 1,
        "slot": 1,
        "molotovs": 0,
        "slot_msg": "",
        "slot_msg_hasta": 0,
        "balas": 10,
        "bmax": 10,
        "rec_hasta": 0,
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
    jdat["zonas_fuego"] = []
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
    if obs_l is None:
        obs_l = obstaculos(mapa, anc, alt)

    desatascar(jdat, anc, alt, obs_l)
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

        if dx != 0 and dy != 0:
            mag = math.hypot(dx, dy)
            dx = round((dx / mag) * v_act)
            dy = round((dy / mag) * v_act)

    _movpaso(r, dx, dy, anc, alt, obs_l)

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

def _icondrops(alt_p):
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

def dibprevmol(pant, jdat, mmundo, anc_m, alt_m, obs_l=None, cam=(0, 0)):
    if jdat is None or jdat.get("slot") != 3:
        return None
    obs_l = _resolvobs(anc_m, alt_m, obs_l=obs_l, mapa=2, ent=jdat)
    tx, ty = destmol(jdat, mmundo, anc_m, alt_m, obs_l=obs_l, mapa=2)
    rad = max(24, int(round(jdat["hitbox"].height * BAL_MOL["radio_mult"])))
    sx = int(tx - cam[0])
    sy = int(ty - cam[1])
    ahora = pygame.time.get_ticks()
    listo = jdat.get("molotovs", 0) > 0 and ahora >= jdat.get("cd_mol_hasta", 0)
    surf = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
    c = (rad + 2, rad + 2)
    col_fill = (255, 150, 40, 46) if listo else (180, 80, 60, 28)
    col_borde = (255, 195, 75, 135) if listo else (200, 100, 80, 95)
    pygame.draw.circle(surf, col_fill, c, rad)
    pygame.draw.circle(surf, col_borde, c, rad, 2)
    pygame.draw.circle(surf, col_borde, c, 4, 1)
    pant.blit(surf, (sx - rad - 2, sy - rad - 2))
    return (tx, ty, rad)

def dibjuego(pant, mgraf, jdat, vidas, objs, mvida=True, proys=None, cam=(0, 0), escudos=None, mouse=None):
    ahora = pygame.time.get_ticks()
    alt_p = pant.get_height()
    cx, cy = cam
    if ahora < jdat.get("shake_hasta", 0):
        cx += random.randint(-5, 5)
        cy += random.randint(-5, 5)

    pant.blit(mgraf, (-cx, -cy))
    icondrops, balasrot = _icondrops(alt_p)

    if mouse is not None and jdat.get("slot") == 3 and jdat.get("mapa_esc") == 2:
        dibprevmol(pant, jdat, (mouse[0] + cx, mouse[1] + cy), mgraf.get_width(), mgraf.get_height(), cam=(cx, cy))

    bm = BAL_MOL
    for z in jdat.get("zonas_fuego", []):
        edad = max(0, ahora - z["inicio"])
        rest = z["dur"] - edad
        if rest <= 0:
            continue
        rz = z["radio"]
        sx = int(z["x"] - cx)
        sy = int(z["y"] - cy)
        alpha = 255 if rest >= bm["fade_ms"] else max(0, min(255, int(255 * (rest / max(1, bm["fade_ms"])))))
        if alpha <= 0:
            continue
        glow = pygame.Surface((rz * 2 + 4, rz * 2 + 4), pygame.SRCALPHA)
        cg = (rz + 2, rz + 2)
        pygame.draw.circle(glow, (255, 105, 20, int(60 * alpha / 255)), cg, rz)
        pygame.draw.circle(glow, (255, 175, 55, int(125 * alpha / 255)), cg, rz, 2)
        pant.blit(glow, (sx - rz - 2, sy - rz - 2))
        frames_f = _fuegofr(rz * 2)
        spr_f = frames_f[(edad // bm["fra_fuego_ms"]) % len(frames_f)]
        if alpha < 255:
            spr_f = spr_f.copy()
            spr_f.set_alpha(alpha)
        pant.blit(spr_f, spr_f.get_rect(center=(sx, sy)))

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

    fent = fuente(tam_f(alt_p, 0.025, 12))

    for _, tent, o in ents:
        if tent == "rect":
            pygame.draw.rect(pant, (120, 55, 35), o.move(-cx, -cy), border_radius=6)
        elif tent == "enemigo":
            dibsombra(pant, o["rect"].centerx - cx, o["rect"].bottom - cy, o["rect"].width * 0.85)
            in_windup = o.get("tipo") == "barracas" and o.get("ataq") and not o.get("golpe_hecho", False)
            if o["ataq"]:
                spr = (o["sprataqrojos"] if ahora < o["golpe_hasta"] else o["sprataq"])[o["dir"]][o["fraataq"]]
                if in_windup and (ahora // 75) % 2 == 0:
                    spr = blancsurf(spr)
            else:
                spr = (o["sprrojos"] if ahora < o["golpe_hasta"] else o["sprs"])[o["dir"]][int(o["frame"]) % 3]
            rx = o["rect"].x - cx
            ry = o["rect"].y - cy
            pant.blit(spr, (rx, ry))
            if in_windup:
                # Señal visual clara de telegrafiado sobre la cabeza
                mx_w = int(o["rect"].centerx - cx)
                my_w = int(ry - 14)
                pygame.draw.circle(pant, (255, 220, 40), (mx_w, my_w), 7)
                pygame.draw.circle(pant, (200, 30, 20), (mx_w, my_w), 7, 2)
                lblw = fent.render("!", False, (20, 20, 20))
                pant.blit(lblw, lblw.get_rect(center=(mx_w, my_w)))

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
                    lblj = fent.render("EL JEFE", False, (255, 215, 60))
                    somj = fent.render("EL JEFE", False, (0, 0, 0))
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
        if p.get("es_molotov"):
            ay = int(round(p.get("arco_y", 0.0)))
            amax = max(1.0, p.get("arco_max", 36.0))
            esc_s = max(0.55, 0.95 - 0.35 * (ay / amax))
            dibsombra(pant, rp.centerx, rp.centery, p["rect"].width * esc_s)
            rots = _molrot(p.get("tam", p["rect"].width))
            s_mol = rots[round(p.get("angulo", 0.0) / 5.0) % 72]
            pant.blit(s_mol, s_mol.get_rect(center=(rp.centerx, rp.centery - ay)))
        elif p.get("lado") == "pistola" and "angulo" in p:
            s_bala = balasrot[round(p["angulo"] / 5) % 72]
            pant.blit(s_bala, s_bala.get_rect(center=rp.center))
        elif p.get("es_piedra"):
            img_p = _obtpiedra()
            if img_p is not None:
                pant.blit(img_p, img_p.get_rect(center=rp.center))
            else:
                pygame.draw.ellipse(pant, (140, 130, 120), rp)
                pygame.draw.ellipse(pant, (35, 30, 25), rp, 1)
        else:
            col = (255, 230, 90) if p.get("lado") == "pistola" else ((235, 85, 75) if p.get("lado") == "enemigo" else (250, 250, 150))
            pygame.draw.ellipse(pant, col, rp)
            pygame.draw.ellipse(pant, (35, 30, 20), rp, 1)

    for c in jdat.get("chispas", []):
        pygame.draw.circle(pant, c["color"], (int(c["x"] - cx), int(c["y"] - cy)), c["radio"])

    for t in jdat.get("textos", []):
        it = fent.render(t["texto"], False, t["color"])
        st = fent.render(t["texto"], False, (0, 0, 0))
        rt = it.get_rect(midbottom=(int(t["x"] - cx), int(t["y"] - cy)))
        pant.blit(st, rt.move(1, 1))
        pant.blit(it, rt)

    if mvida:
        dibvida(pant, vidas, jdat, escudos=escudos)
