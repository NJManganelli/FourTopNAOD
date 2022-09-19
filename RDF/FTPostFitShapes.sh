#!/bin/sh
ulimit -s unlimited
set -e
cd /eos/home-n/nmangane/CMSSW/CMSSW_10_2_22/src
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
analysis_dir_base=$2
fitcard=$3
card=$4
type=$5
    
cd $analysis_dir_base

if [ -f $card/$card.root ]; then
    echo Workspace exists
else
    if [ ! -d $card ]; then
    	mkdir $card
    fi
    text2workspace.py -o $card/$card.root $card.txt
fi
rfile=$card/$card.root

if [ $type = "prefit" ]; then
    PostFitShapesFromWorkspace -d ${card}.txt -w ${rfile} -o ${card}_shapes_prefit.root -m 690
fi
if [ $type = "bonly" ]; then
    PostFitShapesFromWorkspace -d ${card}.txt -w ${rfile} -o ${card}_shapes_bonly.root -m 690 --sampling --print --skip-prefit --postfit --samples 500 --covariance -f $fitcard/fitDiagnostics_${fitcard}_rMin-100_rMax100_strategy0_fitTolerance0p1_signal1_robustHesse.root:fit_b
fi
if [ $type = "splusb" ]; then
    PostFitShapesFromWorkspace -d ${card}.txt -w ${rfile} -o ${card}_shapes_splusb.root -m 690 --sampling --print --skip-prefit --postfit --samples 500 --covariance -f $fitcard/fitDiagnostics_${fitcard}_rMin-100_rMax100_strategy0_fitTolerance0p1_signal1_robustHesse.root:fit_s
fi
