from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.common.lepSplitSFProducer import *
from FourTopNAOD.Kai.tools.toolbox import *
import collections, copy, json, math
from array import array
import multiprocessing
import inspect
import argparse
ROOT.PyConfig.IgnoreCommandLineOptions = True

# parser = argparse.ArgumentParser(description='Test of Stitching module and post-stitching distributions')
# parser.add_argument('--stage', dest='stage', action='store', type=str,
#                     help='Stage to be processed: stitch or hist or plot')
# args = parser.parse_args()


#Dilepton Data
Tuples = []
# filesTTDL=getFiles(query="dbs:/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM",
#                    redir="root://cms-xrd-global.cern.ch/")
filesTTDL=getFiles(query="glob:/eos/user/n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/Stage_NANOv4_to_Stitched/crab_20190718_0045/crab_tt_DL_2017/results/tree_*.root")
filesTTDL = filesTTDL[0:1]
hNameTTDL="SF_TTDL.root"
TTWeight = 88.341 * 1000 * 41.53 / (68875708 - 280100)
# Tuples.append((filesTTDL, hNameTTDL, "2017", "DL", "Fail", "Flag", TTWeight))
# Tuples.append((filesTTDL, hNameTTDL, "2017", "LooseID", "LooseRelIso/LooseID", "VetoID"))
# Tuples.append((filesTTDL, hNameTTDL, "2017", "MediumID", "LooseRelIso/MediumID", "LooseID"))
Tuples.append((filesTTDL, hNameTTDL, "2017", "TightID", "LooseRelIso/TightIDandIPCut", "MediumID"))
# Tuples.append((filesTTDL, hNameTTDL, "2017", "HighPtID", "TightRelTkIso/HighPtIDandIPCut", "TightID"))
# Tuples.append((filesTTDL, hNameTTDL, "2017", "TrkHighPtID", "TightRelTkIso/TrkHighPtID", "MVA80"))
# Tuples.append((filesTTDL, hNameTTDL, "2017", "SoftID", "LooseRelIso/LooseID", "MVA80noiso"))
# Tuples.append((filesTTDL, hNameTTDL, "2017", "MediumID", "TightRelIso/MediumID", "MVA90"))
# Tuples.append((filesTTDL, hNameTTDL, "2017", "TightID", "TightRelIso/TightIDandIPCut", "MVA90noiso"))

def split_sf(fileList, era="2015", muID="LooseID", muISO="LooseRelIso/LooseID", elID="LooseID"):
    p=PostProcessor(".",
                    fileList,
                    cut=None,
                    #Need the plotter, yo
                    modules=[lepSplitSFProducer(muon_ID=muID, muon_ISO=muISO, electron_ID=elID, era=era, debug=True)],
                    noOut=False,
                    postfix="_"+muID+"_"+muISO.replace("/","@")+"_"+elID,
                    # haddFileName="SFTest_"+muID+"_"+muISO.replace("/","@")+"_"+elID+".root",
                    maxEntries=100,
                    # histFileName=hName,
                    # histDirName=hDirName,
    )
    p.run()

pList = []
for tup in Tuples:
    p = multiprocessing.Process(target=split_sf, args=(tup[0], tup[2], tup[3], tup[4], tup[5]))
    pList.append(p)
    p.start()
    
for p in pList:
    p.join()
