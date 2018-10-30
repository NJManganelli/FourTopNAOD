def FileLoader(eventSet=None, era=None, channel=None, configName=None, serverPrefix=None):
    """FileLoader takes as input an evenSet, era, and channel; it returns a list of files, a json, and a configuration dictionary.

eventSet: "TTTT", "TT", "DY", etc.
era: 2016, 2017, 2018. This corresponds to both MC tunes and Data run sets, as well as the default configuration parameters.
channel: SL or DL to return the appropriate configuration parameters that is loaded. Overriden by configName option.
configName: (Optional) When specified, returns the requested configuration instead of the standard one for that era and channel.
serverPrefix: the default prefix for files is root://cms-xrd-global.cern.ch/. Pass any other as a string in the same format. """

    if (eventSet == None or era == None or channel == None):
        raise RuntimeError("FileLoader requires an eventSet, an era(2016, 2017, 2018), and a channel(SL, DL).")
    eventDict = { 
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
#Implement as class, create functions that return possible evensets, store internally so that these values to be returned (list of files, json) are always available through submethods...
