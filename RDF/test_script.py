import ROOT
import numpy
ROOT.gROOT.ProcessLine(".L test_class.cpp")
v=ROOT.std.vector(str)(3)
v[0]="Inclusive_bjets_DeepCSV_M"
v[1]="Inclusive_cjets_DeepCSV_M"
v[2]="Inclusive_udsgjets_DeepCSV_M"
for vv in v: print(vv)
a = ROOT.TH2Lookup("select_20200323/ElMu_selection/BtaggingEfficiency/tt_DL-GF_BTagEff.root", v)
ROOT.gInterpreter.Declare("TH2Lookup* alook;")
ROOT.alook = a

r = ROOT.ROOT.RDataFrame("Events", "tt_DL-GF-1_2017_v2+ElMu.root")#.Range(1000)
rd = r.Define("Jet_eff", 'alook->getJetEfficiency("Inclusive", "DeepCSV_M", &Jet_hadronFlavour, &Jet_pt, &Jet_eta)')
rd = rd.Define("MET_xycorr_doublet", "METXYCorr_Met_MetPhi(METFixEE2017_pt, METFixEE2017_phi, run, 2017, true, PV_npvs)")
rd = rd.Define("MET_xycorr_pt", "MET_xycorr_doublet.first")
rd = rd.Define("MET_xycorr_phi", "MET_xycorr_doublet.second")
rd = rd.Define("MET_xycorr_pt_shift", "MET_xycorr_pt - METFixEE2017_pt")
rd = rd.Define("MET_xycorr_phi_shift", "abs(MET_xycorr_phi - METFixEE2017_phi)")
s1 = rd.Mean("MET_xycorr_pt_shift")
s11 = rd.Mean("MET_xycorr_phi_shift")

r2 = ROOT.ROOT.RDataFrame("Events", "data_ElMu_B_2017_v2+ElMu.root")#.Range(1000)
rd2 = r2.Define("genWeight", "double y = 1.0; return y;") #fake the genweight for simplicity of test
rd2 = rd2.Define("MET_xycorr_doublet", "METXYCorr_Met_MetPhi(METFixEE2017_pt, METFixEE2017_phi, run, 2017, false, PV_npvs)")
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
hists["MC_phi_uncorr"] = rd.Histo1D(("hphi_uncorr", "", 72, -3.14, 3.14), "METFixEE2017_phi", "genWeight")
hists["MC_phi_corr"] = rd.Histo1D(("hphi_corr", "", 72, -3.14, 3.14), "MET_xycorr_phi", "genWeight")
hists["MC_pt_shift"] = rd.Histo1D(("hpt_shift", "", 100, -10, 10), "MET_xycorr_pt_shift", "genWeight")
hists["MC_phi_shift"] = rd.Histo1D(("hphi_shift", "", 72, -3.14, 3.14), "MET_xycorr_phi_shift", "genWeight")


#Data
#hists["Data_pt"] = rd2.Histo2D(("hdpt", "", 120, 0, 1200, 120, 0, 1200), "METFixEE2017_pt", "MET_xycorr_pt", "genWeight")
#hists["Data_phi"] = rd2.Histo2D(("hdphi", "", 72, -3.14, 3.14, 72, -3.14, 3.14), "METFixEE2017_phi", "MET_xycorr_phi", "genWeight")
hists["Data_phi_uncorr"] = rd2.Histo1D(("hdphi_uncorr", "", 72, -3.14, 3.14), "METFixEE2017_phi", "genWeight")
hists["Data_phi_corr"] = rd2.Histo1D(("hdphi_corr", "", 72, -3.14, 3.14), "MET_xycorr_phi", "genWeight")
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
        if "eff" not in hname:
            hists["{}".format(hname.replace("MC_","Data_"))].SetLineColor(ROOT.kRed)
            hists["{}".format(hname.replace("MC_","Data_"))].DrawNormalized("HIST SAME")
    if "eff" in hname:
        canv[hname].SetLogx()
    canv[hname].Draw()
