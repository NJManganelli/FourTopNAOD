from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #DeltaR, match collection methods
from FourTopNAOD.Kai.tools.intools import *
from FourTopNAOD.Kai.tools.mctree import *
import collections, copy, json

class MCTruth(Module):
    def __init__(self, verbose=False, makeHistos=False, maxevt=-1, probEvt=None):
        self.writeHistFile=True
        self.verbose=verbose
        self._verbose = verbose
        self.probEvt = probEvt
        if probEvt:
            #self.probEvt = probEvt
            self.verbose = True
        self.MADEHistos=False
        self.matchAK4counters = [0, 0, 0, 0, 0, 0, 0, 0]
        self.makeHistos = makeHistos
        
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
        self.h_top_dau_count=ROOT.TH1F('h_top_dau_count',   'Count of Top Daughters',   5, 0, 5)
        self.addObject(self.h_top_dau_count)
        self.h_top_dau_pdg=ROOT.TH1F('h_top_dau_pdg',   'PdgId of Top Daughters',   10, 0, 10)
        self.addObject(self.h_top_dau_pdg)
        self.h_bfirst_dau_count=ROOT.TH1F('h_bfirst_dau_count',   'Count of first b Daughters',   25, 0, 25)
        self.addObject(self.h_bfirst_dau_count)
        self.h_bfirst_dau_pdg=ROOT.TH1F('h_bfirst_dau_pdg',   'PdgId of first b Daughters',   30, 0, 30)
        self.addObject(self.h_bfirst_dau_pdg)
        self.h_bfirst_isFirstCopy=ROOT.TH1F('h_bfirst_isFirstCopy',   'isFirstCopy flag for first b',   2, 0, 2)
        self.addObject(self.h_bfirst_isFirstCopy)
        self.h_blast_isLastCopy=ROOT.TH1F('h_blast_isLastCopy',   'isLastCopy flag for last b',   2, 0, 2)
        self.addObject(self.h_blast_isLastCopy)
        self.h_Wfirst_isFirstCopy=ROOT.TH1F('h_Wfirst_isFirstCopy',   'isFirstCopy flag for first W',   2, 0, 2)
        self.addObject(self.h_Wfirst_isFirstCopy)
        self.h_Wfirst_isLastBeforeFSR=ROOT.TH1F('h_Wfirst_isLastBeforeFSR',   'isLastBeforeFSR flag for first W',   2, 0, 2)
        self.addObject(self.h_Wfirst_isLastBeforeFSR)
        self.h_Wlast_isLastCopy=ROOT.TH1F('h_Wlast_isLastCopy',   'isLastCopy flag for last W',   2, 0, 2)
        self.addObject(self.h_Wlast_isLastCopy)
        self.h_Wlast_isLastBeforeFSR=ROOT.TH1F('h_Wlast_isLastBeforeFSR',   'isLastBeforeFSR flag for last W',   2, 0, 2)
        self.addObject(self.h_Wlast_isLastBeforeFSR)
        self.h_Wlast_dau_count=ROOT.TH1F('h_Wlast_dau_count',   'Count of last W Boson Daughters',   5, 0, 5)
        self.addObject(self.h_Wlast_dau_count)
        self.h_Wlast_dau_pdg=ROOT.TH1F('h_Wlast_dau_pdg',   'PdgId of last W Boson Daughters',   26, 0, 26)
        self.addObject(self.h_Wlast_dau_pdg)
        self.h_WTauToL_dau_count=ROOT.TH1F('h_WTauToL_dau_count',   'Count of Tau To L(from W) Daughters',   15, 0, 15)
        self.addObject(self.h_WTauToL_dau_count)
        self.h_WTauToL_dau_pdg=ROOT.TH1F('h_WTauToL_dau_pdg',   'PdgId of Tau To L(from W) Daughters',   8, 0, 8)
        self.addObject(self.h_WTauToL_dau_pdg)
        self.h_WTauToQ_dau_count=ROOT.TH1F('h_WTauToQ_dau_count',   'Count of Tau To Q(from W) Daughters',   15, 0, 15)
        self.addObject(self.h_WTauToQ_dau_count)
        self.h_WTauToQ_dau_pdg=ROOT.TH1F('h_WTauToQ_dau_pdg',   'PdgId of Tau To Q(from W) Daughters',   8, 0, 8)
        self.addObject(self.h_WTauToQ_dau_pdg)
        self.h_hasHadronicW_count=ROOT.TH1F('h_hasHadronicW_count',   'Number of Hadronic top decays per event',   5, 0, 5)
        self.addObject(self.h_hasHadronicW_count)
        self.h_WClassification=ROOT.TH1F('h_WClassification',   'hasHadronicW (W), hasTauIntermediate, hasHadronicTau',   6, 0, 6)
        self.addObject(self.h_WClassification)
        
        
        ##########################
        ### MCTree Diagnostics ###
        ##########################
        self.hTree_top_dau_count=ROOT.TH1F('hTree_top_dau_count',   'Count of Top Daughters',   5, 0, 5)
        self.addObject(self.hTree_top_dau_count)
        self.hTree_top_dau_pdg=ROOT.TH1F('hTree_top_dau_pdg',   'PdgId of Top Daughters',   10, 0, 10)
        self.addObject(self.hTree_top_dau_pdg)
        self.hTree_bfirst_dau_count=ROOT.TH1F('hTree_bfirst_dau_count',   'Count of first b Daughters',   25, 0, 25)
        self.addObject(self.hTree_bfirst_dau_count)
        self.hTree_bfirst_dau_pdg=ROOT.TH1F('hTree_bfirst_dau_pdg',   'PdgId of first b Daughters',   30, 0, 30)
        self.addObject(self.hTree_bfirst_dau_pdg)
        self.hTree_bfirst_isXCopy=ROOT.TH1F('hTree_bfirst_isXCopy',   'Flags for first b',   2, 0, 2)
        self.addObject(self.hTree_bfirst_isXCopy)
        self.hTree_blast_isXCopy=ROOT.TH1F('hTree_blast_isXCopy',   'Flags for last b',   2, 0, 2)
        self.addObject(self.hTree_blast_isXCopy)
        self.hTree_Wfirst_isXCopy=ROOT.TH1F('hTree_Wfirst_isXCopy',   'Flags for first W',   2, 0, 2)
        self.addObject(self.hTree_Wfirst_isXCopy)
        self.hTree_Wlast_isXCopy=ROOT.TH1F('hTree_Wlast_isXCopy',   'Flags for last W',   2, 0, 2)
        self.addObject(self.hTree_Wlast_isXCopy)
        self.hTree_Wlast_dau_count=ROOT.TH1F('hTree_Wlast_dau_count',   'Count of last W Boson Daughters',   5, 0, 5)
        self.addObject(self.hTree_Wlast_dau_count)
        self.hTree_Wlast_dau_pdg=ROOT.TH1F('hTree_Wlast_dau_pdg',   'PdgId of last W Boson Daughters',   26, 0, 26)
        self.addObject(self.hTree_Wlast_dau_pdg)
        self.hTree_WTauToL_dau_count=ROOT.TH1F('hTree_WTauToL_dau_count',   'Count of Tau To L(from W) Daughters',   15, 0, 15)
        self.addObject(self.hTree_WTauToL_dau_count)
        self.hTree_WTauToL_dau_pdg=ROOT.TH1F('hTree_WTauToL_dau_pdg',   'PdgId of Tau To L(from W) Daughters',   8, 0, 8)
        self.addObject(self.hTree_WTauToL_dau_pdg)
        self.hTree_WTauToQ_dau_count=ROOT.TH1F('hTree_WTauToQ_dau_count',   'Count of Tau To Q(from W) Daughters',   15, 0, 15)
        self.addObject(self.hTree_WTauToQ_dau_count)
        self.hTree_WTauToQ_dau_pdg=ROOT.TH1F('hTree_WTauToQ_dau_pdg',   'PdgId of Tau To Q(from W) Daughters',   8, 0, 8)
        self.addObject(self.hTree_WTauToQ_dau_pdg)
        self.hTree_hasHadronicTop_count=ROOT.TH1F('hTree_hasHadronicTop_count',   'Number of Hadronic top decays per event',   5, 0, 5)
        self.addObject(self.hTree_hasHadronicTop_count)
        self.hTree_WClassification=ROOT.TH1F('hTree_WClassification',   'hasHadronicW (W), hasTauIntermediate, hasHadronicTau',   6, 0, 6)
        self.addObject(self.hTree_WClassification)
        self.hTree_WTauClassification=ROOT.TH2F('hTree_WTauClassification',   'Classification of Tau (from W) Daughters ',   6, 0, 6, 10, 0, 10)
        self.addObject(self.hTree_WTauClassification)
        self.hScratch=ROOT.TH2F('hScratch',   'Scratch Space',   8, 0, 8, 6, 0, 6)
        self.addObject(self.hScratch)
        self.hTree_DeltaR=ROOT.TH2F('hTree_DeltaR',   'DeltaR plot for Jet types',   120, 0, 1.2, 6, 0, 6)
        self.addObject(self.hTree_DeltaR)
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
        self.hTree_MuPtDz=ROOT.TH2F('hTree_MuPtDz',   'Muon Pt-Dz; Muon; Dz',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_MuPtDz)
        self.hTree_ElPtDz=ROOT.TH2F('hTree_ElPtDz',   'Electron Pt-Dz; Electron; Dz',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_ElPtDz)
        self.hTree_MuIdIso=ROOT.TH2F('hTree_MuIdIso',   'Muon ID vs ISO; Muon ID; Muon ISO',   2, 0, 2, 2, 0, 2)
        self.addObject(self.hTree_MuIdIso)
        self.hTree_ElIdIso=ROOT.TH2F('hTree_ElIdIso',   'Electron ID vs ISO; Electron ID; Electron ISO',   2, 0, 2, 2, 0, 2)
        self.addObject(self.hTree_ElIdIso)
        self.hTree_MuPtIp3d=ROOT.TH2F('hTree_MuPtIp3d',   'Muon Pt-Ip3d; Muon; 3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.2)
        self.addObject(self.hTree_MuPtIp3d)
        self.hTree_ElPtIp3d=ROOT.TH2F('hTree_ElPtIp3d',   'Electron Pt-Ip3d; Electron; 3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.2)
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
            print("WARNING: Attempt to run MCTruth Module on Data (Detected)!")
            return False
        
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
        #genweight = 
        #lhe = Object(event, "FIXME")
        #weights = FIXME
        #PSWeights = FIXME

        ##################################
        ### Print info for exploration ###
        ##################################

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
   
        ############
        ### Tree ###
        ############
        #evtTree = MCTree(gens, verbose=True, debug=True)
        evtTree = MCTree(gens, muonCollection=muons, electronCollection=electrons, tauCollection=taus, 
                         jetCollection=jets, genJetCollection=genjets, fatJetCollection=fatjets, 
                         genJetAK8Collection=genfatjets)
        PFT = evtTree.buildPFTrees(onlyUseClosest=True)
        TTops = evtTree.linkTops(returnSuccess=False, returnCopy=True)
        TDaughters = evtTree.linkTopDaughters(returnSuccess=False, returnCopy=True)
        TWs= evtTree.linkWDaughters(returnSuccess=False, returnCopy=True)
        TTaus= evtTree.linkTauDaughters(returnSuccess=False, returnCopy=True)
        TBDesc = evtTree.linkBDescendants(returnSuccess=False, returnCopy=True)
        #print("Searching for W Descendants")
        TWDesc = evtTree.linkWDescendants(returnSuccess=False, returnCopy=True)
        #print(TWDesc)
        TDesc = evtTree.linkAllTopDescendants(returnSuccess=False, returnCopy=True)
        TTauDesc = evtTree.linkTauDescendants(returnSuccess=False, returnCopy=True)
        TLeptonicity = evtTree.evaluateLeptonicity(returnCopy=True)
        TJets = evtTree.evaluateHadronicity(returnCopy=True)
        #print(TJets)
        #evtTree.pprintGenNode(nodeKey=-1)
        #print(evtTree.anyDescent(3, sortkey=evtTree.sortByAbsId, onlyDaughterless=True))
        TT = evtTree.getMCTree()
        TIS = evtTree.getInternalState()
        #print(TIS)
        #self.hTree_top_dau_count.Fill()
        #self.hTree_top_dau_pdg.Fill()
        for treeidx in TIS['t_last'].values():
            daus = TT[treeidx]
            dauIds = [str(gens[dau].pdgId) for dau in daus]
            pdgId = gens[treeidx].pdgId
            absId = abs(pdgId)
            self.hTree_top_dau_count.Fill(str(len(daus)), 1.0)
            for dau in dauIds:
                self.hTree_top_dau_pdg.Fill(dau, 1.0)
        for treeidx in TIS['tb_first'].values():
            daus = TT[treeidx]
            dauIds = [str(gens[dau].pdgId) for dau in daus]
            pdgId = gens[treeidx].pdgId
            absId = abs(pdgId)
            statFlags = gens[treeidx].statusFlags
            someTests = [statFlags & self.bits['isFirstCopy'], statFlags & self.bits['isLastCopy'], statFlags & self.bits['isLastCopyBeforeFSR']]
            someTestStrings = []
            if someTests[0]: someTestStrings.append("isFirstCopy")
            if someTests[1]: someTestStrings.append("isLastCopy")
            if someTests[2]: someTestStrings.append("isLastCopyBeforeFSR")
            for stest in someTestStrings:
                self.hTree_bfirst_isXCopy.Fill(stest, 1.0)
            self.hTree_bfirst_dau_count.Fill(str(len(daus)), 1.0)
            for dau in dauIds:
                self.hTree_bfirst_dau_pdg.Fill(dau, 1.0)
        for treeidx in TIS['tb_last'].values():
            daus = TT[treeidx]
            dauIds = [str(gens[dau].pdgId) for dau in daus]
            pdgId = gens[treeidx].pdgId
            absId = abs(pdgId)
            statFlags = gens[treeidx].statusFlags
            someTests = [statFlags & self.bits['isFirstCopy'], statFlags & self.bits['isLastCopy'], statFlags & self.bits['isLastCopyBeforeFSR']]
            someTestStrings = []
            if someTests[0]: someTestStrings.append("isFirstCopy")
            if someTests[1]: someTestStrings.append("isLastCopy")
            if someTests[2]: someTestStrings.append("isLastCopyBeforeFSR")
            for stest in someTestStrings:
                self.hTree_blast_isXCopy.Fill(stest, 1.0)
            #self.hTree_blast_dau_count.Fill(str(len(daus)), 1.0)
        for treeidx in TIS['tW_first'].values():
            daus = TT[treeidx]
            #daus = [(str(dau), str(self.gens[dau].pdgId)) for dau in daus]
            dauIds = [str(gens[dau].pdgId) for dau in daus]
            pdgId = gens[treeidx].pdgId
            absId = abs(pdgId)
            statFlags = gens[treeidx].statusFlags
            someTests = [statFlags & self.bits['isFirstCopy'], statFlags & self.bits['isLastCopy'], statFlags & self.bits['isLastCopyBeforeFSR']]
            someTestStrings = []
            if someTests[0]: someTestStrings.append("isFirstCopy")
            if someTests[1]: someTestStrings.append("isLastCopy")
            if someTests[2]: someTestStrings.append("isLastCopyBeforeFSR")
            for stest in someTestStrings:
                self.hTree_Wfirst_isXCopy.Fill(stest, 1.0)
        for treeidx in TIS['tW_last'].values():
            daus = TT[treeidx]
            #daus = [(str(dau), str(gens[dau].pdgId)) for dau in daus]
            dauIds = [str(gens[dau].pdgId) for dau in daus]
            pdgId = gens[treeidx].pdgId
            absId = abs(pdgId)
            statFlags = gens[treeidx].statusFlags
            someTests = [statFlags & self.bits['isFirstCopy'], statFlags & self.bits['isLastCopy'], statFlags & self.bits['isLastCopyBeforeFSR']]
            someTestStrings = []
            if someTests[0]: someTestStrings.append("isFirstCopy")
            if someTests[1]: someTestStrings.append("isLastCopy")
            if someTests[2]: someTestStrings.append("isLastCopyBeforeFSR")
            for stest in someTestStrings:
                self.hTree_Wlast_isXCopy.Fill(stest, 1.0)
            self.hTree_Wlast_dau_count.Fill(str(len(daus)), 1.0)
            for dau in dauIds:
                self.hTree_Wlast_dau_pdg.Fill(dau, 1.0)
        for tidx in TTaus['nDau'].keys():
            tauClass = "nLep=" + str(TTaus['nLep'][tidx]) + " nHad="\
                     + str(TTaus['nHad'][tidx]) + " nPho=" + str(TTaus['nPho'][tidx])
            self.hTree_WTauClassification.Fill("nDau="+str(TTaus['nDau'][tidx]),tauClass, 1.0)
            if TIS['tHasHadronicWDauTau'][tidx] == True:
                self.hTree_WTauToQ_dau_count.Fill(str(TTaus['nDau'][tidx]), 1.0)
            elif TIS['tHasHadronicWDauTau'][tidx] == False:
                self.hTree_WTauToL_dau_count.Fill(str(TTaus['nDau'][tidx]), 1.0)
            #self.hScratch.Fill("nDau="+str(TTaus['nDau'][tidx]), "nLep="+str(TTaus['nLep'][tidx]), 1.0)
            if TTaus['nDau'][tidx] != TTaus['nLep'][tidx] + TTaus['nHad'][tidx] + TTaus['nPho'][tidx]:
                print(TTaus['daughterIds'][tidx])
            for did in TTaus['daughterIds'][tidx]:
                if TIS['tHasHadronicWDauTau'][tidx] == True:
                    self.hTree_WTauToQ_dau_pdg.Fill(str(did), 1.0)
                elif TIS['tHasHadronicWDauTau'][tidx] == False:
                    self.hTree_WTauToL_dau_pdg.Fill(str(did), 1.0)
                if abs(did) > 399:
                    print(did)
        for cls in ["tHasWDauElectron",
                    "tHasWDauMuon",
                    "tHasWDauTau",
                    "tHasAnyHadronicTau",
                    "tHasHadronicW",
                    "tHasHadronicWDauTau"]:
            #print(cls + " : " + str(TIS[cls]))
            for val in TIS[cls].values():
                if val == True:
                    self.hTree_WClassification.Fill(cls, 1.0)
                    
        ##########################
        ### Tree Jets Plotting ###
        ##########################
        for tidx in TJets['tJets'].keys():
            tJ = TJets['tJets'][tidx]
            tGJ = TJets['tGenJets'][tidx]
            tFJ = TJets['tFatJets'][tidx]
            tGJ8 = TJets['tGenJetAK8s'][tidx]
            bJ = TJets['bJets'][tidx]
            bGJ = TJets['bGenJets'][tidx]
            bFJ = TJets['bFatJets'][tidx]
            bGJ8 = TJets['bGenJetAK8s'][tidx]
            W1J = TJets['WDau1Jets'][tidx]
            W1GJ = TJets['WDau1GenJets'][tidx]
            W1FJ = TJets['WDau1FatJets'][tidx]
            W1GJ8 = TJets['WDau1GenJetAK8s'][tidx]
            W2J = TJets['WDau2Jets'][tidx]
            W2GJ = TJets['WDau2GenJets'][tidx]
            W2FJ = TJets['WDau2FatJets'][tidx]
            W2GJ8 = TJets['WDau2GenJetAK8s'][tidx]
            self.hTree_tJets.Fill("Jet", len(tJ), 1.0 )
            self.hTree_tJets.Fill("GenJet", len(tGJ), 1.0 )
            self.hTree_tJets.Fill("FatJet", len(tFJ), 1.0 )
            self.hTree_tJets.Fill("GenJetAK8", len(tGJ8), 1.0 )
            self.hTree_tbJets.Fill("Jet", len(bJ), 1.0 )
            self.hTree_tbJets.Fill("GenJet", len(bGJ), 1.0 )
            self.hTree_tbJets.Fill("FatJet", len(bFJ), 1.0 )
            self.hTree_tbJets.Fill("GenJetAK8", len(bGJ8), 1.0 )
            self.hTree_tWDau1Jets.Fill("Jet", len(W1J), 1.0 )
            self.hTree_tWDau1Jets.Fill("GenJet", len(W1GJ), 1.0 )
            self.hTree_tWDau1Jets.Fill("FatJet", len(W1FJ), 1.0 )
            self.hTree_tWDau1Jets.Fill("GenJetAK8", len(W1GJ8), 1.0 )
            self.hTree_tWDau2Jets.Fill("Jet", len(W2J), 1.0 )
            self.hTree_tWDau2Jets.Fill("GenJet", len(W2GJ), 1.0 )
            self.hTree_tWDau2Jets.Fill("FatJet", len(W2FJ), 1.0 )
            self.hTree_tWDau2Jets.Fill("GenJetAK8", len(W2GJ8), 1.0 )
            #Tight Jet ID requirement...
            tJ_T = [j for j in tJ if jets[j].jetId >= 2]
            bJ_T = [j for j in bJ if jets[j].jetId >= 2]
            W1J_T = [j for j in W1J if jets[j].jetId >= 2]
            W2J_T = [j for j in W2J if jets[j].jetId >= 2]
            self.hTree_tJets.Fill("Tight Jet", len(tJ_T), 1.0 )
            self.hTree_tbJets.Fill("Tight Jet", len(bJ_T), 1.0 )
            self.hTree_tWDau1Jets.Fill("Tight Jet", len(W1J_T), 1.0 )
            self.hTree_tWDau2Jets.Fill("Tight Jet", len(W2J_T), 1.0 )
            #Tight Lepton Veto Jet ID requirement...
            tJ_TLV = [j for j in tJ if jets[j].jetId >= 6]
            bJ_TLV = [j for j in bJ if jets[j].jetId >= 6]
            W1J_TLV = [j for j in W1J if jets[j].jetId >= 6]
            W2J_TLV = [j for j in W2J if jets[j].jetId >= 6]
            self.hTree_tJets.Fill("TLV Jet", len(tJ_TLV), 1.0 )
            self.hTree_tbJets.Fill("TLV Jet", len(bJ_TLV), 1.0 )
            self.hTree_tWDau1Jets.Fill("TLV Jet", len(W1J_TLV), 1.0 )
            self.hTree_tWDau2Jets.Fill("TLV Jet", len(W2J_TLV), 1.0 )
            # 20 GeV Requirement
            tJ_20 = [j for j in tJ if jets[j].pt >= 20]
            bJ_20 = [j for j in bJ if jets[j].pt >= 20]
            W1J_20 = [j for j in W1J if jets[j].pt >= 20]
            W2J_20 = [j for j in W2J if jets[j].pt >= 20]
            self.hTree_tJets.Fill("20GEV Jet", len(tJ_20), 1.0 )
            self.hTree_tbJets.Fill("20GEV Jet", len(bJ_20), 1.0 )
            self.hTree_tWDau1Jets.Fill("20GEV Jet", len(W1J_20), 1.0 )
            self.hTree_tWDau2Jets.Fill("20GEV Jet", len(W2J_20), 1.0 )
            # 30 GeV Requirement
            #tJ_30 = [j for j in tJ if jets[j].pt >= 30]
            #bJ_30 = [j for j in bJ if jets[j].pt >= 30]
            #W1J_30 = [j for j in W1J if jets[j].pt >= 30]
            #W2J_30 = [j for j in W2J if jets[j].pt >= 30]
            #self.hTree_tJets.Fill("30GEV Jet", len(tJ_30), 1.0 )
            #self.hTree_tbJets.Fill("30GEV Jet", len(bJ_30), 1.0 )
            #self.hTree_tWDau1Jets.Fill("30GEV Jet", len(W1J_30), 1.0 )
            #self.hTree_tWDau2Jets.Fill("30GEV Jet", len(W2J_30), 1.0 )
            #Both 20GeV and Tight+ Id
            tJ_20T = list(set(tJ_20).intersection(tJ_T))
            bJ_20T = list(set(bJ_20).intersection(bJ_T))
            W1J_20T = list(set(W1J_20).intersection(W1J_T))
            W2J_20T = list(set(W2J_20).intersection(W2J_T))
            self.hTree_tJets.Fill("20GeV Tight Jet", len(tJ_20T), 1.0 )
            self.hTree_tbJets.Fill("20GeV Tight Jet", len(bJ_20T), 1.0 )
            self.hTree_tWDau1Jets.Fill("20GeV Tight Jet", len(W1J_20T), 1.0 )
            self.hTree_tWDau2Jets.Fill("20GeV Tight Jet", len(W2J_20T), 1.0 )
            #20GeV and Tight Lepton Veto
            tJ_20TLV = list(set(tJ_20).intersection(tJ_TLV))
            bJ_20TLV = list(set(bJ_20).intersection(bJ_TLV))
            W1J_20TLV = list(set(W1J_20).intersection(W1J_TLV))
            W2J_20TLV = list(set(W2J_20).intersection(W2J_TLV))
            self.hTree_tJets.Fill("20GeV TLV Jet", len(tJ_20TLV), 1.0 )
            self.hTree_tbJets.Fill("20GeV TLV Jet", len(bJ_20TLV), 1.0 )
            self.hTree_tWDau1Jets.Fill("20GeV TLV Jet", len(W1J_20TLV), 1.0 )
            self.hTree_tWDau2Jets.Fill("20GeV TLV Jet", len(W2J_20TLV), 1.0 )
            
            #if len(bJ_20TLV) > 3:
            #    print("tidx: " + str(tidx))
            #    print("List of b-Jet matched jets: " + str(bJ_20TLV))
            #    evtTree.pprintGenNode(nodeKey=-1)
            #    dumpJetCollection(jets)
            #    print(TIS['treeJet'])
            
            
             
                    
        #############################      
        ### Tree Leptons Plotting ###
        #############################
        topMuons = []
        topElectrons = []
        topTauMuons = []
        topTauElectrons = []
        topbLeptons = []
        topWLeptons = []
        for tidx, treeidx in TIS['tW_dau1_last'].iteritems():
            topbLeptons += TIS['tb_hadleps'][tidx]
            topWLeptons += TIS['tW_hadleps'][tidx]
            if TIS['tHasWDauMuon'][tidx] == True:
                topMuons.append(treeidx)
            if TIS['tHasWDauElectron'][tidx] == True:
                topElectrons.append(treeidx)
            if TIS['tHasWDauTau'][tidx] == True and TIS['tHasHadronicWDauTau'][tidx] == False:
                lepIdx = TIS['tWTau_mLep_last'][tidx]
                #evtTree.pprintGenNode(nodeKey=-1)
                if gens[lepIdx].pdgId in [-11, 11]:
                    topTauElectrons.append(lepIdx)
                    #dumpElectronCollection(electrons)
                elif gens[lepIdx].pdgId in [-13, 13]:
                    topTauMuons.append(lepIdx)
                    #dumpMuonCollection(muons)
                #print("pdgId=" + str(gens[lepIdx].pdgId) + " lepIdx=" + str(lepIdx) + " topTauEle=" + str(topTauElectrons)\
                #      + " topTauMu=" + str(topTauMuons))
        
        #print("b Hadronic Leptons: " + str(topbLeptons))            
        treeElectron = TIS['treeElectron']
        treeMuon = TIS['treeMuon']
        treeTau = TIS['treeTau']
        treeJet = TIS['treeJet']
        treeJetDR = PFT['dRJet']
        treeGenJet = TIS['treeGenJet']
        treeGenJetDR = PFT['dRGenJet']
        treeFatJet = TIS['treeFatJet']
        treeFatJetDR = PFT['dRFatJet']
        treeGenJetAK8 = TIS['treeGenJetAK8']
        treeGenJetAK8DR = PFT['dRGenJetAK8']  
         
        nAltCalc = len(topMuons) + len(topElectrons) + len(topTauMuons) + len(topTauElectrons)
        if nAltCalc == 2:
            #dumpMuonCollection(muons)
            if (len(topMuons) + len(topTauMuons)) == 2:
                temp = copy.copy(topMuons) + copy.copy(topTauMuons)
                #print(temp)
                #print("treeMuon[temp[0]]: " + str(treeMuon[temp[0]]) + " treeMuon[temp[1]]: " + str(treeMuon[temp[1]]))
                #print("==== treeMuon ====")
                #print(treeMuon)
                temp = [treeMuon[m] for m in temp] #Store list of lists, as they may be empty if no muon reconstructed
                temp = [t[0] for t in temp if len(t) > 0]
                if len(temp) == 2: 
                    temp.sort(key = lambda m : muons[m].pt, reverse=True)
                    self.hTree_MuMuSpec.Fill(muons[temp[0]].pt, muons[temp[1]].pt)
            elif (len(topElectrons) + len(topTauElectrons)) == 2:
                temp = copy.copy(topElectrons) + copy.copy(topTauElectrons)
                temp = [treeElectron[e] for e in temp] #Store list of lists, as they may be empty if no electron reconstructed
                temp = [t[0] for t in temp if len(t) > 0]
                if len(temp) == 2: 
                    temp.sort(key = lambda e : electrons[e].pt, reverse=True)
                    self.hTree_ElElSpec.Fill(electrons[temp[0]].pt, electrons[temp[1]].pt)
            elif (len(topElectrons) + len(topTauElectrons) + len(topMuons) + len(topTauMuons)) == 2:
                tempE = copy.copy(topElectrons) + copy.copy(topTauElectrons)
                tempE = [treeElectron[e] for e in tempE] #Store list of lists, as they may be empty if no electron reconstructed
                tempE = [t[0] for t in tempE if len(t) > 0]
                tempM = topMuons + topTauMuons
                tempM = [treeMuon[m] for m in tempM] #Store list of lists, as they may be empty if no muon reconstructed
                tempM = [t[0] for t in tempM if len(t) > 0]
                if (len(tempE) + len(tempM)) == 2: 
                    tempE.sort(key = lambda e : electrons[e].pt, reverse=True)
                    tempM.sort(key = lambda m : muons[m].pt, reverse=True)
                    self.hTree_ElMuSpec.Fill(electrons[tempE[0]].pt, muons[tempM[0]].pt)
        nHadTop = TLeptonicity['nHad']
        nLepTop = TLeptonicity['nLep']
        nEleTop = TLeptonicity['nEle']
        nMuonTop = TLeptonicity['nMuon']
        nLepTauTop = TLeptonicity['nLepTau']
        nHadTauTop = TLeptonicity['nHadTau']
        self.hTree_hasHadronicTop_count.Fill(nHadTop)
        #print("nAltCalc vs nLepTop: " + str(nAltCalc) + " :: " + str(nLepTop))
        
        
        
        WMuons = []
        WMuons = [treeMuon[m] for m in topWLeptons]
        WMuons = [mu[0] for mu in WMuons if len(mu) > 0]
        WElectrons = []
        WElectrons = [treeElectron[e] for e in topWLeptons]
        WElectrons = [el[0] for el in WElectrons if len(el) > 0]
        
        #self.addObject(self.hTree_WLepMuPtDz)
        #self.addObject(self.hTree_WLepElPtDz)
        #self.addObject(self.hTree_WLepMuPtIp3d)
        #self.addObject(self.hTree_WLepElPtIp3d)
        #self.addObject(self.hTree_WLepMuIdIso)
        #self.addObject(self.hTree_WLepElIdIso)
        for ww, WMu in enumerate(WMuons):
            #print(bMu)
            muon = muons[WMu]
            #if muon.pt < 15: continue
            muTrueId = []
            muTrueIso = []
            muTrueId.append("looseId")
            muTrueIso.append("noIso")
            
            if muon.mediumId:
                muTrueId.append("mediumId")
            if muon.mediumPromptId:
                muTrueId.append("mediumPromptId")
            if muon.tightId:
                muTrueId.append("tightId")
            if muon.triggerIdLoose:
                muTrueId.append("triggerLooseId")
            if muon.softId:
                muTrueId.append("softId")
            if muon.softMvaId:
                muTrueId.append("softMvaId")
            if muon.mvaId >= 1:
                muTrueId.append("mvaLooseId")
            if muon.mvaId >= 2:
                muTrueId.append("mvaMediumId")
            if muon.mvaId == 3:
                muTrueId.append("mvaTightId")
            if muon.highPtId == 2:
                muTrueId.append("highPtId")

            #Iso variables (booleans)
            if muon.pfIsoId >= 1:
                muTrueIso.append("PFIsoVeryLoose")
            if muon.pfIsoId >= 2:
                muTrueIso.append("PFIsoLoose")
            if muon.pfIsoId >= 3:
                muTrueIso.append("PFIsoMedium")
            if muon.pfIsoId >= 4:
                muTrueIso.append("PFIsoTight")
            if muon.pfIsoId >= 5:
                muTrueIso.append("PFIsoVeryTight")
            if muon.pfIsoId == 6:
                muTrueIso.append("PFIsoVeryVeryTight")
            if muon.multiIsoId >= 1:
                muTrueIso.append("MultiIsoLoose")
            if muon.multiIsoId == 2:
                muTrueIso.append("MultiIsoMedium")
            if muon.tkIsoId >= 1:
                muTrueIso.append("TkIsoLoose")
            if muon.tkIsoId == 2:
                muTrueIso.append("TkIsoTight")
            if muon.miniIsoId >= 1:
                muTrueIso.append("MiniIsoLoose")
            if muon.miniIsoId >= 2:
                muTrueIso.append("MiniIsoMedium")
            if muon.miniIsoId >= 3:
                muTrueIso.append("MiniIsoTight")
            if muon.miniIsoId == 4:
                muTrueIso.append("MiniIsoVeryTight")

            for muTID in muTrueId:
                for muTIO in muTrueIso:
                    self.hTree_WLepMuIdIso.Fill(muTID, muTIO, 1.0)
            
            self.hTree_WLepMuPtDz.Fill(muon.pt, muon.dz, 1.0)
            self.hTree_WLepMuPtIp3d.Fill(muon.pt, muon.ip3d, 1.0)
            
        for ww, WEl in enumerate(WElectrons):
            #print(bEl)
            electron = electrons[WEl]
            #if electron.pt < 15: continue
                
            elTrueId = []
            elTrueIso = []
            elTrueId.append("basicSelection")
            elTrueIso.append("basicSelection")

            if electron.cutBased == 0:
                elTrueId.append("cutBased_fail")
            if electron.cutBased == 1:
                elTrueId.append("cutBased_veto")
            if electron.cutBased >= 2:
                elTrueId.append("cutBased_loose")
            if electron.cutBased >= 3:
                elTrueId.append("cutBased_medium")
            if electron.cutBased == 4:
                elTrueId.append("cutBased_tight")
            if electron.mvaFall17V2Iso_WP80:
                elTrueId.append("mvaFall17V2Iso_WP80")
            if electron.mvaFall17V2Iso_WP90:
                elTrueId.append("mvaFall17V2Iso_WP90")
            if electron.mvaFall17V2Iso_WPL:
                elTrueId.append("mvaFall17V2Iso_WPL")
            if electron.mvaFall17V2noIso_WP80:
                elTrueId.append("mvaFall17V2noIso_WP80")
            if electron.mvaFall17V2noIso_WP90:
                elTrueId.append("mvaFall17V2noIso_WP90")
            if electron.mvaFall17V2noIso_WPL:
                elTrueId.append("mvaFall17V2noIso_WPL")

            for elTID in elTrueId:
                for elTIO in elTrueIso:
                    self.hTree_WLepElIdIso.Fill(elTIO, elTID, 1.0)    
                
            self.hTree_WLepElPtDz.Fill(electron.pt, electron.dz, 1.0)
            self.hTree_WLepElPtIp3d.Fill(electron.pt, electron.ip3d, 1.0)
            
        bMuons = []
        bMuons = [treeMuon[m] for m in topbLeptons]
        bMuons = [mu[0] for mu in bMuons if len(mu) > 0]
        bElectrons = []
        bElectrons = [treeElectron[e] for e in topbLeptons]
        bElectrons = [el[0] for el in bElectrons if len(el) > 0]
        
        for bb, bMu in enumerate(bMuons):
            #print(bMu)
            muon = muons[bMu]
            #if muon.pt < 15: continue
            muTrueId = []
            muTrueIso = []
            muTrueId.append("looseId")
            muTrueIso.append("noIso")
            
            if muon.mediumId:
                muTrueId.append("mediumId")
            if muon.mediumPromptId:
                muTrueId.append("mediumPromptId")
            if muon.tightId:
                muTrueId.append("tightId")
            if muon.triggerIdLoose:
                muTrueId.append("triggerLooseId")
            if muon.softId:
                muTrueId.append("softId")
            if muon.softMvaId:
                muTrueId.append("softMvaId")
            if muon.mvaId >= 1:
                muTrueId.append("mvaLooseId")
            if muon.mvaId >= 2:
                muTrueId.append("mvaMediumId")
            if muon.mvaId == 3:
                muTrueId.append("mvaTightId")
            if muon.highPtId == 2:
                muTrueId.append("highPtId")

            #Iso variables (booleans)
            if muon.pfIsoId >= 1:
                muTrueIso.append("PFIsoVeryLoose")
            if muon.pfIsoId >= 2:
                muTrueIso.append("PFIsoLoose")
            if muon.pfIsoId >= 3:
                muTrueIso.append("PFIsoMedium")
            if muon.pfIsoId >= 4:
                muTrueIso.append("PFIsoTight")
            if muon.pfIsoId >= 5:
                muTrueIso.append("PFIsoVeryTight")
            if muon.pfIsoId == 6:
                muTrueIso.append("PFIsoVeryVeryTight")
            if muon.multiIsoId >= 1:
                muTrueIso.append("MultiIsoLoose")
            if muon.multiIsoId == 2:
                muTrueIso.append("MultiIsoMedium")
            if muon.tkIsoId >= 1:
                muTrueIso.append("TkIsoLoose")
            if muon.tkIsoId == 2:
                muTrueIso.append("TkIsoTight")
            if muon.miniIsoId >= 1:
                muTrueIso.append("MiniIsoLoose")
            if muon.miniIsoId >= 2:
                muTrueIso.append("MiniIsoMedium")
            if muon.miniIsoId >= 3:
                muTrueIso.append("MiniIsoTight")
            if muon.miniIsoId == 4:
                muTrueIso.append("MiniIsoVeryTight")
                
            if muon.jetIdx > -1:
                aJet = jets[muon.jetIdx]
                aCSV = aJet.btagCSVV2 
                aDB = aJet.btagDeepB 
                aDC = aJet.btagDeepC
                aDJ = aJet.btagDeepFlavB
                if muon.pt >= 15:
                    self.hTree_bLepJetBtag.Fill(aCSV, ">15GeV mu + CSVv2", 1.0)
                    self.hTree_bLepJetBtag.Fill(aDB, ">15GeV mu + Deep CSV B", 1.0)
                    self.hTree_bLepJetBtag.Fill(aCSV, ">15GeV mu + Deep CSV C", 1.0)
                    self.hTree_bLepJetBtag.Fill(aDJ, ">15GeV mu + DeepJet B", 1.0)
                else:
                    self.hTree_bLepJetBtag.Fill(aCSV, "<15GeV mu + CSVv2", 1.0)
                    self.hTree_bLepJetBtag.Fill(aDB, "<15GeV mu + Deep CSV B", 1.0)
                    self.hTree_bLepJetBtag.Fill(aCSV, "<15GeV mu + Deep CSV C", 1.0)
                    self.hTree_bLepJetBtag.Fill(aDJ, "<15GeV mu + DeepJet B", 1.0)

            for muTID in muTrueId:
                for muTIO in muTrueIso:
                    self.hTree_bLepMuIdIso.Fill(muTID, muTIO, 1.0)
            
            self.hTree_bLepMuPtDz.Fill(muon.pt, muon.dz, 1.0)
            self.hTree_bLepMuPtIp3d.Fill(muon.pt, muon.ip3d, 1.0)
            
        for bb, bEl in enumerate(bElectrons):
            #print(bEl)
            electron = electrons[bEl]
            #if electron.pt < 15: continue
                
            elTrueId = []
            elTrueIso = []
            elTrueId.append("basicSelection")
            elTrueIso.append("basicSelection")

            if electron.cutBased == 0:
                elTrueId.append("cutBased_fail")
            if electron.cutBased == 1:
                elTrueId.append("cutBased_veto")
            if electron.cutBased >= 2:
                elTrueId.append("cutBased_loose")
            if electron.cutBased >= 3:
                elTrueId.append("cutBased_medium")
            if electron.cutBased == 4:
                elTrueId.append("cutBased_tight")
            if electron.mvaFall17V2Iso_WP80:
                elTrueId.append("mvaFall17V2Iso_WP80")
            if electron.mvaFall17V2Iso_WP90:
                elTrueId.append("mvaFall17V2Iso_WP90")
            if electron.mvaFall17V2Iso_WPL:
                elTrueId.append("mvaFall17V2Iso_WPL")
            if electron.mvaFall17V2noIso_WP80:
                elTrueId.append("mvaFall17V2noIso_WP80")
            if electron.mvaFall17V2noIso_WP90:
                elTrueId.append("mvaFall17V2noIso_WP90")
            if electron.mvaFall17V2noIso_WPL:
                elTrueId.append("mvaFall17V2noIso_WPL")
              
            if electron.jetIdx > -1:
                aJet = jets[electron.jetIdx]
                aCSV = aJet.btagCSVV2 
                aDB = aJet.btagDeepB 
                aDC = aJet.btagDeepC
                aDJ = aJet.btagDeepFlavB
                if electron.pt >= 15:
                    self.hTree_bLepJetBtag.Fill(aCSV, ">15GeV e + CSVv2", 1.0)
                    self.hTree_bLepJetBtag.Fill(aDB, ">15GeV e + Deep CSV B", 1.0)
                    self.hTree_bLepJetBtag.Fill(aCSV, ">15GeV e + Deep CSV C", 1.0)
                    self.hTree_bLepJetBtag.Fill(aDJ, ">15GeV e + DeepJet B", 1.0)
                else:
                    self.hTree_bLepJetBtag.Fill(aCSV, "<15GeV e + CSVv2", 1.0)
                    self.hTree_bLepJetBtag.Fill(aDB, "<15GeV e + Deep CSV B", 1.0)
                    self.hTree_bLepJetBtag.Fill(aCSV, "<15GeV e + Deep CSV C", 1.0)
                    self.hTree_bLepJetBtag.Fill(aDJ, "<15GeV e + DeepJet B", 1.0)

            for elTID in elTrueId:
                for elTIO in elTrueIso:
                    self.hTree_bLepElIdIso.Fill(elTIO, elTID, 1.0)    
                
            self.hTree_bLepElPtDz.Fill(electron.pt, electron.dz, 1.0)
            self.hTree_bLepElPtIp3d.Fill(electron.pt, electron.ip3d, 1.0)
            
        
        allTopLeps = []
        ### All direct muons ###
        allMus = [treeMuon[m] for m in topMuons]
        allMus = [mu[0] for mu in allMus if len(mu) > 0]
        allTopLeps += [(m, muons[m].pt, "Muon") for m in allMus]
        
        ### All direct electrons ###
        allEls = [treeElectron[e] for e in topElectrons]
        allEls = [el[0] for el in allEls if len(el) > 0]
        allTopLeps += [(e, electrons[e].pt, "Electron") for e in allEls]
        
        ### All tau muons ###
        tauMus = [treeMuon[m] for m in topTauMuons]
        tauMus = [mu[0] for mu in tauMus if len(mu) > 0]
        tauMus.sort(key = lambda m : muons[m].pt, reverse=True)
        allTopLeps += [(m, muons[m].pt, "TauMuon") for m in tauMus]
        
        ### All tau electrons ###
        tauEls = [treeElectron[e] for e in topTauElectrons]
        tauEls = [el[0] for el in tauEls if len(el) > 0]
        allTopLeps += [(e, electrons[e].pt, "TauElectron") for e in tauEls]
        
        allTopLeps.sort(key = lambda l : l[1], reverse=True)
        
        #print("allTopLeps: " +str(allTopLeps))
        
        ii = nLepTop - 1 #0-indexed counting of leptonic tops in the event
        #print("nLepTop: " + str(nLepTop))
        for jj, lepTup in enumerate(allTopLeps):
            if lepTup[2] == "Electron":
                electron = electrons[lepTup[0]]
                #print("Found Ele")
                self.hTree_ElPtDz.Fill(electron.pt, electron.dz, 1.0)
                self.hTree_ElPtIp3d.Fill(electron.pt, electron.ip3d, 1.0)
                elTrueId = []
                elTrueIso = []
                elTrueId.append("basicSelection")
                elTrueIso.append("basicSelection")

                self.hTree_ElPtId[ii][jj].Fill(electron.pt, "basicSelection", 1.0)
                if electron.cutBased == 0:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "cutBased_fail", 1.0)
                    elTrueId.append("cutBased_fail")
                if electron.cutBased == 1:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "cutBased_veto", 1.0)
                    elTrueId.append("cutBased_veto")
                if electron.cutBased >= 2:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "cutBased_loose", 1.0)
                    elTrueId.append("cutBased_loose")
                if electron.cutBased >= 3:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "cutBased_medium", 1.0)
                    elTrueId.append("cutBased_medium")
                if electron.cutBased == 2:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "cutBased_tight", 1.0)
                    elTrueId.append("cutBased_tight")
                if electron.mvaFall17V2Iso_WP80:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2Iso_WP80", 1.0)
                    elTrueId.append("mvaFall17V2Iso_WP80")
                if electron.mvaFall17V2Iso_WP90:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2Iso_WP90", 1.0)
                    elTrueId.append("mvaFall17V2Iso_WP90")
                if electron.mvaFall17V2Iso_WPL:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2Iso_WPL", 1.0)
                    elTrueId.append("mvaFall17V2Iso_WPL")
                if electron.mvaFall17V2noIso_WP80:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2noIso_WP80", 1.0)
                    elTrueId.append("mvaFall17V2noIso_WP80")
                if electron.mvaFall17V2noIso_WP90:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2noIso_WP90", 1.0)
                    elTrueId.append("mvaFall17V2noIso_WP90")
                if electron.mvaFall17V2noIso_WPL:
                    self.hTree_ElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2noIso_WPL", 1.0)
                    elTrueId.append("mvaFall17V2noIso_WPL")

                for elTID in elTrueId:
                    for elTIO in elTrueIso:
                        self.hTree_ElIdIso.Fill(elTIO, elTID, 1.0)
                    
                #if electron.mvaFall17V2Iso_WP80:
                #    self.hTree_ElPtIso[ii][jj].Fill(electron.pt, "mvaFall17V2Iso_WP80", 1.0)
                #    elTrueIso.append("mvaFall17V2Iso_WP80")
                #if electron.mvaFall17V2Iso_WP90:
                #    self.hTree_ElPtIso[ii][jj].Fill(electron.pt, "mvaFall17V2Iso_WP90", 1.0)
                #    elTrueIso.append("mvaFall17V2Iso_WP90")
                #if electron.mvaFall17V2Iso_WPL:
                #    self.hTree_ElPtIso[ii][jj].Fill(electron.pt, "mvaFall17V2Iso_WPL", 1.0)
                #    elTrueIso.append("mvaFall17V2Iso_WPL")
                
            elif lepTup[2] == "TauElectron":
                electron = electrons[lepTup[0]]
                #print("Found Tau Ele")
                self.hTree_TauToElPtDz.Fill(electron.pt, electron.dz, 1.0)
                self.hTree_TauToElPtIp3d.Fill(electron.pt, electron.ip3d, 1.0)
                elTrueId = []
                elTrueIso = []
                elTrueId.append("basicSelection")
                elTrueIso.append("basicSelection")
                
                self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "basicSelection", 1.0)
                if electron.cutBased == 0:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "cutBased_fail", 1.0)
                    elTrueId.append("cutBased_fail")
                if electron.cutBased == 1:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "cutBased_veto", 1.0)
                    elTrueId.append("cutBased_veto")
                if electron.cutBased >= 2:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "cutBased_loose", 1.0)
                    elTrueId.append("cutBased_loose")
                if electron.cutBased >= 3:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "cutBased_medium", 1.0)
                    elTrueId.append("cutBased_medium")
                if electron.cutBased == 2:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "cutBased_tight", 1.0)
                    elTrueId.append("cutBased_tight")
                if electron.mvaFall17V2Iso_WP80:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2Iso_WP80", 1.0)
                    elTrueId.append("mvaFall17V2Iso_WP80")
                if electron.mvaFall17V2Iso_WP90:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2Iso_WP90", 1.0)
                    elTrueId.append("mvaFall17V2Iso_WP90")
                if electron.mvaFall17V2Iso_WPL:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2Iso_WPL", 1.0)
                    elTrueId.append("mvaFall17V2Iso_WPL")
                if electron.mvaFall17V2noIso_WP80:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2noIso_WP80", 1.0)
                    elTrueId.append("mvaFall17V2noIso_WP80")
                if electron.mvaFall17V2noIso_WP90:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2noIso_WP90", 1.0)
                    elTrueId.append("mvaFall17V2noIso_WP90")
                if electron.mvaFall17V2noIso_WPL:
                    self.hTree_TauToElPtId[ii][jj].Fill(electron.pt, "mvaFall17V2noIso_WPL", 1.0)
                    elTrueId.append("mvaFall17V2noIso_WPL")

                for elTID in elTrueId:
                    for elTIO in elTrueIso:
                        self.hTree_TauToElIdIso.Fill(elTIO, elTID, 1.0) #Reverse to make easier to read
            elif lepTup[2] == "Muon":
                muon = muons[lepTup[0]]
                #print("Found Mu")

                self.hTree_MuPtDz.Fill(muon.pt, muon.dz, 1.0)
                self.hTree_MuPtIp3d.Fill(muon.pt, muon.ip3d, 1.0)
                self.hTree_MuPtId[ii][jj].Fill(muon.pt, "looseId", 1.0)
                muTrueId = []
                muTrueIso = []
                muTrueId.append("looseId")
                muTrueIso.append("noIso")

                if muon.mediumId:
                    self.hTree_MuPtId[ii][jj].Fill(muon.pt, "mediumId", 1.0)
                    muTrueId.append("mediumId")
                if muon.mediumPromptId:
                    self.hTree_MuPtId[ii][jj].Fill(muon.pt, "mediumPromptId", 1.0)
                    muTrueId.append("mediumPromptId")
                if muon.tightId:
                    self.hTree_MuPtId[ii][jj].Fill(muon.pt, "tightId", 1.0)
                    muTrueId.append("tightId")
                if muon.triggerIdLoose:
                    self.hTree_MuPtId[ii][jj].Fill(muon.pt, "triggerLooseId", 1.0)
                    muTrueId.append("triggerLooseId")
                if muon.softId:
                    self.hTree_MuPtId[ii][jj].Fill(muon.pt, "softId", 1.0)
                    muTrueId.append("softId")
                if muon.softMvaId:
                    self.hTree_MuPtId[ii][jj].Fill(muon.pt, "softMvaId", 1.0)
                    muTrueId.append("softMvaId")
                if muon.mvaId >= 1:
                    self.hTree_MuPtId[ii][jj].Fill(muon.pt, "mvaLooseId", 1.0)
                    muTrueId.append("mvaLooseId")
                if muon.mvaId >= 2:
                    self.hTree_MuPtId[ii][jj].Fill(muon.pt, "mvaMediumId", 1.0)
                    muTrueId.append("mvaMediumId")
                if muon.mvaId == 3:
                    self.hTree_MuPtId[ii][jj].Fill(muon.pt, "mvaTightId", 1.0)
                    muTrueId.append("mvaTightId")
                if muon.highPtId == 2:
                    self.hTree_MuPtId[ii][jj].Fill(muon.pt, "highPtId", 1.0)
                    muTrueId.append("highPtId")

                #Iso variables (booleans)
                if muon.pfIsoId >= 1:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "PFIsoVeryLoose", 1.0)
                    muTrueIso.append("PFIsoVeryLoose")
                if muon.pfIsoId >= 2:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "PFIsoLoose", 1.0)
                    muTrueIso.append("PFIsoLoose")
                if muon.pfIsoId >= 3:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "PFIsoMedium", 1.0)
                    muTrueIso.append("PFIsoMedium")
                if muon.pfIsoId >= 4:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "PFIsoTight", 1.0) 
                    muTrueIso.append("PFIsoTight")
                if muon.pfIsoId >= 5:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "PFIsoVeryTight", 1.0) 
                    muTrueIso.append("PFIsoVeryTight")
                if muon.pfIsoId == 6:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "PFIsoVeryVeryTight", 1.0)
                    muTrueIso.append("PFIsoVeryVeryTight")
                if muon.multiIsoId >= 1:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "MultiIsoLoose", 1.0)
                    muTrueIso.append("MultiIsoLoose")
                if muon.multiIsoId == 2:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "MultiIsoMedium", 1.0)
                    muTrueIso.append("MultiIsoMedium")
                if muon.tkIsoId >= 1:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "TkIsoLoose", 1.0)
                    muTrueIso.append("TkIsoLoose")
                if muon.tkIsoId == 2:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "TkIsoTight", 1.0)
                    muTrueIso.append("TkIsoTight")
                if muon.miniIsoId >= 1:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "MiniIsoLoose", 1.0)
                    muTrueIso.append("MiniIsoLoose")
                if muon.miniIsoId >= 2:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "MiniIsoMedium", 1.0)
                    muTrueIso.append("MiniIsoMedium")
                if muon.miniIsoId >= 3:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "MiniIsoTight", 1.0)
                    muTrueIso.append("MiniIsoTight")
                if muon.miniIsoId == 4:
                    self.hTree_MuIsoId[ii][jj].Fill(muon.pt, "MiniIsoVeryTight", 1.0)
                    muTrueIso.append("MiniIsoVeryTight")

                for muTID in muTrueId:
                    for muTIO in muTrueIso:
                        self.hTree_MuIdIso.Fill(muTID, muTIO, 1.0)
                        
            elif lepTup[2] == "TauMuon":
                muon = muons[lepTup[0]]
                #print("Found Tau Mu")
                self.hTree_TauToMuPtDz.Fill(muon.pt, muon.dz, 1.0)
                self.hTree_TauToMuPtIp3d.Fill(muon.pt, muon.ip3d, 1.0)
                self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "looseId", 1.0)
                muTrueId = []
                muTrueIso = []
                muTrueId.append("looseId")
                muTrueIso.append("noIso")
                if muon.mediumId:
                    self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "mediumId", 1.0)
                    muTrueId.append("mediumId")
                if muon.mediumPromptId:
                    self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "mediumPromptId", 1.0)
                    muTrueId.append("mediumPromptId")
                if muon.tightId:
                    self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "tightId", 1.0)
                    muTrueId.append("tightId")
                if muon.triggerIdLoose:
                    self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "triggerLooseId", 1.0)
                    muTrueId.append("triggerLooseId")
                if muon.softId:
                    self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "softId", 1.0)
                    muTrueId.append("softId")
                if muon.softMvaId:
                    self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "softMvaId", 1.0)
                    muTrueId.append("softMvaId")
                if muon.mvaId >= 1:
                    self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "mvaLooseId", 1.0)
                    muTrueId.append("mvaLooseId")
                if muon.mvaId >= 2:
                    self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "mvaMediumId", 1.0)
                    muTrueId.append("mvaMediumId")
                if muon.mvaId == 3:
                    self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "mvaTightId", 1.0)
                    muTrueId.append("mvaTightId")
                if muon.highPtId == 2:
                    self.hTree_TauToMuPtId[ii][jj].Fill(muon.pt, "highPtId", 1.0)
                    muTrueId.append("highPtId")

                #Iso variables (booleans)
                if muon.pfIsoId >= 1:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "PFIsoVeryLoose", 1.0)
                    muTrueIso.append("PFIsoVeryLoose")
                if muon.pfIsoId >= 2:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "PFIsoLoose", 1.0)
                    muTrueIso.append("PFIsoLoose")
                if muon.pfIsoId >= 3:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "PFIsoMedium", 1.0)
                    muTrueIso.append("PFIsoMedium")
                if muon.pfIsoId >= 4:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "PFIsoTight", 1.0)
                    muTrueIso.append("PFIsoTight")
                if muon.pfIsoId >= 5:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "PFIsoVeryTight", 1.0) 
                    muTrueIso.append("PFIsoVeryTight")
                if muon.pfIsoId == 6:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "PFIsoVeryVeryTight", 1.0)
                    muTrueIso.append("PFIsoVeryVeryTight")
                if muon.multiIsoId >= 1:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "MultiIsoLoose", 1.0)
                    muTrueIso.append("MultiIsoLoose")
                if muon.multiIsoId == 2:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "MultiIsoMedium", 1.0)
                    muTrueIso.append("MultiIsoMedium")
                if muon.tkIsoId >= 1:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "TkIsoLoose", 1.0)
                    muTrueIso.append("TkIsoLoose")
                if muon.tkIsoId == 2:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "TkIsoTight", 1.0)
                    muTrueIso.append("TkIsoTight")
                if muon.miniIsoId >= 1:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "MiniIsoLoose", 1.0)
                    muTrueIso.append("MiniIsoLoose")
                if muon.miniIsoId >= 2:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "MiniIsoMedium", 1.0)
                    muTrueIso.append("MiniIsoMedium")
                if muon.miniIsoId >= 3:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "MiniIsoTight", 1.0)
                    muTrueIso.append("MiniIsoTight")
                if muon.miniIsoId == 4:
                    self.hTree_TauToMuIsoId[ii][jj].Fill(muon.pt, "MiniIsoVeryTight", 1.0)
                    muTrueIso.append("MiniIsoVeryTight")

                for muTID in muTrueId:
                    for muTIO in muTrueIso:
                        self.hTree_TauToMuIdIso.Fill(muTID, muTIO, 1.0)
                
        for sidx in xrange(len(gens)):
            if len(treeElectron[sidx]) > 0:
                self.hScratch.Fill(len(treeElectron[sidx]), "Electron", 1.0)
            if len(treeMuon[sidx]) > 0:
                self.hScratch.Fill(len(treeMuon[sidx]), "Muon", 1.0)
            if len(treeTau[sidx]) > 0:
                self.hScratch.Fill(len(treeTau[sidx]), "Tau", 1.0)
            if len(treeJet[sidx]) > 0:
                self.hScratch.Fill(len(treeJet[sidx]), "Jet", 1.0)
                treeJetDR[sidx].sort()
                for drc, dr in enumerate(treeJetDR[sidx]):
                    self.hTree_DeltaR.Fill(dr, str(drc+1)+" Jet", 1.0)
            if len(treeGenJet[sidx]) > 0:
                self.hScratch.Fill(len(treeGenJet[sidx]), "GenJet", 1.0)
                treeGenJetDR[sidx].sort()
                for drc, dr in enumerate(treeGenJetDR[sidx]):
                    self.hTree_DeltaR.Fill(dr, str(drc+1)+" GenJet", 1.0)
            if len(treeFatJet[sidx]) > 0:
                self.hScratch.Fill(len(treeFatJet[sidx]), "FatJet", 1.0)
                treeFatJetDR[sidx].sort()
                for drc, dr in enumerate(treeFatJetDR[sidx]):
                    self.hTree_DeltaR.Fill(dr, str(drc+1)+" FatJet", 1.0)
            if len(treeGenJetAK8[sidx]) > 0:
                self.hScratch.Fill(len(treeGenJetAK8[sidx]), "GenJetAK8", 1.0)
                treeGenJetAK8DR[sidx].sort()
                for drc, dr in enumerate(treeGenJetAK8DR[sidx]):
                    self.hTree_DeltaR.Fill(dr, str(drc+1)+" GenJetAK8", 1.0)
        #############
        ### Dumps ###
        #############
        #dumpGenCollection(gens)
        #dumpMuonCollection(muons)
        #dumpElectronCollection(electrons)
        #dumpJetCollection(jets)
        
        
        ################################################
        ### Initialize Branch Variables to be Filled ###
        ################################################
            
        #Arrays
        # electrons_PES = []
        # muons_PES = []
        # jets_PES = []
        # jets_Tagged = []
        # jets_Untagged = []
        # for i in xrange(len(electrons)):
        #     electrons_PES.append(False)
        # for j in xrange(len(muons)):
        #     muons_PES.append(False)
        # for k in xrange(len(jets)):
        #     jets_PES.append(False)
        #     jets_Tagged.append(False)
        #     jets_Untagged.append(False)
        #genTop_VARS


        #############################################
        ### Write out slimmed selection variables ###
        #############################################
        
        #Make dictionary that makes this more automated, as in the branch creation
        # self.out.fillBranch("Electron_PES", electrons_PES)
        # self.out.fillBranch("Muon_PES", muons_PES)
        # self.out.fillBranch("Jet_PES", jets_PES)
        # self.out.fillBranch("Jet_Tagged", jets_Tagged)
        # self.out.fillBranch("Jet_Untagged", jets_Untagged)
        # self.out.fillBranch("EventVar_H", H)
        # self.out.fillBranch("EventVar_H2M", H2M)
        # self.out.fillBranch("EventVar_HT", HT)
        # self.out.fillBranch("EventVar_HT2M", HT2M)
        # self.out.fillBranch("EventVar_HTH", HTH)
        # self.out.fillBranch("EventVar_HTRat", HTRat)
        # self.out.fillBranch("EventVar_nBTagJet", nBJets)
        # self.out.fillBranch("EventVar_nTotJet", (nOthJets + nBJets))
        # self.out.fillBranch("EventVar_Trig_MuMu", passMuMu)
        # self.out.fillBranch("EventVar_Trig_ElMu", passElMu)
        # self.out.fillBranch("EventVar_Trig_ElEl", passElEl)
        # self.out.fillBranch("EventVar_Trig_Mu", passMu)

        #print("\n===========\nFinished Event #" + str(event.event) + "\n\n")
        return True
