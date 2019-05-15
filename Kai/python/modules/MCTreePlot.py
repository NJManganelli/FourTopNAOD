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
        # self.hTree_MuMuSpec=ROOT.TH2F('hTree_MuMuSpec',   'DiMuon Pt Spectra; Leading Muon; Sub-leading Muon',   70, 0, 350, 70, 0, 350)
        # self.addObject(self.hTree_MuMuSpec)
        # self.hTree_ElMuSpec=ROOT.TH2F('hTree_ElMuSpec',   'Electron - Muon Pt Spectra; Muon; Electron',   70, 0, 350, 70, 0, 350)
        # self.addObject(self.hTree_ElMuSpec)
        # self.hTree_ElElSpec=ROOT.TH2F('hTree_ElElSpec',   'DiElectron Pt Spectra; Leading Electron; Sub-leading Electron',   70, 0, 350, 70, 0, 350)
        # self.addObject(self.hTree_ElElSpec)
        # #self.hTree_MuPtId=ROOT.TH2F('hTree_MuPtId',   'Muon Pt-Boolean IDs; Muon; ID',   70, 0, 350, 15, 0, 15)
        # #self.addObject(self.hTree_MuPtId)
        # self.hTree_MuPtId={}
        # self.hTree_TauToMuPtId={}
        # self.hTree_MuIsoId={}
        # self.hTree_TauToMuIsoId={}
        # self.hTree_ElPtId={}
        # self.hTree_TauToElPtId={}
        # self.hTree_ElIsoId={}
        # self.hTree_TauToElIsoId={}
        # for i in xrange(4):
        #     self.hTree_MuPtId[i]={}
        #     self.hTree_ElPtId[i]={}
        #     self.hTree_TauToMuPtId[i]={}
        #     self.hTree_TauToElPtId[i]={}
        #     self.hTree_MuIsoId[i]={}
        #     self.hTree_ElIsoId[i]={}
        #     self.hTree_TauToMuIsoId[i]={}
        #     self.hTree_TauToElIsoId[i]={}
        #     for j in xrange(i+1):
        #         self.hTree_MuPtId[i][j]=ROOT.TH2F('hTree_MuPtId_{0:d}LepTop_Muon{1:d}'.format(i+1, j+1),
        #                                           'ID tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton; Muon Pt; ID',
        #                                           100, 0, 500, 10, 0, 10)
        #         self.hTree_ElPtId[i][j]=ROOT.TH2F('hTree_ElPtId_{0:d}LepTop_Electron{1:d}'.format(i+1, j+1),
        #                                           'ID tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton; Electron Pt; ID',
        #                                           100, 0, 500, 10, 0, 10)
        #         self.hTree_TauToMuPtId[i][j]=ROOT.TH2F('hTree_TauToMuPtId_{0:d}LepTop_Muon{1:d}'.format(i+1, j+1),
        #                                           'ID tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton (via Tau); Muon Pt; ID',
        #                                           100, 0, 500, 10, 0, 10)
        #         self.hTree_TauToElPtId[i][j]=ROOT.TH2F('hTree_TauToElPtId_{0:d}LepTop_Electron{1:d}'.format(i+1, j+1),
        #                                           'ID tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton (via Tau); Electron Pt; ID',
        #                                           100, 0, 500, 10, 0, 10)
        #         self.hTree_MuIsoId[i][j]=ROOT.TH2F('hTree_MuIsoId_{0:d}LepTop_Muon{1:d}'.format(i+1, j+1),
        #                                           'Isolation tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton; Muon Pt; Iso ID',
        #                                           100, 0, 500, 10, 0, 10)
        #         self.hTree_ElIsoId[i][j]=ROOT.TH2F('hTree_ElIsoId_{0:d}LepTop_Electron{1:d}'.format(i+1, j+1),
        #                                           'Isolation tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading electron; Electron Pt; Iso ID',
        #                                           100, 0, 500, 10, 0, 10)
        #         self.hTree_TauToMuIsoId[i][j]=ROOT.TH2F('hTree_TauToMuIsoId_{0:d}LepTop_Muon{1:d}'.format(i+1, j+1),
        #                                           'Isolation tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton (via Tau); Muon Pt; Iso ID',
        #                                           100, 0, 500, 10, 0, 10)
        #         self.hTree_TauToElIsoId[i][j]=ROOT.TH2F('hTree_TauToElIsoId_{0:d}LepTop_Electron{1:d}'.format(i+1, j+1),
        #                                           'Isolation tops->' + 'l'*(i+1) + '  ' + 'Sub-'*j + 'Leading lepton (via Tau); Electron Pt; Iso ID',
        #                                           100, 0, 500, 10, 0, 10)
        #         self.addObject(self.hTree_MuPtId[i][j])
        #         self.addObject(self.hTree_ElPtId[i][j])
        #         self.addObject(self.hTree_TauToMuPtId[i][j])
        #         self.addObject(self.hTree_TauToElPtId[i][j])
        #         self.addObject(self.hTree_MuIsoId[i][j])
        #         self.addObject(self.hTree_ElIsoId[i][j])
        #         self.addObject(self.hTree_TauToMuIsoId[i][j])
        #         self.addObject(self.hTree_TauToElIsoId[i][j])
                
        # ### Direct top lepton decays (Muon/Electron) ###        
        # self.hTree_MuPtDz=ROOT.TH3F('hTree_MuPtDz',   'Muon Pt-Dz; Muon; Dz; nJet',   100, 0, 500, 50, 0, 0.2, 15, 0, 15)
        # self.addObject(self.hTree_MuPtDz)
        # self.hTree_ElPtDz=ROOT.TH3F('hTree_ElPtDz',   'Electron Pt-Dz; Electron; Dz; nJet',   100, 0, 500, 50, 0, 0.2, 15, 0, 15)
        # self.addObject(self.hTree_ElPtDz)
        # self.hTree_MuIdIso=ROOT.TH3F('hTree_MuIdIso',   'Muon ID vs ISO; Muon ID; Muon ISO; nJet',   2, 0, 2, 2, 0, 2, 15, 0, 15)
        # self.addObject(self.hTree_MuIdIso)
        # self.hTree_ElIdIso=ROOT.TH3F('hTree_ElIdIso',   'Electron ID vs ISO; Electron ID; Electron ISO; nJet',   2, 0, 2, 2, 0, 2, 15, 0, 15)
        # self.addObject(self.hTree_ElIdIso)
        # self.hTree_MuPtIp3d=ROOT.TH3F('hTree_MuPtIp3d',   'Muon Pt-Ip3d; Muon; 3D Impact Parameter(cm); nJet',   100, 0, 500, 50, 0, 0.2, 15, 0, 15)
        # self.addObject(self.hTree_MuPtIp3d)
        # self.hTree_ElPtIp3d=ROOT.TH3F('hTree_ElPtIp3d',   'Electron Pt-Ip3d; Electron; 3D Impact Parameter(cm); nJet',   100, 0, 500, 50, 0, 0.2, 15, 0, 15)
        # self.addObject(self.hTree_ElPtIp3d)
        
        # ### W soft leptons (hadronization) ###
        # self.hTree_WLepMuPtIp3d=ROOT.TH2F('hTree_WLepMuPtIp3d',   'Hadronic W Jet Muon Pt-Ip3d; Muon; 3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.2)
        # self.addObject(self.hTree_WLepMuPtIp3d)
        # self.hTree_WLepElPtIp3d=ROOT.TH2F('hTree_WLepElPtIp3d',   'Hadronic W Jet Electron Pt-Ip3d; Electron;3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.2)
        # self.addObject(self.hTree_WLepElPtIp3d)
        # self.hTree_WLepMuPtDz=ROOT.TH2F('hTree_WLepMuPtDz',   'Hadronic W Jet Muon Pt-Dz; Muon; Dz',   100, 0, 500, 50, 0, 0.2)
        # self.addObject(self.hTree_WLepMuPtDz)
        # self.hTree_WLepElPtDz=ROOT.TH2F('hTree_WLepElPtDz',   'Hadronic W Jet Electron Pt-Dz; Electron; Dz',   100, 0, 500, 50, 0, 0.2)
        # self.addObject(self.hTree_WLepElPtDz)
        # self.hTree_WLepMuIdIso=ROOT.TH2F('hTree_WLepMuIdIso',   'Hadronic W Jet Muon ID vs ISO; Muon ID; Muon ISO',   2, 0, 2, 2, 0, 2)
        # self.addObject(self.hTree_WLepMuIdIso)
        # self.hTree_WLepElIdIso=ROOT.TH2F('hTree_WLepElIdIso',   'Hadronic W Jet Electron ID vs ISO; Electron ID; Electron ISO',   2, 0, 2, 2, 0, 2)
        # self.addObject(self.hTree_WLepElIdIso)
        
        
        # ### b soft leptons (hadronization) ###
        # self.hTree_bLepMuPtDz=ROOT.TH2F('hTree_bLepMuPtDz',   'b Jet Muon Pt-Dz; Muon; Dz',   100, 0, 500, 50, 0, 0.2)
        # self.addObject(self.hTree_bLepMuPtDz)
        # self.hTree_bLepElPtDz=ROOT.TH2F('hTree_bLepElPtDz',   'b Jet Electron Pt-Dz; Electron; Dz',   100, 0, 500, 50, 0, 0.2)
        # self.addObject(self.hTree_bLepElPtDz)
        # self.hTree_bLepMuPtIp3d=ROOT.TH2F('hTree_bLepMuPtIp3d',   'b Jet Muon Pt-Ip3d; Muon; 3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.2)
        # self.addObject(self.hTree_bLepMuPtIp3d)
        # self.hTree_bLepElPtIp3d=ROOT.TH2F('hTree_bLepElPtIp3d',   'b Jet Electron Pt-Ip3d; Electron;3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.2)
        # self.addObject(self.hTree_bLepElPtIp3d)
        # self.hTree_bLepMuIdIso=ROOT.TH2F('hTree_bLepMuIdIso',   'b Jet Muon ID vs ISO; Muon ID; Muon ISO',   2, 0, 2, 2, 0, 2)
        # self.addObject(self.hTree_bLepMuIdIso)
        # self.hTree_bLepElIdIso=ROOT.TH2F('hTree_bLepElIdIso',   'b Jet Electron ID vs ISO; Electron ID; Electron ISO',   2, 0, 2, 2, 0, 2)
        # self.addObject(self.hTree_bLepElIdIso)
        # self.hTree_bLepJetBtag=ROOT.TH2F('hTree_bLepJetBtag',   'b Jet B-tag with associated lepton; lepton Pt; Lepton Pt X Jet B-tag',   100, 0, 1, 2, 0, 2)
        # self.addObject(self.hTree_bLepJetBtag)
        
        # ### Tau Leptons ###
        # self.hTree_TauToMuPtDz=ROOT.TH2F('hTree_TauToMuPtDz',   'Muon (via Tau) Pt-Dz; Muon; Dz',   100, 0, 500, 50, 0, 0.2)
        # self.addObject(self.hTree_TauToMuPtDz)
        # self.hTree_TauToElPtDz=ROOT.TH2F('hTree_TauToElPtDz',   'Electron (via Tau) Pt-Dz; Electron; Dz',   100, 0, 500, 50, 0, 0.2)
        # self.addObject(self.hTree_TauToElPtDz)
        # self.hTree_TauToMuPtIp3d=ROOT.TH2F('hTree_TauToMuPtIp3d',   'Muon (via Tau) Pt-Ip3d; Muon; 3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.4)
        # self.addObject(self.hTree_TauToMuPtIp3d)
        # self.hTree_TauToElPtIp3d=ROOT.TH2F('hTree_TauToElPtIp3d',   'Electron (via Tau) Pt-Ip3d; Electron; 3D Impact Parameter(cm)',   100, 0, 500, 50, 0, 0.4)
        # self.addObject(self.hTree_TauToElPtIp3d)
        # self.hTree_TauToMuIdIso=ROOT.TH2F('hTree_TauToMuIdIso',   'Muon (via Tau) ID vs ISO; Muon ID; Muon ISO',   2, 0, 2, 2, 0, 2)
        # self.addObject(self.hTree_TauToMuIdIso)
        # self.hTree_TauToElIdIso=ROOT.TH2F('hTree_TauToElIdIso',   'Electron (via Tau) ID vs ISO; Electron ID; Electron ISO',   2, 0, 2, 2, 0, 2)
        # self.addObject(self.hTree_TauToElIdIso)
        
        # ### Jets ###
        # self.hTree_tJets=ROOT.TH2F('hTree_tJets',   'Top Jets; Jet Type; N Jets',   2, 0, 2, 8, 0, 8)
        # self.addObject(self.hTree_tJets)
        # self.hTree_tbJets=ROOT.TH2F('hTree_tbJets',   'b Jets; Jet Type; N Jets',   2, 0, 2, 8, 0, 8)
        # self.addObject(self.hTree_tbJets)
        # self.hTree_tWDau1Jets=ROOT.TH2F('hTree_tWDau1Jets',   'W Daughter 1 Jets; Jet Type; N Jets',   2, 0, 2, 8, 0, 8)
        # self.addObject(self.hTree_tWDau1Jets)
        # self.hTree_tWDau2Jets=ROOT.TH2F('hTree_tWDau2Jets',   'W Daughter 2 Jets; Jet Type; N Jets',   2, 0, 2, 8, 0, 8)
        # self.addObject(self.hTree_tWDau2Jets)

        ### Reco info ###
        # self.hTree_recoMu=ROOT.TH1F('hTree_recoMu', '

        self.hTree_nJets_low=ROOT.TH1F('hTree_nJets_low',   'nJets (pt > 20 && |eta| < 2.5 && tightId); nJets; events', 20, 0, 20)
        self.addObject(self.hTree_nJets_low)
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

        self.hTree_ElDzCat=ROOT.TH3F('hTree_ElDzCat',   't->W->e Dz vs jet and b-tagged jet multiplicities; Dz (cm); nJets; nBJets', 
                                     100, 0, 0.15, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_ElDzCat)
        self.hTree_MuDzCat=ROOT.TH3F('hTree_MuDzCat',   't->W->mu Dz vs jet and b-tagged jet multiplicities; Dz (cm); nJets; nBJets', 
                                     100, 0, 0.15, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_MuDzCat)
        self.hTree_ElPtCat=ROOT.TH3F('hTree_ElPtCat',   't->W->e Pt vs jet and b-tagged jet multiplicities; Pt (GeV); nJets; nBJets', 
                                     400, 0, 400, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_ElPtCat)
        self.hTree_MuPtCat=ROOT.TH3F('hTree_MuPtCat',   't->W->mu Pt vs jet and b-tagged jet multiplicities; Pt (GeV); nJets; nBJets', 
                                     400, 0, 400, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_MuPtCat)
        self.hTree_bMatchedJetCutFlow=ROOT.TH2F('hTree_bMatchedJetCutFlow',
                                                   'CutFlow of best matched b jets;Category;Number of Jets',
                                                1, 0, 1, 1, 0, 1)
        self.addObject(self.hTree_bMatchedJetCutFlow)
        self.hTree_bMultiJet=ROOT.TH2F('hTree_bMultiJet',
                                       'b -> 2+ AK4 Jets Mult; nJets(2016-like);number of multi-jet b quarks',
                                                20, 0, 20, 5, 0, 5)
        self.addObject(self.hTree_bMultiJet)

        #Sorted leptons
        self.hTree_DirectLepPtCat = {} #pt, nJet, nBJet
        self.hTree_IndirectLepPtCat = {}
        self.hTree_TopSystemPt = {} #top, b, W
        self.hTree_bMatchedJet = {} #jetpt, jet rank, nJet
        self.hTree_bMatchedJetDR = {} #b 3-momentum, DR best match, DR second best match
        self.hTree_bMatchedJetVRank = {} #Rank best, 2nd best, 3rd best
        self.hTree_bMatchedJetHad = {} #Rank best, Hadron Flavour (Ghost clustering from GenHFMatcher)
        self.hTree_WMatchedJet1 = {} #W jet 1 pt, match rank, nJet
        self.hTree_WMatchedJet2 = {} #W jet 2 pt, match rank, nJet
        self.hTree_bMatchedJetDeepCSV = {} #1st and 2nd best matched jets' DeepCSV score
        self.hTree_bMatchedJetDeepJet = {} #1st and 2nd best matched jets' DeepJet score
        self.hTree_bMatchedJetSep = {} #DeltaR separation between 1st and 2nd best ranked jets
        for i in xrange(4):
            self.hTree_DirectLepPtCat[i]=ROOT.TH3F('hTree_DirectLepPtCat_{0:d}'.format(i+1),   
                                                   'Pt PF Lepton (t->W->Lep) (R{0:d} t pt); Pt (GeV); nJets; nBJets'.format(i+1), 
                                         400, 0, 400, 20, 0, 20, 8, 0, 8)
            self.addObject(self.hTree_DirectLepPtCat[i])
            self.hTree_IndirectLepPtCat[i]=ROOT.TH3F('hTree_IndirectLepPtCat_{0:d}'.format(i+1),   
                                                     'Pt PF Lepton (t->W->Tau->Lep) (R{0:d} t pt); Pt (GeV); nJets; nBJets'.format(i+1), 
                                         400, 0, 400, 20, 0, 20, 8, 0, 8)
            self.addObject(self.hTree_IndirectLepPtCat[i])
            self.hTree_TopSystemPt[i]=ROOT.TH3F('hTree_TopSystemPt_{0:d}'.format(i+1),   
                                                'Pt Top System {0:d}; Top_Pt (GeV); Bottom_Pt (GeV); W_Pt (GeV)'.format(i+1), 
                                                500, 0, 500, 500, 0, 500, 500, 0, 500)
            self.addObject(self.hTree_TopSystemPt[i])
            self.hTree_bMatchedJet[i]=ROOT.TH3F('hTree_bMatchedJet_{0:d}'.format(i+1),   
                                                'b Matched Jet; b Jet Pt (GeV); b Jet Match Rank (3-mom ratio); nJet Multiplicity (20GeV, ...)', 
                                                500, 0, 500, 500, 0, 5, 20, 0, 20)
            self.addObject(self.hTree_bMatchedJet[i])
            self.hTree_bMatchedJetDR[i]=ROOT.TH3F('hTree_bMatchedJetDR_{0:d}'.format(i+1),   
                                                  'b Matched Jet DeltaR; b quark 3 Momentum; DeltaR(b quark, Best Matched Jet); DeltaR(b quark, 2nd Best Matched Jet)', 
                                                  500, 0, 500, 100, -0.2, 5, 100, -0.2, 5)
            self.addObject(self.hTree_bMatchedJetDR[i])
            # self.hTree_bMatchedJetSep[i]=ROOT.TH2F('hTree_bMatchedJetSep_{0:d}'.format(i+1),   
            #                                        'b Matched Jet Separation; b quark Pt (GeV);DeltaR(best jet, 2nd best jet)'.format(i+1), 
            #                                        500, 0, 500, 500, 0, 10)
            # self.addObject(self.hTree_bMatchedJetSep[i])
            self.hTree_bMatchedJetVRank[i]=ROOT.TH3F('hTree_bMatchedJetVRank_{0:d}'.format(i+1),   
                                                     'b Jet Match ranks (R{0:d} b pt); Rank of Best Match; Rank of Second Best; Rank of 3rd Best'.format(i+1), 
                                                     100, 0, 2, 100, 0, 2, 100, 0, 2)
            self.addObject(self.hTree_bMatchedJetVRank[i])
            self.hTree_WMatchedJet1[i]=ROOT.TH3F('hTree_WMatchedJet1_{0:d}'.format(i+1),   
                                                 'W Matched Jet 2; W Jet Pt (GeV); W Jet Match Rank (3-momentum proxy); nJet Multiplicity (20GeV, ...)'.format(i+1), 
                                                500, 0, 500, 500, 0, 5, 20, 0, 20)
            self.addObject(self.hTree_WMatchedJet1[i])
            self.hTree_WMatchedJet2[i]=ROOT.TH3F('hTree_WMatchedJet2_{0:d}'.format(i+1),   
                                                 'W Matched Jet 2; W Jet Pt (GeV); W Jet Match Rank (3-momentum proxy); nJet Multiplicity (20GeV, ...)'.format(i+1), 
                                                500, 0, 500, 500, 0, 5, 20, 0, 20)
            self.addObject(self.hTree_WMatchedJet2[i])
            self.hTree_bMatchedJetHad[i]=ROOT.TH2F('hTree_bMatchedJetHad_{0:d}'.format(i+1),   
                                                   'b Jet Rank v Hadron Flavour (R{0:d} b pt); Rank of Best Match; Had Flavour (GenHFMatcher)'.format(i+1), 
                                                     100, 0, 2, 7, -1, 6)
            self.addObject(self.hTree_bMatchedJetHad[i])
            self.hTree_bMatchedJetDeepCSV[i]=ROOT.TH2F('hTree_bMatchedJetDeepCSV_{0:d}'.format(i+1),   
                                                  'b Jet Matches DeepCSV Value; DeepCSV of best match; DeepCSV of 2nd best match', 
                                                       200, -1, 1, 200, -1, 1)
            self.addObject(self.hTree_bMatchedJetDeepCSV[i])
            self.hTree_bMatchedJetDeepJet[i]=ROOT.TH2F('hTree_bMatchedJetDeepJet_{0:d}'.format(i+1),   
                                                  'b Jet Matches DeepJet Value; DeepJet of best match; DeepJet of 2nd best match', 
                                                       200, -1, 1, 200, -1, 1)
            self.addObject(self.hTree_bMatchedJetDeepJet[i])

        self.hTree_METCat=ROOT.TH3F('hTree_METCat',   'MET vs jet and b-tagged jet multiplicities; MET (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_METCat)
        self.hTree_HTCat=ROOT.TH3F('hTree_HTCat',   'HT vs jet and b-tagged jet multiplicities; HT (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_HTCat)
        self.hTree_HCat=ROOT.TH3F('hTree_HCat',   'H vs jet and b-tagged jet multiplicities; H (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_HCat)
        self.hTree_HT2MCat=ROOT.TH3F('hTree_HT2MCat',   'HT2M vs jet and b-tagged jet multiplicities; HT2M (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_HT2MCat)
        self.hTree_H2MCat=ROOT.TH3F('hTree_H2MCat',   'H2M vs jet and b-tagged jet multiplicities; H2M (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_H2MCat)
        self.hTree_HTbCat=ROOT.TH3F('hTree_HTbCat',   'HTb vs jet and b-tagged jet multiplicities; HTb (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1500, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_HTbCat)
        self.hTree_HTHCat=ROOT.TH3F('hTree_HTHCat',   'HTH vs jet and b-tagged jet multiplicities; HTH (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_HTHCat)
        self.hTree_HTRatCat=ROOT.TH3F('hTree_HTRatCat',   'HTRat vs jet and b-tagged jet multiplicities; HTRat (GeV); nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 1, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_HTRatCat)
        self.hTree_dRbbCat=ROOT.TH3F('hTree_dRbbCat',   'dRbb vs jet and b-tagged jet multiplicities; dRbb; nJets (25 GeV, M DeepJet...); nBJets (Med DeepJet)', 
                                     500, 0, 5, 20, 0, 20, 8, 0, 8)
        self.addObject(self.hTree_dRbbCat)
        
        self.hTree_RecoVGenJet_low=ROOT.TH2F('hTree_RecoVGenJet_low',   'AK4 Reco vs Gen Jet Multiplicity; nJets(pt > 20 && |eta| < 2.5 && TightLepVeto ID); nGenJets(pt > 20 && |eta| < 2.5)', 20, 0, 20, 20, 0, 20)
        self.addObject(self.hTree_RecoVGenJet_low)
        self.hTree_RecoVGenJet_DeepJet=ROOT.TH2F('hTree_RecoVGenJet_DeepJet',   'AK4 Reco vs Gen Jet Multiplicity; nJets(pt > 20 && |eta| < 2.5 && TightLepVeto ID && Medium DeepJet); nGenJets(pt > 20 && |eta| < 2.5 && b Had Flav)', 20, 0, 20, 20, 0, 20)
        self.addObject(self.hTree_RecoVGenJet_DeepJet)
        self.hTree_RecoVGenJet_oldDeepCSV=ROOT.TH2F('hTree_RecoVGenJet_oldDeepCSV',   'AK4 Reco vs Gen Jet Multiplicity; nJets((pt > 30 || pt > 25 && Med CSVv2) && |eta| < 2.5 && TightLepVeto ID); nGenJets((pt > 30 || b Had Flav) && |eta| < 2.5)', 20, 0, 20, 20, 0, 20)
        self.addObject(self.hTree_RecoVGenJet_oldDeepCSV)
        self.hTree_RecoVGenJet_DeepCSV=ROOT.TH2F('hTree_RecoVGenJet_DeepCSV',   'AK4 Reco vs Gen Jet Multiplicity; nJets(pt > 20 && |eta| < 2.5 && TightLepVeto ID && Medium DeepJet); nGenJets(pt > 20 && |eta| < 2.5 && b Had Flav)', 20, 0, 20, 20, 0, 20)
        self.addObject(self.hTree_RecoVGenJet_DeepCSV)

        self.hTree_RankVotesVBottomPt=ROOT.TH2F('hTree_RankVotesVBottomPt', '; bottom pt; net weighted votes', 400, 0, 400, 100, 0, 10)
        self.addObject(self.hTree_RankVotesVBottomPt)
        
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
            LHE = Object(event, "LHE")
            PSWeights = Collection(event, "PSWeight")
            LHEWeight = getattr(event, "LHEWeight_originalXWGTUP")
            LHEScaleWeight = Collection(event, "LHEScaleWeight")
            # LHEReweightingWeight = Collection(event, "LHEReweightingWeight")
            LHEPdfWeight = Collection(event, "LHEPdfWeight")


        tops = Collection(event, "GenTop")
        topsL = [top for top in tops]

        nLeps = [top for top in tops if top.tIsLeptonic]
        if self.filterNLeps and len(nLeps) != self.filterNLeps:
            return False

        anyMus = set([top.PF_Muon for top in tops if top.PF_Muon > -1])
        anyEles = set([top.PF_Electron for top in tops if top.PF_Electron > -1])
        topMus = [top.PF_Muon for top in tops if top.PF_Muon > -1 and top.tHasWDauMuon]
        topEles = [top.PF_Electron for top in tops if top.PF_Electron > -1 and top.tHasWDauElectron]
        tauMus = list(anyMus - set(topMus))
        tauEles = list(anyEles - set(topEles))

        nJets = [jet for jet in jets if abs(jet.eta) < 2.5 and jet.jetId >= 6 and jet.muonIdx1 not in anyMus and jet.muonIdx2 not in anyMus and jet.electronIdx1 not in anyEles and jet.electronIdx2 not in anyEles]
        nJets_low = [jet for jet in nJets if jet.pt > 20]
        nJets_old = [jet for jet in nJets if jet.pt > 25]
        nJets_oldCSVv2 = [jet for jet in nJets_old if jet.pt > 30 or jet.btagCSVV2 > 0.8838]
        nJets_oldDeepCSV = [jet for jet in nJets_old if jet.pt > 30 or jet.btagDeepB > 0.4941]
        nJets_oldDeepJet = [jet for jet in nJets_old if jet.pt > 30 or jet.btagDeepFlavB > 0.3033]

        #B-tagged jets
        nJetsMCSVv2 = [jet for jet in nJets_low if jet.btagCSVV2 > 0.8838]
        nJetsMDeepCSV = [jet for jet in nJets_low if jet.btagDeepB > 0.4941]
        nJetsMDeepJet = [jet for jet in nJets_low if jet.btagDeepFlavB > 0.3033]

        #Gen Jets
        nGenJets_low = [genjet for genjet in genjets if genjet.pt >= 20 and abs(genjet.eta) < 2.5]
        nGenJets_old = [genjet for genjet in nGenJets_low if genjet.pt > 30 or (genjet.hadronFlavour == 5 and genjet.pt > 25)]
        nGenJets_BTagged = [genjet for genjet in nGenJets_low if genjet.hadronFlavour == 5]

        #HT and other calculations
        HT = 0
        H = 0
        HT2M = 0
        H2M = 0
        HTb = 0
        nJetsBSorted = [jet for jet in nJets_oldDeepJet]
        nJetsBSorted.sort(key=lambda jet : jet.btagDeepFlavB, reverse=True)
        for j, jet in enumerate(nJetsBSorted):
            HT += jet.pt
            H += jet.p4().P()
            if j > 1 and len(nJetsMDeepJet) > 1:
                HT2M += jet.pt
                H2M += jet.p4().P()
            if jet.btagDeepFlavB > .3033:
                HTb += jet.pt
        self.hTree_METCat.Fill(met.pt ,len(nJets_oldDeepJet), len(nJetsMDeepJet))
        self.hTree_HTCat.Fill(HT ,len(nJets_oldDeepJet), len(nJetsMDeepJet))
        self.hTree_HCat.Fill(H ,len(nJets_oldDeepJet), len(nJetsMDeepJet))
        self.hTree_HT2MCat.Fill(HT2M ,len(nJets_oldDeepJet), len(nJetsMDeepJet))
        self.hTree_H2MCat.Fill(H2M ,len(nJets_oldDeepJet), len(nJetsMDeepJet))
        self.hTree_HTbCat.Fill(HTb ,len(nJets_oldDeepJet), len(nJetsMDeepJet))

        if len(nJetsBSorted) > 3:
            # dRbb = deltaR(nJetsBSorted[0], nJetsBSorted[1])
            # HTRat = (nJetsBSorted[0].pt + nJetsBSorted[1].pt)/HT
            HTH = HT/H
            # self.hTree_dRbbCat.Fill(dRbb, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            # self.hTree_HTRatCat.Fill(HTRat, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            self.hTree_HTHCat.Fill(HTH,len(nJets_oldDeepJet), len(nJetsMDeepJet))


        self.hTree_nLeps.Fill(len(nLeps))

        self.hTree_nJets_low.Fill(len(nJets_low))
        self.hTree_nJets_old.Fill(len(nJets_oldCSVv2))
        self.hTree_nJets_oldDeepCSV.Fill(len(nJets_oldDeepCSV))

        self.hTree_nJets_MCSVv2.Fill(len(nJetsMCSVv2))
        self.hTree_nJets_MDeepCSV.Fill(len(nJetsMDeepCSV))
        self.hTree_nJets_MDeepJet.Fill(len(nJetsMDeepJet))

        self.hTree_RecoVGenJet_low.Fill(len(nJets_low), len(nGenJets_low))
        self.hTree_RecoVGenJet_DeepJet.Fill(len(nJetsMDeepJet), len(nGenJets_BTagged))
        self.hTree_RecoVGenJet_oldDeepCSV.Fill(len(nJets_oldDeepCSV), len(nGenJets_old))
        self.hTree_RecoVGenJet_DeepCSV.Fill(len(nJetsMDeepCSV), len(nGenJets_BTagged))

        dleps = []
        ileps = []
        for mid in topMus:
            muon = muons[mid]
            dleps.append(muon)
            # self.hTree_MuPtDz.Fill(muon.pt, muon.dz, len(nJets))
            self.hTree_MuDzCat.Fill(muon.dz, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            self.hTree_MuPtCat.Fill(muon.pt, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            # self.hTree_MuIdIso
            # self.hTree_MuPtIp3d.Fill(muon.pt, muon.ip3d, len(nJets))
        for eid in topEles:
            electron = electrons[eid]
            dleps.append(electron)
            # self.hTree_ElPtDz.Fill(electron.pt, electron.dz, len(nJets))
            self.hTree_ElDzCat.Fill(electron.dz, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            self.hTree_ElPtCat.Fill(electron.pt, len(nJets_oldDeepJet), len(nJetsMDeepJet))
            # self.hTree_ElIdIso
            # self.hTree_ElPtIp3d.Fill(electron.pt, electron.ip3d, len(nJets))
        dleps.sort(key=lambda lep : lep.pt, reverse=True)
        for i, lep in enumerate(dleps):
            self.hTree_DirectLepPtCat[i].Fill(lep.pt, len(nJets_oldDeepJet), len(nJetsMDeepJet))

        for mid in tauMus:
            muon = muons[mid]
            ileps.append(muon)
            # self.hTree_MuDzCat.Fill(muon.dz, len(nJets), len(nJetsMDeepJet))
            # self.hTree_MuPtCat.Fill(muon.pt, len(nJets), len(nJetsMDeepJet))
        for eid in tauEles:
            electron = electrons[eid]
            ileps.append(electron)
            # self.hTree_ElDzCat.Fill(electron.dz, len(nJets), len(nJetsMDeepJet))
            # self.hTree_ElPtCat.Fill(electron.pt, len(nJets), len(nJetsMDeepJet))
        ileps.sort(key=lambda lep : lep.pt, reverse=True)
        for i, lep in enumerate(ileps):
            self.hTree_IndirectLepPtCat[i].Fill(lep.pt, len(nJets), len(nJetsMDeepJet))

        topsL.sort(key=lambda top : gens[top.t].pt, reverse=True)
        for i, top in enumerate(topsL):
            t = gens[top.t]
            b = gens[top.b]
            W = gens[top.W]
            self.hTree_TopSystemPt[i].Fill(t.pt, b.pt, W.pt)

        topsL.sort(key=lambda top : gens[top.b].pt, reverse=True)
        allbJet = []
        bestJets = []
        multijet = 0
        for i, top in enumerate(topsL):
            b = gens[top.b]
            bJet = []
            bJetRank = []
            bestJets.append(top.b_Jet_0)
            if top.b_Jet_0 > -1:
                bJet.append(jets[top.b_Jet_0])
                bJetRank.append(top.b_Jet_0W)
            if top.b_Jet_1 > -1:
                bJet.append(jets[top.b_Jet_1])
                bJetRank.append(top.b_Jet_1W)
                multijet += 1
            if top.b_Jet_2 > -1:
                bJet.append(jets[top.b_Jet_2])
                bJetRank.append(top.b_Jet_2W)
            if top.b_Jet_3 > -1:
                bJet.append(jets[top.b_Jet_3])
                bJetRank.append(top.b_Jet_3W)
            if top.b_Jet_4 > -1:
                bJet.append(jets[top.b_Jet_4])
                bJetRank.append(top.b_Jet_4W)
            allbJet.append(bJet)

            rnor = top.b_Jet_0W + top.b_Jet_1W + top.b_Jet_2W + top.b_Jet_3W + top.b_Jet_4W
            if rnor == 0:
                #protect against 0 division
                rnor = 1
            self.hTree_RankVotesVBottomPt.Fill(b.pt, rnor)
            for j in xrange(len(bJet)):
                if j > 3: continue #didn't make more than 4 plots for these...
                self.hTree_bMatchedJet[j].Fill(bJet[j].pt, bJetRank[j]/rnor, len(nJets_oldDeepJet)) #jetpt, jet rank, nJet
            if len(bJet) > 0:
                dR1 = deltaR(b, bJet[0])
            else:
                dR1 = -0.1
            if len(bJet) > 1:
                dR2 = deltaR(b, bJet[1])
                # dRSep = deltaR(bJet[0], bJet[1])
                # self.hTree_bMatchedJetSep[i].Fill(b.pt, dRSep)
            else:
                dR2 = -0.1
            self.hTree_bMatchedJetDR[i].Fill(b.pt, dR1, dR2) #b 3-momentum, DR best match, DR second best match
            
            R1 = top.b_Jet_0W/rnor
            R2 = top.b_Jet_1W/rnor
            R3 = top.b_Jet_2W/rnor
            self.hTree_bMatchedJetVRank[i].Fill(R1, R2, R3) #Rank best, 2nd best, 3rd best
            if len(bJet) > 0:
                flav = bJet[0].hadronFlavour
            else:
                flav = -1
            self.hTree_bMatchedJetHad[i].Fill(R1, flav)

        self.hTree_bMultiJet.Fill(len(nJets_oldDeepJet), multijet)

        for i, jetset in enumerate(allbJet):
            if len(jetset) > 1:
                DeepCSV1 = jetset[0].btagDeepB
                DeepJet1 = jetset[0].btagDeepFlavB
                DeepCSV2 = jetset[1].btagDeepB
                DeepJet2 = jetset[1].btagDeepFlavB
            elif len(jetset) > 0:
                DeepCSV1 = jetset[0].btagDeepB
                DeepJet1 = jetset[0].btagDeepFlavB
                DeepCSV2 = -1
                DeepJet2 = -1
            else:
                DeepCSV1 = -1
                DeepJet1 = -1
                DeepCSV2 = -1
                DeepJet2 = -1
            self.hTree_bMatchedJetDeepCSV[i].Fill(DeepCSV1, DeepCSV2)
            self.hTree_bMatchedJetDeepJet[i].Fill(DeepJet1, DeepJet2)


        self.hTree_bMatchedJetCutFlow.Fill('Events', 'Events', 1.0)
        bestJets = [jets[j] for j in bestJets if j > -1]
        bestJets.sort(key=lambda jet : jet.btagDeepFlavB, reverse=True)
        for i in xrange(len(bestJets)):
            self.hTree_bMatchedJetCutFlow.Fill('PF Jet', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets = [jet for jet in bestJets if abs(jet.eta) < 2.5]
        for i in xrange(len(bestJets)):
            self.hTree_bMatchedJetCutFlow.Fill('|eta| < 2.5', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets25 = [jet for jet in bestJets if jet.pt > 25]
        for i in xrange(len(bestJets25)):
            self.hTree_bMatchedJetCutFlow.Fill('pt > 25', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets25 = [jet for jet in bestJets25 if jet.jetId >= 2 ]
        for i in xrange(len(bestJets25)):
            self.hTree_bMatchedJetCutFlow.Fill('Tight + pt > 25', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets25 = [jet for jet in bestJets25 if jet.jetId >= 6 ]
        for i in xrange(len(bestJets25)):
            self.hTree_bMatchedJetCutFlow.Fill('TightLepVeto + pt > 25', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets25 = [jet for jet in bestJets25 if jet.btagDeepFlavB > 0.3033 ]
        for i in xrange(len(bestJets25)):
            self.hTree_bMatchedJetCutFlow.Fill('TightLepVeto + pt > 25 + Medium DeepJet', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets25 = [jet for jet in bestJets25 if jet.btagDeepB > 0.4941 ]
        for i in xrange(len(bestJets25)):
            self.hTree_bMatchedJetCutFlow.Fill('TightLepVeto + pt > 25 + Medium DeepCSV', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets20 = [jet for jet in bestJets if jet.pt > 20]
        for i in xrange(len(bestJets20)):
            self.hTree_bMatchedJetCutFlow.Fill('pt > 20', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets20 = [jet for jet in bestJets20 if jet.jetId >= 2 ]
        for i in xrange(len(bestJets20)):
            self.hTree_bMatchedJetCutFlow.Fill('Tight + pt > 20', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets20 = [jet for jet in bestJets20 if jet.jetId >= 6 ]
        for i in xrange(len(bestJets20)):
            self.hTree_bMatchedJetCutFlow.Fill('TightLepVeto + pt > 20', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets20 = [jet for jet in bestJets20 if jet.btagDeepFlavB > 0.3033 ]
        for i in xrange(len(bestJets20)):
            self.hTree_bMatchedJetCutFlow.Fill('TightLepVeto + pt > 20 + Medium DeepJet', '>= {0:d} Jets'.format(i+1), 1.0)
        bestJets20 = [jet for jet in bestJets20 if jet.btagDeepB > 0.4941 ]
        for i in xrange(len(bestJets20)):
            self.hTree_bMatchedJetCutFlow.Fill('TightLepVeto + pt > 20 + Medium DeepCSV', '>= {0:d} Jets'.format(i+1), 1.0)

        topsL.sort(key=lambda top : gens[top.W].pt, reverse=True)
        for i, top in enumerate(topsL):
            W = gens[top.W]
            WJet1 = []
            WJet1Rank = []
            WJet2 = []
            WJet2Rank = []
            if top.W_dau1_Jet_0 > -1:
                WJet1.append(jets[top.W_dau1_Jet_0])
                WJet1Rank.append(top.W_dau1_Jet_0W)                
            if top.W_dau1_Jet_1 > -1:
                WJet1.append(jets[top.W_dau1_Jet_1])
                WJet1Rank.append(top.W_dau1_Jet_1W)
            if top.W_dau1_Jet_2 > -1:
                WJet1.append(jets[top.W_dau1_Jet_2])
                WJet1Rank.append(top.W_dau1_Jet_2W)
            if top.W_dau2_Jet_0 > -1:
                WJet2.append(jets[top.W_dau2_Jet_0])
                WJet2Rank.append(top.W_dau2_Jet_0W)
            if top.W_dau2_Jet_1 > -1:
                WJet2.append(jets[top.W_dau2_Jet_1])
                WJet2Rank.append(top.W_dau2_Jet_1W)
            if top.W_dau2_Jet_2 > -1:
                WJet2.append(jets[top.W_dau2_Jet_2])
                WJet2Rank.append(top.W_dau2_Jet_2W)

        # self.hTree_WMatchedJet1 = {} #W jet 1 pt, match rank, nJet
        # self.hTree_WMatchedJet2 = {} #W jet 2 pt, match rank, nJet


        return True
