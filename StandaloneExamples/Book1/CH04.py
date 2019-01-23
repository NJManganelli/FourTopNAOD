#Import Python 3-style division, print function
from __future__ import (division, print_function)

import ROOT 
from importlib import import_module

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class ExampleModule(Module): #This line defines our class ExampleModule, and in parenthesis, we indicate it Inherits from the Module class we imported above.
    def __init__(self):
        self.counting = 0

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #First N events
        self.counting += 1 
        if self.counting > 10:
            return False
        
        run = getattr(event, "run")
        evt = getattr(event, "event")
        lumi = getattr(event, "luminosityBlock")

        print("Run: {0:>8d} \t LuminosityBlock: {1:>8d} \t Event: {2:>8d}".format(run, lumi, evt) )

        nEles = getattr(event, "nElectron")
        nMus = getattr(event, "nMuon")
        nTaus = getattr(event, "nTau")
        nJets = getattr(event, "nJet")
    
        print("\t Electrons: {0:>3d} \t Muons: {1:>3d} \t Taus: {2:>3d} \t Jets: {3:>3d} \n".format(nEles, nMus, nTaus, nJets) )

        electrons = Collection(event, "Electron")
        photons = Collection(event, "Photon")
        muons = Collection(event, "Muon")
        jets = Collection(event, "Jet")
        met = Object(event, "MET")

        HLT = Object(event, "HLT") 
        Filters = Object(event, "Flag") 
        PV = Object(event, "PV")
        SV = Collection(event, "SV")
        genParts = Collection(event, "GenPart")
        genJets = Collection(event, "GenJet")
        genFatJets = Collection(event, "GenJetAK8")

        print("PV  X: {0: >5.3f} Y: {1: >5.3f} Z: {2:5.3f} nDoF: {3: >5f} Chi^2: {4: >5.3f}".format(
            PV.x,PV.y, PV.z, PV.ndof, PV.chi2))
        if len(SV) > 0:   
            print("nSV: {0: >3d} SV[0] Decay Length:{1: >5.3f}".format(len(SV), SV[0].dlen ))
        else:
            print("nSV: {0: >3d}".format(len(SV)))
        print("{0:>5s} {1:>10s} {2:>10s} {3:>10s}".format("Muon", "Pt", "Eta", "Phi"))
        for nm, lep in enumerate(muons) :
            eventSum += lep.p4()
            #format_spec ::=  [[fill]align][sign][#][0][width][,][.precision][type]
            print("{0:*<5d} {1:>10.4f} {2:>+10.3f} {3:>+10.3f}".format(nm+1, lep.pt, lep.eta, lep.phi))
        print("{0:>5s} {1:>10s} {2:>10s} {3:>10s}".format("Electron", "Pt", "Eta", "Phi"))
        for ne, lep in enumerate(electrons) :
            eventSum += lep.p4()
            print("{0:*^5d} {1:>10.4f} {2:> 10.3f} {3:> 10.3f}".format(ne+1, lep.pt, lep.eta, lep.phi))
        #for j in filter(self.jetSel,jets):
        print("{0:>5s} {1:>10s} {2:>10s} {3:>10s}".format("Jet", "Pt", "Eta", "Phi"))
        for nj, j in enumerate(jets):
            eventSum += j.p4()
            print("{0: >5d} {1:>10.4f} {2:>-10.3f} {3:>-10.3f}".format(nj+1, j.pt, j.eta, j.phi))
        #for nt, trig in enumerate(triggers):
        #    if(nt < 5): print("TypeName: " + trig.GetTypeName())
        #idea: create list of names for triggers, then check bits with "triggers.name for name in names"
        #Use getattr(triggers, variablename) to access!
        passTrig=["PFMETNoMu90_PFMHTNoMu90_IDTight"]
        for trig in passTrig:
            print("HLT_" + str(trig) + " Trigger: " + str(getattr(HLT, trig)) )
        passFilter=["HBHENoiseFilter", "HBHENoiseIsoFilter", "EcalDeadCellTriggerPrimitiveFilter", 
                    "globalSuperTightHalo2016Filter", "goodVertices", "METFilters"]
        for fltr in passFilter:
            print("Flag_" + str(fltr) + " Filter: " + str(getattr(Filters, fltr)))
        print("Event Mass: {:<10.4f}\n".format(eventSum.M()))
        return True

#Try commenting the first one out and uncommenting the skim made in CH01
files=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAOD/TTJets_SingleLeptFromT_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/00000/06CC0D9B-4244-E811-8B62-485B39897212.root"]
#files=["06CC0D9B-4244-E811-8B62-485B39897212_CH01-Skim.root"]

#Create a postprocessor, passing it the necessary and optional parameters
#This time, we pass it our ExampleModule() in the modules list
p2=PostProcessor(".", #The output Directory and files list must appear in the same places every time
                files,
                jsonInput={1 : [[10000, 10010]]}, #Named= options can be moved around
                cut="nMuon > 0 && nJet > 5",
                modules=[ExampleModule()],
                noOut=True #We use the option noOut to prevent the PostProcessor from writing out the NanoAOD file
                #justcount=True,
                )

p2.run()
