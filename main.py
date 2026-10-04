"""
main.py  —  Week 3
OWNER: Member 5 — Mrittika Nandi (Integration & Testing)

Week 3 adds the front-end flow around the Week 2 gameplay loop:

    MENU --start--> PLAYING --(Esc)--> MENU
    MENU --settings--> SETTINGS --back--> MENU
    MENU --tutorial--> TUTORIAL --back/Esc--> MENU
    MENU --exit--> window closes

PLAYING itself still runs Week 2's loop (win -> GA, lose -> adapt_to_history)
and its own RUNNING/GAMEOVER sub-state, unchanged. The Menu, SettingsMenu and
TutorialScreen classes are Member 1's (menu.py); this file only calls them and
reacts to the action strings they return.

Run with:  python main.py
Controls:  Menu/Settings: arrows or mouse + Enter; Playing: WASD/arrows to
           move, SPACE to reset the loop, Esc for the Menu.
"""

import sys

import pygame

from enemy import Enemy
from gamestate import GameState
from grid import Grid
from menu import AppState, Menu, SettingsMenu, TutorialScreen, apply_difficulty
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

        # Menu-side objects (Member 1). Built once so Settings remembers the
        # chosen difficulty across visits.
        self.menu = Menu()
        self.settings_menu = SettingsMenu()
        self.tutorial = None

        self.app_state = AppState.MENU
        self.state = "RUNNING"  # RUNNING | GAMEOVER — only meaningful in PLAYING
        self.gamestate = None
        self.grid = None
        self.player = None
        self.enemy = None

    # ------------------------------------------------------------------
    # Loading / resetting the PLAYING state
    # ------------------------------------------------------------------

    def load(self):
        """Start a brand-new run from Level 1 (called on "Start Game")."""
        self.gamestate = GameState(GRID_WIDTH, GRID_HEIGHT)
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT, TILE_SIZE)
        self.player = Player(self.grid.nodes[1][1], self.grid)
        self.enemy = Enemy(self.grid.nodes[GRID_WIDTH - 2][GRID_HEIGHT - 2], self.grid)
        apply_difficulty(self, self.settings_menu.difficulty)
        self.state = "RUNNING"
        self.app_state = AppState.PLAYING

    def reset_game_loop(self, success=False):
        """Win: the GA builds the next level's map. Loss: the current map adapts."""
        heatmap = self.gamestate.reset_loop(self.player.visited_nodes, success=success)
        if success:
            self.grid.generate_map(level=self.gamestate.level)
        else:
            self.grid.adapt_to_history(heatmap)

        self.player = Player(self.grid.nodes[1][1], self.grid)
        self.enemy = Enemy(self.grid.nodes[GRID_WIDTH - 2][GRID_HEIGHT - 2], self.grid)
        apply_difficulty(self, self.settings_menu.difficulty)
        self.state = "RUNNING"

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update(dt)
            self.draw()

    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
                return

            if self.app_state == AppState.MENU:
                action = self.menu.handle_event(event)
                if action == "start":
                    self.load()
                elif action == "settings":
                    self.app_state = AppState.SETTINGS
                elif action == "tutorial":
                    self.tutorial = TutorialScreen()
                    self.app_state = AppState.TUTORIAL
                elif action == "exit":
                    self.quit()
                    return

            elif self.app_state == AppState.SETTINGS:
                action = self.settings_menu.handle_event(event)
                if action == "back":
                    self.app_state = AppState.MENU

            elif self.app_state == AppState.TUTORIAL:
                action = self.tutorial.handle_event(event)
                if action == "back":
                    self.tutorial = None
                    self.app_state = AppState.MENU

            elif self.app_state == AppState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.reset_game_loop(success=False)
                    elif event.key == pygame.K_ESCAPE:
                        self.app_state = AppState.MENU

    def update(self, dt):
        if self.app_state == AppState.TUTORIAL:
            self.tutorial.update(dt)
            return

        if self.app_state != AppState.PLAYING or self.state == "GAMEOVER":
            return

        self.player.update(dt)
        self.enemy.update(
            dt, self.player.node, self.player.vel,
            self.gamestate.level, self.player.is_backtracking,
        )

        # Win: reached the portal
        if self.player.node.is_portal:
            self.reset_game_loop(success=True)
            return

        # Lose: caught by the enemy
        if self.player.pos.distance_to(self.enemy.pos) < self.player.radius + self.enemy.radius:
            self.state = "GAMEOVER"

    def draw(self):
        if self.app_state == AppState.MENU:
            self.menu.draw(self.screen)
        elif self.app_state == AppState.SETTINGS:
            self.settings_menu.draw(self.screen)
        elif self.app_state == AppState.TUTORIAL:
            self.tutorial.draw(self.screen)
        else:
            self.draw_playing()

        pygame.display.flip()

    def draw_playing(self):
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
                f"LEVEL {self.gamestate.level}   LOOP {self.gamestate.loops_this_level}"
                f"   [{self.settings_menu.difficulty}]",
                True, COLOR_TEXT,
            )
            self.screen.blit(level_text, (20, 20))

            # HUD: what the GA and the enemy are doing right now (demo material)
            opt = self.grid.optimizer
            genes = opt.current_genotype
            ai_text = self.font_small.render(
                f"GA gen {opt.generation}  fitness {opt.last_fitness:.0f}  "
                f"fill {genes.fill_percent:.2f}  |  enemy speed {self.enemy.speed:.0f}",
                True, (150, 150, 170),
            )
            self.screen.blit(ai_text, (20, SCREEN_HEIGHT - 36))

            esc_hint = self.font_small.render("Esc: Menu", True, (150, 150, 170))
            self.screen.blit(esc_hint, esc_hint.get_rect(topright=(SCREEN_WIDTH - 20, 20)))

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
                "Press SPACE to Reset Loop  —  Esc for Menu", True, (200, 200, 200)
            )
            self.screen.blit(
                sub, sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            )


if __name__ == "__main__":
    Game().run()
