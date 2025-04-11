import mesa
import math

class Pedestrian(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)

    def test(self):
        print(f"Hi, I'm agent {str(self.unique_id)}")

    def move(self):
        #otoczenie komórek - wybieramy Moore neighborhood ze środkiem (9 komórek)
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore = True,
            include_center = True
            )
        #place_holder - na razie losowa
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

