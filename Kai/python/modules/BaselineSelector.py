from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.intools import *

class BaselineSelector(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt, isData=True, era="2017", btagging=['DeepCSV','M']):
        self.writeHistFile=True
        self.verbose=verbose
        self.probEvt = probEvt
        self.isData = isData
        if probEvt:
            #self.probEvt = probEvt
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
        self.bTagWorkingPointDict = {
            '2017':{
                'CSVv2':{
                    'L': 0.5803,
                    'M': 0.8838,
                    'T': 0.9693
                    }
                'DeepCSV':{
                    'L': 0.1522,
                    'M': 0.4941,
                    'T': 0.8001
                    }
                'DeepJet':{
                    'L': 0.0521,
                    'M': 0.3033,
                    'T': 0.7489
                    }
            }
        }
        self.BTWP = self.bTagWorkingPointDict[era][btagging[0]]
        self.BTS =  self.bTagWorkingPointDict[era][btagging[0]][btagging[1]]
        print("BTWP " + str(self.BTWP))
        print("BTS " + str(self.BTS))

        #event counters
        self.counter = 0
        self.maxEventsToProcess=maxevt

    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)

        self.h_nJets_low=ROOT.TH1F('h_nJets_low',   'nJets (pt > 20 && |eta| < 2.5 && tightId); nJets; events', 20, 0, 20)
        self.addObject(self.h_nJets_low)
        self.h_nJets_old=ROOT.TH1F('h_nJets_old',   'nJets ((pt > 30 || pt > 25 && Medium CSVv2) && |eta| < 2.5 && tightId); nJets; events', 20, 0, 20)
        self.addObject(self.h_nJets_old)
        self.h_nJets_oldDeepCSV=ROOT.TH1F('h_nJets_oldDeepCSV',   'nJets ((pt > 30 || pt > 25 && Medium DeepCSV) && |eta| < 2.5 && tightId); nJets; events', 20, 0, 20)
        self.addObject(self.h_nJets_oldDeepCSV)
        self.h_nJets_MCSVv2=ROOT.TH1F('h_MCSVv2',   'nJets (pt > 20 && |eta| < 2.5 && tightId && Medium CSVv2); nJets; events', 20, 0, 20)
        self.addObject(self.h_nJets_MCSVv2)
        self.h_nJets_MDeepCSV=ROOT.TH1F('h_MDeepCSV',   'nJets (pt > 20 && |eta| < 2.5 && tightId && Medium DeepCSV); nJets; events', 20, 0, 20)
        self.addObject(self.h_nJets_MDeepCSV)
        self.h_nJets_MDeepJet=ROOT.TH1F('h_MDeepJet',   'nJets (pt > 20 && |eta| < 2.5 && tightId && Medium DeepJet); nJets; events', 20, 0, 20)
        self.addObject(self.h_nJets_MDeepJet)
        self.h_nLeps=ROOT.TH1F('h_nLeps',   'number Leptonic Top Decays; number Leptonic Top Decays; events', 5, 0, 5)
        self.addObject(self.h_nLeps)

        self.h_ElDzCat=ROOT.TH3F('h_ElDzCat',   't->W->e Dz; Dz (cm); nJets; nBJets', 
                                     100, 0, 0.15, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_ElDzCat)
        self.h_MuDzCat=ROOT.TH3F('h_MuDzCat',   't->W->mu Dz; Dz (cm); nJets; nBJets', 
                                     100, 0, 0.15, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_MuDzCat)
        self.h_ElPtCat=ROOT.TH3F('h_ElPtCat',   't->W->e Pt; Pt (GeV); nJets; nBJets', 
                                     400, 0, 400, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_ElPtCat)
        self.h_MuPtCat=ROOT.TH3F('h_MuPtCat',   't->W->mu Pt; Pt (GeV); nJets; nBJets', 
                                     400, 0, 400, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_MuPtCat)
        self.h_ElKinCat=ROOT.TH2F('h_ElKinCat',   't->W->e Kin; eta; phi', 
                                      200, -3, 3, 200, -3.1416, 3.1416)
        self.addObject(self.h_ElKinCat)
        self.h_MuKinCat=ROOT.TH2F('h_MuKinCat',   't->W->mu Kin; eta; phi', 
                                      200, -3, 3, 200, -3.1416, 3.1416)
        self.addObject(self.h_MuKinCat)
        self.h_TauElDzCat=ROOT.TH3F('h_TauElDzCat',   't->W->Tau->e Dz; Dz (cm); nJets; nBJets', 
                                     100, 0, 0.15, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_TauElDzCat)
        self.h_TauMuDzCat=ROOT.TH3F('h_TauMuDzCat',   't->W->Tau->mu Dz; Dz (cm); nJets; nBJets', 
                                     100, 0, 0.15, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_TauMuDzCat)
        self.h_TauElPtCat=ROOT.TH3F('h_TauElPtCat',   't->W->Tau->e Pt; Pt (GeV); nJets; nBJets', 
                                     400, 0, 400, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_TauElPtCat)
        self.h_TauMuPtCat=ROOT.TH3F('h_TauMuPtCat',   't->W->Tau->mu Pt; Pt (GeV); nJets; nBJets', 
                                     400, 0, 400, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_TauMuPtCat)
        self.h_bMatchedJetCutFlow=ROOT.TH2F('h_bMatchedJetCutFlow',
                                                   'CutFlow of best matched b jets;Category;Number of Jets',
                                                1, 0, 1, 1, 0, 1)
        self.addObject(self.h_bMatchedJetCutFlow)
        self.h_bMultiJet=ROOT.TH2F('h_bMultiJet',
                                       'b -> 2+ AK4 Jets Mult; nJets(2016-like);number of multi-jet b quarks',
                                                20, 0, 20, 5, 0, 5)
        self.addObject(self.h_bMultiJet)

        #Sorted leptons
        self.h_DirectLepPtCat = {} #pt, nJet, nBJet
        self.h_IndirectLepPtCat = {}
        self.h_TopSystemPt = {} #top, b, W
        self.h_bMatchedJet = {} #jetpt, jet rank, nJet
        self.h_bMatchedJetDR = {} #b 3-momentum, DR best match, DR second best match
        self.h_bMatchedJetVRank = {} #Rank best, 2nd best, 3rd best
        self.h_bMatchedJetHad = {} #Rank best, Hadron Flavour (Ghost clustering from GenHFMatcher)
        self.h_WMatchedJet1 = {} #W jet 1 pt, match rank, nJet
        self.h_WMatchedJet2 = {} #W jet 2 pt, match rank, nJet
        self.h_bMatchedJetDeepCSV = {} #1st and 2nd best matched jets' DeepCSV score
        self.h_bMatchedJetDeepJet = {} #1st and 2nd best matched jets' DeepJet score
        self.h_bMatchedJetSep = {} #DeltaR separation between 1st and 2nd best ranked jets
        for i in xrange(4):
            self.h_DirectLepPtCat[i]=ROOT.TH3F('h_DirectLepPtCat_{0:d}'.format(i+1),   
                                                   'Pt PF Lepton (t->W->Lep) (R{0:d} t pt); Pt (GeV); nJets; nBJets'.format(i+1), 
                                         400, 0, 400, 20, 0, 20, 8, 0, 8)
            self.addObject(self.h_DirectLepPtCat[i])
            self.h_IndirectLepPtCat[i]=ROOT.TH3F('h_IndirectLepPtCat_{0:d}'.format(i+1),   
                                                     'Pt PF Lepton (t->W->Tau->Lep) (R{0:d} t pt); Pt (GeV); nJets; nBJets'.format(i+1), 
                                         400, 0, 400, 20, 0, 20, 8, 0, 8)
            self.addObject(self.h_IndirectLepPtCat[i])
            self.h_TopSystemPt[i]=ROOT.TH3F('h_TopSystemPt_{0:d}'.format(i+1),   
                                                'Top Sys Pt (R{0:d} t pt); Top_Pt (GeV); Bottom_Pt (GeV); W_Pt (GeV)'.format(i+1), 
                                                400, 0, 1000, 400, 0, 1000, 400, 0, 1000)
            self.addObject(self.h_TopSystemPt[i])
            self.h_bMatchedJet[i]=ROOT.TH3F('h_bMatchedJet_{0:d}'.format(i+1),   
                                                'b Matched Jet; b Jet Pt (GeV); b Jet Match Rank (3-mom ratio); nJet Multiplicity (20GeV, ...)', 
                                                500, 0, 500, 500, 0, 5, 20, 0, 20)
            self.addObject(self.h_bMatchedJet[i])
            self.h_bMatchedJetDR[i]=ROOT.TH3F('h_bMatchedJetDR_{0:d}'.format(i+1),   
                                                  'b Matched Jet DeltaR; b quark 3 Momentum; DeltaR(b quark, Best Matched Jet); DeltaR(b quark, 2nd Best Matched Jet)', 
                                                  500, 0, 500, 100, -0.2, 5, 100, -0.2, 5)
            self.addObject(self.h_bMatchedJetDR[i])
            self.h_bMatchedJetSep[i]=ROOT.TH2F('h_bMatchedJetSep_{0:d}'.format(i+1),   
                                                   'b Matched Jet Separation; b quark Pt (GeV);DeltaR(best jet, 2nd best jet)', 
                                                   500, 0, 500, 500, 0, 10)
            self.addObject(self.h_bMatchedJetSep[i])
            self.h_bMatchedJetVRank[i]=ROOT.TH3F('h_bMatchedJetVRank_{0:d}'.format(i+1),   
                                                     'b Jet Match ranks (R{0:d} b pt); Rank of Best Match; Rank of Second Best; Rank of 3rd Best'.format(i+1), 
                                                     100, 0, 2, 100, 0, 2, 100, 0, 2)
            self.addObject(self.h_bMatchedJetVRank[i])
            self.h_WMatchedJet1[i]=ROOT.TH3F('h_WMatchedJet1_{0:d}'.format(i+1),   
                                                 'W Matched Jet 2; W Jet Pt (GeV); W Jet Match Rank (3-momentum proxy); nJet Multiplicity (20GeV, ...)'.format(i+1), 
                                                500, 0, 500, 500, 0, 5, 20, 0, 20)
            self.addObject(self.h_WMatchedJet1[i])
            self.h_WMatchedJet2[i]=ROOT.TH3F('h_WMatchedJet2_{0:d}'.format(i+1),   
                                                 'W Matched Jet 2; W Jet Pt (GeV); W Jet Match Rank (3-momentum proxy); nJet Multiplicity (20GeV, ...)'.format(i+1), 
                                                500, 0, 500, 500, 0, 5, 20, 0, 20)
            self.addObject(self.h_WMatchedJet2[i])
            self.h_bMatchedJetHad[i]=ROOT.TH2F('h_bMatchedJetHad_{0:d}'.format(i+1),   
                                                   'b Jet Rank v Hadron Flavour (R{0:d} b pt); Rank of Best Match; Had Flavour (GenHFMatcher)'.format(i+1), 
                                                     100, 0, 2, 7, -1, 6)
            self.addObject(self.h_bMatchedJetHad[i])
            self.h_bMatchedJetDeepCSV[i]=ROOT.TH2F('h_bMatchedJetDeepCSV_{0:d}'.format(i+1),   
                                                  'b Jet Matches DeepCSV Value; DeepCSV of best match; DeepCSV of 2nd best match', 
                                                       200, -1, 1, 200, -1, 1)
            self.addObject(self.h_bMatchedJetDeepCSV[i])
            self.h_bMatchedJetDeepJet[i]=ROOT.TH2F('h_bMatchedJetDeepJet_{0:d}'.format(i+1),   
                                                  'b Jet Matches DeepJet Value; DeepJet of best match; DeepJet of 2nd best match', 
                                                       200, -1, 1, 200, -1, 1)
            self.addObject(self.h_bMatchedJetDeepJet[i])

        self.h_METCat=ROOT.TH3F('h_METCat',   'MET vs jet and b-tagged jet multiplicities; MET (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_METCat)
        self.h_HTCat=ROOT.TH3F('h_HTCat',   'HT vs jet and b-tagged jet multiplicities; HT (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_HTCat)
        self.h_HCat=ROOT.TH3F('h_HCat',   'H vs jet and b-tagged jet multiplicities; H (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_HCat)
        self.h_HT2MCat=ROOT.TH3F('h_HT2MCat',   'HT2M vs jet and b-tagged jet multiplicities; HT2M (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_HT2MCat)
        self.h_H2MCat=ROOT.TH3F('h_H2MCat',   'H2M vs jet and b-tagged jet multiplicities; H2M (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_H2MCat)
        self.h_HTbCat=ROOT.TH3F('h_HTbCat',   'HTb vs jet and b-tagged jet multiplicities; HTb (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_HTbCat)
        self.h_HTHCat=ROOT.TH3F('h_HTHCat',   'HTH vs jet and b-tagged jet multiplicities; HTH (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_HTHCat)
        self.h_HTRatCat=ROOT.TH3F('h_HTRatCat',   'HTRat vs jet and b-tagged jet multiplicities; HTRat (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_HTRatCat)
        self.h_dRbbCat=ROOT.TH3F('h_dRbbCat',   'dRbb vs jet and b-tagged jet multiplicities; dRbb; nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 5, 20, 0, 20, 8, 0, 8)
        self.addObject(self.h_dRbbCat)
        
        self.h_RecoVGenJet_low=ROOT.TH2F('h_RecoVGenJet_low',   'AK4 Reco vs Gen Jet Multiplicity; nJets(pt > 20 && |eta| < 2.5 && TightLepVeto ID); nGenJets(pt > 20 && |eta| < 2.5)', 20, 0, 20, 20, 0, 20)
        self.addObject(self.h_RecoVGenJet_low)
        self.h_RecoVGenJet_DeepJet=ROOT.TH2F('h_RecoVGenJet_DeepJet',   'AK4 Reco vs Gen Jet Multiplicity; nJets(pt > 20 && |eta| < 2.5 && TightLepVeto ID && Medium DeepJet); nGenJets(pt > 20 && |eta| < 2.5 && b Had Flav)', 20, 0, 20, 20, 0, 20)
        self.addObject(self.h_RecoVGenJet_DeepJet)
        self.h_RecoVGenJet_oldDeepCSV=ROOT.TH2F('h_RecoVGenJet_oldDeepCSV',   'AK4 Reco vs Gen Jet Multiplicity; nJets((pt > 30 || pt > 25 && Med CSVv2) && |eta| < 2.5 && TightLepVeto ID); nGenJets((pt > 30 || b Had Flav) && |eta| < 2.5)', 20, 0, 20, 20, 0, 20)
        self.addObject(self.h_RecoVGenJet_oldDeepCSV)
        self.h_RecoVGenJet_DeepCSV=ROOT.TH2F('h_RecoVGenJet_DeepCSV',   'AK4 Reco vs Gen Jet Multiplicity; nJets(pt > 20 && |eta| < 2.5 && TightLepVeto ID && Medium DeepJet); nGenJets(pt > 20 && |eta| < 2.5 && b Had Flav)', 20, 0, 20, 20, 0, 20)
        self.addObject(self.h_RecoVGenJet_DeepCSV)

        self.h_RankVotesVBottomPt=ROOT.TH2F('h_RankVotesVBottomPt', '; bottom pt; net weighted votes', 400, 0, 400, 100, 0, 10)
        self.addObject(self.h_RankVotesVBottomPt)
        
        #print("histfile=" + str(histFile) + " directoryname=" + str(histDirName))
        #if histFile != None and histDirName != None:
            #self.writeHistFile=True
            #prevdir = ROOT.gDirectory
            #self.histFile = histFile
            #self.histFile.cd()
            #self.dir = self.histFile.mkdir( histDirName )
            #prevdir.cd()
            #self.objs = []
            #if self.makeHistos:
                # self.h_jSel_map = ROOT.TH2F('h_jSel_map', ';Jet Eta;Jet Phi', 40, -2.5, 2.5, 20, -3.14, 3.14)
                # self.addObject(self.h_jSel_map)
                # self.MADEHistos=True
        
    def endJob(self):
        if hasattr(self, 'objs') and self.objs != None:
            prevdir = ROOT.gDirectory
            self.dir.cd()
            for obj in self.objs:
                obj.Write()
            prevdir.cd()
            if hasattr(self, 'histFile') and self.histFile != None: 
                self.histFile.Close()

    # def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    #     self.out = wrappedOutputTree
    #     self.varDict = getMCTreeVarDict()
    #     if not self.out:
    #         print("No Output file selected, cannot append branches")
    #     else:
    #         self.out.branch('nGenTop', 'i', title='Number of Generator-Level Tops in the event')
    #         for name, valType, valTitle in self.varDict:
    #             #print("name: " + str(name) + " valType: " + str(valType) + " valTitle: " + str(valTitle))
    #             self.out.branch("GenTop_%s"%(name), valType, lenVar="nGenTop", title=valTitle)


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

        if not self.isData:
            gens = Collection(event, "GenPart")
            genjets = Collection(event, "GenJet")
            genfatjets = Collection(event, "GenJetAK8")
            gensubjets = Collection(event, "SubGenJetAK8")
            genmet = Object(event, "GenMET")
            generator = Object(event, "Generator")
            btagweight = Object(event, "btagWeight") #contains .CSVV2 and .DeepCSVB float weights
            LHE = Object(event, "LHE")
            PSWeights = Collection(event, "PSWeight")
            LHEWeight = getattr(event, "LHEWeight_originalXWGTUP")
            LHEScaleWeight = Collection(event, "LHEScaleWeight")
            # LHEReweightingWeight = Collection(event, "LHEReweightingWeight")
            LHEPdfWeight = Collection(event, "LHEPdfWeight")


        nJets = [jet for jet in jets if abs(jet.eta) < 2.5 and jet.jetId >= 6 and jet.pt > 25 and
                 jet.muonIdx1 not in selMus and jet.muonIdx2 not in selMus and 
                 jet.electronIdx1 not in selEles and jet.electronIdx2 not in selEles]
        nJets = [jet for jet in nJets if jet.pt > 30 or jet.btagDeepB > 0.4941]
        # nJets_oldDeepJet = [jet for jet in nJets_old if jet.pt > 30 or jet.btagDeepFlavB > 0.3033]

        #B-tagged jets
        nJetsMCSVv2 = [jet for jet in nJets if jet.btagCSVV2 > 0.8838]
        nJetsMDeepCSV = [jet for jet in nJets_low if jet.btagDeepB > 0.4941]
        nJetsMDeepJet = [jet for jet in nJets_low if jet.btagDeepFlavB > 0.3033]

        nJetsMCSVv2 = [jet for jet in nJets if jet.btagCSVV2 > 0.8838]
        nJetsMDeepCSV = [jet for jet in nJets_low if jet.btagDeepB > 0.4941]
        nJetsMDeepJet = [jet for jet in nJets_low if jet.btagDeepFlavB > 0.3033]

        nJetsMCSVv2 = [jet for jet in nJets if jet.btagCSVV2 > 0.8838]
        nJetsMDeepCSV = [jet for jet in nJets_low if jet.btagDeepB > 0.4941]
        nJetsMDeepJet = [jet for jet in nJets_low if jet.btagDeepFlavB > 0.3033]

        nJetsBTagLoose =  [jet for jet in nJets if jet.btagCSVV2 > 0.8838]


        #HT and other calculations
        HT = 0
        H = 0
        HT2M = 0
        H2M = 0
        HTb = 0
        nJetsBSorted = [jet for jet in nJets]
        nJetsBSorted.sort(key=lambda jet : jet.btagDeepB, reverse=True)
        for j, jet in enumerate(nJetsBSorted):
            HT += jet.pt
            H += jet.p4().P()
            if j > 1 and len(nJetsMDeepCSV) > 1:
                HT2M += jet.pt
                H2M += jet.p4().P()
            if jet.btagDeepB > .4941:
                HTb += jet.pt
        self.h_METCat.Fill(met.pt ,len(nJets), len(nJetsMDeepCSV))
        self.h_HTCat.Fill(HT ,len(nJets), len(nJetsMDeepCSV))
        self.h_HCat.Fill(H ,len(nJets), len(nJetsMDeepCSV))
        self.h_HT2MCat.Fill(HT2M ,len(nJets), len(nJetsMDeepCSV))
        self.h_H2MCat.Fill(H2M ,len(nJets), len(nJetsMDeepCSV))
        self.h_HTbCat.Fill(HTb ,len(nJets), len(nJetsMDeepCSV))

        if len(nJetsBSorted) > 3:
            dRbb = deltaR(nJetsBSorted[0], nJetsBSorted[1])
            HTRat = (nJetsBSorted[0].pt + nJetsBSorted[1].pt)/HT
            HTH = HT/H
            self.h_dRbbCat.Fill(dRbb, len(nJets), len(nJetsMDeepCSV))
            self.h_HTRatCat.Fill(HTRat, len(nJets), len(nJetsMDeepCSV))
            self.h_HTHCat.Fill(HTH,len(nJets), len(nJetsMDeepCSV))


        self.h_nLeps.Fill(len(nLeps))

        self.h_nJets_MCSVv2.Fill(len(nJetsMCSVv2))
        self.h_nJets_MDeepCSV.Fill(len(nJetsMDeepCSV))
        self.h_nJets_MDeepJet.Fill(len(nJetsMDeepJet))

        dleps = []
        ileps = []
        for mid in topMus:
            muon = muons[mid]
            dleps.append(muon)
            # self.h_MuPtDz.Fill(muon.pt, muon.dz, len(nJets))
            self.h_MuDzCat.Fill(muon.dz, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            self.h_MuPtCat.Fill(muon.pt, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            self.h_MuKinCat.Fill(muon.eta, muon.phi)
            # self.h_MuIdIso
            # self.h_MuPtIp3d.Fill(muon.pt, muon.ip3d, len(nJets))
        for eid in topEles:
            electron = electrons[eid]
            dleps.append(electron)
            # self.h_ElPtDz.Fill(electron.pt, electron.dz, len(nJets))
            self.h_ElDzCat.Fill(electron.dz, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            self.h_ElPtCat.Fill(electron.pt, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            self.h_ElKinCat.Fill(electron.eta, electron.phi)
            # self.h_ElIdIso
            # self.h_ElPtIp3d.Fill(electron.pt, electron.ip3d, len(nJets))
        dleps.sort(key=lambda lep : lep.pt, reverse=True)
        for i, lep in enumerate(dleps):
            self.h_DirectLepPtCat[i].Fill(lep.pt, len(nJets_oldDeepJet), len(nJetsMDeepJet))

        for mid in tauMus:
            muon = muons[mid]
            ileps.append(muon)
            self.h_TauMuDzCat.Fill(muon.dz, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            self.h_TauMuPtCat.Fill(muon.pt, len(nJets_oldDeepJet), len(nJetsMDeepJet))
        for eid in tauEles:
            electron = electrons[eid]
            ileps.append(electron)
            self.h_TauElDzCat.Fill(electron.dz, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            self.h_TauElPtCat.Fill(electron.pt, len(nJets_oldDeepJet), len(nJetsMDeepJet))
        ileps.sort(key=lambda lep : lep.pt, reverse=True)
        for i, lep in enumerate(ileps):
            self.h_IndirectLepPtCat[i].Fill(lep.pt, len(nJets), len(nJetsMDeepJet))


        ##########################
        ### Write out branches ###
        ##########################
        # if self.out:
        #     self.out.fillBranch("nGenTop", nGenTop)
        #     for name, valType, valTitle in self.varDict:
        #         self.out.fillBranch("GenTop_%s"%(name), theTops[name])


        return True
