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
import random
import math

class Evacuation(mesa.Model):
    def __init__(self, n=10, width=20, height=10, door_width = 4, seed=10, model_type = "BNE_mixed_SR", p_BNE = 100):
        super().__init__(seed=seed)
        self.patch_data = {}
        self.number_persons = n
        #przestrzeń MultiGrid dopuszcza kilku agentów w jednym polu
        #argument False oznacza torus=False
        self.grid = mesa.space.MultiGrid(width, height, False)
        
        self.moving_pattern = model_type
        
        
    
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
        self.probability_competing = 10
        self.percentage_of_BNE = p_BNE/100
        self.weight_Ud = 1.0

        self.datacollector = mesa.DataCollector(
            model_reporters={"evacuating": self.compute_agents},
            agent_reporters={"x": "pos_x", "y": "pos_y", "speed": "speed"}
        )


        #tworzenie agentów
        agents = Pedestrian.create_agents(model=self, n=n)
        #ustawienie agentów - losujemy współrzędne dla każdego
        Xs = self.rng.integers(0, self.grid.width, size = (n,))
        Ys = self.rng.integers(0, self.grid.height, size = (n,))
        
        for a, i, j in zip(agents, Xs, Ys):
            self.grid.place_agent(a, (i,j))
            a.prepare_agent()

        #ustawienie typu agenta jeśli jest model mieszany
        if self.moving_pattern == "BNE_mixed_SR" or self.moving_pattern == "BNE_mixed_RF":
            BNE_agents = self.random.sample(list(self.agents), int(self.percentage_of_BNE*n))
            for agent in BNE_agents:
                agent.BNE_type = True

        self.running = True
        self.datacollector.collect(self)
        self.calculate_distance_utility()
        self.calculate_expected_comfort()

    def compute_agents(self):
        return len(self.agents.get("exited"))

    def step(self):
        #funkcja shuffle_do miesza listę agentów i wykonuje podaną funkcję
        self.datacollector.collect(self)
        self.agents.shuffle_do("decide")
        self.calculate_expected_comfort()
        self.calculate_distance_utility()


    # def clean(self):
    #     for a in self.agents:
    #         if a.exited:
    #             self.grid.remove_agent(a)
                
    def calculate_distance_utility(self):
        diagonal = math.hypot(self.grid.width, self.grid.height)

        for _, (x, y) in self.grid.coord_iter():
            x_left_door, y_left_list = self.exits['left']
            x_right_door, y_right_list = self.exits['right']

            y_left = min(y_left_list, key=lambda yd: abs(y - yd))
            y_right = min(y_right_list, key=lambda yd: abs(y - yd))

            D_lt = math.hypot(x - x_left_door, y - y_left)
            D_rt = math.hypot(x - x_right_door, y - y_right)

            Ud_lt = (1 - (D_lt / diagonal)) * self.weight_Ud
            Ud_rt = (1 - (D_rt / diagonal)) * self.weight_Ud

            self.patch_data[(x, y)] = {
                **self.patch_data.get((x, y), {}),
                "Ud_lt": Ud_lt,
                "Ud_rt": Ud_rt
            }
    
    def calculate_expected_comfort(self):
        Pm = self.probability_competing / 100

        for _, (x, y) in self.grid.coord_iter():
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