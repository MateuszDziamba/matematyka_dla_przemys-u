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

SYMULACJĘ URUCHAMIAMY Z TERMINALA
(w VS na dole lub po prostu w folderze używając Otwórz w Terminalu)
będąc w tym folderze wpisujemy:
solara run app.py
po prostu odpalenie plików nic nie da
"""
import mesa
from agents import Pedestrian

class Evacuation(mesa.Model):
    def __init__(self, n, width, height, seed=None):
        super().__init__(seed=seed)
        self.number_persons = n
        #przestrzeń MultiGrid dopuszcza kilku agentów w jednym polu
        #argument False oznacza torus=False
        self.grid = mesa.space.MultiGrid(width, height, False)
        self.moving_pattern = None
        
        #exits
        self.door_width = 3
        self.exit_width = None
        self.exits = {''
        #x  #ys - wysokosc drzwi - na razie ręcznie, można dodać suwak, przy parzystych wychodzi +1 szerokość (ze środkiem)
        'left': [0, [self.grid.height//2 + i for i in range(-self.door_width//2, self.door_width//2)] ],
        'right': [self.grid.width,  [self.grid.height//2 + i for i in range(-self.door_width//2, self.door_width//2)]]}

        #poruszanie agentów
        self.move_speed = None
        self.step_length = None
        self.probability_competing = None
        self.percentage_of_BNE = None



        #tworzenie agentów
        agents = Pedestrian.create_agents(model=self, n=n)
        #ustawienie agentów - losujemy współrzędne dla każdego
        Xs = self.rng.integers(0, self.grid.width, size = (n,))
        Ys = self.rng.integers(0, self.grid.height, size = (n,))
        for a, i, j in zip(agents, Xs, Ys):
            self.grid.place_agent(a, (i,j))

        #otoczenie komórek - wybieramy Moore neighborhood ze środkiem (9 komórek)


    def step(self):
        #funkcja shuffle_do miesza listę agentów i wykonuje podaną funkcję
        self.agents.shuffle_do("move_test")
