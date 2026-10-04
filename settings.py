"""
settings.py  —  Week 3
OWNER: Member 1 — Tanvir Rahaman Pranto (Game & Maze Development)

Central configuration. Every other module imports from here, so nothing in this
file may import another project module.

Members 3 and 4 own some *values* (GA, adaptive enemy, penalties, brick wall
colors); Member 1 owns the file and the menu/difficulty values. Change a value
here, never as a magic number inside another module.
"""

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

# Colors (Minimalist / High Contrast)
COLOR_BG = (20, 20, 25)        # Dark Slate / Almost Black
COLOR_PATH = (200, 200, 220)   # Light Path
COLOR_PLAYER = (50, 200, 255)  # Cyan
COLOR_ENEMY = (255, 50, 50)    # Red
COLOR_PORTAL = (50, 255, 100)  # Green
COLOR_ENERGY = (255, 200, 50)  # Gold (used from Week 3)
COLOR_TEXT = (255, 255, 255)

# ---------------------------------------------------------------------------
# Week 3 — wall material (values owned by Member 4, Anindaw Nahian Omi)
# Brick replaces the flat Week 1/2 COLOR_WALL. Node.draw (grid.py) uses these
# to lay a two-tone running-bond brick pattern with mortar lines.
# ---------------------------------------------------------------------------
COLOR_WALL = (120, 58, 43)          # kept for anything that still wants a flat wall color
BRICK_COLOR_LIGHT = (134, 66, 50)   # lighter brick face
BRICK_COLOR_DARK = (104, 48, 36)    # darker brick face (alternates per row for texture)
BRICK_MORTAR = (58, 50, 46)         # mortar line color
BRICK_HEIGHT = 10                   # px, each brick "course"
BRICK_WIDTH_RATIO = 0.5             # brick width as a fraction of TILE_SIZE

# A* / Gameplay settings
MOVEMENT_COST_BASE = 10
MOVEMENT_COST_DIAGONAL = 14

# ---------------------------------------------------------------------------
# Map generation. The Week 1 fixed values are now the GA's STARTING genotype.
# ---------------------------------------------------------------------------
MAP_FILL_PERCENT = 0.40
MAP_SMOOTH_ITERATIONS = 4
MAP_WALL_BIRTH_LIMIT = 4
MAP_WALL_DEATH_LIMIT = 4

# ---------------------------------------------------------------------------
# Week 2 — genetic map generation (values owned by Member 4)
# ---------------------------------------------------------------------------
GA_POPULATION_SIZE = 6          # candidates evaluated per level
GA_SURVIVORS = 3                # top candidates kept as next generation's parents
GA_FITNESS_SAMPLES = 3          # random maps averaged per candidate (maps are random)
GA_MUTATION_RATE = 0.4          # chance each gene mutates
GA_FILL_MIN = 0.35
GA_FILL_MAX = 0.55
GA_SMOOTH_MIN = 2
GA_SMOOTH_MAX = 7
GA_LIMIT_MIN = 3                # birth / death limit range
GA_LIMIT_MAX = 5
GA_LEVEL_PRESSURE_PER_LEVEL = 0.01   # raises the fill floor as levels climb
GA_LEVEL_PRESSURE_MAX = 0.10

# ---------------------------------------------------------------------------
# Week 2 — adaptive enemy (values owned by Member 3)
# ---------------------------------------------------------------------------
ENEMY_REPATH_INTERVAL = 0.5     # seconds between A* recalculations
ENEMY_BASE_SPEED = 100          # level 1 speed (px/s)
ENEMY_SPEED_PER_LEVEL = 5       # extra speed each level above 1
ENEMY_SPEED_MAX = 160           # cap for the normal chase speed
ENEMY_BACKTRACK_MULT = 2.0      # speed multiplier while the player backtracks
ENEMY_BACKTRACK_SPEED_MAX = 280 # hard cap so it never overwhelms max player speed
ENEMY_PREDICTION_LEVEL = 3      # interception starts at this level
ENEMY_PREDICTION_TILES = 3      # how many tiles ahead of the player to aim

# ---------------------------------------------------------------------------
# Week 2 — movement penalty (values owned by Member 3)
# ---------------------------------------------------------------------------
PENALTY_BACKTRACK = 20          # added when the player re-enters a visited tile
PENALTY_HESITATION = 1          # added per frame once hesitating
PENALTY_MAX = 200               # cap so a tile is expensive, never "impassable"
HESITATION_SECONDS = 1.0        # standing still this long starts the penalty

# ---------------------------------------------------------------------------
# Week 2 — heatmap display (owned by Member 1)
# ---------------------------------------------------------------------------
HEAT_TINT_PER_VISIT = 20        # blue added per recorded visit (clamped at 255)

# ---------------------------------------------------------------------------
# Week 3 — menu / UI (values owned by Member 1, Tanvir Rahaman Pranto)
# ---------------------------------------------------------------------------
COLOR_MENU_BG = (14, 14, 18)
COLOR_BUTTON = (40, 40, 52)
COLOR_BUTTON_HOVER = (60, 60, 78)
COLOR_BUTTON_SELECTED = (50, 200, 255)
COLOR_TITLE = (50, 200, 255)
MENU_FONT_NAME = "Consolas"

# ---------------------------------------------------------------------------
# Week 3 — difficulty presets (values owned by Member 1, chosen in Settings;
# applied by Member 3's Enemy.difficulty_mult and Member 4's
# GeneticOptimizer.difficulty_mult — see menu.apply_difficulty)
# ---------------------------------------------------------------------------
DEFAULT_DIFFICULTY = "NORMAL"
DIFFICULTY_PRESETS = {
    "EASY":   {"enemy_speed_mult": 0.80, "fill_mult": 0.90},
    "NORMAL": {"enemy_speed_mult": 1.00, "fill_mult": 1.00},
    "HARD":   {"enemy_speed_mult": 1.25, "fill_mult": 1.15},
}
