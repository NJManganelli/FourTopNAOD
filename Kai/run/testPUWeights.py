from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.intools import *
from FourTopNAOD.Kai.tools.mctree import *
import collections, copy, json

def muonSelector(leptonCollection, nSelect=-1, idList=[], isoList=[], ptMinCut=[], dzMaxCut=[], returnObjects=False):
    finalMuons = []
    leptonLength = len(leptonCollection)
    return 0
    
def getMuonIdDecision(muon, selId="looseId"):
    if selId == "looseId":
        return 0
    

class PUTester(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt=None, isData=False):
        self.writeHistFile=True
        self.verbose=verbose
        self._verbose = verbose
        self.probEvt = probEvt
        if probEvt:
            #self.probEvt = probEvt
            self.verbose = True
        self.subnames = ["noReweight", "Reweight", "ReweightUp", "ReweightDown"]
        
        #event counters
        self.counter = 0
        self.maxEventsToProcess=maxevt

    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)
        self.h_PUDist = {}
        for subname in self.subnames:
            self.h_PUDist[subname]=ROOT.TH1F('h_PUDist_'+subname,   'Pileup Distribution ({0:s})'.format(subname),   200, 0, 200)
            self.h_PUDist[subname+'_v_True']=ROOT.TH2F('h_PUDist_'+subname+'_v_True',   'Pileup Distribution versus True Pileup ({0:s}); npvs; True Pileup'.format(subname),   200, 0, 200, 200, 0, 200)
            self.addObject(self.h_PUDist[subname])
            self.addObject(self.h_PUDist[subname+'_v_True'])
       

    def endJob(self):
        if hasattr(self, 'objs') and self.objs != None:
            prevdir = ROOT.gDirectory
            self.dir.cd()
            for obj in self.objs:
                obj.Write()
            prevdir.cd()
            if hasattr(self, 'histFile') and self.histFile != None : 
                self.histFile.Close()

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #Increment counter and skip events past the maxEventsToProcess, if larger than -1
        self.counter +=1
        # if -1 < self.maxEventsToProcess < self.counter:
        #     return False
        if -1 < self.maxEventsToProcess < self.counter:
            return False
        # if (self.counter % 5000) == 0:
        #     print("Processed {0:2d} Events".format(self.counter))
        
        if self.probEvt:
            if event.event != self.probEvt:
                print("Skipping...")
                return False
        
        ###############################################
        ### Collections and Objects and isData check###
        ###############################################

        #Check whether this file is Data from Runs or Monte Carlo simulations
        self.isData = True
        if hasattr(event, "nGenPart") or hasattr(event, "nGenJet") or hasattr(event, "nGenJetAK8"):
            self.isData = False
        if self.isData:
            #Do nothing, it's the data
            return True
        
        PV = Object(event, "PV")
        otherPV = Collection(event, "OtherPV")
        SV = Collection(event, "SV")
        
        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        taus = Collection(event, "Tau")
        jets = Collection(event, "Jet")
        fatjets = Collection(event, "FatJet")
        subjets = Collection(event, "SubJet")
        #met = Object(event, "MET")
        met = Object(event, "METFixEE2017") #FIXME: Placeholder until passed in via configuration?

        HLT = Object(event, "HLT")
        Filters = Object(event, "Flag") #For Data use only

        gens = Collection(event, "GenPart")
        genjets = Collection(event, "GenJet")
        genfatjets = Collection(event, "GenJetAK8")
        gensubjets = Collection(event, "SubGenJetAK8")
        genmet = Object(event, "GenMET")
        generator = Object(event, "Generator")
        btagweight = Object(event, "btagWeight") #contains .CSVV2 and .DeepCSVB float weights
        pileup = Object(event, "Pileup")
        #genweight = 
        #lhe = Object(event, "FIXME")
        #weights = FIXME
        #PSWeights = FIXME
        
        if hasattr(event, "puWeight"):
            cent = getattr(event, "puWeight")
            up = getattr(event, "puWeightUp")
            down = getattr(event, "puWeightDown")
        else:
            return False

        self.h_PUDist["noReweight"].Fill(pileup.nTrueInt, 1.0)
        self.h_PUDist["noReweight_v_True"].Fill(pileup.nTrueInt, PV.npvs, 1.0)
        self.h_PUDist["Reweight"].Fill(pileup.nTrueInt, cent)
        self.h_PUDist["Reweight_v_True"].Fill(pileup.nTrueInt, PV.npvs, cent)
        self.h_PUDist["ReweightUp"].Fill(pileup.nTrueInt, up)
        self.h_PUDist["ReweightUp_v_True"].Fill(pileup.nTrueInt, PV.npvs, up)
        self.h_PUDist["ReweightDown"].Fill(pileup.nTrueInt, down)
        self.h_PUDist["ReweightDown_v_True"].Fill(pileup.nTrueInt, PV.npvs, down)

        ##################################
        ### Print info for exploration ###
        ##################################

        #print("Gen Weight: " + str(generator.weight))
        verbose=False
        #print("\n\n\nRun: " + str(event.run) + " Lumi: " + str(event.luminosityBlock) + " Event: "
        #      + str(event.event) + " TTBarID: " + str(event.genTtbarId))

        if(verbose):
            print(strGenerator(generator))
            print(strBtagWeight(btagweight))

            
        if(verbose):
            print("\n\n==========Here be thy Muons==========")
            for nm, muon in enumerate(muons):
                print("Idx: {0:<5d}".format(nm) + " " + strMuon(muon))
            print("\n\n==========Here be thy Electrons==========")
            for ne, electron in enumerate(electrons):
                print("Idx: {0:<5d}".format(ne) + " " + strElectron(electron))
        if(verbose):
            print("\n\n==========Here be thy jets==========")
            print("=====Jets=====")
            for nj, jet in enumerate(jets):
                print("Idx: {0:<5d}".format(nj) + " " + strJet(jet))
            print("=====Gen Jets=====")
            for ngj, genjet in enumerate(genjets):
                print("Idx: {0:<5d}".format(ngj) + " " + strGenJet(genjet))
                
        if(verbose):
            print("\n\n==========Here be thy fatjets==========")
            #print("=====Fatjets=====\n{0:<5s} {1:<10s} {2:<10s} {3:<10s} {4:<5s} {5:<10s}".format("IdX", "pt", "eta", "phi","jID", "TvsQCD"))
            print("\n=====Fatjets=====")
            for nfj, jet in enumerate(fatjets):
                print("Idx: {0:<5d}".format(nfj) + " " + strFatJet(jet))
            #print("=====Gen Fatjets=====\n{0:<5s} {1:<10s} {2:<10s} {3:<10s} {4:<10s} {5:<10s}".format("IdX", "pt", "eta", "phi","Had Flav", "Part Flav"))
            print("\n=====Gen Fatjets=====")
            for ngfj, genjet in enumerate(genfatjets):
                print("Idx: {0:<5d}".format(ngfj) + " " + strGenJetAK8(genjet))
        if(self.verbose):
        #if(True):
            print("\n\n==========Here be thy GenParts==========")
            print("=====Gen Particles=====\n{0:>5s} {1:>10s} {2:>10s} {3:>10s} {4:>10s} {5:10s} {6:>10s} {7:>20s}"
              .format("IdX", "pt", "eta", "phi","Moth ID", "PDG ID", "Status", "Stat. Flgs"))
            for np, gen in enumerate(gens):
                #print("{0:>5d} {1:>10.4f} {2:>10.4f} {3:>10.4f} {4:>10d} {5:>10d} {6:>10d} {7:>20b}".format(np, gen.pt, gen.eta, gen.phi, gen.genPartIdxMother, gen.pdgId, gen.status, gen.statusFlags))
                print("Idx: {0:<5d}".format(np) + " " + strGenPart(gen))
                #print(getHadFlav(gen.pdgId))
        if(verbose):
            for np, gen in enumerate(gens):
                print("{0:<3d}".format(np) + " " + strGenPart(gen))
   
        return True

#No HLT applied, samples
#files=["~/eos/AODStorage/TestingSamples/TTJets_TuneCP5_amcatnloFXFX_102X.root"]
#hName="WTT-TTJets.root"
#files=["~/eos/AODStorage/TestingSamples/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_102X.root"]
#hName="WTT-TT2LGF.root"
#files=["~/eos/AODStorage/TestingSamples/TTTo2L2Nu_TuneCP5_PSweights_102X.root"]
#hName="WTT-TT2L.root"
#files=["~/eos/AODStorage/TestingSamples/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_102X.root"]
#hName="WTT-TT1LGF.root"
#files=["~/eos/AODStorage/TestingSamples/ttHTobb_TuneCP5_102X.root"]
#hName="WTT-TTH.root"
#files=["~/eos/AODStorage/TestingSamples/TTTT_TuneCP5_PSweights_102X.root"]
files=["TTTT_TuneCP5_PSweights_102X_Skim.root"]
hName="testPU-TTTT.root"

p=PostProcessor(".",
                files,
                cut=None,
                modules=[PUTester(maxevt=1000000)],
                noOut=True,
                histFileName=hName,
                histDirName="plots",
                #postfix="postPURW"
                #justcount=True,
                )

p.run()
