import ROOT
import argparse
from pathlib import Path

def th1_to_numpy(th1, flow=True):
    https://root.cern.ch/doc/master/TArrayD_8cxx_source.html#l00106
    https://github.com/scikit-hep/root_numpy/blob/b062fefe5ee8164aea6c90d7d4435890a87dc112/root_numpy/_hist.py
    count = th1.GetXaxis().GetNbins()
    if flow:
        count += 2
        offset = 0
    else:
        if isinstance(ROOT.TH1D):
            offset = 8 #bytes -> fp64
        if isinstance(ROOT.TH1F):
            offset = 4 #bytes -> fp64
        if isinstance(ROOT.TH1I):
            offset = 4 #bytes -> fp64
        # if isinstance(ROOT.TH1C):
        #     offset = 8 #bytes -> fp64
        # if isinstance(ROOT.TH1S):
        #     offset = 8 #bytes -> fp64
        else:
            raise NotImplementedError("TH1D is only supported type for conversion")
    return np.frombuffer(th1.GetArray(), count=count, offset=offset))

def th1_from_numpy(th1, contents):
    count = th1.GetXaxis().GetNbins()+2
    th1.
        if isinstance(ROOT.TH1D):
            offset = 8 #bytes -> fp64
        else:
            raise NotImplementedError("TH1D is only supported type for conversion")
    return np.frombuffer(th1.GetArray(), count=count, offset=offset))

void TArrayD::Set(Int_t n, const Double_t *array)

def envelope(hist_dict, systematic_name):
    for k, v in hist_dict.items():
        
    pass

def add_tttt_rate_effect(hist_dict):
    #  LHEScaleSumw_0: 1.2991
    # LHEScaleSumw_1: 1.2298
    # LHEScaleSumw_2: 1.1685
    # LHEScaleSumw_3: 1.0753
    # LHEScaleSumw_4: 1.0000
    # LHEScaleSumw_5: 0.9358
    # LHEScaleSumw_6: 0.8800
    # LHEScaleSumw_7: 0.8088
    # LHEScaleSumw_8: 0.7490    
    rates = {
        "OSDL_RunII_ttttmucorrelatedRFDown": 1.2991,
        "OSDL_RunII_ttttmuRFcorrelatedDown": 1.2991,
        "OSDL_RunII_ttttmuFNomRDown": 1.2298,
        "OSDL_RunII_ttttmuRNomFDown": 1.0753,
        "OSDL_RunII_ttttmuRNomFUp": 0.9358,
        "OSDL_RunII_ttttmuFNomRUp":  0.8088,
        "OSDL_RunII_ttttmucorrelatedRFUp": 0.7490,
        "OSDL_RunII_ttttmuRFcorrelatedUp": 0.7490
    }    
    new_dict = {}
    for k, v in hist_dict.items():
        if "ttttmu" not in k:
            continue
        rate_key = k.split("___")[-1]
        new_key = k.replace("ttttmu", "withrate_ttttmu")
        try:
            new_dict[new_key] = v.Clone(new_key)
            new_dict[new_key].Scale(rates[rate_key])
            assert abs(new_dict[new_key].Integral()/hist_dict[k].Integral() - rates[rate_key]) < 1e-4, "FUCK"
        except:
            print("GOD DAMN IT")
            breakpoint()
    return new_dict
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Envelope the QCD Scales/Renormalization and Factorization Scales and create variants of the tttt signal variations where the rate effects are included (for limit and signal-strength setting; the non-rate versions are appropriate for the cross-section evaluation, which is the default mode employed in FTAnalyzer.py as of July 2022)')
    parser.add_argument('file', action='store', type=str)
    args = parser.parse_args()
    file_path = Path(args.file)
    if file_path.is_file():
        print("Open Sesame")
    f = ROOT.TFile.Open(str(file_path), "read")
    #Get all histograms with muRFcorrelated, muRNomF, or muFNomR in their name
    muRF_histos = dict([(kk.GetName(), f.Get(kk.GetName())) for kk in f.GetListOfKeys() if "muF" in kk.GetName() or "muR" in kk.GetName()])
    #Select subset of histograms for the tttt signal to add the rate effects back in for
    tttt_histos = dict([(k, v) for k, v in muRF_histos.items() if k.startswith("tttt")])
    #Add in tttt rate effects
    rate_tttts = add_tttt_rate_effect(tttt_histos)
    breakpoint()
    #Take envelopes of all muRF_histos (separate by background sample...), including the rate and non-rate tttt ones
    #FIXME
    envs = None
