# utils/helpers.py
import pygame

def draw_path(surface, path, color, width=5):
    if len(path) > 1:
        pygame.draw.lines(surface, color, False, path, width)

def draw_build_spots(surface, spots, color, size=40):
    for x, y in spots:
        rect = pygame.Rect(x - size//2, y - size//2, size, size)
        pygame.draw.rect(surface, color, rect, border_radius=8)
