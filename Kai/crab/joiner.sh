#!/bin/zsh
x=(./crab_ElMu_F_2017/results/hist_*.root)
eval hadd /eos/home-n/nmangane/SWAN_projects/CloudNano/ElMu_F_2017_hist.root ${^x}
