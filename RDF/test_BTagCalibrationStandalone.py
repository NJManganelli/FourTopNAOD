import ROOT
import pdb
from itertools import chain
import os

def is_relevant_syst_for_shape_corr(flavor_btv, syst, era, jesSystsForShape=["jes"]):
    """Returns true if a flavor/syst combination is relevant"""
    jesSysts = list(chain(*[("up_" + j, "down_" + j)
                            for j in jesSystsForShape]))

    if flavor_btv == 0:
        return syst in ["central",
                        "up_lf", "down_lf",
                        "up_hfstats1", "down_hfstats1",
                        "up_hfstats2", "down_hfstats2"] + jesSysts
    elif flavor_btv == 1:
        return syst in ["central",
                        "up_cferr1", "down_cferr1",
                        "up_cferr2", "down_cferr2"]
    elif flavor_btv == 2:
        return syst in ["central",
                        "up_hf", "down_hf",
                        "up_lfstats1", "down_lfstats1",
                        "up_lfstats2", "down_lfstats2"] + jesSysts
    else:
        raise ValueError("ERROR: Undefined flavor = %i!!" % flavor_btv)
    return True


class btagSFProducer():
    """Calculate btagging scale factors
    """

    def __init__(
            self, era, algo='csvv2', selectedWPs=['M', 'shape_corr'],
            sfFileName=None, verbose=0, jesSystsForShape="Reduced",
    ):
        self.era = era
        self.algo = algo.lower()
        self.selectedWPs = selectedWPs
        self.verbose = verbose
        if isinstance(jesSystsForShape, str):
            if jesSystsForShape.lower() == "reduced":
                self.jesSystsForShape = [ "jesBBEC1", "jesEC2", "jesHF", "jesRelativeBal", "jesFlavorQCD", "jesAbsolute", "jes",]
                if era == "2017":
                    csvFileName = "DeepFlavour_94XSF_V4_B_F_JESreduced.csv"
                    self.jesSystsForShape += ["jesBBEC1_2017", "jesEC2_2017", "jesHF_2017", "jesRelativeSample_2017", "jesAbsolute_2017",]
                elif era == "2018":
                    csvFileName = "DeepJet_102XSF_V2_JESreduced.csv"
                    self.jesSystsForShape += ["jesHEMIssue", "jesBBEC1_2018", "jesEC2_2018", "jesHF_2018", "jesRelativeSample_2018", "jesAbsolute_2018",]
            else:
                raise NotImplementedError("not done...")            
        elif isinstane(jesSystsForShape, list):
            self.jesSystsForShape = jesSystsForShape
        # CV: Return value of BTagCalibrationReader::eval_auto_bounds() is zero
        # in case jet abs(eta) > 2.4 !!
        self.max_abs_eta = 2.4
        # define measurement type for each flavor
        # self.inputFilePath = os.environ['CMSSW_BASE'] + \
        #     "/src/PhysicsTools/NanoAODTools/data/btagSF/"
        self.inputFilePath = "./"
        self.inputFileName = sfFileName
        self.measurement_types = None
        self.supported_wp = None
        supported_btagSF = {
            'deepjet': {
                # 'Legacy2016': {
                #     'inputFileName': "DeepJet_2016LegacySF_V1.csv",
                #     'measurement_types': {
                #         0: "comb",  # b
                #         1: "comb",  # c
                #         2: "incl"   # light
                #     },
                #     'supported_wp': ["L", "M", "T", "shape_corr"]
                # },
                '2017': {
                    # 'inputFileName': "DeepFlavour_94XSF_V3_B_F.csv",
                    'inputFileName': "DeepFlavour_94XSF_V4_B_F_JESreduced.csv",
                    'measurement_types': {
                        0: "comb",  # b
                        1: "comb",  # c
                        2: "incl"   # light
                    },
                    # 'supported_wp': ["L", "M", "T", "shape_corr"]
                    'supported_wp': ["shape_corr"]
                },
                # 'UL2017': {
                #     'inputFileName': "DeepJet_106XUL17SF.csv",
                #     'measurement_types': {
                #         0: "comb",  # b
                #         1: "comb",  # c
                #         2: "incl"   # light
                #     },
                #     'supported_wp': ["L", "M", "T", "shape_corr"]
                # },
                '2018': {
                    # 'inputFileName': "DeepJet_102XSF_V1.csv",
                    'inputFileName': "DeepJet_102XSF_V2_JESreduced.csv",
                    'measurement_types': {
                        0: "comb",  # b
                        1: "comb",  # c
                        2: "incl"   # light
                    },
                    # 'supported_wp': ["L", "M", "T", "shape_corr"]
                    'supported_wp': ["shape_corr"]
                },
                # 'UL2018': {
                #     'inputFileName': "DeepJet_106XUL18SF.csv",
                #     'measurement_types': {
                #         0: "comb",  # b
                #         1: "comb",  # c
                #         2: "incl"   # light
                #     },
                #     'supported_wp': ["L", "M", "T", "shape_corr"]
                # },
            },
            # 'cmva': {
            #     '2016': {
            #         'inputFileName': "btagSF_cMVAv2_ichep2016.csv",
            #         'measurement_types': {
            #             0: "ttbar",  # b
            #             1: "ttbar",  # c
            #             2: "incl"   # light
            #         },
            #         'supported_wp': ["L", "M", "T", "shape_corr"]
            #     }
            # }
        }

        supported_algos = []
        for algo in list(supported_btagSF.keys()):
            if self.era in list(supported_btagSF[algo].keys()):
                supported_algos.append(algo)
        if self.algo in list(supported_btagSF.keys()):
            if self.era in list(supported_btagSF[self.algo].keys()):
                if self.inputFileName is None:
                    self.inputFileName = supported_btagSF[self.algo][self.era]['inputFileName']
                self.measurement_types = supported_btagSF[self.algo][self.era]['measurement_types']
                self.supported_wp = supported_btagSF[self.algo][self.era]['supported_wp']
            else:
                raise ValueError("ERROR: Algorithm '%s' not supported for era = '%s'! Please choose among { %s }." % (
                    self.algo, self.era, supported_algos))
        else:
            raise ValueError("ERROR: Algorithm '%s' not supported for era = '%s'! Please choose among { %s }." % (
                self.algo, self.era, supported_algos))
        for wp in self.selectedWPs:
            if wp not in self.supported_wp:
                raise ValueError("ERROR: Working point '%s' not supported for algo = '%s' and era = '%s'! Please choose among { %s }." % (
                    wp, self.algo, self.era, self.supported_wp))

        # load libraries for accessing b-tag scale factors (SFs) from conditions database
        # for library in ["libCondFormatsBTauObjects", "libCondToolsBTau"]:
        #     if library not in ROOT.gSystem.GetLibraries():
        #         print("Load Library '%s'" % library.replace("lib", ""))
        #         ROOT.gSystem.Load(library)

        # define systematic uncertainties
        self.systs = []
        self.systs.append("up")
        self.systs.append("down")
        self.central_and_systs = ["central"]
        self.central_and_systs.extend(self.systs)

        self.systs_shape_corr = []
        for syst in ['lf', 'hf',
                     'hfstats1', 'hfstats2',
                     'lfstats1', 'lfstats2',
                     'cferr1', 'cferr2'] + self.jesSystsForShape:
            self.systs_shape_corr.append("up_%s" % syst)
            self.systs_shape_corr.append("down_%s" % syst)
        self.central_and_systs_shape_corr = ["central"]
        self.central_and_systs_shape_corr.extend(self.systs_shape_corr)

        self.branchNames_central_and_systs = {}
        for wp in self.selectedWPs:
            branchNames = {}
            if wp == 'shape_corr':
                central_and_systs = self.central_and_systs_shape_corr
                baseBranchName = 'Jet_btagSF_{}_shape'.format(self.algo)
            else:
                central_and_systs = self.central_and_systs
                baseBranchName = 'Jet_btagSF_{}_{}'.format(self.algo, wp)
            for central_or_syst in central_and_systs:
                if central_or_syst == "central":
                    branchNames[central_or_syst] = baseBranchName
                else:
                    branchNames[central_or_syst] = baseBranchName + \
                        '_' + central_or_syst
            self.branchNames_central_and_systs[wp] = branchNames

    def initializeReaders(self, rdf=None):
        # initialize BTagCalibrationReader
        # (cf. https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagCalibration )
        
        # print("first test")
        # otherSysts = ROOT.std.vector(str)(["up_jesRelativeBal", "down_jesRelativeBal"])
        # calibration = ROOT.BTagCalibration(taggerName, csvFileName)
        # reader = ROOT.BTagCalibrationReader(3, "central", otherSysts)
        # for flavor_btv in [0, 1, 2]:
        #     reader.load(calibration, flavor_btv, 'iterativefit')
        # print(reader.eval_auto_bounds("up_jesRelativeBal", 2, 1.3, 74, 0.23))
    
        # calib_decl = f'const BTagCalibration <<name>>("{taggerName}", "{csvFileName}");'.replace("<<name>>", calib_name)
        # calib_decl_copy = f'const BTagCalibration <<copy_name>>(<<name>>);'.replace("<<copy_name>>", calib_name + "_copy").replace("<<name>>", calib_name)
        # ROOT.gInterpreter.Declare(calib_decl)
        # ROOT.gInterpreter.Declare(calib_decl_copy)
        # calib_internal = getattr(ROOT, calib_name)
        # calib_copy_internal = getattr(ROOT, calib_name+"_copy")
        self.max_readers = rdf.GetNSlots() if rdf else 1
        self.calib_name = f"bTagCalib_{self.algo}"
        self.calib_decl = f'const BTagCalibration <<name>>("{self.algo}", "{os.path.join(self.inputFilePath, self.inputFileName)}");'.replace("<<name>>", self.calib_name)
        ROOT.gInterpreter.Declare(self.calib_decl)
        self.calibration = getattr(ROOT, self.calib_name)
        # self.calibration = ROOT.BTagCalibration(
        #     self.algo, os.path.join(self.inputFilePath, self.inputFileName))
        self.reader_names = {}
        self.reader_decls = {}
        self.readers = {}
        self.readervec = {}
        self.reader_init = {}
        for wp in self.selectedWPs:
            self.readervec[wp] = {}
            wp_btv = {"l": 0, "m": 1, "t": 2,
                      "shape_corr": 3}.get(wp.lower(), None)
            syts = None
            if wp_btv in [0, 1, 2]:
                systs = self.systs
            else:
                systs = self.systs_shape_corr
            self.reader_names[wp] = f"btagCalibReader_{self.algo}_{wp}"
            wp_translation = {"l": "LOOSE", "m": "MEDIUM", "t": "TIGHT", "shape_corr": "RESHAPING"}[wp.lower()]
            self.reader_decls[wp] = 'BTagCalibrationReader <<name>>(BTagEntry::OP_{0}, "{1}", {{ {2} }} );'\
                .format(wp_translation, "central", ", ".join(f'"{sv}"' for sv in systs)).replace("<<name>>", self.reader_names[wp])
            ROOT.gInterpreter.Declare(self.reader_decls[wp])
            self.reader_init[wp] = getattr(ROOT, self.reader_names[wp])
            for flavor_btv in [0, 1, 2]:
                if wp.lower() == "shape_corr":
                    self.reader_init[wp].load(self.calibration, flavor_btv, 'iterativefit')
                else:
                    self.reader_init[wp].load(self.calibration, flavor_btv,
                                              self.measurement_types[flavor_btv])
            readervec_name = f"btagCalibReaderVec_{self.algo}_{wp}"
            ROOT.gInterpreter.Declare(f"std::vector<BTagCalibrationReader> {readervec_name} = {{}};")
            self.readervec[wp][readervec_name] = getattr(ROOT, readervec_name)
            
            for x in range(self.max_readers):
                # Copy Construct the initialized and configured readers, lets see if we can cheat here...
                self.readervec[wp][readervec_name].push_back(ROOT.BTagCalibrationReader(self.reader_init[wp]))
        # pdb.set_trace()
        for wp_test in self.readervec.keys():
            for readervec_name in self.readervec[wp_test].keys():
                for x_test in range(len(self.readervec[wp_test][readervec_name])):
                    print(self.readervec[wp_test][readervec_name][x_test])
                    print(self.readervec[wp_test][readervec_name][x_test].eval_auto_bounds("up_jesRelativeBal", 2, 1.3, 74, 0.23))
    def callDefines(self, rdf):
        """Append Define calls to the given RDataFrame node"""
        avail_cols = [str(x) for x in rdf.GetColumnNames()]
        r = rdf
        discr = None
        if self.algo == "csvv2":
            discr = "btagCSVV2"
        elif self.algo == "deepcsv":
            discr = "btagDeepB"
        elif self.algo == "cmva":
            discr = "btagCMVA"
        elif self.algo == "deepjet":
            discr = "btagDeepFlavB"
        else:
            raise ValueError("ERROR: Invalid algorithm '%s'!" % self.algo)
        r = r.Define("Jet_btvFlavour", "auto tmp = Map(Jet_hadronFlavour, [](int d){auto t = abs(d); if(t == 5) return BTagEntry::FLAV_B; else if(t == 4) return BTagEntry::FLAV_C; else if((t < 4) || (t == 21)) return BTagEntry::FLAV_UDSG; else throw std::invalid_argument(\"received invalid Jet_hadronFlavour\");}); return tmp;")
        r = r.Define("Jet_etaForBtag", f"auto tmp = Map(Jet_eta, [](double d){{if(d > {self.max_abs_eta}) return ({self.max_abs_eta} - 0.001); else if(d < -{self.max_abs_eta}) return (-{self.max_abs_eta} + 0.001); else return d;}}); return tmp;")
        if "Jet_pt_nom" in avail_cols:
            jet_pt = "Jet_pt_nom"
        else:
            jet_pt = "Jet_pt"

        pdb.set_trace()
        for wp_test in self.readervec.keys():
            for readervec_name in self.readervec[wp_test].keys():
                for x_test in range(len(self.readervec[wp_test][readervec_name])):
                    print(self.readervec[wp_test][readervec_name][x_test])
                    print(self.readervec[wp_test][readervec_name][x_test].eval_auto_bounds("up_jesRelativeBal", 2, 1.3, 74, 0.23))
                    this_reader_name = list(self.readervec[wp_test].keys())[0]
                    print(this_reader_name)
                    syst = "up_jesRelativeBal"
                    this_decl = f'void call_{x_test}() {{ std::cout << {this_reader_name}[{x_test}].eval_auto_bounds("{syst}", 2, 1.3, 74, 0.23) << std::endl; }}'
                    # this_decl = f'void call_{x_test}() {{ std::cout << {this_reader_name}[{x_test}].eval_auto_bounds("{syst}", BTagEntry::FLAV_B, 1.3, 74, 0.23) << std::endl; }}'
                    ROOT.gInterpreter.Declare(this_decl)
                    print(hasattr(ROOT, f'call_{x_test}'))
                    this_call = getattr(ROOT, f'call_{x_test}')
                    this_call()

        for wp, branchdict in self.branchNames_central_and_systs.items():
            # for wp in self.selectedWPs:
            #     reader = self.getReader(wp)
            if wp == "shape_corr":
                for syst, branchname in branchdict.items():
                    this_reader_name = list(self.readervec[wp].keys())[0]
                    SF_call  = 'ROOT::VecOps::RVec<double> tmp = {}; for(int i = 0; i < nJet; ++i){{ '\
                               f'tmp.push_back({this_reader_name}[rdfslot_].eval_auto_bounds("{syst}", Jet_btvFlavour[i], Jet_etaForBtag[i], {jet_pt}[i], Jet_{discr}[i])); }}'\
                               'return tmp;'
                               # f'tmp.push_back({this_reader_name}[rdfslot_].eval_auto_bounds("{syst}", BTagEntry::jetFlavourFromHadronFlavour(Jet_hadronFlavour[i]), Jet_etaForBtag[i], {jet_pt}[i], Jet_{discr}[i]); }}'\
                    if branchname not in avail_cols:
                        try:
                            r = r.Define(branchname, SF_call)
                        except:
                            pdb.set_trace()
                            print(branchname, SF_call)
                            r = r.Define(branchname, SF_call)
            else:
                for syst, branchname in branchdict.items():
                    this_reader_name = list(self.readervec[wp].keys())[0]
                    SF_call  = 'ROOT::VecOps::RVec<double> tmp = {}; for(int i = 0; i < nJet; ++i){{ '\
                               f'tmp.push_back({this_reader_name}[rdfslot_].eval_auto_bounds("{syst}", Jet_btvFlavour[i], Jet_etaForBtag[i], {jet_pt}[i])); }}'\
                               'return tmp;'
                    if branchname not in avail_cols:
                        try:
                            r = r.Define(branchname, SF_call)
                        except:
                            pdb.set_trace()
                            print(branchname, SF_call)
                            r = r.Define(branchname, SF_call)
        return r
        #OLD
        # for wp in self.selectedWPs:
        #     reader = self.getReader(wp)
        #     isShape = (wp == 'shape_corr')
        #     central_and_systs = (
        #         self.central_and_systs_shape_corr if isShape else self.central_and_systs)
        #     for central_or_syst in central_and_systs:
        #         scale_factors = list(self.getSFs(
        #             preloaded_jets, central_or_syst, reader, 'auto', isShape))
        #         self.out.fillBranch(
        #             self.branchNames_central_and_systs[wp][central_or_syst], scale_factors)
        # return True

    # def getSFs(self, jet_data, syst, reader, measurement_type='auto', shape_corr=False):
    #     if reader is None:
    #         if self.verbose > 0:
    #             print("WARNING: Reader not available, setting b-tagging SF to -1!")
    #         for i in range(len(jet_data)):
    #             yield 1
    #         raise StopIteration
    #     for idx, (pt, eta, flavor_btv, discr) in enumerate(jet_data):
    #         epsilon = 1.e-3
    #         max_abs_eta = self.max_abs_eta
    #         if eta <= -max_abs_eta:
    #             eta = -max_abs_eta + epsilon
    #         if eta >= +max_abs_eta:
    #             eta = +max_abs_eta - epsilon
    #         # evaluate SF
    #         sf = None
    #         if shape_corr:
    #             if is_relevant_syst_for_shape_corr(flavor_btv, syst, self.era, self.jesSystsForShape):
    #                 sf = reader.eval_auto_bounds(
    #                     syst, flavor_btv, eta, pt, discr)
    #             else:
    #                 sf = reader.eval_auto_bounds(
    #                     'central', flavor_btv, eta, pt, discr)
    #         else:
    #             sf = reader.eval_auto_bounds(syst, flavor_btv, eta, pt)
    #         # check if SF is OK
    #         if sf < 0.01:
    #             if self.verbose > 0:
    #                 print("jet #%i: pT = %1.1f, eta = %1.1f, discr = %1.3f, flavor = %i" % (
    #                     idx, pt, eta, discr, flavor_btv))
    #             sf = 1.
    #         yield sf

    # def analyze(self, event):
    #     """process event, return True (go to next module) or False (fail, go to next event)"""
    #     jets = Collection(event, "Jet")

    #     discr = None
    #     if self.algo == "csvv2":
    #         discr = "btagCSVV2"
    #     elif self.algo == "deepcsv":
    #         discr = "btagDeepB"
    #     elif self.algo == "cmva":
    #         discr = "btagCMVA"
    #     elif self.algo == "deepjet":
    #         discr = "btagDeepFlavB"
    #     else:
    #         raise ValueError("ERROR: Invalid algorithm '%s'!" % self.algo)

    #     preloaded_jets = [(jet.pt, jet.eta, self.getFlavorBTV(
    #         jet.hadronFlavour), getattr(jet, discr)) for jet in jets]
    #     for wp in self.selectedWPs:
    #         reader = self.getReader(wp)
    #         isShape = (wp == 'shape_corr')
    #         central_and_systs = (
    #             self.central_and_systs_shape_corr if isShape else self.central_and_systs)
    #         for central_or_syst in central_and_systs:
    #             scale_factors = list(self.getSFs(
    #                 preloaded_jets, central_or_syst, reader, 'auto', isShape))
    #             self.out.fillBranch(
    #                 self.branchNames_central_and_systs[wp][central_or_syst], scale_factors)
    #     return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed


# btagSF2016 = lambda: btagSFProducer("2016")
# btagSF2017 = lambda: btagSFProducer("2017")

ROOT.EnableImplicitMT(6)

era = "2017"
taggerName = "deepjet"
wp = "RESHAPING"
sysType = "central"
otherSysTypes = [
    "up_jesBBEC1",
    "up_jesEC2",
    "up_jesHF",
    "up_jesRelativeBal",
    "up_jesFlavorQCD",
    "up_jesAbsolute",
    "up_jes",
    "down_jesBBEC1",
    "down_jesEC2",
    "down_jesHF",
    "down_jesRelativeBal",
    "down_jesFlavorQCD",
    "down_jesAbsolute",
    "down_jes",
]
if era == "2017":
    csvFileName = "DeepFlavour_94XSF_V4_B_F_JESreduced.csv"
    otherSysTypes += [
        "up_jesBBEC1_2017",
        "up_jesEC2_2017",
        "up_jesHF_2017",
        "up_jesRelativeSample_2017",
        "up_jesAbsolute_2017",
        "down_jesBBEC1_2017",
        "down_jesEC2_2017",
        "down_jesHF_2017",
        "down_jesRelativeSample_2017",
        "down_jesAbsolute_2017",
    ]
elif era == "2018":
    csvFileName = "DeepJet_102XSF_V2_JESreduced.csv"
    otherSysTypes += [
        "up_jesHEMIssue",
        "up_jesBBEC1_2018",
        "up_jesEC2_2018",
        "up_jesHF_2018",
        "up_jesRelativeSample_2018",
        "up_jesAbsolute_2018",
        "down_jesHEMIssue",
        "down_jesBBEC1_2018",
        "down_jesEC2_2018",
        "down_jesHF_2018",
        "down_jesRelativeSample_2018",
        "down_jesAbsolute_2018",
    ]

# calibHandle = getattr(gbl, calibName)
# readerHandle = getattr(gbl, readerName)
# for flav, measType in measurementType.items():
#     readerHandle.load(calibHandle, getattr(gbl.BTagEntry, f"FLAV_{flav}"), measType)
# import bamboo.treefunctions as op
# self.reader = op.extVar("BTagCalibrationReader", readerName)

ROOT.gInterpreter.ProcessLine(".L BTagCalibrationStandalone.cpp")
# btagSF2017 = btagSFProducer(era="2017", algo="deepjet", selectedWPs=["shape_corr"], sfFileName=None, jesSystsForShape="Reduced")
btagSF2017 = btagSFProducer(era="2017", algo="deepjet", selectedWPs=["shape_corr"], sfFileName=None)
rdf = ROOT.ROOT.RDataFrame("Events", "root://cms-xrd-global.cern.ch//store/mc/RunIIAutumn18NanoAODv7/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/NANOAODSIM/Nano02Apr2020_102X_upgrade2018_realistic_v21_ext2-v1/240000/B1E3DEC5-B787-A746-8486-58428EDD3FDC.root")
btagSF2017.initializeReaders(rdf)
btagSF2017.callDefines(rdf)


# print("first test")
# otherSysts = ROOT.std.vector(str)(["up_jesRelativeBal", "down_jesRelativeBal"])
# calibration = ROOT.BTagCalibration(taggerName, csvFileName)
# reader = ROOT.BTagCalibrationReader(3, "central", otherSysts)
# for flavor_btv in [0, 1, 2]:
#     reader.load(calibration, flavor_btv, 'iterativefit')
# print(reader.eval_auto_bounds("up_jesRelativeBal", 2, 1.3, 74, 0.23))

# calib_name = f"bTagCalib_{taggerName}"
# calib_decl = f'const BTagCalibration <<name>>("{taggerName}", "{csvFileName}");'.replace("<<name>>", calib_name)
# calib_decl_copy = f'const BTagCalibration <<copy_name>>(<<name>>);'.replace("<<copy_name>>", calib_name + "_copy").replace("<<name>>", calib_name)
# ROOT.gInterpreter.Declare(calib_decl)
# ROOT.gInterpreter.Declare(calib_decl_copy)
# calib_internal = getattr(ROOT, calib_name)
# calib_copy_internal = getattr(ROOT, calib_name+"_copy")

# reader_name = "btagCalibReader_slot"
# reader_decl = 'BTagCalibrationReader <<name>>(BTagEntry::OP_{0}, "{1}", {{ {2} }} );'\
#     .format(wp.upper(), sysType, ", ".join(f'"{sv}"' for sv in otherSysTypes)).replace("<<name>>", reader_name)
# reader_decl_copy = 'BTagCalibrationReader <<copy_name>>(<<name>>);'.replace("<<copy_name>>", reader_name + "_copy").replace("<<name>>", reader_name)
# ROOT.gInterpreter.Declare(reader_decl)
# ROOT.gInterpreter.Declare(reader_decl_copy)
# reader_internal = getattr(ROOT, reader_name)
# reader_copy_internal = getattr(ROOT, reader_name+"_copy")
pdb.set_trace()

print(calib_internal, reader_internal)


