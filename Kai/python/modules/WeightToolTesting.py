import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.intools import *
from FourTopNAOD.Kai.tools.mctree import *
import collections, copy, json

class WeightToolTester(Module):
    def __init__(self, verbose=False, makeHistos=False, maxevt=-1, probEvt=None, subname="DeFaUlT"):
        self.writeHistFile=True
        self.verbose=verbose
        self._verbose = verbose
        self.probEvt = probEvt
        if probEvt:
            #self.probEvt = probEvt
            self.verbose = True
        self.makeHistos = makeHistos
        self.subname = subname
        
        #event counters
        self.counter = 0
        self.maxEventsToProcess=maxevt

    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName+self.subname)
        self.h_PUDist = {}
        self.h_PUDist[self.subname]=ROOT.TH1F('h_PUDist_'+self.subname,   'Pileup Distribution ({0:s})'.format(self.subname),   200, 0, 200)
        self.h_PUDist[self.subname+'_v_True']=ROOT.TH2F('h_PUDist_'+self.subname+'_v_True',   'Pileup Distribution versus True Pileup ({0:s}); nPV - 1; True Pileup'.format(self.subname),   200, 0, 200, 200, 0, 200)
        self.addObject(self.h_PUDist[self.subname])
        self.addObject(self.h_PUDist[self.subname+'_v_True'])
        self.h_GenWeight = {}
        self.h_GenWeight[self.subname]=ROOT.TH1F('h_GenWeight_'+self.subname, 'Generator Weight ({0:s})'.format(self.subname), 200000, -0.100, 0.100)
        self.addObject(self.h_GenWeight[self.subname])
       

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
        
        self.h_PUDist[self.subname].Fill(PV.npvs)
        self.h_PUDist[self.subname+'_v_True'].Fill(pileup.nTrueInt, PV.npvs)
        self.h_GenWeight[self.subname].Fill(generator.weight)

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
