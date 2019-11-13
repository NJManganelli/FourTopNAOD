from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.common.lepSplitSFProducer import *
from FourTopNAOD.Kai.tools.toolbox import *
import collections, copy, json, math
from array import array
import multiprocessing
import inspect
import argparse
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='LepSFProcessor for adding LepSF to files and hadding them')
parser.add_argument('--output', dest='output', action='store', type=str,
                    help='output file name')
parser.add_argument('--input', dest='input', action='store', type=str,
                    help='globbable input file name')
parser.add_argument('--era', dest='era', action='store', type=str, default="2017",
                    help='era (year)')
args = parser.parse_args()

Tuples = []
files=getFiles(query="glob:{}".format(args.input))
output = "{}".format(args.output)
if ".root" not in output:
    output += ".root"
p=PostProcessor("/tmp/nmangane/{}/".format(args.output.replace(".root", "")),
                files,
                cut=None,
                modules=[lepSplitSFProducer(muon_ID="LooseID", muon_ISO="LooseRelIso/LooseID", 
                                            electron_ID="LooseID", era=args.era, doMuonHLT=True, 
                                            doElectronHLT_ZVtx=True, debug=False)],
                noOut=False,
                # postfix="_"+era+"_"+muID+"_"+muISO.replace("/","@")+"_"+elID,
                haddFileName=output,
                maxEntries=None,
                # histFileName=hName,
                # histDirName=hDirName,
)
print(files)
print("{}".format(args.output))
p.run()
