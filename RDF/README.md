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

#Tag v0.8 workflow

#The analysis directory needs to be writeable by you after kinit/voms proxy are run
#If necessary, run the bookkeeping step to populate the splitProcess information for e.g. TTToSemiLeptonic*, TTTo2L2Nu* samples
python -u FTAnalyzer.py bookkeeping --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory> --source <sourcekey> --include <split-process-1> <split-process-2> ...
python -u FTAnalyzer.py bookkeeping --analysisDirectory /eos/user/n/nmangane/analysis/TEST --source NANOv5 --include tt_DL-GF tt_DL tt_SL-GF tt_SL

#Run the btagging yields and then combine them for later stages
#Note, an explicit channel is necessary, i.e ElMu MuMu ElEl
python -u FTAnalyzer.py fill-yields --analysisDirectory /eos/user/n/nmangane/analysis/TEST --channel ElMu
python -u FTAnalyzer.py combine-yields --analysisDirectory /eos/user/n/nmangane/analysis/TEST --channel ElMu

#Fill the histograms
python -u FTAnalyzer.py fill-histograms --analysisDirectory /eos/user/n/nmangane/analysis/TEST --channel ElMu

#Manually handle the output combination, note that the file in "All" should be the hadd of ElMu, MuMu, and ElEl channels if they're all produced
cd /eos/user/n/nmangane/analysis/TEST/Histograms
mkdir All
cd ElMu
hadd -f ../All/2017___Combined.root 2017___ttWH.root 2017___tt_SL-GF.root 2017___ttbb_SL-GF_fr.root 2017___ttother_SL-GF_fr.root 2017___tt_DL-GF.root 2017___ttother_DL-GF_fr.root 2017___ttbb_DL-GF_fr.root 2017___ST_tbarW.root 2017___ttWZ.root 2017___tttt.root 2017___ttWJets.root 2017___ttother_DL_nr.root 2017___tt_DL.root 2017___ttother_DL_fr.root 2017___ttbb_DL_fr.root 2017___ttbb_DL_nr.root 2017___ttHH.root 2017___ttWW.root 2017___ST_tW.root 2017___DYJets_DL.root 2017___ttZH.root 2017___ttZJets.root 2017___ttH.root 2017___tttW.root 2017___ttZZ.root 2017___tt_SL.root 2017___ttother_SL_nr.root 2017___ttbb_SL_nr.root 2017___ttbb_SL_fr.root 2017___ttother_SL_fr.root 2017___tttJ.root 2017___ElMu.root

#Finally, run the plotting script using plotcards and legendcards. Parsing of histograms is done through a combination of the key for a "Plot_" in the plotcard
#and the "Names" inside the legendcard 'Categories', which are in turn combined into the 'Supercategories' which are actually stacked/plotted. The Canvas containing potentially
#several histograms points to plotcards. Optional parameters allow for rebinning (variable or nBin), changing labels, etc. Some of these are still WIP. 
#Methods exist inside Plotting.py to generate default plotcards using parameters for channel, variables, categories, etc. but these are not yet exposed to the CL-interface
python Plotting.py plot-histograms -d /eos/user/n/nmangane/analysis/TEST --era 2017 -f pdf -c ElMu -p 'jsons/v0.8/Event_All_2pB.json' -l 'jsons/v0.8/ElMuLegend.json'

#Looping through many such categories, channels, etc using (zsh) loops
for d in Event MET El Mu Jet; for b in 0pB 1pB 2pB; for c in MuMu_ElMu MuMu; do python Plotting.py plot-histograms -d /eos/user/n/nmangane/analysis/TEST --era 2017 -f pdf -c ${c} -p 'jsons/v0.8/'${d}'_All_'${b}'.json' -l 'jsons/v0.8/$CHANLegend.json';done

```

Using the compareEvents.py script to write events and variables to json files (for overlap comparisons with other channels; original version of script by Melissa Q of UCSB)
```
# Example usage for mu-mu channel tttt sample (channel here is only decided by name/input file; to make cut inside the tree use pandas expression inside -b '<exp>')
python RDF/scripts/compareEvents.py -v event run luminosityBlock -t Events -e event -l luminosityBlock -f /eos/user/n/nmangane/analysis/Ntupletest/Ntuples/MuMu/2017___tttt.root -b 'event > 0' -o 2017MuMu.json -s TTTT
python RDF/scripts/compareEvents.py -v event run luminosityBlock -t Events -e event -l luminosityBlock -f /eos/user/n/nmangane/analysis/Ntupletest/Ntuples/ElMu/2017___tttt.root -b 'event > 0' -o 2017ElMu.json -s TTTT

#Example usage with ttbar dl sample split into four subfiles
python RDF/scripts/scripts/compareEvents.py -v event run luminosityBlock -t Events -e event -l luminosityBlock -f /eos/user/n/nmangane/analysis/Ntupletest/Ntuples/ElMu/2017___ttbb_DL_nr.root /eos/user/n/nmangane/analysis/Ntupletest/Ntuples/ElMu/2017___ttbb_DL_fr.root /eos/user/n/nmangane/analysis/Ntupletest/Ntuples/ElMu/2017___ttother_DL_nr.root /eos/user/n/nmangane/analysis/Ntupletest/Ntuples/ElMu/2017___ttother_DL_fr.root -b 'event > 0' -o 2017ElMu.json -s TTTo2L2Nu

python RDF/scripts/scripts/compareEvents.py -v event run luminosityBlock -t Events -e event -l luminosityBlock -f /eos/user/n/nmangane/analysis/Ntupletest/Ntuples/MuMu/2017___ttbb_DL_nr.root /eos/user/n/nmangane/analysis/Ntupletest/Ntuples/MuMu/2017___ttbb_DL_fr.root /eos/user/n/nmangane/analysis/Ntupletest/Ntuples/MuMu/2017___ttother_DL_nr.root /eos/user/n/nmangane/analysis/Ntupletest/Ntuples/MuMu/2017___ttother_DL_fr.root -b 'event > 0' -o 2017MuMu.json -s TTTo2L2Nu

# Check overlap between the two samples, saving to text file
# Note the first file is still 'composed' of the sample tag and output file name, (-s, -o), $(sample)_$(output) format
python RDF/scripts/compareEvents.py -b 'event > 0' -s TTTT -o 2017ElMu.json -c TTTT_2017MuMu.json > MuMu_ElMu.txt
```