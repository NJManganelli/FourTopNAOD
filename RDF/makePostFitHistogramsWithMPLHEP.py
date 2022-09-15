from __future__ import annotations
from typing import Any, Optional
#import ROOT
import numpy as np
import uproot
import hist
import matplotlib.pyplot as plt
import mplhep
import argparse
from copy import deepcopy
from rich.progress import track

from ColumnarFTA.histtools.manipulation import merge_within_categorical_axis

plt.style.use(mplhep.style.CMS)

class key_btags:
    def __init__(self, obj, *args):
        self.obj = obj
    def __lt__(self, other):
        return enum_btags(self.obj) < enum_btags(other.obj)
    def __gt__(self, other):
        return enum_btags(self.obj) > enum_btags(other.obj)
    def __eq__(self, other):
        return enum_btags(self.obj) == enum_btags(other.obj)
    def __le__(self, other):
        return enum_btags(self.obj) <= enum_btags(other.obj)
    def __ge__(self, other):
        return enum_btags(self.obj) >= enum_btags(other.obj)
    def __ne__(self, other):
        return enum_btags(self.obj) != enum_btags(other.obj)
    
class key_jets:
    def __init__(self, obj, *args):
        self.obj = obj
    def __lt__(self, other):
        return enum_jets(self.obj) < enum_jets(other.obj)
    def __gt__(self, other):
        return enum_jets(self.obj) > enum_jets(other.obj)
    def __eq__(self, other):
        return enum_jets(self.obj) == enum_jets(other.obj)
    def __le__(self, other):
        return enum_jets(self.obj) <= enum_jets(other.obj)
    def __ge__(self, other):
        return enum_jets(self.obj) >= enum_jets(other.obj)
    def __ne__(self, other):
        return enum_jets(self.obj) != enum_jets(other.obj)

def enum_btags(name):
    if "nB0" in name:
        return 0
    elif "nB1" in name:
        return 1
    elif "nB2" in name:
        return 2
    elif "nB3" in name:
        return 3
    elif "nB4p" in name:
        return 4
    else:
        raise ValueError("Bleh")
        
def enum_jets(name):
    if "nBJ4" in name:
        return 0
    elif "nJ5" in name:
        return 1
    elif "nJ6" in name:
        return 2
    elif "nJ7" in name:
        return 3
    elif "nB8p" in name:
        return 4
    else:
        raise ValueError("Bleh")
        
        
def make_the_plots(filename, fit, output_type, filt_name=None, xlabel=None, ylabel=None, ratiolabel=None, output_name="1.pdf"):
    with uproot.open(filename) as f:
        #filt_name="*nB2_nJ6"
        if not filt_name:
            filt_name=""
            filt_name+="*prefit" if fit == "prefit" else "*postfit"
            filt_name+="/" if "/" in filt_name else ""
        if "prefit" not in filt_name and "postfit" not in filt_name:
            raise RuntimeError("filter_name must be constructed containing prefit or postfit, automatically added for default filt_name")
        #dict of directories
        directories={k:v for k, v in f.items(cycle=False, filter_name=filt_name, filter_classname="TDirectory")}
        
        #CombineHarvester breaks on our least significant combine bin and turns our data_obs into NaN, remove it
        
        if len(directories.keys()) < 1:
            raise RuntimeError("Found no directories with filter_name", filt_name)
            
        #dict of strings
        categories = [k for k in directories.keys()]

        #dict of strings
        processes = set([kk for directory in directories.values() for kk, vv in directory.items(cycle=False) if kk not in ["TotalBkg", "TotalProcs", "TotalSig", "data_obs"]])
        #dict of dict of strings, process as key
        process_histograms = {}
        for process in processes:
            process_histograms[process] = {}

        #dict of hist
        total_bkg = {}
        total_sig = {}
        total_procs = {}
        data = {}

        #results
        categorized_histograms = {}

        for i, (category, directory) in enumerate(directories.items()):
            total_bkg[category] = directory["TotalBkg"].to_hist()
            total_sig[category] = directory["TotalSig"].to_hist()
            total_procs[category] = directory["TotalProcs"].to_hist()
            data[category] = directory["data_obs"].to_hist()
            #CombineHarvester breaks on our least significant combine bin and turns our data_obs into NaN, remove it
            if "OSDL_2017_ElEl_nB4p_nJ4" in category:
                if np.any(np.isnan(data[category].values(flow=True))):
                    zeroer = deepcopy(data[category]).reset()
                    mask = np.isnan(data[category].values(flow=True))
                    data[category].view(flow=True)[mask] = zeroer.view(flow=True)[mask]
            # if category not in process_histograms:
            #     process_histograms[category] = {}
            for process in processes:
                try:
                    process_histograms[process][category] = directory[process].to_hist()
                except:
                    print(f"Didn't find {process} for category {category}")
                    process_histograms[process][category] = deepcopy(total_procs[category]).reset()
        # categorized_histogram = make_categorized_histogram(process_histograms[process])
        axis_sorter = None
        if output_type.lower() == "njet":
            # group by number of btags and rebin 3 channels * 2 years * 5 jet categories
            # the sorting is now redundant since the rebinning works...
            #axis_sorter = {"category": {"key": key_btags, "reverse": False}}
            rebin = group_jets
            if ylabel is None:
                ylabel = "Events / Bin"
            if xlabel is None:
                xlabel = "Jet Multiplicity"
            if ratiolabel is None:
                ratiolabel = r"$\frac{Data}{Sig+Bkgd}$"
            make_category_plot(process_histograms, 
                               total_bkg, 
                               total_sig, 
                               total_procs, 
                               data, 
                               category_remapping=None,
                               output=output_name,
                               axis_sorter=axis_sorter,
                               rebin=rebin,
                               ylabel=ylabel,
                               xlabel=xlabel,
                               ratiolabel=ratiolabel
                              )
        elif output_type.lower() == "nbtag":
            # group by number of jets and rebin 3 channels * 2 years * 3 btag categories
            #axis_sorter = {"category": {"key": key_jets, "reverse": False}}
            rebin = group_btags
            if ylabel is None:
                ylabel = "Events / Bin"
            if xlabel is None:
                xlabel = "b-tagged Jet Multiplicity"
            if ratiolabel is None:
                ratiolabel = r"$\frac{Data}{Sig+Bkgd}$"
            print(output_name, xlabel)
            make_category_plot(process_histograms, 
                               total_bkg, 
                               total_sig, 
                               total_procs, 
                               data, 
                               category_remapping=None,
                               output=output_name,
                               axis_sorter=axis_sorter,
                               rebin=rebin,
                               ylabel=ylabel,
                               xlabel=xlabel,
                               ratiolabel=ratiolabel
                              )
        elif output_type.lower() == "categories":
            # group by s/sqrt(s+b) using combine-bins==categories for each actual bin
            axis_sorter = None
            if ylabel is None:
                ylabel = "Events / Bin"
            if xlabel is None:
                xlabel = r"Categorical Bin",
            if ratiolabel is None:
                ratiolabel = r"$\frac{Data}{Sig+Bkgd}$"
            make_category_plot(process_histograms, 
                               total_bkg, 
                               total_sig, 
                               total_procs, 
                               data, 
                               category_remapping=None,
                               output=output_name,
                               axis_sorter=axis_sorter,
                               rebin=rebin,
                               ylabel=ylabel,
                               xlabel=xlabel,
                               ratiolabel=ratiolabel
                              )
        elif output_type.lower() == "soversqrtsplusb":
            # Have to handle this with a different set of functions... do it all in the concatenated_histograms function
            pass
        else:
            raise NotImplementedError(output_type, "is not implemented")

def make_category_plot(process_histograms, total_bkg, total_sig, total_procs, data, category_remapping=None, output=None, signal_procs=["tttt"], axis_sorter=None, rebin=None, ylabel=None, xlabel=None, ratiolabel=None):
    process_cat_histograms = {}
    total_cat_bkg = make_categorized_histogram(total_bkg, category_remapping=category_remapping)
    total_cat_sig = make_categorized_histogram(total_sig, category_remapping=category_remapping)
    total_cat_procs = make_categorized_histogram(total_procs, category_remapping=category_remapping)
    data_cat = make_categorized_histogram(data, category_remapping=category_remapping)
    for process in process_histograms:
        process_cat_histograms[process] = make_categorized_histogram(process_histograms[process], category_remapping=category_remapping)
    background_cat_stack = make_process_histogram({proc:hist for proc, hist in process_cat_histograms.items() if proc not in signal_procs})
    
    if axis_sorter:
        #axis_sorter = {"category": lambda x: ["c", "b", "a"].index(x)}
        for axis, sort_kwords in axis_sorter.items():
            total_cat_bkg = total_cat_bkg.sort(axis, **sort_kwords)
            total_cat_sig = total_cat_sig.sort(axis, **sort_kwords)
            total_cat_procs = total_cat_procs.sort(axis, **sort_kwords)
            data_cat = data_cat.sort(axis, **sort_kwords)
            background_cat_stack = background_cat_stack.sort(axis, **sort_kwords)
            for process in process_cat_histograms:
                process_cat_histograms[process] = process_cat_histograms[process].sort(axis, **sort_kwords)
    if rebin:
        for merging_axis_name, merging_dict in rebin.items():
            total_cat_bkg = merge_within_categorical_axis(total_cat_bkg, 
                                                          merging_axis_name=merging_axis_name, 
                                                          merging_dict=merging_dict)
            total_cat_bkg = merge_within_categorical_axis(total_cat_bkg, 
                                                          merging_axis_name=merging_axis_name, 
                                                          merging_dict=merging_dict)
            total_cat_sig = merge_within_categorical_axis(total_cat_sig, 
                                                          merging_axis_name=merging_axis_name, 
                                                          merging_dict=merging_dict)
            total_cat_procs = merge_within_categorical_axis(total_cat_procs, 
                                                            merging_axis_name=merging_axis_name, 
                                                            merging_dict=merging_dict)
            data_cat = merge_within_categorical_axis(data_cat, 
                                                     merging_axis_name=merging_axis_name, 
                                                     merging_dict=merging_dict)
            background_cat_stack = merge_within_categorical_axis(background_cat_stack, 
                                                                 merging_axis_name=merging_axis_name, 
                                                                 merging_dict=merging_dict)
            for process in process_cat_histograms:
                process_cat_histograms[process] = merge_within_categorical_axis(process_cat_histograms[process], 
                                                                                merging_axis_name=merging_axis_name, 
                                                                                merging_dict=merging_dict)


    for lbl in ["Preliminary", "Supplementary", "Preliminary Supplemental", ""]:
        zzzz = make_plot(background_cat_stack, total_cat_bkg, total_cat_sig, total_cat_procs, data_cat, 
                     draw_signal="stack", output=output, label=lbl, xlabel=xlabel, ylabel=ylabel, ratiolabel=ratiolabel)
    
def make_concatenated_plot(process_histograms, total_bkg, total_sig, total_procs, data, category_remapping=None, output=None, signal_procs=["tttt"], axis_sorter=None, rebin=None, ylabel=None, xlabel=None, ratiolabel=None):
    process_con_histograms = {}
    total_con_bkg = fully_concatenated_histogram(total_bkg)
    total_con_sig = fully_concatenated_histogram(total_sig)
    total_con_procs = fully_concatenated_histogram(total_procs)
    data_con = fully_concatenated_histogram(data)
    soversqrtsplusb = total_con_sig.values() / np.sqrt(total_con_procs.values())
    argsorter = np.argsort(soversqrtsplusb)
    
    #Work from hehre
    for process in process_histograms:
        process_con_histograms[process] = fully_concatenated_histogram(process_histograms[process])
    background_con_stack = make_process_histogram({proc:hist for proc, hist in process_con_histograms.items() if proc not in signal_procs})
    
    if axis_sorter:
        #axis_sorter = {"category": lambda x: ["c", "b", "a"].index(x)}
        for axis, sort_kwords in axis_sorter.items():
            total_cat_bkg = total_cat_bkg.sort(axis, **sort_kwords)
            total_cat_sig = total_cat_sig.sort(axis, **sort_kwords)
            total_cat_procs = total_cat_procs.sort(axis, **sort_kwords)
            data_cat = data_cat.sort(axis, **sort_kwords)
            background_cat_stack = background_cat_stack.sort(axis, **sort_kwords)
            for process in process_cat_histograms:
                process_cat_histograms[process] = process_cat_histograms[process].sort(axis, **sort_kwords)
    if rebin:
        for merging_axis_name, merging_dict in rebin.items():
            total_cat_bkg = merge_within_categorical_axis(total_cat_bkg, 
                                                          merging_axis_name=merging_axis_name, 
                                                          merging_dict=merging_dict)
            total_cat_bkg = merge_within_categorical_axis(total_cat_bkg, 
                                                          merging_axis_name=merging_axis_name, 
                                                          merging_dict=merging_dict)
            total_cat_sig = merge_within_categorical_axis(total_cat_sig, 
                                                          merging_axis_name=merging_axis_name, 
                                                          merging_dict=merging_dict)
            total_cat_procs = merge_within_categorical_axis(total_cat_procs, 
                                                            merging_axis_name=merging_axis_name, 
                                                            merging_dict=merging_dict)
            data_cat = merge_within_categorical_axis(data_cat, 
                                                     merging_axis_name=merging_axis_name, 
                                                     merging_dict=merging_dict)
            background_cat_stack = merge_within_categorical_axis(background_cat_stack, 
                                                                 merging_axis_name=merging_axis_name, 
                                                                 merging_dict=merging_dict)
            for process in process_cat_histograms:
                process_cat_histograms[process] = merge_within_categorical_axis(process_cat_histograms[process], 
                                                                                merging_axis_name=merging_axis_name, 
                                                                                merging_dict=merging_dict)

    for lbl in ["Preliminary", "Supplementary", "Preliminary Supplemental", ""]:
        
        zzzz = make_plot(background_cat_stack, total_cat_bkg, total_cat_sig, total_cat_procs, data_cat, 
                     draw_signal="stack", output=output, label=lbl, xlabel=xlabel, ylabel=ylabel, ratiolabel=ratiolabel)
        
def make_plot(background_stack, total_bkg, total_sig, total_procs, data, draw_signal="stack", 
              output=None, label=None, xlabel="", ylabel="Events / Bin", ratiolabel=r"$\frac{Data}{Sig+Bkgd}$"):
    do_log_y = True
    do_ratio = True
    do_chi_square = False
    n_xpads = 1
    n_ypads = 2
    fig, subpads = plt.subplots(
        n_ypads,
        n_xpads,
        figsize=(10, 10),
        gridspec_kw=dict(
            height_ratios=[3, 1],
            width_ratios=[1],
            hspace=0.06,
            wspace=0.15,
        ),
        sharex=True
    )
    # Hack for n_xpads = 1 and do_ratio = True
    subpads = (
        [[subpads[0]], [subpads[1]]] if (n_xpads == 1 and do_ratio) else subpads
    )
    color_dict = {
        "ttH": "#163d4e",
        "tttt": "#a1794a", ### NOT DIFFERENTIABLE WITH DATA! "#1a142f", ### OLD "#1e6542",
        "ttVJets": "#54792f",
        "ttultrarare": "#1a142f",
        "EWK": "#d07e93",
        "ttnobb": "#cf9ddb",
        "QCD": "#c1caf3",
        "ttbb": "#d3eeef",
    }
    process_lbl_dict = {
        "ttH": r"$t\bar{t}+H$",
        "tttt": r"$t\bar{t}t\bar{t}$",
        "ttVJets": r"$t\bar{t}+V$",
        "ttultrarare": r"$t\bar{t}+rare$",
        "EWK": "EWK",
        "ttnobb": r"$t\bar{t}+!b\bar{b}$",
        "QCD": "QCD",
        "ttbb": r"$t\bar{t}+b\bar{b}$",
        "singletop": r"$t@ + \bar{t})W$",
    }
    from cycler import cycler

    colors = []
    axes = {axis.name: axis for axis in background_stack.axes}
    bkg_order = []
    bkg_sums = background_stack.project("process")
    
    #sort processes...
    for proc in axes["process"]:
        bkg_order.append((proc, bkg_sums[proc].value))
    bkg_order = sorted(bkg_order, key=lambda p: p[1], reverse=True)
    bkg_order=[proc for proc, integral in bkg_order]
      
    unblindlist = [True]*n_xpads
    for it in range(1): #, idct in enumerate(input_tuple):
        # Set the colors for the background stack, with reverse order because that's how the cycler iterates through!
#         temp_c = []
#         for process in bkg_order:
#             temp_c.append(color_dict[process])
#         temp_c = temp_c[::-1]
#         colors.append(temp_c)
#         subpads[0][it].set_prop_cycle(cycler(color=colors[it]))

        # Extract the data slice, total background, signal
        #data = idct["data"][:, :, hist.loc("data_obs"), :].project(projection_axis)
        # bkg_stack = idct["bkg"].project("process", projection_axis)
        # bkg_tot = bkg_stack.project(projection_axis)
        ## bkg_tot = total_bkg
        #background_stack, total_bkg, total_sig, total_procs, data

        if draw_signal:
            sig_tot = total_sig
            simulation = total_procs
            if draw_signal.lower() == "stack":
                sig_tot += total_bkg
        else:
            simulation = total_bkg

#         # draw background components
#         components = background_stack.plot1d(
#             ax=subpads[0][it],
#             stack=True,
#             overlay="process",
#             histtype="fill",
#             edgecolor=(0, 0, 0, 0.3),
#         )
        bkg_base = deepcopy(total_bkg).reset()
        ylog_min = 0.01
        for i, background in enumerate(bkg_order[::-1]):
            subpads[0][it].stairs(
                edges=bkg_base.axes[0].edges,
                baseline=bkg_base.values(),
                values=background_stack[{"process": background}].values()+bkg_base.values(),
                # hatch="....",
                label=process_lbl_dict[background],
                facecolor=color_dict[background],
                fill=True,
                # linewidth=1,
                color=color_dict[background],
                edgecolor=(0, 0, 0, 0.3),
            )
            bkg_base = bkg_base + background_stack[{"process": background}]
            if i == 0:
                ylog_min = np.min(bkg_base.values()/2)

        # create a total statistical uncertainty hatch
        subpads[0][it].stairs(
            edges=total_bkg.axes[0].edges,
            baseline=simulation.values() - np.sqrt(simulation.variances()),
            values=simulation.values() + np.sqrt(simulation.variances()),
            hatch="/////",
            label="Uncertainty" if draw_signal else "Uncertainty",
            facecolor="none",
            linewidth=1,
            color="gray",
        )

        if unblindlist[it]:
            data.plot1d(
                ax=subpads[0][it], histtype="errorbar", color="k", label="data"
            )
            if do_chi_square:
                left = data
                if draw_signal:
                    right = simulation # total_procs
                else:
                    right = simulation # total_bkg
                chi2, dof = hist_chi_square(left, right, mask_left_zeros=False)
                chi2_sub = "_{s+b}" if draw_signal else "_{bkg}"
                print_chi2 = (
                    r"$\chi^2 = \frac{"
                    + "{:3.2f}".format(chi2)
                    + "}{"
                    + "{:d}".format(dof)
                    + "}$"
                )
                plt.text(
                    0.3,
                    0.85,
                    print_chi2,
                    horizontalalignment="center",
                    verticalalignment="center",
                    transform=subpads[0][it].transAxes,
                    fontsize=30,
                    color="black",
                )
        if draw_signal:
            sig_name = "tttt"
            # sig_tot.plot1d(ax=subplots[0][it], histtype="step", color="r", yerr=None)
            subpads[0][it].stairs(
                edges=sig_tot.axes[0].edges,
                #baseline=total_bkg.values() #total_bkg is somehow broken!?
                baseline=bkg_base.values()
                if draw_signal == "stack"
                else sig_tot.values() - sig_tot.values(),
                values=sig_tot.values() + bkg_base.values()
                if draw_signal == "stack"
                else sig_tot.values(),
                # hatch="....",
                label=process_lbl_dict[sig_name],
                facecolor=color_dict[sig_name],
                fill=True,
                # linewidth=1,
                color=color_dict[sig_name],
            )


        # now draw a ratio plot
        if do_ratio:
            from hist.intervals import ratio_uncertainty

            if unblindlist[it]:
                if np.sum(np.abs(data.values())) < 1e-15:
                    the_ratio_unc = None  # np.stack((interval_min, interval_max))
                else:
                    the_ratio_unc = ratio_uncertainty(
                        data.values(), simulation.values(), "poisson"
                    )
                subpads[1][it].errorbar(
                    x=simulation.axes[0].centers,
                    # y=data.view() / Bkg.view(),
                    y=data.values() / simulation.values(),
                    yerr=the_ratio_unc,
                    color="k",
                    linestyle="none",
                    marker="o",
                    elinewidth=1,
                )
            subpads[1][it].stairs(
                edges=total_bkg.axes[0].edges,
                baseline=(simulation.values() - np.sqrt(simulation.variances()))
                / simulation.values(),
                values=(simulation.values() + np.sqrt(simulation.variances()))
                / simulation.values(),
                #hatch="....",
                hatch="/////",
                label="Uncertainty" if draw_signal else "Uncertainty",
                facecolor="none",
                linewidth=1,
                color="gray",
                #color="blue",
            )

#             subplots[1][it].set_ylim(0.1, 2.1)
#             if it == 0:
#                 subplots[1][it].axhline(y=1.0, linestyle="dashed", color="gray")
#                 ratio_denom = "Sig+Bkg" if draw_signal else "Background"
#                 subplots[1][it].set_ylabel(
#                     "$\\frac{Data}{" + ratio_denom + "}$", loc="center"
#                 )
#                 if do_legend:
#                     subplots[1][it].legend()

#             # Adjust labels if mountain_range
#             if True:  # do all labels instead
#                 subplots[1][it].set_xlabel(
#                     "$H_{T}$ [GeV]" if projection_axis == "HT" else projection_axis
#                 )
#             else:
#                 if it == len(input_tuple) - 1:
#                     subplots[1][it].set_xlabel(
#                         "$H_{T}$ [GeV]" if projection_axis == "HT" else projection_axis
#                     )
#                 elif do_mountain_range:
#                     subplots[1][it].set_xlabel(projection_axis)

#             if do_mountain_range and it > 0:
#                 subplots[1][it].yaxis.set_major_locator(ticker.NullLocator())
#                 subplots[1][it].set_ylabel("")
#             if it == 0:
#                 subplots[1][it].axhline(y=1.0, linestyle="dashed", color="gray")
#                 ratio_denom = "Sig+Bkg" if draw_signal else "Background"
#                 subplots[1][it].set_ylabel(
#                     "$\\frac{Data}{" + ratio_denom + "}$", loc="center"
#                 )
#                 if do_legend:
#                     subplots[1][it].legend()


        # Take care of niceties like axes, limits, legend, CMS text, etc.
        subpads[0][it].set_ylabel(ylabel)
        if do_log_y:
            subpads[0][it].set_yscale("log")
            subpads[0][it].set_ylim(ylog_min, 10 * max(total_bkg.values()))
            subpads[0][it].set_ylim(0.5) #FIXME HACK FOR PRL PLOT
        else:
            subpads[0][it].set_ylim(ylog_min, 1.2 * max(total_bkg.values()))
        if do_ratio:
            subpads[1][it].set_ylim(0.5, 1.5)
            subpads[1][it].set_ylabel(ratiolabel, loc="center")
            #subpads[1][it].yaxis.set_label_coords(-.07, 0.85)
            subpads[1][it].set_xlabel(xlabel)
            subpads[0][it].set_xlabel("")
            subpads[1][it].axhline(y=1.0, color='gray', linestyle='--')
            #subpads[1][it].legend()
        else:
            subpads[0][it].set_xlabel(xlabel)
                     
        mplhep.cms.label(
                         #label=0,
                         ax=subpads[0][it],
                         label=label,
                         data=True,
                         lumi=101,
                        )
        if it == 0:
            subpads[0][it].legend(ncol=3)
            mplhep.plot.yscale_legend(ax=subpads[0][it])
#             if do_legend:
#                 subplots[0][it].legend()
#         elif individual_legends:
#             if do_legend:
#                 subplots[0][it].legend()
#         elif it > 0 and do_mountain_range:
#             subplots[0][it].yaxis.set_major_locator(ticker.NullLocator())
#             subplots[1][it].set_ylabel("")

    if output is not None:
        savename = label.replace(" ", "_")+"_"+output if label != "" else output
        fig.savefig(savename)
    return fig, subpads
    
        # gridspec_kw=dict(
        #     height_ratios=height_ratios,
        #     width_ratios=width_ratios,
        #     hspace=hspace,
        #     wspace=wspace,
        # ),
        # figsize=figsize,
        # sharex=sharex,
        # sharey=sharey,
        
def hist_chi_square(left, right, mask_left_zeros=False):
    assert isinstance(left, hist.Hist) and isinstance(right, hist.Hist)
    num = np.power((left.values() - right.values()), 2)
    den = np.sqrt(left.variances() + right.variances())

    if mask_left_zeros == True:
        non_zero = np.nonzero(left)
        dof = np.sum(non_zero)
        return np.sum((num / den)[np.nonzero(left)]), dof
    else:
        return np.sum((num / den)), len(num)
    
def make_process_histogram(dict_of_process_histograms, process_remapping=None):
    if process_remapping is None:
        process_remapping = {}
    procs = [process_remapping.get(key, key) for key in dict_of_process_histograms.keys()]
    hist_args = [hist.axis.StrCategory(procs, name="process", growth=True)]
    hist_args.append(list(dict_of_process_histograms.values())[0].axes[0])
    hist_args.append(hist.storage.Weight())
    histo = hist.Hist(*hist_args)
    for proc, histogram in dict_of_process_histograms.items():
        for category in histogram.axes[0]:
            histo[proc, category] = histogram[category]
    return histo
        
def make_categorized_histogram(dict_of_category_histograms, category_remapping=None):
    if category_remapping is None:
        category_remapping = {}
    cats = [category_remapping.get(key, key) for key in dict_of_category_histograms.keys()]
    #make categorical histogram with overflow bins so we can write it to a root file
    histo = hist.Hist(
        hist.axis.StrCategory(cats, name="category", growth=True),
        hist.storage.Weight()
    )
    for category, histogram in dict_of_category_histograms.items():
        histo[category] = histogram.sum()
    return histo
    
    # with uproot.recreate("test.root") as f:
    #     f["test"] = histo
    # with uproot.open("test.root") as f:
    #     breakpoint()
    #     h2 = f["test"]
    #     print(np.isclose(h2.values(flow=True), histo.values(flow=True)))
        
    # p_hist = hist.Hist(
    #     hist.axis.StrCategory([], name="category", growth=True),
    #     hist.axis.StrCategory([], name="process", growth=True),
    #     hist.storage.Weight()
    # )
    # for category in total_procs.keys():
    #     pass
    #     # hist.fill(category=category, process=process)

def fully_concatenated_histogram(dict_of_category_histograms, include_underflow=False, include_overflow=True):
    histo_values = {}
    histo_variances = {}
    start = None if include_underflow else 1
    end = None if include_overflow else -1
    total_bins = 0
    #cannot do the same for overflow? Inconvenient...
    for category, histogram in dict_of_category_histograms.items():
        starts.append(total_bins)
        histo_values[category]    = histogram.values(flow=True)[start:end]
        histo_variances[category] = histogram.variances(flow=True)[start:end]
        total_bins += len(histo_values[category])
        stops.append(total_bins)
    histo = hist.Hist(
        hist.axis.Regular(total_bins, 0, total_bins, name="bins", flow=True),
        hist.storage.Weight()
    )
    all_values = np.concatenate(histo_values.values(), axis=0)
    all_variances = np.concatenate(histo_variances.values(), axis=0)
    histo.values()[:] = all_values
    histo.variances()[:] = all_variances
    print(histo)
    return histo
    

# def make_njet_nbtag_histograms(process_histograms, total_bkg, total_sig, total_procs, data):
    
#     for category in 

group_btags =  {"category": {"2": [f'OSDL_{year}_{channel}_nB2_nJ{j}_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for j in ['4', '5', '6', '7', '8p']\
                                   for prepost in ['prefit', 'postfit']],
                             "3": [f'OSDL_{year}_{channel}_nB3_nJ{j}_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for j in ['4', '5', '6', '7', '8p']\
                                   for prepost in ['prefit', 'postfit']],
                             "4+": [f'OSDL_{year}_{channel}_nB4p_nJ{j}_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for j in ['4', '5', '6', '7', '8p']\
                                   for prepost in ['prefit', 'postfit']],
                            }
               }

group_jets =  {"category": {"4": [f'OSDL_{year}_{channel}_nB{b}_nJ4_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for b in ['2', '3', '4p']\
                                   for prepost in ['prefit', 'postfit']],
                             "5": [f'OSDL_{year}_{channel}_nB{b}_nJ5_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for b in ['2', '3', '4p']\
                                   for prepost in ['prefit', 'postfit']],
                             "6": [f'OSDL_{year}_{channel}_nB{b}_nJ6_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for b in ['2', '3', '4p']\
                                   for prepost in ['prefit', 'postfit']],
                             "7": [f'OSDL_{year}_{channel}_nB{b}_nJ7_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for b in ['2', '3', '4p']\
                                   for prepost in ['prefit', 'postfit']],
                             "8+": [f'OSDL_{year}_{channel}_nB{b}_nJ8p_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for b in ['2', '3', '4p']\
                                   for prepost in ['prefit', 'postfit']],
                            }
               }
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", action="store", type=str,
                        help="file containing pre/postfit histograms")
    parser.add_argument("--fit", type=str, action="store", choices=["splusb", "bonly", "prefit"], default="splusb")
    parser.add_argument("--output_types", type=str, nargs="*", action="store", 
                        choices=["nbtag", "njet", "categories", "soversqrtsplusb"],
                        default=["njet"],
                        help="types of plots and histograms to produce")
    parser.add_argument("--signal_names", type=str, nargs="*", action="store", 
                        default=["tttt"],
                        help="name(s) of signal samples from combine PostFitShapesFromWorkspace")
    parser.add_argument("--data_name", type=str, action="store", 
                        default=["data_obs"],
                        help="name of observed data from combine PostFitShapesFromWorkspace")
    parser.add_argument("--filter_name", type=str, action="store", 
                        default=None,
                        help="filter_name overrride for uproot")
    parser.add_argument("--output_xlabels", type=str, nargs="*", action="store",
                        default=["Jet Multiplicity"],
                        help="X-axis labels for each of the output types")
    parser.add_argument("--output_ylabels", type=str, nargs="*", action="store",
                        default=["Events / Bin"],
                        help="Y-axis labels for each of the output types")
    parser.add_argument("--output_ratiolabels", type=str, nargs="*", action="store",
                        default=[r"$\frac{Data}{Sig+Bkgd}$"],
                        help="Ratio-plot labels for each of the output types")
    parser.add_argument("--output_names", type=str, nargs="*", action="store",
                        default=["plot.pdf"],
                        help="Name(s) of the plot file to produce")
    
    args = parser.parse_args()
    
    n = len(args.output_types)
    if n > 1:
        if len(args.output_xlabels) == 1:
            args.output_xlabels *= len(args.output_types)
        if len(args.output_ylabels) == 1:
            args.output_ylabels *= len(args.output_types)
        if len(args.output_ratiolabels) == 1:
            args.output_ratiolabels *= len(args.output_types)
        if len(args.output_names) == 1:
            args.output_names = [ot + "_" + args.output_names[0] for ot in args.output_types]
        
    if len(args.output_xlabels) != n or len(args.output_ylabels) != n or len(args.output_ratiolabels) != n:
        raise ValueError("labels must all be length 1 or same length as output_types")
    if len(args.output_names) != n:
        raise ValueError("output_names must be 1 or same length as output_types")

    for otype, xlabel, ylabel, ratiolabel, output in zip(args.output_types,
                                                         args.output_xlabels,
                                                         args.output_ylabels,
                                                         args.output_ratiolabels,
                                                         args.output_names
                                                        ):
        make_the_plots(args.file, args.fit, otype, filt_name=args.filter_name, 
                       xlabel=xlabel, ylabel=ylabel, ratiolabel=ratiolabel, output_name=output)
