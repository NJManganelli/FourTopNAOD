import json
from pprint import pprint
class FileLoader:
    """FileLoader takes as input an evenSet, era, and channel; it returns a list of files, a json, and a configuration dictionary.

eventSet: "TTTT", "TT", "DY", etc.
era: 2016, 2017, 2018. This corresponds to both MC tunes and Data run sets, as well as the default configuration parameters.
channel: SL or DL to return the appropriate configuration parameters that is loaded. Overriden by configName option.
configName: (Optional) When specified, returns the requested configuration instead of the standard one for that era and channel.
serverPrefix: the default prefix for files is root://cms-xrd-global.cern.ch/. Pass any other as a string in the same format. """

    def __init__(self, eventSet=None, era=None, channel=None, configName=None, jsonName=None, filePrefix="root://cms-xrd-global.cern.ch/"):
        #internal variables grabbed, except jsonName and configName
        self._eventSet = eventSet
        self._era = era
        self._channel = channel
        self._filePrefix = filePrefix
        
        #Make these all named options, but still require the first three to always be passed
        if (self._eventSet == None or self._era == None or self._channel == None):
            raise RuntimeError("FileLoader requires an eventSet, an era(2016, 2017, 2018), and an analysis channel(SL, DL)")

        #########################################
        ### USER DEFINED DATASETS and PATHS   ###
        ### Use convenient name and era       ###
        ### and finally indicate path inside  ###
        ### self._filePath defined first      ###
        ### Data must begin with "Run"        ###
        ### Monte Carlo must NOT              ###
        #########################################
        #Ensure JSON files are formatted properly using tool like https://jsonformatter.curiousconcept.com/
        self._jsonPath = "../jsons/"
        self._configPath = "../config/"
        self._filePath = "../filelists/"
        self._eventDict = { 
            "TTTT-PSweights" : { "2016" : "NOT IMPLEMENTED",
                                 "2017" : "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8.txt",
                                 "2018" : "NOT IMPLEMENTED" },
            "TTTT" :  { "2016" : "NOT IMPLEMENTED",
                        "2017" : "TTTT_TuneCP5_13TeV-amcatnlo-pythia8.txt",
                        "2018" : "NOT IMPLEMENTED" },
            "TTJetsSL" :  { "2016" : "NOT IMPLEMENTED",
                            "2017" : "TTJets_SingleLeptFromT_TuneCP5_13TeV-madgraphMLM-pythia8.txt",
                            "2018" : "NOT IMPLEMENTED" },
            "WJetsToLNu" :  { "2016" : "NOT IMPLEMENTED",
                              "2017" : "WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8.txt",
                              "2018" : "NOT IMPLEMENTED" },
            "DoubleMuonRunB" :  { "2016" : "NOT IMPLEMENTED",
                                  "2017" : "DoubleMuon_Run2017B-Nano14Dec2018-v1",
                                  "2018" : "NOT IMPLEMENTED" },
            "DoubleMuonRunC" :  { "2016" : "NOT IMPLEMENTED",
                                  "2017" : "DoubleMuon_Run2017C-Nano14Dec2018-v1",
                                  "2018" : "NOT IMPLEMENTED" },
            "DoubleMuonRunD" :  { "2016" : "NOT IMPLEMENTED",
                                  "2017" : "DoubleMuon_Run2017D-Nano14Dec2018-v1",
                                  "2018" : "NOT IMPLEMENTED" },
            "DoubleMuonRunE" :  { "2016" : "NOT IMPLEMENTED",
                                  "2017" : "DoubleMuon_Run2017E-Nano14Dec2018-v1",
                                  "2018" : "NOT IMPLEMENTED" },
            "DoubleMuonRunF" :  { "2016" : "NOT IMPLEMENTED",
                                  "2017" : "DoubleMuon_Run2017F-Nano14Dec2018-v1",
                                  "2018" : "NOT IMPLEMENTED" },
            "DoubleEGRunB" :  { "2016" : "NOT IMPLEMENTED",
                                "2017" : "DoubleEG_Run2017B-Nano14Dec2018-v1",
                                "2018" : "NOT IMPLEMENTED" },
            "DoubleEGRunC" :  { "2016" : "NOT IMPLEMENTED",
                                "2017" : "DoubleEG_Run2017C-Nano14Dec2018-v1",
                                "2018" : "NOT IMPLEMENTED" },
            "DoubleEGRunD" :  { "2016" : "NOT IMPLEMENTED",
                                "2017" : "DoubleEG_Run2017D-Nano14Dec2018-v1",
                                "2018" : "NOT IMPLEMENTED" },
            "DoubleEGRunE" :  { "2016" : "NOT IMPLEMENTED",
                                "2017" : "DoubleEG_Run2017E-Nano14Dec2018-v1",
                                "2018" : "NOT IMPLEMENTED" },
            "DoubleEGRunF" :  { "2016" : "NOT IMPLEMENTED",
                                "2017" : "DoubleEG_Run2017F-Nano14Dec2018-v1",
                                "2018" : "NOT IMPLEMENTED" },
            "MuonEGRunB" :  { "2016" : "NOT IMPLEMENTED",
                              "2017" : "MuonEG_Run2017B-Nano14Dec2018-v1",
                              "2018" : "NOT IMPLEMENTED" },
            "MuonEGRunC" :  { "2016" : "NOT IMPLEMENTED",
                              "2017" : "MuonEG_Run2017C-Nano14Dec2018-v1",
                              "2018" : "NOT IMPLEMENTED" },
            "MuonEGRunD" :  { "2016" : "NOT IMPLEMENTED",
                              "2017" : "MuonEG_Run2017D-Nano14Dec2018-v1",
                              "2018" : "NOT IMPLEMENTED" },
            "MuonEGRunE" :  { "2016" : "NOT IMPLEMENTED",
                              "2017" : "MuonEG_Run2017E-Nano14Dec2018-v1",
                              "2018" : "NOT IMPLEMENTED" },
            "MuonEGRunF" :  { "2016" : "NOT IMPLEMENTED",
                              "2017" : "MuonEG_Run2017F-Nano14Dec2018-v1",
                              "2018" : "NOT IMPLEMENTED" },
            }

        self._jsonDict = {"2016" : { "Golden" : "NOT IMPLEMENTED",
                                     "ReReco" : "NOT IMPLEMENTED"
                                     },
                          "2017" : { "Golden" : "NOT IMPLEMENTED",
                                     "ReReco" : "Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt"
                                     },
                          "2018" : { "Golden" : "NOT IMPLEMENTED",
                                     "ReReco" : "NOT IMPLEMENTED"
                                     }
                          }
        ######################################################
        ### Name all necessary inputs for convenience here ###
        ######################################################
        #Name configuration, using method that makes it convenient to add many without modifying this function
        self._configName = self._configPath + channel + "_" + era + "_"
        if configName is None:
            self._configName += "default.json"
        else:
            self._configName += configName
        if self._configName[-5:] != ".json":
            self._configName += ".json"
        #Name filelist input
        self._filelistName = self._filePath + self._eventDict[eventSet][era]
        #Grab jsonName from input
        self._jsonName = jsonName
        
        #################################
        ### Set up ToReturn variables ###
        #################################
        #name event JSON if Data and no jsonName was passed in
#        if self._eventSet[:3] is "Run":
        if "Run" in self._eventSet:
            if self._jsonName is None:
                self._jsonToReturn = self._jsonPath + self._jsonDict[era]["ReReco"]
                print(self._jsonToReturn)
            else:
                self.jsonToReturn = self._jsonPath + self._jsonName
        else:
            self._jsonToReturn = None
        #Empty filelistToReturn
        self._filelistToReturn = []
        #Empty config file
        self._configToReturn = {}

        #############################################
        ### hasLoaded boolean for invoking load() ###
        #############################################
        self._hasLoaded = False

    def __load__(self):
        #Open config file in read-only mode, then load the json
        with open(self._configName, "r") as inConfig:
            self._configToReturn = json.load(inConfig)

        #Test that the JSON file can be opened, then do just close it
        if self._jsonToReturn is not None:
            try:
                f = open(self._jsonToReturn, "r")
            except IOError:
                print("IOError: The Requested JSON ({0:s})file does not exist in the absolute/relative path specified by {1:s}".format(self._jsonName, self._jsonPath))
            finally:
                f.close()
            
        with open(self._filelistName, "r") as inFiles:
            for line in inFiles:
                self._filelistToReturn.append(self._filePrefix + str(line).replace('\n',''))
            
        self._hasLoaded = True
        
    def printEventSets(self):
        pprint(self._eventDict)

    def printConfig(self):
        if self._hasLoaded:
            pprint(self._configToReturn)
        else:
            print("A configuration has yet to be loaded. Invoke getConfig(), getFiles(), or getJSONPath() first.")

    def getFiles(self, indexOfFile=-1):
        if not self._hasLoaded:
            self.__load__()
        if indexOfFile < 0:
            return self._filelistToReturn
        elif indexOfFile > len(self._filelistToReturn):
            raise RuntimeError("You've requested a file that is beyond the index range available, which is 0 to {0:s}"
                               .format(self._filelistToReturn))
        else:
            return [self._filelistToReturn[indexOfFile]]

    def getConfig(self):
        if not self._hasLoaded:
            self.__load__()
        return self._configToReturn

    def getJSONPath(self):
        if not self._hasLoaded:
            self.__load__()
        return self._jsonToReturn

    def getSet(self):
        return self._eventSet

#Implement as class, create functions that return possible evensets, store internally so that these values to be returned (list of files, json) are always available through submethods...
