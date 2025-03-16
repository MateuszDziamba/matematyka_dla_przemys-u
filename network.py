import numpy as np

class network:
    
    def __init__(self, num_of_rows: int,num_of_columns: int):
        self.num_of_rows = num_of_rows
        self.num_of_columns = num_of_columns
        self.matrix = np.zeros((num_of_rows,num_of_columns,2)) #network[row][col][0] - idzie w prawo, network[row][col][1] - idzie w lewo
        self.exits = []
    
    def add_agent(self, row: int, column: int, going_right: bool):
        if row < 0 or row >= self.num_of_rows or column < 0 or column >= self.num_of_columns:
            raise ValueError('Index out of range')
        if going_right:
            self.matrix[row][column][0] += 1 #każda wartość w macierzy odpowiada liczbie agentów na danym polu idących w prawo
        if not going_right:
            self.matrix[row][column][1] += 1 #każda wartość w macierzy odpowiada liczbie agentów na danym polu idących w lewo
    
    def add_exit(self, row: int, column: int, going_right: bool):
        if row < 0 or row >= self.num_of_rows or column < 0 or column >= self.num_of_columns:
            raise ValueError('Index out of range')
        self.exits.append((row,column,going_right)) #możliwość dodania wielu wyjść, lub powiększania ich
    
    