import qga_framework, qga_gui

# Function Maximaization Problem
def fitness_func(self: qga_framework.Chromosome):
        return 2 * self.genes[0] ** 2 + self.genes[1] / self.genes[2] - 57
    
genes_limits = [[-500, +100], [-500, 500], [-12.5, 20]]
qga_framework.run_sim(fit_func = fitness_func, genes_limits = genes_limits, no_of_generations = 300, discrete = False, pop_size = 10)
qga_gui.gui()

# # Binary String Problem
# def fitness_func(self: qga_framework.Chromosome):
#     fitness = 0
#     for gene in self.genes:
#         fitness += gene
#     return fitness

# genes_limits = [[0, 1] for i in range(20)]
# qga_framework.run_sim(fit_func=fitness_func, genes_limits=genes_limits, no_of_generations=500, discrete=True, pop_size=10)
# qga_gui.gui()
