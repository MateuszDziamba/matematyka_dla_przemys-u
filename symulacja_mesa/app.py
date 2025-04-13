'''
SYMULACJĘ URUCHAMIAMY Z TERMINALA
(w VS na dole lub po prostu w folderze używając Otwórz w Terminalu)
będąc w tym folderze wpisujemy:
solara run app.py
po prostu odpalenie plików nic nie da
'''
'''
===== DO ZROBIENIA =========
- schematy poruszanie BNE i RF
- zmiana prędkości w zależności od density (to zrobi pewnie większą różnicę w porównaniu innych z BNE) - jak a artykule i jest zaczęte w agents.py
- dodatkowe wykresy i ustawienie elementów na stronie
- widoczność drzwi i ich szerokości na wykresach
- dodatkowe suwaki np. szerokość drzwi
- pewnie coś jeszcze...
============================
'''


from model import Evacuation
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import imageio
import os
import solara
from mesa.visualization import SolaraViz, make_plot_component, make_space_component
from mesa.visualization.utils import update_counter
from matplotlib.figure import Figure

#heatmapa zapisywana do pliku jak wcześniej
def heatmap():
    os.makedirs("plots", exist_ok=True)
    frame_paths = []

    step_num = 0

    while len(model.agents.get("exited"))>0:
        agent_counts = np.zeros((model.grid.width, model.grid.height))
        for cell_content, (x, y) in model.grid.coord_iter():
            agent_count = len(cell_content)
            agent_counts[x][y] = agent_count
        plt.figure(figsize=(model.grid.width, model.grid.height))
        sns.heatmap(agent_counts.T, cmap="viridis", annot=True, cbar=True, vmin = 0, vmax = model.number_persons//10)
        plt.gca().invert_yaxis()
        plt.title(f"Step {step_num}")
        frame_path = f"plots/frame_{step_num:03}.png"
        plt.savefig(frame_path)
        plt.close()
        frame_paths.append(frame_path)
        model.step()
        step_num += 1

    #pusta plansza na koniec
    agent_counts = np.zeros((model.grid.width, model.grid.height))
    plt.figure(figsize=(model.grid.width, model.grid.height))
    sns.heatmap(agent_counts.T, cmap="viridis", annot=True, cbar=True, vmin = 0, vmax = model.number_persons//10)
    plt.gca().invert_yaxis()
    plt.title(f"Step {step_num}")
    frame_path = f"plots/frame_{step_num:03}.png"
    plt.savefig(frame_path)
    plt.close()
    frame_paths.append(frame_path)

    #gif
    frames = []
    for frame_path in frame_paths:
        frames.append(imageio.imread(frame_path))

    gif_path = "plots/ewakuacja.gif"
    imageio.mimsave(gif_path, frames, fps=4, loop=1)

    for path in frame_paths:
        os.remove(path)

#testowo, solara domyślnie robi taki plot - patrz niżej ScatterPlot
def scatter_plot():
    #wersja testowa
    while len(model.agents.get("exited"))>0:
        model.step()
    agents_data = model.datacollector.get_agent_vars_dataframe()
    for step in (np.unique(agents_data.index.get_level_values("Step"))):
        sns.scatterplot(data=agents_data.xs(step, level = "Step"), x= "x", y= "y")
        plt.show()
    

#możemy wykorzystywać informacje o agencie oraz te zebrane przez data.collector (patrz model.py)
def agent_portrayal(agent):
    return {
        "x": agent.pos[0],
        "y": agent.pos[1]
    }


def ScatterPlot(model):
    if not model.agents:
        return solara.Markdown("## Ewakuacja zakończona")
    model.step_callback = True
    return make_space_component(agent_portrayal)(model)

#liczba osób pozostałych na planszy, wykres liniowy
EvPlot = make_plot_component("evacuating")

model = Evacuation(80,20,10)

#w dokumentacji Custom Components
#https://mesa.readthedocs.io/stable/tutorials/visualization_tutorial.html
#heatmapa jak wcześniej w aplikacji automatycznie się aktualizuje
@solara.component
def Heatmap(model):
    update_counter.get()
    agent_counts = np.zeros((model.grid.width, model.grid.height))
    for cell_content, (x, y) in model.grid.coord_iter():
        agent_count = len(cell_content)
        agent_counts[x][y] = agent_count
    fig = Figure(figsize=(model.grid.width, model.grid.height))
    ax = fig.subplots()
    sns.heatmap(agent_counts.T, cmap="viridis", annot=True, cbar=True, vmin = 0, vmax = model.number_persons//10, ax=ax)
    ax.invert_yaxis()
    solara.FigureMatplotlib(fig)


#definiujemy stronę, wszystkie wykresy które chcemy zdefiniowane
#wyżej wpisujemy w components (nie muszą być wszystkie na raz)
page = SolaraViz(
    model,
    model_params={
        "n": {
        "type": "SliderInt",
        "value": 10,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,

        },
        "width": {
        "type": "SliderInt",
        "value": 20,
        "label": "Width:",
        "min": 10,
        "max": 100,
        "step": 10,

        },
        "height": 10
    },
    components=[
        ScatterPlot,
     Heatmap,
    EvPlot
    ],
    name = "Model Ewakuacji"
)
page
