# Interactive用例
## 使用方法
### 初始配置
第一次或创建新的项目时，需执行`setup_interactive.py`，这会进行如下操作，使我们自定义的interactive代码让插件能够找到：
1. 调用`setup_symlink_builder.sh`创建symlink
    1. 遍历`interactive/`文件夹下的所有子文件夹symlink到`$ISAAC_PATH/exts/isaacsim.examples.interactive/isaacsim/examples/interactive`文件夹下
    2. 将`$ISAAC_PATH/exts/isaacsim.examples.interactive/config/extension.toml`配置文件symlink到`interactive/`文件夹下
2. Python脚本自动检查配置文件中是否包含自定义的项目，如果不存在则会给出报错，需要手动将额外的配置粘贴到`extension.toml`文件中

### 代码启动方法
1. `./isaac-sim.sh`打开IsaacSim
2. 点击上方Window -> Examples -> Robotics Examples，下方栏中找到Robot Examples
3. 例如`my_hello_world`项目，在左侧点击`MY_USE_CASES`，点击中间`My Hello World`，点击右侧`LOAD`按钮即可

每次修改项目代码保存后，Robotics Examples中立马就会更新，我们只需要再重新点击`LOAD`即可看到修改后的代码
