from __future__ import division, print_function
import ROOT
# import math
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
# from FourTopNAOD.Kai.tools.toolbox import *

class Stitcher(Module):
    def __init__(self, verbose=False, probEvt=None, mode="Flag", era="2017", channel="DL", condition="Pass"):
        self.writeHistFile=True
        self.verbose=verbose
        self.probEvt = probEvt
        if probEvt:
            self.verbose = True        
        #event counters
        self.counter = 0
        self.mode = mode
        if self.mode not in ["Flag", "Pass", "Fail"]:
            raise NotImplementedError("Not a supported mode for the Stitcher module: '{0}'".format(self.mode))
        self.era = era
        self.channel = channel
        self.condition = condition
        # print("Stitcher is in mode '{0}' for era '{1}', channel '{2}', with condition '{3}'".format(self.mode, self.era, self.channel, self.condition))
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
        self.hName = histFile
        if histFile == None or histDirName == None:
            self.fillHists = False
            Module.beginJob(self, None, None)
        else:
            self.fillHists = True

            Module.beginJob(self,histFile,histDirName)
            self.stitch_PCond_nGenJets = ROOT.TH1I("stitch_PCond_nGenJets", "nGenJet (pt > 30) Pass condition; nGenJets; Events", 18, 2, 20)
            self.addObject(self.stitch_PCond_nGenJets)
            self.stitch_PCond_GenHT = ROOT.TH1D("stitch_PCond_GenHT", "GenHT (pt > 30, |#eta| < 2.4) Pass condition; Gen HT (GeV); Events", 800, 200, 600)
            self.addObject(self.stitch_PCond_GenHT)
            self.stitch_PCond_nGenLeps = ROOT.TH1I("stitch_PCond_nGenLeps", "nGenLeps (LHE level) Pass condition; nGenLeps; Events", 10, 0, 10)
            self.addObject(self.stitch_PCond_nGenLeps)
            self.stitch_PCond_AllVar = ROOT.TH3D("stitch_PCond_AllVar", "nGenLeps, nGenJets, GenHT Pass condition; nGenLeps; nGenJets; GenHT ", 
                                                 6, 0, 6, 6, 5, 12, 12, 300., 600.)
            self.addObject(self.stitch_PCond_AllVar)

            self.stitch_FCond_nGenJets = ROOT.TH1I("stitch_FCond_nGenJets", "nGenJet (pt > 30) Fail condition; nGenJets; Events", 18, 2, 20)
            self.addObject(self.stitch_FCond_nGenJets)
            self.stitch_FCond_GenHT = ROOT.TH1D("stitch_FCond_GenHT", "GenHT (pt > 30, |#eta| < 2.4) Fail condition; Gen HT (GeV); Events", 800, 200, 600)
            self.addObject(self.stitch_FCond_GenHT)
            self.stitch_FCond_nGenLeps = ROOT.TH1I("stitch_FCond_nGenLeps", "nGenLeps (LHE level) Fail condition; nGenLeps; Events", 10, 0, 10)
            self.addObject(self.stitch_FCond_nGenLeps)
            self.stitch_FCond_AllVar = ROOT.TH3D("stitch_FCond_AllVar", "nGenLeps, nGenJets, GenHT  Fail condition; nGenLeps; nGenJets; GenHT ",
                                                 6, 0, 6, 6, 5, 12, 12, 300., 600.)
            self.addObject(self.stitch_FCond_AllVar)
            # self.stitch_nGenLepsPart = ROOT.TH1I("stitch_nGenLeps", "nGenLeps (e(1) or mu (1) or #tau (2)); nGenLeps; Events", 10, 0, 10)
            # self.addObject(self.stitch_nGenLepsPart)

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
        self.varDict = [('passStitchSL', 'O', 'Passes Single Lepton Stitch cuts'),
                        ('passStitchDL', 'O', 'Passes Single Lepton Stitch cuts'),
                        ('passStitchCondition', 'O', 'Passes or fails stitch cuts appropriately for the sample in this channel and era')
                       ]
        if self.mode == "Flag":
            if not self.out:
                raise RuntimeError("No Output file selected, cannot flag events for Stitching")
            else:
                for name, valType, valTitle in self.varDict:
                    self.out.branch("ESV_%s"%(name), valType, title=valTitle)
        elif self.mode == "Pass" or self.mode == "Fail":
            pass



    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        self.counter +=1
        
        ###############################
        ### Collections and Objects ###
        ###############################
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

        # nGLgen = 0
        # for gp, gen in enumerate(gens):
        #     if abs(gen.pdgId) in set([11, 13]) and gen.status == 1:
        #         nGLgen += 1
        #     elif abs(gen.pdgId) in set([15]) and gen.status == 2:
        #         nGLgen += 1
        
        passStitch = {}
        passStitch['passStitchSL'] = (nGL == self.stitchSL['nGenLeps'] and nGJ >= self.stitchSL['nGenJets'] and GenHT >= self.stitchSL['GenHT'])
        passStitch['passStitchDL'] = (nGL == self.stitchDL['nGenLeps'] and nGJ >= self.stitchDL['nGenJets'] and GenHT >= self.stitchDL['GenHT'])
        if self.condition == "Pass":
            passStitch['passStitchCondition'] = passStitch['passStitch'+self.channel]
        elif self.condition == "Fail":
            passStitch['passStitchCondition'] = not passStitch['passStitch'+self.channel]
        if self.fillHists:
            if passStitch['passStitchCondition']:
                # self.stitch_nGenLepsPart.Fill(nGLgen)
                self.stitch_PCond_nGenLeps.Fill(nGL)
                self.stitch_PCond_nGenJets.Fill(nGJ)
                self.stitch_PCond_GenHT.Fill(GenHT)
                self.stitch_PCond_AllVar.Fill(nGL, nGJ, GenHT)
            else:
                # self.stitch_nGenLepsPart.Fill(nGLgen)
                self.stitch_FCond_nGenLeps.Fill(nGL)
                self.stitch_FCond_nGenJets.Fill(nGJ)
                self.stitch_FCond_GenHT.Fill(GenHT)
                self.stitch_FCond_AllVar.Fill(nGL, nGJ, GenHT)

        if self.verbose and self.counter % 100 == 0:
            print("histFile: {3:s} pass SL: nGL[{0:s}] nGJ[{1:s}] GHT[{2:s}]".format(str(nGL == self.stitchSL['nGenLeps']),
                                                                                     str(nGJ >= self.stitchSL['nGenJets']),
                                                                                     str(GenHT >= self.stitchSL['GenHT']),
                                                                                     str(self.hName)))
            print("histFile: {3:s} pass DL: nGL[{0:s}] nGJ[{1:s}] GHT[{2:s}]".format(str(nGL == self.stitchDL['nGenLeps']),
                                                                                     str(nGJ >= self.stitchDL['nGenJets']),
                                                                                     str(GenHT >= self.stitchDL['GenHT']),
                                                                                     str(self.hName)))

            print("histFile: {5:s} nGL[{0:d}]  nGJ[{1:d}]  GHT[{2:f}] passSL[{3:s}] passDL[{4:s}]".format(nGL, 
                                                                                                          nGJ, 
                                                                                                          GenHT, 
                                                                                                          str(passStitch['passStitchSL']), 
                                                                                                          str(passStitch['passStitchDL']),
                                                                                                          str(self.hName))
              )

        ########################## 
        ### Write out branches ###
        ##########################         
        if self.out and self.mode == "Flag":
            for name, valType, valTitle in self.varDict:
                self.out.fillBranch("ESV_%s"%(name), passStitch[name])
            return True
        elif self.mode == "Pass":
            print("Testing event for passing")
            return passStitch['passStitch'+self.channel]
        elif self.mode == "Fail":
            print("Testing event for failure")
            return not passStitch['passStitch'+self.channel]
        else:
            raise NotImplementedError("No method in place for Stitcher module in mode '{0}'".format(self.mode))

Stitcher_2017_DL = lambda : Stitcher(era="2017", channel="DL", condition="Fail", mode="Flag")
Stitcher_2017_DL_GF = lambda : Stitcher(era="2017", channel="DL", condition="Pass", mode="Flag")
Stitcher_2017_SL = lambda : Stitcher(era="2017", channel="SL", condition="Fail", mode="Flag")
Stitcher_2017_SL_GF = lambda : Stitcher(era="2017", channel="SL", condition="Pass", mode="Flag")
