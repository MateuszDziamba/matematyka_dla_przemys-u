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
from map_config import ObstacleMap
from map_config import Spawn
import random
import math
import heapq
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#random.seed(10)

class Evacuation(mesa.Model):
    def __init__(self, n=10, width=20, height=10, door_width = 4, seed=10, model_type = "BNE_mixed_SR", p_BNE = 100, map_type = "empty", spawn_position = "all",right_door = True, classroom=False):
        super().__init__(seed=seed)
        self.classroom = classroom
        self.patch_data = {}
        self.number_persons=n
        #przestrzeń MultiGrid dopuszcza kilku agentów w jednym polu
        #argument False oznacza torus=False
        if self.classroom:
            width=16
            height=20
            map_type="classroom"
            spawn_position='classroom'
            if right_door:
                self.exits = {
                'right': [width-1, [4,5]], #lower
                }
            else:
                self.exits = {
                    'right': [width-1, [4]], #lower
                    'left': [width-1, [16]] #upper
            }

        self.grid = mesa.space.MultiGrid(width, height, False)
        
        self.moving_pattern = model_type
        self.right_door_only = right_door
    
        #exits
        self.door_width = door_width
        self.exit_width = None
        
        if not self.classroom:
            #tylko prawe drzwi
            if self.right_door_only:
                self.exits = {''
                'left': [0,[]],
                'right': [self.grid.width-1,  [self.grid.height//2 + i for i in range(-(self.door_width//2), (self.door_width//2))]]}
            #oba wyjścia
            else:
                self.exits = {
                #x  #ys - wysokosc drzwi - na razie ręcznie, można dodać suwak, przy parzystych wychodzi +1 szerokość (ze środkiem)
                # Zmieniłam bez +1, bo przy parzystej wysokości wyjściowej nie wychodziło równo
                'left': [0, [self.grid.height//2 + i for i in range(-(self.door_width//2), (self.door_width//2) )] ],
                'right': [self.grid.width-1,  [self.grid.height//2 + i for i in range(-(self.door_width//2), (self.door_width//2))]]}

        #przeszkody
        self.obstacles_map = ObstacleMap(height, width, door_width, self.exits).get_map(map_type) #przeszkody zapisane w macierzy 0-1, 0 - brak przeszkody, 1 - przeszkoda

        #poruszanie agentów
        self.move_speed = 1
        self.step_length = None
        self.probability_competing = 1/6
        self.percentage_of_BNE = p_BNE/100
        self.weight_Ud = 1.0 #domyślnie 1.0

        self.datacollector = mesa.DataCollector(
            model_reporters={"evacuating": self.compute_agents},
            agent_reporters={"speed": "speed"}
        )


        #tworzenie agentów
        agents = Pedestrian.create_agents(model=self, n=n)
        #ustawienie agentów - losujemy współrzędne z wyłączeniem ścian dla każdego agenta
        counter = 0
        positions = np.zeros((n,2))
        forbiden_positions = Spawn(height, width).get_spawn_positions(self.obstacles_map, spawn_position)
        if not self.classroom:
            while counter < n:
                pos = (self.rng.integers(0, self.grid.width), self.rng.integers(0, self.grid.height))
                if forbiden_positions[pos[0], pos[1]] == 0:
                    positions[counter] = pos
                    counter += 1
                else:
                    continue
        else:
            rows, cols = forbiden_positions.shape
            possible_pos = [(y,  x) for y in range(rows) for x in range(cols) if forbiden_positions[y, x] == 0]
            used_positions = set()
            pos = (9,13) #Ślęzak
            used_positions.add(pos)
            positions[counter] = pos
            counter+=1
            pos1 = (2,18) #my
            pos2 = (6,18)
            used_positions.add(pos1)
            positions[counter] = pos1
            counter+=1
            used_positions.add(pos2)
            positions[counter] = pos2
            counter+=1
            while counter<n:
                pos = self.rng.choice(possible_pos)
                while counter < n:
                    pos = random.choice(possible_pos)
                    if pos not in used_positions:
                        used_positions.add(pos)
                        positions[counter] = pos
                        counter += 1
                    else:
                        continue

        
        self.calculate_distance_utility() #obliczamy użyteczność odległości przed dodaniem agentów aby móc przypisać do nich bliższe wyjście
        for a, i, j in zip(agents, positions[:,0], positions[:,1]):
            a.pos = (int(i),int(j))
            a.prepare_agent()
            self.grid.place_agent(a, (int(i), int(j)))


        #ustawienie typu agenta jeśli jest model mieszany
        if self.moving_pattern == "BNE_mixed_SR" or self.moving_pattern == "BNE_mixed_RF":
            BNE_agents = self.random.sample(list(self.agents), int(self.percentage_of_BNE*n))
            for agent in BNE_agents:
                agent.BNE_type = True
            
        self.running = True
        self.datacollector.collect(self)
        self.calculate_expected_comfort()
        
    #metoda nieużywana, ale może się przydać w przyszłości np. do ręcznego dodawania przeszkód na mapie
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


    # def clean(self):
    #     for a in self.agents:
    #         if a.exited:
    #             self.grid.remove_agent(a)
                
    def calculate_distance_utility(self):
        '''
        Traktując naszą mapę jak graf (czyli formalnie w jedyny słuszny sposób),
        oblicza dla każdego wierzchołka odległość do najbliższego wyjścia.
        Na tej podstawie każdej komórce przypisywana jest użyteczność, im dalej od wyjścia tym mniejsza,
        dla komórek będących wyjściami użyteczność wynosi 1. 
        '''
    
        width, height = self.grid.width, self.grid.height
        diagonal = math.hypot(width, height)

        # Koszty ruchu: 8 kierunków (Moore)
        directions = [
            (-1,  0, 1), (1,  0, 1),   # góra/dół
            (0, -1, 1), (0,  1, 1),   # lewo/prawo
            (-1, -1, math.sqrt(2)), (1, -1, math.sqrt(2)),  # ukośne
            (-1,  1, math.sqrt(2)), (1,  1, math.sqrt(2))
        ]
        test_map_left = np.zeros((width, height)) #testowa mapa do wizualizacji użyteczności
        test_map_right = np.zeros((width, height))
         
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
        if self.classroom:
            lower_exit = [(self.exits['right'][0], y) for y in self.exits['right'][1]]
            dist_to_lower = dijkstra(lower_exit)
            if not self.right_door_only:
                upper_exit = [(self.exits['left'][0], y) for y in self.exits['left'][1]]
                dist_to_upper = dijkstra(upper_exit)
            
           
        else:
            if not self.right_door_only:
                left_door_positions = [(self.exits['left'][0], y) for y in self.exits['left'][1]]
            right_door_positions = [(self.exits['right'][0], y) for y in self.exits['right'][1]]

            # Oblicz odległości
            if not self.right_door_only:
                dist_to_left = dijkstra(left_door_positions)
            dist_to_right = dijkstra(right_door_positions)
           

        # Przelicz użyteczność
        for x in range(width):
            for y in range(height):
                #przypisanie wartości -100 do komórki z przeszkodą, teoretycznie symulacja powinna działać bez tego, ale jest to dodatkowe zabezpieczenie przed ruchem na pole z przeszkodą
                if self.obstacles_map[x, y] == 1:
                    Ud_lt = -100*self.weight_Ud
                    Ud_rt = -100*self.weight_Ud
                    
                    self.patch_data[(x, y)] = {
                        **self.patch_data.get((x, y), {}),
                        "Ud_lt": Ud_lt,
                        "Ud_rt": Ud_rt
                    }
                    test_map_left[x][y] = -1*self.weight_Ud 
                    test_map_right[x][y] = -1*self.weight_Ud 
                else:
                    if self.classroom:
                        if not self.right_door_only:
                            D_lt = dist_to_upper[x, y]
                            D_rt = dist_to_lower[x, y]
                            Ud_lt = (1 - (D_lt / diagonal)) * self.weight_Ud if not np.isinf(D_lt) else 0
                            Ud_rt = (1 - (D_rt / diagonal)) * self.weight_Ud if not np.isinf(D_rt) else 0
                            self.patch_data[(x, y)] = {
                                    **self.patch_data.get((x, y), {}),
                                    "Ud_lt": Ud_lt,
                                    "Ud_rt": Ud_rt
                                }
                        # test_map_left[x][y] = Ud_lt
                        # test_map_right[x][y] = Ud_rt
                        else:
                            D_rt = dist_to_lower[x, y]
                            Ud_rt = (1 - (D_rt / diagonal)) * self.weight_Ud if not np.isinf(D_rt) else 0
                            self.patch_data[(x, y)] = {
                                    **self.patch_data.get((x, y), {}),
                                    "Ud_rt": Ud_rt}
                    else:
                        if not self.right_door_only:
                            D_lt = dist_to_left[x, y]
                            D_rt = dist_to_right[x, y]
                            Ud_lt = (1 - (D_lt / diagonal)) * self.weight_Ud if not np.isinf(D_rt) else 0
                            Ud_rt = (1 - (D_rt / diagonal)) * self.weight_Ud if not np.isinf(D_rt) else 0

                            self.patch_data[(x, y)] = {
                                **self.patch_data.get((x, y), {}),
                                "Ud_lt": Ud_lt,
                                "Ud_rt": Ud_rt
                            }
                            # test_map_left[x][y] = Ud_lt
                            # test_map_right[x][y] = Ud_rt
                        else:
                            D_rt = dist_to_right[x, y]

                            Ud_rt = (1 - (D_rt / diagonal)) * self.weight_Ud if not np.isinf(D_rt) else 0

                            self.patch_data[(x, y)] = {
                                **self.patch_data.get((x, y), {}),
                                "Ud_rt": Ud_rt
                            }
                        # test_map_right[x][y] = Ud_rt
        
        plt.clf()
        plt.figure(figsize=(20, 20))
        sns.heatmap(data=test_map_left, annot=True)
        plt.savefig('uzytecznosc_left.png')

        plt.clf()
        plt.figure(figsize=(20, 20))
        sns.heatmap(data=test_map_right, annot=True)
        plt.savefig('uzytecznosc_right.png')
    
    def calculate_expected_comfort(self):
        Pm = self.probability_competing
        #test_Uec = np.zeros((self.grid.width, self.grid.height)) #testowa mapa do wizualizacji oczekiwanej użyteczności związanej z komfortem
        for _, (x, y) in self.grid.coord_iter():
            if self.obstacles_map[x, y] == 1:
                continue
            neighbors = self.grid.get_neighbors((x, y), moore=True, include_center=False)
            num_here = len(self.grid.get_cell_list_contents([(x, y)]))
            num_near = len(neighbors)

            num_right_remove = 0
            num_left_remove = 0

            for dx in [-1, 1]:
                neighbor_pos = (x + dx, y)
                if not self.grid.out_of_bounds(neighbor_pos):
                    patch_agents = self.grid.get_cell_list_contents([neighbor_pos])
                    for agent in patch_agents:
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
            #test_Uec[x][y] = Uec
        #plt.clf()
        #plt.figure(figsize=(20, 20))
        #sns.heatmap(data=test_Uec, annot=True)
        #plt.savefig('Uec.png' + str(self.plot_counter) + '.png')
        