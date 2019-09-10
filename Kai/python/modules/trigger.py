import ROOT
import collections, math
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

#Notes on the TriggerTuple type. The Trigger is the string value naming the HLT branch, exactly as in NanoAOD (i.e. "HLT_IsoMu27" not "HLT_IsoMu27_v" or with wildcard as in Miniaod. 
#The era and suberas are strings defining the year and run period(s) that the trigger is valid for. The constructor must be initialized with values that will have equality with the era and pass a python "in" check, such as "A" in "ABC" (True), where the latter subera is the value in the trigger tuple and the former is in the constructor for a run 20XX subera "A" dataset
#The uniqueEraBit will be an integer defining the place in a bitset, and should be unique within the era. That is, If starting from 14 in 2017, then the 10th trigger would be 5, counting down. The important thing is that it is unique within that era, and for bits, it will calculate the value as the sum of 2^(bit_i) for all passing trigger_i.
#The tier defines groupings, which are oriented toward selecting events without duplication from multiple data streams. Tier 0 is highest, in this case, and it increments to higher integers that have lower tier value/priority, reverse of the bit values. Triggers within the same tier use an OR logic, and triggers in lower tiers are only checked if NONE of the triggers in higher tiers fired, if it's data. For MC, an OR of all triggers regardless of tier is used (but with the correct era). 
#The channel has a correspondence with the tiers, and so in this case, Tier 0 = "ElMu", the set of triggers with one muon and one electron. Tier 1 = "MuMu", the double muon triggers. Channels are easier handles for passing to the constructor when the MuonEG dataset, for example, is going to be used. This also allows internal reprioritization without changing constructors. To expound further on the tier logic, to prevent uselessly or incorrectly grabbing duplicate events that are in multiple data streams (An event that has two high-pt, isolated leptons can be in both the double lepton and single lepton sets, for example, if it fires both a double lep and single lep trigger). Thus, the event is only pulled from a dataset if it fires the correct trigger, and doesn't fire a trigger that would mean the event enters and gets selected from a higher tier.
#run 2000657 event 290456921 fires the double muon and single muon triggers, tiers 1 and 3 respectively. It does not fire a tier 0 trigger. When processing the DoubleMuon dataset, it gets picked up because it did NOT fire a tier 0 trigger, but DID fire a tier 1 trigger (that it fired a tier 3 is ignored in this dataset). Now, when processing the single muon dataset, the event is processed again, however, now it fails the veto triggers by fact it fired the tier 1, and so it's ignored despite firing the tier 3. Overall, this permits picking up events that ONLY fire the lower tier trigger and not the higher, whilst preventing duplicate events from being picked up.
#The leadXXXThresh and subXXXThresh are very specifically for TRIGGERING leptons. That is, if the Trigger is "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", then the leadMuThresh is going to be 23 (or higher, to be safe and more uniform across triggers - such as 25). the subMuThresh will be 99999! Because we do not want to find a second triggering muon at any pt. the leadElThresh is similarly 99999, because we're expecting the leading lepton to be the muon, not the electron. The subElThresh is then set at 15, 3 higher than strictly necessary for the second triggering lepton. Finally, we have to select non-triggering leptons for X-lepton veto and selecting events with second leptons when only single-lepton triggers are fired. The field for this is nontriggerLepThresh, which applies uniformly to muons and electrons.

TriggerTuple = collections.namedtuple("TriggerTuple", "trigger era subera uniqueEraBit tier channel leadMuThresh subMuThresh leadElThresh subElThresh nontriggerLepThresh")

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
    def __init__(self, passLevel, era="2013", subera=None, isData=False, TriggerChannel=None, weightMagnitude=1, fillHists=False, debug=False, mode="Flag"):
        """ Trigger logic that checks for fired triggers and searches for appropriate objects based on criteria set by fired triggers.

        passLevel is the level at which the module should trigger "True" to pass the event along to further modules. Available: 'hlt', 'baseline', 'selection'
        Era is a string with the year of data taking or corresponding MC sample ("2017", "2018")
        Subera is a string with the subera of data-taking, only for use in combination with isData=True and TriggerChannel ("B", "E", etc.)
        isData is a boolean for when it's a data sample, as these are handled differently (trigger exclusivity and tier selection) from Monte Carlo.
        TriggerChannel is a string with the trigger channel ("ElMu" for e-mu channel/dataset, regardless of which is higher pT, "El" for single-electron channel/dataset).
        fillHists is a boolean for filling histograms.

        Regarding data, internally there are 'tiers' associated with the trigger tuples. For MC, if the event fires any trigger from any tier, it should be accepted. 
        For data, given that events can be duplicated across data streams ('SingleMuon' and 'MuonEG'), triggers are divided into tiers. 
        The goal is to only select a data event from the highest available tier of triggers that it fires, and veto that event in appropriate 
        data streams when it corresponds to a lower trigger selection.

        For example, let an event fire both a single muon trigger (tier 3) and a mu-mu trigger (tier 1), but not an e-mu trigger (tier 0). In the double muon dataset, 
        the event is selected because it fired the tier 1 trigger in the list (and not the tier 0 triggers). In the single muon dataset, the event is veto'd, 
        because it fired the tier 1 trigger as well as the tier 3. A different event that only fired the tier 3 trigger is appropriately picked up on the single muon 
        dataset, and while it may exist in the double muon dataset, it will only be becasue of a trigger that we have not checked for, and so we must not have picked it up
        in that dataset"""
        self.passLevel = passLevel
        self.era = era
        self.subera = subera
        self.isData = isData
        #Options: "MuMu", "ElMu", "ElEl", "Mu"
        self.TriggerChannel = TriggerChannel
        if self.isData and (self.subera == None or self.TriggerChannel == None): 
            raise ValueError("In TriggerAndSelectionLogic is instantiated with isData, both subera and TriggerChannel must be slected ('B', 'F', 'El', 'ElMu', etc.")
        self.weightMagnitude = weightMagnitude
        self.fillHists = fillHists
        if self.fillHists or self.mode == "Plot": 
            self.fillHists = True
            self.writeHistFile = True
        self.debug = debug
        self.mode = mode
        if self.mode not in ["Flag", "Pass", "Fail", "Plot"]:
            raise NotImplementedError("Not a supported mode for the TriggerAndSelectionLogic module: '{0}'".format(self.mode))
        #TriggerTuple = collections.namedtuple("TriggerTuple", "trigger era subera tier channel leadThresh subMuThresh")
        self.TriggerList = [TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2017",
                                         subera="BCDEF",
                                         uniqueEraBit=14,
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=15,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2017",
                                         subera="BCDEF",
                                         uniqueEraBit=13,
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=25,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                                         era="2017",
                                         subera="B",
                                         uniqueEraBit=12,
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
                                         era="2017",
                                         subera="CDEF",
                                         uniqueEraBit=11,
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2017",
                                         subera="BCDEF",
                                         uniqueEraBit=9,
                                         tier=2,
                                         channel="ElEl",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=25,
                                         subElThresh=15,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu27",
                                         era="2017",
                                         subera="BCDEF",
                                         uniqueEraBit=7,
                                         tier=3,
                                         channel="Mu",
                                         leadMuThresh=28,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Ele35_WPTight_Gsf",
                                         era="2017",
                                         subera="BCDEF",
                                         uniqueEraBit=6,
                                         tier=4,
                                         channel="El",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=36,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=14,
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=25,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=12,
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=15,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=11,
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=9,
                                         tier=2,
                                         channel="ElEl",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=25,
                                         subElThresh=15,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_IsoMu24",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=8,
                                         tier=3,
                                         channel="Mu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Ele32_WPTight_Gsf",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=7,
                                         tier=4,
                                         channel="El",
                                         leadMuThresh=99999,
                                         subMuThresh=99999,
                                         leadElThresh=33,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15)]
        #Store triggers that are (temporarily) abandoned due to overlap or extra restrictions
        self.lostTrigger = [TriggerTuple(trigger="HLT_IsoMu24_eta2p1",
                                         era="2017",
                                         subera="BCD",
                                         uniqueEraBit=8,
                                         tier=3,
                                         channel="Mu",
                                         leadMuThresh=25,
                                         subMuThresh=99999,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
                                         era="2017",
                                         subera="CDEF",
                                         uniqueEraBit=10,
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=13,
                                         tier=0,
                                         channel="ElMu",
                                         leadMuThresh=99999,
                                         subMuThresh=15,
                                         leadElThresh=25,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),
                            TriggerTuple(trigger="HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
                                         era="2018",
                                         subera="ABCD",
                                         uniqueEraBit=10,
                                         tier=1,
                                         channel="MuMu",
                                         leadMuThresh=25,
                                         subMuThresh=15,
                                         leadElThresh=99999,
                                         subElThresh=99999,
                                         nontriggerLepThresh=15),

                        ]



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
        #The levels for filling histograms and event levels
        self.levelToNameDict = {"T": "HLT Trigger",
                                "B_Lep": "Baseline level with leptons",
                                "B_Jet": "Baseline level with leptons and jets", 
                                "B_HT": "Baseline level with leptons and jets and HT", 
                                "S_Lep": "Selection level with leptons", 
                                "S_Jet": "Selection level with leptons and jets", 
                                "S_HT": "Selection level with leptons and jets and HT"
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
        self.BitsBins = 32
        self.BitsMin = 0
        self.BitsMax = 32

    def beginJob(self, histFile=None,histDirName=None):
        if self.fillHists == False:
            Module.beginJob(self, None, None)
        else:
            if histFile == None or histDirName == None:
                raise RuntimeError("fillHists set to True, but no histFile or histDirName specified")
            Module.beginJob(self,histFile,histDirName)
            self.trigLogic_Paths = {}
            self.trigLogic_Freq = {}
            self.trigLogic_2DCorrel = {}
            for lvl in ["TRIG", "BASE", "SLCT"]:
                self.trigLogic_Paths[lvl] = ROOT.TH1D("trigLogic_Paths_{}".format(lvl), 
                                                      "HLT Paths passed by events  at {} level (weightMagnitude={0}); Paths; Events".format(lvl, self.weightMagnitude), 
                                                      self.PathsBins, self.PathsMin, self.PathsMax)
                self.trigLogic_Freq[lvl] = ROOT.TH1D("trigLogic_Freq_{}".format(lvl), 
                                                     "HLT Paths Fired and Vetoed at {} level  (weightMagnitude={0}); Type; Events".format(lvl, self.weightMagnitude), 
                                                     1, 0, 0)
                self.trigLogic_Correl[lvl] = ROOT.TH2D("trigLogic_Correl_{}".format(lvl), 
                                                         "Fired HLT Path Correlations at {} level (weightMagnitude={0}); Path; Path ".format(lvl, self.weightMagnitude),
                                                         self.PathsBins, self.PathsMin, self.PathsMax, self.PathsBins, self.PathsMin, self.PathsMax)
                self.trigLogic_Bits[lvl] = ROOT.TH2D("trigLogic_Bits_{}".format(lvl), 
                                                         "Fired HLT Path Bits at {} level (weightMagnitude={0}); Path; Bits ".format(lvl, self.weightMagnitude),
                                                         self.PathsBins, self.PathsMin, self.PathsMax, self.BitsBins, self.BitsMin, self.BitsMax)
            for lvl in ["TRIG", "BASE", "SLCT"]:
                self.addObject(self.trigLogic_Paths[lvl])
                self.addObject(self.trigLogic_Freq[lvl])
                self.addObject(self.trigLogic_Correl[lvl])
                self.addObject(self.trigLogic_Bits[lvl])

            #Initialize labels to keep consistent across all files
            for lvl in ["TRIG", "BASE", "SLCT"]:
                for trig in self.eraTriggers:
                    self.trigLogic_Paths[lvl].Fill(trig.trigger + " (T{})".format(trig.tier), 0.0)
                    self.trigLogic_Correl[lvl].Fill(trig.trigger + " (T{})".format(trig.tier), trig.trigger + " (T{})".format(trig.tier), 0.0)
                    self.trigLogic_Bits[lvl].Fill(trig.trigger + " (T{})".format(trig.tier), 0, 0.0)
                for cat in ["Vetoed", "Fired", "Neither"]:
                    self.trigLogic_Freq[lvl].Fill(cat, 0.0)

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.branchList = inputTree.GetListOfBranches()
        self.outBranchList = self.out.GetListOfBranches() #Potential check against branches that are being written by previous modules
        if self.isData:
            self.XSweight = self.dataWeightFunc
        elif "genWeight" not in self.branchList:
            self.XSweight = self.backupWeightFunc
            print("Warning in TriggerAndSelectionLogic: expected branch genWeight to be present, but it is not."\
                  "The weight magnitude indicated will be used, but the sign of the genWeight must be assumed positive!")
        else:
            self.XSweight = self.genWeightFunc
        self.varTuple = [('Muon_OSV_baseline', 'O', 'Passes TriggerAndSelectionLogic at baseline level', 'nMuon'),
                         ('Muon_OSV_selection', 'O', 'Passes TriggerAndSelectionLogic at selection level', 'nMuon'),
                         ('Electron_OSV_baseline', 'O', 'Passes TriggerAndSelectionLogic at baseline level', 'nElectron'),
                         ('Electron_OSV_selection', 'O', 'Passes TriggerAndSelectionLogic at selection level', 'nElectron'),
                         ('ESV_TriggerAndSelectionLogic_baseline', 's', 'Passes TriggerAndSelectionLogic at event level,'\
                         ' bits correspond to uniqueEraBit in TriggerAndSelectionLogic', None),
                         ('ESV_TriggerAndSelectionLogic_selection', 's', 'Passes TriggerAndSelectionLogic at event level,'\
                         ' bits correspond to uniqueEraBit in TriggerAndSelectionLogic', None)
                       ]        #OSV = Object Selection Variable
        for trigger in self.eraTriggers:
            #unsigned 16 bit integers for the trigger bit storage
            self.varTuple.append(('ESV_TriggerEraBits_b{}'.format(trigger.uniqueEraBit), 's', 
                                 'Bits (Baseline) for Trigger={}'\
                                 'with uniqueEraBit={}'.format(trigger.trigger, trigger.uniqueEraBit), None))
            self.varTuple.append(('ESV_TriggerEraBits_s{}'.format(trigger.uniqueEraBit), 's', 
                                 'Bits (Selection) for Trigger={}'\
                                 'with uniqueEraBit={}'.format(trigger.trigger, trigger.uniqueEraBit), None))
        if self.mode == "Flag":
            if not self.out:
                raise RuntimeError("No Output file selected, cannot flag events for TriggerAndSelectionLogic module")
            else:
                for name, valType, valTitle, lVar in self.varTuple:
                    self.out.branch("{}".format(name), valType, lenVar=lVar, title=valTitle) 
        elif self.mode == "Pass" or self.mode == "Fail" or self.mode == "Plot":
            pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
        #run = getattr(event, "run")
        #evt = getattr(event, "event")
        #lumi = getattr(event, "luminosityBlock")
        # try:
        #     weight = math.copysign(self.weightMagnitude, getattr(event, "genWeight", 1))
        # except RuntimeError, e:
        #     weight = 1
        weight = self.XSweight(event)
        #getattr with default value doesn't work, have to protect anyway...
        Fired = [trigger for trigger in self.Triggers if hasattr(event, trigger.trigger) and getattr(event, trigger.trigger, False)]
        Vetoed = [trigger for trigger in self.vetoTriggers if hasattr(event, trigger.trigger) and getattr(event, trigger.trigger, False)]
        muons = Collection(event, "Muon")
        elecrtons = Collection(event, "Electron")

        #Prepare dictionary with trigger names as keys
        leadMu_baseline = {}
        leadEl_baseline = {}
        subMu_baseline = {}
        subEl_baseline = {}
        leadMu_selection = {}
        leadEl_selection = {}
        subMu_selection = {}
        subEl_selection = {}
        pass_baseline = {}
        pass_selection = {}
        #Create baseline and selection level lists for each trigger, permitting an event to pass at event and selection levels with different triggers
        for trigger in Fired:
            leadMu_baseline[trigger.trigger] = []
            leadEl_baseline[trigger.trigger] = []
            subMu_baseline[trigger.trigger] = []
            subEl_baseline[trigger.trigger] = []
            nontriggerMu_baseline[trigger.trigger] = []
            nontriggerEl_baseline[trigger.trigger] = []
            leadMu_selection[trigger.trigger] = []
            leadEl_selection[trigger.trigger] = []
            subMu_selection[trigger.trigger] = []
            subEl_selection[trigger.trigger] = []
            nontriggerMu_selection[trigger.trigger] = []
            nontriggerEl_selection[trigger.trigger] = []
            
            #pass variables
            pass_trigger[trigger.trigger] = True #If it's in fired, it fired
            if len(Vetoed) < 1:
                pass_trigger_veto[trigger.trigger] = True #both fired and not vetoed in the event
            else:
                pass_trigger_veto[trigger.trigger] = False #fired but vetoed
            #Store bitsets here for details of the baseline and selection cuts
            pass_baseline_lep[trigger.trigger] = 0 #convert to bit counter, 0 fail, 1 2+ leps, 2 less than 3 leps, 4 opp charge, 8 ID requirements, 16 inv mass
            pass_baseline_jet[trigger.trigger] = 0
            pass_baseline_ht[trigger.trigger] = 0
            pass_selection_lep[trigger.trigger] = 0
            pass_selection_jet[trigger.trigger] = 0
            pass_selection_ht[trigger.trigger] = 0

        #FIXME: Add dz cut, add iso cut or trg object cut, add to triggers as well
        for idx, mu in enumerate(muons):
            if len(Vetoed) > 0 or len(Fired) < 1: continue
            d0 = math.sqrt(mu.dxy**2 + mu.dz**2)
            pass_eta = (abs(mu.eta) < 2.4) #max regardless
            #Baseline bools
            pass_iso_baseline = (mu.pfIsoId >= 3) #trigger iso VVL, so selection = tight (4) far exceeds this...
            pass_dz_baseline = (abs(mu.dz) < 0.06) #trigger dz = 0.2, selection = 0.02, baseline = 0.06
            pass_d0_baseline = (d0 < 0.15) #selection = 0.10, baseline = 0.15
            #Selection bools
            pass_iso_selection = (mu.pfIsoId >= 4) #trigger iso VVL, so selection = tight (4) far exceeds this...
            pass_dz_selection = (abs(mu.dz) < 0.02) #trigger dz = 0.2, selection = 0.02, baseline = 0.06
            pass_d0_selection = (d0 < 0.10) #selection = 0.10, baseline = 0.15
            pass_common_baseline = pass_eta and pass_iso_baseline and pass_dz_baseline and pass_d0_baseline
            pass_common_selection = pass_eta and pass_iso_selection and pass_dz_selection and pass_d0_selection
            for trigger in Fired:
                if pass_common_baseline:
                    #Create OVERLAPPING baseline collections
                    if mu.pt > trigger.leadMuThresh:
                        leadMu_baseline[trigger.trigger].append((idx, mu))
                    if mu.pt > trigger.subMuThresh:
                        subMu_baseline[trigger.trigger].append((idx, mu))
                    if mu.pt > trigger.nontriggerLepThresh:
                        nontriggerMu_baseline[trigger.trigger].append((idx, mu))
                if pass_common_selection:
                    #Create OVERLAPPING selection collections
                    if mu.pt > trigger.leadMuThresh:
                        leadMu_selection[trigger.trigger].append((idx, mu))
                    if mu.pt > trigger.subMuThresh:
                        subMu_selection[trigger.trigger].append((idx, mu))
                    if mu.pt > trigger.nontriggerLepThresh:
                        nontriggerMu_selection[trigger.trigger].append((idx, mu))
    
        for idx, el in enumerate(electrons):
            if len(Vetoed) > 0 or len(Fired) < 1: continue
            d0 = math.sqrt(el.dxy**2 + el.dz**2)
            pass_eta_barrel = (abs(el.eta) < 1.4442) #crack edge
            pass_eta_endcap = (abs(el.eta) > 1.4660 and abs(el.eta) < 2.5) #crack edge and calorimeters
            if pass_eta_barrel: 
                pass_d0_baseline = (d0 < 0.10) #selection < 0.05, baseline < 0.10
                pass_d0_selection = (d0 < 0.05) #selection < 0.05, baseline < 0.10
                pass_eta = True
            elif pass_eta_endcap: 
                pass_d0_baseline = (d0 < 0.15) #selection < 0.10, baseline < 0.15
                pass_d0_selection = (d0 < 0.10) #selection < 0.10, baseline < 0.15
                pass_eta = True
            else: 
                pass_d0_baseline = False #doesn't matter without eta pass
                pass_d0_selection = False #doesn't matter without eta pass
                pass_eta = False
            pass_dz_baseline = (el.dz < 0.06) #selection < 0.02, baseline < 0.06, trigger < 0.2 presumably (verification needed)
            pass_dz_selection = (el.dz < 0.02) #selection < 0.02, baseline < 0.06, trigger < 0.2 presumably (verification needed)
            pass_id_loose = (el.cutBased >= 2)
            pass_id_medium = (el.cutBased >= 3)
            pass_common_baseline = pass_eta and pass_iso_baseline and pass_dz_baseline and pass_d0_baseline and pass_id_loose
            pass_common_selection = pass_eta and pass_iso_selection and pass_dz_selection and pass_d0_selection and pass_id_loose
            for trigger in Fired:
                if pass_common_baseline:
                    #Create OVERLAPPING baseline collections
                    if el.pt > trigger.leadElThresh:
                        leadEl_baseline[trigger.trigger].append((idx, el))
                    if el.pt > trigger.subElThresh:
                        subEl_baseline[trigger.trigger].append((idx, el))
                    if el.pt > trigger.nontriggerLepThresh:
                        nontriggerEl_baseline[trigger.trigger].append((idx, el))
                if pass_common_selection:
                    #Create OVERLAPPING selection collections
                    if el.pt > trigger.leadElThresh:
                        leadEl_selection[trigger.trigger].append((idx, el))
                    if el.pt > trigger.subElThresh:
                        subEl_selection[trigger.trigger].append((idx, el))
                    if el.pt > trigger.nontriggerLepThresh:
                        nontriggerEl_selection[trigger.trigger].append((idx, el))

        #Do Lepton selection logic here
        pass_baseline_bitset = 0
        pass_selection_bitset = 0
        for trigger in Fired:            
            #FIXME: Need the mass, charge, 3-lepton vetos in place. Add a bitset for EVERY trigger, then work on single event-level bitset
            if trigger.channel == "ElMu":
                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadEl_baseline[trigger.trigger]) > 0 and len(subMu_baseline[trigger.trigger]) > 0:
                    #2+ leptons of the right triggering types
                    pass_baseline_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_baseline_lep[trigger.trigger] += 2**1                
                        if leadEl_baseline[trigger.trigger][0][1].charge * subMu_baseline[trigger.trigger][0][1].charge < 0:
                            #Opposite sign leptons
                            pass_baseline_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivialsolution right now, but couple with OS charge requirement
                            pass_baseline_lep[trigger.trigger] += 2**3
                            #Null invariant mass cut for e-mu channel - the trivial bit - but pair it with ID requirements here
                            pass_baseline_lep[trigger.trigger] += 2**4
                if pass_baseline_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_baseline_bitset += 2**trigger.uniqueEraBit

                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadEl_selection[trigger.trigger]) > 0 and len(subMu_selection[trigger.trigger]) > 0:
                    #2+ leptons of the right triggering types
                    pass_selection_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_selection_lep[trigger.trigger] += 2**1                
                        if leadEl_selection[trigger.trigger][0][1].charge * subMu_selection[trigger.trigger][0][1].charge < 0:
                            #Opposite sign leptons
                            pass_selection_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivialsolution right now, but couple with OS charge requirement
                            pass_selection_lep[trigger.trigger] += 2**3
                            #Null invariant mass cut for e-mu channel - the trivial bit - but pair it with ID requirements here
                            pass_selection_lep[trigger.trigger] += 2**4
                if pass_selection_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_selection_bitset += 2**trigger.uniqueEraBit
            elif trigger.channel == "MuMu":
                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadMu_baseline[trigger.trigger]) > 0 and len(subMu_baseline[trigger.trigger]) > 0:
                    #2+ leptons of the right triggering types
                    pass_baseline_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_baseline_lep[trigger.trigger] += 2**1                
                        if leadMu_baseline[trigger.trigger][0][1].charge * subMu_baseline[trigger.trigger][0][1].charge < 0:
                            #Opposite sign leptons
                            pass_baseline_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivialsolution right now, but couple with OS charge requirement
                            pass_baseline_lep[trigger.trigger] += 2**3
                            if (leadMu_baseline[trigger.trigger][0][1].p4() * subMu_baseline[trigger.trigger][0][1].p4()).M() > 8.0:
                                #Require invariant mass over 8GeV to simplify trigger tuples, Code could be simplified/unified, but eh...
                                pass_baseline_lep[trigger.trigger] += 2**4
                if pass_baseline_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_baseline_bitset += 2**trigger.uniqueEraBit

                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadMu_selection[trigger.trigger]) > 0 and len(subMu_selection[trigger.trigger]) > 0:
                    #2+ leptons of the right triggering types
                    pass_selection_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_selection_lep[trigger.trigger] += 2**1                
                        if leadMu_selection[trigger.trigger][0][1].charge * subMu_selection[trigger.trigger][0][1].charge < 0:
                            #Opposite sign leptons
                            pass_selection_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivialsolution right now, but couple with OS charge requirement
                            pass_selection_lep[trigger.trigger] += 2**3
                            if (leadMu_selection[trigger.trigger][0][1].p4() * subMu_selection[trigger.trigger][0][1].p4()).M() > 8.0:
                                #Require invariant mass over 8GeV to simplify trigger tuples, Code could be simplified/unified, but eh...
                                pass_selection_lep[trigger.trigger] += 2**4
                if pass_selection_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_selection_bitset += 2**trigger.uniqueEraBit
            elif trigger.channel == "ElEl":
                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadEl_baseline[trigger.trigger]) > 0 and len(subEl_baseline[trigger.trigger]) > 0:
                    #2+ leptons of the right triggering types
                    pass_baseline_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_baseline_lep[trigger.trigger] += 2**1                
                        if leadEl_baseline[trigger.trigger][0][1].charge * subEl_baseline[trigger.trigger][0][1].charge < 0:
                            #Opposite sign leptons
                            pass_baseline_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivialsolution right now at BASELINE ONLY, but couple with OS charge requirement
                            pass_baseline_lep[trigger.trigger] += 2**3
                            #Trivial solution, no invariant mass cut for e-e channel
                            pass_baseline_lep[trigger.trigger] += 2**4
                if pass_baseline_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_baseline_bitset += 2**trigger.uniqueEraBit

                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadEl_selection[trigger.trigger]) > 0 and len(subEl_selection[trigger.trigger]) > 0:
                    #2+ leptons of the right triggering types
                    pass_selection_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger]) <= 2:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_selection_lep[trigger.trigger] += 2**1                
                        if leadEl_selection[trigger.trigger][0][1].charge * subEl_selection[trigger.trigger][0][1].charge < 0:
                            #Opposite sign leptons
                            pass_selection_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            if leadEl_selection[trigger.trigger][0][1].cutBased >= 3 or subEl_selection[trigger.trigger][0][1].cutBased >= 3:
                                #Require that one is medium ID!
                                pass_selection_lep[trigger.trigger] += 2**3
                                #Trivial solution, no invariant mass cut for e-e channel
                                pass_selection_lep[trigger.trigger] += 2**4
                if pass_selection_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_selection_bitset += 2**trigger.uniqueEraBit

            elif trigger.channel == "Mu":
                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadMu_baseline[trigger.trigger]) > 0 and (len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger])) > 1:
                    #2+ leptons, 1 triggering muon, and at least 2 electrons/muons passing the common selection requirements
                    pass_baseline_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger]) < 3:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_baseline_lep[trigger.trigger] += 2**1              
                        #Now unknown which collection contains the 2nd lepton, so go to the non-triggering collections
                        leptons_baseline = nontriggerMu_baseline[trigger.trigger] + nontriggerEl_baseline[trigger.trigger]
                        if leptons_baseline[0][1].charge * leptons_baseline[1][1].charge < 0:
                            #Opposite sign leptons
                            pass_baseline_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivial solution right now, since there's a mouon, but couple with OS charge requirement
                            pass_baseline_lep[trigger.trigger] += 2**3
                            #Null invariant mass cut for single mu channel - the trivial bit - but pair it with ID requirements here
                            pass_baseline_lep[trigger.trigger] += 2**4
                if pass_baseline_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_baseline_bitset += 2**trigger.uniqueEraBit

                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadMu_selection[trigger.trigger]) > 0 and (len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger])) > 1:
                    #2+ leptons, 1 triggering muon, and at least 2 electrons/muons passing the common selection requirements
                    pass_selection_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger]) < 3:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_selection_lep[trigger.trigger] += 2**1              
                        #Now unknown which collection contains the 2nd lepton, so go to the non-triggering collections
                        leptons_selection = nontriggerMu_selection[trigger.trigger] + nontriggerEl_selection[trigger.trigger]
                        if leptons_selection[0][1].charge * leptons_selection[1][1].charge < 0:
                            #Opposite sign leptons
                            pass_selection_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            #Trivial solution right now, since there's a mouon, but couple with OS charge requirement
                            pass_selection_lep[trigger.trigger] += 2**3
                            #Null invariant mass cut for single mu channel - the trivial bit - but pair it with ID requirements here
                            pass_selection_lep[trigger.trigger] += 2**4
                if pass_selection_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_selection_bitset += 2**trigger.uniqueEraBit

                #Maybe FIXME: Don't forget eta or tkIso cuts different from double lepton values! Difference between 2017 and 2018 values
            elif trigger.channel == "El":
                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadEl_baseline[trigger.trigger]) > 0 and (len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger])) > 1:
                    #2+ leptons, 1 triggering electron, and at least 2 electrons/muons passing the common selection requirements
                    pass_baseline_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_baseline[trigger.trigger]) + len(nontriggerMu_baseline[trigger.trigger]) < 3:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_baseline_lep[trigger.trigger] += 2**1              
                        #Now unknown which collection contains the 2nd lepton, so go to the non-triggering collections
                        #FIXME: have to check for any kind of combination of leptons...
                        leptons_baseline = nontriggerMu_baseline[trigger.trigger] + nontriggerEl_baseline[trigger.trigger]
                        if leptons_baseline[0][1].charge * leptons_baseline[1][1].charge < 0:
                            #Opposite sign leptons
                            pass_baseline_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            if leadEl_baseline[trigger.trigger][0][1].cutBased >= 4:
                                #WPTight on these... effectively the medium cut in case of e-e channel
                                pass_baseline_lep[trigger.trigger] += 2**3
                                #Null invariant mass cut for single e channel - the trivial bit - but pair it with ID requirements here
                                pass_baseline_lep[trigger.trigger] += 2**4
                if pass_baseline_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_baseline_bitset += 2**trigger.uniqueEraBit

                #Partially ascending triggers, to avoid duplicate length checks for safe indexing
                if len(leadEl_selection[trigger.trigger]) > 0 and (len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger])) > 1:
                    #2+ leptons, 1 triggering electron, and at least 2 electrons/muons passing the common selection requirements
                    pass_selection_lep[trigger.trigger] += 2**0
                    if len(nontriggerEl_selection[trigger.trigger]) + len(nontriggerMu_selection[trigger.trigger]) < 3:
                        #Superset containing the leading and subleading leptons, plus any additional leptons of any flavor at the nontriggering threshold
                        #Only 2 leptons here
                        pass_selection_lep[trigger.trigger] += 2**1              
                        #Now unknown which collection contains the 2nd lepton, so go to the non-triggering collections
                        #FIXME: have to check for any kind of combination of leptons...
                        leptons_selection = nontriggerMu_selection[trigger.trigger] + nontriggerEl_selection[trigger.trigger]
                        if leptons_selection[0][1].charge * leptons_selection[1][1].charge < 0:
                            #Opposite sign leptons
                            pass_selection_lep[trigger.trigger] += 2**2
                            #ID Requirements, if any, beyond the loose-loose common selection
                            if leadEl_selection[trigger.trigger][0][1].cutBased >= 4:
                                #WPTight on these... effectively the medium cut in case of e-e channel
                                pass_selection_lep[trigger.trigger] += 2**3
                                #Null invariant mass cut for single e channel - the trivial bit - but pair it with ID requirements here
                                pass_selection_lep[trigger.trigger] += 2**4
                if pass_selection_lep[trigger.trigger] >= 31: #Change to reflect proper number of bits used
                    pass_selection_bitset += 2**trigger.uniqueEraBit
                #maybe L1 Seed additional requirement in 2017 needed?
            elif self.doUnbiasedTrigger:
                pass
            else:
                RuntimeError("Unhandled Trigger.channel class")

#            for lvl in ["T", "B_Lep", "B_Jet", "B_HT", "S_Lep", "S_Jet", "S_HT"]:
        if self.fillHists:
            #FIXME: this obviously needs reworking, now... need a dict?
            if len(Vetoed) > 0: 
                self.trigLogic_Freq["TRIG"].Fill("Vetoed", weight)
            elif len(Fired) > 0:
                self.trigLogic_Freq["TRIG"].Fill("Fired", weight)
                if pass_baseline_bitset > 0:
                    self.trigLogic_Freq["BASE"].Fill("Fired", weight)
                if pass_selection_bitset > 0:
                    self.trigLogic_Freq["SLCT"].Fill("Fired", weight)
            else:
                self.trigLogic_Freq["TRIG"].Fill("Neither", weight)
            for tn, trig in enumerate(Fired):
                self.trigLogic_Paths["TRIG"].Fill(trig.trigger + " (T{})".format(trig.tier), weight)
                if pass_baseline_lep[trig.trigger]:
                    self.trigLogic_Paths["BASE"].Fill(trig.trigger + " (T{})".format(trig.tier), weight)
                if pass_selection_lep[trig.trigger]:
                    self.trigLogic_Paths["SLCT"].Fill(trig.trigger + " (T{})".format(trig.tier), weight)
                self.trigLogic_Bits["BASE"].Fill(trig.trigger + " (T{})".format(trig.tier), pass_baseline_lep[trig.trigger], weight)
                self.trigLogic_Bits["SLCT"].Fill(trig.trigger + " (T{})".format(trig.tier), pass_selection_lep[trig.trigger], weight)
                for tm, trig2 in enumerate(Fired):
                    # if tm >= tn: #Do self correllation to set the scale properly
                    #Just do full correlation matrix
                    self.trigLogic_Correl["TRIG"].Fill(trig.trigger + " (T{})".format(trig.tier), trig2.trigger + " (T{})".format(trig2.tier), weight)
                    if pass_baseline_lep[trig.trigger] and pass_baseline_lep[trig2.trigger]:
                        self.trigLogic_Correl["BASE"].Fill(trig.trigger + " (T{})".format(trig.tier), trig2.trigger + " (T{})".format(trig2.tier), weight)
                    if pass_selection_lep[trig.trigger] and pass_selection_lep[trig2.trigger]:
                        self.trigLogic_Correl["SLCT"].Fill(trig.trigger + " (T{})".format(trig.tier), trig2.trigger + " (T{})".format(trig2.tier), weight)

            
            # for lvl in ["TRIG", "BASE", "SLCT"]:
            #     if len(Vetoed) > 0: 
            #         self.trigLogic_Freq[lvl].Fill("Vetoed", weight)
            #     elif len(Fired) > 0:
            #         self.trigLogic_Freq[lvl].Fill("Fired", weight)
            #     else:
            #         self.trigLogic_Freq[lvl].Fill("Neither", weight)
            #     for tn, trig in enumerate(Fired):
            #         self.trigLogic_Paths[lvl].Fill(trig.trigger + " (T{})".format(trig.tier), weight)
            #         self.trigLogic_Bits[lvl].Fill(trig.trigger + " (T{})".format(trig.tier), trig2.trigger + " (T{})".format(trig2.tier), weight)
            #         for tm, trig2 in enumerate(Fired):
            #             # if tm >= tn: #Do self correllation to set the scale properly
            #             #Just do full correlation matrix
            #             self.trigLogic_Correl[lvl].Fill(trig.trigger + " (T{})".format(trig.tier), trig2.trigger + " (T{})".format(trig2.tier), weight)


        #############################################
        ### Define variable dictionary for values ###
        #############################################

        #FIXME: Muon and Electron baseline and selection boolean lists...
        #make a list with the successful idx's for each trigger path, then:
        #import itertools
        #muon_osv_baseline = list(itertools.repeat(False, len(muons)))
        #muon_osv_baseline[idx_0] = True
        #muon_osv_baseline[idx_1] = True

        # ('Muon_OSV_baseline', 'O', 'Passes TriggerAndSelectionLogic at baseline level', 'nMuon'),
        # ('Muon_OSV_selection', 'O', 'Passes TriggerAndSelectionLogic at selection level', 'nMuon'),
        # ('Electron_OSV_baseline', 'O', 'Passes TriggerAndSelectionLogic at baseline level', 'nElectron'),
        # ('Electron_OSV_selection', 'O', 'Passes TriggerAndSelectionLogic at selection level', 'nElectron'),
        branchVals = {}
        branchVals['ESV_TriggerAndSelectionLogic_hlt'] = (len(Vetoed) == 0 and len(Fired) > 0)
        branchVals['ESV_TriggerAndSelectionLogic_baseline'] = pass_baseline_bitset
        branchVals['ESV_TriggerAndSelectionLogic_selection'] = pass_selection_bitset
        for trig3 in self.eraTriggers:
            branchVals['ESV_TriggerEraBits_b{}'.format(trig3.uniqueEraBit)] = pass_baseline_lep[trig3.trigger]
            branchVals['ESV_TriggerEraBits_s{}'.format(trig3.uniqueEraBit)] = pass_selection_lep[trig3.trigger]

        ########################## 
        ### Write out branches ###
        ##########################         
        if self.out and self.mode == "Flag":
            for name, valType, valTitle, lVar in self.varTuple:
                self.out.fillBranch(name, branchVals[name])
        elif self.mode == "PassFail":
            #Do nothing
            pass
        elif self.mode == "Plot":
            #Do something?
            pass
            #Do pass through if plotting, make no assumptions about what should be done with the event
#FIXME            return True
        else:
            raise NotImplementedError("No method in place for TriggerAndSelectionLogic module in mode '{0}'".format(self.mode))


        if branchVals['ESV_TriggerAndSelectionLogic_{}'.format(self.passLevel)]:
            return True
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

    def genWeightFunc(self, event):
        #Default value is currently useless, since the tree reader array tool raises an exception anyway
        return math.copysign(self.weightMagnitude, getattr(event, "genWeight", 1))
    def backupWeightFunc(self, event):
        return self.weightMagnitude
    def dataWeightFunc(self, event):
        return 1


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
