from model import Evacuation
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import imageio
import os

model = Evacuation(80, 30, 10)

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


heatmap()
