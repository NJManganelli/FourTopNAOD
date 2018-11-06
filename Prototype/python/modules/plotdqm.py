from __future__ import (division, print_function)
import os
import ROOT
import itertools
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }

class PlotDQM(Module):
    """This Module takes as input the names of collections of 5 different types (1 collection per type), and makes some basic DQM-style histograms.

A title must be provided using title="Your Custom Title." This title helps differentiate the output of the module as-configured from the same module run at a later point.
The collections should be passed as a string containing the Collection name, to the corresponding Type, which are typeAK4=, typeAK8=, typeElectron=,
typeMuon=, typeTrigger=, and two boolean values, doOSDL= and doTopologyVariables=. The former triggers invariant mass histograms in same-flavor channels,
if they exist; the latter triggers calculation and plotting of the event variables, like H, HT, HTRat, etc."""
    def __init__(self, title=None, typeAK4=None, typeAK8=None, typeElectron=None, typeMuon=None, typeTrigger=None, doOSDL=False, doTopologyVariables=False):
        #To Do: navigate to folder named after the title, also storing old directory first, then navigating back at the end of the file. Will this work? 
        #Otherwise, give this as pre-title to every single histogram.... maybe equally valid
        #self.jetSel = jetSelection
        self.writeHistFile=True

        self._title = title
        self._typeAK4 = typeAK4
        self._typeAK8 = typeAK8
        self._typeElectron = typeElectron
        self._typeMuon = typeMuon
        self._doOSDL = doOSDL

        #event counters
        self.counter = 0
        self.maxEventsToProcess = -1

        #Trigger counters
        self.MuMuTrig = 0
        self.ElMuTrig = 0
        self.ElElTrig = 0
        self.MuTrig = 0

        #Electron CFG loading from config file
        self.cfg_eMaxEta = self.CFG["Electron"]["Common"]["Eta"] #Max Eta acceptance
        self.cfg_eIdType = self.CFG["Electron"]["Common"]["IdType"]
        self.cfg_eSelPt = self.CFG["Electron"]["Select"]["Pt"] #min Pt for selection
        self.cfg_eIdSelCut = self.CFG["Electron"]["Select"]["IdLevel"] #selection level
        self.cfg_eVetoPt = self.CFG["Electron"]["Veto"]["Pt"] #min Pt for veto counting
        self.cfg_eIdExtraCut = self.CFG["Electron"]["Veto"]["IdLevel"] #veto level

        #Muon CFG loading from config file
        self.cfg_mMaxEta = self.CFG["Muon"]["Common"]["Eta"] #Max Eta acceptance
        self.cfg_mSelPt = self.CFG["Muon"]["Select"]["Pt"] #min Pt for selection
        self.cfg_mSelRelIso = self.CFG["Muon"]["Select"]["RelIso"] #Relative Isolation
        self.cfg_mSelId = self.CFG["Muon"]["Select"]["IdLevel"]

        #Jet CFG loading from config file
        self.cfg_jMaxEta = self.CFG["Jet"]["Common"]["Eta"] #Max Eta acceptance
        self.cfg_jId = self.CFG["Jet"]["Common"]["JetId"]
        self.cfg_jNSelPt = self.CFG["Jet"]["NonBJet"]["Pt"] #Non-B Jet minimum Pt
        self.cfg_jBSelPt = self.CFG["Jet"]["BJet"]["Pt"] #B Jet minimum Pt
        self.cfg_jBAlgo = self.CFG["Jet"]["Algo"] #bTagging Algorithm
        self.cfg_jBWP = self.CFG["Jet"]["WP"] #working point, like "Medium" or "Tight"
        self.cfg_jBThresh = self.CFG["Jet"][self.cfg_jBAlgo][self.cfg_jBWP]
        self.cfg_jClnTyp = self.CFG["Jet"]["CleanType"]

        #Event CFG loading from config file
        self.cfg_lowMRes_cent = self.CFG["Event"]["LowMassReson"]["Center"] #Low mass resonance veto center
        self.cfg_lowMRes_hwidth = self.CFG["Event"]["LowMassReson"]["HalfWidth"] #low mass resonance veto half-width
        self.cfg_ZMRes_cent = self.CFG["Event"]["ZMassReson"]["Center"] #Z mass resonance veto center
        self.cfg_ZMRes_hwidth = self.CFG["Event"]["ZMassReson"]["HalfWidth"] #Z mass resonance veto half-width
        self.cfg_HTMin = self.CFG["Event"]["HTMin"] #Minimum HT
        self.cfg_nBJetMin = self.CFG["Event"]["nBJetMin"] #Minimum bTagged jets
        self.cfg_nTotJetMin = self.CFG["Event"]["nTotJetMin"] #Minimum total jets
        self.cfg_minMET = self.CFG["MET"]["MinMET"] #Minimum MET

    def beginJob(self, histFile=None,histDirName=None):
        #if self.writeHistFile=False, called by the postprocessor as beginJob()
        #If self.writeHistFile=True, then called as beginJob(histFile=self.histFile,histDirName=self.histDirName)
        Module.beginJob(self,histFile,histDirName)
        self.h_jSel_map = ROOT.TH2F('h_jSel_map', ';Jet Eta;Jet Phi', 40, -2.5, 2.5, 20, -3.14, 3.14)
        self.addObject(self.h_jSel_map)
        self.h_jSel_pt = ROOT.TH1F('h_jSel_pt', ';Jet Pt; Events', 20, 20, 420)
        self.addObject(self.h_jSel_pt)
        self.h_jBSel_map = ROOT.TH2F('h_jBSel_map', ';Jet Eta;Jet Phi', 40, -2.5, 2.5, 20, -3.14, 3.14)
        self.addObject(self.h_jBSel_map)
        self.h_jBSel_pt = ROOT.TH1F('h_jBSel_pt', ';Jet Pt; Events', 20, 20, 420)
        self.addObject(self.h_jBSel_pt)
        # self.h_medCSVV2 = ROOT.TH1D('h_medCSVV2', ';Medium CSVV2 btags; Events', 5, 0, 5)
        # self.addObject(self.h_medCSVV2)
        if self.makeHistos:
            self.h_cutHisto = ROOT.TH1F('h_cutHisto', ';Pruning Point in Event Selection; Events', 10, 0, 10)
            self.addObject(self.h_cutHisto)
        pass

#    def endJob(self):
#       Module.endJob()
        #called once output has been written
        #Cannot override and use pass here if objects need to be written to a histFile
        #pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
        #called by the eventloop at start of new inputFile
        #Module just passes
        #wrappedOutputTree only exists if noOut=False and events are written!
        # self.out = wrappedOutputTree
        # self.out.branch("EventMass",  "F");
        #FROM collectionMerger.py: 
        _brlist = inputTree.GetListOfBranches()
        branches = [_brlist.At(i) for i in xrange(_brlist.GetEntries())]
        self.brlist_sep = [self.filterBranchNames(branches,x) for x in self.input]
        self.brlist_all = set(itertools.chain(*(self.brlist_sep)))

        self.is_there = np.zeros(shape=(len(self.brlist_all),self.nInputs),dtype=bool)
        for bridx,br in enumerate(self.brlist_all):
            for j in xrange(self.nInputs):
                if br in self.brlist_sep[j]: self.is_there[bridx][j]=True

        self.out = wrappedOutputTree
        for br in self.brlist_all:
            self.out.branch("%s_%s"%(self.output,br), _rootLeafType2rootBranchType[self.branchType[br]], lenVar="n%s"%self.output)


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        #called by the eventloop at end of inputFile
        #Module just passes
        pass

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #Increment counter and skip events past the maxEventsToProcess, if larger than -1
        self.counter +=1
        if -1 < self.maxEventsToProcess < self.counter:
            return False

        if hasattr(event, self._typeElectron):
            electrons = Collection(event, self._typeElectron)
        else:
            print("Collection {0:s} is not available, histograms will not be filled".format(self._typeElectron))
        if hasattr(event, self._typeMuon):
            muons = Collection(event, self._typeMuon)
        else:
            print("Collection {0:s} is not available, histograms will not be filled".format(self._typeMuon))
        if hasattr(event, self._typeAK4):
            jets = Collection(event, self._typeAK4)
        else:
            print("Collection {0:s} is not available, histograms will not be filled".format(self._typeAK4))
        if hasattr(event, self._typeAK8):
            fatjets = Collection(event, self._typeAK8)
        else:
            print("Collection {0:s} is not available, histograms will not be filled".format(self._typeAK8))
        # met = Object(event, "MET")
        # HLT = Object(event, "HLT")
        # Filters = Object(event, "Flag") #For Data
        
        #########################
        ### Trigger Selection ###
        #########################
        # Triggers = { "MuMu" : ["Mu17_TrkIsoVVL_Mu8_TrkIsoVVL"],
        #              "ElMu" : ["Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",
        #                        "Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL"],
        #              "ElEl" : ["Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"],
        #              "Mu" : ["IsoMu24"]
        #              }
        # passMuMu = False
        # passElMu = False
        # passElEl = False
        # passMu = False
        # for trig in Triggers["MuMu"]:
        #     #Loop through triggers until one is true, then assign it to passCHANNEL, which will break out next iteration if there is one
        #     if passMuMu:
        #         break
        #     else:
        #         passMuMu = getattr(HLT, trig)
        # for trig in Triggers["ElMu"]:
        #     if passElMu:
        #         break
        #     else:
        #         passMuMu = getattr(HLT, trig)
        # for trig in Triggers["ElEl"]:
        #     if passElEl:
        #         break
        #     else:
        #         passMuMu = getattr(HLT, trig)
        # for trig in Triggers["Mu"]:
        #     if passMu:
        #         break
        #     else:
        #         passMuMu = getattr(HLT, trig)

        # if passMuMu:
        #     self.MuMuTrig += 1
        # if passElMu:
        #     self.ElMuTrig += 1
        # if passElEl:
        #     self.ElElTrig += 1
        # if passMu:
        #     self.MuTrig += 1
            
        eventSum = ROOT.TLorentzVector()

        #############
        ### MUONS ###
        #############
        for mInd, muon in enumerate(muons):
            #above min-pt requirement
            if muon.pt < self.cfg_mSelPt:
                continue
            #In eta acceptance
            if abs(muon.eta) > self.cfg_mMaxEta:
                continue
            #selection id. Only check if mediumId or tightId, all looseId by default
            if self.cfg_mSelId != "looseId":
                if getattr(muon, self.cfg_mSelId) == False: 
                    continue
            #Isolated muons
            if muon.pfRelIso04_all < self.cfg_mSelRelIso:
                #Count muon and lepton
                nSelMuons += 1
                nSelLeptons += 1
                #Add lepton type, location, and charge to lists
                lepType.append("Muon")
                lepIndex.append(mInd)
                lepCharge.append(muon.charge)
                #Store the cross-link Id of any matching jet in a list for cross-cleaning later
                crosslinkJetIdx.append(muon.jetIdx)
            
        #################
        ### ELECTRONS ###
        #################
        for eInd, ele in enumerate(electrons):
            if ele.pt < min(self.cfg_eSelPt, self.cfg_eVetoPt):
                continue
            if abs(ele.eta) > self.cfg_eMaxEta:
                continue
            if getattr(ele, self.cfg_eIdType) >= self.cfg_eIdSelCut:
                #count electron and lepton
                nSelElectrons += 1
                nSelLeptons += 1
                #Add lepton type, location, and charge to lists
                lepType.append("Electron")
                lepIndex.append(eInd)
                lepCharge.append(ele.charge)
                #Store the cross-link Id of any matching jet in a list for cross-cleaning later
                crosslinkJetIdx.append(ele.jetIdx)
            elif getattr(ele, self.cfg_eIdType) == self.cfg_eIdExtraCut:
                #count veto-level electrons
                nExtraLeptons += 1

        #Dilepton event selection cuts
        if nExtraLeptons > 0:
            if self.verbose: print("1")
            if self.makeHistos: self.h_cutHisto.Fill(1.5)
            return False
        if nSelLeptons != 2:
            if self.verbose: print("[{0:d}]".format(nSelLeptons))
            if self.makeHistos: self.h_cutHisto.Fill(2.5)
            return False

        #Opposite-sign charges
        if (lepCharge[0]*lepCharge[1] > 0):
            if self.verbose: print("3")
            if self.makeHistos: self.h_cutHisto.Fill(3.5)
            return False

        #Same-flavor low mass and Z mass resonance veto
        if nSelMuons == 2:
            diLepMass = (muons[lepIndex[0]].p4() + muons[lepIndex[1]].p4()).M()
            if abs(diLepMass - self.cfg_lowMRes_cent) < self.cfg_lowMRes_hwidth:
                if self.verbose: print("4")
                if self.makeHistos: self.h_cutHisto.Fill(4.5)
                return False
            if abs(diLepMass - self.cfg_ZMRes_cent) < self.cfg_ZMRes_hwidth:
                if self.verbose: print("5")
                if self.makeHistos: self.h_cutHisto.Fill(5.5)
                return False
        if nSelElectrons == 2:
            diLepMass = (electrons[lepIndex[0]].p4() + electrons[lepIndex[1]].p4()).M()
            if abs(diLepMass - self.cfg_lowMRes_cent) < self.cfg_lowMRes_hwidth:
                if self.verbose: print("4")
                if self.makeHistos: self.h_cutHisto.Fill(4.5)
                return False
            if abs(diLepMass - self.cfg_ZMRes_cent) < self.cfg_ZMRes_hwidth:
                if self.verbose: print("5")
                if self.makeHistos: self.h_cutHisto.Fill(5.5)
                return False


#        for j in filter(self.jetSel,jets):
        nBJets = 0
        nClnBJets = 0
        nOthJets = 0
        nClnOthJets = 0
        HT = 0.0
        H = 0.0
        HT2M = 0.0
        H2M = 0.0
        HTRat = 0.0
        HTH = 0.0

        
        for jInd, jet in enumerate(jets):
            #Skip any jets that are below the threshold chosen (pass Loose: +1, pass Tight: +2 , pass TightLepVeto: +4
            #In 2017 data, pass Loose is always a fail (doesn't exist), so pass Tight and not TLV = 2, pass both = 6
            if jet.jetId < self.cfg_jId:
                continue
            #Eta acceptance
            if abs(jet.eta) > self.cfg_jMaxEta:
                continue
            #https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
            ##if jet.ChosenBTag > ChosenBtagWorkingPoint's Threshold and jet.pt > BTaggedJet's minimum cut
            if getattr(jet, self.cfg_jBAlgo) > self.cfg_jBThresh and jet.pt > self.cfg_jBSelPt:
                nBJets += 1
                if self.cfg_jClnTyp == "PartonMatching":
                    if jInd not in crosslinkJetIdx:
                        nClnBJets += 1
                        if self.makeHistos: self.h_jBSel_map.Fill(jet.eta, jet.phi)
                        if self.makeHistos: self.h_jBSel_pt.Fill(jet.pt)
                        HT += jet.pt
                        H += (jet.p4()).P()
                        if nClnBJets > 2:
                            HT2M += jet.pt
                            H2M += (jet.p4()).P()
                        #Add BJets to collection here
                        #Add momentum to HT2M, HT, H here
                elif self.cfg_jClnTyp == "DeltaR":
                    raise NotImplementedError("In eventselector class, in jet loop, selected cleaning type of DeltaR matching has not been implemented")
                    #if DeltaR(jet, lepton) < 0.4
                        #Need to import from the tools.py the DeltaR function to test between jets and leptons
                        #Add BJets to collection here
                        #Add momentum to HT2M, HT, H here
                else:
                    raise RuntimeError("The requested Lepton-Jet cross-cleaning algorithm [{0:s}] is not available."
                                       "Please use \"PartonMatching\" or \"DeltaR\"".format(self.cfg_jClnTyp))
            elif jet.pt > self.cfg_jNSelPt:
                nOthJets +=1
                if self.makeHistos: self.h_jSel_map.Fill(jet.eta, jet.phi)
                if self.makeHistos: self.h_jSel_pt.Fill(jet.pt)
                HT += jet.pt
                H += (jet.p4()).P()
                HT2M += jet.pt
                H2M += (jet.p4()).P() 
                #Add non-B jets to collection here

        #Cut events that don't have minimum number of b-tagged jets
        if nBJets < self.cfg_nBJetMin:
            if self.verbose: print("6")
            if self.makeHistos: self.h_cutHisto.Fill(6.5)
            return False
        #Cut events that don't have minimum number of selected, cross-cleaned jets
        if nBJets + nOthJets < self.cfg_nTotJetMin:
            if self.verbose: print("7")
            if self.makeHistos: self.h_cutHisto.Fill(7.5)
            return False
        #Cut events that don't have minimum value of HT #BUT was calculating HT only from selected jets right? cross-checking needed
        if HT < self.cfg_HTMin:
            if self.verbose: print("8")
            if self.makeHistos: self.h_cutHisto.Fill(8.5)
            if self.cutOnHT: return False

        #Calculate HTRat and HTH, since more than 4 jets in the events reaching this point
        HTH = HT/H
        #HTRat = Pt of two highest pt jets / HT

        #The event made it! Pass to next module/write out of PostProcessor
        return True
        #self.out.fillBranch("EventMass",eventSum.M())

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

#exampleModuleConstr = lambda : exampleProducer(jetSelection= lambda j : j.pt > 30) 
defaultEventSelector = lambda : EventSelector()
loudEventSelector = lambda : EventSelector(verbose=True)
showyEventSelector = lambda : EventSelector(makeHistos=True)


