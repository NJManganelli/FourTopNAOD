import os, sys
import ROOT
#After doing:
#g++ -c -fPIC -o LumiMask.o LumiMask.cc $(root-config --libs --cflags)
#gcc -shared -o libLumiMask.so LumiMask.o
#Add the current location to include path for testing
ROOT.gSystem.SetIncludePath("-I{}".format(os.path.abspath(os.path.dirname(__file__))))
#Add the current location as dynamic library (.so) loading path
ROOT.gSystem.AddDynamicPath("{}".format(os.path.abspath(os.path.dirname(__file__))))
#print the exit code of trying to load the dynamic library
print(ROOT.gSystem.Load("libLumiMask.so"))
#Must still include the associated header
ROOT.gROOT.ProcessLine('#include "LumiMask.h"')

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


#print the exit code of trying to load the dynamic library
print(ROOT.gSystem.Load("libFTFunctions.so"))
#Must still include the associated header
ROOT.gROOT.ProcessLine('#include "FTFunctions.cpp"')
#Test the namespace FTA function unpackGenTtbarId
test = ROOT.FTA.unpackGenTtbarId(12153)
print(test)
