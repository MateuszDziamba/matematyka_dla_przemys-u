import mesa
import math
import numpy as np
import random

class Pedestrian(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.speed = None
        self.left = random.choice([True, False])
        self.follow = None
        self.BNE_type = None
        self.nearby_leaders = None
        self.leader = False
        self.door = self.get_door()
        self.exited = False

    def get_door(self):
        print("Hi i'm agent", self.unique_id, "going left:", self.left)
        print("my door is:",self.model.exits['left' if self.left else 'right'] )
        return self.model.exits['left' if self.left else 'right']
       
    def test(self):
        print(f"Hi, I'm agent {str(self.unique_id)}")

    def get_neighborhood(self):
        #otoczenie komórek - wybieramy Moore neighborhood ze środkiem (9 komórek)
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore = True,
            include_center = True
            )
        return possible_steps

    def move_test(self):
        #place_holder - na razie losowa
        possible_steps = self.get_neighborhood()
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def set_speed(self):
        density = (len(self.get_neighborhood())-1)/(0.7*3*0.7*3) # ped/m^2 - wszsyscy w otoczeniu poza nami podzielone przez długośc i szerokość 3x3 komórki po 0.7 m
        self.speed = 1
        #DO DOKOŃCZENIA - różna prędkość w zależności od density - na heatmapie bez problemy z "wirtualną pozycją float", ale dla ludzików nie wiem chyba trzeba by zrobić sztucznie gęstszą siatkę, żeby dało sie tak ruszać, ale wtedy trudniej wybieranie komórek
        # if density<=4:
        #     print("density<-4")
        #     self.speed = self.model.move_speed
        # elif density>=8:
        #     self.speed = self.model.move_speed/14
        # else:
        #     self.speed = 0.03*(density**2) - 0.64*density +3.36
        # print("sel_speed speed", self.speed)
        
    def move_to_cell(self, cell):
        self.model.grid.move_agent(self, cell)

    def find_closest_door_cell(self):
        x, y = self.pos
        x_door, y_door = self.door
        dists_to_door = [math.hypot(x_door-x, y_exit-y) for y_exit in y_door] #majbiższa komórka drzwi (gdy ma szerokość>1)
        y_door = y_door[np.argmin(dists_to_door)]
        return x_door, y_door

    def move_to_door(self, target):
        x, y = self.pos
        x_target, y_target = target
        dx = np.sign(x_target-x)
        dy = np.sign(y_target-y)

        self.model.grid.move_agent(self, (x+dx, y+dy))

    def decide(self):
        x, y = self.pos
        x_exit, ys_exit = self.door
        if x==x_exit and y in ys_exit:
            self.model.grid.remove_agent(self)
            self.remove()
            return 
        
        if self.model.moving_pattern == "SR":
            self.shortest_route()
        if self.model.moving_pattern == "RF":
            self.random_follow()
        if self.model.moving_pattern == "BNE_mixed_SR":
            self.bne_mixed_sr()
        if self.model.moving_pattern == "BNE_mixed_RF":
            self.bne_mixed_rf()

    def shortest_route(self):
        self.set_speed()
        door_cell = self.find_closest_door_cell()
        self.move_to_door(door_cell)