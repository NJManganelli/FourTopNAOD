#!/usr/bin/env python
from __future__ import (division, print_function)
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from FourTopNAOD.Kai.modules.eventselector import *
from FourTopNAOD.Kai.tools.fileloader import FileLoader as IFL

preselection="nJet > 3 && (nMuon + nElectron) > 1"

# Y = IFL(eventSet="TTTT", era="2017", channel="DL") #Default, deltaR and CSVv2
# Y = IFL(eventSet="TTTT", era="2017", channel="DL", configName="PartonMatching")
# Y = IFL(eventSet="TTTT", era="2017", channel="DL", configName="DeepCSV")
# Y = IFL(eventSet="TTTT", era="2017", channel="DL", configName="PM+DCSV")
Y = IFL(eventSet="TTTT", era="2017", channel="DL", configName="kai0p2")
print(Y.getFiles(indexOfFile=0))
p=PostProcessor(".",
                Y.getFiles(indexOfFile=0),
                cut=preselection,
                branchsel=None,
                outputbranchsel=None,
                postfix="_" + Y.getSet() + "_runKai",
                jsonInput=Y.getJSONPath(),
                modules=[EventSelector(makeHistos=True, cutOnTrigs=False, cutOnMET=True, 
                                       cutOnHT=False, verbose=False, selectionConfig=Y.getConfig())],
                justcount=False,
                provenance=True,
#                fwkJobReport=True,
#                haddFileName="hadded.root",
                noOut=False,
                histFileName="hist" + Y.getSet() + "_runKai.root",
                histDirName="plots",
                compression="LZMA:9"
                )
for i in xrange(len(p.modules)):
    if hasattr(p.modules[i], "maxEventsToProcess"):
        p.modules[i].maxEventsToProcess=10000
p.run()
