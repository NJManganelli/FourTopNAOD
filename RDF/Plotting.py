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
import array
import json
import copy
import argparse
import uuid
import pdb
# from ruamel.yaml import YAML
from IPython.display import Image, display, SVG
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
                 channel="No Channel", name_format="Plot_{chan}___{cat}___{var}", rebin=None, projection=None, force=False):
    if channel == "ElMu":
        nice_channel = "#it{e}#mu"
    elif channel == "MuMu":
        nice_channel = "#mu#mu"
    elif channel == "ElEl":
        nice_channel = "#it{e}#it{e}"
    else:
        nice_channel = channel
    theDict = {}
    for categorization, categories in categories_dict.items():
        for variable in variables:
            for k, v in model.items():
                newKey = k.replace("$VAR", variable).replace("$CATEGORIZATION", categorization)
                if "$CAT" in newKey:
                    for cat in categories:
                        theDict[newKey.replace("$CAT", cat)] = {}
                        for vk, vv in v.items():
                            #newSubkey = vk.replace("$VAR", variable)
                            if type(vv) == str:
                                newSubvalue = vv.replace("$VAR", variable).replace("$CATEGORIZATION", categorization).replace("$CAT", cat).replace("$CHANNEL", nice_channel)
                            elif type(vv) == list:
                                newSubvalue = []
                                for l in vv:
                                    if type(l) == str:
                                        newSubvalue.append(l.replace("$VAR", variable).replace("$CATEGORIZATION", category).replace("$CAT", cat).replace("$CHANNEL", nice_channel))
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
                            newSubvalue = vv.replace("$VAR", variable).replace("$CATEGORIZATION", categorization).replace("$CHANNEL", nice_channel)
                        elif type(vv) == list:
                            #Canvas specialization
                            if vk == "Plots":
                                #Plot_ElMu___HT500_ZWindowMET0Width0_$CAT___$VAR"
                                newSubvalue = [copy.copy(name_format).format(chan=channel, cat=cat, var=variable) for cat in categories]
                            #Canvas specialization
                            elif vk == "Labels":
                                newSubvalue = ["{} {}".format(nice_channel, cat.replace("blind_", "").replace("_", " ")) for cat in categories]
                            else:
                                newSubvalue = []
                                for l in vv:
                                    if type(l) == str:
                                        newSubvalue.append(l.replace("$VAR", variable).replace("$CATEGORIZATION", category).replace("$CHANNEL", nice_channel))
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
# pprint.pprint(generateJSON(modelPlotJSON_CAT, ["HT"], rebin=7, projection=["X", 2, 4], force=True))

#1180, 1185, 1179, 1181, 1183, 1182, 1184
colors = {
        "ggH": ROOT.TColor.GetColor("#BF2229"),
        "qqH": ROOT.TColor.GetColor("#00A88F"),
        "TT": ROOT.TColor.GetColor(155, 152, 204),
        "W": ROOT.TColor.GetColor(222, 90, 106),
        "QCD":  ROOT.TColor.GetColor(250, 202, 255),
        "ZLL": ROOT.TColor.GetColor(100, 192, 232),
        "ZTT": ROOT.TColor.GetColor(248, 206, 104),
        }
colortest = {}
# cc = ROOT.TCanvas()
# tl = ROOT.TLegend()
# mx = 1
# for kn, k in enumerate(colors):
#     colortest[k] = ROOT.TH1F(k, k, 10,0,10)
#     colortest[k].Fill(kn, 1+math.sqrt(kn))
#     mx = max(mx, colortest[k].GetMaximum())
#     colortest[k].SetFillColor(colors[k])
#     tl.AddEntry(colortest[k], k, "f")
#     if kn == 0:
#         colortest[k].Draw("FILL")
#     else:
#         colortest[k].Draw("FILL SAME")
# mx *= 1.1
# for k in colortest:
#     colortest[k].SetMaximum(mx)
# tl.Draw()
# cc.Draw()
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
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

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

    ROOT.gStyle.SetLabelColor(1, "XYZ")
    ROOT.gStyle.SetLabelFont(42, "XYZ")
    ROOT.gStyle.SetLabelOffset(0.007, "XYZ")
    ROOT.gStyle.SetLabelSize(0.04, "XYZ")
    
    ROOT.gStyle.SetAxisColor(1, "XYZ")
    ROOT.gStyle.SetStripDecimals(True)
    ROOT.gStyle.SetTickLength(0.03, "XYZ")
    ROOT.gStyle.SetNdivisions(nDivisions, "XYZ")
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)

    ROOT.gStyle.SetPaperSize(20., 20.)
    ROOT.gStyle.SetHatchesLineWidth(5)
    ROOT.gStyle.SetHatchesSpacing(0.05)

    ROOT.TGaxis.SetExponentOffset(-0.08, 0.01, "Y")

###########SAME UP TO THIS POINT##############
def createRatio(h1, h2, Cache=None, ratioTitle="input 0 vs input 1", ratioColor = None, ratioStyle = None,
                ratioMarkerStyle = 20, ratioAlpha = 0.5, yMin = 0.5, yMax = 1.5, isBlinded=False, scaleText=2.0, nDivisions=105,):
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
    if "ROOT.TH" in str(type(h2)):
        h3.Divide(h2)
    h3.SetMinimum(yMin)
    h3.SetMaximum(yMax)

    # Adjust y-axis settings
    y = h3.GetYaxis()
    y.SetTitle(ratioTitle)
    y.SetNdivisions(nDivisions)
    #FIXME#y.SetTitleSize(20)
    #FIXME#y.SetTitleFont(43)
    #FIXME#y.SetTitleOffset(2.5) #1.55
    #y.SetLabelFont(43*nPads)
    y.SetLabelSize(y.GetLabelSize()*scaleText)

    # Adjust x-axis settings
    x = h3.GetXaxis()
    x.SetNdivisions(nDivisions)
    #FIXME#x.SetTitleSize(20)
    #FIXME#x.SetTitleFont(43)
    #FIXME#x.SetTitleOffset(4.0)
    #x.SetLabelFont(43*nPads)
    x.SetLabelSize(x.GetLabelSize()*scaleText)

    #Do blinding
    if isBlinded:
        for i in xrange(h3.GetNbinsX()):
            h3.SetBinContent(i+1, 0.0)
        h3.SetMarkerColor(ROOT.kWhite)
        h3.SetLineColor(ROOT.kWhite)
        h3.SetFillColor(ROOT.kWhite)
    if Cache == None:
        Cache = {}
    #These keys will not be sufficient for multiple ratios to be plotted together, #FIXME
    Cache["ratio_hist"] = h3
    Cache["ratio_Xaxis"] = x
    Cache["ratio_Yaxis"] = y
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
    xEdgesLow = [bordersL + usableLR*z/float(nXPads) for z in xrange(nXPads)]
    #Unnecessary for pdf, doesn't help with jsroot canvas gap between 3rd and 4th pads in mountain range
    #xEdgesLow = [float("{:.3f}".format(edge)) for edge in xEdgesLow] 
    xEdgesHigh = [bordersL + usableLR*(z+1)/float(nXPads) for z in xrange(nXPads)]
    #xEdgesHigh = [float("{:.3f}".format(edge)) for edge in xEdgesHigh]
    #Now the edges must be calculated for each pad, hardcode nYPads = 2
    nYPads = 2
    #Here's where we correct the 1st and last pads to make space for the border/pad margin
    xEdgesLow[0] -= bordersL
    xEdgesHigh[-1] += bordersR
    yEdgesLow = [0, bordersB + usableTB*(1-topFraction)]
    yEdgesHigh = [bordersB + usableTB*(1-topFraction), 1]
    #yEdgesLow[0] -= bordersB
    #yEdgesHigh[-1] += bordersT
    yDivision = 1-bordersT
    if doRatio:
        yDivision = 1-topFraction
        
    #Calculate the pad margins, which will be converted from the desired border size as fraction of the total canvas size
    #to equivalent fraction of the pad size itself, using the edges arrays.
    marginL = bordersL/(xEdgesHigh[0] - xEdgesLow[0])
    marginR = bordersR/(xEdgesHigh[-1] - xEdgesLow[-1])
    marginB = bordersB/(yEdgesHigh[0] - yEdgesLow[0])
    marginT = bordersT/(yEdgesHigh[-1] - yEdgesLow[-1])
    #print("{} {} \n {} {}".format(xEdgesLow, xEdgesHigh, yEdgesLow, yEdgesHigh))
    #print("{} {} {} {}".format(marginL, marginR, marginT, marginB))


    for z in xrange(nXPads):
        c.cd()  # returns to main canvas before defining another pad, to not create sub-subpad
        padU = ROOT.TPad("{}_{}".format(canvasTitle,z), "{}_{}".format(canvasTitle,z), 
                        xEdgesLow[z], yEdgesLow[-1], xEdgesHigh[z], yEdgesHigh[-1]) #xmin ymin xmax ymax as fraction
        #Set margins for pads depending on passed configuration option, whether ratio and mountainranging are enabled
        padU.SetTopMargin(marginT)
        if doRatio:
            padU.SetBottomMargin(0)  # joins upper and lower plot
        else:
            padU.SetBottomMargin(marginB)
        if doMountainrange:
            #Only set the margin to 0 if there is at least one pad to the right, which is equal to zlast = nXPads - 1. Don't do the last right margin...
            if 0 <= z < nXPads - 1:
                padU.SetRightMargin(0)
            else:
                padU.SetRightMargin(marginR)
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
            padL.SetTopMargin(0)  # joins upper and lower plot
            padL.SetBottomMargin(marginB)
            if doMountainrange:
                #Only set the margin to 0 if there is at least one pad to the right, which is equal to zlast = nXPads - 1. Don't do the last right margin...
                if 0 <= z < nXPads - 1:
                    padL.SetRightMargin(0)
                else:
                    padL.SetRightMargin(marginR)
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

def createCanvasPads_OldVersion(canvasTitle, Cache=None, doRatio=False, doMountainrange=False, setXGrid=False, setYGrid=False,
                     nXPads=1, topFraction=0.7, marginsLRTB=[0.1, 0.1, 0.1, 0.1], xPixels=800, yPixels=800):
    """Create canvas with two pads vertically for each of doLin and doLog if they are true"""
    #Divide implicitely creates subpads. This function uses more explicit methods to do the same with varying pad sizes
    c = ROOT.TCanvas(canvasTitle, canvasTitle, xPixels, yPixels)
    # Upper histogram plot is pad1
    upperPads = []
    lowerPads = []
    marginL = marginsLRTB[0]
    marginR = marginsLRTB[1]
    marginT = marginsLRTB[2]
    marginB = marginsLRTB[3]
    #FIXME: Add in space for margins on the left, which will require an additional offset when calculating the edges
    usableLR = 1.0 - marginL - marginR
    usableTB = 1.0 - marginT - marginB
    xEdgesLow = [marginL + usableLR*z/float(nXPads) for z in xrange(nXPads)]
    xEdgesHigh = [marginL + usableLR*(z+1)/float(nXPads) for z in xrange(nXPads)]
    #Margins aren't wholly correct for first and last pads, so hardcode a correction here:
    xEdgesLow[0] -= marginL/5.0
    xEdgesHigh[-1] += marginR/5.0
    yDivision = 1-marginT
    if doRatio:
        yDivision = 1-topFraction
        
    


    for z in xrange(nXPads):
        c.cd()  # returns to main canvas before defining another pad, to not create sub-subpad
        padU = ROOT.TPad("{}_{}".format(canvasTitle,z), "{}_{}".format(canvasTitle,z), 
                        xEdgesLow[z], yDivision, xEdgesHigh[z], 1.0 - marginT) #xmin ymin xmax ymax as fraction
        #Set margins for pads depending on passed configuration option, whether ratio and mountainranging are enabled
        padU.SetTopMargin(marginT)
        if doRatio:
            padU.SetBottomMargin(0)  # joins upper and lower plot
        else:
            padU.SetBottomMargin(marginB)
        if doMountainrange:
            #Only set the margin to 0 if there is at least one pad to the right, which is equal to zlast = nXPads - 1. Don't do the last right margin...
            if 0 <= z < nXPads - 1:
                padU.SetRightMargin(0)
            else:
                padU.SetRightMargin(marginR)
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
                             xEdgesLow[z], marginB, xEdgesHigh[z], yDivision) #xmin ymin xmax ymax as fraction
            padL.SetTopMargin(0)  # joins upper and lower plot
            padL.SetBottomMargin(marginB)
            if doMountainrange:
                #Only set the margin to 0 if there is at least one pad to the right, which is equal to zlast = nXPads - 1. Don't do the last right margin...
                if 0 <= z < nXPads - 1:
                    padL.SetRightMargin(0)
                else:
                    padL.SetRightMargin(marginR)
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
    #Store the edges in the Cache, along with the canvas, upper and lower pads
    Cache["canvas"] = c
    Cache["canvas/upperPads"] = upperPads
    Cache["canvas/lowerPads"] = lowerPads
    Cache["canvas/xEdgesLow"] = xEdgesLow
    Cache["canvas/xEdgesHigh"] = xEdgesHigh
    Cache["canvas/yEdgesLow"] = yEdgesLow
    Cache["canvas/yEdgesHigh"] = yEdgesHigh
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

def makeCategoryHists(histFile, legendConfig, histNameCommon, systematic=None, rebin=None, projection=None, 
                      separator="___", nominalPostfix="nom", verbose=False, debug=False, pn=None):
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
    histKeys = set([hist.GetName() for hist in histFile.GetListOfKeys()])
    unblindedKeys = dict([(histKey.replace("blind_", "").replace("BLIND", ""), histKey) for histKey in histKeys])
    #try:
    #    #histFile = ROOT.TFile.Open(histFileName)
    #    histKeys = set([hist.GetName() for hist in histFile.GetListOfKeys()])
    #except:
    #    print("GetListOfKeys() fails in file {}".format(histFile.GetName()))
    #    return {}
    if debug:
        print("The histKeys are: {}".format(histKeys))
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
        addHistoName = sampleCat + separator + expectedBaseName
        #print(addHistoName)
        scaleArray = config.get("ScaleArray", None)
        scaleList = [] if scaleArray != None else None
        for nn, subCatName in enumerate(config["Names"]):
            expectedName = subCatName + separator + expectedBaseName
            fallbackName = subCatName + separator + fallbackBaseName
            fallbackName2 = subCatName + separator + fallbackBaseName
            if fallbackName2[-6:] == "___nom": fallbackName2 = fallbackName2[:-6]
            if debug: print("Creating addHistoName {}".format(addHistoName))
            #Skip plots that contain neither the systematic requested nor the nominal histogram
            # if expectedName in histKeys:
            if expectedName in unblindedKeys:
                #Append the histo to a list which will be added using a dedicated function
                histoList.append(histFile.Get(unblindedKeys[expectedName]))
                if scaleList != None:
                    scaleList.append(scaleArray[nn])
            # elif fallbackName in histKeys:
            elif fallbackName in unblindedKeys:
                #Append the histo to a list which will be added using a dedicated function
                histoList.append(histFile.Get(unblindedKeys[fallbackName]))
                if scaleList != None:
                    scaleList.append(scaleArray[nn])
            elif fallbackName2 in unblindedKeys:
                #Append the histo to a list which will be added using a dedicated function
                histoList.append(histFile.Get(unblindedKeys[fallbackName2]))
                if scaleList != None:
                    scaleList.append(scaleArray[nn])
            else:
                theUnfound[sampleCat][subCatName] = expectedName
                if verbose:
                    print("for {} and histNameCommon {}, makeCombinationHists failed to find a histogram (systematic or nominal) corresponding to {}\n\t{}\n\t{}"\
                          .format(histFile.GetName(), histNameCommon, subCatName, expectedName, fallbackName))
                continue

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
            elif type(projection) == str:
                pre_projection_name = retHists[sampleCat].GetName()
                if "ROOT.TH2" in str(type(retHists[sampleCat])):
                    retHists[sampleCat].SetName(pre_projection_name + "_preProjection")
                    if projection == "X":
                        retHists[sampleCat] = retHists[sampleCat].ProjectionX(pre_projection_name)
                    elif projection == "Y":
                        retHists[sampleCat] = retHists[sampleCat].ProjectionY(pre_projection_name)
                    else:
                        print("Error, {} is not a valid projection axis for TH2".format(projection))
                elif "ROOT.TH3" in str(type(retHists[sampleCat])):
                    retHists[sampleCat].SetName(pre_projection_name + "_preProjection")
                    if projection in ["X", "Y", "Z", "XY", "XZ", "YZ", "YX", "ZX", "ZY"]:
                        retHists[sampleCat] = retHists[sampleCat].Project3D(projection)
                    else:
                        print("Error, {} is not a valid projection axis/axes for TH3".format(projection))
                else:
                    print("Error, projection not possible for input type in [histo_category: {} ]: {}".format(addHistoName, type(rebin)))
            elif type(projection) == list and type(projection[0]) == str:
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
            #execute rebinning based on type: int or list for variable width binning
            if rebin == None:
                pass
            elif type(rebin) == int:
                retHists[sampleCat].Rebin(rebin)
            elif type(rebin) == list:
                rebin_groups = len(rebin) - 1
                rebin_array = array.array('d', rebin)
                original_name = retHists[sampleCat].GetName()
                retHists[sampleCat].SetName(original_name + "_originalBinning")
                retHists[sampleCat] = retHists[sampleCat].Rebin(rebin_groups, original_name, rebin_array)
            else:
                print("Unsupported rebin input type in [histo_category: {} ]: {}".format(addHistoName, type(rebin)))
            if debug:
                print("the retHists for category '{}' is {}".format(cat, retHists))
            #Modify the histogram with style and color information, where appropriate
            if config["Style"] == "Fill":
                retHists[sampleCat].SetFillColor(int(config["Color"]))
                retHists[sampleCat].SetLineColor(int(config["Color"]))
            elif config["Style"] == "FillAlpha":
                retHists[sampleCat].SetFillColorAlpha(config["Color"], config.get("Alpha", 0.5))
                retHists[sampleCat].SetLineColor(config["Color"])
            elif config["Style"] == "Line":     
                retHists[sampleCat].SetLineColor(config["Color"])
            elif config["Style"] == "Marker":   
                retHists[sampleCat].SetMarkerStyle(config.get("MarkerStyle", 0))
                retHists[sampleCat].SetMarkerSize(1.0)
                retHists[sampleCat].SetMarkerColor(config["Color"])
                retHists[sampleCat].SetLineColor(config["Color"])
                #Styles kFullCircle (20), kFullSquare (21), kFullTriangleUp (22), kFullTriangleDown (23), kOpenCircle (24)
            else:
                pass
    #for hn, hh in retHists.items():
    #    ROOT.SetOwnership(hh,0)
    return retHists, theUnfound


def makeSuperCategories(histFile, legendConfig, histNameCommon, systematic=None, nominalPostfix="nom", 
                        separator="___", orderByIntegral=True, rebin=None, projection=None, 
                        verbose=False, debug=False, pn=None):
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
    #Get coordinates for the legend, create it, store the pointer in the dictionary (so it isn't deleted, to hammer the point over and over)
    coord = legendConfig.get("Coordinates")
    nColumns = legendConfig.get("nColumns")
    leg = ROOT.TLegend(coord[0], coord[1], coord[2], coord[3])
    #leg.SetBorderSize(0)
    #nColumns = math.floor(math.sqrt(len(legendConfig.get("Categories"))))
    leg.SetNColumns(nColumns)
    if debug:
        print("nColumns = {} generated from {}".format(nColumns, len(legendConfig.get("Categories"))))
    leg.SetTextSize(0.03)
    retDict["Legend"] = leg
    
    #Create dictionary to return one level up, calling makeCategoryHists to combine subsamples together 
    #and do color, style configuration for them. Pass through the rebin parameter
    retDict["Categories/hists"], retDict["Categories/theUnfound"] = makeCategoryHists(histFile, legendConfig, histNameCommon,
                                                    systematic=systematic, rebin=rebin, projection=projection,
                                                    nominalPostfix=nominalPostfix, separator=separator,
                                                    verbose=verbose, debug=debug, pn=pn)
    #If empty because of a failure in opening some file, early return the dictionary
    #if len(retDict["Categories/hists"]) == 0:
    #    return retDict
    if debug:
        print("the retDict contains:")
        pprint.pprint(retDict["Categories/hists"])
    #Create an ordered list of tuples using either the integral of each category histogram or just the name (for consistency)
    orderingList = []
    for cat_name, cat_hist in retDict["Categories/hists"].items():
        orderingList.append((cat_hist.GetSumOfWeights(), cat_name, cat_hist, ))
    if orderByIntegral:
        orderingList.sort(key=lambda j: j[0], reverse=False)
    else:
        orderingList.sort(key=lambda j: j[1], reverse=False)
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
            for tup in tmpList:
                legendCode = legendConfig["Categories"][tup[1]]["Style"]
                if legendCode == "Fill" or legendCode == "FillAlpha":
                    legendCode = "F"
                elif legendCode == "Line":
                    legendCode = "L"
                else:
                    #Assume Marker style
                    legendCode = "P"
                #Add the legend entry
                leg.AddEntry(tup[2], tup[1] + "(blind)" if "blind" in tup[2].GetName().lower() else tup[1], legendCode)
                #Add the category histogram to the stack
                retDict["Supercategories"][super_cat_name].Add(tup[2])
            #Acquire the stats for the finished stack and store it in the dictionary, but we only half-prepare this, since the histogram must be 'drawn' before a stats object is created
            retDict["Supercategories/hists"][super_cat_name] = retDict["Supercategories"][super_cat_name].GetStack().Last()#.GetListOfFunctions().FindObject("stats")
            #retDict["Supercategories/xAxis"][super_cat_name] = retDict["Supercategories"][super_cat_name].GetStack().First().GetXaxis()
            #retDict["Supercategories/yAxis"][super_cat_name] = retDict["Supercategories"][super_cat_name].GetStack().First().GetYaxis()
        #Treat it as a super addition of histograms instead
        else:
            retDict["Supercategories"][super_cat_name] = addHists([tup[2] for tup in tmpList], 
                                                                  "s_{blind}{cat}{sep}{com}{sep}{sys}".format(cat=super_cat_name, 
                                                                                                       sep=separator,
                                                                                                       com=histNameCommon,
                                                                                                              sys="" if systematic == None else systematic,
                                                                                                              blind="BLIND" if len([tup[2].GetName() for tup in tmpList if "BLIND" in tup[2].GetName()]) > 0 else ""), 
                                                                  scaleArray = None)
            legendCode = legendConfig["Categories"][tup[1]]["Style"]
            if legendCode == "Fill" or legendCode == "FillAlpha":
                legendCode = "F"
            elif legendCode == "Line":
                legendCode = "L"
            else:
                #Assume Marker style
                legendCode = "P"
            #Add the legend entry, but instead of the tup[2] histogram, the overall added hist.
            legendLabel = tup[1] + " (blind)" if "blind" in tup[2].GetName().lower() else tup[1] #This only works if the first category is blinded
            leg.AddEntry(retDict["Supercategories"][super_cat_name], legendLabel, legendCode)
            retDict["Supercategories/hists"][super_cat_name] = retDict["Supercategories"][super_cat_name]#.GetListOfFunctions().FindObject("stats")
            #retDict["Supercategories/xAxis"][super_cat_name] = retDict["Supercategories"][super_cat_name].GetXaxis()
            #retDict["Supercategories/yAxis"][super_cat_name] = retDict["Supercategories"][super_cat_name].GetYaxis()
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
    
    
def loopPlottingJSON(inputJSON, Cache=None, histogramDirectory = ".", batchOutput=False, closeFiles=True, 
                     pdfOutput=None, combineOutput=None, macroOutput=None, pngOutput=None, useCanvasMax=False,
                     nominalPostfix="nom", separator="___", verbose=False, debug=False, nDivisions=105, lumi="N/A"):
    """Loop through a JSON encoded plotcard to draw plots based on root files containing histograms.
    Must pass a cache (python dictionary) to the function to prevent python from garbage collecting everything.
    
    This latter point could be fixed via SetDirectory(0) being called on relevant histograms and not creating python
    intermediate objects like xaxis=hist.GetXaxis(), but instead chaining accessors/methods a la
    hist.GetXaxis().SetTitle(hist.GetXaxis().GetTitle().replace("meh", "amazing"))"""
    
    #Disable drawing in batch mode
    if batchOutput is True:
        ROOT.gROOT.SetBatch()
        
    #set default style
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
    for fn in fileList:
        if fn == "NON-STRING FILES VALUE": continue
        fileDict["{}/{}".format(histogramDirectory, fn)] = ROOT.TFile.Open("{}/{}".format(histogramDirectory, fn), "read")
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
    print("FIXME: systematics disabled unless combineOutput!=None right now! Temporary patch for faster plotting")
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
        # systematics = legendConfig["Systematics"]
        print("Making systematics list by hand here, FIXME FIXME")
        systematics = ['prefireDown', 'prefireUp', 'pileupDown', 'pileupUp', 
                       'jec_13TeV_R2017Down', 'jec_13TeV_R2017Up', 'jer_13TeV_R2017Down', 'jer_13TeV_R2017Up', 
                       'btagSF_shape_lfDown', 'btagSF_shape_lfUp', 'btagSF_shape_hfDown', 'btagSF_shape_hfUp', 
                       'btagSF_shape_jesDown', 'btagSF_shape_jesUp', 
                       'btagSF_shape_lfstats1Down', 'btagSF_shape_lfstats1Up', 'btagSF_shape_lfstats2Up', 'btagSF_shape_lfstats2Down', 
                       'btagSF_shape_hfstats1Down', 'btagSF_shape_hfstats1Up', 'btagSF_shape_hfstats2Down', 'btagSF_shape_hfstats2Up', 
                       'btagSF_shape_cferr1Down', 'btagSF_shape_cferr1Up', 'btagSF_shape_cferr2Down', 'btagSF_shape_cferr2Up', 
                       'FSRDown', 'FSRUp', 'ISRDown', 'ISRUp', 
                       'muRNomFDown', 'muRNomFUp', 'muFNomRDown', 'muFNomRUp', 'muRFcorrelatedDown', 'muRFcorrelatedUp', 
        ]
        #Deduce systematics automatically...
        
        #Load the LegendConfig which denotes which samples to use, colors to assign, etc.
        
        #Call createCanvasPads with our Can(vas)Cache passed to it, which will be subsequently filled,
        #allowing us to toss the returned dictionary into a throwaway variable '_'
        _ = createCanvasPads(can_name, CanCache, doRatio=doRatio, doMountainrange=doMountainrange, setXGrid=False, 
                             setYGrid=False, nXPads=nXPads, topFraction=0.7, bordersLRTB = canCoordinates, 
                             xPixels=xPixels, yPixels=yPixels)
        CanCache["subplots/files"] = []
        CanCache["subplots/supercategories"] = []
        CanCache["subplots/firstdrawn"] = []
        CanCache["subplots/supercategories/systematics"] = {}
        for sys in systematics:
            CanCache["subplots/supercategories/systematics"][sys] = []
        CanCache["subplots/ratios"] = []
        CanCache["subplots/channels"] = []
        CanCache["subplots/histograms"] = []
        CanCache["subplots/stats"] = []
        CanCache["subplots/rebins"] = []
        CanCache["subplots/projections"] = []
        CanCache["subplots/labels"] = []
        CanCache["subplots/maxima"] = []
        CanCache["subplots/minima"] = []
        CanCache["subplots/integrals"] = []
        CanCache["subplots/integraltables"] = []
        
        
        #generate the header and label for the canvas, adding them in the cache as 'cms_label' and 'cms_header'
        header = can_dict.get("Header", legendConfig.get("Header", "#sqrt{{s}} = 13 TeV, L_{{int}} = {lumi} fb^{{-1}}"))
        header_position = can_dict.get("HeaderPosition", legendConfig.get("HeaderPosition", 0.063))
        label = can_dict.get("Label", legendConfig.get("Label", "#bf{CMS Internal}"))
        label_position = can_dict.get("LabelPosition", legendConfig.get("LabelPosition", 0.05))
        _ = getLabelAndHeader(Cache=CanCache, 
                              label=label, 
                              header=header.format(lumi=lumi),
                              header_position=header_position,
                              label_position=label_position,
                              marginTop=CanCache["canvas/marginT"])
        
        
        for pn, subplot_name in enumerate(CanCache["subplots"]):
            subplot_dict = plots["{}".format(subplot_name)]
            nice_name = subplot_name.replace("Plot_", "").replace("Plot", "").replace("blind_", "").replace("BLIND", "")
            #Append the filename to the list
            plotFileName = "{}/{}".format(histogramDirectory, subplot_dict["Files"])
            if plotFileName in fileDict:
                CanCache["subplots/files"].append(fileDict[plotFileName])
            else:
                raise RuntimeError("File not available, was it stored in a list or something?")
            CanCache["subplots/rebins"].append(subplot_dict.get("Rebin"))
            CanCache["subplots/projections"].append(subplot_dict.get("Projection"))
            CanCache["subplots/integrals"].append(collections.OrderedDict())
            #Call makeSuperCategories with the very same file [pn] referenced, plus the legendConfig
            CanCache["subplots/supercategories"].append(makeSuperCategories(CanCache["subplots/files"][pn], legendConfig, nice_name, 
                                systematic=None, orderByIntegral=True, rebin=CanCache["subplots/rebins"][pn], 
                                projection=CanCache["subplots/projections"][pn], 
                                nominalPostfix=nominalPostfix, separator=separator, verbose=verbose, debug=False, pn=pn))
            if combineOutput != None:                
                for sys in systematics:
                    CanCache["subplots/supercategories/systematics"][sys].append(makeSuperCategories(CanCache["subplots/files"][pn], legendConfig, 
                                nice_name,
                                systematic=sys, orderByIntegral=True, rebin=CanCache["subplots/rebins"][pn], 
                                projection=CanCache["subplots/projections"][pn], 
                                nominalPostfix=nominalPostfix, separator=separator, verbose=verbose, debug=False, pn=pn))
            #access the list of upperPads created by createCanvasPads(...)
            #if len(CanCache["subplots/supercategories"][-1]["Categories/hists"]) == 0:
            #    continue
            CanCache["canvas/upperPads"][pn].cd()
            
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
                    thisIntegral = "(blind)"
                    pass
                else:
                    thisMax = max(thisMax, drawable.GetMaximum())
                    thisMin = min(thisMin, drawable.GetMinimum())
                    if isinstance(drawable, (ROOT.TH1)):
                        thisIntegral = str("{:4.3f}".format(drawable.Integral()))
                    elif isinstance(drawable, (ROOT.THStack)):
                        thisIntegral = str("{:4.3f}".format(drawable.GetStack().Last().Integral()))
                CanCache["subplots/integrals"][pn][super_cat_name] = thisIntegral

                #Find and store the maxima/minima for each histogram
            CanCache["subplots/maxima"].append(thisMax)
            CanCache["subplots/minima"].append(thisMin)
            
            #Do nasty in-place sorting of the dictionary to get the Stacks drawn first, by getting the key from each key-value pair and getting the "Stack" field value,
            #from the legendConfig, recalling we need the key part of the tuple (tuple[0]) with a reverse to put the Stack == True items up front...
            for super_cat_name, drawable in sorted(CanCache["subplots/supercategories"][pn]["Supercategories"].items(), 
                                                   key=lambda x: legendConfig["Supercategories"][x[0]]["Stack"], reverse=True):
                #Don't draw blinded data...
                if "data" in super_cat_name.lower() and "blind" in drawable.GetName().lower() and subplot_dict.get("Unblind", False) == False:
                    if isinstance(drawable, ROOT.TH1):
                        for binnumber in xrange(drawable.GetNbinsX()+2):
                            drawable.SetBinContent(binnumber, 0); drawable.SetBinError(binnumber, 0)
                    else: #handle TH2, graphs?
                        pass
                #Draw SAME if not the first item, using options present in legend configuration
                draw_command = legendConfig["Supercategories"][super_cat_name]["Draw"]
                if dn > 0:
                    draw_command += " SAME"
                #Append the drawable to a list for later modification of the maxima/minima... messy for deletion if that has to be done, though!
                else:
                    CanCache["subplots/firstdrawn"].append(drawable)
                if debug:
                    print("supercategory: {}    type: {}    command: {}".format(super_cat_name, type(drawable), draw_command))
                
                #Because these are stacks, don't bother with getting axes and setting titles, just choose whether
                #it needs both the x and y axes or just y axis (to avoid many x axis titles being drawn)
                if pn == (len(CanCache["subplots"]) - 1):
                    if xAxisTitle != None and yAxisTitle != None:
                        drawable.SetTitle(";{};{}".format(xAxisTitle, yAxisTitle))
                    elif xAxisTitle != None:
                        drawable.SetTitle(";{};{}".format(xAxisTitle, ""))
                    elif yAxisTitle != None:
                        drawable.SetTitle(";{};{}".format("", yAxisTitle))
                    else:
                        drawable.SetTitle(";{};{}".format("", ""))
                else:
                    if yAxisTitle != None:
                        drawable.SetTitle(";;{}".format(yAxisTitle))
                    else:
                        drawable.SetTitle(";;{}".format(""))

                #increment our counter
                if "data" in super_cat_name.lower() and "blind" in drawable.GetName().lower() and subplot_dict.get("Unblind", False) == False:
                    pass
                else:
                    drawable.Draw(draw_command)
                    dn += 1
            if pn == 0:
                #Draw the legend in the first category for now...
                CanCache["subplots/supercategories"][pn]["Legend"].Draw()
                scaleText = 1.3
                offsetText = CanCache["canvas/marginL"]
                CanCache["cms_label"].Draw()
                #Draw the label on the leftmost top pad
                #CanCache["cms_label"].Draw()
                #Set the y axis title
                #####drawable.SetTitle(yAxisTitle)
                pass
            elif pn == len(CanCache["subplots"]):
                scaleText = 0.6
                #scaleText = (1-CanCache["canvas/marginR"])
                offsetText = 0
                CanCache["cms_header"].Draw()
                #####drawable.SetTitle(yAxisTitle)
                pass
            else:
                scaleText = 2.0
                offsetText = 0
            if doLogY:
                CanCache["canvas/upperPads"][pn].SetLogy()
                
            #Create the subpad label, to be drawn. Text stored in CanCache["sublabels"] which should be a list, possibly a list of tuples in the future
            CanCache["subplots/labels"].append(ROOT.TLatex())
            #padArea = (CanCache["canvas/xEdgesHigh"][pn] - CanCache["canvas/xEdgesLow"][pn])*(CanCache["canvas/yEdgesHigh"][-1] - CanCache["canvas/yEdgesLow"][-1])
            #padWidth = (CanCache["canvas/xEdgesHigh"][pn] - CanCache["canvas/xEdgesLow"][pn])
            #CanCache["subplots/labels"][-1].SetTextSize(0.5*scaleText) #.04?
            CanCache["subplots/labels"][-1].SetTextSizePixels(int(0.05*xPixels)) #.04?
            CanCache["subplots/labels"][-1].DrawLatexNDC(0.10 + offsetText, 0.78, "{}".format(CanCache["sublabels"][pn]))
            CanCache["subplots/labels"][-1].Draw()
            
            #Draw the pad
            CanCache["canvas/upperPads"][pn].Draw()
            #Now do the ratio plots, if requested
            CanCache["canvas/lowerPads"][pn].cd()
            CanCache["canvas/lowerPads"][pn].SetGridy()
            if doRatio:
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
                    color = aRatio.get("Color", None)
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
                    _ = createRatio(num_hist, den_hist, Cache = CanCache["subplots/ratios"][-1][aRatioName], ratioTitle = aRatioName, 
                                    ratioColor = color, ratioStyle = style, ratioMarkerStyle = markerStyle, ratioAlpha = alpha,
                                    yMin = ratioYMin, yMax = ratioYMax, isBlinded=isBlinded, scaleText=scaleText, nDivisions=nDivisions)
                    #ratio_draw_command = legendConfig["Supercategories"][num]["Draw"]
                    ratio_draw_command = aRatio.get("Draw", "PXE1")
                    ratio_draw_command
                    if rdn > 0:
                        ratio_draw_command += " SAME"
                    CanCache["subplots/ratios"][-1][aRatioName]["ratio_hist"].Draw(ratio_draw_command)
                    #Set the x axis title if it's the last drawable item
                    if pn == (len(CanCache["subplots"]) - 1):
                        if xAxisTitle != None:
                            CanCache["subplots/ratios"][-1][aRatioName]["ratio_Xaxis"].SetTitle(xAxisTitle)
                    #increment our counter for ratios
                    rdn += 1
                #FIXME: better would be to make the Supercategory "blindable" instead of assuming 'data' is in the name
            #Draw the pad regardless, for consistency
            CanCache["canvas/lowerPads"][pn].Draw() 
        #Return to the main canvas
        CanCache["canvas"].cd()
        #Fill in integrals for super categories, and set the minima/maxima per pad
        padWidth = (1.0 - CanCache["canvas/bordersL"] - CanCache["canvas/bordersR"])/nXPads
        drawPoint = CanCache["canvas/marginL"]*0.33
        for pn in xrange(len(CanCache["subplots/integrals"])):
            tmp = ROOT.TLatex()
            tmp.SetTextSize(0.016)
            tmpString = "#splitline"
            for super_cat_name, str_integral in CanCache["subplots/integrals"][pn].items():
                if "data" in super_cat_name.lower(): continue
                tmpString += "{" + "{} : {}".format(super_cat_name, str_integral) + "}"
            tmp.DrawLatexNDC(drawPoint, 0.02, tmpString)
            drawPoint += padWidth
        #Modify the vertical axes now that we have the first drawn object, and each maximum and minima.
        if doLogY:
            canvasMin = min(CanCache["subplots/minima"] + [10e-3])
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
        ROOT.gStyle.SetOptTitle(1);
        #CanCache["canvas_title"] = ROOT.TPaveLabel(.25,.95,.6,.99, canTitle,"trndc");
        CanCache["canvas_title"] = ROOT.TLatex()
        canTitlePerc = 0.2
        CanCache["canvas_title"].SetTextSizePixels(int(canTitlePerc*xPixels))
        CanCache["canvas_title"].DrawLatexNDC(0.5 - len(canTitle)/80.0, 0.95, str(canTitle))
        CanCache["canvas_title"].Draw()
        #CanCache["cms_label"].Draw()
        CanCache["canvas"].Draw()
        if pdfOutput != None and can_num == 1: #count from 1 since we increment at the beginning of the loop on this one
            print("Opening {}".format(pdfOutput))
        print("\tDrew {}".format(can_name))
        if pdfOutput != None:
            if can_num == 1 and can_num != can_max: #count from 1 since we increment at the beginning of the loop on this one
                #print(CanCache["canvas"])
                CanCache["canvas"].SaveAs("{}(".format(pdfOutput))
            elif can_num == can_max and can_num != 1:
                print("Closing {}".format(pdfOutput))
                CanCache["canvas"].SaveAs("{})".format(pdfOutput))
            else:
                CanCache["canvas"].SaveAs("{}".format(pdfOutput))
        #for f in CanCache["subplots/files"]:
        #    f.Close()
        if macroOutput != None:
                CanCache["canvas"].SaveAs("{}".format(macroOutput))
        if pngOutput != None:
            CanCache["canvas"].SaveAs("{}".format(pngOutput))

        #Save histograms for Combine, this is a hacked first attempt, might be cleaner to create a dictionary of histograms with keys from the histogram name to avoid duplicates/cycle numbers in the root files.
        if combineOutput!= None and ("HT" in can_name):
            if "signalSensitive_HT" in can_name: continue
            if "nBtag2p" in can_name: continue
            for i in xrange(len(CanCache["subplots/supercategories"])):
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
                    #BLINDData___HT500_nMediumDeepJetB4+_nJet8+___HT___nom
                    combProcess, combCategory, combVariable, combSystematic = hist.GetName().split(separator)
                    combSystematics[processName].append(combSystematic)
                    #combProcess.replace("BLIND", "").replace("Data", "data_obs")
                    combVariables[processName].append(combVariable)
                    combCategories[processName].append(combCategory.replace("+", "p"))
                    histName = "___".join([combProcess.replace("BLIND", "").replace("Data", "data_obs"), 
                                           combCategory.replace("+", "p"), 
                                           combVariable, 
                                           combSystematic])
                    combHist = hist.Clone(histName)
                    if "BLIND" in combProcess:
                        print("Blinding histogram for Combine")
                        combHist = hist.Clone(hist.GetName().replace("Data", "data_obs").replace("+", "p").replace("BLIND", ""))
                        combHist.SetDirectory(0)
                        for combBin in xrange(combHist.GetNbinsX() + 2):
                            combHist.SetBinContent(combBin, 0); combHist.SetBinError(combBin, 0)
                    combHistograms[processName].append(combHist)
            for sys in CanCache["subplots/supercategories/systematics"].keys():
                for i in xrange(len(CanCache["subplots/supercategories/systematics"][sys])):
                    for preProcessName, hist in CanCache["subplots/supercategories/systematics"][sys][i]['Categories/hists'].items():
                        processName = preProcessName.replace("BLIND", "").replace("Data", "data_obs")
                        if processName not in combSystematics:
                            combSystematics[processName] = []
                        if processName not in combVariables:
                            combVariables[processName] = []
                        if processName not in combCategories:
                            combCategories[processName] = []
                        if processName not in combHistograms:
                            combHistograms[processName] = []
                        #BLINDData___HT500_nMediumDeepJetB4+_nJet8+___HT___nom
                        combProcess, combCategory, combVariable, combSystematic = hist.GetName().split(separator)
                        #Remap systematic names for decorrelation in Higgs Combine
                        #Decorrelated systematics: mu(Factorization/Renormalization) scale and ISR, FSR usually correlated (qcd vs ewk like ttbar vs singletop) unless
                        # " the analysis is too sensitive to off-shell effects" https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopSystematics#Factorization_and_renormalizatio
                        if processName in  ["ttbb", "ttother", "ttnobb"]:
                            if combSystematic in ["muRNomFDown", "muRNomFUp", "muFNomRDown", "muFNomRUp", "ISRDown", "ISRUp", "FSRDown", "FSRUp"]:
                                combSystematic = "tt" + combSystematic
                            elif combSystematic in ["muRFcorrelatedDown", "muRFcorrelatedUp",]:
                                combSystematic = combSystematic.replace("muRFcorrelated", "ttmuRFcorrdNew")
                        elif processName in ["DY"]:
                            if combSystematic in ["muRNomFDown", "muRNomFUp", "muFNomRDown", "muFNomRUp", "ISRDown", "ISRUp", "FSRDown", "FSRUp"]: 
                                combSystematic = "ewk" + combSystematic
                            elif combSystematic in ["muRFcorrelatedDown", "muRFcorrelatedUp",]:
                                combSystematic = combSystematic.replace("muRFcorrelated", "ewkmuRFcorrdNew")
                        else:
                            if combSystematic in ["muRNomFDown", "muRNomFUp", "muFNomRDown", "muFNomRUp", "ISRDown", "ISRUp", "FSRDown", "FSRUp"]: 
                                combSystematic = processName + combSystematic
                            elif combSystematic in ["muRFcorrelatedDown", "muRFcorrelatedUp",]:
                                combSystematic = combSystematic.replace("muRFcorrelated", processName + "muRFcorrdNew")
                            
                        combSystematics[processName].append(combSystematic)
                        combVariables[processName].append(combVariable)
                        combCategories[processName].append(combCategory.replace("+", "p"))
                        histName = "___".join([combProcess.replace("BLIND", "").replace("Data", "data_obs"), 
                                               combCategory.replace("+", "p"), 
                                               combVariable, 
                                               combSystematic])
                        combHist = hist.Clone(histName)
                        #No data histograms for systematic variations... 
                        if "Data" in combProcess: continue
                        combHistograms[processName].append(combHist)
    combHistogramsFinal = {}
    for processName in combSystematics.keys():
        combSystematics[processName] = list(set(combSystematics[processName]))
        combVariables[processName] = list(set(combVariables[processName]))
        combCategories[processName] = list(set(combCategories[processName]))
        combHistogramsFinal[processName] = dict([(h.GetName(), h) for h in combHistograms[processName]])
    if combineOutput != None:
        combFile = ROOT.TFile.Open(combineOutput, "recreate")
        for processName, processDict in combHistogramsFinal.items():
            for histName, hist in processDict.items():
                hist.Write()
        combFile.Close()
    if closeFiles == True:
        for fo in fileDict.values():
            fo.Close()
        return "Files Closed"
    else:
        return Cache

#DrawFrame is TH1/THStack/TPad method to just draw the axes

catsForSplitStitching={"nocat":[""]}
varsForSplitStitching=['el_eta', 'GenHT', 'nGenJet', 'jet5_eta', 'mu_eta', 'jet1_pt', 
                       'mu_pt', 'el_pt', 'HT', 'jet1_eta', 'jet5_pt', 'nGenLep', 'nJet']
nSplit=generateJSON(modelPlotJSON_SPLITSTITCH, varsForSplitStitching, 
                    categories_dict=catsForSplitStitching, name_format="Plot_diagnostic___{var}", 
                    channel="")
nSplit.update(defaultNoLegend)
if False:
    # with open("/eos/user/n/nmangane/analysis/Nominal_Zvtx/Diagnostics/NoChannel/plots.json", "w") as jo:
    with open("/eos/user/n/nmangane/analysis/SplitProcessTest/Diagnostics/NoChannel/plots.json", "w") as jo:
        jo.write(json.dumps(nSplit, indent=4))


replacementLegend1=None
replacementLegend2=None
replacementLegend3=None
replacementLegend4=None
replacementLegend5=None
resultsS_DL = None
resultsMS_DL = None
resultsRS_DL = None
resultsS_SL = None
resultsMS_SL = None
resultsRS_SL = None
# base="/eos/user/n/nmangane/analysis/Nominal_Zvtx/Diagnostics/NoChannel"
base="/eos/user/n/nmangane/analysis/SplitProcessTest/Diagnostics/NoChannel"
with open("{}/stitchedDL.json".format(base), "r") as jlegend1:
    replacementLegend1 = copy.copy(json_load_byteified(jlegend1))
with open("{}/multistitchedDL.json".format(base), "r") as jlegend2:
    replacementLegend2 = copy.copy(json_load_byteified(jlegend2))
# with open("{}/restitchedDL.json".format(base), "r") as jlegend3:
#     replacementLegend3 = copy.copy(json_load_byteified(jlegend3))
with open("{}/multistitchedSL.json".format(base), "r") as jlegend4:
    replacementLegend4 = copy.copy(json_load_byteified(jlegend4))
with open("{}/multistitchedSL.json".format(base), "r") as jlegend5:
    replacementLegend5 = copy.copy(json_load_byteified(jlegend5))
# with open("{}/restitchedSL.json".format(base), "r") as jlegend6:
#     replacementLegend6 = copy.copy(json_load_byteified(jlegend6))
with open("{}/plots.json".format(base), "r") as j1:
    loadedJSON1 = json_load_byteified(j1)
    loadedJSON2 = copy.copy(loadedJSON1)
    loadedJSON3 = copy.copy(loadedJSON1)
    loadedJSON4 = copy.copy(loadedJSON1)
    loadedJSON5 = copy.copy(loadedJSON1)
    loadedJSON6 = copy.copy(loadedJSON1)
    loadedJSON1.update(replacementLegend1)
    loadedJSON2.update(replacementLegend2)
    # loadedJSON3.update(replacementLegend3)
    loadedJSON4.update(replacementLegend4)
    loadedJSON5.update(replacementLegend5)
    # loadedJSON3.update(replacementLegend6)
    #Plot results stitching unfiltered + filtered, using filtered sample exclusively in its phase space
    # resultsS_SL = loopPlottingJSON(loadedJSON1, Cache=None, directory="{}".format(base), batchOutput=True, 
    #                             pdfOutput="{}/stitchedDL.pdf".format(base), verbose=False, nominalPostfix=None)
    #Plot results stitching unfiltered + filtered, using both nominal and filtered samples weighted proportional to their number of net simulated events (N_+ - N_-)
    # resultsMS_SL= loopPlottingJSON(loadedJSON2, Cache=None, directory="{}".format(base), batchOutput=True,
    #                            pdfOutput="{}/multistitchedDL.pdf".format(base), verbose=False, nominalPostfix=None)
    #Plot results stitching unfiltered only back together, to ensure perfect agreement with the nominal sample when not split
    # resultsRS_SL = loopPlottingJSON(loadedJSON3, Cache=None, directory="{}".format(base), batchOutput=True, 
    #                             pdfOutput="{}/restitchedDL.pdf".format(base), verbose=False, nominalPostfix=None)
    #Plot results stitching unfiltered + filtered, using filtered sample exclusively in its phase space
    # resultsS_SL = loopPlottingJSON(loadedJSON4, Cache=None, directory="{}".format(base), batchOutput=True, 
    #                             pdfOutput="{}/stitchedSL.pdf".format(base), verbose=False, nominalPostfix=None)
    #Plot results stitching unfiltered + filtered, using both nominal and filtered samples weighted proportional to their number of net simulated events (N_+ - N_-)
    # resultsMS_SL= loopPlottingJSON(loadedJSON5, Cache=None, directory="{}".format(base), batchOutput=True,
    #                            pdfOutput="{}/multistitchedSL.pdf".format(base), verbose=False, nominalPostfix=None)



new_test_dict = {"nJet_nBtag2":["HT500_ZWindowMET0Width0_nMediumDeepCSVB2_nJet4", "HT500_ZWindowMET0Width0_nMediumDeepCSVB2_nJet5", "HT500_ZWindowMET0Width0_nMediumDeepCSVB2_nJet6", "blind_HT500_ZWindowMET0Width0_nMediumDeepCSVB2_nJet7", "blind_HT500_ZWindowMET0Width0_nMediumDeepCSVB2_nJet8+"],
}
#newTestVars=["MET_pt", "MET_uncorr_pt", "MET_phi", "MET_uncorr_phi", "Jet_DeepCSVB_jet1", "MTofMETandEl", "MTofMETandMu", "MTofElandMu"]
newVarsMu=['Muon_phi_LeadLep', 'Muon_pfRelIso03_all', 'Muon_pfRelIso04_all', 'Muon_pt', 'Muon_eta_LeadLep', 
           'nLooseFTAMuon', 'Muon_InvMass', 'Muon_pt_SubleadLep', 'Muon_eta_SubleadLep', 
           'Muon_pfRelIso03_chg', 'Muon_phi_SubleadLep', 'nTightFTAMuon', 
           'nMediumFTAMuon', 'Muon_pt_LeadLep']
newVarsEl=['nMediumFTAElectron', 'Electron_InvMass', 'Electron_eta_SubleadLep', 'nTightFTAElectron', 
           'Electron_eta_LeadLep', 'Electron_phi_LeadLep', 'Electron_pt_SubleadLep', 'nLooseFTAElectron', 
           'Electron_phi_SubleadLep', 'Electron_pt', 'Electron_pt_LeadLep', 'Electron_pfRelIso03_all', 
           'Electron_pfRelIso03_chg']
newVarsMET=['MTofMETandEl', 'MTofMETandMu', 'MET_phi', 'MET_uncorr_pt', 'Muon_InvMass_v_MET', 'MET_uncorr_phi', 
            'MET_pt', 'Electron_InvMass_v_MET']
newVarsJet=['Jet_phi_jet5', 'Jet_phi_jet4', 'Jet_phi_jet3', 'Jet_phi_jet2', 'Jet_phi_jet1', 'nJet_LooseDeepCSV', 'Jet_DeepCSVB_sortedjet3', 'nJet_TightDeepCSV', 
            'Jet_DeepJetB_sortedjet1', 'Jet_DeepJetB_sortedjet3', 'Jet_DeepJetB_sortedjet2', 'Jet_DeepJetB_sortedjet5', 'Jet_DeepJetB_sortedjet4', 
            'Jet_pt_jet3', 'Jet_pt_jet2', 'Jet_pt_jet1', 'Jet_pt_jet5', 'Jet_pt_jet4', 'Jet_DeepCSVB_jet1', 'Jet_DeepCSVB_jet3', 'Jet_DeepCSVB_jet2', 
            'Jet_DeepCSVB_jet5', 'Jet_DeepCSVB_jet4', 'Jet_eta_jet1', 'Jet_eta_jet2', 'Jet_eta_jet3', 'Jet_eta_jet4', 'Jet_eta_jet5', 
            'Jet_DeepCSVB_sortedjet4', 'Jet_DeepCSVB_sortedjet5', 'Jet_DeepCSVB_sortedjet1', 'Jet_DeepCSVB_sortedjet2', 'Jet_DeepJetB_jet4', 
            'Jet_DeepJetB_jet5', 'Jet_DeepJetB_jet1', 'Jet_DeepJetB_jet2', 'Jet_DeepJetB_jet3', 'nJet', 'nJet_MediumDeepCSV']
newVarsEvent=["HT", "H", "HT2M", "H2M", "HTb", "HTH", "HTRat", "dRbb", "dPhibb", "dEtabb"]

nMu = generateJSON(modelPlotJSON_CAT, newVarsMu, categories_dict=new_test_dict, channel="ElMu")
nEl = generateJSON(modelPlotJSON_CAT, newVarsEl, categories_dict=new_test_dict, channel="ElMu")
nMET = generateJSON(modelPlotJSON_CAT, newVarsMET, categories_dict=new_test_dict, channel="ElMu")
nJet = generateJSON(modelPlotJSON_CAT, newVarsJet, categories_dict=new_test_dict, channel="ElMu")
nEvent = generateJSON(modelPlotJSON_CAT, newVarsEvent, categories_dict=new_test_dict, channel="ElMu")
nMu.update(defaultAndLegends)
nEl.update(defaultAndLegends)
nMET.update(defaultAndLegends)
nJet.update(defaultAndLegends)
nEvent.update(defaultAndLegends)
# folder="/eos/user/n/nmangane/analysis/Apr-22-2020/Histograms/ElMu"
# folder="/eos/user/n/nmangane/analysis/SplitProcessTest/Diagnostics/All"
folder="/eos/user/n/nmangane/analysis/July2/Histograms"
if False:
    with open("{}/newMu.json".format(folder), "w") as jo:
        jo.write(json.dumps(nMu, indent=4))
    with open("{}/newEl.json".format(folder), "w") as jo:
        jo.write(json.dumps(nEl, indent=4))
    with open("{}/newMET.json".format(folder), "w") as jo:
        jo.write(json.dumps(nMET, indent=4))
    with open("{}/newJet.json".format(folder), "w") as jo:
        jo.write(json.dumps(nJet, indent=4))
    with open("{}/newEvent.json".format(folder), "w") as jo:
        jo.write(json.dumps(nEvent, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for plotting FourTop analysis histograms in mountain-ranges, using configuration (json) cards')
    parser.add_argument('stage', action='store', type=str, choices=['generate-plotCard', 'generate-legendCard', 'plot-histograms', 'plot-diagnostics',
                                                                    'prepare-combine'],
                        help='plotting stage to be produced')
    parser.add_argument('--relUncertainty', dest='relUncertainty', action='store', type=float, default=0.3,
                        help='maximum relative uncertainty (sqrt(N)/N) per bin used as the criteria for merging, should be on unweighted histograms')
    parser.add_argument('-c', '--channel', dest='channel', action='store', type=str, default="ElMu", choices=['ElMu', 'ElEl', 'MuMu', 'ElEl_LowMET', 
                                                                                                              'ElEl_HighMET', 'MuMu_ElMu','MuMu_ElMu_ElEl', 'All'],
                        help='Decay channel for opposite-sign dilepton analysis')
    parser.add_argument('-d', '--analysisDirectory', dest='analysisDirectory', action='store', type=str, default="/eos/user/$U/$USER/analysis/$DATE",
                        help='analysis directory where btagging yields, histograms, etc. are stored')
    parser.add_argument('-f', '--formats', dest='formats', action='append', choices=['pdf', 'C', 'png', 'combine'],
                        help='Formats to save plots as, supporting subset of ROOT SaveAs() formats: pdf, C macro, png')
    parser.add_argument('-p', '--plotCard', dest='plotCard', action='store', type=str, default="$ADIR/Histograms/All/plots.json",
                        help='input plotting configuration, defaulting to "$ADIR/Histograms/All/plots.json"')
    parser.add_argument('-l', '--legendCard', dest='legendCard', action='store', type=str, default="$ADIR/Histograms/All/legend.json",
                        help='input legend configuration, defaulting to "$ADIR/Histograms/All/legend.json". This card controls the grouping of histograms into categories and supercategories, colors, stacking, sample-scaling, etc.')
    parser.add_argument('--era', dest='era', type=str, default="2017",
                        help='era for plotting, which deduces the lumi only for now')
    parser.add_argument('--vars', '--variables', dest='variables', action='store', default=None, type=str, nargs='*',
                        help='List of variables for generating a plotcard')
    parser.add_argument('--nJets', '--nJetCategories', dest='nJetCategories', action='store', default=None, type=str, nargs='*',
                        help='List of nJet categories for generating a plotcard, i.e. "nJet4 nJet5 nJet6p"')
    parser.add_argument('--nBTags', '--nBTagCategories', dest='nBTagCategories', action='store', default=None, type=str, nargs='*',
                        help='List of nBTag categories for generating a plotcard, i.e. "nMediumDeepJetB2 nMediumDeepJetB3 nMediumDeepJetB4p"')
    parser.add_argument('--noBatch', dest='noBatch', action='store_true',
                        help='Disable batch output and attempt to draw histograms to display')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')
    parser.add_argument('--useCanvasMax', dest='useCanvasMax', action='store_true',
                        help='use the Canvas card\' maximum rather than 110% of the subplots\' maxima')
    

    #Parse the arguments
    args = parser.parse_args()
    #Get the username and today's date for default directory:
    uname = pwd.getpwuid(os.getuid()).pw_name
    uinitial = uname[0]
    dateToday = datetime.date.today().strftime("%b-%d-%Y")
    stage = args.stage
    channel = args.channel
    era = args.era
    variables = args.variables
    nJets = args.nJetCategories
    nBTags = args.nBTagCategories
    doBatch = not args.noBatch
    verb = args.verbose
    useCanvasMax = args.useCanvasMax
    analysisDir = args.analysisDirectory.replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday).replace("$CHAN", channel)

    lumiDict = {"2017": 41.53,
                "2018": 59.97}
    lumi = lumiDict.get(era, "N/A")
if stage == 'plot-histograms' or stage == 'plot-diagnostics' or stage == 'prepare-combine':    
    plotConfig = args.plotCard.replace("$ADIR", analysisDir).replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday).replace("$CHAN", channel).replace("//", "/")
    legendConfig = args.legendCard.replace("$ADIR", analysisDir).replace("$USER", uname).replace("$U", uinitial).replace("$DATE", dateToday).replace("$CHAN", channel).replace("//", "/")
    tag = analysisDir.split("/")[-1]
    plotCardName = plotConfig.split("/")[-1]
    plotcard = plotCardName.replace(".json", "")
    legendCardName = legendConfig.split("/")[-1]
    legendcard = legendCardName.replace(".json", "")

    if os.path.isdir(analysisDir):
        jsonDir = "$ADIR/jsons".replace("$ADIR", analysisDir).replace("//", "/")
        plotDir = "$ADIR/Plots".replace("$ADIR", analysisDir).replace("//", "/")
        if stage == 'plot-histograms':
            histogramDir = "$ADIR/Histograms/All".replace("$ADIR", analysisDir).replace("//", "/")
        elif stage == 'plot-diagnostics':
            histogramDir = "$ADIR/Diagnostics/NoChannel".replace("$ADIR", analysisDir).replace("//", "/")
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
            print("plotcard = {}".format(plotcard))
            
        if 'pdf' in args.formats:
            pdfOut = "$ADIR/Plots/$TAG_$PLOTCARD_$CHAN.pdf".replace("$ADIR", analysisDir).replace("$TAG", tag).replace("$PLOTCARD", plotcard).replace("$CHAN", channel).replace("//", "/")
            if verb:
                print("pdfOutput = {}".format(pdfOut))
        if 'combine' in args.formats:
            combineOut = "$ADIR/Combine/combTest_$CHAN.root".replace("$ADIR", analysisDir).replace("$TAG", tag).replace("$PLOTCARD", plotcard).replace("$CHAN", channel).replace("//", "/")
            if verb:
                print("pdfOutput = {}".format(pdfOut))
        else:
            combineOut = None
        resultsDict = loopPlottingJSON(loadedPlotConfig, Cache=None, histogramDirectory=histogramDir, batchOutput=doBatch, pdfOutput=pdfOut, 
                                       combineOutput=combineOut, lumi=lumi, useCanvasMax=useCanvasMax, verbose=verb);
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
    
    thePlotCard = generateJSON(models["v0.8"], variables, categories_dict=categories_dict,channel=channel, 
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
   
