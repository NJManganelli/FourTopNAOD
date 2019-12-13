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
parser.add_argument('--haddName', dest='haddName', action='store', type=str, default=""
                    help='output file name if haddnano is desired, default None')
parser.add_argument('--outDirectory', dest='outDirectory', action='store', type=str, default="."
                    help='output directory path defaulting to "."')
parser.add_argument('--postfix', dest='postfix', action='store', type=str, default="_LSF"
                    help='postfix for output files defaulting to "_LSF"')
parser.add_argument('--input', dest='input', action='store', type=str,
                    help='globbable input file name')
parser.add_argument('--year', dest='year', action='store', type=str, default="2017",
                    help='simulation/run year')
args = parser.parse_args()

Tuples = []
files=getFiles(query="glob:{}".format(args.input))
if args.haddName == "":
    haddName = None
else:
    haddName = args.haddName
writeLocation = args.outDirectory
postfix = args.postfix
if args.postfix == None:
#    writeLocation = "/tmp/nmangane/{}/".format(args.output.replace(".root", ""))
print("Will run over these files: {}".format(files))
print("Will use this output directory: {} \nWill use this haddName: {}\n Will use this postfix: {}\n Will configure with this year: {}"\
      .format(writeLocation, haddName, postfix, args.year))
p=PostProcessor(writeLocation,
                files,
                cut=None,
                modules=[lepSplitSFProducer(muon_ID="LooseID", muon_ISO="LooseRelIso/LooseID", 
                                            electron_ID="LooseID", year=args.year, doMuonHLT=True, 
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
