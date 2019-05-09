from __future__ import division, print_function
#import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 

files=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/280000/95FE111B-F77C-FD44-904A-97A842868FC2.root"]

p=PostProcessor(".",
                files,
                cut=None,
                justcount=True,
                )

p.run()
