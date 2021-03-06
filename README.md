# FourTopNAOD
UC Riverside Four Top Analysis in NanoAOD format (2016 validation, 2017 and 2018 data analysis)

## RDataFrame Skimming code
### Initial setup (do once from an area where you have access to /cvmfs)
~~~~~~~~~~~~~{sh}
export SCRAM_ARCH=slc7_amd64_gcc830
cmsrel CMSSW_10_2_26
cd CMSSW_10_2_26/src
cmsenv
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
git clone https://github.com/NJManganelli/FourTopNAOD.git FourTopNAOD
scram b -j4
source FourTopNAOD/Kai/standalone/env_standalone.sh build
source FourTopNAOD/RDF/standalone/env_standalone.sh build
~~~~~~~~~~~~~
### RDF Usage (do every time when using anything in the FourTopNAOD/RDF directory; recommend a .bashrc function)
~~~~~~~~~~~~~{sh}
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc830
source /cvmfs/sft.cern.ch/lcg/views/LCG_99/x86_64-centos7-gcc8-opt/setup.sh
#Get authentication tokens where necessary, e.g. voms and kerberos
voms-proxy-init -voms cms --valid 192:00
kinit
cd CMSSW_10_2_26/src/FourTopNAOD/RDF
source standalone/env_standalone.sh
cd skimming
#Run a script that uses the FourTopNAOD/RDF/scripts/nanoframe.py skimming code.
python ../scripts/nanoframe.py --help
sh skimming_example.sh
~~~~~~~~~~~~~
## PostProcessor code
~~~~~~~~~~~~~{sh}
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_18
cd CMSSW_10_2_18/src
cmsenv
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
git clone https://github.com/NJManganelli/FourTopNAOD.git FourTopNAOD
scram b -j4
~~~~~~~~~~~~~
### Getting files with dasgoclient
~~~~~~~~~~~~~{sh}
voms-proxy-init -voms cms
dasgoclient --query="file dataset=/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM"
~~~~~~~~~~~~~
Choose a file from those printed, add an xrootd redirector such as root://cms-xrd-global.cern.ch/
~~~~~~~~~~~~~{sh}
xrdcp root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/0E27F419-ADDE-1E4C-AC0A-130DA36C1FA6.root testfile.root
~~~~~~~~~~~~~

### Running Lepton Scale Factor insertion code
~~~~~~~~~~~~~{sh}
cd FourTopNAOD/Kai
mkdir test
cd test
python ../scripts/LepSFProcessor.py --help
~~~~~~~~~~~~~
For example, we can add the Loose ID SF's for muons and electrons, using the LooseRelIso/LooseID Isolation SF's, with the following ommand line code. If path/to/inputfile_*.root is a globbable path to multipe inputs (or a single input), and output directory 'somedirectory' exists
~~~~~~~~~~~~~{sh}
python ../scripts/LepSFProcessor.py 'path/to/testfile.root' --outDirectory . --muon_ID LooseID --muon_ISO LooseRelIso/LooseID --electron_ID LooseID --era 2017 --maxEntries 2500
~~~~~~~~~~~~~

### Running Stitching code for flagging
~~~~~~~~~~~~~{sh}
cd FourTopNAOD/Kai
mkdir test
cd test
python ../scripts/StitchingProcessor.py --help
~~~~~~~~~~~~~
Run over testfile with dilepton nominal and single lepton filtered setting
~~~~~~~~~~~~~{sh}
python ../scripts/StitchFlagProcessor.py testfile.root --outDirectory . --era 2017 --channel DL --mode Flag --maxEntries 3000 --source Nominal --fillHists --weight 0.27
python ../scripts/StitchFlagProcessor.py testfile.root --outDirectory . --era 2017 --channel SL --mode Flag --maxEntries 3000 --source Filtered --fillHists --weight 0.15
~~~~~~~~~~~~~
## New instructions

### Setting up NanoAODv5 Production
~~~~~~~~~~~~~{sh}
export SCRAM_ARCH=slc7_amd64_gcc700
mkdir NanoProduction && cd NanoProduction
cmsrel CMSSW_10_2_15
cd CMSSW_10_2_15/src
cmsenv
git cms-init
git cms-merge-topic -u pastika:AddAxis1_1026
git clone https://github.com/susy2015/TopTagger.git
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
git clone https://github.com/NJManganelli/FourTopNAOD.git FourTopNAOD
scram b -j4
mkdir -p ${CMSSW_BASE}/src/TopTagger/TopTagger/data
getTaggerCfg.sh -o -n -t DeepResolved_DeepCSV_GR_noDisc_Release_v1.0.0 -d $CMSSW_BASE/src/TopTagger/TopTagger/data
~~~~~~~~~~~~~ 

### Attempt to fix resolvedTagger jet source
in TopTagger/TopTagger/python/resolvedTagger_cff.py, replace instances of slimmedJets with upatedJets, like so:
~~~~~~~~~~~~~ 
inputJetCollection = process.slimmedJetsWithUserData.src
~~~~~~~~~~~~~ 
with
~~~~~~~~~~~~~ 
inputJetCollection = process.updatedJetsWithUserData.src
~~~~~~~~~~~~~ 

### cmsDriver commands for NanoAOD Production
2017:
~~~~~~~~~~~~~{sh}
cmsDriver.py myNanoProdMc2017 -s NANO --mc --eventcontent NANOAODSIM --datatier NANOAODSIM  --no_exec  --conditions 102X_mc2017_realistic_v7 --era Run2_2017,run2_nanoAOD_94XMiniAODv2 --customise_commands="process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))"

cmsDriver.py myNanoProdData2017 -s NANO --data --eventcontent NANOAOD --datatier NANOAOD  --no_exec  --conditions 102X_dataRun2_v11 --era Run2_2017,run2_nanoAOD_94XMiniAODv2 --customise_commands="process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))"
~~~~~~~~~~~~~ 
### Customizing with Resolved TopTagger (WIP)
Add the following lines in the custoization section of the cmsRun configuration produced by cmsDriver:
~~~~~~~~~~~~~
from TopTagger.TopTagger.resolvedTagger_cff import customizeResolvedTagger, customizeResolvedTaggerAllCanidiates, customizeResolvedTaggerAllCanidiates, customizeResolvedTaggerAndVariables, customizeResolvedTaggerAllCanidiatesAndVariables

#call to customisation function customizeResolvedTagger imported from TopTagger.TopTagger.resolvedTagger_cff
process = customizeResolvedTagger(process)
#process = customizeResolvedTaggerAllCanidiates(process)
~~~~~~~~~~~~~ 

### Old Notes and Instructions
Please read here:
https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD#How_to_check_out_the_code_and_pr
cmsDriver.py can be used to create barebones configurations, as in documentation above, for producing NanoAOD from Mini

Centrally Produced NanoAOD Campaigns:
80X MC + data: https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=%2F*%2F*05Feb2018*%2FNANOAOD*
80X Run2016 data: https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=%2F*%2F*05Feb2018*%2FNANOAOD
94X MC: https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=%2F*%2F*12Apr2018*%2FNANOAODSIM
94X data: https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=%2F*%2F*31Mar2018*%2FNANOAOD
94X data not necessarily the most recently processed!

Note about GitHub source code:
There are two collections of NanoAOD source code; one is maintained within cms-sw, and the other within cms-nanoAOD.
The latter is the collection of tools for processing NanoAOD data in a postprocessor framework.
https://github.com/cms-sw/cmssw/tree/master/PhysicsTools/NanoAOD
https://github.com/cms-nanoAOD/nanoAOD-tools.git

Root/Python or Mixed Toolchain:
(DO ONCE:)
(Intall Python 2.7 and recent ROOT release OR CMSSW Release)
	(Case: Standalone)
	       git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git NanoAODTools #The postprocessing tools!
	       git clone https://github.com/NJManganelli/FourTopNAOD.git FourTopNAOD #this code
	       cd NanoAODTools
	       bash standalone/env_standalone.sh build
	       source standalone/env_standalone.sh
	(Case: CMSSW)
	       source /cvmfs/cms.cern.ch/cmsset_default.sh #LXPLUS
	       source $VO_CMS_SW_DIR/cmsset_default.sh	   #T2_BE MX Machines
	       cmsrel CMSSW_X_Y_Z (9_4_9 tested for 2017 data)
	       cd CMSSW_X_Y_Z/src
	       cmsenv
	       git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git NanoAODTools #The postprocessing tools!
	       git clone https://github.com/NJManganelli/FourTopNAOD.git FourTopNAOD #this code
	       scram b -j10 (or package instructions!)


(DO EVERY NEW SESSION:)
        (Case: Standalone)
	       cd NanoAODTools
    	       source standalone/env-standalone.sh
	(Case: CMSSW)
	       cd CMSSW_X_Y_Z/src
	       cmsenv

####################################
###### Using Python Notebooks ######
####################################
A python notebook can be started by opening another terminal, and executing the command:
ssh -L localhost:4444:localhost:4444 <NiceLogin>@lxplus.cern.ch
Establishing cmsenv (new session) as above
Getting grid proxy (if accessing root files stored on servers, using CRAB, etc):
voms-proxy-init -voms cms
Navigate to:
/path/to/notebook/directory
execute:
jupyter-notebook --no-browser --port=4444 --ip=127.0.0.1
When it produces a token, paste in your webbrowser to connect to homepage, and open one of the notebooks or start a new one

########################
###### Stable Tag ######
########################
A stable tag of this release can be grabbed by, following the clone of this repository, checking out a stable tag and simultaneously creating a branch

git checkout tags/<Tag-version> -b branchedFrom<Tag-version>

Tag-Versions:
v0.2	- demonstrates accessing collections, triggers, MET filters, etc. in basicAccessAndLoop.ipynb and dataTrigAndJson.ipynb