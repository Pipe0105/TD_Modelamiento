# utils/ui_panel.py
import pygame
from game import settings

class MetricsPanel:
    def __init__(self, font):
        self.visible = False
        self.font = font
        self.rect = pygame.Rect(settings.SCREEN_WIDTH - 310, 60, 300, 220)
        self.button_rect = pygame.Rect(settings.SCREEN_WIDTH - 130, 10, 120, 35)

    def handle_click(self, pos):
       # """Alterna entre mostrar/ocultar el panel."""
        if self.button_rect.collidepoint(pos):
            self.visible = not self.visible
            return True
        return False

    def draw_button(self, surface):
        color = (70, 120, 200) if not self.visible else (150, 80, 80)
        pygame.draw.rect(surface, color, self.button_rect, border_radius=6)
        label = self.font.render("📊 Métricas", True, (255, 255, 255))
        surface.blit(label, (self.button_rect.x + 8, self.button_rect.y + 6))

    def draw_panel(self, surface, metrics):
        if not self.visible:
            return
        pygame.draw.rect(surface, (30, 30, 50, 180), self.rect, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 150), self.rect, 2, border_radius=10)

        y = self.rect.y + 20
        for key, val in metrics.items():
            text = self.font.render(f"{key}: {val}", True, (255, 255, 255))
            surface.blit(text, (self.rect.x + 15, y))
            y += 30
