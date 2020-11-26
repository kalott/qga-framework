from __future__ import annotations      # To overcome NameError when referencing class from within itself
                                        # e.g. Chromosome.crossover()
                                        # Should be solved by python 4.0
from random import randint, choices, random
from statistics import mean
from typing import List
from tabulate import tabulate
from tkinter import Tk, Button, Label, Text, END, Entry
import pandas
import matplotlib.pyplot as plt

# Constants
LENGTH = 20     # Length of each chromosome
MAX_GENERATION = 100
POPULATION_SIZE = 10
TARGET_FITNESS = 20

# Global Variables
generations_population: List[List[Chromosome]] = []     # Saves the population of each generation
generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Fitness stats of each generation [generation, min, max, mean]
window = Tk()
txt = Text(window, width=70)

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
    
    # Crossover
    def crossover(self, parent: Chromosome) -> List[Chromosome]:
        copy1 = self.genes.copy()
        copy2 = parent.genes.copy()
        if random() < 0.7:
            locus = randint(1, LENGTH-1)    # the locus at which the crossover occurs
            genes_copy = self.genes.copy()
            child1 = Chromosome(copy1[:locus] + copy2[locus:])
            child2 = Chromosome(copy2[:locus] + genes_copy[locus:])
            return [child1, child2]
        else:
            child1 = Chromosome(copy1)
            child2 = Chromosome(copy2)
            return [child1, child2]
    
    # Randomly Mutate Genes on the Chromosome
    def mutate(self) -> None:
        for i in range(LENGTH):
            if random() < 0.1:      # Each gene has a 10% probability of mutating
                self.genes[i] = 0 if self.genes[i] == 1 else 1
        self.calculate_fitness()
    
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
        parents.append(parent2)
        return parents

    # Eliminating the Weakest Chromosomes from the population
    def eliminate(self) -> None:
        self.chromosomes.pop(self.fitness_array.index(min(self.fitness_array)))
    
    # Add new chromosome to the population
    def add(self, chrome: Chromosome) -> None:
        self.eliminate()
        self.chromosomes.append(chrome)
        self.calculate_fitness()


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
    global generations_population
    generations_population = []     # Flushing the variable with each run
    generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Flushing the dataframe from any previous results
    for i in range(0, MAX_GENERATION):
        population_fitness_stats(i+1, pop)
        parents = pop.select_parents()
        children = parents[0].crossover(parents[1])
        children[0].mutate()
        children[1].mutate()
        pop.add(children[0])
        pop.add(children[1])
        generations_population.append(pop.chromosomes.copy())
        # Termination condition
        if generations_stats.iloc[i, 2] == 20:
            break
    
    # Output the simulation results in the text widget
    txt.delete("1.0", "end")
    stats_string = tabulate(generations_stats, headers=['Generation', 'Min', 'Max', 'Average'], showindex=False)
    txt.insert(END, stats_string)


# Show a Scatterplot of min, max and average Population Fitness over the Generations
def gui() -> None:
    def show_gen():
        if not etr.get().isdigit():
            txt.delete("1.0", "end")
            txt.insert(END, 'Please run the simulation first,\nthen enter a valid generation number!')
        else:
            generation = int(etr.get()) - 1
            if generation > len(generations_population):
                txt.delete("1.0", "end")
                txt.insert(END, 'Please run the simulation first,\nthen enter a valid generation number!')
            else:
                text = '\n'
                for chrome in generations_population[generation]:
                    text += str(chrome.genes) + '\n'
                txt.delete("1.0", "end")
                txt.insert(END, text)

    window.geometry('+400+100')
    window.title('Binary String Problem')
    lbl1 = Label(window, text='Results:')
    lbl1.grid(row=0, columnspan=2, sticky='w')
    txt.grid(rowspan=4, columnspan=2, sticky='nsew')
    lbl2 = Label(window, text='Enter generation number:')
    lbl2.grid(row=0, column=2, sticky='nsew')
    etr = Entry(window, width=5)
    etr.grid(row=1, column=2)
    btn1 = Button(window, text='Show Population', command=show_gen)
    btn1.grid(row=2, column=2, sticky='n')
    btn2 = Button(window, text='Run', command=run_sim)
    btn2.grid(row=3, column=2, sticky='nsew')
    btn3 = Button(window, text='Show Graph', command=plot_stats)
    btn3.grid(row=4, column=2, sticky='nsew')

    window.focus()
    window.mainloop()
    





