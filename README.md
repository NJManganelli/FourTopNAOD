# FourTopNAOD
UC Riverside Four Top Analysis in NanoAOD format (2016 validation, 2017 and 2018 data analysis)

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
