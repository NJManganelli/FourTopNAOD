from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from FourTopNAOD.Kai.tools.intools import *
import collections, copy, json, math
from array import array
import multiprocessing
import inspect


class Stitcher(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt=None, mode="Flag", era="2017", channel="DL", condition="Pass"):
        self.writeHistFile=True
        self.verbose=verbose
        self._verbose = verbose
        self.probEvt = probEvt
        if probEvt:
            #self.probEvt = probEvt
            self.verbose = True        
        #event counters
        self.counter = 0
        self.maxEventsToProcess=maxevt
        self.mode = mode
        if self.mode not in ["Flag", "Pass", "Fail"]:
            raise NotImplementedError("Not a supported mode for the Stitcher module: '{0}'".format(self.mode))
        self.era = era
        self.channel = channel
        self.condition = condition
        self.bits = {'isPrompt':0b000000000000001,
                     'isDecayedLeptonHadron':0b000000000000010,
                     'isTauDecayProduct':0b000000000000100,
                     'isPromptTauDecaypprProduct':0b000000000001000,
                     'isDirectTauDecayProduct':0b000000000010000,
                     'isDirectPromptTauDecayProduct':0b000000000100000,
                     'isDirectHadronDecayProduct':0b000000001000000,
                     'isHardProcess':0b000000010000000,
                     'fromHardProcess':0b000000100000000,
                     'isHardProcessTauDecayProduct':0b000001000000000,
                     'isDirectHardProcessTauDecayProduct':0b000010000000000,
                     'fromHardProcessBeforeFSR':0b000100000000000,
                     'isFirstCopy':0b001000000000000,
                     'isLastCopy':0b010000000000000,
                     'isLastCopyBeforeFSR':0b100000000000000
                    }
        self.stitchDict = {'2016': {'SL': {'nGenJets': None,
                                           'nGenLeps': None,
                                           'GenHT': None},
                                    'DL': {'nGenJets': None,
                                           'nGenLeps': None,
                                           'GenHT': None}
                                },
                           '2017': {'SL': {'nGenJets': 9,
                                           'nGenLeps': 1,
                                           'GenHT': 500},
                                    'DL': {'nGenJets': 7,
                                           'nGenLeps': 2,
                                           'GenHT': 500}
                                },
                           '2018': {'SL': {'nGenJets': None,
                                           'nGenLeps': None,
                                           'GenHT': None},
                                    'DL': {'nGenJets': None,
                                           'nGenLeps': None,
                                           'GenHT': None}
                                }
                       }
        self.stitchSL = self.stitchDict[self.era]['SL']
        self.stitchDL = self.stitchDict[self.era]['DL']

    def beginJob(self,histFile=None,histDirName=None):
        if histFile == None or histDirName == None:
            Module.beginJob(self, None, None)
        else:
            Module.beginJob(self,histFile,histDirName)
            self.stitch_nGenJets = ROOT.TH1I("stitch_nGenJets", "nGenJet (pt > 30); nGenJets; Events", 18, 2, 20)
            self.addObject(self.stitch_nGenJets)
            self.stitch_GenHT = ROOT.TH1D("stitch_GenHT", "GenHT (pt > 30, |#eta| < 2.4); Gen HT (GeV); Events", 800, 200, 600)
            self.addObject(self.stitch_GenHT)
            self.stitch_nGenLeps = ROOT.TH1I("stitch_nGenLeps", "nGenLeps (e(1) or mu (1) or #tau (2)); nGenLeps; Events", 10, 0, 10)
            self.addObject(self.stitch_nGenLeps)
            self.stitch_AllVar = ROOT.TH3D("stitch_AllVar", "nGenLeps, nGenJets, GenHT; nGenLeps; nGenJets; GenHT ", 5, 0, 5, 6, 5, 12, 12, 300., 600.)
            self.addObject(self.stitch_AllVar)

    def endJob(self):
        if hasattr(self, 'objs') and self.objs != None:
            prevdir = ROOT.gDirectory
            self.dir.cd()
            for obj in self.objs:
                obj.Write()
            prevdir.cd()
            if hasattr(self, 'histFile') and self.histFile != None : 
                self.histFile.Close()

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.varDict = [('passSL', 'O', 'Passes Single Lepton Stitch cuts'),
                        ('passDL', 'O', 'Passes Single Lepton Stitch cuts'),
                       ]
        if self.mode == "Flag":
            if not self.out:
                raise RuntimeError("No Output file selected, cannot flag events for Stitching")
            else:
                for name, valType, valTitle in self.varDict:
                    self.out.branch("Stitch_%s"%(name), valType, title=valTitle)
        elif self.mode == "Pass" or self.mode == "Fail":
            pass



    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #Increment counter and skip events past the maxEventsToProcess, if larger than -1
        self.counter +=1
        if -1 < self.maxEventsToProcess < self.counter:
            return False        
        if self.probEvt:
            if event.event != self.probEvt:
                print("Skipping...")
                return False
        
        ###############################
        ### Collections and Objects ###
        ###############################
        gens = Collection(event, "GenPart")
        genjets = Collection(event, "GenJet")

        #Stitch variables
        nGL = 0
        nGJ = 0
        GenHT = 0
        for gj, jet in enumerate(genjets):
            if jet.pt > 30:
                nGJ += 1
                if abs(jet.eta) < 2.4: 
                    GenHT += jet.pt
        for gp, gen in enumerate(gens):
            if abs(gen.pdgId) in set([11, 13]) and gen.status == 1:
                nGL += 1
            elif abs(gen.pdgId) in set([15]) and gen.status == 2:
                nGL += 1
        
        

        passStitch = {}
        passStitch['passSL'] = (nGL >= self.stitchSL['nGenLeps'] and nGJ >= self.stitchSL['nGenJets'] and GenHT >= self.stitchSL['GenHT'])
        passStitch['passDL'] = (nGL >= self.stitchDL['nGenLeps'] and nGJ >= self.stitchDL['nGenJets'] and GenHT >= self.stitchDL['GenHT'])
        print("pass SL: nGL[{0:s}] nGJ[{1:s}] GHT[{2:s}]".format(str(nGL >= self.stitchSL['nGenLeps']),
                                                                 str(nGJ >= self.stitchSL['nGenJets']),
                                                                 str(GenHT >= self.stitchSL['GenHT'])))
        print("pass DL: nGL[{0:s}] nGJ[{1:s}] GHT[{2:s}]".format(str(nGL >= self.stitchDL['nGenLeps']),
                                                                 str(nGJ >= self.stitchDL['nGenJets']),
                                                                 str(GenHT >= self.stitchDL['GenHT'])))

        print("nGL[{0:d}]  nGJ[{1:d}]  GHT[{2:f}] passSL[{3:s}] passDL[{4:s}]".format(nGL, nGJ, GenHT, str(passStitch['passSL']), str(passStitch['passDL'])))

        self.stitch_nGenLeps.Fill(nGL)
        self.stitch_nGenJets.Fill(nGJ)
        self.stitch_GenHT.Fill(GenHT)
        self.stitch_AllVar.Fill(nGL, nGJ, GenHT)

        ########################## 
        ### Write out branches ###
        ##########################         
        if self.out and self.mode == "Flag":
            for name, valType, valTitle in self.varDict:
                self.out.fillBranch("Stitch_%s"%(name), passStitch[name])
            return True
        elif self.mode == "Pass":
            print("Testing event for passing")
            return passStitch['pass'+self.channel]
        elif self.mode == "Fail":
            print("Testing event for failure")
            return not passStitch['pass'+self.channel]
        else:
            raise NotImplementedError("No method in place for Stitcher module in mode '{0}'".format(self.mode))

Tuples = []
filesTT=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/80000/FB2C8D48-139E-7647-90C2-1CF1767DB0A1.root"]
hNameTT="StitchingTTv5.root"
Tuples.append((filesTT, hNameTT, 0))
filesTTGF=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/E565691C-17D4-6046-865E-8393F1FE0414.root"]
hNameTTGF="StitchingTTGF.root"
Tuples.append((filesTTGF, hNameTTGF, 0))

def multiplier(fileList, hName=None, wOpt=0):
    if hName == None:
        hDirName = None
    else:
        hDirName = "plots"

        p=PostProcessor(".",
                        fileList,
                        cut=None,
                        modules=[Stitcher(maxevt=1000, era="2017", channel="DL", mode="Flag")],
                        # modules=[TopSystemPt(maxevt=100, wOpt=wOption)],
                        noOut=False,
                        histFileName=hName,
                        histDirName=hDirName,
                       )
        p.run()

pList = []
for tup in Tuples:
    p = multiprocessing.Process(target=multiplier, args=(tup[0], tup[1], tup[2]))
    pList.append(p)
    p.start()

for p in pList:
    p.join()
