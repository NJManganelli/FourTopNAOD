from __future__ import division, print_function
import ROOT
import math
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.toolbox import *

class BaselineSelector(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt=None, isData=True, 
                 genEquivalentLuminosity=1, genXS=1, genNEvents=1, genSumWeights=1, era="2017", lepPt=13, MET=40, HT=350, jetPtVar = "pt_nom", jetMVar = "mass_nom"):
        self.writeHistFile=True
        self.verbose=verbose
        self.probEvt = probEvt
        self.isData = isData
        if self.isData:
            self.evtWeightBase = 1
        else:
            if genEquivalentLuminosity == 1 and genXS == 1 and genNEvents == 1:
                self.evtWeightBase = None
                self.evtWeightAlt = None
            else:
                self.evtWeightBase = genEquivalentLuminosity*genXS/genNEvents
                self.evtWeightAlt = genEquivalentLuminosity*genXS/genSumWeights
        self.era = era
        if probEvt:
            #self.probEvt = probEvt
            print("Skipping events until event #{0:d} is found".format(probEvt))
            self.verbose = True
        
        #Bits for status flag checking
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
        #flags for MET filters
        self.FlagsDict = {"2016" :  { "isData" : ["globalSuperTightHalo2016Filter"],
                                      "Common" :  ["goodVertices",
                                                   "HBHENoiseFilter",
                                                   "HBHENoiseIsoFilter",
                                                   "EcalDeadCellTriggerPrimitiveFilter",
                                                   "BadPFMuonFilter"
                                                  ],
                                      "NotRecommended" : ["BadChargedCandidateFilter",
                                                          "eeBadScFilter"
                                                         ]
                                     },
                          "2017" :  { "isData" : ["globalSuperTightHalo2016Filter"],
                                      "Common" :  ["goodVertices",
                                                   "HBHENoiseFilter",
                                                   "HBHENoiseIsoFilter",
                                                   "EcalDeadCellTriggerPrimitiveFilter",
                                                   "BadPFMuonFilter",
                                                   "ecalBadCalibFilterV2"
                                                  ],
                                      "NotRecommended" : ["BadChargedCandidateFilter",
                                                          "eeBadScFilter"
                                                         ]
                                     },
                          "2018" :  { "isData" : ["globalSuperTightHalo2016Filter"],
                                      "Common" :  ["goodVertices",
                                                   "HBHENoiseFilter",
                                                   "HBHENoiseIsoFilter",
                                                   "EcalDeadCellTriggerPrimitiveFilter",
                                                   "BadPFMuonFilter",
                                                   "ecalBadCalibFilterV2"
                                                  ],
                                      "NotRecommended" : ["BadChargedCandidateFilter",
                                                          "eeBadScFilter"
                                                         ]
                                     }
                         } 
        self.Flags = self.FlagsDict[era]
        #Btagging dictionary
        #FIXMEFIXMEFIXME
        self.bTagWorkingPointDict = {
            '2016':{
                'DeepCSV':{
                    'L': 0.2217,
                    'M': 0.6321,
                    'T': 0.8953,
                    'Var': 'btagDeepB'
                    },
                'DeepJet':{
                    'L': 0.0614,
                    'M': 0.3093,
                    'T': 0.7221,
                    'Var': 'btagDeepFlavB'
                    }
            },
            '2017':{
                'CSVv2':{
                    'L': 0.5803,
                    'M': 0.8838,
                    'T': 0.9693,
                    'Var': 'btagCSVV2'
                    },
                'DeepCSV':{
                    'L': 0.1522,
                    'M': 0.4941,
                    'T': 0.8001,
                    'Var': 'btagDeepB'
                    },
                'DeepJet':{
                    'L': 0.0521,
                    'M': 0.3033,
                    'T': 0.7489,
                    'Var': 'btagDeepFlavB'
                    }
            },
            '2018':{
                'DeepCSV':{
                    'L': 0.1241,
                    'M': 0.4184,
                    'T': 0.7527,
                    'Var': 'btagDeepB'
                    },
                'DeepJet':{
                    'L': 0.0494,
                    'M': 0.2770,
                    'T': 0.7264,
                    'Var': 'btagDeepFlavB'
                    }
            }
        }
        #Weight variations
        if self.isData:
            self.weightList = ["NONE"]
        else:
            self.weightList = ["NONE", "EWo", "EWS", "GWo", "PUo", "EP"]
            # EventWeight only (calculated from XS, Lumi, NumberGeneratedEvents)
            # GenWeight only (as stored in NanoAOD itself)
            # PileupWeight only
            # BTag weight only (not yet implemented... need btagging efficiencies(jet pt, jet eta) functionality...)
            # EP = EventWeight * PileupWeight
            # EPB = EventWeight * PileupWeight * BTagWeight

        self.lepPt = lepPt
        self.MET = MET
        self.HT = HT
        self.jetPtVar = jetPtVar
        self.jetMVar = jetMVar
        if self.verbose:
            print("Minimum lepton Pt: " + str(self.lepPt))
            print("Minimum MET: " + str(self.MET))
            print("Minimum HT: " + str(self.HT))            

        #event counters
        self.counter = 0
        self.maxEventsToProcess=maxevt

    def beginJob(self,histFile=None,histDirName=None):
        if histFile == None or histDirName == None:
            Module.beginJob(self, None, None)
        else:
            Module.beginJob(self,histFile,histDirName)
            self.ctrl_Muons = {}
            self.ctrl_Electrons = {}
            self.ctrl_Leptons = {}
            self.ctrl_Jets = {}
            self.ctrl_FatJets = {}
            self.cutflow = {}
            self.ctrl_met_phi = {}
            self.ctrl_met_pt = {}
            self.ctrl_HT = {}
            self.ctrl_nJets = {}
            
            for weight in self.weightList:
                self.cutflow[weight] = ROOT.TH1F("h_base_cutflow[{0:s}]".format(weight), "Cutflow in the baseline event selector;; Events[{0:s}]".format(weight), 1, 0, 1)
                self.addObject(self.cutflow[weight])
                self.ctrl_met_phi[weight] = ROOT.TH1F("ctrl_met_phi[{0:s}]".format(weight), "MET;MET #phi; Events[{0:s}]".format(weight), 100, -math.pi, math.pi)
                self.addObject(self.ctrl_met_phi[weight])
                self.ctrl_met_pt[weight] = ROOT.TH1F("ctrl_met_pt[{0:s}]".format(weight), "MET;MET Pt (GeV); Events[{0:s}]".format(weight), 400, 0, 2000)
                self.addObject(self.ctrl_met_pt[weight])
                self.ctrl_HT[weight] = ROOT.TH1F("ctrl_HT[{0:s}]".format(weight), "HT; HT (GeV); Events[{0:s}]".format(weight), 600, 0, 3000)
                self.addObject(self.ctrl_HT[weight])
                self.ctrl_nJets[weight] = ROOT.TH1F("ctrl_nJets[{0:s}]".format(weight), "Jets; nJets; Events[{0:s}]".format(weight), 20, 0, 20)
                self.addObject(self.ctrl_nJets[weight])
                    
                self.ctrl_Jets[weight] = {}
                self.jetPlotVars = [self.jetPtVar, "eta", "phi", self.jetMVar, "btagCSVV2", "btagDeepB", "btagDeepFlavB"]
                for i in xrange(10):
                    self.ctrl_Jets[weight][i] = {}
                    for var in self.jetPlotVars:
                        if var == self.jetPtVar:
                            xmin = 0
                            xmax = 1000
                        elif var == "eta":
                            xmin = -3.0
                            xmax = 3.0
                        elif var == "phi":
                            xmin = -math.pi
                            xmax = math.pi
                        elif var == self.jetMVar:
                            xmin = 0
                            xmax = 300
                        elif var == "btagCSVV2" or var == "btagDeepB" or var == "btagDeepFlavB":
                            xmin = 0
                            xmax = 1
                        self.ctrl_Jets[weight][i][var] = ROOT.TH1F("ctrl_Jets[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                                                                    "Pt Sorted Jet [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                        self.addObject(self.ctrl_Jets[weight][i][var])
                    
                self.ctrl_FatJets[weight] = {}
                self.jetAK8PlotVars = ["pt", "eta", "phi", "mass", "btagCSVV2", "btagDeepB", "deepTag_TvsQCD", "deepTag_WvsQCD", "deepTag_MD_bbvsLight"]
                for i in xrange(4):
                    self.ctrl_FatJets[weight][i] = {}
                    for var in self.jetAK8PlotVars:
                        if var == "pt":
                            xmin = 0
                            xmax = 1500
                        elif var == "eta":
                            xmin = -3.0
                            xmax = 3.0
                        elif var == "phi":
                            xmin = -math.pi
                            xmax = math.pi
                        elif var == "mass":
                            xmin = 0
                            xmax = 300
                        elif var in ["btagCSVV2", "btagDeepB", "deepTag_TvsQCD", "deepTag_WvsQCD", "deepTag_MD_bbvsLight"]:
                            xmin = 0
                            xmax = 1
                        self.ctrl_FatJets[weight][i][var] = ROOT.TH1F("ctrl_FatJets[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                                                                      "AK8 Jet [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                        self.addObject(self.ctrl_FatJets[weight][i][var])
    
                self.ctrl_Muons[weight] = {}
                self.ctrl_Electrons[weight] = {}
                self.ctrl_Leptons[weight] = {}
                self.leptonPlotVars = ["pt", "eta", "phi", "mass", "dz", "dxy", "jetRelIso", "ip3d"]
                for i in xrange(4):
                    self.ctrl_Muons[weight][i] = {}
                    self.ctrl_Electrons[weight][i] = {}
                    self.ctrl_Leptons[weight][i] = {}
                    for var in self.leptonPlotVars:
                        if var == "pt":
                            xmin = 0
                            xmax = 500
                        elif var == "eta":
                            xmin = -3.0
                            xmax = 3.0
                        elif var == "phi":
                            xmin = -math.pi
                            xmax = math.pi
                        elif var == "mass":
                            xmin = 0
                            xmax = 5
                        elif var == "dz":
                            xmin = 0
                            xmax = 0.02
                        elif var == "dxy" or var == "ip3d":
                            xmin = 0
                            xmax = 0.2
                        elif var in ["jetRelIso"]:
                            xmin = 0
                            xmax = 1
                        # self.ctrl_Muons[weight][i][var] = ROOT.TH1F("ctrl_Muons[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                        #                                     "Selected Muon [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                        # self.addObject(self.ctrl_Muons[weight][i][var])
                        # self.ctrl_Electrons[weight][i][var] = ROOT.TH1F("ctrl_Electrons[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                        #                                     "Selected Electron [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                        # self.addObject(self.ctrl_Electrons[weight][i][var])
                        self.ctrl_Leptons[weight][i][var] = ROOT.TH1F("ctrl_Leptons[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                                                                      "Selected Lepton [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                        self.addObject(self.ctrl_Leptons[weight][i][var])
    
            self.stitch_nGenJets = ROOT.TH1I("stitch_nGenJets", "nGenJet (pt > 30); nGenJets; Events", 18, 2, 20)
            self.addObject(self.stitch_nGenJets)
            self.stitch_GenHT = ROOT.TH1F("stitch_GenHT", "GenHT (pt > 30, |#eta| < 2.4); Gen HT (GeV); Events", 800, 200, 600)
            self.addObject(self.stitch_GenHT)
            self.stitch_nGenLeps = ROOT.TH1I("stitch_nGenLeps", "nGenLeps (e(1) or mu (1) or #tau (2)); nGenLeps; Events", 10, 0, 10)
            self.addObject(self.stitch_nGenLeps)


                    

    def endJob(self):
        if hasattr(self, 'objs') and self.objs != None:
            prevdir = ROOT.gDirectory
            self.dir.cd()
            for obj in self.objs:
                obj.Write()
            prevdir.cd()
            if hasattr(self, 'histFile') and self.histFile != None: 
                self.histFile.Close()

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.branchList = inputTree.GetListOfBranches()
        if "Jet_{0:s}".format(self.jetPtVar) not in self.branchList:
            print("Warning: expected branch Jet_{0:s} to be present, but it is not. If not added in a module preceding this one, there will be a crash.".format(self.jetPtVar))
            # for var in self.jetPlotVars:
            #     if var == self.jetPtVar:
            #         var = "pt"
            # self.jetPtVar = "pt"
        if "Jet_{0:s}".format(self.jetMVar) not in self.branchList:
            print("Warning: expected branch Jet_{0:s} to be present, but it is not. If not added in a module preceding this one, there will be a crash.".format(self.jetMVar))
            # for var in self.jetPlotVars:
            #     if var == self.jetMVar:
            #         var = "mass"
            # self.jetMVar = "mass"

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #Increment counter and skip events past the maxEventsToProcess, if larger than -1
        self.counter +=1
        if -1 < self.maxEventsToProcess < self.counter:
            return False        
        if self.probEvt:
            if event.event != self.probEvt:
                return False
        
        ###############################################
        ### Collections and Objects and isData check###
        ###############################################        
        PV = Object(event, "PV")
        otherPV = Collection(event, "OtherPV")
        SV = Collection(event, "SV")
        
        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        taus = Collection(event, "Tau")
        jets = Collection(event, "Jet")
        fatjets = Collection(event, "FatJet")
        subjets = Collection(event, "SubJet")
        if not self.isData:
            generator = Object(event, "Generator")
            btagweight = Object(event, "btagWeight") #contains .CSVV2 and .DeepCSVB float weights
            genWeight = getattr(event, "genWeight")
            LHEWeight = getattr(event, "LHEWeight_originalXWGTUP")
        if self.era == "2017":
            met = Object(event, "METFixEE2017")
        else:
            met = Object(event, "MET")

        HLT = Object(event, "HLT")
        Filters = Object(event, "Flag")

        #Set up dictionary for all the weights to be used.
        theWeight = {}

        #Begin weight calculations. Some won't work properly with cutflow, so they'll be running weights
        # ["NONE", "EWo", "PUo", "BTo", "EP", "EPB"]
        btagSFs = {}
        for jet in jets:
            pass
        for weight in self.weightList:
            if weight == "NONE":
                theWeight[weight] = 1
            elif weight == "EWo":
                theWeight[weight] = math.copysign(self.evtWeightBase, generator.weight)
            elif weight == "EWS":
                theWeight[weight] = math.copysign(self.evtWeightAlt, generator.weight)
            elif weight == "GWo":
                theWeight[weight] = genWeight/LHEWeight
            elif weight == "PUo":
                theWeight[weight] = event.puWeight #puWeightUp, puWeightDown
            elif weight == "EP":
                theWeight[weight] = math.copysign(self.evtWeightBase, generator.weight)*event.puWeight
            else:
                theWeight[weight] = -1
            self.cutflow[weight].Fill("> preselection", theWeight[weight])
        ###########
        ### MET ###
        ###########
        #Ensure MC and Data pass all recommended filters for 2017 and 2018
        for flag in self.Flags["Common"]:
            passFilters = getattr(Filters, flag)
            if not passFilters: return False
        #Check additional flag(s) solely for Data
        if self.isData:
            passFilters = getattr(Filters, self.Flags["isData"][0])
            if not passFilters: return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> MET filters", theWeight[weight])
        if met.pt < self.MET:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> MET > {0:d}".format(self.MET), theWeight[weight])



        if not self.isData:
            gens = Collection(event, "GenPart")
            genjets = Collection(event, "GenJet")
            genfatjets = Collection(event, "GenJetAK8")
            gensubjets = Collection(event, "SubGenJetAK8")
            genmet = Object(event, "GenMET")
            #These two are grabbed earlier
            # generator = Object(event, "Generator") #stored earlier for weights access
            # btagweight = Object(event, "btagWeight") #contains .CSVV2 and .DeepCSVB float weights
            #This doesn't exist yet
            # LHEReweightingWeight = Collection(event, "LHEReweightingWeight")
            #These might fail because some of the samples lack weights... axe them for now, check later when actually needed.
            # LHE = Object(event, "LHE")
            # PSWeights = Collection(event, "PSWeight")
            # LHEWeight = getattr(event, "LHEWeight_originalXWGTUP")
            # LHEScaleWeight = Collection(event, "LHEScaleWeight")
            # LHEPdfWeight = Collection(event, "LHEPdfWeight")

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
            #No weights for stitching variables
            self.stitch_nGenJets.Fill(nGJ)
            self.stitch_GenHT.Fill(GenHT)
            self.stitch_nGenLeps.Fill(nGL)
        
        selEleUniform = []
        for idx, electron in enumerate(electrons):
            d0 = math.sqrt(electron.dxy**2 + electron.dz**2)
            if ((abs(electron.eta) < 1.4442 and d0 < 0.10 and abs(electron.dz) < 0.15 ) or (abs(electron.eta) > 1.4660 and abs(electron.eta) < 3.0 and d0 < 0.15 and abs(electron.dz) < 0.25))\
               and electron.cutBased_Fall17_V1 >= 1:
                if electron.pt > self.lepPt:
                    selEleUniform.append((idx, electron))

        selMuUniform = []
        for idx, muon in enumerate(muons):
            d0 = math.sqrt(muon.dxy**2 + muon.dz**2)
            if abs(muon.eta) < 3.0 and d0 < 0.15 and abs(muon.dz) < 0.25:
                if muon.pt > self.lepPt:
                    selMuUniform.append((idx, muon))

        nMu = len(selMuUniform)
        nEle = len(selEleUniform)
        nLep = nMu + nEle
        if nLep < 2:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> Dilepton", theWeight[weight])
        
        selJets = []
        for idx, jet in enumerate(jets):
            if abs(jet.eta) < 3.0 and jet.jetId >= 2 and getattr(jet, self.jetPtVar) > 20  and jet.cleanmask:
                selJets.append((idx, jet))

        nJets = len(selJets)
        if nJets < 3:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> 3+ Jets", theWeight[weight])

        #HT and other calculations
        HT = 0
        
        for j, jet in selJets:
            HT += getattr(jet, self.jetPtVar)

        if HT < self.HT:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> HT > {0:d}".format(self.HT), theWeight[weight])


        #####################
        ### Control Plots ###
        #####################
        for weight in self.weightList:
            self.ctrl_met_phi[weight].Fill(met.phi ,theWeight[weight])
            self.ctrl_met_pt[weight].Fill(met.pt ,theWeight[weight])
            self.ctrl_HT[weight].Fill(HT ,theWeight[weight])
            self.ctrl_nJets[weight].Fill(nJets ,theWeight[weight])
            for var in self.jetPlotVars:
                for i, jettup in enumerate(selJets):
                    try:
                        self.ctrl_Jets[weight][i][var].Fill(getattr(jettup[1], var), theWeight[weight])
                    except:
                        pass
            for var in self.jetAK8PlotVars:
                for i, jet in enumerate(fatjets):
                    try:
                        self.ctrl_FatJets[weight][i][var].Fill(getattr(jet, var), theWeight[weight])
                    except:
                        pass
            for var in self.leptonPlotVars:
                for i, leptup in enumerate(selMuUniform + selEleUniform):
                    try:
                        self.ctrl_Leptons[weight][i][var].Fill(getattr(leptup[1], var), theWeight[weight])
                    except:
                        pass
    

        return True
