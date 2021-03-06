from __future__ import (division, print_function)
import os
import ROOT
import numpy as np
import itertools
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #deltaR, deltaPhi, etc.

#ProtoEventSelector is broken, lacking a deltaR implementation, and failing to correctly clean non-b jets. Do not use. Left for reference (currently)
class ProtoEventSelector(Module):
    def __init__(self, selectionConfig=None, verbose=False, makeHistos=False, cutOnMET=True, cutOnTrigs=True, cutOnHT=True):
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

        #choose whether we want verbose output or to produce cut histograms 
        self._verbose = verbose
        self.makeHistos = makeHistos
        self.cutOnMET = cutOnMET
        self.cutOnTrigs = cutOnTrigs
        self.cutOnHT = cutOnHT

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
        #All muons in NanoAOD are loose Muons or better, so loose-only are just those failing the "mediumId"

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
        if (self.counter % 1000) == 0:
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
        
        #########################
        ### Trigger Selection ###
        #########################
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
            
        ##########################
        ### Early Cut on Trigs ###
        ##########################
        if not (passMu or passMuMu or passElMu or passElEl):
            if self.makeHistos: self.h_cutHisto.Fill(0.5)
            if self.cutOnTrigs: return False

        ###########
        ### MET ###
        ###########
        if self.cutOnMET and met.pt < self.cfg_minMET: return False

        eventSum = ROOT.TLorentzVector()
        
        nSelMuons = 0
        nSelElectrons = 0
        nSelLeptons = 0
        nExtraLeptons = 0
        lepType = []
        lepIndex = []
        lepCharge = []
        crosslinkJetIdx = []
        

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
            if getattr(ele, self.cfg_eIdType) >= self.cfg_eIdSelCut and ele.pt > self.cfg_eSelPt:
                #count electron and lepton
                nSelElectrons += 1
                nSelLeptons += 1
                #Add lepton type, location, and charge to lists
                lepType.append("Electron")
                lepIndex.append(eInd)
                lepCharge.append(ele.charge)
                #Store the cross-link Id of any matching jet in a list for cross-cleaning later
                crosslinkJetIdx.append(ele.jetIdx)
            elif getattr(ele, self.cfg_eIdType) == self.cfg_eIdExtraCut and ele.pt > self.cfg_eVetoPt:
                #count veto-level electrons
                nExtraLeptons += 1

        #Dilepton event selection cuts
        if nExtraLeptons > 0:
            if self._verbose: print("1")
            if self.makeHistos: self.h_cutHisto.Fill(1.5)
            return False
        if nSelLeptons != 2:
            if self._verbose: print("[{0:d}]".format(nSelLeptons))
            if self.makeHistos: self.h_cutHisto.Fill(2.5)
            return False

        #Opposite-sign charges
        if (lepCharge[0]*lepCharge[1] > 0):
            if self._verbose: print("3")
            if self.makeHistos: self.h_cutHisto.Fill(3.5)
            return False

        #Same-flavor low mass and Z mass resonance veto
        if nSelMuons == 2:
            diLepMass = (muons[lepIndex[0]].p4() + muons[lepIndex[1]].p4()).M()
            if abs(diLepMass - self.cfg_lowMRes_cent) < self.cfg_lowMRes_hwidth:
                if self._verbose: print("4")
                if self.makeHistos: self.h_cutHisto.Fill(4.5)
                return False
            if abs(diLepMass - self.cfg_ZMRes_cent) < self.cfg_ZMRes_hwidth:
                if self._verbose: print("5")
                if self.makeHistos: self.h_cutHisto.Fill(5.5)
                return False
        if nSelElectrons == 2:
            diLepMass = (electrons[lepIndex[0]].p4() + electrons[lepIndex[1]].p4()).M()
            if abs(diLepMass - self.cfg_lowMRes_cent) < self.cfg_lowMRes_hwidth:
                if self._verbose: print("4")
                if self.makeHistos: self.h_cutHisto.Fill(4.5)
                return False
            if abs(diLepMass - self.cfg_ZMRes_cent) < self.cfg_ZMRes_hwidth:
                if self._verbose: print("5")
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
            if self._verbose: print("6")
            if self.makeHistos: self.h_cutHisto.Fill(6.5)
            return False
        #Cut events that don't have minimum number of selected, cross-cleaned jets
        if nBJets + nOthJets < self.cfg_nTotJetMin:
            if self._verbose: print("7")
            if self.makeHistos: self.h_cutHisto.Fill(7.5)
            return False
        #Cut events that don't have minimum value of HT #BUT was calculating HT only from selected jets right? cross-checking needed
        if HT < self.cfg_HTMin:
            if self._verbose: print("8")
            if self.makeHistos: self.h_cutHisto.Fill(8.5)
            if self.cutOnHT: return False

        #Calculate HTRat and HTH, since more than 4 jets in the events reaching this point
        HTH = HT/H
        #HTRat = Pt of two highest pt jets / HT

        #The event made it! Pass to next module/write out of PostProcessor
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

#exampleModuleConstr = lambda : exampleProducer(jetSelection= lambda j : j.pt > 30) 
defaultEventSelector = lambda : ProtoEventSelector()
loudEventSelector = lambda : ProtoEventSelector(verbose=True)
showyEventSelector = lambda : ProtoEventSelector(makeHistos=True)

#Add new collections for selected items following https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/common/collectionMerger.py
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }
class EventSelector(Module):
    def __init__(self, selectionConfig=None, verbose=False, makeHistos=False, cutOnMET=True, cutOnTrigs=True, cutOnHT=True, isLastModule=True):
        #Adapt collectionMerger.py for adding new branches for selected leptons, jets...
        ########################
        #Input branches for leptons and Jets. Position one must correspond to incoming electrons, two to incoming muons, and three to AK4 jets
        self.input = { "typeElectron" : "Electron",
                       "typeMuon" : "Muon",
                       "typeAK4" : "Jet"
                       }
        #Output branches. One = electrons, Two = Muons, Three = b Jets, Four = Non-b Jets
        self.output = { "typeElectron" : "SelectedElectron",
                        "typeMuon" : "SelectedMuon",
                        "typeAK4Heavy" : "SelectedHeavyJet",
                        "typeAK4Light" : "SelectedLightJet"
                        }
        #Create dictionary of empty dictionaries which will map each output collection's branches to a branchtype
        self.nInputs = len(self.input)
        placeholder = []
        for elem in self.output:
            placeholder.append({})
        self.branchType = dict(zip(self.input.values(), placeholder))
        ########################

        #self.jetSel = jetSelection
        self.writeHistFile=True

        #load the criteria for brevity
        self.CFG = selectionConfig

        #choose whether we want verbose output or to produce cut histograms 
        self._verbose = verbose
        self.makeHistos = makeHistos
        self.cutOnMET = cutOnMET
        self.cutOnTrigs = cutOnTrigs
        self.cutOnHT = cutOnHT
        self._isLastModule = isLastModule

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
        #All muons in NanoAOD are loose Muons or better, so loose-only are just those failing the "mediumId"

        #Jet CFG loading from config file
        self.cfg_jMaxEta = self.CFG["Jet"]["Common"]["Eta"] #Max Eta acceptance
        self.cfg_jId = self.CFG["Jet"]["Common"]["JetId"]
        self.cfg_jNSelPt = self.CFG["Jet"]["NonBJet"]["Pt"] #Non-B Jet minimum Pt
        self.cfg_jBSelPt = self.CFG["Jet"]["BJet"]["Pt"] #B Jet minimum Pt
        self.cfg_jBAlgo = self.CFG["Jet"]["Algo"] #bTagging Algorithm
        self.cfg_jBWP = self.CFG["Jet"]["WP"] #working point, like "Medium" or "Tight"
        self.cfg_jBThresh = self.CFG["Jet"][self.cfg_jBAlgo][self.cfg_jBWP]
        self.cfg_jClnTyp = self.CFG["Jet"]["CleanType"]
        self.cfg_jMaxdR = self.CFG["Jet"]["MaxDeltaR"]

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
        if self.makeHistos:
            self.h_cutHisto = ROOT.TH1F('h_cutHisto', ';Pruning Point in Event Selection; Events', 10, 0, 10)
            self.addObject(self.h_cutHisto)
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
        pass

#    def endJob(self):
#       Module.endJob()
        #called once output has been written
        #Cannot override and use pass here if objects need to be written to a histFile
        #pass

    def endJob(self):
        if hasattr(self, 'objs') and self.objs != None:
            prevdir = ROOT.gDirectory
            if self._verbose:
                print("EventSelector is switching from directory {0:s} to directory {1:s}".format(prevdir, self.dir))
            self.dir.cd()
            if self._verbose:
                print("EventSelector is writing objects inside the directory.")
            for obj in self.objs:
                obj.Write()
            if self._verbose:
                print("Returning to previous directory...")
            prevdir.cd()
            if self._isLastModule and hasattr(self, 'histFile') and self.histFile != None :
                if self._verbose:
                    print("EventSelector was passed the option isLastModule=True. It is closing the file at endJob().")
                self.histFile.Close()

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        _brlist = inputTree.GetListOfBranches()
        branches = [_brlist.At(i) for i in xrange(_brlist.GetEntries())]
        #Create dictionary of empty dictionaries which will map each output collection's branches to a branchtype
        #self.branchType = dict(zip(self.input, placeholder))
        placeholder = []
        for elem in self.input:
            placeholder.append([])
        self.brlist_sep = dict(zip(self.input.keys(), placeholder))

        for key in self.input.keys():
            self.brlist_sep[key] = self.filterBranchNames(branches,self.input[key])
        #self.brlist_all = set(itertools.chain(*(self.brlist_sep)))
        # for bridx,br in enumerate(self.brlist_all):
        #     for j in xrange(self.nInputs):
        #         if br in self.brlist_sep[j]: self.is_there[bridx][j]=True

        self.out = wrappedOutputTree
        #want multipe sets of output branche collections for the different categories.... not one single branch collection
        #Create output branches for the selected electrons, muons, and distinct b Jet/Non-b Jet collections
        for ebr in self.brlist_sep["typeElectron"]:
            self.out.branch("%s_%s"%(self.output["typeElectron"], ebr), 
                            _rootLeafType2rootBranchType[self.branchType[self.input["typeElectron"]][ebr]], lenVar="n%s"%self.output["typeElectron"])
        for mbr in self.brlist_sep["typeMuon"]:
            self.out.branch("%s_%s"%(self.output["typeMuon"], mbr), 
                            _rootLeafType2rootBranchType[self.branchType[self.input["typeMuon"]][mbr]], lenVar="n%s"%self.output["typeMuon"])
        for jbr in self.brlist_sep["typeAK4"]:
            self.out.branch("%s_%s"%(self.output["typeAK4Heavy"], jbr), 
                            _rootLeafType2rootBranchType[self.branchType[self.input["typeAK4"]][jbr]], lenVar="n%s"%self.output["typeAK4Heavy"])
            self.out.branch("%s_%s"%(self.output["typeAK4Light"], jbr), 
                            _rootLeafType2rootBranchType[self.branchType[self.input["typeAK4"]][jbr]], lenVar="n%s"%self.output["typeAK4Light"])

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        #called by the eventloop at end of inputFile
        #Module just passes
        pass

    #Use method from CollectionMerger.py
    def filterBranchNames(self,branches,collection):
        out = []
        for br in branches:
            name = br.GetName()
            if not name.startswith(collection+'_'): continue
            out.append(name.replace(collection+'_',''))
            self.branchType[collection][out[-1]] = br.FindLeaf(br.GetName()).GetTypeName() #Need to fix this type part for multi collections...
        return out

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #Increment counter and skip events past the maxEventsToProcess, if larger than -1
        self.counter +=1
        if -1 < self.maxEventsToProcess < self.counter:
            return False
        if (self.counter % 1000) == 0:
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
        
        #########################
        ### Trigger Selection ###
        #########################
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
            
        ##########################
        ### Early Cut on Trigs ###
        ##########################
        if not (passMu or passMuMu or passElMu or passElEl):
            if self.makeHistos: self.h_cutHisto.Fill(0.5)
            if self.cutOnTrigs: return False

        ###########
        ### MET ###
        ###########
        if self.cutOnMET and met.pt < self.cfg_minMET: return False

        eventSum = ROOT.TLorentzVector()
        
        nSelMuons = 0 #used for cuts and invariant mass vetos
        nSelElectrons = 0 #used for cuts and invariant mass vetos
        nSelLeptons = 0 #used for cuts
        nExtraLeptons = 0 #used for cuts
        lepType = [] #intended for small-data forwarding of event selection (only store indices/type of selected leptons to next module)
        lepIndex = [] #Used for invariant mass veto, can be replaced with mIndex and eIndex now that they have been added for collection creation
        mIndex = [] #For making clean muon collection
        eIndex = [] #For making clean electron collection
        jBIndex = [] #For making clean b jet collection
        jNBIndex = [] #For making clean non-b jet collection
        lepCharge = [] 
        crosslinkJetIdx = [] #for cleaning jets with PartonMatching algorithm
        

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
            #selection id. Only check if mediumId or tightId, all looseId by default...
            if self.cfg_mSelId != "looseId":
                if getattr(muon, self.cfg_mSelId) == False: 
                    continue
            #Isolated muons
            if muon.pfRelIso04_all < self.cfg_mSelRelIso:
                #Count muon and lepton
                nSelMuons += 1
                nSelLeptons += 1
                #Add lepton type, location index, and charge to lists
                lepType.append("Muon")
                mIndex.append(mInd)
                lepIndex.append(mInd)
                lepCharge.append(muon.charge)
                #Store the cross-link Id of any matching jet in a list for cross-cleaning later
                crosslinkJetIdx.append(muon.jetIdx)
            
        #################
        ### ELECTRONS ###
        #################
        for eInd, ele in enumerate(electrons):
            #Early pt cut
            if ele.pt < min(self.cfg_eSelPt, self.cfg_eVetoPt):
                continue
            if abs(ele.eta) > self.cfg_eMaxEta:
                continue
            if getattr(ele, self.cfg_eIdType) >= self.cfg_eIdSelCut and ele.pt > self.cfg_eSelPt:
                #count electron and lepton
                nSelElectrons += 1
                nSelLeptons += 1
                #Add lepton type, location, and charge to lists
                lepType.append("Electron")
                eIndex.append(eInd)
                lepIndex.append(eInd)
                lepCharge.append(ele.charge)
                #Store the cross-link Id of any matching jet in a list for cross-cleaning later
                crosslinkJetIdx.append(ele.jetIdx)
            elif getattr(ele, self.cfg_eIdType) == self.cfg_eIdExtraCut and ele.pt > self.cfg_eVetoPt:
                #count veto-level electrons
                nExtraLeptons += 1

        #Dilepton event selection cuts
        if nExtraLeptons > 0:
            if self.makeHistos: self.h_cutHisto.Fill(1.5)
            return False
        #print("n: " + str(nSelLeptons) + " ")
        if nSelLeptons != 2:
            if self.makeHistos: self.h_cutHisto.Fill(2.5)
            return False

        #print(lepCharge)
        #Opposite-sign charges
        #Get almost exactly 1/3 events failing opposite-sign , if they pass dilepton veto, which is appropriate for 4-top production.
        if (lepCharge[0]*lepCharge[1] > 0):
            #print("<-Failed")
            if self.makeHistos: self.h_cutHisto.Fill(3.5)
            return False

        #Same-flavor low mass and Z mass resonance veto ###Improvement: now have separate index lists for muons, electrons, just use those for counting and matching
        if nSelMuons == 2:
            diLepMass = (muons[lepIndex[0]].p4() + muons[lepIndex[1]].p4()).M()
            if abs(diLepMass - self.cfg_lowMRes_cent) < self.cfg_lowMRes_hwidth:
                if self.makeHistos: self.h_cutHisto.Fill(4.5)
                return False
            if abs(diLepMass - self.cfg_ZMRes_cent) < self.cfg_ZMRes_hwidth:
                if self.makeHistos: self.h_cutHisto.Fill(5.5)
                return False
        if nSelElectrons == 2:
            diLepMass = (electrons[lepIndex[0]].p4() + electrons[lepIndex[1]].p4()).M()
            if abs(diLepMass - self.cfg_lowMRes_cent) < self.cfg_lowMRes_hwidth:
                if self.makeHistos: self.h_cutHisto.Fill(4.5)
                return False
            if abs(diLepMass - self.cfg_ZMRes_cent) < self.cfg_ZMRes_hwidth:
                if self.makeHistos: self.h_cutHisto.Fill(5.5)
                return False


#        for j in filter(self.jetSel,jets):
        nBJets = 0
        #nClnBJets = 0
        nOthJets = 0
        #nClnOthJets = 0
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
            if self.cfg_jClnTyp == "PartonMatching":
                if jInd in crosslinkJetIdx:
                    continue
            elif self.cfg_jClnTyp == "DeltaR":
                #raise NotImplementedError("In eventselector class, in jet loop, selected cleaning type of DeltaR matching has not been implemented")
                failCleaning = False
                for mIdx in mIndex:
                    if deltaR(muons[mIdx], jet) < self.cfg_jMaxdR:
                        failCleaning = True
                for eIdx in eIndex:
                    if deltaR(electrons[eIdx], jet) < self.cfg_jMaxdR:
                        failCleaning = True
                if failCleaning:
                    continue
            else:
                raise RuntimeError("The requested Lepton-Jet cross-cleaning algorithm [{0:s}] is not available."
                                   "Please use \"PartonMatching\" or \"DeltaR\"".format(self.cfg_jClnTyp))
            #https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
            ##if jet.ChosenBTag > ChosenBtagWorkingPoint's Threshold and jet.pt > BTaggedJet's minimum cut
            if getattr(jet, self.cfg_jBAlgo) > self.cfg_jBThresh and jet.pt > self.cfg_jBSelPt:
                nBJets += 1
                #nClnBJets += 1
                if self.makeHistos: self.h_jBSel_map.Fill(jet.eta, jet.phi)
                if self.makeHistos: self.h_jBSel_pt.Fill(jet.pt)
                #Add jet index to list for collection filling
                jBIndex.append(jInd) 
                HT += jet.pt
                H += (jet.p4()).P()
                #Improper calculation below, fix later
                #if nClnBJets > 2:
                #Event variables
                if nBJets > 2:
                    HT2M += jet.pt
                    H2M += (jet.p4()).P()
                    #Add momentum to HT2M, HT, H here
            elif jet.pt > self.cfg_jNSelPt:
                nOthJets +=1
                if self.makeHistos: self.h_jSel_map.Fill(jet.eta, jet.phi)
                if self.makeHistos: self.h_jSel_pt.Fill(jet.pt)
                #Add jet index to list for collection filling
                jNBIndex.append(jInd)
                #Event variables
                HT += jet.pt
                H += (jet.p4()).P()
                HT2M += jet.pt
                H2M += (jet.p4()).P() 

        #Cut events that don't have minimum number of b-tagged jets
        if nBJets < self.cfg_nBJetMin:
            if self.makeHistos: self.h_cutHisto.Fill(6.5)
            return False
        #Cut events that don't have minimum number of selected, cross-cleaned jets
        if nBJets + nOthJets < self.cfg_nTotJetMin:
            if self.makeHistos: self.h_cutHisto.Fill(7.5)
            return False
        #Cut events that don't have minimum value of HT
        if HT < self.cfg_HTMin:
            if self.makeHistos: self.h_cutHisto.Fill(8.5)
            if self.cutOnHT: return False

        #Calculate HTRat and HTH, since more than 4 jets in the events reaching this point
        HTH = HT/H
        #HTRat = Pt of two highest pt jets / HT

        #####################################################
        ### Write out Selected lepton and jet collections ###
        #####################################################
        ### typeElectron input/typeElectron output corresponds to the electrons
        for br in self.brlist_sep["typeElectron"]:
            out = []
            for elem in eIndex:
                out.append(getattr(electrons[elem], br))
            self.out.fillBranch("%s_%s"%(self.output["typeElectron"],br), out)
        ### typeMuon input/typeMuon output corresponds to the muons
        for br in self.brlist_sep["typeMuon"]:
            out = []
            for elem in mIndex:
                out.append(getattr(muons[elem], br))
            self.out.fillBranch("%s_%s"%(self.output["typeMuon"],br), out)
        ### typeAK4 input/typeAK4Heavy output corresponds to the non-b jets
        for br in self.brlist_sep["typeAK4"]:
            out = []
            for elem in jBIndex:
                out.append(getattr(jets[elem], br))
            self.out.fillBranch("%s_%s"%(self.output["typeAK4Heavy"],br), out)
        ### typeAK4 input/typeAK4Light output corresponds to the non-b jets
        for br in self.brlist_sep["typeAK4"]:
            out = []
            for elem in jNBIndex:
                out.append(getattr(jets[elem], br))
            self.out.fillBranch("%s_%s"%(self.output["typeAK4Light"],br), out)

        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
standaloneEventSelector = lambda : EventSelector(isLastModule=True, verbose=True)
#AllEventSelector = lambda : EventSelector(makeHistos=True, cutOnTrigs=TRUE, cutOnMET=True, cutOnHT=True, verbose=True, selectionConfig=Y.getConfig(), isLastModule=False)

class SimpleActivity(Module):
    def __init__(self):
        #self.writeHistFile=True
        #event counters
        self.counter = 0
        self.maxEventsToProcess = -1


    def beginJob(self, histFile=None,histDirName=None):
        #if self.writeHistFile=False, called by the postprocessor as beginJob()
        #If self.writeHistFile=True, then called as beginJob(histFile=self.histFile,histDirName=self.histDirName)
        Module.beginJob(self,histFile,histDirName)
        # if self.makeHistos:
        #     self.h_cutHisto = ROOT.TH1F('h_cutHisto', ';Pruning Point in Event Selection; Events', 10, 0, 10)
        #     self.addObject(self.h_cutHisto)
        #     self.h_jSel_map = ROOT.TH2F('h_jSel_map', ';Jet Eta;Jet Phi', 40, -2.5, 2.5, 20, -3.14, 3.14)
        #     self.addObject(self.h_jSel_map)
        #     self.h_jSel_pt = ROOT.TH1F('h_jSel_pt', ';Jet Pt; Events', 20, 20, 420)
        #     self.addObject(self.h_jSel_pt)
        #     self.h_jBSel_map = ROOT.TH2F('h_jBSel_map', ';Jet Eta;Jet Phi', 40, -2.5, 2.5, 20, -3.14, 3.14)
        #     self.addObject(self.h_jBSel_map)
        #     self.h_jBSel_pt = ROOT.TH1F('h_jBSel_pt', ';Jet Pt; Events', 20, 20, 420)
        #     self.addObject(self.h_jBSel_pt)
            # self.h_medCSVV2 = ROOT.TH1D('h_medCSVV2', ';Medium CSVV2 btags; Events', 5, 0, 5)
            # self.addObject(self.h_medCSVV2)
        pass

    # def endJob(self):
    #     Module.endJob()
        #called once output has been written
        #Cannot override and use pass here if objects need to be written to a histFile
        #pass

    # def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    #     Module.beginFile(inputFile, outputFile, inputTree, wrappedOutputTree)
    #     pass

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
        if (self.counter % 100) == 0:
            print("Processed {0:2d} Events".format(self.counter))

        HT = 0

        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        jets = Collection(event, "Jet")
        met = Object(event, "MET")
        HLT = Object(event, "HLT")

        if met.pt < 25:
            return False

        for jet in jets:
            if jet.jetId < 2:
                continue
            if abs(jet.eta) > 2.5:
                continue
            HT += jet.pt
        
        if HT < 350:
            return False

        return True
            
TestMiddle = lambda : SimpleActivity()
