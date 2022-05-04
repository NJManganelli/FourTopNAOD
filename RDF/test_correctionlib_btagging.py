import correctionlib
import pandas
from correctionlib import convert
from correctionlib.schemav2 import (
    VERSION,
    Binning,
    Category,
    Correction,
    CorrectionSet,
    Formula,
)
import gzip

def build_formula(sf):
    if len(sf) != 1:
        raise ValueError(sf)
    try:
        value = sf.iloc[0]["formula"]
    except:
        value = None
        for pkey in sf.iloc[0].keys():
            if pkey.startswith("formula") or "formula" in pkey:
                value = sf.iloc[0][pkey]
    # value = sf.iloc[0]["formula"]
    if "x" in value:
        return Formula.parse_obj(
            {
                "nodetype": "formula",
                "expression": value,
                "parser": "TFormula",
                # For this case, since this is a "reshape" SF, we know the parameter is the discriminant
                "variables": ["discriminant"],
                "parameters": [],
            }
        )
    else:
        return float(value)


def build_discrbinning(sf):
    edges = sorted(set(sf["discrMin"]) | set(sf["discrMax"]))
    return Binning.parse_obj(
        {
            "nodetype": "binning",
            "input": "discriminant",
            "edges": edges,
            "content": [
                build_formula(sf[(sf["discrMin"] >= lo) & (sf["discrMax"] <= hi)])
                for lo, hi in zip(edges[:-1], edges[1:])
            ],
            "flow": "clamp",
        }
    )


def build_ptbinning(sf):
    edges = sorted(set(sf["ptMin"]) | set(sf["ptMax"]))
    return Binning.parse_obj(
        {
            "nodetype": "binning",
            "input": "pt",
            "edges": edges,
            "content": [
                build_discrbinning(sf[(sf["ptMin"] >= lo) & (sf["ptMax"] <= hi)])
                for lo, hi in zip(edges[:-1], edges[1:])
            ],
            "flow": "clamp",
        }
    )


def build_etabinning(sf):
    edges = sorted(set(sf["etaMin"]) | set(sf["etaMax"]))
    return Binning.parse_obj(
        {
            "nodetype": "binning",
            "input": "abseta",
            "edges": edges,
            "content": [
                build_ptbinning(sf[(sf["etaMin"] >= lo) & (sf["etaMax"] <= hi)])
                for lo, hi in zip(edges[:-1], edges[1:])
            ],
            "flow": "error",
        }
    )


# def build_flavor(sf):
#     keys = sorted(sf["jetFlavor"].unique())
#     return Category.parse_obj(
#         {
#             "nodetype": "category",
#             "input": "flavor",
#             "content": [
#                 {"key": key, "value": build_etabinning(sf[sf["jetFlavor"] == key])}
#                 for key in keys
#             ],
#         }
#     )

def build_flavor(sf):
    keys = sorted(sf["jetFlavor"].unique())
    return Category.parse_obj(
        {
            "nodetype": "category",
            "input": "flavor",
            "content": [
                {"key": str(key), "value": build_etabinning(sf[sf["jetFlavor"] == key])}
                for key in keys
            ],
        }
    )


def build_systs(sf):
    keys = list(sf["sysType"].unique())
    return Category.parse_obj(
        {
            "nodetype": "category",
            "input": "systematic",
            "content": [
                {"key": key, "value": build_flavor(sf[sf["sysType"] == key])}
                for key in keys
            ],
        }
    )


corrs = dict()
for era, sf_file in [
        ("2017", "DeepFlavour_94XSF_V4_B_F_JESreduced.csv"),
        ("2018", "DeepJet_102XSF_V2_JESreduced.csv")
]:

    sf = pandas.read_csv(sf_file, skipinitialspace=True)
    corrs[era] = Correction.parse_obj(
        {
            "version": VERSION,
            "name": f"DeepJet_{era}LegacySF",
            "description": "A btagging scale factor",
            "inputs": [
                {"name": "systematic", "type": "string"},
                {
                    "name": "flavor",
                    # "type": "int", #FIXME
                    "type": "string",
                    "description": "BTV flavor definiton: 0=b, 1=c, 2=udsg",
                },
                {"name": "abseta", "type": "real"},
                {"name": "pt", "type": "real"},
                {
                    "name": "discriminant",
                    "type": "real",
                    "description": "DeepJet output value",
                },
            ],
            "output": {"name": "weight", "type": "real"},
            "data": build_systs(sf),
        }
    )

cset = CorrectionSet.parse_obj(
    {
        "schema_version": VERSION,
        "corrections": [
            corrs["2017"],
            corrs["2018"],
        ],
    }
)

with gzip.open("correctionlibtest.json.gz", "wt") as fout:
    fout.write(cset.json(exclude_unset=True))
