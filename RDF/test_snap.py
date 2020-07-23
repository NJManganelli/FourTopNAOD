import ROOT
import pdb
import time, collections, array
ROOT.ROOT.EnableImplicitMT(8)

systematics_2017 = {"$NOMINAL": {"jet_mask": "jet_mask",
                                 "lep_postfix": "",
                                 "wgt_final": "wgt__nom",
                                 "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                 "jet_pt_var": "Jet_pt",
                                 "jet_mass_var": "Jet_mass",
                                 "met_pt_var": "METFixEE2017_pt",
                                 "met_phi_var": "METFixEE2017_phi",
                                 "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                            "DeepJet": "Jet_btagSF_deepjet_shape",
                                        },
                                 "weightVariation": False},
                    "jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp",
                                   "lep_postfix": "",
                                   "wgt_final": "wgt__jesTotalUp",
                                   "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                   "jet_pt_var": "Jet_pt_jesTotalUp",
                                   "jet_mass_var": "Jet_mass_jesTotalUp",
                                   "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                   "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                   "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                              "DeepJet": "Jet_btagSF_deepjet_shape",
                                          },
                                   "weightVariation": False},
                    "jesTotalDown": {"jet_mask": "jet_mask_jesTotalDown",
                                     "lep_postfix": "",
                                     "wgt_final": "wgt__jesTotalDown", 
                                     "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                     "jet_pt_var": "Jet_pt_jesTotalDown",
                                     "jet_mass_var": "Jet_mass_jesTotalDown",
                                     "met_pt_var": "METFixEE2017_pt_jesTotalDown",
                                     "met_phi_var": "METFixEE2017_phi_jesTotalDown",
                                     "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                                "DeepJet": "Jet_btagSF_deepjet_shape",
                                            },
                                     "weightVariation": False},
                    "btagSF_deepcsv_shape_up_hf": {"jet_mask": "jet_mask",
                                                   "lep_postfix": "", 
                                                   "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                   "jet_pt_var": "Jet_pt",
                                                   "btagSF":{"DeepCSV": "Jet_btagSF_deepcsv_shape_up_hf",
                                                             "DeepJet": "Jet_btagSF_deepjet_shape_up_hf",
                                                         },
                                                   "weightVariation": True},
                    "btagSF_deepcsv_shape_down_hf": {"jet_mask": "jet_mask",
                                                     "lep_postfix": "", 
                                                     "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                     "jet_pt_var": "Jet_pt",
                                                     "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape_down_hf",
                                                                "DeepJet": "Jet_btagSF_deepjet_shape_down_hf",
                                                            },
                                                     "weightVariation": True},
                    "btagSF_deepcsv_shape_up_lf": {"jet_mask": "jet_mask",
                                                   "lep_postfix": "", 
                                                   "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                   "jet_pt_var": "Jet_pt",
                                                   "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape_up_lf",
                                                              "DeepJet": "Jet_btagSF_deepjet_shape_up_lf",
                                                          },
                                                   "weightVariation": True},
                    "btagSF_deepcsv_shape_down_lf": {"jet_mask": "jet_mask",
                                                     "lep_postfix": "", 
                                                     "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                                     "jet_pt_var": "Jet_pt",
                                                     "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape_down_lf",
                                                                "DeepJet": "Jet_btagSF_deepjet_shape_down_lf",
                                                            },
                                                     "weightVariation": True},
                    "no_btag_shape_reweight": {"jet_mask": "jet_mask",
                                               "lep_postfix": "", 
                                               "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF", 
                                               "jet_pt_var": "Jet_pt",
                                               "btagSF": {"DeepCSV": "Jet_btagSF_deepcsv_shape",
                                                          "DeepJet": "Jet_btagSF_deepjet_shape",
                                                      },
                                               "weightVariation": True},
}
def defineLeptons(input_df, input_lvl_filter=None, isData=True, era="2017", rdfLeptonSelection=False, useBackupChannel=False, verbose=False,
                  triggers=[],
                 sysVariations={"$NOMINAL": {"jet_mask": "jet_mask", 
                                             "lep_postfix": "",
                                             "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                             "jet_pt_var": "Jet_pt",
                                             "jet_mass_var": "Jet_mass",
                                             "met_pt_var": "METFixEE2017_pt",
                                             "met_phi_var": "METFixEE2017_phi",
                                             "btagSF": "Jet_btagSF_deepcsv_shape",
                                             "weightVariation": False},
                                },
                 ):
    """Function to take in a dataframe and return one with new columns defined,
    plus event filtering based on the criteria defined inside the function"""
        
    #Set up channel bits for selection and baseline. Separation not necessary in this stage, but convenient for loops
    Chan = {}
    Chan["ElMu"] = 24576
    Chan["MuMu"] = 6144
    Chan["ElEl"] = 512
    Chan["ElEl_LowMET"] = Chan["ElEl"]
    Chan["ElEl_HighMET"] = Chan["ElEl"]
    Chan["Mu"] = 128
    Chan["El"] = 64
    Chan["selection"] = Chan["ElMu"] + Chan["MuMu"] + Chan["ElEl"] + Chan["Mu"] + Chan["El"]
    Chan["ElMu_baseline"] = 24576
    Chan["MuMu_baseline"] = 6144
    Chan["ElEl_baseline"] = 512
    Chan["Mu_baseline"] = 128
    Chan["El_baseline"] = 64
    Chan["baseline"] = Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"] + Chan["Mu_baseline"] + Chan["El_baseline"]
    b = {}
    b["baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) > 0".format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + 
                                                                            Chan["ElEl_baseline"] + Chan["Mu_baseline"] + Chan["El_baseline"])
    
    b["ElMu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) > 0".format(Chan["ElMu_baseline"])
    b["MuMu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"], Chan["MuMu_baseline"])
    b["ElEl_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"], Chan["ElEl_baseline"])
    b["Mu_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"], Chan["Mu_baseline"])
    b["El_baseline"] = "(ESV_TriggerAndLeptonLogic_baseline & {0}) == 0 && (ESV_TriggerAndLeptonLogic_baseline & {1}) > 0"\
        .format(Chan["ElMu_baseline"] + Chan["MuMu_baseline"] + Chan["ElEl_baseline"] + Chan["Mu_baseline"], Chan["El_baseline"])
    b["selection"] = "ESV_TriggerAndLeptonLogic_selection > 0"
    b["ElMu"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) > 0".format(Chan["ElMu"])
    b["MuMu"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"], Chan["MuMu"])
    b["ElEl"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"] + Chan["MuMu"], Chan["ElEl"])
    b["ElEl_LowMET"] = b["ElEl"]
    b["ElEl_HighMET"] = b["ElEl"]
    b["Mu"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"] + Chan["MuMu"] + Chan["ElEl"], Chan["Mu"])
    b["El"] = "(ESV_TriggerAndLeptonLogic_selection & {0}) == 0 && (ESV_TriggerAndLeptonLogic_selection & {1}) > 0"\
        .format(Chan["ElMu"] + Chan["MuMu"] + Chan["ElEl"] + Chan["Mu"], Chan["El"])
    if input_lvl_filter == None:
        rdf = input_df.Define("mu_mask", "Muon_pt > 0").Define("e_mask", "Electron_pt > 0")
    else:
        if "baseline" in input_lvl_filter:
            lvl_type = "baseline"
        else:
            lvl_type = "selection"
        rdf_input = input_df.Filter(b[input_lvl_filter], input_lvl_filter)
        rdf = rdf_input
        # for trgTup in triggers:
        #     if trgTup.era != era: continue
        #     trg = trgTup.trigger
        #     rdf = rdf.Define("typecast___{}".format(trg), "return (int){} == true;".format(trg))
        if not rdfLeptonSelection:
            rdf = rdf.Define("mu_mask", "(Muon_OSV_{0} & {1}) > 0 && Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_looseId == true && Muon_pfIsoId >= 4 && abs(Muon_ip3d) < 0.10 && abs(Muon_dz) < 0.02".format(lvl_type, Chan[input_lvl_filter]))
            rdf = rdf.Define("e_mask", "(Electron_OSV_{0} & {1}) > 0 && Electron_pt > 15 && Electron_cutBased >= 2 && ((abs(Electron_eta) < 1.4442 && abs(Electron_ip3d) < 0.05 && abs(Electron_dz) < 0.1) || (abs(Electron_eta) > 1.5660 && abs(Electron_eta) < 2.5 && abs(Electron_ip3d) < 0.10 && abs(Electron_dz) < 0.2))".format(lvl_type, Chan[input_lvl_filter]))
        else:
            pass
    transverseMassCode = '''auto MT2 = {m1}*{m1} + {m2}*{m2} + 2*(sqrt({m1}*{m1} + {pt1}*{pt1})*sqrt({m2}*{m2} + {pt2}*{pt2}) - {pt1}*{pt2}*cos(ROOT::VecOps::DeltaPhi({phi1}, {phi2})));
                         return sqrt(MT2);'''
    transverseMassCodeChannelSafe = '''
                         if( {pt1}.size() != {pt2}.size()){{ROOT::VecOps::RVec<float> v; v.push_back(-9999); return v;}}
                         else {{auto MT2 = {m1}*{m1} + {m2}*{m2} + 2*(sqrt({m1}*{m1} + {pt1}*{pt1})*sqrt({m2}*{m2} + {pt2}*{pt2}) - {pt1}*{pt2}*cos(ROOT::VecOps::DeltaPhi({phi1}, {phi2})));
                         return sqrt(MT2);
                         }}'''
    transverseMassCodeChecker = '''auto V1 = ROOT::Math::PtEtaPhiMVector({pt1}, {eta1}, {phi1}, {m1});
                                auto V2 = ROOT::Math::PtEtaPhiMVector({pt2}, {eta2}, {phi2}, {m2});
                                auto V = V1 + V2;
                                return V.Mt();'''
    transverseMassLightCode = '''auto MT2 = 2*{pt1}*{pt2}*(1 - cos(ROOT::VecOps::DeltaPhi({phi1}, {phi2})));
                              return sqrt(MT2);'''
    z = []
    #only valid postfix for leptons, excluding calculations involving MET, is "" for now, can become "__SOMETHING" inside a loop on systematic variations 
    leppostfix = ""
    
    #MUONS
    z.append(("Muon_idx", "FTA::generateIndices(Muon_pt);"))
    z.append(("nFTAMuon{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Muon_pt[mu_mask].size())"))
    z.append(("FTAMuon{lpf}_idx".format(lpf=leppostfix), "Muon_idx[mu_mask]"))
    z.append(("FTAMuon{lpf}_pfIsoId".format(lpf=leppostfix), "Muon_pfIsoId[mu_mask]"))
    z.append(("FTAMuon{lpf}_looseId".format(lpf=leppostfix), "Muon_looseId[mu_mask]"))
    z.append(("FTAMuon{lpf}_pt".format(lpf=leppostfix), "Muon_pt[mu_mask]"))
    z.append(("FTAMuon{lpf}_eta".format(lpf=leppostfix), "Muon_eta[mu_mask]"))
    z.append(("FTAMuon{lpf}_phi".format(lpf=leppostfix), "Muon_phi[mu_mask]"))
    z.append(("FTAMuon{lpf}_mass".format(lpf=leppostfix), "Muon_mass[mu_mask]"))
    z.append(("FTAMuon{lpf}_charge".format(lpf=leppostfix), "Muon_charge[mu_mask]"))
    z.append(("FTAMuon{lpf}_dz".format(lpf=leppostfix), "Muon_dz[mu_mask]"))
    z.append(("FTAMuon{lpf}_dxy".format(lpf=leppostfix), "Muon_dxy[mu_mask]"))
    z.append(("FTAMuon{lpf}_d0".format(lpf=leppostfix), "sqrt(Muon_dz*Muon_dz + Muon_dxy*Muon_dxy)[mu_mask]"))
    z.append(("FTAMuon{lpf}_ip3d".format(lpf=leppostfix), "Muon_ip3d[mu_mask]"))
    z.append(("FTAMuon{lpf}_pfRelIso03_all".format(lpf=leppostfix), "Muon_pfRelIso03_all[mu_mask]"))
    z.append(("FTAMuon{lpf}_pfRelIso03_chg".format(lpf=leppostfix), "Muon_pfRelIso03_chg[mu_mask]"))
    z.append(("FTAMuon{lpf}_pfRelIso04_all".format(lpf=leppostfix), "Muon_pfRelIso04_all[mu_mask]"))
    z.append(("FTAMuon{lpf}_jetIdx".format(lpf=leppostfix), "Muon_jetIdx[mu_mask]"))
    #z.append(("METofMETandMu2", ) #FIXME: switch to MET_xycorr_pt{}
    # z.append(("nFTAMuon{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Muon{pf}_pt.size())"))
    z.append(("nLooseFTAMuon{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Muon_looseId[mu_mask && Muon_looseId == true].size())"))
    z.append(("nMediumFTAMuon{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Muon_mediumId[mu_mask && Muon_mediumId == true].size())"))
    z.append(("nTightFTAMuon{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Muon_tightId[mu_mask && Muon_tightId == true].size())"))
    z.append(("FTAMuon{lpf}_InvariantMass".format(lpf=leppostfix), "nFTAMuon{lpf} == 2 ? InvariantMass(FTAMuon{lpf}_pt, FTAMuon{lpf}_eta, FTAMuon{lpf}_phi, FTAMuon{lpf}_mass) : -0.1".format(lpf=leppostfix)))    
    if isData == False:
        z.append(("FTAMuon{lpf}_SF_ID_nom".format(lpf=leppostfix), "Muon_SF_ID_nom[mu_mask]"))
        z.append(("FTAMuon{lpf}_SF_ID_stat".format(lpf=leppostfix), "Muon_SF_ID_stat[mu_mask]"))
        z.append(("FTAMuon{lpf}_SF_ID_syst".format(lpf=leppostfix), "Muon_SF_ID_syst[mu_mask]"))
        z.append(("FTAMuon{lpf}_SF_ISO_nom".format(lpf=leppostfix), "Muon_SF_ISO_nom[mu_mask]"))
        z.append(("FTAMuon{lpf}_SF_ISO_stat".format(lpf=leppostfix), "Muon_SF_ISO_stat[mu_mask]"))
        z.append(("FTAMuon{lpf}_SF_ISO_syst".format(lpf=leppostfix), "Muon_SF_ISO_syst[mu_mask]"))
    #ELECTRONS
    z.append(("Electron_idx", "FTA::generateIndices(Electron_pt);"))
    z.append(("nFTAElectron{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Electron_pt[e_mask].size())"))
    z.append(("FTAElectron{lpf}_idx".format(lpf=leppostfix), "Electron_idx[e_mask]"))
    z.append(("FTAElectron{lpf}_cutBased".format(lpf=leppostfix), "Electron_cutBased[e_mask]"))
    z.append(("FTAElectron{lpf}_pt".format(lpf=leppostfix), "Electron_pt[e_mask]"))
    z.append(("FTAElectron{lpf}_eta".format(lpf=leppostfix), "Electron_eta[e_mask]"))
    z.append(("FTAElectron{lpf}_phi".format(lpf=leppostfix), "Electron_phi[e_mask]"))
    z.append(("FTAElectron{lpf}_mass".format(lpf=leppostfix), "Electron_mass[e_mask]"))
    z.append(("FTAElectron{lpf}_charge".format(lpf=leppostfix), "Electron_charge[e_mask]"))
    z.append(("FTAElectron{lpf}_dz".format(lpf=leppostfix), "Electron_dz[e_mask]"))
    z.append(("FTAElectron{lpf}_dxy".format(lpf=leppostfix), "Electron_dxy[e_mask]"))
    z.append(("FTAElectron{lpf}_d0".format(lpf=leppostfix), "sqrt(Electron_dz*Electron_dz + Electron_dxy*Electron_dxy)[e_mask]"))
    z.append(("FTAElectron{lpf}_ip3d".format(lpf=leppostfix), "Electron_ip3d[e_mask]"))
    z.append(("FTAElectron{lpf}_pfRelIso03_all".format(lpf=leppostfix), "Electron_pfRelIso03_all[e_mask]"))
    z.append(("FTAElectron{lpf}_pfRelIso03_chg".format(lpf=leppostfix), "Electron_pfRelIso03_chg[e_mask]"))
    z.append(("FTAElectron{lpf}_jetIdx".format(lpf=leppostfix), "Electron_jetIdx[e_mask]"))
    ##FIXME: This code above is broken for some reason, doesn't like it... why?
    z.append(("nLooseFTAElectron{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Sum(FTAElectron{lpf}_cutBased >= 2))".format(lpf=leppostfix)))
    z.append(("nMediumFTAElectron{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Sum(FTAElectron{lpf}_cutBased >= 3))".format(lpf=leppostfix)))
    z.append(("nTightFTAElectron{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Sum(FTAElectron{lpf}_cutBased >= 4))".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_InvariantMass".format(lpf=leppostfix), "nFTAElectron{lpf} == 2 ? InvariantMass(FTAElectron{lpf}_pt, FTAElectron{lpf}_eta, FTAElectron{lpf}_phi, FTAElectron{lpf}_mass) : -0.1".format(lpf=leppostfix)))
    if isData == False:
        z.append(("FTAElectron{lpf}_SF_EFF_nom".format(lpf=leppostfix), "Electron_SF_EFF_nom[e_mask]"))
        z.append(("FTAElectron{lpf}_SF_EFF_unc".format(lpf=leppostfix), "Electron_SF_EFF_unc[e_mask]"))
        z.append(("FTAElectron{lpf}_SF_ID_nom".format(lpf=leppostfix), "Electron_SF_ID_nom[e_mask]"))
        z.append(("FTAElectron{lpf}_SF_ID_unc".format(lpf=leppostfix), "Electron_SF_ID_unc[e_mask]"))
    #LEPTONS
    z.append(("nLooseFTALepton{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(nLooseFTAMuon{lpf} + nLooseFTAElectron{lpf})".format(lpf=leppostfix)))
    z.append(("nMediumFTALepton{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(nMediumFTAMuon{lpf} + nMediumFTAElectron{lpf})".format(lpf=leppostfix)))
    z.append(("nTightFTALepton{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(nTightFTAMuon{lpf} + nTightFTAElectron{lpf})".format(lpf=leppostfix)))
    z.append(("nFTALepton{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(nFTAMuon{lpf} + nFTAElectron{lpf})".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_argsort".format(lpf=leppostfix), "Reverse(Argsort(Concatenate(Muon_pt[mu_mask], Electron_pt[e_mask])))"))
    z.append(("FTALepton{lpf}_pt".format(lpf=leppostfix), "Take(Concatenate(Muon_pt[mu_mask], Electron_pt[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_eta".format(lpf=leppostfix), "Take(Concatenate(Muon_eta[mu_mask], Electron_eta[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_phi".format(lpf=leppostfix), "Take(Concatenate(Muon_phi[mu_mask], Electron_phi[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_jetIdx".format(lpf=leppostfix), "Take(Concatenate(Muon_jetIdx[mu_mask], Electron_jetIdx[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_pdgId".format(lpf=leppostfix), "Take(Concatenate(Muon_pdgId[mu_mask], Electron_pdgId[e_mask]), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_dRll".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? ROOT::VecOps::DeltaR(FTALepton{lpf}_eta.at(0), FTALepton{lpf}_eta.at(1), FTALepton{lpf}_phi.at(0), FTALepton{lpf}_phi.at(1)) : -0.1".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_dPhill".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? ROOT::VecOps::DeltaPhi(FTALepton{lpf}_phi.at(0), FTALepton{lpf}_phi.at(1)) : -999".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_dEtall".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? abs(FTALepton{lpf}_eta.at(0) - FTALepton{lpf}_eta.at(1)) : -999".format(lpf=leppostfix)))
    z.append(("nFTALepton{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(FTALepton{lpf}_pt.size())".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_pt_LeadLep".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 0 ? FTALepton{lpf}_pt.at(0) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_pt_SubleadLep".format(lpf=leppostfix), "FTALepton{lpf}_pt.size() > 1 ? FTALepton{lpf}_pt.at(1) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_eta_LeadLep".format(lpf=leppostfix), "FTALepton{lpf}_eta.size() > 0 ? FTALepton{lpf}_eta.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_eta_SubleadLep".format(lpf=leppostfix), "FTALepton{lpf}_eta.size() > 1 ? FTALepton{lpf}_eta.at(1) : -9999".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_jetIdx_0".format(lpf=leppostfix), "FTALepton{lpf}_jetIdx.size() > 0 ? FTALepton{lpf}_jetIdx.at(0) : -1".format(lpf=leppostfix)))
    z.append(("FTALepton{lpf}_jetIdx_1".format(lpf=leppostfix), "FTALepton{lpf}_jetIdx.size() > 1 ? FTALepton{lpf}_jetIdx.at(1) : -1".format(lpf=leppostfix)))
    if isData == False:
        z.append(("FTALepton{lpf}_SF_nom".format(lpf=leppostfix), "Take(Concatenate(FTAMuon{lpf}_SF_ID_nom*FTAMuon{lpf}_SF_ISO_nom, FTAElectron{lpf}_SF_ID_nom*FTAElectron{lpf}_SF_EFF_nom), FTALepton{lpf}_argsort)".format(lpf=leppostfix)))

    z.append(("FTAMuon{lpf}_pt_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_pt.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 13 ? FTALepton{lpf}_pt.at(0) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTAMuon{lpf}_pt_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_pt.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 13 ? FTALepton{lpf}_pt.at(1) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTAMuon{lpf}_eta_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_eta.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 13 ? FTALepton{lpf}_eta.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTAMuon{lpf}_eta_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_eta.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 13 ? FTALepton{lpf}_eta.at(1) : -9999".format(lpf=leppostfix)))
    z.append(("FTAMuon{lpf}_phi_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_phi.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 13 ? FTALepton{lpf}_phi.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTAMuon{lpf}_phi_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_phi.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 13 ? FTALepton{lpf}_phi.at(1) : -9999".format(lpf=leppostfix)))

    z.append(("FTAElectron{lpf}_pt_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_pt.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 11 ? FTALepton{lpf}_pt.at(0) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_pt_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_pt.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 11 ? FTALepton{lpf}_pt.at(1) : -0.000000000001".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_eta_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_eta.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 11 ? FTALepton{lpf}_eta.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_eta_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_eta.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 11 ? FTALepton{lpf}_eta.at(1) : -9999".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_phi_LeadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_phi.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 11 ? FTALepton{lpf}_phi.at(0) : -9999".format(lpf=leppostfix)))
    z.append(("FTAElectron{lpf}_phi_SubleadLep".format(lpf=leppostfix), 
              "FTALepton{lpf}_phi.size() > 1 && abs(FTALepton{lpf}_pdgId.at(1)) == 11 ? FTALepton{lpf}_phi.at(1) : -9999".format(lpf=leppostfix)))


    for sysVar, sysDict in sysVariations.items():
        #skip systematic variations on data, only do the nominal
        if isData and sysVar != "$NOMINAL": 
            continue
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        if isWeightVariation == True: continue
        syspostfix = "___" + sysVar.replace("$NOMINAL", "nom")
        branchpostfix = "__nom" if isWeightVariation else "__" + sysVar.replace("$NOMINAL", "nom")
        #metPt = sysDict.get("met_pt_var")
        #metPhi = sysDict.get("met_phi_var")
        #These are the xy corrected MET values, to be used in the calculations
        metPtName = "FTAMET{bpf}_pt".format(bpf=branchpostfix)#"source" variable so use the branchpostfix of this systematic, whereas defines should use syspostfix like "MTof..."
        metPhiName = "FTAMET{bpf}_phi".format(bpf=branchpostfix)
        z.append(("MTofMETandMu{bpf}".format(bpf=branchpostfix), 
                         "FTA::transverseMassMET(FTAMuon{lpf}_pt, FTAMuon{lpf}_phi, FTAMuon{lpf}_mass, {mpt}, {mph})".format(lpf=leppostfix, mpt=metPtName, mph=metPhiName)))
        z.append(("MTofMETandEl{bpf}".format(bpf=branchpostfix),  
                         "FTA::transverseMassMET(FTAElectron{lpf}_pt, FTAElectron{lpf}_phi, FTAElectron{lpf}_mass, {mpt}, {mph})".format(lpf=leppostfix, mpt=metPtName, mph=metPhiName)))
        #There shouldn't be any variation on this quantity, but... easier looping
        z.append(("MTofElandMu{bpf}".format(bpf=branchpostfix), 
                         "FTA::transverseMass(FTAMuon{lpf}_pt, FTAMuon{lpf}_phi, FTAMuon{lpf}_mass, FTAElectron{lpf}_pt, FTAElectron{lpf}_phi, FTAElectron{lpf}_mass)".format(lpf=leppostfix)))

    
    listOfColumns = rdf.GetColumnNames()
    #Add them to the dataframe...
    for defName, defFunc in z:
        if defName in listOfColumns:
            if verbose:
                print("{} already defined, skipping".format(defName))
            continue
        else:
            if verbose:
                print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
            rdf = rdf.Define(defName, defFunc)
            listOfColumns.push_back(defName)
    return rdf

def defineJets(input_df, era="2017", doAK8Jets=False, jetPtMin=30.0, jetPUId=None, useDeltaR=True, isData=True,
               nJetsToHisto=10, bTagger="DeepCSV", verbose=False,
               sysVariations={"$NOMINAL": {"jet_mask": "jet_mask",
                                           "lep_postfix": "", 
                                           "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                           "jet_pt_var": "Jet_pt",
                                           "jet_mass_var": "Jet_mass",
                                           "met_pt_var": "METFixEE2017_pt",
                                           "met_phi_var": "METFixEE2017_phi",
                                           "btagSF": "Jet_btagSF_deepcsv_shape",
                                           "weightVariation": False},
                              "jesTotalUp": {"jet_mask": "jet_mask_jesTotalUp", 
                                              "lep_postfix": "",
                                              "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                              "jet_pt_var": "Jet_pt_jesTotalUp",
                                              "jet_mass_var": "Jet_mass_jesTotalUp",
                                              "met_pt_var": "METFixEE2017_pt_jesTotalUp",
                                              "met_phi_var": "METFixEE2017_phi_jesTotalUp",
                                              "btagSF": "Jet_btagSF_deepcsv_shape",
                                              "weightVariation": False},
                              "jesTotalDown": {"jet_mask": "jet_mask_jesTotalDown", 
                                                "lep_postfix": "",
                                                "wgt_prebTag": "wgt_SUMW_PU_LSF_L1PF",
                                                "jet_pt_var": "Jet_pt_jesTotalDown",
                                                "jet_mass_var": "Jet_mass_jesTotalDown",
                                                "met_pt_var": "METFixEE2017_pt_jesTotalDown",
                                                "met_phi_var": "METFixEE2017_phi_jesTotalDown",
                                                "btagSF": "Jet_btagSF_deepcsv_shape",
                                                "weightVariation": False},
                          },
              ):
    """Function to take in a dataframe and return one with new columns defined,
    plus event filtering based on the criteria defined inside the function"""
    bTagWorkingPointDict = {
        '2016':{
            'DeepCSV':{'L': 0.2217, 'M': 0.6321, 'T': 0.8953, 'Var': 'btagDeepB'},
            'DeepJet':{ 'L': 0.0614, 'M': 0.3093, 'T': 0.7221, 'Var': 'btagDeepFlavB'}
        },
        '2017':{
            'CSVv2':{'L': 0.5803, 'M': 0.8838, 'T': 0.9693, 'Var': 'btagCSVV2'},
            'DeepCSV':{'L': 0.1522, 'M': 0.4941, 'T': 0.8001, 'Var': 'btagDeepB'},
            'DeepJet':{'L': 0.0521, 'M': 0.3033, 'T': 0.7489, 'Var': 'btagDeepFlavB'}
        },
        '2018':{
            'DeepCSV':{'L': 0.1241, 'M': 0.4184, 'T': 0.7527, 'Var': 'btagDeepB'},
            'DeepJet':{'L': 0.0494, 'M': 0.2770, 'T': 0.7264, 'Var': 'btagDeepFlavB'}
        }
    }
    if bTagger.lower() == "deepcsv":
        useDeepCSV=True
    elif bTagger.lower() == "deepjet":
        useDeepCSV=False
    elif bTagger.lower() == "csvv2":
        raise RuntimeError("CSVv2 is not a supported bTagger option in defineJets() right now")
    else:
        raise RuntimeError("{} is not a supported bTagger option in defineJets()".format(bTagger))
    print("FIXMEFIXME: Setting Jet_pt min to 30GeV! Must fix!")
    leppostfix = ""
    #z will be a list of tuples to define, so that we can do cleaner error handling and checks
    z = []
    for sysVar, sysDict in sysVariations.items():
        #skip systematic variations on data, only do the nominal
        if isData and sysVar != "$NOMINAL": 
            continue
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        if isWeightVariation == True: continue
        jetMask = sysDict.get("jet_mask")
        jetPt = sysDict.get("jet_pt_var")
        jetMass = sysDict.get("jet_mass_var")
        postfix = "__" + sysVar.replace("$NOMINAL", "nom")
        
        #Fill lists
        if jetPUId:
            if jetPUId == 'L':
                jetPUId = " && ({jpt} >= 50 || Jet_puId >= 4)".format(jpt=jetPt) #pass Loose Id, >=6 pass Medium, ==7 pass Tight
            elif jetPUId == 'M':
                jetPUId = " && ({jpt} >= 50 || Jet_puId >= 6)".format(jpt=jetPt) #pass Loose Id, >=6 pass Medium, ==7 pass Tight
            elif jetPUId == 'T':
                jetPUId = " && ({jpt} >= 50 || Jet_puId == 7)".format(jpt=jetPt) #pass Loose Id, >=6 pass Medium, ==7 pass Tight
            else:
                raise ValueError("Invalid Jet PU Id selected")
        else:
            jetPUId = ""
        z.append(("Jet_idx", "FTA::generateIndices(Jet_pt)"))
        z.append(("pre{jm}".format(jm=jetMask), "({jpt} >= {jptMin} && abs(Jet_eta) <= 2.5 && Jet_jetId > 2{jpuid})".format(lpf=leppostfix, 
                                                                                                                            jpt=jetPt, 
                                                                                                                            jptMin=jetPtMin,
                                                                                                                            jpuid=jetPUId
                                                                                                                        )))
        if useDeltaR is False: #Use PFMatching
            z.append(("{jm}".format(jm=jetMask), "ROOT::VecOps::RVec<Int_t> jmask = ({jpt} >= {jptMin} && abs(Jet_eta) <= 2.5 && Jet_jetId > 2{jpuid}); "\
                      "for(int i=0; i < FTALepton{lpf}_jetIdx.size(); ++i){{jmask = jmask && (Jet_idx != FTALepton{lpf}_jetIdx.at(i));}}"\
                      "return jmask;".format(lpf=leppostfix, jpt=jetPt, jptMin=jetPtMin, jpuid=jetPUId)))
        else: #DeltaR matching
            z.append(("{jm}".format(jm=jetMask), "ROOT::VecOps::RVec<Int_t> jmask = ({jpt} >= {jptMin} && abs(Jet_eta) <= 2.5 && Jet_jetId > 2{jpuid}); "\
                      "for(int i=0; i < FTALepton{lpf}_jetIdx.size(); ++i){{"\
                      "ROOT::VecOps::RVec<Float_t> dr;"\
                      "for(int j=0; j < jmask.size(); ++j){{"\
                      "dr.push_back(ROOT::VecOps::DeltaR(Jet_eta.at(j), FTALepton{lpf}_eta.at(i), Jet_phi.at(j), FTALepton{lpf}_phi.at(i)));}}"\
                      "jmask = jmask && dr >= {drt};"\
                      "dr.clear();}}"\
                      "return jmask;".format(lpf=leppostfix, jpt=jetPt, jptMin=jetPtMin, jpuid=jetPUId, drt=useDeltaR)))
        #Store the Jet Pt, Jet Raw Pt, Lep Pt
        z.append(("FTACrossCleanedJet{pf}_pt".format(pf=postfix), "(FTALepton{lpf}_jetIdx.at(0) >= 0 && pre{jm}.at(FTALepton{lpf}_jetIdx.at(0)) == true) ? {jpt}.at(FTALepton{lpf}_jetIdx.at(0)) : 0.0".format(jm=jetMask, lpf=leppostfix, jpt=jetPt)))
        z.append(("FTACrossCleanedJet{pf}_rawpt".format(pf=postfix), "(FTALepton{lpf}_jetIdx.at(0) >= 0 && pre{jm}.at(FTALepton{lpf}_jetIdx.at(0)) == true) ? (1 - Jet_rawFactor.at(FTALepton{lpf}_jetIdx.at(0))) * {jpt}.at(FTALepton{lpf}_jetIdx.at(0)) : 0.0".format(jm=jetMask, lpf=leppostfix, jpt=jetPt)))
        z.append(("FTACrossCleanedJet{pf}_leppt".format(pf=postfix), "(FTALepton{lpf}_jetIdx.at(0) >= 0 && pre{jm}.at(FTALepton{lpf}_jetIdx.at(0)) == true) ? FTALepton{lpf}_pt.at(0) : 0.0".format(jm=jetMask, lpf=leppostfix, jpt=jetPt)))
        # z.append(("FTACrossCleanedJet{pf}_diffpt".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) >= 0 ? FTACrossCleanedJet{pf}_pt + FTACrossCleanedJet{pf}_leppt - FTACrossCleanedJet{pf}_rawpt : -9999".format(jm=jetMask, lpf=leppostfix, pf=postfix)))
        z.append(("FTACrossCleanedJet{pf}_diffpt".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) >= 0 ? FTACrossCleanedJet{pf}_leppt - FTACrossCleanedJet{pf}_pt : -9999".format(jm=jetMask, lpf=leppostfix, pf=postfix)))
        z.append(("FTACrossCleanedJet{pf}_diffptraw".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) >= 0 ? (-1.0 * Jet_rawFactor * {jpt}).at(FTALepton{lpf}_jetIdx.at(0)) : -9999".format(jm=jetMask, lpf=leppostfix, pf=postfix, jpt=jetPt)))
        z.append(("FTACrossCleanedJet{pf}_diffptrawinverted".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) < 0 ? ROOT::VecOps::RVec<Float_t>(-1.0 * Jet_rawFactor * {jpt}[pre{jm}]) : ROOT::VecOps::RVec<Float_t> {{-9999.0}}".format(jm=jetMask, lpf=leppostfix, pf=postfix, jpt=jetPt)))
        z.append(("nFTAJet{pf}".format(pf=postfix), "static_cast<Int_t>({jm}[{jm}].size())".format(jm=jetMask)))
        z.append(("FTAJet{pf}_ptsort".format(pf=postfix), "Reverse(Argsort({jpt}[{jm}]))".format(jpt=jetPt, jm=jetMask)))
        z.append(("FTAJet{pf}_deepcsvsort".format(pf=postfix), "Reverse(Argsort(Jet_{btv}[{jm}]))".format(btv=bTagWorkingPointDict[era]["DeepCSV"]["Var"], jm=jetMask)))
        z.append(("FTAJet{pf}_deepjetsort".format(pf=postfix), "Reverse(Argsort(Jet_{btv}[{jm}]))".format(btv=bTagWorkingPointDict[era]["DeepJet"]["Var"], jm=jetMask)))
        z.append(("FTAJet{pf}_idx".format(pf=postfix), "Jet_idx[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_pt".format(pf=postfix), "{jpt}[{jm}]".format(jpt=jetPt, jm=jetMask)))
        z.append(("FTAJet{pf}_eta".format(pf=postfix), "Jet_eta[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_phi".format(pf=postfix), "Jet_phi[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_mass".format(pf=postfix), "{jms}[{jm}]".format(jms=jetMass, jm=jetMask)))
        z.append(("FTAJet{pf}_jetId".format(pf=postfix), "Jet_jetId[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_puId".format(pf=postfix), "Jet_puId[{jm}]".format(jm=jetMask)))
        if isData == False:
            z.append(("FTAJet{pf}_genJetIdx".format(pf=postfix), "Jet_genJetIdx[{jm}]".format(jm=jetMask)))
            z.append(("nFTAJet{pf}_genMatched".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_genJetIdx[FTAJet{pf}_genJetIdx >= 0].size())".format(pf=postfix)))
            z.append(("nFTAJet{pf}_puIdLoose".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_genJetIdx[(FTAJet{pf}_puId >= 4 || FTAJet{pf}_pt >= 50)].size())".format(pf=postfix)))
            z.append(("nFTAJet{pf}_genMatched_puIdLoose".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_genJetIdx[FTAJet{pf}_genJetIdx >= 0 && (FTAJet{pf}_puId >= 4 || FTAJet{pf}_pt >= 50)].size())".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepCSVB".format(pf=postfix), "Jet_btagDeepB[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_DeepCSVB_sorted".format(pf=postfix), "Take(FTAJet{pf}_DeepCSVB, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepCSVB_sorted_LeadtagJet".format(pf=postfix), "FTAJet{pf}_DeepCSVB_sorted.size() > 0 ? FTAJet{pf}_DeepCSVB_sorted.at(0) : -9999".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepCSVB_sorted_SubleadtagJet".format(pf=postfix), "FTAJet{pf}_DeepCSVB_sorted.size() > 1 ? FTAJet{pf}_DeepCSVB_sorted.at(1) : -9999".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepJetB".format(pf=postfix), "Jet_btagDeepFlavB[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_DeepJetB_sorted".format(pf=postfix), "Take(FTAJet{pf}_DeepJetB, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepJetB_sorted_LeadtagJet".format(pf=postfix), "FTAJet{pf}_DeepJetB_sorted.size() > 0 ? FTAJet{pf}_DeepJetB_sorted.at(0) : -9999".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepJetB_sorted_SubleadtagJet".format(pf=postfix), "FTAJet{pf}_DeepJetB_sorted.size() > 1 ? FTAJet{pf}_DeepJetB_sorted.at(1) : -9999".format(pf=postfix)))
        for x in xrange(nJetsToHisto):
            z.append(("FTAJet{pf}_pt_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_pt.size() > {n} ? FTAJet{pf}_pt.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_eta_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_eta.size() > {n} ? FTAJet{pf}_phi.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_phi_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_phi.size() > {n} ? FTAJet{pf}_phi.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_DeepCSVB_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepCSVB.size() > {n} ? FTAJet{pf}_DeepCSVB.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_DeepJetB_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepJetB.size() > {n} ? FTAJet{pf}_DeepJetB.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_DeepCSVB_sortedjet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepCSVB_sorted.size() > {n} ? FTAJet{pf}_DeepCSVB_sorted.at({n}) : -9999".format(pf=postfix, n=x)))
            z.append(("FTAJet{pf}_DeepJetB_sortedjet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepJetB_sorted.size() > {n} ? FTAJet{pf}_DeepJetB_sorted.at({n}) : -9999".format(pf=postfix, n=x)))
        z.append(("FTAJet{pf}_LooseDeepCSVB".format(pf=postfix), "FTAJet{pf}_DeepCSVB[FTAJet{pf}_DeepCSVB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepCSV"]["L"])))
        z.append(("FTAJet{pf}_MediumDeepCSVB".format(pf=postfix), "FTAJet{pf}_DeepCSVB[FTAJet{pf}_DeepCSVB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepCSV"]["M"])))
        z.append(("FTAJet{pf}_TightDeepCSVB".format(pf=postfix), "FTAJet{pf}_DeepCSVB[FTAJet{pf}_DeepCSVB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepCSV"]["T"])))
        z.append(("nLooseDeepCSVB{pf}".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_LooseDeepCSVB.size())".format(pf=postfix)))
        z.append(("nMediumDeepCSVB{pf}".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_MediumDeepCSVB.size())".format(pf=postfix)))
        z.append(("nTightDeepCSVB{pf}".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_TightDeepCSVB.size())".format(pf=postfix)))
        z.append(("FTAJet{pf}_LooseDeepJetB".format(pf=postfix), "FTAJet{pf}_DeepJetB[FTAJet{pf}_DeepJetB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepJet"]["L"])))
        z.append(("FTAJet{pf}_MediumDeepJetB".format(pf=postfix), "FTAJet{pf}_DeepJetB[FTAJet{pf}_DeepJetB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepJet"]["M"])))
        z.append(("FTAJet{pf}_TightDeepJetB".format(pf=postfix), "FTAJet{pf}_DeepJetB[FTAJet{pf}_DeepJetB > {wpv}]".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepJet"]["T"])))
        z.append(("nLooseDeepJetB{pf}".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_LooseDeepJetB.size())".format(pf=postfix)))
        z.append(("nMediumDeepJetB{pf}".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_MediumDeepJetB.size())".format(pf=postfix)))
        z.append(("nTightDeepJetB{pf}".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_TightDeepJetB.size())".format(pf=postfix)))
        #These might be more efficiently calculated with my own custom code, instead of this... well, lets try for the sake of experimentation
        #HT is just the sum of good jet pts
        # HT2M is the sum of jet pt's for all but the two highest-b-tagged jets (2016 analysis requires 4+ jets to define this quantity), so here Take() is used twice.
        # The first call acquires the good jet pt's sorted by b-tagging, the senond Take() gets the last n-2 elements, thereby excluding the two highest b-tagged jet's pt
        # HTRat = HT(two highest b-tagged) / HT, so it's useful to define this similarly to HT2M (and crosscheck that HTNum + HT2M = HT!)
        # H and H2M are defined similarly for the overall momentum magnitude...
        # P = pt/sin(theta) = pt * (1/sin(theta)) = pt * cosh(eta)
        if useDeepCSV:
            z.append(("FTAJet{pf}_pt_bsrt".format(pf=postfix), "Take(FTAJet{pf}_pt, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_eta_bsrt".format(pf=postfix), "Take(FTAJet{pf}_eta, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_phi_bsrt".format(pf=postfix), "Take(FTAJet{pf}_phi, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_mass_bsrt".format(pf=postfix), "Take(FTAJet{pf}_mass, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
        else:
            z.append(("FTAJet{pf}_pt_bsrt".format(pf=postfix), "Take(FTAJet{pf}_pt, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_eta_bsrt".format(pf=postfix), "Take(FTAJet{pf}_eta, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_phi_bsrt".format(pf=postfix), "Take(FTAJet{pf}_phi, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
            z.append(("FTAJet{pf}_mass_bsrt".format(pf=postfix), "Take(FTAJet{pf}_mass, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
        z.append(("FTAJet{pf}_P_bsrt".format(pf=postfix), "FTAJet{pf}_pt_bsrt * ROOT::VecOps::cosh(FTAJet{pf}_eta_bsrt)".format(pf=postfix)))
        z.append(("ST{pf}".format(pf=postfix), "Sum(FTAJet{pf}_pt) + Sum(FTALepton{lpf}_pt)".format(pf=postfix, lpf=leppostfix)))
        z.append(("HT{pf}".format(pf=postfix), "Sum(FTAJet{pf}_pt)".format(pf=postfix)))
        z.append(("HT2M{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? Sum(Take(FTAJet{pf}_pt_bsrt, (2 - FTAJet{pf}_pt_bsrt.size()))) : -0.1".format(pf=postfix)))
        z.append(("HTNum{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? Sum(Take(FTAJet{pf}_pt_bsrt, 2)) : -0.1".format(pf=postfix)))
        z.append(("HTRat{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? (HT2M{pf} / HT{pf}) : -0.1".format(pf=postfix)))
        z.append(("dRbb{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? ROOT::VecOps::DeltaR(FTAJet{pf}_eta_bsrt.at(0), FTAJet{pf}_eta_bsrt.at(1), FTAJet{pf}_phi_bsrt.at(0), FTAJet{pf}_phi_bsrt.at(1)) : -0.1".format(pf=postfix)))
        z.append(("dPhibb{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? ROOT::VecOps::DeltaPhi(FTAJet{pf}_phi_bsrt.at(0), FTAJet{pf}_phi_bsrt.at(1)) : -999".format(pf=postfix)))
        z.append(("dEtabb{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? abs(FTAJet{pf}_eta_bsrt.at(0) - FTAJet{pf}_eta_bsrt.at(1)) : -999".format(pf=postfix)))
        z.append(("H{pf}".format(pf=postfix), "Sum(FTAJet{pf}_P_bsrt)".format(pf=postfix)))
        z.append(("H2M{pf}".format(pf=postfix), "FTAJet{pf}_pt_bsrt.size() > 2 ? Sum(Take(FTAJet{pf}_P_bsrt, (2 - FTAJet{pf}_pt_bsrt.size()))) : -0.1".format(pf=postfix)))
        z.append(("HTH{pf}".format(pf=postfix), "HT{pf}/H{pf}".format(pf=postfix)))
        if useDeepCSV:
            z.append(("HTb{pf}".format(pf=postfix), "Sum(FTAJet{pf}_pt[FTAJet{pf}_DeepCSVB > {wpv}])".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepCSV"]["M"])))
        else:
            z.append(("HTb{pf}".format(pf=postfix), "Sum(FTAJet{pf}_pt[FTAJet{pf}_DeepJetB > {wpv}])".format(pf=postfix, wpv=bTagWorkingPointDict[era]["DeepJet"]["M"])))
        
    rdf = input_df
    listOfColumns = rdf.GetColumnNames()
    for defName, defFunc in z:
        if defName in listOfColumns:
            if verbose:
                print("{} already defined, skipping".format(defName))
            continue
        else:
            if verbose:
                print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
            rdf = rdf.Define(defName, defFunc)
            listOfColumns.push_back(defName)
                
    return rdf

def METXYCorr(input_df, run_branch = "run", era = "2017", isData = True, npv_branch = "PV_npvs",
               sysVariations=None, verbose=False):
    rdf = input_df
    listOfColumns = input_df.GetColumnNames()
    z = []
    for sysVar, sysDict in sysVariations.items():
        #skip systematic variations on data, only do the nominal
        if isData and sysVar != "$NOMINAL": 
            continue
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        branchpostfix = "ERROR_NO_BRANCH_POSTFIX_METXYCorr"
        if isWeightVariation == True: 
            continue
        else:
            branchpostfix = "__" + sysVar.replace("$NOMINAL", "nom")
        metPt = sysDict.get("met_pt_var")
        metPhi = sysDict.get("met_phi_var")
        metDoublet = "MET_xycorr_doublet{bpf}".format(bpf=branchpostfix)
        metPtName = "FTAMET{bpf}_pt".format(bpf=branchpostfix)
        metPhiName = "FTAMET{bpf}_phi".format(bpf=branchpostfix)
        #XY correctors takes the: uncorrected pt and phi, run branch, year, C++ true/false for isData, and PV branch
        def_fnc = "FTA::METXYCorr({mpt}, {mph}, {run}, {era}, {isData}, {pv})".format(mpt=metPt,
                                                                        mph=metPhi,
                                                                        run=run_branch,
                                                                        era=era,
                                                                        isData=str(isData).lower(),
                                                                        pv=npv_branch
                                                                        )
        #append the definitions to the list in the order required
        z.append((metDoublet, def_fnc))
        z.append((metPtName, "{}.first".format(metDoublet)))
        z.append((metPhiName, "{}.second".format(metDoublet)))

    for defName, defFunc in z:
        if defName in listOfColumns:
            if verbose:
                print("{} already defined, skipping".format(defName))
            continue
        else:
            if verbose:
                print("rdf = rdf.Define(\"{}\", \"{}\")".format(defName, defFunc))
            rdf = rdf.Define(defName, defFunc)
            listOfColumns.push_back(defName)
    return rdf

def bookSnapshot(input_df, filename, columnList, lazy=True, treename="Events", mode="RECREATE", compressionAlgo="LZ4", compressionLevel=6, splitLevel=99, debug=False):
    if columnList is None:
        raise RuntimeError("Cannot take empty columnList in bookSnapshot")
    elif isinstance(columnList, str) or 'vector<string>' in str(type(columnList)):
        columns = columnList #regexp case or vector of strings
    elif isinstance(columnList, list):
        columns = ROOT.std.vector(str)(len(columnList))
        for col in columnList:
            columns.push_back(col)
    else:
        raise RuntimeError("Cannot handle columnList of type {} in bookSnapshot".format(type(columnList)))
        
    Algos = {"ZLIB": 1,
             "LZMA": 2,
             "LZ4": 4,
             "ZSTD": 5
         }
    sopt = ROOT.RDF.RSnapshotOptions(mode, Algos[compressionAlgo], compressionLevel, 0, splitLevel, True) #lazy is last option
    if lazy is False:
        sopt.fLazy = False
    handle = input_df.Snapshot(treename, filename, columns, sopt)

    return handle
    # print(type(handle))
    
    # handle.GetValue()
    # print("mode: {}\nalgo: {}\nlevel: {}\nsplit: {}\nlazy: {}".format(sopt.fMode, sopt.fCompressionAlgorithm, sopt.fCompressionLevel, splitLevel, sopt.fLazy))

def delegateFlattening(inputDF, varsToFlatten, channel=None, debug=False):
    """Function that contains info about which variables to flatten and delegates this to functions, returning the RDataFrame after flattened variables have been defined."""

    finalVars = ROOT.std.vector(str)(0) #Final variables that have been flattened and need to be returned to caller
    allColumns = inputDF.GetColumnNames()
    definedColumns = inputDF.GetDefinedColumnNames()
    rdf = inputDF
    skippedVars = [] #Skipped due to not being in the list
    flattenedVars = [] #Need to be flattened (parent variable, not post-flattening children)
    flatVars = [] #Already flat

    for var in allColumns:
        if var not in varsToFlatten:
            skippedVars.append(var)
            continue
        if "ROOT::VecOps::RVec" in rdf.GetColumnType(var):
            if debug:
                print("Flatten {}".format(var))
            if "FTAMuon" in var:
                if "mumu" in channel.lower():
                    depth = 2
                elif "elmu" in channel.lower():
                    depth = 1
                elif "elel" in channel.lower():
                    depth = 0
                else:
                    depth = 2
            if "FTALepton" in var:
                depth = 2
            if "FTAElectron" in var:
                if "mumu" in channel.lower():
                    depth = 0
                elif "elmu" in channel.lower():
                    depth = 1
                elif "elel" in channel.lower():
                    depth = 2
                else:
                    depth = 2
            elif "FTAJet" in var:
                depth = 10
            else:
                depth = 2
            flattenedVars.append(var)
            rdf, iterFlattenedVars = flattenVariable(rdf, var, depth, static_cast=True, fallback=None, debug=debug)
            for fvar in iterFlattenedVars:
                finalVars.push_back(fvar)
        else:
            # if debug:
            #     print("Retain {}".format(var))
            flatVars.append(var)
            finalVars.push_back(var)
        
    for c in finalVars:
        if debug:
            print("{:45s} | {}".format(c, rdf.GetColumnType(c)))
    
    return rdf, {"finalVars": finalVars, "flattenedVars": flattenedVars, "flatVars": flatVars, "skippedVars": skippedVars}


def flattenVariable(input_df, var, depth, static_cast=None, fallback=None, debug=False):
    """Take an RVec or std::vector of variables and define new columns for the first n (depth) elements, falling back to a default value if less than n elements are in an event."""

    rdf = input_df
    t = rdf.GetColumnType(var) #Get the type for deduction of casting rule and fallback value
    flats = [] #Store the defined variables so they may be added to a list for writing
    if static_cast is True: #deduce the static_cast and store the beginning and end of the wrapper in 'sci' and 'sce'
        sce = ")"
        if "<double>" in t.lower() or "<double_t>" in t.lower():
            sci = "static_cast<Double_t>("
            # sci = "static_cast<Float_t>("
        if "<float>" in t.lower() or "<float_t>" in t.lower():
            # sci = "static_cast<Double_t>("
            sci = "static_cast<Float_t>("
        elif "<uint>" in t.lower() or "<uint_t>" in t.lower() or "<unsigned char>" in t.lower() or "<uchar_t>" in t.lower():
            # sci = "static_cast<Uint_t>("
            sci = "static_cast<unsigned int>("
        elif "<int>" in t.lower() or "<int_t>" in t.lower():
            sci = "static_cast<Int_t>("
        elif "<bool" in t.lower():
            sci = "static_cast<Bool_t>("
        elif "<unsigned long>" in t.lower():
            sci = "static_cast<unsigned long>(" 
        else:
            raise NotImplementedError("No known casting rule for variable {} of type {}".format(var, t))
    elif isinstance(static_cast, str):
        sce = ")"
        sci = static_cast
    else:
        sce = ""
        sci = ""

    if isinstance(fallback, (float, int)):
        fb = fallback
    else:
        if "<double>" or "<float>" in t:
            fb = -9876.54321
        elif "<uint>" in t:
            fb = 0
        elif "<int>" in t:
            fb = -9876
        else:
            raise NotImplementedError("No known fallback rule")        

    for x in xrange(depth):
        split_name = var.split("_")
        to_replace = split_name[0]
        name = var.replace(to_replace, "{tr}{n}".format(tr=to_replace, n=x+1))
        # name = "{var}{n}".format(var=var, n=x+1)
        flats.append(name)
        defn = "{var}.size() > {x} ? {sci}{var}.at({x}){sce} : {fb}".format(sci=sci, var=var, x=x, sce=sce, fb=fb)
        if debug:
            print("{} : {}".format(name, defn))
        rdf = rdf.Define(name, defn)

    return rdf, flats
            
            
        
ROOT.gROOT.ProcessLine(".L /eos/user/n/nmangane/CMSSW/CMSSW_10_2_18/src/FourTopNAOD/RDF/FTFunctions.cpp")
ROOT.gInterpreter.Declare("""
    const UInt_t barWidth = 60;
    ULong64_t processed = 0, totalEvents = 0;
    std::string progressBar;
    std::mutex barMutex; 
    auto registerEvents = [](ULong64_t nIncrement) {totalEvents += nIncrement;};

    ROOT::RDF::RResultPtr<ULong64_t> AddProgressBar(ROOT::RDF::RNode df, int everyN=10000, int totalN=100000) {
        registerEvents(totalN);
        auto c = df.Count();
        c.OnPartialResultSlot(everyN, [everyN] (unsigned int slot, ULong64_t &cnt){
            std::lock_guard<std::mutex> l(barMutex);
            processed += everyN; //everyN captured by value for this lambda
            progressBar = "[";
            for(UInt_t i = 0; i < static_cast<UInt_t>(static_cast<Float_t>(processed)/totalEvents*barWidth); ++i){
                progressBar.push_back('|');
            }
            // escape the '\' when defined in python string
            std::cout << "\\r" << std::left << std::setw(barWidth) << progressBar << "] " << processed << "/" << totalEvents << std::flush;
        });
        return c;
    }
""")

bookerV2 = {
    "tt_DL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8510388,
        "nEventsPositive": 8467543,
        "nEventsNegative": 42845,
        "sumWeights": 612101836.284397,
        "sumWeights2": 44925503249.097206,
        "isSignal": False,
        "doFilter": True,
        "crossSection": 0.0486771857914 + 1.40805743121,
        "crossSectionGenHT500-550nJet7Matching": 1.4529,
        "source": {"NANOv5": "dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
                   "NANOv5p1": "dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/palencia-TopNanoAODv5p1_2017-caa716c30b9109c88acae23be6386548/USER",
                   "LJMLogic": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-*_2017_v2.root",
                   "LJMLogic__ElMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_DL-GF-*_2017_v2*.root",
                   "LJMLogic__MuMu_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/MuMu_selection/tt_DL-GF-*_2017_v2*.root",
                   "LJMLogic__ElEl_selection": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElEl_selection/tt_DL-GF-*_2017_v2*.root",
                  },
        "sourceSPARK": ["root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-1_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-2_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-3_2017_v2.root",
                       "root://eosuser.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-4_2017_v2.root",],
        "destination": "/$HIST_CLASS/$HIST/tt_DL-GF/$SYSTEMATIC",
        "stitch": {"mode": "Flag",
                   "source": "Filtered",
                   "channel": "DL"
                  },
        "Notes": "1.4815 was the old XS * BR * stitching factor, now scaled down so that the XS matches Brown's lower BR calculation",
        "splitProcess": {"ID":{"unpackGenTtbarId": True,
                               "nFTAGenJet/FTAGenHT": True,
                               "subera": False,
                              },
                         "processes": {"ttbb_DL-GF_fr": {"filter": "nAdditionalBJets >= 2 && nFTAGenLep == 2 && nFTAGenJet >= 7 && FTAGenHT >= 500",
                                                         "sumWeights": 20410377.7205,
                                                         "sumWeights2": 1495802529.19,
                                                         "nominalXS": 0.0485744525276,
                                                         "nominalXS2": 8.47204020682e-09,
                                                         "effectiveXS": 0.0535612126499,
                                                         "effectiveXS2": 1.03008480636e-08,
                                                         "nEventsPositive": 282130,
                                                         "nEventsNegative": 1215,
                                                         "nLep2nJet7GenHT500-550-nominalXS": 0.00446767251882,
                                                         "nLep2nJet7pGenHT500p-nominalXS": 0.0485744525276,
                                                         "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                         "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                         "nLep2nJet7GenHT500-550-effectiveXS": 0.00492633360499,
                                                         "nLep2nJet7pGenHT500p-effectiveXS": 0.0535612126499,
                                                         "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                         "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                         "fractionalContribution": 1 - 0.11972537248,
                                                         "effectiveCrossSection": 0.0486771857914 * 0.040/0.032,
                                                         "snapshotPriority": 4,
                                                     },
                                       "ttother_DL-GF_fr": {"filter": "nAdditionalBJets < 2 && nFTAGenLep == 2 && nFTAGenJet >= 7 && FTAGenHT >= 500",
                                                            "sumWeights": 591691409.848,
                                                            "sumWeights2": 43429698960.3,
                                                            "nominalXS": 1.40816043153,
                                                            "nominalXS2": 2.45980434304e-07,
                                                            "effectiveXS": 1.2290807799,
                                                            "effectiveXS2": 1.87394631545e-07,
                                                            "nEventsPositive": 8185412,
                                                            "nEventsNegative": 41630,
                                                            "nLep2nJet7GenHT500-550-nominalXS": 0.17731136686,
                                                            "nLep2nJet7pGenHT500p-nominalXS": 1.40816043153,
                                                            "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                            "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                            "nLep2nJet7GenHT500-550-effectiveXS": 0.154762190574,
                                                            "nLep2nJet7pGenHT500p-effectiveXS": 1.2290807799,
                                                            "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                            "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                            "fractionalContribution": 1 - 0.11949870629,
                                                            "effectiveCrossSection": 1.40805743121 - 0.0486771857914 * (0.040 - 0.032)/0.032,
                                                            "snapshotPriority": 2,
                                                        },
                                   },
                         "inclusiveProcess": {"tt_DL-GF_inclusive": {"sumWeights": 612101860.267,
                                                                     "sumWeights2": 44925506774.5,
                                                                     "nominalXS": 1.45673505707,
                                                                     "nominalXS2": 2.54452504445e-07,
                                                                     "effectiveXS": 1.45673505707,
                                                                     "effectiveXS2": 2.54452504445e-07,
                                                                     "nEventsPositive": 8467543,
                                                                     "nEventsNegative": 42845,
                                                                     "nLep2nJet7GenHT500-550-nominalXS": 0.181779039379,
                                                                     "nLep2nJet7pGenHT500p-nominalXS": 1.45673488406,
                                                                     "nLep1nJet9GenHT500-550-nominalXS": 0.0,
                                                                     "nLep1nJet9pGenHT500p-nominalXS": 0.0,
                                                                     "nLep2nJet7GenHT500-550-effectiveXS": 0.181779039379,
                                                                     "nLep2nJet7pGenHT500p-effectiveXS": 1.45673488406,
                                                                     "nLep1nJet9GenHT500-550-effectiveXS": 0.0,
                                                                     "nLep1nJet9pGenHT500p-effectiveXS": 0.0,
                                                                     },
                                          },
                     },
    },
}
r = ROOT.ROOT.RDataFrame("Events", "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tttt*.root")
def splitProcess(input_df, splitProcess=None, sampleName=None, isData=True, era="2017", printInfo=False, inclusiveProcess=None, fillDiagnosticHistos=False):
    lumiDict = {"2017": 41.53,
                "2018": 59.97}
    filterNodes = dict() #For storing tuples to debug and be verbose about
    defineNodes = collections.OrderedDict() #For storing all histogram tuples --> Easier debugging when printed out, can do branch checks prior to invoking HistoND, etc...
    countNodes = dict() #For storing the counts at each node
    snapshotPriority = dict()
    diagnosticNodes = dict()
    diagnosticHistos = dict()
    nodes = dict()#For storing nested dataframe nodes, THIS has filters, defines applied to it, not 'filterNodes' despite the name
    #Define the base node in nodes when we split/don't split the process

    # if splitProcess != None:
    if True: #Deprecate the alternate code path to reduce duplication, use the inclusiveProcess instead
        if isinstance(splitProcess, (dict, collections.OrderedDict)) or isinstance(inclusiveProcess, (dict, collections.OrderedDict)):
            df_with_IDs = input_df
            if isinstance(splitProcess, (dict, collections.OrderedDict)):
                splitProcs = splitProcess.get("processes")
                IDs = splitProcess.get("ID")  
            else:
                splitProcs = collections.OrderedDict()
                IDs = {}
            if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                inclusiveProc = inclusiveProcess.get("processes")
                inclusiveDict = inclusiveProc.values()[0]
                if inclusiveProc.keys()[0] not in splitProcs:
                    splitProcs.update(inclusiveProc)
                else:
                    print("Inclusive process already defined, not overriding in splitProces")
            listOfColumns = df_with_IDs.GetColumnNames()
            for IDname, IDbool in IDs.items():
                if IDbool and IDname == "unpackGenTtbarId":
                    if "unpackedGenTtbarId" not in listOfColumns:
                        df_with_IDs = df_with_IDs.Define("unpackedGenTtbarId", "FTA::unpackGenTtbarId(genTtbarId)")
                        df_with_IDs = df_with_IDs.Define("nAdditionalBJets", "unpackedGenTtbarId[0]")
                        # df_with_IDs = df_with_IDs.Define("n2BHadronJets", "unpackedGenTtbarId[1]")
                        # df_with_IDs = df_with_IDs.Define("n1BHadronJets", "unpackedGenTtbarId[2]")
                        df_with_IDs = df_with_IDs.Define("nAdditionalCJets", "unpackedGenTtbarId[3]")
                        # df_with_IDs = df_with_IDs.Define("n2CHadronJets", "unpackedGenTtbarId[4]")
                        # df_with_IDs = df_with_IDs.Define("n1CHadronJets", "unpackedGenTtbarId[5]")
                        # df_with_IDs = df_with_IDs.Define("nBJetsFromTop", "unpackedGenTtbarId[6]")
                        # df_with_IDs = df_with_IDs.Define("nBJetsFromW", "unpackedGenTtbarId[7]")
                        # df_with_IDs = df_with_IDs.Define("nCJetsFromW", "unpackedGenTtbarId[8]")
                if IDbool and IDname == "nFTAGenJet/FTAGenHT":
                    #Production notes (SL filter -> nGenJet 9)
                    # Combination of filters is applied:
                    # exactly 1 lepton (electron,muon or tau) in LHE record
                    # HT calculated from jets with pT>30 and |eta|<2.4 > 500 GeV
                    # Jet multiplicity (jet pT>30) >= 9
                    if "nFTAGenLep" not in listOfColumns:
                        df_with_IDs = df_with_IDs.Define("nFTAGenLep", "static_cast<Int_t>(LHEPart_pdgId[abs(LHEPart_pdgId)==11 || abs(LHEPart_pdgId)==13 || abs(LHEPart_pdgId)==15].size())")
                        listOfColumns.push_back("nFTAGenLep")
                    if "nFTAGenJet" not in listOfColumns:
                        df_with_IDs = df_with_IDs.Define("nFTAGenJet", "static_cast<Int_t>(GenJet_pt[GenJet_pt > 30].size())")
                        listOfColumns.push_back("nFTAGenJet")
                    if "FTAGenHT" not in listOfColumns:
                        df_with_IDs = df_with_IDs.Define("FTAGenHT", "Sum(GenJet_pt[GenJet_pt > 30 && abs(GenJet_eta) < 2.4])")
                        listOfColumns.push_back("FTAGenHT")
                if IDbool and IDname == "subera":
                    raise NotImplementedError("splitProcess 'subera' not yet implemented")
            nodes["BaseNode"] = df_with_IDs #Always store the base node we'll build upon in the next level
            for preProcessName, processDict in splitProcs.items():
                processName = era + "___" + preProcessName
                filterString = processDict.get("filter")
                snapshotPriority[processName] = processDict.get("snapshotPriority", 0)
                filterName = "{} :: {}".format(processName, filterString.replace(" && ", " and ").replace(" || ", " or ")\
                                               .replace("&&", " and ").replace("||", " or "))
                if not isData:
                    #Make the fractional contribution equal to N_eff(sample_j) / Sum(N_eff(sample_i)), where N_eff = nEventsPositive - nEventsNegative
                    #Need to gather those bookkeeping stats from the original source rather than the ones after event selection
                    effectiveXS = processDict.get("effectiveCrossSection")
                    sumWeights = processDict.get("sumWeights")
                    # nEffective = processDict.get("nEventsPositive") - processDict.get("nEventsNegative")
                    fractionalContribution = processDict.get("fractionalContribution")
                    #Calculate XS * Lumi
                    wgtFormula = "{eXS:f} * {lumi:f} * 1000 * genWeight * {frCon:f} / {sW:f}".format(eXS=effectiveXS,
                                                                                                     lumi=lumiDict[era],
                                                                                                     frCon=fractionalContribution,
                                                                                                     sW=sumWeights
                                                                                                 )
                    if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                        formulaForNominalXS = "{nXS:f} * genWeight / {sW:f}".format(nXS=inclusiveDict.get("effectiveCrossSection"),
                                                                                    sW=inclusiveDict.get("sumWeights")
                        )
                        print("{} - nominalXS - {}".format(processName, formulaForNominalXS))
                        formulaForEffectiveXS = "{nXS:f} * genWeight * {frCon:f} / {sW:f}".format(nXS=effectiveXS,
                                                                                      frCon=fractionalContribution,
                                                                                      sW=sumWeights
                        )
                        print("{} - effectiveXS - {}".format(processName, formulaForEffectiveXS))
                    if fillDiagnosticHistos == True:
                        diagnostic_e_mask = "Electron_pt > 15 && Electron_cutBased >= 2 && ((abs(Electron_eta) < 1.4442 && abs(Electron_ip3d) < 0.05 && abs(Electron_dz) < 0.1) || (abs(Electron_eta) > 1.5660 && abs(Electron_eta) < 2.5 && abs(Electron_ip3d) < 0.10 && abs(Electron_dz) < 0.2))"
                        diagnostic_mu_mask = "Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_looseId == true && Muon_pfIsoId >= 4 && abs(Muon_ip3d) < 0.10 && abs(Muon_dz) < 0.02"
                        diagnostic_lepjet_idx = "Concatenate(Muon_jetIdx[diagnostic_mu_mask], Electron_jetIdx[diagnostic_e_mask])"
                        diagnostic_jet_idx = "FTA::generateIndices(Jet_pt)"
                        diagnostic_jet_mask = "ROOT::VecOps::RVec<int> jmask = (Jet_pt > 30 && abs(Jet_eta) < 2.5 && Jet_jetId > 2); "\
                                              "for(int i=0; i < diagnostic_lepjet_idx.size(); ++i){jmask = jmask && diagnostic_jet_idx != diagnostic_lepjet_idx.at(i);}"\
                                              "return jmask;"
                if processName not in nodes:
                    #L-2 filter, should be the packedEventID filter in that case
                    filterNodes[processName] = dict()
                    filterNodes[processName]["BaseNode"] = (filterString, filterName, processName, None, None, None, None)
                    nodes[processName] = dict()
                    if not isData:
                        nodes[processName]["BaseNode"] = nodes["BaseNode"]\
                            .Filter(filterNodes[processName]["BaseNode"][0], filterNodes[processName]["BaseNode"][1])\
                            .Define("pwgt___LumiXS", wgtFormula)
                        if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                            nodes[processName]["BaseNode"] = nodes[processName]["BaseNode"]\
                                .Define("nominalXS", formulaForNominalXS)\
                                .Define("nominalXS2", "pow(nominalXS, 2)")\
                                .Define("effectiveXS", formulaForEffectiveXS)\
                                .Define("effectiveXS2", "pow(effectiveXS, 2)")
                        if fillDiagnosticHistos == True:
                            nodes[processName]["BaseNode"] = nodes[processName]["BaseNode"]\
                                .Define("diagnostic_e_mask", diagnostic_e_mask)\
                                .Define("diagnostic_mu_mask", diagnostic_mu_mask)\
                                .Define("diagnostic_lepjet_idx", diagnostic_lepjet_idx)\
                                .Define("diagnostic_jet_idx", diagnostic_jet_idx)\
                                .Define("diagnostic_jet_mask", diagnostic_jet_mask)\
                                .Define("diagnostic_HT", "Sum(Jet_pt[diagnostic_jet_mask])")\
                                .Define("diagnostic_nJet", "Jet_pt[diagnostic_jet_mask].size()")\
                                .Define("diagnostic_jet1_pt", "Sum(diagnostic_jet_mask) > 0 ? Jet_pt[diagnostic_jet_mask].at(0) : -0.01")\
                                .Define("diagnostic_jet1_eta", "Sum(diagnostic_jet_mask) > 0 ? Jet_eta[diagnostic_jet_mask].at(0) : 9999.9")\
                                .Define("diagnostic_jet5_pt", "Sum(diagnostic_jet_mask) > 4 ? Jet_pt[diagnostic_jet_mask].at(4) : -0.01")\
                                .Define("diagnostic_jet5_eta", "Sum(diagnostic_jet_mask) > 4 ? Jet_eta[diagnostic_jet_mask].at(4) : 9999.9")\
                                .Define("diagnostic_el_pt", "Electron_pt[diagnostic_e_mask]")\
                                .Define("diagnostic_el_eta", "Electron_eta[diagnostic_e_mask]")\
                                .Define("diagnostic_mu_pt", "Muon_pt[diagnostic_mu_mask]")\
                                .Define("diagnostic_mu_eta", "Muon_eta[diagnostic_mu_mask]")
                            


                    else:
                        nodes[processName]["BaseNode"] = nodes["BaseNode"]\
                            .Filter(filterNodes[processName]["BaseNode"][0], filterNodes[processName]["BaseNode"][1])
                    countNodes[processName] = dict()
                    countNodes[processName]["BaseNode"] = nodes[processName]["BaseNode"].Count()
                    diagnosticNodes[processName] = collections.OrderedDict()
                    diagnosticHistos[processName] = collections.OrderedDict()
                    defineNodes[processName] = collections.OrderedDict()
                if not isData:
                    #Need to gather those bookkeeping stats from the original source rather than the ones after event selection...
                    diagnosticNodes[processName]["sumWeights::Sum"] = nodes[processName]["BaseNode"].Sum("genWeight")
                    diagnosticNodes[processName]["sumWeights2::Sum"] = nodes[processName]["BaseNode"].Define("genWeight2", "pow(genWeight, 2)").Sum("genWeight2")
                    if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                        diagnosticNodes[processName]["nominalXS::Sum"] = nodes[processName]["BaseNode"].Sum("nominalXS")
                        diagnosticNodes[processName]["nominalXS2::Sum"] = nodes[processName]["BaseNode"].Sum("nominalXS2")
                    # pdb.set_trace()
                    diagnosticNodes[processName]["effectiveXS::Sum"] = nodes[processName]["BaseNode"].Sum("effectiveXS")
                    diagnosticNodes[processName]["effectiveXS2::Sum"] = nodes[processName]["BaseNode"].Sum("effectiveXS2")
                    diagnosticNodes[processName]["nEventsPositive::Count"] = nodes[processName]["BaseNode"].Filter("genWeight >= 0", "genWeight >= 0").Count()
                    diagnosticNodes[processName]["nEventsNegative::Count"] = nodes[processName]["BaseNode"].Filter("genWeight < 0", "genWeight < 0").Count()
                if "nFTAGenJet/FTAGenHT" in IDs:
                    if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                        diagnosticNodes[processName]["nLep2nJet7GenHT500-550-nominalXS::Sum"] = nodes[processName]["BaseNode"]\
                            .Filter("nFTAGenLep == 2 && nFTAGenJet == 7 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 2, nFTAGenJet 7, FTAGenHT 500-550").Sum("nominalXS")
                        diagnosticNodes[processName]["nLep2nJet7pGenHT500p-nominalXS::Sum"] = nodes[processName]["BaseNode"]\
                            .Filter("nFTAGenLep == 2 && nFTAGenJet >= 7 && 500 <= FTAGenHT", "nFTAGenLep 2, nFTAGenJet 7+, FTAGenHT 500+").Sum("nominalXS")
                        diagnosticNodes[processName]["nLep1nJet9GenHT500-550-nominalXS::Sum"] = nodes[processName]["BaseNode"]\
                            .Filter("nFTAGenLep == 1 && nFTAGenJet == 9 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 1, nFTAGenJet 9, FTAGenHT 500-550").Sum("nominalXS")
                        diagnosticNodes[processName]["nLep1nJet9pGenHT500p-nominalXS::Sum"] = nodes[processName]["BaseNode"]\
                            .Filter("nFTAGenLep == 1 && nFTAGenJet >= 9 && 500 <= FTAGenHT", "nFTAGenLep 1, nFTAGenJet 9+, FTAGenHT 500+").Sum("nominalXS")
                    if fillDiagnosticHistos == True:
                        diagnosticHistos[processName]["NoChannel"] = collections.OrderedDict()
                        diagnosticHistos[processName]["NoChannel"]["GenHT-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___GenHT".format(proc=processName), 
                                      "GenHT;GenHT;#sigma/GeV", 200, 0, 2000), "FTAGenHT", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["GenHT-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___GenHT".format(proc=processName), 
                                      "GenHT;GenHT;#sigma/GeV", 200, 0, 2000), "FTAGenHT", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["nGenJet-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___nGenJet".format(proc=processName), 
                                      "nGenJet;nGenJet;#sigma/nGenJet", 20, 0, 20), "nFTAGenJet", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["nGenJet-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___nGenJet".format(proc=processName), 
                                      "nGenJet;nGenJet;#sigma/nGenJet", 20, 0, 20), "nFTAGenJet", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["nGenLep-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___nGenLep".format(proc=processName), 
                                      "nGenLep;nGenLep;#sigma/nGenLep", 5, 0, 5), "nFTAGenLep", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["nGenLep-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___nGenLep".format(proc=processName), 
                                      "nGenLep;nGenLep;#sigma/nGenLep", 5, 0, 5), "nFTAGenLep", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["HT-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___HT".format(proc=processName), 
                                      "HT;HT;#sigma/GeV", 200, 0, 2000), "diagnostic_HT", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["HT-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___HT".format(proc=processName), 
                                      "HT;HT;#sigma/GeV", 200, 0, 2000), "diagnostic_HT", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["nJet-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___nJet".format(proc=processName), 
                                      "nJet;nJet;#sigma/nJet", 20, 0, 20), "diagnostic_nJet", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["nJet-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___nJet".format(proc=processName), 
                                      "nJet;nJet;#sigma/nJet", 20, 0, 20), "diagnostic_nJet", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["jet1_pt-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet1_pt".format(proc=processName), 
                                      "Leading Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet1_pt", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["jet1_pt-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet1_pt".format(proc=processName), 
                                      "Leading Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet1_pt", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["jet1_eta-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet1_eta".format(proc=processName), 
                                      "Leading Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet1_eta", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["jet1_eta-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet1_eta".format(proc=processName), 
                                      "Leading Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet1_eta", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["jet5_pt-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet5_pt".format(proc=processName), 
                                      "Fifth Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet5_pt", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["jet5_pt-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet5_pt".format(proc=processName), 
                                      "Fifth Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet5_pt", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["jet5_eta-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet5_eta".format(proc=processName), 
                                      "Fift Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet5_eta", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["jet5_eta-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet5_eta".format(proc=processName), 
                                      "Fift Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet5_eta", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["el_pt-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___el_pt".format(proc=processName), 
                                      "e p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_el_pt", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["el_pt-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___el_pt".format(proc=processName), 
                                      "e p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_el_pt", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["el_eta-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___el_eta".format(proc=processName), 
                                      "e #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_el_eta", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["el_eta-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___el_eta".format(proc=processName), 
                                      "e #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_el_eta", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["mu_pt-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___mu_pt".format(proc=processName), 
                                      "#mu p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_mu_pt", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["mu_pt-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___mu_pt".format(proc=processName), 
                                      "#mu p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_mu_pt", "effectiveXS")
                        diagnosticHistos[processName]["NoChannel"]["mu_eta-nominalXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___mu_eta".format(proc=processName), 
                                      "#mu #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_mu_eta", "nominalXS")
                        diagnosticHistos[processName]["NoChannel"]["mu_eta-effectiveXS::Histo"] = nodes[processName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___mu_eta".format(proc=processName), 
                                      "#mu #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_mu_eta", "effectiveXS")

                    diagnosticNodes[processName]["nLep2nJet7GenHT500-550-effectiveXS::Sum"] = nodes[processName]["BaseNode"]\
                        .Filter("nFTAGenLep == 2 && nFTAGenJet == 7 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 2, nFTAGenJet 7, FTAGenHT 500-550").Sum("effectiveXS")
                    diagnosticNodes[processName]["nLep2nJet7pGenHT500p-effectiveXS::Sum"] = nodes[processName]["BaseNode"]\
                        .Filter("nFTAGenLep == 2 && nFTAGenJet >= 7 && 500 <= FTAGenHT", "nFTAGenLep 2, nFTAGenJet 7+, FTAGenHT 500+").Sum("effectiveXS")
                    diagnosticNodes[processName]["nLep1nJet9GenHT500-550-effectiveXS::Sum"] = nodes[processName]["BaseNode"]\
                        .Filter("nFTAGenLep == 1 && nFTAGenJet == 9 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 1, nFTAGenJet 9, FTAGenHT 500-550").Sum("effectiveXS")
                    diagnosticNodes[processName]["nLep1nJet9pGenHT500p-effectiveXS::Sum"] = nodes[processName]["BaseNode"]\
                        .Filter("nFTAGenLep == 1 && nFTAGenJet >= 9 && 500 <= FTAGenHT", "nFTAGenLep 1, nFTAGenJet 9+, FTAGenHT 500+").Sum("effectiveXS")
            if printInfo == True:
                print("splitProcess(..., printInfo=True, ...) set, executing the event loop to gather and print diagnostic info (presumably from the non-event-selected source...")
                for pName, pDict in diagnosticNodes.items():
                    print("processName == {}".format(pName))
                    for dName, dNode in pDict.items():
                        parseDName = dName.split("::")
                        if parseDName[1] in ["Count", "Sum"]:
                            dString = "\t\t\"{}\": {},".format(parseDName[0], dNode.GetValue())
                        elif parseDName[1] in ["Stats"]:
                            thisStat = dNode.GetValue()
                            dString = "\t\t\"{}::Min\": {}".format(parseDName[0], thisStat.GetMin())
                            dString += "\n\t\t\"{}::Mean\": {}".format(parseDName[0], thisStat.GetMean())
                            dString += "\n\t\t\"{}::Max\": {}".format(parseDName[0], thisStat.GetMax())
                        elif parseDName[1] in ["Histo"]:
                            dString = "\t\tNo method implemented for histograms, yet"
                        else:
                            dString = "\tDiagnostic node type not recognized: {}".format(parseDName[1])
                        print(dString)
        else:
            raise RuntimeError("Invalid type passed for splitProcess. Require a dictionary containing keys 'ID' and 'processes' to split the sample.")
        
    else:
        raise RuntimeError("Deprecated, form an inclusive process and configure splitProcess with it.")
            
    prePackedNodes = dict()
    prePackedNodes["snapshotPriority"] = snapshotPriority
    prePackedNodes["filterNodes"] = filterNodes
    prePackedNodes["nodes"] = nodes
    prePackedNodes["countNodes"] = countNodes
    prePackedNodes["diagnosticNodes"] = diagnosticNodes
    prePackedNodes["diagnosticHistos"] = diagnosticHistos
    prePackedNodes["defineNodes"] = defineNodes
    return prePackedNodes

def defineWeights(input_df_or_nodes, era, splitProcess=None, isData=False, verbose=False, final=False, sysVariations={"$NOMINAL":"NoValueNeeded"}):
    """Define all the pre-final or final weights and the variations, to be referened by the sysVariations dictionaries as wgt_final.
    if final=False, do the pre-final weights for BTaggingYields calculations.
    
    pwgt = partial weight, component for final weight
    wgt_$SYSTEMATIC is form of final event weights, i.e. wgt_nom or wgt_puWeightDown
    prewgt_$SYSTEMATIC is form of weight for BTaggingYields calculation, should include everything but pwgt_btag__$SYSTEMATIC"""
    # if splitProcess != None:
    if isinstance(input_df_or_nodes, (dict, collections.OrderedDict)):
        print("Splitting process in defineWeights()")
        filterNodes = input_df_or_nodes.get("filterNodes")
        nodes = input_df_or_nodes.get("nodes")
        defineNodes = input_df_or_nodes.get("defineNodes")
        diagnosticNodes = input_df_or_nodes.get("diagnosticNodes")
        countNodes = input_df_or_nodes.get("countNodes")
    else:
        raise NotImplementedError("Non-split process has been deprecated in defineWeights, wrap the RDF nodes in nodes['<process-name>'] dictionary")
        # rdf = input_df_or_nodes

    #There's only one lepton branch variation (nominal), but if it ever changes, this will serve as sign it's referenced here and made need to be varied
    leppostfix = ""
    lumiDict = {"2017": 41.53,
                "2018": 59.97}


    #era = "2017"
    # mc_def["wgt_SUMW"] = "({xs:s} * {lumi:s} * 1000 * genWeight) / {sumw:s}".format(xs=str(crossSection), lumi=str(lumi), sumw=str(sumWeights))

    #Two lists of weight definitions, one or the other is chosen at the end via 'final' optional parameter
    zFin = []
    zPre = []
    # zFin.append(("pwgt___LumiXS", "wgt_SUMW")) #Now defined in the splitProcess function
    zFin.append(("pwgt_LSF___nom", "(FTALepton{lpf}_SF_nom.size() > 1 ? FTALepton{lpf}_SF_nom.at(0) * FTALepton{lpf}_SF_nom.at(1) : FTALepton{lpf}_SF_nom.at(0))".format(lpf=leppostfix)))
    # zPre.append(("pwgt___LumiXS", "wgt_SUMW")) #alias this until it's better defined here or elsewhere
    zPre.append(("pwgt_LSF___nom", "(FTALepton{lpf}_SF_nom.size() > 1 ? FTALepton{lpf}_SF_nom.at(0) * FTALepton{lpf}_SF_nom.at(1) : FTALepton{lpf}_SF_nom.at(0))".format(lpf=leppostfix)))
    if era == "2017": #This only applies to 2017
        zPre.append(("pwgt_Z_vtx___nom", "((FTALepton{lpf}_pdgId.size() > 1 && (abs(FTALepton{lpf}_pdgId.at(0)) == 11 || abs(FTALepton{lpf}_pdgId.at(1)) == 11)) || (FTALepton{lpf}_pdgId.size() > 0 && abs(FTALepton{lpf}_pdgId.at(0)) == 11)) ? EGamma_HLT_ZVtx_SF_nom : 1.00000000000000".format(lpf=leppostfix)))
    else:
        zPre.append(("pwgt_Z_vtx___nom", "(Int_t)1;"))
    
    #WARNING: on btag weights, it can ALWAYS be 'varied' to match the systematic, so that the event weight from
    #the correct jet collection, btag SFs, and yields is used. Always match! This duplicates some calculations uselessly
    #in the BTaggingYields function, but it should help avoid mistakes at the level of final calculations
    
    print("\nFIXME: Need to propagate pwgt_Z_vtx___nom to all non-nominal event weights properly.\n")
    #Nominal weight
    zFin.append(("wgt___nom", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom * pwgt_btag___nom"))
    #pre-btagging yield weight. Careful modifying, it is 'inherited' for many other weights below!
    zPre.append(("prewgt___nom", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    
    #JES Up and Down - effectively the nominal weight, but with the CORRECT btag weight for those jets!
    if "jesTotalDown" in sysVariations.keys():
        zFin.append(("wgt___jesTotalDown", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag___jesTotalDown * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___jesTotalDown", "prewgt___nom * pwgt_Z_vtx___nom")) #JES *weight* only changes with event-level btag weight, so this is just the nominal
        
    if "jesTotalDown" in sysVariations.keys():
        zPre.append(("prewgt___jesTotalUp", "prewgt___nom"))
        zFin.append(("wgt___jesTotalUp", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag___jesTotalUp"))
    
    #Pileup variations 
    print("FIXME: Using temporary definition of weights for PU variations (change pwgt_btag__VARIATION)")
    if "puWeightDown" in sysVariations.keys():
        zFin.append(("wgt___puWeightDown", "pwgt___LumiXS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag___nom * pwgt_Z_vtx___nom"))
        #zFin.append(("wgt___puWeightDown", "pwgt___LumiXS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag__puWeightDown * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___puWeightDown", "pwgt___LumiXS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
        #zPre.append(("prewgt___puWeightDown", "pwgt___LumiXS * puWeightDown * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    if "puWeightUp" in sysVariations.keys():
        zFin.append(("wgt___puWeightUp", "pwgt___LumiXS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag___nom * pwgt_Z_vtx___nom"))
        #zFin.append(("wgt___puWeightUp", "pwgt___LumiXS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_btag__puWeightUp * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___puWeightUp", "pwgt___LumiXS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
        #zPre.append(("prewgt___puWeightUp", "pwgt___LumiXS * puWeightUp * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    
    
    #L1 PreFiring variations
    print("FIXME: Using temporary definition of weights for L1PreFire variations (change pwgt_btag__VARIATION)")
    if "L1PreFireDown" in sysVariations.keys():
        zFin.append(("wgt___L1PreFireDown", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF___nom * pwgt_btag___nom * pwgt_Z_vtx___nom"))
        #zFin.append(("wgt___L1PreFireDown", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF___nom * pwgt_btag__L1PreFireDown * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___L1PreFireDown", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
        #zPre.append(("prewgt___L1PreFireDown", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Dn * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    
    if "L1PreFireUp" in sysVariations.keys():
        zFin.append(("wgt___L1PreFireUp", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Up * pwgt_LSF___nom * pwgt_btag___nom * pwgt_Z_vtx___nom"))
        #zFin.append(("wgt___L1PreFireUp", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Up * pwgt_LSF___nom * pwgt_btag__L1PreFireUp * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___L1PreFireUp", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Up * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
        #zPre.append(("prewgt___L1PreFireUp", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Up * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    
    #Pure BTagging variations, no other variations necessary. 
    #Since there may be many, use a common base factor for fewer multiplies... for pre-btagging, they're identical!
    print("\n\nWARNING! WARNING! L1PreFiringWeight Only applies to 2017 and perhaps 2016, drop it from calculations in 2018!")
    zFin.append(("pwgt_btagSF_common", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    zPre.append(("pwgt_btagSF_common", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    
    if "btagSF_deepcsv_shape_down_hf" in sysVariations.keys():
        zFin.append(("wgt___btagSF_deepcsv_shape_down_hf", "pwgt_btagSF_common * pwgt_btag___btagSF_deepcsv_shape_down_hf * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___btagSF_deepcsv_shape_down_hf", "pwgt_btagSF_common * pwgt_Z_vtx___nom"))#Really just aliases w/o btagging part
    if "btagSF_deepcsv_shape_up_hf" in sysVariations.keys():
        zFin.append(("wgt___btagSF_deepcsv_shape_up_hf", "pwgt_btagSF_common * pwgt_btag___btagSF_deepcsv_shape_up_hf * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___btagSF_deepcsv_shape_up_hf", "pwgt_btagSF_common * pwgt_Z_vtx___nom"))
    if "btagSF_deepcsv_shape_down_lf" in sysVariations.keys():
        zFin.append(("wgt___btagSF_deepcsv_shape_down_lf", "pwgt_btagSF_common * pwgt_btag___btagSF_deepcsv_shape_down_lf * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___btagSF_deepcsv_shape_down_lf", "pwgt_btagSF_common * pwgt_Z_vtx___nom"))
    if "btagSF_deepcsv_shape_up_lf" in sysVariations.keys():
        zFin.append(("wgt___btagSF_deepcsv_shape_up_lf", "pwgt_btagSF_common * pwgt_btag___btagSF_deepcsv_shape_up_lf * pwgt_Z_vtx___nom"))
        zPre.append(("prewgt___btagSF_deepcsv_shape_up_lf", "pwgt_btagSF_common * pwgt_Z_vtx___nom"))

    #Special variations for testing central components
    zFin.append(("wgt___no_btag_shape_reweight", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    zFin.append(("wgt___no_LSF", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_Z_vtx___nom"))
    zFin.append(("wgt___no_L1PreFiringWeight", "pwgt___LumiXS * puWeight * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    zFin.append(("wgt___no_puWeight", "pwgt___LumiXS * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))

    zPre.append(("prewgt___no_btag_shape_reweight", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    zPre.append(("prewgt___no_LSF", "pwgt___LumiXS * puWeight * L1PreFiringWeight_Nom * pwgt_Z_vtx___nom"))
    zPre.append(("prewgt___no_L1PreFiringWeight", "pwgt___LumiXS * puWeight * pwgt_LSF___nom * pwgt_Z_vtx___nom"))
    zPre.append(("prewgt___no_puWeight", "pwgt___LumiXS * L1PreFiringWeight_Nom * pwgt_LSF___nom * pwgt_Z_vtx___nom"))


    #Factorization/Renormalization weights... depend on dividing genWeight back out?
    #TBD x4 for top samples, MAYBE NOT FOR OTHERS! (Until "Run II Legacy" samples are being used)
    
    #Load the initial or final definitions
    if final:
        z = zFin
    else:
        z = zPre
    nodes = input_df_or_nodes.get("nodes")
    for processName in nodes:
        if processName.lower() == "basenode": continue
        # pdb.set_trace()
        listOfColumns = nodes[processName]["BaseNode"].GetColumnNames()
        if isData:
            defName = "wgt___nom"
            defFunc = "int i = 1; return i"
            if defName not in listOfColumns:
                nodes[processName]["BaseNode"] = nodes[processName]["BaseNode"].Define(defName, defFunc)
        else:
            for defName, defFunc in z:
                if defName in listOfColumns:
                    if verbose:
                        print("{} already defined, skipping".format(defName))
                    continue
                else:
                    if verbose:
                        print("nodes[processName][\"BaseNode\"] = nodes[processName][\"BaseNode\"].Define(\"{}\", \"{}\")".format(defName, defFunc))
                    nodes[processName]["BaseNode"] = nodes[processName]["BaseNode"].Define(defName, defFunc)
                    listOfColumns.push_back(defName) 
               
    return input_df_or_nodes
name = "tt_DL-GF"
vals = bookerV2[name]
path_name = vals["source"]["LJMLogic__ElMu_selection"]
splitProcessConfig = vals.get("splitProcess", None)
verbose=False
#snapshotPriority -1 means this is neither snapshotted nor cached! Memory management...
inclusiveProcessConfig = {"processes": {"{}".format(name): {"filter": "return true;",
                                                            "nEventsPositive": vals.get("nEventsPositive", -1),
                                                            "nEventsNegative": vals.get("nEventsNegative", -1),
                                                            "fractionalContribution": 1,
                                                            "sumWeights": vals.get("sumWeights", -1.0),
                                                            "effectiveCrossSection": vals.get("crossSection", 0),
                                                            "snapshotPriority": -1,
                                                        }}}

input_df = ROOT.ROOT.RDataFrame("Events", path_name)
inputCount = input_df.Count()
inputCount = inputCount.GetValue()
progressbar = ROOT.AddProgressBar(ROOT.RDF.AsRNode(input_df), 2000, long(inputCount))
# r2 = METXYCorr(r, 
#                run_branch = "run", 
#                era = "2017", 
#                isData = False, 
#                npv_branch = "PV_npvs",
#                sysVariations=systematics_2017, 
#                verbose=False
# )
# r2 =  defineLeptons(r2, 
#                     "ElMu",
#                     isData=False, 
#                     era="2017",
#                     useBackupChannel=False,
#                     triggers=None,
#                     sysVariations=systematics_2017,
#                     rdfLeptonSelection=False,
#                     verbose=False
# )
r2 = METXYCorr(input_df,
               run_branch="run",
               era=vals["era"],
               isData=vals["isData"],
               sysVariations=systematics_2017, 
               verbose=verbose,
           )
#Define the leptons based on LeptonLogic bits, to be updated and replaced with code based on triggers/thresholds/leptons present (on-the-fly cuts)
r2 = defineLeptons(r2, 
                   input_lvl_filter="ElMu",
                   isData=vals["isData"], 
                   era=vals["era"],
                   useBackupChannel=False,
                   triggers=None,
                   sysVariations=systematics_2017,
                   rdfLeptonSelection=False,
                   verbose=verbose,
)
r2 = defineJets(r2,
                era=vals["era"],
                bTagger="DeepJet",
                isData=vals["isData"],
                sysVariations=systematics_2017, 
                jetPtMin=30.0,
                jetPUId=None,
                useDeltaR=0.4,
                verbose=verbose,
)
r2 = r2.Filter("nFTALepton == 2 && HT__nom >= 500 && nMediumDeepJetB__nom >= 2 && nFTAJet__nom >= 4")
prePackedNodes = splitProcess(r2, 
                              splitProcess = splitProcessConfig, 
                              inclusiveProcess = inclusiveProcessConfig,
                              sampleName = name, 
                              isData = vals["isData"], 
                              era = vals["era"],
                              printInfo = False,
                          )
prePackedNodes = defineWeights(prePackedNodes,
                               splitProcess = splitProcessConfig,
                               era=vals["era"],
                               isData=vals["isData"],
                               final=False,
                               sysVariations=systematics_2017, 
                               verbose=verbose,
                           )
newnodes = {}
flatteningDict = {}
columns = {}
skipped = {}
flattened = {}
counts = {}
handles = {}
cacheNode = {} #Cache results for saving with snapshots, potentially...
test = {}
varsToSave = []
for leppostfix in [""]:
    varsToSave += [
        "FTALepton{lpf}_pt".format(lpf=leppostfix), 
        "FTALepton{lpf}_eta".format(lpf=leppostfix),
        "FTALepton{lpf}_phi".format(lpf=leppostfix),
        "FTALepton{lpf}_jetIdx".format(lpf=leppostfix),
        "FTALepton{lpf}_pdgId".format(lpf=leppostfix),
        "FTALepton{lpf}_dRll".format(lpf=leppostfix),
        # "FTALepton{lpf}_dPhill".format(lpf=leppostfix),
        # "FTALepton{lpf}_dEtall".format(lpf=leppostfix)
    ]
for branchpostfix in ["__nom","__jesTotalUp", "__jesTotalDown"]:
    varsToSave += [
        "nFTAJet{bpf}".format(bpf=branchpostfix),
        # "FTAJet{bpf}_ptsort".format(bpf=branchpostfix), #sorting index...
        # "FTAJet{bpf}_deepcsvsort".format(bpf=branchpostfix),
        # "FTAJet{bpf}_deepjetsort".format(bpf=branchpostfix), #This is the sorting index...
        # "FTAJet{bpf}_idx".format(bpf=branchpostfix),
        "FTAJet{bpf}_pt".format(bpf=branchpostfix),
        "FTAJet{bpf}_eta".format(bpf=branchpostfix),
        "FTAJet{bpf}_phi".format(bpf=branchpostfix),
        "FTAJet{bpf}_mass".format(bpf=branchpostfix),
        # "FTAJet{bpf}_jetId".format(bpf=branchpostfix),
        # "FTAJet{bpf}_DeepCSVB".format(bpf=branchpostfix),
        # "FTAJet{bpf}_DeepCSVB_sorted".format(bpf=branchpostfix),
        "FTAJet{bpf}_DeepJetB".format(bpf=branchpostfix),
        "FTAJet{bpf}_DeepJetB_sorted".format(bpf=branchpostfix),
        # "FTAJet{bpf}_LooseDeepCSVB".format(bpf=branchpostfix),
        # "FTAJet{bpf}_MediumDeepCSVB".format(bpf=branchpostfix),
        # "FTAJet{bpf}_TightDeepCSVB".format(bpf=branchpostfix),
        # "nLooseDeepCSVB{bpf}".format(bpf=branchpostfix),
        # "nMediumDeepCSVB{bpf}".format(bpf=branchpostfix),
        # "nTightDeepCSVB{bpf}".format(bpf=branchpostfix),
        "FTAJet{bpf}_MediumDeepJetB".format(bpf=branchpostfix),
        "nLooseDeepJetB{bpf}".format(bpf=branchpostfix),
        "nMediumDeepJetB{bpf}".format(bpf=branchpostfix),
        "nTightDeepJetB{bpf}".format(bpf=branchpostfix),
        "ST{bpf}".format(bpf=branchpostfix),
        "HT{bpf}".format(bpf=branchpostfix),
        "HT2M{bpf}".format(bpf=branchpostfix),
        # "HTNum{bpf}".format(bpf=branchpostfix),
        "HTRat{bpf}".format(bpf=branchpostfix),
        "dRbb{bpf}".format(bpf=branchpostfix),
        # "dPhibb{bpf}".format(bpf=branchpostfix),
        # "dEtabb{bpf}".format(bpf=branchpostfix),
        "H{bpf}".format(bpf=branchpostfix),
        "H2M{bpf}".format(bpf=branchpostfix),
        "HTH{bpf}".format(bpf=branchpostfix),
        "HTb{bpf}".format(bpf=branchpostfix),
    ]
# for sname, sval in prePackedNodes["nodes"].items():

#Use reversed order to cycle from highest priority level to lowest, finally calling snapshot on lowest priority level greater than 0
snapshotTrigger = sorted([p for p in prePackedNodes["snapshotPriority"].values() if p > 0])[0]
print(snapshotTrigger)
for sname, spriority in sorted(prePackedNodes["snapshotPriority"].items(), key=lambda x: x[1], reverse=True):
    sval = prePackedNodes["nodes"][sname]
    if sname == "BaseNode": continue#Skip the pre-split node
    snapshotPriority = prePackedNodes["snapshotPriority"][sname]
    if snapshotPriority < 0:
        print("Skipping snapshotPriority < 0 node")
        continue
    if snapshotPriority == 0:
        print("Warning, snapshotPriority 0 node! This points to a splitProcess config without (properly) defined priority value")
        continue
    print(snapshotPriority)
    print(sname)

    newnodes[sname], flatteningDict[sname]= delegateFlattening(sval["BaseNode"], varsToSave, debug=False)
    counts[sname] = newnodes[sname].Count()
    if snapshotPriority > snapshotTrigger:
        #cache and book snapshot (assuming it will not be written due to the RDF bugs)
        cacheNode[sname] = newnodes[sname].Cache(flatteningDict[sname]["finalVars"])
        handles[sname] = bookSnapshot(cacheNode[sname], "ntuple_{}.root".format(sname), lazy=True, columnList=flatteningDict[sname]["finalVars"], 
                                     treename="Events", mode="RECREATE", compressionAlgo="ZSTD", compressionLevel=6, splitLevel=99)
        
    else:
        # handles[sname] = bookSnapshot(newnodes[sname], "ntuple_{}.root".format(sname), lazy=False, columnList=flatteningDict[sname]["finalVars"], 
        #                              treename="Events", mode="RECREATE", compressionAlgo="ZSTD", compressionLevel=6, splitLevel=99)
        # don't make handle for uncached snapshots
        _ = bookSnapshot(newnodes[sname], "ntuple_{}.root".format(sname), lazy=False, columnList=flatteningDict[sname]["finalVars"], 
                                     treename="Events", mode="RECREATE", compressionAlgo="ZSTD", compressionLevel=6, splitLevel=99)
        
    # small = ROOT.std.vector(str)(0)
    # small.push_back("run"); small.push_back("event"); small.push_back("FTAJet5__jesTotalUp_MediumDeepCSVB")
    # cacheNode[sname] = newnodes[sname].Cache(small)
    # test[sname] = cacheNode[sname].Max("FTAJet5__jesTotalUp_MediumDeepCSVB")
    # handles[sname] = bookSnapshot(newnodes[sname], "ntuple_{}.root".format(sname), columnList=flatteningDict[sname]["finalVars"], 
    #                                  treename="Events", mode="RECREATE", compressionAlgo="ZSTD", compressionLevel=6, splitLevel=99)
    # print("Flattened variables")
    # print(flatteningDict[sname]["flattenedVars"])
    # print("Already flat variables")
    # print(flatteningDict[sname]["flatVars"])
    # print("Prepared columns")
    # print(flatteningDict[sname]["finalVars"])
# trigger the overall loop
# progressbar.GetValue()

#Make non-lazy snapshots of each from the Cache
# for sname in cacheNode:
#     handles[sname] = bookSnapshot(newnodes[sname], "ntuple_{}.root".format(sname), lazy=False, columnList=flatteningDict[sname]["finalVars"], 
#                                      treename="Events", mode="RECREATE", compressionAlgo="ZSTD", compressionLevel=6, splitLevel=99)

# for xn, x in newnodes.items():
#     print("{} - {}".format(xn, x))
# for xn, x in handles.items():
#     if "tt_DL-GF" in xn: continue #skip the inclusive sample...
#     x.GetValue()

# pdb.set_trace()

# r3, handle = bookSnapshot(r2, "test_snap2.root", columnList=None, treename="Events", mode="RECREATE", compressionAlgo="LZMA", compressionLevel=6, splitLevel=99)
# h = {}
# # for x in ["FTAMuon1_pt", "FTAElectron1_pt", "FTAElectron2_pt"]:
# #     h[x] = r3.Histo1D(("h_{}".format(x), "{};{};Events".format(x, x), 100, 15, 315), x, "genWeight")
# c = r3.Count()
# booktrigger = ROOT.AddProgressBar(ROOT.RDF.AsRNode(r3), 2000, long(65000))
# # _ = booktrigger.GetValue()

# start = time.time()
# handle.GetValue()
# finish1 = time.time()

# for x in ["FTAMuon1_pt", "FTAElectron1_pt", "FTAElectron2_pt"]:
#     h[x] = r3.Histo1D(("h_{}".format(x), "{};{};Events".format(x, x), 100, 15, 315), x, "genWeight")
# f = ROOT.TFile.Open("test_snap2_hist.root", "RECREATE")
# for x, hist in h.items():
#     hist.GetValue().Write()
# f.Close()
# finish2 = time.time()
# print(finish1-start)
# print(finish2-start)
# print(finish2-finish1)

# v = r2.GetColumnNames()
# # for vv in v:
# #     print("{} - {}".format(vv, r.GetColumnType(vv)))
# v2 = ROOT.std.vector(str)(0)
# v2.push_back("run")
# v2.push_back("luminosityBlock")
# v2.push_back("event")
# v2.push_back("nJet")
# v2.push_back("nMuon")
# v2.push_back("genWeight")
# zz = ROOT.FTA.getOption("RECREATE")
# help(zz)
# ROOT.FTA.bookSnapshot(ROOT.RDF.AsRNode(r), "Events", "lazy_snap.root", v2)
# c = r.Count()

# v = ROOT.std.vector(str)(4); v[0]="nGoodMuon";v[1]="GoodMuon_pt";v[2]="GoodMuon_eta";v[3]="GoodMuon_phi"
# s = rd.Snapshot("Events", "test_snap.root", v) #works
# s = rd.Snapshot("Events", "test_snap.root")
