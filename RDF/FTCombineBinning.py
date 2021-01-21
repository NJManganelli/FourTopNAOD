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

def main(stage, analysisDirectory, channel, era, relUncertainty, jsonInput, outDir, sourceVariable = "HT", merged = False, verbose=False):
    varsOfInterest = [sourceVariable + "Unweighted"]
    erasOfInterest = [era]
    channelsOfInterest = [channel]
    samplesOfInterest = ['ttbb_SL_nr', 'ttbb_SL_fr', 'ttbb_SL-GF_fr', 'ttbb_DL_nr', 'ttbb_DL_fr', 'ttbb_DL-GF_fr', #'ttbb_AH'
                         'ttother_SL_nr', 'ttother_SL_fr', 'ttother_SL-GF_fr', 'ttother_DL_nr', 'ttother_DL_fr', 'ttother_DL-GF_fr', #'ttother_AH'
    ]
    if merged:
        histogramFile = "$ADIR/Combine/All/$ERA___MergedChannelsBTags_$VAR.root".replace("$ADIR", analysisDir).replace("$ERA", era).replace("$VAR", sourceVariable).replace("//", "/") # 
        categoriesOfInterest = ['MergedChannelsBTags_nJet4', 'MergedChannelsBTags_nJet5', 'MergedChannelsBTags_nJet6',
                                'MergedChannelsBTags_nJet7', 'MergedChannelsBTags_nJet8+',
        ]
    else:
        categoriesOfInterest = ['HT500_nMediumDeepJetB2_nJet4', 'HT500_nMediumDeepJetB2_nJet5', 'HT500_nMediumDeepJetB2_nJet6',
                                'HT500_nMediumDeepJetB2_nJet7', 'HT500_nMediumDeepJetB2_nJet8+',
                                'HT500_nMediumDeepJetB3_nJet4', 'HT500_nMediumDeepJetB3_nJet5', 'HT500_nMediumDeepJetB3_nJet6',
                                'HT500_nMediumDeepJetB3_nJet7', 'HT500_nMediumDeepJetB3_nJet8+',
                                'HT500_nMediumDeepJetB4+_nJet4', 'HT500_nMediumDeepJetB4+_nJet5', 'HT500_nMediumDeepJetB4+_nJet6',
                                'HT500_nMediumDeepJetB4+_nJet7', 'HT500_nMediumDeepJetB4+_nJet8+',
        ]
        # systematicsOfInterest = [''] #Not needed, only scale systematics get the unweighted histogram in FTAnalyzer.py as of writing
        histogramFile = "$ADIR/Combine/All/$ERA___Combined.root".replace("$ADIR", analysisDir).replace("$ERA", era).replace("$VAR", sourceVariable).replace("//", "/") # 
    f = ROOT.TFile.Open(histogramFile, "read")
    keys = [k.GetName() for k in f.GetListOfKeys()]
    keys = [k for k in keys if k.split("___")[0] in erasOfInterest and k.split("___")[1] in samplesOfInterest]
    keys = [k for k in keys if k.split("___")[2] in channelsOfInterest and k.split("___")[5] in varsOfInterest]
    keys = [k for k in keys if k.split("___")[4] in categoriesOfInterest]
    eras = list(set([k.split("___")[0] for k in keys]))
    samples = list(set([k.split("___")[1] for k in keys]))
    channels = list(set([k.split("___")[2] for k in keys]))
    channelWindows = list(set(["___".join(k.split("___")[2:4]) for k in keys]))
    categories = sorted(sorted(list(set([k.split("___")[4] for k in keys])), key=lambda j : j.split("nJet")[-1]), key=lambda j: j.split("nMediumDeep")[-1])
    variables = list(set([k.split("___")[5] for k in keys]))
    systematics = list(set([k.split("___")[6] for k in keys]))
    if verbose:
        print("Eras: {}".format(eras))
        print("Samples: {}".format(samples))
        print("Channels: {}".format(channels))
        print("Channel + Z Windows: {}".format(channelWindows))
        print("Categories: {}".format(categories))
        print("Variables: {}".format(variables))
        print("Systematics: {}".format(systematics))
    print("Looping...")
    for era in eras:
        if verbose:
            print("\t{}".format(era))
        for channelWindow in channelWindows:
            if verbose:
                print("\t\t{}".format(channelWindow))
            if jsonInput:
                jsonInputPath = jsonInput.replace("$ERA", era).replace("$CHANNEL", channel)
                jsonOutputPath = os.path.join(outDir, jsonInput.split("/")[-1].replace("$ERA", era).replace("$CHANNEL", channel))
                jsonCopy = None
                with open(jsonInputPath, "r") as jI:
                    jsonCopy = copy.copy(json.load(jI))
            for category in categories:
                if verbose:
                    print("\t\t\t{}".format(category))
                for variable in variables:
                    if verbose:
                        print("\t\t\t\t{}".format(variable))
                    hists = {}
                    rebinnedHists = {}
                    nBinsX = 0
                    if variable != "HTUnweighted":
                        continue
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
                                if thisKey in keys:
                                    hists[systematic].Add(f.Get(thisKey))
                                else:
                                    raise RuntimeError("Key not found: {}".format(thisKey))                                    
                    #Have all the systematic variations that are relevant and adding the histograms together; create empty numpy array
                    entryArray = np.zeros((len(systematics), nBinsX+2), dtype=np.int32)
                    # binningArray.append(0) #Can't rebin the overflow anyway... thanks ROOT
                    for nsyst, systematic in enumerate(systematics):
                        for nbin in range(0, hists[systematic].GetNbinsX()+2): #Include underflow and overflow for bin numbering clarity                            
                            entryArray[nsyst, nbin] = hists[systematic].GetBinContent(nbin)
                    start = 1 #Don't include underflow
                    stop = start + 1 #Initialize so that we start with checking the singular bin
                    end = nBinsX + 1 #Include the overflow bin so we still attain its low edge without special logic
                    binningArray = []
                    binningArray.append(start)
                    with np.errstate(divide='ignore'):
                        while(stop <= end): #Need quality to end to append the end as a stop in the array
                            while(np.any(1/np.sqrt(np.sum(entryArray[:, start:stop], axis=1)) > relUncertainty)):
                                stop += 1
                                #After the while loop, we should have a good start:stop range for rebinning, unless it failed for the last bin, so merge (start:end)! range
                                if stop > end:
                                    if np.any(1/np.sqrt(entryArray[:, start:end].sum(axis=1)) > relUncertainty):
                                        if len(binningArray) > 1:
                                            #Merge with the previous bin by replacement of the last deduced stop with end
                                            binningArray[-1] = end
                                        else:
                                            #Array has only the histogram lowest edge, looks like we've got a one-bin pony show!
                                            binningArray.append(end)
                                        break
                                    else:
                                        raise RuntimeError("Unhandled logical path")
                            if verbose:
                                print("start: {}    stop: {}     end: {}".format(start, stop, end))
                            #Continue handling the stop > end break from the inner while loop
                            if stop > end:
                                break
                            #Append the stop and increment the start and stop
                            binningArray.append(stop)
                            start = copy.copy(stop)
                            stop = copy.copy(start) + 1
                        if verbose: 
                            print("Binning Array: {}".format(binningArray))
                            print("Numpy Entry Array: {}".format(entryArray))
                    rebinningEdges = []
                    for binNumber in binningArray:
                        rebinningEdges.append(list(hists.values())[0].GetBinLowEdge(binNumber))
                    edgesArray = array.array('d', rebinningEdges)
                    for systematic in systematics:
                        rebinnedHists[systematic] = hists[systematic].Rebin(len(edgesArray)-1, hists[systematic].GetName() + "_rebin", edgesArray)
                        # for binNumber in range(1, rebinnedHists[systematic].GetNbinsX()+1):
                        #     assert rebinnedHists[systematic].GetBinError(binNumber)/rebinnedHists[systematic].GetBinContent(binNumber) <= relUncertainty, "Rebinning not below threshold in the rebinned hist for '{}' systematic, bin {}, range {} - {}".format(systematic, binNumber, rebinnedHists[systematic].GetBinLowEdge(binNumber), rebinnedHists[systematic].GetBinLowEdge(binNumber) + rebinnedHists[systematic].GetBinWidth(binNumber))
                replacements = []
                if jsonInput:
                    for jkey, jdict in jsonCopy.items():
                        if category in jkey and variable.replace("Unweighted", "") in jkey:
                            if verbose:
                                print("Input array: ", jdict.get("Rebin"), "\nOutput array: ", rebinningEdges)
                            jdict["Rebin"] = rebinningEdges
                            replacements.append(jkey)
                    if len(replacements) > 1:
                        print("Potential error: [{era}][{cat}][{var}] rebin array used as replacement in following items: {keys}".format(era=era, cat=category, var=variable, keys=replacements))
                else:
                    print(era, channel, category)
                    print('        "Rebin":', rebinningEdges, ',')
            if jsonInput:                
                print("Writing output json to: {}".format(jsonOutputPath))
                with open(jsonOutputPath, "w") as jo:
                    jo.write(json.dumps(jsonCopy, indent=4))
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Determine binning automatically for categorized histograms using a particular subset of processes')
    parser.add_argument('stage', action='store', type=str, choices=['determine-binning'],
                        help='analysis stage to be produced')
    parser.add_argument('--analysisDirectory', dest='analysisDirectory', action='store', type=str, default="/eos/user/$U/$USER/analysis/$DATE",
                        help='output directory path defaulting to "."')
    parser.add_argument('--channel', dest='channel', action='store', type=str, default="ElMu", choices=['ElMu', 'ElEl', 'MuMu', 'All'],
                        help='Decay channel for opposite-sign dilepton analysis, All for use with merged legends cards')
    parser.add_argument('--era', dest='era', type=str, default="2017",
                        help='era for plotting, which deduces the lumi only for now')
    parser.add_argument('--variable', dest='variable', action='store', default="HT", type=str,
                        help='Variable of interest to do rebinning on, must have an Unweighted version called <variable>Unweighted, e.g. HT --> HTUnweighted')
    parser.add_argument('--relUncertainty', dest='relUncertainty', action='store', type=float, default=0.3,
                        help='maximum relative uncertainty (sqrt(N)/N) per bin used as the criteria for merging')
    parser.add_argument('--include', dest='include', action='store', default=None, type=str, nargs='*',
                        help='List of sample names to be used in the stage (if not called, defaults to all; takes precedene over exclude)')
    parser.add_argument('--exclude', dest='exclude', action='store', default=None, type=str, nargs='*',
                        help='List of sample names to not be used in the stage (if not called, defaults to none; include takes precedence)')
    parser.add_argument('--json', '-j', dest='json', action='store', default=None, type=str,
                        help='path to json file plotcard to overwrite "Rebin" categories with those determined here. Output determined by --out argument')
    parser.add_argument('--merged', dest='merged', action='store_true',
                        help='Check for the $ERA___MergedChannelsBTags_$VAR.root file in the Combine/All subdirectory, a product of FTMergeChannelsBTags.py for systematic studies')
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
    main(stage, analysisDir, channel, args.era, args.relUncertainty, args.json, ".", args.variable, args.merged, verbose=verbose)
