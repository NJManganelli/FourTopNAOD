from __future__ import (division, print_function)
import os
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class EventSelector(Module):
    def __init__(self, selectionConfig=None, verbose=False):
        #self.jetSel = jetSelection
        self.writeHistFile=True

        #Choose the channel for selection criteria
        #self.channel = channel
        #Abandoned this in favor of speed for this prototype
        #Better idea may be to separate prototype into ~3 modules (HLT selection/reporting, lepton selection, jet selection/Cleaning)
        #where the first and third can be easily configured with an input channel type
        #but the lepton selection differs enough to make it better to make one version for each channel, possibly. Maybe not

        #load the criteria for brevity
        self.CFG = selectionConfig

        #choose whether we want verbose output
        #No implementation yet
        self.verbose = verbose

        #event counters
        self.counter = 0
        self.MuMuTrig = 0
        self.ElMuTrig = 0
        self.ElElTrig = 0
        self.MuTrig = 0

        #cfg Electron criteria (later: load from configuration dictionary
        self.cfg_eSelPt = 25.0 #min Pt for selection
        #self.cfg_eVetoPt = 20 #"FIXME" not clear what pt requirements are CURRENTLY for all these leptons
        self.cfg_eSelEta = 2.4 #Max Eta acceptance
        self.cfg_eIdType = "cutBased"
        self.cfg_eIdSelCut = 2 #loose
        self.cfg_eIdExtraCut = 1 #veto

        #cfg Muon criteria
        self.cfg_mSelPt = 20 #min Pt for selection
        self.cfg_mSelEta = 2.4 #Max Eta acceptance
        #self.cfg_mIdSel = "mediumId" #would be appropriate for SL, using "tightId"
        #All muons in NanoAOD are loose Muons or better, so loose-only are just those failing the "mediumId"

        #cfg Individual Jet criteria
        self.cfg_jId = 2 #Tight and Tight Lep Veto are the only supported IDs in 2017, corresponding to bits 2 and 3, respectively
        self.cfg_jSelEta = 2.4 #Max Eta acceptance
        self.cfg_jNSelPt = 30.0 #Non-B Jet minimum Pt
        self.cfg_jBSelPt = 25.0 #B Jet minimum Pt
        self.cfg_jBId = "btagCSVV2" #method of bTagging
        self.cfg_jBWP = 0.8838 #Medium CSVv2 working point cut
        self.cfg_jClnTyp = "PartonMatching" #As opposed to "DetlaR"

        #Baseline Event-level criteria
        self.cfg_lowMRes_cent = 10.0 #Low mass resonance veto center
        self.cfg_lowMRes_hwidth = 10.0 #low mass resonance veto half-width
        self.cfg_ZMRes_cent = 91.0 #Z mass resonance veto center
        self.cfg_ZMRes_hwidth = 15 #Z mass resonance veto half-width
        self.cfg_HTMin = 500
        self.cfg_nBJetMin = 2
        self.cfg_nTotJetMin = 4

    def beginJob(self, histFile=None,histDirName=None):
        #if self.writeHistFile=False, called by the postprocessor as beginJob()
        #If self.writeHistFile=True, then called as beginJob(histFile=self.histFile,histDirName=self.histDirName)
        Module.beginJob(self,histFile,histDirName)
        self.h_jet_map = ROOT.TH2F('h_jet_map', ';Jet Eta;Jet Phi', 40, -2.5, 2.5, 20, -3.14, 3.14)
        self.addObject(self.h_jet_map)
        self.h_medCSVV2 = ROOT.TH1D('h_medCSVV2', ';Medium CSVV2 btags; Events', 5, 0, 5)
        self.addObject(self.h_medCSVV2)
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

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        #called by the eventloop at end of inputFile
        #Module just passes
        pass

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        self.counter +=1
        if (self.counter % 10) == 0:
            print("Processed {0:2d} Events".format(self.counter))

        PV = Object(event, "PV")
        otherPV = Collection(event, "OtherPV")
        SV = Collection(event, "SV")

        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        jets = Collection(event, "Jet")
        met = Object(event, "MET")

        HLT = Object(event, "HLT")
        #Filters = Object(event, "Flag") #For Data

        #Trigger selection
        Triggers = { "MuMu" : ["Mu17_TrkIsoVVL_Mu8_TrkIsoVVL"],
                     "ElMu" : ["Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",
                               "Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL"],
                     "ElEl" : ["Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"],
                     "Mu" : ["IsoMu24"]
                     }
        passMuMu = False
        passElMu = False
        passElEl = False
        passMu = False
        for trig in Triggers["MuMu"]:
            #Loop through triggers until one is true, then assign it to passCHANNEL, which will break out next iteration if there is one
            if passMuMu:
                break
            else:
                passMuMu = getattr(HLT, trig)
        for trig in Triggers["ElMu"]:
            if passElMu:
                break
            else:
                passMuMu = getattr(HLT, trig)
        for trig in Triggers["ElEl"]:
            if passElEl:
                break
            else:
                passMuMu = getattr(HLT, trig)
        for trig in Triggers["Mu"]:
            if passMu:
                break
            else:
                passMuMu = getattr(HLT, trig)

        if passMuMu:
            self.MuMuTrig += 1
        if passElMu:
            self.ElMuTrig += 1
        if passElEl:
            self.ElElTrig += 1
        if passMu:
            self.MuTrig += 1

        #Early cut
#        if not (passMu or passMuMu or passElMu or passElEl):
#            return False

        eventSum = ROOT.TLorentzVector()
        
        nSelMuons = 0
        nSelElectrons = 0
        nSelLeptons = 0
        nExtraLeptons = 0
        lepType = []
        lepIndex = []
        lepCharge = []
        crosslinkJetIdx = []
        
        for mInd, muon in enumerate(muons):
            #above min-pt requirement
            if muon.pt < self.cfg_mSelPt:
                continue
            #In eta acceptance
            if abs(muon.eta) > self.cfg_mSelEta:
                continue
            #Below not necessary, since selecting looseID, which is all muons in the collection
            #if getattr(muon, self.cfg_mIdSel): 
            #Isolated muons
            if muon.pfRelIso04_all < 0.15:
                #Count muon and lepton
                nSelMuons += 1
                nSelLeptons += 1
                #Add lepton type, location, and charge to lists
                lepType.append("Muon")
                lepIndex.append(mInd)
                lepCharge.append(muon.charge)
                #Store the cross-link Id of any matching jet in a list for cross-cleaning later
                crosslinkJetIdx.append(muon.jetIdx)
            
        for eInd, ele in enumerate(electrons):
            if ele.pt < self.cfg_eSelPt:
                continue
            if abs(ele.eta) > self.cfg_eSelEta:
                continue
            if getattr(ele, self.cfg_eIdType) == self.cfg_eIdSelCut:
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
            return False
        if nSelLeptons != 2:
            if self.verbose: print("[{0:d}]".format(nSelLeptons))
            return False

        #Opposite-sign charges
        if (lepCharge[0]*lepCharge[1] > 0):
            if self.verbose: print("3")
            return False

        #Same-flavor low mass and Z mass resonance veto
        if nSelMuons == 2:
            diLepMass = (muons[lepIndex[0]].p4() + muons[lepIndex[1]].p4()).M()
            if abs(diLepMass - self.cfg_lowMRes_cent) < self.cfg_lowMRes_hwidth:
                if self.verbose: print("4")
                return False
            if abs(diLepMass - self.cfg_ZMRes_cent) < self.cfg_ZMRes_hwidth:
                if self.verbose: print("5")
                return False
        if nSelElectrons == 2:
            diLepMass = (electrons[lepIndex[0]].p4() + electrons[lepIndex[1]].p4()).M()
            if abs(diLepMass - self.cfg_lowMRes_cent) < self.cfg_lowMRes_hwidth:
                if self.verbose: print("4")
                return False
            if abs(diLepMass - self.cfg_ZMRes_cent) < self.cfg_ZMRes_hwidth:
                if self.verbose: print("5")
                return False


#        for j in filter(self.jetSel,jets):
        nBJets = 0
        nClnBJets = 0
        nOthJets = 0
        nClnOthJets = 0
        HT = 0.0
        HT2M = 0.0
        H = 0.0
        for jInd, jet in enumerate(jets):
            #Skip any jets that are below the threshold chosen (pass Loose: +1, pass Tight: +2 , pass TightLepVeto: +4
            #In 2017 data, pass Loose is always a fail (doesn't exist), so pass Tight and not TLV = 2, pass both = 6
            if jet.jetId < self.cfg_jId:
                continue
            #Eta acceptance
            if abs(jet.eta) > self.cfg_jSelEta:
                continue
            #https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
            ##if jet.ChosenBTag > ChosenBtagWorkingPoint's Threshold and jet.pt > BTaggedJet's minimum cut
            if getattr(jet, self.cfg_jBId) > self.cfg_jBWP and jet.pt > self.cfg_jBSelPt:
                nBJets += 1
                if self.cfg_jClnTyp == "PartonMatching":
                    if jInd not in crosslinkJetIdx:
                        nClnBJets += 1
                        HT += jet.pt
                        #Add BJets to collection here
                        #Add momentum to HT2M, HT, H here
                if self.cfg_jClnTyp == "DeltaR":
                    raise NotImplementedError("In eventselector class, in jet loop, selected cleaning type of DeltaR matching has not been implemented")
                    #if DeltaR(jet, lepton) < 0.4
                        #Need to import from the tools.py the DeltaR function to test between jets and leptons
                        #Add BJets to collection here
                        #Add momentum to HT2M, HT, H here
            elif jet.pt > self.cfg_jNSelPt:
                nOthJets +=1
                HT += jet.pt
                #Add non-B jets to collection here

        #Cut events that don't have minimum number of b-tagged jets
        if nBJets < self.cfg_nBJetMin:
            if self.verbose: print("6")
            return False
        #Cut events that don't have minimum number of selected, cross-cleaned jets
        if nBJets + nOthJets < self.cfg_nTotJetMin:
            if self.verbose: print("7")
            return False
        #Cut events that don't have minimum value of HT #BUT was calculating HT only from selected jets right? cross-checking needed
        if HT < self.cfg_HTMin:
            if self.verbose: print("8")
            return False

        #The event made it! Pass to next module/write out of PostProcessor
        return True
        #self.out.fillBranch("EventMass",eventSum.M())

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

#exampleModuleConstr = lambda : exampleProducer(jetSelection= lambda j : j.pt > 30) 
#DileptonEventSelector = lambda : EventSelector(channel="DL")
#SingleLepEventSelector = lambda : EventSelector(channel="SL")
defaultEventSelector = lambda : EventSelector(selectionConfig=None, verbose=False)
loudEventSelector = lambda : EventSelector(selectionConfig=None, verbose=True)
