from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
from FourTopNAOD.Kai.tools.toolbox import *
import collections, copy, json, math
from array import array
import multiprocessing
import inspect
ROOT.PyConfig.IgnoreCommandLineOptions = True

#Dilepton Data
Tuples = []
filesTTDL=getFiles(query="glob:/eos/user/n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/Stage_NANOv4_to_Stitched/crab_20190718_0045/crab_tt_DL_2017/results/tree_*.root")
filesTTDL = filesTTDL[0:1]
hNameTTDL="btSF_TTDL.root"
TTWeight = 88.341 * 1000 * 41.53 / (68875708 - 280100)

'csvv2,' 'cmva,' 'deepcsv,' or 'deepjet'
#cmva
Tuples.append((filesTTDL, hNameTTDL, "2016", "CMVA", "M"))
Tuples.append((filesTTDL, hNameTTDL, "2016", "CMVA", "shape_corr"))

#CSVv2
Tuples.append((filesTTDL, hNameTTDL, "2016", "CSVv2", "M"))
Tuples.append((filesTTDL, hNameTTDL, "2016", "CSVv2", "shape_corr"))
Tuples.append((filesTTDL, hNameTTDL, "2017", "CSVv2", "M"))
Tuples.append((filesTTDL, hNameTTDL, "2017", "CSVv2", "shape_corr"))

#DeepCSV
Tuples.append((filesTTDL, hNameTTDL, "Legacy2016", "DeepCSV", "M"))
Tuples.append((filesTTDL, hNameTTDL, "Legacy2016", "DeepCSV", "shape_corr"))
Tuples.append((filesTTDL, hNameTTDL, "2017", "DeepCSV", "M"))
Tuples.append((filesTTDL, hNameTTDL, "2017", "DeepCSV", "shape_corr"))
Tuples.append((filesTTDL, hNameTTDL, "2018", "DeepCSV", "M"))
Tuples.append((filesTTDL, hNameTTDL, "2018", "DeepCSV", "shape_corr"))

#DeepJet
Tuples.append((filesTTDL, hNameTTDL, "Legacy2016", "DeepCSV", "M"))
Tuples.append((filesTTDL, hNameTTDL, "Legacy2016", "DeepCSV", "shape_corr"))
Tuples.append((filesTTDL, hNameTTDL, "2017", "DeepJet", "M"))
Tuples.append((filesTTDL, hNameTTDL, "2017", "DeepJet", "shape_corr"))
Tuples.append((filesTTDL, hNameTTDL, "2018", "DeepJet", "M"))
Tuples.append((filesTTDL, hNameTTDL, "2018", "DeepJet", "shape_corr"))

def btag_sf(fileList, hName="default.root", era="2015", algo=None, wp=None):
    p=PostProcessor(".",
                    fileList,
                    cut=None,
                    modules=[btagSFProducer(muon_ID=muID, muon_ISO=muISO, electron_ID=elID, era=era, doMuonHLT=True, doElectronHLT_ZVtx=True, debug=True)],
                    noOut=False,
                    postfix="_"+era+"_"+algo+"_"+wp,
                    # haddFileName="SFTest_"+muID+"_"+muISO.replace("/","@")+"_"+elID+".root",
                    maxEntries=4,
                    histFileName=era + hName,
                    histDirName=hDirName,
    )
    p.run()

pList = []
for tup in Tuples:
    p = multiprocessing.Process(target=btag_sf, args=(tup[0], tup[1], tup[2], tup[3], tup[4]))
    pList.append(p)
    p.start()
    
for p in pList:
    p.join()
