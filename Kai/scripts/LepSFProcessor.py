from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from FourTopNAOD.Kai.modules.lepSplitSFProducer import *
from FourTopNAOD.Kai.tools.toolbox import *
import collections, copy, json, math
from array import array
import multiprocessing
import inspect
import argparse
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='LepSFProcessor for adding LepSF to files and hadding them')
parser.add_argument('input', action='store', type=str,
                    help='globbable input file name')
parser.add_argument('--haddName', dest='haddName', action='store', type=str, default="",
                    help='output file name if haddnano is desired, default None')
parser.add_argument('--outDirectory', dest='outDirectory', action='store', type=str, default=".",
                    help='output directory path defaulting to "."')
parser.add_argument('--postfix', dest='postfix', action='store', type=str, default="_LSF",
                    help='postfix for output files defaulting to "_LSF"')
parser.add_argument('--year', dest='year', action='store', type=str, default="2017",
                    help='simulation/run year')
parser.add_argument('--maxEntries', dest='maxEntries', action='store', type=int, default=-1,
                    help='maxEntries per file for processing')
parser.add_argument('--muon_ID', dest='muon_ID', action='store', type=str, default="LooseID",
                    help='Muon ID for ScaleFactor insertion. See lepSpitSFProducer.py module for options')
parser.add_argument('--muon_ISO', dest='muon_ISO', action='store', type=str, default="LooseRelIso/LooseID",
                    help='Muon ISO for ScaleFactor insertion. See lepSpitSFProducer.py module for options')
parser.add_argument('--electron_ID', dest='electron_ID', action='store', type=str, default="LooseID",
                    help='Electron ID for ScaleFactor insertion. See lepSpitSFProducer.py module for options')
args = parser.parse_args()

Tuples = []
files=getFiles(query="glob:{}".format(args.input))
if args.haddName == "":
    args.haddName = None
# else:
#     haddName = args.haddName
if args.maxEntries < 0:
    args.maxEntries = None
writeLocation = args.outDirectory
print("Will run over these files: {}".format(files))
print("Will use this output directory: {} \nWill use this haddName: {}\nWill use this postfix: {}\nWill configure with this year: {}"\
      .format(writeLocation, args.haddName, args.postfix, args.year))
print("Will use this muon ID: {}\nWill use this Muon ISO: {}\nWill use this Electron ID: {}".format(args.muon_ID, args.muon_ISO, args.electron_ID))
p=PostProcessor(writeLocation,
                files,
                cut=None,
                modules=[lepSplitSFProducer(muon_ID=args.muon_ID, muon_ISO=args.muon_ISO, 
                                            electron_ID=args.electron_ID, year=args.year, 
                                            doMuonHLT=True, doElectronHLT_ZVtx=True, debug=False)],
                noOut=False,
                postfix=args.postfix,
                haddFileName=args.haddName,
                maxEntries=args.maxEntries,
                # histFileName=hName,
                # histDirName=hDirName,
)
print("Wrote outputs in: {}".format(args.outDirectory))
p.run()
