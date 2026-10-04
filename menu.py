"""
menu.py  —  Week 3
OWNER: Member 1 — Tanvir Rahaman Pranto (Game & Maze Development)

New this week: the front-end flow around the game loop.

  AppState       — the five screens main.py (Member 5) switches between
  Menu           — Start Game / Settings / Tutorial / Exit
  SettingsMenu   — difficulty picker (EASY / NORMAL / HARD), remembers the
                   player's choice for the rest of the session
  TutorialScreen — a small, enemy-free playable level that teaches movement,
                   walls, the portal, and the backtracking penalty
  apply_difficulty(game, difficulty) — pushes the chosen difficulty's
                   multipliers into Member 3's Enemy and Member 4's
                   GeneticOptimizer (both already expose a `difficulty_mult`
                   field for exactly this; menu.py only ever writes that one
                   field, it never edits enemy.py or grid.py)

main.py only needs to: construct Menu()/SettingsMenu() once, call their
handle_event()/update()/draw() while in the matching AppState, and act on the
action strings they return ("start", "settings", "tutorial", "back", "exit").
"""

import pygame

from grid import Grid
from player import Player
from settings import (
    COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_SELECTED, COLOR_MENU_BG,
    COLOR_TEXT, COLOR_TITLE, DEFAULT_DIFFICULTY, DIFFICULTY_PRESETS,
    GRID_HEIGHT, GRID_WIDTH, MENU_FONT_NAME, SCREEN_HEIGHT, SCREEN_WIDTH,
    TILE_SIZE, TITLE,
)


class AppState:
    """OWNER: Member 1. The screens main.py's Game can be in."""
    MENU = "MENU"
    SETTINGS = "SETTINGS"
    TUTORIAL = "TUTORIAL"
    PLAYING = "PLAYING"
    GAMEOVER = "GAMEOVER"


def apply_difficulty(game, difficulty):
    """OWNER: Member 1. Pushes DIFFICULTY_PRESETS[difficulty] onto the live
    Enemy and GeneticOptimizer. Call this once after Game.load()/reset and
    again whenever the player confirms a new difficulty in Settings."""
    preset = DIFFICULTY_PRESETS.get(difficulty, DIFFICULTY_PRESETS[DEFAULT_DIFFICULTY])
    if getattr(game, "enemy", None) is not None:
        game.enemy.difficulty_mult = preset["enemy_speed_mult"]
    if getattr(game, "grid", None) is not None and game.grid.optimizer is not None:
        game.grid.optimizer.difficulty_mult = preset["fill_mult"]


class _Button:
    """OWNER: Member 1. A single clickable/selectable menu row."""

    def __init__(self, label, center_y, action):
        self.label = label
        self.action = action
        self.rect = pygame.Rect(0, 0, 360, 56)
        self.rect.center = (SCREEN_WIDTH // 2, center_y)

    def draw(self, surface, font, is_selected, is_hovered):
        if is_selected or is_hovered:
            color = COLOR_BUTTON_SELECTED if is_selected else COLOR_BUTTON_HOVER
        else:
            color = COLOR_BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_TEXT, self.rect, 2, border_radius=8)
        text = font.render(self.label, True, COLOR_TEXT)
        surface.blit(text, text.get_rect(center=self.rect.center))


class Menu:
    """OWNER: Member 1. The title screen: Start Game, Settings, Tutorial, Exit."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("Arial", 56, bold=True)
        self.font_item = pygame.font.SysFont(MENU_FONT_NAME, 28, bold=True)
        self.font_hint = pygame.font.SysFont(MENU_FONT_NAME, 18)
        self.buttons = [
            _Button("Start Game", 300, "start"),
            _Button("Settings", 370, "settings"),
            _Button("Tutorial", 440, "tutorial"),
            _Button("Exit", 510, "exit"),
        ]
        self.selected = 0

    def handle_event(self, event):
        """Returns an action string ("start"/"settings"/"tutorial"/"exit") or None."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.buttons)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.buttons[self.selected].action
            elif event.key == pygame.K_ESCAPE:
                return "exit"
        elif event.type == pygame.MOUSEMOTION:
            for i, button in enumerate(self.buttons):
                if button.rect.collidepoint(event.pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    return button.action
        return None

    def draw(self, surface):
        surface.fill(COLOR_MENU_BG)
        title = self.font_title.render(TITLE, True, COLOR_TITLE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 170)))

        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(self.buttons):
            button.draw(
                surface, self.font_item,
                is_selected=(i == self.selected),
                is_hovered=button.rect.collidepoint(mouse_pos),
            )

        hint = self.font_hint.render(
            "Arrow keys / mouse to choose, Enter to select, Esc to exit", True, COLOR_TEXT
        )
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))


class SettingsMenu:
    """OWNER: Member 1. Difficulty picker. Kept alive for the whole session so
    the chosen difficulty survives returning to it."""

    LEVELS = ["EASY", "NORMAL", "HARD"]

    def __init__(self, difficulty=DEFAULT_DIFFICULTY):
        self.font_title = pygame.font.SysFont("Arial", 44, bold=True)
        self.font_item = pygame.font.SysFont(MENU_FONT_NAME, 26, bold=True)
        self.font_hint = pygame.font.SysFont(MENU_FONT_NAME, 18)
        self.difficulty = difficulty if difficulty in self.LEVELS else DEFAULT_DIFFICULTY
        self.buttons = [
            _Button(level.title(), 300 + i * 70, level) for i, level in enumerate(self.LEVELS)
        ]
        self.back_button = _Button("Back", 300 + len(self.LEVELS) * 70 + 20, "back")
        self.cursor = self.LEVELS.index(self.difficulty)  # which row the keyboard is on

    def _rows(self):
        return self.buttons + [self.back_button]

    def handle_event(self, event):
        """Returns "back" to leave Settings, or None while still choosing."""
        rows = self._rows()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.cursor = (self.cursor + 1) % len(rows)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.cursor = (self.cursor - 1) % len(rows)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._activate(rows[self.cursor])
            elif event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEMOTION:
            for i, row in enumerate(rows):
                if row.rect.collidepoint(event.pos):
                    self.cursor = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for row in rows:
                if row.rect.collidepoint(event.pos):
                    return self._activate(row)
        return None

    def _activate(self, row):
        if row is self.back_button:
            return "back"
        self.difficulty = row.action
        return None

    def draw(self, surface):
        surface.fill(COLOR_MENU_BG)
        title = self.font_title.render("Settings", True, COLOR_TITLE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))

        mouse_pos = pygame.mouse.get_pos()
        rows = self._rows()
        for i, row in enumerate(rows):
            is_chosen = (row is not self.back_button and row.action == self.difficulty)
            is_cursor = (i == self.cursor)
            row.draw(
                surface, self.font_item,
                is_selected=is_chosen or is_cursor,
                is_hovered=row.rect.collidepoint(mouse_pos),
            )

        hint = self.font_hint.render(
            f"Difficulty: {self.difficulty}  —  affects enemy speed and maze density",
            True, COLOR_TEXT,
        )
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))


class TutorialScreen:
    """OWNER: Member 1. A small, non-lethal playable level: move with the real
    Player and Grid classes (owned by Members 1/2/4), no Enemy, with staged
    captions. Reaching the portal, or Esc, returns to the Menu."""

    STEPS = [
        "WASD / Arrow keys move you (the cyan circle).",
        "Brick tiles are walls - you can't pass through them.",
        "Revisiting a tile you've already walked lights it up: it now costs "
        "the enemy's A* more to path through, so backtracking is a real tool.",
        "Reach the green portal to finish the tutorial.",
    ]
    CAPTION_MAX_WIDTH = SCREEN_WIDTH - 120  # leaves a margin on both sides

    def __init__(self):
        self.font_caption = pygame.font.SysFont(MENU_FONT_NAME, 22, bold=True)
        self.font_hint = pygame.font.SysFont(MENU_FONT_NAME, 20, bold=True)
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT, TILE_SIZE)
        self.player = Player(self.grid.nodes[1][1], self.grid)
        self.step = 0
        self.completed = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"
        return None

    def update(self, dt):
        self.player.update(dt)

        if self.step == 0 and self.player.last_node is not self.player.node:
            self.step = 1
        if self.step <= 1 and self.player.is_backtracking:
            self.step = 2
        if self.player.node.is_portal:
            self.completed = True
            self.step = 3

    def _wrap(self, text, font, max_width):
        """OWNER: Member 1. Break `text` into lines that each fit max_width —
        pygame's font.render() has no built-in word wrap, so a long caption
        would otherwise run straight off the sides of the screen."""
        words = text.split(" ")
        lines, current = [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw(self, surface):
        surface.fill((20, 20, 25))
        self.grid.draw(surface)
        self.player.draw(surface)

        # --- Always-visible control bar across the top ---
        bar = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(surface, COLOR_MENU_BG, bar)
        pygame.draw.line(surface, (70, 70, 85), (0, 100), (SCREEN_WIDTH, 100), 2)

        caption_text = self.STEPS[min(self.step, len(self.STEPS) - 1)]
        lines = self._wrap(caption_text, self.font_caption, self.CAPTION_MAX_WIDTH)
        line_h = self.font_caption.get_height() + 4
        start_y = 16
        for i, line in enumerate(lines):
            rendered = self.font_caption.render(line, True, COLOR_TEXT)
            surface.blit(rendered, rendered.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * line_h)))

        hint_text = (
            "Tutorial complete! Press ESC to return to the Menu."
            if self.completed else
            f"Step {self.step + 1}/{len(self.STEPS)}   —   press ESC any time to return to the Menu"
        )
        hint_color = (50, 255, 100) if self.completed else (150, 150, 170)
        hint = self.font_hint.render(hint_text, True, hint_color)
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 100 - 20)))
