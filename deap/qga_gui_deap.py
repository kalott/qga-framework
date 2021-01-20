# import one_max_deap
from tkinter import Tk, Button, Label, Text, END, Entry, Grid
from tabulate import tabulate
from statistics import mean
import matplotlib.pyplot as plt
import pandas

# Global variables
generations_population = pandas.DataFrame()#columns=['Generation', 'A', 'B', 'C', 'Fitness'])     # Saves the population of each generation
generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Fitness stats of each generation [generation, min, max, mean]


# Population Fitness Calculations
def population_fitness_stats(epoch: int, pop: list, fitnesses: list) -> None:
    """Generates fitness statistics of the population and appends them to the global variable generation_stats

    Args:
        epoch (int): the generation from which the population came from
        pop (Population): the population from which the statistics will be generated
    """
    generations_stats.loc[len(generations_stats)] = [epoch, min(fitnesses), max(fitnesses), mean(fitnesses)]    # Append to the end of the dataframe

# Resets generations_stats variable
def reset_generations_stats() -> None:
    """Reset the generation_stats global variable
    """
    global generations_stats
    generations_stats = pandas.DataFrame(columns=['Generation', 'Min', 'Max', 'Average'])   # Flushing the dataframe from any previous results

# Saves a copy of the current generation population
def save_generation_population(generation: int, pop: list) -> None:
    """Append a copy of the current generation chromosomes fitness and genes' values into the generations_population global variable

    Args:
        generation (int): ID number of the current generation
        pop (Population): The current population from which the values is extracted
    """
    for chrome in pop:
            generations_population.loc[len(generations_population)] = [generation] + chrome + [chrome.fitness.values[0]]    # Append to the end of the dataframe

# Resets generations_population variable
def reset_generations_population(genes_no: int) -> None:
    """Reset the generation_population global variable

    Args:
        genes_no (int): number of genes in each chromosome
    """
    global generations_population
    generations_population = pandas.DataFrame(columns=['Generation'] + [i+1 for i in range(genes_no)] + ['Fitness'])


def gui() -> None:
    window = Tk()
    window.geometry('+400+100')
    window.title('Function Maximization Problem')
    Grid.columnconfigure(window,0,weight=1)     # Text object can be resized dynamically
    lbl1 = Label(window, text='Results:')
    lbl1.grid(row=0, columnspan=2, sticky='w')
    txt = Text(window, width=70)
    txt.grid(rowspan=5, columnspan=2, sticky='nsew')
    lbl2 = Label(window, text='Enter generation number:')
    lbl2.grid(row=0, column=2, sticky='nsew')
    def show_gen():
        if not etr.get().isdigit():
            txt.delete("1.0", "end")
            txt.insert(END, 'Please run the simulation first,\nthen enter a valid generation number!')
        else:
            generation = int(etr.get())
            if generation > len(generations_population):
                txt.delete("1.0", "end")
                txt.insert(END, 'Please run the simulation first,\nthen enter a valid generation number!')
            else:
                gen_df = generations_population.loc[generations_population["Generation"] == generation]
                generation_string = tabulate(gen_df, headers=list(generations_population.columns), showindex=False)
                txt.delete("1.0", "end")
                txt.insert(END, generation_string)
    def show_stats():
        if len(generations_stats['Generation']) < 1:
            # Showing an error message in the text widget
            txt.delete("1.0", "end")
            txt.insert(END, 'Please run the simulation first!')
        else:
            # Output the simulation results in the text widget
            txt.delete("1.0", "end")
            stats_string = tabulate(generations_stats, headers=list(generations_stats.columns), showindex=False)
            txt.insert(END, stats_string)
    def plot_stats() -> None:
        """Plots the statistics from generations_stats into scatter plot
        """
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

    etr = Entry(window, width=5)
    etr.grid(row=1, column=2)
    btn1 = Button(window, text='Show Population', command=show_gen)
    btn1.grid(row=2, column=2, sticky='n')
    btn3 = Button(window, text='Show Stats', command=show_stats)
    btn3.grid(row=4, column=2, sticky='nsew')
    btn3 = Button(window, text='Show Graph', command=plot_stats)
    btn3.grid(row=5, column=2, sticky='nsew')

    window.focus()
    window.mainloop()
