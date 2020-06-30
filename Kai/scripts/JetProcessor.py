#!/bin/env python
import os, time, collections, copy, json, multiprocessing
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import * 
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import * 
from FourTopNAOD.Kai.tools.toolbox import *
import argparse
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='JetProcessor for adding btagSF and JECs to files and hadding them')
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
parser.add_argument('--runPeriod', dest='runPeriod', action='store', type=str, default=None, choices=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                    help='Run Period for data, i.e. "B" for 2017B')
parser.add_argument('--redoJEC', dest='redoJEC', action='store_true', default=False,
                    help='Do not rerun JECs when calculating jetmet uncertainties and smearing, it was broken as of writing!')
parser.add_argument('--isData', dest='isData', action='store_true', default=False,
                    help='Data vs MC boolean flag')
#Not necessary shape factors for both algos can be added with sequential modules
# parser.add_argument('--btagAlgo', dest='btagAlgo', action='store', type=str, default='deepcsv', choices=['csvv2', 'deepcsv', 'deepjet'],
#                     help='b tagging SF algorithm')
parser.add_argument('--btagWPs', dest='btagWPs', action='append', nargs='*', type=str, default=['shape_corr'], choices=['L', 'M', 'T', 'shape_corr'],
                    help='b tagging SF algorithm')
args = parser.parse_args()

moduleCache = []
jmeModule = createJMECorrector(isMC=(not args.isData), 
                               dataYear=int(args.era), 
                               runPeriod=args.runPeriod if args.isData else None, 
                               jesUncert="Total", 
                               redojec=args.redoJEC, 
                               jetType = "AK4PFchs", 
                               noGroom=False, 
                               metBranchName="METFixEE2017" if args.era == "2017" else "MET", 
                               applySmearing=True, 
                               isFastSim=False)
moduleCache.append(jmeModule())
if not args.isData:
    if args.era == "2017":
        moduleCache.append(btagSFProducer(args.era, 
                                          algo="csvv2", 
                                          # selectedWPs=['M', 'shape_corr'], 
                                          selectedWPs=['L', 'M', 'T', 'shape_corr'], 
                                          sfFileName=None, #Automatically deduced
                                          verbose=0, 
                                          jesSystsForShape=["jes"]
                                      )
                       )
    moduleCache.append(btagSFProducer(args.era, 
                                      algo="deepcsv", 
                                      # selectedWPs=['M', 'shape_corr'], 
                                      selectedWPs=['L', 'M', 'T', 'shape_corr'], 
                                      sfFileName=None, #Automatically deduced
                                      verbose=0, 
                                      jesSystsForShape=["jes"]
                                  )
                   )
    moduleCache.append(btagSFProducer(args.era, 
                                      algo="deepjet", 
                                      # selectedWPs=['M', 'shape_corr'], 
                                      selectedWPs=['L', 'M', 'T', 'shape_corr'], 
                                      sfFileName=None, #Automatically deduced
                                      verbose=0, 
                                      jesSystsForShape=["jes"]
                                  )
                   )
#Get files
files=getFiles(query="glob:{}".format(args.input))
if args.haddName == "":
    args.haddName = None
if args.maxEntries < 0:
    args.maxEntries = None
writeLocation = args.outDirectory
print("Will run over these files: {}".format(files))
print("Will use this output directory: {} \nWill use this haddName: {}\nWill use this postfix: {}\nWill configure with this year: {}{}"\
      .format(writeLocation, args.haddName, args.postfix, args.era, args.runPeriod if args.isData else ""))
if not args.isData:
    #print("Will configure the btagSFProducer using {}".format(args.btagAlgo))
    print("Will configure the btagSFProducer using {}".format("deepcsv, deepjet"))


p=PostProcessor(writeLocation, 
                files,
                modules=moduleCache, 
                cut=None, 
                jsonInput=None, 
                # histFileName="hist.root",
                # histDirName="plots",
                branchsel=None,
                outputbranchsel=None,
                # compression="LZMA:9",
                compression="ZLIB:3",
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
