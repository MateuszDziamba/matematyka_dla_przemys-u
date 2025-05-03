"""
Mesa: Agent-based modelling in Python
dokumentacja: https://mesa.readthedocs.io/latest/

==================
Model ewakuacji
==================
Podstawowe założenia:
- siatka prostokątna z kwadratowymi komórkami
- dopuszczamy wielu agentów w jednym polu
- możliwe schematy poruszania agentów (moving_pattern): BNE, SR, RF, mixed

Pliki:
- model.py definiujemy model tj. rodzaj środowiska (mesa.space),
przebieg symulacji oraz zbieranie danych z jej przebiegu
- agents.py definiujemy agentów i różne schematy poruszania
- app.py ustawiamy parametry modelu, inicjalizujemy model i przeprowadzamy symulację
z wizualizacją, dodajemy wykresy na żywo, suwaki itp.
"""
import mesa
from agents import Pedestrian
from agents import Obstacle
import random
import math
import heapq
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Evacuation(mesa.Model):
    def __init__(self, n=10, width=20, height=10, door_width = 4, seed=None, model_type = "BNE_mixed_SR", p_BNE = 100):
        super().__init__(seed=seed)
        self.patch_data = {}
        self.number_persons = n
        #przestrzeń MultiGrid dopuszcza kilku agentów w jednym polu
        #argument False oznacza torus=False
        self.grid = mesa.space.MultiGrid(width, height, False)
        
        self.moving_pattern = model_type
        
        #przeszkody
        self.obstacles_map = np.zeros((self.grid.width, self.grid.height))
        for i in range(1,self.grid.height-1):
            self.obstacles_map[1, i] = 1
            Obstacle(self, 1, i)
            
        for i in range(self.grid.width//2, self.grid.width):
            self.obstacles_map[i,3*(self.grid.height//4)] = 1
            self.obstacles_map[i,self.grid.height//4 - 1] = 1
            Obstacle(self, i, 3*(self.grid.height//4 ))
            Obstacle(self, i, self.grid.height//4 - 1)
    
        #exits
        self.door_width = door_width
        self.exit_width = None
        self.exits = {''
        #x  #ys - wysokosc drzwi - na razie ręcznie, można dodać suwak, przy parzystych wychodzi +1 szerokość (ze środkiem)
        # Zmieniłam bez +1, bo przy parzystej wysokości wyjściowej nie wychodziło równo
        'left': [0, [self.grid.height//2 + i for i in range(-(self.door_width//2), (self.door_width//2) )] ],
        'right': [self.grid.width-1,  [self.grid.height//2 + i for i in range(-(self.door_width//2), (self.door_width//2))]]}

        #poruszanie agentów
        self.move_speed = 1
        self.step_length = None
        self.probability_competing = 1/6
        self.percentage_of_BNE = p_BNE/100
        self.weight_Ud = 1.0

        self.datacollector = mesa.DataCollector(
            model_reporters={"evacuating": self.compute_agents},
            agent_reporters={"speed": "speed"}
        )


        #tworzenie agentów
        agents = Pedestrian.create_agents(model=self, n=n)
        #ustawienie agentów - losujemy współrzędne dla każdego
        Xs = self.rng.integers(0, self.grid.width, size = (n,))
        Ys = self.rng.integers(0, self.grid.height, size = (n,))
        
        self.calculate_distance_utility()
        for a, i, j in zip(agents, Xs, Ys):
            a.pos = (i,j)
            a.prepare_agent()
            self.grid.place_agent(a, (i,j))


        #ustawienie typu agenta jeśli jest model mieszany
        if self.moving_pattern == "BNE_mixed_SR" or self.moving_pattern == "BNE_mixed_RF":
            BNE_agents = self.random.sample(list(self.agents), int(self.percentage_of_BNE*n))
            for agent in BNE_agents:
                agent.BNE_type = True
            
        self.running = True
        self.datacollector.collect(self)
        self.calculate_distance_utility()
        self.calculate_expected_comfort()
        
    
    def add_obstacle(self, x, y):
        if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
            #sprawdzamy czy nie ma już przeszkody w danym polu
            if self.obstacles_map[x, y] == 0:
                #jeśli nie ma to dodajemy przeszkodę
                self.obstacles_map[x, y] = 1
                
        else:
            print("Invalid coordinates for obstacle:", x, y)

    def compute_agents(self):
        if len(self.agents.get("exited"))>0:
            return len(self.agents.get("exited"))
        else:
            self.running=False

    def step(self):
                
        self.datacollector.collect(self)
        #funkcja shuffle_do miesza listę agentów i wykonuje podaną funkcję
        self.agents.shuffle_do("decide")
        self.calculate_expected_comfort()
        self.calculate_distance_utility()


    # def clean(self):
    #     for a in self.agents:
    #         if a.exited:
    #             self.grid.remove_agent(a)
                
    def calculate_distance_utility(self):
    
        width, height = self.grid.width, self.grid.height
        diagonal = math.hypot(width, height)

        # Koszty ruchu: 8 kierunków (Moore)
        directions = [
            (-1,  0, 1), (1,  0, 1),   # góra/dół
            (0, -1, 1), (0,  1, 1),   # lewo/prawo
            (-1, -1, math.sqrt(2)), (1, -1, math.sqrt(2)),  # ukośne
            (-1,  1, math.sqrt(2)), (1,  1, math.sqrt(2))
        ]
        test_map = np.zeros((width, height))

        def dijkstra(start_positions):
            """Zwraca mapę odległości z Dijkstrą z ruchem ukośnym."""
            distance = np.full((width, height), np.inf)
            visited = np.full((width, height), False)
            queue = []

            for x, y in start_positions:
                if self.obstacles_map[x, y] == 0:
                    distance[x, y] = 0
                    heapq.heappush(queue, (0, x, y))

            while queue:
                dist, x, y = heapq.heappop(queue)

                if visited[x, y]:
                    continue
                visited[x, y] = True

                for dx, dy, cost in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if self.obstacles_map[nx, ny] == 0 and not visited[nx, ny]:
                            new_dist = dist + cost
                            if new_dist < distance[nx, ny]:
                                distance[nx, ny] = new_dist
                                heapq.heappush(queue, (new_dist, nx, ny))

            return distance

        # Lista pozycji drzwi
        left_door_positions = [(self.exits['left'][0], y) for y in self.exits['left'][1]]
        right_door_positions = [(self.exits['right'][0], y) for y in self.exits['right'][1]]

        # Oblicz odległości
        dist_to_left = dijkstra(left_door_positions)
        dist_to_right = dijkstra(right_door_positions)

        # Przelicz użyteczność
        for x in range(width):
            for y in range(height):
                #zablokowanie pól z przeszkodami 
                if self.obstacles_map[x, y] == 1:
                    Ud_lt = -100*self.weight_Ud
                    Ud_rt = -100*self.weight_Ud
                    
                    self.patch_data[(x, y)] = {
                        **self.patch_data.get((x, y), {}),
                        "Ud_lt": Ud_lt,
                        "Ud_rt": Ud_rt
                    }
                    test_map[x][y] = -1*self.weight_Ud
                else:
                    D_lt = dist_to_left[x, y]
                    D_rt = dist_to_right[x, y]

                    Ud_lt = (1 - (D_lt / diagonal)) * self.weight_Ud if not np.isinf(D_lt) else 0
                    Ud_rt = (1 - (D_rt / diagonal)) * self.weight_Ud if not np.isinf(D_rt) else 0

                    self.patch_data[(x, y)] = {
                        **self.patch_data.get((x, y), {}),
                        "Ud_lt": Ud_lt,
                        "Ud_rt": Ud_rt
                    }
                    test_map[x][y] = Ud_rt
        
        plt.clf()
        plt.figure(figsize=(20, 20))
        sns.heatmap(data=test_map, annot=True)
        plt.savefig('uzytecznosc.png')
    
    def calculate_expected_comfort(self):
        Pm = self.probability_competing

        for _, (x, y) in self.grid.coord_iter():
            if self.obstacles_map[x, y] == 1:
                continue
            neighbors = self.grid.get_neighbors((x, y), moore=True, include_center=False)
            for neighbor in neighbors:
                if isinstance(neighbor, Obstacle):
                    neighbors.remove(neighbor)
            num_here = len(self.grid.get_cell_list_contents([(x, y)]))
            num_near = len(neighbors)

            num_right_remove = 0
            num_left_remove = 0

            for dx in [-1, 1]:
                neighbor_pos = (x + dx, y)
                if not self.grid.out_of_bounds(neighbor_pos):
                    patch_agents = self.grid.get_cell_list_contents([neighbor_pos])
                    for agent in patch_agents:
                        if isinstance(agent, Obstacle):
                            continue
                        if dx == 1 and not agent.left:
                            num_right_remove += 1
                        elif dx == -1 and agent.left:
                            num_left_remove += 1

            N_total = num_here + num_near - num_right_remove - num_left_remove

            P0 = (1 - Pm) ** N_total
            P1 = N_total * Pm * (1 - Pm) ** (N_total - 1) if N_total >= 1 else 0
            P2 = N_total * (N_total - 1) * 0.5 * (Pm ** 2) * (1 - Pm) ** (N_total - 2) if N_total >= 2 else 0
            P3 = N_total * (N_total - 1) * (N_total - 2) / 6 * (Pm ** 3) * (1 - Pm) ** (N_total - 3) if N_total >= 3 else 0
            P4 = N_total * (N_total - 1) * (N_total - 2) * (N_total - 3) / 24 * (Pm ** 4) * (1 - Pm) ** (N_total - 4) if N_total >= 4 else 0

            Uec = P0 + P1 + P2 + 0.51 * P3 + 0.07 * P4

            self.patch_data[(x, y)] = {
                **self.patch_data.get((x, y), {}),
                "Uec": Uec
            }