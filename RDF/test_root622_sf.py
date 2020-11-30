import ROOT
import numpy
import ctypes
import array
import pdb

print("For the rest of the design, we need to create a vector of LUTs, probably using a manager that gets an std::map<string, std::vector<std::string>> as input containing the key names (used as branch names, which also need to be unique? No, we need to use two histos to get the electron ID efficiency in 2017 and 2016 due to the 'low efficiency' ones... so just the unique reference key for the LUT class) along with the file, histo/profile/spline path inside the file, with the key name eventually passed to the LUT creator. Perhaps the vectors 3rd-6th elements can be the accessors and branch names that will be passed (in order) to the corrector, the type being deduced form the length {'file1.root', 'Muont_pt_abseta_SF', 'Nominal'/'Err', 'Muon_pt', 'Muon_eta'} --> TH2Lookup with central or error value, ... 'When all of these are added properly, the manager can 'finalize' things by using the object cloning to match the number of threads (GetNSlots() in RDataFrame). Finally, it can return the vector of correctors for use in multithreaded applications")

# print((ROOT__version__) #Doesn't work before version 6.22, hahahahaha
ROOT.gROOT.ProcessLine(".L FTFunctions.cpp")

#Figure out what's going on here...
ROOT.gROOT.ProcessLine("std::cout << \"Hello, There!\" << std::endl;")
code = """LUT *test2LUT;
          test2LUT = new LUT; //also new LUT ( <initialization parameters> ) in C++ regular syntax
          test2LUT->Add("/afs/cern.ch/user/n/nmangane/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/Kai/python/data/leptonSF/Muon/2017/RunBCDEF_SF_ISO_syst.root",
          "NUM_TightRelIso_DEN_MediumID_pt_abseta", "Test");
          std::cout << test2LUT->TH2Lookup("Test", 35, 1.7) << std::endl;"""
ROOT.gROOT.ProcessLine(code)
# print("ROOT libraries loaded: ", ROOT.gSystem.GetLibraries())
print("testing python retrieval of C++ LUT")
cppLUT = getattr(ROOT, "test2LUT")
print("cppLUT test", cppLUT.TH2Lookup("Test", 35, 1.7))
ROOT.gROOT.ProcessLine("LUT *test2LUTClone(test2LUT);")
cppLUTClone = getattr(ROOT, "test2LUTClone")
print("cppLUT clone test", cppLUTClone.TH2Lookup("Test", 35, 1.7))

# "RunBCDEF_SF_ISO_syst.root==NUM_TightRelIso_DEN_MediumID_pt_abseta",
# "STAT": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelIso_DEN_MediumID_pt_abseta_stat",
# "SYST": "RunBCDEF_SF_ISO_syst.root==NUM_TightRelIso_DEN_MediumID_pt_abseta_syst"
ROOT.gInterpreter.ProcessLine("LUT *testLUT; testLUT = new LUT;") #Need the pointer declaration and the class initialization
testLUT = getattr(ROOT, "testLUT")
testLUT.Add("/afs/cern.ch/user/n/nmangane/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/Kai/python/data/leptonSF/Muon/2017/RunBCDEF_SF_ISO_syst.root", "NUM_TightRelIso_DEN_MediumID_pt_abseta", "TightRelIso/MediumID")
testLUT.Add("/afs/cern.ch/user/n/nmangane/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/Kai/python/data/leptonSF/Muon/2017/RunBCDEF_SF_ISO_syst.root", "NUM_TightRelIso_DEN_MediumID_pt_abseta_stat", "TightRelIso/MediumID_stat")
testLUT.Add("/afs/cern.ch/user/n/nmangane/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/Kai/python/data/leptonSF/Muon/2017/RunBCDEF_SF_ISO_syst.root", "NUM_TightRelIso_DEN_MediumID_pt_abseta_syst", "TightRelIso/MediumID_syst")
print(testLUT.TH2Lookup("TightRelIso/MediumID", 90, 0.4))

#Test Muon_SF_ID_nom
rdf = ROOT.ROOT.RDataFrame("Events", "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/ElMu_selection/tttt-1_2017_v2+ElMu.root")

columns = rdf.GetColumnNames()
for c in columns:
    if "Muon" in str(c) and "ID" in str(c): print(c)
rdf2 = rdf.Define("Muon_SF_ID_altnom", "ROOT::VecOps::RVec<double> ret = {}; "\
                  "for(int i=0; i < Muon_pt.size(); ++i) {"\
                  "ret.push_back(testLUT->TH2Lookup(\"TightRelIso/MediumID\", Muon_pt[i], abs(Muon_eta[i])));"\
                  "}"\
                  "return ret;"
              )
ROOT.gInterpreter.Declare("std::map<std::string, std::vector<std::string>> testMAP;")

era = "2017"

testMAP = getattr(ROOT, "testMAP")
testMAP["TEST"].push_back("Hello")
testMAP["TEST"].push_back("There")
testMAP["TEST"].push_back("Poppet!")
testMAP["MuonID"].push_back("A key")
testMAP["MuonID"].push_back("A File")
testMAP["MuonID"].push_back("A Histogram")

node_and_vecLUT = ROOT.FTA.AddLeptonSF(ROOT.RDF.AsRNode(rdf2), era, testMAP)
rdf3 = node_and_vecLUT.first
np = rdf3.AsNumpy(["Muon_SF_ID_altnom"])
print("rdf3 slot count", rdf.GetNSlots())
print(np.keys())
print(len(np["Muon_SF_ID_altnom"]))


# TProfile2DModel::TProfile2DModel(const char* name, const char* title, int nbinsx, const double* xbins, int nbinsy, const double* ybins, const char* option = "")
#                     ModelBefore = ROOT.RDF.TH2DModel("{}_BTaggingYield_{}_sumW_before".format(processName, btagSFProduct.replace("btagSFProduct_","")),
#                                                      "BTaggingYield #Sigma#omega_{before}; HT; nJet",
#                                                      len(HTArr)-1, HTArr, len(nJetArr)-1, nJetArr)
#                     histosDict[processName][channel][k+"__sumW_before"] = nodes[processName]["BaseNode"].Histo2D(ModelBefore,
#                                                                                                                  HTName,
#                                                                                                                  nJetName,
#                                                                                                                  calculationWeightBefore)
# ProfModelPT = ROOT.RDF.TProfile2DModel("prof2", "", len(xarray)-1, xarray, len(yarray)-1, yarray)
# ProfModelETA = ROOT.RDF.TProfile2DModel("prof2", "", len(xarray)-1, xarray, len(yarray)-1, yarray)
# profPT = rdf2.Profile2D(ProfModelPT, 

# Muon_SF_ID_stat
# Muon_SF_ID_syst
# Muon_SF_ISO_nom
# Muon_SF_ISO_stat
# Muon_SF_ISO_syst
# Electron_SF_EFF_nom
# Electron_SF_EFF_unc
# Electron_SF_ID_nom
# Electron_SF_ID_unc
