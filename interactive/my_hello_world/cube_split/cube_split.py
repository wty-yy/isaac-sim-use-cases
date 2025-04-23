import omni.usd
import numpy as np
from isaacsim.core.api.world import World
from isaacsim.core.api.scenes import Scene
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.examples.interactive.base_sample import BaseSample
from pxr import UsdLux, Gf, Sdf
from isaacsim.core.utils.prims import delete_prim, get_prim_at_path

class SplitCube:
    def __init__(
            self, world: World, scene: Scene,
            idx: int, scale: float,
            position: np.ndarray, color: np.ndarray,
            line_velocity: np.ndarray
        ):
        self.world = world
        self.scene = scene
        self.prim_path = f"/World/SplitCubes/Cube_{idx}"
        self.cube = DynamicCuboid(
            prim_path=self.prim_path,
            name=f"cube{idx}",
            position=position,
            scale=np.array([scale] * 3),
            color=color,
            linear_velocity=line_velocity
        )
        self.scene.add(self.cube)
    
    def remove(self):
        if get_prim_at_path(self.prim_path):
            delete_prim(self.prim_path)

class CubeSplit(BaseSample):
    def __init__(self) -> None:
        super().__init__()
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
        
        light = UsdLux.SphereLight.Define(self.stage, "/World/SphereLight")
        light.CreateIntensityAttr(2e5)
        light.AddTranslateOp().Set(Gf.Vec3f(5, 0, 5))

        self.cube = SplitCube(self.world, self.scene, self.idx, )
        return
    
    def add_split_cube(self, scale, position, color, line_velocity):
        self.split_cube = SplitCube(
            self.world, self.scene, self.idx,
        )
        self.idx += 1

    # after setup_scene, and after one physics time step
    async def setup_post_load(self):
        t = self.world.current_time
        if t - self.last_time > 1:
            self.last_time = t

        return

    async def setup_pre_reset(self):
        return

    async def setup_post_reset(self):
        return

    def world_cleanup(self):
        return
