import os
import subprocess
import argparse
import time
from FourTopNAOD.RDF.tools.toolbox import getFiles
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

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

def prefetchFile(fname, longTermCache=False, verbose=True):
    #Taken from the nanoAOD-tools, with a few python3-izations and more functional form
    tmpdir = os.environ['TMPDIR'] if 'TMPDIR' in os.environ else "/tmp/{}".format(os.getuname())
    if not fname.startswith("root://"):
        return fname, False
    rndchars = "".join([hex(ord(str(i)[0:1]))[2:] for i in os.urandom(
        8)]) if not longTermCache else "long_cache-id{:d}-{:s}"\
        .format((os.getuid(), hashlib.sha1(fname).hexdigest()))
    localfile = "{:s}/{:s}-{:s}.root"\
                .format(tmpdir, os.path.basename(fname).replace(".root", ""), rndchars)
    if longTermCache and os.path.exists(localfile):
        if verbose:
            print("Filename %s is already available in local path {} "\
                .format((fname, localfile)))
        return localfile, False
    try:
        if verbose:
            print("Filename {:s} is remote, will do a copy to local path {}"\
                  .format(fname, localfile))
        start = time.perf_counter()
        subprocess.check_output(["xrdcp", "-f", "-N", fname, localfile])
        if verbose:
            print("Time used for transferring the file locally: {:.2f}s"\
                  .format(time.perf_counter() - start))
        return localfile, (not longTermCache)
    except:
        if verbose:
            print("Error: could not save file locally, will run from remote")
        if os.path.exists(localfile):
            if verbose:
                print("Deleting partially transferred file {}".format(localfile))
            try:
                os.unlink(localfile)
            except:
                pass
        return fname, False

def getResults(node):
    return node.GetValue()
class dummyResult:
    def __init__(self):
        pass
    def GetValue(self):
        return "Dummy Result"

def bookSnapshot(input_df, filename, columnList, lazy=True, treename="Events", mode="RECREATE", compressionAlgo="LZ4", compressionLevel=6, splitLevel=99, debug=False):
    if columnList is None:
        columns = input_df.GetColumnNames()
        # raise RuntimeError("Cannot take empty columnList in bookSnapshot")
    elif isinstance(columnList, str) or "<class cppyy.gbl.std.vector<string>" in str(type(columnList)) or 'vector<string>' in str(type(columnList)):
        columns = columnList #regexp case or vector of strings
    elif isinstance(columnList, list):
        columns = ROOT.std.vector(str)()
        for col in columnList:
            columns.push_back(col)
    else:
        raise RuntimeError("Cannot handle columnList of type {} in bookSnapshot".format(type(columnList)))
        
    Algos = {"Inherit": -1,
             "UseGlobal": 0,
             "ZLIB": 1,
             "LZMA": 2,
             "OldCompressionAlgo": 3,
             "LZ4": 4,
             "ZSTD": 5,
             "Undefined": 6
         }
    sopt = ROOT.RDF.RSnapshotOptions(mode, Algos[compressionAlgo], compressionLevel, 0, splitLevel, True) #lazy is last option
    if lazy is False:
        sopt.fLazy = False
    handle = input_df.Snapshot(treename, filename, columns, sopt)

    return handle


parser = argparse.ArgumentParser(description='nanovisor.py is a lightweight tool leveraging root\'s RDataFrame to quickly make skims and very basic plots or stats')
parser.add_argument('--input', dest='input', action='store', type=str, required=True,
                    help='input path, in the form accepted by getFiles method')
parser.add_argument('--nThreads', dest='nThreads', action='store', type=int, default=1, #nargs='?', const=0.4,
                    help='number of threads for implicit multithreading (0 or 1 to disable)')
parser.add_argument('--simultaneous', dest='simultaneous', action='store', type=int, default=1, #nargs='?', const=0.4,
                    help='simultaneous graphs to process (recommendation for network-accessed files: 3 or less)')
parser.add_argument('--define', dest='defines', action='append', type=str, #nargs='*'
                    help='list of new variables with syntax variable_name>==>variable_definition, where both are valid C++ variable names and code, respectively')
parser.add_argument('--filter', dest='filters', action='append', type=str, #nargs='*', 
                    help='list of filters with syntax filter_name>==>filter_cut, where the former is any text and the latter is valid C++ code')
parser.add_argument('--keep', dest='keep', action='store', nargs='*', type=str, default=None,
                    help='list of branch names to keep in output files, does not accept wildcards')
parser.add_argument('--postfix', dest='postfix', action='store', type=str, default="_Skim",
                    help='name to append to root filenames')
parser.add_argument('--write', dest='write', action='store_true',
                    help='Write output files')
parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                    help='Overwrite already completed output files, these will be skipped otherwise')
parser.add_argument('--redirector', dest='redir', action='store', type=str, nargs='?', default=None, const='root://cms-xrd-global.cern.ch/',
                    help='redirector for XRootD, such as "root://cms-xrd-global.cern.ch/"')
parser.add_argument('--outdir', dest='outdir', action='store', type=str, default='skims/',
                    help='directory to place output in')
parser.add_argument('--prefetch', dest='prefetch', action='store_true',
                    help='Prefetch files locally before processing and then deleting upon successful completion')
parser.add_argument('--longTermCache', dest='longTermCache', action='store_true',
                    help='LongTermCache files, preventing deletion of source files transferred locally')
# parser.add_argument('--merge', dest='merge', action='store_true',
#                     help='Merge output files immediately on input, which may be susceptible to problems if requested branches do not align')
# parser.add_argument('--haddnano', dest='haddnano', action='store_true',
#                     help='Merge output files at the end by calling haddnano.py, which can forward/back fill non-aligned branches in the NanoAOD format')

args = parser.parse_args()

if args.nThreads > 1:
    print("Enabling multithreading. Event order will not be preserved for final skims.")
    ROOT.ROOT.EnableImplicitMT(args.nThreads)
print(args.input)
print("filters/cuts: ", args.filters)
print("defines: ", args.defines)
if args.input.startswith("dbs:") or args.input.startswith("glob:") or args.input.startswith("list:"):
    fileList = getFiles(query=args.input, redir=args.redir, outFileName=None)
else:
    fileList = [args.input]
print("Inputs: ")
for fn in fileList:
    print("\t{}".format(fn))
print("Output directory: ", args.outdir)
if args.write and not os.path.isdir(args.outdir):
    os.makedirs(args.outdir)

print("nThreads: ", args.nThreads)
print("Simultaneous graph executions: ", args.simultaneous)
assert int(args.nThreads/args.simultaneous) >= 1, "nThreads/simultaneous must be >= 1"
print("Keep list: ", args.keep)
print("Postfix: ", args.postfix)

tchains = {}
tcmeta = {}
rdf_bases = {}
rdf_finals = {}
booktriggers = {}
handles = []
results = []
foNameDict = {}
print("Processing {} files per batch".format(args.simultaneous))
for x in range(0, len(fileList), args.simultaneous):
    print("")
    for fnumber, fn in enumerate(fileList[x:min(x + args.simultaneous, len(fileList))]):
        fnumber += x
        if fn not in foNameDict.keys(): 
            foNameDict[fn] = {}
        foNameDict[fn]["final"] = os.path.join(args.outdir, fn.split("/")[-1].replace(".root", args.postfix + ".root"))
        foNameDict[fn]["temp"] = os.path.join(args.outdir, fn.split("/")[-1].replace(".root", "_temp" + ".root"))
        #Skip files that are finished unless overwrite is requested
        if os.path.isfile(foNameDict[fn]["final"]) and not args.overwrite:
            #Put a dummy result in the list to keep array indexing consistent
            if args.write:
                handles.append(dummyResult())
            foNameDict[fn]["source"] = "Done"
            continue
        foNameDict[fn]["source"], requiresDeletion = prefetchFile(fn, longTermCache=args.longTermCache, verbose=True) if (args.prefetch or args.longTermCache) else (fn, False)
        print("temp output {}: {}".format(fnumber, foNameDict[fn]["temp"]))
        tchains[fn] = ROOT.TChain("Events")
        # tcmeta[fn] = ROOT.TChain("Runs")
        tchains[fn].Add(str(foNameDict[fn]["source"]))
        # tcmeta[fn].Add(str(foNameDict[fn]["source"]))
        rdfEntries = tchains[fn].GetEntries()
        rdf_bases[fn] = ROOT.ROOT.RDataFrame(tchains[fn])
        booktriggers[fn] = ROOT.AddProgressBar(ROOT.RDF.AsRNode(rdf_bases[fn]), 
                                               2000, int(rdfEntries))
        # if checkMeta:
        #     tcmeta.Add(str(vfe))
        # rdf = ROOT.ROOT.RDataFrame("Events", fn)
        rdfFinal = rdf_bases[fn] #Placeholder
        if args.defines is not None:
            for define in args.defines:
                var, defn = define.split(">==>")
                rdfFinal = rdfFinal.Define(var, defn)
        if args.filters is not None:
            for cut in args.filters:
                name, defn = cut.split(">==>")
                rdfFinal = rdfFinal.Filter(defn, name)
        rdf_finals[fn] = rdfFinal
        columnList = [str(c) for c in rdf_finals[fn].GetColumnNames() if str(c) in args.keep] if args.keep is not None else None
        if args.write:
            snaphandle = bookSnapshot(rdf_finals[fn], foNameDict[fn]["temp"], columnList, lazy=True, treename="Events", mode="RECREATE", compressionAlgo="LZMA", compressionLevel=9, splitLevel=99, debug=False)
            # booktrigger = ROOT.AddProgressBar(ROOT.RDF.AsRNode(), 
            #                                   2000, int(metainfo[name]["totalEvents"]))
            handles.append(snaphandle)
    print("Writing results for files {} through {}".format(x, min(x + args.simultaneous, len(fileList))-1))
    results += list(map(getResults, handles[x:min(x + args.simultaneous, len(fileList))]))
    print("\nWriting meta information to files.")
    for fnumber, fn in enumerate(fileList[x:min(x + args.simultaneous, len(fileList))]):
        if os.path.isfile(foNameDict[fn]["final"]) and not args.overwrite:
            continue
        if args.write:
            #Handle the rest of the trees
            fi = ROOT.TFile.Open(foNameDict[fn]["source"], "read")
            treeNames = [str(ll.GetName()) for ll in fi.GetListOfKeys() if ll.GetClassName() in ['TTree']]
            # print("TTrees: ", treeNames)
            fo = ROOT.TFile.Open(foNameDict[fn]["temp"], "update")
            fo.cd()
            for treeName in treeNames:
                if treeName != "Events": #Handle the events tree using RDataFrame
                    fi.cd()
                    tree = fi.Get(treeName)
                    fo.cd()
                    treeclone = tree.CloneTree(-1, "fast")# if goFast else "")
                    treeclone.Write()
            fi.Close()
            fo.Close()
            try:
                os.rename(foNameDict[fn]["temp"], foNameDict[fn]["final"])
            except:
                print("Rename of file {} to {} failed, continuing".format(foNameDict[fn]["temp"], foNameDict[fn]["final"]))
    #Do NOT release foNameDict entries, they are required for final meta info insertion
    # rdf_finals = {}; rdf_bases = {}; tchains = {} ; tcmeta = {} #Release pointers to objects, permit GC?
    for fnumber, fn in enumerate(fileList[x:min(x + args.simultaneous, len(fileList))]):
        if fn in booktriggers.keys():
            del booktriggers[fn]
            del rdf_bases[fn]
            del tchains[fn]
        # del tcmeta[fn]
        if args.prefetch and not args.longTermCache and os.path.isfile(foNameDict[fn]["source"]):
            try:
                os.unlink(foNameDict[fn]["source"])
            except:
                print("Could not remove prefetched source file {}".format(foNameDict[fn]["source"]))
print("Done")
