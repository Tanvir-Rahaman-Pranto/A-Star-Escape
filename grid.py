
import heapq
import random

import pygame

from settings import (
    COLOR_BG, COLOR_PORTAL, COLOR_WALL,
    MAP_FILL_PERCENT, MAP_SMOOTH_ITERATIONS,
    MAP_WALL_BIRTH_LIMIT, MAP_WALL_DEATH_LIMIT,
)


class Node:
    """A single grid cell. OWNER: Member 1 (fields marked below excepted)."""

    def __init__(self, x, y, tile_size):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
        self.is_wall = False
        self.is_portal = False
        self.movement_penalty = 0
        self.g_cost = float("inf")
        self.h_cost = 0
        self.f_cost = float("inf")
        self.parent = None
        self.visited_count = 0

    def draw(self, surface):
        """OWNER: Member 1."""
        if self.is_wall:
            color = COLOR_WALL
        elif self.is_portal:
            color = COLOR_PORTAL
        else:
            base_color = list(COLOR_BG)
            if self.movement_penalty > 0:
                base_color[0] = min(255, base_color[0] + self.movement_penalty * 2)
                base_color[1] = max(0, base_color[1] - self.movement_penalty)
            color = tuple(base_color)

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (30, 30, 35), self.rect, 1)  # Border

    def get_pos(self):
        """OWNER: Member 1."""
        return self.x, self.y

    def __lt__(self, other):
      return self.f_cost < other.f_cost

class Grid:
    def __init__(self, width, height, tile_size, headless=False):
        """OWNER: Member 1."""
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.headless = headless
        self.nodes = [[Node(x, y, tile_size) for y in range(height)] for x in range(width)]

        if not self.headless:
            self.generate_map()

            
    def generate_map(self, level=1):
        """Evolves parameters if level progression, then applies them."""
        print(f"--- Generating Level {level} (Evolutionary Strategy) ---")
        best_genes = self.optimizer.evolve(Grid, self.width, self.height, level)
        self.apply_parameters(
            fill_percent=best_genes.fill_percent,
            smooth_iterations=best_genes.smooth_iterations,
            wall_birth_limit=best_genes.wall_birth_limit,
            wall_death_limit=best_genes.wall_death_limit
        )

    # Step 2: Write apply_parameters end to end
    def apply_parameters(self, 
                         fill_percent=DEFAULT_FILL_PERCENT, 
                         smooth_iterations=DEFAULT_SMOOTH_ITERATIONS, 
                         wall_birth_limit=DEFAULT_WALL_BIRTH_LIMIT, 
                         wall_death_limit=DEFAULT_WALL_DEATH_LIMIT):
        # 1. Random fill with solid boundaries
        for x in range(self.width):
            for y in range(self.height):
                node = self.nodes[x][y]
                node.is_portal = False
                node.is_energy = False
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    node.is_wall = True
                else:
                    node.is_wall = (random.random() < fill_percent)
        
        # Step 1: Cellular automata smoothing
        for _ in range(smooth_iterations): 
            self.smooth_map(wall_birth_limit, wall_death_limit)
            
        # Step 3: Match Tanvir's spawn/portal corners
        self.clear_vital_areas()
        
        # Step 4: Wire ensure_connectivity to Jahidul's find_path
        self.ensure_connectivity()
        
        # Place collectible energy pickups
        self.place_energy_nodes()

    def apply_genes(self, genes):
        """Bridge for GeneticOptimizer genotype instances."""
        self.apply_parameters(
            fill_percent=genes.fill_percent,
            smooth_iterations=genes.smooth_iterations,
            wall_birth_limit=genes.wall_birth_limit,
            wall_death_limit=genes.wall_death_limit
        )

    # Step 1: Start smoothing and wall count (no find_path dependency)
    def smooth_map(self, birth_limit=DEFAULT_WALL_BIRTH_LIMIT, death_limit=DEFAULT_WALL_DEATH_LIMIT):
        new_map_walls = [[False for _ in range(self.height)] for _ in range(self.width)]
        
        for x in range(self.width):
            for y in range(self.height):
                neighbor_walls = self.get_wall_count(x, y)
                if self.nodes[x][y].is_wall:
                    new_map_walls[x][y] = (neighbor_walls >= death_limit)
                else:
                    new_map_walls[x][y] = (neighbor_walls > birth_limit)
                    
        for x in range(self.width):
            for y in range(self.height):
                self.nodes[x][y].is_wall = new_map_walls[x][y]

    def get_wall_count(self, grid_x, grid_y):
        wall_count = 0
        for neighbor_x in range(grid_x - 1, grid_x + 2):
            for neighbor_y in range(grid_y - 1, grid_y + 2):
                if 0 <= neighbor_x < self.width and 0 <= neighbor_y < self.height:
                    if neighbor_x != grid_x or neighbor_y != grid_y:
                        if self.nodes[neighbor_x][neighbor_y].is_wall:
                            wall_count += 1
                else:
                    wall_count += 1
        return wall_count

    # Step 3 & Step 6: Clear spawn (1, 1) and portal (width-2, height-2)
    def clear_vital_areas(self):
        # Clear around spawn (1, 1)
        for x in range(1, 4):
            for y in range(1, 4):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.nodes[x][y].is_wall = False
                
        # Clear around portal (width-2, height-2)
        for x in range(self.width - 4, self.width - 1):
            for y in range(self.height - 4, self.height - 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.nodes[x][y].is_wall = False
                
        portal_node = self.nodes[self.width - 2][self.height - 2]
        portal_node.is_wall = False
        portal_node.is_portal = True

    # Step 4: Wire ensure_connectivity to find_path
    def ensure_connectivity(self):
        start_node = self.nodes[1][1]
        end_node = self.nodes[self.width - 2][self.height - 2]
        
        path = self.find_path(start_node, end_node)
        if not path:
            # Drunkard's walk carver to guarantee connectivity
            current = start_node
            while current != end_node:
                current.is_wall = False
                cx, cy = current.x, current.y
                ex, ey = end_node.x, end_node.y
                
                dx = 1 if cx < ex else (-1 if cx > ex else 0)
                dy = 1 if cy < ey else (-1 if cy > ey else 0)
                
                if dx != 0 and dy != 0:
                    if random.random() < 0.5:
                        dy = 0
                    else:
                        dx = 0
                
                current = self.nodes[cx + dx][cy + dy]
            end_node.is_wall = False
            end_node.is_portal = True

    def place_energy_nodes(self):
        for x in range(self.width):
            for y in range(self.height):
                node = self.nodes[x][y]
                if not node.is_wall and not node.is_portal and (node.x, node.y) != (1, 1):
                    if random.random() < 0.03:
                        node.is_energy = True

    def adapt_to_history(self, heatmap):
        for x in range(self.width):
            for y in range(self.height):
                visits = heatmap[x][y]
                self.nodes[x][y].visited_count = visits
                self.nodes[x][y].movement_penalty = 0
                if visits > 0:
                    self.nodes[x][y].is_wall = False
                    
        self.clear_vital_areas()
        self.ensure_connectivity()
        self.nodes[self.width - 2][self.height - 2].is_portal = True

    def draw(self, surface):
        """OWNER: Member 1."""
        for x in range(self.width):
            for y in range(self.height):
                self.nodes[x][y].draw(surface)

    def get_neighbors(self, node):
        """OWNER: Member 1. 4-directional, walls excluded."""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = node.x + dx, node.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if not self.nodes[nx][ny].is_wall:
                    neighbors.append(self.nodes[nx][ny])
        return neighbors

    def reset_path_costs(self):
         for col in self.nodes:
            for node in col:
                node.g_cost = float("inf")
                node.h_cost = 0
                node.f_cost = float("inf")
                node.parent = None


    def find_path(self, start_node, end_node):
        self.reset_path_costs()
        start_node.g_cost = 0
        start_node.h_cost = self.heuristic(start_node, end_node)
        start_node.f_cost = start_node.g_cost + start_node.h_cost

        open_set = []
        heapq.heappush(open_set, start_node)
        closed_set = set()

        while open_set:
            current = heapq.heappop(open_set)

            if current == end_node:
                return self.retrace_path(start_node, end_node)

            closed_set.add(current)

            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue

                base_dist = self.get_distance(current, neighbor)
                # OWNER: Member 3 — penalty term makes over-used tiles expensive
                penalty = neighbor.movement_penalty
                new_cost = current.g_cost + base_dist + penalty

                if new_cost < neighbor.g_cost:
                    neighbor.g_cost = new_cost
                    neighbor.h_cost = self.heuristic(neighbor, end_node)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    neighbor.parent = current

                    if neighbor not in open_set:
                        heapq.heappush(open_set, neighbor)

        return []  # No path found

    def retrace_path(self, start_node, end_node):
        path = []
        current = end_node
        while current != start_node:
            path.append(current)
            current = current.parent
        path.reverse()
        return path
    def get_distance(self, node_a, node_b):
        dist_x = abs(node_a.x - node_b.x)
        dist_y = abs(node_a.y - node_b.y)
        if dist_x > dist_y:
            return 14 * dist_y + 10 * (dist_x - dist_y)
        return 14 * dist_x + 10 * (dist_y - dist_x)

    def heuristic(self, node_a, node_b):
        return (abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)) * 10
