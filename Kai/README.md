# Fri13 Campaign
For production of NanoAOD skims with central corrections (PU Reweighting, JES, golden JSON application, btag SF insertion (M, shape), dilepton trigger and loose lepton selection, loose jet and pseudo-HT selection)

## Prepare code for submission
~~~~~~~~~~~~~{sh}
export SCRAM_ARCH=slc7_amd64_gcc700
mkdir Fri13Campaign && cd Fri13Campaign
cmsrel CMSSW_10_2_24_patch1
cd CMSSW_10_2_24_patch1/src
cmsenv
git clone https://github.com/NJManganelli/nanoAOD-tools.git PhysicsTools/NanoAODTools --branch Fri13
git clone https://github.com/NJManganelli/FourTopNAOD.git FourTopNAOD --branch Fri13
scram b -j4
voms-proxy-init -vomc cms --valid 192:00
cd $CMSSW_BASE/src/FourTopNAOD/Kai/crab/NANOv7_Fri13
~~~~~~~~~~~~~
### Example submission
~~~~~~~~~~~~~{sh}
cd <This_CMSSW>/src
cmsenv
voms-proxy-init -vomc cms --valid 192:00
cd $CMSSW_BASE/src/FourTopNAOD/Kai/crab/NANOv7_Fri13/2017/ttt
crab submit -c crab_cfg_2017_tttt.py
~~~~~~~~~~~~~
