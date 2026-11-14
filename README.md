# A* Escape: The Living Network

An adaptive maze-escape game built with **Python and Pygame**. The maze evolves, the enemy learns, and every level is different.

> Add a demo GIF here: `![Gameplay](assets/demo.gif)`

## How it works

- **A\* pathfinding** – the enemy continuously re-plans the shortest route to you.
- **Predictive enemy AI** – from higher levels onward, the enemy aims at where you are heading, not where you are. Backtracking triggers a speed boost.
- **Genetic algorithm map generation** – maze parameters (fill percent, smoothing iterations, birth/death limits) are evolved with crossover and mutation, using cellular automata to build each map.
- **Heatmap-driven adaptation** – tiles you visit often are tracked and the environment adapts to your movement history.
- **Level scaling** – enemy speed and map difficulty increase as you progress.

## Run it

```bash
pip install pygame
python main.py
```

Move with **WASD** or the **arrow keys**.

## Project structure

| File | Purpose |
|---|---|
| `main.py` | Game loop and state handling |
| `menu.py` | Menu screens |
| `grid.py` | Grid, tiles, A* search, heatmap adaptation |
| `player.py` | Player movement and collision |
| `enemy.py` | Enemy pathing, prediction, adaptive speed |
| `genetic_map_gen.py` | Genetic algorithm for procedural maps |
| `gamestate.py` | Game state tracking |
| `settings.py` | Tunable constants |

## Team

Built as an AI Lab group project at United International University (UIU).
