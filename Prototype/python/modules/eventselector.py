import os
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class EventSelector(Module):
    def __init__(self, channel=None, verbose=False, overrideCriteria=None, invertIsolation=False):
        #self.jetSel = jetSelection
        self.writeHistFile=False
        #Choose the channel for selection criteria
        self.channel = channel
        #choose whether we want verbose output
        self.verbose = verbose
        #designate whether we were passed overriding criteria (rather than the standard ones from 2016 analysis (eventually 2017))
        self.std_selection = (overrideCriteria == None)
        #load the criteria
        self.Selection = overrideCriteria
        #boolean for inverting isolation cut
        self.invIso = invertIsolation
        self.counter = 0
        pass
    def beginJob(self):
        #called by the postprocessor as beginJob() if not writing a histogram file
        #If self.writeHistFile=True, then called as beginJob(histFile=self.histFile,histDirName=self.histDirName)
        if self.channel not in ["SL", "DL"]:
            raise RuntimeError("No channel specified for EventSelector. Use EventSelector(channel) where channel = \"SL\", \"DL\"")
        if self.std_selection:
            if self.channel == "SL":
                raise NotImplementedError("No Implementation for Single-Lepton Channel yet exists")
            if self.channel == "DL":
                #This could just be spun off, and always loaded externally, with a check that the name and channel match in some way
                self.Selection = {
                    "Electron" : {
                        "Select" : {
                            "Pt" : 25.0, 
                            "Eta" : 2.4, 
                            "IDType" : "Cutbased", #MVA available too
                            "IDlevel" : "Medium"
                            },
                        "Veto" : {
                            "Pt" : 25.0,
                            "Eta" : 2.4,
                            "IDType" : "Cutbased",
                            "IDlevel" : "Veto"
                            }
                        },
                    "Muon" : {
                        "Select" : {
                            "Pt" : 20,
                            "Eta" : 2.4,
                            "RelIso" : 0.15,
                            "IDlevel" : "Medium"
                            },
                        "Veto" : {
                            "Pt" : 20,
                            "Eta" : 2.4,
                            "RelIso" : 0.25, #FIXME
                            "IDlevel" : "Loose"
                            }
                        },
                    "AK4Jet" : {
                        "PtNonBJet" : 30.0,
                        "PtBJet" : 25.0,
                        "Eta" : 2.4,
                        "JetID" : "Tight", #Only Tight and Tight Lepton Veto supported in 2017 and 2018
                        "bTagger" : "CSVv2", #DeepB and DeepFlavour available
                        "bTaggerWP" : "Medium",
                        "bTaggerThresh" : { 
                            "CSVv2" : { "Loose" : "FIXME", "Medium" : "FIXME", "Tight" : "FIXME"},
                            "DeepB" : { "Loose" : "FIXME", "Medium" : "FIXME", "Tight" : "FIXME"},
                            "DeepFlav" : { "Loose" : "FIXME", "Medium" : "FIXME", "Tight" : "FIXME"}
                            },
                        "CleanType" : "PartonMatch" #This is implicit in using jetIDx references, otherwise use "Delta"
                        },
                    "HLT" : {
                        "cutOnTrigs" : False, #FIXME, default True? 
                        "chMuMu" : ["Placeholder", "List", "of", "trigger", "names"],
                        "chElMu" : ["Placeholder", "List", "of", "trigger", "names"],
                        "chElEl" : ["Placeholder", "List", "of", "trigger", "names"]
                        },
                    "PV" : { 
                        "FIXME, Placeholder for Primary Vertex requirements" 
                        },
                    "MET" : { 
                        #FIXME, default True 
                        "cutOnFilts" : False
                        },
                    "Baseline" : {
                        "HT" : 500,
                        "nSelLep" : 2,
                        "nVetoLep" : 0,
                        "LowMassReson" : {
                            "Center" : 10.0, 
                            "HalfWidth" : 20.0
                            },
                        "ZMassReson" : {
                            "Center" : 91.0, 
                            "HalfWidth" : 15.0
                            }
                        }
                    }
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
        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        jets = Collection(event, "Jet")
        eventSum = ROOT.TLorentzVector()
        for lep in muons :
            eventSum += lep.p4()
        for lep in electrons :
            eventSum += lep.p4()
#        for j in filter(self.jetSel,jets):
        for j in jets :
            eventSum += j.p4()
        self.out.fillBranch("EventMass",eventSum.M())
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

#exampleModuleConstr = lambda : exampleProducer(jetSelection= lambda j : j.pt > 30) 
DileptonEventSelector = lambda : EventSelector(channel="DL")
SingleLepEventSelector = lambda : EventSelector(channel="SL")
