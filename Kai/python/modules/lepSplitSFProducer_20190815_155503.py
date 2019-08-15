import ROOT
import os
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class lepSplitSFProducer(Module):
    def __init__(self, muon_ID=None, muon_ISO=None, electron_ID=None, era=None, debug=False):
        self.era = era
        self.muon_ID = muon_ID
        self.muon_ISO = muon_ISO
        self.electron_ID = electron_ID
        self.debug = debug
        self.elD = {"2016": {"TRG_SL": {"SF": "INVALID"}
                             },
                    "2017": {"TRG_SL": {"SF": "INVALID"},
                             "EFF": {"SF": "egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root==EGamma_SF2D"},
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
                    "2018": {"TRG_SL": {"SF": "INVALID"},
                             "EFF": {"SF": "egammaEffi.txt_EGM2D_updatedAll.root==EGamma_SF2D"},
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

        self.muD = {"2016": {"INVALID": "INVALID"},
                    "2017": {"TRG_SL": {"SF": "EfficienciesAndSF_RunBtoF_Nov17Nov2017.root==IsoMu27_PtEtaBins/pt_abseta_ratio"},
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
                    "2018": {"TRG_SL": {"SF": "INVALID"},
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
                             "LooseRelIso/MediumId": {"SF": "RunABCD_SF_ISO.root==NUM_LooseRelIso_DEN_MediumID_pt_abseta",
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
        if self.era == "2017":
            self.el_eff_lowEt[0] = el_pre + self.elD[self.era]["EFF_lowEt"]["SF"].split("==")[0]
            self.el_eff_lowEt_h[0] = self.elD[self.era]["EFF_lowEt"]["SF"].split("==")[1]

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

        self.mu_id_nom[0] = mu_pre + self.muD[self.era][self.muon_ID]["SF"].split("==")[0]
        self.mu_id_nom_h[0] = self.muD[self.era][self.muon_ID]["SF"].split("==")[1]
        self.mu_id_stat[0] = mu_pre + self.muD[self.era][self.muon_ID]["STAT"].split("==")[0]
        self.mu_id_stat_h[0] = self.muD[self.era][self.muon_ID]["STAT"].split("==")[1]
        self.mu_id_syst[0] = mu_pre + self.muD[self.era][self.muon_ID]["SYST"].split("==")[0]
        self.mu_id_syst_h[0] = self.muD[self.era][self.muon_ID]["SYST"].split("==")[1]
        self.mu_iso_nom[0] = mu_pre + self.muD[self.era][self.muon_ISO]["SF"].split("==")[0]
        self.mu_iso_nom_h[0] = self.muD[self.era][self.muon_ISO]["SF"].split("==")[1]
        self.mu_iso_stat[0] = mu_pre + self.muD[self.era][self.muon_ISO]["STAT"].split("==")[0]
        self.mu_iso_stat_h[0] = self.muD[self.era][self.muon_ISO]["STAT"].split("==")[1]
        self.mu_iso_syst[0] = mu_pre + self.muD[self.era][self.muon_ISO]["SYST"].split("==")[0]
        self.mu_iso_syst_h[0] = self.muD[self.era][self.muon_ISO]["SYST"].split("==")[1]

        if "/LeptonEfficiencyCorrector_cc.so" not in ROOT.gSystem.GetLibraries():
            print "Load C++ Worker"
            ROOT.gROOT.ProcessLine(".L %s/src/PhysicsTools/NanoAODTools/python/postprocessing/helpers/LeptonEfficiencyCorrector.cc+" % os.environ['CMSSW_BASE'])
    def beginJob(self):
        self._worker_mu_ID_nom = ROOT.LeptonEfficiencyCorrector(self.mu_id_nom, self.mu_id_nom_h)
        self._worker_mu_ID_stat = ROOT.LeptonEfficiencyCorrector(self.mu_id_stat, self.mu_id_stat_h)
        self._worker_mu_ID_syst = ROOT.LeptonEfficiencyCorrector(self.mu_id_syst, self.mu_id_syst_h)
        self._worker_mu_ISO_nom = ROOT.LeptonEfficiencyCorrector(self.mu_iso_nom, self.mu_iso_nom_h)
        self._worker_mu_ISO_stat = ROOT.LeptonEfficiencyCorrector(self.mu_iso_stat, self.mu_iso_stat_h)
        self._worker_mu_ISO_syst = ROOT.LeptonEfficiencyCorrector(self.mu_iso_syst, self.mu_iso_syst_h)

        self._worker_el_EFF = ROOT.LeptonEfficiencyCorrector(self.el_eff, self.el_eff_h)
        if self.era == "2017":
            self._worker_el_EFF_lowEt = ROOT.LeptonEfficiencyCorrector(self.el_eff_lowEt, self.el_eff_lowEt_h)
        self._worker_el_ID = ROOT.LeptonEfficiencyCorrector(self.el_id, self.el_id_h)
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Muon_SF_ID_nom", "F",  lenVar="nMuon", title="Muon ID SF ({0:s})".format(self.muon_ID))
        self.out.branch("Muon_SF_ID_stat", "F", lenVar="nMuon", title="Muon ID SF stat uncertainty ({0:s})".format(self.muon_ID))
        self.out.branch("Muon_SF_ID_syst", "F", lenVar="nMuon", title="Muon ID SF syst uncertainty ({0:s})".format(self.muon_ID))
        self.out.branch("Muon_SF_ISO_nom", "F", lenVar="nMuon", title="Muon ISO SF ({0:s})".format(self.muon_ISO))
        self.out.branch("Muon_SF_ISO_stat", "F", lenVar="nMuon", title="Muon ISO SF stat uncertainty ({0:s})".format(self.muon_ISO))
        self.out.branch("Muon_SF_ISO_syst", "F", lenVar="nMuon", title="Muon ISO SF syst uncertainty ({0:s})".format(self.muon_ISO))

        self.out.branch("Electron_SF_EFF_nom", "F", lenVar="nElectron", title="Electron Efficiency SF")
        self.out.branch("Electron_SF_EFF_unc", "F", lenVar="nElectron", title="Electron Efficiency SF uncertainty")
        self.out.branch("Electron_SF_ID_nom", "F", lenVar="nElectron", title="Electron ID SF ({0:s})".format(self.electron_ID))
        self.out.branch("Electron_SF_ID_unc", "F", lenVar="nElectron", title="Electron ID SF uncertainty ({0:s})".format(self.electron_ID))
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
            #Efficiency SFs
            if self.era == "2017" and el.pt < 20:
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

        sf_mu_id_nom = []
        sf_mu_id_stat = []
        sf_mu_id_syst = []
        sf_mu_iso_nom = []
        sf_mu_iso_stat = []
        sf_mu_iso_syst = []
        for mu in muons:
            #ID SFs
            sf_mu_id_nom.append(self._worker_mu_ID_nom.getSF(mu.pdgId, mu.pt, mu.eta))
            sf_mu_id_stat.append(self._worker_mu_ID_stat.getSFErr(mu.pdgId, mu.pt, mu.eta))
            sf_mu_id_syst.append(self._worker_mu_ID_syst.getSFErr(mu.pdgId, mu.pt, mu.eta))
            if self.debug: print("MU ID: ALGO={0:s} pt={1:5.2f} |eta|={2:5.2f} sf={3:5.6f} stat={4:5.2f} syst={5:5.2f}".format(self.muon_ID, mu.pt, abs(mu.eta), sf_mu_id_nom[-1], sf_mu_id_stat[-1], sf_mu_id_syst[-1]))
            #ISO SFs
            sf_mu_iso_nom.append(self._worker_mu_ISO_nom.getSF(mu.pdgId, mu.pt, mu.eta))
            sf_mu_iso_stat.append(self._worker_mu_ISO_stat.getSFErr(mu.pdgId, mu.pt, mu.eta))
            sf_mu_iso_syst.append(self._worker_mu_ISO_syst.getSFErr(mu.pdgId, mu.pt, mu.eta))
            if self.debug: print("MU ISO: ALGO={0:s} pt={1:5.2f} |eta|={2:5.2f} sf={3:5.6f} stat={4:5.2f} syst={5:5.2f}".format(self.muon_ISO, mu.pt, abs(mu.eta), sf_mu_iso_nom[-1], sf_mu_iso_stat[-1], sf_mu_iso_syst[-1]))

        self.out.fillBranch("Electron_SF_EFF_nom", sf_el_eff_nom)
        self.out.fillBranch("Electron_SF_EFF_unc", sf_el_eff_unc)
        self.out.fillBranch("Electron_SF_ID_nom", sf_el_id_nom)
        self.out.fillBranch("Electron_SF_ID_unc", sf_el_eff_unc)

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

