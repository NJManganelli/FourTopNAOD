#!/bin/env/python3
import os
import pdb
import argparse
import ROOT

def main(input1, input2, Ch22Maximum, KSMinimum, sort_key, maxResults, keyword, verbose=False):
    if not os.path.isfile(input1):
        raise IOError("Input 1 ({}) does not exist".format(input1))
    if not os.path.isfile(input2):
        raise IOError("Input 2 ({}) does not exist".format(input2))
    f1 = ROOT.TFile.Open(input1, "read")
    f2 = ROOT.TFile.Open(input2, "read")
    k1 = [kk.GetName() for kk in f1.GetListOfKeys() if kk.GetClassName() in ['TH1I', 'TH1F', 'TH1D', 'TH2I', 'TH2F', 'TH2D', 'TH3I', 'TH3F', 'TH3D']]
    k2 = [kk.GetName() for kk in f2.GetListOfKeys() if kk.GetClassName() in ['TH1I', 'TH1F', 'TH1D', 'TH2I', 'TH2F', 'TH2D', 'TH3I', 'TH3F', 'TH3D']]
    kNotKeyworded = []
    if keyword is not None:
        k1 = [kk for kk in k1 if keyword in kk]
        k2 = [kk for kk in k2 if keyword in kk]
        kNotKeyworded = list(set([kk for kk in k1 + k2 if keyword not in kk]))
    kOnlyInOne = set(k1) - set(k2)
    kOnlyInTwo = set(k2) - set(k1)
    kInBoth = set(k1).intersection(set(k2))
    print("Histogram keys...\n\tOnly in input1: {}\n\tOnly in input2: {}\n\tIn common: {}\n\tKeyword not found: {}".format(len(kOnlyInOne), len(kOnlyInTwo), len(kInBoth), len(kNotKeyworded)))
    print("Running KS and Chi2 tests on matching histograms")

    KSTestResults = {}
    Chi2TestResults = {}
    IntegralResults = {}
    for kk in kInBoth:
        KSTestResults[kk] = f1.Get(kk).KolmogorovTest(f2.Get(kk), "U O N")
        Chi2TestResults[kk] = f1.Get(kk).Chi2Test(f2.Get(kk), "WW OF UF Chi2/NDF")
        IntegralResults[kk] = (f1.Get(kk).Integral() - f2.Get(kk).Integral())/max(f1.Get(kk).Integral(), 1e-29)
    Results = [(kk, KSTestResults[kk], Chi2TestResults[kk], IntegralResults[kk]) for kk in kInBoth]
    sort_function = None
    if sort_key == 'Chi2':
        Results = sorted(Results, key=lambda k: k[2], reverse=True)
    elif sort_key == 'KS':
        Results = sorted(Results, key=lambda k: k[1], reverse=False)
    elif sort_key.lower() in ['norm', 'integral', 'area']:
        Results = sorted(Results, key=lambda k: k[3], reverse=True)
    elif sort_key.lower() in ['absnorm', 'absintegral', 'absarea']:
        Results = sorted(Results, key=lambda k: abs(k[3]), reverse=True)
    elif sort_key.lower() == 'name':
        Results = sorted(Results, key=lambda k: k[0], reverse=False)

    maxToPrint = min(maxResults, len(Results))
    for result in Results[:maxToPrint]:
        print("KS: ", result[1], " Chi2/NDoF: ", result[2], " Integral %diff: ", result[3], " Histogram: ", result[0])
# doCSV = False
# if doCSV:
#     print("branch,KS,CHI2/NDF")
# for a, b in z:
#     branch = "{}".format(a[0].replace("h_", "").replace("_v6p1", "").replace("_v6", ""))
#     if doCSV:
#         print("{},{:1.7g},{:1.7g}".format(branch, a[1], b[1]))
#     else:
#         print("{:50s}\tKS: {:10.7g}\tChi2/NDF: {:10.7g}".format(branch, a[1], b[1]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Determine binning automatically for categorized histograms using a particular subset of processes')
    parser.add_argument('--KSMinimum', dest='KSMinimum', action='store', type=float, default=0.9999,
                        help='Minimal KS test value, histogram pairs with lower will be flagged')
    parser.add_argument('--Chi2Maximum', dest='Chi2Maximum', action='store', type=float, default=float(1e-4),
                        help='Maximal Chi2 test value, histogram pairs with higher will be flagged')
    parser.add_argument('--input1', dest='input1', action='store', default=None, type=str,
                        help='Path to the input1 file')
    parser.add_argument('--input2', dest='input2', action='store', default=None, type=str,
                        help='Path to the input2 file')
    parser.add_argument('--sort', dest='sort', action='store', choices=['KS', 'Chi2', 'Name', 'name', 'Integral', 'Area', 'Norm', 'AbsIntegral', 'AbsNorm', 'AbsArea'], default='Chi2', type=str,
                        help='Sorting key, defaulting to descending Chi2 test values; KS sorts in ascending order; Integral/Area/Norm are synonyms and sort in descending order')
    parser.add_argument('--maxResults', dest='maxResults', action='store', default=10, type=int,
                        help='Max number of results to print out')
    parser.add_argument('--keyword', dest='keyword', action='store', default=None, type=str,
                        help='Keyword to search for in histogram names, will skip any that do not contain this string, if invoked')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')

    #Parse the arguments
    args = parser.parse_args()
    verbose = args.verbose
    main(args.input1, args.input2, args.Chi2Maximum, args.KSMinimum, args.sort, args.maxResults, args.keyword, verbose=verbose)
