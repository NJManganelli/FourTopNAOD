import ROOT 
from importlib import import_module

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

#Create a List [] with filenames as strings
files=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAOD/TTJets_SingleLeptFromT_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/00000/06CC0D9B-4244-E811-8B62-485B39897212.root"]

#Create a postprocessor, passing it the necessary and optional parameters
#Try running with justcount=True, and modifying the numbers in the cut=" " parameter string.
#Then, switch the justcount=False, and when it runs, it will produce a skim of NanoAOD with that number of events.
#Try opening the file in the command line with 'root -l 06CC0D9B-4244-E811-8B62-485B39897212_CH01-Skim.root'
#At the ROOT prompt, use 'new TBrowser' to get a GUI 
p=PostProcessor(".", #This tells the postprocessor where to write the ROOT files
                files,
                cut="nMuon > 0 && nJet > 5",
                modules=[],
                jsonInput={1 : [[10000, 10010]]}, #This json input limits the postprocessor to only events in run 1, and lumesections 10000 to 10010
                postfix="_CH01-Skim", #This will be attached to the end of the filename if it's output
                justcount=True, #When True, just counts events that pass the cut=" " and jsonInput criteria. When False, will let this produce a skim!
                )

#Up to this point, things have only been imported and defined. 
#Nothing gets processed until the postprocessor we've created (and named "p") has its run command invoked:
p.run()
