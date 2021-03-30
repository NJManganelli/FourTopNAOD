import ROOT
ROOT.gInterpreter.ProcessLine(".L test_lepton_selection.cpp")

rdf = ROOT.ROOT.RDataFrame("Events", "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_topNanoAOD_v6_1_1.root")
rdfQCD1 = ROOT.ROOT.RDataFrame("Events", "root://cms-xrd-global.cern.ch//store/mc/RunIIAutumn18NanoAODv7/QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/100000/19F322DD-B815-C040-A761-34BDDE5AD645.root")
rdfQCD2 = ROOT.ROOT.RDataFrame("Events", "root://cms-xrd-global.cern.ch//store/mc/RunIIAutumn18NanoAODv7/QCD_bEnriched_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/120000/B1B4AA9E-8886-814A-83D2-E4343E4F00F3.root")
for era in ["2017", "2018"]:
    datasuberas = [(False, "")]
    if era == "2018": 
        datasuberas += [(True, "A")]
    datasuberas += [(True, "B"), (True, "C"), (True, "D")]
    if era == "2017":
        datasuberas += [(True, "E"), (True, "F")]
    for decayChannel, triggerChannels in {"ElMu": ["ElMu", "El", "Mu", "MET"], "MuMu": ["MuMu", "Mu", "MET"], "ElEl": ["ElEl", "El", "MET"]}.items():
        for triggerChannel in triggerChannels:
            for isData, subera in datasuberas:        
                pass
                # test = ROOT.applyTriggerSelection(ROOT.RDF.AsRNode(rdf), era, triggerChannel, decayChannel, isData, subera, "Loose", "Loose", False)

rdfQCD1test = ROOT.applyTriggerSelection(ROOT.RDF.AsRNode(rdfQCD1), "2018", "ElMu", "ElMu", False, "", "Loose", "Loose", False)
# nQCD1 = rdfQCD1.Count()
# nQCD1Cut = rdfQCD1test.Count()
# print(nQCD1Cut.GetValue()/nQCD1.GetValue(), nQCD1Cut.GetValue())

rdfQCD2test = ROOT.applyTriggerSelection(ROOT.RDF.AsRNode(rdfQCD2), "2018", "ElMu", "ElMu", False, "", "Loose", "Loose", False)
# nQCD2 = rdfQCD2.Count()
# nQCD2Cut = rdfQCD2test.Count()
# print(nQCD2Cut.GetValue()/nQCD2.GetValue(), nQCD2Cut.GetValue())
rdfQCD2test = ROOT.applyTriggerSelection(ROOT.RDF.AsRNode(rdfQCD2), "2018", "MuMu", "MuMu", False, "", "Loose", "Loose", False)
