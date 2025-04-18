# Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from isaacsim.core.api.scenes import Scene
import numpy as np
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.examples.interactive.base_sample import BaseSample

# Note: checkout the required tutorials at https://docs.omniverse.nvidia.com/app_isaacsim/app_isaacsim/overview.html


class MyHelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):

        self.world = self.get_world()
        self.world.scene.add_default_ground_plane()
        self.scene: Scene = self.world.scene
        theta = np.pi / 4
        self.cube = self.scene.add(DynamicCuboid(
            prim_path="/World/cube0",
            name="fancy_cube",
            position=np.array([0, 0, 1.0]),
            scale=np.array([1.0, 0.5, 0.2]),
            color=np.array([1.0, 0, 0]),
            orientation=np.array([np.cos(theta/2), np.sin(theta/2), 0, 0]),
            linear_velocity=np.array([5.0, 0, 0])
        ))
        return

    # after setup_scene, and after one physics time step
    async def setup_post_load(self):
        self.world.add_physics_callback(callback_name="print_cube_info", callback_fn=self.print_cube_info)
        return
    

    # check cube state callback, for each physics step
    def print_cube_info(self, dt):
        position, orientation = self.cube.get_world_pose()
        linear_velocity = self.cube.get_linear_velocity()
        print(f"Cube {position=}, {orientation=}, {linear_velocity=}")

    async def setup_pre_reset(self):
        return

    async def setup_post_reset(self):
        return

    def world_cleanup(self):
        return
