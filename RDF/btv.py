import ROOT

ROOT.gROOT.ProcessLine(".L btv.cpp")
rdf = ROOT.ROOT.RDataFrame("Events", "root://cms-xrd-global.cern.ch//pnfs/iihe/cms//store/group/fourtop/NoveCampaign/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/NoveCampaign/201126_034536/0000/tree_1.root").Filter("rdfentry_<2000;")

r = ROOT.apply_btv_sfs(ROOT.RDF.AsRNode(rdf), 
                       "shape_corr", #std::string wp, 
                       "2018", #std::string era, 
                       "correctionlibtest_v2.json.gz", #std::string corrector_file,
                       "Jet", #std::string input_collection = "Jet",
                       "hadronFlavour", #std::string flav_name = "hadronFlavour", 
                       "eta", #std::string eta_name = "eta", 
                       "pt", #std::string pt_name = "pt",
                       "btagDeepFlavB", #std::string disc_name = "btagDeepFlavB",
                       True, #bool jes_total = false, 
                       True, #bool jes_reduced = false, 
                       False, #bool jes_complete = false, 
                       False, #bool verbose=false
                   )
print([str(c) for c in r.GetDefinedColumnNames()])
c = r.Stats("Jet_btagSF_deepjet_shape_up_jesAbsolute")
print(c.GetMean())
