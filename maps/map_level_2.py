"""
map_level_2.py
---------------------------------------
Mapa del Nivel 2: "Valle Dividido"
"""

from .map_utils import cargar_sprite, Tile, extraer_caminos



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
    "crecimiento_oleada": {"velocidad": 1.06, "salud": 1.15},
    "enemigos": [
        {
            "nombre": "Explorador",
            "peso": 0.55,
            "velocidad": (1.3, 2.4),
            "salud": (90, 150),
            "recompensa": 15,
            "color": (210, 80, 80),
            "radio": 10,
            "sprite_set": "1",
        },
        {
            "nombre": "Guardia",
            "peso": 0.3,
            "velocidad": (1.1, 1.9),
            "salud": (140, 210),
            "salud_factor": 1.2,
            "recompensa": 22,
            "color": (200, 120, 60),
            "radio": 12,
            "sprite_set": "2",
        },
        {
            "nombre": "Asaltante",
            "peso": 0.15,
            "velocidad": (1.8, 2.8),
            "velocidad_factor": 1.15,
            "salud": (100, 150),
            "recompensa": 18,
            "color": (230, 60, 120),
            "radio": 10,
            "sprite_set": "3",
        },
    ],
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

    caminos = extraer_caminos(MAPA_NIVEL_2, (1,))

    return tiles, caminos
