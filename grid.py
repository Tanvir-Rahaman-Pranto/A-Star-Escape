"""
grid.py  —  Week 3
Grid graph, Node state, A* pathfinding, cellular automata map generation,
and procedural brick wall rendering.
"""

import heapq
import random

import pygame

from genetic_map_gen import GeneticOptimizer
from settings import (
    BRICK_COLOR_DARK, BRICK_COLOR_LIGHT, BRICK_HEIGHT, BRICK_MORTAR,
    BRICK_WIDTH_RATIO, COLOR_BG, COLOR_PORTAL, HEAT_TINT_PER_VISIT, PENALTY_MAX,
)


class Node:
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

    def reset_runtime(self):
        self.movement_penalty = 0
        self.visited_count = 0

    def add_penalty(self, amount):
        self.movement_penalty = min(PENALTY_MAX, self.movement_penalty + amount)

    def draw(self, surface):
        if self.is_wall:
            self.draw_brick(surface)
            return
        elif self.is_portal:
            color = COLOR_PORTAL
        else:
            base_color = list(COLOR_BG)
            if self.movement_penalty > 0:
                base_color[0] = min(255, base_color[0] + self.movement_penalty * 2)
                base_color[1] = max(0, base_color[1] - self.movement_penalty)
            if self.visited_count > 0:
                base_color[2] = min(255, base_color[2] + self.visited_count * HEAT_TINT_PER_VISIT)
            color = tuple(base_color)

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (30, 30, 35), self.rect, 1)

    def draw_brick(self, surface):
        pygame.draw.rect(surface, BRICK_COLOR_DARK, self.rect)

        brick_w = max(4, int(self.tile_size * BRICK_WIDTH_RATIO))
        brick_h = BRICK_HEIGHT
        x0, y0 = self.rect.left, self.rect.top

        row = 0
        y = y0
        while y < self.rect.bottom:
            offset = (brick_w // 2) if row % 2 else 0
            x = x0 - offset
            while x < self.rect.right:
                face = pygame.Rect(x, y, brick_w - 1, min(brick_h, self.rect.bottom - y) - 1)
                face = face.clip(self.rect)
                if face.width > 0 and face.height > 0:
                    pygame.draw.rect(surface, BRICK_COLOR_LIGHT, face)
                x += brick_w
            y += brick_h
            row += 1

        pygame.draw.rect(surface, BRICK_MORTAR, self.rect, 1)

    def get_pos(self):
        return self.x, self.y

    def __lt__(self, other):
        if self.f_cost == other.f_cost:
            return self.h_cost < other.h_cost
        return self.f_cost < other.f_cost


class Grid:
    def __init__(self, width, height, tile_size, headless=False):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.headless = headless
        self.nodes = [[Node(x, y, tile_size) for y in range(height)] for x in range(width)]

        self.optimizer = None
        if not self.headless:
            self.optimizer = GeneticOptimizer()
            self.generate_map(level=1)

    def reset_runtime_state(self):
        for col in self.nodes:
            for node in col:
                node.reset_runtime()

    def generate_map(self, level=1):
        self.reset_runtime_state()
        genes = self.optimizer.evolve(Grid, self.width, self.height, level)
        self.apply_genes(genes)

    def apply_genes(self, genes):
        self.apply_parameters(
            fill_percent=genes.fill_percent,
            smooth_iterations=genes.smooth_iterations,
            wall_birth_limit=genes.wall_birth_limit,
            wall_death_limit=genes.wall_death_limit,
        )

    def apply_parameters(self, fill_percent, smooth_iterations,
                         wall_birth_limit, wall_death_limit):
        for x in range(self.width):
            for y in range(self.height):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.nodes[x][y].is_wall = True
                else:
                    self.nodes[x][y].is_wall = random.random() < fill_percent

        for _ in range(smooth_iterations):
            self.smooth_map(wall_birth_limit, wall_death_limit)

        self.clear_vital_areas()
        self.ensure_connectivity()

    def smooth_map(self, birth_limit=4, death_limit=4):
        new_map_walls = [[False for _ in range(self.height)] for _ in range(self.width)]

        for x in range(self.width):
            for y in range(self.height):
                neighbor_walls = self.get_wall_count(x, y)
                if self.nodes[x][y].is_wall:
                    new_map_walls[x][y] = neighbor_walls >= death_limit
                else:
                    new_map_walls[x][y] = neighbor_walls > birth_limit

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

    def clear_vital_areas(self):
        for x in range(1, 4):
            for y in range(1, 4):
                self.nodes[x][y].is_wall = False

        for x in range(self.width - 4, self.width - 1):
            for y in range(self.height - 4, self.height - 1):
                self.nodes[x][y].is_wall = False

        self.nodes[self.width - 2][self.height - 2].is_portal = True

    def ensure_connectivity(self):
        start_node = self.nodes[1][1]
        end_node = self.nodes[self.width - 2][self.height - 2]

        if self.find_path(start_node, end_node):
            return

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

            self.nodes[cx + dx][cy + dy].is_wall = False
            current = self.nodes[cx + dx][cy + dy]

    def adapt_to_history(self, heatmap):
        for x in range(self.width):
            for y in range(self.height):
                visits = heatmap[x][y]
                node = self.nodes[x][y]
                node.visited_count = visits
                node.movement_penalty = 0
                if visits > 0:
                    node.is_wall = False

        self.clear_vital_areas()
        self.ensure_connectivity()

    def draw(self, surface):
        for x in range(self.width):
            for y in range(self.height):
                self.nodes[x][y].draw(surface)

    def get_neighbors(self, node):
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
        open_hash = {start_node}
        heapq.heappush(open_set, start_node)
        closed_set = set()

        while open_set:
            current = heapq.heappop(open_set)
            open_hash.discard(current)

            if current == end_node:
                return self.retrace_path(start_node, end_node)

            closed_set.add(current)

            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue

                base_dist = self.get_distance(current, neighbor)
                penalty = neighbor.movement_penalty
                new_cost = current.g_cost + base_dist + penalty

                if new_cost < neighbor.g_cost:
                    neighbor.g_cost = new_cost
                    neighbor.h_cost = self.heuristic(neighbor, end_node)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    neighbor.parent = current

                    if neighbor not in open_hash:
                        heapq.heappush(open_set, neighbor)
                        open_hash.add(neighbor)

        return []

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