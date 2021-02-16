import pdb
def write_combine_cards(analysisDirectory, era, channel, variable, categories, template="TTTT_templateV8.txt", counts = {}):
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
            R_DATA =   "{:.5f}".format(counts.get(category).get("data_obs", -1).get("nom", -1))
            R_TTNOBB = "{:.5f}".format(counts.get(category).get("ttnobb", -1).get("nom", -1))
            R_TTBB =   "{:.5f}".format(counts.get(category).get("ttbb", -1).get("nom", -1))
            R_ST =     "{:.5f}".format(counts.get(category).get("singletop", -1).get("nom", -1))
            R_TTH =    "{:.5f}".format(counts.get(category).get("ttH", -1).get("nom", -1))
            R_TTV =    "{:.5f}".format(counts.get(category).get("ttVJets", -1).get("nom", -1))
            R_TTRARE = "{:.5f}".format(counts.get(category).get("ttultrarare", -1).get("nom", -1))
            R_EWK =    "{:.5f}".format(counts.get(category).get("DY", -1).get("nom", -1))
            R_TTTT =   "{:.5f}".format(counts.get(category).get("tttt", -1).get("nom", -1))
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
            for line in outputLines:
                if "prefire" in line and era == "2018":
                    continue
                if "leptonSFEl" in line and channel == "MuMu":
                    continue
                if "leptonSFMu" in line and channel == "ElEl":
                    continue
                if "OSDL_RunII_nJet" in line and "Mult" in line and category.split("_")[-1] not in line:
                    continue
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
                outFile.write(outputline)
            print("Finished writing output for category {}".format(category))
