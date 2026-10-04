import random
import heapq
from dataclasses import dataclass
import copy

@dataclass
class MapGenotype:
    """Represents the DNA of a map generation strategy."""
    fill_percent: float
    smooth_iterations: int
    wall_death_limit: int # Cellular Automata parameter
    wall_birth_limit: int # Cellular Automata parameter
    mutation_rate: float = 0.4

    def mutate(self):
        """Randomly adjust genes."""
        if random.random() < self.mutation_rate:
            self.fill_percent += random.uniform(-0.05, 0.05)
            self.fill_percent = max(0.35, min(0.55, self.fill_percent)) # Clamp
            
        if random.random() < self.mutation_rate:
            self.smooth_iterations += random.choice([-1, 1])
            self.smooth_iterations = max(2, min(7, self.smooth_iterations))

        if random.random() < self.mutation_rate:
             # Occasionally flip rules for chaos
            self.wall_birth_limit = 4 if random.random() > 0.5 else 5

@dataclass
class Candidate:
    genotype: MapGenotype
    fitness: float = 0.0

class GeneticOptimizer:
    def __init__(self):
        self.current_genotype = MapGenotype(
            fill_percent=0.40,
            smooth_iterations=4,
            wall_death_limit=4,
            wall_birth_limit=4
        )
        self.generation = 0

    def evolve(self, grid_class, width, height, level):
        """
        Evolves the next level's parameters.
        Generates candidates, tests them (simulates map gen + A*), and picks the best.
        """
        self.generation += 1
        population_size = 5 # Small population for real-time speed
        candidates = []

        # 1. Elitism: Keep current winner but mutate slightly
        parent = self.current_genotype
        
        for _ in range(population_size):
            # Create child
            child_genes = copy.deepcopy(parent)
            child_genes.mutate()
            
            # Force harder parameters based on level
            # Higher level -> Drift towards higher fill (more complex)
            level_pressure = min(0.10, level * 0.01)
            child_genes.fill_percent = min(0.55, child_genes.fill_percent + level_pressure)

            # Evaluate Fitness
            fitness = self.evaluate_fitness(child_genes, grid_class, width, height)
            candidates.append(Candidate(child_genes, fitness))

        # 2. Selection: Pick best
        candidates.sort(key=lambda c: c.fitness, reverse=True)
        best_candidate = candidates[0]
        
        print(f"[GA] Gen {self.generation} | Best Fitness: {best_candidate.fitness:.2f} | Genes: {best_candidate.genotype}")
        
        self.current_genotype = best_candidate.genotype
        return self.current_genotype

    def evaluate_fitness(self, genes, grid_class, width, height):
        """
        Simulate a map generation and measure difficulty.
        Fitness = Path Length (A*) 
        Penalty = 0 if no path exists.
        """
        # Create a temporary lightweight grid simulation
        # We can't use the full Pygame Grid because it loads images/rects.
        # We need a simulation method or just use the Grid class if it's light enough.
        # Grid class seems light (just logic + rects).
        
        try:
            # Generate Map with these genes
            # Note: We need to pass the genes to the map generator.
            # We'll use a helper on the Grid class or just assume we can patch it.
            # For now, let's assume we instantiate a grid and run the algo.
            
            # To avoid dependency cycles or heavy init, we assume Grid has a static-like method
            # or we instantiate it. grid.py imports pygame, which is fine.
            
            # We instantiate a minimal grid (no draw calls needed)
            sim_grid = grid_class(width, height, 1, headless=True) # 1 = dummy tile size
            sim_grid.apply_genes(genes)
            
            start_node = sim_grid.nodes[1][1]
            end_node = sim_grid.nodes[width-2][height-2]
            
            path = sim_grid.find_path(start_node, end_node)
            
            if not path:
                return 0.0 # Unsolvable = Trash
            
            # Fitness = Length
            return len(path)
            
        except Exception as e:
            print(f"[GA] Eval Error: {e}")
            return 0.0
