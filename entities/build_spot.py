# entities/build_spot.py
from __future__ import annotations

from pathlib import Path

import pygame

from game import settings


def _load_scaled_image(path: Path, size: int) -> pygame.Surface | None:
    """Carga una imagen desde disco y la escala al tamaño solicitado."""

    if size <= 0 or not path.exists():
        return None

    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None

    if image.get_width() == size and image.get_height() == size:
        return image

    return pygame.transform.smoothscale(image, (size, size))


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
        image = self._get_base_image(self.size)
        if image is not None:
            rect = image.get_rect(center=self.pos)
            surface.blit(image, rect)

            if self.occupied:
                overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
                overlay.fill((30, 70, 120, 120))
                surface.blit(overlay, rect)
            return

        color = settings.COLORS["spot"] if not self.occupied else (30, 70, 120)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
