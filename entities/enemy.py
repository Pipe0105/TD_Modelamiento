# entities/enemy.py
import pygame, math
import random
from game import settings

class Enemy:
    def __init__(self, path, speed=2):
        self.path = path
        self.pos = list(path[0])
        self.index = 0
        self.speed = random.uniform(1.5,3.0)
        self.radius = 10
        self.color = settings.COLORS["enemy"]
        self.alive = True
        self.health = random.randint(80, 150)
        self.max_healt = self.health
        self.reward = settings.ENEMY_REWARD

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
        pygame.draw.rect(surface, (255,0,0), (self.pos[0]-10, self.pos[1]-15, 20, 4))
        pygame.draw.rect(surface, (0,255,0), (self.pos[0]-10, self.pos[1]-15, max(0, 20*self.health/100), 4))
