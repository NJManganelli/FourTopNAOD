from __future__ import print_function, division
import os
import time
import pwd
import datetime
import collections
import pprint
import math
import array
import json
import copy
import argparse
import uuid
import pdb
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

ROOT.gROOT.SetBatch(True)

def main(analysisDirectory, era, channel, variable, verbose=0):
    categoriesOfInterest = ['HT500_nMediumDeepJetB2_nJet4', 'HT500_nMediumDeepJetB2_nJet5', 'HT500_nMediumDeepJetB2_nJet6',
                            'HT500_nMediumDeepJetB2_nJet7', 'HT500_nMediumDeepJetB2_nJet8+',
                            'HT500_nMediumDeepJetB3_nJet4', 'HT500_nMediumDeepJetB3_nJet5', 'HT500_nMediumDeepJetB3_nJet6',
                            'HT500_nMediumDeepJetB3_nJet7', 'HT500_nMediumDeepJetB3_nJet8+',
                            'HT500_nMediumDeepJetB4+_nJet4', 'HT500_nMediumDeepJetB4+_nJet5', 'HT500_nMediumDeepJetB4+_nJet6',
                            'HT500_nMediumDeepJetB4+_nJet7', 'HT500_nMediumDeepJetB4+_nJet8+',
    ]
    histogramFile = "$ADIR/Combine/CI_$ERA_$CHANNEL_$VAR.root".replace("$ADIR", analysisDir)\
                                                              .replace("$ERA", era)\
                                                              .replace("$CHANNEL", channel)\
                                                              .replace("$VAR", variable)\
                                                              .replace("//", "/") 
    f = ROOT.TFile.Open(histogramFile, "read")
    keys = [k.GetName() for k in f.GetListOfKeys()]
    if len(keys[0].split("___")) == 4: #format post-fill-(histograms/combine)
        processes = sorted(list(set([k.split("___")[0] for k in keys])))
        categories = sorted(sorted(list(set([k.split("___")[1] for k in keys])), key=lambda j : j.split("nJet")[-1]), key=lambda j: j.split("nMediumDeep")[-1])
        variables = list(set([k.split("___")[2] for k in keys]))
        systematics = list(set([k.split("___")[3] for k in keys]))
    else:
        raise RuntimeError("Unhandled histogram key format: length: {} key: {}".format(len(keys[0].split("___")), keys[0]))

    supportedTypes = (ROOT.TH1) #, ROOT.TH2, ROOT.TH3)

    if verbose > 0:
        print("Processes: {}".format(processes))
        print("Categories: {}".format(categories))
        print("Variables: {}".format(variables))
        print("Systematics: {}".format(systematics))
    output_file = ROOT.TFile.Open("prefit___" + histogramFile.split("/")[-1], "recreate")
    for category in categories:
        # filter for category
        c_keys = [key for key in keys if category in key]
        for variable in variables:
            dir_name = category + "___" + variable
            output_file.mkdir(dir_name)
            for process in processes:
                # filter for process and variable, only varying in systematics
                s_keys = [key for key in c_keys if key.startswith(process) and variable in key]
                central_histo = f.Get("___".join([process, category, variable, "nom"]))
                if process == "data_obs":
                    final_histo = central_histo.Clone(central_histo.GetName().replace("___nom", "___TotalWithError"))
                else:
                    v_keys = [key for key in s_keys if not key.endswith("___nom")]
                    syst_histos = [f.Get(key) for key in v_keys] + get_xsec_histogram(central_histo, process) + get_lumi_histogram(central_histo, process, era)
                    n_before = len(syst_histos)
                    syst_histos = [h for h in syst_histos if isinstance(h, supportedTypes)]
                    n_after = len(syst_histos)
                    if n_after > n_before:
                        print(process, category, variable, n_after, n_before)
                    print(category, variable, process)
                    final_histo = compute_quadrature_naive(syst_histos, central_histo, verbose=verbose)
                final_histo.SetDirectory(0)
                # write the histo
                # current_dir = ROOT.gDirectory
                # try:
                #     output_file.cd()
                #     output_file.cd(dir_name)
                # except:
                #     output_file.cd()
                #     output_file.mkdir(dir_name)
                output_file.cd(dir_name)
                final_histo.Write(process)
    # Need to write TotalBkg, TotalProcs, TotalSig too... what a clusterfuck
    dirs = output_file.GetListOfKeys()
    for dir in dirs:
        output_file.cd(dir.GetName())
        curr_dir = ROOT.gDirectory
        TotalSig = None
        TotalBkg = None
        hkeys = []
        hkeys = [kk.GetName() for kk in curr_dir.GetListOfKeys()]
        for hkey in hkeys:
            histo = curr_dir.Get(hkey)
            histo.SetDirectory(0)
            # Signal
            if hkey in ["tttt"]:
                if TotalSig is None:
                    TotalSig = histo.Clone("TotalSig")
            # Data
            elif hkey in ["data_obs"]:
                continue
            # Background
            else:
                if TotalBkg is None:
                    TotalBkg = histo.Clone("TotalBkg")
                else:
                    TotalBkg.Add(histo)
        TotalProcs = TotalSig.Clone("TotalProcs")
        TotalProcs.Add(TotalBkg)
        TotalSig.Write()
        TotalBkg.Write()
        TotalProcs.Write()
        output_file.cd()
    output_file.Close()
    f.Close()
                                

def get_xsec_histogram(histo, process):
    # OSDL_RunII_ttnobb_xsec                   lnN     0.911/1.111     -               -               -               -               -               -    
    # OSDL_RunII_tt_ActCorr                    lnN     1.054           -               -               -               -               -               -                
    # OSDL_RunII_ttHF                          lnN     -               1.080           -               -               -               -               -
    # OSDL_RunII_ttbb_xsec                     lnN     -               0.911/1.111     -               -               -               -               -    
    # OSDL_RunII_ttH_xsec                      lnN     -               -               1.20            -               -               -               -
    # OSDL_RunII_ttVJets_xsec                  lnN     -               -               -               1.20            -               -               -
    # OSDL_RunII_ttultrarare_xsec              lnN     -               -               -               -               1.50            -               -
    # OSDL_RunII_ewk_xsec                      lnN     -               -               -               -               -               1.038           -
    scales = None
    if process == "EWK":
        scales = [1.038, 1/1.038]
    elif process == "tt + !bb":
        scales = [math.sqrt(1.111**2 + 1.054**2), 1/math.sqrt(1.089**2 + 1.054**2)]
    elif process == "tt + bb":
        scales = [math.sqrt(1.111**2 + 1.08**2), 1/math.sqrt(1.089**2 + 1.08**2)]
    elif process == "tt + H":
        scales = [1.2, 1/1.2]
    elif process == "tt + rare":
        scales = [1.5, 1/1.5]
    elif process == "tt + V":
        scales = [1.2, 1/1.2]
    elif process == "tttt":
        scales = [1, 1]
    elif process == "data_obs":
        scales = [1, 1]
    else:
        raise ValueError(f"Process {process} not recognized for xsec scaling")
    hUP = histo.Clone(histo.GetName().replace("___nom", "___xsecUp"))
    hDOWN = histo.Clone(histo.GetName().replace("___nom", "___xsecDown"))
    return [hUP * scales[0], hDOWN * scales[1]]

def get_lumi_histogram(histo, process, era):
    # OSDL_2018_leptonSF                     lnN     1.03
    # OSDL_2017_lumi                           lnN     1.020
    # OSDL_2018_lumi                           lnN     1.015
    # OSDL_CL161718_lumi_2018                       lnN     1.020
    # OSDL_CL1718_lumi_2018                         lnN     1.002
    # OSDL_CL161718_lumi_2017                       lnN     1.009
    # OSDL_CL1718_lumi_2017                         lnN     1.006
    # 2018_lumi = OSDL_2018_lumi + OSDL_CL161718_lumi_2018 + OSDL_CL1718_lumi_2018
    lumi_2018 = math.sqrt(1.015**2 + 1.020**2 + 1.002**2)
    lumi_2017 = math.sqrt(1.020**2 + 1.009**2 + 1.006**2)
    lumi_runii = math.sqrt((59/101 * 1.020 + 42/101 * 1.009)**2 + (59/101 * 1.002 + 42/101 * 1.006)**2 + (59/101 * 1.015)**2 + (42/101 * 1.020)**2)
    scales = None
    if era == "RunII":
        scales = [lumi_runii, 1/lumi_runii]
    elif era == "2018":
        scales = [lumi_2018, 1/lumi_2018]
    elif era == "2017":
        scales = [lumi_2017, 1/lumi_2017]
    else:
        raise ValueError(f"Era {era} not recognized for lumi scaling")
    hUP = histo.Clone(histo.GetName().replace("___nom", "___lumiUp"))
    hDOWN = histo.Clone(histo.GetName().replace("___nom", "___lumiDown"))
    return [hUP * scales[0], hDOWN * scales[1]]

def compute_quadrature_naive(all_syst_histos, central_histo, verbose=0):
    # diff_histos = [histo - central_histo for histo in all_syst_histos]
    #Add in quadrature all the negative and all the positive shifts, separately per bin, then symmetrize or take the absmax. 
    #Take the central histo for anything but data and add in quadrature this per-bin error (to keep the MC stat uncertainty)

    nbins = central_histo.GetNbinsX() + 2
    diff_up = [0] * nbins
    diff_down = [0] * nbins
    # for ndiff, diff_histo in enumerate(diff_histos):
    for ndiff, diff_histo in enumerate(all_syst_histos):
        if verbose > 1:
            print(ndiff, diff_histo.GetName(), diff_histo.Integral() - central_histo.Integral())
        for nbin in range(nbins):
            if ndiff == 0:
                if verbose > 0:
                    print("nbin, central, syst, bin_diff, sum(diff_up**2), sum(diff_down**2)")
                diff_up[nbin] += central_histo.GetBinError(nbin)**2
                diff_down[nbin] += central_histo.GetBinError(nbin)**2
            # bin_diff = diff_histo.GetBinContent(nbin)
            bin_diff = diff_histo.GetBinContent(nbin) - central_histo.GetBinContent(nbin)
            if bin_diff >= 0:
                diff_up[nbin] += bin_diff**2
            else:
                diff_down[nbin] += bin_diff**2
            if nbin == 5 and verbose > 0:
                print( nbin, central_histo.GetBinContent(nbin), diff_histo.GetBinContent(nbin), bin_diff, diff_up[nbin], diff_down[nbin])

    quad_histo = central_histo.Clone(central_histo.GetName().replace("___nom", "___TotalWithError"))
    for nbin in range(nbins):
        diff_up[nbin] = math.sqrt(diff_up[nbin])
        diff_down[nbin] = math.sqrt(diff_down[nbin])
        quad_histo.SetBinContent(nbin, central_histo.GetBinContent(nbin))
        quad_histo.SetBinError(nbin, (diff_up[nbin] + diff_down[nbin]) / 2)
    return quad_histo



    # merge = dict()
    # for mera in eras:
    #     merge[mera] = dict()
    #     for mprocess in processes:
    #         merge[mera][mprocess] = dict()
    #         for mvariable in variables:
    #             if mvariable not in [variable, variable + "Unweighted"]:
    #                 continue
    #             merge[mera][mprocess][mvariable] = dict()
    #             for msyst in systematics:
    #                 merge[mera][mprocess][mvariable][msyst] = dict()
    #                 for mcategory in ["nMediumDeepJetB2", "nMediumDeepJetB3", "nMediumDeepJetB4+"]:
    #                     merge[mera][mprocess][mvariable][msyst][mcategory] = []

    # for key in keys:
    #     mera, mprocess, mchannel, mwindow, mcategory, mvariable, msyst = key.split("___")
    #     if mvariable not in [variable, variable + "Unweighted"] or mera != era:
    #         continue
    #     mcat = mcategory.split("_")[-2].replace("BLIND", "")
    #     merge[mera][mprocess][mvariable][msyst][mcat].append(key)
    
    # outputHistogramFile = histogramFile.replace("Combined", "").replace(".root", "MergedChannelsJets_" + variable + ".root")
    # print("Opening {}".format(outputHistogramFile))
    # of = ROOT.TFile.Open(outputHistogramFile, "recreate")
    # of.cd()
    # for mera, submerge in merge.items():
    #     for mprocess, subsubmerge in submerge.items():
    #         print("Writing results for {}".format(mprocess))
    #         for mvariable, subsubsubmerge in subsubmerge.items():
    #             for msyst, subsubsubsubmerge in subsubsubmerge.items():
    #                 print("*", end="")
    #                 for mcat, subsubsubsubsubmerge in subsubsubsubmerge.items():
    #                     mergeName = "___".join([mera, mprocess, "All", "ZWindow", "MergedChannelsJets_" + mcat, mvariable, msyst])
    #                     hist = None
    #                     blind = len([hk for hk in subsubsubsubsubmerge if "blind" in hk.lower()]) > 0
    #                     for histKey in subsubsubsubsubmerge:
    #                         rootobj = f.Get(histKey)
    #                         if isinstance(rootobj, supportedTypes):
    #                             if hist is None:
    #                                 hist = rootobj.Clone(mergeName)
    #                             else:
    #                                 hist.Add(rootobj)
    #                     if blind:
    #                         for bin in range(hist.GetNbinsX() + 2):
    #                             hist.SetBinContent(bin, 0)
    #                             hist.SetBinError(bin, 0)
    #                     if hist is not None:
    #                         pass
    #                         # hist.Write()
    #             print("")
    # f.Close()
    # of.Close()
    print("Done")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge Jet categories and decay channels for the purpose of btag-dependent systematic studies')
    parser.add_argument('--analysisDirectory', dest='analysisDirectory', action='store', type=str, default="/eos/user/$U/$USER/analysis/$DATE", required=True,
                        help='output directory path defaulting to "."')
    parser.add_argument('--era', dest='era', type=str, default="2017", required=True, choices=["2017", "2018", "RunII"],
                        help='era for plotting, which deduces the lumi only for now')
    parser.add_argument('--channel', dest='channel', type=str, default="ElMu", required=True, choices=["ElMu", "ElEl", "MuMu", "All"],
                        help='Decay channel')
    parser.add_argument('--variable', dest='variable', type=str, default="HT", required=True,
                        help='Variable')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')

    #Parse the arguments
    args = parser.parse_args()
    uname = pwd.getpwuid(os.getuid()).pw_name
    uinitial = uname[0]
    dateToday = datetime.date.today().strftime("%b-%d-%Y")
    analysisDir = args.analysisDirectory.replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday)
    verbose = args.verbose
    main(analysisDir, era=args.era, channel=args.channel, variable=args.variable, verbose=verbose)
