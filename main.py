import network
import random
import numpy as np

num_of_rows = 11
num_of_columns = 11

net = network.network(num_of_rows,num_of_columns)
net.add_exit(5,10,True)
#net.add_exit(5,0,False) #dodanie drugiego wyjścia

#rozmieszczenie agentów na planszy
num_of_agents = 10
agents_positions = []
for i in range(num_of_agents):
    row = random.randint(0,num_of_rows-1)
    column = random.randint(0,num_of_columns-1)
    net.add_agent(row,column,True) #True - idzie w prawo, False - idzie w lewo, na razie tylko w prawo
    
    is_index_in_list = False
    for index in agents_positions:
        if index == (row,column):
            is_index_in_list = True
            break
    if not is_index_in_list:
        agents_positions.append((row,column))
    
#symulacja ruchu agentów
while len(agents_positions) > 0:
    new_agents_positions = []
    for index in agents_positions:
        row = index[0]
        column = index[1]
        
        if (row,column) in net.exits:
            agents_positions.remove((row,column))
            continue
        
        for i in range(net.matrix[row][column][0]):
            continue
        for i in range(net.matrix[row][column][1]):
            continue
    agents_positions = new_agents_positions
        
print(net.matrix)
print(agents_positions)

