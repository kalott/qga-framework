import qga_framework
from tkinter import Tk, Button, Label, Text, END, Entry, Grid
from tabulate import tabulate
import matplotlib.pyplot as plt

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
            if generation > len(qga_framework.generations_population):
                txt.delete("1.0", "end")
                txt.insert(END, 'Please run the simulation first,\nthen enter a valid generation number!')
            else:
                gen_df = qga_framework.generations_population.loc[qga_framework.generations_population["Generation"] == generation]
                generation_string = tabulate(gen_df, headers=list(qga_framework.generations_population.columns), showindex=False)
                txt.delete("1.0", "end")
                txt.insert(END, generation_string)
    def show_stats():
        if len(qga_framework.generations_stats['Generation']) < 1:
            # Showing an error message in the text widget
            txt.delete("1.0", "end")
            txt.insert(END, 'Please run the simulation first!')
        else:
            # Output the simulation results in the text widget
            txt.delete("1.0", "end")
            stats_string = tabulate(qga_framework.generations_stats, headers=list(qga_framework.generations_stats.columns), showindex=False)
            txt.insert(END, stats_string)
    def plot_stats() -> None:
        """Plots the statistics from generations_stats into scatter plot
        """
        if len(qga_framework.generations_stats['Generation']) < 1:
            # Showing an error message in the text widget
            txt.delete("1.0", "end")
            txt.insert(END, 'Please run the simulation first!')

        else:
            # Show the plot in a new window
            plt.title('Generations Statistics')
            plt.plot(qga_framework.generations_stats['Generation'], qga_framework.generations_stats['Min'], 'b.-', label='Min')
            plt.plot(qga_framework.generations_stats['Generation'], qga_framework.generations_stats['Max'], 'r.-', label='Max')
            plt.plot(qga_framework.generations_stats['Generation'], qga_framework.generations_stats['Average'], 'g.-', label='Average')
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
