import network
import numpy as np
import random
import math

def cosine_between_vectors(v1, v2):
    # Rozpakowanie współrzędnych
    a, b = v1
    x, y = v2
    
    # Obliczenie iloczynu skalarnego
    dot_product = a * x + b * y
    
    # Obliczenie długości wektorów
    magnitude_v1 = math.sqrt(a ** 2 + b ** 2)
    magnitude_v2 = math.sqrt(x ** 2 + y ** 2)
    
    # Zabezpieczenie przed dzieleniem przez zero
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        raise ValueError("Jeden z wektorów ma zerową długość.")
    
    # Obliczenie cosinusa kąta
    cosine = dot_product / (magnitude_v1 * magnitude_v2)
    
    return cosine

def p_avoi(p2: float,p4: float,row: int,col: int,going_right: bool,net: network.network) -> float:
    """Oblicza wartość p_avoi z artykułu

    Args:
        p2 (float): jak w artykule
        p4 (float): jak w artykule
        row (int): wiersz na którym znajduje się analizowany agent
        col (int): kolumna na której znajduje się analizowany agent
        going_right (bool): kierunek w którym porusza się agent

    Returns:
        float: wartość p_avoi
    """
    if going_right:
        n = net.matrix[row][col+1][1]
    else:
        n = net.matrix[row][col-1][0]
        
    p = (p2+p4)/2 #przyjmuję, że p2=p4, bo tak jest w artykule. Jeśli ktoś to zmieni to funkcja będzie nadal działać, ale inaczej niż w artykule bo nie chce mi się robić tego na razie implementować
    p_avoi = 1 - (1-p)**n
    
    return p_avoi

def get_random_position(row: int, col: int, going_right: bool,
                     p0: float, p1: float, p2: float, p3: float, p4: float, p5: float) -> tuple:
    """
    Losowe wybranie nowej pozycji agenta na planszy
    """
    P = [p0,p1,p2,p3,p4,p5]
    random_number = random.random()
    controll_number = 0
    for i in range(6):
        controll_number += P[i]
        if random_number < controll_number:
            break
    if going_right:
        if i == 0:
            return int(row),int(col)
        if i == 1:
            return int(row-1), int(col)
        if i == 2:
            return int(row-1), int(col+1)
        if i == 3:
            return int(row), int(col+1)
        if i == 4:
            return int(row+1), int(col+1)
        if i == 5:
            return int(row+1), int(col)
    if not going_right:
        if i == 0:
            return int(row),int(col)
        if i == 1:
            return int(row+1), int(col)
        if i == 2:
            return int(row+1), int(col-1)
        if i == 3:
            return int(row), int(col-1)
        if i == 4:
            return int(row-1), int(col-1)
        if i == 5:
            return int(row-1), int(col)
        

def calculate_g_values(net: network.network, row: int, col: int, index: int, going_right: bool) -> tuple:
    """Oblicza wartości g_i tak jak w artykule

    Args:
        net (network.network): sieć na której odbywa się symulacja
        row (int): wiersz na którym znajduje się analizowany agent
        col (int): kolumna na której znajduje się analizowany agent
        index (int): indeks komórki (z konwencji oznaczeń prawdopodobieństw) dla której liczone są wartości g
    Returns:
        tuple: wartości g_i
    """
    if going_right:
        if index == 0:
            r,c = row, col
        if index == 1:
            r,c = row - 1, col
        if index == 2:
            r,c = row-1, col+1
        if index == 3:
            r,c = row, col + 1
        if index == 4:
            r,c = row + 1, col + 1
        if index == 5:
            r,c = row + 1, col
    if not going_right:
        if index == 0:
            r,c = row, col
        if index == 1:
            r,c = row + 1, col
        if index == 2:
            r,c = row+1, col-1
        if index == 3:
            r,c = row, col - 1
        if index == 4:
            r,c = row - 1, col - 1
        if index == 5:
            r,c = row - 1, col
    
    g0 = net.matrix[r][c][0] + net.matrix[r][c][1]
    g1,g2,g3,g4,g5 = 0,0,0,0,0
    #try-excepty obsługują brzeg planszy, nie chce mi się tego rozbijać na milion przypadków
    try:
        g1 += net.matrix[r+1][c][0] 
    except:
        g1 += 0
    try:
        g1 += net.matrix[r-1][c][1]
    except:
        g1 += 0
        
    try:
        g2 += net.matrix[r+1][c-1][0] 
    except:
        g2 += 0
    try:
        g2 += net.matrix[r-1][c+1][1]
    except:
        g2 += 0
        
    try:
        g3 += net.matrix[r][c-1][0] 
    except:
        g3 += 0
    try:
        g3 += + net.matrix[r][c+1][1] 
    except:
        g3 += 0
    g3 -= 1
    
        
    try:
        g4 += net.matrix[r-1][c-1][0] 
    except:
        g4 += 0
    try:
        g4 += net.matrix[r+1][c+1][1]
    except:
        g4 += 0
        
    try:
        g5 += net.matrix[r-1][c][0]
    except:
        g5 += 0
    try:
        g5 += net.matrix[r+1][c][1]
    except:
        g5 += 0
    
    return g0, g1, g2, g3, g4, g5


def mi_comf(n: int) -> float:
    """Implementacja mi_comf z artykułu

    Args:
        n (int): liczba agentów w komórce

    Returns:
        float: poziom komfortu
    """
    if n <= 2:
        return 1.0
    elif n == 0:
        return 0.52
    else:
        return 0.07
    

def ksi_comf(p0: float, p1: float, p2: float, p3: float, p4: float, p5: float,
             g0: float, g1: float, g2: float, g3: float, g4: float, g5: float):
    """Wprost implementuje sposób obliczania ksi_comf przedstawiony w artykule
    Args:
        p0 (float): jak w artykule
        p1 (float): jak w artykule
        p2 (float): jak w artykule
        p3 (float): jak w artykule
        p4 (float): jak w artykule
        p5 (float): jak w artykule
        g0 (float): jak w artykule
        g1 (float): jak w artykule
        g2 (float): jak w artykule
        g3 (float): jak w artykule
        g4 (float): jak w artykule
        g5 (float): jak w artykule

    Returns:
        ksi_comf (float): wartość oczekiwana komfortu w danej komórce
    """
    
    P = [p0,p1,p2,p3,p4,p5]
    G = [g0,g1,g2,g3,g4,g5]
    
    P_0 = 1
    for i in range(6):
        P_0 *= (1-P[i])**G[i]
        
    P_1 = 0
    for i in range(6):
        P_1 += G[i]*P[i]*P_0/(1-P[i])
        
    P_2 = 1
    for i in range(6):
       P_2 += G[i]*(G[i]-1)*(P[i]**2)*P_0/(2*((1-P[i])**2))
        
    for j in range(5):
        for i in range(j+1,6):
            P_2 += G[j]*G[i]*P[j]*P[i]*P_0/((1-P[j])*(1-P[i]))
    
    return mi_comf(1)*P_0 + mi_comf(2)*P_1 + mi_comf(3)*P_2 + mi_comf(4)*(1-P_0-P_1-P_2)


def get_new_position(net: network.network, row: int, col: int, going_right: bool,
                     p0: float, p1: float, p2: float, p3: float, p4: float, p5: float) -> tuple:
    """
    Funkcja zwraca nową pozycję agenta na planszy
    """
    
    utilty_map = np.zeros(6) #numeracja taka sama jak dla prawdopodobieństw z artykułu
    
    if going_right:
        exit_distance = np.sqrt(net.num_of_rows**2 + net.num_of_columns**2)
        for exit in net.exits:
                if exit[2] == True:
                    distance = np.sqrt((exit[0]-row)**2 + (exit[1]-col)**2)
                    if distance <= exit_distance:
                        exit_distance = distance
                        exit_row = exit[0]
                        exit_col = exit[1]
                    
        exit_vect = [exit_row-row,exit_col-col]
        s = 1 #dystans wszędzie (czyli do ruchów po przekątnej również) przyjąłem 1, można zmienić i zobaczyć co się stanie
        
        for i in range(6):
            #obsługa brzegu planszy
            if row == 0 and (i == 1 or i == 2):
                continue
            if row == net.num_of_rows-1 and (i == 4 or i == 5):
                continue
            if col == net.num_of_columns-1 and (i==2 or i == 3 or i == 4):
                continue
            
            mi_move = 0
            g0,g1,g2,g3,g4,g5 = calculate_g_values(net,row,col,i,going_right)
            
            #zakometnowane podejście jest bardziej ogólne, ale ma błędy zaokrągleń
            if i == 1:
                v = [-1,0]
                #mi_move += s * cosine_between_vectors(v,exit_vect)
                mi_move += 0
            if i == 2:
                v = [-1,1]
                #mi_move += s * cosine_between_vectors(v,exit_vect)
                mi_move += 1
            if i == 3:
                v = [0,1]
                #mi_move += s * cosine_between_vectors(v,exit_vect)
                mi_move += 1
            if i == 4:
                v = [1,1]
                #mi_move += s * cosine_between_vectors(v,exit_vect)
                mi_move += 1
            if i == 5:
                v = [1,0]
                #mi_move += s * cosine_between_vectors(v,exit_vect)
                mi_move += 0
            
            utilty_map[i] = mi_move + ksi_comf(p0,p1,p2,p3,p4,p5,g0,g1,g2,g3,g4,g5)
            
        best_index = utilty_map.argmax()
            
        if best_index == 0:
            return int(row),int(col)
        if best_index == 1:
            return int(row-1), int(col)
        if best_index == 2:
            return int(row-1), int(col+1)
        if best_index == 3:
            return int(row), int(col+1)
        if best_index == 4:
            return int(row+1), int(col+1)
        if best_index == 5:
            return int(row+1), int(col)
        
    if not going_right:
        exit_distance = np.sqrt(net.num_of_rows**2 + net.num_of_columns**2)
        for exit in net.exits:
                if exit[2] == False:
                    distance = np.sqrt((exit[0]-row)**2 + (exit[1]-col)**2)
                    if distance <= exit_distance:
                        exit_distance = distance
                        exit_row = exit[0]
                        exit_col = exit[1]
        
        exit_vect = [exit_row-row,exit_col-col]
        s = 1 #dystans wszędzie (czyli do ruchów po przekątnej również) przyjąłem 1, można zmienić i zobaczyć co się stanie
        
        for i in range(6):
            #obsługa brzegu planszy
            if row == 0 and (i == 4 or i == 5):
                continue
            if row == net.num_of_rows-1 and (i == 1 or i == 2):
                continue
            if col == 0 and (i==2 or i == 3 or i == 4):
                continue
            
            mi_move = 0
            g0,g1,g2,g3,g4,g5 = calculate_g_values(net,row,col,i,going_right)
            
            if i == 1:
                v = [1,0]
                #mi_move += s * cosine_between_vectors(v,exit_vect)
                mi_move += 0
            if i == 2:
                v = [1,-1]
                #mi_move += s * cosine_between_vectors(v,exit_vect)
                mi_move += 1
            if i == 3:
                v = [0,-1]
                #mi_move += s * cosine_between_vectors(v,exit_vect)
                mi_move += 1
            if i == 4:
                v = [-1,-1]
                #mi_move += s * cosine_between_vectors(v,exit_vect)
                mi_move += 1
            if i == 5:
                v = [-1,0]
                #mi_move += s * cosine_between_vectors(v,exit_vect)
                mi_move += 1
            
            utilty_map[i] = mi_move + ksi_comf(p0,p1,p2,p3,p4,p5,g0,g1,g2,g3,g4,g5)
            
        best_index = utilty_map.argmax()
            
        if best_index == 0:
            return int(row),int(col)
        if best_index == 1:
            return int(row+1), int(col)
        if best_index == 2:
            return int(row+1), int(col-1)
        if best_index == 3:
            return int(row), int(col-1)
        if best_index == 4:
            return int(row-1), int(col-1)
        if best_index == 5:
            return int(row-1), int(col)
