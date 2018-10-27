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
        #Increment the counter each time we process an event
        self.counting += 1 
        
        #Here, we return False after counting reaches a certain point, which effectively "Skips" to the next event until it reaches end of file.
        if self.counting > 7:
            return False
        
        #For the first N events, before this limit, we'll continue to the below code, so that we can print out the Run, Lumi, Event, and number of leptons/jets
        run = getattr(event, "run") #run = event.run works equally well, but this method is more powerful
        evt = getattr(event, "event")
        lumi = getattr(event, "luminosityBlock")

        #This function formats a string and prints it out, using \t for tabs and d for double/float type elements
        print("Run: {0:>8d} \t LuminosityBlock: {1:>8d} \t Event: {2:>8d}".format(run, lumi, evt) )

        nEles = getattr(event, "nElectron")
        nMus = getattr(event, "nMuon")
        nTaus = getattr(event, "nTau")
        nJets = getattr(event, "nJet")

        #Print the leptons and jets, insert a newline using \n
        print("\t Electrons: {0:>3d} \t Muons: {1:>3d} \t Taus: {2:>3d} \t Jets: {3:>3d} \n".format(nEles, nMus, nTaus, nJets) )
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
