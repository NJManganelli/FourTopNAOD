#!/usr/bin/env python
import os, time, collections, copy, json, multiprocessing
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from FourTopNAOD.Kai.modules.WeightInserter import WeightInserter
from FourTopNAOD.Kai.modules.HistCloser import HistCloser
from FourTopNAOD.Kai.tools.toolbox import *
import argparse
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='LepSFProcessor for adding LepSF to files and hadding them')
parser.add_argument('input', action='store', type=str,
                    help='globbable input file name')
parser.add_argument('--haddName', dest='haddName', action='store', type=str, default="",
                    help='output file name if haddnano is desired, default None')
parser.add_argument('--outDirectory', dest='outDirectory', action='store', type=str, default=".",
                    help='output directory path defaulting to "."')
parser.add_argument('--postfix', dest='postfix', action='store', type=str, default="_Stitched",
                    help='postfix for output files defaulting to "_Stitched"')
parser.add_argument('--era', dest='era', action='store', type=str, default="2017", choices=['2016', '2017', '2018'],
                    help='simulation/run year')
parser.add_argument('--maxEntries', dest='maxEntries', action='store', type=int, default=-1,
                    help='maxEntries per file for processing')
parser.add_argument('--weight', dest='weight', action='store', type=float, default=1,
                    help='magnitude of weight/genWeight (genWeight acquired per event), as in calculation: N_effective = process_cross_section * Luminosity * genWeight/SUM(genWeights)')
parser.add_argument('--cut', dest='cut', action='store', type=str, default=None,
                    help='Cut string to pre-process the events tree, greatly reducing processing time')
args = parser.parse_args()

#Example calculation of weight magnitude
# crossSection = 1.4705 #pb
# equivLumi = 41.53 #/fb
# sumWeights = 612101836.284 #for NanoAOD, stored in the Runs tree
# weight = crossSection * equivLumi * 1000 / sumWeights #include conversion of pb to fb

moduleCache = []
moduleCache.append(WeightInserter(weightMagnitude=args.weight,))
moduleCache.append(HistCloser())
#Get files
files=getFiles(query="glob:{}".format(args.input))
if args.haddName == "":
    args.haddName = None
if args.maxEntries < 0:
    args.maxEntries = None
writeLocation = args.outDirectory
print("Will run over these files: {}".format(files))
print("Will use this output directory: {} \nWill use this haddName: {}\nWill use this postfix: {}"\
      .format(writeLocation, args.haddName, args.postfix))


p=PostProcessor(writeLocation, 
                files,
                modules=moduleCache, 
                cut=args.cut, 
                jsonInput=None, 
                histFileName="hist.root",
                histDirName="plots",
                branchsel=None,
                outputbranchsel=None,
                compression="LZMA:9",
                friend=False,
                postfix=args.postfix,
                noOut=False,
                justcount=False,
                haddFileName=args.haddName,
                maxEntries=args.maxEntries,
                firstEntry=0,
                prefetch=False,
                longTermCache=False
                )
p.run()
print("Wrote outputs in: {}".format(args.outDirectory))
