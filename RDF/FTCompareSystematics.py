from __future__ import print_function, division
import os
import time
import pwd
import datetime
import collections
import pprint
import math
import array
import json
import copy
import argparse
import uuid
import pdb
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

ROOT.gROOT.SetBatch(True)

def main(stage, analysisDirectory, channel, era, includeSystematics=None, excludeSystematics=None, skipSamples=None, verbose=False):
    varsOfInterest = ["HT"]
    erasOfInterest = [era]
    channelsOfInterest = [channel]
    categoriesOfInterest = ['HT500_nMediumDeepJetB2_nJet4', 'HT500_nMediumDeepJetB2_nJet5', 'HT500_nMediumDeepJetB2_nJet6',
                            'HT500_nMediumDeepJetB2_nJet7', 'HT500_nMediumDeepJetB2_nJet8p',
                            'HT500_nMediumDeepJetB3_nJet4', 'HT500_nMediumDeepJetB3_nJet5', 'HT500_nMediumDeepJetB3_nJet6',
                            'HT500_nMediumDeepJetB3_nJet7', 'HT500_nMediumDeepJetB3_nJet8p',
                            'HT500_nMediumDeepJetB4p_nJet4', 'HT500_nMediumDeepJetB4p_nJet5', 'HT500_nMediumDeepJetB4p_nJet6',
                            'HT500_nMediumDeepJetB4p_nJet7', 'HT500_nMediumDeepJetB4p_nJet8p',
    ]
    # categoriesOfInterest = ['HT500_nMediumDeepJetB2_nJet4', 'HT500_nMediumDeepJetB3_nJet6', 'HT500_nMediumDeepJetB4+_nJet8+',
    # ]
    # categoriesOfInterest = ['HT500_nMediumDeepJetB2_nJet4',
    # ]

    # systematicsOfInterest = [''] #Not needed, only scale systematics get the unweighted histogram in FTAnalyzer.py as of writing
    histogramFile = "$ADIR/Combine/CI_$ERA_$CHANNEL_$VAR.root".replace("$ADIR", analysisDir).replace("$ERA", era).replace("$CHANNEL", channel).replace("$VAR", varsOfInterest[0]).replace("//", "/") # 
    f = ROOT.TFile.Open(histogramFile, "read")
    keys = [k.GetName() for k in f.GetListOfKeys()]
    if len(keys[0].split("___")) == 7: #format post-fill-(histograms/combine)
        eras = sorted(list(set([k.split("___")[0] for k in keys])))
        samples = sorted(list(set([k.split("___")[1] for k in keys])))
        channels = sorted(list(set([k.split("___")[2] for k in keys])))
        channelWindows = list(set(["___".join(k.split("___")[2:4]) for k in keys]))
        categories = sorted(sorted(list(set([k.split("___")[4] for k in keys])), key=lambda j : j.split("nJet")[-1]), key=lambda j: j.split("nMediumDeep")[-1])
        variables = list(set([k.split("___")[5] for k in keys]))
        systematics = list(set([k.split("___")[6] for k in keys]))
    elif len(keys[0].split("___")) == 4: #combine-input format
        # eras = sorted(list(set([k.split("___")[0] for k in keys])))
        eras = erasOfInterest
        samples = sorted(list(set([k.split("___")[0] for k in keys])))
        # channels = sorted(list(set([k.split("___")[2] for k in keys])))
        # channelWindows = list(set(["___".join(k.split("___")[2:4]) for k in keys]))
        channels = None
        channelWindows = None
        categories = sorted(sorted(list(set([k.split("___")[1] for k in keys])), key=lambda j : j.split("nJet")[-1]), key=lambda j: j.split("nMediumDeep")[-1])
        variables = list(set([k.split("___")[2] for k in keys]))
        systematics = list(set([k.split("___")[3] for k in keys]))
    else:
        raise RuntimeError("Unhandled histogram key format: length: {} key: {}".format(len(keys[0].split("___")), keys[0]))

    supportedTypes = (ROOT.TH1, ROOT.TH2, ROOT.TH3)

    if verbose:
        print("Eras: {}".format(eras))
        print("Samples: {}".format(samples))
        print("Channels: {}".format(channels))
        print("Channel + Z Windows: {}".format(channelWindows))
        print("Categories: {}".format(categories))
        print("Variables: {}".format(variables))
    print("Systematics: {}".format(systematics))
    print("Looping...")
    if len(keys[0].split("___")) == 7: #format post-fill-(histograms/combine)
        for era in eras:
            print("\t{}".format(era))
            for channelWindow in channelWindows:
                print("\t\t{}".format(channelWindow))
                for category in categories:
                    print("\t\t\t{}".format(category))
                    for variable in variables:
                        print("\t\t\t\t{}".format(variable))
                        hists = {}
                        for systematic in systematics:
                            if verbose: print(systematic)
                            for nSample, sample in enumerate(samples):
                                thisKey = "___".join([era, sample, channelWindow, category, variable, systematic])
                                if nSample == 0:                                
                                    if thisKey in keys:
                                        hists[systematic] = f.Get(thisKey).Clone()
                                        hists[systematic].SetDirectory(0)
                                        nBinsX = hists[systematic].GetNbinsX()
                                    else:
                                        raise RuntimeError("Key not found: {}".format(thisKey))
                                else:
                                    hists[systematic].Add(f.Get(thisKey))
    elif len(keys[0].split("___")) == 4: #format for combine input
        can = ROOT.TCanvas()
        drawCounter = 0
        hist = {}
        histUp = {}
        histDown = {}
        histRU = {}
        histRD = {} #Down ratio histograms
        pdfOut = "{era}_{chan}_Systematics.pdf".format(era=era, chan=channel)
        for category in categories:
            if category not in categoriesOfInterest:
                print("Skipping category {}".format(category))
                continue
            print("\t\t\t{}".format(category))
            hist[category] = {}
            histUp[category] = {}
            histDown[category] = {}
            histRU[category] = {}
            histRD[category] = {}
            for variable in variables:
                print("\t\t\t\t{}".format(variable))
                hist[category][variable] = {}
                histUp[category][variable] = {}
                histDown[category][variable] = {}
                histRU[category][variable] = {}
                histRD[category][variable] = {}
                for nSample, sample in enumerate(samples):
                    if skipSamples and sample in skipSamples:
                        print("Skipping sample {}".format(sample))
                        continue
                    print("\t\t\t\t\t{}".format(sample))
                    histUp[category][variable][sample] = {}
                    histDown[category][variable][sample] = {}
                    histRU[category][variable][sample] = {}
                    histRD[category][variable][sample] = {}
                    # thisSampleSystematics = []
                    thisSampleSystematics = list(set([k.split("___")[3] for k in keys if k.split("___")[0] == sample]))
                    print(sample, thisSampleSystematics)
                    maxes = []
                    mins = []
                    # for systematic in systematics:
                    for systematic in thisSampleSystematics:
                        if verbose: print(systematic)
                        if "Up" == systematic[-2:]:
                            thisSyst = systematic[:-2]
                            # thisSampleSystematics.append(thisSyst)
                        elif "Down" == systematic[-4:]:
                            thisSyst = systematic[:-4]
                            # thisSampleSystematics.append(thisSyst)
                        else:
                            thisSyst = "nom"
                        thisKey = "___".join([sample, category, variable, systematic])
                        if includeSystematics and thisSyst not in includeSystematics + ["nom"]:
                            print("Skipping systematic {}".format(thisSyst))
                            continue
                        elif excludeSystematics and thisSyst in excludeSystematics:
                            print("Skipping systematic {}".format(thisSyst))
                            continue
                        if "Up" == systematic[-2:]:
                            histUp[category][variable][sample][thisSyst] = f.Get(thisKey)
                            if isinstance(histUp[category][variable][sample][thisSyst], supportedTypes):
                                histUp[category][variable][sample][thisSyst] = histUp[category][variable][sample][thisSyst].Clone()
                                histUp[category][variable][sample][thisSyst].SetDirectory(0)
                                histUp[category][variable][sample][thisSyst].SetFillColor(0)
                                histUp[category][variable][sample][thisSyst].SetLineColor(ROOT.kRed)
                                histRU[category][variable][sample][thisSyst] = histUp[category][variable][sample][thisSyst].Clone(
                                    histUp[category][variable][sample][thisSyst].GetName() + "_ratio"
                                )
                                maxes.append(histUp[category][variable][sample][thisSyst].GetMaximum())
                                mins.append(histUp[category][variable][sample][thisSyst].GetMinimum())
                            else:
                                print("no Up")
                        elif "Down" == systematic[-4:]:
                            histDown[category][variable][sample][thisSyst] = f.Get(thisKey)
                            if isinstance(histDown[category][variable][sample][thisSyst], supportedTypes):
                                histDown[category][variable][sample][thisSyst] = histDown[category][variable][sample][thisSyst].Clone()
                                histDown[category][variable][sample][thisSyst].SetDirectory(0)
                                histDown[category][variable][sample][thisSyst].SetFillColor(0)
                                histDown[category][variable][sample][thisSyst].SetLineColor(ROOT.kBlue)
                                histRD[category][variable][sample][thisSyst] = histDown[category][variable][sample][thisSyst].Clone(
                                    histDown[category][variable][sample][thisSyst].GetName() + "_ratio"
                                )
                                maxes.append(histDown[category][variable][sample][thisSyst].GetMaximum())
                                mins.append(histDown[category][variable][sample][thisSyst].GetMinimum())
                            else:
                                print("no Down")
                        else:
                            hist[category][variable][sample] = f.Get(thisKey)
                            if isinstance(hist[category][variable][sample], supportedTypes):
                                hist[category][variable][sample] = hist[category][variable][sample].Clone()
                                hist[category][variable][sample].SetDirectory(0)
                                hist[category][variable][sample].SetFillColor(0)
                                hist[category][variable][sample].SetLineColor(ROOT.kBlack)
                                maxes.append(hist[category][variable][sample].GetMaximum())
                                mins.append(hist[category][variable][sample].GetMinimum())
                            else:
                                print("no nominal")
                    thisMin = min(mins)
                    thisMax = max(maxes)
                    # thisSampleSystematics = sorted(list(set(thisSampleSystematics)))
                    for syst in histUp[category][variable][sample].keys():
                        oldtitle = hist[category][variable][sample].GetTitle()
                        hist[category][variable][sample].SetTitle("{} {}({})[{}];{};Events/bin(variable)".format(sample, variable, category, syst, variable))
                        print("{}: {} - up: {} down: {}".format(hist[category][variable][sample].GetTitle(),
                            hist[category][variable][sample].Integral(),
                            histUp[category][variable][sample][syst].Integral(),
                            histDown[category][variable][sample][syst].Integral()
                                                        ))
                        hist[category][variable][sample].SetMinimum(0.9 * thisMin)
                        hist[category][variable][sample].SetMaximum(1.1 * thisMax)
                        hist[category][variable][sample].Draw("HIST S")
                        histUp[category][variable][sample][syst].Draw("HIST SAMES E")
                        histDown[category][variable][sample][syst].Draw("HIST SAMES E")
                        can.Draw()
                        up_stats = histUp[category][variable][sample][syst].GetListOfFunctions().FindObject("stats")
                        up_stats.SetX1NDC(.7)
                        up_stats.SetX2NDC(.9)
                        # histUp[category][variable][sample][syst].GetListOfFunctions().FindObject("stats").SetX2NDC(.9)
                        nom_stats = hist[category][variable][sample].GetListOfFunctions().FindObject("stats")
                        nom_stats.SetX1NDC(.5)
                        nom_stats.SetX2NDC(.7)
                        # hist[category][variable][sample].GetListOfFunctions().FindObject("stats").SetX2NDC(.7)
                        dn_stats = histDown[category][variable][sample][syst].GetListOfFunctions().FindObject("stats")
                        dn_stats.SetX1NDC(.3)
                        dn_stats.SetX2NDC(.5)
                        # histDown[category][variable][sample][syst].GetListOfFunctions().FindObject("stats").SetX1NDC(.5)
                        can.Update()
                        if drawCounter == 0:
                            can.SaveAs(pdfOut + "(")
                        else:
                            can.SaveAs(pdfOut)
                        histRU[category][variable][sample][syst].Divide(hist[category][variable][sample])
                        histRD[category][variable][sample][syst].Divide(hist[category][variable][sample])
                        histRU[category][variable][sample][syst].SetMinimum(0.5)
                        histRU[category][variable][sample][syst].SetMaximum(1.5)
                        histRU[category][variable][sample][syst].Draw("HIST")
                        histRD[category][variable][sample][syst].Draw("HIST SAME")
                        can.Draw()
                        can.SaveAs(pdfOut)
                        drawCounter += 1
                        hist[category][variable][sample].SetTitle(oldtitle)
        can2 = ROOT.TCanvas()
        can2.SaveAs(pdfOut + ")")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Determine binning automatically for categorized histograms using a particular subset of processes')
    parser.add_argument('stage', action='store', type=str, choices=['plot-systematics'],
                        help='analysis stage to be produced')
    parser.add_argument('--analysisDirectory', dest='analysisDirectory', action='store', type=str, default="/eos/user/$U/$USER/analysis/$DATE",
                        help='output directory path defaulting to "."')
    parser.add_argument('--channel', dest='channel', action='store', type=str, default="ElMu", choices=['ElMu', 'ElEl', 'MuMu'],
                        help='Decay channel for opposite-sign dilepton analysis')
    parser.add_argument('--era', dest='era', type=str, default="2017",
                        help='era for plotting, which deduces the lumi only for now')
    parser.add_argument('--includeSystematics', dest='includeSystematics', action='store', default=None, type=str, nargs='*',
                        help='List of systematic names to be considered when setting common miminma/maxima and plotting')
    parser.add_argument('--excludeSystematics', dest='excludeSystematics', action='store', default=None, type=str, nargs='*',
                        help='List of systematic names to be ignored when setting common miminma/maxima and plotting')
    parser.add_argument('--skipSamples', dest='skipSamples', action='store', default=None, type=str, nargs='*',
                        help='List of sample names to be ignored when setting common miminma/maxima and plotting')
    parser.add_argument('--include', dest='include', action='store', default=None, type=str, nargs='*',
                        help='List of sample names to be used in the stage (if not called, defaults to all; takes precedene over exclude)')
    parser.add_argument('--exclude', dest='exclude', action='store', default=None, type=str, nargs='*',
                        help='List of sample names to not be used in the stage (if not called, defaults to none; include takes precedence)')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')
    # parser.add_argument('--era', dest='era', action='store', type=str, default="2017", choices=['2016', '2017', '2018'],
    #                     help='simulation/run year')
    # parser.add_argument('--nThreads', dest='nThreads', action='store', type=int, default=8, #nargs='?', const=0.4,
    #                     help='number of threads for implicit multithreading (0 or 1 to disable)')
    #nargs='+' #this option requires a minimum of arguments, and all arguments are added to a list. '*' but minimum of 1 argument instead of none

    #Parse the arguments
    args = parser.parse_args()
    uname = pwd.getpwuid(os.getuid()).pw_name
    uinitial = uname[0]
    dateToday = datetime.date.today().strftime("%b-%d-%Y")
    stage = args.stage
    channel = args.channel
    analysisDir = args.analysisDirectory.replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday).replace("$CHAN", channel)
    verbose = args.verbose
    main(stage, analysisDir, channel, args.era, includeSystematics = args.includeSystematics, excludeSystematics = args.excludeSystematics, skipSamples = args.skipSamples, verbose=verbose)
