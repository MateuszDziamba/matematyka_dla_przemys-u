import network
import functions
import random
import numpy as np
from seaborn import heatmap
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import os
from datetime import datetime
import imageio.v2 as imageio


current_directory = os.path.dirname(os.path.abspath(__file__))
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

save_folder = os.path.join(current_directory, 'save')
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

output_folder = os.path.join(save_folder, current_time)
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


num_of_rows = int(3/0.7)
num_of_columns = int(25)
p0,p1,p2,p3,p4,p5 = 0.05,0.1,0.2,0.35,0.2,0.1 #wartości z artykułu #scenariusz 1
# p0,p1,p2,p3,p4,p5 = 0.07,0.1,0.2,0.35,0.2,0.1 #scenariusz 2
# p0,p1,p2,p3,p4,p5 = 0.03,0.1,0.2,0.37,0.2,0.1 #scenariusz 3
# p0,p1,p2,p3,p4,p5 = 0.05,0.12,0.18,0.35,0.18,0.12 #scenariusz 4
# p0,p1,p2,p3,p4,p5 = 0.05,0.08,0.22,0.35,0.22,0.08 #scenariusz 5

net = network.network(num_of_rows,num_of_columns) #stworzenie sieci

#dodanie wyjść na obu krawędziach
for i in range(num_of_rows):
    net.add_exit(i,0,False)
    net.add_exit(i,num_of_columns-1,True)

#rozmieszczenie agentów na planszy
num_of_agents = 200
agents_to_go = num_of_agents
spawned_agents = 0
num_of_steps = 0
agents_positions = []
'''
for i in range(num_of_agents):
    going_right = random.choice([True,False]) #True - idzie w prawo, False - idzie w lewo
    
    #losowanie pozycji agentów jedynie na krawiędziach
    if going_right:
        row = random.randint(0,num_of_rows-1)
        column = 0
    else:
        row = random.randint(0,num_of_rows-1)
        column = num_of_columns-1 
    net.add_agent(row,column,going_right) #dodaie agenta do sieci
    
    #zapisanie pozycji agentów w liście
    index = (row,column,going_right)
    if not index in agents_positions:
        agents_positions.append(index)
    
'''

avg_speed_counter=0
agents_in_exit=[]
speed_vec=[]
simulation=[]
lam = 1.2

# Symulacja ruchu agentów
while agents_to_go > 0:
    num_of_steps += 1
    
    if spawned_agents < num_of_agents: #jeżeli nie ma jeszcze wszystkich agentów w sieci
        for exit in net.exits:
            num_of_new_agents = np.random.poisson(lam) #liczba nowych agentów w danym kroku
            spawned_agents += num_of_new_agents
            if not (exit[0],exit[1],not exit[2]) in agents_positions:
                agents_positions.append((exit[0],exit[1],not exit[2])) #dodanie nowych agentów do listy pozycji
            for _ in range(num_of_new_agents):
                net.add_agent(exit[0],exit[1],not exit[2]) #dodanie nowych agentów do sieci

    speed_per_step=0
    exit_reached=0

    matrix_snapshot=net.matrix[::, ::, 0] + net.matrix[::, ::, 1]
    simulation.append(matrix_snapshot)
    
    new_agents_positions = []
    indexes_to_remove = []
    for index in agents_positions:
        if index in net.exits:
            row = index[0]
            column = index[1]
            going_right = index[2]

            num_of_agents_in_cell_to_exit = int(net.matrix[row][column][int(not going_right)])
            exit_reached += num_of_agents_in_cell_to_exit
            agents_to_go -= num_of_agents_in_cell_to_exit #zmniejszenie liczby agentów w sieci
            # print('Agent dotarł do wyjścia o współrzędnych: ',index)
            '''tu nie wiem jak zdobyc ile agentow jest na wyjściu, a nie jakie pole'''
            net.matrix[index[0]][index[1]][int(not index[2])] = 0
            indexes_to_remove.append(index)
    for index in indexes_to_remove:
        agents_positions.remove(index)
           
        
        
    Possible_collision = [] #przechowuje krotki postaci (r1,c1,r2,c2), gdzie (r1,c1) i (r2,c2) to kolejno pozycja przed i po (potencjalnym) ruchu   
    for index in agents_positions:
        row = index[0]
        column = index[1]
        going_right = index[2]
        
        num_of_agents_in_cell = int(net.matrix[row][column][int(not going_right)])
        for _ in range(num_of_agents_in_cell):
            new_row, new_col = functions.get_new_position(net,row,column,going_right,p0,p1,p2,p3,p4,p5)
            
            #obsługa kolizji takich jak w artykule
            if going_right:
                #w prawo-góra
                if new_row == row-1 and new_col == column+1: 
                    if (row,column+1,new_row,column) in Possible_collision: #kolizja
                        if random.random() < functions.p_avoi(p2,p4,row,column,going_right,net):
                            new_row, new_col = functions.get_random_position(row,column,going_right,p0,p1,p2,p3,p4,p5) #unik
                            if (new_row == row+1 and new_col == column+1) and ((row,column,new_row,new_col) not in Possible_collision): #unik w prawo-dół = potencjalna kolejna kolizja dla innych agentów
                                Possible_collision.append((row,column,new_row,new_col))
                    else: #brak kolizji, ale potencjalnie możliwa dla innego agenta
                        Possible_collision.append((row,column,new_row,new_col))
                #w prawo-dół
                if new_row == row+1 and new_col == column+1:
                    if (row,column+1,new_row,column) in Possible_collision: #kolizja
                        if random.random() < functions.p_avoi(p2,p4,row,column,going_right,net):
                            new_row, new_col = functions.get_random_position(row,column,going_right,p0,p1,p2,p3,p4,p5) #unik
                            if (new_row == row-1 and new_col == column+1) and ((row,column,new_row,new_col) not in Possible_collision): #unik w prawo-góra = potencjalna kolejna kolizja dla innych agentów
                                Possible_collision.append((row,column,new_row,new_col))
                    else: #brak kolizji, ale potencjalnie możliwa dla innego agenta
                        Possible_collision.append((row,column,new_row,new_col))


                #zliczanie średniej prędkości w zależności od ruchu oraz prędkości w czasie
                #idzie prosto lub na boki
                if (new_row==row and new_col==column+1) or (new_row==row-1 and new_col==column) or (new_row==row+1 and new_col==column):
                    avg_speed_counter+=1.4
                    speed_per_step+=1.4
                #idzie po przekątnej
                if (new_row==row+1 and new_col==column+1) or (new_row==row-1 and new_col==column+1):
                    avg_speed_counter+=1.4*np.sqrt(2)
                    speed_per_step+=1.4*np.sqrt(2)
                else:
                    avg_speed_counter+=0
                    speed_per_step+=0

            if not going_right:
                #w lewo-góra
                if new_row == row-1 and new_col == column-1: 
                    if (row,column-1,new_row,column) in Possible_collision: #kolizja
                        if random.random() < functions.p_avoi(p2,p4,row,column,going_right,net):
                            new_row, new_col = functions.get_random_position(row,column,going_right,p0,p1,p2,p3,p4,p5) #unik
                            if (new_row == row+1 and new_col == column-1) and ((row,column,new_row,new_col) not in Possible_collision): #unik w lewo-dół = potencjalna kolejna kolizja dla innych agentów
                                Possible_collision.append((row,column,new_row,new_col))
                    else: #brak kolizji, ale potencjalnie możliwa dla innego agenta
                        Possible_collision.append((row,column,new_row,new_col))
                #w lewo-dół
                if new_row == row+1 and new_col == column-1:
                    if (row,column-1,new_row,column) in Possible_collision: #kolizja
                        if random.random() < functions.p_avoi(p2,p4,row,column,going_right,net):
                            new_row, new_col = functions.get_random_position(row,column,going_right,p0,p1,p2,p3,p4,p5) #unik
                            if (new_row == row-1 and new_col == column-1) and ((row,column,new_row,new_col) not in Possible_collision): #unik w lewo-góra = potencjalna kolejna kolizja dla innych agentów
                                Possible_collision.append((row,column,new_row,new_col))
                    else: #brak kolizji, ale potencjalnie możliwa dla innego agenta
                        Possible_collision.append((row,column,new_row,new_col))


                #zliczanie średniej prędkości w zależności od ruchu
                #idzie prosto lub na boki
                if (new_row==row and new_col==column-1) or (new_row==row-1 and new_col==column) or (new_row==row+1 and new_col==column):
                    avg_speed_counter+=1.4
                    speed_per_step+=1.4
                #idzie po przekątnej
                if (new_row==row+1 and new_col==column-1) or (new_row==row-1 and new_col==column-1):
                    avg_speed_counter+=1.4*np.sqrt(2)
                    speed_per_step+=1.4*np.sqrt(2)
                else:
                    avg_speed_counter+=0
                    speed_per_step+=0

            
            net.add_agent(new_row,new_col,going_right)
            net.matrix[row][column][int(not going_right)] -= 1
            new_index = (new_row,new_col,going_right)
            if not new_index in new_agents_positions: 
                new_agents_positions.append((new_row,new_col,going_right))   
    if np.sum(net.matrix) > 0:
        speed_vec.append(speed_per_step/np.sum(net.matrix))  #śr predkość jednego człowieka per krok  
        agents_in_exit.append(exit_reached)   
    agents_positions = new_agents_positions

#zapis heatmap
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
    

#wykres prędkości
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

#wykres ilości wyjść agentów w zależności od kroku
exit_fig, ax = plt.subplots()
ax.plot(steps, agents_in_exit, 'b.-')
ax.set_xlabel('Steps')
ax.set_title('Number of pedestarians getting out of tunel')
ax.grid()

exit_filename=os.path.join(output_folder, 'exits_of_tunel.png')
plt.savefig(exit_filename)
plt.close(exit_fig)


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