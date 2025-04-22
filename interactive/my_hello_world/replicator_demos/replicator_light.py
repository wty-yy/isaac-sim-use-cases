import numpy as np
from isaacsim.examples.interactive.base_sample import BaseSample
import omni.replicator.core as rep
from isaacsim.core.api.scenes import Scene
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.utils.viewports import set_camera_view
import omni.usd
from pxr import Usd

class ReplicatorLightDemo(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        self.world = self.get_world()
        self.scene: Scene = self.world.scene
        self.scene.add_default_ground_plane()
        rep.create.light(
            position=(0, 0, 5), light_type="sphere", color=(1,1,1),
            intensity=1e5
        )
        self.stage = omni.usd.get_context().get_stage()
        prim = self.stage.GetPrimAtPath("/World/defaultGroundPlane/SphereLight")
        if prim:
            prim.SetActive(False)
        return

    # after setup_scene, and after one physics time step
    async def setup_post_load(self):
        set_camera_view(eye=(10, 10, 10), target=(0, 0, 0))
        return
    
    async def setup_pre_reset(self):
        return

    async def setup_post_reset(self):
        return

    def world_cleanup(self):
        return
