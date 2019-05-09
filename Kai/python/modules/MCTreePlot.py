from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.intools import *
from FourTopNAOD.Kai.tools.mctree import *

class MCTreePlot(Module):
    def __init__(self, verbose=False, maxevt=-1, probEvt=None, filterNLeps=None):
        self.writeHistFile=True
        self.verbose=verbose
        self.probEvt = probEvt
        self.filterNLeps=filterNLeps
        if probEvt:
            #self.probEvt = probEvt
            self.verbose = True
        
        #Bits for status flag checking
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

        #event counters
        self.counter = 0
        self.maxEventsToProcess=maxevt

    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)
        
        ##########################
        ### MCTree Diagnostics ###
        ##########################
        # self.hTree_top_dau_count=ROOT.TH1F('hTree_top_dau_count',   'Count of Top Daughters',   5, 0, 5)
        # self.addObject(self.hTree_top_dau_count)
        # self.hTree_top_dau_pdg=ROOT.TH1F('hTree_top_dau_pdg',   'PdgId of Top Daughters',   10, 0, 10)
        # self.addObject(self.hTree_top_dau_pdg)
        # self.hTree_bfirst_dau_count=ROOT.TH1F('hTree_bfirst_dau_count',   'Count of first b Daughters',   25, 0, 25)
        # self.addObject(self.hTree_bfirst_dau_count)
        # self.hTree_bfirst_dau_pdg=ROOT.TH1F('hTree_bfirst_dau_pdg',   'PdgId of first b Daughters',   30, 0, 30)
        # self.addObject(self.hTree_bfirst_dau_pdg)
        # self.hTree_bfirst_isXCopy=ROOT.TH1F('hTree_bfirst_isXCopy',   'Flags for first b',   2, 0, 2)
        # self.addObject(self.hTree_bfirst_isXCopy)
        # self.hTree_blast_isXCopy=ROOT.TH1F('hTree_blast_isXCopy',   'Flags for last b',   2, 0, 2)
        # self.addObject(self.hTree_blast_isXCopy)
        # self.hTree_Wfirst_isXCopy=ROOT.TH1F('hTree_Wfirst_isXCopy',   'Flags for first W',   2, 0, 2)
        # self.addObject(self.hTree_Wfirst_isXCopy)
        # self.hTree_Wlast_isXCopy=ROOT.TH1F('hTree_Wlast_isXCopy',   'Flags for last W',   2, 0, 2)
        # self.addObject(self.hTree_Wlast_isXCopy)
        # self.hTree_Wlast_dau_count=ROOT.TH1F('hTree_Wlast_dau_count',   'Count of last W Boson Daughters',   5, 0, 5)
        # self.addObject(self.hTree_Wlast_dau_count)
        # self.hTree_Wlast_dau_pdg=ROOT.TH1F('hTree_Wlast_dau_pdg',   'PdgId of last W Boson Daughters',   26, 0, 26)
        # self.addObject(self.hTree_Wlast_dau_pdg)
        # self.hTree_WTauToL_dau_count=ROOT.TH1F('hTree_WTauToL_dau_count',   'Count of Tau To L(from W) Daughters',   15, 0, 15)
        # self.addObject(self.hTree_WTauToL_dau_count)
        # self.hTree_WTauToL_dau_pdg=ROOT.TH1F('hTree_WTauToL_dau_pdg',   'PdgId of Tau To L(from W) Daughters',   8, 0, 8)
        # self.addObject(self.hTree_WTauToL_dau_pdg)
        # self.hTree_WTauToQ_dau_count=ROOT.TH1F('hTree_WTauToQ_dau_count',   'Count of Tau To Q(from W) Daughters',   15, 0, 15)
        # self.addObject(self.hTree_WTauToQ_dau_count)
        # self.hTree_WTauToQ_dau_pdg=ROOT.TH1F('hTree_WTauToQ_dau_pdg',   'PdgId of Tau To Q(from W) Daughters',   8, 0, 8)
        # self.addObject(self.hTree_WTauToQ_dau_pdg)
        # self.hTree_hasHadronicTop_count=ROOT.TH1F('hTree_hasHadronicTop_count',   'Number of Hadronic top decays per event',   5, 0, 5)
        # self.addObject(self.hTree_hasHadronicTop_count)
        # self.hTree_WClassification=ROOT.TH1F('hTree_WClassification',   'hasHadronicW (W), hasTauIntermediate, hasHadronicTau',   6, 0, 6)
        # self.addObject(self.hTree_WClassification)
        # self.hTree_WTauClassification=ROOT.TH2F('hTree_WTauClassification',   'Classification of Tau (from W) Daughters ',   6, 0, 6, 10, 0, 10)
        # self.addObject(self.hTree_WTauClassification)
        # self.hScratch=ROOT.TH2F('hScratch',   'Scratch Space',   8, 0, 8, 6, 0, 6)
        # self.addObject(self.hScratch)
        # self.hTree_DeltaR=ROOT.TH2F('hTree_DeltaR',   'DeltaR plot for Jet types',   120, 0, 1.2, 6, 0, 6)
        # self.addObject(self.hTree_DeltaR)
        self.hTree_MuMuSpec=ROOT.TH2F('hTree_MuMuSpec',   'DiMuon Pt Spectra; Leading Muon; Sub-leading Muon',   70, 0, 350, 70, 0, 350)
        self.addObject(self.hTree_MuMuSpec)
        self.hTree_ElMuSpec=ROOT.TH2F('hTree_ElMuSpec',   'Electron - Muon Pt Spectra; Muon; Electron',   70, 0, 350, 70, 0, 350)
        self.addObject(self.hTree_ElMuSpec)
        self.hTree_ElElSpec=ROOT.TH2F('hTree_ElElSpec',   'DiElectron Pt Spectra; Leading Electron; Sub-leading Electron',   70, 0, 350, 70, 0, 350)
        self.addObject(self.hTree_ElElSpec)
        #self.hTree_MuPtId=ROOT.TH2F('hTree_MuPtId',   'Muon Pt-Boolean IDs; Muon; ID',   70, 0, 350, 15, 0, 15)
        #self.addObject(self.hTree_MuPtId)
        self.hTree_MuPtId={}
        self.hTree_TauToMuPtId={}
        self.hTree_MuIsoId={}
        self.hTree_TauToMuIsoId={}
        self.hTree_ElPtId={}
        self.hTree_TauToElPtId={}
        self.hTree_ElIsoId={}
        self.hTree_TauToElIsoId={}
        for i in xrange(4):
            self.hTree_MuPtId[i]={}
            self.hTree_ElPtId[i]={}
            self.hTree_TauToMuPtId[i]={}
            self.hTree_TauToElPtId[i]={}
            self.hTree_MuIsoId[i]={}
            self.hTree_ElIsoId[i]={}
            self.hTree_TauToMuIsoId[i]={}
            self.hTree_TauToElIsoId[i]={}
            for j in xrange(i+1):
                self.hTree_MuPtId[i][j]=ROOT.TH2F('hTree_MuPtId_{0:d}LepTop_Muon{1:d}'.format(i+1, j+1),
                                                  'ID tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton; Muon Pt; ID',
                                                  100, 0, 500, 10, 0, 10)
                self.hTree_ElPtId[i][j]=ROOT.TH2F('hTree_ElPtId_{0:d}LepTop_Electron{1:d}'.format(i+1, j+1),
                                                  'ID tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton; Electron Pt; ID',
                                                  100, 0, 500, 10, 0, 10)
                self.hTree_TauToMuPtId[i][j]=ROOT.TH2F('hTree_TauToMuPtId_{0:d}LepTop_Muon{1:d}'.format(i+1, j+1),
                                                  'ID tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton (via Tau); Muon Pt; ID',
                                                  100, 0, 500, 10, 0, 10)
                self.hTree_TauToElPtId[i][j]=ROOT.TH2F('hTree_TauToElPtId_{0:d}LepTop_Electron{1:d}'.format(i+1, j+1),
                                                  'ID tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton (via Tau); Electron Pt; ID',
                                                  100, 0, 500, 10, 0, 10)
                self.hTree_MuIsoId[i][j]=ROOT.TH2F('hTree_MuIsoId_{0:d}LepTop_Muon{1:d}'.format(i+1, j+1),
                                                  'Isolation tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton; Muon Pt; Iso ID',
                                                  100, 0, 500, 10, 0, 10)
                self.hTree_ElIsoId[i][j]=ROOT.TH2F('hTree_ElIsoId_{0:d}LepTop_Electron{1:d}'.format(i+1, j+1),
                                                  'Isolation tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading electron; Electron Pt; Iso ID',
                                                  100, 0, 500, 10, 0, 10)
                self.hTree_TauToMuIsoId[i][j]=ROOT.TH2F('hTree_TauToMuIsoId_{0:d}LepTop_Muon{1:d}'.format(i+1, j+1),
                                                  'Isolation tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton (via Tau); Muon Pt; Iso ID',
                                                  100, 0, 500, 10, 0, 10)
                self.hTree_TauToElIsoId[i][j]=ROOT.TH2F('hTree_TauToElIsoId_{0:d}LepTop_Electron{1:d}'.format(i+1, j+1),
                                                  'Isolation tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton (via Tau); Electron Pt; Iso ID',
                                                  100, 0, 500, 10, 0, 10)
                self.addObject(self.hTree_MuPtId[i][j])
                self.addObject(self.hTree_ElPtId[i][j])
                self.addObject(self.hTree_TauToMuPtId[i][j])
                self.addObject(self.hTree_TauToElPtId[i][j])
                self.addObject(self.hTree_MuIsoId[i][j])
                self.addObject(self.hTree_ElIsoId[i][j])
                self.addObject(self.hTree_TauToMuIsoId[i][j])
                self.addObject(self.hTree_TauToElIsoId[i][j])
                
        ### Direct top lepton decays (Muon/Electron) ###        
        self.hTree_MuPtDz=ROOT.TH3F('hTree_MuPtDz',   'Muon Pt-Dz; Muon; Dz; nJet',   100, 0, 500, 50, 0, 0.2, 15, 0, 15)
        self.addObject(self.hTree_MuPtDz)
        self.hTree_ElPtDz=ROOT.TH3F('hTree_ElPtDz',   'Electron Pt-Dz; Electron; Dz; nJet',   100, 0, 500, 50, 0, 0.2, 15, 0, 15)
        self.addObject(self.hTree_ElPtDz)
        self.hTree_MuIdIso=ROOT.TH3F('hTree_MuIdIso',   'Muon ID vs ISO; Muon ID; Muon ISO; nJet',   2, 0, 2, 2, 0, 2, 15, 0, 15)
        self.addObject(self.hTree_MuIdIso)
        self.hTree_ElIdIso=ROOT.TH3F('hTree_ElIdIso',   'Electron ID vs ISO; Electron ID; Electron ISO; nJet',   2, 0, 2, 2, 0, 2, 15, 0, 15)
        self.addObject(self.hTree_ElIdIso)
        self.hTree_MuPtIp3d=ROOT.TH3F('hTree_MuPtIp3d',   'Muon Pt-Ip3d; Muon; 3D Impact Parameter(cm); nJet',   100, 0, 500, 50, 0, 0.2, 15, 0, 15)
        self.addObject(self.hTree_MuPtIp3d)
        self.hTree_ElPtIp3d=ROOT.TH3F('hTree_ElPtIp3d',   'Electron Pt-Ip3d; Electron; 3D Impact Parameter(cm); nJet',   100, 0, 500, 50, 0, 0.2, 15, 0, 15)
        self.addObject(self.hTree_ElPtIp3d)
        
        ### W soft leptons (hadronization) ###
        self.hTree_WLepMuPtIp3d=ROOT.TH2F('hTree_WLepMuPtIp3d',   'Hadronic W Jet Muon Pt-Ip3d; Muon; 3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_WLepMuPtIp3d)
        self.hTree_WLepElPtIp3d=ROOT.TH2F('hTree_WLepElPtIp3d',   'Hadronic W Jet Electron Pt-Ip3d; Electron;3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_WLepElPtIp3d)
        self.hTree_WLepMuPtDz=ROOT.TH2F('hTree_WLepMuPtDz',   'Hadronic W Jet Muon Pt-Dz; Muon; Dz',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_WLepMuPtDz)
        self.hTree_WLepElPtDz=ROOT.TH2F('hTree_WLepElPtDz',   'Hadronic W Jet Electron Pt-Dz; Electron; Dz',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_WLepElPtDz)
        self.hTree_WLepMuIdIso=ROOT.TH2F('hTree_WLepMuIdIso',   'Hadronic W Jet Muon ID vs ISO; Muon ID; Muon ISO',   2, 0, 2, 2, 0, 2)
        self.addObject(self.hTree_WLepMuIdIso)
        self.hTree_WLepElIdIso=ROOT.TH2F('hTree_WLepElIdIso',   'Hadronic W Jet Electron ID vs ISO; Electron ID; Electron ISO',   2, 0, 2, 2, 0, 2)
        self.addObject(self.hTree_WLepElIdIso)
        
        
        ### b soft leptons (hadronization) ###
        self.hTree_bLepMuPtDz=ROOT.TH2F('hTree_bLepMuPtDz',   'b Jet Muon Pt-Dz; Muon; Dz',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_bLepMuPtDz)
        self.hTree_bLepElPtDz=ROOT.TH2F('hTree_bLepElPtDz',   'b Jet Electron Pt-Dz; Electron; Dz',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_bLepElPtDz)
        self.hTree_bLepMuPtIp3d=ROOT.TH2F('hTree_bLepMuPtIp3d',   'b Jet Muon Pt-Ip3d; Muon; 3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_bLepMuPtIp3d)
        self.hTree_bLepElPtIp3d=ROOT.TH2F('hTree_bLepElPtIp3d',   'b Jet Electron Pt-Ip3d; Electron;3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_bLepElPtIp3d)
        self.hTree_bLepMuIdIso=ROOT.TH2F('hTree_bLepMuIdIso',   'b Jet Muon ID vs ISO; Muon ID; Muon ISO',   2, 0, 2, 2, 0, 2)
        self.addObject(self.hTree_bLepMuIdIso)
        self.hTree_bLepElIdIso=ROOT.TH2F('hTree_bLepElIdIso',   'b Jet Electron ID vs ISO; Electron ID; Electron ISO',   2, 0, 2, 2, 0, 2)
        self.addObject(self.hTree_bLepElIdIso)
        self.hTree_bLepJetBtag=ROOT.TH2F('hTree_bLepJetBtag',   'b Jet B-tag with associated lepton; lepton Pt; Lepton Pt X Jet B-tag',   100, 0, 1, 2, 0, 2)
        self.addObject(self.hTree_bLepJetBtag)
        
        ### Tau Leptons ###
        self.hTree_TauToMuPtDz=ROOT.TH2F('hTree_TauToMuPtDz',   'Muon (via Tau) Pt-Dz; Muon; Dz',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_TauToMuPtDz)
        self.hTree_TauToElPtDz=ROOT.TH2F('hTree_TauToElPtDz',   'Electron (via Tau) Pt-Dz; Electron; Dz',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_TauToElPtDz)
        self.hTree_TauToMuPtIp3d=ROOT.TH2F('hTree_TauToMuPtIp3d',   'Muon (via Tau) Pt-Ip3d; Muon; 3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.4)
        self.addObject(self.hTree_TauToMuPtIp3d)
        self.hTree_TauToElPtIp3d=ROOT.TH2F('hTree_TauToElPtIp3d',   'Electron (via Tau) Pt-Ip3d; Electron; 3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.4)
        self.addObject(self.hTree_TauToElPtIp3d)
        self.hTree_TauToMuIdIso=ROOT.TH2F('hTree_TauToMuIdIso',   'Muon (via Tau) ID vs ISO; Muon ID; Muon ISO',   2, 0, 2, 2, 0, 2)
        self.addObject(self.hTree_TauToMuIdIso)
        self.hTree_TauToElIdIso=ROOT.TH2F('hTree_TauToElIdIso',   'Electron (via Tau) ID vs ISO; Electron ID; Electron ISO',   2, 0, 2, 2, 0, 2)
        self.addObject(self.hTree_TauToElIdIso)
        
        ### Jets ###
        self.hTree_tJets=ROOT.TH2F('hTree_tJets',   'Top Jets; Jet Type; N Jets',   2, 0, 2, 8, 0, 8)
        self.addObject(self.hTree_tJets)
        self.hTree_tbJets=ROOT.TH2F('hTree_tbJets',   'b Jets; Jet Type; N Jets',   2, 0, 2, 8, 0, 8)
        self.addObject(self.hTree_tbJets)
        self.hTree_tWDau1Jets=ROOT.TH2F('hTree_tWDau1Jets',   'W Daughter 1 Jets; Jet Type; N Jets',   2, 0, 2, 8, 0, 8)
        self.addObject(self.hTree_tWDau1Jets)
        self.hTree_tWDau2Jets=ROOT.TH2F('hTree_tWDau2Jets',   'W Daughter 2 Jets; Jet Type; N Jets',   2, 0, 2, 8, 0, 8)
        self.addObject(self.hTree_tWDau2Jets)

        ### Reco info ###
        # self.hTree_recoMu=ROOT.TH1F('hTree_recoMu', '

        self.hTree_nJets_new=ROOT.TH1F('hTree_nJets_new',   'nJets (pt > 20 && |eta| < 2.5 && tightId); nJets; events', 20, 0, 20)
        self.addObject(self.hTree_nJets_new)
        self.hTree_nJets_old=ROOT.TH1F('hTree_nJets_old',   'nJets ((pt > 30 || pt > 25 && Medium CSVv2) && |eta| < 2.5 && tightId); nJets; events', 20, 0, 20)
        self.addObject(self.hTree_nJets_old)
        self.hTree_nJets_oldDeepCSV=ROOT.TH1F('hTree_nJets_oldDeepCSV',   'nJets ((pt > 30 || pt > 25 && Medium DeepCSV) && |eta| < 2.5 && tightId); nJets; events', 20, 0, 20)
        self.addObject(self.hTree_nJets_oldDeepCSV)
        self.hTree_nJets_MCSVv2=ROOT.TH1F('hTree_MCSVv2',   'nJets (pt > 20 && |eta| < 2.5 && tightId && Medium CSVv2); nJets; events', 20, 0, 20)
        self.addObject(self.hTree_nJets_MCSVv2)
        self.hTree_nJets_MDeepCSV=ROOT.TH1F('hTree_MDeepCSV',   'nJets (pt > 20 && |eta| < 2.5 && tightId && Medium DeepCSV); nJets; events', 20, 0, 20)
        self.addObject(self.hTree_nJets_MDeepCSV)
        self.hTree_nJets_MDeepJet=ROOT.TH1F('hTree_MDeepJet',   'nJets (pt > 20 && |eta| < 2.5 && tightId && Medium DeepJet); nJets; events', 20, 0, 20)
        self.addObject(self.hTree_nJets_MDeepJet)
        self.hTree_nLeps=ROOT.TH1F('hTree_nLeps',   'number Leptonic Top Decays; number Leptonic Top Decays; events', 5, 0, 5)
        self.addObject(self.hTree_nLeps)
        
        #print("histfile=" + str(histFile) + " directoryname=" + str(histDirName))
        #if histFile != None and histDirName != None:
            #self.writeHistFile=True
            #prevdir = ROOT.gDirectory
            #self.histFile = histFile
            #self.histFile.cd()
            #self.dir = self.histFile.mkdir( histDirName )
            #prevdir.cd()
            #self.objs = []
            #if self.makeHistos:
                # self.h_jSel_map = ROOT.TH2F('h_jSel_map', ';Jet Eta;Jet Phi', 40, -2.5, 2.5, 20, -3.14, 3.14)
                # self.addObject(self.h_jSel_map)
                # self.MADEHistos=True
        
    def endJob(self):
        if hasattr(self, 'objs') and self.objs != None:
            prevdir = ROOT.gDirectory
            self.dir.cd()
            for obj in self.objs:
                obj.Write()
            prevdir.cd()
            if hasattr(self, 'histFile') and self.histFile != None: 
                self.histFile.Close()


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

        #Check whether this file is Data from Runs or Monte Carlo simulations
        self.isData = True
        if hasattr(event, "nGenPart") or hasattr(event, "nGenJet") or hasattr(event, "nGenJetAK8"):
            self.isData = False
        
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

        if not self.isData:
            gens = Collection(event, "GenPart")
            genjets = Collection(event, "GenJet")
            genfatjets = Collection(event, "GenJetAK8")
            gensubjets = Collection(event, "SubGenJetAK8")
            genmet = Object(event, "GenMET")
            generator = Object(event, "Generator")
            btagweight = Object(event, "btagWeight") #contains .CSVV2 and .DeepCSVB float weights
            #genweight = 
            #lhe = Object(event, "FIXME")
            #weights = FIXME
            #PSWeights = FIXME

        if hasattr(event, "nGenTop"):
            tops = Collection(event, "GenTop")

        nLeps = [top for top in tops if top.tIsLeptonic]
        if self.filterNLeps and len(nLeps) != self.filterNLeps:
            return False

        anyMus = set([top.PF_Muon for top in tops if top.PF_Muon > -1])
        anyEles = set([top.PF_Electron for top in tops if top.PF_Electron > -1])
        topMus = [top.PF_Muon for top in tops if top.PF_Muon > -1 and top.tHasWDauMuon]
        topEles = [top.PF_Electron for top in tops if top.PF_Electron > -1 and top.tHasWDauElectron]
        nJets = [jet for jet in jets if abs(jet.eta) < 2.5 and jet.jetId >= 6 and jet.muonIdx1 not in anyMus and jet.muonIdx2 not in anyMus and jet.electronIdx1 not in anyEles and jet.electronIdx2 not in anyEles]
        nJets_new = [jet for jet in nJets if jet.pt > 20]
        nJets_old = [jet for jet in nJets if jet.pt > 25]
        nJets_oldCSVv2 = [jet for jet in nJets_old if jet.pt > 30 or jet.btagCSVV2 > 0.8838]
        nJets_oldDeepCSV = [jet for jet in nJets_old if jet.pt > 30 or jet.btagDeepB > 0.4941]

        nJetsMCSVv2 = [jet for jet in nJets_new if jet.btagCSVV2 > 0.8838]
        nJetsMDeepCSV = [jet for jet in nJets_new if jet.btagDeepB > 0.4941]
        nJetsMDeepJet = [jet for jet in nJets_new if jet.btagDeepFlavB > 0.3033]
        
        # print("nMus = " + str(len(topMus)) + " nEles = " + str(len(topEles)) + " nJets = " + str(len(nJets)) + " nJets_old = " + str(len(nJets_old)))

        self.hTree_nLeps.Fill(len(nLeps))

        self.hTree_nJets_new.Fill(len(nJets_new))
        self.hTree_nJets_old.Fill(len(nJets_oldCSVv2))
        self.hTree_nJets_oldDeepCSV.Fill(len(nJets_oldDeepCSV))

        self.hTree_nJets_MCSVv2.Fill(len(nJetsMCSVv2))
        self.hTree_nJets_MDeepCSV.Fill(len(nJetsMDeepCSV))
        self.hTree_nJets_MDeepJet.Fill(len(nJetsMDeepJet))
        
        for mid in topMus:
            muon = muons[mid]
            self.hTree_MuPtDz.Fill(muon.pt, muon.dz, len(nJets))
            # self.hTree_MuIdIso
            self.hTree_MuPtIp3d.Fill(muon.pt, muon.ip3d, len(nJets))
        for eid in topEles:
            electron = electrons[eid]
            self.hTree_ElPtDz.Fill(electron.pt, electron.dz, len(nJets))
            # self.hTree_ElIdIso
            self.hTree_ElPtIp3d.Fill(electron.pt, electron.ip3d, len(nJets))

        return True
