from __future__ import division, print_function
import ROOT
import math
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
# from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
# from FourTopNAOD.Kai.tools.toolbox import *
#cutstring = "METFixEE2017 > 40 && ESV_JetMETLogic_nJet_baseline > 3 &&  ESV_JetMETLogic_HT_baseline > 450"
class WeightInserter(Module):
    def __init__(self, isData=True, weightMagnitude=1):
                 # genEquivalentLuminosity=1, genXS=1, genNEvents=1, genSumWeights=1, era="2017", btagging=['DeepCSV','M'], lepPt=25,  GenTop_LepSelection=None):
        """Class to insert the cross-section weight into each event, permitting combinations of backgrounds for faster testing.

        Formula = lumi * processCrossSection * genWeight/Sum(genWeights_processed) where the denominator is stored in the Runs tree as genEventSumw.
        weightMagnitude = lumi * processCrossSection / Sum(genWeights_processed)"""

        self.writeHistFile=True #Allow other modules to fill histograms
        self.fillHists = fillHists
        # if self.fillHists and not self.writeHistFile:
        #     self.writeHistFile=True
        self.isData = isData
        self.weightMagnitude = weightMagnitude
        # self.era = era

    def beginJob(self, histFile=None,histDirName=None):
        if self.fillHists == False and self.writehistFile == False:
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



    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.branchList = inputTree.GetListOfBranches()
        self.out = wrappedOutputTree
        self.varTuple = [('XSWeight', 'D', 'The cross section weight as calculated using WeightInserter PP Module', None),]
        if self.isData:
            self.XSweight = self.dataWeightFunc
        elif "genWeight" not in self.branchList:
            self.XSweight = self.backupWeightFunc
            print("Warning in WeightInserter: expected branch genWeight to be present, but it is not."\
                  "The weight magnitude indicated will be used, but the sign of the genWeight must be assumed positive!")
        else:
            self.XSweight = self.genWeightFunc

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        self.counter +=1
        ###############################################
        ### Collections and Objects and isData check###
        ###############################################        

        weight = self.XSweight(event) # * PU weight, L1Prefiring weight, etc.

        ####################################
        ### Variables for branch filling ###
        ####################################
        branchVals = {}
        branchVals['XSWeight'] = weight

        ########################## 
        ### Write out branches ###
        ##########################         
        if self.out:
            for name, valType, valTitle, lVar in self.varTuple:
                self.out.fillBranch(name, branchVals[name])
            return True
        else:
            return True

    def genWeightFunc(self, event):
        #Default value is currently useless, since the tree reader array tool raises an exception anyway
        return getattr(event, "genWeight") * self.weightMagnitude
    def backupWeightFunc(self, event):
        return self.weightMagnitude
    def dataWeightFunc(self, event):
        return 1
