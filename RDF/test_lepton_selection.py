import ROOT
ROOT.gInterpreter.ProcessLine(".L test_lepton_selection.cpp")

rdf = ROOT.ROOT.RDataFrame("Events", "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_topNanoAOD_v6_1_1.root")
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
                test = ROOT.applyTriggerSelection(ROOT.RDF.AsRNode(rdf), era, triggerChannel, decayChannel, isData, subera, "Loose", "Loose", False)
