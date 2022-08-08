import os
import argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main(inFile, findReplace):
    try:
        f = ROOT.TFile.Open(inFile, "UPDATE")
        k = [kk.GetName() for kk in f.GetListOfKeys() if kk.GetClassName() in ['TH1I', 'TH1F', 'TH1D', 'TH2I', 'TH2F', 'TH2D', 'TH3I', 'TH3F', 'TH3D']]
        h = dict()
        for kk in k:
            h[kk] = f.Get(kk)
            name = h[kk].GetName()
            for fR in findReplace:
                findKey, replaceValue = fR.split("==")
                name = name.replace(findKey, replaceValue)
            h[kk].SetName(name)
            h[kk].Write()
        f.Close()
    except:
        print("Failed")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Determine binning automatically for categorized histograms using a particular subset of processes')
    parser.add_argument('--inputFile', dest='inputFile', action='store', default=None, type=str,
                        help='Path to the input file')
    parser.add_argument('--findReplace', dest='findReplace', action='store', default=None, type=str, nargs='*',
                        help='VALUE1==VALUE2 pairs to replace when rewriting names')
    args = parser.parse_args()
    main(args.inputFile, args.findReplace)
