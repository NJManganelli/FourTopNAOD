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

def main(stage, analysisDirectory, channel, era, relUncertainty):
    varsOfInterest = ["HTUnweighted"]
    erasOfInterest = [era]
    channelsOfInterest = [channel]
    samplesOfInterest = ['ttbb_SL_nr', 'ttbb_SL_fr', 'ttbb_SL-GF_fr', 'ttbb_DL_nr', 'ttbb_DL_fr', 'ttbb_DL-GF_fr', 
                         'ttother_SL_nr', 'ttother_SL_fr', 'ttother_SL-GF_fr', 'ttother_DL_nr', 'ttother_DL_fr', 'ttother_DL-GF_fr',]
    # systematicsOfInterest = [''] #Not needed, only scale systematics get the unweighted histogram in FTAnalyzer.py as of writing
    histogramFile = "$ADIR/Combine/All/$ERA___Combined.root".replace("$ADIR", analysisDir).replace("$ERA", era).replace("//", "/") # 
    f = ROOT.TFile.Open(histogramFile)
    keys = [k.GetName() for k in f.GetListOfKeys()]
    keys = [k for k in keys if k.split("___")[0] in erasOfInterest and k.split("___")[1] in samplesOfInterest]
    keys = [k for k in keys if k.split("___")[2] in channelsOfInterest and  k.split("___")[5] in varsOfInterest]
    eras = list(set([k.split("___")[0] for k in keys]))
    print(eras)
    samples = list(set([k.split("___")[1] for k in keys]))
    print(samples)
    channels = list(set([k.split("___")[2] for k in keys]))
    print(channels)
    channelWindows = list(set(["___".join(k.split("___")[2:4]) for k in keys]))
    print(channelWindows)
    categories = list(set([k.split("___")[4] for k in keys]))
    print(categories)
    variables = list(set([k.split("___")[5] for k in keys]))
    print(variables)
    systematics = list(set([k.split("___")[6] for k in keys]))
    print(systematics)
    for era in eras:
        print(era)
        for channelWindow in channelWindows:
            print(channelWindow)
            for category in categories:
                print(category)
                for variable in variables:
                    print(variable)
                    hists = {}
                    rebinnedHists = {}
                    nBinsX = 0
                    print("Skipping...")
                    if variable != "HTUnweighted" and category != "HT500_nMediumDeepJetB4+_nJet8+": continue
                    for systematic in systematics:
                        print(systematic)
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
                    #Have all the systematic variations that are relevant
                    #Finished hadding the histograms
                    entryArray = np.zeros((len(systematics), nBinsX+2), dtype=np.int32)
                    # binningArray.append(0) #Can't rebin the overflow anyway... thanks ROOT
                    for nsyst, systematic in enumerate(systematics):
                        for nbin in xrange(0, hists[systematic].GetNbinsX()+2): #Include underflow and overflow for bin numbering clarity                            
                            entryArray[nsyst, nbin] = hists[systematic].GetBinContent(nbin)
                    start = 1 #Don't include underflow
                    stop = start + 1 #Initialize so that we start with checking the singular bin
                    end = nBinsX + 1 #Don't include overflow
                    lastbin = end - 1
                    binningArray = []
                    binningArray.append(start)
                    with np.errstate(divide='ignore'):
                        while(stop < end - 1):
                            while(np.all(1/np.sqrt(entryArray[:, start:stop].sum(axis=1)) > relUncertainty)):
                                # theArray = entryArray[:, start:stop]
                                # theSum = theArray.sum(axis=1)
                                # theError = 1/min(np.sqrt(theSum), 0.0000000000001)
                                # theComparison = theError < relUncertainty
                                # theSolution = np.all(theComparison)
                                # print("array: {}".format(theArray))
                                # print("sum: {}".format(theSum))
                                # print("relative error: {}".format(theError))
                                # print("relative error < threshold: {}".format(theComparison))
                                # print(theSolution)
                                # print("solution found: {}:{} --> {}".format(start, stop, theSolution))
                                stop += 1
                            #After the while loop, we should have a good start:stop range for rebinning
                            binningArray.append(stop)
                            #Now increment the start and stop
                            start = copy.copy(stop)
                            stop += 1
                            print("start: {}    stop: {}     end: {}".format(start, stop, end))
                        #If we did not find a solution to the last rebinning, then merge it with the previous rebin
                        if binningArray[-1] < lastbin:
                            binningArray[-1] = lastbin
                        print(binningArray)
                        print(entryArray)
                    rebinningEdges = []
                    for binNumber in binningArray:
                        rebinningEdges.append(hists.values()[0].GetBinLowEdge(binNumber))
                    edgesArray = array.array('d', rebinningEdges)
                    for systematic in systematics:
                        rebinnedHists[systematic] = hists[systematic].Rebin(len(edgesArray)-1, hists[systematic].GetName() + "_rebin", edgesArray)
                        testError = []
                        for binNumber in xrange(1, hists[systematic].GetNbinsX()+1):
                            testError.append(rebinnedHists[systematic].GetBinError(binNumber)/rebinnedHists[systematic].GetBinContent(binNumber))
                        print("testError[{}]: {}".format(systematic, testError))
                        print("testErrorBelowThresh[{}]: {}".format(systematic, [t < relUncertainty for t in testError]))                        
                    pdb.set_trace()
                    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Determine binning automatically for categorized histograms using a particular subset of processes')
    parser.add_argument('stage', action='store', type=str, choices=['determine-binning'],
                        help='analysis stage to be produced')
    parser.add_argument('--analysisDirectory', dest='analysisDirectory', action='store', type=str, default="/eos/user/$U/$USER/analysis/$DATE",
                        help='output directory path defaulting to "."')
    parser.add_argument('--channel', dest='channel', action='store', type=str, default="ElMu", choices=['ElMu', 'ElEl', 'MuMu'],
                        help='Decay channel for opposite-sign dilepton analysis')
    parser.add_argument('--era', dest='era', type=str, default="2017",
                        help='era for plotting, which deduces the lumi only for now')
    parser.add_argument('--relUncertainty', dest='relUncertainty', action='store', type=float, default=0.3,
                        help='maximum relative uncertainty (sqrt(N)/N) per bin used as the criteria for merging')
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
    main(stage, analysisDir, channel, args.era, args.relUncertainty)
