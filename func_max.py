from __future__ import annotations      # To overcome NameError when referencing class from within itself
                                        # e.g. Chromosome.crossover(paren: Chromosome)
                                        # Should be solved by python 4.0
from random import choices, random, uniform
from statistics import mean
from typing import List
from tabulate import tabulate
from tkinter import Tk, Button, Label, Text, END, Entry
from copy import deepcopy
import pandas
import matplotlib.pyplot as plt

# Constants
MAX_GENERATION = 500
POPULATION_SIZE = 10

# Global Variables
generations_population = pandas.DataFrame(columns=['Generation', 'A', 'B', 'C', 'Fitness'])     # Saves the population of each generation
generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Fitness stats of each generation [generation, min, max, mean]

# Global Types
class Chromosome:
    def __init__(self, a: float, b: float, c: float) -> None:
        """Intializes the chromosome values, then calculates the fitness
        """
        self.a, self.b, self.c = a, b, c
        self.calculate_fitness()
    
    # For chromosomes comparison
    def __eq__(self, other: object) -> bool:
        """For comparing two chromosomes values

        Args:
            other (object): a chromosome object to compare against

        Returns:
            bool: true if the two chromosomes have identical values
        """
        if not isinstance(other, Chromosome):
            return NotImplemented
        return self.a, self.b, self.c == other.a, other.b, other.c

    
    # Chromosome Fitness Calculation
    def calculate_fitness(self) -> None:
        """Calculates the fitness of the chromosome using the formula:
        f(chromosome) = 2a^2 + b / c- 57
        """
        self.fitness = 2 * self.a ** 2 + self.b / self.c - 57
    
    # Normalizes the Chromosome Fitness
    def normalize_fitness(self, total_population_fitness: float):
        """Normalizes the fitness value

        Args:
            total_population_fitness (float): the sum fitness value of all the individuals in the population
        """
        self.fitness_normalized = self.fitness/total_population_fitness
    
    # Crossover
    def crossover(self, parent: Chromosome) -> List[Chromosome]:
        """Performs the crossover operation between this chromosome instance and another parent

        Args:
            parent (Chromosome): the second parent chromosome

        Returns:
            List[Chromosome]: list of two offsprings produced
        """
        children: List[Chromosome]= []
        if random() < 0.7:
            child1 = Chromosome(self.a, parent.b, parent.c)
            child2 = Chromosome(parent.a, self.b, self.c)
        else:
            child1 = deepcopy(self)
            child2 = deepcopy(parent)
        children.append(child1)
        children.append(child2)
        return children
    
    # Randomly Mutate Genes on the Chromosome
    def mutate(self) -> None:
        """Performs the mutation operation on this chromosome instance
        """
        if random() < 0.1:      # Each gene has a 10% probability of mutating
            self.a = uniform(-500, 100)
        if random() < 0.1:
            self.b = uniform(-500, 500)
        if random() < 0.1:
            self.c = uniform(-12.5, 20)
        self.calculate_fitness()

class Population:
    def __init__(self, chrome_list: List[Chromosome] = []) -> None:
        """Initializes the population object. Empty by default

        Args:
            chrome_list (List[Chromosome], optional): list of individuals. Defaults to [].
        """
        self.chromosomes = chrome_list.copy()
    
    # Creates Random Population
    def random_population(self) -> None:
        """Generates a list of POPULATION_SIZE of chromosomes with random genes' values
        """
        for _ in range(POPULATION_SIZE):
            a = uniform(-500, 100)
            b = uniform(-500, 500)
            c = uniform(-12.5, 20)
            self.chromosomes.append(Chromosome(a, b, c))
        self.calculate_fitness()
    
    # Calculate the normalized fitness of the population
    def calculate_fitness(self) -> None:
        """Gets the fitness value of all individuals and saves it in a local fitness_array variable.
        Also, calculates the normalized fitness values and saves it into a local fitness_normalized_array variable
        """
        self.fitness_array = []     # Flushing the array
        self.fitness_normalized_array = []
        for chrome in self.chromosomes:
            self.fitness_array.append(chrome.fitness)
        total_fitness = sum(self.fitness_array)
        for chrome in self.chromosomes:
            chrome.normalize_fitness(total_fitness)
            self.fitness_normalized_array.append(chrome.fitness_normalized)
        
    
    # Parents Selection
    def select_parents(self) -> List[Chromosome]:
        """Selects two chromosomes for mating using roulette wheel selection method

        Returns:
            List[Chromosome]: a list of two individual candidates for mating
        """
        parents: List[Chromosome] = []
        parent1 = choices(self.chromosomes, weights=self.fitness_array, k=1)[0]
        parents.append(parent1)
        parent2 = choices(self.chromosomes, weights=self.fitness_array, k=1)[0]
        parents.append(parent2)
        return deepcopy(parents)

    
    # Eliminating the Weakest Chromosomes from the population
    def eliminate(self) -> None:
        """Eliminates the individual with lowest fitness score from the population pool
        """
        self.chromosomes.pop(self.fitness_array.index(min(self.fitness_array)))
    
    # Add new chromosome to the population
    def add(self, chrome: Chromosome) -> None:
        """Adds a new individual to the population pool

        Args:
            chrome (Chromosome): the individual to be added
        """
        self.eliminate()
        self.chromosomes.append(chrome)
        self.calculate_fitness()


# Population Fitness Calculations
def population_fitness_stats(epoch: int, pop: Population) -> None:
    """Generates fitness statistics of the population and appends them to the global variable generation_stats

    Args:
        epoch (int): the generation from which the population came from
        pop (Population): the population from which the statistics will be generated
    """
    generations_stats.loc[len(generations_stats)] = [epoch, min(pop.fitness_array), max(pop.fitness_array), mean(pop.fitness_array)]    # Append to the end of the dataframe

# Running the simulation
def run_sim() -> None:
    """Runs the GA for a maximum iterations of MAX_GENERATION.
    Updates the generations_stats and generations_population with each iteration
    """
    pop = Population()
    pop.random_population()
    global generations_stats
    global generations_population
    generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Flushing the dataframe from any previous results
    generations_population = pandas.DataFrame(columns=['Generation', 'A', 'B', 'C', 'Fitness'])

    for i in range(0, MAX_GENERATION):
        population_fitness_stats(i+1, pop)
        parents = pop.select_parents()
        children = parents[0].crossover(parents[1])
        children[0].mutate()
        children[1].mutate()
        pop.add(children[0])
        pop.add(children[1])
        for chrome in pop.chromosomes:
            generations_population.loc[len(generations_population)] = [i+1, chrome.a, chrome.b, chrome.c, chrome.fitness]    # Append to the end of the dataframe

        # TODO Termination condition
        
    





