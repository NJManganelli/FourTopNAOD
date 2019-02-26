#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis
from FourTopNAOD.Kai.modules.eventselector import EventSelector
from FourTopNAOD.Kai.modules.trigger import Trigger

theConfig={
"Electron" : {
	     "Common" : {
	     	      "Eta" : 2.4,
		      "IdType" : "cutBased"
		      },
  	     "Select" : {
	     	      "Pt" : 25.0,
		      "IdLevel" : 2
		      },
	     "Veto" : {
	     	    "Pt" : 25.0,
		    "IdLevel" : 1
		    }
	     },
"Muon" : {
       "Common" : {
      		"Eta" : 2.4
		},
       "Select" : {
       		"Pt" : 20,
		"RelIso" : 0.15,
		"IdLevel" : "looseId"
		}
	 },
"Jet" : {
      "Common" : {
      	       "Eta" : 2.4,
	       "JetId" : 6
	       },
      "NonBJet" : {
      		"Pt" : 30.0
		},
      "BJet" : {
      	     "Pt" : 25.0
	     },
      "Algo" : "btagDeepB",
      "WP" : "Medium",
      "btagCSVV2" : { 
	     	  "Loose" : "FIXME", 
		  "Medium" : 0.8838, 
		  "Tight" : "FIXME"
		  },
      "btagDeepB" : { 
      		  "Loose" : "FIXME", 
		  "Medium" : 0.4941, 
		  "Tight" : "FIXME"
		  },
      "DeepFlav" : { 
      		 "Loose" : "FIXME", 
		 "Medium" : "FIXME", 
		 "Tight" : "FIXME"
		 },
      "CleanType" : "PartonMatching",
      "MaxDeltaR" : 0.4
      },
"HLT" : {
    "cutOnTrigs" : "False",
    "chMuMu" : ["Placeholder", "List", "of", "trigger", "names"],
    "chElMu" : ["Placeholder", "List", "of", "trigger", "names"],
    "chElEl" : ["Placeholder", "List", "of", "trigger", "names"]
    },
"PV" : { 
    "FIXME" : "Placeholder for Primary Vertex requirements" 
    },
"MET" : { 
    "cutOnFilts" : "False",
    "MinMET" : 50
    },
"Event" : {
    "HTMin" : 500,
    "nBJetMin" : 2,
    "nTotJetMin" : 4,
    "nSelLep" : 2,
    "nVetoLep" : 0,
    "LowMassReson" : {
        "Center" : 10.0, 
        "HalfWidth" : 10.0
        },
    "ZMassReson" : {
        "Center" : 91.0, 
        "HalfWidth" : 15.0
        }
    },
"InvertIsolation" : "False"	
}

print(theConfig)

#from  PhysicsTools.NanoAODTools.postprocessing.examples.exampleModule import * #Creates infinite loop with my modifications added in?

#Working crab processor, used to make samples Sergio used
# p=PostProcessor(".",inputFiles(), cut=None, modules=[EventSelector(selectionConfig=theConfig, makeHistos=False, cutOnMET=True, cutOnTrigs=False, cutOnHT=False)],provenance=True,fwkJobReport=True,jsonInput=runsAndLumis())
#p=PostProcessor(".",inputFiles(), cut=None, modules=[EventSelector(selectionConfig=theConfig, makeHistos=True, cutOnMET=True, cutOnTrigs=False, cutOnHT=False)],provenance=True,fwkJobReport=True,jsonInput=runsAndLumis(), histFileName="hist.root", histDirName="plots")

#Trigger+preselection module, for MC studies
preselection="(nElectron + nMuon) > 1 && nJet > 3"
triggers=["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
          "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
          "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
          "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
          "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"
          ]
p=PostProcessor(".",inputFiles(), cut=preselection, modules=[Trigger(triggers)],provenance=True,fwkJobReport=True,jsonInput=runsAndLumis())
#test this module locally
#testfile=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TT_DiLept_TuneCP5_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/280000/F77DF374-A98D-F146-A8B6-E93C69D646E4.root"]
#testfile2=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/10000/CED95035-252C-174B-9A58-B0A614732A7B.root"]
#p=PostProcessor("../run",testfile, cut=preselection, modules=[Trigger(triggers)],provenance=True,fwkJobReport=True,jsonInput=None)

p.run()

print "DONE"
os.system("ls -lR")

