import argparse
import glob
import ROOT

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='script to check the generator sum of weights for all files ending in .root or .empty inside a folder, specified with --Directory')

    parser.add_argument('--Directory', dest='Directory', action='store', type=str, default="./",
                        help='Directory specifying the file locations')
    args = parser.parse_args()
    
    rfiles = glob.glob(args.Directory + "/*.root")
    efiles = glob.glob(args.Directory + "/*.empty")

    tchains = dict()
    results = dict()
    for variation, files in [("empty", efiles),
                             ("filled", rfiles),
                             ("all", efiles + rfiles)]:
    
        tchains[variation] = ROOT.TChain("Runs")
        for f in files:
            tchains[variation].Add(f)
        results[variation] = ROOT.ROOT.RDataFrame(tchains[variation]).Sum("genEventSumw")
        results[variation] = results[variation].GetValue()
    print(results)
        
