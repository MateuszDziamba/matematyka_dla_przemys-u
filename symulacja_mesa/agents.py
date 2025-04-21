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
        self.leader = None
        self.door = self.get_door()
        self.exited = False
        self.pos_x = None
        self.pos_y = None
        self.color = "blue"
        self.float_position = None
        #self.movement_buffer = np.array([0.0, 0.0])
        self.follow_patience = random.randint(5, 15)  # how many steps we tolerate following
        self.follow_timer = 0  # how long following the current leader



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
        if density <= 4:
            self.speed = self.model.move_speed
        elif density >= 8:
            self.speed = self.model.move_speed / 14
        else:
            self.speed =  self.model.move_speed*(0.03*density**2 - 0.64*density +3.36)/1.4


    def move_to_cell(self, cell):
        cell = np.array(cell)
        dx = int(np.sign(cell[0]-self.float_position[0]))
        dy = int(np.sign(cell[1]-self.float_position[1]))

        #przesunąć się do celu
        new_float_pos = self.float_position + np.array([dx*self.speed, dy*self.speed], dtype=float)
        if sum(abs(self.float_position - cell) > self.speed) == 0 :
            self.model.grid.move_agent(self, cell)
            self.prepare_agent()
        #przesunął się w inne miejsce zygzakiem przez zmienianie zdania
        elif np.sum(abs(self.pos - new_float_pos) > 1)>0:
            new_int_pos = np.array(self.pos + np.sign(np.floor(new_float_pos-self.pos)), dtype=int)
            self.model.grid.move_agent(self, new_int_pos)
            self.prepare_agent()
        else:
            self.float_position += np.array([dx*self.speed, dy*self.speed], dtype=float)


    def distance_to(self, target):
        x, y = self.pos
        Tx, Ty = target.pos
        dx = Tx - x
        dy = Ty - y
        angle_rad = math.atan2(dy, dx)
        correct_angle = True
        if self.left:
            correct_angle = (angle_rad > 5/6*np.pi or angle_rad < -5/6*np.pi)
        else:
            correct_angle = (angle_rad < 1/6*np.pi and angle_rad > -1/6*np.pi) #30 stopni w każdą stronę
        return np.sqrt(dx**2 + dy**2), correct_angle
    
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
            self.speed = 0
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
        self.set_speed()
        self.nearby_leaders = None
        self.leader = None
        self.follow = False
        self.nearby_leaders = [agent for agent in self.model.grid.get_neighbors(tuple(self.pos), moore = True, include_center = False, radius = 3)
                                    if self.distance_to(agent)[1]] #ustawiony dystans na 3, ale można zmienić

        if self.nearby_leaders:
            #self.leader = min(self.nearby_leaders, key=lambda target: self.distance_to(target)[0])
            self.leader = random.choice(self.nearby_leaders)
            self.follow = True
        else:
            self.leader = None
            self.follow = False

        if self.follow:    
            self.face_leader()
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

    def p_avoid(self):
        x, y = self.pos
        neighbor_coords = []
        if self.left:
            possible_collisions = [(x-1, y)]
        else:
            possible_collisions = [(x+1, y)]

        for coord in possible_collisions:
            if not self.model.grid.out_of_bounds(coord):
                neighbor_coords.append(coord)

        
        if neighbor_coords:
            agents = self.model.grid.get_cell_list_contents(neighbor_coords[0])
            # liczymy tylko tych agentów, którzy mają przeciwną wartość 'left'
            number_of_agents = sum(1 for agent in agents if agent.left != self.left)
        else:
            number_of_agents = 0            
        p2, p4 = self.model.probability_competing, self.model.probability_competing   #wartości z artykłu
        p_avoi = [0, 0] #góra, dół po skosie

        p_avoi[0] = 1 - (1 - p2)**number_of_agents
        p_avoi[1] = 1 - (1 - p4)**number_of_agents
        return p_avoi

        
    def find_patch_BNE(self):
        x, y = self.pos
        neighbor_coords = []

        if self.left:
            possible_coords = [(x-1, y), (x-1, y+1), (x-1, y-1), (x, y-1), (x, y+1), (x,y)]
        else:
            possible_coords = [(x+1, y), (x+1, y+1), (x+1, y-1), (x, y-1), (x, y+1), (x,y)]

        # Filtrowanie tylko tych, które mieszczą się w siatce
        for coord in possible_coords:
            if not self.model.grid.out_of_bounds(coord):
                neighbor_coords.append(coord)

        best_patch = None
        best_utility = -float('inf')
        possible_collisions = [0,0]

        if self.left:
            #miejsca z których mogą iść agenci tak by było zderzenie
            possible_collisions = [(x-1, y +1), (x - 1, y - 1)]
        else:
            #miejsca z których mogą iść agenci tak by było zderzenie
            possible_collisions = [(x+1, y +1), (x+1, y - 1)]
        p_avoi = self.p_avoid()

        for coord in neighbor_coords:
            if self.model.grid.out_of_bounds(coord):
                continue

            if coord == possible_collisions[0] and random.random() < p_avoi[0]:
                #print(p_avoi)
                continue
            elif coord == possible_collisions[1] and random.random() < p_avoi[1]:
                #print(p_avoi)
                continue
            else:
                patch_data = self.model.patch_data.get(coord)
                if patch_data:
                    total_u = patch_data.get("Ud_lt" if self.left else "Ud_rt", 0) + patch_data.get("Uec", 0)
                    if total_u > best_utility:
                        best_utility = total_u
                        best_patch = coord

        return best_patch
    
