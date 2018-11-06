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
    def __init__(self, title=None, typeAK4=None, typeAK8=None, typeElectron=None, typeMuon=None, typeMET=None, typeTrigger=None, doOSDL=False, doTopologyVariables=False):
        #To Do: navigate to folder named after the title, also storing old directory first, then navigating back at the end of the file. Will this work? 
        #Otherwise, give this as pre-title to every single histogram.... maybe equally valid
        #self.jetSel = jetSelection
        self.writeHistFile=True

        self._title = title
        self._dirName = "PlotDQM_" + self._title

        #Collection handles and options
        self._typeAK4 = typeAK4
        self._typeAK8 = typeAK8
        self._typeElectron = typeElectron
        self._typeMuon = typeMuon
        self._doOSDL = doOSDL
        self._doTopologyVariables = doTopologyVariables

        #collection flags, to safely handle bad collection names
        self._flagAK4 = False
        self._flagAK8 = False
        self._flagElectron = False
        self._flagMuon = False
        self._flagDiLep = False

        #event counters
        self.counter = 0
        self.maxEventsToProcess = -1

        #Trigger counters
        # self.MuMuTrig = 0
        # self.ElMuTrig = 0
        # self.ElElTrig = 0
        # self.MuTrig = 0

    def beginJob(self, histFile=None,histDirName=None):
        #if self.writeHistFile=False, called by the postprocessor as beginJob()
        #If self.writeHistFile=True, then called as beginJob(histFile=self.histFile,histDirName=self.histDirName)
        Module.beginJob(self,histFile,histDirName)
        if self._typeAK4:
            self.h_ak4_map = ROOT.TH2F('h_' + self._typeAK4 + '_map', ';Jet Eta;Jet Phi', 40, -2.5, 2.5, 20, -3.14, 3.14)
            self.addObject(self.h_ak4_map)
            self.h_ak4_pt = ROOT.TH1F('h_' + self._typeAK4 + '_pt', ';Jet Pt; Events', 20, 20, 420)
            self.addObject(self.h_ak4_pt)
            self.h_ak4_eta = ROOT.TH1F('h_' + self._typeAK4 + '_eta', ';Jet Eta; Events', 64, -2.8, 2.8)
            self.addObject(self.h_ak4_eta)
            self.h_ak4_phi = ROOT.TH1F('h_' + self._typeAK4 + '_phi', ';Jet Phi; Events', 64, -3.14159265, 3.14159265)
            self.addObject(self.h_ak4_phi)
            self.h_ak4_jetId = ROOT.TH1D('h_' + self._typeAK4 + '_jetId', ';Jet ID; Events', 8, 0, 7)
            self.addObject(self.h_ak4_jetId)
            self.h_ak4_csvv2 = ROOT.TH1F('h_' + self._typeAK4 + '_csvv2', ';btag CSVv2; Events', 100, -0.1, 1.0)
            self.addObject(self.h_ak4_csvv2)
            self.h_ak4_deepcsv = ROOT.TH1F('h_' + self._typeAK4 + '_deepcsv', ';btag DeepB; Events', 100, -0.1, 1.0)
            self.addObject(self.h_ak4_deepcsv)
            self.h_ak4_deepflav = ROOT.TH1F('h_' + self._typeAK4 + '_deepflav', ';btag DeepFlavB; Events', 100, -0.1, 1.0)
            self.addObject(self.h_ak4_deepflav)
        if self._typeMuon:
            self.h_mu_Id = ROOT.TH1F('h_' + self._typeMuon + '_muonId', ';Muon ID; Events', 3, 1, 3)
            self.addObject(self.h_mu_Id)
            self.h_mu_reliso = ROOT.TH1F('h_' + self._typeMuon + '_reliso', ';PF Relative Isolation; Events', 100, 0.0, 1.0)
            self.addObject(self.h_mu_reliso)
        if self._doOSDL:
            self.h_osdl_minv = ROOT.TH1F('h_osdl_minv', ';Invariant Mass; Events', 100, 0., 200.)
            self.addObject(self.h_osdl_minv)
#    def endJob(self):
#       Module.endJob()
        #called once output has been written
        #Cannot override and use pass here if objects need to be written to a histFile
        #pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        prevdir = ROOT.gDirectory
        self.histFile = histFile
        self.histFile.cd()
        self.dir = self.histFile.mkdir( self._dirName )
        prevdir.cd()

        _brlist = inputTree.GetListOfBranches()
        branches = [_brlist.At(i) for i in xrange(_brlist.GetEntries())]
        self.brlist_sep = [self.filterBranchNames(branches,x) for x in self.input]
        self.brlist_all = set(itertools.chain(*(self.brlist_sep)))

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        prevdir = ROOT.gDirectory
        outputFile.cd()
        self.dirName.cd()
        #self.dir.cd() #Would this also work?
        #self.h_nevents.Write()
        prevdir.cd()

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #Increment counter and skip events past the maxEventsToProcess, if larger than -1
        self.counter +=1
        if -1 < self.maxEventsToProcess < self.counter:
            return False

        if self.counter == 1:
            if hasattr(event, self._typeElectron):
                electrons = Collection(event, self._typeElectron)
                self._flagElectron = True
                if self._doOSDL: self._flagOSDL = True
            else:
                print("Collection {0:s} is not available, histograms will not be filled".format(self._typeElectron))
            if hasattr(event, self._typeMuon):
                muons = Collection(event, self._typeMuon)
                self._flagMuon = True
                if self._doOSDL: self._flagOSDL = True
            else:
                print("Collection {0:s} is not available, histograms will not be filled".format(self._typeMuon))
            if hasattr(event, self._typeAK4):
                jets = Collection(event, self._typeAK4)
                self._flagAK4 = True
            else:
                print("Collection {0:s} is not available, histograms will not be filled".format(self._typeAK4))
            if hasattr(event, self._typeAK8):
                fatjets = Collection(event, self._typeAK8)
                self._flagAK8 = True
            else:
                print("Collection {0:s} is not available, histograms will not be filled".format(self._typeAK8))
            if self._doSODL and not self._flagOSDL:
                self._flagOSDL = False
                print("Request for Opposite-Sign Dilepton Histograms made, but collections {0:s} and {1:s} not present. Will not be filled"
                      .format(self._typeMuon, self._typeElectron))
        else:
            if self._flagElectron:
                electrons = Collection(event, self._typeElectron)
            if self._flagMuon:
                muons = Collection(event, self._typeMuon)
            if self._flagAK4:
                jets = Collection(event, self._typeAK4)
            if self._flagAK8:
                fatjets = Collection(event, self._typeAK8)

        #This doesn't protect against missing variables... should really do hasattr(muon, branch) to make sure, first...
        if electrons:
            for e, electron in enumerate(electrons):
                if self._flagOSDL:
                    for ee, electron2 in enumerate(electrons):
                        #Avoid double counting same-flavor leptons...
                        if ee <= e: continue
                        #calculate invariant mass
                        minv = (electron.p4() + electron2.p4()).M()
                        #fill Histo
                        self.h_osdl_minv.Fill(minv)
        if muons:
            for m, muon in enumerate(muons):
                if muon.tightId: self.h_mu_Id.Fill(2.5)
                elif muon.mediumId: self.h_mu_Id.Fill(1.5)
                else: self.h_mu_Id.Fill(0.5)
                self.h_mu_reliso.Fill(muon.pfRelIso04_all)
                if self._flagOSDL:
                    for mm, muon2 in enumerate(muons):
                        #Avoid double counting same-flavor leptons...
                        if mm <= m: continue
                        #calculate invariant mass
                        minv = (muon.p4() + muon2.p4()).M()
                        #fill Histo
                        self.h_osdl_minv.Fill(minv)
        if jets:
            for jet in jets:
                self.h_ak4_map.Fill(jet.eta, jet.phi)
                self.h_ak4_pt.Fill(jet.pt)
                self.h_ak4_eta.Fill(jet.eta)
                self.h_ak4_phi.Fill(jet.phi)
                self.h_ak4_jetId.Fill(jet.jetId)
                self.h_ak4_csvv2.Fill(jet.btagCSVV2)
                self.h_ak4_deepcsv.Fill(jet.btagDeepB)
                self.h_ak4_deepflav.Fill(jet.btagDeepFlavB)
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

        # for eInd, ele in enumerate(electrons):
        #     if ele.pt < min(self.cfg_eSelPt, self.cfg_eVetoPt):
        #         continue
        #     if abs(ele.eta) > self.cfg_eMaxEta:
        #         continue
        #     if getattr(ele, self.cfg_eIdType) >= self.cfg_eIdSelCut:
        #         #count electron and lepton
        #         nSelElectrons += 1
        #         nSelLeptons += 1
        #         #Add lepton type, location, and charge to lists
        #         lepType.append("Electron")
        #         lepIndex.append(eInd)
        #         lepCharge.append(ele.charge)
        #         #Store the cross-link Id of any matching jet in a list for cross-cleaning later
        #         crosslinkJetIdx.append(ele.jetIdx)
        #     elif getattr(ele, self.cfg_eIdType) == self.cfg_eIdExtraCut:
        #         #count veto-level electrons
        #         nExtraLeptons += 1
        # for jInd, jet in enumerate(jets):
        #     #Skip any jets that are below the threshold chosen (pass Loose: +1, pass Tight: +2 , pass TightLepVeto: +4
        #     #In 2017 data, pass Loose is always a fail (doesn't exist), so pass Tight and not TLV = 2, pass both = 6
        #     if jet.jetId < self.cfg_jId:
        #         continue
        #     #Eta acceptance
        #     if abs(jet.eta) > self.cfg_jMaxEta:
        #         continue
        #     #https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
        #     ##if jet.ChosenBTag > ChosenBtagWorkingPoint's Threshold and jet.pt > BTaggedJet's minimum cut
        #     if getattr(jet, self.cfg_jBAlgo) > self.cfg_jBThresh and jet.pt > self.cfg_jBSelPt:
        #         nBJets += 1
        #         if self.cfg_jClnTyp == "PartonMatching":
        #             if jInd not in crosslinkJetIdx:
        #                 nClnBJets += 1
        #                 if self.makeHistos: self.h_jBSel_map.Fill(jet.eta, jet.phi)
        #                 if self.makeHistos: self.h_jBSel_pt.Fill(jet.pt)
        #                 HT += jet.pt
        #                 H += (jet.p4()).P()
        #                 if nClnBJets > 2:
        #                     HT2M += jet.pt
        #                     H2M += (jet.p4()).P()
        #                 #Add BJets to collection here
        #                 #Add momentum to HT2M, HT, H here
        #         elif self.cfg_jClnTyp == "DeltaR":
        #             raise NotImplementedError("In eventselector class, in jet loop, selected cleaning type of DeltaR matching has not been implemented")
        #             #if DeltaR(jet, lepton) < 0.4
        #                 #Need to import from the tools.py the DeltaR function to test between jets and leptons
        #                 #Add BJets to collection here
        #                 #Add momentum to HT2M, HT, H here
        #         else:
        #             raise RuntimeError("The requested Lepton-Jet cross-cleaning algorithm [{0:s}] is not available."
        #                                "Please use \"PartonMatching\" or \"DeltaR\"".format(self.cfg_jClnTyp))
        #     elif jet.pt > self.cfg_jNSelPt:
        #         nOthJets +=1
        #         if self.makeHistos: self.h_jSel_map.Fill(jet.eta, jet.phi)
        #         if self.makeHistos: self.h_jSel_pt.Fill(jet.pt)
        #         HT += jet.pt
        #         H += (jet.p4()).P()
        #         HT2M += jet.pt
        #         H2M += (jet.p4()).P() 
        #         #Add non-B jets to collection here

        #Calculate HTRat and HTH, since more than 4 jets in the events reaching this point
        #HTH = HT/H
        #HTRat = Pt of two highest pt jets / HT

        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
TestDQM = lambda : PlotDQM(title="Test", typeAK4="Jet", typeAK8="FatJet", typeElectron="Electron", typeMuon="Muon", typeMET="MET", typeTrigger="HLT", doOSDL=True, doTopologyVariables=False)
