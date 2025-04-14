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
- dobrze by było ustabilizować zakres 0y na wykresach 
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
    if agent.BNE_type:
        color = "#7b1fa2"
    else:
        color = "#1565c0"
    
    return {
        "x": agent.pos[0],
        "y": agent.pos[1],
        "color": color
    }

def post_process(model):
    def inner(ax):
        ax.set_aspect("equal")
        ax.get_figure().set_size_inches(10, 10)

        width = model.grid.width
        height = model.grid.height

        # Górna i dolna ściana (ciągłe linie)
        ax.plot([-0.5, width - 0.5], [-0.5, -0.5], color='black', linewidth=6)          
        ax.plot([-0.5, width - 0.5], [height - 0.5, height - 0.5], color='black', linewidth=6)

        # Lewa i prawa ściana z przerwami na drzwi
        for door in model.exits:
            x, y_list = model.exits[door]
            y_set = set(y_list)
            if door == "left":
                wall_x = x - 0.5
            else:
                wall_x = x + 0.5
            for y in range(height):
                if y not in y_set:
                    ax.plot([wall_x, wall_x], [y - 0.5, y + 0.5], color='black', linewidth=6)
    return inner


@solara.component
def SpeedPlot(model):
    update_counter.get()

    fig = Figure(figsize=(6, 4))
    ax = fig.subplots()

    df = model.datacollector.get_agent_vars_dataframe()

    if not df.empty and "speed" in df.columns:
        grouped = df.groupby("Step")["speed"].mean()
        ax.plot(grouped.index, grouped.values, color="blue")
        ax.set_ylim((0, 2))
        ax.set_title("Avg speed of agents per step")
        ax.set_xlabel("Step")
        ax.set_ylabel("Speed")
        ax.grid(True)
        ax.legend()
    else:
        ax.set_title("No data")

    solara.FigureMatplotlib(fig)

def ScatterPlot(model):
    if not model.agents:
        return solara.Markdown("## Ewakuacja zakończona")
    model.step_callback = True
    #property_layers = exits_portrayal(model)
    return make_space_component(agent_portrayal, post_process=post_process(model))(model)
 
def post_process_evplot(model):
    def inner(ax):
        ax.set_ylim(-2, model.number_persons + 2)
        ax.set_xlabel("Step")
        ax.set_ylabel("exited")
        ax.set_title("Number of agents in the room")
        ax.get_figure().set_size_inches(6, 4)
        ax.grid(True)

    return inner

#liczba osób pozostałych na planszy, wykres liniowy
model = Evacuation(80, 20, 10)
EvPlot = make_plot_component("evacuating", post_process=post_process_evplot(model))


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
        "height": 10,
        "door_width":{
        "type": "SliderInt",
        "value": 4,
        "label": "Door width:",
        "min": 2,
        "max": 10,
        "step": 2,
        },
        "p_BNE":{
        "type": "SliderInt",
        "value": 50,
        "label": "Percent of agents BNE:",
        "min": 0,
        "max": 100,
        "step": 1,
        
        },
        "model_type":{
            "type": "Select",
            "value": "BNE_mixed_SR",
            "label": "Model type",
            "values": ["BNE_mixed_SR", "BNE_mixed_RF", "SR", "RF"],

        }
    },
    components=[
        ScatterPlot,
     Heatmap,
    EvPlot,
    SpeedPlot
    ],
    name = "Model Ewakuacji"
)
page
