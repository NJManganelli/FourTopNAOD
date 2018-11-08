#!/usr/bin/env python
from __future__ import (division, print_function)
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from FourTopNAOD.Prototype.modules.eventselector import *
from FourTopNAOD.Prototype.modules.plotdqm import *
from FourTopNAOD.Prototype.tools.fileloader import FileLoader as IFL
#from FourTopNAOD.Prototype.modules.eventselector import *

preselection="nJet > 4 && (nMuon + nElectron) > 1"

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
                modules = [
        PlotDQM(title="Input", typeAK4="Jet", typeAK4_e=None, typeAK8="FatJet", typeElectron="Electron", typeMuon="Muon", 
                typeMET="MET", typeTrigger="HLT", doOSDL=True, doTopologyVariables=True, verbose=True, isLastModule=False),
        EventSelector(makeHistos=True, cutOnTrigs=False, cutOnMET=True, 
                                       cutOnHT=True, verbose=True, selectionConfig=Y.getConfig(), isLastModule=True),
        PlotDQM(title="Output", typeAK4="SelectedHeavyJet", typeAK4_e="SelectedLightJet", typeAK8="FatJet", typeElectron="SelectedElectron", 
                typeMuon="SelectedMuon", typeMET="MET", typeTrigger="HLT", doOSDL=True, doTopologyVariables=True, verbose=True, isLastModule=True)
        ],
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
