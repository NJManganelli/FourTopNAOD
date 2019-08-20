from __future__ import division, print_function
import ROOT
# import math
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
# from FourTopNAOD.Kai.tools.toolbox import *

class Stitcher(Module):
    def __init__(self, verbose=False, probEvt=None, mode="Flag", era="2017", channel="DL", condition="Pass", weightMagnitude=1, fillHists=False, HTBinWidth=50, desiredHTMin=200, desiredHTMax=800):
        """Class for stitching gen(jet)HT-, nGenLep(ton)-, and nGenJet-binned samples. 

        The mode "Flag" adds a boolean branch which is set to True if the sample event should be used, and False if it should not. 
        Whether an event should be marked as True/False depends on the three variables era, condition, and channel. The era and channel should match the sample being put through ("DL" for Dilepton, "SL" for Single lepton,
        "2016, "2017" or "2018" for the era). The condition should be set to "Pass" if the desirable events are those that 'pass' the simultaneous cuts (that is, filtered sample where nGenJet >= X and GenHT >= Y and nGenLep >= Z),
        and set to "Fail" if the desirable events are those that 'fail' the simultaneity conditions (that is, the events fail one OR more of those conditions). In this way, events that are from the 'bulk' of the nominal sample are
        flagged with True, events from the high-HT, high-nJet tail of the nominal sample are flagged with False, events from the filtered sample should be flagged with True.

        The mode "Pass" or "Fail" does not create branches, but simply decides whether to pass the event on to the next module or not. This is synonymous with the condition "Pass" and "Fail," so in pass mode, events fulfilling all
        the simultaneous criteria will go to the next module/be written to the tree, and in fail mode, only those that fail to pass one of the conditions will continue/be written out. Not fully tested, last this docstring was updated.
        """
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
        self.weightMagnitude = weightMagnitude
        self.fillHists = fillHists

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
                           '2018': {'SL': {'nGenJets': 9,
                                           'nGenLeps': 1,
                                           'GenHT': 500},
                                    'DL': {'nGenJets': 7,
                                           'nGenLeps': 2,
                                           'GenHT': 500}
                                }
                       }
        self.stitchSL = self.stitchDict[self.era]['SL']
        self.stitchDL = self.stitchDict[self.era]['DL']
        
        #Binning variables for determining continuity or normalization factor
        #nGenJet and nGenLep (just hardcoded here, don't see much use for varying these that much
        self.nGenJetMin = 2
        self.nGenJetMax = 20
        self.nGenJetBins = self.nGenJetMax - self.nGenJetMin
        self.nGenLepMin = 0
        self.nGenLepMax = 5
        self.nGenLepBins = self.nGenJetMax - self.nGenJetMin

        #HT
        self.HTBinWidth = HTBinWidth
        self.desiredHTMin = desiredHTMin
        self.desiredHTMax = desiredHTMax
        cutValue = self.stitchDict[self.era][self.channel]['GenHT']
        self.HTMin = cutValue
        self.HTMax = cutValue
        self.HTBins = 0
        while (self.HTMin > self.desiredHTMin):
            self.HTMin -= self.HTBinWidth
            self.HTBins += 1
        while (self.HTMax < self.desiredHTMax):
            self.HTMax += self.HTBinWidth
            self.HTBins += 1
        if self.verbose: 
            print("For desiredHTMin={0:<.1f} and desiredHTMax={1:<.1f}, with HTBinWidth={2:<.1f}, the calculated HTMin={3:<.1f} and HTMax={4:<.1f} with HTBins={5:<d}".format(self.desiredHTMin, self.desiredHTMax,
                                                                                                                                                                              self.HTBinWidth, self.HTMin,
                                                                                                                                                                              self.HTMax, self.HTBins)
            )
        
        #Warning for excessive 3D binning that might lead to O(Gigabyte) histograms in RAM
        n3DBins = self.nGenLepBins * self.nGenJetBins * self.HTBins
        if n3DBins * 8 > 1024**3: #blithely assume about 12 bytes per bin, for 3 doubles (number of entries, mean, RMS...)
            print("TriggerAndSelectionLogic Module has been configured with an excessive number of bins in 3D histograms ({0}). This may consume O({1})GB of RAM... consider decreasing bin sizes!".format(n3DBins, n3DBins*4/(1024**3)))

    def beginJob(self,histFile=None,histDirName=None):
        self.hName = histFile
        if histFile == None or histDirName == None or self.fillHists == False:
            Module.beginJob(self, None, None)
        else:
            Module.beginJob(self,histFile,histDirName)
            self.stitch_PCond_nGenJets = ROOT.TH1D("stitch_PCond_nGenJets", "nGenJet (pt > 30) Pass condition (weightMagnitude={0}); nGenJets; Events".format(self.weightMagnitude), self.nGenJetBins, self.nGenJetMin, self.nGenJetMax)
            self.addObject(self.stitch_PCond_nGenJets)
            self.stitch_PCond_GenHT = ROOT.TH1D("stitch_PCond_GenHT", "GenHT (pt > 30, |#eta| < 2.4) Pass condition (weightMagnitude={0}); Gen HT (GeV); Events".format(self.weightMagnitude), self.HTBins, self.HTMin, self.HTMax)
            self.addObject(self.stitch_PCond_GenHT)
            self.stitch_PCond_nGenLeps = ROOT.TH1D("stitch_PCond_nGenLeps", "nGenLeps (LHE level) Pass condition (weightMagnitude={0}); nGenLeps; Events".format(self.weightMagnitude), self.nGenLepBins, self.nGenLepMin, self.nGenLepMax)
            self.addObject(self.stitch_PCond_nGenLeps)
            self.stitch_PCond_2DJetHT = ROOT.TH2D("stitch_PCond_2DJetHT", "nGenJets, GenHT  Fail condition (weightMagnitude={0}); nGenJets; GenHT ".format(self.weightMagnitude),
                                                  self.nGenJetBins, self.nGenJetMin, self.nGenJetMax, self.HTBins, self.HTMin, self.HTMax)
            self.addObject(self.stitch_PCond_2DJetHT)
            self.stitch_PCond_AllVar = ROOT.TH3D("stitch_PCond_AllVar", "nGenLeps, nGenJets, GenHT Pass condition (weightMagnitude={0}); nGenLeps; nGenJets; GenHT ".format(self.weightMagnitude), 
                                                 self.nGenLepBins, self.nGenLepMin, self.nGenLepMax, self.nGenJetBins, self.nGenJetMin, self.nGenJetMax, self.HTBins, self.HTMin, self.HTMax.)
            self.addObject(self.stitch_PCond_AllVar)

            self.stitch_FCond_nGenJets = ROOT.TH1D("stitch_FCond_nGenJets", "nGenJet (pt > 30) Fail condition (weightMagnitude={0}); nGenJets; Events".format(self.weightMagnitude), self.nGenJetBins, self.nGenJetMin, self.nGenJetMax)
            self.addObject(self.stitch_FCond_nGenJets)
            self.stitch_FCond_GenHT = ROOT.TH1D("stitch_FCond_GenHT", "GenHT (pt > 30, |#eta| < 2.4) Fail condition (weightMagnitude={0}); Gen HT (GeV); Events".format(self.weightMagnitude), self.HTBins, self.HTMin, self.HTMax)
            self.addObject(self.stitch_FCond_GenHT)
            self.stitch_FCond_nGenLeps = ROOT.TH1D("stitch_FCond_nGenLeps", "nGenLeps (LHE level) Fail condition (weightMagnitude={0}); nGenLeps; Events".format(self.weightMagnitude), self.nGenLepBins, self.nGenLepMin, self.nGenLepMax)
            self.addObject(self.stitch_FCond_nGenLeps)
            self.stitch_FCond_2DJetHT = ROOT.TH2D("stitch_FCond_2DJetHT", "nGenJets, GenHT  Fail condition (weightMagnitude={0}); nGenJets; GenHT ".format(self.weightMagnitude),
                                                  self.nGenJetBins, self.nGenJetMin, self.nGenJetMax, self.HTBins, self.HTMin, self.HTMax)
            self.addObject(self.stitch_FCond_2DJetHT)
            self.stitch_FCond_AllVar = ROOT.TH3D("stitch_FCond_AllVar", "nGenLeps, nGenJets, GenHT  Fail condition (weightMagnitude={0}); nGenLeps; nGenJets; GenHT ".format(self.weightMagnitude),
                                                 self.nGenLepBins, self.nGenLepMin, self.nGenLepMax, self.nGenJetBins, self.nGenJetMin, self.nGenJetMax, self.HTBins, self.HTMin, self.HTMax)
            self.addObject(self.stitch_FCond_AllVar)
            # self.stitch_nGenLepsPart = ROOT.TH1D("stitch_nGenLeps", "nGenLeps (e(1) or mu (1) or #tau (2)); nGenLeps; Events", 10, 0, 10)
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
                # self.stitch_nGenLepsPart.Fill(nGLgen, weight)
                self.stitch_PCond_nGenLeps.Fill(nGL, weight)
                self.stitch_PCond_nGenJets.Fill(nGJ, weight)
                self.stitch_PCond_GenHT.Fill(GenHT, weight)
                self.stitch_PCond_2DJetHT(nGJ, GenHT, weight)
                self.stitch_PCond_AllVar.Fill(nGL, nGJ, GenHT, weight)
            else:
                # self.stitch_nGenLepsPart.Fill(nGLgen, weight)
                self.stitch_FCond_nGenLeps.Fill(nGL, weight)
                self.stitch_FCond_nGenJets.Fill(nGJ, weight)
                self.stitch_FCond_GenHT.Fill(GenHT, weight)
                self.stitch_FCond_2DJetHT(nGJ, GenHT, weight)
                self.stitch_FCond_AllVar.Fill(nGL, nGJ, GenHT, weight)

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

Stitcher_2018_DL = lambda : Stitcher(era="2018", channel="DL", condition="Fail", mode="Flag")
Stitcher_2018_DL_GF = lambda : Stitcher(era="2018", channel="DL", condition="Pass", mode="Flag")
Stitcher_2018_SL = lambda : Stitcher(era="2018", channel="SL", condition="Fail", mode="Flag")
Stitcher_2018_SL_GF = lambda : Stitcher(era="2018", channel="SL", condition="Pass", mode="Flag")
