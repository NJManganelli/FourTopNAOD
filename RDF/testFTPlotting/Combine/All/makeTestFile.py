import ROOT
import math
from tqdm import tqdm
#Want to study the systematics with enveloping (two that have a crossover point, three that don't)
#addInQuadrature: 4 templates
#two backgrounds and one signal, plus data sampled from the sum
#4 bins total
#Need the final hand-calculated result for checking that FTPlotting.py is combining them correctly

rng = ROOT.TRandom3()
f = ROOT.TFile.Open("2018___testFile.root", "recreate")
#names of processes BackgroundA1, BackgroundA2, BackgroundB1, SignalA1, Data1
#grouped into BackgroundA, BackgroundB --> Background, SignalA --> Signal, Data --> Data
h = dict()
names = {"BackgroundA1": ["nom", "envA1_1", "envA1_2", "envA1VerifyUp", "envA1VerifyDown"], 
         "BackgroundA2":["nom", "envA2_1", "envA2_2", "envA2VerifyUp", "envA2VerifyDown"], 
         "BackgroundB1":["nom", "envB1_1", "envB1_2", "envB1_3", "envB1VerifyUp", "envB1VerifyDown"], 
         "SignalA1":["nom", "quadS1_1", "quadS1_2", "quadS1_3", "quadS1_4", "quadS1_5", "quadS1_6", "quadS1VerifyUp", "quadS1VerifyDown"], 
         "Data1":["nom"]
     }
for name, systs in names.items():
    nbins = 5
    for syst in systs:
        h[name + "___" + syst] = ROOT.TH1D("2018___"+name+"___ElMu___ZWindowMET0Width0___HT500_nMediumDeepJetB0_nJet4___HT"+"___"+syst, name+"___"+syst, nbins, 0, 5)



mean = 2
sigma = 0.5
gamma = 1
tau = 1.3


for x in tqdm(range(10000)):
    syst = "nom"
    h["BackgroundA1"+"___"+syst].Fill(rng.Gaus(mean, sigma), rng.Gaus(0.1, 0.03))
    h["BackgroundA2"+"___"+syst].Fill(rng.Gaus(2*mean, sigma/2), rng.Gaus(0.1, 0.03))
    h["BackgroundB1"+"___"+syst].Fill(rng.Exp(tau), rng.Gaus(0.1, 0.03))
    h["SignalA1"+"___"+syst].Fill(rng.BreitWigner(mean, gamma), rng.Gaus(0.1, 0.03))

stack = ROOT.THStack()
stack.Add(h["BackgroundA1"+"___"+syst])
stack.Add(h["BackgroundA2"+"___"+syst])
stack.Add(h["BackgroundB1"+"___"+syst])
stack.Add(h["SignalA1"+"___"+syst])
stackLast = stack.GetStack().Last()

for name, systs in names.items():
    nbins = 5
    for syst in systs:
        if "BackgroundA1" in name:
            h[name + "___" + syst].SetLineColor(ROOT.kRed-1)
            # MC: 10000 entries with weight distributed about 0.1 (gaussian)
            # Supercategory:Background
            # BackgroundA
            # gaussian
            # Sum of two gaussians, BackgroundA1, BackgroundA2
            # systematic envelope with two crossover uncertainties of 2% each, result should be VerifyUp:2%, VerifyDown:2%
            for bin in range(nbins+2):
                print(name+" is being cycled over for systematics")
                if syst == "envA1_1":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * (1.02 if bin > nbins/2 else 0.98))
                elif syst == "envA1_2":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * (1.02 if bin < nbins/2 else 0.98))
                elif syst == "envA1VerifyUp":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * 1.02)
                elif syst == "envA1VerifyDown":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * 0.98)
        elif "BackgroundA2" in name:
            h[name + "___" + syst].SetLineColor(ROOT.kRed+2)
            for bin in range(nbins+2):
                if syst == "envA2_1":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * (1.02 if bin > nbins/2 else 0.98))
                elif syst == "envA2_2":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * (1.02 if bin < nbins/2 else 0.98))
                elif syst == "envA2VerifyUp":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * 1.02)
                elif syst == "envA2VerifyDown":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * 0.98)
        elif "BackgroundB" in name:
            h[name + "___" + syst].SetLineColor(ROOT.kBlue)
            # BackgroundB
            # exponential
            # single exponential, BackgroundB1
            # systematic envelope with 3 uncertainties of varying amounts, result should be VerifyUp:4/4/4/4/4%, VerifyDown:-1/0/0/0/-1% and 0 in flow bins
            b1 =    [0, 1.01, 1.02, 1.03, 1.04, 1.04, 0]
            b2 =    [0, 0.99, 1.04, 1.00, 1.00, 1.01, 0]
            b3 =    [0, 1.04, 1.00, 1.04, 1.01, 0.99, 0]            
            bVerifyUp =   [0, 1.04, 1.04, 1.04, 1.04, 1.04, 0]
            bVerifyDown = [0, 0.99, 1.00, 1.00, 1.00, 0.99, 0]
            for bin in range(nbins+2):
                if syst == "envB1_1":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * b1[bin])
                elif syst == "envB1_2":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * b2[bin])
                elif syst == "envB1_3":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * b3[bin])
                elif syst == "envB1VerifyUp":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * bVerifyUp[bin])
                elif syst == "envB1VerifyDown":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * bVerifyDown[bin])
        elif "Signal" in name:
            h[name + "___" + syst].SetLineColor(ROOT.kGreen)
            # Signal
            # uniform
            # single Signal1
            # systematic addInQuadrature, with +3%, +4%, +5%, -.3%, -.4%, -.5%
            for bin in range(nbins+2):
                if syst == "quadS1_1":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * 1.03)
                elif syst == "quadS1_2":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * 1.04)
                elif syst == "quadS1_3":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * 1.05)
                elif syst == "quadS1_4":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * (1 - 0.003))
                elif syst == "quadS1_5":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * (1 - 0.004))
                elif syst == "quadS1_6":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * (1 - 0.005))
                elif syst == "quadS1VerifyUp":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * (1 + math.sqrt(0.03**2 + 0.04**2 + 0.05**2)))
                elif syst == "quadS1VerifyDown":
                    h[name + "___" + syst].SetBinContent(bin, h[name + "___" + "nom"].GetBinContent(bin) * (1 - math.sqrt(0.003**2 + 0.004**2 + 0.005**2)))
        elif "Data" in name:
            h[name + "___" + syst].FillRandom(stackLast, 1000)


# can = ROOT.TCanvas()
drawn = False
for name, hist in h.items():
    print(name)
    hist.Write()
    if True:
    # if "nom" in name:
        print([hist.GetBinContent(bin) for bin in range(hist.GetNbinsX() + 2)])
#         if drawn:
#             hist.Draw("HIST SAME")
#         else:
#             hist.Draw("HIST")
#             drawn = True
# can.Draw()

f.Close()
