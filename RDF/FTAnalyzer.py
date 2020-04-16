#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!pip install graphviz --user
#!echo $PYTHONPATH
#!ls -ltr /eos/user/n/nmangane/.local/lib/python2.7/site-packages/
#!export PATH=/eos/user/n/nmangane/.local/lib/python2.7/site-packages/:$PATH
#!ls -ltr | grep .root
get_ipython().system(u'ls -ltr /eos/user/n/nmangane/CMSSW/CMSSW_10_2_18/src/FourTopNAOD/RDF/')
#Notes: When nJet cut is applied for variations, must account for different counts when JES changes. 
#Therefore, this must b inside the histogramming function


# In[ ]:


from __future__ import print_function
import os, time, sys, collections, array
import ROOT
import numpy as np
#from IPython.display import Image, display, SVG
#import graphviz

useSpark = False #Doesn't seem to work with gcc8 at least...
if useSpark:
    import PyRDF
    PyRDF.use("spark", {'npartitions': '8'}) #was 32 in example
    RDF = PyRDF.RDataFrame
else:
    #print("DISABLING IMT for bebugging branches")
    ROOT.ROOT.EnableImplicitMT()
    RS = ROOT.ROOT
    RDF = RS.RDataFrame


# In[ ]:


#Load functions, can eventually be changed to ROOT.gInterpreter.Declare(#include "someheader.h")
#WARNING! Do not rerun this cell without restarting the kernel, it will kill it!
ROOT.TH1.SetDefaultSumw2() #Make sure errors are done this way
ROOT.gROOT.ProcessLine(".L /eos/user/n/nmangane/CMSSW/CMSSW_10_2_18/src/FourTopNAOD/RDF/test_class.cpp")


# In[ ]:


#FIXME: Need filter efficiency calculated for single lepton generator filtered sample. First approximation will be from MCCM (0.15) but as seen before, it's not ideal. 
#May need to recalculate using genWeight/sumWeights instead of sign(genWeight)/(nPositiveEvents - nNegativeEvents), confirm if there's any difference.
lumi = {"2017": 41.53,
        "2018": 1}
era = "2017"
leg_dict = {"tttt": ROOT.kAzure-2,
            "ttbar": ROOT.kRed,
            "singletop": ROOT.kYellow,
            "ttH": ROOT.kMagenta,
            "ttVJets": ROOT.kViolet,
            "ttultrarare": ROOT.kGreen,
            "DY": ROOT.kCyan,
            "Data": ROOT.kBlack,
            "QCD": ROOT.kPink,
           }
microbookerV2 = {
    "tttt":{
        "era": "2017",
        "isData": False,
        "nEvents": 2273928,
        "nEventsPositive": 1561946,
        "nEventsNegative": 711982,
        "sumWeights": 18645.487772,
        "sumWeights2": 1094.209551,
        "isSignal": True,
        "crossSection": 0.012,
        "color": leg_dict["tttt"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttt-*_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttt-1_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tttt-2_2017_v2.root"],
        "destination": "/$HIST_CLASS/$HIST/tttt/$SYSTEMATIC",
    },
    "tt_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 69098644,
        "nEventsPositive": 68818780,
        "nEventsNegative": 279864,
        "sumWeights": 4980769113.241218,
        "sumWeights2": 364913493679.955078,
        "isSignal": False,
        "crossSection": 89.0482,
        "color": leg_dict["ttbar"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-*_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-1_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-2_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-3_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-4_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-5_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-6_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-7_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-8_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-9_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-10_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-11_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-12_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-13_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-14_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_DL/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Nominal",
                   "channel": "DL"
                  },
    },
    "tt_SL":{
        "era": "2017",
        "isData": False,
        "nEvents": 20122010,
        "nEventsPositive": 20040607,
        "nEventsNegative": 81403,
        "sumWeights": 6052480345.748356,
        "sumWeights2": 1850350248120.376221,
        "isSignal": False,
        "crossSection": 366.2073,
        "color": leg_dict["ttbar"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_SL/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Nominal",
                   "channel": "SL"
                  },
    },

    "ST_tW":{
        "era": "2017",
        "isData": False,
        "nEvents": 7945242,
        "nEventsPositive": 7914815,
        "nEventsNegative": 30427,
        "sumWeights": 277241050.840222,
        "sumWeights2": 9823995766.508368,
        "isSignal": False,
        "crossSection": 35.8,
        "color": leg_dict["singletop"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tW_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tW_2017_v2.root"],
        "destination": "/$HIST_CLASS/$HIST/ST_tW/$SYSTEMATIC",
    },
    "ST_tbarW":{
        "era": "2017",
        "isData": False,
        "nEvents": 7745276,
        "nEventsPositive": 7715654,
        "nEventsNegative": 30427,
        "sumWeights": 270762750.172525,
        "sumWeights2": 9611964941.797768,
        "isSignal": False,
        "crossSection": 35.8,
        "color": leg_dict["singletop"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tbarW_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tbarW_2017_v2.root"],
        "destination": "/$HIST_CLASS/$HIST/ST_tbarW/$SYSTEMATIC",
    },
    "DYJets_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 49125561,
        "nEventsPositive": 49103859,
        "nEventsNegative": 21702,
        "sumWeights": 49082157.000000,
        "sumWeights2": 49125561.000000,
        "isSignal": False,
        "crossSection": 5075.6,
        "color": leg_dict["DY"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-*_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-1_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-2_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-3_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-4_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-5_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-6_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-7_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/DYJets_DL/$SYSTEMATIC",
    },
}
tt_data_V2 = {
    "tt_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 69098644,
        "nEventsPositive": 68818780,
        "nEventsNegative": 279864,
        "sumWeights": 4980769113.241218,
        "sumWeights2": 364913493679.955078,
        "isSignal": False,
        "crossSection": 89.0482,
        "color": leg_dict["ttbar"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-*_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-1_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-2_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-3_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-4_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-5_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-6_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-7_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-8_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-9_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-10_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-11_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-12_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-13_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-14_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_DL/$SYSTEMATIC",
    },
    "tt_SL":{
        "era": "2017",
        "isData": False,
        "nEvents": 20122010,
        "nEventsPositive": 20040607,
        "nEventsNegative": 81403,
        "sumWeights": 6052480345.748356,
        "sumWeights2": 1850350248120.376221,
        "isSignal": False,
        "crossSection": 366.2073,
        "color": leg_dict["ttbar"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_SL/$SYSTEMATIC",
    },
    "ElMu":{
        "era": "2017",
        "subera": "BCDEF",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 4453465 + 15595214 + 9164365 + 19043421 + 25776363,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElMu_*_2017.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElMu_*_2017.root",],
        "destination": "/$HIST_CLASS/$HIST/ElMu/$SYSTEMATIC",
    },    
}
bookerV2_MC = {
    "tttt":{
        "era": "2017",
        "isData": False,
        "nEvents": 2273928,
        "nEventsPositive": 1561946,
        "nEventsNegative": 711982,
        "sumWeights": 18645.487772,
        "sumWeights2": 1094.209551,
        "isSignal": True,
        "crossSection": 0.012,
        "color": leg_dict["tttt"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttt-*_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tttt-*_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tttt-*_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tttt-*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttt-1_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tttt-2_2017_v2.root"],
        "destination": "/$HIST_CLASS/$HIST/tttt/$SYSTEMATIC",
    },
    "tt_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 69098644,
        "nEventsPositive": 68818780,
        "nEventsNegative": 279864,
        "sumWeights": 4980769113.241218,
        "sumWeights2": 364913493679.955078,
        "isSignal": False,
        "doFilter": True,
        "crossSection": 89.0482,
        "color": leg_dict["ttbar"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-*_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_DL-NOM-*_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_DL-NOM-*_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_DL-NOM-*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-1_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-2_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-3_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-4_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-5_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-6_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-7_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-8_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-9_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-10_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-11_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-12_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-13_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-14_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_DL/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Nominal",
                   "channel": "DL"
                  },
    },
    "tt_DL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8510388,
        "nEventsPositive": 8467543,
        "nEventsNegative": 42845,
        "sumWeights": 612101836.284397,
        "sumWeights2": 44925503249.097206,
        "isSignal": False,
        "doFilter": True,
        "crossSection": 1.4815,
        "color": leg_dict["ttbar"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-*_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_DL-GF-*_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_DL-GF-*_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_DL-GF-*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-1_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-2_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-3_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-4_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_DL-GF/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Filtered",
                   "channel": "DL"
                  },
    },
    "tt_SL":{
        "era": "2017",
        "isData": False,
        "nEvents": 20122010,
        "nEventsPositive": 20040607,
        "nEventsNegative": 81403,
        "sumWeights": 6052480345.748356,
        "sumWeights2": 1850350248120.376221,
        "isSignal": False,
        "doFilter": True,
        "crossSection": 366.2073,
        "color": leg_dict["ttbar"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_SL-NOM_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_SL-NOM_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_SL-NOM_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_SL/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Nominal",
                   "channel": "SL"
                  },
    },
    "tt_SL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8836856,
        "nEventsPositive": 8794464,
        "nEventsNegative": 42392,
        "sumWeights": 2653328498.476976,
        "sumWeights2": 812201885978.209229,
        "isSignal": False,
        "doFilter": True,
        "crossSection": 12.4071,
        "color": leg_dict["ttbar"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-GF_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_SL-GF_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_SL-GF_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_SL-GF_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-GF_2017_v2.root"],
        "destination": "/$HIST_CLASS/$HIST/tt_SL-GF/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Filtered",
                   "channel": "SL"
                  },
    },
    "ST_tW":{
        "era": "2017",
        "isData": False,
        "nEvents": 7945242,
        "nEventsPositive": 7914815,
        "nEventsNegative": 30427,
        "sumWeights": 277241050.840222,
        "sumWeights2": 9823995766.508368,
        "isSignal": False,
        "crossSection": 35.8,
        "color": leg_dict["singletop"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tW_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ST_tW_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ST_tW_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ST_tW_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tW_2017_v2.root"],
        "destination": "/$HIST_CLASS/$HIST/ST_tW/$SYSTEMATIC",
    },
    "ST_tbarW":{
        "era": "2017",
        "isData": False,
        "nEvents": 7745276,
        "nEventsPositive": 7715654,
        "nEventsNegative": 30427,
        "sumWeights": 270762750.172525,
        "sumWeights2": 9611964941.797768,
        "isSignal": False,
        "crossSection": 35.8,
        "color": leg_dict["singletop"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tbarW_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ST_tbarW_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ST_tbarW_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ST_tbarW_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tbarW_2017_v2.root"],
        "destination": "/$HIST_CLASS/$HIST/ST_tbarW/$SYSTEMATIC",
    },
    "DYJets_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 49125561,
        "nEventsPositive": 49103859,
        "nEventsNegative": 21702,
        "sumWeights": 49082157.000000,
        "sumWeights2": 49125561.000000,
        "isSignal": False,
        "crossSection": 5075.6,
        "color": leg_dict["DY"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-*_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/DYJets_DL-*_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/DYJets_DL-*_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/DYJets_DL-*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-1_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-2_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-3_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-4_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-5_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-6_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-7_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/DYJets_DL/$SYSTEMATIC",
    },
    "ttH":{
        "era": "2017",
        "isData": False,
        "nEvents": 8000000,
        "nEventsPositive": 7916867,
        "nEventsNegative": 83133,
        "sumWeights": 4216319.315884,
        "sumWeights2": 2317497.816608,
        "isSignal": False,
        "crossSection": 0.2934,
        "color": leg_dict["ttH"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttH_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttH_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttH_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttH_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttH_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ttH/$SYSTEMATIC",
    },
    "ttWJets":{
        "era": "2017",
        "isData": False,
        "nEvents": 9425384,
        "nEventsPositive": 9404856,
        "nEventsNegative": 20528,
        "sumWeights": 9384328.000000,
        "sumWeights2": 9425384.000000,
        "isSignal": False,
        "crossSection": 0.611,
        "color": leg_dict["ttVJets"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWJets_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttWJets_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttWJets_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttWJets_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWJets_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ttWJets/$SYSTEMATIC",
    },
    "ttZJets":{
        "era": "2017",
        "isData": False,
        "nEvents": 8536618,
        "nEventsPositive": 8527846,
        "nEventsNegative": 8772,
        "sumWeights": 8519074.000000,
        "sumWeights2": 8536618.000000,
        "isSignal": False,
        "crossSection": 0.783,
        "color": leg_dict["ttVJets"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZJets_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttZJets_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttZJets_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttZJets_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZJets_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ttZJets/$SYSTEMATIC",
    },
    "ttWH":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199491,
        "nEventsNegative": 509,
        "sumWeights": 198839.680865,
        "sumWeights2": 199704.039588,
        "isSignal": False,
        "crossSection": 0.001572,
        "color": leg_dict["ttultrarare"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWH_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttWH_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttWH_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttWH_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWH_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ttWH/$SYSTEMATIC",
    },
    "ttWW":{
        "era": "2017",
        "isData": False,
        "nEvents": 962000,
        "nEventsPositive": 962000,
        "nEventsNegative": 0,
        "sumWeights": 962000.000000,
        "sumWeights2": 962000.000000,
        "isSignal": False,
        "crossSection": 0.007882,
        "color": leg_dict["ttultrarare"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWW_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttWW_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttWW_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttWW_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWW_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ttWW/$SYSTEMATIC",
    },
    "ttWZ":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199379,
        "nEventsNegative": 621,
        "sumWeights": 198625.183551,
        "sumWeights2": 199708.972601,
        "isSignal": False,
        "crossSection": 0.002974,
        "color": leg_dict["ttultrarare"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWZ_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttWZ_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttWZ_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttWZ_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWZ_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ttWZ/$SYSTEMATIC",
    },
    "ttZZ":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199686,
        "nEventsNegative": 314,
        "sumWeights": 199286.628891,
        "sumWeights2": 199816.306332,
        "isSignal": False,
        "crossSection": 0.001572,
        "color": leg_dict["ttultrarare"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZZ_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttZZ_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttZZ_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttZZ_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZZ_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ttZZ/$SYSTEMATIC",
    },
    "ttZH":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199643,
        "nEventsNegative": 357,
        "sumWeights": 199192.234990,
        "sumWeights2": 199794.753976,
        "isSignal": False,
        "crossSection": 0.01253,
        "color": leg_dict["ttultrarare"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZH_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttZH_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttZH_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttZH_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZH_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ttZH/$SYSTEMATIC",
    },
    "ttHH":{
        "era": "2017",
        "isData": False,
        "nEvents": 194817,
        "nEventsPositive": 194516,
        "nEventsNegative": 301,
        "sumWeights": 194116.909912,
        "sumWeights2": 194611.090542,
        "isSignal": False,
        "crossSection": 0.0007408,
        "color": leg_dict["ttultrarare"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttHH_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttHH_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttHH_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttHH_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttHH_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ttHH/$SYSTEMATIC",
    },    
    "tttW":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199852,
        "nEventsNegative": 148,
        "sumWeights": 199552.187377,
        "sumWeights2": 199697.648421,
        "isSignal": False,
        "crossSection": 0.007882,
        "color": leg_dict["ttultrarare"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttW_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tttW_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tttW_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tttW_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttW_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tttW/$SYSTEMATIC",
    },
    "tttJ":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199273,
        "nEventsNegative": 727,
        "sumWeights": 198394.878491,
        "sumWeights2": 199663.384954,
        "isSignal": False,
        "crossSection": 0.0004741,
        "color": leg_dict["ttultrarare"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttJ_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tttJ_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tttJ_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tttJ_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttJ_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tttJ/$SYSTEMATIC",
    },
}
bookerV2_ElMu = {
    "ElMu":{
        "era": "2017",
        "subera": "BCDEF",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 4453465 + 15595214 + 9164365 + 19043421 + 25776363,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_*_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/data_ElMu_*_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/data_ElMu_*_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/data_ElMu_*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_B_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_C_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_D_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_E_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_F_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ElMu/NOMINAL",
    },
}
bookerV2_MuMu = {
    "MuMu":{
        "era": "2017",
        "subera": "BCDEF",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 14501767 + 49636525 + 23075733 + 51589091 + 79756560,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_*_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/data_MuMu_*_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/data_MuMu_*_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/data_MuMu_*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_B_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_C_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_D_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_E_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_F_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/MuMu/NOMINAL",
        },
}
bookerV2_ElEl = {
    "ElEl":{
        "era": "2017",
        "subera": "B",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 58088760 + 65181125 + 25911432 + 56233597 + 74307066,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_*_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/data_ElEl_*_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/data_ElEl_*_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/data_ElEl_*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_B_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_C_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_D_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_E_2017_v2.root",
                        "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_F_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ElEl/NOMINAL",
        },
}
cutoutV2_ToBeFixed = {
    "Mu":{
        "era": "2017",
        "subera": "BCDEF",
        "channel": "Mu",
        "isData": True,
        "nEvents": 136300266 + 165652756 + 70361660 + 154630534 + 242135500,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_*_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/data_Mu_*_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/data_Mu_*_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/data_Mu_*_2017_v2*.root",
                  },
        },
    "El":{
        "era": "2017",
        "subera": "BCDEF",
        "channel": "El",
        "isData": True,
        "nEvents": 60537490 + 136637888 + 51526710 + 102121689 + 128467223,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_*_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/data_El_*_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/data_El_*_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/data_El_*_2017_v2*.root",
                  },
        },
    "QCD_HT200":{
        "era": "2017",
        "isData": False,
        "nEvents": 59200263,
        "nEventsPositive": 59166789,
        "nEventsNegative": 32544,
        "sumWeights": 59133315.000000,
        "sumWeights2": 59200263.000000,
        "isSignal": False,
        "crossSection": 1712000.0,
        "color": leg_dict["QCD"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT200_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT200_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT200_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT200_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT200_2017_v2.root",],
    },
    "QCD_HT300":{
        "era": "2017",
        "isData": False,
        "nEvents": 59569132,
        "nEventsPositive": 59514373,
        "nEventsNegative": 54759,
        "sumWeights": 59459614.000000,
        "sumWeights2": 59569132.000000,
        "isSignal": False,
        "crossSection": 347700.0,
        "color": leg_dict["QCD"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT300_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT300_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT300_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT300_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT300_2017_v2.root",],
    },   
    "QCD_HT500":{
        "era": "2017",
        "isData": False,
        "nEvents": 56207744,
        "nEventsPositive": 56124381,
        "nEventsNegative": 83363,
        "sumWeights": 56041018.000000,
        "sumWeights2": 56207744.000000,
        "isSignal": False,
        "crossSection": 32100.0,
        "color": leg_dict["QCD"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT500_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT500_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT500_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT500_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT500_2017_v2.root",],
    },
    "QCD_HT700":{
        "era": "2017",
        "isData": False,
        "nEvents": 46840955,
        "nEventsPositive": 46739970,
        "nEventsNegative": 100985,
        "sumWeights": 46638985.000000,
        "sumWeights2": 46840955.000000,
        "isSignal": False,
        "crossSection": 6831.0,
        "color": leg_dict["QCD"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT700_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT700_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT700_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT700_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT700_2017_v2.root",],
    },
    "QCD_HT1000":{
        "era": "2017",
        "isData": False,
        "nEvents": 16882838,
        "nEventsPositive": 16826800,
        "nEventsNegative": 56038,
        "sumWeights": 16770762.000000,
        "sumWeights2": 16882838.000000,
        "isSignal": False,
        "crossSection": 1207.0,
        "color": leg_dict["QCD"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1000_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT1000_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT1000_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT1000_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1000_2017_v2.root",],
    },
    "QCD_HT1500":{
        "era": "2017",
        "isData": False,
        "nEvents": 11634434,
        "nEventsPositive": 11571519,
        "nEventsNegative": 62915,
        "sumWeights": 11508604.000000,
        "sumWeights2": 11634434.000000,
        "isSignal": False,
        "crossSection": 119.9,
        "color": leg_dict["QCD"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1500_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT1500_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT1500_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT1500_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1500_2017_v2.root",],
    },
    "QCD_HT2000":{
        "era": "2017",
        "isData": False,
        "nEvents": 5941306,
        "nEventsPositive": 5883436,
        "nEventsNegative": 57870,
        "sumWeights": 5825566.000000,
        "sumWeights2": 5941306.000000,
        "isSignal": False,
        "crossSection": 25.24,
        "color": leg_dict["QCD"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT2000_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT2000_2017_v2*.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT2000_2017_v2*.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT2000_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT2000_2017_v2.root",],
    },
    "ElMu_B":{
        "era": "2017",
        "subera": "B",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 4453465,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_B*_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_B_2017.root",],
        },
    "ElMu_C":{
        "era": "2017",
        "subera": "C",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 15595214, 
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_C*_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_C_2017.root",],
        },
    "ElMu_D":{
        "era": "2017",
        "subera": "D",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 9164365,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_D*_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_D_2017.root",],
        },
    "ElMu_E":{
        "era": "2017",
        "subera": "E",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 19043421,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_E*_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_E_2017.root",],
        },
    "ElMu_F":{
        "era": "2017",
        "subera": "F",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 25776363,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_F*_2017_v2.root",},
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_F_2017.root",],
        },
    "MuMu_B":{
        "era": "2017",
        "subera": "B",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 14501767,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_B*_2017_v2.root",},
        },
    "MuMu_C":{
        "era": "2017",
        "subera": "C",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 49636525,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_C*_2017_v2.root",},
        },
    "MuMu_D":{
        "era": "2017",
        "subera": "D",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 23075733,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_D*_2017_v2.root",},
        },
    "MuMu_E":{
        "era": "2017",
        "subera": "E",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 51589091,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_E*_2017_v2.root",},
        },
    "MuMu_F":{
        "era": "2017",
        "subera": "F",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 79756560,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_F*_2017_v2.root",},
        },
    "ElEl_B":{
        "era": "2017",
        "subera": "B",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 58088760,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_B*_2017_v2.root",},
        },
    "ElEl_C":{
        "era": "2017",
        "subera": "C",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 65181125,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_C*_2017_v2.root",},
        },
    "ElEl_D":{
        "era": "2017",
        "subera": "D",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 25911432,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_D*_2017_v2.root",},
        },
    "ElEl_E":{
        "era": "2017",
        "subera": "E",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 56233597,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_E*_2017_v2.root",},
        },
    "ElEl_F":{
        "era": "2017",
        "subera": "F",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 74307066,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_F*_2017_v2.root",},
        },
    "Mu_B":{
        "era": "2017",
        "subera": "B",
        "channel": "Mu",
        "isData": True,
        "nEvents": 136300266,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_B*_2017_v2.root",},
        },
    "Mu_C":{
        "era": "2017",
        "subera": "C",
        "channel": "Mu",
        "isData": True,
        "nEvents": 165652756,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_C*_2017_v2.root",},
        },
    "Mu_D":{
        "era": "2017",
        "subera": "D",
        "channel": "Mu",
        "isData": True,
        "nEvents": 70361660,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_D*_2017_v2.root",},
        },
    "Mu_E":{
        "era": "2017",
        "subera": "E",
        "channel": "Mu",
        "isData": True,
        "nEvents": 154630534,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_E*_2017_v2.root",},
        },
    "Mu_F":{
        "era": "2017",
        "subera": "F",
        "channel": "Mu",
        "isData": True,
        "nEvents": 242135500,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_F*_2017_v2.root",},
        },
    "El_B":{
        "era": "2017",
        "subera": "B",
        "channel": "El",
        "isData": True,
        "nEvents": 60537490,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_B*_2017_v2.root",},
        },
    "El_C":{
        "era": "2017",
        "subera": "C",
        "channel": "El",
        "isData": True,
        "nEvents": 136637888,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_C*_2017_v2.root",},
        },
    "El_D":{
        "era": "2017",
        "subera": "D",
        "channel": "El",
        "isData": True,
        "nEvents": 51526710,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_D*_2017_v2.root",},
        },
    "El_E":{
        "era": "2017",
        "subera": "E",
        "channel": "El",
        "isData": True,
        "nEvents": 102121689,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_E*_2017_v2.root",},
        },
    "El_F":{
        "era": "2017",
        "subera": "F",
        "channel": "El",
        "isData": True,
        "nEvents": 128467223,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_F*_2017_v2.root",},
    },
}
bookerV2UNSTITCHED = {
    "tt_SL-UNSTITCHED":{
        "era": "2017",
        "isData": False,
        "nEvents": 20122010,
        "nEventsPositive": 20040607,
        "nEventsNegative": 81403,
        "sumWeights": 6052480345.748356,
        "sumWeights2": 1850350248120.376221,
        "isSignal": False,
        "doFilter": True,
        "crossSection": 366.2073,
        "color": leg_dict["ttbar"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_SL-NOM_2017_v2.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_SL-NOM_2017_v2.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_SL-NOM_2017_v2.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_SL/$SYSTEMATIC",
    },  
    "tt_DL-UNSTITCHED":{
        "era": "2017",
        "isData": False,
        "nEvents": 69098644,
        "nEventsPositive": 68818780,
        "nEventsNegative": 279864,
        "sumWeights": 4980769113.241218,
        "sumWeights2": 364913493679.955078,
        "isSignal": False,
        "doFilter": True,
        "crossSection": 89.0482,
        "color": leg_dict["ttbar"],
        "source": {"LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-*_2017_v2.root",
                   "LJMLogic/ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_DL-NOM-*_2017_v2.root",
                   "LJMLogic/MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_DL-NOM-*_2017_v2.root",
                   "LJMLogic/ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_DL-NOM-*_2017_v2.root",
                  },
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-1_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-2_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-3_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-4_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-5_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-6_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-7_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-8_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-9_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-10_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-11_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-12_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-13_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-14_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_DL/$SYSTEMATIC",
    },
}
ttbooker = {
    "tt_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 69098644,
        "nEventsPositive": 68818780,
        "nEventsNegative": 279864,
        "sumWeights": 4980769113.241218,
        "sumWeights2": 364913493679.955078,
        "isSignal": False,
        "crossSection": 89.0482,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_DL_2017_PUFix.root",},
        },
}
ttttbooker = {
    "tttt":{
        "era": "2017",
        "isData": False,
        "nEvents": 2273928,
        "nEventsPositive": 1561946,
        "nEventsNegative": 711982,
        "sumWeights": 18645.487772,
        "sumWeights2": 1094.209551,
        "isSignal": True,
        "crossSection": 0.012,
        "color": leg_dict["tttt"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tttt_2017_PUFix.root",},
        },
}
microbooker = {
    "tttt":{
        "era": "2017",
        "isData": False,
        "nEvents": 2273928,
        "nEventsPositive": 1561946,
        "nEventsNegative": 711982,
        "sumWeights": 18645.487772,
        "sumWeights2": 1094.209551,
        "isSignal": True,
        "crossSection": 0.012,
        "color": leg_dict["tttt"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tttt_2017_PUFix.root",},
        },
    "tt_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 69098644,
        "nEventsPositive": 68818780,
        "nEventsNegative": 279864,
        "sumWeights": 4980769113.241218,
        "sumWeights2": 364913493679.955078,
        "isSignal": False,
        "crossSection": 89.0482,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_DL_2017_PUFix.root",},
        },
    "ST_tW":{
        "era": "2017",
        "isData": False,
        "nEvents": 7945242,
        "nEventsPositive": 7914815,
        "nEventsNegative": 30427,
        "sumWeights": 277241050.840222,
        "sumWeights2": 9823995766.508368,
        "isSignal": False,
        "crossSection": 35.8,
        "color": leg_dict["singletop"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ST_tW_2017_PUFix.root",},
        },
}
theOriginal = {
    "tttt_orig":{
        "era": "2017",
        "isData": False,
        "nEvents": 2273928,
        "nEventsPositive": 1561946,
        "nEventsNegative": 711982,
        "sumWeights": 18645.487772,
        "sumWeights2": 1094.209551,
        "isSignal": False,
        "crossSection": 0.012,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tttt-orig_2.root",},
        },
}
pyrdfbooker = {
    "tt_DL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8510388,
        "nEventsPositive": 8467543,
        "nEventsNegative": 42845,
        "sumWeights": 612101836.284397,
        "sumWeights2": 44925503249.097206,
        "isSignal": False,
        "crossSection": 1.4705,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_DL-GF-*_2017_PUFix.root",},
        },
}
booker = {
    "tttt":{
        "era": "2017",
        "isData": False,
        "nEvents": 2273928,
        "nEventsPositive": 1561946,
        "nEventsNegative": 711982,
        "sumWeights": 18645.487772,
        "sumWeights2": 1094.209551,
        "isSignal": True,
        "crossSection": 0.012,
        "color": leg_dict["tttt"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tttt_2017_PUFix.root",},
        },
    "tt_SL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8836856,
        "nEventsPositive": 8794464,
        "nEventsNegative": 42392,
        "sumWeights": 2653328498.476976,
        "sumWeights2": 812201885978.209229,
        "isSignal": False,
        "crossSection": 6,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_SL-GF_2017_PUFix.root",},
        },
    "tt_DL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8510388,
        "nEventsPositive": 8467543,
        "nEventsNegative": 42845,
        "sumWeights": 612101836.284397,
        "sumWeights2": 44925503249.097206,
        "isSignal": False,
        "crossSection": 1.4705,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_DL-GF-*_2017_PUFix.root",},
        },
    "tt_SL":{
        "era": "2017",
        "isData": False,
        "nEvents": 20122010,
        "nEventsPositive": 20040607,
        "nEventsNegative": 81403,
        "sumWeights": 6052480345.748356,
        "sumWeights2": 1850350248120.376221,
        "isSignal": False,
        "crossSection": 366.2073,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_SL_2017_PUFix.root",},
        },
    "tt_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 69098644,
        "nEventsPositive": 68818780,
        "nEventsNegative": 279864,
        "sumWeights": 4980769113.241218,
        "sumWeights2": 364913493679.955078,
        "isSignal": False,
        "crossSection": 89.0482,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_DL_2017_PUFix.root",},
        },
    "ST_tW":{
        "era": "2017",
        "isData": False,
        "nEvents": 7945242,
        "nEventsPositive": 7914815,
        "nEventsNegative": 30427,
        "sumWeights": 277241050.840222,
        "sumWeights2": 9823995766.508368,
        "isSignal": False,
        "crossSection": 35.8,
        "color": leg_dict["singletop"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ST_tW_2017_PUFix.root",},
        },
    "ST_tbarW":{
        "era": "2017",
        "isData": False,
        "nEvents": 7745276,
        "nEventsPositive": 7715654,
        "nEventsNegative": 30427,
        "sumWeights": 270762750.172525,
        "sumWeights2": 9611964941.797768,
        "isSignal": False,
        "crossSection": 35.8,
        "color": leg_dict["singletop"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ST_tbarW_2017_PUFix.root",},
        },
    "ttH":{
        "era": "2017",
        "isData": False,
        "nEvents": 8000000,
        "nEventsPositive": 7916867,
        "nEventsNegative": 83133,
        "sumWeights": 4216319.315884,
        "sumWeights2": 2317497.816608,
        "isSignal": False,
        "crossSection": 0.2934,
        "color": leg_dict["ttH"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ttH_2017_PUFix.root",},
        },
    "ttWJets":{
        "era": "2017",
        "isData": False,
        "nEvents": 9425384,
        "nEventsPositive": 9404856,
        "nEventsNegative": 20528,
        "sumWeights": 9384328.000000,
        "sumWeights2": 9425384.000000,
        "isSignal": False,
        "crossSection": 0.611,
        "color": leg_dict["ttVJets"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ttWJets_2017_PUFix.root",},
        },
    "ttZJets":{
        "era": "2017",
        "isData": False,
        "nEvents": 8536618,
        "nEventsPositive": 8527846,
        "nEventsNegative": 8772,
        "sumWeights": 8519074.000000,
        "sumWeights2": 8536618.000000,
        "isSignal": False,
        "crossSection": 0.783,
        "color": leg_dict["ttVJets"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ttZJets_2017_PUFix.root",},
        },
    "ttWH":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199491,
        "nEventsNegative": 509,
        "sumWeights": 198839.680865,
        "sumWeights2": 199704.039588,
        "isSignal": False,
        "crossSection": 0.001572,
        "color": leg_dict["ttultrarare"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ttWH_2017_PUFix.root",},
        },
    "ttWW":{
        "era": "2017",
        "isData": False,
        "nEvents": 962000,
        "nEventsPositive": 962000,
        "nEventsNegative": 0,
        "sumWeights": 962000.000000,
        "sumWeights2": 962000.000000,
        "isSignal": False,
        "crossSection": 0.007882,
        "color": leg_dict["ttultrarare"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ttWW_2017_PUFix.root",},
        },
    "ttWZ":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199379,
        "nEventsNegative": 621,
        "sumWeights": 198625.183551,
        "sumWeights2": 199708.972601,
        "isSignal": False,
        "crossSection": 0.002974,
        "color": leg_dict["ttultrarare"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ttWZ_2017_PUFix.root",},
        },
    "ttZZ":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199686,
        "nEventsNegative": 314,
        "sumWeights": 199286.628891,
        "sumWeights2": 199816.306332,
        "isSignal": False,
        "crossSection": 0.001572,
        "color": leg_dict["ttultrarare"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ttZZ_2017_PUFix.root",},
        },
    "ttZH":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199643,
        "nEventsNegative": 357,
        "sumWeights": 199192.234990,
        "sumWeights2": 199794.753976,
        "isSignal": False,
        "crossSection": 0.01253,
        "color": leg_dict["ttultrarare"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ttZH_2017_PUFix.root",},
        },
    "ttHH":{
        "era": "2017",
        "isData": False,
        "nEvents": 194817,
        "nEventsPositive": 194516,
        "nEventsNegative": 301,
        "sumWeights": 194116.909912,
        "sumWeights2": 194611.090542,
        "isSignal": False,
        "crossSection": 0.0007408,
        "color": leg_dict["ttultrarare"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ttHH_2017_PUFix.root",},
        },
    "tttW":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199852,
        "nEventsNegative": 148,
        "sumWeights": 199552.187377,
        "sumWeights2": 199697.648421,
        "isSignal": False,
        "crossSection": 0.007882,
        "color": leg_dict["ttultrarare"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tttW_2017_PUFix.root",},
        },
    "tttJ":{
        "era": "2017",
        "isData": False,
        "nEvents": 200000,
        "nEventsPositive": 199273,
        "nEventsNegative": 727,
        "sumWeights": 198394.878491,
        "sumWeights2": 199663.384954,
        "isSignal": False,
        "crossSection": 0.0004741,
        "color": leg_dict["ttultrarare"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tttJ_2017_PUFix.root",},
        },
    "DYJets_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 49125561,
        "nEventsPositive": 49103859,
        "nEventsNegative": 21702,
        "sumWeights": 49082157.000000,
        "sumWeights2": 49125561.000000,
        "isSignal": False,
        "crossSection": 5075.6,
        "color": leg_dict["DY"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/DYJets_DL_2017_PUFix.root",},
        },
    "ElMu_B":{
        "era": "2017",
        "subera": "B",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 4453465,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElMu_B_2017.root",},
        },
    "ElMu_C":{
        "era": "2017",
        "subera": "C",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 15595214,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElMu_C_2017.root",},
        },
    "ElMu_D":{
        "era": "2017",
        "subera": "D",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 9164365,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElMu_D_2017.root",},
        },
    "ElMu_E":{
        "era": "2017",
        "subera": "E",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 19043421,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElMu_E_2017.root",},
        },
    "ElMu_F":{
        "era": "2017",
        "subera": "F",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 25776363,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElMu_F_2017.root",},
        },
}
cutout = {
    "MuMu_B":{
        "era": "2017",
        "subera": "B",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 14501767,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/MuMu_B_2017.root",},
        },
    "MuMu_C":{
        "era": "2017",
        "subera": "C",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 49636525,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/MuMu_C_2017.root",},
        },
    "MuMu_D":{
        "era": "2017",
        "subera": "D",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 23075733,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/MuMu_D_2017.root",},
        },
    "MuMu_E":{
        "era": "2017",
        "subera": "E",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 51589091,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/MuMu_E_2017.root",},
        },
    "MuMu_F":{
        "era": "2017",
        "subera": "F",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 79756560,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/MuMu_F_2017.root",},
        },
    "ElEl_B":{
        "era": "2017",
        "subera": "B",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 58088760,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElEl_B_2017.root",},
        },
    "ElEl_C":{
        "era": "2017",
        "subera": "C",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 65181125,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElEl_C_2017.root",},
        },
    "ElEl_D":{
        "era": "2017",
        "subera": "D",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 25911432,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElEl_D_2017.root",},
        },
    "ElEl_E":{
        "era": "2017",
        "subera": "E",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 56233597,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElEl_E_2017.root",},
        },
    "ElEl_F":{
        "era": "2017",
        "subera": "F",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 74307066,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElEl_F_2017.root",},
        },
    "Mu_B":{
        "era": "2017",
        "subera": "B",
        "channel": "Mu",
        "isData": True,
        "nEvents": 136300266,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/Mu_B_2017.root",},
        },
    "Mu_C":{
        "era": "2017",
        "subera": "C",
        "channel": "Mu",
        "isData": True,
        "nEvents": 165652756,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/Mu_C_2017.root",},
        },
    "Mu_D":{
        "era": "2017",
        "subera": "D",
        "channel": "Mu",
        "isData": True,
        "nEvents": 70361660,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/Mu_D_2017.root",},
        },
    "Mu_E":{
        "era": "2017",
        "subera": "E",
        "channel": "Mu",
        "isData": True,
        "nEvents": 154630534,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/Mu_E_2017.root",},
        },
    "Mu_F":{
        "era": "2017",
        "subera": "F",
        "channel": "Mu",
        "isData": True,
        "nEvents": 242135500,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/Mu_F_2017.root",},
        },
    "El_B":{
        "era": "2017",
        "subera": "B",
        "channel": "El",
        "isData": True,
        "nEvents": 60537490,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/El_B_2017.root",},
        },
    "El_C":{
        "era": "2017",
        "subera": "C",
        "channel": "El",
        "isData": True,
        "nEvents": 136637888,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/El_C_2017.root",},
        },
    "El_D":{
        "era": "2017",
        "subera": "D",
        "channel": "El",
        "isData": True,
        "nEvents": 51526710,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/El_D_2017.root",},
        },
    "El_E":{
        "era": "2017",
        "subera": "E",
        "channel": "El",
        "isData": True,
        "nEvents": 102121689,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/El_E_2017.root",},
        },
    "El_F":{
        "era": "2017",
        "subera": "F",
        "channel": "El",
        "isData": True,
        "nEvents": 128467223,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/El_F_2017.root",},
        },
    }
minibooker = {
    "tttt":{
        "era": "2017",
        "isData": False,
        "nEvents": 2273928,
        "nEventsPositive": 1561946,
        "nEventsNegative": 711982,
        "sumWeights": 18645.487772,
        "sumWeights2": 1094.209551,
        "isSignal": True,
        "crossSection": 0.012,
        "color": leg_dict["tttt"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tttt_2017_PUFix.root",},
        },
    "tt_SL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8836856,
        "nEventsPositive": 8794464,
        "nEventsNegative": 42392,
        "sumWeights": 2653328498.476976,
        "sumWeights2": 812201885978.209229,
        "isSignal": False,
        "crossSection": 6,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_SL-GF_2017_PUFix.root",},
        },
    "tt_DL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8510388,
        "nEventsPositive": 8467543,
        "nEventsNegative": 42845,
        "sumWeights": 612101836.284397,
        "sumWeights2": 44925503249.097206,
        "isSignal": False,
        "crossSection": 1.4705,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_DL-GF-*_2017_PUFix.root",},
        },
    "tt_SL":{
        "era": "2017",
        "isData": False,
        "nEvents": 20122010,
        "nEventsPositive": 20040607,
        "nEventsNegative": 81403,
        "sumWeights": 6052480345.748356,
        "sumWeights2": 1850350248120.376221,
        "isSignal": False,
        "crossSection": 366.2073,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_SL_2017_PUFix.root",},
        },
    "tt_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 69098644,
        "nEventsPositive": 68818780,
        "nEventsNegative": 279864,
        "sumWeights": 4980769113.241218,
        "sumWeights2": 364913493679.955078,
        "isSignal": False,
        "crossSection": 89.0482,
        "color": leg_dict["ttbar"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tt_DL_2017_PUFix.root",},
        },
    "ST_tW":{
        "era": "2017",
        "isData": False,
        "nEvents": 7945242,
        "nEventsPositive": 7914815,
        "nEventsNegative": 30427,
        "sumWeights": 277241050.840222,
        "sumWeights2": 9823995766.508368,
        "isSignal": False,
        "crossSection": 35.8,
        "color": leg_dict["singletop"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ST_tW_2017_PUFix.root",},
        },
    "ST_tbarW":{
        "era": "2017",
        "isData": False,
        "nEvents": 7745276,
        "nEventsPositive": 7715654,
        "nEventsNegative": 30427,
        "sumWeights": 270762750.172525,
        "sumWeights2": 9611964941.797768,
        "isSignal": False,
        "crossSection": 35.8,
        "color": leg_dict["singletop"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ST_tbarW_2017_PUFix.root",},
        },

    "DYJets_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 49125561,
        "nEventsPositive": 49103859,
        "nEventsNegative": 21702,
        "sumWeights": 49082157.000000,
        "sumWeights2": 49125561.000000,
        "isSignal": False,
        "crossSection": 5075.6,
        "color": leg_dict["DY"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/DYJets_DL_2017_PUFix.root",},
        },
    "MuMu":{
        "era": "2017",
        "subera": "B",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 14501767 + 49636525 + 23075733 + 51589091 + 79756560,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/MuMu_*_2017.root",},
        },
    "ElEl":{
        "era": "2017",
        "subera": "B",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 58088760 + 65181125 + 25911432 + 56233597 + 74307066,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElEl_*_2017.root",},
        },
    "ElMu":{
        "era": "2017",
        "subera": "B",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 4453465 + 15595214 + 9164365 + 19043421 + 25776363,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/ElMu_*_2017.root",},
        },
    "Mu":{
        "era": "2017",
        "subera": "B",
        "channel": "Mu",
        "isData": True,
        "nEvents": 136300266 + 165652756 + 70361660 + 154630534 + 242135500,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/Mu_*_2017.root",},
        },
    "El":{
        "era": "2017",
        "subera": "B",
        "channel": "El",
        "isData": True,
        "nEvents": 60537490 + 136637888 + 51526710 + 102121689 + 128467223,
        "color": leg_dict["Data"],
        "source": {"Unknown": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/El_*_2017.root",},
        },
    }

#Set up channel bits for selection and baseline. Separation not necessary in this stage, but convenient for loops
Chan = {}
Chan["ElMu_selection"] = 24576
Chan["MuMu_selection"] = 6144
Chan["ElEl_selection"] = 512
Chan["Mu_selection"] = 128
Chan["El_selection"] = 64
Chan["selection"] = Chan["ElMu_selection"] + Chan["MuMu_selection"] + Chan["ElEl_selection"] + Chan["Mu_selection"] + Chan["El_selection"]
Chan["ElMu_baseline"] = 24576
Chan["MuMu_baseline"] = 6144
Chan["ElEl_baseline"] = 512
Chan["Mu_baseline"] = 128
Chan["El_baseline"] = 64
Chan["baseline"] = Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"] + Chan["Mu_baseline"] + Chan["El_baseline"]


# In[ ]:


def METXYCorr(input_df, run_branch = "run", era = "2017", isData = True, npv_branch = "PV_npvs",
               sysVariations={"$NOMINAL": {"jet_mask": "jet_mask", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt",
                                             "jet_mass_var": "Jet_mass",
                                             "met_pt_var": "METFixEE2017_pt",
                                             "met_phi_var": "METFixEE2017_phi",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                              "_jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt_jesTotalUp",
                                             "jet_mass_var": "Jet_mass_jesTotalUp",
                                             "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                             "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                              "_jesTotalDown": {"jet_mask": "jet_mask_jesTotalDown", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt_jesTotalDown",
                                             "jet_mass_var": "Jet_mass_jesTotalDown",
                                             "met_pt_var": "METFixEE2017_pt_jesTotalDown",
                                             "met_phi_var": "METFixEE2017_phi_jesTotalDown",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                                     },
                       verbose=False):
    rdf = input_df
    listOfDefinedColumns = input_df.GetColumnNames()
    z = []
    for sysVar, sysDict in sysVariations.items():
        #skip systematic variations on data, only do the nominal
        if isData and sysVar != "$NOMINAL": 
            continue
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        if isWeightVariation == True: continue
        metPt = sysDict.get("met_pt_var")
        metPhi = sysDict.get("met_phi_var")
        metDoublet = "MET_xycorr_doublet{pf}".format(pf=sysVar.replace("$NOMINAL", "_nom"))
        metPtName = "FTAMET{pf}_pt".format(pf=sysVar.replace("$NOMINAL", "_nom"))
        metPhiName = "FTAMET{pf}_phi".format(pf=sysVar.replace("$NOMINAL", "_nom"))
        #XY correctors takes the: uncorrected pt and phi, run branch, year, C++ true/false for isData, and PV branch
        def_fnc = "FTA::METXYCorr({mpt}, {mph}, {run}, {era}, {isData}, {pv})".format(mpt=metPt,
                                                                        mph=metPhi,
                                                                        run=run_branch,
                                                                        era=era,
                                                                        isData=str(isData).lower(),
                                                                        pv=npv_branch
                                                                        )
        #append the definitions to the list in the order required
        z.append((metDoublet, def_fnc))
        z.append((metPtName, "{}.first".format(metDoublet)))
        z.append((metPhiName, "{}.second".format(metDoublet)))

    for defName, defFunc in z:
        if defName in listOfDefinedColumns:
            if verbose:
                print("{} already defined, skipping".format(defName))
            continue
        else:
            if verbose:
                print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
            rdf = rdf.Define(defName, defFunc)
            listOfDefinedColumns.push_back(defName)
    return rdf
        #if metDoublet not in listOfDefinedColumns:
            #if verbose: 
            #    print("Doing MET XY correction:\nrdf = rdf.Define(\"{0}\", \"{1}\")".format(metDoublet, def_fnc))
            #rdf = rdf.Define(metDoublet, def_fnc)
            #listOfDefinedColumns.push_back(metDoublet)
        #if metPt not in listOfDefinedColumns and metPhi not in listOfDefinedColumns:
            #if verbose: 
            #    print("rdf = rdf.Define(\"{0}\", \"{1}\")".format(metPt, metDoublet))
            #    print("rdf = rdf.Define(\"{0}\", \"{1}\")".format(metPhi, metDoublet))
            #rdf = rdf.Define(metPt, "{}.first".format(metDoublet))
            #rdf = rdf.Define(metPhi, "{}.second".format(metDoublet))
            #listOfDefinedColumns.push_back(metPt)
            #listOfDefinedColumns.push_back(metPhi)
    #return rdf


# In[ ]:


def defineLeptons(input_df, input_lvl_filter=None, isData=True, useBackupChannel=False, verbose=False,
                 sysVariations={"$NOMINAL": {"jet_mask": "jet_mask", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt",
                                             "jet_mass_var": "Jet_mass",
                                             "met_pt_var": "METFixEE2017_pt",
                                             "met_phi_var": "METFixEE2017_phi",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                              "_jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt_jesTotalUp",
                                             "jet_mass_var": "Jet_mass_jesTotalUp",
                                             "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                             "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                              "_jesTotalDown": {"jet_mask": "jet_mask_jesTotalDown", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt_jesTotalDown",
                                             "jet_mass_var": "Jet_mass_jesTotalDown",
                                             "met_pt_var": "METFixEE2017_pt_jesTotalDown",
                                             "met_phi_var": "METFixEE2017_phi_jesTotalDown",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                                },
                 ):
    """Function to take in a dataframe and return one with new columns defined,
    plus event filtering based on the criteria defined inside the function"""
        
    #Set up channel bits for selection and baseline. Separation not necessary in this stage, but convenient for loops
    Chan = {}
    Chan["ElMu_selection"] = 24576
    Chan["MuMu_selection"] = 6144
    Chan["ElEl_selection"] = 512
    Chan["Mu_selection"] = 128
    Chan["El_selection"] = 64
    Chan["selection"] = Chan["ElMu_selection"] + Chan["MuMu_selection"] + Chan["ElEl_selection"] + Chan["Mu_selection"] + Chan["El_selection"]
    Chan["ElMu_baseline"] = 24576
    Chan["MuMu_baseline"] = 6144
    Chan["ElEl_baseline"] = 512
    Chan["Mu_baseline"] = 128
    Chan["El_baseline"] = 64
    Chan["baseline"] = Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"] + Chan["Mu_baseline"] + Chan["El_baseline"]
    b = {}
    b["baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) > 0".format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + 
                                                                            Chan["ElEl_baseline"] + Chan["Mu_baseline"] + Chan["El_baseline"])
    
    b["ElMu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) > 0".format(Chan["ElMu_baseline"])
    b["MuMu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0".format(Chan["ElMu_baseline"], 
                                                                                                                                Chan["MuMu_baseline"])
    b["ElEl_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0".format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"], 
                                                                                                                                Chan["ElEl_baseline"])
    b["Mu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0".format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"], Chan["Mu_baseline"])
    b["El_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0".format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + 
                                                                                                                    Chan["ElEl_baseline"] + Chan["Mu_baseline"], Chan["El_baseline"])
    b["selection"] = "ESV_TriggerAndLeptonLogic_selection > 0"
    b["ElMu_selection"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) > 0".format(Chan["ElMu_selection"])
    b["MuMu_selection"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0".format(Chan["ElMu_selection"], Chan["MuMu_selection"])
    b["ElEl_selection"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0".format(Chan["ElMu_selection"] + Chan["MuMu_selection"], Chan["ElEl_selection"])
    b["Mu_selection"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0".format(Chan["ElMu_selection"] + Chan["MuMu_selection"] + Chan["ElEl_selection"], Chan["Mu_selection"])
    b["El_selection"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0".format(Chan["ElMu_selection"] + Chan["MuMu_selection"] + Chan["ElEl_selection"]
                                                                                                                                 + Chan["Mu_selection"], Chan["El_selection"])
    if input_lvl_filter == None:
        rdf = input_df                .Define("mu_mask", "Muon_pt > 0").Define("e_mask", "Electron_pt > 0")
    else:
        if "baseline" in input_lvl_filter:
            lvl_type = "baseline"
        elif "selection" in input_lvl_filter:
            lvl_type = "selection"
        else:
            raise RuntimeError("No such level permissable: must contain 'selection' or 'baseline'")
        rdf_input = input_df.Filter(b[input_lvl_filter], input_lvl_filter)
        rdf = rdf_input
        rdf = rdf.Define("mu_mask", "(Muon_OSV_{0} & {1}) > 0".format(lvl_type, Chan[input_lvl_filter]))
        rdf = rdf.Define("e_mask", "(Electron_OSV_{0} & {1}) > 0".format(lvl_type, Chan[input_lvl_filter]))
    transverseMassCode = '''auto MT2 = {m1}*{m1} + {m2}*{m2} + 2*(sqrt({m1}*{m1} + {pt1}*{pt1})*sqrt({m2}*{m2} + {pt2}*{pt2}) - {pt1}*{pt2}*cos(ROOT::VecOps::DeltaPhi({phi1}, {phi2})));
                         return sqrt(MT2);'''
    transverseMassCodeChannelSafe = '''
                         if( {pt1}.size() != {pt2}.size()){{ROOT::VecOps::RVec<float> v; v.push_back(-9999); return v;}}
                         else {{auto MT2 = {m1}*{m1} + {m2}*{m2} + 2*(sqrt({m1}*{m1} + {pt1}*{pt1})*sqrt({m2}*{m2} + {pt2}*{pt2}) - {pt1}*{pt2}*cos(ROOT::VecOps::DeltaPhi({phi1}, {phi2})));
                         return sqrt(MT2);
                         }}'''
    transverseMassCodeChecker = '''auto V1 = ROOT::Math::PtEtaPhiMVector({pt1}, {eta1}, {phi1}, {m1});
                                auto V2 = ROOT::Math::PtEtaPhiMVector({pt2}, {eta2}, {phi2}, {m2});
                                auto V = V1 + V2;
                                return V.Mt();'''
    transverseMassLightCode = '''auto MT2 = 2*{pt1}*{pt2}*(1 - cos(ROOT::VecOps::DeltaPhi({phi1}, {phi2})));
                              return sqrt(MT2);'''
    z = []
    #only valid postfix for leptons, excluding calculations involving MET, is "_nom"
    leppostfix = "_nom"
    
    #MUONS
    z.append(("Muon_idx", "FTA::generateIndices(Muon_pt);"))
    z.append(("nFTAMuon{lpf}".format(lpf=leppostfix), "Muon_pt[mu_mask].size()"))
    z.append(("FTAMuon{lpf}_idx".format(lpf=leppostfix), "Muon_idx[mu_mask]"))
    z.append(("FTAMuon{lpf}_pfIsoId".format(lpf=leppostfix), "Muon_pfIsoId[mu_mask]"))
    z.append(("FTAMuon{lpf}_looseId".format(lpf=leppostfix), "Muon_looseId[mu_mask]"))
    z.append(("FTAMuon{lpf}_pt".format(lpf=leppostfix), "Muon_pt[mu_mask]"))
    z.append(("FTAMuon{lpf}_eta".format(lpf=leppostfix), "Muon_eta[mu_mask]"))
    z.append(("FTAMuon{lpf}_phi".format(lpf=leppostfix), "Muon_phi[mu_mask]"))
    z.append(("FTAMuon{lpf}_mass".format(lpf=leppostfix), "Muon_mass[mu_mask]"))
    z.append(("FTAMuon{lpf}_charge".format(lpf=leppostfix), "Muon_charge[mu_mask]"))
    z.append(("FTAMuon{lpf}_dz".format(lpf=leppostfix), "Muon_dz[mu_mask]"))
    z.append(("FTAMuon{lpf}_dxy".format(lpf=leppostfix), "Muon_dxy[mu_mask]"))
    z.append(("FTAMuon{lpf}_d0".format(lpf=leppostfix), "sqrt(Muon_dz*Muon_dz + Muon_dxy*Muon_dxy)[mu_mask]"))
    z.append(("FTAMuon{lpf}_ip3d".format(lpf=leppostfix), "Muon_ip3d[mu_mask]"))
    z.append(("FTAMuon{lpf}_pfRelIso03_all".format(lpf=leppostfix), "Muon_pfRelIso03_all[mu_mask]"))
    z.append(("FTAMuon{lpf}_pfRelIso03_chg".format(lpf=leppostfix), "Muon_pfRelIso03_chg[mu_mask]"))
    z.append(("FTAMuon{lpf}_pfRelIso04_all".format(lpf=leppostfix), "Muon_pfRelIso04_all[mu_mask]"))
    z.append(("FTAMuon{lpf}_jetIdx".format(lpf=leppostfix), "Muon_jetIdx[mu_mask]"))
    #z.append(("METofMETandMu2", ) #FIXME: switch to MET_xycorr_pt{}
    z.append(("nFTAMuon{lpf}".format(lpf=leppostfix), "Muon{pf}_pt.size()"))
    z.append(("nLooseFTAMuon{lpf}".format(lpf=leppostfix), "Muon_looseId[mu_mask && Muon_looseId == true].size()"))
    z.append(("nMediumFTAMuon{lpf}".format(lpf=leppostfix), "Muon_mediumId[mu_mask && Muon_mediumId == true].size()"))
    z.append(("nTightFTAMuon{lpf}".format(lpf=leppostfix), "Muon_tightId[mu_mask && Muon_tightId == true].size()"))
    z.append(("FTAMuon{lpf}_InvariantMass".format(lpf=leppostfix), "nFTAMuon{lpf} == 2 ? InvariantMass(FTAMuon{lpf}_pt, FTAMuon{lpf}_eta, FTAMuon{lpf}_phi, FTAMuon{lpf}_mass) : -0.1".format(lpf=leppostfix)))    
    if isData == False:
        z.append(("FTAMuon{lpf}_SF_ID_nom".format(lpf=leppostfix), "Muon_SF_ID_nom[mu_mask]"))
        z.append(("FTAMuon{lpf}_SF_ID_stat".format(lpf=leppostfix), "Muon_SF_ID_stat[mu_mask]"))
        z.append(("FTAMuon{lpf}_SF_ID_syst".format(lpf=leppostfix), "Muon_SF_ID_syst[mu_mask]"))
        z.append(("FTAMuon{lpf}_SF_ISO_nom".format(lpf=leppostfix), "Muon_SF_ISO_nom[mu_mask]"))
        z.append(("FTAMuon{lpf}_SF_ISO_stat".format(lpf=leppostfix), "Muon_SF_ISO_stat[mu_mask]"))
        z.append(("FTAMuon{lpf}_SF_ISO_syst".format(lpf=leppostfix), "Muon_SF_ISO_syst[mu_mask]"))
    #ELECTRONS
    z.append(("Electron_idx", "FTA::generateIndices(Electron_pt);"))
    z.append(("nFTAElectron{lpf}".format(lpf=leppostfix), "Electron_pt[e_mask].size()"))
    z.append(("FTAElectron{lpf}_idx".format(lpf=leppostfix), "Electron_idx[e_mask]"))
    z.append(("FTAElectron{lpf}_cutBased".format(lpf=leppostfix), "Electron_cutBased[e_mask]"))
    z.append(("FTAElectron{lpf}_pt".format(lpf=leppostfix), "Electron_pt[e_mask]"))
    z.append(("FTAElectron{lpf}_eta".format(lpf=leppostfix), "Electron_eta[e_mask]"))
    z.append(("FTAElectron{lpf}_phi".format(lpf=leppostfix), "Electron_phi[e_mask]"))
    z.append(("FTAElectron{lpf}_mass".format(lpf=leppostfix), "Electron_mass[e_mask]"))
    z.append(("FTAElectron{lpf}_charge".format(lpf=leppostfix), "Electron_charge[e_mask]"))
    z.append(("FTAElectron{lpf}_dz".format(lpf=leppostfix), "Electron_dz[e_mask]"))
    z.append(("FTAElectron{lpf}_dxy".format(lpf=leppostfix), "Electron_dxy[e_mask]"))
    z.append(("FTAElectron{lpf}_d0".format(lpf=leppostfix), "sqrt(Electron_dz*Electron_dz + Electron_dxy*Electron_dxy)[e_mask]"))
    z.append(("FTAElectron{lpf}_ip3d".format(lpf=leppostfix), "Electron_ip3d[e_mask]"))
    z.append(("FTAElectron{lpf}_pfRelIso03_all".format(lpf=leppostfix), "Electron_pfRelIso03_all[e_mask]"))
    z.append(("FTAElectron{lpf}_pfRelIso03_chg".format(lpf=leppostfix), "Electron_pfRelIso03_chg[e_mask]"))
    z.append(("FTAElectron{lpf}_jetIdx".format(lpf=leppostfix), "Electron_jetIdx[e_mask]"))
    ##FIXME: This code above is broken for some reason, doesn't like it... why?
    z.append(("nLooseFTAElectron{lpf}".format(lpf=leppostfix), "Sum(FTAElectron{lpf}_cutBased >= 2)".format(lpf=leppostfix)))
    z.append(("nMediumFTAElectron{lpf}".format(lpf=leppostfix), "Sum(FTAElectron{lpf}_cutBased >= 3)".format(lpf=leppostfix)))
    z.append(("nTightFTAElectron{lpf}".format(lpf=leppostfix), "Sum(FTAElectron{lpf}_cutBased >= 4)".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_InvariantMass".format(lpf=leppostfix), "nFTAElectron{lpf} == 2 ? InvariantMass(FTAElectron{lpf}_pt, FTAElectron{lpf}_eta, FTAElectron{lpf}_phi, FTAElectron{lpf}_mass) : -0.1".format(lpf=leppostfix)))
    if isData == False:
        z.append(("FTAElectron{lpf}_SF_EFF_nom".format(lpf=leppostfix), "Electron_SF_EFF_nom[e_mask]"))
        z.append(("FTAElectron{lpf}_SF_EFF_unc".format(lpf=leppostfix), "Electron_SF_EFF_unc[e_mask]"))
        z.append(("FTAElectron{lpf}_SF_ID_nom".format(lpf=leppostfix), "Electron_SF_ID_nom[e_mask]"))
        z.append(("FTAElectron{lpf}_SF_ID_unc".format(lpf=leppostfix), "Electron_SF_ID_unc[e_mask]"))
    #LEPTONS
    z.append(("nLooseFTALepton{lpf}".format(lpf=leppostfix), "nLooseFTAMuon{lpf} + nLooseFTAElectron{lpf}".format(lpf=leppostfix)))
    z.append(("nMediumFTALepton{lpf}".format(lpf=leppostfix), "nMediumFTAMuon{lpf} + nMediumFTAElectron{lpf}".format(lpf=leppostfix)))
    z.append(("nTightFTALepton{lpf}".format(lpf=leppostfix), "nTightFTAMuon{lpf} + nTightFTAElectron{lpf}".format(lpf=leppostfix)))
    z.append(("nFTALepton{lpf}".format(lpf=leppostfix), "nFTAMuon{lpf} + nFTAElectron{lpf}".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_argsort".format(lpf=leppostfix), "Reverse(Argsort(Concatenate(Muon_pt[mu_mask], Electron_pt[e_mask])))"))
    z.append(("FTALepton{lpf}_pt".format(lpf=leppostfix), "Take(Concatenate(Muon_pt[mu_mask], Electron_pt[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_eta".format(lpf=leppostfix), "Take(Concatenate(Muon_eta[mu_mask], Electron_eta[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_phi".format(lpf=leppostfix), "Take(Concatenate(Muon_phi[mu_mask], Electron_phi[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_jetIdx".format(lpf=leppostfix), "Take(Concatenate(Muon_jetIdx[mu_mask], Electron_jetIdx[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_pdgId".format(lpf=leppostfix), "Take(Concatenate(Muon_pdgId[mu_mask], Electron_pdgId[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_dRll".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? ROOT::VecOps::DeltaR(FTALepton{lpf}_eta.at(0), FTALepton{lpf}_eta.at(1), FTALepton{lpf}_phi.at(0), FTALepton{lpf}_phi.at(1)) : -0.1".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_dPhill".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? ROOT::VecOps::DeltaPhi(FTALepton{lpf}_phi.at(0), FTALepton{lpf}_phi.at(1)) : -999".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_dEtall".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? abs(FTALepton{lpf}_eta.at(0) - FTALepton{lpf}_eta.at(1)) : -999".format(lpf=leppostfix)))
    z.append(("nFTALepton{lpf}".format(lpf=leppostfix), "FTALepton{lpf}_pt.size()".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_pt_LeadLep".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 0 ? FTALepton{lpf}_pt.at(0) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_pt_SubleadLep".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? FTALepton{lpf}_pt.at(1) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_eta_LeadLep".format(lpf=leppostfix), "FTALepton{lpf}_eta.size() > 0 ? FTALepton{lpf}_eta.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_eta_SubleadLep".format(lpf=leppostfix), "FTALepton{lpf}_eta.size() > 1 ? FTALepton{lpf}_eta.at(1) : -0.9999".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_jetIdx_0".format(lpf=leppostfix), "FTALepton{lpf}_jetIdx.size() > 0 ? FTALepton{lpf}_jetIdx.at(0) : -1".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_jetIdx_1".format(lpf=leppostfix), "FTALepton{lpf}_jetIdx.size() > 1 ? FTALepton{lpf}_jetIdx.at(1) : -1".format(lpf=leppostfix)))
    if isData == False:
        z.append(("FTALepton{lpf}_SF_nom".format(lpf=leppostfix), "Take(Concatenate(FTAMuon{lpf}_SF_ID_nom*FTAMuon{lpf}_SF_ISO_nom, FTAElectron{lpf}_SF_ID_nom*FTAElectron{lpf}_SF_EFF_nom), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))

    for sysVar, sysDict in sysVariations.items():
        #skip systematic variations on data, only do the nominal
        if isData and sysVar != "$NOMINAL": 
            continue
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        if isWeightVariation == True: continue
        postfix = sysVar.replace("$NOMINAL", "_nom")
        #metPt = sysDict.get("met_pt_var")
        #metPhi = sysDict.get("met_phi_var")
        #These are the xy corrected MET values, to be used in the calculations
        metPtName = "FTAMET{pf}_pt".format(pf=sysVar.replace("$NOMINAL", "_nom"))
        metPhiName = "FTAMET{pf}_phi".format(pf=sysVar.replace("$NOMINAL", "_nom"))
        z.append(("MTofMETandMu{pf}".format(pf=postfix), 
                         "FTA::transverseMassMET(FTAMuon{lpf}_pt, FTAMuon{lpf}_phi, FTAMuon{lpf}_mass, {mpt}, {mph})".format(lpf=leppostfix, mpt=metPtName, mph=metPhiName)))
        z.append(("MTofMETandEl{pf}".format(pf=postfix),  
                         "FTA::transverseMassMET(FTAElectron{lpf}_pt, FTAElectron{lpf}_phi, FTAElectron{lpf}_mass, {mpt}, {mph})".format(lpf=leppostfix, mpt=metPtName, mph=metPhiName)))
        #There shouldn't be any variation on this quantity, but... easier looping
        z.append(("MTofElandMu{pf}".format(pf=postfix), 
                         "FTA::transverseMass(FTAMuon{lpf}_pt, FTAMuon{lpf}_phi, FTAMuon{lpf}_mass, FTAElectron{lpf}_pt, FTAElectron{lpf}_phi, FTAElectron{lpf}_mass)".format(lpf=leppostfix)))
    
    listOfDefinedColumns = rdf.GetDefinedColumnNames()
    #Add them to the dataframe...
    for defName, defFunc in z:
        if defName in listOfDefinedColumns:
            if verbose:
                print("{} already defined, skipping".format(defName))
            continue
        else:
            if verbose:
                print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
            rdf = rdf.Define(defName, defFunc)
            listOfDefinedColumns.push_back(defName)
    return rdf
    #OLD CODE
    #rdf = rdf.Define("Muon_idx", "FTA::generateIndices(Muon_pt);")
    #rdf = rdf.Define("GMuon_idx", "Muon_idx[mu_mask]")
    #rdf = rdf.Define("GMuon_pfIsoId", "Muon_pfIsoId[mu_mask]")
    #rdf = rdf.Define("GMuon_looseId", "Muon_looseId[mu_mask]")
    #rdf = rdf.Define("GMuon_pt", "Muon_pt[mu_mask]")
    #rdf = rdf.Define("GMuon_eta", "Muon_eta[mu_mask]")
    #rdf = rdf.Define("GMuon_phi", "Muon_phi[mu_mask]")
    #rdf = rdf.Define("GMuon_mass", "Muon_mass[mu_mask]")
    #rdf = rdf.Define("GMuon_charge", "Muon_charge[mu_mask]")
    #rdf = rdf.Define("GMuon_dz", "Muon_dz[mu_mask]")
    #rdf = rdf.Define("GMuon_dxy", "Muon_dxy[mu_mask]")
    #rdf = rdf.Define("GMuon_d0", "sqrt(Muon_dz*Muon_dz + Muon_dxy*Muon_dxy)[mu_mask]")
    #rdf = rdf.Define("GMuon_ip3d", "Muon_ip3d[mu_mask]")
    #rdf = rdf.Define("GMuon_pfRelIso03_all", "Muon_pfRelIso03_all[mu_mask]")
    #rdf = rdf.Define("GMuon_pfRelIso03_chg", "Muon_pfRelIso03_chg[mu_mask]")
    #rdf = rdf.Define("GMuon_pfRelIso04_all", "Muon_pfRelIso04_all[mu_mask]")
    #rdf = rdf.Define("GMuon_jetIdx", "Muon_jetIdx[mu_mask]")
    ##rdf = rdf.Define("METofMETandMu2", ) #FIXME: switch to MET_xycorr_pt{}
    #rdf = rdf.Define("nGMuon", "GMuon_pt.size()")
    #rdf = rdf.Define("nLooseGMuon", "Muon_looseId[mu_mask && Muon_looseId == true].size()")
    #rdf = rdf.Define("nMediumGMuon", "Muon_mediumId[mu_mask && Muon_mediumId == true].size()")
    #rdf = rdf.Define("nTightGMuon", "Muon_tightId[mu_mask && Muon_tightId == true].size()")
    #rdf = rdf.Define("GMuon_InvariantMass", "nGMuon == 2 ? InvariantMass(GMuon_pt, GMuon_eta, GMuon_phi, GMuon_mass) : -0.1")
    #rdf = rdf.Define("Electron_idx", "FTA::generateIndices(Electron_pt);")
    #rdf = rdf.Define("GElectron_idx", "Electron_idx[e_mask]")
    #rdf = rdf.Define("GElectron_cutBased", "Electron_cutBased[e_mask]")
    #rdf = rdf.Define("GElectron_pt", "Electron_pt[e_mask]")
    #rdf = rdf.Define("GElectron_eta", "Electron_eta[e_mask]")
    #rdf = rdf.Define("GElectron_phi", "Electron_phi[e_mask]")
    #rdf = rdf.Define("GElectron_mass", "Electron_mass[e_mask]")
    #rdf = rdf.Define("GElectron_charge", "Electron_charge[e_mask]")
    #rdf = rdf.Define("GElectron_dz", "Electron_dz[e_mask]")
    #rdf = rdf.Define("GElectron_dxy", "Electron_dxy[e_mask]")
    #rdf = rdf.Define("GElectron_d0", "sqrt(Electron_dz*Electron_dz + Electron_dxy*Electron_dxy)[e_mask]")
    #rdf = rdf.Define("GElectron_ip3d", "Electron_ip3d[e_mask]")
    #rdf = rdf.Define("GElectron_pfRelIso03_all", "Electron_pfRelIso03_all[e_mask]")
    #rdf = rdf.Define("GElectron_pfRelIso03_chg", "Electron_pfRelIso03_chg[e_mask]")
    #rdf = rdf.Define("GElectron_jetIdx", "Electron_jetIdx[e_mask]")
    ##FIXME: This code above is broken for some reason, doesn't like it... why?
    #rdf = rdf.Define("nGElectron", "GElectron_pt.size()")
    #rdf = rdf.Define("nLooseGElectron", "Sum(GElectron_cutBased >= 2)")
    #rdf = rdf.Define("nMediumGElectron", "Sum(GElectron_cutBased >= 3)")
    #rdf = rdf.Define("nTightGElectron", "Sum(GElectron_cutBased >= 4)")
        
    #for sysVar, sysDict in sysVariations.items():
    #    #skip systematic variations on data, only do the nominal
    #    if isData and sysVar != "$NOMINAL": 
    #        continue
    #    #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
    #    isWeightVariation = sysDict.get("weightVariation", False)
    #    if isWeightVariation == True: continue
    #    postfix = sysVar.replace("$NOMINAL", "_nom")
    #    metPt = sysDict.get("met_pt_var")
    #    metPhi = sysDict.get("met_phi_var")
    #    metPtName = "MET_xycorr_pt{}".format(sysVar.replace("$NOMINAL", "_nom"))
    #    metPhiName = "MET_xycorr_phi{}".format(sysVar.replace("$NOMINAL", "_nom"))
    #    rdf = rdf.Define()
    #    rdf = rdf.Define("MTofMETandMu{}".format(postfix), 
    #                     "FTA::transverseMassMET(\"GMuon_pt\", \"GMuon_phi\", \"GMuon_mass\", \"{0}\", \"{1}\")".format(metPtName, metPhiName))
    #    rdf = rdf.Define("MTofMETandEl{}".format(postfix),  
    #                     "FTA::transverseMassMET(\"GElectron_pt\", \"GElectron_phi\", \"GElectron_mass\", \"{0}\", \"{1}\")".format(metPtName, metPhiName))
    #    #There shouldn't be any variation on this quantity, but... easier looping
    #    rdf = rdf.Define("MTofElandMu{}".format(postfix), 
    #                     "FTA::transverseMassMET(\"GMuon_pt\", \"GMuon_phi\", \"GMuon_mass\", \"GElectron_pt\", \"GElectron_phi\", \"GElectron_mass\")")
    
    #rdf = rdf.Define("nLooseGLepton", "nLooseGMuon + nLooseGElectron")
    #rdf = rdf.Define("nMediumGLepton", "nMediumGMuon + nMediumGElectron")
    #rdf = rdf.Define("nTightGLepton", "nTightGMuon + nTightGElectron")
    #rdf = rdf.Define("GElectron_InvariantMass", "nGElectron == 2 ? InvariantMass(GElectron_pt, GElectron_eta, GElectron_phi, GElectron_mass) : -0.1")
    #rdf = rdf.Define("GLepton_argsort", "Reverse(Argsort(Concatenate(Muon_pt[mu_mask], Electron_pt[e_mask])))")
    #rdf = rdf.Define("GLepton_pt", "Take(Concatenate(Muon_pt[mu_mask], Electron_pt[e_mask]), GLepton_argsort)")
    #rdf = rdf.Define("GLepton_eta", "Take(Concatenate(Muon_eta[mu_mask], Electron_eta[e_mask]), GLepton_argsort)")
    #rdf = rdf.Define("GLepton_phi", "Take(Concatenate(Muon_phi[mu_mask], Electron_phi[e_mask]), GLepton_argsort)")
    #rdf = rdf.Define("GLepton_jetIdx", "Take(Concatenate(Muon_jetIdx[mu_mask], Electron_jetIdx[e_mask]), GLepton_argsort)")
    #rdf = rdf.Define("GLepton_pdgId", "Take(Concatenate(Muon_pdgId[mu_mask], Electron_pdgId[e_mask]), GLepton_argsort)")
    #rdf = rdf.Define("GLepton_dRll", "GLepton_pt.size() > 1 ? ROOT::VecOps::DeltaR(GLepton_eta.at(0), GLepton_eta.at(1), GLepton_phi.at(0), GLepton_phi.at(1)) : -0.1")
    #rdf = rdf.Define("GLepton_dPhill", "GLepton_pt.size() > 1 ? ROOT::VecOps::DeltaPhi(GLepton_phi.at(0), GLepton_phi.at(1)) : -999")
    #rdf = rdf.Define("GLepton_dEtall", "GLepton_pt.size() > 1 ? abs(GLepton_eta.at(0) - GLepton_eta.at(1)) : -999")
    #rdf = rdf.Define("nGLepton", "GLepton_pt.size()")
    #rdf = rdf.Define("GLepton_pt_LeadLep", "GLepton_pt.size() > 0 ? GLepton_pt.at(0) : -0.000000000001")
    #rdf = rdf.Define("GLepton_pt_SubleadLep", "GLepton_pt.size() > 1 ? GLepton_pt.at(1) : -0.000000000001")
    #rdf = rdf.Define("GLepton_eta_LeadLep", "GLepton_eta.size() > 0 ? GLepton_eta.at(0) : -9999")
    #rdf = rdf.Define("GLepton_eta_SubleadLep", "GLepton_eta.size() > 1 ? GLepton_eta.at(1) : -0.9999")
    #rdf = rdf.Define("GLepton_jetIdx_0", "GLepton_jetIdx.size() > 0 ? GLepton_jetIdx.at(0) : -1")
    #rdf = rdf.Define("GLepton_jetIdx_1", "GLepton_jetIdx.size() > 1 ? GLepton_jetIdx.at(1) : -1")
    #if isData == False:
    #    rdf = rdf.Define("GMuon_SF_ID_nom", "Muon_SF_ID_nom[mu_mask]")
    #    rdf = rdf.Define("GMuon_SF_ID_stat", "Muon_SF_ID_stat[mu_mask]")
    #    rdf = rdf.Define("GMuon_SF_ID_syst", "Muon_SF_ID_syst[mu_mask]")
    #    rdf = rdf.Define("GMuon_SF_ISO_nom", "Muon_SF_ISO_nom[mu_mask]")
    #    rdf = rdf.Define("GMuon_SF_ISO_stat", "Muon_SF_ISO_stat[mu_mask]")
    #    rdf = rdf.Define("GMuon_SF_ISO_syst", "Muon_SF_ISO_syst[mu_mask]")
    #    rdf = rdf.Define("GElectron_SF_EFF_nom", "Electron_SF_EFF_nom[e_mask]")
    #    rdf = rdf.Define("GElectron_SF_EFF_unc", "Electron_SF_EFF_unc[e_mask]")
    #    rdf = rdf.Define("GElectron_SF_ID_nom", "Electron_SF_ID_nom[e_mask]")
    #    rdf = rdf.Define("GElectron_SF_ID_unc", "Electron_SF_ID_unc[e_mask]")
    #    rdf = rdf.Define("GLepton_SF_nom", "Take(Concatenate(Muon_SF_ID_nom[mu_mask]*Muon_SF_ISO_nom[mu_mask], Electron_SF_ID_nom[e_mask]*Electron_SF_EFF_nom[e_mask]), GLepton_argsort)")
#    else:
#        rdf = rdf.Define("GMuon_SF_ID_nom", "1")
#        rdf = rdf.Define("GMuon_SF_ID_stat", "0")
#        rdf = rdf.Define("GMuon_SF_ID_syst", "0")
#        rdf = rdf.Define("GMuon_SF_ISO_nom", "1")
#        rdf = rdf.Define("GMuon_SF_ISO_stat", "0")
#        rdf = rdf.Define("GMuon_SF_ISO_syst", "0")
#        rdf = rdf.Define("GElectron_SF_EFF_nom", "1")
#        rdf = rdf.Define("GElectron_SF_EFF_unc", "0")
#        rdf = rdf.Define("GElectron_SF_ID_nom", "1")
#        rdf = rdf.Define("GElectron_SF_ID_unc", "0")
#        rdf = rdf.Define("GLepton_SF_nom", "Take(Concatenate(Muon_SF_ID_nom[mu_mask]*Muon_SF_ISO_nom[mu_mask], Electron_SF_ID_nom[e_mask]*Electron_SF_EFF_nom[e_mask]), GLepton_argsort)")
    
                
    #Things that don't work...
    #NOPE doesn't work .Define("nLooseGMuon", "Sum(Muon_looseId[mu_mask])")\
#    return rdf


# In[ ]:


def defineInitWeights(input_df, crossSection=0, sumWeights=-1, lumi=0,
                  nEvents=-1, nEventsPositive=2, nEventsNegative=1,
                  isData=True, verbose=False):
    leppostfix = "_nom"
    
    mc_def = collections.OrderedDict()
    data_def = collections.OrderedDict()
    mc_def["wgt_NUMW"] = "({xs:s} * {lumi:s} * 1000 * genWeight) / (abs(genWeight) * ( {nevtp:s} - {nevtn:s} ) )"            .format(xs=str(crossSection), lumi=str(lumi), nevt=str(nEvents),
                    nevtp=str(nEventsPositive), nevtn=str(nEventsNegative))
    mc_def["wgt_SUMW"] = "({xs:s} * {lumi:s} * 1000 * genWeight) / {sumw:s}"            .format(xs=str(crossSection), lumi=str(lumi), sumw=str(sumWeights))
    mc_def["wgt_LSF"] = "(FTALepton{lpf}_SF_nom.size() > 1 ? FTALepton{lpf}_SF_nom.at(0) * FTALepton{lpf}_SF_nom.at(1) : FTALepton{lpf}_SF_nom.at(0))".format(lpf=leppostfix)
    mc_def["wgt_SUMW_PU"] = "wgt_SUMW * puWeight"
    mc_def["wgt_SUMW_LSF"] = "wgt_SUMW * wgt_LSF"
    mc_def["wgt_SUMW_L1PF"] = "wgt_SUMW * L1PreFiringWeight_Nom"
    mc_def["wgt_SUMW_PU_LSF"] = "wgt_SUMW * puWeight * wgt_LSF"
    mc_def["wgt_SUMW_PU_L1PF"] = "wgt_SUMW * puWeight * L1PreFiringWeight_Nom"
    mc_def["wgt_SUMW_PU_LSF_L1PF"] = "wgt_SUMW * puWeight * wgt_LSF * L1PreFiringWeight_Nom"
    mc_def["wgt_SUMW_LSF_L1PF"] = "wgt_SUMW * wgt_LSF * L1PreFiringWeight_Nom"
    mc_def["wgt_NUMW_LSF_L1PF"] = "wgt_NUMW * wgt_LSF * L1PreFiringWeight_Nom"
    #mc_def["wgt_SUMW_PU_LSF"] = "wgt_SUMW * puWeight * GLepton_SF_nom.at(0) * GLepton_SF_nom.at(1)"
    mc_def["SPL_SP"] = "wgt_SUMW_PU_LSF/wgt_SUMW_PU"
    mc_def["wgt_diff"] = "abs(wgt_NUMW - wgt_SUMW)/max(abs(wgt_SUMW), abs(wgt_NUMW))"
    for k in mc_def.keys():
        data_def[k] = "1"
    if verbose == True:
        print("===data and mc weight definitions===")
        print(data_def)
        print(mc_def)
        
    rdf = input_df
    if isData:
        for k, v in data_def.items():
            rdf = rdf.Define(k, v)
    else:
        for k, v in mc_def.items():
            rdf = rdf.Define(k, v)
    return rdf


# In[ ]:


def defineJets(input_df, era="2017", doAK8Jets=False, isData=True, debugInfo = True, 
               nJetsToHisto=10, useDeepCSV=True, verbose=False,
               sysVariations={"$NOMINAL": {"jet_mask": "jet_mask", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt",
                                             "jet_mass_var": "Jet_mass",
                                             "met_pt_var": "METFixEE2017_pt",
                                             "met_phi_var": "METFixEE2017_phi",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                              "_jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt_jesTotalUp",
                                             "jet_mass_var": "Jet_mass_jesTotalUp",
                                             "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                             "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                              "_jesTotalDown": {"jet_mask": "jet_mask_jesTotalDown", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt_jesTotalDown",
                                             "jet_mass_var": "Jet_mass_jesTotalDown",
                                             "met_pt_var": "METFixEE2017_pt_jesTotalDown",
                                             "met_phi_var": "METFixEE2017_phi_jesTotalDown",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                                },
              ):
    """Function to take in a dataframe and return one with new columns defined,
    plus event filtering based on the criteria defined inside the function"""
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
    print("FIXMEFIXME: Setting Jet_pt min to 30GeV! Must fix!")
    leppostfix = "_nom"
    #z will be a list of tuples to define, so that we can do cleaner error handling and checks
    z = []
    for sysVar, sysDict in sysVariations.items():
        #skip systematic variations on data, only do the nominal
        if isData and sysVar != "$NOMINAL": 
            continue
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        if isWeightVariation == True: continue
        jetMask = sysDict.get("jet_mask")
        jetPt = sysDict.get("jet_pt_var")
        jetMass = sysDict.get("jet_mass_var")
        postfix = sysVar.replace("$NOMINAL", "_nom")
        
        #Fill lists
        z.append(("Jet_idx", "FTA::generateIndices(Jet_pt)"))
        z.append(("{jm}".format(jm=jetMask), "({jpt} >= 30 && abs(Jet_eta) <= 2.5 && Jet_jetId > 2 && Jet_idx != FTALepton{lpf}_jetIdx_0 && Jet_idx != FTALepton{lpf}_jetIdx_1)".format(lpf=leppostfix, jpt=jetPt)))
        z.append(("nFTAJet{pf}".format(pf=postfix), "{jm}[{jm}].size()".format(jm=jetMask)))
        z.append(("FTAJet{pf}_ptsort".format(pf=postfix), "Reverse(Argsort({jpt}[{jm}]))".format(jpt=jetPt, jm=jetMask)))
        z.append(("FTAJet{pf}_deepcsvsort".format(pf=postfix), "Reverse(Argsort(Jet_{btv}[{jm}]))".format(btv=bTagWorkingPointDict[era]["DeepCSV"]["Var"], jm=jetMask)))
        z.append(("FTAJet{pf}_deepjetsort".format(pf=postfix), "Reverse(Argsort(Jet_{btv}[{jm}]))".format(btv=bTagWorkingPointDict[era]["DeepJet"]["Var"], jm=jetMask)))
        z.append(("FTAJet{pf}_idx".format(pf=postfix), "Jet_idx[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_pt".format(pf=postfix), "{jpt}[{jm}]".format(jpt=jetPt, jm=jetMask)))
        z.append(("FTAJet{pf}_eta".format(pf=postfix), "Jet_eta[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_phi".format(pf=postfix), "Jet_phi[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_mass".format(pf=postfix), "{jms}[{jm}]".format(jms=jetMass, jm=jetMask)))
        z.append(("FTAJet{pf}_jetId".format(pf=postfix), "Jet_jetId[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_puId".format(pf=postfix), "Jet_puId[{jm}]".format(jm=jetMask)))
        if isData is False:
            z.append(("FTAJet{pf}_genJetIdx".format(pf=postfix), "Jet_genJetIdx[{jm}]".format(jm=jetMask)))
            z.append(("nFTAJet{pf}_genMatched".format(pf=postfix), "FTAJet{pf}_genJetIdx[FTAJet{pf}_genJetIdx >= 0].size()".format(pf=postfix)))
            z.append(("nFTAJet{pf}_puIdLoose".format(pf=postfix), "FTAJet{pf}_genJetIdx[(FTAJet{pf}_puId >= 4 || FTAJet{pf}_pt >= 50)].size()".format(pf=postfix)))
            z.append(("nFTAJet{pf}_genMatched_puIdLoose".format(pf=postfix), "FTAJet{pf}_genJetIdx[FTAJet{pf}_genJetIdx >= 0 && (FTAJet{pf}_puId >= 4 || FTAJet{pf}_pt >= 50)].size()".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepCSVB".format(pf=postfix), "Jet_btagDeepB[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_DeepCSVB_sorted".format(pf=postfix), "Take(FTAJet{pf}_DeepCSVB, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepCSVB_sorted_LeadtagJet".format(pf=postfix), "FTAJet{pf}_DeepCSVB_sorted.size() > 0 ? FTAJet{pf}_DeepCSVB_sorted.at(0) : -9999".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepCSVB_sorted_SubleadtagJet".format(pf=postfix), "FTAJet{pf}_DeepCSVB_sorted.size() > 1 ? FTAJet{pf}_DeepCSVB_sorted.at(1) : -9999".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepJetB".format(pf=postfix), "Jet_btagDeepFlavB[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_DeepJetB_sorted".format(pf=postfix), "Take(FTAJet{pf}_DeepJetB, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepJetB_sorted_LeadtagJet".format(pf=postfix), "FTAJet{pf}_DeepJetB_sorted.size() > 0 ? FTAJet{pf}_DeepJetB_sorted.at(0) : -9999".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepJetB_sorted_SubleadtagJet".format(pf=postfix), "FTAJet{pf}_DeepJetB_sorted.size() > 1 ? FTAJet{pf}_DeepJetB_sorted.at(1) : -9999".format(pf=postfix)))
        for x in xrange(nJetsToHisto):
            z.append(("FTAJet{pf}_pt_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_pt.size() > {n} ? FTAJet{pf}_pt.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_eta_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_eta.size() > {n} ? FTAJet{pf}_phi.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_phi_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_phi.size() > {n} ? FTAJet{pf}_phi.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_DeepCSVB_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepCSVB.size() > {n} ? FTAJet{pf}_DeepCSVB.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_DeepJetB_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepJetB.size() > {n} ? FTAJet{pf}_DeepJetB.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_DeepCSVB_sortedjet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepCSVB_sorted.size() > {n} ? FTAJet{pf}_DeepCSVB_sorted.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_DeepJetB_sortedjet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepJetB_sorted.size() > {n} ? FTAJet{pf}_DeepJetB_sorted.at({n}) : -9999".format(pf=postfix, n=x)))
        z.append(("FTAJet{pf}_LooseDeepCSVB".format(pf=postfix), "FTAJet{pf}_DeepCSVB[FTAJet{pf}_DeepCSVB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepCSV"]["L"])))
        z.append(("FTAJet{pf}_MediumDeepCSVB".format(pf=postfix), "FTAJet{pf}_DeepCSVB[FTAJet{pf}_DeepCSVB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepCSV"]["M"])))
        z.append(("FTAJet{pf}_TightDeepCSVB".format(pf=postfix), "FTAJet{pf}_DeepCSVB[FTAJet{pf}_DeepCSVB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepCSV"]["T"])))
        z.append(("nLooseDeepCSVB{pf}".format(pf=postfix), "FTAJet{pf}_LooseDeepCSVB.size()".format(pf=postfix)))
        z.append(("nMediumDeepCSVB{pf}".format(pf=postfix), "FTAJet{pf}_MediumDeepCSVB.size()".format(pf=postfix)))
        z.append(("nTightDeepCSVB{pf}".format(pf=postfix), "FTAJet{pf}_TightDeepCSVB.size()".format(pf=postfix)))
        z.append(("FTAJet{pf}_LooseDeepJetB".format(pf=postfix), "FTAJet{pf}_DeepJetB[FTAJet{pf}_DeepJetB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepJet"]["L"])))
        z.append(("FTAJet{pf}_MediumDeepJetB".format(pf=postfix), "FTAJet{pf}_DeepJetB[FTAJet{pf}_DeepJetB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepJet"]["M"])))
        z.append(("FTAJet{pf}_TightDeepJetB".format(pf=postfix), "FTAJet{pf}_DeepJetB[FTAJet{pf}_DeepJetB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepJet"]["T"])))
        z.append(("nLooseDeepJetB{pf}".format(pf=postfix), "FTAJet{pf}_LooseDeepJetB.size()".format(pf=postfix)))
        z.append(("nMediumDeepJetB{pf}".format(pf=postfix), "FTAJet{pf}_MediumDeepJetB.size()".format(pf=postfix)))
        z.append(("nTightDeepJetB{pf}".format(pf=postfix), "FTAJet{pf}_TightDeepJetB.size()".format(pf=postfix)))
        #These might be more efficiently calculated with my own custom code, instead of this... well, lets try for the sake of experimentation
        #HT is just the sum of good jet pts
        # HT2M is the sum of jet pt's for all but the two highest-b-tagged jets (2016 analysis requires 4+ jets to define this quantity), so here Take() is used twice.
        # The first call acquires the good jet pt's sorted by b-tagging, the senond Take() gets the last n-2 elements, thereby excluding the two highest b-tagged jet's pt
        # HTRat = HT(two highest b-tagged) / HT, so it's useful to define this similarly to HT2M (and crosscheck that HTNum + HT2M = HT!)
        # H and H2M are defined similarly for the overall momentum magnitude...
        # P = pt/sin(theta) = pt * (1/sin(theta)) = pt * cosh(eta)
        if useDeepCSV:
            z.append(("FTAJet{pf}_pt_bsrt".format(pf=postfix), "Take(FTAJet{pf}_pt, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_eta_bsrt".format(pf=postfix), "Take(FTAJet{pf}_eta, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_phi_bsrt".format(pf=postfix), "Take(FTAJet{pf}_phi, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_mass_bsrt".format(pf=postfix), "Take(FTAJet{pf}_mass, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
        else:
            z.append(("FTAJet{pf}_pt_bsrt".format(pf=postfix), "Take(FTAJet{pf}_pt, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_eta_bsrt".format(pf=postfix), "Take(FTAJet{pf}_eta, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_phi_bsrt".format(pf=postfix), "Take(FTAJet{pf}_phi, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_mass_bsrt".format(pf=postfix), "Take(FTAJet{pf}_mass, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
        z.append(("FTAJet{pf}_P_bsrt".format(pf=postfix), "FTAJet{pf}_pt_bsrt * ROOT::VecOps::cosh(FTAJet{pf}_eta_bsrt)".format(pf=postfix)))
        z.append(("HT{pf}".format(pf=postfix), "Sum(FTAJet{pf}_pt)".format(pf=postfix)))
        z.append(("HT2M{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? Sum(Take(FTAJet{pf}_pt_bsrt, (2 - FTAJet{pf}_pt_bsrt.size()))) : -0.1".format(pf=postfix)))
        z.append(("HTNum{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? Sum(Take(FTAJet{pf}_pt_bsrt, 2)) : -0.1".format(pf=postfix)))
        z.append(("HTRat{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? (HT2M{pf} / HT{pf}) : -0.1".format(pf=postfix)))
        z.append(("dRbb{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? ROOT::VecOps::DeltaR(FTAJet{pf}_eta_bsrt.at(0), FTAJet{pf}_eta_bsrt.at(1), FTAJet{pf}_phi_bsrt.at(0), FTAJet{pf}_phi_bsrt.at(1)) : -0.1".format(pf=postfix)))
        z.append(("dPhibb{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? ROOT::VecOps::DeltaPhi(FTAJet{pf}_phi_bsrt.at(0), FTAJet{pf}_phi_bsrt.at(1)) : -999".format(pf=postfix)))
        z.append(("dEtabb{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? abs(FTAJet{pf}_eta_bsrt.at(0) - FTAJet{pf}_eta_bsrt.at(1)) : -999".format(pf=postfix)))
        z.append(("H{pf}".format(pf=postfix), "Sum(FTAJet{pf}_P_bsrt)".format(pf=postfix)))
        z.append(("H2M{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? Sum(Take(FTAJet{pf}_P_bsrt, (2 - FTAJet{pf}_pt_bsrt.size()))) : -0.1".format(pf=postfix)))
        z.append(("HTH{pf}".format(pf=postfix), "HT{pf}/H{pf}".format(pf=postfix)))
        if useDeepCSV:
            z.append(("HTb{pf}".format(pf=postfix), "Sum(FTAJet{pf}_pt[FTAJet{pf}_DeepCSVB > {wpv}])".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepCSV"]["M"])))
        else:
            z.append(("HTb{pf}".format(pf=postfix), "Sum(FTAJet{pf}_pt[FTAJet{pf}_DeepJetB > {wpv}])".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepJet"]["M"])))
        
    rdf = input_df
    listOfDefinedColumns = rdf.GetDefinedColumnNames()
    for defName, defFunc in z:
        if defName in listOfDefinedColumns:
            if verbose:
                print("{} already defined, skipping".format(defName))
            continue
        else:
            if verbose:
                print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
            rdf = rdf.Define(defName, defFunc)
            listOfDefinedColumns.push_back(defName)
                
    return rdf
        #rdf = rdf.Define("Jet_idx", "FTA::generateIndices(Jet_pt)")#G
        #rdf = rdf.Define("{}".format(jetMask), "({jpt} >= 30 && abs(Jet_eta) <= 2.5 && Jet_jetId > 2 && Jet_idx != GLepton_jetIdx_0 && Jet_idx != GLepton_jetIdx_1)".format(jpt=jetPt))#G
        #rdf = rdf.Define("jet{}_ptsort".format(postfix), "Reverse(Argsort({jpt}[{jm}]))".format(jpt=jetPt, jm=jetMask))#G
        #rdf = rdf.Define("jet{}_deepcsvsort".format(postfix), "Reverse(Argsort(Jet_{btv}[{jm}]))".format(btv=bTagWorkingPointDict[era]["DeepCSV"]["Var"], jetMask))#G
        #rdf = rdf.Define("jet{}_deepjetsort".format(postfix), "Reverse(Argsort(Jet_{btv}[{jm}]))".format(btv=bTagWorkingPointDict[era]["DeepJet"]["Var"], jetMask))#G
        #rdf = rdf.Define("Jet{}_idx".format(postfix), "Jet_idx[{jm}]".format(jm=jetMask))#G
        #rdf = rdf.Define("Jet{}_pt".format(postfix), "{jpt}[{jm}]".format(jpt=jetPt, jm=jetMask))#G
        #rdf = rdf.Define("Jet{}_eta".format(postfix), "Jet_eta[{jm}]".format(jm=jetMask))#G
        #rdf = rdf.Define("Jet{}_phi".format(postfix), "Jet_phi[{jm}]".format(jm=jetMask))#G
        #rdf = rdf.Define("Jet{}_mass".format(postfix), "{jms}[{jm}]".format(jms=jetMass, jm=jetMask))#G
        #rdf = rdf.Define("Jet{}_jetId".format(postfix), "Jet_jetId[{jm}]".format(jm=jetMask))#G
        #rdf = rdf.Define("Jet{}_puId".format(postfix), "Jet_puId[{jm}]".format(jm=jetMask))#G
        #if isData is False:
        #    rdf = rdf.Define("Jet{}_genJetIdx".format(postfix), "Jet_genJetIdx[jet_mask]")
        #    rdf = rdf.Define("nJet{}_genMatched".format(postfix), "Jet{}_genJetIdx[Jet{}_genJetIdx >= 0].size()")
        #    rdf = rdf.Define("nJet{}_puIdLoose".format(postfix), "Jet{}_genJetIdx[(Jet{}_puId >= 4 || Jet{}_pt >= 50)].size()")
        #    rdf = rdf.Define("nJet{}_genMatched_puIdLoose".format(postfix), "Jet{}_genJetIdx[Jet{}_genJetIdx >= 0 && (Jet{}_puId >= 4 || Jet{}_pt >= 50)].size()")
        #rdf = rdf.Define("nJet{}".format(postfix), "Jet{}_pt.size()".format(postfix))#G, don't want normal jetPt input here!
        #rdf = rdf.Define("Jet{}_btagDeepB", "Jet_btagDeepB[{jm}]".format(jm=jetMask))#G
        #rdf = rdf.Define("Jet{}_btagDeepB_sorted", "Take(Jet_btagDeepB[jet_mask], jet_deepcsvsort)")
        #rdf = rdf.Define("Jet{}_btagDeepFlavB_sorted_LeadtagJet", "Jet{}_btagDeepB_sorted.size() > 0 ? Jet{}_btagDeepB_sorted.at(0) : -9999")
        #rdf = rdf.Define("Jet{}_btagDeepFlavB_sorted_SubleadtagJet", "Jet{}_btagDeepB_sorted.size() > 1 ? Jet{}_btagDeepB_sorted.at(1) : -9999")
        #rdf = rdf.Define("Jet{}_btagDeepB_LeadtagJet", "Jet{}_btagDeepB.size() > 0 ? Reverse(Sort(Jet{}_btagDeepB)).at(0) : -0.000000000001")
        #rdf = rdf.Define("Jet{}_btagDeepB_SubleadtagJet", "Jet{}_btagDeepB.size() > 1 ? Reverse(Sort(Jet{}_btagDeepB)).at(1) : -0.000000000001")
        #rdf = rdf.Define("Jet{}_btagDeepFlavB", "Jet_btagDeepFlavB[jet_mask]")
        #rdf = rdf.Define("Jet{}_btagDeepFlavB_sorted", "Take(Jet_btagDeepFlavB[jet_mask], jet_deepjetsort)")
        #rdf = rdf.Define("Jet{}_btagDeepFlavB_sorted_LeadtagJet", "Jet{}_btagDeepFlavB_sorted.size() > 0 ? Jet{}_btagDeepFlavB_sorted.at(0) : -9999")
        #rdf = rdf.Define("Jet{}_btagDeepFlavB_sorted_SubleadtagJet", "Jet{}_btagDeepFlavB_sorted.size() > 1 ? Jet{}_btagDeepFlavB_sorted.at(1) : -9999")
        #for x in xrange(nJetsToHisto):
        #    rdf = rdf.Define("Jet{}_pt_jet{}".format(x+1), "Jet{}_pt.size() > {} ? Jet{}_pt.at({}) : -9999".format(x, x))
        #    rdf = rdf.Define("Jet{}_eta_jet{}".format(x+1), "Jet{}_eta.size() > {} ? Jet{}_phi.at({}) : -9999".format(x, x))
        #    rdf = rdf.Define("Jet{}_phi_jet{}".format(x+1), "Jet{}_phi.size() > {} ? Jet{}_phi.at({}) : -9999".format(x, x))
        #    rdf = rdf.Define("Jet{}_DeepCSV_jet{}".format(x+1), "Jet{}_btagDeepB.size() > {} ? Jet{}_btagDeepB.at({}) : -9999".format(x, x))
        #    rdf = rdf.Define("Jet{}_DeepJet_jet{}".format(x+1), "Jet{}_btagDeepFlavB.size() > {} ? Jet{}_btagDeepFlavB.at({}) : -9999".format(x, x))
        #    rdf = rdf.Define("Jet{}_DeepCSV_sortedjet{}".format(x+1), "Jet{}_btagDeepB_sorted.size() > {} ? Jet{}_btagDeepB_sorted.at({}) : -9999".format(x, x))
        #    rdf = rdf.Define("Jet{}_DeepJet_sortedjet{}".format(x+1), "Jet{}_btagDeepFlavB_sorted.size() > {} ? Jet{}_btagDeepFlavB_sorted.at({}) : -9999".format(x, x))
        #rdf = rdf.Define("Jet{}_LooseDeepCSV", "Jet{}_{0}[Jet{}_{0} > {1}]".format(bTagWorkingPointDict[era]["DeepCSV"]["Var"],
        #                                                                        bTagWorkingPointDict[era]["DeepCSV"]["L"]))
        #rdf = rdf.Define("Jet{}_MediumDeepCSV", "Jet{}_{0}[Jet{}_{0} > {1}]".format(bTagWorkingPointDict[era]["DeepCSV"]["Var"],
        #                                                                        bTagWorkingPointDict[era]["DeepCSV"]["M"]))
        #rdf = rdf.Define("Jet{}_TightDeepCSV", "Jet{}_{0}[Jet{}_{0} > {1}]".format(bTagWorkingPointDict[era]["DeepCSV"]["Var"],
        #                                                                        bTagWorkingPointDict[era]["DeepCSV"]["T"]))
        #rdf = rdf.Define("nJet{}_LooseDeepCSV", "Jet{}_LooseDeepCSV.size()")
        #rdf = rdf.Define("nJet{}_MediumDeepCSV", "Jet{}_MediumDeepCSV.size()")
        #rdf = rdf.Define("nJet{}_TightDeepCSV", "Jet{}_TightDeepCSV.size()")
        #rdf = rdf.Define("Jet{}_LooseDeepJet", "Jet{}_{0}[Jet{}_{0} > {1}]".format(bTagWorkingPointDict[era]["DeepJet"]["Var"],
        #                                                                        bTagWorkingPointDict[era]["DeepJet"]["L"]))
        #rdf = rdf.Define("Jet{}_MediumDeepJet", "Jet{}_{0}[Jet{}_{0} > {1}]".format(bTagWorkingPointDict[era]["DeepJet"]["Var"],
        #                                                                        bTagWorkingPointDict[era]["DeepJet"]["M"]))
        #rdf = rdf.Define("Jet{}_TightDeepJet", "Jet{}_{0}[Jet{}_{0} > {1}]".format(bTagWorkingPointDict[era]["DeepJet"]["Var"],
        #                                                                        bTagWorkingPointDict[era]["DeepJet"]["T"]))
        #rdf = rdf.Define("nJet{}_LooseDeepJet", "Jet{}_LooseDeepJet.size()")
        #rdf = rdf.Define("nJet{}_MediumDeepJet", "Jet{}_MediumDeepJet.size()")
        #rdf = rdf.Define("nJet{}_TightDeepJet", "Jet{}_TightDeepJet.size()")
        #These might be more efficiently calculated with my own custom code, instead of this... well, lets try for the sake of experimentation
        #HT is just the sum of good jet pts
        # HT2M is the sum of jet pt's for all but the two highest-b-tagged jets (2016 analysis requires 4+ jets to define this quantity), so here Take() is used twice.
        # The first call acquires the good jet pt's sorted by b-tagging, the senond Take() gets the last n-2 elements, thereby excluding the two highest b-tagged jet's pt
        # HTRat = HT(two highest b-tagged) / HT, so it's useful to define this similarly to HT2M (and crosscheck that HTNum + HT2M = HT!)
        # H and H2M are defined similarly for the overall momentum magnitude...
        # P = pt/sin(theta) = pt * (1/sin(theta)) = pt * cosh(eta)
        #if useDeepCSV:
        #    rdf = rdf.Define("Jet{}_pt_bsrt", "Take(Jet{}_pt, jet_deepcsvsort)")
        #    rdf = rdf.Define("Jet{}_eta_bsrt", "Take(Jet{}_eta, jet_deepcsvsort)")
        #    rdf = rdf.Define("Jet{}_phi_bsrt", "Take(Jet{}_phi, jet_deepcsvsort)")
        #else:
        #    rdf = rdf.Define("Jet{}_pt_bsrt", "Take(Jet{}_pt, jet_deepjetsort)")
        #    rdf = rdf.Define("Jet{}_eta_bsrt", "Take(Jet{}_eta, jet_deepjetsort)")
        #    rdf = rdf.Define("Jet{}_phi_bsrt", "Take(Jet{}_phi, jet_deepjetsort)")
        #rdf = rdf.Define("Jet{}_P_bsrt", "Jet{}_pt_bsrt * ROOT::VecOps::cosh(Jet{}_eta_bsrt)")
        #rdf = rdf.Define("Jet{}_HT", "Sum(Jet{}_pt)")
        #rdf = rdf.Define("Jet{}_HT2M", "Jet{}_pt_bsrt.size() > 2 ? Sum(Take(Jet{}_pt_bsrt, (2 - Jet{}_pt_bsrt.size()))) : -0.1")
        #rdf = rdf.Define("Jet{}_HTNum", "Jet{}_pt_bsrt.size() > 2 ? Sum(Take(Jet{}_pt_bsrt, 2)) : -0.1")
        #rdf = rdf.Define("Jet{}_HTRat", "Jet{}_pt_bsrt.size() > 2 ? (Jet{}_HT2M / Jet{}_HT) : -0.1")
        #rdf = rdf.Define("Jet{}_dRbb", "Jet{}_pt_bsrt.size() > 2 ? ROOT::VecOps::DeltaR(Jet{}_eta_bsrt.at(0), Jet{}_eta_bsrt.at(1), Jet{}_phi_bsrt.at(0), Jet{}_phi_bsrt.at(1)) : -0.1")
        #rdf = rdf.Define("Jet{}_dPhibb", "Jet{}_pt_bsrt.size() > 2 ? ROOT::VecOps::DeltaPhi(Jet{}_phi_bsrt.at(0), Jet{}_phi_bsrt.at(1)) : -999")
        #rdf = rdf.Define("Jet{}_dEtabb", "Jet{}_pt_bsrt.size() > 2 ? abs(Jet{}_eta_bsrt.at(0) - Jet{}_eta_bsrt.at(1)) : -999")
        #rdf = rdf.Define("Jet{}_H", "Sum(Jet{}_P_bsrt)")
        #rdf = rdf.Define("Jet{}_H2M", "Jet{}_pt_bsrt.size() > 2 ? Sum(Take(Jet{}_P_bsrt, (2 - Jet{}_pt_bsrt.size()))) : -0.1")
        #rdf = rdf.Define("Jet{}_HTH", "Jet{}_HT/Jet{}_H")
        #rdf = rdf.Define("Jet{}_HTb", "Sum(Jet{}_pt[Jet{}_{0} > {1}])".format(bTagWorkingPointDict[era]["DeepJet"]["Var"],
        #                                                                        bTagWorkingPointDict[era]["DeepJet"]["M"]))
        #if debugInfo == True:
        #    rdf = rdf.Define("Jet{}_ptALT", "Jet_pt[jet_maskALT]")
        #    rdf = rdf.Define("Jet{}_etaALT", "Jet_eta[jet_maskALT]")
        #    rdf = rdf.Define("Jet{}_phiALT", "Jet_phi[jet_maskALT]")
        #    rdf = rdf.Define("Jet{}_massALT", "Jet_mass[jet_maskALT]")
        #    rdf = rdf.Define("Jet{}_jetIdALT", "Jet_jetId[jet_maskALT]")
        #    rdf = rdf.Define("DiffMaskVsALT", "Jet{}_ptALT.size() - Jet{}_pt.size()")
        #    rdf = rdf.Define("DiffnJet", "nGJet - ESV_JetMETLogic_nJet_selection")
        #    rdf = rdf.Define("dR_Jet_Mu_leading", "GLepton_jetIdx_0 > -1 && abs(GLepton_pdgId.at(0)) == 13 ? ROOT::VecOps::DeltaR(Jet_eta.at(GLepton_jetIdx_0), GLepton_eta.at(0), Jet_phi.at(GLepton_jetIdx_0), GLepton_phi.at(0)) : -0.01")
        #    rdf = rdf.Define("dR_Jet_Mu_sublead", "GLepton_jetIdx_1 > -1 && abs(GLepton_pdgId.at(1)) == 13 ? ROOT::VecOps::DeltaR(Jet_eta.at(GLepton_jetIdx_1), GLepton_eta.at(1), Jet_phi.at(GLepton_jetIdx_1), GLepton_phi.at(1)) : -0.01")
        #    rdf = rdf.Define("dR_Jet_El_leading", "GLepton_jetIdx_0 > -1 && abs(GLepton_pdgId.at(1)) == 11 ? ROOT::VecOps::DeltaR(Jet_eta.at(GLepton_jetIdx_0), GLepton_eta.at(0), Jet_phi.at(GLepton_jetIdx_0), GLepton_phi.at(0)) : -0.01")
        #    rdf = rdf.Define("dR_Jet_El_sublead", "GLepton_jetIdx_1 > -1 && abs(GLepton_pdgId.at(1)) == 11 ? ROOT::VecOps::DeltaR(Jet_eta.at(GLepton_jetIdx_1), GLepton_eta.at(1), Jet_phi.at(GLepton_jetIdx_1), GLepton_phi.at(1)) : -0.01")
        #    #rdf = rdf.Define("dR_Jet_lep0", "GLepton_jetIdx_0 > -1 ? ROOT::VecOps::DeltaR(Jet_eta.at(GLepton_jetIdx_0), GLepton_eta.at(0), Jet_phi.at(GLepton_jetIdx_0), GLepton_phi.at(0)) : -0.01")
        #    #rdf = rdf.Define("dR_Jet_lep1", "GLepton_jetIdx_1 > -1 ? ROOT::VecOps::DeltaR(Jet_eta.at(GLepton_jetIdx_1), GLepton_eta.at(1), Jet_phi.at(GLepton_jetIdx_1), GLepton_phi.at(1)) : -0.01")
        #    rdf = rdf.Define("Jet{}_btagDeepFlavB_jet0Med", "Jet{}_MediumDeepJet.size() > 0 ? Reverse(Sort(Jet{}_MediumDeepJet)).at(0) : -0.000000000001")
        #    rdf = rdf.Define("Jet{}_btagDeepFlavB_jet1Med", "Jet{}_MediumDeepJet.size() > 1 ? Reverse(Sort(Jet{}_MediumDeepJet)).at(1) : -0.000000000001")
        #    rdf = rdf.Define("DeepJetSorted", "Jet{}_btagDeepFlavB_sorted.size() > 1 ? (Jet{}_btagDeepFlavB_sorted.at(0) >= Jet{}_btagDeepFlavB_sorted.at(1)) : true")
        #    rdf = rdf.Define("DeepJet0Minus1", "Jet{}_btagDeepFlavB_sorted.size() > 1 ? (Jet{}_btagDeepFlavB_sorted.at(0) - Jet{}_btagDeepFlavB_sorted.at(1)) : 0")
        #    rdf = rdf.Define("MediumDeepJetSorted", "Jet{}_MediumDeepJet.size() > 1 ? (Reverse(Sort(Jet{}_MediumDeepJet)).at(0) >= Reverse(Sort(Jet{}_MediumDeepJet)).at(1)) : true")
        #    rdf = rdf.Define("MediumDeepJet0Minus1", "Jet{}_MediumDeepJet.size() > 1 ? (Reverse(Sort(Jet{}_MediumDeepJet)).at(0) - Reverse(Sort(Jet{}_MediumDeepJet)).at(1)) : 0")
        #return rdf
        #Code taht doesn't work...
        #Can see that the jets are in fact not sorted when calling Reverse(Jet{}_MediumDeepJet).at(0), for example, as the one .at(1) can sometimes not be smaller
        #Looking at the definition makes it obvious, because Reverse is not short for "ReverseSort" but is literally just std::reverse. Must call (Arg)sort first...
        #Definig a functor in the string like this doesn't work either:
        #.Define("Jet{}_btagDeepB_jet0", "Jet{}_btagDeepB.size() > 0 ? Sort(Jet{}_btagDeepB, [](double x, double y) {return x > y;}).at(0) : -0.000000000001")\
        #Cannot use ternary operator with RVec and double return types (Take(...) : -0.0000000001)
        #.Define("Jet{}_btagDeepFlavB_jet0", "Jet{}_btagDeepFlavB.size() > 0 ? Take(Reverse(Jet{}_btagDeepFlavB), {0}) : -0.000000000001")\


# In[ ]:


def defineWeights(input_df, isData=False, verbose=False, final=False):
    """Define all the pre-final or final weights and the variations, to be referened by the sysVariations dictionaries as wgt_final.
    if final=False, do the pre-final weights for BtaggingYields calculations.
    
    pwgt = partial weight, component for final weight
    wgt_$SYSTEMATIC is form of final event weights, i.e. wgt_nom or wgt_puWeightDown
    prewgt_$SYSTEMATIC is form of weight for BtaggingYields calculation, should include everything but pwgt_btag_$SYSTEMATIC"""
    rdf = input_df
    #There's only one lepton branch variation (nominal), but if it ever changes, this will serve as sign it's referenced here and made need to be varied
    leppostfix = "_nom"
    
    #Two lists of weight definitions, one or the other is chosen at the end via 'final' optional parameter
    zFin = []
    zPre = []
    zFin.append(("pwgt_XS", "wgt_SUMW")) #alias this until it's better defined here or elsewhere
    zFin.append(("pwgt_LSF_nom", "(FTALepton{lpf}_SF_nom.size() > 1 ? FTALepton{lpf}_SF_nom.at(0) * FTALepton{lpf}_SF_nom.at(1) : FTALepton{lpf}_SF_nom.at(0))".format(lpf=leppostfix)))
    zPre.append(("pwgt_XS", "wgt_SUMW")) #alias this until it's better defined here or elsewhere
    zPre.append(("pwgt_LSF_nom", "(FTALepton{lpf}_SF_nom.size() > 1 ? FTALepton{lpf}_SF_nom.at(0) * FTALepton{lpf}_SF_nom.at(1) : FTALepton{lpf}_SF_nom.at(0))".format(lpf=leppostfix)))
    
    #WARNING: on btag weights, it can ALWAYS be 'varied' to match the systematic, so that the event weight from
    #the correct jet collection, btag SFs, and yields is used. Always match! This duplicates some calculations uselessly
    #in the BtaggingYields function, but it should help avoid mistakes at the level of final calculations
    
    #Nominal weight
    zFin.append(("wgt_nom", "pwgt_XS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF_nom * pwgt_btag_nom"))
    #pre-btagging yield weight. Careful modifying, it is 'inherited' for may other weights below!
    zPre.append(("prewgt_nom", "pwgt_XS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF_nom"))
    
    #JES Up and Down - effectively the nominal weight, but with the CORRECT btag weight for those jets!
    zFin.append(("wgt_jesTotalDown", "pwgt_XS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF_nom * pwgt_btag_jesTotalDown"))
    zFin.append(("wgt_jesTotalUp", "pwgt_XS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF_nom * pwgt_btag_jesTotalUp"))
    
    zPre.append(("prewgt_jesTotalDown", "prewgt_nom")) #JES *weight* only changes with event-level btag weight, so this is just the nominal
    zPre.append(("prewgt_jesTotalUp", "prewgt_nom"))
    
    #Pileup variations 
    print("FIXME: Using temporary definition of weights for PU variations (change pwgt_btag_VARIATION)")
    zFin.append(("wgt_puWeightDown", "pwgt_XS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF_nom * pwgt_btag_nom"))
    zFin.append(("wgt_puWeightUp", "pwgt_XS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF_nom * pwgt_btag_nom"))
    #zFin.append(("wgt_puWeightDown", "pwgt_XS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF_nom * pwgt_btag_puWeightDown"))
    #zFin.append(("wgt_puWeightUp", "pwgt_XS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF_nom * pwgt_btag_puWeightUp"))
    
    zPre.append(("prewgt_puWeightDown", "pwgt_XS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF_nom"))
    zPre.append(("prewgt_puWeightUp", "pwgt_XS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF_nom"))
    #zPre.append(("prewgt_puWeightDown", "pwgt_XS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF_nom"))
    #zPre.append(("prewgt_puWeightUp", "pwgt_XS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF_nom"))
    
    #L1 PreFiring variations
    print("FIXME: Using temporary definition of weights for L1PreFire variations (change pwgt_btag_VARIATION)")
    zFin.append(("wgt_L1PreFireDown", "pwgt_XS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF_nom * pwgt_btag_nom"))
    zFin.append(("wgt_L1PreFireUp", "pwgt_XS * puWeight * L1PreFiringWeight_Up * pwgt_LSF_nom * pwgt_btag_nom"))
    #zFin.append(("wgt_L1PreFireDown", "pwgt_XS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF_nom * pwgt_btag_L1PreFireDown"))
    #zFin.append(("wgt_L1PreFireUp", "pwgt_XS * puWeight * L1PreFiringWeight_Up * pwgt_LSF_nom * pwgt_btag_L1PreFireUp"))
    
    zPre.append(("prewgt_L1PreFireDown", "pwgt_XS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF_nom"))
    zPre.append(("prewgt_L1PreFireUp", "pwgt_XS * puWeight * L1PreFiringWeight_Up * pwgt_LSF_nom"))
    #zPre.append(("prewgt_L1PreFireDown", "pwgt_XS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF_nom"))
    #zPre.append(("prewgt_L1PreFireUp", "pwgt_XS * puWeight * L1PreFiringWeight_Up * pwgt_LSF_nom"))
    
    #Lepton ScaleFactor variations
    #To be done, still...
    
    #HLT SF variations
    #To be done, still...
    
    #Pure BTagging variations, no other variations necessary. 
    #Since there may be many, use a common base factor for fewer multiplies... for pre-btagging, they're identical!
    zFin.append(("pwgt_btagSF_common", "pwgt_XS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF_nom"))
    zFin.append(("wgt_btagSF_deepcsv_shape_down_hf", "pwgt_btagSF_common * pwgt_btag_btagSF_deepcsv_shape_down_hf"))
    zFin.append(("wgt_btagSF_deepcsv_shape_up_hf", "pwgt_btagSF_common * pwgt_btag_btagSF_deepcsv_shape_up_hf"))
    zFin.append(("wgt_btagSF_deepcsv_shape_down_lf", "pwgt_btagSF_common * pwgt_btag_btagSF_deepcsv_shape_down_lf"))
    zFin.append(("wgt_btagSF_deepcsv_shape_up_lf", "pwgt_btagSF_common * pwgt_btag_btagSF_deepcsv_shape_up_lf"))
    
    zPre.append(("pwgt_btagSF_common", "pwgt_XS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF_nom"))
    zPre.append(("prewgt_btagSF_deepcsv_shape_down_hf", "pwgt_btagSF_common"))#Really just aliases w/o btagging part
    zPre.append(("prewgt_btagSF_deepcsv_shape_up_hf", "pwgt_btagSF_common"))
    zPre.append(("prewgt_btagSF_deepcsv_shape_down_lf", "pwgt_btagSF_common"))
    zPre.append(("prewgt_btagSF_deepcsv_shape_up_lf", "pwgt_btagSF_common"))
    
    #Factorization/Renormalization weights... depend on dividing genWeight back out?
    #TBD x4 for top samples, MAYBE NOT FOR OTHERS! (Until "Run II Legacy" samples are being used)
    
    #Load the initial or final definitions
    if final:
        z = zFin
    else:
        z = zPre
    if isData:
        rdf = rdf.Define("wgt_nom", "1")
    else:
        listOfDefinedColumns = rdf.GetDefinedColumnNames()
        for defName, defFunc in z:
            if defName in listOfDefinedColumns:
                if verbose:
                    print("{} already defined, skipping".format(defName))
                continue
            else:
                if verbose:
                    print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
                rdf = rdf.Define(defName, defFunc)
                listOfDefinedColumns.push_back(defName) 
    return rdf


# In[ ]:


def BtaggingYields(input_df, sampleName, isData = True, histos_dict=None, verbose=False,
                   sysVariations={"$NOMINAL": {"jet_mask": "jet_mask", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt",
                                             "jet_mass_var": "Jet_mass",
                                             "met_pt_var": "METFixEE2017_pt",
                                             "met_phi_var": "METFixEE2017_phi",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                              "_jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt_jesTotalUp",
                                             "jet_mass_var": "Jet_mass_jesTotalUp",
                                             "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                             "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                              "_jesTotalDown": {"jet_mask": "jet_mask_jesTotalDown", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt_jesTotalDown",
                                             "jet_mass_var": "Jet_mass_jesTotalDown",
                                             "met_pt_var": "METFixEE2017_pt_jesTotalDown",
                                             "met_phi_var": "METFixEE2017_phi_jesTotalDown",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                                  "_btagSF_deepcsv_shape_up_hf": {"jet_mask": "jet_mask", 
                                                                 "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                                 "jet_pt_var": "Jet_pt",
                                                                 "btagSF": "Jet_btagSF_deepcsv_shape_up_hf",
                                                                 "weightVariation": True},
                                  "_btagSF_deepcsv_shape_down_hf": {"jet_mask": "jet_mask", 
                                                                   "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                                   "jet_pt_var": "Jet_pt",
                                                                   "btagSF": "Jet_btagSF_deepcsv_shape_down_hf",
                                                                   "weightVariation": True},
                                  "_btagSF_deepcsv_shape_up_lf": {"jet_mask": "jet_mask", 
                                                                 "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                                 "jet_pt_var": "Jet_pt",
                                                                 "btagSF": "Jet_btagSF_deepcsv_shape_up_lf",
                                                                 "weightVariation": True},
                                  "_btagSF_deepcsv_shape_down_lf": {"jet_mask": "jet_mask", 
                                                                   "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                                   "jet_pt_var": "Jet_pt",
                                                                   "btagSF": "Jet_btagSF_deepcsv_shape_down_lf",
                                                                   "weightVariation": True},
                                              },
                   loadYields=None,
                   lookupMap="LUM",
                   useAggregate=True,
                   calculateYields=True,
                   HTBinWidth=10, HTMin=200, HTMax=3200,
                   nJetBinWidth=1, nJetMin=4, nJetMax=20):
    """Calculate or load the event yields in various categories for the purpose of renormalizing btagging shape correction weights.
    
    A btagging preweight (event level) must be calculated using the product of all SF(discriminant, pt, eta) for
    all selected jets. Then a ratio of the sum(weights before)/sum(weights after) for application of this btagging 
    preweight serves as a renormalization, and this phase space extrapolation can be a function of multiple variables.
    Minimally, for high-jet multiplicity analyses, it can be expected to depend on nJet. The final btagging event weight
    is then the product of this phase space ratio and the btagging preweight. This should be computed PRIOR to ANY
    btagging requirements; after, the event yields and shapes are expected to shift.
    
    The final and preweight are computed separately from the input weight (that is, it must be multiplied with the non-btagging event weight)
    The yields are calculated as the sum of weights before and after multiplying the preweight with the input weight
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagShapeCalibration"""
                        
    JetBins = int((nJetMax - nJetMin)/nJetBinWidth)
    HTBins = int((HTMax-HTMin)/HTBinWidth)
    
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
            raise RuntimeError("lookupMap (used in BtaggingYields function) must either be a string name "                               "for the declared function's (C++ variable) name, used to find or declare one of type "                               "std::map<std::string, std::vector<TH2Lookup*>>")
        nSlots = input_df.GetNSlots()
        while iLUM[sampleName].size() < nSlots:
            if type(loadYields) == str:
                iLUM[sampleName].push_back(ROOT.TH2Lookup(loadYields))
            elif loadYields == True:
                iLUM[sampleName].push_back(ROOT.TH2Lookup("/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/BTaggingYields.root"))
    
    #column guards
    listOfColumns = input_df.GetDefinedColumnNames()
    listOfDefinedColumns = input_df.GetColumnNames() #This is a superset, containing non-Define'd columns as well

    if isData == True:
        return input_df
    else:
        rdf = input_df
        #List of defines to do
        z = {}
        #Create list of the variations to be histogrammed (2D yields)
        yieldList = []
        #Add key to histos dictionary, if calculating the yields
        if calculateYields and "BtaggingYields" not in histos_dict.keys():
            histos_dict["BtaggingYields"] = {}
        for sysVar, sysDict in sysVariations.items():
            z[sysVar] = []
            isWeightVariation = sysDict.get("weightVariation")
            branchpostfix = "_nom" if isWeightVariation else sysVar.replace("$NOMINAL", "_nom") #branch postfix for 
            syspostfix = sysVar.replace("$NOMINAL", "_nom")
            jetMask = sysDict.get("jet_mask") #mask as defined for the jet collection under this systematic variation
            jetPt = sysDict.get("jet_pt_var") #colum name of jet pt collection for this systematic
            jetSF = sysDict.get("btagSF") #colum name of per-jet shape SFs
            #We must get or calculate various weights, defined below
            #This btagSFProduct is the product of the SFs for the selected jets from collection jetPt with mask jetMask
            btagSFProduct = "btagSFProduct{spf}".format(spf=syspostfix)
            #input weight, should include all corrections for this systematic variation except Btagging SF and yield ratio
            calculationWeightBefore = "prewgt{spf}".format(spf=syspostfix)
            #For calculating the yeild ratio, we need this weight, which will be the product of calculationWeightBefore and the product of btag SFs (no yield ratio!)
            calculationWeightAfter = "calcBtagYields_after{spf}".format(spf=syspostfix)
            #Define the form of the final name of the btagSFProduct * YieldRatio(HT, nJet)
            #This needs to match what will be picked up in the final weight definitions!
            btagFinalWeight = "pwgt_btag{spf}".format(spf=syspostfix)
            
            #Lets be really obvious about missing jet_masks... exception it
            if jetMask not in listOfDefinedColumns:
                raise RuntimeError("Could not find {} column in method BtaggingYields".format(jetMask))
            
            #Skip SFs for which the requisite per-jet SFs are not present...
            if jetSF not in listOfDefinedColumns:
                if verbose: print("Skipping {} in BtaggingYields as it is not a valid column name".format(jetSF))
                continue
                
            #Check we have the input weight for before btagSF and yield ratio multiplication
            if calculationWeightBefore not in listOfDefinedColumns:
                raise RuntimeError("{} is not defined, cannot continue with calculating BTaggingYields".format(calculationWeightBefore))
            
            #Now check if the event preweight SF is in the list of columns, and if not, define it (common to calculating yields and loading them...)
            #We might want to call this function twice to calculate yields for a future iteration and use an older iteration at the same time
            if btagSFProduct not in listOfDefinedColumns:
                if calculateYields and btagSFProduct not in histos_dict["BtaggingYields"].keys():
                    histos_dict["BtaggingYields"][btagSFProduct] = {}
                z[sysVar].append(("{}".format(btagSFProduct), "FTA::btagEventWeight_shape({}, {})".format(jetSF, jetMask)))
            if calculationWeightAfter not in listOfDefinedColumns:
                z[sysVar].append(("{}".format(calculationWeightAfter), "{} * {}".format(calculationWeightBefore, 
                                                                                         btagSFProduct)))
                
            #Check that the HT and nJet numbers are available to us, and if not, define them based on the available masks    
            #if isScaleVariation:
            nJetName = "nFTAJet{bpf}".format(bpf=branchpostfix)
            HTName = "HT{bpf}".format(bpf=branchpostfix)
            if nJetName not in listOfDefinedColumns:
                z[sysVar].append((nJetName, "{0}[{1}].size()".format(jetPt, jetMask)))
            if HTName not in listOfDefinedColumns:
                z[sysVar].append((HTName, "Sum({0}[{1}])".format(jetPt, jetMask)))
            
            #loadYields path...
            if loadYields:
                if useAggregate:
                    z[sysVar].append((btagFinalWeight, "{bsf} * {lm}[\"{sn}\"][rdfslot_]->getEventYieldRatio(\"{yk}\", \"{vk}\", {nj}, {ht});"                                     .format(bsf=btagSFProduct, lm=lookupMap, sn=sampleName, yk="Aggregate", vk=btagSFProduct.replace("nonorm_",""), nj=nJetName, ht=HTName)))
                else:
                    z[sysVar].append((btagFinalWeight, "{bsf} * {lm}[\"{sn}\"][rdfslot_]->getEventYieldRatio(\"{yk}\", \"{vk}\", {nj}, {ht});"                                     .format(bsf=btagSFProduct, lm=lookupMap, sn=sampleName, yk=sampleName, vk=btagSFProduct.replace("nonorm_",""), nj=nJetName, ht=HTName)))

            for defName, defFunc in z[sysVar]:
                if defName in listOfDefinedColumns:
                    if verbose:
                        print("{} already defined, skipping".format(defName))
                    continue
                else:
                    if verbose:
                        print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
                    rdf = rdf.Define(defName, defFunc)
                    listOfDefinedColumns.push_back(defName)        
            #calculate Yields path
            if calculateYields:
                k = btagSFProduct
                histos_dict["BtaggingYields"][k] = {}
                histos_dict["BtaggingYields"][k]["sumW_before"] = rdf.Histo2D(("{}_BtaggingYield_{}_sumW_before".format(sampleName, btagSFProduct.replace("btagSFProduct_","")), 
                                                                               "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                                               HTBins, HTMin, HTMax,
                                                                               JetBins, nJetMin, nJetMax),
                                                                               HTName,
                                                                               nJetName,
                                                                               calculationWeightBefore)
                histos_dict["BtaggingYields"][k]["sumW_after"] = rdf.Histo2D(("{}_BtaggingYield_{}_sumW_after".format(sampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                                              "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                                              HTBins, HTMin, HTMax,
                                                                              JetBins, nJetMin, nJetMax),
                                                                              HTName,
                                                                              nJetName,
                                                                              calculationWeightAfter)
                #For Unified JetBinning calculation
                histos_dict["BtaggingYields"][k]["1DXsumW_before"] = rdf.Histo2D(("{}_BtaggingYield1DX_{}_sumW_before".format(sampleName, btagSFProduct.replace("btagSFProduct_","")), 
                                                                               "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                                               HTBins, HTMin, HTMax,
                                                                               1, nJetMin, nJetMax),
                                                                               HTName,
                                                                               nJetName,
                                                                               calculationWeightBefore)
                histos_dict["BtaggingYields"][k]["1DXsumW_after"] = rdf.Histo2D(("{}_BtaggingYield1DX_{}_sumW_after".format(sampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                                              "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                                              HTBins, HTMin, HTMax,
                                                                              1, nJetMin, nJetMax),
                                                                              HTName,
                                                                              nJetName,
                                                                              calculationWeightAfter)
                #For Unified HTBinning calculation
                histos_dict["BtaggingYields"][k]["1DYsumW_before"] = rdf.Histo2D(("{}_BtaggingYield1DY_{}_sumW_before".format(sampleName, btagSFProduct.replace("btagSFProduct_","")), 
                                                                               "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                                               1, HTMin, HTMax,
                                                                               JetBins, nJetMin, nJetMax),
                                                                               HTName,
                                                                               nJetName,
                                                                               calculationWeightBefore)
                histos_dict["BtaggingYields"][k]["1DYsumW_after"] = rdf.Histo2D(("{}_BtaggingYield1DY_{}_sumW_after".format(sampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                                              "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                                              1, HTMin, HTMax,
                                                                              JetBins, nJetMin, nJetMax),
                                                                              HTName,
                                                                              nJetName,
                                                                              calculationWeightAfter)
        return rdf


def BtaggingEfficiencies(input_df, sampleName=None, era="2017", wgtVar="wgt_SUMW_PU_L1PF", isData = True, histos_dict=None, 
               doDeepCSV=True, doDeepJet=True, debugInfo=False):
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
        if histos_dict != None:
            if "Btagging" not in histos_dict:
                histos_dict["Btagging"] = {}
            for tc in theCats.keys(): 
                if tc not in histos_dict["Btagging"]: 
                    histos_dict["Btagging"][tc] = {}
            for tc, cut in theCats.items():
                tcn = tc.replace("blind_", "")
                for jettype in ["bjet", "cjet", "udsgjet"]:
                    histos_dict["Btagging"][tc]["{}s_untagged".format(jettype)] = cat_df[tc].Histo2D(("{0}s_untagged_[{0}]({1})".format(tcn, wgtVar), ";jet p_{T}; jet |#eta|", 248, 20, 2500, 25, 0, 2.5), 
                                                                                                     "GJet_{}_untagged_pt".format(jettype), "GJet_{}_untagged_abseta".format(jettype), wgtVar)
                    for algo in validAlgos:
                        for wp in ["L", "M", "T"]:
                            histos_dict["Btagging"][tc]["{0}s_{1}_{2}".format(jettype, algo, wp)] = cat_df[tc].Histo2D(("{0}s_{1}_{2}_[{0}]({3})".format(tcn, algo, wp, wgtVar), ";jet p_{T}; jet |#eta|", 248, 20, 2500, 25, 0, 2.5), 
                                                                                                             "GJet_{0}_{1}_{2}_pt".format(jettype, algo, wp), "GJet_{0}_{1}_{2}_abseta".format(jettype, algo, wp), wgtVar)
                            
                            


# In[ ]:


def cutPVandMETFilters(input_df, level, isData=False):
    if "selection" in level: 
        lvl = "selection"
    else:
        lvl = "baseline"
    PVbits = 0b00000000000000000111
    METbits_MC = 0b00000000001111110000
    METbits_Data = 0b00000000000000001000
    if isData:
        METbits = METbits_MC + METbits_Data 
    else:
        METbits = METbits_MC
    rdf = input_df.Filter("(ESV_JetMETLogic_{lvl} & {bits}) >= {bits}".format(lvl=lvl, bits=METbits), "PV, MET Filters")
    return rdf

def insertPVandMETFilters(input_df, level, era="2017", isData=False):
    rdf = input_df
    #flags for MET filters
    FlagsDict = {"2016" :  
                 { "isData" : ["globalSuperTightHalo2016Filter"],
                   "Common" :  ["goodVertices",
                                "HBHENoiseFilter",
                                "HBHENoiseIsoFilter",
                                "EcalDeadCellTriggerPrimitiveFilter",
                                "BadPFMuonFilter"
                               ],
                   "NotRecommended" : ["BadChargedCandidateFilter",
                                       "eeBadScFilter"
                                      ],
                 },
                 "2017" :  
                 { "isData" : ["globalSuperTightHalo2016Filter"],
                   "Common" :  ["goodVertices",
                                "HBHENoiseFilter",
                                "HBHENoiseIsoFilter",
                                "EcalDeadCellTriggerPrimitiveFilter",
                                "BadPFMuonFilter",
                                "ecalBadCalibFilterV2"
                               ],
                  "NotRecommended" : ["BadChargedCandidateFilter",
                                      "eeBadScFilter"
                                     ],
                 },
                 "2018" :  { "isData" : ["globalSuperTightHalo2016Filter"],
                            "Common" :  ["goodVertices",
                                         "HBHENoiseFilter",
                                         "HBHENoiseIsoFilter",
                                         "EcalDeadCellTriggerPrimitiveFilter",
                                         "BadPFMuonFilter",
                                         "ecalBadCalibFilterV2"
                                        ],
                            "NotRecommended" : ["BadChargedCandidateFilter",
                                                "eeBadScFilter"
                                               ],
                           },
                } 
    Flags = FlagsDict[era]

    #2016selection required !isFake(), nDegreesOfFreedom> 4 (strictly),|z| < 24 (in cm? fractions of acentimeter?), and rho =sqrt(PV.x**2 + PV.y**2)< 2
    #Cuts are to use strictly less than and greater than, i.e. PV.ndof > minNDoF, not >=
    PVCutDict = {
            '2016':{
                'minNDoF': 4,
                'maxAbsZ': 24.0,
                'maxRho': 2
                },
            '2017':{
                'minNDoF': 4,
                'maxAbsZ': 24.0,
                'maxRho': 2
                },
            '2018':{
                'minNDoF': 4,
                'maxAbsZ': 24.0,
                'maxRho': 2
                }
        }
    PVCut = PVCutDict[era]
        
        
        

#    if "selection" in level:
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000000001), "PV NDoF > 4")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000000010), "PV |z| < 24.0")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000000100), "PV rho < 2")
#        if isData == True:
#            rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000001000), "MET globalSuperTightHalo2016Filter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000010000), "MET goodVertices")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000100000), "MET HBHENoiseFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000001000000), "MET HBHENoiseIsoFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000010000000), "MET EcalDeadCellTriggerPrimitiveFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000100000000), "MET BadPFMuonFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000001000000000), "MET ecalBadCalibFilterV2")
#    elif "baseline" in level:
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000000001), "PV NDoF > 4")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000000010), "PV |z| < 24.0")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000000100), "PV rho < 2")
#        if isData == True:
#            rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000001000), "MET globalSuperTightHalo2016Filter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000010000), "MET goodVertices")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000100000), "MET HBHENoiseFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000001000000), "MET HBHENoiseIsoFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000010000000), "MET EcalDeadCellTriggerPrimitiveFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000100000000), "MET BadPFMuonFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000001000000000), "MET ecalBadCalibFilterV2")
#    return rdf
    
#def defineEventVars(input_df):
#    rdf = input_df
#    #rdf = rdf.Define("JML_baseline_pass", "(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00001100011111111111))#Cut on MET pt, nJet, HT
#    rdf = rdf.Define("JML_baseline_pass", "(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000001111111111))#Only PV and MET filters required to pass
#    #rdf = rdf.Define("JML_selection_pass", "(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00001100011111111111))#Cut on MET pt, nJet, HT
#    rdf = rdf.Define("JML_selection_pass", "(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000001111111111))#Only PV and MET filters required to pass
#    return rdf


# In[ ]:


def fillHistos(input_df, sampleName=None, wgtVar="wgt_SUMW", isData = True, histos1D_dict=None, histos2D_dict=None, histosNS_dict=None, 
               doMuons=False, doElectrons=False, doLeptons=False, doJets=False, doWeights=False, doEventVars=False, 
               makeMountains=False, debugInfo=True, nJetsToHisto=10, useDeepCSV=False, verbose=False,
               HTCut=500, METCut=None, ZMassMETWindow=None, verbose=False
               sysVariations={"$NOMINAL": {"jet_mask": "jet_mask",
                                           "wgt_final": "wgt_nom",
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt",
                                             "jet_mass_var": "Jet_mass",
                                             "met_pt_var": "METFixEE2017_pt",
                                             "met_phi_var": "METFixEE2017_phi",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                              "_jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp",
                                             "wgt_final": "wgt_jesTotalUp",
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt_jesTotalUp",
                                             "jet_mass_var": "Jet_mass_jesTotalUp",
                                             "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                             "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                              "_jesTotalDown": {"jet_mask": "jet_mask_jesTotalDown",
                                             "wgt_final": "wgt_jesTotalDown", 
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt_jesTotalDown",
                                             "jet_mass_var": "Jet_mass_jesTotalDown",
                                             "met_pt_var": "METFixEE2017_pt_jesTotalDown",
                                             "met_phi_var": "METFixEE2017_phi_jesTotalDown",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                                     },):
    """Method to fill histograms given an input RDataFrame, input sample/dataset name, input histogram dictionaries.
    Has several options of which histograms to fill, such as Leptons, Jets, Weights, EventVars, etc.
    Types of histograms (1D, 2D, those which will not be stacked(NS - histosNS)) are filled by passing non-None
    value to that histosXX_dict variable. Internally stored with structure separating the categories of histos,
    with 'Muons,' 'Electrons,' 'Leptons,' 'Jets,' 'EventVars,' 'Weights' subcategories.
    
    ZMassMETWindow = [<invariant mass halfwidth>, <METCut>] - If in the same-flavor dilepton channel, require 
    abs(DileptonInvMass - ZMass) < ZWindowHalfWidth and MET >= METCut
    """
    
    
    if doMuons == False and doElectrons == False and doLeptons == False                and doJets == False and doWeights == False and doEventVars == False                and makeMountains == False:
        raise RuntimeError("Must select something to plot:"                               "Set do{Muons,Electrons,Leptons,Jets,Weights,EventVars,etc} = True in init method")
    
    pi = ROOT.TMath.Pi()
    #Get the list of defined columns for checks
    listOfDefinedColumns = input_df.GetDefinedColumnNames()
    #Dictionary to hold all the categorization nodes
    cat_df = collections.OrderedDict()
    #Make sure the nominal is done first so that categorization is successful
    for sysVar, sysDict in sorted(sysVariations.items(), key=lambda x: "$NOMINAL" in x[0], reverse=True):
        #skip systematic variations on data, only do the nominal
        if isData and sysVar != "$NOMINAL": 
            continue
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        #jetMask = sysDict.get("jet_mask")
        #jetPt = sysDict.get("jet_pt_var")
        #jetMass = sysDict.get("jet_mass_var")
        #Name histograms with their actual systematic variation postfix, using the convention that HISTO_NAME__nom is
        # the nominal and HISTO_NAME__$SYSTEMATIC is the variation, like so:
        syspostfix = "__nom" if sysVar == "$NOMINAL" else "_{}".format(sysVar)
        #name branches for filling with the nominal postfix if weight variations, and systematic postfix if scale variation (jes_up, etc.)
        branchpostfix = None
        if isWeightVariation:
            branchpostfix = "_nom"
        else:
            branchpostfix = sysVar.replace("$NOMINAL", "_nom")
        leppostfix = "_nom" #No variation on this yet, but just in case
        
        fillJet = "FTAJet{bpf}".format(bpf=branchpostfix)
        fillJet_pt = "FTAJet{bpf}_pt".format(bpf=branchpostfix)
        fillJet_phi = "FTAJet{bpf}_phi".format(bpf=branchpostfix)
        fillJet_eta = "FTAJet{bpf}_eta".format(bpf=branchpostfix)
        fillJet_mass = "FTAJet{bpf}_mass".format(bpf=branchpostfix)
        fillMET_pt = "FTAMET{bpf}_pt".format(bpf=branchpostfix)
        fillMET_phi = "FTAMET{bpf}_phi".format(bpf=branchpostfix)
        
        #Get the appropriate weight defined in defineFinalWeights function
        wgtVar = sysDict.get("wgt_final", "wgt_nom")
        if wgtVar not in listOfDefinedColumns:
            print("{} not found as a valid weight variation, trying something else as backup".format(wgtVar))
            if "wgt_SUMW_PU_LSF_L1PF" in listOfDefinedColumns:
                wgtVar = "wgt_SUMW_PU_LSF_L1PF"
            elif "wgt_SUMW" in listOfDefinedColumns:
                wgtVar = "wgt_SUMW"
            else:
                raise RuntimeError("Couldn't find a valid fallback weight variation in fillHistos()")
            print("{} chosen as the weight for {} variation".format(wgtVar, syspostfix))

    
        if doWeights == True:
            if histosNS_dict != None:
                if "EventVars" not in histosNS_dict:
                    histosNS_dict["EventVars"] = {}
                histosNS[name][lvl]["EventVars"]["wgt_NUMW"] = input_df.Histo1D("wgt_NUMW")
                histosNS[name][lvl]["EventVars"][wgtVar] = input_df.Histo1D(wgtVar)
            if histos1D_dict != None:
                if "EventVars" not in histos1D_dict:
                    histos1D_dict["EventVars"] = {}
                histos1D_dict["EventVars"]["wgt_diff"] = input_df.Histo1D(("wgt_diff", "(wgt_NUMW - wgt_SUMW)/wgt_SUMW", 2000, -1, 1), "wgt_diff", "1")
                histos1D_dict["EventVars"]["wgt_PU"] = input_df.Histo1D(("wgt_PU", "", 2000, 0, 5), "puWeight", "wgt_SUMW")
                histos1D_dict["EventVars"]["wgt_LSF"] = input_df.Histo1D(("wgt_LSF", "", 2000, 0, 5), "wgt_LSF", "wgt_SUMW")
                histos1D_dict["EventVars"]["wgt_L1PF"] = input_df.Histo1D(("wgt_L1PF", "", 2000, 0, 5), "L1PreFiringWeight_Nom", "wgt_SUMW")
                histos1D_dict["EventVars"]["wgt_PU_LSF_L1PF"] = input_df.Histo1D(("wgt_PU_LSF_L1PF", "", 2000, 0, 5), "wgt_PU_LSF_L1PF", "wgt_SUMW")
        if doMuons == True:
            if histos1D_dict != None:
                if "Muons" not in histos1D_dict: 
                    histos1D_dict["Muons"] = {}
                histos1D_dict["Muons"]["idx"] = input_df.Histo1D(("idx{}".format(postfix), "", 5, 0, 5), "Muon_idx", wgtVar)
                histos1D_dict["Muons"]["Gidx"] = input_df.Histo1D(("Gidx{}".format(postfix), "", 5, 0, 5), "FTAMuon{lpf}_idx", wgtVar)
                histos1D_dict["Muons"]["nMu"] = input_df.Histo1D(("nMuon{}".format(postfix), "", 5, 0, 5), "nFTAMuon{lpf}", wgtVar)
                histos1D_dict["Muons"]["nLooseMu"] = input_df.Histo1D(("nLooseMuon{}".format(postfix), "", 5, 0, 5), "nLooseFTAMuon{lpf}", wgtVar)
                histos1D_dict["Muons"]["nMediumMu"] = input_df.Histo1D(("nMediumMuon{}".format(postfix), "", 5, 0, 5), "nMediumFTAMuon{lpf}", wgtVar)
                histos1D_dict["Muons"]["pt"] = input_df.Histo1D(("Muon_pt{}".format(postfix), "", 100, 0, 500), "FTAMuon{lpf}_pt", wgtVar)
                histos1D_dict["Muons"]["eta"] = input_df.Histo1D(("Muon_eta{}".format(postfix), "", 104, -2.6, 2.6), "FTAMuon{lpf}_eta", wgtVar)
                histos1D_dict["Muons"]["phi"] = input_df.Histo1D(("Muon_phi{}".format(postfix), "", 64, -pi, pi), "FTAMuon{lpf}_phi", wgtVar)
                #histos1D_dict["Muons"]["mass"] = input_df.Histo1D(("Muon_mass{}".format(postfix), "", 50, 0, 1), "FTAMuon{lpf}_mass", wgtVar)
                histos1D_dict["Muons"]["iso"] = input_df.Histo1D(("Muon_iso{}".format(postfix), "", 8, 0, 8), "FTAMuon{lpf}_pfIsoId", wgtVar)
                histos1D_dict["Muons"]["dz"] = input_df.Histo1D(("Muon_dz{}".format(postfix), "", 100, -0.01, 0.01), "FTAMuon{lpf}_dz", wgtVar)
                histos1D_dict["Muons"]["dxy"] = input_df.Histo1D(("Muon_dxy{}".format(postfix), "", 100, -0.1, 0.1), "FTAMuon{lpf}_dxy", wgtVar)
                #histos1D_dict["Muons"]["d0"] = input_df.Histo1D(("Muon_d0{}".format(postfix), "", 100, -0.01, 0.01), "FTAMuon{lpf}_d0", wgtVar)
                histos1D_dict["Muons"]["ip3d"] = input_df.Histo1D(("Muon_ip3d{}".format(postfix), "", 100, 0, 0.01), "FTAMuon{lpf}_ip3d", wgtVar)
                histos1D_dict["Muons"]["pfRelIso03_all"] = input_df.Histo1D(("Muon_pfRelIso03_all{}".format(postfix), "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_all", wgtVar)
                histos1D_dict["Muons"]["pfRelIso03_chg"] = input_df.Histo1D(("Muon_pfRelIso03_chg{}".format(postfix), "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_chg", wgtVar)
                histos1D_dict["Muons"]["pfRelIso04_all"] = input_df.Histo1D(("Muon_pfRelIso04_all{}".format(postfix), "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso04_all", wgtVar)
            if histos2D_dict != None:
                if "Muons" not in histos2D_dict:
                    histos2D_dict["Muons"] = {}
                histos2D_dict["Muons"]["eta_phi"] = input_df.Histo2D(("Muon_eta_phi{}".format(postfix), "",
                                                                      104, -2.6, 2.6,
                                                                      64, -pi, pi),
                                                                     "FTAMuon{lpf}_eta", "FTAMuon{lpf}_phi", wgtVar)
                histos2D_dict["Muons"]["dz_ip3d"] = input_df.Histo2D(("Muon_dz_ip3d{}".format(postfix), "",
                                                                      100, -0.01, 0.01,
                                                                      100, 0, 0.01),
                                                                     "FTAMuon{lpf}_dz", "FTAMuon{lpf}_ip3d", wgtVar)
        if doElectrons == True:
            if histos1D_dict != None:
                if "Electrons" not in histos1D_dict: 
                    histos1D_dict["Electrons"] = {}
                histos1D_dict["Electrons"]["nEl"] = input_df.Histo1D(("nElectron{}".format(postfix), "", 5, 0, 5), "nFTAElectron{lpf}", wgtVar)
                histos1D_dict["Electrons"]["nLooseEl"] = input_df.Histo1D(("nLooseElectron{}".format(postfix), "", 5, 0, 5), "nLooseFTAElectron{lpf}", wgtVar)
                histos1D_dict["Electrons"]["nMediumEl"] = input_df.Histo1D(("nMediumElectron{}".format(postfix), "", 5, 0, 5), "nMediumFTAElectron{lpf}", wgtVar)
                histos1D_dict["Electrons"]["pt"] = input_df.Histo1D(("Electron_pt{}".format(postfix), "", 100, 0, 500), "FTAElectron{lpf}_pt", wgtVar)
                histos1D_dict["Electrons"]["eta"] = input_df.Histo1D(("Electron_eta{}".format(postfix), "", 104, -2.6, 2.6), "FTAElectron{lpf}_eta", wgtVar)
                histos1D_dict["Electrons"]["phi"] = input_df.Histo1D(("Electron_phi{}".format(postfix), "", 64, -pi, pi), "FTAElectron{lpf}_phi", wgtVar)
                #histos1D_dict["Electrons"]["mass"] = input_df.Histo1D(("Electron_mass{}".format(postfix), "", 50, 0, 1), "FTAElectron{lpf}_mass", wgtVar)
                histos1D_dict["Electrons"]["dz"] = input_df.Histo1D(("Electron_dz{}".format(postfix), "", 100, -0.01, 0.01), "FTAElectron{lpf}_dz", wgtVar)
                #histos1D_dict["Electrons"]["d0"] = input_df.Histo1D(("Electron_d0{}".format(postfix), "", 100, 0, 0.01), "FTAElectron{lpf}_d0", wgtVar)
                histos1D_dict["Electrons"]["ip3d"] = input_df.Histo1D(("Electron_ip3d{}".format(postfix), "", 100, 0, 0.01), "FTAElectron{lpf}_ip3d", wgtVar)
                histos1D_dict["Electrons"]["pfRelIso03_all"] = input_df.Histo1D(("Electron_pfRelIso03_all{}".format(postfix), "", 100, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_all", wgtVar)
                histos1D_dict["Electrons"]["pfRelIso03_chg"] = input_df.Histo1D(("Electron_pfRelIso03_chg{}".format(postfix), "", 100, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_chg", wgtVar)
                histos1D_dict["Electrons"]["cutBased"] = input_df.Histo1D(("Electron_cutBased{}".format(postfix), "", 5, 0, 5), "FTAElectron{lpf}_cutBased", wgtVar)
            if histos2D_dict != None:
                if "Electrons" not in histos2D_dict: 
                    histos2D_dict["Electrons"] = {}
                histos2D_dict["Electrons"]["eta_phi"] = input_df.Histo2D(("Electron_eta_phi{}".format(postfix), "",
                                                                          104, -2.6, 2.6,
                                                                          64, -pi, pi),
                                                                         "FTAElectron{lpf}_eta", "FTAElectron{lpf}_phi", wgtVar)
                histos2D_dict["Electrons"]["dz_ip3d"] = input_df.Histo2D(("Electron_dz_ip3d{}".format(postfix), "",
                                                                          100, -0.01, 0.01,
                                                                          100, 0, 0.01),
                                                                         "FTAElectron{lpf}_dz", "FTAElectron{lpf}_ip3d", wgtVar)
        if doLeptons == True:
            if histos1D_dict != None:
                if "Leptons" not in histos1D_dict: 
                    histos1D_dict["Leptons"] = {}
                histos1D_dict["Leptons"]["pt_LeadLep"] = input_df                        .Histo1D(("FTALepton{lpf}_pt_LeadLep{}".format(postfix), "", 100, 0, 500),"FTALepton{lpf}_pt_LeadLep", wgtVar)
                histos1D_dict["Leptons"]["pt_SubleadLep"] = input_df                        .Histo1D(("FTALepton{lpf}_pt_SubleadLep{}".format(postfix), "", 100, 0, 500),"FTALepton{lpf}_pt_SubleadLep", wgtVar)
                histos1D_dict["Leptons"]["eta"] = input_df                        .Histo1D(("FTALepton{lpf}_eta{}".format(postfix), "", 104, -2.6, 2.6),"FTALepton{lpf}_eta", wgtVar)
                histos1D_dict["Leptons"]["phi"] = input_df                        .Histo1D(("FTALepton{lpf}_phi{}".format(postfix), "", 64, -pi, pi),"FTALepton{lpf}_phi", wgtVar)
                histos1D_dict["Leptons"]["nLepton"] = input_df                        .Histo1D(("nLepton{}".format(postfix), "", 5, 0, 5), "nFTALepton{lpf}", wgtVar)
                histos1D_dict["Leptons"]["pdgId"] = input_df                        .Histo1D(("Lepton_pdgId{}".format(postfix), "", 32, -16, 16), "FTALepton{lpf}_pdgId", wgtVar)
                histos1D_dict["Leptons"]["jetIdx"] = input_df                        .Histo1D(("Lepton_jetIdx{}".format(postfix), "", 20, 0, 20), "FTALepton{lpf}_jetIdx", wgtVar)
                #histos1D_dict["Leptons"]["LepSF"] = input_df\
                #        .Histo1D(("Lepton_SF_({})".format("wgt_SUMW_PU:HARDCODED"), "", 100, 0.93, 1.03), "FTALepton{lpf}_SF_nom", "wgt_SUMW_PU")
                #histos1D_dict["Leptons"]["LSF"] = input_df\
                #        .Histo1D(("LSF_({})".format("wgt_SUMW_PU:HARDCODED"), "", 200, 0.80, 1.1), "wgt_LSF", "wgt_SUMW_PU")
                #histos1D_dict["Leptons"]["SPL_SP"] = input_df\
                #        .Histo1D(("SPL_SP_({})".format("wgt_SUMW_PU:HARDCODED"), "", 200, 0.80, 1.1), "SPL_SP", "wgt_SUMW_PU")
                #histos1D_dict["Leptons"]["LepSF"] = input_df.Histo1D("FTALepton{lpf}_SF_nom")#, "wgt_SUMW_PU")
                #histos1D_dict["Leptons"]["LSF"] = input_df.Histo1D("wgt_LSF")#, "wgt_SUMW_PU")
                #histos1D_dict["Leptons"]["SPL_SP"] = input_df.Histo1D("SPL_SP")#, "wgt_SUMW_PU")
                #histos1D_dict["Leptons"]["SUMW_PU"] = input_df.Histo1D("wgt_SUMW_PU")#, "wgt_SUMW_PU")
                #histos1D_dict["Leptons"]["SUMW_PU_LSF"] = input_df.Histo1D("wgt_SUMW_PU_LSF")#, "wgt_SUMW_PU")
                #histos1D_dict["Leptons"]["PU"] = input_df.Histo1D("puWeight")#, "wgt_SUMW_PU")
        if doJets == True:
            if histos1D_dict != None:
                if "Jets" not in histos1D_dict:
                    histos1D_dict["Jets"] = {}
                histos1D_dict["Jets"]["pt"] = input_df.Histo1D(("Jet_pt{}".format(postfix), "", 100, 0, 500), fillJet_pt, wgtVar)
                for x in xrange(nJetsToHisto):
                    histos1D_dict["Jets"]["pt_jet{}".format(x+1)] = input_df.Histo1D(("Jet_pt_jet{}({})".format(x+1, wgtVar), "", 100, 0, 500), "Jet{bpf}_pt_jet{}".format(x+1), wgtVar)
                    histos1D_dict["Jets"]["eta_jet{}".format(x+1)] = input_df.Histo1D(("Jet_eta_jet{}({})".format(x+1, wgtVar), "", 104, -2.6, 2.6), "Jet{bpf}_eta_jet{}".format(x+1), wgtVar)
                    histos1D_dict["Jets"]["phi_jet{}".format(x+1)] = input_df.Histo1D(("Jet_phi_jet{}({})".format(x+1, wgtVar), "", 64, -pi, pi), "Jet{bpf}_phi_jet{}".format(x+1), wgtVar)
                histos1D_dict["Jets"]["eta"] = input_df.Histo1D(("Jet_eta{}".format(postfix), "", 104, -2.6, 2.6), fillJet_eta, wgtVar)
                histos1D_dict["Jets"]["phi"] = input_df.Histo1D(("Jet_phi{}".format(postfix), "", 64, -pi, pi), fillJet_phi, wgtVar)
                histos1D_dict["Jets"]["mass"] = input_df.Histo1D(("Jet_mass{}".format(postfix), "", 100, 0, 500), fillJet_mass, wgtVar)
                histos1D_dict["Jets"]["jetId"] = input_df.Histo1D(("Jet_jetId{}".format(postfix), "", 8, 0, 8), "Jet{bpf}_jetId", wgtVar) #FIXME: not based on variation... okay? maybe not with masks...
                #histos1D_dict["Jets"]["btagDeepB_LeadtagJet"] = input_df.Histo1D(("Jet_btagDeepB_LeadtagJet{}".format(postfix), "", 101, -0.01, 1), "Jet{bpf}_btagDeepB_LeadtagJet", wgtVar)
                #histos1D_dict["Jets"]["btagDeepB_SubleadtagJet"] = input_df.Histo1D(("Jet_btagDeepB_SubleadtagJet{}".format(postfix), "", 101, -0.01, 1), "Jet{bpf}_btagDeepB_SubleadtagJet", wgtVar)
                #histos1D_dict["Jets"]["btagDeepJet_LeadtagJet"] = input_df.Histo1D(("Jet_btagDeepJetB_LeadtagJet{}".format(postfix), "", 101, -0.01, 1), "Jet{bpf}_btagDeepFlavB_sorted_LeadtagJet", wgtVar)
                #histos1D_dict["Jets"]["btagDeepJet_SubleadtagJet"] = input_df.Histo1D(("Jet_btagDeepJetB_SubleadtagJet{}".format(postfix), "", 101, -0.01, 1), "Jet{bpf}_btagDeepFlavB_sorted_SubleadtagJet", wgtVar)
                #histos1D_dict["Jets"]["nMediumCSVv2"] = input_df.Histo1D(("nJet_MediumCSVv2{}".format(postfix), "", 10, 0, 10), "nJet{bpf}_MediumCSVv2", wgtVar)
                histos1D_dict["Jets"]["nMediumDeepCSV"] = input_df.Histo1D(("nJet_MediumDeepCSV{}".format(postfix), "", 10, 0, 10), "nJet{bpf}_MediumDeepCSV", wgtVar)
                histos1D_dict["Jets"]["nMediumDeepJet"] = input_df.Histo1D(("nJet_MediumDeepJet{}".format(postfix), "", 10, 0, 10), "nJet{bpf}_MediumDeepJet", wgtVar)
                histos1D_dict["Jets"]["nJet"] = input_df.Histo1D(("nJet{}".format(postfix), "", 15, 0, 15), "nJet{bpf}", wgtVar)
                histos1D_dict["Jets"]["dR_Jet_Mu_leading"] = input_df.Histo1D(("dR_Jet_Mu_leading{}".format(postfix), "dR(Jet, #mu_{leading}); dR; Events)", 40, 0, 0.8), "dR_Jet_Mu_leading", wgtVar)
                histos1D_dict["Jets"]["dR_Jet_Mu_sublead"] = input_df.Histo1D(("dR_Jet_Mu_sublead{}".format(postfix), "dR(Jet, #mu_{subleading}); dR; Events)", 40, 0, 0.8), "dR_Jet_Mu_sublead", wgtVar)
                histos1D_dict["Jets"]["dR_Jet_El_leading"] = input_df.Histo1D(("dR_Jet_El_leading{}".format(postfix), "dR(Jet, #e_{leading}); dR; Events)", 40, 0, 0.8), "dR_Jet_El_leading", wgtVar)
                histos1D_dict["Jets"]["dR_Jet_El_sublead"] = input_df.Histo1D(("dR_Jet_El_sublead{}".format(postfix), "dR(Jet, #e_{subleading}); dR; Events)", 40, 0, 0.8), "dR_Jet_El_sublead", wgtVar)
            
                if debugInfo == True:
                    #histos1D_dict["Jets"]["DiffMaskVsALT"] = input_df.Histo1D(("DiffMaskVsALT", "", 10, -10, 10), "DiffMaskVsALT", wgtVar)
                    #histos1D_dict["Jets"]["DiffnJet"] = input_df.Histo1D(("DiffnJet", "", 10, -10, 10), "DiffnJet", wgtVar)
                    histos1D_dict["Jets"]["DeepJetSorted"] = input_df.Histo1D("DeepJetSorted", wgtVar)
                    histos1D_dict["Jets"]["DeepJetLeadtagMinusSubleadtag"] = input_df.Histo1D(("DeepJetLeadtagMinusSubleadtag", "DeepJet(Leadtag - Subleadtag);;Events", 100, -1, 1), "DeepJet0Minus1", wgtVar)
                    histos1D_dict["Jets"]["MediumDeepJetSorted"] = input_df.Histo1D("MediumDeepJetSorted", wgtVar)
                    #histos1D_dict["Jets"]["MediumDeepJet0Minus1"] = input_df.Histo1D(("MediumDeepJet0Minus1", "", 100, -1, 1), "MediumDeepJet0Minus1", wgtVar)
                    #histos1D_dict["Jets"]["btagDeepJet_jet0Med"] = input_df.Histo1D(("Jet_btagDeepJetB_jet0Med{}".format(postfix), "", 102, -0.02, 1), "Jet{bpf}_btagDeepFlavB_jet0Med", wgtVar)
                    #histos1D_dict["Jets"]["btagDeepJet_jet1Med"] = input_df.Histo1D(("Jet_btagDeepJetB_jet1Med{}".format(postfix), "", 102, -0.02, 1), "Jet{bpf}_btagDeepFlavB_jet1Med", wgtVar)
                    #histos1D_dict["Jets"]["nJetNUMW"] = input_df.Histo1D(("nJet_NUMW", "", 15, 0, 15), "nJet{bpf}", "wgt_NUMW_V2")
                    #histos1D_dict["Jets"]["nJetSUMW_PU"] = input_df.Histo1D(("nJet_SUMW_PU", "", 15, 0, 15), "nJet{bpf}", "wgt_SUMW_PU")
                    #histos1D_dict["Jets"]["nJetSUMW_LSF"] = input_df.Histo1D(("nJet_SUMW_LSF", "", 15, 0, 15), "nJet{bpf}", "wgt_SUMW_LSF")
                    #histos1D_dict["Jets"]["ptALT"] = input_df.Histo1D(("Jet_ptALT{}".format(postfix), "", 100, 0, 500), "Jet{bpf}_ptALT", wgtVar)
                    #histos1D_dict["Jets"]["etaALT"] = input_df.Histo1D(("Jet_etaALT{}".format(postfix), "", 104, -2.6, 2.6), "Jet{bpf}_etaALT", wgtVar)
                    #histos1D_dict["Jets"]["phiALT"] = input_df.Histo1D(("Jet_phiALT{}".format(postfix), "", 64, -pi, pi), "Jet{bpf}_phiALT", wgtVar)
                    #histos1D_dict["Jets"]["massALT"] = input_df.Histo1D(("Jet_massALT{}".format(postfix), "", 100, 0, 500), "Jet{bpf}_massALT", wgtVar)
                    #histos1D_dict["Jets"]["jetIdALT"] = input_df.Histo1D(("Jet_jetIdALT{}".format(postfix), "", 8, 0, 8), "Jet{bpf}_jetIdALT", wgtVar)
        
            if histos2D_dict != None:
                if "Jets" not in histos2D_dict:
                    histos2D_dict["Jets"] = {}
                histos2D_dict["Jets"]["eta_phi"] = input_df.Histo2D(("Jet_eta_phi{}".format(postfix), "",
                                                                     104, -2.6, 2.6,
                                                                     64, -pi, pi),
                                                                    fillJet_eta, fillJet_phi, wgtVar)
        if doEventVars == True:
            if histos1D_dict != None:
                if "EventVars" not in histos1D_dict:
                    histos1D_dict["EventVars"] = {}
                #histos1D_dict["EventVars"]["JML_baseline"] = input_df.Histo1D(("JML_baseline{}".format(postfix), "", 2,0,2), "JML_baseline_pass", wgtVar)
                #histos1D_dict["EventVars"]["JML_selection"] = input_df.Histo1D(("JML_selection{}".format(postfix), "", 2,0,2), "JML_selection_pass", wgtVar)
                #histos1D_dict["EventVars"]["HT_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_HT_baseline{}".format(postfix), "", 100,400,1400), "ESV_JetMETLogic_HT_baseline", wgtVar)
                #histos1D_dict["EventVars"]["H_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_H_baseline{}".format(postfix), "", 100,400,1400), "ESV_JetMETLogic_H_baseline", wgtVar)
                #histos1D_dict["EventVars"]["HT2M_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_HT2M_baseline{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_HT2M_baseline", wgtVar)
                #histos1D_dict["EventVars"]["H2M_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_H2M_baseline{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_H2M_baseline", wgtVar)
                #histos1D_dict["EventVars"]["HTb_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_HTb_baseline{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_HTb_baseline", wgtVar)
                #histos1D_dict["EventVars"]["HTH_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_HTH_baseline{}".format(postfix), "", 100,0,1), "ESV_JetMETLogic_HTH_baseline", wgtVar)
                #histos1D_dict["EventVars"]["HTRat_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_HTRat_baseline{}".format(postfix), "", 100,0,1), "ESV_JetMETLogic_HTRat_baseline", wgtVar)
                #histos1D_dict["EventVars"]["dRbb_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_dRbb_baseline{}".format(postfix), "", 64,0,2*pi), "ESV_JetMETLogic_dRbb_baseline", wgtVar)
                #histos1D_dict["EventVars"]["DiLepMass_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_DiLepMass_baseline{}".format(postfix), "", 100,0,500), "ESV_JetMETLogic_DiLepMass_baseline", wgtVar)
                #histos1D_dict["EventVars"]["HT_selection"] = input_df.Histo1D(("ESV_JetMETLogic_HT_selection{}".format(postfix), "", 100,400,1400), "ESV_JetMETLogic_HT_selection", wgtVar)
                #histos1D_dict["EventVars"]["H_selection"] = input_df.Histo1D(("ESV_JetMETLogic_H_selection{}".format(postfix), "", 100,400,1400), "ESV_JetMETLogic_H_selection", wgtVar)
                #histos1D_dict["EventVars"]["HT2M_selection"] = input_df.Histo1D(("ESV_JetMETLogic_HT2M_selection{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_HT2M_selection", wgtVar)
                #histos1D_dict["EventVars"]["H2M_selection"] = input_df.Histo1D(("ESV_JetMETLogic_H2M_selection{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_H2M_selection", wgtVar)
                #histos1D_dict["EventVars"]["HTb_selection"] = input_df.Histo1D(("ESV_JetMETLogic_HTb_selection{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_HTb_selection", wgtVar)
                #histos1D_dict["EventVars"]["HTH_selection"] = input_df.Histo1D(("ESV_JetMETLogic_HTH_selection{}".format(postfix), "", 100,0,1), "ESV_JetMETLogic_HTH_selection", wgtVar)
                #histos1D_dict["EventVars"]["HTRat_selection"] = input_df.Histo1D(("ESV_JetMETLogic_HTRat_selection{}".format(postfix), "", 100,0,1), "ESV_JetMETLogic_HTRat_selection", wgtVar)
                #histos1D_dict["EventVars"]["dRbb_selection"] = input_df.Histo1D(("ESV_JetMETLogic_dRbb_selection{}".format(postfix), "", 64,0,2*pi), "ESV_JetMETLogic_dRbb_selection", wgtVar)
                #histos1D_dict["EventVars"]["DiLepMass_selection"] = input_df.Histo1D(("ESV_JetMETLogic_DiLepMass_selection{}".format(postfix), "", 100,0,500), "ESV_JetMETLogic_DiLepMass_selection", wgtVar)
                histos1D_dict["EventVars"]["MET_pt"] = input_df.Histo1D(("MET_xycorr_pt{}".format(postfix), "", 100,30,1030), fillMET_pt, wgtVar)
                histos1D_dict["EventVars"]["MET_phi"] = input_df.Histo1D(("MET_xycorr_phi{}".format(postfix), "", 100,-pi,pi), fillMET_phi, wgtVar)
                histos1D_dict["EventVars"]["HT"] = input_df.Histo1D(("HT{}".format(postfix), "", 130,400,1700), "FTAJet{bpf}_HT", wgtVar)
                histos1D_dict["EventVars"]["H"] = input_df.Histo1D(("H{}".format(postfix), "", 160,400,2000), "FTAJet{bpf}_H", wgtVar)
                histos1D_dict["EventVars"]["HT2M"] = input_df.Histo1D(("HT2M{}".format(postfix), "", 100,0,1000), "FTAJet{bpf}_HT2M", wgtVar)
                histos1D_dict["EventVars"]["H2M"] = input_df.Histo1D(("H2M{}".format(postfix), "", 150,0,1500), "FTAJet{bpf}_H2M", wgtVar)
                histos1D_dict["EventVars"]["HTb"] = input_df.Histo1D(("HTb{}".format(postfix), "", 100,0,1000), "FTAJet{bpf}_HTb", wgtVar)
                histos1D_dict["EventVars"]["HTH"] = input_df.Histo1D(("HTH{}".format(postfix), "", 100,0,1), "FTAJet{bpf}_HTH", wgtVar)
                histos1D_dict["EventVars"]["HTRat"] = input_df.Histo1D(("HTRat{}".format(postfix), "", 100,0,1), "FTAJet{bpf}_HTRat", wgtVar)
                histos1D_dict["EventVars"]["dRbb"] = input_df.Histo1D(("dRbb{}".format(postfix), "", 64,0,2*pi), "FTAJet{bpf}_dRbb", wgtVar)
                histos1D_dict["EventVars"]["dPhibb"] = input_df.Histo1D(("dPhibb{}".format(postfix), "", 64,-pi,pi), "FTAJet{bpf}_dPhibb", wgtVar)
                histos1D_dict["EventVars"]["dEtabb"] = input_df.Histo1D(("dEtabb{}".format(postfix), "", 50,0,5), "FTAJet{bpf}_dEtabb", wgtVar)
                histos1D_dict["EventVars"]["dRll"] = input_df.Histo1D(("dRll{}".format(postfix), "", 64,0,2*pi), "FTALepton{lpf}_dRll", wgtVar)
                histos1D_dict["EventVars"]["dPhill"] = input_df.Histo1D(("dPhill{}".format(postfix), "", 64,-pi,pi), "FTALepton{lpf}_dPhill", wgtVar)
                histos1D_dict["EventVars"]["dEtall"] = input_df.Histo1D(("dEtall{}".format(postfix), "", 50,0,5), "FTALepton{lpf}_dEtall", wgtVar)
                histos1D_dict["EventVars"]["MTofMETandEl"] = input_df.Histo1D(("MTofMETandEl{}".format(postfix), "", 100, 0, 200), "MTofMETandEl", wgtVar)
                histos1D_dict["EventVars"]["MTofMETandMu"] = input_df.Histo1D(("MTofMETandMu{}".format(postfix), "", 100, 0, 200), "MTofMETandMu", wgtVar)
                histos1D_dict["EventVars"]["MTofElandMu"] = input_df.Histo1D(("MTofElandMu{}".format(postfix), "", 100, 0, 200), "MTofElandMu", wgtVar)
                #histos1D_dict["EventVars"]["MTMasslessCheck"] = input_df.Histo1D(("MTMasslessCheck{}".format(postfix), "", 100, 0, 200), "MTMasslessCheck", wgtVar)
                #histos1D_dict["EventVars"]["MTCrossCheck"] = input_df.Histo1D(("MTCrossCheck{}".format(postfix), "", 100, 0, 200), "MTCrossCheck", wgtVar)
                #histos1D_dict["EventVars"]["MTCrossCheckDifference"] = input_df.Histo1D(("MTCrossCheckDifference{}".format(postfix), "", 100, 0, 10), "MTCrossCheckDifference", wgtVar)
                #histos1D_dict["EventVars"]["MTCrossCheckMasslessDifference"] = input_df.Histo1D(("MTCrossCheckMasslessDifference{}".format(postfix), "", 100, 0, 0.02), "MTCrossCheckMasslessDifference", wgtVar)
                histos1D_dict["EventVars"]["PV_npvsGood"] = input_df.Histo1D(("PV_npvsGood{}".format(postfix), "", 100, 0, 100), "PV_npvsGood", wgtVar)
                histos1D_dict["EventVars"]["PV_npvs"] = input_df.Histo1D(("PV_npvs{}".format(postfix), "", 150, 0, 150), "PV_npvs", wgtVar)
                if isData == False:
                    histos1D_dict["EventVars"]["Pileup_nTrueInt"] = input_df.Histo1D(("Pileup_TrueInt{}".format(postfix), ";Pileup_TrueInt;Events", 150, 0, 150), "Pileup_nTrueInt", wgtVar)
                    histos1D_dict["EventVars"]["Pileup_nTrueInt_XS"] = input_df.Histo1D(("Pileup_TrueInt_({})".format("wgt_SUMW"), ";Pileup_TrueInt;Events", 150, 0, 150), "Pileup_nTrueInt", "wgt_SUMW")
                    histos1D_dict["EventVars"]["Pileup_nPU_XS"] = input_df.Histo1D(("Pileup_nPU_({})".format("wgt_SUMW"), ";Pileup_nPU;Events", 150, 0, 150), "Pileup_nPU", "wgt_SUMW")
                    histos1D_dict["EventVars"]["Pileup_nPU"] = input_df.Histo1D(("Pileup_nPU{}".format(postfix), ";Pileup_nPU;Events", 150, 0, 150), "Pileup_nPU", wgtVar)
            
            if histos2D_dict != None:
                if "EventVars" not in histos2D_dict:
                    histos2D_dict["EventVars"] = {}
                if isData == False:
                    histos2D_dict["EventVars"]["npvsGood_vs_nTrueInt"] = input_df.Histo2D(("npvsGood_vs_nTrueInt{}".format(postfix), ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvsGood", wgtVar)
                    histos2D_dict["EventVars"]["npvsGood_vs_nPU"] = input_df.Histo2D(("npvsGood_vs_nPU{}".format(postfix), ";nPU;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvsGood", wgtVar)
                    histos2D_dict["EventVars"]["npvs_vs_nTrueInt"] = input_df.Histo2D(("npvs_vs_nTrueInt{}".format(postfix), ";nTrueInt;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvs", wgtVar)
                    histos2D_dict["EventVars"]["npvs_vs_nPU"] = input_df.Histo2D(("npvs_vs_nPU{}".format(postfix), ";nPU;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvs", wgtVar)
                
                if debugInfo == True:
                    #histos1D_dict["EventVars"]["Jet{bpf}_HT_Match"] = input_df.Histo1D(("Jet{bpf}_HT_Match{}".format(postfix), "", 2,0,2), "Jet{bpf}_HT_matches", wgtVar)
                    pass
            
        if makeMountains == True:
            if useDeepCSV == True:
                tagger = "CSV"
            else:
                tagger = "Jet"
            theCatsL0 = collections.OrderedDict()#Baseline nJet selection (inclusive!) for each systematic scale variation
            theCatsL1 = collections.OrderedDict() #Next level of selection, like nJet categories. If we need nBTag inclusive, they'll have to go here
            theCatsL2 = collections.OrderedDict() #Next level of selection, i.e. nBTag categories. 
            theCatsL0["Inclusive{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} >= 4".format(bpf=branchpostfix)
            
            theCatsL1["nMediumDeep{tag}B0{bpf}".format(tag=tagger, bpf=branchpostfix)] = "nMediumDeep{tag}B{bpf} == 0".format(tag=tagger, bpf=branchpostfix)
            theCatsL1["nMediumDeep{tag}B1{bpf}".format(tag=tagger, bpf=branchpostfix)] = "nMediumDeep{tag}B{bpf} == 1".format(tag=tagger, bpf=branchpostfix)
            theCatsL1["nMediumDeep{tag}B2{bpf}".format(tag=tagger, bpf=branchpostfix)] = "nMediumDeep{tag}B{bpf} == 2".format(tag=tagger, bpf=branchpostfix)
            theCatsL1["blind_nMediumDeep{tag}B3{bpf}".format(tag=tagger, bpf=branchpostfix)] = "nMediumDeep{tag}B{bpf} == 3".format(tag=tagger, bpf=branchpostfix)
            theCatsL1["blind_nMediumDeep{tag}B4+{bpf}".format(tag=tagger, bpf=branchpostfix)] = "nMediumDeep{tag}B{bpf} >= 4".format(tag=tagger, bpf=branchpostfix)
            
            theCatsL2["nJet4{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} == 4".format(bpf=branchpostfix)
            theCatsL2["nJet5{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} == 5".format(bpf=branchpostfix)
            theCatsL2["blind_nJet6{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} == 6".format(bpf=branchpostfix)
            theCatsL2["blind_nJet7{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} == 7".format(bpf=branchpostfix)
            theCatsL2["blind_nJet8+{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} >= 8".format(bpf=branchpostfix)
            
            #Don't redefine the nodes by accident! Do not redo for weight variations
            rdf = input_df
            if HTCut:
                if verbose:
                    print("Filtering Events: HT{bpf} >= {cut}".format(bpf=branchpostfix, cut=HTCut))
                rdf = rdf.Filter("HT{bpf} >= {cut}".format(bpf=branchpostfix, cut=HTCut),
                                 "HT{bpf} >= {cut}".format(bpf=branchpostfix, cut=HTCut)
                                )
            if ZMassMETWindow:
                if verbose:
                    print("Filtering Events: {met} >= {metcut}".format(met=fillMET_pt, metcut=ZMassMETWindow[1]))
                    print("Filtering Events: (FTAElectron{lpf}_InvariantMass > 0 && abs(FTAElectron{lpf}_InvariantMass - 91.2) < {zwidth}) || "                                 "(FTAMuon{lpf}_InvariantMass > 0 && abs(FTAMuon{lpf}_InvariantMass - 91.2) < {zwidth}) || "                                 "(FTAElectron{lpf}_InvariantMass < 0 && FTAMuon{lpf}_InvariantMass < 0".format(lpf=leppostfix,
                                                                                                                zwidth=ZMassMETWindow[0]
                                                                                                               )
                         )
                rdf = rdf.Filter("{met} >= {metcut} || (FTAElectron{lpf}_InvariantMass < 0 && FTAMuon{lpf}_InvariantMass < 0"                                 .format(lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1]),
                                 "MET >= {metcut}".format(metcut=ZMassMETWindow[1])
                                )
                rdf = rdf.Filter("(FTAElectron{lpf}_InvariantMass > 0 && abs(FTAElectron{lpf}_InvariantMass - 91.2) < {zwidth}) || "                                 "(FTAMuon{lpf}_InvariantMass > 0 && abs(FTAMuon{lpf}_InvariantMass - 91.2) < {zwidth}) || "                                 "(FTAElectron{lpf}_InvariantMass < 0 && FTAMuon{lpf}_InvariantMass < 0".format(lpf=leppostfix,
                                                                                                                zwidth=ZMassMETWindow[0]
                                                                                                               ),
                                 "abs(Dilepton Invariant Mass - Z_mass) < {zwidth}".format(zwidth=ZMassMETWindow[0])
                                )
            if not isWeightVariation:
                for ck0, cs0 in theCatsL0.items():
                    #Strip the FourTopAnalysis- (FTA) from the collection strings when naming the filters
                    if ck0 in cat_df:
                        print("ERROR! Attempted redefinition of the filter node for categorization. Check logic")
                        continue
                    cat_df[ck0] = rdf.Filter(cs0, cs0.replace("FTA", ""))
                    for ck1, cs1 in theCatsL1.items():
                        #Strip the FourTopAnalysis- (FTA) from the collection strings when naming the filters
                        cat_df[ck1] = cat_df[ck0].Filter(cs1, cs1.replace("FTA", ""))
                        for ck2, cs2 in theCatsL2.items():
                            l1 = ck1.replace("blind_", "").replace("{bpf}".format(bpf=branchpostfix), "")
                            l2 = ck2.replace("blind_", "").replace("{bpf}".format(bpf=branchpostfix), "")
                            if "nJet7" in l2 or "nJet8+" in l2 or "nMediumDeep{tag}B3".format(tag=tagger) in l1 or "nMediumDeep{tag}B4" in l1:
                                #Blind these regions in the cross-group!
                                cknest = "blind_{c1}_{c2}_{bpf}".format(c1=l2, c2=l1, bpf=branchpostfix)
                            else:
                                cknest = "{c1}_{c2}_{bpf}".format(c1=l2, c2=l1, bpf=branchpostfix)
                            #Strip the FourTopAnalysis- (FTA) from the collection strings when naming the filters
                            cat_df[cknest] = cat_df[ck1].Filter(cs2, "{} && {}".format(cs1.replace("FTA", ""), cs2.replace("FTA", "")))
                                                                
        
            if histos1D_dict != None:
                if "sysVar{spf}".format(spf=syspostfix) not in histos1D_dict:
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)] = {}
                for tc in cat_df.keys(): 
                    if tc not in histos1D_dict["sysVar{spf}".format(spf=syspostfix)]: 
                        histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc] = {}
                for tc, node in cat_df.items():
                    if verbose:
                        print("Histogramming the {} node".format(tc))
                    tcn = tc#.replace("blind_", "") #FIXME do I want blind stripped with new convention for naming?
                    for x in xrange(nJetsToHisto):
                        #FIXME: None of these are based upon jet scale variations, yet!
                        histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_pt_jet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_pt_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 100, 0, 500), "{fj}_pt_jet{n}".format(fj=fillJet, n=x+1), wgtVar)
                        histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_eta_jet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_eta_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 104, -2.6, 2.6), "{fj}_eta_jet{n}".format(fj=fillJet, n=x+1), wgtVar)
                        histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_phi_jet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_phi_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 64, -pi, pi), "{fj}_phi_jet{n}".format(fj=fillJet, n=x+1), wgtVar)
                        histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_DeepCSVB_jet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_DeepCSVB_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 100, 0.0, 1.0), "{fj}_DeepCSVB_jet{n}".format(fj=fillJet, n=x+1), wgtVar)
                        histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_DeepJetB_jet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_DeepJetB_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 100, 0.0, 1.0), "{fj}_DeepJetB_jet{n}".format(fj=fillJet, n=x+1), wgtVar)
                        histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_DeepCSVB_sortedjet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_DeepCSVB_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 100, 0.0, 1.0), "{fj}_DeepCSVB_sortedjet{n}".format(fj=fillJet, n=x+1), wgtVar)
                        histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_DeepJetB_sortedjet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_DeepJetB_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 100, 0.0, 1.0), "{fj}_DeepJetB_sortedjet{n}".format(fj=fillJet, n=x+1), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MET_pt"] = cat_df[tc].Histo1D(("{name}__{cat}__MET_pt_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1000), fillMET_pt, wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MET_phi"] = cat_df[tc].Histo1D(("{name}__{cat}__MET_phi_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,-pi,pi), fillMET_phi, wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_all"] = cat_df[tc].Histo1D(("{name}__{cat}__Muon_pfRelIso03_all_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_all".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_chg"] = cat_df[tc].Histo1D(("{name}__{cat}__Muon_pfRelIso03_chg_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_chg".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso04_all"] = cat_df[tc].Histo1D(("{name}__{cat}__Muon_pfRelIso04_all_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 0.2), "FTAMuon{lpf}_pfRelIso04_all".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_all"] = cat_df[tc].Histo1D(("{name}__{cat}__Electron_pfRelIso03_all_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_all".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_chg"] = cat_df[tc].Histo1D(("{name}__{cat}__Electron_pfRelIso03_chg_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_chg".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["HT"] = cat_df[tc].Histo1D(("{name}__{cat}__HT_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 30,400,2000), "HT{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["H"] = cat_df[tc].Histo1D(("{name}__{cat}__H_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 30,400,2000), "H{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["HT2M"] = cat_df[tc].Histo1D(("{name}__{cat}__HT2M_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1000), "HT2M{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["H2M"] = cat_df[tc].Histo1D(("{name}__{cat}__H2M_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1500), "H2M{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["HTb"] = cat_df[tc].Histo1D(("{name}__{cat}__HTb_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1000), "HTb{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["HTH"] = cat_df[tc].Histo1D(("{name}__{cat}__HTH_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1), "HTH{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["HTRat"] = cat_df[tc].Histo1D(("{name}__{cat}__HTRat_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1), "HTRat{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dRbb"] = cat_df[tc].Histo1D(("{name}__{cat}__dRbb_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 16,0,2*pi), "dRbb{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dPhibb"] = cat_df[tc].Histo1D(("{name}__{cat}__dPhibb_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 16,-pi,pi), "dPhibb{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dEtabb"] = cat_df[tc].Histo1D(("{name}__{cat}__dEtabb_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 10,0,5), "dEtabb{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Lepton{lpf}_pt_LeadLep".format(lpf=leppostfix)] = cat_df[tc].Histo1D(("{name}__{cat}__Lepton{lpf}_pt_LeadLep_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 100,0,500), "FTALepton{lpf}_pt_LeadLep".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Lepton{lpf}_pt_SubleadLep".format(lpf=leppostfix)] = cat_df[tc].Histo1D(("{name}__{cat}__Lepton{lpf}_pt_SubleadLep_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 100,0,500), "FTALepton{lpf}_pt_SubleadLep".format(lpf=leppostfix), wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon{lpf}_pt".format(lpf=leppostfix)] = cat_df[tc].Histo1D(("{name}__{cat}__Muon{lpf}_pt_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 100,0,500), "FTAMuon{lpf}_pt".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Lepton{lpf}_eta_LeadLep".format(lpf=leppostfix)] = cat_df[tc].Histo1D(("{name}__{cat}__Lepton{lpf}_eta_LeadLep_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 52,-2.6,2.6), "FTALepton{lpf}_eta_LeadLep".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Lepton{lpf}_eta_SubleadLep".format(lpf=leppostfix)] = cat_df[tc].Histo1D(("{name}__{cat}__Lepton{lpf}_eta_SubleadLep_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 52,-2.6,2.6), "FTALepton{lpf}_eta_SubleadLep".format(lpf=leppostfix), wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Lepton{lpf}_eta_SubleadLep".format(lpf=leppostfix)] = cat_df[tc].Histo1D(("{name}__{cat}__Lepton{lpf}_eta_SubleadLep_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 52,-2.6,2.6), "FTALepton{lpf}_eta_SubleadLep".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dRll"] = cat_df[tc].Histo1D(("{name}__{cat}__dRll_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 16,0,2*pi), "FTALepton{lpf}_dRll".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dPhill"] = cat_df[tc].Histo1D(("{name}__{cat}__dPhill_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 16,-pi,pi), "FTALepton{lpf}_dPhill".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dEtall"] = cat_df[tc].Histo1D(("{name}__{cat}__dEtall_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 10,0,5), "FTALepton{lpf}_dEtall".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofMETandEl"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofMETandEl_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofMETandEl{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofMETandMu"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofMETandMu_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofMETandMu{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofElandMu"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofElandMu_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofElandMu{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nJet"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 14, 0, 14), "n{fj}".format(fj=fillJet), wgtVar)
                    if isData is False:
                        histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nJet_genMatched"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_genMatched_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 14, 0, 14), "n{fj}_genMatched".format(fj=fillJet), wgtVar)
                        histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nJet_genMatched_puIdLoose"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_genMatched_puIdLoose_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 14, 0, 14), "n{fj}_genMatched_puIdLoose".format(fj=fillJet), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nLooseDeepCSV"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_LooseDeepCSV_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nLooseDeepCSVB{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nMediumDeepCSV"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_MediumDeepCSV_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nMediumDeepCSVB{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nTightDeepCSV"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_TightDeepCSV_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nTightDeepCSVB{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nLooseDeepJet"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_LooseDeepJet_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nLooseDeepJetB{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nMediumDeepJet"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_MediumDeepJet_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nMediumDeepJetB{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nTightDeepJet"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_TightDeepJet_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nTightDeepJetB{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nLooseMuon"] = cat_df[tc].Histo1D(("{name}__{cat}__nLooseFTAMuon{lpf}_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 4, 0, 4), "nLooseFTAMuon{lpf}".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nMediumMuon"] = cat_df[tc].Histo1D(("{name}__{cat}__nMediumFTAMuon{lpf}_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 4, 0, 4), "nMediumFTAMuon{lpf}".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nTightMuon"] = cat_df[tc].Histo1D(("{name}__{cat}__nTightFTAMuon{lpf}_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 4, 0, 4), "nTightFTAMuon{lpf}".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nLooseElectron"] = cat_df[tc].Histo1D(("{name}__{cat}__nLooseFTAElectron{lpf}_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 4, 0, 4), "nLooseFTAElectron{lpf}".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nMediumElectron"] = cat_df[tc].Histo1D(("{name}__{cat}__nMediumFTAElectron{lpf}_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 4, 0, 4), "nMediumFTAElectron{lpf}".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nTightElectron"] = cat_df[tc].Histo1D(("{name}__{cat}__nTightFTAElectron{lpf}_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 4, 0, 4), "nTightFTAElectron{lpf}".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nLooseLepton"] = cat_df[tc].Histo1D(("{name}__{cat}__nLooseFTALepton{lpf}_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 4, 0, 4), "nLooseFTALepton{lpf}".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nMediumLepton"] = cat_df[tc].Histo1D(("{name}__{cat}__nMediumFTALepton{lpf}_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 4, 0, 4), "nMediumFTALepton{lpf}".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nTightLepton"] = cat_df[tc].Histo1D(("{name}__{cat}__nTightFTALepton{lpf}_{spf}".format(name=sampleName, cat=tcn, lpf=leppostfix, spf=syspostfix), "", 4, 0, 4), "nTightFTALepton{lpf}".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofMETandEl"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofMETandEl_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofMETandEl{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofMETandMu"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofMETandMu_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofMETandMu{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofElandMu"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofElandMu_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofElandMu{bpf}".format(bpf=branchpostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_InvMass"] = cat_df[tc].Histo1D(("{name}__{cat}__Muon_InvMass_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 60, 0, 150), "FTAMuon{lpf}_InvariantMass".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_InvMass"] = cat_df[tc].Histo1D(("{name}__{cat}__Electron_InvMass_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 60, 0, 150), "FTAElectron{lpf}_InvariantMass".format(lpf=leppostfix), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_InvMass_v_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_InvMass_v_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 30, 0, 150, 20, 0, 400), "FTAMuon{lpf}_InvariantMass".format(lpf=leppostfix), fillMET_pt, wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_InvMass_v_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_InvMass_v_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 30, 0, 150, 20, 0, 400), "FTAElectron{lpf}_InvariantMass".format(lpf=leppostfix), fillMET_pt, wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 30, 0., 0.2, 20,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso04_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso04_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso04_all;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "RVec_MET_pt", wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                
                    if isData == False:
                        pass                
            
            if histos2D_dict != None:
                if "sysVar_{spf}".format(spf=syspostfix) not in histos2D_dict:
                    histos2D_dict["sysVar{spf}".format(spf=syspostfix)] = {}
                for tc in cat_df.keys(): 
                    if tc not in histos2D_dict["sysVar{spf}".format(spf=syspostfix)]: 
                        histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc] = {}
                for tc, node in cat_df.items():
                    tcn = tc#.replace("blind_", "")
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 30, 0., 0.2, 20,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso04_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso04_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso04_all;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "RVec_MET_pt", wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                    #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                    #### Older versions
                    #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 100, 0., 0.2, 100,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                    #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 100, 0, 0.2, 100,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                    #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso04_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso04_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso04_all;MET", 100, 0, 0.2, 100,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "RVec_MET_pt", wgtVar)
                    #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 100, 0, 0.2, 100,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                    #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 100, 0, 0.2, 100,30,1030), "FTAElectron{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                    if isData == False:
                        #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["test1"] = cat_df[tc].Histo2D(("{name}__{cat}__test1_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAMuon{lpf}_pfRelIso03_all", "PV_npvsGood", wgtVar)
                        #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["test2"] = cat_df[tc].Histo2D(("{name}__{cat}__test2_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAMuon{lpf}_pfRelIso03_all", "METFixEE2017_pt", wgtVar)
                        #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["npvsGood_vs_nTrueInttest"] = cat_df[tc].Histo2D(("{name}__{cat}__npvsGood_vs_nTrueInttest_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAElectron{lpf}_pfRelIso03_all", "MET_pt_flat", wgtVar)
                        histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["npvsGood_vs_nTrueInt"] = cat_df[tc].Histo2D(("{name}__{cat}__npvsGood_vs_nTrueInt_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvsGood", wgtVar)
                        histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["npvsGood_vs_nPU"] = cat_df[tc].Histo2D(("{name}__{cat}__npvsGood_vs_nPU_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nPU;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvsGood", wgtVar)
                        histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["npvs_vs_nTrueInt"] = cat_df[tc].Histo2D(("{name}__{cat}__npvs_vs_nTrueInt_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nTrueInt;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvs", wgtVar)
                        histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["npvs_vs_nPU"] = cat_df[tc].Histo2D(("{name}__{cat}__npvs_vs_nPU_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nPU;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvs", wgtVar)
      
    return cat_df


# In[ ]:


def fillHistosOld(input_df, sampleName=None, wgtVar="wgt_SUMW", isData = True, histos1D_dict=None, histos2D_dict=None, histosNS_dict=None, 
               doMuons=False, doElectrons=False, doLeptons=False, doJets=False, doWeights=False, doEventVars=False, 
               makeMountains=False, debugInfo=True, nJetsToHisto=10, useDeepCSV=False,
               sysVariations={"$NOMINAL": {"jet_mask": "jet_mask", 
                                           "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                           "wgt_final": "_deepcsv_shape",
                                           "jet_pt_var": "Jet_pt",
                                           "met_pt_var": "METFixEE2017_pt",
                                           "met_phi_var": "METFixEE2017_phi",
                                           "btagSF": "Jet_btagSF_deepcsv_shape",
                                           "weightVariation": False}
                                     },):
    """Method to fill histograms given an input RDataFrame, input sample/dataset name, input histogram dictionaries.
    Has several options of which histograms to fill, such as Leptons, Jets, Weights, EventVars, etc.
    Types of histograms (1D, 2D, those which will not be stacked(NS - histosNS)) are filled by passing non-None
    value to that histosXX_dict variable. Internally stored with structure separating the categories of histos,
    with 'Muons,' 'Electrons,' 'Leptons,' 'Jets,' 'EventVars,' 'Weights' subcategories."""
    if doMuons == False and doElectrons == False and doLeptons == False                and doJets == False and doWeights == False and doEventVars == False                and makeMountains == False:
        raise RuntimeError("Must select something to plot:"                               "Set do{Muons,Electrons,Leptons,Jets,Weights,EventVars,etc} = True in init method")
    
    pi = ROOT.TMath.Pi()
    sysVar, sysDict = sysVariations.items()
    #Everything here needs to be indented and looped over, excepting FILTERS!
    wgtVar = sysDict.get(wgt_final, "wgt_SUMW_PU_LSF_L1PF")
    isWeightVariation = sysDict.get("weightVariation", False)
    #Name histograms with their actual systematic variation postfix
    syspostfix = sysVar.replace("$NOMINAL", "_nom")
    #name branches for filling with the nominal postfix if weight variations, and systematic postfix if scale variation (jes_up, etc.)
    branchpostfix = None
    if isWeightVariation:
        branchpostfix = "_nom"
    else:
        branchpostfix = sysVar.replace("$NOMINAL", "_nom")
    fillJet_pt = "FTAJet{bpf}_pt".format(bpf=branchpostfix)
    fillJet_phi = "FTAJet{bpf}_phi".format(bpf=branchpostfix)
    fillJet_eta = "FTAJet{bpf}_eta".format(bpf=branchpostfix)
    fillJet_mass = "FTAJet{bpf}_mass".format(bpf=branchpostfix)
    fillMET_pt = "FTAMET{bpf}_pt".format(bpf=branchpostfix)
    fillMET_phi = "FTAMET{bpf}_phi".format(bpf=branchpostfix)
    
    if doWeights == True:
        if histosNS_dict != None:
            if "EventVars" not in histosNS_dict:
                histosNS_dict["EventVars"] = {}
            histosNS[name][lvl]["EventVars"]["wgt_NUMW"] = input_df.Histo1D("wgt_NUMW")
            histosNS[name][lvl]["EventVars"][wgtVar] = input_df.Histo1D(wgtVar)
        if histos1D_dict != None:
            if "EventVars" not in histos1D_dict:
                histos1D_dict["EventVars"] = {}
            histos1D_dict["EventVars"]["wgt_diff"] = input_df.Histo1D(("wgt_diff", "(wgt_NUMW - wgt_SUMW)/wgt_SUMW", 2000, -1, 1), "wgt_diff", "1")
            histos1D_dict["EventVars"]["wgt_PU"] = input_df.Histo1D(("wgt_PU", "", 2000, 0, 5), "puWeight", "wgt_SUMW")
            histos1D_dict["EventVars"]["wgt_LSF"] = input_df.Histo1D(("wgt_LSF", "", 2000, 0, 5), "wgt_LSF", "wgt_SUMW")
            histos1D_dict["EventVars"]["wgt_L1PF"] = input_df.Histo1D(("wgt_L1PF", "", 2000, 0, 5), "L1PreFiringWeight_Nom", "wgt_SUMW")
            histos1D_dict["EventVars"]["wgt_PU_LSF_L1PF"] = input_df.Histo1D(("wgt_PU_LSF_L1PF", "", 2000, 0, 5), "wgt_PU_LSF_L1PF", "wgt_SUMW")
    if doMuons == True:
        if histos1D_dict != None:
            if "Muons" not in histos1D_dict: 
                histos1D_dict["Muons"] = {}
            histos1D_dict["Muons"]["idx"] = input_df.Histo1D(("idx{}".format(postfix), "", 5, 0, 5), "Muon_idx", wgtVar)
            histos1D_dict["Muons"]["Gidx"] = input_df.Histo1D(("Gidx{}".format(postfix), "", 5, 0, 5), "FTAMuon{lpf}_idx", wgtVar)
            histos1D_dict["Muons"]["nMu"] = input_df.Histo1D(("nMuon{}".format(postfix), "", 5, 0, 5), "nFTAMuon{lpf}", wgtVar)
            histos1D_dict["Muons"]["nLooseMu"] = input_df.Histo1D(("nLooseMuon{}".format(postfix), "", 5, 0, 5), "nLooseFTAMuon{lpf}", wgtVar)
            histos1D_dict["Muons"]["nMediumMu"] = input_df.Histo1D(("nMediumMuon{}".format(postfix), "", 5, 0, 5), "nMediumFTAMuon{lpf}", wgtVar)
            histos1D_dict["Muons"]["pt"] = input_df.Histo1D(("Muon_pt{}".format(postfix), "", 100, 0, 500), "FTAMuon{lpf}_pt", wgtVar)
            histos1D_dict["Muons"]["eta"] = input_df.Histo1D(("Muon_eta{}".format(postfix), "", 104, -2.6, 2.6), "FTAMuon{lpf}_eta", wgtVar)
            histos1D_dict["Muons"]["phi"] = input_df.Histo1D(("Muon_phi{}".format(postfix), "", 64, -pi, pi), "FTAMuon{lpf}_phi", wgtVar)
            #histos1D_dict["Muons"]["mass"] = input_df.Histo1D(("Muon_mass{}".format(postfix), "", 50, 0, 1), "FTAMuon{lpf}_mass", wgtVar)
            histos1D_dict["Muons"]["iso"] = input_df.Histo1D(("Muon_iso{}".format(postfix), "", 8, 0, 8), "FTAMuon{lpf}_pfIsoId", wgtVar)
            histos1D_dict["Muons"]["dz"] = input_df.Histo1D(("Muon_dz{}".format(postfix), "", 100, -0.01, 0.01), "FTAMuon{lpf}_dz", wgtVar)
            histos1D_dict["Muons"]["dxy"] = input_df.Histo1D(("Muon_dxy{}".format(postfix), "", 100, -0.1, 0.1), "FTAMuon{lpf}_dxy", wgtVar)
            #histos1D_dict["Muons"]["d0"] = input_df.Histo1D(("Muon_d0{}".format(postfix), "", 100, -0.01, 0.01), "FTAMuon{lpf}_d0", wgtVar)
            histos1D_dict["Muons"]["ip3d"] = input_df.Histo1D(("Muon_ip3d{}".format(postfix), "", 100, 0, 0.01), "FTAMuon{lpf}_ip3d", wgtVar)
            histos1D_dict["Muons"]["pfRelIso03_all"] = input_df.Histo1D(("Muon_pfRelIso03_all{}".format(postfix), "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_all", wgtVar)
            histos1D_dict["Muons"]["pfRelIso03_chg"] = input_df.Histo1D(("Muon_pfRelIso03_chg{}".format(postfix), "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_chg", wgtVar)
            histos1D_dict["Muons"]["pfRelIso04_all"] = input_df.Histo1D(("Muon_pfRelIso04_all{}".format(postfix), "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso04_all", wgtVar)
        if histos2D_dict != None:
            if "Muons" not in histos2D_dict:
                histos2D_dict["Muons"] = {}
            histos2D_dict["Muons"]["eta_phi"] = input_df.Histo2D(("Muon_eta_phi{}".format(postfix), "",
                                                                  104, -2.6, 2.6,
                                                                  64, -pi, pi),
                                                                 "FTAMuon{lpf}_eta", "FTAMuon{lpf}_phi", wgtVar)
            histos2D_dict["Muons"]["dz_ip3d"] = input_df.Histo2D(("Muon_dz_ip3d{}".format(postfix), "",
                                                                  100, -0.01, 0.01,
                                                                  100, 0, 0.01),
                                                                 "FTAMuon{lpf}_dz", "FTAMuon{lpf}_ip3d", wgtVar)
    if doElectrons == True:
        if histos1D_dict != None:
            if "Electrons" not in histos1D_dict: 
                histos1D_dict["Electrons"] = {}
            histos1D_dict["Electrons"]["nEl"] = input_df.Histo1D(("nElectron{}".format(postfix), "", 5, 0, 5), "nFTAElectron{lpf}", wgtVar)
            histos1D_dict["Electrons"]["nLooseEl"] = input_df.Histo1D(("nLooseElectron{}".format(postfix), "", 5, 0, 5), "nLooseFTAElectron{lpf}", wgtVar)
            histos1D_dict["Electrons"]["nMediumEl"] = input_df.Histo1D(("nMediumElectron{}".format(postfix), "", 5, 0, 5), "nMediumFTAElectron{lpf}", wgtVar)
            histos1D_dict["Electrons"]["pt"] = input_df.Histo1D(("Electron_pt{}".format(postfix), "", 100, 0, 500), "FTAElectron{lpf}_pt", wgtVar)
            histos1D_dict["Electrons"]["eta"] = input_df.Histo1D(("Electron_eta{}".format(postfix), "", 104, -2.6, 2.6), "FTAElectron{lpf}_eta", wgtVar)
            histos1D_dict["Electrons"]["phi"] = input_df.Histo1D(("Electron_phi{}".format(postfix), "", 64, -pi, pi), "FTAElectron{lpf}_phi", wgtVar)
            #histos1D_dict["Electrons"]["mass"] = input_df.Histo1D(("Electron_mass{}".format(postfix), "", 50, 0, 1), "FTAElectron{lpf}_mass", wgtVar)
            histos1D_dict["Electrons"]["dz"] = input_df.Histo1D(("Electron_dz{}".format(postfix), "", 100, -0.01, 0.01), "FTAElectron{lpf}_dz", wgtVar)
            #histos1D_dict["Electrons"]["d0"] = input_df.Histo1D(("Electron_d0{}".format(postfix), "", 100, 0, 0.01), "FTAElectron{lpf}_d0", wgtVar)
            histos1D_dict["Electrons"]["ip3d"] = input_df.Histo1D(("Electron_ip3d{}".format(postfix), "", 100, 0, 0.01), "FTAElectron{lpf}_ip3d", wgtVar)
            histos1D_dict["Electrons"]["pfRelIso03_all"] = input_df.Histo1D(("Electron_pfRelIso03_all{}".format(postfix), "", 100, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_all", wgtVar)
            histos1D_dict["Electrons"]["pfRelIso03_chg"] = input_df.Histo1D(("Electron_pfRelIso03_chg{}".format(postfix), "", 100, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_chg", wgtVar)
            histos1D_dict["Electrons"]["cutBased"] = input_df.Histo1D(("Electron_cutBased{}".format(postfix), "", 5, 0, 5), "FTAElectron{lpf}_cutBased", wgtVar)
        if histos2D_dict != None:
            if "Electrons" not in histos2D_dict: 
                histos2D_dict["Electrons"] = {}
            histos2D_dict["Electrons"]["eta_phi"] = input_df.Histo2D(("Electron_eta_phi{}".format(postfix), "",
                                                                      104, -2.6, 2.6,
                                                                      64, -pi, pi),
                                                                     "FTAElectron{lpf}_eta", "FTAElectron{lpf}_phi", wgtVar)
            histos2D_dict["Electrons"]["dz_ip3d"] = input_df.Histo2D(("Electron_dz_ip3d{}".format(postfix), "",
                                                                      100, -0.01, 0.01,
                                                                      100, 0, 0.01),
                                                                     "FTAElectron{lpf}_dz", "FTAElectron{lpf}_ip3d", wgtVar)
    if doLeptons == True:
        if histos1D_dict != None:
            if "Leptons" not in histos1D_dict: 
                histos1D_dict["Leptons"] = {}
            histos1D_dict["Leptons"]["pt_LeadLep"] = input_df                    .Histo1D(("FTALepton{lpf}_pt_LeadLep{}".format(postfix), "", 100, 0, 500),"FTALepton{lpf}_pt_LeadLep", wgtVar)
            histos1D_dict["Leptons"]["pt_SubleadLep"] = input_df                    .Histo1D(("FTALepton{lpf}_pt_SubleadLep{}".format(postfix), "", 100, 0, 500),"FTALepton{lpf}_pt_SubleadLep", wgtVar)
            histos1D_dict["Leptons"]["eta"] = input_df                    .Histo1D(("FTALepton{lpf}_eta{}".format(postfix), "", 104, -2.6, 2.6),"FTALepton{lpf}_eta", wgtVar)
            histos1D_dict["Leptons"]["phi"] = input_df                    .Histo1D(("FTALepton{lpf}_phi{}".format(postfix), "", 64, -pi, pi),"FTALepton{lpf}_phi", wgtVar)
            histos1D_dict["Leptons"]["nLepton"] = input_df                    .Histo1D(("nLepton{}".format(postfix), "", 5, 0, 5), "nFTALepton{lpf}", wgtVar)
            histos1D_dict["Leptons"]["pdgId"] = input_df                    .Histo1D(("Lepton_pdgId{}".format(postfix), "", 32, -16, 16), "FTALepton{lpf}_pdgId", wgtVar)
            histos1D_dict["Leptons"]["jetIdx"] = input_df                    .Histo1D(("Lepton_jetIdx{}".format(postfix), "", 20, 0, 20), "FTALepton{lpf}_jetIdx", wgtVar)
            #histos1D_dict["Leptons"]["LepSF"] = input_df\
            #        .Histo1D(("Lepton_SF_({})".format("wgt_SUMW_PU:HARDCODED"), "", 100, 0.93, 1.03), "FTALepton{lpf}_SF_nom", "wgt_SUMW_PU")
            #histos1D_dict["Leptons"]["LSF"] = input_df\
            #        .Histo1D(("LSF_({})".format("wgt_SUMW_PU:HARDCODED"), "", 200, 0.80, 1.1), "wgt_LSF", "wgt_SUMW_PU")
            #histos1D_dict["Leptons"]["SPL_SP"] = input_df\
            #        .Histo1D(("SPL_SP_({})".format("wgt_SUMW_PU:HARDCODED"), "", 200, 0.80, 1.1), "SPL_SP", "wgt_SUMW_PU")
            #histos1D_dict["Leptons"]["LepSF"] = input_df.Histo1D("FTALepton{lpf}_SF_nom")#, "wgt_SUMW_PU")
            #histos1D_dict["Leptons"]["LSF"] = input_df.Histo1D("wgt_LSF")#, "wgt_SUMW_PU")
            #histos1D_dict["Leptons"]["SPL_SP"] = input_df.Histo1D("SPL_SP")#, "wgt_SUMW_PU")
            #histos1D_dict["Leptons"]["SUMW_PU"] = input_df.Histo1D("wgt_SUMW_PU")#, "wgt_SUMW_PU")
            #histos1D_dict["Leptons"]["SUMW_PU_LSF"] = input_df.Histo1D("wgt_SUMW_PU_LSF")#, "wgt_SUMW_PU")
            #histos1D_dict["Leptons"]["PU"] = input_df.Histo1D("puWeight")#, "wgt_SUMW_PU")
    if doJets == True:
        if histos1D_dict != None:
            if "Jets" not in histos1D_dict:
                histos1D_dict["Jets"] = {}
            histos1D_dict["Jets"]["pt"] = input_df.Histo1D(("Jet_pt{}".format(postfix), "", 100, 0, 500), fillJet_pt, wgtVar)
            for x in xrange(nJetsToHisto):
                histos1D_dict["Jets"]["pt_jet{}".format(x+1)] = input_df.Histo1D(("Jet_pt_jet{}({})".format(x+1, wgtVar), "", 100, 0, 500), "Jet{bpf}_pt_jet{}".format(x+1), wgtVar)
                histos1D_dict["Jets"]["eta_jet{}".format(x+1)] = input_df.Histo1D(("Jet_eta_jet{}({})".format(x+1, wgtVar), "", 104, -2.6, 2.6), "Jet{bpf}_eta_jet{}".format(x+1), wgtVar)
                histos1D_dict["Jets"]["phi_jet{}".format(x+1)] = input_df.Histo1D(("Jet_phi_jet{}({})".format(x+1, wgtVar), "", 64, -pi, pi), "Jet{bpf}_phi_jet{}".format(x+1), wgtVar)
            histos1D_dict["Jets"]["eta"] = input_df.Histo1D(("Jet_eta{}".format(postfix), "", 104, -2.6, 2.6), fillJet_eta, wgtVar)
            histos1D_dict["Jets"]["phi"] = input_df.Histo1D(("Jet_phi{}".format(postfix), "", 64, -pi, pi), fillJet_phi, wgtVar)
            histos1D_dict["Jets"]["mass"] = input_df.Histo1D(("Jet_mass{}".format(postfix), "", 100, 0, 500), fillJet_mass, wgtVar)
            histos1D_dict["Jets"]["jetId"] = input_df.Histo1D(("Jet_jetId{}".format(postfix), "", 8, 0, 8), "Jet{bpf}_jetId", wgtVar) #FIXME: not based on variation... okay? maybe not with masks...
            #histos1D_dict["Jets"]["btagDeepB_LeadtagJet"] = input_df.Histo1D(("Jet_btagDeepB_LeadtagJet{}".format(postfix), "", 101, -0.01, 1), "Jet{bpf}_btagDeepB_LeadtagJet", wgtVar)
            #histos1D_dict["Jets"]["btagDeepB_SubleadtagJet"] = input_df.Histo1D(("Jet_btagDeepB_SubleadtagJet{}".format(postfix), "", 101, -0.01, 1), "Jet{bpf}_btagDeepB_SubleadtagJet", wgtVar)
            #histos1D_dict["Jets"]["btagDeepJet_LeadtagJet"] = input_df.Histo1D(("Jet_btagDeepJetB_LeadtagJet{}".format(postfix), "", 101, -0.01, 1), "Jet{bpf}_btagDeepFlavB_sorted_LeadtagJet", wgtVar)
            #histos1D_dict["Jets"]["btagDeepJet_SubleadtagJet"] = input_df.Histo1D(("Jet_btagDeepJetB_SubleadtagJet{}".format(postfix), "", 101, -0.01, 1), "Jet{bpf}_btagDeepFlavB_sorted_SubleadtagJet", wgtVar)
            #histos1D_dict["Jets"]["nMediumCSVv2"] = input_df.Histo1D(("nJet_MediumCSVv2{}".format(postfix), "", 10, 0, 10), "nJet{bpf}_MediumCSVv2", wgtVar)
            histos1D_dict["Jets"]["nMediumDeepCSV"] = input_df.Histo1D(("nJet_MediumDeepCSV{}".format(postfix), "", 10, 0, 10), "nJet{bpf}_MediumDeepCSV", wgtVar)
            histos1D_dict["Jets"]["nMediumDeepJet"] = input_df.Histo1D(("nJet_MediumDeepJet{}".format(postfix), "", 10, 0, 10), "nJet{bpf}_MediumDeepJet", wgtVar)
            histos1D_dict["Jets"]["nJet"] = input_df.Histo1D(("nJet{}".format(postfix), "", 15, 0, 15), "nJet{bpf}", wgtVar)
            histos1D_dict["Jets"]["dR_Jet_Mu_leading"] = input_df.Histo1D(("dR_Jet_Mu_leading{}".format(postfix), "dR(Jet, #mu_{leading}); dR; Events)", 40, 0, 0.8), "dR_Jet_Mu_leading", wgtVar)
            histos1D_dict["Jets"]["dR_Jet_Mu_sublead"] = input_df.Histo1D(("dR_Jet_Mu_sublead{}".format(postfix), "dR(Jet, #mu_{subleading}); dR; Events)", 40, 0, 0.8), "dR_Jet_Mu_sublead", wgtVar)
            histos1D_dict["Jets"]["dR_Jet_El_leading"] = input_df.Histo1D(("dR_Jet_El_leading{}".format(postfix), "dR(Jet, #e_{leading}); dR; Events)", 40, 0, 0.8), "dR_Jet_El_leading", wgtVar)
            histos1D_dict["Jets"]["dR_Jet_El_sublead"] = input_df.Histo1D(("dR_Jet_El_sublead{}".format(postfix), "dR(Jet, #e_{subleading}); dR; Events)", 40, 0, 0.8), "dR_Jet_El_sublead", wgtVar)
            
            if debugInfo == True:
                #histos1D_dict["Jets"]["DiffMaskVsALT"] = input_df.Histo1D(("DiffMaskVsALT", "", 10, -10, 10), "DiffMaskVsALT", wgtVar)
                #histos1D_dict["Jets"]["DiffnJet"] = input_df.Histo1D(("DiffnJet", "", 10, -10, 10), "DiffnJet", wgtVar)
                histos1D_dict["Jets"]["DeepJetSorted"] = input_df.Histo1D("DeepJetSorted", wgtVar)
                histos1D_dict["Jets"]["DeepJetLeadtagMinusSubleadtag"] = input_df.Histo1D(("DeepJetLeadtagMinusSubleadtag", "DeepJet(Leadtag - Subleadtag);;Events", 100, -1, 1), "DeepJet0Minus1", wgtVar)
                histos1D_dict["Jets"]["MediumDeepJetSorted"] = input_df.Histo1D("MediumDeepJetSorted", wgtVar)
                #histos1D_dict["Jets"]["MediumDeepJet0Minus1"] = input_df.Histo1D(("MediumDeepJet0Minus1", "", 100, -1, 1), "MediumDeepJet0Minus1", wgtVar)
                #histos1D_dict["Jets"]["btagDeepJet_jet0Med"] = input_df.Histo1D(("Jet_btagDeepJetB_jet0Med{}".format(postfix), "", 102, -0.02, 1), "Jet{bpf}_btagDeepFlavB_jet0Med", wgtVar)
                #histos1D_dict["Jets"]["btagDeepJet_jet1Med"] = input_df.Histo1D(("Jet_btagDeepJetB_jet1Med{}".format(postfix), "", 102, -0.02, 1), "Jet{bpf}_btagDeepFlavB_jet1Med", wgtVar)
                #histos1D_dict["Jets"]["nJetNUMW"] = input_df.Histo1D(("nJet_NUMW", "", 15, 0, 15), "nJet{bpf}", "wgt_NUMW_V2")
                #histos1D_dict["Jets"]["nJetSUMW_PU"] = input_df.Histo1D(("nJet_SUMW_PU", "", 15, 0, 15), "nJet{bpf}", "wgt_SUMW_PU")
                #histos1D_dict["Jets"]["nJetSUMW_LSF"] = input_df.Histo1D(("nJet_SUMW_LSF", "", 15, 0, 15), "nJet{bpf}", "wgt_SUMW_LSF")
                #histos1D_dict["Jets"]["ptALT"] = input_df.Histo1D(("Jet_ptALT{}".format(postfix), "", 100, 0, 500), "Jet{bpf}_ptALT", wgtVar)
                #histos1D_dict["Jets"]["etaALT"] = input_df.Histo1D(("Jet_etaALT{}".format(postfix), "", 104, -2.6, 2.6), "Jet{bpf}_etaALT", wgtVar)
                #histos1D_dict["Jets"]["phiALT"] = input_df.Histo1D(("Jet_phiALT{}".format(postfix), "", 64, -pi, pi), "Jet{bpf}_phiALT", wgtVar)
                #histos1D_dict["Jets"]["massALT"] = input_df.Histo1D(("Jet_massALT{}".format(postfix), "", 100, 0, 500), "Jet{bpf}_massALT", wgtVar)
                #histos1D_dict["Jets"]["jetIdALT"] = input_df.Histo1D(("Jet_jetIdALT{}".format(postfix), "", 8, 0, 8), "Jet{bpf}_jetIdALT", wgtVar)
        
        if histos2D_dict != None:
            if "Jets" not in histos2D_dict:
                histos2D_dict["Jets"] = {}
            histos2D_dict["Jets"]["eta_phi"] = input_df.Histo2D(("Jet_eta_phi{}".format(postfix), "",
                                                                 104, -2.6, 2.6,
                                                                 64, -pi, pi),
                                                                fillJet_eta, fillJet_phi, wgtVar)
    if doEventVars == True:
        if histos1D_dict != None:
            if "EventVars" not in histos1D_dict:
                histos1D_dict["EventVars"] = {}
            #histos1D_dict["EventVars"]["JML_baseline"] = input_df.Histo1D(("JML_baseline{}".format(postfix), "", 2,0,2), "JML_baseline_pass", wgtVar)
            #histos1D_dict["EventVars"]["JML_selection"] = input_df.Histo1D(("JML_selection{}".format(postfix), "", 2,0,2), "JML_selection_pass", wgtVar)
            #histos1D_dict["EventVars"]["HT_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_HT_baseline{}".format(postfix), "", 100,400,1400), "ESV_JetMETLogic_HT_baseline", wgtVar)
            #histos1D_dict["EventVars"]["H_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_H_baseline{}".format(postfix), "", 100,400,1400), "ESV_JetMETLogic_H_baseline", wgtVar)
            #histos1D_dict["EventVars"]["HT2M_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_HT2M_baseline{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_HT2M_baseline", wgtVar)
            #histos1D_dict["EventVars"]["H2M_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_H2M_baseline{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_H2M_baseline", wgtVar)
            #histos1D_dict["EventVars"]["HTb_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_HTb_baseline{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_HTb_baseline", wgtVar)
            #histos1D_dict["EventVars"]["HTH_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_HTH_baseline{}".format(postfix), "", 100,0,1), "ESV_JetMETLogic_HTH_baseline", wgtVar)
            #histos1D_dict["EventVars"]["HTRat_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_HTRat_baseline{}".format(postfix), "", 100,0,1), "ESV_JetMETLogic_HTRat_baseline", wgtVar)
            #histos1D_dict["EventVars"]["dRbb_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_dRbb_baseline{}".format(postfix), "", 64,0,2*pi), "ESV_JetMETLogic_dRbb_baseline", wgtVar)
            #histos1D_dict["EventVars"]["DiLepMass_baseline"] = input_df.Histo1D(("ESV_JetMETLogic_DiLepMass_baseline{}".format(postfix), "", 100,0,500), "ESV_JetMETLogic_DiLepMass_baseline", wgtVar)
            #histos1D_dict["EventVars"]["HT_selection"] = input_df.Histo1D(("ESV_JetMETLogic_HT_selection{}".format(postfix), "", 100,400,1400), "ESV_JetMETLogic_HT_selection", wgtVar)
            #histos1D_dict["EventVars"]["H_selection"] = input_df.Histo1D(("ESV_JetMETLogic_H_selection{}".format(postfix), "", 100,400,1400), "ESV_JetMETLogic_H_selection", wgtVar)
            #histos1D_dict["EventVars"]["HT2M_selection"] = input_df.Histo1D(("ESV_JetMETLogic_HT2M_selection{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_HT2M_selection", wgtVar)
            #histos1D_dict["EventVars"]["H2M_selection"] = input_df.Histo1D(("ESV_JetMETLogic_H2M_selection{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_H2M_selection", wgtVar)
            #histos1D_dict["EventVars"]["HTb_selection"] = input_df.Histo1D(("ESV_JetMETLogic_HTb_selection{}".format(postfix), "", 100,400,900), "ESV_JetMETLogic_HTb_selection", wgtVar)
            #histos1D_dict["EventVars"]["HTH_selection"] = input_df.Histo1D(("ESV_JetMETLogic_HTH_selection{}".format(postfix), "", 100,0,1), "ESV_JetMETLogic_HTH_selection", wgtVar)
            #histos1D_dict["EventVars"]["HTRat_selection"] = input_df.Histo1D(("ESV_JetMETLogic_HTRat_selection{}".format(postfix), "", 100,0,1), "ESV_JetMETLogic_HTRat_selection", wgtVar)
            #histos1D_dict["EventVars"]["dRbb_selection"] = input_df.Histo1D(("ESV_JetMETLogic_dRbb_selection{}".format(postfix), "", 64,0,2*pi), "ESV_JetMETLogic_dRbb_selection", wgtVar)
            #histos1D_dict["EventVars"]["DiLepMass_selection"] = input_df.Histo1D(("ESV_JetMETLogic_DiLepMass_selection{}".format(postfix), "", 100,0,500), "ESV_JetMETLogic_DiLepMass_selection", wgtVar)
            histos1D_dict["EventVars"]["MET_pt"] = input_df.Histo1D(("MET_xycorr_pt{}".format(postfix), "", 100,30,1030), fillMET_pt, wgtVar)
            histos1D_dict["EventVars"]["MET_phi"] = input_df.Histo1D(("MET_xycorr_phi{}".format(postfix), "", 100,-pi,pi), fillMET_phi, wgtVar)
            histos1D_dict["EventVars"]["HT"] = input_df.Histo1D(("HT{}".format(postfix), "", 130,400,1700), "FTAJet{bpf}_HT", wgtVar)
            histos1D_dict["EventVars"]["H"] = input_df.Histo1D(("H{}".format(postfix), "", 160,400,2000), "FTAJet{bpf}_H", wgtVar)
            histos1D_dict["EventVars"]["HT2M"] = input_df.Histo1D(("HT2M{}".format(postfix), "", 100,0,1000), "FTAJet{bpf}_HT2M", wgtVar)
            histos1D_dict["EventVars"]["H2M"] = input_df.Histo1D(("H2M{}".format(postfix), "", 150,0,1500), "FTAJet{bpf}_H2M", wgtVar)
            histos1D_dict["EventVars"]["HTb"] = input_df.Histo1D(("HTb{}".format(postfix), "", 100,0,1000), "FTAJet{bpf}_HTb", wgtVar)
            histos1D_dict["EventVars"]["HTH"] = input_df.Histo1D(("HTH{}".format(postfix), "", 100,0,1), "FTAJet{bpf}_HTH", wgtVar)
            histos1D_dict["EventVars"]["HTRat"] = input_df.Histo1D(("HTRat{}".format(postfix), "", 100,0,1), "FTAJet{bpf}_HTRat", wgtVar)
            histos1D_dict["EventVars"]["dRbb"] = input_df.Histo1D(("dRbb{}".format(postfix), "", 64,0,2*pi), "FTAJet{bpf}_dRbb", wgtVar)
            histos1D_dict["EventVars"]["dPhibb"] = input_df.Histo1D(("dPhibb{}".format(postfix), "", 64,-pi,pi), "FTAJet{bpf}_dPhibb", wgtVar)
            histos1D_dict["EventVars"]["dEtabb"] = input_df.Histo1D(("dEtabb{}".format(postfix), "", 50,0,5), "FTAJet{bpf}_dEtabb", wgtVar)
            histos1D_dict["EventVars"]["dRll"] = input_df.Histo1D(("dRll{}".format(postfix), "", 64,0,2*pi), "FTALepton{lpf}_dRll", wgtVar)
            histos1D_dict["EventVars"]["dPhill"] = input_df.Histo1D(("dPhill{}".format(postfix), "", 64,-pi,pi), "FTALepton{lpf}_dPhill", wgtVar)
            histos1D_dict["EventVars"]["dEtall"] = input_df.Histo1D(("dEtall{}".format(postfix), "", 50,0,5), "FTALepton{lpf}_dEtall", wgtVar)
            histos1D_dict["EventVars"]["MTofMETandEl"] = input_df.Histo1D(("MTofMETandEl{}".format(postfix), "", 100, 0, 200), "MTofMETandEl", wgtVar)
            histos1D_dict["EventVars"]["MTofMETandMu"] = input_df.Histo1D(("MTofMETandMu{}".format(postfix), "", 100, 0, 200), "MTofMETandMu", wgtVar)
            histos1D_dict["EventVars"]["MTofElandMu"] = input_df.Histo1D(("MTofElandMu{}".format(postfix), "", 100, 0, 200), "MTofElandMu", wgtVar)
            #histos1D_dict["EventVars"]["MTMasslessCheck"] = input_df.Histo1D(("MTMasslessCheck{}".format(postfix), "", 100, 0, 200), "MTMasslessCheck", wgtVar)
            #histos1D_dict["EventVars"]["MTCrossCheck"] = input_df.Histo1D(("MTCrossCheck{}".format(postfix), "", 100, 0, 200), "MTCrossCheck", wgtVar)
            #histos1D_dict["EventVars"]["MTCrossCheckDifference"] = input_df.Histo1D(("MTCrossCheckDifference{}".format(postfix), "", 100, 0, 10), "MTCrossCheckDifference", wgtVar)
            #histos1D_dict["EventVars"]["MTCrossCheckMasslessDifference"] = input_df.Histo1D(("MTCrossCheckMasslessDifference{}".format(postfix), "", 100, 0, 0.02), "MTCrossCheckMasslessDifference", wgtVar)
            histos1D_dict["EventVars"]["PV_npvsGood"] = input_df.Histo1D(("PV_npvsGood{}".format(postfix), "", 100, 0, 100), "PV_npvsGood", wgtVar)
            histos1D_dict["EventVars"]["PV_npvs"] = input_df.Histo1D(("PV_npvs{}".format(postfix), "", 150, 0, 150), "PV_npvs", wgtVar)
            if isData == False:
                histos1D_dict["EventVars"]["Pileup_nTrueInt"] = input_df.Histo1D(("Pileup_TrueInt{}".format(postfix), ";Pileup_TrueInt;Events", 150, 0, 150), "Pileup_nTrueInt", wgtVar)
                histos1D_dict["EventVars"]["Pileup_nTrueInt_XS"] = input_df.Histo1D(("Pileup_TrueInt_({})".format("wgt_SUMW"), ";Pileup_TrueInt;Events", 150, 0, 150), "Pileup_nTrueInt", "wgt_SUMW")
                histos1D_dict["EventVars"]["Pileup_nPU_XS"] = input_df.Histo1D(("Pileup_nPU_({})".format("wgt_SUMW"), ";Pileup_nPU;Events", 150, 0, 150), "Pileup_nPU", "wgt_SUMW")
                histos1D_dict["EventVars"]["Pileup_nPU"] = input_df.Histo1D(("Pileup_nPU{}".format(postfix), ";Pileup_nPU;Events", 150, 0, 150), "Pileup_nPU", wgtVar)
            
        if histos2D_dict != None:
            if "EventVars" not in histos2D_dict:
                histos2D_dict["EventVars"] = {}
            if isData == False:
                histos2D_dict["EventVars"]["npvsGood_vs_nTrueInt"] = input_df.Histo2D(("npvsGood_vs_nTrueInt{}".format(postfix), ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvsGood", wgtVar)
                histos2D_dict["EventVars"]["npvsGood_vs_nPU"] = input_df.Histo2D(("npvsGood_vs_nPU{}".format(postfix), ";nPU;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvsGood", wgtVar)
                histos2D_dict["EventVars"]["npvs_vs_nTrueInt"] = input_df.Histo2D(("npvs_vs_nTrueInt{}".format(postfix), ";nTrueInt;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvs", wgtVar)
                histos2D_dict["EventVars"]["npvs_vs_nPU"] = input_df.Histo2D(("npvs_vs_nPU{}".format(postfix), ";nPU;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvs", wgtVar)
            
            if debugInfo == True:
                #histos1D_dict["EventVars"]["Jet{bpf}_HT_Match"] = input_df.Histo1D(("Jet{bpf}_HT_Match{}".format(postfix), "", 2,0,2), "Jet{bpf}_HT_matches", wgtVar)
                pass
            
    if makeMountains == True:
        if useDeepCSV == True:
            tagger = "CSV"
        else:
            tagger = "Jet"
        theCatsL0 = collections.OrderedDict()#Baseline nJet selection (inclusive!) for each systematic scale variation
        theCatsL1 = collections.OrderedDict() #Next level of selection, like nJet categories. If we need nBTag inclusive, they'll have to go here
        theCatsL2 = collections.OrderedDict() #Next level of selection, i.e. nBTag categories. 
        theCatsL0["Inclusive{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} >= 4".format(bpf=branchpostfix)
        
        theCatsL1["nMediumDeep{tag}0{bpf}".format(tag=tagger, bpf=branchpostfix)] = "nMediumDeep{tag}B{pf} == 0".format(tag=tagger)
        theCatsL1["nMediumDeep{tag}1{bpf}".format(tag=tagger, bpf=branchpostfix)] = "nMediumDeep{tag}B{pf} == 1".format(tag=tagger)
        theCatsL1["nMediumDeep{tag}2{bpf}".format(tag=tagger, bpf=branchpostfix)] = "nMediumDeep{tag}B{pf} == 2".format(tag=tagger)
        theCatsL1["blind_nMediumDeep{tag}3{bpf}".format(tag=tagger, bpf=branchpostfix)] = "nMediumDeep{tag}B{pf} == 3".format(tag=tagger)
        theCatsL1["blind_nMediumDeep{tag}4{bpf}".format(tag=tagger, bpf=branchpostfix)] = "nMediumDeep{tag}B{pf} == 4".format(tag=tagger)
        
        theCatsL2["nJet4{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} == 4".format(bpf=branchpostfix)
        theCatsL2["nJet5{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} == 5".format(bpf=branchpostfix)
        theCatsL2["blind_nJet6{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} == 6".format(bpf=branchpostfix)
        theCatsL2["blind_nJet7{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} == 7".format(bpf=branchpostfix)
        theCatsL2["blind_nJet8+{bpf}".format(bpf=branchpostfix)] = "nFTAJet{bpf} >= 8".format(bpf=branchpostfix)
        
        cat_df = collections.OrderedDict()
        for ck, cs in theCats.items():
            cat_df[ck] = input_df.Filter(cs, cs)
        
        
        #theCats["nMediumDeep{tag}0".format(tag=tagger)] = "nJet{bpf}_MediumDeep{tag} == 0".format(tag=tagger)
        #theCats["nMediumDeep{tag}1".format(tag=tagger)] = "nJet{bpf}_MediumDeep{tag} == 1".format(tag=tagger)
        #theCats["nMediumDeep{tag}2".format(tag=tagger)] = "nJet{bpf}_MediumDeep{tag} == 2".format(tag=tagger)
        
        #theCats["nMediumDeep{}0_nJet4".format(tagger)] = "nJet{bpf}_MediumDeep{} == 0 && nJet{bpf} == 4".format(tagger)
        #theCats["nMediumDeep{}1_nJet4".format(tagger)] = "nJet{bpf}_MediumDeep{} == 1 && nJet{bpf} == 4".format(tagger)
        #theCats["nMediumDeep{}2_nJet4".format(tagger)] = "nJet{bpf}_MediumDeep{} == 2 && nJet{bpf} == 4".format(tagger)
        #theCats["blind_nMediumDeep{}3_nJet4".format(tagger)] = "nJet{bpf}_MediumDeep{} == 3 && nJet{bpf} == 4".format(tagger)
        #theCats["blind_nMediumDeep{}4+_nJet4".format(tagger)] = "nJet{bpf}_MediumDeep{} >= 4 && nJet{bpf} == 4".format(tagger)
        
        #theCats["nMediumDeep{}0_nJet5".format(tagger)] = "nJet{bpf}_MediumDeep{} == 0 && nJet{bpf} == 5".format(tagger)
        #theCats["nMediumDeep{}1_nJet5".format(tagger)] = "nJet{bpf}_MediumDeep{} == 1 && nJet{bpf} == 5".format(tagger)
        #theCats["nMediumDeep{}2_nJet5".format(tagger)] = "nJet{bpf}_MediumDeep{} == 2 && nJet{bpf} == 5".format(tagger)
        #theCats["blind_nMediumDeep{}3_nJet5".format(tagger)] = "nJet{bpf}_MediumDeep{} == 3 && nJet{bpf} == 5".format(tagger)
        #theCats["blind_nMediumDeep{}4+_nJet5".format(tagger)] = "nJet{bpf}_MediumDeep{} >= 4 && nJet{bpf} == 5".format(tagger)
        
        #theCats["nMediumDeep{}0_nJet6".format(tagger)] = "nJet{bpf}_MediumDeep{} == 0 && nJet{bpf} == 6".format(tagger)
        #theCats["nMediumDeep{}1_nJet6".format(tagger)] = "nJet{bpf}_MediumDeep{} == 1 && nJet{bpf} == 6".format(tagger)
        #theCats["nMediumDeep{}2_nJet6".format(tagger)] = "nJet{bpf}_MediumDeep{} == 2 && nJet{bpf} == 6".format(tagger)
        #theCats["blind_nMediumDeep{}3_nJet6".format(tagger)] = "nJet{bpf}_MediumDeep{} == 3 && nJet{bpf} == 6".format(tagger)
        #theCats["blind_nMediumDeep{}4+_nJet6".format(tagger)] = "nJet{bpf}_MediumDeep{} >= 4 && nJet{bpf} == 6".format(tagger)
        
        #theCats["nMediumDeep{}0_nJet7".format(tagger)] = "nJet{bpf}_MediumDeep{} == 0 && nJet{bpf} == 7".format(tagger)
        #theCats["nMediumDeep{}1_nJet7".format(tagger)] = "nJet{bpf}_MediumDeep{} == 1 && nJet{bpf} == 7".format(tagger)
        #theCats["blind_nMediumDeep{}2_nJet7".format(tagger)] = "nJet{bpf}_MediumDeep{} == 2 && nJet{bpf} == 7".format(tagger)
        #theCats["blind_nMediumDeep{}3_nJet7".format(tagger)] = "nJet{bpf}_MediumDeep{} == 3 && nJet{bpf} == 7".format(tagger)
        #theCats["blind_nMediumDeep{}4+_nJet7".format(tagger)] = "nJet{bpf}_MediumDeep{} >= 4 && nJet{bpf} == 7".format(tagger)
        
        #theCats["nMediumDeep{}0_nJet8+".format(tagger)] = "nJet{bpf}_MediumDeep{} == 0 && nJet{bpf} >= 8".format(tagger)
        #theCats["nMediumDeep{}1_nJet8+".format(tagger)] = "nJet{bpf}_MediumDeep{} == 1 && nJet{bpf} >= 8".format(tagger)
        #theCats["blind_nMediumDeep{}2_nJet8+".format(tagger)] = "nJet{bpf}_MediumDeep{} == 2 && nJet{bpf} >= 8".format(tagger)
        #theCats["blind_nMediumDeep{}3_nJet8+".format(tagger)] = "nJet{bpf}_MediumDeep{} == 3 && nJet{bpf} >= 8".format(tagger)
        #theCats["blind_nMediumDeep{}4+_nJet8+".format(tagger)] = "nJet{bpf}_MediumDeep{} >= 4 && nJet{bpf} >= 8".format(tagger)
        
        if histos1D_dict != None:
            if "sysVar_{spf}".format(spf=syspostfix) not in histos1D_dict:
                histos1D_dict["sysVar_{spf}".format(spf=syspostfix)] = {}
            for tc in theCats.keys(): 
                if tc not in histos1D_dict["sysVar_{spf}".format(spf=syspostfix)]: 
                    histos1D_dict["sysVar_{spf}".format(spf=syspostfix)][tc] = {}
            for tc, cut in theCats.items():
                tcn = tc#.replace("blind_", "") #FIXME do I want blind stripped with new convention for naming?
                for x in xrange(nJetsToHisto):
                    #FIXME: None of these are based upon jet scale variations, yet!
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_pt_jet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_pt_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 100, 0, 500), "FTAJet{bpf}_pt_jet{n}".format(bpf=branchpostfix, n=x+1), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_eta_jet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_eta_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 104, -2.6, 2.6), "FTAJet{bpf}_eta_jet{n}".format(bpf=branchpostfix, n=x+1), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_phi_jet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_phi_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 64, -pi, pi), "FTAJet{bpf}_phi_jet{n}".format(bpf=branchpostfix, n=x+1), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_DeepCSV_jet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_DeepCSV_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 100, 0.0, 1.0), "FTAJet{bpf}_DeepCSV_jet{n}".format(bpf=branchpostfix, n=x+1), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_DeepJet_jet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_DeepJet_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 100, 0.0, 1.0), "FTAJet{bpf}_DeepJet_jet{n}".format(bpf=branchpostfix, n=x+1), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_DeepCSV_sortedjet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_DeepCSV_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 100, 0.0, 1.0), "FTAJet{bpf}_DeepCSV_sortedjet{n}".format(bpf=branchpostfix, n=x+1), wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Jet_DeepJet_sortedjet{}".format(x+1)] = cat_df[tc].Histo1D(("{name}__{cat}__Jet_DeepJet_jet{n}_{spf}".format(name=sampleName, n=x+1, cat=tcn, spf=syspostfix), "", 100, 0.0, 1.0), "FTAJet{bpf}_DeepJet_sortedjet{n}".format(bpf=branchpostfix, n=x+1), wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MET_pt"] = cat_df[tc].Histo1D(("{name}__{cat}__MET_pt_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1000), fillMET_pt, wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MET_phi"] = cat_df[tc].Histo1D(("{name}__{cat}__MET_phi_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,-pi,pi), fillMET_phi, wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_all"] = cat_df[tc].Histo1D(("{name}__{cat}__Muon_pfRelIso03_all_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_all", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_chg"] = cat_df[tc].Histo1D(("{name}__{cat}__Muon_pfRelIso03_chg_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_chg", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso04_all"] = cat_df[tc].Histo1D(("{name}__{cat}__Muon_pfRelIso04_all_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 0.2), "FTAMuon{lpf}_pfRelIso04_all", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_all"] = cat_df[tc].Histo1D(("{name}__{cat}__Electron_pfRelIso03_all_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_all", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_chg"] = cat_df[tc].Histo1D(("{name}__{cat}__Electron_pfRelIso03_chg_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_chg", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["HT"] = cat_df[tc].Histo1D(("{name}__{cat}__HT_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 30,400,2000), "Jet{bpf}_HT", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["H"] = cat_df[tc].Histo1D(("{name}__{cat}__H_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 30,400,2000), "Jet{bpf}_H", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["HT2M"] = cat_df[tc].Histo1D(("{name}__{cat}__HT2M_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1000), "Jet{bpf}_HT2M", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["H2M"] = cat_df[tc].Histo1D(("{name}__{cat}__H2M_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1500), "Jet{bpf}_H2M", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["HTb"] = cat_df[tc].Histo1D(("{name}__{cat}__HTb_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1000), "Jet{bpf}_HTb", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["HTH"] = cat_df[tc].Histo1D(("{name}__{cat}__HTH_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1), "Jet{bpf}_HTH", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["HTRat"] = cat_df[tc].Histo1D(("{name}__{cat}__HTRat_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20,0,1), "Jet{bpf}_HTRat", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dRbb"] = cat_df[tc].Histo1D(("{name}__{cat}__dRbb_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 16,0,2*pi), "Jet{bpf}_dRbb", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dPhibb"] = cat_df[tc].Histo1D(("{name}__{cat}__dPhibb_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 16,-pi,pi), "Jet{bpf}_dPhibb", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dEtabb"] = cat_df[tc].Histo1D(("{name}__{cat}__dEtabb_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 10,0,5), "Jet{bpf}_dEtabb", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Lepton{lpf}_pt_LeadLep"] = cat_df[tc].Histo1D(("{name}__{cat}__Lepton{lpf}_pt_LeadLep_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 100,0,500), "FTALepton{lpf}_pt_LeadLep", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Lepton{lpf}_pt_SubleadLep"] = cat_df[tc].Histo1D(("{name}__{cat}__Lepton{lpf}_pt_SubleadLep_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 100,0,500), "FTALepton{lpf}_pt_SubleadLep", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon{lpf}_pt"] = cat_df[tc].Histo1D(("{name}__{cat}__Muon{lpf}_pt_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 100,0,500), "FTAMuon{lpf}_pt", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Lepton{lpf}_eta_LeadLep"] = cat_df[tc].Histo1D(("{name}__{cat}__Lepton{lpf}_eta_LeadLep_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 52,-2.6,2.6), "FTALepton{lpf}_eta_LeadLep", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Lepton{lpf}_eta_SubleadLep"] = cat_df[tc].Histo1D(("{name}__{cat}__Lepton{lpf}_eta_SubleadLep_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 52,-2.6,2.6), "FTALepton{lpf}_eta_SubleadLep", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Lepton{lpf}_eta_SubleadLep"] = cat_df[tc].Histo1D(("{name}__{cat}__Lepton{lpf}_eta_SubleadLep_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 52,-2.6,2.6), "FTALepton{lpf}_eta_SubleadLep", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dRll"] = cat_df[tc].Histo1D(("{name}__{cat}__dRll_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 16,0,2*pi), "FTALepton{lpf}_dRll", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dPhill"] = cat_df[tc].Histo1D(("{name}__{cat}__dPhill_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 16,-pi,pi), "FTALepton{lpf}_dPhill", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["dEtall"] = cat_df[tc].Histo1D(("{name}__{cat}__dEtall_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 10,0,5), "FTALepton{lpf}_dEtall", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofMETandEl"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofMETandEl_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofMETandEl{}".format(postfix), wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofMETandMu"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofMETandMu_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofMETandMu{}".format(postfix), wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofElandMu"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofElandMu_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofElandMu{}".format(postfix), wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nJet"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 14, 0, 14), "nJet{bpf}", wgtVar)
                if isData is False:
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nJet_genMatched"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_genMatched_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 14, 0, 14), "nJet{bpf}_genMatched", wgtVar)
                    histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nJet_genMatched_puIdLoose"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_genMatched_puIdLoose_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 14, 0, 14), "nJet{bpf}_genMatched_puIdLoose", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nLooseDeepCSV"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_LooseDeepCSV_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nJet{bpf}_LooseDeepCSV", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nMediumDeepCSV"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_MediumDeepCSV_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nJet{bpf}_MediumDeepCSV", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nTightDeepCSV"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_TightDeepCSV_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nJet{bpf}_TightDeepCSV", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nLooseDeepJet"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_LooseDeepJet_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nJet{bpf}_LooseDeepJet", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nMediumDeepJet"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_MediumDeepJet_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nJet{bpf}_MediumDeepJet", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nTightDeepJet"] = cat_df[tc].Histo1D(("{name}__{cat}__nJet_TightDeepJet_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 6, 0, 6), "nJet{bpf}_TightDeepJet", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nLooseMuon"] = cat_df[tc].Histo1D(("{name}__{cat}__nLooseFTAMuon{lpf}_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 4, 0, 4), "nLooseFTAMuon{lpf}", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nMediumMuon"] = cat_df[tc].Histo1D(("{name}__{cat}__nMediumFTAMuon{lpf}_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 4, 0, 4), "nMediumFTAMuon{lpf}", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nTightMuon"] = cat_df[tc].Histo1D(("{name}__{cat}__nTightFTAMuon{lpf}_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 4, 0, 4), "nTightFTAMuon{lpf}", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nLooseElectron"] = cat_df[tc].Histo1D(("{name}__{cat}__nLooseFTAElectron{lpf}_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 4, 0, 4), "nLooseFTAElectron{lpf}", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nMediumElectron"] = cat_df[tc].Histo1D(("{name}__{cat}__nMediumFTAElectron{lpf}_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 4, 0, 4), "nMediumFTAElectron{lpf}", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nTightElectron"] = cat_df[tc].Histo1D(("{name}__{cat}__nTightFTAElectron{lpf}_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 4, 0, 4), "nTightFTAElectron{lpf}", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nLooseLepton"] = cat_df[tc].Histo1D(("{name}__{cat}__nLooseFTALepton{lpf}_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 4, 0, 4), "nLooseFTALepton{lpf}", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nMediumLepton"] = cat_df[tc].Histo1D(("{name}__{cat}__nMediumFTALepton{lpf}_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 4, 0, 4), "nMediumFTALepton{lpf}", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["nTightLepton"] = cat_df[tc].Histo1D(("{name}__{cat}__nTightFTALepton{lpf}_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 4, 0, 4), "nTightFTALepton{lpf}", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofMETandEl"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofMETandEl_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofMETandEl", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofMETandMu"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofMETandMu_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofMETandMu", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["MTofElandMu"] = cat_df[tc].Histo1D(("{name}__{cat}__MTofElandMu_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 20, 0, 200), "MTofElandMu", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_InvMass"] = cat_df[tc].Histo1D(("{name}__{cat}__Muon_InvMass_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 60, 0, 150), "FTAMuon{lpf}_InvariantMass", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_InvMass"] = cat_df[tc].Histo1D(("{name}__{cat}__Electron_InvMass_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 60, 0, 150), "FTAElectron{lpf}_InvariantMass", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_InvMass_v_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_InvMass_v_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 30, 0, 150, 20, 0, 400), "FTAMuon{lpf}_InvariantMass", "METFixEE2017_pt", wgtVar)
                histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_InvMass_v_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_InvMass_v_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), "", 30, 0, 150, 20, 0, 400), "FTAElectron{lpf}_InvariantMass", "METFixEE2017_pt", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 30, 0., 0.2, 20,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso04_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso04_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso04_all;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "RVec_MET_pt", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                
                if isData == False:
                    pass                
            
        if histos2D_dict != None:
            if "sysVar_{spf}".format(spf=syspostfix) not in histos2D_dict:
                histos2D_dict["sysVar{spf}".format(spf=syspostfix)] = {}
            for tc in theCats.keys(): 
                if tc not in histos2D_dict["sysVar{spf}".format(spf=syspostfix)]: 
                    histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc] = {}
            for tc, cut in theCats.items():
                tcn = tc.replace("blind_", "")
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 30, 0., 0.2, 20,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso04_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso04_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso04_all;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "RVec_MET_pt", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                #histos1D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                #### Older versions
                #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 100, 0., 0.2, 100,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 100, 0, 0.2, 100,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Muon_pfRelIso04_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Muon_pfRelIso04_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso04_all;MET", 100, 0, 0.2, 100,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "RVec_MET_pt", wgtVar)
                #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_all_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_all_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_all;MET", 100, 0, 0.2, 100,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "RVec_MET_pt", wgtVar)
                #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["Electron_pfRelIso03_chg_vs_MET"] = cat_df[tc].Histo2D(("{name}__{cat}__Electron_pfRelIso03_chg_vs_MET_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";pfRelIso03_chg;MET", 100, 0, 0.2, 100,30,1030), "FTAElectron{lpf}_pfRelIso03_chg", "RVec_MET_pt", wgtVar)
                if isData == False:
                    #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["test1"] = cat_df[tc].Histo2D(("{name}__{cat}__test1_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAMuon{lpf}_pfRelIso03_all", "PV_npvsGood", wgtVar)
                    #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["test2"] = cat_df[tc].Histo2D(("{name}__{cat}__test2_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAMuon{lpf}_pfRelIso03_all", "METFixEE2017_pt", wgtVar)
                    #histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["npvsGood_vs_nTrueInttest"] = cat_df[tc].Histo2D(("{name}__{cat}__npvsGood_vs_nTrueInttest_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAElectron{lpf}_pfRelIso03_all", "MET_pt_flat", wgtVar)
                    histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["npvsGood_vs_nTrueInt"] = cat_df[tc].Histo2D(("{name}__{cat}__npvsGood_vs_nTrueInt_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvsGood", wgtVar)
                    histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["npvsGood_vs_nPU"] = cat_df[tc].Histo2D(("{name}__{cat}__npvsGood_vs_nPU_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nPU;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvsGood", wgtVar)
                    histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["npvs_vs_nTrueInt"] = cat_df[tc].Histo2D(("{name}__{cat}__npvs_vs_nTrueInt_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nTrueInt;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvs", wgtVar)
                    histos2D_dict["sysVar{spf}".format(spf=syspostfix)][tc]["npvs_vs_nPU"] = cat_df[tc].Histo2D(("{name}__{cat}__npvs_vs_nPU_{spf}".format(name=sampleName, cat=tcn, spf=syspostfix), ";nPU;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvs", wgtVar)
      
            


# In[ ]:


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


# In[ ]:


#def lepMatchingEfficiency(input_df, wgtVar="")

def jetMatchingEfficiency(input_df, max_eta = 2.5, min_pt = 30.0, wgtVar="wgt_SUMW_PU_L1PF", stats_dict=None,
                         isData=True):
    if isData == True:
        pass
    else:
        theCats = collections.OrderedDict()
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
        cat_df = collections.OrderedDict()
        for ck, cs in theCats.items():
            cat_df[ck] = input_df_defined.Filter(cs, "Jet Matching Efficiency " + cs)
            stats_dict[ck] = {}
            stats_dict[ck]["nJet"] = cat_df[ck].Stats("nGJet", wgtVar)
            stats_dict[ck]["nJet_genMatched"] = cat_df[ck].Stats("nGJet_genMatched", wgtVar)
            stats_dict[ck]["nJet_puIdLoose"] = cat_df[ck].Stats("nGJet_puIdLoose", wgtVar)
            stats_dict[ck]["nJet_genMatched_puIdLoose"] = cat_df[ck].Stats("nGJet_genMatched_puIdLoose", wgtVar)

def fillHLTMeans(input_df, wgtVar="wgt_SUMW_PU_L1PF", stats_dict=None, debugInfo=False):
    theCats = collections.OrderedDict()
    theCats["Inclusive"] = "nGJet >= 4"
    theCats["nJet4to5"] = "nGJet == 4 || nGJet == 5"
    theCats["nJet6+"] = "nGJet >= 6"
    
    branches = [branch for branch in input_df.GetColumnNames() if "HLT_" in branch and "Ele" not in branch
                and "Mu" not in branch and "Tau" not in branch]
                #and ("PF" in branch or "HT" in branch or "MET" in branch)]
    #print(branches)
    
    input_df_defined = input_df
    branches_weighted = []
    for branch in branches:
        branches_weighted.append("{}_weighted".format(branch))
        input_df_defined = input_df_defined.Define("{}_weighted".format(branch), 
                                                   "{} == true ? {} : 0".format(branch, wgtVar))
                
    cat_df = collections.OrderedDict()
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


# In[ ]:


def writeHistosForCombine(hist_dict, directory, levels_of_iterest, dict_key="Mountains", mode="RECREATE"):
    rootDict = {}
    if not os.path.isdir(directory):
        os.makedirs(directory)
    for name, levels_dict in hist_dict.items():
        for level, obj_dict in levels_dict.items():
            if level not in levels_of_interest: continue
            if not os.path.isdir(directory + "/" + level):
                os.makedirs(directory + "/" + level)
            for pre_obj_name, obj_val in obj_dict[dict_key].items():
                for hname, hist in obj_val.items():
                    dictKey = pre_obj_name + "_" + hname
                    if dictKey not in rootDict:
                        rootDict[dictKey] = ROOT.TFile.Open("{}.root"                                     .format(directory + "/" + level + "/"+ dictKey), mode)
                    rootDict[dictKey].cd()
                    hptr = hist.GetPtr()
                    oldname = hptr.GetName()
                    hptr.SetName("{}".format(name))
                    hptr.Write()
                    hptr.SetName("{}".format(oldname)) #Avoid overwriting things by switching back, save from segfault
                    #hptr.SetDirectory(0)
    for f in rootDict.values():
        f.Close()
        
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
        
        
        
def writeHistos(hist_dict, directory, levels_of_interest="All", samples_of_interest="All", dict_keys="All", mode="RECREATE"):
    rootDict = {}
    if not os.path.isdir(directory):
        os.makedirs(directory)
    for name, levels_dict in hist_dict.items():
        if samples_of_interest == "All": pass
        elif name not in samples_of_interest: continue
        for level, obj_dict in levels_dict.items():
            if levels_of_interest == "All": pass
            elif level not in levels_of_interest: continue
            if not os.path.isdir(directory + "/" + level):
                os.makedirs(directory + "/" + level)
            rootDict[name] = ROOT.TFile.Open("{}.root"                                         .format(directory + "/" + level + "/"+ name), mode)
            for dict_key in obj_dict.keys():
                if dict_keys == "All": pass
                elif dict_key not in dict_keys: continue

                for pre_obj_name, obj_val in obj_dict[dict_key].items():
                    if type(obj_val) == dict:
                        for hname, hist in obj_val.items():
                            #help(hist)
                            #dictKey = pre_obj_name + "$" + hname
                            #if dictKey not in rootDict:
                            #rootDict[dictKey].cd()
                            hptr = hist.GetPtr()
                            oldname = hptr.GetName()
                            #hptr.SetName("{}".format(dict_key + "*" + pre_obj_name + "*" + hname))
                            hptr.Write()
                            #hptr.SetName("{}".format(oldname)) #Avoid overwriting things by switching back, save from segfault
                    elif "ROOT.TH" in str(type(obj_val)):
                        hptr = obj_val.GetPtr()
                        oldname = hptr.GetName()
                        #hptr.SetName("{}".format(dict_key + "*" + pre_obj_name))
                        hptr.Write()
                        #hptr.SetName("{}".format(oldname)) #Avoid overwriting things by switching back, save from segfault
            print("Wrote histogram file for {} - {}".format(name, directory + "/" + level + "/"+ name))
    for f in rootDict.values():
        f.Close()
        
def makeHLTReport(stats_dict, directory, levels_of_iterest="All"):
    if not os.path.isdir(directory):
        os.makedirs(directory)
    #name, level, weighted/unweighted, category, (count?)
    path_dict = collections.OrderedDict()
    count_dict = collections.OrderedDict()
    all_names = []
    for name, name_dict in stats_dict.items():
        all_names.append(name)
        for level, level_dict in name_dict.items():
            if level not in path_dict.keys():
                path_dict[level] = collections.OrderedDict()
            if level not in count_dict.keys():
                count_dict[level] = collections.OrderedDict()
            if levels_of_interest is not "All" and level not in levels_of_interest: continue
            for stat_category, stat_category_dict in level_dict.items():
                if stat_category is "counts":
                    for category, counter in stat_category_dict.items():
                        count_dict[level][category] = str(counter.GetValue())
                elif stat_category in ["weighted", "unweighted"]:
                    if stat_category not in path_dict[level].keys():
                        path_dict[level][stat_category] = collections.OrderedDict()
                    #pprint.pprint(stat_category_dict)
                    for category, category_dict in stat_category_dict.items():
                        if category not in path_dict[level][stat_category].keys():
                            path_dict[level][stat_category][category] = collections.OrderedDict()
                        for path, count in category_dict.items():
                            if path not in path_dict[level][stat_category][category].keys():
                                #path_dict[level][stat_category][category][path] = collections.OrderedDict()
                                path_dict[level][stat_category][category][path] = {}
                            path_dict[level][stat_category][category][path][name] = str(count.GetValue())
                elif stat_category in ["weightedStats", "weightedStatsSMT"]:
                    if stat_category not in path_dict[level].keys():
                        path_dict[level][stat_category] = collections.OrderedDict()
                    #pprint.pprint(stat_category_dict)
                    for category, category_dict in stat_category_dict.items():
                        if category not in path_dict[level][stat_category].keys():
                            path_dict[level][stat_category][category] = collections.OrderedDict()
                        for path, count in category_dict.items():
                            if path not in path_dict[level][stat_category][category].keys():
                                #path_dict[level][stat_category][category][path] = collections.OrderedDict()
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
            
                    
        


# In[ ]:


##################################################
##################################################
### CHOOSE SAMPLE DICT AND CHANNEL TO ANALYZE ####
##################################################
##################################################

#Focus on limited set of events at a time
#levels_of_interest = set(["ElMu_selection"])
#levels_of_interest = set(["MuMu_selection",])
#levels_of_interest = set(["ElEl_selection",])
#levels_of_interest = set(["selection", "ElMu_selection", "ElEl_selection", "MuMu_selection", "Mu_selection", "El_selection"])
#levels_of_interest = set(["baseline", "MuMu_baseline", "ElEl_baseline", "selection", "MuMu_selection", "ElMu_selection"])
#levels_of_interest = set(["baseline", "MuMu_selection", "ElMu_selection"])

#Choose the sample dictionary to run
#theSampleDict = ttbooker #needs modification to make work...
#theSampleDict = ttttbooker
#theSampleDict = microbooker #tttt, ttbar-DL unfiltered, DY, one single top sample
#theSampleDict = minibooker #tttt, all ttbar, both single top, DY
#theSampleDict = booker #All
#theSampleDict = bookerV2 #All with reprocessing (WIP: Other data streams, ttVJets, Filtered samples!)
#theSampleDict = tt_data_V2
#theSampleDict = pyrdfbooker

#Where to write histograms
analysisDir = "hists20200414"

#trigger verbose output for all the define and histo functions
beVerbose = True

all_samples = ["ElMu", "MuMu", "ElEl", "tttt", "ST_tW", "ST_tbarW", "tt_DL", "tt_DL-GF", 
                 "tt_SL", "tt_SL-GF", "ttH", "ttWJets", "ttZJets", "ttWH", "ttWW", "ttWZ", 
                 "ttZZ", "ttZH", "ttHH", "tttW", "tttJ", "DYJets_DL",]
#Mask samples to divy up work
#valid_samples = ["ElMu", "MuMu", "ElEl", ]
#valid_samples = ["tttt", "ST_tW", "ST_tbarW"]
#valid_samples = ["tt_DL",]
#valid_samples = ["tt_DL-GF",]
#valid_samples = ["tt_SL", "tt_SL-GF",]
#valid_samples = ["ttH", "ttWJets", "ttZJets"]
#valid_samples = ["ttWH", "ttWW", "ttWZ", "ttZZ", "ttZH", "ttHH", "tttW", "tttJ"]
#valid_samples = ["DYJets_DL",]
#valid_samples = ["ElMu", "tttt", "ST_tW", "ST_tbarW"]
valid_samples = all_samples

#Decide on things to do
doHLTMeans = False
doHistos = False
doBtaggingEfficiencies = False
doBtaggingYields = True
doJetEfficiency = False

if doBtaggingYields:
    print("Loading all samples for calculating BtaggingYields")
    #valid_samples = all_samples
    removeThese = []
    #removeThese += ['ttZJets', 'ttH', 'tttW', 'ttZZ', 'tt_SL', 'tttJ'] #done
    #removeThese += ['ttWH', 'tt_SL-GF', 'tt_DL-GF', 'ST_tbarW', 'ttWZ', 'tttt', 'ttWJets'] #done
    #removeThese += ['tt_DL', 'ttHH', 'ElMu', 'ttWW', 'ST_tW', 'DYJets_DL', 'ttZH'] #done
    valid_samples = []
    for sample in all_samples:
        if sample not in removeThese:
            valid_samples.append(sample)
    

#Use skimmed channels flag
useSkimmed = True
chooseChannel = "ElMu"
#chooseChannel = "MuMu"
#chooseChannel = "ElEl"
#chooseChannel = "Mu"
#chooseChannel = "El"
#chooseChannel = "test"
source_level = "LJMLogic"
#source_level = "LJMLogic/ElMu_selection"
#source_level = "LJMLogic/MuMu_selection"
#source_level = "LJMLogic/ElEl_selection"
if chooseChannel == "ElMu":
    levels_of_interest = set(["ElMu_selection",])
    theSampleDict = bookerV2_ElMu.copy()
    theSampleDict.update(bookerV2_MC)
    if useSkimmed == True:
        source_level = "LJMLogic/ElMu_selection"
elif chooseChannel == "MuMu":
    levels_of_interest = set(["MuMu_selection",])
    theSampleDict = bookerV2_MuMu.copy()
    theSampleDict.update(bookerV2_MC)
    if useSkimmed == True:
        source_level = "LJMLogic/MuMu_selection"
elif chooseChannel == "ElEl":    
    levels_of_interest = set(["ElEl_selection",])
    theSampleDict = bookerV2_ElEl.copy()
    theSampleDict.update(bookerV2_MC)
    if useSkimmed == True:
        source_level = "LJMLogic/ElEl_selection"
elif chooseChannel == "Mu":    
    levels_of_interest = set(["Mu_selection",])
    theSampleDict = bookerV2_Mu.copy()
    theSampleDict.update(bookerV2_MC)
    if useSkimmed == True:
        print("No skimmed samples prepared for this selection level, please advise")
elif chooseChannel == "El":    
    levels_of_interest = set(["El_selection",])
    theSampleDict = bookerV2_El.copy()
    theSampleDict.update(bookerV2_MC)
    if useSkimmed == True:
        print("No skimmed samples prepared for this selection level, please advise")
elif chooseChannel == "test":
    levels_of_interest = set(["ElMu_selection", "MuMu_selection", "ElEl_selection"])
    theSampleDict = microbookerV2.copy()
    if useSkimmed == True:
        print("No skimmed samples prepared for this selection level, please advise")




#Choose the weight variation
#theWeight = "wgt_SUMW"
#theWeight = "wgt_SUMW_PU"
#theWeight = "wgt_SUMW_LSF"
#theWeight = "wgt_SUMW_L1PF"
#theWeight = "wgt_SUMW_PU_LSF"
theWeight = "wgt_SUMW_PU_LSF_L1PF"
#theWeight = "wgt_SUMW_LSF_L1PF"
#theWeight = "wgt_NUMW_LSF_L1PF"


# In[ ]:


print("Creating selection and baseline bits")
b = {}
b["ElMu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) > 0".format(Chan["ElMu_baseline"])
b["MuMu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0".format(Chan["ElMu_baseline"], 
                                                                                                                                Chan["MuMu_baseline"])
b["ElEl_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0".format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"], 
                                                                                                                                Chan["ElEl_baseline"])
b["Mu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0".format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"], Chan["Mu_baseline"])
b["El_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0".format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + 
                                                                                                                    Chan["ElEl_baseline"] + Chan["Mu_baseline"], Chan["El_baseline"])
b["selection"] = "ESV_TriggerAndLeptonLogic_selection > 0"
b["ElMu_selection"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) > 0".format(Chan["ElMu_selection"])
b["MuMu_selection"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0".format(Chan["ElMu_selection"], Chan["MuMu_selection"])
b["ElEl_selection"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0".format(Chan["ElMu_selection"] + Chan["MuMu_selection"], Chan["ElEl_selection"])
b["Mu_selection"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0".format(Chan["ElMu_selection"] + Chan["MuMu_selection"] + Chan["ElEl_selection"], Chan["Mu_selection"])
b["El_selection"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0".format(Chan["ElMu_selection"] + Chan["MuMu_selection"] + Chan["ElEl_selection"]
                                                                            + Chan["Mu_selection"], Chan["El_selection"]) 
#b["ESV_JetMETLogic_baseline"] = "(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00001100011111111111) #This enables the MET pt cut (11) and nJet (15) and HT (16) cuts from PostProcessor
b["ESV_JetMETLogic_baseline"] = "(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000001111111111) #Only do the PV and MET filters, nothing else
#b["ESV_JetMETLogic_selection"] = "(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00001100011111111111) #FIXME, this isn't right!
b["ESV_JetMETLogic_selection"] = "(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00001100011111111111)#This enables the MET pt cut (11) and nJet (15) and HT (16) cuts from PostProcessor
b["ESV_JetMETLogic_selection"] = "(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000001111111111)
#b["ESV_JetMETLogic_default"] = "(ESV_JetMETLogic_baseline & {}) > 0".format(0b11111111111111111111)
#print(b["ESV_JetMETLogic_selection"])

stitchDict = {'2016': {'SL': {'nGenJets': None,
                                           'nGenLeps': None,
                                           'GenHT': None},
                                    'DL': {'nGenJets': None,
                                           'nGenLeps': None,
                                           'GenHT': None}
                                },
                           '2017': {'SL': {'nGenJets': 9,
                                           'nGenLeps': 1,
                                           'GenHT': 500},
                                    'DL': {'nGenJets': 7,
                                           'nGenLeps': 2,
                                           'GenHT': 500}
                                },
                           '2018': {'SL': {'nGenJets': 9,
                                           'nGenLeps': 1,
                                           'GenHT': 500},
                                    'DL': {'nGenJets': 7,
                                           'nGenLeps': 2,
                                           'GenHT': 500}
                                }
                       }


filtered = {}
base = {}
reports = {}
#theValidSet = set(["tt_SL", "tt_SL-GF", "tt_DL-GF"])
for name, vals in theSampleDict.items():
    #print("Skipping all samples except {}".format(theValidSet))
    if name not in valid_samples: continue
    print("Initializing RDataFrame - {} - {}".format(name, vals["source"][source_level]))
    filtered[name] = {}
    base[name] = RDF("Events", vals["source"][source_level])
    reports[name] = base[name].Report()
    for lvl in levels_of_interest:
        if "baseline" in lvl:
            JMLOG = "ESV_JetMETLogic_baseline"
        elif "selection" in lvl:
            JMLOG = "ESV_JetMETLogic_selection"
        else:
            JMLOG = "ESV_JetMETLogic_default"
            
        if lvl == "baseline":
            filtered[name][lvl] = base[name]#.Filter(b[JMLOG], JMLOG)#.Cache()
        else:
            filtered[name][lvl] = base[name].Filter(b[lvl], lvl)#.Filter(b[JMLOG], JMLOG)#.Cache()
        #Cache() seemingly has an issue with the depth/breadth of full NanoAOD file. Perhaps one with fewer branches would work
        #filtered[name][lvl] = filtered[name][lvl].Cache()
        if vals.get("stitch") != None:
            stitch_def = collections.OrderedDict()
            stitch_def["stitch_jet_mask"] = "GenJet_pt > 30"
            stitch_def["stitch_HT_mask"] = "GenJet_pt > 30 && abs(GenJet_eta) < 2.4"
            stitch_def["stitch_lep_mask"] = "abs(LHEPart_pdgId) == 15 || abs(LHEPart_pdgId) == 13 || abs(LHEPart_pdgId) == 11"
            stitch_def["stitch_nGenLep"] = "LHEPart_pdgId[stitch_lep_mask].size()"
            stitch_def["stitch_nGenJet"] = "GenJet_pt[stitch_jet_mask].size()"
            stitch_def["stitch_GenHT"] = "Sum(GenJet_pt[stitch_HT_mask])"
            
            stdict = stitchDict[vals.get("era")][vals.get("stitch").get("channel")]
            stitch_cut = "stitch_nGenLep == {} && stitch_nGenJet >= {} && stitch_GenHT >= {}"                .format(stdict.get("nGenLeps"), stdict.get("nGenJets"), stdict.get("GenHT"))
            if vals.get("stitch").get("source") == "Nominal":
                stitch_cut = "!({})".format(stitch_cut)
            elif vals.get("stitch").get("source") == "Filtered":
                pass
            else:
                print("Invalid stitching source type")
                sys.exit(1)
            print(stitch_cut)
            for k, v in stitch_def.items():
                filtered[name][lvl] = filtered[name][lvl].Define("{}".format(k), "{}".format(v))
            filtered[name][lvl] = filtered[name][lvl].Filter(stitch_cut, "nJet_GenHT_Filter")


# In[ ]:


samples = {}
counts = {}
histos1D = {}
histos1D_PU = {}
histos2D = {}
histosNS = {} #unstacked histograms
the_df = {}
stats = {} #Stats for HLT branches
effic = {} #Stats for jet matching efficiencies
btagging = {} #For btagging efficiencies
cat_df = {} #Categorization node dictionary, returned by fillHistos method
masterstart = time.clock()#Timers...
substart = {}
subfinish = {}
processed = {}
processedSampleList = []
print("Starting loop for booking")
for name, vals in theSampleDict.items():
    if name not in valid_samples: continue
    #if name not in ["tttt", "ElMu_F"]: continue
    print("Booking - {}".format(name))
    counts[name] = {}
    histos1D[name] = {}
    histos1D_PU[name] = {}
    histos2D[name] = {}
    histosNS[name] = {}
    the_df[name] = {}
    stats[name] = {}
    effic[name] = {}
    btagging[name] = {}
    cat_df[name] = {}
    substart[name] = {}
    subfinish[name] = {}
    processed[name] = {}
    #counts[name]["baseline"] = filtered[name].Count() #Unnecessary with baseline in levels of interest?
    for lvl in levels_of_interest:
        the_df[name][lvl] = METXYCorr(filtered[name][lvl],
                                      run_branch = "run",
                                      era="2017", 
                                      isData=vals["isData"],
                                      verbose=beVerbose,
                                      )
        the_df[name][lvl] = defineLeptons(the_df[name][lvl], 
                                          input_lvl_filter=lvl,
                                          isData=vals["isData"], 
                                          useBackupChannel=False,
                                          verbose=beVerbose,
                                         )
        #Use the cutPV and METFilters function to do cutflow on these requirements...
        the_df[name][lvl] = cutPVandMETFilters(the_df[name][lvl], lvl, isData=vals["isData"])
        if vals["isData"] == False:
            the_df[name][lvl] = defineInitWeights(the_df[name][lvl],
                                                  crossSection=vals["crossSection"], 
                                                  sumWeights=vals["sumWeights"], 
                                                  lumi=lumi[era],
                                                  nEvents=vals["nEvents"], 
                                                  nEventsPositive=vals["nEventsPositive"], 
                                                  nEventsNegative=vals["nEventsNegative"], 
                                                  isData=vals["isData"], 
                                                  verbose=beVerbose,
                                                 )
        else:
            the_df[name][lvl] = defineInitWeights(the_df[name][lvl],
                                                  isData=True,
                                                  verbose=beVerbose,
                                                 )
        the_df[name][lvl] = defineJets(the_df[name][lvl],
                                       era="2017",
                                       useDeepCSV=True,
                                       isData=vals["isData"],
                                       verbose=beVerbose,
                                      )
        the_df[name][lvl] = defineWeights(the_df[name][lvl],
                                          isData = vals["isData"],
                                          final=False,
                                          verbose=beVerbose,
                                         )
        
        print("Need to make cuts on HT, MET, InvariantMass, ETC.")
        #the_df[name][lvl] = the_df[name][lvl].Filter("nGJet > 2", "nJet > 2")
        #the_df[name][lvl] = the_df[name][lvl].Filter("nGJet > 3", "nJet > 3")
        #the_df[name][lvl] = the_df[name][lvl].Filter("nGJet_MediumDeepCSV > 1")
        #the_df[name][lvl] = the_df[name][lvl].Filter("nGJet_MediumDeepJet > 1", "nMedDeepJet > 1")
        #the_df[name][lvl] = the_df[name][lvl].Filter("METFixEE2017_pt > 40", "MET > 40")
        #the_df[name][lvl] = the_df[name][lvl].Filter("METFixEE2017_pt > 0", "MET > 50")
        #the_df[name][lvl] = the_df[name][lvl].Filter("GJet_HT > 450", "HT > 450")
        #the_df[name][lvl] = the_df[name][lvl].Filter("GJet_HT > 500", "HT > 500")
        counts[name][lvl] = the_df[name][lvl].Count()
        histos1D[name][lvl] = {}
        histos1D_PU[name][lvl] = {}
        histosNS[name][lvl] = {}
        histos2D[name][lvl] = {}
        stats[name][lvl] = {}
        effic[name][lvl] = {}
        btagging[name][lvl] = {}
        cat_df[name][lvl] = {'fillHistos(...)':'NotRunOrFailed'} #will be a dictionary returned by fillHistos, so empty histo if fillHistos not run or fails
        #Define all the btag event weights or calculate yields based on defining the btag pre-event weight
        #as well as nJet_variation, HT_variation if necessary (move to defineJets function later)
        ##yb = the_df[name][lvl].GetDefinedColumnNames()
        ##nb = the_df[name][lvl].GetColumnNames()
        ##print(len(yb), len(nb))
        ##bc = 0
        ##print(the_df[name][lvl])
        ##for branch in yb:
        ##    if "FTAMuon" in branch or "FTAElectron" in branch or "FTALepton" in branch:
        ##        continue
        ##    btype = the_df[name][lvl].GetColumnType(branch)
        ##    if "bool" in str(btype):
        ##        continue
        ##    if "_doublet" in branch:
        ##        continue
        ##    print("Testing branch {} of type {}".format(branch, btype))
        ##    h = the_df[name][lvl].Histo1D(branch)
        ##    hv = h.GetValue()
        ##    n = hv.GetBinContent(1)
        ##    print(n)
        #Calculate or load yields to produce the btag event weights
        if doBtaggingYields == True:
            loadTheYields = None
            calculateTheYields = True
        else:
            loadTheYields = "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/BTaggingYields.root"
            calculateTheYields = False
        #Insert the yields or calculate them
        the_df[name][lvl] = BtaggingYields(the_df[name][lvl], sampleName=name, isData = vals["isData"], 
                                           histos_dict=btagging[name][lvl], loadYields=loadTheYields,
                                           useAggregate=True, calculateYields=calculateTheYields,
                                           HTBinWidth=10, HTMin=200, HTMax=3200,
                                           nJetBinWidth=1, nJetMin=4, nJetMax=20,
                                           verbose=beVerbose,
                                          )
        #Define the final weights/variations so long as we have btagging yields inserted...
        if loadTheYields:
            the_df[name][lvl] = defineWeights(the_df[name][lvl],
                                              isData = vals["isData"],
                                              final=True,
                                              verbose=beVerbose,
                                             )
        if doBtaggingEfficiencies == True:
            BtaggingEfficiencies(the_df[name][lvl], sampleName=None, era="2017", wgtVar="wgt_SUMW_PU_LSF_L1PF", 
                           isData = vals["isData"], histos_dict=btagging[name][lvl], 
                           doDeepCSV=True, doDeepJet=True, debugInfo=False)
        if doJetEfficiency:
            jetMatchingEfficiency(the_df[name][lvl], wgtVar="wgt_SUMW_PU_LSF_L1PF", stats_dict=effic[name][lvl],
                                  isData = vals["isData"])
        if doHLTMeans:
            fillHLTMeans(the_df[name][lvl], wgtVar="wgt_SUMW_PU_L1PF", stats_dict=stats[name][lvl])
        #Hold the categorization nodes if doing histograms
        if doHistos:
            cat_df[name][lvl] = fillHistos(the_df[name][lvl], wgtVar=theWeight, isData = vals["isData"],
                                           histos1D_dict=histos1D[name][lvl], histos2D_dict=histos2D[name][lvl], 
                                           histosNS_dict=histosNS[name][lvl],
                                           doMuons=False, doElectrons=False, doLeptons=False, 
                                           doJets=False, doWeights=False, doEventVars=False,
                                           makeMountains=True, useDeepCSV=True)
        #print(cat_df)
            
        #Trigger the loop
        substart[name][lvl] = time.clock()
        processed[name][lvl] = counts[name][lvl].GetValue()
        subfinish[name][lvl] = time.clock()
        theTime = subfinish[name][lvl] - substart[name][lvl]
        #Write the output!
        if doBtaggingYields:
            writeHistos(btagging,
                        analysisDir + "/BTagging",
                        levels_of_interest=[lvl],
                        samples_of_interest=[name],
                        dict_keys="All",
                        mode="RECREATE"
                       )
        if doHistos:
            writeHistos(histos1D,
                        analysisDir,
                        levels_of_interest=[lvl],
                        samples_of_interest=[name],
                        dict_keys="All",
                        mode="RECREATE"
                       )
            
        #Add sample name to the list of processed samples and print it, in case things ****ing break in Jupyter Kernel
        processedSampleList.append(name)
        print("Processed Samples:")
        print(processedSampleList)
        print("Took {}m {}s ({}s) to process {} events from sample {} in channel {}\n\n\n{}"             .format(theTime//60, theTime%60, theTime, processed[name][lvl], 
                     name, lvl, "".join(["\_/"]*25)))
#        fillHistos(the_df[name][lvl], wgtVar="wgt_SUMW_PU_LSF", histos1D_dict=histos1D[name][lvl], 
#                   histos2D_dict=histos2D[name][lvl], histosNS_dict=histosNS[name][lvl],
#                   doMuons=False, doElectrons=False, doLeptons=True, 
#                   doJets=False, doWeights=True, doEventVars=False)
#        fillHistos(the_df[name][lvl], wgtVar="wgt_SUMW_PU", histos1D_dict=histos1D[name][lvl], 
#                   histos2D_dict=histos2D[name][lvl], histosNS_dict=histosNS[name][lvl],
#                   doMuons=False, doElectrons=False, doLeptons=False, 
#                   doJets=False, doWeights=False, doEventVars=True)
#        fillHistos(the_df[name][lvl], wgtVar="wgt_SUMW_PU", histos1D_dict=histos1D_PU[name][lvl], 
#                   histos2D_dict=histos2D[name][lvl], histosNS_dict=histosNS[name][lvl],
#                   doMuons=True, doElectrons=True, doLeptons=True, 
#                   doJets=True, doWeights=True, doEventVars=False)


# In[ ]:


print("Warning: if filtered[name][lvl] RDFs are not reset, then calling Define(*) on them will cause the error"      " with 'program state reset' due to multiple definitions for the same variable")
loopcounter = 0
masterstart = time.clock()
substart = {}
subfinish = {}
for name, cnt in counts.items():
    #if name in ["MuMu", "ElMu", "ElEl"]: continue
    substart[name] = time.clock()
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
finish = time.clock()
masterfinish = time.clock()


# In[ ]:


for name, val in substart.items():
    print("Took {}s to process sample {}".format(subfinish[name] - substart[name], name))
print()
masterfinish = time.time() #clock gives cpu time, not accurate multi-core?
print("Took {}m {}s to process in real-time".format((masterfinish - masterstart)//60, (masterfinish - masterstart)%60))


# In[ ]:


def BtaggingYieldsAnalyzer(directory, outDirectory="{}", globKey="*.root", stripKey=".root",
                           internalKeys = {"Numerators":["_sumW_before"],
                                           "Denominator": "_sumW_after",
                                          },
                           internalKeysReplacements = {"BtaggingYield": "",
                                                       "_sumW_before": "",
                                                       "_sumW_after": "",
                                                      },
                           sample_rebin={"default": {"Y": [4, 5, 6, 7, 8, 9, 20],
                                                     "X": [500.0, 600, 700.0, 900.0, 1100.0, 3200.0],
                                                    },
                                         },
                           overrides={"Title": "$NAME BtaggingYield r=#frac{#Sigma#omega_{before}}{#Sigma#omega_{after}}($INTERNALS)",
                                      "Xaxis": "H_{T} (GeV)",
                                      "Yaxis": "nJet",
                                     },
                           mode="RECREATE", doNumpyValidation=False, forceDefaultRebin=False, debug=False, debug_dict={}):
    """For btagging yield ratio calculations using method 1d (shape corrections)
    
    take list of files in <directory>, with optional <globKey>, and create individual root files containing
    each sample's btagging yield ratio histograms, based on derived categories. 
    
    
    #FIXME (below this line)
    Keys can be parsed with 
    <name_format> (default 'BtaggingYield*btagPreSF_$VARIATION*$SUM') where $CAT, $JETTYPE, and $TAG are cycled through from 
    their respective input lists, format_dict{<categories>, <jettypes>, <tags>}. The format_dict{<untag>} option 
    specifies the denominator histogram (where $TAG is replaced by <untag>). A file 'ttWH.root' with 
    'Btagging*nJet4*bjets_DeepJet_T' will generate a file 'ttWH_BTagEff.root' containing the histogram 
    'nJet4_bjets_DeepJet_T'"""
    
    if doNumpyValidation == True:
        #FORCE consistent binning and warn the user
        print("Setting rebinning to the default")
        forceDefaultRebin = True
        if 'numpy' not in dir() and 'np' not in dir():
            try:
                import numpy as np
            except Exception as e:
                raise RuntimeError("Could not import the numpy (as np) module in method BtaggingYieldsAnalyzer")
    
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
            raise RuntimeError("Could not import the glob module in method BtaggingYieldsAnalyzer")
    if 'copy' not in dir():
        try:
            import copy
        except Exception as e:
            raise RuntimeError("Could not import the copy module in method BtaggingYieldsAnalyzer")
    files = glob.glob("{}/{}".format(directory, globKey))
    #deduce names from the filenames, with optional stripKey parameter that defaults to .root
    names = [fname.split("/")[-1].replace(stripKey, "") for fname in files]
    fileDict = {}
    oFile = ROOT.TFile.Open("{}/BTaggingYields.root".format(outDirectory).replace("//", "/"),"RECREATE")
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
            x_rebin = sample_rebin.get(name, sample_rebin.get("default"))["X"]
            y_rebin = sample_rebin.get(name, sample_rebin.get("default"))["Y"]
        else:
            x_rebin = sample_rebin.get("default")["X"]
            y_rebin = sample_rebin.get("default")["Y"]
            
        #index everything by the numerator for later naming purposes: $SAMPLENAME_$NUMERATOR style
        for tbr, stripped_numerator, stripped_denominator in uniqueTuples:
            numerator = "{}_{}".format(name, stripped_numerator)
            denominator = "{}_{}".format(name, stripped_denominator)
            #Rebinning for this specific numerator. If "1DY" or "1DX" is in the name, there's only 1 bin 
            #in the other axis, i.e. 1DY = normal Y bins, 1 X bin
            this_y_rebin = copy.copy(y_rebin)
            this_x_rebin = copy.copy(x_rebin)
            if "1DY" in numerator:
                this_x_rebin = [x_rebin[0]] + [x_rebin[-1]]
            if "1DX" in numerator:
                this_y_rebin = [y_rebin[0]] + [y_rebin[-1]]
                
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
                numerators_dict[name][numerator], yield_dict_num[name][numerator], yield_err_dict_num[name][numerator] =                                                                 rebin2D(numerators_dict[name][numerator],
                                                                "{}_{}".format(name, internals),
                                                                this_x_rebin,
                                                                this_y_rebin,
                                                                return_numpy_arrays=True,
                                                                )
                denominator_dict[name][numerator], yield_dict_den[name][numerator], yield_err_dict_den[name][numerator] =                                                                 rebin2D(denominator_dict[name][numerator],
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
                yield_err_dict_num[name][numerator], yield_err_dict_num[name][numerator] = numpy_div_and_error(
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
    #Get the rebinning lists with a default fallback, but it will be forced when doNumpyValidation is true
    if forceDefaultRebin == False:
        x_rebin = sample_rebin.get(name, sample_rebin.get("default"))["X"]
        y_rebin = sample_rebin.get(name, sample_rebin.get("default"))["Y"]
    else:
        x_rebin = sample_rebin.get("default")["X"]
        y_rebin = sample_rebin.get("default")["Y"]
    for numerator in numerators_dict["Aggregate"].keys():
        #Rebinning for this specific numerator. If "1DY" or "1DX" is in the name, there's only 1 bin 
        #in the other axis, i.e. 1DY = normal Y bins, 1 X bin
        that_y_rebin = copy.copy(y_rebin)
        that_x_rebin = copy.copy(x_rebin)
        if "1DY" in numerator:
            that_x_rebin = [x_rebin[0]] + [x_rebin[-1]]
        if "1DX" in numerator:
            that_y_rebin = [y_rebin[0]] + [y_rebin[-1]]
        internals = copy.copy(numerator)
        for k, v in internalKeysReplacements.items():
            internals = internals.replace(k, v)
        if doNumpyValidation:
            numerators_dict[name][numerator], yield_dict_num[name][numerator + "Cross"], yield_err_dict_num[name][numerator + "Cross"] =                                                             rebin2D(numerators_dict[name][numerator],
                                                            "{}_{}".format(name, internals),
                                                            that_x_rebin,
                                                            that_y_rebin,
                                                            return_numpy_arrays=True,
                                                            )
            denominator_dict[name][numerator], yield_dict_den[name][numerator + "Cross"], yield_err_dict_den[name][numerator + "Cross"] =                                                             rebin2D(denominator_dict[name][numerator],
                                                            "{}_{}_denominator".format(name, internals),
                                                            that_x_rebin,
                                                            that_y_rebin,
                                                            return_numpy_arrays=True,
                                                            )
        else:
            numerators_dict[name][numerator] = rebin2D(numerators_dict[name][numerator],
                                                        "{}_{}".format(name, internals),
                                                        that_x_rebin,
                                                        that_y_rebin,
                                                        )
            denominator_dict[name][numerator] = rebin2D(denominator_dict[name][numerator],
                                                        "{}_{}_denominator".format(name, internals),
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
                yield_err_dict_num[name][numerator], yield_err_dict_num[name][numerator] = numpy_div_and_error(
                    yield_dict_num[name][numerator],
                    yield_err_dict_num[name][numerator], 
                    yield_dict_den[name][numerator], 
                    yield_err_dict_den[name][numerator]
                )
    #close the output file
    oFile.Close() 
 
    
def BtaggingEfficienciesAnalyzer(directory, outDirectory="{}/BtaggingEfficiencies", globKey="*.root", stripKey=".root", 
                       name_format="Btagging*$CAT*$JETTYPE_$TAG",
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
    <name_format> (default 'Btagging*$CAT*$JETTYPE_$TAG') where $CAT, $JETTYPE, and $TAG are cycled through from 
    their respective input lists, format_dict{<categories>, <jettypes>, <tags>}. The format_dict{<untag>} option 
    specifies the denominator histogram (where $TAG is replaced by <untag>). A file 'ttWH.root' with 
    'Btagging*nJet4*bjets_DeepJet_T' will generate a file 'ttWH_BTagEff.root' containing the histogram 
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
            raise RuntimeError("Could not import the glob module in method BtaggingEfficienciesAnalyzer")
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
        keysDict[name] = [hist.GetName() for hist in fileDict[name].GetListOfKeys() if "Btagging*" in hist.GetName()]
        #Skip files without Btagging 
        if len(keysDict[name]) is 0: 
            print("Skipping sample {} whose file contains no histograms containing 'Btagging*'".format(name))
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
                        eff_dict[name][jettype][cat][tag], eff_err_dict[name][jettype][cat][tag] = numpy_div_and_error(
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
                    eff_dict["Aggregate"][jettype][cat][tag], eff_err_dict["Aggregate"][jettype][cat][tag] = numpy_div_and_error(
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
    #Get xrange objects that store the bins to be projected and added
    ybinsrange = [xrange(nybins[:-1][z], nybins[1:][z]) for z in xrange(len(nybins)-1)]
    
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
        #ybinset is an xrange object, so iterate through it for each ybin to be added in this slice
        for bn, ybin in enumerate(ybinset):
            #Create hist for this slice if it's the first bin being combined
            if bn is 0:
                slice_dict[str(sn)]["hist"] = hist.ProjectionX("{}_Yslice{}".format(hist.GetName(), sn), ybin, ybin)
            #THAdd the rest of the bins being combined into this slice
            else:
                slice_dict[str(sn)]["hist"].Add(hist.ProjectionX("{}_Yslice{}_subslice{}".format(hist.GetName(), sn, bn), ybin, ybin))
            
            #If it's the last bin for this slice, do the X rebinning
            if bn is len(ybinset)-1:
                #make sure to get the return value, don't try to rebin in place
                slice_dict[str(sn)]["hist"] = slice_dict[str(sn)]["hist"].Rebin(len(xbins)-1, "", xbins_vec)
        #Carry over slice content and errors to the new histogram, remembering sn starts at 0, and non-underflow
        #in histograms begins at 1 (overflow at NBins + 1, requiring us to add 2 when creating an xrange object)
        #print(slice_dict[str(sn)])
        for fbn in xrange(slice_dict[str(sn)]["hist"].GetXaxis().GetNbins()+2):
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
        for x in xrange(nBinsX):
            for y in xrange(nBinsY):
                hist_contents[nBinsY-1-y, x] = final_hist.GetBinContent(x, y)
                hist_errors[nBinsY-1-y, x] = final_hist.GetBinError(x, y)
        return final_hist, hist_contents, hist_errors
    else:
        return final_hist
    
def numpy_div_and_error(num, num_err, den, den_err):
    """Take 4 numpy arrays containing the numerator, numerator errors, denominator, and denominator errors.
    Compute the division and appropriate error"""
    
    if 'numpy' not in dir() and 'np' not in dir():
        try:
            import numpy as np
        except Exception as e:
            raise RuntimeError("Could not import the numpy module in method numpy_div_and_error")
    
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
        print("{} :: {}\n\tTest Result: ChiSquare/ndf: {} ndf: {} p-value: {}"              .format(tup[0], tup[1], float(tup[2].value)/float(tup[3].value), tup[3].value, tup[5]))
        
    


# In[ ]:


def cartesian_product_list(name_format="$NUM_$LET_$SYM", name_tuples=[("$NUM", ["1", "2"]), ("$LET", ["A", "B", "C"]), ("$SYM", ["*", "@"])]):
    """Take as input a string <name_format> and list of tuples <name_tuple> where a cartesian product of the tuples is formed.
    The tuples contain a key-string (also present in the name_format string) and value-list with the replacements to cycle through.
    The last tuple is the innermost replacement in the list formed, regardless of placement in the name_format string."""
    if 'copy' not in dir():
        try:
            import copy
        except:
            raise RuntimeError("Could not import the copy module in method cartesian_product_list")
    if 'itertools' not in dir():
        try:
            import itertools
        except:
            raise RuntimeError("Could not import the itertools module in method cartesian_product_list")
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

def root_to_pdf(directory, outDirectory="{}/PDF", globKey="*.root", stripKey=".root", 
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
            raise RuntimeError("Could not import the glob module in method root_to_pdf")
    files = glob.glob("{}/{}".format(directory, globKey))
    #deduce names from the filenames, with optional stripKey parameter that defaults to .root
    names = [fname.split("/")[-1].replace(stripKey, "") for fname in files]
    fileDict = {}
    oFileDict = {}
    keysDict = {}
    
    draw_list = cartesian_product_list(name_format=name_format, name_tuples=name_tuples)
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
        if len(keysDict[name]) is 0: 
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


def makeJetEfficiencyReport(input_stats_dict, directory, levels_of_iterest="All"):
    if not os.path.isdir(directory):
        os.makedirs(directory)
    stats_dict = collections.OrderedDict()
    all_names = []
    for name, name_dict in input_stats_dict.items():
        all_names.append(name)
        for level, level_dict in name_dict.items():
            if level not in stats_dict.keys():
                stats_dict[level] = collections.OrderedDict()
            if name not in stats_dict[level].keys():
                stats_dict[level][name] = collections.OrderedDict()
            if levels_of_interest is not "All" and level not in levels_of_interest: continue
            for category, category_dict in level_dict.items():
                if category not in stats_dict[level].keys():
                    stats_dict[level][name][category] = collections.OrderedDict()
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


# In[ ]:


histDir = "select_20200414"
#pprint.pprint(stats['DYJets_DL']['ElMu_selection'])
mode="RECREATE"
#mode="UPDATE"
if doHLTMeans == True:
    makeHLTReport(stats, histDir)
if doHistos == True:
    writeHistos(histos1D, histDir, "All", mode=mode)
    mode="UPDATE"
if doBtaggingEfficiencies == True:
    writeHistos(btagging, histDir, "All", mode=mode)
    mode="UPDATE"
    BtaggingEfficienciesAnalyzer("{}/ElMu_selection".format(histDir))
if doBtaggingYields == True:
    writeHistos(btagging, histDir, "BtaggingYields", mode=mode)
    mode="UPDATE"


# In[ ]:


dbdict={}
#BtaggingEfficienciesAnalyzer("select_20200323/ElMu_selection", doNumpyValidation=True, debug=True, debug_dict=dbdict)
BtaggingYieldsAnalyzer("hists20200414/BTagging/ElMu_selection")


# In[ ]:


ChiSquareTest("select_20200403/ElMu_selection/BtaggingYields/BTaggingYields.root", test_against="Aggregate__deepcsv", 
              must_not_contain = ["up", "down"])
ChiSquareTest("select_20200403/ElMu_selection/BtaggingYields/BTaggingYields.root", test_against="Aggregate__deepcsv", 
              must_contain = ["Aggregate"])
root_to_pdf("select_20200403/ElMu_selection/BtaggingYields",
            outDirectory="{}/PDFSamples",
            name_format="$NAME__$ALGO$VAR",
            name_tuples=[("$NAME", ["Aggregate", "tt_DL-GF", "tt_DL", "tttt", "ttH"," tt_SL-GF", "tt_SL", 
                                    "DYJets_DL", "ST_tW", "ST_tbarW", "ttHH", "ttWH", "ttWJets", "ttWW", "ttWZ",
                                    "ttZJets", "ttZZ", "ttZH", "tttJ", "tttW"]), 
                         ("$ALGO", ["deepcsv"]),
                         ("$VAR", ["",])],
            draw_option="COLZ TEXT45E", draw_min=0.8, draw_max=1.2)
root_to_pdf("select_20200403/ElMu_selection/BtaggingYields",
            outDirectory="{}/PDFVariations",
            name_format="$NAME__$ALGO$VAR",
            name_tuples=[("$NAME", ["Aggregate",]), 
                         ("$ALGO", ["deepcsv"]),
                         ("$VAR", ["", "_shape_up_hf", "_shape_down_hf"])],
            draw_option="COLZ TEXT45E", draw_min=0.8, draw_max=1.2)


# In[ ]:


np.set_printoptions(precision=10, linewidth=125)
print(dbdict['agg_eff'])
print("-----------------------------------------------------------------------------------------------")
print(dbdict['agg_err'])


# In[ ]:


if doHistos == True:
    histoCombine("{}/ElMu_selection".format(histDir))


# In[ ]:


histDir = "select_20200323"
root_to_pdf("{}/ElMu_selection/BtaggingEfficiencyNotWorking".format(histDir),
         name_tuples=[("$JETTYPE", ["bjets", "cjets", "udsgjets"]), ("$TAG", ["DeepCSV_M", "DeepJet_M"]),
                         ("$CAT", ["Inclusive",])],
         draw_option="COLZ TEXT45E",
        )


# In[ ]:


makeJetEfficiencyReport(effic, "{}/ElMu_selection/BtaggingEfficiency".format(histDir))


# In[ ]:


rootDict = {}
histDir = "select_20200310"
if not os.path.isdir(histDir):
    os.makedirs(histDir)
for name, levels_dict in histos1D.items():
    #if "DY" not in name and "t" not in name: continue
    #if theSampleDict[name]["isData"] == True: continue
    print(name, end='')
    #print(theSampleDict[name].keys())
    print(" - c=" + str(theSampleDict[name]["color"]))
    for level, obj_dict in levels_dict.items():
        if level not in levels_of_interest: continue
        if not os.path.isdir(histDir + "/" + level):
            os.makedirs(histDir + "/" + level)
        print("\t" + level)
        print(obj_dict.keys())
        for pre_obj_name, obj_val in obj_dict["Mountains"].items():
            obj_name = "Mountains_" + pre_obj_name
            print("\t\t" + obj_name)
            for hname, hist in obj_val.items():
                #print("\t\t\t" + hname)
                #help(hist)
                dictKey = pre_obj_name + "_" + hname
                if dictKey not in rootDict:
                    rootDict[dictKey] = ROOT.TFile.Open("{}.root"                                 .format(histDir + "/" + level + "/"+ dictKey), "RECREATE")
                rootDict[dictKey].cd()
                hptr = hist.GetPtr()
                oldname = hptr.GetName()
                hptr.SetName("{}".format(name))
                hptr.Write()
                hptr.SetName("{}".format(oldname)) #Avoid overwriting things by switching back, save from segfault
for f in rootDict.values():
    f.Close()


# In[ ]:


for name, report in reports.items():
    if "El" in name or "Mu" in name: continue
    print("{}".format(name))
    report.Print()


# In[ ]:


fff = ROOT.TCanvas("fff", "", 800, 600)
fff.cd()
histos1D["tt_DL-GF"]["MuMu_selection"]["Mountains"]['nMediumDeepJet2']['Muon_InvMass'].Draw("COLZ TEXT")
fff.Draw()


# In[ ]:


stacks = {}
stacksource = {} #Create sortable lists to fill stacks from
stacksource_data = {} #create separte list to append all the data to, so that they can be conbined into one hist file and added to the stacksoure at the end
model_dict = [histos1D[k] for k in theSampleDict.keys() if theSampleDict[k]["isData"] == False]
model_dict = model_dict[0]
if len(model_dict) < 1:
    raise RuntimeError("Failure, no histogram dictionary found to form stacks from")
for level, obj_dict in model_dict.items():
    if level not in levels_of_interest: continue
    stacks[level] = {}
    stacksource[level] = {}
    stacksource_data[level] = {}
    for obj_name, obj_val in obj_dict.items():
        if obj_name == "Mountains": continue #extra depth to account for, custom implementation until next version developed
        stacks[level][obj_name] = {}
        stacksource[level][obj_name] = {}
        stacksource_data[level][obj_name] = {}
        for hname, hist in obj_val.items():
            stacks[level][obj_name][hname] = []
            stacks[level][obj_name][hname].append(ROOT.THStack("s_{}_{}_{}".format(level, obj_name, hname), "{}_{}_{}".format(level, obj_name, hname)))
            stacksource[level][obj_name][hname] = []
            stacksource_data[level][obj_name][hname] = []
    for pre_obj_name, obj_val in obj_dict["Mountains"].items():
        obj_name = "Mountains_" + pre_obj_name
        stacks[level][obj_name] = {}
        stacksource[level][obj_name] = {}
        stacksource_data[level][obj_name] = {}
        for hname, hist in obj_val.items():
            stacks[level][obj_name][hname] = []
            stacks[level][obj_name][hname].append(ROOT.THStack("s_{}_{}_{}".format(level, obj_name, hname), "{}_{}_{}".format(level, obj_name, hname)))
            stacksource[level][obj_name][hname] = []
            stacksource_data[level][obj_name][hname] = []
for name, levels_dict in histos1D.items():
    #if "DY" not in name and "t" not in name: continue
    #if theSampleDict[name]["isData"] == True: continue
    print(name, end='')
    #print(theSampleDict[name].keys())
    print(" - c=" + str(theSampleDict[name]["color"]))
    for level, obj_dict in levels_dict.items():
        if level not in levels_of_interest: continue
        print("\t" + level)
        for pre_obj_name, obj_val in obj_dict["Mountains"].items():
            obj_name = "Mountains_" + pre_obj_name
            print("\t\t" + obj_name)
            for hname, hist in obj_val.items():
                print("\t\t\t" + hname)
                #help(hist)
                hptr = hist.GetPtr().Clone()
                hptr.SetFillColor(theSampleDict[name]["color"])
                hptr.SetLineColor(theSampleDict[name]["color"])
                #stacks[level][obj_name][hname].Add(hptr)
                #stacksource[level][obj_name][hname].append((hptr, hptr.GetIntegral()))
                #Integral fails sometimes, use sum of weights...
                if theSampleDict[name]["isData"] == False:
                    stacksource[level][obj_name][hname].append((hptr, hptr.GetSumOfWeights(), theSampleDict[name]["isData"]))
                else:
                    stacksource_data[level][obj_name][hname].append((hptr, hptr.GetSumOfWeights(), theSampleDict[name]["isData"]))
        for obj_name, obj_val in obj_dict.items():
            if obj_name == "Mountains": continue #extra depth to account for, custom implementation until next version developed
            print("\t\t" + obj_name)
            for hname, hist in obj_val.items():
                print("\t\t\t" + hname)
                #help(hist)
                hptr = hist.GetPtr().Clone()
                hptr.SetFillColor(theSampleDict[name]["color"])
                hptr.SetLineColor(theSampleDict[name]["color"])
                #stacks[level][obj_name][hname].Add(hptr)
                #stacksource[level][obj_name][hname].append((hptr, hptr.GetIntegral()))
                #Integral fails sometimes, use sum of weights...
                if theSampleDict[name]["isData"] == False:
                    stacksource[level][obj_name][hname].append((hptr, hptr.GetSumOfWeights(), theSampleDict[name]["isData"]))
                else:
                    stacksource_data[level][obj_name][hname].append((hptr, hptr.GetSumOfWeights(), theSampleDict[name]["isData"]))
print()
#Now cycle through and sort each list, once it contains all hists from every source (outermost loop - name - above)
print(stacksource_data)
for level, obj_dict in model_dict.items():
    if level not in levels_of_interest: continue
    for pre_obj_name, obj_val in obj_dict["Mountains"].items():
        obj_name = "Mountains_" + pre_obj_name
        for hname, hist in obj_val.items():
            #Sort the MC-only histograms
            stacksource[level][obj_name][hname].sort(key=lambda b: b[1], reverse=False)
            
            #Create a MC-only histogram for statistics purposes
            tmpMC = None
            for himc, h_mc in enumerate(stacksource[level][obj_name][hname]):
                if himc == 0:
                    #take first histo
                    tmpMC = h_mc[0].Clone()
                    tmpMC.SetTitle("MC")
                else:
                    #hadd the other histos
                    #tmpMC = tmpMC + h_mc[0].Clone()
                    tmpMC.Add(h_mc[0].Clone())
            if tmpMC != None:
                #tmpMC.SetMarkerStyle(0)
                tmpMC.SetLineColor(ROOT.kRed)  #FIXME Color from largest sample?
                tmpMC.SetFillColorAlpha(ROOT.kRed, 0) #FIXME
            stacks[level][obj_name][hname].append(tmpMC)
            
            tmp = None
            for hid, h_data in enumerate(stacksource_data[level][obj_name][hname]):
                if hid == 0:
                    #take first histo
                    tmp = h_data[0].Clone()
                    tmp.SetTitle("Data")
                else:
                    #hadd the other histos
                    #tmp = tmp + h_data[0].Clone()
                    tmp.Add(h_data[0].Clone())
            if tmp != None:
                tmp.SetMarkerStyle(0) #20 round dot, with SetMarkerSize(1.0) in an example
                tmp.SetLineColor(ROOT.kBlack)
                tmp.SetFillColorAlpha(ROOT.kWhite, 0)
            stacks[level][obj_name][hname].append(tmp)
                
            for hptrTup in stacksource[level][obj_name][hname]:
                #add to the THStack in the first position of the tuple
                stacks[level][obj_name][hname][0].Add(hptrTup[0])
    for obj_name, obj_val in obj_dict.items():
        if obj_name == "Mountains": continue #extra depth to account for, custom implementation until next version developed
        for hname, hist in obj_val.items():
            #Sort the MC-only histograms
            stacksource[level][obj_name][hname].sort(key=lambda b: b[1], reverse=False)
            
            #Create a MC-only histogram for statistics purposes
            tmpMC = None
            for himc, h_mc in enumerate(stacksource[level][obj_name][hname]):
                if himc == 0:
                    #take first histo
                    tmpMC = h_mc[0].Clone()
                    tmpMC.SetTitle("MC")
                else:
                    #hadd the other histos
                    #tmpMC = tmpMC + h_mc[0].Clone()
                    tmpMC.Add(h_mc[0].Clone())
            if tmpMC != None:
                #tmpMC.SetMarkerStyle(0)
                tmpMC.SetLineColor(ROOT.kRed) #FIXME Color set to highest integral's
                tmpMC.SetLineWidth(0)
                tmpMC.SetFillColorAlpha(ROOT.kRed, 0)
            stacks[level][obj_name][hname].append(tmpMC)
            
            tmp = None
            for hid, h_data in enumerate(stacksource_data[level][obj_name][hname]):
                if hid == 0:
                    #take first histo
                    tmp = h_data[0].Clone()
                    tmp.SetTitle("Data")
                else:
                    #hadd the other histos
                    #tmp = tmp + h_data[0].Clone()
                    tmp.Add(h_data[0].Clone())
            if tmp != None:
                tmp.SetMarkerStyle(0) #20 round dot, with SetMarkerSize(1.0) in an example
                tmp.SetLineColor(ROOT.kBlack)
                #tmp.SetFillColorAlpha(ROOT.kWhite, 0)
            stacks[level][obj_name][hname].append(tmp)
                
            for hptrTup in stacksource[level][obj_name][hname]:
                #add to the THStack in the first position of the tuple
                stacks[level][obj_name][hname][0].Add(hptrTup[0])


# In[ ]:


#c2 = ROOT.TCanvas()
#c2.cd()
#histos2D["tttt"]["ElMu_selection"]["Mountains"]["nMediumDeepCSV0"]["npvsGood_vs_nTrueInt"].Draw("COLZ")
#c2.Draw()


# In[ ]:


leg = ROOT.TLegend(0.75,0.80, 0.95, 0.90)
#leg = ROOT.TLegend(0.15,0.10)
#leg.SetFillColor(0)
#leg.SetBorderSize(0)
leg.SetNColumns(2)
leg.SetTextSize(0.03)
leg_colors = set([smpl["color"] for smpl in theSampleDict.values()])
leg_tuple = [(smpl[0], smpl[1]) for smpl in leg_dict.items() if smpl[1] in leg_colors]
leg_hists = {}
for samplecategory, color in leg_tuple:
    leg_hists[color] = ROOT.TH1D(samplecategory, samplecategory, 0, 0, 1)
    if samplecategory != "Data":
        leg_hists[color].SetFillColor(color)
        leg.AddEntry(leg_hists[color], samplecategory, "F")
    else:
        leg.AddEntry(leg_hists[color], samplecategory, "P")
get_ipython().magic(u'jsroot on')
#help(ROOT.TLegend)


# In[ ]:


get_ipython().magic(u'jsroot off')
for obj_name, obj_dict in stacks["ElMu_selection"].items():
    if obj_name != "Jets": continue
    print(obj_name)
    for sname, stack in obj_dict.items():
        c = ROOT.TCanvas("cs_{}_{}".format(obj_name, sname), "", 800, 600)
        c.cd()
        c.Update()
        #For data first
        #if len(stack) > 1:
        #    stack[1].Draw("PE1")
        #    stack[0].Draw("HIST SAME")
        #else:
        #    stack[0].Draw("HIST")
        #if len(stack) > 1:
        #    stack[1].Draw("PE1 SAME")
        #for MC first
        stack[0].Draw("HIST S")
        #The `mode` has up to nine digits that can be set to on (1 or 2), off (0).
 
         #mode = ksiourmen  (default = 000001111)
         #k = 1;  kurtosis printed
         #k = 2;  kurtosis and kurtosis error printed
         #s = 1;  skewness printed
         #s = 2;  skewness and skewness error printed
         #i = 1;  integral of bins printed
         #i = 2;  integral of bins with option "width" printed
         #o = 1;  number of overflows printed
         #u = 1;  number of underflows printed
         #r = 1;  standard deviation printed
         #r = 2;  standard deviation and standard deviation error printed
         #m = 1;  mean value printed
         #m = 2;  mean and mean error values printed
         #e = 1;  number of entries printed
         #n = 1;  name of histogram is printed
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1111111)
            stack[1].Draw("SAMES")
        if len(stack) > 2 and stack[2] != None:
            ROOT.gStyle.SetOptStat(1111111)
            stack[2].Draw("PE1 SAMES")
        # Add header
        cms_label = ROOT.TLatex()
        cms_label.SetTextSize(0.04)
        cms_label.DrawLatexNDC(0.16, 0.92, "#bf{CMS Preliminary}")
        header = ROOT.TLatex()
        header.SetTextSize(0.03)
        header.DrawLatexNDC(0.63, 0.92, "#sqrt{{s}} = 13 TeV, L_{{int}} = {0} fb^{{-1}}".format(lumi[era]))
        leg.Draw()
        c.Draw()
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1001111)
            StatBox = stack[1].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.7)
            StatBox.SetY2NDC(0.5)
            #StatBox.SetName("MC")
        if len(stack) > 2 and stack[2] != None:
            #ROOT.gStyle.SetOptStat(111111)
            StatBox = stack[2].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.5)
            StatBox.SetY2NDC(0.3)
            #StatBox.SetLabel("Data")
        if not os.path.isdir("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name)):
            os.makedirs("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name))
        c.SetLogy()
        c.SaveAs("./{channel}/{object_name}/{hname}_LOGY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        c.SetLogy(0)
        c.SaveAs("./{channel}/{object_name}/{hname}_LINY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        


# In[ ]:


for obj_name, obj_dict in stacks["ElMu_selection"].items():
    if obj_name != "Muons": continue
    print(obj_name)
    for sname, stack in obj_dict.items():
        c = ROOT.TCanvas("cs_{}_{}".format(obj_name, sname), "", 800, 600)
        c.cd()
        c.Update()
        #For data first
        #if len(stack) > 1:
        #    stack[1].Draw("PE1")
        #    stack[0].Draw("HIST SAME")
        #else:
        #    stack[0].Draw("HIST")
        #if len(stack) > 1:
        #    stack[1].Draw("PE1 SAME")
        #for MC first
        stack[0].Draw("HIST S")
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1111111)
            stack[1].Draw("SAMES")
        if len(stack) > 2 and stack[2] != None:
            ROOT.gStyle.SetOptStat(1111111)
            stack[2].Draw("PE1 SAMES")
        # Add header
        cms_label = ROOT.TLatex()
        cms_label.SetTextSize(0.04)
        cms_label.DrawLatexNDC(0.16, 0.92, "#bf{CMS Preliminary}")
        header = ROOT.TLatex()
        header.SetTextSize(0.03)
        header.DrawLatexNDC(0.63, 0.92, "#sqrt{{s}} = 13 TeV, L_{{int}} = {0} fb^{{-1}}".format(lumi[era]))
        leg.Draw()
        c.Draw()
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1001111)
            StatBox = stack[1].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.7)
            StatBox.SetY2NDC(0.5)
            #StatBox.SetName("MC")
        if len(stack) > 2 and stack[2] != None:
            #ROOT.gStyle.SetOptStat(111111)
            StatBox = stack[2].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.5)
            StatBox.SetY2NDC(0.3)
            #StatBox.SetLabel("Data")
        if not os.path.isdir("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name)):
            os.makedirs("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name))
        c.SetLogy()
        c.SaveAs("./{channel}/{object_name}/{hname}_LOGY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        c.SetLogy(0)
        c.SaveAs("./{channel}/{object_name}/{hname}_LINY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        


# In[ ]:


for obj_name, obj_dict in stacks["ElMu_selection"].items():
    if obj_name != "Electrons": continue
    print(obj_name)
    for sname, stack in obj_dict.items():
        c = ROOT.TCanvas("cs_{}_{}".format(obj_name, sname), "", 800, 600)
        c.cd()
        c.Update()
        #For data first
        #if len(stack) > 1:
        #    stack[1].Draw("PE1")
        #    stack[0].Draw("HIST SAME")
        #else:
        #    stack[0].Draw("HIST")
        #if len(stack) > 1:
        #    stack[1].Draw("PE1 SAME")
        #for MC first
        stack[0].Draw("HIST S")
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1111111)
            stack[1].Draw("SAMES")
        if len(stack) > 2 and stack[2] != None:
            ROOT.gStyle.SetOptStat(1111111)
            stack[2].Draw("PE1 SAMES")
        # Add header
        cms_label = ROOT.TLatex()
        cms_label.SetTextSize(0.04)
        cms_label.DrawLatexNDC(0.16, 0.92, "#bf{CMS Preliminary}")
        header = ROOT.TLatex()
        header.SetTextSize(0.03)
        header.DrawLatexNDC(0.63, 0.92, "#sqrt{{s}} = 13 TeV, L_{{int}} = {0} fb^{{-1}}".format(lumi[era]))
        leg.Draw()
        c.Draw()
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1001111)
            StatBox = stack[1].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.7)
            StatBox.SetY2NDC(0.5)
            #StatBox.SetName("MC")
        if len(stack) > 2 and stack[2] != None:
            #ROOT.gStyle.SetOptStat(111111)
            StatBox = stack[2].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.5)
            StatBox.SetY2NDC(0.3)
            #StatBox.SetLabel("Data")
        if not os.path.isdir("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name)):
            os.makedirs("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name))
        c.SetLogy()
        c.SaveAs("./{channel}/{object_name}/{hname}_LOGY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        c.SetLogy(0)
        c.SaveAs("./{channel}/{object_name}/{hname}_LINY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        


# In[ ]:


for obj_name, obj_dict in stacks["ElMu_selection"].items():
    if obj_name != "Leptons": continue
    print(obj_name)
    for sname, stack in obj_dict.items():
        c = ROOT.TCanvas("cs_{}_{}".format(obj_name, sname), "", 800, 600)
        c.cd()
        c.Update()
        #For data first
        #if len(stack) > 1:
        #    stack[1].Draw("PE1")
        #    stack[0].Draw("HIST SAME")
        #else:
        #    stack[0].Draw("HIST")
        #if len(stack) > 1:
        #    stack[1].Draw("PE1 SAME")
        #for MC first
        stack[0].Draw("HIST S")
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1111111)
            stack[1].Draw("SAMES")
        if len(stack) > 2 and stack[2] != None:
            ROOT.gStyle.SetOptStat(1111111)
            stack[2].Draw("PE1 SAMES")
        # Add header
        cms_label = ROOT.TLatex()
        cms_label.SetTextSize(0.04)
        cms_label.DrawLatexNDC(0.16, 0.92, "#bf{CMS Preliminary}")
        header = ROOT.TLatex()
        header.SetTextSize(0.03)
        header.DrawLatexNDC(0.63, 0.92, "#sqrt{{s}} = 13 TeV, L_{{int}} = {0} fb^{{-1}}".format(lumi[era]))
        leg.Draw()
        c.Draw()
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1001111)
            StatBox = stack[1].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.7)
            StatBox.SetY2NDC(0.5)
            #StatBox.SetName("MC")
        if len(stack) > 2 and stack[2] != None:
            #ROOT.gStyle.SetOptStat(111111)
            StatBox = stack[2].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.5)
            StatBox.SetY2NDC(0.3)
            #StatBox.SetLabel("Data")
        if not os.path.isdir("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name)):
            os.makedirs("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name))
        c.SetLogy()
        c.SaveAs("./{channel}/{object_name}/{hname}_LOGY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        c.SetLogy(0)
        c.SaveAs("./{channel}/{object_name}/{hname}_LINY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        


# In[ ]:


for obj_name, obj_dict in stacks["ElMu_selection"].items():
    if obj_name != "EventVars": continue
    print(obj_name)
    for sname, stack in obj_dict.items():
        c = ROOT.TCanvas("cs_{}_{}".format(obj_name, sname), "", 800, 600)
        c.cd()
        c.Update()
        #For data first
        #if len(stack) > 1:
        #    stack[1].Draw("PE1")
        #    stack[0].Draw("HIST SAME")
        #else:
        #    stack[0].Draw("HIST")
        #if len(stack) > 1:
        #    stack[1].Draw("PE1 SAME")
        #for MC first
        stack[0].Draw("HIST S")
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1111111)
            stack[1].Draw("SAMES")
        if len(stack) > 2 and stack[2] != None:
            ROOT.gStyle.SetOptStat(1111111)
            stack[2].Draw("PE1 SAMES")
        # Add header
        cms_label = ROOT.TLatex()
        cms_label.SetTextSize(0.04)
        cms_label.DrawLatexNDC(0.16, 0.92, "#bf{CMS Preliminary}")
        header = ROOT.TLatex()
        header.SetTextSize(0.03)
        header.DrawLatexNDC(0.63, 0.92, "#sqrt{{s}} = 13 TeV, L_{{int}} = {0} fb^{{-1}}".format(lumi[era]))
        leg.Draw()
        c.Draw()
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1001111)
            StatBox = stack[1].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.7)
            StatBox.SetY2NDC(0.5)
            #StatBox.SetName("MC")
        if len(stack) > 2 and stack[2] != None:
            #ROOT.gStyle.SetOptStat(111111)
            StatBox = stack[2].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.5)
            StatBox.SetY2NDC(0.3)
            #StatBox.SetLabel("Data")
        if not os.path.isdir("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name)):
            os.makedirs("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name))
        c.SetLogy()
        c.SaveAs("./{channel}/{object_name}/{hname}_LOGY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        c.SetLogy(0)
        c.SaveAs("./{channel}/{object_name}/{hname}_LINY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        


# In[ ]:


#%jsroot on
unblind_whitelist = set([])
CanvasCache = {}
CanvasCache["Open/Close"] = ROOT.TCanvas("open_close", "", 800, 100)

for obj_name, obj_dict in stacks["ElMu_selection"].items():
    if "Mountains" not in obj_name: continue
    print(obj_name)
    CanvasCache[obj_name] = {}
    #Save to a pdf using the '.pdf(' string to make a file that stays open for subsequent writes to the same filename. To be closed by '.pdf)' 
    CanvasCache["Open/Close"].SaveAs("./{channel}/{object_name}_All.pdf(".format(channel=fileChannel.replace("_selection", ""), object_name=obj_name.replace("Mountains_", "")))
    for sname, stack in sorted(obj_dict.items()):
        c = None
        if "_vs_" in sname: #hack to draw 2D histos in the 1D histo dict
            CanvasCache[obj_name][sname] = ROOT.TCanvas("cs_{}_{}".format(obj_name, sname), "", 800, 1800)
            CanvasCache[obj_name][sname].Divide(1,3)
            CanvasCache[obj_name][sname].cd(1)
        else:
        #if True:
            CanvasCache[obj_name][sname] = ROOT.TCanvas("cs_{}_{}".format(obj_name, sname), "", 800, 600)
            CanvasCache[obj_name][sname].cd()
        CanvasCache[obj_name][sname].SetLogy()
        CanvasCache[obj_name][sname].Update()
        #For data first
        #if len(stack) > 1:
        #    stack[1].Draw("PE1")
        #    stack[0].Draw("HIST SAME")
        #else:
        #    stack[0].Draw("HIST")
        #if len(stack) > 1:
        #    stack[1].Draw("PE1 SAME")
        #for MC first
        if "_vs_" in sname: #hack to draw 2D histos in the 1D histo dict
            stack[0].Draw("")
        else:
            stack[0].Draw("HIST S")
        #Draw the MC summed histogram for stats (better way with THStack? why the fuck don't people document this in a useful way?)
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1111111)
            if "_vs_" in sname: #hack to draw 2D histos in the 1D histo dict
                stack[1].Draw("SAMES") #Also SAME0, SAMES0 which 'do not use the z axis of the previous plot'
                CanvasCache[obj_name][sname].cd(2)
                tmp1 = stack[1].Clone()
                tmp1.SetLineColor(ROOT.kBlue)
                tmp1.SetFillColorAlpha(ROOT.kGreen, 0.7)
                tmp1.Draw("VIOLINX")
                #stack[1].ProfileX().Draw("E3")
                CanvasCache[obj_name][sname].cd(3)
                tmp1.Draw("VIOLINY")
                #stack[1].ProfileY().Draw("E3")
                CanvasCache[obj_name][sname].cd(1)
            else:
                stack[1].Draw("SAMES HIST")
        #Draw the data histogram, assuming that it's unblinded ("blind" not in the name and or in the whitelist )
        if len(stack) > 2 and stack[2] != None and ("blind" not in obj_name or obj_name in unblind_whitelist):
            ROOT.gStyle.SetOptStat(1111111)
            if "_vs_" in sname: #hack to draw 2D histos in the 1D histo dict
                stack[2].Draw("SAMES") #Maybe add ARR for arrow mode? or something else
                CanvasCache[obj_name][sname].cd(2)
                tmp2 = stack[2].Clone()
                tmp2.SetLineColor(ROOT.kRed)
                tmp2.SetFillColorAlpha(ROOT.kGray, 0.4)
                tmp2.Draw("SAMES CANDLEX")
                #stack[2].ProfileX().Draw("PE1 SAMES")
                CanvasCache[obj_name][sname].cd(3)
                tmp2.Draw("SAMES CANDLEY")
                #stack[2].ProfileY().Draw("PE1 SAMES")
                CanvasCache[obj_name][sname].cd(1)
            else:
                stack[2].Draw("PE1 SAMES")
        # Add header
        cms_label = ROOT.TLatex()
        cms_label.SetTextSize(0.04)
        cms_label.DrawLatexNDC(0.16, 0.92, "#bf{CMS Internal}")
        header = ROOT.TLatex()
        header.SetTextSize(0.03)
        header.DrawLatexNDC(0.63, 0.92, "#sqrt{{s}} = 13 TeV, L_{{int}} = {0} fb^{{-1}}".format(lumi[era]))
        leg.Draw()
        CanvasCache[obj_name][sname].Draw()
        if len(stack) > 1 and stack[1] != None:
            ROOT.gStyle.SetOptStat(1001111)
            StatBox = stack[1].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.7)
            StatBox.SetY2NDC(0.5)
            #StatBox.SetName("MC")
        if len(stack) > 2 and stack[2] != None and ("blind" not in obj_name or obj_name in unblind_whitelist):
            #ROOT.gStyle.SetOptStat(111111)
            StatBox = stack[2].GetListOfFunctions().FindObject("stats")
            StatBox.SetY1NDC(0.5)
            StatBox.SetY2NDC(0.3)
            #StatBox.SetLabel("Data")

        if not os.path.isdir("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name)):
            os.makedirs("./{channel}/{object_name}/".format(channel=fileChannel, object_name=obj_name))
        CanvasCache[obj_name][sname].SetLogy()
        CanvasCache[obj_name][sname].SaveAs("./{channel}/{object_name}/{hname}_LOGY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        CanvasCache[obj_name][sname].SaveAs("./{channel}/{object_name}_All.pdf".format(channel=fileChannel.replace("_selection", ""), object_name=obj_name.replace("Mountains_", ""), wgtVar=theWeight, hname=sname, filetype=theFormat))
        CanvasCache[obj_name][sname].SetLogy(0)
        CanvasCache[obj_name][sname].SaveAs("./{channel}/{object_name}/{hname}_LINY{filetype}".format(channel=fileChannel, object_name=obj_name, wgtVar=theWeight, hname=sname, filetype=theFormat))
        CanvasCache[obj_name][sname].SaveAs("./{channel}/{object_name}_All.pdf".format(channel=fileChannel.replace("_selection", ""), object_name=obj_name.replace("Mountains_", ""), wgtVar=theWeight, hname=sname, filetype=theFormat))
    #Close the pdf using '.pdf)' 
    CanvasCache["Open/Close"].SaveAs("./{channel}/{object_name}_All.pdf)".format(channel=fileChannel.replace("_selection", ""), object_name=obj_name.replace("Mountains_", "")))
    


# In[ ]:


masterfinish2 = time.time() #clock gives cpu time, not accurate multi-core?
print("Took {}m {}s to process in real-time including plots".format((masterfinish2 - masterstart)//60, (masterfinish - masterstart)%60))


# In[ ]:


#From example: https://root.cern.ch/doc/master/df103__NanoAODHiggsAnalysis_8py_source.html

#def plot(sig, bkg, data, x_label, filename):
#     """
#     Plot invariant mass for signal and background processes from simulated
#     events overlay the measured data.
#     """
#     # Canvas and general style options
#     ROOT.gStyle.SetOptStat(0)
#     ROOT.gStyle.SetTextFont(42)
#     d = ROOT.TCanvas("d", "", 800, 700)
#     d.SetLeftMargin(0.15)
# 
#     # Get signal and background histograms and stack them to show Higgs signal
#     # on top of the background process
#     h_bkg = bkg
#     h_cmb = sig.Clone()
# 
#     h_cmb.Add(h_bkg)
#     h_cmb.SetTitle("")
#     h_cmb.GetXaxis().SetTitle(x_label)
#     h_cmb.GetXaxis().SetTitleSize(0.04)
#     h_cmb.GetYaxis().SetTitle("N_{Events}")
#     h_cmb.GetYaxis().SetTitleSize(0.04)
#     h_cmb.SetLineColor(ROOT.kRed)
#     h_cmb.SetLineWidth(2)
#     h_cmb.SetMaximum(18)
#     h_bkg.SetLineWidth(2)
#     h_bkg.SetFillStyle(1001)
#     h_bkg.SetLineColor(ROOT.kBlack)
#     h_bkg.SetFillColor(ROOT.kAzure - 9)
# 
#     # Get histogram of data points
#     h_data = data
#     h_data.SetLineWidth(1)
#     h_data.SetMarkerStyle(20)
#     h_data.SetMarkerSize(1.0)
#     h_data.SetMarkerColor(ROOT.kBlack)
#     h_data.SetLineColor(ROOT.kBlack)
# 
#     # Draw histograms
#     h_cmb.DrawCopy("HIST")
#     h_bkg.DrawCopy("HIST SAME")
#     h_data.DrawCopy("PE1 SAME")
# 
#     # Add legend
#     legend = ROOT.TLegend(0.62, 0.70, 0.82, 0.88)
#     legend.SetFillColor(0)
#     legend.SetBorderSize(0)
#     legend.SetTextSize(0.03)
#     legend.AddEntry(h_data, "Data", "PE1")
#     legend.AddEntry(h_bkg, "ZZ", "f")
#     legend.AddEntry(h_cmb, "m_{H} = 125 GeV", "f")
#     legend.Draw()
# 
#     # Add header
#     cms_label = ROOT.TLatex()
#     cms_label.SetTextSize(0.04)
#     cms_label.DrawLatexNDC(0.16, 0.92, "#bf{CMS Open Data}")
#     header = ROOT.TLatex()
#     header.SetTextSize(0.03)
#     header.DrawLatexNDC(0.63, 0.92, "#sqrt{s} = 8 TeV, L_{int} = 11.6 fb^{-1}")
# 
#     # Save plot
#     d.SaveAs(filename)


# In[ ]:


#gg1 = ROOT.ROOT.RDF.SaveGraph(the_df['tttt']['ElMu_selection'], './mydot.dot')
#!dot -Tsvg mydot.dot -o mydot.svg
#listOfImageNames = ['./mydot.svg',
#                    ]
#
#for imageName in listOfImageNames:
#    display(SVG(filename=imageName))


# In[ ]:


#c = ROOT.TCanvas()


# In[ ]:





# In[ ]:


#stacks["ElMu_selection"]["Mountains_nMediumDeepJet0"]["Muon_pfRelIso03_chg_vs_MET"]
#stacksource_data["ElMu_selection"]["Mountains_nMediumDeepJet0"]["Muon_pfRelIso03_chg_vs_MET"]


# In[ ]:




