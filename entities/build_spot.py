# entities/build_spot.py
import pygame
from game import settings

class BuildSpot:
    def __init__(self, pos):
        self.pos = pos
        self.size = 50
        self.rect = pygame.Rect(pos[0]-self.size//2, pos[1]-self.size//2, self.size, self.size)
        self.occupied = False

    def draw(self, surface):
        color = settings.COLORS["spot"] if not self.occupied else (30, 70, 120)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
