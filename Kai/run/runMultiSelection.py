from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
from FourTopNAOD.Kai.modules.BaselineSelector import BaselineSelector
from FourTopNAOD.Kai.modules.MCTreePlot import MCTreePlot
from FourTopNAOD.Kai.modules.trigger import Trigger
import collections, copy, json
import multiprocessing
import os, time

triggers=["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
          "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
          "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
          "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
          "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"
          ]


Tuples=[]

#basefiles=["tree_1.root", "tree_2.root", "tree_3.root", "tree_4.root", "tree_5.root", "tree_6.root"] 
basefiles=["tree_2.root"] 
#extfiles=["tree_7.root", "tree_8.root", "tree_9.root", "tree_10.root", "tree_11.root", "tree_12.root"] 
extfiles=[]
preTTTT="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTTv2/results/"
preTTTT16="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTT_2016/results/"
preTTTT18="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTT_2018/results/"
preTT2L="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTo2L2Nu/results/"
preTT2LGF="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTo2L2Nu_GenFilt/results/"
preTT1L="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTToSemiLeptonic/results/"
preTT1LGF="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTToSemiLeptonic_GenFilt/results/"



# hName="BES-TTTT16-DiLepton-v1p7.root"
# files=[preTTTT16+file for file in basefiles]
# filt=2
# Tuples.append((files, hName, filt))

# hName="BES-TTTT18-DiLepton-v1p7.root"
# files=[preTTTT18+file for file in basefiles]
# filt=2
# Tuples.append((files, hName, filt))

hName="BES-TTTT-v1p7.root"
files=[preTTTT+file for file in basefiles]
filt=None
# Tuples.append((files, "B1_"+hName, filt, ["2017", "NONE"], ["CSVv2", "M"], [False, 41.53, 0.012, 2273928]))
# Tuples.append((files, "B2_"+hName, filt, ["2017", "NONE"], ["DeepCSV", "M"], [False, 41.53, 0.012, 2273928]))
# Tuples.append((files, "B3_"+hName, filt, ["2017", "NONE"], ["DeepJet", "M"], [False, 41.53, 0.012, 2273928]))
Tuples.append((files, "B1_"+hName, filt, ["2017", "NONE"], ["CSVv2", "M"], [False, 41.53, 0.012, 85136, 706.75]))
# Tuples.append((files, "B2_"+hName, filt, ["2017", "NONE"], ["DeepCSV", "M"], [False, 41.53, 0.012, 85136]))
# Tuples.append((files, "B3_"+hName, filt, ["2017", "NONE"], ["DeepJet", "M"], [False, 41.53, 0.012, 85136]))

# hName="BES-TTTT-SingleLepton-v1p7.root"
# files=[preTTTT+file for file in basefiles]
# filt=1
# Tuples.append((files, hName, filt))

# hName="BES-TTTT-DiLepton-v1p7.root"
# files=[preTTTT+file for file in basefiles]
# filt=2
# Tuples.append((files, hName, filt))

# hName="BES-TTTT-TriLepton-v1p7.root"
# files=[preTTTT+file for file in basefiles]
# filt=3
# Tuples.append((files, hName, filt))

hName="BES-TTTo2L2Nu-v1p7.root"
files=[preTT2L+file for file in basefiles + extfiles]
filt=None
#Tuples.append((files, hName, filt))
Tuples.append((files, "B1_"+hName, filt, ["2017", "NONE"], ["CSVv2", "M"], [False, 41.53, 88.341, 1098554, 79184700]))
# Tuples.append((files, "B2_"+hName, filt, ["2017", "NONE"], ["DeepCSV", "M"], [False, 41.53, 88.341, 1098554]))
# Tuples.append((files, "B3_"+hName, filt, ["2017", "NONE"], ["DeepJet", "M"], [False, 41.53, 88.341, 1098554]))


# hName="BES-TTTo2L2NuGF-v1p7.root"
# files=[preTT2LGF+file for file in basefiles + extfiles]
# filt=None
# Tuples.append((files, hName, filt))

# hName="BES-TTToSemiLeptonic-v1p7.root"
# files=[preTT1L+file for file in basefiles + extfiles]
# filt=None
# Tuples.append((files, hName, filt))

# hName="BES-TTToSemiLeptonicGF-v1p7.root"
# files=[preTT1LGF+file for file in basefiles + extfiles]
# filt=None
# Tuples.append((files, hName, filt))

### Data JECs - Data only, below option for MC JECs + smearing. What about typeI MET correction? Also optional in these modules...
# jetRecalib2017B = lambda : jetRecalib("Fall17_17Nov2017B_V32_DATA","Fall17_17Nov2017_V32_DATA")
# jetRecalib2017C = lambda : jetRecalib("Fall17_17Nov2017C_V32_DATA","Fall17_17Nov2017_V32_DATA")
# jetRecalib2017DE = lambda : jetRecalib("Fall17_17Nov2017DE_V32_DATA","Fall17_17Nov2017_V32_DATA")
# jetRecalib2017F = lambda : jetRecalib("Fall17_17Nov2017F_V32_DATA","Fall17_17Nov2017_V32_DATA")

### MC JECs + JER smearing - MC only
# jetmetUncertainties2017 = lambda : jetmetUncertaintiesProducer("2017", "Fall17_17Nov2017_V32_MC", [ "Total" ])
# jetmetUncertainties2017All = lambda : jetmetUncertaintiesProducer("2017", "Fall17_17Nov2017_V32_MC", [ "All" ], redoJEC=True)

### Prefire Corrector - MC Only, presumably
# PrefCorr(jetroot="L1prefiring_jetpt_2017BtoF.root", jetmapname="L1prefiring_jetpt_2017BtoF",
#           photonroot="L1prefiring_photonpt_2017BtoF.root", photonmapname="L1prefiring_photonpt_2017BtoF")

def multiplier(fileList, hName=None, NLeps=None, theEra=["2017", "NONE"], theBTagger=['CSVv2','M'], evtConfig=[True, 1, 1, 1, 1], maxevt=-1): #evtConfig=[isData, genEquivalentLuminosity, genXS, genNEvents]
    if hName == None:
        hDirName = None
    else:
        hName = hName
        hDirName = "plots"
        modulesMC=[puWeightProducer("auto",
                                    pufile_data2017,
                                    "pu_mc",
                                    "pileup",
                                    verbose=False
                                ),
                   Trigger(triggers),
                   jetmetUncertaintiesProducer("2017", 
                                               "Fall17_17Nov2017_V32_MC", 
                                               [ "All" ], 
                                               redoJEC=True
                                           ),
                   btagSFProducer(theEra[0], algo=theBTagger[0]),
                   BaselineSelector(maxevt=maxevt, 
                                    probEvt=None,
                                    isData=evtConfig[0],
                                    genEquivalentLuminosity=evtConfig[1],
                                    genXS=evtConfig[2],
                                    genNEvents=evtConfig[3],
                                    genSumWeights=evtConfig[4],
                                    era=theEra[0],
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
               ]
        dataRecalib = {'2017': 
                       {'B': jetRecalib("Fall17_17Nov2017B_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                        'C': jetRecalib("Fall17_17Nov2017C_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                        'D': jetRecalib("Fall17_17Nov2017DE_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                        'E': jetRecalib("Fall17_17Nov2017DE_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                        'F': jetRecalib("Fall17_17Nov2017F_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                        'NONE': 'NothingToSeeHere'
                        }
                   }
        modulesData=[Trigger(triggers),
                     dataRecalib[theEra[0]][theEra[1]],
                     BaselineSelector(maxevt=maxevt, 
                                      probEvt=None,
                                      isData=evtConfig[0],
                                      genEquivalentLuminosity=evtConfig[1],
                                      genXS=evtConfig[2],
                                      genNEvents=evtConfig[3],
                                      era=theEra[0],
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
                 ]
    if evtConfig[0] == True:
        theModules=modulesData
    else:
        theModules=modulesMC
    p=PostProcessor("/tmp/nmangane", #"./"+theEra+"/"+theBTagger[0],
                    fileList,
                    modules=theModules,
                    noOut=False,
                    postfix=hName,
                    haddFileName="Tree_"+hName,
                    histFileName=hName,
                    histDirName=hDirName,
                   )
    p.run()

pList = []
for tup in Tuples:
    p = multiprocessing.Process(target=multiplier, args=(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], 80000))
    pList.append(p)
    p.start()

for p in pList:
    p.join()

    # for i, file in enumerate(tup[0]):
    #     print("file {0:d}: ".format(i+1) + str(file))
    # print("history file name: " + str(tup[1]))
    # print("Lepton Multiplicity Filter: {0:s}".format(str(tup[2])))
