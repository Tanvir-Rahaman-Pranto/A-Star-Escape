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

    def update(self, dt, player_node, player_vel, level=1, player_is_backtracking=False):
        # Adaptive Difficulty: Speed up if player is backtracking
        if player_is_backtracking:
            self.speed = 200  # Faster chase
            self.color = (255, 100, 100)  # Brighter red
        else:
            self.speed = 100
            self.color = COLOR_ENEMY

        # Repath periodically
        self.repath_timer += dt
        if self.repath_timer > 0.5:  # Recalculate every 0.5 seconds
            self.repath_timer = 0

            # AI Logic based on Level
            target_node = player_node

            if level >= 3:
                # Intercept Logic: Target where player is GOING
                # Simple prediction: Player Node + Vel Direction * Factor
                if player_vel.length() > 0:
                    pred_dist = 3  # Look 3 tiles ahead
                    norm_vel = player_vel.normalize()

                    # Convert grid coords
                    current_grid_x = player_node.x
                    current_grid_y = player_node.y

                    target_x = int(current_grid_x + norm_vel.x * pred_dist)
                    target_y = int(current_grid_y + norm_vel.y * pred_dist)

                    # Clamp
                    target_x = max(0, min(self.grid.width - 1, target_x))
                    target_y = max(0, min(self.grid.height - 1, target_y))

                    # Check if valid
                    potential_node = self.grid.nodes[target_x][target_y]
                    if not potential_node.is_wall:
                        target_node = potential_node

            self.path = self.grid.find_path(self.node, target_node)
            if self.path:
                self.target_node = self.path[0]

        # Follow path
        if self.target_node:
            target_pos = pygame.math.Vector2(self.target_node.rect.center)
            direction = target_pos - self.pos
            if direction.length() > 5:
                direction.normalize_ip()
                self.pos += direction * self.speed * dt
            else:
                # Reached node
                self.node = self.target_node
                if len(self.path) > 1:
                    self.path.pop(0)
                    self.target_node = self.path[0]
                else:
                    self.target_node = None  # Reached player (or end of path)

    def draw(self, surface):
        """OWNER: Member 2."""
        pygame.draw.circle(
            surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius
        )
