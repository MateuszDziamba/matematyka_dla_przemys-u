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
    #heatmap(net.matrix[::, ::, 0] + net.matrix[::, ::, 1], annot=True)
    #plt.show()
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
        
        num_of_agents_in_cell_going_right = int(net.matrix[row][column][0])
        for _ in range(num_of_agents_in_cell_going_right):
            new_row, new_col = functions.get_new_position(net,row,column,True,p0,p1,p2,p3,p4,p5)
            net.add_agent(new_row,new_col,True)
            net.matrix[row][column][0] -= 1
            #brak obsługi kolizji
            new_index = (new_row,new_col,True)
            if not new_index in new_agents_positions: 
                new_agents_positions.append((new_row,new_col,True))   
        
        num_of_agents_in_cell_going_left = int(net.matrix[row][column][1])
        for _ in range(int(net.matrix[row][column][1])):
            new_row, new_col = functions.get_new_position(net,row,column,False,p0,p1,p2,p3,p4,p5)
            net.add_agent(new_row,new_col,False)
            net.matrix[row][column][1] -= 1
            #brak obsługi kolizji
            new_index = (new_row,new_col,False)
            if not new_index in new_agents_positions: 
                new_agents_positions.append((new_row,new_col,False))
            
    agents_positions = new_agents_positions
    
    
        


