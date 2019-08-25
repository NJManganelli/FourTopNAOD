import collections
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

TriggerTuple = collections.namedtuple("TriggerTuple", "trigger era subera tier channel leadThresh subMuThresh")

class Trigger(Module):
    def __init__(self, Trigger):
        self.counting = 0
        self.maxEventsToProcess = -1
        self.Trigger = Trigger
        
    def beginJob(self, histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #First N events
        self.counting += 1 
        if -1 < self.maxEventsToProcess < self.counting:
            return False
        
        #run = getattr(event, "run")
        #evt = getattr(event, "event")
        #lumi = getattr(event, "luminosityBlock")
        
        for trig in self.Trigger:
            if hasattr(event, trig) and getattr(event, trig):
                #print(getattr(event, trig))
                return True
            #else:
                #print("No trigger fired")
        return False

class TriggerAndSelectionLogic(Module):
    def __init__(self, era="2017", subera=None, isData="False", TriggerChannel=None, fillHists=False):
        self.era = era
        self.subera = subera
        self.isData = isData
        #Options: "MuMu", "ElMu", "ElEl", "Mu"
        self.TriggerChannel = TriggerChannel
        self.fillHists = fillHists
        #TriggerTuple = collections.namedtuple("TriggerTuple", "trigger era subera tier channel leadThresh subMuThresh")
        self.TriggerList = [TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                                         era="2017",
                                         subera="B",
                                         tier=0,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8_v",
                                         era="2017",
                                         subera="CDEF",
                                         tier=0,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8_v",
                                         era="2017",
                                         subera="CDEF",
                                         tier=0,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v",
                                         era="2017",
                                         subera="BCDEF",
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v",
                                         era="2017",
                                         subera="BCDEF",
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=25,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v",
                                         era="2017",
                                         subera="BCDEF",
                                         tier=0,
                                         channel="ElEl",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=25,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu24_eta2p1_v",
                                         era="2017",
                                         subera="BCD",
                                         tier=1,
                                         channel="Mu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu27_v",
                                         era="2017",
                                         subera="BCD",
                                         tier=1,
                                         channel="Mu",
                                         leadMuThresh=30,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu27_v",
                                         era="2017",
                                         subera="EF",
                                         tier=1,
                                         channel="Mu",
                                         leadMuThresh=30,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_Ele35_WPTight_Gsf_v",
                                         era="2017",
                                         subera="BCDEF",
                                         tier=2,
                                         channel="El",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=15)]
        self.TrigDict = {"2016": {"Principal": {"MuMu": [],
                                                "ElMu": [],
                                                "ElEl": []
                                                },
                                  "Fallback": {"Mu": []}
                              },
                         "2017": {"Principal": {"MuMu": {"B": ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"],
                                                         "CDEF": ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8_v",
                                                                  "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8_v"]
                                                         },
                                                "ElMu": {"BCDEF": ["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v",
                                                               "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v"]
                                                         },
                                                "ElEl": {"BCDEF": ["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v"]
                                                         }
                                                }
                                  "Fallback": {"Mu": {"BCD": ["HLT_IsoMu24_eta2p1_v",
                                                                "HLT_IsoMu27_v"],
                                                      "EF": ["HLT_IsoMu27_v"]
                                                      }
                                               }
                              },
                         "2018": {"Principal": {"MuMu": {"ABCD": []
                                                         },
                                                "ElMu": {"ABCD": []
                                                         },
                                                "ElEl": {"ABCD": []
                                                         }
                                                }
                                  "Fallback": {"Mu": {"ABCD": []
                                                      }
                                               }
                              },
                     }
        
    def beginJob(self, histFile=None,histDirName=None):
        if self.fillHists == False:
            Module.beginJob(self, None, None)
        else:
            if histFile == None or histDirName == None:
                raise RuntimeError("fillHists set to True, but no histFile or histDirName specified")
            Module.beginJob(self,histFile,histDirName)
            self.stitch_PCond_nGenJets = ROOT.TH1D("stitch_PCond_nGenJets", "nGenJet (pt > 30) Pass condition (weightMagnitude={0}); nGenJets; Events".format(self.weightMagnitude), self.nGenJetBins, self.nGenJetMin, self.nGenJetMax)
            self.addObject(self.stitch_PCond_nGenJets)
            self.stitch_PCond_GenHT = ROOT.TH1D("stitch_PCond_GenHT", "GenHT (pt > 30, |#eta| < 2.4) Pass condition (weightMagnitude={0}); Gen HT (GeV); Events".format(self.weightMagnitude), self.HTBins, self.HTMin, self.HTMax)
            self.addObject(self.stitch_PCond_GenHT)
            self.stitch_PCond_nGenLeps = ROOT.TH1D("stitch_PCond_nGenLeps", "nGenLeps (LHE level) Pass condition (weightMagnitude={0}); nGenLeps; Events".format(self.weightMagnitude), self.nGenLepBins, self.nGenLepMin, self.nGenLepMax)
            self.addObject(self.stitch_PCond_nGenLeps)
            self.stitch_PCond_2DJetHT = ROOT.TH2D("stitch_PCond_2DJetHT", "nGenJets, GenHT  Fail condition (weightMagnitude={0}); nGenJets; GenHT ".format(self.weightMagnitude),
                                                  self.nGenJetBins, self.nGenJetMin, self.nGenJetMax, self.HTBins, self.HTMin, self.HTMax)
            self.addObject(self.stitch_PCond_2DJetHT)
            self.stitch_PCond_AllVar = ROOT.TH3D("stitch_PCond_AllVar", "nGenLeps, nGenJets, GenHT Pass condition (weightMagnitude={0}); nGenLeps; nGenJets; GenHT ".format(self.weightMagnitude), 
                                                 self.nGenLepBins, self.nGenLepMin, self.nGenLepMax, self.nGenJetBins, self.nGenJetMin, self.nGenJetMax, self.HTBins, self.HTMin, self.HTMax)
            self.addObject(self.stitch_PCond_AllVar)


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
        #run = getattr(event, "run")
        #evt = getattr(event, "event")
        #lumi = getattr(event, "luminosityBlock")
        
        for trig in self.Trigger:
            # if hasattr(event, trig) and getattr(event, trig):
            if getattr(event, trig, False):
                #print(getattr(event, trig))
                return True
            #else:
                #print("No trigger fired")
        return False

############## Trigger information
#### 2018 ####
# #Run2018A [315264,315974)
# Muon 
# HLT_IsoMu24_v 
# L1_SingleMu22 
# SingleMuon PD 

# Double electron 
# HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL(_DZ)_v 
# L1_SingleEG* OR L1_DoubleEG_22_10 OR L1_DoubleEG_25_12 OR L1_DoubleEG_25_14 OR L1_DoubleEG_LooseIso23_10 OR L1_DoubleEG_LooseIso24_10 
# EGamma PD. Both DZ and non DZ versions unprescaled 

# Double Muon 
# HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ(_Mass3p8/8)_v 
# L1_DoubleMu_12_5 OR L1_DoubleMu_15_7 
# DoubleMuon PD. Only DZ_MassX versions unprescaled!! 

# Muon + Electron (1)
# HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL(_DZ)_v OR HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL(_DZ)_v 
# L1_Mu5_EG23 OR L1_Mu5_LooseIsoEG20 OR L1_Mu7_EG23 OR L1_Mu7_LooseIsoEG20 OR L1_Mu7_LooseIsoEG23 
# MuonEG PD. DZ versions unprescaled. Non DZ versions are prescaled 

# Muon + Electron (2)
# HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL(_DZ)_v 
# L1_Mu23_EG10 OR L1_Mu20_EG17 OR L1_SingleMu22 
# MuonEG PD. DZ and non-DZ versions unprescaled 

# #Run2018A [315974, 316361)
# Muon 
# HLT_IsoMu24_v 
# L1_SingleMu22 
# SingleMuon PD 

# Double Electron 
# HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL(_DZ)_v 
# L1_SingleEG* OR L1_DoubleEG_22_10_er2p5 OR L1_DoubleEG_25_12_er2p5 OR L1_DoubleEG_25_14_er2p5 OR L1_DoubleEG_LooseIso22_12_er2p5 
# EGamma PD. Both DZ and non DZ versions unprescaled 

# Double Muon 
# HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ(_Mass3p8/8)_v 
# L1_DoubleMu_12_5 OR L1_DoubleMu_15_7 
# DoubleMuon PD. Only DZ_MassX versions unprescaled!! 

# Muon + Electron (1)
# HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL(_DZ)_v OR HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL(_DZ)_v 
# L1_Mu5_EG23 OR L1_Mu5_LooseIsoEG20 OR L1_Mu7_EG23 OR L1_Mu7_LooseIsoEG20 OR L1_Mu7_LooseIsoEG23 
# MuonEG PD. DZ versions unprescaled. Non DZ versions are prescaled

# Muon + Electron (2)
# HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL(_DZ)_v 
# L1_Mu20_EG10er2p5 OR L1_SingleMu22 
# MuonEG PD. DZ and non-DZ versions unprescaled 

# #Run2018A/B [316361317509,) - no relevant changes in HLT Menus after this (for top!)
# Muon 
# HLT_IsoMu24_v 
# L1_SingleMu22 
# SingleMuon PD

# Double Electron 
# HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL(_DZ)_v 
# L1_SingleEG* OR L1_DoubleEG_22_10_er2p5 OR L1_DoubleEG_25_12_er2p5 OR L1_DoubleEG_25_14_er2p5 OR L1_DoubleEG_LooseIso22_12_er2p5 
# EGamma PD. Both DZ and non DZ versions unprescaled 

# Double Muon 
# HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ(_Mass3p8/8)_v 
# L1_DoubleMu_12_5 OR L1_DoubleMu_15_7 
# DoubleMuon PD. Only DZ_MassX versions unprescaled!!

# Muon + Electron (1)
# HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL(_DZ)_v OR HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL(_DZ)_v 
# L1_Mu5_EG23 OR L1_Mu5_LooseIsoEG20 OR L1_Mu7_EG23 OR L1_Mu7_LooseIsoEG20 OR L1_Mu7_LooseIsoEG23 
# MuonEG PD. DZ versions unprescaled. Non DZ versions are prescaled

# Muon + Electron (2)
# HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL(_DZ)_v 
# L1_Mu20_EG10er2p5 OR L1_SingleMu22 
# MuonEG PD. DZ and non-DZ versions unprescaled 

#### 2017 ####
# Muon 
# HLT_IsoMu27_v OR HLT_IsoMu24_eta2p1_v
# Run2017A - Run2017D

# HLT_IsoMu27_v
# Run2017E - Run2017F

# Double Muon 
# HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ
# Run2017A - Run2017B DZ version unprescaled

# HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8/Mass3p8_v
# From Run2017C: Only DZ_MassX versions

# Double Electron 
# HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL(_DZ)_v 
# All Run2017X, both versions unprescaled

# Muon + Electron 
# HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL(_DZ)_v OR HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v OR HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v 
# All Run2017X, All DZ and Mu23Ele12 non-DZ are unprescaled 
