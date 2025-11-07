"""
map_level_3.py
---------------------------------------
Mapa del Nivel 3: "Infierno Convergente"

Responsabilidades:
- Definir la matriz del mapa (MAPA_NIVEL_3)
- Proveer una función para crear los tiles y caminos del nivel
- Incluir la configuración básica del nivel (vidas, dinero, oleadas, etc.)

Uso:
    from maps.map_level_3 import crear_mapa_nivel_3, CONFIG_NIVEL_3
"""

from .map_utils import cargar_sprite, Tile, extraer_camino


import pygame

# --------------------------------------------------
# 🗺️ MATRIZ DEL MAPA NIVEL 3
# --------------------------------------------------
MAPA_NIVEL_3 = [
    [3, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 0, 0, 1, 0, 2, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0],
]

# --------------------------------------------------
# ⚙️ CONFIGURACIÓN GENERAL DEL NIVEL
# --------------------------------------------------
CONFIG_NIVEL_3 = {
    "nombre": "Infierno Convergente",
    "mapa": MAPA_NIVEL_3,
    "oleadas_victoria": 9,
    "dinero_inicial": 190,
    "vidas_inicial": 3,
    "multiplicadores": {"velocidad": 1.3, "salud": 1.45, "lambda": 1.3},
}

# --------------------------------------------------
# 🧩 FUNCIÓN PRINCIPAL PARA CREAR EL MAPA
# --------------------------------------------------
def crear_mapa_nivel_3():
    """
    Genera los tiles y caminos del Nivel 3.
    Retorna:
        - tiles (pygame.sprite.Group)
        - caminos (list[list[tuple[int, int]]])
    """
    pygame.font.init()  # Inicializa fuente para texto sobre los tiles

    # Sprites simples para cada tipo de celda
    sprites = {
        0: cargar_sprite("suelo"),
        1: cargar_sprite("camino"),
        2: cargar_sprite("base_torre"),
        3: cargar_sprite("inicio"),
        4: cargar_sprite("fin"),
    }

    # Grupo de tiles
    tiles = pygame.sprite.Group()
    for fila_idx, fila in enumerate(MAPA_NIVEL_3):
        for col_idx, tipo in enumerate(fila):
            tile = Tile(col_idx, fila_idx, tipo, sprites)
            tiles.add(tile)

    # Generar caminos a partir de tipos definidos
    caminos = []
    for tipo in [1]:
        camino = extraer_camino(MAPA_NIVEL_3, tipo)
        if camino:
            caminos.append(camino)

    return tiles, caminos
