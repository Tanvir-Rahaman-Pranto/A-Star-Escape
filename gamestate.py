"""
gamestate.py  —  Week 2
OWNER: Member 5 — Mrittika Nandi (Heatmap Analytics, Testing & Integration)

Week 2 scope: the heatmap is now USED. It is tallied every loop, handed to
Grid.adapt_to_history() after a failed loop (Member 3), and wiped when the
player advances to a new level (a new map makes old heat meaningless).

Heatmap format (contract with Member 3): heatmap[x][y] = int visit count.
"""


class GameState:
    def __init__(self, grid_width, grid_height):
        self.loop_count = 1          # total loops played this session
        self.loops_this_level = 1    # loops played on the current level
        self.level = 1
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.heatmap = self._empty_heatmap()

    def _empty_heatmap(self):
        return [[0 for _ in range(self.grid_height)] for _ in range(self.grid_width)]

    def update_heatmap(self, visited_nodes):
        """Tally every tile the player stepped on during this loop."""
        for node in visited_nodes:
            if 0 <= node.x < self.grid_width and 0 <= node.y < self.grid_height:
                self.heatmap[node.x][node.y] += 1

    def reset_level(self):
        """New level, new map: clear the heatmap and the per-level loop counter."""
        self.heatmap = self._empty_heatmap()
        self.loops_this_level = 1

    def reset_loop(self, visited_nodes, success=False):
        """Called on death or on reaching the portal. Returns the heatmap.

        On failure the returned heatmap (including this loop) feeds
        Grid.adapt_to_history(). On success the level advances and the heatmap
        starts fresh.
        """
        self.update_heatmap(visited_nodes)
        self.loop_count += 1
        if success:
            self.level += 1
            self.reset_level()
        else:
            self.loops_this_level += 1
        return self.heatmap

    def get_hot_tiles(self, min_visits=2):
        """Tiles visited at least `min_visits` times, hottest first: [(x, y, visits)]."""
        hot = [
            (x, y, self.heatmap[x][y])
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if self.heatmap[x][y] >= min_visits
        ]
        hot.sort(key=lambda t: t[2], reverse=True)
        return hot

    def max_heat(self):
        return max(max(col) for col in self.heatmap)
