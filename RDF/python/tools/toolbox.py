import copy
import glob #For getFiles
import os, pwd, sys #For getFiles
import tempfile #For getFiles
import ruamel.yaml as yaml #for load and write yaml files
import ROOT
import ctypes

def get_number_of_labels(hist):
    xLow = hist.GetXaxis().GetBinLowEdge(1)
    xHigh = hist.GetXaxis().GetBinLowEdge(hist.GetXaxis().GetNbins()+1)
    xDivisions = hist.GetXaxis().GetNdivisions() % 100

    if xDivisions < 0:
        return -xDivisions + 1

    # Setup ctypes to be optimized by THLimitsFinder::Optimize
    xLowOptimized = ctypes.c_double(0.)
    xHighOptimized = ctypes.c_double(0.)
    xDivisionsOptimized = ctypes.c_int(0)
    xBinWidthOptimized = ctypes.c_double(0.)

    # Run the optimization
    # Optimize (Double_t A1, Double_t A2, Int_t nold, Double_t &BinLow, Double_t &BinHigh, Int_t &nbins, Double_t &BWID, Option_t *option="")
    ROOT.THLimitsFinder.Optimize(xLow, xHigh, xDivisions, xLowOptimized, xHighOptimized, xDivisionsOptimized, xBinWidthOptimized, "")
    return int(xDivisionsOptimized.value % 100) + 1

def getFiles(query, redir="", outFileName=None, globSort=lambda f: int(f.split('_')[-1].replace('.root', '')), doEOSHOME=False, doGLOBAL=False, verbose=False):
    """Use one of several different methods to acquire a list or text file specifying the filenames.

Method is defined by a string passed to the query argument (required, first), with the type of query prepended to a string path.
'dbs:' - Used to signify getFiles should do a DAS query using the following string path
'glob:' - Used to signify getFiles should do a glob of the following string path, which should include a reference to the filetype, i.e. "glob:~/my2017ttbarDir/*/results/myTrees_*.root"
    optional - globSort is a lambda expression to sort the globbed filenames, with a default of lambda f: int(f.split('_')[-1].replace('.root', ''))
'list:' - Used to signify getFiles should open the file in the following path and return a List. 

outFileName can be specified for any option to also write a file with the list (as prepended with any redir string, specified with redir="root://cms-xrd-global.cern.ch" or "root://eoshome-<FIRST_INITIAL>.cern.ch/"
redir will prepend the redirector to the beginning of the paths, such as redir="root://cms-xrd-global.cern.ch/"
doEOSHOME will override the redir string with the one formatted based on your username for the eoshome-<FIRST_INITIAL>, which is your typical workspace on EOS (/eos/user/<FIRST_INITIAL>/<USERNAME>/)
    For example, this xrdcp will work with valid grid proxy or KRB5: "xrdcp root://eoshome-n.cern.ch//eos/user/n/nmangane/PATH/TO/ROOT/FILE.root ."
"""
    #methods to support: "dbs" using dasgoclient query, "glob" using directory path, "file" using text file
    fileList = []
    if doEOSHOME:
        #Set eoshome-<FIRST_INITIAL> as redirector, by getting the username and then the first initial from the username
        redir = "root://eoshome-{0:s}.cern.ch/".format((pwd.getpwuid(os.getuid())[0])[0])
    elif doGLOBAL:
        #Standard redirector
        redir = "root://cms-xrd-global.cern.ch/"
    elif redir != "":
        #accept redirector as-is
        pass
    else:
        redir = ""
    if "dbs:" in query:
        with tempfile.NamedTemporaryFile() as f:
            cmd = 'dasgoclient --query="file dataset={0:s}" > {1:s}'.format(query.replace("dbs:",""),f.name)
            if verbose:
                print("dbs query reformatted to:\n\t" + query)
            os.system(cmd)
            for line in f:
                fileList.append(line.decode("utf-8").rstrip("\s\n\t"))
    elif "glob:" in query:
        query_stripped = query.replace("glob:","")
        fileList = glob.glob(query_stripped)
    elif "list:" in query:
        query_stripped = query.replace("list:","")
        fileList = []
        with open(query_stripped, "r") as in_f:
            for line in in_f:
                fileList.append(line.rstrip("\s\n\t"))
    else:
        print("No query passed to getFiles(), exiting")
        sys.exit(9001)
    if redir != "":
        if verbose: print("prepending redir")
        #Protect against double redirectors, assuming root:// is in the beginning
        if len(fileList) > 0 and "root://" not in fileList[0]:
            if verbose: print("Not prepending redirector, as one is already in place")
            fileList[:] = [redir + file for file in fileList]

    #Write desired output file with the list
    if outFileName:
        if verbose: print("Writing output file {0:s}".format(outFileName))
        with open(outFileName, 'w') as out_f:
            for line in fileList:
                out_f.write(line + "\n")
    #Return the list
    return fileList

def load_yaml_cards(sample_cards):
    SampleList = None
    SampleDict = dict()
    try:
        import ruamel.yaml
        ruamel.yaml.preserve_quotes = True
    except:
        print("Cannot load ruamel package to convert yaml file. Consider installing in a virtual environment with 'pip install --user 'ruamel.yaml<0.16,>0.15.95' --no-deps'")

    for scard in sample_cards:
        with open(scard, "r") as sample:
            if SampleList is None:
                SampleList = ruamel.yaml.load(sample, Loader=ruamel.yaml.RoundTripLoader)
            else:
                SampleList.update(ruamel.yaml.load(sample, Loader=ruamel.yaml.RoundTripLoader))

    for scard in sample_cards:
        with open(scard, "r") as sample:
            SampleDict[scard] = ruamel.yaml.load(sample, Loader=ruamel.yaml.RoundTripLoader)
    return SampleList, SampleDict

def write_yaml_cards(sample_cards, postfix="_updated"):
    try:
        import ruamel.yaml
        ruamel.yaml.preserve_quotes = True
    except:
        print("Cannot load ruamel package to convert yaml file. Consider installing in a virtual environment with 'pip install --user 'ruamel.yaml<0.16,>0.15.95' --no-deps'")

    for scard, scontent in sample_cards.items():
        with open(scard.replace(".yaml", postfix+".yaml").replace(".yml", postfix+".yml"), "w") as outf:
            ruamel.yaml.dump(scontent, outf, Dumper=ruamel.yaml.RoundTripDumper)

def filter_systematics(yaml_dict, era, sampleName, isSystematicSample, nominal=False, scale=False, weight=False, baseColumns=None):
                       #resolveEnsembles=False, resolveRemappings=False):
    #In general, nominal is both nominal and a scale variation, is not a weight variation, is not dedicated systematic
    #resolveEnsembles means a group of systematics for which the many are summed in quadrature, or some other process is done, to produce a single systematic.
    #How to handle up/down in an ensemble remains to be seen
    if nominal is False and scale is False and weight is False:
        if not isSystematicSample:
            raise RuntimeError("All systematics are either scale or weight, with nominal being a subset of scale. The only other option is a systematic for a dedicated systematic sample. Change request in filter_systematics")
    pass_filter = []
    for sysVar, sysDict in yaml_dict.items():
        ### Logic for handling scale, weight, nominal systematics
        isNominal = sysDict.get("isNominal", False)
        isWeight = sysDict.get("weightVariation", True)
        isScale = not isWeight
        isSampleSpecificSystematic = True if sysDict.get("isSystematicForSample", False) else False
        #logic for handling systematics requiring presence of particular columns, e.g. LHEScaleWeight, in the BASE node before defines.
        require = True
        requiredBranches = sysDict.get("requires", [])
        if baseColumns is not None:
            for branch in requiredBranches:
                if branch not in baseColumns:
                    require = False
            if not require:
                print("filter_systematics has removed systematic variation '{}' due to missing branches in the base node for sample '{}'".format(sysVar, sampleName))
                continue
        # print("{} is counted as sampleSpecificSystematic: {}".format(sysVar, isSampleSpecificSystematic))
        #Filter out systematics if they aren't matched by dedicated systematic status:
        if isSampleSpecificSystematic:
            if isSystematicSample and sampleName in sysDict.get("isSystematicForSample", []):
                #Potential match
                pass
            else:
                #Skip dedicated systematic if the sampleName isn't in the systematics' list of applicable ones
                # print("Skipping dedicated systematic {} for non-matching era sample {} {}".format(sysVar, era, sampleName))
                continue
        else:
            if isSystematicSample:
                #skip non-dedicated systematics if the sample is a nominal type
                # print("Skipping non-dedicated systematic {} for systematic era sample {} {}".format(sysVar, era, sampleName))
                continue
            else:
                #Potential match
                pass
        #Now choose which ones to append...
        if nominal and isNominal:
            pass_filter.append(sysVar)
            continue
        if scale and isScale:
            pass_filter.append(sysVar)
            continue
        if weight and isWeight:
            pass_filter.append(sysVar)
            continue
    return pass_filter

def configure_template_systematics(yaml_dict, era, channel, include_nominal=True):
    assert isinstance(era, str)
    assert isinstance(channel, str)
    systs = []
    for sysVarRaw, sysDictRaw in yaml_dict.items():
        lep_postfix = sysDictRaw.get("lep_postfix", "")
        # if sysDictRaw.get("ensembleMapping", None) is not None:
        sampleRemappings = sysDictRaw.get("sampleRemapping", None)
        if sampleRemappings is not None:
            for name, samples in sampleRemappings.items():
                systs.append(name.replace("$ERA", era).replace("$CHANNEL", channel).replace("$LEP_POSTFIX", lep_postfix).replace("$NOMINAL", "nom"))
        else:
            if not include_nominal and sysVarRaw.replace("$ERA", era).replace("$CHANNEL", channel).replace("$LEP_POSTFIX", lep_postfix) in ["$NOMINAL", "nom"]:
                continue
            systs.append(sysVarRaw.replace("$ERA", era).replace("$CHANNEL", channel).replace("$LEP_POSTFIX", lep_postfix).replace("$NOMINAL", "nom"))
    return systs

def configure_template_systematics_dict(yaml_dict, era, channel, include_nominal=True):
    assert isinstance(era, str)
    assert isinstance(channel, str)
    systs = dict()
    for sysVarRaw, sysDictRaw in yaml_dict.items():
        lep_postfix = sysDictRaw.get("lep_postfix", "")
        # if sysDictRaw.get("ensembleMapping", None) is not None:
        sampleRemappings = sysDictRaw.get("sampleRemapping", None)
        if sampleRemappings is not None:
            for name, samples in sampleRemappings.items():
                systs[name.replace("$ERA", era).replace("$CHANNEL", channel).replace("$LEP_POSTFIX", lep_postfix).replace("$NOMINAL", "nom")] = sysDictRaw
        else:
            if not include_nominal and sysVarRaw.replace("$ERA", era).replace("$CHANNEL", channel).replace("$LEP_POSTFIX", lep_postfix) in ["$NOMINAL", "nom"]:
                continue
            systs[sysVarRaw.replace("$ERA", era).replace("$CHANNEL", channel).replace("$LEP_POSTFIX", lep_postfix).replace("$NOMINAL", "nom")] = sysDictRaw
    for sysVar, sysDict in systs.items():
        for k, v in sysDict.items():
            if isinstance(v, str):
                if "$" in v:
                    v = v.replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', ''))
            else:
                try:
                    for kk, vv in v.items():
                        new_kk = kk.replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', ''))
                        v[new_kk] = v.pop(kk)
                        v[new_kk] = v[new_kk].replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', ''))
                except:
                    try:
                        for vv in v:
                            if isinstance(vv, str):
                                vv = vv.replace("$SYSTEMATIC", sysVar).replace("$NOMINAL", "nom").replace("$LEP_POSTFIX", sysDict.get('lep_postfix', ''))
                    except:
                        pass
    return systs
