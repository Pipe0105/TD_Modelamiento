# entities/projectile.py
import math

import pygame

from game import settings


class Projectile:
    def __init__(self, pos, target, damage, speed=None):
        self.pos = list(pos)
        self.target = target
        self.speed = speed if speed is not None else settings.PROJECTILE_SPEED
        self.damage = damage
        self.alive = True

    def update(self):
        # Si el objetivo ya murió, eliminar el proyectil
        if not self.target.alive:
            self.alive = False
            return

        # Calcular dirección hacia el objetivo
        dx = self.target.pos[0] - self.pos[0]
        dy = self.target.pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)

        # Si el proyectil está suficientemente cerca, aplica daño
        if dist < 10:
            self.target.health -= self.damage
            if self.target.health <= 0:
                self.target.health = 0      # Evita números negativos
                self.target.alive = False   # Marca enemigo como eliminado
            self.alive = False               # Destruye el proyectil tras impacto
        else:
            # Movimiento normal del proyectil hacia el objetivo
            self.pos[0] += self.speed * dx / dist
            self.pos[1] += self.speed * dy / dist


    def draw(self, surface):
        pygame.draw.circle(
            surface,
            settings.COLORS["projectile"],
            (int(self.pos[0]), int(self.pos[1])),
            7,
        )