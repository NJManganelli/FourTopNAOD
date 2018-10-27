#Import Python 3-style division, print function
from __future__ import (division, print_function)

import ROOT 
from importlib import import_module

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class ExampleModule(Module): #This line defines our class ExampleModule, and in parenthesis, we indicate it Inherits from the Module class we imported above.
    def __init__(self):
        self.counting = 0

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #First N events
        self.counting += 1 
        if self.counting > 5:
            return False
        
        run = getattr(event, "run")
        evt = getattr(event, "event")
        lumi = getattr(event, "luminosityBlock")

        print("================================================================================================")
        print("Run: {0:>8d} \t LuminosityBlock: {1:>8d} \t Event: {2:>8d} \n".format(run, lumi, evt) )

        ###########################################
        ###### Event Collections and Objects ######
        ###########################################
        electrons = Collection(event, "Electron")
        #photons = Collection(event, "Photon")
        muons = Collection(event, "Muon")
        jets = Collection(event, "Jet")
        met = Object(event, "MET")
        
        nEles = len(electrons)
        nMus = len(muons)
        nJets = len(jets)
    
        #The format used here is: {FormatIndex : JustificationType ReservedSpace DataType
        #    Thus {1:>3d} means this place should have the value of nMus(nEles is index 0 in .format( arg0, arg1, arg2, arg3) inserted, 
        #    it should be right justified (>), have a width of 3 characters,  and it's an integer (d) rather than a string (s) or float/double (f)
        # See: https://docs.python.org/2/library/string.html#format-string-syntax
        print("\t Electrons: {0:>3d} \t Muons: {1:>3d} \t Jets: {2:>3d} \n".format(nEles, nMus, nJets) )

        # Create a LorentzVector for the event 4-momentum:
        eventSum = ROOT.TLorentzVector()

        #Use the enumerate() function to get both an index and the iterated item in the collection
        print("\n{0:>5s} {1:>10s} {2:>10s} {3:>10s}".format("Muon", "Pt", "Eta", "Phi"))
        for nm, muon in enumerate(muons) :
            eventSum += muon.p4()
            print("{0:*<5d} {1:>10.4f} {2:>+10.3f} {3:>+10.3f}".format(nm+1, muon.pt, muon.eta, muon.phi))

        print("\n{0:>5s} {1:>10s} {2:>10s} {3:>10s}".format("Ele", "Pt", "Eta", "Phi"))
        for ne, ele in enumerate(electrons) :
            eventSum += ele.p4()
            print("{0:*^5d} {1:>10.4f} {2:> 10.3f} {3:> 10.3f}".format(ne+1, ele.pt, ele.eta, ele.phi))

        print("\n{0:>5s} {1:>10s} {2:>10s} {3:>10s}".format("Jet", "Pt", "Eta", "Phi"))
        for nj, jet in enumerate(jets):
            eventSum += jet.p4()
            print("{0: >5d} {1:>10.4f} {2:>-10.3f} {3:>-10.3f}".format(nj+1, jet.pt, jet.eta, jet.phi))

        #Slightly different syntax for getting the Mass, Pt, etc. from a TLorentzVector
        print("\n\nEvent Mass: {0:<10.4f} \t Event Pt: {1:<10.4f} \t Event Eta: {2:<10.4f} \t Event Phi: {3:10.4f}\n"
              .format(eventSum.M(), eventSum.Pt(), eventSum.Eta(), eventSum.Phi() ) )
        print("================================================================================================")
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
