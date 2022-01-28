import ROOT
def declare_cpp_constants(name, isData, constants_dict, nLHEScaleSumw=9, nLHEPdfSumw=33, normalizeScale=False, normalizePdf=False):
    """Declare constants via ROOT.gInterpreter.ProcessLine, such as renormalization factors from the sample meta Runs tree"""
    if isData:
        print("Finished declaring Data constants")
        return
    cpp_code_scale = "ROOT::VecOps::RVec<Double_t> $SAMPLE_LHESCaleSumw = {".replace("$SAMPLE", make_cpp_safe_name(name))
    for nScale in range(nLHEScaleSumw):
        if nScale > 0: cpp_code_scale += ", "
        if normalizeScale:
            cpp_code_scale += str(constants_dict["LHEScaleSumw_{nscale}".format(nscale=nScale)])
        else:
            cpp_code_scale += "1.0000"
    cpp_code_scale += "};"
    ROOT.gInterpreter.ProcessLine(cpp_code_scale)

    cpp_code_pdf = "ROOT::VecOps::RVec<Double_t> $SAMPLE_LHEPdfSumw = {".replace("$SAMPLE", make_cpp_safe_name(name))
    for nPDF in range(nLHEPdfSumw):
        if nPDF > 0: cpp_code_pdf += ", "
        if normalizePdf:
            cpp_code_pdf += str(constants_dict["LHEPdfSumw_{npdf}".format(npdf=nPDF)])
        else:
            cpp_code_pdf += "1.0000"    
    cpp_code_pdf += "};"
    ROOT.gInterpreter.ProcessLine(cpp_code_pdf)

    print("Finished declaring Monte Carlo constants")
    print(cpp_code_scale)
    print(cpp_code_pdf)
    return

def make_cpp_safe_name(name):
    return name.replace("-", "_")
