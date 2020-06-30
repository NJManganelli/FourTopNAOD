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
from datetime import datetime
ROOT.PyConfig.IgnoreCommandLineOptions = True

ROOT.gInterpreter.Declare("""
    ROOT::RDF::RResultPtr<ULong64_t> AddProgressPrinter(ROOT::RDF::RNode df, int everyN=10000) {
        auto c = df.Count();
        c.OnPartialResult(/*every=*/everyN, [] (ULong64_t e) { std::cout << e << std::endl; });
        return c;
    }
""")
ROOT.gInterpreter.Declare("""
    const UInt_t barWidth = 60;
    ULong64_t processed = 0, totalEvents = 0;
    std::string progressBar;
    std::mutex barMutex; 
    auto registerEvents = [](ULong64_t nIncrement) {totalEvents += nIncrement;};

    ROOT::RDF::RResultPtr<ULong64_t> AddProgressBar(ROOT::RDF::RNode df, int everyN=10000, int totalN=100000) {
        registerEvents(totalN);
        auto c = df.Count();
        c.OnPartialResultSlot(everyN, [everyN] (unsigned int slot, ULong64_t &cnt){
            std::lock_guard<std::mutex> l(barMutex);
            processed += everyN; //everyN captured by value for this lambda
            progressBar = "[";
            for(UInt_t i = 0; i < static_cast<UInt_t>(static_cast<Float_t>(processed)/totalEvents*barWidth); ++i){
                progressBar.push_back('|');
            }
            // escape the '\' when defined in python string
            std::cout << "\\r" << std::left << std::setw(barWidth) << progressBar << "] " << processed << "/" << totalEvents << std::flush;
        });
        return c;
    }
""")

parser = argparse.ArgumentParser(description='NanoAOD-Diff Does comparisons between two samples of NanoAOD')

parser.add_argument('--stage', dest='stage', choices=['report', 'stats', 'plots'],
                    help='Stage for NanoAOD-Diff. Report produces text file of common and unique branches. Stats produces text files of Min, Max, Mean, Variance, etc. for branches. Plots produces histograms of branches.')
parser.add_argument('--nThreads', dest='nThreads', action='store', type=int, default=4,
                    help='CPU threads for computation')
parser.add_argument('--reportEvery', dest='reportEvery', action='store', type=int, default=10000,
                    help='Number of events to process before notifying of progress')
parser.add_argument('--doHLT', dest='doHLT', action='store_true', 
                    help='Do computations for HLT branches')
parser.add_argument('--doL1', dest='doL1', action='store_true', 
                    help='Do computations for L1 branches')
parser.add_argument('--input', '-i', dest='input', action='append', nargs='*', type=str,
                    help='globbable path to an input or list. Call once for each set of input files')
parser.add_argument('--label', '-l', dest='label', action='append', nargs='?', type=str, default=None,
                    help='label of inputs')
parser.add_argument('--weight', '-w', dest='weight', action='append', nargs='?', type=str, default=None,
                    help='weight formulas for inputs')
parser.add_argument('--WL', dest='WL', action='store', nargs='*', type=str, default=None,
                    help='WhiteList for plotting')
parser.add_argument('--BL', dest='BL', action='store', nargs='*', type=str, default=None,
                    help='BlackList for plotting')
parser.add_argument('--match', dest='match', choices=['exact', 'subexpression'],
                    help='Whether WhiteList/BlackList elements must match exactly or may be subexpressions of plotted variables')
parser.add_argument('--backend', dest='backend', choices=['RDF', 'PyRDF'],
                    help='Backend used for computation.\nRDF = RDataFrame (https://root.cern.ch/doc/master/classROOT_1_1RDataFrame.html)')
parser.add_argument('--noIMT', dest='noIMT', action='store_true', 
                    help='Disable Implicit MultiThread for RDataFrame')
parser.add_argument('--noBatch', dest='noBatch', action='store_true', 
                    help='Disable Batch mode, allowing plots to be drawn in windows')
parser.add_argument('--plotcards', dest='plotcards', action='store', nargs='*', type=str, default=None,
                    help='plotcards to load and parse, syntax (separator = 4 spaces):<branchname>    <nbins>    <xmin>    <xmax>')
parser.add_argument('--rMin', dest='rMin', action='store', nargs='?', type=float, default=0.9,
                    help='Minimum for ratio plots')
parser.add_argument('--rMax', dest='rMax', action='store', nargs='?', type=float, default=1.1,
                    help='Maximum for ratio plots')
parser.add_argument('--pdfOut', dest='pdfOut', action='store', nargs='?', type=str, const="NanoAOD-Diff.pdf", default=None,
                    help='Name of pdf output file, if plotting selected')
parser.add_argument('--histOut', dest='histOut', action='store', nargs='?', type=str, const="NanoAOD-Diff_hist.root", default=None,
                    help='Name of hist output file, if plotting selected')
parser.add_argument('--noPlots', dest='noPlots', action='store_true', 
                    help='Disable plotting')
args = parser.parse_args()


#Call RDataFrame backend, if chosen
if args.backend == "RDF":
    print("\tRDataFrame Implicit Multi-threading {}".format("ENABLED" if args.noIMT == False else "DISABLED"))
    print("====================")
    if not args.noIMT:
        ROOT.ROOT.EnableImplicitMT(args.nThreads)
    RDF = ROOT.ROOT.RDataFrame
if args.backend == "PyRDF":
    import PyRDF
    PyRDF.use("spark", {'npartitions': '64'}) #was 32 in example
    RDF = PyRDF.RDataFrame
            
procstart = collections.OrderedDict()
procfinish = collections.OrderedDict()
nToLabel = {}
labelToN = {}
print(args.label)
for ln, label in enumerate(args.label):
    nToLabel[ln] = label
    labelToN[label] = ln

def main():
  
    for fn, fs in enumerate(args.input):
        print("\tSample '{}'".format(nToLabel[fn]))
        for fname in fs[0].split():
            print("\t\t{}".format(fname))
            
    #inputFiles = [fs[0].split() for fs in args.input]
    weightFormulas = args.weight
    try: 
        match_subexpression = (args.match.lower() == 'subexpression')
    except:
        match_subexpression = False
    try: 
        match_exact = (args.match.lower() == 'exact')
    except:
        match_exact = False
    print("\tInputs - {}".format(args.input))
    print("\tLabels - {}".format(args.label))
    print("\tWeights - {}".format(args.weight))
    print("\tBlackList file - {}".format(args.BL))
    print("\tWhiteList file - {}".format(args.WL))
    print("\tplotcard files - {}".format(args.plotcards))
    print("\tmatch_exact = {} match_subexpression = {}".format(match_exact, match_subexpression))
    print("\n\tUsing backend - {}".format(args.backend))

    #Check for mismatch in labels or weights, since expecting 1-1 correspondence
    if args.label != None:
        if len(args.input) != len(args.label):
            raise RuntimeError("Mismatch in mumber of labels and input sets. If labels are specified, must be equal calls to --label and --input")
    if args.weight != None:
        if len(args.input) != len(args.weight):
            raise RuntimeError("Mismatch in mumber of weight formulas and input sets. If weights are specified, must be equal calls to --weight and --input")

    if args.noBatch == False:
        ROOT.gROOT.SetBatch()

    if args.backend in ["RDF", "PyRDF"]:
        inputSets = []
        for fn, f in enumerate(args.input):
            #convert a list (len(f) > 1) of inputs for a given sample to a vector of strings, an acceptable input type for RDF
            fList = []
            print(f)
            if isinstance(f, list) and len(f) == 1 and ".txt" in f[0] or "list:" in f[0]:
                with open(f[0], "r") as ifl:
                    for line in ifl:
                        fList.append(line.rstrip())
            else:
                fList = f
            print(fList)
            if isinstance(fList, list):
                if args.backend == "RDF":
                    tmp = ROOT.std.vector(str)(len(fList))
                    for sn, subf in enumerate(fList):
                        tmp[sn] = subf
                    inputSets.append(tmp)
                elif args.backend == "PyRDF":
                    inputSets.append(fList)
                else:
                    raise NotImplementedError("Unhandled backend")
            # elif isinstance(fList, list):
            #     inputSets.append(f[0])
            else:
                raise ValueError("Unhandled file input of type {} and value {}".format(type(f), f))
        print(inputSets)
        branchDict = getBranchInfo_RDF(inputSets, whiteList = args.WL, blackList = args.BL)
        if args.stage.lower() == 'report':
            branchReport_RDF(branchDict, reportFile = "branchReport.txt")
        elif args.stage.lower() == 'stats':
            branchStats_RDF(branchDict, reportFile = "branchStats.txt", plotCard = "plotCard_{label}.txt")
        elif args.stage.lower() == 'plots':
            if args.noPlots == False:
                plotDict = makePlotDict(args.plotcards)
                histDict, uniqueHistDict = makeHists_RDF(branchDict, plotDict, eventsKey = "Events", weightsKey = "Weights")
                #Make histogram file if option histOut is called, which optionally contains a non-default filename.
                if args.histOut != None:
                    print("Writing hist file")
                    for sn, flatDict in histDict.items():
                        dictToFile(flatDict, args.histOut, update=True, prefix=nToLabel[sn])
                #Make the function for plotting here
                if args.pdfOut != None:
                    canvasDict = makePlots_RDF(histDict, args.pdfOut)
                
            
    timeReport(prnt=True)

def getBranchInfo_RDF(inputSets, blackList = None, whiteList = None):
    """
    Get dictionary of branch info including fields like SumWeights, SumEvents, BranchTypes, BranchSetsFiltered, etc. See method getBranchInfo_*
    """

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
        # Runs[fn] = ROOT.ROOT.RDataFrame("Runs", f) #Keep standard RDF for this computation
        Runs[fn] = RDF("Runs", f) #Keep standard RDF for this computation
        listOfMetaColumns = [cn for cn in Runs[fn].GetColumnNames()]
        SumEventsBranchName[fn] = [cn for cn in listOfMetaColumns if "genEventCount" in cn.__str__()]
        SumWeightsBranchName[fn] = [cn for cn in listOfMetaColumns if "genEventSumw" in cn and "genEventSumw2" not in cn.__str__()]
        SumWeights2BranchName[fn] = [cn for cn in listOfMetaColumns if "genEventSumw2" in cn.__str__()]
        print(SumEventsBranchName)
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
        if args.weight != None:
            Weights[fn] = "(Float_t)" + args.weight[fn]\
                                            .replace(SumWeights2BranchName[fn][0], str(SumWeights2[fn]))\
                                            .replace("genEventSumw2", str(SumWeights2[fn]))\
                                            .replace(SumWeightsBranchName[fn][0], str(SumWeights[fn]))\
                                            .replace("genEventSumw", str(SumWeights[fn]))\
                                            .replace(SumEventsBranchName[fn][0], str(SumEvents[fn]))\
                                            .replace("genEventCount", str(SumEvents[fn]))
            print("For dataset {}, will define 'diffWeight' = '{}'".format(nToLabel[fn], Weights[fn]))
        else:
            Weights[fn] = "(UInt_t)1"

        Events[fn] = RDF("Events", f).Define("diffWeight", str(Weights[fn]))
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
    triggers = collections.OrderedDict()
    rdf_nodes = branchDict.get("Events")
    event_counts = branchDict.get("SumEvents")
    branches_all = branchDict.get("Branches")
    branch_types_all = branchDict.get("BranchTypesRaw")
    

    procstart['makeHists_RDF(Define)'] = datetime.now()
    histDict = collections.OrderedDict()
    uniqueHistDict = collections.OrderedDict()
    for index in branchDict[eventsKey].keys():
        histDict[index] = collections.OrderedDict()
        uniqueHistDict[index] = collections.OrderedDict()
    for branch, plot in plotDict.items():
        #Catch the devectorized boolean branches in the plot cards:
        if branch[0:4] == "HLT_":
            if not doHLT: continue
        if branch[0:3] == "L1_":
            if not doL1: continue
        if branch[0:4] == "DVB_":
            branch_type = 'ROOT::VecOps::RVec<Bool_t>'
        else:
            branch_type = "UNKNOWN"
        print("{} - {}".format(branch, branch_type))
        if branch_type == 'ROOT::VecOps::RVec<Bool_t>':
            print("Skipping branch that must be devectorized from boolean")
            continue
            # for index, rdf in rdf_nodes.items():
                
            #     if branch in histDict[index]: 
            #         print("Warning, dual definition of branch {} when making Histograms from plotcards. Will keep first branch only.")
            #         continue
            #     if branch not in rdf.GetColumnNames():
            #         print(branch)
            #         uniqueHistDict[index][branch] = rdf.Histo1D(plot, str(branch), "diffWeight")
            #     # print("({}, {}, {})".format(plot, branch, branchDict[weightsKey][index]))
            #     else:
            #         #change the plot name in memory by replacing 
            #         plot_labeled = (plot[0].replace("$INPUT", nToLabel[index]), plot[1], plot[2], plot[3], plot[4])
            #         histDict[index][branch] = rdf.Histo1D(plot_labeled, str(branch), "diffWeight")

            # if branch not in 
            # #need to unpack these (root 6.22 dev)
            # dnode, dcolumns = devectorizeBool(rdf_nodes[index], branch, )
            # for dcolumn in dcolumns:
            #     stats[index][dcolumn] = (dnode.Filter("{dcol} > -1".format(dcol=dcolumn)).(dcolumn, "diffWeight"), branch_type)
        else:
            for index, rdf in rdf_nodes.items():
                if branch in histDict[index]: 
                    print("Warning, dual definition of branch {} when making Histograms from plotcards. Will keep first branch only.")
                    continue
                if branch not in branchDict["BranchSetsFiltered"][index]:
                    print(branch)
                    uniqueHistDict[index][branch] = rdf.Histo1D(plot, str(branch), "diffWeight")
                # print("({}, {}, {})".format(plot, branch, branchDict[weightsKey][index]))
                else:
                    #change the plot name in memory by replacing 
                    plot_labeled = (plot[0].replace("$INPUT", nToLabel[index]), plot[1], plot[2], plot[3], plot[4])
                    histDict[index][branch] = rdf.Histo1D(plot_labeled, str(branch), "diffWeight")
        # elif branch_type == 'ULong64_t':
        #     #run number
        #     pass
        # else:
        #     print("Skipping unhandled branch (name={}, type={})".format(branch, branch_type))

    procfinish['makeHists_RDF(Define)'] = datetime.now()
    procstart['makeHists_RDF(Run)'] = datetime.now()
    for index, rdf in branchDict[eventsKey].items():
        triggers[index] = ROOT.AddProgressBar(ROOT.RDF.AsRNode(rdf), max(100, int(event_counts[index]/50000)), int(event_counts[index]))

    print("Starting event loop...")
    for index, count in triggers.items():
        print(count.GetValue())
    # counts = map(lambda x: x.GetValue(), triggers.values())
    for index, rdf in branchDict[eventsKey].items():
        for branch, hist in histDict[index].items():
            histDict[index][branch] = hist.GetPtr().Clone()
        for branch, hist in uniqueHistDict[index].items():
            histDict[index][branch] = hist.GetPtr().Clone()
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

def branchStats_RDF(branchDict, reportFile = "branchStats.txt", plotCard="plotCard_{label}.txt", doHLT=False, doL1=False):
    procstart['branchStats_RDF'] = datetime.now()
    uniquePairs = [(a,b) for a in branchDict["indices"] for b in branchDict["indices"] if a < b]

    stats = collections.OrderedDict()
    triggers = collections.OrderedDict()
    rdf_nodes = branchDict.get("Events")
    event_counts = branchDict.get("SumEvents")
    branches_all = branchDict.get("Branches")
    branch_types_all = branchDict.get("BranchTypesRaw")
    for index in branchDict.get("indices"):
        label = nToLabel[index]
        stats[index] = collections.OrderedDict()
        # triggers[index] = rdf_nodes[index].Count()
        triggers[index] = ROOT.AddProgressBar(ROOT.RDF.AsRNode(rdf_nodes[index]), max(100, int(event_counts[index]/50000)), int(event_counts[index]))
        branches = branches_all[index]
        branch_types = branch_types_all[index]
        for branch in branches:
            branch_type = branch_types[branch]
            if branch_type == 'Bool_t':
                if branch[0:4] == "HLT_":
                    if not doHLT: continue
                if branch[0:3] == "L1_":
                    if not doL1: continue
                stats[index][branch] = (rdf_nodes[index].Stats(branch, "diffWeight"), branch_type)
            elif branch_type in ['Int_t', 'UChar_t', 'UInt_t', 'Float_t', 'double']:
                stats[index][branch] = (rdf_nodes[index].Stats(branch, "diffWeight"), branch_type)
            elif branch_type in ['ROOT::VecOps::RVec<Int_t>', 'ROOT::VecOps::RVec<UChar_t>', 'ROOT::VecOps::RVec<Float_t>']:
                #Potentially unpack these
                stats[index][branch] = (rdf_nodes[index].Stats(branch, "diffWeight"), branch_type)
            elif branch_type == 'ROOT::VecOps::RVec<Bool_t>':
                #need to unpack these (root 6.22 dev)
                dnode, dcolumns = devectorizeBool(rdf_nodes[index], branch)
                for dcolumn in dcolumns:
                    stats[index][dcolumn] = (dnode.Filter("{dcol} > -1".format(dcol=dcolumn)).Stats(dcolumn, "diffWeight"), branch_type)
            elif branch_type == 'ULong64_t':
                #run number
                pass
            else:
                print("Skipping unhandled branch (name={}, type={})".format(branch, branch_type))
    for index, count in triggers.items():
        print(count.GetValue())
    final_stats = collections.OrderedDict()
    for index, stats_dict in stats.items():
        label = nToLabel[index]
        final_stats[index] = collections.OrderedDict()
        plotcard_name = copy.copy(plotCard).format(label=label)
        with open(plotcard_name, "w") as pc:
            print("Filling plotcard {}".format(plotcard_name))
            for branch , branch_stats in stats_dict.items():
                temp = branch_stats[0].GetValue()
                if "Bool" in branch_stats[1]:
                    plot = [str(branch), str(2), str(0), str(2)]
                    final_stats[index][branch] =  [branch, 0, temp.GetMean(), 1, 0, 0]
                elif "int" in branch_stats[1].lower():
                    plot = [str(branch), str(100), str(temp.GetMin()), str(temp.GetMax()+1)]
                    final_stats[index][branch] = [branch, temp.GetMin(), temp.GetMean(), temp.GetMax(), temp.GetM2(), temp.GetRMS()]
                else:
                    plot = [str(branch), str(100), str(temp.GetMin()), str(temp.GetMax())]
                    final_stats[index][branch] = [branch, temp.GetMin(), temp.GetMean(), temp.GetMax(), temp.GetM2(), temp.GetRMS()]
                pc.write("    ".join(plot) + "\n")
    with open(reportFile, "w") as o:
        for indexA, indexB in uniquePairs:
            labelA = nToLabel[indexA]
            labelB = nToLabel[indexB]
            # inCommon = branchDict["BranchSets"][indexA].intersection(branchDict["BranchSets"][indexB])
            # onlyInA = branchDict["BranchSets"][indexA] - branchDict["BranchSets"][indexB]
            # onlyInB = branchDict["BranchSets"][indexB] - branchDict["BranchSets"][indexA]
            inCommon = set(final_stats[indexA].keys()).intersection(set(final_stats[indexB].keys()))
            onlyInA = set(final_stats[indexA].keys()) - set(final_stats[indexB].keys())
            onlyInB = set(final_stats[indexB].keys()) - set(final_stats[indexA].keys())
            o.write("==================================\n")
            o.write("Report on inputs {iA} and {iB}:\n    files[{iA}]: {fA}\n    files[{iB}]: {fB}\n"\
                    "\n    SumEvents[{iA}]: {seA}\n    SumEvents[{iB}]: {seB}"\
                    "\n    SumWeights[{iA}]: {swA}\n    SumWeights[{iB}]: {swB}\n"\
                    .format(iA = labelA, iB = labelB, fA = branchDict["Files"][indexA], fB = branchDict["Files"][indexB],
                            seA = branchDict["SumEvents"][indexA], seB = branchDict["SumEvents"][indexB],
                            swA = branchDict["SumWeights"][indexA], swB = branchDict["SumWeights"][indexB]))
            o.write("\n======== Common Branches % Change ({} - {})/{}========\n".format(labelA, labelB, labelA))
            for b in sorted(inCommon):
                if final_stats[indexA].get(b, None) is None or final_stats[indexB].get(b, None) is None:
                    o.write("{branch} Stats not computed due to type or name".format(branch=b))
                    continue
                # print("{} - {}".format(b, final_stats[indexA][b]))
                printout = "{branch} Min: {cminN}/{cminD} Mean: {cmeanN}/{cmeanD} Max: {cmaxN}/{cmaxD} Moment2: {cmomN}/{cmomD} RMS: {crmsN}/{crmsD}\n".format(
                    branch=b,
                    cminN=(final_stats[indexA][b][1] - final_stats[indexB][b][1]),
                    cminD=final_stats[indexA][b][1],
                    cmeanN=(final_stats[indexA][b][2] - final_stats[indexB][b][2]),
                    cmeanD=final_stats[indexA][b][2],
                    cmaxN=(final_stats[indexA][b][3] - final_stats[indexB][b][3]),
                    cmaxD=final_stats[indexA][b][3],
                    cmomN=(final_stats[indexA][b][4] - final_stats[indexB][b][4]),
                    cmomD=final_stats[indexA][b][4],
                    crmsN=(final_stats[indexA][b][5] - final_stats[indexB][b][5]),
                    crmsD=final_stats[indexA][b][5])
                o.write(printout)
            o.write("\n======== Branches only in {iA} ========\n".format(iA = labelA))
            for b in sorted(onlyInA): 
                if final_stats[indexA].get(b, None) is None:
                    o.write("{branch} Stats not computed due to type or name".format(branch=b))
                    continue
                printout = "{branch} Min: {cmin} Mean: {cmean} Max: {cmax} Moment2: {cmom} RMS: {crms}\n".format(
                    branch=b,
                    cmin=final_stats[indexA][b][1],
                    cmean=final_stats[indexA][b][2],
                    cmax=final_stats[indexA][b][3],
                    cmom=final_stats[indexA][b][4],
                    crms=final_stats[indexA][b][5])
                o.write(printout)
            o.write("\n======== Branches only in {iB} ========\n".format(iB = labelB))
            for b in sorted(onlyInB): 
                if final_stats[indexB].get(b, None) is None:
                    o.write("{branch} Stats not computed due to type or name".format(branch=b))
                    continue
                printout = "{branch} Min: {cmin} Mean: {cmean} Max: {cmax} Moment2: {cmom} RMS: {crms}\n".format(
                    branch=b,
                    cmin=final_stats[indexB][b][1],
                    cmean=final_stats[indexB][b][2],
                    cmax=final_stats[indexB][b][3],
                    cmom=final_stats[indexB][b][4],
                    crms=final_stats[indexB][b][5])
                o.write(printout)
    procfinish['branchStats_RDF'] = datetime.now()
# GetN()
# GetNeff()
# GetM2()
# GetMean()
# GetMeanErr()
# GetRMS()
# GetVar()
# GetW()
# GetW2()
# GetMin()
# GetMax()


def makePlots_RDF(histDict, pdfFile, colorList = [ROOT.kBlack, ROOT.kRed, ROOT.kGreen, ROOT.kAzure]):
    procstart['makePlots_RDF'] = datetime.now()
    last = len(histDict[0].keys()) - 1
    for bn, branch in enumerate(histDict[0].keys()):
        c, upperPads, lowerPads = createCanvasPads(branch, doRatio=True, setXGrid=True, setYGrid=False,
                                                   nXPads=1, topFraction=0.7, xpixels=800, ypixels=800)
        upperPads[0].cd()
        for sn, sample in enumerate(histDict.keys()):
            print("{}_{}".format(branch, sample))
            theClone = "".format(histDict[sample][branch].GetName()).replace("h_", "")
            h = histDict[sample][branch].Clone(theClone)
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

def devectorizeBool(node, column_name, length=10):
    derived_node = node
    column_names = node.GetColumnNames()
    derived_columns = []
    for i in xrange(length):
        col_name = "DVB_{col}_bit{it}".format(col=column_name, it=i+1)
        if col_name not in column_names:
            derived_node = derived_node.Define(col_name, "Char_t ret = ({col}.size() > {it} ? (Char_t){col}.at({it}) : (Char_t)(-1)); return ret;".format(col=column_name, it=i))
        derived_columns.append(col_name)
    return (derived_node, derived_columns)


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
    
    

if __name__ == '__main__':
    main()

