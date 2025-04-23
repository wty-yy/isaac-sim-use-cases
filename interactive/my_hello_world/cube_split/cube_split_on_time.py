import omni.usd
import numpy as np
from isaacsim.core.api.world import World
from isaacsim.core.api.scenes import Scene
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.examples.interactive.base_sample import BaseSample
from pxr import UsdLux, Gf, Sdf
from isaacsim.core.utils.prims import delete_prim, get_prim_at_path
from isaacsim.core.utils.viewports import set_camera_view
from scipy.spatial.transform import Rotation as R
import omni.timeline


def get_spatial_sphere_vectors(y_delta_degree=20, y_num=None, z_delta_degree=20, z_num=None):
    top = np.array([0, 0, 1])
    rot_y = R.from_euler('y', y_delta_degree, degrees=True)
    rot_z = R.from_euler('z', z_delta_degree, degrees=True)
    if y_num is None:
        y_num = 180 // y_delta_degree
    if z_num is None:
        z_num = 360 // z_delta_degree
    xs = [top]
    for i in range(y_num):
        xs.append(rot_y.apply(xs[-1]))
        for _ in range(z_num):
            xs.append(rot_z.apply(xs[-1]))
    xs = np.array(xs).round(4)
    xs = np.unique(xs, axis=0)
    return xs

class SingleCube:
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
        self.scale = scale
        self.default_velocity = np.linalg.norm(line_velocity)
        self.cube = DynamicCuboid(
            prim_path=self.prim_path,
            name=f"cube{idx}",
            position=np.array(position),
            scale=np.array([scale] * 3),
            color=np.array(color),
            linear_velocity=np.array(line_velocity)
        )
        self.scene.add(self.cube)
        self.create_time = self.world.current_time
        self.timeline = omni.timeline.get_timeline_interface()
    
    def remove(self):
        if get_prim_at_path(self.prim_path):
            delete_prim(self.prim_path)
    
    def deactivate(self):
        self.timeline.stop()
        self.stage.GetPrimAtPath(self.prim_path).SetActive(False)
        self.timeline.play()

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
        light.CreateIntensityAttr(5e5)
        light.AddTranslateOp().Set(Gf.Vec3f(10, 0, 10))
        light = UsdLux.SphereLight.Define(self.stage, "/World/Lights/SphereLight2")
        light.CreateIntensityAttr(5e5)
        light.AddTranslateOp().Set(Gf.Vec3f(-10, 0, 10))

        self.cubes: set[SingleCube] = set()
        self.cubes.add(self.add_split_cube(
            scale=4, position=np.array([0, 0, 2]), color=np.random.rand(3), line_velocity=np.array([0, 0, 10])
        ))
        return
    
    def debug_add(self):
        self.add_split_cube(
            np.random.uniform(0.5, 2.0), position=np.random.uniform(0, 2, (3,)),
            color=np.random.rand(3), line_velocity=np.array([0, 0, np.random.rand()])
        )
    
    def add_split_cube(self, scale, position, color, line_velocity):
        cube = SingleCube(
            self.world, self.scene, self.stage, self.idx,
            scale=scale, position=position, color=color, line_velocity=line_velocity
        )
        self.idx += 1
        return cube

    # after setup_scene, and after one physics time step
    async def setup_post_load(self):
        set_camera_view(eye=(30, 30, 30), target=(0, 0, 0))
        self.world.add_physics_callback("physics_step", self.physics_step)
        return
    
    def update_split(self, cube: SingleCube):
        if cube.cube.is_valid():
            vel = np.linalg.norm(cube.cube.get_linear_velocity())
        if cube.scale <= 1: return
        if cube.create_time - self.world.current_time > 5 or vel < 0.5:
            pos, _ = cube.cube.get_world_pose()
            base_vec = get_spatial_sphere_vectors(y_delta_degree=45, z_delta_degree=90)
            # print(base_vec.shape)
            for vec in base_vec:
                lin_vel = vec * cube.default_velocity/2
                self.cubes.add(self.add_split_cube(cube.scale/2, pos+vec*cube.scale/2, np.random.rand(3), lin_vel))
            self.cubes.remove(cube)
            # print("DEACTIVATE!!!!!!!!!")
            cube.deactivate()
            # print("REMOVE!!!!!!!!!")
            # cube.remove()
    
    def physics_step(self, dt):
        self.cubes_copy = self.cubes.copy()
        # print(len(self.cubes_copy))
        for cube in self.cubes_copy:
            self.update_split(cube)

    async def setup_pre_reset(self):
        return

    async def setup_post_reset(self):
        return

    def world_cleanup(self):
        return
