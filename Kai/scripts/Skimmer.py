from __future__ import division, print_function
import os, sys, time
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.common.lepSplitSFProducer import *
from FourTopNAOD.Kai.tools.toolbox import *
import collections, copy, json, math
from array import array
import multiprocessing
import inspect
import argparse
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='Skimmer for selecting branches and implementing cutstring on NanoAOD files')
parser.add_argument('--output', dest='output', action='store', type=str, default="DefaultSkim.root",
                    help='output file name')
parser.add_argument('--outDirectory', dest='outDirectory', action='store', type=str,
                    help='output directory path for usage with postfix option')
parser.add_argument('--postfix', dest='postfix', action='store', type=str,
                    help='postfix file name, which will also store the files in the same directory as they were input from')
parser.add_argument('--input', dest='input', action='store', type=str,
                    help='for globbable input, a string prepended with "glob:", else for das querying, "dbs:"')
parser.add_argument('--cut', dest='cut', action='store', type=str, default="",
                    help='cutstring valid for TTree::Draw()')
parser.add_argument('--keepdrop', dest='keepdrop', action='store', type=str, default=None,
                    help='path to keepdrop text file for the PostProcessor')
args = parser.parse_args()

Tuples = []
tmp = args.input
if "glob:" in args.input or "dbs:" in args.input:
    print("executing command: getFiles(query='{}', verbose=True)".format(args.input))
    files=getFiles(query="{}".format(tmp), verbose=True)
    # print("sleeping for 150s to prevent overzealous execution")
    # time.sleep(150)
    print(files)
else:
    files=[args.input]
output = "{}".format(args.output)
if ".root" not in output:
    output += ".root"
if args.postfix == None:
    writeLocation = "/tmp/nmangane/{}/".format(args.output.replace(".root", ""))
    haddName = output
else:
    writeLocation = args.outDirectory
    haddName = None
print("Will run over these files: {}".format(files))
print("Will use this output directory: {} \nWill use this haddName: {}\n Will use this postfix: {}".format(writeLocation, haddName, args.postfix))
p=PostProcessor(writeLocation,
                files,
                cut=args.cut,
                branchsel=args.keepdrop,
                outputbranchsel=args.keepdrop,
                modules=[],
                noOut=False,
                postfix=args.postfix,
                haddFileName=haddName,
                maxEntries=None,
                # histFileName=hName,
                # histDirName=hDirName,
)
print("The output: {}".format(args.output))
p.run()
