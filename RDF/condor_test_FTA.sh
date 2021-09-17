#!/bin/sh
printf "%s\n" "$*"
ulimit -s unlimited
set -e
export SCRAM_ARCH=slc7_amd64_gcc830
source /cvmfs/cms.cern.ch/cmsset_default.sh

export X509_USER_PROXY=$1
job_number=$2
num_cores=$3

export XRDPARALLELEVTLOOP=16 #This might only work in development environments, but should increase the throughput...
echo /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc8-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc8-opt/setup.sh;
export LHAPDF_PATH=/cvmfs/sft.cern.ch/lcg/releases/LCG_100/MCGenerators/lhapdf/6.3.0/x86_64-centos7-gcc8-opt
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LHAPDF_PATH/lib/
export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/:${LHAPDF_PATH}/share/LHAPDF
export PYTHONPATH=/afs/cern.ch/user/n/nmangane/.local/lib/python3.8/site-packages/:$PYTHONPATH

cd ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF
source ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/standalone/env_standalone.sh

if [ $2 -eq 0 ]; then
  # echo "using dasgoclient"
  # dasgoclient --query="file dataset=/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv2-106X_upgrade2018_realistic_v15_L1v1-v1/NANOAODSIM"
    echo "Running the analyzer..."
    python -u FTAnalyzer.py fill-yields --analysisDirectory /eos/user/n/nmangane/analysis/Sep16_test_condor_2018 --noAggregate --channel ElMu --bTagger DeepJet --jetPUId L --include tttt --nThreads 10 --source NANOv7_CorrNov__ElMu --sample_cards '../Kai/python/samplecards/2018_NanoAODv7.yaml' '../Kai/python/samplecards/2018_NanoAODv7_additional.yaml' --systematics_cards '../Kai/python/samplecards/2018_systematics_NanoV7_V6_controlledFullPDF.yaml' --era 2018 # --recreateFileList
  # python -u FTAnalyzer.py fill-combine --variableList FTAJet4{bpf}_pt FTAJet4{bpf}_eta --categorySet 5x5 --analysisDirectory /eos/user/n/nmangane/analysis/Sep16_test_condor_2018 --noAggregate --channel ElMu --bTagger DeepJet --jetPUId L --include tttt --nThreads 12 --source NANOv7_CorrNov__ElMu --sample_cards ../Kai/python/samplecards/2018_NanoAODv7.yaml ../Kai/python/samplecards/2018_NanoAODv7_additional.yaml --systematics_cards ../Kai/python/samplecards/2018_systematics_NanoV7_V6_controlledFullPDF.yaml --era 2018 # --recreateFileList
fi
