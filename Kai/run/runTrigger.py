#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from FourTopNAOD.Kai.modules.trigger import Trigger

#Trigger+preselection module, for MC studies
preselection="(nElectron + nMuon) > 1 && nJet > 3"
triggers=["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
          "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
          "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
          "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
          "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"
          ]

testfile=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TT_DiLept_TuneCP5_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/280000/F77DF374-A98D-F146-A8B6-E93C69D646E4.root"]
p=PostProcessor("../run",testfile, cut=preselection, modules=[Trigger(triggers)],provenance=True,fwkJobReport=True,jsonInput=None)
p.run()

