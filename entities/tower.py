# entities/tower.py
from __future__ import annotations

import math
import time
from pathlib import Path
import random

import pygame

from game import settings
from entities.projectile import Projectile


from utils.helpers import remove_background


class Tower:
    _image_path = (
        Path(__file__).resolve().parents[1]
        / "maps"
        / "assets"
        / "images"
        / "torre_pred.png"
    )
    _image_cache: pygame.Surface | None = None

    def __init__(self, pos, tower_type: str = "guardian"):
        self.pos = (int(pos[0]), int(pos[1]))
        self.type_key = tower_type
        self.type_config = self._resolve_type_config(tower_type)

        self.range = self.type_config.get("range", settings.TOWER_RANGE)
        self.fire_rate = self.type_config.get("fire_rate", settings.TOWER_FIRE_RATE)
        self.damage = self.type_config.get("damage", settings.PROJECTILE_DAMAGE)
        self.projectile_speed = self.type_config.get("projectile_speed", settings.PROJECTILE_SPEED)
        self.name = self.type_config.get("label", "Torre")
        self.upgrade_levels = {key: 0 for key in settings.TOWER_UPGRADES}
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
        projectile = Projectile(
            list(self.pos),
            target,
            damage=self.damage,
            speed=self.projectile_speed,
        )
        self.projectiles.append(projectile)
        print(f"Torre en {self.pos} disparó a enemigo en {target.pos}")

    def get_rect(self) -> pygame.Rect:
        if self.image is not None:
            return self.image.get_rect(center=self.pos)
        size = 40
        return pygame.Rect(self.pos[0] - size // 2, self.pos[1] - size // 2, size, size)

    def contains_point(self, pos: tuple[int, int]) -> bool:
        return self.get_rect().collidepoint(pos)

    def get_upgrade_level(self, key: str) -> int:
        return self.upgrade_levels.get(key, 0)

    def can_upgrade(self, key: str) -> bool:
        config = settings.TOWER_UPGRADES.get(key)
        if not config:
            return False
        max_level = config.get("max_level")
        if max_level is None:
            return True
        return self.get_upgrade_level(key) < max_level

    def apply_upgrade(self, key: str) -> bool:
        config = settings.TOWER_UPGRADES.get(key)
        if not config or not self.can_upgrade(key):
            return False

        increment = config.get("increment", 0)
        if key == "damage":
            self.damage += increment
        elif key == "fire_rate":
            self.fire_rate = max(0.1, self.fire_rate + increment)
        elif key == "range":
            self.range = max(10, self.range + increment)
        else:
            return False

        self.upgrade_levels[key] = self.upgrade_levels.get(key, 0) + 1
        return True

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
        
        image = remove_background(image)

        target_size = int(settings.TILE_SIZE * 1.2)

        if target_size <= 0:
            cleaned = remove_background(image)
            cls._image_cache = cleaned
            return cleaned

        width, height = image.get_size()
        if width == 0 or height == 0:
            cls._image_cache = image
            return image

        scale = target_size / max(width, height)
        scaled_size = (max(1, int(width * scale)), max(1, int(height * scale)))
        scaled = pygame.transform.smoothscale(image, scaled_size)
        cls._image_cache = remove_background(scaled)
        return cls._image_cache

    def draw(self, surface, selected: bool = False):
        if self.image is not None:
            rect = self.image.get_rect(center=self.pos)
            surface.blit(self.image, rect)
        else:
            pygame.draw.circle(surface, settings.get_color("tower"), self.pos, 20)


        # Dibujar rango de ataque (transparente)
        pygame.draw.circle(surface, (80, 80, 150, 60), self.pos, self.range, 1)
        if selected:
            highlight_radius = max(24, self.get_rect().width // 2 + 6)
            pygame.draw.circle(surface, (220, 220, 120), self.pos, highlight_radius, 2)
        # Dibujar proyectiles
        for p in self.projectiles:
            p.draw(surface)

    @staticmethod
    def _resolve_type_config(tower_type: str) -> dict:
        config = settings.TOWER_TYPES.get(tower_type)
        if config is None:
            # Fallback al primer tipo disponible o configuración por defecto
            if settings.TOWER_TYPES:
                return next(iter(settings.TOWER_TYPES.values()))
            return {
                "label": "Torre",
                "range": settings.TOWER_RANGE,
                "fire_rate": settings.TOWER_FIRE_RATE,
                "damage": settings.PROJECTILE_DAMAGE,
                "projectile_speed": settings.PROJECTILE_SPEED,
            }
        return dict(config)
