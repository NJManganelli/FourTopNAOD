# FourTopNAOD
UC Riverside Four Top Analysis in NanoAOD format (2016 validation, 2017 and 2018 data analysis)

	#CMSSW ToolChain not yet supported:
	#(DO ONCE:)
	#To set up a CMSSW release (94X for 2017 data and MC):
	#source $VO_CMS_SW_DIR/cmsset_default.sh #bash shell on T2 Belgium Mx machines (or .csh)
	##source /cvmfs/cms.cern.ch/cmsset_default.sh #bash shell on LX Plus machines (or .csh)
	#export SCRAM_ARCH=slc6_amd64_gcc630 #If server still runs Scientific Linux (CERN) 6, check by inspecting /etc/system-release
	#cmsrel CMSSW_X_Y_Z #Example 94X release: CMSSW_9_4_9
	#
	#cd $CMSSW_BASE/src
	#cmsenv
	#
	#git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git NanoAODTools
	#git clone 
	#
	#
	#(DO EVERY NEW SESSION:)
	#cd CMSSW_X_Y_Z/src #Release you chose earlier
	#cmsenv

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
