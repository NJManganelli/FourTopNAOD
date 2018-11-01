import json
class FileLoader:
    """FileLoader takes as input an evenSet, era, and channel; it returns a list of files, a json, and a configuration dictionary.

eventSet: "TTTT", "TT", "DY", etc.
era: 2016, 2017, 2018. This corresponds to both MC tunes and Data run sets, as well as the default configuration parameters.
channel: SL or DL to return the appropriate configuration parameters that is loaded. Overriden by configName option.
configName: (Optional) When specified, returns the requested configuration instead of the standard one for that era and channel.
serverPrefix: the default prefix for files is root://cms-xrd-global.cern.ch/. Pass any other as a string in the same format. """

    def __init__(self, eventSet=None, era=None, channel=None, configName=None):
        #internal variables
        self._eventSet = eventSet
        self._era = era
        self._channel = channel
        
        #Make these all named options, but still require the first three to always be passed
        if (self._eventSet == None or self._era == None or self._channel == None):
            raise RuntimeError("FileLoader requires an eventSet, an era(2016, 2017, 2018), and an analysis channel(SL, DL)")

        #Here we define paths to the event jsons, the config jsons, and the eventSet
        self._jsonPath = "../json/"
        self._configPath = "../config/"
        self._filePath = "../filelists/"
        
        #Load configuration
        if configName == None:
            self._configName = self.configPath + channel + "_" + era + "_default.json"
        else:
            self._configName = self.configPath + channel + "_" + era + "_" + configName

        #The filelist(list of strings giving paths), configuration (dictionary), and event json(path) to be returned upon request
        self._filelist = []
        self._configuration
        #The Event data sets for our analysis, with keys eventSet and era
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
    def __load__(self):
        #Method to check that file paths are valid, safely handle their loading all at once
        #for now, just dumbly assume everything there for prototyping purpose, fix later if used
        
    def printEventSets(self):
        
    def getFiles(self, serverPrefix=None, oneFileIndex=None):
        self.__load__()

#Implement as class, create functions that return possible evensets, store internally so that these values to be returned (list of files, json) are always available through submethods...
