from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from FourTopNAOD.Kai.tools.intools import *
import collections, copy, json
from array import array


class TopSystemPt(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt=None, isData=False, writeNtup=False):
        self.writeHistFile=True
        self.verbose=verbose
        self._verbose = verbose
        self.probEvt = probEvt
        if probEvt:
            #self.probEvt = probEvt
            self.verbose = True        
        #event counters
        self.counter = 0
        self.maxEventsToProcess=maxevt

    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)
        if histFile and histDirName:
            self.h_bfcount=ROOT.TH1I('h_bfcount', 'Count of first b quarks in event; number of b quarks directly descended from top quarks; frequency', 10, 0, 10)
            self.addObject(self.h_bfcount)
            self.h_Wfcount=ROOT.TH1I('h_Wfcount', 'Count of first W bosons in event; number of W bosons directly descended from top quarks; frequency', 10, 0, 10)
            self.addObject(self.h_Wfcount)
            self.h_TopSystemPt = {}
            for i in xrange(4):
                self.h_TopSystemPt[i]=ROOT.TH3F('h_TopSystemPt_{0:d}'.format(i+1),   
                                                'Top Sys Pt (R{0:d} t pt); Top_Pt (GeV); Bottom_Pt (GeV); W_Pt (GeV)'.format(i+1), 
                                                200, 0, 1000, 200, 0, 1000, 200, 0, 1000)
                self.addObject(self.h_TopSystemPt[i])       

    def endJob(self):
        if hasattr(self, 'objs') and self.objs != None:
            prevdir = ROOT.gDirectory
            self.dir.cd()
            for obj in self.objs:
                obj.Write()
            prevdir.cd()
            if hasattr(self, 'histFile') and self.histFile != None : 
                self.histFile.Close()

    # def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    #     self.out = wrappedOutputTree

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #Increment counter and skip events past the maxEventsToProcess, if larger than -1
        self.counter +=1
        if -1 < self.maxEventsToProcess < self.counter:
            return False        
        if self.probEvt:
            if event.event != self.probEvt:
                print("Skipping...")
                return False
        
        ###############################################
        ### Collections and Objects and isData check###
        ###############################################

        gens = Collection(event, "GenPart")
        bs = [gen for gen in gens if abs(gen.pdgId) == 5]
        Ws = [gen for gen in gens if abs(gen.pdgId) == 24]
        bFirst = [gen for gen in bs if gen.genPartIdxMother > -1 and abs(gens[gen.genPartIdxMother].pdgId) == 6]#.sort(key=lambda g : gens[g.genPartIdxMother].pt, reverse=True)
        WFirst = [gen for gen in Ws if gen.genPartIdxMother > -1 and abs(gens[gen.genPartIdxMother].pdgId) == 6]#.sort(key=lambda g : gens[g.genPartIdxMother].pt, reverse=True)
        bFirst.sort(key=lambda g : gens[g.genPartIdxMother].pt, reverse=True)
        WFirst.sort(key=lambda g : gens[g.genPartIdxMother].pt, reverse=True)
        for i in xrange(len(WFirst)):
            b = bFirst[i]
            W = WFirst[i]
            t = gens[bFirst[i].genPartIdxMother]
            self.h_TopSystemPt[i].Fill(t.pt, b.pt, W.pt)

        self.h_bfcount.Fill(len(bFirst))
        self.h_Wfcount.Fill(len(WFirst))
        return True

files=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/BD738994-6BD2-6D41-9D93-E0AC468497A5.root"]
# files=["/eos/home-n/nmangane/AODStorage/TestingSamples/TTTT_TuneCP5_PSweights_102X.root"]
hName="TopSysPt.root"


#Configuration
writeNtuple = True

if writeNtuple:
    inHistFileName = hName
    inHistDirName = "plots"

modulecache = TopSystemPt(maxevt=-1)

p=PostProcessor(".",
                files,
                cut=None,
                modules=[modulecache],
                noOut=True,
                histFileName=inHistFileName,
                histDirName=inHistDirName,
                )

p.run()
