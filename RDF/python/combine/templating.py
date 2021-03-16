import pdb
def write_combine_cards(analysisDirectory, era, channel, variable, categories, template="TTTT_templateV9.txt", counts = {}):
    lumistr = {"2017": "1.023", "2018": "1.025"}[era] #Uncertainty per year
    outputLines = []
    with open(template, "r") as inFile:
        for line in inFile:
            outputLines.append(line)
    keymapping = {"DATA": "data_obs", "TTNOBB": "ttnobb", "TTBB": "ttbb", "ST": "singletop", "TTV": "ttVJets", "TTRARE": "ttultrarare", "TTH": "ttH", "EWK": "DY", "TTTT": "tttt"}
    for category in categories:
        rate = {}
        activeUncertainty = {}
        twoSidedSystematics = set()
        oneSidedSystematics = set()
        if category in counts:
            for kword, kproc in keymapping.items():
                twoSidedSystematics = twoSidedSystematics.union(set([syst.replace("Up", "").replace("Down", "") for syst in 
                                                                     counts.get(category).get(kproc, {}).keys() if syst.endswith("Up") or syst.endswith("Down")]))
                oneSidedSystematics = oneSidedSystematics.union(set([syst for syst in counts.get(category).get(kproc, {}).keys() if not (syst.endswith("Up") or syst.endswith("Down"))]))
                rate[kword] = "{:.5f}".format(counts.get(category).get(kproc, -1).get("nom", -1))
                if kword == "DATA": 
                    continue
                activeUncertainty[kword] = dict()
                for ksyst, ksystrate in counts.get(category).get(kproc, {}).items():
                    activeUncertainty[kword][ksyst] = "1.0" if counts.get(category).get(kproc, {ksyst: -1}).get(ksyst, -1) > 0 else "-  "
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
                                 .replace("$LUMI", lumistr)
                for kword in rate.keys():
                    if "$R_" + kword in outputline:
                        outputline = outputline.replace("$R_" + kword, "{:16s}".format(rate[kword]))
                lsplit = outputline.split(" ")
                if len(lsplit) > 0:
                    if lsplit[0] in oneSidedSystematics:
                        for kword in activeUncertainty.keys():
                            active = "{:16s}".format(activeUncertainty[kword][lsplit[0]])
                            if "$ACT_"+kword in outputline:
                                outputline = outputline.replace("{:16s}".format("$ACT_"+kword), active)
                                if "$ACT_"+kword in outputline:
                                    outputline = outputline.replace("$ACT_"+kword, active)
                    elif lsplit[0] in twoSidedSystematics:
                        for kword in activeUncertainty.keys():
                            active = "{:16s}".format("1.0") if activeUncertainty[kword][lsplit[0] + "Up"] == "1.0"\
                                     and activeUncertainty[kword][lsplit[0] + "Down"] == "1.0" else "{:16s}".format("-")
                            if "$ACT_"+kword in outputline:
                                outputline = outputline.replace("{:16s}".format("$ACT_"+kword), active)
                                if "$ACT_"+kword in outputline:
                                    outputline = outputline.replace("$ACT_"+kword, active)
                if "prefire" in outputline and era == "2018":
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
                # if "ttttISR" in outputline or "ttttFSR" in outputline:
                #     disabledSystematics.append("ISR/FSR for tttt")
                #     outputline = "# " + outputline
                if era == "2017" and "ttVJetsISR" in outputline or "ttVJetsFSR" in outputline or "ttHISR" in outputline or "ttHFSR" in outputline:
                    disabledSystematics.append("ISR/FSR for 2017 ttVJets, ttH (inclusive samples assumed!)")
                    outputline = "# " + outputline
                outFile.write(outputline)
            print("Finished writing output for category {}".format(category))
            print("Disabled systematics:", set(disabledSystematics))
