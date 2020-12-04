import ROOT
# muon_options_syst["LooseRelIso/TightIDandIPCut"] =       {"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_syst", "TH2Lookup", };
for fn, f in enumerate(["2016/UL/postVFP/Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root",
                        "2017/UL/Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root",
                        "2016/UL/postVFP/Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root",
                        "2018/non-UL/EfficienciesAndSF_2018Data_AfterMuonHLTUpdate.root",
                        "2016/UL/preVFP/Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root",
                        "2018/non-UL/EfficienciesAndSF_2018Data_BeforeMuonHLTUpdate.root",
                        "2016/UL/preVFP/Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root",
                        "2018/non-UL/RunABCD_SF_ID.root",
                        "2017/non-UL/EfficienciesAndSF_RunBtoF_Nov17Nov2017.root",
                        "2018/non-UL/RunABCD_SF_ISO.root",
                        "2017/non-UL/RunBCDEF_SF_ID_syst.root",
                        "2018/UL/Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root",
                        "2017/non-UL/RunBCDEF_SF_ISO_syst.root",
                        "2018/UL/Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root",
                        "2017/UL/Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root"]):
    # if fn != 10: continue
    print(f)
    kf = f.split("/")[-1]
    in_file = ROOT.TFile.Open(f, "read")
    subkeys = [(kk.GetName(), kk.GetClassName()) for kk in in_file.GetListOfKeys()]
    for subkey, subkeyclassname in subkeys:
        if subkeyclassname == 'TDirectoryFile': continue
        if "efficiencyData" in subkey or "efficiencyMC" in subkey: continue
        h = in_file.Get(subkey)
        # print("subkey: ", subkey)
        split = subkey.split("_")
        if "iso" not in split[1].lower():
            lutkey = split[1]
        if "iso" in split[1].lower():
            lutkey = "_".join([split[1], split[3]])
        output = 'muon_options_'
        if "_syst" in subkey:
            output += 'syst'
        elif "_stat" in subkey:
            output += 'stat'
        else:
            output += 'central'
        output += '["' + lutkey + '"] = {"' + kf + '", "' + subkey + '", "TH2Lookup", ' + ('"Muon_pt", "Muon_eta"' if 'pt' in h.GetXaxis().GetTitle() else '"Muon_eta", "Muon_pt"') + '};'
        print(output)
    print("\n\n")

    
