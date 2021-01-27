import array
import collections
import pdb
import ROOT
import ruamel.yaml

def fill_histos_ndim(input_df_or_nodes, splitProcess, 
                     sampleName=None, 
                     channel="All", 
                     isData=True, 
                     era="2017", 
                     histosDict=None,
                     doDiagnostics=True, 
                     doCombineHistosOnly=False, 
                     nJetsToHisto=10, 
                     bTagger="DeepCSV",
                     HTCut=500, 
                     ZMassMETWindow=[15.0, 0.0],
                     sysVariations={"$NOMINAL": {"jet_mask": "jet_mask",
                                                 "lep_postfix": "",
                                                 "jet_pt_var": "Jet_pt",
                                                 "jet_mass_var": "Jet_mass",
                                                 "met_pt_var": "METFixEE2017_pt",
                                                 "met_phi_var": "METFixEE2017_phi",
                                                 "btagSF": "Jet_btagSF_deepcsv_shape",
                                                 "weightVariation": False},
                                },
                     sysFilter=["$NOMINAL"],
                     skipNominalHistos=False,
                     verbose=False,
                 ):
    """Method to fill histograms given an input RDataFrame, input sample/dataset name, input histogram dictionaries.
    Has several options of which histograms to fill, such as Leptons, Jets, Weights, EventVars, etc.
    Types of histograms (1D, 2D, those which will not be stacked(NS - histosNS)) are filled by passing non-None
    value to that histosXX_dict variable. Internally stored with structure separating the categories of histos,
    with 'Muons,' 'Electrons,' 'Leptons,' 'Jets,' 'EventVars,' 'Weights' subcategories.
    
    ZMassMETWindow = [<invariant mass halfwidth>, <METCut>] - If in the same-flavor dilepton channel, require 
    abs(DileptonInvMass - ZMass) < ZWindowHalfWidth and MET >= METCut
    """
    

    if bTagger.lower() == "deepcsv":
        tagger = "DeepCSVB"
    elif bTagger.lower() == "deepjet":
        tagger = "DeepJetB"
    elif bTagger.lower() == "csvv2":
        tagger = "CSVv2B"
    else:
        raise RuntimeError("{} is not a supported bTagger option in fillHistos()".format(bTagger))
    combineHistoTemplate = []    
    #Variables to save for Combine when doCombineHistosOnly=True
    # combineHistoTemplate = ["HT{bpf}"]
    # combineHistoTemplate = ["HT{bpf}", "ST{bpf}", "HTH{bpf}", "HTRat{bpf}", "HTb{bpf}", "HT2M{bpf}", "H{bpf}", "H2M{bpf}", "dRbb{bpf}", 
    #                          # "FTALepton_dRll", 
    #                          "FTALepton1_pt", "FTALepton1_eta",
    #                          "FTALepton2_pt", "FTALepton2_eta", 
    #                          "FTAMuon_InvariantMass", "FTAElectron_InvariantMass",
    #                          "MTofMETandMu{bpf}", "MTofMETandEl{bpf}", "MTofElandMu{bpf}"
    #                          "nFTAJet{bpf}", 
    #                          "FTAJet1{bpf}_pt", "FTAJet1{bpf}_eta", "FTAJet1{bpf}_DeepJetB", 
    #                          "FTAJet2{bpf}_pt", "FTAJet2{bpf}_eta", "FTAJet2{bpf}_DeepJetB", 
    #                          "FTAJet3{bpf}_pt", "FTAJet3{bpf}_eta", "FTAJet3{bpf}_DeepJetB", 
    #                          "FTAJet4{bpf}_pt", "FTAJet4{bpf}_eta", "FTAJet4{bpf}_DeepJetB",
    #                          # "nLooseFTAMuon", "nMediumFTAMuon", "nTightFTAMuon",
    #                          # "nLooseFTAElectron", "nMediumFTAElectron", "nTightFTAElectron",
    #                          # "nLooseFTALepton", "nMediumFTALepton", "nTightFTALepton",
    #                      ]
    if bTagger.lower() == "deepjet":
        combineHistoTemplate += ["nLooseDeepJetB{bpf}", "nMediumDeepJetB{bpf}", "nTightDeepJetB{bpf}",]
    elif bTagger.lower() == "deepcsv":
        combineHistoTemplate += ["nLooseDeepCSVB{bpf}", "nMediumDeepCSVB{bpf}", "nTightDeepCSVB{bpf}",]
    elif bTagger.lower() == "csvv2":
        combineHistoTemplate += ["nLooseCSVv2B{bpf}", "nMediumCSVv2B{bpf}", "nTightCSVv2B{bpf}",]

    print("\n\nDisabled histo templates except HT!!!!!\n\n")
    combineHistoTemplate = ["HT{bpf}",]

    #Fill this list with variables for each branchpostfix
    combineHistoVariables = [] 
    pi = ROOT.TMath.Pi()
    #Get the list of defined columns for checks
    histoNodes = histosDict #Inherit this from initiliazation, this is where the histograms will actually be stored
    if isinstance(input_df_or_nodes, (dict, collections.OrderedDict)):
        filterNodes = input_df_or_nodes.get("filterNodes")
        nodes = input_df_or_nodes.get("nodes")
        defineNodes = input_df_or_nodes.get("defineNodes")
        diagnosticNodes = input_df_or_nodes.get("diagnosticNodes")
        countNodes = input_df_or_nodes.get("countNodes")
    else:
        filterNodes = collections.OrderedDict()
        nodes = collections.OrderedDict()
        defineNodes = collections.OrderedDict()
        diagnosticNodes = collections.OrderedDict()
        countNodes = collections.OrderedDict()
        eraAndSampleName = era + "___" + sampleName #Easy case without on-the-fly ttbb, ttcc, etc. categorization
        nodes["BaseNode"] = input_df_or_nodes #Always store the base node we'll build upon in the next level
        #The below references branchpostfix since we only need nodes for these types of scale variations...
        if eraAndSampleName not in nodes:
            #L-2 filter, should be the packedEventID filter in that case
            filterNodes[eraAndSampleName] = collections.OrderedDict()
            filterNodes[eraAndSampleName]["BaseNode"] = ("return true;", "{}".format(eraAndSampleName), eraAndSampleName, None, None, None, None)
            nodes[eraAndSampleName] = collections.OrderedDict()
            nodes[eraAndSampleName]["BaseNode"] = nodes["BaseNode"].Filter(filterNodes[eraAndSampleName]["BaseNode"][0], filterNodes[eraAndSampleName]["BaseNode"][1])
            countNodes[eraAndSampleName] = collections.OrderedDict()
            countNodes[eraAndSampleName]["BaseNode"] = nodes[eraAndSampleName]["BaseNode"].Count()
            diagnosticNodes[eraAndSampleName] = collections.OrderedDict()
            defineNodes[eraAndSampleName] = collections.OrderedDict()


    #Make sure the nominal is done first so that categorization is successful
    for sysVarRaw, sysDict in sorted(sysVariations.items(), key=lambda x: "$NOMINAL" in x[0], reverse=True):
        #skip systematic variations on data, only do the nominal
        if isData and sysVarRaw != "$NOMINAL": 
            continue
        #Only do systematics that are in the filter list (storing raw systematic names...
        if sysVarRaw not in sysFilter:
            continue
        #get final systematic name
        sysVar = sysVarRaw.replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', '')).replace("$ERA", era)
        #skip making MET corrections unless it is: Nominal or a scale variation (i.e. JES up...)
        isWeightVariation = sysDict.get("weightVariation", False)
        #jetMask = sysDict.get("jet_mask").replace("$SYSTEMATIC", sysVar).replace("$LEP_POSTFIX", sysDict.get('lep_postfix', ''))
        #jetPt = sysDict.get("jet_pt_var")
        #jetMass = sysDict.get("jet_mass_var")
        #Name histograms with their actual systematic variation postfix, using the convention that HISTO_NAME__nom is
        # the nominal and HISTO_NAME__$SYSTEMATIC is the variation, like so:
        syspostfix = "___nom" if sysVarRaw == "$NOMINAL" else "___{}".format(sysVar)
        #Rename systematics on a per-sample basis, rest of code in the eraAndSampleName cycle
        systematicRemapping = sysDict.get("sampleRemapping", None)
        #name branches for filling with the nominal postfix if weight variations, and systematic postfix if scale variation (jes_up, etc.)
        branchpostfix = None
        if isWeightVariation:
            branchpostfix = "__nom"
        else:
            branchpostfix = "__" + sysVar
        leppostfix = sysDict.get("lep_postfix", "") #No variation on this yet, but just in case
        combineHistoVariables += [templateVar.format(bpf=branchpostfix) for templateVar in combineHistoTemplate]

        
        fillJet = "FTAJet{bpf}".format(bpf=branchpostfix)
        fillJetEnumerated = "FTAJet{{n}}{bpf}".format(bpf=branchpostfix)
        fillJet_pt = "FTAJet{bpf}_pt".format(bpf=branchpostfix)
        fillJet_phi = "FTAJet{bpf}_phi".format(bpf=branchpostfix)
        fillJet_eta = "FTAJet{bpf}_eta".format(bpf=branchpostfix)
        fillJet_mass = "FTAJet{bpf}_mass".format(bpf=branchpostfix)
        fillMET_pt = "FTAMET{bpf}_pt".format(bpf=branchpostfix)
        fillMET_phi = "FTAMET{bpf}_phi".format(bpf=branchpostfix)
        fillMET_uncorr_pt = sysDict.get("met_pt_var", "MET_pt")
        fillMET_uncorr_phi = sysDict.get("met_phi_var", "MET_phi")

        if verbose:
            print("Systematic: {spf} \n\t - Branch: {bpf}\n\t - Jets: {fj}=({fjp}, {fji}, {fje}"\
                  ", {fjm})\n\t - MET: ({mpt}, {mph})".format(spf=syspostfix,
                                                              bpf=branchpostfix,
                                                              fj=fillJet,
                                                              fjp=fillJet_pt,
                                                              fji=fillJet_phi,
                                                              fje=fillJet_eta,
                                                              fjm=fillJet_mass,
                                                              mpt=fillMET_pt,
                                                              mph=fillMET_phi)
              )
            

        #Get the appropriate weight defined in defineFinalWeights function
        # wgtVar = sysDict.get("wgt_final", "wgt__nom")
        wgtVar = "wgt{spf}".format(spf=syspostfix)
        print("{} chosen as the weight for {} variation (pre systematic re-mapping)".format(wgtVar, syspostfix.replace("___", "")))

        #We need to create filters that depend on scale variations like jesUp/Down, i.e. HT and Jet Pt can and will change
        #Usually weight variations will be based upon the _nom (nominal) calculations/filters,
        #Scale variations will usually have a special branch defined. Exeption is sample-based variations like ttbar hdamp, where the nominal branch is used for calculations
        #but even there, the inputs should be tailored to point to 'nominal' jet pt
        if not isWeightVariation:
            #cycle through processes here, should we have many packed together in the sample (ttJets -> lepton decay channel, heavy flavor, light flavor, etc.
            for eraAndSampleName in nodes:
                if eraAndSampleName.lower() == "basenode": continue
                if eraAndSampleName not in histoNodes:
                    histoNodes[eraAndSampleName] = dict()
                listOfColumns = nodes[eraAndSampleName]["BaseNode"].GetColumnNames()

                #Guard against wgtVar not being in place
                if wgtVar not in listOfColumns:
                    print("{} not found as a valid weight variation, no backup solution implemented".format(wgtVar))
                    raise RuntimeError("Couldn't find a valid fallback weight variation in fillHistos()")

                #potentially add other channels here, like "IsoMuNonisoEl", etc. for QCD studies, or lpf-dependency
                #NOTE: we append an extra underscore (postfixes should always have 1 to begin with) to enable use of split("__") to re-deduce postfix outside this 
                #deeply nested loop
                for decayChannel in ["ElMu{lpf}".format(lpf=leppostfix), 
                                     "MuMu{lpf}".format(lpf=leppostfix),
                                     "ElEl{lpf}".format(lpf=leppostfix),
                                     "ElEl_LowMET{lpf}".format(lpf=leppostfix),
                                     "ElEl_HighMET{lpf}".format(lpf=leppostfix),
                                     ]:
                    testInputChannel = channel.lower().replace("_baseline", "").replace("_selection", "")
                    testLoopChannel = decayChannel.lower().replace("{lpf}".format(lpf=leppostfix), "").replace("_baseline", "").replace("_selection", "")
                    if testInputChannel == "all": 
                        pass
                    elif testInputChannel != testLoopChannel: 
                        if verbose:
                            print("Skipping channel {chan} in process {proc} for systematic {spf}".format(chan=decayChannel, 
                                                                                                          proc=eraAndProcessName, 
                                                                                                          spf=syspostfix.replace("___", "")
                                                                                                      )
                            )
                        continue
                    #Regarding keys: we'll insert the systematic when we insert all th L0 X L1 X L2 keys in the dictionaries, not here in the L($N) keys
                    # print("Filtering events with ST >= 500, and removing HT cut!")
                    if decayChannel == "ElMu{lpf}".format(lpf=leppostfix):
                        channelFilter = "nFTALepton{lpf} == 2 && nFTAMuon{lpf} == 1 && nFTAElectron{lpf}== 1".format(lpf=leppostfix)
                        channelFiltName = "1 el, 1 mu ({lpf})".format(lpf=leppostfix)
                        L0String = "HT{bpf} >= {htc}".format(bpf=branchpostfix, htc=HTCut)
                        L0Name = "HT{bpf} >= {htc}"\
                            .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        L0Key = "ZWindowMET{metcut}Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), metcut=str(0).replace(".", "p"), 
                                                                                 zwidth=0)
                    elif decayChannel == "MuMu{lpf}".format(lpf=leppostfix):
                        channelFilter = "nFTALepton{lpf} == 2 && nFTAMuon{lpf} == 2".format(lpf=leppostfix)
                        channelFiltName = "2 mu ({lpf})".format(lpf=leppostfix)
                        L0String = "HT{bpf} >= {htc} && {met} >= {metcut} && FTAMuon{lpf}_InvariantMass > 20 && abs(FTAMuon{lpf}_InvariantMass - 91.2) > {zwidth}"\
                            .format(lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0], bpf=branchpostfix, htc=HTCut)
                        L0Name = "HT{bpf} >= {htc}, {met} >= {metcut}, Di-Muon Resonance > 20GeV and outside {zwidth}GeV Z Window"\
                            .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        L0Key = "ZWindowMET{metcut}Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), 
                                                                                 metcut=str(ZMassMETWindow[1]).replace(".", "p"), 
                                                                                 zwidth=str(ZMassMETWindow[0]).replace(".", "p"))
                    elif decayChannel == "ElEl{lpf}".format(lpf=leppostfix):
                        channelFilter = "nFTALepton{lpf} == 2 && nFTAElectron{lpf}== 2".format(lpf=leppostfix)
                        # print("\n\n2MediumElectron test in ElEl Channel\n\n")
                        # channelFilter = "nFTALepton{lpf} == 2 && nMediumFTAElectron{lpf}== 2".format(lpf=leppostfix)
                        channelFiltName = "2 el ({lpf})".format(lpf=leppostfix)
                        L0String = "HT{bpf} >= {htc} && {met} >= {metcut} && FTAElectron{lpf}_InvariantMass > 20 && abs(FTAElectron{lpf}_InvariantMass - 91.2) > {zwidth}"\
                            .format(lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0], bpf=branchpostfix, htc=HTCut)
                        L0Name = "HT{bpf} >= {htc}, {met} >= {metcut}, Di-Electron Resonance > 20GeV and outside {zwidth}GeV Z Window"\
                            .format(bpf=branchpostfix, htc=HTCut, lpf=leppostfix, met=fillMET_pt, metcut=ZMassMETWindow[1], zwidth=ZMassMETWindow[0])
                        L0Key = "ZWindowMET{metcut}Width{zwidth}___HT{htc}".format(spf=syspostfix, htc=str(HTCut).replace(".", "p"), 
                                                                                 metcut=str(ZMassMETWindow[1]).replace(".", "p"), 
                                                                                 zwidth=str(ZMassMETWindow[0]).replace(".", "p"))
                    else:
                        raise NotImplementedError("No definition for decayChannel = {} yet".format(decayChannel))
                    #filter define, filter name, process, channel, L0 (HT/ZWindow <cross> SCALE variations), L1 (nBTags), L2 (nJet)
                    #This is the layer -1 key, insert and proceed to layer 0
                    if decayChannel not in nodes[eraAndSampleName]: 
                        #protect against overwriting, as these nodes will be shared amongst non-weight variations!
                        #There will be only one basenode per decay channel
                        # filterNodes[eraAndSampleName][decayChannel] = collections.OrderedDict()
                        filterNodes[eraAndSampleName][decayChannel] = collections.OrderedDict()
                        filterNodes[eraAndSampleName][decayChannel]["BaseNode"] = (channelFilter, channelFiltName, eraAndSampleName, decayChannel, None, None, None) #L-1 filter
                        print(filterNodes[eraAndSampleName][decayChannel]["BaseNode"])
                        # nodes[eraAndSampleName][decayChannel] = collections.OrderedDict()
                        nodes[eraAndSampleName][decayChannel] = collections.OrderedDict()
                        nodes[eraAndSampleName][decayChannel]["BaseNode"] = nodes[eraAndSampleName]["BaseNode"].Filter(filterNodes[eraAndSampleName][decayChannel]["BaseNode"][0],
                                                                                                             filterNodes[eraAndSampleName][decayChannel]["BaseNode"][1])
                        # countNodes[eraAndSampleName][decayChannel] = collections.OrderedDict()
                        countNodes[eraAndSampleName][decayChannel] = collections.OrderedDict()
                        countNodes[eraAndSampleName][decayChannel]["BaseNode"] = nodes[eraAndSampleName][decayChannel]["BaseNode"].Count()

                        #more freeform diagnostic nodes
                        diagnosticNodes[eraAndSampleName][decayChannel] = dict()

                        #Make some key for the histonodes, lets stop at decayChannel for now for the tuples, but keep a dict with histoName as key for histos...
                        defineNodes[eraAndSampleName][decayChannel] = []
                    if decayChannel not in histoNodes[eraAndSampleName]:
                        histoNodes[eraAndSampleName][decayChannel] = collections.OrderedDict()

                    #NOTE: This structure requires no dependency of L0 and higher nodes upon eraAndSampleName, leppostfix... potential problem later if that changes
                    #The layer 0 key filter, this is where we intend to start doing histograms (plus subsequently nested nodes on layers 1 and 2
                    if "L0Nodes" not in filterNodes[eraAndSampleName][decayChannel]:
                        filterNodes[eraAndSampleName][decayChannel]["L0Nodes"] = []
                        filterNodes[eraAndSampleName][decayChannel]["L1Nodes"] = []
                        filterNodes[eraAndSampleName][decayChannel]["L2Nodes"] = [] 

        
                    #We need some indices to be able to sub-select the filter nodes we need to apply, this makes it more automated when we add different nodes
                    #These indicate the start for slicing i.e list[start:stop]
                    L0start = len(filterNodes[eraAndSampleName][decayChannel]["L0Nodes"])
                    L1start = len(filterNodes[eraAndSampleName][decayChannel]["L1Nodes"])
                    L2start = len(filterNodes[eraAndSampleName][decayChannel]["L2Nodes"])
                        
                    #L0 nodes must reference the process, decay chanel, and this L0Key, which will form the first 3 nested keys in nodes[...]
                    #We'll create one of these for each decay channel, since this filter depends directly on the channel, and since it also depends on
                    #scale variation, it necessarily depends on the process, since that process may or may not have such a scale variation to be applied
                    filterNodes[eraAndSampleName][decayChannel]["L0Nodes"].append((L0String, L0Name, eraAndSampleName, decayChannel, L0Key, None, None)) #L0 filter
                    #Tuple format: (filter code, filter name, process, channel, L0 key, L1 key, L2 key) where only one of L0, L1, L2 keys are non-None!
                    
                    #These nodes should apply to any/all L0Nodes
                    filterNodes[eraAndSampleName][decayChannel]["L1Nodes"].append(
                        ("nMedium{tag}{bpf} >= 0".format(tag=tagger, bpf=branchpostfix), "0+ nMedium{tag}({bpf})".format(tag=tagger, bpf=branchpostfix),
                         eraAndSampleName, decayChannel, None, "nMedium{tag}0+".format(tag=tagger, bpf=branchpostfix), None))
                    #These filters should apply to all L1Nodes
                    filterNodes[eraAndSampleName][decayChannel]["L2Nodes"].append(
                        ("nFTAJet{bpf} >= 4".format(bpf=branchpostfix), "4+ Jets ({bpf})".format(bpf=branchpostfix),
                         eraAndSampleName, decayChannel, None, None, "nJet4+".format(bpf=branchpostfix)))

                    #We need some indices to be able to sub-select the filter nodes we need to apply, this makes it more automated when we add different nodes
                    #These indicate the end for slicing
                    L0stop = len(filterNodes[eraAndSampleName][decayChannel]["L0Nodes"])
                    L1stop = len(filterNodes[eraAndSampleName][decayChannel]["L1Nodes"])
                    L2stop = len(filterNodes[eraAndSampleName][decayChannel]["L2Nodes"])

                    #To avoid any additional complexity, since this is too far from KISS as is, continue applying the filters right after defining them (same depth)
                    #unpack the tuple using lower case l prefix
                    for l0Tuple in filterNodes[eraAndSampleName][decayChannel]["L0Nodes"][L0start:L0stop]:
                        l0Code = l0Tuple[0]
                        l0Name = l0Tuple[1]
                        l0Proc = l0Tuple[2]
                        l0Chan = l0Tuple[3]
                        l0Key = l0Tuple[4]
                        l0l1Key = l0Tuple[5]
                        l0l2Key = l0Tuple[6]
                        assert l0Proc == eraAndSampleName, "eraAndSampleName mismatch, was it formatted correctly?\n{}".format(l0Tuple)
                        assert l0Chan == decayChannel, "decayChannel mismatch, was it formatted correctly?\n{}".format(l0Tuple)
                        assert l0l1Key == None, "non-None key in tuple for L1, was it added in the correct place?\n{}".format(l0Tuple)
                        assert l0l2Key == None, "non-None key in tuple for L2, was it added in the correct place?\n{}".format(l0Tuple)

                        #Here we begin the complication of flattening the key-value structure. We do not nest any deeper, but instead
                        #form keys as combinations of l0Key, l1Key, l2Key... 
                        #Here, form the cross key, and note the reference key it must use
                        crossl0Key = "{l0}{spf}".format(l0=l0Key, spf=syspostfix)
                        referencel0Key = "BaseNode" #L0 Filters are applied to 'BaseNode' of the nodes[proc][chan] dictionary of dataframes
                        if crossl0Key in nodes[eraAndSampleName][decayChannel]:
                            raise RuntimeError("Tried to redefine rdf node due to use of the same key: {}".format(crossl0Key))
                        nodes[eraAndSampleName][decayChannel][crossl0Key] = nodes[eraAndSampleName][decayChannel][referencel0Key].Filter(l0Code, l0Name)
                        countNodes[eraAndSampleName][decayChannel][crossl0Key] = nodes[eraAndSampleName][decayChannel][crossl0Key].Count()


        #Regarding naming conventions:
        #Since category can use __ as a separator between branchpostfix and the rest, extend to ___ to separate further... ugly, but lets
        #try sticking with valid C++ variable names (alphanumeric + _). Also note that {spf} will result in 3 underscores as is currently defined
        #CYCLE THROUGH CATEGORIES in the nodes that exist now, nodes[eraAndSampleName][decayChannel][CATEGORIES]
        #We are inside the systematics variation, so we cycle through everything else (nominal nodes having been created first!)
        if skipNominalHistos and sysVar.lower() in ["nom", "nominal", "$nominal"]:
            print("Skipping histograms and diagnostics for the nominal due to skipNominalHistos=True flag")
            continue
        for eraAndSampleName in nodes:
            if eraAndSampleName.lower() == "basenode": continue
            eraAndProcessName = eraAndSampleName.replace("-HDAMPdown", "").replace("-HDAMPup", "").replace("-TuneCP5down", "").replace("-TuneCP5up", "")
            histopostfix = None
            if systematicRemapping is None:
                histopostfix = syspostfix
            else:
                for systRemap, remapSamples in systematicRemapping.items():
                    if eraAndSampleName.split("___")[-1] in remapSamples:
                        histopostfix = "___{}".format(systRemap)
            if histopostfix is None:
                raise RuntimeError("Systematic {syst}'s remapping dictionary does not contain process {proc}.".format(syst=sysVar, proc=eraAndProcessName))

            for decayChannel in nodes[eraAndSampleName]:
                if decayChannel.lower() == "basenode": continue
                for category, categoryNode in nodes[eraAndSampleName][decayChannel].items():
                    if category.lower() == "basenode": continue
                    #IMPORTANT: Skip nodes that belong to other systematic variations, since it's a dictionary!
                    if category.split("___")[-1] != branchpostfix.replace("__", ""): 
                        continue 

                    diagnosticNodes[eraAndSampleName][decayChannel][category] = dict()
                    # if doDiagnostics:
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["nLooseMuon"] = categoryNode.Stats("nLooseFTAMuon{lpf}".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Muon_pfIsoId"] = categoryNode.Stats("FTAMuon{lpf}_pfIsoId".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Muon_pt"] = categoryNode.Stats("FTAMuon{lpf}_pt".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Muon_eta"] = categoryNode.Stats("FTAMuon{lpf}_eta".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Muon_charge"] = categoryNode.Stats("FTAMuon{lpf}_charge".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Muon_dz"] = categoryNode.Stats("FTAMuon{lpf}_dz".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Muon_dxy"] = categoryNode.Stats("FTAMuon{lpf}_dxy".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Muon_d0"] = categoryNode.Stats("FTAMuon{lpf}_d0".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Muon_ip3d"] = categoryNode.Stats("FTAMuon{lpf}_ip3d".format(lpf=leppostfix))
    
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["nLooseElectron"] = categoryNode.Stats("nLooseFTAElectron{lpf}".format(lpf=leppostfix))
                    #     # diagnosticNodes[eraAndSampleName][decayChannel][category]["Electron_pfIsoId"] = categoryNode.Stats("FTAElectron{lpf}_pfIsoId".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Electron_pt"] = categoryNode.Stats("FTAElectron{lpf}_pt".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Electron_eta"] = categoryNode.Stats("FTAElectron{lpf}_eta".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Electron_charge"] = categoryNode.Stats("FTAElectron{lpf}_charge".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Electron_dz"] = categoryNode.Stats("FTAElectron{lpf}_dz".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Electron_dxy"] = categoryNode.Stats("FTAElectron{lpf}_dxy".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Electron_d0"] = categoryNode.Stats("FTAElectron{lpf}_d0".format(lpf=leppostfix))
                    #     diagnosticNodes[eraAndSampleName][decayChannel][category]["Electron_ip3d"] = categoryNode.Stats("FTAElectron{lpf}_ip3d".format(lpf=leppostfix))
                        
                    crossSeparated = "___".join(category.split("___")[:-1]).split("_CROSS_")#Strip the systematic name from the branch by taking all but the last element
                    #Hack for nDim to put the tagger and nJet into the category name... might be best to handle a different weay
                    categoryName = "_".join(crossSeparated + ["nMedium{tag}".format(tag=tagger), "nJet"]) #No extra references to (lep/branch/sys)postfixes...
                    HTArray=[400 + 16*x for x in range(101)]
                    nJetArray=[4,5,6,7,8,20]
                    nBTagArray=[0,1,2,3,4,10]
                    HTArr = array.array('d', HTArray)
                    nJetArr = array.array('d', nJetArray)
                    nBTagArr = array.array('d', nBTagArray)
                    HT_Model= ROOT.RDF.TH3DModel("{proc}___{chan}___{cat}___HT{hpf}".format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                                                 "[{hpf}]; HT; nJet; nBTag".format(hpf=histopostfix.replace("___", "")),
                                                 len(HTArr)-1, HTArr, len(nJetArr)-1, nJetArr, len(nBTagArr)-1, nBTagArr)
                    HTUnweighted_Model= ROOT.RDF.TH3DModel("{proc}___{chan}___{cat}___HTUnweighted{hpf}".format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                                                           "[{hpf}]; HT; nJet; nBTag".format(hpf=histopostfix.replace("___", "")),
                                                           len(HTArr)-1, HTArr, len(nJetArr)-1, nJetArr, len(nBTagArr)-1, nBTagArr)

                    #Append histogram tuples for HistoND() methods to the list, the list should overall contain each set grouped by systematic variation
                    Hstart = len(defineNodes[eraAndSampleName][decayChannel])
                    defineNodes[eraAndSampleName][decayChannel].append((HT_Model, "HT{bpf}".format(bpf=branchpostfix), "nFTAJet{bpf}".format(bpf=branchpostfix), "nMedium{tag}{bpf}".format(tag=tagger, bpf=branchpostfix), wgtVar, "Histo3D"))
                    if not isWeightVariation:
                        defineNodes[eraAndSampleName][decayChannel].append((HTUnweighted_Model, "HT{bpf}".format(bpf=branchpostfix), "nFTAJet{bpf}".format(bpf=branchpostfix), "nMedium{tag}{bpf}".format(tag=tagger, bpf=branchpostfix), "Histo3D"))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_diffptraw{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "(Jet - Raw) p_{{T}} (CCJet)({hpf});(Raw - Jet) p_{{T}}(CC LeadLep); Events".format(hpf=histopostfix.replace("__", "")), 
                    #                                                 100,-300,300), "FTACrossCleanedJet{bpf}_diffptraw".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_diffptrawinverted{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "(Raw - Jet) p_{{T}} (non-CCJets)({hpf});(Raw - Jet) p_{{T}}(CC LeadLep); Events".format(hpf=histopostfix.replace("__", "")), 
                    #                                                 100,-300,300), "FTACrossCleanedJet{bpf}_diffptrawinverted".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_diffpt{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "(Jet - LeadLep) p_{{T}} (CCJet)({hpf});(Jet - LeadLep) p_{{T}}(CC LeadLep); Events".format(hpf=histopostfix.replace("__", "")), 
                    #                                                 100,-300,300), "FTACrossCleanedJet{bpf}_diffpt".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_pt{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "Jet p_{{T}} (CCJet)({hpf});Jet p_{{T}}(CC LeadLep); Events".format(hpf=histopostfix.replace("__", "")), 
                    #                                                 100,0,300), "FTACrossCleanedJet{bpf}_pt".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_rawpt{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "Jet Raw p_{{T}} (CCJet)({hpf});Jet Raw p_{{T}}(CC LeadLep); Events".format(hpf=histopostfix.replace("__", "")), 
                    #                                                 100,0,300), "FTACrossCleanedJet{bpf}_rawpt".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___FTACrossCleanedJet_leppt{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "Lead Lep p_{{T}} (CCJet)({hpf});Lead Lep p_{{T}}(CC Jet); Events".format(hpf=histopostfix.replace("__", "")), 
                    #                                                 100,0,300), "FTACrossCleanedJet{bpf}_leppt".format(bpf=branchpostfix), wgtVar))
                    # for x in range(nJetsToHisto):
                    #     thisFillJet = fillJetEnumerated.format(n=x+1)
                    #     defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Jet{n}_pt{hpf}"\
                    #                                                     .format(proc=eraAndProcessName, n=x+1, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                     "Jet_{n} p_{{T}} ({hpf}); p_{{T}}; Events"\
                    #                                                     .format(n=x+1, hpf=histopostfix.replace("__", "")), 100, 0, 500),
                    #                                                    "{tfj}_pt".format(tfj=thisFillJet, n=x+1), wgtVar))
                    #     defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Jet{n}_eta{hpf}"\
                    #                                                     .format(proc=eraAndProcessName, n=x+1, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                     "Jet_{n} #eta ({hpf}); #eta; Events"\
                    #                                                     .format(n=x+1, hpf=histopostfix.replace("__", "")), 100, -2.6, 2.6),
                    #                                                    "{tfj}_eta".format(tfj=thisFillJet, n=x+1), wgtVar))
                    #     defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Jet{n}_phi{hpf}"\
                    #                                                     .format(proc=eraAndProcessName, n=x+1, chan=decayChannel, cat=categoryName,  hpf=histopostfix),
                    #                                                     "Jet_{n} #phi ({hpf}); #phi; Events".format(n=x+1, hpf=histopostfix.replace("__", "")), 100, -pi, pi),
                    #                                                    "{tfj}_phi".format(tfj=thisFillJet, n=x+1), wgtVar))
                    #     if bTagger.lower() == "deepcsv":
                    #         defineNodes[eraAndSampleName][decayChannel].append( (("{proc}___{chan}___{cat}___Jet{n}_DeepCSVB{hpf}"\
                    #                                                          .format(proc=eraAndProcessName, n=x+1, chan=decayChannel, cat=categoryName,  hpf=histopostfix),
                    #                                                          "Jet_{n} (p_{{T}} sorted) DeepCSV B Discriminant ({hpf}); Discriminant; Events"\
                    #                                                          .format(n=x+1, hpf=histopostfix.replace("__", "")), 100, 0.0, 1.0),
                    #                                                         "{tfj}_DeepCSVB".format(tfj=thisFillJet, n=x+1), wgtVar))
                    #         defineNodes[eraAndSampleName][decayChannel].append( (("{proc}___{chan}___{cat}___Jet{n}_DeepCSVB_sorted{hpf}"\
                    #                                                          .format(proc=eraAndProcessName, n=x+1, chan=decayChannel, cat=categoryName,  hpf=histopostfix),
                    #                                                          "Jet_{n} (DeepCSVB sorted) DeepCSV B Discriminant ({hpf}); Discriminant; Events"\
                    #                                                          .format(n=x+1, hpf=histopostfix.replace("__", "")), 100, 0.0, 1.0),
                    #                                                         "{tfj}_DeepCSVB_sorted".format(tfj=thisFillJet, n=x+1), wgtVar))
                    #     if bTagger.lower() == "deepjet":
                    #         defineNodes[eraAndSampleName][decayChannel].append( (("{proc}___{chan}___{cat}___Jet{n}_DeepJetB{hpf}"\
                    #                                                          .format(proc=eraAndProcessName, n=x+1, chan=decayChannel, cat=categoryName,  hpf=histopostfix),
                    #                                                          "Jet_{n} (p_{{T}} sorted) DeepJet B Discriminant ({hpf}); Discriminant; Events"\
                    #                                                          .format(n=x+1, hpf=histopostfix.replace("__", "")), 100, 0.0, 1.0),
                    #                                                         "{tfj}_DeepJetB".format(tfj=thisFillJet, n=x+1), wgtVar))

                    #         defineNodes[eraAndSampleName][decayChannel].append( (("{proc}___{chan}___{cat}___Jet{n}_DeepJetB_sortedjet{hpf}"\
                    #                                                          .format(proc=eraAndProcessName, n=x+1, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                          "Jet_{n} (DeepJetB sorted) DeepJet B Discriminant ({hpf}); Discriminant; Events"\
                    #                                                          .format(n=x+1, hpf=histopostfix.replace("__", "")), 100, 0.0, 1.0),
                    #                                                         "{tfj}_DeepJetB_sorted".format(tfj=thisFillJet, n=x+1), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___MET_pt{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "MET ({hpf}); Magnitude (GeV); Events".format(hpf=histopostfix.replace("__", "")), 
                    #                                                 100,0,1000), fillMET_pt, wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___MET_phi{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix),
                    #                                                 "MET #phi({hpf}); #phi; Events".format(hpf=histopostfix.replace("__", "")), 
                    #                                                 100,-pi,pi), fillMET_phi, wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___MET_uncorr_pt{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "Uncorrected MET", 100,0,1000), fillMET_uncorr_pt, wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___MET_uncorr_phi{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,-pi,pi), fillMET_uncorr_phi, wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_all{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_all".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_pt_LeadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, 10, 510), "FTAMuon{lpf}_pt_LeadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_pt_SubleadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, 10, 510), "FTAMuon{lpf}_pt_SubleadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_eta_LeadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, -2.5, 2.5), "FTAMuon{lpf}_eta_LeadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_eta_SubleadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, -2.5, 2.5), "FTAMuon{lpf}_eta_SubleadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_phi_LeadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, -pi, pi), "FTAMuon{lpf}_phi_LeadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_phi_SubleadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, -pi, pi), "FTAMuon{lpf}_phi_SubleadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_chg{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso03_chg".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso04_all{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix),
                    #                                                 "", 100, 0, 0.2), "FTAMuon{lpf}_pfRelIso04_all".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_pt_LeadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, 10, 510), "FTAElectron{lpf}_pt_LeadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_pt_SubleadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, 10, 510), "FTAElectron{lpf}_pt_SubleadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_eta_LeadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, -2.5, 2.5), "FTAElectron{lpf}_eta_LeadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_eta_SubleadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, -2.5, 2.5), "FTAElectron{lpf}_eta_SubleadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_phi_LeadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, -pi, pi), "FTAElectron{lpf}_phi_LeadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_phi_SubleadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix, lpf=leppostfix), 
                    #                                                 "", 100, -pi, pi), "FTAElectron{lpf}_phi_SubleadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_all{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_all".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_chg{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100, 0, 0.2), "FTAElectron{lpf}_pfRelIso03_chg".format(lpf=leppostfix), wgtVar))
                    # # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___npvsGood_vs_HT{hpf}"\
                    # #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    # #                                                 ";npvsGood;HT", 100, 400, 2000, 20, 0, 100), "PV_npvsGood", "HT{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___ST{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,400,2000), "ST{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___HT{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,400,2000), "HT{bpf}".format(bpf=branchpostfix), wgtVar))
                    # if not isWeightVariation:
                    #     defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___HTUnweighted{hpf}"\
                    #                                                     .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                     "", 100,400,2000), "HT{bpf}".format(bpf=branchpostfix)))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___H{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,400,2000), "H{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___HT2M{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,0,1000), "HT2M{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___H2M{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,0,1500), "H2M{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___HTb{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,0,1000), "HTb{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___HTH{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,0,1), "HTH{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___HTRat{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,0,1), "HTRat{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___dRbb{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,0,2*pi), "dRbb{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___dPhibb{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,-pi,pi), "dPhibb{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___dEtabb{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100,0,5), "dEtabb{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Lepton{lpf}_pt_LeadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 100,0,500), "FTALepton{lpf}_pt_LeadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Lepton{lpf}_pt_SubleadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 100,0,500), "FTALepton{lpf}_pt_SubleadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Lepton{lpf}_eta_LeadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 100,-2.6,2.6), "FTALepton{lpf}_eta_LeadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Lepton{lpf}_eta_SubleadLep{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 100,-2.6,2.6), "FTALepton{lpf}_eta_SubleadLep".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon{lpf}_pt{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 100,0,500), "FTAMuon{lpf}_pt".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron{lpf}_pt{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 100,0,500), "FTAElectron{lpf}_pt".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___dRll{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 100,0,2*pi), 
                    #                                                "FTALepton{lpf}_dRll".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___dPhill{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 100,-pi,pi), 
                    #                                                "FTALepton{lpf}_dPhill".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___dEtall{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 100,0,5), 
                    #                                                "FTALepton{lpf}_dEtall".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___MTofMETandEl{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 100, 0, 200), 
                    #                                                "MTofMETandEl{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___MTofMETandMu{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 100, 0, 200), 
                    #                                                "MTofMETandMu{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___MTofElandMu{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 100, 0, 200), 
                    #                                                "MTofElandMu{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nJet{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 14, 0, 14), 
                    #                                                "n{fj}".format(fj=fillJet), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_LooseDeepCSV{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 6, 0, 6), 
                    #                                                "nLooseDeepCSVB{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_MediumDeepCSV{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 6, 0, 6), 
                    #                                                "nMediumDeepCSVB{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_TightDeepCSV{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 6, 0, 6), 
                    #                                                "nTightDeepCSVB{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_LooseDeepJet{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 6, 0, 6), 
                    #                                                "nLooseDeepJetB{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_MediumDeepJet{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 6, 0, 6), 
                    #                                                "nMediumDeepJetB{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_TightDeepJet{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), "", 6, 0, 6), 
                    #                                                "nTightDeepJetB{bpf}".format(bpf=branchpostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nLooseFTAMuon{lpf}{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 4, 0, 4), "nLooseFTAMuon{lpf}".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nMediumFTAMuon{lpf}{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 4, 0, 4), "nMediumFTAMuon{lpf}".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nTightFTAMuon{lpf}{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 4, 0, 4), "nTightFTAMuon{lpf}".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nLooseFTAElectron{lpf}{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 4, 0, 4), "nLooseFTAElectron{lpf}".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nMediumFTAElectron{lpf}{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 4, 0, 4), "nMediumFTAElectron{lpf}".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nTightFTAElectron{lpf}{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 4, 0, 4), "nTightFTAElectron{lpf}".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nLooseFTALepton{lpf}{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 4, 0, 4), "nLooseFTALepton{lpf}".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nMediumFTALepton{lpf}{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 4, 0, 4), "nMediumFTALepton{lpf}".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nTightFTALepton{lpf}{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  lpf=leppostfix, hpf=histopostfix), 
                    #                                                 "", 4, 0, 4), "nTightFTALepton{lpf}".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_InvMass{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100, 0, 150), "FTAMuon{lpf}_InvariantMass".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_InvMass{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 100, 0, 150), "FTAElectron{lpf}_InvariantMass".format(lpf=leppostfix), wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_InvMass_v_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 30, 0, 150, 20, 0, 400), "FTAMuon{lpf}_InvariantMass".format(lpf=leppostfix), fillMET_pt, wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_InvMass_v_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 "", 30, 0, 150, 20, 0, 400), "FTAElectron{lpf}_InvariantMass".format(lpf=leppostfix), fillMET_pt, wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_all_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso03_all;MET", 30, 0., 0.2, 20,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_chg_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso04_all_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso04_all;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_all_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso03_all;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_chg_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_chg", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_all_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso03_all;MET", 30, 0., 0.2, 20,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_chg_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso03_chg;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso04_all_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso04_all;MET", 30, 0, 0.2, 20,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_all_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso03_all;MET", 30, 0, 0.2, 20,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # Older versions
                    # defineNodes[eraAndSampleName][decayChannel].append(("{proc}___{chan}___{cat}___Muon_pfRelIso03_all_vs_MET{hpf}"\
                    #                                                .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                ";pfRelIso03_all;MET", 100, 0., 0.2, 100,30.,1030.), "FTAMuon{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso03_chg_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso03_chg;MET", 100, 0, 0.2, 100,30,1030), "FTAMuon{lpf}_pfRelIso03_chg", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Muon_pfRelIso04_all_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso04_all;MET", 100, 0, 0.2, 100,30,1030), "FTAMuon{lpf}_pfRelIso04_all", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_all_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso03_all;MET", 100, 0, 0.2, 100,30,1030), "FTAElectron{lpf}_pfRelIso03_all", "fillMET_pt", wgtVar))
                    # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___Electron_pfRelIso03_chg_vs_MET{hpf}"\
                    #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                    #                                                 ";pfRelIso03_chg;MET", 100, 0, 0.2, 100,30,1030), "FTAElectron{lpf}_pfRelIso03_chg", "fillMET_pt", wgtVar))
                    if isData == False:                                                                           
                        # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_genMatched_puIdLoose{hpf}"\
                        #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                        #                                                 "", 14, 0, 14), "n{fj}_genMatched_puIdLoose".format(fj=fillJet), wgtVar))
                        # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___nJet_genMatched{hpf}"\
                        #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                        #                                                 "", 14, 0, 14), "n{fj}_genMatched".format(fj=fillJet), wgtVar))
                        # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___test1{hpf}"
                        #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                        #                                                 ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAMuon{lpf}_pfRelIso03_all", "PV_npvsGood", wgtVar))
                        # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___test2{hpf}"
                        #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                        #                                                 ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAMuon{lpf}_pfRelIso03_all", "METFixEE2017_pt", wgtVar))
                        # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___npvsGood_vs_nTrueInttest{hpf}"
                        #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                        #                                                ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "FTAElectron{lpf}_pfRelIso03_all", "MET_pt_flat", wgtVar))
                        # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___npvsGood_vs_nTrueInt{hpf}"\
                        #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                        #                                                 ";nTrueInt;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvsGood", wgtVar))
                        # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___npvsGood_vs_nPU{hpf}"\
                        #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                        #                                                 ";nPU;npvsGood", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvsGood", wgtVar))
                        # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___npvs_vs_nTrueInt{hpf}"\
                        #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                        #                                                 ";nTrueInt;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nTrueInt", "PV_npvs", wgtVar))
                        # defineNodes[eraAndSampleName][decayChannel].append((("{proc}___{chan}___{cat}___npvs_vs_nPU{hpf}"\
                        #                                                 .format(proc=eraAndProcessName, chan=decayChannel, cat=categoryName,  hpf=histopostfix), 
                        #                                                 ";nPU;npvs", 150, 0, 150, 150, 0, 150), "Pileup_nPU", "PV_npvs", wgtVar))
                        pass


                    #End of definitions for this process + channel + category, now define the histoNodes based upon this categoryNode (nodes[proc][chan][category + branchpostfix]
                    Hstop = len(defineNodes[eraAndSampleName][decayChannel])
                    #Guard against histogram names already included (via keys in histNodes) as well as variables that aren't present in branches
                    # print("==============================> {} {} start: {} stop: {}".format(eraAndSampleName, decayChannel, Hstart, Hstop)) 
                    ## catTest = categoryName.lower()
                    ## if "njet" not in catTest and ("nmedium" not in catTest or "ntight" not in catTest and "nloose" not in catTest):
                    ##     continue
                    ##     if verbose:
                    ##         print("Skipping category nodes without btag and njet categorization")
                    for dnode in defineNodes[eraAndSampleName][decayChannel][Hstart:Hstop]:
                        defHName = dnode[0].fName
                        #Need to determine which kind of histo function to use... have to be careful, this guess will be wrong if anyone ever does an unweighted histo!
                        if defHName in histoNodes[eraAndSampleName][decayChannel]:
                            raise RuntimeError("This histogram name already exists in memory or is intentionally being overwritten:"\
                                               "eraAndSampleName - {}\t decayChannel - {}\t defHName - {}".format(eraAndSampleName, decayChannel, defHName))
                        else:
                            for i in range(1, len(dnode)-1):
                                if dnode[i] not in listOfColumns and dnode[i] != "1":
                                    raise RuntimeError("This histogram's variable/weight is not defined:"\
                                                       "eraAndSampleName - {}\t decayChannel - {}\t variable/weight - {}".format(eraAndSampleName, decayChannel, dnode[i]))
                            if dnode[-1] == "Histo1D":
                                # if doCombineHistosOnly and dnode[1] not in combineHistoVariables: 
                                #     # print("Skipping histogram filling with {}".format(dnode[1]))
                                #     continue
                                if len(dnode) == 3:
                                    histoNodes[eraAndSampleName][decayChannel][defHName] = categoryNode.Histo1D(dnode[0], dnode[1])
                                elif len(dnode) == 4:
                                    histoNodes[eraAndSampleName][decayChannel][defHName] = categoryNode.Histo1D(dnode[0], dnode[1], dnode[2])
                                else:
                                    raise RuntimeError("Unhandled case in Histogram node calls", dnode)
                            elif dnode[-1] == "Histo2D":
                                if len(dnode) == 4:
                                    histoNodes[eraAndSampleName][decayChannel][defHName] = categoryNode.Histo2D(dnode[0], dnode[1], dnode[2])
                                elif len(dnode) == 5:
                                    histoNodes[eraAndSampleName][decayChannel][defHName] = categoryNode.Histo2D(dnode[0], dnode[1], dnode[2], dnode[3])
                                else:
                                    raise RuntimeError("Unhandled case in Histogram node calls", dnode)
                            elif dnode[-1] == "Histo3D":
                                if len(dnode) == 5:
                                    histoNodes[eraAndSampleName][decayChannel][defHName] = categoryNode.Histo3D(dnode[0], dnode[1], dnode[2], dnode[3])
                                elif len(dnode) == 6:
                                    histoNodes[eraAndSampleName][decayChannel][defHName] = categoryNode.Histo3D(dnode[0], dnode[1], dnode[2], dnode[3], dnode[4])
                                else:
                                    raise RuntimeError("Unhandled case in Histogram node calls", dnode)
                            else:
                                raise RuntimeError("Unhandled node type in defineNodes: ", dnode)

    packedNodes = {}
    packedNodes["filterNodes"] = filterNodes
    packedNodes["defineNodes"] = defineNodes
    packedNodes["countNodes"] = countNodes
    packedNodes["diagnosticNodes"] = diagnosticNodes
    packedNodes["nodes"] = nodes
    return packedNodes
