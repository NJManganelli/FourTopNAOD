import ROOT
# muon_options_syst["LooseRelIso/TightIDandIPCut"] =       {"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_syst", "TH2Lookup", };
for fn, f in enumerate(["2016/UL/postVFP/egammaEffi.txt_Ele_Loose_postVFP_EGM2D.root",
"2016/UL/postVFP/egammaEffi.txt_Ele_Medium_postVFP_EGM2D.root",
"2016/UL/postVFP/egammaEffi.txt_Ele_Tight_postVFP_EGM2D.root",
"2016/UL/postVFP/egammaEffi.txt_Ele_Veto_postVFP_EGM2D.root",
"2016/UL/postVFP/egammaEffi.txt_Ele_wp80iso_postVFP_EGM2D.root",
"2016/UL/postVFP/egammaEffi.txt_Ele_wp80noiso_postVFP_EGM2D.root",
"2016/UL/postVFP/egammaEffi.txt_Ele_wp90iso_postVFP_EGM2D.root",
"2016/UL/postVFP/egammaEffi.txt_Ele_wp90noiso_postVFP_EGM2D.root",
"2016/UL/preVFP/egammaEffi_ptAbove20.txt_EGM2D_UL2016preVFP.root",
"2016/UL/preVFP/egammaEffi_ptBelow20.txt_EGM2D_UL2016preVFP.root",
"2016/UL/preVFP/egammaEffi.txt_Ele_Loose_preVFP_EGM2D.root",
"2016/UL/preVFP/egammaEffi.txt_Ele_Medium_preVFP_EGM2D.root",
"2016/UL/preVFP/egammaEffi.txt_Ele_Tight_preVFP_EGM2D.root",
"2016/UL/preVFP/egammaEffi.txt_Ele_Veto_preVFP_EGM2D.root",
"2016/UL/preVFP/egammaEffi.txt_Ele_wp80iso_preVFP_EGM2D.root",
"2016/UL/preVFP/egammaEffi.txt_Ele_wp80noiso_preVFP_EGM2D.root",
"2016/UL/preVFP/egammaEffi.txt_Ele_wp90iso_preVFP_EGM2D.root",
"2016/UL/preVFP/egammaEffi.txt_Ele_wp90noiso_preVFP_EGM2D.root",
"2017/non-UL/2017_ElectronLoose.root",
"2017/non-UL/2017_ElectronMedium.root",
"2017/non-UL/2017_ElectronMVA80noiso.root",
"2017/non-UL/2017_ElectronMVA80.root",
"2017/non-UL/2017_ElectronMVA90noiso.root",
"2017/non-UL/2017_ElectronMVA90.root",
"2017/non-UL/2017_ElectronTight.root",
"2017/non-UL/2017_ElectronWPVeto_Fall17V2.root",
"2017/non-UL/egammaEffi.txt_EGM2D_runBCDEF_passingRECO_lowEt.root",
"2017/non-UL/egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root",
"2017/UL/egammaEffi_ptAbove20.txt_EGM2D_UL2017.root",
"2017/UL/egammaEffi_ptBelow20.txt_EGM2D_UL2017.root",
"2017/UL/egammaEffi.txt_EGM2D_Loose_UL17.root",
"2017/UL/egammaEffi.txt_EGM2D_Medium_UL17.root",
"2017/UL/egammaEffi.txt_EGM2D_MVA80iso_UL17.root",
"2017/UL/egammaEffi.txt_EGM2D_MVA80noIso_UL17.root",
"2017/UL/egammaEffi.txt_EGM2D_MVA90iso_UL17.root",
"2017/UL/egammaEffi.txt_EGM2D_MVA90noIso_UL17.root",
"2017/UL/egammaEffi.txt_EGM2D_Tight_UL17.root",
"2017/UL/egammaEffi.txt_EGM2D_Veto_UL17.root",
"2018/non-UL/2018_ElectronLoose.root",
"2018/non-UL/2018_ElectronMedium.root",
"2018/non-UL/2018_ElectronMVA80noiso.root",
"2018/non-UL/2018_ElectronMVA80.root",
"2018/non-UL/2018_ElectronMVA90noiso.root",
"2018/non-UL/2018_ElectronMVA90.root",
"2018/non-UL/2018_ElectronTight.root",
"2018/non-UL/2018_ElectronWPVeto_Fall17V2.root",
"2018/non-UL/egammaEffi.txt_EGM2D_updatedAll.root",
"2018/UL/egammaEffi_ptAbove20.txt_EGM2D_UL2018.root",
"2018/UL/egammaEffi_ptBelow20.txt_EGM2D_UL2018.root",
"2018/UL/egammaEffi.txt_Ele_Loose_EGM2D.root",
"2018/UL/egammaEffi.txt_Ele_Medium_EGM2D.root",
"2018/UL/egammaEffi.txt_Ele_Tight_EGM2D.root",
"2018/UL/egammaEffi.txt_Ele_Veto_EGM2D.root",
"2018/UL/egammaEffi.txt_Ele_wp80iso_EGM2D.root",
"2018/UL/egammaEffi.txt_Ele_wp80noiso_EGM2D.root",
"2018/UL/egammaEffi.txt_Ele_wp90iso_EGM2D.root",
"2018/UL/egammaEffi.txt_Ele_wp90noiso_EGM2D.root"]):
    # if fn != 10: continue
    print(f)
    kf = f.split("/")[-1]
    in_file = ROOT.TFile.Open(f, "read")
    subkeys = [(kk.GetName(), kk.GetClassName()) for kk in in_file.GetListOfKeys()]
    for subkey, subkeyclassname in subkeys:
        if subkey != "EGamma_SF2D": continue
        h = in_file.Get(subkey)
        # print("subkey: ", subkey)
        lutkey = kf.replace("egammaEffi.txt_", "").replace("_EGM2D.root", "")
        output1 = 'electron_options_central'
        output2 = 'electron_options_uncertainty'
        if "pt" not in  h.GetXaxis().GetTitle() and "eta" not in  h.GetXaxis().GetTitle(): print("Failed to deduce axis")
        output1 += '["' + lutkey + '"] = {"' + kf + '", "' + subkey + '", "TH2Lookup", ' + ('"Electron_pt", "Electron_eta"' if 'pt' in h.GetXaxis().GetTitle() else '"Electron_eta", "Electron_pt"') + '};'
        output2 += '["' + lutkey + '"] = {"' + kf + '", "' + subkey + '", "TH2LookupErr", ' + ('"Electron_pt", "Electron_eta"' if 'pt' in h.GetXaxis().GetTitle() else '"Electron_eta", "Electron_pt"') + '};'
        print(output1)
        print(output2)
    print("\n\n")

    
