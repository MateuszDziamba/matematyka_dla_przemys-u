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