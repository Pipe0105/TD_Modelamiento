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

from map_utils import TILE_SIZE, crear_sprite_simple, Tile, extraer_camino
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
    [3, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 0, 0, 5, 0, 2, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0],
    [3, 6, 6, 6, 6, 6, 6, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 6, 6, 6, 6, 6, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0],
]

# --------------------------------------------------
# ⚙️ CONFIGURACIÓN GENERAL DEL NIVEL
# --------------------------------------------------
CONFIG_NIVEL_3 = {
    "nombre": "Infierno Convergente",
    "mapa": MAPA_NIVEL_3,
    "oleadas_victoria": 15,
    "dinero_inicial": 250,
    "vidas_inicial": 15,
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
        0: crear_sprite_simple("suelo"),
        1: crear_sprite_simple("camino"),
        2: crear_sprite_simple("base_torre"),
        3: crear_sprite_simple("inicio"),
        4: crear_sprite_simple("fin"),
        5: crear_sprite_simple("camino"),
        6: crear_sprite_simple("camino"),
    }

    # Grupo de tiles
    tiles = pygame.sprite.Group()
    for fila_idx, fila in enumerate(MAPA_NIVEL_3):
        for col_idx, tipo in enumerate(fila):
            tile = Tile(col_idx, fila_idx, tipo, sprites)
            tiles.add(tile)

    # Generar caminos a partir de tipos definidos
    caminos = []
    for tipo in [1, 5, 6]:
        camino = extraer_camino(MAPA_NIVEL_3, tipo)
        if camino:
            caminos.append(camino)

    return tiles, caminos
