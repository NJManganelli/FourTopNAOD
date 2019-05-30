from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.intools import *

class BaselineSelector(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt=None, isData=True, era="2017", btagging=['DeepCSV','M'], lepPt=25, MET=50, HT=500, invertZWindow=False, GenTop_LepSelection=None):
        self.writeHistFile=True
        self.verbose=verbose
        self.probEvt = probEvt
        self.isData = isData
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
        #BTagging method, algorithm name, and chosen selection working point
        self.BTMeth = self.bTagWorkingPointDict[era][btagging[0]]
        self.BTWP =  self.bTagWorkingPointDict[era][btagging[0]][btagging[1]]
        self.BTAlg = self.bTagWorkingPointDict[era][btagging[0]]["Var"]
        print("BTMeth " + str(self.BTMeth))
        print("BTWP " + str(self.BTWP))
        print("BTAlg " + str(self.BTAlg))
        self.lepPt = lepPt
        self.MET = MET
        self.HT = HT
        self.invertZWindow = invertZWindow

        #event counters
        self.counter = 0
        self.maxEventsToProcess=maxevt

    def beginJob(self,histFile=None,histDirName=None):
        if histFile == None or histDirName == None:
            Module.beginJob(self, None, None)
        else:
            Module.beginJob(self,histFile,histDirName)
            self.cutflow = ROOT.TH1F("h_base_cutflow", "Cutflow in the baseline event selector;; Events", 1, 0, 1)
            self.addObject(self.cutflow)

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
        met = Object(event, "METFixEE2017") #FIXME: Placeholder until passed in via configuration?

        HLT = Object(event, "HLT")
        Filters = Object(event, "Flag") #For Data use only


        self.cutflow.Fill("> preselection", 1.0)
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
        self.cutflow.Fill("> MET filters", 1.0)
        if met.pt < self.MET:
            return False
        self.cutflow.Fill("> MET > {0:d}".format(self.MET), 1.0)



        # if not self.isData:
        #     gens = Collection(event, "GenPart")
        #     genjets = Collection(event, "GenJet")
        #     genfatjets = Collection(event, "GenJetAK8")
        #     gensubjets = Collection(event, "SubGenJetAK8")
        #     genmet = Object(event, "GenMET")
        #     generator = Object(event, "Generator")
        #     btagweight = Object(event, "btagWeight") #contains .CSVV2 and .DeepCSVB float weights
        #     LHE = Object(event, "LHE")
        #     PSWeights = Collection(event, "PSWeight")
        #     LHEWeight = getattr(event, "LHEWeight_originalXWGTUP")
        #     LHEScaleWeight = Collection(event, "LHEScaleWeight")
        #     # LHEReweightingWeight = Collection(event, "LHEReweightingWeight")
        #     LHEPdfWeight = Collection(event, "LHEPdfWeight")
        

        # selEle25 = []
        # selEle20 = []
        # selEle15 = []
        selEleUniform = []
        for idx, electron in enumerate(electrons):
            if abs(electron.eta) < 2.4 and electron.cutBased_Fall17_V1 >= 2 and electron.dz < 0.02:
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
        self.cutflow.Fill("> Dilepton", 1.0)
        lepCharge = [lep[1].charge for lep in (selMuUniform + selEleUniform)]
        jetsToClean = set([lep[1].jetIdx for lep in (selMuUniform + selEleUniform)])
        if len(lepCharge) !=2:
            print("Danger Will Robinson! Danger!")
        if lepCharge[0]*lepCharge[1] > 0:
            return False
        self.cutflow.Fill("> OS Leps", 1.0)
        Lep4Mom = [lep[1].p4() for lep in (selMuUniform + selEleUniform)]
        #calc invariant mass if two same flavor leptons
        if nMu == 2 or nEle == 2:
            DiLepMass = (Lep4Mom[0] + Lep4Mom[1]).M()
            #Low mass resonance rejection
            if DiLepMass < 20:
                return False
            self.cutflow.Fill("> Low M Res", 1.0)
            #Z mass resonance rejection or inversion
            if self.invertZWindow:
                if abs(DiLepMass - 91.0) > 15.0:
                    return False
                self.cutflow.Fill("> Z Window (IN)", 1.0)
            elif not self.invertZWindow:
                if abs(DiLepMass - 91.0) < 15.0:
                    return False
                self.cutflow.Fill("> Z Window (OUT)", 1.0)
        else:
            #0 default for different flavour leptons
            DiLepMass = -1
        
        selJets = []
        selBTsortedJets = []
        for idx, jet in enumerate(jets):
            if abs(jet.eta) < 2.5 and jet.jetId >= 6 and ((jet.pt > 25 and getattr(jet, self.BTAlg) > self.BTWP) or jet.pt > 30) and idx not in jetsToClean:
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
        self.cutflow.Fill("> 4+ Jets", 1.0)
        if nBTMedium < 2:
            return False
        self.cutflow.Fill("> 2+ Btag Jets", 1.0)

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
            HT += jet.pt
            H += jet.p4().P()
            if j > 1 and nBTMedium > 1:
                HT2M += jet.pt
                H2M += jet.p4().P()
            if getattr(jet, self.BTAlg) > self.BTWP:
                HTb += jet.pt

        if HT < self.HT:
            return False
        self.cutflow.Fill("> HT > {0:d}".format(self.HT), 1.0)

        if nJets > 3: #redundant, but only so long as 4 jet cut is in place
            jet1 = selBTsortedJets[0][1]
            jet2 = selBTsortedJets[1][1]
            dRbb = deltaR(jet1, jet2)
            HTRat = (jet1.pt + jet2.pt)/HT
            HTH = HT/H

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
