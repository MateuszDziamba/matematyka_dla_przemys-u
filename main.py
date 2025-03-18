import network
import functions
import random
import numpy as np

num_of_rows = 11
num_of_columns = 11
p0,p1,p2,p3,p4,p5 = 0.05,0.1,0.2,0.35,0.2,0.1 #wartości z artykułu

net = network.network(num_of_rows,num_of_columns)
net.add_exit(5,10,True)
net.add_exit(6,10,True) #dodanie drugiego wyjścia
net.add_exit(7,0,False) #dodanie trzeciego wyjścia

#rozmieszczenie agentów na planszy
num_of_agents = 10
agents_positions = []
for i in range(num_of_agents):
    row = random.randint(0,num_of_rows-1)
    column = random.randint(0,num_of_columns-1)
    going_right = random.choice([True,False])
    net.add_agent(row,column,going_right) #True - idzie w prawo, False - idzie w lewo
    
    index = (row,column,going_right)
    if not index in agents_positions:
        agents_positions.append(index)
    
#symulacja ruchu agentów
while len(agents_positions) > 0:
    new_agents_positions = []
    
    indexes_to_remove = []
    for index in agents_positions:
        if index in net.exits:
            print('Agent dotarł do wyjścia o współrzędnych: ',index)
            net.matrix[index[0]][index[1]][int(not index[2])] = 0
            indexes_to_remove.append(index)
    for index in indexes_to_remove:
        agents_positions.remove(index)
        
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
    print(net.matrix[::, ::, 0])
    #print(agents_positions)
    
        


