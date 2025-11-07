# entities/build_spot.py
from __future__ import annotations

from pathlib import Path

import pygame

from game import settings


def _remove_background(image: pygame.Surface) -> pygame.Surface:
    """Elimina un fondo plano (negro/gris) tomando el color de la esquina superior izquierda."""

    cleaned = image.copy()
    background = cleaned.get_at((0, 0))
    if getattr(background, "a", 255) == 0:
        return cleaned

    base_color = (background.r, background.g, background.b)
    threshold = 25

    width, height = cleaned.get_size()
    for x in range(width):
        for y in range(height):
            r, g, b, a = cleaned.get_at((x, y))
            if (
                a > 0
                and abs(r - base_color[0]) <= threshold
                and abs(g - base_color[1]) <= threshold
                and abs(b - base_color[2]) <= threshold
            ):
                cleaned.set_at((x, y), (r, g, b, 0))

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