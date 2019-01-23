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

#preselection="nJet > 4 && (nMuon + nElectron) > 1"
preselection=None

# Y = IFL(eventSet="TTTT", era="2017", channel="DL") #Default, deltaR and CSVv2
# Y = IFL(eventSet="TTTT", era="2017", channel="DL", configName="PartonMatching")
# Y = IFL(eventSet="TTTT", era="2017", channel="DL", configName="DeepCSV")
Y = IFL(eventSet="TTTT", era="2017", channel="DL", configName="PM+DCSV")
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
                histFileName="hist" + Y.getSet() + "_runEventSelection.root",
                histDirName="plots",
                compression="LZMA:9"
                )
for i in xrange(len(p.modules)):
    if hasattr(p.modules[i], "maxEventsToProcess"):
        p.modules[i].maxEventsToProcess=30000
p.run()
