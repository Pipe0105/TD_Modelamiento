# game/game_manager.py
import pygame, random
from game import settings
from entities.enemy import Enemy
from entities.tower import Tower
from entities.build_spot import BuildSpot
from utils.helpers import draw_path
from utils.ui_panel import MetricsPanel

class GameManager:
    def __init__(self):
        self.enemies = []
        self.towers = []
        self.spots = [BuildSpot(p) for p in settings.BUILD_SPOTS]
        self.spawn_timer = 0
        self.enemy_interval = random.expovariate(settings.LAMBDA_RATE)
        self.wave = 1
        self.enemies_per_wave = 10
        self.spawned_in_wave = 0
        self.wave_active = True
        self.lambda_base = settings.LAMBDA_RATE
        self.path = settings.PATH
        self.font = pygame.font.SysFont("consolas", 18)
        self.money = settings.STARTING_MONEY
        self.total_spawned = 0
        self.lives = 10
        self.metrics_panel = MetricsPanel(self.font)

    def calculate_metrics(self):
       # """Calcula métricas básicas de teoría de colas."""
        c = len(self.towers)
        λ = round(self.lambda_base, 2)
        μ = round(settings.TOWER_FIRE_RATE, 2)
        ρ = round(λ / (c * μ), 3) if c > 0 else 0
        L = len(self.enemies)
        return {"λ": λ, "μ": μ, "c": c, "ρ": ρ, "Enemigos (L)": L}


    def update(self, dt):
        # Control del spawn de enemigos (oleadas)
        if self.wave_active:
            self.spawn_timer += dt

            # Generación exponencial de llegadas (λ)
            if self.spawn_timer >= self.enemy_interval and self.spawned_in_wave < self.enemies_per_wave:
                self.spawn_enemy()
                self.spawn_timer = 0
                self.enemy_interval = random.expovariate(self.lambda_base)
                self.spawned_in_wave += 1

            # Si todos los enemigos de la oleada murieron, pasar a la siguiente
            if self.spawned_in_wave >= self.enemies_per_wave and not self.enemies:
                self.next_wave()

        # Actualizar enemigos (posición, vida)
        for enemy in list(self.enemies):
            enemy.update()

            # Si el enemigo llega al final del camino, se pierde una vida
            if enemy.index >= len(self.path) - 1:
                self.enemies.remove(enemy)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over()

        # Eliminar enemigos muertos y sumar dinero
        for enemy in list(self.enemies):
            if not enemy.alive:
                self.money += enemy.reward
                self.enemies.remove(enemy)

        # Actualizar torres y proyectiles
        for tower in self.towers:
            tower.update(self.enemies)


    def spawn_enemy(self):
        self.enemies.append(Enemy(self.path))
        self.total_spawned += 1

    

    def next_wave(self):
       
        # Inicia la siguiente oleada, aumentando dificultad.
        self.wave += 1
        self.enemies_per_wave += 5
        self.lambda_base *= 1.1  # aumenta frecuencia de llegada
        print(f"--- Inicia Oleada {self.wave} ---")
        self.spawned_in_wave = 0
        self.wave_active = True
        
    def handle_click(self, pos):
        print(f"[DEBUG] Clic detectado en {pos}")  # opcional para verificar

        # Primero intenta alternar el panel de métricas
        if self.metrics_panel.handle_click(pos):
            return  # si fue clic en el botón, no sigue con torres

        # Si no fue sobre el botón, intenta construir torre
        for spot in self.spots:
            if spot.rect.collidepoint(pos) and not spot.occupied:
                if self.money >= settings.TOWER_COST:
                    self.money -= settings.TOWER_COST
                    self.towers.append(Tower(spot.pos))
                    spot.occupied = True


    def draw(self, surface):
        surface.fill(settings.COLORS["bg"])
        draw_path(surface, self.path, settings.COLORS["path"])
        for spot in self.spots:
            spot.draw(surface)
        for tower in self.towers:
            tower.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)

        # Datos de la UI principal
        ui_text = self.font.render(
            f"$ {self.money} | Enemigos: {len(self.enemies)} | Torres: {len(self.towers)} | Oleada: {self.wave}",
            True, (255,255,255)
        )
        surface.blit(ui_text, (10, 10))

        # Botón de métricas
        self.metrics_panel.draw_button(surface)

        # Si está visible, calcular métricas y mostrarlas
        metrics = self.calculate_metrics()
        self.metrics_panel.draw_panel(surface, metrics)


