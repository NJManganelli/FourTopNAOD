import pdb
import array
import ROOT


def project(hist, axes, slices):
    m = dict([(hist.GetXaxis().GetTitle().lstrip().rstrip(), "x"), (hist.GetYaxis().GetTitle().lstrip().rstrip(), "y"), (hist.GetZaxis().GetTitle().lstrip().rstrip(), "z")])
    for slc in slices:
        assert isinstance(slc[0], str) and slc[0] in m.keys() and isinstance(slc[1], (int, float)) and isinstance(slc[2], (int, float)), [m.items(), slc]
        if m.get(slc[0]) == "x":
            # m[slc[0]] = "x"
            hist.GetXaxis().SetRangeUser(slc[1], slc[2])
        elif m.get(slc[0]) == "y":
            # m[slc[0]] = "y"
            hist.GetYaxis().SetRangeUser(slc[1], slc[2])
        elif m.get(slc[0]) == "z":
            # m[slc[0]] = "z"
            hist.GetZaxis().SetRangeUser(slc[1], slc[2])
        else:
             raise ValueError("Axes slices do not match Axes titles\n", slc, " Axes: ", list(m.items()))
    draw_opt = ""
    for axis in axes:
        assert axis in m.keys()
        draw_opt+= m.get(axis)
    draw_opt += " e"
    proj = hist.Project3D(draw_opt)
    hist.GetXaxis().SetRange(0,0)
    hist.GetYaxis().SetRange(0,0)
    hist.GetZaxis().SetRange(0,0)
    return proj


def cartesian_product_list(name_format="$NUM_$LET_$SYM", name_tuples=[("$NUM", ["1", "2"]), ("$LET", ["A", "B", "C"]), ("$SYM", ["*", "@"])]):
    """Take as input a string <name_format> and list of tuples <name_tuple> where a cartesian product of the tuples is formed.
    The tuples contain a key-string (also present in the name_format string) and value-list with the replacements to cycle through.
    The last tuple is the innermost replacement in the list formed, regardless of placement in the name_format string."""
    if 'copy' not in dir():
        try:
            import copy
        except:
            raise RuntimeError("Could not import the copy module in method cartesianProductList")
    if 'itertools' not in dir():
        try:
            import itertools
        except:
            raise RuntimeError("Could not import the itertools module in method cartesianProductList")
    list_of_lists = []
    list_of_keys = []
    for k, v in name_tuples:
        list_of_lists.append(v)
        list_of_keys.append(k)
    cart_prod = [zip(list_of_keys, l) for l in list(itertools.product(*list_of_lists))]
    ret_list = []
    for uzip in cart_prod:
        nc = copy.copy(name_format)
        for k, v in uzip:
            nc = nc.replace(k, v)
        ret_list.append(nc)
    return ret_list

'2018___ttother_DL-GF_fr___ElMu___ZWindowMET0Width0___HT500___HT___nom'
def group(available_keys, eras, processes, channels, categories, variable, systematic, 
          input_format="$ERA___$PROCESS___$CHANNEL___$WINDOW___$CATEGORY$BLIND___$VARIABLE___$SYSTEMATIC",
          fallback_systematic="nom", 
          windows={"ElMu": "ZWindowMET0Width0", "ElEl": "ZWindowMET0p0Width15p0", "MuMu": "ZWindowMET0p0Width15p0"}):
    # output_name = input_format.format("$ERA", eras
    principal = cartesian_product_list(name_format=input_format,
                                       name_tuples=[("$ERA", eras),
                                                    ("$PROCESS", processes),
                                                    ("$CHANNEL", channels),
                                                    ("$WINDOW", list(set(windows.values()))),
                                                    ("$CATEGORY", categories),
                                                    ("$VARIABLE", [variable]),])
                                                    # ("$SYSTEMATIC", [systematic])])
    principal = [prel for prel in principal if windows.get(prel.split("___")[2]) == prel.split("___")[3]]
    ret = []
    unfound = []
    blind = False
    for princ in principal:
        if princ.replace("$SYSTEMATIC", systematic).replace("$BLIND", "") in available_keys:
            ret.append(princ.replace("$SYSTEMATIC", systematic).replace("$BLIND", ""))
        elif princ.replace("$SYSTEMATIC", systematic).replace("$BLIND", "BLIND") in available_keys:
            blind = True
            ret.append(princ.replace("$SYSTEMATIC", systematic).replace("$BLIND", "BLIND"))
        elif systematic != fallback_systematic and princ.replace("$SYSTEMATIC",fallback_systematic).replace("$BLIND", "") in available_keys:
            ret.append(princ.replace("$SYSTEMATIC", fallback_systematic).replace("$BLIND", ""))
        elif systematic != fallback_systematic and princ.replace("$SYSTEMATIC",fallback_systematic).replace("$BLIND", "BLIND") in available_keys:
            blind = True
            ret.append(princ.replace("$SYSTEMATIC", fallback_systematic).replace("$BLIND", "BLIND"))
        else:
            unfound.append(princ.replace("$SYSTEMATIC", systematic))
    return ret, blind, unfound
    # prelim = cartesian_product_list(name_format=input_format,
    #                                 name_tuples=[("$ERA", eras),
    #                                              ("$PROCESS", processes),
    #                                              ("$CHANNEL", channels),
    #                                              ("$WINDOW", list(windows.values())),
    #                                              ("$CATEGORY", categories),
    #                                              ("$VARIABLE", [variable]),
    #                                              ("$SYSTEMATIC", [systematic])])
    # prelim = [prel for prel in prelim if windows.get(prel.split("___")[2]) == prel.split("___")[3]]
    # return prelim

HTArray=[400 + 16*x for x in range(101)]
nJetArray=[4,5,6,7,8,20]
nBTagArray=[0,1,2,3,4,10]
HTArr = array.array('d', HTArray)
nJetArr = array.array('d', nJetArray)
nBTagArr = array.array('d', nBTagArray)
h = ROOT.TH3D("h", "; HT; nJet; nBTag", len(HTArr)-1, HTArr, len(nJetArr)-1, nJetArr, len(nBTagArr)-1, nBTagArr)
for nJ in nJetArray[:-1]:
    for nB in nBTagArray[:-1]:
        h.Fill(550, nJ, nB, 10*nJ + nB)

# g = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Jan23_2018/Combine/ElMu/2018___ttother_DL-GF_fr.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Jan25_2018/Combine/ElMu/2018___ttother_DL-GF_fr.root", "read")
# gk = [kk.GetName() for kk in g.GetListOfKeys()]
# fk = [kk.GetName() for kk in f.GetListOfKeys()]

# g0 = g.Get('2018___ttother_DL-GF_fr___ElMu___ZWindowMET0Width0___HT500_nMediumDeepJetB2_nJet5___HT___nom')
# fsource = f.Get('2018___ttother_DL-GF_fr___ElMu___ZWindowMET0Width0___HT500___HT___nom')
# f0 = project(fsource, ["HT"], [("HT", g0.GetXaxis().GetXmin(), g0.GetXaxis().GetXmax()), ("nJet", 5, 6), ("nBTag", 2, 3)])
# f1 = project(fsource, ["HT"], [("nJet", 5, 6), ("nBTag", 2, 3)])


processGroups = dict()
processGroups["ttnobb"] = {
    "Color": 632, 
    "Style": "Fill", 
    "Names": ["ttother_DL_fr", "ttother_SL_fr", "ttother_DL_nr", "ttother_SL_nr", "ttother_DL-GF_fr", "ttother_SL-GF_fr", "ttother_AH",]
}
processGroups["ttbb"] = {
    "Color": 38, 
    "Style": "Fill", 
    "Names": ["ttbb_DL_fr", "ttbb_SL_fr", "ttbb_DL_nr", "ttbb_SL_nr", "ttbb_DL-GF_fr", "ttbb_SL-GF_fr", "ttbb_AH",]
}
processGroups["ttultrarare"] =  {
        "Color": 432, 
    "Style": "Fill", 
    "Names": ["ttWW", "ttWH", "ttWZ", "ttZZ", "ttZH", "ttHH", "tttW", "tttJ",]
}
processGroups["ewk"] = {
    "Color": 416, 
    "Style": "Fill", 
    "OldNames": ["DYJets_DL",],
    "Names": ["DYJets_DL-HT100", "DYJets_DL-HT200", "DYJets_DL-HT400", "DYJets_DL-HT600", "DYJets_DL-HT800", "DYJets_DL-HT1200", "DYJets_DL-HT2500",
              "WJets_SL-HT100", "WJets_SL-HT200", "WJets_SL-HT400", "WJets_SL-HT600", "WJets_SL-HT800", "WJets_SL-HT1200", "WJets_SL-HT2500",
              "WW", "WZ", "ZZ",]
}
processGroups["singletop"] = {
    "Color": 400, 
    "Style": "Fill", 
    "OldNames": ["ST_tW", "ST_tbarW",],
    "Names": ["ST_tW-NoFHad", "ST_tbarW-NoFHad",]
}
processGroups["ttH"] = {
    "Color": 616, 
    "Style": "Fill", 
    "OldNames": ["ttH",],
    "Names": ["ttH_SL-bb", "ttH_DL-bb",]
}
processGroups["tttt"] = {
    "Color": 864, 
    "Style": "Line", 
    "Names": ["tttt",]
}
# processGroups["tttt_badNPartonInBorn"] = {
#     "Color": 864, 
#     "Style": "Line", 
#     "Names": ["tttt_badNPartonInBorn",]
# }
processGroups["ttVJets"] = {
    "Color": 880, 
    "Style": "Fill", 
    "Names": ["ttWJets", "ttZJets",],
    "UnusableNames": ["ttWJets_QQ", "ttWJets_LNu", "ttZJets_QQ", "ttZJets_DL-M10", "ttZJets_DL-M1to10",]
}    
processGroups["Data"] = {
    "Color": 1, 
    "Style": "Marker",
    "MarkerStyle": 20, 
    "Names": ["ElMu_A", "MuMu_A", "ElEl_A", "El_A", "Mu_A", 
              "ElMu_B", "MuMu_B", "ElEl_B", "El_B", "Mu_B",
              "ElMu_C", "MuMu_C", "ElEl_C", "El_C", "Mu_C",
              "ElMu_D", "MuMu_D", "ElEl_D", "El_D", "Mu_D",
              "ElMu_E", "MuMu_E", "ElEl_E", "El_E", "Mu_E",
              "ElMu_F", "MuMu_F", "ElEl_F", "El_F", "Mu_F",]
}
    
# test = group(None, ["2018"], processGroups["ttnobb"].get("Names"), channels=["ElMu"], categories=["HT500"], variable="HT", systematic="nom")

# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Jan25_2017/Combine/All/2017___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Jan25_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/testPUID_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb5_PUID_nonJetMult2017/Combine/All/2017___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb5_PUID_nonJetMult2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb12_Baseline_2017/Combine/All/2017___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb12_Baseline_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb12_TightPUID_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb12_TightLeptonIDandSFs_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb12_DeepCSV_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb12_TopPtReweighting_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb12_5BTagCats_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb12_HT350_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Feb12_ZWindowMET40_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/nJetSF_2017/Combine/All/2017___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/nJetSF_2018/Combine/All/2018___Combined.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Mar19_Baseline_2017/Combine/All/2017___HTOnly___5x5.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Mar19_Baseline_2018/Combine/All/2018___HTOnly___5x5.root", "read")
f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Apr8_nJetSF_2017/Combine/All/2017___HTOnly___5x5.root", "read")
# f = ROOT.TFile.Open("/eos/user/n/nmangane/analysis/Apr8_nJetSF_2018/Combine/All/2018___HTOnly___5x5.root", "read")
fkeys = [kk.GetName() for kk in f.GetListOfKeys()]
histos = dict()
name_format="$ERA___$PROCESS___$CHANNEL___$WINDOW___$CATEGORY$BLIND___$VARIABLE___$SYSTEMATIC"
erasDict = {"2018": ["2018"], "2017": ["2017"], "RunII": ["2017", "2018"]}
era = "2017"
# era = "2018"
channels = ["ElMu", "MuMu", "ElEl"]
# channels = ["ElMu"]
# channels = ["MuMu"]
# channels = ["ElEl"]
var = "HT"
# syst = "OSDL_2018_top_pTDown"
syst = "nom"
# tagger="DeepCSV"
tagger="DeepJet"
htcut="500"
# htcut="350"
btagcat="2"
# btagcat="1"
# btagcat="0"
for k, v in processGroups.items():
    print(k)
    keys = dict()
    histos[k] = dict()
    for n in ["4", "5", "6", "7", "8+"]:
        name = name_format.replace("$ERA", era).replace("$PROCESS", k).replace("$WINDOW", "ZMETWindow").replace("$CATEGORY", "HT{htcut}_nMedium{tagger}B{nbtag}_nJet{njet}".format(htcut=htcut, njet=n, nbtag=btagcat, tagger=tagger)).replace("$VARIABLE", var).replace("$SYSTEMATIC", syst).replace("$BLIND", "")
        histos[k][n] = None
        keys[n], blind, fails = group(fkeys, erasDict[era], v.get("Names"), channels=channels, categories=["HT{htcut}_nMedium{tagger}B{nbtag}_nJet{njet}".format(htcut=htcut, njet=n, nbtag=btagcat, tagger=tagger)], variable=var, systematic=syst, input_format=name_format)
        assert len(list(set(keys[n]))) == len(keys[n]), "Duplicate keys detected"
        # if len(list(set(keys[n]))) != len(keys[n]):
        #     print("\n\n\n\n\n\n", keys[n], "\n\n\n")
        for nhist, histkey in enumerate(keys[n]):
            try:
                hist = f.Get(histkey)
                if nhist == 0:
                    histos[k][n] = hist.Clone(name)
                else:
                    histos[k][n].Add(hist)
            except:
                print(histkey)
        # print(keys[n])
        print(k, " Blind: ", blind, " Succeeded/Failed to find match: ", len(keys[n]), len(fails))

print("\neras = ", erasDict[era], " channels = ", channels, " syst = ", syst)
print("nJet,Data,Data-nonttbar/ttbar,Data/Bkg,Data/(Sgnl+Bkg),", ",".join(['ttnobb','ttbb','singletop','ttH','ttVJets','ttultrarare','ewk', 'tttt']))
for n in ['4', '5', '6', '7', '8+']:
    print("{}j,{},{:.4f},{:.4f},{:s}"\
          .format(n, 
                  histos['Data'][n].Integral(),
                  (histos['Data'][n].Integral() - sum([histos[s][n].Integral() for s in ['singletop','ewk', 'ttH', 'ttVJets', 'ttultrarare']]))/sum([histos[s][n].Integral() for s in ['ttnobb','ttbb']]),
                  histos['Data'][n].Integral()/sum([histos[s][n].Integral() for s in ['ttnobb','ttbb','singletop','ttH','ttVJets','ttultrarare','ewk', 'tttt']]),
                  ",".join(["{:.4f}".format(histos[s][n].Integral()) for s in ['ttnobb','ttbb','singletop','ttH','ttVJets','ttultrarare','ewk', 'tttt']])
              )
      )
#Unfinished...
# print("{}j,{},{:.4f},{:.4f},{:s}"\
#       .format("4+", 
#               sum([histos['Data'][n].Integral() for n in ['4', '5', '6', '7', '8+']]),
#               sum([(histos['Data'][n].Integral() - sum([histos[s][n].Integral() for s in ['singletop','ewk', 'ttH', 'ttVJets', 'ttultrarare']]))/sum([histos[s][n].Integral() for s in ['ttnobb','ttbb']]) for n in ['4', '5', '6', '7', '8+']]),
#               sum([histos['Data'][n].Integral() for n in ['4', '5', '6', '7', '8+']])/sum([sum([histos[s][n].Integral() for s in ['ttnobb','ttbb','singletop','ttH','ttVJets','ttultrarare','ewk', 'tttt']]) for n in ['4', '5', '6', '7', '8+']]),
#               ",".join(["{:.4f}".format(histos[s][n].Integral()) for s in ['ttnobb','ttbb','singletop','ttH','ttVJets','ttultrarare','ewk', 'tttt']])
#           )
#   )
    
