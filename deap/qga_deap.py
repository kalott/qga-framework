from copy import deepcopy

from deap.tools.init import initIterate, initRepeat
import qga_gui_deap
from deap import base, creator, tools
from random import choice, randint, random, seed, uniform, sample
# from __future__ import annotations      # To overcome NameError when referencing class from within itself
                                        # e.g. Chromosome.crossover(parent: Chromosome)
                                        # Should be solved by Python v4.0 (or 3.10?)
from statistics import mean
from math import sqrt
# import sys
from typing import List, Callable, Sequence
# from tabulate import tabulate
# from copy import deepcopy
# import pandas
from sys import maxsize
from typing import List, Callable

# Randomness seed (for replication purposes)
random_seed = randint(0, maxsize)
seed(random_seed)

# OneMax Problem
def main_oneMax():

    #Contatiners
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()

    #Generators
    toolbox.register("attr_bool", randint, 0, 1)    #Genes generator
    toolbox.register("individual_bool", tools.initRepeat, creator.Individual, toolbox.attr_bool, 10)    #Chromosomes generator
    toolbox.register("population_bool", tools.initRepeat, list, toolbox.individual_bool)  #Population generator

    #Fitness Evaluation function
    def evalOneMax(individual):
        return [sum(individual)]
    
    #Operators
    toolbox.register("evaluate", evalOneMax)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    
    pop = toolbox.population_bool(n=10)
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    
    CXPB, MUTPB = 0.5, 0.2 # Probability for cross and mutate operators

    fits = [ind.fitness.values[0] for ind in pop]

    g = 0

    qga_gui_deap.reset_generations_stats()
    qga_gui_deap.reset_generations_population(len(pop[0]))

    while max(fits) < 10 and g < 100:
        g += 1
        print(f"-- Generation {g} --")

        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring)) #make a deepcopy

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]            
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        pop[:] = offspring
        
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        avg = mean(fits)
        sum2 = sum(x*x for x in fits)
        std = abs(sum2/length-avg**2)**0.5

        print(f"    Min : {min(fits)}   Max : {max(fits)}   Average : {avg:.2f}   Std : {std:.2f}")
        qga_gui_deap.save_generation_population(g, pop)
        qga_gui_deap.population_fitness_stats(g, pop, fits)
    
    print(f'All randomness generated from the seed: {random_seed}')
    qga_gui_deap.gui()

# Polynomial Max Problem
def main_poly():
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()

    #Generators
    toolbox.register("attr_float", uniform)    #Genes generator

    func_seq: List[Callable] = []   # list of functions the algorithm will cycle through to create individual's genes
    BOUND_LOW: List[float] = [-500, -500, -12.5]    # the lower bounds of each gene
    BOUND_UP: List[float] = [100, 500, 20]  # the upper bounds of each gene
    for i in range(len(BOUND_LOW)):
        def fun(_low = BOUND_LOW[i], _up = BOUND_UP[i]):
            return toolbox.attr_float(_low, _up)
        func_seq.append(fun)

    toolbox.register("individual", tools.initCycle, creator.Individual, func_seq)    #Chromosomes generator
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)  #Population generator

    #Fitness function
    def evalFuncMax(individual):
        return [2 * individual[0] ** 2 + individual[1] / individual[2] - 57]

    #Operators
    toolbox.register("evaluate", evalFuncMax)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutPolynomialBounded, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=10)
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    
    CXPB, MUTPB = 0.5, 0.2 # Probability for cross and mutate operators

    fits = [ind.fitness.values[0] for ind in pop]

    qga_gui_deap.reset_generations_stats()
    qga_gui_deap.reset_generations_population(len(pop[0]))

    g = 0   #Generation count

    while g < 300:
        g += 1
        # print(f"-- Generation {g} --")

        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring)) #make a deepcopy

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random() < MUTPB:
                toolbox.mutate(mutant, eta=10, low=BOUND_LOW, up=BOUND_UP)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]            
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        pop[:] = offspring

        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits)/length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2/length-mean**2)**0.5
        # print(f"    Min : {min(fits)}   Max : {max(fits)}   Average : {mean:.2f}   Std : {std:.2f}")
        # Save generation stats
        qga_gui_deap.save_generation_population(g, pop)
        qga_gui_deap.population_fitness_stats(g, pop, fits)
    
    print(f'All randomness generated from the seed: {random_seed}')
    qga_gui_deap.gui()


# Traveling Salesman Problem
def main_tsp():
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)
    toolbox = base.Toolbox()

    cities_coords = [(1, 5), (3, 1), (6, 9), (4, 2), (8, 7), (2, 4), (9, 3), (7, 7), (5, 2), (1, 7)]
    # def ind_gen():
    #     while True:
    #         coords = deepcopy(cities_coords)
    #         for _ in range(len(coords)):
    #             index = randint(0, len(coords)-1)
    #             yield coords[index]
    #             del coords[index]
    
    toolbox.register("indexes", sample, cities_coords, k=len(cities_coords))
    toolbox.register("individual", initIterate, creator.Individual, toolbox.indexes)
    toolbox.register("population", initRepeat, list, toolbox.individual)

    # Fitness Function
    def evalTSM(individual):
        sum_distance = 0
        pre_x, pre_y = individual[0]    #previous city coordinates
        i = 1
        while i < len(individual):
            cur_x, cur_y = individual[i]
            sum_distance += sqrt((cur_x-pre_x)**2 + (cur_y-pre_y)**2)
            pre_x, pre_y = cur_x, cur_y
            i += 1
        return sum_distance,
    
    # Mutation Function
    def mutTSM(individual: Sequence, indpb):
        for i in range(len(individual)):
            if random() < indpb:
                mut_gene = choice(cities_coords)
                individual[individual.index(mut_gene)] = deepcopy(individual[i])
                individual[i] = deepcopy(mut_gene)
        return individual,

    # Crossover
    def orderCX(parent1, parent2):
        # convert list of cities' coords into indexes
        def ind_indices(individual):
            indices = []
            for gene in individual:
                indices.append(cities_coords.index(gene))
            return indices
        
        # convet list of indexes into cities' coords
        def ind_coords(individual):
            coords = []
            for gene in individual:
                coords.append(cities_coords[gene])
            return coords

        p1_indices = ind_indices(parent1)
        p2_indices = ind_indices(parent2)
        c1_indices, c2_indices = tools.cxOrdered(p1_indices, p2_indices)
        c1 = ind_coords(c1_indices)
        c2 = ind_coords(c2_indices)
        return c1, c2


    # Operators
    toolbox.register("evaluate", evalTSM)
    toolbox.register("mate", orderCX)
    toolbox.register("mutate", mutTSM, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=10)

    pop = toolbox.population(n=20)
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    
    CXPB, MUTPB = 0.5, 0.2 # Probability for cross and mutate operators

    fits = [ind.fitness.values[0] for ind in pop]

    qga_gui_deap.reset_generations_stats()
    qga_gui_deap.reset_generations_population(len(pop[0]))

    g = 0   #Generation count

    while g < 200:
        g += 1
        # print(f"-- Generation {g} --")

        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring)) #make a deepcopy

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]            
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        pop[:] = offspring

        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits)/length
        sum2 = sum(x*x for x in fits)
        # std = abs(sum2/length-mean**2)**0.5
        # print(f"    Min : {min(fits)}   Max : {max(fits)}   Average : {mean:.2f}   Std : {std:.2f}")
        # Save generation stats
        qga_gui_deap.save_generation_population(g, pop)
        qga_gui_deap.population_fitness_stats(g, pop, fits)
    
    print(f'All randomness generated from the seed: {random_seed}')
    qga_gui_deap.gui()






if __name__ == "__main__":
    # main_oneMax()
    # main_poly()
    main_tsp()

