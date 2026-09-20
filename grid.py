
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

    def generate_map(self):
        """Written by Member 4 — Anindaw Nahian Omi. Do not edit here."""
        raise NotImplementedError("owned by Member 4 — Anindaw Nahian Omi")

    def apply_parameters(self, fill_percent, smooth_iterations,
                         wall_birth_limit, wall_death_limit):
        """Written by Member 4 — Anindaw Nahian Omi. Do not edit here."""
        raise NotImplementedError("owned by Member 4 — Anindaw Nahian Omi")

    def smooth_map(self, birth_limit=4, death_limit=4):
        """Written by Member 4 — Anindaw Nahian Omi. Do not edit here."""
        raise NotImplementedError("owned by Member 4 — Anindaw Nahian Omi")

    def get_wall_count(self, grid_x, grid_y):
        """Written by Member 4 — Anindaw Nahian Omi. Do not edit here."""
        raise NotImplementedError("owned by Member 4 — Anindaw Nahian Omi")

    def clear_vital_areas(self):
        """Written by Member 4 — Anindaw Nahian Omi. Do not edit here."""
        raise NotImplementedError("owned by Member 4 — Anindaw Nahian Omi")

    def ensure_connectivity(self):
        """Written by Member 4 — Anindaw Nahian Omi. Do not edit here."""
        raise NotImplementedError("owned by Member 4 — Anindaw Nahian Omi")

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
