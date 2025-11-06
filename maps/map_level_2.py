"""
map_level_2.py
---------------------------------------
Mapa del Nivel 2: "Valle Dividido"
"""

from .map_utils import crear_sprite_simple, Tile, extraer_camino

import pygame

# Matriz del mapa (solo define el terreno)
MAPA_NIVEL_2 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [3,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,0,2,0,0,0,2,0,0,0,0,0,0],
    [0,0,2,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,2,0,0,0,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
    [0,0,0,2,0,2,0,0,0,0,0,0,0,0,2,0,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
    [0,0,5,5,5,5,5,0,0,0,0,0,0,0,0,0,1,0],
    [0,0,5,0,0,0,5,0,2,0,2,0,2,0,0,0,1,0],
    [0,0,5,0,2,0,5,5,5,5,5,5,5,5,5,5,1,0],
    [0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

# Configuración del nivel
CONFIG_NIVEL_2 = {
    "nombre": "Valle Dividido",
    "mapa": MAPA_NIVEL_2,
    "oleadas_victoria": 7,
    "dinero_inicial": 170,
    "vidas_inicial": 3,
    "multiplicadores": {"velocidad": 1.15, "salud": 1.2, "lambda": 1.15},
}

def crear_mapa_nivel_2():
    """
    Genera los tiles y caminos del Nivel 2.
    Retorna:
        - tiles (pygame.sprite.Group)
        - caminos (list[list[tuple[int, int]]])
    """
    pygame.font.init()

    sprites = {
        0: crear_sprite_simple("suelo"),
        1: crear_sprite_simple("camino"),
        2: crear_sprite_simple("base_torre"),
        3: crear_sprite_simple("inicio"),
        4: crear_sprite_simple("fin"),
        5: crear_sprite_simple("camino"),
    }

    tiles = pygame.sprite.Group()
    for fila_idx, fila in enumerate(MAPA_NIVEL_2):
        for col_idx, tipo in enumerate(fila):
            tile = Tile(col_idx, fila_idx, tipo, sprites)
            tiles.add(tile)

    caminos = []
    for tipo in [1, 5]:
        camino = extraer_camino(MAPA_NIVEL_2, tipo)
        if camino:
            caminos.append(camino)

    return tiles, caminos
