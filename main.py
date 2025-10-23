import pygame, sys
from game.game_manager import GameManager
from game import settings

def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption("Tower Defense - Simulación λ/μ (versión jugable)")
    clock = pygame.time.Clock()

    game = GameManager()
    running = True

    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        # --- EVENTOS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # ✅ Envía el clic al GameManager
                game.handle_click(event.pos)

        # --- ACTUALIZAR Y DIBUJAR ---
        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
