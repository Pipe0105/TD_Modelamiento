# entities/enemy.py
import pygame, math
import random
from game import settings

class Enemy:
    def __init__(
        self,
        path,
        speed_range=(1.5, 3.0),
        health_range=(80, 150),
        reward=None,
        speed_multiplier=1.0,
        health_multiplier=1.0,
    ):
        self.path = path
        self.pos = list(path[0])
        self.index = 0
        base_speed = random.uniform(*speed_range)
        self.speed = base_speed * speed_multiplier
        self.radius = 10
        self.color = settings.COLORS["enemy"]
        self.alive = True
        base_health = random.randint(*health_range)
        self.max_health = max(1, int(base_health * health_multiplier))
        self.health = self.max_health
        self.reward = reward if reward is not None else settings.ENEMY_REWARD

    def update(self):
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

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)
        # Barra de vida
        pygame.draw.rect(surface, (255, 0, 0), (self.pos[0] - 10, self.pos[1] - 15, 20, 4))
        health_ratio = self.health / self.max_health if self.max_health else 0
        pygame.draw.rect(
            surface,
            (0, 255, 0),
            (self.pos[0] - 10, self.pos[1] - 15, max(0, int(20 * health_ratio)), 4),
        )
