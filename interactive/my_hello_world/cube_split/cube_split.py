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
from isaacsim.sensors.camera import Camera
import isaacsim.core.utils.numpy.rotations as rot_utils
import os, cv2
from pathlib import Path

path_video = Path(f"{os.getenv('HOME')}/Videos/isaacsim")
path_video.mkdir(exist_ok=True)
path_video /= "cube_split.avi"

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
        light.CreateIntensityAttr(1e7)
        light.AddTranslateOp().Set(Gf.Vec3f(40, 0, 40))
        # light.CreateColorAttr(Gf.Vec3f(1, 182/255, 193/255))
        light = UsdLux.SphereLight.Define(self.stage, "/World/Lights/SphereLight2")
        light.CreateIntensityAttr(1e7)
        light.AddTranslateOp().Set(Gf.Vec3f(-40, 0, 40))
        # light.CreateColorAttr(Gf.Vec3f(1, 182/255, 193/255))

        ts = np.linspace(0, 2 * np.pi, 15)
        ys = 16 * np.sin(ts) ** 3
        zs = 13 * np.cos(ts) - 5 * np.cos(2*ts) - 2 * np.cos(3*ts) - np.cos(4*ts)
        zs -= zs.min()
        base_vec = get_spatial_sphere_vectors(y_delta_degree=45, z_delta_degree=90)
        for (y, z) in zip(ys, zs):
            pos = np.array([0, y, z])
            for vec in base_vec:
                lin_vel = vec * 5
                self.add_split_cube(1, pos+vec*1, np.random.rand(3), lin_vel)
        
        # width, height, fps = 512, 288, 30
        width, height, fps = 1920, 1080, 60
        self.camera = Camera(
            "/World/Camera", position=(150, 0, 20), resolution=(width, height), frequency=fps,
            orientation=rot_utils.euler_angles_to_quats(np.array([0, 2, 180]), degrees=True)
        )

        print(f"[INFO] write video to {path_video}")
        self.writer = cv2.VideoWriter(str(path_video), cv2.VideoWriter_fourcc(*'XVID'), fps=fps, frameSize=(width, height))

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
        # set_camera_view(eye=(60, 0, 20), target=(0, 0, 15))
        self.camera.initialize()
        self.world.add_render_callback("render_step", self.render_step)
        return

    def render_step(self, dt):
        img = self.camera.get_rgb()
        print(img.shape)
        if not len(img): return
        # cv2.imwrite("/home/yy/Programs/isaac-sim-standalone@4.5.0/isaac-sim-use-cases/interactive/my_hello_world/cube_split/1.png", img[..., ::-1])
        if self.writer:
            self.writer.write(img[...,::-1])
        # plt.imshow(self.camera.get_rgb())
        # plt.savefig(, dpi=100)
        # plt.close()

    async def setup_pre_reset(self):
        self.writer.release()
        self.writer = None
        return

    async def setup_post_reset(self):
        return

    def world_cleanup(self):
        return
