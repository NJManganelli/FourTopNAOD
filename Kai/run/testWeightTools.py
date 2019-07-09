from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.toolbox import *
from FourTopNAOD.Kai.tools.mctree import *
import collections, copy, json

#files=["TTJets_amcatnloFXFX.root"]
#files=["TTTT_HLT_PES_500HT.root"]
#files=["TTTo2L2Nu_Njet7_HLT_PES_500HT.root"]
#files=["TTTT_HLT.root"]
#files=["TTTo2L2Nu_Njet7_part.root"]

#No HLT applied, samples
#files=["~/eos/AODStorage/TestingSamples/TTJets_TuneCP5_amcatnloFXFX_102X.root"]
#hName="WTT-TTJets.root"
#files=["~/eos/AODStorage/TestingSamples/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_102X.root"]
#hName="WTT-TT2LGF.root"
#files=["~/eos/AODStorage/TestingSamples/TTTo2L2Nu_TuneCP5_PSweights_102X.root"]
#hName="WTT-TT2L.root"
#files=["~/eos/AODStorage/TestingSamples/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_102X.root"]
#hName="WTT-TT1LGF.root"
#files=["~/eos/AODStorage/TestingSamples/ttHTobb_TuneCP5_102X.root"]
#hName="WTT-TTH.root"
files=["~/eos/AODStorage/TestingSamples/TTTT_TuneCP5_PSweights_102X.root"]
hName="WTT-TTTT.root"

p=PostProcessor(".", #The output Directory and files list must appear in the same places every time
                files,
                cut=None,
                #modules=[MCTruth(maxevt=5000, probEvt=155325)],
                modules=[puWeightProducer("auto",pufile_data2017,"pu_mc","pileup",verbose=True)],
                         #WeightToolTester(maxevt=1000, subname=S2)
                         #],
                #modules=[]
                noOut=False,
                histFileName=hName,
                histDirName="plots",
                #justcount=True,
                )

p.run()
