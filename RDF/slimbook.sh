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
echo /cvmfs/sft.cern.ch/lcg/views/LCG_102rc1/x86_64-centos7-gcc11-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_102rc1/x86_64-centos7-gcc11-opt/setup.sh;
# export LHAPDF_PATH=/cvmfs/sft.cern.ch/lcg/releases/LCG_100/MCGenerators/lhapdf/6.3.0/x86_64-centos7-gcc8-opt
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LHAPDF_PATH/lib/
# export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/:${LHAPDF_PATH}/share/LHAPDF
export PYTHONPATH=/afs/cern.ch/user/n/nmangane/.local/lib/python3.9/site-packages/:$PYTHONPATH

cd ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF
source ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/standalone/env_standalone.sh

if [ $2 -eq 0 ]; then
    echo Running 2017 DYJets_DL;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_DYJets_DL.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/DYJets_DL --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 1 ]; then
    echo Running 2017 DYJets_DL-HT100;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_DYJets_DL-HT100.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/DYJets_DL-HT100 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 2 ]; then
    echo Running 2017 DYJets_DL-HT200;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_DYJets_DL-HT200.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/DYJets_DL-HT200 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 3 ]; then
    echo Running 2017 DYJets_DL-HT400;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_DYJets_DL-HT400.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/DYJets_DL-HT400 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 4 ]; then
    echo Running 2017 DYJets_DL-HT600;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_DYJets_DL-HT600.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/DYJets_DL-HT600 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 5 ]; then
    echo Running 2017 DYJets_DL-HT800;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_DYJets_DL-HT800.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/DYJets_DL-HT800 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 6 ]; then
    echo Running 2017 DYJets_DL-HT1200;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_DYJets_DL-HT1200.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/DYJets_DL-HT1200 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 7 ]; then
    echo Running 2017 DYJets_DL-HT2500;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_DYJets_DL-HT2500.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/DYJets_DL-HT2500 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 8 ]; then
    echo Running 2017 ST_tW;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ST_tW.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ST_tW --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 9 ]; then
    echo Running 2017 ST_tbarW;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ST_tbarW.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ST_tbarW --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 10 ]; then
    echo Running 2017 ST_tW-NoFHad;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ST_tW-NoFHad.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ST_tW-NoFHad --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 11 ]; then
    echo Running 2017 ST_tbarW-NoFHad;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ST_tbarW-NoFHad.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ST_tbarW-NoFHad --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 12 ]; then
    echo Running 2017 ST_s-channel;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ST_s-channel.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ST_s-channel --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 13 ]; then
    echo Running 2017 ST_t_t-channel;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ST_t_t-channel.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ST_t_t-channel --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 14 ]; then
    echo Running 2017 ST_tbar_t-channel;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ST_tbar_t-channel.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ST_tbar_t-channel --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 15 ]; then
    echo Running 2017 ttH;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttH.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttH --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 16 ]; then
    echo Running 2017 ttH_DL-bb;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttH_DL-bb.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttH_DL-bb --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 17 ]; then
    echo Running 2017 ttH_SL-bb;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttH_SL-bb.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttH_SL-bb --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 18 ]; then
    echo Running 2017 ttHH;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttHH.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttHH --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 19 ]; then
    echo Running 2017 ttWH;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttWH.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttWH --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 20 ]; then
    echo Running 2017 ttWJets;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttWJets.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttWJets --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 21 ]; then
    echo Running 2017 ttWJets_QQ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttWJets_QQ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttWJets_QQ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 22 ]; then
    echo Running 2017 ttWJets_LNu;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttWJets_LNu.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttWJets_LNu --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 23 ]; then
    echo Running 2017 ttWW;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttWW.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttWW --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 24 ]; then
    echo Running 2017 ttWZ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttWZ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttWZ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 25 ]; then
    echo Running 2017 ttZH;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttZH.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttZH --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 26 ]; then
    echo Running 2017 ttZJets;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttZJets.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttZJets --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 27 ]; then
    echo Running 2017 ttZZ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttZZ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttZZ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 28 ]; then
    echo Running 2017 ttZ_DL-M10;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttZ_DL-M10.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttZ_DL-M10 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 29 ]; then
    echo Running 2017 ttZ_DL-M1to10;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttZ_DL-M1to10.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttZ_DL-M1to10 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 30 ]; then
    echo Running 2017 ttZ_QQ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ttZ_QQ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ttZ_QQ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 31 ]; then
    echo Running 2017 tt_AH;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_AH.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_AH --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 32 ]; then
    echo Running 2017 tt_AH-CR1-QCD;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_AH-CR1-QCD.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_AH-CR1-QCD --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 33 ]; then
    echo Running 2017 tt_AH-CR2-GluonMove;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_AH-CR2-GluonMove.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_AH-CR2-GluonMove --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 34 ]; then
    echo Running 2017 tt_AH-HDAMPdown;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_AH-HDAMPdown.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_AH-HDAMPdown --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 35 ]; then
    echo Running 2017 tt_AH-HDAMPup;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_AH-HDAMPup.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_AH-HDAMPup --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 36 ]; then
    echo Running 2017 tt_AH-TuneCP5down;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_AH-TuneCP5down.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_AH-TuneCP5down --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 37 ]; then
    echo Running 2017 tt_AH-TuneCP5up;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_AH-TuneCP5up.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_AH-TuneCP5up --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 38 ]; then
    echo Running 2017 tt_DL;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 39 ]; then
    echo Running 2017 tt_DL-CR1-QCD;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-CR1-QCD.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-CR1-QCD --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 40 ]; then
    echo Running 2017 tt_DL-CR2-GluonMove;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-CR2-GluonMove.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-CR2-GluonMove --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 41 ]; then
    echo Running 2017 tt_DL-HDAMPdown;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-HDAMPdown.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-HDAMPdown --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 42 ]; then
    echo Running 2017 tt_DL-HDAMPup;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-HDAMPup.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-HDAMPup --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 43 ]; then
    echo Running 2017 tt_DL-TuneCP5down;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-TuneCP5down.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-TuneCP5down --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 44 ]; then
    echo Running 2017 tt_DL-TuneCP5up;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-TuneCP5up.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-TuneCP5up --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 45 ]; then
    echo Running 2017 tt_DL-GF;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-GF.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-GF --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 46 ]; then
    echo Running 2017 tt_DL-GF-HDAMPdown;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-GF-HDAMPdown.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-GF-HDAMPdown --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 47 ]; then
    echo Running 2017 tt_DL-GF-HDAMPup;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-GF-HDAMPup.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-GF-HDAMPup --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 48 ]; then
    echo Running 2017 tt_DL-GF-TuneCP5down;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-GF-TuneCP5down.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-GF-TuneCP5down --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 49 ]; then
    echo Running 2017 tt_DL-GF-TuneCP5up;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_DL-GF-TuneCP5up.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_DL-GF-TuneCP5up --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 50 ]; then
    echo Running 2017 tt_SL;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 51 ]; then
    echo Running 2017 tt_SL-CR1-QCD;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-CR1-QCD.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-CR1-QCD --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 52 ]; then
    echo Running 2017 tt_SL-CR2-GluonMove;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-CR2-GluonMove.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-CR2-GluonMove --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 53 ]; then
    echo Running 2017 tt_SL-HDAMPdown;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-HDAMPdown.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-HDAMPdown --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 54 ]; then
    echo Running 2017 tt_SL-HDAMPup;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-HDAMPup.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-HDAMPup --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 55 ]; then
    echo Running 2017 tt_SL-TuneCP5down;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-TuneCP5down.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-TuneCP5down --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 56 ]; then
    echo Running 2017 tt_SL-TuneCP5up;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-TuneCP5up.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-TuneCP5up --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 57 ]; then
    echo Running 2017 tt_SL-GF;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-GF.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-GF --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 58 ]; then
    echo Running 2017 tt_SL-GF-HDAMPdown;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-GF-HDAMPdown.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-GF-HDAMPdown --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 59 ]; then
    echo Running 2017 tt_SL-GF-HDAMPup;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-GF-HDAMPup.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-GF-HDAMPup --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 60 ]; then
    echo Running 2017 tt_SL-GF-TuneCP5down;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-GF-TuneCP5down.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-GF-TuneCP5down --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 61 ]; then
    echo Running 2017 tt_SL-GF-TuneCP5up;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tt_SL-GF-TuneCP5up.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tt_SL-GF-TuneCP5up --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 62 ]; then
    echo Running 2017 tttJ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tttJ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tttJ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 63 ]; then
    echo Running 2017 tttW;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tttW.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tttW --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 64 ]; then
    echo Running 2017 tttt;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tttt.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tttt --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 65 ]; then
    echo Running 2017 WJets_SL;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_WJets_SL.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/WJets_SL --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 66 ]; then
    echo Running 2017 WJets_SL-HT100;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_WJets_SL-HT100.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/WJets_SL-HT100 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 67 ]; then
    echo Running 2017 WJets_SL-HT200;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_WJets_SL-HT200.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/WJets_SL-HT200 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 68 ]; then
    echo Running 2017 WJets_SL-HT400;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_WJets_SL-HT400.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/WJets_SL-HT400 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 69 ]; then
    echo Running 2017 WJets_SL-HT600;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_WJets_SL-HT600.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/WJets_SL-HT600 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 70 ]; then
    echo Running 2017 WJets_SL-HT800;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_WJets_SL-HT800.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/WJets_SL-HT800 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 71 ]; then
    echo Running 2017 WJets_SL-HT1200;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_WJets_SL-HT1200.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/WJets_SL-HT1200 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 72 ]; then
    echo Running 2017 WJets_SL-HT2500;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_WJets_SL-HT2500.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/WJets_SL-HT2500 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 73 ]; then
    echo Running 2017 WW;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_WW.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/WW --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 74 ]; then
    echo Running 2017 WZ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_WZ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/WZ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 75 ]; then
    echo Running 2017 ZZ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_ZZ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/ZZ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 76 ]; then
    echo Running 2017 tttt_badNPartonInBorn;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2017_tttt_badNPartonInBorn.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2017/tttt_badNPartonInBorn --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 77 ]; then
    echo Running 2018 DYJets_DL;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_DYJets_DL.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/DYJets_DL --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 78 ]; then
    echo Running 2018 DYJets_DL-HT100;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_DYJets_DL-HT100.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/DYJets_DL-HT100 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 79 ]; then
    echo Running 2018 DYJets_DL-HT200;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_DYJets_DL-HT200.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/DYJets_DL-HT200 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 80 ]; then
    echo Running 2018 DYJets_DL-HT400;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_DYJets_DL-HT400.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/DYJets_DL-HT400 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 81 ]; then
    echo Running 2018 DYJets_DL-HT600;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_DYJets_DL-HT600.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/DYJets_DL-HT600 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 82 ]; then
    echo Running 2018 DYJets_DL-HT800;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_DYJets_DL-HT800.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/DYJets_DL-HT800 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 83 ]; then
    echo Running 2018 DYJets_DL-HT1200;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_DYJets_DL-HT1200.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/DYJets_DL-HT1200 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 84 ]; then
    echo Running 2018 DYJets_DL-HT2500;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_DYJets_DL-HT2500.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/DYJets_DL-HT2500 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 85 ]; then
    echo Running 2018 ST_tW;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ST_tW.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ST_tW --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 86 ]; then
    echo Running 2018 ST_tbarW;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ST_tbarW.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ST_tbarW --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 87 ]; then
    echo Running 2018 ST_tW-NoFHad;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ST_tW-NoFHad.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ST_tW-NoFHad --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 88 ]; then
    echo Running 2018 ST_tbarW-NoFHad;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ST_tbarW-NoFHad.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ST_tbarW-NoFHad --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 89 ]; then
    echo Running 2018 ST_s-channel;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ST_s-channel.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ST_s-channel --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 90 ]; then
    echo Running 2018 ST_t_t-channel;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ST_t_t-channel.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ST_t_t-channel --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 91 ]; then
    echo Running 2018 ST_tbar_t-channel;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ST_tbar_t-channel.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ST_tbar_t-channel --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 92 ]; then
    echo Running 2018 ttH;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttH.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttH --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 93 ]; then
    echo Running 2018 ttH_DL-bb;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttH_DL-bb.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttH_DL-bb --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 94 ]; then
    echo Running 2018 ttH_SL-bb;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttH_SL-bb.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttH_SL-bb --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 95 ]; then
    echo Running 2018 ttHH;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttHH.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttHH --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 96 ]; then
    echo Running 2018 ttWH;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttWH.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttWH --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 97 ]; then
    echo Running 2018 ttWJets;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttWJets.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttWJets --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 98 ]; then
    echo Running 2018 ttWJets_QQ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttWJets_QQ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttWJets_QQ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 99 ]; then
    echo Running 2018 ttWJets_LNu;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttWJets_LNu.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttWJets_LNu --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 100 ]; then
    echo Running 2018 ttWW;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttWW.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttWW --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 101 ]; then
    echo Running 2018 ttWZ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttWZ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttWZ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 102 ]; then
    echo Running 2018 ttZH;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttZH.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttZH --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 103 ]; then
    echo Running 2018 ttZJets;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttZJets.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttZJets --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 104 ]; then
    echo Running 2018 ttZZ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttZZ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttZZ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 105 ]; then
    echo Running 2018 ttZ_DL-M10;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttZ_DL-M10.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttZ_DL-M10 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 106 ]; then
    echo Running 2018 ttZ_DL-M1to10;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttZ_DL-M1to10.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttZ_DL-M1to10 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 107 ]; then
    echo Running 2018 ttZ_QQ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ttZ_QQ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ttZ_QQ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 108 ]; then
    echo Running 2018 tt_AH;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_AH.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_AH --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 109 ]; then
    echo Running 2018 tt_AH-CR1-QCD;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_AH-CR1-QCD.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_AH-CR1-QCD --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 110 ]; then
    echo Running 2018 tt_AH-CR2-GluonMove;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_AH-CR2-GluonMove.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_AH-CR2-GluonMove --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 111 ]; then
    echo Running 2018 tt_AH-HDAMPdown;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_AH-HDAMPdown.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_AH-HDAMPdown --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 112 ]; then
    echo Running 2018 tt_AH-HDAMPup;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_AH-HDAMPup.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_AH-HDAMPup --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 113 ]; then
    echo Running 2018 tt_AH-TuneCP5down;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_AH-TuneCP5down.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_AH-TuneCP5down --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 114 ]; then
    echo Running 2018 tt_AH-TuneCP5up;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_AH-TuneCP5up.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_AH-TuneCP5up --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 115 ]; then
    echo Running 2018 tt_DL;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 116 ]; then
    echo Running 2018 tt_DL-CR1-QCD;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-CR1-QCD.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-CR1-QCD --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 117 ]; then
    echo Running 2018 tt_DL-CR2-GluonMove;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-CR2-GluonMove.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-CR2-GluonMove --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 118 ]; then
    echo Running 2018 tt_DL-HDAMPdown;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-HDAMPdown.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-HDAMPdown --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 119 ]; then
    echo Running 2018 tt_DL-HDAMPup;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-HDAMPup.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-HDAMPup --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 120 ]; then
    echo Running 2018 tt_DL-TuneCP5down;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-TuneCP5down.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-TuneCP5down --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 121 ]; then
    echo Running 2018 tt_DL-TuneCP5up;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-TuneCP5up.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-TuneCP5up --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 122 ]; then
    echo Running 2018 tt_DL-GF;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-GF.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-GF --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 123 ]; then
    echo Running 2018 tt_DL-GF-HDAMPdown;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-GF-HDAMPdown.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-GF-HDAMPdown --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 124 ]; then
    echo Running 2018 tt_DL-GF-HDAMPup;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-GF-HDAMPup.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-GF-HDAMPup --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 125 ]; then
    echo Running 2018 tt_DL-GF-TuneCP5down;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-GF-TuneCP5down.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-GF-TuneCP5down --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 126 ]; then
    echo Running 2018 tt_DL-GF-TuneCP5up;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_DL-GF-TuneCP5up.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_DL-GF-TuneCP5up --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 127 ]; then
    echo Running 2018 tt_SL;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 128 ]; then
    echo Running 2018 tt_SL-CR1-QCD;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-CR1-QCD.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-CR1-QCD --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 129 ]; then
    echo Running 2018 tt_SL-CR2-GluonMove;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-CR2-GluonMove.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-CR2-GluonMove --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 130 ]; then
    echo Running 2018 tt_SL-HDAMPdown;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-HDAMPdown.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-HDAMPdown --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 131 ]; then
    echo Running 2018 tt_SL-HDAMPup;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-HDAMPup.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-HDAMPup --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 132 ]; then
    echo Running 2018 tt_SL-TuneCP5down;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-TuneCP5down.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-TuneCP5down --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 133 ]; then
    echo Running 2018 tt_SL-TuneCP5up;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-TuneCP5up.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-TuneCP5up --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 134 ]; then
    echo Running 2018 tt_SL-GF;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-GF.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-GF --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 135 ]; then
    echo Running 2018 tt_SL-GF-HDAMPdown;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-GF-HDAMPdown.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-GF-HDAMPdown --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 136 ]; then
    echo Running 2018 tt_SL-GF-HDAMPup;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-GF-HDAMPup.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-GF-HDAMPup --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 137 ]; then
    echo Running 2018 tt_SL-GF-TuneCP5down;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-GF-TuneCP5down.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-GF-TuneCP5down --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 138 ]; then
    echo Running 2018 tt_SL-GF-TuneCP5up;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tt_SL-GF-TuneCP5up.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tt_SL-GF-TuneCP5up --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 139 ]; then
    echo Running 2018 tttJ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tttJ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tttJ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 140 ]; then
    echo Running 2018 tttW;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tttW.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tttW --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 141 ]; then
    echo Running 2018 tttt;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_tttt.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/tttt --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 142 ]; then
    echo Running 2018 WJets_SL;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_WJets_SL.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/WJets_SL --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 143 ]; then
    echo Running 2018 WJets_SL-HT100;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_WJets_SL-HT100.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/WJets_SL-HT100 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 144 ]; then
    echo Running 2018 WJets_SL-HT200;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_WJets_SL-HT200.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/WJets_SL-HT200 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 145 ]; then
    echo Running 2018 WJets_SL-HT400;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_WJets_SL-HT400.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/WJets_SL-HT400 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 146 ]; then
    echo Running 2018 WJets_SL-HT600;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_WJets_SL-HT600.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/WJets_SL-HT600 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 147 ]; then
    echo Running 2018 WJets_SL-HT800;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_WJets_SL-HT800.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/WJets_SL-HT800 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 148 ]; then
    echo Running 2018 WJets_SL-HT1200;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_WJets_SL-HT1200.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/WJets_SL-HT1200 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 149 ]; then
    echo Running 2018 WJets_SL-HT2500;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_WJets_SL-HT2500.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/WJets_SL-HT2500 --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 150 ]; then
    echo Running 2018 WW;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_WW.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/WW --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 151 ]; then
    echo Running 2018 WZ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_WZ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/WZ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
if [ $2 -eq 152 ]; then
    echo Running 2018 ZZ;
    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:skimming/2018_ZZ.txt' --simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir /eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/2018/ZZ --keep run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup --tempdir ./ --noProgressBar; 
fi
