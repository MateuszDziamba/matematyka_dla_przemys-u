from model import Evacuation
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

model = Evacuation(10, 2, 5)
for _ in range(20):
    model.step()

agent_counts = np.zeros((model.grid.width, model.grid.height))
for cell_content, (x, y) in model.grid.coord_iter():
    agent_count = len(cell_content)
    agent_counts[x][y] = agent_count
g = sns.heatmap(agent_counts, cmap="viridis", annot=True, cbar=False, square=True)
plt.show()