import numpy as np
from isaacsim.core.api.scenes import Scene
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.robots import Robot
from isaacsim.core.api.controllers.articulation_controller import ArticulationController, ArticulationAction
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
import time
import carb


class MyHelloJetbot(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):

        self.world = self.get_world()
        self.world.scene.add_default_ground_plane()
        self.scene: Scene = self.world.scene
        assets_root_path = get_assets_root_path()
        asset_path = assets_root_path + "/Isaac/Robots/Jetbot/jetbot.usd"
        self.robot_prim_path = "/World/Jetbot"
        add_reference_to_stage(usd_path=asset_path, prim_path=self.robot_prim_path)
        self.jetbot: Robot = self.scene.add(Robot(prim_path=self.robot_prim_path, name="Jetbot"))
        return

    # after setup_scene, and after one physics time step
    async def setup_post_load(self):
        print(f"{self.jetbot.num_dof=}, {self.jetbot.get_joint_positions()}")
        print(f"{self.jetbot.dof_names=}")
        self.jetbot_controller: ArticulationController = self.jetbot.get_articulation_controller()
        self.world.add_physics_callback("Sending actions", callback_fn=self.send_robot_actions)
        kp, kd = self.jetbot_controller.get_gains()
        print(f"{kp=}, {kd=}")
        self.diff_controller = WheelBasePoseController(
            name="diff_controller",
            open_loop_wheel_controller=DifferentialController(
                name="simple_controller", wheel_radius=0.03, wheel_base=0.1125
            ),
            is_holonomic=False
        )
        return
    
    def send_robot_actions(self, dt):
        # if self.world.current_time > 5: return
        # self.jetbot_controller.apply_action(ArticulationAction(
        #     joint_velocities=[0, 5 * np.random.rand()],
        # ))
        position, orientation = self.jetbot.get_world_pose()
        self.jetbot_controller.apply_action(self.diff_controller.forward(
            start_position=position,
            start_orientation=orientation,
            goal_position=np.array([0.8, 0.8])
        ))

    async def setup_pre_reset(self):
        return

    async def setup_post_reset(self):
        return

    def world_cleanup(self):
        return
