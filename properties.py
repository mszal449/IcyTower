FRAMERATE = 144  # maksymalne fps
START_WINDOW_RESOLUTION = (1280, 720)  # wielksoc okna gry

# opcje animacji
ANIMATION_SPEED = {"walk":20, "idle":4}
ROTATION_START = 7
ROTATION_SPEED = 1.5
ROTATE_SPEED_SMOOTH = 50

# opcje kamery
CAMERA_SMOOTH = 10

# schodki
NEW_FLOOR_DISTANCE = 100

# opcje rozgrywki
TIME_SPEED_UP_INTERLUDE = {"easy": 2000,"medium": 1600,"hard": 1200}
CAMERA_SCROLL_SPEED = {"easy": 0.3,"medium": 0.4,"hard": 0.5}
SPEED_UP_MULTIPLIER = {"easy": 1.1,"medium": 1.2,"hard": 1.3}
MAX_SLAB_WIDTH = {"easy": 8,"medium": 6,"hard": 4}

# fizyka
GRAVITY = 0.14
JUMP_SPEED = -3  # wysokość skoku
ACCELERATION = 0.05  # prędkość przyspieszenia horyzontalnego
DECELERATION = 0.08  # prędkość spowolnienia horyzontalnego
WALL_BOUNCE = 0.3  # zachowanie energii przy odbiciu się od ściany

# combo
COMBO_TIMER_SPEED = 0.01

# particle
PARTICLE_COLORS = ((104, 81, 147), (85, 66, 120), (48, 52, 94), (65, 71, 128), (144, 47, 148), (180, 59, 185))
PARTICLE_SPAWN_AMOUNT = {"none": 0, "some": 2, "lots": 4}
# muzyka
MUSIC_VOLUME_DIFFERENCE = -0.3
