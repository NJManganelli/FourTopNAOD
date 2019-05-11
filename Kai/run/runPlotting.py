from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.modules.MCTreeDev import TenKTree
from FourTopNAOD.Kai.modules.MCTreePlot import MCTreePlot
import collections, copy, json

files=["tree_1.root", "tree_2.root", "tree_3.root", "tree_4.root", "tree_5.root", "tree_6.root"] 
preTTTT="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTTv2/results/"
preTT2L="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTo2L2Nu/results/"
preTT2LGF="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTTo2L2Nu_GenFilt/results/"
preTT1L="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTToSemiLeptonic/results/"
preTT1LGF="/eos/home-n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/crab_NanoGenTop_TTToSemiLeptonic_GenFilt/results/"


filt=None


hName="MCTreePlot-TTTT-v0p4.root"
files=[preTTTT+file for file in files]

# hName="MCTreePlot-TTTT-DiLepton.root"
# files=[preTTTT+file for file in files]
# filt=2

# hName="MCTreePlot-TTTT-TriLepton.root"
# files=[preTTTT+file for file in files]
# filt=3

# hName="MCTreePlot-TTTo2L2Nu.root"
# files=[preTT2L+file for file in files]

# hName="MCTreePlot-TTTo2L2NuGF.root"
# files=[preTT2LGF+file for file in files]

# hName="MCTreePlot-TTToSemiLeptonic.root"
# files=[preTT1L+file for file in files]

# hName="MCTreePlot-TTToSemiLeptonicGF.root"
# files=[preTT1LGF+file for file in files]



p=PostProcessor(".",
                files,
                cut=None,
                modules=[MCTreePlot(maxevt=10000, filterNLeps=filt)],
                noOut=True,
                histFileName=hName,
                histDirName="plots",
                )
p.run()
