# game/settings.py
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 50

# Escalado simple (1.5x de tamaño original)
SCALE = 1.5

# parametros de simulacion visual

LAMBDA_RATE = 0.5
MAX_LIVES = 3

# Camino temporal (lista de coordenadas)
PATH = [(int(x * SCALE), int(y * SCALE)) for (x, y) in [
    (50, 300), (150, 300), (250, 250),
    (350, 250), (450, 300), (550, 350),
    (700, 350), (750, 400)
]]

# Lugares donde se pueden colocar torres
BUILD_SPOTS = [(int(x * SCALE), int(y * SCALE)) for (x, y) in [
    (200, 150), (400, 150), (600, 200)
]]


# Economia

STARTING_MONEY = 100
TOWER_COST = 50
ENEMY_REWARD = 15

# Tipos de torres disponibles
# Cada tipo define los atributos base de la torre y su costo específico.
# "guardian" es el tipo clásico equilibrado; "centinela" prioriza el alcance y daño;
# "ráfaga" dispara con mayor frecuencia pero con menor daño por proyectil.
TOWER_TYPES = {
    "guardian": {
        "label": "Torre Guardián",
        "description": "Equilibrada en alcance, daño y cadencia.",
        "cost": 55,
        "range": 420,
        "fire_rate": 10,
        "damage": 55,
        "projectile_speed": 8,
    },
    "centinela": {
        "label": "Torre Centinela",
        "description": "Gran alcance y daño, pero dispara más lento.",
        "cost": 75,
        "range": 780,
        "fire_rate": 5,
        "damage": 85,
        "projectile_speed": 9,
    },
    "rafaga": {
        "label": "Torre Ráfaga",
        "description": "Cadencia altísima para frenar grandes grupos.",
        "cost": 65,
        "range": 360,
        "fire_rate": 16,
        "damage": 40,
        "projectile_speed": 11,
    },
}

# Torres

TOWER_RANGE = 220       # antes 150
TOWER_FIRE_RATE = 1.5   # antes 1.0
PROJECTILE_SPEED = 6
PROJECTILE_DAMAGE = 50

# Mejoras de torres (etiqueta, costo, incremento, nivel máximo opcional)
TOWER_UPGRADES = {
    "damage": {
        "label": "Daño",
        "description": "Aumenta el daño directo por proyectil.",
        "cost": 70,
        "increment": 20,
        "max_level": 3,
    },
    "fire_rate": {
        "label": "Vel. disparo",
        "description": "Disminuye el tiempo entre disparos.",
        "cost": 85,
        "increment": 0.5,
        "max_level": 3,
    },
    "range": {
        "label": "Rango",
        "description": "Amplía el área de cobertura de la torre.",
        "cost": 60,
        "increment": 35,
        "max_level": 3,
    },
}

# colores (tema)

COLORS = {
    "bg": (30, 30, 40),
    "path": (120, 120, 120),
    "enemy": (200, 60, 60),
    "build_spot": (60, 120, 200),
    "tower": (60, 120, 220),
    "projectile": (255, 220, 50),
    "spot": (60, 120, 200),
}