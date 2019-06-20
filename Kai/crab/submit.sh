#!/bin/zsh
for y in crab_cfg_ElEl_B_2017.py crab_cfg_ElEl_C_2017.py crab_cfg_ElEl_D_2017.py crab_cfg_ElEl_E_2017.py crab_cfg_ElMu_B_2017.py crab_cfg_ElMu_C_2017.py crab_cfg_ElMu_D_2017.py crab_cfg_ElMu_E_2017.py crab_cfg_MuMu_B_2017.py crab_cfg_MuMu_C_2017.py crab_cfg_MuMu_D_2017.py crab_cfg_MuMu_E_2017.py; eval crab submit -c ${y}
