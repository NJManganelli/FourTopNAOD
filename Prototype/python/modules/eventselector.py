import os
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class EventSelector(Module):
    def __init__(self, channel=None, selectionConfig=None, verbose=False):
        #self.jetSel = jetSelection
        self.writeHistFile=False
        #Choose the channel for selection criteria
        self.channel = channel
        #load the criteria for brevity
        self.CFG = selectionConfig
        #choose whether we want verbose output
        self.verbose = verbose
        #counter
        self.counter = 0
        #cfg Electron criteria (later: load from configuration dictionary
        self.cfg_eSelPt = 25.0 #min Pt for selection
        self.cfg_eSelEta = 2.4 #Max Eta acceptance
        self.cfg_eIDType = "cutBased"
        self.cfg_eIdSel = 3 #medium
        self.cfg_eIdExtra = 1 #veto
        #cfg Muon criteria
        self.cfg_mSelPt = 20 #min Pt for selection
        self.cfg_mSelEta = 2.4 #Max Eta acceptance
        self.cfg_mIdSel = "mediumId"
        self.cfg_mIdExtra = "looseId"
        #cfg Jet criteria
        self.cfg_jId = 2 #Tight and Tight Lep Veto are the only supported IDs in 2017
        self.cfg_jSelEta = 2.4 #Max Eta acceptance
        self.cfg_jNSelPt = 30.0 #Non-B Jet minimum Pt
        self.cfg_jBSelPt = 25.0 #B Jet minimum Pt
        self.cfg_jBId = "btagCSVV2" #method of bTagging
        self.cfg_jBWP = 0.8838 #Medium CSVv2 working point cut
        self.cfg_jClnTyp = "PartonMatching" #As opposed to "DetlaR"
        #Baseline criteria
        self.cfg_nSelLep = 2
        self.cfg_minHt = 500
        self.cfg_lepOppChg = True
        self.cfg_lowMRes_cent = 10.0 #Low mass resonance veto center
        self.cfg_lowMRes_hwidth = 10.0 #low mass resonance half-width
        self.cfg_ZMRes_cent = 91.0 #Z mass resonance veto center
        self.cfg_ZMRes_hwidth = 15 #Z mass resonance half-width

    def beginJob(self):
        #called by the postprocessor as beginJob() if not writing a histogram file
        #If self.writeHistFile=True, then called as beginJob(histFile=self.histFile,histDirName=self.histDirName)
        #Below channel can be stripped out if it's handled by the FileLoader tool, instead using a check based on config passed (selected leps = 2 or 1)
        if self.channel not in ["SL", "DL"]:
            raise RuntimeError("No channel specified for EventSelector. Use EventSelector(channel) where channel = \"SL\", \"DL\"")
        if self.channel == "SL":
            raise NotImplementedError("No Implementation for Single-Lepton Channel yet exists")
        if self.channel == "DL":
            print("EventSelector has been configured for running Opposite-sign Dilepton selection\n")
        
        

    def endJob(self):
        #called once output has been written
        #Cannot override and use pass here if objects need to be written to a histFile
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree): #called by the eventloop at start of new inputFile
        #Module just passes
        #wrappedOutputTree only exists if noOut=False and events are written!
        self.out = wrappedOutputTree
        self.out.branch("EventMass",  "F");
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree): #called by the eventloop at end of inputFile
        #Module just passes
        pass
    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        self.counter +=1
        if (self.counter % 10) == 0:
            print("Processed {0:2d} Events".format(self.counter))

        PV = Object(event, "PV")
        otherPV = Collection(event, "otherPV")
        SV = Collection(event, "SV")

        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        jets = Collection(event, "Jet")
        met = Object(event, "MET")

        HLT = Object(event, "HLT")
        Filters = Object(event, "Flag")

        eventSum = ROOT.TLorentzVector()
        
        for lep in muons :
            if lep.
            eventSum += lep.p4()
        for lep in electrons :
            eventSum += lep.p4()
#        for j in filter(self.jetSel,jets):

        nBJets = 0
        nOthJets = 0
        jSC = self.Selection["Jet"]
        for jet in jets :
            if jet.jetId < 2:
                continue
            if abs(jet.eta) > jSC["Eta"]:
                continue
            #Count b-tagged jets with two algos at the medium working point
            #https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
            ##if jet.ChosenBTag > ChosenBtagWorkingPoint's Threshold and jet.pt > BTaggedJet's minimum cut
            if getattr(jet, jSC["bTag"]) > jSC["bTagThresh"][jSC["bTagWP"]] and jet.pt > jSC["PtBJet"]:
                nBJets += 1
            elif jet.pt > jSC["PtOthJet"]:
                nOthJets +=1
                
            eventSum += jet.p4()



        self.out.fillBranch("EventMass",eventSum.M())
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

#exampleModuleConstr = lambda : exampleProducer(jetSelection= lambda j : j.pt > 30) 
DileptonEventSelector = lambda : EventSelector(channel="DL")
SingleLepEventSelector = lambda : EventSelector(channel="SL")
