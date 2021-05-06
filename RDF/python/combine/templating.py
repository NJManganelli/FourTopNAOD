import pdb
import math
def write_combine_cards(analysisDirectory, era, channel, variable, categories, template="TTTT_templateV9.txt", counts = dict(), options = dict()): 
    lumistr = {"2016": "1.012", "2017": "1.023", "2018": "1.025"}[era] #Uncertainty per year with old, uncorrelated recommendation
    #For recommendations from https://twiki.cern.ch/twiki/bin/view/CMS/TopSystematics#Luminosity, applicable to TTTT_templateV14.txt and after
    uncorrlumi = {"2016": "1.010", "2017": "1.020", "2018": "1.015"}[era] #replace $ULUM
    corr161718lumi = {"2016": "1.006    ", "2017": "1.009    ", "2018": "1.020    "}[era] #replace $CL161718
    corr1718lumi = {"2016": "-      ", "2017": "1.006  ", "2018": "1.002  "}[era] #replace $CL1718
    hdampstr = {"2017": "0.93/1.10", "2018": "0.93/1.10"}[era] #Uncertainty per year, derived from inclusive check of channels, btag and jet categories, ttbar subprocesses
    uestr = {"2017": "0.99/1.01", "2018": "0.99/1.01"}[era] #Uncertainty per year, derived from inclusive check of channels, btag and jet categories, ttbar subprocesses
    outputLines = []
    with open(template, "r") as inFile:
        for line in inFile:
            outputLines.append(line)
    keymapping = {"DATA": "data_obs", "TTNOBB": "ttnobb", "TTBB": "ttbb", "ST": "singletop", "TTV": "ttVJets", "TTRARE": "ttultrarare", "TTH": "ttH", "EWK": "EWK", "TTTT": "tttt"}
    normkeys = ["OSDL_RunII_hdampUp", "OSDL_RunII_hdampDown", "OSDL_RunII_ueUp", "OSDL_RunII_ueDown"]
    for category in categories:
        rate = {}
        activeUncertainty = {}
        normUncertainty = {}
        twoSidedSystematics = set()
        oneSidedSystematics = set()
        if category in counts:
            for kword, kproc in keymapping.items():
                twoSidedSystematics = twoSidedSystematics.union(set([syst.replace("Up", "").replace("Down", "") for syst in 
                                                                     counts.get(category).get(kproc, {}).keys() if syst.endswith("Up") or syst.endswith("Down")]))
                oneSidedSystematics = oneSidedSystematics.union(set([syst for syst in counts.get(category).get(kproc, {}).keys() if not (syst.endswith("Up") or syst.endswith("Down"))]))
                try:
                    rate[kword] = "{:.5f}".format(counts.get(category).get(kproc, -1).get("nom", -1))
                except:
                    pdb.set_trace()
                # rate[kword] = "{:.5f}".format(counts.get(category).get(kproc, {"nom": -1}).get("nom", -1))
                if kword == "DATA": 
                    continue
                activeUncertainty[kword] = dict()
                normUncertainty[kword] = dict()
                for ksyst, ksystrate in counts.get(category).get(kproc, {}).items():
                    activeUncertainty[kword][ksyst] = "1.0" if counts.get(category).get(kproc, {ksyst: -1}).get(ksyst, -1) > 0 else "-  "
                    if ksyst in normkeys:
                        if counts.get(category).get(kproc, {"nom": -1}).get("nom", -1) < 1e-6:
                            norm = 1.00
                        else:
                            norm = counts.get(category).get(kproc, {ksyst: -1}).get(ksyst, -1) / counts.get(category).get(kproc, {"nom": -1}).get("nom", -1)
                        normUncertainty[kword][ksyst] = math.copysign(min(3.0, abs(norm)), norm)
        else:
            print("Category not found in counts dict")
            for kword in keymapping.items():
                rate[kword] = str(-1)
                activeUncertainty[kword] = dict()
                activeUncertainty[kword]["ALLACTIVE"] = "{:16s}".format("1.0")
        with open("{}/TTTT_{}_{}_{}_{}.txt".format(analysisDirectory, era, channel, category, variable).replace("//", "/"), "w") as outFile:
            disabledSystematics = []
            for line in outputLines:
                outputline = line.replace("$ERA", era)\
                                 .replace("$CHANNEL", channel)\
                                 .replace("$CATEGORY", category)\
                                 .replace("$VAR", variable)\
                                 .replace("$LUMI", lumistr)\
                                 .replace("$ULUM", uncorrlumi)\
                                 .replace("$CL161718", corr161718lumi)\
                                 .replace("$CL1718", corr1718lumi)\
                                 .replace("$HDAMP   ", hdampstr)\
                                 .replace("$UE      ", uestr)
                for kword in rate.keys():
                    if "$R_" + kword in outputline:
                        outputline = outputline.replace("{:16s}".format("$R_" + kword), "{:16s}".format(rate[kword]))
                        if "$R_" + kword in outputline:
                            outputline = outputline.replace("$R_" + kword, "{:16s}".format(rate[kword]))
                lsplit = outputline.split(" ")
                if len(lsplit) > 0:
                    thisSyst = lsplit[0].replace("#", "") if not outputline.startswith("# ") else lsplit[1]
                    if thisSyst in oneSidedSystematics:
                        for kword in activeUncertainty.keys():
                            active = "{:16s}".format(activeUncertainty[kword][thisSyst])
                            if "$ACT_"+kword in outputline:
                                outputline = outputline.replace("{:16s}".format("$ACT_"+kword), active)
                                if "$ACT_"+kword in outputline:
                                    #catch end of line active flags, where extra spaces aren't present as in '{:16s}'.format('$ACT_TTBB')
                                    outputline = outputline.replace("$ACT_"+kword, active)
                    elif thisSyst in twoSidedSystematics:
                        for kword in activeUncertainty.keys():
                            active = "{:16s}".format("1.0") if activeUncertainty[kword][thisSyst + "Up"] == "1.0"\
                                     and activeUncertainty[kword][thisSyst + "Down"] == "1.0" else "{:16s}".format("-")
                            if "$ACT_"+kword in outputline:
                                outputline = outputline.replace("{:16s}".format("$ACT_"+kword), active)
                                if "$ACT_"+kword in outputline:
                                    outputline = outputline.replace("$ACT_"+kword, active)
                            if thisSyst in normkeys or thisSyst+"Up" in normkeys or thisSyst+"Down" in normkeys:
                                try:
                                    #Combine convention is down/up systematic as relative ratio of yields for the systematic ot the nominal.
                                    norm = "{:.2f}/{:.2f}".format(normUncertainty[kword][thisSyst+"Down"], normUncertainty[kword][thisSyst+"Up"])
                                except:
                                    norm = "1.00/1.00"
                                    pdb.set_trace()
                                norm = "{:16s}".format(norm)
                                if "$NORM_"+kword in outputline:
                                    try:
                                        outputline = outputline.replace("{:16s}".format("$NORM_"+kword), norm)
                                    except:
                                        pdb.set_trace()
                                    if "$NORM_"+kword in outputline:
                                        outputline = outputline.replace("$NORM_"+kword, norm)
                if "prefire" in outputline and era not in ["2017", "UL17"]:
                    disabledSystematics.append("prefire")
                    continue
                if "leptonSFEl" in outputline and channel == "MuMu":
                    disabledSystematics.append("leptonSFEl")
                    continue
                if "leptonSFMu" in outputline and channel == "ElEl":
                    disabledSystematics.append("leptonSFMu")
                    continue
                if "OSDL_RunII_nJet" in outputline and "Mult" in outputline and category.split("_")[-1] not in outputline:
                    continue
                #Re-enabled: tttt ISR/FSR
                # if "ttttISR" in outputline or "ttttFSR" in outputline:
                #     disabledSystematics.append("ISR/FSR for tttt")
                #     outputline = "# " + outputline
                #Re-enabled: ttH ISR/FSR
                # if era == "2017" and ("ttHISR" in outputline or "ttHFSR" in outputline):
                #     disabledSystematics.append("ISR/FSR for 2017 ttH (inclusive samples assumed!)")
                #     outputline = "# " + outputline
                if era == "2017" and ("ttVJetsISR" in outputline or "ttVJetsFSR" in outputline):
                    disabledSystematics.append("ISR/FSR for 2017 ttVJets")
                    outputline = "# " + outputline
                if ("OSDL_RunII_hdamp" in outputline or "OSDL_RunII_ue" in outputline) and "shape" in outputline:
                    disabledSystematics.append("hdamp/ue shape-type")
                    outputline = "# " + outputline
                if ("OSDL_RunII_hdamp" in outputline or "OSDL_RunII_ue" in outputline) and "lnN" in outputline:
                    disabledSystematics.append("hdamp/ue asymmetric lnN-type")
                    outputline = "# " + outputline
                if (era == "2016" or era == "2017") and "HEM" in outputline:
                    disabledSystematics.append("HEM (2016 or 2017)")
                    outputline = "# " + outputline
                outFile.write(outputline)
            print("Finished writing output for category {}".format(category))
            print("Disabled systematics:", set(disabledSystematics))
