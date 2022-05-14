from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import ROOT

corrections_btv_status = False
compile_flag, compile_force, compile_gcc = False, False, False
if os.environ.get('FOURTOPNAOD_COMPILE'):
    compile_flag = True 
if os.environ.get('FOURTOPNAOD_FORCE'):
    compile_force = True 
if os.environ.get('FOURTOPNAOD_GCC'):
    compile_gcc = True 

corrections_btv_loc = Path(__file__).parent

if not hasattr(ROOT, "apply_btv_sfs"):
    corrections_btv_src = corrections_btv_loc / "btv.cpp"
    corrections_btv_so  = corrections_btv_loc / "btv.so"
    cmd = ""
    if compile_flag:
        # Fundamentally broken somehow... do not compile
        # do_compile = False
        # if corrections_btv_so.exists():
        #     if compile_force or os.path.getmtime(corrections_btv_so) < os.path.getmtime(corrections_btv_src):
        #         do_compile = True
        # else:
        #     do_compile = True
        # if do_compile:
        #     print(f"Compiling shared object library {corrections_btv_so}")
        #     comp_cmd = f"g++ -c -fPIC -o {corrections_btv_so} {corrections_btv_src} $(root-config --libs --cflags)"
        #     ret_comp = os.system(comp_cmd)
        # decl_cmd = f'#include "{corrections_btv_src}"'
        # load_cmd = f"{corrections_btv_so}"
        # ROOT.gInterpreter.Declare(decl_cmd)
        # ROOT.gSystem.Load(load_cmd)
        cmd = f".L {corrections_btv_src}"
        ROOT.gROOT.ProcessLine(cmd)
    elif compile_gcc:
        # print("To compile the loaded file, append a '+' to the '.L <file_name>+' line, and to specify gcc as the compile, also add 'g' after that")
        cmd = f".L {corrections_btv_src}+g"
        ROOT.gROOT.ProcessLine(cmd)
    else:
        cmd = f".L {corrections_btv_src}"
        ROOT.gROOT.ProcessLine(cmd)

def apply_btv_sfs(
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
                corrector_file = corrections_btv_loc / "DeepFlavour_94XSF_V4_B_F_JESreduced.json"
            elif year == "2018":
                corrector_file = corrections_btv_loc / "DeepJet_102XSF_V2_JESreduced.json"
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

corrections_btv_status = True
