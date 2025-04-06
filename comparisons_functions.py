import simulation as sim
import network
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime



def do_staff(density=True, lam_vec=[], N=0, num_of_rows=0, num_of_columns=0, num_of_agents=0, p0=0, p1=0, p2=0, p3=0, p4=0, p5=0, net=network):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    save_folder = os.path.join(current_directory, 'save_comparisons')
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    output_folder = os.path.join(save_folder, current_time)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


    if density:
        avg_max_num_agents_lam=[] #średnia maksymalna ilość agentów w symulacji w zależności od lambdy

        for lam in lam_vec:
            max_in_sim_lam=[] #lista przechowuje maxy dla jednej z lambd
            for _ in range(N):
                simulation, _,_,_ = sim.do_simulation(net, num_of_agents, lam, p0, p1, p2, p3, p4, p5)
                frame_agents=[np.sum(frame) for frame in simulation]
                max_in_sim_lam.append(max(frame_agents))
            avg_max_num_agents_lam.append(np.mean(max_in_sim_lam)) #zliczamy średni max agentów z listy z daną lambdą

        max_cells=num_of_columns*num_of_rows
        density=[num_agents/(0.49*max_cells) for num_agents in avg_max_num_agents_lam] #uśredniamy denisty do m2, bo 1 komórka ma 0.49m2

        density_fig, ax = plt.subplots()
        ax.plot(lam_vec, density, marker='.')
        ax.set_xlabel('Pedestarian Flow [Ped/s]')
        ax.set_ylabel('Max Reached Density [Ped/$m^2$]')
        ax.set_title(f'''Pedestarians` Density over the Pedestarian Flow Rate, \nparams: N={num_of_agents}, tunnel: {num_of_rows}x{num_of_columns}m''')
        ax.grid()

        density_filename=os.path.join(output_folder, 'density.png')
        plt.savefig(density_filename)
        plt.close(density_fig)
        print(f"Done: density")