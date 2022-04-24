#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function, division
import os
import time
import pwd
import datetime
import ROOT
import collections
import pprint
import math
import numpy as np
np.set_printoptions(precision=3, threshold=None, edgeitems=None, linewidth=120, suppress=None, nanstr=None, infstr=None, formatter=None, sign=None, floatmode=None, legacy=None)
import array
import json
import copy
import argparse
import uuid
from tqdm import tqdm
from FourTopNAOD.RDF.tools.toolbox import get_number_of_labels, load_yaml_cards, write_yaml_cards, configure_template_systematics, configure_template_systematics_dict
from FourTopNAOD.RDF.combine.templating import write_combine_cards
# from ruamel.yaml import YAML
from IPython.display import Image, display, SVG

#Debugging and profiling
import pdb
import cProfile
import pstats
from functools import wraps
def profile(output_file=None, sort_by='cumulative', lines_to_print=None, strip_dirs=False):
    """A time profiler decorator.

    Inspired by and modified the profile decorator of Giampaolo Rodola:
    http://code.activestate.com/recipes/577817-profile-decorator/

    Args:
        output_file: str or None. Default is None
            Path of the output file. If only name of the file is given, it's
            saved in the current directory.
            If it's None, the name of the decorated function is used.
        sort_by: str or SortKey enum or tuple/list of str/SortKey enum
            Sorting criteria for the Stats object.
            For a list of valid string and SortKey refer to:
            https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats
        lines_to_print: int or None
            Number of lines to print. Default (None) is for all the lines.
            This is useful in reducing the size of the printout, especially
            that sorting by 'cumulative', the time consuming operations
            are printed toward the top of the file.
        strip_dirs: bool
            Whether to remove the leading path info from file names.
            This is also useful in reducing the size of the printout

    Returns:
        Profile of the decorated function
    """

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _output_file = output_file or func.__name__ + '.prof'
            pr = cProfile.Profile()
            pr.enable()
            retval = func(*args, **kwargs)
            pr.disable()
            pr.dump_stats(_output_file)

            with open(_output_file, 'w') as f:
                ps = pstats.Stats(pr, stream=f)
                if strip_dirs:
                    ps.strip_dirs()
                if isinstance(sort_by, (tuple, list)):
                    ps.sort_stats(*sort_by)
                else:
                    ps.sort_stats(sort_by)
                ps.print_stats(lines_to_print)
            return retval

        return wrapper

    return inner

np.seterr(all='raise')

#import graphviz
ROOT.PyConfig.IgnoreCommandLineOptions = True
models = {}
models["v0.8"] = {
    "Plot_$CAT___$VAR": {
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle", 
        "Xaxis": None, 
        "Yaxis": None, 
        "Rebin": 10, 
        "Files": "2017___Combined.root", 
        "Projection": None, 
        "Unblind": False, 
    },
    "Canvas_$CATEGORIZATION_$VAR": {
        "Type": "CanvasConfig", 
        "Title": "$VAR ($CATEGORIZATION)", 
        "Margins": [0.1, 0.1, 0.1, 0.1], 
        "Coordinates": [], 
        "Plots": [],
        "Labels": [], 
        "Legend": "DefaultLegend", 
        "Rebin": None, 
        "XPixels": 1200, 
        "YPixels": 1000, 
        "XAxisTitle": "$VAR", 
        "YAxisTitle": "Events/bin", 
        "Projection": None, 
        "DoRatio": True, 
        "doLogY": False,
        "DoMountainrange": True, 
    }, 
}
models["v1.0"] = {
    "Plot_$CAT___$VAR": {
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle", 
        "Xaxis": None, 
        "Yaxis": None, 
        "Rebin": 5, 
        "Files": "$ERA___Combined.root", 
        "Projection": None, 
        "Unblind": False, 
    },
    "Canvas_$CATEGORIZATION_$VAR": {
        "Type": "CanvasConfig", 
        "Title": "$PRETTYVAR ($PRETTYCATEGORIZATION)", 
        "Margins": [0.1, 0.1, 0.1, 0.1], 
        "Coordinates": [], 
        "Plots": [],
        "Labels": [], 
        "Legend": "DefaultLegend", 
        "Rebin": None, 
        "XPixels": 1200, 
        "YPixels": 1000, 
        "XAxisTitle": "$PRETTYVAR", 
        "YAxisTitle": "Events / bin", 
        "Projection": None, 
        "DoRatio": True, 
        "doLogY": False,
        "DoMountainrange": True, 
    }, 
}
modelPlotJSON_CAT = {
    "Plot_ElMu___$CAT___$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": 10,
        "Files": "2017___Combined.root",
        "Unblind": False,
    },
    "Canvas_$CATEGORIZATION_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": [],
        "Labels": [],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": False,
        "DoMountainrange": True,
    },
}
modelPlotJSON_SPLITSTITCH = {
    "Plot_diagnostic___$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": 10,
        "Files": "2017___Combined.root",
        "Unblind": False,
    },
    "Canvas_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": [],
        "Labels": [],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "DoRatio": True,
        "doLogY": False,
        "DoMountainrange": True,
    },
}
# print("no LogY until file handling is fixed!\n\n\n\n\n\n\n")
zzzz = {
"Canvas_LogY_$CATEGORIZATION_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": [],
        "Labels": [],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": True,
        "DoMountainrange": True,
    },
}
modelPlotJSON_nJetProjection = {
    "Plot_Inclusive_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 5, -1],
        "Files": "Inclusive_$VAR.root",
        "Unblind": False,
    },
    "Plot_nJet4_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nJet4_$VAR.root",
        "Unblind": False,
    },
    "Plot_nJet5_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 2, -1],
        "Files": "nJet5_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nJet6_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 3, -1],
        "Files": "blind_nJet6_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nJet7_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 4, -1],
        "Files": "blind_nJet7_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nJet8+_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 6, -1],
        "Files": "blind_nJet8+_$VAR.root",
        "Unblind": False,
    },
    "Canvas_Inclusive_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_Inclusive_$VAR"],
        "Labels": ["$CHANNEL\n Inclusive"],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": False,
        "DoMountainrange": True,
    },
    "Canvas_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_nJet4_$VAR", "Plot_nJet5_$VAR", "Plot_blind_nJet6_$VAR", "Plot_blind_nJet7_$VAR", "Plot_blind_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nJet=4", "$CHANNEL\n nJet=5", "$CHANNEL\n nJet=6", "$CHANNEL\n nJet=7", "$CHANNEL\n nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": False,
        "DoMountainrange": True,
    },
    "Canvas_LogY_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_nJet4_$VAR", "Plot_nJet5_$VAR", "Plot_blind_nJet6_$VAR", "Plot_blind_nJet7_$VAR", "Plot_blind_nJet8+_$VAR"],
        "Labels": ["$CHANNEL nJet == 4", "$CHANNEL nJet == 5", "$CHANNEL nJet == 6", "$CHANNEL nJet == 7", "$CHANNEL nJet >= 8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": True,
        "DoMountainrange": True,
    },
}
modelPlotJSON_nMediumDeepCSV_nJet = {
    "Plot_nMediumDeepCSV0_nJet4_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV0_nJet4_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV0_nJet5_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV0_nJet5_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV0_nJet6_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV0_nJet6_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV0_nJet7_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV0_nJet7_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV0_nJet8+_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV0_nJet8+_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV1_nJet4_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV1_nJet4_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV1_nJet5_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV1_nJet5_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV1_nJet6_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV1_nJet6_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV1_nJet7_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV1_nJet7_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV1_nJet8+_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV1_nJet8+_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV2_nJet4_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV2_nJet4_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV2_nJet5_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV2_nJet5_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV2_nJet6_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "nMediumDeepCSV2_nJet6_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV2_nJet7_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV2_nJet7_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV2_nJet8+_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV2_nJet8+_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV3_nJet4_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV3_nJet4_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV3_nJet5_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV3_nJet5_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV3_nJet6_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV3_nJet6_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV3_nJet7_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV3_nJet7_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV3_nJet8+_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV3_nJet8+_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV4+_nJet4_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV4+_nJet4_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV4+_nJet5_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV4+_nJet5_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV4+_nJet6_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV4+_nJet6_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV4+_nJet7_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV4+_nJet7_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV4+_nJet8+_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Projection": ["X", 1, -1],
        "Files": "blind_nMediumDeepCSV4+_nJet8+_$VAR.root",
        "Unblind": False,
    },
    "Canvas_nMediumDeepCSV0_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_nMediumDeepCSV0_nJet4_$VAR", "Plot_nMediumDeepCSV0_nJet5_$VAR", "Plot_nMediumDeepCSV0_nJet6_$VAR", "Plot_nMediumDeepCSV0_nJet7_$VAR", "Plot_nMediumDeepCSV0_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nBTag=0 nJet=4", "$CHANNEL\n nBTag=0 nJet=5", "$CHANNEL\n nBTag=0 nJet=6", "$CHANNEL\n nBTag=0 nJet=7", "$CHANNEL\n nBTag=0 nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": False,
        "DoMountainrange": True,
    },
    "Canvas_LogY_nMediumDeepCSV0_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_nMediumDeepCSV0_nJet4_$VAR", "Plot_nMediumDeepCSV0_nJet5_$VAR", "Plot_nMediumDeepCSV0_nJet6_$VAR", "Plot_nMediumDeepCSV0_nJet7_$VAR", "Plot_nMediumDeepCSV0_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nBTag=0 nJet=4", "$CHANNEL\n nBTag=0 nJet=5", "$CHANNEL\n nBTag=0 nJet=6", "$CHANNEL\n nBTag=0 nJet=7", "$CHANNEL\n nBTag=0 nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": True,
        "DoMountainrange": True,
    },
    "Canvas_nMediumDeepCSV1_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_nMediumDeepCSV1_nJet4_$VAR", "Plot_nMediumDeepCSV1_nJet5_$VAR", "Plot_nMediumDeepCSV1_nJet6_$VAR", "Plot_nMediumDeepCSV1_nJet7_$VAR", "Plot_nMediumDeepCSV1_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nBTag=1 nJet=4", "$CHANNEL\n nBTag=1 nJet=5", "$CHANNEL\n nBTag=1 nJet=6", "$CHANNEL\n nBTag=1 nJet=7", "$CHANNEL\n nBTag=1 nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": False,
        "DoMountainrange": True,
    },
    "Canvas_LogY_nMediumDeepCSV1_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_nMediumDeepCSV1_nJet4_$VAR", "Plot_nMediumDeepCSV1_nJet5_$VAR", "Plot_nMediumDeepCSV1_nJet6_$VAR", "Plot_nMediumDeepCSV1_nJet7_$VAR", "Plot_nMediumDeepCSV1_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nBTag=1 nJet=4", "$CHANNEL\n nBTag=1 nJet=5", "$CHANNEL\n nBTag=1 nJet=6", "$CHANNEL\n nBTag=1 nJet=7", "$CHANNEL\n nBTag=1 nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": True,
        "DoMountainrange": True,
    },
    "Canvas_nMediumDeepCSV2_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_nMediumDeepCSV2_nJet4_$VAR", "Plot_nMediumDeepCSV2_nJet5_$VAR", "Plot_nMediumDeepCSV2_nJet6_$VAR", "Plot_blind_nMediumDeepCSV2_nJet7_$VAR", "Plot_blind_nMediumDeepCSV2_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nBTag=2 nJet=4", "$CHANNEL\n nBTag=2 nJet=5", "$CHANNEL\n nBTag=2 nJet=6", "$CHANNEL\n nBTag=2 nJet=7", "$CHANNEL\n nBTag=2 nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": False,
        "DoMountainrange": True,
    },
    "Canvas_LogY_nMediumDeepCSV2_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_nMediumDeepCSV2_nJet4_$VAR", "Plot_nMediumDeepCSV2_nJet5_$VAR", "Plot_nMediumDeepCSV2_nJet6_$VAR", "Plot_blind_nMediumDeepCSV2_nJet7_$VAR", "Plot_blind_nMediumDeepCSV2_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nBTag=2 nJet=4", "$CHANNEL\n nBTag=2 nJet=5", "$CHANNEL\n nBTag=2 nJet=6", "$CHANNEL\n nBTag=2 nJet=7", "$CHANNEL\n nBTag=2 nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": True,
        "DoMountainrange": True,
    },
    "Canvas_nMediumDeepCSV3_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_blind_nMediumDeepCSV3_nJet4_$VAR", "Plot_blind_nMediumDeepCSV3_nJet5_$VAR", "Plot_blind_nMediumDeepCSV3_nJet6_$VAR", "Plot_blind_nMediumDeepCSV3_nJet7_$VAR", "Plot_blind_nMediumDeepCSV3_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nBTag=3 nJet=4", "$CHANNEL\n nBTag=3 nJet=5", "$CHANNEL\n nBTag=3 nJet=6", "$CHANNEL\n nBTag=3 nJet=7", "$CHANNEL\n nBTag=3 nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": False,
        "DoMountainrange": True,
    },
    "Canvas_LogY_nMediumDeepCSV3_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_blind_nMediumDeepCSV3_nJet4_$VAR", "Plot_blind_nMediumDeepCSV3_nJet5_$VAR", "Plot_blind_nMediumDeepCSV3_nJet6_$VAR", "Plot_blind_nMediumDeepCSV3_nJet7_$VAR", "Plot_blind_nMediumDeepCSV3_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nBTag=3 nJet=4", "$CHANNEL\n nBTag=3 nJet=5", "$CHANNEL\n nBTag=3 nJet=6", "$CHANNEL\n nBTag=3 nJet=7", "$CHANNEL\n nBTag=3 nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": True,
        "DoMountainrange": True,
    },
    "Canvas_nMediumDeepCSV4+_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_blind_nMediumDeepCSV4+_nJet4_$VAR", "Plot_blind_nMediumDeepCSV4+_nJet5_$VAR", "Plot_blind_nMediumDeepCSV4+_nJet6_$VAR", "Plot_blind_nMediumDeepCSV4+_nJet7_$VAR", "Plot_blind_nMediumDeepCSV3_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nBTag>=4 nJet=4", "$CHANNEL\n nBTag>=4 nJet=5", "$CHANNEL\n nBTag>=4 nJet=6", "$CHANNEL\n nBTag>=4 nJet=7", "$CHANNEL\n nBTag>=4 nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": False,
        "DoMountainrange": True,
    },
    "Canvas_LogY_nMediumDeepCSV4+_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_blind_nMediumDeepCSV4+_nJet4_$VAR", "Plot_blind_nMediumDeepCSV4+_nJet5_$VAR", "Plot_blind_nMediumDeepCSV4+_nJet6_$VAR", "Plot_blind_nMediumDeepCSV4+_nJet7_$VAR", "Plot_blind_nMediumDeepCSV3_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nBTag>=4 nJet=4", "$CHANNEL\n nBTag>=4 nJet=5", "$CHANNEL\n nBTag>=4 nJet=6", "$CHANNEL\n nBTag>=4 nJet=7", "$CHANNEL\n nBTag>=4 nJet>=8" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": True,
        "DoMountainrange": True,
    },
}
modelPlotJSON_nMediumDeepCSV2_nJet = {
    "Plot_nMediumDeepCSV2_nJet4_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Files": "nMediumDeepCSV2_nJet4_$VAR.root",
        "Unblind": False,
    },
    "Plot_nMediumDeepCSV2_nJet5_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Files": "nMediumDeepCSV2_nJet5_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV2_nJet6_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Files": "nMediumDeepCSV2_nJet6_$VAR.root",
        "Unblind": True,
    },
    "Plot_blind_nMediumDeepCSV2_nJet7_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Files": "blind_nMediumDeepCSV2_nJet7_$VAR.root",
        "Unblind": False,
    },
    "Plot_blind_nMediumDeepCSV2_nJet8+_$VAR":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Files": "blind_nMediumDeepCSV2_nJet8+_$VAR.root",
        "Unblind": False,
    },
    "Canvas_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_nMediumDeepCSV2_nJet4_$VAR", "Plot_nMediumDeepCSV2_nJet5_$VAR", "Plot_blind_nMediumDeepCSV2_nJet6_$VAR", "Plot_blind_nMediumDeepCSV2_nJet7_$VAR", "Plot_blind_nMediumDeepCSV2_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nJet=4 nBTag=2", "$CHANNEL\n nJet=5 nBTag=2", "$CHANNEL\n nJet=6 nBTag=2", "$CHANNEL\n nJet=7 nBTag=2", "$CHANNEL\n nJet>=8 nBTag=2" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": False,
        "DoMountainrange": True,
    },
    "Canvas_LogY_nJet_$VAR":{
        "Type": "CanvasConfig",
        "Title": "$VAR",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Coordinates": [],
        "Plots": ["Plot_nMediumDeepCSV2_nJet4_$VAR", "Plot_nMediumDeepCSV2_nJet5_$VAR", "Plot_blind_nMediumDeepCSV2_nJet6_$VAR", "Plot_blind_nMediumDeepCSV2_nJet7_$VAR", "Plot_blind_nMediumDeepCSV2_nJet8+_$VAR"],
        "Labels": ["$CHANNEL\n nJet=4 nBTag=2", "$CHANNEL\n nJet=5 nBTag=2", "$CHANNEL\n nJet=6 nBTag=2", "$CHANNEL\n nJet=7 nBTag=2", "$CHANNEL\n nJet>=8 nBTag=2" ],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "XAxisTitle": "$VAR",
        "YAxisTitle": "Events/bin",
        "DoRatio": True,
        "doLogY": True,
        "DoMountainrange": True,
    },
}
#modelPlotJSON_nJet_noLogY = {}
#for k, v in modelPlotJSON_nJet.items():
#    if "_LogY_" in k: continue
#    modelPlotJSON_nJet_noLogY[k] = v
def generateJSON(model, variables, categories_dict={"nJet":["nJet4", "nJet5", "blind_nJet6", "blind_nJet7", "blind_nJet8"]},
                 era="RunII",channel="No Channel", name_format="Plot_{chan}___{cat}___{var}", rebin=None, projection=None, force=False):
    if channel == "ElMu":
        # nice_channel = "#it{e}#mu"
        nice_channel = "e#mu"
    elif channel == "MuMu":
        # nice_channel = "#mu#mu"
        nice_channel = "#mu#mu"
    elif channel == "ElEl":
        # nice_channel = "#it{e}#it{e}"
        nice_channel = "ee"
    elif channel.lower() in ["all", "dilepton"]:
        # nice_channel = "#it{l}#it{l}"
        nice_channel = "\\mathscr{ll}"
    else:
        nice_channel = channel
    theDict = {}
    for categorization, categories in categories_dict.items():
        categories_labels = []
        for lcat in categories:
            lht, lbtag, ljet = lcat.replace("blind_", "").split("_")
            thislabel = ""
            if len(lbtag.split("B")) > 1:
                thislabel += " nB#geq" + lbtag.split("B")[-1].replace("+", "").replace("p", "") if "+" in lbtag.split("B")[-1] or "p" in lbtag.split("B")[-1] else " nB=" + lbtag.split("B")[-1]
            if len(ljet.split("nJet")) > 1:
                thislabel += " nJ#geq" + ljet.split("nJet")[-1].replace("+", "").replace("p", "") if "+" in ljet.split("nJet")[-1] or "p" in ljet.split("nJet")[-1] else " nJ=" + ljet.split("nJet")[-1]
            categories_labels.append(thislabel)
        prettycategorization = "PLACEHOLDER PRETTY CATEGORIZATION"
        if categorization.startswith("nMedium"):
            prettycategorization = "{} {} b tags".format(categorization.split("B")[1], categorization.split("B")[0].replace("nMedium", ""))
        elif categorization.startswith("nJet"):
            prettycategorization = "{} jets".format(categorization.split("nJet")[1])
        else:
            prettycategorization = ""
        for variable in variables:
            prettyvariable = variable.replace("FTA", "").replace("_", "") #.replace("Electron", "\\mathscr{e}").replace("electron", "\\mathscr{e}").replace("Muon", "\\mu").replace("muon", "\\mu").replace("_", " ")
            # if prettyvariable == "HT":
            #     prettyvariable = "H\_{T}"
            for k, v in model.items():
                newKey = k.replace("$VAR", variable).replace("$CATEGORIZATION", categorization).replace("$ERA", era)
                if "$CAT" in newKey:
                    for cat in categories:
                        theDict[newKey.replace("$CAT", cat)] = {}
                        for vk, vv in v.items():
                            #newSubkey = vk.replace("$VAR", variable)
                            if type(vv) == str:
                                newSubvalue = vv.replace("$VAR", variable)\
                                                .replace("$ERA", era)\
                                                .replace("$CATEGORIZATION", categorization)\
                                                .replace("$CAT", cat)\
                                                .replace("$CHANNEL", nice_channel)\
                                                .replace("$PRETTYVAR", prettyvariable)\
                                                .replace("$PRETTYCATEGORIZATION", prettycategorization)
                            elif type(vv) == list:
                                newSubvalue = []
                                for l in vv:
                                    if type(l) == str:
                                        newSubvalue.append(l.replace("$VAR", variable)\
                                                           .replace("$ERA", era)\
                                                           .replace("$CATEGORIZATION", category)\
                                                           .replace("$CAT", cat)\
                                                           .replace("$CHANNEL", nice_channel)\
                                                           .replace("$PRETTYVAR", prettyvariable)\
                                                           .replace("$PRETTYCATEGORIZATION", prettycategorization))
                                    else:
                                        newSubvalue.append(l)
                            else:
                                newSubvalue = vv
                            theDict[newKey.replace("$CAT", cat)][vk] = newSubvalue
                        if "Rebin" in theDict[newKey.replace("$CAT", cat)].keys():
                            if force == True:
                                theDict[newKey.replace("$CAT", cat)]["Rebin"] = rebin
                        else:
                            theDict[newKey.replace("$CAT", cat)]["Rebin"] = rebin
                        if "Projection" in theDict[newKey.replace("$CAT", cat)].keys():
                            if force == True:
                                theDict[newKey.replace("$CAT", cat)]["Projection"] = projection
                        else:
                            theDict[newKey.replace("$CAT", cat)]["Projection"] = projection
                else:
                    theDict[newKey] = {}
                    for vk, vv in v.items():
                        #newSubkey = vk.replace("$VAR", variable)
                        if type(vv) == str:
                            newSubvalue = vv.replace("$VAR", variable)\
                                            .replace("$ERA", era)\
                                            .replace("$CATEGORIZATION", categorization)\
                                            .replace("$CHANNEL", nice_channel)\
                                            .replace("$PRETTYVAR", prettyvariable)\
                                            .replace("$PRETTYCATEGORIZATION", prettycategorization)
                        elif type(vv) == list:
                            #Canvas specialization
                            if vk == "Plots":
                                #Plot_ElMu___HT500_ZWindowMET0Width0_$CAT___$VAR"
                                newSubvalue = [copy.copy(name_format).format(chan=channel, cat=cat, var=variable) for cat in categories]
                            #Canvas specialization
                            elif vk == "Labels":
                                newSubvalue = ["{}{}".format(nice_channel, lcat) for lcat in categories_labels]
                            else:
                                newSubvalue = []
                                for l in vv:
                                    if type(l) == str:
                                        newSubvalue.append(l.replace("$VAR", variable)\
                                                           .replace("$ERA", era)\
                                                           .replace("$CATEGORIZATION", category)\
                                                           .replace("$CHANNEL", nice_channel)\
                                                           .replace("$PRETTYVAR", prettyvariable)\
                                                           .replace("$PRETTYCATEGORIZATION", prettycategorization))
                                    else:
                                        newSubvalue.append(l)
                        else:
                            newSubvalue = vv
                        theDict[newKey][vk] = newSubvalue
                    if "Rebin" in theDict[newKey].keys():
                        if force == True:
                            theDict[newKey]["Rebin"] = rebin
                    else:
                        theDict[newKey]["Rebin"] = rebin
                    if "Projection" in theDict[newKey].keys():
                        if force == True:
                            theDict[newKey]["Projection"] = projection
                    else:
                        theDict[newKey]["Projection"] = projection
    return theDict

defaultNoLegend = {
    "DefaultPlot":{
        "Type": "DefaultPlot",
        "Title": "DefaultPlotTitle",
        "Rebin": None,
        "Files": None,
        "Unblind": False,
        "RatioYMin": 0.5,
        "RatioYMax": 1.5,
    },
    "DefaultCanvas":{
        "Type": "DefaultCanvas",
        "Title": "DefaultCanvasTitle",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Plots": None,
        "XPixels": 800, 
        "YPixels": 800,
        "DoRatio": False,
        "DoMountainrange": False,
    }
}
defaultAndLegends = {
    "DefaultPlot":{
        "Type": "DefaultPlot",
        "Title": "DefaultPlotTitle",
        "Rebin": None,
        "Files": None,
        "Unblind": False,
        "RatioYMin": 0.5,
        "RatioYMax": 1.5,
    },
    "DefaultLegend":{
        "Type": "DefaultLegend",
        "Coordinates": [0.0, 0.1, 0.3, 0.65],
        "nColumns": 1,
        "OLDY-Coordinates": [0.35, 0.75, 0.95, 0.90],
        "OLDY-nColumns": 3,
        "Categories": {
            "tttt": {"Color": ROOT.kAzure+4,
                     "Names": ["2017___tttt"],
                     "Style": "Fill",
                    },
            "ttbar": {"Color": ROOT.kRed,
                      "Names": ["2017___tt_DL", "2017___tt_SL", "2017___tt_DL-GF", "2017___tt_SL-GF"],
                      "Style": "Fill",
                     },
            "singletop": {"Color": ROOT.kYellow,
                          "Names": ["2017___ST_tW", "2017___ST_tbarW"],
                          "Style": "Fill",
                         },
            "ttH":  {"Color": ROOT.kMagenta,
                     "Names": ["2017___ttH"],
                     "Style": "Fill",
                    },
            "ttVJets": {"Color": ROOT.kViolet,
                        "Names": ["2017___ttWJets", "2017___ttZJets"],
                        "Style": "Fill",
                       },
            "ttultrarare": {"Color": ROOT.kCyan,
                            "Names": ["2017___ttWW", "2017___ttWH", "2017___ttWZ", 
                                      "2017___ttZZ", "2017___ttZH", "2017___ttHH", "2017___tttJ"],
                            "Style": "Fill",
                           },
            "DY": {"Color": ROOT.kGreen,
                   "Names": ["2017___DYJets_DL"],
                   "Style": "Fill",
                  },
            "Data": {"Color": ROOT.kBlack,
                     "Names": ["MuMu_A", "MuMu_B", "MuMu_C", "MuMu_D", "MuMu_E", "MuMu_F", "MuMu_G", "MuMu_H",
                               "ElMu_A", "ElMu_B", "ElMu_C", "ElMu_D", "ElMu_E", "ElMu_F", "ElMu_G", "ElMu_H",
                               "ElEl_A", "ElEl_B", "ElEl_C", "ElEl_D", "ElEl_E", "ElEl_F", "ElEl_G", "ElEl_H",
                               "El_A", "El_B", "El_C", "El_D", "El_E", "El_F", "El_G", "El_H",
                               "Mu_A", "Mu_B", "Mu_C", "Mu_D", "Mu_E", "Mu_F", "Mu_G", "Mu_H",
                               "2017___ElMu", "2017___MuMu", "2017___ElEl", "2017___El", "2017___Mu",],
                     "Style": "Marker",
                    },
            "QCD": {"Color": ROOT.kPink,
                    "Names": ["2017___QCD_HT200", "2017___QCD_HT300", "2017___QCD_HT500", "2017___QCD_HT700", 
                              "2017___QCD_HT1000", "2017___QCD_HT1500", "2017___QCD_HT2000"],
                    "Style": "Fill",
                   },
        },
        "Supercategories": {
            "Background": {"Names": ["ttbar", "singletop", "ttH", "ttVJets", "ttultrarare", "DY", "QCD"],
                           "Stack": True,
                           "Draw": "HIST",
                                 },
            "Signal": {"Names": ["tttt"],
                       "Stack": False,
                       "Draw": "HIST",
                       },
            "Data": {"Names": ["Data"],
                     "Stack": False,
                     "Draw": "PE1",
                    },
        },
        "Ratios": {"Data/MC": {"Numerator": "Data",
                               "Denominator": "Background",
                               "Color": ROOT.kBlack,
                               "Style": "Marker"
                              }
                  },
        "Systematics": [],
    },
    "SinglePlotLegend":{
        "Type": "DefaultLegend",
        "Coordinates": [0.75, 0.80, 0.95, 0.90],
        "nColumns": 3,
        "Categories": {
            "tttt": {"Color": ROOT.kAzure-2,
                     "Names": ["tttt"],
                     "Style": "Fill",
                    },
            "ttbar": {"Color": ROOT.kRed,
                      "Names": ["tt_DL", "tt_SL", "tt_DL-GF", "tt_SL-GF"],
                      "Style": "Fill",
                     },
            "singletop": {"Color": ROOT.kYellow,
                          "Names": ["ST_tW", "ST_tbarW"],
                          "Style": "Fill",
                         },
            "ttH":  {"Color": ROOT.kMagenta,
                     "Names": ["ttH"],
                     "Style": "Fill",
                    },
            "ttVJets": {"Color": ROOT.kViolet,
                        "Names": ["ttWJets", "ttZJets"],
                        "Style": "Fill",
                       },
            "ttultrarare": {"Color": ROOT.kGreen,
                            "Names": ["ttWW", "ttWH", "ttWZ", "ttZZ", "ttZH", "ttHH", "tttJ"],
                            "Style": "Fill",
                           },
            "DY": {"Color": ROOT.kCyan,
                   "Names": ["DYJets_DL"],
                   "Style": "Fill",
                  },
            "Data": {"Color": ROOT.kBlack,
                     "Names": ["MuMu_A", "MuMu_B", "MuMu_C", "MuMu_D", "MuMu_E", "MuMu_F", "MuMu_G", "MuMu_H",
                               "ElMu_A", "ElMu_B", "ElMu_C", "ElMu_D", "ElMu_E", "ElMu_F", "ElMu_G", "ElMu_H",
                               "ElEl_A", "ElEl_B", "ElEl_C", "ElEl_D", "ElEl_E", "ElEl_F", "ElEl_G", "ElEl_H",
                               "El_A", "El_B", "El_C", "El_D", "El_E", "El_F",
                               "Mu_A", "Mu_B", "Mu_C", "Mu_D", "Mu_E", "Mu_F",
                               "ElMu", "ElEl", "El", "Mu",],
                     "Style": "Marker",
                    },
            "QCD": {"Color": ROOT.kPink,
                    "Names": ["QCD_HT200", "QCD_HT300", "QCD_HT500", "QCD_HT700", 
                              "QCD_HT1000", "QCD_HT1500", "QCD_HT2000"],
                    "Style": "Fill",
                   },
        },
        "Supercategories": {
            "Signal+Background": {"Names": ["tttt", "ttbar", "singletop", "ttH", "ttVJets", "ttultrarare", "DY", "QCD"],
                                  "Stack": True,
                                  "Draw": "HIST",
                                 },
            "Data": {"Names": ["Data"],
                     "Stack": False,
                     "Draw": "PE1",
                    },
        },
        "Ratios": {"Data/MC": {"Numerator": "Data",
                               "Denominator": "Signal+Background",
                               "Color": ROOT.kBlack,
                               "Style": "Marker"
                              }
                  },
    },
    "DefaultCanvas":{
        "Type": "DefaultCanvas",
        "Title": "DefaultCanvasTitle",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Plots": None,
        "XPixels": 800, 
        "YPixels": 800,
        "DoRatio": False,
        "DoMountainrange": False,
    },
}
defaultForStitchComparison = {
    "DefaultPlot":{
        "Type": "DefaultPlot",
        "Title": "DefaultPlotTitle",
        "Rebin": None,
        "Files": None,
        "Unblind": False,
        "RatioYMin": 0.5,
        "RatioYMax": 1.5,
    },
    "DefaultLegend":{
        "Type": "DefaultLegend",
        "Coordinates": [0.35, 0.75, 0.95, 0.90],
        "nColumns": 3,
        "Categories": {
            "tttt": {"Color": ROOT.kAzure-2,
                     "Names": ["tttt"],
                     "Style": "Fill",
                    },
            "ttbar": {"Color": ROOT.kRed,
                      "Names": ["tt_DL", "tt_SL", "tt_DL-GF", "tt_SL-GF"],
                      "Style": "Fill",
                     },
            "ttbar-UNSTITCHED": {"Color": ROOT.kRed,
                      "Names": ["tt_DL-UNSTITCHED", "tt_SL-UNSTITCHED",],
                      "Style": "Fill",
                     },
            "singletop": {"Color": ROOT.kYellow,
                          "Names": ["ST_tW", "ST_tbarW"],
                          "Style": "Fill",
                         },
            "ttH":  {"Color": ROOT.kMagenta,
                     "Names": ["ttH"],
                     "Style": "Fill",
                    },
            "ttVJets": {"Color": ROOT.kViolet,
                        "Names": ["ttWJets", "ttZJets"],
                        "Style": "Fill",
                       },
            "ttultrarare": {"Color": ROOT.kGreen,
                            "Names": ["ttWW", "ttWH", "ttWZ", "ttZZ", "ttZH", "ttHH", "tttJ"],
                            "Style": "Fill",
                           },
            "DY": {"Color": ROOT.kCyan,
                   "Names": ["DYJets_DL"],
                   "Style": "Fill",
                  },
            "Data": {"Color": ROOT.kBlack,
                     "Names": ["MuMu_A", "MuMu_B", "MuMu_C", "MuMu_D", "MuMu_E", "MuMu_F", "MuMu_G", "MuMu_H",
                               "ElMu_A", "ElMu_B", "ElMu_C", "ElMu_D", "ElMu_E", "ElMu_F", "ElMu_G", "ElMu_H",
                               "ElEl_A", "ElEl_B", "ElEl_C", "ElEl_D", "ElEl_E", "ElEl_F", "ElEl_G", "ElEl_H",
                               "El_A", "El_B", "El_C", "El_D", "El_E", "El_F",
                               "Mu_A", "Mu_B", "Mu_C", "Mu_D", "Mu_E", "Mu_F",
                               "ElMu", "ElEl", "El", "Mu",],
                     "Style": "Marker",
                    },
            "QCD": {"Color": ROOT.kPink,
                    "Names": ["QCD_HT200", "QCD_HT300", "QCD_HT500", "QCD_HT700", 
                              "QCD_HT1000", "QCD_HT1500", "QCD_HT2000"],
                    "Style": "Fill",
                   },
        },
        "Supercategories": {
            "Signal+Background": {"Names": ["tttt", "ttbar", "singletop", "ttH", "ttVJets", "ttultrarare", "DY", "QCD"],
                                  "Stack": True,
                                  "Draw": "HIST",
                                 },
            "UNSTITCHED": {"Names": ["tttt", "ttbar-UNSTITCHED", "singletop", "ttH", "ttVJets", "ttultrarare", "DY", "QCD"],
                                  "Stack": False,
                                  "Draw": "PE1",
                                 },
        },
        "Ratios": {"Unstitched/Stitched": {"Numerator": "UNSTITCHED",
                               "Denominator": "Signal+Background",
                               "Color": ROOT.kBlack,
                               "Style": "Marker"
                              }
                  },
    },
    "DefaultCanvas":{
        "Type": "DefaultCanvas",
        "Title": "DefaultCanvasTitle",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Plots": None,
        "XPixels": 800, 
        "YPixels": 800,
        "DoRatio": False,
        "DoMountainrange": False,
    },
}
defaultForStitchComparisonOnlyTT = {
    "DefaultPlot":{
        "Type": "DefaultPlot",
        "Title": "DefaultPlotTitle",
        "Rebin": None,
        "Files": None,
        "Unblind": False,
        "RatioYMin": 0.5,
        "RatioYMax": 1.5,
    },
    "DefaultLegend":{
        "Type": "DefaultLegend",
        "Coordinates": [0.35, 0.75, 0.95, 0.90],
        "nColumns": 3,
        "Categories": {
            "ttbar": {"Color": ROOT.kRed,
                      "Names": ["tt_DL", "tt_SL", "tt_DL-GF", "tt_SL-GF"],
                      "Style": "Fill",
                     },
            "ttbar-UNSTITCHED": {"Color": ROOT.kBlack,
                      "Names": ["tt_DL-UNSTITCHED", "tt_SL-UNSTITCHED",],
                      "Style": "Marker",
                     },
        },
        "Supercategories": {
            "STITCHED": {"Names": ["ttbar",],
                                  "Stack": True,
                                  "Draw": "HIST",
                                 },
            "UNSTITCHED": {"Names": ["ttbar-UNSTITCHED",],
                                  "Stack": False,
                                  "Draw": "PE1",
                                 },
        },
        "Ratios": {"Unstitched/Stitched": {"Numerator": "UNSTITCHED",
                               "Denominator": "STITCHED",
                               "Color": ROOT.kBlack,
                               "Style": "Marker"
                              }
                  },
    },
    "DefaultCanvas":{
        "Type": "DefaultCanvas",
        "Title": "DefaultCanvasTitle",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Plots": None,
        "XPixels": 800, 
        "YPixels": 800,
        "DoRatio": False,
        "DoMountainrange": False,
    },
}
argsDOTplotJSON = {
    "Plot_nJet4_HT":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Style": {"MC": "Fill",
                  "Data": "Marker",
                 },
        "Files": "nJet4_HT.root",
        "Unblind": False,
    },
    "Plot_nJet5_HT":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Style": {"MC": "Fill",
                  "Data": "Marker",
                 },
        "Files": "nJet5_HT.root",
        "Unblind": False,
    },
    "Plot_blind_nJet6_HT":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Style": {"MC": "Fill",
                  "Data": "Marker",
                 },
        "Files": "blind_nJet6_HT.root",
        "Unblind": False,
    },
    "Plot_blind_nJet7_HT":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Style": {"MC": "Fill",
                  "Data": "Marker",
                 },
        "Files": "blind_nJet7_HT.root",
        "Unblind": False,
    },
    "Plot_blind_nJet8+_HT":{
        "Type": "PlotConfig",
        "Title": "DefaultPlotTitle",
        "Xaxis": None,
        "Yaxis": None,
        "Rebin": None,
        "Style": {"MC": "Fill",
                  "Data": "Marker",
                 },
        "Files": "blind_nJet8+_HT.root",
        "Unblind": False,
    },
    "Canvas_HT":{
        "Type": "CanvasConfig",
        "Title": "HT (nJet == {4, 5, 6, 7, 8+})",
        "Margins": [0.05, 0.05, 0.1, 0.1],
        "Plots": ["Plot_nJet4_HT", "Plot_nJet5_HT", "Plot_blind_nJet6_HT", "Plot_blind_nJet7_HT", "Plot_blind_nJet8+_HT"],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "DoRatio": True,
        "DoMountainrange": True,
        "doLogY": False,
    },
    "Canvas_LogY_HT":{
        "Type": "CanvasConfig",
        "Title": "HT (nJet == {4, 5, 6, 7, 8+})",
        "Margins": [0.1, 0.1, 0.1, 0.1],
        "Plots": ["Plot_nJet4_HT", "Plot_nJet5_HT", "Plot_blind_nJet6_HT", "Plot_blind_nJet7_HT", "Plot_blind_nJet8+_HT"],
        "Legend": "DefaultLegend",
        "XPixels": 1200, 
        "YPixels": 1000,
        "DoRatio": True,
        "DoMountainrange": True,
        "doLogY": True,
    },
}
#Add the defaults and any common legends to the dictionary
argsDOTplotJSON.update(defaultAndLegends)


def json_load_byteified(file_handle):
    return json.load(file_handle)

def json_loads_byteified(json_text):
    return json.loads(json_text)

# def json_load_byteified(file_handle):
#     return _byteify(
#         json.load(file_handle, object_hook=_byteify),
#         ignore_dicts=True
#     )

# def json_loads_byteified(json_text):
#     return _byteify(
#         json.loads(json_text, object_hook=_byteify),
#         ignore_dicts=True
#     )

# def _byteify(data, ignore_dicts = False):
#     # if this is a unicode string, return its string representation
#     if isinstance(data, unicode):
#         return data.encode('utf-8')
#     # if this is a list of values, return list of byteified values
#     if isinstance(data, list):
#         return [ _byteify(item, ignore_dicts=True) for item in data ]
#     # if this is a dictionary, return dictionary of byteified keys and values
#     # but only if we haven't already byteified it
#     if isinstance(data, dict) and not ignore_dicts:
#         return {
#             _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
#             for key, value in data.iteritems()
#         }
#     # if it's anything else, return it in its original form
#     return data

def uproot_hist_hist2array(pyroot_obj, flow=True):
    intermediate = uproot.pyroot.from_pyroot(pyroot_obj).to_hist()
    return np.copy(intermediate.values(flow=flow)), [np.copy(axis.edges) for axis in intermediate.axes]

def root_numpy_hist2array(pyroot_obj, flow=True):
    vals, edgesTup = root_numpy.hist2array(pyroot_obj, include_overflow=flow, copy=True, return_edges=True)
    return vals, edgesTup

def pyroot_hist2array(pyroot_obj, flow=True):
    if not isinstance(pyroot_obj, (ROOT.TH1, ROOT.TProfile)):
        raise NotImplementedError("Only 1-dimensional types supported for now")
    start, end = (0, pyroot_obj.GetXaxis().GetNbins()+2) if flow else (1, pyroot_obj.GetXaxis().GetNbins()+1)
    vals = []
    edges = []
    for x in range(start, end):
        vals.append(pyroot_obj.GetBinContent(x))
        if x > 0 and x < pyroot_obj.GetXaxis().GetNbins()+2:
            edges.append(pyroot_obj.GetBinLowEdge(x))
    return np.array(vals), [np.array(edges)]
    
try:
    import root_numpy
    wrapped_hist2array = root_numpy_hist2array
except:
    try:
        import uproot
        wrapped_hist2array = uproot_hist_hist2array
    except:
        wrapped_hist2array = pyroot_hist2array

#prototyping the array2hist construction... but is it necessary?
# h6 = Hist(hist.axis.Variable(root_numpy.hist2array(h3, return_edges=True)[1][0], label="x", flow=True))
# >>> h6.view()[:] = root_numpy.hist2array(h3, return_edges=True, include_overflow=True)[0]
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# ValueError: could not broadcast input array from shape (7) into shape (5)
# >>> h6.view(flow=True)[:] = root_numpy.hist2array(h3, return_edges=True, include_overflow=True)[0]
# >>> h6
# Hist(Variable([0, 1, 2, 3, 4, 5]), storage=Double()) # Sum: 1000.0
# >>> hs.values(flow=True)
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# NameError: name 'hs' is not defined
# >>> h6.values(flow=True)
# array([  0., 692., 253.,  51.,   3.,   1.,   0.])

def cartesianProductList(name_format="$NUM_$LET_$SYM", name_tuples=[("$NUM", ["1", "2"]), ("$LET", ["A", "B", "C"]), ("$SYM", ["*", "@"])]):
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
def setGStyle(nDivisions=105):
    #Override stats style with ROOT.gStyle.SetOptStat(<opt string>) with following elements
    #k :  kurtosis printed
    #K :  kurtosis and kurtosis error printed
    #s :  skewness printed
    #S :  skewness and skewness error printed
    #i :  integral of bins printed
    #o :  number of overflows printed
    #u :  number of underflows printed
    #r :  rms printed
    #R :  rms and rms error printed
    #m :  mean value printed
    #M :  mean value mean error values printed
    #e :  number of entries printed
    #n :  name of histogram is printed
    
    #If interacting with TPaveStats object in batch mode, after calling histogram draw, should also call:
    #gPad->Update();
    #TPaveStats *st = (TPaveStats*)h->FindObject("stats");
    #st->SetX1NDC(newx1); //new x start position
    #st->SetX2NDC(newx2); //new x end position
    #st->SetStats(0); //disable stat box for this histogram
    #st->SetStats(1); //re-enable stat box
    #ROOT.gStyle.SetCanvasBorderMode(0)
    #ROOT.gStyle.SetCanvasColor(ROOT.kWhite)
    ##ROOT.gStyle.SetCanvasDefH(600)
    ##ROOT.gStyle.SetCanvasDefW(600)
    ##ROOT.gStyle.SetCanvasDefX(0)
    ##ROOT.gStyle.SetCanvasDefY(0)

    ##ROOT.gStyle.SetPadTopMargin(0.08)
    ##ROOT.gStyle.SetPadBottomMargin(0.13)
    ##ROOT.gStyle.SetPadLeftMargin(0.16)
    ##ROOT.gStyle.SetPadRightMargin(0.05)

    ROOT.gStyle.SetHistLineColor(1)
    ROOT.gStyle.SetHistLineStyle(0)
    ROOT.gStyle.SetHistLineWidth(1)
    ROOT.gStyle.SetEndErrorSize(2)
    ROOT.gStyle.SetMarkerStyle(20)

    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleColor(1)
    ROOT.gStyle.SetTitleTextColor(1)
    ROOT.gStyle.SetTitleFillColor(10)
    ROOT.gStyle.SetTitleFontSize(0.05)

    ROOT.gStyle.SetTitleColor(1, "XYZ")
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetTitleSize(0.10, "XYZ")
    ROOT.gStyle.SetTitleXOffset(1.00)
    ROOT.gStyle.SetTitleYOffset(1.60)
    # ROOT.gStyle.SetTitleColor(1, "XYZ")
    # ROOT.gStyle.SetTitleFont(43, "XYZ")
    # ROOT.gStyle.SetTitleSize(50, "XYZ")
    # ROOT.gStyle.SetTitleXOffset(1.00)
    # ROOT.gStyle.SetTitleYOffset(1.60)

    ROOT.gStyle.SetLabelColor(1, "XYZ")
    ROOT.gStyle.SetLabelFont(43, "XYZ")
    # ROOT.gStyle.SetLabelOffset(, "XYZ")
    ROOT.gStyle.SetLabelSize(25, "XYZ")
    # ROOT.gStyle.SetLabelColor(1, "XYZ")
    # ROOT.gStyle.SetLabelFont(43, "XYZ")
    # ROOT.gStyle.SetLabelOffset(0.007, "XYZ")
    # ROOT.gStyle.SetLabelSize(0.04, "XYZ")
    
    ROOT.gStyle.SetAxisColor(1, "XYZ")
    ROOT.gStyle.SetStripDecimals(True)
    ROOT.gStyle.SetTickLength(0.03, "XYZ")
    ROOT.gStyle.SetNdivisions(nDivisions, "XYZ")
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)

    ROOT.gStyle.SetPaperSize(20., 20.)
    ROOT.gStyle.SetHatchesLineWidth(1)
    ROOT.gStyle.SetHatchesSpacing(1)

    ROOT.TGaxis.SetExponentOffset(-0.08, 0.01, "Y")
    #Improve png resolution 
    ROOT.gStyle.SetImageScaling(4.0)

def createRatio(h1, h2, Cache=None, ratioTitle="input 0 vs input 1", ratioColor = None, ratioStyle = None,
                ratioMarkerStyle = 20, ratioAlpha = 0.5, yMin = 0.1, yMax = 1.9, isBlinded=False, xLabelSize=50, yLabelSize=50, nDivisions=105,):
    #h3 = h1.Clone("rat_{}_{}".format(h1.GetName(), ratioTitle.replace(" ", "_")))
    #h3 = h1.Clone("rat_{}".format(h1.GetName()))
    if h1 is None or h2 is None:
        uniqueName = str(uuid.uuid1()).replace("-", "_")
        h3 = ROOT.TH1F(uniqueName, "", 1, 0, 1)
    else:
        # print("debug: {} // {}".format((h1.GetName()).replace("h_",""), (h2.GetName()).replace("h_","")))
        h3 = h1.Clone("ratio_{}__{}".format( (h1.GetName()).replace("h_",""), (h2.GetName()).replace("h_","") ))
    if ratioStyle == "Fill":
        if ratioColor != None:
            h3.SetMarkerColor(ROOT.kWhite)
            h3.SetFillColor(ratioColor)
            h3.SetLineColor(ratioColor)
        else:
            h3.SetMarkerColor(ROOT.kWhite)
            h3.SetFillColor(h3.GetFillColor())
            h3.SetLineColor(h3.GetFillColor())
    elif ratioStyle == "FillAlpha":
        if ratioColor != None:
            h3.SetMarkerColor(ROOT.kWhite)
            h3.SetFillColorAlpha(ratioColor, ratioAlpha)
            h3.SetLineColor(ratioColor)
        else:
            h3.SetMarkerColor(ROOT.kWhite)
            h3.SetFillColorAlpha(h3.GetFillColor(), ratioAlpha)
            h3.SetLineColor(h3.GetFillColor())
    elif ratioStyle == "Line":
        if ratioColor != None:
            h3.SetMarkerColor(ratioColor)
            h3.SetFillColor(ROOT.kWhite)
            h3.SetLineColor(ratioColor)
            h3.SetLineWidth(1)
        else:
            h3.SetMarkerColor(ROOT.kMagenta)
            h3.SetFillColor(ROOT.kOrange)
            h3.SetLineColor(h3.GetFillColor())
            h3.SetLineWidth(1)
    elif ratioStyle == "Marker": 
        h3.SetMarkerStyle(ratioMarkerStyle)
        h3.SetMarkerSize(1.0)
        if ratioColor != None:   
            h3.SetMarkerColor(ratioColor)
            h3.SetLineColor(ratioColor)
            h3.SetFillColor(ratioColor)
        else:
            h3.SetMarkerColor(h3.GetMarkerColor())
            h3.SetLineColor(h3.GetMarkerColor())
            h3.SetFillColor(ROOT.kWhite)
    else:
        if ratioColor != None:
            h3.SetMarkerColor(ratioColor)
            h3.SetFillColor(ratioColor)
            h3.SetLineColor(ratioColor)
        
    #FIXME#h3.SetMarkerStyle(21)
    # h3.SetTitle("")
    # Set up plot for markers and errors according to ROOT example, but SetStats(0) might be too minimal sometimes
    # h3.Sumw2() #Not necesary if set globally already
    h3.SetStats(0)
    if str(h2.ClassName()) in ["TH1I", "TH1F", "TH1D"]:
        # if h3.GetNbinsX() != h2.GetNbinsX():
        #     pdb.set_trace()
        h3.Divide(h2)
    else:
        raise NotImplementedError("Unhandled class type for histogram division: {}".format(str(h2.ClassName())))
    h3.SetMinimum(yMin)
    h3.SetMaximum(yMax)

    # Adjust y-axis settings
    # y = h3.GetYaxis()
    h3.GetYaxis().SetTitle(ratioTitle)
    h3.GetYaxis().SetNdivisions(nDivisions)
    #FIXME#y.SetTitleSize(20)
    #FIXME#y.SetTitleFont(43)
    #FIXME#y.SetTitleOffset(2.5) #1.55
    h3.GetYaxis().SetLabelFont(43)
    h3.GetYaxis().SetLabelSize(yLabelSize)

    # Adjust x-axis settings
    # x = h3.GetXaxis()
    h3.GetXaxis().SetNdivisions(nDivisions)
    #FIXME#x.SetTitleSize(20)
    #FIXME#x.SetTitleFont(43)
    #FIXME#x.SetTitleOffset(4.0)
    h3.GetXaxis().SetLabelFont(43)
    h3.GetXaxis().SetLabelSize(xLabelSize)
    # h3.GetXaxis().SetLabelOffset(10)

    #Do blinding
    if isBlinded:
        for i in range(h3.GetNbinsX()):
            h3.SetBinContent(i+1, 0.0)
        h3.SetMarkerColor(ROOT.kWhite)
        h3.SetLineColor(ROOT.kWhite)
        h3.SetFillColor(ROOT.kWhite)
    if Cache == None:
        Cache = {}
    #These keys will not be sufficient for multiple ratios to be plotted together, #FIXME
    Cache["ratio_hist"] = h3
    Cache["ratio_Xaxis"] = h3.Clone().GetXaxis()
    Cache["ratio_Yaxis"] = h3.Clone().GetYaxis()
    return Cache


def createCanvasPads(canvasTitle, Cache=None, doRatio=False, doMountainrange=False, setXGrid=False, setYGrid=False,
                     nXPads=1, topFraction=0.7, bordersLRTB=[0.1, 0.1, 0.1, 0.1], xPixels=800, yPixels=800):
    """Create canvas with two pads vertically for each of doLin and doLog if they are true"""
    #Divide implicitely creates subpads. This function uses more explicit methods to do the same with varying pad sizes
    c = ROOT.TCanvas(canvasTitle, canvasTitle, xPixels, yPixels)
    # Upper histogram plot is pad1
    upperPads = []
    lowerPads = []
    #Calculate borders as fraction of the canvas, starting from the desired input. The borders will include area for
    #axes and titles.
    bordersL = bordersLRTB[0]
    bordersR = bordersLRTB[1]
    bordersT = bordersLRTB[2]
    bordersB = bordersLRTB[3]
    #FIXME: Add in space for margins on the left, which will require an additional offset when calculating the edges
    usableLR = 1.0 - bordersL - bordersR
    usableTB = 1.0 - bordersT - bordersB
    #FIXME: This is really for Mountain Ranges where they're all joined. If pads are to be separated, should 
    #not make assumptions about the larger left/right pads that include border size.
    #Then try limiting precision to get rid of weird visual artifacts by casting to limited precision string and back
    xEdgesLow = [bordersL + usableLR*z/float(nXPads) for z in range(nXPads)]
    #Unnecessary for pdf, doesn't help with jsroot canvas gap between 3rd and 4th pads in mountain range
    #xEdgesLow = [float("{:.3f}".format(edge)) for edge in xEdgesLow] 
    xEdgesHigh = [bordersL + usableLR*(z+1)/float(nXPads) for z in range(nXPads)]
    #xEdgesHigh = [float("{:.3f}".format(edge)) for edge in xEdgesHigh]
    #Now the edges must be calculated for each pad, hardcode nYPads = 2
    nYPads = 2
    #Here's where we correct the 1st and last pads to make space for the border/pad margin
    xEdgesLow[0] -= bordersL
    # xEdgesHigh[-1] += bordersR
    if not doRatio:
        print("Overriding topFraction for pad sizing")
        topFraction = 1
    yEdgesLow = [0, bordersB + usableTB*(1-topFraction)]
    yEdgesHigh = [bordersB + usableTB*(1-topFraction), 1]
    #yEdgesLow[0] -= bordersB
    #yEdgesHigh[-1] += bordersT
    # yDivision = 1-bordersT #Deprecated... not used anywhere?
    # if doRatio:
    #     yDivision = 1-topFraction
        
    #Calculate the pad margins, which will be converted from the desired border size as fraction of the total canvas size
    #to equivalent fraction of the pad size itself, using the edges arrays.
    marginL = bordersL/(xEdgesHigh[0] - xEdgesLow[0])
    marginR = bordersR/(xEdgesHigh[-1] - xEdgesLow[-1])
    marginB = bordersB/(yEdgesHigh[0] - yEdgesLow[0])
    marginT = bordersT/(yEdgesHigh[-1] - yEdgesLow[-1])
    #print("{} {} \n {} {}".format(xEdgesLow, xEdgesHigh, yEdgesLow, yEdgesHigh))
    #print("{} {} {} {}".format(marginL, marginR, marginT, marginB))


    for z in range(nXPads):
        c.cd()  # returns to main canvas before defining another pad, to not create sub-subpad
        padU = ROOT.TPad("{}_{}".format(canvasTitle,z), "{}_{}".format(canvasTitle,z), 
                        xEdgesLow[z], yEdgesLow[-1], xEdgesHigh[z], yEdgesHigh[-1]) #xmin ymin xmax ymax as fraction
        #Set margins for pads depending on passed configuration option, whether ratio and mountainranging are enabled
        padU.SetTopMargin(marginT)
        if doRatio:
            padU.SetBottomMargin(0.02)  # joins upper and lower plot
        else:
            padU.SetBottomMargin(marginB)
        if doMountainrange:
            #Only set the margin to 0 if there is at least one pad to the right, which is equal to zlast = nXPads - 1. Don't do the last right margin...
            if 0 <= z < nXPads - 1:
                padU.SetRightMargin(0)
            else:
                padU.SetRightMargin(marginR)
            #Set all right margins to 0, so that size is consistented between n-1 pads (the first still being oddly sized by the left margin...)
            if 0 <= z < nXPads:
                padU.SetRightMargin(0)
            #Now do the left margins, only starting with the second pad, should it exist (hence the equality switching versus the right margins)
            if 0 < z <= nXPads - 1:
                padU.SetLeftMargin(0)
            else:
                padU.SetLeftMargin(marginL)
        if setXGrid:
            padU.SetGridx()
        if setYGrid:
            padU.SetGridy()
        padU.Draw()
        if doRatio:
            # Lower ratio plot is pad2
            padL = ROOT.TPad("ratio_{}_{}".format(canvasTitle,z), "ratio_{}_{}".format(canvasTitle,z), 
                             xEdgesLow[z], yEdgesLow[0], xEdgesHigh[z], yEdgesHigh[0]) #xmin ymin xmax ymax as fraction
            padL.SetTopMargin(0.02)  # joins upper and lower plot
            padL.SetBottomMargin(marginB)
            if doMountainrange:
                # Only set the margin to 0 if there is at least one pad to the right, which is equal to zlast = nXPads - 1. Don't do the last right margin...
                if 0 <= z < nXPads - 1:
                    padL.SetRightMargin(0)
                else:
                    padL.SetRightMargin(marginR)
                if 0 <= z < nXPads:
                    padL.SetRightMargin(0)
                #Now do the left margins, only starting with the second pad, should it exist (hence the equality switching versus the right margins)
                if 0 < z <= nXPads - 1:
                    padL.SetLeftMargin(0)
                else:
                    padL.SetLeftMargin(marginL)
            if setXGrid:
                padL.SetGridx()
            if setYGrid:
                padL.SetGridy()
            padL.Draw()
            lowerPads.append(padL)
        upperPads.append(padU)
    if Cache == None:
        Cache = {}
    Cache["canvas"] = c
    Cache["canvas/xEdgesLow"] = xEdgesLow
    Cache["canvas/xEdgesHigh"] = xEdgesHigh
    Cache["canvas/yEdgesLow"] = yEdgesLow
    Cache["canvas/yEdgesHigh"] = yEdgesHigh
    Cache["canvas/bordersL"] = bordersL
    Cache["canvas/bordersR"] = bordersR
    Cache["canvas/bordersT"] = bordersT
    Cache["canvas/bordersB"] = bordersB
    Cache["canvas/marginL"] = marginL
    Cache["canvas/marginR"] = marginR
    Cache["canvas/marginT"] = marginT
    Cache["canvas/marginB"] = marginB
    Cache["canvas/upperPads"] = upperPads
    Cache["canvas/lowerPads"] = lowerPads
    return Cache

def getLabelAndHeader(Cache=None, label="#bf{CMS Internal}", 
                      header="#sqrt{{s}} = 13 TeV, L_{{int}} = {0} fb^{{-1}}".format("PLACEHOLDER"), 
                      marginTop=0.1, pixels=None,
                      header_position=0.63, label_position=0.05):
    # Add header
    cms_label = ROOT.TLatex()
    cms_header = ROOT.TLatex()
    if type(pixels) == int:
        cms_label.SetTextSizePixels(int(0.04*pixels))
        cms_header.SetTextSizePixels(int(0.03*pixels))
    else:
        cms_label.SetTextSize(0.04)
        cms_header.SetTextSize(0.03)
    cms_label.DrawLatexNDC(label_position, 1-0.55*marginTop, str(label))
    cms_header.DrawLatexNDC(header_position, 1-0.55*marginTop, str(header))
    if Cache == None:
        Cache = {}
    Cache["cms_label"] = cms_label
    Cache["cms_header"] = cms_header
    return Cache

def prepareLabel(pixels=None):
    cms_label = ROOT.TLatex()
    if type(pixels) == int:
        cms_label.SetTextSizePixels(int(0.04*pixels))
    else:
        cms_label.SetTextSize(0.04)
    return cms_label

def prepareLumi(pixels=None):
    cms_header = ROOT.TLatex()
    if type(pixels) == int:
        cms_header.SetTextSizePixels(int(0.03*pixels))
    else:
        cms_header.SetTextSize(0.03)
    return cms_header

def addHists(inputHists, name, scaleArray = None, blind=False):
    """Add a list of histograms together, with the name passed, and with scaling done according to a matching length array containing the floats for each histogram.

    blinding, when set to true, only prepends "BLIND" to the beginning of thehistogram name, rather than zeroing out bin values or any other method."""
    retHist = None
    blindTag = "BLIND" if blind else ""
    for hn, hist in enumerate(inputHists):
        if hn == 0:
            retHist = hist.Clone("{}{}".format(blindTag, name))
            if scaleArray != None and len(scaleArray) == len(inputHists):
                retHist.Scale(scaleArray[hn])
        else:
            if scaleArray != None and len(scaleArray) == len(inputHists):
                retHist.Add(hist, scaleArray[hn])
            else:
                retHist.Add(hist)
    return retHist

# @profile(output_file="makeCategoryHists_profile.txt", sort_by="cumulative", lines_to_print=500, strip_dirs=True)
def makeCategoryHists(histFile, histKeys, legendConfig, histNameCommon, systematic=None, rebin=None, setRangeUser=None, projection=None, 
                      profile=None, separator="___", nominalPostfix="nom", verbose=False, debug=False, pn=None, 
                      normalizeToNominal=False, smoothing=0, zeroingThreshold=50, differentialScale=False):
    """Function tailored to using a legendConfig to create histograms.
    
    The legendConfig contains the sampleNames to prefix for the rest of the histogram name.
    histNameCommon is the common part of the name, without the sample name (in legendConfig 
    ['Categories']['Names'] list) or the systematic variation name at the end. The separator 
    variable denotes how to join the common name with the sample name and systematic, 
    and there's a fallback to nominalPostfix if the systematic is not present or is None"""
    #Take the legendConfig, which includes coloring and style information in addition to 
    #The Categories group contains the name of each category along with its color, style, and list of histogram (base) names
    #Particular details like title, axes, etc. are left to the higher level function to change.
    if type(legendConfig) != dict or "Categories" not in legendConfig.keys():
        raise ValueError("legendConfig passed to makeCategoryHists contains no 'Categories' key")
    # histKeys = set([hist.GetName() for hist in histFile.GetListOfKeys()])
    # unblindedKeys = dict([(histKey.replace("blind_", "").replace("BLIND", ""), histKey) for histKey in histKeys]) #Don't use "blind_" anywhere, get rid of this function call..
    unblindedKeys = dict([(histKey.replace("BLIND", "") if "BLIND" in histKey else histKey, histKey) for histKey in histKeys])
    if debug:
        print("The histKeys are: {}".format(" ".join(histKeys)))
    #Create dictionary of histograms to be returned by the function
    retHists = {}
    #Create a baseName using the passed rootPrefixName and systematic, if non-None. Will be combined with category information
    #when making each added histogram's name
    baseName = None
    if systematic == None:
        expectedBaseName = histNameCommon + separator + nominalPostfix if nominalPostfix != None else histNameCommon
        fallbackBaseName = histNameCommon + separator + nominalPostfix if nominalPostfix != None else histNameCommon
    else:
        expectedBaseName = histNameCommon + separator + systematic
        fallbackBaseName = histNameCommon + separator + nominalPostfix if nominalPostfix != None else histNameCommon
    #Create list of histograms not found, to potentially be reported up the chain
    theUnfound = collections.OrderedDict()    
    #Cycle through the config's categories
    for sampleCat, config in legendConfig["Categories"].items():
        theUnfound[sampleCat] = collections.OrderedDict()    
        histoList = []
        nominalList = []
        addHistoName = sampleCat + separator + expectedBaseName
        #print(addHistoName)
        scaleArray = config.get("ScaleArray", None)
        scaleList = [] if scaleArray != None else None
        successCounter = 0
        attemptedName = None
        for nn, subCatName in enumerate(config["Names"]):
            expectedName = subCatName + separator + expectedBaseName
            fallbackName = subCatName + separator + fallbackBaseName
            attemptedName = (expectedName,fallbackName)
            if debug: print("Creating addHistoName {}".format(addHistoName))
            #Skip plots that contain neither the systematic requested nor the nominal histogram
            # if expectedName in histKeys:
            if expectedName in unblindedKeys:
                #Append the histo to a list which will be added using a dedicated function
                successCounter += 1
                histoList.append(histFile.Get(unblindedKeys[expectedName]))
                nominalList.append(histFile.Get(unblindedKeys[fallbackName]))
                if scaleList != None:
                    scaleList.append(scaleArray[nn])
            # elif fallbackName in histKeys:
            elif fallbackName in unblindedKeys:
                #Append the histo to a list which will be added using a dedicated function
                successCounter += 1
                histoList.append(histFile.Get(unblindedKeys[fallbackName]))
                nominalList.append(None)
                if scaleList != None:
                    scaleList.append(scaleArray[nn])
            else:
                theUnfound[sampleCat][subCatName] = expectedName
                if verbose:
                    print("for {} and histNameCommon {}, makeCombinationHists failed to find a histogram (systematic or nominal) corresponding to {}\n\t{}\n\t{}"\
                          .format(histFile.GetName(), histNameCommon, subCatName, expectedName, fallbackName))
                continue
        # Need to make this work with e.g. QCD which isn't there...
        # if successCounter == 0:
        #     maxLength = min(len(unblindedKeys), 100)
        #     raise RuntimeError("Found no working keys, a pair of attempted keys were {}, and the list of unblinded keys were {}".format(attemptedName, list(unblindedKeys.keys())[:maxLength]))

        for nHist, hist in enumerate(histoList):
            #Normalize to the nominal, if applicable
            if normalizeToNominal and isinstance(nominalList[nHist], (ROOT.TH1, ROOT.TH2, ROOT.TH3)):
                if abs(nominalList[nHist].Integral()) > 1e-7:
                    hist.Scale(nominalList[nHist].Integral()/hist.Integral())
            if isinstance(smoothing, int) and smoothing > 0 and isinstance(nominalList[nHist], (ROOT.TH1, ROOT.TH2, ROOT.TH3)):
                hist.Add(nominalList[nHist], -1)
                hist.Smooth(smoothing, "")
                hist.Add(nominalList[nHist], 1)        

        #Make the new histogram with addHistoName, optionally with per-histogram scaling factors
        if debug:
            print("The histoList currently is: {} and the desired categories is {}".format(histoList, config["Names"]))
        #print(addHistoName)
        
        if len(histoList) == 0:
            if debug:
                print("for category '{}' and config '{}', the histoList is empty".format(sampleCat, config["Names"]))
            continue
        else:
            retHists[sampleCat] = addHists(histoList, addHistoName, scaleArray = scaleList, 
                                           blind=True if len([bb.GetName() for bb in histoList if "BLIND" in bb.GetName()]) > 0 else False)
            #do projection of the histogram if it's 2D or 3D, based on either the axis
            # or a list containing the axis and projection bins
            if projection == None:
                pass
            elif isinstance(projection, str):
                pre_projection_name = retHists[sampleCat].GetName()
                # if "ROOT.TH2" in str(type(retHists[sampleCat])):
                if isinstance(retHists[sampleCat], ROOT.TH2):
                    retHists[sampleCat].SetName(pre_projection_name + "_preProjection")
                    if projection == "X":
                        retHists[sampleCat] = retHists[sampleCat].ProjectionX(pre_projection_name)
                    elif projection == "Y":
                        retHists[sampleCat] = retHists[sampleCat].ProjectionY(pre_projection_name)
                    else:
                        print("Error, {} is not a valid projection axis for TH2".format(projection))
                # elif "ROOT.TH3" in str(type(retHists[sampleCat])):
                elif isinstance(retHists[sampleCat], ROOT.TH3):
                    retHists[sampleCat].SetName(pre_projection_name + "_preProjection")
                    if projection in ["X", "Y", "Z", "XY", "XZ", "YZ", "YX", "ZX", "ZY"]:
                        retHists[sampleCat] = retHists[sampleCat].Project3D(projection)
                    else:
                        print("Error, {} is not a valid projection axis/axes for TH3".format(projection))
                else:
                    print("Error, projection not possible for input type in [histo_category: {} ]: {}".format(addHistoName, type(rebin)))
            elif isinstance(projection, list) and isinstance(projection[0], str):
                pre_projection_name = retHists[sampleCat].GetName()
                if "ROOT.TH2" in str(type(retHists[sampleCat])):
                    retHists[sampleCat].SetName(pre_projection_name + "_preProjection")
                    if projection[0] == "X":
                        retHists[sampleCat] = retHists[sampleCat].ProjectionX(pre_projection_name, projection[1], projection[2])
                    elif projection[0] == "Y":
                        retHists[sampleCat] = retHists[sampleCat].ProjectionY(pre_projection_name, projection[1], projection[2])
                    else:
                        print("Error, {} is not a valid projection list for TH2".format(projection))
                elif "ROOT.TH3" in str(type(retHists[sampleCat])):
                    retHists[sampleCat].SetName(pre_projection_name + "_preProjection")
                    if projection[0] == "X":
                        retHists[sampleCat] = retHists[sampleCat].ProjectionX(pre_projection_name, projection[0], projection[1], 
                                                                  projection[2], projection[3], projection[4])
                    elif projection[0] == "Y":
                        retHists[sampleCat] = retHists[sampleCat].ProjectionY(pre_projection_name, projection[0], projection[1], 
                                                                  projection[2], projection[3], projection[4])
                    elif projection[0] == "Z":
                        retHists[sampleCat] = retHists[sampleCat].ProjectionZ(pre_projection_name, projection[0], projection[1], 
                                                                  projection[2], projection[3], projection[4])
                    else:
                        print("Error, {} is not a valid projection list for TH3".format(projection))
                else:
                    print("Error, projection not possible for input type in [histo_category: {} ]: {}".format(addHistoName, type(rebin)))

            #do profiling, akin to projection
            if profile == None:
                pass
            elif isinstance(profile, str):
                pre_profile_name = retHists[sampleCat].GetName()
                # if "ROOT.TH2" in str(type(retHists[sampleCat])):
                if isinstance(retHists[sampleCat], ROOT.TH2):
                    retHists[sampleCat].SetName(pre_profile_name + "_preProfile")
                    if profile == "X":
                        retHists[sampleCat] = retHists[sampleCat].ProfileX().ProjectionX(pre_profile_name)
                    elif profile == "Y":
                        retHists[sampleCat] = retHists[sampleCat].ProfileY().ProjectionX(pre_profile_name)
                    else:
                        print("Error, {} is not a valid profile axis for TH2".format(profile))
                # elif "ROOT.TH3" in str(type(retHists[sampleCat])):
                elif isinstance(retHists[sampleCat], ROOT.TH3):
                    raise NotImplementedError("profile option not implemented for TH3")
                else:
                    print("Error, projection not possible for input type in [histo_category: {} ]: {}".format(addHistoName, type(rebin)))

            #Zero templates that are below the threshold for entries
            if 0 < retHists[sampleCat].GetEntries() < zeroingThreshold and "data" not in sampleCat.lower():
                if systematic is None:
                    print("Zeroing template: {} ({} entries)".format(sampleCat, retHists[sampleCat].GetEntries()))
                retHists[sampleCat].Reset("ICESM") #Reset Integral, Contents, Errors, Statistics, Minimum/Maximum (I, C, E, S, M). Last 1 or 2 may be omitted if desired

            #execute rebinning based on type: int or list for variable width binning
            if rebin == None:
                pass
            elif isinstance(rebin, int):
                retHists[sampleCat].Rebin(rebin)
            elif isinstance(rebin, list):
                rebin_groups = len(rebin) - 1
                rebin_array = array.array('d', rebin)
                original_name = retHists[sampleCat].GetName()
                retHists[sampleCat].SetName(original_name + "_originalBinning")
                retHists[sampleCat] = retHists[sampleCat].Rebin(rebin_groups, original_name, rebin_array)
            else:
                print("Unsupported rebin input type in [histo_category: {} ]: {}".format(addHistoName, type(rebin)))
            if debug:
                print("the retHists for category '{}' is {}".format(cat, retHists))

            #Do differential counts, i.e. <Events / GeV> instead of Events / bin, using the scaling function optional parameter "width"
            if differentialScale:
                retHists[sampleCat].Scale(1.0, "width") #Scales contents and errors to the bin width

            #Set the axis ranges according to setRangeUser
            if setRangeUser:
                if len(setRangeUser) != 2:
                    raise ValueError("SetRangeUser must be a list or tuple with 2 values, floats equal to x-axis minimum and maximum in real units.")
                retHists[sampleCat].GetXaxis().SetRangeUser(setRangeUser[0], setRangeUser[1])

            #Modify the histogram with style and color information, where appropriate
            if isinstance(config["Color"], int): 
                thisFillColor = ROOT.TColor.GetColor(int(config["Color"]))
                thisLineColor = ROOT.TColor.GetColorDark(thisFillColor)
            elif isinstance(config["Color"], str): 
                thisFillColor = ROOT.TColor.GetColor(config["Color"])
                thisLineColor = ROOT.TColor.GetColorDark(thisFillColor)
            elif isinstance(config["Color"], list):
                thisFillColor = ROOT.TColor.GetColor(*config["Color"])
                thisLineColor = ROOT.TColor.GetColorDark(thisFillColor)
            else:
                raise ValueError("Unhandled process color encoding: type {}, value {}".format(type(config["Color"]), config["Color"]))
            if config["Style"] == "Fill":
                retHists[sampleCat].SetFillColor(thisFillColor)
                retHists[sampleCat].SetLineColor(thisLineColor)
                #hack for profiles...
                if profile in ["Y", "X"]:
                    retHists[sampleCat].SetMarkerStyle(config.get("MarkerStyle", 2))
                    retHists[sampleCat].SetMarkerSize(0.3)
                    retHists[sampleCat].SetMarkerColor(thisFillColor)
                    retHists[sampleCat].SetLineColor(thisLineColor)
            elif config["Style"] == "FillAlpha":
                retHists[sampleCat].SetFillColorAlpha(thisFillColor, config.get("Alpha", 0.5))
                retHists[sampleCat].SetLineColor(thisLineColor)
            elif config["Style"] == "Line":     
                # retHists[sampleCat].SetLineColor(config["Color"])
                retHists[sampleCat].SetFillColor(0)
                retHists[sampleCat].SetLineColor(thisFillColor)
                retHists[sampleCat].SetLineStyle(config.get("Hatch", 1))
            elif config["Style"] == "Marker":   
                retHists[sampleCat].SetMarkerStyle(config.get("MarkerStyle", 0))
                retHists[sampleCat].SetMarkerSize(0.5)
                retHists[sampleCat].SetMarkerColor(thisFillColor)
                retHists[sampleCat].SetLineColor(thisLineColor)
                # retHists[sampleCat].SetMarkerColor(config["Color"])
                # retHists[sampleCat].SetLineColor(config["Color"])
                #Styles kFullCircle (20), kFullSquare (21), kFullTriangleUp (22), kFullTriangleDown (23), kOpenCircle (24)
            else:
                pass
    #for hn, hh in retHists.items():
    #    ROOT.SetOwnership(hh,0)
    return retHists, theUnfound


def makeSuperCategories(histFile, histKeys, legendConfig, histNameCommon, systematic=None, nominalPostfix="nom", 
                        separator="___", orderByIntegral=True, orderReverse=False, rebin=None, setRangeUser=None, projection=None, 
                        profile=profile, verbose=False, debug=False, pn=None, doLogY=False, smoothing=0, 
                        normalizeToNominal=False, zeroingThreshold=50, differentialScale=False,
                        nominalCache=None,):
    """histFile is an open ROOT file containing histograms without subdirectories, legendConfig contains 'Categories'
    with key: value pairs of sample categories (like ttbar or Drell-Yan) and corresponding list of histogram sample names
    (like tt_SL, tt_SL-GF, tt_DL, etc.) that are subcomponents of the sample)
    The 'SuperCategories' in the configuration contains key: value pairs where the list then references the 'Categories'
    to be stacked together.
    However, category names should not include any _$SYSTEMATIC postfix; instead, it will be assumed to be appended to each histogram's category name,
    so the histograms made for each category will include the _$SYSTEMATIC variation if present, and the nominal if not."""
    retDict = {}
    
    #Prepare a counter so we know how many categories are actuallly filled, whatever the legendConfig has as default
    nFilledCategories = 0
    if systematic is None and pn == 0:
        #Get coordinates for the legend, create it, store the pointer in the dictionary (so it isn't deleted, to hammer the point over and over)
        coord = legendConfig.get("Coordinates")
        nColumns = legendConfig.get("nColumns")
        leg = ROOT.TLegend(coord[0], coord[1], coord[2], coord[3])
        leg.SetNColumns(nColumns)
        leg.SetBorderSize(0)
        leg.SetTextFont(43)
        leg.SetTextSize(20)
        leg.SetFillColorAlpha(0, 0) #Transparent
        if doLogY:
            #Plan to paint it in the leftmost pads, in the bulk of the histogram
            leg_top = 0.45
        else:
            #plan to paint it above the lower yield histograms of the rightmost pads
            leg_top = 0.7
        leg1_bottom = leg_top - 4 * 0.07 #4 = number of samples in this legend
        leg2_bottom = leg_top - 5 * 0.07 #5 = rest of stack + signal + data, usually
        leg_left = 0.1
        leg_right = 0.9
        leg1 = ROOT.TLegend(leg_left, leg1_bottom, leg_right, leg_top)
        leg1.SetBorderSize(0)
        leg1.SetTextFont(43)
        leg1.SetTextSize(20)
        leg1.SetFillColorAlpha(0, 0) #Transparent
        leg2 = ROOT.TLegend(leg_left, leg2_bottom, leg_right, leg_top)
        leg2.SetBorderSize(0)
        leg2.SetTextFont(43)
        leg2.SetTextSize(20)
        leg2.SetFillColorAlpha(0, 0) #Transparent
        #From other plotting scripts:
        # leg.SetFillStyle(0)
    
        #nColumns = math.floor(math.sqrt(len(legendConfig.get("Categories"))))
        # leg.SetNColumns(nColumns)
        # if debug:
        #     print("nColumns = {} generated from {}".format(nColumns, len(legendConfig.get("Categories"))))
        retDict["Legend"] = leg
        retDict["Legend1"] = leg1
        retDict["Legend2"] = leg2
    #Create dictionary to return one level up, calling makeCategoryHists to combine subsamples together 
    #and do color, style configuration for them. Pass through the rebin parameter
    filteredHistKeys = histKeys #[fkey for fkey in histKeys if histNameCommon in fkey]
    retDict["Categories/hists"], retDict["Categories/theUnfound"] = makeCategoryHists(histFile, filteredHistKeys, legendConfig, histNameCommon,
                                                                                      systematic=systematic, rebin=rebin, setRangeUser=setRangeUser, projection=projection,
                                                                                      profile=profile, nominalPostfix=nominalPostfix, separator=separator,
                                                                                      verbose=verbose, debug=debug, pn=pn, normalizeToNominal=normalizeToNominal, 
                                                                                      smoothing=smoothing, zeroingThreshold=zeroingThreshold, differentialScale=differentialScale)
    if debug:
        print("the retDict contains:")
        pprint.pprint(retDict["Categories/hists"])
    #Create an ordered list of tuples using either the integral of each category histogram or just the name (for consistency)
    orderingList = []
    if len(retDict["Categories/hists"].keys()) < 1:
        print("Failed to find any working keys in the makeSueprCategories method. Printing first 10 searched-for keys...")
        for cat_name, cat_dict in enumerate(retDict["Categories/theUnfound"].items()):
            print(cat_name)
            print(cat_dict)
    for cat_name, cat_hist in retDict["Categories/hists"].items():
        #Perform smoothing post-aggregation and rebinning, if requested
        if nominalCache is not None and isinstance(smoothing, int) and smoothing > 0:
            nominal_hist = nominalCache["Categories/hists"][cat_name]
            if isinstance(nominal_hist, (ROOT.TH1, ROOT.TH2, ROOT.TH3)) and isinstance(cat_hist, (ROOT.TH1, ROOT.TH2, ROOT.TH3)):
                if "data" in cat_name.lower():
                    continue
                cat_hist.Add(nominal_hist, -1)
                cat_hist.Smooth(smoothing, "")
                cat_hist.Add(nominal_hist, 1)
        orderingList.append((cat_hist.GetSumOfWeights(), cat_name, cat_hist, ))
    if orderByIntegral:
        orderingList.sort(key=lambda j: j[0], reverse=orderReverse)
    else:
        orderingList.sort(key=lambda j: j[1], reverse=orderReverse)
    #Create dictionary of supercategory items
    retDict["Supercategories"] = {}
    retDict["Supercategories/stats"] = {}
    retDict["Supercategories/hists"] = {} #This will be the last histogram in a stack, or the final added histogram in an unstacked Supercategory
    retDict["Supercategories/xAxis"] = {}
    retDict["Supercategories/yAxis"] = {}
    for super_cat_name, super_cat_list in legendConfig["Supercategories"].items():
        if verbose:
            print("Working on Supercategory '{}' with list {}".format(super_cat_name, super_cat_list))
        #seperate out the orderedLists into sublists which can be combined differently for stacked and unstacked types
        #superCategories["{}/list".format(super_cat_name)] = [tup for tup in orderingList if orderingList[1] in super_cat_list["Names"]]
        if verbose:
            print("the list of names to check in the supercategory: {}".format(super_cat_list["Names"]))
        tmpList = [tup for tup in orderingList if tup[1] in super_cat_list["Names"]]
        #Check that the list is non-empty, continue to next supercategory otherwise
        if len(tmpList) == 0:
            continue
        else:
            pass
        #branch based on whether to do stacking or another addition instead
        if debug:
            print("the value in the dictionary is: {}".format(super_cat_list["Stack"]))
            print(super_cat_list)
        if super_cat_list["Stack"] == True:
            retDict["Supercategories"][super_cat_name] = ROOT.THStack("s_{cat}{sep}{com}{sep}{spf}".format(cat=super_cat_name, 
                                                                                                           sep=separator, 
                                                                                                           com=histNameCommon,
                                                                                                           spf="" if systematic == None else systematic),
                                                                      ""
                                                                     )                
            for ntup, tup in enumerate(tmpList):
                if systematic is None and pn == 0:
                    legendCode = legendConfig["Categories"][tup[1]]["Style"]
                    if legendCode == "Fill" or legendCode == "FillAlpha":
                        legendCode = "F"
                    elif legendCode == "Line":
                        legendCode = "L"
                    else:
                        #Assume Marker style
                        legendCode = "P"
                    #Add the legend entry
                    if tup[1] not in [lx.GetLabel() for lx in leg.GetListOfPrimitives()]:
                        leg.AddEntry(tup[2], tup[1] + "(blind)" if "blind" in tup[2].GetName().lower() else tup[1], legendCode)
                    if (ntup % 2) == 0:
                        if tup[1] not in [lx.GetLabel() for lx in leg1.GetListOfPrimitives()]:
                            leg1.AddEntry(tup[2], tup[1] + "(blind)" if "blind" in tup[2].GetName().lower() else tup[1], legendCode)
                    else:
                        if tup[1] not in [lx.GetLabel() for lx in leg2.GetListOfPrimitives()]:
                            leg2.AddEntry(tup[2], tup[1] + "(blind)" if "blind" in tup[2].GetName().lower() else tup[1], legendCode)
                #Add the category histogram to the stack
                retDict["Supercategories"][super_cat_name].Add(tup[2])
            #Acquire the stats for the finished stack and store it in the dictionary, but we only half-prepare this, since the histogram must be 'drawn' before a stats object is created
            retDict["Supercategories/hists"][super_cat_name] = retDict["Supercategories"][super_cat_name].GetStack().Last()#.GetListOfFunctions().FindObject("stats")
        #Treat it as a super addition of histograms instead
        else:
            retDict["Supercategories"][super_cat_name] = addHists([tup[2] for tup in tmpList], 
                                                                  "s_{blind}{cat}{sep}{com}{sep}{sys}".format(cat=super_cat_name, 
                                                                                                              sep=separator,
                                                                                                              com=histNameCommon,
                                                                                                              sys="" if systematic == None else systematic,
                                                                                                              blind="BLIND" if len([tup[2].GetName() for tup in tmpList if "BLIND" in tup[2].GetName()]) > 0 else ""), 
                                                                  scaleArray = None)
            #We need the tuple, which one? Choose the last/most significant one...
            tup = tmpList[-1]
            if systematic is None and pn == 0:
                legendCode = legendConfig["Categories"][tup[1]]["Style"]
                if legendCode == "Fill" or legendCode == "FillAlpha":
                    legendCode = "F"
                elif legendCode == "Line":
                    legendCode = "L"
                else:
                    #Assume Marker style
                    legendCode = "P"
                #Add the legend entry, but instead of the tup[2] histogram, the overall added hist.
                legendLabel = tup[1] #+ " (partially/blind)" if any(["blind" in tup[2].GetName().lower() for tup in tmpList]) else tup[1]
                leg.AddEntry(retDict["Supercategories"][super_cat_name], legendLabel, legendCode)
                leg2.AddEntry(retDict["Supercategories"][super_cat_name], legendLabel, legendCode)
            retDict["Supercategories/hists"][super_cat_name] = retDict["Supercategories"][super_cat_name]#.GetListOfFunctions().FindObject("stats")
    #Modify the number of columns based on actual filled Categories
    nColumns = int(math.floor(math.sqrt(nFilledCategories)))
    return retDict

def makeStack_Prototype(histFile, histList=None, legendConfig=None, rootName=None, systematic=None, orderByIntegral=True):
    """histFile is an open ROOT file containing histograms without subdirectories, histList is a python list of the name of histograms to be stacked together,
    not including any _$SYSTEMATIC postfix; this latter part will be assumed to be appended to each histogram, and when the systematic option is used,
    this function will stack histograms that have _$SYSTEMATIC postfix; if such a histogram is not present, the nominal histogram without a _$SYSTEMATIC will
    be used.
    
    legendConfig should be a dictionary containing subgrouping, color, and style information about the samples to be loaded"""
    if histList == None and legendConfig == None:
        raise ValueError("makeStack has received no histList and no legendConfig to create a stack from...")
    elif histList == None:
        pass 
    #Check that the desired histograms is actually present in the root file, separating into category where systematic variation is present and fallback nominal
    hists_systematic_set = set([])
    if systematic != None:
        hists_systematic_set = set([inclusion for inclusion in histList for hist in histFile.GetListOfKeys() if "{}_{}".format(inclusion, systematic) == hist.GetName()])
    hists_nominal_set = set([inclusion for inclusion in histList for hist in histFile.GetListOfKeys() if inclusion == hist.GetName()])
    hists_nominal_set = hist_nominal - hists_systematic
    hists_systematic = ["{}_{}".format(inclusion, systematic) for inclusion in hists_systematic_set]
    hists_nominal = [inclusion for inclusion in hists_nominal_set]
    print(hists_systematic)
    print(hists_nominal)

@profile(output_file="function_profile.txt", sort_by="cumulative", lines_to_print=500, strip_dirs=True)
def loopPlottingJSON(inputJSON, era=None, channel=None, systematicCards=None, Cache=None, histogramDirectory = ".", batchOutput=False, closeFiles=True, 
                     analysisDirectory=None, tag=None, plotCard=None, drawSystematic=None, drawLegends=True, drawNormalized=False,
                     plotDir=None, pdfOutput=None, macroOutput=None, pngOutput=None, useCanvasMax=False,
                     combineOutput=None, combineInput=None, combineCards=False, combineInputList=None,
                     nominalPostfix="nom", separator="___", skipSystematics=None, verbose=False, 
                     debug=False, nDivisions=105, lumi="N/A", drawYields=False,
                     zeroingThreshold=0, differentialScale=False, histogramUncertainties=False, ratioUncertainties=False,
                     removeNegativeBins=True, orderReverse=False,
                     normalizeUncertainties=[],
                     unusedNormalizationUncertainties=[
                                           'OSDL_RunII_ttmuRFcorrelatedDown', 'OSDL_RunII_ttmuRFcorrelatedUp', 
                     ],
                     smootheUncertainties=[],
                     normalizeAllUncertaintiesForProcess=[],
):
    """Loop through a JSON encoded plotCard to draw plots based on root files containing histograms.
    Must pass a cache (python dictionary) to the function to prevent python from garbage collecting everything.
    
    This latter point could be fixed via SetDirectory(0) being called on relevant histograms and not creating python
    intermediate objects like xaxis=hist.GetXaxis(), but instead chaining accessors/methods a la
    hist.GetXaxis().SetTitle(hist.GetXaxis().GetTitle().replace("meh", "amazing"))"""
    
    #Disable drawing in batch mode
    if batchOutput is True:
        ROOT.gROOT.SetBatch()
        #Improve png resolution 
        ROOT.gStyle.SetImageScaling(4.0)
        
    #set default style, but we'll override nDivisions later based on how many canvases there are...
    setGStyle(nDivisions=nDivisions)
    
    # #Need the output directory to exist
    # if not os.path.isdir(histogramDirectory):
    #     os.makedirs(histogramDirectory)
    
    #Parse the config file into non-default legends, canvases, and plots; make a separate dictionary for the default legend, plot, and canvas which 
    # are the fallback for any options
    legends = dict([(i, j) for i, j in inputJSON.items() if j.get("Type") == "LegendConfig"])
    canvases = dict([(i, j) for i, j in inputJSON.items() if j.get("Type") == "CanvasConfig"])
    plots = dict([(i, j) for i, j in inputJSON.items() if j.get("Type") == "PlotConfig"])
    fileList = set([plot.get("Files") for plot in plots.values() if (type(plot.get("Files")) == str) and plot.get("Files") != None])
    fileDict = {}
    fileDictKeys = {}
    fileDictRawKeys = {}
    for fn in fileList:
        if fn == "NON-STRING FILES VALUE": continue
        fileToBeOpened = "{}/{}".format(histogramDirectory, fn)
        if not os.path.isfile(fileToBeOpened):
            raise RuntimeError("File does not exist: {}".format(fileToBeOpened))
        fileDict[fileToBeOpened] = ROOT.TFile.Open(fileToBeOpened, "read")
        fileDictRawKeys[fileToBeOpened] = fileDict[fileToBeOpened].GetListOfKeys()
        fileDictKeys[fileToBeOpened] = [kk.GetName() for kk in fileDictRawKeys[fileToBeOpened]]
                                        
    defaults = dict([(i, j) for i, j in inputJSON.items() if j.get("Type") in ["DefaultPlot", "DefaultCanvas", "DefaultLegend"]])

    #Save histograms for Combine
    combSystematics = {}
    combVariables = {}
    combCategories = {}
    combHistograms = {}

    #Cache everything, we don't want python garbage collecting our objects before we're done using them. 
    if Cache == None:
        Cache = {}
    #Loop through the canvases to create. These are the head configurations for making our plots. The Cache should be filled with CanvasConfigs (unique), 
    #because PlotConfigs may be reused!
    #Each CanvasConfig should point to a LegendConfig, which in turn configures how to organize the individual histograms for stacks and grouping
    #Each CanvasConfig also must point to a number of PlotConfigs, where a mountain range canvas of 3 categories would point to 3 PlotConfigs.
    #The PlotConfig itself has a field for the root file which contains all the sample/data subcategories for that individual histogram 
    # (for example, ttbar (single lepton), tttt, ttH, DY, data for the leading Muon_pt). 
    print("Looping through canvases")
    can_num = 0
    can_max = len(canvases.keys())
    for can_name, can_dict in sorted(canvases.items(), key=lambda x: x[0].split("_")[-1], reverse=False):
        can_num += 1
        CanCache = {} #shorter access to this canvas dictionary
        Cache[can_name] = CanCache
        
        #Acquire the details of this canvas, including the list of (sub)plots, the number of pixels, whether to include a ratio, etc.
        CanCache["subplots"] = can_dict.get("Plots")
        CanCache["sublabels"] = can_dict.get("Labels")
        canTitle = can_dict.get("Title", defaults["DefaultCanvas"].get("Title"))
        canCoordinates = can_dict.get("Coordinates", defaults["DefaultCanvas"].get("Coordinates"))
        canCoordinates = can_dict.get("Margins", defaults["DefaultCanvas"].get("Margins"))
        nXPads = len(CanCache["subplots"])
        xPixels=can_dict.get("XPixels", defaults["DefaultCanvas"].get("XPixels"))
        yPixels=can_dict.get("YPixels", defaults["DefaultCanvas"].get("YPixels"))
        xAxisTitle=can_dict.get("XAxisTitle", defaults["DefaultCanvas"].get("XAxisTitle"))
        yAxisTitle=can_dict.get("YAxisTitle", defaults["DefaultCanvas"].get("YAxisTitle"))
        doRatio=can_dict.get("DoRatio", defaults["DefaultCanvas"].get("DoRatio"))
        doMountainrange=can_dict.get("DoMountainrange", defaults["DefaultCanvas"].get("DoMountainrange"))
        doLogY=can_dict.get("doLogY", defaults["DefaultCanvas"].get("doLogY"))
        
        
        #Load the requested legendConfig, grabing the default if necessary
        #The legend, a name understating its importance, determines groupings of MC/data to merge, stack, draw,
        #create ratios of, and draw systematics for. Each 'Supercategory' defined here gets a legend entry,
        legendConfig = legends.get(can_dict.get("Legend", "FallbackToDefault"), defaults["DefaultLegend"])
        CanCache["ratioTitle"] = legendConfig.get("ratioTitle", "#frac{Data}{Simulation}")
        sysVariationsYaml, sysVariationCardDict = load_yaml_cards(systematicCards) if systematicCards is not None else ([], {})
        systematics = configure_template_systematics(sysVariationsYaml, era, channel, include_nominal=False) if len(sysVariationsYaml) > 0 else []
        systematicsDict = configure_template_systematics_dict(sysVariationsYaml, era, channel, include_nominal=False) if len(sysVariationsYaml) > 0 else []
        # print(" ".join(systematics))
        #Load the LegendConfig which denotes which samples to use, colors to assign, etc.
        
        #Call createCanvasPads with our Can(vas)Cache passed to it, which will be subsequently filled,
        #allowing us to toss the returned dictionary into a throwaway variable '_'
        print("Creating canvas pads")
        _ = createCanvasPads(can_name, CanCache, doRatio=doRatio, doMountainrange=doMountainrange, setXGrid=False, 
                             setYGrid=False, nXPads=nXPads, topFraction=0.7, bordersLRTB = canCoordinates, 
                             xPixels=xPixels, yPixels=yPixels)
        # nTheseDivisions = int(nDivisions/nXPads)
        CanCache["subplots/files"] = []
        CanCache["subplots/files/keys"] = []
        CanCache["subplots/supercategories"] = []
        CanCache["subplots/firstdrawn"] = []
        CanCache["subplots/supercategories/systematics"] = {}
        for syst in systematics:
            CanCache["subplots/supercategories/systematics"][syst] = []
        CanCache["subplots/ratios"] = []
        CanCache["subplots/channels"] = []
        CanCache["subplots/stats"] = []
        CanCache["subplots/rebins"] = []
        CanCache["subplots/draw_override"] = []
        CanCache["subplots/draw_extra"] = []
        CanCache["subplots/setrangeuser"] = []
        CanCache["subplots/projections"] = []
        CanCache["subplots/profiles"] = []
        CanCache["subplots/labels"] = []
        CanCache["subplots/maxima"] = []
        CanCache["subplots/minima"] = []
        CanCache["subplots/stringintegrals"] = []
        CanCache["subplots/integrals"] = []
        CanCache["subplots/integraltables"] = []
        
        
        #generate the header and label for the canvas, adding them in the cache as 'cms_label' and 'cms_header'
        header = can_dict.get("Header", legendConfig.get("Header", "{lumi} fb^{{-1}} (13 TeV)"))
        header_position = can_dict.get("HeaderPosition", legendConfig.get("HeaderPosition", 0.063))
        label = can_dict.get("Label", legendConfig.get("Label", "#bf{CMS} #it{Preliminary}"))
        label_position = can_dict.get("LabelPosition", legendConfig.get("LabelPosition", 0.05))        
        histDrawSystematicNom = []
        histDrawSystematicUp = []
        histDrawSystematicDown = []
        histDrawSystematicUpRatio = []
        histDrawSystematicDownRatio = []
        npValues = [] #npValues[padNumber][Supercategory][systematic, bin] stores the contents of each histogram of systematics, with a reverse lookup sD dictionary for mapping systematic name to number in the last array lookup
        npDifferences = []
        npMasks = []
        npAddInQuads = []
        npEnvelopes = []
        npNominal = [] # n-vector
        npBinCenters = [] # n-vector
        npXErrorsUp = []
        npXErrorsDown = []
        npStatErrorsUp = [] # n-vector
        npStatErrorsDown = [] # n-vector
        npSystematicErrorsUp = [] # n-vector
        npSystematicErrorsDown = [] # n-vector
        npStatSystematicErrorsUp = [] # n-vector
        npStatSystematicErrorsDown = [] # n-vector
        
        #Get the variables that will go into the plots, prefilter the histogram keys
        subplot_variables = [subplot_name.split(separator)[-1] for subplot_name in CanCache["subplots"]]
        subplot_categories = [subplot_name.split(separator)[0].replace("Plot_", "", 1).replace("blind_", "") for subplot_name in CanCache["subplots"]]
        if combineInputList and not any([x in combineInputList for x in subplot_variables]):
            print("Skipping",subplot_variables,"Since they're not in ",combineInputList)
            continue
        for pn, subplot_name in enumerate(CanCache["subplots"]):
            subplot_dict = plots["{}".format(subplot_name)]
            nice_name = subplot_name.replace("Plot_", "").replace("Plot", "").replace("blind_", "").replace("BLIND", "")
            print("Creating subplot {}".format(nice_name))
            #Append the filename to the list
            plotFileName = "{}/{}".format(histogramDirectory, subplot_dict["Files"])
            if plotFileName in fileDict:
                CanCache["subplots/files"].append(fileDict[plotFileName])
                # CanCache["subplots/files/keys"].append([fkey for fkey in fileDictKeys[plotFileName] if subplot_variables[pn] in fkey and fkey.split(separator)[-2] == subplot_variables[pn]])
                CanCache["subplots/files/keys"].append([fkey for fkey in fileDictKeys[plotFileName] if subplot_variables[pn] in fkey and subplot_categories[pn] in fkey])
                if len(CanCache["subplots/files/keys"][-1]) < 1:
                    raise RuntimeError("No matching keys found for subplot variables {} and categories {}, some available keys: {}"\
                                       .format(subplot_variables[pn], subplot_categories[pn], fileDictKeys[plotFileName][0:min(10, len(fileDictKeys[plotFileName]))]))
            else:
                raise RuntimeError("File not available, was it stored in a list or something?")
            CanCache["subplots/rebins"].append(subplot_dict.get("Rebin"))
            CanCache["subplots/draw_extra"].append(subplot_dict.get("Draw_extra", False))
            CanCache["subplots/draw_override"].append(subplot_dict.get("Draw", False))
            CanCache["subplots/setrangeuser"].append(subplot_dict.get("SetRangeUser", can_dict.get("SetRangeUser", None)))
            CanCache["subplots/projections"].append(subplot_dict.get("Projection"))
            CanCache["subplots/profiles"].append(subplot_dict.get("Profile", None))
            CanCache["subplots/stringintegrals"].append(collections.OrderedDict())
            CanCache["subplots/integrals"].append(collections.OrderedDict())
            #Call makeSuperCategories with the very same file [pn] referenced, plus the legendConfig
            # filteredHistKeys = [fkey for fkey in CanCache["subplots/files/keys"][pn] if fkey.split(separator)[-1] in ["$NOMINAL", "nom"]]
            CanCache["subplots/supercategories"].append(makeSuperCategories(CanCache["subplots/files"][pn], CanCache["subplots/files/keys"][pn], legendConfig, nice_name, 
                                                                            systematic=None, orderByIntegral=True, orderReverse=orderReverse, 
                                                                            rebin=CanCache["subplots/rebins"][pn], setRangeUser=CanCache["subplots/setrangeuser"][pn],
                                                                            projection=CanCache["subplots/projections"][pn], profile=CanCache["subplots/profiles"][pn],
                                                                            nominalPostfix=nominalPostfix, separator=separator, verbose=verbose, debug=False, pn=pn, doLogY=doLogY,
                                                                            normalizeToNominal=False, smoothing=0, zeroingThreshold=zeroingThreshold, 
                                                                            differentialScale=differentialScale)
            )
            #This is not sufficient for skipping undone histograms
            # if len(list(CanCache["subplots/supercategories"][pn]['Supercategories/hists'].values())) == 0:
            #     print("No histograms found for '{}', skipping".format(nice_name))
            #     continue
            print(" Done :: ", end="")
            blindSupercategories = [k for k in CanCache["subplots/supercategories"][pn]['Supercategories'] if "BLIND" in k]
            if len(blindSupercategories) > 0: print("Blinded - skipping systematics")
            nSystsEnd = len(systematics) - 1 if skipSystematics is None else len(systematics) - 1 - len(skipSystematics)
            if combineOutput is not None or (pdfOutput is not None and len(blindSupercategories) < 1):
                nSysts = len(systematics)
                print(" {} unskipped systematics: ".format(nSystsEnd + 1), end="")
                try:
                    nBins = list(CanCache["subplots/supercategories"][pn]['Supercategories/hists'].values())[0].GetNbinsX()
                except:
                    print("Failed to find any working key combinations...")
                    pdb.set_trace()
                sD = dict() #systematic dictionary for lookup into numpy array
                sD['statisticsUp'] = nSysts + 0
                sD['statisticsDown'] = nSysts + 1
                histDrawSystematicNom.append(dict())
                histDrawSystematicUp.append(dict())
                histDrawSystematicDown.append(dict())
                histDrawSystematicUpRatio.append(dict())
                histDrawSystematicDownRatio.append(dict())
                npValues.append(dict())
                npDifferences.append(dict())
                npMasks.append(dict())
                npAddInQuads.append(dict())
                npEnvelopes.append(dict())
                npNominal.append(dict())
                npBinCenters.append(dict())
                npXErrorsUp.append(dict())
                npXErrorsDown.append(dict())
                npStatErrorsUp.append(dict())
                npStatErrorsDown.append(dict())
                npSystematicErrorsUp.append(dict())
                npSystematicErrorsDown.append(dict())
                npStatSystematicErrorsUp.append(dict())
                npStatSystematicErrorsDown.append(dict())
                for supercategory, scHisto in CanCache["subplots/supercategories"][pn]['Supercategories/hists'].items():
                    # multiprocessing.Pool.map() may be faster... but it didn't work in my first test. list comprehension better if tupled up?
                    if "data" in supercategory.lower(): continue
                    histoArrays = [(scHisto.GetBinErrorLow(x), scHisto.GetBinErrorUp(x)) for x in range(nBins + 2)]
                    histDrawSystematicNom[pn][supercategory] = scHisto.Clone(scHisto.GetName() + "_drawSystematic_" + "nom")
                    npNominal[pn][supercategory], edgesTuple = wrapped_hist2array(scHisto, flow=True)
                    # npValues[pn][supercategory] = np.zeros((nSysts + 2, nBins + 2), dtype=float)
                    npValues[pn][supercategory] = npNominal[pn][supercategory].reshape((1,nBins+2)) * np.ones_like(1.0, shape=(nSysts + 2, nBins + 2), dtype=float)
                    #npAddInQuads, npEnvelopes, npMasks contains various arrays for only getting positive entries, negative entries
                    #systematic only, those which should be added in quadrature, enveloped...
                    npAddInQuads[pn][supercategory] = dict()
                    npEnvelopes[pn][supercategory] = dict()
                    npMasks[pn][supercategory] = dict()
                    npMasks[pn][supercategory]['R_Systematic'] = np.ones_like(True, shape=(nSysts + 2, nBins + 2), dtype=bool)  
                    npMasks[pn][supercategory]['R_Systematic'][nSysts+0:nSysts+2, :] = False #Set the two statistical dimensions to False
                    #Stat errors up and down Assumes positive return value, untrue for esoteric stat options?
                    #TGraphAsymmErrors constructor requires the number of points and ALL POSITIVE arrays for the x, y, xdown, xup, ydown, yup (latter 4 RELATIVE)
                    npStatErrorsDown[pn][supercategory] = np.asarray([bt[0] for bt in histoArrays], dtype=float)
                    npStatErrorsUp[pn][supercategory] = np.asarray([bt[1] for bt in histoArrays], dtype=float) 
                    binWidths = (edgesTuple[0][1:] - edgesTuple[0][:-1])
                    halfBinMin = np.min(binWidths)/2
                    npBinCenters[pn][supercategory] = np.append(np.insert(edgesTuple[0][:-1] + binWidths/2, 0, 
                                                                          edgesTuple[0][0] - halfBinMin), edgesTuple[0][-1] + halfBinMin)
                    npXErrorsUp[pn][supercategory] = np.append(np.insert(binWidths/2, 0, halfBinMin), halfBinMin)
                    npXErrorsDown[pn][supercategory] = np.append(np.insert(binWidths/2, 0, halfBinMin), halfBinMin)
                    npValues[pn][supercategory][nSysts + 0, :] = npNominal[pn][supercategory] + npStatErrorsUp[pn][supercategory]
                    npValues[pn][supercategory][nSysts + 1, :] = npNominal[pn][supercategory] - npStatErrorsDown[pn][supercategory]
                for category, catHisto in CanCache["subplots/supercategories"][pn]['Categories/hists'].items():
                    # multiprocessing.Pool.map() may be faster... but it didn't work in my first test. list comprehension better if tupled up?
                    if "data" in category.lower(): continue
                    histoArrays = [(catHisto.GetBinErrorLow(x), catHisto.GetBinErrorUp(x)) for x in range(nBins + 2)]
                    #### histDrawSystematicNom[pn][category] = catHisto.Clone(catHisto.GetName() + "_drawSystematic_" + "nom")
                    npNominal[pn][category], edgesTuple = wrapped_hist2array(catHisto, flow=True)
                    npValues[pn][category] = npNominal[pn][category].reshape((1,nBins+2)) * np.ones_like(1.0, shape=(nSysts + 2, nBins + 2), dtype=float)
                    npAddInQuads[pn][category] = dict()
                    npEnvelopes[pn][category] = dict()
                    npMasks[pn][category] = dict()
                    npMasks[pn][category]['R_Systematic'] = np.ones_like(True, shape=(nSysts + 2, nBins + 2), dtype=bool)  
                    npMasks[pn][category]['R_Systematic'][nSysts+0:nSysts+2, :] = False #Set the two statistical dimensions to False
                    npStatErrorsDown[pn][category] = np.asarray([bt[0] for bt in histoArrays], dtype=float)
                    npStatErrorsUp[pn][category] = np.asarray([bt[1] for bt in histoArrays], dtype=float) 
                    binWidths = (edgesTuple[0][1:] - edgesTuple[0][:-1])
                    halfBinMin = np.min(binWidths)/2
                    npBinCenters[pn][category] = np.append(np.insert(edgesTuple[0][:-1] + binWidths/2, 0, 
                                                                          edgesTuple[0][0] - halfBinMin), edgesTuple[0][-1] + halfBinMin)
                    npXErrorsUp[pn][category] = np.append(np.insert(binWidths/2, 0, halfBinMin), halfBinMin)
                    npXErrorsDown[pn][category] = np.append(np.insert(binWidths/2, 0, halfBinMin), halfBinMin)
                    npValues[pn][category][nSysts + 0, :] = npNominal[pn][category] + npStatErrorsUp[pn][category]
                    npValues[pn][category][nSysts + 1, :] = npNominal[pn][category] - npStatErrorsDown[pn][category]
                for nSyst, syst in enumerate(tqdm(sorted(sorted(systematics, key = lambda l: l[-2:] == "Up", reverse=True), 
                                                              key = lambda l: l.replace("Down", "").replace("Up", "")
                                                          ))):
                    # if nSyst < nSystsEnd:
                    #     print("*", end="")
                    # else:
                    #     print("*")
                    #prepare masks for creation of systematics added in quadrature, enveloped, and so on
                    addInQuadratureAs = systematicsDict[syst].get("addInQuadratureAs", False)
                    envelopeAs = systematicsDict[syst].get("envelopeAs", False)
                    if skipSystematics is not None:
                        if "all" in skipSystematics or "All" in skipSystematics or "ALL" in skipSystematics:
                            continue
                        if syst in skipSystematics: 
                            continue
                        if isinstance(addInQuadratureAs, str) and addInQuadratureAs in skipSystematics:
                            continue
                        if isinstance(envelopeAs, str) and envelopeAs in skipSystematics:
                            continue
                    sD[syst] = nSyst
                    normalizeToNominal = False
                    smoothing = 0
                    if syst in normalizeUncertainties:
                        normalizeToNominal = True
                    if syst in smootheUncertainties:
                        smoothing = 5
                    CanCache["subplots/supercategories/systematics"][syst].append(makeSuperCategories(CanCache["subplots/files"][pn], CanCache["subplots/files/keys"][pn], legendConfig, 
                                                                                                      nice_name,
                                                                                                      systematic=syst, orderByIntegral=True, 
                                                                                                      orderReverse=orderReverse,
                                                                                                      rebin=CanCache["subplots/rebins"][pn], 
                                                                                                      setRangeUser=CanCache["subplots/setrangeuser"][pn],
                                                                                                      projection=CanCache["subplots/projections"][pn], 
                                                                                                      profile=CanCache["subplots/profiles"][pn],
                                                                                                      nominalPostfix=nominalPostfix, separator=separator, verbose=verbose, 
                                                                                                      debug=False, pn=pn, doLogY=doLogY,
                                                                                                      normalizeToNominal=normalizeToNominal, smoothing=smoothing, 
                                                                                                      zeroingThreshold=zeroingThreshold, differentialScale=differentialScale,
                                                                                                      nominalCache=CanCache["subplots/supercategories"][-1],
                                                                                                  ))
                    #Prepare the histogram dictionaries for this house of cards, lets gooooo. Would it be better to rewrite this entire thing? without a doubt. No time!
                    if isinstance(addInQuadratureAs, str) and len(addInQuadratureAs) > 0:
                        if addInQuadratureAs + "Up" not in CanCache["subplots/supercategories/systematics"]:
                            CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Up"] = []
                            CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Down"] = []
                        CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Up"].append({'Supercategories/hists': dict(), 'Categories/hists': dict()})
                        CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Down"].append({'Supercategories/hists': dict(), 'Categories/hists': dict()})
                    if isinstance(envelopeAs, str) and len(envelopeAs) > 0:
                        if envelopeAs + "Up" not in CanCache["subplots/supercategories/systematics"]:
                            CanCache["subplots/supercategories/systematics"][envelopeAs + "Up"] = []
                            CanCache["subplots/supercategories/systematics"][envelopeAs + "Down"] = []
                        CanCache["subplots/supercategories/systematics"][envelopeAs + "Up"].append({'Supercategories/hists': dict(), 'Categories/hists': dict()})
                        CanCache["subplots/supercategories/systematics"][envelopeAs + "Down"].append({'Supercategories/hists': dict(), 'Categories/hists': dict()})
                    conglom_supercats = CanCache["subplots/supercategories/systematics"][syst][pn]['Supercategories/hists']
                    conglom_cats = CanCache["subplots/supercategories/systematics"][syst][pn]['Categories/hists']
                    conglomeration = list(conglom_supercats.items()) + list(conglom_cats.items())
                    for categoryorsupercategory, scHisto in conglomeration:
                        if "data" in categoryorsupercategory.lower(): continue
                        if addInQuadratureAs:
                            assert "$" not in addInQuadratureAs, "Unresolved symbol in addInQuadratureAs '{}' from '{}'".format(addInQuadratureAs, syst)
                            aIQA_SU = CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Up"][pn]['Supercategories/hists']
                            aIQA_SD = CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Down"][pn]['Supercategories/hists']
                            aIQA_CU = CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Up"][pn]['Categories/hists']
                            aIQA_CD = CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Down"][pn]['Categories/hists']
                            if addInQuadratureAs not in npAddInQuads[pn][categoryorsupercategory]:
                                npAddInQuads[pn][categoryorsupercategory][addInQuadratureAs] = np.full_like(None, False, shape=(nSysts + 2, nBins + 2), dtype=bool)
                            npAddInQuads[pn][categoryorsupercategory][addInQuadratureAs][nSyst, :] = True
                            if categoryorsupercategory in conglom_supercats:
                                if categoryorsupercategory not in aIQA_SU:
                                    aIQA_SU[categoryorsupercategory] = scHisto.Clone(separator.join(scHisto.GetName().split(separator)[:-1] + [addInQuadratureAs + "Up"]))
                                    aIQA_SU[categoryorsupercategory].Reset("ICESM")
                                if categoryorsupercategory not in aIQA_SD:
                                    aIQA_SD[categoryorsupercategory] = scHisto.Clone(separator.join(scHisto.GetName().split(separator)[:-1] + [addInQuadratureAs + "Down"]))
                                    aIQA_SD[categoryorsupercategory].Reset("ICESM")
                            if categoryorsupercategory in conglom_cats:
                                if categoryorsupercategory not in aIQA_CU:
                                    aIQA_CU[categoryorsupercategory] = scHisto.Clone(separator.join(scHisto.GetName().split(separator)[:-1] + [addInQuadratureAs + "Up"]))
                                    aIQA_CU[categoryorsupercategory].Reset("ICESM")
                                if categoryorsupercategory not in aIQA_CD:
                                    aIQA_CD[categoryorsupercategory] = scHisto.Clone(separator.join(scHisto.GetName().split(separator)[:-1] + [addInQuadratureAs + "Down"]))
                                    aIQA_CD[categoryorsupercategory].Reset("ICESM")
                        if envelopeAs:
                            assert "$" not in envelopeAs, "Unresolved symbol in envelopeAs '{}' from '{}'".format(envelopeAs, syst)
                            eA_SU = CanCache["subplots/supercategories/systematics"][envelopeAs + "Up"][pn]['Supercategories/hists']
                            eA_SD = CanCache["subplots/supercategories/systematics"][envelopeAs + "Down"][pn]['Supercategories/hists']
                            eA_CU = CanCache["subplots/supercategories/systematics"][envelopeAs + "Up"][pn]['Categories/hists']
                            eA_CD = CanCache["subplots/supercategories/systematics"][envelopeAs + "Down"][pn]['Categories/hists']
                            if envelopeAs not in npEnvelopes[pn][categoryorsupercategory]:
                                npEnvelopes[pn][categoryorsupercategory][envelopeAs] = np.full_like(None, False, shape=(nSysts + 2, nBins + 2), dtype=bool)
                            npEnvelopes[pn][categoryorsupercategory][envelopeAs][nSyst, :] = True
                            if categoryorsupercategory in conglom_supercats:
                                if categoryorsupercategory not in eA_SU:
                                    eA_SU[categoryorsupercategory] = scHisto.Clone(separator.join(scHisto.GetName().split(separator)[:-1] + [envelopeAs + "Up"]))
                                    eA_SU[categoryorsupercategory].Reset("ICESM")
                                if categoryorsupercategory not in eA_SD:
                                    eA_SD[categoryorsupercategory] = scHisto.Clone(separator.join(scHisto.GetName().split(separator)[:-1] + [envelopeAs + "Down"]))
                                    eA_SD[categoryorsupercategory].Reset("ICESM")
                            if categoryorsupercategory in conglom_cats:
                                if categoryorsupercategory not in eA_CU:
                                    eA_CU[categoryorsupercategory] = scHisto.Clone(separator.join(scHisto.GetName().split(separator)[:-1] + [envelopeAs + "Up"]))
                                    eA_CU[categoryorsupercategory].Reset("ICESM")
                                if categoryorsupercategory not in eA_CD:
                                    eA_CD[categoryorsupercategory] = scHisto.Clone(separator.join(scHisto.GetName().split(separator)[:-1] + [envelopeAs + "Down"]))
                                    eA_CD[categoryorsupercategory].Reset("ICESM")
                        npValues[pn][categoryorsupercategory][nSyst, :], _ = wrapped_hist2array(scHisto, flow=True)
                        if categoryorsupercategory in CanCache["subplots/supercategories/systematics"][syst][pn]['Supercategories/hists']:
                            if drawSystematic == syst.replace("Up", ""):
                                histDrawSystematicUp[pn][categoryorsupercategory] = scHisto.Clone(scHisto.GetName() + "_drawSystematic_" + syst)
                                histDrawSystematicUpRatio[pn][categoryorsupercategory] = scHisto.Clone(scHisto.GetName() + "_drawSystematicRatio_" + syst)
                                histDrawSystematicUpRatio[pn][categoryorsupercategory].Divide(histDrawSystematicNom[pn][categoryorsupercategory])
                                histDrawSystematicUp[pn][categoryorsupercategory].SetLineColor(ROOT.kGreen)
                                histDrawSystematicUp[pn][categoryorsupercategory].SetFillColor(0)
                                histDrawSystematicUp[pn][categoryorsupercategory].SetLineWidth(1)
                                histDrawSystematicUp[pn][categoryorsupercategory].SetLineStyle(1)
                                histDrawSystematicUpRatio[pn][categoryorsupercategory].SetLineColor(ROOT.kGreen)
                                histDrawSystematicUpRatio[pn][categoryorsupercategory].SetFillColor(0)
                                histDrawSystematicUpRatio[pn][categoryorsupercategory].SetLineWidth(1)
                                histDrawSystematicUpRatio[pn][categoryorsupercategory].SetLineStyle(1)
                            if drawSystematic == syst.replace("Down", ""):
                                histDrawSystematicDown[pn][categoryorsupercategory] = scHisto.Clone(scHisto.GetName() + "_drawSystematic_" + syst)
                                histDrawSystematicDownRatio[pn][categoryorsupercategory] = scHisto.Clone(scHisto.GetName() + "_drawSystematicRatio_" + syst)
                                histDrawSystematicDownRatio[pn][categoryorsupercategory].Divide(histDrawSystematicNom[pn][categoryorsupercategory])
                                histDrawSystematicDown[pn][categoryorsupercategory].SetLineColor(ROOT.kBlue)
                                histDrawSystematicDown[pn][categoryorsupercategory].SetFillColor(0)
                                histDrawSystematicDown[pn][categoryorsupercategory].SetLineWidth(1)
                                histDrawSystematicDown[pn][categoryorsupercategory].SetLineStyle(1)
                                histDrawSystematicDownRatio[pn][categoryorsupercategory].SetLineColor(ROOT.kBlue)
                                histDrawSystematicDownRatio[pn][categoryorsupercategory].SetFillColor(0)
                                histDrawSystematicDownRatio[pn][categoryorsupercategory].SetLineWidth(1)
                                histDrawSystematicDownRatio[pn][categoryorsupercategory].SetLineStyle(1)
                #Only calculate the differences once all values are populated for every systematic (and categoryorsupercategory, since it's nested one level deeper still)
                for categoryorsupercategory in npValues[pn].keys():
                    npDifferences[pn][categoryorsupercategory] = npValues[pn][categoryorsupercategory] - npNominal[pn][categoryorsupercategory]
                    npDifferences[pn][categoryorsupercategory][nSysts] = npStatErrorsUp[pn][categoryorsupercategory]
                    npDifferences[pn][categoryorsupercategory][nSysts+1] = - np.abs(npStatErrorsDown[pn][categoryorsupercategory])
                    try:
                        npMasks[pn][categoryorsupercategory]['R_UpVar'] = npDifferences[pn][categoryorsupercategory] >= 0
                        npMasks[pn][categoryorsupercategory]['R_DownVar'] = npDifferences[pn][categoryorsupercategory] < 0
                    except:
                        pdb.set_trace()
                    npSystematicErrorsUp[pn][categoryorsupercategory] = np.sqrt(np.sum(np.power(npDifferences[pn][categoryorsupercategory], 
                                                                                      2, 
                                                                                      out=np.zeros((nSysts + 2, nBins + 2), dtype=float),
                                                                                      where=npMasks[pn][categoryorsupercategory]['R_Systematic'] & 
                                                                                      npMasks[pn][categoryorsupercategory]['R_UpVar']), axis=0))
                    npSystematicErrorsDown[pn][categoryorsupercategory] = np.sqrt(np.sum(np.power(npDifferences[pn][categoryorsupercategory], 
                                                                                        2, 
                                                                                        out=np.zeros((nSysts + 2, nBins + 2), dtype=float),
                                                                                        where=npMasks[pn][categoryorsupercategory]['R_Systematic'] & 
                                                                                        npMasks[pn][categoryorsupercategory]['R_DownVar']), axis=0))
                    npStatSystematicErrorsUp[pn][categoryorsupercategory] = np.sqrt(np.sum(np.power(npDifferences[pn][categoryorsupercategory], 
                                                                                          2, 
                                                                                          out=np.zeros((nSysts + 2, nBins + 2), dtype=float),
                                                                                          where=npMasks[pn][categoryorsupercategory]['R_UpVar']), axis=0))
                    npStatSystematicErrorsDown[pn][categoryorsupercategory] = np.sqrt(np.sum(np.power(npDifferences[pn][categoryorsupercategory], 
                                                                                            2, 
                                                                                            out=np.zeros((nSysts + 2, nBins + 2), dtype=float),
                                                                                            where=npMasks[pn][categoryorsupercategory]['R_DownVar']), axis=0))
                    for addInQuadratureAs, mask in npAddInQuads[pn][categoryorsupercategory].items():
                        differenceUp = np.sqrt(np.sum(np.power(npDifferences[pn][categoryorsupercategory], 
                                                               2, 
                                                               out=np.zeros((nSysts + 2, nBins + 2), dtype=float),
                                                               where=npAddInQuads[pn][categoryorsupercategory][addInQuadratureAs] & 
                                                               npMasks[pn][categoryorsupercategory]['R_UpVar']), axis=0))
                        differenceDown = -np.sqrt(np.sum(np.power(npDifferences[pn][categoryorsupercategory], 
                                                                  2, 
                                                                  out=np.zeros((nSysts + 2, nBins + 2), dtype=float),
                                                                  where=npAddInQuads[pn][categoryorsupercategory][addInQuadratureAs] & 
                                                                  npMasks[pn][categoryorsupercategory]['R_DownVar']), axis=0))
                        histUp = None
                        if categoryorsupercategory in CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Up"][pn]['Supercategories/hists']:
                            histUp = CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Up"][pn]['Supercategories/hists'][categoryorsupercategory]
                        elif categoryorsupercategory in CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Up"][pn]['Categories/hists']:
                            histUp = CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Up"][pn]['Categories/hists'][categoryorsupercategory]
                        # pdb.set_trace()
                        # histUpTest = histUp.Clone() # TEST
                        # _, edgesTest = wrapped_hist2array(histUpTest, flow=True)
                        # edgesTest = np.asarray(edgesTest)
                        # binCentersTest = (edgesTest[1:] + edgesTest[:-1])/2
                        # histUpTest.FillN(len(differenceUp), binCentersTest, differenceUp + npNominal[pn][categoryorsupercategory])
                        # histUpTest.ResetStats()
                        _ = root_numpy.array2hist(differenceUp + npNominal[pn][categoryorsupercategory], histUp)
                        histUp.ResetStats()
                        histDown = None
                        if categoryorsupercategory in CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Down"][pn]['Supercategories/hists']:
                            histDown = CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Down"][pn]['Supercategories/hists'][categoryorsupercategory]
                        elif categoryorsupercategory in CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Down"][pn]['Categories/hists']:
                            histDown = CanCache["subplots/supercategories/systematics"][addInQuadratureAs + "Down"][pn]['Categories/hists'][categoryorsupercategory]
                        _ = root_numpy.array2hist(differenceDown + npNominal[pn][categoryorsupercategory], histDown)
                        histDown.ResetStats()
                    for envelopeAs, mask in npEnvelopes[pn][categoryorsupercategory].items():
                        differenceUp = np.max(npDifferences[pn][categoryorsupercategory], 
                                              initial=0.0,
                                              where=npEnvelopes[pn][categoryorsupercategory][envelopeAs] & 
                                              npMasks[pn][categoryorsupercategory]['R_UpVar'], 
                                              axis=0)
                        differenceDown = np.min(npDifferences[pn][categoryorsupercategory], 
                                                initial=0.0,
                                                where=npEnvelopes[pn][categoryorsupercategory][envelopeAs] & 
                                                npMasks[pn][categoryorsupercategory]['R_DownVar'],
                                                axis=0)
                        histUp = None
                        if categoryorsupercategory in CanCache["subplots/supercategories/systematics"][envelopeAs + "Up"][pn]['Supercategories/hists']:
                            histUp = CanCache["subplots/supercategories/systematics"][envelopeAs + "Up"][pn]['Supercategories/hists'][categoryorsupercategory]
                        elif categoryorsupercategory in CanCache["subplots/supercategories/systematics"][envelopeAs + "Up"][pn]['Categories/hists']:
                            histUp = CanCache["subplots/supercategories/systematics"][envelopeAs + "Up"][pn]['Categories/hists'][categoryorsupercategory]
                        _ = root_numpy.array2hist(differenceUp + npNominal[pn][categoryorsupercategory], histUp)
                        histUp.ResetStats()
                        histDown = None
                        if categoryorsupercategory in CanCache["subplots/supercategories/systematics"][envelopeAs + "Down"][pn]['Supercategories/hists']:
                            histDown = CanCache["subplots/supercategories/systematics"][envelopeAs + "Down"][pn]['Supercategories/hists'][categoryorsupercategory]
                        elif categoryorsupercategory in CanCache["subplots/supercategories/systematics"][envelopeAs + "Down"][pn]['Categories/hists']:
                            histDown = CanCache["subplots/supercategories/systematics"][envelopeAs + "Down"][pn]['Categories/hists'][categoryorsupercategory]
                        _ = root_numpy.array2hist(differenceDown + npNominal[pn][categoryorsupercategory], histDown)
                        histDown.ResetStats()
            CanCache["subplots/supercategories"][pn]['Supercategories/statErrors'] = dict()
            CanCache["subplots/supercategories"][pn]['Supercategories/statErrors/ratio'] = dict()
            CanCache["subplots/supercategories"][pn]['Supercategories/systematicErrors'] = dict()
            CanCache["subplots/supercategories"][pn]['Supercategories/systematicErrors/ratio'] = dict()
            CanCache["subplots/supercategories"][pn]['Supercategories/statSystematicErrors'] = dict()
            CanCache["subplots/supercategories"][pn]['Supercategories/statSystematicErrors/ratio'] = dict()
            for categoryorsupercategory in CanCache["subplots/supercategories"][pn]['Supercategories/hists']:
                if "data" in supercategory.lower(): continue
                #More hacks, because my time has been stolen...
                if categoryorsupercategory not in npDifferences[pn].keys():
                    continue
                if categoryorsupercategory not in CanCache["subplots/supercategories"][pn]['Supercategories/hists'].keys(): 
                    continue 
                supercategory = categoryorsupercategory #Explicitly note we only do supercategories now
                handle = CanCache["subplots/supercategories"][pn]
                #For fill stye, see https://root.cern.ch/doc/master/classTAttFill.html
                #Stat error
                handle['Supercategories/statErrors'][supercategory] = ROOT.TGraphAsymmErrors(nBins + 2, 
                                                                                             npBinCenters[pn][supercategory],
                                                                                             npNominal[pn][supercategory],
                                                                                             npXErrorsDown[pn][supercategory],
                                                                                             npXErrorsUp[pn][supercategory],
                                                                                             npStatErrorsDown[pn][supercategory],
                                                                                             npStatErrorsUp[pn][supercategory]
                                                                                         )
                handle['Supercategories/statErrors'][supercategory].SetName(handle['Supercategories'][supercategory].GetName().replace("s_", "statError_"))
                handle['Supercategories/statErrors'][supercategory].SetFillStyle(3245)
                handle['Supercategories/statErrors'][supercategory].SetFillColorAlpha(ROOT.kBlue, 0.5)
                handle['Supercategories/statErrors'][supercategory].SetLineColorAlpha(ROOT.kBlue, 0.5)
                handle['Supercategories/statErrors/ratio'][supercategory] = ROOT.TGraphAsymmErrors(nBins + 2, 
                                                                                                   npBinCenters[pn][supercategory],
                                                                                                   np.divide(npNominal[pn][supercategory],
                                                                                                             npNominal[pn][supercategory],
                                                                                                             out=np.zeros(nBins + 2),
                                                                                                             where=npNominal[pn][supercategory] != 0),
                                                                                                   npXErrorsDown[pn][supercategory],
                                                                                                   npXErrorsUp[pn][supercategory],
                                                                                                   np.divide(npStatErrorsDown[pn][supercategory],
                                                                                                             npNominal[pn][supercategory],
                                                                                                             out=np.zeros(nBins + 2),
                                                                                                             where=npNominal[pn][supercategory] != 0),
                                                                                                   np.divide(npStatErrorsUp[pn][supercategory],
                                                                                                             npNominal[pn][supercategory],
                                                                                                             out=np.zeros(nBins + 2),
                                                                                                             where=npNominal[pn][supercategory] != 0)
                                                                                         )
                handle['Supercategories/statErrors/ratio'][supercategory].SetName(
                    handle['Supercategories'][supercategory].GetName().replace("s_", "statErrorRatio_"))
                handle['Supercategories/statErrors/ratio'][supercategory].SetFillStyle(3245)
                handle['Supercategories/statErrors/ratio'][supercategory].SetFillColorAlpha(ROOT.kBlue, 0.5)
                handle['Supercategories/statErrors/ratio'][supercategory].SetLineColorAlpha(ROOT.kBlue, 0.5)
                #Syst error
                handle['Supercategories/systematicErrors'][supercategory] = ROOT.TGraphAsymmErrors(nBins + 2, 
                                                                                                   npBinCenters[pn][supercategory],
                                                                                                   npNominal[pn][supercategory],
                                                                                                   npXErrorsDown[pn][supercategory],
                                                                                                   npXErrorsUp[pn][supercategory],
                                                                                                   npSystematicErrorsDown[pn][supercategory],
                                                                                                   npSystematicErrorsUp[pn][supercategory]
                                                                                               )
                handle['Supercategories/systematicErrors'][supercategory].SetName(
                    handle['Supercategories'][supercategory].GetName().replace("s_", "systematicError_"))
                handle['Supercategories/systematicErrors'][supercategory].SetFillStyle(3154)
                handle['Supercategories/systematicErrors'][supercategory].SetFillColorAlpha(ROOT.kRed, 0.5)
                handle['Supercategories/systematicErrors'][supercategory].SetLineColorAlpha(ROOT.kRed, 0.5)
                handle['Supercategories/systematicErrors/ratio'][supercategory] = ROOT.TGraphAsymmErrors(nBins + 2, 
                                                                                                             npBinCenters[pn][supercategory],
                                                                                                             np.divide(npNominal[pn][supercategory],
                                                                                                                       npNominal[pn][supercategory],
                                                                                                                       out=np.zeros(nBins + 2),
                                                                                                                       where=npNominal[pn][supercategory] != 0
                                                                                                                   ),
                                                                                                             npXErrorsDown[pn][supercategory],
                                                                                                             npXErrorsUp[pn][supercategory],
                                                                                                             np.divide(npSystematicErrorsDown[pn][supercategory],
                                                                                                                       npNominal[pn][supercategory],
                                                                                                                       out=np.zeros(nBins + 2),
                                                                                                                       where=npNominal[pn][supercategory] != 0),
                                                                                                             np.divide(npSystematicErrorsUp[pn][supercategory],
                                                                                                                       npNominal[pn][supercategory],
                                                                                                                       out=np.zeros(nBins + 2),
                                                                                                                       where=npNominal[pn][supercategory] != 0)
                                                                                         )
                handle['Supercategories/systematicErrors/ratio'][supercategory].SetName(
                    handle['Supercategories'][supercategory].GetName().replace("s_", "systematicErrorRatio_"))
                handle['Supercategories/systematicErrors/ratio'][supercategory].SetFillStyle(3154)
                handle['Supercategories/systematicErrors/ratio'][supercategory].SetFillColorAlpha(ROOT.kRed, 0.5)
                handle['Supercategories/systematicErrors/ratio'][supercategory].SetLineColorAlpha(ROOT.kRed, 0.5)
                #Stat + Syst errors
                handle['Supercategories/statSystematicErrors'][supercategory] = ROOT.TGraphAsymmErrors(nBins + 2, 
                                                                                             npBinCenters[pn][supercategory],
                                                                                             npNominal[pn][supercategory],
                                                                                             npXErrorsDown[pn][supercategory],
                                                                                             npXErrorsUp[pn][supercategory],
                                                                                             npStatSystematicErrorsDown[pn][supercategory],
                                                                                             npStatSystematicErrorsUp[pn][supercategory]
                                                                                         )
                handle['Supercategories/statSystematicErrors'][supercategory].SetName(
                    handle['Supercategories'][supercategory].GetName().replace("s_", "statSystematicError_"))
                handle['Supercategories/statSystematicErrors'][supercategory].SetFillStyle(3144)
                handle['Supercategories/statSystematicErrors'][supercategory].SetFillColorAlpha(ROOT.kGray, 0.5)
                handle['Supercategories/statSystematicErrors'][supercategory].SetLineColorAlpha(ROOT.kGray, 0.5)
                handle['Supercategories/statSystematicErrors/ratio'][supercategory] = ROOT.TGraphAsymmErrors(nBins + 2, 
                                                                                                             npBinCenters[pn][supercategory],
                                                                                                             np.divide(npNominal[pn][supercategory],
                                                                                                                       npNominal[pn][supercategory],
                                                                                                                       out=np.zeros(nBins + 2),
                                                                                                                       where=npNominal[pn][supercategory] != 0
                                                                                                                   ),
                                                                                                             npXErrorsDown[pn][supercategory],
                                                                                                             npXErrorsUp[pn][supercategory],
                                                                                                             np.divide(npStatSystematicErrorsDown[pn][supercategory],
                                                                                                                       npNominal[pn][supercategory],
                                                                                                                       out=np.zeros(nBins + 2),
                                                                                                                       where=npNominal[pn][supercategory] != 0),
                                                                                                             np.divide(npStatSystematicErrorsUp[pn][supercategory],
                                                                                                                       npNominal[pn][supercategory],
                                                                                                                       out=np.zeros(nBins + 2),
                                                                                                                       where=npNominal[pn][supercategory] != 0)
                                                                                         )
                handle['Supercategories/statSystematicErrors/ratio'][supercategory].SetName(
                    handle['Supercategories'][supercategory].GetName().replace("s_", "statSystematicErrorRatio_"))
                handle['Supercategories/statSystematicErrors/ratio'][supercategory].SetFillStyle(3144)
                handle['Supercategories/statSystematicErrors/ratio'][supercategory].SetFillColorAlpha(ROOT.kGray, 0.5)
                handle['Supercategories/statSystematicErrors/ratio'][supercategory].SetLineColorAlpha(ROOT.kGray, 0.5)
                if "tttt" in supercategory.lower() or "signal" in supercategory.lower(): continue
                if pn == 0:
                    if ratioUncertainties:
                        if "stat err" not in [x.GetLabel() for x in CanCache["subplots/supercategories"][0]["Legend"].GetListOfPrimitives()]:
                            CanCache["subplots/supercategories"][0]["Legend"].AddEntry(handle['Supercategories/statErrors'][supercategory], "stat err", "F")
                            CanCache["subplots/supercategories"][0]["Legend1"].AddEntry(handle['Supercategories/statErrors'][supercategory], "stat err", "F")
                            CanCache["subplots/supercategories"][0]["Legend"].AddEntry(handle['Supercategories/statSystematicErrors'][supercategory], "stat+syst err", "F")
                            CanCache["subplots/supercategories"][0]["Legend2"].AddEntry(handle['Supercategories/statSystematicErrors'][supercategory], "stat+syst err", "F")
                    if histogramUncertainties:
                        if "syst err" not in [x.GetLabel() for x in CanCache["subplots/supercategories"][0]["Legend"].GetListOfPrimitives()]:
                            CanCache["subplots/supercategories"][0]["Legend"].AddEntry(handle['Supercategories/systematicErrors'][supercategory], "syst err", "F")
                            CanCache["subplots/supercategories"][0]["Legend2"].AddEntry(handle['Supercategories/systematicErrors'][supercategory], "syst err", "F")

            CanCache["canvas/upperPads"][pn].cd()
            if doLogY:
                CanCache["canvas/upperPads"][pn].SetLogy()
            if verbose:
                print("Unfound histograms(including fallbacks):")
                pprint.pprint(CanCache["subplots/supercategories"][pn]["Categories/theUnfound"])
            
            dn = 0
            rdn = 0
            #Get the maxima and minima, I don't care about efficiency anymore
            thisMax = 0
            thisMin = 10000 #inverted start
            for super_cat_name, drawable in sorted(CanCache["subplots/supercategories"][pn]["Supercategories"].items(), 
                                                   key=lambda x: legendConfig["Supercategories"][x[0]]["Stack"], reverse=True):
                #Blinding is done via the keyword "BLIND" insterted into the supercategory histogram name, propragated up from the addHists method, etc. 
                if "data" in super_cat_name.lower() and "blind" in drawable.GetName().lower() and subplot_dict.get("Unblind", False) == False:
                    thisStrIntegral = "(blind)"
                    thisIntegral = -9876.54321
                    pass
                else:
                    thisMax = max(thisMax, drawable.GetMaximum())
                    thisMin = min(thisMin, drawable.GetMinimum())
                    if isinstance(drawable, (ROOT.TH1)):
                        thisStrIntegral = str("{:4.3f}".format(drawable.Integral()))
                        thisIntegral = drawable.Integral()
                    elif isinstance(drawable, (ROOT.THStack)):
                        thisStrIntegral = str("{:4.3f}".format(drawable.GetStack().Last().Integral()))
                        thisIntegral = drawable.GetStack().Last().Integral()
                CanCache["subplots/stringintegrals"][pn][super_cat_name] = thisStrIntegral
                CanCache["subplots/integrals"][pn][super_cat_name] = thisIntegral

                #Find and store the maxima/minima for each histogram
            CanCache["subplots/maxima"].append(thisMax)
            CanCache["subplots/minima"].append(thisMin)
            

            # for drawVariation in ["complete"]:
            #Do nasty in-place sorting of the dictionary to get the Stacks drawn first, by getting the key from each key-value pair and getting the "Stack" field value,
            #from the legendConfig, recalling we need the key part of the tuple (tuple[0]) with a reverse to put the Stack == True items up front...
            for super_cat_name, drawable in sorted(CanCache["subplots/supercategories"][pn]["Supercategories"].items(), 
                                                   key=lambda x: legendConfig["Supercategories"][x[0]]["Stack"], reverse=True):
                #Don't draw blinded data...
                if "data" in super_cat_name.lower() and "blind" in drawable.GetName().lower() and subplot_dict.get("Unblind", False) == False:
                    if isinstance(drawable, ROOT.TH1):
                        drawable.Reset("ICESM")
                        # for binnumber in range(drawable.GetNbinsX()+2):
                        #     drawable.SetBinContent(binnumber, 0); drawable.SetBinError(binnumber, 0)
                    else: #handle TH2, graphs?
                        pass
                #Draw SAME if not the first item, using options present in legend configuration
                if isinstance(CanCache["subplots/draw_override"][pn], str):
                    draw_command = CanCache["subplots/draw_override"][pn]
                else:
                    draw_command = legendConfig["Supercategories"][super_cat_name]["Draw"]
                if isinstance(CanCache["subplots/draw_extra"][pn], str):
                    draw_command += " " + CanCache["subplots/draw_extra"][pn]
                if dn > 0:
                    draw_command += " SAME"
                #Append the drawable to a list for later modification of the maxima/minima... messy for deletion if that has to be done, though!
                else:
                    CanCache["subplots/firstdrawn"].append(drawable)
                if debug:
                    print("supercategory: {}    type: {}    command: {}".format(super_cat_name, type(drawable), draw_command))
                
                #Because these are stacks, don't bother with getting axes and setting titles, just choose whether
                #it needs both the x and y axes or just y axis (to avoid many x axis titles being drawn)
                # if pn == (len(CanCache["subplots"]) - 1):
                #     if xAxisTitle != None and yAxisTitle != None:
                #         drawable.SetTitle(";{};{}".format(xAxisTitle, yAxisTitle))
                #     elif xAxisTitle != None:
                #         drawable.SetTitle(";{};{}".format(xAxisTitle, ""))
                #     elif yAxisTitle != None:
                #         drawable.SetTitle(";{};{}".format("", yAxisTitle))
                #     else:
                #         drawable.SetTitle(";{};{}".format("", ""))
                # else:
                #     if yAxisTitle != None:
                #         drawable.SetTitle(";;{}".format(yAxisTitle))
                #     else:
                #         drawable.SetTitle(";;{}".format(""))

                #Give up on setting the titles here... draw them 'by hand'
                drawable.SetTitle(";;{}".format(""))

                # SetNdivisions
                # if not isinstance(drawable, ROOT.THStack):
                #     drawable.SetNdivisions(nTheseDivisions)

                #Set the color
                color_input = legendConfig["Supercategories"][super_cat_name].get("Color", None)
                if color_input is not None:
                    if isinstance(color_input, int): 
                        color = ROOT.TColor.GetColor(int(color_input))
                    elif isinstance(color_input, str): 
                        color = ROOT.TColor.GetColor(color_input)
                    elif isinstance(color_input, list):
                        color = ROOT.TColor.GetColor(*color_input)
                    else:
                        raise ValueError("Unhandled process color encoding: type {}, value {}".format(type(color_input), color_input))
                    if not isinstance(drawable, ROOT.THStack):
                        drawable.SetLineColor(color)
                        drawable.SetMarkerColor(color)

                #increment our counter
                if "data" in super_cat_name.lower() and "blind" in drawable.GetName().lower() and subplot_dict.get("Unblind", False) == False:
                    pass
                elif not isinstance(drawable, (ROOT.TH1, ROOT.TH2, ROOT.TH3, ROOT.TProfile, ROOT.THStack, ROOT.TGraph)):
                    pass
                else:
                    if drawNormalized and not isinstance(drawable, ROOT.THStack):
                        drawable.DrawNormalized(draw_command, max([float(ival) for ival in CanCache["subplots/integrals"][pn].values()]))
                    else:
                        drawable.Draw(draw_command)
                    if CanCache["subplots/setrangeuser"][pn]:
                        if len(CanCache["subplots/setrangeuser"][pn]) != 2:
                            raise ValueError("SetRangeUser must be a list or tuple with 2 values, floats equal to x-axis minimum and maximum in real units.")
                        drawable.GetXaxis().SetRangeUser(CanCache["subplots/setrangeuser"][pn][0], CanCache["subplots/setrangeuser"][pn][1])

                    dn += 1
                if histogramUncertainties:
                    # if "Supercategories/statErrors" in CanCache["subplots/supercategories"][pn].keys():
                    #     if super_cat_name not in ["Background"]: 
                    #         pass
                    #     else:
                    #         if isinstance(CanCache["subplots/supercategories"][pn]['Supercategories/statErrors'][super_cat_name], (ROOT.TGraphAsymmErrors)):
                    #             CanCache["subplots/supercategories"][pn]['Supercategories/statErrors'][super_cat_name].Draw("5") #2 does fill rectangle, 5 adds the line around it
                    # if "Supercategories/statSystematicErrors" in CanCache["subplots/supercategories"][pn].keys():
                    #     if super_cat_name not in ["Background"]: 
                    #         pass
                    #     else:
                    #         if isinstance(CanCache["subplots/supercategories"][pn]['Supercategories/statSystematicErrors'][super_cat_name], (ROOT.TGraphAsymmErrors)):
                    #             CanCache["subplots/supercategories"][pn]['Supercategories/statSystematicErrors'][super_cat_name].Draw("5")
                    if "Supercategories/systematicErrors" in CanCache["subplots/supercategories"][pn].keys():
                        if super_cat_name not in ["Background"]: 
                            pass
                        else:
                            if isinstance(CanCache["subplots/supercategories"][pn]['Supercategories/statSystematicErrors'][super_cat_name], (ROOT.TGraphAsymmErrors)):
                                CanCache["subplots/supercategories"][pn]['Supercategories/statSystematicErrors'][super_cat_name].Draw("5")
                if super_cat_name in histDrawSystematicDown[pn].keys():
                        histDrawSystematicDown[pn][super_cat_name].Draw("HIST SAME")
                if super_cat_name in histDrawSystematicUp[pn].keys():
                        histDrawSystematicUp[pn][super_cat_name].Draw("HIST SAME")
                #Eliminate bin labels if there's a ratio plot just below
                if doRatio and "SAME" not in draw_command:
                    for bin in range(get_number_of_labels(drawable)+1):
                    # for bin in range(get_number_of_labels(drawable)+1):
                        # TAxis::ChangeLabel ( Int_t  labNum = 0, Double_t  labAngle = -1., Double_t  labSize = -1.,
                        #                      Int_t  labAlign = -1, Int_t  labColor = -1, Int_t  labFont = -1, TString  labText = "" 
                        #                  ) 
                        drawable.GetXaxis().ChangeLabel(bin, -1, 0, -1, -1, -1, "")
            xLabelSize = int(yPixels/48)
            yLabelSize = int(yPixels/48)
            if pn == 0:
                # xLabelSize = 1.3
                offsetText = CanCache["canvas/marginL"]
            else:
                # xLabelSize = 2.0
                offsetText = 0
            #Legends are only created in the dictionary for pad 0, so do not lookup pn but [0]
            if drawLegends:
                #######fix legends after-the-fect
                nl_entries = [x for x in CanCache["subplots/supercategories"][0]["Legend"].GetListOfPrimitives()]
                nl_left = 0.1
                nl_right = 0.9
                if doLogY:
                    #Plan to paint it in the leftmost pads, in the bulk of the histogram
                    nl_top = 0.45
                else:
                    #plan to paint it above the lower yield histograms of the rightmost pads
                    nl_top = 0.7
                nl_bottom = nl_top - len(nl_entries) * 0.07 #4 = number of samples in this legend
                # newLegend = ROOT.TLegend(nl_left, nl_bottom, nl_right, nl_top)
                # for x in nl_entries:
                #     newLegend.AddEntry(x)
                temp = CanCache["subplots/supercategories"][0]["Legend"]

                # temp.SetX1(nl_left)
                # temp.SetX2(nl_right)
                # temp.SetY1(nl_bottom)
                # temp.SetY2(nl_top)

                # CanCache["subplots/supercategories"][0]["Legend"].SetX1NDC(nl_left)
                # CanCache["subplots/supercategories"][0]["Legend"].SetX1NDC(nl_right)
                #######
                
                
                if doLogY:
                    if nXPads == 1:
                        CanCache["subplots/supercategories"][0]["Legend"].Draw()
                    else:
                        if pn == 0:    
                            CanCache["subplots/supercategories"][0]["Legend2"].Draw()
                        elif pn == 1:
                            CanCache["subplots/supercategories"][0]["Legend1"].Draw()
                else:
                    if nXPads == 1:
                        CanCache["subplots/supercategories"][0]["Legend"].Draw()
                    else:
                        if pn == nXPads - 2:
                            CanCache["subplots/supercategories"][0]["Legend1"].Draw()
                        elif pn == nXPads - 1:
                            CanCache["subplots/supercategories"][0]["Legend2"].Draw()
                
            #Create the subpad label, to be drawn. Text stored in CanCache["sublabels"] which should be a list, possibly a list of tuples in the future
            CanCache["subplots/labels"].append(ROOT.TLatex())
            CanCache["subplots/labels"][-1].SetTextFont(43)
            CanCache["subplots/labels"][-1].SetTextSize(int(yPixels/50))
            CanCache["subplots/labels"][-1].DrawLatexNDC(0.10 + offsetText, 0.78, "{}".format(CanCache["sublabels"][pn]))

            #Draw the pad
            CanCache["canvas/upperPads"][pn].Draw()
            #Now do the ratio plots, if requested
            if doRatio:
                CanCache["canvas/lowerPads"][pn].cd()
                CanCache["canvas/lowerPads"][pn].SetGridy()
                CanCache["subplots/ratios"].append({})
                #Get the ratio min/max from the subplot dictionary, falling back to the default plot if there is none
                ratioYMin = subplot_dict.get("RatioYMin", defaults["DefaultPlot"].get("RatioYMin"))
                ratioYMax = subplot_dict.get("RatioYMax", defaults["DefaultPlot"].get("RatioYMax"))
                for aRatioName, aRatio in legendConfig.get("Ratios", defaults["DefaultLegend"].get("Ratios")).items():
                    #Create a key for each ratio that will get drawn in this pad, the information for which is contained in
                    #CanCache["subplots/ratios"][-1] <- -1 being last list element, i.e. for last pad created
                    CanCache["subplots/ratios"][-1][aRatioName] = {}
                    #Get the name of the 'numerator' Supercategory, then use that to grab the final histogram for it (not a THStack! use "Supercategories/hists" instead)
                    num = aRatio["Numerator"]
                    num_hist = CanCache["subplots/supercategories"][pn]["Supercategories/hists"].get(num)
                    den = aRatio["Denominator"]
                    den_hist = CanCache["subplots/supercategories"][pn]["Supercategories/hists"].get(den)
                    color_input = aRatio.get("Color", 1)
                    if isinstance(color_input, int): 
                        color = ROOT.TColor.GetColor(int(color_input))
                    elif isinstance(color_input, str): 
                        color = ROOT.TColor.GetColor(color_input)
                    elif isinstance(color_input, list):
                        color = ROOT.TColor.GetColor(*color_input)
                    else:
                        raise ValueError("Unhandled process color encoding: type {}, value {}".format(type(color_input), color_input))
                    style = aRatio.get("Style", None)
                    markerStyle = aRatio.get("MarkerStyle", 20)
                    alpha = aRatio.get("Alpha", 0.5)
                    isBlinded=False #flag for making empty ratio plot to still draw axes, etc.
                    if ("data" in num.lower() or "data" in den.lower()) and "blind" in subplot_name.lower() and subplot_dict.get("Unblind", False) == False:
                        if debug: print("Skipping blinded category with data")
                        isBlinded=True #set flag to create empty histo
                    #Fallback for not finding histogram in the keys, i.e. MC-only histograms with templated JSONs
                    if num_hist is None or den_hist is None:
                        isBlinded=True
                    #Give it the dictionary we just appended when creating the ratio and storing the axes/other root memory objects
                    # _ = createRatio(num_hist, den_hist, Cache = CanCache["subplots/ratios"][-1][aRatioName], ratioTitle = aRatioName, 
                    _ = createRatio(num_hist, den_hist, Cache = CanCache["subplots/ratios"][-1][aRatioName], ratioTitle = "", 
                                    ratioColor = color, ratioStyle = style, ratioMarkerStyle = markerStyle, ratioAlpha = alpha,
                                    yMin = ratioYMin, yMax = ratioYMax, isBlinded=isBlinded, xLabelSize=xLabelSize, yLabelSize=yLabelSize, nDivisions=nDivisions)
                    #ratio_draw_command = legendConfig["Supercategories"][num]["Draw"]
                    ratio_draw_command = aRatio.get("Draw", "PXE1")
                    if rdn > 0:
                        ratio_draw_command += " SAME"
                    if isinstance(CanCache["subplots/ratios"][-1][aRatioName]["ratio_hist"], (ROOT.TH1, ROOT.TH2, ROOT.TH3, ROOT.TProfile, ROOT.THStack, ROOT.TGraph)):
                        CanCache["subplots/ratios"][-1][aRatioName]["ratio_hist"].Draw(ratio_draw_command)
                    #Fix label sizes
                    # if "SAME" not in ratio_draw_command:
                    if True:
                        maxBins = get_number_of_labels(CanCache["subplots/ratios"][-1][aRatioName]["ratio_hist"])
                        # maxBins = CanCache["subplots/ratios"][-1][aRatioName]["ratio_hist"].GetXaxis().GetNbins()
                        for bin in range(maxBins+1):
                            # TAxis::ChangeLabel ( Int_t  labNum = 0, Double_t  labAngle = -1., Double_t  labSize = -1.,
                            #                      Int_t  labAlign = -1, Int_t  labColor = -1, Int_t  labFont = -1, TString  labText = "" 
                            #                  ) 
                            # CanCache["subplots/ratios"][-1][aRatioName]["ratio_hist"].GetXaxis().ChangeLabel(bin, -1, 0.08, -1, -1, -1, "")
                            # align = 10*HorizontalAlign + VerticalAlign
                            # For horizontal alignment the following convention applies:
                            # 1=left adjusted, 2=centered, 3=right adjusted
                                
                            # For vertical alignment the following convention applies:
                            # 1=bottom adjusted, 2=centered, 3=top adjusted
                            # if (bin < 2):
                            #     binAlign = 13
                            #     binAngle = 45
                            # elif (bin == maxBins):
                            #     binAlign = 31
                            #     binAngle = 45
                            # else:
                            #     binAlign = 31
                            #     binAngle = 45
                            binAngle = 0
                            binAlign = 11
                            CanCache["subplots/ratios"][-1][aRatioName]["ratio_hist"].GetXaxis().ChangeLabel(bin, binAngle, xLabelSize, binAlign, -1, 43, "")
                    #Draw ratio graph errors...
                    redraw = False
                    if ratioUncertainties:
                        if den in CanCache["subplots/supercategories"][pn]['Supercategories/statErrors/ratio'].keys():
                            scGraph = CanCache["subplots/supercategories"][pn]['Supercategories/statErrors/ratio'][den]
                            if isinstance(scGraph, (ROOT.TGraphAsymmErrors)):
                                scGraph.Draw("2") #2 does fill rectangle, 5 adds the line around it
                                redraw = True
                        if den in CanCache["subplots/supercategories"][pn]['Supercategories/systematicErrors/ratio'].keys():
                            scGraph = CanCache["subplots/supercategories"][pn]['Supercategories/systematicErrors/ratio'][den]
                            if isinstance(scGraph, (ROOT.TGraphAsymmErrors)):
                                scGraph.Draw("2")
                                redraw = True
                        # if den in CanCache["subplots/supercategories"][pn]['Supercategories/statSystematicErrors/ratio'].keys():
                        #     scGraph = CanCache["subplots/supercategories"][pn]['Supercategories/statSystematicErrors/ratio'][den]
                        #     if isinstance(scGraph, (ROOT.TGraphAsymmErrors)):
                        #         scGraph.Draw("2")
                        #         redraw = True
                    if redraw and isinstance(CanCache["subplots/ratios"][-1][aRatioName]["ratio_hist"], (ROOT.TH1, ROOT.TH2, ROOT.TH3, ROOT.TProfile, ROOT.THStack, ROOT.TGraph)):
                        CanCache["subplots/ratios"][-1][aRatioName]["ratio_hist"].Draw(ratio_draw_command + "SAME")
                        
                    if den in histDrawSystematicDownRatio[pn].keys():
                        histDrawSystematicDownRatio[pn][supercategory].Draw("HIST SAME")
                    if den in histDrawSystematicUpRatio[pn].keys():
                        histDrawSystematicUpRatio[pn][supercategory].Draw("HIST SAME")

                    #Set the x axis title if it's the last drawable item
                    # if pn == (nXPads - 1):
                    #     if xAxisTitle != None:
                    #         CanCache["subplots/ratios"][-1][aRatioName]["ratio_Xaxis"].SetTitle(xAxisTitle)
                    #increment our counter for ratios
                    rdn += 1
                #FIXME: better would be to make the Supercategory "blindable" instead of assuming 'data' is in the name

            if doRatio:
                #Draw the pad regardless, for consistency
                CanCache["canvas/lowerPads"][pn].Draw()
        #Return to the main canvas
        CanCache["canvas"].cd()
        #Fill in integrals for super categories, and set the minima/maxima per pad
        if drawYields:
            padWidth = (1.0 - CanCache["canvas/bordersL"] - CanCache["canvas/bordersR"])/nXPads
            drawPoint = CanCache["canvas/marginL"]*0.33
            for pn in range(len(CanCache["subplots/stringintegrals"])):
                tmp = ROOT.TLatex()
                tmp.SetTextSize(0.016)
                tmpString = "#splitline"
                for super_cat_name, str_integral in CanCache["subplots/stringintegrals"][pn].items():
                    if "data" in super_cat_name.lower(): continue
                    tmpString += "{" + "{} : {}".format(super_cat_name, str_integral) + "}"
                tmp.DrawLatexNDC(drawPoint, 0.02, tmpString)
                drawPoint += padWidth
            #Modify the vertical axes now that we have the first drawn object, and each maximum and minima.
        if doLogY:
            canvasMin = max(min(CanCache["subplots/minima"]), 10e-4)
            print("setting mimimum to: " + str(canvasMin))
        else:
            canvasMin = min(CanCache["subplots/minima"])
        if useCanvasMax:
            canvasMax = can_dict.get("canvasMax", 1.1 * max(CanCache["subplots/maxima"]))
        else:
            canvasMax = 1.1 * max(CanCache["subplots/maxima"])

        for pn, drawable in enumerate(CanCache["subplots/firstdrawn"]):
            drawable.SetMinimum(canvasMin)
            drawable.SetMaximum(canvasMax)
            CanCache["canvas/upperPads"][pn].Draw()

        #Disable default title and make our own
        #aligntment: leading digit for left/center/right alignment as 1 2 3, following digit for bottom center top alignment, i.e. 11 = left bottom, 32 = right center
        #https://root.cern.ch/root/html604/TAttText.html
        ROOT.gStyle.SetOptTitle(1);
        #CanCache["canvas_title"] = ROOT.TPaveLabel(.25,.95,.6,.99, canTitle,"trndc");
        canTitlePerc = 0.2

        CanCache["canvas_upper_yaxis"] = ROOT.TLatex()
        CanCache["canvas_upper_yaxis"].SetNDC(True)
        CanCache["canvas_upper_yaxis"].SetTextFont(43)
        CanCache["canvas_upper_yaxis"].SetTextSize(35)
        CanCache["canvas_upper_yaxis"].SetTextAlign(33)
        CanCache["canvas_upper_yaxis"].SetTextAngle(90)
        differentialTitle = "< "
        differentialTitle += str(yAxisTitle).replace("bin", "GeV") if "GeV" in str(xAxisTitle) else str(yAxisTitle)
        differentialTitle += " >"
        if doRatio:
            CanCache["canvas_upper_yaxis"].DrawLatexNDC(0.13*CanCache["canvas/marginL"], 1-0.550*CanCache["canvas/marginT"], 
                                                        differentialTitle if differentialScale else str(yAxisTitle))
        else:
            CanCache["canvas_upper_yaxis"].DrawLatexNDC(0.13*CanCache["canvas/marginL"], 1-1.00*CanCache["canvas/marginT"], 
                                                        differentialTitle if differentialScale else str(yAxisTitle))
        CanCache["canvas_upper_yaxis"].Draw()        

        if doRatio:
            CanCache["canvas_lower_yaxis"] = ROOT.TLatex()
            CanCache["canvas_lower_yaxis"].SetNDC(True)
            CanCache["canvas_lower_yaxis"].SetTextFont(43)
            CanCache["canvas_lower_yaxis"].SetTextSize(35)
            CanCache["canvas_lower_yaxis"].SetTextAlign(33)
            CanCache["canvas_lower_yaxis"].SetTextAngle(90)
            CanCache["canvas_lower_yaxis"].DrawLatexNDC(0.05*CanCache["canvas/marginL"], 0+1.0*CanCache["canvas/marginB"], str(CanCache["ratioTitle"]))
            CanCache["canvas_lower_yaxis"].Draw()        
            
        CanCache["canvas_xaxis"] = ROOT.TLatex()
        CanCache["canvas_xaxis"].SetNDC(True)
        CanCache["canvas_xaxis"].SetTextFont(43)
        CanCache["canvas_xaxis"].SetTextSize(35)
        CanCache["canvas_xaxis"].SetTextAlign(33)
        if nXPads > 1:
            if doRatio:
                CanCache["canvas_xaxis"].DrawLatexNDC(1 - 0.17*CanCache["canvas/marginR"], 0.20*CanCache["canvas/marginB"], str(xAxisTitle))
            else:
                CanCache["canvas_xaxis"].DrawLatexNDC(1 - 0.17*CanCache["canvas/marginR"], 0.15*CanCache["canvas/marginB"], str(xAxisTitle))
        else:
            if doRatio:
                CanCache["canvas_xaxis"].DrawLatexNDC(1 - 1.0*CanCache["canvas/marginR"], 0.22*CanCache["canvas/marginB"], str(xAxisTitle))
            else:
                CanCache["canvas_xaxis"].DrawLatexNDC(1 - 1.0*CanCache["canvas/marginR"], 0.22*CanCache["canvas/marginB"], str(xAxisTitle))
        CanCache["canvas_xaxis"].Draw()        

        CanCache["canvas_label"] = ROOT.TLatex()
        CanCache["canvas_label"].SetNDC(True)
        CanCache["canvas_label"].SetTextFont(43)
        CanCache["canvas_label"].SetTextSize(35)
        CanCache["canvas_label"].SetTextAlign(13)
        if nXPads > 1:
            CanCache["canvas_label"].DrawLatexNDC(0.33*CanCache["canvas/marginL"], 1-0.40*CanCache["canvas/marginT"], str(label))
        else:
            CanCache["canvas_label"].DrawLatexNDC(1.0*CanCache["canvas/marginL"], 1-0.40*CanCache["canvas/marginT"], str(label))
        CanCache["canvas_label"].Draw()

        CanCache["canvas_title"] = ROOT.TLatex()
        CanCache["canvas_title"].SetNDC(True)
        CanCache["canvas_title"].SetTextFont(43) #Includes precision 3, which locks text size so that it stops fucking scaling according to pad size
        CanCache["canvas_title"].SetTextSize(40)
        CanCache["canvas_title"].SetTextAlign(22)
        if nXPads > 1:
            CanCache["canvas_title"].DrawLatexNDC(0.5, 1-0.2*CanCache["canvas/marginT"], str(canTitle) + "[{}]".format(drawSystematic) if isinstance(drawSystematic, str) else str(canTitle))
        else:
            CanCache["canvas_title"].DrawLatexNDC(0.5, 1-0.2*CanCache["canvas/marginT"], str(canTitle) + "[{}]".format(drawSystematic) if isinstance(drawSystematic, str) else str(canTitle))
        CanCache["canvas_title"].Draw()

        CanCache["canvas_header"] = ROOT.TLatex()
        CanCache["canvas_header"].SetNDC(True)
        CanCache["canvas_header"].SetTextFont(43)
        CanCache["canvas_header"].SetTextSize(30)
        CanCache["canvas_header"].SetTextAlign(33) #Lumi and sqrt(s)
        if nXPads > 1:
            CanCache["canvas_header"].DrawLatexNDC(1.0-0.2*CanCache["canvas/marginR"], 1-0.40*CanCache["canvas/marginT"], str(header.format(lumi=lumi)))
        else:
            CanCache["canvas_header"].DrawLatexNDC(1.0-1.0*CanCache["canvas/marginR"], 1-0.40*CanCache["canvas/marginT"], str(header.format(lumi=lumi)))
        CanCache["canvas_header"].Draw()

        CanCache["canvas"].Draw()

        formattedCommonName = "$ADIR/Plots/$ERA/$CHANNEL/$PLOTCARD/$SYST/$CANVAS".replace("$ADIR", analysisDir)\
                                                                                 .replace("$TAG", tag)\
                                                                                 .replace("$ERA", era)\
                                                                                 .replace("$PLOTCARD", plotCard)\
                                                                                 .replace("$CHANNEL", channel)\
                                                                                 .replace("$SYST", "nominal" if drawSystematic is None else drawSystematic)

        formattedCollectionName = formattedCommonName.replace("$CANVAS", tag + "_" + plotCard).replace("//", "/")
        formattedCanvasName = formattedCommonName.replace("$CANVAS", can_name.replace("___", "_").replace("Canvas_", "")).replace("//", "/")
        formattedCanvasPath, _ = os.path.split(formattedCanvasName)
        if not os.path.isdir(formattedCanvasPath):
            os.makedirs(formattedCanvasPath)
        if pdfOutput:
            if can_num == 1 and can_num != can_max: #count from 1 since we increment at the beginning of the loop on this one
                #print(CanCache["canvas"])
                CanCache["canvas"].SaveAs("{}.pdf(".format(formattedCollectionName))
            elif can_num == can_max and can_num != 1:
                print("Closing {}".format(formattedCollectionName))
                CanCache["canvas"].SaveAs("{}.pdf)".format(formattedCollectionName))
            else:
                CanCache["canvas"].SaveAs("{}.pdf".format(formattedCollectionName))
            CanCache["canvas"].SaveAs("{}".format(formattedCanvasName + ".pdf"))
        if isinstance(drawSystematic, str):
            formattedCanvasName += "." + drawSystematic
        if macroOutput:
            CanCache["canvas"].SaveAs("{}".format(formattedCanvasName + ".C"))
        if pngOutput:
            CanCache["canvas"].SaveAs("{}".format(formattedCanvasName + ".png"))
        if pdfOutput or macroOutput or pngOutput:
            print("\tDrew {}".format(can_name))

        #Save histograms for Combine, this is a hacked first attempt, might be cleaner to create a dictionary of histograms with keys from the histogram name to avoid duplicates/cycle numbers in the root files.
        if combineOutput is not None:
            if "signalSensitive_HT" in can_name: continue
            # if "nBtag2p" in can_name: continue
            normalizationDict = {}
            for i in range(len(CanCache["subplots/supercategories"])):
                for preProcessName, hist in CanCache["subplots/supercategories"][i]['Categories/hists'].items():
                    processName = preProcessName.replace("BLIND", "").replace("Data", "data_obs")
                    if processName not in combSystematics:
                        combSystematics[processName] = []
                    if processName not in combVariables:
                        combVariables[processName] = []
                    if processName not in combCategories:
                        combCategories[processName] = []
                    if processName not in combHistograms:
                        combHistograms[processName] = []
                    combProcess, combCategory, combVariable, combSystematic = hist.GetName().split(separator)
                    if "_stack_" in combSystematic:
                        combSystematic = combSystematic.split("_stack_")[0]
                    for iName, oName in [("ttother", "ttnobb")]:
                        combProcess = combProcess.replace(iName, oName)
                    if combVariable not in combineInputList:
                        print("Not writing histograms for {} ({},{},{})".format(combVariable,combProcess,combCategory,combSystematic))
                        continue
                    combSystematics[processName].append(combSystematic)
                    #combProcess.replace("BLIND", "").replace("Data", "data_obs")
                    combVariables[processName].append(combVariable)
                    combCategories[processName].append(combCategory.replace("+", "p"))
                    histName = "___".join([combProcess.replace("BLIND", "").replace("Data", "data_obs"), 
                                           combCategory.replace("+", "p"), 
                                           combVariable, 
                                           combSystematic])
                    # if "BLIND" in combProcess:
                    #     print("Blinding histogram for Combine")
                    #     combHist = hist.Clone(hist.GetName().replace("Data", "data_obs").replace("+", "p").replace("BLIND", ""))
                    #     combHist.SetDirectory(0)
                    #     for combBin in range(combHist.GetNbinsX() + 2):
                    #         combHist.SetBinContent(combBin, 0); combHist.SetBinError(combBin, 0)
                    # else:
                    #     combHist = hist.Clone(histName)
                    combHist = hist.Clone(histName)
                    #Remove negative weight bins if the option is selected
                    normalizationDict[combHist.GetName()] = combHist.Integral()
                    if removeNegativeBins:
                        negativeBins = np.nonzero(wrapped_hist2array(hist, flow=True)[0] < 0)[0]
                        for bin in negativeBins:
                            combHist.SetBinContent(int(bin), 0)
                            combHist.SetBinError(int(bin), 0)
                        if abs(combHist.Integral()) > 0.00001:
                            combHist.Scale(normalizationDict[combHist.GetName()]/combHist.Integral())
                        #Reset normalization so that systematics that are shape-only will match.
                        normalizationDict[combHist.GetName()] = combHist.Integral()
                    combHistograms[processName].append(combHist)
            for syst in CanCache["subplots/supercategories/systematics"].keys():
                for i in range(len(CanCache["subplots/supercategories/systematics"][syst])):
                    for preProcessName, hist in CanCache["subplots/supercategories/systematics"][syst][i]['Categories/hists'].items():
                        processName = preProcessName.replace("BLIND", "").replace("Data", "data_obs")
                        if processName not in combSystematics:
                            combSystematics[processName] = []
                        if processName not in combVariables:
                            combVariables[processName] = []
                        if processName not in combCategories:
                            combCategories[processName] = []
                        if processName not in combHistograms:
                            combHistograms[processName] = []
                        combProcess, combCategory, combVariable, combSystematic = hist.GetName().split(separator)
                        #Fix stack appends to the systematic name
                        if "_stack_" in combSystematic:
                            combSystematic = combSystematic.split("_stack_")[0]
                        #Remap systematic names for decorrelation in Higgs Combine
                        #Decorrelated systematics: mu(Factorization/Renormalization) scale and ISR, FSR usually correlated (qcd vs ewk like ttbar vs singletop) unless
                        # " the analysis is too sensitive to off-shell effects" https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopSystematics#Factorization_and_renormalizatio
                        #Systematic renaming now occurs in the FTAnalyzer...
                        # if any([substr in combSystematic 
                        #         for substr in ["muRFcorrelatedDown", "muRFcorrelatedUp", "muRNomFDown", "muRNomFUp",
                        #                        "muFNomRDown", "muFNomRUp", "ISRDown", "ISRUp", "FSRDown", "FSRUp"]]):

                        #     if processName in  ["ttbb", "ttother", "ttnobb"]:
                        #         combSystematic = "tt" + combSystematic
                        #     elif processName in ["DY"]:
                        #         combSystematic = "ewk" + combSystematic
                        #     else:
                        #         combSystematic = processName + combSystematic
                        for iName, oName in [("ttother", "ttnobb")]:
                            combProcess = combProcess.replace(iName, oName)                            
                        combSystematics[processName].append(combSystematic)
                        combVariables[processName].append(combVariable)
                        combCategories[processName].append(combCategory.replace("+", "p"))
                        histName = "___".join([combProcess.replace("BLIND", "").replace("Data", "data_obs"), 
                                               combCategory.replace("+", "p"), 
                                               combVariable, 
                                               combSystematic])
                        combHist = hist.Clone(histName)
                        #Remove negative weight bins if the option is selected
                        systIntegral = combHist.Integral()
                        if removeNegativeBins:
                            negativeBins = np.nonzero(wrapped_hist2array(combHist, flow=True)[0] < 0)[0]
                            for bin in negativeBins:
                                combHist.SetBinContent(int(bin), 0)
                                combHist.SetBinError(int(bin), 0)
                        #Regardless if negative weight bins are removed, check if there is a normalization to do
                        if systIntegral > 0.00001:
                            if normalizeUncertainties is not None:
                                if combSystematic in normalizeUncertainties:
                                    normValue = normalizationDict.get(combHist.GetName().replace(combSystematic, "nom"), "FAILED TO FIND NORM VALUE")
                                    try:
                                        combHist.Scale(normValue/combHist.Integral())
                                    except:
                                        print(normValue, type(normValue))
                                #If we're not normalizing to the non-systematic, check if we still need to normalize to itself
                                elif removeNegativeBins:
                                    combHist.Scale(systIntegral/combHist.Integral())
                            #Check separately if we need to normalize to the version prior to negative bin removal, separate from the alternative path just above,
                            #to avoid double scaling calculations
                            elif removeNegativeBins:
                                combHist.Scale(systIntegral()/combHist.Integral())
                            if normalizeAllUncertaintiesForProcess is not None:
                                # print("Process in normalizeAllUncertaintiesForProcess: ({}, {}): {}".format(processName, normalizeAllUncertaintiesForProcess, processName in normalizeAllUncertaintiesForProcess))
                                if processName in normalizeAllUncertaintiesForProcess:
                                    normValue = normalizationDict.get(combHist.GetName().replace(combSystematic, "nom"), 
                                                                      combHist.GetName().replace(combSystematic, ""))
                                    combHist.Scale(normValue/combHist.Integral())
                        #No data histograms for systematic variations... 
                        if "Data" in combProcess: continue
                        combHistograms[processName].append(combHist)
    combHistogramsFinal = {}
    for processName in combSystematics.keys():
        combSystematics[processName] = list(set(combSystematics[processName]))
        combVariables[processName] = list(set(combVariables[processName]))
        combCategories[processName] = list(set(combCategories[processName]))
        combHistogramsFinal[processName] = dict([(h.GetName(), h) for h in combHistograms[processName]])
    if combineOutput is not None:
        for can_var in combineInputList:
            print("Opening file for combine input templates: {}".format(combineOutput))
            combFile = ROOT.TFile.Open(combineOutput.replace("$VAR", can_var), "recreate")
            combCounts = dict()
            print("Writing histograms to {}".format(combineOutput.replace("$VAR", can_var)))
            for processName, processDict in tqdm(combHistogramsFinal.items()):
                for histName, hist in processDict.items():
                    countsProc, countsHTandCategory, countsVar, countsSyst = histName.split("___")
                    # countsCategory = countsHTandCategory.replace("HT500_", "")
                    if countsVar == can_var:
                        if countsHTandCategory not in combCounts:
                            combCounts[countsHTandCategory] = dict()
                        if countsProc not in combCounts[countsHTandCategory]:
                            combCounts[countsHTandCategory][countsProc] = dict()
                        combCounts[countsHTandCategory][countsProc][countsSyst] = hist.Integral()
                        hist.Write()
            combFile.Close()
            print("Wrote file for combine input templates")
            if combineCards:
                with open(os.path.join(analysisDir, "Combine", "Counts_"+era+"_"+channel+"_"+can_var+".json"), "w") as countfile: 
                    countfile.write(json.dumps(combCounts, indent=4))
                write_combine_cards(os.path.join(analysisDir, "Combine"), era, channel, can_var, list(combCounts.keys()), template="TTTT_templateV19.txt", counts=combCounts)
                print("Wrote combine cards for {}".format(can_var))
        # cmd = "hadd -f {wdir}/{era}___Combined.root {ins}".format(wdir=writeDir, era=era, ins=" ".join(f)) 
        # # print(cmd)
        # spo = subprocess.Popen(args="{}".format(cmd), shell=True, executable="/bin/zsh", env=dict(os.environ))
        # spo.communicate()
    if closeFiles == True:
        for fo in fileDict.values():
            fo.Close()
        return "Files Closed"
    else:
        return Cache

#DrawFrame is TH1/THStack/TPad method to just draw the axes

# catsForSplitStitching={"nocat":[""]}
# varsForSplitStitching=['el_eta', 'GenHT', 'nGenJet', 'jet5_eta', 'mu_eta', 'jet1_pt', 
#                        'mu_pt', 'el_pt', 'HT', 'jet1_eta', 'jet5_pt', 'nGenLep', 'nJet']
# nSplit=generateJSON(modelPlotJSON_SPLITSTITCH, varsForSplitStitching, 
#                     categories_dict=catsForSplitStitching, name_format="Plot_diagnostic___{var}", 
#                     channel="")
# nSplit.update(defaultNoLegend)
# if False:
#     # with open("/eos/user/n/nmangane/analysis/Nominal_Zvtx/Diagnostics/NoChannel/plots.json", "w") as jo:
#     with open("/eos/user/n/nmangane/analysis/SplitProcessTest/Diagnostics/NoChannel/plots.json", "w") as jo:
#         jo.write(json.dumps(nSplit, indent=4))


# replacementLegend1=None
# replacementLegend2=None
# replacementLegend3=None
# replacementLegend4=None
# replacementLegend5=None
# resultsS_DL = None
# resultsMS_DL = None
# resultsRS_DL = None
# resultsS_SL = None
# resultsMS_SL = None
# resultsRS_SL = None
# # base="/eos/user/n/nmangane/analysis/Nominal_Zvtx/Diagnostics/NoChannel"
# base="/eos/user/n/nmangane/analysis/SplitProcessTest/Diagnostics/NoChannel"
# with open("{}/stitchedDL.json".format(base), "r") as jlegend1:
#     replacementLegend1 = copy.copy(json_load_byteified(jlegend1))
# with open("{}/multistitchedDL.json".format(base), "r") as jlegend2:
#     replacementLegend2 = copy.copy(json_load_byteified(jlegend2))
# # with open("{}/restitchedDL.json".format(base), "r") as jlegend3:
# #     replacementLegend3 = copy.copy(json_load_byteified(jlegend3))
# with open("{}/multistitchedSL.json".format(base), "r") as jlegend4:
#     replacementLegend4 = copy.copy(json_load_byteified(jlegend4))
# with open("{}/multistitchedSL.json".format(base), "r") as jlegend5:
#     replacementLegend5 = copy.copy(json_load_byteified(jlegend5))
# # with open("{}/restitchedSL.json".format(base), "r") as jlegend6:
# #     replacementLegend6 = copy.copy(json_load_byteified(jlegend6))
# with open("{}/plots.json".format(base), "r") as j1:
#     loadedJSON1 = json_load_byteified(j1)
#     loadedJSON2 = copy.copy(loadedJSON1)
#     loadedJSON3 = copy.copy(loadedJSON1)
#     loadedJSON4 = copy.copy(loadedJSON1)
#     loadedJSON5 = copy.copy(loadedJSON1)
#     loadedJSON6 = copy.copy(loadedJSON1)
#     loadedJSON1.update(replacementLegend1)
#     loadedJSON2.update(replacementLegend2)
#     # loadedJSON3.update(replacementLegend3)
#     loadedJSON4.update(replacementLegend4)
#     loadedJSON5.update(replacementLegend5)
#     # loadedJSON3.update(replacementLegend6)
#     #Plot results stitching unfiltered + filtered, using filtered sample exclusively in its phase space
#     # resultsS_SL = loopPlottingJSON(loadedJSON1, Cache=None, directory="{}".format(base), batchOutput=True, 
#     #                             pdfOutput="{}/stitchedDL.pdf".format(base), verbose=False, nominalPostfix=None)
#     #Plot results stitching unfiltered + filtered, using both nominal and filtered samples weighted proportional to their number of net simulated events (N_+ - N_-)
#     # resultsMS_SL= loopPlottingJSON(loadedJSON2, Cache=None, directory="{}".format(base), batchOutput=True,
#     #                            pdfOutput="{}/multistitchedDL.pdf".format(base), verbose=False, nominalPostfix=None)
#     #Plot results stitching unfiltered only back together, to ensure perfect agreement with the nominal sample when not split
#     # resultsRS_SL = loopPlottingJSON(loadedJSON3, Cache=None, directory="{}".format(base), batchOutput=True, 
#     #                             pdfOutput="{}/restitchedDL.pdf".format(base), verbose=False, nominalPostfix=None)
#     #Plot results stitching unfiltered + filtered, using filtered sample exclusively in its phase space
#     # resultsS_SL = loopPlottingJSON(loadedJSON4, Cache=None, directory="{}".format(base), batchOutput=True, 
#     #                             pdfOutput="{}/stitchedSL.pdf".format(base), verbose=False, nominalPostfix=None)
#     #Plot results stitching unfiltered + filtered, using both nominal and filtered samples weighted proportional to their number of net simulated events (N_+ - N_-)
#     # resultsMS_SL= loopPlottingJSON(loadedJSON5, Cache=None, directory="{}".format(base), batchOutput=True,
#     #                            pdfOutput="{}/multistitchedSL.pdf".format(base), verbose=False, nominalPostfix=None)



# new_test_dict = {"nJet_nBtag2":["HT500_ZWindowMET0Width0_nMediumDeepCSVB2_nJet4", "HT500_ZWindowMET0Width0_nMediumDeepCSVB2_nJet5", "HT500_ZWindowMET0Width0_nMediumDeepCSVB2_nJet6", "blind_HT500_ZWindowMET0Width0_nMediumDeepCSVB2_nJet7", "blind_HT500_ZWindowMET0Width0_nMediumDeepCSVB2_nJet8+"],
# }
# #newTestVars=["MET_pt", "MET_uncorr_pt", "MET_phi", "MET_uncorr_phi", "Jet_DeepCSVB_jet1", "MTofMETandEl", "MTofMETandMu", "MTofElandMu"]
# newVarsMu=['Muon_phi_LeadLep', 'Muon_pfRelIso03_all', 'Muon_pfRelIso04_all', 'Muon_pt', 'Muon_eta_LeadLep', 
#            'nLooseFTAMuon', 'Muon_InvMass', 'Muon_pt_SubleadLep', 'Muon_eta_SubleadLep', 
#            'Muon_pfRelIso03_chg', 'Muon_phi_SubleadLep', 'nTightFTAMuon', 
#            'nMediumFTAMuon', 'Muon_pt_LeadLep']
# newVarsEl=['nMediumFTAElectron', 'Electron_InvMass', 'Electron_eta_SubleadLep', 'nTightFTAElectron', 
#            'Electron_eta_LeadLep', 'Electron_phi_LeadLep', 'Electron_pt_SubleadLep', 'nLooseFTAElectron', 
#            'Electron_phi_SubleadLep', 'Electron_pt', 'Electron_pt_LeadLep', 'Electron_pfRelIso03_all', 
#            'Electron_pfRelIso03_chg']
# newVarsMET=['MTofMETandEl', 'MTofMETandMu', 'MET_phi', 'MET_uncorr_pt', 'Muon_InvMass_v_MET', 'MET_uncorr_phi', 
#             'MET_pt', 'Electron_InvMass_v_MET']
# newVarsJet=['Jet_phi_jet5', 'Jet_phi_jet4', 'Jet_phi_jet3', 'Jet_phi_jet2', 'Jet_phi_jet1', 'nJet_LooseDeepCSV', 'Jet_DeepCSVB_sortedjet3', 'nJet_TightDeepCSV', 
#             'Jet_DeepJetB_sortedjet1', 'Jet_DeepJetB_sortedjet3', 'Jet_DeepJetB_sortedjet2', 'Jet_DeepJetB_sortedjet5', 'Jet_DeepJetB_sortedjet4', 
#             'Jet_pt_jet3', 'Jet_pt_jet2', 'Jet_pt_jet1', 'Jet_pt_jet5', 'Jet_pt_jet4', 'Jet_DeepCSVB_jet1', 'Jet_DeepCSVB_jet3', 'Jet_DeepCSVB_jet2', 
#             'Jet_DeepCSVB_jet5', 'Jet_DeepCSVB_jet4', 'Jet_eta_jet1', 'Jet_eta_jet2', 'Jet_eta_jet3', 'Jet_eta_jet4', 'Jet_eta_jet5', 
#             'Jet_DeepCSVB_sortedjet4', 'Jet_DeepCSVB_sortedjet5', 'Jet_DeepCSVB_sortedjet1', 'Jet_DeepCSVB_sortedjet2', 'Jet_DeepJetB_jet4', 
#             'Jet_DeepJetB_jet5', 'Jet_DeepJetB_jet1', 'Jet_DeepJetB_jet2', 'Jet_DeepJetB_jet3', 'nJet', 'nJet_MediumDeepCSV']
# newVarsEvent=["HT", "H", "HT2M", "H2M", "HTb", "HTH", "HTRat", "dRbb", "dPhibb", "dEtabb"]

# nMu = generateJSON(modelPlotJSON_CAT, newVarsMu, categories_dict=new_test_dict, channel="ElMu")
# nEl = generateJSON(modelPlotJSON_CAT, newVarsEl, categories_dict=new_test_dict, channel="ElMu")
# nMET = generateJSON(modelPlotJSON_CAT, newVarsMET, categories_dict=new_test_dict, channel="ElMu")
# nJet = generateJSON(modelPlotJSON_CAT, newVarsJet, categories_dict=new_test_dict, channel="ElMu")
# nEvent = generateJSON(modelPlotJSON_CAT, newVarsEvent, categories_dict=new_test_dict, channel="ElMu")
# nMu.update(defaultAndLegends)
# nEl.update(defaultAndLegends)
# nMET.update(defaultAndLegends)
# nJet.update(defaultAndLegends)
# nEvent.update(defaultAndLegends)
# # folder="/eos/user/n/nmangane/analysis/Apr-22-2020/Histograms/ElMu"
# # folder="/eos/user/n/nmangane/analysis/SplitProcessTest/Diagnostics/All"
# folder="/eos/user/n/nmangane/analysis/July2/Histograms"
# if False:
#     with open("{}/newMu.json".format(folder), "w") as jo:
#         jo.write(json.dumps(nMu, indent=4))
#     with open("{}/newEl.json".format(folder), "w") as jo:
#         jo.write(json.dumps(nEl, indent=4))
#     with open("{}/newMET.json".format(folder), "w") as jo:
#         jo.write(json.dumps(nMET, indent=4))
#     with open("{}/newJet.json".format(folder), "w") as jo:
#         jo.write(json.dumps(nJet, indent=4))
#     with open("{}/newEvent.json".format(folder), "w") as jo:
#         jo.write(json.dumps(nEvent, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for plotting FourTop analysis histograms in mountain-ranges, using configuration (json) cards')
    parser.add_argument('stage', action='store', type=str, choices=['generate-plotCard', 'generate-legendCard', 'plot-histograms', 'plot-diagnostics',
                                                                    'prepare-combine'],
                        help='plotting stage to be produced')
    parser.add_argument('--relUncertainty', dest='relUncertainty', action='store', type=float, default=0.3,
                        help='maximum relative uncertainty (sqrt(N)/N) per bin used as the criteria for merging, should be on unweighted histograms')
    parser.add_argument('-c', '--channel', dest='channel', action='store', type=str, default="ElMu", choices=['ElMu', 'ElEl', 'MuMu', 'ElEl_LowMET', 
                                                                                                              'ElEl_HighMET', 'MuMu_ElMu','MuMu_ElMu_ElEl', 
                                                                                                              'All', 'Merged', 'DL', 'SL', 'AH', 'SameFlavor'],
                        help='Decay channel for opposite-sign dilepton analysis')
    parser.add_argument('--systematics_cards', dest='systematics_cards', action='store', nargs='*', type=str,
                        help='path and name of the systematics card(s) to be used')
    parser.add_argument('-ci', '--combineInputList', dest='combineInputList', action='store', type=str, nargs='*', default=None,
                        help='Variable to be used as input to Higgs Combine. If None, output histograms will not be produced')
    parser.add_argument('--combineCards', dest='combineCards', action='store_true',
                        help='If --combineInputList is active as well, write out combine card templates')
    parser.add_argument('-d', '--analysisDirectory', dest='analysisDirectory', action='store', type=str, default="/eos/user/$U/$USER/analysis/$DATE",
                        help='analysis directory where btagging yields, histograms, etc. are stored')
    parser.add_argument('-f', '--formats', dest='formats', action='store', choices=['pdf', 'C', 'png'], nargs="*",
                        help='Formats to save plots as, supporting subset of ROOT SaveAs() formats: pdf, C macro, png')
    parser.add_argument('--json', '-p', '--plotCard', dest='plotCard', action='store', type=str, default="$ADIR/Histograms/All/plots.json",
                        help='input plotting configuration, defaulting to "$ADIR/Histograms/All/plots.json"')
    parser.add_argument('-l', '--legendCard', dest='legendCard', action='store', type=str, default="$ADIR/Histograms/All/legend.json",
                        help='input legend configuration, defaulting to "$ADIR/Histograms/All/legend.json". This card controls the grouping of histograms into categories and supercategories, colors, stacking, sample-scaling, etc.')
    parser.add_argument('--era', dest='era', type=str, default="NOERA", choices=["2017", "2018", "RunII"],
                        help='era for plotting, lumi, systematics deduction')
    parser.add_argument('--vars', '--variables', dest='variables', action='store', default=None, type=str, nargs='*',
                        help='List of variables for generating a plotCard')
    parser.add_argument('--nJets', '--nJetCategories', dest='nJetCategories', action='store', default=None, type=str, nargs='*',
                        help='List of nJet categories for generating a plotCard, i.e. "nJet4 nJet5 nJet6p"')
    parser.add_argument('--nBTags', '--nBTagCategories', dest='nBTagCategories', action='store', default=None, type=str, nargs='*',
                        help='List of nBTag categories for generating a plotCard, i.e. "nMediumDeepJetB2 nMediumDeepJetB3 nMediumDeepJetB4p"')
    parser.add_argument('--noBatch', dest='noBatch', action='store_true',
                        help='Disable batch output and attempt to draw histograms to display')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')
    parser.add_argument('--useCanvasMax', dest='useCanvasMax', action='store_true',
                        help='use the Canvas card\'s maximum rather than 110% of the subplots\' maxima')
    parser.add_argument('--skipSystematics', '--skipSystematics', dest='skipSystematics', action='store', 
                        default=None, type=str, nargs='*',
                        help='List of systematics to skip')
    parser.add_argument('--drawSystematic', dest='drawSystematic', action='store', default=None, type=str,
                        help='Single systematic name to be drawn on plots, besides the total statistical and systematic + statistical errors')
    parser.add_argument('--nominalPostfix', dest='nominalPostfix', action='store', default="nom", type=str,
                        help='name of the nominal systematic, default "nom"')
    parser.add_argument('--zeroingThreshold', dest='zeroingThreshold', action='store', type=int, default=50,
                        help='Threshold for Entries in grouped histograms, below which the contents will be reset. To disable, set equal or less than 0')
    parser.add_argument('--differentialScale', dest='differentialScale', action='store_true',
                        help='For variable width binning, set the bin errors and contents equal to the average over the bin width. Not compatible with --combineInputList option')
    parser.add_argument('--noHistogramUncertainties', dest='histogramUncertainties', action='store_false',
                        help='For drawing the MC stat + systematic uncertainties on the main histogram plot')
    parser.add_argument('--noRatioUncertainties', dest='ratioUncertainties', action='store_false',
                        help='For drawing the MC stat + systematic uncertainties on the ratio plot')
    parser.add_argument('--disableLegends', dest='drawLegends', action='store_false',
                        help='Disable the drawing of legends.')
    parser.add_argument('--orderReverse', dest='orderReverse', action='store_true',
                        help='For reversing the order of samples in the THStacks')
    parser.add_argument('--forceIntegerBinning', dest='forceBinning', action='store', type=int,
                        help='int or list to force rebinning on histograms')
    parser.add_argument('--forceArrayBinning', dest='forceBinning', action='store', type=list, nargs='*',
                        help='int or list to force rebinning on histograms')
    parser.add_argument('--forceLogY', dest='forceLogY', action='store_true',
                        help='Force LogY axis plotting')
    parser.add_argument('--forceWIP', dest='forceWIP', action='store_true',
                        help='Force Work In Progress header on plots')
    parser.add_argument('--noSmoothing', dest='noSmoothing', action='store_true',
                        help='Disable smoothing of systematics')
    parser.add_argument('--unblind', dest='unblind', action='store_true',
                        help='force unblinding of histograms')
    parser.add_argument('--drawNormalized', dest='drawNormalized', action='store_true',
                        help='use DrawNormalized for plotting')
    

    #Parse the arguments
    args = parser.parse_args()
    #Get the username and today's date for default directory:
    uname = pwd.getpwuid(os.getuid()).pw_name
    uinitial = uname[0]
    dateToday = datetime.date.today().strftime("%b-%d-%Y")
    stage = args.stage
    channel = args.channel
    combineInputList = args.combineInputList
    combineCards = args.combineCards
    era = args.era
    variables = args.variables
    nJets = args.nJetCategories
    nBTags = args.nBTagCategories
    doBatch = not args.noBatch
    verb = args.verbose
    useCanvasMax = args.useCanvasMax
    analysisDir = args.analysisDirectory.replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday).replace("$CHANNEL", channel)
    skipSystematics = args.skipSystematics
    zeroingThreshold=args.zeroingThreshold
    differentialScale = False
    if combineInputList is None:
        differentialScale=args.differentialScale
    elif args.differentialScale:
        print("differentialScale will set bin contents to the average over the bin width. This is not compatible with the combineInputList option, as the templates will no longer be absolute in scale. Disabled")

    lumiDict = {"2016": {"non-UL": 36.33,
                         "UL": 36.33},
                "2017": {"non-UL": 41.53,
                         "UL": 41.48},
                "2018": {"non-UL": 59.74,
                         "UL": 59.83},
                "RunII": {"non-UL": 101.2, 
                          "UL": -999999999999999999.9}
                # "RunII": {"non-UL": 137.60,
                #           "UL": 137.65}
            }
    lumi = lumiDict.get(era, "N/A").get("non-UL", "N/A")
if stage == 'plot-histograms' or stage == 'plot-diagnostics' or stage == 'prepare-combine':    
    plotConfig = args.plotCard.replace("$ADIR", analysisDir).replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday).replace("$CHANNEL", channel).replace("$ERA", era).replace("//", "/")
    legendConfig = args.legendCard.replace("$ADIR", analysisDir).replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday).replace("$CHANNEL", channel).replace("$ERA", era).replace("//", "/")
    tag = analysisDir.split("/")[-1]
    plotCardName = plotConfig.split("/")[-1]
    plotCard = plotCardName.replace(".json", "")
    legendCardName = legendConfig.split("/")[-1]
    legendcard = legendCardName.replace(".json", "")
    nominalPostfix = args.nominalPostfix

    if os.path.isdir(analysisDir):
        jsonDir = "$ADIR/jsons".replace("$ADIR", analysisDir).replace("//", "/")
        plotDir = "$ADIR/Plots".replace("$ADIR", analysisDir).replace("//", "/")
        if stage == 'plot-histograms':
            histogramDir = "$ADIR/Histograms/All".replace("$ADIR", analysisDir).replace("//", "/")
        elif stage == 'plot-diagnostics':
            histogramDir = "$ADIR/Diagnostics/NoChannel".replace("$ADIR", analysisDir).replace("//", "/")
            nominalPostfix = None #Get rid of ___nom from expectedBaseName
        elif stage == 'prepare-combine':
            histogramDir = "$ADIR/Combine/All".replace("$ADIR", analysisDir).replace("//", "/")
        else:
            raise NotImplementedError("Unrecognized plotting sub-stage: need to define the histogramDir for this case")
        if not os.path.isdir(jsonDir):
            os.makedirs(jsonDir)
        if not os.path.isdir(plotDir):
            os.makedirs(plotDir)
        if not os.path.isfile(plotConfig):
            raise ValueError("The requested plotCard {} does not appear to exist".format(plotConfig))
        if not os.path.isfile(legendConfig):
            raise ValueError("The requested legendCard {} does not appear to exist".format(legendConfig))
    else:
        raise ValueError("The analysis directory {} doesn't appear to exist".format(analysisDir))


    resultsDict = None
    loadedPlotConfig = None
    loadedLegendConfig = None
    pdfOut = None
    with open(plotConfig, "r") as jplot:
        loadedPlotConfig = copy.copy(json_load_byteified(jplot))
        with open("$ADIR/jsons/{}".format(plotCardName).replace("$ADIR", analysisDir), "w") as jpo:
            jpo.write(json.dumps(loadedPlotConfig, indent=4))
    with open(legendConfig, "r") as jlegend:
        loadedLegendConfig = copy.copy(json_load_byteified(jlegend))
        with open("$ADIR/jsons/{}".format(legendCardName).replace("$ADIR", analysisDir), "w") as jlo:
            jlo.write(json.dumps(loadedLegendConfig, indent=4))
    if isinstance(loadedPlotConfig, dict) and isinstance(loadedLegendConfig, dict):
        # jplot.write("$ADIR/jsons/{}".format(plotCardName).replace("$ADIR", analysisDir))
        #Update the plot config with the legend dictionary
        loadedPlotConfig.update(loadedLegendConfig)
        if verb:
            print("stage = {}".format(stage))
            print("analysis directory = {}".format(analysisDir))
            print("histogram directory = {}".format(histogramDir))
            print("tag = {}".format(tag))
            print("channel = {}".format(channel))
            print("plotConfig = {}".format(plotConfig))
            print("legendConfig = {}".format(legendConfig))
            print("plotCard = {}".format(plotCard))
            
        if 'pdf' in args.formats:
            pdfOutput = "$ADIR/Plots/$TAG_$PLOTCARD_$CHANNEL.pdf".replace("$ADIR", analysisDir).replace("$TAG", tag).replace("$PLOTCARD", plotCard).replace("$CHANNEL", channel).replace("//", "/")
            if args.drawSystematic is not None:
                pdfOutput = pdfOutput.replace(".pdf", ".{}.pdf".format(args.drawSystematic))
            if verb:
                print("pdfOutput = {}".format(pdfOutput))
        else:
            pdfOutput = False
        if 'C' in args.formats:
            macroOutput = True
        else:
            macroOutput = False
        if 'png' in args.formats:
            pngOutput = True
        else:
            pngOutput = False
        if combineInputList is not None:
            # combineOut = "$ADIR/Combine/CI_$ERA_$CHANNEL_$VAR.root".replace("$ADIR", analysisDir).replace("$ERA", era).replace("$VAR", combineInput).replace("$TAG", tag).replace("$PLOTCARD", plotCard).replace("$CHANNEL", channel).replace("//", "/")
            combineOut = "$ADIR/Combine/CI_$ERA_$CHANNEL_$VAR.root".replace("$ADIR", analysisDir).replace("$ERA", era).replace("$TAG", tag).replace("$PLOTCARD", plotCard).replace("$CHANNEL", channel).replace("//", "/")
            if verb:
                print("pdfOutput = {}".format(pdfOutput))
        else:
            combineOut = None
        if args.unblind:
            print("Unblinding all cards")
            for k, v in loadedPlotConfig.items():
                if "Unblind" in v.keys():
                    v["Unblind"] = True
        if args.forceBinning:
            print("Enforcing new binning: {}".format(args.forceBinning))
            for k, v in loadedPlotConfig.items():
                if "Rebin" in v.keys():
                    v["Rebin"] = args.forceBinning
        if args.forceLogY:
            print("Enforcing LogY")
            for k, v in loadedPlotConfig.items():
                if "doLogY" in v.keys():
                    v["doLogY"] = True
        if args.forceWIP:
            print("Enforcing Work In Progress Label")
            for k, v in loadedPlotConfig.items():
                if v.get("Type") == "CanvasConfig":
                    v["Label"] = "#bf{CMS} #it{Work In Progress}"

        smootheUncertainties=['OSDL_2016_jesTotalUp', 'OSDL_2016_jesTotalDown', 'OSDL_2016APV_jesTotalUp', 'OSDL_2016APV_jesTotalDown',
                              'OSDL_2017_jesTotalUp', 'OSDL_2017_jesTotalDown', 'OSDL_2018_jesTotalUp', 'OSDL_2018_jesTotalDown', 
                              'OSDL_RunII_ewkISRUp', 'OSDL_RunII_ewkISRDown', 'OSDL_RunII_ewkFSRUp', 'OSDL_RunII_ewkFSRDown', 
                              'OSDL_RunII_singletopISRUp', 'OSDL_RunII_singletopISRDown', 'OSDL_RunII_singletopFSRUp', 'OSDL_RunII_singletopFSRDown', 
                              'OSDL_RunII_ttVJetsISRUp', 'OSDL_RunII_ttVJetsISRDown', 'OSDL_RunII_ttVJetsFSRUp', 'OSDL_RunII_ttVJetsFSRDown', 
                              'OSDL_RunII_ttHISRUp', 'OSDL_RunII_ttHISRDown', 'OSDL_RunII_ttHFSRUp', 'OSDL_RunII_ttHFSRDown', 
                              'OSDL_RunII_ttultrarareISRUp', 'OSDL_RunII_ttultrarareISRDown', 'OSDL_RunII_ttultrarareFSRUp', 'OSDL_RunII_ttultrarareFSRDown', 
                              'OSDL_RunII_ttISRUp', 'OSDL_RunII_ttISRDown', 'OSDL_RunII_ttFSRUp', 'OSDL_RunII_ttFSRDown', 
                              'OSDL_RunII_ttttISRUp', 'OSDL_RunII_ttttISRDown', 'OSDL_RunII_ttttFSRUp', 'OSDL_RunII_ttttFSRDown', 
                              'OSDL_RunII_hdampUp', 'OSDL_RunII_hdampDown', 'OSDL_RunII_ueUp', 'OSDL_RunII_ueDown',
                              'OSDL_RunII_btagSF_shape_hfUp', 'OSDL_RunII_btagSF_shape_hfDown',
                              'OSDL_RunII_btagSF_shape_lfUp', 'OSDL_RunII_btagSF_shape_lfDown', 
                              'OSDL_RunII_btagSF_shape_cferr1Up', 'OSDL_RunII_btagSF_shape_cferr1Down',
                              'OSDL_RunII_btagSF_shape_cferr2Up', 'OSDL_RunII_btagSF_shape_cferr2Down', 
                              'OSDL_2017_btagSF_shape_hfstats1Up', 'OSDL_2017_btagSF_shape_hfstats1Down',
                              'OSDL_2017_btagSF_shape_hfstats2Up', 'OSDL_2017_btagSF_shape_hfstats2Down',
                              'OSDL_2017_btagSF_shape_lfstats1Up', 'OSDL_2017_btagSF_shape_lfstats1Down',
                              'OSDL_2017_btagSF_shape_lfstats2Up', 'OSDL_2017_btagSF_shape_lfstats2Down',
                              'OSDL_2018_btagSF_shape_hfstats1Up', 'OSDL_2018_btagSF_shape_hfstats1Down',
                              'OSDL_2018_btagSF_shape_hfstats2Up', 'OSDL_2018_btagSF_shape_hfstats2Down',
                              'OSDL_2018_btagSF_shape_lfstats1Up', 'OSDL_2018_btagSF_shape_lfstats1Down',
                              'OSDL_2018_btagSF_shape_lfstats2Up', 'OSDL_2018_btagSF_shape_lfstats2Down',
                              'OSDL_2016_jerUp', 'OSDL_2016_jerDown', 'OSDL_2016APV_jerUp', 'OSDL_2016APV_jerDown',
                              'OSDL_2017_jerUp', 'OSDL_2017_jerDown', 'OSDL_2018_jerUp', 'OSDL_2018_jerDown', 
                              'OSDL_RunII_ttmuRNomFDown', 'OSDL_RunII_ttmuRNomFUp', 'OSDL_RunII_ttmuFNomRDown', 'OSDL_RunII_ttmuFNomRUp', 
                              'OSDL_RunII_ttVJetsmuRNomFDown', 'OSDL_RunII_ttVJetsmuRNomFUp', 
                              'OSDL_RunII_ttVJetsmuFNomRDown', 'OSDL_RunII_ttVJetsmuFNomRUp', 
                              'OSDL_RunII_ttVJetsmuRFcorrelatedDown', 'OSDL_RunII_ttVJetsmuRFcorrelatedUp', 
                              'OSDL_RunII_singletopmuRNomFDown', 'OSDL_RunII_singletopmuRNomFUp', 
                              'OSDL_RunII_singletopmuFNomRDown', 'OSDL_RunII_singletopmuFNomRUp', 
                              'OSDL_RunII_singletopmuRFcorrelatedDown', 'OSDL_RunII_singletopmuRFcorrelatedUp', 
                              'OSDL_RunII_ttultrararemuRNomFDown', 'OSDL_RunII_ttultrararemuRNomFUp', 
                              'OSDL_RunII_ttultrararemuFNomRDown', 'OSDL_RunII_ttultrararemuFNomRUp', 
                              'OSDL_RunII_ttultrararemuRFcorrelatedDown', 'OSDL_RunII_ttultrararemuRFcorrelatedUp', 
                              'OSDL_RunII_ttHmuRNomFDown', 'OSDL_RunII_ttHmuRNomFUp', 'OSDL_RunII_ttHmuFNomRDown', 'OSDL_RunII_ttHmuFNomRUp', 
                              'OSDL_RunII_ttHmuRFcorrelatedDown', 'OSDL_RunII_ttHmuRFcorrelatedUp', 
                              'OSDL_RunII_ttttmuRNomFDown', 'OSDL_RunII_ttttmuRNomFUp', 'OSDL_RunII_ttttmuFNomRDown', 'OSDL_RunII_ttttmuFNomRUp', 
                              'OSDL_RunII_ttttmuRFcorrelatedDown', 'OSDL_RunII_ttttmuRFcorrelatedUp', 
                              'OSDL_2016_pileupUp', 'OSDL_2016_pileupDown', 'OSDL_2016APV_pileupUp', 'OSDL_2016APV_pileupDown',
                              'OSDL_2017_pileupUp', 'OSDL_2017_pileupDown', 'OSDL_2018_pileupUp', 'OSDL_2018_pileupDown', 
                              'OSDL_RunII_pdfUp', 'OSDL_RunII_pdfDown',
                              'OSDL_RunII_pdf1', 'OSDL_RunII_pdf2', 'OSDL_RunII_pdf3', 'OSDL_RunII_pdf4',
                              'OSDL_RunII_pdf5', 'OSDL_RunII_pdf6', 'OSDL_RunII_pdf7', 'OSDL_RunII_pdf8',
                              'OSDL_RunII_pdf9', 'OSDL_RunII_pdf10', 'OSDL_RunII_pdf11', 'OSDL_RunII_pdf12',
                              'OSDL_RunII_pdf13', 'OSDL_RunII_pdf14', 'OSDL_RunII_pdf15', 'OSDL_RunII_pdf16',
                              'OSDL_RunII_pdf17', 'OSDL_RunII_pdf18', 'OSDL_RunII_pdf19', 'OSDL_RunII_pdf20',
                              'OSDL_RunII_pdf21', 'OSDL_RunII_pdf22', 'OSDL_RunII_pdf23', 'OSDL_RunII_pdf24',
                              'OSDL_RunII_pdf25', 'OSDL_RunII_pdf26', 'OSDL_RunII_pdf27', 'OSDL_RunII_pdf28',
                              'OSDL_RunII_pdf29', 'OSDL_RunII_pdf30',
        ],
        if args.noSmoothing:
            smootheUncertainties=[]
        
        resultsDict = loopPlottingJSON(loadedPlotConfig, era=args.era, channel=args.channel, systematicCards=args.systematics_cards,
                                       Cache=None, histogramDirectory=histogramDir, batchOutput=doBatch, drawSystematic=args.drawSystematic, drawLegends=args.drawLegends,
                                       drawNormalized=args.drawNormalized,
                                       analysisDirectory=analysisDir, tag=tag, plotCard=plotCard, macroOutput=macroOutput, pngOutput=pngOutput,
                                       pdfOutput=pdfOutput, combineOutput=combineOut, combineInputList=combineInputList,
                                       combineCards=combineCards,
                                       nominalPostfix=nominalPostfix, separator="___", lumi=lumi, useCanvasMax=useCanvasMax,
                                       smootheUncertainties=smootheUncertainties,
                                       skipSystematics=skipSystematics, verbose=verb,
                                       zeroingThreshold=zeroingThreshold, differentialScale=differentialScale, histogramUncertainties=args.histogramUncertainties,
                                       ratioUncertainties=args.ratioUncertainties, orderReverse=args.orderReverse
        );
    else:
        raise RuntimeError("The loading of the plot or legend cards failed. They are of type {} and {}, respectively".format(type(loadedPlotConfig),type(loadedLegendConfig)))

elif stage == 'generate-plotCard':
    if verb:
        print("stage = {}".format(stage))
        print("analysis directory = {}".format(analysisDir))
        print("channel = {}".format(channel))
        print("variables = {}".format(variables))
        print("nJet categories = {}".format(nJets))
        print("nBTagCategories = {}".format(nBTags))
    categories_dict = {}
    for b in nBTags:
        categories_dict[b] = []
        for j in nJets:
            categories_dict[b].append("{blind}HT500_{nB}_{nJ}".format(blind="" if "B2" in b and ("4" in j or "5" in j or "6" in j) else "blind_", nB=b, nJ=j))
    
    thePlotCard = generateJSON(models["v1.0"], variables, categories_dict=categories_dict,era=era,channel=channel,
                               name_format="Plot_{cat}___{var}", rebin=None, projection=None, force=False)
    thePlotCard.update(defaultNoLegend)
    with open("testPlotCard.json", "w") as jo:
        jo.write(json.dumps(thePlotCard, indent=4))
elif stage == 'generate-legendCard':
    print("No method for generating legendCard yet")
    


for channel in ["MuMu_ElMu", "MuMu", "ElMu",]: # "All", "ChannelComparison", "ElEl"]:
    continue
    if channel in ["MuMu", "ElMu"]: continue
    Tag = "July2"; lumi=41.53; nB = "2pB"
    folder = "/eos/user/n/nmangane/analysis/{tag}/Histograms/All".format(tag=Tag, chan=channel)
    replacementLegend={}
    with open("{}/{}Legend.json".format(folder, channel), "r") as jlegend:
        replacementLegend = copy.copy(json_load_byteified(jlegend))
    with open("{}/Mu_All_{}.json".format(folder, nB), "r") as j1:
        loadedJSON1 = json_load_byteified(j1)
        loadedJSON1.update(replacementLegend)
        # resultsMU = loopPlottingJSON(loadedJSON1, Cache=None, directory=folder, batchOutput=True, pdfOutput="{}/{}.pdf".format(folder.replace("/Histograms/All", ""), Tag + "_Muons_" + channel + "_" + nB), lumi=lumi)
    time.sleep(5)
    with open("{}/El_All_{}.json".format(folder, nB), "r") as j2:
        loadedJSON2 = json_load_byteified(j2)
        loadedJSON2.update(replacementLegend)
        # resultsEL = loopPlottingJSON(loadedJSON2, Cache=None, directory=folder, batchOutput=True, pdfOutput="{}/{}.pdf".format(folder.replace("/Histograms/All".format(channel), ""), Tag + "_Electrons_" + channel + "_" + nB), lumi=lumi)
    time.sleep(5)
    with open("{}/MET_All_{}.json".format(folder, nB), "r") as j3:
        loadedJSON3 = json_load_byteified(j3)
        loadedJSON3.update(replacementLegend)
        # resultsMET = loopPlottingJSON(loadedJSON3, Cache=None, directory=folder, batchOutput=True, pdfOutput="{}/{}.pdf".format(folder.replace("/Histograms/All".format(channel), ""), Tag + "_MET_" + channel + "_" + nB), lumi=lumi);
    time.sleep(5)
    with open("{}/Jet_All_{}.json".format(folder, nB), "r") as j4:
        loadedJSON4 = json_load_byteified(j4)
        loadedJSON4.update(replacementLegend)
        # resultsJET = loopPlottingJSON(loadedJSON4, Cache=None, directory=folder, batchOutput=True, pdfOutput="{}/{}.pdf".format(folder.replace("/Histograms/All".format(channel), ""), Tag + "_Jets_" + channel + "_" + nB), lumi=lumi)
    time.sleep(5)
    with open("{}/Event_All_{}.json".format(folder, nB), "r") as j4:
        loadedJSON5 = json_load_byteified(j4)
        loadedJSON5.update(replacementLegend)
        # resultsEvent = loopPlottingJSON(loadedJSON5, Cache=None, directory=folder, batchOutput=True, pdfOutput="{}/{}.pdf".format(folder.replace("/Histograms/All".format(channel), ""), Tag + "_Event_" + channel + "_" + nB), lumi=lumi)
   
