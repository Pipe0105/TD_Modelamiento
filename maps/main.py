"""
main.py
---------------------------------------
Ejemplo de uso de los mapas del módulo "maps".
"""
import pygame
from map_level_1 import crear_mapa_nivel_1, CONFIG_NIVEL_1

ANCHO = 900
ALTO = 700

def main():
    pygame.init()
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Visualizador de Mapas Tower Defense")
    clock = pygame.time.Clock()

    # Crear mapa
    tiles, caminos = crear_mapa_nivel_1()

    print(f"🗺️ Mapa: {CONFIG_NIVEL_1['nombre']}")
    print(f"👣 Caminos detectados: {len(caminos)}")

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

        screen.fill((15, 25, 15))
        tiles.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
