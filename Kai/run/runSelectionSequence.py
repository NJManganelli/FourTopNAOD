from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from FourTopNAOD.Kai.modules.MCTreeDev import TenKTree
from FourTopNAOD.Kai.modules.MCTreePlot import MCTreePlot
from FourTopNAOD.Kai.modules.BaselineSelector import BaselineSelector
from FourTopNAOD.Kai.modules.trigger import Trigger
import collections, copy, json
import multiprocessing
import os, time

Tuples=[]

basefiles=["tree_1.root", "tree_2.root", "tree_3.root", "tree_4.root", "tree_5.root", "tree_6.root"] 
preTTTT="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTTv2/results/"
preTT2L="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTo2L2Nu/results/"
preTT2LGF="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTo2L2Nu_GenFilt/results/"
preTT1L="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTToSemiLeptonic/results/"
preTT1LGF="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTToSemiLeptonic_GenFilt/results/"

triggers=["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
          "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
          "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
          "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
          "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"
          ]

hName="SelSeq-TTTT-PU-TRG.root"
fName="SelSeq-TTTT-PU-TRG.root"
files=[preTTTT+file for file in basefiles]
filt=None
Tuples.append((files, hName, fName, filt))

hName="SelSeq-TTTT-SingleLepton-PU-TRG.root"
fName="SelSeq-TTTT-SingleLepton-PU-TRG.root"
files=[preTTTT+file for file in basefiles]
filt=1
Tuples.append((files, hName, fName, filt))

hName="SelSeq-TTTT-DiLepton-PU-TRG.root"
fName="SelSeq-TTTT-DiLepton-PU-TRG.root"
files=[preTTTT+file for file in basefiles]
filt=2
Tuples.append((files, hName, fName, filt))

hName="SelSeq-TTTT-TriLepton-PU-TRG.root"
fName="SelSeq-TTTT-TriLepton-PU-TRG.root"
files=[preTTTT+file for file in basefiles]
filt=3
Tuples.append((files, hName, fName, filt))

hName="SelSeq-TTTo2L2Nu-PU-TRG.root"
fName="SelSeq-TTTo2L2Nu-PU-TRG.root"
files=[preTT2L+file for file in basefiles]
filt=None
Tuples.append((files, hName, fName, filt))

hName="SelSeq-TTTo2L2NuGF-PU-TRG.root"
fName="SelSeq-TTTo2L2NuGF-PU-TRG.root"
files=[preTT2LGF+file for file in basefiles]
filt=None
Tuples.append((files, hName, fName, filt))

hName="SelSeq-TTToSemiLeptonic-PU-TRG.root"
fName="SelSeq-TTToSemiLeptonic-PU-TRG.root"
files=[preTT1L+file for file in basefiles]
filt=None
Tuples.append((files, hName, fName, filt))

hName="SelSeq-TTToSemiLeptonicGF-PU-TRG.root"
fName="SelSeq-TTToSemiLeptonicGF-PU-TRG.root"
files=[preTT1LGF+file for file in basefiles]
filt=None
Tuples.append((files, hName, fName, filt))


def multiplier(fileList, hName=None, fName="def.root", NLeps=None, maxevt=10000):
    hName = None
    hDirName = None
    p=PostProcessor(".",
                    fileList,
                    modules=[puWeightProducer("auto",pufile_data2017,"pu_mc","pileup",verbose=True), 
                             Trigger(triggers), 
                             BaselineSelector(isData=True, era="2017", btagging=['DeepCSV','M'], lepPt=25, MET=50, HT=500, invertZWindow=False, GenTop_LepSelection=None),
                             # MCTreePlot(maxevt=maxevt, filterNLeps=NLeps)
                            ],
                    haddFileName=fName,
                    noOut=False,
                    # histFileName=hName,
                    # histDirName=hDirName,
                   )
    p.run()

pList = []
nmbr = 0
for tup in Tuples:
    if nmbr > 0: continue
    nmbr += 1
    p = multiprocessing.Process(target=multiplier, args=(tup[0], tup[1], tup[2], tup[3], 10000))
    pList.append(p)
    p.start()

for p in pList:
    p.join()
