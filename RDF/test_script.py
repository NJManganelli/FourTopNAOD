import ROOT
import numpy
import ctypes
import array
ROOT.gROOT.ProcessLine(".L test_class.cpp")

print("Testing HLT SF for tight-tight ID leptons in emu channel")
xvec = array.array('d', [20, 40, 60, 80, 100, 150, 200])
yvec = array.array('d', [15, 30, 45, 60, 80, 100, 150, 200])
HLTSF = ROOT.TH2D("HLTSF", "HLT SF test; lep1 pt(); lep2 pt()", 6, xvec, 7, yvec)
for xin in [30, 50, 70, 90, 125, 175]:
    for yin in [22.5, 37.5, 52.5, 70, 90, 125, 175]:
        z = ROOT.FTA.ElMu2017HLTSF(xin, yin)
        if z > 0:
            HLTSF.Fill(xin, yin, z)
hltcan = ROOT.TCanvas("HLTCAN", "", 800, 600)
HLTSF.SetMinimum(0.88)
HLTSF.SetMaximum(0.998)
HLTSF.Draw("COLZ TEXT")
hltcan.Draw()

f_mc = "/eos/user/n/nmangane/data/20200403/mc_test_file.root"
f_data = "/eos/user/n/nmangane/data/20200403/data_test_file.root"
print("Test files for...\nMC:{}\nData:{}".format(f_mc, f_data))

print("Testing TH2Lookup class")
aa = ROOT.TH2Lookup("/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/select_20200403/ElMu_selection/BtaggingYields/BTaggingYields.root")
ROOT.gInterpreter.Declare("TH2Lookup* yielder;")
ROOT.yielder = aa
valnJet = ctypes.c_int(6)
valHT = ctypes.c_double(823)
valYield = ROOT.yielder.getEventYieldRatio("Aggregate", "_deepcsv", valnJet.value, valHT.value)
print("Yield value: {}".format(valYield))
v=ROOT.std.vector(str)(3)
v[0]="Inclusive_bjets_DeepCSV_M"
v[1]="Inclusive_cjets_DeepCSV_M"
v[2]="Inclusive_udsgjets_DeepCSV_M"
for vv in v: print(vv)
a = ROOT.TH2Lookup("/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/select_20200323/ElMu_selection/BtaggingEfficiency/tt_DL-GF_BTagEff.root", v)
ROOT.gInterpreter.Declare("TH2Lookup* alook;")
ROOT.alook = a

r = ROOT.ROOT.RDataFrame("Events", f_mc)#.Range(1000)
rd = r.Define("Jet_eff", 'alook->getJetEfficiency("Inclusive", "DeepCSV_M", &Jet_hadronFlavour, &Jet_pt, &Jet_eta)')

print("Testing FTA::generateIndices function")
jidx = r.Range(10).Define("Jet_idx", "FTA::generateIndices(Jet_pt);").AsNumpy(["Jet_idx", "nJet"])
print(jidx["Jet_idx"])
print(jidx["nJet"])


print("Testing FTA::METXYCorr function")
rd = rd.Define("MET_xycorr_doublet", "FTA::METXYCorr(METFixEE2017_pt, METFixEE2017_phi, run, 2017, false, PV_npvs)")
rd = rd.Define("MET_xycorr_pt", "MET_xycorr_doublet.first")
rd = rd.Define("MET_xycorr_phi", "MET_xycorr_doublet.second")
rd = rd.Define("MET_xycorr_pt_shift", "MET_xycorr_pt - METFixEE2017_pt")
rd = rd.Define("MET_xycorr_phi_shift", "abs(MET_xycorr_phi - METFixEE2017_phi)")
print("Testing FTA::btagEventWeight_shape function")
rd =rd.Define("jet_mask", "Jet_pt > 20 && abs(Jet_eta) < 2.5")
rd = rd.Define("btagPreEventWeight", "genWeight * FTA::btagEventWeight_shape(Jet_btagSF_deepcsv_shape, jet_mask)")
rd = rd.Define("btagEventWeight", "btagPreEventWeight * yielder->getEventYieldRatio(\"Aggregate\", \"_deepcsv\", Jet_pt[jet_mask].size(), Sum(Jet_pt[jet_mask]));")
rd = rd.Define("btagPreShift", "(1 - btagPreEventWeight/genWeight)")
rd = rd.Define("btagFinalShift", "(1 - btagEventWeight/genWeight)")
s1 = rd.Mean("MET_xycorr_pt_shift")
s11 = rd.Mean("MET_xycorr_phi_shift")

r2 = ROOT.ROOT.RDataFrame("Events", f_data)#.Range(1000)
rd2 = r2.Define("genWeight", "double y = 1.0; return y;") #fake the genweight for simplicity of test
rd2 = rd2.Define("MET_xycorr_doublet", "FTA::METXYCorr(METFixEE2017_pt, METFixEE2017_phi, run, 2017, true, PV_npvs)")
rd2 = rd2.Define("MET_xycorr_pt", "MET_xycorr_doublet.first")
rd2 = rd2.Define("MET_xycorr_phi", "MET_xycorr_doublet.second")
rd2 = rd2.Define("MET_xycorr_pt_shift", "MET_xycorr_pt - METFixEE2017_pt")
rd2 = rd2.Define("MET_xycorr_phi_shift", "(MET_xycorr_phi - METFixEE2017_phi)")
s2 = rd2.Mean("MET_xycorr_pt_shift")
s22 = rd2.Mean("MET_xycorr_phi_shift")
# n = rd.AsNumpy("Jet_eff")
# print(n)

print("{} {} {} {}".format(s1.GetValue(), s11.GetValue(), s2.GetValue(), s22.GetValue()))

hists = {}
canv = {}
#MC
#hists["MC_jet_eff"] = rd.Histo1D(("hr", "", 100, 0, 1), "Jet_eff", "genWeight")
#hists["MC_pt"] = rd.Histo2D(("hpt", "", 120, 0, 1200, 120, 0, 1200), "METFixEE2017_pt", "MET_xycorr_pt", "genWeight")
#hists["MC_phi"] = rd.Histo2D(("hphi", "", 72, -3.14, 3.14, 72, -3.14, 3.14), "METFixEE2017_phi", "MET_xycorr_phi", "genWeight")
hists["MC_phi_uncorr"] = rd.Histo1D(("hphi_uncorr", "", 36, -3.14, 3.14), "METFixEE2017_phi", "genWeight")
hists["MC_phi_corr"] = rd.Histo1D(("hphi_corr", "", 36, -3.14, 3.14), "MET_xycorr_phi", "genWeight")
hists["MC_pt_shift"] = rd.Histo1D(("hpt_shift", "", 100, -10, 10), "MET_xycorr_pt_shift", "genWeight")
hists["MC_phi_shift"] = rd.Histo1D(("hphi_shift", "", 72, -3.14, 3.14), "MET_xycorr_phi_shift", "genWeight")
hists["MC_btagPreShift"] = rd.Histo1D(("hbtagPreShift", "", 100, -1, 1), "btagPreShift")
hists["MC_btagFinalShift"] = rd.Histo1D(("hbtagFinalShift", "", 100, -1, 1), "btagFinalShift")


#Data
#hists["Data_pt"] = rd2.Histo2D(("hdpt", "", 120, 0, 1200, 120, 0, 1200), "METFixEE2017_pt", "MET_xycorr_pt", "genWeight")
#hists["Data_phi"] = rd2.Histo2D(("hdphi", "", 72, -3.14, 3.14, 72, -3.14, 3.14), "METFixEE2017_phi", "MET_xycorr_phi", "genWeight")
hists["Data_phi_uncorr"] = rd2.Histo1D(("hdphi_uncorr", "", 36, -3.14, 3.14), "METFixEE2017_phi", "genWeight")
hists["Data_phi_corr"] = rd2.Histo1D(("hdphi_corr", "", 36, -3.14, 3.14), "MET_xycorr_phi", "genWeight")
hists["Data_pt_shift"] = rd.Histo1D(("hdpt_shift", "", 100, -10, 10), "MET_xycorr_pt_shift", "genWeight")
hists["Data_phi_shift"] = rd.Histo1D(("hdphi_shift", "", 72, -3.14, 3.14), "MET_xycorr_phi_shift", "genWeight")

for hname, hist in hists.items():
    t = type(hist.GetValue())
    if "TH2" in str(t):
        canv[hname] = ROOT.TCanvas("c_{}".format(hname), "", 800, 600)
        hist.Draw("COLZ TEXT")
    else:
        if "Data_" in hname: continue
        canv[hname] = ROOT.TCanvas("c_{}".format(hname), "", 800, 600)
        hist.DrawNormalized("HIST")
        if hname.replace("MC_", "Data_") in hists:
            hists["{}".format(hname.replace("MC_","Data_"))].SetLineColor(ROOT.kRed)
            hists["{}".format(hname.replace("MC_","Data_"))].DrawNormalized("HIST SAME")
    if "eff" in hname:
        canv[hname].SetLogx()
    canv[hname].Draw()
