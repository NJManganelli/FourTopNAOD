Setup Requirements
Source the cms default environment to enable access to the dasgoclient
Source the LCG stack for software, RDataFrame requires a root version > 6.14, 6.20 recommended
Source the standalone setup scripts for the FourTopNAOD/Kai and PhysicsTools/nanoAOD-tools repositories, i.e.
```
#Source the basic software, example release with gcc800 compiler and ROOT 6.20
source /cvmfs/sft.cern.ch/lcg/views/LCG_97rc4/x86_64-centos7-gcc8-opt/setup.sh

#Get valid grid proxy
voms-proxy-init -voms cms --valid 192:00

#Setup PYTHONPATH for modules to load
source FourTopNAOD/RDF/standalone/env_standalone.sh (or .zsh)

#get KRB5 credentials if eosuser redirector not working (may be issue with registration of grid proxy with EOS
kinit <username>@CERN.CH #kinit <username>@FNAL.GOV

touch /eos/user/<userinitial>/<username>/test.txt
xrdcp root://eosuser.cern.ch//eos/user/<userinitial>/<username>/test.txt xrdtest.txt

#Run the analyzer on just the tttt sample in the ElMu channel
python -u FTAnalyzer.py fill-yields --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory> --include tttt --channel ElMu
python -u FTAnalyzer.py combine-yields --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory> --include tttt --channel ElMu
python -u FTAnalyzer.py fill-histograms --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory> --include tttt --channel ElMu
```