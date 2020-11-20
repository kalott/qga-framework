from random import choices, randint
from statistics import mean
from typing import List
from tabulate import tabulate
from tkinter import Tk, Button, Label, Text, StringVar, LEFT, RIGHT,X, Y, BOTH, END
import pandas
import matplotlib.pyplot as plt


# Global Types
Chromosome = List[int]
Population = List[Chromosome]

# Constants
LENGTH = 20     # Length of each chromosome
MAX_GENERATION = 100
POPULATION_SIZE = 10
TARGET_FITNESS = 20

# Global Variables
generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Fitness stats of each generation [generation, min, max, mean]
window = Tk()
txt = Text(window, width=40)

# Population Creation
def random_population() -> Population:
    pop = []
    for i in range(POPULATION_SIZE):
        pop.append(choices([0, 1], k=LENGTH))
    return pop

# Chromosome Fitness Calculation
def chromosome_fitness(chrome: Chromosome) -> int:
    fitness = 0
    for gene in chrome:
        fitness += gene
    return fitness

# Population Fitness Calculations
def population_fitness_stats(epoch: int, pop: Population) -> None:
    fit_array = []
    for chrome in pop:
        fit_array.append(chromosome_fitness(chrome))
    generations_stats.loc[len(generations_stats)] = [epoch, min(fit_array), max(fit_array), mean(fit_array)]    # Append to the end of the dataframe
    #TODO normalization

# Parents Selection
def select_parents(population: Population) -> Population:
    pop = population.copy()     # to avoid modifying the original list referenced in the func parameter
    fit_array = []
    parents = []
    for chrome in pop:
        fit_array.append(chromosome_fitness(chrome))

    max_fitness = max(fit_array)
    indices = []
    for i in range(len(fit_array)):
        if fit_array[i] == max_fitness:
            indices.append(i)
    if len(indices) > 1:
        for i in range(2):
            parents.append(pop[indices[i]])
        return parents
    else:
        parents.append(pop[indices[0]])
        pop.pop(indices[0])
        fit_array.pop(indices[0])
        parents.append(pop[fit_array.index(max(fit_array))])
        return parents

# Crossover
def crossover(parents: Population) -> Population:
    children = []
    children.append(parents[0][0:10] + parents[1][10:])
    children.append(parents[1][0:10] + parents[0][10:])
    return children

# Randomly Mutate Genes on the Chromosome
def mutate(child: Chromosome) -> None:
    locuses = choices([i for i in range(20)], k=3)      # Locations of the genes to mutate on the chromosome. k = number of genes to mutate
    for i in locuses:
        child[i] = 0 if child[i] == 1 else 1

# Eliminating the Weakest
def eliminate(population: Population) -> None:
    fit_array = []
    for chrome in population:
        fit_array.append(chromosome_fitness(chrome))
    population.pop(fit_array.index(min(fit_array)))

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
    pop = random_population()
    global generations_stats
    generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Flushing the dataframe from any previous results
    for i in range(0, MAX_GENERATION):
        population_fitness_stats(i+1, pop)
        parents = select_parents(pop)
        children = crossover(parents)
        mutate(children[0])
        mutate(children[1])
        pop.extend(children)
        eliminate(pop)
        eliminate(pop)

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
    txt.grid(rowspan=3, columnspan=2, sticky='nsew')
    btn1 = Button(window, text='Run', command=run_sim)
    btn1.grid(row=1, column=2, sticky='nsew')
    btn2 = Button(window, text='Show Graph', command=plot_stats)
    btn2.grid(row=2, column=2, sticky='nsew')
    window.focus()
    window.mainloop()


