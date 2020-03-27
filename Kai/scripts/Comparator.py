#!/usr/python
import time
import argparse
from datetime import datetime
import collections 
#from collections import Counter, OrderedDict
import traceback #For handling exceptions
import math
import copy
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


from datetime import datetime
parser = argparse.ArgumentParser(description='NanoAOD-Diff Does comparisons between two samples of NanoAOD')
parser.add_argument('--input', dest='input', action='append', nargs='*', type=str,
                    help='globbable path to an input. May be used multiple times, once per set of inputs')
parser.add_argument('--labels', dest='labels', action='store', nargs='*', type=str, default=None,
                    help='labels of inputs')
parser.add_argument('--noBatch', dest='noBatch', action='store_true', 
                    help='Disable Batch mode, allowing plots to be drawn in windows')
parser.add_argument('--rMin', dest='rMin', action='store', nargs='?', type=float, default=0.9,
                    help='Minimum for ratio plots')
parser.add_argument('--rMax', dest='rMax', action='store', nargs='?', type=float, default=1.1,
                    help='Maximum for ratio plots')
parser.add_argument('--pdfOut', dest='pdfOut', action='store', nargs='?', type=str, const="NanoAOD-Diff.pdf", default=None,
                    help='Name of pdf output file, if plotting selected')
args = parser.parse_args()
procstart = collections.OrderedDict()
procfinish = collections.OrderedDict()
nToLabel = {}
labelToN = {}
for ln, label in enumerate(args.labels):
    nToLabel[ln] = label
    labelToN[label] = ln




def main():
  
    # for fn, fs in enumerate(args.input):
    #     print("\tSample '{}'".format(nToLabel[fn]))
    #     for fname in fs[0].split():
    #         print("\t\t{}".format(fname))
            
    # #inputFiles = [fs[0].split() for fs in args.input]
    # weightFormulas = args.weights
    # try: 
    #     match_subexpression = (args.match.lower() == 'subexpression')
    # except:
    #     match_subexpression = False
    # try: 
    #     match_exact = (args.match.lower() == 'exact')
    # except:
    #     match_exact = False
    # print("\tInputs - {}".format(args.input))
    # print("\tLabels - {}".format(args.labels))
    # print("\tWeights - {}".format(args.weights))
    # print("\tBlackList file - {}".format(args.BL))
    # print("\tWhiteList file - {}".format(args.WL))
    # print("\tplotcard files - {}".format(args.plotcards))
    # print("\tmatch_exact = {} match_subexpression = {}".format(match_exact, match_subexpression))
    # print("\n\tUsing backend - {}".format(args.backend))

    #Check for mismatch in labels or weights, since expecting 1-1 correspondence
    # if args.labels != None:
    #     if len(args.input) != len(args.labels):
    #         raise RuntimeError("Mismatch in mumber of labels and input sets. If labels are specified, must be equal calls to --label and --input")

    if args.noBatch == False:
        ROOT.gROOT.SetBatch()

    #Call RDataFrame backend, if chosen
    # if args.backend == "RDF":
    #     print("\tRDataFrame Implicit Multi-threading disabled - {}".format(args.noIMT))
    #     print("====================")
    #     if not args.noIMT:
    #         ROOT.ROOT.EnableImplicitMT()
    #     inputSets = []
    #     for fn, f in enumerate(args.input):
    #         #convert a list (len(f) > 1) of inputs for a given sample to a vector of strings, an acceptable input type for RDF
    #         if len(f) > 1:
    #             tmp = ROOT.std.vector(str)(len(f))
    #             for sn, subf in enumerate(f):
    #                 tmp[sn] = subf
    #             inputSets.append(tmp)
    #         else:
    #             inputSets.append(f[0])
    #     branchDict = getBranchInfo_RDF(inputSets, whiteList = args.WL, blackList = args.BL)
    #     branchReport_RDF(branchDict, reportFile = "branchReport.txt")
    #     if args.noPlots == False:
    #         plotDict = makePlotDict(args.plotcards)
    #         histDict, uniqueHistDict = makeHists_RDF(branchDict, plotDict, eventsKey = "Events", weightsKey = "Weights")
    #         #Make histogram file if option histOut is called, which optionally contains a non-default filename.
    #         if args.histOut != None:
    #             print("Writing hist file")
    #             for sn, flatDict in histDict.items():
    #                 dictToFile(flatDict, args.histOut, update=True, prefix=nToLabel[sn])
    histDict = fileToDict(nToLabel, args.input[0][0])
    #Make the function for plotting here
    if args.pdfOut != None:
        canvasDict = makePlots_RDF(histDict, args.pdfOut)
            
            
    timeReport(prnt=True)

def getBranchInfo_RDF(inputSets, blackList = None, whiteList = None):
    """Get dictionary of branch info including fields like SumWeights, SumEvents, BranchTypes, BranchSetsFiltered, etc. See method getBranchInfo_*"""
    procstart['getBranchInfo_RDF'] = datetime.now()
    #["HLT_", "L1_", "nTau", "nSubJet", "nSubGenJetAK8", "nSoftActivityJet", "nSV", "nPhoton", "nOtherPV", "nMuon", ]
    #["Electron", "Muon", "Photon", "Jet", "GenJet", "FatJet", "GenJetAK8", "GenPart", "Tau", "MET", "SubJet", "PV", "SV"]
    #Runs meta info in the TChain
    Files = {} #Files 
    Runs = {} #Store the Runs tree RDF node
    SumEvents = {} #Store the sum of events that were processed (meta-level)
    SumEventsBranchName = {} #The branch name, in case there are some minor perturbation, such as addition of '_'
    SumWeights = {} #Store the sum of event weights from processed events (meta-level)
    SumWeightsBranchName = {}
    SumWeights2 = {} #Store the sum of event weights squared from processed events (meta-level)
    SumWeights2BranchName = {}

    Events = {} #The actual events info for each TChain
    Branches = {} #list of branches in the Events tree, for use in creating histograms
    BranchTypesRaw = {}
    BranchTypes = {} #Store the type, min, and max of each branch (implies double event loop, but Min/Max likely faster than histogram
    # BranchMin = {} #These break on a number of NanoAOD branches. Very concerning... same for Stats, Histo1D, etc. No exact pattern found yet
    # BranchMax = {}
    # BranchStats = {}
    Blacks = {} #sets of branches that will be rejected if no whitelist
    Whites = {} #sets of branches that will be plotted, with crossplots for the intersection between inputs

    BranchSets = {} #for use in finding common branches and reducing plots (via whiteList or blackList)
    BranchSetsFiltered = {} #The filtered set of branches after filtering via whiteList or blackList
    TypeCountsRaw = {}
    TypeCounts = {}
    indices = []
    Weights = {}

    for fn, f in enumerate(inputSets):
        indices.append(fn)
        Files[fn] = f
        Runs[fn] = ROOT.ROOT.RDataFrame("Runs", f)
        SumEventsBranchName[fn] = [cn for cn in Runs[fn].GetColumnNames() if "genEventCount" in cn]
        SumWeightsBranchName[fn] = [cn for cn in Runs[fn].GetColumnNames() if "genEventSumw" in cn and "genEventSumw2" not in cn]
        SumWeights2BranchName[fn] = [cn for cn in Runs[fn].GetColumnNames() if "genEventSumw2" in cn]
        if len(SumEventsBranchName[fn]) > 0:
            SumEvents[fn] = Runs[fn].Define("se", SumEventsBranchName[fn][0]).Sum("se").GetValue() #Stats available
        else: 
            SumEvents[fn] = None
        if len(SumWeightsBranchName[fn]) > 0:
            SumWeights[fn] = Runs[fn].Define("sw", SumWeightsBranchName[fn][0]).Sum("sw").GetValue()
        else:
            SumWeights[fn] = None
        if len(SumWeights2BranchName[fn]) > 0:
            SumWeights2[fn] = Runs[fn].Define("sw2", SumWeights2BranchName[fn][0]).Sum("sw2").GetValue()
        else:
            SumWeights2[fn] = None
        #Make use of meta info to replace keyword values in Weights definitions
        if args.weights != None:
            Weights[fn] = args.weights[fn]\
                              .replace(SumWeights2BranchName[fn][0], str(SumWeights2[fn]))\
                              .replace("genEventSumw2", str(SumWeights2[fn]))\
                              .replace(SumWeightsBranchName[fn][0], str(SumWeights[fn]))\
                              .replace("genEventSumw", str(SumWeights[fn]))\
                              .replace(SumEventsBranchName[fn][0], str(SumEvents[fn]))\
                              .replace("genEventCount", str(SumEvents[fn]))
            print("For dataset {}, will define 'diffWeight' = '{}'".format(nToLabel[fn], Weights[fn]))
        else:
            Weights[fn] = "1"

        Events[fn] = ROOT.ROOT.RDataFrame("Events", f).Define("diffWeight", str(Weights[fn]))
        Branches[fn] = [b for b in Events[fn].GetColumnNames()]
        BranchTypesRaw[fn] = {}
        BranchTypes[fn] = {}
        # BranchMin[fn] = {}
        # BranchMax[fn] = {}
        # BranchStats[fn] = {}
        TypeCountsRaw[fn] = {}
        TypeCounts[fn] = {}
        for b in Branches[fn]:
            BranchTypesRaw[fn][b] = Events[fn].GetColumnType(b)
            BranchTypes[fn][b] = BranchTypesRaw[fn][b].replace("ROOT::VecOps::RVec<", "").replace(">", "")
            #BranchMin[fn][b] = Events[fn].Min(b) if 'Bool_t' not in BranchTypes[fn][b] else 0
            #BranchMax[fn][b] = Events[fn].Max(b) if 'Bool_t' not in BranchTypes[fn][b] else 2
            #BranchStats[fn][b] = Events[fn].Stats("{}".format(b))
        TypeCountsRaw[fn] = collections.Counter(BranchTypesRaw[fn].values()) 
        TypeCounts[fn] = collections.Counter(BranchTypes[fn].values()) 
        BranchSets[fn] = set([b for b in Branches[fn]])
        Blacks[fn] = set([])
        Whites[fn] = set([])
        if (type(whiteList) is list or type(whiteList) is set) and len(whiteList) > 0:
            for whiteList_elem in whiteList:
                tmp = set([])
                if match_subexpression == True:
                    tmp = set([b for b in Branches[fn] if whiteList_elem in b])
                elif match_exact == True:
                    tmp = set([b for b in Branches[fn] if whiteList_elem == b])
                Whites[fn] = Whites[fn].union(tmp)
        if (type(blackList) is list or type(blackList) is set) and len(blackList) > 0:
            for blackList_elem in blackList:
                tmp = set([])
                if match_subexpression == True:
                    tmp = set([b for b in Branches[fn] if blackList_elem in b])
                elif match_exact == True:
                    tmp = set([b for b in Branches[fn] if blackList_elem == b])
                Blacks[fn] = Blacks[fn].union(tmp)
        if len(Whites[fn]) > 0:
            #Filter for whitelist items
            BranchSetsFiltered[fn] = BranchSets[fn] & Whites[fn] #Intersection with .intersection() = operator&
            if len(Blacks[fn]) > 0: #Also filter out the blacklist items
                BranchSetsFiltered[fn] -= Blacks[fn]
        elif len(Blacks[fn]) > 0:
            BranchSetsFiltered[fn] = BranchSets[fn] - Blacks[fn] #Remove elements with .difference() = operator-
        else:
            BranchSetsFiltered[fn] = BranchSets[fn]
        #Blacks[fn] = set([b for b in Branchs[fn]]) #do loop over elements of blackList creating subsets, then union/disjoint things


    retDict = {"Files": Files,
               "Runs": Runs,
               "SumEvents": SumEvents,
               "SumEventsBranchName": SumEventsBranchName,
               "SumWeights": SumWeights,
               "SumWeightsBranchName": SumWeightsBranchName,
               "SumWeights2": SumWeights,
               "SumWeights2BranchName": SumWeightsBranchName,
               "Weights": Weights,
               "Events": Events,
               "Branches": Branches,
               "BranchTypesRaw": BranchTypesRaw,
               "BranchTypes": BranchTypes,
               "BranchSets": BranchSets,
               "BranchSetsFiltered": BranchSetsFiltered,
               "TypeCountsRaw": TypeCountsRaw,
               "TypeCounts": TypeCounts,
               "indices": indices
               }
    procfinish['getBranchInfo_RDF'] = datetime.now()
    return retDict

def makeHists_RDF(branchDict, plotDict, eventsKey = "Events", weightsKey = "Weights"):
    procstart['makeHists_RDF(Define)'] = datetime.now()
    histDict = collections.OrderedDict()
    uniqueHistDict = collections.OrderedDict()
    for fn in branchDict[eventsKey].keys():
        histDict[fn] = collections.OrderedDict()
        uniqueHistDict[fn] = collections.OrderedDict()
    for br, plot in plotDict.items():
        for fn, rdf in branchDict[eventsKey].items():
            if br in histDict[fn]: 
                print("Warning, dual definition of branch {} when making Histograms from plotcards. Will keep first branch only.")
                continue
            if br not in branchDict["BranchSetsFiltered"][fn]:
                uniqueHistDict[fn][br] = rdf.Histo1D(plot, str(br), "diffWeight")
            # print("({}, {}, {})".format(plot, br, branchDict[weightsKey][fn]))
            else:
                #change the plot name in memory by replacing 
                plot_labeled = (plot[0].replace("$INPUT", nToLabel[fn]), plot[1], plot[2], plot[3], plot[4])
                histDict[fn][br] = rdf.Histo1D(plot_labeled, str(br), "diffWeight")
    procfinish['makeHists_RDF(Define)'] = datetime.now()
    procstart['makeHists_RDF(Run)'] = datetime.now()
    counts = {}
    #Trigger the event loops and replace the histogram RResultPtr's with the actual filled histograms
    print("Starting event loop...")
    for fn, rdf in branchDict[eventsKey].items():
        counts[fn] = rdf.Count().GetValue()
        for br, hist in histDict[fn].items():
            histDict[fn][br] = hist.GetPtr().Clone()
        for br, hist in uniqueHistDict[fn].items():
            histDict[fn][br] = hist.GetPtr().Clone()
    procfinish['makeHists_RDF(Run)'] = datetime.now()
    return histDict, uniqueHistDict

def makePlotDict(plotcards):
    procstart['makePlotDict'] = datetime.now()
    """Create a dictionary of tuples for plotting, including a name for ROOT, a title, number of bins, X axis mins and maxes, starting from a list of text files.
    Text files should contain "<branchname>    <nbins>    <xmin>    <xmax>" on each line, where the newline will be stripped and the line will be split by "    " (4 whitespaces) separator.
    Returns the dictionary of tuples with branches as the keys"""
    plotDict = collections.OrderedDict()
    for card in plotcards:
        with open(card, "r") as c:
            for line in c:
                br, nb, mn, mx = line.rstrip().split("    ")
                if br[0] == "#": continue #skip commented lines
                plotDict[br] = ("h_{0}_$INPUT".format(br), "{0}; {0} ; Arbitrary units".format(br), int(nb), float(mn), float(mx))
    # for k, v in plotDict.items():
    procfinish['makePlotDict'] = datetime.now()
    return plotDict
    
def timeReport(prnt=False):
    """Generate string report on the time each step took when called"""
    report = ""
    for k in procstart.keys():
        timedelt = procfinish[k] - procstart[k]
        td_s = timedelt.total_seconds()
        report += "Took {:4d}m and {:4.1f}s to finish {}\n".format(int(td_s//60), td_s%60, k)
    if prnt == True:
        print(report)
    return report

def getEdgesAndBinning(low_in, high_in, request):
    """low is the lower edge of an integer binning, high is a float that represents the minimum high edge, request is the desired number of bins (also an integer). 
    Return the high edge integer that gives integer bin width"""
    #if type(request) != int:
    #    raise ValueError("getEdgeHigh did not receive an integer for the requested number of bins")
    #Get the float bin width, after flooring the low
    low = int(math.floor(low_in))
    w = abs((high_in - low)/request)
    #try two different values of integer bin width to find the one that most closely reaches the high desired
    a = int(math.floor(w))# + 1.0))
    if a < 1: a = 1
    b = int(math.ceil(w))
    if b < 1: b = 1
    #make sure the low bin is below the low threshold input
    if low < 0: 
        alow = int(math.ceil(low))
    else: 
        alow = int(math.floor(low))
    blow = alow
    #Initialize the high bins to equality with low, then increment bins and bin widths
    ahigh = copy.copy(low)
    abins = 0
    bhigh = copy.copy(low)
    bbins = 0
    #Increase number of bins and high edge until over the high threshold input
    while ahigh < high_in:
        abins += 1
        ahigh += a
    while bhigh < high_in:
        bbins += 1
        bhigh += b
    #check for the high edge closest to input threshold, choose that one
    if (ahigh - high_in) < (bhigh - high_in):
        return alow, ahigh, abins
    else:
        return blow, bhigh, bbins
    
def getBinOverIntegralThresh(hist, thresh=None, frac=None):
    nbins = hist.GetNbinsX()
    theBin = 0
    tot = hist.Integral(0, nbins)
    if frac == None and thresh == None:
        raise ValueError("Either thresh or perc must be chosen in getBinMinIntegral()")
    elif frac == None:
        min_thresh = thresh
    elif thresh == None:
        min_thresh = frac*tot #
    for x in xrange(nbins+1): #+1 to include last bin
        y = hist.Integral(0, x)
        if y > min_thresh:
            return x
    return None 

def branchReport_RDF(branchDict, reportFile = "branchReport.txt"):
    procstart['branchReport_RDF'] = datetime.now()
    uniquePairs = [(a,b) for a in branchDict["indices"] for b in branchDict["indices"] if a < b]
    with open(reportFile, "w") as o:
        for indexA, indexB in uniquePairs:
            inCommon = branchDict["BranchSets"][indexA].intersection(branchDict["BranchSets"][indexB])
            onlyInA = branchDict["BranchSets"][indexA] - branchDict["BranchSets"][indexB]
            onlyInB = branchDict["BranchSets"][indexB] - branchDict["BranchSets"][indexA]
            o.write("==================================\n")
            o.write("Report on inputs {iA} and {iB}:\n    files[{iA}]: {fA}\n    files[{iB}]: {fB}\n"\
                    "\n    SumEvents[{iA}]: {seA}\n    SumEvents[{iB}]: {seB}"\
                    "\n    SumWeights[{iA}]: {swA}\n    SumWeights[{iB}]: {swB}\n"\
                    .format(iA = indexA, iB = indexB, fA = branchDict["Files"][indexA], fB = branchDict["Files"][indexB],
                            seA = branchDict["SumEvents"][indexA], seB = branchDict["SumEvents"][indexB],
                            swA = branchDict["SumWeights"][indexA], swB = branchDict["SumWeights"][indexB]))
        o.write("\n======== Common Branches ========\n")
        for b in sorted(inCommon): 
            o.write(b + " << " + branchDict["BranchTypes"][indexA][b] + " << "+ branchDict["BranchTypes"][indexB][b] + "\n")
        o.write("\n======== Branches only in {iA} ========\n".format(iA = indexA))
        for b in sorted(onlyInA): 
            o.write(b + " << " + branchDict["BranchTypes"][indexA][b] + "\n")
        o.write("\n======== Branches only in {iB} ========\n".format(iB = indexB))
        for b in sorted(onlyInB): 
            o.write(b + " << " + branchDict["BranchTypes"][indexB][b] + "\n")
        o.write("==================================\n")
    procfinish['branchReport_RDF'] = datetime.now()

def makePlots_RDF(histDict, pdfFile, colorList = [ROOT.kBlack, ROOT.kRed, ROOT.kGreen, ROOT.kAzure]):
    procstart['makePlots_RDF'] = datetime.now()
    last = len(histDict[0].keys()) - 1
    for bn, branch in enumerate(histDict[0].keys()):
        c, upperPads, lowerPads = createCanvasPads(branch, doRatio=True, setXGrid=True, setYGrid=False,
                                                   nXPads=1, topFraction=0.7, xpixels=800, ypixels=800)
        upperPads[0].cd()
        for sn, sample in enumerate(histDict.items()):
            print(sample)
            # print("{}_{}".format(branch, sample))
            # theClone = "{}".format(histDict[sample][branch].GetName()).replace("h_", "")
            # print(theClone)
            h = histDict[sample][branch]#.Clone(theClone)
            print(type(h))
            if sn == 0:
                h.SetFillColorAlpha(colorList[sn], 0.3)
                #h.SetLineColor(colorList[sn])
                #ROOT.gStyle.SetOptStat(1001111)
                h.Draw("S HIST")
                xaxis = h.GetXaxis()
                yaxis = h.GetYaxis()
                xaxis.SetLabelFont(43)
                xaxis.SetLabelSize(15)
                #yaxis.SetLabelSize(0.0)
                #axis = ROOT.TGaxis(xaxis.GetXmin(), yaxis.GetXmin(), xaxis.GetXmax(), yaxis.GetXmax(), 20., 220., 510, "") #last 4 are wmin, wmax, nDivisions, options string
                #axis.SetLabelFont(43)
                #axis.SetLabelSize(15)
                #axis.Draw()
            else:
                if sn >= len(colorList): raise RuntimeError("makePlots_* Requires a longer colorList to set the line color for this histogram, see configuration")
                h.SetLineColor(colorList[sn])
                #ROOT.gStyle.SetOptStat(1001111)
                h.Draw("SAME HIST S")
        #organize the stats boxes
        #for sn, sample in enumerate(histDict.keys()):
        #    if sn == 0:
        #        StatBox = h.GetListOfFunctions().FindObject("stats")
        #        StatBox.SetY1NDC(0.7)
        #        StatBox.SetY2NDC(0.5)
        #    else:
        #        StatBox = h.GetListOfFunctions().FindObject("stats")
        #        StatBox.SetY1NDC(0.5)
        #        StatBox.SetY2NDC(0.3)
        lowerPads[0].cd()
        for sn, sample in enumerate(histDict.keys()):
            if sn == 0: continue #Take first sample as the denominator always
            numerator = nToLabel[sn]
            denominator = nToLabel[0]
            hrat = createRatio(histDict[sample][branch], histDict[0][branch], ratioTitle="#frac{0}{1}".format("{"+numerator+"}", "{"+denominator+"}"))
            if sn == 1:
                hrat.Draw("ep")
            else:
                hrat.Draw("SAME ep")
        c.Draw()
        if bn == 0:
            c.SaveAs("{}(".format(pdfFile))
        elif bn == last:
            c.SaveAs("{})".format(pdfFile))
        else:
            c.SaveAs("{}".format(pdfFile))
    procfinish['makePlots_RDF'] = datetime.now()

def createRatio(h1, h2, ratioTitle="input 0 vs input 1", ratioColor = ROOT.kBlack):
    #h3 = h1.Clone("rat_{}_{}".format(h1.GetName(), ratioTitle.replace(" ", "_")))
    #h3 = h1.Clone("rat_{}".format(h1.GetName()))
    h3 = h1#.Clone("rat_{}".format((h1.GetName()).replace("h_","")))
    h3.SetLineColor(ratioColor)
    h3.SetMarkerStyle(21)
    # h3.SetTitle("")
    h3.SetMinimum(args.rMin)
    h3.SetMaximum(args.rMax)
    # Set up plot for markers and errors
    h3.Sumw2()
    h3.SetStats(0)
    h3.Divide(h2)

    # Adjust y-axis settings
    y = h3.GetYaxis()
    y.SetTitle(ratioTitle)
    y.SetNdivisions(505)
    y.SetTitleSize(20)
    y.SetTitleFont(43)
    y.SetTitleOffset(1.55)
    y.SetLabelFont(43)
    y.SetLabelSize(15)

    # Adjust x-axis settings
    x = h3.GetXaxis()
    x.SetTitleSize(20)
    x.SetTitleFont(43)
    x.SetTitleOffset(4.0)
    x.SetLabelFont(43)
    x.SetLabelSize(15)

    return h3


def createCanvasPads(canvasTitle, doRatio=True, setXGrid=False, setYGrid=False,
                     nXPads=1, topFraction=0.7, xpixels=800, ypixels=800):
    """Create canvas with two pads vertically for each of doLin and doLog if they are true"""
    #Divide implicitely creates subpads. This function uses more explicit methods to do the same with varying pad sizes
    c = ROOT.TCanvas(canvasTitle, canvasTitle, xpixels, ypixels)
    # Upper histogram plot is pad1
    upperPads = []
    lowerPads = []
    xEdgesLow = [z/float(nXPads) for z in xrange(nXPads)]
    xEdgesHigh = [(z+1)/float(nXPads) for z in xrange(nXPads)]
    if doRatio:
        yDivision = 1-topFraction
    else:
        yDivision = 0


    for z in xrange(nXPads):
        c.cd()  # returns to main canvas before defining another pad, to not create sub-subpad
        padU = ROOT.TPad("{}_{}".format(canvasTitle,z), "{}_{}".format(canvasTitle,z), 
                        xEdgesLow[z], 1-topFraction, xEdgesHigh[z], 1.0) #xmin ymin xmax ymax as fraction
        if doRatio:
            padU.SetBottomMargin(0)  # joins upper and lower plot
        if setXGrid:
            padU.SetGridx()
        if setYGrid:
            padU.SetGridy()
        padU.Draw()
        if doRatio:
            # Lower ratio plot is pad2
            padL = ROOT.TPad("ratio_{}_{}".format(canvasTitle,z), "ratio_{}_{}".format(canvasTitle,z), 
                             xEdgesLow[z], 0.05, xEdgesHigh[z], 1-topFraction) #xmin ymin xmax ymax as fraction
            padL.SetTopMargin(0)  # joins upper and lower plot
            padL.SetBottomMargin(0.2)
            if setXGrid:
                padL.SetGridx()
            if setYGrid:
                padL.SetGridy()
            padL.Draw()
        upperPads.append(padU)
        lowerPads.append(padL)
    return c, upperPads, lowerPads

def dictToFile(histDict, fileName, update=False, prefix=None):
    for k, v in histDict.items():
        if type(v) == dict or type(v) == collections.OrderedDict:
            raise NotImplementedError("In method dictToFile, the key '{}' corresponds to a nested dictionary. dictToFile cannot handle recursively."\
                                      .format(k))
    f = None
    #Store the previous directory so we can return to it once the file is opened and closed, otherwise ROOT suicides itself
    prevdir = ROOT.gDirectory
    print("Attempting to open file {}".format(fileName))
    try:
        if update == True:
            f = ROOT.TFile.Open(fileName, "UPDATE")
        else:
            f = ROOT.TFile.Open(fileName, "RECREATE")

        f.cd()
        for k, v in histDict.items():
            if prefix != None:
                name = prefix + "_" + k
            else:
                name = k
            print(name)
            v.Write(name)
    except:
        print("There was an exception in the function dictToFile()")
    finally:
        if f != None:
            f.Close()
        prevdir.cd()
    

def fileToDict(nToLabel, fileName, parseIndex = 0):
    prevdir = ROOT.gDirectory
    histDict = collections.OrderedDict()
    histList = collections.OrderedDict()
    for n in nToLabel.keys():
        histDict[n] = collections.OrderedDict()
        histList[n] = []
    f = None
    print("Attempting to open file {}".format(fileName))
    try:
        f = ROOT.TFile.Open(fileName, "r")
        keys = f.GetListOfKeys()
        keys = [k.GetName() for k in keys]
        for n, label in nToLabel.items():
            print("making dictionary for {} - {}".format(n, label))
            print(keys[0].split("_")[parseIndex])
            histList[n] = [k for k in keys if label == k.split("_")[parseIndex]]
            for k in histList[n]:
                truekey = k.replace("_{}".format(label), "").replace("{}_".format(label), "")
                histDict[n][truekey] = f.Get(k)
        print(histDict)
        return histDict
    except:
        print("There was an exception in the function fileToDict()")
    finally:
        if f != None:
            f.Close()
        prevdir.cd()
    

if __name__ == '__main__':
    main()

