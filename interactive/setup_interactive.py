import toml
import textwrap
import subprocess
from pathlib import Path
SCRIPT_DIR = Path(__file__).parent

subprocess.run(['bash', str(SCRIPT_DIR/"setup_symlink_builder.sh")])

cfg = toml.load(str(SCRIPT_DIR/"extension.toml"))
modules: list = cfg['python']['module']
module_names = [x['name'].split('.')[-1] for x in modules]
ok = True
for dir in SCRIPT_DIR.glob("*"):
    if dir.is_dir():
        if dir.name not in module_names:
            ok = False
            print(f"Please add following in extension.toml\n\
================================================\n\
[[python.module]]\n\
name = \"isaacsim.examples.interactive.{dir.name}\"\n\
================================================")
if ok:
    print("Complete extension.toml configuration file review!")
else:
    print("Please copy the above configuration into extension.toml")

