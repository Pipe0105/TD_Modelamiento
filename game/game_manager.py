# game/game_manager.py
import random
from typing import List, Optional

import pygame

from game import settings
from entities.enemy import Enemy
from entities.tower import Tower
from entities.build_spot import BuildSpot
from utils.ui_panel import MetricsPanel
from maps import LEVELS
from maps.map_utils import (
    TILE_SIZE,
    convertir_camino_a_pixeles,
    dimensiones_mapa,
    obtener_posiciones_por_tipo,
)

class GameManager:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 26)
        # Estado general
        self.levels = LEVELS
        self.state: str = "menu"
        self.current_level_index: Optional[int] = None
        self.level_config = None

        # Elementos del mapa
        self.tiles: Optional[pygame.sprite.Group] = None
        self.map_offset = (0, 0)
        self.paths: List[List[tuple[int, int]]] = []
        self.spots: List[BuildSpot] = []
        self.towers: List[Tower] = []
        self.enemies: List[Enemy] = []
        self.enemy_tiers: List[dict] = []

        # Control de oleadas
        self.spawn_timer = 0.0
        self.enemy_interval = 0.0
        self.wave = 0
        self.target_waves = 0
        self.enemies_per_wave = 0
        self.spawned_in_wave = 0
        self.wave_active = False
        self.lambda_base = settings.LAMBDA_RATE

        # Recursos y dificultad
        self.money = settings.STARTING_MONEY
        self.total_spawned = 0
        self.metrics_panel = MetricsPanel(self.font)
        self.wave_speed_growth = 1.0
        self.wave_health_growth = 1.0

        self.menu_buttons = self._build_menu_buttons()
        self.overlay_buttons: List[dict] = []
        self.pause_button = self._make_button(
            "Menú",
            (settings.SCREEN_WIDTH - 110, 45),
            self.enter_pause_menu,
            size=(180, 50),
        )
        self._wave_was_active = True

    # ------------------------------------------------------------------
    # Configuración de niveles
    # ------------------------------------------------------------------
    def _build_menu_buttons(self) -> List[dict]:
        buttons = []
        center_x = settings.SCREEN_WIDTH // 2
        base_y = settings.SCREEN_HEIGHT // 2 - (len(self.levels) * 80) // 2
        for idx, level in enumerate(self.levels):
            center = (center_x, base_y + idx * 90)
            buttons.append(
                self._make_button(
                    level["config"]["nombre"],
                    center,
                    lambda index=idx: self.load_level(index),
                    level_index=idx,
                )
            )
        return buttons

    def _make_button(self, text, center, action, level_index=None, size=(320, 60)) -> dict:
        rect = pygame.Rect(0, 0, *size)
        rect.center = center
        return {"rect": rect, "text": text, "action": action, "level_index": level_index}

    def load_level(self, index: int):
        """Carga un mapa y reinicia todos los parámetros asociados."""
        self.current_level_index = index
        level_entry = self.levels[index]
        self.level_config = level_entry["config"]

        # Construcción visual del mapa
        self.tiles, raw_paths = level_entry["creator"]()
        mapa = self.level_config["mapa"]
        map_width, map_height = dimensiones_mapa(mapa)
        offset_x = max(0, (settings.SCREEN_WIDTH - map_width) // 2)
        offset_y = max(0, (settings.SCREEN_HEIGHT - map_height) // 2)
        self.map_offset = (offset_x, offset_y)

        if self.tiles:
            for tile in self.tiles:
                tile.rect.x += offset_x
                tile.rect.y += offset_y

        self.paths = [convertir_camino_a_pixeles(camino, self.map_offset) for camino in raw_paths if camino]
        if not self.paths:
            fallback = obtener_posiciones_por_tipo(mapa, 1)
            if fallback:
                self.paths = [convertir_camino_a_pixeles(fallback, self.map_offset)]

        build_coords = obtener_posiciones_por_tipo(mapa, 2)
        self.spots = [
            BuildSpot(
                (
                    col * TILE_SIZE + TILE_SIZE // 2 + offset_x,
                    fila * TILE_SIZE + TILE_SIZE // 2 + offset_y,
                )
            )
            for col, fila in build_coords
        ]
        for spot in self.spots:
            spot.occupied = False

        # Reinicio de estado jugable
        self.towers = []
        self.enemies = []
        self.spawn_timer = 0.0
        multipliers = self.level_config.get("multiplicadores", {})
        self.speed_multiplier = multipliers.get("velocidad", 1.0)
        self.health_multiplier = multipliers.get("salud", 1.0)
        lambda_multiplier = multipliers.get("lambda", 1.0)
        self.lambda_base = settings.LAMBDA_RATE * lambda_multiplier
        crecimiento = self.level_config.get("crecimiento_oleada", {})
        self.wave_speed_growth = crecimiento.get("velocidad", 1.05)
        self.wave_health_growth = crecimiento.get("salud", 1.1)
        self.enemy_tiers = self.level_config.get("enemigos", [])
        self.enemy_interval = random.expovariate(self.lambda_base)
        self.wave = 1
        self.target_waves = self.level_config.get("oleadas_victoria", 5)
        self.enemies_per_wave = 6 + index * 2
        self.spawned_in_wave = 0
        self.wave_active = True
        self.money = self.level_config.get("dinero_inicial", settings.STARTING_MONEY)
        self.total_spawned = 0
        self.lives = self.level_config.get("vidas_inicial", settings.MAX_LIVES)
        self.metrics_panel.visible = False
        self.overlay_buttons = []
        self._wave_was_active = True
        self.pause_button["text"] = "Menú"
        self.state = "playing"
        print(f"--- Inicia Nivel {index + 1}: {self.level_config['nombre']} ---")

    def restart_level(self):
        if self.current_level_index is not None:
            self.load_level(self.current_level_index)

    def enter_pause_menu(self):
        if self.state != "playing":
            return
        self._wave_was_active = self.wave_active
        self.wave_active = False
        self.state = "paused"
        self.pause_button["text"] = "Reanudar"
        self._set_overlay_buttons(
            [
                ("Continuar", self.resume_from_pause),
                ("Reiniciar nivel", self.restart_level),
                ("Volver al menú", self.back_to_menu),
            ]
        )

    def resume_from_pause(self):
        if self.state != "paused":
            return
        self.overlay_buttons = []
        self.state = "playing"
        self.wave_active = self._wave_was_active
        self.pause_button["text"] = "Menú"

    def advance_to_next_level(self):
        if self.current_level_index is None:
            return
        if self.current_level_index < len(self.levels) - 1:
            self.load_level(self.current_level_index + 1)
        else:
            self.back_to_menu()

    def back_to_menu(self):
        self.state = "menu"
        self.current_level_index = None
        self.level_config = None
        self.tiles = None
        self.paths = []
        self.spots = []
        self.towers = []
        self.enemies = []
        self.wave = 0
        self.target_waves = 0
        self.enemies_per_wave = 0
        self.spawned_in_wave = 0
        self.wave_active = False
        self.money = settings.STARTING_MONEY
        self.lives = settings.MAX_LIVES
        self.metrics_panel.visible = False
        self.overlay_buttons = []
        self._wave_was_active = True
        self.pause_button["text"] = "Menú"

    # ------------------------------------------------------------------
    # Lógica principal del juego
    # ------------------------------------------------------------------

    def calculate_metrics(self):
        c = len(self.towers)
        λ = round(self.lambda_base, 2)
        μ = round(settings.TOWER_FIRE_RATE, 2)
        ρ = round(λ / (c * μ), 3) if c > 0 else 0
        L = len(self.enemies)
        return {"λ": λ, "μ": μ, "c": c, "ρ": ρ, "Enemigos (L)": L}


    def update(self, dt):
        if self.state != "playing":
            return
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
                if self.wave >= self.target_waves:
                    self.handle_level_complete()
                else:
                    self.next_wave()

        # Actualizar enemigos (posición, vida)
        for enemy in list(self.enemies):
            enemy.update(dt)

            # Si el enemigo llega al final del camino, se pierde una vida
            if enemy.index >= len(enemy.path) - 1:
                self.enemies.remove(enemy)
                self.lives -= 1
                if self.lives <= 0:
                    self.trigger_game_over()

        # Eliminar enemigos muertos y sumar dinero
        for enemy in list(self.enemies):
            if not enemy.alive:
                self.money += enemy.reward
                self.enemies.remove(enemy)

        # Actualizar torres y proyectiles
        for tower in self.towers:
            tower.update(self.enemies)


    def spawn_enemy(self):
        if not self.paths:
            return
        path = random.choice(self.paths)

        
        skin_index = 0
        if self.current_level_index is not None:
            skin_index = min(self.current_level_index, 3)
            sprite_set=str(skin_index + 1),


        tier = self._choose_enemy_tier()

        velocidad_factor = tier.get("velocidad_factor", 1.0)
        salud_factor = tier.get("salud_factor", 1.0)
        enemy = Enemy(
            path,
            speed_range=tier.get("velocidad", (1.5, 3.0)),
            health_range=tier.get("salud", (80, 150)),
            reward=tier.get("recompensa"),
            speed_multiplier=self.speed_multiplier * velocidad_factor,
            health_multiplier=self.health_multiplier * salud_factor,
            radius=tier.get("radio", 10),
            color=tier.get("color"),
        )
        self.enemies.append(enemy)
        self.total_spawned += 1

    

    def next_wave(self):
       
        # Inicia la siguiente oleada, aumentando dificultad.
        self.wave += 1
        self.enemies_per_wave = int(self.enemies_per_wave * 1.2) + 2
        self.lambda_base *= 1.08
        self.speed_multiplier *= self.wave_speed_growth
        self.health_multiplier *= self.wave_health_growth
        self.spawned_in_wave = 0
        self.wave_active = True
        self.enemy_interval = random.expovariate(self.lambda_base)
        print(f"--- Inicia Oleada {self.wave} ---")
        print(
            f"Multiplicadores actuales -> Velocidad: {self.speed_multiplier:.2f}, Salud: {self.health_multiplier:.2f}"
        )

    def _choose_enemy_tier(self) -> dict:
        if not self.enemy_tiers:
            return {}
        pesos = [max(0.0, tier.get("peso", 1.0)) for tier in self.enemy_tiers]
        if sum(pesos) <= 0:
            pesos = None
        return random.choices(self.enemy_tiers, weights=pesos, k=1)[0]

    @staticmethod
    def _format_multiplier(multiplier: float) -> str:
        delta = (multiplier - 1.0) * 100
        if abs(delta) < 0.05:
            return "±0%"
        signo = "+" if delta > 0 else ""
        return f"{signo}{delta:.1f}%"

    def trigger_game_over(self):
        if self.state != "playing":
            return
        self.state = "game_over"
        self.wave_active = False
        self._set_overlay_buttons([
            ("Reintentar", self.restart_level),
            ("Volver al menú", self.back_to_menu),
        ])

    def handle_level_complete(self):
        self.wave_active = False
        self.state = "victory" if self.current_level_index == len(self.levels) - 1 else "level_complete"
        options = []
        if self.state == "level_complete":
            options.append(("Siguiente nivel", self.advance_to_next_level))
            options.append(("Volver al menú", self.back_to_menu))
        else:
            options.append(("Reintentar", self.restart_level))
            options.append(("Volver al menú", self.back_to_menu))
        self._set_overlay_buttons(options)

    def _set_overlay_buttons(self, options):
        center_x = settings.SCREEN_WIDTH // 2
        start_y = settings.SCREEN_HEIGHT // 2 + 40
        spacing = 80
        self.overlay_buttons = []
        for idx, (label, action) in enumerate(options):
            center = (center_x, start_y + idx * spacing)
            self.overlay_buttons.append(self._make_button(label, center, action))

    # ------------------------------------------------------------------
    # Interacción de usuario
    # ------------------------------------------------------------------
    def handle_click(self, pos):
        if self.state == "menu":
            for button in self.menu_buttons:
                if button["rect"].collidepoint(pos):
                    button["action"]()
                    break
            return
        
        if self.state in {"playing", "paused"}:
            if self.pause_button["rect"].collidepoint(pos):
                if self.state == "playing":
                    self.enter_pause_menu()
                else:
                    self.resume_from_pause()
                return
        
        if self.state == "playing":
            if self.metrics_panel.handle_click(pos):
                return
            
            for spot in self.spots:
                if spot.rect.collidepoint(pos) and not spot.occupied:
                    if self.money >= settings.TOWER_COST:
                        self.money -= settings.TOWER_COST
                        self.towers.append(Tower(spot.pos))
                        spot.occupied = True
                    return
        elif self.state in {"game_over", "level_complete", "victory", "paused"}:
            for button in self.overlay_buttons:
                if button["rect"].collidepoint(pos):
                    button["action"]()
                    break

    # ------------------------------------------------------------------
    # Renderizado
    # ------------------------------------------------------------------


    def draw(self, surface):
        surface.fill(settings.COLORS["bg"])

        if self.state == "menu":
            self._draw_menu(surface)
            return

        if self.tiles:
            self.tiles.draw(surface)
        for spot in self.spots:
            spot.draw(surface)
        for tower in self.towers:
            tower.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
        self._draw_hud(surface)

        if self.state in {"game_over", "level_complete", "victory", "paused"}:

            self._draw_overlay(surface)

    def _draw_hud(self, surface):
        level_text = "-" if self.current_level_index is None else str(self.current_level_index + 1)
        ui_text = self.font.render(
            f"Nivel: {level_text}/{len(self.levels)} | Oleada: {self.wave}/{self.target_waves} | $ {self.money}",
            True,
            (255, 255, 255),
        )
        surface.blit(ui_text, (10, 10))

        # Botón de métricas
        lives_text = self.font.render(f"Vidas restantes: {self.lives}", True, (255, 200, 200))
        surface.blit(lives_text, (10, 40))


        if self.state in {"playing", "paused"}:
            self._draw_button(surface, self.pause_button)

    def _draw_menu(self, surface):
        title = self.title_font.render("Tower Defense - Selección de mapas", True, (255, 255, 255))
        title_rect = title.get_rect(center=(settings.SCREEN_WIDTH // 2, 120))
        surface.blit(title, title_rect)

        subtitle = self.font.render(
            "Elige un nivel: cada mapa aumenta la dificultad y modifica la ruta.",
            True,
            (200, 200, 200),
        )
        subtitle_rect = subtitle.get_rect(center=(settings.SCREEN_WIDTH // 2, 170))
        surface.blit(subtitle, subtitle_rect)

        for button in self.menu_buttons:
            self._draw_button(surface, button)
            idx = button.get("level_index")
            if idx is None:
                continue
            config = self.levels[idx]["config"]
            multipliers = config.get("multiplicadores", {})
            salud_pct = self._format_multiplier(multipliers.get("salud", 1.0))
            vel_pct = self._format_multiplier(multipliers.get("velocidad", 1.0))
            lambda_pct = self._format_multiplier(multipliers.get("lambda", 1.0))
            info = self.font.render(
                " | ".join(
                    [
                        f"Oleadas: {config.get('oleadas_victoria', 0)}",
                        f"Salud {salud_pct}",
                        f"Velocidad {vel_pct}",
                        f"Aparición {lambda_pct}",
                    ]
                ),                True,
                (180, 180, 180),
            )
            info_rect = info.get_rect(center=(button["rect"].centerx, button["rect"].bottom + 18))
            surface.blit(info, info_rect)

    def _draw_overlay(self, surface):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        if self.state == "game_over":
            title_text = "¡Derrota!"
            message = "3 enemigos alcanzaron la meta."
        elif self.state == "level_complete":
            title_text = "Nivel completado"
            message = "Prepárate para un desafío mayor."
        elif self.state == "victory":
            title_text = "¡Victoria total!"
            message = "Has superado todos los mapas disponibles."
        else:
            title_text = "Menú de pausa"
            message = "Selecciona una opción para continuar."

        title = self.title_font.render(title_text, True, (255, 255, 255))
        title_rect = title.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 80))
        surface.blit(title, title_rect)

        message_text = self.font.render(message, True, (220, 220, 220))
        message_rect = message_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 30))
        surface.blit(message_text, message_rect)

        for button in self.overlay_buttons:
            self._draw_button(surface, button)

    def _draw_button(self, surface, button):
        rect = button["rect"]
        pygame.draw.rect(surface, (70, 120, 200), rect, border_radius=10)
        pygame.draw.rect(surface, (30, 40, 70), rect, 2, border_radius=10)
        label = self.button_font.render(button["text"], True, (255, 255, 255))
        label_rect = label.get_rect(center=rect.center)
        surface.blit(label, label_rect)

