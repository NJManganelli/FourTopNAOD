import os
import ROOT
def writeHistosForCombine(histDict, directory, levelsOfInterest, dict_key="Mountains", mode="RECREATE"):
    rootDict = {}
    if not os.path.isdir(directory):
        os.makedirs(directory)
    for name, levelsDict in histDict.items():
        for level, objDict in levelsDict.items():
            if level not in levelsOfInterest: continue
            if not os.path.isdir(directory + "/" + level):
                os.makedirs(directory + "/" + level)
            for preObjName, objVal in objDict[dict_key].items():
                for hname, hist in objVal.items():
                    dictKey = preObjName + "_" + hname
                    if dictKey not in rootDict:
                        rootDict[dictKey] = ROOT.TFile.Open("{}.root".format(directory + "/" + level + "/"+ dictKey), mode)
                    rootDict[dictKey].cd()
                    hptr = hist.GetPtr()
                    oldname = hptr.GetName()
                    hptr.SetName("{}".format(name))
                    hptr.Write()
                    hptr.SetName("{}".format(oldname)) #Avoid overwriting things by switching back, save from segfault
                    #hptr.SetDirectory(0)
    for f in rootDict.values():
        f.Close()
        
def writeHistosV1(histDict, directory, levelsOfInterest="All", samplesOfInterest="All", dict_keys="All", mode="RECREATE"):
    rootDict = {}
    if not os.path.isdir(directory):
        os.makedirs(directory)
    for name, levelsDict in histDict.items():
        if samplesOfInterest == "All": pass
        elif name not in samplesOfInterest: continue
        for level, objDict in levelsDict.items():
            if levelsOfInterest == "All": pass
            elif level not in levelsOfInterest: continue
            if not os.path.isdir(directory + "/" + level):
                os.makedirs(directory + "/" + level)
            rootDict[name] = ROOT.TFile.Open("{}.root".format(directory + "/" + level + "/"+ name), mode)
            for dict_key in objDict.keys():
                if dict_keys == "All": pass
                elif dict_key not in dict_keys: continue

                for preObjName, objVal in objDict[dict_key].items():
                    if type(objVal) == dict:
                        for hname, hist in objVal.items():
                            #help(hist)
                            #dictKey = preObjName + "$" + hname
                            #if dictKey not in rootDict:
                            #rootDict[dictKey].cd()
                            hptr = hist.GetPtr()
                            oldname = hptr.GetName()
                            #hptr.SetName("{}".format(dict_key + "*" + preObjName + "*" + hname))
                            hptr.Write()
                            #hptr.SetName("{}".format(oldname)) #Avoid overwriting things by switching back, save from segfault
                    elif "ROOT.TH" in str(type(objVal)):
                        hptr = objVal.GetPtr()
                        oldname = hptr.GetName()
                        #hptr.SetName("{}".format(dict_key + "*" + preObjName))
                        hptr.Write()
                        #hptr.SetName("{}".format(oldname)) #Avoid overwriting things by switching back, save from segfault
            print("Wrote histogram file for {} - {}".format(name, directory + "/" + level + "/"+ name))
    for f in rootDict.values():
        f.Close()

def writeHistos(histDict, directory, variableSet="NA", categorySet="NA", samplesOfInterest="All", systematicsOfInterest="All",
                channelsOfInterest="All", dict_keys="All", mode="RECREATE", compatibility=False):
    rootDict = {}
    if not os.path.isdir(directory):
        os.makedirs(directory)
    if len(histDict.keys()) < 1: print("writeHistos::no histDict keys")
    nameCounter = 0
    channelCounter = 0
    objCounter = 0
    nameCounterSkipped = 0
    channelCounterSkipped = 0
    for name, channelsDict in histDict.items():
        nameCounter += 1
        if isinstance(samplesOfInterest, str) and samplesOfInterest.lower() == "all": pass
        elif name not in samplesOfInterest: 
            nameCounterSkipped += 1
            continue
        for channel, objDict in channelsDict.items():
            channelCounter += 1
            counter = 0
            if isinstance(channelsOfInterest, str) and channelsOfInterest.lower() == "all": pass
            elif channel  not in channelsOfInterest: 
                channelCounterSkipped += 1
                continue
            elif len(objDict.values()) < 1:
                print("No objects to write, not creating directory or writing root file for {} {}".format(name, channel))
                continue
            #Cute way to format the name as 'blah.root' or 'blah.nominal.ps.rf.root'
            if isinstance(systematicsOfInterest, str) and systematicsOfInterest.lower() == "all":
                systematicsDescriptors = ["all"]
            elif isinstance(systematicsOfInterest, list) and len(systematicsOfInterest) == 1 and systematicsOfInterest[0].lower() == "all": #Handle case of passing the systematicsSet the option 'ALL'
                systematicsDescriptors = ["all"]
            else:
                systematicsDescriptors = ["__".join(systematicsOfInterest)]
            if compatibility:
                formattedFileName = directory + "/" + channel + "/" + name + ".root"
            else:
                formattedFileName = directory + "/" + channel + "/" + name + "___".join(["", str(variableSet),str(categorySet)]+systematicsDescriptors) + ".root"
            if not os.path.isdir(directory + "/" + channel):
                os.makedirs(directory + "/" + channel)
            # rootFileName = "{}{}".format(directory + "/" + channel + "/"+ name, ".".join(systematicsAndRoot))
            # rootDict[name] = ROOT.TFile.Open("{}".format(rootFileName), mode)
            rootDict[name] = ROOT.TFile.Open("{}".format(formattedFileName), mode)
            # for dict_key in objDict.keys():
            #     if dict_keys == "All": pass
            #     elif dict_key not in dict_keys: continue
            for objname, obj in objDict.items():
                objCounter += 1
                if type(obj) == dict:
                    for hname, hist in obj.items():
                        if "ROOT.RDF.RResultPtr" in str(type(obj)):
                            hptr = hist.GetPtr()
                        else:
                            hptr = hist
                        hptr.Write()
                        counter += 1
                elif "ROOT.RDF.RResultPtr" in str(type(obj)):
                    hptr = obj.GetPtr()
                else:
                    hptr = obj
                hptr.Write()
                counter += 1
            print("Wrote {} histograms into file for {}::{} - {}".format(counter, name, channel, formattedFileName))
            rootDict[name].Close()
    print("samples skipped/cycled: {}/{}\tchannels skipped/cycled: {}/{}\tobjects cycled: {}".format(nameCounterSkipped,
                                                                                                     nameCounter, 
                                                                                                     channelCounterSkipped,
                                                                                                     channelCounter,
                                                                                                     objCounter
                                                                                                 ))

def bookSnapshot(input_df, filename, columnList, lazy=True, treename="Events", mode="RECREATE", compressionAlgo="LZ4", compressionLevel=6, splitLevel=99, debug=False):
    if columnList is None:
        raise RuntimeError("Cannot take empty columnList in bookSnapshot")
    elif isinstance(columnList, str) or 'vector<string>' in str(type(columnList)):
        columns = columnList #regexp case or vector of strings
    elif isinstance(columnList, list):
        columns = ROOT.std.vector(str)()
        for col in columnList:
            columns.push_back(col)
    else:
        raise RuntimeError("Cannot handle columnList of type {} in bookSnapshot".format(type(columnList)))
        
    Algos = {"ZLIB": 1,
             "LZMA": 2,
             "LZ4": 4,
             "ZSTD": 5
         }
    sopt = ROOT.RDF.RSnapshotOptions(mode, Algos[compressionAlgo], compressionLevel, 0, splitLevel, True) #lazy is last option
    if lazy is False:
        sopt.fLazy = False
    handle = input_df.Snapshot(treename, filename, columns, sopt)

    return handle

