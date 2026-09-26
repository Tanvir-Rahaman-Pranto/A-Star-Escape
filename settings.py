import pygame

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
TITLE = "A* Escape: The Living Network"

# Grid settings
TILE_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Cellular Automata / Map Gen Defaults (Step 2)
DEFAULT_FILL_PERCENT = 0.40
DEFAULT_SMOOTH_ITERATIONS = 4
DEFAULT_WALL_BIRTH_LIMIT = 4
DEFAULT_WALL_DEATH_LIMIT = 4

# Colors (Minimalist / High Contrast)
COLOR_BG = (20, 20, 25)        # Dark Slate / Almost Black
COLOR_WALL = (40, 40, 50)      # Darker Wall
COLOR_PATH = (200, 200, 220)   # Light Path
COLOR_PLAYER = (50, 200, 255)  # Cyan
COLOR_ENEMY = (255, 50, 50)    # Red
COLOR_PORTAL = (50, 255, 100)  # Green
COLOR_ENERGY = (255, 200, 50)  # Gold
COLOR_TEXT = (255, 255, 255)

# A* / Gameplay settings
MOVEMENT_COST_BASE = 10
MOVEMENT_COST_DIAGONAL = 14