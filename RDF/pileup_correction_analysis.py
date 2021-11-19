import ROOT
import pdb
f = ROOT.TFile.Open("~/private/nTruePileup_analysis_mc.root", "read")
names = ["ElEl___nom",
"ElEl___pileupDown",
"ElEl___pileupOff",
"ElEl___pileupUp",
"ElMu___nom",
"ElMu___pileupDown",
"ElMu___pileupOff",
"ElMu___pileupUp",
"GOLDJSON___nom",
"GOLDJSON___pileupDown",
"GOLDJSON___pileupUp",
"MC___nom",
"MuMu___nom",
"MuMu___pileupDown",
"MuMu___pileupOff",
"MuMu___pileupUp",
"OSDL___nom",
"OSDL___pileupDown",
"OSDL___pileupOff",
"OSDL___pileupUp",]

h = dict([(name, f.Get(name)) for name in names])
norms = dict([(name, hist.GetIntegral()) for name, hist in h.items()])

can_name = "OSLD_pileup_corrOff"
c_input = ROOT.TCanvas(can_name)
#This is actually pileupOff... the 'source' distribution that get reweighted to the target GODLJSON___nom or the up/down variations
# h["MC___nom"].SetFillColorAlpha(ROOT.kGray, 0.3)
h["GOLDJSON___nom"].SetLineColor(ROOT.kYellow-2)
h["GOLDJSON___nom"].DrawNormalized("HIST")
h["MC___nom"].SetMarkerColor(ROOT.kWhite)
h["MC___nom"].SetLineColor(ROOT.kWhite)
h["MC___nom"].SetFillColorAlpha(ROOT.kGray, 0.5)
h["MC___nom"].DrawNormalized("SAME")
h["OSDL___pileupOff"].DrawNormalized("HIST SAME")
h["ElEl___pileupOff"].SetLineColor(ROOT.kGreen)
h["ElEl___pileupOff"].SetMarkerColor(ROOT.kGreen)
h["ElEl___pileupOff"].DrawNormalized("PEX1 SAME")
h["ElMu___pileupOff"].SetLineColor(ROOT.kViolet)
h["ElMu___pileupOff"].SetMarkerColor(ROOT.kViolet)
h["ElMu___pileupOff"].DrawNormalized("PEX1 SAME")
h["MuMu___pileupOff"].SetLineColor(ROOT.kRed)
h["MuMu___pileupOff"].SetMarkerColor(ROOT.kRed)
h["MuMu___pileupOff"].DrawNormalized("PEX1 SAME")
h["GOLDJSON___nom"].DrawNormalized("HIST SAME") #Draw again on top... dumb tricks for maximums...
# c_input_label = ROOT.TLatex();
# c_input_label.SetTextSize(0.05)
# c_input_label.DrawLatexNDC(0.1, 0.9, "Post-selection events in analysis versus assumed MC pileup")
c_input.SetTitle("Total OSDL simulation pre-PUReweighting versus assumed nTrueInt; 2018 pileup;")
c_input.Draw()
input_leg = c_input.BuildLegend()
input_leg_list = input_leg.GetListOfPrimitives()
input_leg_list.RemoveLast()
for nx, xx in enumerate(input_leg_list):
  if "ElMu" in xx.GetLabel():
      xx.SetLabel("e#mu reweightOff")
  if "ElEl" in xx.GetLabel():
      xx.SetLabel("ee reweightOff")
  if "MuMu" in xx.GetLabel():
      xx.SetLabel("#mu#mu reweightOff")
  if "OSDL" in xx.GetLabel():
      xx.SetLabel("#mu#mu+e#mu+ee reweightOff")
  if "pileup" == xx.GetLabel():
      xx.SetLabel("GOLDEN JSON")
  if "MC" in xx.GetLabel():
      xx.SetLabel("GEN PU Profile")
c_input.Update()
c_input.SaveAs(can_name+".pdf")

can_name = "OSLD_pileup_corrOn"
c_reweighted = ROOT.TCanvas(can_name)
# stack = ROOT.THStack()
# s1 = h["OSDL___pileupDown"].Clone("OSDL_pileupDown")
# s1.SetFillColor(ROOT.kWhite)
# s1.SetLineColorAlpha(ROOT.kBlue, 0.6)
# stack.Add(s1)
# s2 = h["OSDL___nom"].Clone("OSDL_nominal")
# s2.Add(-1*h["OSDL___pileupDown"])
# s2.SetFillColorAlpha(ROOT.kBlue, 0.4)
# s2.SetLineColorAlpha(ROOT.kBlack, 0.6)
# stack.Add(s2)
# s3 = h["OSDL___pileupUp"].Clone("OSDL_pileupUp")
# s3.Add(-1*h["OSDL___nom"])
# s3.SetFillColorAlpha(ROOT.kRed, 0.4)
# s3.SetLineColorAlpha(ROOT.kRed, 0.6)
# stack.Add(s3)
# total = s2.Integral()

golden_nominal = h["GOLDJSON___nom"].Clone("GOLDJSON_nominal")
# golden_nominal.Scale(total/golden_nominal.Integral())
golden_nominal.SetLineColor(ROOT.kViolet)
golden_nominal.SetMarkerColor(ROOT.kViolet)
golden_nominal.SetTitle("GOLDEN JSON Central")
golden_up = h["GOLDJSON___pileupUp"].Clone("GOLDJSON_pileupUp")
# golden_up.Scale(total/golden_up.Integral())
golden_up.SetLineColor(ROOT.kRed-4)
golden_up.SetMarkerColor(ROOT.kRed-4)
golden_up.SetTitle("GOLDEN JSON Up")
golden_down = h["GOLDJSON___pileupDown"].Clone("GOLDJSON_pileupDown")
# golden_down.Scale(total/golden_down.Integral())
golden_down.SetLineColor(ROOT.kBlue+2)
golden_down.SetMarkerColor(ROOT.kBlue+2)
golden_down.SetTitle("GOLDEN JSON Down")

h["OSDL___pileupDown"].DrawNormalized("HIST")
h["OSDL___nom"].DrawNormalized("HIST SAME")
h["OSDL___pileupUp"].DrawNormalized("HIST SAME")
golden_nominal.DrawNormalized("PEX1 SAME")
golden_up.DrawNormalized("PEX1 SAME")
golden_down.DrawNormalized("PEX1 SAME")


# h["GOLDJSON___nom"].SetLineColor(ROOT.kYellow-2)
# h["GOLDJSON___nom"].DrawNormalized("HIST")
# h["OSDL___nom"].SetLineColor(ROOT.kBlack)
# h["OSDL___nom"].DrawNormalized("HIST SAME")
# h["OSDL___nom"].SetLineColor(ROOT.kBlack)
# h["OSDL___nom"].DrawNormalized("HIST SAME")
# h["GOLDJSON___nom"].DrawNormalized("HIST SAME") #Draw again on top... dumb tricks for maximums...


# c_reweighted_label = ROOT.TLatex();
# c_reweighted_label.SetTextSize(0.05)
# c_reweighted_label.DrawLatexNDC(0.1, 0.9, "Post-selection events in analysis versus assumed MC pileup")
c_reweighted.SetTitle("Total OSDL simulation post-PUReweighting versus data; pileup;")
c_reweighted.Draw()
rew_legend = c_reweighted.BuildLegend()
rew_leg_list = rew_legend.GetListOfPrimitives()
for nx, xx in enumerate(rew_leg_list):
  print(xx.GetLabel())
  if "OSDL" in xx.GetLabel() and "nom" in xx.GetLabel():
      xx.SetLabel("#mu#mu+e#mu+ee reweightCentral")
  if "OSDL" in xx.GetLabel() and "Up" in xx.GetLabel():
      xx.SetLabel("#mu#mu+e#mu+ee reweightUp")
  if "OSDL" in xx.GetLabel() and "Down" in xx.GetLabel():
      xx.SetLabel("#mu#mu+e#mu+ee reweightDown")
  if "GOLDEN" in xx.GetLabel():
      xx.SetOption("p")
c_reweighted.Update()
c_reweighted.SaveAs(can_name+".pdf")


f.Close()
