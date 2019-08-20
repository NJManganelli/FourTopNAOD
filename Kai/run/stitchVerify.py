from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from FourTopNAOD.Kai.modules.Stitcher import Stitcher
from FourTopNAOD.Kai.tools.toolbox import *
import collections, copy, json, math
from array import array
import multiprocessing
import inspect
import argparse
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='Test of Stitching module and post-stitching distributions')
parser.add_argument('--stage', dest='stage', action='store', type=str,
                    help='Stage to be processed: stitch or hist or plot')
args = parser.parse_args()

class StitchHist(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt=None, mode="Flag", era="2017", channel="DL", weightMagnitude=1):
        self.writeHistFile=True
        self.verbose=verbose
        #event counters
        self.counter = 0
        self.maxEventsToProcess=maxevt
        # self.mode = mode
        # if self.mode not in ["Flag", "Pass", "Fail"]:
        #     raise NotImplementedError("Not a supported mode for the Stitcher module: '{0}'".format(self.mode))
        self.era = era
        self.channel = channel
        self.weightMagnitude=weightMagnitude

    def beginJob(self,histFile=None,histDirName=None):
        self.hName = histFile
        if histFile == None or histDirName == None:
            self.fillHists = False
            Module.beginJob(self, None, None)
        else:
            self.fillHists = True

            Module.beginJob(self,histFile,histDirName)
            self.stitchPlot_PCond_nGenJets = ROOT.TH1D("stitchPlot_PCond_nGenJets", "nGenJet (pt > 30) Pass condition; nGenJets; Events", 18, 2, 20)
            self.addObject(self.stitchPlot_PCond_nGenJets)
            self.stitchPlot_PCond_GenHT = ROOT.TH1D("stitchPlot_PCond_GenHT", "GenHT (pt > 30, |#eta| < 2.4) Pass condition; Gen HT (GeV); Events", 500, 200, 1200)
            self.addObject(self.stitchPlot_PCond_GenHT)
            self.stitchPlot_PCond_nGenLeps = ROOT.TH1D("stitchPlot_PCond_nGenLeps", "nGenLeps (LHE level) Pass condition; nGenLeps; Events", 10, 0, 10)
            self.addObject(self.stitchPlot_PCond_nGenLeps)
            self.stitchPlot_PCond_AllVar = ROOT.TH3D("stitchPlot_PCond_AllVar", "nGenLeps, nGenJets, GenHT Pass condition; nGenLeps; nGenJets; GenHT ", 
                                                 6, 0, 6, 6, 5, 12, 12, 300., 600.)
            self.addObject(self.stitchPlot_PCond_AllVar)

            self.stitchPlot_FCond_nGenJets = ROOT.TH1D("stitchPlot_FCond_nGenJets", "nGenJet (pt > 30) Fail condition; nGenJets; Events", 18, 2, 20)
            self.addObject(self.stitchPlot_FCond_nGenJets)
            self.stitchPlot_FCond_GenHT = ROOT.TH1D("stitchPlot_FCond_GenHT", "GenHT (pt > 30, |#eta| < 2.4) Fail condition; Gen HT (GeV); Events", 500, 200, 1200)
            self.addObject(self.stitchPlot_FCond_GenHT)
            self.stitchPlot_FCond_nGenLeps = ROOT.TH1D("stitchPlot_FCond_nGenLeps", "nGenLeps (LHE level) Fail condition; nGenLeps; Events", 10, 0, 10)
            self.addObject(self.stitchPlot_FCond_nGenLeps)
            self.stitchPlot_FCond_AllVar = ROOT.TH3D("stitchPlot_FCond_AllVar", "nGenLeps, nGenJets, GenHT  Fail condition; nGenLeps; nGenJets; GenHT ",
                                                 6, 0, 6, 6, 5, 12, 12, 300., 600.)
            self.addObject(self.stitchPlot_FCond_AllVar)
            # self.stitchPlot_nGenLepsPart = ROOT.TH1D("stitchPlot_nGenLeps", "nGenLeps (e(1) or mu (1) or #tau (2)); nGenLeps; Events", 10, 0, 10)
            # self.addObject(self.stitchPlot_nGenLepsPart)

            

    def endJob(self):
        if hasattr(self, 'objs') and self.objs != None:
            prevdir = ROOT.gDirectory
            self.dir.cd()
            for obj in self.objs:
                obj.Write()
            prevdir.cd()
            if hasattr(self, 'histFile') and self.histFile != None : 
                self.histFile.Close()

    # def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    #     self.varDict = [('passStitchSL', 'O', 'Passes Single Lepton Stitch cuts'),
    #                     ('passStitchDL', 'O', 'Passes Single Lepton Stitch cuts'),
    #                     ('passStitchCondition', 'O', 'Passes or fails stitch cuts appropriately for the sample in this channel and era')
    #                    ]
    #     if self.mode == "Flag":
    #         if not self.out:
    #             raise RuntimeError("No Output file selected, cannot flag events for Stitching")
    #         else:
    #             for name, valType, valTitle in self.varDict:
    #                 self.out.branch("ESV_%s"%(name), valType, title=valTitle)



    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #Increment counter and skip events past the maxEventsToProcess, if larger than -1
        self.counter +=1
        if -1 < self.maxEventsToProcess < self.counter:
            return False        
        
        ###############################
        ### Collections and Objects ###
        ###############################
        weight = math.copysign(self.weightMagnitude, getattr(event, "genWeight"))
        gens = Collection(event, "GenPart")
        genjets = Collection(event, "GenJet")
        lheparts = Collection(event, "LHEPart")

        #Stitch variables
        nGL = 0
        nGJ = 0
        GenHT = 0
        for gj, jet in enumerate(genjets):
            if jet.pt > 30:
                nGJ += 1
                if abs(jet.eta) < 2.4: 
                    GenHT += jet.pt
        for lhep in lheparts:
            if lhep.pdgId in set([-15, -13, -11, 11, 13, 15]):            
                nGL += 1

        if self.fillHists:
            if getattr(event, "ESV_passStitchCondition"):
                # self.stitchPlot_nGenLepsPart.Fill(nGLgen, weight)
                self.stitchPlot_PCond_nGenLeps.Fill(nGL, weight)
                self.stitchPlot_PCond_nGenJets.Fill(nGJ, weight)
                self.stitchPlot_PCond_GenHT.Fill(GenHT, weight)
                self.stitchPlot_PCond_AllVar.Fill(nGL, nGJ, GenHT, weight)
            elif not getattr(event, "ESV_passStitchCondition"):
                # self.stitchPlot_nGenLepsPart.Fill(nGLgen, weight)
                self.stitchPlot_FCond_nGenLeps.Fill(nGL, weight)
                self.stitchPlot_FCond_nGenJets.Fill(nGJ, weight)
                self.stitchPlot_FCond_GenHT.Fill(GenHT, weight)
                self.stitchPlot_FCond_AllVar.Fill(nGL, nGJ, GenHT, weight)

        return True

# class Stitcher(Module):
#     def __init__(self, verbose=False, maxevt=-1, probEvt=None, mode="Flag", era="2017", channel="DL", condition="Pass"):
#         self.writeHistFile=True
#         self.verbose=verbose
#         self.probEvt = probEvt
#         if probEvt:
#             self.verbose = True        
#         #event counters
#         self.counter = 0
#         self.maxEventsToProcess=maxevt
#         self.mode = mode
#         if self.mode not in ["Flag", "Pass", "Fail"]:
#             raise NotImplementedError("Not a supported mode for the Stitcher module: '{0}'".format(self.mode))
#         self.era = era
#         self.channel = channel
#         self.condition = condition
#         # print("Stitcher is in mode '{0}' for era '{1}', channel '{2}', with condition '{3}'".format(self.mode, self.era, self.channel, self.condition))
#         self.bits = {'isPrompt':0b000000000000001,
#                      'isDecayedLeptonHadron':0b000000000000010,
#                      'isTauDecayProduct':0b000000000000100,
#                      'isPromptTauDecaypprProduct':0b000000000001000,
#                      'isDirectTauDecayProduct':0b000000000010000,
#                      'isDirectPromptTauDecayProduct':0b000000000100000,
#                      'isDirectHadronDecayProduct':0b000000001000000,
#                      'isHardProcess':0b000000010000000,
#                      'fromHardProcess':0b000000100000000,
#                      'isHardProcessTauDecayProduct':0b000001000000000,
#                      'isDirectHardProcessTauDecayProduct':0b000010000000000,
#                      'fromHardProcessBeforeFSR':0b000100000000000,
#                      'isFirstCopy':0b001000000000000,
#                      'isLastCopy':0b010000000000000,
#                      'isLastCopyBeforeFSR':0b100000000000000
#                     }
#         self.stitchDict = {'2016': {'SL': {'nGenJets': None,
#                                            'nGenLeps': None,
#                                            'GenHT': None},
#                                     'DL': {'nGenJets': None,
#                                            'nGenLeps': None,
#                                            'GenHT': None}
#                                 },
#                            '2017': {'SL': {'nGenJets': 9,
#                                            'nGenLeps': 1,
#                                            'GenHT': 500},
#                                     'DL': {'nGenJets': 7,
#                                            'nGenLeps': 2,
#                                            'GenHT': 500}
#                                 },
#                            '2018': {'SL': {'nGenJets': None,
#                                            'nGenLeps': None,
#                                            'GenHT': None},
#                                     'DL': {'nGenJets': None,
#                                            'nGenLeps': None,
#                                            'GenHT': None}
#                                 }
#                        }
#         self.stitchSL = self.stitchDict[self.era]['SL']
#         self.stitchDL = self.stitchDict[self.era]['DL']

#     def beginJob(self,histFile=None,histDirName=None):
#         self.hName = histFile
#         if histFile == None or histDirName == None:
#             self.fillHists = False
#             Module.beginJob(self, None, None)
#         else:
#             self.fillHists = True

#             Module.beginJob(self,histFile,histDirName)
#             self.stitch_PCond_nGenJets = ROOT.TH1D("stitch_PCond_nGenJets", "nGenJet (pt > 30) Pass condition; nGenJets; Events", 18, 2, 20)
#             self.addObject(self.stitch_PCond_nGenJets)
#             self.stitch_PCond_GenHT = ROOT.TH1D("stitch_PCond_GenHT", "GenHT (pt > 30, |#eta| < 2.4) Pass condition; Gen HT (GeV); Events", 800, 200, 600)
#             self.addObject(self.stitch_PCond_GenHT)
#             self.stitch_PCond_nGenLeps = ROOT.TH1D("stitch_PCond_nGenLeps", "nGenLeps (LHE level) Pass condition; nGenLeps; Events", 10, 0, 10)
#             self.addObject(self.stitch_PCond_nGenLeps)
#             self.stitch_PCond_AllVar = ROOT.TH3D("stitch_PCond_AllVar", "nGenLeps, nGenJets, GenHT Pass condition; nGenLeps; nGenJets; GenHT ", 
#                                                  6, 0, 6, 6, 5, 12, 12, 300., 600.)
#             self.addObject(self.stitch_PCond_AllVar)

#             self.stitch_FCond_nGenJets = ROOT.TH1D("stitch_FCond_nGenJets", "nGenJet (pt > 30) Fail condition; nGenJets; Events", 18, 2, 20)
#             self.addObject(self.stitch_FCond_nGenJets)
#             self.stitch_FCond_GenHT = ROOT.TH1D("stitch_FCond_GenHT", "GenHT (pt > 30, |#eta| < 2.4) Fail condition; Gen HT (GeV); Events", 800, 200, 600)
#             self.addObject(self.stitch_FCond_GenHT)
#             self.stitch_FCond_nGenLeps = ROOT.TH1D("stitch_FCond_nGenLeps", "nGenLeps (LHE level) Fail condition; nGenLeps; Events", 10, 0, 10)
#             self.addObject(self.stitch_FCond_nGenLeps)
#             self.stitch_FCond_AllVar = ROOT.TH3D("stitch_FCond_AllVar", "nGenLeps, nGenJets, GenHT  Fail condition; nGenLeps; nGenJets; GenHT ",
#                                                  6, 0, 6, 6, 5, 12, 12, 300., 600.)
#             self.addObject(self.stitch_FCond_AllVar)
#             # self.stitch_nGenLepsPart = ROOT.TH1D("stitch_nGenLeps", "nGenLeps (e(1) or mu (1) or #tau (2)); nGenLeps; Events", 10, 0, 10)
#             # self.addObject(self.stitch_nGenLepsPart)

#     def endJob(self):
#         if hasattr(self, 'objs') and self.objs != None:
#             prevdir = ROOT.gDirectory
#             self.dir.cd()
#             for obj in self.objs:
#                 obj.Write()
#             prevdir.cd()
#             if hasattr(self, 'histFile') and self.histFile != None : 
#                 self.histFile.Close()

#     def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
#         self.out = wrappedOutputTree
#         self.varDict = [('passStitchSL', 'O', 'Passes Single Lepton Stitch cuts'),
#                         ('passStitchDL', 'O', 'Passes Single Lepton Stitch cuts'),
#                         ('passStitchCondition', 'O', 'Passes or fails stitch cuts appropriately for the sample in this channel and era')
#                        ]
#         if self.mode == "Flag":
#             if not self.out:
#                 raise RuntimeError("No Output file selected, cannot flag events for Stitching")
#             else:
#                 for name, valType, valTitle in self.varDict:
#                     self.out.branch("ESV_%s"%(name), valType, title=valTitle)
#         elif self.mode == "Pass" or self.mode == "Fail":
#             pass



#     def analyze(self, event): #called by the eventloop per-event
#         """process event, return True (go to next module) or False (fail, go to next event)"""
#         #Increment counter and skip events past the maxEventsToProcess, if larger than -1
#         self.counter +=1
#         if -1 < self.maxEventsToProcess < self.counter:
#             return False        
#         if self.probEvt:
#             if event.event != self.probEvt:
#                 print("Skipping...")
#                 return False
        
#         ###############################
#         ### Collections and Objects ###
#         ###############################
#         gens = Collection(event, "GenPart")
#         genjets = Collection(event, "GenJet")
#         lheparts = Collection(event, "LHEPart")

#         #Stitch variables
#         nGL = 0
#         nGJ = 0
#         GenHT = 0
#         for gj, jet in enumerate(genjets):
#             if jet.pt > 30:
#                 nGJ += 1
#                 if abs(jet.eta) < 2.4: 
#                     GenHT += jet.pt
#         for lhep in lheparts:
#             if lhep.pdgId in set([-15, -13, -11, 11, 13, 15]):            
#                 nGL += 1

#         # nGLgen = 0
#         # for gp, gen in enumerate(gens):
#         #     if abs(gen.pdgId) in set([11, 13]) and gen.status == 1:
#         #         nGLgen += 1
#         #     elif abs(gen.pdgId) in set([15]) and gen.status == 2:
#         #         nGLgen += 1
        
        

#         passStitch = {}
#         if nGL == self.stitchSL['nGenLeps'] and nGJ >= self.stitchSL['nGenJets'] and GenHT >= self.stitchSL['GenHT']:
#             shitTestSL = True
#         else:
#             shitTestSL = False
#         if nGL == self.stitchDL['nGenLeps'] and nGJ >= self.stitchDL['nGenJets'] and GenHT >= self.stitchDL['GenHT']:
#             shitTestDL = True
#         else:
#             shitTestDL = False
#         passStitch['passStitchSL'] = (nGL == self.stitchSL['nGenLeps'] and nGJ >= self.stitchSL['nGenJets'] and GenHT >= self.stitchSL['GenHT'])
#         passStitch['passStitchDL'] = (nGL == self.stitchDL['nGenLeps'] and nGJ >= self.stitchDL['nGenJets'] and GenHT >= self.stitchDL['GenHT'])
#         if passStitch['passStitchSL'] != shitTestSL:
#             print("GODDAMNED FAIL, SL!")
#         if passStitch['passStitchDL'] != shitTestDL:
#             print("GODDAMNED FAIL, DL!")
#         if self.condition == "Pass":
#             passStitch['passStitchCondition'] = passStitch['passStitch'+self.channel]
#         elif self.condition == "Fail":
#             passStitch['passStitchCondition'] = not passStitch['passStitch'+self.channel]
#         if self.fillHists:
#             if passStitch['passStitchCondition']:
#                 # self.stitch_nGenLepsPart.Fill(nGLgen)
#                 self.stitch_PCond_nGenLeps.Fill(nGL)
#                 self.stitch_PCond_nGenJets.Fill(nGJ)
#                 self.stitch_PCond_GenHT.Fill(GenHT)
#                 self.stitch_PCond_AllVar.Fill(nGL, nGJ, GenHT)
#             else:
#                 # self.stitch_nGenLepsPart.Fill(nGLgen)
#                 self.stitch_FCond_nGenLeps.Fill(nGL)
#                 self.stitch_FCond_nGenJets.Fill(nGJ)
#                 self.stitch_FCond_GenHT.Fill(GenHT)
#                 self.stitch_FCond_AllVar.Fill(nGL, nGJ, GenHT)



#         if self.verbose and self.counter % 100 == 0:
#             print("histFile: {3:s} pass SL: nGL[{0:s}] nGJ[{1:s}] GHT[{2:s}]".format(str(nGL == self.stitchSL['nGenLeps']),
#                                                                                      str(nGJ >= self.stitchSL['nGenJets']),
#                                                                                      str(GenHT >= self.stitchSL['GenHT']),
#                                                                                      str(self.hName)))
#             print("histFile: {3:s} pass DL: nGL[{0:s}] nGJ[{1:s}] GHT[{2:s}]".format(str(nGL == self.stitchDL['nGenLeps']),
#                                                                                      str(nGJ >= self.stitchDL['nGenJets']),
#                                                                                      str(GenHT >= self.stitchDL['GenHT']),
#                                                                                      str(self.hName)))

#             print("histFile: {5:s} nGL[{0:d}]  nGJ[{1:d}]  GHT[{2:f}] passSL[{3:s}] passDL[{4:s}]".format(nGL, 
#                                                                                                           nGJ, 
#                                                                                                           GenHT, 
#                                                                                                           str(passStitch['passStitchSL']), 
#                                                                                                           str(passStitch['passStitchDL']),
#                                                                                                           str(self.hName))
#               )

#         ########################## 
#         ### Write out branches ###
#         ##########################         
#         if self.out and self.mode == "Flag":
#             for name, valType, valTitle in self.varDict:
#                 self.out.fillBranch("ESV_%s"%(name), passStitch[name])
#             return True
#         elif self.mode == "Pass":
#             print("Testing event for passing")
#             return passStitch['passStitch'+self.channel]
#         elif self.mode == "Fail":
#             print("Testing event for failure")
#             return not passStitch['passStitch'+self.channel]
#         else:
#             raise NotImplementedError("No method in place for Stitcher module in mode '{0}'".format(self.mode))

#Dilepton Data
Tuples = []
# filesTTDL=getFiles(query="dbs:/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM",
#                    redir="root://cms-xrd-global.cern.ch/")
filesTTDL=getFiles(query="dbs:/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   redir="root://cms-xrd-global.cern.ch/")
# filesTTDL=getFiles(query="glob:/eos/user/n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/Stage_NANOv4_to_Stitched/crab_20190718_0045/crab_tt_DL_2017/results/tree_*.root")
# filesTTDL = filesTTDL[0:1]
hNameTTDL="StitchingTTDLv7.root"
TTWeight = 89.0482 * 1000 * 41.53 / (68875708 - 280100)
Tuples.append((filesTTDL, hNameTTDL, "2017", "DL", "Fail", "Flag", TTWeight))

# filesTTDLGF =getFiles(query="dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
#                       redir="root://cms-xrd-global.cern.ch/")
filesTTDLGF=getFiles(query="dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                     redir="root://cms-xrd-global.cern.ch/")
# filesTTDLGF=getFiles(query="glob:/eos/user/n/nmangane/CMSSW/CMSSW_10_2_14/src/FourTopNAOD/Kai/crab/Stage_NANOv4_to_Stitched/crab_20190718_0045/crab_tt_DL-GF_2017_v2/results/tree_*.root")
# filesTTDLGF = filesTTDLGF[0:1]
hNameTTDLGF="StitchingTTDLGFv7.root"
# TTGFWeight = 0 * 1000 * 41.53 / (8415626 - 42597)
TTGFWeight = 89.0482 * 1000 * 41.53 / (8415626 - 42597) #Without the filter efficiency, to make the calculation more transparent - that is, same XS
Tuples.append((filesTTDLGF, hNameTTDLGF,  "2017", "DL", "Pass", "Flag", TTGFWeight))

# filesTTSL=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/00000/7BB010D2-1FE4-1D45-B5E0-ABC7A285E8FC.root"]
filesTTSL=getFiles(query="dbs:/TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   redir="root://cms-xrd-global.cern.ch/")
hNameTTSL="StitchingTTSLv7.root"
TTWeightSL = 366.2073 * 1000 * 41.53 / (20040607 - 81403)
Tuples.append((filesTTSL, hNameTTSL,  "2017", "SL", "Fail", "Flag", TTWeightSL))
# filesTTSLGF=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/CD79F874-9C0A-6446-81A2-344B4C7B3EE9.root"]
filesTTSLGF=getFiles(query="dbs:/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                     redir="root://cms-xrd-global.cern.ch/")`
hNameTTSLGF="StitchingTTSLGFv7.root"
TTGFWeightSL = 366.2073 * 1000 * 41.53 / (8794464 - 42392)
Tuples.append((filesTTSLGF, hNameTTSLGF, "2017", "SL", "Pass", "Flag", TTGFWeightSL))

def stitcher(fileList, hName=None, theEra="2021", theChannel="NL", theCondition="Nope", theMode="Bloop!", weightMagnitude=1):
    # print("Stitcher disabled here, use hist or plot")
    if hName == None:
        hDirName = None
    else:
        hDirName = "plots"
        p=PostProcessor(".",
                        fileList,
                        cut=None,
                        # modules=[Stitcher(maxevt=300000, era=theEra, channel=theChannel, mode=theMode, condition=theCondition, verbose=False)],
                        modules=[Stitcher(verbose=True,  mode=theMode, era=theEra, channel=theChannel, condition=theCondition, weightMagnitude=weightMagnitude, fillHists=True, HTBinWidth=50, desiredHTMin=200, desiredHTMax=800)],
                        noOut=False,
                        maxEntries=4000,
                        haddFileName=hName,
                        histFileName="hist_"+hName,
                        histDirName=hDirName,
                       )
        # p.run()

def histogramer(fileList, hName=None, theEra="2021", theChannel="NL", weightMagnitude=1):
    if hName == None:
        hDirName = None
    else:
        hDirName = "plots"
        p=PostProcessor(".",
                        fileList,
                        cut=None,
                        #Need the plotter, yo
                        modules=[StitchHist(maxevt=-1, era=theEra, channel=theChannel, verbose=False, weightMagnitude=weightMagnitude)],
                        noOut=True,
                        histFileName=hName,
                        histDirName=hDirName,
                       )
        p.run()

def plotter(fileList, hName=None, theEra="2021", theChannel="NL", theCondition="Nope", weightMagnitude=1):
    pass

if args.stage == 'stitch':
    pList = []
    for tup in Tuples:
        p = multiprocessing.Process(target=stitcher, args=(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5]))
        pList.append(p)
        p.start()
        
    for p in pList:
        p.join()

elif args.stage == 'hist':
    pList = []
    for tup in Tuples:
        p = multiprocessing.Process(target=histogramer, args=(tup[0], tup[1].replace(".root", "_verify.root"), tup[2], tup[3], tup[6]))
        pList.append(p)
        p.start()
        
    for p in pList:
        p.join()

elif args.stage == 'plot':
    pass
else:
    print("Unsuppored stage selected, please choose 'stitch' (add pass/fail stitch branches), 'hist' (make histograms), or 'plot' (Plot the histograms)")
