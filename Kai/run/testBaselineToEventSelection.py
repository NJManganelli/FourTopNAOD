from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
from FourTopNAOD.Kai.modules.EventSelector import EventSelector
from FourTopNAOD.Kai.modules.trigger import Trigger
from Supervisor import getFiles
import collections, copy, json
import multiprocessing
import os, time

theBTagger=['CSVv2', 'M']    
p=PostProcessor("/tmp/nmangane", #"./"+theEra+"/"+theBTagger[0],
                    getFiles(globPath="../crab/Stage_NANOv4_to_Baseline/crab_20190626_1624/crab_tt_DL-GF_2017/results/", globFileExp='tree_*.root'),
                    modules=[#                   btagSFProducer(theEra[0], algo=theBTagger[0]),
                        EventSelector(maxevt=500000, 
                                      probEvt=None,
                                      isData=False,
                                      genEquivalentLuminosity=42.5,
                                      genXS=1.32512,
                                      genNEvents=8458223,
                                      genSumWeights=608347760.180597,
                                      era="2017",
                                      btagging=theBTagger,
                                      lepPt=25, 
                                      MET=50, 
                                      HT=500, 
                                      invertZWindow=False, 
                                      invertZWindowEarlyReturn=False,
                                      GenTop_LepSelection=None,
                                      jetPtVar="pt_nom",
                                      jetMVar="mass_nom"
                                  ),
                    ],
                    noOut=False,
                    postfix="test",
                    haddFileName="testBtESel_tt_DL-GF_2017.root",
                    histFileName="testBtE_hist.root",
                    histDirName="plots",
                   )
p.run()

