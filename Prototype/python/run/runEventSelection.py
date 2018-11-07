#!/usr/bin/env python
from __future__ import (division, print_function)
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from FourTopNAOD.Prototype.modules.eventselector import *
from FourTopNAOD.Prototype.tools.fileloader import FileLoader as IFL
#from FourTopNAOD.Prototype.modules.eventselector import *

preselection="nJet > 4 && (nMuon + nElectron) > 1"

Y = IFL(eventSet="TTTT", era="2017", channel="DL")
print(Y.getFiles(indexOfFile=0))
p=PostProcessor(".",
                Y.getFiles(indexOfFile=0),
                cut=preselection,
                branchsel=None,
                outputbranchsel=None,
                postfix="_" + Y.getSet() + "_PostEvtSel",
                jsonInput=Y.getJSONPath(),
                modules=[EventSelector(makeHistos=True, cutOnTrigs=True, cutOnMET=True, 
                                       cutOnHT=True, verbose=False, selectionConfig=Y.getConfig())],
                justcount=False,
                provenance=True,
#                fwkJobReport=True,
#                haddFileName="hadded.root",
                noOut=False,
                histFileName="hist" + Y.getSet() + ".root",
                histDirName="plots",
                compression="LZMA:9"
                )
for i in xrange(len(p.modules)):
    if p.modules[i].maxEventsToProcess:
        p.modules[i].maxEventsToProcess=1000
p.run()
