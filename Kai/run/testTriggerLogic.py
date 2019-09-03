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
# for tup in Tuples:
#     print(tup)
if args.stage == 'test':
    Mods = []
    for tup in Tuples:
        Mods.append(TriggerAndSelectionLogic(era=tup[0], subera=tup[1], isData=tup[2], TriggerChannel=tup[3]))
    # for mod in Mods:
    #     print(mod.getCutString())
