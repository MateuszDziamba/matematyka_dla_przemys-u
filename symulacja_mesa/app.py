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
import matplotlib.colors as mplc
import matplotlib as mpl


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
        sns.heatmap(agent_counts.T,  cmap="mako_r", annot=True, cbar=True,  norm = mplc.LogNorm(vmin=1, vmax=10))
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
    sns.heatmap(agent_counts.T, cmap="viridis", annot=True, cbar=True, vmin = 0, vmax = 10)
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
        color = "#fa6ed7"
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
                    
        #przeszkody
        for x in range(width):
            for y in range(height):
                if model.obstacles_map[x, y] == 1:
                    ax.plot(x, y, 's', color='black', markersize=300/np.maximum(height, width))
        
    return inner
def ScatterPlot(model):
    if not model.agents:
        return solara.Markdown("## Ewakuacja zakończona")
    model.step_callback = True
    #property_layers = exits_portrayal(model)
    return make_space_component(agent_portrayal, post_process=post_process(model))(model)
 

@solara.component
def SpeedPlot(model):
    update_counter.get()

    fig = Figure(figsize=(model.grid.width//2, model.grid.height//2))
    #fig = Figure(figsize=(model.grid.width//2,model.grid.height//2))
    ax = fig.subplots()

    df = model.datacollector.get_agent_vars_dataframe()

    if not df.empty and "speed" in df.columns:
        grouped = df.groupby("Step")["speed"].mean()
        ax.plot(grouped.index, 1.4*grouped.values, color="blue")
        ax.set_ylim((0, 1.5))
        ax.set_title("Avg speed of agents per step")
        ax.set_xlabel("Step")
        ax.set_ylabel("Speed")
        ax.grid(True)
        ax.legend()
    else:
        ax.set_title("No data")

    solara.FigureMatplotlib(fig)


def post_process_evplot(model):
    def inner(ax):
        ax.set_ylim(-2, model.number_persons + 2)
        ax.set_xlabel("Step")
        ax.set_ylabel("exited")
        ax.set_title("Number of agents in the room")
        ax.get_figure().set_size_inches(6, 4)
        ax.grid(True)

    return inner

@solara.component
def EvPlot(model):
    update_counter.get()

    fig = Figure(figsize=(model.grid.width//2, model.grid.height//2))
    #fig = Figure(figsize=(model.grid.width//2,model.grid.height//2))
    ax = fig.subplots()

    df = model.datacollector.get_model_vars_dataframe()

    if not df.empty and "evacuating" in df.columns:
        step = len(df)
        agent_door = np.zeros(step)
        for i in range(1,step):
            agent_door[i] = - df["evacuating"][i] + df["evacuating"][i-1]
        ax.plot(range(step), agent_door, color="blue")
        ax.set_xlabel("Step")
        ax.set_ylabel("Agent")
        ax.set_title("Number of agents crossing the door")
        #ax.get_figure().set_size_inches(6, 4)
        ax.grid(True)
    else:
        ax.set_title("No data")

    solara.FigureMatplotlib(fig)

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
    ax.set_title("Pedestrians density")
    sns.heatmap(agent_counts.T, cmap="mako_r", annot=True, cbar=True,  norm = mplc.LogNorm(vmin=1, vmax=10), ax=ax)
    ax.invert_yaxis()
    solara.FigureMatplotlib(fig, bbox_inches = 'tight')


#### ładniejszy układ strony (nie nachodzą na siebie przy zmianie rozmiarów) ################
@solara.component
def CombinedPlot(model):
    update_counter.get()
    #with solara.Row(gap='20px'):
    with solara.Card(elevation=5):
        with solara.Columns():
            ScatterPlot(model)
            Heatmap(model) 

    with solara.Card(elevation=1):        
        with solara.Columns():
            EvPlot(model)
            SpeedPlot(model)


model = Evacuation(80, 20, 10)
page = SolaraViz(
    model,
    play_interval=1,
    render_interval=1,
    model_params={
        "n": {
        "type": "SliderInt",
        "value": 80,
        "label": "Number of agents:",
        "min": 10,
        "max": 1000,
        "step": 10,

        },
        "width": {
        "type": "SliderInt",
        "value": 20,
        "label": "Width:",
        "min": 10,
        "max": 50,
        "step": 10,
        },
        "height": {
        "type": "SliderInt",
        "value": 10,
        "label": "Height:",
        "min": 10,
        "max": 30,
        "step": 10,
        },
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
        "value": 100,
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

        },
        "right_door":{
            "type": "Checkbox",
            "value": True,
            "label": "Right door only",
            "description": "Add right door",
        }
    },
    components=
        [CombinedPlot]
    ,
    name = "Model Ewakuacji",
)
