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
r = ROOT.ROOT.RDataFrame("Events", "tt_DL-GF-1_2017_v2+ElMu.root")
rd = r.Range(5).Define("Jet_eff", 'alook->getJetEfficiency("Inclusive", "DeepCSV_M", &Jet_hadronFlavour, &Jet_pt, &Jet_eta)')
n = rd.AsNumpy("Jet_eff")
print(n)
h = rd.Histo1D(("hr", "", 100, 0, 1), "Jet_eff", "genWeight")
c = ROOT.TCanvas("c", "", 800, 600)
c.SetLogx()
h.Draw("HIST")
c.Draw()
