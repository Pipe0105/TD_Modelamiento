# entities/build_spot.py
from __future__ import annotations
from pathlib import Path

import pygame

from game import settings
from utils.helpers import remove_background


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

    return remove_background(image)



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

        pygame.draw.rect(surface, settings.get_color("spot"), self.rect, border_radius=8)

