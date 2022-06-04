#!/bin/sh
printf "%s\n" "$*"
ulimit -s unlimited
set -e
export SCRAM_ARCH=slc7_amd64_gcc830
source /cvmfs/cms.cern.ch/cmsset_default.sh

export X509_USER_PROXY=$1
job_number=$2
num_cores=$3
num_threads=${num_cores}
stage=$4
era=$5
channel=$6
sample=$7
var_set=$8
cat_set=$9
analysis_dir_base=$10


export XRDPARALLELEVTLOOP=16 #This might only work in development environments, but should increase the throughput...
echo /cvmfs/sft.cern.ch/lcg/views/LCG_102rc1/x86_64-centos7-gcc11-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_102rc1/x86_64-centos7-gcc11-opt/setup.sh;
# export LHAPDF_PATH=/cvmfs/sft.cern.ch/lcg/releases/LCG_100/MCGenerators/lhapdf/6.3.0/x86_64-centos7-gcc8-opt
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LHAPDF_PATH/lib/
# export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/:${LHAPDF_PATH}/share/LHAPDF
export PYTHONPATH=/afs/cern.ch/user/n/nmangane/.local/lib/python3.8/site-packages/:$PYTHONPATH

cd ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF
source ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/standalone/env_standalone.sh

echo ${job_number} ${stage} ${era} ${channel} ${var_set} ${cat_set} ${sample} >> ${analysis_dir}/condor_touch.log
echo "Running the analyzer... filling plots"
echo python FTAnalyzer.py ${stage} --variableSet ${var_set} --categorySet ${cat_set} --analysisDirectory ${analysis_dir_base}_${era} --noAggregate --channel ${channel} --bTagger DeepJet --jetPUId L --include ${sample} --nThreads ${num_threads} --source NANOv7_CorrNov__${channel} --sample_cards '../Kai/python/samplecards/'${era}'_NanoAODv7.yaml' '../Kai/python/samplecards/'${era}'_NanoAODv7_additional.yaml' --systematics_cards '../Kai/python/samplecards/'${era}'_systematics_NanoV7_V8.yaml' --noProgressBar --era ${era} >> ${analysis_dir}/condor_command.log

python FTAnalyzer.py ${stage} --variableSet ${var_set} --categorySet ${cat_set} --analysisDirectory ${analysis_dir_base}_${era} --noAggregate --channel ${channel} --bTagger DeepJet --jetPUId L --include ${sample} --nThreads ${num_threads} --source NANOv7_CorrNov__${channel} --sample_cards '../Kai/python/samplecards/'${era}'_NanoAODv7.yaml' '../Kai/python/samplecards/'${era}'_NanoAODv7_additional.yaml' --systematics_cards '../Kai/python/samplecards/'${era}'_systematics_NanoV7_V8.yaml' --noProgressBar --era ${era}
