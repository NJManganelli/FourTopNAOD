import ROOT
r = ROOT.ROOT.RDataFrame("Events", "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tt_DL-GF*.root").Range(100)
rd = r.Define("nGoodMuon", "(int)Muon_pt[Muon_pt > 15 && abs(Muon_eta) < 2.5 && Muon_looseId].size()") #works
# rd = r.Define("nGoodMuon", "Muon_pt[Muon_pt > 15 && abs(Muon_eta) < 2.5 && Muon_looseId].size()") #Not good
rd = rd.Define("GoodMuon_pt", "Muon_pt[Muon_pt > 15 && abs(Muon_eta) < 2.5 && Muon_looseId]")
rd = rd.Define("GoodMuon_eta", "Muon_eta[Muon_pt > 15 && abs(Muon_eta) < 2.5 && Muon_looseId]")
rd = rd.Define("GoodMuon_phi", "Muon_phi[Muon_pt > 15 && abs(Muon_eta) < 2.5 && Muon_looseId]")
print(rd.Count().GetValue())
v = ROOT.std.vector(str)(4); v[0]="nGoodMuon";v[1]="GoodMuon_pt";v[2]="GoodMuon_eta";v[3]="GoodMuon_phi"
# s = rd.Snapshot("Events", "test_snap.root", v) #works
s = rd.Snapshot("Events", "test_snap.root")
