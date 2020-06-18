import ROOT
import array
x = array.array('d', [500, 700, 900, 1200])
y = array.array('d', [2, 4, 6])
r = ROOT.ROOT.RDataFrame("Events", "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_DL-GF*.root").Range(100).Define("HT", "Sum(Jet_pt)")
m = ROOT.RDF.TH2DModel("test", "test; x; y", len(x)-1, x, len(y)-1, y)
h = r.Histo2D(m, "HT", "nMuon", "genWeight")
c = ROOT.TCanvas()
h.Draw("COLZ TEXT")
c.Draw()
