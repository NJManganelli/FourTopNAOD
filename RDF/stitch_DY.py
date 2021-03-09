import ROOT
import math
f = ROOT.TFile.Open("DYJets_DL.root", "read")
stack = ROOT.THStack()

c = ROOT.TCanvas()
c.SetLogy()
hincl = f.Get("2018___DYJets_DL___effectiveXS___diagnostic___LHE_HT")
h = {}
for ht, color, scale in [(100, ROOT.kRed,0.9765832637382239), (200, ROOT.kBlue, 0.9174941567489592), (400, ROOT.kYellow, 0.8882032424620397), 
                         (600, ROOT.kMagenta, 0.8503393239836625), (800, ROOT.kOrange, 0.9033623269985387), (1200, ROOT.kCyan, 0.9730259911590133), 
                         (2500, ROOT.kGreen, 0.9730259911590133)]: #for 2500+, don't trust 1/scale value of 1.4434248816308983
# for ht, color, scale in [(1200, ROOT.kCyan, 0.9730259911590133), (2500, ROOT.kGreen, 0.9730259911590133)]: #for 2500+, don't trust 1/scale value of 1.4434248816308983
   h[ht] = f.Get("2018___DYJets_DL-HT{ht}___effectiveXS___diagnostic___LHE_HT".format(ht=str(ht)))
   # h[ht].SetMinimum(-5)
   # h[ht].SetMaximum(4)
   h[ht].SetLineColor(0)
   h[ht].SetFillStyle(1001)
   h[ht].SetFillColor(color)
   first = h[ht].FindFirstBinAbove(0.00000001)
   last = h[ht].FindLastBinAbove(0.00000001)
   # for x in range(first, last+1):
   #    h[ht].SetBinContent(x, math.log(h[ht].GetBinContent(x)))
   #    hincl.SetBinContent(x, math.log(hincl.GetBinContent(x)))
   h[ht].Scale(1/scale)
   hincl.GetXaxis().SetRange(first, last)
   print(h[ht].Integral()/hincl.Integral())
   if ht == 100:
      h[ht].Draw("HIST")
   else:
      h[ht].Draw("HIST SAME")
   stack.Add(h[ht])
hincl.GetXaxis().SetRange(0, hincl.GetXaxis().GetNbins()+2)
# stack.Draw("FILL")
hincl.Draw("SAME")
c.Draw()

c2 = ROOT.TCanvas()
hrat = hincl.Clone()
hrat.Divide(stack.GetStack().Last())
hrat.Draw("HIST")
c2.Draw()
