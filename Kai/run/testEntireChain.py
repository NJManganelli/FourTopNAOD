from __future__ import division, print_function

import os, sys, subprocess
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
from FourTopNAOD.Kai.modules.LeptonLogic import TriggerAndLeptonLogic
from FourTopNAOD.Kai.modules.JetMETLogic import JetMETLogic
from FourTopNAOD.Kai.modules.Stitcher import Stitcher
from FourTopNAOD.Kai.modules.HistCloser import HistCloser
import argparse
# import collections, copy, json, math
# from array import array
# import multiprocessing
# import inspect

####Old list from Nanovisor V1 baseline generation
# import os, time, collections, copy, json, multiprocessing
# from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *
# from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis
# from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
# from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
# from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
# from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
# from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
# from FourTopNAOD.Kai.modules.BaselineSelector import BaselineSelector
# from FourTopNAOD.Kai.modules.trigger import Trigger
# from FourTopNAOD.Kai.modules.MCTreeDev import MCTrees


parser = argparse.ArgumentParser(description='Test of entire chain of production')
parser.add_argument('--stage', dest='stage', action='store', type=str,
                    help='Stage to be processed: test or cache or correct or cutstring or process or combined or hist')
parser.add_argument('--era', dest='era', action='store', type=str, default=None,
                    help='Era to be processed: 2017 or 2018')
parser.add_argument('--subera', dest='subera', action='store', type=str, default=None,
                    help='Subera to be processed: A, B, C, D, E, F (year dependant)')
parser.add_argument('--rmin', dest='rmin', action='store', type=int, default=0,
                    help='inclusive range minimum (samples start counting at 0; default is 0)')
parser.add_argument('--rmax', dest='rmax', action='store', type=int, default=99999,
                    help='inclusive range maximum (samples start counting at 0; default is 99999)')
args = parser.parse_args()



#### Trigger tuples, not strictly necessary in this file
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

#### Dictionary for the data jetrecalibrator
dataRecalib = {"2017": {"B": jetRecalib("Fall17_17Nov2017B_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                          "C": jetRecalib("Fall17_17Nov2017C_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                          "D": jetRecalib("Fall17_17Nov2017DE_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                          "E": jetRecalib("Fall17_17Nov2017DE_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                          "F": jetRecalib("Fall17_17Nov2017F_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                          "NONE": "NothingToSeeHere"
                      }
            }

#Test the module initialization and cutstrings produced
if args.stage == 'test':
    Mods = []
    for tup in Tuples:
        Mods.append(JetMETLogic('baseline', era=tup[0], subera=tup[1], isData=tup[2], TriggerChannel=tup[3]))
    for mod in Mods:
        print(mod.getCutString())

#Cache files locally from a variety_pack_tuple, because remote files are wasting my time
elif args.stage == 'cache':
    tuple_file = "dirtestTriggerLogic/variety_pack_tuples_2017_NANOv5.txt"
    local_tuple_file = "dirtestTriggerLogic/local_variety_pack_tuples_2017_NANOv5.txt"
    files_to_cache = []
    file_names = []
    local_tuple_lines = []
    with open(tuple_file, "r") as in_f:
        for l, line in enumerate(in_f):
            #Don't clean line, going to write back with file name replacement
            tup = line.split(",")
            files_to_cache.append(tup[0])
            #Fuck wasting more time on this, numerology it is
            file_names.append("dirtestTriggerLogic/file_{}.root".format(str(l)))
            local_tuple_lines.append(line.replace(files_to_cache[-1], file_names[-1]))

    xrd_list = zip(files_to_cache, file_names)

    with open(local_tuple_file, "w") as out_f:
        for line in local_tuple_lines:
            out_f.write(line)

    # subprocess.Popen(args="voms-proxy-info", shell=True, executable="/bin/zsh", env=dict(os.environ))
    # subprocess.Popen(args="print $PWD", shell=True, executable="/bin/zsh", env=dict(os.environ))
    for file_original, file_local in xrd_list:
        pass
        # os.system("echo xrdcp {} {}".format(file_original, file_local))
        # subprocess.Popen(args="xrdcp {} {}".format(file_original, file_local), shell=True, executable="/bin/zsh", env=dict(os.environ))
        #Call subprocess such that the script waits for it to finish. Otherwise, the script continues and can finish while subprocesses run in the background, and output will get muxed a bit. Useful, however, for interacting with shell while something runs!
        subprocess.Popen(args="xrdcp {} {}".format(file_original, file_local), shell=True, executable="/bin/zsh", env=dict(os.environ)).wait()

#Test the counts from using the cutstrings
elif args.stage == 'cutstring':
    local_tuple_file = "dirtestTriggerLogic/local_variety_pack_tuples_2017_NANOv5.txt"
    with open(local_tuple_file, "r") as in_f:
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

            #Skip choices if requested, only with explicit parameter choice
            if args.era and era != args.era:
                continue
            if args.subera and subera != args.subera:
                continue


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
            modules = [JetMETLogic('baseline', era=era, subera=subera, isData=isData,  weightMagnitude=weight)]
            # print(modules[0].getCutString())
            p = PostProcessor(".",
                              files,
                              cut=modules[0].getCutString(),
                              # cut=None,
                              branchsel=None,
                              modules=modules,
                              compression="LZMA:9",
                              friend=False,
                              postfix="_Chain",
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
                              # prefetch=False,
                              prefetch=True,
                              longTermCache=False
            )
            p.run()
#Get the real number of events, +, - from the files, to do quicker studies
elif args.stage == 'correct':
    local_tuple_file = "dirtestTriggerLogic/local_variety_pack_tuples_2017_NANOv5.txt"
    corrected_lines = []
    with open(local_tuple_file, "r") as in_f:
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

            #Skip choices if requested, only with explicit parameter choice
            if args.era and era != args.era:
                continue
            if args.subera and subera != args.subera:
                continue

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

            root_file = ROOT.TFile.Open(files[0], 'r')
            root_tree = root_file.Get('Events')
            nEvents =  int(root_tree.GetEntries())
            if not isData:
                nEventsPositive =  int(root_tree.GetEntries('genWeight > 0'))
                nEventsNegative =  int(root_tree.GetEntries('genWeight < 0'))
            else:
                nEventsPositive = 0
                nEventsNegative = 0

            tup[5] = str(nEvents)
            tup[6] = str(nEventsPositive)
            tup[7] = str(nEventsNegative)
            line_corrected = ",".join(tup) + "\n"
            # print("line vs corrected line:")
            # print(line + line_corrected)
            corrected_lines.append(line_corrected)

    with open(local_tuple_file, "w") as out_f:
        for corrected_line in corrected_lines:
            print(corrected_line)
            out_f.write(corrected_line)

#Just run the module without the cutstring, for comparing counts
elif args.stage == 'process':
    local_tuple_file = "dirtestTriggerLogic/local_variety_pack_tuples_2017_NANOv5.txt"
    with open(local_tuple_file, "r") as in_f:
        for l, line in enumerate(in_f):
            # if l > 0: 
            #     continue
            if l < args.rmin or l > args.rmax:
                continue

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

            #Skip choices if requested, only with explicit parameter choice
            if args.era and era != args.era:
                continue
            if args.subera and subera != args.subera:
                continue

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
                if nEvents == (nEventsNegative + nEventsPositive):
                    weight = lumi * 1000 * crossSection / (nEventsPositive - nEventsNegative)
                else:
                    weight = lumi * 1000 * crossSection / nEvents
                subera = None
            else:
                weight = 1
            # print("era= {}\t subera={}\t isData={}\t TriggerChannel={}\t weight={}".format(era, subera, str(isData), channel, weight))
            modules = []
            if not isData: 
                if era == "2017": 
                    modules.append(puWeightProducer(pufile_mc2017, pufile_data2017, "pu_mc", "pileup", verbose=False, doSysVar=True))
                elif era == "2018": 
                    modules.append(puWeightProducer(pufile_mc2018, pufile_data2018, "pu_mc", "pileup", verbose=False, doSysVar=True))
            modules.append(TriggerAndLeptonLogic(passLevel='baseline',era=era, subera=subera, isData=isData, TriggerChannel=channel,
                                                 weightMagnitude=weight, fillHists=True, mode="Flag"))
            if not isData: 
                if l == 2:
                    modules.append(Stitcher(mode="Pass", era=era, channel="DL", condition="Pass", weightMagnitude=weight, fillHists=True, HTBinWidth=50, desiredHTMin=200, desiredHTMax=800))
                elif l == 4:                   
                    modules.append(Stitcher(mode="Fail", era=era, channel="DL", condition="Fail", weightMagnitude=weight, fillHists=True, HTBinWidth=50, desiredHTMin=200, desiredHTMax=800))
                elif l == 1: #Try to fix on-the-fly the SL channel which still has the wrong weight...
                    modules.append(Stitcher(mode="Pass", era=era, channel="SL", condition="Pass", weightMagnitude=weight*0.15, fillHists=True, HTBinWidth=50, desiredHTMin=200, desiredHTMax=800))
                elif l == 3:                   
                    modules.append(Stitcher(mode="Fail", era=era, channel="SL", condition="Fail", weightMagnitude=weight, fillHists=True, HTBinWidth=50, desiredHTMin=200, desiredHTMax=800))
            # if isData: modules.append(dataRecalib[era][subera])
            # if not isData: modules.append(jetmetUncertaintiesProducer("2017", "Fall17_17Nov2017_V32_MC", [ "All" ], redoJEC=True)) #Broken to hell because of their shenanigans in jetSmearer.py
            # modules.append(JetMETLogic(passLevel='baseline',era=era, subera=subera, isData=isData,  weightMagnitude=weight, fillHists=True, mode="Flag",
            #                            jetPtVar = "pt_nom", jetMVar = "mass_nom", debug=True)) 
            modules.append(JetMETLogic(passLevel='baseline',era=era, subera=subera, isData=isData,  weightMagnitude=weight, fillHists=True, mode="Flag",
                                       jetPtVar = "pt", jetMVar = "mass", debug=True)) #without _nom, since no newer JECs
            modules.append(HistCloser())
            # print(modules[0].getCutString())
            print(modules)
            p = PostProcessor("/eos/user/n/nmangane/SWAN_projects/TriggerLogicRDF",
                              files,
                              # cut=modules[0].getCutString(),
                              cut=None,
                              branchsel=None,
                              modules=modules,
                              compression="LZMA:9",
                              friend=False,
                              postfix="_Chain",
                              jsonInput=None,
                              # noOut=True,
                              noOut=False,
                              # justcount=True,
                              justcount=False,
                              provenance=False,
                              haddFileName=None,
                              fwkJobReport=False,
                              # histFileName="/eos/user/n/nmangane/SWAN_projects/" + files[0].replace("file", "hist").replace(".root", "_Chain.root"),
                              histFileName=files[0].replace("file", "hist").replace(".root", "_Chain.root"),
                              histDirName="plots", 
                              outputbranchsel=None,
                              maxEntries=None,
                              # maxEntries=20001,
                              firstEntry=0,
                              # prefetch=False,
                              prefetch=True,
                              longTermCache=False
            )
            # print(files[0].replace("file", "hist"))
            p.run()

elif args.stage == 'subprocess':
    #tailor code to also handle ranges, to break things up more
    for x in xrange(args.rmin, args.rmax+1):
        print(x)
        #Decide to wait, or let multiple subprocesses start in sequence but run in parallel, using .wait() or not
        subprocess.Popen(args="python testEntireChain.py --stage process --era {0} --rmin {1} --rmax {1} > /tmp/nmangane/subprocess_{1}.o".format(args.era, x), shell=True, executable="/bin/zsh", env=dict(os.environ))#.wait() 
#Simultaneously run the module and the cutstring
elif args.stage == 'combined':
    local_tuple_file = "dirtestTriggerLogic/local_variety_pack_tuples_2017_NANOv5.txt"
    with open(local_tuple_file, "r") as in_f:
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

            #Skip choices if requested, only with explicit parameter choice
            if args.era and era != args.era:
                continue
            if args.subera and subera != args.subera:
                continue

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
                if nEvents == (nEventsNegative + nEventsPositive):
                    weight = lumi * 1000 * crossSection / (nEventsPositive - nEventsNegative)
                else:
                    weight = lumi * 1000 * crossSection / nEvents
                subera = None
            else:
                weight = 1
            # print("era= {}\t subera={}\t isData={}\t TriggerChannel={}\t weight={}".format(era, subera, str(isData), channel, weight))
            modules = [JetMETLogic('baseline', era=era, subera=subera, isData=isData,  weightMagnitude=weight, fillHists=False)]
            # print(modules[0].getCutString())
            p = PostProcessor(".",
                              files,
                              cut=modules[0].getCutString(),
                              # cut=None,
                              branchsel=None,
                              modules=modules,
                              compression="LZMA:9",
                              friend=False,
                              postfix="_JetMET",
                              jsonInput=None,
                              noOut=True,
                              # noOut=False,
                              # justcount=True,
                              justcount=False,
                              provenance=False,
                              haddFileName=None,
                              fwkJobReport=False,
                              histFileName=None,
                              histDirName=None, 
                              outputbranchsel=None,
                              maxEntries=None,
                              firstEntry=0,
                              # prefetch=False,
                              prefetch=True,
                              longTermCache=False
            )
            p.run()

elif args.stage == 'hist':
    local_tuple_file = "dirtestTriggerLogic/local_variety_pack_tuples_2017_NANOv5.txt"
    with open(local_tuple_file, "r") as in_f:
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

            #Skip choices if requested, only with explicit parameter choice
            if args.era and era != args.era:
                continue
            if args.subera and subera != args.subera:
                continue

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
                if nEvents == (nEventsNegative + nEventsPositive):
                    weight = lumi * 1000 * crossSection / (nEventsPositive - nEventsNegative)
                else:
                    weight = lumi * 1000 * crossSection / nEvents
                subera = None
                theHistName = files[0].replace("file","hist_"+era)
            else:
                theHistName = files[0].replace("file","hist_"+era+subera+"_"+channel)
                weight = 1
            # print("era= {}\t subera={}\t isData={}\t TriggerChannel={}\t weight={}".format(era, subera, str(isData), channel, weight))
            modules = [JetMETLogic('baseline', era=era, subera=subera, isData=isData,  weightMagnitude=weight, fillHists=True)]
            # print(modules[0].getCutString())
            p = PostProcessor("dirtestTriggerLogic",
                              files,
                              # cut=modules[0].getCutString(),
                              cut=None,
                              branchsel=None,
                              modules=modules,
                              compression="LZMA:9",
                              friend=False,
                              postfix="_JetMET",
                              jsonInput=None,
                              noOut=True,
                              # noOut=False,
                              # justcount=True,
                              justcount=False,
                              provenance=False,
                              haddFileName=None,
                              fwkJobReport=False,
                              histFileName=theHistName,
                              histDirName="plots", 
                              outputbranchsel=None,
                              maxEntries=None,
                              firstEntry=0,
                              # prefetch=False,
                              prefetch=True,
                              longTermCache=False
            )
            p.run()
