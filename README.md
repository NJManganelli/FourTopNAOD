# FourTopNAOD
UC Riverside Four Top Analysis in NanoAOD format (2016 validation, 2017 and 2018 data analysis)

Root/Python or Mixed Toolchain:
(DO ONCE:)
(Intall Python 2.7 and recent ROOT release OR CMSSW Release)
	(Case: Standalone)
	       git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git NanoAODTools
	       cd NanoAODTools
	       bash standalone/env_standalone.sh build
	       source standalone/env_standalone.sh
	(Case: CMSSW)
	       source /cvmfs/cms.cern.ch/cmsset_default.sh #LXPLUS
	       source $VO_CMS_SW_DIR/cmsset_default.sh	   #T2_BE MX Machines
	       cmsrel CMSSW_X_Y_Z (9_4_9 tested for 2017 data)
	       cd CMSSW_X_Y_Z/src
	       cmsenv
	       git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git NanoAODTools
	       git clone https://github.com/NJManganelli/FourTopNAOD.git FourTopNAOD
	       scram b -j10 (or package instructions!)


(DO EVERY NEW SESSION:)
        (Case: Standalone)
	       cd NanoAODTools
    	       source standalone/env-standalone.sh
	(Case: CMSSW)
	       cd CMSSW_X_Y_Z/src
	       cmsenv
