from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.modules.MCTreeDev import TenKTree
from FourTopNAOD.Kai.modules.MCTreePlot import MCTreePlot
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



hName="MCTreePlot-TTTT-v0p4.root"
files=[preTTTT+file for file in basefiles]
filt=None
Tuples.append((files, hName, filt))

hName="MCTreePlot-TTTT-SingleLepton-v0p4.root"
files=[preTTTT+file for file in basefiles]
filt=1
Tuples.append((files, hName, filt))

hName="MCTreePlot-TTTT-DiLepton-v0p4.root"
files=[preTTTT+file for file in basefiles]
filt=2
Tuples.append((files, hName, filt))

hName="MCTreePlot-TTTT-TriLepton-v0p4.root"
files=[preTTTT+file for file in basefiles]
filt=3
Tuples.append((files, hName, filt))

hName="MCTreePlot-TTTo2L2Nu-v0p4.root"
files=[preTT2L+file for file in basefiles]
filt=None
Tuples.append((files, hName, filt))

hName="MCTreePlot-TTTo2L2NuGF-v0p4.root"
files=[preTT2LGF+file for file in basefiles]
filt=None
Tuples.append((files, hName, filt))

hName="MCTreePlot-TTToSemiLeptonic-v0p4.root"
files=[preTT1L+file for file in basefiles]
filt=None
Tuples.append((files, hName, filt))

hName="MCTreePlot-TTToSemiLeptonicGF-v0p4.root"
files=[preTT1LGF+file for file in basefiles]
filt=None
Tuples.append((files, hName, filt))


def multiplier(fileList, hName=None, NLeps=None, maxevt=10000):
    if hName == None:
        hDirName = None
    else:
        hDirName = "plots"
    p=PostProcessor(".",
                    fileList,
                    modules=[MCTreePlot(maxevt=maxevt, filterNLeps=NLeps)],
                    noOut=True,
                    histFileName=hName,
                    histDirName=hDirName,
                   )
    p.run()

pList = []
for tup in Tuples:
    p = multiprocessing.Process(target=multiplier, args=(tup[0], tup[1], tup[2], 1000000))
    pList.append(p)
    p.start()

for p in pList:
    p.join()

    # for i, file in enumerate(tup[0]):
    #     print("file {0:d}: ".format(i+1) + str(file))
    # print("history file name: " + str(tup[1]))
    # print("Lepton Multiplicity Filter: {0:s}".format(str(tup[2])))
