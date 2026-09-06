import pygame
import cv2

def capas(ancho, alto, anchopanel):
    panelizq = pygame.Surface((anchopanel, alto))
    panelizq.fill((0, 0, 0))
    panelizq.set_alpha(170)

    panelder = pygame.Surface((ancho - anchopanel, alto))
    panelder.fill((0, 0, 0))
    panelder.set_alpha(128)

    return panelizq, panelder

def fuentes(alto):
    fuentetit = pygame.font.Font("minecraft.ttf", int(alto * 0.065))
    fuentebtn = pygame.font.Font("minecraft.ttf", int(alto * 0.038))
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
