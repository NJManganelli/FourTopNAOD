import os
import math
import argparse
import copy
import pdb

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

def configureLatex(channel, limits, significance, XS, sigfigs=3, blind=False):
    if isinstance(XS, str):
        XS = float(XS)
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
    aposteriori = False
    if len(limits) == 6:
        if blind:
            result += "$" + "X." + "X"*(sigfigs-1) + "$ & "
            result += "$" + "X." + "X"*(sigifigs-1) + "$ & "
        else:
            observed = limits[0] if not blind else None
            result += "$" + str(round_to_n(observed, sigfigs)) + "$ & "
            result += "$" + str(round_to_n(XS * observed, sigfigs)) + "$ & "
        offset = 1
        aposteriori = True
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
    if aposteriori:
        header = "Channel    & Obs. lim. & Obs. lim. & Exp. lim. & Exp. lim. & Obs. significance \\\\ \n"\
                 "           & [$\\times \sigmattttsm$] & [fb] & [$\\times \sigmattttsm$]  & [fb] & Std. Dev. \\\\"
    else:
        header = "Channel    & Exp. lim. & Exp. lim. & Exp. significance \\\\ \n"\
                 "           & [$\\times \sigmattttsm$]  & [fb] & Std. Dev. \\\\"

    return result, header


def main(analysisDir, inputs, ):
    for subinput in inputs:
        if len(subinput.split(":")) == 3:
            fLim, fSig, XS = subinput.split(":")
            assert fLim != ""
            assert fSig != ""
            assert fLim.split(".")[0] == fSig.split(".")[0]
            era, channel, _, var, *other = fLim.split("_")
            var = var.split(".")[0]
            print(fLim, fSig, XS, era, channel, var)
            limits = None
            significance = None
            if os.path.isfile(os.path.join(analysisDir, "Combine", fLim)):
                limits = getLimits(os.path.join(analysisDir, "Combine", fLim))
            else:
                print(str(os.path.join(analysisDir, "Combine", fLim) + "not found"))

            if os.path.isfile(os.path.join(analysisDir, "Combine", fSig)):
                significance = getSignificance(os.path.join(analysisDir, "Combine", fSig))
            else:
                print(str(os.path.join(analysisDir, "Combine", fSig) + "not found"))

            if limits is None or significance is None:
                raise ValueError(f"Failed to find limits or significance: limits={limits} significance={significance}")
            results, header = configureLatex(channel, limits, significance, XS, sigfigs=3)
            print("=================")
            print(header)
            print(results)
            print("=================")
        # elif len(subinput.split(":")) == 5:
        #     #We have Apriori and (unblinded?) data in our usual workflow
        #     fLimApriori, fLimAposteriori, fSigApriori, fSigAposteriori, XS = subinput.split(":")
        #     assert fLimApriori != ""
        #     assert fLimAposteriori != ""
        #     assert fSigApriori != ""
        #     assert fSigAposteriori != ""
        #     assert fLimApriori.split(".")[0] == fSigApriori.split(".")[0]
        #     assert fLimAposteriori.split(".")[0] == fSigAposteriori.split(".")[0]
        #     era, channel, _, var, *other = fLimApriori.split("/")[-1].split("_")
        #     var = var.split(".")[0]
        #     print(fLimApriori, fLimAposteriori, fSigApriori, fSigAposteriori, XS, era, channel, var)
        #     limitsApriori = None
        #     limitsAposteriori = None
        #     significanceApriori = None
        #     significanceAposteriori = None
        #     if os.path.isfile(os.path.join(analysisDir, "Combine", fLimApriori)):
        #         limitsApriori = getLimits(os.path.join(analysisDir, "Combine", fLimApriori))
        #     else:
        #         print(str(os.path.join(analysisDir, "Combine", fLimApriori) + "not found"))
        #     if os.path.isfile(os.path.join(analysisDir, "Combine", fLimAposteriori)):
        #         limitsAposteriori = getLimits(os.path.join(analysisDir, "Combine", fLimAposteriori))
        #     else:
        #         print(str(os.path.join(analysisDir, "Combine", fLimAposteriori) + "not found"))

        #     if os.path.isfile(os.path.join(analysisDir, "Combine", fSigApriori)):
        #         significanceApriori = getSignificance(os.path.join(analysisDir, "Combine", fSigApriori))
        #     else:
        #         print(str(os.path.join(analysisDir, "Combine", fSigApriori) + "not found"))
        #     if os.path.isfile(os.path.join(analysisDir, "Combine", fSigAposteriori)):
        #         significanceAposteriori = getSignificance(os.path.join(analysisDir, "Combine", fSigAposteriori))
        #     else:
        #         print(str(os.path.join(analysisDir, "Combine", fSigAposteriori) + "not found"))

        #     if limitsApriori is None or significanceApriori is None or limitsAposteriori is None or significanceAposteriori is None:
        #         raise ValueError(f"Failed to find limits or significance: limits={limits} significance={significance}")

        #     resultsApriori, headerApriori = configureLatex(channel, limitsApriori, 
        #                                                    significanceApriori, XS, sigfigs=3, blind=False)
        #     resultsAposteriori, headerAposteriori = configureLatex(channel, limitsAposteriori, 
        #                                                            significanceAposteriori, XS, sigfigs=3, blind=False)
        #     print("=================")
        #     print(headerApriori)
        #     print(resultsApriori)
        #     print("===")
        #     print(headerAposteriori)
        #     print(resultsAposteriori)
        #     print("=================")
        #     # print(configureLatexApriorAposteriori(channel, limitsApriori, limitsAposteriori, 
        #     #                                       significanceApriori, significanceAposteriori, XS, sigfigs=3))
        else:
            raise RuntimeError

def limitsToLatex(limits, XS=None, sigfigs=3, blind=False):
    result = "" #Apriori or aposteriori results, with 95% confidence band
    data_result = ""
    if len(limits) == 6:
        if blind:
            if XS is None:
                data_result += "$" + "X." + "X"*(sigfigs-1) + "$"
            else:
                data_result += "$" + "XX." + "X"*(sigfigs-2) + "$"
        else:
            observed = limits[0] if not blind else None
            if XS is None:
                data_result += "$" + str(round_to_n(observed, sigfigs)) + "$"
            else:
                data_result += "$" + str(round_to_n(XS * observed, sigfigs)) + "$"
        offset = 1
    else:
        offset = 0
    central = limits[offset+2]
    up = limits[offset+4] - limits[offset+2]
    down = limits[offset+0] - limits[offset+2]
    lps1 = "+" if up > 0 else ""
    lps2 = "+" if down > 0 else ""

    #If XS is non-None, return in fb
    #limits in mu
    if XS is None:
        result += "$" + str(round_to_n(central, sigfigs)) + "_{" + lps2 + str(round_to_n(down, sigfigs)) + "}^{" + lps1 + str(round_to_n(up, sigfigs)) + "}$"
    #limits in fb
    else:
        result += "$" + str(round_to_n(XS * central, sigfigs)) + "_{" + lps2 + str(round_to_n(XS * down, sigfigs)) + "}^{" + lps1 + str(round_to_n(XS * up, sigfigs)) + "}$"
    return result, data_result

def significanceToLatex(significance, sigfigs, blind=False):
    #significance
    if not blind:
        result = "$" + str(round_to_n(significance, sigfigs-1)) + " \\sigma$" # \\\\"
    else:
        result = "$" + "X." + "X"*(sigfigs-1) + "$"
    return result

def buildMonoTable(nested, feature="rate-lim"):
    eras = nested['rate-lim']['apriori'].keys()
    channels = nested['rate-lim']['apriori'][list(eras)[0]].keys()
    lines = []
    lines.append("\\begin{table}[ht!]")
    lines.append("\\centering")
    if feature == "rate-lim" or feature == "fb-lim":
        lines.append("\\caption{Summary of asymptotic cross section limits for \\tttt production using the RunII dataset.}")
    elif feature == "sig":
        lines.append("\\caption{Summary of asymptotic significances for \\tttt production using the RunII dataset.}")

    if feature == "rate-lim":
        lines.append("\\begin{tabular}{lcccc}")
        #lines.append("%  \\hline")
        lines.append("Era  &  Channel  &  Apriori limit [$\\times \\sigmattttsm$]  &  Aposteriori limit [$\\times \\sigmattttsm$]  &  Observed Limit [$\\times \\sigmattttsm$]")
    elif feature == "fb-lim":
        lines.append("\\begin{tabular}{lcccc}")
        #lines.append("%  \\hline")
        lines.append("Era  &  Channel  &  Apriori limit [fb]  &  Aposteriori limit [fb]  &  Observed Limit  [fb]  \\\\")
    elif feature == "sig":
        lines.append("\\begin{tabular}{lccc}")
        #lines.append("%  \\hline")
        lines.append("Era  &  Channel  &  Apriori significance [Std. Dev.] &  Observed significance [Std. Dev.]  \\\\")


    for era in eras:
        lines.append("\\hline")
        for channel in channels:
            if feature == "rate-lim" or feature == "fb-lim":
                lines.append( "  &  ".join([era, 
                                        nested["rows"][channel], 
                                        nested[feature]["apriori"][era][channel], 
                                        nested[feature]["aposteriori"][era][channel], 
                                        nested[feature]["observed"][era][channel] + "  \\\\",
                                    ]) )
            elif feature == "sig":
                lines.append( "  &  ".join([era, 
                                        nested["rows"][channel], 
                                        nested[feature]["apriori"][era][channel], 
                                        nested[feature]["observed"][era][channel] + "  \\\\",
                                    ]) )
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    lines.append("\\label{table:limits-" + feature + "-HT")
    lines.append("\\vskip -4mm")
    lines.append("\\end{table}")
    return lines

def main2(opts):
    #dictionary for string formatted results
    res = dict()
    res["rate-lim"] = dict()
    res["fb-lim"] = dict()
    res["sig"] = dict()

    res["rate-lim"]["apriori"] = dict()
    res["rate-lim"]["aposteriori"] = dict()
    res["rate-lim"]["observed"] = dict()
    res["fb-lim"]["apriori"] = dict()
    res["fb-lim"]["aposteriori"] = dict()
    res["fb-lim"]["observed"] = dict()
    res["sig"]["apriori"] = dict()
    res["sig"]["observed"] = dict()

    
    
    #Dictionary for some LaTeX column and row names, for now only channel-dependent, could be re-organized into a single table with all years/channels
    res["rows"] = dict()
    res["rows"]["MuMu"] = "$\PGm\PGm$ \\rule[-2mm]{0mm}{6mm}"
    res["rows"]["ElMu"] = "$\Pe\PGm$  \\rule[-2mm]{0mm}{6mm}"
    res["rows"]["ElEl"] = "$\Pe\Pe$   \\rule[-2mm]{0mm}{6mm}"
    res["rows"]["AllChan"] = "Combined   \\rule[-2mm]{0mm}{6mm}"
    for era in args.eras:
        res["rate-lim"]["apriori"][era] = dict()
        res["rate-lim"]["aposteriori"][era] = dict()
        res["rate-lim"]["observed"][era] = dict()
        res["fb-lim"]["apriori"][era] = dict()
        res["fb-lim"]["aposteriori"][era] = dict()
        res["fb-lim"]["observed"][era] = dict()
        res["sig"]["apriori"][era] = dict()
        res["sig"]["observed"][era] = dict()
        for channel in args.channels:
            #TemplateSubPath
            tsp_lim = copy.copy(args.subpath)

            #Apriori results
            tsp_lim_apriori = tsp_lim.replace("$ERA", era).replace("$CHANNEL", channel).replace("$PREPOST", args.apriori).replace("$LIMSIG", "limit")
            try:
                path = os.path.join(opts.analysisDirectory, tsp_lim_apriori)
                tmp = getLimits(path)
                res["rate-lim"]["apriori"][era][channel] = limitsToLatex(tmp, XS=None, sigfigs=opts.sigfigs, blind=False)[0]
                res["fb-lim"]["apriori"][era][channel] = limitsToLatex(tmp, XS=opts.XS, sigfigs=opts.sigfigs, blind=False)[0]
            except:
                tmp = "$?.??_{?.??}^{?.??}$"
                res["rate-lim"]["apriori"][era][channel] = tmp
                res["fb-lim"]["apriori"][era][channel] = tmp

            #Aposteriori results
            tsp_lim_aposteriori = tsp_lim.replace("$ERA", era).replace("$CHANNEL", channel).replace("$PREPOST", args.aposteriori).replace("$LIMSIG", "limit")
            try:
                path = os.path.join(opts.analysisDirectory, tsp_lim_aposteriori)
                tmp = getLimits(path)
                res["rate-lim"]["aposteriori"][era][channel] = limitsToLatex(tmp, XS=None, sigfigs=opts.sigfigs, blind=False)[0]
                res["rate-lim"]["observed"][era][channel]    = limitsToLatex(tmp, XS=None, sigfigs=opts.sigfigs, blind=False)[1]
                res["fb-lim"]["aposteriori"][era][channel]   = limitsToLatex(tmp, XS=opts.XS, sigfigs=opts.sigfigs, blind=False)[0]
                res["fb-lim"]["observed"][era][channel]      = limitsToLatex(tmp, XS=opts.XS, sigfigs=opts.sigfigs, blind=False)[1]
            except:
                tmp = "$?.??_{?.??}^{?.??}$"
                res["rate-lim"]["aposteriori"][era][channel] = tmp
                res["rate-lim"]["observed"][era][channel] = tmp
                res["fb-lim"]["aposteriori"][era][channel] = tmp
                res["fb-lim"]["observed"][era][channel] = tmp

            #Significances
            tsp_sig = copy.copy(args.subpath)
            tsp_sig_apriori = tsp_sig.replace("$ERA", era).replace("$CHANNEL", channel).replace("$PREPOST", args.apriori).replace("$LIMSIG", "significance")
            try:
                path = os.path.join(opts.analysisDirectory, tsp_sig_apriori)
                tmp = getSignificance(path)
                tmp = significanceToLatex(tmp, sigfigs=opts.sigfigs, blind=False)
                res["sig"]["apriori"][era][channel] = tmp
            except:
                tmp = "$?.?? \sigma$"
                res["sig"]["apriori"][era][channel] = tmp
            tsp_sig_aposteriori = tsp_sig.replace("$ERA", era).replace("$CHANNEL", channel).replace("$PREPOST", args.aposteriori).replace("$LIMSIG", "significance")
            try:
                path = os.path.join(opts.analysisDirectory, tsp_sig_aposteriori)
                tmp = getSignificance(path)
                tmp = significanceToLatex(tmp, sigfigs=opts.sigfigs, blind=opts.blind)
                res["sig"]["observed"][era][channel] = tmp
            except:
                if opts.blind:
                    tmp = "$X.XX \sigma$"
                else:
                    tmp = "$?.?? \sigma$"
                res["sig"]["observed"][era][channel] = tmp
    print("==== RATE LIMIT ====")
    for line in buildMonoTable(res, feature="rate-lim"):
        print(line)
    print("==== CROSS SECTION LIMIT ====")
    for line in buildMonoTable(res, feature="fb-lim"):
        print(line)
    print("==== SIGNIFICANCE ====")
    for line in buildMonoTable(res, feature="sig"):
        print(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert the text output of Higgs Combine to LaTeX for inclusion in Analysis Notes')
    parser.add_argument('--limSigXS', dest='limSigXS', action='append', default=None, type=str,
                        help='Colon (:) separated values for the file containing the  limit, the significance, and finally the float value of the signal cross-section')
    parser.add_argument('--analysisDirectory', dest='analysisDirectory', action='store', type=str, default = ".",
                        help='analysis directory head folder, results presumed to be found in the Combine subfolder')
    parser.add_argument('--subpath', dest='subpath', action='store', type=str, default = "Combine/$ERA_$CHANNEL_AllSyst_HT.$LIMSIG",
                        help='template for the relative path from the analsysiDirectory folder to get to results, keywords $ERA, $CHANNEL, $PREPOST, $LIMSIG ("limit", "significance") from the analysis directory')
    parser.add_argument('--eras', dest='eras', action='store', nargs='*', type=str, default=['2017', '2018', 'RunII'],
                        help='eras to be run over')
    parser.add_argument('--channels', dest='channels', action='store', nargs='*', type=str, default=['MuMu', 'ElMu', 'ElEl', 'AllChan'],
                        help='channels to be run over')
    parser.add_argument('--apriori', dest='apriori', action='store', type=str, default = "Asimov",
                        help='apriori flag for replacement of $PREPOST flag in subpath')
    parser.add_argument('--aposteriori', dest='aposteriori', action='store', type=str, default = "Unblinded",
                        help='aposteriori flag for replacement of $PREPOST flag in subpath')
    parser.add_argument('--XS', dest='XS', action='store', type=float, default = 12.0,
                        help='Signal cross-section [fb] for converting limits from rate parameter to femtobarns')
    parser.add_argument('--unblind', dest='blind', action='store_false', default=True,
                        help='unblind results')
    parser.add_argument('--sigfigs', dest='sigfigs', action='store', type=int, default = 3,
                        help='Significant figures to report limits and significances with')
        

    #Parse the arguments
    args = parser.parse_args()
    main2(args)
    # main(args.analysisDirectory, args.limSigXS)
