from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from FourTopNAOD.Kai.modules.trigger import TriggerAndSelectionLogic
import argparse
# import collections, copy, json, math
# from array import array
# import multiprocessing
# import inspect
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='Test of TriggerAndSelectionLogic Module and post-selection variables')
parser.add_argument('--stage', dest='stage', action='store', type=str,
                    help='Stage to be processed: test or process')
parser.add_argument('--era', dest='era', action='store', type=str, default=None,
                    help='Era to be processed: 2017 or 2018')
parser.add_argument('--subera', dest='subera', action='store', type=str, default=None,
                    help='Subera to be processed: A, B, C, D, E, F (year dependant)')
args = parser.parse_args()

Tuples = []
Tuples.append(("2017", None, False, None))
Tuples.append(("2017", "B", True, "ElMu"))
Tuples.append(("2017", "C", True, "ElMu"))
Tuples.append(("2017", "D", True, "ElMu"))
Tuples.append(("2017", "E", True, "ElMu"))
Tuples.append(("2017", "F", True, "ElMu"))
Tuples.append(("2017", "B", True, "MuMu"))
Tuples.append(("2017", "C", True, "MuMu"))
Tuples.append(("2017", "D", True, "MuMu"))
Tuples.append(("2017", "E", True, "MuMu"))
Tuples.append(("2017", "F", True, "MuMu"))
Tuples.append(("2017", "B", True, "ElEl"))
Tuples.append(("2017", "C", True, "ElEl"))
Tuples.append(("2017", "D", True, "ElEl"))
Tuples.append(("2017", "E", True, "ElEl"))
Tuples.append(("2017", "F", True, "ElEl"))
Tuples.append(("2017", "B", True, "Mu"))
Tuples.append(("2017", "C", True, "Mu"))
Tuples.append(("2017", "D", True, "Mu"))
Tuples.append(("2017", "E", True, "Mu"))
Tuples.append(("2017", "F", True, "Mu"))
Tuples.append(("2017", "B", True, "El"))
Tuples.append(("2017", "C", True, "El"))
Tuples.append(("2017", "D", True, "El"))
Tuples.append(("2017", "E", True, "El"))
Tuples.append(("2017", "F", True, "El"))

Tuples.append(("2018", None, False, None))
Tuples.append(("2018", "A", True, "ElMu"))
Tuples.append(("2018", "B", True, "ElMu"))
Tuples.append(("2018", "C", True, "ElMu"))
Tuples.append(("2018", "D", True, "ElMu"))
Tuples.append(("2018", "A", True, "MuMu"))
Tuples.append(("2018", "B", True, "MuMu"))
Tuples.append(("2018", "C", True, "MuMu"))
Tuples.append(("2018", "D", True, "MuMu"))
Tuples.append(("2018", "A", True, "ElEl"))
Tuples.append(("2018", "B", True, "ElEl"))
Tuples.append(("2018", "C", True, "ElEl"))
Tuples.append(("2018", "D", True, "ElEl"))
Tuples.append(("2018", "A", True, "Mu"))
Tuples.append(("2018", "B", True, "Mu"))
Tuples.append(("2018", "C", True, "Mu"))
Tuples.append(("2018", "D", True, "Mu"))
Tuples.append(("2018", "A", True, "El"))
Tuples.append(("2018", "B", True, "El"))
Tuples.append(("2018", "C", True, "El"))
Tuples.append(("2018", "D", True, "El"))

if args.era:
    Tuples = [tup for tup in Tuples if tup[0] == args.era]
if args.subera:
    Tuples = [tup for tup in Tuples if tup[1] == args.subera]

Tuples.sort(key=lambda j : j[1]) #sort by subera
Tuples.sort(key=lambda j : j[0]) #then by era, again
# for tup in Tuples:
#     print(tup)
if args.stage == 'test':
    Mods = []
    for tup in Tuples:
        Mods.append(TriggerAndSelectionLogic(era=tup[0], subera=tup[1], isData=tup[2], TriggerChannel=tup[3]))
    for mod in Mods:
        print(mod.getCutString())

elif args.stage == 'cutstring':
    tuple_file = "anotherDirectory/variety_pack_tuples_2017_NANOv5.txt"
    with open(tuple_file, "r") as in_f:
        for l, line in enumerate(in_f):
            # if l > 0: 
            #     continue

            cline = line.rstrip("\n\s\t")
            tup = cline.split(",") #0 filename, 1 era, 2 subera, 3 isData, 4 isSignal, 5 nEvents, 6 nEvents+, 7 nEvents-, 8 crossSection, 9 channel
            # for t in tup: print(t)
            files = [tup[0]]
            era = tup[1]
            subera = tup[2]
            isData = tup[3]
            isSignal = tup[4]
            nEvents = int(tup[5])
            try:
                nEventsPositive = int(tup[6])
                nEventsNegative = int(tup[7])
            except:
                nEventsPositive = 0
                nEventsNegative = 0
            crossSection = float(tup[8])
            channel = tup[9]

            if isData in ["True", "TRUE", "true"]:
                isData = True
            else:
                isData = False
            if isSignal in ["True", "TRUE", "true"]:
                isSignal = True
            else:
                isSignal = False
            if channel not in ["ElMu", "MuMu", "ElEl", "Mu", "El"]:
                # print("converting channel {} to None".format(channel))
                channel = None
            if era == "2017":
                lumi = 41.53
            elif era == "2018":
                lumi = 60 #rough estimate
            else:
                lumi = 1

            if not isData:
                if nEventsNegative > 0 and nEventsPositive > 0:
                    weight = lumi * 1000 * crossSection / (nEventsPositive - nEventsNegative)
                else:
                    weight = lumi * 1000 * crossSection / nEvents
                subera = None
            else:
                weight = 1
            # print("era= {}\t subera={}\t isData={}\t TriggerChannel={}\t weight={}".format(era, subera, str(isData), channel, weight))
            modules = [TriggerAndSelectionLogic(era=era, subera=subera, isData=isData, TriggerChannel=channel, weightMagnitude=weight)]
            # print(modules[0].getCutString())
            p = PostProcessor(".",
                              files,
                              cut=modules[0].getCutString(),
                              # cut=None,
                              branchsel=None,
                              modules=modules,
                              compression="LZMA:9",
                              friend=False,
                              postfix=None,
                              jsonInput=None,
                              noOut=True,
                              # noOut=False,
                              justcount=True,
                              # justcount=False,
                              provenance=False,
                              haddFileName=None,
                              fwkJobReport=False,
                              histFileName=None,
                              histDirName=None, 
                              outputbranchsel=None,
                              maxEntries=None,
                              firstEntry=0,
                              prefetch=False,
                              longTermCache=False
            )
            p.run()
