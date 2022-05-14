from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import ROOT

ftfuncions_load_status = False
compile_flag, compile_force, compile_gcc = False, False, False
if os.environ.get('FOURTOPNAOD_COMPILE'):
    compile_flag = True 
if os.environ.get('FOURTOPNAOD_FORCE'):
    compile_force = True 
if os.environ.get('FOURTOPNAOD_GCC'):
    compile_gcc = True 
print(compile_flag, compile_force, compile_gcc)

ftfunctions_loc = Path(__file__).parent

#Declare random number generator
if not hasattr(ROOT, "rng"):
    ROOT.gInterpreter.Declare("TRandom3 rng = TRandom3();")
if not hasattr(ROOT, "AddProgressBar"):
    ROOT.gInterpreter.Declare("""
    const UInt_t barWidth = 60;
    ULong64_t processed = 0, totalEvents = 0;
    std::string progressBar;
    std::mutex barMutex; 
    auto registerEvents = [](ULong64_t nIncrement) {totalEvents += nIncrement;};

    ROOT::RDF::RResultPtr<ULong64_t> AddProgressBar(ROOT::RDF::RNode df, int everyN=10000, int totalN=100000) {
        registerEvents(totalN);
        auto c = df.Count();
        c.OnPartialResultSlot(everyN, [everyN] (unsigned int slot, ULong64_t &cnt){
            std::lock_guard<std::mutex> l(barMutex);
            processed += everyN; //everyN captured by value for this lambda
            progressBar = "[";
            for(UInt_t i = 0; i < static_cast<UInt_t>(static_cast<Float_t>(processed)/totalEvents*barWidth); ++i){
                progressBar.push_back('|');
            }
            // escape the '\' when defined in python string
            std::cout << "\\r" << std::left << std::setw(barWidth) << progressBar << "] " << processed << "/" << totalEvents << std::flush;
        });
        return c;
    }
    """)

if not hasattr(ROOT, "FTA"):
    ftfunctions_src = ftfunctions_loc / "FTFunctions.cpp"
    ftfunctions_so  = ftfunctions_loc / "FTFunctions.so"
    cmd = ""
    # if compile_flag:
    #     raise NotImplementedError("Compiling automatically not yet supported.")
    if compile_flag:
        if compile_force or not ftfunctions_so.exists():
            comp_cmd = f"g++ -c -fPIC -o {ftfunctions_so} {ftfunctions_src} $(root-config --libs --cflags)"
            decl_cmd = f'#include "{ftfunctions_src}"'
            load_cmd = f"{ftfunctions_so}"
            ret_comp = os.system(comp_cmd)
            ROOT.gInterpreter.Declare(decl_cmd)
            ROOT.gSystem.Load(load_cmd)
            # g++ -c -fPIC -o FTFunctions.so FTFunctions.cpp $(root-config --libs --cflags)
            # ROOT.gInterpreter.Declare('#include "FTFunctions.cpp"')
            # ROOT.gSystem.Load("FTFunctions.so")
    elif compile_gcc:
        # print("To compile the loaded file, append a '+' to the '.L <file_name>+' line, and to specify gcc as the compile, also add 'g' after that")
        cmd = f".L {ftfunctions_src}+g"
    else:
        cmd = f".L {ftfunctions_src}"
        ROOT.gROOT.ProcessLine(cmd)

ftfunctions_load_status = True
#https://root-forum.cern.ch/t/saving-root-numba-declare-callables-in-python/44020/2
#Alternate formulations of loading the functions:
#1 compile externally and then load it
#2 compile in ROOT from python, with the first part optionally done externally or previously (it shouldn't recompile if it already exists?), and option 'k' keeps the .so persistent
# print("Compiling")
# ROOT.gSystem.CompileMacro("FTFunctions.cpp", "kO")
# print("Declaring")
# ROOT.gInterpreter.Declare('#include "FTFunctions.cpp"')
# print("Loading")
# ROOT.gInterpreter.Load("FTFunctions_cpp.so")
# print("Done")

# David Ren-Hwa Yu
# 22:43
# In older versions of ROOT, I vaguely remember that you had to load the header files for the libraries, like 

# gInterpreter.Declare("#include \"MyTools/RootUtils/interface/HistogramManager.h\"")
# gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/$SCRAM_ARCH/libMyToolsRootUtils.so"))
# ROOT.gROOT.ProcessLine(".L FTFunctions.cpp+g") #+ compiles, g specifies gcc as the compiler to use instead of whatever ROOT naturally prefers (llvm? clang?)
