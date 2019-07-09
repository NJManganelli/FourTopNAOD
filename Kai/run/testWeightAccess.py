from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from FourTopNAOD.Kai.tools.toolbox import *
import collections, copy, json, math
from array import array
import multiprocessing
import inspect


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
        self.weightcounter = [0, 0]
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
        print("Negative weights: {0:d}\t All Weights: {1:d}".format(self.weightcounter[0], self.weightcounter[1]))
        print("Fraction of negative weights: {0:f}".format(self.weightcounter[0]/self.weightcounter[1]))
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
        LHEWeight = getattr(event, "LHEWeight_originalXWGTUP")
        # PSWeights = getattr(event, "PSWeight")
        # LHEScaleWeights = getattr(event, "LHEScaleWeight")
        # LHEPdfWeights = getattr(event, "LHEPdfWeight")
        # These weights are accessible...
        # print(LHEPdfWeights[0])
        # print(LHEPdfWeights[32])
        # print("LHEPdfWeight[3]:" + str(event._tree.LHEPdfWeight[3]))
        # print("PSWeight[3]:" + str(event._tree.PSWeight[3]))
        # event._tree.GetEntry(self.counter-1)
        # print("After setting GetEntry, LHEPdfWeight[3]:" + str(event._tree.LHEPdfWeight[3]))
        # print("After setting GetEntry, PSWeight[3]:" + str(event._tree.PSWeight[3]))
        # print("After setting GetEntry, LHEScaleWeight[3]:" + str(event._tree.LHEScaleWeight[3]))
        # print("Using getattr() method, LHEPdfWeight[3]:" + str(getattr(event,"LHEPdfWeight")[3]))
        # print("Using getattr() method, PSWeight[3]:" + str(getattr(event, "PSWeight")[3]))
        # print("Using getattr() method, LHEScaleWeight[3]:" + str(getattr(event, "LHEScaleWeight")[3]))
        centralweight = weight/abs(LHEWeight)
        if self.counter < 5:
            print("Central Weight: {0:f}".format(centralweight))
            print("PSWeights:")
            for i in xrange(getattr(event, "nPSWeight")):
                print("\t{0:f}".format(getattr(event, "PSWeight")[i]))
            print("LHEPdfWeights:")
            for i in xrange(getattr(event, "nLHEPdfWeight")):
                print("\t{0:f}".format(getattr(event, "LHEPdfWeight")[i]))
            print("LHEScaleWeights:")
            for i in xrange(getattr(event, "nLHEScaleWeight")):
                print("\t{0:f}".format(getattr(event, "LHEScaleWeight")[i]))

        self.weightcounter[1] += 1
        if centralweight < 0:
            self.weightcounter[0] += 1


        # print("PSWeights: number = {0:d} type = {1}".format(getattr(event, "nPSWeight"), type(PSWeights)))
        # print(type(LHEScaleWeights))
        # print("LHEScaleWeights: number = {0:d} type = {1}".format(getattr(event, "nLHEScaleWeight"), type(LHEScaleWeights)))
        # print(type(LHEPdfWeights))
        # print("LHEPdfWeights: number = {0:d} type = {1}".format(getattr(event, "nLHEPdfWeight"), type(LHEPdfWeights)))
        # print(PSWeights[0])
        # print(LHEScaleWeights[0])


        for i in xrange(getattr(event, "nPSWeight")):
            pass
            # print("PSWeight[{0:d}]: {1:f}".format(i, PSWeights[i]))
            # print("PSWeight[{1:d}]: {0:f}".format((psw/LHEWeight), i))
        # for i, lsw in enumerate(LHEScaleWeights):
        #     pass
        #     # print("LHEScaleWeight[{1:d}]: {0:f}".format((lsw/LHEWeight), i))
        # for i, lpw in enumerate(LHEPdfWeights):
        #     pass
        #     # print("LHEPdfWeight[{1:d}]: {0:f}".format((lpw/LHEWeight), i))


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

filesNAODv5=["root://cms-xrd-global.cern.ch//store/mc/RunIIAutumn18NanoAODv5/GluGluToBulkGravitonToHHTo2B2Tau_M-450_narrow_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/Nano1June2019_102X_upgrade2018_realistic_v19-v1/120000/BDC075B0-A628-DB49-AEFC-36FA1A23E5C4.root"]
hNameNAODv5="TopSysPtNAODv5.root"
# Tuples.append((filesNAODv5, hNameNAODv5, 1))

# filesTTTT=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/BD738994-6BD2-6D41-9D93-E0AC468497A5.root"]
# filesTTTT=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/89A33910-2A54-F949-868C-CB068F613229.root"]
filesTTTT=["../crab/Stage_0_to_1/crab_20190620_1021/crab_tttt_2017/results/tree_1.root",
           "../crab/Stage_0_to_1/crab_20190620_1021/crab_tttt_2017/results/tree_2.root",
           "../crab/Stage_0_to_1/crab_20190620_1021/crab_tttt_2017/results/tree_3.root",
           "../crab/Stage_0_to_1/crab_20190620_1021/crab_tttt_2017/results/tree_4.root",
           "../crab/Stage_0_to_1/crab_20190620_1021/crab_tttt_2017/results/tree_5.root",
           "../crab/Stage_0_to_1/crab_20190620_1021/crab_tttt_2017/results/tree_6.root"]
# files=["/eos/home-n/nmangane/AODStorage/TestingSamples/TTTT_TuneCP5_PSweights_102X.root"]
hNameTTTT="TopSysPtTTTTv5.root"
hNameTTTTw="TopSysPtTTTTv6w.root"
hNameTTTTabsw="TopSysPtTTTTv5absw.root"
# Tuples.append((filesTTTT, hNameTTTT, 0)) #Central test configuration, no weights
Tuples.append((filesTTTT, hNameTTTTw, 1))
# Tuples.append((filesTTTT, hNameTTTTabsw, 2))

filesTTTTRaw=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/BD738994-6BD2-6D41-9D93-E0AC468497A5.root",
              "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/BAE5B739-9EFE-CD4C-B9D9-770F8DCCCB74.root",
              "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/A2E4F2CE-364B-8A48-BF97-741B7F10B88A.root",
              "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/9D7C479D-84CE-9A47-BCCE-6A88AC31A1D7.root",
              "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/36126C94-981C-1542-88E8-AA275957EF92.root",
              "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/35515832-D9A1-4644-8A38-FA658307DDE9.root"]
hNameTTTTRaw="TopSySPtTTTTRawv6w.root"
Tuples.append((filesTTTTRaw, hNameTTTTRaw, 1))

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
                        modules=[TopSystemPt(maxevt=-1, wOpt=wOption)],
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
