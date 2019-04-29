from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.modules.MCTreeDev import *
import collections, copy, json

#files=["TTJets_amcatnloFXFX.root"]
#files=["TTTT_HLT_PES_500HT.root"]
#files=["TTTo2L2Nu_Njet7_HLT_PES_500HT.root"]
#files=["TTTT_HLT.root"]
#files=["TTTo2L2Nu_Njet7_part.root"]

#No HLT applied, samples
#files=["../../AODStorage/TestingSamples/TTJets_TuneCP5_amcatnloFXFX_102X.root"]
#hName="treeHist-TTJets.root"
#files=["../../AODStorage/TestingSamples/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_102X.root"]
#hName="treeHist-TT2LGF.root"
#files=["../../AODStorage/TestingSamples/TTTo2L2Nu_TuneCP5_PSweights_102X.root"]
#hName="treeHist-TT2L.root"
#files=["../../AODStorage/TestingSamples/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_102X.root"]
#hName="treeHist-TT1LGF.root"
#files=["../../AODStorage/TestingSamples/ttHTobb_TuneCP5_102X.root"]
#hName="treeHist-TTH.root"
files=["~/eos/AODStorage/TestingSamples/TTTT_TuneCP5_PSweights_102X.root"]
hName="treeHist-TTTT-v3.root"

p=PostProcessor(".",
                files,
                cut=None,
                #modules=[MCTruth(maxevt=5000, probEvt=155325)],
                modules=[MCTruth(maxevt=10000)],
                noOut=True,
                histFileName=hName,
                histDirName="plots",
                #justcount=True,
                )

p.run()
