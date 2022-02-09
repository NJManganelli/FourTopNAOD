import ROOT
from FourTopNAOD.RDF.io.root import bookSnapshot
from FourTopNAOD.RDF.tools.branchselection import BranchSelection

def getNtupleVariables(vals, isData=True, channel="all", era=None, sysVariations=None, sysFilter=["$NOMINAL"],bTagger="DeepJet"):
    if era is None:
        raise ValueError
    varsToFlattenOrSave = []
    varsToFlattenOrSave += ["run", 
                            "luminosityBlock", 
                            "event", 
                            "genWeight"
    ]
    for leppostfix in [""]:
        varsToFlattenOrSave += [
            "FTALepton{lpf}_pt".format(lpf=leppostfix), 
            "FTALepton{lpf}_eta".format(lpf=leppostfix),
            "FTALepton{lpf}_phi".format(lpf=leppostfix),
            # "FTALepton{lpf}_jetIdx".format(lpf=leppostfix),
            "FTALepton{lpf}_pdgId".format(lpf=leppostfix),
            # "FTALepton{lpf}_dRll".format(lpf=leppostfix),
            # "FTALepton{lpf}_dPhill".format(lpf=leppostfix),
            # "FTALepton{lpf}_dEtall".format(lpf=leppostfix),
            "FTAMuon{lpf}_pt".format(lpf=leppostfix), 
            "FTAMuon{lpf}_eta".format(lpf=leppostfix),
            "FTAMuon{lpf}_InvariantMass",
            "FTAElectron{lpf}_pt".format(lpf=leppostfix), 
            "FTAElectron{lpf}_eta".format(lpf=leppostfix),
            "FTAElectron{lpf}_InvariantMass",
            "MTofMETandMu{bpf}",
            "MTofMETandEl{bpf}",
            "MTofElandMu{bpf}"            
        ]
    if isData:
        branchPostFixes = ["__$NOMINAL".replace("$NOMINAL", "nom")]
    else:
        branchPostFixes = ["__" + sysVarRaw.replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', '')).replace("$ERA", era) 
                           for sysVarRaw, sysDict in sysVariations.items() if sysVarRaw in sysFilter and sysDict.get("weightVariation", True) is False]
    for branchpostfix in branchPostFixes:
        varsToFlattenOrSave += [
            "nFTAJet{bpf}".format(bpf=branchpostfix),
            # "FTAJet{bpf}_ptsort".format(bpf=branchpostfix), #sorting index...
            # "FTAJet{bpf}_deepcsvsort".format(bpf=branchpostfix),
            # "FTAJet{bpf}_deepjetsort".format(bpf=branchpostfix), #This is the sorting index...
            # "FTAJet{bpf}_idx".format(bpf=branchpostfix),
            "FTAJet{bpf}_pt".format(bpf=branchpostfix),
            "FTAJet{bpf}_eta".format(bpf=branchpostfix),
            "FTAJet{bpf}_phi".format(bpf=branchpostfix),
            # "FTAJet{bpf}_mass".format(bpf=branchpostfix),
            # "FTAJet{bpf}_jetId".format(bpf=branchpostfix),
            "ST{bpf}".format(bpf=branchpostfix),
            "HT{bpf}".format(bpf=branchpostfix),
            "HT2M{bpf}".format(bpf=branchpostfix),
            "HTRat{bpf}".format(bpf=branchpostfix),
            "dRbb{bpf}".format(bpf=branchpostfix),
            "H{bpf}".format(bpf=branchpostfix),
            "H2M{bpf}".format(bpf=branchpostfix),
            "HTH{bpf}".format(bpf=branchpostfix),
            "HTb{bpf}".format(bpf=branchpostfix),
            # "dPhibb{bpf}".format(bpf=branchpostfix),
            # "dEtabb{bpf}".format(bpf=branchpostfix),
        ]
        if bTagger.lower() == "deepjet":
            varsToFlattenOrSave += [
                "FTAJet{bpf}_DeepJetB".format(bpf=branchpostfix),
                "FTAJet{bpf}_DeepJetB_sorted".format(bpf=branchpostfix),
                "nLooseDeepJetB{bpf}".format(bpf=branchpostfix),
                "nMediumDeepJetB{bpf}".format(bpf=branchpostfix),
                "nTightDeepJetB{bpf}".format(bpf=branchpostfix),
                # "FTAJet{bpf}_LooseDeepJetB".format(bpf=branchpostfix),
                # "FTAJet{bpf}_MediumDeepJetB".format(bpf=branchpostfix),
                # "FTAJet{bpf}_TightDeepJetB".format(bpf=branchpostfix),
            ]
        if bTagger.lower() == "deepcsv":
            varsToFlattenOrSave += [
                "FTAJet{bpf}_DeepCSVB".format(bpf=branchpostfix),
                "FTAJet{bpf}_DeepCSVB_sorted".format(bpf=branchpostfix),
                "nLooseDeepCSVB{bpf}".format(bpf=branchpostfix),
                "nMediumDeepCSVB{bpf}".format(bpf=branchpostfix),
                "nTightDeepCSVB{bpf}".format(bpf=branchpostfix),
                # "FTAJet{bpf}_LooseDeepCSVB".format(bpf=branchpostfix),
                # "FTAJet{bpf}_MediumDeepCSVB".format(bpf=branchpostfix),
                # "FTAJet{bpf}_TightDeepCSVB".format(bpf=branchpostfix),
            ]
        if bTagger.lower() == "csvv2":
            varsToFlattenOrSave += [
                "FTAJet{bpf}_CSVv2B".format(bpf=branchpostfix),
                "FTAJet{bpf}_CSVv2B_sorted".format(bpf=branchpostfix),
                "nLooseCSVv2B{bpf}".format(bpf=branchpostfix),
                "nMediumCSVv2B{bpf}".format(bpf=branchpostfix),
                "nTightCSVv2B{bpf}".format(bpf=branchpostfix),
            ]
    return varsToFlattenOrSave


def delegateFlattening(inputDF, varsToFlatten, channel=None, debug=False):
    """Function that contains info about which variables to flatten and delegates this to functions, returning the RDataFrame after flattened variables have been defined."""

    ntupleVariables = ROOT.std.vector(str)(0) #Final variables that have been flattened and need to be returned to caller
    allColumns = inputDF.GetColumnNames()
    definedColumns = inputDF.GetDefinedColumnNames()
    rdf = inputDF
    skippedVars = [] #Skipped due to not being in the list
    flattenedVars = [] #Need to be flattened (parent variable, not post-flattening children)
    flatVars = [] #Already flat

    for var in allColumns:
        strVar = str(var)
        if var not in varsToFlatten:
            skippedVars.append(strVar)
            continue
        if "ROOT::VecOps::RVec" in rdf.GetColumnType(strVar):
            if debug:
                print("Flatten {}".format(strVar))
            if "FTAMuon" in strVar:
                if "mumu" in channel.lower():
                    depth = 2
                elif "elmu" in channel.lower():
                    depth = 1
                elif "elel" in channel.lower():
                    depth = 0
                else:
                    depth = 2
            if "FTALepton" in strVar:
                depth = 2
            if "FTAElectron" in strVar:
                if "mumu" in channel.lower():
                    depth = 0
                elif "elmu" in channel.lower():
                    depth = 1
                elif "elel" in channel.lower():
                    depth = 2
                else:
                    depth = 2
            if "FTAJet" in strVar:
                depth = 10
            else:
                depth = 2
            flattenedVars.append(strVar)
            rdf, iterFlattenedVars = flattenVariable(rdf, strVar, depth, static_cast=True, fallback=None, debug=debug)
            for fvar in iterFlattenedVars:
                ntupleVariables.push_back(fvar)
        else:
            # if debug:
            #     print("Retain {}".format(strVar))
            flatVars.append(strVar)
            ntupleVariables.push_back(strVar)
        
    for c in ntupleVariables:
        if debug:
            print("{:45s} | {}".format(c, rdf.GetColumnType(c)))
    
    return rdf, {"ntupleVariables": ntupleVariables, "flattenedVars": flattenedVars, "flatVars": flatVars, "skippedVars": skippedVars}

def flattenVariable(input_df, var, depth, static_cast=None, fallback=None, debug=False):
    """Take an RVec or std::vector of variables and define new columns for the first n (depth) elements, falling back to a default value if less than n elements are in an event."""

    rdf = input_df
    t = rdf.GetColumnType(var) #Get the type for deduction of casting rule and fallback value
    flats = [] #Store the defined variables so they may be added to a list for writing
    if static_cast is True: #deduce the static_cast and store the beginning and end of the wrapper in 'sci' and 'sce'
        sce = ")"
        if "<double>" in t.lower() or "<double_t>" in t.lower():
            sci = "static_cast<Double_t>("
            # sci = "static_cast<Float_t>("
        if "<float>" in t.lower() or "<float_t>" in t.lower():
            # sci = "static_cast<Double_t>("
            sci = "static_cast<Float_t>("
        elif "<uint>" in t.lower() or "<uint_t>" in t.lower() or "<unsigned char>" in t.lower() or "<uchar_t>" in t.lower():
            # sci = "static_cast<Uint_t>("
            sci = "static_cast<unsigned int>("
        elif "<int>" in t.lower() or "<int_t>" in t.lower():
            sci = "static_cast<Int_t>("
        elif "<bool" in t.lower():
            sci = "static_cast<Bool_t>("
        elif "<unsigned long>" in t.lower():
            sci = "static_cast<unsigned long>(" 
        else:
            raise NotImplementedError("No known casting rule for variable {} of type {}".format(var, t))
    elif isinstance(static_cast, str):
        sce = ")"
        sci = static_cast
    else:
        sce = ""
        sci = ""

    if isinstance(fallback, (float, int)):
        fb = fallback
    else:
        if "<double>" or "<float>" in t:
            fb = -9876.54321
        elif "<uint>" in t:
            fb = 0
        elif "<int>" in t:
            fb = -9876
        else:
            raise NotImplementedError("No known fallback rule")        

    for x in range(depth):
        split_name = str(var).split("_")
        to_replace = split_name[0]
        name = str(var).replace(to_replace, "{tr}{n}".format(tr=to_replace, n=x+1))
        # name = "{var}{n}".format(var=var, n=x+1)
        flats.append(name)
        defn = "{var}.size() > {x} ? {sci}{var}.at({x}){sce} : {fb}".format(sci=sci, var=str(var), x=x, sce=sce, fb=fb)
        if debug:
            print("{} : {}".format(name, defn))
        rdf = rdf.Define(name, defn)

    return rdf, flats

def writeNtuples(packedNodes, ntupledir, nJetMin=4, HTMin=350, bTagger="DeepJet"):
    # Use reversed order to cycle from highest priority level to lowest, finally calling snapshot on lowest priority level greater than 0
    snapshotTrigger = sorted([p for p in packedNodes["snapshotPriority"].values() if p > 0])
    if len(snapshotTrigger) > 0:
        snapshotTrigger = snapshotTrigger[0]
    else:
        #There is only the inclusive process...
        snapshotTrigger = -1
    #Prepare cacheNodes
    if "cacheNodes" not in packedNodes:
        packedNodes["cacheNodes"] = dict()
    handles = dict()
    for eraAndSampleName, spriority in sorted(packedNodes["snapshotPriority"].items(), key=lambda x: x[1], reverse=True):
        sval = packedNodes["nodes"][eraAndSampleName]
        if eraAndSampleName == "BaseNode": continue #Skip the pre-split node
        snapshotPriority = packedNodes["snapshotPriority"][eraAndSampleName]
        if snapshotTrigger > 0 and snapshotPriority < 0:
            print("Skipping snapshotPriority < 0 node")
            continue
        if snapshotPriority == 0:
            print("Warning, snapshotPriority 0 node! This points to a splitProcess config without (properly) defined priority value")
            continue
        if snapshotPriority > snapshotTrigger:
            print("NEED TO FILTER NODES BY THIS POINT TO MAINTAIN SMALL SNAPSHOT AND CACHE SIZES! Temp in place")
            #cache and book snapshot (assuming it will not be written due to the RDF bugs) #FILTER HERE
            handles[eraAndSampleName] = bookSnapshot(packedNodes["nodes"][eraAndSampleName]["BaseNode"]\
                                                     .Filter("HT__nom > {htmin} && nFTAJet__nom > {njetmin} && nFTALepton == 2 && nMediumDeepJetB__nom >= 2"\
                                                             .format(htmin=HTMin, njetmin=nJetMin)),
                                                     "{}/{}.root".format(ntupledir, eraAndSampleName), lazy=True,
                                                     columnList=packedNodes["ntupleVariables"][eraAndSampleName], treename="Events", 
                                                     mode="RECREATE", compressionAlgo="ZSTD", compressionLevel=6, splitLevel=99)            
        else:
            print("Executing event loop for writeNtuples()")
            handles[eraAndSampleName] = bookSnapshot(packedNodes["nodes"][eraAndSampleName]["BaseNode"]\
                                                     .Filter("HT__nom > 450 && nFTAJet__nom > 3 && nFTALepton == 2 && nMediumDeepJetB__nom >= 2"), 
                                                     "{}/{}.root".format(ntupledir, eraAndSampleName), lazy=False, 
                                                     columnList=packedNodes["ntupleVariables"][eraAndSampleName], 
                                                     treename="Events", mode="RECREATE", compressionAlgo="ZSTD", compressionLevel=6, splitLevel=99)
    print("Finished executing event loop for writeNtuples()")

def delegateSnapshots(packedNodes, ntupledir, branchselfile, verbose=False):
    """Lazily book snapshots for all nodes with snapshotPriority > 0, saving the selected columns."""
    #Lazily book snapshots for all the nodes with snapshot priority > 0, which previously ordered things to keep caches small. 
    #Now we depend on simultaneous snapshotting to work
    # Use reversed order to cycle from highest priority level to lowest
    snapshotTrigger = sorted([p for p in packedNodes["snapshotPriority"].values() if p > 0])
    if len(snapshotTrigger) > 0:
        snapshotTrigger = snapshotTrigger[0]
    else:
        #There is only the inclusive process...
        snapshotTrigger = -1

    handles = dict()
    columns = dict()
    br_selector = BranchSelection(branchselfile)
    for eraAndSampleName, spriority in sorted(packedNodes["snapshotPriority"].items(), key=lambda x: x[1], reverse=True):
        sval = packedNodes["nodes"][eraAndSampleName]
        if eraAndSampleName == "BaseNode": continue #Skip the pre-split node
        snapshotPriority = packedNodes["snapshotPriority"][eraAndSampleName]
        if snapshotPriority <= 0:
            continue
        else:
            columns[eraAndSampleName] = br_selector.selectBranches(packedNodes["nodes"][eraAndSampleName]["BaseNode"], verbose=verbose)
            handles[eraAndSampleName] = bookSnapshot(packedNodes["nodes"][eraAndSampleName]["BaseNode"],
                                                     f"{ntupledir}/{eraAndSampleName}.root", 
                                                     lazy=True,
                                                     columnList=columns[eraAndSampleName], 
                                                     treename="Events", 
                                                     mode="RECREATE", 
                                                     compressionAlgo="ZSTD", 
                                                     compressionLevel=6, 
                                                     splitLevel=99,
                                                 )
    print(len(list(columns.values())[0]))
    print("Taking columns:", list(columns.values())[0])
    return handles, columns
