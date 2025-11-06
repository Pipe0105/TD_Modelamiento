"""Paquete que agrupa la configuración de niveles del juego."""
from .map_level_1 import CONFIG_NIVEL_1, crear_mapa_nivel_1
from .map_level_2 import CONFIG_NIVEL_2, crear_mapa_nivel_2
from .map_level_3 import CONFIG_NIVEL_3, crear_mapa_nivel_3

LEVELS = [
    {"config": CONFIG_NIVEL_1, "creator": crear_mapa_nivel_1},
    {"config": CONFIG_NIVEL_2, "creator": crear_mapa_nivel_2},
    {"config": CONFIG_NIVEL_3, "creator": crear_mapa_nivel_3},
]

__all__ = ["LEVELS"]