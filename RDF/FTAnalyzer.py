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
import ROOT
from ruamel.yaml import YAML
from FourTopNAOD.RDF.tools.toolbox import getFiles
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
    ROOT.ROOT.EnableImplicitMT()
    RS = ROOT.ROOT
    RDF = RS.RDataFrame

#Load functions, can eventually be changed to ROOT.gInterpreter.Declare(#include "someheader.h")
#WARNING! Do not rerun this cell without restarting the kernel, it will kill it!
ROOT.TH1.SetDefaultSumw2() #Make sure errors are done this way
ROOT.gROOT.ProcessLine(".L /eos/user/n/nmangane/CMSSW/CMSSW_10_2_18/src/FourTopNAOD/RDF/FTFunctions.cpp")
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


#FIXME: Need filter efficiency calculated for single lepton generator filtered sample. First approximation will be from MCCM (0.15) but as seen before, it's not ideal. 
#May need to recalculate using genWeight/sumWeights instead of sign(genWeight)/(nPositiveEvents - nNegativeEvents), confirm if there's any difference.
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
systematics_2017_NOMINAL = {"$NOMINAL": {"jet_mask": "jet_mask",
                                 "lep_postfix": "",
                                 "wgt_final": "wgt__nom",
                                 "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                 "jet_pt_var": "Jet_pt",
                                 "jet_mass_var": "Jet_mass",
                                 "met_pt_var": "METFixEE2017_pt",
                                 "met_phi_var": "METFixEE2017_phi",
                                 "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                            "DeepJet": "Jet_btagSF_deepjet_shape",
                                        },
                                 "weightVariation": False},
}
systematics_2017_ALL = {"$NOMINAL": {"jet_mask": "jet_mask",
                                 "lep_postfix": "",
                                 "wgt_final": "wgt__nom",
                                 "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                 "jet_pt_var": "Jet_pt",
                                 "jet_mass_var": "Jet_mass",
                                 "met_pt_var": "METFixEE2017_pt",
                                 "met_phi_var": "METFixEE2017_phi",
                                 "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                            "DeepJet": "Jet_btagSF_deepjet_shape",
                                        },
                                 "weightVariation": False},
                    "jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp",
                                   "lep_postfix": "",
                                   "wgt_final": "wgt__jesTotalUp",
                                   "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                   "jet_pt_var": "Jet_pt_jesTotalUp",
                                   "jet_mass_var": "Jet_mass_jesTotalUp",
                                   "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                   "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                   "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                              "DeepJet": "Jet_btagSF_deepjet_shape",
                                          },
                                    "weightVariation": False},
                    "jesTotalDown": {"jet_mask": "jet_mask_jesTotalDown",
                                      "lep_postfix": "",
                                      "wgt_final": "wgt__jesTotalDown", 
                                      "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                      "jet_pt_var": "Jet_pt_jesTotalDown",
                                      "jet_mass_var": "Jet_mass_jesTotalDown",
                                      "met_pt_var": "METFixEE2017_pt_jesTotalDown",
                                      "met_phi_var": "METFixEE2017_phi_jesTotalDown",
                                      "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                                 "DeepJet": "Jet_btagSF_deepjet_shape",
                                             },
                                      "weightVariation": False},
                    "btagSF_deepcsv_shape_up_hf": {"jet_mask": "jet_mask",
                                                    "lep_postfix": "", 
                                                    "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                    "jet_pt_var": "Jet_pt",
                                                    "btagSF":{"DeepCSV": "Jet_btagSF_deepcsv_shape_up_hf",
                                                              "DeepJet": "Jet_btagSF_deepjet_shape_up_hf",
                                                          },
                                                    "weightVariation": True},
                    "btagSF_deepcsv_shape_down_hf": {"jet_mask": "jet_mask",
                                                      "lep_postfix": "", 
                                                      "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                      "jet_pt_var": "Jet_pt",
                                                      "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape_down_hf",
                                                                 "DeepJet": "Jet_btagSF_deepjet_shape_down_hf",
                                                             },
                                                      "weightVariation": True},
                    "btagSF_deepcsv_shape_up_lf": {"jet_mask": "jet_mask",
                                                    "lep_postfix": "", 
                                                    "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                    "jet_pt_var": "Jet_pt",
                                                    "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape_up_lf",
                                                               "DeepJet": "Jet_btagSF_deepjet_shape_up_lf",
                                                           },
                                                    "weightVariation": True},
                    "btagSF_deepcsv_shape_down_lf": {"jet_mask": "jet_mask",
                                                      "lep_postfix": "", 
                                                      "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                      "jet_pt_var": "Jet_pt",
                                                      "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape_down_lf",
                                                                 "DeepJet": "Jet_btagSF_deepjet_shape_down_lf",
                                                             },
                                                      "weightVariation": True},
                    "no_btag_shape_reweight": {"jet_mask": "jet_mask",
                                                "lep_postfix": "", 
                                                "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                "jet_pt_var": "Jet_pt",
                                                "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                                           "DeepJet": "Jet_btagSF_deepjet_shape",
                                                       },
                                                "weightVariation": True},
                    "no_puWeight": {"jet_mask": "jet_mask",
                                     "lep_postfix": "", 
                                     "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                     "jet_pt_var": "Jet_pt",
                                     "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                                "DeepJet": "Jet_btagSF_deepjet_shape",
                                            },
                                     "weightVariation": True},
                    "no_L1PreFiringWeight": {"jet_mask": "jet_mask",
                                              "lep_postfix": "", 
                                              "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                              "jet_pt_var": "Jet_pt",
                                              "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                                         "DeepJet": "Jet_btagSF_deepjet_shape",
                                                     },
                                              "weightVariation": True},
                    "no_LSF": {"jet_mask": "jet_mask",
                                "lep_postfix": "", 
                                "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                "jet_pt_var": "Jet_pt",
                                "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                           "DeepJet": "Jet_btagSF_deepjet_shape",
                                       },
                                "weightVariation": True},
}
print("Only using the nominal variations right now, see L142")
systematics_2017 = systematics_2017_NOMINAL
# systematics_2017 = systematics_2017_ALL

TriggerTuple = collections.namedtuple("TriggerTuple", "trigger era subera uniqueEraBit tier lumi channel leadMuThresh subMuThresh leadElThresh subElThresh nontriggerLepThresh")
TriggerList = [TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=14,
                            tier=0,
                            lumi=0,
                            channel="ElMu",
                            leadMuThresh=25,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=15,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=13,
                            tier=0,
                            lumi=0,
                            channel="ElMu",
                            leadMuThresh=99999,
                            subMuThresh=15,
                            leadElThresh=25,
                            subElThresh=99999,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                            era="2017",
                            subera="B",
                            uniqueEraBit=12,
                            tier=1,
                            lumi=0,
                            channel="MuMu",
                            leadMuThresh=25,
                            subMuThresh=15,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
                            era="2017",
                            subera="CDEF",
                            uniqueEraBit=11,
                            tier=1,
                            lumi=0,
                            channel="MuMu",
                            leadMuThresh=25,
                            subMuThresh=15,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=9,
                            tier=2,
                            lumi=0,
                            channel="ElEl",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=25,
                            subElThresh=15,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_IsoMu27",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=7,
                            tier=3,
                            lumi=0,
                            channel="Mu",
                            leadMuThresh=28,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_Ele35_WPTight_Gsf",
                            era="2017",
                            subera="BCDEF",
                            uniqueEraBit=6,
                            tier=4,
                            lumi=0,
                            channel="El",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=36,
                            subElThresh=99999,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=14,
                            tier=0,
                            lumi=0,
                            channel="ElMu",
                            leadMuThresh=99999,
                            subMuThresh=15,
                            leadElThresh=25,
                            subElThresh=99999,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=12,
                            tier=0,
                            lumi=0,
                            channel="ElMu",
                            leadMuThresh=25,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=15,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=11,
                            tier=1,
                            lumi=0,
                            channel="MuMu",
                            leadMuThresh=25,
                            subMuThresh=15,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=9,
                            tier=2,
                            lumi=0,
                            channel="ElEl",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=25,
                            subElThresh=15,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_IsoMu24",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=8,
                            tier=3,
                            lumi=0,
                            channel="Mu",
                            leadMuThresh=25,
                            subMuThresh=99999,
                            leadElThresh=99999,
                            subElThresh=99999,
                            nontriggerLepThresh=15),
               TriggerTuple(trigger="HLT_Ele32_WPTight_Gsf",
                            era="2018",
                            subera="ABCD",
                            uniqueEraBit=7,
                            tier=4,
                            lumi=0,
                            channel="El",
                            leadMuThresh=99999,
                            subMuThresh=99999,
                            leadElThresh=33,
                            subElThresh=99999,
                            nontriggerLepThresh=15)]
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
        "source": {"NANOv5": "dbs:/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttt-*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tttt-*_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tttt-*_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tttt-*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttt-1_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/tttt-2_2017_v2.root"],
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
        "crossSection": 87.3348, 
        "color": leg_dict["ttbar"],
        "source": {"NANOv5": "dbs:/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "NANOv5p1": "dbs:/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/palencia-TopNanoAODv5p1_2017-caa716c30b9109c88acae23be6386548/USER",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_DL-NOM-*_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_DL-NOM-*_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_DL-NOM-*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-1_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-2_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-3_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-4_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-5_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-6_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-7_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-8_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-9_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-10_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-11_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-12_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-13_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-14_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_DL/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Nominal",
                   "channel": "DL"
                  },
        "Notes": "crossSection folds in the branching ratio to DL. when splitting the process, need to know both the effective crossSection in each "\
        "phase space and the effective number of events to combine multiple samples in that phase space proportional to the effective number of"\
        "simulated events (N_eff = N_positive - N_negative) over the nEffectivePhaseSpace (sum of N_eff from all contributing samples)"\
        "The old XS form 2018 PDG BRs was 89.0482, swapped to Brown's value... Need to update SL technically as well",
        "splitProcess": {"ID":{"unpackGenTtbarId": True,
                               "nFTAGenJet/FTAGenHT": True,
                               "subera": False,
                              },
                         "processes": {"ttbb_DL_fr": {"filter": "nAdditionalBJets >= 2 && nFTAGenLep == 2 && nFTAGenJet >= 7 && FTAGenHT >= 500",
                                                      "sumWeights": 2776096.39581,
                                                      "sumWeights2": 203548428.082,
                                                      "nominalXS": 0.0486771857914,
                                                      "nominalXS2": 6.25820222319e-08,
                                                      "effectiveXS": 0.00728478735001,
                                                      "effectiveXS2": 1.40162690665e-09,
                                                      "nEventsPositive": 38381,
                                                      "nEventsNegative": 174,
                                                      "nLep2nJet7GenHT500-550-nominalXS": 0.00453612161001,
                                                      "nLep2nJet7pGenHT500p-nominalXS": 0.0486771857914,
                                                      "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                      "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                      "nLep2nJet7GenHT500-550-effectiveXS": 0.000678853569398,
                                                      "nLep2nJet7pGenHT500p-effectiveXS": 0.00728478735001,
                                                      "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                      "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                      "fractionalContribution": 0.11972537248,
                                                      "effectiveCrossSection": 0.0486771857914 * 0.040/0.032,
                                                  },
                                       "ttbb_DL_nr": {"filter": "nAdditionalBJets >= 2 && nFTAGenLep == 2 && (nFTAGenJet < 7 || FTAGenHT < 500)",
                                                      "sumWeights": 15117576.3357,
                                                      "sumWeights2": 1108001380.45,
                                                      "nominalXS": 0.265077636755,
                                                      "nominalXS2": 3.40660783667e-07,
                                                      "effectiveXS": 0.331347,
                                                      "effectiveXS2": 5.32282326868e-07,
                                                      "nEventsPositive": 208932,
                                                      "nEventsNegative": 894,
                                                      "nLep2nJet7GenHT500-550-nominalXS": 0.0,
                                                      "nLep2nJet7pGenHT500p-nominalXS": 0.0,
                                                      "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                      "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                      "nLep2nJet7GenHT500-550-effectiveXS": 0.0,
                                                      "nLep2nJet7pGenHT500p-effectiveXS": 0.0,
                                                      "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                      "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                      "fractionalContribution": 1,
                                                      "effectiveCrossSection": 0.265077636755 * 0.040/0.032,
                                                  },
                                       "ttother_DL_fr": {"filter": "nAdditionalBJets < 2 && nFTAGenLep == 2 && nFTAGenJet >= 7 && FTAGenHT >= 500",
                                                         "sumWeights": 80302570.8316,
                                                         "sumWeights2": 5895277293.01,
                                                         "nominalXS": 1.40805743121,
                                                         "nominalXS2": 1.81253364662e-06,
                                                         "effectiveXS": 0.166807220112,
                                                         "effectiveXS2": 2.54375352784e-08,
                                                         "nEventsPositive": 1111004,
                                                         "nEventsNegative": 5757,
                                                         "nLep2nJet7GenHT500-550-nominalXS": 0.176787980442,
                                                         "nLep2nJet7pGenHT500p-nominalXS": 1.40805743121,
                                                         "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                         "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                         "nLep2nJet7GenHT500-550-effectiveXS": 0.0209434011092,
                                                         "nLep2nJet7pGenHT500p-effectiveXS": 0.166807220112,
                                                         "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                         "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                         "fractionalContribution": 0.11949870629,
                                                         "effectiveCrossSection": 1.40805743121 - 0.0486771857914 * (0.040 - 0.032)/0.032,
                                                  },
                                       "ttother_DL_nr": {"filter": "nAdditionalBJets < 2 && nFTAGenLep == 2 && (nFTAGenJet < 7 || FTAGenHT < 500)",
                                                         "sumWeights": 4882573073.47,
                                                         "sumWeights2": 3.57706696495e+11,
                                                         "nominalXS": 85.6129913169,
                                                         "nominalXS2": 0.000109978783148,
                                                         "effectiveXS": 85.5467219936,
                                                         "effectiveXS2": 0.000109808589394,
                                                         "nEventsPositive": 67460463,
                                                         "nEventsNegative": 273039,
                                                         "nLep2nJet7GenHT500-550-nominalXS": 0.0,
                                                         "nLep2nJet7pGenHT500p-nominalXS": 0.0,
                                                         "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                         "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                         "nLep2nJet7GenHT500-550-effectiveXS": 0.0,
                                                         "nLep2nJet7pGenHT500p-effectiveXS": 0.0,
                                                         "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                         "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                         "fractionalContribution": 1,
                                                         "effectiveCrossSection": 85.6129913168 - 0.265077636755 * (0.040 - 0.032)/0.032,
                                                     },
                                   },
                         "inclusiveProcess": {"tt_DL_inclusive": {"filter": "return true;",
                                                           "sumWeights": 4980769317.03,
                                                           "sumWeights2": 3.64913523596e+11,
                                                           "nominalXS": 87.3348035714,
                                                           "nominalXS2": 0.000112194559601,
                                                           "effectiveXS": 87.3348035714,
                                                           "effectiveXS2": 0.000112194559601,
                                                           "nEventsPositive": 68818780,
                                                           "nEventsNegative": 279864,
                                                           "nLep2nJet7GenHT500-550-nominalXS": 0.181324102052,
                                                           "nLep2nJet7pGenHT500p-nominalXS": 1.456734617,
                                                           "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                           "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                           "nLep2nJet7GenHT500-550-effectiveXS": 0.181324102052,
                                                           "nLep2nJet7pGenHT500p-effectiveXS": 1.456734617,
                                                           "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                           "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                           "fractionalContribution": 1,
                                                           "effectiveCrossSection": 87.3348, 
                                                        },

                                          },
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
        "crossSection": 0.0486771857914 + 1.40805743121,
        "crossSectionGenHT500-550nJet7Matching": 1.4529,
        "color": leg_dict["ttbar"],
        "source": {"NANOv5": "dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "NANOv5p1": "dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/palencia-TopNanoAODv5p1_2017-caa716c30b9109c88acae23be6386548/USER",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_DL-GF-*_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_DL-GF-*_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_DL-GF-*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-1_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-2_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-3_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-4_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_DL-GF/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Filtered",
                   "channel": "DL"
                  },
        "Notes": "1.4815 was the old XS * BR * stitching factor, now scaled down so that the XS matches Brown's lower BR calculation",
        "splitProcess": {"ID":{"unpackGenTtbarId": True,
                               "nFTAGenJet/FTAGenHT": True,
                               "subera": False,
                              },
                         "processes": {"ttbb_DL-GF_fr": {"filter": "nAdditionalBJets >= 2 && nFTAGenLep == 2 && nFTAGenJet >= 7 && FTAGenHT >= 500",
                                                         "sumWeights": 20410377.7205,
                                                         "sumWeights2": 1495802529.19,
                                                         "nominalXS": 0.0485744525276,
                                                         "nominalXS2": 8.47204020682e-09,
                                                         "effectiveXS": 0.0535612126499,
                                                         "effectiveXS2": 1.03008480636e-08,
                                                         "nEventsPositive": 282130,
                                                         "nEventsNegative": 1215,
                                                         "nLep2nJet7GenHT500-550-nominalXS": 0.00446767251882,
                                                         "nLep2nJet7pGenHT500p-nominalXS": 0.0485744525276,
                                                         "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                         "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                         "nLep2nJet7GenHT500-550-effectiveXS": 0.00492633360499,
                                                         "nLep2nJet7pGenHT500p-effectiveXS": 0.0535612126499,
                                                         "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                         "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                         "fractionalContribution": 1 - 0.11972537248,
                                                         "effectiveCrossSection": 0.0486771857914 * 0.040/0.032,
                                                     },
                                       "ttother_DL-GF_fr": {"filter": "nAdditionalBJets < 2 && nFTAGenLep == 2 && nFTAGenJet >= 7 && FTAGenHT >= 500",
                                                            "sumWeights": 591691409.848,
                                                            "sumWeights2": 43429698960.3,
                                                            "nominalXS": 1.40816043153,
                                                            "nominalXS2": 2.45980434304e-07,
                                                            "effectiveXS": 1.2290807799,
                                                            "effectiveXS2": 1.87394631545e-07,
                                                            "nEventsPositive": 8185412,
                                                            "nEventsNegative": 41630,
                                                            "nLep2nJet7GenHT500-550-nominalXS": 0.17731136686,
                                                            "nLep2nJet7pGenHT500p-nominalXS": 1.40816043153,
                                                            "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                            "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                            "nLep2nJet7GenHT500-550-effectiveXS": 0.154762190574,
                                                            "nLep2nJet7pGenHT500p-effectiveXS": 1.2290807799,
                                                            "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                            "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                            "fractionalContribution": 1 - 0.11949870629,
                                                            "effectiveCrossSection": 1.40805743121 - 0.0486771857914 * (0.040 - 0.032)/0.032,
                                                        },
                                   },
                         "inclusiveProcess": {"tt_DL-GF_inclusive": {"sumWeights": 612101860.267,
                                                                     "sumWeights2": 44925506774.5,
                                                                     "nominalXS": 1.45673505707,
                                                                     "nominalXS2": 2.54452504445e-07,
                                                                     "effectiveXS": 1.45673505707,
                                                                     "effectiveXS2": 2.54452504445e-07,
                                                                     "nEventsPositive": 8467543,
                                                                     "nEventsNegative": 42845,
                                                                     "nLep2nJet7GenHT500-550-nominalXS": 0.181779039379,
                                                                     "nLep2nJet7pGenHT500p-nominalXS": 1.45673488406,
                                                                     "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                                     "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                                     "nLep2nJet7GenHT500-550-effectiveXS": 0.181779039379,
                                                                     "nLep2nJet7pGenHT500p-effectiveXS": 1.45673488406,
                                                                     "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                                     "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                                     },
                                          },
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
        "crossSection": 364.3109,
        "color": leg_dict["ttbar"],
        "source": {"NANOv5": "dbs:/TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "NANOv5p1": "dbs:/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/palencia-TopNanoAODv5p1_2017-caa716c30b9109c88acae23be6386548/USER",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_SL-NOM_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_SL-NOM_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_SL-NOM_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_SL/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Nominal",
                   "channel": "SL"
                  },
        "splitProcess": {"ID":{"unpackGenTtbarId": True,
                               "nFTAGenJet/FTAGenHT": True,
                               "subera": False,
                              },
                         "processes": {"ttbb_SL_fr": {"filter": "nAdditionalBJets >= 2 && nFTAGenLep == 1 && nFTAGenJet >= 9 && FTAGenHT >= 500",
                                                      "sumWeights": 1656838.94388,
                                                      "sumWeights2": 506713855.51,
                                                      "nominalXS": 0.0997284505393,
                                                      "nominalXS2": 1.83586327709e-06,
                                                      "effectiveXS": 0.00164567288,
                                                      "effectiveXS2": 4.99906997665e-10,
                                                      "nEventsPositive": 5490,
                                                      "nEventsNegative": 24,
                                                      "nLep2nJet7GenHT500-550-nominalXS": 0.0,
                                                      "nLep2nJet7pGenHT500p-nominalXS": 0.0,
                                                      "nLep1nJet9GenHT500-550-nominalXS": 0.00622291611373,
                                                      "nLep1nJet9pGenHT500p-nominalXS": 0.0997284505393,
                                                      "nLep2nJet7GenHT500-550-effectiveXS": 0.0,
                                                      "nLep2nJet7pGenHT500p-effectiveXS": 0.0,
                                                      "nLep1nJet9GenHT500-550-effectiveXS": 0.000102687690699,
                                                      "nLep1nJet9pGenHT500p-effectiveXS": 0.00164567288,
                                                      "fractionalContribution": 0.01384021714,
                                                      "effectiveCrossSection": 0.0997284505393 * 0.062/0.052, 
                                                  },
                                       "ttbb_SL_nr": {"filter": "nAdditionalBJets >= 2 && nFTAGenLep == 1 && (nFTAGenJet < 9 || FTAGenHT < 500)",
                                                      "sumWeights": 22135434.4955,
                                                      "sumWeights2": 6767694727.14,
                                                      "nominalXS": 1.33237608423,
                                                      "nominalXS2": 2.45198785962e-05,
                                                      "effectiveXS": 1.588602,
                                                      "effectiveXS2": 3.48573902185e-05,
                                                      "nEventsPositive": 73301,
                                                      "nEventsNegative": 302,
                                                      "nLep2nJet7GenHT500-550-nominalXS": 0.0,
                                                      "nLep2nJet7pGenHT500p-nominalXS": 0.0,
                                                      "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                      "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                      "nLep2nJet7GenHT500-550-effectiveXS": 0.0,
                                                      "nLep2nJet7pGenHT500p-effectiveXS": 0.0,
                                                      "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                      "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                      "fractionalContribution": 1,
                                                      "effectiveCrossSection": 1.33237608423 * 0.062/0.052,
                                                  },
                                       "ttother_SL_fr": {"filter": "nAdditionalBJets < 2 && nFTAGenLep == 1 && nFTAGenJet >= 9 && FTAGenHT >= 500",
                                                         "sumWeights": 36038396.785,
                                                         "sumWeights2": 11028806959.9,
                                                         "nominalXS": 2.16922319732,
                                                         "nominalXS2": 3.99582159982e-05,
                                                         "effectiveXS": 0.030132880675,
                                                         "effectiveXS2": 7.71043559122e-09,
                                                         "nEventsPositive": 119432,
                                                         "nEventsNegative": 560,
                                                         "nLep2nJet7GenHT500-550-nominalXS": 0.0,
                                                         "nLep2nJet7pGenHT500p-nominalXS": 0.0,
                                                         "nLep1nJet9GenHT500-550-nominalXS": 0.187760421205,
                                                         "nLep1nJet9pGenHT500p-nominalXS": 2.16922319732,
                                                         "nLep2nJet7GenHT500-550-effectiveXS": 0.0,
                                                         "nLep2nJet7pGenHT500p-effectiveXS": 0.0,
                                                         "nLep1nJet9GenHT500-550-effectiveXS": 0.00260819742969,
                                                         "nLep1nJet9pGenHT500p-effectiveXS": 0.030132880675,
                                                         "fractionalContribution": 0.01401549826,
                                                         "effectiveCrossSection": 2.16922319732 - 0.0997284505393 * (0.062 - 0.052)/0.052,
                                                  },
                                       "ttother_SL_nr": {"filter": "nAdditionalBJets < 2 && nFTAGenLep == 1 && (nFTAGenJet < 9 || FTAGenHT < 500)",
                                                         "sumWeights": 5992649717.25,
                                                         "sumWeights2": 1.83204705804e+12,
                                                         "nominalXS": 360.709574761,
                                                         "nominalXS2": 0.00663764742005,
                                                         "effectiveXS": 360.453348999,
                                                         "effectiveXS2": 0.0066282208208,
                                                         "nEventsPositive": 19842384,
                                                         "nEventsNegative": 80517,
                                                         "nLep2nJet7GenHT500-550-nominalXS": 0.0,
                                                         "nLep2nJet7pGenHT500p-nominalXS": 0.0,
                                                         "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                         "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                         "nLep2nJet7GenHT500-550-effectiveXS": 0.0,
                                                         "nLep2nJet7pGenHT500p-effectiveXS": 0.0,
                                                         "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                         "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                         "fractionalContribution": 1,
                                                         "effectiveCrossSection": 360.709574761 - 1.33237608423 * (0.062 - 0.052)/0.052,
                                                  },
                                   },
                         "inclusiveProcess": {"tt_SL_inclusive": {"filter": "return true;",
                                                                  "sumWeights": 6052480387.47,
                                                                  "sumWeights2": 1.85035027359e+12,
                                                                  "nominalXS": 364.310902493,
                                                                  "nominalXS2": 0.00670396137791,
                                                                  "effectiveXS": 364.310902493,
                                                                  "effectiveXS2": 0.00670396137791,
                                                                  "nEventsPositive": 20040607,
                                                                  "nEventsNegative": 81403,
                                                                  "nLep2nJet7GenHT500-550-nominalXS": 0.0,
                                                                  "nLep2nJet7pGenHT500p-nominalXS": 0.0,
                                                                  "nLep1nJet9GenHT500-550-nominalXS": 0.193983337319,
                                                                  "nLep1nJet9pGenHT500p-nominalXS": 2.26895164785,
                                                                  "nLep2nJet7GenHT500-550-effectiveXS": 0.0,
                                                                  "nLep2nJet7pGenHT500p-effectiveXS": 0.0,
                                                                  "nLep1nJet9GenHT500-550-effectiveXS": 0.193983337319,
                                                                  "nLep1nJet9pGenHT500p-effectiveXS": 2.26895164785,
                                                                  "effectiveCrossSection": 364.3109,
                                                                  "fractionalContribution": 1,
                                                              },
                                              
                                          },
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
        "crossSection": 0.0997284505393 + 2.16922319732,
        "color": leg_dict["ttbar"],
        "source": {"NANOv5": "dbs:/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "NANOv5p1": "dbs:/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/palencia-TopNanoAODv5p1_2017-caa716c30b9109c88acae23be6386548/USER",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-GF_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_SL-GF_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_SL-GF_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_SL-GF_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-GF_2017_v2.root"],
        "destination": "/$HIST_CLASS/$HIST/tt_SL-GF/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Filtered",
                   "channel": "SL"
                  },
        "splitProcess": {"ID":{"unpackGenTtbarId": True,
                               "nFTAGenJet/FTAGenHT": True,
                               "subera": False,
                              },
                         "processes": {"ttbb_SL-GF_fr": {"filter": "nAdditionalBJets >= 2 && nFTAGenLep == 1 && nFTAGenJet >= 9 && FTAGenHT >= 500",
                                                         "sumWeights": 118077149.406,
                                                         "sumWeights2": 36125534258.9,
                                                         "nominalXS": 0.100971811238,
                                                         "nominalXS2": 2.64169608221e-08,
                                                         "effectiveXS": 0.11726132712,
                                                         "effectiveXS2": 3.56280594874e-08,
                                                         "nEventsPositive": 391250,
                                                         "nEventsNegative": 1780,
                                                         "nLep2nJet7GenHT500-550-nominalXS": 0.0,
                                                         "nLep2nJet7pGenHT500p-nominalXS": 0.0,
                                                         "nLep1nJet9GenHT500-550-nominalXS": 0.00636695757789,
                                                         "nLep1nJet9pGenHT500p-nominalXS": 0.100971811238,
                                                         "nLep2nJet7GenHT500-550-effectiveXS": 0.0,
                                                         "nLep2nJet7pGenHT500p-effectiveXS": 0.0,
                                                         "nLep1nJet9GenHT500-550-effectiveXS": 0.00739412204407,
                                                         "nLep1nJet9pGenHT500p-effectiveXS": 0.11726132712,
                                                         "fractionalContribution": 1-0.01384021714,
                                                         "effectiveCrossSection": 0.0997284505393 * 0.062/0.052,
                                                     },
                                       "ttother_SL-GF_fr": {"filter": "nAdditionalBJets < 2 && nFTAGenLep == 1 && nFTAGenJet >= 9 && FTAGenHT >= 500",
                                                            "sumWeights": 2535249552.17,
                                                            "sumWeights2": 7.76075813737e+11,
                                                            "nominalXS": 2.1679786522,
                                                            "nominalXS2": 5.67508959725e-07,
                                                            "effectiveXS": 2.11991211931,
                                                            "effectiveXS2": 5.42623295899e-07,
                                                            "nEventsPositive": 8403208,
                                                            "nEventsNegative": 40612,
                                                            "nLep2nJet7GenHT500-550-nominalXS": 0.0,
                                                            "nLep2nJet7pGenHT500p-nominalXS": 0.0,
                                                            "nLep1nJet9GenHT500-550-nominalXS": 0.185403834447,
                                                            "nLep1nJet9pGenHT500p-nominalXS": 2.1679786522,
                                                            "nLep2nJet7GenHT500-550-effectiveXS": 0.0,
                                                            "nLep2nJet7pGenHT500p-effectiveXS": 0.0,
                                                            "nLep1nJet9GenHT500-550-effectiveXS": 0.181293222246,
                                                            "nLep1nJet9pGenHT500p-effectiveXS": 2.11991211931,
                                                            "fractionalContribution": 1 - 0.01401549826,
                                                            "effectiveCrossSection": 2.16922319732 - 0.0997284505393 * (0.062 - 0.052)/0.052,
                                                        },
                                   },
                         "inclusiveProcess": {"tt_SL-GF_inclusive": {"sumWeights": 2653328518.69,
                                                                  "sumWeights2": 8.12201898319e+11,
                                                                  "nominalXS": 2.26895201732,
                                                                  "nominalXS2": 5.93926322975e-07,
                                                                  "effectiveXS": 2.26895201732,
                                                                  "effectiveXS2": 5.93926322975e-07,
                                                                  "nEventsPositive": 8794464,
                                                                  "nEventsNegative": 42392,
                                                                  "nLep2nJet7GenHT500-550-nominalXS": 0.0,
                                                                  "nLep2nJet7pGenHT500p-nominalXS": 0.0,
                                                                  "nLep1nJet9GenHT500-550-nominalXS": 0.191770792025,
                                                                  "nLep1nJet9pGenHT500p-nominalXS": 2.26895046344,
                                                                  "nLep2nJet7GenHT500-550-effectiveXS": 0.0,
                                                                  "nLep2nJet7pGenHT500p-effectiveXS": 0.0,
                                                                  "nLep1nJet9GenHT500-550-effectiveXS": 0.191770792025,
                                                                  "nLep1nJet9pGenHT500p-effectiveXS": 2.26895046344,
                                                                  "fractionalContribution": 1,
                                                                  "effectiveCrossSection": 0.0997284505393 + 2.16922319732,
                                                              },
                                          },
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
        "crossSection": 35.83,
        "color": leg_dict["singletop"],
        "source": {"NANOv5": "dbs:/ST_tW_top_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "NANOv5p1": "dbs:/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/palencia-TopNanoAODv5p1_2017-caa716c30b9109c88acae23be6386548/USER",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tW_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ST_tW_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ST_tW_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ST_tW_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tW_2017_v2.root"],
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
        "crossSection": 35.83,
        "color": leg_dict["singletop"],
        "source": {"NANOv5": "dbs:/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "NANOv5p1": "dbs:/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/palencia-TopNanoAODv5p1_2017-caa716c30b9109c88acae23be6386548/USER",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tbarW_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ST_tbarW_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ST_tbarW_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ST_tbarW_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ST_tbarW_2017_v2.root"],
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
        "crossSection": 6077.22,
        "color": leg_dict["DY"],
        "source": {"NANOv5": "dbs:/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017RECOSIMstep_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7_ext1-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/DYJets_DL-*_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/DYJets_DL-*_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/DYJets_DL-*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-1_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-2_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-3_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-4_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-5_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-6_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/DYJets_DL-7_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttH_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttH_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttH_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttH_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttH_2017_v2.root",],
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
        "crossSection": 0.6105,
        "color": leg_dict["ttVJets"],
        "source": {"NANOv5": "dbs:/ttWJets_TuneCP5_13TeV_madgraphMLM_pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7_ext1-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWJets_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttWJets_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttWJets_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttWJets_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWJets_2017_v2.root",],
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
        "crossSection": 0.7826,
        "color": leg_dict["ttVJets"],
        "source": {"NANOv5": "dbs:/ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7_ext1-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZJets_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttZJets_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttZJets_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttZJets_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZJets_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/TTWH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWH_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttWH_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttWH_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttWH_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWH_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/TTWW_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWW_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttWW_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttWW_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttWW_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWW_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/TTWZ_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWZ_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttWZ_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttWZ_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttWZ_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttWZ_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/TTZZ_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZZ_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttZZ_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttZZ_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttZZ_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZZ_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/TTZH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZH_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttZH_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttZH_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttZH_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttZH_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/TTHH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttHH_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/ttHH_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/ttHH_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/ttHH_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ttHH_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/TTTW_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttW_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tttW_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tttW_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tttW_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttW_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/TTTJ_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttJ_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tttJ_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tttJ_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tttJ_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tttJ_2017_v2.root",],
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
        "source": {"LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/data_ElMu_*_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/data_ElMu_*_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/data_ElMu_*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_B_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_C_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_D_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_E_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_F_2017_v2.root",],
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
        "source": {"LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/data_MuMu_*_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/data_MuMu_*_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/data_MuMu_*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_B_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_C_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_D_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_E_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_F_2017_v2.root",],
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
        "source": {"LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/data_ElEl_*_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/data_ElEl_*_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/data_ElEl_*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_B_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_C_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_D_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_E_2017_v2.root",
                        "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_F_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/ElEl/NOMINAL",
        },
}
bookerV2_Mu = {
    "Mu":{
        "era": "2017",
        "subera": "BCDEF",
        "channel": "Mu",
        "isData": True,
        "nEvents": 136300266 + 165652756 + 70361660 + 154630534 + 242135500,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/data_Mu_*_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/data_Mu_*_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/data_Mu_*_2017_v2*.root",
                  },
        },
}
bookerV2_El = {
    "El":{
        "era": "2017",
        "subera": "BCDEF",
        "channel": "El",
        "isData": True,
        "nEvents": 60537490 + 136637888 + 51526710 + 102121689 + 128467223,
        "color": leg_dict["Data"],
        "source": {"LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/data_El_*_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/data_El_*_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/data_El_*_2017_v2*.root",
                  },
        },
}
bookerV2_SplitData = {
    "ElMu_B":{
        "era": "2017",
        "subera": "B",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 4453465,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/MuonEG/Run2017B-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_B*_2017_v2.root",},
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_B_2017.root",],
        },
    "ElMu_C":{
        "era": "2017",
        "subera": "C",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 15595214, 
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/MuonEG/Run2017C-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_C*_2017_v2.root",},
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_C_2017.root",],
        },
    "ElMu_D":{
        "era": "2017",
        "subera": "D",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 9164365,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/MuonEG/Run2017D-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_D*_2017_v2.root",},
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_D_2017.root",],
        },
    "ElMu_E":{
        "era": "2017",
        "subera": "E",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 19043421,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/MuonEG/Run2017E-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_E*_2017_v2.root",},
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_E_2017.root",],
        },
    "ElMu_F":{
        "era": "2017",
        "subera": "F",
        "channel": "ElMu",
        "isData": True,
        "nEvents": 25776363,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/MuonEG/Run2017F-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElMu_F*_2017_v2.root",},
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_F_2017.root",],
        },
    "MuMu_B":{
        "era": "2017",
        "subera": "B",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 14501767,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/DoubleMuon/Run2017B-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_B*_2017_v2.root",},
        },
    "MuMu_C":{
        "era": "2017",
        "subera": "C",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 49636525,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/DoubleMuon/Run2017C-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_C*_2017_v2.root",},
        },
    "MuMu_D":{
        "era": "2017",
        "subera": "D",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 23075733,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/DoubleMuon/Run2017D-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_D*_2017_v2.root",},
        },
    "MuMu_E":{
        "era": "2017",
        "subera": "E",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 51589091,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/DoubleMuon/Run2017E-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_E*_2017_v2.root",},
        },
    "MuMu_F":{
        "era": "2017",
        "subera": "F",
        "channel": "MuMu",
        "isData": True,
        "nEvents": 79756560,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/DoubleMuon/Run2017F-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_MuMu_F*_2017_v2.root",},
        },
    "ElEl_B":{
        "era": "2017",
        "subera": "B",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 58088760,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/DoubleEG/Run2017B-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_B*_2017_v2.root",},
        },
    "ElEl_C":{
        "era": "2017",
        "subera": "C",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 65181125,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/DoubleEG/Run2017C-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_C*_2017_v2.root",},
        },
    "ElEl_D":{
        "era": "2017",
        "subera": "D",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 25911432,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/DoubleEG/Run2017D-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_D*_2017_v2.root",},
        },
    "ElEl_E":{
        "era": "2017",
        "subera": "E",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 56233597,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/DoubleEG/Run2017E-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_E*_2017_v2.root",},
        },
    "ElEl_F":{
        "era": "2017",
        "subera": "F",
        "channel": "ElEl",
        "isData": True,
        "nEvents": 74307066,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/DoubleEG/Run2017F-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_ElEl_F*_2017_v2.root",},
        },
    "Mu_B":{
        "era": "2017",
        "subera": "B",
        "channel": "Mu",
        "isData": True,
        "nEvents": 136300266,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/SingleMuon/Run2017B-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_B*_2017_v2.root",},
        },
    "Mu_C":{
        "era": "2017",
        "subera": "C",
        "channel": "Mu",
        "isData": True,
        "nEvents": 165652756,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/SingleMuon/Run2017C-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_C*_2017_v2.root",},
        },
    "Mu_D":{
        "era": "2017",
        "subera": "D",
        "channel": "Mu",
        "isData": True,
        "nEvents": 70361660,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/SingleMuon/Run2017D-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_D*_2017_v2.root",},
        },
    "Mu_E":{
        "era": "2017",
        "subera": "E",
        "channel": "Mu",
        "isData": True,
        "nEvents": 154630534,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/SingleMuon/Run2017E-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_E*_2017_v2.root",},
        },
    "Mu_F":{
        "era": "2017",
        "subera": "F",
        "channel": "Mu",
        "isData": True,
        "nEvents": 242135500,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/SingleMuon/Run2017F-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_Mu_F*_2017_v2.root",},
        },
    "El_B":{
        "era": "2017",
        "subera": "B",
        "channel": "El",
        "isData": True,
        "nEvents": 60537490,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/SingleElectron/Run2017B-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_B*_2017_v2.root",},
        },
    "El_C":{
        "era": "2017",
        "subera": "C",
        "channel": "El",
        "isData": True,
        "nEvents": 136637888,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/SingleElectron/Run2017C-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_C*_2017_v2.root",},
        },
    "El_D":{
        "era": "2017",
        "subera": "D",
        "channel": "El",
        "isData": True,
        "nEvents": 51526710,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/SingleElectron/Run2017D-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_D*_2017_v2.root",},
        },
    "El_E":{
        "era": "2017",
        "subera": "E",
        "channel": "El",
        "isData": True,
        "nEvents": 102121689,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/SingleElectron/Run2017E-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_E*_2017_v2.root",},
        },
    "El_F":{
        "era": "2017",
        "subera": "F",
        "channel": "El",
        "isData": True,
        "nEvents": 128467223,
        "color": leg_dict["Data"],
        "source": {"NANOv5": "dbs:/SingleElectron/Run2017F-Nano1June2019-v1/NANOAOD",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/data_El_F*_2017_v2.root",},
    },
}
cutoutV2_ToBeFixed = {
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
        "source": {"NANOv5": "dbs:/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT200_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT200_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT200_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT200_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT200_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT300_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT300_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT300_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT300_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT300_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT500_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT500_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT500_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT500_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT500_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT700_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT700_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT700_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT700_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT700_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1000_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT1000_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT1000_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT1000_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1000_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1500_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT1500_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT1500_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT1500_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT1500_2017_v2.root",],
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
        "source": {"NANOv5": "dbs:/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT2000_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/QCD_HT2000_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/QCD_HT2000_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/QCD_HT2000_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/QCD_HT2000_2017_v2.root",],
    },
}
bookerV2_UNPROCESSED = {
    "ST_tbar_t-channel":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 136.02,
        "source": {"NANOv5": "dbs:/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "NANOv5p1": "dbs:/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/palencia-TopNanoAODv5p1_2017-caa716c30b9109c88acae23be6386548/USER",
                  },
    },
    "ST_t_t-channel":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 80.95,
        "source": {"NANOv5": "dbs:/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "NANOv5p1": "dbs:/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/palencia-TopNanoAODv5p1_2017-caa716c30b9109c88acae23be6386548/USER",
                  },
    },
    "ST_s-channel":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 11.36/3,
        "source": {"NANOv5": "dbs:/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "NANOv5p1": "dbs:/ST_s-channel_4f_leptonDecays_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/palencia-TopNanoAODv5p1_2017-caa716c30b9109c88acae23be6386548/USER",
                  },
    },
    "DYJets_DL-HT100":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 147.4*1.23,
        "color": leg_dict["DY"],
        "source": {"NANOv5": "dbs:/DYJetsToLL_M-50_HT-100to200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "DYJets_DL-HT200":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 40.99*1.23,
        "color": leg_dict["DY"],
        "source": {"NANOv5": "dbs:/DYJetsToLL_M-50_HT-200to400_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "DYJets_DL-HT400":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 5.678*1.23,
        "color": leg_dict["DY"],
        "source": {"NANOv5": "dbs:/DYJetsToLL_M-50_HT-400to600_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "DYJets_DL-HT600":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 1.367*1.23,
        "color": leg_dict["DY"],
        "source": {"NANOv5": "dbs:/DYJetsToLL_M-50_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "DYJets_DL-HT800":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 0.6304*1.23,
        "color": leg_dict["DY"],
        "source": {"NANOv5": "dbs:/DYJetsToLL_M-50_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "DYJets_DL-HT1200":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 0.1514*1.23,
        "color": leg_dict["DY"],
        "source": {"NANOv5": "dbs:/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "DYJets_DL-HT2500":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 0.003565*1.23,
        "color": leg_dict["DY"],
        "source": {"NANOv5": "dbs:/DYJetsToLL_M-50_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "tt_DL-TuneCP5down":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 831.76,
        "color": leg_dict["ttbar"],
        "source": {"NANOv5": "dbs:/TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "tt_DL-TuneCP5up":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 831.76,
        "color": leg_dict["ttbar"],
        "source": {"NANOv5": "dbs:/TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "tt_DL-HDAMPdown":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 831.76,
        "color": leg_dict["ttbar"],
        "source": {"NANOv5": "dbs:/TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "tt_DL-HDAMPup":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 831.76,
        "color": leg_dict["ttbar"],
        "source": {"NANOv5": "dbs:/TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "tt_DL-CR2-GluonMove":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 831.76,
        "color": leg_dict["ttbar"],
        "source": {"NANOv5": "dbs:/TTTo2L2Nu_TuneCP5CR2_GluonMove_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
    "tt_DL-CR1-QCD":{
        "era": "2017",
        "isData": False,
        "nEvents": 1,
        "nEventsPositive": 1,
        "nEventsNegative": 0,
        "sumWeights": 1,
        "sumWeights2": 1,
        "isSignal": False,
        "crossSection": 831.76,
        "color": leg_dict["ttbar"],
        "source": {"NANOv5": "dbs:/TTTo2L2Nu_TuneCP5CR1_QCDbased_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                  },
    },
}
# 'TTZlM10':'TTZToLLNuNu_M-10_TuneCP5_PSweights_13TeV-amcatnlo-pythia8',
# 'TTZlM1to10':'TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8',
# 'TTHB':'ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8',
# 'TTHnoB':'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8',
# 'TTJetsSemiLepUEdnTTbb':'TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8',
# 'TTJetsSemiLepUEupTTbb':'TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8',
# 'TTJetsSemiLepHDAMPdnTTbb':'TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8',
# 'TTJetsSemiLepHDAMPupTTbb':'TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8',

# 'TTJets2L2nuTTbb':'TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8',
# 'TTJetsHadTTbb':'TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8',
# 'TTJetsSemiLepNjet9binTTbb':'TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8',
# 'TTJetsSemiLepNjet0TTbb':'TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0',
# 'TTJetsSemiLepNjet9TTbb':'TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9',

# 'TTJets2L2nuUEdnTTbb':'TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttbb',
# 'TTJets2L2nuUEupTTbb':'TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttbb',
# 'TTJets2L2nuHDAMPdnTTbb':'TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb',
# 'TTJets2L2nuHDAMPupTTbb':'TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb',

# 'TTJetsHadUEdnTTbb':'TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttbb',
# 'TTJetsHadUEupTTbb':'TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttbb',
# 'TTJetsHadHDAMPdnTTbb':'TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb',
# 'TTJetsHadHDAMPupTTbb':'TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb',
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
        "source": {"LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_SL-NOM_2017_v2.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_SL-NOM_2017_v2.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_SL-NOM_2017_v2.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",],
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
        "source": {"LJMLogic": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_DL-NOM-*_2017_v2.root",
                   "LJMLogic__MuMu_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_DL-NOM-*_2017_v2.root",
                   "LJMLogic__ElEl_selection": "glob:/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_DL-NOM-*_2017_v2.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-1_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-2_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-3_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-4_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-5_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-6_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-7_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-8_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-9_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-10_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-11_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-12_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-13_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-14_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_DL/$SYSTEMATIC",
    },
}


def METXYCorr(input_df, run_branch = "run", era = "2017", isData = True, npv_branch = "PV_npvs",
               sysVariations={"$NOMINAL": {"jet_mask": "jet_mask", 
                                           "lep_postfix": "",
                                           "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                           "jet_pt_var": "Jet_pt",
                                           "jet_mass_var": "Jet_mass",
                                           "met_pt_var": "METFixEE2017_pt",
                                           "met_phi_var": "METFixEE2017_phi",
                                           "btagSF": "Jet_btagSF_deepcsv_shape",
                                           "weightVariation": False},
                              "jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp", 
                                              "lep_postfix": "",
                                              "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                              "jet_pt_var": "Jet_pt_jesTotalUp",
                                              "jet_mass_var": "Jet_mass_jesTotalUp",
                                              "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                              "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                              "btagSF": "Jet_btagSF_deepcsv_shape",
                                              "weightVariation": False},
                              "jesTotalDown": {"jet_mask": "jet_mask_jesTotalDown", 
                                                "lep_postfix": "",
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
    listOfColumns = input_df.GetColumnNames()
    z = []
    for sysVar, sysDict in sysVariations.items():
        #skip systematic variations on data, only do the nominal
        if isData and sysVar != "$NOMINAL": 
            continue
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        branchpostfix = "ERROR_NO_BRANCH_POSTFIX_METXYCorr"
        if isWeightVariation == True: 
            continue
        else:
            branchpostfix = "__" + sysVar.replace("$NOMINAL", "nom")
        metPt = sysDict.get("met_pt_var")
        metPhi = sysDict.get("met_phi_var")
        metDoublet = "MET_xycorr_doublet{bpf}".format(bpf=branchpostfix)
        metPtName = "FTAMET{bpf}_pt".format(bpf=branchpostfix)
        metPhiName = "FTAMET{bpf}_phi".format(bpf=branchpostfix)
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
        if defName in listOfColumns:
            if verbose:
                print("{} already defined, skipping".format(defName))
            continue
        else:
            if verbose:
                print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
            rdf = rdf.Define(defName, defFunc)
            listOfColumns.push_back(defName)
    return rdf
        #if metDoublet not in listOfColumns:
            #if verbose: 
            #    print("Doing MET XY correction:\nrdf = rdf.Define(\"{0}\", \"{1}\")".format(metDoublet, def_fnc))
            #rdf = rdf.Define(metDoublet, def_fnc)
            #listOfColumns.push_back(metDoublet)
        #if metPt not in listOfColumns and metPhi not in listOfColumns:
            #if verbose: 
            #    print("rdf = rdf.Define(\"{0}\", \"{1}\")".format(metPt, metDoublet))
            #    print("rdf = rdf.Define(\"{0}\", \"{1}\")".format(metPhi, metDoublet))
            #rdf = rdf.Define(metPt, "{}.first".format(metDoublet))
            #rdf = rdf.Define(metPhi, "{}.second".format(metDoublet))
            #listOfColumns.push_back(metPt)
            #listOfColumns.push_back(metPhi)
    #return rdf


# In[ ]:


def defineLeptons(input_df, input_lvl_filter=None, isData=True, era="2017", rdfLeptonSelection=False, useBackupChannel=False, verbose=False,
                  triggers=[],
                 sysVariations={"$NOMINAL": {"jet_mask": "jet_mask", 
                                             "lep_postfix": "",
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt",
                                             "jet_mass_var": "Jet_mass",
                                             "met_pt_var": "METFixEE2017_pt",
                                             "met_phi_var": "METFixEE2017_phi",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                                },
                 ):
    """Function to take in a dataframe and return one with new columns defined,
    plus event filtering based on the criteria defined inside the function"""
        
    #Set up channel bits for selection and baseline. Separation not necessary in this stage, but convenient for loops
    Chan = {}
    Chan["ElMu"] = 24576
    Chan["MuMu"] = 6144
    Chan["ElEl"] = 512
    Chan["ElEl_LowMET"] = Chan["ElEl"]
    Chan["ElEl_HighMET"] = Chan["ElEl"]
    Chan["Mu"] = 128
    Chan["El"] = 64
    Chan["selection"] = Chan["ElMu"] + Chan["MuMu"] + Chan["ElEl"] + Chan["Mu"] + Chan["El"]
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
    b["MuMu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"], Chan["MuMu_baseline"])
    b["ElEl_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"], Chan["ElEl_baseline"])
    b["Mu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"], Chan["Mu_baseline"])
    b["El_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"] + Chan["Mu_baseline"], Chan["El_baseline"])
    b["selection"] = "ESV_TriggerAndLeptonLogic_selection > 0"
    b["ElMu"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) > 0".format(Chan["ElMu"])
    b["MuMu"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"], Chan["MuMu"])
    b["ElEl"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"] + Chan["MuMu"], Chan["ElEl"])
    b["ElEl_LowMET"] = b["ElEl"]
    b["ElEl_HighMET"] = b["ElEl"]
    b["Mu"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"] + Chan["MuMu"] + Chan["ElEl"], Chan["Mu"])
    b["El"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"] + Chan["MuMu"] + Chan["ElEl"] + Chan["Mu"], Chan["El"])
    if input_lvl_filter == None:
        rdf = input_df.Define("mu_mask", "Muon_pt > 0").Define("e_mask", "Electron_pt > 0")
    else:
        if "baseline" in input_lvl_filter:
            lvl_type = "baseline"
        else:
            lvl_type = "selection"
        rdf_input = input_df.Filter(b[input_lvl_filter], input_lvl_filter)
        rdf = rdf_input
        for trgTup in triggers:
            if trgTup.era != era: continue
            trg = trgTup.trigger
            rdf = rdf.Define("typecast___{}".format(trg), "return (int){} == true;".format(trg))
        if not rdfLeptonSelection:
            rdf = rdf.Define("mu_mask", "(Muon_OSV_{0} & {1}) > 0 && Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_looseId == true && Muon_pfIsoId >= 4 && abs(Muon_ip3d) < 0.10 && abs(Muon_dz) < 0.02".format(lvl_type, Chan[input_lvl_filter]))
            rdf = rdf.Define("e_mask", "(Electron_OSV_{0} & {1}) > 0 && Electron_pt > 15 && Electron_cutBased >= 2 && ((abs(Electron_eta) < 1.4442 && abs(Electron_ip3d) < 0.05 && abs(Electron_dz) < 0.1) || (abs(Electron_eta) > 1.5660 && abs(Electron_eta) < 2.5 && abs(Electron_ip3d) < 0.10 && abs(Electron_dz) < 0.2))".format(lvl_type, Chan[input_lvl_filter]))
        else:
            pass
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
    #only valid postfix for leptons, excluding calculations involving MET, is "" for now, can become "__SOMETHING" inside a loop on systematic variations 
    leppostfix = ""
    
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
    z.append(("nFTAMuon{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Muon{pf}_pt.size())"))
    z.append(("nLooseFTAMuon{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Muon_looseId[mu_mask && Muon_looseId == true].size())"))
    z.append(("nMediumFTAMuon{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Muon_mediumId[mu_mask && Muon_mediumId == true].size())"))
    z.append(("nTightFTAMuon{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Muon_tightId[mu_mask && Muon_tightId == true].size())"))
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
    z.append(("nFTAElectron{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Electron_pt[e_mask].size())"))
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
    z.append(("nLooseFTAElectron{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Sum(FTAElectron{lpf}_cutBased >= 2))".format(lpf=leppostfix)))
    z.append(("nMediumFTAElectron{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Sum(FTAElectron{lpf}_cutBased >= 3))".format(lpf=leppostfix)))
    z.append(("nTightFTAElectron{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Sum(FTAElectron{lpf}_cutBased >= 4))".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_InvariantMass".format(lpf=leppostfix), "nFTAElectron{lpf} == 2 ? InvariantMass(FTAElectron{lpf}_pt, FTAElectron{lpf}_eta, FTAElectron{lpf}_phi, FTAElectron{lpf}_mass) : -0.1".format(lpf=leppostfix)))
    if isData == False:
        z.append(("FTAElectron{lpf}_SF_EFF_nom".format(lpf=leppostfix), "Electron_SF_EFF_nom[e_mask]"))
        z.append(("FTAElectron{lpf}_SF_EFF_unc".format(lpf=leppostfix), "Electron_SF_EFF_unc[e_mask]"))
        z.append(("FTAElectron{lpf}_SF_ID_nom".format(lpf=leppostfix), "Electron_SF_ID_nom[e_mask]"))
        z.append(("FTAElectron{lpf}_SF_ID_unc".format(lpf=leppostfix), "Electron_SF_ID_unc[e_mask]"))
    #LEPTONS
    z.append(("nLooseFTALepton{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(nLooseFTAMuon{lpf} + nLooseFTAElectron{lpf})".format(lpf=leppostfix)))
    z.append(("nMediumFTALepton{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(nMediumFTAMuon{lpf} + nMediumFTAElectron{lpf})".format(lpf=leppostfix)))
    z.append(("nTightFTALepton{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(nTightFTAMuon{lpf} + nTightFTAElectron{lpf})".format(lpf=leppostfix)))
    z.append(("nFTALepton{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(nFTAMuon{lpf} + nFTAElectron{lpf})".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_argsort".format(lpf=leppostfix), "Reverse(Argsort(Concatenate(Muon_pt[mu_mask], Electron_pt[e_mask])))"))
    z.append(("FTALepton{lpf}_pt".format(lpf=leppostfix), "Take(Concatenate(Muon_pt[mu_mask], Electron_pt[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_eta".format(lpf=leppostfix), "Take(Concatenate(Muon_eta[mu_mask], Electron_eta[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_phi".format(lpf=leppostfix), "Take(Concatenate(Muon_phi[mu_mask], Electron_phi[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_jetIdx".format(lpf=leppostfix), "Take(Concatenate(Muon_jetIdx[mu_mask], Electron_jetIdx[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_pdgId".format(lpf=leppostfix), "Take(Concatenate(Muon_pdgId[mu_mask], Electron_pdgId[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_dRll".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? ROOT::VecOps::DeltaR(FTALepton{lpf}_eta.at(0), FTALepton{lpf}_eta.at(1), FTALepton{lpf}_phi.at(0), FTALepton{lpf}_phi.at(1)) : -0.1".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_dPhill".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? ROOT::VecOps::DeltaPhi(FTALepton{lpf}_phi.at(0), FTALepton{lpf}_phi.at(1)) : -999".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_dEtall".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? abs(FTALepton{lpf}_eta.at(0) - FTALepton{lpf}_eta.at(1)) : -999".format(lpf=leppostfix)))
    z.append(("nFTALepton{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(FTALepton{lpf}_pt.size())".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_pt_LeadLep".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 0 ? FTALepton{lpf}_pt.at(0) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_pt_SubleadLep".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? FTALepton{lpf}_pt.at(1) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_eta_LeadLep".format(lpf=leppostfix), "FTALepton{lpf}_eta.size() > 0 ? FTALepton{lpf}_eta.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_eta_SubleadLep".format(lpf=leppostfix), "FTALepton{lpf}_eta.size() > 1 ? FTALepton{lpf}_eta.at(1) : -9999".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_jetIdx_0".format(lpf=leppostfix), "FTALepton{lpf}_jetIdx.size() > 0 ? FTALepton{lpf}_jetIdx.at(0) : -1".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_jetIdx_1".format(lpf=leppostfix), "FTALepton{lpf}_jetIdx.size() > 1 ? FTALepton{lpf}_jetIdx.at(1) : -1".format(lpf=leppostfix)))
    if isData == False:
        z.append(("FTALepton{lpf}_SF_nom".format(lpf=leppostfix), "Take(Concatenate(FTAMuon{lpf}_SF_ID_nom*FTAMuon{lpf}_SF_ISO_nom, FTAElectron{lpf}_SF_ID_nom*FTAElectron{lpf}_SF_EFF_nom), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))

    z.append(("FTAMuon{lpf}_pt_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_pt.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 13 ? FTALepton{lpf}_pt.at(0) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTAMuon{lpf}_pt_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_pt.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 13 ? FTALepton{lpf}_pt.at(1) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTAMuon{lpf}_eta_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_eta.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 13 ? FTALepton{lpf}_eta.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTAMuon{lpf}_eta_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_eta.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 13 ? FTALepton{lpf}_eta.at(1) : -9999".format(lpf=leppostfix)))
    z.append(("FTAMuon{lpf}_phi_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_phi.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 13 ? FTALepton{lpf}_phi.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTAMuon{lpf}_phi_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_phi.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 13 ? FTALepton{lpf}_phi.at(1) : -9999".format(lpf=leppostfix)))

    z.append(("FTAElectron{lpf}_pt_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_pt.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 11 ? FTALepton{lpf}_pt.at(0) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_pt_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_pt.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 11 ? FTALepton{lpf}_pt.at(1) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_eta_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_eta.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 11 ? FTALepton{lpf}_eta.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_eta_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_eta.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 11 ? FTALepton{lpf}_eta.at(1) : -9999".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_phi_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_phi.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 11 ? FTALepton{lpf}_phi.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_phi_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_phi.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 11 ? FTALepton{lpf}_phi.at(1) : -9999".format(lpf=leppostfix)))


    for sysVar, sysDict in sysVariations.items():
        #skip systematic variations on data, only do the nominal
        if isData and sysVar != "$NOMINAL": 
            continue
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        if isWeightVariation == True: continue
        syspostfix = "___" + sysVar.replace("$NOMINAL", "nom")
        branchpostfix = "__nom" if isWeightVariation else "__" + sysVar.replace("$NOMINAL", "nom")
        #metPt = sysDict.get("met_pt_var")
        #metPhi = sysDict.get("met_phi_var")
        #These are the xy corrected MET values, to be used in the calculations
        metPtName = "FTAMET{bpf}_pt".format(bpf=branchpostfix)#"source" variable so use the branchpostfix of this systematic, whereas defines should use syspostfix like "MTof..."
        metPhiName = "FTAMET{bpf}_phi".format(bpf=branchpostfix)
        z.append(("MTofMETandMu{bpf}".format(bpf=branchpostfix), 
                         "FTA::transverseMassMET(FTAMuon{lpf}_pt, FTAMuon{lpf}_phi, FTAMuon{lpf}_mass, {mpt}, {mph})".format(lpf=leppostfix, mpt=metPtName, mph=metPhiName)))
        z.append(("MTofMETandEl{bpf}".format(bpf=branchpostfix),  
                         "FTA::transverseMassMET(FTAElectron{lpf}_pt, FTAElectron{lpf}_phi, FTAElectron{lpf}_mass, {mpt}, {mph})".format(lpf=leppostfix, mpt=metPtName, mph=metPhiName)))
        #There shouldn't be any variation on this quantity, but... easier looping
        z.append(("MTofElandMu{bpf}".format(bpf=branchpostfix), 
                         "FTA::transverseMass(FTAMuon{lpf}_pt, FTAMuon{lpf}_phi, FTAMuon{lpf}_mass, FTAElectron{lpf}_pt, FTAElectron{lpf}_phi, FTAElectron{lpf}_mass)".format(lpf=leppostfix)))

    
    listOfColumns = rdf.GetColumnNames()
    #Add them to the dataframe...
    for defName, defFunc in z:
        if defName in listOfColumns:
            if verbose:
                print("{} already defined, skipping".format(defName))
            continue
        else:
            if verbose:
                print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
            rdf = rdf.Define(defName, defFunc)
            listOfColumns.push_back(defName)
    return rdf

def defineInitWeights(input_df, crossSection=0, era="2017", sumWeights=-1, lumiOverride=None,
                  nEvents=-1, nEventsPositive=2, nEventsNegative=1,
                  isData=True, verbose=False):
    leppostfix = ""
    lumiDict = {"2017": 41.53,
                "2018": 59.97}
    lumi = lumiDict.get(era, 41.53)
    
    mc_def = collections.OrderedDict()
    data_def = collections.OrderedDict()
    mc_def["wgt_NUMW"] = "({xs:s} * {lumi:s} * 1000 * genWeight) / (abs(genWeight) * ( {nevtp:s} - {nevtn:s} ) )".format(xs=str(crossSection), lumi=str(lumi), nevt=str(nEvents),
                    nevtp=str(nEventsPositive), nevtn=str(nEventsNegative))
    mc_def["wgt_SUMW"] = "({xs:s} * {lumi:s} * 1000 * genWeight) / {sumw:s}".format(xs=str(crossSection), lumi=str(lumi), sumw=str(sumWeights))
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

def defineJets(input_df, era="2017", doAK8Jets=False, jetPtMin=30.0, jetPUId=None, useDeltaR=True, isData=True,
               nJetsToHisto=10, bTagger="DeepCSV", verbose=False,
               sysVariations={"$NOMINAL": {"jet_mask": "jet_mask",
                                           "lep_postfix": "", 
                                           "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                           "jet_pt_var": "Jet_pt",
                                           "jet_mass_var": "Jet_mass",
                                           "met_pt_var": "METFixEE2017_pt",
                                           "met_phi_var": "METFixEE2017_phi",
                                           "btagSF": "Jet_btagSF_deepcsv_shape",
                                           "weightVariation": False},
                              "jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp", 
                                              "lep_postfix": "",
                                              "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                              "jet_pt_var": "Jet_pt_jesTotalUp",
                                              "jet_mass_var": "Jet_mass_jesTotalUp",
                                              "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                              "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                              "btagSF": "Jet_btagSF_deepcsv_shape",
                                              "weightVariation": False},
                              "jesTotalDown": {"jet_mask": "jet_mask_jesTotalDown", 
                                                "lep_postfix": "",
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
    if bTagger.lower() == "deepcsv":
        useDeepCSV=True
    elif bTagger.lower() == "deepjet":
        useDeepCSV=False
    elif bTagger.lower() == "csvv2":
        raise RuntimeError("CSVv2 is not a supported bTagger option in defineJets() right now")
    else:
        raise RuntimeError("{} is not a supported bTagger option in defineJets()".format(bTagger))
    print("FIXMEFIXME: Setting Jet_pt min to 30GeV! Must fix!")
    leppostfix = ""
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
        postfix = "__" + sysVar.replace("$NOMINAL", "nom")
        
        #Fill lists
        if jetPUId:
            if jetPUId == 'L':
                jetPUId = " && Jet_puId >= 4" #pass Loose Id, >=6 pass Medium, ==7 pass Tight
            elif jetPUId == 'M':
                jetPUId = " && Jet_puId >= 6" #pass Loose Id, >=6 pass Medium, ==7 pass Tight
            elif jetPUId == 'T':
                jetPUId = " && Jet_puId == 7" #pass Loose Id, >=6 pass Medium, ==7 pass Tight
            else:
                raise ValueError("Invalid Jet PU Id selected")
        else:
            jetPUId = ""
        z.append(("Jet_idx", "FTA::generateIndices(Jet_pt)"))
        z.append(("pre{jm}".format(jm=jetMask), "({jpt} >= {jptMin} && abs(Jet_eta) <= 2.5 && Jet_jetId > 2{jpuid})".format(lpf=leppostfix, 
                                                                                                                            jpt=jetPt, 
                                                                                                                            jptMin=jetPtMin,
                                                                                                                            jpuid=jetPUId
                                                                                                                        )))
        if useDeltaR is False: #Use PFMatching
            z.append(("{jm}".format(jm=jetMask), "ROOT::VecOps::RVec<Int_t> jmask = ({jpt} >= {jptMin} && abs(Jet_eta) <= 2.5 && Jet_jetId > 2{jpuid}); "\
                      "for(int i=0; i < FTALepton{lpf}_jetIdx.size(); ++i){{jmask = jmask && (Jet_idx != FTALepton{lpf}_jetIdx.at(i));}}"\
                      "return jmask;".format(lpf=leppostfix, jpt=jetPt, jptMin=jetPtMin, jpuid=jetPUId)))
        else: #DeltaR matching
            z.append(("{jm}".format(jm=jetMask), "ROOT::VecOps::RVec<Int_t> jmask = ({jpt} >= {jptMin} && abs(Jet_eta) <= 2.5 && Jet_jetId > 2{jpuid}); "\
                      "for(int i=0; i < FTALepton{lpf}_jetIdx.size(); ++i){{"\
                      "ROOT::VecOps::RVec<Float_t> dr;"\
                      "for(int j=0; j < jmask.size(); ++j){{"\
                      "dr.push_back(ROOT::VecOps::DeltaR(Jet_eta.at(j), FTALepton{lpf}_eta.at(i), Jet_phi.at(j), FTALepton{lpf}_phi.at(i)));}}"\
                      "jmask = jmask && dr >= {drt};"\
                      "dr.clear();}}"\
                      "return jmask;".format(lpf=leppostfix, jpt=jetPt, jptMin=jetPtMin, jpuid=jetPUId, drt=useDeltaR)))
        #Store the Jet Pt, Jet Raw Pt, Lep Pt
        z.append(("FTACrossCleanedJet{pf}_pt".format(pf=postfix), "(FTALepton{lpf}_jetIdx.at(0) >= 0 && pre{jm}.at(FTALepton{lpf}_jetIdx.at(0)) == true) ? {jpt}.at(FTALepton{lpf}_jetIdx.at(0)) : 0.0".format(jm=jetMask, lpf=leppostfix, jpt=jetPt)))
        z.append(("FTACrossCleanedJet{pf}_rawpt".format(pf=postfix), "(FTALepton{lpf}_jetIdx.at(0) >= 0 && pre{jm}.at(FTALepton{lpf}_jetIdx.at(0)) == true) ? (1 - Jet_rawFactor.at(FTALepton{lpf}_jetIdx.at(0))) * {jpt}.at(FTALepton{lpf}_jetIdx.at(0)) : 0.0".format(jm=jetMask, lpf=leppostfix, jpt=jetPt)))
        z.append(("FTACrossCleanedJet{pf}_leppt".format(pf=postfix), "(FTALepton{lpf}_jetIdx.at(0) >= 0 && pre{jm}.at(FTALepton{lpf}_jetIdx.at(0)) == true) ? FTALepton{lpf}_pt.at(0) : 0.0".format(jm=jetMask, lpf=leppostfix, jpt=jetPt)))
        # z.append(("FTACrossCleanedJet{pf}_diffpt".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) >= 0 ? FTACrossCleanedJet{pf}_pt + FTACrossCleanedJet{pf}_leppt - FTACrossCleanedJet{pf}_rawpt : -9999".format(jm=jetMask, lpf=leppostfix, pf=postfix)))
        z.append(("FTACrossCleanedJet{pf}_diffpt".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) >= 0 ? FTACrossCleanedJet{pf}_leppt - FTACrossCleanedJet{pf}_pt : -9999".format(jm=jetMask, lpf=leppostfix, pf=postfix)))
        z.append(("FTACrossCleanedJet{pf}_diffptraw".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) >= 0 ? (-1.0 * Jet_rawFactor * {jpt}).at(FTALepton{lpf}_jetIdx.at(0)) : -9999".format(jm=jetMask, lpf=leppostfix, pf=postfix, jpt=jetPt)))
        z.append(("FTACrossCleanedJet{pf}_diffptrawinverted".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) < 0 ? ROOT::VecOps::RVec<Float_t>(-1.0 * Jet_rawFactor * {jpt}[pre{jm}]) : ROOT::VecOps::RVec<Float_t> {{-9999.0}}".format(jm=jetMask, lpf=leppostfix, pf=postfix, jpt=jetPt)))
        z.append(("nFTAJet{pf}".format(pf=postfix), "static_cast<Int_t>({jm}[{jm}].size())".format(jm=jetMask)))
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
        if isData == False:
            z.append(("FTAJet{pf}_genJetIdx".format(pf=postfix), "Jet_genJetIdx[{jm}]".format(jm=jetMask)))
            z.append(("nFTAJet{pf}_genMatched".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_genJetIdx[FTAJet{pf}_genJetIdx >= 0].size())".format(pf=postfix)))
            z.append(("nFTAJet{pf}_puIdLoose".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_genJetIdx[(FTAJet{pf}_puId >= 4 || FTAJet{pf}_pt >= 50)].size())".format(pf=postfix)))
            z.append(("nFTAJet{pf}_genMatched_puIdLoose".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_genJetIdx[FTAJet{pf}_genJetIdx >= 0 && (FTAJet{pf}_puId >= 4 || FTAJet{pf}_pt >= 50)].size())".format(pf=postfix)))
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
        z.append(("nLooseDeepCSVB{pf}".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_LooseDeepCSVB.size())".format(pf=postfix)))
        z.append(("nMediumDeepCSVB{pf}".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_MediumDeepCSVB.size())".format(pf=postfix)))
        z.append(("nTightDeepCSVB{pf}".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_TightDeepCSVB.size())".format(pf=postfix)))
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
        z.append(("ST{pf}".format(pf=postfix), "Sum(FTAJet{pf}_pt) + Sum(FTALepton{lpf}_pt)".format(pf=postfix, lpf=leppostfix)))
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
    listOfColumns = rdf.GetColumnNames()
    for defName, defFunc in z:
        if defName in listOfColumns:
            if verbose:
                print("{} already defined, skipping".format(defName))
            continue
        else:
            if verbose:
                print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
            rdf = rdf.Define(defName, defFunc)
            listOfColumns.push_back(defName)
                
    return rdf


def defineWeights(input_df_or_nodes, era, splitProcess=None, isData=False, verbose=False, final=False, sysVariations={"$NOMINAL":"NoValueNeeded"}):
    """Define all the pre-final or final weights and the variations, to be referened by the sysVariations dictionaries as wgt_final.
    if final=False, do the pre-final weights for BTaggingYields calculations.
    
    pwgt = partial weight, component for final weight
    wgt_$SYSTEMATIC is form of final event weights, i.e. wgt_nom or wgt_puWeightDown
    prewgt_$SYSTEMATIC is form of weight for BTaggingYields calculation, should include everything but pwgt_btag__$SYSTEMATIC"""
    # if splitProcess != None:
    if isinstance(input_df_or_nodes, (dict, collections.OrderedDict)):
        print("Splitting process in defineWeights()")
        filterNodes = input_df_or_nodes.get("filterNodes")
        nodes = input_df_or_nodes.get("nodes")
        defineNodes = input_df_or_nodes.get("defineNodes")
        diagnosticNodes = input_df_or_nodes.get("diagnosticNodes")
        countNodes = input_df_or_nodes.get("countNodes")
    else:
        raise NotImplementedError("Non-split process has been deprecated in defineWeights, wrap the RDF nodes in nodes['<process-name>'] dictionary")
        # rdf = input_df_or_nodes

    #There's only one lepton branch variation (nominal), but if it ever changes, this will serve as sign it's referenced here and made need to be varied
    leppostfix = ""
    lumiDict = {"2017": 41.53,
                "2018": 59.97}


    #era = "2017"
    # mc_def["wgt_SUMW"] = "({xs:s} * {lumi:s} * 1000 * genWeight) / {sumw:s}".format(xs=str(crossSection), lumi=str(lumi), sumw=str(sumWeights))

    #Two lists of weight definitions, one or the other is chosen at the end via 'final' optional parameter
    zFin = []
    zPre = []
    # zFin.append(("pwgt___LumiXS", "wgt_SUMW")) #Now defined in the splitProcess function
    zFin.append(("pwgt_LSF___nom", "(FTALepton{lpf}_SF_nom.size() > 1 ? FTALepton{lpf}_SF_nom.at(0) * FTALepton{lpf}_SF_nom.at(1) : FTALepton{lpf}_SF_nom.at(0))".format(lpf=leppostfix)))
    # zPre.append(("pwgt___LumiXS", "wgt_SUMW")) #alias this until it's better defined here or elsewhere
    zPre.append(("pwgt_LSF___nom", "(FTALepton{lpf}_SF_nom.size() > 1 ? FTALepton{lpf}_SF_nom.at(0) * FTALepton{lpf}_SF_nom.at(1) : FTALepton{lpf}_SF_nom.at(0))".format(lpf=leppostfix)))
    if era == "2017": #This only applies to 2017
        zPre.append(("pwgt_Z_vtx___nom", "((FTALepton{lpf}_pdgId.size() > 1 && (abs(FTALepton{lpf}_pdgId.at(0)) == 11 || abs(FTALepton{lpf}_pdgId.at(1)) == 11)) || (FTALepton{lpf}_pdgId.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 11)) ? EGamma_HLT_ZVtx_SF_nom : 1.00000000000000".format(lpf=leppostfix)))
    else:
        zPre.append(("pwgt_Z_vtx___nom", "(Int_t)1;"))
    
    #WARNING: on btag weights, it can ALWAYS be 'varied' to match the systematic, so that the event weight from
    #the correct jet collection, btag SFs, and yields is used. Always match! This duplicates some calculations uselessly
    #in the BTaggingYields function, but it should help avoid mistakes at the level of final calculations
    
    print("\nFIXME: Need to propagate pwgt_Z_vtx___nom to all non-nominal event weights properly.\n")
    #Nominal weight
    zFin.append(("wgt___nom", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom * pwgt_btag___nom"))
    #pre-btagging yield weight. Careful modifying, it is 'inherited' for many other weights below!
    zPre.append(("prewgt___nom", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    
    #JES Up and Down - effectively the nominal weight, but with the CORRECT btag weight for those jets!
    if "jesTotalDown" in sysVariations.keys():
        zFin.append(("wgt___jesTotalDown", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag___jesTotalDown * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___jesTotalDown", "prewgt___nom * pwgt_Z_vtx___nom")) #JES *weight* only changes with event-level btag weight, so this is just the nominal
        
    if "jesTotalDown" in sysVariations.keys():
        zPre.append(("prewgt___jesTotalUp", "prewgt___nom"))
        zFin.append(("wgt___jesTotalUp", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag___jesTotalUp"))
    
    #Pileup variations 
    print("FIXME: Using temporary definition of weights for PU variations (change pwgt_btag__VARIATION)")
    if "puWeightDown" in sysVariations.keys():
        zFin.append(("wgt___puWeightDown", "pwgt___LumiXS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag___nom * pwgt_Z_vtx___nom"))
        #zFin.append(("wgt___puWeightDown", "pwgt___LumiXS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag__puWeightDown * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___puWeightDown", "pwgt___LumiXS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
        #zPre.append(("prewgt___puWeightDown", "pwgt___LumiXS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    if "puWeightUp" in sysVariations.keys():
        zFin.append(("wgt___puWeightUp", "pwgt___LumiXS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag___nom * pwgt_Z_vtx___nom"))
        #zFin.append(("wgt___puWeightUp", "pwgt___LumiXS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag__puWeightUp * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___puWeightUp", "pwgt___LumiXS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
        #zPre.append(("prewgt___puWeightUp", "pwgt___LumiXS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    
    
    #L1 PreFiring variations
    print("FIXME: Using temporary definition of weights for L1PreFire variations (change pwgt_btag__VARIATION)")
    if "L1PreFireDown" in sysVariations.keys():
        zFin.append(("wgt___L1PreFireDown", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF___nom * pwgt_btag___nom * pwgt_Z_vtx___nom"))
        #zFin.append(("wgt___L1PreFireDown", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF___nom * pwgt_btag__L1PreFireDown * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___L1PreFireDown", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
        #zPre.append(("prewgt___L1PreFireDown", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    
    if "L1PreFireUp" in sysVariations.keys():
        zFin.append(("wgt___L1PreFireUp", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Up * pwgt_LSF___nom * pwgt_btag___nom * pwgt_Z_vtx___nom"))
        #zFin.append(("wgt___L1PreFireUp", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Up * pwgt_LSF___nom * pwgt_btag__L1PreFireUp * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___L1PreFireUp", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Up * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
        #zPre.append(("prewgt___L1PreFireUp", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Up * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    
    #Lepton ScaleFactor variations
    #To be done, still...
    
    #HLT SF variations
    #To be done, still...
    
    #Pure BTagging variations, no other variations necessary. 
    #Since there may be many, use a common base factor for fewer multiplies... for pre-btagging, they're identical!
    print("\n\nWARNING! WARNING! L1PreFiringWeight Only applies to 2017 and perhaps 2016, drop it from calculations in 2018!")
    zFin.append(("pwgt_btagSF_common", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    zPre.append(("pwgt_btagSF_common", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    
    if "btagSF_deepcsv_shape_down_hf" in sysVariations.keys():
        zFin.append(("wgt___btagSF_deepcsv_shape_down_hf", "pwgt_btagSF_common * pwgt_btag___btagSF_deepcsv_shape_down_hf * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___btagSF_deepcsv_shape_down_hf", "pwgt_btagSF_common * pwgt_Z_vtx___nom"))#Really just aliases w/o btagging part
    if "btagSF_deepcsv_shape_up_hf" in sysVariations.keys():
        zFin.append(("wgt___btagSF_deepcsv_shape_up_hf", "pwgt_btagSF_common * pwgt_btag___btagSF_deepcsv_shape_up_hf * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___btagSF_deepcsv_shape_up_hf", "pwgt_btagSF_common * pwgt_Z_vtx___nom"))
    if "btagSF_deepcsv_shape_down_lf" in sysVariations.keys():
        zFin.append(("wgt___btagSF_deepcsv_shape_down_lf", "pwgt_btagSF_common * pwgt_btag___btagSF_deepcsv_shape_down_lf * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___btagSF_deepcsv_shape_down_lf", "pwgt_btagSF_common * pwgt_Z_vtx___nom"))
    if "btagSF_deepcsv_shape_up_lf" in sysVariations.keys():
        zFin.append(("wgt___btagSF_deepcsv_shape_up_lf", "pwgt_btagSF_common * pwgt_btag___btagSF_deepcsv_shape_up_lf * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___btagSF_deepcsv_shape_up_lf", "pwgt_btagSF_common * pwgt_Z_vtx___nom"))

    #Special variations for testing central components
    zFin.append(("wgt___no_btag_shape_reweight", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    zFin.append(("wgt___no_LSF", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_Z_vtx___nom"))
    zFin.append(("wgt___no_L1PreFiringWeight", "pwgt___LumiXS * puWeight * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    zFin.append(("wgt___no_puWeight", "pwgt___LumiXS * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))

    zPre.append(("prewgt___no_btag_shape_reweight", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    zPre.append(("prewgt___no_LSF", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_Z_vtx___nom"))
    zPre.append(("prewgt___no_L1PreFiringWeight", "pwgt___LumiXS * puWeight * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    zPre.append(("prewgt___no_puWeight", "pwgt___LumiXS * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))


    #Factorization/Renormalization weights... depend on dividing genWeight back out?
    #TBD x4 for top samples, MAYBE NOT FOR OTHERS! (Until "Run II Legacy" samples are being used)
    
    #Load the initial or final definitions
    if final:
        z = zFin
    else:
        z = zPre
    nodes = input_df_or_nodes.get("nodes")
    for processName in nodes:
        if processName.lower() == "basenode": continue
        # pdb.set_trace()
        listOfColumns = nodes[processName]["BaseNode"].GetColumnNames()
        if isData:
            defName = "wgt___nom"
            defFunc = "int i = 1; return i"
            if defName not in listOfColumns:
                nodes[processName]["BaseNode"] = nodes[processName]["BaseNode"].Define(defName, defFunc)
        else:
            for defName, defFunc in z:
                if defName in listOfColumns:
                    if verbose:
                        print("{} already defined, skipping".format(defName))
                    continue
                else:
                    # prereqs = re.findall(r"[\w']+", defFunc)
                    # allPreReqs = True
                    # for prereq in prereqs:
                    #     if prereq not in listOfColumns: allPreReqs = False
                    if verbose:
                        print("nodes[processName][\"BaseNode\"] = nodes[processName][\"BaseNode\"].Define(\"{}\", \"{}\")".format(defName, defFunc))
                    nodes[processName]["BaseNode"] = nodes[processName]["BaseNode"].Define(defName, defFunc)
                    listOfColumns.push_back(defName) 

                    # if allPreReqs:
                    #     nodes[processName]["BaseNode"] = nodes[processName]["BaseNode"].Define(defName, defFunc)
                    #     listOfColumns.push_back(defName) 
                    # else:
                    #     print("Skipping definition for {} due to missing prereqs in the list: {}".format(defName, prereqs))
               
    #return the dictionary of all nodes
    return input_df_or_nodes

    # else:
    #     z = zPre

    #     listOfColumns = rdf.GetColumnNames()
    #     if isData:
    #         defName = "wgt___nom"
    #         defFunc = "int i = 1; return i"
    #         if defName not in listOfColumns:
    #             rdf = rdf.Define(defName, defFunc)
    #     else:
    #         for defName, defFunc in z:
    #             if defName in listOfColumns:
    #                 if verbose:
    #                     print("{} already defined, skipping".format(defName))
    #                 continue
    #             else:
    #                 if verbose:
    #                     print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
    #                 rdf = rdf.Define(defName, defFunc)
                    
    #                 listOfColumns.push_back(defName) 
    #     return rdf
    
def BTaggingYields(input_df_or_nodes, sampleName, channel="All", isData = True, histosDict=None, bTagger="DeepCSV", verbose=False,
                   loadYields=None, lookupMap="LUM", useAggregate=True, useHTOnly=False, useNJetOnly=False, 
                   calculateYields=True, HTArray=[500, 650, 800, 1000, 1200, 10000], nJetArray=[4,5,6,7,8,20],
                   sysVariations={"$NOMINAL": {"jet_mask": "jet_mask",
                                               "lep_postfix": "", 
                                               "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                               "jet_pt_var": "Jet_pt",
                                               "jet_mass_var": "Jet_mass",
                                               "met_pt_var": "METFixEE2017_pt",
                                               "met_phi_var": "METFixEE2017_phi",
                                               "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                                          "DeepJet": "Jet_btagSF_deepjet_shape",
                                                      },
                                               "weightVariation": False},
                                  "btagSF_deepcsv_shape_up_hf": {"jet_mask": "jet_mask",
                                                                  "lep_postfix": "", 
                                                                  "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                                  "jet_pt_var": "Jet_pt",
                                                                  "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape_up_hf",
                                                                             "DeepJet": "Jet_btagSF_deepjet_shape_up_hf",
                                                                         },
                                                                  "weightVariation": True},
                                  "btagSF_deepcsv_shape_down_lf": {"jet_mask": "jet_mask",
                                                                    "lep_postfix": "", 
                                                                    "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                                    "jet_pt_var": "Jet_pt",
                                                                    "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape_down_lf",
                                                                               "DeepJet": "Jet_btagSF_deepjet_shape_down_lf",
                                                                           },
                                                                    "weightVariation": True},
                                              },
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
    special replacement for nominal, and "jesTotalUp" -> "prewgt_jesTotalUp" is expected
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
        for processName in nodes.keys():
            if processName.lower() == "basenode": continue
            #Add key to histos dictionary, if calculating the yields
            if calculateYields and processName not in histosDict:
                histosDict[processName] = collections.OrderedDict()
                histosDict[processName][channel] = collections.OrderedDict()
            if processName not in  bTaggingDefineNodes:
                 bTaggingDefineNodes[processName] = collections.OrderedDict()
            if processName not in diagnosticNodes:
                diagnosticNodes[processName] = collections.OrderedDict()
            if processName not in countNodes:
                countNodes[processName] = collections.OrderedDict()
            # for decayChannel in nodes[processName].keys():
            #     if processName not in nodes[processName]:
            #         nodes[processName][decayChannel] = collections.OrderedDict()
            #     if processName not in  bTaggingDefineNodes[processName]:
            #          bTaggingDefineNodes[processName][decayChannel] = collections.OrderedDict()
            #     if processName not in diagnosticNodes[processName]:
            #         diagnosticNodes[processName][decayChannel] = collections.OrderedDict()
            #     if processName not in countNodes[processName]:
            #         countNodes[processName][decayChannel] = collections.OrderedDict()
            
            if loadYields != None:
                while iLUM[processName].size() < nSlots:
                    if isinstance(loadYields, str):
                        iLUM[processName].push_back(ROOT.TH2Lookup(loadYields))
                    else:
                        raise RuntimeError("No string path to a yields file has been provided in BTaggingYields() ...")
                        
                #Test to see that it's accessible...
                testKeyA = yieldsKey + "___nom"
                # testKeyB = "__nom"
                testNJ = 6
                testHT = 689.0
                if verbose:
                    testVal = iLUM[processName][0].getEventYieldRatio(testKeyA, testNJ, testHT, True)
                    print("BTaggingYield has done a test evaluation on the yield histogram with search for histogram {}, nJet={}, HT={} and found value {}"\
                          .format(testKeyA, testNJ, testHT, testVal))
                else:
                    testVal = iLUM[processName][0].getEventYieldRatio(testKeyA, testNJ, testHT)
                # pdb.set_trace()
                assert type(testVal) == float, "LookupMap did not provide a valid return type, something is wrong"
                assert testVal >= 0.0, "LookupMap did not provide a reasonable BTagging Yield ratio in the test... ({} is considered unrealistic...)".format(testVal)
                assert testVal <= 5.0, "LookupMap did not provide a reasonable BTagging Yield ratio in the test... ({} is considered unrealistic...)".format(testVal)
        
            listOfColumns = nodes[processName]["BaseNode"].GetColumnNames() #This is a superset, containing non-Define'd columns as well


            # rdf = input_df
            #Create list of the variations to be histogrammed (2D yields)
            yieldList = []
            for sysVar, sysDict in sysVariations.items():
                bTaggingDefineNodes[processName][sysVar] = []
                isWeightVariation = sysDict.get("weightVariation")
                branchpostfix = "__nom" if isWeightVariation else "__" + sysVar.replace("$NOMINAL", "nom") #branch postfix for identifying input branch variation
                syspostfix = "___" + sysVar.replace("$NOMINAL", "nom")
                jetMask = sysDict.get("jet_mask") #mask as defined for the jet collection under this systematic variation
                jetPt = sysDict.get("jet_pt_var") #colum name of jet pt collection for this systematic
                jetSF = sysDict.get("btagSF").get(bTagger, "NO / VALID / jetSF") #colum name of per-jet shape SFs
                #We must get or calculate various weights, defined below
                #This btagSFProduct is the product of the SFs for the selected jets from collection jetPt with mask jetMask
                btagSFProduct = "btagSFProduct{spf}".format(spf=syspostfix)
                #input weight, should include all corrections for this systematic variation except BTagging SF and yield ratio
                calculationWeightBefore = "prewgt{spf}".format(spf=syspostfix)
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
                    bTaggingDefineNodes[processName][sysVar].append(("{}".format(btagSFProduct), "FTA::btagEventWeight_shape({}, {})".format(jetSF, jetMask)))
                if calculationWeightAfter not in listOfColumns:
                    bTaggingDefineNodes[processName][sysVar].append(("{}".format(calculationWeightAfter), "{} * {}".format(calculationWeightBefore, 
                                                                                                                                 btagSFProduct)))
                        
                #Check that the HT and nJet numbers are available to us, and if not, define them based on the available masks    
                #if isScaleVariation:
                nJetName = "nFTAJet{bpf}".format(bpf=branchpostfix)
                HTName = "HT{bpf}".format(bpf=branchpostfix)
                if nJetName not in listOfColumns:
                    bTaggingDefineNodes[processName][sysVar].append((nJetName, "{0}[{1}].size()".format(jetPt, jetMask)))
                if HTName not in listOfColumns:
                    bTaggingDefineNodes[processName][sysVar].append((HTName, "Sum({0}[{1}])".format(jetPt, jetMask)))
                    
                #loadYields path...
                if loadYields:
                    # if useAggregate:
                    # print("\nPROBLEM: syspostfix was assumed to have only one underscore before, now it has two. Until new Yields calculated, gonna hack this away...\n\n\n")
                    # bTaggingDefineNodes[processName][sysVar].append((btagFinalWeight, "{bsf} * {lm}[\"{pn}\"][rdfslot_]->getEventYieldRatio(\"{yk}\", \"{spf}\", {nj}, {ht});".format(bsf=btagSFProduct, lm=lookupMap, pn=processName, yk=yieldsKey, spf=syspostfix, nj=nJetName, ht=HTName))) #.replace("__", "_")
                    bTaggingDefineNodes[processName][sysVar].append((btagFinalWeight, "{bsf} * {lm}[\"{pn}\"][rdfslot_]->getEventYieldRatio(\"{lk}\", {nj}, {ht});".format(bsf=btagSFProduct, lm=lookupMap, pn=processName, lk=yieldsKey+syspostfix, nj=nJetName, ht=HTName))) #.replace("__", "_")
        
                for defName, defFunc in bTaggingDefineNodes[processName][sysVar]:
                    if defName in listOfColumns:
                        if verbose:
                            print("{} already defined, skipping".format(defName))
                        continue
                    else:
                        if verbose:
                            print("nodes[processName][\"BaseNode\"] = nodes[processName][\"BaseNode\"].Define(\"{}\", \"{}\")".format(defName, defFunc))
                        nodes[processName]["BaseNode"] = nodes[processName]["BaseNode"].Define(defName, defFunc)
                        listOfColumns.push_back(defName)        
        
         #            test = nodes[processName]["BaseNode"].Define("testThis", "{lm}[\"{sn}\"][rdfslot_]->getEventYieldRatio(\"{yk}\", \"{spf}\", {nj}, {ht}, true);".format(bsf=btagSFProduct, lm=lookupMap,\
         # sn=processName, yk=yieldsKey, spf=syspostfix, nj=nJetName, ht=HTName)).Stats("testThis").GetMean()
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
                    
                    ModelBefore = ROOT.RDF.TH2DModel("{}_BTaggingYield_{}_sumW_before".format(processName, btagSFProduct.replace("btagSFProduct_","")),
                                                     "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                     len(HTArr)-1, HTArr, len(nJetArr)-1, nJetArr)
                    ModelAfter = ROOT.RDF.TH2DModel("{}_BTaggingYield_{}_sumW_after".format(processName, btagSFProduct.replace("btagSFProduct_","")),
                                                    "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                    len(HTArr)-1, HTArr, len(nJetArr)-1, nJetArr)
                    ModelBefore1DX = ROOT.RDF.TH2DModel("{}_BTaggingYield1DX_{}_sumW_before".format(processName, btagSFProduct.replace("btagSFProduct_","")),
                                                        "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                        len(HTArr)-1, HTArr, 1, nJet1Bin)
                    ModelAfter1DX = ROOT.RDF.TH2DModel("{}_BTaggingYield1DX_{}_sumW_after".format(processName, btagSFProduct.replace("btagSFProduct_","")),
                                                       "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                       len(HTArr)-1, HTArr, 1, nJet1Bin)
                    ModelBefore1DY = ROOT.RDF.TH2DModel("{}_BTaggingYield1DY_{}_sumW_before".format(processName, btagSFProduct.replace("btagSFProduct_","")),
                                                        "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                        1, HT1Bin, len(nJetArr)-1, nJetArr)
                    ModelAfter1DY = ROOT.RDF.TH2DModel("{}_BTaggingYield1DY_{}_sumW_after".format(processName, btagSFProduct.replace("btagSFProduct_","")),
                                                       "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                       1, HT1Bin, len(nJetArr)-1, nJetArr)
                    histosDict[processName][channel][k+"__sumW_before"] = nodes[processName]["BaseNode"].Histo2D(ModelBefore,
                                                                                                                 HTName,
                                                                                                                 nJetName,
                                                                                                                 calculationWeightBefore)
                    histosDict[processName][channel][k+"__sumW_after"] = nodes[processName]["BaseNode"].Histo2D(ModelAfter,
                                                                                                                HTName,
                                                                                                                nJetName,
                                                                                                                calculationWeightAfter)
                    #For Unified JetBinning calculation
                    histosDict[processName][channel][k+"__1DXsumW_before"] = nodes[processName]["BaseNode"].Histo2D(ModelBefore1DX,
                                                                                                                    HTName,
                                                                                                                    nJetName,
                                                                                                                    calculationWeightBefore)
                    histosDict[processName][channel][k+"__1DXsumW_after"] =  nodes[processName]["BaseNode"].Histo2D(ModelAfter1DX,
                                                                                                                    HTName,
                                                                                                                    nJetName,
                                                                                                                    calculationWeightAfter)
                    #For Unified HTBinning calculation
                    histosDict[processName][channel][k+"__1DYsumW_before"] = nodes[processName]["BaseNode"].Histo2D(ModelBefore1DY,
                                                                                                                    HTName,
                                                                                                                    nJetName,
                                                                                                                    calculationWeightBefore)
                    histosDict[processName][channel][k+"__1DYsumW_after"] =  nodes[processName]["BaseNode"].Histo2D(ModelAfter1DY,
                                                                                                                    HTName,
                                                                                                                    nJetName,
                                                                                                                    calculationWeightAfter)
        return input_df_or_nodes
        

def BTaggingYieldsV1(input_df, sampleName, channel="All", isData = True, histosDict=None, verbose=False,
                   loadYields=None, lookupMap="LUM", useAggregate=True, useHTOnly=False, useNJetOnly=False, 
                   calculateYields=True, HTBinWidth=10, HTMin=200, HTMax=3200, nJetBinWidth=1, nJetMin=4, nJetMax=20,
                   sysVariations={"$NOMINAL": {"jet_mask": "jet_mask",
                                               "lep_postfix": "", 
                                               "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                               "jet_pt_var": "Jet_pt",
                                               "jet_mass_var": "Jet_mass",
                                               "met_pt_var": "METFixEE2017_pt",
                                               "met_phi_var": "METFixEE2017_phi",
                                               "btagSF": "Jet_btagSF_deepcsv_shape",
                                               "weightVariation": False},
                                  "btagSF_deepcsv_shape_up_hf": {"jet_mask": "jet_mask",
                                                                  "lep_postfix": "", 
                                                                  "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                                  "jet_pt_var": "Jet_pt",
                                                                  "btagSF": "Jet_btagSF_deepcsv_shape_up_hf",
                                                                  "weightVariation": True},
                                  "btagSF_deepcsv_shape_down_lf": {"jet_mask": "jet_mask",
                                                                    "lep_postfix": "", 
                                                                    "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                                    "jet_pt_var": "Jet_pt",
                                                                    "btagSF": "Jet_btagSF_deepcsv_shape_down_lf",
                                                                    "weightVariation": True},
                                              },
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
    special replacement for nominal, and "jesTotalUp" -> "prewgt_jesTotalUp" is expected
    <HTBinWidth>, <HTMin>, <HTMax> are as expected. Don't screw up the math on your end, (max-min) should be evenly divisible.
    <nJetBinWidth>, <nJetMin>, <nJetMax> are similar

    For more info on btagging, see...
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagShapeCalibration"""
                        
    JetBins = int((nJetMax - nJetMin)/nJetBinWidth)
    HTBins = int((HTMax-HTMin)/HTBinWidth)

    if useAggregate:
        yieldsKey = "Aggregate_"
    else:
        yieldsKey = "{}_".format(sampleName) #copy it, we'll modify
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
            raise RuntimeError("lookupMap (used in BTaggingYields function) must either be a string name "                               "for the declared function's (C++ variable) name, used to find or declare one of type "                               "std::map<std::string, std::vector<TH2Lookup*>>")
        nSlots = input_df.GetNSlots()
        assert os.path.isfile(loadYields), "BTaggingYield file does not appear to exist... aborting execution"
        while iLUM[sampleName].size() < nSlots:
            if type(loadYields) == str:
                iLUM[sampleName].push_back(ROOT.TH2Lookup(loadYields))
            else:
                raise RuntimeError("No string path to a yields file has been provided in BTaggingYields() ...")
                
        #Test to see that it's accessible...
        testKeyA = yieldsKey
        testKeyB = "_nom"
        testNJ = 6
        testHT = 689.0
        testVal = iLUM[sampleName][0].getEventYieldRatio(testKeyA, testKeyB, testNJ, testHT)
        if verbose:
            print("BTaggingYield has done a test evaluation on the yield histogram with search for histogram {}{}, nJet={}, HT={} and found value {}"\
                  .format(testKeyA, testKeyB, testNJ, testHT, testVal))
        assert type(testVal) == float, "LookupMap did not provide a valid return type, something is wrong"
        assert testVal < 5.0, "LookupMap did not provide a reasonable BTagging Yield ratio in the test... (>5.0 is considered unrealistic...)"        
    
    #column guards
    listOfColumns = input_df.GetColumnNames() #This is a superset, containing non-Define'd columns as well

    if isData == True:
        return input_df
    else:
        rdf = input_df
        #List of defines to do
        z = {}
        #Create list of the variations to be histogrammed (2D yields)
        yieldList = []
        #Add key to histos dictionary, if calculating the yields
        if calculateYields and "BTaggingYields" not in histosDict.keys():
            histosDict["BTaggingYields"] = {}
        for sysVar, sysDict in sysVariations.items():
            z[sysVar] = []
            isWeightVariation = sysDict.get("weightVariation")
            branchpostfix = "__nom" if isWeightVariation else "__" + sysVar.replace("$NOMINAL", "nom") #branch postfix for 
            syspostfix = "___" + sysVar.replace("$NOMINAL", "nom")
            jetMask = sysDict.get("jet_mask") #mask as defined for the jet collection under this systematic variation
            jetPt = sysDict.get("jet_pt_var") #colum name of jet pt collection for this systematic
            jetSF = sysDict.get("btagSF") #colum name of per-jet shape SFs
            #We must get or calculate various weights, defined below
            #This btagSFProduct is the product of the SFs for the selected jets from collection jetPt with mask jetMask
            btagSFProduct = "btagSFProduct{spf}".format(spf=syspostfix)
            #input weight, should include all corrections for this systematic variation except BTagging SF and yield ratio
            calculationWeightBefore = "prewgt{spf}".format(spf=syspostfix)
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
                if calculateYields and btagSFProduct not in histosDict["BTaggingYields"].keys():
                    histosDict["BTaggingYields"][btagSFProduct] = {}
                z[sysVar].append(("{}".format(btagSFProduct), "FTA::btagEventWeight_shape({}, {})".format(jetSF, jetMask)))
            if calculationWeightAfter not in listOfColumns:
                z[sysVar].append(("{}".format(calculationWeightAfter), "{} * {}".format(calculationWeightBefore, 
                                                                                         btagSFProduct)))
                
            #Check that the HT and nJet numbers are available to us, and if not, define them based on the available masks    
            #if isScaleVariation:
            nJetName = "nFTAJet{bpf}".format(bpf=branchpostfix)
            HTName = "HT{bpf}".format(bpf=branchpostfix)
            if nJetName not in listOfColumns:
                z[sysVar].append((nJetName, "{0}[{1}].size()".format(jetPt, jetMask)))
            if HTName not in listOfColumns:
                z[sysVar].append((HTName, "Sum({0}[{1}])".format(jetPt, jetMask)))
            
            #loadYields path...
            if loadYields:
                # if useAggregate:
                print("\nPROBLEM: syspostfix was assumed to have only one underscore before, now it has two. Until new Yields calculated, gonna hack this away...\n\n\n")
                z[sysVar].append((btagFinalWeight, "{bsf} * {lm}[\"{sn}\"][rdfslot_]->getEventYieldRatio(\"{yk}\", {nj}, {ht});".format(bsf=btagSFProduct, lm=lookupMap, sn=sampleName, yk=yieldsKey + syspostfix, nj=nJetName, ht=HTName)))
                # else:
                #     z[sysVar].append((btagFinalWeight, "{bsf} * {lm}[\"{sn}\"][rdfslot_]->getEventYieldRatio(\"{yk}\", \"{vk}\", {nj}, {ht});".format(bsf=btagSFProduct, lm=lookupMap, sn=sampleName, yk=sampleName, vk=btagSFProduct.replace("nonorm_",""), nj=nJetName, ht=HTName)))

            for defName, defFunc in z[sysVar]:
                if defName in listOfColumns:
                    if verbose:
                        print("{} already defined, skipping".format(defName))
                    continue
                else:
                    if verbose:
                        print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
                    rdf = rdf.Define(defName, defFunc)
                    listOfColumns.push_back(defName)        

 #            test = rdf.Define("testThis", "{lm}[\"{sn}\"][rdfslot_]->getEventYieldRatio(\"{yk}\", \"{spf}\", {nj}, {ht}, true);".format(bsf=btagSFProduct, lm=lookupMap,\
 # sn=sampleName, yk=yieldsKey, spf=syspostfix, nj=nJetName, ht=HTName)).Stats("testThis").GetMean()
            # print("Debugging test: {}".format(test))
            #calculate Yields path
            if calculateYields:
                k = btagSFProduct
                histosDict["BTaggingYields"][k] = {}
                #Prepare working variable-bin-size 2D models (root 6.20.04+ ?)
                nJetArr = array.array('d', [4, 5, 6, 7, 8, 20])
                HTArr = array.array('d', [500, 650, 800, 1000, 1200, 10000])
                ModelBefore = ("{}_BTaggingYield_{}_sumW_before".format(sampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                                               "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                                               len(HTArr), HTArr, len(nJetArr), nJetArr)
                ModelAfter = ("{}_BTaggingYield_{}_sumW_after".format(sampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                                               "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                                               len(HTArr), HTArr, len(nJetArr), nJetArr)
                histosDict["BTaggingYields"][k]["sumW_before"] = rdf.Histo2D(("{}_BTaggingYield_{}_sumW_before".format(sampleName, btagSFProduct.replace("btagSFProduct_","")), 
                                                                               "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                                               HTBins, HTMin, HTMax,
                                                                               JetBins, nJetMin, nJetMax),
                                                                               HTName,
                                                                               nJetName,
                                                                               calculationWeightBefore)
                histosDict["BTaggingYields"][k]["sumW_after"] = rdf.Histo2D(("{}_BTaggingYield_{}_sumW_after".format(sampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                                              "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                                              HTBins, HTMin, HTMax,
                                                                              JetBins, nJetMin, nJetMax),
                                                                              HTName,
                                                                              nJetName,
                                                                              calculationWeightAfter)
                #For Unified JetBinning calculation
                histosDict["BTaggingYields"][k]["1DXsumW_before"] = rdf.Histo2D(("{}_BTaggingYield1DX_{}_sumW_before".format(sampleName, btagSFProduct.replace("btagSFProduct_","")), 
                                                                               "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                                               HTBins, HTMin, HTMax,
                                                                               1, nJetMin, nJetMax),
                                                                               HTName,
                                                                               nJetName,
                                                                               calculationWeightBefore)
                histosDict["BTaggingYields"][k]["1DXsumW_after"] = rdf.Histo2D(("{}_BTaggingYield1DX_{}_sumW_after".format(sampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                                              "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                                              HTBins, HTMin, HTMax,
                                                                              1, nJetMin, nJetMax),
                                                                              HTName,
                                                                              nJetName,
                                                                              calculationWeightAfter)
                #For Unified HTBinning calculation
                histosDict["BTaggingYields"][k]["1DYsumW_before"] = rdf.Histo2D(("{}_BTaggingYield1DY_{}_sumW_before".format(sampleName, btagSFProduct.replace("btagSFProduct_","")), 
                                                                               "BTaggingYield #Sigma#omega_{before}; HT; nJet",
                                                                               1, HTMin, HTMax,
                                                                               JetBins, nJetMin, nJetMax),
                                                                               HTName,
                                                                               nJetName,
                                                                               calculationWeightBefore)
                histosDict["BTaggingYields"][k]["1DYsumW_after"] = rdf.Histo2D(("{}_BTaggingYield1DY_{}_sumW_after".format(sampleName, btagSFProduct.replace("btagSFProduct_","")),
                                                                              "BTaggingYield #Sigma#omega_{after}; HT; nJet",
                                                                              1, HTMin, HTMax,
                                                                              JetBins, nJetMin, nJetMax),
                                                                              HTName,
                                                                              nJetName,
                                                                              calculationWeightAfter)
        return rdf


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

def splitProcess(input_df, splitProcess=None, sampleName=None, isData=True, era="2017", printInfo=False, inclusiveProcess=None, fillDiagnosticHistos=False):
    lumiDict = {"2017": 41.53,
                "2018": 59.97}
    filterNodes = dict() #For storing tuples to debug and be verbose about
    defineNodes = collections.OrderedDict() #For storing all histogram tuples --> Easier debugging when printed out, can do branch checks prior to invoking HistoND, etc...
    countNodes = dict() #For storing the counts at each node
    diagnosticNodes = dict()
    diagnosticHistos = dict()
    nodes = dict()#For storing nested dataframe nodes, THIS has filters, defines applied to it, not 'filterNodes' despite the name
    #Define the base node in nodes when we split/don't split the process

    # if splitProcess != None:
    if True: #Deprecate the alternate code path to reduce duplication, use the inclusiveProcess instead
        if isinstance(splitProcess, (dict, collections.OrderedDict)) or isinstance(inclusiveProcess, (dict, collections.OrderedDict)):
            df_with_IDs = input_df
            if isinstance(splitProcess, (dict, collections.OrderedDict)):
                splitProcs = splitProcess.get("processes")
                IDs = splitProcess.get("ID")  
            else:
                splitProcs = collections.OrderedDict()
                IDs = {}
            if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                inclusiveProc = inclusiveProcess.get("processes")
                inclusiveDict = inclusiveProc.values()[0]
                if inclusiveProc.keys()[0] not in splitProcs:
                    splitProcs.update(inclusiveProc)
                else:
                    print("Inclusive process already defined, not overriding in splitProces")
            listOfColumns = df_with_IDs.GetColumnNames()
            for IDname, IDbool in IDs.items():
                if IDbool and IDname == "unpackGenTtbarId":
                    if "unpackedGenTtbarId" not in listOfColumns:
                        df_with_IDs = df_with_IDs.Define("unpackedGenTtbarId", "FTA::unpackGenTtbarId(genTtbarId)")
                        df_with_IDs = df_with_IDs.Define("nAdditionalBJets", "unpackedGenTtbarId[0]")
                        # df_with_IDs = df_with_IDs.Define("n2BHadronJets", "unpackedGenTtbarId[1]")
                        # df_with_IDs = df_with_IDs.Define("n1BHadronJets", "unpackedGenTtbarId[2]")
                        df_with_IDs = df_with_IDs.Define("nAdditionalCJets", "unpackedGenTtbarId[3]")
                        # df_with_IDs = df_with_IDs.Define("n2CHadronJets", "unpackedGenTtbarId[4]")
                        # df_with_IDs = df_with_IDs.Define("n1CHadronJets", "unpackedGenTtbarId[5]")
                        # df_with_IDs = df_with_IDs.Define("nBJetsFromTop", "unpackedGenTtbarId[6]")
                        # df_with_IDs = df_with_IDs.Define("nBJetsFromW", "unpackedGenTtbarId[7]")
                        # df_with_IDs = df_with_IDs.Define("nCJetsFromW", "unpackedGenTtbarId[8]")
                if IDbool and IDname == "nFTAGenJet/FTAGenHT":
                    #Production notes (SL filter -> nGenJet 9)
                    # Combination of filters is applied:
                    # exactly 1 lepton (electron,muon or tau) in LHE record
                    # HT calculated from jets with pT>30 and |eta|<2.4 > 500 GeV
                    # Jet multiplicity (jet pT>30) >= 9
                    if "nFTAGenLep" not in listOfColumns:
                        df_with_IDs = df_with_IDs.Define("nFTAGenLep", "static_cast<Int_t>(LHEPart_pdgId[abs(LHEPart_pdgId)==11 || abs(LHEPart_pdgId)==13 || abs(LHEPart_pdgId)==15].size())")
                        listOfColumns.push_back("nFTAGenLep")
                    if "nFTAGenJet" not in listOfColumns:
                        df_with_IDs = df_with_IDs.Define("nFTAGenJet", "static_cast<Int_t>(GenJet_pt[GenJet_pt > 30].size())")
                        listOfColumns.push_back("nFTAGenJet")
                    if "FTAGenHT" not in listOfColumns:
                        df_with_IDs = df_with_IDs.Define("FTAGenHT", "Sum(GenJet_pt[GenJet_pt > 30 && abs(GenJet_eta) < 2.4])")
                        listOfColumns.push_back("FTAGenHT")
                if IDbool and IDname == "subera":
                    raise NotImplementedError("splitProcess 'subera' not yet implemented")
            nodes["BaseNode"] = df_with_IDs #Always store the base node we'll build upon in the next level
            for preProcessName, processDict in splitProcs.items():
                processName = era + "___" + preProcessName
                filterString = processDict.get("filter")
                filterName = "{} :: {}".format(processName, filterString.replace(" && ", " and ").replace(" || ", " or ")\
                                               .replace("&&", " and ").replace("||", " or "))
                if not isData:
                    #Make the fractional contribution equal to N_eff(sample_j) / Sum(N_eff(sample_i)), where N_eff = nEventsPositive - nEventsNegative
                    #Need to gather those bookkeeping stats from the original source rather than the ones after event selection
                    effectiveXS = processDict.get("effectiveCrossSection")
                    sumWeights = processDict.get("sumWeights")
                    # nEffective = processDict.get("nEventsPositive") - processDict.get("nEventsNegative")
                    fractionalContribution = processDict.get("fractionalContribution")
                    #Calculate XS * Lumi
                    wgtFormula = "{eXS:f} * {lumi:f} * 1000 * genWeight * {frCon:f} / {sW:f}".format(eXS=effectiveXS,
                                                                                                     lumi=lumiDict[era],
                                                                                                     frCon=fractionalContribution,
                                                                                                     sW=sumWeights
                                                                                                 )
                    if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                        formulaForNominalXS = "{nXS:f} * genWeight / {sW:f}".format(nXS=inclusiveDict.get("effectiveCrossSection"),
                                                                                    sW=inclusiveDict.get("sumWeights")
                        )
                        print("{} - nominalXS - {}".format(processName, formulaForNominalXS))
                        formulaForEffectiveXS = "{nXS:f} * genWeight * {frCon:f} / {sW:f}".format(nXS=effectiveXS,
                                                                                      frCon=fractionalContribution,
                                                                                      sW=sumWeights
                        )
                        print("{} - effectiveXS - {}".format(processName, formulaForEffectiveXS))
                    if fillDiagnosticHistos == True:
                        diagnostic_e_mask = "Electron_pt > 15 && Electron_cutBased >= 2 && ((abs(Electron_eta) < 1.4442 && abs(Electron_ip3d) < 0.05 && abs(Electron_dz) < 0.1) || (abs(Electron_eta) > 1.5660 && abs(Electron_eta) < 2.5 && abs(Electron_ip3d) < 0.10 && abs(Electron_dz) < 0.2))"
                        diagnostic_mu_mask = "Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_looseId == true && Muon_pfIsoId >= 4 && abs(Muon_ip3d) < 0.10 && abs(Muon_dz) < 0.02"
                        diagnostic_lepjet_idx = "Concatenate(Muon_jetIdx[diagnostic_mu_mask], Electron_jetIdx[diagnostic_e_mask])"
                        diagnostic_jet_idx = "FTA::generateIndices(Jet_pt)"
                        diagnostic_jet_mask = "ROOT::VecOps::RVec<int> jmask = (Jet_pt > 30 && abs(Jet_eta) < 2.5 && Jet_jetId > 2); "\
                                              "for(int i=0; i < diagnostic_lepjet_idx.size(); ++i){jmask = jmask && diagnostic_jet_idx != diagnostic_lepjet_idx.at(i);}"\
                                              "return jmask;"
                if processName not in nodes:
                    #L-2 filter, should be the packedEventID filter in that case
                    filterNodes[processName] = dict()
                    filterNodes[processName]["BaseNode"] = (filterString, filterName, processName, None, None, None, None)
                    nodes[processName] = dict()
                    if not isData:
                        nodes[processName]["BaseNode"] = nodes["BaseNode"]\
                            .Filter(filterNodes[processName]["BaseNode"][0], filterNodes[processName]["BaseNode"][1])\
                            .Define("pwgt___LumiXS", wgtFormula)
                        if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                            nodes[processName]["BaseNode"] = nodes[processName]["BaseNode"]\
                                .Define("nominalXS", formulaForNominalXS)\
                                .Define("nominalXS2", "pow(nominalXS, 2)")\
                                .Define("effectiveXS", formulaForEffectiveXS)\
                                .Define("effectiveXS2", "pow(effectiveXS, 2)")
                        if fillDiagnosticHistos == True:
                            nodes[processName]["BaseNode"] = nodes[processName]["BaseNode"]\
                                .Define("diagnostic_e_mask", diagnostic_e_mask)\
                                .Define("diagnostic_mu_mask", diagnostic_mu_mask)\
                                .Define("diagnostic_lepjet_idx", diagnostic_lepjet_idx)\
                                .Define("diagnostic_jet_idx", diagnostic_jet_idx)\
                                .Define("diagnostic_jet_mask", diagnostic_jet_mask)\
                                .Define("diagnostic_HT", "Sum(Jet_pt[diagnostic_jet_mask])")\
                                .Define("diagnostic_nJet", "Jet_pt[diagnostic_jet_mask].size()")\
                                .Define("diagnostic_jet1_pt", "Sum(diagnostic_jet_mask) > 0 ? Jet_pt[diagnostic_jet_mask].at(0) : -0.01")\
                                .Define("diagnostic_jet1_eta", "Sum(diagnostic_jet_mask) > 0 ? Jet_eta[diagnostic_jet_mask].at(0) : 9999.9")\
                                .Define("diagnostic_jet5_pt", "Sum(diagnostic_jet_mask) > 4 ? Jet_pt[diagnostic_jet_mask].at(4) : -0.01")\
                                .Define("diagnostic_jet5_eta", "Sum(diagnostic_jet_mask) > 4 ? Jet_eta[diagnostic_jet_mask].at(4) : 9999.9")\
                                .Define("diagnostic_el_pt", "Electron_pt[diagnostic_e_mask]")\
                                .Define("diagnostic_el_eta", "Electron_eta[diagnostic_e_mask]")\
                                .Define("diagnostic_mu_pt", "Muon_pt[diagnostic_mu_mask]")\
                                .Define("diagnostic_mu_eta", "Muon_eta[diagnostic_mu_mask]")
                            


                    else:
                        nodes[processName]["BaseNode"] = nodes["BaseNode"]\
                            .Filter(filterNodes[processName]["BaseNode"][0], filterNodes[processName]["BaseNode"][1])
                    countNodes[processName] = dict()
                    countNodes[processName]["BaseNode"] = nodes[processName]["BaseNode"].Count()
                    diagnosticNodes[processName] = collections.OrderedDict()
                    diagnosticHistos[processName] = collections.OrderedDict()
                    defineNodes[processName] = collections.OrderedDict()
                if not isData:
                    #Need to gather those bookkeeping stats from the original source rather than the ones after event selection...
                    diagnosticNodes[processName]["sumWeights::Sum"] = nodes[processName]["BaseNode"].Sum("genWeight")
                    diagnosticNodes[processName]["sumWeights2::Sum"] = nodes[processName]["BaseNode"].Define("genWeight2", "pow(genWeight, 2)").Sum("genWeight2")
                    if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                        diagnosticNodes[processName]["nominalXS::Sum"] = nodes[processName]["BaseNode"].Sum("nominalXS")
                        diagnosticNodes[processName]["nominalXS2::Sum"] = nodes[processName]["BaseNode"].Sum("nominalXS2")
                    # pdb.set_trace()
                    diagnosticNodes[processName]["effectiveXS::Sum"] = nodes[processName]["BaseNode"].Sum("effectiveXS")
                    diagnosticNodes[processName]["effectiveXS2::Sum"] = nodes[processName]["BaseNode"].Sum("effectiveXS2")
                    diagnosticNodes[processName]["nEventsPositive::Count"] = nodes[processName]["BaseNode"].Filter("genWeight >= 0", "genWeight >= 0").Count()
                    diagnosticNodes[processName]["nEventsNegative::Count"] = nodes[processName]["BaseNode"].Filter("genWeight < 0", "genWeight < 0").Count()
                if "nFTAGenJet/FTAGenHT" in IDs:
                    if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                        diagnosticNodes[processName]["nLep2nJet7GenHT500-550-nominalXS::Sum"] = nodes[processName]["BaseNode"]\
                            .Filter("nFTAGenLep == 2 && nFTAGenJet == 7 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 2, nFTAGenJet 7, FTAGenHT 500-550").Sum("nominalXS")
                        diagnosticNodes[processName]["nLep2nJet7pGenHT500p-nominalXS::Sum"] = nodes[processName]["BaseNode"]\
                            .Filter("nFTAGenLep == 2 && nFTAGenJet >= 7 && 500 <= FTAGenHT", "nFTAGenLep 2, nFTAGenJet 7+, FTAGenHT 500+").Sum("nominalXS")
                        diagnosticNodes[processName]["nLep1nJet9GenHT500-550-nominalXS::Sum"] = nodes[processName]["BaseNode"]\
                            .Filter("nFTAGenLep == 1 && nFTAGenJet == 9 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 1, nFTAGenJet 9, FTAGenHT 500-550").Sum("nominalXS")
                        diagnosticNodes[processName]["nLep1nJet9pGenHT500p-nominalXS::Sum"] = nodes[processName]["BaseNode"]\
                            .Filter("nFTAGenLep == 1 && nFTAGenJet >= 9 && 500 <= FTAGenHT", "nFTAGenLep 1, nFTAGenJet 9+, FTAGenHT 500+").Sum("nominalXS")
                    if fillDiagnosticHistos == True:
                        diagnosticHistos[processName]["NoChannel"] = collections.OrderedDict()
                        diagnosticHistos[processName]["NoChannel"]["GenHT-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___GenHT".format(proc=processName), 
                                      "GenHT;GenHT;#sigma/GeV", 200, 0, 2000), "FTAGenHT", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["GenHT-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___GenHT".format(proc=processName), 
                                      "GenHT;GenHT;#sigma/GeV", 200, 0, 2000), "FTAGenHT", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["nGenJet-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___nGenJet".format(proc=processName), 
                                      "nGenJet;nGenJet;#sigma/nGenJet", 20, 0, 20), "nFTAGenJet", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["nGenJet-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___nGenJet".format(proc=processName), 
                                      "nGenJet;nGenJet;#sigma/nGenJet", 20, 0, 20), "nFTAGenJet", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["nGenLep-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___nGenLep".format(proc=processName), 
                                      "nGenLep;nGenLep;#sigma/nGenLep", 5, 0, 5), "nFTAGenLep", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["nGenLep-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___nGenLep".format(proc=processName), 
                                      "nGenLep;nGenLep;#sigma/nGenLep", 5, 0, 5), "nFTAGenLep", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["HT-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___HT".format(proc=processName), 
                                      "HT;HT;#sigma/GeV", 200, 0, 2000), "diagnostic_HT", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["HT-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___HT".format(proc=processName), 
                                      "HT;HT;#sigma/GeV", 200, 0, 2000), "diagnostic_HT", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["nJet-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___nJet".format(proc=processName), 
                                      "nJet;nJet;#sigma/nJet", 20, 0, 20), "diagnostic_nJet", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["nJet-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___nJet".format(proc=processName), 
                                      "nJet;nJet;#sigma/nJet", 20, 0, 20), "diagnostic_nJet", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["jet1_pt-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet1_pt".format(proc=processName), 
                                      "Leading Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet1_pt", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["jet1_pt-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet1_pt".format(proc=processName), 
                                      "Leading Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet1_pt", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["jet1_eta-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet1_eta".format(proc=processName), 
                                      "Leading Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet1_eta", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["jet1_eta-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet1_eta".format(proc=processName), 
                                      "Leading Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet1_eta", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["jet5_pt-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet5_pt".format(proc=processName), 
                                      "Fifth Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet5_pt", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["jet5_pt-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet5_pt".format(proc=processName), 
                                      "Fifth Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet5_pt", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["jet5_eta-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet5_eta".format(proc=processName), 
                                      "Fift Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet5_eta", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["jet5_eta-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet5_eta".format(proc=processName), 
                                      "Fift Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet5_eta", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["el_pt-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___el_pt".format(proc=processName), 
                                      "e p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_el_pt", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["el_pt-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___el_pt".format(proc=processName), 
                                      "e p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_el_pt", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["el_eta-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___el_eta".format(proc=processName), 
                                      "e #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_el_eta", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["el_eta-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___el_eta".format(proc=processName), 
                                      "e #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_el_eta", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["mu_pt-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___mu_pt".format(proc=processName), 
                                      "#mu p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_mu_pt", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["mu_pt-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___mu_pt".format(proc=processName), 
                                      "#mu p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_mu_pt", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["mu_eta-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___mu_eta".format(proc=processName), 
                                      "#mu #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_mu_eta", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["mu_eta-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___mu_eta".format(proc=processName), 
                                      "#mu #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_mu_eta", "effectiveXS")

                    diagnosticNodes[processName]["nLep2nJet7GenHT500-550-effectiveXS::Sum"] = nodes[processName]["BaseNode"]\
                        .Filter("nFTAGenLep == 2 && nFTAGenJet == 7 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 2, nFTAGenJet 7, FTAGenHT 500-550").Sum("effectiveXS")
                    diagnosticNodes[processName]["nLep2nJet7pGenHT500p-effectiveXS::Sum"] = nodes[processName]["BaseNode"]\
                        .Filter("nFTAGenLep == 2 && nFTAGenJet >= 7 && 500 <= FTAGenHT", "nFTAGenLep 2, nFTAGenJet 7+, FTAGenHT 500+").Sum("effectiveXS")
                    diagnosticNodes[processName]["nLep1nJet9GenHT500-550-effectiveXS::Sum"] = nodes[processName]["BaseNode"]\
                        .Filter("nFTAGenLep == 1 && nFTAGenJet == 9 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 1, nFTAGenJet 9, FTAGenHT 500-550").Sum("effectiveXS")
                    diagnosticNodes[processName]["nLep1nJet9pGenHT500p-effectiveXS::Sum"] = nodes[processName]["BaseNode"]\
                        .Filter("nFTAGenLep == 1 && nFTAGenJet >= 9 && 500 <= FTAGenHT", "nFTAGenLep 1, nFTAGenJet 9+, FTAGenHT 500+").Sum("effectiveXS")
            if printInfo == True:
                print("splitProcess(..., printInfo=True, ...) set, executing the event loop to gather and print diagnostic info (presumably from the non-event-selected source...")
                for pName, pDict in diagnosticNodes.items():
                    print("processName == {}".format(pName))
                    for dName, dNode in pDict.items():
                        parseDName = dName.split("::")
                        if parseDName[1] in ["Count", "Sum"]:
                            dString = "\t\t\"{}\": {},".format(parseDName[0], dNode.GetValue())
                        elif parseDName[1] in ["Stats"]:
                            thisStat = dNode.GetValue()
                            dString = "\t\t\"{}::Min\": {}".format(parseDName[0], thisStat.GetMin())
                            dString += "\n\t\t\"{}::Mean\": {}".format(parseDName[0], thisStat.GetMean())
                            dString += "\n\t\t\"{}::Max\": {}".format(parseDName[0], thisStat.GetMax())
                        elif parseDName[1] in ["Histo"]:
                            dString = "\t\tNo method implemented for histograms, yet"
                        else:
                            dString = "\tDiagnostic node type not recognized: {}".format(parseDName[1])
                        print(dString)
        else:
            raise RuntimeError("Invalid type passed for splitProcess. Require a dictionary containing keys 'ID' and 'processes' to split the sample.")
        
    else:
        raise RuntimeError("Deprecated, form an inclusive process and configure splitProcess with it.")
        # processName = era + "___" + sampleName #Easy case without on-the-fly ttbb, ttcc, etc. categorization
        # nodes["BaseNode"] = input_df #Always store the base node we'll build upon in the next level
        # #The below references branchpostfix since we only need nodes for these types of scale variations...
        # if processName not in nodes:
        #     #L-2 filter, should be the packedEventID filter in that case
        #     filterNodes[processName] = dict()
        #     filterNodes[processName]["BaseNode"] = ("return true;", "{}".format(processName), processName, None, None, None, None)
        #     nodes[processName] = dict()
        #     nodes[processName]["BaseNode"] = nodes["BaseNode"].Filter(filterNodes[processName]["BaseNode"][0], filterNodes[processName]["BaseNode"][1])
        #     countNodes[processName] = collections.OrderedDict()
        #     countNodes[processName]["BaseNode"] = nodes[processName]["BaseNode"].Count()
        #     diagnosticNodes[processName] = collections.OrderedDict()
        #     defineNodes[processName] = collections.OrderedDict()
        #     if not isData:
        #         #Need to gather those bookkeeping stats from the original source rather than the ones after event selection...
        #         diagnosticNodes[processName]["sumWeights::Sum"] = nodes[processName]["BaseNode"].Sum("genWeight")
        #         diagnosticNodes[processName]["nEventsPositive::Count"] = nodes[processName]["BaseNode"].Filter("genWeight >= 0", "genWeight >= 0").Count()
        #         diagnosticNodes[processName]["nEventsNegative::Count"] = nodes[processName]["BaseNode"].Filter("genWeight < 0", "genWeight < 0").Count()
        #     if printInfo == True:
        #         print("splitProcess(..., printInfo=True, ...) set, executing the event loop to gather and print diagnostic info (presumably from the non-event-selected source...")
        #         for pName, pDict in diagnosticNodes.items():
        #             print("processName == {}".format(pName))
        #             for dName, dNode in pDict.items():
        #                 parseDName = dName.split("::")
        #                 if parseDName[1] in ["Count", "Sum"]:
        #                     dString = "\t\t\"{}\": {},".format(parseDName[0], dNode.GetValue())
        #                 elif parseDName[1] in ["Stats"]:
        #                     thisStat = dNode.GetValue()
        #                     dString = "\t\t\"{}::Min\": {}".format(parseDName[0], thisStat.GetMin())
        #                     dString += "\n\t\t\"{}::Mean\": {}".format(parseDName[0], thisStat.GetMean())
        #                     dString += "\n\t\t\"{}::Max\": {}".format(parseDName[0], thisStat.GetMax())
        #                 elif parseDName[1] in ["Histo"]:
        #                     dString = "\t\tNo method implemented for histograms, yet"
        #                 else:
        #                     dString = "\tDiagnostic node type not recognized: {}".format(parseDName[1])
        #                 print(dString)
            
    prePackedNodes = dict()
    prePackedNodes["filterNodes"] = filterNodes
    prePackedNodes["nodes"] = nodes
    prePackedNodes["countNodes"] = countNodes
    prePackedNodes["diagnosticNodes"] = diagnosticNodes
    prePackedNodes["diagnosticHistos"] = diagnosticHistos
    prePackedNodes["defineNodes"] = defineNodes
    return prePackedNodes


def fillHistos(input_df_or_nodes, splitProcess=False, sampleName=None, channel="All", isData=True, era="2017", histosDict=None,
               doCategorized=False, doDiagnostics=True, debugInfo=True, nJetsToHisto=10, bTagger="DeepCSV",
               HTCut=500, ZMassMETWindow=[15.0, 0.0], verbose=False,
               triggers=[],
               sysVariations={"$NOMINAL": {"jet_mask": "jet_mask",
                                           "lep_postfix": "",
                                           "wgt_final": "wgt__nom",
                                           "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                           "jet_pt_var": "Jet_pt",
                                           "jet_mass_var": "Jet_mass",
                                           "met_pt_var": "METFixEE2017_pt",
                                           "met_phi_var": "METFixEE2017_phi",
                                           "btagSF": "Jet_btagSF_deepcsv_shape",
                                           "weightVariation": False},
                              "jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp",
                                              "lep_postfix": "",
                                              "wgt_final": "wgt__jesTotalUp",
                                              "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                              "jet_pt_var": "Jet_pt_jesTotalUp",
                                              "jet_mass_var": "Jet_mass_jesTotalUp",
                                              "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                              "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                              "btagSF": "Jet_btagSF_deepcsv_shape",
                                              "weightVariation": False},
                              "btagSF_deepcsv_shape_down_hf": {"jet_mask": "jet_mask",
                                                                "lep_postfix": "", 
                                                                "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                                "jet_pt_var": "Jet_pt",
                                                                "btagSF": "Jet_btagSF_deepcsv_shape_down_hf",
                                                                "weightVariation": True},
                              "no_LSF": {"jet_mask": "jet_mask",
                                          "lep_postfix": "", 
                                          "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                          "jet_pt_var": "Jet_pt",
                                          "btagSF": "Jet_btagSF_deepcsv_shape",
                                          "weightVariation": True},
                                     },
):
    """Method to fill histograms given an input RDataFrame, input sample/dataset name, input histogram dictionaries.
    Has several options of which histograms to fill, such as Leptons, Jets, Weights, EventVars, etc.
    Types of histograms (1D, 2D, those which will not be stacked(NS - histosNS)) are filled by passing non-None
    value to that histosXX_dict variable. Internally stored with structure separating the categories of histos,
    with 'Muons,' 'Electrons,' 'Leptons,' 'Jets,' 'EventVars,' 'Weights' subcategories.
    
    ZMassMETWindow = [<invariant mass halfwidth>, <METCut>] - If in the same-flavor dilepton channel, require 
    abs(DileptonInvMass - ZMass) < ZWindowHalfWidth and MET >= METCut
    """
    

    if doCategorized == False and doDiagnostics == False:
        raise RuntimeError("Must select something to plot: Set do{Categorized, Diagnostics, etc} = True in init method")

    if splitProcess:
        print("Using packedEventID to categorize events into (sub)sample names and channel")
    elif sampleName != None and channel != None:
        print("Using input sampleName and channel to categorize events in histograms dictionary: {} - {}".format(sampleName, channel))
    else:
        raise RuntimeError("fillHistos() must be configured with the sampleName and channel or to deduce these internally based upon packedEventID (higher precedence)")

    if bTagger.lower() == "deepcsv":
        tagger = "CSV"
    elif bTagger.lower() == "deepjet":
        tagger = "Jet"
    elif bTagger.lower() == "csvv2":
        raise RuntimeError("CSVv2 is not a supported bTagger option in fillHistos() right now")
    else:
        raise RuntimeError("{} is not a supported bTagger option in fillHistos()".format(bTagger))

    #Define blinded regions here, each sublist with multiple elements must have matches for BOTH to mark the category as blinded
    blindings = [["nMediumDeep{tag}B2".format(tag=tagger), "nJet7"],
                 ["nMediumDeep{tag}B2".format(tag=tagger), "nJet8+"],
                 ["nMediumDeep{tag}B3".format(tag=tagger), "nJet4"],
                 ["nMediumDeep{tag}B3".format(tag=tagger), "nJet5"],
                 ["nMediumDeep{tag}B3".format(tag=tagger), "nJet6"],
                 ["nMediumDeep{tag}B3".format(tag=tagger), "nJet7"],
                 ["nMediumDeep{tag}B3".format(tag=tagger), "nJet8+"],
                 ["nMediumDeep{tag}B4+".format(tag=tagger), "nJet4"],
                 ["nMediumDeep{tag}B4+".format(tag=tagger), "nJet5"],
                 ["nMediumDeep{tag}B4+".format(tag=tagger), "nJet6"],
                 ["nMediumDeep{tag}B4+".format(tag=tagger), "nJet7"],
                 ["nMediumDeep{tag}B4+".format(tag=tagger), "nJet8+"],
                 ["nJet7"],
                 ["nJet8+"],
                 ["nMediumDeep{tag}B3".format(tag=tagger)],
                 ["nMediumDeep{tag}B4+".format(tag=tagger)],
             ]

    pi = ROOT.TMath.Pi()
    #Get the list of defined columns for checks
    histoNodes = histosDict #Inherit this from initiliazation, this is where the histograms will actually be stored
    if isinstance(input_df_or_nodes, (dict, collections.OrderedDict)):
        filterNodes = input_df_or_nodes.get("filterNodes")
        nodes = input_df_or_nodes.get("nodes")
        defineNodes = input_df_or_nodes.get("defineNodes")
        diagnosticNodes = input_df_or_nodes.get("diagnosticNodes")
        countNodes = input_df_or_nodes.get("countNodes")
    else:
        filterNodes = collections.OrderedDict()
        nodes = collections.OrderedDict()
        defineNodes = collections.OrderedDict()
        diagnosticNodes = collections.OrderedDict()
        countNodes = collections.OrderedDict()
        processName = era + "___" + sampleName #Easy case without on-the-fly ttbb, ttcc, etc. categorization
        nodes["BaseNode"] = input_df_or_nodes #Always store the base node we'll build upon in the next level
        #The below references branchpostfix since we only need nodes for these types of scale variations...
        if processName not in nodes:
            #L-2 filter, should be the packedEventID filter in that case
            filterNodes[processName] = collections.OrderedDict()
            filterNodes[processName]["BaseNode"] = ("return true;", "{}".format(processName), processName, None, None, None, None)
            nodes[processName] = collections.OrderedDict()
            nodes[processName]["BaseNode"] = nodes["BaseNode"].Filter(filterNodes[processName]["BaseNode"][0], filterNodes[processName]["BaseNode"][1])
            countNodes[processName] = collections.OrderedDict()
            countNodes[processName]["BaseNode"] = nodes[processName]["BaseNode"].Count()
            diagnosticNodes[processName] = collections.OrderedDict()
            defineNodes[processName] = collections.OrderedDict()


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
        syspostfix = "___nom" if sysVar == "$NOMINAL" else "___{}".format(sysVar)
        #name branches for filling with the nominal postfix if weight variations, and systematic postfix if scale variation (jes_up, etc.)
        branchpostfix = None
        if isWeightVariation:
            branchpostfix = "__nom"
        else:
            branchpostfix = "__" + sysVar.replace("$NOMINAL", "nom")
        leppostfix = sysDict.get("lep_postfix", "") #No variation on this yet, but just in case
        
        fillJet = "FTAJet{bpf}".format(bpf=branchpostfix)
        fillJet_pt = "FTAJet{bpf}_pt".format(bpf=branchpostfix)
        fillJet_phi = "FTAJet{bpf}_phi".format(bpf=branchpostfix)
        fillJet_eta = "FTAJet{bpf}_eta".format(bpf=branchpostfix)
        fillJet_mass = "FTAJet{bpf}_mass".format(bpf=branchpostfix)
        fillMET_pt = "FTAMET{bpf}_pt".format(bpf=branchpostfix)
        fillMET_phi = "FTAMET{bpf}_phi".format(bpf=branchpostfix)
        fillMET_uncorr_pt = sysDict.get("met_pt_var", "MET_pt")
        fillMET_uncorr_phi = sysDict.get("met_phi_var", "MET_phi")

        if verbose:
            print("Systematic: {spf} - Branch: {bpf} - Jets: {fj}=({fjp}, {fji}, {fje}, {fjm}) - MET: ({mpt}, {mph})".format(spf=syspostfix,
                                                                                                                             bpf=branchpostfix,
                                                                                                                             fj=fillJet,
                                                                                                                             fjp=fillJet_pt,
                                                                                                                             fji=fillJet_phi,
                                                                                                                             fje=fillJet_eta,
                                                                                                                             fjm=fillJet_mass,
                                                                                                                             mpt=fillMET_pt,
                                                                                                                             mph=fillMET_phi)
              )
        
        #We need to create filters that depend on scale variations like jesUp/Down, i.e. HT and Jet Pt can and will change
        #Usually weight variations will be based upon the _nom (nominal) calculations/filters,
        #Scale variations will usually have a special branch defined. Exeption is sample-based variations like ttbar hdamp, where the nominal branch is used for calculations
        #but even there, the inputs should be tailored to point to 'nominal' jet pt
        if not isWeightVariation:
            #cycle through processes here, should we have many packed together in the sample (ttJets -> lepton decay channel, heavy flavor, light flavor, etc.
            for processName in nodes:
                if processName.lower() == "basenode": continue
                if processName not in histoNodes:
                    histoNodes[processName] = dict()
                listOfColumns = nodes[processName]["BaseNode"].GetColumnNames()

                #Get the appropriate weight defined in defineFinalWeights function
                # wgtVar = sysDict.get("wgt_final", "wgt__nom")
                wgtVar = "wgt{spf}".format(spf=syspostfix)
                if verbose:
                    print("\tFor systematic variation {}, weight branch is {}".format(syspostfix.replace("___", ""), wgtVar))
                if wgtVar not in listOfColumns:
                    print("{} not found as a valid weight variation, no backup solution implemented".format(wgtVar))
                    raise RuntimeError("Couldn't find a valid fallback weight variation in fillHistos()")
                print("{} chosen as the weight for {} variation".format(wgtVar, syspostfix.replace("___", "")))



                #potentially add other channels here, like "IsoMuNonisoEl", etc. for QCD studies, or lpf-dependency
                #NOTE: we append an extra underscore (postfixes should always have 1 to begin with) to enable use of split("__") to re-deduce postfix outside this 
                #deeply nested loop
                for decayChannel in ["ElMu{lpf}".format(lpf=leppostfix), 
                                     "MuMu{lpf}".format(lpf=leppostfix),
                                     "ElEl{lpf}".format(lpf=leppostfix),
                                     "ElEl_LowMET{lpf}".format(lpf=leppostfix),
                                     "ElEl_HighMET{lpf}".format(lpf=leppostfix),
                                     ]:
                    testInputChannel = channel.lower().replace("_baseline", "").replace("_selection", "")
                    testLoopChannel = decayChannel.lower().replace("{lpf}".format(lpf=leppostfix), "").replace("_baseline", "").replace("_selection", "")
                    if testInputChannel == "all": 
                        pass
                    elif testInputChannel != testLoopChannel: 
                        print("Skipping channel {chan} in process {proc} for systematic {spf}".format(chan=decayChannel, proc=processName, spf=syspostfix.replace("___", "")))
                        continue
                    #Regarding keys: we'll insert the systematic when we insert all th L0 X L1 X L2 keys in the dictionaries, not here in the L($N) keys
                    # print("Filtering events with ST >= 500, and removing HT cut!")
                    if decayChannel == "ElMu{lpf}".format(lpf=leppostfix):
                        channelFilter = "nFTALepton{lpf} == 2 && nFTAMuon{lpf} == 1 && nFTAElectron{lpf}== 1".format(lpf=leppostfix)
                        channelFiltName = "1 el, 1 mu ({lpf})".format(lpf=leppostfix)
                        L0String = "HT{bpf} >= {htc}".format(bpf=branchpostfix, htc=HTCut)
                        L0Name = "HT{bpf} >= {htc}"\
                            .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        L0Key = "ZWindowMET{metcut}Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), metcut=str(0).replace(".", "p"), 
                                                                                 zwidth=0)
                        # L0String = "ST{bpf} >= {htc}".format(bpf=branchpostfix, htc=HTCut)
                        # L0Name = "ST{bpf} >= {htc}"\
                        #     .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        # L0Key = "ZWindowMET{metcut}Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), metcut=str(0).replace(".", "p"), 
                        #                                                          zwidth=0)
                    elif decayChannel == "MuMu{lpf}".format(lpf=leppostfix):
                        channelFilter = "nFTALepton{lpf} == 2 && nFTAMuon{lpf} == 2".format(lpf=leppostfix)
                        channelFiltName = "2 mu ({lpf})".format(lpf=leppostfix)
                        L0String = "HT{bpf} >= {htc} && {met} >= {metcut} && FTAMuon{lpf}_InvariantMass > 20 && abs(FTAMuon{lpf}_InvariantMass - 91.2) > {zwidth}"\
                            .format(lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0], bpf=branchpostfix, htc=HTCut)
                        L0Name = "HT{bpf} >= {htc}, {met} >= {metcut}, Di-Muon Resonance > 20GeV and outside {zwidth}GeV Z Window"\
                            .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        L0Key = "ZWindowMET{metcut}Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), 
                                                                                 metcut=str(ZMassMETWindow[1]).replace(".", "p"), 
                                                                                 zwidth=str(ZMassMETWindow[0]).replace(".", "p"))
                        # L0String = "ST{bpf} >= {htc} && {met} >= {metcut} && FTAMuon{lpf}_InvariantMass > 20 && abs(FTAMuon{lpf}_InvariantMass - 91.2) > {zwidth}"\
                        #     .format(lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0], bpf=branchpostfix, htc=HTCut)
                        # L0Name = "ST{bpf} >= {htc}, {met} >= {metcut}, Di-Muon Resonance > 20GeV and outside {zwidth}GeV Z Window"\
                        #     .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        # L0Key = "ZWindowMET{metcut}Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), 
                        #                                                          metcut=str(ZMassMETWindow[1]).replace(".", "p"), 
                        #                                                          zwidth=str(ZMassMETWindow[0]).replace(".", "p"))
                    elif decayChannel == "ElEl{lpf}".format(lpf=leppostfix):
                        channelFilter = "nFTALepton{lpf} == 2 && nFTAElectron{lpf}== 2".format(lpf=leppostfix)
                        channelFiltName = "2 el ({lpf})".format(lpf=leppostfix)
                        L0String = "HT{bpf} >= {htc} && {met} >= {metcut} && FTAElectron{lpf}_InvariantMass > 20 && abs(FTAElectron{lpf}_InvariantMass - 91.2) > {zwidth}"\
                            .format(lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0], bpf=branchpostfix, htc=HTCut)
                        L0Name = "HT{bpf} >= {htc}, {met} >= {metcut}, Di-Electron Resonance > 20GeV and outside {zwidth}GeV Z Window"\
                            .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        L0Key = "ZWindowMET{metcut}Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), 
                                                                                 metcut=str(ZMassMETWindow[1]).replace(".", "p"), 
                                                                                 zwidth=str(ZMassMETWindow[0]).replace(".", "p"))
                        # L0String = "ST{bpf} >= {htc} && {met} >= {metcut} && FTAElectron{lpf}_InvariantMass > 20 && abs(FTAElectron{lpf}_InvariantMass - 91.2) > {zwidth}"\
                        #     .format(lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0], bpf=branchpostfix, htc=HTCut)
                        # L0Name = "ST{bpf} >= {htc}, {met} >= {metcut}, Di-Electron Resonance > 20GeV and outside {zwidth}GeV Z Window"\
                        #     .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        # L0Key = "ZWindowMET{metcut}Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), 
                        #                                                          metcut=str(ZMassMETWindow[1]).replace(".", "p"), 
                        #                                                          zwidth=str(ZMassMETWindow[0]).replace(".", "p"))
                    elif decayChannel == "ElEl_LowMET{lpf}".format(lpf=leppostfix):
                        channelFilter = "nFTALepton{lpf} == 2 && nFTAElectron{lpf}== 2".format(lpf=leppostfix)
                        channelFiltName = "2 el, Low MET ({lpf})".format(lpf=leppostfix)
                        L0String = "HT{bpf} >= {htc} && {met} < 50 && FTAElectron{lpf}_InvariantMass > 20 && abs(FTAElectron{lpf}_InvariantMass - 91.2) > {zwidth}"\
                            .format(lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0], bpf=branchpostfix, htc=HTCut)
                        L0Name = "HT{bpf} >= {htc}, {met} < 50, Di-Electron Resonance > 20GeV and outside {zwidth}GeV Z Window"\
                            .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        L0Key = "ZWindowMET0to50Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), 
                                                                                 metcut=str(ZMassMETWindow[1]).replace(".", "p"), 
                                                                                 zwidth=str(ZMassMETWindow[0]).replace(".", "p"))
                    elif decayChannel == "ElEl_HighMET{lpf}".format(lpf=leppostfix):
                        channelFilter = "nFTALepton{lpf} == 2 && nFTAElectron{lpf}== 2".format(lpf=leppostfix)
                        channelFiltName = "2 el, High MET ({lpf})".format(lpf=leppostfix)
                        L0String = "HT{bpf} >= {htc} && {met} >= 50 && FTAElectron{lpf}_InvariantMass > 20 && abs(FTAElectron{lpf}_InvariantMass - 91.2) > {zwidth}"\
                            .format(lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0], bpf=branchpostfix, htc=HTCut)
                        L0Name = "HT{bpf} >= {htc}, {met} >= 50, Di-Electron Resonance > 20GeV and outside {zwidth}GeV Z Window"\
                            .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        L0Key = "ZWindowMET50Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), 
                                                                                 metcut=str(ZMassMETWindow[1]).replace(".", "p"), 
                                                                                 zwidth=str(ZMassMETWindow[0]).replace(".", "p"))
                    else:
                        raise NotImplementedError("No definition for decayChannel = {} yet".format(decayChannel))
                    #filter define, filter name, process, channel, L0 (HT/ZWindow <cross> SCALE variations), L1 (nBTags), L2 (nJet)
                    #This is the layer -1 key, insert and proceed to layer 0
                    if decayChannel not in nodes[processName]: 
                        #protect against overwriting, as these nodes will be shared amongst non-weight variations!
                        #There will be only one basenode per decay channel
                        # filterNodes[processName][decayChannel] = collections.OrderedDict()
                        filterNodes[processName][decayChannel] = collections.OrderedDict()
                        filterNodes[processName][decayChannel]["BaseNode"] = (channelFilter, channelFiltName, processName, decayChannel, None, None, None) #L-1 filter
                        print(filterNodes[processName][decayChannel]["BaseNode"])
                        # nodes[processName][decayChannel] = collections.OrderedDict()
                        nodes[processName][decayChannel] = collections.OrderedDict()
                        nodes[processName][decayChannel]["BaseNode"] = nodes[processName]["BaseNode"].Filter(filterNodes[processName][decayChannel]["BaseNode"][0],
                                                                                                             filterNodes[processName][decayChannel]["BaseNode"][1])
                        # countNodes[processName][decayChannel] = collections.OrderedDict()
                        countNodes[processName][decayChannel] = collections.OrderedDict()
                        countNodes[processName][decayChannel]["BaseNode"] = nodes[processName][decayChannel]["BaseNode"].Count()

                        #more freeform diagnostic nodes
                        diagnosticNodes[processName][decayChannel] = dict()

                        #Make some key for the histonodes, lets stop at decayChannel for now for the tuples, but keep a dict with histoName as key for histos...
                        defineNodes[processName][decayChannel] = []
                    if decayChannel not in histoNodes[processName]:
                        histoNodes[processName][decayChannel] = collections.OrderedDict()

                    #NOTE: This structure requires no dependency of L0 and higher nodes upon processName, leppostfix... potential problem later if that changes
                    #The layer 0 key filter, this is where we intend to start doing histograms (plus subsequently nested nodes on layers 1 and 2
                    if "L0Nodes" not in filterNodes[processName][decayChannel]:
                        filterNodes[processName][decayChannel]["L0Nodes"] = []
                        filterNodes[processName][decayChannel]["L1Nodes"] = []
                        filterNodes[processName][decayChannel]["L2Nodes"] = [] 

        
                    #We need some indices to be able to sub-select the filter nodes we need to apply, this makes it more automated when we add different nodes
                    #These indicate the start for slicing i.e list[start:stop]
                    L0start = len(filterNodes[processName][decayChannel]["L0Nodes"])
                    L1start = len(filterNodes[processName][decayChannel]["L1Nodes"])
                    L2start = len(filterNodes[processName][decayChannel]["L2Nodes"])
                        
                    #L0 nodes must reference the process, decay chanel, and this L0Key, which will form the first 3 nested keys in nodes[...]
                    #We'll create one of these for each decay channel, since this filter depends directly on the channel, and since it also depends on
                    #scale variation, it necessarily depends on the process, since that process may or may not have such a scale variation to be applied
                    filterNodes[processName][decayChannel]["L0Nodes"].append((L0String, L0Name, processName, decayChannel, L0Key, None, None)) #L0 filter
                    #Tuple format: (filter code, filter name, process, channel, L0 key, L1 key, L2 key) where only one of L0, L1, L2 keys are non-None!
                    
                    #These nodes should apply to any/all L0Nodes
                    # filterNodes[processName][decayChannel]["L1Nodes"].append(
                    #     ("return true;".format(tag=tagger, bpf=branchpostfix), "0+ nMediumDeep{tag}B({bpf})".format(tag=tagger, bpf=branchpostfix),processName, decayChannel, None, "nMediumDeep{tag}B0+".format(tag=tagger, bpf=branchpostfix), None))
                    # filterNodes[processName][decayChannel]["L1Nodes"].append(
                    #     ("nMediumDeep{tag}B{bpf} >= 1".format(tag=tagger, bpf=branchpostfix), "1+ nMediumDeep{tag}B({bpf})".format(tag=tagger, bpf=branchpostfix), processName, decayChannel, None, "nMediumDeep{tag}B1+".format(tag=tagger, bpf=branchpostfix), None))
                    filterNodes[processName][decayChannel]["L1Nodes"].append(
                        ("nMediumDeep{tag}B{bpf} >= 2".format(tag=tagger, bpf=branchpostfix), "2+ nMediumDeep{tag}B({bpf})".format(tag=tagger, bpf=branchpostfix), processName, decayChannel, None, "nMediumDeep{tag}B2+".format(tag=tagger, bpf=branchpostfix), None))
                    # filterNodes[processName][decayChannel]["L1Nodes"].append(
                    #     ("nMediumDeep{tag}B{bpf} == 0".format(tag=tagger, bpf=branchpostfix), "0 nMediumDeep{tag}B({bpf})".format(tag=tagger, bpf=branchpostfix),
                    #      processName, decayChannel, None, "nMediumDeep{tag}B0".format(tag=tagger, bpf=branchpostfix), None))
                    # filterNodes[processName][decayChannel]["L1Nodes"].append(
                    #     ("nMediumDeep{tag}B{bpf} == 1".format(tag=tagger, bpf=branchpostfix), "1 nMediumDeep{tag}B({bpf})".format(tag=tagger, bpf=branchpostfix),
                    #      processName, decayChannel, None, "nMediumDeep{tag}B1".format(tag=tagger, bpf=branchpostfix), None))
                    filterNodes[processName][decayChannel]["L1Nodes"].append(
                        ("nMediumDeep{tag}B{bpf} == 2".format(tag=tagger, bpf=branchpostfix), "2 nMediumDeep{tag}B({bpf})".format(tag=tagger, bpf=branchpostfix),
                         processName, decayChannel, None, "nMediumDeep{tag}B2".format(tag=tagger, bpf=branchpostfix), None))
                    filterNodes[processName][decayChannel]["L1Nodes"].append(
                        ("nMediumDeep{tag}B{bpf} == 3".format(tag=tagger, bpf=branchpostfix), "3 nMediumDeep{tag}B({bpf})".format(tag=tagger, bpf=branchpostfix),
                         processName, decayChannel, None, "nMediumDeep{tag}B3".format(tag=tagger, bpf=branchpostfix), None))
                    filterNodes[processName][decayChannel]["L1Nodes"].append(
                        ("nMediumDeep{tag}B{bpf} >= 4".format(tag=tagger, bpf=branchpostfix), "4+ nMediumDeep{tag}B({bpf})".format(tag=tagger, bpf=branchpostfix),
                         processName, decayChannel, None, "nMediumDeep{tag}B4+".format(tag=tagger, bpf=branchpostfix), None))
                    #These filters should apply to all L1Nodes
                    filterNodes[processName][decayChannel]["L2Nodes"].append(
                        ("nFTAJet{bpf} == 4".format(bpf=branchpostfix), "4 Jets ({bpf})".format(bpf=branchpostfix),
                         processName, decayChannel, None, None, "nJet4".format(bpf=branchpostfix)))
                    filterNodes[processName][decayChannel]["L2Nodes"].append(
                        ("nFTAJet{bpf} == 5".format(bpf=branchpostfix), "5 Jets ({bpf})".format(bpf=branchpostfix),
                         processName, decayChannel, None, None, "nJet5".format(bpf=branchpostfix)))
                    filterNodes[processName][decayChannel]["L2Nodes"].append(
                        ("nFTAJet{bpf} == 6".format(bpf=branchpostfix), "6 Jets ({bpf})".format(bpf=branchpostfix),
                         processName, decayChannel, None, None, "nJet6".format(bpf=branchpostfix)))
                    filterNodes[processName][decayChannel]["L2Nodes"].append(
                        ("nFTAJet{bpf} == 7".format(bpf=branchpostfix), "7 Jets ({bpf})".format(bpf=branchpostfix),
                         processName, decayChannel, None, None, "nJet7".format(bpf=branchpostfix)))
                    filterNodes[processName][decayChannel]["L2Nodes"].append(
                        ("nFTAJet{bpf} >= 8".format(bpf=branchpostfix), "8+ Jets ({bpf})".format(bpf=branchpostfix),
                         processName, decayChannel, None, None, "nJet8+".format(bpf=branchpostfix)))

                    #We need some indices to be able to sub-select the filter nodes we need to apply, this makes it more automated when we add different nodes
                    #These indicate the end for slicing
                    L0stop = len(filterNodes[processName][decayChannel]["L0Nodes"])
                    L1stop = len(filterNodes[processName][decayChannel]["L1Nodes"])
                    L2stop = len(filterNodes[processName][decayChannel]["L2Nodes"])

                    #To avoid any additional complexity, since this is too far from KISS as is, continue applying the filters right after defining them (same depth)
                    #unpack the tuple using lower case l prefix
                    for l0Tuple in filterNodes[processName][decayChannel]["L0Nodes"][L0start:L0stop]:
                        l0Code = l0Tuple[0]
                        l0Name = l0Tuple[1]
                        l0Proc = l0Tuple[2]
                        l0Chan = l0Tuple[3]
                        l0Key = l0Tuple[4]
                        l0l1Key = l0Tuple[5]
                        l0l2Key = l0Tuple[6]
                        assert l0Proc == processName, "processName mismatch, was it formatted correctly?\n{}".format(l0Tuple)
                        assert l0Chan == decayChannel, "decayChannel mismatch, was it formatted correctly?\n{}".format(l0Tuple)
                        assert l0l1Key == None, "non-None key in tuple for L1, was it added in the correct place?\n{}".format(l0Tuple)
                        assert l0l2Key == None, "non-None key in tuple for L2, was it added in the correct place?\n{}".format(l0Tuple)

                        #Here we begin the complication of flattening the key-value structure. We do not nest any deeper, but instead
                        #form keys as combinations of l0Key, l1Key, l2Key... 
                        #Here, form the cross key, and note the reference key it must use
                        crossl0Key = "{l0}{spf}".format(l0=l0Key, spf=syspostfix)
                        referencel0Key = "BaseNode" #L0 Filters are applied to 'BaseNode' of the nodes[proc][chan] dictionary of dataframes
                        if crossl0Key in nodes[processName][decayChannel]:
                            raise RuntimeError("Tried to redefine rdf node due to use of the same key: {}".format(crossl0Key))
                        nodes[processName][decayChannel][crossl0Key] = nodes[processName][decayChannel][referencel0Key].Filter(l0Code, l0Name)
                        countNodes[processName][decayChannel][crossl0Key] = nodes[processName][decayChannel][crossl0Key].Count()

                        #Begin the L1 nodes loop, mostly C+P
                        for l1Tuple in filterNodes[processName][decayChannel]["L1Nodes"][L1start:L1stop]:
                            l1Code = l1Tuple[0]
                            l1Name = l1Tuple[1]
                            l1Proc = l1Tuple[2]
                            l1Chan = l1Tuple[3]
                            l1l0Key = l1Tuple[4] #should be none
                            l1Key = l1Tuple[5]
                            l1l2Key = l1Tuple[6] #none
                            assert l1Proc == processName, "processName mismatch, was it formatted correctly?\n{}".format(l1Tuple)
                            assert l1Chan == decayChannel, "decayChannel mismatch, was it formatted correctly?\n{}".format(l1Tuple)
                            assert l1l0Key == None, "non-None key in tuple for L0, was it added in the correct place?\n{}".format(l1Tuple)
                            assert l1l2Key == None, "non-None key in tuple for L2, was it added in the correct place?\n{}".format(l1Tuple)
    
                            #Here we begin the complication of flattening the key-value structure. We do not nest any deeper, but instead
                            #form keys as combinations of l0Key, l1Key, l2Key... 
                            #Here, form the cross key, and note the reference key it must use
                            crossl0l1Key = "{l0}_CROSS_{l1}{spf}".format(l0=l0Key, l1=l1Key, spf=syspostfix)
                            referencel0l1Key = "{}".format(crossl0Key) #L1 Filters are applied to L0 filters, so this is the nodes[proc][chan][reference] to build filter on
                            if crossl0l1Key in nodes[processName][decayChannel]:
                                raise RuntimeError("Tried to redefine rdf node due to use of the same key: {}".format(crossl0l1Key))
                            nodes[processName][decayChannel][crossl0l1Key] = nodes[processName][decayChannel][referencel0l1Key].Filter(l1Code, l1Name)
                            countNodes[processName][decayChannel][crossl0l1Key] = nodes[processName][decayChannel][crossl0l1Key].Count()

                            #Begin the L2 nodes loop, mostly C+P
                            for l2Tuple in filterNodes[processName][decayChannel]["L2Nodes"][L2start:L2stop]:
                                l2Code = l2Tuple[0]
                                l2Name = l2Tuple[1]
                                l2Proc = l2Tuple[2]
                                l2Chan = l2Tuple[3]
                                l2l0Key = l2Tuple[4] #should be none
                                l2l1Key = l2Tuple[5] #none
                                l2Key = l2Tuple[6]
                                assert l2Proc == processName, "processName mismatch, was it formatted correctly?\n{}".format(l2Tuple)
                                assert l2Chan == decayChannel, "decayChannel mismatch, was it formatted correctly?\n{}".format(l2Tuple)
                                assert l2l0Key == None, "non-None key in tuple for L0, was it added in the correct place?\n{}".format(l2Tuple)
                                assert l2l1Key == None, "non-None key in tuple for L1, was it added in the correct place?\n{}".format(l2Tuple)
        
                                #Here we begin the complication of flattening the key-value structure. We do not nest any deeper, but instead
                                #form keys as combinations of l0Key, l1Key, l2Key... 
                                #Here, form the cross key, and note the reference key it must use
                                crossl0l1l2Key = "{l0}_CROSS_{l1}_CROSS_{l2}{spf}".format(l0=l0Key, l1=l1Key, l2=l2Key, spf=syspostfix)
                                referencel0l1l2Key = "{}".format(crossl0l1Key)#L2 Filters are applied to L1 filters, so this is the nodes[proc][chan][reference] to build upon
                                if crossl0l1l2Key in nodes[processName][decayChannel]:
                                    raise RuntimeError("Tried to redefine rdf node due to use of the same key: {}".format(crossl0l1l2Key))
                                nodes[processName][decayChannel][crossl0l1l2Key] = nodes[processName][decayChannel][referencel0l1l2Key].Filter(l2Code, l2Name)
                                countNodes[processName][decayChannel][crossl0l1l2Key] = nodes[processName][decayChannel][crossl0l1l2Key].Count()
                    #Start defining histograms here
                    #Name using unique identifying set: processName, decayChannel (lpf?), category (no bpf - non-unique), histogram name, systematic postfix
                    #The spf needs to uniquely identify the histogram relative to variations in lpf and bpf, so any given systematic should only referene these 
                    #as a set... would need a rework to involve 

        #Regarding naming conventions:
        #Since category can use __ as a separator between branchpostfix and the rest, extend to ___ to separate further... ugly, but lets
        #try sticking with valid C++ variable names (alphanumeric + _). Also note that {spf} will result in 3 underscores as is currently defined
        #CYCLE THROUGH CATEGORIES in the nodes that exist now, nodes[processName][decayChannel][CATEGORIES]
        #We are inside the systematics variation, so we cycle through everything else (nominal nodes having been created first!)
        for processName in nodes:
            if processName.lower() == "basenode": continue
            for decayChannel in nodes[processName]:
                if decayChannel.lower() == "basenode": continue
                for category, categoryNode in nodes[processName][decayChannel].items():
                    if category.lower() == "basenode": continue
                    diagnosticNodes[processName][decayChannel][category] = dict()
                    if doDiagnostics:
                        for trgTup in triggers:
                            if trgTup.era != era: continue
                            trg = trgTup.trigger
                            # diagnosticNodes[processName][decayChannel][category][trg] = categoryNode.Stats("typecast___{}".format(trg))
                        diagnosticNodes[processName][decayChannel][category]["nLooseMuon"] = categoryNode.Stats("nLooseFTAMuon{lpf}".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Muon_pfIsoId"] = categoryNode.Stats("FTAMuon{lpf}_pfIsoId".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Muon_pt"] = categoryNode.Stats("FTAMuon{lpf}_pt".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Muon_eta"] = categoryNode.Stats("FTAMuon{lpf}_eta".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Muon_charge"] = categoryNode.Stats("FTAMuon{lpf}_charge".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Muon_dz"] = categoryNode.Stats("FTAMuon{lpf}_dz".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Muon_dxy"] = categoryNode.Stats("FTAMuon{lpf}_dxy".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Muon_d0"] = categoryNode.Stats("FTAMuon{lpf}_d0".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Muon_ip3d"] = categoryNode.Stats("FTAMuon{lpf}_ip3d".format(lpf=leppostfix))
    
                        diagnosticNodes[processName][decayChannel][category]["nLooseElectron"] = categoryNode.Stats("nLooseFTAElectron{lpf}".format(lpf=leppostfix))
                        # diagnosticNodes[processName][decayChannel][category]["Electron_pfIsoId"] = categoryNode.Stats("FTAElectron{lpf}_pfIsoId".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Electron_pt"] = categoryNode.Stats("FTAElectron{lpf}_pt".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Electron_eta"] = categoryNode.Stats("FTAElectron{lpf}_eta".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Electron_charge"] = categoryNode.Stats("FTAElectron{lpf}_charge".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Electron_dz"] = categoryNode.Stats("FTAElectron{lpf}_dz".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Electron_dxy"] = categoryNode.Stats("FTAElectron{lpf}_dxy".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Electron_d0"] = categoryNode.Stats("FTAElectron{lpf}_d0".format(lpf=leppostfix))
                        diagnosticNodes[processName][decayChannel][category]["Electron_ip3d"] = categoryNode.Stats("FTAElectron{lpf}_ip3d".format(lpf=leppostfix))
                        
                    #IMPORTANT: Skip nodes that belong to other systematic variations, since it's a dictionary!
                    print("FIXME: Need to check this logic is properly skipping things correctly (see below this line in the source code)")
                    if category.split("___")[-1] != branchpostfix.replace("__", ""): continue 
                    isBlinded = False
                    #need to check that a category is blinded by making sure all orthogonal categories are blinded, i.e.,
                    #The category of nMediumDeepJetB2 + nJet7 is blinded, but not the same btag category with nJet4
                    for blindList in blindings:
                        #Check how many of the othrogonal categories in the blindList are contained in this category name
                        matchedElements = [blindElem for blindElem in blindList if blindElem in category]
                        #If all elements are contained, this is definitely a blinded category
                        if len(matchedElements) == len(blindList): 
                            isBlinded = True
                            continue
                    crossSeparated = "___".join(category.split("___")[:-1]).split("_CROSS_")#Strip the systematic name from the branch by taking all but the last element
                    categoryName = "_".join(crossSeparated) #No extra references to (lep/branch/sys)postfixes...
                    #This will be easier to deal with in plotting than prepending "blind_"
                    if isBlinded and isData:
                        # categoryName = "blind_" + categoryName
                        categoryName = categoryName + "BLIND"
                    if verbose:
                        print("blind={}\n{}\n{}\n\n".format(isBlinded, crossSeparated, categoryName))

                    #Append histogram tuples for HistoND() methods to the list, the list should overall contain each set grouped by systematic variation
                    Hstart = len(defineNodes[processName][decayChannel])
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_diffptraw{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "(Jet - Raw) p_{{T}} (CCJet)({spf});(Raw - Jet) p_{{T}}(CC LeadLep); Events".format(spf=syspostfix.replace("__", "")), 
                                                                    100,-300,300), "FTACrossCleanedJet{bpf}_diffptraw".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_diffptrawinverted{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "(Raw - Jet) p_{{T}} (non-CCJets)({spf});(Raw - Jet) p_{{T}}(CC LeadLep); Events".format(spf=syspostfix.replace("__", "")), 
                                                                    100,-300,300), "FTACrossCleanedJet{bpf}_diffptrawinverted".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_diffpt{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "(Jet - LeadLep) p_{{T}} (CCJet)({spf});(Jet - LeadLep) p_{{T}}(CC LeadLep); Events".format(spf=syspostfix.replace("__", "")), 
                                                                    100,-300,300), "FTACrossCleanedJet{bpf}_diffpt".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_pt{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "Jet p_{{T}} (CCJet)({spf});Jet p_{{T}}(CC LeadLep); Events".format(spf=syspostfix.replace("__", "")), 
                                                                    100,0,300), "FTACrossCleanedJet{bpf}_pt".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_rawpt{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "Jet Raw p_{{T}} (CCJet)({spf});Jet Raw p_{{T}}(CC LeadLep); Events".format(spf=syspostfix.replace("__", "")), 
                                                                    100,0,300), "FTACrossCleanedJet{bpf}_rawpt".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_leppt{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "Lead Lep p_{{T}} (CCJet)({spf});Lead Lep p_{{T}}(CC Jet); Events".format(spf=syspostfix.replace("__", "")), 
                                                                    100,0,300), "FTACrossCleanedJet{bpf}_leppt".format(bpf=branchpostfix), wgtVar))
                    for x in xrange(nJetsToHisto):
                        defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Jet_pt_jet{n}{spf}"\
                                                                        .format(proc=processName, n=x+1, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                        "Jet_{n} p_{{T}} ({spf}); p_{{T}}; Events"\
                                                                        .format(n=x+1, spf=syspostfix.replace("__", "")), 100, 0, 500),
                                                                       "{fj}_pt_jet{n}".format(fj=fillJet, n=x+1), wgtVar))
                        defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Jet_eta_jet{n}{spf}"\
                                                                        .format(proc=processName, n=x+1, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                        "Jet_{n} #eta ({spf}); #eta; Events"\
                                                                        .format(n=x+1, spf=syspostfix.replace("__", "")), 100, -2.6, 2.6),
                                                                       "{fj}_eta_jet{n}".format(fj=fillJet, n=x+1), wgtVar))
                        defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Jet_phi_jet{n}{spf}"\
                                                                        .format(proc=processName, n=x+1, chan=decayChannel, cat=categoryName,  spf=syspostfix),
                                                                        "Jet_{n} #phi ({spf}); #phi; Events".format(n=x+1, spf=syspostfix.replace("__", "")), 100, -pi, pi),
                                                                       "{fj}_phi_jet{n}".format(fj=fillJet, n=x+1), wgtVar))
                        defineNodes[processName][decayChannel].append( (("{proc}___{chan}___{cat}___Jet_DeepCSVB_jet{n}{spf}"\
                                                                         .format(proc=processName, n=x+1, chan=decayChannel, cat=categoryName,  spf=syspostfix),
                                                                         "Jet_{n} (p_{{T}} sorted) DeepCSV B Discriminant ({spf}); Discriminant; Events"\
                                                                         .format(n=x+1, spf=syspostfix.replace("__", "")), 100, 0.0, 1.0),
                                                                        "{fj}_DeepCSVB_jet{n}".format(fj=fillJet, n=x+1), wgtVar))
                        defineNodes[processName][decayChannel].append( (("{proc}___{chan}___{cat}___Jet_DeepJetB_jet{n}{spf}"\
                                                                         .format(proc=processName, n=x+1, chan=decayChannel, cat=categoryName,  spf=syspostfix),
                                                                         "Jet_{n} (p_{{T}} sorted) DeepJet B Discriminant ({spf}); Discriminant; Events"\
                                                                         .format(n=x+1, spf=syspostfix.replace("__", "")), 100, 0.0, 1.0),
                                                                        "{fj}_DeepJetB_jet{n}".format(fj=fillJet, n=x+1), wgtVar))
                        defineNodes[processName][decayChannel].append( (("{proc}___{chan}___{cat}___Jet_DeepCSVB_sortedjet{n}{spf}"\
                                                                         .format(proc=processName, n=x+1, chan=decayChannel, cat=categoryName,  spf=syspostfix),
                                                                         "Jet_{n} (DeepCSVB sorted) DeepCSV B Discriminant ({spf}); Discriminant; Events"\
                                                                         .format(n=x+1, spf=syspostfix.replace("__", "")), 100, 0.0, 1.0),
                                                                        "{fj}_DeepCSVB_sortedjet{n}".format(fj=fillJet, n=x+1), wgtVar))
                        defineNodes[processName][decayChannel].append( (("{proc}___{chan}___{cat}___Jet_DeepJetB_sortedjet{n}{spf}"\
                                                                         .format(proc=processName, n=x+1, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                         "Jet_{n} (DeepJetB sorted) DeepCSV B Discriminant ({spf}); Discriminant; Events"\
                                                                         .format(n=x+1, spf=syspostfix.replace("__", "")), 100, 0.0, 1.0),
                                                                        "{fj}_DeepJetB_sortedjet{n}".format(fj=fillJet, n=x+1), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___MET_pt{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "MET ({spf}); Magnitude (GeV); Events".format(spf=syspostfix.replace("__", "")), 
                                                                    100,0,1000), fillMET_pt, wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___MET_phi{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix),
                                                                    "MET #phi({spf}); #phi; Events".format(spf=syspostfix.replace("__", "")), 
                                                                    100,-pi,pi), fillMET_phi, wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___MET_uncorr_pt{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "Uncorrected MET", 100,0,1000), fillMET_uncorr_pt, wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___MET_uncorr_phi{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,-pi,pi), fillMET_uncorr_phi, wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_all{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_all".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_pt_LeadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, 10, 510), "FTAMuon{lpf}_pt_LeadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_pt_SubleadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, 10, 510), "FTAMuon{lpf}_pt_SubleadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_eta_LeadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, -2.5, 2.5), "FTAMuon{lpf}_eta_LeadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_eta_SubleadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, -2.5, 2.5), "FTAMuon{lpf}_eta_SubleadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_phi_LeadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, -pi, pi), "FTAMuon{lpf}_phi_LeadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_phi_SubleadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, -pi, pi), "FTAMuon{lpf}_phi_SubleadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_chg{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_chg".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso04_all{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix),
                                                                    "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso04_all".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_pt_LeadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, 10, 510), "FTAElectron{lpf}_pt_LeadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_pt_SubleadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, 10, 510), "FTAElectron{lpf}_pt_SubleadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_eta_LeadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, -2.5, 2.5), "FTAElectron{lpf}_eta_LeadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_eta_SubleadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, -2.5, 2.5), "FTAElectron{lpf}_eta_SubleadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_phi_LeadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, -pi, pi), "FTAElectron{lpf}_phi_LeadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_phi_SubleadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix, lpf=leppostfix), 
                                                                    "", 100, -pi, pi), "FTAElectron{lpf}_phi_SubleadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_all{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_all".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_chg{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_chg".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___ST{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,400,2000), "ST{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___HT{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,400,2000), "HT{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___H{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,400,2000), "H{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___HT2M{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,0,1000), "HT2M{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___H2M{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,0,1500), "H2M{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___HTb{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,0,1000), "HTb{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___HTH{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,0,1), "HTH{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___HTRat{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,0,1), "HTRat{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___dRbb{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,0,2*pi), "dRbb{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___dPhibb{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,-pi,pi), "dPhibb{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___dEtabb{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100,0,5), "dEtabb{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Lepton{lpf}_pt_LeadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 100,0,500), "FTALepton{lpf}_pt_LeadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Lepton{lpf}_pt_SubleadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 100,0,500), "FTALepton{lpf}_pt_SubleadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Lepton{lpf}_eta_LeadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 100,-2.6,2.6), "FTALepton{lpf}_eta_LeadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Lepton{lpf}_eta_SubleadLep{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 100,-2.6,2.6), "FTALepton{lpf}_eta_SubleadLep".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_pt{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 100,0,500), "FTAMuon{lpf}_pt".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_pt{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 100,0,500), "FTAElectron{lpf}_pt".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___dRll{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 100,0,2*pi), 
                                                                   "FTALepton{lpf}_dRll".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___dPhill{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 100,-pi,pi), 
                                                                   "FTALepton{lpf}_dPhill".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___dEtall{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 100,0,5), 
                                                                   "FTALepton{lpf}_dEtall".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___MTofMETandEl{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 100, 0, 200), 
                                                                   "MTofMETandEl{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___MTofMETandMu{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 100, 0, 200), 
                                                                   "MTofMETandMu{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___MTofElandMu{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 100, 0, 200), 
                                                                   "MTofElandMu{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nJet{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 14, 0, 14), 
                                                                   "n{fj}".format(fj=fillJet), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_LooseDeepCSV{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 6, 0, 6), 
                                                                   "nLooseDeepCSVB{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_MediumDeepCSV{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 6, 0, 6), 
                                                                   "nMediumDeepCSVB{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_TightDeepCSV{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 6, 0, 6), 
                                                                   "nTightDeepCSVB{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_LooseDeepJet{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 6, 0, 6), 
                                                                   "nLooseDeepJetB{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_MediumDeepJet{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 6, 0, 6), 
                                                                   "nMediumDeepJetB{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_TightDeepJet{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), "", 6, 0, 6), 
                                                                   "nTightDeepJetB{bpf}".format(bpf=branchpostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nLooseFTAMuon{lpf}{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 4, 0, 4), "nLooseFTAMuon{lpf}".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nMediumFTAMuon{lpf}{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 4, 0, 4), "nMediumFTAMuon{lpf}".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nTightFTAMuon{lpf}{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 4, 0, 4), "nTightFTAMuon{lpf}".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nLooseFTAElectron{lpf}{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 4, 0, 4), "nLooseFTAElectron{lpf}".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nMediumFTAElectron{lpf}{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 4, 0, 4), "nMediumFTAElectron{lpf}".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nTightFTAElectron{lpf}{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 4, 0, 4), "nTightFTAElectron{lpf}".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nLooseFTALepton{lpf}{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 4, 0, 4), "nLooseFTALepton{lpf}".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nMediumFTALepton{lpf}{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 4, 0, 4), "nMediumFTALepton{lpf}".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nTightFTALepton{lpf}{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, spf=syspostfix), 
                                                                    "", 4, 0, 4), "nTightFTALepton{lpf}".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_InvMass{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100, 0, 150), "FTAMuon{lpf}_InvariantMass".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_InvMass{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 100, 0, 150), "FTAElectron{lpf}_InvariantMass".format(lpf=leppostfix), wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_InvMass_v_MET{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 30, 0, 150, 20, 0, 400), "FTAMuon{lpf}_InvariantMass".format(lpf=leppostfix), fillMET_pt, wgtVar))
                    defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_InvMass_v_MET{spf}"\
                                                                    .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                    "", 30, 0, 150, 20, 0, 400), "FTAElectron{lpf}_InvariantMass".format(lpf=leppostfix), fillMET_pt, wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_all_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso03_all;MET", 30, 0., 0.2, 20,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_chg_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso04_all_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso04_all;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_all_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso03_all;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_chg_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_chg", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_all_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso03_all;MET", 30, 0., 0.2, 20,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_chg_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso04_all_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso04_all;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_all_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso03_all;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # Older versions
                    # defineNodes[processName][decayChannel].append(("{proc}___{chan}___{cat}___Muon_pfRelIso03_all_vs_MET{spf}"\
                    #                                                .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                ";pfRelIso03_all;MET", 100, 0., 0.2, 100,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_chg_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso03_chg;MET", 100, 0, 0.2, 100,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso04_all_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso04_all;MET", 100, 0, 0.2, 100,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_all_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso03_all;MET", 100, 0, 0.2, 100,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_chg_vs_MET{spf}"\
                    #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                    #                                                 ";pfRelIso03_chg;MET", 100, 0, 0.2, 100,30,1030), "FTAElectron{lpf}_pfRelIso03_chg", "fillMET_pt", wgtVar))
                    if isData == False:
                        defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_genMatched_puIdLoose{spf}"\
                                                                        .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                        "", 14, 0, 14), "n{fj}_genMatched_puIdLoose".format(fj=fillJet), wgtVar))
                        defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_genMatched{spf}"\
                                                                        .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                        "", 14, 0, 14), "n{fj}_genMatched".format(fj=fillJet), wgtVar))
                        # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___test1{spf}"
                        #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                        #                                                 ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAMuon{lpf}_pfRelIso03_all", "PV_npvsGood", wgtVar))
                        # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___test2{spf}"
                        #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                        #                                                 ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAMuon{lpf}_pfRelIso03_all", "METFixEE2017_pt", wgtVar))
                        # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___npvsGood_vs_nTrueInttest{spf}"
                        #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                        #                                                ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAElectron{lpf}_pfRelIso03_all", "MET_pt_flat", wgtVar))
                        defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___npvsGood_vs_nTrueInt{spf}"\
                                                                        .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                                                                        ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvsGood", wgtVar))
                        # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___npvsGood_vs_nPU{spf}"\
                        #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                        #                                                 ";nPU;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvsGood", wgtVar))
                        # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___npvs_vs_nTrueInt{spf}"\
                        #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                        #                                                 ";nTrueInt;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvs", wgtVar))
                        # defineNodes[processName][decayChannel].append((("{proc}___{chan}___{cat}___npvs_vs_nPU{spf}"\
                        #                                                 .format(proc=processName, chan=decayChannel, cat=categoryName,  spf=syspostfix), 
                        #                                                 ";nPU;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvs", wgtVar))


                    #End of definitions for this process + channel + category, now define the histoNodes based upon this categoryNode (nodes[proc][chan][category + branchpostfix]
                    Hstop = len(defineNodes[processName][decayChannel])
                    #Guard against histogram names already included (via keys in histNodes) as well as variables that aren't present in branches
                    # print("==============================> {} {} start: {} stop: {}".format(processName, decayChannel, Hstart, Hstop)) 
                    for dnode in defineNodes[processName][decayChannel][Hstart:Hstop]:
                        defHName = dnode[0][0]
                        #Need to determine which kind of histo function to use... have to be careful, this guess will be wrong if anyone ever does an unweighted histo!
                        if defHName in histoNodes[processName][decayChannel]:
                            raise RuntimeError("This histogram name already exists in memory or is intentionally being overwritten:"\
                                               "processName - {}\t decayChannel - {}\t defHName - {}".format(processName, decayChannel, defHName))
                        else:
                            for i in xrange(1, len(dnode)):
                                if dnode[i] not in listOfColumns:
                                    raise RuntimeError("This histogram's variable/weight is not defined:"\
                                                       "processName - {}\t decayChannel - {}\t variable/weight - {}".format(processName, decayChannel, dnode[i]))

                            guessDim = 0
                            if len(dnode) == 3:
                                guessDim = 1
                                histoNodes[processName][decayChannel][defHName] = categoryNode.Histo1D(dnode[0], dnode[1], dnode[2])
                            elif len(dnode) == 4:
                                guessDim = 2
                                histoNodes[processName][decayChannel][defHName] = categoryNode.Histo2D(dnode[0], dnode[1], dnode[2], dnode[3])
                            elif len(dnode) == 4:
                                guessDim = 3
                                histoNodes[processName][decayChannel][defHName] = categoryNode.Histo3D(dnode[0], dnode[1], dnode[2], dnode[3], dnode[4])

    packedNodes = {}
    packedNodes["filterNodes"] = filterNodes
    packedNodes["defineNodes"] = defineNodes
    packedNodes["countNodes"] = countNodes
    packedNodes["diagnosticNodes"] = diagnosticNodes
    packedNodes["nodes"] = nodes
    return packedNodes

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

def fillHLTMeans(input_df, wgtVar="wgt_SUMW_PU_L1PF", stats_dict=None):
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

def writeHistosForCombine(histDict, directory, levelsOfInterest, dict_key="Mountains", mode="RECREATE"):
    rootDict = {}
    if not os.path.isdir(directory):
        os.makedirs(directory)
    for name, levelsDict in histDict.items():
        for level, objDict in levelsDict.items():
            if level not in levelsOfInterest: continue
            if not os.path.isdir(directory + "/" + level):
                os.makedirs(directory + "/" + level)
            for preObjName, objVal in objDict[dict_key].items():
                for hname, hist in objVal.items():
                    dictKey = preObjName + "_" + hname
                    if dictKey not in rootDict:
                        rootDict[dictKey] = ROOT.TFile.Open("{}.root".format(directory + "/" + level + "/"+ dictKey), mode)
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
        
        
        
def writeHistosV1(histDict, directory, levelsOfInterest="All", samplesOfInterest="All", dict_keys="All", mode="RECREATE"):
    rootDict = {}
    if not os.path.isdir(directory):
        os.makedirs(directory)
    for name, levelsDict in histDict.items():
        if samplesOfInterest == "All": pass
        elif name not in samplesOfInterest: continue
        for level, objDict in levelsDict.items():
            if levelsOfInterest == "All": pass
            elif level not in levelsOfInterest: continue
            if not os.path.isdir(directory + "/" + level):
                os.makedirs(directory + "/" + level)
            rootDict[name] = ROOT.TFile.Open("{}.root".format(directory + "/" + level + "/"+ name), mode)
            for dict_key in objDict.keys():
                if dict_keys == "All": pass
                elif dict_key not in dict_keys: continue

                for preObjName, objVal in objDict[dict_key].items():
                    if type(objVal) == dict:
                        for hname, hist in objVal.items():
                            #help(hist)
                            #dictKey = preObjName + "$" + hname
                            #if dictKey not in rootDict:
                            #rootDict[dictKey].cd()
                            hptr = hist.GetPtr()
                            oldname = hptr.GetName()
                            #hptr.SetName("{}".format(dict_key + "*" + preObjName + "*" + hname))
                            hptr.Write()
                            #hptr.SetName("{}".format(oldname)) #Avoid overwriting things by switching back, save from segfault
                    elif "ROOT.TH" in str(type(objVal)):
                        hptr = objVal.GetPtr()
                        oldname = hptr.GetName()
                        #hptr.SetName("{}".format(dict_key + "*" + preObjName))
                        hptr.Write()
                        #hptr.SetName("{}".format(oldname)) #Avoid overwriting things by switching back, save from segfault
            print("Wrote histogram file for {} - {}".format(name, directory + "/" + level + "/"+ name))
    for f in rootDict.values():
        f.Close()

def writeHistos(histDict, directory, samplesOfInterest="All", channelsOfInterest="All", dict_keys="All", mode="RECREATE"):
    rootDict = {}
    if not os.path.isdir(directory):
        os.makedirs(directory)
    if len(histDict.keys()) < 1: print("writeHistos::no histDict keys")
    nameCounter = 0
    channelCounter = 0
    objCounter = 0
    nameCounterSkipped = 0
    channelCounterSkipped = 0
    for name, channelsDict in histDict.items():
        nameCounter += 1
        if samplesOfInterest == "All": pass
        elif name not in samplesOfInterest: 
            nameCounterSkipped += 1
            continue
        for channel, objDict in channelsDict.items():
            channelCounter += 1
            counter = 0
            if channelsOfInterest == "All": pass
            elif channel  not in channelsOfInterest: 
                channelCounterSkipped += 1
                continue
            elif len(objDict.values()) < 1:
                print("No objects to write, not creating directory or writing root file for {} {}".format(name, channel))
                continue
            if not os.path.isdir(directory + "/" + channel):
                os.makedirs(directory + "/" + channel)
            rootDict[name] = ROOT.TFile.Open("{}.root".format(directory + "/" + channel + "/"+ name), mode)
            # for dict_key in objDict.keys():
            #     if dict_keys == "All": pass
            #     elif dict_key not in dict_keys: continue
            for objname, obj in objDict.items():
                objCounter += 1
                if type(obj) == dict:
                    for hname, hist in obj.items():
                        if "ROOT.RDF.RResultPtr" in str(type(obj)):
                            hptr = hist.GetPtr()
                        else:
                            hptr = hist
                        hptr.Write()
                        counter += 1
                elif "ROOT.RDF.RResultPtr" in str(type(obj)):
                    hptr = obj.GetPtr()
                else:
                    hptr = obj
                hptr.Write()
                counter += 1
            print("Wrote {} histograms into file for {}::{} - {}.root".format(counter, name, channel, directory + "/" + channel + "/"+ name))
            rootDict[name].Close()
    print("samples skipped/cycled: {}/{}\tchannels skipped/cycled: {}/{}\tobjects cycled: {}".format(nameCounterSkipped,
                                                                                                     nameCounter, 
                                                                                                     channelCounterSkipped,
                                                                                                     channelCounter,
                                                                                                     objCounter
                                                                                                 ))



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
        if len(keysDict[name]) is 0: 
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
            for x in xrange(nBinsX):
                for y in xrange(nBinsY):
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
                if len(xbins)-1 > 1:
                    slice_dict[str(sn)]["hist"] = slice_dict[str(sn)]["hist"].Rebin(len(xbins)-1, "", xbins_vec)
                else:
                    pass
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


def makeJetEfficiencyReport(input_stats_dict, directory, levelsOfInterest="All"):
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
            if levelsOfInterest is not "All" and level not in levelsOfInterest: continue
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

        
def makeHLTReport(stats_dict, directory, levelsOfInterest="All"):
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
            if levelsOfInterest is not "All" and level not in levelsOfInterest: continue
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
            
def main(analysisDir, source, channel, bTagger, doDiagnostics=False, doNtuples=False, doHistos=False, 
         doLeptonSelection=False, doBTaggingYields=True, BTaggingYieldsFile="{}", 
         BTaggingYieldsAggregate=True, useHTOnly=False, useNJetOnly=False, 
         printBookkeeping=False, triggers=[], includeSampleNames=None, 
         useDeltaR=False, jetPtMin=30.0, jetPUId=None, 
         excludeSampleNames=None, verbose=False, quiet=False, checkMeta=True):

    ##################################################
    ##################################################
    ### CHOOSE SAMPLE DICT AND CHANNEL TO ANALYZE ####
    ##################################################
    ##################################################
    
    #Focus on limited set of events at a time
    #levelsOfInterest = set(["ElMu_selection"])
    #levelsOfInterest = set(["MuMu_selection",])
    #levelsOfInterest = set(["ElEl_selection",])
    #levelsOfInterest = set(["selection", "ElMu_selection", "ElEl_selection", "MuMu_selection", "Mu_selection", "El_selection"])
    #levelsOfInterest = set(["baseline", "MuMu_baseline", "ElEl_baseline", "selection", "MuMu_selection", "ElMu_selection"])
    #levelsOfInterest = set(["baseline", "MuMu_selection", "ElMu_selection"])    
    
    print("FIXME: The default list of samples has been defined internally and not deduced from the analysis directory...")
    all_samples = ["ElMu", "MuMu", "ElEl", "tttt", "ST_tW", "ST_tbarW", "tt_DL", "tt_DL-GF", 
                     "tt_SL", "tt_SL-GF", "ttH", "ttWJets", "ttZJets", "ttWH", "ttWW", "ttWZ", 
                     "ttZZ", "ttZH", "ttHH", "tttW", "tttJ", "DYJets_DL"]
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
    elif not doHistos and not doBTaggingYields and not doDiagnostics and not printBookkeeping and not doLeptonSelection:
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
        theSampleDict = bookerV2_SplitData.copy()
        theSampleDict.update(bookerV2_MC)
    elif channel == "ElMu":
        levelsOfInterest = set(["ElMu",])
        theSampleDict = bookerV2_ElMu.copy()
        theSampleDict.update(bookerV2_MC)
    elif channel == "MuMu":
        levelsOfInterest = set(["MuMu",])
        theSampleDict = bookerV2_MuMu.copy()
        theSampleDict.update(bookerV2_MC)
    elif channel == "ElEl":    
        levelsOfInterest = set(["ElEl",])
        theSampleDict = bookerV2_ElEl.copy()
        theSampleDict.update(bookerV2_MC)
    elif channel == "ElEl_LowMET":    
        levelsOfInterest = set(["ElEl_LowMET",])
        theSampleDict = bookerV2_ElEl.copy()
        theSampleDict.update(bookerV2_MC)
    elif channel == "ElEl_HighMET":    
        levelsOfInterest = set(["ElEl_HighMET",])
        theSampleDict = bookerV2_ElEl.copy()
        theSampleDict.update(bookerV2_MC)
    # This doesn't work, need the corrections on all the samples and such...
    # elif channel == "All":
    #     levelsOfInterest = set(["ElMu", "MuMu", "ElEl",])
    #     theSampleDict = bookerV2_ElMu.copy()
    #     theSampleDict.update(bookerV2_ElEl)
    #     theSampleDict.update(bookerV2_MuMu)
    #     theSampleDict.update(bookerV2_MC)
    elif channel == "Mu":    
        levelsOfInterest = set(["Mu",])
        theSampleDict = bookerV2_Mu.copy()
        theSampleDict.update(bookerV2_MC)
    elif channel == "El":    
        levelsOfInterest = set(["El",])
        theSampleDict = bookerV2_El.copy()
        theSampleDict.update(bookerV2_MC)
    elif channel == "test":
        print("More work to be done, exiting")
        sys.exit(2)
        
    
    print("Creating selection and baseline bits")
    #Set up channel bits for selection and baseline. Separation not necessary in this stage, but convenient for loops
    Chan = {}
    Chan["ElMu"] = 24576
    Chan["MuMu"] = 6144
    Chan["ElEl"] = 512
    Chan["ElEl_LowMET"] = Chan["ElEl"]
    Chan["ElEl_HighMET"] = Chan["ElEl"]
    Chan["Mu"] = 128
    Chan["El"] = 64
    Chan["selection"] = Chan["ElMu"] + Chan["MuMu"] + Chan["ElEl"] + Chan["Mu"] + Chan["El"]
    Chan["ElMu_baseline"] = 24576
    Chan["MuMu_baseline"] = 6144
    Chan["ElEl_baseline"] = 512
    Chan["Mu_baseline"] = 128
    Chan["El_baseline"] = 64
    Chan["baseline"] = Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"] + Chan["Mu_baseline"] + Chan["El_baseline"]
    
    b = {}
    b["ElMu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) > 0".format(Chan["ElMu_baseline"])
    b["MuMu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"], 
                Chan["MuMu_baseline"])
    b["ElEl_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"], Chan["ElEl_baseline"])
    b["Mu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"], Chan["Mu_baseline"])
    b["El_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"] + Chan["Mu_baseline"], Chan["El_baseline"])
    b["selection"] = "ESV_TriggerAndLeptonLogic_selection > 0"
    b["ElMu"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) > 0".format(Chan["ElMu"])
    b["MuMu"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"], Chan["MuMu"])
    b["ElEl"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"] + Chan["MuMu"], Chan["ElEl"])
    b["ElEl_LowMET"] = b["ElEl"]
    b["ElEl_HighMET"] = b["ElEl"]
    b["Mu"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"] + Chan["MuMu"] + Chan["ElEl"], Chan["Mu"])
    b["El"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"] + Chan["MuMu"] + Chan["ElEl"] + Chan["Mu"], Chan["El"]) 
    #This is deprecated, use dedicated RDF module
    #b["ESV_JetMETLogic_baseline"] = "(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00001100011111111111) #This enables the MET pt cut (11) and nJet (15) and HT (16) cuts from PostProcessor
    #b["ESV_JetMETLogic_baseline"] = "(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000001111111111) #Only do the PV and MET filters, nothing else
    #b["ESV_JetMETLogic_selection"] = "(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00001100011111111111) #FIXME, this isn't right!
    #b["ESV_JetMETLogic_selection"] = "(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00001100011111111111)#This enables the MET pt cut (11) and nJet (15) and HT (16) cuts from PostProcessor
    #b["ESV_JetMETLogic_selection"] = "(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000001111111111)
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
    metanode = {}
    metainfo = {}
    reports = {}
    samples = {}
    counts = {}
    histos = {}
    packedNodes = {}
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

    if not os.path.isdir(analysisDir):
        os.makedirs(analysisDir)

    Benchmark = ROOT.TBenchmark()
    for name, vals in theSampleDict.items():
        if name not in valid_samples: 
            print("Skipping sample {}".format(name))
            continue
        filelistDir = analysisDir + "/Filelists"
        if not os.path.isdir(filelistDir):
            os.makedirs(filelistDir)
        sampleOutFile = "{base}/{era}__{src}__{sample}.txt".format(base=filelistDir, era=vals["era"], src=source_level, sample=name)
        # sampleFriendFile = "{base}/{era}__{src}__{sample}__Friend0.txt".format(base=filelistDir, era=vals["era"], src=source_level, sample=name)
        fileList = []
        if os.path.isfile(sampleOutFile):
            fileList = getFiles(query="list:{}".format(sampleOutFile), outFileName=None)
        else:
            if "/eos/" in vals["source"][source_level]:
                redir="root://eosuser.cern.ch/".format(str(pwd.getpwuid(os.getuid()).pw_name)[0])
            else:
                redir="root://cms-xrd-global.cern.ch/"
            # if "dbs:" in vals["source"][source_level]:
            fileList = getFiles(query=vals["source"][source_level], redir=redir, outFileName=sampleOutFile)
            # else:
            #     fileList = getFiles(query=vals["source"][source_level], outFileName=sampleOutFile)
        transformedFileList = ROOT.std.vector(str)()
        for fle in fileList:
            transformedFileList.push_back(fle)
        if transformedFileList.size() < 1:
            print("No files located... skipping sample {}".format(name))
            continue

        #Construct TChain that we can add friends to potentially, but similarly constructin TChains and adding the chains with AddFriend
        print("Creating TChain for sample {}".format(name))
        tcmain = ROOT.TChain("Events")
        tcmeta = ROOT.TChain("Runs")
        for vfe in transformedFileList:
            print("\t{}".format(vfe))
            tcmain.Add(vfe)
            if checkMeta:
                tcmeta.Add(vfe)
        # tcfriend0 = ROOT.TChain("Events")
        # for vfef0 in transformedFileList_Friend0:
        #     tcfriend0.Add(vfef0)
        # tcmain.AddFriend(tcfriend0)
        # print("Initializing RDataFrame\n\t{} - {}".format(name, vals["source"][source_level]))
        # print("Initializing RDataFrame\n\t{} - {}".format(name, len(transformedFileList)))
        print("Initializing RDataFrame with TChain")
        filtered[name] = {}
        base[name] = RDF(tcmain)
        if checkMeta:
            metanode[name] = RDF(tcmeta) #meta tree
            if vals["isData"]:
                metainfo[name] = {"run": metanode[name].Sum("run")}
            else:
                metainfo[name] = {"run": metanode[name].Sum("run"), 
                                  "genEventCount": metanode[name].Sum("genEventCount"), 
                                  "genEventSumw": metanode[name].Sum("genEventSumw"), 
                                  "genEventSumw2": metanode[name].Sum("genEventSumw2"), 
                                  "nLHEScaleSumw": metanode[name].Sum("nLHEScaleSumw"), 
                                  "LHEScaleSumw": metanode[name].Sum("LHEScaleSumw"), 
                                  "nLHEPdfSumw": metanode[name].Sum("nLHEPdfSumw"), 
                                  "LHEPdfSumw": metanode[name].Sum("LHEPdfSumw")
                              }
            for mk, mv in metainfo[name].items():
                metainfo[name][mk] = mv.GetValue()
        metainfo[name]["totalEvents"] = tcmain.GetEntries()
        print("\n{}".format(name))
        pprint.pprint(metainfo[name])
        reports[name] = base[name].Report()
        counts[name] = {}
        # histos[name] = {}
        packedNodes[name] = {}
        the_df[name] = {}
        stats[name] = {}
        effic[name] = {}
        # btagging[name] = {}
        cat_df[name] = {}
        substart[name] = {}
        subfinish[name] = {}
        processed[name] = {}
        #counts[name]["baseline"] = filtered[name].Count() #Unnecessary with baseline in levels of interest?
        for lvl in levelsOfInterest:
            splitProcessConfig = vals.get("splitProcess", None)
            inclusiveProcessConfig = {"processes": {"{}".format(name): {"filter": "return true;",
                                                                  "nEventsPositive": vals.get("nEventsPositive", -1),
                                                                  "nEventsNegative": vals.get("nEventsNegative", -1),
                                                                  "fractionalContribution": 1,
                                                                  "sumWeights": vals.get("sumWeights", -1.0),
                                                                  "effectiveCrossSection": vals.get("crossSection", 0),
                                                              }}}
            pprint.pprint(inclusiveProcessConfig)
            
            if lvl == "BOOKKEEPING":
                #We just need the info printed on this one... book a Count node with progress bar if not quiet
                if quiet:
                    print("Going Quiet")
                    booktrigger = base[name].Count()
                else:
                    print("Booking progress bar")
                    booktrigger = ROOT.AddProgressBar(ROOT.RDF.AsRNode(base[name]), 
                                                      2000, long(metainfo[name]["totalEvents"]))
                prePackedNodes = splitProcess(base[name], 
                                              splitProcess = splitProcessConfig, 
                                              inclusiveProcess = inclusiveProcessConfig,
                                              sampleName = name, 
                                              isData = vals["isData"], 
                                              era = vals["era"],
                                              printInfo = True,
                                              fillDiagnosticHistos = True,
                )
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
                filtered[name][lvl] = base[name].Filter(b[lvl], lvl)
            #Cache() seemingly has an issue with the depth/breadth of full NanoAOD file. Perhaps one with fewer branches would work
            #filtered[name][lvl] = filtered[name][lvl].Cache()
            # if vals.get("stitch") != None:
            #     stitch_def = collections.OrderedDict()
            #     stitch_def["stitch_jet_mask"] = "GenJet_pt > 30"
            #     stitch_def["stitch_HT_mask"] = "GenJet_pt > 30 && abs(GenJet_eta) < 2.4"
            #     stitch_def["stitch_lep_mask"] = "abs(LHEPart_pdgId) == 15 || abs(LHEPart_pdgId) == 13 || abs(LHEPart_pdgId) == 11"
            #     stitch_def["stitch_nGenLep"] = "LHEPart_pdgId[stitch_lep_mask].size()"
            #     stitch_def["stitch_nGenJet"] = "GenJet_pt[stitch_jet_mask].size()"
            #     stitch_def["stitch_GenHT"] = "Sum(GenJet_pt[stitch_HT_mask])"
                
            #     stdict = stitchDict[vals.get("era")][vals.get("stitch").get("channel")]
            #     stitch_cut = "stitch_nGenLep == {} && stitch_nGenJet >= {} && stitch_GenHT >= {}"\
            #         .format(stdict.get("nGenLeps"), stdict.get("nGenJets"), stdict.get("GenHT"))
            #     if vals.get("stitch").get("source") == "Nominal":
            #         stitch_cut = "!({})".format(stitch_cut)
            #     elif vals.get("stitch").get("source") == "Filtered":
            #         print("Filtered sample, not producing a filter (no events expected to fail filtering. If otherwise, alter code")
            #     else:
            #         print("Invalid stitching source type")
            #         sys.exit(1)
            #     if verbose:
            #         print(stitch_cut)
            #     for k, v in stitch_def.items():
            #         filtered[name][lvl] = filtered[name][lvl].Define("{}".format(k), "{}".format(v))
            #     filtered[name][lvl] = filtered[name][lvl].Filter(stitch_cut, "nJet_GenHT_Filter")
            #Add the MET corrections, creating a consistently named branch incorporating the systematics loaded
            the_df[name][lvl] = METXYCorr(filtered[name][lvl],
                                          run_branch="run",
                                          era=vals["era"],
                                          isData=vals["isData"],
                                          sysVariations=systematics_2017, 
                                          verbose=verbose,
                                          )
            #Define the leptons based on LeptonLogic bits, to be updated and replaced with code based on triggers/thresholds/leptons present (on-the-fly cuts)
            the_df[name][lvl] = defineLeptons(the_df[name][lvl], 
                                              input_lvl_filter=lvl,
                                              isData=vals["isData"], 
                                              era=vals["era"],
                                              useBackupChannel=False,
                                              triggers=triggers,
                                              sysVariations=systematics_2017,
                                              rdfLeptonSelection=doLeptonSelection,
                                              verbose=verbose,
                                             )
            #Use the cutPV and METFilters function to do cutflow on these requirements... this should be updated, still uses JetMETLogic bits... FIXME
            the_df[name][lvl] = cutPVandMETFilters(the_df[name][lvl], lvl, isData=vals["isData"])
            #Init weights necessary for now, should be combined with defineWeights to do everything after the other defines are finished (Jets...)
            if vals["isData"] == False:
                the_df[name][lvl] = defineInitWeights(the_df[name][lvl],
                                                      crossSection=vals["crossSection"], 
                                                      sumWeights=vals["sumWeights"], 
                                                      era=vals["era"],
                                                      nEvents=vals["nEvents"], 
                                                      nEventsPositive=vals["nEventsPositive"], 
                                                      nEventsNegative=vals["nEventsNegative"], 
                                                      isData=vals["isData"], 
                                                      verbose=verbose,
                                                     )
            else:
                the_df[name][lvl] = defineInitWeights(the_df[name][lvl],
                                                      isData=True,
                                                      verbose=verbose,
                                                     )
            the_df[name][lvl] = defineJets(the_df[name][lvl],
                                           era=vals["era"],
                                           bTagger=bTagger,
                                           isData=vals["isData"],
                                           sysVariations=systematics_2017, 
                                           jetPtMin=jetPtMin,
                                           jetPUId=jetPUId,
                                           useDeltaR=useDeltaR,
                                           verbose=verbose,
                                          )
            # print("Filtering out events where a jet is/isn't cross-cleaned against the leading lepton")
            # the_df[name][lvl] = the_df[name][lvl].Filter("FTALepton_jetIdx.at(0) < 0 || prejet_mask.at(FTALepton_jetIdx.at(0)) == false", "events with no otherwise selected jet cross-cleaned against the lead lepton")
            # the_df[name][lvl] = the_df[name][lvl].Filter("FTALepton_jetIdx.at(0) >= 0 && prejet_mask.at(FTALepton_jetIdx.at(0)) == true", "events with otherwise-selected jet cross-cleaned against the lead lepton")
            if quiet:
                print("Going Quiet")
                counts[name][lvl] = the_df[name][lvl].Count()
            else:
                print("Booking progress bar")
                counts[name][lvl] = ROOT.AddProgressBar(ROOT.RDF.AsRNode(the_df[name][lvl]), 
                                                        min(5000, max(1000, int(metainfo[name]["totalEvents"]/5000))), long(metainfo[name]["totalEvents"]))
            # histos[name][lvl] = {} #new style, populated inside fillHistos... differs from BTaggingYields right now! Future work
            packedNodes[name][lvl] = None
            stats[name][lvl] = {}
            effic[name][lvl] = {}
            # btagging[name][lvl] = {}
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
            #Insert the yields or calculate them
            #Define the final weights/variations so long as we have btagging yields inserted...
            # splitProcessConfig=None
            # print("Forcing splitProcess to False for now, check this line!")
            prePackedNodes = splitProcess(the_df[name][lvl], 
                                          splitProcess = splitProcessConfig, 
                                          inclusiveProcess = inclusiveProcessConfig,
                                          sampleName = name, 
                                          isData = vals["isData"], 
                                          era = vals["era"],
                                          printInfo = printBookkeeping,
            )
            prePackedNodes = defineWeights(prePackedNodes,
                                           splitProcess = splitProcessConfig,
                                           era=vals["era"],
                                           isData=vals["isData"],
                                           final=False,
                                           sysVariations=systematics_2017, 
                                           verbose=verbose,
            )
            prePackedNodes = BTaggingYields(prePackedNodes, sampleName=name, isData=vals["isData"], channel=lvl,
                                            histosDict=btagging, loadYields=BTaggingYieldsFile,
                                            useAggregate=True, useHTOnly=useHTOnly, useNJetOnly=useNJetOnly,
                                            sysVariations=systematics_2017, 
                                            bTagger=bTagger,
                                            calculateYields=calculateTheYields,
                                            HTArray=[500, 650, 800, 1000, 1200, 10000], 
                                            nJetArray=[4,5,6,7,8,20],
                                            verbose=verbose,
            )
            if BTaggingYieldsFile:
                print("What is happening in defineWeights here? Need to modify the prePackedNodes, then... pass on to the fillHistos method")
                prePackedNodes = defineWeights(prePackedNodes,
                                               splitProcess = splitProcessConfig,
                                               # inclusiveProcess = inclusiveProcessConfig,
                                               era = vals["era"],
                                               isData = vals["isData"],
                                               final=True,
                                               sysVariations=systematics_2017, 
                                               verbose=verbose,
                )
            #All of these are deprecated as-is
            # if doBTaggingEfficiencies == True:
            #     BTaggingEfficiencies(the_df[name][lvl], sampleName=None, era = vals["era"], wgtVar="wgt_SUMW_PU_LSF_L1PF", 
            #                    isData = vals["isData"], histosDict=btagging[name][lvl], 
            #                    doDeepCSV=True, doDeepJet=True)
            # if doJetEfficiency:
            #     jetMatchingEfficiency(the_df[name][lvl], wgtVar="wgt_SUMW_PU_LSF_L1PF", stats_dict=effic[name][lvl],
            #                           isData = vals["isData"])
            # if doHLTMeans:
            #     fillHLTMeans(the_df[name][lvl], wgtVar="wgt_SUMW_PU_L1PF", stats_dict=stats[name][lvl])

            #Hold the categorization nodes if doing histograms
            if doNtuples:
                ntupleDir = analysisDir + "/Ntuples"
                if not os.path.isdir(ntupleDir):
                    os.makedirs(ntupleDir)
                treeName = "Events"
                pdb.set_trace()
                filename = ntupleDir + "/{}".format("bleh")
                print("I made a name: {}".format(filename))
                # ROOT.FTA.bookLazySnapshot(ROOT.RDF.AsRNode(), "Events",  
            if doHistos:
                packedNodes[name][lvl] = fillHistos(prePackedNodes, splitProcess=splitProcessConfig, isData = vals["isData"], era = vals["era"], triggers = triggers,
                                                    sampleName=name, channel=lvl.replace("_selection", "").replace("_baseline", ""), 
                                                    histosDict=histos, sysVariations=systematics_2017, doCategorized=True, 
                                                    doDiagnostics=True, bTagger=bTagger, verbose=verb)
            if doDiagnostics:
                packedNodes[name][lvl] = fillHistos(prePackedNodes, splitProcess=splitProcessConfig, isData = vals["isData"], era = vals["era"], triggers = triggers,
                                                    sampleName=name, channel=lvl.replace("_selection", "").replace("_baseline", ""), 
                                                    histosDict=histos, sysVariations=systematics_2017, doCategorized=False, 
                                                    doDiagnostics=True, bTagger=bTagger, verbose=verb)
                # print(packedNodes[name][lvl].keys())
                # print(packedNodes[name][lvl].keys())
                # assert False, "Exiting early here, brah"
            #print(cat_df)
                
            #Trigger the loop
            print("\nSTARTING THE EVENT LOOP")
            substart[name][lvl] = time.clock()
            Benchmark.Start("{}/{}".format(name, lvl))
            processed[name][lvl] = counts[name][lvl].GetValue()
            print("\nFINISHING THE EVENT LOOP")
            print("ROOT Benchmark stats...")
            Benchmark.Show("{}/{}".format(name, lvl))
            subfinish[name][lvl] = time.clock()
            theTime = subfinish[name][lvl] - substart[name][lvl]

            #Write the output!
            # if doBTaggingYields:
            #     print("Writing outputs...")
            #     writeDir = analysisDir + "/BTaggingYields"
            #     writeHistosV1(btagging,
            #                 writeDir,
            #                 levelsOfInterest=[lvl],
            #                 samplesOfInterest=[name],
            #                 dict_keys="All",
            #                 mode="RECREATE"
            #                )
            if doHistos or doBTaggingYields:
                print("Writing outputs...")
                processesOfInterest = []
                if splitProcessConfig != None:
                    for thisProc in splitProcessConfig.get("processes", {}).keys():
                        processesOfInterest.append(vals.get("era") + "___" + thisProc)
                else:
                    processesOfInterest.append(vals.get("era") + "___" + name)
                print("Writing historams for...{}".format(processesOfInterest))

                if doHistos:
                    writeDir = analysisDir + "/Histograms"
                    writeDict = histos
                if doBTaggingYields:
                    writeDir = analysisDir + "/BTaggingYields"
                    writeDict = btagging
                writeHistos(writeDict, 
                            writeDir,
                            channelsOfInterest="All",
                            samplesOfInterest=processesOfInterest,
                            dict_keys="All",
                            mode="RECREATE"
                        )
                print("Wrote Histograms for {} to this directory:\n{}".format(name, writeDir))
            if doBTaggingYields:
                print("To calculate the yield ratios, run 'BTaggingYieldsAnalyzer()' once all samples that are to be aggregated are in the directory")
            #Add sample name to the list of processed samples and print it, in case things ****ing break in Jupyter Kernel
            processedSampleList.append(name)
            print("Processed Samples:")
            processedSamples = ""
            for n in processedSampleList:
                processedSamples += "{} ".format(n)
            print(processedSamples)
            print("Took {}m {}s ({}s) to process {} events from sample {} in channel {}\n\n\n{}".format(theTime//60, theTime%60, theTime, processed[name][lvl], 
                         name, lvl, "".join(["\_/"]*25)))
    # Benchmark.Summary()
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
    
    for name, val in substart.items():
        print("Took {}s to process sample {}".format(subfinish[name] - substart[name], name))
    print()
    masterfinish = time.time() #clock gives cpu time, not accurate multi-core?
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
    parser.add_argument('stage', action='store', type=str, choices=['bookkeeping', 'fill-yields', 'combine-yields', 'lepton-selection', 'fill-diagnostics', 
                                                                    'fill-histograms', 'fill-ntuples', 'prepare-for-combine'],
                        help='analysis stage to be produced')
    parser.add_argument('--source', dest='source', action='store', type=str, default='LJMLogic__{chan}_selection',
                        help='Stage of data storage to pull from, as referenced in Sample dictionaries as subkeys of the "source" key.'\
                        'Must be available in all samples to be processed. {chan} will be replaced with the channel analyzed')
    parser.add_argument('--channel', dest='channel', action='store', type=str, default="ElMu", choices=['ElMu', 'ElEl', 'MuMu', 'ElEl_LowMET', 'ElEl_HighMET'],
                        help='Decay channel for opposite-sign dilepton analysis')
    parser.add_argument('--analysisDirectory', dest='analysisDirectory', action='store', type=str, default="/eos/user/$U/$USER/analysis/$DATE",
                        help='output directory path defaulting to "."')
    parser.add_argument('--quiet', dest='quiet', action='store_true',
                        help='Disable progress bars')
    parser.add_argument('--jetPtMin', dest='jetPtMin', action='store', default=30.0, type=float,
                        help='Float value for the minimum Jet pt in GeV, defaulting to 30.0')
    parser.add_argument('--jetPUId', dest='jetPUId', action='store', default=None, nargs='?', const='L', type=str, choices=['L', 'M', 'T'],
                        help='Optionally apply Jet PU Id to the selected jets, with options for Loose ("L"), Medium ("M"), or Tight ("T") using the 80X training.')
    parser.add_argument('--useDeltaR', dest='useDeltaR', action='store', type=float, default=0.4, #nargs='?', const=0.4,
                        help='Default distance parameter 0.4, set alternative float value for Lepton-Jet cross-cleaning')
    parser.add_argument('--usePFMatching', dest='usePFMatching', action='store_true', 
                        help='Enable usage of PFMatching for Lepton-Jet cross-cleaning')
    parser.add_argument('--bTagger', dest='bTagger', action='store', default='DeepCSV', type=str, choices=['DeepCSV', 'DeepJet'],
                        help='bTagger algorithm to be used')
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
    parser.add_argument('--systematics', dest='systematics', action='store', default=None, type=str, nargs='*',
                        help='List of systematic variations to compute (if not called, defaults to None and only nominal is run. Call with list of systematic names or "All"')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')
    # parser.add_argument('--sample_cards', dest='sample_cards', action='store', nargs='*', type=str,
    #                     help='path and name of the sample card(s) to be used')
    # parser.add_argument('--filter', dest='filter', action='store', type=str, default=None,
    #                     help='string to filter samples while checking events or generating configurations')
    # parser.add_argument('--redir', dest='redir', action='append', type=str, default='root://cms-xrd-global.cern.ch/',
    #                     help='redirector for XRootD, such as "root://cms-xrd-global.cern.ch/"')
    # parser.add_argument('--era', dest='era', action='store', type=str, default="2017", choices=['2016', '2017', '2018'],
    #                     help='simulation/run year')
    #nargs='+' #this option requires a minimum of arguments, and all arguments are added to a list. '*' but minimum of 1 argument instead of none

    #Parse the arguments
    args = parser.parse_args()
    #Get the username and today's date for default directory:
    uname = pwd.getpwuid(os.getuid()).pw_name
    uinitial = uname[0]
    dateToday = datetime.date.today().strftime("%b-%d-%Y")

    #Grab and format required and optional arguments
    analysisDir = args.analysisDirectory.replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday)
    stage = args.stage
    channel = args.channel
    source = args.source.format(chan=channel)
    doNtuples = args.doNtuples
    if stage == 'fill-ntuples':
        doNtuples = True
    jetPtMin=args.jetPtMin
    jetPUId=args.jetPUId
    useDeltaR = args.useDeltaR
    bTagger = args.bTagger
    includeSampleNames = args.include
    excludeSampleNames = args.exclude
    verb = args.verbose
    useAggregate = not args.noAggregate
    useHTOnly = args.useHTOnly
    useNJetOnly = args.useNJetOnly
    quiet = args.quiet
    
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

    print("Analysis stage: {stg}".format(stg=stage))
    print("Analysis directory: {adir}".format(adir=analysisDir))
    print("Channel to be analyzed: {chan}".format(chan=channel))
    print("Algorithm for Lepton-Jet crosscleaning: {}".format("PFMatching" if not useDeltaR else "DeltaR < {}".format(useDeltaR)))
    print("Jet selection is using these parameters: Minimum Pt: {} PU Id: {}".format(jetPtMin, jetPUId))
    print("BTagger algorithm to be used: {tag}".format(tag=bTagger))
    print("BTagging aggregate Yields/Efficiencies will be used ({uAgg}) and depend on HT only ({uHT}) or nJet only ({uNJ})"\
          .format(uAgg=useAggregate, uHT=useHTOnly, uNJ=useNJetOnly))
    if includeSampleNames:
        print("Include samples: {incld}".format(incld=includeSampleNames))
    elif excludeSampleNames:
        print("Exclude samples: {excld}".format(excld=excludeSampleNames))
    else:
        print("Using all samples!")
    print("Verbose option: {verb}".format(verb=verb))
    print("Quiet option: {qt}".format(qt=quiet))
    print("Systematics (This code not yet integrated... testing): {}".format(args.systematics))    


    #Run algos appropriately for the given configuration
    if stage == 'fill-yields':
        print("This function needs reworking... work on it")
        print("Filling BTagging sum of weights (yields) before and after applying shape-correction scale factors for the jets")
        # print('main(analysisDir=analysisDir, channel=channel, doBTaggingYields=True, doHistos=False, BTaggingYieldsFile="{}", source=source, verbose=False)')
        packed = main(analysisDir, source, channel, bTagger=bTagger, doDiagnostics=False, doHistos=False, doBTaggingYields=True, BTaggingYieldsFile="{}", 
                      BTaggingYieldsAggregate=useAggregate, useDeltaR=useDeltaR, jetPtMin=jetPtMin, jetPUId=jetPUId, useHTOnly=useHTOnly, useNJetOnly=useNJetOnly, 
                      printBookkeeping = False, triggers=TriggerList, includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, quiet=quiet)
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
        packed = main(analysisDir, source, channel, bTagger=bTagger, doDiagnostics=False, doHistos=False, doLeptonSelection=True, doBTaggingYields=False, 
                      BTaggingYieldsFile="{}", BTaggingYieldsAggregate=useAggregate, jetPtMin=jetPtMin, jetPUId=jetPUId, useDeltaR=useDeltaR, 
                      useHTOnly=useHTOnly, useNJetOnly=useNJetOnly, printBookkeeping = False, triggers=TriggerList, 
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, quiet=quiet)
    elif stage == 'fill-diagnostics':
        print("This method needs some to-do's checked off. Work on it.")
        packed = main(analysisDir, source, channel, bTagger=bTagger, doDiagnostics=True, doHistos=False, doBTaggingYields=False, BTaggingYieldsFile="{}", 
                      BTaggingYieldsAggregate=useAggregate, jetPtMin=jetPtMin, jetPUId=jetPUId, useDeltaR=useDeltaR, useHTOnly=useHTOnly, 
                      useNJetOnly=useNJetOnly, printBookkeeping = False, triggers=TriggerList, 
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, quiet=quiet)
    elif stage == 'bookkeeping':
        packed = main(analysisDir, source, "BOOKKEEPING", bTagger=bTagger, doDiagnostics=False, doHistos=False, doBTaggingYields=False, BTaggingYieldsFile="{}", 
                      BTaggingYieldsAggregate=useAggregate, jetPtMin=jetPtMin, jetPUId=jetPUId, useDeltaR=useDeltaR, useHTOnly=useHTOnly, 
                      useNJetOnly=useNJetOnly, printBookkeeping = True, triggers=TriggerList, 
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, quiet=quiet)
    elif stage == 'fill-histograms':
        #filling ntuples is also possible with the option --doNtuples
        packed = main(analysisDir, source, channel, bTagger=bTagger, doDiagnostics=False, doNtuples=doNtuples, doHistos=True, 
                      doBTaggingYields=False, BTaggingYieldsFile="{}", BTaggingYieldsAggregate=useAggregate, 
                      jetPtMin=jetPtMin, jetPUId=jetPUId, useDeltaR=useDeltaR, useHTOnly=useHTOnly, 
                      useNJetOnly=useNJetOnly, printBookkeeping = False, triggers=TriggerList, 
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, quiet=quiet)
    elif stage == 'fill-ntuples':
        packed = main(analysisDir, source, channel, bTagger=bTagger, doDiagnostics=False, doNtuples=doNtuples, doHistos=False, 
                      doBTaggingYields=False, BTaggingYieldsFile="{}", BTaggingYieldsAggregate=useAggregate, 
                      jetPtMin=jetPtMin, jetPUId=jetPUId, useDeltaR=useDeltaR, useHTOnly=useHTOnly, 
                      useNJetOnly=useNJetOnly, printBookkeeping = False, triggers=TriggerList, 
                      includeSampleNames=includeSampleNames, excludeSampleNames=excludeSampleNames, verbose=verb, quiet=quiet)
    elif stage == 'prepare-for-combine':
        print("This analysis stage is not yet finished. It will call the method histoCombine() which needs to be updated for the new internal key structure from fillHistos")
    else:
        print("stage {stag} is not yet prepared, please update the FTAnalyzer".format(stag))
