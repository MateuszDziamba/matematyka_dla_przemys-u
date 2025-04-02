import numpy as np
from seaborn import heatmap
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import os
from datetime import datetime
import imageio.v2 as imageio

def do_staff(animation = True, avg_speed = True, num_of_exits = True, simulation = [], num_of_steps = 0, agents_in_exit = 0, speed_vec = 0):
    '''
    Tworzy animację i wykresy na podstawie podanych danych i zapisuje je w odpowiednich folderach.
    '''
    current_directory = os.path.dirname(os.path.abspath(__file__))
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    save_folder = os.path.join(current_directory, 'save')
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    output_folder = os.path.join(save_folder, current_time)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


    if animation:
        num_of_columns = simulation[0].shape[1]
        num_of_rows = simulation[0].shape[0]
        
        current_max_num_of_agent=np.max(simulation)
        fig_width = num_of_columns *1
        fig_height = num_of_rows *1.5

        for i, matrix_snapshot in enumerate(simulation):
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            heatmap(matrix_snapshot, annot=True, ax=ax, vmin=0, vmax=current_max_num_of_agent)
            ax.set_title('Pedestarian flow')
            ax.set_xlabel('Step')
            ax.set_ylabel('Number of exits')
            
            image_filename = os.path.join(output_folder, f"frame_{i:03d}.png")
            plt.savefig(image_filename)
            plt.close(fig)
            
        #gif
        gif_filename = os.path.join(output_folder, "film.gif")
        frames = []
        for filename in sorted(os.listdir(output_folder)):
            if filename.endswith(".png") and filename.startswith("frame_"):
                img_path = os.path.join(output_folder, filename)
                frames.append(imageio.imread(img_path))

        imageio.mimsave(gif_filename, frames, fps=4, loop=0)
        relative_gif_path = os.path.relpath(gif_filename, current_directory)
        print(f"GIF saved as: {relative_gif_path}")
        

    if avg_speed:
        avg_speed=np.average(speed_vec) # średnia prędkość w całym ruchu, ruchów jest o 1 mniej niż kolumn 
        steps=np.linspace(1,len(speed_vec),len(speed_vec))
        velocity_fig, ax = plt.subplots()
        ax.plot(steps, speed_vec, label='AVG speed') # usuwam ostatnią obserwację bo jest 0
        ax.plot(steps, [avg_speed]*len(steps), 'r--', label='VPF') #vpf = velocity of pedestarian flow
        ax.set_xlabel('Steps')
        ax.set_ylabel('Velocity [m/s]')
        ax.set_title('Velocity of pedestarian flow over time')
        ax.legend()
        ax.grid()

        velocity_filename=os.path.join(output_folder, 'velocity.png')
        plt.savefig(velocity_filename)
        plt.close(velocity_fig)
        print(f"VPF: {avg_speed}")

    if num_of_exits:
        steps=np.linspace(1,num_of_steps,num_of_steps)
        exit_fig, ax = plt.subplots()
        ax.plot(steps, agents_in_exit, 'b.-')
        ax.set_xlabel('Steps')
        ax.set_title('Number of pedestarians getting out of tunel')
        ax.grid()

        exit_filename=os.path.join(output_folder, 'exits_of_tunel.png')
        plt.savefig(exit_filename)
        plt.close(exit_fig)

def do_animation(simulation: list):
    '''
    Tworzy animację na podstawie podanej symulacji i zapisuje ją jako GIF.
    '''
    current_directory = os.path.dirname(os.path.abspath(__file__))
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    save_folder = os.path.join(current_directory, 'save')
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    output_folder = os.path.join(save_folder, current_time)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    num_of_columns = simulation[0].shape[1]
    num_of_rows = simulation[0].shape[0]
    
    current_max_num_of_agent=np.max(simulation)
    fig_width = num_of_columns *1
    fig_height = num_of_rows *1.5

    for i, matrix_snapshot in enumerate(simulation):
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        heatmap(matrix_snapshot, annot=True, ax=ax, vmin=0, vmax=current_max_num_of_agent)
        ax.set_title('Pedestarian flow')
        ax.set_xlabel('Step')
        ax.set_ylabel('Number of exits')
        
        image_filename = os.path.join(output_folder, f"frame_{i:03d}.png")
        plt.savefig(image_filename)
        plt.close(fig)
        
    #gif
    gif_filename = os.path.join(output_folder, "film.gif")
    frames = []
    for filename in sorted(os.listdir(output_folder)):
        if filename.endswith(".png") and filename.startswith("frame_"):
            img_path = os.path.join(output_folder, filename)
            frames.append(imageio.imread(img_path))

    imageio.mimsave(gif_filename, frames, fps=4, loop=0)
    relative_gif_path = os.path.relpath(gif_filename, current_directory)
    print(f"GIF saved as: {relative_gif_path}")
    
def do_avg_speed_plot(num_of_steps: int, speed_vec: int):
    '''
    Tworzy wykres prędkości na podstawie podanych danych i zapisuje go jako PNG.
    '''
    current_directory = os.path.dirname(os.path.abspath(__file__))
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    save_folder = os.path.join(current_directory, 'save')
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    output_folder = os.path.join(save_folder, current_time)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    avg_speed=np.average(speed_vec) # średnia prędkość w całym ruchu, ruchów jest o 1 mniej niż kolumn 
    steps=np.linspace(1,num_of_steps-1,num_of_steps-1)
    velocity_fig, ax = plt.subplots()
    ax.plot(steps, speed_vec, label='AVG speed') # usuwam ostatnią obserwację bo jest 0
    ax.plot(steps, [avg_speed]*len(steps), 'r--', label='VPF') #vpf = velocity of pedestarian flow
    ax.set_xlabel('Steps')
    ax.set_ylabel('Velocity [m/s]')
    ax.set_title('Velocity of pedestarian flow over time')
    ax.legend()
    ax.grid()

    velocity_filename=os.path.join(output_folder, 'velocity.png')
    plt.savefig(velocity_filename)
    plt.close(velocity_fig)
    print(f"VPF: {avg_speed}")
    
def do_num_of_exits_plot(agents_in_exit: int, num_of_steps: int):
    '''
    Tworzy wykres ilości wyjść agentów w zależności od kroku i zapisuje go jako PNG.
    '''
    current_directory = os.path.dirname(os.path.abspath(__file__))
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    save_folder = os.path.join(current_directory, 'save')
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    output_folder = os.path.join(save_folder, current_time)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    steps=np.linspace(1,num_of_steps,num_of_steps)
    exit_fig, ax = plt.subplots()
    ax.plot(steps, agents_in_exit, 'b.-')
    ax.set_xlabel('Steps')
    ax.set_title('Number of pedestarians getting out of tunel')
    ax.grid()

    exit_filename=os.path.join(output_folder, 'exits_of_tunel.png')
    plt.savefig(exit_filename)
    plt.close(exit_fig)
