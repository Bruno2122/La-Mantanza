import pygame
import cv2
import os

# C
def ccontinuara(ancho, alto):
    ruta = "F/Continuara....png" if os.path.exists("F/Continuara....png") else "Continuara....png"
    img = pygame.image.load(ruta).convert()
    return pygame.transform.scale(img, (ancho, alto))

def dcontinuara(pantalla, imagen):
    pantalla.blit(imagen, (0, 0))
# C

def cargarvidas(alto):
    vidas = []
    altovida = int(alto * 0.14)
    for numero in range(6):
        ruta = f"Sprites/Vida/vida{numero:02d}.png"
        img = pygame.image.load(ruta).convert_alpha()
        proporcion = img.get_width() / img.get_height()
        vidas.append(pygame.transform.scale(img, (int(altovida * proporcion), altovida)))
    return vidas

def dibujarvida(pantalla, vidas, jugdatos):
    vida = max(0, min(jugdatos["vida"], 5))
    spritevida = 5 - vida
    rectvida = vidas[spritevida].get_rect(bottomleft=(0, pantalla.get_height()))
    pantalla.blit(vidas[spritevida], rectvida)

def recibirdaño(jugdatos, objetivos):
    ahora = pygame.time.get_ticks()
    if ahora - jugdatos["ultimo_daño"] < 1000:
        return

    for objetivo in objetivos:
        if jugdatos["rect"].colliderect(objetivo):
            jugdatos["vida"] = max(0, jugdatos["vida"] - 1)
            jugdatos["ultimo_daño"] = ahora
            return

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

def dibujarperdida(pantalla, jugdatos, mapagraf, fuentetitulo, fuente, botones, mouse):
    dibujarjuego(pantalla, mapagraf, jugdatos, [], [], False)

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
        {"texto": "AJUSTES", "rect": pygame.Rect(posx, posy + espacio, anchobtn, altobtn), "accion": "ajustes"},
        {"texto": "SALIR", "rect": pygame.Rect(posx, posy + espacio * 2, anchobtn, altobtn), "accion": "salir"}
    ]

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
    ruta = "F/mapa.jpg" if os.path.exists("F/mapa.jpg") else "mapa.jpg"
    img = pygame.image.load(ruta)
    return pygame.transform.scale(img, (ancho, alto)).convert()

def cargarmapa2(ancho, alto):
    ruta = "F/mapa2.png" if os.path.exists("F/mapa2.png") else "mapa2.png"
    img = pygame.image.load(ruta)
    return pygame.transform.scale(img, (ancho, alto)).convert()

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

def crearjugador(ancho, alto):
    hjug = int(alto * 0.15)
    wjug = int(hjug * (52 / 96))
    xjug = 0
    yjug = int(alto * 0.50)
    rectjug = pygame.Rect(xjug, yjug, wjug, hjug)
    vel = int(alto * 0.009)
    sprs = cargarsprites(wjug, hjug)

    jugdatos = {
        "rect": rectjug,
        "vel": vel,
        "sprs": sprs,
        "dir": "abajo",
        "frame": 1.0,
        "vida": 5,
        "ultimo_daño": -1000
    }
    return jugdatos

def moverjugador(jugdatos, teclas, ancho, alto):
    rect = jugdatos["rect"]
    vel = jugdatos["vel"]
    mov = False

    if teclas[pygame.K_w] or teclas[pygame.K_UP]:
        rect.y -= vel
        jugdatos["dir"] = "arriba"
        mov = True
    elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
        rect.y += vel
        jugdatos["dir"] = "abajo"
        mov = True

    if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
        rect.x -= vel
        jugdatos["dir"] = "izquierda"
        mov = True
    elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
        rect.x += vel
        jugdatos["dir"] = "derecha"
        mov = True

    limitesuperior = int(alto * 0.40)
    limiteinferior = int(alto * 0.73)

    if rect.bottom < limitesuperior:
        rect.bottom = limitesuperior
    if rect.bottom > limiteinferior:
        rect.bottom = limiteinferior
    if rect.left < 0:
        rect.left = 0
    if rect.right > ancho:
        rect.right = ancho

    if mov:
        jugdatos["frame"] = (jugdatos["frame"] + 0.15) % 4
    else:
        jugdatos["frame"] = 1.0

def dibujarjuego(pantalla, mapagraf, jugdatos, vidas, objetivos, mostrarvida=True):
    pantalla.blit(mapagraf, (0, 0))
    for objetivo in objetivos:
        pygame.draw.rect(pantalla, (120, 55, 35), objetivo, border_radius=6)
    d = jugdatos["dir"]
    secuencia = [0, 1, 2, 1]
    idx = secuencia[int(jugdatos["frame"]) % 4]
    spr = jugdatos["sprs"][d][idx]
    pantalla.blit(spr, jugdatos["rect"].topleft)
    if mostrarvida:
        dibujarvida(pantalla, vidas, jugdatos)
def dibujarjuego2(pantalla, mapagraf, jugdatos, vidas, mostrarvida=True):
    pantalla.blit(mapagraf, (0, 0))
    d = jugdatos["dir"]
    secuencia = [0, 1, 2, 1]
    idx = secuencia[int(jugdatos["frame"]) % 4]
    spr = jugdatos["sprs"][d][idx]
    pantalla.blit(spr, jugdatos["rect"].topleft)
    if mostrarvida:
        dibujarvida(pantalla, vidas, jugdatos)
