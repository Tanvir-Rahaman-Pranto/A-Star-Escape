"""
genetic_map_gen.py  —  Week 3
Genetic algorithm for evolving cellular-automata map generation genotypes.
"""

import copy
import random
from dataclasses import dataclass

from settings import (
    GA_FILL_MAX, GA_FILL_MIN, GA_FITNESS_SAMPLES, GA_LEVEL_PRESSURE_MAX,
    GA_LEVEL_PRESSURE_PER_LEVEL, GA_LIMIT_MAX, GA_LIMIT_MIN,
    GA_MUTATION_RATE, GA_POPULATION_SIZE, GA_SMOOTH_MAX, GA_SMOOTH_MIN,
    GA_SURVIVORS, MAP_FILL_PERCENT, MAP_SMOOTH_ITERATIONS,
    MAP_WALL_BIRTH_LIMIT, MAP_WALL_DEATH_LIMIT,
)


@dataclass
class MapGenotype:
    fill_percent: float
    smooth_iterations: int
    wall_birth_limit: int
    wall_death_limit: int

    def mutate(self, rate=GA_MUTATION_RATE, fill_floor=GA_FILL_MIN):
        if random.random() < rate:
            self.fill_percent += random.uniform(-0.05, 0.05)
        if random.random() < rate:
            self.smooth_iterations += random.choice([-1, 1])
        if random.random() < rate:
            self.wall_birth_limit += random.choice([-1, 1])
        if random.random() < rate:
            self.wall_death_limit += random.choice([-1, 1])
        self.clamp(fill_floor)

    def clamp(self, fill_floor=GA_FILL_MIN):
        self.fill_percent = max(fill_floor, min(GA_FILL_MAX, self.fill_percent))
        self.smooth_iterations = max(GA_SMOOTH_MIN, min(GA_SMOOTH_MAX, self.smooth_iterations))
        self.wall_birth_limit = max(GA_LIMIT_MIN, min(GA_LIMIT_MAX, self.wall_birth_limit))
        self.wall_death_limit = max(GA_LIMIT_MIN, min(GA_LIMIT_MAX, self.wall_death_limit))


def crossover(parent_a, parent_b):
    return MapGenotype(
        fill_percent=random.choice([parent_a.fill_percent, parent_b.fill_percent]),
        smooth_iterations=random.choice([parent_a.smooth_iterations, parent_b.smooth_iterations]),
        wall_birth_limit=random.choice([parent_a.wall_birth_limit, parent_b.wall_birth_limit]),
        wall_death_limit=random.choice([parent_a.wall_death_limit, parent_b.wall_death_limit]),
    )


@dataclass
class Candidate:
    genotype: MapGenotype
    fitness: float = 0.0


class GeneticOptimizer:
    def __init__(self):
        self.current_genotype = MapGenotype(
            fill_percent=MAP_FILL_PERCENT,
            smooth_iterations=MAP_SMOOTH_ITERATIONS,
            wall_birth_limit=MAP_WALL_BIRTH_LIMIT,
            wall_death_limit=MAP_WALL_DEATH_LIMIT,
        )
        self.survivors = []
        self.generation = 0
        self.last_fitness = 0.0
        self.difficulty_mult = 1.0

    def fill_floor_for(self, level):
        pressure = min(GA_LEVEL_PRESSURE_MAX, level * GA_LEVEL_PRESSURE_PER_LEVEL)
        floor = (GA_FILL_MIN + pressure) * self.difficulty_mult
        return max(GA_FILL_MIN, min(GA_FILL_MAX, floor))

    def evolve(self, grid_class, width, height, level):
        self.generation += 1
        floor = self.fill_floor_for(level)

        parents = self.survivors or [self.current_genotype]

        population = [copy.deepcopy(g) for g in parents]
        for genotype in population:
            genotype.clamp(floor)

        while len(population) < GA_POPULATION_SIZE:
            parent_a = random.choice(parents)
            parent_b = random.choice(parents)
            child = crossover(parent_a, parent_b)
            child.mutate(fill_floor=floor)
            population.append(child)

        candidates = [
            Candidate(g, self.evaluate_fitness(g, grid_class, width, height))
            for g in population
        ]
        candidates.sort(key=lambda c: c.fitness, reverse=True)

        best = candidates[0]
        self.survivors = [c.genotype for c in candidates[:GA_SURVIVORS]]
        self.current_genotype = best.genotype
        self.last_fitness = best.fitness

        print(f"[GA] Gen {self.generation} | Level {level} | "
              f"Best fitness: {best.fitness:.1f} | Genes: {best.genotype}")
        return best.genotype

    def evaluate_fitness(self, genes, grid_class, width, height):
        total = 0.0
        for _ in range(GA_FITNESS_SAMPLES):
            try:
                sim_grid = grid_class(width, height, 1, headless=True)
                sim_grid.apply_genes(genes)
                start_node = sim_grid.nodes[1][1]
                end_node = sim_grid.nodes[width - 2][height - 2]
                path = sim_grid.find_path(start_node, end_node)
                total += len(path)
            except Exception as error:
                print(f"[GA] evaluation error: {error}")
        return total / GA_FITNESS_SAMPLES