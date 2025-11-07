# entities/build_spot.py
from __future__ import annotations

from collections import deque
from pathlib import Path

import pygame

from game import settings


def _remove_background(image: pygame.Surface, tolerance: int = 70) -> pygame.Surface:
    """Elimina un fondo plano (negro/gris) tomando el color de la esquina superior izquierda."""

    cleaned = image.copy().convert_alpha()
    width, height = cleaned.get_size()
    if width == 0 or height == 0:
        return cleaned

    background = pygame.Color(*cleaned.get_at((0, 0)))
    if background.a == 0:
        return cleaned

    tolerance_sq = max(0, tolerance) ** 2
    queue = deque()
    visited = set()

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))

        color = pygame.Color(*cleaned.get_at((x, y)))
        if color.a == 0:
            continue

        dr = color.r - background.r
        dg = color.g - background.g
        db = color.b - background.b
        if dr * dr + dg * dg + db * db <= tolerance_sq:
            cleaned.set_at((x, y), (color.r, color.g, color.b, 0))
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    queue.append((nx, ny))

    return cleaned


def _load_scaled_image(path: Path, size: int) -> pygame.Surface | None:
    """Carga una imagen desde disco, limpia el fondo y la escala al tamaño solicitado."""

    if size <= 0 or not path.exists():
        return None

    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None

    if image.get_width() != size or image.get_height() != size:
        image = pygame.transform.smoothscale(image, (size, size))

    return _remove_background(image)


class BuildSpot:
    """Representa una casilla disponible para construir una torre."""

    _base_image_path = (
        Path(__file__).resolve().parents[1]
        / "maps"
        / "assets"
        / "images"
        / "base_torre.png"
    )
    _base_image_cache: dict[int, pygame.Surface] = {}

    def __init__(self, pos, size=None):
        self.pos = (int(pos[0]), int(pos[1]))
        self.size = size or settings.TILE_SIZE
        self.rect = pygame.Rect(
            self.pos[0] - self.size // 2,
            self.pos[1] - self.size // 2,
            self.size,
            self.size,
        )
        self.occupied = False

    @classmethod
    def _get_base_image(cls, size: int) -> pygame.Surface | None:
        cached = cls._base_image_cache.get(size)
        if cached is not None:
            return cached

        image = _load_scaled_image(cls._base_image_path, size)
        if image is not None:
            cls._base_image_cache[size] = image
        return image
    def draw(self, surface):
        """Renderiza el punto de construcción si está disponible."""

        if self.occupied:
            return

        image = self._get_base_image(self.size)
        if image is not None:
            rect = image.get_rect(center=self.pos)
            surface.blit(image, rect)
            return

        pygame.draw.rect(surface, settings.COLORS["spot"], self.rect, border_radius=8)
