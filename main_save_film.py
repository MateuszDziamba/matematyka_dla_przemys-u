import network
import simulation as sim
import numpy as np
from seaborn import heatmap
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import os
from datetime import datetime
import imageio.v2 as imageio
import animation_and_plots

#sieć na której będzie się odbywała symulacja
num_of_rows = int(3/0.7) #3m to szerokość tunelu, 0.7m to szerokość jednej komórki
num_of_columns = int(25)
net = network.network(num_of_rows,num_of_columns) #stworzenie sieci
#dodanie wyjść na obu krawędziach
for i in range(num_of_rows):
    net.add_exit(i,0,False)
    net.add_exit(i,num_of_columns-1,True)

#parametry do symulacji
num_of_agents = 200
lam = 1.2
p0,p1,p2,p3,p4,p5 = 0.05,0.1,0.2,0.35,0.2,0.1 #wartości z artykułu #scenariusz 1
# p0,p1,p2,p3,p4,p5 = 0.07,0.1,0.2,0.35,0.2,0.1 #scenariusz 2
# p0,p1,p2,p3,p4,p5 = 0.03,0.1,0.2,0.37,0.2,0.1 #scenariusz 3
# p0,p1,p2,p3,p4,p5 = 0.05,0.12,0.18,0.35,0.18,0.12 #scenariusz 4
# p0,p1,p2,p3,p4,p5 = 0.05,0.08,0.22,0.35,0.22,0.08 #scenariusz 5

# Symulacja ruchu agentów
simulation, num_of_steps, agents_in_exit, speed_vec = sim.do_simulation(net, num_of_agents, lam, p0, p1, p2, p3, p4, p5)

#TWORZENIE ANIMACJI I WYKRESÓW
animation_and_plots.do_staff(animation=True, avg_speed=True, num_of_exits=True, simulation=simulation, num_of_steps=num_of_steps, agents_in_exit=agents_in_exit, speed_vec=speed_vec)