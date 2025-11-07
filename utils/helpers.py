"""Utility helpers for drawing and surface manipulation."""

from __future__ import annotations

from collections import deque

import pygame


def remove_background(image: pygame.Surface, tolerance: int = 70) -> pygame.Surface:
    """Return a copy of *image* with its flat background made transparent.

    The function assumes the pixel in the top-left corner represents the
    background color.  Pixels whose RGB distance from that color is below the
    provided *tolerance* (squared) are made fully transparent using a flood-fill
    starting from the borders of the image.
    """

    cleaned = image.copy().convert_alpha()
    width, height = cleaned.get_size()
    if width == 0 or height == 0:
        return cleaned

    background = pygame.Color(*cleaned.get_at((0, 0)))
    if background.a == 0:
        return cleaned

    tolerance_sq = max(0, tolerance) ** 2
    queue = deque()
    visited: set[tuple[int, int]] = set()

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))

        color = pygame.Color(*cleaned.get_at((x, y)))
        if color.a == 0:
            continue

        dr = color.r - background.r
        dg = color.g - background.g
        db = color.b - background.b
        if dr * dr + dg * dg + db * db <= tolerance_sq:
            cleaned.set_at((x, y), (color.r, color.g, color.b, 0))
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    queue.append((nx, ny))

    return cleaned


def draw_path(surface, path, color, width=5):
    if len(path) > 1:
        pygame.draw.lines(surface, color, False, path, width)


def draw_build_spots(surface, spots, color, size=40):
    for x, y in spots:
        rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
        pygame.draw.rect(surface, color, rect, border_radius=8)