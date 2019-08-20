import ROOT
import os
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class lepSplitSFProducer(Module):
    def __init__(self, muon_ID=None, muon_ISO=None, electron_ID=None, era=None, doMuonHLT=False, doElectronHLT_ZVtx=False, pre2018Run316361Lumi = 8.942, post2018Run316361Lumi = 50.785, debug=False):
        self.era = era
        #See self.muD dictionary for options. ISO are denoted with a '/' in the key
        self.muon_ID = muon_ID
        self.muon_ISO = muon_ISO
        #See self.elD dictionary for options
        self.electron_ID = electron_ID
        #insert the SL HLT SF for the given era, with option for the EGamma HLT ZVtx SF (which is 1 pm 0 for 2016, 2018, and 2017DEF, but lower for 2017B and 2017C)
        self.doMuonHLT = doMuonHLT
        self.doElectronHLT_ZVtx = doElectronHLT_ZVtx
        #These are used to weight the single-muon HLT scale factors for 2018 according to how many /fb of data is used from each era
        self.pre2018Run316361Lumi = pre2018Run316361Lumi
        self.post2018Run316361Lumi = post2018Run316361Lumi
        self.debug = debug
        self.elD = {"2016": {"EFF": {"SF": "EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root==EGamma_SF2D"},
                             "EFF_lowEt": {"SF": "EGM2D_BtoH_low_RecoSF_Legacy2016.root==EGamma_SF2D"},
                             "LooseID": {"SF": "2016LegacyReReco_ElectronLoose_Fall17V2.root==EGamma_SF2D"},
                             "MediumID": {"SF": "2016LegacyReReco_ElectronMedium_Fall17V2.root==EGamma_SF2D"},
                             "TightID": {"SF": "2016LegacyReReco_ElectronTight_Fall17V2.root==EGamma_SF2D"},
                             "MVA80": {"SF": "2016LegacyReReco_ElectronMVA80_Fall17V2.root==EGamma_SF2D"},
                             "MVA80noiso": {"SF": "2016LegacyReReco_ElectronMVA80noiso_Fall17V2.root==EGamma_SF2D"},
                             "MVA90": {"SF": "2016LegacyReReco_ElectronMVA90_Fall17V2.root==EGamma_SF2D"},
                             "MVA90noiso": {"SF": "2016LegacyReReco_ElectronMVA90noiso_Fall17V2.root==EGamma_SF2D"}
                             },
                    "2017": {"EFF": {"SF": "egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root==EGamma_SF2D"},
                             "EFF_lowEt": {"SF": "egammaEffi.txt_EGM2D_runBCDEF_passingRECO_lowEt.root==EGamma_SF2D"},
                             "LooseID": {"SF": "2017_ElectronLoose.root==EGamma_SF2D"},
                             "MediumID": {"SF": "2017_ElectronMedium.root==EGamma_SF2D"},
                             "TightID": {"SF": "2017_ElectronTight.root==EGamma_SF2D"},
                             "VetoID": {"SF": "2017_ElectronWPVeto_Fall17V2.root==EGamma_SF2D"},
                             "MVA80": {"SF": "2017_ElectronMVA80.root==EGamma_SF2D"},
                             "MVA80noiso": {"SF": "2017_ElectronMVA80noiso.root==EGamma_SF2D"},
                             "MVA90": {"SF": "2017_ElectronMVA90.root==EGamma_SF2D"},
                             "MVA90noiso": {"SF": "2017_ElectronMVA90noiso.root==EGamma_SF2D"}
                             },
                    "2018": {"EFF": {"SF": "egammaEffi.txt_EGM2D_updatedAll.root==EGamma_SF2D"},
                             "LooseID": {"SF": "2018_ElectronLoose.root==EGamma_SF2D"},
                             "MediumID": {"SF": "2018_ElectronMedium.root==EGamma_SF2D"},
                             "TightID": {"SF": "2018_ElectronTight.root==EGamma_SF2D"},
                             "VetoID": {"SF": "2018_ElectronWPVeto_Fall17V2.root==EGamma_SF2D"},
                             "MVA80": {"SF": "2018_ElectronMVA80.root==EGamma_SF2D"},
                             "MVA80noiso": {"SF": "2018_ElectronMVA80noiso.root==EGamma_SF2D"},
                             "MVA90": {"SF": "2018_ElectronMVA90.root==EGamma_SF2D"},
                             "MVA90noiso": {"SF": "2018_ElectronMVA90noiso.root==EGamma_SF2D"}
                             }
                    }

        self.muD = {"2016": {"TRG_SL": {"SF": "Mu_Trg.root==IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio",
                                        "STAT": "Mu_Trg.root==IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio"},
                             "TRG_SL50": {"SF": "Mu_Trg.root==Mu50_OR_TkMu50_PtEtaBins/pt_abseta_ratio",
                                          "STAT": "Mu_Trg.root==Mu50_OR_TkMu50_PtEtaBins/pt_abseta_ratio"},
                             "LooseID": {"SF": "Mu_ID.root==MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio",
                                         "STAT": "Mu_ID.root==MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio"},
                             "MediumID2016": {"SF": "Mu_ID.root==MC_NUM_MediumID2016_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio",
                                              "STAT": "Mu_ID.root==MC_NUM_MediumID2016_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio"},
                             "MediumID": {"SF": "Mu_ID.root==MC_NUM_MediumID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio",
                                          "STAT": "Mu_ID.root==MC_NUM_MediumID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio"},
                             "TightID": {"SF": "Mu_ID.root==MC_NUM_TightID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio",
                                         "STAT": "Mu_ID.root==MC_NUM_TightID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio"},
                             "HighPtID": {"SF": "Mu_ID.root==MC_NUM_HighPtID_DEN_genTracks_PAR_newpt_eta/pair_ne_ratio",
                                          "STAT": "Mu_ID.root==MC_NUM_HighPtID_DEN_genTracks_PAR_newpt_eta/pair_ne_ratio"},
                             "LooseRelIso/LooseID": {"SF": "Mu_Iso.root==LooseISO_LooseID_pt_eta/pt_abseta_ratio",
                                                     "STAT": "Mu_Iso.root==LooseISO_LooseID_pt_eta/pt_abseta_ratio"},
                             "LooseRelIso/MediumID": {"SF": "Mu_Iso.root==LooseISO_MediumID_pt_eta/pt_abseta_ratio",
                                                      "STAT": "Mu_Iso.root==LooseISO_MediumID_pt_eta/pt_abseta_ratio"},
                             "LooseRelIso/TightID": {"SF": "Mu_Iso.root==LooseISO_TightID_pt_eta/pt_abseta_ratio",
                                                     "STAT": "Mu_Iso.root==LooseISO_TightID_pt_eta/pt_abseta_ratio"},
                             "TightRelIso/MediumID": {"SF": "Mu_Iso.root==TightISO_MediumID_pt_eta/pt_abseta_ratio",
                                                      "STAT": "Mu_Iso.root==TightISO_MediumID_pt_eta/pt_abseta_ratio"},
                             "TightRelIso/TightID": {"SF": "Mu_Iso.root==TightISO_TightID_pt_eta/pt_abseta_ratio",
                                                     "STAT": "Mu_Iso.root==TightISO_TightID_pt_eta/pt_abseta_ratio"},
                             "LooseRelTkIso/HighPtID": {"SF": "Mu_Iso.root==tkLooseISO_highptID_newpt_eta/pair_ne_ratio",
                                                        "STAT": "Mu_Iso.root==tkLooseISO_highptID_newpt_eta/pair_ne_ratio"}
                             },
                    "2017": {"TRG_SL": {"SF": "EfficienciesAndSF_RunBtoF_Nov17Nov2017.root==IsoMu27_PtEtaBins/pt_abseta_ratio",
                                        "STAT": "EfficienciesAndSF_RunBtoF_Nov17Nov2017.root==IsoMu27_PtEtaBins/pt_abseta_ratio"},
                             "LooseID": {"SF": "RunBCDEF_SF_ID_syst.root==NUM_LooseID_DEN_genTracks_pt_abseta",
                                         "STAT": "RunBCDEF_SF_ID_syst.root==NUM_LooseID_DEN_genTracks_pt_abseta_stat",
                                         "SYST": "RunBCDEF_SF_ID_syst.root==NUM_LooseID_DEN_genTracks_pt_abseta_syst"},
                             "MediumID": {"SF": "RunBCDEF_SF_ID_syst.root==NUM_MediumID_DEN_genTracks_pt_abseta",
                                          "STAT": "RunBCDEF_SF_ID_syst.root==NUM_MediumID_DEN_genTracks_pt_abseta_stat",
                                          "SYST": "RunBCDEF_SF_ID_syst.root==NUM_MediumID_DEN_genTracks_pt_abseta_syst"},
                             "TightID": {"SF": "RunBCDEF_SF_ID_syst.root==NUM_TightID_DEN_genTracks_pt_abseta",
                                         "STAT": "RunBCDEF_SF_ID_syst.root==NUM_TightID_DEN_genTracks_pt_abseta_stat",
                                         "SYST": "RunBCDEF_SF_ID_syst.root==NUM_TightID_DEN_genTracks_pt_abseta_syst"},
                             "HighPtID": {"SF": "RunBCDEF_SF_ID_syst.root==NUM_HighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta",
                                          "STAT": "RunBCDEF_SF_ID_syst.root==NUM_HighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_stat",
                                          "SYST": "RunBCDEF_SF_ID_syst.root==NUM_HighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_syst"},
                             "TrkHighPtID": {"SF": "RunBCDEF_SF_ID_syst.root==NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta",
                                             "STAT": "RunBCDEF_SF_ID_syst.root==NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_stat",
                                             "SYST": "RunBCDEF_SF_ID_syst.root==NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_syst"},
                             "SoftID": {"SF": "RunBCDEF_SF_ID_syst.root==NUM_SoftID_DEN_genTracks_pt_abseta",
                                        "STAT": "RunBCDEF_SF_ID_syst.root==NUM_SoftID_DEN_genTracks_pt_abseta_stat",
                                        "SYST": "RunBCDEF_SF_ID_syst.root==NUM_SoftID_DEN_genTracks_pt_abseta_syst"},
                             "LooseRelIso/LooseID": {"SF": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelIso_DEN_LooseID_pt_abseta",
                                                     "STAT": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelIso_DEN_LooseID_pt_abseta_stat",
                                                     "SYST": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelIso_DEN_LooseID_pt_abseta_syst"},
                             "LooseRelIso/MediumID": {"SF": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelIso_DEN_MediumID_pt_abseta",
                                                      "STAT": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelIso_DEN_MediumID_pt_abseta_stat",
                                                      "SYST": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelIso_DEN_MediumID_pt_abseta_syst"},
                             "TightRelIso/MediumID": {"SF": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelIso_DEN_MediumID_pt_abseta",
                                                      "STAT": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelIso_DEN_MediumID_pt_abseta_stat",
                                                      "SYST": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelIso_DEN_MediumID_pt_abseta_syst"},
                             "LooseRelIso/TightIDandIPCut": {"SF": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta",
                                                             "STAT": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_stat",
                                                             "SYST": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_syst"},
                             "TightRelIso/TightIDandIPCut": {"SF": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta",
                                                             "STAT": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_stat",
                                                             "SYST": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_syst"},
                             "LooseRelTkIso/TrkHighPtID": {"SF": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta",
                                                           "STAT": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat",
                                                           "SYST": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst"},
                             "TightRelTkIso/TrkHighPtID": {"SF": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta",
                                                           "STAT": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat",
                                                           "SYST": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst"},
                             "LooseRelTkIso/HighPtIDandIPCut": {"SF": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta",
                                                                "STAT": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat",
                                                                "SYST": "RunBCDEF_SF_ISO_syst.root==NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst"},
                             "TightRelTkIso/HighPtIDandIPCut": {"SF": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta",
                                                                "STAT": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat",
                                                                "SYST": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst"}   
                         },
                    "2018": {"TRG_SL_preRun316361": {"SF": "EfficienciesAndSF_2018Data_BeforeMuonHLTUpdate.root==IsoMu24_PtEtaBins/pt_abseta_ratio",
                                                     "STAT": "EfficienciesAndSF_2018Data_BeforeMuonHLTUpdate.root==IsoMu24_PtEtaBins/pt_abseta_ratio"},
                             "TRG_SL": {"SF": "EfficienciesAndSF_2018Data_AfterMuonHLTUpdate.root==IsoMu24_PtEtaBins/pt_abseta_ratio",
                                        "STAT": "EfficienciesAndSF_2018Data_AfterMuonHLTUpdate.root==IsoMu24_PtEtaBins/pt_abseta_ratio"},
                             "LooseID": {"SF": "RunABCD_SF_ID.root==NUM_LooseID_DEN_TrackerMuons_pt_abseta",
                                         "STAT": "RunABCD_SF_ID.root==NUM_LooseID_DEN_TrackerMuons_pt_abseta_stat",
                                         "SYST": "RunABCD_SF_ID.root==NUM_LooseID_DEN_TrackerMuons_pt_abseta_syst"},
                             "MediumID": {"SF": "RunABCD_SF_ID.root==NUM_MediumID_DEN_TrackerMuons_pt_abseta",
                                          "STAT": "RunABCD_SF_ID.root==NUM_MediumID_DEN_TrackerMuons_pt_abseta_stat",
                                          "SYST": "RunABCD_SF_ID.root==NUM_MediumID_DEN_TrackerMuons_pt_abseta_syst"},
                             "TightID": {"SF": "RunABCD_SF_ID.root==NUM_TightID_DEN_TrackerMuons_pt_abseta",
                                         "STAT": "RunABCD_SF_ID.root==NUM_TightID_DEN_TrackerMuons_pt_abseta_stat",
                                         "SYST": "RunABCD_SF_ID.root==NUM_TightID_DEN_TrackerMuons_pt_abseta_syst"},
                             "HighPtID": {"SF": "RunABCD_SF_ID.root==NUM_HighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta",
                                          "STAT": "RunABCD_SF_ID.root==NUM_HighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta_stat",
                                          "SYST": "RunABCD_SF_ID.root==NUM_HighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta_syst"},
                             "TrkHighPtID": {"SF": "RunABCD_SF_ID.root==NUM_TrkHighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta",
                                             "STAT": "RunABCD_SF_ID.root==NUM_TrkHighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta_stat",
                                             "SYST": "RunABCD_SF_ID.root==NUM_TrkHighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta_syst"},
                             "SoftID": {"SF": "RunABCD_SF_ID.root==NUM_SoftID_DEN_TrackerMuons_pt_abseta",
                                        "STAT": "RunABCD_SF_ID.root==NUM_SoftID_DEN_TrackerMuons_pt_abseta_stat",
                                        "SYST": "RunABCD_SF_ID.root==NUM_SoftID_DEN_TrackerMuons_pt_abseta_syst"},
                             "MediumPromptID": {"SF": "RunABCD_SF_ID.root==NUM_MediumPromptID_DEN_TrackerMuons_pt_abseta",
                                                "STAT": "RunABCD_SF_ID.root==NUM_MediumPromptID_DEN_TrackerMuons_pt_abseta_stat",
                                                "SYST": "RunABCD_SF_ID.root==NUM_MediumPromptID_DEN_TrackerMuons_pt_abseta_syst"},
                             "LooseRelIso/LooseID": {"SF": "RunABCD_SF_ISO.root==NUM_LooseRelIso_DEN_LooseID_pt_abseta",
                                                     "STAT": "RunABCD_SF_ISO.root==NUM_LooseRelIso_DEN_LooseID_pt_abseta_stat",
                                                     "SYST": "RunABCD_SF_ISO.root==NUM_LooseRelIso_DEN_LooseID_pt_abseta_syst"},
                             "LooseRelIso/MediumID": {"SF": "RunABCD_SF_ISO.root==NUM_LooseRelIso_DEN_MediumID_pt_abseta",
                                                      "STAT": "RunABCD_SF_ISO.root==NUM_LooseRelIso_DEN_MediumID_pt_abseta_stat",
                                                      "SYST": "RunABCD_SF_ISO.root==NUM_LooseRelIso_DEN_MediumID_pt_abseta_syst"},
                             "LooseRelIso/TightIDandIPCut": {"SF": "RunABCD_SF_ISO.root==NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta",
                                                             "STAT": "RunABCD_SF_ISO.root==NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_stat",
                                                             "SYST": "RunABCD_SF_ISO.root==NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_syst"},
                             "TightRelIso/MediumID": {"SF": "RunABCD_SF_ISO.root==NUM_TightRelIso_DEN_MediumID_pt_abseta",
                                                      "STAT": "RunABCD_SF_ISO.root==NUM_TightRelIso_DEN_MediumID_pt_abseta_stat",
                                                      "SYST": "RunABCD_SF_ISO.root==NUM_TightRelIso_DEN_MediumID_pt_abseta_syst"},
                             "TightRelIso/TightIDandIPCut": {"SF": "RunABCD_SF_ISO.root==NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta",
                                                             "STAT": "RunABCD_SF_ISO.root==NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_stat",
                                                             "SYST": "RunABCD_SF_ISO.root==NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_syst"},
                             "LooseRelTkIso/TrkHighPtID": {"SF": "RunABCD_SF_ISO.root==NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta",
                                                           "STAT": "RunABCD_SF_ISO.root==NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat",
                                                           "SYST": "RunABCD_SF_ISO.root==NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst"},
                             "LooseRelTkIso/HighPtIDandIPCut": {"SF": "RunABCD_SF_ISO.root==NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta",
                                                                "STAT": "RunABCD_SF_ISO.root==NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat",
                                                                "SYST": "RunABCD_SF_ISO.root==NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst"},
                             "TightRelTkIso/TrkHighPtID": {"SF": "RunABCD_SF_ISO.root==NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta",
                                                           "STAT": "RunABCD_SF_ISO.root==NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat",
                                                           "SYST": "RunABCD_SF_ISO.root==NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst"},
                             "TightRelTkIso/HighPtIDandIPCut": {"SF": "RunABCD_SF_ISO.root==NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta",
                                                                "STAT": "RunABCD_SF_ISO.root==NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat",
                                                                "SYST": "RunABCD_SF_ISO.root==NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst"}
                         }
                }

        el_pre = "{0:s}/src/PhysicsTools/NanoAODTools/python/postprocessing/data/leptonSF/Electron/{1:s}/".format(os.environ['CMSSW_BASE'], self.era)
        mu_pre = "{0:s}/src/PhysicsTools/NanoAODTools/python/postprocessing/data/leptonSF/Muon/{1:s}/".format(os.environ['CMSSW_BASE'], self.era)

        self.el_eff = ROOT.std.vector(str)(1)
        self.el_eff_lowEt = ROOT.std.vector(str)(1)
        self.el_id = ROOT.std.vector(str)(1)
        self.el_eff_h = ROOT.std.vector(str)(1)
        self.el_eff_lowEt_h = ROOT.std.vector(str)(1)
        self.el_id_h = ROOT.std.vector(str)(1)
        self.el_eff[0] = el_pre + self.elD[self.era]["EFF"]["SF"].split("==")[0]
        self.el_eff_h[0] = self.elD[self.era]["EFF"]["SF"].split("==")[1]
        self.el_id[0] = el_pre + self.elD[self.era][self.electron_ID]["SF"].split("==")[0]
        self.el_id_h[0] = self.elD[self.era][self.electron_ID]["SF"].split("==")[1]
        if self.era == "2017" or self.era == "2016":
            self.el_eff_lowEt[0] = el_pre + self.elD[self.era]["EFF_lowEt"]["SF"].split("==")[0]
            self.el_eff_lowEt_h[0] = self.elD[self.era]["EFF_lowEt"]["SF"].split("==")[1]

        if self.doMuonHLT:
            self.mu_hlt_nom = ROOT.std.vector(str)(1)
            self.mu_hlt_stat = ROOT.std.vector(str)(1)
            self.mu_hlt_nom_h = ROOT.std.vector(str)(1)
            self.mu_hlt_stat_h = ROOT.std.vector(str)(1)
            if self.era == "2018":
                self.mu_hltpre316361_nom = ROOT.std.vector(str)(1)
                self.mu_hltpre316361_stat = ROOT.std.vector(str)(1)
                self.mu_hltpre316361_nom_h = ROOT.std.vector(str)(1)
                self.mu_hltpre316361_stat_h = ROOT.std.vector(str)(1)
        self.mu_id_nom = ROOT.std.vector(str)(1)
        self.mu_id_stat = ROOT.std.vector(str)(1)
        self.mu_id_syst = ROOT.std.vector(str)(1)
        self.mu_iso_nom = ROOT.std.vector(str)(1)
        self.mu_iso_stat = ROOT.std.vector(str)(1)
        self.mu_iso_syst = ROOT.std.vector(str)(1)
        self.mu_id_nom_h = ROOT.std.vector(str)(1)
        self.mu_id_stat_h = ROOT.std.vector(str)(1)
        self.mu_id_syst_h = ROOT.std.vector(str)(1)
        self.mu_iso_nom_h = ROOT.std.vector(str)(1)
        self.mu_iso_stat_h = ROOT.std.vector(str)(1)
        self.mu_iso_syst_h = ROOT.std.vector(str)(1)

        if self.doMuonHLT:
            self.mu_hlt_nom[0] = mu_pre + self.muD[self.era]["TRG_SL"]["SF"].split("==")[0]
            self.mu_hlt_nom_h[0] = self.muD[self.era]["TRG_SL"]["SF"].split("==")[1]
            self.mu_hlt_stat[0] = mu_pre + self.muD[self.era]["TRG_SL"]["STAT"].split("==")[0]
            self.mu_hlt_stat_h[0] = self.muD[self.era]["TRG_SL"]["STAT"].split("==")[1]
            if self.era == "2018":
                self.mu_hltpre316361_nom[0] = mu_pre + self.muD[self.era]["TRG_SL_preRun316361"]["SF"].split("==")[0]
                self.mu_hltpre316361_nom_h[0] = self.muD[self.era]["TRG_SL_preRun316361"]["SF"].split("==")[1]
                self.mu_hltpre316361_stat[0] = mu_pre + self.muD[self.era]["TRG_SL_preRun316361"]["STAT"].split("==")[0]
                self.mu_hltpre316361_stat_h[0] = self.muD[self.era]["TRG_SL_preRun316361"]["STAT"].split("==")[1]
        self.mu_id_nom[0] = mu_pre + self.muD[self.era][self.muon_ID]["SF"].split("==")[0]
        self.mu_id_nom_h[0] = self.muD[self.era][self.muon_ID]["SF"].split("==")[1]
        self.mu_id_stat[0] = mu_pre + self.muD[self.era][self.muon_ID]["STAT"].split("==")[0]
        self.mu_id_stat_h[0] = self.muD[self.era][self.muon_ID]["STAT"].split("==")[1]
        self.mu_iso_nom[0] = mu_pre + self.muD[self.era][self.muon_ISO]["SF"].split("==")[0]
        self.mu_iso_nom_h[0] = self.muD[self.era][self.muon_ISO]["SF"].split("==")[1]
        self.mu_iso_stat[0] = mu_pre + self.muD[self.era][self.muon_ISO]["STAT"].split("==")[0]
        self.mu_iso_stat_h[0] = self.muD[self.era][self.muon_ISO]["STAT"].split("==")[1]
        if self.era == "2017" or self.era == "2018":
            self.mu_id_syst[0] = mu_pre + self.muD[self.era][self.muon_ID]["SYST"].split("==")[0]
            self.mu_id_syst_h[0] = self.muD[self.era][self.muon_ID]["SYST"].split("==")[1]
            self.mu_iso_syst[0] = mu_pre + self.muD[self.era][self.muon_ISO]["SYST"].split("==")[0]
            self.mu_iso_syst_h[0] = self.muD[self.era][self.muon_ISO]["SYST"].split("==")[1]


        if "/LeptonEfficiencyCorrector_cc.so" not in ROOT.gSystem.GetLibraries():
            print "Load C++ Worker"
            ROOT.gROOT.ProcessLine(".L %s/src/PhysicsTools/NanoAODTools/python/postprocessing/helpers/LeptonEfficiencyCorrector.cc+" % os.environ['CMSSW_BASE'])
    def beginJob(self):
        if self.era == "2016":
            print("2016 Muon Scale Factors are not fully updated, do not account for weighted SF for era GH versus earlier, and do not include systematics")
        if self.doMuonHLT:
            self._worker_mu_HLT_nom = ROOT.LeptonEfficiencyCorrector(self.mu_hlt_nom, self.mu_hlt_nom_h)
            self._worker_mu_HLT_stat = ROOT.LeptonEfficiencyCorrector(self.mu_hlt_stat, self.mu_hlt_stat_h)
            if self.era == "2018":
                print("2018 Single Lepton Muon HLT Scale Factors are weighted between one set before Run2018A (run < 316361) and another set for Run2018ABCD (run >= 316361)."\
                      "If not using all of 2018, use brilcalc and pass the lumi in /fb to pre2018Run316361Lumi and post2018Run316361Lumi")
                self._worker_mu_HLTpreRun316361_nom = ROOT.LeptonEfficiencyCorrector(self.mu_hltpre316361_nom, self.mu_hltpre316361_nom_h)
                self._worker_mu_HLTpreRun316361_stat = ROOT.LeptonEfficiencyCorrector(self.mu_hltpre316361_stat, self.mu_hltpre316361_stat_h)
        self._worker_mu_ID_nom = ROOT.LeptonEfficiencyCorrector(self.mu_id_nom, self.mu_id_nom_h)
        self._worker_mu_ID_stat = ROOT.LeptonEfficiencyCorrector(self.mu_id_stat, self.mu_id_stat_h)
        self._worker_mu_ISO_nom = ROOT.LeptonEfficiencyCorrector(self.mu_iso_nom, self.mu_iso_nom_h)
        self._worker_mu_ISO_stat = ROOT.LeptonEfficiencyCorrector(self.mu_iso_stat, self.mu_iso_stat_h)
        if self.era == "2017" or self.era == "2018":
            self._worker_mu_ID_syst = ROOT.LeptonEfficiencyCorrector(self.mu_id_syst, self.mu_id_syst_h)
            self._worker_mu_ISO_syst = ROOT.LeptonEfficiencyCorrector(self.mu_iso_syst, self.mu_iso_syst_h)

        self._worker_el_EFF = ROOT.LeptonEfficiencyCorrector(self.el_eff, self.el_eff_h)
        if self.era == "2017" or self.era == "2016":
            self._worker_el_EFF_lowEt = ROOT.LeptonEfficiencyCorrector(self.el_eff_lowEt, self.el_eff_lowEt_h)
        self._worker_el_ID = ROOT.LeptonEfficiencyCorrector(self.el_id, self.el_id_h)
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        if self.doMuonHLT:
            self.out.branch("Muon_SF_HLT_nom", "F",  lenVar="nMuon", title="Muon Single Lepton HLT SF")
            self.out.branch("Muon_SF_HLT_stat", "F", lenVar="nMuon", title="Muon Single Lepton HLT SF stat uncertainty")
        if self.doElectronHLT_ZVtx:
            self.out.branch("EGamma_HLT_ZVtx_SF_nom", "F", title="EGamma HLT Z_vtx Scale Factor for era={0:s}".format(self.era))
            self.out.branch("EGamma_HLT_ZVtx_SF_unc", "F", title="EGamma HLT Z_vtx Scale Factor for era={0:s}".format(self.era))
        self.out.branch("Muon_SF_ID_nom", "F",  lenVar="nMuon", title="Muon ID SF ({0:s}) for era={1:s}".format(self.muon_ID, self.era))
        self.out.branch("Muon_SF_ID_stat", "F", lenVar="nMuon", title="Muon ID SF stat uncertainty ({0:s}) for era={1:s}".format(self.muon_ID, self.era))
        self.out.branch("Muon_SF_ID_syst", "F", lenVar="nMuon", title="Muon ID SF syst uncertainty ({0:s}) for era={1:s}".format(self.muon_ID, self.era + " syst is not properly fetched, stored as 0" if self.era == "2016" else self.era))
        self.out.branch("Muon_SF_ISO_nom", "F", lenVar="nMuon", title="Muon ISO SF ({0:s}) for era={1:s}".format(self.muon_ISO, self.era))
        self.out.branch("Muon_SF_ISO_stat", "F", lenVar="nMuon", title="Muon ISO SF stat uncertainty ({0:s}) for era={1:s}".format(self.muon_ISO, self.era))
        self.out.branch("Muon_SF_ISO_syst", "F", lenVar="nMuon", title="Muon ISO SF syst uncertainty ({0:s}) for era={1:s}".format(self.muon_ISO, self.era + " syst is not properly fetched, stored as 0" if self.era == "2016" else self.era))

        self.out.branch("Electron_SF_EFF_nom", "F", lenVar="nElectron", title="Electron Efficiency SF for era={0:s}".format(self.era))
        self.out.branch("Electron_SF_EFF_unc", "F", lenVar="nElectron", title="Electron Efficiency SF uncertainty for era={0:s}".format(self.era))
        self.out.branch("Electron_SF_ID_nom", "F", lenVar="nElectron", title="Electron ID SF ({0:s}) for era={1:s}".format(self.electron_ID, self.era))
        self.out.branch("Electron_SF_ID_unc", "F", lenVar="nElectron", title="Electron ID SF uncertainty ({0:s}) for era={1:s}".format(self.electron_ID, self.era))
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        muons = Collection(event, "Muon")
        electrons = Collection(event, "Electron")

        sf_el_eff_nom = []
        sf_el_eff_unc = []
        sf_el_id_nom = []
        sf_el_id_unc = []        
        for el in electrons:
            #Efficiency SFs, split into low and high Et for 2016 and 2017
            if self.era != "2018" and el.pt < 20: 
                sf_el_eff_nom.append(self._worker_el_EFF_lowEt.getSF(el.pdgId, el.pt, el.eta))
                sf_el_eff_unc.append(self._worker_el_EFF_lowEt.getSFErr(el.pdgId, el.pt, el.eta))
                if self.debug: print("EL EFF: pt={0:5.2f} eta={1:5.2f} sf={2:5.6f} unc={3:5.2f}".format(el.pt, el.eta, sf_el_eff_nom[-1], sf_el_eff_unc[-1]))
            else:
                sf_el_eff_nom.append(self._worker_el_EFF.getSF(el.pdgId, el.pt, el.eta))
                sf_el_eff_unc.append(self._worker_el_EFF.getSFErr(el.pdgId, el.pt, el.eta))
                if self.debug: print("EL EFF: pt={0:5.2f} eta={1:5.2f} sf={2:5.6f} unc={3:5.2f}".format(el.pt, el.eta, sf_el_eff_nom[-1], sf_el_eff_unc[-1]))
            #ID SFs
            sf_el_id_nom.append(self._worker_el_ID.getSF(el.pdgId, el.pt, el.eta))
            sf_el_id_unc.append(self._worker_el_ID.getSFErr(el.pdgId, el.pt, el.eta))
            if self.debug: print("EL ID: ALGO={0:s} pt={1:5.2f} eta={2:5.2f} sf={3:5.6f} unc={4:5.2f}".format(self.electron_ID, el.pt, el.eta, sf_el_id_nom[-1], sf_el_id_unc[-1]))

        sf_mu_hlt_nom = []
        sf_mu_hlt_stat = []
        sf_mu_id_nom = []
        sf_mu_id_stat = []
        sf_mu_id_syst = []
        sf_mu_iso_nom = []
        sf_mu_iso_stat = []
        sf_mu_iso_syst = []
        for mu in muons:
            #SL HLT SFs
            if self.doMuonHLT:
                if self.era == "2018":
                    HLTnomSF = self.pre2018Run316361Lumi * self._worker_mu_HLTpreRun316361_nom.getSF(mu.pdgId, mu.pt, mu.eta) + self.post2018Run316361Lumi * self._worker_mu_HLT_nom.getSF(mu.pdgId, mu.pt, mu.eta)
                    HLTnomSF /= (self.pre2018Run316361Lumi + self.post2018Run316361Lumi)
                    HLTstatSF = self.pre2018Run316361Lumi * self._worker_mu_HLTpreRun316361_stat.getSFErr(mu.pdgId, mu.pt, mu.eta) + self.post2018Run316361Lumi * self._worker_mu_HLT_stat.getSFErr(mu.pdgId, mu.pt, mu.eta)
                    HLTstatSF /= (self.pre2018Run316361Lumi + self.post2018Run316361Lumi)
                else:
                    HLTnomSF = self._worker_mu_HLT_nom.getSF(mu.pdgId, mu.pt, mu.eta)
                    HLTstatSF = self._worker_mu_HLT_stat.getSFErr(mu.pdgId, mu.pt, mu.eta)
                sf_mu_hlt_nom.append(HLTnomSF)
                sf_mu_hlt_stat.append(HLTstatSF)
            #ID SFs
            sf_mu_id_nom.append(self._worker_mu_ID_nom.getSF(mu.pdgId, mu.pt, mu.eta))
            sf_mu_id_stat.append(self._worker_mu_ID_stat.getSFErr(mu.pdgId, mu.pt, mu.eta))
            sf_mu_id_syst.append(0.0 if self.era == "2016" else self._worker_mu_ID_syst.getSFErr(mu.pdgId, mu.pt, mu.eta))
            if self.debug: print("MU ID: ALGO={0:s} pt={1:5.2f} |eta|={2:5.2f} sf={3:5.6f} stat={4:5.2f} syst={5:5.2f}".format(self.muon_ID, mu.pt, abs(mu.eta), sf_mu_id_nom[-1], sf_mu_id_stat[-1], sf_mu_id_syst[-1]))
            #ISO SFs
            sf_mu_iso_nom.append(self._worker_mu_ISO_nom.getSF(mu.pdgId, mu.pt, mu.eta))
            sf_mu_iso_stat.append(self._worker_mu_ISO_stat.getSFErr(mu.pdgId, mu.pt, mu.eta))
            sf_mu_iso_syst.append(0.0 if self.era == "2016" else self._worker_mu_ISO_syst.getSFErr(mu.pdgId, mu.pt, mu.eta))
            if self.debug: print("MU ISO: ALGO={0:s} pt={1:5.2f} |eta|={2:5.2f} sf={3:5.6f} stat={4:5.2f} syst={5:5.2f}".format(self.muon_ISO, mu.pt, abs(mu.eta), sf_mu_iso_nom[-1], sf_mu_iso_stat[-1], sf_mu_iso_syst[-1]))

        self.out.fillBranch("Electron_SF_EFF_nom", sf_el_eff_nom)
        self.out.fillBranch("Electron_SF_EFF_unc", sf_el_eff_unc)
        self.out.fillBranch("Electron_SF_ID_nom", sf_el_id_nom)
        self.out.fillBranch("Electron_SF_ID_unc", sf_el_id_unc)

        if self.doMuonHLT:
            self.out.fillBranch("Muon_SF_HLT_nom", sf_mu_hlt_nom)
            self.out.fillBranch("Muon_SF_HLT_stat", sf_mu_hlt_stat)
        if self.doElectronHLT_ZVtx:
            #https://twiki.cern.ch/twiki/bin/view/CMS/EgammaRunIIRecommendations#HLT_Zvtx_Scale_Factor
            self.out.fillBranch("EGamma_HLT_ZVtx_SF_nom", 0.991 if self.era=="2017" else 1.0)
            self.out.fillBranch("EGamma_HLT_ZVtx_SF_unc", 0.001 if self.era=="2017" else 0.0)

        self.out.fillBranch("Muon_SF_ID_nom", sf_mu_id_nom)
        self.out.fillBranch("Muon_SF_ID_stat", sf_mu_id_stat)
        self.out.fillBranch("Muon_SF_ID_syst", sf_mu_id_syst)
        self.out.fillBranch("Muon_SF_ISO_nom", sf_mu_iso_nom)
        self.out.fillBranch("Muon_SF_ISO_stat", sf_mu_iso_stat)
        self.out.fillBranch("Muon_SF_ISO_syst", sf_mu_iso_syst)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# 2017_elTight_muTightTight = lambda : lepSplitSFProducer(muon_ID="TightID", muon_ISO="TightRelIso/TightIDandIPCut", electron_ID="TightID", era="2017")
# 2017_elLoose_muLooseLoose = lambda : lepSplitSFProducer(muon_ID="LooseID", muon_ISO="LooseRelIso/LooseID", electron_ID="LooseID", era="2017")

