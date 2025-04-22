import numpy as np
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.api.scenes import Scene
from isaacsim.core.utils.viewports import set_camera_view
import omni.usd
from isaacsim.core.api.objects import DynamicCuboid
from pxr import UsdLux, Sdf, Gf, UsdGeom, UsdPhysics, PhysxSchema, UsdShade, Tf
from scipy.spatial.transform import Rotation as R

class PXRDemo(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        self.world = self.get_world()
        self.scene: Scene = self.world.scene
        # self.scene.add_default_ground_plane()
        # self.scene.add_ground_plane()
        self.stage = omni.usd.get_context().get_stage()
        # 手动创建平行光源
        # light_path = "/World/DistantLight"
        # light = UsdLux.DistantLight.Define(self.stage, Sdf.Path(light_path))
        # light.CreateIntensityAttr(2e5)  # 设置光照强度
        # light.CreateColorAttr(Gf.Vec3f(0.2, 0.1, 0.5))  # 设置RGB颜色
        # light.AddRotateXYZOp().Set(Gf.Vec3f(-45, 0, 0))  # 设置旋转
        # 手动创建聚光灯源
        light_path = "/World/SphereLight"
        light = UsdLux.SphereLight.Define(self.stage, Sdf.Path(light_path))  # 初始化SphereLight实例
        light.CreateIntensityAttr(2e5)  # 设置光照强度
        light.CreateColorAttr(Gf.Vec3f(0.1, 0.7, 0.7))  # 设置RGB颜色
        light.AddScaleOp().Set(Gf.Vec3f(3, 1, 3))  # 设置缩放
        light.AddTranslateOp().Set(Gf.Vec3f(2, 0, 2))  # 设置坐标

        # 创建平面
        plane_path = "/World/Plane"
        plane = UsdGeom.Plane.Define(self.stage, Sdf.Path(plane_path))
        plane.CreateLengthAttr(10)
        plane.CreateWidthAttr(20)
        plane.CreateAxisAttr('Z')  # Or UsdGeom.Tokens.[x,y,z]
        UsdPhysics.CollisionAPI.Apply(plane.GetPrim())

        # 创建Cube不推荐, 可能产生穿模
        cube_path = "/World/Cube"
        cube = UsdGeom.Cube.Define(self.stage, Sdf.Path(cube_path))
        cube.AddScaleOp().Set(Gf.Vec3f(1, 0.5, 1))
        cube.AddTranslateOp().Set(Gf.Vec3f(0, 0, 4))
        cube.AddRotateXYZOp().Set(Gf.Vec3f(-45, 0, 0))  # 设置旋转
        cube.CreateDisplayColorAttr([Gf.Vec3f(0, 1, 0)])
        UsdPhysics.CollisionAPI.Apply(cube.GetPrim())
        UsdPhysics.RigidBodyAPI.Apply(cube.GetPrim())

        # 推荐使用如下方法创建Cube
        # euler_angles = [0, 45, 30]
        # quat = R.from_euler('xyz', euler_angles, degrees=True).as_quat()[[3, 0, 1, 2]]
        # cube1 = DynamicCuboid(
        #     prim_path="/World/Cube1", name='Cube1', color=np.array([0, 1, 0]),
        #     position=np.array([0, 0, 4]), scale=np.array([2, 3, 1]),
        #     orientation=np.array(quat)
        # )
        # self.scene.add(cube1)

        cube2 = DynamicCuboid(prim_path="/World/Cube2", name='Cube2', color=np.array([0, 0, 1]))
        self.scene.add(cube2)

        cube3 = DynamicCuboid(prim_path="/World/Cube3", name='Cube3', color=np.array([1, 0, 0]), position=np.array([0, 0, 2]))
        self.scene.add(cube3)
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
