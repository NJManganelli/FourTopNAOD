#!/usr/bin/env python
from __future__ import (division, print_function)
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from FourTopNAOD.Prototype.modules.eventselector import *
from FourTopNAOD.Prototype.modules.plotdqm import *
from FourTopNAOD.Prototype.tools.fileloader import FileLoader
#from FourTopNAOD.Prototype.modules.eventselector import *

#preselection="nJet > 4 && (nMuon + nElectron) > 1"
preselection=None
InputClass = FileLoader(eventSet="TTTT", era="2017", channel="DL")
print(InputClass.getFiles(indexOfFile=0))
p=PostProcessor(".",
                InputClass.getFiles(indexOfFile=0),
                cut=preselection,
                branchsel=None,
                outputbranchsel=None,
                postfix="_" + InputClass.getSet() + "_PlotDQM",
                jsonInput=InputClass.getJSONPath(),
#                modules=[EventSelector(makeHistos=True, cutOnTrigs=True, cutOnMET=True, 
#                                       cutOnHT=True, verbose=False, selectionConfig=InputClass.getConfig())],
#                modules=[PlotDQM(title="Test",typeAK4="Jet", typeAK8=None, typeElectron="Electron", typeMuon="Muon", typeMET=None, typeTrigger=None, doOSDL=False)],
#                modules=[TestDQM()],
                modules=[TestInput(), TestMiddle(), TestOutput()],
                justcount=False,
                provenance=True,
#                fwkJobReport=True,
#                haddFileName="hadded.root",
                noOut=True,
                histFileName="hist" + InputClass.getSet() + "_runDQM.root",
                histDirName="plots",
                compression="LZMA:9"
                )
for i in xrange(len(p.modules)):
    if p.modules[i].maxEventsToProcess:
        p.modules[i].maxEventsToProcess=1000
p.run()
