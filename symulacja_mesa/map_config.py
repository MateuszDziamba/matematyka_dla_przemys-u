import numpy as np

class ObstacleMap:
    def __init__(self, height: int, width: int, door_width: int, door_position: list):
        self.height = height
        self.width = width
        self.door_width = door_width
        self.door_position = door_position

    def get_map(self, map_type: str) -> list:
        self.obstacles_map = np.zeros((self.width, self.height))
        if map_type == 'empty':
            return self.obstacles_map
        
        elif map_type == 'two_blocks':
            for i in range(self.width//2, self.width-2):
                for j in range(self.height//2 - 3):
                    self.obstacles_map[i,self.height - 3 - j] = 1
                    self.obstacles_map[i, j + 2] = 1
            return self.obstacles_map
        
        elif map_type == 'snake':
            for i in range(self.width//6):
                for j in range(self.height - 2):
                    self.obstacles_map[self.width//2 + i, j] = 1
                    self.obstacles_map[3*self.width//4 + i, j + 2] = 1
            return self.obstacles_map
        
        elif map_type == 'random_squares':
            num_of_squares = self.width * self.height // 40
            for _ in range(num_of_squares):
                x = np.random.randint(1, self.width-2)
                y = np.random.randint(0, self.height-1)
                for i in (0,1):
                    for j in (0,1):
                        if x + i < self.width and y + j < self.height:
                            self.obstacles_map[x + i, y + j] = 1
            return self.obstacles_map
        
        elif map_type == 'classroom':
            #tutaj już ustalone width = 16, height=20
            self.obstacles_map = np.array([
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # biurko
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # biurko
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ]).T

            return self.obstacles_map

        
        #---------mapa_wymagająca_cofania------------------
        #for i in range(1,self.grid.height-1):
        #    self.obstacles_map[1, i] = 1
        #    Obstacle(self, 1, i)
            
        #for i in range(self.grid.width//2, self.grid.width):
        #    self.obstacles_map[i,self.grid.height//2 - (self.door_width//2) - 1] = 1
        #    self.obstacles_map[i,self.grid.height//2 + (self.door_width//2)] = 1
        #    Obstacle(self, i, self.grid.height//2 - (self.door_width//2) - 1)
        #    Obstacle(self, i, self.grid.height//2 + (self.door_width//2))
        #--------------------------------------------------

class Spawn:
    def __init__(self,height: int, width: int):
        self.height = height
        self.width = width
    def get_spawn_positions(self, obstacles_map: list, spawn_position: str) -> list:
        import numpy as np
        self.spawn_positions = np.zeros((self.width, self.height))
        if spawn_position == 'all_map':
            pass
        elif spawn_position == 'left_half':
            for i in range(self.width//2, self.width):
                for j in range(self.height):
                    self.spawn_positions[i][j] = 1
        elif spawn_position == 'left_quarter':
            for i in range(self.width//4, self.width):
                for j in range(self.height):
                    self.spawn_positions[i][j] = 1
        elif spawn_position == 'classroom':
            import numpy as np
            modified_obstacles_map = np.array([
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # ławka
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # ławka
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1], #ławka Ślęzaka
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # ławka
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], #między biurkiem a 1 ławką
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # biurko
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # biurko
                [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            ]).T
            self.spawn_positions = modified_obstacles_map
        
        if spawn_position!='classroom':
            for i in range(self.width):
                for j in range(self.height):
                    self.spawn_positions[i][j] = self.spawn_positions[i][j] or obstacles_map[i][j]
            
        return self.spawn_positions
        