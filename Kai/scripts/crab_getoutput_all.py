#!/usr/bin/env python
import os, sys, datetime, subprocess
from glob import glob
dirs = glob("./crab_*")
dirs = [f.replace("./", "") for f in dirs if "." not in f.replace("./", "")]
for f in dirs:
    cmd = "crab getoutput -d {0:s} > getoutput_{1:s}.log".format(f.replace("./", ""), f.replace("crab_", ""))
    print(cmd)
    # subprocess.Popen(args="print '{}'".format(cmd), shell=True, executable="/bin/zsh", env=dict(os.environ))
    subprocess.Popen(args="{}".format(cmd), shell=True, executable="/bin/zsh", env=dict(os.environ))
