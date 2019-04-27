from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from FourTopNAOD.Kai.tools.intools import *
import collections, copy, json
from array import array

def muonSelector(leptonCollection, nSelect=-1, idList=[], isoList=[], ptMinCut=[], dzMaxCut=[], returnObjects=False):
    finalMuons = []
    leptonLength = len(leptonCollection)
    return 0
    
def getMuonIdDecision(muon, selId="looseId"):
    if selId == "looseId":
        return 0
    

class SelTester(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt=None, isData=False, writeNtup=False):
        self.writeHistFile=True
        self.writingHistFile=False
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
        self.ntupName = 'nTuple'
        self.ntupTitle = 'nTuple containing a muon and 4 jets and MET'
        self.ntupVars = 'run:lumi:event:muon_pt:muon_eta:muon_phi:muon_mass:jet1_pt:jet1_eta:jet1_phi:jet1_DeepFlavB:jet2_pt:jet2_eta:jet2_phi:jet2_DeepFlavB:'\
                        'jet3_pt:jet3_eta:jet3_phi:jet3_DeepFlavB:jet4_pt:jet4_eta:jet4_phi:jet4_DeepFlavB:MET_pt:MET_phi:PUWeightCentral:'\
                        'PUWeightUp:PUWeightDown'

    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)
        if histFile and histDirName:
            self.writingHistFile = True
            self.ntup = ROOT.TNtuple(self.ntupName, self.ntupTitle, self.ntupVars)
            self.addObject(self.ntup)
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
        # if self.counter % 4 != 0:
        #     return False
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
            cent = 0.0
            up = 0.0
            down = 0.0

        if self.writingHistFile:
            self.h_PUDist["noReweight"].Fill(pileup.nTrueInt, 1.0)
            self.h_PUDist["noReweight_v_True"].Fill(pileup.nTrueInt, PV.npvs, 1.0)
            self.h_PUDist["Reweight"].Fill(pileup.nTrueInt, cent)
            self.h_PUDist["Reweight_v_True"].Fill(pileup.nTrueInt, PV.npvs, cent)
            self.h_PUDist["ReweightUp"].Fill(pileup.nTrueInt, up)
            self.h_PUDist["ReweightUp_v_True"].Fill(pileup.nTrueInt, PV.npvs, up)
            self.h_PUDist["ReweightDown"].Fill(pileup.nTrueInt, down)
            self.h_PUDist["ReweightDown_v_True"].Fill(pileup.nTrueInt, PV.npvs, down)

        foundMuon = False
        for muon in muons:
            if foundMuon: continue
            #skip muons of pt less than 25, outside the muon spectrometer acceptance, non-PFIsoTight (pfIsoId >= 4), and with dz > 0.02
            if abs(muon.eta) > 2.4 or muon.pt < 25 or muon.pfIsoId < 4 or muon.dz > 0.02: continue
            foundMuon = True
            theMuon = muon

        #Skip events without a good muon
        #if not foundMuon: return False

        foundJets = 0
        theJets = []
        for jidx, jet in enumerate(jets):
            #skip jets of pt less than 30, outside 2.4 eta, and with jetId less than TightLeptonVeto. Crossclean against theMuon if it exists
            if jet.pt < 30 or abs(jet.eta) > 2.4 or jet.jetId < 6: continue
            if foundMuon and theMuon.jetIdx == jidx: continue
            theJets.append(jet)

        if foundMuon:
            muonpt = theMuon.pt
            muoneta = theMuon.eta
            muonphi = theMuon.phi
            muonmass = theMuon.mass
        else:
            muonpt = 0.0
            muoneta = 0.0
            muonphi = 0.0
            muonmass = 0.0

        if len(theJets) > 0:
            jet1pt = theJets[0].pt
            jet1eta = theJets[0].eta
            jet1phi = theJets[0].phi
            jet1btag = theJets[0].btagDeepFlavB
        else:
            jet1pt = 0.0
            jet1eta = 0.0
            jet1phi = 0.0 
            jet1btag = 0.0

        if len(theJets) > 1:
            jet2pt = theJets[1].pt
            jet2eta = theJets[1].eta
            jet2phi = theJets[1].phi
            jet2btag = theJets[1].btagDeepFlavB
        else:
            jet2pt = 0.0
            jet2eta = 0.0
            jet2phi = 0.0 
            jet2btag = 0.0

        if len(theJets) > 2:
            jet3pt = theJets[2].pt
            jet3eta = theJets[2].eta
            jet3phi = theJets[2].phi
            jet3btag = theJets[2].btagDeepFlavB
        else:
            jet3pt = 0.0
            jet3eta = 0.0
            jet3phi = 0.0 
            jet3btag = 0.0

        if len(theJets) > 3:
            jet4pt = theJets[3].pt
            jet4eta = theJets[3].eta
            jet4phi = theJets[3].phi
            jet4btag = theJets[3].btagDeepFlavB
        else:
            jet4pt = 0.0
            jet4eta = 0.0
            jet4phi = 0.0 
            jet4btag = 0.0

        args = array('f', [event.run,
                           event.luminosityBlock,
                           event.event,
                           muonpt,
                           muoneta,
                           muonphi,
                           muonmass,
                           jet1pt,
                           jet1eta,
                           jet1phi,
                           jet1btag,
                           jet2pt,
                           jet2eta,
                           jet2phi,
                           jet2btag,
                           jet3pt,
                           jet3eta,
                           jet3phi,
                           jet3btag,
                           jet4pt,
                           jet4eta,
                           jet4phi,
                           jet4btag,
                           met.pt,
                           met.phi,
                           cent,
                           up,
                           down])
        if self.writingHistFile:
            self.ntup.Fill(args)   
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
files=["~/eos/AODStorage/TestingSamples/TTTT_TuneCP5_PSweights_102X.root"]
hName="testSel-TTTT.root"

#Default output
#files=["TTTT_TuneCP5_PSweights_102X_Skim.root"] 
#Uncompressed file
#files=["TTTT_TuneCP5_PSweights_102X_nocompression.root"]




#Configuration
writeNtuple = True
writeTree = False
writeCompressed = False

if writeNtuple:
    inHistFileName = hName
    inHistDirName = "plots"
else:
    inHistFileName = None
    inHistDirName = None
if writeTree:
    inNoOut = False
else:
    inNoOut = True
if writeCompressed:
#    inCompression = "LZMA:9"
#    inCompression = "ZLIB:9"
#    inCompression = "LZ4:9"
#    inCompression = "LZMA:3"
    inCompression = "ZLIB:3"
#    inCompression = "LZ4:3"
else:
    inCompression = "none"

modulecache = SelTester(maxevt=100000, writeNtup=writeNtuple)
p=PostProcessor(".",
                files,
                cut=None,
                #modules=[puWeightProducer("auto",pufile_data2017,"pu_mc","pileup",verbose=True),
                #modules=[puWeightProducer(pufile_mc2017,pufile_data2017,"pu_mc","pileup",verbose=True, doSysVar=True),
                modules=[modulecache],
                #modules=[],
                noOut=inNoOut,
                histFileName=inHistFileName,
                histDirName=inHistDirName,
                compression = inCompression,
                #postfix="postPURW"
                #justcount=True,
                )

p.run()
