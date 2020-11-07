from __future__ import division, print_function
import ROOT
import math
import pdb
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.toolbox import *

class JetMETSkimmer(Module):
    def __init__(self, jetMinPt=20.0, jetMaxEta=2.5, jetMinID=0b010, jetMinCount=2, fillHists=False):
                 #passLevel, era="2017", subera=None, isData=True, weightMagnitude=1, fillHists=False, btagging=['DeepJet', 'M'], MET=[45, 50], HT=[450,500], ZWidth=15, jetPtVar = "pt_nom", jetMVar = "mass_nom", verbose=False, probEvt=None, mode="Flag", debug=False):
                 # genEquivalentLuminosity=1, genXS=1, genNEvents=1, genSumWeights=1, era="2017", btagging=['DeepCSV','M'], lepPt=25,  GenTop_LepSelection=None):
        """Slim Jet selection module that looks across all jes/jer variations and selections events with the requirements in initialization. Currentlly no lepton cross-cleaning is done in order to fully support QCD estimations and other studies."""

        self._need_systematics = True #Set this flag to false after running the first event and grabbing the sytematic variations
        self.systematics = []
        self.jet_min_pt = jetMinPt
        self.jet_max_eta = jetMaxEta
        self.jet_min_id = jetMinID
        self.jet_min_count = jetMinCount

        self.writeHistFile = False
        self.fillHists = False
        if self.fillHists and not self.writeHistFile:
            self.writeHistFile=True

    def beginJob(self, histFile=None,histDirName=None):
        if self.fillHists == False and self.writeHistFile == False:
            Module.beginJob(self, None, None)
        else:
            if histFile == None or histDirName == None:
                raise RuntimeError("fillHists set to True, but no histFile or histDirName specified")
            ###Inherited from Module
            prevdir = ROOT.gDirectory
            self.histFile = histFile
            self.histFile.cd()
            self.dir = self.histFile.mkdir( histDirName + "_JetMETLogic")
            prevdir.cd()
            self.objs = []

    # def endJob(self):
    #     if hasattr(self, 'objs') and self.objs != None:
    #         prevdir = ROOT.gDirectory
    #         self.dir.cd()
    #         for obj in self.objs:
    #             obj.Write()
    #         prevdir.cd()
    #         if hasattr(self, 'histFile') and self.histFile != None: 
    #             self.histFile.Close()

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""

        if self._need_systematics:
            self.systematics = self.getSystematics(event)
            print("Jet pt systematic variations: {}".format(self.systematics))
            if len(self.systematics) > 0:
                self._need_systematics = False
            else:
                pdb.set_trace()
                raise RuntimeError("No Jet pt systematics deduced in {}".format(self.__name__))

        ###############################################
        ### Collections and Objects and isData check###
        ###############################################        
        
        jets = Collection(event, "Jet")
        # electrons = Collection(event, "Electron")
        # muons = Collection(event, "Muon")
        # taus = Collection(event, "Tau")

        ############
        ### Jets ###
        ###########

        selected_jets = dict()
        #create lists for each systematic. Not strictly necessary, as simple counters would be minimally sufficient for current implementation
        for syst in self.systematics:
            selected_jets[syst] = []
        #pre-select jets via fast list comprehension, eta and jet id requirements
        partial_jets = [j for j in enumerate(jets) if abs(j[1].eta) <= self.jet_max_eta and (j[1].jetId & self.jet_min_id) > 0]
        #Look at all systematic variations for jet pt, preferentially looking at the "Up" variations first
        for syst in sorted(self.systematics, key=lambda k: k.endswith("Up")):
            #append the idx and jet to tuples
            for idx, jet in partial_jets:
                if getattr(jet, "pt_{syst}".format(syst=syst)) >= self.jet_min_pt:
                    selected_jets[syst].append((idx, jet))
            #If at least one systematic variation has two selected jets, the event is kept via potentially-early return
            if len(selected_jets[syst]) >= self.jet_min_count:
                return True
        return False
                
    def getSystematics(self, event, exclude_raw=True):
        branches = event._tree._ttrvs.keys() + event._tree._ttras.keys() + event._tree._extrabranches.keys() + [bb.GetName() for bb in event._tree.GetListOfBranches()]
        return [x.split("_")[-1] for x in branches if x.startswith("Jet_") and "_pt_" in x and (not x.endswith("_raw") if exclude_raw else True)]
