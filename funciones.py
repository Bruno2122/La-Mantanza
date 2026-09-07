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
    hjug = int(alto * 0.18)
    wjug = int(hjug * (68 / 96))
    xjug = ancho // 2
    yjug = int(alto * 0.50)
    rectjug = pygame.Rect(xjug, yjug, wjug, hjug)
    vel = int(alto * 0.009)
    sprs = cargarsprites(wjug, hjug)

    jugdatos = {
        "rect": rectjug,
        "vel": vel,
        "sprs": sprs,
        "dir": "abajo",
        "frame": 1.0
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

def dibujarjuego(pantalla, mapagraf, jugdatos):
    pantalla.blit(mapagraf, (0, 0))
    d = jugdatos["dir"]
    secuencia = [0, 1, 2, 1]
    idx = secuencia[int(jugdatos["frame"]) % 4]
    spr = jugdatos["sprs"][d][idx]
    pantalla.blit(spr, jugdatos["rect"].topleft)
