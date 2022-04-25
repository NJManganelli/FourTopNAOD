import collections
import ROOT
from FourTopNAOD.RDF.analyzer.cpp import make_cpp_safe_name

def METXYCorr(input_df, run_branch = "run", era = "2017", isData = True, npv_branch = "PV_npvs",
               sysVariations={"$NOMINAL": {"jet_mask": "jet_mask", 
                                           "lep_postfix": "",
                                           "jet_pt_var": "Jet_pt",
                                           "jet_mass_var": "Jet_mass",
                                           "met_pt_var": "METFixEE2017_pt",
                                           "met_phi_var": "METFixEE2017_phi",
                                           "btagSF": "Jet_btagSF_deepcsv_shape",
                                           "weightVariation": False},
                                     },
              sysFilter=["$NOMINAL"],
                       verbose=False):
    rdf = input_df
    listOfColumns = input_df.GetColumnNames()
    z = []
    for sysVarRaw, sysDict in sysVariations.items():
        #Only do systematics that are in the filter list (storing raw systematic names...
        if sysVarRaw not in sysFilter:
            continue
        #skip systematic variations on data, only do the nominal
        if isData and sysVarRaw != "$NOMINAL": 
            continue
        #get final systematic name
        sysVar = sysVarRaw.replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', '')).replace("$ERA", era)
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        branchpostfix = "ERROR_NO_BRANCH_POSTFIX_METXYCorr"
        if isWeightVariation == True: 
            continue
        else:
            branchpostfix = "__" + sysVar
        metPt = sysDict.get("met_pt_var").replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', ''))
        metPhi = sysDict.get("met_phi_var").replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', ''))
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
        #if metDoublet not in listOfColumns:
            #if verbose: 
            #    print("Doing MET XY correction:\nrdf = rdf.Define(\"{0}\", \"{1}\")".format(metDoublet, def_fnc))
            #rdf = rdf.Define(metDoublet, def_fnc)
            #listOfColumns.push_back(metDoublet)
        #if metPt not in listOfColumns and metPhi not in listOfColumns:
            #if verbose: 
            #    print("rdf = rdf.Define(\"{0}\", \"{1}\")".format(metPt, metDoublet))
            #    print("rdf = rdf.Define(\"{0}\", \"{1}\")".format(metPhi, metDoublet))
            #rdf = rdf.Define(metPt, "{}.first".format(metDoublet))
            #rdf = rdf.Define(metPhi, "{}.second".format(metDoublet))
            #listOfColumns.push_back(metPt)
            #listOfColumns.push_back(metPhi)
    #return rdf

def defineLeptons(input_df, input_lvl_filter=None, isData=True, era="2017", rdfLeptonSelection=False, useBackupChannel=False, verbose=False,
                  triggers=[],
                  sysVariations={"$NOMINAL": {"jet_mask": "jet_mask", 
                                              "lep_postfix": "",
                                              "jet_pt_var": "Jet_pt",
                                              "jet_mass_var": "Jet_mass",
                                              "met_pt_var": "METFixEE2017_pt",
                                              "met_phi_var": "METFixEE2017_phi",
                                              "btagSF": "Jet_btagSF_deepcsv_shape",
                                              "weightVariation": False},
                             },
                  sysFilter=["$NOMINAL"],
              ):
    """Function to take in a dataframe and return one with new columns defined,
    plus event filtering based on the criteria defined inside the function"""
        
    #Set up channel bits for selection and baseline. Separation not necessary in this stage, but convenient for loops
    Chan = {}
    if era == "2017":# or era == "2018":
        Chan["ElMu"] = 24576
        Chan["MuMu"] = 6144
        Chan["ElEl"] = 512
        Chan["ElEl_LowMET"] = Chan["ElEl"]
        Chan["ElEl_HighMET"] = Chan["ElEl"]
        Chan["Mu"] = 128
        Chan["El"] = 64
        Chan["ElMu_baseline"] = 24576
        Chan["MuMu_baseline"] = 6144
        Chan["ElEl_baseline"] = 512
        Chan["Mu_baseline"] = 128
        Chan["El_baseline"] = 64
    elif era == "2018":
        Chan["ElMu"] = 20480
        Chan["MuMu"] = 2048
        Chan["ElEl"] = 512
        Chan["ElEl_LowMET"] = Chan["ElEl"]
        Chan["ElEl_HighMET"] = Chan["ElEl"]
        Chan["Mu"] = 256
        Chan["El"] = 128
        Chan["ElMu_baseline"] = 20480
        Chan["MuMu_baseline"] = 2048
        Chan["ElEl_baseline"] = 512
        Chan["Mu_baseline"] = 256
        Chan["El_baseline"] = 128
    else:
        raise ValueError("other eras not supported right now")
    Chan["selection"] = Chan["ElMu"] + Chan["MuMu"] + Chan["ElEl"] + Chan["Mu"] + Chan["El"]
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
        for trgTup in triggers:
            if trgTup.era != era: continue
            # trg = trgTup.trigger
            # rdf = rdf.Define("typecast___{}".format(trg), "return (int){} == true;".format(trg))
        if not rdfLeptonSelection:
            rdf = rdf.Define("mu_mask", "(Muon_OSV_{0} & {1}) > 0 && Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_looseId == true && Muon_pfIsoId >= 4 && abs(Muon_ip3d) < 0.10 && abs(Muon_dz) < 0.02".format(lvl_type, Chan[input_lvl_filter]))
            rdf = rdf.Define("e_mask", "(Electron_OSV_{0} & {1}) > 0 && Electron_pt > 15 && Electron_cutBased >= 2 && ((abs(Electron_eta) < 1.4442 && abs(Electron_ip3d) < 0.05 && abs(Electron_dz) < 0.1) || (abs(Electron_eta) > 1.5660 && abs(Electron_eta) < 2.5 && abs(Electron_ip3d) < 0.10 && abs(Electron_dz) < 0.2))".format(lvl_type, Chan[input_lvl_filter]))
        else:
            pass
    z = []
    #only valid postfix for leptons, excluding calculations involving MET, is "" for now, can become "__SOMETHING" inside a loop on systematic variations 
    leppostfix = ""
    
    #MUONS
    z.append(("Muon_idx", "FTA::generateIndices(Muon_pt);"))
    z.append(("nFTAMuon{lpf}".format(lpf=leppostfix), "static_cast<Int_t>(Muon_pt[mu_mask].size())"))
    z.append(("FTAMuon{lpf}_idx".format(lpf=leppostfix), "Muon_idx[mu_mask]"))
    z.append(("FTAMuon{lpf}_pfIsoId".format(lpf=leppostfix), "Muon_pfIsoId[mu_mask]"))
    # z.append(("FTAMuon{lpf}_looseId".format(lpf=leppostfix), "static_cast<int>(Muon_looseId[mu_mask])")) #This causes problems if of length 0 as in ElEl channel!
    z.append(("FTAMuon{lpf}_looseId".format(lpf=leppostfix), "ROOT::VecOps::RVec<bool> v {}; return Muon_looseId[mu_mask].size() > 0 ? Muon_looseId[mu_mask] : v;"))
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


    for sysVarRaw, sysDict in sysVariations.items():
        #skip systematic variations on data, only do the nominal
        if isData and sysVarRaw != "$NOMINAL": 
            continue
        #Only do systematics that are in the filter list (storing raw systematic names...
        if sysVarRaw not in sysFilter:
            continue
        #get final systematic name
        sysVar = sysVarRaw.replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', '')).replace("$ERA", era)
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        if isWeightVariation == True: continue
        syspostfix = "___" + sysVar
        branchpostfix = "__nom" if isWeightVariation else "__" + sysVar
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

def defineJets(input_df, era="2017", doAK8Jets=False, jetPtMin=30.0, jetPUIdChoice=None, useDeltaR=True, isData=True,
               nJetsToHisto=10, bTagger="DeepCSV", verbose=False,
               sysVariations={"$NOMINAL": {"jet_mask": "jet_mask",
                                           "lep_postfix": "", 
                                           "jet_pt_var": "Jet_pt",
                                           "jet_mass_var": "Jet_mass",
                                           "met_pt_var": "METFixEE2017_pt",
                                           "met_phi_var": "METFixEE2017_phi",
                                           "btagSF": "Jet_btagSF_deepcsv_shape",
                                           "weightVariation": False},
                          },
              sysFilter=["$NOMINAL"],
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
    leppostfix = ""
    #z will be a list of tuples to define, so that we can do cleaner error handling and checks
    z = []
    if era == "2018":
        #HEM affects 38.6/fb of lumi, and not the first 21.1/fb. As such, do a binomial draw with p=38.6/59.7 (mean p * ntot = p * 1) and apply hem shift
        z.append(("Jet_pt_hem_down", "if(rng.Binomial(1, 0.6465) > 0){"\
                                     "auto hem_mask = Jet_phi > -1.57 && Jet_phi < -0.87 && Jet_eta > -2.5 && Jet_eta < -1.3;"\
                                     "ROOT::VecOps::RVec<float> Jet_pt_hem = 0.8 * Jet_pt_nom;"\
                                     "return ROOT::VecOps::Where(hem_mask, Jet_pt_hem, Jet_pt);"\
                                     "} else {"\
                                     "return Jet_pt;}"\
              ))
    for sysVarRaw, sysDict in sysVariations.items():
        #skip systematic variations on data, only do the nominal
        if isData and sysVarRaw != "$NOMINAL": 
            continue
        #Only do systematics that are in the filter list (storing raw systematic names...
        if sysVarRaw not in sysFilter:
            continue
        #get final systematic name
        sysVar = sysVarRaw.replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', '')).replace("$ERA", era)
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        if isWeightVariation == True: continue
        jetMask = sysDict.get("jet_mask").replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', ''))
        jetPt = sysDict.get("jet_pt_var").replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', ''))
        jetMass = sysDict.get("jet_mass_var").replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', ''))
        postfix = "__" + sysVar
        
        #Fill lists
        jetPUId = ""
        if jetPUIdChoice:
            if jetPUIdChoice == 'N':
                jetPUId = ""
            elif jetPUIdChoice == 'L':
                jetPUId = " && ({jpt} >= 50 || Jet_puId >= 4)".format(jpt=jetPt) #pass Loose Id, >=6 pass Medium, ==7 pass Tight
            elif jetPUIdChoice == 'M':
                jetPUId = " && ({jpt} >= 50 || Jet_puId >= 6)".format(jpt=jetPt) #pass Loose Id, >=6 pass Medium, ==7 pass Tight
            elif jetPUIdChoice == 'T':
                jetPUId = " && ({jpt} >= 50 || Jet_puId == 7)".format(jpt=jetPt) #pass Loose Id, >=6 pass Medium, ==7 pass Tight
            else:
                raise ValueError("Invalid Jet PU Id selected")
        else:
            jetPUId = ""
        z.append(("Jet_idx", "FTA::generateIndices(Jet_pt)"))
        z.append(("pre{jm}".format(jm=jetMask), "ROOT::VecOps::RVec<Int_t> prejm = ({jpt} >= {jptMin} && abs(Jet_eta) <= 2.5 && Jet_jetId > 2{jpuid}); return prejm".format(lpf=leppostfix, 
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
        # z.append(("FTACrossCleanedJet{pf}_pt".format(pf=postfix), "std::cout << \"event: \" << event << \" entry: \" << rdfentry_ << \" nMu nEl nLep nLep_jetIdx  \" ; std::cout << nFTAMuon{lpf} << \" \" << nFTAElectron{lpf} << \" \" << nFTALepton{lpf} << \" \" << FTALepton{lpf}_jetIdx.size() << \"   \"; std::cout << FTALepton{lpf}_jetIdx.at(0) << \"  \" ; std::cout << pre{jm} << std::endl; double ret = (FTALepton{lpf}_jetIdx.at(0) >= 0 && pre{jm}.at(FTALepton{lpf}_jetIdx.at(0)) == true) ? {jpt}.at(FTALepton{lpf}_jetIdx.at(0)) : 0.0; return ret;".format(jm=jetMask, lpf=leppostfix, jpt=jetPt)))
        z.append(("FTACrossCleanedJet{pf}_pt".format(pf=postfix), "(FTALepton{lpf}_jetIdx.at(0) >= 0 && pre{jm}.at(FTALepton{lpf}_jetIdx.at(0)) == true) ? {jpt}.at(FTALepton{lpf}_jetIdx.at(0)) : 0.0".format(jm=jetMask, lpf=leppostfix, jpt=jetPt)))
        z.append(("FTACrossCleanedJet{pf}_rawpt".format(pf=postfix), "(FTALepton{lpf}_jetIdx.at(0) >= 0 && pre{jm}.at(FTALepton{lpf}_jetIdx.at(0)) == true) ? (1 - Jet_rawFactor.at(FTALepton{lpf}_jetIdx.at(0))) * {jpt}.at(FTALepton{lpf}_jetIdx.at(0)) : 0.0".format(jm=jetMask, lpf=leppostfix, jpt=jetPt)))
        z.append(("FTACrossCleanedJet{pf}_leppt".format(pf=postfix), "(FTALepton{lpf}_jetIdx.at(0) >= 0 && pre{jm}.at(FTALepton{lpf}_jetIdx.at(0)) == true) ? FTALepton{lpf}_pt.at(0) : 0.0".format(jm=jetMask, lpf=leppostfix, jpt=jetPt)))
        # # z.append(("FTACrossCleanedJet{pf}_diffpt".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) >= 0 ? FTACrossCleanedJet{pf}_pt + FTACrossCleanedJet{pf}_leppt - FTACrossCleanedJet{pf}_rawpt : -9999".format(jm=jetMask, lpf=leppostfix, pf=postfix)))
        z.append(("FTACrossCleanedJet{pf}_diffpt".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) >= 0 ? FTACrossCleanedJet{pf}_leppt - FTACrossCleanedJet{pf}_pt : -9999".format(jm=jetMask, lpf=leppostfix, pf=postfix)))
        z.append(("FTACrossCleanedJet{pf}_diffptraw".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) >= 0 ? (-1.0 * Jet_rawFactor * {jpt}).at(FTALepton{lpf}_jetIdx.at(0)) : -9999".format(jm=jetMask, lpf=leppostfix, pf=postfix, jpt=jetPt)))
        z.append(("FTACrossCleanedJet{pf}_diffptrawinverted".format(pf=postfix), "FTALepton{lpf}_jetIdx.at(0) < 0 ? ROOT::VecOps::RVec<Float_t>(-1.0 * (Jet_rawFactor * {jpt})[pre{jm}]) : ROOT::VecOps::RVec<Float_t> {{-9999.0}}".format(jm=jetMask, lpf=leppostfix, pf=postfix, jpt=jetPt)))
        z.append(("nFTAJet{pf}".format(pf=postfix), "static_cast<Int_t>({jm}[{jm}].size())".format(jm=jetMask)))
        z.append(("FTAJet{pf}_ptsort".format(pf=postfix), "Reverse(Argsort({jpt}[{jm}]))".format(jpt=jetPt, jm=jetMask)))
        z.append(("take_{jm}".format(jm=jetMask), "ROOT::VecOps::Reverse(ROOT::VecOps::Argsort({jpt}[{jm}]))".format(jpt=jetPt, jm=jetMask)))
        z.append(("take_noleadingpair_{jm}".format(jm=jetMask), "ROOT::VecOps::Take(take_{jm}, take_{jm}.size() - 2)".format(jm=jetMask)))
        z.append(("FTAScalarRecoilTotal{pf}_pt".format(pf=postfix), "Sum(ROOT::VecOps::Take({jpt}, take_noleadingpair_{jm}))".format(jm=jetMask, jpt=jetPt)))
        z.append(("FTAScalarRecoilAverage{pf}_pt".format(pf=postfix), "FTAScalarRecoilTotal{pf}_pt / take_noleadingpair_{jm}.size()".format(pf=postfix, jm=jetMask)))
        z.append(("FTAVectorRecoil{pf}_px".format(pf=postfix), "ROOT::VecOps::Take({jpt} * cos(Jet_phi), take_noleadingpair_{jm})".format(jm=jetMask, jpt=jetPt)))
        z.append(("FTAVectorRecoil{pf}_py".format(pf=postfix), "ROOT::VecOps::Take({jpt} * sin(Jet_phi), take_noleadingpair_{jm})".format(jm=jetMask, jpt=jetPt)))
        z.append(("FTAVectorRecoil{pf}_pt".format(pf=postfix), "sqrt(pow(FTAVectorRecoil{pf}_px, 2) + pow(FTAVectorRecoil{pf}_py, 2))".format(pf=postfix)))
        z.append(("FTAJet{pf}_deepcsvsort".format(pf=postfix), "Reverse(Argsort(Jet_{btv}[{jm}]))".format(btv=bTagWorkingPointDict[era]["DeepCSV"]["Var"], jm=jetMask)))
        z.append(("FTAJet{pf}_deepjetsort".format(pf=postfix), "Reverse(Argsort(Jet_{btv}[{jm}]))".format(btv=bTagWorkingPointDict[era]["DeepJet"]["Var"], jm=jetMask)))
        print("FIXME: To be pt-sorted, all corresponding values should be converted from Variable[mask] to Take(Variable, FTAJet{pf}_ptsort)...\".format(pf=postfix)")
        z.append(("FTAJet{pf}_idx".format(pf=postfix), "Jet_idx[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_pt".format(pf=postfix), "{jpt}[{jm}]".format(jpt=jetPt, jm=jetMask)))
        z.append(("FTAJet{pf}_eta".format(pf=postfix), "Jet_eta[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_phi".format(pf=postfix), "Jet_phi[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_mass".format(pf=postfix), "{jms}[{jm}]".format(jms=jetMass, jm=jetMask)))
        z.append(("FTAJet{pf}_jetId".format(pf=postfix), "Jet_jetId[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_nConstituents".format(pf=postfix), "Jet_nConstituents[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_muEF".format(pf=postfix), "Jet_muEF[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_chEmEF".format(pf=postfix), "Jet_chEmEF[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_chHEF".format(pf=postfix), "Jet_chHEF[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_neEmEF".format(pf=postfix), "Jet_neEmEF[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_neHEF".format(pf=postfix), "Jet_neHEF[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_chFPV0EF".format(pf=postfix), "Jet_chFPV0EF[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_chFPV1EF".format(pf=postfix), "Jet_chFPV1EF[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_chFPV2EF".format(pf=postfix), "Jet_chFPV2EF[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_chFPV3EF".format(pf=postfix), "Jet_chFPV3EF[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_puIdDisc".format(pf=postfix), "Jet_puIdDisc[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_puId".format(pf=postfix), "Jet_puId[{jm}]".format(jm=jetMask)))
        if isData == False:
            z.append(("FTAJet{pf}_genJetIdx".format(pf=postfix), "Jet_genJetIdx[{jm}]".format(jm=jetMask)))
            z.append(("FTAJet{pf}_genpt".format(pf=postfix), "ROOT::VecOps::RVec<Float_t> temp;"\
                      "for(int i=0; i < FTAJet{pf}_genJetIdx.size(); ++i){{"\
                      "if(FTAJet{pf}_genJetIdx.at(i) > -1 && FTAJet{pf}_genJetIdx.at(i) < GenJet_pt.size())"\
                      "{{ temp.push_back(GenJet_pt.at(FTAJet{pf}_genJetIdx.at(i)));}}"\
                      "else{{temp.push_back(0.0);}}"\
                      "}}"\
                      "return temp;".format(pf=postfix)))
            z.append(("nFTAJet{pf}_genMatched".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_genJetIdx[FTAJet{pf}_genJetIdx >= 0].size())".format(pf=postfix)))
            z.append(("nFTAJet{pf}_nonGenMatched".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_genJetIdx[FTAJet{pf}_genJetIdx < 0].size())".format(pf=postfix)))
            z.append(("nFTAJet{pf}_puIdLoose".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_genJetIdx[(FTAJet{pf}_puId >= 4 || FTAJet{pf}_pt >= 50)].size())".format(pf=postfix)))
            z.append(("nFTAJet{pf}_genMatched_puIdLoose".format(pf=postfix), "static_cast<Int_t>(FTAJet{pf}_genJetIdx[FTAJet{pf}_genJetIdx >= 0 && (FTAJet{pf}_puId >= 4 || FTAJet{pf}_pt >= 50)].size())".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepCSVB".format(pf=postfix), "Jet_btagDeepB[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_DeepCSVB_sorted".format(pf=postfix), "Take(FTAJet{pf}_DeepCSVB, FTAJet{pf}_deepcsvsort)".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepCSVB_sorted_LeadtagJet".format(pf=postfix), "FTAJet{pf}_DeepCSVB_sorted.at(0, -0.10)".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepCSVB_sorted_SubleadtagJet".format(pf=postfix), "FTAJet{pf}_DeepCSVB_sorted.at(1, -0.10)".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepJetB".format(pf=postfix), "Jet_btagDeepFlavB[{jm}]".format(jm=jetMask)))
        z.append(("FTAJet{pf}_DeepJetB_sorted".format(pf=postfix), "Take(FTAJet{pf}_DeepJetB, FTAJet{pf}_deepjetsort)".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepJetB_sorted_LeadtagJet".format(pf=postfix), "FTAJet{pf}_DeepJetB_sorted.at(0, -0.10)".format(pf=postfix)))
        z.append(("FTAJet{pf}_DeepJetB_sorted_SubleadtagJet".format(pf=postfix), "FTAJet{pf}_DeepJetB_sorted.at(1, -0.10)".format(pf=postfix)))
        #Deprecating these, taken care of within the delegateFlattening method if the variables are added in the getNtuple...() functions
        # for x in range(nJetsToHisto):
        #     z.append(("FTAJet{pf}_pt_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_pt.size() > {n} ? FTAJet{pf}_pt.at({n}) : -9999".format(pf=postfix, n=x)))
        #     z.append(("FTAJet{pf}_eta_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_eta.size() > {n} ? FTAJet{pf}_phi.at({n}) : -9999".format(pf=postfix, n=x)))
        #     z.append(("FTAJet{pf}_phi_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_phi.size() > {n} ? FTAJet{pf}_phi.at({n}) : -9999".format(pf=postfix, n=x)))
        #     z.append(("FTAJet{pf}_DeepCSVB_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepCSVB.size() > {n} ? FTAJet{pf}_DeepCSVB.at({n}) : -9999".format(pf=postfix, n=x)))
        #     z.append(("FTAJet{pf}_DeepJetB_jet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepJetB.size() > {n} ? FTAJet{pf}_DeepJetB.at({n}) : -9999".format(pf=postfix, n=x)))
        #     z.append(("FTAJet{pf}_DeepCSVB_sortedjet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepCSVB_sorted.size() > {n} ? FTAJet{pf}_DeepCSVB_sorted.at({n}) : -9999".format(pf=postfix, n=x)))
        #     z.append(("FTAJet{pf}_DeepJetB_sortedjet{n}".format(pf=postfix, n=x+1), "FTAJet{pf}_DeepJetB_sorted.size() > {n} ? FTAJet{pf}_DeepJetB_sorted.at({n}) : -9999".format(pf=postfix, n=x)))
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
        if isData == False:
            z.append(("GenMatchedHT{pf}".format(pf=postfix), "Sum(FTAJet{pf}_genpt)".format(pf=postfix)))
        z.append(("HT{pf}".format(pf=postfix), "Sum(FTAJet{pf}_pt)".format(pf=postfix)))
        if isData == False:
            z.append(("HTminusGenMatchedHT{pf}".format(pf=postfix), "HT{pf}-GenMatchedHT{pf}".format(pf=postfix)))
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


def defineWeights(name, input_df_or_nodes, era, splitProcess=None, isData=False, isSignal=False, verbose=False, final=False, disableNjetMultiplicityCorrection=False, enableTopPtReweighting=False, sysVariations={"$NOMINAL":"ValueNeeded"}, sysFilter=["$NOMINAL"]):
    """Define all the pre-final or final weights and the variations, to be referened by the sysVariations dictionaries as wgt_final.
    if final=False, do the pre-final weights for BTaggingYields calculations.
    
    pwgt = partial weight, component for final weight
    wgt_$SYSTEMATIC is form of final event weights, i.e. wgt_nom or wgt_pileupDown
    prewgt_$SYSTEMATIC is form of weight for BTaggingYields calculation, should include everything but pwgt_btag__$SYSTEMATIC"""
    # if splitProcess != None:
    if isinstance(input_df_or_nodes, (dict, collections.OrderedDict)):
        filterNodes = input_df_or_nodes.get("filterNodes")
        nodes = input_df_or_nodes.get("nodes")
        defineNodes = input_df_or_nodes.get("defineNodes")
        diagnosticNodes = input_df_or_nodes.get("diagnosticNodes")
        countNodes = input_df_or_nodes.get("countNodes")
        ntupleVariables = input_df_or_nodes.get("ntupleVariables", ROOT.std.vector(str)())
    else:
        raise NotImplementedError("Non-split process has been deprecated in defineWeights, wrap the RDF nodes in nodes['<process-name>'] dictionary")
        # rdf = input_df_or_nodes

    #There's only one lepton branch variation (nominal), but if it ever changes, this will serve as sign it's referenced here and made need to be varied
    leppostfix = ""

    #Start the new implementatino
    zPre = []
    zFin = []
    z = []
    for sysVarRaw, sysDict in sysVariations.items():
        #Only do systematics that are in the filter list (storing raw systematic names...
        if sysVarRaw not in sysFilter:
            continue
        leppostfix = sysDict.get('lep_postfix', '')
        #get final systematic name
        sysVar = sysVarRaw.replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', '')).replace("$ERA", era)
        if sysDict.get("isNominal", False) or sysDict.get("isSystematicForSample", False): 
            for wgtKey, wgtDef in sysDict.get("commonWeights", {}).items():
                zPre.append((wgtKey.replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", leppostfix).replace("$SAMPLE", make_cpp_safe_name(name)),
                             wgtDef.replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", leppostfix).replace("$SAMPLE", make_cpp_safe_name(name))))
        for wgtKey, wgtDef in sysDict.get("preWeights", {}).items():
            zPre.append((wgtKey.replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", leppostfix).replace("$SAMPLE", make_cpp_safe_name(name)),
                         wgtDef.replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", leppostfix).replace("$SAMPLE", make_cpp_safe_name(name))))
        for wgtKey, wgtDef in sysDict.get("finalWeights", {}).items():
            zFin.append((wgtKey.replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", leppostfix).replace("$SAMPLE", make_cpp_safe_name(name)),
                         wgtDef.replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", leppostfix).replace("$SAMPLE", make_cpp_safe_name(name))))
            finalKey = zFin[-1][0]
            presumedNominal = "wgt___nom"
            zFin.append(("weightLogAbsoluteRelative___$SYSTEMATIC".replace("$SYSTEMATIC", sysVar), "std::log(std::fabs({}/{} + 0.000000000001))".format(finalKey, presumedNominal)))
                
    
    #Load the initial or final definitions
    if final:
        z = zFin
    else:
        z = zPre
    nodes = input_df_or_nodes.get("nodes")
    for eraAndSampleName in nodes:
        if eraAndSampleName.lower() == "basenode": continue
        listOfColumns = nodes[eraAndSampleName]["BaseNode"].GetColumnNames()
        if isData:
            defName = "wgt___nom"
            defFunc = "int i = 1; return i"
            if defName not in listOfColumns:
                nodes[eraAndSampleName]["BaseNode"] = nodes[eraAndSampleName]["BaseNode"].Define(defName, defFunc)
        else:
            for defName, defFunc in z:
                #Apply era-specific rules to the weights, such as whether L1PreFire applies
                if era == "2016":
                    if defName in ["NONE"]:
                        continue
                    defFuncModulated = defFunc
                elif era == "2017":
                    if defName in ["NONE"]:
                        continue
                    defFuncModulated = defFunc
                elif era == "2018":
                    if defName in ["prefireUp", "prefireDown"]:
                        continue
                    #We don't want the L1 Prefiring weight in 2018, it doesn't apply
                    defFuncModulated = defFunc.replace("L1PreFiringWeight_Nom", "1.0")\
                                              .replace("L1PreFiringWeight_Dn", "1.0")\
                                              .replace("L1PreFiringWeight_Up", "1.0")
                else:
                    raise RuntimeError("Unhandled era '{}' in method defineWeights()".format(era))
                if enableTopPtReweighting and ("ttother" in eraAndSampleName.lower() or "ttnobb" in eraAndSampleName.lower()):
                    if verbose:
                        print("Top pt reweighting function applied to eraAndSample {}: {} = {}".format(eraAndSampleName, defName, defFuncModulated))
                else:
                    defFuncModulated = defFuncModulated.replace("pwgt_top_pT_data_nlo", "1.0").replace("pwgt_top_pT_nnlo_nlo", "1.0")
                #Careful... here, eraAndSampleName is actually eraAndProcessName? 
                if disableNjetMultiplicityCorrection or ("ttother" not in eraAndSampleName.lower() and 
                                                         "ttbb" not in eraAndSampleName.lower() and 
                                                         "ttnobb" not in eraAndSampleName.lower()):
                    if defName.startswith("pwgt_ttbar_njet_multiplicity"):
                        defFuncModulated = "return 1.0;"
                        if verbose:
                            print("Not applying ttbar jet multiplicity corrections to eraAndSample {}".format(eraAndSampleName))
                            if disableNjetMultiplicityCorrection: print("disableNjetMultiplicityCorrection = True")
                    # defFuncModulated = defFuncModulated.replace("pwgt_ttbar_njet_multiplicity___$SYSTEMATIC".replace("$SYSTEMATIC", sysVar), "1.0").replace("pwgt_ttbar_njet_multiplicity___$NOMINAL".replace("$NOMINAL", "nom"), "1.0")
                else:
                    if verbose:
                        print("ttbar jet multiplicity corrections applied to eraAndSample {}: {} = {}".format(eraAndSampleName, defName, defFuncModulated))
                if defName in listOfColumns:
                    if verbose:
                        print("{} already defined, skipping".format(defName))
                    continue
                else:
                    # prereqs = re.findall(r"[\w']+", defFunc)
                    # allPreReqs = True
                    # for prereq in prereqs:
                    #     if prereq not in listOfColumns: allPreReqs = False
                    
                    if verbose:
                        print("nodes[eraAndSampleName][\"BaseNode\"] = nodes[eraAndSampleName][\"BaseNode\"].Define(\"{}\", \"{}\")".format(defName, defFuncModulated))
                    nodes[eraAndSampleName]["BaseNode"] = nodes[eraAndSampleName]["BaseNode"].Define(defName, defFuncModulated)
                    if final:
                        ntupleVariables[eraAndSampleName].push_back(defName)
                    listOfColumns.push_back(defName) 

                    # if allPreReqs:
                    #     nodes[eraAndSampleName]["BaseNode"] = nodes[eraAndSampleName]["BaseNode"].Define(defName, defFunc)
                    #     listOfColumns.push_back(defName) 
                    # else:
                    #     print("Skipping definition for {} due to missing prereqs in the list: {}".format(defName, prereqs))
               
    #return the dictionary of all nodes
    return input_df_or_nodes

def cutPVandMETFilters(input_df, level, isData=False):
    """Deprecated in favor of FTFunctions.cpp function applyMETandPVFilters"""
    if "baseline" in level: 
        lvl = "baseline"
    else:
        lvl = "selection"
    PVbits = 0b00000000000000000111
    METbits_MC = 0b00000000001111110000
    METbits_Data = 0b00000000000000001000
    if isData:
        METbits = METbits_MC + METbits_Data + PVbits
    else:
        METbits = METbits_MC + PVbits
    rdf = input_df.Filter("(ESV_JetMETLogic_{lvl} & {bits}) >= {bits}".format(lvl=lvl, bits=METbits), "PV, MET Filters")
    return rdf

def insertPVandMETFilters(input_df, level, era="2017", isData=False):
    """Deprecated in favor of FTFunctions.cpp function applyMETandPVFilters"""
    rdf = input_df
    #flags for MET filters
    FlagsDict = {"2016" :  
                 { "isData" : ["globalSuperTightHalo2016Filter"],
                   "Common" :  ["goodVertices",
                                "HBHENoiseFilter",
                                "HBHENoiseIsoFilter",
                                "EcalDeadCellTriggerPrimitiveFilter",
                                "BadPFMuonFilter"
                               ],
                   "NotRecommended" : ["BadChargedCandidateFilter",
                                       "eeBadScFilter"
                                      ],
                 },
                 "2017" :  
                 { "isData" : ["globalSuperTightHalo2016Filter"],
                   "Common" :  ["goodVertices",
                                "HBHENoiseFilter",
                                "HBHENoiseIsoFilter",
                                "EcalDeadCellTriggerPrimitiveFilter",
                                "BadPFMuonFilter",
                                "ecalBadCalibFilterV2"
                               ],
                  "NotRecommended" : ["BadChargedCandidateFilter",
                                      "eeBadScFilter"
                                     ],
                 },
                 "2018" :  { "isData" : ["globalSuperTightHalo2016Filter"],
                            "Common" :  ["goodVertices",
                                         "HBHENoiseFilter",
                                         "HBHENoiseIsoFilter",
                                         "EcalDeadCellTriggerPrimitiveFilter",
                                         "BadPFMuonFilter",
                                         "ecalBadCalibFilterV2"
                                        ],
                            "NotRecommended" : ["BadChargedCandidateFilter",
                                                "eeBadScFilter"
                                               ],
                           },
                } 
    Flags = FlagsDict[era]

    #2016selection required !isFake(), nDegreesOfFreedom> 4 (strictly),|z| < 24 (in cm? fractions of acentimeter?), and rho =sqrt(PV.x**2 + PV.y**2)< 2
    #Cuts are to use strictly less than and greater than, i.e. PV.ndof > minNDoF, not >=
    PVCutDict = {
            '2016':{
                'minNDoF': 4,
                'maxAbsZ': 24.0,
                'maxRho': 2
                },
            '2017':{
                'minNDoF': 4,
                'maxAbsZ': 24.0,
                'maxRho': 2
                },
            '2018':{
                'minNDoF': 4,
                'maxAbsZ': 24.0,
                'maxRho': 2
                }
        }
    PVCut = PVCutDict[era]

#    if "selection" in level:
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000000001), "PV NDoF > 4")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000000010), "PV |z| < 24.0")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000000100), "PV rho < 2")
#        if isData == True:
#            rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000001000), "MET globalSuperTightHalo2016Filter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000010000), "MET goodVertices")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000000100000), "MET HBHENoiseFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000001000000), "MET HBHENoiseIsoFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000010000000), "MET EcalDeadCellTriggerPrimitiveFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000000100000000), "MET BadPFMuonFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000001000000000), "MET ecalBadCalibFilterV2")
#    elif "baseline" in level:
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000000001), "PV NDoF > 4")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000000010), "PV |z| < 24.0")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000000100), "PV rho < 2")
#        if isData == True:
#            rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000001000), "MET globalSuperTightHalo2016Filter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000010000), "MET goodVertices")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000000100000), "MET HBHENoiseFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000001000000), "MET HBHENoiseIsoFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000010000000), "MET EcalDeadCellTriggerPrimitiveFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000000100000000), "MET BadPFMuonFilter")
#        rdf = rdf.Filter("(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000001000000000), "MET ecalBadCalibFilterV2")
#    return rdf
    
#def defineEventVars(input_df):
#    rdf = input_df
#    #rdf = rdf.Define("JML_baseline_pass", "(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00001100011111111111))#Cut on MET pt, nJet, HT
#    rdf = rdf.Define("JML_baseline_pass", "(ESV_JetMETLogic_baseline & {0}) >= {0}".format(0b00000000001111111111))#Only PV and MET filters required to pass
#    #rdf = rdf.Define("JML_selection_pass", "(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00001100011111111111))#Cut on MET pt, nJet, HT
#    rdf = rdf.Define("JML_selection_pass", "(ESV_JetMETLogic_selection & {0}) >= {0}".format(0b00000000001111111111))#Only PV and MET filters required to pass
#    return rdf

def splitProcess(input_df, splitProcess=None, sampleName=None, isData=True, era="2017", isUL="non-UL", inputNtupleVariables=None, printInfo=False, inclusiveProcess=None, fillDiagnosticHistos=False, inputSampleCard=None):
    if isinstance(isUL, bool):
        if isUL:
            isUL = "UL"
        else:
            isUL = "non-UL"            
    lumi = {"2016": {"non-UL": 36.33,
                     "UL": 36.33},
            "2017": {"non-UL": 41.53,
                     "UL": 41.48},
            "2018": {"non-UL": 59.74,
                     "UL": 59.83},
            "RunII": {"non-UL": 137.60,
                      "UL": 137.65}
        }[era][isUL] #Immediately grab by era and UL status
    lumiUncertainty = {"2016": "1.012", "2017": "1.023", "2018": "1.025", "RunII": "1.016"}[era]
    filterNodes = dict() #For storing tuples to debug and be verbose about
    defineNodes = collections.OrderedDict() #For storing all histogram tuples --> Easier debugging when printed out, can do branch checks prior to invoking HistoND, etc...
    countNodes = dict() #For storing the counts at each node
    snapshotPriority = dict()
    diagnosticNodes = dict()
    diagnosticHistos = dict()
    ntupleVariables = dict()
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
                IDs = dict()
            if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                inclusiveProc = inclusiveProcess.get("processes")
                inclusiveDict = list(inclusiveProc.values())[0]
                if list(inclusiveProc.keys())[0] not in splitProcs:
                    pass
                    # splitProcs.update(inclusiveProc) #don't update the central dict, so we can roundtrip write it...
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
            for preProcessName, processDict in list(splitProcs.items()) + list(inclusiveProc.items()):
                eraAndSampleName = era + "___" + preProcessName
                eraAndProcessName = eraAndSampleName.replace("-HDAMPdown", "").replace("-HDAMPup", "").replace("-TuneCP5down", "").replace("-TuneCP5up", "")
                filterString = processDict.get("filter")
                snapshotPriority[eraAndSampleName] = processDict.get("snapshotPriority", 0)
                filterName = "{} :: {}".format(eraAndSampleName, filterString.replace(" && ", " and ").replace(" || ", " or ")\
                                               .replace("&&", " and ").replace("||", " or "))
                if not isData:
                    #Make the fractional contribution equal to N_eff(sample_j) / Sum(N_eff(sample_i)), where N_eff = nEventsPositive - nEventsNegative
                    #Need to gather those bookkeeping stats from the original source rather than the ones after event selection
                    effectiveCrossSection = processDict.get("effectiveCrossSection")
                    effectiveXS = processDict.get("effectiveXS")
                    sumWeights = processDict.get("sumWeights")
                    # nEffective = processDict.get("nEventsPositive") - processDict.get("nEventsNegative")
                    fractionalContribution = processDict.get("fractionalContribution")
                    phaseSpaceFactor = processDict.get("phaseSpaceFactor")
                    #Calculate XS * Lumi
                    print("FIXME: Need to modify fractional sample weighting to use the meta info, defaulting to 1.0 right now")
                    print("OPTIONAL: Need to take the lumi value from the actual sample card era, not the presumed one passed to analyzer")
                    wgtFormula = f"{effectiveCrossSection} * {lumi} * 1000 * genWeight * {fractionalContribution} * {phaseSpaceFactor} / {sumWeights}"
                    if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                        formulaForNominalXS = "{nXS:f} * genWeight / {sW:f}".format(nXS=inclusiveDict.get("effectiveCrossSection"),
                                                                                    sW=inclusiveDict.get("sumWeights")
                        )
                        print("{} - nominalXS - {}".format(eraAndSampleName, formulaForNominalXS))
                        formulaForEffectiveXS = "{eXS:f} * genWeight * {frCon:f} / {sW:f}".format(eXS=effectiveCrossSection,
                                                                                      frCon=fractionalContribution,
                                                                                      sW=sumWeights
                        )
                        print("{} - effectiveXS - {}".format(eraAndSampleName, formulaForEffectiveXS))
                    if fillDiagnosticHistos == True:
                        diagnostic_e_mask = "Electron_pt > 15 && Electron_cutBased >= 2 && ((abs(Electron_eta) < 1.4442 && abs(Electron_ip3d) < 0.05 && abs(Electron_dz) < 0.1) || (abs(Electron_eta) > 1.5660 && abs(Electron_eta) < 2.5 && abs(Electron_ip3d) < 0.10 && abs(Electron_dz) < 0.2))"
                        diagnostic_mu_mask = "Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_looseId == true && Muon_pfIsoId >= 4 && abs(Muon_ip3d) < 0.10 && abs(Muon_dz) < 0.02"
                        diagnostic_lepjet_idx = "Concatenate(Muon_jetIdx[diagnostic_mu_mask], Electron_jetIdx[diagnostic_e_mask])"
                        diagnostic_jet_idx = "FTA::generateIndices(Jet_pt)"
                        diagnostic_jet_mask = "ROOT::VecOps::RVec<int> jmask = (Jet_pt > 30 && abs(Jet_eta) < 2.5 && Jet_jetId > 2); "\
                                              "for(int i=0; i < diagnostic_lepjet_idx.size(); ++i){jmask = jmask && diagnostic_jet_idx != diagnostic_lepjet_idx.at(i);}"\
                                              "return jmask;"
                if eraAndSampleName not in nodes:
                    #add in any ntuple variables already defined, plus subprocess-specific ones from the dict
                    ntupleVariables[eraAndSampleName] = ROOT.std.vector(str)()
                    if inputNtupleVariables is not None:
                        for var in inputNtupleVariables:
                            ntupleVariables[eraAndSampleName].push_back(var)
                    #L-2 filter, should be the packedEventID filter in that case
                    filterNodes[eraAndSampleName] = dict()
                    filterNodes[eraAndSampleName]["BaseNode"] = (filterString, filterName, eraAndSampleName, None, None, None, None)
                    nodes[eraAndSampleName] = dict()
                    if not isData:
                        nodes[eraAndSampleName]["BaseNode"] = nodes["BaseNode"]\
                            .Filter(filterNodes[eraAndSampleName]["BaseNode"][0], filterNodes[eraAndSampleName]["BaseNode"][1])\
                            .Define("pwgt___LumiXS", wgtFormula)
                        if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                            nodes[eraAndSampleName]["BaseNode"] = nodes[eraAndSampleName]["BaseNode"]\
                                .Define("nominalXS", formulaForNominalXS)\
                                .Define("nominalXS2", "pow(nominalXS, 2)")\
                                .Define("effectiveXS", formulaForEffectiveXS)\
                                .Define("effectiveXS2", "pow(effectiveXS, 2)")
                        if fillDiagnosticHistos == True:
                            nodes[eraAndSampleName]["BaseNode"] = nodes[eraAndSampleName]["BaseNode"]\
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
                        nodes[eraAndSampleName]["BaseNode"] = nodes["BaseNode"]\
                            .Filter(filterNodes[eraAndSampleName]["BaseNode"][0], filterNodes[eraAndSampleName]["BaseNode"][1])
                    countNodes[eraAndSampleName] = dict()
                    countNodes[eraAndSampleName]["BaseNode"] = nodes[eraAndSampleName]["BaseNode"].Count()
                    diagnosticNodes[eraAndSampleName] = collections.OrderedDict()
                    diagnosticHistos[eraAndSampleName] = dict()
                    defineNodes[eraAndSampleName] = collections.OrderedDict()
                if not isData:
                    #Need to gather those bookkeeping stats from the original source rather than the ones after event selection...
                    diagnosticNodes[eraAndSampleName]["sumWeights::Sum"] = nodes[eraAndSampleName]["BaseNode"].Sum("genWeight")
                    diagnosticNodes[eraAndSampleName]["sumWeights2::Sum"] = nodes[eraAndSampleName]["BaseNode"].Define("genWeight2", "pow(genWeight, 2)").Sum("genWeight2")
                    if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                        diagnosticNodes[eraAndSampleName]["nominalXS::Sum"] = nodes[eraAndSampleName]["BaseNode"].Sum("nominalXS")
                        diagnosticNodes[eraAndSampleName]["nominalXS2::Sum"] = nodes[eraAndSampleName]["BaseNode"].Sum("nominalXS2")
                    diagnosticNodes[eraAndSampleName]["effectiveXS::Sum"] = nodes[eraAndSampleName]["BaseNode"].Sum("effectiveXS")
                    diagnosticNodes[eraAndSampleName]["effectiveXS2::Sum"] = nodes[eraAndSampleName]["BaseNode"].Sum("effectiveXS2")
                    diagnosticNodes[eraAndSampleName]["nEventsPositive::Count"] = nodes[eraAndSampleName]["BaseNode"].Filter("genWeight >= 0", "genWeight >= 0").Count()
                    diagnosticNodes[eraAndSampleName]["nEventsNegative::Count"] = nodes[eraAndSampleName]["BaseNode"].Filter("genWeight < 0", "genWeight < 0").Count()
                    if fillDiagnosticHistos == True:
                        if "NoChannel" not in diagnosticHistos[eraAndSampleName].keys():
                            diagnosticHistos[eraAndSampleName]["NoChannel"] = dict()
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["XS-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Define("Unity", "return static_cast<int>(1);")\
                            .Histo1D(("{proc}___nominalXS___diagnostic___XS".format(proc=eraAndProcessName), 
                                      "#sigma;;#sigma", 1, 0, 2), "Unity", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["XS-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Define("Unity", "return static_cast<int>(1);")\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___XS".format(proc=eraAndProcessName), 
                                      "#sigma;;#sigma", 1, 0, 2), "Unity", "effectiveXS")
                        if nodes[eraAndSampleName]["BaseNode"].HasColumn("LHE_HT"):
                            diagnosticHistos[eraAndSampleName]["NoChannel"]["LHE_HT-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                                .Histo1D(("{proc}___effectiveXS___diagnostic___LHE_HT".format(proc=eraAndProcessName), 
                                          "#sigma;;#sigma", 600, 0, 3000), "LHE_HT", "effectiveXS")
                if "nFTAGenJet/FTAGenHT" in IDs and IDs["nFTAGenJet/FTAGenHT"]:
                    if isinstance(inclusiveProcess, (dict,collections.OrderedDict)) and "processes" in inclusiveProcess.keys():
                        diagnosticNodes[eraAndSampleName]["nLep2nJet7GenHT500-550-nominalXS::Sum"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Filter("nFTAGenLep == 2 && nFTAGenJet == 7 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 2, nFTAGenJet 7, FTAGenHT 500-550").Sum("nominalXS")
                        diagnosticNodes[eraAndSampleName]["nLep2nJet7pGenHT500p-nominalXS::Sum"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Filter("nFTAGenLep == 2 && nFTAGenJet >= 7 && 500 <= FTAGenHT", "nFTAGenLep 2, nFTAGenJet 7+, FTAGenHT 500+").Sum("nominalXS")
                        diagnosticNodes[eraAndSampleName]["nLep1nJet9GenHT500-550-nominalXS::Sum"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Filter("nFTAGenLep == 1 && nFTAGenJet == 9 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 1, nFTAGenJet 9, FTAGenHT 500-550").Sum("nominalXS")
                        diagnosticNodes[eraAndSampleName]["nLep1nJet9pGenHT500p-nominalXS::Sum"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Filter("nFTAGenLep == 1 && nFTAGenJet >= 9 && 500 <= FTAGenHT", "nFTAGenLep 1, nFTAGenJet 9+, FTAGenHT 500+").Sum("nominalXS")
                    if fillDiagnosticHistos == True:
                        if "NoChannel" not in diagnosticHistos[eraAndSampleName].keys():
                            diagnosticHistos[eraAndSampleName]["NoChannel"] = dict()
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["GenHT-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___GenHT".format(proc=eraAndProcessName), 
                                      "GenHT;GenHT;#sigma/GeV", 200, 0, 2000), "FTAGenHT", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["GenHT-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___GenHT".format(proc=eraAndProcessName), 
                                      "GenHT;GenHT;#sigma/GeV", 200, 0, 2000), "FTAGenHT", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["nGenJet-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___nGenJet".format(proc=eraAndProcessName), 
                                      "nGenJet;nGenJet;#sigma/nGenJet", 20, 0, 20), "nFTAGenJet", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["nGenJet-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___nGenJet".format(proc=eraAndProcessName), 
                                      "nGenJet;nGenJet;#sigma/nGenJet", 20, 0, 20), "nFTAGenJet", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["nGenLep-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___nGenLep".format(proc=eraAndProcessName), 
                                      "nGenLep;nGenLep;#sigma/nGenLep", 5, 0, 5), "nFTAGenLep", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["nGenLep-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___nGenLep".format(proc=eraAndProcessName), 
                                      "nGenLep;nGenLep;#sigma/nGenLep", 5, 0, 5), "nFTAGenLep", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["HT-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___HT".format(proc=eraAndProcessName), 
                                      "HT;HT;#sigma/GeV", 200, 0, 2000), "diagnostic_HT", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["HT-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___HT".format(proc=eraAndProcessName), 
                                      "HT;HT;#sigma/GeV", 200, 0, 2000), "diagnostic_HT", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["nJet-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___nJet".format(proc=eraAndProcessName), 
                                      "nJet;nJet;#sigma/nJet", 20, 0, 20), "diagnostic_nJet", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["nJet-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___nJet".format(proc=eraAndProcessName), 
                                      "nJet;nJet;#sigma/nJet", 20, 0, 20), "diagnostic_nJet", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["jet1_pt-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet1_pt".format(proc=eraAndProcessName), 
                                      "Leading Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet1_pt", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["jet1_pt-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet1_pt".format(proc=eraAndProcessName), 
                                      "Leading Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet1_pt", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["jet1_eta-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet1_eta".format(proc=eraAndProcessName), 
                                      "Leading Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet1_eta", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["jet1_eta-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet1_eta".format(proc=eraAndProcessName), 
                                      "Leading Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet1_eta", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["jet5_pt-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet5_pt".format(proc=eraAndProcessName), 
                                      "Fifth Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet5_pt", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["jet5_pt-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet5_pt".format(proc=eraAndProcessName), 
                                      "Fifth Jet p_{T};p_{T};#sigma/GeV", 100, 0, 500), "diagnostic_jet5_pt", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["jet5_eta-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___jet5_eta".format(proc=eraAndProcessName), 
                                      "Fift Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet5_eta", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["jet5_eta-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___jet5_eta".format(proc=eraAndProcessName), 
                                      "Fift Jet #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_jet5_eta", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["el_pt-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___el_pt".format(proc=eraAndProcessName), 
                                      "e p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_el_pt", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["el_pt-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___el_pt".format(proc=eraAndProcessName), 
                                      "e p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_el_pt", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["el_eta-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___el_eta".format(proc=eraAndProcessName), 
                                      "e #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_el_eta", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["el_eta-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___el_eta".format(proc=eraAndProcessName), 
                                      "e #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_el_eta", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["mu_pt-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___mu_pt".format(proc=eraAndProcessName), 
                                      "#mu p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_mu_pt", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["mu_pt-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___mu_pt".format(proc=eraAndProcessName), 
                                      "#mu p_{T};p_{T};#sigma/GeV", 100, 0, 150), "diagnostic_mu_pt", "effectiveXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["mu_eta-nominalXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___nominalXS___diagnostic___mu_eta".format(proc=eraAndProcessName), 
                                      "#mu #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_mu_eta", "nominalXS")
                        diagnosticHistos[eraAndSampleName]["NoChannel"]["mu_eta-effectiveXS::Histo"] = nodes[eraAndSampleName]["BaseNode"]\
                            .Histo1D(("{proc}___effectiveXS___diagnostic___mu_eta".format(proc=eraAndProcessName), 
                                      "#mu #Eta;#Eta;#sigma/GeV", 100, -3, 3), "diagnostic_mu_eta", "effectiveXS")

                    diagnosticNodes[eraAndSampleName]["nLep2nJet7GenHT500-550-effectiveXS::Sum"] = nodes[eraAndSampleName]["BaseNode"]\
                        .Filter("nFTAGenLep == 2 && nFTAGenJet == 7 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 2, nFTAGenJet 7, FTAGenHT 500-550").Sum("effectiveXS")
                    diagnosticNodes[eraAndSampleName]["nLep2nJet7pGenHT500p-effectiveXS::Sum"] = nodes[eraAndSampleName]["BaseNode"]\
                        .Filter("nFTAGenLep == 2 && nFTAGenJet >= 7 && 500 <= FTAGenHT", "nFTAGenLep 2, nFTAGenJet 7+, FTAGenHT 500+").Sum("effectiveXS")
                    diagnosticNodes[eraAndSampleName]["nLep1nJet9GenHT500-550-effectiveXS::Sum"] = nodes[eraAndSampleName]["BaseNode"]\
                        .Filter("nFTAGenLep == 1 && nFTAGenJet == 9 && 500 <= FTAGenHT && FTAGenHT < 550", "nFTAGenLep 1, nFTAGenJet 9, FTAGenHT 500-550").Sum("effectiveXS")
                    diagnosticNodes[eraAndSampleName]["nLep1nJet9pGenHT500p-effectiveXS::Sum"] = nodes[eraAndSampleName]["BaseNode"]\
                        .Filter("nFTAGenLep == 1 && nFTAGenJet >= 9 && 500 <= FTAGenHT", "nFTAGenLep 1, nFTAGenJet 9+, FTAGenHT 500+").Sum("effectiveXS")
            if printInfo == True:
                print("splitProcess(..., printInfo=True, ...) set, executing the event loop to gather and print diagnostic info (presumably from the non-event-selected source...")
                for pName, pDict in diagnosticNodes.items():
                    preProcessName = pName.split("___")[1]
                    print("eraAndSampleName == {}".format(pName))
                    for dName, dNode in pDict.items():
                        parseDName = dName.split("::")
                        if parseDName[1] in ["Count", "Sum"]:
                            dString = "\t\t\"{}\": {},".format(parseDName[0], dNode.GetValue())
                            if inputSampleCard is not None and sampleName in inputSampleCard:
                                if "splitProcess" in inputSampleCard[sampleName].keys():
                                    if preProcessName in inputSampleCard[sampleName]['splitProcess']['processes'].keys() and parseDName[0] in inputSampleCard[sampleName]['splitProcess']['processes'][preProcessName]:
                                        if dName == "sumWeights::Sum": print(preProcessName, " updated in yaml file for split process")
                                        inputSampleCard[sampleName]['splitProcess']['processes'][preProcessName][parseDName[0]] = dNode.GetValue()
                                    elif preProcessName + "_inclusive" in inputSampleCard[sampleName]['splitProcess']['inclusiveProcess'].keys() and parseDName[0] in inputSampleCard[sampleName]['splitProcess']['inclusiveProcess'][preProcessName + "_inclusive"]:
                                        if dName == "sumWeights::Sum": 
                                            print(preProcessName, " updated in yaml file for inclusive process")
                                            if inputSampleCard[sampleName]['sumWeights'] != dNode.GetValue(): 
                                                print("Mismatch in inclusive sumWeights(2) with Runs tree value: {} vs {}".format(dNode.GetValue(), inputSampleCard[sampleName]['sumWeights']))
                                        inputSampleCard[sampleName]['splitProcess']['inclusiveProcess'][preProcessName + "_inclusive"][parseDName[0]] = dNode.GetValue()
                                        if dName in ["nEventsPositive::Count", "nEventsNegative::Count"]:
                                            inputSampleCard[sampleName][parseDName[0]] = dNode.GetValue()
                                else:
                                    if dName in ["nEventsPositive::Count", "nEventsNegative::Count"]:
                                        inputSampleCard[sampleName][parseDName[0]] = dNode.GetValue()
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
    prePackedNodes["ntupleVariables"] = ntupleVariables
    prePackedNodes["filterNodes"] = filterNodes
    prePackedNodes["nodes"] = nodes
    prePackedNodes["countNodes"] = countNodes
    prePackedNodes["diagnosticNodes"] = diagnosticNodes
    prePackedNodes["diagnosticHistos"] = diagnosticHistos
    prePackedNodes["defineNodes"] = defineNodes
    return prePackedNodes
