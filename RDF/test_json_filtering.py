import os, sys
import ROOT
ROOT.gSystem.SetIncludePath("-I{}".format(os.path.abspath(os.path.dirname(__file__))))
ROOT.gROOT.ProcessLine(".L LumiMask.cc")
myLumiMaskName="myLumiMask"
ROOT.gROOT.ProcessLine("const auto {lumiMask} = LumiMask::fromJSON(\"../Kai/python/jsons/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt\")".format(lumiMask=myLumiMaskName))
if hasattr(ROOT, myLumiMaskName):
    mask = getattr(ROOT, myLumiMaskName)

try:
    #"315257": [[1, 88], [91, 92]]
    print("This should be True:", mask.accept(315257, 87))
    print("This should be False:", mask.accept(315257, 90))
except:
    print("No go monopoly guy!")
