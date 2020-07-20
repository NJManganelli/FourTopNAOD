import ROOT
import pdb

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

def bookLazySnapshot(input_df, filename, columnList=None, treename="Events", mode="RECREATE", compressionAlgo="LZ4", compressionLevel=6, splitLevel=99, debug=False):
    finalVars = ROOT.std.vector(str)(0)
    desiredOriginalColumns = ["run", "luminosityBlock", "event", "genWeight",]
    undesiredDefinedColumns = ["MET_xycorr_doublet__nom", "MET_xycorr_doublet__jesTotalDown", "MET_xycorr_doublet__jesTotalUp", "mu_mask", "e_mask", "jet_mask",
                               "Electron_idx", "Muon_idx", "Jet_idx"]
    allColumns = input_df.GetColumnNames()
    definedColumns = input_df.GetDefinedColumnNames()
    rdf = input_df


    for var in allColumns:
        #Check if column in superset is also in defined columns
        if var in definedColumns:
            if var in undesiredDefinedColumns:
                if debug:
                    print("Skip {}".format(var))
                continue
        #Column is in original column list, not in defined columns
        elif var not in desiredOriginalColumns:
            if debug:
                print("Skip {}".format(var))
            continue
        if "ROOT::VecOps::RVec" in rdf.GetColumnType(var):
            if debug:
                print("Flatten {}".format(var))
            if "FTAMuon" in var or "FTALepton" in var or "FTAElectron" in var:
                depth = 2
            elif "FTAJet" in var:
                depth = 10
            else:
                depth = 2
            rdf, flattenedVars = flattenVariable(rdf, var, depth, static_cast=True, fallback=None, debug=debug)
            for dvar in flattenedVars:
                if dvar not in rdf.GetDefinedColumnNames():
                    print("What in the god damned flying fuck")
            for fvar in flattenedVars:
                finalVars.push_back(fvar)
        else:
            if debug:
                print("Retain {}".format(var))
            finalVars.push_back(var)
        
    for c in finalVars:
        print("{:45s} | {}".format(c, rdf.GetColumnType(c)))
    
    Algos = {"ZLIB": 1,
             "LZMA": 2,
             "LZ4": 4,
             "ZSTD": 5
         }
    sopt = ROOT.RDF.RSnapshotOptions(mode, Algos[compressionAlgo], compressionLevel, 0, splitLevel, True) #lazy is last option
    handle = rdf.Snapshot(treename, filename, finalVars, sopt)
    print(type(handle))
    handle.GetValue()
    # print("mode: {}\nalgo: {}\nlevel: {}\nsplit: {}\nlazy: {}".format(sopt.fMode, sopt.fCompressionAlgorithm, sopt.fCompressionLevel, splitLevel, sopt.fLazy))


def flattenVariable(input_df, var, depth, static_cast=None, fallback=None, debug=False):
    """Take an RVec or std::vector of variables and define new columns for the first n (depth) elements, falling back to a default value if less than n elements are in an event."""

    rdf = input_df
    t = rdf.GetColumnType(var) #Get the type for deduction of casting rule and fallback value
    flats = [] #Store the defined variables so they may be added to a list for writing
    if static_cast is True: #deduce the static_cast and store the beginning and end of the wrapper in 'sci' and 'sce'
        sce = ")"
        if "<double>" or "<float>" in t:
            sci = "static_cast<Double_t>("
        elif "<uint>" in t:
            sci = "static_cast<Uint_t>("
        elif "<int>" in t:
            sci = "static_cast<Int_t>("
        else:
            raise NotImplementedError("No known casting rule")
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
r = ROOT.ROOT.RDataFrame("Events", "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tttt*.root")
r2 = METXYCorr(r, 
               run_branch = "run", 
               era = "2017", 
               isData = False, 
               npv_branch = "PV_npvs",
               sysVariations=systematics_2017, 
               verbose=False
)
r2 =  defineLeptons(r2, 
                    "ElMu",
                    isData=False, 
                    era="2017",
                    useBackupChannel=False,
                    triggers=None,
                    sysVariations=systematics_2017,
                    rdfLeptonSelection=False,
                    verbose=False
)
bookLazySnapshot(r2, "test_snap2.root", columnList=None, treename="Events", mode="RECREATE", compressionAlgo="LZMA", compressionLevel=6, splitLevel=99)

v = r2.GetColumnNames()
# for vv in v:
#     print("{} - {}".format(vv, r.GetColumnType(vv)))
v2 = ROOT.std.vector(str)(0)
v2.push_back("run")
v2.push_back("luminosityBlock")
v2.push_back("event")
v2.push_back("nJet")
v2.push_back("nMuon")
v2.push_back("genWeight")
# zz = ROOT.FTA.getOption("RECREATE")
# help(zz)
# ROOT.FTA.bookLazySnapshot(ROOT.RDF.AsRNode(r), "Events", "lazy_snap.root", v2)
# c = r.Count()

# v = ROOT.std.vector(str)(4); v[0]="nGoodMuon";v[1]="GoodMuon_pt";v[2]="GoodMuon_eta";v[3]="GoodMuon_phi"
# s = rd.Snapshot("Events", "test_snap.root", v) #works
# s = rd.Snapshot("Events", "test_snap.root")
