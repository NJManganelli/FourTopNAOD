#!/usr/bin/env python
# coding: utf-8 
from __future__ import print_function
import os
import pwd #needed for username, together with os
import sys
import time
import datetime
import argparse
import numpy as np
import subprocess
import copy
import glob
import collections
import array
import pprint
import re
import pdb
import psutil #psutil.Process().memory_info() for info...
import ROOT
import ruamel.yaml as yaml
from FourTopNAOD.RDF.tools.toolbox import getFiles, load_yaml_cards, write_yaml_cards, filter_systematics
from FourTopNAOD.RDF.analyzer.histogram import fill_histos, fill_histos_ndim
from FourTopNAOD.RDF.analyzer.cpp import declare_cpp_constants, make_cpp_safe_name
from FourTopNAOD.RDF.analyzer.core import METXYCorr, defineJets, defineWeights, defineLeptons, splitProcess
from FourTopNAOD.RDF.io.ntupler import getNtupleVariables, delegateFlattening, flattenVariable, writeNtuples, delegateSnapshots
from FourTopNAOD.RDF.io.root import writeHistos, bookSnapshot#, writeHistosForCombine, writeHistosV1
from tqdm import tqdm
#from IPython.display import Image, display, SVG
#import graphviz
ROOT.PyConfig.IgnoreCommandLineOptions = True

useSpark = False #Doesn't seem to work with gcc8 at least...
if useSpark:
    import PyRDF
    PyRDF.use("spark", {'npartitions': '8'}) #was 32 in example
    RDF = PyRDF.RDataFrame
else:
    #print("DISABLING IMT for bebugging branches")
    # ROOT.ROOT.EnableImplicitMT() #Disabled here, configurable parameter prior to calling main()
    RS = ROOT.ROOT
    RDF = RS.RDataFrame

#Load functions, can eventually be changed to ROOT.gInterpreter.Declare(#include "someheader.h")
#WARNING! Do not rerun this cell without restarting the kernel, it will kill it!
ROOT.TH1.SetDefaultSumw2() #Make sure errors are done this way #Extra note, this is completely irrelevant, since ROOT 6 all histograms that have a (non-unitary) weight provided for filling 
#Declare random number generator
ROOT.gInterpreter.Declare("TRandom3 rng = TRandom3();")
print("FIXME? Consider removing even unitary weight from data histogram filling, due to the bug in ROOT where Sumw2 is impossible to disable using the documented method")
print("FIXME: Hardcoded FTFunctions.cpp path, needs fixin'...")
ROOT.gROOT.ProcessLine(".L FTFunctions.cpp")
# print("To compile the loaded file, append a '+' to the '.L <file_name>+' line, and to specify gcc as the compile, also add 'g' after that")
#https://root-forum.cern.ch/t/saving-root-numba-declare-callables-in-python/44020/2
#Alternate formulations of loading the functions:
#1 compile externally and then load it
# g++ -c -fPIC -o FTFunctions.so FTFunctions.cpp $(root-config --libs --cflags)
# ROOT.gInterpreter.Declare('#include "FTFunctions.cpp"')
# ROOT.gSystem.Load("FTFunctions.so")
#2 compile in ROOT from python, with the first part optionally done externally or previously (it shouldn't recompile if it already exists?), and option 'k' keeps the .so persistent
# print("Compiling")
# ROOT.gSystem.CompileMacro("FTFunctions.cpp", "kO")
# print("Declaring")
# ROOT.gInterpreter.Declare('#include "FTFunctions.cpp"')
# print("Loading")
# ROOT.gInterpreter.Load("FTFunctions_cpp.so")
# print("Done")

# David Ren-Hwa Yu
# 22:43
# In older versions of ROOT, I vaguely remember that you had to load the header files for the libraries, like 

# gInterpreter.Declare("#include \"MyTools/RootUtils/interface/HistogramManager.h\"")
# gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/$SCRAM_ARCH/libMyToolsRootUtils.so"))
# ROOT.gROOT.ProcessLine(".L FTFunctions.cpp+g") #+ compiles, g specifies gcc as the compiler to use instead of whatever ROOT naturally prefers (llvm? clang?)
ROOT.gInterpreter.Declare("""
    const UInt_t barWidth = 60;
    ULong64_t processed = 0, totalEvents = 0;
    std::string progressBar;
    std::mutex barMutex; 
    auto registerEvents = [](ULong64_t nIncrement) {totalEvents += nIncrement;};

    ROOT::RDF::RResultPtr<ULong64_t> AddProgressBar(ROOT::RDF::RNode df, int everyN=10000, int totalN=100000) {
        registerEvents(totalN);
        auto c = df.Count();
        c.OnPartialResultSlot(everyN, [everyN] (unsigned int slot, ULong64_t &cnt){
            std::lock_guard<std::mutex> l(barMutex);
            processed += everyN; //everyN captured by value for this lambda
            progressBar = "[";
            for(UInt_t i = 0; i < static_cast<UInt_t>(static_cast<Float_t>(processed)/totalEvents*barWidth); ++i){
                progressBar.push_back('|');
            }
            // escape the '\' when defined in python string
            std::cout << "\\r" << std::left << std::setw(barWidth) << progressBar << "] " << processed << "/" << totalEvents << std::flush;
        });
        return c;
    }
""")

#Add lumi to the trigger tuple?
TriggerTuple = collections.namedtuple("TriggerTuple", "trigger era subera uniqueEraBit tier channel leadMuThresh subMuThresh leadElThresh subElThresh nontriggerLepThresh")
TriggerList = [TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=14,
                            tier=0,
                            channel="ElMu",
                            leadMuThresh=23,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=12,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=13,
                            tier=0,
                            channel="ElMu",
                            leadMuThresh=99999,
                            subMuThresh=12,
                            leadElThresh=23,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                            era="2017",
                            subera="B",
                            uniqueEraBit=12,
                            tier=1,
                            channel="MuMu",
                            leadMuThresh=17,
                            subMuThresh=12,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
                            era="2017",
                            subera="CDEF",
                            uniqueEraBit=11,
                            tier=1,
                            channel="MuMu",
                            leadMuThresh=17,
                            subMuThresh=12,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=9,
                            tier=2,
                            channel="ElEl",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=23,
                            subElThresh=12,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_IsoMu27",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=7,
                            tier=3,
                            channel="Mu",
                            leadMuThresh=27,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_Ele35_WPTight_Gsf",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=6,
                            tier=4,
                            channel="El",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=35,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_PFMET200_NotCleaned",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=3,
                            tier=5,
                            channel="MET",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_PFMET200_HBHECleaned",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=2,
                            tier=5,
                            channel="MET",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=1,
                            tier=5,
                            channel="MET",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=14,
                            tier=0,
                            channel="ElMu",
                            leadMuThresh=99999,
                            subMuThresh=12,
                            leadElThresh=23,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=12,
                            tier=0,
                            channel="ElMu",
                            leadMuThresh=23,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=12,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=11,
                            tier=1,
                            channel="MuMu",
                            leadMuThresh=17,
                            subMuThresh=12,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=9,
                            tier=2,
                            channel="ElEl",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=23,
                            subElThresh=12,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_IsoMu24",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=8,
                            tier=3,
                            channel="Mu",
                            leadMuThresh=24,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_Ele32_WPTight_Gsf",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=7,
                            tier=4,
                            channel="El",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=32,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_PFMET200_NotCleaned",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=3,
                            tier=5,
                            channel="MET",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_PFMET200_HBHECleaned",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=2,
                            tier=5,
                            channel="MET",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
               TriggerTuple(trigger="HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=1,
                            tier=5,
                            channel="MET",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=12),
           ]

# cutoutV2_ToBeFixed = {
#     "QCD_HT200":{
#         "era": "2017",
#         "channels": ["All"],
#         "isData": False,
#         "nEvents": 59200263,
#         "nEventsPositive": 59166789,
#         "nEventsNegative": 32544,
#         "sumWeights": 59133315.000000,
#         "sumWeights2": 59200263.000000,
#         "isSignal": False,
#         "crossSection": 1712000.0,
#         "source": {"NANOv5": "dbs:/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
#                    "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT200_2017_v2.root",
#                    "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT200_2017_v2*.root",
#                    "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT200_2017_v2*.root",
#                    "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT200_2017_v2*.root",
#                   },
#         "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT200_2017_v2.root",],
#     },
#     "QCD_HT300":{
#         "era": "2017",
#         "channels": ["All"],
#         "isData": False,
#         "nEvents": 59569132,
#         "nEventsPositive": 59514373,
#         "nEventsNegative": 54759,
#         "sumWeights": 59459614.000000,
#         "sumWeights2": 59569132.000000,
#         "isSignal": False,
#         "crossSection": 347700.0,
#         "source": {"NANOv5": "dbs:/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
#                    "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT300_2017_v2.root",
#                    "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT300_2017_v2*.root",
#                    "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT300_2017_v2*.root",
#                    "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT300_2017_v2*.root",
#                   },
#         "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT300_2017_v2.root",],
#     },   
#     "QCD_HT500":{
#         "era": "2017",
#         "channels": ["All"],
#         "isData": False,
#         "nEvents": 56207744,
#         "nEventsPositive": 56124381,
#         "nEventsNegative": 83363,
#         "sumWeights": 56041018.000000,
#         "sumWeights2": 56207744.000000,
#         "isSignal": False,
#         "crossSection": 32100.0,
#         "source": {"NANOv5": "dbs:/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
#                    "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT500_2017_v2.root",
#                    "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT500_2017_v2*.root",
#                    "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT500_2017_v2*.root",
#                    "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT500_2017_v2*.root",
#                   },
#         "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT500_2017_v2.root",],
#     },
#     "QCD_HT700":{
#         "era": "2017",
#         "channels": ["All"],
#         "isData": False,
#         "nEvents": 46840955,
#         "nEventsPositive": 46739970,
#         "nEventsNegative": 100985,
#         "sumWeights": 46638985.000000,
#         "sumWeights2": 46840955.000000,
#         "isSignal": False,
#         "crossSection": 6831.0,
#         "source": {"NANOv5": "dbs:/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
#                    "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT700_2017_v2.root",
#                    "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT700_2017_v2*.root",
#                    "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT700_2017_v2*.root",
#                    "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT700_2017_v2*.root",
#                   },
#         "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT700_2017_v2.root",],
#     },
#     "QCD_HT1000":{
#         "era": "2017",
#         "channels": ["All"],
#         "isData": False,
#         "nEvents": 16882838,
#         "nEventsPositive": 16826800,
#         "nEventsNegative": 56038,
#         "sumWeights": 16770762.000000,
#         "sumWeights2": 16882838.000000,
#         "isSignal": False,
#         "crossSection": 1207.0,
#         "source": {"NANOv5": "dbs:/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
#                    "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1000_2017_v2.root",
#                    "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT1000_2017_v2*.root",
#                    "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT1000_2017_v2*.root",
#                    "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT1000_2017_v2*.root",
#                   },
#         "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1000_2017_v2.root",],
#     },
#     "QCD_HT1500":{
#         "era": "2017",
#         "channels": ["All"],
#         "isData": False,
#         "nEvents": 11634434,
#         "nEventsPositive": 11571519,
#         "nEventsNegative": 62915,
#         "sumWeights": 11508604.000000,
#         "sumWeights2": 11634434.000000,
#         "isSignal": False,
#         "crossSection": 119.9,
#         "source": {"NANOv5": "dbs:/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
#                    "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1500_2017_v2.root",
#                    "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT1500_2017_v2*.root",
#                    "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT1500_2017_v2*.root",
#                    "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT1500_2017_v2*.root",
#                   },
#         "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1500_2017_v2.root",],
#     },
#     "QCD_HT2000":{
#         "era": "2017",
#         "channels": ["All"],
#         "isData": False,
#         "nEvents": 5941306,
#         "nEventsPositive": 5883436,
#         "nEventsNegative": 57870,
#         "sumWeights": 5825566.000000,
#         "sumWeights2": 5941306.000000,
#         "isSignal": False,
#         "crossSection": 25.24,
#         "source": {"NANOv5": "dbs:/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
#                    "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT2000_2017_v2.root",
#                    "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT2000_2017_v2*.root",
#                    "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT2000_2017_v2*.root",
#                    "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT2000_2017_v2*.root",
#                   },
#         "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT2000_2017_v2.root",],
#     },
# }



def testVariableProcessing(inputDForNodes, nodes=False, searchMode=True, skipColumns=[],
                           allowedTypes=['int','double','ROOT::VecOps::RVec<int>','float','ROOT::VecOps::RVec<float>','bool']):
    """Pass in a dataframe or head dictionary containing nodes (as returned by splitProcess function), walking through each variable and defining a mean and getting it's value to test if it causes issue. type as retuned by dataframe's GetColumnType should be in the list of 'allowedTypes'"""
    if nodes is True:
        testnodes = {}
        testvalues = {}
        for testProcess in inputDForNodes["nodes"].keys():
            if testProcess == 'BaseNode': continue
            testnodes[testProcess] = inputDForNodes["nodes"][testProcess]['BaseNode']
            safes = [branch for branch in testnodes[testProcess].GetDefinedColumnNames() if testnodes[testProcess].GetColumnType(branch) in allowedTypes and branch not in skipColumns]
            if searchMode is True:
                print("{}".format(testProcess))
                for branch in safes:
                    print("\t{}: ".format(branch), end="")
                    print("{}".format(testnodes[testProcess].Mean(branch).GetValue()))
            else:
                testvalues[testProcess] = [(branch, testnodes[testProcess].Mean(branch)) for branch in safes]
        if searchMode is False:
            for testProcess in inputDForNodes["nodes"].keys():
                if testProcess == 'BaseNode': continue
                for SV in testvalues[testProcess]:
                    print(SV[0], end=' ')
                    print(SV[1].GetValue(), end='\n')
    else:
        safes = [branch for branch in inputDForNodes.GetDefinedColumnNames() if inputDForNodes.GetColumnType(branch) in allowedTypes and branch not in skipColumns]
        if searchMode is True:
            print("{}".format("Unsplit process"))
            for branch in safes:
                print("\t{}: ".format(branch), end="")
                print("{}".format(inputDForNodes.Mean(branch).GetValue()))
        else:
            testvalues = [(branch, inputDForNodes.Mean(branch)) for branch in safes]
        if searchMode is False:
            for SV in testvalues:
                print(SV[0], end=' ')
                print(SV[1].GetValue(), end='\n')
    return safes

def BTaggingYields(input_df_or_nodes, sampleName, era, channel="All", isData = True, histosDict=None, bTagger="DeepCSV", verbose=False,
                   loadYields=None, lookupMap="LUM", vectorLUTs=None, correctorMap=None,
                   useAggregate=True, useHTOnly=False, useNJetOnly=False, 
                   calculateYields=True, HTArray=[500, 650, 800, 1000, 1200, 10000], nJetArray=[4,5,6,7,8,20],
                   sysVariations={"$NOMINAL": {"jet_mask": "jet_mask",
                                               "lep_postfix": "", 
                                               "jet_pt_var": "Jet_pt",
                                               "jet_mass_var": "Jet_mass",
                                               "met_pt_var": "METFixEE2017_pt",
                                               "met_phi_var": "METFixEE2017_phi",
                                               "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                                          "DeepJet": "Jet_btagSF_deepjet_shape",
                                                      },
                                               "weightVariation": False},
                                              },
                   sysFilter=["$NOMINAL"],
               ):
    """Calculate or load the event yields in various categories for the purpose of renormalizing btagging shape correction weights.
    
    A btagging preweight (event level) must be calculated using the product of all SF(function of discriminant, pt, eta) for
    all selected jets. Then a ratio of the sum(weights before)/sum(weights after) for application of this btagging 
    preweight serves as a renormalization, and this phase space extrapolation can be a function of multiple variables.
    For high-jet multiplicity analyses, it can be expected to depend on nJet. The final btagging event weight
    is then the product of this phase space ratio and the btagging preweight. This should be computed PRIOR to ANY
    btagging requirements (cut on number of BTags); after, the event yields and shapes are expected to shift.
    
    The final and preweight are computed separately from the input weight (that is, it must be multiplied with the non-btagging event weight)
    The yields are calculated as the sum of weights before and after multiplying the preweight with the input weight

    <sampleName> should be passed to provide a 'unique' key for the declared lookupMap. This is purely to avoid namesplace conflicts
    when aggregate yields are to be used. If not using aggregates, it provides the actual lookup key (into a yields histogram)
    <isData> If running on data, disable all systematic variations besides $NOMINAL/'_nom'
    <histosDict> dictionary for writing the histograms to fill yields

    Group - Yield Loading
    <loadYields> string path to the BTaggingYields.root file containing the ratios
    <lookupMap> is a string name for the lookupMap object (std::map<std::string, std::vector<TH2Lookup*> > in the ROOT interpreter.
    This object can be shared amongnst several dataframes, as the key (std::string) is the sampleName. For each thread/slot assigned
    to an RDataFrame, there will be a TH2Lookup pointer, to avoid multiple threads accessing the same object (has state)
    <useAggregate> will toggle using the weighted average of all processed samples (those used when choosing to analyze the files)
    <useHTOnly> and <useNJetOnly> will toggle the lookup to use the 1D yield ratios computed in either HT only or nJet only

    Group - Yield Computation
    <calculateYields> as indicated, fill histograms for the yields, making an assumption that there is a weight named
    "prewgt<SYSTEMATIC_POSTFIX>" where the postfix is the key inside sysVariations. i.e. "$NOMINAL" -> "prewgt_nom" due to 
    special replacement for nominal, and "jec_13TeV_R2017Up" -> "prewgt_jec_13TeV_R2017Up" is expected
    <HTBinWidth>, <HTMin>, <HTMax> are as expected. Don't screw up the math on your end, (max-min) should be evenly divisible.
    <nJetBinWidth>, <nJetMin>, <nJetMax> are similar

    For more info on btagging, see...
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagShapeCalibration"""

    if useAggregate:
        yieldsKey = "Aggregate"
    else:
        yieldsKey = "{}".format(sampleName) #copy it, we'll modify
    if useHTOnly:
        yieldsKey += "1DX"
    elif useNJetOnly:
        yieldsKey += "1DY"        
    
    #internal variable/pointer to the TH2 lookup map, and the sample-specific one
    iLUM = None
    if loadYields != None:
        calculateYields = False
        #We need a lookupMap to store the TH2Lookup class with the yields loaded in them,
        #With key1 based on the sample name and key2 based on slot number in the RDataFrame
        #We need the string name for the object in the ROOT space, creating it if necessary
        if type(lookupMap) == str:
            #It's a string name, see if it's been declared in the ROOT instance and if not create it
            try:
                if str(type(getattr(ROOT, lookupMap))) == "<class 'ROOT.map<string,vector<TH2Lookup*> >'>":
                    #We'll pick it up after the except statement
                    pass
            except:
                ROOT.gInterpreter.Declare("std::map<std::string, std::vector<TH2Lookup*>> {0};".format(lookupMap))
            iLUM = getattr(ROOT, lookupMap)
        else:
            raise RuntimeError("lookupMap (used in BTaggingYields function) must either be a string name "\
                               "for the declared function's (C++ variable) name, used to find or declare one of type "\
                               "std::map<std::string, std::vector<TH2Lookup*>>")
        nSlots = 1
        try:
            nSlots = input_df_or_nodes.get("nodes").get("BaseNode").GetNSlots()
        except:
            nSlots = ROOT.ROOT.RDataFrame(10).GetNSlots()
        assert os.path.isfile(loadYields), "BTaggingYield file does not appear to exist... aborting execution\n{}".format(loadYields)
        # while iLUM[sampleName].size() < nSlots:
        #     if type(loadYields) == str:
        #         iLUM[sampleName].push_back(ROOT.TH2Lookup(loadYields))
        #     else:
        #         raise RuntimeError("No string path to a yields file has been provided in BTaggingYields() ...")
                
        # #Test to see that it's accessible...
        # testKeyA = yieldsKey
        # testKeyB = "nom"
        # testNJ = 6
        # testHT = 689.0
        # testVal = iLUM[sampleName][0].getEventYieldRatio(testKeyA, testKeyB, testNJ, testHT)
        # if verbose:
        #     print("BTaggingYield has done a test evaluation on the yield histogram with search for histogram {}{}, nJet={}, HT={} and found value {}"\
        #           .format(testKeyA, testKeyB, testNJ, testHT, testVal))
        # assert type(testVal) == float, "LookupMap did not provide a valid return type, something is wrong"
        # assert testVal < 5.0, "LookupMap did not provide a reasonable BTagging Yield ratio in the test... (>5.0 is considered unrealistic...)"        
    
    if isData == True:
        return input_df_or_nodes
    else:
    # if type(input_df_or_nodes) in [dict, collections.OrderedDict]:
        histoNodes = histosDict #Inherit this from initiliazation, this is where the histograms will actually be stored
        filterNodes = input_df_or_nodes.get("filterNodes")
        nodes = input_df_or_nodes.get("nodes")
        if "bTaggingDefineNodes" not in input_df_or_nodes:
            input_df_or_nodes["bTaggingDefineNodes"] = collections.OrderedDict()
        bTaggingDefineNodes = input_df_or_nodes.get("bTaggingDefineNodes")
        diagnosticNodes = input_df_or_nodes.get("diagnosticNodes", collections.OrderedDict())
        countNodes = input_df_or_nodes.get("countNodes", collections.OrderedDict())
        #column guards
        for eraAndSampleName in nodes.keys():
            if eraAndSampleName.lower() == "basenode": continue
            #Add key to histos dictionary, if calculating the yields
            if calculateYields and eraAndSampleName not in histosDict:
                histosDict[eraAndSampleName] = collections.OrderedDict()
                histosDict[eraAndSampleName][channel] = collections.OrderedDict()
            if eraAndSampleName not in  bTaggingDefineNodes:
                 bTaggingDefineNodes[eraAndSampleName] = collections.OrderedDict()
            if eraAndSampleName not in diagnosticNodes:
                diagnosticNodes[eraAndSampleName] = collections.OrderedDict()
            if eraAndSampleName not in countNodes:
                countNodes[eraAndSampleName] = collections.OrderedDict()
            # for decayChannel in nodes[eraAndSampleName].keys():
            #     if eraAndSampleName not in nodes[eraAndSampleName]:
            #         nodes[eraAndSampleName][decayChannel] = collections.OrderedDict()
            #     if eraAndSampleName not in  bTaggingDefineNodes[eraAndSampleName]:
            #          bTaggingDefineNodes[eraAndSampleName][decayChannel] = collections.OrderedDict()
            #     if eraAndSampleName not in diagnosticNodes[eraAndSampleName]:
            #         diagnosticNodes[eraAndSampleName][decayChannel] = collections.OrderedDict()
            #     if eraAndSampleName not in countNodes[eraAndSampleName]:
            #         countNodes[eraAndSampleName][decayChannel] = collections.OrderedDict()
            
            if loadYields != None:
                thisSlot = 0
                while iLUM[eraAndSampleName].size() < nSlots:
                    if isinstance(loadYields, str):
                        # iLUM[eraAndSampleName].push_back(ROOT.TH2Lookup(loadYields, str(thisSlot), True))
                        iLUM[eraAndSampleName].push_back(ROOT.TH2Lookup(loadYields, str(thisSlot)))
                    else:
                        raise RuntimeError("No string path to a yields file has been provided in BTaggingYields() ...")
                    thisSlot += 1
                        
                #Test to see that it's accessible...
                testKeyA = yieldsKey + "___nom"
                # testKeyB = "__nom"
                testNJ = 6
                testHT = 689.0
                print("FIXME: BTagging LUT Assertion removed for old method, add new method test?")
                # if verbose:
                #     testVal = iLUM[eraAndSampleName][0].getEventYieldRatio(testKeyA, testNJ, testHT)
                #     print("BTaggingYield has done a test evaluation on the yield histogram with search for histogram {}, nJet={}, HT={} and found value {}"\
                #           .format(testKeyA, testNJ, testHT, testVal))
                # else:
                #     testVal = iLUM[eraAndSampleName][0].getEventYieldRatio(testKeyA, testNJ, testHT)
                # assert type(testVal) == float, "LookupMap did not provide a valid return type, something is wrong"
                # assert testVal >= 0.0, "LookupMap did not provide a reasonable BTagging Yield ratio in the test... ({} is considered unrealistic...)".format(testVal)
                # assert testVal <= 5.0, "LookupMap did not provide a reasonable BTagging Yield ratio in the test... ({} is considered unrealistic...)".format(testVal)
        
            listOfColumns = nodes[eraAndSampleName]["BaseNode"].GetColumnNames() #This is a superset, containing non-Define'd columns as well


            # rdf = input_df
            #Create list of the variations to be histogrammed (2D yields)
            yieldList = []
            for sysVarRaw, sysDict in sysVariations.items():
                #Only do systematics that are in the filter list (storing raw systematic names...
                if sysVarRaw not in sysFilter:
                    continue
                #get final systematic name
                sysVar = sysVarRaw.replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', '')).replace("$ERA", era)
                bTaggingDefineNodes[eraAndSampleName][sysVar] = []
                isWeightVariation = sysDict.get("weightVariation")
                branchpostfix = "__nom" if isWeightVariation else "__" + sysVar.replace("$NOMINAL", "nom") #branch postfix for identifying input branch variation
                syspostfix = "___" + sysVar
                jetMask = sysDict.get("jet_mask").replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', '')) #mask as defined for the jet collection under this systematic variation
                jetPt = sysDict.get("jet_pt_var").replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', '')) #colum name of jet pt collection for this systematic
                jetSF = sysDict.get("btagSF").get(bTagger, "NO / VALID / jetSF") #colum name of per-jet shape SFs
                #We must get or calculate various weights, defined below
                #This btagSFProduct is the product of the SFs for the selected jets from collection jetPt with mask jetMask
                btagSFProduct = "btagSFProduct{spf}".format(spf=syspostfix)
                #input weight, should include all corrections for this systematic variation except BTagging SF and yield ratio
                calculationWeightBefore = "prewgt{spf}".format(spf=syspostfix)

                if isWeightVariation and jetMask not in ["jet_mask", "jet_mask_nom"]:
                    print("Warning: Potential systematic card misconfiguration, weightVariation:true overrides the use of a scale-varying jet_mask, and the jet_mask name is not 'jet_mask' or 'jet_mask_nom' for the systematic {}".format(sysVar))
                if verbose:
                    print(calculationWeightBefore)
                #For calculating the yeild ratio, we need this weight, which will be the product of calculationWeightBefore and the product of btag SFs (no yield ratio!)
                calculationWeightAfter = "calcBtagYields_after{spf}".format(spf=syspostfix)
                #Define the form of the final name of the btagSFProduct * YieldRatio(HT, nJet)
                #This needs to match what will be picked up in the final weight definitions!
                btagFinalWeight = "pwgt_btag{spf}".format(spf=syspostfix)
                
                #Lets be really obvious about missing jet_masks... exception it
                if jetMask not in listOfColumns:
                    raise RuntimeError("Could not find {} column in method BTaggingYields".format(jetMask))
                    
                #Skip SFs for which the requisite per-jet SFs are not present...
                if jetSF not in listOfColumns:
                    if verbose: print("Skipping {} in BTaggingYields as it is not a valid column name".format(jetSF))
                    continue
                        
                #Check we have the input weight for before btagSF and yield ratio multiplication
                if calculationWeightBefore not in listOfColumns:
                    raise RuntimeError("{} is not defined, cannot continue with calculating BTaggingYields".format(calculationWeightBefore))
                
                #Now check if the event preweight SF is in the list of columns, and if not, define it (common to calculating yields and loading them...)
                #We might want to call this function twice to calculate yields for a future iteration and use an older iteration at the same time
                if btagSFProduct not in listOfColumns:
                    # if calculateYields and btagSFProduct not in histosDict["BTaggingYields"].keys():
                    #     histosDict["BTaggingYields"][btagSFProduct] = {}
                    bTaggingDefineNodes[eraAndSampleName][sysVar].append(("{}".format(btagSFProduct), "FTA::btagEventWeight_shape({}, {})".format(jetSF, jetMask)))
                if calculationWeightAfter not in listOfColumns:
                    bTaggingDefineNodes[eraAndSampleName][sysVar].append(("{}".format(calculationWeightAfter), "{} * {}".format(calculationWeightBefore, 
                                                                                                                                 btagSFProduct)))
                        
                #Check that the HT and nJet numbers are available to us, and if not, define them based on the available masks    
                #if isScaleVariation:
                nJetName = "nFTAJet{bpf}".format(bpf=branchpostfix)
                HTName = "HT{bpf}".format(bpf=branchpostfix)
                if nJetName not in listOfColumns:
                    bTaggingDefineNodes[eraAndSampleName][sysVar].append((nJetName, "{0}[{1}].size()".format(jetPt, jetMask)))
                if HTName not in listOfColumns:
                    bTaggingDefineNodes[eraAndSampleName][sysVar].append((HTName, "Sum({0}[{1}])".format(jetPt, jetMask)))
                    
                #loadYields path...
                if loadYields:
                    pass
                    #Deprecated this part, now done after all systematics are run over in the node
                    # bTaggingDefineNodes[eraAndSampleName][sysVar].append((btagFinalWeight, "if({ht} > 550 && {ht} < 551 && {nj} == 8)std::cout << \"Original: \" << {nj} << \" \" << {ht} << \" \" << {bsf} << \" \" << \"{lm}\" << \" \" << \"{pn}\" << \" \" << {lm}[\"{pn}\"][rdfslot_]->getEventYieldRatio(\"{lk}\", {nj}, {ht}) << std::endl; return {bsf} * {lm}[\"{pn}\"][rdfslot_]->getEventYieldRatio(\"{lk}\", {nj}, {ht});".format(bsf=btagSFProduct, lm=lookupMap, pn=eraAndSampleName, lk=yieldsKey+syspostfix, nj=nJetName, ht=HTName))) #.replace("__", "_")
                    # bTaggingDefineNodes[eraAndSampleName][sysVar].append((btagFinalWeight, "{bsf} * {lm}[\"{pn}\"][rdfslot_]->getEventYieldRatio(\"{lk}\", {nj}, {ht});".format(bsf=btagSFProduct, lm=lookupMap, pn=eraAndSampleName, lk=yieldsKey+syspostfix, nj=nJetName, ht=HTName))) #.replace("__", "_")
                    # compareMethods.append(btagFinalWeight)

                for defName, defFunc in bTaggingDefineNodes[eraAndSampleName][sysVar]:
                    if defName in listOfColumns:
                        if verbose:
                            print("{} already defined, skipping".format(defName))
                        continue
                    else:
                        if verbose:
                            print("nodes[eraAndSampleName][\"BaseNode\"] = nodes[eraAndSampleName][\"BaseNode\"].Define(\"{}\", \"{}\")".format(defName, defFunc))
                        nodes[eraAndSampleName]["BaseNode"] = nodes[eraAndSampleName]["BaseNode"].Define(defName, defFunc)
                        listOfColumns.push_back(defName)        

        
         #            test = nodes[eraAndSampleName]["BaseNode"].Define("testThis", "{lm}[\"{sn}\"][rdfslot_]->getEventYieldRatio(\"{yk}\", \"{spf}\", {nj}, {ht}, true);".format(bsf=btagSFProduct, lm=lookupMap,\
         # sn=eraAndSampleName, yk=yieldsKey, spf=syspostfix, nj=nJetName, ht=HTName)).Stats("testThis").GetMean()
                    # print("Debugging test: {}".format(test))
                    #calculate Yields path
                if calculateYields:
                    k = btagSFProduct
                    # histosDict["BTaggingYields"][k] = {}
                    #Prepare working variable-bin-size 2D models (root 6.20.04+ ?)
                    nJetArr = array.array('d', nJetArray)
                    nJet1Bin = array.array('d', [nJetArray[0], nJetArray[-1]])
                    HTArr = array.array('d', HTArray)
                    HT1Bin = array.array('d', [HTArray[0], HTArray[-1]])
                    
                    ModelBefore = ROOT.RDF.TH2DModel("{}_BTaggingYield_{}_sumW_before".format(eraAndSampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                     "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                     len(HTArr)-1, HTArr, len(nJetArr)-1, nJetArr)
                    ModelAfter = ROOT.RDF.TH2DModel("{}_BTaggingYield_{}_sumW_after".format(eraAndSampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                    "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                    len(HTArr)-1, HTArr, len(nJetArr)-1, nJetArr)
                    ModelBefore1DX = ROOT.RDF.TH2DModel("{}_BTaggingYield1DX_{}_sumW_before".format(eraAndSampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                        "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                        len(HTArr)-1, HTArr, 1, nJet1Bin)
                    ModelAfter1DX = ROOT.RDF.TH2DModel("{}_BTaggingYield1DX_{}_sumW_after".format(eraAndSampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                       "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                       len(HTArr)-1, HTArr, 1, nJet1Bin)
                    ModelBefore1DY = ROOT.RDF.TH2DModel("{}_BTaggingYield1DY_{}_sumW_before".format(eraAndSampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                        "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                        1, HT1Bin, len(nJetArr)-1, nJetArr)
                    ModelAfter1DY = ROOT.RDF.TH2DModel("{}_BTaggingYield1DY_{}_sumW_after".format(eraAndSampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                       "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                       1, HT1Bin, len(nJetArr)-1, nJetArr)
                    histosDict[eraAndSampleName][channel][k+"__sumW_before"] = nodes[eraAndSampleName]["BaseNode"].Histo2D(ModelBefore,
                                                                                                                 HTName,
                                                                                                                 nJetName,
                                                                                                                 calculationWeightBefore)
                    histosDict[eraAndSampleName][channel][k+"__sumW_after"] = nodes[eraAndSampleName]["BaseNode"].Histo2D(ModelAfter,
                                                                                                                HTName,
                                                                                                                nJetName,
                                                                                                                calculationWeightAfter)
                    #For Unified JetBinning calculation
                    histosDict[eraAndSampleName][channel][k+"__1DXsumW_before"] = nodes[eraAndSampleName]["BaseNode"].Histo2D(ModelBefore1DX,
                                                                                                                    HTName,
                                                                                                                    nJetName,
                                                                                                                    calculationWeightBefore)
                    histosDict[eraAndSampleName][channel][k+"__1DXsumW_after"] =  nodes[eraAndSampleName]["BaseNode"].Histo2D(ModelAfter1DX,
                                                                                                                    HTName,
                                                                                                                    nJetName,
                                                                                                                    calculationWeightAfter)
                    #For Unified HTBinning calculation
                    histosDict[eraAndSampleName][channel][k+"__1DYsumW_before"] = nodes[eraAndSampleName]["BaseNode"].Histo2D(ModelBefore1DY,
                                                                                                                    HTName,
                                                                                                                    nJetName,
                                                                                                                    calculationWeightBefore)
                    histosDict[eraAndSampleName][channel][k+"__1DYsumW_after"] =  nodes[eraAndSampleName]["BaseNode"].Histo2D(ModelAfter1DY,
                                                                                                                    HTName,
                                                                                                                    nJetName,
                                                                                                                    calculationWeightAfter)
            #Insert the new LUT method...
            if loadYields:
                era, processName = eraAndSampleName.split("___")
                nodes[eraAndSampleName]["BaseNode"] = ROOT.FTA.AddBTaggingYieldsRenormalization(ROOT.RDF.AsRNode(nodes[eraAndSampleName]["BaseNode"]), 
                                                                                                 era, 
                                                                                                 processName,
                                                                                                 vectorLUTs,
                                                                                                 correctorMap,
                                                                                             )
            #Conclusion of comparison: the old btagging method is somehow broken, the new one is picking up the CORRECT values from the HT2. The other inputs are the same...
            # for x in compareMethods:
            #     if x in listOfColumns:
            #         print("{} in columns, searching for altnernate".format(x))
            #         if "alt_{}".format(x) in nodes[eraAndSampleName]["BaseNode"].GetDefinedColumnNames():
            #             print(x, len(compareMethodsResults))
            #             compareMethodsResults.append(nodes[eraAndSampleName]["BaseNode"].Define("diff_{}".format(x), "double x = abs({} - alt_{})/{}; if(x > 0.533) std::cout << rdfentry_ << std::endl; return x;".format(x, x, x)).Stats("diff_{}".format(x)))
            #         else:
            #             print("alt_{} not found".format(x))
            #     else:
            #         print("skipping {}".format(x))
            # test3 = compareMethodsResults[3].GetValue()

        return input_df_or_nodes
        
def BTaggingEfficiencies(input_df, sampleName=None, era="2017", wgtVar="wgt_SUMW_PU_L1PF", isData = True, histosDict=None, 
               doDeepCSV=True, doDeepJet=True):
    validAlgos = []
    if doDeepCSV == True: validAlgos.append("DeepCSV")
    if doDeepJet == True: validAlgos.append("DeepJet")
    bTagWorkingPointDict = {
        '2016':{
            'DeepCSV':{'L': 0.2217, 'M': 0.6321, 'T': 0.8953, 'Var': 'btagDeepB'},
            'DeepJet':{ 'L': 0.0614, 'M': 0.3093, 'T': 0.7221, 'Var': 'btagDeepFlavB'}
        },
        '2017':{
            'CSVv2':{'L': 0.5803, 'M': 0.8838, 'T': 0.9693, 'Var': 'btagCSVV2'},
            'DeepCSV':{'L': 0.1522, 'M': 0.4941, 'T': 0.8001, 'Var': 'btagDeepB'},
            'DeepJet':{'L': 0.0521, 'M': 0.3033, 'T': 0.7489, 'Var': 'btagDeepFlavB'}
        },
        '2018':{
            'DeepCSV':{'L': 0.1241, 'M': 0.4184, 'T': 0.7527, 'Var': 'btagDeepB'},
            'DeepJet':{'L': 0.0494, 'M': 0.2770, 'T': 0.7264, 'Var': 'btagDeepFlavB'}
        }
    }
    if isData == True:
        pass
    else:
        theCats = collections.OrderedDict()
        theCats["Inclusive"] = "nGJet >= 4"
        theCats["nJet4"] = "nGJet == 4"
        theCats["nJet5"] = "nGJet == 5"
        theCats["nJet6"] = "nGJet == 6"
        theCats["nJet7"] = "nGJet == 7"
        theCats["nJet8+"] = "nGJet >= 8"
        
        input_df_defined = input_df.Define("GJet_hadronFlavour", "Jet_hadronFlavour[jet_mask]")
        input_df_defined = input_df_defined.Define("GJet_abseta", "abs(Jet_eta[jet_mask])")
        input_df_defined = input_df_defined.Define("GJet_bjet_mask", "GJet_hadronFlavour == 5")
        input_df_defined = input_df_defined.Define("GJet_cjet_mask", "GJet_hadronFlavour == 4")
        input_df_defined = input_df_defined.Define("GJet_udsgjet_mask", "GJet_hadronFlavour < 4")
        for algo in ["DeepJet", "DeepCSV"]:
            for wp in ["L", "M", "T"]:
                input_df_defined = input_df_defined.Define("GJet_{0}_{1}_mask".format(algo, wp),
                                                           "GJet_{0} > {1}".format(bTagWorkingPointDict[era][algo]["Var"],
                                                                                bTagWorkingPointDict[era][algo][wp]))
        
        for jettype in ["bjet", "cjet", "udsgjet"]:
            input_df_defined = input_df_defined.Define("GJet_{}_untagged_pt".format(jettype), "GJet_pt[GJet_{}_mask]".format(jettype))
            input_df_defined = input_df_defined.Define("GJet_{}_untagged_abseta".format(jettype), "GJet_abseta[GJet_{}_mask]".format(jettype))
            for algo in validAlgos:
                for wp in ["L", "M", "T"]:
                    input_df_defined = input_df_defined.Define("GJet_{0}_{1}_{2}_pt".format(jettype, algo, wp), "GJet_pt[GJet_{0}_mask && GJet_{1}_{2}_mask]".format(jettype, algo, wp))
                    input_df_defined = input_df_defined.Define("GJet_{0}_{1}_{2}_abseta".format(jettype, algo, wp), "GJet_abseta[GJet_{0}_mask && GJet_{1}_{2}_mask]".format(jettype, algo, wp))
                    
        cat_df = collections.OrderedDict()
        for ck, cs in theCats.items():
            cat_df[ck] = input_df_defined.Filter(cs, "btagging " + cs)
        if histosDict != None:
            if "BTagging" not in histosDict:
                histosDict["BTagging"] = {}
            for tc in theCats.keys(): 
                if tc not in histosDict["BTagging"]: 
                    histosDict["BTagging"][tc] = {}
            for tc, cut in theCats.items():
                tcn = tc.replace("blind_", "")
                for jettype in ["bjet", "cjet", "udsgjet"]:
                    histosDict["BTagging"][tc]["{}s_untagged".format(jettype)] = cat_df[tc].Histo2D(("{0}s_untagged_[{0}]({1})".format(tcn, wgtVar), ";jet p_{T}; jet |#eta|", 248, 20, 2500, 25, 0, 2.5), 
                                                                                                     "GJet_{}_untagged_pt".format(jettype), "GJet_{}_untagged_abseta".format(jettype), wgtVar)
                    for algo in validAlgos:
                        for wp in ["L", "M", "T"]:
                            histosDict["BTagging"][tc]["{0}s_{1}_{2}".format(jettype, algo, wp)] = cat_df[tc].Histo2D(("{0}s_{1}_{2}_[{0}]({3})".format(tcn, algo, wp, wgtVar), ";jet p_{T}; jet |#eta|", 248, 20, 2500, 25, 0, 2.5), 
                                                                                                             "GJet_{0}_{1}_{2}_pt".format(jettype, algo, wp), "GJet_{0}_{1}_{2}_abseta".format(jettype, algo, wp), wgtVar)
                            

def jetMatchingEfficiency(input_df, max_eta = 2.5, min_pt = 30.0, wgtVar="wgt_SUMW_PU_L1PF", stats_dict=None,
                         isData=True):
    if isData == True:
        pass
    else:
        theCats = dict()
        #Subtract 2 for the GenJets which are actually leptons
        theCats["nGenJet2"] = "jetmatch_nGenJet == 4"
        theCats["nGenJet3"] = "jetmatch_nGenJet == 5"
        theCats["nGenJet4"] = "jetmatch_nGenJet == 6"
        theCats["nGenJet5"] = "jetmatch_nGenJet == 7"
        theCats["nGenJet6"] = "jetmatch_nGenJet == 8"
        theCats["nGenJet7"] = "jetmatch_nGenJet == 9"
        theCats["nGenJet8"] = "jetmatch_nGenJet == 10"
        theCats["nGenJet9"] = "jetmatch_nGenJet == 11"
        theCats["nGenJet10+"] = "jetmatch_nGenJet >= 12"
        #define genjets as needed for this study
        input_df_defined = input_df.Define("jetmatch_nGenJet", "GenJet_pt[GenJet_pt >= {}  && abs(GenJet_eta) <= {}].size()".format(min_pt, max_eta))
        cat_df = dict()
        for ck, cs in theCats.items():
            cat_df[ck] = input_df_defined.Filter(cs, "Jet Matching Efficiency " + cs)
            stats_dict[ck] = {}
            stats_dict[ck]["nJet"] = cat_df[ck].Stats("nGJet", wgtVar)
            stats_dict[ck]["nJet_genMatched"] = cat_df[ck].Stats("nGJet_genMatched", wgtVar)
            stats_dict[ck]["nJet_puIdLoose"] = cat_df[ck].Stats("nGJet_puIdLoose", wgtVar)
            stats_dict[ck]["nJet_genMatched_puIdLoose"] = cat_df[ck].Stats("nGJet_genMatched_puIdLoose", wgtVar)

def fillHLTMeans(input_df, wgtVar="wgt_SUMW_PU_L1PF", stats_dict=None):
    theCats = dict()
    theCats["Inclusive"] = "nGJet >= 4"
    theCats["nJet4to5"] = "nGJet == 4 || nGJet == 5"
    theCats["nJet6+"] = "nGJet >= 6"
    
    branches = [branch for branch in input_df.GetColumnNames() if "HLT_" in str(branch) and "Ele" not in str(branch)
                and "Mu" not in str(branch) and "Tau" not in str(branch)]
                #and ("PF" in branch or "HT" in branch or "MET" in branch)]
    #print(branches)
    
    input_df_defined = input_df
    branches_weighted = []
    for branch in branches:
        branches_weighted.append("{}_weighted".format(branch))
        input_df_defined = input_df_defined.Define("{}_weighted".format(branch), 
                                                   "{} == true ? {} : 0".format(branch, wgtVar))
                
    cat_df = dict()
    for ck, cs in theCats.items():
        cat_df[ck] = input_df_defined.Filter(cs, "HLT Report " + cs)
    if stats_dict != None:
        if "unweighted" not in stats_dict:
            stats_dict["unweighted"] = {}
        if "weighted" not in stats_dict:
            stats_dict["weighted"] = {}
        if "weightedStats" not in stats_dict:
            stats_dict["weightedStats"] = {}
        if "weightedStatsSMT" not in stats_dict:
            stats_dict["weightedStatsSMT"] = {}
        if "counts" not in stats_dict:
            stats_dict["counts"] = {}
        for tc, cut in theCats.items():
            if tc not in stats_dict["unweighted"]: 
                stats_dict["unweighted"][tc] = {}
            if tc not in stats_dict["weighted"]: 
                stats_dict["weighted"][tc] = {}
            if tc not in stats_dict["weightedStats"]: 
                stats_dict["weightedStats"][tc] = {}
            if tc not in stats_dict["weightedStatsSMT"]: 
                stats_dict["weightedStatsSMT"][tc] = {}
            if tc not in stats_dict["counts"]: 
                stats_dict["counts"][tc] = cat_df[tc].Count()
            for branch in branches:
                stats_dict["unweighted"][tc]["{}".format(branch)] = cat_df[tc].Sum("{}".format(branch)) #instead of mean
                stats_dict["weightedStatsSMT"][tc]["{}".format(branch)] = cat_df[tc].Stats("{}".format(branch), wgtVar)
            for branch in branches_weighted:
                stats_dict["weighted"][tc]["{}".format(branch)] = cat_df[tc].Sum("{}".format(branch)) 
                stats_dict["weightedStats"][tc]["{}".format(branch)] = cat_df[tc].Stats("{}".format(branch))

def histoCombine(directory, outDirectory="{}/Combine", globKey="*.root", stripKey=".root", internalSeperator="*",
                systematicSeperator="__", mode="RECREATE"):
    """take list of files in <directory>, with optional <globKey>, and create individual root files containing
    each sample (nominal and systematic variation) for each histogram category. Keys can be parsed with 
    <internalSeperator> (default '*') and <systematicSeperator> (default '__') such that file 'ttWH.root' with
    'Mountains*nJet4*DeepCSV_jet1__JESup' will generate a file 'nJet4_DeepCSV_jet1.root' containing the systematic 
    variation histogram 'ttWH_JESup'"""
    if "{}/" in outDirectory:
        outDirectory = outDirectory.format(directory)
    if not os.path.isdir(outDirectory):
        print("Checking for (and if necessary, creating) directory {}".format(outDirectory))
        os.makedirs(outDirectory)
    #Get the files
    if 'glob' not in dir():
        try:
            import glob
        except Exception as e:
            raise RuntimeError("Could not import the glob module in method histoCombine")
    files = glob.glob("{}/{}".format(directory, globKey))
    #deduce names from the filenames, with optional stripKey parameter that defaults to .root
    names = [fname.split("/")[-1].replace(stripKey, "") for fname in files]
    fileDict = {}
    keysDict = {}
    nominalDict = {}
    keySet = set([])
    for name, fname in zip(names, files):
        #inFiles
        fileDict[name] = ROOT.TFile.Open(fname)
        #hist names
        keysDict[name] = [hist.GetName() for hist in fileDict[name].GetListOfKeys()]
        #for creation of outFiles (group nominal + systematic variations!)
        nominalDict[name] = [hist.split("{}".format(systematicSeperator))[0] for hist in keysDict[name]]
        keySet = keySet.union(set(nominalDict[name]))
    #start parsing to generate outFile names
    for outname_raw in keySet:
        splt = outname_raw.split("{}".format(internalSeperator))
        n = len(splt)
        if n == 1:
            var = splt[0]
        elif n == 2:
            cat, var = splt
        elif n == 3:
            super_cat, cat, var = splt
        #ignore super_cat names for now, create the name with the outDirectory and guard against doubled '/' character
        outname = "{}/{}_{}.root".format(outDirectory, cat, var).replace("//", "/")
        oFile = ROOT.TFile.Open(outname, mode)
        for name, hNameList_raw in keysDict.items():
            hNameList = [hName for hName in hNameList_raw if outname_raw == hName.split("{}".format(systematicSeperator))[0]]
            for hName in hNameList:
                hist = fileDict[name].Get(hName)
                original_name = hist.GetName()
                #format the new name by replacing the non-systematic portion with the sample's name
                new_name = hName.replace(outname_raw, name)
                hist.SetName(new_name)
                hist.Write()
                hist.SetName(original_name)
        oFile.Close()
        
def BTaggingYieldsAnalyzer(directory, outDirectory="{}", globKey="*.root", stripKey=".root", includeSampleNames=None, 
                           excludeSampleNames=None, mode="RECREATE", doNumpyValidation=False, forceDefaultRebin=False, verbose=False,
                           internalKeys = {"Numerators":["_sumW_before"],
                                           "Denominator": "_sumW_after",
                                          },
                           internalKeysReplacements = {"BTaggingYield": "",
                                                       "_sumW_before": "",
                                                       "_sumW_after": "",
                                                      },
                           sampleRebin={"default": {"Y": [4, 5, 6, 7, 8, 9, 20],
                                                     "X": [500.0, 600, 700.0, 900.0, 1100.0, 3200.0],
                                                    },
                                         },
                           overrides={"Title": "$NAME BTaggingYield r=#frac{#Sigma#omega_{before}}{#Sigma#omega_{after}}($INTERNALS)",
                                      "Xaxis": "H_{T} (GeV)",
                                      "Yaxis": "nJet",
                                     },
                          ):
    """For btagging yield ratio calculations using method 1d (shape corrections)
    
    take list of files in <directory>, with optional <globKey>, and create individual root files containing
    each sample's btagging yield ratio histograms, based on derived categories. 
    
    Keys can be parsed with a dictionary called <internalKeys>, which should have a key "Numerators" with a list of unique strings for identifying numerator histograms.
    Another key, "Denominator", should be a string key (single) that uniquely identifies denominator histograms. Keys will be searched for these string contents.
    For naming final yield ratios, the dictionary <internalKeysReplacements> takes a dictionary of key-value pairs where keys present in histogram names are replaced by the values
    <sampleRebin> is a nested set of dictionaries. "default" must always be present, with keys for "Y" and "X" to provide lists of the bin edges for 2D rebinning.
    <overrides> is a dictionary with keys "Title", "Xaxis", and "Yaxis" for overwriting those properties. Special identifiers $NAME and $INTERNALS
    will be replaced with the name of the sample (Aggregate for weighted sum of all samples) and the systematic variation, respectively
    <doNumpyValidation> toggles a numpy based calculation of errors to shadow ROOTs internal computation from adding and dividing histograms. This toggles <forceDefaultRebin>
    <forceDefaultRebin> will ignore sample-specific rebinning schemes in the sampleRebin dictionary and force the default to be used instead
    """
    
    if doNumpyValidation == True:
        #FORCE consistent binning and warn the user
        print("Setting rebinning to the default")
        forceDefaultRebin = True
        if 'numpy' not in dir() and 'np' not in dir():
            try:
                import numpy as np
            except Exception as e:
                raise RuntimeError("Could not import the numpy (as np) module in method BTaggingYieldsAnalyzer")
    
    if "{}" in outDirectory:
        outDirectory = outDirectory.format(directory)
    print("Checking for (and if necessary, creating) directory {}".format(outDirectory))
    if not os.path.isdir(outDirectory):
        os.makedirs(outDirectory)
    #Get the files
    if 'glob' not in dir():
        try:
            import glob
        except Exception as e:
            raise RuntimeError("Could not import the glob module in method BTaggingYieldsAnalyzer")
    if 'copy' not in dir():
        try:
            import copy
        except Exception as e:
            raise RuntimeError("Could not import the copy module in method BTaggingYieldsAnalyzer")
    files = glob.glob("{}/{}".format(directory, globKey))
    if includeSampleNames:
        if verbose:
            print("Including these files: {}".format([f for f in files if f.split("/")[-1].replace(".root", "") in includeSampleNames]))
        files = [f for f in files if f.split("/")[-1].replace(".root", "") in includeSampleNames and f.split("/")[-1].replace(".root", "") not in ["BTaggingYields"]]
    elif excludeSampleNames:
        if verbose:
            print("Excluding these files: {}".format([f for f in files if f.split("/")[-1].replace(".root", "") in excludeSampleNames]))
        files = [f for f in files if f.split("/")[-1].replace(".root", "") not in excludeSampleNames and f.split("/")[-1] not in ["BTaggingYields"]]
    else:
        files = [f for f in files if f.split("/")[-1].replace(".root", "") not in ["BTaggingYields"]]
    #deduce names from the filenames, with optional stripKey parameter that defaults to .root
    names = [fname.split("/")[-1].replace(stripKey, "") for fname in files]
    fileDict = {}
    oFile = ROOT.TFile.Open("{}/BTaggingYields.root".format(outDirectory).replace("//", "/"), mode)
    keysDict = {}
    numerators_dict = {}
    denominator_dict = {}
    #For storing numpy contents to validate error and efficiency calculations
    yield_dict = {}
    yield_dict_num = {}
    yield_dict_den = {}
    yield_err_dict = {}
    yield_err_dict_num = {}
    yield_err_dict_den = {}
    for name, fname in zip(names, files):
        print(name)
        #prepare histogram dictionaries
        numerators_dict[name] = {}
        denominator_dict[name] = {}
        yield_dict[name] = {}
        yield_dict_num[name] = {}
        yield_dict_den[name] = {}
        yield_err_dict[name] = {}
        yield_err_dict_num[name] = {}
        yield_err_dict_den[name] = {}
        #Aggregate only works if it's done before rebinning, should per-sample settings be done
        if "Aggregate" not in numerators_dict.keys():
            numerators_dict["Aggregate"] = {}
            denominator_dict["Aggregate"] = {}
            yield_dict["Aggregate"] = {}
            yield_dict_num["Aggregate"] = {}
            yield_dict_den["Aggregate"] = {}
            yield_err_dict["Aggregate"] = {}
            yield_err_dict_num["Aggregate"] = {}
            yield_err_dict_den["Aggregate"] = {}
        #inFiles
        fileDict[name] = ROOT.TFile.Open(fname, "READ")
        #hist names
        keysDict[name] = [hist.GetName() for hist in fileDict[name].GetListOfKeys()]
        #Create tuples of names for the numerator and matching denominator histogram
        #replace the name if at the beginning, for cleaner keys
        uniqueTuples = [(tbr, hist.replace("{}_".format(name), ""), hist.replace(tbr, internalKeys.get("Denominator")).replace("{}_".format(name), "")) for hist in keysDict[name] for tbr in internalKeys.get("Numerators", ["NothingHere"]) if tbr in hist]
        
        #Get the rebinning lists with a default fallback, but it will be forced when doNumpyValidation is true
        if forceDefaultRebin == False:
            x_rebin = sampleRebin.get(name, sampleRebin.get("default"))["X"]
            y_rebin = sampleRebin.get(name, sampleRebin.get("default"))["Y"]
        else:
            x_rebin = sampleRebin.get("default")["X"]
            y_rebin = sampleRebin.get("default")["Y"]
            
        #index everything by the numerator for later naming purposes: $SAMPLENAME_$NUMERATOR style
        for tbr, stripped_numerator, stripped_denominator in uniqueTuples:
            numerator = "{}_{}".format(name, stripped_numerator)
            denominator = "{}_{}".format(name, stripped_denominator)
            #Rebinning for this specific numerator. If "1DY" or "1DX" is in the name, there's only 1 bin 
            #in the other axis, i.e. 1DY = normal Y bins, 1 X bin
            this_y_rebin = copy.copy(y_rebin)
            this_x_rebin = copy.copy(x_rebin)
            #Not needed anymore, explicit maps created
            # if "1DY" in numerator:
            #     this_x_rebin = [x_rebin[0]] + [x_rebin[-1]]
            # if "1DX" in numerator:
            #     this_y_rebin = [y_rebin[0]] + [y_rebin[-1]]
                
            internals = copy.copy(stripped_numerator)
            for k, v in internalKeysReplacements.items():
                internals = internals.replace(k, v)
            
            #Get the original numerator/denominator histograms...
            numerators_dict[name][numerator] = fileDict[name].Get(numerator)
            denominator_dict[name][numerator] = fileDict[name].Get(denominator) #Yeah, this will be duplicated x (number of numerators per denominator)
            if stripped_numerator not in numerators_dict["Aggregate"].keys():
                numerators_dict["Aggregate"][stripped_numerator] = numerators_dict[name][numerator].Clone("{}".format(stripped_numerator.replace(tbr, "")))
                denominator_dict["Aggregate"][stripped_numerator] = denominator_dict[name][numerator].Clone("{}_denominator".format(stripped_numerator.replace(tbr, "")))
                numerators_dict["Aggregate"][stripped_numerator].SetDirectory(0)
                denominator_dict["Aggregate"][stripped_numerator].SetDirectory(0)
            else:
                numerators_dict["Aggregate"][stripped_numerator].Add(numerators_dict[name][numerator])
                denominator_dict["Aggregate"][stripped_numerator].Add(denominator_dict[name][numerator])
                
            #Do rebinning, with flow control for optional numpy validation calculations
            if doNumpyValidation:
                numerators_dict[name][numerator], yield_dict_num[name][numerator], yield_err_dict_num[name][numerator] =                                                                                                                rebin2D(numerators_dict[name][numerator],
                                                                "{}_{}".format(name, internals),
                                                                this_x_rebin,
                                                                this_y_rebin,
                                                                return_numpy_arrays=True,
                                                                )
                denominator_dict[name][numerator], yield_dict_den[name][numerator], yield_err_dict_den[name][numerator] =                                                                                                               rebin2D(denominator_dict[name][numerator],
                                                                "{}_{}_denominator".format(name, internals),
                                                                this_x_rebin,
                                                                this_y_rebin,
                                                                return_numpy_arrays=True,
                                                                )
                if stripped_numerator not in yield_dict_num["Aggregate"].keys():
                    yield_dict_num["Aggregate"][stripped_numerator] = np.copy(yield_dict_num[name][numerator])
                    yield_dict_den["Aggregate"][stripped_numerator] = np.copy(yield_dict_den[name][numerator])
                    yield_err_dict_num["Aggregate"][stripped_numerator] = np.copy(yield_err_dict_num[name][numerator])
                    yield_err_dict_den["Aggregate"][stripped_numerator] = np.copy(yield_err_dict_den[name][numerator])
                else:
                    np.add(
                        yield_dict_num["Aggregate"][stripped_numerator],
                        yield_dict_num[name][numerator],
                        out=yield_dict_num["Aggregate"][stripped_numerator]
                    )
                    np.add(
                        yield_dict_den["Aggregate"][stripped_numerator],
                        yield_dict_den[name][numerator],
                        out=yield_dict_den["Aggregate"][stripped_numerator]
                    )
                    np.sqrt(
                        np.square(yield_err_dict_num["Aggregate"][stripped_numerator]) + 
                        np.square(yield_err_dict_num[name][numerator]),
                        out=yield_err_dict_num["Aggregate"][stripped_numerator]
                    )
                    np.sqrt(
                        np.square(yield_err_dict_num["Aggregate"][stripped_numerator]) + 
                        np.square(yield_err_dict_num[name][numerator]),
                        out=yield_err_dict_num["Aggregate"][stripped_numerator]
                    )
            else:
                numerators_dict[name][numerator] = rebin2D(numerators_dict[name][numerator],
                                                           "{}_{}".format(name, internals),
                                                           this_x_rebin,
                                                           this_y_rebin,
                                                          )
                denominator_dict[name][numerator] = rebin2D(denominator_dict[name][numerator],
                                                            "{}_{}_denominator".format(name, internals),
                                                            this_x_rebin,
                                                            this_y_rebin,
                                                            )
                yield_dict_num[name][numerator] = None
                yield_dict_den[name][numerator] = None
                yield_err_dict_num[name][numerator] = None
                yield_err_dict_den[name][numerator] = None
                
            #Do the yield division
            #numerators_dict[name][numerator].GetXaxis().SetRange(1, jets_dict[name][jettype][cat][tag].GetNbinsX())
            numerators_dict[name][numerator].Divide(denominator_dict[name][numerator])
            #Do some overrides to change titles, axis laabels...
            if overrides != None:
                internals = copy.copy(stripped_numerator)
                for k, v in internalKeysReplacements.items():
                    internals = internals.replace(k, v)
                otitle = overrides["Title"].replace("$NAME", name).replace("$INTERNALS", internals)
                oxaxis = overrides["Xaxis"]
                oyaxis = overrides["Yaxis"]
                numerators_dict[name][numerator].SetTitle(otitle)
                numerators_dict[name][numerator].GetXaxis().SetTitle(oxaxis)
                numerators_dict[name][numerator].GetYaxis().SetTitle(oyaxis)
                #make sure we're back here...
                oFile.cd()
                numerators_dict[name][numerator].Write()
                #renaming to prevent name clash with other samples isn't necessary if name included, so this is just a reminder in case that changes
            if doNumpyValidation:
                yield_err_dict_num[name][numerator], yield_err_dict_num[name][numerator] = numpyDivAndError(
                    yield_dict_num[name][numerator],
                    yield_err_dict_num[name][numerator], 
                    yield_dict_den[name][numerator], 
                    yield_err_dict_den[name][numerator]
                )
        #close the input file
        fileDict[name].Close()    
                    
    #Do aggregate calculations...
    #Loop through all the aggregate histograms and write them
    name = "Aggregate"
    print(name)
    #Get the rebinning lists with a default fallback, but it will be forced when doNumpyValidation is true
    if forceDefaultRebin == False:
        x_rebin = sampleRebin.get(name, sampleRebin.get("default"))["X"]
        y_rebin = sampleRebin.get(name, sampleRebin.get("default"))["Y"]
    else:
        x_rebin = sampleRebin.get("default")["X"]
        y_rebin = sampleRebin.get("default")["Y"]
    for numerator in numerators_dict["Aggregate"].keys():
        #Rebinning for this specific numerator. If "1DY" or "1DX" is in the name, there's only 1 bin 
        #in the other axis, i.e. 1DY = normal Y bins, 1 X bin
        that_y_rebin = copy.copy(y_rebin)
        that_x_rebin = copy.copy(x_rebin)
        #Not needed
        # if "1DY" in numerator:
        #     that_x_rebin = [x_rebin[0]] + [x_rebin[-1]]
        # if "1DX" in numerator:
        #     that_y_rebin = [y_rebin[0]] + [y_rebin[-1]]
        #Form the replacement values for the name, i.e. Aggregate1DX___nom
        internals = copy.copy(numerator)
        for k, v in internalKeysReplacements.items():
            internals = internals.replace(k, v)
        if doNumpyValidation:
            numerators_dict[name][numerator], yield_dict_num[name][numerator + "Cross"], yield_err_dict_num[name][numerator + "Cross"] =                                                             rebin2D(numerators_dict[name][numerator],
                                                            "{}{}".format(name, internals),
                                                            that_x_rebin,
                                                            that_y_rebin,
                                                            return_numpy_arrays=True,
                                                            )
            denominator_dict[name][numerator], yield_dict_den[name][numerator + "Cross"], yield_err_dict_den[name][numerator + "Cross"] =                                                             rebin2D(denominator_dict[name][numerator],
                                                            "{}{}_denominator".format(name, internals),
                                                            that_x_rebin,
                                                            that_y_rebin,
                                                            return_numpy_arrays=True,
                                                            )
        else:
            numerators_dict[name][numerator] = rebin2D(numerators_dict[name][numerator],
                                                        "{}{}".format(name, internals),
                                                        that_x_rebin,
                                                        that_y_rebin,
                                                        )
            denominator_dict[name][numerator] = rebin2D(denominator_dict[name][numerator],
                                                        "{}{}_denominator".format(name, internals),
                                                        that_x_rebin,
                                                        that_y_rebin,
                                                        )
        #Do the yield division
        #numerators_dict[name][numerator].GetXaxis().SetRange(1, jets_dict[name][jettype][cat][tag].GetNbinsX())
        numerators_dict[name][numerator].Divide(denominator_dict[name][numerator])
        #Do some overrides to change titles, axis laabels...
        if overrides != None:
            otitle = overrides["Title"].replace("$NAME", name).replace("$INTERNALS", internals)
            oxaxis = overrides["Xaxis"]
            oyaxis = overrides["Yaxis"]
            numerators_dict[name][numerator].SetTitle(otitle)
            numerators_dict[name][numerator].GetXaxis().SetTitle(oxaxis)
            numerators_dict[name][numerator].GetYaxis().SetTitle(oyaxis)
            #make sure we're back here...
            oFile.cd()
            numerators_dict[name][numerator].Write()
            #renaming to prevent name clash with other samples isn't necessary if name included, so this is just a reminder in case that changes
            if doNumpyValidation:
                yield_err_dict_num[name][numerator], yield_err_dict_num[name][numerator] = numpyDivAndError(
                    yield_dict_num[name][numerator],
                    yield_err_dict_num[name][numerator], 
                    yield_dict_den[name][numerator], 
                    yield_err_dict_den[name][numerator]
                )
    #close the output file
    oFile.Close() 
 
    
def BTaggingEfficienciesAnalyzer(directory, outDirectory="{}/BTaggingEfficiencies", globKey="*.root", stripKey=".root", 
                       name_format="BTagging*$CAT*$JETTYPE_$TAG",
                       format_dict={"categories": ["Inclusive", "nJet4", "nJet5", "nJet6", "nJet7", "nJet8+"],
                                    "jettypes": ["bjets", "cjets", "udsgjets"],
                                    "tags": ["DeepCSV_L", "DeepCSV_M", "DeepCSV_T", "DeepJet_L", "DeepJet_M", "DeepJet_T"],
                                    "untag": "untagged", 
                                   },
                       jettype_rebin={"bjets":{"Y": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5],
                                               "X": [20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 200.0, 2500.0],
                                              },
                                      "cjets":{"Y": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5],
                                               "X": [20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 200.0, 2500.0],
                                              },
                                      "udsgjets":{"Y": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5],
                                                  "X": [20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 200.0, 2500.0],
                                                 },
                                     },
                       overrides={"Title": "$NAME $JETTYPE $TAG Efficiency($CATEGORY)",
                                  "Xaxis": "Jet p_{T}",
                                  "Yaxis": "Jet |#eta|",
                                 },
                       mode="RECREATE",
                       doNumpyValidation=False,
                       debug=False,debug_dict={}):
    """For btagging event weight calculations using method 1a and similar (non-shape corrections)
    
    take list of files in <directory>, with optional <globKey>, and create individual root files containing
    each sample's btagging efficiency histograms, based on derived categories. Keys can be parsed with 
    <name_format> (default 'BTagging*$CAT*$JETTYPE_$TAG') where $CAT, $JETTYPE, and $TAG are cycled through from 
    their respective input lists, format_dict{<categories>, <jettypes>, <tags>}. The format_dict{<untag>} option 
    specifies the denominator histogram (where $TAG is replaced by <untag>). A file 'ttWH.root' with 
    'BTagging*nJet4*bjets_DeepJet_T' will generate a file 'ttWH_BTagEff.root' containing the histogram 
    'nJet4_bjets_DeepJet_T'"""
    
    #old binning in X:
    #"bjets":"X": [20.0, 30.0, 50.0, 70.0, 100.0, 2500.0],
    #"cjets":"X": [20.0, 30.0, 50.0, 60.0, 90.0, 2500.0],
    #"udsgjets":"X": [20.0, 30.0, 40.0, 60.0, 2500.0]
    
    if "{}/" in outDirectory:
        outDirectory = outDirectory.format(directory)
    print("Checking for (and if necessary, creating) directory {}".format(outDirectory))
    if not os.path.isdir(outDirectory):
        os.makedirs(outDirectory)
    #Get the files
    if 'glob' not in dir():
        try:
            import glob
        except Exception as e:
            raise RuntimeError("Could not import the glob module in method BTaggingEfficienciesAnalyzer")
    files = glob.glob("{}/{}".format(directory, globKey))
    #deduce names from the filenames, with optional stripKey parameter that defaults to .root
    names = [fname.split("/")[-1].replace(stripKey, "") for fname in files]
    fileDict = {}
    oFileDict = {}
    keysDict = {}
    nominalDict = {}
    keySet = set([])
    jets_dict = {}
    canvas_dict = {}
    untag = format_dict["untag"]
    #For storing numpy contents to compute chi-square between efficincy measurements
    eff_dict = {}
    eff_err_dict = {}
    for name, fname in zip(names, files):
        print(name)
        #prepare histogram dictionaries
        jets_dict[name] = {}
        canvas_dict[name] = {}
        eff_dict[name] = {}
        eff_err_dict[name] = {}
        if "Aggregate" not in jets_dict.keys(): 
            jets_dict["Aggregate"] = {}
        #if "Aggregate" not in canvas_dict.keys(): 
            canvas_dict["Aggregate"] = {}
        #if "Aggregate" not in eff_dict.keys():
            eff_dict["Aggregate"] = {}
        #if "Aggregate" not in eff_err_dict.keys():
            eff_err_dict["Aggregate"] = {}
        #inFiles
        fileDict[name] = ROOT.TFile.Open(fname, "READ")
        #hist names
        keysDict[name] = [hist.GetName() for hist in fileDict[name].GetListOfKeys() if "BTagging*" in hist.GetName()]
        #Skip files without BTagging 
        if len(keysDict[name]) == 0: 
            print("Skipping sample {} whose file contains no histograms containing 'BTagging*'".format(name))
            fileDict[name].Close()
            continue
        #outFiles
        oFileDict[name] = ROOT.TFile.Open("{}/{}_BTagEff.root".format(outDirectory, name).replace("//", "/"),
                                          "RECREATE"
                                         )
        #cycle through the jettypes
        for jettype in format_dict["jettypes"]:
            jets_dict[name][jettype] = {}
            canvas_dict[name][jettype] = {}
            eff_dict[name][jettype] = {}
            eff_err_dict[name][jettype] = {}
            #Assume all dictionaries are being filled together
            if jettype not in jets_dict["Aggregate"].keys(): 
                jets_dict["Aggregate"][jettype] = {}
            #if jettype not in canvas_dict["Aggregate"].keys(): 
                canvas_dict["Aggregate"][jettype] = {}
            #if jettype not in eff_dict["Aggregate"].keys():
                eff_dict["Aggregate"][jettype] = {}
            #if jettype not in eff_err_dict["Aggregate"].keys():
                eff_err_dict["Aggregate"][jettype] = {}
            #cycle through the categories
            for cat in format_dict["categories"]:
                jets_dict[name][jettype][cat] = {}
                canvas_dict[name][jettype][cat] = {}
                eff_dict[name][jettype][cat] = {}
                eff_err_dict[name][jettype][cat] = {}
                if cat not in jets_dict["Aggregate"][jettype].keys(): 
                    jets_dict["Aggregate"][jettype][cat] = {}
                #if cat not in canvas_dict["Aggregate"][jettype].keys(): 
                    canvas_dict["Aggregate"][jettype][cat] = {}
                #if cat not in eff_dict["Aggregate"][jettype].keys(): 
                    eff_dict["Aggregate"][jettype][cat] = {}
                #if cat not in eff_err_dict["Aggregate"][jettype].keys(): 
                    eff_err_dict["Aggregate"][jettype][cat] = {}
                keyWithTag = name_format.replace("$CAT", cat).replace("$JETTYPE", jettype)
                #make dict for the denominator histograms (untagged jets), but skip this category if it's not in the file
                if keyWithTag.replace("$TAG", untag) not in keysDict[name]: continue
                jets_dict[name][jettype][cat][untag] = fileDict[name].Get(keyWithTag.replace("$TAG", untag))
                #jets_dict[name][jettype][cat][untag].SetDirectory(0)
                if doNumpyValidation:
                    jets_dict[name][jettype][cat][untag], eff_dict[name][jettype][cat][untag], eff_err_dict[name][jettype][cat][untag] =                                                                   rebin2D(jets_dict[name][jettype][cat][untag],
                                                                   "{}_{}_{}_{}".format(name, cat, jettype, untag),
                                                                   jettype_rebin[jettype]["X"],
                                                                   jettype_rebin[jettype]["Y"],
                                                                   return_numpy_arrays=True,
                                                                  )
                else:
                    jets_dict[name][jettype][cat][untag] = rebin2D(jets_dict[name][jettype][cat][untag],
                                                                   "{}_{}_{}_{}".format(name, cat, jettype, untag),
                                                                   jettype_rebin[jettype]["X"],
                                                                   jettype_rebin[jettype]["Y"]
                                                                  )
                    eff_dict[name][jettype][cat][untag] = None
                    eff_err_dict[name][jettype][cat][untag] = None
                    
                if untag not in jets_dict["Aggregate"][jettype][cat].keys():
                    jets_dict["Aggregate"][jettype][cat][untag] = jets_dict[name][jettype][cat][untag].Clone("{}_{}_{}_{}".format("Aggregate", cat, jettype, untag))
                    jets_dict["Aggregate"][jettype][cat][untag].SetDirectory(0)
                    #If doNumpyValidation is false, these values will be None
                    if doNumpyValidation:
                        eff_dict["Aggregate"][jettype][cat][untag] = np.copy(eff_dict[name][jettype][cat][untag])
                        eff_err_dict["Aggregate"][jettype][cat][untag] = np.copy(eff_err_dict[name][jettype][cat][untag])
                elif doNumpyValidation:
                    jets_dict["Aggregate"][jettype][cat][untag].Add(jets_dict[name][jettype][cat][untag])
                    np.add(
                        eff_dict["Aggregate"][jettype][cat][untag], 
                        eff_dict[name][jettype][cat][untag],
                        out=eff_dict["Aggregate"][jettype][cat][untag]
                    )
                    np.sqrt(
                        np.square(eff_err_dict["Aggregate"][jettype][cat][untag]) + 
                        np.square(eff_err_dict[name][jettype][cat][untag]),
                        out=eff_err_dict["Aggregate"][jettype][cat][untag]
                        )
                else:
                    jets_dict["Aggregate"][jettype][cat][untag].Add(jets_dict[name][jettype][cat][untag])
                    
                if debug and jettype == "bjets" and cat in ["Inclusive"]:# and name in ["tt_DL-GF", "tt_DL", "tttt"]:
                    nums = jets_dict[name][jettype][cat][untag].GetBinContent(5, 6)
                    numa = jets_dict["Aggregate"][jettype][cat][untag].GetBinContent(5, 6) #x, y
                    print("untagged {} {} {}/{}".format(name, cat, nums, numa))
                    if doNumpyValidation:
                        numss = eff_dict[name][jettype][cat][untag][7, 5] #nYbins-1-y, x
                        numaa = eff_dict["Aggregate"][jettype][cat][untag][7, 5]
                        print("untagged {} {} numpy array {}/{}".format(name, cat, numss, numaa))
                #cycle through all the tag categories available
                for tag in format_dict["tags"]:
                    jets_dict[name][jettype][cat][tag] = fileDict[name].Get(keyWithTag.replace("$TAG", tag))
                    #jets_dict[name][jettype][cat][tag].SetDirectory(0) #Disassociates from the original file
                    #Rebin here...
                    if doNumpyValidation:
                        jets_dict[name][jettype][cat][tag], eff_dict[name][jettype][cat][tag], eff_err_dict[name][jettype][cat][tag] =                                                                   rebin2D(jets_dict[name][jettype][cat][tag],
                                                                   "{}_{}_{}".format(cat, jettype, tag),
                                                                   jettype_rebin[jettype]["X"],
                                                                   jettype_rebin[jettype]["Y"],
                                                                   return_numpy_arrays=True,
                                                                  )
                    else:
                        jets_dict[name][jettype][cat][tag] = rebin2D(jets_dict[name][jettype][cat][tag],
                                                                     "{}_{}_{}".format(cat, jettype, tag),
                                                                     jettype_rebin[jettype]["X"],
                                                                     jettype_rebin[jettype]["Y"]
                                                                    )
                    #Make or add to the aggregate histogram, and do numpy calcs if chi-square requested
                    if tag not in jets_dict["Aggregate"][jettype][cat].keys():
                        jets_dict["Aggregate"][jettype][cat][tag] = jets_dict[name][jettype][cat][tag].Clone("{}_{}_{}_{}".format("Aggregate", cat, jettype, tag))
                        jets_dict["Aggregate"][jettype][cat][tag].SetDirectory(0)
                        if doNumpyValidation:
                            eff_dict["Aggregate"][jettype][cat][tag] = np.copy(eff_dict[name][jettype][cat][tag])
                            eff_err_dict["Aggregate"][jettype][cat][tag] = np.copy(eff_err_dict[name][jettype][cat][tag])
                    elif doNumpyValidation:
                        jets_dict["Aggregate"][jettype][cat][tag].Add(jets_dict[name][jettype][cat][tag])
                        np.add(
                            eff_dict["Aggregate"][jettype][cat][tag], 
                            eff_dict[name][jettype][cat][tag],
                            out=eff_dict["Aggregate"][jettype][cat][tag]
                        )
                        np.sqrt(
                            np.square(eff_err_dict["Aggregate"][jettype][cat][tag]) + 
                            np.square(eff_err_dict[name][jettype][cat][tag]),
                            out=eff_err_dict["Aggregate"][jettype][cat][tag]
                        )
                    else:
                        jets_dict["Aggregate"][jettype][cat][tag].Add(jets_dict[name][jettype][cat][tag])
                        
                    if debug and jettype == "bjets" and cat == "Inclusive" and tag=="DeepCSV_M":#and name in ["tt_DL-GF", "tt_DL", "tttt"]:
                        nums = jets_dict[name][jettype][cat][tag].GetBinContent(5, 6)
                        numa = jets_dict["Aggregate"][jettype][cat][tag].GetBinContent(5, 6) #x, y
                        print("{} {} {} {}/{}".format(tag, name, cat, nums, numa))
                        if doNumpyValidation:
                            numss = eff_dict[name][jettype][cat][tag][7, 5] #nYbins-1-y, x
                            numaa = eff_dict["Aggregate"][jettype][cat][tag][7, 5]
                            print("{} {} {} numpy array {}/{}".format(tag, name, cat, numss, numaa))
                        
                    #Do the efficiency division
                    jets_dict[name][jettype][cat][tag].GetXaxis().SetRange(1, jets_dict[name][jettype][cat][tag].GetNbinsX())
                    jets_dict[name][jettype][cat][tag].Divide(jets_dict[name][jettype][cat][untag])
                    #Do some overrides to change titles, axis laabels...
                    if overrides != None:
                        otitle = overrides["Title"].replace("$NAME", name).replace("$JETTYPE", jettype).replace("$TAG", tag).replace("$CATEGORY", cat)
                        oxaxis = overrides["Xaxis"]
                        oyaxis = overrides["Yaxis"]
                        jets_dict[name][jettype][cat][tag].SetTitle(otitle)
                        jets_dict[name][jettype][cat][tag].GetXaxis().SetTitle(oxaxis)
                        jets_dict[name][jettype][cat][tag].GetYaxis().SetTitle(oyaxis)
                        
                    jets_dict[name][jettype][cat][tag].Write()
                    #rename to prevent name clash with other samples
                    jets_dict[name][jettype][cat][tag].SetName("{}_{}_{}_{}".format(name, cat, jettype, tag))
                    
                    if doNumpyValidation:
                        eff_dict[name][jettype][cat][tag], eff_err_dict[name][jettype][cat][tag] = numpyDivAndError(
                            eff_dict[name][jettype][cat][tag],
                            eff_err_dict[name][jettype][cat][tag], 
                            eff_dict[name][jettype][cat][untag], 
                            eff_err_dict[name][jettype][cat][untag]
                        )
                    
        fileDict[name].Close()
        oFileDict[name].Close()
        
    #Loop through all the aggregate histograms and write them to a separate file. 
    aggregateFile = ROOT.TFile.Open("{}/{}_BTagEff.root".format(outDirectory, "Aggregate").replace("//", "/"),
                                          "RECREATE")
    for jettype, jettype_dict in jets_dict["Aggregate"].items():
        for cat, cat_dict in jettype_dict.items():
            for tag, tag_hist in cat_dict.items():
                jets_dict["Aggregate"][jettype][cat][tag].Divide(jets_dict["Aggregate"][jettype][cat][untag])
                jets_dict["Aggregate"][jettype][cat][tag].SetName("{}_{}_{}".format(cat, jettype, tag))
                #Override the title, Xaxis, Yaxis for the histogram
                if overrides != None:
                    otitle = overrides.get("Title", "NONE").replace("$NAME", name).replace("$JETTYPE", jettype).replace("$TAG", tag).replace("$CATEGORY", cat)
                    oxaxis = overrides.get("Xaxis", "NONE")
                    oyaxis = overrides.get("Yaxis", "NONE")
                    if otitle != "NONE":
                        jets_dict["Aggregate"][jettype][cat][tag].SetTitle(otitle)
                    if oxaxis != "NONE":
                        jets_dict["Aggregate"][jettype][cat][tag].GetXaxis().SetTitle(oxaxis)
                    if oyaxis != "NONE":
                        jets_dict["Aggregate"][jettype][cat][tag].GetYaxis().SetTitle(oyaxis)
                jets_dict["Aggregate"][jettype][cat][tag].Write()
                jets_dict["Aggregate"][jettype][cat][tag].SetName("{}_{}_{}_{}".format("Aggregate", cat, jettype, tag))
                if doNumpyValidation:
                    eff_dict["Aggregate"][jettype][cat][tag], eff_err_dict["Aggregate"][jettype][cat][tag] = numpyDivAndError(
                        eff_dict["Aggregate"][jettype][cat][tag],
                        eff_err_dict["Aggregate"][jettype][cat][tag], 
                        eff_dict["Aggregate"][jettype][cat][untag], 
                        eff_err_dict["Aggregate"][jettype][cat][untag]
                    )
                    if debug and jettype == "bjets" and cat == "Inclusive" and tag in ["DeepCSV_M"]:
                        #print(eff_dict["Aggregate"][jettype][cat][tag])
                        #print(eff_err_dict["Aggregate"][jettype][cat][tag])
                        debug_dict["agg_eff"] = eff_dict["Aggregate"][jettype][cat][tag]
                        debug_dict["agg_err"] = eff_err_dict["Aggregate"][jettype][cat][tag]
    aggregateFile.Close()
    #return jets_dict, oFileDict

def rebin2D(hist, name, xbins, ybins, return_numpy_arrays=False):
    """Rebin a 2D histogram by project slices in Y, adding them together, and using TH1::Rebin along the X axes,
    then create a new histogram with the content of these slices"""

    if return_numpy_arrays:
        if 'numpy' not in dir() and 'np' not in dir():
            try:
                import numpy as np
            except Exception as e:
                raise RuntimeError("Could not import the numpy module in method rebin2D")
        #Early return workaround in case no rebinning is necessary, the trivial case. Would be better to split this into a separate function, but, ya know... PhD life!
    if xbins is None and ybins is None:
        final_hist = hist.Clone(name)
        if return_numpy_arrays:
            #Create arrays of zeros to be filled after rebinning, with extra rows and columns for over/underflows
            #Note: actual bins are len(<axis>bins) - 1, and we add 2 for the x axis to account for under/overflow
            #since y-axis will account for it via the ranges actually included when slicing and projections are done
            nBinsX = final_hist.GetXaxis().GetNbins()+2
            nBinsY = final_hist.GetYaxis().GetNbins()+2
            hist_contents = np.zeros((nBinsY, nBinsX), dtype=float)
            hist_errors = np.zeros((nBinsY, nBinsX), dtype=float)
            #Reverse the y array since numpy counts from top to bottom, and swap X and Y coordinates (row-column)
            for x in range(nBinsX):
                for y in range(nBinsY):
                    hist_contents[nBinsY-1-y, x] = final_hist.GetBinContent(x, y)
                    hist_errors[nBinsY-1-y, x] = final_hist.GetBinError(x, y)
            return final_hist, hist_contents, hist_errors
        else:
            return final_hist


    #xbins_vec = ROOT.std.vector(float)(len(xbins))
    nxbins = []
    xbins_vec = array.array('d', xbins)
    for xn, x in enumerate(xbins):
        nxbins.append(hist.GetXaxis().FindBin(x))
        #xbins_vec[xn] = x
        
        
    #ybins_vec = ROOT.std.vector(float)(len(ybins))
    nybins = []
    ybins_vec = array.array('d', ybins)
    for yn, y in enumerate(ybins):
        nybins.append(hist.GetYaxis().FindBin(y))
        #ybins_vec[yn] = y
    #Get range objects that store the bins to be projected and added
    ybinsrange = [range(nybins[:-1][z], nybins[1:][z]) for z in range(len(nybins)-1)]
    
    #set up the final histogram, copying most of the parameters over
    final_hist = ROOT.TH2D(name, hist.GetTitle(), len(xbins)-1, xbins_vec, len(ybins)-1, ybins_vec)
    #Xaxis
    #final_hist.GetXaxis().SetNdivisions(hist.GetXaxis().GetNdivisions())
    final_hist.GetXaxis().SetAxisColor(hist.GetXaxis().GetAxisColor())
    final_hist.GetXaxis().SetLabelColor(hist.GetXaxis().GetLabelColor())
    final_hist.GetXaxis().SetLabelFont(hist.GetXaxis().GetLabelFont())
    final_hist.GetXaxis().SetLabelOffset(hist.GetXaxis().GetLabelOffset())
    final_hist.GetXaxis().SetLabelSize(hist.GetXaxis().GetLabelSize())
    final_hist.GetXaxis().SetTickLength(hist.GetXaxis().GetTickLength())
    final_hist.GetXaxis().SetTitleOffset(hist.GetXaxis().GetTitleOffset())
    final_hist.GetXaxis().SetTitleSize(hist.GetXaxis().GetTitleSize())
    final_hist.GetXaxis().SetTitleColor(hist.GetXaxis().GetTitleColor())
    final_hist.GetXaxis().SetTitleFont(hist.GetXaxis().GetTitleFont())
    #Yaxis
    #final_hist.GetYaxis().SetNdivisions(hist.GetYaxis().GetNdivisions())
    final_hist.GetYaxis().SetAxisColor(hist.GetYaxis().GetAxisColor())
    final_hist.GetYaxis().SetLabelColor(hist.GetYaxis().GetLabelColor())
    final_hist.GetYaxis().SetLabelFont(hist.GetYaxis().GetLabelFont())
    final_hist.GetYaxis().SetLabelOffset(hist.GetYaxis().GetLabelOffset())
    final_hist.GetYaxis().SetLabelSize(hist.GetYaxis().GetLabelSize())
    final_hist.GetYaxis().SetTickLength(hist.GetYaxis().GetTickLength())
    final_hist.GetYaxis().SetTitleOffset(hist.GetYaxis().GetTitleOffset())
    final_hist.GetYaxis().SetTitleSize(hist.GetYaxis().GetTitleSize())
    final_hist.GetYaxis().SetTitleColor(hist.GetYaxis().GetTitleColor())
    final_hist.GetYaxis().SetTitleFont(hist.GetYaxis().GetTitleFont())
    
    slice_dict = {}
    #Begin looping through slices that are to be made, each slice composed of multiple bins in the yrange, potentially
    for sn, ybinset in enumerate(ybinsrange):
        slice_dict[str(sn)] = {}
        #ybinset is an range object, so iterate through it for each ybin to be added in this slice
        for bn, ybin in enumerate(ybinset):
            #Create hist for this slice if it's the first bin being combined
            if bn == 0:
                slice_dict[str(sn)]["hist"] = hist.ProjectionX("{}_Yslice{}".format(hist.GetName(), sn), ybin, ybin)
            #THAdd the rest of the bins being combined into this slice
            else:
                slice_dict[str(sn)]["hist"].Add(hist.ProjectionX("{}_Yslice{}_subslice{}".format(hist.GetName(), sn, bn), ybin, ybin))
            
            #If it's the last bin for this slice, do the X rebinning
            if bn is len(ybinset)-1:
                #make sure to get the return value, don't try to rebin in place
                if len(xbins)-1 > 1:
                    slice_dict[str(sn)]["hist"] = slice_dict[str(sn)]["hist"].Rebin(len(xbins)-1, "", xbins_vec)
                else:
                    pass
        #Carry over slice content and errors to the new histogram, remembering sn starts at 0, and non-underflow
        #in histograms begins at 1 (overflow at NBins + 1, requiring us to add 2 when creating an range object)
        #print(slice_dict[str(sn)])
        for fbn in range(slice_dict[str(sn)]["hist"].GetXaxis().GetNbins()+2):
            #sn+1 might be in error if we actually need underflows and overflows in the y range...
            final_hist.SetBinContent(fbn, sn+1, slice_dict[str(sn)]["hist"].GetBinContent(fbn))
            final_hist.SetBinError(fbn, sn+1, slice_dict[str(sn)]["hist"].GetBinError(fbn))
                                 
    
    if return_numpy_arrays:
        #Create arrays of zeros to be filled after rebinning, with extra rows and columns for over/underflows
        #Note: actual bins are len(<axis>bins) - 1, and we add 2 for the x axis to account for under/overflow
        #since y-axis will account for it via the ranges actually included when slicing and projections are done
        nBinsX = final_hist.GetXaxis().GetNbins()+2
        nBinsY = final_hist.GetYaxis().GetNbins()+2
        hist_contents = np.zeros((nBinsY, nBinsX), dtype=float)
        hist_errors = np.zeros((nBinsY, nBinsX), dtype=float)
        #Reverse the y array since numpy counts from top to bottom, and swap X and Y coordinates (row-column)
        for x in range(nBinsX):
            for y in range(nBinsY):
                hist_contents[nBinsY-1-y, x] = final_hist.GetBinContent(x, y)
                hist_errors[nBinsY-1-y, x] = final_hist.GetBinError(x, y)
        return final_hist, hist_contents, hist_errors
    else:
        return final_hist
    
def numpyDivAndError(num, num_err, den, den_err):
    """Take 4 numpy arrays containing the numerator, numerator errors, denominator, and denominator errors.
    Compute the division and appropriate error"""
    
    if 'numpy' not in dir() and 'np' not in dir():
        try:
            import numpy as np
        except Exception as e:
            raise RuntimeError("Could not import the numpy module in method numpyDivAndError")
    
    #A = B/C; (dA/A)^2 = (dB/B)^2 + (dC/C)^2. Compute sqrt(RHS) of the error first
    #Use the out = zeros and where=(denominator != 0) to prevent NaN in divisions
    num_err = np.sqrt(np.add(
        np.square(
            np.divide(
                num_err,
                num,
                out = np.zeros_like(num),
                where=(num!=0)
            )
        ),
        np.square(
            np.divide(
                den_err,
                den,
                out = np.zeros_like(den),
                where=(den!=0)
            )
        )
    ))
    #A = B/C
    num = np.divide(
        num,
        den,
        out = np.zeros_like(num),
        where=(den!=0)
    )
    #dA = A* sqrt(RHS of formula) (latter already stored in num_err)
    num_err = np.multiply(num_err, num)
    return num, num_err

def ChiSquareTest(input_file, test_against="All", must_contain = [], must_not_contain=[]):
    if 'ctypes' not in dir():
        try:
            import ctypes
        except Exception as e:
            raise RuntimeError("Could not import the ctypes module in method ChiSquareTest")
    if 'copy' not in dir():
        try:
            import copy
        except Exception as e:
            raise RuntimeError("Could not import the copy module in method ChiSquareTest")
    f = ROOT.TFile.Open(input_file, "read")
    #not a smart check against stacks, differing dimensioned histograms... use at one's own risk
    h_list_unclean = [h.GetName() for h in f.GetListOfKeys() if "ROOT.TH" in str(type(f.Get(h.GetName())))]
    h_list = []
    for h in h_list_unclean:
        if len(must_contain) == 0:
            matched_contained = True
        else:
            matched_contained = False
            for mc in must_contain:
                if mc in h: matched_contained = True
        matched_not_contained = False
        for mnc in must_not_contain:
            if mnc in h: matched_not_contained = True
        if not matched_not_contained and matched_contained: h_list.append(h)
        
    #print(h_list)
    test_against_clean = []
    if type(test_against) == str:
        if test_against.lower() == "all":
            test_against_clean = h_list
        elif test_against in h_list:
            test_against_clean = [test_against]
    elif type(test_against) == list:
        test_against_clean = [h for h in test_against if h in h_list]
    #print(test_against_clean)

    tuples = []
    for t in test_against_clean:
        for h in h_list:
            chi2 = ctypes.c_double()
            ndf = ctypes.c_int()
            igood = ctypes.c_int()
            p = f.Get(t).Chi2TestX(f.Get(h), chi2, ndf, igood, "WW");
            tuples.append((t, h, copy.copy(chi2), copy.copy(ndf), copy.copy(igood), copy.copy(p)))
    for tup in tuples:
        print("{} :: {}\n\tTest Result: ChiSquare/ndf: {} ndf: {} p-value: {}".format(tup[0], tup[1], float(tup[2].value)/float(tup[3].value), tup[3].value, tup[5]))

def cartesianProductList(name_format="$NUM_$LET_$SYM", name_tuples=[("$NUM", ["1", "2"]), ("$LET", ["A", "B", "C"]), ("$SYM", ["*", "@"])]):
    """Take as input a string <name_format> and list of tuples <name_tuple> where a cartesian product of the tuples is formed.
    The tuples contain a key-string (also present in the name_format string) and value-list with the replacements to cycle through.
    The last tuple is the innermost replacement in the list formed, regardless of placement in the name_format string."""
    if 'copy' not in dir():
        try:
            import copy
        except:
            raise RuntimeError("Could not import the copy module in method cartesianProductList")
    if 'itertools' not in dir():
        try:
            import itertools
        except:
            raise RuntimeError("Could not import the itertools module in method cartesianProductList")
    list_of_lists = []
    list_of_keys = []
    for k, v in name_tuples:
        list_of_lists.append(v)
        list_of_keys.append(k)
    cart_prod = [zip(list_of_keys, l) for l in list(itertools.product(*list_of_lists))]
    ret_list = []
    for uzip in cart_prod:
        nc = copy.copy(name_format)
        for k, v in uzip:
            nc = nc.replace(k, v)
        ret_list.append(nc)
    return ret_list

def rootToPDF(directory, outDirectory="{}/PDF", globKey="*.root", stripKey=".root", 
             name_format="$CAT_$JETTYPE_$TAG",
             name_tuples=[("$JETTYPE", ["bjets", "cjets", "udsgjets"]), ("$TAG", ["DeepCSV_M",]),
                         ("$CAT", ["Inclusive", "nJet4", "nJet5", "nJet6", "nJet7", "nJet8+"])],
             draw_option="COLZ TEXTE", draw_min=None, draw_max=None
            ):
    """take list of files in <directory>, with optional <globKey>, and create individual PDF files containing
    each file's histograms, based on derived categories. Keys can be parsed with 
    <name_format> (default '$CAT_$JETTYPE_$TAG') where up to 3 $KEYs are cycled through from 
    their respective input lists."""
    if "{}/" in outDirectory:
        outDirectory = outDirectory.format(directory)
    print("Checking for (and if necessary, creating) directory {}".format(outDirectory))
    if not os.path.isdir(outDirectory):
        os.makedirs(outDirectory)
    #Get the files
    if 'glob' not in dir():
        try:
            import glob
        except:
            raise RuntimeError("Could not import the glob module in method rootToPDF")
    files = glob.glob("{}/{}".format(directory, globKey))
    #deduce names from the filenames, with optional stripKey parameter that defaults to .root
    names = [fname.split("/")[-1].replace(stripKey, "") for fname in files]
    fileDict = {}
    oFileDict = {}
    keysDict = {}
    
    draw_list = cartesianProductList(name_format=name_format, name_tuples=name_tuples)
    print(draw_list)
    c = ROOT.TCanvas("c", "", 1200, 900)
    c.SetLogx()
        
    for name, fname in zip(names, files):
        print(name)
        #inFiles
        fileDict[name] = ROOT.TFile.Open(fname, "READ")
        #hist names
        keysDict[name] = [hist.GetName() for hist in fileDict[name].GetListOfKeys()]
        #Skip empty files
        if len(keysDict[name]) == 0: 
            print("Skipping sample {} whose file contains no histograms".format(name))
            fileDict[name].Close()
            continue
            
        ofname = "{}/{}.pdf".format(outDirectory, name).replace("//", "/")
        dn = 0
        dnmax = set(keysDict[name])
        dnmax = len(set(keysDict[name]).intersection(set(draw_list)))
        for drawable in draw_list:
            if drawable not in keysDict[name]:
                continue
            else:
                dn += 1
            h = fileDict[name].Get(drawable)
            #Text size is based on the marker size (scale factor * pad size * marker size)
            h.SetMarkerSize(0.5*h.GetMarkerSize())
            if draw_min:
                h.SetMinimum(draw_min)
            if draw_max:
                h.SetMaximum(draw_max)
            #good draw options: COLZ TEXTE. Add 2 digits between TEXT and E for rotation (degrees): TEXT90E does 90deg rotation
            h.SetStats(0) #disable stats box, it's in the way...
            h.Draw(draw_option)
            c.Draw()
            if dn == 1:
                print("Opening {}".format(ofname))
                c.SaveAs(ofname + "(")
            elif dn == dnmax:
                print("Closing {}".format(ofname))
                c.SaveAs(ofname + ")")
            else:
                c.SaveAs(ofname)
                
        fileDict[name].Close()


# In[ ]:


def makeJetEfficiencyReport(input_stats_dict, directory, levelsOfInterest="All"):
    if not os.path.isdir(directory):
        os.makedirs(directory)
    stats_dict = dict()
    all_names = []
    for name, name_dict in input_stats_dict.items():
        all_names.append(name)
        for level, level_dict in name_dict.items():
            if level not in stats_dict.keys():
                stats_dict[level] = dict()
            if name not in stats_dict[level].keys():
                stats_dict[level][name] = dict()
            if levelsOfInterest != "All" and level not in levelsOfInterest: continue
            for category, category_dict in level_dict.items():
                if category not in stats_dict[level].keys():
                    stats_dict[level][name][category] = dict()
                for stat_name, stat_obj in category_dict.items():
                    stats_dict[level][name][category][stat_name] = [name, category, stat_name, str(stat_obj.GetMean()), 
                                                                    str(stat_obj.GetMeanErr()), str(stat_obj.GetRMS())]
                        
    for level, level_dict in stats_dict.items():
        ofname = "{}/{}_JetEfficiencyReport.csv".format(directory, level).replace("//", "/")
        print("Opening {}".format(ofname))
        with open(ofname, "w") as f:
            f.write("Sample,Category,Jet Counter,Mean,MeanError,RMS\n")
            for name, name_dict in level_dict.items():
                for category, category_dict in name_dict.items():
                    for stat_name, stat_obj in category_dict.items():
                        line = ",".join(stat_obj) + "\n"
                        f.write(line)

        
def makeHLTReport(stats_dict, directory, levelsOfInterest="All"):
    if not os.path.isdir(directory):
        os.makedirs(directory)
    #name, level, weighted/unweighted, category, (count?)
    path_dict = dict()
    count_dict = dict()
    all_names = []
    for name, name_dict in stats_dict.items():
        all_names.append(name)
        for level, level_dict in name_dict.items():
            if level not in path_dict.keys():
                path_dict[level] = dict()
            if level not in count_dict.keys():
                count_dict[level] = dict()
            if levelsOfInterest != "All" and level not in levelsOfInterest: continue
            for stat_category, stat_category_dict in level_dict.items():
                if stat_category == "counts":
                    for category, counter in stat_category_dict.items():
                        count_dict[level][category] = str(counter.GetValue())
                elif stat_category in ["weighted", "unweighted"]:
                    if stat_category not in path_dict[level].keys():
                        path_dict[level][stat_category] = dict()
                    #pprint.pprint(stat_category_dict)
                    for category, category_dict in stat_category_dict.items():
                        if category not in path_dict[level][stat_category].keys():
                            path_dict[level][stat_category][category] = dict()
                        for path, count in category_dict.items():
                            if path not in path_dict[level][stat_category][category].keys():
                                #path_dict[level][stat_category][category][path] = dict()
                                path_dict[level][stat_category][category][path] = {}
                            path_dict[level][stat_category][category][path][name] = str(count.GetValue())
                elif stat_category in ["weightedStats", "weightedStatsSMT"]:
                    if stat_category not in path_dict[level].keys():
                        path_dict[level][stat_category] = dict()
                    #pprint.pprint(stat_category_dict)
                    for category, category_dict in stat_category_dict.items():
                        if category not in path_dict[level][stat_category].keys():
                            path_dict[level][stat_category][category] = dict()
                        for path, count in category_dict.items():
                            if path not in path_dict[level][stat_category][category].keys():
                                #path_dict[level][stat_category][category][path] = dict()
                                path_dict[level][stat_category][category][path] = {}
                            path_dict[level][stat_category][category][path][name] = str(count.GetMean() * count.GetW())
                    
                        
    for level, level_dict in path_dict.items():
        with open("{}/{}_HLTReport.csv".format(directory, level), "w") as f:
            for stat_category, stat_category_dict in level_dict.items():
                f.write("====={}=====\n".format(stat_category))
                for category, category_dict in stat_category_dict.items():
                    f.write("=========={}==========\n".format(category))
                    wroteKey = False
                    for path, path_values in category_dict.items():
                        #pad values in the dictionary, this depends on it NOT being an OrderedDict at this level...
                        for n in all_names:
                            if n not in path_values: path_values[n] = "-0.000000000000000001"
                    for path, path_values in sorted(category_dict.items(), key=lambda k: k[0]):
                        if wroteKey is False: 
                            line = "HLT Path," + ",".join(path_values.keys()) + "\n"
                            f.write(line)
                            wroteKey = True
                        line = path + "," + ",".join(path_values.values()) + "\n"
                        f.write(line)
def getTriggerCutString(passTriggers, vetoTriggers):
    vetoSection = "!("
    for tn, trigger in enumerate(vetoTriggers):
        if tn > 0:
            vetoSection += " || "
        vetoSection += trigger.trigger
    vetoSection += ")"

    passSection = "("
    for tn, trigger in enumerate(passTriggers):
        if tn > 0:
            passSection += " || "
        passSection += trigger.trigger
    passSection += ")"

    retString = ""
    if len(vetoTriggers) > 0: retString += vetoSection + " && "
    retString += passSection

    return retString
            
def main(analysisDir, sampleCards, source, channel, bTagger, systematicCards, TriggerList,
         doDiagnostics=False, doNtuples=False, doHistos=False, doCombineHistosOnly=False,
         doLeptonSelection=False, doBTaggingYields=True, BTaggingYieldsFile="{}", 
         BTaggingYieldsAggregate=False, useHTOnly=False, useNJetOnly=False, 
         printBookkeeping=False, triggers=[], includeSampleNames=None, 
         useDeltaR=False, jetPtMin=30.0, jetPUId=None, 
         HTBins=100, HTCut=500, METCut=0.0, ZMassMETWindow=[15.0, 10000.0],
         disableNjetMultiplicityCorrection=False, enableTopPtReweighting=False,
         excludeSampleNames=None, verbose=False, checkMeta=True,
         testVariables=False, categorySet="5x3", variableSet="HTOnly", variableList=None, systematicSet="All", nThreads=8,
         redirector=None, recreateFileList=False, doRDFReport=False, options=None
     ):
    ########################################################
    ########################################################
    ### Override variableSet if variableList is not None ###
    ########################################################
    ########################################################
    if variableList is not None:
        print("Overriding variableSet ({vS}) with variableList ({vL})".format(vS=variableSet,vL=variableList))
        variableSet = "__".join(variableList)

    ##################################################
    ##################################################
    ### CHOOSE SAMPLE DICT AND CHANNEL TO ANALYZE ####
    ##################################################
    ##################################################
    inputSamplesAll, inputSampleCardDict = load_yaml_cards(sampleCards)
    sysVariationsYaml, sysVariationCardDict = load_yaml_cards(systematicCards)
    sysVariationsAll = sysVariationsYaml 
    # with open("2017_systematics_NANOv5.yaml", "w") as of:
    #     of.write(yaml.dump(sysVariationsAll, Dumper=yaml.RoundTripDumper))
    # with open("2017_samples_NANOv5.yaml", "w") as of:
    #     of.write(yaml.dump(inputSamples, Dumper=yaml.RoundTripDumper))
    # inputSamplesYaml = None
    # sysVariationsAllYaml = None
    # with open("2017_samples_NANOv5.yaml", "r") as inf:
    #     inputSamplesYaml = yaml.load(inf)
    # with open("2017_systematics_NANOv5.yaml", "r") as inf:
    #     sysVariationsAllYaml = yaml.load(inf)
    # print("samples")
    # for k, v in inputSamples.items():
    #     for inputSampleCardName, inputSampleCardYaml in inputSampleCardDict.items():
    #         if k in inputSampleCardYaml.keys():
    #             if isinstance(v, dict):
    #                 for kk, vv in v.items():
    #                     if kk in inputSampleCardYaml[k].keys() and vv == inputSampleCardYaml[k][kk]:
    #                         print("success")
    #                     else:
    #                         print(k, kk, vv, inputSampleCardYaml[k][kk] if kk in inputSampleCardYaml[k].keys() else "FailFail")
    #             else:
    #                 if v == inputSampleCardYaml[k]:
    #                     print("success")
    #         else:
    #             print(k, type(v), type(inputSampleCardYaml[k]) if k in inputSampleCardYaml else "Fail")
    # print("systematics")
    # for k, v in sysVariationsAll.items():
    #     for sysVariationCardName, sysVariationCardYaml in sysVariationCardDict.items():
    #         if k in sysVariationCardYaml.keys():
    #             if isinstance(v, dict):
    #                 for kk, vv in v.items():
    #                     if kk in sysVariationCardYaml[k].keys() and vv == sysVariationCardYaml[k][kk]:
    #                         print("success")
    #                     else:
    #                         print(k, kk, vv, sysVariationCardYaml[k][kk] if kk in sysVariationCardYaml[k].keys() else "FailFail")
    #             else:
    #                 if v == sysVariationCardYaml[k]:
    #                     print("success")
    #         else:
    #             print(k, type(v), type(sysVariationCardYaml[k]) if k in sysVariationCardYaml else "Fail")

    for inputSampleCardName, inputSampleCardYaml in inputSampleCardDict.items():
        all_samples = [s[0] for s in inputSampleCardYaml.items() if channel in s[1].get("channels",[""]) or "All" in s[1].get("channels",[""])]
        print("All samples: {}".format(" ".join(sorted(all_samples))))
        if includeSampleNames:
            if (type(includeSampleNames) == list or type(includeSampleNames) == dict):
                valid_samples = [s for s in all_samples if s in includeSampleNames]
            else:
                raise RuntimeError("include option is neither a list nor a dictionary, this is not expected")
        elif excludeSampleNames:
            if (type(excludeSampleNames) == list or type(excludeSampleNames) == dict):
                valid_samples = [s for s in all_samples if s not in excludeSampleNames]
            else:
                raise RuntimeError("exclude option is neither a list nor a dictionary, this is not expected")
        else:
            valid_samples = all_samples
    
        #Decide on things to do: either calculate yields for ratios or fill histograms
        #Did we not chooose to do incompatible actions at the same time?
        if doBTaggingYields and (doHistos or doDiagnostics or printBookkeeping or doLeptonSelection):
            raise RuntimeError("Cannot calculate BTaggingYields and Fill Histograms simultaneously, choose only one mode")
        elif not doHistos and not doBTaggingYields and not doDiagnostics and not printBookkeeping and not doLeptonSelection and not doNtuples and not options.stage == 'fill-nano':
            raise RuntimeError("If not calculating BTaggingYields and not Filling Histograms and not doing diagnostics and not printing Bookkeeping and not checking lepton selection, there is no work to be done.")
    
        #These are deprecated for now!
        doJetEfficiency = False
        doBTaggingEfficiencies = False
        doHLTMeans = False
        
        if doBTaggingYields:
            print("\nLoading all samples for calculating BTaggingYields")
            #Set these options for the BTaggingYields module, to differentiate between calculating and loading yields
            BTaggingYieldsFile = None
            calculateTheYields = True
        else:
            #If we're not calculating the yields, we need to have the string value of the Yields to be loaded...
            #Where to load BTaggingYields from
            if BTaggingYieldsFile == "{}":
                BTaggingYieldsFile = "{}/BTaggingYields/{}/BTaggingYields.root".format(analysisDir, channel)
            calculateTheYields = False
            print("Loading BTaggingYields from this path: {}".format(BTaggingYieldsFile))
    
    
        #The source level used is... the source
        source_level = source
    
    
        if channel == "BOOKKEEPING":
            levelsOfInterest=set(["BOOKKEEPING"])
            theSampleDict = inputSampleCardYaml.keys()
        elif channel == "PILEUP":
            levelsOfInterest=set(["PILEUP"])
            theSampleDict = inputSampleCardYaml.keys()
        elif channel == "ElMu":
            levelsOfInterest = set(["ElMu",])
            theSampleDict = [nn for nn in inputSampleCardYaml.keys() if not inputSampleCardYaml[nn]["isData"] or (inputSampleCardYaml[nn]["isData"] and inputSampleCardYaml[nn]["channel"] == channel)]
            # theSampleDict = bookerV2_ElMu.copy()
            # theSampleDict.update(bookerV2_MC)
        elif channel == "MuMu":
            levelsOfInterest = set(["MuMu",])
            theSampleDict = [nn for nn in inputSampleCardYaml.keys() if not inputSampleCardYaml[nn]["isData"] or (inputSampleCardYaml[nn]["isData"] and inputSampleCardYaml[nn]["channel"] == channel)]
            # theSampleDict = bookerV2_MuMu.copy()
            # theSampleDict.update(bookerV2_MC)
        elif channel == "ElEl":    
            levelsOfInterest = set(["ElEl",])
            theSampleDict = [nn for nn in inputSampleCardYaml.keys() if not inputSampleCardYaml[nn]["isData"] or (inputSampleCardYaml[nn]["isData"] and inputSampleCardYaml[nn]["channel"] == channel)]
            # theSampleDict = bookerV2_ElEl.copy()
            # theSampleDict.update(bookerV2_MC)
        elif channel == "ElEl_LowMET":    
            levelsOfInterest = set(["ElEl_LowMET",])
            theSampleDict = [nn for nn in inputSampleCardYaml.keys() if not inputSampleCardYaml[nn]["isData"] or (inputSampleCardYaml[nn]["isData"] and inputSampleCardYaml[nn]["channel"] == "ElEl")]
            # theSampleDict = bookerV2_ElEl.copy()
            # theSampleDict.update(bookerV2_MC)
        elif channel == "ElEl_HighMET":    
            levelsOfInterest = set(["ElEl_HighMET",])
            theSampleDict = [nn for nn in inputSampleCardYaml.keys() if not inputSampleCardYaml[nn]["isData"] or (inputSampleCardYaml[nn]["isData"] and inputSampleCardYaml[nn]["channel"] == "ElEl")]
            # theSampleDict = bookerV2_ElEl.copy()
            # theSampleDict.update(bookerV2_MC)
        # This doesn't work, need the corrections on all the samples and such...
        # elif channel == "All":
        #     levelsOfInterest = set(["ElMu", "MuMu", "ElEl",])
        #     theSampleDict = bookerV2_ElMu.copy()
        #     theSampleDict.update(bookerV2_ElEl)
        #     theSampleDict.update(bookerV2_MuMu)
        #     theSampleDict.update(bookerV2_MC)
        elif channel == "Mu":    
            levelsOfInterest = set(["Mu",])
            theSampleDict = [nn for nn in inputSampleCardYaml.keys() if not inputSampleCardYaml[nn]["isData"] or (inputSampleCardYaml[nn]["isData"] and inputSampleCardYaml[nn]["channel"] == channel)]
            # theSampleDict = bookerV2_Mu.copy()
            # theSampleDict.update(bookerV2_MC)
        elif channel == "El":    
            levelsOfInterest = set(["El",])
            theSampleDict = [nn for nn in inputSampleCardYaml.keys() if not inputSampleCardYaml[nn]["isData"] or (inputSampleCardYaml[nn]["isData"] and inputSampleCardYaml[nn]["channel"] == channel)]
            # theSampleDict = bookerV2_El.copy()
            # theSampleDict.update(bookerV2_MC)
        elif channel == "test":
            print("More work to be done, exiting")
            sys.exit(2)                
        
        filtered = dict()
        base = dict()
        metanode = dict()
        metainfo = dict()
        reports = dict()
        samples = dict()
        counts = dict()
        histos = dict()
        packedNodes = dict()
        varsToFlattenOrSave = dict() #Variables that will be saved to ntuples (completely flat)
        flatteningDict = dict() #Dict breaking down variables that have been flattened, were already flat, were skipped due to function rules, etc.
        the_df = dict()
        stats = dict() #Stats for HLT branches
        effic = dict() #Stats for jet matching efficiencies
        btagging = dict() #For btagging efficiencies
        cat_df = dict() #Categorization node dictionary, returned by fill_histos method
        masterstart = time.perf_counter()#Timers...
        substart = dict()
        subfinish = dict()
        processed = dict()
        processedSampleList = []
    
        if not os.path.isdir(analysisDir):
            os.makedirs(analysisDir)
    
        Benchmark = ROOT.TBenchmark()
    
        ################################################################################
        #### Setup all correctors e.g. LeptonSFs and BTaggingYields Renormalization ####
        ################################################################################
        globalisUL = "non-UL"
        globalVFP = "" #should be either preVFP or postVFP if era == "2016" and isUL = "UL"
        cppVerbosity = False
        btaggingProcessMap = ROOT.std.map(str, ROOT.std.vector(ROOT.std.pair(str, str)))()
        btaggingInclusiveMap = ROOT.std.map(str, ROOT.std.vector(ROOT.std.pair(str, str)))()
        for name in sorted(theSampleDict, key=lambda n: n):
            if name not in inputSampleCardYaml.keys():
                continue
            cppsafename = make_cpp_safe_name(name)
            vals = inputSampleCardYaml[name]
            if name not in valid_samples or vals["isData"]:
                continue
            elif vals["era"] != era:
                print("\nSkipping sample with disparate era: {} in the sample, {} expected by analyzer.\n".format(vals["era"], era))
            else:
                #Get all the potential split process names (in BTaggingYields() function era + "___" + subprocess is the 'eraAndSampleName', e.g. 2017___ttbb_DL-GF. Since the corrector map handles this era modifier already, we drop it here...
                #What an inconsistent mess it all is.
                earlySplitProcess = vals.get("splitProcess", None)
                if isinstance(earlySplitProcess, (dict)):
                    # df_with_IDs = input_df
                    splitProcs = earlySplitProcess.get("processes")
                    for preProcessName, processDict in splitProcs.items():
                        btaggingProcessMap[preProcessName] = ROOT.std.vector(ROOT.std.pair(str, str))()
                    #Get the inclusive process name for those that are also split
                    btaggingInclusiveMap[name] = ROOT.std.vector(ROOT.std.pair(str, str))()
                #store the names 'normally' for samples that are NOT split 
                else:
                    btaggingProcessMap[name] = ROOT.std.vector(ROOT.std.pair(str, str))()
    
        sysVariationsForBtagging = dict([(sv[0], sv[1]) for sv in sysVariationsAll.items() if len(set(sv[1].get("systematicSet", [""])).intersection(set(systematicSet))) > 0 or sv[0] in ["$NOMINAL", "nominal", "nom"] or "ALL" in systematicSet])
        # for sysVar, sysDict in sysVariationsForBtagging.items():
        if len(valid_samples) > 1:
            print("\n\n\n\nFor now, the ability to iterate over multiple samples is broken, so that the GetCorrectorMap can retrieve the right LUTs for that one sample without breaking")
            print("\n\n\nThe clusterfuck of btag yield aggregates leads to another rewrite. In order to handle multiple samples in an FTAnalyzer instance, the GetCorrectorMap would need to change so that the process, systematic, scalepostfix vectors are changed into a map, where the key is the process and the systematic and scalepostfix are paired string vectors in a submap, i.e. input['tt_DL-GF']['systematic_names'] = {'nom', 'btagSF_shape_hfUp', 'jec'}, input['tt_DL-GF']['scale_postfix'] = {'nom', 'nom', 'jec'}")
            raise NotImplementedError("Hahahahahaa")
        elif len(valid_samples) == 1:
            allSystematicsWorkaround = filter_systematics(sysVariationsAll, era=era, sampleName=valid_samples[0], isSystematicSample=inputSampleCardYaml[valid_samples[0]].get("isSystematicSampleFor", False), nominal=True, scale=True, weight=True)
        else:
            print("No valid samples found, continuing")
            continue
        print("FIXME: hardcoded incorrect btagging top path for the corrector map")
        print("FIXME: hardcoded non-UL/UL and no VFP handling in the corrector map retrieval")
        BTaggingYieldsTopPath = BTaggingYieldsFile.replace("BTaggingYields.root", "") if BTaggingYieldsFile is not None and channel not in ["BOOKKEEPING", "PILEUP"] else "" #Trigger the null set of correctors for btagging if there's no yields file we're pointing to...
        # BTaggingYieldsTopPath = ""
        correctorMap = ROOT.FTA.GetCorrectorMap(era, #2017 or 2018 or 2016, as string
                                                globalisUL, #UL or non_UL
                                                globalVFP, ##preVFP or postVFP if 2016
                                                "../Kai/python/data/leptonSF/Muon", "LooseID", "TightRelIso_MediumID",
                                                "../Kai/python/data/leptonSF/Electron", "Loose", "UseEfficiency",
                                                cppVerbosity) #bool btag_use_nJet_only = false
        print("testing LUTManager")
        LUTManager = ROOT.LUTManager()
        LUTManager.Add(correctorMap, cppVerbosity)
        LUTManager.Finalize(nThreads)
        generalLUTs = LUTManager.GetLUTVector()
        btaggingCorrectorMaps = dict()
        btaggingLUTManagers = dict()
        btaggingLUTs = dict()
    
        ################################
        #### Loop through processes ####
        ################################
        # for name, vals in sorted(theSampleDict.items(), key=lambda n: n[0]):
        for name in sorted(theSampleDict, key=lambda n: n):
            if name not in inputSampleCardYaml.keys():
                continue
            vals = inputSampleCardYaml[name]
            if name not in valid_samples: 
                # print("Skipping sample {}".format(name))
                continue
            filelistDir = analysisDir + "/Filelists"
            if not os.path.isdir(filelistDir):
                os.makedirs(filelistDir)
            sampleOutFile = "{base}/{era}__{src}__{sample}.txt".format(base=filelistDir, era=vals["era"], src=source_level, sample=name)
            # sampleFriendFile = "{base}/{era}__{src}__{sample}__Friend0.txt".format(base=filelistDir, era=vals["era"], src=source_level, sample=name)
            fileList = []
            metaList = []
            if os.path.isfile(sampleOutFile) and not recreateFileList:
                print("Loading filelist from the cached list in this analysis directory: {}".format(sampleOutFile))
                fileList = getFiles(query="list:{}".format(sampleOutFile), outFileName=None)
                metaList = copy.copy(fileList)
            else:
                if isinstance(redirector, str):
                    redir = redirector
                elif "/eos/user/" in vals["source"][source_level] or "/eos/home-" in vals["source"][source_level]:
                    #If we can directly access the files, then do so, otherwise redirector is called for
                    if vals["source"][source_level].startswith("glob:") and len(glob.glob(vals["source"][source_level].replace("glob:",""))) > 0:
                        redir=""
                    else:
                        redir="root://eosuser.cern.ch/".format(str(pwd.getpwuid(os.getuid()).pw_name)[0])
                else:
                    redir=""
                print("Determining redirector...{}".format(redir))
                # if "dbs:" in vals["source"][source_level]:
                fileList = getFiles(query=vals["source"][source_level], redir=redir, outFileName=sampleOutFile)
                metaList = copy.copy(fileList)
                if vals["source"][source_level].startswith("glob:"):
                    metaList += getFiles(query=vals["source"][source_level].replace(".root", ".empty"), redir=redir)
            transformedFileList = ROOT.std.vector(str)()
            transformedMetaList = ROOT.std.vector(str)()
            for fle in fileList:
                transformedFileList.push_back(fle)
            for fle in metaList:
                transformedMetaList.push_back(fle)
            if transformedFileList.size() < 1:
                print("Filelist empty, attempting new query in case the cache file ({}) is wrong".format(sampleOutFile))
                if isinstance(redirector, str):
                    redir = redirector
                elif "/eos/" in vals["source"][source_level]:
                    redir="root://eosuser.cern.ch/".format(str(pwd.getpwuid(os.getuid()).pw_name)[0])
                else:
                    redir="root://cms-xrd-global.cern.ch/"
                # if "dbs:" in vals["source"][source_level]:
                fileList = getFiles(query=vals["source"][source_level], redir=redir, outFileName=sampleOutFile)
                metaList = fileList
                if vals["source"][source_level].startswith("glob:"):
                    metaList +=getFiles(query=vals["source"][source_level].replace(".root", ".empty"), redir=redir)
                for fle in fileList:
                    transformedFileList.push_back(fle)
                for fle in metaList:
                    transformedMetaList.push_back(fle)
                if transformedFileList.size() < 1:
                    print("No files located... skipping sample {}".format(name))
                    continue
    
            #Construct TChain that we can add friends to potentially, but similarly constructin TChains and adding the chains with AddFriend
            print("Creating TChain for sample {}".format(name))
            tcmain = ROOT.TChain("Events")
            tcmeta = ROOT.TChain("Runs")
            for vfe in transformedFileList:
                print("\t{}".format(vfe))
                tcmain.Add(str(vfe))
                tcmeta.Add(str(vfe))
            if checkMeta:
                print("Additional files with meta information:")
                for vfe in transformedMetaList:
                    if vfe not in transformedFileList:
                        print("\t{}".format(vfe))                        
                        tcmeta.Add(str(vfe))
            # tcfriend0 = ROOT.TChain("Events")
            # for vfef0 in transformedFileList_Friend0:
            #     tcfriend0.Add(vfef0)
            # tcmain.AddFriend(tcfriend0)
            # print("Initializing RDataFrame\n\t{} - {}".format(name, vals["source"][source_level]))
            # print("Initializing RDataFrame\n\t{} - {}".format(name, len(transformedFileList)))
            print("Initializing RDataFrame with TChain")
            threadPoolSize = ROOT.GetThreadPoolSize()
            if checkMeta:
                #Disable IMT, it breaks on the files with empty Events trees in them, for some strange fuckin' reason
                ROOT.DisableImplicitMT()
                metanode[name] = RDF(tcmeta) #meta tree
                if vals["isData"]:
                    metainfo[name] = {"run": metanode[name].Sum("run")}
                else:
                    metainfo[name] = {"run": metanode[name].Sum("run"), 
                                      "genEventCount": metanode[name].Sum("genEventCount"), 
                                      "genEventSumw": metanode[name].Sum("genEventSumw"), 
                                      "genEventSumw2": metanode[name].Sum("genEventSumw2"), 
                                      "nLHEScaleSumw": metanode[name].Mean("nLHEScaleSumw"), 
                                      "nLHEPdfSumw": metanode[name].Mean("nLHEPdfSumw"), 
                                  }
                    for nScale in range(9):
                        metanode[name] = metanode[name].Define("LHEScaleSumw_{nscale}".format(nscale=nScale), "genEventSumw * LHEScaleSumw.at({nscale}, 0)".format(nscale=nScale))
                        metainfo[name]["LHEScaleSumw_{nscale}".format(nscale=nScale)] = metanode[name].Sum("LHEScaleSumw_{nscale}".format(nscale=nScale))
                    for nPDF in range(33):
                        metanode[name] = metanode[name].Define("LHEPdfSumw_{npdf}".format(npdf=nPDF), "genEventSumw * LHEPdfSumw.at({npdf}, 0)".format(npdf=nPDF))
                        metainfo[name]["LHEPdfSumw_{npdf}".format(npdf=nPDF)] = metanode[name].Sum("LHEPdfSumw_{npdf}".format(npdf=nPDF))
                for mk, mv in metainfo[name].items():
                    metainfo[name][mk] = mv.GetValue()
                    if mk.startswith("nLHEScaleSumw") or mk.startswith("nLHEPdfSumw") or mk.startswith("genEventCount"):
                        metainfo[name][mk] = int(round(metainfo[name][mk]))
                    if mk == "genEventSumw":
                        if (abs(1 - vals.get("sumWeights", 0)/metainfo[name]["genEventSumw"]) >= 1e-4):
                            print("Weight discrepancy found, did you mean to override and run over a subset of files? {}".format(name))
                        if channel != "BOOKKEEPING":
                            assert (abs(1 - vals.get("sumWeights", 0)/metainfo[name]["genEventSumw"]) < 1e-4), "Weight discrepancy found, did you mean to override and run over a subset of files? {}".format(name)
                    if mk.startswith("LHEPdfSumw") or mk.startswith("LHEScaleSumw"):
                        metainfo[name][mk] /= metainfo[name]["genEventSumw"]
                declare_cpp_constants(name, 
                                      isData=vals.get("isData", True),
                                      constants_dict=metainfo[name], 
                                      nLHEScaleSumw=int(round(metainfo[name].get("nLHEScaleSumw", 0))),
                                      nLHEPdfSumw=int(round(metainfo[name].get("nLHEPdfSumw", 0))),
                                      normalizeScale = vals.get("isSignal", False),
                                      normalizePdf = vals.get("isSignal", False)
                                  )
            #Reenable IMT and create the 
            if threadPoolSize != ROOT.GetThreadPoolSize():
                ROOT.EnableImplicitMT(threadPoolSize)
            filtered[name] = dict()
            base[name] = RDF(tcmain)
            baseColumns = base[name].GetColumnNames()
            metainfo[name]["totalEvents"] = tcmain.GetEntries()
            print("\n{}".format(name))
            pprint.pprint(metainfo[name])


            #Deduce filters for scale calculations (MET, defineLeptons, defineJets) and where all are needed (defineWeights, BTaggingYields, fill_histos...)
            scaleSystematics = filter_systematics(sysVariationsAll, era=era, sampleName=name, isSystematicSample=vals.get("isSystematicSampleFor", False), nominal=True, scale=True, weight=False, baseColumns=baseColumns)
            allSystematics = filter_systematics(sysVariationsAll, era=era, sampleName=name, isSystematicSample=vals.get("isSystematicSampleFor", False), nominal=True, scale=True, weight=True, baseColumns=baseColumns)
            # print("scale systematics: {}\nall systematics: {}".format(scaleSystematics, allSystematics))
            #Now do the btagging LUTs
            for sysVarRaw, sysDict in sysVariationsAll.items():
                if vals.get("isData", True):
                    continue
                if sysVarRaw not in allSystematics:
                    print("Skipping inapplicable systematic variation for btagging LUT creation: {}".format(sysVarRaw))
                    continue
                #get final systematic name
                sysVar = sysVarRaw.replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', '')).replace("$ERA", era)
                isWeightVariation = sysDict.get("weightVariation")
                slimbranchpostfix = "nom" if isWeightVariation else sysVar #branch postfix for identifying input branch variation
                earlySplitProcess = vals.get("splitProcess", None)
                if isinstance(earlySplitProcess, (dict)):
                    # df_with_IDs = input_df
                    splitProcs = earlySplitProcess.get("processes")
                    for preProcessName, processDict in splitProcs.items():
                        btaggingProcessMap[preProcessName].push_back(ROOT.std.pair(str, str)(sysVar, slimbranchpostfix))
                    btaggingInclusiveMap[name].push_back(ROOT.std.pair(str, str)(sysVar, slimbranchpostfix))
                else:
                    btaggingProcessMap[name].push_back(ROOT.std.pair(str, str)(sysVar, slimbranchpostfix))
            btaggingCorrectorMaps[name] = ROOT.FTA.GetBtaggingCorrectorMap(era, #2017 or 2018 or 2016, as string
                                                                    globalisUL, #UL or non_UL
                                                                    globalVFP, ##preVFP or postVFP if 2016
                                                                    BTaggingYieldsTopPath,
                                                                    btaggingProcessMap,
                                                                    btaggingInclusiveMap,
                                                                    BTaggingYieldsAggregate, #bool btag_use_aggregate = false,
                                                                    useHTOnly, #bool btag_use_HT_only = false,
                                                                    useNJetOnly,
                                                                    cppVerbosity) #bool btag_use_nJet_only = false
            btaggingLUTManagers[name] = ROOT.LUTManager()
            btaggingLUTManagers[name].Add(btaggingCorrectorMaps[name], cppVerbosity)
            btaggingLUTManagers[name].Finalize(nThreads)
            btaggingLUTs[name] = btaggingLUTManagers[name].GetLUTVector()

            #General setup of nodes, counts, reports, start times, etc.
            reports[name] = base[name].Report()
            counts[name] = dict()
            # histos[name] = dict()
            packedNodes[name] = dict()
            the_df[name] = dict()
            stats[name] = dict()
            effic[name] = dict()
            varsToFlattenOrSave[name] = dict()
            flatteningDict[name] = dict()
            # btagging[name] = dict()
            cat_df[name] = dict()
            substart[name] = dict()
            subfinish[name] = dict()
            processed[name] = dict()
            #counts[name]["baseline"] = filtered[name].Count() #Unnecessary with baseline in levels of interest?
            for lvl in levelsOfInterest:
                #########################
                ### Split proc config ###
                #########################
                splitProcessConfig = vals.get("splitProcess", None)
                #Note the snapshotPriority value of -1, which means this dataset does not get cached or written to disk with Snapshot
                inclusiveProcessConfig = {"processes": {"{}".format(name): {"filter": "return true;",
                                                                            "nEventsPositive": vals.get("nEventsPositive", -1),
                                                                            "nEventsNegative": vals.get("nEventsNegative", -1),
                                                                            "fractionalContribution": 1,
                                                                            "sumWeights": vals.get("sumWeights", -1.0),
                                                                            "effectiveCrossSection": vals.get("crossSection", 0),
                                                                            "snapshotPriority": -1,
                                                                  }}}
                pprint.pprint(inclusiveProcessConfig)
                if lvl == "PILEUP":
                    #~/Work/CMSSW_10_2_24_patch1/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup
                    #mcPileup2017.root  pileup_Cert_294927-306462_13TeV_PromptReco_Collisions17_withVar.root  PileupHistogram-goldenJSON-13tev-2017-99bins_withVar.root   PileupHistogram-goldenJSON-13tev-2018-99bins_withVar.root
                    #mcPileup2018.root  PileupData_GoldenJSON_Full2016.root                                   PileupHistogram-goldenJSON-13tev-2018-100bins_withVar.root
                    vals = inputSampleCardYaml[name]
                    if vals.get("isData", True):
                        print("Halting execution on real data")
                        continue
                    if hasattr(options, 'noProgressBar') and options.noProgressBar:
                        print("Not preparing progress bars")
                        booktrigger = base[name].Count()
                    else:
                        print("Booking progress bar")
                        booktrigger = ROOT.AddProgressBar(ROOT.RDF.AsRNode(base[name]), 
                                                          2000, int(metainfo[name]["totalEvents"]))
                    baseWithWeight = base[name]\
                        .Define("NormWgt", "return 1.0/{nEvents:f};".format(nEvents = metainfo[name]["genEventCount"]))\
                        .Define("NormGenWgt", "return genWeight/{sW:f};".format(sW = metainfo[name]["genEventSumw"]))
                    #prepare the nested histo structure expected by writeHistos
                    pileupHistos = dict()
                    eraAndSampleName = vals.get("era", "Unknown") + "___" + name
                    pileupHistos[eraAndSampleName] = dict()
                    pileupHistos[eraAndSampleName]["NoChannel"] = dict()
                    pileupHistos[eraAndSampleName]["NoChannel"]["unsignedPileup"] = baseWithWeight.Histo1D(("{proc}___unsigned___diagnostic___pileup".format(proc=eraAndSampleName),
                                                                                                            "unsigned;Pileup_nTrueInt; dEvents/dbin", 99, 0, 99), "Pileup_nTrueInt", "NormWgt")
                    pileupHistos[eraAndSampleName]["NoChannel"]["genWeightPileup"] = baseWithWeight.Histo1D(("{proc}___genWeight___diagnostic___pileup".format(proc=eraAndSampleName),
                                                                                                             "genWeight;Pileup_nTrueInt; dEvents/dbin", 99, 0, 99), "Pileup_nTrueInt", "NormGenWgt")
                    _ = booktrigger.GetValue()
                    print("Finished processing pileup profiling")
                    print("Writing histos to {}".format(analysisDir + "/Pileup"))
                    writeHistos(pileupHistos, 
                                analysisDir + "/Pileup",
                                channelsOfInterest="All",
                                samplesOfInterest="All",
                                dict_keys="All",
                                mode="RECREATE"
                    )                    
                    #skip any further calculations for bookkeeping
                    continue                    
                elif lvl == "BOOKKEEPING":
                    #We just need the info printed on this one... book a Count node with progress bar if not quiet
                    if hasattr(options, 'noProgressBar') and options.noProgressBar:
                        print("Not preparing progress bars")
                        booktrigger = base[name].Count()
                    else:
                        print("Booking progress bar")
                        booktrigger = ROOT.AddProgressBar(ROOT.RDF.AsRNode(base[name]), 
                                                          2000, int(metainfo[name]["totalEvents"]))
                    updatedMeta = True
                    for mk, mv in metainfo[name].items():
                        if mk == "genEventSumw":
                            print(inputSampleCardYaml[name].get("sumWeights", -1), mv)
                            inputSampleCardYaml[name]["sumWeights"] = mv
                        elif mk == "genEventSumw2":
                            print(inputSampleCardYaml[name].get("sumWeights2", -1), mv)
                            inputSampleCardYaml[name]["sumWeights2"] = mv
                        if mk == "genEventCount":
                            print(inputSampleCardYaml[name].get("nEvents", -1), mv)
                            inputSampleCardYaml[name]["nEvents"] = int(mv)
                        inputSampleCardYaml[name][mk] = metainfo[name][mk]
                    if updatedMeta == True:
                        #Reloading the vals and split/inclusive ProcessConfigs
                        vals = inputSampleCardYaml[name]
                        splitProcessConfig = inputSampleCardYaml[name].get("splitProcess", None)
                        inclusiveProcessConfig = {"processes": {"{}".format(name): {"filter": "return true;",
                                                                            "nEventsPositive": inputSampleCardYaml[name].get("nEventsPositive", -1),
                                                                            "nEventsNegative": inputSampleCardYaml[name].get("nEventsNegative", -1),
                                                                            "fractionalContribution": 1,
                                                                            "sumWeights": inputSampleCardYaml[name].get("sumWeights", -1.0),
                                                                            "effectiveCrossSection": inputSampleCardYaml[name].get("crossSection", 0),
                                                                            "snapshotPriority": -1,
                                                                  }}}
                        pprint.pprint(inclusiveProcessConfig)
                        print("Updated meta information for process based on discrepancy in inputsample card and loaded files from source ", source_level)
                    prePackedNodes = splitProcess(base[name], 
                                                  splitProcess = splitProcessConfig, 
                                                  inclusiveProcess = inclusiveProcessConfig,
                                                  sampleName = name, 
                                                  isData = vals["isData"], 
                                                  era = vals["era"],
                                                  isUL = globalisUL,
                                                  printInfo = True,
                                                  fillDiagnosticHistos = True,
                                                  inputSampleCard=inputSampleCardYaml,
                    )
                    # print("\n\nDisabled fillDiagnosticHistos temporarily to test speedier baseline number crunching, to be re-enabled for plots...\n\n")
                    #Trigger the loop
                    _ = booktrigger.GetValue()
                    print("Finished processing")
                    for k, v in prePackedNodes["diagnosticHistos"].items():
                        print("{} - {}".format(k, v.keys()))
                    print("Writing diagnostic histos to {}".format(analysisDir + "/Diagnostics"))
                    writeHistos(prePackedNodes["diagnosticHistos"], 
                                analysisDir + "/Diagnostics",
                                channelsOfInterest="All",
                                samplesOfInterest="All",
                                dict_keys="All",
                                mode="RECREATE"
                    )
                    
                    #skip any further calculations for bookkeeping
                    continue
                else:
                    ####################
                    ### Trigger Code ###
                    ####################
                    #At this stage, lvl ~ channel (except specials like BOOKKEEPING), i.e. "ElMu", "MuMu", "El" - used to include 'baseline' or '
                    #Code for triggers from LeptonSkimmer (LeptonLogic previously)
                    #This will eventually move into defineLeptons ideally, to do the HLT and lepton selecetion entirely in RDF
                    eraTriggers = [trig for trig in TriggerList if vals.get("era", "NOERA") == trig.era]
                    #NOTE IMPORTANT CHANGE w.r.t. LeptonSkimmer: now check that either MC or that the subera matches, 
                    #but require the channel matching for BOTH instead of only data... now we filter out the MC that belongs to other channels, 
                    #instead of accepting all inclusively (skimming-appropriate)
                    triggers = [trig for trig in eraTriggers if (vals.get("isData", None) == False or vals.get("subera", "NOSUBERA") in trig.subera) and lvl == trig.channel]
                    #Create list of veto triggers for data, where explicit tiers are expected (calculating the tier first)
                    tier = [trig.tier for trig in triggers]
                    tier.sort(key=lambda i: i, reverse=False)
                    # if debug: 
                    #     print("Sorted trigger tiers selected are: " + str(tier))
                    tier = tier[0] if len(tier) > 0 else 9999
                    #Logic: select triggers if the channel matches and either it's MC (isData == False) or it's Data and the subera matches (Run B, C, D...)
                    triggers = [trig for trig in eraTriggers if (vals.get("isData", None) == False or vals.get("subera", "NOSUBERA") in trig.subera) and lvl == trig.channel]
                    #Logic: veto on triggers if the event fired a higher tier trigger and is either data + matching subera or is MC
                    vetoTriggers = [trig for trig in eraTriggers if (vals.get("isData", None) == False or vals.get("subera", "NOSUBERA") in trig.subera) and trig.tier < tier]
                    # Fired = [trig for trig in triggers if hasattr(event, trig.trigger) and getattr(event, trig.trigger, False)]
                    # Vetoed = [trig for trig in vetoTriggers if hasattr(event, trig.trigger) and getattr(event, trig.trigger, False)]
                    triggerBitSum = sum([pow(2, t.uniqueEraBit) for t in eraTriggers if t.channel == lvl])
                    tieredTriggerBitSums = dict()
                    channelToTierDict = dict()
                    vetoChannelCode = dict()
                    passChannelCode = dict()
                    channelFilterCode = dict()
                    for trig_channel, tier in [(trig.channel, trig.tier) for trig in sorted(eraTriggers, key=lambda nTup: nTup.tier, reverse=False)]:
                        if trig_channel in tieredTriggerBitSums.keys(): continue
                        channelToTierDict[trig_channel] = min([trig.tier for trig in eraTriggers if trig.channel == trig_channel])
                        tieredTriggerBitSums[trig_channel] = sum([pow(2, t.uniqueEraBit) for t in eraTriggers if t.channel == trig_channel])
                        vetoChannelCode[trig_channel] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0".format(tieredTriggerBitSums[trig_channel])
                        passChannelCode[trig_channel] = "(ESV_TriggerAndLeptonLogic_selection & {0}) > 0".format(tieredTriggerBitSums[trig_channel])
                        channelFilterCode[trig_channel] = ""
                    for trig_channel_outer in channelFilterCode.keys():                    
                        skipList = []
                        for trig_channel, tier in [(trig.channel, trig.tier) for trig in sorted(eraTriggers, key=lambda nTup: nTup.tier, reverse=False)]:
                            if trig_channel in skipList: 
                                continue
                            else:
                                skipList.append(trig_channel)
                            if channelToTierDict[trig_channel_outer] == tier:
                                if len(channelFilterCode[trig_channel_outer]) > 0:
                                    channelFilterCode[trig_channel_outer] += " && "
                                channelFilterCode[trig_channel_outer] += passChannelCode[trig_channel]
                            elif channelToTierDict[trig_channel_outer] > tier:
                                if len(channelFilterCode[trig_channel_outer]) > 0:
                                    channelFilterCode[trig_channel_outer] += " && "
                                channelFilterCode[trig_channel_outer] += vetoChannelCode[trig_channel]
                            else:
                                #Do nothing, the code is finished
                                pass
                    #Print the filter code for each channel here...
                    # for k, v in channelFilterCode.items():
                    #     print(k, v)
        
                    #Finished verification that new bitset channelFilterCode produces same output as old b, swapping in and deprecating the old one.
                    filtered[name][lvl] = base[name].Filter(channelFilterCode[lvl], lvl)
                #Add the MET corrections, creating a consistently named branch incorporating the systematics loaded
                the_df[name][lvl] = METXYCorr(filtered[name][lvl],
                                              run_branch="run",
                                              era=vals["era"],
                                              isData=vals["isData"],
                                              sysVariations=sysVariationsAll,
                                              sysFilter=scaleSystematics,
                                              verbose=verbose,
                                              )
                the_df[name][lvl] = ROOT.FTA.applyMETandPVFilters(ROOT.RDF.AsRNode(the_df[name][lvl]), 
                                                                  vals["era"], 
                                                                  globalisUL, 
                                                                  globalVFP, 
                                                                  vals["isData"], 
                                                                  cppVerbosity
                                                                  )
                the_df[name][lvl] = ROOT.FTA.AddLeptonSF(ROOT.RDF.AsRNode(the_df[name][lvl]), 
                                                         vals["era"], 
                                                         name, 
                                                         generalLUTs, 
                                                         correctorMap
                                                         )
                #Define the leptons based on LeptonLogic bits, to be updated and replaced with code based on triggers/thresholds/leptons present (on-the-fly cuts)
                the_df[name][lvl] = defineLeptons(the_df[name][lvl], 
                                                  input_lvl_filter=lvl,
                                                  isData=vals["isData"], 
                                                  era=vals["era"],
                                                  useBackupChannel=False,
                                                  triggers=triggers,
                                                  sysVariations=sysVariationsAll,
                                                  sysFilter=scaleSystematics,
                                                  rdfLeptonSelection=doLeptonSelection,
                                                  verbose=verbose,
                                                 )

                if True:
                    print("Introducing early cut on lepton number: 2 required")
                    leptoncutstring = "nFTALepton > 1"
                elif "elel" in lvl.lower():
                    print("Doing two tight leptons early cut...")
                    leptoncutstring = "nTightFTAElectron == 2 && nLooseFTAMuon == 0"
                elif "elmu" in lvl.lower():
                    print("Doing two tight leptons early cut...")
                    leptoncutstring = "nTightFTAElectron == 1 && nTightFTAMuon == 1"
                elif "mumu" in lvl.lower():
                    print("Doing two tight leptons early cut...")
                    leptoncutstring = "nLooseFTAElectron == 0 && nTightFTAMuon == 2"
                else:
                    raise RuntimeError("Unhandled logic at early lepton cut location")
                the_df[name][lvl] = the_df[name][lvl].Filter(leptoncutstring, "Early lepton filter {}".format(leptoncutstring))
                if testVariables:
                    skipTestVariables = testVariableProcessing(the_df[name][lvl], nodes=False, searchMode=True, skipColumns=[],
                                                               allowedTypes=['int','double','ROOT::VecOps::RVec<int>','float','ROOT::VecOps::RVec<float>','bool'])
                the_df[name][lvl] = defineJets(the_df[name][lvl],
                                               era=vals["era"],
                                               bTagger=bTagger,
                                               isData=vals["isData"],
                                               sysVariations=sysVariationsAll, 
                                               sysFilter=scaleSystematics,
                                               jetPtMin=jetPtMin,
                                               jetPUIdChoice=jetPUId,
                                               useDeltaR=useDeltaR,
                                               verbose=verbose,
                                              )
                if testVariables:
                    skipTestVariables += testVariableProcessing(the_df[name][lvl], nodes=False, searchMode=True, skipColumns=skipTestVariables,
                                                                allowedTypes=['int','double','ROOT::VecOps::RVec<int>','float','ROOT::VecOps::RVec<float>','bool'])
                if hasattr(options, 'noProgressBar') and options.noProgressBar:
                    print("Not preparing progress bars")
                    counts[name][lvl] = the_df[name][lvl].Count()
                else:
                    print("Booking progress bar")
                    counts[name][lvl] = ROOT.AddProgressBar(ROOT.RDF.AsRNode(the_df[name][lvl]), 
                                                            min(5000, max(1000, int(metainfo[name]["totalEvents"]/5000))), int(metainfo[name]["totalEvents"]))
                packedNodes[name][lvl] = None
                stats[name][lvl] = dict()
                effic[name][lvl] = dict()
                # btagging[name][lvl] = dict()
                cat_df[name][lvl] = {'fill_histos(...)':'NotRunOrFailed'} #will be a dictionary returned by fill_histos, so empty histo if fill_histos not run or fails
                #Get the variables to save using a function that takes the processDict as input (for special sample-specific variables to add)
                #Variable which are NOT flat will be subsequently flattened by delegateFlattening(which calls flattenVariable with some hints)
                varsToFlattenOrSave[name][lvl] = getNtupleVariables(vals, 
                                                                    isData=vals["isData"],
                                                                    era=vals["era"],
                                                                    sysVariations=sysVariationsAll,
                                                                    sysFilter=scaleSystematics,
                                                                    bTagger=bTagger
                )
                #Actually flatten variables, and store in a dict various info for those variables flattened, already flat, final ntuple vars, etc.
                the_df[name][lvl], flatteningDict[name][lvl] = delegateFlattening(the_df[name][lvl], 
                                                                                  varsToFlattenOrSave[name][lvl], 
                                                                                  channel=lvl, 
                                                                                  debug=False
                )
                if testVariables:
                    skipTestVariables += testVariableProcessing(the_df[name][lvl], nodes=False, searchMode=True, skipColumns=skipTestVariables,
                                                                allowedTypes=['int','double','ROOT::VecOps::RVec<int>','float','ROOT::VecOps::RVec<float>','bool'])
                #Inject the flat and flattened variables for saving in ntuples through the 'inputNtupleVariables'
                #Split the process based on sample-specific flags in its vals dictionary, some of which was parsed above i.e. splitProcessConfig, inclusive...
                if options.defines is not None:
                    for define in options.defines:
                        cut_var = define[:define.index("=")]
                        cut_defn = define[define.index("=")+1:]
                        the_def[name][lvl] = the_def[name][lvl].Define(cut_var, cut_defn)
                if options.filters is not None:
                    for ncut, cut in enumerate(options.filters):
                        cut_name = cut[:cut.index("=")]
                        cut_defn = cut[cut.index("=")+1:]
                        the_def[name][lvl] = the_def[name][lvl].Filter(cut_defn, cut_name)
                prePackedNodes = splitProcess(the_df[name][lvl], 
                                              splitProcess = splitProcessConfig,
                                              inputNtupleVariables=flatteningDict[name][lvl]["ntupleVariables"],
                                              inclusiveProcess = inclusiveProcessConfig,
                                              sampleName = name, 
                                              isData = vals["isData"], 
                                              era = vals["era"],
                                              printInfo = printBookkeeping,
                                              inputSampleCard=inputSampleCardYaml,
                )
                if testVariables:
                    testVariableProcessing(prePackedNodes, nodes=True, searchMode=True, skipColumns=skipTestVariables,
                                           allowedTypes=['int','double','ROOT::VecOps::RVec<int>','float','ROOT::VecOps::RVec<float>','bool'])
                #Do initial round of weights, preparation for btagging yields to be calculated
                print("\n\nFIXME: defineWeights needs input normalization for PS and potentially other systematic variations\n")
                prePackedNodes = defineWeights(name,
                                               prePackedNodes,
                                               splitProcess = splitProcessConfig,
                                               era=vals["era"],
                                               isData=vals["isData"],
                                               final=False,
                                               disableNjetMultiplicityCorrection=disableNjetMultiplicityCorrection,
                                               enableTopPtReweighting=enableTopPtReweighting,
                                               sysVariations=sysVariationsAll, 
                                               sysFilter=allSystematics,
                                               verbose=verbose,
                )
                #Get the yields, the ultimate goal of which is to determin in a parameterized way the renormalization factors for btag shape reweighting procedure
                prePackedNodes = BTaggingYields(prePackedNodes, sampleName=name, era=vals["era"], isData=vals["isData"], channel=lvl,
                                                histosDict=btagging, loadYields=BTaggingYieldsFile,
                                                useAggregate=True, useHTOnly=useHTOnly, useNJetOnly=useNJetOnly,
                                                sysVariations=sysVariationsAll, 
                                                sysFilter=allSystematics,
                                                vectorLUTs=btaggingLUTs[name],
                                                correctorMap=btaggingCorrectorMaps[name],
                                                bTagger=bTagger,
                                                calculateYields=calculateTheYields,
                                                HTArray=[500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200, 10000], 
                                                nJetArray=[4,5,6,7,8,9,10,20],
                                                verbose=verbose,
                )
                # testnode = prePackedNodes["nodes"]['2017___ttbb_SL_nr']['BaseNode']
                #Use the fact we have a yields file as the flag for being in the "final" mode for weights, so do final=True variant
                if BTaggingYieldsFile:
                    prePackedNodes = defineWeights(name,
                                                   prePackedNodes,
                                                   splitProcess = splitProcessConfig,
                                                   # inclusiveProcess = inclusiveProcessConfig,
                                                   era = vals["era"],
                                                   isData = vals["isData"],
                                                   final=True,
                                                   disableNjetMultiplicityCorrection=disableNjetMultiplicityCorrection,
                                                   enableTopPtReweighting=enableTopPtReweighting,
                                                   sysVariations=sysVariationsAll,
                                                   sysFilter=allSystematics,
                                                   verbose=verbose,
                    )
                #Hold the categorization nodes if doing histograms
                if isinstance(systematicSet, list) and "All" not in systematicSet:
                    print("Filtering systematics according to specified sets: {}".format(systematicSet))
                    #Don't need to do replacements for keys or values in this dict ($SYSTEMATIC, $ERA, $LEP_POSTFIX, etc.) as this is done in fill_histos anyway
                    sysVariationsForHistos = dict([(sv[0], sv[1]) for sv in sysVariationsAll.items() if len(set(sv[1].get("systematicSet", [""])).intersection(set(systematicSet))) > 0 or sv[0] in ["$NOMINAL", "nominal", "nom"] or "ALL" in systematicSet])
                    if "nominal" not in systematicSet:
                        skipNominalHistos = True
                    else:
                        skipNominalHistos = False
                    if verbose:
                        print(sysVariationsForHistos.keys())
                else:
                    sysVariationsForHistos = sysVariationsAll
                    skipNominalHistos = False
                if doHistos:
                    if False:
                        print("\n\nDOING NDIM HISTOGRAMS")
                        fill_histos_ndim(prePackedNodes, 
                                         splitProcess=splitProcessConfig, 
                                         sampleName=name, 
                                         channel=lvl.replace("_selection", "").replace("_baseline", ""), 
                                         isData=vals.get("isData", True), 
                                         era=vals.get("era"), 
                                         histosDict=histos,
                                         doDiagnostics=False, 
                                         doCombineHistosOnly=doCombineHistosOnly, 
                                         nJetsToHisto=10, 
                                         bTagger=bTagger,
                                         HTCut=HTCut, 
                                         ZMassMETWindow=ZMassMETWindow, 
                                         sysVariations=sysVariationsForHistos, 
                                         sysFilter=allSystematics,
                                         skipNominalHistos=skipNominalHistos,
                                         verbose=verb,
                        )
                    else:
                        packedNodes[name][lvl] = fill_histos(prePackedNodes, 
                                                            splitProcess=splitProcessConfig, 
                                                            isData = vals["isData"], 
                                                            era = vals["era"], 
                                                            triggers = triggers, 
                                                            variableSet=variableSet,
                                                            variableList=variableList,
                                                            categorySet=categorySet, 
                                                            sampleName=name, 
                                                            channel=lvl.replace("_selection", "").replace("_baseline", ""), 
                                                            histosDict=histos, 
                                                            sysVariations=sysVariationsForHistos, 
                                                            sysFilter=allSystematics, 
                                                            doCategorized=True, 
                                                            doDiagnostics=False, 
                                                            doCombineHistosOnly=doCombineHistosOnly, 
                                                            bTagger=bTagger, 
                                                            HTBins=HTBins,
                                                            HTCut=HTCut,
                                                            METCut=METCut,
                                                            ZMassMETWindow=ZMassMETWindow,
                                                            skipNominalHistos=skipNominalHistos, 
                                                            verbose=verb,
                                                            options=options)
                if doDiagnostics:
                    packedNodes[name][lvl] = fill_histos(prePackedNodes, splitProcess=splitProcessConfig, isData = vals["isData"], 
                                                        era = vals["era"], triggers = triggers, categorySet=categorySet, 
                                                        sampleName=name, channel=lvl.replace("_selection", "").replace("_baseline", ""), 
                                                        histosDict=histos, sysVariations=sysVariationsForHistos, sysFilter=allSystematics, 
                                                        doCategorized=False, doDiagnostics=True, bTagger=bTagger, 
                                                        skipNominalHistos=skipNominalHistos, verbose=verb)
    
                #Trigger the loop either by hitting the count/progressbar node or calling for a (Non-lazy) snapshot
                print("\nSTARTING THE EVENT LOOP")
                substart[name][lvl] = time.perf_counter()
                Benchmark.Start("{}/{}".format(name, lvl))
                if doNtuples:
                    print("Writing outputs...")
                    ntupleDir = analysisDir + "/Ntuples"
                    subNtupleDir = ntupleDir + "/" + lvl
                    if not os.path.isdir(subNtupleDir):
                        os.makedirs(subNtupleDir)
                    writeNtuples(prePackedNodes, subNtupleDir)
                    print("Wrote Ntuples for {} to this directory:\n{}".format(name, subNtupleDir))
                if options.stage == 'fill-nano':
                    nanoDir = analysisDir + f"/Nano/{options.channel}"
                    if not os.path.isdir(nanoDir):
                        os.makedirs(nanoDir)
                    fn_handles, fn_columns = delegateSnapshots(prePackedNodes, nanoDir, options.branchselection)
    
                #The ntuple writing will trigger the loop first, if that path is taken, but this is still safe to do always
                processed[name][lvl] = counts[name][lvl].GetValue()
                print("\nFINISHING THE EVENT LOOP")
                print("ROOT Benchmark stats...")
                Benchmark.Show("{}/{}".format(name, lvl))
                subfinish[name][lvl] = time.perf_counter()
                theTime = subfinish[name][lvl] - substart[name][lvl]
                if doRDFReport:
                    print("\nPrinting the report...")
                    reports[name].Print()
                    print("\n\n")
                if doCombineHistosOnly or doHistos or doBTaggingYields:
                    print("Writing outputs...")
                    processesOfInterest = []
                    if splitProcessConfig != None:
                        for thisProc in splitProcessConfig.get("processes", dict()).keys():
                            processesOfInterest.append(vals.get("era") + "___" + thisProc)
                    else:
                        processesOfInterest.append(vals.get("era") + "___" + name)
                    print("Writing historams for...{}".format(processesOfInterest))
    
                    if doCombineHistosOnly:
                        writeDir = analysisDir + "/Combine"
                        writeDict = histos
                        compatibility = False
                    elif doHistos:
                        writeDir = analysisDir + "/Histograms"
                        writeDict = histos
                        compatibility = False
                    if doBTaggingYields:
                        writeDir = analysisDir + "/BTaggingYields"
                        writeDict = btagging
                        compatibility = True
                    writeHistos(writeDict, 
                                writeDir,
                                variableSet=variableSet,
                                categorySet=categorySet,
                                channelsOfInterest="All",
                                samplesOfInterest=processesOfInterest,
                                systematicsOfInterest=systematicSet,
                                dict_keys="All",
                                mode="RECREATE",
                                compatibility= compatibility
                            )
                    print("Wrote Histograms for {} to this directory:\n{}".format(name, writeDir))
                processedSampleList.append(name)
                print("Processed Samples:")
                processedSamples = ""
                for n in processedSampleList:
                    processedSamples += "{} ".format(n)
                print(processedSamples)
                print("Took {}m {}s ({}s) to process {} events from sample {} in channel {}\n\n\n{}".format(theTime//60, theTime%60, theTime, processed[name][lvl], 
                             name, lvl, "".join(["\_/"]*25)))
        # Benchmark.Summary()
        if channel in ["BOOKKEEPING"]:
            # sort_order = ["filter", "fractionalContribution", "effectiveCrossSection", "snapshotPriority", 
            #               "nEventsPositive", "nEventsNegative", "sumWeights", "sumWeights2", "nominalXS", "nominalXS2", "effectiveXS", "effectiveXS2",
            #               "nLep2nJet7GenHT500-550-nominalXS", "nLep2nJet7pGenHT500p-nominalXS", "nLep1nJet9GenHT500-550-nominalXS",
            #               "nLep1nJet9pGenHT500p-nominalXS", "nLep2nJet7GenHT500-550-effectiveXS", "nLep2nJet7pGenHT500p-effectiveXS",
            #               "nLep1nJet9GenHT500-550-effectiveXS", "nLep1nJet9pGenHT500p-effectiveXS",]
            with open(inputSampleCardName.replace(".yaml", ".{}.roundtrip.yaml".format(channel)), "w") as of:
                of.write(yaml.dump(inputSampleCardYaml, Dumper=yaml.RoundTripDumper))
        return packedNodes
def otherFuncs():
    """Code stripped from jupyter notebook when converted to script."""

#This is example code for declaring TH2Lookup map and using it from python (also accessible from C++ side in RDataFrame                      
#ROOT.gInterpreter.Declare("std::map<std::string, std::vector<TH2Lookup*>> LUM;")
#ROOT.LUM["no"].push_back(ROOT.TH2Lookup("/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/BTaggingYields.root"))
#ROOT.LUM["no"].getEventYieldRatio("Aggregate", "_deepcsv", 5, 695.0)
#ROOT.LUM["bleh"].size()
#ROOT.LUM["no"].push_back(ROOT.TH2Lookup("/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/BTaggingYields.root"))
#ROOT.LUM["no"].size()
#ROOT.LUM["no"][0].getEventYieldRatio("Aggregate", "_deepcsv", 5, 695.0)
#ROOT.LUM["yes"].size()
#str(type(ROOT.LUM))
#getattr(ROOT, "LUM")["no"].size()
#if str(type(getattr(ROOT, "LUM"))) == "<class 'ROOT.map<string,vector<TH2Lookup*> >'>":
#    print("Okay!")


    print("Warning: if filtered[name][lvl] RDFs are not reset, then calling Define(*) on them will cause the error"      " with 'program state reset' due to multiple definitions for the same variable")
    loopcounter = 0
    masterstart = time.perf_counter()
    substart = dict()
    subfinish = dict()
    for name, cnt in counts.items():
        #if name in ["MuMu", "ElMu", "ElEl"]: continue
        substart[name] = time.perf_counter()
        loopcounter += 1
        print("==========={}/{}\n{}".format(loopcounter, len(counts), name))
        if "baseline" in cnt:
            print("Baseline = " + str(cnt["baseline"].GetValue()))
        else:
            print("Baseline")
        if "ElMu_baseline" in cnt:
            print("\tElMu = {}".format(cnt["ElMu_baseline"].GetValue()),end='')
        if "MuMu_baseline" in cnt:
            print("\tMuMu = {}".format(cnt["MuMu_baseline"].GetValue()),end='')
        if "ElEl_baseline" in cnt:
            print("\tElEl = {}".format(cnt["ElEl_baseline"].GetValue()),end='')
        if "Mu_baseline" in cnt:
            print("\tMu = {}".format(cnt["Mu_baseline"].GetValue()),end='')
        if "El_baseline" in cnt:
            print("\tEl = {}".format(cnt["El_baseline"].GetValue()),end='')
        print("")
        if "ElMu_baseline" in cnt and "ElEl_baseline" in cnt and "MuMu_baseline" in cnt            and "Mu_baseline" in cnt and "El_baseline" in cnt:
            print("\nTotal = {}".format(cnt["ElMu_baseline"].GetValue() + cnt["MuMu_baseline"].GetValue() + cnt["ElEl_baseline"].GetValue() + cnt["Mu_baseline"].GetValue() + cnt["El_baseline"].GetValue()))
        if "selection" in cnt:
            print("Selection = " + str(cnt["selection"].GetValue()))
        else: 
            print("Selection")
        if "ElMu_selection" in cnt:
            print("\tElMu = {}".format(cnt["ElMu_selection"].GetValue()),end='')
        if "MuMu_selection" in cnt:
            print("\tMuMu = {}".format(cnt["MuMu_selection"].GetValue()),end='')
        if "ElEl_selection" in cnt:
            print("\tElEl = {}".format(cnt["ElEl_selection"].GetValue()),end='')
        if "Mu_selection" in cnt:
            print("\tMu = {}".format(cnt["Mu_selection"].GetValue()),end='')
        if "El_selection" in cnt:
            print("\tEl = {}".format(cnt["El_selection"].GetValue()),end='')
        print("")  
        if "ElMu_selection" in cnt and "ElEl_selection" in cnt and "MuMu_selection" in cnt            and "Mu_selection" in cnt and "El_selection" in cnt:
            print("\nTotal = {}".format(cnt["ElMu_selection"].GetValue() + cnt["MuMu_selection"].GetValue() + cnt["ElEl_selection"].GetValue() + cnt["Mu_selection"].GetValue() + cnt["El_selection"].GetValue()))
        subfinish[name] = time.time()
        print("====> Took {}s to process sample {}".format(subfinish[name] - substart[name], name))
    finish = time.perf_counter()
    masterfinish = time.perf_counter()
    
    for name, val in substart.items():
        print("Took {}s to process sample {}".format(subfinish[name] - substart[name], name))
    print("Took {}m {}s to process in real-time".format((masterfinish - masterstart)//60, (masterfinish - masterstart)%60))
    
    mode="RECREATE"
    if doHLTMeans == True:
        makeHLTReport(stats, histDir)
    if doHistos == True:
        writeHistos(histos, histDir, "All", mode=mode)
        mode="UPDATE"
    if doBTaggingEfficiencies == True:
        writeHistos(btagging, histDir, "All", mode=mode)
        mode="UPDATE"
        BTaggingEfficienciesAnalyzer("{}/ElMu_selection".format(histDir))
    if doBTaggingYields == True:
        writeHistos(btagging, histDir, "BTaggingYields", mode=mode)
        mode="UPDATE"    
    
    ChiSquareTest("select_20200403/ElMu_selection/BTaggingYields/BTaggingYields.root", test_against="Aggregate__deepcsv", 
                  must_not_contain = ["up", "down"])
    ChiSquareTest("select_20200403/ElMu_selection/BTaggingYields/BTaggingYields.root", test_against="Aggregate__deepcsv", 
                  must_contain = ["Aggregate"])
    rootToPDF("select_20200403/ElMu_selection/BTaggingYields",
                outDirectory="{}/PDFSamples",
                name_format="$NAME__$ALGO$VAR",
                name_tuples=[("$NAME", ["Aggregate", "tt_DL-GF", "tt_DL", "tttt", "ttH"," tt_SL-GF", "tt_SL", 
                                        "DYJets_DL", "ST_tW", "ST_tbarW", "ttHH", "ttWH", "ttWJets", "ttWW", "ttWZ",
                                        "ttZJets", "ttZZ", "ttZH", "tttJ", "tttW"]), 
                             ("$ALGO", ["deepcsv"]),
                             ("$VAR", ["",])],
                draw_option="COLZ TEXT45E", draw_min=0.8, draw_max=1.2)
    rootToPDF("select_20200403/ElMu_selection/BTaggingYields",
                outDirectory="{}/PDFVariations",
                name_format="$NAME__$ALGO$VAR",
                name_tuples=[("$NAME", ["Aggregate",]), 
                             ("$ALGO", ["deepcsv"]),
                             ("$VAR", ["", "_shape_up_hf", "_shape_down_hf"])],
                draw_option="COLZ TEXT45E", draw_min=0.8, draw_max=1.2)
    
    if doHistos == True:
        histoCombine("{}/ElMu_selection".format(histDir))
    
    histDir = "select_20200323"
    rootToPDF("{}/ElMu_selection/BTaggingEfficiencyNotWorking".format(histDir),
             name_tuples=[("$JETTYPE", ["bjets", "cjets", "udsgjets"]), ("$TAG", ["DeepCSV_M", "DeepJet_M"]),
                             ("$CAT", ["Inclusive",])],
             draw_option="COLZ TEXT45E",
            )

    makeJetEfficiencyReport(effic, "{}/ElMu_selection/BTaggingEfficiency".format(histDir))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FTAnalyzer.py is the main framework for doing the Four Top analysis in Opposite-Sign Dilepton channel after corrections are added with nanoAOD-tools (PostProcessor). Expected corrections are JECs/Systematics, btag SFs, lepton SFs, and pileup reweighting')
    parser.add_argument('stage', action='store', type=str, choices=['bookkeeping', 'pileup', 'fill-yields', 'combine-yields', 'lepton-selection', 'fill-diagnostics', 
                                                                    'fill-histograms', 'hadd-histograms', 'fill-ntuples', 'fill-combine',
                                                                    'hadd-combine', 'fill-nano'],
                        help='analysis stage to be produced')
    parser.add_argument('--varSet', '--variableSet', dest='variableSet', action='store',
                        type=str, choices=['HTOnly', 'MVAInput', 'Control', 'Study', 'TriggerStudy', 'ResolutionStudy', 'WeightStudy', 'nPVs', 'Pileup', 'nTruePileup'], 
                        default='HTOnly', help='Variable set to include in filling templates')
    parser.add_argument('--varList', '--variableList', dest='variableList', action='store', nargs='*',
                        type=str, default=None,
                        help='Variable list to include in filling templates, must include {bpf} if it is sensitive to JEC variations, e.g. HT{bpf}')
    parser.add_argument('--categorySet', '--categorySet', dest='categorySet', action='store',
                        type=str, choices=['5x5', '5x3', '5x1', '2Bp', '2BnJet4p', '3pBnJet4p', 'SignalSensitive', 'FullyInclusive', 'BackgroundDominant', 'nBTag'], default='5x3',
                        help='Variable set to include in filling templates')
    parser.add_argument('--systematicSet', dest='systematicSet', action='store', nargs='*',
                        type=str, choices=['ALL', 'nominal', 'pu', 'pf', 'btag', 'jerc', 'ps', 'rf',
                                           'btag_hf', 'btag_lf', 'btag_other', 'pdf', 'test'], default='All',
                        help='Systematic set to include in running, defaulting to "All"')
    parser.add_argument('--source', dest='source', action='store', type=str, default='LJMLogic__{chan}_selection',
                        help='Stage of data storage to pull from, as referenced in Sample dictionaries as subkeys of the "source" key.'\
                        'Must be available in all samples to be processed. {chan} will be replaced with the channel analyzed')
    parser.add_argument('--channel', dest='channel', action='store', type=str, default="ElMu", choices=['ElMu', 'ElEl', 'MuMu', 'ElEl_LowMET', 'ElEl_HighMET', 'Mu', 'El'],
                        help='Decay channel for opposite-sign dilepton analysis')
    parser.add_argument('--analysisDirectory', dest='analysisDirectory', action='store', type=str, default="/eos/user/$U/$USER/analysis/$DATE",
                        help='output directory path defaulting to "."')
    parser.add_argument('--jetPtMin', dest='jetPtMin', action='store', default=30.0, type=float,
                        help='Float value for the minimum Jet pt in GeV, defaulting to 30.0')
    parser.add_argument('--jetPUId', dest='jetPUId', action='store', default='L', nargs='?', const='L', type=str, choices=['N', 'L', 'M', 'T'],
                        help='Apply Jet PU Id to the selected jets, with choices of None ("N"), Loose ("L"), Medium ("M"), or Tight ("T") using the 94X and 102X training in NanoAODv7.')
    parser.add_argument('--HTBins', dest='HTBins', action='store', default=50, type=int,
                        help='Number of bins in the HT distribution to use, defaulting to 100')
    parser.add_argument('--HTCut', dest='HTCut', action='store', default=500, type=float,
                        help='Float value for the HT cut for filled histograms in GeV, defaulting to 500')
    parser.add_argument('--METCut', dest='METCut', action='store', default=0.0, type=float,
                        help='Float value for the MET cut (outside Z window) for filled histograms in GeV, defaulting to 0.0')
    parser.add_argument('--ZWindowMET', dest='ZWindowMET', action='store', default=10000.0, type=float,
                        help='Float value for the MET cut (inside Z window) for filled histograms in GeV, defaulting to 10000.0')
    parser.add_argument('--ZWindowWidth', dest='ZWindowWidth', action='store', default=15.0, type=float,
                        help='Float value for the Z Boson Width (same-flavor invariant lepton mass) for filled histograms in GeV, defaulting to 15.0')
    parser.add_argument('--useDeltaR', dest='useDeltaR', action='store', type=float, default=0.4, #nargs='?', const=0.4,
                        help='Default distance parameter 0.4, use to set alternative float value for Lepton-Jet cross-cleaning')
    parser.add_argument('--usePFMatching', dest='usePFMatching', action='store_true', 
                        help='Enable usage of PFMatching for Lepton-Jet cross-cleaning')
    parser.add_argument('--disableNjetMultiplicityCorrection', '--noNjetMult', dest='disableNjetMultiplicityCorrection', action='store_true',
                        help='Disable the ttbar jet multiplicity correction on tt(+ X(Y)) processes besides the signal')
    parser.add_argument('--enableTopPtReweighting', dest='enableTopPtReweighting', action='store_true',
                        help='Enable the nnlo+nlo/powheg+pythia8 top pT reweighting on ttbar (non-ttbb) process')
    parser.add_argument('--bTagger', dest='bTagger', action='store', default='DeepJet', type=str, choices=['DeepCSV', 'DeepJet'],
                        help='bTagger algorithm to be used, default DeepJet')
    parser.add_argument('--doNtuples', dest='doNtuples', action='store_true',
                        help='Add ntuple output during other mode, such as fill-histograms')
    parser.add_argument('--noAggregate', dest='noAggregate', action='store_true',
                        help='Disable usage of aggregate BTagging Yields/Efficiencies in favor of individual per-sample maps')
    parser.add_argument('--useHTOnly', dest='useHTOnly', action='store_true',
                        help='For BTagging Yields, use 1D map depending on HT only')
    parser.add_argument('--useNJetOnly', dest='useNJetOnly', action='store_true',
                        help='For BTagging Yields, use 1D map depending on nJet only')
    parser.add_argument('--include', dest='include', action='store', default=None, type=str, nargs='*',
                        help='List of sample names to be used in the stage (if not called, defaults to all; takes precedene over exclude)')
    parser.add_argument('--exclude', dest='exclude', action='store', default=None, type=str, nargs='*',
                        help='List of sample names to not be used in the stage (if not called, defaults to none; include takes precedence)')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')
    parser.add_argument('--test', dest='test', action='store_true',
                        help='Test variables one-by-one to scan for runtime errors')
    parser.add_argument('--sample_cards', dest='sample_cards', action='store', nargs='*', type=str,
                        help='path and name of the sample card(s) to be used')
    parser.add_argument('--systematics_cards', dest='systematics_cards', action='store', nargs='*', type=str,
                        help='path and name of the systematics card(s) to be used')
    parser.add_argument('--redirector', dest='redir', action='store', type=str, nargs='?', default=None, const='root://cms-xrd-global.cern.ch/',
                        help='redirector for XRootD, such as "root://cms-xrd-global.cern.ch/"')
    parser.add_argument('--recreateFileList', dest='recreateFileList', action='store_true',
                        help='Replace old fileList caches with newly created ones, necessary if the "source" value changes for a key already used in an analysis directory.')
    parser.add_argument('--era', dest='era', action='store', type=str, default="2015", choices=['2016', '2017', '2018'],
                        help='simulation/run year')
    parser.add_argument('--nThreads', dest='nThreads', action='store', type=int, default=8, #nargs='?', const=0.4,
                        help='number of threads for implicit multithreading (0 or 1 to disable)')
    parser.add_argument('--report', dest='report', action='store_true',
                        help='Toggle the RDataFrame Filter Report')
    parser.add_argument('--noProgressBar', dest='noProgressBar', action='store_true', help='Toggle off the tqdm progress bars')
    parser.add_argument('--define', dest='defines', action='append', type=str, default=None, #nargs='*'
                        help='list of new variables with syntax variable_name=variable_definition, where both are valid C++ variable names and code, respectively. Wrap each individual define in single quotes to prevent shell parsing them as commands, i.e. \'nGoodMuons=return Sum(Muon_pt > 30 && Muon_looseId == true);\'')
    parser.add_argument('--filter', dest='filters', action='append', type=str, default=None, #nargs='*'
                        help='list of filters with syntax filter_name=filter_cut, where the former is any text and the latter is valid C++ code. Wrap each individual filter in single quotes to prevent shell parsing them as commands')
    parser.add_argument('--branchselection', dest='branchselection', action='store', type=str, default=None,
                        help='Name of file for branchselection when calling stage fill-nano, using the NanoAOD-tools syntax of keep, drop, keepmatch, and keepdrop')

    #Parse the arguments
    args = parser.parse_args()
    #Get the username and today's date for default directory:
    uname = pwd.getpwuid(os.getuid()).pw_name
    uinitial = uname[0]
    dateToday = datetime.date.today().strftime("%b-%d-%Y")

    #Grab and format required and optional arguments
    analysisDir = args.analysisDirectory.replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday)
    stage = args.stage
    # inputSampleNames, inputSamples = load_yaml_cards(args.sample_cards)
    # sysVariationNames, sysVariationsAll = load_yaml_cards(args.systematics_cards)
    sampleCards = args.sample_cards
    systematicCards = args.systematics_cards
    variableSet = args.variableSet
    variableList = args.variableList
    categorySet = args.categorySet
    systematicSet = args.systematicSet
    channel = args.channel
    era = args.era
    source = args.source.format(chan=channel)
    doNtuples = args.doNtuples
    if stage == 'fill-ntuples':
        doNtuples = True
    jetPtMin=args.jetPtMin
    jetPUId=args.jetPUId
    HTBins=args.HTBins
    HTCut=args.HTCut
    METCut=args.METCut
    ZWindowWidth=args.ZWindowWidth
    ZWindowMET=args.ZWindowMET
    disableNjetMultiplicityCorrection = args.disableNjetMultiplicityCorrection
    enableTopPtReweighting = args.enableTopPtReweighting
    useDeltaR = args.useDeltaR
    bTagger = args.bTagger
    includeSampleNames = args.include
    excludeSampleNames = args.exclude
    verb = args.verbose
    useAggregate = not args.noAggregate
    useHTOnly = args.useHTOnly
    useNJetOnly = args.useNJetOnly
    test = args.test
    nThreads = args.nThreads
    if nThreads > 1:
        ROOT.ROOT.EnableImplicitMT(nThreads)

    print("=========================================================")
    print("=               ____   _______      _                   =")
    print("=              |          |        / \                  =")
    print("=              |___       |       /   \                 =")
    print("=              |          |      /_____\                =")
    print("=              |          |     /       \               =")
    print("=                                                       =")
    print("=========================================================")

    print("Running the Four Top Analyzer")
    print("Configuring according to the input parameters")
    print("Threads: {}".format(nThreads))
    print("Analysis stage: {stg}".format(stg=stage))
    print("Analysis directory: {adir}".format(adir=analysisDir))
    print("Sample cards: {scards}".format(scards=args.sample_cards))
    print("Systematics cards: {systcards}".format(systcards=args.systematics_cards))
    print("Era to be analyzed: {era}".format(era=era))
    print("Channel to be analyzed: {chan}".format(chan=channel))
    print("Algorithm for Lepton-Jet crosscleaning: {}".format("PFMatching" if not useDeltaR else "DeltaR < {}".format(useDeltaR)))
    print("Jet selection is using these parameters: Minimum Pt: {} PU Id: {}".format(jetPtMin, jetPUId))
    print("HTCut: {htc}      METCut: {metcut}     ZMassMETWindow: [{zwidth}, {metwindow}]".format(htc=HTCut,
                                                                                                  metcut=METCut,
                                                                                                  zwidth=ZWindowWidth,
                                                                                                  metwindow=ZWindowMET))
    print("ttbar njet multiplicity correction is disabled for tt (+ X(Y)): {}".format(disableNjetMultiplicityCorrection))
    print("BTagger algorithm to be used: {tag}".format(tag=bTagger))
    print("BTagging aggregate Yields/Efficiencies will be used ({uAgg}) and depend on HT only ({uHT}) or nJet only ({uNJ})"\
          .format(uAgg=useAggregate, uHT=useHTOnly, uNJ=useNJetOnly))
    if includeSampleNames:
        print("Include samples: {incld}".format(incld=includeSampleNames))
    elif excludeSampleNames:
        print("Exclude samples: {excld}".format(excld=excludeSampleNames))
    else:
        print("Using all samples!")
    print("Redirector used (overridden if '/eos/' is in the file path!): ".format(args.redir))
    print("cached fileLists will be recreated, if they exist: {}".format(args.recreateFileList))
    print("Verbose option: {verb}".format(verb=verb))
    print("Variable set: {vS}".format(vS=variableSet))
    print("Variable list: {vL}".format(vL=variableList))
    print("Category set: {cS}".format(cS=categorySet))
    print("Systematic Set: {sS}".format(sS=systematicSet))    
    print("\n\nFIXME: Need to fix the btagging yields access, properly close file after the histograms are loaded...\n\n")

    #Run algos appropriately for the given configuration
    if stage == 'fill-yields':
        print("This function needs reworking... work on it")
        print("Filling BTagging sum of weights (yields) before and after applying shape-correction scale factors for the jets")
        # print('main(analysisDir=analysisDir, channel=channel, doBTaggingYields=True, doHistos=False, BTaggingYieldsFile="{}", source=source, verbose=False)')
        packed = main(analysisDir, sampleCards, source, channel, bTagger, systematicCards, TriggerList, doDiagnostics=False, doHistos=False, doBTaggingYields=True, BTaggingYieldsFile="{}", 
                      BTaggingYieldsAggregate=useAggregate, useDeltaR=useDeltaR, jetPtMin=jetPtMin, jetPUId=jetPUId, 
                      HTBins=HTBins, HTCut=HTCut, METCut=METCut, ZMassMETWindow=[ZWindowWidth, ZWindowMET], useHTOnly=useHTOnly, useNJetOnly=useNJetOnly, 
                      disableNjetMultiplicityCorrection=disableNjetMultiplicityCorrection, enableTopPtReweighting=enableTopPtReweighting,
                      printBookkeeping = False, triggers=TriggerList, includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, 
                      testVariables=test, categorySet=categorySet, variableSet=variableSet, variableList=variableList, systematicSet=systematicSet, nThreads=nThreads, redirector=args.redir, 
                      recreateFileList=args.recreateFileList, doRDFReport=args.report, options=args)
        # main(analysisDir=analysisDir, channel=channel, doBTaggingYields=True, doHistos=False, BTaggingYieldsFile="{}", source=source, 
        #      verbose=False)
        # packed = main(analysisDir, source, channel, bTagger=bTagger, doDiagnostics=False, doHistos=False, doBTaggingYields=True, 
        #               BTaggingYieldsFile="{}", triggers=TriggerList, includeSampleNames=includeSampleNames, 
        #               sysVexcludeSampleNames=excludeSampleNames, verbose=verb)

    elif stage == 'combine-yields':
        print("Combining BTagging yields and calculating ratios, a necessary ingredient for calculating the final btag event weight for filling histograms")
        yieldDir = "{adir}/BTaggingYields/{chan}".format(adir=analysisDir, chan=channel)
        globKey = "*.root"
        print("Looking for files to combine into yield ratios inside {ydir}".format(ydir=yieldDir))
        if verb:
            f = glob.glob("{}/{}".format(yieldDir, globKey))
            f = [fiter for fiter in f if fiter.split("/")[-1] != "BTaggingYields.root"]
            print("\nFound these files: ")
            for fiter in f: print("\t\t{}".format(fiter))
        BTaggingYieldsAnalyzer(yieldDir, outDirectory="{}", globKey=globKey, stripKey=".root", includeSampleNames=includeSampleNames, 
                               excludeSampleNames=excludeSampleNames, mode="RECREATE", doNumpyValidation=False, forceDefaultRebin=False, verbose=verb,
                               internalKeys = {"Numerators":["_sumW_before"],
                                               "Denominator": "_sumW_after",
                                           },
                               internalKeysReplacements = {"BTaggingYield": "",
                                                           "_sumW_before": "",
                                                           "_sumW_after": "",
                                                       },
                               sampleRebin={"default": {"Y": None,
                                                        "X": None,
                                                    },
                                        },
                               # sampleRebin={"default": {"Y": [4, 5, 6, 7, 8, 9, 20],
                               #                          "X": [500.0, 600, 700.0, 900.0, 1100.0, 3200.0],
                               #                      },
                               #          },
                               # overrides={"Title": "$NAME BTaggingYield r=#frac{#Sigma#omega_{before}}{#Sigma#omega_{after}}($INTERNALS)",
                               #            "Xaxis": "H_{T}/Bin (GeV)",
                               #            "Yaxis": "nJet",
                               #        },
                           )
    elif stage == 'lepton-selection':
        packed = main(analysisDir, sampleCards, source, channel, bTagger, systematicCards, TriggerList, doDiagnostics=False, doHistos=False, doLeptonSelection=True, doBTaggingYields=False, 
                      BTaggingYieldsFile="{}", BTaggingYieldsAggregate=useAggregate, jetPtMin=jetPtMin, jetPUId=jetPUId, 
                      HTBins=HTBins, HTCut=HTCut, METCut=METCut, ZMassMETWindow=[ZWindowWidth, ZWindowMET], useDeltaR=useDeltaR, 
                      useHTOnly=useHTOnly, useNJetOnly=useNJetOnly, printBookkeeping = False, triggers=TriggerList,  
                      disableNjetMultiplicityCorrection=disableNjetMultiplicityCorrection, enableTopPtReweighting=enableTopPtReweighting,
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, testVariables=test,
                      categorySet=categorySet, variableSet=variableSet, variableList=variableList, systematicSet=systematicSet, nThreads=nThreads, redirector=args.redir, 
                      recreateFileList=args.recreateFileList, doRDFReport=args.report, options=args)
    elif stage == 'fill-diagnostics':
        print("This method needs some to-do's checked off. Work on it.")
        packed = main(analysisDir, sampleCards, source, channel, bTagger, systematicCards, TriggerList, doDiagnostics=True, doHistos=False, doBTaggingYields=False, BTaggingYieldsFile="{}", 
                      BTaggingYieldsAggregate=useAggregate, jetPtMin=jetPtMin, jetPUId=jetPUId, 
                      HTBins=HTBins, HTCut=HTCut, METCut=METCut, ZMassMETWindow=[ZWindowWidth, ZWindowMET], useDeltaR=useDeltaR, useHTOnly=useHTOnly, 
                      useNJetOnly=useNJetOnly, printBookkeeping = False, triggers=TriggerList,  
                      disableNjetMultiplicityCorrection=disableNjetMultiplicityCorrection, enableTopPtReweighting=enableTopPtReweighting,
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, testVariables=test,
                      categorySet=categorySet, variableSet=variableSet, variableList=variableList, systematicSet=systematicSet, nThreads=nThreads, redirector=args.redir, 
                      recreateFileList=args.recreateFileList, doRDFReport=args.report, options=args)
    elif stage == 'bookkeeping':
        packed = main(analysisDir, sampleCards, source, "BOOKKEEPING", bTagger, systematicCards, TriggerList, doDiagnostics=False, doHistos=False, doBTaggingYields=False, BTaggingYieldsFile="{}", 
                      BTaggingYieldsAggregate=useAggregate, jetPtMin=jetPtMin, jetPUId=jetPUId, 
                      HTBins=HTBins, HTCut=HTCut, METCut=METCut, ZMassMETWindow=[ZWindowWidth, ZWindowMET], useDeltaR=useDeltaR, useHTOnly=useHTOnly, 
                      useNJetOnly=useNJetOnly, printBookkeeping = True, triggers=TriggerList,  
                      disableNjetMultiplicityCorrection=disableNjetMultiplicityCorrection, enableTopPtReweighting=enableTopPtReweighting,
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, testVariables=test,
                      categorySet=categorySet, variableSet=variableSet, variableList=variableList, systematicSet=systematicSet, nThreads=nThreads, redirector=args.redir, 
                      recreateFileList=args.recreateFileList, doRDFReport=args.report, options=args)
    elif stage == 'pileup':
        packed = main(analysisDir, sampleCards, source, "PILEUP", bTagger, systematicCards, TriggerList, doDiagnostics=False, doHistos=False, doBTaggingYields=False, BTaggingYieldsFile="{}", 
                      BTaggingYieldsAggregate=useAggregate, jetPtMin=jetPtMin, jetPUId=jetPUId, 
                      HTBins=HTBins, HTCut=HTCut, METCut=METCut, ZMassMETWindow=[ZWindowWidth, ZWindowMET], useDeltaR=useDeltaR, useHTOnly=useHTOnly, 
                      useNJetOnly=useNJetOnly, printBookkeeping = True, triggers=TriggerList,  
                      disableNjetMultiplicityCorrection=disableNjetMultiplicityCorrection, enableTopPtReweighting=enableTopPtReweighting,
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, testVariables=test,
                      categorySet=categorySet, variableSet=variableSet, variableList=variableList, systematicSet=systematicSet, nThreads=nThreads, redirector=args.redir, 
                      recreateFileList=args.recreateFileList, doRDFReport=args.report, options=args)
    elif stage == 'fill-histograms':
        #filling ntuples is also possible with the option --doNtuples
        packed = main(analysisDir, sampleCards, source, channel, bTagger, systematicCards, TriggerList, doDiagnostics=False, 
                      doNtuples=doNtuples, doHistos=True, doCombineHistosOnly=False,
                      doBTaggingYields=False, BTaggingYieldsFile="{}", BTaggingYieldsAggregate=useAggregate, 
                      jetPtMin=jetPtMin, jetPUId=jetPUId, HTBins=HTBins, HTCut=HTCut, METCut=METCut, ZMassMETWindow=[ZWindowWidth, ZWindowMET], useDeltaR=useDeltaR, useHTOnly=useHTOnly, 
                      disableNjetMultiplicityCorrection=disableNjetMultiplicityCorrection, enableTopPtReweighting=enableTopPtReweighting,
                      useNJetOnly=useNJetOnly, printBookkeeping = False, triggers=TriggerList, 
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, testVariables=test,
                      categorySet=categorySet, variableSet=variableSet, variableList=variableList, systematicSet=systematicSet, nThreads=nThreads, redirector=args.redir, 
                      recreateFileList=args.recreateFileList, doRDFReport=args.report, options=args)
    elif stage == 'fill-combine':
        #filling ntuples is also possible with the option --doNtuples
        packed = main(analysisDir, sampleCards, source, channel, bTagger, systematicCards, TriggerList, doDiagnostics=False, 
                      doNtuples=doNtuples, doHistos=True, doCombineHistosOnly=True,
                      doBTaggingYields=False, BTaggingYieldsFile="{}", BTaggingYieldsAggregate=useAggregate, 
                      jetPtMin=jetPtMin, jetPUId=jetPUId, HTBins=HTBins, HTCut=HTCut, METCut=METCut, ZMassMETWindow=[ZWindowWidth, ZWindowMET], useDeltaR=useDeltaR, useHTOnly=useHTOnly, 
                      disableNjetMultiplicityCorrection=disableNjetMultiplicityCorrection, enableTopPtReweighting=enableTopPtReweighting,
                      useNJetOnly=useNJetOnly, printBookkeeping = False, triggers=TriggerList, 
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, testVariables=test,
                      categorySet=categorySet, variableSet=variableSet, variableList=variableList, systematicSet=systematicSet, nThreads=nThreads, redirector=args.redir, 
                      recreateFileList=args.recreateFileList, doRDFReport=args.report, options=args)
    elif stage == 'hadd-histograms' or stage == 'hadd-combine':
        print("Combining root files for plotting")
        if stage == 'hadd-histograms':
            histDir = "{adir}/Histograms".format(adir=analysisDir, chan=channel)
            writeDir = "{adir}/Histograms/All".format(adir=analysisDir)
        elif stage == 'hadd-combine':
            histDir = "{adir}/Combine".format(adir=analysisDir, chan=channel)
            writeDir = "{adir}/Combine/All".format(adir=analysisDir)
        else:
            raise RuntimeError("hadd stage not properly configured with histDir and writeDir")
        if not os.path.isdir(writeDir):
            os.makedirs(writeDir)
        
        globKey = "**/*" + args.variableSet + "*" + args.categorySet + "*.root"
        print("Looking for histogram files to combine inside {hdir}, with key {glk}".format(hdir=histDir, glk=globKey))
        f = glob.glob("{}/{}".format(histDir, globKey))
        f = [ff for ff in f if histDir+"/All" not in ff]
        fexcluded = [ff for ff in f if histDir+"/All" in ff]
        if len(fexcluded) > 0:
            print("Excluded these files: ")
            for fiter in fexcluded: print("\t\t{}".format(fiter))
        if verb:
            print("\nFound these files: ")
            for fiter in f: print("\t\t{}".format(fiter))
        cmd = "hadd -f {wdir}/{era}___{vS}___{cS}.root {ins}".format(wdir=writeDir, era=era, vS=args.variableSet, cS=args.categorySet, ins=" ".join(f)) 
        # print(cmd)
        spo = subprocess.Popen(args="{}".format(cmd), shell=True, executable="/bin/zsh", env=dict(os.environ))
        spo.communicate()
    elif stage == 'fill-ntuples' or 'fill-nano':
        packed = main(analysisDir, sampleCards, source, channel, bTagger, systematicCards, TriggerList, doDiagnostics=False, 
                      doNtuples=doNtuples, 
                      doHistos=False, doBTaggingYields=False, BTaggingYieldsFile="{}", BTaggingYieldsAggregate=useAggregate, 
                      jetPtMin=jetPtMin, jetPUId=jetPUId, useDeltaR=useDeltaR, useHTOnly=useHTOnly, 
                      disableNjetMultiplicityCorrection=disableNjetMultiplicityCorrection, enableTopPtReweighting=enableTopPtReweighting,
                      useNJetOnly=useNJetOnly, printBookkeeping = False, triggers=TriggerList, 
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, 
                      testVariables=test, categorySet=categorySet, variableSet=variableSet, variableList=variableList, systematicSet=systematicSet, 
                      nThreads=nThreads, redirector=args.redir, recreateFileList=args.recreateFileList, doRDFReport=args.report, options=args)
    else:
        print("stage {stag} is not yet prepared, please update the FTAnalyzer".format(stag))

