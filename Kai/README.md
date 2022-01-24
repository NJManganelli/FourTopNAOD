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
git clone https://github.com/NJManganelli/FourTopNAOD.git FourTopNAOD 
cd FourTopNAOD
git checkout f21bd50687b44463d816aab58ff55821db386aee #Get the commit with all configurations embedded in the crab folder
cd ..
scram b -j4
voms-proxy-init -voms cms --valid 192:00
cd $CMSSW_BASE/src/FourTopNAOD/Kai/crab/NANOv7_NoveCampaign
#cd $CMSSW_BASE/src/FourTopNAOD/Kai/crab/NANOv7_NoveCampaign_addition_v2 #Additional samples
~~~~~~~~~~~~~
### Example submission
~~~~~~~~~~~~~{sh}
cd <This_CMSSW>/src
cmsenv
voms-proxy-init -voms cms --valid 192:00
cd $CMSSW_BASE/src/FourTopNAOD/Kai/crab/NANOv7_Fri13/2017/ttt
crab submit -c crab_cfg_2017_tttt.py
~~~~~~~~~~~~~

### Resubmission
In the event jobs fail, they may be resubmitted with the followin syntax, supposing that 3 jobs in 2018_WJets_SL-HT2500 failed due to hitting the wall clock
~~~~~~~~~~~~~{sh}
crab status -d crab_2018_WJets_SL-HT2500 --verboseErrors 
crab resubmit -d crab_2018_WJets_SL-HT2500 --jobids=7,8,9 --maxjobruntime=2750
~~~~~~~~~~~~~