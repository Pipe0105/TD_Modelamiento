"""
---------------------------------------
Módulo auxiliar para gestionar los mapas del juego Tower Defense.

Responsabilidades:
- Definir los tipos de celdas (suelo, camino, torre, inicio, fin)
- Crear sprites simples (sin imágenes externas)
- Extraer el camino de los enemigos desde una matriz de mapa
- Generar un grupo de tiles dibujables con Pygame

Dependencias:
- pygame (para crear superficies y sprites)
"""

import pygame
import os

# --------------------------------------------
# 🎨 CONFIGURACIÓN VISUAL
# --------------------------------------------

RUTA_IMAGENES = os.path.join(os.path.dirname(__file__), "..\assets\images")

TILE_SIZE = 50  # Tamaño de cada celda del mapa

# Colores base para generar sprites simples
COLORES = {
    "suelo": (34, 139, 34),
    "camino": (139, 90, 43),
    "base_torre": (128, 128, 128),
    "inicio": (100, 255, 100),
    "fin": (255, 100, 100),
}


def cargar_sprite(tipo, tamaño=50):
    """
    Carga una imagen desde assets/images/{tipo}.png.
    Si no existe, crea un sprite sólido de color base.
    """
    ruta = os.path.join(RUTA_IMAGENES, f"{tipo}.png")

    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        imagen = pygame.transform.scale(imagen, (tamaño, tamaño))
        return imagen
    except FileNotFoundError:
        print(f"⚠️ Imagen no encontrada: {ruta} — usando color base.")
        superficie = pygame.Surface((tamaño, tamaño))
        superficie.fill(COLORES.get(tipo, (255, 255, 255)))
        return superficie


def extraer_camino(mapa, tipo_camino):
    """
    Extrae y ordena las coordenadas del camino (path) en el mapa.

    Args:
        mapa (list[list[int]]): matriz que representa el mapa
        tipo_camino (int): número que identifica el tipo de camino (1, 5, 6, etc.)
    
    Returns:
        list[tuple[int, int]]: lista ordenada de coordenadas (x, y) del camino
    """
    coordenadas = []
    fin_pos = None

    for fila_idx, fila in enumerate(mapa):
        for col_idx, tipo in enumerate(fila):
            if tipo == tipo_camino or tipo == 3:  # 3 = inicio
                coordenadas.append((col_idx, fila_idx))
            elif tipo == 4:  # 4 = fin
                fin_pos = (col_idx, fila_idx)

    if not coordenadas:
        return []

    camino_ordenado = [coordenadas[0]]
    sin_visitar = coordenadas[1:]

    while sin_visitar:
        ultima = camino_ordenado[-1]
        siguiente = None
        distancia_min = float('inf')

        for coord in sin_visitar:
            dist = abs(coord[0] - ultima[0]) + abs(coord[1] - ultima[1])
            if dist <= 1 and dist < distancia_min:
                distancia_min = dist
                siguiente = coord

        if siguiente:
            camino_ordenado.append(siguiente)
            sin_visitar.remove(siguiente)
        else:
            break

    if fin_pos:
        camino_ordenado.append(fin_pos)

    return camino_ordenado


class Tile(pygame.sprite.Sprite):
    """
    Clase que representa una celda del mapa.
    Cada Tile tiene una posición (x, y) y un tipo de terreno.
    """
    def __init__(self, x, y, tipo, sprites):
        super().__init__()
        self.tipo = tipo
        self.image = sprites[tipo].copy()
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
