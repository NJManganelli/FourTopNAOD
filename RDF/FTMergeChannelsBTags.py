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

def main(analysisDirectory, era, variable, verbose=False):
    categoriesOfInterest = ['HT500_nMediumDeepJetB2_nJet4', 'HT500_nMediumDeepJetB2_nJet5', 'HT500_nMediumDeepJetB2_nJet6',
                            'HT500_nMediumDeepJetB2_nJet7', 'HT500_nMediumDeepJetB2_nJet8p',
                            'HT500_nMediumDeepJetB3_nJet4', 'HT500_nMediumDeepJetB3_nJet5', 'HT500_nMediumDeepJetB3_nJet6',
                            'HT500_nMediumDeepJetB3_nJet7', 'HT500_nMediumDeepJetB3_nJet8p',
                            'HT500_nMediumDeepJetB4p_nJet4', 'HT500_nMediumDeepJetB4p_nJet5', 'HT500_nMediumDeepJetB4p_nJet6',
                            'HT500_nMediumDeepJetB4p_nJet7', 'HT500_nMediumDeepJetB4p_nJet8p',
    ]
    histogramFile = "$ADIR/Combine/All/$ERA___Combined.root".replace("$ADIR", analysisDir).replace("$ERA", era).replace("//", "/") 
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


    merge = dict()
    for mera in eras:
        merge[mera] = dict()
        for msample in samples:
            merge[mera][msample] = dict()
            for mvariable in variables:
                if mvariable not in [variable, variable + "Unweighted"]:
                    continue
                merge[mera][msample][mvariable] = dict()
                for msyst in systematics:
                    merge[mera][msample][mvariable][msyst] = dict()
                    for mcategory in ["nJet4", "nJet5", "nJet6", "nJet7", "nJet8p"]:
                        merge[mera][msample][mvariable][msyst][mcategory] = []

    for key in keys:
        mera, msample, mchannel, mwindow, mcategory, mvariable, msyst = key.split("___")
        if mvariable not in [variable, variable + "Unweighted"] or mera != era:
            continue
        mcat = mcategory.split("_")[-1].replace("+", "p").replace("BLIND", "")
        merge[mera][msample][mvariable][msyst][mcat].append(key)
    
    outputHistogramFile = histogramFile.replace("Combined", "").replace(".root", "MergedChannelsBTags_" + variable + ".root")
    print("Opening {}".format(outputHistogramFile))
    of = ROOT.TFile.Open(outputHistogramFile, "recreate")
    of.cd()
    for mera, submerge in merge.items():
        for msample, subsubmerge in submerge.items():
            print("Writing results for {}".format(msample))
            for mvariable, subsubsubmerge in subsubmerge.items():
                for msyst, subsubsubsubmerge in subsubsubmerge.items():
                    print("*", end="")
                    for mcat, subsubsubsubsubmerge in subsubsubsubmerge.items():
                        mergeName = "___".join([mera, msample, "All", "ZWindow", "MergedChannelsBTags_" + mcat, mvariable, msyst])
                        hist = None
                        blind = len([hk for hk in subsubsubsubsubmerge if "blind" in hk.lower()]) > 0
                        for histKey in subsubsubsubsubmerge:
                            rootobj = f.Get(histKey)
                            if isinstance(rootobj, supportedTypes):
                                if hist is None:
                                    hist = rootobj.Clone(mergeName)
                                else:
                                    hist.Add(rootobj)
                        if blind:
                            for bin in range(hist.GetNbinsX() + 2):
                                hist.SetBinContent(bin, 0)
                                hist.SetBinError(bin, 0)
                        if hist is not None:
                            hist.Write()
                print("")
    f.Close()
    of.Close()
    print("Done")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Determine binning automatically for categorized histograms using a particular subset of processes')
    parser.add_argument('--analysisDirectory', dest='analysisDirectory', action='store', type=str, default="/eos/user/$U/$USER/analysis/$DATE", required=True,
                        help='output directory path defaulting to "."')
    parser.add_argument('--era', dest='era', type=str, default="2017", required=True,
                        help='era for plotting, which deduces the lumi only for now')
    parser.add_argument('--variable', dest='variable', type=str, default="HT", required=True,
                        help='Variable to be merged across channels and BTag categories')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')

    #Parse the arguments
    args = parser.parse_args()
    uname = pwd.getpwuid(os.getuid()).pw_name
    uinitial = uname[0]
    dateToday = datetime.date.today().strftime("%b-%d-%Y")
    analysisDir = args.analysisDirectory.replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday)
    verbose = args.verbose
    main(analysisDir, era=args.era, variable=args.variable, verbose=verbose)
