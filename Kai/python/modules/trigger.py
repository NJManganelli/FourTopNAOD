import collections, math
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

TriggerTuple = collections.namedtuple("TriggerTuple", "trigger era subera tier channel leadMuThresh subMuThresh leadElThresh subElThresh")

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
    def __init__(self, era="2013", subera=None, isData=False, TriggerChannel=None, weightMagnitude=1, fillHists=False, debug=False):
        """ Trigger logic that checks for fired triggers and searches for appropriate objects based on criteria set by fired triggers.

        Era is a string with the year of data taking or corresponding MC sample ("2017", "2018")
        Subera is a string with the subera of data-taking, only for use in combination with isData=True and TriggerChannel ("B", "E", etc.)
        isData is a boolean for when it's a data sample, as these are handled differently (trigger exclusivity and tier selection) from Monte Carlo.
        TriggerChannel is a string with the trigger channel ("ElMu" for e-mu channel/dataset, regardless of which is higher pT, "El" for single-electron channel/dataset).
        fillHists is a boolean for filling histograms.

        Regarding data, internally there are 'tiers' associated with the trigger tuples. For MC, if the event fires any trigger from any tier, it should be accepted. 
        For data, given that events can be duplicated across data streams ('SingleMuon' and 'MuonEG'), triggers are divided into tiers. The goal is to only select a data event
        from the highest available tier of triggers that it fires, and veto that event in appropriate data streams when it corresponds to a lower trigger selection.
        For example, let an event fire both a single muon trigger (tier 4) and a mu-mu trigger (tier 1), but not an e-mu trigger (tier 0). In the double muon dataset, 
        the event is selected because it fired the tier 1 trigger in the list (and not the tier 0 triggers). In the single muon dataset, the event is veto'd, 
        because it fired the tier 1 trigger as well as the tier 4."""
        self.era = era
        self.subera = subera
        self.isData = isData
        #Options: "MuMu", "ElMu", "ElEl", "Mu"
        self.TriggerChannel = TriggerChannel
        if self.isData and (self.subera == None or self.TriggerChannel == None): 
            raise ValueError("In TriggerAndSelectionLogic is instantiated with isData, both subera and TriggerChannel must be slected ('B', 'F', 'El', 'ElMu', etc.")
        self.weightMagnitude = weightMagnitude
        self.fillHists = fillHists
        self.debug = debug
        #TriggerTuple = collections.namedtuple("TriggerTuple", "trigger era subera tier channel leadThresh subMuThresh")
        self.TriggerList = [TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2017",
                                         subera="BCDEF",
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2017",
                                         subera="BCDEF",
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=25,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                                         era="2017",
                                         subera="B",
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
                                         era="2017",
                                         subera="CDEF",
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
                                         era="2017",
                                         subera="CDEF",
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2017",
                                         subera="BCDEF",
                                         tier=2,
                                         channel="ElEl",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=25,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu24_eta2p1",
                                         era="2017",
                                         subera="BCD",
                                         tier=3,
                                         channel="Mu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu27",
                                         era="2017",
                                         subera="BCD",
                                         tier=3,
                                         channel="Mu",
                                         leadMuThresh=28,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu27",
                                         era="2017",
                                         subera="EF",
                                         tier=3,
                                         channel="Mu",
                                         leadMuThresh=28,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_Ele35_WPTight_Gsf",
                                         era="2017",
                                         subera="BCDEF",
                                         tier=4,
                                         channel="El",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=36,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=25,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=25,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
                                         era="2018",
                                         subera="ABCD",
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
                                         era="2018",
                                         subera="ABCD",
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999),
                            TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         tier=2,
                                         channel="ElEl",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=25,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu24",
                                         era="2018",
                                         subera="ABCD",
                                         tier=3,
                                         channel="Mu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=15),
                            TriggerTuple(trigger="HLT_Ele32_WPTight_Gsf",
                                         era="2018",
                                         subera="ABCD",
                                         tier=4,
                                         channel="El",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=33,
                                         subElThresh=15)]
        #Tiers and TriggerChannels should have a 1-to-1 or 1-to-multiple correspondence, dependant upon how data streams are arranged. Logic of multiple streams will need to be sorted for 2018, wheres some singleLepton stream is folded into the double lepton stream
        #2018 implication: given the combination of DoubleElectron and SingleElectron streams into EGamma (along with xPhoton?) data stream, this implies using the 4th backup tier and re-running over the same dataset yet again...
        #This is a waste of resources, but straightforward and keeps the same backup tiers. The alternative is to swap Mu and El backups, and combine the double electron and single electron into the same Tier...
        self.TierToChannelDict = {'2016': {0: [None]},
                                  '2017': {0: ["ElMu"],
                                           1: ["MuMu"],
                                           2: ["ElEl"],
                                           3: ["Mu"],
                                           4: ["El"]},
                                  '2018': {0: ["ElMu"],
                                           1: ["MuMu"],
                                           2: ["ElEl"],
                                           3: ["Mu"],
                                           4: ["El"]}
                                  }
        #Era subset of triggers, for use in bin labeling (cycle through axis and fill a bin for each trigger with weight 0.0)
        self.eraTriggers = [trigger for trigger in self.TriggerList if self.era == trigger.era]
        self.Triggers = [trigger for trigger in self.eraTriggers if self.isData == False or (self.subera in trigger.subera and self.TriggerChannel == trigger.channel)]
        #Create list of veto triggers for data, where explicit tiers are expected (calculating the tier first)
        #For 2017, 0 = ElMu dataset, 1 = MuMu, 2 = ElEl, 3 = Mu(Any), 4 = El(Any). Veto any events that fire any higher trigger, to avoid double counting by using this dataset
        #For 2018, 0 = ElMu dataset, Rest to be determined!
        self.tier = [trigger.tier for trigger in self.Triggers]
        self.tier.sort(key=lambda i: i, reverse=False)
        if self.debug: 
            print("Sorted trigger tiers selected are: " + str(self.tier))
        self.tier = self.tier[0]
        self.vetoTriggers = [trigger for trigger in self.eraTriggers if self.isData and self.subera in trigger.subera and trigger.tier < self.tier]
        if self.debug: 
            print("Trigger tier selected is: " + str(self.tier))
            print("Selected {} Triggers for usage".format(len(self.Triggers)))
            for t in self.Triggers:
                print(t)
            print("Selected {} Triggers for veto".format(len(self.vetoTriggers)))
            for t in self.vetoTriggers:
                print(t)

        #Bins for the fired HLT paths; max set to 0 for nice labeling without empty bin
        self.PathsBins = 1
        self.PathsMin = 0
        self.PathsMax = 0
        
    def beginJob(self, histFile=None,histDirName=None):
        if self.fillHists == False:
            Module.beginJob(self, None, None)
        else:
            if histFile == None or histDirName == None:
                raise RuntimeError("fillHists set to True, but no histFile or histDirName specified")
            Module.beginJob(self,histFile,histDirName)
            self.trigLogic_Paths = ROOT.TH1D("trigLogic_Paths", "HLT Paths passed by events (weightMagnitude={0}); Paths; Events".format(self.weightMagnitude), self.PathsBins, self.PathsMin, self.PathsMax)
            self.addObject(self.trigLogic_Paths)
            self.trigLogic_Freq = ROOT.TH1D("trigLogic_Freq", "HLT Paths Fired and Vetoed (weightMagnitude={0}); Fired or Vetoed or Neither; Events".format(self.weightMagnitude), 1, 0, 0)
            self.addObject(self.trigLogic_Freq)
            self.trigLogic_2DCorrel = ROOT.TH2D("trigLogic_2DCorrel", "nGenJets, GenHT  Fail condition (weightMagnitude={0}); nGenJets; GenHT ".format(self.weightMagnitude),
                                                self.PathsBins, self.PathsMin, self.PathsMax, self.PathsBins, self.PathsMin, self.PathsMax)
            self.addObject(self.trigLogic_2DCorrel)

            #Initialize labels to keep consistent across all files
            for trig in self.eraTriggers:
                self.trigLogic_Paths.Fill(trig.trigger + "T{})".format(trig.tier), 0.0)
                self.trigLogic_2DCorrel.Fill(trig.trigger + "T{})".format(trig.tier), trig.trigger + "T{})".format(trig.tier), 0.0)
            for cat in ["Vetoed", "Fired", "Neither"]:
                self.trigLogic_Freq.Fill(cat, 0.0)

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.branchList = inputTree.GetListOfBranches()
        if not self.isData and "genWeight" not in self.branchList:
            print("Warning in TriggerAndLogicSelection: expected branch genWeight to be present, but it is not. The weight magnitude indicated will be used, but the sign of the genWeight must be assumed positive!")

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
        #run = getattr(event, "run")
        #evt = getattr(event, "event")
        #lumi = getattr(event, "luminosityBlock")
        weight = math.copysign(self.weightMagnitude, getattr(event, "genWeight", 1))
        Fired = [trigger for trigger in self.Triggers if getattr(event, trigger.trigger, False)]
        Vetoed = [trigger for trigger in self.vetoTriggers if getattr(event, trigger.trigger, False)]
        if self.fillHists:
            if len(Vetoed) > 0: 
                self.trigLogic_Freq.Fill("Vetoed", weight)
            elif len(Fired) > 0:
                self.trigLogic_Freq.Fill("Fired", weight)
            else:
                self.trigLogic_Freq.Fill("Neither", weight)
            for tn, trig in enumerate(Fired):
                self.trigLogic_Paths.Fill(trig.trigger + " (T{})".format(trig.tier), weight)
                for tm, trig2 in enumerate(Fired):
                    if tm > tn:
                        self.trigLogic_2DCorrel.Fill(trig.trigger + " (T{})".format(trig.tier), trig2.trigger + " (T{})".format(trig2.tier), weight)
        if len(Vetoed) == 0 and len(Fired) > 0: return True
        return False

    def getCutString(self):
        vetoSection = "!("
        for tn, trigger in enumerate(self.vetoTriggers):
            if tn > 0:
                vetoSection += " || "
            vetoSection += trigger.trigger
        vetoSection += ")"

        passSection = "("
        for tn, trigger in enumerate(self.Triggers):
            if tn > 0:
                passSection += " || "
            passSection += trigger.trigger
        passSection += ")"

        retString = ""
        if len(self.vetoTriggers) > 0: retString += vetoSection + " && "
        retString += passSection

        return retString

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
