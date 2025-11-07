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

# Torres

TOWER_RANGE = 220       # antes 150
TOWER_FIRE_RATE = 1.5   # antes 1.0
PROJECTILE_SPEED = 6
PROJECTILE_DAMAGE = 50

# Mejoras de torres (etiqueta, costo, incremento, nivel máximo opcional)
TOWER_UPGRADES = {
    "damage": {
        "label": "Daño",
        "cost": 70,
        "increment": 20,
        "max_level": 3,
    },
    "fire_rate": {
        "label": "Vel. disparo",
        "cost": 85,
        "increment": 0.5,
        "max_level": 3,
    },
    "range": {
        "label": "Rango",
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