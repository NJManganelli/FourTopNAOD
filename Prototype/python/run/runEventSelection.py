#!/usr/bin/env python
from __future__ import (division, print_function)
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from FourTopNAOD.Prototype.modules.eventselector import defaultEventSelector, loudEventSelector, showyEventSelector, EventSelector
#from FourTopNAOD.Prototype.modules.eventselector import *

preselection="nJet > 4 && (nMuon + nElectron) > 1"
#preselection="Jet_pt[1] > 250 && nJet > 3 && (nElectron > 0 || nMuon > 0)"
#files=[" root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAOD/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/40000/2CE738F9-C212-E811-BD0E-EC0D9A8222CE.root"]
files=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAOD/TTJets_SingleLeptFromT_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/00000/06CC0D9B-4244-E811-8B62-485B39897212.root"]
p=PostProcessor(".",
                files,
                cut=preselection,
                branchsel=None,
                outputbranchsel=None,
                postfix="_PostEvtSel",
                jsonInput=None,
#                jsonInput={1 : [[10000, 19000]]},
                modules=[EventSelector(makeHistos=True, cutOnTrigs=False, cutOnMET=True, cutOnHT=True, verbose=False)],
#                modules=[showyEventSelector()],
                justcount=False,
                provenance=True,
                fwkJobReport=True,
                haddFileName="hadded.root",
                noOut=False,
                histFileName="histOut.root",
                histDirName="plots",
                compression="LZMA:9"
                )
p.run()
