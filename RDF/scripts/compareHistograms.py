#!/bin/env/python3
import os
import pdb
import argparse
from tqdm import tqdm
import ROOT

def main(input1, input2, Ch22Maximum, KSMinimum, sort_key, maxResults, keywords, findReplace, skipNull, verbose=False):
    if not os.path.isfile(input1):
        raise IOError("Input 1 ({}) does not exist".format(input1))
    if not os.path.isfile(input2):
        raise IOError("Input 2 ({}) does not exist".format(input2))
    f1 = ROOT.TFile.Open(input1, "read")
    f2 = ROOT.TFile.Open(input2, "read")
    k1 = [kk.GetName() for kk in tqdm(f1.GetListOfKeys()) if kk.GetClassName() in ['TH1I', 'TH1F', 'TH1D', 'TH2I', 'TH2F', 'TH2D', 'TH3I', 'TH3F', 'TH3D']]
    k2 = [kk.GetName() for kk in tqdm(f2.GetListOfKeys()) if kk.GetClassName() in ['TH1I', 'TH1F', 'TH1D', 'TH2I', 'TH2F', 'TH2D', 'TH3I', 'TH3F', 'TH3D']]
    kAll = k1 + k2
    kNotKeyworded = []
    keywords2 = keywords
    if keywords is not None and isinstance(keywords, list) and len(keywords) > 0:
        if isinstance(findReplace, list):
            keywords2 = []
            for keyword in keywords:
                keyword2 = "{}".format(keyword)
                for mapping in findReplace:
                    keyword2 = keyword2.replace(mapping.split("==")[0], mapping.split("==")[1])
                keywords2.append(keyword2)
        print(keywords, keywords2)
        k1 = dict([(kk, kk) for kk in tqdm(k1) if all([keyword in kk for keyword in keywords])])
        k2temp = dict([(kk, kk) for kk in tqdm(k2) if all([keyword in kk for keyword in keywords2])])
        if isinstance(findReplace, list):
            k2 = dict()
            for key, value in k2temp.items():
                key2 = "{}".format(key)
                for mapping in findReplace:
                    #The mapping is reversed here, to get back to equivalence of input1
                    key2 = key2.replace(mapping.split("==")[1], mapping.split("==")[0])
                k2[key2] = value
        else:
            k2 = k2temp
    else:
        k1 = dict([(kk, kk) for kk in tqdm(k1)])
        k2 = dict([(kk, kk) for kk in tqdm(k2)])
    kAll = list(k1.keys()) + list(k2.keys())
    kNotKeyworded = list(set([kk for kk in tqdm(kAll) if kk not in list(k1.keys()) + list(k2.keys())]))
    kOnlyInOne = set(k1.keys()) - set(k2.keys())
    kOnlyInTwo = set(k2.keys()) - set(k1.keys())
    kInBoth = set(k1.keys()).intersection(set(k2.keys()))
    print("Histogram keys...\n\tOnly in input1: {}\n\tOnly in input2: {}\n\tIn common: {}\n\tKeywords not found: {}".format(len(kOnlyInOne), len(kOnlyInTwo), len(kInBoth), len(kNotKeyworded)))
    print("Running KS and Chi2 tests on matching histograms")

    KSTestResults = {}
    Chi2TestResults = {}
    IntegralResults = {}
    Integrals1 = {}
    Integrals2 = {}
    NullResults = {}
    for kk in tqdm(kInBoth):
        norm1 = f1.Get(k1[kk]).Integral()
        norm2 = f2.Get(k2[kk]).Integral()
        if skipNull:
            thresh = 1e-25
            if abs(norm1) < thresh:
                if abs(norm2) < thresh:
                    NullResults[kk] = "Both"
                else:
                    NullResults[kk] = "input1"
                continue
            elif abs(norm2) < thresh:
                NullResults[kk] = "input2"
                continue
        KSTestResults[kk] = f1.Get(k1[kk]).KolmogorovTest(f2.Get(k2[kk]), "U O N")
        Chi2TestResults[kk] = f1.Get(k1[kk]).Chi2Test(f2.Get(k2[kk]), "WW OF UF Chi2/NDF")
        IntegralResults[kk] = (norm2 - norm1)/max(norm1, 1e-29)
        Integrals1[kk] = norm1
        Integrals2[kk] = norm2
    if skipNull:
        print("{} results had null norms and were skipped according to skipNull option ({} both, {} input1, {} input2)".format(len(NullResults.keys()), 
                                                                                                                               len([vv for vv in NullResults.values() if vv.lower() == "both"]),
                                                                                                                               len([vv for vv in NullResults.values() if vv.lower() == "input1"]),
                                                                                                                               len([vv for vv in NullResults.values() if vv.lower() == "input2"]),
                                                                                                                           )
          )
    Results = [(kk, KSTestResults[kk], Chi2TestResults[kk], IntegralResults[kk], Integrals1[kk], Integrals2[kk]) for kk in tqdm(kInBoth) if (not skipNull or kk not in NullResults.keys())]
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
        print("KS: {:.5f}".format(result[1]), " Chi2/NDoF: {:.5f}".format(result[2]), " Integral (new/old - 1): {:+.5f}".format(result[3]), " Histogram: ", result[0])
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
    parser.add_argument('--keywords', dest='keywords', action='store', default=None, type=str, nargs='*',
                        help='Keywords to search for in histogram names, will skip any that do not contain a match for all, if invoked')
    parser.add_argument('--findReplace', dest='findReplace', action='store', default=None, type=str, nargs='*',
                        help='VALUE1==VALUE2 pairs to replace when comparing histograms in input1 to histograms in input2')
    parser.add_argument('--skipNull', dest='skipNull', action='store_true',
                        help='Skip comparisons where one or both histograms have 0 integral')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')

    #Parse the arguments
    args = parser.parse_args()
    verbose = args.verbose
    main(args.input1, args.input2, args.Chi2Maximum, args.KSMinimum, args.sort, args.maxResults, args.keywords, args.findReplace, args.skipNull, verbose=verbose)
