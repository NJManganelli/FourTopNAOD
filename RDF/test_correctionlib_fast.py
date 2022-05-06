import ROOT
import pdb
from itertools import chain
import os
import time
import pickle
import hashlib
import numpy as np
import correctionlib
correctionlib.register_pyroot_binding()

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

    def get_or_create_correctorSet(self):
        if not hasattr(self, "correctorSet"):
            try:
                ROOT.gInterpreter.Declare(f'auto b_load_{self.era} = correction::CorrectionSet::from_file("correctionlibtest_v2.json.gz");')
                ROOT.gInterpreter.Declare(f'auto b_corr = b_load_{self.era}->at("deepJet_shape_{self.era}");')
                self.correctorSet = getattr(ROOT, f'b_load_{self.era}')
                self.corrector = getattr(ROOT, 'b_corr')
            except:
                print("WELP...")
                self.correctorSet = None
                self.corrector = None
            finally:
                return self.corrector


    def load_or_create_calibrator(self, cache=True):
        if hasattr(self, "calibration") and self.calibration is not None:
            return self.calibration
        cache_name = "btag_calibration"+str(hashlib.md5(self.calib_decl.encode()).hexdigest())+".pkl"
        # hash_object = hashlib.md5(mystring.encode())
        # print(hash_object.hexdigest())
        # cache_name = "btag_calibration.pkl"
        if os.path.exists(cache_name):
            print("CALIBRATOR CACHE EXISTS")
            try:
                with open(cache_name, "rb") as pkl_calib:
                    ret = pickle.load(pkl_calib)
                    return ret
            except:
                print("Failed to load pickle-calibrator, instantiating new one")
        ROOT.gInterpreter.Declare(self.calib_decl)
        ret = getattr(ROOT, self.calib_name)
        if cache:
            try:
                print("PICKLING RICK CALIBRATOR")
                pickle.dump(ret, open(cache_name, "wb"))
                print("PICKLING COMPLETE")
            except:
                print("Failed to pickle calibrator")
        return ret

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
        # self.calibration = self.load_or_create_calibrator(cache=True)
        self.reader_names = {}
        self.reader_decls = {}
        self.readers = {}
        self.readervec = {}
        self.reader_init = {}
        x = self.get_or_create_correctorSet()

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
        r = r.Define("Jet_etaForBtag", f"auto tmp = Map(Jet_eta, [](double d){{if(d > {self.max_abs_eta}) return ({self.max_abs_eta} - 0.001); else if(d < -{self.max_abs_eta}) return (-{self.max_abs_eta} + 0.001); else return d;}}); return tmp;")
        if "Jet_pt_nom" in avail_cols:
            jet_pt = "Jet_pt"
            print("\n\nUsing Jet_pt only!!!! Correct or incorrect? YOU DECIDE\n\n")
            # jet_pt = "Jet_pt_nom"
        else:
            jet_pt = "Jet_pt"

        for wp, branchdict in self.branchNames_central_and_systs.items():
            # for wp in self.selectedWPs:
            #     reader = self.getReader(wp)
            if wp == "shape_corr":
                for syst, branchname in branchdict.items():
                    code =        'ROOT::VecOps::RVec<double> tmp = {}; for(int i = 0; i < nJet; ++i){ '\
                                  f'try {{ auto inputs = {{"{syst}", Jet_hadronFlavour[i], abs(Jet_etaForBtag[i]), {jet_pt}[i], Jet_{discr}[i]}};'\
                                  f'tmp.push_back(b_corr->evaluate({{"{syst}", Jet_hadronFlavour[i], abs(Jet_etaForBtag[i]), {jet_pt}[i], Jet_{discr}[i]}}));'\
                                  '} catch(...){ std::cout << "caught exception for inputs: " << inputs << std::endl; }'\
                                  '} return tmp;'
                    code =        'ROOT::VecOps::RVec<double> tmp = {}; for(int i = 0; i < nJet; ++i){ '\
                                  f'const std::vector<std::variant<int,double,std::string>> inputs = {{"{syst}", Jet_hadronFlavour[i], abs(Jet_etaForBtag[i]), {jet_pt}[i], Jet_{discr}[i]}};'\
                                  'try{ tmp.push_back(b_corr->evaluate(inputs)); } catch(const std::exception & e) {tmp.push_back(1.0);}'\
                                  '} return tmp;'
                    # if "cferr" in syst:
                    #     code =        'ROOT::VecOps::RVec<double> tmp = {}; for(int i = 0; i < nJet; ++i){ '\
                    #                   f'const std::vector<std::variant<int,double,std::string>> inputs = {{"{syst}", Jet_hadronFlavour[i], abs(Jet_etaForBtag[i]), {jet_pt}[i], Jet_{discr}[i]}};'\
                    #                   f'if(Jet_hadronFlavour[i] != 4) tmp.push_back(1.0); else tmp.push_back(b_corr->evaluate(inputs));'\
                    #                   '} return tmp;'
                    # else:
                    #     code =        'ROOT::VecOps::RVec<double> tmp = {}; for(int i = 0; i < nJet; ++i){ '\
                    #                   f'const std::vector<std::variant<int,double,std::string>> inputs = {{"{syst}", Jet_hadronFlavour[i], abs(Jet_etaForBtag[i]), {jet_pt}[i], Jet_{discr}[i]}};'\
                    #                   f'if(Jet_hadronFlavour[i] == 4) tmp.push_back(1.0); else tmp.push_back(b_corr->evaluate(inputs));'\
                    #                   '} return tmp;'
                    # code =        'ROOT::VecOps::RVec<double> tmp = {}; for(int i = 0; i < nJet; ++i){ '\
                    #               f'const std::vector<std::variant<int,double,std::string>> inputs = {{"{syst}", Jet_hadronFlavour[i], abs(Jet_etaForBtag[i]), {jet_pt}[i], Jet_{discr}[i]}};'\
                    #               'try{tmp.push_back(b_corr->evaluate(inputs));} catch(std::exception & e){ std::cout << Jet_hadronFlavour[i] << " " << abs(Jet_etaForBtag[i]) << " " << Jet_pt[i] << " " << std::endl; '\
                    #               'std::cout << rdfentry_ << " " << std::get<string>(inputs[0]) << " " << std::get<string>(inputs[1]) << " " << std::get<string>(inputs[2]) << " " << std::get<string>(inputs[3]) << " " << std::get<string>(inputs[4]) << std::endl;}'\
                    #               '} return tmp;'
                                  # 'try{tmp.push_back(b_corr->evaluate(std::string(inputs));} catch(std::exception & e){std::cout << std::string(inputs[0]) << " " << std::string(inputs[1]) << " " << std::string(inputs[2]) << " " << std::string(inputs[3]) << std::endl;}'\
                    print(code)
                    r = r.Define(branchname+"CORLIB", code)
        return r
ROOT.EnableImplicitMT(8)
# print("NO MULTITHREADING IN THIS TEST\n\n\n\n\n\n\n")
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

btagSF2017 = btagSFProducer(era="2017", algo="deepjet", selectedWPs=["shape_corr"], sfFileName=None)
rdf = ROOT.ROOT.RDataFrame("Events", "root://cms-xrd-global.cern.ch//pnfs/iihe/cms//store/group/fourtop/NoveCampaign/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/NoveCampaign/201126_034536/0000/tree_1.root")
btagSF2017.initializeReaders(rdf)
x = btagSF2017.callDefines(rdf)
test_branches = [str(v) for v in x.GetDefinedColumnNames() if str(v).startswith('Jet_btagSF')]
cnt = x.Count()
start = time.time()
print("extracting:", test_branches)
# n = x.AsNumpy([str(v) for v in x.GetDefinedColumnNames() if str(v).startswith('Jet_btagSF')])
diffs = dict()
ntest = 0
all_branches = [str(v) for v in x.GetColumnNames() if str(v).startswith('Jet_btagSF')]
for br in [br for br in test_branches if br.endswith("CORLIB")]:
    brnom = br.replace("CORLIB", "")
    if brnom not in all_branches:
        print("skipping", brnom)
        continue
    x = x.Define("test_diff"+str(ntest), f"return Sum({br}/{brnom} - 1.0);")
    diffs[br] = x.Mean("test_diff"+str(ntest))
    ntest += 1
print("testing means of", ntest, "branches")
print([(name, diff.GetValue()) for name, diff in diffs.items()])
# n = x.AsNumpy([str(v) for v in x.GetDefinedColumnNames() if str(v).startswith('Jet_btagSF')])
# for v in x.GetDefinedColumnNames():
#     if str(v).endswith("CORLIB"):
#         print(str(v))
#         n = x.AsNumpy([str(v)])
print((time.time() - start)/60, "s to process", cnt.GetValue(), "events")
