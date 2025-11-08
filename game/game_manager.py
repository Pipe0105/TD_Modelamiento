# game/game_manager.py
import random
from typing import List, Optional
from pathlib import Path

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
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.description_font = pygame.font.SysFont("Arial", 20)


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
        self.build_menu: dict | None = None


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
        base_y = settings.SCREEN_HEIGHT // 2 - (len(self.levels) * 96) // 2
        for idx, level in enumerate(self.levels):
            config = level["config"]
            center = (center_x, base_y + idx * 110)
            subtitle = self._format_level_summary(config)
            buttons.append(
                self._make_button(
                    config["nombre"],
                    center,
                    lambda index=idx: self.load_level(index),
                    level_index=idx,
                    subtitle=subtitle,
                    size=(420, 86),
                )
            )
        return buttons


    def _make_button(
        self,
        text,
        center,
        action,
        level_index=None,
        size=(320, 60),
        subtitle: str | None = None,
    ) -> dict:
        rect = pygame.Rect(0, 0, *size)
        rect.center = center
        return {
            "rect": rect,
            "text": text,
            "action": action,
            "level_index": level_index,
            "subtitle": subtitle,
        }

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
        self.build_menu = None


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
        self.close_tower_menu()
        self.close_build_menu()
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
        self.build_menu = None

        self._wave_was_active = True
        self.pause_button["text"] = "Menú"

    # ------------------------------------------------------------------
    # Lógica principal del juego
    # ------------------------------------------------------------------

    def calculate_metrics(self):
        c = len(self.towers)
        λ = round(self.lambda_base, 2)
        if c > 0:
            avg_fire_rate = sum(tower.fire_rate for tower in self.towers) / c
        else:
            avg_fire_rate = settings.TOWER_FIRE_RATE
        μ = round(avg_fire_rate, 2)
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
    
    def _format_level_summary(self, config: dict) -> str:
        waves = config.get("oleadas_victoria")
        money = config.get("dinero_inicial", settings.STARTING_MONEY)
        lives = config.get("vidas_inicial", settings.MAX_LIVES)
        multipliers = config.get("multiplicadores", {})
        vel = multipliers.get("velocidad", 1.0)
        hp = multipliers.get("salud", 1.0)

        waves_text = f"{waves} oleadas" if waves else "Oleadas variables"
        summary_parts = [waves_text, f"$ {money} inicial", f"{lives} vidas"]

        vel_text = self._format_multiplier(vel)
        hp_text = self._format_multiplier(hp)
        summary_parts.append(f"Vel {vel_text}")
        summary_parts.append(f"Salud {hp_text}")

        return " · ".join(summary_parts)

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

            if self.build_menu and self._handle_build_menu_click(pos):
                
                return

            if self.tower_menu and self._handle_tower_menu_click(pos):
                return

            tower = self._get_tower_at(pos)
            if tower:
                self.close_build_menu()

                if self.tower_menu and self.tower_menu.get("tower") is tower:
                    self.close_tower_menu()
                else:
                    self.open_tower_menu(tower)
                return

            for spot in self.spots:
                if spot.rect.collidepoint(pos) and not spot.occupied:
                    if self.build_menu and self.build_menu.get("spot") is spot:
                        self.close_build_menu()
                    else:
                        self.open_build_menu(spot)
                    self.close_tower_menu()
                    return

            if self.tower_menu:
                self.close_tower_menu()
            if self.build_menu:
                self.close_build_menu()
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

        button_width = 230
        button_height = 64
        spacing = 10
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

    def open_build_menu(self, spot: BuildSpot):
        if not settings.TOWER_TYPES:
            self.build_menu = None
            return

        options = sorted(
            settings.TOWER_TYPES.items(),
            key=lambda item: item[1].get("cost", settings.TOWER_COST),
        )

        button_width = 300
        button_height = 96
        spacing = 12
        total_height = len(options) * button_height + (len(options) - 1) * spacing

        x_offset = max(80, settings.TILE_SIZE)
        x = spot.pos[0] + x_offset
        if x + button_width + 10 > settings.SCREEN_WIDTH:
            x = spot.pos[0] - x_offset - button_width
        x = max(20, min(settings.SCREEN_WIDTH - button_width - 20, x))

        y = spot.pos[1] - total_height // 2
        y = max(20, min(settings.SCREEN_HEIGHT - total_height - 20, y))

        buttons: list[dict] = []
        current_y = y
        for type_key, config in options:
            rect = pygame.Rect(x, current_y, button_width, button_height)
            buttons.append({
                "rect": rect,
                "type": type_key,
                "config": dict(config),
            })
            current_y += button_height + spacing

        if not buttons:
            self.build_menu = None
            return

        panel_rect = buttons[0]["rect"].copy()
        for btn in buttons[1:]:
            panel_rect.union_ip(btn["rect"])
        panel_rect.inflate_ip(24, 24)

        self.build_menu = {
            "spot": spot,
            "buttons": buttons,
            "panel_rect": panel_rect,
            "blocked": None,
        }

    def close_build_menu(self):
        self.build_menu = None

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

    def _handle_build_menu_click(self, pos) -> bool:
        if not self.build_menu:
            return False

        for button in self.build_menu.get("buttons", []):
            rect = button.get("rect")
            if rect is not None and rect.collidepoint(pos):
                self._attempt_build_tower(button)
                return True
        return False

    def _attempt_build_tower(self, button: dict):
        if not self.build_menu:
            return

        spot: BuildSpot | None = self.build_menu.get("spot")
        if spot is None or spot.occupied:
            return

        tower_type = button.get("type")
        if not tower_type:
            return
        config = button.get("config", {})
        cost = config.get("cost", settings.TOWER_COST)

        if self.money < cost:
            self.build_menu["blocked"] = tower_type
            return

        tower = Tower(spot.pos, tower_type)
        self.towers.append(tower)
        self.money -= cost
        spot.occupied = True
        self.close_build_menu()
        self.close_tower_menu()

    def _draw_tower_menu(self, surface):
        if not self.tower_menu:
            return

        tower: Tower | None = self.tower_menu.get("tower")
        if tower is None:
            return
        
        tower_rect = tower.get_rect()
        name_pos = (tower.pos[0], tower_rect.top - 6)
        self._draw_text_with_shadow(
            surface,
            self.small_font,
            tower.name,
            (250, 250, 255),
            name_pos,
            anchor="midbottom",
        )

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
            base_color = (42, 48, 72) if enabled else (28, 32, 48)
            top_color = tuple(min(255, c + 30) for c in base_color)
            bottom_color = tuple(max(0, c - 20) for c in base_color)
            for y in range(rect.height):
                blend = y / max(1, rect.height - 1)
                color = tuple(
                    int(top_color[i] * (1 - blend) + bottom_color[i] * blend)
                    for i in range(3)
                )
                alpha = 245 if enabled else 180
                pygame.draw.line(panel, (*color, alpha), (0, y), (rect.width, y))
            surface.blit(panel, rect.topleft)

            border_color = (150, 210, 120) if enabled else (120, 130, 150)
            pygame.draw.rect(surface, border_color, rect, width=2, border_radius=10)

            padding_x = 16
            padding_y = 10

            label = config.get("label", key.title())
            increment = config.get("increment")
            if isinstance(increment, float):
                inc_text = f"+{increment:.1f}" if increment else ""
            else:
                inc_text = f"+{increment}" if increment else ""

            title_text = label if not inc_text else f"{label} {inc_text}"
            title_color = (245, 245, 245) if enabled else (180, 180, 180)
            title_rect = self._draw_text_with_shadow(
                surface,
                self.button_font,
                title_text,
                title_color,
                (rect.left + padding_x, rect.top + padding_y),
                anchor="topleft",
            )

            description = config.get("description")
            if description:
                desc_color = (215, 220, 240) if enabled else (160, 160, 180)
                self._draw_text_with_shadow(
                    surface,
                    self.small_font,
                    description,
                    desc_color,
                    (rect.left + padding_x, title_rect.bottom + 4),
                    anchor="topleft",
                )

            if not can_upgrade:
                status_text = "Nivel máximo alcanzado"
            else:
                cost = config.get("cost", 0)
                status_text = f"Costo: $ {cost}"
                if not affordable:
                    status_text += " · Reúne más recursos"

            if max_level:
                level_text = f"Nivel {level}/{max_level}"
            else:
                level_text = f"Nivel {level}"

            status_color = (225, 230, 240) if enabled else (170, 150, 150)
            status_rect = self._draw_text_with_shadow(
                surface,
                self.small_font,
                status_text,
                status_color,
                (rect.left + padding_x, rect.bottom - 24),
                anchor="topleft",
            )

            level_badge = pygame.Surface((110, 30), pygame.SRCALPHA)
            level_badge.fill((255, 255, 255, 40))
            badge_rect = level_badge.get_rect()
            badge_rect.topright = (rect.right - 16, rect.top + padding_y)
            surface.blit(level_badge, badge_rect.topleft)
            self._draw_text_with_shadow(
                surface,
                self.small_font,
                level_text,
                (240, 240, 255),
                badge_rect.center,
            )

    def _draw_build_menu(self, surface):
        if not self.build_menu:
            return

        spot: BuildSpot | None = self.build_menu.get("spot")
        if spot and not spot.occupied:
            pygame.draw.circle(surface, (240, 220, 140), spot.pos, spot.size // 2 + 12, 3)

        panel_rect: pygame.Rect | None = self.build_menu.get("panel_rect")
        if panel_rect:
            backdrop = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            backdrop.fill((10, 14, 24, 180))
            surface.blit(backdrop, panel_rect.topleft)

        if spot and panel_rect:
            if panel_rect.centerx > spot.pos[0]:
                anchor = panel_rect.midleft
            else:
                anchor = panel_rect.midright
            pygame.draw.line(surface, (220, 230, 255), spot.pos, anchor, 2)

        blocked_type = self.build_menu.get("blocked")

        for button in self.build_menu.get("buttons", []):
            rect = button.get("rect")
            if rect is None:
                continue

            config = button.get("config", {})
            cost = config.get("cost", settings.TOWER_COST)
            affordable = self.money >= cost
            if affordable and blocked_type == button.get("type"):
                self.build_menu["blocked"] = None
                blocked_type = None

            base_color = (70, 82, 132) if affordable else (45, 48, 72)
            top_color = tuple(min(255, c + 30) for c in base_color)
            bottom_color = tuple(max(0, c - 24) for c in base_color)
            card = pygame.Surface(rect.size, pygame.SRCALPHA)
            for y in range(rect.height):
                blend = y / max(1, rect.height - 1)
                color = tuple(
                    int(top_color[i] * (1 - blend) + bottom_color[i] * blend)
                    for i in range(3)
                )
                alpha = 240 if affordable else 190
                pygame.draw.line(card, (*color, alpha), (0, y), (rect.width, y))
            surface.blit(card, rect.topleft)

            border_color = (180, 200, 255) if affordable else (110, 120, 150)
            pygame.draw.rect(surface, border_color, rect, width=2, border_radius=12)

            title_color = (250, 250, 255) if affordable else (190, 190, 210)
            desc_color = (225, 230, 250) if affordable else (160, 165, 190)
            stats_color = (210, 220, 240) if affordable else (150, 150, 180)

            padding_x = 20
            padding_y = 14

            label = config.get("label", button.get("type", "Torre"))
            title_rect = self._draw_text_with_shadow(
                surface,
                self.button_font,
                label,
                title_color,
                (rect.left + padding_x, rect.top + padding_y),
                anchor="topleft",
            )

            description = config.get("description")
            if description:
                self._draw_text_with_shadow(
                    surface,
                    self.description_font,
                    description,
                    desc_color,
                    (rect.left + padding_x, title_rect.bottom + 4),
                    anchor="topleft",
                )

            stats_lines = []
            rango = config.get("range")
            fire_rate = config.get("fire_rate")
            damage = config.get("damage")
            projectile_speed = config.get("projectile_speed")

            first_line_parts = []
            if rango is not None:
                first_line_parts.append(f"Rango {rango}px")
            if fire_rate is not None:
                first_line_parts.append(f"Cadencia {fire_rate}/s")
            if first_line_parts:
                stats_lines.append(" · ".join(first_line_parts))

            second_line_parts = []
            if damage is not None:
                second_line_parts.append(f"Daño {damage}")
            if projectile_speed is not None:
                second_line_parts.append(f"Vel proyectil {projectile_speed}px/s")
            if second_line_parts:
                stats_lines.append(" · ".join(second_line_parts))
            stats_y = rect.bottom - 48
            for line in stats_lines:
                if not line:
                    continue
                self._draw_text_with_shadow(
                    surface,
                    self.small_font,
                    line,
                    stats_color,
                    (rect.left + padding_x, stats_y),
                    anchor="topleft",
                )
                stats_y += 18

            badge_width = 140
            badge_height = 40
            badge_rect = pygame.Rect(0, 0, badge_width, badge_height)
            badge_rect.bottomright = (rect.right - 18, rect.bottom - 14)
            badge_panel = pygame.Surface(badge_rect.size, pygame.SRCALPHA)
            badge_color = (255, 230, 130, 240) if affordable else (160, 140, 150, 220)
            badge_panel.fill(badge_color)
            surface.blit(badge_panel, badge_rect.topleft)

            coin_center = (badge_rect.left + 18, badge_rect.centery)
            pygame.draw.circle(surface, (245, 205, 80), coin_center, 10)
            pygame.draw.circle(surface, (220, 180, 60), coin_center, 10, 2)
            coin_text = self.small_font.render("$", True, (60, 40, 20))
            coin_rect = coin_text.get_rect(center=coin_center)
            surface.blit(coin_text, coin_rect)

            cost_text = f"{cost}"
            self._draw_text_with_shadow(
                surface,
                self.button_font,
                cost_text,
                (40, 40, 40) if affordable else (90, 60, 60),
                (badge_rect.left + 36, badge_rect.centery),
                anchor="midleft",
            )

            if not affordable and blocked_type == button.get("type"):
                warning_text = "Dinero insuficiente"
                self._draw_text_with_shadow(
                    surface,
                    self.small_font,
                    warning_text,
                    (255, 160, 160),
                    (badge_rect.centerx, badge_rect.top - 6),
                )
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

        if self.build_menu:
            self._draw_build_menu(surface)

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

    def _draw_button(self, surface, button: dict, *, highlight: bool = False):
        """Renderiza un botón genérico usado en menús y overlays."""

        rect: pygame.Rect | None = button.get("rect")
        if rect is None:
            return

        text = button.get("text", "")
        subtitle = button.get("subtitle")
        level_index = button.get("level_index")

        base_color = (68, 74, 102)
        border_color = (150, 160, 210)
        text_color = (245, 245, 255)

        if highlight:
            base_color = (98, 110, 160)
            border_color = (200, 210, 255)

        # Sombra
        shadow_rect = rect.move(0, 6)
        shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
        shadow.fill((10, 10, 20, 120))
        surface.blit(shadow, shadow_rect.topleft)

        # Panel con degradado
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        top_color = tuple(min(255, c + 24) for c in base_color)
        bottom_color = tuple(max(0, c - 18) for c in base_color)
        for y in range(rect.height):
            blend = y / max(1, rect.height - 1)
            color = tuple(
                int(top_color[i] * (1 - blend) + bottom_color[i] * blend) for i in range(3)
            )
            pygame.draw.line(panel, (*color, 230), (0, y), (rect.width, y))
        surface.blit(panel, rect.topleft)

        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=12)

        padding_x = 24
        padding_y = 16
        if text:
            title_pos = (rect.left + padding_x, rect.top + padding_y)
            title_rect = self._draw_text_with_shadow(
                surface,
                self.button_font,
                text,
                text_color,
                title_pos,
                anchor="topleft",
            )
        else:
            title_rect = pygame.Rect(rect.left + padding_x, rect.top + padding_y, 0, 0)

        if subtitle:
            subtitle_color = (220, 225, 240)
            self._draw_text_with_shadow(
                surface,
                self.description_font,
                subtitle,
                subtitle_color,
                (rect.left + padding_x, title_rect.bottom + 6),
                anchor="topleft",
            )

        if level_index is not None:
            badge_text = f"Nivel {level_index + 1}"
            badge_surf = self.small_font.render(badge_text, True, (20, 25, 40))
            badge_padding = 10
            badge_rect = badge_surf.get_rect()
            badge_rect.width += badge_padding * 2
            badge_rect.height += 8
            badge_rect.topright = (rect.right - padding_x, rect.top + padding_y - 6)
            badge_panel = pygame.Surface(badge_rect.size, pygame.SRCALPHA)
            badge_panel.fill((230, 230, 255, 235))
            surface.blit(badge_panel, badge_rect.topleft)
            surface.blit(
                badge_surf,
                (
                    badge_rect.left + badge_padding,
                    badge_rect.top + 4,
                ),
            )

    def _draw_text_with_shadow(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        color,
        position,
        *,
        anchor: str = "center",
        shadow_offset: tuple[int, int] = (2, 2),
        shadow_alpha: int = 150,
    ) -> pygame.Rect:
        """Dibuja texto con una ligera sombra para mejorar la legibilidad."""

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        if hasattr(text_rect, anchor):
            setattr(text_rect, anchor, position)
        else:
            text_rect.center = position

        shadow_surface = font.render(text, True, (0, 0, 0))
        shadow_surface.set_alpha(shadow_alpha)
        shadow_rect = text_rect.copy()
        shadow_rect.x += shadow_offset[0]
        shadow_rect.y += shadow_offset[1]

        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)
        return text_rect

    def _draw_menu(self, surface):
        header_rect = pygame.Rect(0, 0, settings.SCREEN_WIDTH, 220)
        header = pygame.Surface(header_rect.size, pygame.SRCALPHA)
        top_color = (40, 45, 70)
        bottom_color = (20, 24, 40)
        for y in range(header_rect.height):
            blend = y / max(1, header_rect.height - 1)
            color = tuple(
                int(top_color[i] * (1 - blend) + bottom_color[i] * blend) for i in range(3)
            )
            pygame.draw.line(header, (*color, 200), (0, y), (header_rect.width, y))
        surface.blit(header, header_rect)

        title_rect = self._draw_text_with_shadow(
            surface,
            self.title_font,
            "Tower Defense - Selección de mapas",
            (255, 255, 255),
            (settings.SCREEN_WIDTH // 2, 110),
        )

        subtitle_rect = self._draw_text_with_shadow(
            surface,
            self.font,
            "Elige un mapa para comenzar la partida",
            (220, 220, 220),
            (settings.SCREEN_WIDTH // 2, title_rect.bottom + 30),
        )

        for button in self.menu_buttons:
            highlight = button.get("level_index") == self.current_level_index
            self._draw_button(surface, button, highlight=highlight)

    def _draw_overlay(self, surface):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((15, 15, 25, 180))
        surface.blit(overlay, (0, 0))

        titles = {
            "paused": "Juego en pausa",
            "game_over": "¡Derrota!",
            "level_complete": "Nivel completado",
            "victory": "¡Victoria!",
        }

        title_text = titles.get(self.state)
        if title_text:
            title_surf = self.title_font.render(title_text, True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 140))
            surface.blit(title_surf, title_rect)

        if self.state == "paused":
            info = "Puedes reanudar o gestionar el nivel desde el menú"