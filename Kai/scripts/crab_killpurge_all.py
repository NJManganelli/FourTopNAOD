#!/usr/bin/env python
import os, sys, datetime, subprocess
from glob import glob
# dirs = glob("./crab_*")
dirs = [] #Don't blindly enable this command, make myself add a list or edit it to work, first
dirs = [f.replace("./", "") for f in dirs if "." not in f.replace("./", "")]
for f in dirs:
    #--cache optoin only purges the scheduler cache, which is the important goal. disabling it will purge both the remote cache and the local cache (meaning it breaks crab commands on the directory from that point forward
    cmd = "crab kill -d {0:s} && crab purge -d {0:s} --cache > killpurge_{1:s}.log".format(f.replace("./", ""), f.replace("crab_", ""))
    print(cmd)
    # subprocess.Popen(args="print '{}'".format(cmd), shell=True, executable="/bin/zsh", env=dict(os.environ))
    subprocess.Popen(args="{}".format(cmd), shell=True, executable="/bin/zsh", env=dict(os.environ)).wait()
