import mesa
import math
import numpy as np
import random

class Pedestrian(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.speed = model.move_speed
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
        self.float_position = None


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

    def set_speed(self):
        neighborhood = self.model.grid.get_neighbors(tuple(self.pos), moore=True, include_center=True)
        density = len(neighborhood) / (0.7 * 0.7 * 9)
        print("============ Agent", self.unique_id)
        print("density", density)
        if density <= 4:
            self.speed = self.model.move_speed
        elif density >= 8:
            self.speed = self.model.move_speed / 10
        else:
            self.speed =  ((8.12-density)/4.12)*self.model.move_speed


    def move_to_cell(self, cell):
        cell = np.array(cell)
        dx = np.sign(cell[0]-self.pos_x)
        dy = np.sign(cell[1]-self.pos_y)
        print("Prędkość", self.speed)
        print("Pozycja:", self.pos)
        print("pos_x, pos_y", self.pos_x, self.pos_y)
        print("Float_pos:", self.float_position)
        print("Cel: ", cell)
        print("dx, dy", dx, dy)

        #if np.sum(np.sign(self.float_position)*np.floor(np.abs(self.float_position)) == cell)==2: #nowe współrzędne
        print("warunek")
        print("abs", abs(self.float_position - cell), ">", self.speed)
        print(abs(self.float_position - cell) > self.speed)
        if sum(abs(self.float_position - cell) > self.speed) == 0 :
            self.model.grid.move_agent(self, cell)
            self.prepare_agent()
            print("RUCH i nowa pozycja ", self.pos, self.float_position)
        else:
            print("BEZ RUCHU")
            self.float_position += np.array([dx*self.speed, dy*self.speed], dtype=float)
            print("float_pos", self.pos, self.float_position)



    def distance_to(self, target):
        x, y = self.pos
        Tx, Ty = target.pos
        #print(np.sqrt((x - Tx)**2 + (y - Ty)**2))
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
        target = (x+dx, y+dy)
        self.move_to_cell(target)

    def prepare_agent(self):
        x, y = self.pos
        self.pos_x = x
        self.pos_y = y
        self.float_position = np.array(self.pos, dtype=float)

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
        self.nearby_leaders = None
        self.leader = None
        self.follow = False
        if self.left:
            self.nearby_leaders = [agent for agent in self.model.agents if (agent.pos_x < Tx 
                                   and self.distance_to(agent) > 0 and self.distance_to(agent)< 5)] #ustawiony dystans na 5, ale można zmienić
        else:
            self.nearby_leaders = [agent for agent in self.model.agents if (agent.pos_x > Tx 
                                   and self.distance_to(agent) > 0 and self.distance_to(agent)< 5)]


        if self.nearby_leaders:
            self.leader = min(self.nearby_leaders, key=lambda target: self.distance_to(target))
            print(self.distance_to(self.leader))
            self.follow = True
        else:
            self.leader = None
            self.follow = False

        if self.follow:    
            if self.left:
                if self.leader.pos_x < Tx :
                    self.face_leader()               
                else:
                    self.stop_following()
            else:
                if self.leader.pos_x > Tx:
                    
                    self.face_leader()                    
                else:
                    self.stop_following()
        else:
            self.shortest_route()


    def face_leader(self):
        x, y = self.pos
        leader_x, leader_y = self.leader.pos
        if leader_x >= x and self.left: # teoretycznie powinno działać bez tego if, ale coś się wcześniej psuje i nie wiem co
            self.stop_following()
        elif leader_x <= x and not self.left:
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
            possible_coords = [(x-1, y), (x-1, y+1), (x-1, y-1), (x, y-1), (x, y+1)]
        else:
            possible_coords = [(x+1, y), (x+1, y+1), (x+1, y-1), (x, y-1), (x, y+1)]

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
    
