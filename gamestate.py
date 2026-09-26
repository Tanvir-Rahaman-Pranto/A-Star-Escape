"""
gamestate.py  —  Week 1
OWNER: Member 5 — Mrittika Nandi (Heatmap Analytics, Testing & Integration)

Week 1 scope: track the level and loop counters and allocate the empty heatmap
grid. update_heatmap() is written now but not yet used to reshape the map —
grid.adapt_to_history() is a Week 2 task.
"""


class GameState:
    def __init__(self, grid_width, grid_height):
        self.loop_count = 1
        self.level = 1
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.heatmap = [[0 for _ in range(grid_height)] for _ in range(grid_width)]

    def update_heatmap(self, visited_nodes):
        """Tally every tile the player stepped on during this loop."""
        for node in visited_nodes:
            if 0 <= node.x < self.grid_width and 0 <= node.y < self.grid_height:
                self.heatmap[node.x][node.y] += 1

    def reset_loop(self, visited_nodes, success=False):
        """Called on death or on reaching the portal. Returns the heatmap."""
        self.update_heatmap(visited_nodes)
        self.loop_count += 1
        if success:
            self.level += 1
        return self.heatmap
