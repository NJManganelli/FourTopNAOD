from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from FourTopNAOD.Kai.tools.intools import *
import collections, copy, json, math
from array import array
import multiprocessing


class TopSystemPt(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt=None, isData=False, writeNtup=False, wOpt=0):
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
        self.wOpt = wOpt
        self.bits = {'isPrompt':0b000000000000001,
                     'isDecayedLeptonHadron':0b000000000000010,
                     'isTauDecayProduct':0b000000000000100,
                     'isPromptTauDecaypprProduct':0b000000000001000,
                     'isDirectTauDecayProduct':0b000000000010000,
                     'isDirectPromptTauDecayProduct':0b000000000100000,
                     'isDirectHadronDecayProduct':0b000000001000000,
                     'isHardProcess':0b000000010000000,
                     'fromHardProcess':0b000000100000000,
                     'isHardProcessTauDecayProduct':0b000001000000000,
                     'isDirectHardProcessTauDecayProduct':0b000010000000000,
                     'fromHardProcessBeforeFSR':0b000100000000000,
                     'isFirstCopy':0b001000000000000,
                     'isLastCopy':0b010000000000000,
                     'isLastCopyBeforeFSR':0b100000000000000
                    }


    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)
        if histFile and histDirName:
            self.h_proc=ROOT.TH1I('h_proc', 'Initial pp interacting partons; interaction type; Events', 1, 0, 1)
            self.addObject(self.h_proc)
            self.h_bfcount=ROOT.TH1I('h_bfcount', 'Count of first b quarks in event; number of b quarks descended from top quarks; frequency', 10, 0, 10)
            self.addObject(self.h_bfcount)
            self.h_bfpcount=ROOT.TH1I('h_bfpcount', 'Count of first b quarks in event after pruning; number of b quarks descended from top quarks with sibling W; frequency', 10, 0, 10)
            self.addObject(self.h_bfpcount)
            self.h_Wfcount=ROOT.TH1I('h_Wfcount', 'Count of first W bosons in event; number of W bosons directly descended from top quarks; frequency', 10, 0, 10)
            self.addObject(self.h_Wfcount)
            self.h_TopSystemPt = {}
            self.h_bSystemCorr = {}
            self.h_bSystemCorrMom = {}
            for proc in ["qq", "gg", "All"]:
                self.h_TopSystemPt[proc] = {}
                self.h_bSystemCorr[proc] = {}
                self.h_bSystemCorrMom[proc] = {}
                for i in xrange(4):
                    self.h_TopSystemPt[proc][i]=ROOT.TH3F('h_TopSystemPt_{0:d}_{1:s}'.format(i+1, proc),   
                                                    'Top Sys Pt (R{0:d} t pt); Top_Pt (GeV); Bottom_Pt (GeV); W_Pt (GeV)'.format(i+1), 
                                                    50, 0, 1000, 200, 0, 1000, 200, 0, 1000)
                                                    #200, 0, 1000, 200, 0, 1000, 200, 0, 1000)
                    self.addObject(self.h_TopSystemPt[proc][i])       
                    self.h_bSystemCorr[proc][i]=ROOT.TH3F('h_bSystemCorr_{0:d}_{1:s}'.format(i+1, proc),   
                                                          'b Sys Correlations (R{0:d} t pt);|#eta_t - #eta_b|; Bottom_Pt (GeV); #Theta(t, b)'.format(i+1), 
                                                          100, 0, 4, 1000, 0, 1000, 100, 0, math.pi)
                    self.addObject(self.h_bSystemCorr[proc][i])       
                    self.h_bSystemCorrMom[proc][i]=ROOT.TH3F('h_bSystemCorrMom_{0:d}_{1:s}'.format(i+1, proc),   
                                                             'b Sys Correlations (R{0:d} t pt);|#eta_b|; Bottom_Pt (GeV); Bottom_P()'.format(i+1), 
                                                             100, 0, 4, 250, 0, 500, 250, 0, 500)
                    self.addObject(self.h_bSystemCorrMom[proc][i])       
    
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
        if self.wOpt == 0:
            weight = 1.0
        elif self.wOpt == 1:
            weight = getattr(event, "genWeight")
        elif self.wOpt == 2:
            weight = abs(getattr(event, "genWeight"))
        else:
            raise Exception("Invalid weight option")

        gens = Collection(event, "GenPart")
        # LHEP = Collection(event, "LHEPart")
        # theLHElist = "The LHE pdgIDs: "
        # for lhep in LHEP:
        #     theLHElist += str(lhep.pdgId) + "   "
        # print(theLHElist)
        # subproc = "The initial parton IDs:    {0:>5d}   {1:>5d}".format(gens[0].pdgId, gens[1].pdgId)
        subproc = ""
        for gen in [gens[0], gens[1]]:
            if abs(gens[0].pdgId) == 21:
                subproc += "g"
            elif abs(gens[0].pdgId) in set([1, 2, 3, 4, 5]):
                subproc += "q"
            else:
                subproc += "X"
        self.h_proc.Fill(subproc, 1.0)
        bs = [gen for gen in gens if abs(gen.pdgId) == 5]
        Ws = [gen for gen in gens if abs(gen.pdgId) == 24]
        WFirst = [gen for gen in Ws if gen.genPartIdxMother > -1 and abs(gens[gen.genPartIdxMother].pdgId) == 6]#.sort(key=lambda g : gens[g.genPartIdxMother].pt, reverse=True)
        bFirst = [gen for gen in bs if gen.genPartIdxMother > -1 and abs(gens[gen.genPartIdxMother].pdgId) == 6]#.sort(key=lambda g : gens[g.genPartIdxMother].pt, reverse=True)
        tops = set([gen.genPartIdxMother for gen in WFirst])
        self.h_bfcount.Fill(len(bFirst), weight)
        self.h_Wfcount.Fill(len(WFirst), weight)
        bFirst = [gen for gen in bFirst if gen.genPartIdxMother in tops]
        self.h_bfpcount.Fill(len(bFirst), weight)
        WFirst.sort(key=lambda g : gens[g.genPartIdxMother].pt, reverse=True)
        bFirst.sort(key=lambda g : gens[g.genPartIdxMother].pt, reverse=True)
        for i in xrange(len(WFirst)):
            b = bFirst[i]
            W = WFirst[i]
            t = gens[bFirst[i].genPartIdxMother]
            self.h_TopSystemPt[subproc][i].Fill(t.pt, b.pt, W.pt, weight)
            self.h_TopSystemPt["All"][i].Fill(t.pt, b.pt, W.pt, weight)
            # stats = ""
            # for flag, bits in self.bits.iteritems():
            #     if flag not in ['fromHardProcessBeforeFSR','isFirstCopy','isLastCopy','isLastCopyBeforeFSR']: continue
            #     if b.statusFlags & bits:
            #         stats += " " + flag
            b_mass = (t.p4() - W.p4()).M()
            t4 = t.p4()
            b4 = t.p4() - W.p4()
            self.h_bSystemCorrMom[subproc][i].Fill(abs(b.eta), b.pt, b4.P(), weight)            
            self.h_bSystemCorrMom["All"][i].Fill(abs(b.eta), b.pt, b4.P(), weight)            
            b4.Boost(-(t4.BoostVector()))
            cosTheta = (b4.Px()*t4.Px() + b4.Py()*t4.Py() + b4.Pz()*t4.Pz())/(b4.P() * t4.P())
            if cosTheta > 1:
                cosTheta = 1
            elif cosTheta < -1:
                cosTheta = -1
            self.h_bSystemCorr[subproc][i].Fill(abs(t.eta - b.eta), b.pt, abs(math.acos(cosTheta)), weight)            
            self.h_bSystemCorr["All"][i].Fill(abs(t.eta - b.eta), b.pt, abs(math.acos(cosTheta)), weight)            
            # print(cosTheta)
            #Boost to CoM, measure polar angle between unboosted top and b from CoM -> are there polarization effects?

        return True
Tuples = []
filesTTTT=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/BD738994-6BD2-6D41-9D93-E0AC468497A5.root"]
# files=["/eos/home-n/nmangane/AODStorage/TestingSamples/TTTT_TuneCP5_PSweights_102X.root"]
hNameTTTT="TopSysPtTTTTv5.root"
# hNameTTTTw="TopSysPtTTTTw.root"
# hNameTTTTabsw="TopSysPtTTTTabsw.root"
Tuples.append((filesTTTT, hNameTTTT, 0)) #Central test configuration, no weights
# Tuples.append((filesTTTT, hNameTTTTw, 1))
# Tuples.append((filesTTTT, hNameTTTTabsw, 2))

filesTT=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/80000/FB2C8D48-139E-7647-90C2-1CF1767DB0A1.root"]
hNameTT="TopSysPtTTv5.root"
# Tuples.append((filesTT, hNameTT, 0))
# filesTTGF=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/E565691C-17D4-6046-865E-8393F1FE0414.root"]
# hNameTTGF="TopSysPtTTGF.root"
# hNameTTGFw="TopSysPtTTGFw.root"
# hNameTTGFabsw="TopSysPtTTGFabsw.root"
# Tuples.append((filesTTGF, hNameTTGF, 0))
# Tuples.append((filesTTGF, hNameTTGFw, 1))
# Tuples.append((filesTTGF, hNameTTGFabsw, 2))

filesTT_MG=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTJets_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/79097697-485B-9542-8E6B-43A747EA7F4B.root"]
hNameTT_MG="TopSysPtTT_MGv5.root"
# Tuples.append((filesTT_MG, hNameTT_MG, 0))



def multiplier(fileList, hName=None, wOption=0):
    if hName == None:
        hDirName = None
    else:
        hDirName = "plots"

        p=PostProcessor(".",
                        fileList,
                        cut=None,
                        modules=[TopSystemPt(maxevt=100000, wOpt=wOption)],
                        # modules=[TopSystemPt(maxevt=100, wOpt=wOption)],
                        noOut=True,
                        histFileName=hName,
                        histDirName=hDirName,
                       )
        p.run()

pList = []
for tup in Tuples:
    p = multiprocessing.Process(target=multiplier, args=(tup[0], tup[1], tup[2]))
    pList.append(p)
    p.start()

for p in pList:
    p.join()
