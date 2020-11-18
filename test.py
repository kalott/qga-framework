import qga


pop = qga.random_population()
for i in range(0, qga.MAX_GENERATION):
    qga.population_fitness_stats(i+1, pop)
    parents = qga.select_parents(pop)
    children = qga.crossover(parents)
    qga.mutate(children[0])
    qga.mutate(children[1])
    pop.extend(children)
    qga.eliminate(pop)
    qga.eliminate(pop)

    # Termination condition
    if qga.generations_stats[i][2] == 20:
        break
    
qga.print_stats()
