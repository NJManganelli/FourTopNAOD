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
import matplotlib.pyplot as plt
f = ROOT.TFile.Open("HTResolution_tttt.root", "read")
k = [kk.GetName() for kk in f.GetListOfKeys() if "HTminusGenMatchedHT" in kk.GetName()]
# systs = list(set([kk.split("___")[-1] for kk in k]))
# channels = list(set([kk.split("___")[-1] for kk in k]))
# years = list(set([kk.split("___")[-1] for kk in k]))

#Get histograms
sample="tttt"
h = dict()
# for nJet in ["nJet4", "nJet5", "nJet6", "nJet7", "nJet8+"]:
for nJet in ["nJet4Plus"]:
    add_list = cartesian_product_list(name_format="$ERA___"+sample+"___$CHANNELWINDOW___HT500_nMedium$BTAG_$NJET___HTminusGenMatchedHT___$SYST",
                                      name_tuples=[("$ERA", ["2017", "2018"]),
                                                   ("$CHANNELWINDOW", ["MuMu___ZWindowMET0p0Width15p0", "ElEl___ZWindowMET0p0Width15p0", "ElMu___ZWindowMET0Width0"]),
                                                   ("$BTAG", ["DeepJetB1", "DeepJetB2", "DeepJetB3", "DeepJetB4+"]),
                                                   ("$NJET", ["nJet4", "nJet5", "nJet6", "nJet7", "nJet8+"]),
                                                   ("$SYST", ["nom"])])
    for hnum, hname in enumerate(add_list):        
        if hnum==0:
            h[nJet] = f.Get(hname)
            h[nJet].SetDirectory(0)
        else:
            htemp = f.Get(hname)
            h[nJet].Add(htemp)
f.Close()

edges = dict()
centers = dict()
means = dict()
stddevs = dict()
#Perform sliced projections and do a gaussian fit, getting the mean and standard deviation of each.
for nJet, h2d in h.items():
    edges[nJet] = [h2d.GetXaxis().GetBinLowEdge(i) for i in range(h2d.GetXaxis().GetNbins())]
    centers[nJet] = [h2d.GetXaxis().GetBinCenter(i) for i in range(h2d.GetXaxis().GetNbins())]
    means[nJet] = []
    stddevs[nJet] = []
    for j in range(len(edges[nJet])-1):
        if edges[nJet][j] < 1000:
            h2d.GetXaxis().SetRangeUser(edges[nJet][j], edges[nJet][j+1])
        else:
            h2d.GetXaxis().SetRangeUser(edges[nJet][j-1], edges[nJet][min(j+2, len(edges[nJet])-1)])
        slc = h2d.ProjectionY()
        if slc.GetEntries() < 10:
            means[nJet].append(0)
            stddevs[nJet].append(0)
            continue
        _ = slc.Fit("gaus")
        func = slc.GetFunction("gaus")
        res = func.GetParameters()
        scale, mean, stddev = res[0], res[1], res[2]
        means[nJet].append(mean)
        stddevs[nJet].append(stddev)
        # print(nJet, edges[j], mean, stddev)


    edges[nJet] = np.asarray(edges[nJet])
    centers[nJet] = np.asarray(centers[nJet])
    means[nJet] = np.asarray(means[nJet])
    stddevs[nJet] = np.asarray(stddevs[nJet])
        
fig, subplots = plt.subplots(2, #n_ypads,
                             1,
                             #gridspec_kw=dict(height_ratios=height_ratios,
                             #                 width_ratios=width_ratios,
                             #                 hspace=hspace,
                             #                 wspace=wspace),
                             figsize=(10, 10),
                             sharex=False,
                             sharey=False)
for nJet in edges.keys():
    subplots[0].stairs(
            edges=edges[nJet],
            #baseline=(bkg_tot.values() - np.sqrt(bkg_tot.variances())) / bkg_tot.values(),
            values=means[nJet],
            #hatch="....",
            label=nJet+" gaus mean",
            #facecolor="none",
            #linewidth=0,
            #color="blue",
        )
    subplots[0].legend()
    subplots[0].set_ylim(-60, 60)
    subplots[0].set_ylabel("Gaussian fit mean [GeV]")
    subplots[0].set_xlabel("Reco HT [GeV]")
    subplots[0].set_title("gaussian mean in fit to HT-GenHT(" + sample + ")")

    subplots[1].stairs(
            edges=edges[nJet],
            #baseline=(bkg_tot.values() - np.sqrt(bkg_tot.variances())) / bkg_tot.values(),
            values=stddevs[nJet],
            #hatch="....",
            label=nJet+" gaus stddev",
            #facecolor="none",
            #linewidth=0,
            #color="blue",
        )
    subplots[1].legend()
    subplots[1].set_ylim(0, 100)
    subplots[1].set_ylabel("Gaussian fit stddev [GeV]")
    subplots[1].set_xlabel("Reco HT [GeV]")
    subplots[1].set_title("gaussian stddev in fit to HT-GenHT(" + sample + ")")
fig.savefig("HTResolutionFit.pdf")
