#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

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
from  FourTopNAOD.Kai.modules.eventselector import *
p=PostProcessor(".",inputFiles(), cut=None, modules=[EventSelector(selectionConfig=theConfig, makeHistos=False, cutOnMET=True, cutOnTrigs=False, cutOnHT=False)],provenance=True,fwkJobReport=True,jsonInput=runsAndLumis())
#p=PostProcessor(".",inputFiles(), cut=None, modules=[EventSelector(selectionConfig=theConfig, makeHistos=True, cutOnMET=True, cutOnTrigs=False, cutOnHT=False)],provenance=True,fwkJobReport=True,jsonInput=runsAndLumis(), histFileName="hist.root", histDirName="plots")
p.run()

print "DONE"
os.system("ls -lR")

