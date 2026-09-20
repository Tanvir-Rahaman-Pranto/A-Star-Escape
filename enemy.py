import pygame

from settings import COLOR_ENEMY, TILE_SIZE


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

    def update(self, dt, player_node, player_is_backtracking=False):
        # --- Adaptive speed hook. OWNER: Member 3 ---
        if player_is_backtracking:
            self.speed = 200
            self.color = (255, 100, 100)
        else:
            self.speed = self.base_speed
            self.color = COLOR_ENEMY

        # --- Repath every 0.5s. OWNER: Member 2 ---
        self.repath_timer += dt
        if self.repath_timer > 0.5:
            self.repath_timer = 0
            self.path = self.grid.find_path(self.node, player_node)
            if self.path:
                self.target_node = self.path[0]

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
