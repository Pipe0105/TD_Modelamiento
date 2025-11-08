# game/settings.py
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Escalado simple (1.5x de tamaño original)
SCALE = 1.5

# parametros de simulacion visual
LAMBDA_RATE = 0.5

# Camino temporal (lista de coordenadas)
PATH = [(int(x * SCALE), int(y * SCALE)) for (x, y) in [
    (50, 450),

    (50, 300), (150, 300), (250, 250),
    (350, 250), (500, 300), (800,300),

    (800, 50),   (500,50),( 500,100), (550,100),
     
    

    (550, 500)

]]

# Lugares donde se pueden colocar torres
BUILD_SPOTS = [(int(x * SCALE), int(y * SCALE)) for (x, y) in [
    (100, 150), (400, 150), (700, 200), (700, 400) , (300,450)  #añae otr atore en
]]


# Economia
STARTING_MONEY = 100
TOWER_COST = 50
ENEMY_REWARD = 15

# Torres

TOWER_RANGE = 700       # antes 220
TOWER_FIRE_RATE = 12   # antes 1.5
PROJECTILE_SPEED = 40  #antes 6
PROJECTILE_DAMAGE = 2 # antes 200


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