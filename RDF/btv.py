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
        if algo.lower() == "deepjet":
            if year == "2017":
                corrector_file = loc / "DeepFlavour_94XSF_V4_B_F_JESreduced.json"
            elif year == "2018":
                corrector_file = loc / "DeepJet_102XSF_V2_JESreduced.json"
            else:
                raise NotImplementedError(f"{algo} has no matching file for {era}")
        else:
            raise NotImplementedError(f"{algo} has no matching file for {era}")
        corrector_file = str(corrector_file)
        jes_total = False
        jes_reduced = False
        jes_complete = False
        for jes in jes_systematics:
            jl = jes.lower()
            if jl == "total":
                jes_total = True
            if jl == "reduced":
                jes_reduced = True
            if jl == "complete":
                jes_complete = True
        rdf = ROOT.apply_btv_sfs(ROOT.RDF.AsRNode(input_df),
                                 wp,
                                 era,
                                 corrector_file,
                                 algo.lower(),
                                 input_collection,
                                 jes_total,
                                 jes_reduced,
                                 jes_complete,
        )
        return rdf
    else:
        return input_df

# ROOT.EnableImplicitMT(12)
# rdf = ROOT.ROOT.RDataFrame("Events", "root://cms-xrd-global.cern.ch//pnfs/iihe/cms//store/group/fourtop/NoveCampaign/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/NoveCampaign/201126_034536/0000/tree_1.root")

# era = "2018"
# r = btv_sfs(rdf,
#             "2018",
#             is_mc = True,
#             wp = "shape_corr",
#             algo = "deepjet",
#             input_collection = "Jet",
#             jes_systematics = ("total", "reduced"),
#             is_ultra_legacy = False,
#             pre_post_VFP = None,
#         )
# r2 = btv_sfs(rdf,
#             "2017",
#             is_mc = True,
#             wp = "shape_corr",
#             algo = "deepjet",
#             input_collection = "Jet",
#             jes_systematics = ("total", "reduced"),
#             is_ultra_legacy = False,
#             pre_post_VFP = None,
#         )
# testing = [(col, r.Stats(col)) for col in r.GetDefinedColumnNames()]
# testing2 = [(col, r2.Stats(col)) for col in r2.GetDefinedColumnNames()]
# c = r.Count()
# import time
# start = time.perf_counter()
# print(c.GetValue())
# print("took", time.perf_counter() - start, "s to process", c.GetValue(), "events")
# for col, stats in testing + testing2:
#     print(col, stats.GetMin(), stats.GetMean(), stats.GetMax())
