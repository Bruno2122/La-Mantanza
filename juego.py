import pygame
def menu():
    pygame.init()
    info_pantalla = pygame.display.Info()
    pantalla = pygame.display.set_mode((info_pantalla.current_w, info_pantalla.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("El prime")
    fondo = pygame.image.load("fondo menu.png").convert()
    fondo = pygame.transform.scale(fondo, (info_pantalla.current_w, info_pantalla.current_h))
    pygame.display.flip()
    ejecutar = True
    while ejecutar:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutar = False
        pantalla.blit(fondo, (0, 0))
        pygame.display.flip()
    pygame.quit()
menu()