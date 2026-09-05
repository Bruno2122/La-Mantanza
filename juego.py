import pygame
def menu():
    x = 835
    y = 765
    pygame.init()
    info_pantalla = pygame.display.Info()
    pantalla = pygame.display.set_mode((info_pantalla.current_w, info_pantalla.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("El prime")
    fondo = pygame.image.load("fondo.menu.png").convert()
    fondo = pygame.transform.scale(fondo, (info_pantalla.current_w, info_pantalla.current_h))
    pygame.draw.rect(pantalla, (255, 0, 0), (x, y, 100, 100))
    pygame.display.flip()

