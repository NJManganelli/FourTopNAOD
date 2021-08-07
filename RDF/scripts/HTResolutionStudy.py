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

import ROOT
import numpy as np
import array
import pdb
import matplotlib.pyplot as plt
# f = ROOT.TFile.Open("HTResolution_tttt.root", "read")
f = ROOT.TFile.Open("HTResolutionStudyV2.root", "read")
k = [kk.GetName() for kk in f.GetListOfKeys() if "HTminusGenMatchedHT" in kk.GetName()]
# systs = list(set([kk.split("___")[-1] for kk in k]))
# channels = list(set([kk.split("___")[-1] for kk in k]))
# years = list(set([kk.split("___")[-1] for kk in k]))

#Get histograms
sample="tttt"
h = dict()
# for nJet in ["nJet4", "nJet5", "nJet6", "nJet7", "nJet8+"]:
for nJet in ["nJet4Plus"]: #2017___tttt___MuMu___ZWindowMET0p0Width15p0___HT500_nMediumDeepJetB2_nJet8+___HTminusGenMatchedHT___
    add_list = cartesian_product_list(name_format="$ERA___"+sample+"___$CHANNELWINDOW___HT500_nMedium$BTAG_$NJET___HTminusGenMatchedHT___$SYST",
                                      name_tuples=[("$ERA", ["2017", "2018"]),
                                                   ("$CHANNELWINDOW", ["MuMu___ZWindowMET0p0Width15p0", "ElEl___ZWindowMET0p0Width15p0", "ElMu___ZWindowMET0Width0"]),
                                                   # ("$BTAG", ["DeepJetB1", "DeepJetB2", "DeepJetB3", "DeepJetB4+"]),
                                                   ("$BTAG", ["DeepJetB2"]), #Actually B2+, but I goofed... fixed for the next iteration, if there will be one
                                                   ("$NJET", ["nJet4", "nJet5", "nJet6", "nJet7", "nJet8+"]),
                                                   ("$SYST", ["nom"])])
    for hnum, hname in enumerate(add_list):        
        if hnum==0:
            h[nJet] = f.Get(hname)
            try:
                h[nJet].SetDirectory(0)
            except:
                pdb.set_trace()
        else:
            htemp = f.Get(hname)
            h[nJet].Add(htemp)
f.Close()

edges = dict()
centers = dict()
means = dict() #mean and SD from the fit in each slice
merrs = dict()
stddevs = dict()
sderrs = dict() 
reshists = dict() #TH1
resfunc = dict() #TF1
resfit = dict() #Numpy and matplotlib plotting
#Perform sliced projections and do a gaussian fit, getting the mean and standard deviation of each.
for nJet, h2d in h.items():
    # edges[nJet] = [h2d.GetXaxis().GetBinLowEdge(i) for i in range(h2d.GetXaxis().GetNbins())]
    # centers[nJet] = [h2d.GetXaxis().GetBinCenter(i) for i in range(h2d.GetXaxis().GetNbins())]
    edges[nJet] = [500.0, 505.0, 510.0, 515.0, 520.0, 525.0, 530.0, 535.0, 540.0, 545.0, 550.0, 555.0, 560.0, 565.0, 570.0, 575.0, 580.0, 585.0, 590.0, 595.0, 600.0, 605.0, 610.0, 615.0, 620.0, 625.0, 630.0, 635.0, 640.0, 645.0, 650.0, 655.0, 660.0, 665.0, 670.0, 675.0, 680.0, 685.0, 690.0, 695.0, 700.0, 705.0, 710.0, 715.0, 720.0, 725.0, 730.0, 735.0, 740.0, 745.0, 750.0, 755.0, 760.0, 765.0, 770.0, 775.0, 780.0, 785.0, 790.0, 795.0, 800.0, 805.0, 810.0, 815.0, 820.0, 825.0, 830.0, 835.0, 840.0, 845.0, 850.0, 855.0, 860.0, 865.0, 870.0, 875.0, 880.0, 885.0, 890.0, 895.0, 900.0, 905.0, 910.0, 915.0, 920.0, 925.0, 930.0, 935.0, 940.0, 945.0, 950.0, 955.0, 960.0, 965.0, 970.0, 975.0, 980.0, 985.0, 990.0, 995.0, 1000.0, 1005.0, 1010.0, 1015.0, 1020.0, 1025.0, 1030.0, 1035.0, 1040.0, 1045.0, 1050.0, 1055.0, 1060.0, 1065.0, 1070.0, 1075.0, 1080.0, 1085.0, 1090.0, 1095.0, 1100.0, 1105.0, 1110.0, 1115.0, 1120.0, 1125.0, 1130.0, 1135.0, 1140.0, 1145.0, 1150.0, 1155.0, 1160.0, 1165.0, 1170.0, 1175.0, 1180.0, 1185.0, 1190.0, 1195.0, 1200.0, 1205.0, 1210.0, 1215.0, 1220.0, 1225.0, 1230.0, 1235.0, 1240.0, 1245.0, 1250.0, 1255.0, 1260.0, 1265.0, 1270.0, 1275.0, 1280.0, 1285.0, 1290.0, 1295.0, 1300.0, 1305.0, 1310.0, 1315.0, 1320.0, 1325.0, 1330.0, 1335.0, 1340.0, 1345.0, 1350.0, 1355.0, 1360.0, 1365.0, 1370.0, 1375.0, 1380.0, 1385.0, 1390.0, 1395.0, 1400.0, 1405.0, 1410.0, 1415.0, 1420.0, 1425.0, 1430.0, 1435.0, 1440.0, 1445.0, 1450.0, 1455.0, 1460.0, 1465.0, 1470.0, 1475.0, 1480.0, 1485.0, 1490.0, 1495.0, 1500.0, 1505.0, 1510.0, 1515.0, 1520.0, 1525.0, 1530.0, 1535.0, 1540.0, 1545.0, 1550.0, 1555.0, 1560.0, 1565.0, 1570.0, 1575.0, 1580.0, 1585.0, 1590.0, 1595.0, 1600.0, 1605.0, 1610.0, 1615.0, 1620.0, 1625.0, 1630.0, 1635.0, 1640.0, 1645.0, 1650.0, 1655.0, 1660.0, 1665.0, 1670.0, 1675.0, 1680.0, 1685.0, 1690.0, 1695.0, 1700.0, 1705.0, 1710.0, 1715.0, 1720.0, 1725.0, 1730.0, 1735.0, 1740.0, 1745.0, 1750.0, 1755.0, 1760.0, 1765.0, 1770.0, 1775.0, 1780.0, 1785.0, 1790.0, 1795.0, 1800.0, 1805.0, 1810.0, 1815.0, 1820.0, 1825.0, 1830.0, 1835.0, 1840.0, 1845.0, 1850.0, 1855.0, 1860.0, 1865.0, 1870.0, 1875.0, 1880.0, 1885.0, 1890.0, 1895.0, 1900.0, 1905.0, 1910.0, 1915.0, 1920.0, 1925.0, 1930.0, 1935.0, 1940.0, 1945.0, 1950.0, 1955.0, 1960.0, 1965.0, 1970.0, 1975.0, 1980.0, 1985.0, 1990.0, 1995.0, 2000.0, 2005.0]
    # edges[nJet] = [500.0, 520.0, 540.0, 560.0, 580.0, 600.0, 620.0, 640.0, 660.0, 680.0, 700.0, 720.0, 740.0, 760.0, 780.0, 800.0, 820.0, 850.0, 880.0, 910.0, 940.0, 970.0, 1000.0, 1050.0, 1100.0, 1150.0, 1200.0, 1250.0, 1300.0, 1350.0, 1400.0, 1450.0, 1500.0, 1550.0, 1600.0, 1650.0, 1700.0, 1750.0, 1800.0, 2000.0]
    edges[nJet] = [500.0, 550.0, 600.0, 650.0, 700.0, 750.0, 800.0, 850.0, 900.0, 950.0, 1000.0, 1050.0, 1100.0, 1150.0, 1200.0, 1250.0, 1300.0, 1350.0, 1400.0, 1450.0, 1500.0, 1550.0, 1600.0, 1650.0, 1700.0, 1750.0, 1800.0, 2000.0]
    centers[nJet] = [edge + 2.5 for edge in edges[nJet]]
    means[nJet] = []
    stddevs[nJet] = []
    merrs[nJet] = []
    sderrs[nJet] = []
    reshists[nJet] = h2d.Clone("reshist").ProjectionX()
    reshists[nJet].Reset("ICESM")
    reshists[nJet] = reshists[nJet].Rebin(len(edges[nJet])-1, "", array.array('d', edges[nJet]))
    # reshists[nJet] = reshists[nJet].Rebin(10)
    c = ROOT.TCanvas()
    for j in range(len(edges[nJet])-1):
        if edges[nJet][j] < 1000:
            h2d.GetXaxis().SetRangeUser(edges[nJet][j], edges[nJet][j+1])
        else:
            h2d.GetXaxis().SetRangeUser(edges[nJet][j-1], edges[nJet][min(j+2, len(edges[nJet])-1)])
        slc = h2d.ProjectionY()
        if slc.GetEntries() < 10 or edges[nJet][j+1] <= 500.00:
            means[nJet].append(0)
            stddevs[nJet].append(0)
            continue
        _ = slc.Fit("gaus")
        func = slc.GetFunction("gaus")
        slc.Draw("HIST")
        func.Draw("SAME")
        c.SaveAs("HT_"+str(edges[nJet][j])+"to"+str(edges[nJet][j+1])+"_sliceFit.pdf")
        # res = func.GetParameters()
        scale, mean, stddev = func.GetParameter(0), func.GetParameter(1), func.GetParameter(2)
        serr, merr, sderr = func.GetParError(0), func.GetParError(1), func.GetParError(2)
        assert func.GetParName(2) == 'Sigma'
        means[nJet].append(mean)
        stddevs[nJet].append(stddev)
        merrs[nJet].append(merr)
        sderrs[nJet].append(sderr)
        reshists[nJet].SetBinContent(j, stddev)
        reshists[nJet].SetBinError(j, sderr)
        # print(nJet, edges[nJet][j], mean, merr, stddev, sderr)


    edges[nJet] = np.asarray(edges[nJet])
    centers[nJet] = np.asarray(centers[nJet])
    means[nJet] = np.asarray(means[nJet])
    merrs[nJet] = np.asarray(merrs[nJet])
    stddevs[nJet] = np.asarray(stddevs[nJet])
    sderrs[nJet] = np.asarray(sderrs[nJet])

    #Perform the resolution fit, using a - exp(b + c*HT)
    rescanvas = ROOT.TCanvas()

    resfunc[nJet] = ROOT.TF1("resfunc_"+nJet, "[0] - expo(1)", 500, 2000)
    reshists[nJet].Fit(resfunc[nJet])
    constant, expshift, exprate = resfunc[nJet].GetParameter(0), resfunc[nJet].GetParameter(1), resfunc[nJet].GetParameter(2)
    constant_err, expshift_err, exprate_err = resfunc[nJet].GetParError(0), resfunc[nJet].GetParError(1), resfunc[nJet].GetParError(2)
    resfit[nJet] = constant * np.ones_like(centers[nJet]) - np.exp(expshift + exprate * centers[nJet])
    reshists[nJet].SetTitle("t#bar{t}t#bar{t} Resolution (Fit: "+str(constant)+" - e^{"+str(exprate)+"* H_{T} "+str(expshift)+"}); H_{T} [GeV]; Resolution [GeV]")
    reshists[nJet].Draw("HIST")
    resfunc[nJet].Draw("SAME")
    rescanvas.Update()
    rescanvas.SaveAs(nJet+"_ROOT_ResolutionFit.pdf")
    print("constant = {} += {}".format(constant, constant_err))
    print("expshift = {} += {}".format(expshift, expshift_err))
    print("exprate = {} += {}".format(exprate, exprate_err))
nYPads = 1
fig, subplots = plt.subplots(nYPads, #n_ypads,
                             1,
                             #gridspec_kw=dict(height_ratios=height_ratios,
                             #                 width_ratios=width_ratios,
                             #                 hspace=hspace,
                             #                 wspace=wspace),
                             figsize=(10, 10),
                             sharex=False,
                             sharey=False)
for nJet in edges.keys():
    if nYPads > 1:
        subplots[0].stairs(
                edges=edges[nJet],
                #baseline=(bkg_tot.values() - np.sqrt(bkg_tot.variances())) / bkg_tot.values(),
                values=stddevs[nJet],
                #hatch="....",
                label=nJet+" HT resolution",
                #facecolor="none",
                #linewidth=0,
                #color="blue",
            )
        subplots[0].plot(centers[nJet], 
                         resfit[nJet], 
                         label="fit: 69.88 - exp(4.168 - 0.00107 * HT)",
                         color="red")
        # 69.8816304839025 4.28377894418222
        # 4.168549245620038 0.02944828321720983
        # -0.001075477399833888 0.00017640731635102308
        subplots[0].legend()
        subplots[0].set_ylim(25, 75)
        subplots[0].set_ylabel("Gaussian fit stddev [GeV]")
        subplots[0].set_xlabel("Reco HT [GeV]")
        subplots[0].set_title("gaussian stddev in fit to HT-GenHT(" + sample + ")")
    
        subplots[1].stairs(
                edges=edges[nJet],
                #baseline=(bkg_tot.values() - np.sqrt(bkg_tot.variances())) / bkg_tot.values(),
                values=means[nJet],
                #hatch="....",
                label=nJet+" gaus mean",
                #facecolor="none",
                #linewidth=0,
                #color="blue",
            )
        subplots[1].legend()
        subplots[1].set_ylim(-60, 60)
        subplots[1].set_ylabel("Gaussian fit mean [GeV]")
        subplots[1].set_xlabel("Reco HT [GeV]")
        subplots[1].set_title("gaussian mean in fit to HT-GenHT(" + sample + ")")
    else:
        subplots.stairs(
                edges=edges[nJet],
                #baseline=(bkg_tot.values() - np.sqrt(bkg_tot.variances())) / bkg_tot.values(),
                values=stddevs[nJet],
                #hatch="....",
                label=nJet+" HT resolution",
                #facecolor="none",
                #linewidth=0,
                #color="blue",
            )
        subplots.plot(centers[nJet], 
                         resfit[nJet], 
                         label="fit: 69.88 - exp(4.168 - 0.00107 * HT)",
                         color="red")
        # 69.8816304839025 4.28377894418222
        # 4.168549245620038 0.02944828321720983
        # -0.001075477399833888 0.00017640731635102308
        subplots.legend()
        subplots.set_ylim(25, 75)
        subplots.set_ylabel("Gaussian fit stddev [GeV]")
        subplots.set_xlabel("Reco HT [GeV]")
        subplots.set_title("gaussian stddev in fit to HT-GenHT(" + sample + ")")
    
    
fig.savefig("HTResolutionFit_ef.pdf")
