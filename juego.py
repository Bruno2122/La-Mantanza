import pygame
def menu():
    x = 835
    y = 765
    pygame.init()
    info_pantalla = pygame.display.Info()
    pantalla = pygame.display.set_mode((info_pantalla.current_w, info_pantalla.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("El prime")
    fondo = pygame.image.load("imagen.jpg").convert()
    fondo = pygame.transform.scale(fondo, (info_pantalla.current_w, info_pantalla.current_h))
    pygame.draw.rect(pantalla, (255, 0, 0), (x, y, 100, 100))
    pygame.display.flip()
    ejecutar = True
    while ejecutar:

        pantalla.blit(fondo, (0, 0))
        pygame.draw.rect(pantalla, (0, 255, 0), (200, 765, 150, 100))
        pygame.draw.rect(pantalla, (255, 0, 0), (x, y, 100, 100))
        pygame.display.flip()
