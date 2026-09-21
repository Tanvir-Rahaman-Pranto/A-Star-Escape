"""
main.py  —  Week 1
OWNER: Member 5 — Mrittika Nandi (Integration & Testing)

Wires the four Week 1 deliverables together into a playable loop:
setup -> grid/maze -> player movement & collision -> A* enemy chase.

Run with:  python main.py
Controls:  WASD / arrow keys to move, SPACE to reset the loop.
"""

import sys

import pygame

from enemy import Enemy
from gamestate import GameState
from grid import Grid
from player import Player
from settings import (
    COLOR_BG, COLOR_TEXT, FPS, GRID_HEIGHT, GRID_WIDTH,
    SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, TITLE,
)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.font_large = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 24, bold=True)

        self.state = "RUNNING"  # RUNNING | GAMEOVER
        self.load()

    def load(self):
        self.gamestate = GameState(GRID_WIDTH, GRID_HEIGHT)
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT, TILE_SIZE)

        self.player = Player(self.grid.nodes[1][1], self.grid)
        self.enemy = Enemy(
            self.grid.nodes[GRID_WIDTH - 2][GRID_HEIGHT - 2], self.grid
        )
        self.state = "RUNNING"

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update(dt)
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset_game_loop(success=False)

    def reset_game_loop(self, success=False):
        """Week 1: always regenerate a fresh map.
        Week 2: on failure, call grid.adapt_to_history(heatmap) instead."""
        self.gamestate.reset_loop(self.player.visited_nodes, success=success)
        self.grid.generate_map()

        self.player = Player(self.grid.nodes[1][1], self.grid)
        self.enemy = Enemy(
            self.grid.nodes[GRID_WIDTH - 2][GRID_HEIGHT - 2], self.grid
        )
        self.state = "RUNNING"

    def update(self, dt):
        if self.state == "GAMEOVER":
            return

        self.player.update(dt)
        self.enemy.update(dt, self.player.node, self.player.is_backtracking)

        # Win: reached the portal
        if self.player.node.is_portal:
            self.reset_game_loop(success=True)
            return

        # Lose: caught by the enemy
        if self.player.pos.distance_to(self.enemy.pos) < self.player.radius + self.enemy.radius:
            self.state = "GAMEOVER"

    def draw(self):
        self.screen.fill(COLOR_BG)
        self.grid.draw(self.screen)

        # Enemy's current A* path, drawn so the algorithm is visible in the demo
        if self.enemy.path:
            points = [node.rect.center for node in self.enemy.path]
            points.insert(0, (self.enemy.pos.x, self.enemy.pos.y))
            if len(points) > 1:
                pygame.draw.lines(self.screen, (200, 50, 50), False, points, 2)

        self.player.draw(self.screen)
        self.enemy.draw(self.screen)

        if self.state == "RUNNING":
            level_text = self.font_small.render(
                f"LEVEL {self.gamestate.level}", True, COLOR_TEXT
            )
            self.screen.blit(level_text, (20, 20))

            if self.player.pos.distance_to(self.enemy.pos) < 300:
                text = self.font_small.render("MOVE!", True, (255, 50, 50))
                rect = text.get_rect(center=(self.player.pos.x, self.player.pos.y - 40))
                self.screen.blit(text, rect)

        elif self.state == "GAMEOVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            msg = self.font_large.render("FAILURE", True, (255, 50, 50))
            self.screen.blit(
                msg, msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            )

            sub = self.font_small.render(
                "Press SPACE to Reset Loop", True, (200, 200, 200)
            )
            self.screen.blit(
                sub, sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            )

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
