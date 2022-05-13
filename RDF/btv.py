from __future__ import annotations

from pathlib import Path
from typing import Any

import ROOT

loc = Path(__file__).parent
if not hasattr(ROOT, "apply_btv_sfs"):
    src = loc / "btv.cpp"
    ROOT.gROOT.ProcessLine(f".L {src}")

def btv_sfs(
        input_df: Any,
        era: str,
        is_mc: bool,
        wp: str = "shape_corr",
        algo: str = "deepjet",
        input_collection: str = "Jet",
        jes_systematics: tuple[str] = ("total", "reduced", "complete"),
        is_ultra_legacy: bool = True,
        pre_post_VFP: str | None = None,
) -> Any:
    rdf = input_df
    isUL = str(is_ultra_legacy).lower()
    year = str(era)
    if is_ultra_legacy and era == "2016":
        if pre_post_VFP == "preVFP":
            year += "APV"
        elif pre_post_VFP == "postVFP":
            year += "nonAPV"
        else:
            raise ValueError(
                f"Invalid choice of pre_post_VFP ({pre_post_VFP}) for year ({era})."
            )

    if is_mc:
        corrector_file = None
        if algo == "deepjet":
            if year == "2017":
                corrector_file = loc / "DeepFlavour_94XSF_V4_B_F_JESreduced.json"
            elif year == "2018":
                corrector_file = loc / "DeepJet_102XSF_V2_JESreduced.json"
            else:
                raise NotImplementedError("Yeah...")
        else:
            raise NotImplementedError("Yeah...")
        jes_total = False
        jes_reduced = False
        jes_complete = False
        if "total" in jes_systematics:
            jes_total = True
        if "reduced" in jes_systematics:
            jes_reduced = True
        if "complete" in jes_systematics:
            jes_complete = True
        rdf = ROOT.apply_btv_sfs(ROOT.RDF.AsRnode(df,
                                                  wp,
                                                  era,
                                                  corrector_file,
                                                  algo,
                                                  input_collection,
                                                  jes_total,
                                                  jes_reduced,
                                                  jes_complete,
                                              )
        return rdf
    else:
        return input_df

rdf = ROOT.ROOT.RDataFrame("Events", "root://cms-xrd-global.cern.ch//pnfs/iihe/cms//store/group/fourtop/NoveCampaign/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/NoveCampaign/201126_034536/0000/tree_1.root").Filter("rdfentry_<2000;")

# r = ROOT.apply_btv_sfs(ROOT.RDF.AsRNode(rdf), 
#                        "shape_corr", #std::string wp, 
#                        "2018", #std::string era, 
#                        "correctionlibtest_v2.json.gz", #std::string corrector_file,
#                        "Jet", #std::string input_collection = "Jet",
#                        "hadronFlavour", #std::string flav_name = "hadronFlavour", 
#                        "eta", #std::string eta_name = "eta", 
#                        "pt", #std::string pt_name = "pt",
#                        "btagDeepFlavB", #std::string disc_name = "btagDeepFlavB",
#                        True, #bool jes_total = false, 
#                        True, #bool jes_reduced = false, 
#                        False, #bool jes_complete = false, 
#                        False, #bool verbose=false
#                    )
r = btv_sfs(rdf,
            era,
            is_mc = True,
            wp = "shape_corr",
            algo = "deepjet",
            input_collection = "Jet",
            jes_systematics = ("reduced"),
            is_ultra_legacy = False,
            pre_post_VFP = None,
        )
print([str(c) for c in r.GetDefinedColumnNames()])
c = r.Stats("Jet_btagSF_deepjet_shape_up_jesAbsolute")
print(c.GetMean())
