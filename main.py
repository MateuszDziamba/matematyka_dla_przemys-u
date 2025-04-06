import network
import functions
import random
import numpy as np
from seaborn import heatmap
import matplotlib.pyplot as plt

num_of_rows = 7
num_of_columns = 7
p0,p1,p2,p3,p4,p5 = 0.05,0.1,0.2,0.35,0.2,0.1 #wartości z artykułu

net = network.network(num_of_rows,num_of_columns) #stworzenie sieci

#dodanie wyjść na obu krawędziach
for i in range(num_of_rows):
    net.add_exit(i,0,False)
    net.add_exit(i,num_of_columns-1,True)

#rozmieszczenie agentów na planszy
num_of_agents = 30
agents_positions = []
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
    
#symulacja ruchu agentów
while len(agents_positions) > 0:
    print(net.matrix[::, ::, 0] + net.matrix[::, ::, 1])
    heatmap(net.matrix[::, ::, 0] + net.matrix[::, ::, 1], annot=True)
    plt.show()
    #print(agents_positions)
    
    new_agents_positions = []
    indexes_to_remove = []
    for index in agents_positions:
        if index in net.exits:
            print('Agent dotarł do wyjścia o współrzędnych: ',index)
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
                
            
            net.add_agent(new_row,new_col,going_right)
            net.matrix[row][column][int(not going_right)] -= 1
            new_index = (new_row,new_col,going_right)
            if not new_index in new_agents_positions: 
                new_agents_positions.append((new_row,new_col,going_right))   
            
    agents_positions = new_agents_positions
    
    #APUD
    
    
        


