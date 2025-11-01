# constants.py
# Game configuration and constants

# Window settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

# Board settings
BOARD_SIZE = 4
CELL_SIZE = 120
BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 100
INFO_PANEL_X = 550

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
BLUE = (50, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
YELLOW = (255, 255, 100)
DARK_BLUE = (30, 60, 180)
DARK_RED = (180, 30, 30)
PURPLE = (200, 100, 255)
ORANGE = (255, 165, 0)

# Game settings
MAX_TURNS = 30  # 25 turns per player
WIN_CONDITION_PLANETS = 12

# AI vs AI settings
AI_VS_AI_DELAY = 30  # Frames to wait between AI moves (0.5 seconds at 60fps)