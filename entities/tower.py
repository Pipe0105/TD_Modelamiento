# entities/tower.py
from __future__ import annotations

import math
import time
from pathlib import Path

import pygame

from game import settings
from entities.projectile import Projectile


def _remove_background(image: pygame.Surface) -> pygame.Surface:
    """Elimina fondos planos aprovechando el color de la esquina superior izquierda."""

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

class Tower:
    _image_path = (
        Path(__file__).resolve().parents[1]
        / "maps"
        / "assets"
        / "images"
        / "torre_pred.png"
    )
    _image_cache: pygame.Surface | None = None

    def __init__(self, pos):
        self.pos = (int(pos[0]), int(pos[1]))
        self.range = settings.TOWER_RANGE
        self.fire_rate = settings.TOWER_FIRE_RATE
        self.last_shot = 0
        self.projectiles = []
        self.image = self._load_image()

    def update(self, enemies):
        now = time.time()
        # Mantener solo proyectiles activos
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Actualizar proyectiles
        for p in self.projectiles:
            p.update()

        # Buscar objetivo y disparar si corresponde
        if now - self.last_shot >= 1 / self.fire_rate:
            target = self.get_target(enemies)
            if target:
                self.shoot(target)
                self.last_shot = now

    def get_target(self, enemies):
        """Busca el primer enemigo dentro del rango"""
        for enemy in enemies:
            if not enemy.alive:
                continue
            dx = enemy.pos[0] - self.pos[0]
            dy = enemy.pos[1] - self.pos[1]
            distance = math.hypot(dx, dy)
            if distance <= self.range:
                return enemy
        return None

    def shoot(self, target):
        """Crea un proyectil que sigue a su objetivo"""
        projectile = Projectile(list(self.pos), target)
        self.projectiles.append(projectile)
        print(f"Torre en {self.pos} disparó a enemigo en {target.pos}")

    @classmethod
    def _load_image(cls) -> pygame.Surface | None:
        if cls._image_cache is not None:
            return cls._image_cache

        if not cls._image_path.exists():
            cls._image_cache = None
            return None

        try:
            image = pygame.image.load(str(cls._image_path)).convert_alpha()
        except pygame.error:
            cls._image_cache = None
            return None
        
        image = _remove_background(image)

        target_size = int(settings.TILE_SIZE * 1.2)

        if target_size <= 0:
            cleaned = _remove_background(image)
            cls._image_cache = cleaned
            return cleaned

        width, height = image.get_size()
        if width == 0 or height == 0:
            cls._image_cache = image
            return image

        scale = target_size / max(width, height)
        scaled_size = (max(1, int(width * scale)), max(1, int(height * scale)))
        scaled = pygame.transform.smoothscale(image, scaled_size)
        cls._image_cache = _remove_background(scaled)
        return cls._image_cache

    def draw(self, surface):
        if self.image is not None:
            rect = self.image.get_rect(center=self.pos)
            surface.blit(self.image, rect)
        else:
            pygame.draw.circle(surface, settings.COLORS["tower"], self.pos, 20)

        # Dibujar rango de ataque (transparente)
        pygame.draw.circle(surface, (80, 80, 150, 30), self.pos, self.range, 1)
        # Dibujar proyectiles
        for p in self.projectiles:
            p.draw(surface)