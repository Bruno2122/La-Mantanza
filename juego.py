import pygame
import sys
import os
import cv2

pygame.init()

pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
ancho, alto = pantalla.get_size()
pygame.display.set_caption("La Matanza Avanza")

video = cv2.VideoCapture("trenfondo.mp4")

anchoPanel = int(ancho * 0.32)

panelIzquierdo = pygame.Surface((anchoPanel, alto))
panelIzquierdo.fill((0, 0, 0))
panelIzquierdo.set_alpha(170)

panelDerecho = pygame.Surface((ancho - anchoPanel, alto))
panelDerecho.fill((0, 0, 0))
panelDerecho.set_alpha(128)

fuenteTitulo = pygame.font.Font("minecraft.ttf", int(alto * 0.065))
fuenteBoton = pygame.font.Font("minecraft.ttf", int(alto * 0.038))

def renderGrosor(fuente, texto, color, grosor=2):
    surf = fuente.render(texto, True, color)
    w_t, h_t = surf.get_size()
    surfGrueso = pygame.Surface((w_t + grosor * 2, h_t + grosor * 2), pygame.SRCALPHA)
    for dx in range(-grosor, grosor + 1):
        for dy in range(-grosor, grosor + 1):
            surfGrueso.blit(surf, (dx + grosor, dy + grosor))
    return surfGrueso

titulo1 = renderGrosor(fuenteTitulo, "La Matanza,", (255, 255, 255), 2)
titulo2 = renderGrosor(fuenteTitulo, "Avanza", (255, 255, 255), 2)

rectTitulo1 = titulo1.get_rect(center=(anchoPanel // 2, int(alto * 0.12)))
rectTitulo2 = titulo2.get_rect(center=(anchoPanel // 2, int(alto * 0.20)))

anchoBoton = int(anchoPanel * 0.78)
altoBoton = int(alto * 0.08)
posXBoton = (anchoPanel - anchoBoton) // 2
posYInicio = int(alto * 0.36)
espacio = int(alto * 0.12)

botones = [
    {"texto": "JUGAR", "rect": pygame.Rect(posXBoton, posYInicio, anchoBoton, altoBoton), "accion": "jugar"},
    {"texto": "AJUSTES", "rect": pygame.Rect(posXBoton, posYInicio + espacio, anchoBoton, altoBoton), "accion": "ajustes"},
    {"texto": "SALIR", "rect": pygame.Rect(posXBoton, posYInicio + espacio * 2, anchoBoton, altoBoton), "accion": "salir"}
]

reloj = pygame.time.Clock()

jugando = True
while jugando:
    posMouse = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jugando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                jugando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for b in botones:
                if b["rect"].collidepoint(posMouse):
                    if b["accion"] == "salir":
                        jugando = False

    exito, frame = video.read()
    if not exito:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        exito, frame = video.read()

    if exito:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (ancho, alto))
        fondoSurf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        pantalla.blit(fondoSurf, (0, 0))

    pantalla.blit(panelIzquierdo, (0, 0))
    pantalla.blit(panelDerecho, (anchoPanel, 0))

    pantalla.blit(titulo1, rectTitulo1)
    pantalla.blit(titulo2, rectTitulo2)

    for b in botones:
        activo = b["rect"].collidepoint(posMouse)
        colorFondo = (95, 95, 95) if activo else (75, 75, 75)
        colorBorde = (130, 130, 130) if activo else (45, 45, 45)

        pygame.draw.rect(pantalla, colorFondo, b["rect"], border_radius=6)
        pygame.draw.rect(pantalla, colorBorde, b["rect"], width=3, border_radius=6)

        surfTexto = fuenteBoton.render(b["texto"], True, (255, 255, 255))
        rectTexto = surfTexto.get_rect(center=b["rect"].center)
        pantalla.blit(surfTexto, rectTexto)

    pygame.display.flip()
    reloj.tick(60)

video.release()
pygame.quit()
sys.exit()
