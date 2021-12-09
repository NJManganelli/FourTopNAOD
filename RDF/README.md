# Setup Requirements
## Source the LCG stack for software, RDataFrame requires a recent root version, 6.24/04 or higher recommended
## Source the standalone setup scripts for the FourTopNAOD/Kai and PhysicsTools/nanoAOD-tools repositories, i.e.

# Setup convenience function
```
#Add this function to your .zshrc, then source it or login to the node again
rdf(){
    ulimit -s 14000
    export SCRAM_ARCH=slc7_amd64_gcc830
    export XRDPARALLELEVTLOOP=16 #This might only work in development environments, but should increase the throughput...
    if [ ${1} = "101gcc10" ];
    then
	print /cvmfs/sft.cern.ch/lcg/views/LCG_101swan/x86_64-centos7-gcc10-opt/setup.sh;
	source /cvmfs/sft.cern.ch/lcg/views/LCG_101swan/x86_64-centos7-gcc10-opt/setup.sh;
	export LHAPDF_PATH=/cvmfs/sft.cern.ch/lcg/releases/LCG_101swan/MCGenerators/lhapdf/6.3.0/x86_64-centos7-gcc10-opt
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LHAPDF_PATH/lib/
	export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/:${LHAPDF_PATH}/share/LHAPDF
	export PYTHONPATH=/afs/cern.ch/user/n/nmangane/.local/lib/python3.9/site-packages/:$PYTHONPATH
    elif [ ${1} = "101" ];
    then
	print /cvmfs/sft.cern.ch/lcg/views/LCG_101swan/x86_64-centos7-gcc8-opt/setup.sh;
	source /cvmfs/sft.cern.ch/lcg/views/LCG_101swan/x86_64-centos7-gcc8-opt/setup.sh;
	export LHAPDF_PATH=/cvmfs/sft.cern.ch/lcg/releases/LCG_101swan/MCGenerators/lhapdf/6.3.0/x86_64-centos7-gcc8-opt
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LHAPDF_PATH/lib/
	export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/:${LHAPDF_PATH}/share/LHAPDF
	export PYTHONPATH=/afs/cern.ch/user/n/nmangane/.local/lib/python3.9/site-packages/:$PYTHONPATH
    elif [ ${1} = "100" ];
    then
	# print /cvmfs/sft.cern.ch/lcg/views/dev3/${1}/x86_64-centos7-gcc8-opt/setup.sh
	# source /cvmfs/sft.cern.ch/lcg/views/dev3/${1}/x86_64-centos7-gcc8-opt/setup.sh
	print /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc8-opt/setup.sh
	source /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc8-opt/setup.sh;
	export LHAPDF_PATH=/cvmfs/sft.cern.ch/lcg/releases/LCG_100/MCGenerators/lhapdf/6.3.0/x86_64-centos7-gcc8-opt
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LHAPDF_PATH/lib/
	export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/:${LHAPDF_PATH}/share/LHAPDF
	export PYTHONPATH=/afs/cern.ch/user/n/nmangane/.local/lib/python3.8/site-packages/:$PYTHONPATH
    else;
	# print /cvmfs/sft.cern.ch/lcg/views/dev3/${1}/x86_64-centos7-gcc8-opt/setup.sh
	# source /cvmfs/sft.cern.ch/lcg/views/dev3/${1}/x86_64-centos7-gcc8-opt/setup.sh
	print /cvmfs/sft.cern.ch/lcg/views/dev3/${1}/x86_64-centos7-gcc8-opt/setup.sh
	source /cvmfs/sft.cern.ch/lcg/views/dev3/${1}/x86_64-centos7-gcc8-opt/setup.sh
	export LHAPDF_PATH=/cvmfs/sft.cern.ch/lcg/releases/dev3/${1}/MCGenerators/lhapdf/6.3.0/x86_64-centos7-gcc8-opt
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LHAPDF_PATH/lib/
	export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/:${LHAPDF_PATH}/share/LHAPDF
	export PYTHONPATH=/afs/cern.ch/user/n/nmangane/.local/lib/python3.8/site-packages/:$PYTHONPATH
    fi
    voms-proxy-init -voms cms --valid 192:00
    cd ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF
    source ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/standalone/env_standalone.zsh
    if [ $(source ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/standalone/env_standalone.zsh | grep -c build) -gt 0 ];
    then 
	source ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/Kai/standalone/env_standalone.zsh build
	source ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/standalone/env_standalone.zsh build
	source ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/standalone/env_standalone.zsh
    fi
}
```

Then call this function on each login, e.g.
```
rdf 101
```

Some checks to ensure you have expected write access using KRB5
```
#get KRB5 credentials if eosuser redirector not working (may be issue with registration of grid proxy with EOS
kinit <username>@CERN.CH #kinit <username>@FNAL.GOV
touch /eos/user/<userinitial>/<username>/test.txt
xrdcp root://eosuser.cern.ch//eos/user/<userinitial>/<username>/test.txt xrdtest.txt
```

A test run over just a few samples:
```

#Run the analyzer on just the tttt and tt_DL-GF samples in the ElMu channel
#zsh loop to fill yields maps for btagging weights
#These renorm maps are needed for ALL final plots or templating, and must be re-run if any systematics are either changed or added to. Code will fail if a map does not exist for a sample/systematic combo that is later requested for histograms.
tagger=DeepJet puid=T; for e in 2018; for c in ElMu; for s in $(less standardmc.txt | grep 'tttt\|tt_DL-GF'); do tag=MyTestCampaign_${e} && python -u FTAnalyzer.py fill-yields --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory>/${tag} --noAggregate --channel ${c} --bTagger ${tagger} --jetPUId ${puid} --include ${s} --nThreads 4 --source NANOv7_CorrNov__${c} --sample_cards '../Kai/python/samplecards/'${e}'_NanoAODv7.yaml' '../Kai/python/samplecards/'${e}'_NanoAODv7_additional.yaml' --systematics_cards '../Kai/python/samplecards/'${e}'_systematics_NanoV7_V6_controlledFullPDF.yaml' --era ${e} --recreateFileList; done

#Combine the yields to get the renormalizations
for e in 2018; for c in ElMu; for tag in MyTestCampaign_${e}; do python -u FTAnalyzer.py combine-yields --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory>/${tag} --channel ${c} --bTagger DeepJet --exclude $(less yieldexclusionlist.txt) --era ${e}; done

#Fill the HT templates in all regions for all systematics
e=2018 tagger=DeepJet puid=L; for c in ElMu;do tag=MyTestCampaign_${e}; for s in $(less standardmc.txt | grep 'tttt\|tt_DL-GF') $(less datalist.txt); do print ${s} && python -u FTAnalyzer.py fill-combine --variableSet HTOnly --categorySet 5x5 --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory>/${tag} --noAggregate --channel ${c} --bTagger ${tagger} --jetPUId ${puid} --include ${s} --nThreads 2 --source NANOv7_CorrNov__${c} --sample_cards '../Kai/python/samplecards/'${e}'_NanoAODv7.yaml' '../Kai/python/samplecards/'${e}'_NanoAODv7_additional.yaml' --systematics_cards '../Kai/python/samplecards/'${e}'_systematics_NanoV7_V6_controlledFullPDF.yaml' --era ${e} --recreateFileList; done; done

#Check all outputs are available for the 5x5 HTOnly sets run, which should be 50 per channel in 2017 and 49 in 2018:
for e in 2017 2018; for c in ElMu ElEl MuMu; do print ${c} ${e} && ls -ltr /eos/user/<userinitial>/<username>/<analysisdirectory>/MyTestCampaign_${e}/Combine/${c} | grep -c HTOnly___5x5; done

#If they are all there, hadd, since unfortunately some templating and plotting options require access to multiple years and channels together:
for e in 2017; for tag in MyTestCampaign_${e}; do python -u FTAnalyzer.py hadd-combine --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory>/${tag} --verbose --era ${e} --variableSet HTOnly --categorySet 5x5; done

#Warning: FTPlotting.py currently requires root_numpy, removed from LCG > 100, so this should be run with that until it's replaced with uproot implementation in full.
#Run templating UNBLINDED (blinding policy is set inside the FTAnalyzer.py script using an additional tag in histogram names, applying strictly to data. 
#The --zerioingThreshold sets how many events must be contributed by a template in order to not be zeroed out (given a lack of trust in the template at this point).
for e in 2018; for t in MyTestCampaign_${e}; for c in ElMu; do python -u FTPlotting.py prepare-combine --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory>/${t} --era ${e} --channel ${c} --combineCards --combineInputList HT --formats pdf --json 'HTCombine_5x5_$ERA_$CHANNEL_DeepJet.json' --legendCard 'jsons/v1.0/$CHANNELLegend_mergeST.json' --systematics_cards '../Kai/python/samplecards/'${e}'_systematics_NanoV7_V6_controlledFullPDF.yaml' --zeroingThreshold 10 --unblind; done

#In order to prepare control regions and plot them:
e=2018 tagger=DeepJet puid=L; for c in ElMu;do tag=MyTestCampaign_${e}; for s in $(less standardmc.txt | grep 'tttt\|tt_DL-GF') $(less datalist.txt) ; do print ${s} && python -u FTAnalyzer.py fill-combine --variableSet Control --categorySet 2BnJet4p --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory>/${tag} --noAggregate --channel ${c} --bTagger ${tagger} --jetPUId ${puid} --include ${s} --nThreads 4 --source NANOv7_CorrNov__${c} --sample_cards '../Kai/python/samplecards/'${e}'_NanoAODv7.yaml' '../Kai/python/samplecards/'${e}'_NanoAODv7_additional.yaml' --systematics_cards '../Kai/python/samplecards/'${e}'_systematics_NanoV7_V6_controlledFullPDF.yaml' --era ${e} --recreateFileList; done; done

#Plot the control regions:
e=2017; for t in MyTestCampaign_${e}; for c in ElMu; do python -u FTPlotting.py prepare-combine --analysisDirectory /eos/user/<userinitial>/<username>/<analysisdirectory>/${t} --era ${e} --channel ${c} --formats pdf --json 'jsons/v1.0/Control_2BnJet4p_$ERA_$CHANNEL_DeepJet.json' --legendCard 'jsons/v1.0/$CHANNELLegend_mergeST.json' --systematics_cards '../Kai/python/samplecards/'${e}'_systematics_NanoV7_V6_controlledFullPDF.yaml' --zeroingThreshold 10 --unblind; done
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