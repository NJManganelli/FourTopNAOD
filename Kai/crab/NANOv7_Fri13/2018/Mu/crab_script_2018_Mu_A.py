#!/usr/bin/env python
import os, time, collections, copy, json, multiprocessing
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *
from FourTopNAOD.Kai.modules.LeptonSkimmer import *
from FourTopNAOD.Kai.modules.JetMETSkimmer import *
isData = True
isUltraLegacy = False
era = "2018"
subera = "A"
thePreselection = None
crossSection = None
equivLumi = 59.97
nEventsPositive = None
nEventsNegative = None
sumWeights = None
TriggerChannel = "Mu"
JESUnc = "Merged" # options: "All", "Merged", "Total"

theFiles = inputFiles()
GoldenJSON = {"2016": {"non-UL": "Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt",
                       "UL": "Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
                   },
              "2017": {"non-UL": "Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt",
                       "UL": "Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt"
                   },
              "2018": {"non-UL": "Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt",
                       "UL": "Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"
                   }
          }

if isData:
    theLumis = os.path.join(os.environ["CMSSW_BASE"], "python/FourTopNAOD/Kai/jsons", GoldenJSON.get(era).get("UL" if isUltraLegacy else "non-UL"))
    print("Loading Golden Json: {}".format(theLumis))
    if not os.path.isfile(theLumis):
        theLumis = os.path.join(os.environ["CMSSW_BASE"], "src/FourTopNAOD/Kai/python/jsons", GoldenJSON.get(era).get("UL" if isUltraLegacy else "non-UL"))
        if not os.path.isfile(theLumis):
            raise RuntimeError("Valid GoldenJSON file not found, if running on CRAB try a new scram build before resubmitting")
else:
    theLumis = None
moduleCache = []
if not isData: 
    if era == "2016": 
        moduleCache.append(puWeight_2016())
    elif era == "2017": 
        moduleCache.append(puWeight_2017())
    elif era == "2018": 
        moduleCache.append(puWeight_2018())
    else:
        raise RuntimeError("Unexpected era identifier {}".format(era))
    
    if JESUnc in ["All", "Merged"]: #btag POG provides all JEC unc sources, except for RelativeSample
        btagjes_sources = ['jes', 'jesAbsoluteMPFBias', 'jesAbsoluteScale', 'jesAbsoluteStat', 'jesFlavorQCD', 'jesFragmentation', 'jesPileUpDataMC', 'jesPileUpPtBB', 'jesPileUpPtEC1', 'jesPileUpPtEC2', 'jesPileUpPtHF', 'jesPileUpPtRef', 'jesRelativeBal', 'jesRelativeFSR', 'jesRelativeJEREC1', 'jesRelativeJEREC2', 'jesRelativeJERHF', 'jesRelativePtBB', 'jesRelativePtEC1', 'jesRelativePtEC2', 'jesRelativePtHF', 'jesRelativeStatEC', 'jesRelativeStatFSR', 'jesRelativeStatHF', 'jesSinglePionECAL', 'jesSinglePionHCAL', 'jesTimePtEta']
#    if JESUnc == "Merged": #no btag shape unc for regrouped JEC available, so use the total one ("jes") and the remaining single ones that are not grouped (see also: https://docs.google.com/spreadsheets/d/1Feuj1n0MdotcPq19Mht7SUIgvkXkA4hiB0BxEuBShLw/edit#gid=1345121349)
#        btagjes_sources = ['jes', 'jesFlavorQCD','jesPileUpPtEC2', 'jesRelativeBal']
    else:
        btagjes_sources = ['jes']

    moduleCache.append(btagSFProducer(era,
                                      algo="deepjet",
                                      selectedWPs=['M', 'shape_corr'],
                                      sfFileName=None, #Automatically deduced
                                      verbose=0,
                                      jesSystsForShape=btagjes_sources
                                  )
                   )
    moduleCache.append(btagSFProducer(era,
                                      algo="deepcsv",
                                      selectedWPs=['M', 'shape_corr'],
                                      sfFileName=None, #Automatically deduced
                                      verbose=0,
                                      jesSystsForShape=btagjes_sources
                                  )
                   )
#Need to make it into a function, so extra () pair...
jmeModule = createJMECorrector(isMC=(not isData), 
                               dataYear=int(era), 
                               runPeriod=subera if isData else None, 
                               jesUncert=JESUnc, 
                               jetType="AK4PFchs", 
                               noGroom=False, 
                               metBranchName="METFixEE2017" if era == "2017" else "MET",
                               applySmearing=True, 
                               isFastSim=False, 
                               applyHEMfix=True if era == "2018" and isUltraLegacy else False, 
                               splitJER=False, 
                               saveMETUncs=['T1', 'T1Smear']
                           )
moduleCache.append(jmeModule())
moduleCache.append(TriggerAndLeptonSkimmer('baseline',
                                           era=era,
                                           subera=subera,
                                           isData=isData,
                                           TriggerChannel=TriggerChannel,
                                           fillHists=False,
                                           mode="Flag",
                                       )
               )
moduleCache.append(JetMETSkimmer(jetMinPt=20.0,
                                 jetMaxEta=2.4 if era == "2016" else 2.5,
                                 jetMinID=0b010,
                                 jetMinCount=3,
                                 minPseudoHT=350,
                                 fillHists=False
                             )
               )
p=PostProcessor(".", 
                theFiles,       
                modules=moduleCache, 
                cut=thePreselection, 
                provenance=True, 
                fwkJobReport=True, 
                jsonInput=theLumis, 
                histFileName="hist.root",
                histDirName="plots",
                branchsel=None,
                outputbranchsel=None,
                compression="LZMA:9",
                friend=False,
                postfix=None,
                noOut=False,
                justcount=False,
                # haddFileName=None,
                maxEntries=None,
                firstEntry=0,
                prefetch=True,
                longTermCache=False
                )
p.run()
