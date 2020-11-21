from random import choices, random
from statistics import mean
from typing import List
from tabulate import tabulate
from tkinter import Tk, Button, Label, Text, END
import pandas
import matplotlib.pyplot as plt


# Global Types
class Chromosome:
    def __init__(self, genes_list: List[int] = []):
        self.genes = genes_list.copy()
        self.calculate_fitness()
    
    # For chromosomes comparison
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Chromosome):
            return NotImplemented
        return self.genes == other.genes
    
    # Chromosome Fitness Calculation
    def calculate_fitness(self) -> None:
        self.fitness = 0
        for gene in self.genes:
            self.fitness += gene
    
    # Normalizes the Chromosome Fitness
    def normalize_fitness(self, total_population_fitness: int):
        self.normalized_fitness = self.fitness/total_population_fitness

class Population:
    def __init__(self, chrome_list: List[Chromosome] = []) -> None:
        self.chromosomes = chrome_list.copy()
    
    # Creates Random Population
    def random_population(self) -> None:
        for i in range(POPULATION_SIZE):
            self.chromosomes.append(Chromosome(choices([0, 1], k=LENGTH)))
        self.calculate_fitness()
    
    # Calculate the normalized fitness of the population
    def calculate_fitness(self) -> None:
        self.fitness_array = []     # Flushing the array
        for chrome in self.chromosomes:
            self.fitness_array.append(chrome.fitness)
        total_fitness = sum(self.fitness_array)
        for chrome in self.chromosomes:
            chrome.normalize_fitness(total_fitness)
    
    # Parents Selection
    def select_parents(self) -> List[Chromosome]:
        parents: List[Chromosome] = []
        parent1 = choices(self.chromosomes, weights=self.fitness_array, k=1)[0]
        parents.append(parent1)
        parent2 = choices(self.chromosomes, weights=self.fitness_array, k=1)[0]
        while parent1 == parent2:   # ensuring parents are separate individual
            parent2 = choices(self.chromosomes, weights=self.fitness_array, k=1)[0]
        parents.append(parent2)
        return parents

    # Crossover
    def crossover(self, parents: List[Chromosome]) -> List[Chromosome]:
        children = []
        child1 = Chromosome(parents[0].genes[0:10] + parents[1].genes[10:])
        child2 = Chromosome(parents[1].genes[0:10] + parents[0].genes[10:])
        children.append(child1)
        children.append(child2)
        return children
    
    # Randomly Mutate Genes on the Chromosome
    def mutate(self, child: Chromosome) -> None:
        for i in range(LENGTH):
            if random() < 0.1:      # Each gene has a 10% probability of mutating
                child.genes[i] = 0 if child.genes[i] == 1 else 1
        child.calculate_fitness()

    # Eliminating the Weakest Chromosomes from the population
    def eliminate(self) -> None:
        self.chromosomes.pop(self.fitness_array.index(min(self.fitness_array)))
    
    # Add new chromosome to the population
    def add(self, chrome: Chromosome) -> None:
        self.eliminate()
        self.chromosomes.append(chrome)
        self.calculate_fitness()

# Constants
LENGTH = 20     # Length of each chromosome
MAX_GENERATION = 100
POPULATION_SIZE = 10
TARGET_FITNESS = 20

# Global Variables
generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Fitness stats of each generation [generation, min, max, mean]
window = Tk()
txt = Text(window, width=40)

# Population Fitness Calculations
def population_fitness_stats(epoch: int, pop: Population) -> None:
    generations_stats.loc[len(generations_stats)] = [epoch, min(pop.fitness_array), max(pop.fitness_array), mean(pop.fitness_array)]    # Append to the end of the dataframe

# Plotting the Stats
def plot_stats() -> None:
    if len(generations_stats['Generation']) < 1:
        # Showing an error message in the text widget
        txt.delete("1.0", "end")
        txt.insert(END, 'Please run the simulation first!')

    else:
        # Show the plot in a new window
        plt.title('Generations Statistics')
        plt.plot(generations_stats['Generation'], generations_stats['Min'], 'b.-', label='Min')
        plt.plot(generations_stats['Generation'], generations_stats['Max'], 'r.-', label='Max')
        plt.plot(generations_stats['Generation'], generations_stats['Average'], 'g.-', label='Average')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.legend()
        plt.show()

# Running the simulation
def run_sim() -> None:
    pop = Population()
    pop.random_population()
    global generations_stats
    generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Flushing the dataframe from any previous results
    for i in range(0, MAX_GENERATION):
        population_fitness_stats(i+1, pop)
        parents = pop.select_parents()
        children = pop.crossover(parents)
        pop.mutate(children[0])
        pop.mutate(children[1])
        pop.add(children[0])
        pop.add(children[1])

        # Termination condition
        if generations_stats.iloc[i, 2] == 20:
            break
    
    # Output the simulation results in the text widget
    txt.delete("1.0", "end")
    stats_string = tabulate(generations_stats, headers=['Generation', 'Min', 'Max', 'Average'], showindex=False)
    txt.insert(END, stats_string)


# Show a Scatterplot of min, max and average Population Fitness over the Generations
def gui() -> None:
    window.geometry('+400+100')
    window.title('Binary String Problem')
    txt.grid(rowspan=3, columnspan=2, sticky='nsew')
    btn1 = Button(window, text='Run', command=run_sim)
    btn1.grid(row=1, column=2, sticky='nsew')
    btn2 = Button(window, text='Show Graph', command=plot_stats)
    btn2.grid(row=2, column=2, sticky='nsew')
    window.focus()
    window.mainloop()


