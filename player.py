import pygame
import random
from settings import *

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
        
        # Cost tracking
        self.visited_nodes = set()
        self.visited_nodes.add(self.node)
        self.hesitation_timer = 0
        self.last_node = start_node
        self.is_backtracking = False
        self.boost_timer = 0

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
        
        # Physics equations
        self.acc += self.vel * self.friction
        self.vel += self.acc * dt
        
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
            
        self.pos += self.vel * dt + 0.5 * self.acc * dt ** 2
        
        self.rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
        self.collide_with_walls()

        # Update current node
        grid_x = int(self.pos.x // TILE_SIZE)
        grid_y = int(self.pos.y // TILE_SIZE)
        if 0 <= grid_x < self.grid.width and 0 <= grid_y < self.grid.height:
            current_node = self.grid.nodes[grid_x][grid_y]
            
            # Change Node Logic
            if current_node != self.node:
                self.last_node = self.node
                self.node = current_node
                
                # Energy Node Logic
                if self.node.is_energy:
                    self.node.is_energy = False
                    # Strategic Instability: Reset backtracking history
                    self.visited_nodes.clear()
                    # Also boost speed temporarily?
                    self.max_speed = 600 
                    self.boost_timer = 2.0
                
                # Backtracking Logic
                if self.node in self.visited_nodes:
                    # Player is backtracking! Increase cost.
                    self.node.movement_penalty += 20
                    self.is_backtracking = True
                else:
                    self.visited_nodes.add(self.node)
                    self.is_backtracking = False
                    # "Preferred routes lower estimated cost" -> This is for heuristic learning over loops.
                    # For now just track visited.
            
            # Hesitation Logic (Standing still)
            if self.vel.length() < 50:
                self.hesitation_timer += dt
                if self.hesitation_timer > 1.0: # 1 second of standing still
                    self.node.movement_penalty += 1
            else:
                self.hesitation_timer = 0
                
        # Boost Timer Logic
        if self.boost_timer > 0:
            self.boost_timer -= dt
            # Increase Acceleration significantly during boost
            self.speed = 4000 
            if self.boost_timer <= 0:
                self.max_speed = 300 # Reset to normal
                self.speed = 1500 # Reset acceleration
        else:
             self.speed = 1500

    def collide_with_walls(self):
        # A simple way to handle collisions is to check future position or separate axes.
        # Since I already moved, I need to resolve overlap.
        # Checking neighbors of current grid cell.
        
        # Grid coordinates of player center
        cx = int(self.pos.x // TILE_SIZE)
        cy = int(self.pos.y // TILE_SIZE)
        
        # Check surrounding tiles
        for x in range(cx - 1, cx + 2):
            for y in range(cy - 1, cy + 2):
                if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                    node = self.grid.nodes[x][y]
                    if node.is_wall:
                        if self.rect.colliderect(node.rect):
                            # Resolve collision
                            self.resolve_collision(node.rect)

    def resolve_collision(self, wall_rect):
        # Determine direction of collision
        # Only simple AABB resolution
        if self.rect.colliderect(wall_rect):
            # Calculate overlap
            dx = (self.rect.centerx - wall_rect.centerx) / (wall_rect.width / 2)
            dy = (self.rect.centery - wall_rect.centery) / (wall_rect.height / 2)
            
            if abs(dx) > abs(dy):
                # X-axis collision
                if dx > 0: # Player is right of wall
                    self.pos.x = wall_rect.right + self.radius
                else: # Player is left of wall
                    self.pos.x = wall_rect.left - self.radius
                self.vel.x = 0
            else:
                # Y-axis collision
                if dy > 0: # Player is below wall
                    self.pos.y = wall_rect.bottom + self.radius
                else: # Player is above wall
                    self.pos.y = wall_rect.top - self.radius
                self.vel.y = 0
            
            # Update rect
            self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface):
        draw_pos = (int(self.pos.x), int(self.pos.y))
        
        # Shake effect if boosting
        if self.boost_timer > 0:
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
            draw_pos = (int(self.pos.x + offset_x), int(self.pos.y + offset_y))
            
        pygame.draw.circle(surface, self.color, draw_pos, self.radius)
