# -*- coding: utf-8 -*-
# Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
'''
@File    : getting_started_kuavo.py
@Time    : 2025/04/15 19:38:34
@Author  : wty-yy
@Version : 1.0
@Blog    : https://wty-yy.github.io/
@Desc    : None
'''

from isaacsim.simulation_app import SimulationApp
simulation_app = SimulationApp({"headless": False})  # start the simulation app, with GUI open

import torch
import os, sys
import argparse
import numpy as np
from pathlib import Path
from isaacsim.core.api import World
from isaacsim.core.prims import Articulation
from isaacsim.core.utils.stage import add_reference_to_stage, get_stage_units, get_current_stage
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.core.api.scenes import Scene
import omni.replicator.core as rep

ISAAC_PATH = Path(os.environ['ISAAC_PATH'])
sys.path.append(str(ISAAC_PATH/"exts/isaacsim.robot_setup.assembler/isaacsim"))
from robot_setup.assembler import RobotAssembler

RESOURCES_PATH = Path(__file__).parents[1] / "resources"
USE_CUDA = False

asset_path = RESOURCES_PATH / "kuavo42.usd"
legged_mapping = {
    'knee': 'leg_*4_joint',
    'hip': 'leg_*3_joint',
    'ankle': 'leg_*5_joint'
}

def trun_sin(x, min: float, max: float):
    return (np.sin(x) + 1) / 2 * (max - min) + min

legged_dof_pos_func = {
    'hip': lambda phi: trun_sin(2 * np.pi * phi, -0.7854, -0),
    'knee': lambda phi: trun_sin(2 * np.pi * (phi+3/16), 0.5236, 1.7453),
    'ankle': lambda phi: trun_sin(2 * np.pi * (phi-3/8), -0.4363, 0.0873)
}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix-base-link", default=True, type=lambda x: x in ['1', 'true', 'True'],
        help="If true, fix base link to debug gait")
    args = parser.parse_args()
    return args


class Runner:
    def __init__(self, args):
        self.hz = 1000
        self.world = World(physics_dt=1/self.hz, stage_units_in_meters=1.0, backend='torch', device='cuda' if USE_CUDA else 'cpu')
        self.scene = Scene()
        self.scene.add_ground_plane(color=np.array([1.0, 1.0 , 1.0]))
        rep.create.light(rotation=(0, 45, 0), light_type="distant", parent="/World/groundPlane")
        set_camera_view(
            eye=[0.0, 4.0, 1.5], target=[0.00, 0.00, 1.00], camera_prim_path="/OmniverseKit_Persp"
        )  # set camera view

        self.prim_bot_path = "/World/bot"
        add_reference_to_stage(usd_path=str(asset_path), prim_path=self.prim_bot_path)  # add robot to stage
        self.bot = Articulation(prim_paths_expr=self.prim_bot_path, name='kauvo')
        self.bot.set_world_poses(positions=torch.tensor([[0.0, 0.0, 0.1]]) / get_stage_units())
        if args.fix_base_link:
            self.add_fixed_joint(self.prim_bot_path+"/links/base_link")
        self.world.reset()

        self.last_dof_pos = [0] * len(self.bot.dof_names)
        self.cycle_time = 0.64

    def run(self):
        while True:
            phi = self.world.current_time / self.cycle_time % 1
            for key in ['knee', 'hip', 'ankle']:
                for idx, name in zip((0, 1), ('l', 'r')):
                    rad = legged_dof_pos_func[key]((phi + 0.5 * idx) % 1)
                    dof_idx = self.bot.get_dof_index(legged_mapping[key].replace('*', name))
                    self.last_dof_pos[dof_idx] = rad
            if self.world.is_simulating():
                self.bot.set_joint_position_targets(torch.tensor([self.last_dof_pos], dtype=torch.float))
            self.world.step(render=True)

    def add_fixed_joint(self, link_path):
        robot_assembler = RobotAssembler()
        robot_assembler.create_fixed_joint(
            prim_path=self.prim_bot_path,
            target0="/World",
            target1=link_path,
        )

    

if __name__ == '__main__':
    args = parse_args()
    runner = Runner(args)
    runner.run()
    simulation_app.close()
