from __future__ import division, print_function
import ROOT
import math
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.toolbox import *

class JetMETLogic(Module):
    def __init__(self, passLevel, era="2017", subera=None, isData=True, weightMagnitude=1, fillHists=False, btagging=['DeepJet', 'M'], MET=[45, 50], HT=[450,500], ZWidth=15, jetPtVar = "pt_nom", jetMVar = "mass_nom", verbose=False, probEvt=None, ):
                 # genEquivalentLuminosity=1, genXS=1, genNEvents=1, genSumWeights=1, era="2017", btagging=['DeepCSV','M'], lepPt=25,  GenTop_LepSelection=None):
        """ Jet, MET, HT logic that performs lepton cleaning and jet selection. Optionally can do b-tagging, but mode without this requirement can be enabled/disabled

        passLevel is the level at which the module should trigger "True" to pass the event along to further modules. Available: 'all', 'baseline', 'selection'
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
        self.flagbits = {'isPrompt':0b000000000000001,
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

        #Bits for Event Selection Variables
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
                         'Jet_nJet20':0b00000100000000000000,
                         'HT':0b00001000000000000000,
                         'Jet_nBJet_2DCSV':0b00010000000000000000,
                         'Jet_nBJet_2DJet':0b00100000000000000000,
                    }

        #bits for Object Selection Variables - Jets
        self.jetbits = {'lepClean': 0b000000001,
                        'maxEta': 0b000000010,
                        'jetID': 0b000000100,
                        'pt25': 0b000001000,
                        'pt20': 0b000010000,
                        'unused': 0b000100000,
                        'DCSV': 0b001000000,
                        'DJET': 0b010000000,
                        'BTag_WP': 0b100000000
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
            #No histograms in here, right now


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
                         ('ESV_JetMETLogic_baseline', 'i', 'Passes JetMETLogic at event level baseline,'\
                          ' bits correspond to levels of baseline in JetMETLogic', None),
                         ('ESV_JetMETLogic_selection', 'i', 'Passes JetMETLogic at event level selection,'\
                          ' bits correspond to levels of selection in JetMETLogic', None),
                         ('ESV_JetMETLogic_nJet_baseline', 'i', 'Number of jets passing baseline requirements', None),
                         ('ESV_JetMETLogic_HT_baseline', 'D', 'Scalar sum of selected jets\' Pt', None),
                         ('ESV_JetMETLogic_H_baseline', 'D', 'Scalar sum of selected jets\' P', None),
                         ('ESV_JetMETLogic_HT2M_baseline', 'D', 'Scalar sum of selected jets\' Pt except 2 highest b-tagged if they are medium or tight', None),
                         ('ESV_JetMETLogic_H2M_baseline', 'D', 'Scalar sum of selected jets\' P except 2 highest b-tagged if they are medium or tight', None),
                         ('ESV_JetMETLogic_HTb_baseline', 'D', 'Scalar sum of Pt for medium and tight b-tagged jets', None),
                         ('ESV_JetMETLogic_HTH_baseline', 'D', 'Hadronic centrality, HT/H', None),
                         ('ESV_JetMETLogic_HTRat_baseline', 'D', 'Ratio of Pt for two highest b-tagged jets to HT', None),
                         ('ESV_JetMETLogic_dRbb_baseline', 'D', 'DeltaR between the two highest b-tagged jets', None),
                         ('ESV_JetMETLogic_DiLepMass_baseline', 'D', 'Invariant mass of same-flavour leptons (0 default)', None),
                         ('ESV_JetMETLogic_nJet_selection', 'i', 'Number of jets passing selection requirements', None),
                         ('ESV_JetMETLogic_HT_selection', 'D', 'Scalar sum of selected jets\' Pt', None),
                         ('ESV_JetMETLogic_H_selection', 'D', 'Scalar sum of selected jets\' P', None),
                         ('ESV_JetMETLogic_HT2M_selection', 'D', 'Scalar sum of selected jets\' Pt except 2 highest b-tagged if they are medium or tight', None),
                         ('ESV_JetMETLogic_H2M_selection', 'D', 'Scalar sum of selected jets\' P except 2 highest b-tagged if they are medium or tight', None),
                         ('ESV_JetMETLogic_HTb_selection', 'D', 'Scalar sum of Pt for medium and tight b-tagged jets', None),
                         ('ESV_JetMETLogic_HTH_selection', 'D', 'Hadronic centrality, HT/H', None),
                         ('ESV_JetMETLogic_HTRat_selection', 'D', 'Ratio of Pt for two highest b-tagged jets to HT', None),
                         ('ESV_JetMETLogic_dRbb_selection', 'D', 'DeltaR between the two highest b-tagged jets', None),
                         ('ESV_JetMETLogic_DiLepMass_selection', 'D', 'Invariant mass of same-flavour leptons (0 default)', None),
                       ]
        self.deprecated = [('ESV_JetMETLogic_nJet', 'I', 'Number of jets passing selection requirements', None),
                           ('ESV_JetMETLogic_nJetBTL', 'I', 'Number of jets passing selection requirements and loose b-tagged', None),
                           ('ESV_JetMETLogic_nJetBTM', 'I', 'Number of jets passing selection requirements and medium b-tagged', None),
                           ('ESV_JetMETLogic_nJetBTT', 'I', 'Number of jets passing selection requirements and tight b-tagged', None),
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
                if leptons_baseline[0][1].charge * leptons_baseline[1][1].charge > 0:
                    print("Charging up!")
            if self.passLevel == 'selection':
                if len(leptons_selection) > 2:
                    print("Mayday!")
                if leptons_selection[0][1].charge * leptons_selection[1][1].charge > 0:
                    print("Charging up!")
        
        #passbit if outside the Z window in same-flavor event or all in different-flavor event
        if (len(electron_baseline) > 1 or len(muon_baseline) > 1):
            DiLepMass_baseline = (leptons_baseline[0][1].p4() + leptons_baseline[1][1].p4()).M()
            if abs( DiLepMass_baseline - 91.0) > self.ZWidth:
                ESV_baseline += self.passbits['Lepton_ZWindow']
        else: #opposite-flavor
            ESV_baseline += self.passbits['Lepton_ZWindow']
            DiLepMass_baseline = -1
        #Should see no difference in invariant mass except when a collection drops below length 1, given the TriggerAndLeptonLogic Module in LeptonLogic.py
        if (len(electron_selection) > 1 or len(muon_selection) > 1):
            DiLepMass_selection = (leptons_selection[0][1].p4() + leptons_selection[1][1].p4()).M()
            if abs( DiLepMass_selection - 91.0) > self.ZWidth:
                ESV_selection += self.passbits['Lepton_ZWindow']
        else: #opposite-flavor
            ESV_selection += self.passbits['Lepton_ZWindow']
            DiLepMass_selection = -1
        
        ############
        ### Jets ###
        ###########
        jetsToClean_selection = set([lep[1].jetIdx for lep in leptons_selection])
        selJets_selection = []
        selBTsortedJets_selection = []
        jetbits_selection = [0]*len(jets)

        jetsToClean_baseline = set([lep[1].jetIdx for lep in leptons_baseline])
        selJets_baseline = []
        selBTsortedJets_baseline = []
        jetbits_baseline = [0]*len(jets)
        
        for idx, jet in enumerate(jets):
            if idx not in jetsToClean_baseline:
                jetbits_baseline[idx] += self.jetbits['lepClean']
            if abs(jet.eta) < 2.5:
                jetbits_baseline[idx] += self.jetbits['maxEta']
            if jet.jetId >= 2:
                jetbits_baseline[idx] += self.jetbits['jetID']
            if getattr(jet, self.jetPtVar) > 25:
                jetbits_baseline[idx] += self.jetbits['pt25']
            if getattr(jet, self.jetPtVar) > 20:
                jetbits_baseline[idx] += self.jetbits['pt20']
            if getattr(jet, self.bTagWorkingPointDict[self.era]['DeepCSV']['Var']) > self.bTagWorkingPointDict[self.era]['DeepCSV']['L']:
                jetbits_baseline[idx] += self.jetbits['DCSV']
            if getattr(jet, self.bTagWorkingPointDict[self.era]['DeepJet']['Var']) > self.bTagWorkingPointDict[self.era]['DeepJet']['L']:
                jetbits_baseline[idx] += self.jetbits['DJET']
            if getattr(jet, self.BTAlg) > self.BTWP:
                jetbits_baseline[idx] += self.jetbits['BTag_WP']
            if jetbits_baseline[idx] >= 0b000010111:
                selJets_baseline.append((idx, jet))
                selBTsortedJets_baseline.append((idx, jet))
            # #BTagging input disabled without highest bit! Use DeepJet Loose...
            # if jetbits_baseline[idx] >= 0b010010111:


            if idx not in jetsToClean_selection:
                jetbits_selection[idx] += self.jetbits['lepClean']
            if abs(jet.eta) < 2.5:
                jetbits_selection[idx] += self.jetbits['maxEta']
            if jet.jetId >= 6:
                jetbits_selection[idx] += self.jetbits['jetID']
            if getattr(jet, self.jetPtVar) > 25:
                jetbits_selection[idx] += self.jetbits['pt25']
            if getattr(jet, self.jetPtVar) > 20:
                jetbits_selection[idx] += self.jetbits['pt20']
            if getattr(jet, self.bTagWorkingPointDict[self.era]['DeepCSV']['Var']) > self.bTagWorkingPointDict[self.era]['DeepCSV']['M']:
                jetbits_selection[idx] += self.jetbits['DCSV']
            if getattr(jet, self.bTagWorkingPointDict[self.era]['DeepJet']['Var']) > self.bTagWorkingPointDict[self.era]['DeepJet']['M']:
                jetbits_selection[idx] += self.jetbits['DJET']
            if getattr(jet, self.BTAlg) > self.BTWP:
                jetbits_selection[idx] += self.jetbits['BTag_WP']
            if jetbits_selection[idx] >= 0b000010111:
                selJets_selection.append((idx, jet))
                selBTsortedJets_selection.append((idx, jet))
            # #BTagging input disabled without highest bit! Use DeepJet Medium...
            # if jetbits_selection[idx] >= 0b010010111:

        nJets_baseline = len(selJets_baseline)
        nJets_selection = len(selJets_selection)
        #BTagging algo used for sorting, still
        selBTsortedJets_baseline.sort(key=lambda j : getattr(j[1], self.BTAlg), reverse=True)
        selBTsortedJets_selection.sort(key=lambda j : getattr(j[1], self.BTAlg), reverse=True)

        #B-tagged jets
        # selBTLooseJets = [jetTup for jetTup in selBTsortedJets if getattr(jetTup[1], self.BTAlg) > self.BTMeth['L']]
        # selBTMediumJets = [jetTup for jetTup in selBTLooseJets if getattr(jetTup[1], self.BTAlg) > self.BTMeth['M']]
        # selBTTightJets = [jetTup for jetTup in selBTMediumJets if getattr(jetTup[1], self.BTAlg) > self.BTMeth['T']]
        # selBTJets = [jetTup for jetTup in selBTsortedJets if getattr(jetTup[1], self.BTAlg) > self.BTWP]
        # nJets = len(selJets)
        # nBTLoose = len(selBTLooseJets)
        # nBTMedium = len(selBTMediumJets)
        # nBTTight = len(selBTTightJets)
        # nBTSelected = len(selBTJets)

        nJets25_baseline = [bits for bits in jetbits_baseline if (jetbits & self.jetbits['pt25'] > 0)]
        nBJetsDeepCSV_baseline = [bits for bits in jetbits_baseline if (jetbits & self.jetbits['DCSV'] > 0)]
        nBJetsDeepJet_baseline = [bits for bits in jetbits_baseline if (jetbits & self.jetbits['DJET'] > 0)]
        #Just 3 jets in baseline
        if nJets_baseline > 2:
            ESV_baseline += self.passbits['Jet_nJet20']
        if len(nJets25_baseline) > 2:
            ESV_baseline += self.passbits['Jet_nJet25']
        #Require 2 loose tagged jets
        if len(nBJetsDeepCSV_baseline) > 1:
            ESV_baseline += self.passbits['Jet_nBJet_2DCSV']
        if len(nBJetsDeepJet_baseline) > 1:
            ESV_baseline += self.passbits['Jet_nBJet_2DJet']

        nJets25_selection = [bits for bits in jetbits_selection if (jetbits & self.jetbits['pt25'] > 0)]
        nBJetsDeepCSV_selection = [bits for bits in jetbits_selection if (jetbits & self.jetbits['DCSV'] > 0)]
        nBJetsDeepJet_selection = [bits for bits in jetbits_selection if (jetbits & self.jetbits['DJET'] > 0)]
        #4 jets in selection
        if nJets_selection > 3:
            ESV_selection += self.passbits['Jet_nJet20']
        if len(nJets25_selection) > 3:
            ESV_selection += self.passbits['Jet_nJet25']
        #Require 2 loose tagged jets
        if len(nBJetsDeepCSV_selection) > 1:
            ESV_selection += self.passbits['Jet_nBJet_2DCSV']
        if len(nBJetsDeepJet_selection) > 1:
            ESV_selection += self.passbits['Jet_nBJet_2DJet']

        #HT and other calculations
        HT_baseline = 0
        H_baseline = 0
        HT2M_baseline = 0
        H2M_baseline = 0
        HTb_baseline = 0
        HTH_baseline = 0
        HTRat_baseline = 0
        dRbb_baseline = -1
        
        for j, jet in selBTsortedJets_baseline:
            HT_baseline += getattr(jet, self.jetPtVar)
            jetP4_baseline = ROOT.TLorentzVector()
            jetP4_baseline.SetPtEtaPhiM(getattr(jet, self.jetPtVar),
                               getattr(jet, "eta"),
                               getattr(jet, "phi"),
                               getattr(jet, self.jetMVar)
            )
            H_baseline += jetP4.P()
            #Only use deepjet
            if j > 1 and len(nBJetsDeepJet_baseline) > 1:
                HT2M_baseline += getattr(jet, self.jetPtVar)
                H2M_baseline += jetP4.P()
            if jetbits_baseline[j] & self.jetbits['DJET']:
                HTb_baseline += getattr(jet, self.jetPtVar)

        if HT_baseline >= self.HT[0]:
            ESV_baseline += self.passbits['HT']
        if len(selBTsortedJets_baseline) > 3: #redundant, but only so long as 4 jet cut is in place
            jet1_baseline = selBTsortedJets_baseline[0][1]
            jet2_baseline = selBTsortedJets_baseline[1][1]
            dRbb_baseline = deltaR(jet1, jet2)
            HTRat_baseline = (jet1_baseline.pt + jet2_baseline.pt)/HT
            HTH_baseline = HT_baseline/H_baseline
        else:
            dRbb_baseline = -1
            HTRat_baseline = -0.1
            HTH_baseline = -0.1


        #HT and other calculations
        HT_selection = 0
        H_selection = 0
        HT2M_selection = 0
        H2M_selection = 0
        HTb_selection = 0
        HTH_selection = 0
        HTRat_selection = 0
        dRbb_selection = -1
        
        for j, jet in selBTsortedJets_selection:
            HT_selection += getattr(jet, self.jetPtVar)
            jetP4_selection = ROOT.TLorentzVector()
            jetP4_selection.SetPtEtaPhiM(getattr(jet, self.jetPtVar),
                               getattr(jet, "eta"),
                               getattr(jet, "phi"),
                               getattr(jet, self.jetMVar)
            )
            H_selection += jetP4.P()
            #Only use deepjet
            if j > 1 and len(nBJetsDeepJet_selection) > 1:
                HT2M_selection += getattr(jet, self.jetPtVar)
                H2M_selection += jetP4.P()
            if jetbits_selection[j] & self.jetbits['DJET']:
                HTb_selection += getattr(jet, self.jetPtVar)

        if HT_selection >= self.HT[0]:
            ESV_selection += self.passbits['HT']
        if len(selBTsortedJets_selection) > 3: #redundant, but only so long as 4 jet cut is in place
            jet1_selection = selBTsortedJets_selection[0][1]
            jet2_selection = selBTsortedJets_selection[1][1]
            dRbb_selection = deltaR(jet1, jet2)
            HTRat_selection = (jet1_selection.pt + jet2_selection.pt)/HT
            HTH_selection = HT_selection/H_selection
        else:
            dRbb_selection = -1
            HTRat_selection = -0.1
            HTH_selection = -0.1

        ####################################
        ### Variables for branch filling ###
        ####################################
        branchVals = {}
        branchVals['Jet_OSV_baseline'] = jetbits_baseline
        branchVals['Jet_OSV_selection'] = jetbits_selection
        branchVals['ESV_JetMETLogic_baseline'] = ESV_baseline
        branchVals['ESV_JetMETLogic_selection'] = ESV_selection
        branchVals['ESV_JetMETLogic_nJet_baseline'] = nJets_baseline
        branchVals['ESV_JetMETLogic_nJet_selection'] = nJets_selection
        # branchVals['ESV_JetMETLogic_nJetBTL'] = nBTLoose
        # branchVals['ESV_JetMETLogic_nJetBTM'] = nBTMedium
        # branchVals['ESV_JetMETLogic_nJetBTT'] = nBTTight
        branchVals['ESV_JetMETLogic_HT_baseline'] = HT_baseline
        branchVals['ESV_JetMETLogic_H_baseline'] = H_baseline
        branchVals['ESV_JetMETLogic_HT2M_baseline'] = HT2M_baseline
        branchVals['ESV_JetMETLogic_H2M_baseline'] = H2M_baseline
        branchVals['ESV_JetMETLogic_HTb_baseline'] = HTb_baseline
        branchVals['ESV_JetMETLogic_HTH_baseline'] = HTH_baseline
        branchVals['ESV_JetMETLogic_HTRat_baseline'] = HTRat_baseline
        branchVals['ESV_JetMETLogic_dRbb_baseline'] = dRbb_baseline
        branchVals['ESV_JetMETLogic_DiLepMass_baseline'] = DiLepMass_baseline
        branchVals['ESV_JetMETLogic_HT_selection'] = HT_selection
        branchVals['ESV_JetMETLogic_H_selection'] = H_selection
        branchVals['ESV_JetMETLogic_HT2M_selection'] = HT2M_selection
        branchVals['ESV_JetMETLogic_H2M_selection'] = H2M_selection
        branchVals['ESV_JetMETLogic_HTb_selection'] = HTb_selection
        branchVals['ESV_JetMETLogic_HTH_selection'] = HTH_selection
        branchVals['ESV_JetMETLogic_HTRat_selection'] = HTRat_selection
        branchVals['ESV_JetMETLogic_dRbb_selection'] = dRbb_selection
        branchVals['ESV_JetMETLogic_DiLepMass_selection'] = DiLepMass_selection

        branchVals['ESV_JetMETLogic_all'] = True
        #1-10 common, 11 MET_baseline, 13 is Z_Window (not required), 14 is nJets25 (nr), 15 is nJets20, 16 is HT, 17 and 18 are btagging (nr x2)
        branchVals['ESV_JetMETLogic_baseline'] = (branchVals['ESV_JetMETLogic_baseline'] & 0b00001100011111111111 >= 0b00001100011111111111)
        #1-10 common, 12 MET_selection, 13 is Z_Window (not required), 14 is nJets25 (nr), 15 is nJets20, 16 is HT, 17 and 18 are btagging (nr x2)
        branchVals['ESV_JetMETLogic_selection'] = (branchVals['ESV_JetMETLogic_selection'] & 0b00001100101111111111 > 0b00001100101111111111)

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

        if branchVals['ESV_JetMETLogic_{}'.format(self.passLevel)]:
            return True
        return False

    def genWeightFunc(self, event):
        #Default value is currently useless, since the tree reader array tool raises an exception anyway
        return math.copysign(self.weightMagnitude, getattr(event, "genWeight", 1))
    def backupWeightFunc(self, event):
        return self.weightMagnitude
    def dataWeightFunc(self, event):
        return 1
