import numpy as np
from isaacsim.core.api.scenes import Scene
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController


class FrankaPickAndPlace(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        self.world = self.get_world()
        self.world.scene.add_default_ground_plane()
        self.scene: Scene = self.world.scene
        self.franka: Franka = self.scene.add(Franka(prim_path="/World/Franka"))
        self.cube: DynamicCuboid = self.scene.add(
            DynamicCuboid(
                prim_path="/World/cube",
                position=np.array([0.3 , 0.3, 0.3]),
                scale=np.array([0.05, 0.05, 0.05]),
                color=np.array([1.0, 0, 0])
            )
        )
        return

    # after setup_scene, and after one physics time step
    async def setup_post_load(self):
        self.controller = PickPlaceController(
            name="controller",
            gripper=self.franka.gripper,
            robot_articulation=self.franka
        )
        self.world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        current_joint_position = self.franka.get_joint_positions()
        self.franka.gripper.set_joint_positions(self.franka.gripper.joint_opened_positions)
        # print(f"{current_joint_position=}")
        return
    
    def physics_step(self, dt):
        cube_position, _ = self.cube.get_world_pose()
        goal_position = np.array([-0.3, -0.3, 0.0515/2.0])
        current_joint_position = self.franka.get_joint_positions()
        # print(f"{current_joint_position=}")
        actions = self.controller.forward(
            picking_position=cube_position,
            placing_position=goal_position,
            current_joint_positions=current_joint_position
        )
        self.franka.apply_action(actions)
        if self.controller.is_done():
            self.world.pause()

    async def setup_pre_reset(self):
        return

    async def setup_post_reset(self):
        self.controller.reset()
        self.franka.gripper.set_joint_positions(self.franka.gripper.joint_opened_positions)
        await self.world.play_async()
        return

    def world_cleanup(self):
        return
