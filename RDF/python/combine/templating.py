def write_combine_cards(analysisDirectory, era, channel, variable, categories, template="TTTT_templateV6.txt", counts = {}):
    lumistr = {"2017": "1.023", "2018": "1.025"}[era] #Uncertainty per year
    outputLines = []
    with open(template, "r") as inFile:
        for line in inFile:
            outputLines.append(line)
    for category in categories:
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
        else:
            print("Category not found in counts dict")
            R_DATA = R_TTNOBB = R_TTBB = R_ST = R_TTH = R_TTV = R_TTRARE = R_EWK = R_TTTT = str(-1)
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
                outFile.write(line\
                              .replace("$ERA", era)\
                              .replace("$CHANNEL", channel)\
                              .replace("$CATEGORY", category)\
                              .replace("$VAR", variable)\
                              .replace("$LUMI", lumistr)\
                              .replace("$R_DATA",          "{:16s}".format(R_DATA))\
                              .replace("$R_TTNOBB       ", "{:16s}".format(R_TTNOBB))\
                              .replace("$R_TTBB         ", "{:16s}".format(R_TTBB))\
                              .replace("$R_ST           ", "{:16s}".format(R_ST))\
                              .replace("$R_TTH          ", "{:16s}".format(R_TTH))\
                              .replace("$R_TTV          ", "{:16s}".format(R_TTV))\
                              .replace("$R_TTRARE       ", "{:16s}".format(R_TTRARE))\
                              .replace("$R_EWK          ", "{:16s}".format(R_EWK))\
                              .replace("$R_TTTT",          "{:16s}".format(R_TTTT)))
            print("Finished writing output for category {}".format(category))
