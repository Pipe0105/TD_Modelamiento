# entities/enemy.py
import pygame, math
import math
import random
from pathlib import Path

from game import settings


class Enemy:
    """Enemigo que sigue un camino y se representa con sprites animados."""

    SPRITE_BASE_PATH = Path(__file__).resolve().parents[1] / "maps" / "assets" / "images" / "enemy"
    _SPRITE_CACHE: dict[object, dict[str, list[pygame.Surface]]] = {}


    def __init__(
        self,
        path,
        speed_range=(1.5, 3.0),
        health_range=(80, 150),
        reward=None,
        speed_multiplier=1.0,
        health_multiplier=1.0,
        sprite_set: str | None = None,
        radius: int | None = None,
        color: tuple[int, int, int] | None = None,
    ):
        self.path = path
        self.pos = list(path[0])
        self.index = 0
        base_speed = random.uniform(*speed_range)
        self.speed = base_speed * speed_multiplier
        self.alive = True
        base_health = random.randint(*health_range)
        self.max_health = max(1, int(base_health * health_multiplier))
        self.health = self.max_health
        self.reward = reward if reward is not None else settings.ENEMY_REWARD

        self.base_radius = max(1, int(radius)) if radius is not None else 10
        self.base_color = (
            color if color is not None else settings.get_color("enemy", (200, 60, 60))
        )

                # Superficie de respaldo utilizada cuando no existen fotogramas reales.
        # Mantener un placeholder permanente evita parpadeos visibles al cambiar
        # entre sprites o cuando un conjunto carece de ciertas direcciones.
        self.placeholder_image = self._create_placeholder_surface(
            self.base_radius, self.base_color
        )

        # Configuración visual / animación
        self.sprite_set = str(sprite_set) if sprite_set else "1"
        self.sprites = self._load_sprite_set(
            self.sprite_set, placeholder_radius=self.base_radius, placeholder_color=self.base_color
        )
        self.direction = "down"
        self.facing_left = False
        self.frame_index = 0
        self.animation_timer = 0.0
        self.animation_speed = 6.0  # frames por segundo
        self.current_image: pygame.Surface | None = None
        self.visible_image: pygame.Surface | None = self.placeholder_image
        self.rect: pygame.Rect | None = None
        self.radius = self.base_radius
        self.collision_radius = max(10, self.base_radius // 2)
        self._update_image(force=True)

    # ------------------------------------------------------------------
    # Carga de sprites
    # ------------------------------------------------------------------
    @classmethod
    def _load_sprite_set(
        cls,
        sprite_set: str,
        *,
        placeholder_radius: int | None = None,
        placeholder_color: tuple[int, int, int] | None = None,
    ) -> dict[str, list[pygame.Surface]]:
        cache_key: object
        if placeholder_radius is None and placeholder_color is None:
            cache_key = sprite_set
        else:
            cache_key = (sprite_set, placeholder_radius, placeholder_color)

        if cache_key in cls._SPRITE_CACHE:
            return cls._SPRITE_CACHE[cache_key]

        base_dir = cls.SPRITE_BASE_PATH / sprite_set
        placeholder = cls._create_placeholder_surface(placeholder_radius, placeholder_color)
        animations: dict[str, list[pygame.Surface]] = {}
        placeholder_flags: dict[str, bool] = {}

        for direction, prefix in {"down": "D", "up": "U", "side": "S"}.items():
            frames = cls._load_direction_frames(base_dir, prefix)
            if not frames:
                frames = [placeholder]
                placeholder_flags[direction] = True
            else:
                placeholder_flags[direction] = False
            animations[direction] = frames

        fallback_frames = animations.get("down")
        if fallback_frames:
            has_real_fallback = any(frame is not placeholder for frame in fallback_frames)
            if has_real_fallback:
                for direction, frames in animations.items():
                    if placeholder_flags.get(direction):
                        animations[direction] = fallback_frames
                
            animations[direction] = frames
        if base_dir.exists() and cache_key != sprite_set:
            # Si el sprite_set existe físicamente, mantener un caché compartido por nombre.
            cls._SPRITE_CACHE[sprite_set] = animations
        cls._SPRITE_CACHE[cache_key] = animations
        return animations

    @staticmethod
    def _create_placeholder_surface(
        radius: int | None = None, color: tuple[int, int, int] | None = None
    ) -> pygame.Surface:
        radius = max(1, radius) if radius is not None else settings.TILE_SIZE // 2
        color = color if color is not None else settings.get_color("enemy", (200, 60, 60))
        diameter = radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (radius, radius), radius)
        return surface

    @classmethod
    def _load_direction_frames(cls, base_dir: Path, prefix: str) -> list[pygame.Surface]:
        if not base_dir.exists():
            return []

        patterns = [f"{prefix}_Walk*.png", f"{prefix}_Walk.png", f"{prefix}_*.png"]
        image_paths: list[Path] = []
        for pattern in patterns:
            matched = sorted(base_dir.glob(pattern))
            if matched:
                image_paths = matched
                break

        frames: list[pygame.Surface] = []
        for img_path in image_paths:
            try:
                image = pygame.image.load(str(img_path)).convert_alpha()
            except pygame.error:
                continue
            frames.append(cls._scale_image(image))
        return frames

    @staticmethod
    def _scale_image(image: pygame.Surface) -> pygame.Surface:
        target_height = max(1, int(settings.TILE_SIZE * 0.9))
        if image.get_height() == target_height:
            return image
        scale = target_height / image.get_height()
        target_size = (max(1, int(image.get_width() * scale)), target_height)
        return pygame.transform.smoothscale(image, target_size)

    # ------------------------------------------------------------------
    # Ciclo de vida del enemigo
    # ------------------------------------------------------------------
    def update(self, dt: float):
        if self.index >= len(self.path) - 1 or not self.alive:
            return

        target = self.path[self.index + 1]
        dx, dy = target[0] - self.pos[0], target[1] - self.pos[1]
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.index += 1
        else:
            self.pos[0] += self.speed * dx / dist
            self.pos[1] += self.speed * dy / dist

        self._update_direction(dx, dy)
        self._animate(dt)
        self._sync_rect_position()

    # ------------------------------------------------------------------
    # Animación y dirección
    # ------------------------------------------------------------------
    def _update_direction(self, dx: float, dy: float):
        if not self.sprites:
            return

        new_direction = self.direction
        facing_left = self.facing_left

        if abs(dx) >= abs(dy):
            new_direction = "side"
            facing_left = dx < 0
        else:
            new_direction = "down" if dy > 0 else "up"
            facing_left = False

        if new_direction != self.direction or facing_left != self.facing_left:
            self.direction = new_direction
            self.facing_left = facing_left
            self.frame_index = 0
            self._update_image(force=True)

    def _animate(self, dt: float):
        if not self.sprites or self.animation_speed <= 0:
            return

        self.animation_timer += dt
        frame_time = 1.0 / self.animation_speed
        if self.animation_timer >= frame_time:
            self.animation_timer %= frame_time
            self.frame_index = (self.frame_index + 1) % len(self.sprites[self.direction])
            self._update_image()

    def _update_image(self, force: bool = False):
        if not self.sprites:
            if self.current_image is None:
                self.current_image = self.placeholder_image
                self.visible_image = self.placeholder_image
                self.rect = self.placeholder_image.get_rect()
                self._sync_rect_position()
            return

        frames = self.sprites.get(self.direction, [])
        frame: pygame.Surface | None
        if frames:
            frame = frames[self.frame_index % len(frames)]
        else:
            frame = self.placeholder_image

        if self.direction == "side" and frame is not None and self.facing_left:

            frame = pygame.transform.flip(frame, True, False)
        if frame is None:
            frame = self.placeholder_image

        if force or self.current_image is not frame:
            self.current_image = frame
            self.visible_image = frame
            self.rect = frame.get_rect()
            self._sync_rect_position()

        if not self.radius:
            self.radius = self.base_radius
        self.collision_radius = max(10, self.radius // 2)

    def _sync_rect_position(self):
        if not self.rect:
            reference = self.current_image or self.visible_image or self.placeholder_image
            if reference is not None:
                self.rect = reference.get_rect()

        if self.rect:
            self.rect.center = (int(self.pos[0]), int(self.pos[1]))

    # ------------------------------------------------------------------
    # Renderizado
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface):
        image = self.current_image or self.visible_image or self.placeholder_image
        rect = self.rect

        if image is None:
            center = (int(self.pos[0]), int(self.pos[1]))
            pygame.draw.circle(surface, self.base_color, center, self.base_radius)
            bar_width = 36
            bar_height = 6
            bar_x = center[0] - bar_width // 2
            bar_y = center[1] - self.base_radius - bar_height - 4
        else:
            if rect is None:
                rect = image.get_rect()
                self.rect = rect
            self._sync_rect_position()
            if self.rect:
                rect = self.rect
            surface.blit(image, rect)

            bar_width = max(rect.width, 36)
            bar_height = 6
            bar_x = rect.centerx - bar_width // 2
            bar_y = rect.top - bar_height - 6


        # Barra de vida
        pygame.draw.rect(surface, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        health_ratio = self.health / self.max_health if self.max_health else 0
        pygame.draw.rect(
            surface,
            (0, 200, 0),
            (bar_x, bar_y, max(0, int(bar_width * health_ratio)), bar_height),
        )
