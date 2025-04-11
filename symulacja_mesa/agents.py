import mesa
import math
import numpy as np

class Pedestrian(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.speed = None
        self.left = None
        self.follow = None
        self.BNE_type = None
        self.nearby_leaders = None
        self.leader = False
        self.door = self.get_door()

    def get_door(self):
        return self.model.exits['left' if self.left else 'right']

    def test(self):
        print(f"Hi, I'm agent {str(self.unique_id)}")

    def get_neighbours(self):
        #otoczenie komórek - wybieramy Moore neighborhood ze środkiem (9 komórek)
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore = True,
            include_center = True
            )
        return possible_steps

    def move_test(self):
        #place_holder - na razie losowa
        possible_steps = self.get_neighbours()
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def move_to(self, target):
        x_curr, y_curr = self.pos
        x_target, y_target = target
        if isinstance(target, list):
            #drzwi
            dists_to_door = [self.model.grid.get_distance(self.pos, (x_target, y_exit)) for y_exit in y_target]
            #majbiższa komórka drzwi (gdy ma szerokość>1)
            y_target = y_target[np.argmin(dists_to_door)]
        distance = self.model.grid.get_distance(self.pos, (x_target, y_target))
        #DO DOKOŃCZENIA
        

    def decide(self):
        if self.model.moving_pattern == "SR":
            self.shortest_route()
        if self.model.moving_patter == "RF":
            self.random_follow()
        if self.model.moving_pattern == "BNE_mixed_SR":
            self.bne_mixed_sr()
        if self.model.moving_pattern == "BNE_mixed_RF":
            self.bne_mixed_rf()

    def shortest_route(self):
        self.set_speed()
        self.move_to(self.door)