import ROOT
import collections, math
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class Trigger(Module):
    def __init__(self, Trigger):
        self.counting = 0
        self.maxEventsToProcess = -1
        self.Trigger = Trigger
        
    def beginJob(self, histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #First N events
        self.counting += 1 
        if -1 < self.maxEventsToProcess < self.counting:
            return False
        
        #run = getattr(event, "run")
        #evt = getattr(event, "event")
        #lumi = getattr(event, "luminosityBlock")
        
        for trig in self.Trigger:
            if hasattr(event, trig) and getattr(event, trig):
                #print(getattr(event, trig))
                return True
            #else:
                #print("No trigger fired")
        return False
