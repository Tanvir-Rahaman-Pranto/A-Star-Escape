
import pygame

from settings import COLOR_PLAYER, TILE_SIZE


class Player:
    def __init__(self, start_node, grid):
        self.node = start_node
        self.grid = grid
        self.color = COLOR_PLAYER
        self.radius = TILE_SIZE // 3
        self.pos = pygame.math.Vector2(start_node.rect.center)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.speed = 1500
        self.friction = -10
        self.max_speed = 300
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def get_input(self):
        keys = pygame.key.get_pressed()
        self.acc = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.acc.x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.acc.x = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.acc.y = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.acc.y = self.speed

    def update(self, dt):
        self.get_input()

        # --- Physics ---
        self.acc += self.vel * self.friction
        self.vel += self.acc * dt

        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)

        self.pos += self.vel * dt + 0.5 * self.acc * dt ** 2

        self.rect = pygame.Rect(
            self.pos.x - self.radius, self.pos.y - self.radius,
            self.radius * 2, self.radius * 2,
        )
        self.collide_with_walls()

        # --- Current node tracking ---
        grid_x = int(self.pos.x // TILE_SIZE)
        grid_y = int(self.pos.y // TILE_SIZE)
        if 0 <= grid_x < self.grid.width and 0 <= grid_y < self.grid.height:
            self.node = self.grid.nodes[grid_x][grid_y]

    def collide_with_walls(self):
        """Checks the 8 tiles around the player's current cell."""
        cx = int(self.pos.x // TILE_SIZE)
        cy = int(self.pos.y // TILE_SIZE)

        for x in range(cx - 1, cx + 2):
            for y in range(cy - 1, cy + 2):
                if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                    node = self.grid.nodes[x][y]
                    if node.is_wall and self.rect.colliderect(node.rect):
                        self.resolve_collision(node.rect)

    def resolve_collision(self, wall_rect):
        """Axis-aligned overlap resolution — resolve the larger-overlap axis."""
        if not self.rect.colliderect(wall_rect):
            return

        dx = (self.rect.centerx - wall_rect.centerx) / (wall_rect.width / 2)
        dy = (self.rect.centery - wall_rect.centery) / (wall_rect.height / 2)

        if abs(dx) > abs(dy):
            if dx > 0:
                self.pos.x = wall_rect.right + self.radius
            else:
                self.pos.x = wall_rect.left - self.radius
            self.vel.x = 0
        else:
            if dy > 0:
                self.pos.y = wall_rect.bottom + self.radius
            else:
                self.pos.y = wall_rect.top - self.radius
            self.vel.y = 0

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface):
        pygame.draw.circle(
            surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius
        )