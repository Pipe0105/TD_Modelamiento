# entities/tower.py
import pygame, math, time
from game import settings
from entities.projectile import Projectile

class Tower:
    def __init__(self, pos):
        self.pos = pos
        self.range = settings.TOWER_RANGE
        self.fire_rate = settings.TOWER_FIRE_RATE
        self.last_shot = 0
        self.projectiles = []

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

    def draw(self, surface):
        # Torre base
        pygame.draw.circle(surface, settings.COLORS["tower"], self.pos, 20)
        # Dibujar rango de ataque (transparente)
        pygame.draw.circle(surface, (80, 80, 150, 30), self.pos, self.range, 1)
        # Dibujar proyectiles
        for p in self.projectiles:
            p.draw(surface)
