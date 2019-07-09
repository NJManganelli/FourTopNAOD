from __future__ import division, print_function
import os, sys
import collections, copy, json, math
import ROOT
import argparse
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from FourTopNAOD.Kai.tools.toolbox import * #includes getFiles
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='Test of alternative method of counting event weights that doesn\'t rely directly on postprocessor')
parser.add_argument('--stage', dest='stage', action='store', type=str,
                    help='analysis stage to be produced')
args = parser.parse_args()

class EventCounter(Module):
    def __init__(self, verbose=False, isData=False):
        # self.writeHistFile=True
        self.verbose=verbose
        #event counters
        self.nPositiveEvents = 0
        self.nNegativeEvents = 0
        self.nZeroEvents = 0
        self.nEvents = 0

    # def beginJob(self,histFile=None,histDirName=None):
    #     Module.beginJob(self,histFile,histDirName)
    
    def endJob(self):
        print("nEvents: {0}\t nPositivEvents: {1}\t nNegativeEvents: {2}\t nZeroEvents: {3}".format(
            self.nEvents, self.nPositiveEvents, self.nNegativeEvents, self.nZeroEvents)
        )
        Module.endJob(self)
        

    # def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    #     self.out = wrappedOutputTree

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        if event.genWeight > 0: self.nPositiveEvents += 1
        elif event.genWeight < 0: self.nNegativeEvents += 1
        else: self.nZeroEvents += 1
        self.nEvents += 1
        return True

if args.stage == '1':
    fileList = getFiles(query="dbs:/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM", redir="root://cms-xrd-global.cern.ch/")
    stage1=PostProcessor("/tmp/nmangane",
                         fileList,
                         modules=[],
                         noOut=False,
                         branchsel='kdAltNegPosCount.txt',
                         outputbranchsel='kdAltNegPosCount.txt',
                         maxEntries=None,
                         firstEntry=0,
                         prefetch=False,
                         longTermCache=False,
                         haddFileName="ttttAltNegPostCount.root"
    )
    stage1.run()

if args.stage == '2':
    print("Not yet implemented")
    stage2=PostProcessor(".",
                         ["ttttAltNegPostCount.root"],
                         modules=[EventCounter()],
                         noOut=True,
                         # branchsel='keepdrop.txt',
                         maxEntries=None,
                         firstEntry=0,
                         prefetch=False,
                         longTermCache=False,
            )
    stage2.run()
