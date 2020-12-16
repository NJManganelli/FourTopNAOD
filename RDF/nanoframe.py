import argparse
from FourTopNAOD.RDF.tools.toolbox import getFiles
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def bookSnapshot(input_df, filename, columnList, lazy=True, treename="Events", mode="RECREATE", compressionAlgo="LZ4", compressionLevel=6, splitLevel=99, debug=False):
    if columnList is None:
        raise RuntimeError("Cannot take empty columnList in bookSnapshot")
    elif isinstance(columnList, str) or 'vector<string>' in str(type(columnList)):
        columns = columnList #regexp case or vector of strings
    elif isinstance(columnList, list):
        columns = ROOT.std.vector(str)()
        for col in columnList:
            columns.push_back(col)
    elif "<class cppyy.gbl.std.vector<string>" in str(type(columnList)):
        columns = columnList
    else:
        raise RuntimeError("Cannot handle columnList of type {} in bookSnapshot".format(type(columnList)))
        
    Algos = {"ZLIB": 1,
             "LZMA": 2,
             "LZ4": 4,
             "ZSTD": 5
         }
    sopt = ROOT.RDF.RSnapshotOptions(mode, Algos[compressionAlgo], compressionLevel, 0, splitLevel, True) #lazy is last option
    if lazy is False:
        sopt.fLazy = False
    print("snapshot columns", columns)
    handle = input_df.Snapshot(treename, filename, columns, sopt)

    return handle


parser = argparse.ArgumentParser(description='nanovisor.py is a lightweight tool leveraging root\'s RDataFrame to quickly make skims and very basic plots or stats')
parser.add_argument('--input', dest='input', action='store', type=str, required=True,
                    help='input path, in the form accepted by getFiles method')
parser.add_argument('--nThreads', dest='nThreads', action='store', type=int, default=1, #nargs='?', const=0.4,
                    help='number of threads for implicit multithreading (0 or 1 to disable)')
# parser.add_argument('--defines', dest='defines', action='store', nargs='*', type=str,
#                     help='list of new variables with syntax variable_name=variable_definition, where both are valid C++ variable names and code, respectively')
# parser.add_argument('--filters', dest='filters', action='store', nargs='*', type=str,
#                     help='list of filters with syntax filter_name=filter_cut, where the former is any text and the latter is valid C++ code')
parser.add_argument('--keep', dest='keep', action='store', nargs='*', type=str,
                    help='list of branch names to keep in output files, does not accept wildcards')
parser.add_argument('--postfix', dest='postfix', action='store', type=str, default="_Skim",
                    help='name to append to root filenames')
# parser.add_argument('--merge', dest='merge', action='store_true',
#                     help='Merge output files immediately on input, which may be susceptible to problems if requested branches do not align')
# parser.add_argument('--haddnano', dest='haddnano', action='store_true',
#                     help='Merge output files at the end by calling haddnano.py, which can forward/back fill non-aligned branches in the NanoAOD format')

args = parser.parse_args()

if args.nThreads > 1:
    print("Enabling multithreading. Event order will not be preserved for final skims.")
    ROOT.ROOT.EnableImplicitMT(nThreads)
print(args.input)
if args.input.startswith("dbs:") or args.input.startswith("glob:") or args.input.startswith("list:"):
    fileList = getFiles(query=args.input, outFileName=None)
else:
    fileList = [args.input]
print("inputs: ", fileList)
print("nThreads: ", args.nThreads)
print("keep list: ", args.keep)
print("postfix: ", args.postfix)

for fn in fileList:
    foName = fn.replace(".root", args.postfix + ".root")
    rdf = ROOT.ROOT.RDataFrame("Events", fn)
    rdfFinal = rdf #Placeholder
    columnList = [str(c) for c in rdf.GetColumnNames() if str(c) in args.keep]
    print("columns to keep: ", columnList)
    snaphandle = bookSnapshot(rdfFinal, foName, columnList, lazy=False, treename="Events", mode="RECREATE", compressionAlgo="LZMA", compressionLevel=9, splitLevel=99, debug=False)

    #Handle the rest of the trees
    fi = ROOT.TFile.Open(fn, "read")
    treeNames = [str(ll.GetName()) for ll in fi.GetListOfKeys() if ll.GetClassName() in ['TTree']]
    print("TTrees: ", treeNames)
    fo = ROOT.TFile.Open(foName, "update")
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
    
# rdf = ROOT.ROOT.RDataFrame("Events", 
keepBranches = args.keep
