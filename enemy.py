import pygame
from settings import (
    COLOR_ENEMY, ENEMY_BACKTRACK_MULT, ENEMY_BACKTRACK_SPEED_MAX,
    ENEMY_BASE_SPEED, ENEMY_PREDICTION_LEVEL, ENEMY_PREDICTION_TILES,
    ENEMY_REPATH_INTERVAL, ENEMY_SPEED_MAX, ENEMY_SPEED_PER_LEVEL, TILE_SIZE,
)


class Enemy:
    def __init__(self, start_node, grid):
        """OWNER: Member 2."""
        self.node = start_node
        self.grid = grid
        self.color = COLOR_ENEMY
        self.radius = TILE_SIZE // 3
        self.pos = pygame.math.Vector2(start_node.rect.center)
        self.path = []
        self.target_node = None
        self.base_speed = 100
        self.speed = self.base_speed
        self.repath_timer = 0
        self.difficulty_mult = 1.0

    def apply_adaptive_speed(self, level, player_is_backtracking):
        """OWNER: Member 3. Base speed climbs with level and difficulty; backtracking
        makes it sprint."""
        self.base_speed = min(
            ENEMY_SPEED_MAX,
            (ENEMY_BASE_SPEED + (level - 1) * ENEMY_SPEED_PER_LEVEL) * self.difficulty_mult,
        )
        if player_is_backtracking:
            self.speed = min(self.base_speed * ENEMY_BACKTRACK_MULT, ENEMY_BACKTRACK_SPEED_MAX)
            self.color = (255, 100, 100)
        else:
            self.speed = self.base_speed
            self.color = COLOR_ENEMY

    def choose_target(self, player_node, player_vel, level):
        """OWNER: Member 3. Aim at the player's tile, or ahead of them from the
        prediction level onward. Always returns a walkable node."""
        if level < ENEMY_PREDICTION_LEVEL or player_vel.length() < 1:
            return player_node

        direction = player_vel.normalize()
        # Look ENEMY_PREDICTION_TILES ahead; if that tile is a wall, back off one
        # tile at a time until a walkable one is found.
        for tiles_ahead in range(ENEMY_PREDICTION_TILES, 0, -1):
            target_x = int(round(player_node.x + direction.x * tiles_ahead))
            target_y = int(round(player_node.y + direction.y * tiles_ahead))
            target_x = max(0, min(self.grid.width - 1, target_x))
            target_y = max(0, min(self.grid.height - 1, target_y))
            candidate = self.grid.nodes[target_x][target_y]
            if not candidate.is_wall:
                return candidate
        return player_node

    def update(self, dt, player_node, player_vel, level=1, player_is_backtracking=False):
        # --- Adaptive speed hook. OWNER: Member 3 ---
        self.apply_adaptive_speed(level, player_is_backtracking)

        # --- Repath. OWNER: Member 2 ---
        self.repath_timer += dt
        if self.repath_timer > ENEMY_REPATH_INTERVAL:
            self.repath_timer = 0
            target = self.choose_target(player_node, player_vel, level)
            path = self.grid.find_path(self.node, target)
            if not path and target is not player_node:
                path = self.grid.find_path(self.node, player_node)
            self.path = path
            self.target_node = path[0] if path else None

        # --- Follow the path. OWNER: Member 2 ---
        if not self.target_node:
            return

        target_pos = pygame.math.Vector2(self.target_node.rect.center)
        direction = target_pos - self.pos

        if direction.length() > 5:
            direction.normalize_ip()
            self.pos += direction * self.speed * dt
        else:
            self.node = self.target_node
            if len(self.path) > 1:
                self.path.pop(0)
                self.target_node = self.path[0]
            else:
                self.target_node = None

    def draw(self, surface):
        """OWNER: Member 2."""
        pygame.draw.circle(
            surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius
        )
