import omni.usd
import numpy as np
from isaacsim.core.api.world import World
from isaacsim.core.api.scenes import Scene
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.examples.interactive.base_sample import BaseSample
from pxr import UsdLux, Gf, Sdf
from isaacsim.core.utils.prims import delete_prim, get_prim_at_path
from isaacsim.core.utils.viewports import set_camera_view

class SplitCube:
    def __init__(
            self, world: World, scene: Scene, stage,
            idx: int, scale: float,
            position: np.ndarray, color: np.ndarray,
            line_velocity: np.ndarray
        ):
        self.world = world
        self.scene = scene
        self.stage = stage
        self.prim_path = f"/World/SplitCubes/Cube_{idx}"
        self.cube = DynamicCuboid(
            prim_path=self.prim_path,
            name=f"cube{idx}",
            position=np.array(position),
            scale=np.array([scale] * 3),
            color=np.array(color),
            linear_velocity=np.array(line_velocity)
        )
        self.scene.add(self.cube)
    
    def remove(self):
        if get_prim_at_path(self.prim_path):
            delete_prim(self.prim_path)
    
    def deactivate(self):
        self.stage.GetPrimAtPath(self.prim_path).SetActive(False)

class CubeSplit(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        # self._world_settings.update({'backend': 'torch', 'device': 'cuda'})
        self.last_time = 0
        self.idx = 0
        return

    def setup_scene(self):
        self.world = self.get_world()
        self.scene: Scene = self.world.scene
        self.stage = omni.usd.get_context().get_stage()
        self.scene.add_ground_plane()
        # self.scene.add_default_ground_plane()
        # self.stage.RemovePrim("/World/defaultGroundPlane/SphereLight")
        # self.stage.GetPrimAtPath("/World/defaultGroundPlane/SphereLight").SetActive(False)
        
        light = UsdLux.SphereLight.Define(self.stage, "/World/Lights/SphereLight1")
        light.CreateIntensityAttr(5e6)
        light.AddTranslateOp().Set(Gf.Vec3f(40, 0, 40))
        light = UsdLux.SphereLight.Define(self.stage, "/World/Lights/SphereLight2")
        light.CreateIntensityAttr(5e6)
        light.AddTranslateOp().Set(Gf.Vec3f(-40, 0, 40))

        for _ in range(256):
            self.debug_add()
        return
    
    def debug_add(self):
        self.add_split_cube(
            np.random.uniform(0.5, 2.0), position=np.random.uniform(0, 2, (3,)),
            color=np.random.rand(3), line_velocity=np.array([0, 0, np.random.rand()])
        )
    
    def add_split_cube(self, scale, position, color, line_velocity):
        self.split_cube = SplitCube(
            self.world, self.scene, self.stage, self.idx,
            scale=scale, position=position, color=color, line_velocity=line_velocity
        )
        self.idx += 1

    # after setup_scene, and after one physics time step
    async def setup_post_load(self):
        set_camera_view(eye=(30, 30, 30), target=(0, 0, 0))
        # self.world.add_physics_callback("physics_step", self.physics_step)
        return
    
    # def physics_step(self, dt):
    #     t = self.world.current_time
    #     if t - self.last_time > 1:
    #         self.last_time = t
    #         # self.split_cube.remove()
    #         # self.split_cube.deactivate()
    #         self.debug_add()

    async def setup_pre_reset(self):
        return

    async def setup_post_reset(self):
        return

    def world_cleanup(self):
        return
