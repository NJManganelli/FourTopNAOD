# Hitchhiker's Guide to the NanoAOD
Examples created for NanoAOD processing using the standard PostProcessor framework.

Note about GitHub source code:
There are two collections of NanoAOD source code; one is maintained within cms-sw, and the other within cms-nanoAOD.
The latter is the collection of tools for processing NanoAOD data in a postprocessor framework, and the former contiains code for producing NanoAOD from MiniAOD.
1. <https://github.com/cms-sw/cmssw/tree/master/PhysicsTools/NanoAOD>
2. <https://github.com/cms-nanoAOD/nanoAOD-tools.git>

## Installing within CMSSW (For Python/ROOT functionality)
### DO ONCE:
```bash
	       source /cvmfs/cms.cern.ch/cmsset_default.sh #LXPLUS
	       source $VO_CMS_SW_DIR/cmsset_default.sh	   #T2_BE MX Machines
	       cd $WORK
	       cmsrel CMSSW_9_4_9
	       cd CMSSW_9_4_9/src
	       cmsenv
	       git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git NanoAODTools #The postprocessing tools!
	       git clone https://github.com/NJManganelli/FourTopNAOD.git FourTopNAOD #this code
	       scram b -j4
```


### DO EVERY NEW SESSION:
```bash
cd $WORK/CMSSW_X_Y_Z/src
cmsenv
```

## Intro Examples
```bash
cd StandaloneExamples/Book1
python CH01.py
python CH02.py
...
```

## Bigger Examples
```bash
cd StandaloneExamples/Book2
python CH01.py
```

## Using Python Notebooks
A python notebook can be started by opening another terminal, and executing the commands:
```bash
ssh -L localhost:4444:localhost:4444 <NiceLogin>@lxplus.cern.ch
cd path/to/CMSSW_X_Y_Z/src
cmsenv
voms-proxy-init -voms cms
cd path/to/notebook/directory
jupyter-notebook --no-browser --port=4444 --ip=127.0.0.1
```
When it produces a token, paste in your webbrowser to connect to homepage, and open one of the notebooks or start a new one

## PostProcessor Encyclopedia
Standalone.ipynb is a Standalone Jupyter Notebook that contains significant commentary and options. It dumps event information for leptons, jets, etc. 