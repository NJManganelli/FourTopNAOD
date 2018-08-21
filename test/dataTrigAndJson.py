from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os, sys, time
import ROOT
from importlib import import_module

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class MFaJaT(Module):
    def __init__(self):
        self.writeHistFile=True
        self.counter = 0
    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)
        
        self.h_lumiblock = ROOT.TH1I('h_lumiblock', 'lumiblock',   100, 0, 1000)
        self.addObject(self.h_lumiblock)
        self.h_run = ROOT.TH1D('h_run', 'runs', 100, 273.0, 280.0)
        self.addObject(self.h_run)
 #   def endJob(self):
#        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
        ###########################################
        ###### Basic Attributes of the Event ######
        ###########################################
        run = getattr(event, "run")
        lumi = getattr(event, "luminosityBlock")
        evt = getattr(event, "event")
        
        self.h_lumiblock.Fill(lumi)
        self.h_run.Fill(run)
        #print("Run: {0:>8d} LuminosityBlock: {2:>8d} Event: {1:>8d}".format(run, evt, lumi)) #swizzling because lazy
        self.counter += 1
        if(self.counter > 6000): 
            return False
        return True #Exit early, to just print this info for a json file test...
        
        ################################
        ###### High Level Trigger ######
        ################################
        HLT = Object(event, "HLT") #Grab all the HLT triggers 'together'
        passTrig=["PFMETNoMu90_PFMHTNoMu90_IDTight"] #Create a list of valid triggers to check, dropping "HLT_"
        for trig in passTrig:
            print("HLT_" + str(trig) + " Trigger: " + str(getattr(HLT, trig)) )
            
            
        ###############################
        ######### MET Filters #########
        ###############################
        Filters = Object(event, "Flag") #Grab all the MET Filters in a group
        passFilter=["HBHENoiseFilter", "HBHENoiseIsoFilter", "EcalDeadCellTriggerPrimitiveFilter", 
                    "globalSuperTightHalo2016Filter", "goodVertices", "METFilters"] #All the filters commonly used 
        for fltr in passFilter:
            print("Flag_" + str(fltr) + " Filter: " + str(getattr(Filters, fltr)))
        
        
        ###########################################
        ###### Event Collections and Objects ######
        ###########################################
        electrons = Collection(event, "Electron")
        photons = Collection(event, "Photon")
        muons = Collection(event, "Muon")
        taus = Collection(event, "Tau")
        jets = Collection(event, "Jet")
        met = Object(event, "MET")
        PV = Object(event, "PV")
        SV = Collection(event, "SV")
        
        ###############################
        ###### Time To Do Stuff? ######
        ###############################
        eventSum = ROOT.TLorentzVector()
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
        print("Event Mass: {:<10.4f}\n".format(eventSum.M()))
        
        ###########################################
        ###### Return True to pass the event ######
        ###########################################
        return True

preselection=None
inputList = open("../data/Run2016/Run2016B_SM", "r")
files=[]
for line in inputList:
    files.append("root://cms-xrd-global.cern.ch/" + str(line))
onefile = [files[0]] #Experiment with just one file for now...

p=PostProcessor(".",onefile,cut=preselection,branchsel=None,modules=[MFaJaT()],friend=False,postfix="_MFaJaT", 
                jsonInput=None,noOut=True,justcount=False,provenance=False,
                haddFileName=None,fwkJobReport=False,histFileName="histOut.root",
                histDirName="plots", outputbranchsel=None)

p.run()
