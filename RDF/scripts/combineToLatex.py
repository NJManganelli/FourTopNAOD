import os
import math
import argparse

def getLimits(limitsFile):
    doAppend = False
    doObserved = False
    results = []
    with open(limitsFile, "r") as lf:
        for line in lf:
            line = line.rstrip()
            if doAppend:
                results.append(float(line.split(" ")[-1]))
            if "-- AsymptoticLimits ( CLs ) --" in line: 
                doAppend = True
            if "Observed Limit:" in line:
                doObserved = True
            if (doObserved and len(results) == 6) or (not doObserved and len(results) == 5):
                doAppend = False
        return results
    return "No file found"

def getSignificance(significanceFile):
    with open(significanceFile, "r") as sf:
        for line in sf:
            line = line.rstrip()
            if "Significance:" in line:
                return float(line.split(" ")[1])
        return "No result found in file"
    return "No file found"

def round_to_n(x, sigfigs):
    abs_x = abs(x)
    if float(abs_x) == 0.0:
        return "0." + "0"*(sigfigs-1)
    else:
        return round(x, -int(math.floor(math.log10(abs_x))) + sigfigs - 1)

def configureLatex(channel, limits, significance, XS, sigfigs=3):
    result = ""
    if channel == "MuMu":
        result += "$\\PGm\\PGm$ \\rule[-2mm]{0mm}{6mm}  & "
    elif channel == "ElMu":
        result += "$\\Pe\\PGm$  \\rule[-2mm]{0mm}{6mm}  & "
    elif channel == "ElEl":
        result += "$\\Pe\\Pe$   \\rule[-2mm]{0mm}{6mm}  & "
    elif channel == "AllChan":
        result += "Combined   \\rule[-2mm]{0mm}{6mm}  & "
    else:
        raise ValueError("channel not recognized: {}".format(channel))

    #Is the first observed or do we only have the 5 expected limit values?
    observed = None
    if len(limits) == 6:
        observed = limits[0]
        result += "$" + str(round_to_n(observed, sigfigs)) + "$ & "
        result += "$" + str(round_to_n(XS * observed, sigfigs)) + "$ & "
        offset = 1
    else:
        offset = 0
    central = limits[offset+2]
    up = limits[offset+4] - limits[offset+2]
    down = limits[offset+0] - limits[offset+2]
    lps = "+" if up > 0 else ""

    #limits in mu
    result += "$" + str(round_to_n(central, sigfigs)) + "_{" + str(round_to_n(down, sigfigs)) + "}^{" + lps + str(round_to_n(up, sigfigs)) + "}$ & "
    #limits in fb
    result += "$" + str(round_to_n(XS * central, sigfigs)) + "_{" + str(round_to_n(XS * down, sigfigs)) + "}^{" + lps + str(round_to_n(XS * up, sigfigs)) + "}$ & "
    #significance
    result += "$" + str(round_to_n(significance, sigfigs-1)) + " \\sigma$ \\\\"

    return result
# $\PGm\PGm$\rule[-2mm]{0mm}{6mm}  & $7.28_{-3.61}^{+7.97}$ & $87.4_{-43.3}^{+95.6}$     & $0.31 \sigma$ \\
#  \hline
#  $\Pe\PGm $ \rule[-2mm]{0mm}{6mm}      &  $5.17_{-2.55}^{+5.48}$ & $62.0_{-30.6}^{+65.8}$     & $0.44 \sigma$ \\
#  \hline
#  $\Pe\Pe$\rule[-2mm]{0mm}{6mm}       & $7.53_{-3.74}^{+8.10}$ & $90.4_{-44.9}^{+97.2}$     & $0.30 \sigma$ \\
#   \hline
# Combined  \rule[-2mm]{0mm}{6mm}   & $3.61_{-1.75}^{+3.67}$  & $43.3_{-21.0}^{+44.0}$    & $0.60 \sigma$  \\
# % \hline
# \end{tabular}
# \label{table:limits"+shortera+"HT}
# \vskip -4mm
# \end{table}                

def main(analysisDir, inputs):    
    for fLim, fSig, XS in inputs:        
        assert fLim != ""
        assert fSig != ""
        assert fLim.split(".")[0] == fSig.split(".")[0]
        era, channel, _, var, *other = fLim.split("_")
        var = var.split(".")[0]
        print(fLim, fSig, XS, era, channel, var)
        if os.path.isfile(os.path.join(analysisDir, "Combine", fLim)):
            limits = getLimits(os.path.join(analysisDir, "Combine", fLim))
        else:
            print(str(os.path.join(analysisDir, "Combine", fLim) + "not found"))
        if os.path.isfile(os.path.join(analysisDir, "Combine", fSig)):
            significance = getSignificance(os.path.join(analysisDir, "Combine", fSig))
        else:
            print(str(os.path.join(analysisDir, "Combine", fSig) + "not found"))
        
        print(configureLatex(channel, limits, significance, XS, sigfigs=3))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert the text output of Higgs Combine to LaTeX for inclusion in Analysis Notes')
    parser.add_argument('--limSigXS', dest='limSigXS', action='append', default=None, type=str,
                        help='Colon (:) separated values for the file containing the  limit, the significance, and finally the float value of the signal cross-section')
    parser.add_argument('--analysisDirectory', dest='analysisDirectory', action='store', type=str, default = ".",
                        help='analysis directory head folder, results presumed to be found in the Combine subfolder')
    # parser.add_argument('--KSMinimum', dest='KSMinimum', action='store', type=float, default=0.9999,
    #                     help='Minimal KS test value, histogram pairs with lower will be flagged')
    # parser.add_argument('--Chi2Maximum', dest='Chi2Maximum', action='store', type=float, default=float(1e-4),
    #                     help='Maximal Chi2 test value, histogram pairs with higher will be flagged')
    # parser.add_argument('--input1', dest='input1', action='store', default=None, type=str,
    #                     help='Path to the input1 file')
    # parser.add_argument('--input2', dest='input2', action='store', default=None, type=str,
    #                     help='Path to the input2 file')
    # parser.add_argument('--sort', dest='sort', action='store', choices=['KS', 'Chi2', 'Name', 'name', 'Integral', 'Area', 'Norm', 'AbsIntegral', 'AbsNorm', 'AbsArea'], default='Chi2', type=str,
    #                     help='Sorting key, defaulting to descending Chi2 test values; KS sorts in ascending order; Integral/Area/Norm are synonyms and sort in descending order')
    # parser.add_argument('--maxResults', dest='maxResults', action='store', default=10, type=int,
    #                     help='Max number of results to print out')
    # parser.add_argument('--findReplace', dest='findReplace', action='store', default=None, type=str, nargs='*',
    #                     help='VALUE1==VALUE2 pairs to replace when comparing histograms in input1 to histograms in input2')
    # parser.add_argument('--skipNull', dest='skipNull', action='store_true',
    #                     help='Skip comparisons where one or both histograms have 0 integral')
    # parser.add_argument('--verbose', dest='verbose', action='store_true',
    #                     help='Enable more verbose output during actions')

    #Parse the arguments
    args = parser.parse_args()
    inputs = [(x.split(":")[0], x.split(":")[1], float(x.split(":")[2])) for x in args.limSigXS]
    main(args.analysisDirectory, inputs)
