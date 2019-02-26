from __future__ import (division, print_function)
import os
import ROOT
#import numpy as np
#import itertools
#from collections import OrderedDict
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #deltaR, deltaPhi, etc.

_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }

class MCTruth(Module):
    def __init__(self, verbose=False, makeHistos=False):
        self.writeHistFile=True
        self.MADEHistos=False

        #load the criteria for brevity
        #self.CFG = selectionConfig

        #choose whether we want verbose output or to produce cut histograms 
        self._verbose = verbose
        self.makeHistos = makeHistos

        #event counters
        self.counter = 0
        self.maxEventsToProcess = -1

        # #Muon CFG loading from config file
        # self.cfg_mMaxEta = self.CFG["Muon"]["Common"]["Eta"] #Max Eta acceptance
        # self.cfg_mSelPt = self.CFG["Muon"]["Select"]["Pt"] #min Pt for selection
        # self.cfg_mSelRelIso = self.CFG["Muon"]["Select"]["RelIso"] #Relative Isolation
        # self.cfg_mSelId = self.CFG["Muon"]["Select"]["IdLevel"]
        # #All muons in NanoAOD are loose Muons or better, so loose-only are just those failing the "mediumId"

        # #Jet CFG loading from config file
        # self.cfg_jMaxEta = self.CFG["Jet"]["Common"]["Eta"] #Max Eta acceptance
        # self.cfg_jId = self.CFG["Jet"]["Common"]["JetId"]
        # self.cfg_jNSelPt = self.CFG["Jet"]["NonBJet"]["Pt"] #Non-B Jet minimum Pt
        # self.cfg_jBSelPt = self.CFG["Jet"]["BJet"]["Pt"] #B Jet minimum Pt
        # self.cfg_jBAlgo = self.CFG["Jet"]["Algo"] #bTagging Algorithm
        # self.cfg_jBWP = self.CFG["Jet"]["WP"] #working point, like "Medium" or "Tight"
        # self.cfg_jBThresh = self.CFG["Jet"][self.cfg_jBAlgo][self.cfg_jBWP]
        # self.cfg_jClnTyp = self.CFG["Jet"]["CleanType"]
        # self.cfg_jMaxdR = self.CFG["Jet"]["MaxDeltaR"]

        # #Event CFG loading from config file
        # self.cfg_lowMRes_cent = self.CFG["Event"]["LowMassReson"]["Center"] #Low mass resonance veto center
        # self.cfg_lowMRes_hwidth = self.CFG["Event"]["LowMassReson"]["HalfWidth"] #low mass resonance veto half-width
        # self.cfg_ZMRes_cent = self.CFG["Event"]["ZMassReson"]["Center"] #Z mass resonance veto center
        # self.cfg_ZMRes_hwidth = self.CFG["Event"]["ZMassReson"]["HalfWidth"] #Z mass resonance veto half-width
        # self.cfg_HTMin = self.CFG["Event"]["HTMin"] #Minimum HT
        # self.cfg_nBJetMin = self.CFG["Event"]["nBJetMin"] #Minimum bTagged jets
        # self.cfg_nTotJetMin = self.CFG["Event"]["nTotJetMin"] #Minimum total jets
        # self.cfg_minMET = self.CFG["MET"]["MinMET"] #Minimum MET

    def beginJob(self,histFile=None,histDirName=None):
        print("histfile=" + str(histFile) + " directoryname=" + str(histDirName))
        if histFile != None and histDirName != None:
            #self.writeHistFile=True
            prevdir = ROOT.gDirectory
            self.histFile = histFile
            self.histFile.cd()
            self.dir = self.histFile.mkdir( histDirName )
            prevdir.cd()
            self.objs = []
            if self.makeHistos:
                # self.h_jSel_map = ROOT.TH2F('h_jSel_map', ';Jet Eta;Jet Phi', 40, -2.5, 2.5, 20, -3.14, 3.14)
                # self.addObject(self.h_jSel_map)
                self.MADEHistos=True

    def endJob(self):
        if hasattr(self, 'objs') and self.objs != None:
            prevdir = ROOT.gDirectory
            self.dir.cd()
            for obj in self.objs:
                obj.Write()
            prevdir.cd()
            if hasattr(self, 'histFile') and self.histFile != None : 
                self.histFile.Close()

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        # _brlist = inputTree.GetListOfBranches()
        # branches = [_brlist.At(i) for i in xrange(_brlist.GetEntries())]
        # placeholder = []
        # for elem in self.input:
        #     placeholder.append([])
        # self.brlist_sep = dict(zip(self.input.keys(), placeholder))
        # for key in self.input.keys():
        #     self.brlist_sep[key] = self.filterBranchNames(branches,self.input[key])

        self.out = wrappedOutputTree
        # self.out.branch("Electron_PES", "O", lenVar="nElectron", title="Boolean for electrons passing the event selection criteria")
        # self.out.branch("Muon_PES", "O", lenVar="nMuon", title="Boolean for muons passing the event selection criteria")
        # self.out.branch("Jet_PES", "O", lenVar="nJet", title="Boolean for jets passing the event selection criteria")
        # self.out.branch("Jet_Tagged", "O", lenVar="nJet", title="Boolean for jets passing the B-tagging and corresponding Pt requirements")
        # self.out.branch("Jet_Untagged", "O", lenVar="nJet", title="Boolean for jets passing the non-B-tagged and corresponding Pt  criteria")

        #Define the EventVar_ subvariables' type (Double, Int, Bool...)
        # self.varDict = OrderedDict([("H", "D"),
        #                              ("H2M", "D"),
        #                              ("HT", "D"),
        #                              ("HT2M", "D"),
        #                              ("HTH", "D"),
        #                              ("HTRat", "D"),
        #                              ("nBTagJet", "I"),
        #                              ("nTotJet", "I"),
        #                              ("Trig_MuMu", "O"),
        #                              ("Trig_ElMu", "O"),
        #                              ("Trig_ElEl", "O"),
        #                              ("Trig_Mu", "O"),
        #                             ])

        #Define the EventVar_ subvariables' titles
        # self.titleDict = OrderedDict([("H", "Sum of selected jet's 3-momentum P (magnitude)"), 
        #                              ("H2M", "Sum of slected jet 3-momentum (magnitude) except the 2 highest-pt B-tagged jets"),
        #                              ("HT", "Sum of selected jet transverse momentum"),
        #                              ("HT2M", "Sum of slected jet transverse momentum except the 2 highest-Pt B-tagged jets"),
        #                              ("HTH", "Ratio of HT to H in the event"),
        #                              ("HTRat", "Ratio of the sum of 2 highest selected jet Pts to HT"),
        #                              ("nBTagJet", "Number of post-selection and cross-cleaned b-tagged jets"),
        #                              ("nTotJet", "Number of total post-selection and cross-cleaned jets"),
        #                              ("Trig_MuMu", "Event passed one of the dimuon HLT triggers"),
        #                              ("Trig_ElMu", "Event passed one of the electron-muon HLT triggers"),
        #                              ("Trig_ElEl", "Event passed one of the dielectron HLT triggers"),
        #                              ("Trig_Mu", "Event passed one of the solo-muon HLT triggers"),
        #                             ])
        # for name, valType in self.varDict.items():
        #     self.out.branch("EventVar_%s"%(name), valType, title=self.titleDict[name])


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
        # if -1 < self.maxEventsToProcess < self.counter:
        #     return False
        if 5 < self.counter:
            return False
        # if (self.counter % 5000) == 0:
        #     print("Processed {0:2d} Events".format(self.counter))
        
        ###############################################
        ### Collections and Objects and isData check###
        ###############################################

        #Check whether this file is Data from Runs or Monte Carlo simulations
        self.isData = True
        if hasattr(event, "nGenPart") or hasattr(event, "nGenJet") or hasattr(event, "nGenJetAK8"):
            self.isData = False
        if self.isData:
            print("WARNING: Attempt to run MCTruth Module on Data (Detected)!")
            return False
        
        PV = Object(event, "PV")
        otherPV = Collection(event, "OtherPV")
        SV = Collection(event, "SV")
        
        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        jets = Collection(event, "Jet")
        fatjets = Collection(event, "FatJet") #Correct capitalization?
        subjets = Collection(event, "SubJet")
        #met = Object(event, "MET")
        met = Object(event, "METFixEE2017") #FIXME: Placeholder until passed in via configuration?

        HLT = Object(event, "HLT")
        Filters = Object(event, "Flag") #For Data use only

        gens = Collection(event, "GenPart")
        genjets = Collection(event, "GenJet")
        genfatjets = Collection(event, "GenJetAK8")
        gensubjets = Collection(event, "SubGenJetAK8")
        genmet = Object(event, "GenMET")
        generator = Object(event, "Generator")
        btagweight = Object(event, "btagWeight") #contains .CSVV2 and .DeepCSVB float weights
        #genweight = 
        #lhe = Object(event, "FIXME")
        #weights = FIXME
        #PSWeights = FIXME

        ##################################
        ### Print info for exploration ###
        ##################################

        print("\n\n\nRun: " + str(event.run) + " Lumi: " + str(event.luminosityBlock) + " Event: " + str(event.event))
        print("\n==========Generator==========")
        print("{0:>10s} {1:>5s} {2:>5s} {3:>10s} {4:>10s} {5:>7s} {6:>7s} {7:>10s} {8:>10s}"
              .format("Bin Var", "ID 1", "ID 2", "Q2 Scale", "gen wght", "x1 mom.", "x2 mom.", "x*pdf 1", "x*pdf 2"))
        print("{0:>10f} {1:>5d} {2:>5d} {3:>10.4f} {4:>10.4f} {5:>7.3f} {6:>7.3f} {7:>10.4f} {8:>10.4f}"
              .format(generator.binvar, generator.id1, generator.id2, 
                      generator.scalePDF, generator.weight, generator.x1,
                      generator.x2, generator.xpdf1, generator.xpdf2))

        print("\n==========btag Weight==========")
        print("CSVv2: " + str(btagweight.CSVV2) + " DeepCSV: " + str(btagweight.DeepCSVB))

        print("\n\n==========Here be thy jets==========")
        print("=====Selected Jets=====\n{0:>5s} {1:>10s} {2:>10s} {3:>10s} {4:>10s} {5:10s} {6:>10s}"
              .format("IdX", "pt", "eta", "phi","DeepFlavB", "genJetIdx", "jID"))
        for nj, jet in enumerate(jets):
            if not jet.PES:
                continue
            print("{0:>5d} {1:>10.4f} {2:>10.4f} {3:>10.4f} {4:>10.4f} {5:>10d} {6:>10d}".format(nj, jet.pt, jet.eta, jet.phi, jet.btagDeepFlavB, jet.genJetIdx, jet.jetId))
        print("=====Unselected Jets=====\n{0:>5s} {1:>10s} {2:>10s} {3:>10s} {4:>10s} {5:10s} {6:>10s}"
              .format("IdX", "pt", "eta", "phi","DeepFlavB", "genJetIdx", "jID"))
        for nj, jet in enumerate(jets):
            if jet.PES:
                continue
            print("{0:>5d} {1:>10.4f} {2:>10.4f} {3:>10.4f} {4:>10.4f} {5:>10d} {6:>10d}".format(nj, jet.pt, jet.eta, jet.phi, jet.btagDeepFlavB, jet.genJetIdx, jet.jetId))
        print("=====Gen Jets=====\n{0:>5s} {1:>10s} {2:>10s} {3:>10s} {4:>10s} {5:10s}"
              .format("IdX", "pt", "eta", "phi","Had Flav", "Part Flav"))
        for ngj, genjet in enumerate(genjets):
            print("{0:>5d} {1:>10.4f} {2:>10.4f} {3:>10.4f} {4:>10d} {5:>10d}".format(ngj, genjet.pt, genjet.eta, genjet.phi, genjet.hadronFlavour, genjet.partonFlavour))

        print("\n\n==========Here be thy fatjets==========")
        print("=====Fatjets=====\n{0:>5s} {1:>10s} {2:>10s} {3:>10s} {4:>5s} {5:10s}"
              .format("IdX", "pt", "eta", "phi","jID", "TvsQCD"))
        for nfj, jet in enumerate(fatjets):
            print("{0:>5d} {1:>10.4f} {2:>10.4f} {3:>10.4f} {4:>5d} {5:>10.4f}".format(nfj, jet.pt, jet.eta, jet.phi, jet.jetId, jet.deepTag_TvsQCD))
        print("=====Gen Fatjets=====\n{0:>5s} {1:>10s} {2:>10s} {3:>10s} {4:>10s} {5:10s}"
              .format("IdX", "pt", "eta", "phi","Had Flav", "Part Flav"))
        for ngfj, genjet in enumerate(genfatjets):
            print("{0:>5d} {1:>10.4f} {2:>10.4f} {3:>10.4f} {4:>10d} {5:>10d}".format(ngfj, genjet.pt, genjet.eta, genjet.phi, genjet.hadronFlavour, genjet.partonFlavour))

        print("\n\n==========Here be thy GenParts==========")
        print("=====Gen Fatjets=====\n{0:>5s} {1:>10s} {2:>10s} {3:>10s} {4:>10s} {5:10s} {6:>10s} {7:>10s}"
              .format("IdX", "pt", "eta", "phi","Moth ID", "PDG ID", "Status", "Stat. Flgs"))
        for np, gen in enumerate(gens):
            print("{0:>5d} {1:>10.4f} {2:>10.4f} {3:>10.4f} {4:>10d} {5:>10d} {6:>10d} {7:>10d}".format(np, gen.pt, gen.eta, gen.phi, gen.genIdxMother, gen.pdgId, gen.status, gen.statusFlags))
            
        ################################################
        ### Initialize Branch Variables to be Filled ###
        ################################################
            
        #Arrays
        # electrons_PES = []
        # muons_PES = []
        # jets_PES = []
        # jets_Tagged = []
        # jets_Untagged = []
        # for i in xrange(len(electrons)):
        #     electrons_PES.append(False)
        # for j in xrange(len(muons)):
        #     muons_PES.append(False)
        # for k in xrange(len(jets)):
        #     jets_PES.append(False)
        #     jets_Tagged.append(False)
        #     jets_Untagged.append(False)
        #genTop_VARS

        #########################
        ### Prepare Variables ###
        #########################
        
        

        #############
        ### MUONS ###
        #############

        # for jInd, jet in enumerate(jets):
        #     #Skip any jets that are below the threshold chosen (pass Loose: +1, pass Tight: +2 , pass TightLepVeto: +4
        #     #In 2017 data, pass Loose is always a fail (doesn't exist), so pass Tight and not TLV = 2, pass both = 6
        #     if jet.jetId < self.cfg_jId:
        #         continue
        #     #Eta acceptance
        #     if abs(jet.eta) > self.cfg_jMaxEta:
        #         continue
        #     #Walk through lepton-jet cleaning methods, starting with most accurate and cheapest: PartonMatching
        #     if self.cfg_jClnTyp == "PartonMatching":
        #         if jInd in crosslinkJetIdx:
        #             continue
        #     #Next check if DeltaR was requested instead. More computation required in NanoAOD format, less accurate
        #     elif self.cfg_jClnTyp == "DeltaR":
        #         #raise NotImplementedError("In eventselector class, in jet loop, selected cleaning type of DeltaR matching has not been implemented")
        #         failCleaning = False
        #         #DeltaR against muons
        #         for mIdx in mIndex:
        #             if deltaR(muons[mIdx], jet) < self.cfg_jMaxdR:
        #                 failCleaning = True
        #         #DeltaR against electrons
        #         for eIdx in eIndex:
        #             if deltaR(electrons[eIdx], jet) < self.cfg_jMaxdR:
        #                 failCleaning = True
        #         #Check if jet survived cleaning or now
        #         if failCleaning:
        #             continue
        #     #And protect against invalid lepton-jet cleaning methods, or add in alternative ones here
        #     else:
        #         raise RuntimeError("The requested Lepton-Jet cross-cleaning algorithm [{0:s}] is not available."
        #                            "Please use \"PartonMatching\" or \"DeltaR\"".format(self.cfg_jClnTyp))
        #     #https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
        #     ##if jet.ChosenBTag > ChosenBtagWorkingPoint's Threshold and jet.pt > BTaggedJet's minimum cut
        #     if getattr(jet, self.cfg_jBAlgo) > self.cfg_jBThresh and jet.pt > self.cfg_jBSelPt:
        #         #Flip PassEventSelection and (B)Tagged bits
        #         jets_PES[jInd] = True
        #         jets_Tagged[jInd] = True
        #         nBJets += 1
        #         #Add to HTRat_Numerator if counter is less than 2 (i.e., one of the two highest Pt jets to pass event selection)
        #         if HTRat_Counter < 2:
        #             HTRat_Numerator += jet.pt
        #             HTRat_Counter += 1
        #         #Fill jet histos (Ideally replaced with hsnap() in the future)
        #         if self.MADEHistos: self.h_jBSel_map.Fill(jet.eta, jet.phi)
        #         if self.MADEHistos: self.h_jBSel_pt.Fill(jet.pt)
        #         #Add jet index to list for collection filling
        #         jBIndex.append(jInd) 
        #         #Add momentum to HT, H variables here
        #         HT += jet.pt
        #         H += (jet.p4()).P()
        #         #Improper calculation below, fix later
        #         if nBJets > 2:
        #             #Add momentum to HT2M, H2M variables here
        #             #FIXME: If tagging selection changes from medium, this will be incorrect! (by definition)
        #             HT2M += jet.pt
        #             H2M += (jet.p4()).P()
        #     elif jet.pt > self.cfg_jNSelPt:
        #         #Flip PassEventSelection and Untagged bits
        #         jets_PES[jInd] = True
        #         jets_Untagged[jInd] = True
        #         #Add to HTRat_Numerator if counter is less than 2, relying on cascading through b-tagging/non-b-tagging selection
        #         if HTRat_Counter < 2:
        #             HTRat_Numerator += jet.pt
        #             HTRat_Counter += 1
        #         #Increment jet counter
        #         nOthJets +=1
        #         #Fill jet histos (Ideally replaced with hsnap() in the future) 
        #         #FIXME: This isn't the distribution for the jets post event selection!
        #         if self.MADEHistos: self.h_jSel_map.Fill(jet.eta, jet.phi)
        #         if self.MADEHistos: self.h_jSel_pt.Fill(jet.pt)
        #         #Add jet index to list for collection filling
        #         jNBIndex.append(jInd)
        #         #Add momentum to event variables, no restrictions since these are all untagged jets 
        #         HT += jet.pt
        #         H += (jet.p4()).P()
        #         HT2M += jet.pt
        #         H2M += (jet.p4()).P() 

        # #Cut events that don't have minimum number of b-tagged jets
        # if nBJets < self.cfg_nBJetMin:
        #     if self.MADEHistos: self.h_cutHisto.Fill(6.5)
        #     return False
        # #Cut events that don't have minimum number of selected, cross-cleaned jets
        # if nBJets + nOthJets < self.cfg_nTotJetMin:
        #     if self.MADEHistos: self.h_cutHisto.Fill(7.5)
        #     return False
        # #Cut events that don't have minimum value of HT
        # if HT < self.cfg_HTMin:
        #     if self.MADEHistos: self.h_cutHisto.Fill(8.5)
        #     if self.cutOnHT: return False

        # #Calculate HTRat and HTH, since more than 4 jets in the events reaching this point
        # HTH = HT/H
        # #HTRat = Pt of two highest pt jets / HT
        # HTRat = HTRat_Numerator / HT


        #############################################
        ### Write out slimmed selection variables ###
        #############################################
        
        #Make dictionary that makes this more automated, as in the branch creation
        # self.out.fillBranch("Electron_PES", electrons_PES)
        # self.out.fillBranch("Muon_PES", muons_PES)
        # self.out.fillBranch("Jet_PES", jets_PES)
        # self.out.fillBranch("Jet_Tagged", jets_Tagged)
        # self.out.fillBranch("Jet_Untagged", jets_Untagged)
        # self.out.fillBranch("EventVar_H", H)
        # self.out.fillBranch("EventVar_H2M", H2M)
        # self.out.fillBranch("EventVar_HT", HT)
        # self.out.fillBranch("EventVar_HT2M", HT2M)
        # self.out.fillBranch("EventVar_HTH", HTH)
        # self.out.fillBranch("EventVar_HTRat", HTRat)
        # self.out.fillBranch("EventVar_nBTagJet", nBJets)
        # self.out.fillBranch("EventVar_nTotJet", (nOthJets + nBJets))
        # self.out.fillBranch("EventVar_Trig_MuMu", passMuMu)
        # self.out.fillBranch("EventVar_Trig_ElMu", passElMu)
        # self.out.fillBranch("EventVar_Trig_ElEl", passElEl)
        # self.out.fillBranch("EventVar_Trig_Mu", passMu)

        return True
