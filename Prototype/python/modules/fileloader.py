import json
from pprint import pprint
#TO DO: more safety, implement serverName feature for filelists "root://cms-xrd-global.cern.ch/ is only one available for now
class FileLoader:
    """FileLoader takes as input an evenSet, era, and channel; it returns a list of files, a json, and a configuration dictionary.

eventSet: "TTTT", "TT", "DY", etc.
era: 2016, 2017, 2018. This corresponds to both MC tunes and Data run sets, as well as the default configuration parameters.
channel: SL or DL to return the appropriate configuration parameters that is loaded. Overriden by configName option.
configName: (Optional) When specified, returns the requested configuration instead of the standard one for that era and channel.
serverPrefix: the default prefix for files is root://cms-xrd-global.cern.ch/. Pass any other as a string in the same format. """

    def __init__(self, eventSet=None, era=None, channel=None, configName=None, jsonName=None, filePrefix="root://cms-xrd-global.cern.ch/"):
        #internal variables grabbedn
        self._eventSet = eventSet
        self._era = era
        self._channel = channel
        self._configName = configName
        self._jsonName = jsonName
        self._filePrefix

        #Has loaded boolean for so __load__ only runs once
        self._hasLoaded = False
        
        #Make these all named options, but still require the first three to always be passed
        if (self._eventSet == None or self._era == None or self._channel == None):
            raise RuntimeError("FileLoader requires an eventSet, an era(2016, 2017, 2018), and an analysis channel(SL, DL)")

        #########################################
        ### USER DEFINED DATASETS and PATHS   ###
        ### Use convenient name and era       ###
        ### and finally indicate path inside  ###
        ### self._filePath defined first      ###
        ### Data must being with "Run"        ###
        ### Monte Carlo must NOT              ###
        #########################################
        self._jsonPath = "../json/"
        self._configPath = "../config/"
        self._filePath = "../filelists/"
        self._eventDict = { 
            "TTTT-PSweights" : { "2016" : "NOT IMPLEMENTED",
                                 "2017" : "../filelists/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8.txt",
                                 "2018" : "NOT IMPLEMENTED" },
            "TTTT" :  { "2016" : "NOT IMPLEMENTED",
                        "2017" : "../filelists/TTTT_TuneCP5_13TeV-amcatnlo-pythia8.txt",
                        "2018" : "NOT IMPLEMENTED" },
            "TTJetsSL" :  { "2016" : "NOT IMPLEMENTED",
                            "2017" : "../filelists/TTJets_SingleLeptFromT_TuneCP5_13TeV-madgraphMLM-pythia8.txt",
                            "2018" : "NOT IMPLEMENTED" },
            "WJetsToLNu" :  { "2016" : "NOT IMPLEMENTED",
                              "2017" : "../filelists/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8.txt",
                              "2018" : "NOT IMPLEMENTED" },
            "RunB" :  { "2016" : "NOT IMPLEMENTED",
                        "2017" : "NOT IMPLEMENTED",
                        "2018" : "NOT IMPLEMENTED" },
            "RunC" :  { "2016" : "NOT IMPLEMENTED",
                        "2017" : "NOT IMPLEMENTED",
                        "2018" : "NOT IMPLEMENTED" },
            "RunD" :  { "2016" : "NOT IMPLEMENTED",
                        "2017" : "NOT IMPLEMENTED",
                        "2018" : "NOT IMPLEMENTED" },
            "RunE" :  { "2016" : "NOT IMPLEMENTED",
                        "2017" : "NOT IMPLEMENTED",
                        "2018" : "NOT IMPLEMENTED" },
            "RunF" :  { "2016" : "NOT IMPLEMENTED",
                        "2017" : "NOT IMPLEMENTED",
                        "2018" : "NOT IMPLEMENTED" },
            "RunG" :  { "2016" : "NOT IMPLEMENTED",
                        "2017" : "NOT IMPLEMENTED",
                        "2018" : "NOT IMPLEMENTED" },
            "RunH" :  { "2016" : "NOT IMPLEMENTED",
                        "2017" : "NOT IMPLEMENTED",
                        "2018" : "NOT IMPLEMENTED" }
            }

        ######################################################
        ### Name all necessary inputs for convenience here ###
        ######################################################
        #Name configuration, using method that makes it convenient to add many without modifying this function
        if configName is None:
            self._configName = self.configPath + channel + "_" + era + "_default.json"
        else:
            self._configName = self.configPath + channel + "_" + era + "_" + configName + (".json" if configName[-5:] is not ".json")
        #Name filelist input
        self._filelistName = self._filePath + self._eventDict[eventSet][era]
        #name event JSON if Data and no jsonName was passed in
        if eventSet[:3] is "Run" and self._jsonName is None:
            self._jsonToReturn = self._jsonPath + "Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt"

    def __load__(self):
        #Open config file in read-only mode, then load the json
        try: #is this necessary, or implemented in "with" syntax automatically?
            with open(self._configName, "r") as inConfig:
                self._configToReturn = json.load(inConfig)
        finally:
            inConfig.close()

        #Test that the JSON file can be opened, then do just close it
        if self._jsonToReturn is not None:
            try:
                f = open(self._jsonToReturn, "r")
            finally:
                f.close()
            
        try:
            f2 = open(self._filelistName, "r")
            for line in f2:
                self._filelistToReturn.append(self._filePrefix + str(line).replace('\n',''))
        finally:
            f2.close()
            
        self._filelistToReturn =
        self._hasLoaded = True
        
    def printEventSets(self):
        pprint(self._eventDict)

    def printConfig(self):
        pprint(self._configToReturn)

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

    def getJSONpath(self):
        if not self._hasLoaded:
            self.__load__()
        return self._jsonToReturn

#Implement as class, create functions that return possible evensets, store internally so that these values to be returned (list of files, json) are always available through submethods...
