from __future__ import division, print_function
import ROOT
import math
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.intools import *

class BaselineSelector(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt=None, isData=True, 
                 genEquivalentLuminosity=1, genXS=1, genNEvents=1, era="2017", btagging=['DeepCSV','M'], lepPt=25, MET=50, HT=500, invertZWindow=False, invertZWindowEarlyReturn=True, GenTop_LepSelection=None, jetPtVar = "pt_nom", jetMVar = "mass_nom"):
        self.writeHistFile=True
        self.verbose=verbose
        self.probEvt = probEvt
        self.isData = isData
        if self.isData:
            self.evtWeightBase = 1
        else:
            if genEquivalentLuminosity == 1 and genXS == 1 and genNEvents == 1:
                self.evtWeightBase = None
            else:
                self.evtWeightBase = genEquivalentLuminosity*genXS/genNEvents
        self.btagging = btagging
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
            self.weightList = ["NONE", "EWo", "GWo", "PUo", "BTo", "EP", "EPB"]
            # EventWeight only (calculated from XS, Lumi, NumberGeneratedEvents)
            # GenWeight only (as stored in NanoAOD itself)
            # PileupWeight only
            # BTag weight only (not yet implemented... need btagging efficiencies(jet pt, jet eta) functionality...)
            # EP = EventWeight * PileupWeight
            # EPB = EventWeight * PileupWeight * BTagWeight

            

        #BTagging method, algorithm name, and chosen selection working point
        self.BTMeth = self.bTagWorkingPointDict[era][btagging[0]]
        self.BTWP =  self.bTagWorkingPointDict[era][btagging[0]][btagging[1]]
        self.BTAlg = self.bTagWorkingPointDict[era][btagging[0]]["Var"]
        self.lepPt = lepPt
        self.MET = MET
        self.HT = HT
        self.invertZWindow = invertZWindow
        self.invertZWindowEarlyReturn = invertZWindowEarlyReturn
        self.jetPtVar = jetPtVar
        self.jetMVar = jetMVar
        if self.verbose:
            print("BTMeth " + str(self.BTMeth))
            print("BTWP " + str(self.BTWP))
            print("BTAlg " + str(self.BTAlg))
            print("Minimum lepton Pt: " + str(self.lepPt))
            print("Minimum MET: " + str(self.MET))
            print("Minimum HT: " + str(self.HT))
            print("Inverted Z window: " + str(self.invertZWindow))
            print("Inverted Z window early return: " + str(self.invertZWindowEarlyReturn))
            

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
            self.ctrl_BJets = {}
            self.ctrl_AJets = {}
            self.ctrl_FatJets = {}
            self.cutflow = {}
            self.ctrl_met_phi = {}
            self.ctrl_met_pt = {}
            self.ctrl_HT = {}
            self.ctrl_H = {}
            self.ctrl_HTb = {}
            self.ctrl_HT2M = {}
            self.ctrl_H2M = {}
            self.ctrl_HTH = {}
            self.ctrl_HTRat = {}
            self.ctrl_dRbb = {}
            self.ctrl_DLM = {}
            self.ctrl_nJets = {}
            self.ctrl_nJets_BTL = {}
            self.ctrl_nJets_BTM = {}
            self.ctrl_nJets_BTT = {}
            
            for weight in self.weightList:
                self.cutflow[weight] = ROOT.TH1F("h_base_cutflow[{0:s}]".format(weight), "Cutflow in the baseline event selector;; Events[{0:s}]".format(weight), 1, 0, 1)
                self.addObject(self.cutflow[weight])
                self.ctrl_met_phi[weight] = ROOT.TH1F("ctrl_met_phi[{0:s}]".format(weight), "MET;MET #phi; Events[{0:s}]".format(weight), 100, -math.pi, math.pi)
                self.addObject(self.ctrl_met_phi[weight])
                self.ctrl_met_pt[weight] = ROOT.TH1F("ctrl_met_pt[{0:s}]".format(weight), "MET;MET Pt (GeV); Events[{0:s}]".format(weight), 400, 0, 2000)
                self.addObject(self.ctrl_met_pt[weight])
                self.ctrl_HT[weight] = ROOT.TH1F("ctrl_HT[{0:s}]".format(weight), "HT; HT (GeV); Events[{0:s}]".format(weight), 600, 0, 3000)
                self.addObject(self.ctrl_HT[weight])
                self.ctrl_H[weight] = ROOT.TH1F("ctrl_H[{0:s}]".format(weight), "H; H (GeV); Events[{0:s}]".format(weight), 600, 0, 3000)
                self.addObject(self.ctrl_H[weight])
                self.ctrl_HTb[weight] = ROOT.TH1F("ctrl_HTb[{0:s}]".format(weight), "HTb; HTb (GeV); Events[{0:s}]".format(weight), 400, 0, 2000)
                self.addObject(self.ctrl_HTb[weight])
                self.ctrl_HT2M[weight] = ROOT.TH1F("ctrl_HT2M[{0:s}]".format(weight), "HT2M; HT2M (GeV); Events[{0:s}]".format(weight), 400, 0, 2000)
                self.addObject(self.ctrl_HT2M[weight])
                self.ctrl_H2M[weight] = ROOT.TH1F("ctrl_H2M[{0:s}]".format(weight), "H2M; H2M (GeV); Events[{0:s}]".format(weight), 600, 0, 3000)
                self.addObject(self.ctrl_H2M[weight])
                self.ctrl_HTH[weight] = ROOT.TH1F("ctrl_HTH[{0:s}]".format(weight), "HTH; HTH; Events[{0:s}]".format(weight), 400, 0, 1)
                self.addObject(self.ctrl_HTH[weight])
                self.ctrl_HTRat[weight] = ROOT.TH1F("ctrl_HTRat[{0:s}]".format(weight), "HTRat; HTRat; Events[{0:s}]".format(weight), 400, 0, 1)
                self.addObject(self.ctrl_HTRat[weight])
                self.ctrl_dRbb[weight] = ROOT.TH1F("ctrl_dRbb[{0:s}]".format(weight), "dR bb; dRbb; Events[{0:s}]".format(weight), 400, 0, 8)
                self.addObject(self.ctrl_dRbb[weight])
                self.ctrl_DLM[weight] = ROOT.TH1F("ctrl_DLM[{0:s}]".format(weight), "Same-flavor Dilepton Invariant Mass; Mass (GeV); Events[{0:s}]".format(weight), 400, 0, 400)
                self.addObject(self.ctrl_DLM[weight])
                self.ctrl_nJets[weight] = ROOT.TH1F("ctrl_nJets[{0:s}]".format(weight), "Jets; nJets; Events[{0:s}]".format(weight), 20, 0, 20)
                self.addObject(self.ctrl_nJets[weight])
                self.ctrl_nJets_BTL[weight] = ROOT.TH1F("ctrl_nJets_BTL[{0:s}]".format(weight), "Loose b-Tagged Jets; nJets; Events[{0:s}]".format(weight), 12, 0, 12)
                self.addObject(self.ctrl_nJets_BTL[weight])
                self.ctrl_nJets_BTM[weight] = ROOT.TH1F("ctrl_nJets_BTM[{0:s}]".format(weight), "Medium b-Tagged Jets; nJets; Events[{0:s}]".format(weight), 12, 0, 12)
                self.addObject(self.ctrl_nJets_BTM[weight])
                self.ctrl_nJets_BTT[weight] = ROOT.TH1F("ctrl_nJets_BTT[{0:s}]".format(weight), "Tight b-Tagged Jets; nJets; Events[{0:s}]".format(weight), 12, 0, 12)
                self.addObject(self.ctrl_nJets_BTT[weight])
    
                self.ctrl_BJets[weight] = {}
                self.ctrl_AJets[weight] = {}
                self.jetPlotVars = [self.jetPtVar, "eta", "phi", self.jetMVar, "btagCSVV2", "btagDeepB", "btagDeepFlavB"]
                for i in xrange(8):
                    self.ctrl_BJets[weight][i] = {}
                    self.ctrl_AJets[weight][i] = {}
                    for var in self.jetPlotVars:
                        if var == "pt":
                            xmin = 0
                            xmax = 1000
                        elif var == "eta":
                            xmin = -2.6
                            xmax = 2.6
                        elif var == "phi":
                            xmin = -math.pi
                            xmax = math.pi
                        elif var == "mass":
                            xmin = 0
                            xmax = 300
                        elif var == "btagCSVV2" or var == "btagDeepB" or var == "btagDeepFlavB":
                            xmin = 0
                            xmax = 1
                        self.ctrl_BJets[weight][i][var] = ROOT.TH1F("ctrl_BJets[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                                                                    "B-tagged Jet [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                        self.addObject(self.ctrl_BJets[weight][i][var])
                        self.ctrl_AJets[weight][i][var] = ROOT.TH1F("ctrl_AJets[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                                                                    "Pt Sorted Jet [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                        self.addObject(self.ctrl_AJets[weight][i][var])
                    
                self.ctrl_FatJets[weight] = {}
                self.jetAK8PlotVars = ["pt", "eta", "phi", "mass", "btagCSVV2", "btagDeepB", "deepTag_TvsQCD", "deepTag_WvsQCD", "deepTag_MD_bbvsLight"]
                for i in xrange(4):
                    self.ctrl_FatJets[weight][i] = {}
                    for var in self.jetAK8PlotVars:
                        if var == "pt":
                            xmin = 0
                            xmax = 1500
                        elif var == "eta":
                            xmin = -2.6
                            xmax = 2.6
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
                for i in xrange(2):
                    self.ctrl_Muons[weight][i] = {}
                    self.ctrl_Electrons[weight][i] = {}
                    self.ctrl_Leptons[weight][i] = {}
                    for var in self.leptonPlotVars:
                        if var == "pt":
                            xmin = 0
                            xmax = 500
                        elif var == "eta":
                            xmin = -2.6
                            xmax = 2.6
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
            print("Warning: expected branch Jet_{0:s} to be present, but it is not. Switching to Jet_pt".format(self.jetPtVar))
            for var in self.jetPlotVars:
                if var == self.jetPtVar:
                    var = "pt"
            self.jetPtVar = "pt"
        if "Jet_{0:s}".format(self.jetMVar) not in self.branchList:
            print("Warning: expected branch Jet_{0:s} to be present, but it is not. Switching to Jet_mass".format(self.jetMVar))
            for var in self.jetPlotVars:
                if var == self.jetMVar:
                    var = "mass"
            self.jetMVar = "mass"
        self.out = wrappedOutputTree
        self.varDict = [('nJet', 'I', 'Number of jets passing selection requirements'),
                        ('nJetBTL', 'I', 'Number of jets passing selection requirements and loose b-tagged'),
                        ('nJetBTM', 'I', 'Number of jets passing selection requirements and medium b-tagged'),
                        ('nJetBTT', 'I', 'Number of jets passing selection requirements and tight b-tagged'),
                        # ('tHasHadronicWDauTau', 'O', ' '),
                        ('HT', 'D', 'Scalar sum of selected jets\' Pt'),
                        ('H', 'D', 'Scalar sum of selected jets\' P'),
                        ('HT2M', 'D', 'Scalar sum of selected jets\' Pt except 2 highest b-tagged if they are medium or tight'),
                        ('H2M', 'D', 'Scalar sum of selected jets\' P except 2 highest b-tagged if they are medium or tight'),
                        ('HTb', 'D', 'Scalar sum of Pt for medium and tight b-tagged jets'),
                        ('HTH', 'D', 'Hadronic centrality, HT/H'),
                        ('HTRat', 'D', 'Ratio of Pt for two highest b-tagged jets to HT'),
                        ('dRbb', 'D', 'DeltaR between the two highest b-tagged jets'),
                        ('DiLepMass', 'D', 'Invariant mass of same-flavour leptons (0 default)'),
                       ]
        if not self.out:
            print("No Output file selected, cannot append branches")
        else:
            # self.out.branch('nESV', 'i', title='number of event selection ')
            for name, valType, valTitle in self.varDict:
                #print("name: " + str(name) + " valType: " + str(valType) + " valTitle: " + str(valTitle))
                # self.out.branch("Temp_%s"%(name), valType, lenVar="nGenTop", title=valTitle)
                self.out.branch("ESV_%s"%(name), valType, title=valTitle)


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
            elif weight == "GWo":
                theWeight[weight] = generator.weight
            elif weight == "PUo":
                theWeight[weight] = event.puWeight #puWeightUp, puWeightDown
            elif weight == "BTo":
                if self.BTAlg == "btagCSVV2":
                    theWeight[weight] = btagweight.CSVV2
                elif self.BTAlg == "btagDeepB":
                    theWeight[weight] = btagweight.DeepCSVB                    
                else:
                    theWeight[weight] = 1.0 
            elif weight == "EP":
                theWeight[weight] = math.copysign(self.evtWeightBase, generator.weight)*event.puWeight
            elif weight == "EPB":
                #FIXME
                #Dangerous implementation... depending on "BTo" to be in the list and evaluated first
                #Needs to be replaced once a stable and consistent btagweight calculator is in place.
                theWeight[weight] = math.copysign(self.evtWeightBase, generator.weight)*event.puWeight*theWeight["BTo"]
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
        

        # selEle25 = []
        # selEle20 = []
        # selEle15 = []
        selEleUniform = []
        for idx, electron in enumerate(electrons):
            if (abs(electron.eta) < 1.4442 or (abs(electron.eta) > 1.4660 and abs(electron.eta) < 2.4)) and electron.cutBased_Fall17_V1 >= 2 and electron.dz < 0.02:
                if electron.pt > self.lepPt:
                    selEleUniform.append((idx, electron))
        #         if electron.pt > 25:
        #             selMu25.append((idx, electron))
        #         elif electron.pt > 20:
        #             selMu20.append((idx, electron))
        #         elif electron.pt > 15:
        #             selMu15.append((idx, electron))

        # selMu25 = []
        # selMu20 = []
        # selMu15 = []
        selMuUniform = []
        for idx, muon in enumerate(muons):
            if abs(muon.eta) < 2.4 and muon.pfIsoId >= 4 and muon.dz < 0.02:
                if muon.pt > self.lepPt:
                    selMuUniform.append((idx, muon))
        #         if muon.pt > 25:
        #             selMu25.append((idx, muon))
        #         elif muon.pt > 20:
        #             selMu20.append((idx, muon))
        #         elif muon.pt > 15:
        #             selMu15.append((idx, muon))

        # nMu = len(selMu25) + len(selMu20) + len(selMu15)
        # nEle = len(selEle25) + len(selEle20) + len(selEle15)
        # n25 = len(selMu25) + len(selEle25)
        # n20 = len(selMu20) + len(selEle20)
        # n15 = len(selMu15) + len(selEle15)
        
        # if nMu + nEle == 2:
        #     if nMu == 2:
        #         selHigh = selMu25 + selMu20
        #         selLow = selMu15
        #     elif nEle == 2:
        #         selHigh = selEle25
        #         selLow = selEle20 + selEle15
        #     else:
        #         pass
        # else:
        #     return False

        nMu = len(selMuUniform)
        nEle = len(selEleUniform)
        nLep = nMu + nEle
        if nLep != 2:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> Dilepton", theWeight[weight])
        lepCharge = [lep[1].charge for lep in (selMuUniform + selEleUniform)]
        jetsToClean = set([lep[1].jetIdx for lep in (selMuUniform + selEleUniform)])
        if len(lepCharge) !=2:
            print("Danger Will Robinson! Danger!")
        if lepCharge[0]*lepCharge[1] > 0:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> OS Leps", theWeight[weight])
        Lep4Mom = [lep[1].p4() for lep in (selMuUniform + selEleUniform)]
        #calc invariant mass if two same flavor leptons
        if nMu == 2 or nEle == 2:
            DiLepMass = (Lep4Mom[0] + Lep4Mom[1]).M()
            #Low mass resonance rejection
            if DiLepMass < 20:
                return False
            for weight in self.weightList:
                self.cutflow[weight].Fill("> Low M Res", theWeight[weight])
            #Z mass resonance rejection or inversion
            if self.invertZWindow:
                if abs(DiLepMass - 91.0) > 15.0:
                    return False
                for weight in self.weightList:
                    self.cutflow[weight].Fill("> Z Window (IN)", theWeight[weight])
                if self.invertZWindowEarlyReturn:
                    return True
            elif not self.invertZWindow:
                if abs(DiLepMass - 91.0) < 15.0:
                    return False
                for weight in self.weightList:
                    self.cutflow[weight].Fill("> Z Window (OUT)", theWeight[weight])
        else:
            #0 default for different flavour leptons
            DiLepMass = -1
            #consistent cutflow histogramming...
            for weight in self.weightList:
                self.cutflow[weight].Fill("> Low M Res", theWeight[weight])
            if self.invertZWindow:
                for weight in self.weightList:
                    self.cutflow[weight].Fill("> Z Window (IN)", theWeight[weight])
            elif not self.invertZWindow:
                for weight in self.weightList:
                    self.cutflow[weight].Fill("> Z Window (OUT)", theWeight[weight])
        
        selJets = []
        selBTsortedJets = []
        for idx, jet in enumerate(jets):
            if abs(jet.eta) < 2.4 and jet.jetId >= 6 and ((getattr(jet, self.jetPtVar) > 25 and getattr(jet, self.BTAlg) > self.BTWP) or getattr(jet, self.jetPtVar) > 30) and idx not in jetsToClean:
                selJets.append((idx, jet))
                selBTsortedJets.append((idx, jet))
        selBTsortedJets.sort(key=lambda j : getattr(j[1], self.BTAlg), reverse=True)

        #B-tagged jets
        selBTLooseJets = [jetTup for jetTup in selBTsortedJets if getattr(jetTup[1], self.BTAlg) > self.BTMeth['L']]
        selBTMediumJets = [jetTup for jetTup in selBTLooseJets if getattr(jetTup[1], self.BTAlg) > self.BTMeth['M']]
        selBTTightJets = [jetTup for jetTup in selBTMediumJets if getattr(jetTup[1], self.BTAlg) > self.BTMeth['T']]
        nJets = len(selJets)
        nBTLoose = len(selBTLooseJets)
        nBTMedium = len(selBTMediumJets)
        nBTTight = len(selBTTightJets)

        if nJets < 4:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> 4+ Jets", theWeight[weight])
        if nBTMedium < 2:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> 2+ Btag Jets", theWeight[weight])

        #HT and other calculations
        HT = 0
        H = 0
        HT2M = 0
        H2M = 0
        HTb = 0
        HTH = 0
        HTRat = 0
        dRbb = -1

        
        for j, jet in selBTsortedJets:
            HT += getattr(jet, self.jetPtVar)
            jetP4 = ROOT.TLorentzVector()
            jetP4.SetPtEtaPhiM(getattr(jet, self.jetPtVar),
                               getattr(jet, "eta"),
                               getattr(jet, "phi"),
                               getattr(jet, self.jetMVar)
            )
            H += jetP4.P()
            if j > 1 and nBTMedium > 1:
                HT2M += getattr(jet, self.jetPtVar)
                H2M += jetP4.P()
            if getattr(jet, self.BTAlg) > self.BTWP:
                HTb += getattr(jet, self.jetPtVar)

        if HT < self.HT:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> HT > {0:d}".format(self.HT), theWeight[weight])

        if nJets > 3: #redundant, but only so long as 4 jet cut is in place
            jet1 = selBTsortedJets[0][1]
            jet2 = selBTsortedJets[1][1]
            dRbb = deltaR(jet1, jet2)
            HTRat = (jet1.pt + jet2.pt)/HT
            HTH = HT/H

        #####################
        ### Control Plots ###
        #####################
        for weight in self.weightList:
            self.ctrl_met_phi[weight].Fill(met.phi ,theWeight[weight])
            self.ctrl_met_pt[weight].Fill(met.pt ,theWeight[weight])
            self.ctrl_HT[weight].Fill(HT ,theWeight[weight])
            self.ctrl_H[weight].Fill(H ,theWeight[weight])
            self.ctrl_HTb[weight].Fill(HTb ,theWeight[weight])
            self.ctrl_HT2M[weight].Fill(HT2M ,theWeight[weight])
            self.ctrl_H2M[weight].Fill(H2M ,theWeight[weight])
            self.ctrl_HTH[weight].Fill(HTH ,theWeight[weight])
            self.ctrl_HTRat[weight].Fill(HTRat ,theWeight[weight])
            self.ctrl_dRbb[weight].Fill(dRbb ,theWeight[weight])
            self.ctrl_DLM[weight].Fill(DiLepMass ,theWeight[weight])
            self.ctrl_nJets[weight].Fill(nJets ,theWeight[weight])
            self.ctrl_nJets_BTL[weight].Fill(nBTLoose ,theWeight[weight])
            self.ctrl_nJets_BTM[weight].Fill(nBTMedium ,theWeight[weight])
            self.ctrl_nJets_BTT[weight].Fill(nBTTight ,theWeight[weight])
            for var in self.jetPlotVars:
                for i, jettup in enumerate(selJets):
                    try:
                        self.ctrl_AJets[weight][i][var].Fill(getattr(jettup[1], var), theWeight[weight])
                    except:
                        pass
                for i, jettup in enumerate(selBTsortedJets):
                    try:
                        self.ctrl_BJets[weight][i][var].Fill(getattr(jettup[1], var), theWeight[weight])
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
    
    
        ####################################
        ### Variables for branch filling ###
        ####################################
        ESV = {}
        ESV['nJet'] = nJets
        ESV['nJetBTL'] = nBTLoose
        ESV['nJetBTM'] = nBTMedium
        ESV['nJetBTT'] = nBTTight
        ESV['HT'] = HT
        ESV['H'] = H
        ESV['HT2M'] = HT2M
        ESV['H2M'] = H2M
        ESV['HTb'] = HTb
        ESV['HTH'] = HTH
        ESV['HTRat'] = HTRat
        ESV['dRbb'] = dRbb
        ESV['DiLepMass'] = DiLepMass

        ########################## 
        ### Write out branches ###
        ##########################         
        if self.out:
            # self.out.fillBranch("nGenTop", nGenTop)
            for name, valType, valTitle in self.varDict:
                self.out.fillBranch("ESV_%s"%(name), ESV[name])


        return True
