from __future__ import annotations      # To overcome NameError when referencing class from within itself
                                        # e.g. Chromosome.crossover(parent: Chromosome)
                                        # Should be solved by Python v4.0 (or 3.10?)
from random import choice, choices, random, uniform, randint, seed
from statistics import mean
from typing import List, Callable
from tabulate import tabulate
from copy import deepcopy
import pandas
from sys import maxsize

# Global Variables
generations_population = pandas.DataFrame()#columns=['Generation', 'A', 'B', 'C', 'Fitness'])     # Saves the population of each generation
generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Fitness stats of each generation [generation, min, max, mean]
fitness_formula: Callable
random_seed = randint(0, maxsize)
seed(random_seed)

# Global Types
class Chromosome:
    def __init__(self, genes: List, genes_limits: List, discrete: bool) -> None:
        """Intializes the chromosome values, then calculates the fitness
        """
        self.genes = genes
        self.calculate_fitness()
        self.genes_limits = genes_limits
        self.discrete = discrete
    
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
        return self.genes == other.genes

    
    # Chromosome Fitness Calculation
    def calculate_fitness(self) -> None:
        """Calculates the fitness of the chromosome using the formula defined in the global variable
        fitness_formula
        """
        try:
            self.fitness = fitness_formula(self)
        except NameError:
            print("""A fitness function has not been defined
            Hint:
            def foo(chromosome):
                return chromosome.genes[0] * 2 + chromosome.genes[1] / 6
            global fitness_formula
            fitness_formula = foo""")
            raise SystemExit
        
        
    
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
        genes1 = deepcopy(self.genes)
        genes2 = deepcopy(parent.genes)
        tempgenes = deepcopy(self.genes)
        if random() < 0.7:      # 70% probability for the crossover to happen
            locus = randint(1, len(self.genes) - 1)
            genes1 = genes1[:locus] + genes2[locus:]
            genes2 = genes2[:locus] + tempgenes[locus:]
        child1 = Chromosome(genes1, self.genes_limits, self.discrete)
        child2 = Chromosome(genes2, self.genes_limits, self.discrete)
        children.append(child1)
        children.append(child2)
        return children
        
    
    ## Randomly Mutate Genes on the Chromosome (Random approach)
    # def mutate(self) -> None:
    #     """Performs the mutation operation on this chromosome instance
    #     """
    #     if self.discrete:
    #         for i in range(len(self.genes)):
    #             if random() < 0.1:      # Each gene has a 10% probability of mutating
    #                 self.genes[i] = randint(self.genes_limits[i][0], self.genes_limits[i][1])
    #     else:
    #         for i in range(len(self.genes)):
    #             if random() < 0.1:
    #                 self.genes[i] = uniform(self.genes_limits[i][0], self.genes_limits[i][1])
    #     self.calculate_fitness()

    ## Randomly Mutate Genes on the Chromosome (Newtonian approach)
    def mutate(self) -> None:
        """Performs the mutation operation on this chromosome instance
        """
        if self.discrete:
            for i in range(len(self.genes)):
                if random() < 0.1:      # Each gene has a 10% probability of mutating
                    self.genes[i] = randint(self.genes_limits[i][0], self.genes_limits[i][1])
        else:
            for i in range(len(self.genes)):
                if random() < 0.1:
                    # Check whether increasing the gene value or decreasing it produce better fitness
                    inc_genes = deepcopy(self.genes)
                    inc_genes[i] += 0.5
                    dec_genes = deepcopy(self.genes)
                    dec_genes[i] -= 0.5
                    inc_chrome = Chromosome(inc_genes, self.genes_limits, self.discrete)
                    dec_chrome = Chromosome(dec_genes, self.genes_limits, self.discrete)

                    # Perform the mutation in the favorable direction
                    if inc_chrome.fitness > dec_chrome.fitness:
                        self.genes[i] = uniform(self.genes[i], self.genes_limits[i][1])
                    else:
                        self.genes[i] = uniform(self.genes_limits[i][0], self.genes[i])                    
        self.calculate_fitness()

class Population:
    def __init__(self, chrome_list: List[Chromosome] = []) -> None:
        """Initializes the population object. Empty by default

        Args:
            chrome_list (List[Chromosome], optional): list of individuals. Defaults to [].
        """
        self.chromosomes = deepcopy(chrome_list)
        
    # Creates Random Population
    def random_population(self, pop_size: int, genes_limits: List, discrete: bool) -> None:
        """Generates a list of chromosomes with random genes' values

        Args:
            pop_size (int): Number of chromosomes to be produced
            genes_limits (List): A list of genes lower and upper values e.g. [[0,1], [-4,5], [-12.4, 1]]
            discrete (bool): Whether the genes are integers or floats. True = integers
        """
        if discrete:
            for _ in range(pop_size):
                genes = []
                for limits in genes_limits:
                    genes.append(randint(limits[0], limits[1]))
                self.chromosomes.append(Chromosome(genes, genes_limits, discrete))
        else:
            for _ in range(pop_size):
                genes = []
                for limits in genes_limits:
                    genes.append(uniform(limits[0], limits[1]))
                self.chromosomes.append(Chromosome(genes, genes_limits, discrete))
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
        
    
    # # Parents Selection (Roulette Wheel)
    # def select_parents(self) -> List[Chromosome]:
    #     """Selects two chromosomes for mating using roulette wheel selection method

    #     Returns:
    #         List[Chromosome]: a list of two individual candidates for mating
    #     """
    #     parents: List[Chromosome] = []
    #     parent1 = choices(self.chromosomes, weights=self.fitness_normalized_array, k=1)[0]
    #     parents.append(parent1)
    #     parent2 = choices(self.chromosomes, weights=self.fitness_normalized_array, k=1)[0]
    #     parents.append(parent2)
    #     return deepcopy(parents)

    # A method to be used locally inside the select_parents() method
    def get_parent(self) -> Chromosome:
        """Returns a single individual from the population to be used as a parent

        Returns:
            Chromosome: the parent candidate
        """
        parent1: Chromosome = choice(self.chromosomes)
        parent2 = choice(self.chromosomes)
        while parent1 == parent2:   # ensure uniqueness of candidates
            parent2 = choice(self.chromosomes)
        if parent1.fitness > parent2.fitness:
            if random() < 0.75:     # the fitter individual has a 75% chance of being chosen
                return parent1
            else:
                return parent2
        else:
            if random() < 0.75:
                return parent2
            else:
                return parent1

    # Parents Selection (Tournament)
    def select_parents(self) -> List[Chromosome]:
        """Selects two chromosomes for mating using tournament selection method

        Returns:
            List[Chromosome]: a list of two individual candidates for mating
        """
        parents: List[Chromosome] = []
        parent1 = self.get_parent()
        parents.append(parent1)
        parent2 = self.get_parent()
        while parent1 == parent2:   # ensure uniqueness of parents
            parent2 = self.get_parent()
        parents.append(parent2)
        return deepcopy(parents)
    
    

    # Eliminating the Weakest Chromosomes from the population
    def eliminate(self) -> None:
        """Eliminates the individual with lowest fitness score from the population pool
        """
        self.chromosomes.pop(self.fitness_normalized_array.index(min(self.fitness_normalized_array)))
    
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

# Resets generations_stats variable
def reset_generations_stats() -> None:
    """Reset the generation_stats global variable
    """
    global generations_stats
    generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Flushing the dataframe from any previous results

# Saves a copy of the current generation population
def save_generation_population(generation: int, pop: Population) -> None:
    """Append a copy of the current generation chromosomes fitness and genes' values into the generations_population global variable

    Args:
        generation (int): ID number of the current generation
        pop (Population): The current population from which the values is extracted
    """
    for chrome in pop.chromosomes:
            generations_population.loc[len(generations_population)] = [generation] + chrome.genes + [chrome.fitness]    # Append to the end of the dataframe

# Resets generations_population variable
def reset_generations_population(genes_no: int) -> None:
    """Reset the generation_population global variable

    Args:
        genes_no (int): number of genes in each chromosome
    """
    global generations_population
    generations_population = pandas.DataFrame(columns=['Generation'] + [i+1 for i in range(genes_no)] + ['Fitness'])


# Running the simulation
def run_sim(fit_func: Callable, genes_limits: List[List[float]], no_of_generations: int = 500, discrete: bool = True, pop_size: int = 10) -> None:
    """Runs the GA for a maximum iterations of no_of_generations.
    Updates the generations_stats and generations_population with each iteration

    Args:
        fit_func (Callable): The fitness calculation function
        genes_limits (List[List[float]]): A list of each gene lower and upper limits' values
        no_of_generations (int, optional): number of generations to be produced. Defaults to 500.
        discrete (bool, optional): Whether the genes values are integers of floats. Defaults to True = integers.
        pop_size (int, optional): number of individuals in each generation. Defaults to 10.
    """
    global fitness_formula
    fitness_formula = fit_func
    pop = Population()
    pop.random_population(pop_size, genes_limits, discrete)
    reset_generations_stats()
    reset_generations_population(len(pop.chromosomes[0].genes))
    for i in range(0, no_of_generations):
        parents = pop.select_parents()
        children = parents[0].crossover(parents[1])
        children[0].mutate()
        children[1].mutate()
        pop.add(children[0])
        pop.add(children[1])
        save_generation_population(i+1, pop)
        population_fitness_stats(i+1, pop)
        # TODO Termination condition
    print(f'All randomness generated from the seed: {random_seed}')

        
    





