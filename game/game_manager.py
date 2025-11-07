# game/game_manager.py
import random
from typing import List, Optional
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

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
        root = tk.Tk()
        root.withdraw()
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 26)
        self.small_font = pygame.font.SysFont("Arial", 18)

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
        self.tower_menu: dict | None = None

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
        available_sprite_sets = self._get_available_sprite_sets()
        self.enemy_tiers = self._prepare_enemy_tiers(
            self.level_config.get("enemigos", []), available_sprite_sets
        )
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
        self.tower_menu = None

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
        self.tower_menu = None

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



        tier = self._choose_enemy_tier()
        sprite_set = str(tier.get("sprite_set", "1")) if tier else "1"


        velocidad_factor = tier.get("velocidad_factor", 1.0)
        salud_factor = tier.get("salud_factor", 1.0)
        enemy = Enemy(
            path,
            speed_range=tier.get("velocidad", (1.5, 3.0)),
            health_range=tier.get("salud", (80, 150)),
            reward=tier.get("recompensa"),
            speed_multiplier=self.speed_multiplier * velocidad_factor,
            health_multiplier=self.health_multiplier * salud_factor,
            sprite_set=sprite_set,
            radius=tier.get("radio"),
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
    def _get_available_sprite_sets() -> list[str]:
        base_path = (
            Path(__file__).resolve().parents[1] / "maps" / "assets" / "images" / "enemy"
        )
        if not base_path.exists():
            return ["1"]

        sprite_sets = [entry.name for entry in base_path.iterdir() if entry.is_dir()]
        return sorted(sprite_sets)

    @staticmethod
    def _prepare_enemy_tiers(tiers: list[dict], sprite_sets: list[str]) -> list[dict]:
        if not tiers:
            return []
        if not sprite_sets:
            sprite_sets = ["1"]

        prepared: list[dict] = []

        for idx, tier in enumerate(tiers):
            tier_copy = dict(tier)
            if "sprite_set" in tier_copy and tier_copy["sprite_set"]:
                tier_copy["sprite_set"] = str(tier_copy["sprite_set"])
            else:
                sprite_index = idx % len(sprite_sets)
                tier_copy["sprite_set"] = sprite_sets[sprite_index]
            prepared.append(tier_copy)

        return prepared

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
            
            respuesta = messagebox.askyesno(
                 "Cuadro de diálogo", "¿Deseas continuar?"
                                                            )

            if self.tower_menu and self._handle_tower_menu_click(pos):
                return

            tower = self._get_tower_at(pos)
            if tower:
                if self.tower_menu and self.tower_menu.get("tower") is tower:
                    self.close_tower_menu()
                else:
                    self.open_tower_menu(tower)
                return

            for spot in self.spots:
                if spot.rect.collidepoint(pos) and not spot.occupied:
                    if self.money >= settings.TOWER_COST:
                        self.money -= settings.TOWER_COST
                        self.towers.append(Tower(spot.pos, respuesta))
                        spot.occupied = True
                        self.close_tower_menu()
                    return

            if self.tower_menu:
                self.close_tower_menu()
        elif self.state in {"game_over", "level_complete", "victory", "paused"}:
            for button in self.overlay_buttons:
                if button["rect"].collidepoint(pos):
                    button["action"]()
                    break

    def _get_tower_at(self, pos):
        for tower in reversed(self.towers):
            if tower.contains_point(pos):
                return tower
        return None

    def open_tower_menu(self, tower: Tower):
        total_buttons = len(settings.TOWER_UPGRADES)
        if total_buttons == 0:
            self.tower_menu = None
            return

        button_width = 190
        button_height = 44
        spacing = 8
        total_height = total_buttons * button_height + (total_buttons - 1) * spacing

        tower_rect = tower.get_rect()
        offset = tower_rect.width // 2 + 16
        x = tower.pos[0] + offset
        if x + button_width + 10 > settings.SCREEN_WIDTH:
            x = tower.pos[0] - offset - button_width
        x = max(10, min(settings.SCREEN_WIDTH - button_width - 10, x))

        y = tower.pos[1] - total_height // 2
        y = max(10, min(settings.SCREEN_HEIGHT - total_height - 10, y))

        buttons = []
        current_y = y
        for key in settings.TOWER_UPGRADES:
            rect = pygame.Rect(x, current_y, button_width, button_height)
            buttons.append({"rect": rect, "key": key})
            current_y += button_height + spacing

        self.tower_menu = {"tower": tower, "buttons": buttons}

    def close_tower_menu(self):
        self.tower_menu = None

    def _handle_tower_menu_click(self, pos) -> bool:
        if not self.tower_menu:
            return False

        for button in self.tower_menu.get("buttons", []):
            if button["rect"].collidepoint(pos):
                self._attempt_tower_upgrade(button["key"])
                return True
        return False

    def _attempt_tower_upgrade(self, key: str):
        if not self.tower_menu:
            return

        tower: Tower | None = self.tower_menu.get("tower")
        if tower is None:
            return

        config = settings.TOWER_UPGRADES.get(key)
        if not config:
            return

        if not tower.can_upgrade(key):
            return

        cost = config.get("cost", 0)
        if self.money < cost:
            return

        if tower.apply_upgrade(key):
            self.money -= cost
            self.open_tower_menu(tower)

    def _draw_tower_menu(self, surface):
        if not self.tower_menu:
            return

        tower: Tower | None = self.tower_menu.get("tower")
        if tower is None:
            return

        for button in self.tower_menu.get("buttons", []):
            key = button.get("key")
            rect = button.get("rect")
            if rect is None or key is None:
                continue

            config = settings.TOWER_UPGRADES.get(key, {})
            max_level = config.get("max_level")
            level = tower.get_upgrade_level(key)
            can_upgrade = tower.can_upgrade(key)
            affordable = self.money >= config.get("cost", 0)
            enabled = can_upgrade and affordable

            panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            base_alpha = 220 if enabled else 140
            panel.fill((30, 35, 45, base_alpha))
            surface.blit(panel, rect.topleft)

            border_color = (130, 200, 100) if enabled else (120, 120, 120)
            pygame.draw.rect(surface, border_color, rect, width=2, border_radius=6)

            label = config.get("label", key.title())
            increment = config.get("increment")
            if isinstance(increment, float):
                inc_text = f"+{increment:.1f}" if increment else ""
            else:
                inc_text = f"+{increment}" if increment else ""

            title_text = label if not inc_text else f"{label} {inc_text}"
            title_color = (240, 240, 240) if enabled else (180, 180, 180)
            title_surf = self.button_font.render(title_text, True, title_color)
            title_rect = title_surf.get_rect(midtop=(rect.centerx, rect.top + 6))
            surface.blit(title_surf, title_rect)

            if not can_upgrade:
                status_text = "Máx."
            else:
                cost = config.get("cost", 0)
                status_text = f"$ {cost}"
                if not affordable:
                    status_text += " (no hay $)"

            if max_level:
                status_text += f" | Lv {level}/{max_level}"
            else:
                status_text += f" | Lv {level}"

            status_color = (210, 210, 210) if enabled else (170, 150, 150)
            status_surf = self.small_font.render(status_text, True, status_color)
            status_rect = status_surf.get_rect(midbottom=(rect.centerx, rect.bottom - 6))
            surface.blit(status_surf, status_rect)
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
            selected = self.tower_menu and self.tower_menu.get("tower") is tower
            tower.draw(surface, selected=bool(selected))
        for enemy in self.enemies:
            enemy.draw(surface)
        self._draw_hud(surface)

        if self.tower_menu:
            self._draw_tower_menu(surface)

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