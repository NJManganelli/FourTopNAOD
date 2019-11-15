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
parser.add_argument('--outDirectory', dest='outDirectory', action='store', type=str,
                    help='output directory path for usage with postfix option')
parser.add_argument('--postfix', dest='postfix', action='store', type=str,
                    help='postfix file name, which will also store the files in the same directory as they were input from')
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
if args.postfix == None:
    writeLocation = "/tmp/nmangane/{}/".format(args.output.replace(".root", ""))
    haddName = output
    postfix = None
else:
    writeLocation = args.outDirectory
    haddName = None
    postfix = "_LSF"
print("Will run over these files: {}".format(files))
print("Will use this output directory: {} \nWill use this haddName: {}\n Will use this postfix: {}".format(writeLocation, haddName, postfix))
p=PostProcessor(writeLocation,
                files,
                cut=None,
                modules=[lepSplitSFProducer(muon_ID="LooseID", muon_ISO="LooseRelIso/LooseID", 
                                            electron_ID="LooseID", era=args.era, doMuonHLT=True, 
                                            doElectronHLT_ZVtx=True, debug=False)],
                noOut=False,
                postfix=postfix,
                haddFileName=haddName,
                maxEntries=None,
                # histFileName=hName,
                # histDirName=hDirName,
)
print("The output: {}".format(args.output))
p.run()
