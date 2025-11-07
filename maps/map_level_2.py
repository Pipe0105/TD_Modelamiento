"""
map_level_2.py
---------------------------------------
Mapa del Nivel 2: "Valle Dividido"
"""

from .map_utils import cargar_sprite, Tile, extraer_camino


import pygame

# Matriz del mapa (solo define el terreno)
MAPA_NIVEL_2 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [3, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 0, 1, 0, 2, 0, 2, 0, 2, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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
        0: cargar_sprite("suelo"),
        1: cargar_sprite("camino"),
        2: cargar_sprite("base_torre"),
        3: cargar_sprite("inicio"),
        4: cargar_sprite("fin"),
    }

    tiles = pygame.sprite.Group()
    for fila_idx, fila in enumerate(MAPA_NIVEL_2):
        for col_idx, tipo in enumerate(fila):
            tile = Tile(col_idx, fila_idx, tipo, sprites)
            tiles.add(tile)

    caminos = []
    for tipo in [1]:

        camino = extraer_camino(MAPA_NIVEL_2, tipo)
        if camino:
            caminos.append(camino)

    return tiles, caminos
