import network
import functions
import random
import numpy as np

def do_simulation(net: network.network, num_of_agents: int, lam: float, p0: float, p1: float, p2: float, p3: float, p4: float, p5: float) -> tuple:
    '''
    do_simulation
    Funkcja przeprowadza symulację ruchu agentów w sieci.
    Arguments:
    net -- obiekt klasy network, reprezentujący sieć
    num_of_agents -- łączna liczba agentów, którzy mają zostać dodani do sieci
    lam -- średnia liczba nowych agentów dodawanych (zgodnie z rozkładem Poissona) do każdej komórki będącej wyjściem w każdym kroku
    p0, p1, p2, p3, p4, p5 -- parametry symulacji, tj. prawdopodobieństwa związane z ruchem agentów
    Returns:
    simulation -- lista reprezentująca stan sieci w każdym kroku symulacji
    num_of_steps -- liczba kroków symulacji
    agents_in_exit -- lista przechowująca liczbę agentów, którzy dotarli do wyjścia w każdym kroku symulacji
    speed_vec -- lista przechowująca średnią prędkość agentów w każdym kroku symulacji
    '''
    #zmienne potrzebne do przechowywania wyników symulacji
    agents_to_go = num_of_agents
    spawned_agents = 0
    num_of_steps = 0
    agents_positions = []
    avg_speed_counter = 0
    agents_in_exit = []
    speed_vec = []
    simulation = []
    
    #symulacja
    while agents_to_go > 0:
        
        num_of_steps += 1 #licznik klatek symulacji
        
        #dodanie nowych agentów do sieci jeżli dodanych dotychczas agentów jest mniej niż docelowa liczba num_of_agents
        if spawned_agents < num_of_agents: #jeżeli nie ma jeszcze wszystkich agentów w sieci
            for exit in net.exits:
                num_of_new_agents = np.random.poisson(lam) #liczba nowych agentów w danym kroku
                spawned_agents += num_of_new_agents
                if not (exit[0],exit[1],not exit[2]) in agents_positions:
                    agents_positions.append((exit[0],exit[1],not exit[2])) #dodanie nowych agentów do listy pozycji
                for _ in range(num_of_new_agents):
                    net.add_agent(exit[0],exit[1],not exit[2]) #dodanie nowych agentów do sieci
        
        #zapisanie stanu symulacji
        matrix_snapshot=net.matrix[::, ::, 0] + net.matrix[::, ::, 1]
        simulation.append(matrix_snapshot)
        
        #usunięcie agentów, którzy dotarli do wyjścia
        indexes_to_remove = []
        for index in agents_positions:
            if index in net.exits:
                row = index[0]
                column = index[1]
                going_right = index[2]

                num_of_agents_in_cell_to_exit = int(net.matrix[row][column][int(not going_right)])
                exit_reached += num_of_agents_in_cell_to_exit
                agents_to_go -= num_of_agents_in_cell_to_exit #zmniejszenie liczby agentów w sieci
                net.matrix[index[0]][index[1]][int(not index[2])] = 0
                indexes_to_remove.append(index)
        for index in indexes_to_remove:
            agents_positions.remove(index)
        agents_in_exit.append(exit_reached)   
            
        #wyznaczanie nowych pozycji agentów oraz obsługa kolizji
        speed_per_step = 0 #wykorzystywana przy wyznaczaniu średniej prędkości
        exit_reached = 0 #zmienna pomocnicza do zliczania liczby agentów, którzy dotarli do wyjścia w danym kroku
        Possible_collision = [] #przechowuje krotki postaci (r1,c1,r2,c2), gdzie (r1,c1) i (r2,c2) to kolejno pozycja przed i po (potencjalnym) ruchu   
        new_agents_positions = []
        for index in agents_positions: #przechodzenie po wszystkich agentach w sieci korzystając z listy przechowującej ich pozycje
            
            row = index[0] #aktualny wiersz w którym znajduje się agent
            column = index[1] #aktualna kolumna w której znajduje się agent
            going_right = index[2] #kierunek w którym porusza się agent (True - w prawo, False - w lewo)
            num_of_agents_in_cell = int(net.matrix[row][column][int(not going_right)]) #liczba agentów w na danej pozycji, którzy poruszają się w kierunku zgodnym z going_right (True - w prawo, False - w lewo)
            
            for _ in range(num_of_agents_in_cell): #przechodzenie po wszystkich agentach w danej komórce poruszających się w kierunku going_right (True - w prawo, False - w lewo)
                new_row, new_col = functions.get_new_position(net,row,column,going_right,p0,p1,p2,p3,p4,p5) #nowa pozycja agenta po ruchu - może zostać zmieniona jeśli prowadzi do kolizji
                
                #obsługa kolizji takich jak w artykule oraz wyznaczanie średniej prędkości
                if going_right: #dla ruchu w prawo
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

                if not going_right: #dla ruchu w lewo
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

                net.add_agent(new_row,new_col,going_right) #dodanie agenta do sieci na nowej pozycji
                net.matrix[row][column][int(not going_right)] -= 1 #usunięcie agenta z poprzedniej pozycji w sieci
                new_index = (new_row,new_col,going_right) #nowa pozycja agenta w sieci
                #dodanie nowej pozycji agenta do nowej listy pozycji agentów, jeśli jeszcze jej tam nie ma
                if not new_index in new_agents_positions: 
                    new_agents_positions.append((new_row,new_col,going_right))  
        
        #zapisanie średniej prędkości agentów jeśli sieć nie jest pusta 
        if np.sum(net.matrix) > 0:
            speed_vec.append(speed_per_step/np.sum(net.matrix))  #śr predkość jednego człowieka per krok  
            
        agents_positions = new_agents_positions #aktualizacja pozycji agentów w sieci

    return simulation, num_of_steps, agents_in_exit, speed_vec