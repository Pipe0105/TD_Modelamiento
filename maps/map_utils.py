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


import os
import pygame
from collections import deque
from math import gcd
# --------------------------------------------
# 🎨 CONFIGURACIÓN VISUAL
# --------------------------------------------
RUTA_IMAGENES = os.path.join(os.path.dirname(__file__), "assets", "images")


TILE_SIZE = 50  # Tamaño de cada celda del mapa

# Colores base para generar sprites simples
COLORES = {
    "suelo": (34, 139, 34),
    "camino": (139, 90, 43),
    "base_torre": (128, 128, 128),
    "inicio": (100, 255, 100),
    "fin": (255, 100, 100),
}

def _extraer_primer_cuadro(superficie: pygame.Surface) -> pygame.Surface:
    """
    Cuando la imagen original es una hoja de sprites con múltiples cuadros,
    recorta y devuelve únicamente el primer frame. Si no parece haber más de
    un cuadro, devuelve la superficie original.
    """

    ancho, alto = superficie.get_size()
    if not ancho or not alto:
        return superficie

    # Hojas típicas suelen organizarse en cuadros cuadrados. Utilizamos el MCD
    # para detectar subdivisiones posibles y validar que haya más de un cuadro.
    cuadro = gcd(ancho, alto)
    if cuadro <= 0:
        return superficie

    cuadros_horizontales = ancho // cuadro
    cuadros_verticales = alto // cuadro

    if cuadros_horizontales * cuadros_verticales <= 1:
        return superficie

    rect = pygame.Rect(0, 0, cuadro, cuadro)
    return superficie.subsurface(rect).copy()



def cargar_sprite(tipo, tamaño=TILE_SIZE):

    """
    Carga una imagen desde assets/images/{tipo}.png.
    Si no existe, crea un sprite sólido de color base.
    """
    ruta = os.path.join(RUTA_IMAGENES, f"{tipo}.png")

    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        imagen = _extraer_primer_cuadro(imagen)

        imagen = pygame.transform.scale(imagen, (tamaño, tamaño))
        return imagen
    except FileNotFoundError:
        print(f"⚠️ Imagen no encontrada: {ruta} — usando color base.")
        return crear_sprite_simple(tipo, tamaño)


def _vecinos(x, y):
    """Genera las celdas vecinas en las cuatro direcciones cardinales."""
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        yield x + dx, y + dy


def extraer_caminos(mapa, tipos_camino=(1,), tipo_inicio=3, tipo_fin=4):
    """Obtiene todos los caminos válidos desde cada punto de inicio hasta el final.

    Args:
        mapa: Matriz que describe el terreno del mapa.
        tipos_camino: Valores considerados como casillas transitables.
        tipo_inicio: Valor que representa una casilla de inicio.
        tipo_fin: Valor que representa la casilla final.

    Returns:
        list[list[tuple[int, int]]]: Lista de caminos, uno por cada punto de inicio.

    """
    if not mapa:
        return []

    filas = len(mapa)
    columnas = len(mapa[0]) if filas else 0

    permitidos = set(tipos_camino)
    permitidos.update({tipo_inicio, tipo_fin})

    inicios = [
        (col_idx, fila_idx)
        for fila_idx, fila in enumerate(mapa)
        for col_idx, valor in enumerate(fila)
        if valor == tipo_inicio
    ]

    if not inicios:
        for fila_idx, fila in enumerate(mapa):
            for col_idx, valor in enumerate(fila):
                if valor in permitidos:
                    inicios.append((col_idx, fila_idx))
                    break
            if inicios:
                break

    caminos = []

    for inicio in inicios:
        cola = deque([inicio])
        visitados = {inicio}
        padres = {}
        destino = None

        while cola:
            actual = cola.popleft()
            x, y = actual

            if mapa[y][x] == tipo_fin:
                destino = actual
                break

            for nx, ny in _vecinos(x, y):
                if not (0 <= nx < columnas and 0 <= ny < filas):
                    continue
                if (nx, ny) in visitados:
                    continue
                if mapa[ny][nx] not in permitidos:
                    continue
                visitados.add((nx, ny))
                padres[(nx, ny)] = actual
                cola.append((nx, ny))

        if destino is None:
            continue

        camino = []
        nodo = destino
        while nodo in padres:
            camino.append(nodo)
            nodo = padres[nodo]
        camino.append(nodo)
        camino.reverse()

        caminos.append(camino)

    return caminos

def extraer_camino(mapa, tipo_camino):
    """Compatibilidad hacia atrás: devuelve el primer camino encontrado."""

    caminos = extraer_caminos(mapa, (tipo_camino,))
    return caminos[0] if caminos else []

def crear_sprite_simple(tipo, tamaño=TILE_SIZE):
    """Genera una superficie sólida utilizando el color base del tipo indicado."""
    superficie = pygame.Surface((tamaño, tamaño))
    superficie.fill(COLORES.get(tipo, (255, 255, 255)))
    return superficie


def convertir_camino_a_pixeles(camino, offset=(0, 0)):
    """Convierte una lista de coordenadas de celdas a posiciones en píxeles."""
    ox, oy = offset
    return [
        (int(x * TILE_SIZE + TILE_SIZE // 2 + ox), int(y * TILE_SIZE + TILE_SIZE // 2 + oy))
        for x, y in camino
    ]


def obtener_posiciones_por_tipo(mapa, tipo):
    """Retorna las coordenadas (col, fila) donde el mapa contiene el tipo indicado."""
    posiciones = []
    for fila_idx, fila in enumerate(mapa):
        for col_idx, valor in enumerate(fila):
            if valor == tipo:
                posiciones.append((col_idx, fila_idx))
    return posiciones


def dimensiones_mapa(mapa):
    """Obtiene el ancho y alto en píxeles de una matriz de mapa."""
    filas = len(mapa)
    columnas = len(mapa[0]) if filas else 0
    return columnas * TILE_SIZE, filas * TILE_SIZE


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
