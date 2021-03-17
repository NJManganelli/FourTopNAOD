#!/usr/bin/env python
import os, sys, datetime, subprocess
from glob import glob
cfg_files = glob("./crab_cfg_*")
cfg_files = [f for f in cfg_files if ".pyc" not in f]
for f in cfg_files:
    cmd = "crab submit -c {0:s} > submission_{1:s}.log".format(f.replace("./", ""), f.replace("crab_cfg_", "").replace(".py","").replace("./", ""))
    # subprocess.Popen(args="print '{}'".format(cmd), shell=True, executable="/bin/zsh", env=dict(os.environ))
    subprocess.Popen(args="{}".format(cmd), shell=True, executable="/bin/zsh", env=dict(os.environ))