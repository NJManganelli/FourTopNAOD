from __future__ import division, print_function
import ROOT
import math
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.toolbox import *

class JetMETLogic(Module):
    def __init__(self, passLevel, enforceMCCascade=True, era="2013", subera=None, isData=False, TriggerChannel=None, weightMagnitude=1, fillHists=False, debug=False, mode="Flag"):
    def __init__(self, verbose=False, probEvt=None, era="2017", subera=None, isData=True, weightMagnitude=1, fillHists=False, btagging=['DeepCSV', 'M'], MET=[45, 50], HT=[450,500], ZWidth=15,
                 jetPtVar = "pt_nom", jetMVar = "mass_nom"):
                 # genEquivalentLuminosity=1, genXS=1, genNEvents=1, genSumWeights=1, era="2017", btagging=['DeepCSV','M'], lepPt=25,  GenTop_LepSelection=None):
        self.passLevel = passLevel
        self.writeHistFile=True
        self.fillHists = fillHists
        if self.fillHists and not self.writeHistFile:
            self.writeHistFile=True
        self.verbose=verbose
        self.probEvt = probEvt
        self.isData = isData
        if self.isData:
            self.evtWeightBase = 1
        else:
            
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

        #Bits for status flag checking
        self.passbits = {'PV_minNDoF':0b00000000000000000001,
                         'PV_maxAbsZ':0b00000000000000000010,
                         'PV_maxRho':0b00000000000000000100,
                         'MET_globalSuperTightHalo2016Filter':0b00000000000000001000,
                         'MEt_goodVertices':0b00000000000000010000,
                         'MET_HBHENoiseFilter':0b00000000000000100000,
                         'MET_HBHENoiseIsoFilter':0b00000000000001000000,
                         'MET_EcalDeadCellTriggerPrimitiveFilter':0b00000000000010000000,
                         'MET_BadPFMuonFilter':0b00000000000100000000,
                         'MET_ecalBadCalibFilterV2':0b00000000001000000000,
                         'MET_pt_baseline':0b00000000010000000000,
                         'MET_pt_selection':0b00000000100000000000,
                         'Lepton_ZWindow':0b00000001000000000000,
                         'Jet_nJet25':0b00000010000000000000,
                         'Jet_nJet20':0b00000100000000000000
                         'HT':0b00001000000000000000
                         'Jet_nBJet_2DCSV':0b00010000000000000000
                         'Jet_nBJet_2DJet':0b00100000000000000000
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
        #2016selection required !isFake(), nDegreesOfFreedom> 4 (strictly),|z| < 24 (in cm? fractions of acentimeter?), and rho =sqrt(PV.x**2 + PV.y**2)< 2
        #Cuts are to use strictly less than and greater than, i.e. PV.ndof > minNDoF, not >=
        self.PVCutDict = {
            '2016':{
                'minNDoF': 4,
                'maxAbsZ': 24.0,
                'maxRho': 2
                },
            '2017':{
                'minNDoF': 4,
                'maxAbsZ': 24.0,
                'maxRho': 2
                },
            '2018':{
                'minNDoF': 4,
                'maxAbsZ': 24.0,
                'maxRho': 2
                }
        }
        self.PVCut = self.PVCutDict[era]


        #Weight variations
        if self.isData:
            self.weightList = ["NONE"]
        else:
            # self.weightList = ["NONE", "EWo", "EWS", "PUo", "EP"]
            self.weightList = ["NOM"]
            #NOM will be XS weight * PU weight * L1Prefiring weight? No Lepton weights, yet
            

        #BTagging method, algorithm name, and chosen selection working point
        self.BTName = btagging[0]
        self.BTMeth = self.bTagWorkingPointDict[era][btagging[0]]
        self.BTWP =  self.bTagWorkingPointDict[era][btagging[0]][btagging[1]]
        self.BTAlg = self.bTagWorkingPointDict[era][btagging[0]]["Var"]
        self.lepPt = lepPt
        self.MET = MET
        self.HT = HT
        self.ZWidth = ZWidth
        # self.invertZWindow = invertZWindow
        # self.invertZWindowEarlyReturn = invertZWindowEarlyReturn
        self.jetPtVar = jetPtVar
        self.jetMVar = jetMVar
        if self.verbose:
            print("BTMeth " + str(self.BTMeth))
            print("BTWP " + str(self.BTWP))
            print("BTAlg " + str(self.BTAlg))
            print("Minimum lepton Pt: " + str(self.lepPt))
            print("Minimum MET[Baseline, Selection]: " + str(self.MET))
            print("Minimum HT[Baseline, Selection]: " + str(self.HT))
            print("Z Window Width for veto bit: " + str(self.ZWidth))
            # print("Inverted Z window: " + str(self.invertZWindow))
            # print("Inverted Z window early return: " + str(self.invertZWindowEarlyReturn))
            

        #event counters
        self.counter = 0

    def beginJob(self, histFile=None,histDirName=None):
        if self.fillHists == False and self.writehistFile == False:
            Module.beginJob(self, None, None)
        else:
            if histFile == None or histDirName == None:
                raise RuntimeError("fillHists set to True, but no histFile or histDirName specified")
            Module.beginJob(self,histFile,histDirName)
            # self.ctrl_Muons = {}
            # self.ctrl_Electrons = {}
            # self.ctrl_Leptons = {}
            # self.ctrl_BJets = {}
            # self.ctrl_AJets = {}
            # self.ctrl_FatJets = {}
            # self.cutflow = {}
            # self.ctrl_met_phi = {}
            # self.ctrl_met_pt = {}
            # self.ctrl_HT = {}
            # self.ctrl_H = {}
            # self.ctrl_HTb = {}
            # self.ctrl_HT2M = {}
            # self.ctrl_H2M = {}
            # self.ctrl_HTH = {}
            # self.ctrl_HTRat = {}
            # self.ctrl_dRbb = {}
            # self.ctrl_DLM = {}
            # self.ctrl_nJets = {}
            # self.ctrl_nJets_BTL = {}
            # self.ctrl_nJets_BTM = {}
            # self.ctrl_nJets_BTT = {}
            
            # for weight in self.weightList:
            #     self.cutflow[weight] = ROOT.TH1F("h_base_cutflow_{}".format(weight), "Cutflow in the baseline event selector;; Events".format(weight), 1, 0, 1)
            #     self.addObject(self.cutflow[weight])
            #     self.ctrl_met_phi[weight] = ROOT.TH1F("ctrl_met_phi_{}".format(weight), "MET;MET #phi; Events".format(weight), 100, -math.pi, math.pi)
            #     self.addObject(self.ctrl_met_phi[weight])
            #     self.ctrl_met_pt[weight] = ROOT.TH1F("ctrl_met_pt_{}".format(weight), "MET;MET Pt (GeV); Events".format(weight), 400, 0, 2000)
            #     self.addObject(self.ctrl_met_pt[weight])
            #     self.ctrl_HT[weight] = ROOT.TH1F("ctrl_HT_{}".format(weight), "HT; HT (GeV); Events".format(weight), 600, 0, 3000)
            #     self.addObject(self.ctrl_HT[weight])
            #     self.ctrl_H[weight] = ROOT.TH1F("ctrl_H_{}".format(weight), "H; H (GeV); Events".format(weight), 600, 0, 3000)
            #     self.addObject(self.ctrl_H[weight])
            #     self.ctrl_HTb[weight] = ROOT.TH1F("ctrl_HTb_{}".format(weight), "HTb; HTb (GeV); Events".format(weight), 400, 0, 2000)
            #     self.addObject(self.ctrl_HTb[weight])
            #     self.ctrl_HT2M[weight] = ROOT.TH1F("ctrl_HT2M_{}".format(weight), "HT2M; HT2M (GeV); Events".format(weight), 400, 0, 2000)
            #     self.addObject(self.ctrl_HT2M[weight])
            #     self.ctrl_H2M[weight] = ROOT.TH1F("ctrl_H2M_{}".format(weight), "H2M; H2M (GeV); Events".format(weight), 600, 0, 3000)
            #     self.addObject(self.ctrl_H2M[weight])
            #     self.ctrl_HTH[weight] = ROOT.TH1F("ctrl_HTH_{}".format(weight), "HTH; HTH; Events".format(weight), 400, 0, 1)
            #     self.addObject(self.ctrl_HTH[weight])
            #     self.ctrl_HTRat[weight] = ROOT.TH1F("ctrl_HTRat_{}".format(weight), "HTRat; HTRat; Events".format(weight), 400, 0, 1)
            #     self.addObject(self.ctrl_HTRat[weight])
            #     self.ctrl_dRbb[weight] = ROOT.TH1F("ctrl_dRbb_{}".format(weight), "dR bb; dRbb; Events".format(weight), 400, 0, 8)
            #     self.addObject(self.ctrl_dRbb[weight])
            #     self.ctrl_DLM[weight] = ROOT.TH1F("ctrl_DLM_{}".format(weight), "Same-flavor Dilepton Invariant Mass; Mass (GeV); Events".format(weight), 400, 0, 400)
            #     self.addObject(self.ctrl_DLM[weight])
            #     self.ctrl_nJets[weight] = ROOT.TH1F("ctrl_nJets_{}".format(weight), "Jets; nJets; Events".format(weight), 20, 0, 20)
            #     self.addObject(self.ctrl_nJets[weight])
            #     self.ctrl_nJets_BTL[weight] = ROOT.TH1F("ctrl_nJets_BTL_{}".format(weight), "Loose b-Tagged Jets; nJets; Events".format(weight), 12, 0, 12)
            #     self.addObject(self.ctrl_nJets_BTL[weight])
            #     self.ctrl_nJets_BTM[weight] = ROOT.TH1F("ctrl_nJets_BTM_{}".format(weight), "Medium b-Tagged Jets; nJets; Events".format(weight), 12, 0, 12)
            #     self.addObject(self.ctrl_nJets_BTM[weight])
            #     self.ctrl_nJets_BTT[weight] = ROOT.TH1F("ctrl_nJets_BTT_{}".format(weight), "Tight b-Tagged Jets; nJets; Events".format(weight), 12, 0, 12)
            #     self.addObject(self.ctrl_nJets_BTT[weight])
    
            #     self.ctrl_BJets[weight] = {}
            #     self.ctrl_AJets[weight] = {}
            #     self.jetPlotVars = [self.jetPtVar, "eta", "phi", self.jetMVar, "btagCSVV2", "btagDeepB", "btagDeepFlavB"]
            #     for i in xrange(8):
            #         self.ctrl_BJets[weight][i] = {}
            #         self.ctrl_AJets[weight][i] = {}
            #         for var in self.jetPlotVars:
            #             if var == self.jetPtVar:
            #                 xmin = 0
            #                 xmax = 1000
            #             elif var == "eta":
            #                 xmin = -2.6
            #                 xmax = 2.6
            #             elif var == "phi":
            #                 xmin = -math.pi
            #                 xmax = math.pi
            #             elif var == self.jetMVar:
            #                 xmin = 0
            #                 xmax = 300
            #             elif var == "btagCSVV2" or var == "btagDeepB" or var == "btagDeepFlavB":
            #                 xmin = 0
            #                 xmax = 1
            #             self.ctrl_BJets[weight][i][var] = ROOT.TH1F("ctrl_BJets_{0}_{1:d}_{2:s}".format(weight, i, var), 
            #                                                         "B-tagged Jet {0:d}; BTag sorted Jet {1:s}; Events_{2:s}".format(i, var, weight), 100, xmin, xmax)
            #             self.addObject(self.ctrl_BJets[weight][i][var])
            #             self.ctrl_AJets[weight][i][var] = ROOT.TH1F("ctrl_AJets_{0}_{1:d}_{2:s}".format(weight, i, var), 
            #                                                         "Pt Sorted Jet {0:d}; Pt sorted Jet {1:s}; Events_{2:s}".format(i, var, weight), 100, xmin, xmax)
            #             self.addObject(self.ctrl_AJets[weight][i][var])
                    
                # self.ctrl_FatJets[weight] = {}
                # self.jetAK8PlotVars = ["pt", "eta", "phi", "mass", "btagCSVV2", "btagDeepB", "deepTag_TvsQCD", "deepTag_WvsQCD", "deepTag_MD_bbvsLight"]
                # for i in xrange(4):
                #     self.ctrl_FatJets[weight][i] = {}
                #     for var in self.jetAK8PlotVars:
                #         if var == "pt":
                #             xmin = 0
                #             xmax = 1500
                #         elif var == "eta":
                #             xmin = -2.6
                #             xmax = 2.6
                #         elif var == "phi":
                #             xmin = -math.pi
                #             xmax = math.pi
                #         elif var == "mass":
                #             xmin = 0
                #             xmax = 300
                #         elif var in ["btagCSVV2", "btagDeepB", "deepTag_TvsQCD", "deepTag_WvsQCD", "deepTag_MD_bbvsLight"]:
                #             xmin = 0
                #             xmax = 1
                #         self.ctrl_FatJets[weight][i][var] = ROOT.TH1F("ctrl_FatJets[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                #                                                       "AK8 Jet [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                #         self.addObject(self.ctrl_FatJets[weight][i][var])
    
                # self.ctrl_Muons[weight] = {}
                # self.ctrl_Electrons[weight] = {}
                # self.ctrl_Leptons[weight] = {}
                # self.leptonPlotVars = ["pt", "eta", "phi", "mass", "dz", "dxy", "jetRelIso", "ip3d"]
                # for i in xrange(2):
                #     self.ctrl_Muons[weight][i] = {}
                #     self.ctrl_Electrons[weight][i] = {}
                #     self.ctrl_Leptons[weight][i] = {}
                #     for var in self.leptonPlotVars:
                #         if var == "pt":
                #             xmin = 0
                #             xmax = 500
                #         elif var == "eta":
                #             xmin = -2.6
                #             xmax = 2.6
                #         elif var == "phi":
                #             xmin = -math.pi
                #             xmax = math.pi
                #         elif var == "mass":
                #             xmin = 0
                #             xmax = 5
                #         elif var == "dz":
                #             xmin = 0
                #             xmax = 0.02
                #         elif var == "dxy" or var == "ip3d":
                #             xmin = 0
                #             xmax = 0.2
                #         elif var in ["jetRelIso"]:
                #             xmin = 0
                #             xmax = 1
                #         # self.ctrl_Muons[weight][i][var] = ROOT.TH1F("ctrl_Muons[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                #         #                                     "Selected Muon [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                #         # self.addObject(self.ctrl_Muons[weight][i][var])
                #         # self.ctrl_Electrons[weight][i][var] = ROOT.TH1F("ctrl_Electrons[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                #         #                                     "Selected Electron [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                #         # self.addObject(self.ctrl_Electrons[weight][i][var])
                #         self.ctrl_Leptons[weight][i][var] = ROOT.TH1F("ctrl_Leptons[{2:s}][{0:d}][{1:s}]".format(i, var, weight), 
                #                                                       "Selected Lepton [{0:d}]; {1:s}; Events[{2:s}]".format(i, var, weight), 100, xmin, xmax)
                #         self.addObject(self.ctrl_Leptons[weight][i][var])
                    

    # def endJob(self):
    #     if hasattr(self, 'objs') and self.objs != None:
    #         prevdir = ROOT.gDirectory
    #         self.dir.cd()
    #         for obj in self.objs:
    #             obj.Write()
    #         prevdir.cd()
    #         if hasattr(self, 'histFile') and self.histFile != None: 
    #             self.histFile.Close()

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.branchList = inputTree.GetListOfBranches()
        if "Jet_{0:s}".format(self.jetPtVar) not in self.branchList:
            print("Warning: expected branch Jet_{0:s} to be present, but it is not. If not added in a module preceding this one, there will be a crash.".format(self.jetPtVar))
        if "Jet_{0:s}".format(self.jetMVar) not in self.branchList:
            print("Warning: expected branch Jet_{0:s} to be present, but it is not. If not added in a module preceding this one, there will be a crash.".format(self.jetMVar))
        self.out = wrappedOutputTree
        self.varTuple = [('Jet_OSV_baseline', 'i', 'Passes JetMETLeptonLogic at baseline level', 'nJet'),
                         ('Jet_OSV_selection', 'i', 'Passes JetMETLogic at selection level', 'nJet'),
                         ('ESV_JetMETLogic_selection', 'i', 'Passes JetMETLogic at event level,'\
                          ' bits correspond to levels of selection in JetMETLogic', None)
                         ('ESV_JetMETLogic_nJet', 'I', 'Number of jets passing selection requirements', None),
                         ('ESV_JetMETLogic_nJetBTL', 'I', 'Number of jets passing selection requirements and loose b-tagged', None),
                         ('ESV_JetMETLogic_nJetBTM', 'I', 'Number of jets passing selection requirements and medium b-tagged', None),
                         ('ESV_JetMETLogic_nJetBTT', 'I', 'Number of jets passing selection requirements and tight b-tagged', None),
                         ('ESV_JetMETLogic_HT', 'D', 'Scalar sum of selected jets\' Pt', None),
                         ('ESV_JetMETLogic_H', 'D', 'Scalar sum of selected jets\' P', None),
                         ('ESV_JetMETLogic_HT2M', 'D', 'Scalar sum of selected jets\' Pt except 2 highest b-tagged if they are medium or tight', None),
                         ('ESV_JetMETLogic_H2M', 'D', 'Scalar sum of selected jets\' P except 2 highest b-tagged if they are medium or tight', None),
                         ('ESV_JetMETLogic_HTb', 'D', 'Scalar sum of Pt for medium and tight b-tagged jets', None),
                         ('ESV_JetMETLogic_HTH', 'D', 'Hadronic centrality, HT/H', None),
                         ('ESV_JetMETLogic_HTRat', 'D', 'Ratio of Pt for two highest b-tagged jets to HT', None),
                         ('ESV_JetMETLogic_dRbb', 'D', 'DeltaR between the two highest b-tagged jets', None),
                         ('ESV_JetMETLogic_DiLepMass', 'D', 'Invariant mass of same-flavour leptons (0 default)', None),
                       ]
        if self.mode == "Flag":
            if not self.out:
                raise RuntimeError("No Output file selected, cannot flag events for JetMETLogic module")
            else:
                for name, valType, valTitle, lVar in self.varTuple:
                    self.out.branch("{}".format(name), valType, lenVar=lVar, title=valTitle) 
        elif self.mode == "Pass" or self.mode == "Fail" or self.mode == "Plot":
            pass

        if self.isData:
            self.XSweight = self.dataWeightFunc
        elif "genWeight" not in self.branchList:
            self.XSweight = self.backupWeightFunc
            print("Warning in TriggerAndLeptonLogic: expected branch genWeight to be present, but it is not."\
                  "The weight magnitude indicated will be used, but the sign of the genWeight must be assumed positive!")
        else:
            self.XSweight = self.genWeightFunc

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #Increment counter and skip events past the maxEventsToProcess, if larger than -1
        self.counter +=1
        # if -1 < self.maxEventsToProcess < self.counter:
        #     return False        
        # if self.probEvt:
        #     if event.event != self.probEvt:
        #         return False
        
        ###############################################
        ### Collections and Objects and isData check###
        ###############################################        

        #Bits for passing different cuts in the event, make final decision at the end, the loop is going to be slow anyway, thanks to PostProcessor
        ESV_baseline = 0
        ESV_selection = 0

        PV = Object(event, "PV")
        otherPV = Collection(event, "OtherPV")
        SV = Collection(event, "SV")
        
        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        taus = Collection(event, "Tau")
        jets = Collection(event, "Jet")
        # fatjets = Collection(event, "FatJet")
        # subjets = Collection(event, "SubJet")
        weight = self.XSweight(event)
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
        # theWeight = {}

        #Begin weight calculations. Some won't work properly with cutflow, so they'll be running weights
        # ["NONE", "EWo", "EWS", "PUo", "EP"]
        btagSFs = {}
        for jet in jets:
            pass
        # for WLweight in self.weightList:
        #     if WLweight == "NONE":
        #         theWeight[WLweight] = 1
        #     elif WLweight == "EWo":
        #         theWeight[WLweight] = math.copysign(self.evtWeightBase, generator.weight)
        #     elif WLweight == "EWS":
        #         theWeight[WLweight] = math.copysign(self.evtWeightAlt, generator.weight)
        #     elif WLweight == "GWo":
        #         theWeight[weight] = generator.weight
        #     elif weight == "PUo":
        #         theWeight[weight] = event.puWeight #puWeightUp, puWeightDown
        #     elif weight == "EP":
        #         theWeight[weight] = math.copysign(self.evtWeightBase, generator.weight)*event.puWeight
        #     else:
        #         theWeight[weight] = -1
        #     self.cutflow[weight].Fill("> preselection", theWeight[weight])

        ######################
        ### Primary Vertex ###
        ######################
        #Require ndof > minNDoF, |z| < maxAbsZ, and rho < maxRho
        # if PV.ndof <= self.PVCut['minNDoF'] or abs(PV.z) >= self.VPCut['maxAbsZ'] or math.sqrt(PV.x**2 + PV.y**2) >= self.PVCut['maxRho']:
        #     return False
        if PV.ndof > self.PVCut['minNDoF']:
            ESV_baseline += self.passbits['PV_minNDoF']
            ESV_selection += self.passbits['PV_minNDoF']
        if abs(PV.z) < self.PVCut['maxAbsZ']:
            ESV_baseline += self.passbits['PV_maxAbsZ']
            ESV_selection += self.passbits['PV_maxAbsZ']
        if math.sqrt(PV.x**2 + PV.y**2) < self.PVCut['maxRho']:
            ESV_baseline += self.passbits['PV_maxRho']
            ESV_selection += self.passbits['PV_maxRho']


        ###########
        ### MET ###
        ###########
        #Check additional flag(s) solely for Data
        if self.isData:
            passFilters = getattr(Filters, self.Flags["isData"][0])
            if passFilters: 
                ESV_baseline += self.passbits['MET_globalSuperTightHalo2016Filter']
                ESV_selection += self.passbits['MET_globalSuperTightHalo2016Filter']
        else:
            #Default to true for MC
            ESV_baseline += self.passbits['MET_globalSuperTightHalo2016Filter']
            ESV_selection += self.passbits['MET_globalSuperTightHalo2016Filter']

        #Ensure MC and Data pass all recommended filters for 2017 and 2018
        for fi, flag in enumerate(self.Flags["Common"]):
            passFilters = getattr(Filters, flag)
            if passFilters:
                ESV_baseline += self.passbits['MET_{}'.format(flag)]
                ESV_selection += self.passbits['MET_{}'.format(flag)]
        if met.pt >= self.MET[0]: #baseline level
            ESV_baseline += self.passbits['MET_pt_baseline']
        if met.pt >= self.MET[1]: #selection level
            ESV_selection += self.passbits['MET_pt_selection']
        # for weight in self.weightList:
        #     self.cutflow[weight].Fill("> MET > {0:d}".format(self.MET), theWeight[weight])



        if not self.isData:
            pass
            # gens = Collection(event, "GenPart")
            # genjets = Collection(event, "GenJet")
            # genfatjets = Collection(event, "GenJetAK8")
            # gensubjets = Collection(event, "SubGenJetAK8")
            # genmet = Object(event, "GenMET")
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

            #BIG Weights lesson learned: you cannot use Collection, and possibly, you cannot even assign the variable and iterate through it using indices or 
            #pythonic methods. Thus, to ge the 3rd LHEScaleWeight, should use 3rdLHEScaleWeight = getattr(event, "LHEScaleWeight")[2] instead, indexing after acquis.

            #These are redundant and also incorrectly computed as of now (see StitchModule for proper implementation), so no longer used
            #Stitch variables
            # nGL = 0
            # nGJ = 0
            # GenHT = 0
            # for gj, jet in enumerate(genjets):
            #     if jet.pt > 30:
            #         nGJ += 1
            #         if abs(jet.eta) < 2.4: 
            #             GenHT += jet.pt
            # for gp, gen in enumerate(gens):
            #     if abs(gen.pdgId) in set([11, 13]) and gen.status == 1:
            #         nGL += 1
            #     elif abs(gen.pdgId) in set([15]) and gen.status == 2:
            #         nGL += 1
            # #No weights for stitching variables
            # self.stitch_nGenJets.Fill(nGJ)
            # self.stitch_GenHT.Fill(GenHT)
            # self.stitch_nGenLeps.Fill(nGL)
        

        # selEle25 = []
        # selEle20 = []
        # selEle15 = []
        # selEleUniform = []
        # for idx, electron in enumerate(electrons):
        #     d0 = math.sqrt(electron.dxy**2 + electron.dz**2)
        #     if ((abs(electron.eta) < 1.4442 and d0 < 0.05) or (abs(electron.eta) > 1.4660 and abs(electron.eta) < 2.4 and d0 < 0.10)) and electron.cutBased_Fall17_V1 >= 2 and abs(electron.dz) < 0.02:
        #         if electron.pt > self.lepPt:
        #             selEleUniform.append((idx, electron))
        #         if electron.pt > 25:
        #             selMu25.append((idx, electron))
        #         elif electron.pt > 20:
        #             selMu20.append((idx, electron))
        #         elif electron.pt > 15:
        #             selMu15.append((idx, electron))

        # selMu25 = []
        # selMu20 = []
        # selMu15 = []
        # selMuUniform = []
        # for idx, muon in enumerate(muons):
        #     d0 = math.sqrt(muon.dxy**2 + muon.dz**2)
        #     if abs(muon.eta) < 2.4 and muon.pfIsoId >= 4 and abs(muon.dz) < 0.02 and d0 < 0.10:
        #         if muon.pt > self.lepPt:
        #             selMuUniform.append((idx, muon))
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

        #FIXME: Not necessary now
        # nMu = len(selMuUniform)
        # nEle = len(selEleUniform)
        # nLep = nMu + nEle
        # if nLep != 2:
        #     return False
        # for weight in self.weightList:
        #     self.cutflow[weight].Fill("> Dilepton", theWeight[weight])
        
#                         # 'Lepton_ZWindow':0b00000001000000000000,
#                         # 'Jet_nJet25':0b00000010000000000000,
#                         # 'Jet_nJet20':0b00000100000000000000
#                         # 'HT':0b00001000000000000000
#                         # 'Jet_nBJet_2DCSV':0b00010000000000000000
#                         # 'Jet_nBJet_2DJet':0b00100000000000000000

        muon_baseline = []
        muon_selection = []
        for idx, muon in enumerate(muons):
            if muon.OSV_baseline > 0:
                muon_baseline.append((idx, muon))
            if muon.OSV_selection > 0:
                muon_selection.append((idx, muon))

        electron_baseline = []
        electron_selection = []
        for idx, electron in enumerate(electrons):
            if electron.OSV_baseline > 0:
                electron_baseline.append((idx, electron))
            if electron.OSV_selection > 0:
                electron_selection.append((idx, electron))

        leptons_baseline = electron_baseline + muon_baseline
        leptons_selection = electron_selection + muon_selection

        if self.debug:
            if self.passLevel == 'baseline':
                if len(leptons_baseline) > 2:
                    print("Mayday!")
                if leptons_baseline[0][1].charge * leptons_baseline[1][1].charge < 0:
                    print("Charging up!")
            if self.passLevel == 'selection':
                if len(leptons_selection) > 2:
                    print("Mayday!")
                if leptons_selection[0][1].charge * leptons_selection[1][1].charge < 0:
                    print("Charging up!")


        
        
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
        selBTJets = [jetTup for jetTup in selBTsortedJets if getattr(jetTup[1], self.BTAlg) > self.BTWP] #GETOVERHERE
        nJets = len(selJets)
        nBTLoose = len(selBTLooseJets)
        nBTMedium = len(selBTMediumJets)
        nBTTight = len(selBTTightJets)
        nBTSelected = len(selBTJets)

        if nJets < 4:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> 4+ Jets", theWeight[weight])
        if nBTSelected < 2:
            return False
        for weight in self.weightList:
            self.cutflow[weight].Fill("> 2+ Btag Jets ({0} {1})".format(self.BTName, self.BTWP), theWeight[weight])

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
        # for weight in self.weightList:
        #     self.ctrl_met_phi[weight].Fill(met.phi ,theWeight[weight])
        #     self.ctrl_met_pt[weight].Fill(met.pt ,theWeight[weight])
        #     self.ctrl_HT[weight].Fill(HT ,theWeight[weight])
        #     self.ctrl_H[weight].Fill(H ,theWeight[weight])
        #     self.ctrl_HTb[weight].Fill(HTb ,theWeight[weight])
        #     self.ctrl_HT2M[weight].Fill(HT2M ,theWeight[weight])
        #     self.ctrl_H2M[weight].Fill(H2M ,theWeight[weight])
        #     self.ctrl_HTH[weight].Fill(HTH ,theWeight[weight])
        #     self.ctrl_HTRat[weight].Fill(HTRat ,theWeight[weight])
        #     self.ctrl_dRbb[weight].Fill(dRbb ,theWeight[weight])
        #     self.ctrl_DLM[weight].Fill(DiLepMass ,theWeight[weight])
        #     self.ctrl_nJets[weight].Fill(nJets ,theWeight[weight])
        #     self.ctrl_nJets_BTL[weight].Fill(nBTLoose ,theWeight[weight])
        #     self.ctrl_nJets_BTM[weight].Fill(nBTMedium ,theWeight[weight])
        #     self.ctrl_nJets_BTT[weight].Fill(nBTTight ,theWeight[weight])
        #     for var in self.jetPlotVars:
        #         for i, jettup in enumerate(selJets):
        #             try:
        #                 self.ctrl_AJets[weight][i][var].Fill(getattr(jettup[1], var), theWeight[weight])
        #             except:
        #                 pass
        #         for i, jettup in enumerate(selBTsortedJets):
        #             try:
        #                 self.ctrl_BJets[weight][i][var].Fill(getattr(jettup[1], var), theWeight[weight])
        #             except:
        #                 pass
        #     for var in self.jetAK8PlotVars:
        #         for i, jet in enumerate(fatjets):
        #             try:
        #                 self.ctrl_FatJets[weight][i][var].Fill(getattr(jet, var), theWeight[weight])
        #             except:
        #                 pass
        #     for var in self.leptonPlotVars:
        #         for i, leptup in enumerate(selMuUniform + selEleUniform):
        #             try:
        #                 self.ctrl_Leptons[weight][i][var].Fill(getattr(leptup[1], var), theWeight[weight])
        #             except:
        #                 pass
    
    
        ####################################
        ### Variables for branch filling ###
        ####################################
        branchVals = {}
        branchVals['ESV_JetMETLogic_baseline'] = ESV_baseline
        branchVals['ESV_JetMETLogic_selection'] = ESV_selection
        branchVals['ESV_JetMETLogic_nJet'] = nJets
        branchVals['ESV_JetMETLogic_nJetBTL'] = nBTLoose
        branchVals['ESV_JetMETLogic_nJetBTM'] = nBTMedium
        branchVals['ESV_JetMETLogic_nJetBTT'] = nBTTight
        branchVals['ESV_JetMETLogic_HT'] = HT
        branchVals['ESV_JetMETLogic_H'] = H
        branchVals['ESV_JetMETLogic_HT2M'] = HT2M
        branchVals['ESV_JetMETLogic_H2M'] = H2M
        branchVals['ESV_JetMETLogic_HTb'] = HTb
        branchVals['ESV_JetMETLogic_HTH'] = HTH
        branchVals['ESV_JetMETLogic_HTRat'] = HTRat
        branchVals['ESV_JetMETLogic_dRbb'] = dRbb
        branchVals['ESV_JetMETLogic_DiLepMass'] = DiLepMass

        ########################## 
        ### Write out branches ###
        ##########################         
        if self.out and self.mode == "Flag":
            for name, valType, valTitle, lVar in self.varTuple:
                self.out.fillBranch(name, branchVals[name])
        elif self.mode == "PassFail":
            #Do nothing
            pass
        elif self.mode == "Plot":
            #Do something?
            pass
            #Do pass through if plotting, make no assumptions about what should be done with the event
#FIXME            return True
        else:
            raise NotImplementedError("No method in place for JetMETLogic module in mode '{0}'".format(self.mode))


        if branchVals['ESV_TriggerAndLeptonLogic_{}'.format(self.passLevel)]:
            return True
        return False

    def genWeightFunc(self, event):
        #Default value is currently useless, since the tree reader array tool raises an exception anyway
        return math.copysign(self.weightMagnitude, getattr(event, "genWeight", 1))
    def backupWeightFunc(self, event):
        return self.weightMagnitude
    def dataWeightFunc(self, event):
        return 1


TriggerTuple = collections.namedtuple("TriggerTuple", "trigger era subera uniqueEraBit tier channel leadMuThresh subMuThresh leadElThresh subElThresh nontriggerLepThresh")

class TriggerAndLeptonLogic(Module):
    def __init__(self, passLevel, enforceMCCascade=True, era="2013", subera=None, isData=False, TriggerChannel=None, weightMagnitude=1, fillHists=False, debug=False, mode="Flag"):
        """ Trigger logic that checks for fired triggers and searches for appropriate objects based on criteria set by fired triggers.

        passLevel is the level at which the module should trigger "True" to pass the event along to further modules. Available: 'all', 'veto', 'hlt', 'baseline', 'selection'
        Era is a string with the year of data taking or corresponding MC sample ("2017", "2018")
        Subera is a string with the subera of data-taking, only for use in combination with isData=True and TriggerChannel ("B", "E", etc.)
        isData is a boolean for when it's a data sample, as these are handled differently (trigger exclusivity and tier selection) from Monte Carlo.
        TriggerChannel is a string with the trigger channel ("ElMu" for e-mu channel/dataset, regardless of which is higher pT, "El" for single-electron channel/dataset).
        fillHists is a boolean for filling histograms.

        Regarding data, internally there are 'tiers' associated with the trigger tuples. For MC, if the event fires any trigger from any tier, it should be accepted. 
        For data, given that events can be duplicated across data streams ('SingleMuon' and 'MuonEG'), triggers are divided into tiers. 
        The goal is to only select a data event from the highest available tier of triggers that it fires, and veto that event in appropriate 
        data streams when it corresponds to a lower trigger selection.

        For example, let an event fire both a single muon trigger (tier 3) and a mu-mu trigger (tier 1), but not an e-mu trigger (tier 0). In the double muon dataset, 
        the event is selected because it fired the tier 1 trigger in the list (and not the tier 0 triggers). In the single muon dataset, the event is veto'd, 
        because it fired the tier 1 trigger as well as the tier 3. A different event that only fired the tier 3 trigger is appropriately picked up on the single muon 
        dataset, and while it may exist in the double muon dataset, it will only be becasue of a trigger that we have not checked for, and so we must not have picked it up
        in that dataset"""
        self.passLevel = passLevel
        self.enforceMCCascade = enforceMCCascade #This might not be necessary outside of plotting
        self.era = era
        self.subera = subera
        self.isData = isData
        #Options: "MuMu", "ElMu", "ElEl", "Mu"
        self.TriggerChannel = TriggerChannel
        if self.isData and (self.subera == None or self.TriggerChannel == None): 
            raise ValueError("In TriggerAndLeptonLogic is instantiated with isData, both subera and TriggerChannel must be slected ('B', 'F', 'El', 'ElMu', etc.")
        self.weightMagnitude = weightMagnitude
        self.fillHists = fillHists
        self.debug = debug
        self.mode = mode
        if self.mode not in ["Flag", "Pass", "Fail", "Plot"]:
            raise NotImplementedError("Not a supported mode for the TriggerAndLeptonLogic module: '{0}'".format(self.mode))
        if self.fillHists or self.mode == "Plot": 
            self.fillHists = True
            self.writeHistFile = True
        self.TriggerList = [TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2017",
                                         subera="BCDEF",
                                         uniqueEraBit=14,
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=15,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2017",
                                         subera="BCDEF",
                                         uniqueEraBit=13,
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=25,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                                         era="2017",
                                         subera="B",
                                         uniqueEraBit=12,
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
                                         era="2017",
                                         subera="CDEF",
                                         uniqueEraBit=11,
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2017",
                                         subera="BCDEF",
                                         uniqueEraBit=9,
                                         tier=2,
                                         channel="ElEl",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=25,
                                         subElThresh=15,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu27",
                                         era="2017",
                                         subera="BCDEF",
                                         uniqueEraBit=7,
                                         tier=3,
                                         channel="Mu",
                                         leadMuThresh=28,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Ele35_WPTight_Gsf",
                                         era="2017",
                                         subera="BCDEF",
                                         uniqueEraBit=6,
                                         tier=4,
                                         channel="El",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=36,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=14,
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=25,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=12,
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=15,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=11,
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=9,
                                         tier=2,
                                         channel="ElEl",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=25,
                                         subElThresh=15,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu24",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=8,
                                         tier=3,
                                         channel="Mu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Ele32_WPTight_Gsf",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=7,
                                         tier=4,
                                         channel="El",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=33,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15)]
        #Store triggers that are (temporarily) abandoned due to overlap or extra restrictions
        self.lostTrigger = [TriggerTuple(trigger="HLT_IsoMu24_eta2p1",
                                         era="2017",
                                         subera="BCD",
                                         uniqueEraBit=8,
                                         tier=3,
                                         channel="Mu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
                                         era="2017",
                                         subera="CDEF",
                                         uniqueEraBit=10,
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=13,
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=25,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=10,
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),

                        ]



        #Tiers and TriggerChannels should have a 1-to-1 or 1-to-multiple correspondence, dependant upon how data streams are arranged. Logic of multiple streams will need to be sorted for 2018, wheres some singleLepton stream is folded into the double lepton stream
        #2018 implication: given the combination of DoubleElectron and SingleElectron streams into EGamma (along with xPhoton?) data stream, this implies using the 4th backup tier and re-running over the same dataset yet again...
        #This is a waste of resources, but straightforward and keeps the same backup tiers. The alternative is to swap Mu and El backups, and combine the double electron and single electron into the same Tier...
        self.TierToChannelDict = {'2016': {0: [None]},
                                  '2017': {0: ["ElMu"],
                                           1: ["MuMu"],
                                           2: ["ElEl"],
                                           3: ["Mu"],
                                           4: ["El"]},
                                  '2018': {0: ["ElMu"],
                                           1: ["MuMu"],
                                           2: ["ElEl"],
                                           3: ["Mu"],
                                           4: ["El"]}
                                  }
        #The levels for filling histograms and event levels
        self.levelToNameDict = {"T": "HLT Trigger",
                                "B_Lep": "Baseline level with leptons",
                                "B_Jet": "Baseline level with leptons and jets", 
                                "B_HT": "Baseline level with leptons and jets and HT", 
                                "S_Lep": "Selection level with leptons", 
                                "S_Jet": "Selection level with leptons and jets", 
                                "S_HT": "Selection level with leptons and jets and HT"
                                }
        #Era subset of triggers, for use in bin labeling (cycle through axis and fill a bin for each trigger with weight 0.0)
        self.eraTriggers = [trigger for trigger in self.TriggerList if self.era == trigger.era]
        self.Triggers = [trigger for trigger in self.eraTriggers if self.isData == False or (self.subera in trigger.subera and self.TriggerChannel == trigger.channel)]
        #Create list of veto triggers for data, where explicit tiers are expected (calculating the tier first)
        #For 2017, 0 = ElMu dataset, 1 = MuMu, 2 = ElEl, 3 = Mu(Any), 4 = El(Any). Veto any events that fire any higher trigger, to avoid double counting by using this dataset
        #For 2018, 0 = ElMu dataset, Rest to be determined!
        self.tier = [trigger.tier for trigger in self.Triggers]
        self.tier.sort(key=lambda i: i, reverse=False)
        if self.debug: 
            print("Sorted trigger tiers selected are: " + str(self.tier))
        self.tier = self.tier[0]
        self.vetoTriggers = [trigger for trigger in self.eraTriggers if self.isData and self.subera in trigger.subera and trigger.tier < self.tier]
        if self.debug: 
            print("Trigger tier selected is: " + str(self.tier))
            print("Selected {} Triggers for usage".format(len(self.Triggers)))
            for t in self.Triggers:
                print(t)
            print("Selected {} Triggers for veto".format(len(self.vetoTriggers)))
            for t in self.vetoTriggers:
                print(t)

        #Bins for the fired HLT paths; max set to 0 for nice labeling without empty bin
        self.PathsBins = 1
        self.PathsMin = 0
        self.PathsMax = 0
        self.BitsBins = 32
        self.BitsMin = 0
        self.BitsMax = 32

    def beginJob(self, histFile=None,histDirName=None):
        if self.fillHists == False:
            Module.beginJob(self, None, None)
        else:
            if histFile == None or histDirName == None:
                raise RuntimeError("fillHists set to True, but no histFile or histDirName specified")
            Module.beginJob(self,histFile,histDirName)
            self.trigLogic_Paths = {}
            self.trigLogic_Freq = {}
            self.trigLogic_Correl = {}
            self.trigLogic_Bits = {}
            for lvl in ["TRIG", "BASE", "SLCT"]:
                self.trigLogic_Paths[lvl] = ROOT.TH1D("trigLogic_Paths_{}".format(lvl), 
                                                      "HLT Paths passed by events  at {} level (weightMagnitude={}); Paths; Events".format(lvl, self.weightMagnitude), 
                                                      self.PathsBins, self.PathsMin, self.PathsMax)
                self.trigLogic_Freq[lvl] = ROOT.TH1D("trigLogic_Freq_{}".format(lvl), 
                                                     "HLT Paths Fired and Vetoed at {} level  (weightMagnitude={}); Type; Events".format(lvl, self.weightMagnitude), 
                                                     1, 0, 0)
                self.trigLogic_Correl[lvl] = ROOT.TH2D("trigLogic_Correl_{}".format(lvl), 
                                                         "Fired HLT Path Correlations at {} level (weightMagnitude={}); Path; Path ".format(lvl, self.weightMagnitude),
                                                         self.PathsBins, self.PathsMin, self.PathsMax, self.PathsBins, self.PathsMin, self.PathsMax)
                self.trigLogic_Bits[lvl] = ROOT.TH2D("trigLogic_Bits_{}".format(lvl), 
                                                         "Fired HLT Path Bits at {} level (weightMagnitude={}); Path; Bits ".format(lvl, self.weightMagnitude),
                                                         self.PathsBins, self.PathsMin, self.PathsMax, self.BitsBins, self.BitsMin, self.BitsMax)
            for lvl in ["TRIG", "BASE", "SLCT"]:
                self.addObject(self.trigLogic_Paths[lvl])
                self.addObject(self.trigLogic_Freq[lvl])
                self.addObject(self.trigLogic_Correl[lvl])
                self.addObject(self.trigLogic_Bits[lvl])

            #Initialize labels to keep consistent across all files
            for lvl in ["TRIG", "BASE", "SLCT"]:
                for trig in self.eraTriggers:
                    self.trigLogic_Paths[lvl].Fill(trig.trigger + " (T{})".format(trig.tier), 0.0)
                    self.trigLogic_Correl[lvl].Fill(trig.trigger + " (T{})".format(trig.tier), trig.trigger + " (T{})".format(trig.tier), 0.0)
                    self.trigLogic_Bits[lvl].Fill(trig.trigger + " (T{})".format(trig.tier), 0, 0.0)
                for cat in ["Vetoed", "Fired", "Neither"]:
                    self.trigLogic_Freq[lvl].Fill(cat, 0.0)

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.branchList = inputTree.GetListOfBranches()
        if self.isData:
            self.XSweight = self.dataWeightFunc
        elif "genWeight" not in self.branchList:
            self.XSweight = self.backupWeightFunc
            print("Warning in TriggerAndLeptonLogic: expected branch genWeight to be present, but it is not."\
                  "The weight magnitude indicated will be used, but the sign of the genWeight must be assumed positive!")
        else:
            self.XSweight = self.genWeightFunc
        self.varTuple = [('Muon_OSV_baseline', 'i', 'Passes TriggerAndLeptonLogic at baseline level', 'nMuon'),
                         ('Muon_OSV_selection', 'i', 'Passes TriggerAndLeptonLogic at selection level', 'nMuon'),
                         ('Electron_OSV_baseline', 'i', 'Passes TriggerAndLeptonLogic at baseline level', 'nElectron'),
                         ('Electron_OSV_selection', 'i', 'Passes TriggerAndLeptonLogic at selection level', 'nElectron'),
                         ('ESV_TriggerAndLeptonLogic_baseline', 'i', 'Passes TriggerAndLeptonLogic at event level,'\
                         ' bits correspond to uniqueEraBit in TriggerAndLeptonLogic', None),
                         ('ESV_TriggerAndLeptonLogic_selection', 'i', 'Passes TriggerAndLeptonLogic at event level,'\
                         ' bits correspond to uniqueEraBit in TriggerAndLeptonLogic', None)
                       ]        #OSV = Object Selection Variable
        for trigger in self.eraTriggers:
            #unsigned 32 bit integers for the trigger bit storage, because 16 is not in the root branch to python branch 
            #dictionary of the postprocessor framework's output module
            self.varTuple.append(('ESV_TriggerEraBits_b{}'.format(trigger.uniqueEraBit), 'i', 
                                 'Bits (Baseline) for Trigger={}'\
                                 'with uniqueEraBit={}'.format(trigger.trigger, trigger.uniqueEraBit), None))
            self.varTuple.append(('ESV_TriggerEraBits_s{}'.format(trigger.uniqueEraBit), 'i', 
                                 'Bits (Selection) for Trigger={}'\
                                 'with uniqueEraBit={}'.format(trigger.trigger, trigger.uniqueEraBit), None))
        if self.mode == "Flag":
            if not self.out:
                raise RuntimeError("No Output file selected, cannot flag events for TriggerAndLeptonLogic module")
            else:
                for name, valType, valTitle, lVar in self.varTuple:
                    self.out.branch("{}".format(name), valType, lenVar=lVar, title=valTitle) 
        elif self.mode == "Pass" or self.mode == "Fail" or self.mode == "Plot":
            pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
        #run = getattr(event, "run")
        #evt = getattr(event, "event")
        #lumi = getattr(event, "luminosityBlock")
        # try:
        #     weight = math.copysign(self.weightMagnitude, getattr(event, "genWeight", 1))
        # except RuntimeError, e:
        #     weight = 1
        weight = self.XSweight(event)
        #getattr with default value doesn't work, have to protect anyway...
        Fired = [trigger for trigger in self.Triggers if hasattr(event, trigger.trigger) and getattr(event, trigger.trigger, False)]
        Vetoed = [trigger for trigger in self.vetoTriggers if hasattr(event, trigger.trigger) and getattr(event, trigger.trigger, False)]
        muons = Collection(event, "Muon")
        electrons = Collection(event, "Electron")

        #Prepare dictionary with trigger names as keys
        leadMu_baseline = {}
        leadEl_baseline = {}
        subMu_baseline = {}
        subEl_baseline = {}
        nontriggerEl_baseline = {}
        nontriggerMu_baseline = {}
        leadMu_selection = {}
        leadEl_selection = {}
        subMu_selection = {}
        subEl_selection = {}
        nontriggerEl_selection = {}
        nontriggerMu_selection = {}
        pass_trigger = {}
        pass_trigger_veto = {}
        pass_baseline_lep = {}
        pass_selection_lep = {}

        #Prepare lepton selection bits
        muon_osv_baseline = [0]*len(muons)
        muon_osv_selection = [0]*len(muons)
        electron_osv_baseline = [0]*len(electrons)
        electron_osv_selection = [0]*len(electrons)

        #Create baseline and selection level lists for each trigger, permitting an event to pass at event and selection levels with different triggers
        for trigger in Fired:
            leadMu_baseline[trigger.trigger] = []
            leadEl_baseline[trigger.trigger] = []
            subMu_baseline[trigger.trigger] = []
            subEl_baseline[trigger.trigger] = []
            nontriggerMu_baseline[trigger.trigger] = []
            nontriggerEl_baseline[trigger.trigger] = []
            leadMu_selection[trigger.trigger] = []
            leadEl_selection[trigger.trigger] = []
            subMu_selection[trigger.trigger] = []
            subEl_selection[trigger.trigger] = []
            nontriggerMu_selection[trigger.trigger] = []
            nontriggerEl_selection[trigger.trigger] = []
            
            #pass variables
            pass_trigger[trigger.trigger] = True #If it's in fired, it fired
            if len(Vetoed) < 1:
                pass_trigger_veto[trigger.trigger] = True #both fired and not vetoed in the event
            else:
                pass_trigger_veto[trigger.trigger] = False #fired but vetoed
            #Store bitsets here for details of the baseline and selection cuts
            pass_baseline_lep[trigger.trigger] = 0 #convert to bit counter, 0 fail, 1 2+ leps, 2 less than 3 leps, 4 opp charge, 8 ID requirements, 16 inv mass
            # pass_baseline_jet[trigger.trigger] = 0
            # pass_baseline_ht[trigger.trigger] = 0
            pass_selection_lep[trigger.trigger] = 0
            # pass_selection_jet[trigger.trigger] = 0
            # pass_selection_ht[trigger.trigger] = 0

        #FIXME: Add dz cut, add iso cut or trg object cut, add to triggers as well
        for idx, mu in enumerate(muons):
            if len(Vetoed) > 0 or len(Fired) < 1:
                continue
            d0 = math.sqrt(mu.dxy**2 + mu.dz**2)
            pass_eta = (abs(mu.eta) < 2.4) #max regardless
            #Baseline bools
            pass_iso_baseline = (mu.pfIsoId >= 3) #trigger iso VVL, so selection = tight (4) far exceeds this...
            pass_dz_baseline = (abs(mu.dz) < 0.06) #trigger dz = 0.2, selection = 0.02, baseline = 0.06
            pass_d0_baseline = (d0 < 0.15) #selection = 0.10, baseline = 0.15
            #Selection bools
            pass_iso_selection = (mu.pfIsoId >= 4) #trigger iso VVL, so selection = tight (4) far exceeds this...
            pass_dz_selection = (abs(mu.dz) < 0.02) #trigger dz = 0.2, selection = 0.02, baseline = 0.06
            pass_d0_selection = (d0 < 0.10) #selection = 0.10, baseline = 0.15
            pass_common_baseline = pass_eta and pass_iso_baseline and pass_dz_baseline and pass_d0_baseline
            pass_common_selection = pass_eta and pass_iso_selection and pass_dz_selection and pass_d0_selection
            for trigger in Fired:
                if pass_common_baseline:
                    #Create OVERLAPPING baseline collections
                    if mu.pt > trigger.leadMuThresh:
                        leadMu_baseline[trigger.trigger].append((idx, mu))
                    if mu.pt > trigger.subMuThresh:
                        subMu_baseline[trigger.trigger].append((idx, mu))
                    if mu.pt > trigger.nontriggerLepThresh:
                        nontriggerMu_baseline[trigger.trigger].append((idx, mu))
                if pass_common_selection:
                    #Create OVERLAPPING selection collections
                    if mu.pt > trigger.leadMuThresh:
                        leadMu_selection[trigger.trigger].append((idx, mu))
                    if mu.pt > trigger.subMuThresh:
                        subMu_selection[trigger.trigger].append((idx, mu))
                    if mu.pt > trigger.nontriggerLepThresh:
                        nontriggerMu_selection[trigger.trigger].append((idx, mu))
    
        for idx, el in enumerate(electrons):
            if len(Vetoed) > 0 or len(Fired) < 1: 
                continue
            d0 = math.sqrt(el.dxy**2 + el.dz**2)
            pass_eta_barrel = (abs(el.eta) < 1.4442) #crack edge
            pass_eta_endcap = (abs(el.eta) > 1.4660 and abs(el.eta) < 2.5) #crack edge and calorimeters
            if pass_eta_barrel: 
                pass_d0_baseline = (d0 < 0.10) #selection < 0.05, baseline < 0.10
                pass_d0_selection = (d0 < 0.05) #selection < 0.05, baseline < 0.10
                pass_eta = True
            elif pass_eta_endcap: 
                pass_d0_baseline = (d0 < 0.15) #selection < 0.10, baseline < 0.15
                pass_d0_selection = (d0 < 0.10) #selection < 0.10, baseline < 0.15
                pass_eta = True
            else: 
                pass_d0_baseline = False #doesn't matter without eta pass
                pass_d0_selection = False #doesn't matter without eta pass
                pass_eta = False
            pass_dz_baseline = (el.dz < 0.06) #selection < 0.02, baseline < 0.06, trigger < 0.2 presumably (verification needed)
            pass_dz_selection = (el.dz < 0.02) #selection < 0.02, baseline < 0.06, trigger < 0.2 presumably (verification needed)
            pass_id_loose = (el.cutBased >= 2)
            pass_id_medium = (el.cutBased >= 3)
            pass_common_baseline = pass_eta and pass_dz_baseline and pass_d0_baseline and pass_id_loose
            pass_common_selection = pass_eta and pass_dz_selection and pass_d0_selection and pass_id_loose
            for trigger in Fired:
                if pass_common_baseline:
                    #Create OVERLAPPING baseline collections
                    if el.pt > trigger.leadElThresh:
                        leadEl_baseline[trigger.trigger].append((idx, el))
                    if el.pt > trigger.subElThresh:
                        subEl_baseline[trigger.trigger].append((idx, el))
                    if el.pt > trigger.nontriggerLepThresh:
                        nontriggerEl_baseline[trigger.trigger].append((idx, el))
                if pass_common_selection:
                    #Create OVERLAPPING selection collections
                    if el.pt > trigger.leadElThresh:
                        leadEl_selection[trigger.trigger].append((idx, el))
                    if el.pt > trigger.subElThresh:
                        subEl_selection[trigger.trigger].append((idx, el))
                    if el.pt > trigger.nontriggerLepThresh:
                        nontriggerEl_selection[trigger.trigger].append((idx, el))

        #Do Lepton selection logic here
        pass_baseline_bitset = 0
        pass_selection_bitset = 0
        for trigger in Fired:            
            #FIXME: Need the mass, charge, 3-lepton vetos in place. Add a bitset for EVERY trigger, then work on single event-level bitset
            if trigger.channel == "ElMu":
                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                #Failure: This only selects leading electron trigger variants...
                #exactly one of the lead collections will have a non-empty set of sub-99.999TeV leptons, thus we combine the orthogonal e and mu lists
                leadLep_baseline = leadEl_baseline[trigger.trigger] + leadMu_baseline[trigger.trigger]
                subLep_baseline = subEl_baseline[trigger.trigger] + subMu_baseline[trigger.trigger]
                if len(leadLep_baseline) > 0 and len(subLep_baseline) > 0:
                    #2+ leptons of the right triggering types
                    pass_baseline_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_baseline_lep[trigger.trigger] += 2**1
                        # if leadEl_baseline[trigger.trigger][0][1].charge * subMu_baseline[trigger.trigger][0][1].charge < 0:
                        #Because we choose a lead and subleading lepton from separate collections, they must necessarily be non-overlapping collections.
                        #We choose the first from each tuple, where the second item is the lepton, and then get its charge
                        if leadLep_baseline[0][1].charge * subLep_baseline[0][1].charge < 0:
                            #Opposite sign leptons
                            pass_baseline_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivialsolution right now, but couple with OS charge requirement
                            pass_baseline_lep[trigger.trigger] += 2**3
                            #Null invariant mass cut for e-mu channel - the trivial bit - but pair it with ID requirements here
                            pass_baseline_lep[trigger.trigger] += 2**4
                if pass_baseline_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_baseline_bitset += 2**trigger.uniqueEraBit
                    #access the index of the selected leptons, and add the trigger ID to its bitset, indicated it passed on this trigger path
                    #Need to know the pdgId of each one to access the right index and set bit high
                    #Technically, we know that if one is an electron, the other must be a muon, so we only need one if-else block
                    if leadLep_baseline[0][1].pdgId in [-11, 11]: #electron-muon
                        electron_osv_baseline[leadLep_baseline[0][0]] += 2**trigger.uniqueEraBit
                        muon_osv_baseline[subLep_baseline[0][0]] += 2**trigger.uniqueEraBit
                    elif leadLep_baseline[0][1].pdgId in [-13, 13]: #muon-electron
                        muon_osv_baseline[leadLep_baseline[0][0]] += 2**trigger.uniqueEraBit
                        electron_osv_baseline[subLep_baseline[0][0]] += 2**trigger.uniqueEraBit
                    else:
                        raise RuntimeError("Logical Error!")
                    # if subLep_baseline[0][1].pdgId in [-11, 11]: #electron
                    #     electron_osv_baseline[subLep_baseline[0][0]] += 2**trigger.uniqueEraBit
                    # else: #muon
                    #     muon_osv_baseline[subLep_baseline[0][0]] += 2**trigger.uniqueEraBit

                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                leadLep_selection = leadEl_selection[trigger.trigger] + leadMu_selection[trigger.trigger]
                subLep_selection = subEl_selection[trigger.trigger] + subMu_selection[trigger.trigger]
                if len(leadLep_selection) > 0 and len(subLep_selection) > 0:
                    #2+ leptons of the right triggering types
                    pass_selection_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_selection_lep[trigger.trigger] += 2**1                
                        # if leadEl_selection[trigger.trigger][0][1].charge * subMu_selection[trigger.trigger][0][1].charge < 0:
                        #Because we choose a lead and subleading lepton from separate collections, they must necessarily be non-overlapping collections.
                        #We choose the first from each tuple, where the second item is the lepton, and then get its charge
                        if leadLep_selection[0][1].charge * subLep_selection[0][1].charge < 0:
                            #Opposite sign leptons
                            pass_selection_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivialsolution right now, but couple with OS charge requirement
                            pass_selection_lep[trigger.trigger] += 2**3
                            #Null invariant mass cut for e-mu channel - the trivial bit - but pair it with ID requirements here
                            pass_selection_lep[trigger.trigger] += 2**4
                if pass_selection_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_selection_bitset += 2**trigger.uniqueEraBit
                    #access the index of the selected leptons, and add the trigger ID to its bitset, indicated it passed on this trigger path
                    #Need to know the pdgId of each one to access the right index and set bit high
                    #Technically, we know that if one is an electron, the other must be a muon, so we only need one if-else block
                    if leadLep_selection[0][1].pdgId in [-11, 11]: #electron-muon
                        electron_osv_selection[leadLep_selection[0][0]] += 2**trigger.uniqueEraBit
                        muon_osv_selection[subLep_selection[0][0]] += 2**trigger.uniqueEraBit
                    elif leadLep_selection[0][1].pdgId in [-13, 13]: #muon-electron
                        muon_osv_selection[leadLep_selection[0][0]] += 2**trigger.uniqueEraBit
                        electron_osv_selection[subLep_selection[0][0]] += 2**trigger.uniqueEraBit
                    else:
                        raise RuntimeError("Logical Error!")

            elif trigger.channel == "MuMu":
                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadMu_baseline[trigger.trigger]) > 0 and len(subMu_baseline[trigger.trigger]) > 1:
                    #2+ leptons of the right triggering types
                    pass_baseline_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_baseline_lep[trigger.trigger] += 2**1
                        #Exploit fact that subMu is superset of leadMu in this case, and we have only 2 leptons passing cuts so far, so take the 1st and 2nd...
                        if subMu_baseline[trigger.trigger][0][1].charge * subMu_baseline[trigger.trigger][1][1].charge < 0:
                            #Opposite sign leptons
                            pass_baseline_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivialsolution right now, but couple with OS charge requirement
                            pass_baseline_lep[trigger.trigger] += 2**3
                            if (subMu_baseline[trigger.trigger][0][1].p4() + subMu_baseline[trigger.trigger][1][1].p4()).M() > 8.0:
                                #Require invariant mass over 8GeV to simplify trigger tuples, Code could be simplified/unified, but eh...
                                pass_baseline_lep[trigger.trigger] += 2**4
                if pass_baseline_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_baseline_bitset += 2**trigger.uniqueEraBit
                    #access the index of the selected leptons, and add the trigger ID to its bitset, indicated it passed on this trigger path
                    muon_osv_baseline[subMu_baseline[trigger.trigger][0][0]] += 2**trigger.uniqueEraBit
                    muon_osv_baseline[subMu_baseline[trigger.trigger][1][0]] += 2**trigger.uniqueEraBit

#FIXME: Simplify access to the collections so that trigger.trigger no longer needs to be referenced for the charge or accessing the indices, like ElMu or El channels

                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadMu_selection[trigger.trigger]) > 0 and len(subMu_selection[trigger.trigger]) > 1:
                    #2+ leptons of the right triggering types
                    pass_selection_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_selection_lep[trigger.trigger] += 2**1                
                        if subMu_selection[trigger.trigger][0][1].charge * subMu_selection[trigger.trigger][1][1].charge < 0:
                            #Opposite sign leptons
                            pass_selection_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivialsolution right now, but couple with OS charge requirement
                            pass_selection_lep[trigger.trigger] += 2**3
                            if (subMu_selection[trigger.trigger][0][1].p4() + subMu_selection[trigger.trigger][1][1].p4()).M() > 8.0:
                                #Require invariant mass over 8GeV to simplify trigger tuples, Code could be simplified/unified, but eh...
                                pass_selection_lep[trigger.trigger] += 2**4
                if pass_selection_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_selection_bitset += 2**trigger.uniqueEraBit
                    #access the index of the selected leptons, and add the trigger ID to its bitset, indicated it passed on this trigger path
                    muon_osv_selection[subMu_selection[trigger.trigger][0][0]] += 2**trigger.uniqueEraBit
                    muon_osv_selection[subMu_selection[trigger.trigger][1][0]] += 2**trigger.uniqueEraBit

            elif trigger.channel == "ElEl":
                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                #Since the same flavor, the subEl must be a superset of the leadEl, and we thus check the first is len>=2, the second len>=1
                if len(leadEl_baseline[trigger.trigger]) > 0 and len(subEl_baseline[trigger.trigger]) > 1:
                    #2+ leptons of the right triggering types
                    pass_baseline_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_baseline_lep[trigger.trigger] += 2**1
                        if subEl_baseline[trigger.trigger][0][1].charge * subEl_baseline[trigger.trigger][1][1].charge < 0:
                            #Opposite sign leptons
                            pass_baseline_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivialsolution right now at BASELINE ONLY, but couple with OS charge requirement
                            pass_baseline_lep[trigger.trigger] += 2**3
                            #Trivial solution, no invariant mass cut for e-e channel
                            pass_baseline_lep[trigger.trigger] += 2**4
                if pass_baseline_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_baseline_bitset += 2**trigger.uniqueEraBit
                    #access the index of the selected leptons, and add the trigger ID to its bitset, indicated it passed on this trigger path
                    electron_osv_baseline[subEl_baseline[trigger.trigger][0][0]] += 2**trigger.uniqueEraBit
                    electron_osv_baseline[subEl_baseline[trigger.trigger][1][0]] += 2**trigger.uniqueEraBit

                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadEl_selection[trigger.trigger]) > 0 and len(subEl_selection[trigger.trigger]) > 1:
                    #2+ leptons of the right triggering types
                    pass_selection_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_selection_lep[trigger.trigger] += 2**1                
                        if subEl_selection[trigger.trigger][0][1].charge * subEl_selection[trigger.trigger][1][1].charge < 0:
                            #Opposite sign leptons
                            pass_selection_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            if leadEl_selection[trigger.trigger][0][1].cutBased >= 3 or subEl_selection[trigger.trigger][0][1].cutBased >= 3:
                                #Require that one is medium ID!
                                pass_selection_lep[trigger.trigger] += 2**3
                                #Trivial solution, no invariant mass cut for e-e channel
                                pass_selection_lep[trigger.trigger] += 2**4
                if pass_selection_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_selection_bitset += 2**trigger.uniqueEraBit
                    #access the index of the selected leptons, and add the trigger ID to its bitset, indicated it passed on this trigger path
                    electron_osv_selection[subEl_selection[trigger.trigger][0][0]] += 2**trigger.uniqueEraBit
                    electron_osv_selection[subEl_selection[trigger.trigger][1][0]] += 2**trigger.uniqueEraBit


            elif trigger.channel == "Mu":
                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadMu_baseline[trigger.trigger]) > 0 and (len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger])) > 1:
                    #2+ leptons, 1 triggering muon, and at least 2 electrons/muons passing the common selection requirements
                    pass_baseline_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger]) < 3:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_baseline_lep[trigger.trigger] += 2**1              
                        #Now unknown which collection contains the 2nd lepton, so go to the non-triggering collections
                        leptons_baseline = nontriggerMu_baseline[trigger.trigger] + nontriggerEl_baseline[trigger.trigger]
                        if leptons_baseline[0][1].charge * leptons_baseline[1][1].charge < 0:
                            #Opposite sign leptons
                            pass_baseline_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivial solution right now, since there's a mouon, but couple with OS charge requirement
                            pass_baseline_lep[trigger.trigger] += 2**3
                            #Null invariant mass cut for single mu channel - the trivial bit - but pair it with ID requirements here
                            pass_baseline_lep[trigger.trigger] += 2**4
                if pass_baseline_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_baseline_bitset += 2**trigger.uniqueEraBit
                    #access the index of the selected leptons, and add the trigger ID to its bitset, indicated it passed on this trigger path
                    #Obviously, now that we no longer know for certain what the 2nd lepton is, we must check
                    if leptons_baseline[0][1].pdgId in [-11, 11]: #electron
                        electron_osv_baseline[leptons_baseline[0][0]] += 2**trigger.uniqueEraBit
                    elif leptons_baseline[0][1].pdgId in [-13, 13]: #muon
                        muon_osv_baseline[leptons_baseline[0][0]] += 2**trigger.uniqueEraBit
                    else:
                        raise RuntimeError("Logical Error!")
                    if leptons_baseline[1][1].pdgId in [-11, 11]: #electron
                        electron_osv_baseline[leptons_baseline[1][0]] += 2**trigger.uniqueEraBit
                    elif leptons_baseline[1][1].pdgId in [-13, 13]: #muon
                        muon_osv_baseline[leptons_baseline[1][0]] += 2**trigger.uniqueEraBit
                    else:
                        raise RuntimeError("Logical Error!")


                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadMu_selection[trigger.trigger]) > 0 and (len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger])) > 1:
                    #2+ leptons, 1 triggering muon, and at least 2 electrons/muons passing the common selection requirements
                    pass_selection_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger]) < 3:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_selection_lep[trigger.trigger] += 2**1              
                        #Now unknown which collection contains the 2nd lepton, so go to the non-triggering collections
                        leptons_selection = nontriggerMu_selection[trigger.trigger] + nontriggerEl_selection[trigger.trigger]
                        if leptons_selection[0][1].charge * leptons_selection[1][1].charge < 0:
                            #Opposite sign leptons
                            pass_selection_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivial solution right now, since there's a mouon, but couple with OS charge requirement
                            pass_selection_lep[trigger.trigger] += 2**3
                            #Null invariant mass cut for single mu channel - the trivial bit - but pair it with ID requirements here
                            pass_selection_lep[trigger.trigger] += 2**4
                if pass_selection_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_selection_bitset += 2**trigger.uniqueEraBit
                    #access the index of the selected leptons, and add the trigger ID to its bitset, indicated it passed on this trigger path
                    #Obviously, now that we no longer know for certain what the 2nd lepton is, we must check
                    if leptons_selection[0][1].pdgId in [-11, 11]: #electron
                        electron_osv_selection[leptons_selection[0][0]] += 2**trigger.uniqueEraBit
                    elif leptons_selection[0][1].pdgId in [-13, 13]: #muon
                        muon_osv_selection[leptons_selection[0][0]] += 2**trigger.uniqueEraBit
                    else:
                        raise RuntimeError("Logical Error!")
                    if leptons_selection[1][1].pdgId in [-11, 11]: #electron
                        electron_osv_selection[leptons_selection[1][0]] += 2**trigger.uniqueEraBit
                    elif leptons_selection[1][1].pdgId in [-13, 13]: #muon
                        muon_osv_selection[leptons_selection[1][0]] += 2**trigger.uniqueEraBit
                    else:
                        raise RuntimeError("Logical Error!")

                #Maybe FIXME: Don't forget eta or tkIso cuts different from double lepton values! Difference between 2017 and 2018 values
            elif trigger.channel == "El":
                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadEl_baseline[trigger.trigger]) > 0 and (len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger])) > 1:
                    #2+ leptons, 1 triggering electron, and at least 2 electrons/muons passing the common selection requirements
                    pass_baseline_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger]) < 3:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_baseline_lep[trigger.trigger] += 2**1              
                        #Now unknown which collection contains the 2nd lepton, so go to the non-triggering collections
                        #FIXME: have to check for any kind of combination of leptons...
                        leptons_baseline = nontriggerMu_baseline[trigger.trigger] + nontriggerEl_baseline[trigger.trigger]
                        if leptons_baseline[0][1].charge * leptons_baseline[1][1].charge < 0:
                            #Opposite sign leptons
                            pass_baseline_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            if leadEl_baseline[trigger.trigger][0][1].cutBased >= 4:
                                #WPTight on these... effectively the medium cut in case of e-e channel
                                pass_baseline_lep[trigger.trigger] += 2**3
                                #Null invariant mass cut for single e channel - the trivial bit - but pair it with ID requirements here
                                pass_baseline_lep[trigger.trigger] += 2**4
                if pass_baseline_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_baseline_bitset += 2**trigger.uniqueEraBit
                    #access the index of the selected leptons, and add the trigger ID to its bitset, indicated it passed on this trigger path
                    #Obviously, now that we no longer know for certain what the 2nd lepton is, we must check
                    if leptons_baseline[0][1].pdgId in [-11, 11]: #electron
                        electron_osv_baseline[leptons_baseline[0][0]] += 2**trigger.uniqueEraBit
                    elif leptons_baseline[0][1].pdgId in [-13, 13]: #muon
                        muon_osv_baseline[leptons_baseline[0][0]] += 2**trigger.uniqueEraBit
                    else:
                        raise RuntimeError("Logical Error!")
                    if leptons_baseline[1][1].pdgId in [-11, 11]: #electron
                        electron_osv_baseline[leptons_baseline[1][0]] += 2**trigger.uniqueEraBit
                    elif leptons_baseline[1][1].pdgId in [-13, 13]: #muon
                        muon_osv_baseline[leptons_baseline[1][0]] += 2**trigger.uniqueEraBit
                    else:
                        raise RuntimeError("Logical Error!")

                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadEl_selection[trigger.trigger]) > 0 and (len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger])) > 1:
                    #2+ leptons, 1 triggering electron, and at least 2 electrons/muons passing the common selection requirements
                    pass_selection_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger]) < 3:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_selection_lep[trigger.trigger] += 2**1              
                        #Now unknown which collection contains the 2nd lepton, so go to the non-triggering collections
                        #FIXME: have to check for any kind of combination of leptons...
                        leptons_selection = nontriggerMu_selection[trigger.trigger] + nontriggerEl_selection[trigger.trigger]
                        if leptons_selection[0][1].charge * leptons_selection[1][1].charge < 0:
                            #Opposite sign leptons
                            pass_selection_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            if leadEl_selection[trigger.trigger][0][1].cutBased >= 4:
                                #WPTight on these... effectively the medium cut in case of e-e channel
                                pass_selection_lep[trigger.trigger] += 2**3
                                #Null invariant mass cut for single e channel - the trivial bit - but pair it with ID requirements here
                                pass_selection_lep[trigger.trigger] += 2**4
                if pass_selection_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_selection_bitset += 2**trigger.uniqueEraBit
                    #access the index of the selected leptons, and add the trigger ID to its bitset, indicated it passed on this trigger path
                    #Obviously, now that we no longer know for certain what the 2nd lepton is, we must check
                    if leptons_selection[0][1].pdgId in [-11, 11]: #electron
                        electron_osv_selection[leptons_selection[0][0]] += 2**trigger.uniqueEraBit
                    elif leptons_selection[0][1].pdgId in [-13, 13]: #muon
                        muon_osv_selection[leptons_selection[0][0]] += 2**trigger.uniqueEraBit
                    else:
                        raise RuntimeError("Logical Error!")
                    if leptons_selection[1][1].pdgId in [-11, 11]: #electron
                        electron_osv_selection[leptons_selection[1][0]] += 2**trigger.uniqueEraBit
                    elif leptons_selection[1][1].pdgId in [-13, 13]: #muon
                        muon_osv_selection[leptons_selection[1][0]] += 2**trigger.uniqueEraBit
                    else:
                        raise RuntimeError("Logical Error!")
                #maybe L1 Seed additional requirement in 2017 needed?
            elif self.doUnbiasedTrigger:
                pass
            else:
                RuntimeError("Unhandled Trigger.channel class")

#            for lvl in ["T", "B_Lep", "B_Jet", "B_HT", "S_Lep", "S_Jet", "S_HT"]:
        if self.fillHists:
            #FIXME: this obviously needs reworking, now... need a dict?
            tierFired = [t.tier for t in Fired]
            tierFired.sort(key=lambda i: i, reverse=False)
            if len(tierFired) > 0:
                highestTierFired = tierFired[0]
            else:
                highestTierFired = None

            if len(Vetoed) > 0: 
                self.trigLogic_Freq["TRIG"].Fill("Vetoed", weight)
            elif len(Fired) > 0:
                self.trigLogic_Freq["TRIG"].Fill("Fired", weight)
                if pass_baseline_bitset > 0:
                    self.trigLogic_Freq["BASE"].Fill("Fired", weight)
                if pass_selection_bitset > 0:
                    self.trigLogic_Freq["SLCT"].Fill("Fired", weight)
            else:
                self.trigLogic_Freq["TRIG"].Fill("Neither", weight)
            for tn, trig in enumerate(Fired):
                #Skip (primary) trigger filling if not in the tier that fired first (Han!)
                if self.enforceMCCascade == True and highestTierFired != trig.tier:
                    continue
                self.trigLogic_Paths["TRIG"].Fill(trig.trigger + " (T{})".format(trig.tier), weight)
                if pass_baseline_lep[trig.trigger]:
                    self.trigLogic_Paths["BASE"].Fill(trig.trigger + " (T{})".format(trig.tier), weight)
                if pass_selection_lep[trig.trigger]:
                    self.trigLogic_Paths["SLCT"].Fill(trig.trigger + " (T{})".format(trig.tier), weight)
                self.trigLogic_Bits["BASE"].Fill(trig.trigger + " (T{})".format(trig.tier), pass_baseline_lep[trig.trigger], weight)
                self.trigLogic_Bits["SLCT"].Fill(trig.trigger + " (T{})".format(trig.tier), pass_selection_lep[trig.trigger], weight)
                for tm, trig2 in enumerate(Fired):
                    # if tm >= tn: #Do self correllation to set the scale properly
                    #Just do full correlation matrix
                    self.trigLogic_Correl["TRIG"].Fill(trig.trigger + " (T{})".format(trig.tier), trig2.trigger + " (T{})".format(trig2.tier), weight)
                    if pass_baseline_lep[trig.trigger] and pass_baseline_lep[trig2.trigger]:
                        self.trigLogic_Correl["BASE"].Fill(trig.trigger + " (T{})".format(trig.tier), trig2.trigger + " (T{})".format(trig2.tier), weight)
                    if pass_selection_lep[trig.trigger] and pass_selection_lep[trig2.trigger]:
                        self.trigLogic_Correl["SLCT"].Fill(trig.trigger + " (T{})".format(trig.tier), trig2.trigger + " (T{})".format(trig2.tier), weight)

        #############################################
        ### Define variable dictionary for values ###
        #############################################

        branchVals = {}
        branchVals['Muon_OSV_baseline'] = muon_osv_baseline
        branchVals['Muon_OSV_selection'] = muon_osv_selection
        branchVals['Electron_OSV_baseline'] = electron_osv_baseline
        branchVals['Electron_OSV_selection'] = electron_osv_selection
        branchVals['ESV_TriggerAndLeptonLogic_all'] = True
        branchVals['ESV_TriggerAndLeptonLogic_veto'] = (len(Vetoed) > 0)
        branchVals['ESV_TriggerAndLeptonLogic_hlt'] = (len(Vetoed) == 0 and len(Fired) > 0)
        branchVals['ESV_TriggerAndLeptonLogic_baseline'] = pass_baseline_bitset
        branchVals['ESV_TriggerAndLeptonLogic_selection'] = pass_selection_bitset
        for trig3 in self.eraTriggers:
            branchVals['ESV_TriggerEraBits_b{}'.format(trig3.uniqueEraBit)] = pass_baseline_lep.get(trig3.trigger, 0)
            branchVals['ESV_TriggerEraBits_s{}'.format(trig3.uniqueEraBit)] = pass_selection_lep.get(trig3.trigger, 0)

        ########################## 
        ### Write out branches ###
        ##########################         
        if self.out and self.mode == "Flag":
            for name, valType, valTitle, lVar in self.varTuple:
                self.out.fillBranch(name, branchVals[name])
        elif self.mode == "PassFail":
            #Do nothing
            pass
        elif self.mode == "Plot":
            #Do something?
            pass
            #Do pass through if plotting, make no assumptions about what should be done with the event
#FIXME            return True
        else:
            raise NotImplementedError("No method in place for TriggerAndLeptonLogic module in mode '{0}'".format(self.mode))


        if branchVals['ESV_TriggerAndLeptonLogic_{}'.format(self.passLevel)]:
            return True
        return False

    def getCutString(self):
        vetoSection = "!("
        for tn, trigger in enumerate(self.vetoTriggers):
            if tn > 0:
                vetoSection += " || "
            vetoSection += trigger.trigger
        vetoSection += ")"

        passSection = "("
        for tn, trigger in enumerate(self.Triggers):
            if tn > 0:
                passSection += " || "
            passSection += trigger.trigger
        passSection += ")"

        retString = ""
        if len(self.vetoTriggers) > 0: retString += vetoSection + " && "
        retString += passSection

        return retString

    def genWeightFunc(self, event):
        #Default value is currently useless, since the tree reader array tool raises an exception anyway
        return math.copysign(self.weightMagnitude, getattr(event, "genWeight", 1))
    def backupWeightFunc(self, event):
        return self.weightMagnitude
    def dataWeightFunc(self, event):
        return 1
