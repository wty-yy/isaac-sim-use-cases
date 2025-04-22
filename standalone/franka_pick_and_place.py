import numpy as np

from isaacsim.simulation_app import SimulationApp
simulation_app = SimulationApp({"headless": False})

from isaacsim.core.api.world import World
from isaacsim.core.api.scenes import Scene
import omni.replicator.core as rep

class Runner:
    def __init__(self):
        self.world = World(stage_units_in_meters=1.0)
        self.scene = Scene()
        self.scene.add_ground_plane(color=np.array([1, 1, 1]))
        # self.scene.add_default_ground_plane()
        rep.create.light(rotation=(0, 45, 0), light_type='distant')
    
    def run(self):
        while True:
            self.world.step()


if __name__ == '__main__':
    runner = Runner()
    runner.run()
    simulation_app.close()
