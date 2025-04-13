import mesa
import math
import numpy as np
import random

class Pedestrian(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.speed = None
        self.left = random.choice([True, False])
        self.follow = True
        self.BNE_type = None
        self.nearby_leaders = None
        self.leader = False
        self.door = self.get_door()
        self.exited = False
        self.pos_x = None
        self.pos_y = None
        self.color = "blue"


    def get_door(self):
        return self.model.exits['left' if self.left else 'right']
       
    def test(self):
        print(f"Hi, I'm agent {str(self.unique_id)}")

    def get_neighborhood(self):
        #otoczenie komórek - wybieramy Moore neighborhood ze środkiem (9 komórek)
        possible_steps = self.model.grid.get_neighborhood(
            tuple(self.pos),
            moore = True,
            include_center = True
            )
        return possible_steps

    def move_test(self):
        #place_holder - na razie losowa
        possible_steps = self.get_neighborhood()
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    # def set_speed(self):
    #     density = (len(self.get_neighborhood())-1)/(0.7*3*0.7*3) # ped/m^2 - wszsyscy w otoczeniu poza nami podzielone przez długośc i szerokość 3x3 komórki po 0.7 m
    #     self.speed = 1
    def set_speed(self):
        neighborhood = self.model.grid.get_neighbors(tuple(self.pos), moore=True, include_center=True)
        density = len(neighborhood) / (0.7 * 0.7 * 9)

        if density <= 4:
            self.speed = self.model.move_speed
        elif density >= 8:
            self.speed = self.model.move_speed / 14
        else:
            self.speed = self.model.move_speed * (0.03 * density ** 2 - 0.64 * density + 3.36) / 1.4
        
    def move_to_cell(self, cell):
        self.model.grid.move_agent(self, cell)

    def distance_to(self, target):
        x, y = self.pos
        Tx, Ty = target.pos
        print(np.sqrt((x - Tx)**2 + (y - Ty)**2))
        return np.sqrt((x - Tx)**2 + (y - Ty)**2)
    
    def find_closest_door_cell(self):
        x, y = self.pos
        x_door, y_door = self.door
        dists_to_door = [math.hypot(x_door-x, y_exit-y) for y_exit in y_door] #najbiższa komórka drzwi (gdy ma szerokość>1)
        y_door = y_door[np.argmin(dists_to_door)]
        return x_door, y_door

    def move_to_door(self, target):
        x, y = self.pos
        x_target, y_target = target
        dx = np.sign(x_target-x)
        dy = np.sign(y_target-y)

        self.model.grid.move_agent(self, (x+dx, y+dy))

    def prepare_agent(self):
        x, y = self.pos
        self.pos_x = x
        self.pos_y = y

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
            if self.BNE_type:
                self.bne_moving()
            else:
                self.shortest_route()
        if self.model.moving_pattern == "BNE_mixed_RF":
            if self.BNE_type:
                self.bne_moving()
            else:
                self.random_follow()

    def shortest_route(self):
        self.set_speed()
        door_cell = self.find_closest_door_cell()
        self.move_to_door(door_cell)

    def random_follow(self):
        Tx = self.pos_x
        if self.left:
            self.nearby_leaders = [agent for agent in self.model.agents if (agent.pos_x < Tx 
                                   and self.distance_to(agent) > 0 and self.distance_to(agent)< 5)]
        else:
            self.nearby_leaders = [agent for agent in self.model.agents if (agent.pos_x > Tx 
                                   and self.distance_to(agent) > 0 and self.distance_to(agent)< 5)]


        if self.nearby_leaders:
            self.leader = min(self.nearby_leaders, key=lambda target: self.distance_to(target))
            self.follow = True
        else:
            self.leader = None
            self.follow = False

        if self.follow:    
            if self.left:
                if self.leader.pos_x >= Tx: 
                    self.stop_following()
                else:
                    self.face_leader()
            else:
                if self.leader.pos_x <= Tx:
                    self.stop_following()                    
                else:
                    self.face_leader()
        else:
            self.shortest_route()


    def face_leader(self):
        x, y = self.pos
        leader_x, leader_y = self.leader.pos
        if leader_x == x: # teoretycznie powinno działać bez tego if, ale coś się wcześniej psuje i nie wiem co
            self.stop_following()
        else:
            dx = np.sign(leader_x - x)
            dy = np.sign(leader_y - y)
            self.move_to_cell((x + dx, y + dy))
    
    def stop_following(self):
        self.leader = None
        self.nearby_leaders = None
        self.follow = False
        self.shortest_route()
 
    def bne_moving(self):
        self.set_speed()
        target_patch = self.find_patch_BNE()
        if target_patch:
            self.move_to_cell(target_patch)

    def find_patch_BNE(self):
        x, y = self.pos
        neighbor_coords = []

        if self.left:
            possible_coords = [(x-1, y), (x-1, y+1), (x-1, y-1)]
        else:
            possible_coords = [(x+1, y), (x+1, y+1), (x+1, y-1)]

        # Filtrowanie tylko tych, które mieszczą się w siatce
        for coord in possible_coords:
            if not self.model.grid.out_of_bounds(coord):
                neighbor_coords.append(coord)

        best_patch = None
        best_utility = -float('inf')

        for coord in neighbor_coords:
            if self.model.grid.out_of_bounds(coord):
                continue
            patch_data = self.model.patch_data.get(coord)
            if patch_data:
                total_u = patch_data.get("Ud_lt" if self.left else "Ud_rt", 0) + patch_data.get("Uec", 0)
                if total_u > best_utility:
                    best_utility = total_u
                    best_patch = coord

        return best_patch
    
