from __future__ import annotations
from typing import Any, Optional
import uproot, hist
import numpy as np
from copy import deepcopy

def make_QCDScales_with_rate_tttt(tfile, 
                                  mode="add", 
                                  filter_name="/tttt___.*___HT___OSDL_RunII_ttttmu.*/", 
                                  normalizations={
                                      "OSDL_RunII_ttttmuRFcorrelatedDown": 1.2991,
                                      "OSDL_RunII_ttttmuFNomRDown": 1.2298,
                                      "OSDL_RunII_ttttmuRNomFDown": 1.0753,
                                      "OSDL_RunII_ttttmuRNomFUp": 0.9358,
                                      "OSDL_RunII_ttttmuFNomRUp":  0.8088,
                                      "OSDL_RunII_ttttmuRFcorrelatedUp": 0.7490
                                  }
                                 ):
    _mode = mode.lower()
    if _mode not in ["add", "remove"]:
        raise ValueError(self.name + " requires mode to be 'add (scale)' or 'remove (divide out)' for the normalizations")
    
    
    ret = {}
    for k, v in tfile.items(filter_name=filter_name, cycle=False):
        mu_type = k.split("___")[-1]
        if _mode == "add":
            mu_factor = normalizations[mu_type]
            name = k.replace("ttttmu", "ttttmuWithRate")
        else:
            mu_factor = 1.0/normalizations[mu_type]
            name = k.replace("ttttmu", "ttttmuWithoutRate")
        ret[name] = mu_factor * v.to_hist()
    return ret
    

def make_envelope_hists(hist_list, nom_hist=None):
    """Wonky but minimally working 1D and 2D envelopes. Do not trust for more dimensions, it probably doesn't generalize."""
    new_axis=0 #don't play around with it
    new_hist_up = deepcopy(hist_list[0])
    new_hist_up.reset()
    new_hist_down = deepcopy(new_hist_up)
    
    values = []
    variances = []
    i = 0
    for i, h in enumerate(hist_list):
        values.append(h.values(flow=True))
        variances.append(h.variances(flow=True))
    if nom_hist:
        values.append(nom_hist.values(flow=True))
        variances.append(nom_hist.variances(flow=True))
    #Stack values and variances
    s_values = np.stack(values, axis=new_axis)
    s_variances = np.stack(variances, axis=new_axis)
    
    # Find the minima and maxima per bin, corresponding to new_axis
    s_val_argmax = np.argmax(s_values, axis=new_axis, keepdims=True)
    s_val_argmin = np.argmin(s_values, axis=new_axis, keepdims=True)
    
    # Get the corresponding minima and maxima and (for now) matching variances
    s_val_max = np.take_along_axis(s_values, s_val_argmax, axis=new_axis)[0]
    s_var_max = np.take_along_axis(s_variances, s_val_argmax, axis=new_axis)[0]
    s_val_min = np.take_along_axis(s_values, s_val_argmin, axis=new_axis)[0]
    s_var_min = np.take_along_axis(s_variances, s_val_argmin, axis=new_axis)[0]
    
    # Set the values and variances accordingly, this one doesn't use new_axis
    new_hist_up.view(flow=True)[...] = np.stack([s_val_max, s_var_max], axis=-1)
    new_hist_down.view(flow=True)[...] = np.stack([s_val_min, s_var_min], axis=-1)
    
    return new_hist_up, new_hist_down
    
def test_envelope():
    init = hist.Hist.new.Reg(3, 0, 3, name="x", flow=False).Reg(3, 0, 3, name="y", flow=False).Weight()
    a = deepcopy(init)
    b = deepcopy(init)
    c = deepcopy(init)
    a.values()[...] = np.array([[-2, -1, 0],
                                [-1, -1, 0],
                                [0, 1, 1]], dtype=np.int32).T[:, ::-1]
    b.values()[...] = np.array([[0, 1, 1],
                                [-2, 0, 1],
                                [-2, -1, -2]], dtype=np.int32).T[:, ::-1]
    c.values()[...] = np.array([[1, 0, -2],
                                [1, 1, -2],
                                [1, 0, 0]], dtype=np.int32).T[:, ::-1]
    d1, d2 = make_envelope_hists([a, b, c])
    #d2.plot()
    d2.plot()
    assert np.all(d1.values() == 1)
    print(d2.values()[:, :])
    assert np.all(d2.values()[0, :] == -2)
    assert np.all(d2.values()[1, :] == -1)
    assert np.all(d2.values()[2, :] == -2)

def make_QCDScales_envelopes(tfile,
                  top_filter_name="/.*___.*___HT___OSDL_RunII_.*mu(R|F).*(Down|Up)/"):
    keys = tfile.keys(filter_name=top_filter_name, cycle=False)
    skeys = [kk.split("___") for kk in keys]
    
    tttt_rates = make_QCDScales_with_rate_tttt(tfile, 
                                               mode="add", 
                                               filter_name=top_filter_name.replace(".*mu", "ttttmu")
                                               #filter_name=f"/tttt___.*___.*___OSDL_RunII_ttttmu.*/"
                                              )
                                             
    tree = {}
    ret_hists = {}
    ret_rates = {}
    for proc, cat, var, syst in skeys + [kk.split("___") for kk in tttt_rates]:
        if proc not in tree:
            tree[proc] = {}
        if cat not in tree[proc]:
            tree[proc][cat] = {}
        if var not in tree[proc][cat]:
            tree[proc][cat][var] = {}
        search_key = f"{proc}___{cat}___{var}___{syst}"
        if search_key in tttt_rates:
            tree[proc][cat][var][syst] = tttt_rates[search_key]
        else:
            tree[proc][cat][var][syst] = tfile[f"{proc}___{cat}___{var}___{syst}"].to_hist()
            
        #rates for the datacard maker
        if cat not in ret_rates:
            ret_rates[cat] = {}
        if proc not in ret_rates[cat]:
            ret_rates[cat][proc] = {}
    
    
    for proc in tree.keys():
        for cat in tree[proc].keys():
            for var in tree[proc][cat].keys():
                syst_hists = tree[proc][cat][var]
                nom_hist = tfile[f"{proc}___{cat}___{var}___nom"].to_hist()
                for env_set, disq in [(f"OSDL_RunII_{proc}muWithRate", "$NODISQ"),
                                      (f"OSDL_RunII_{proc}muWithoutRate", "$NODISQ"),
                                      (f"OSDL_RunII_{proc}mu", "Rate"),
                                     ]:
                    hist_name_base = f"{proc}___{cat}___{var}___{env_set}RFenvelope"
                    hist_list = [v for k,v in syst_hists.items() if k.startswith(env_set) and disq not in k]
                    #print(proc, cat, var, env_set, hist_list,"\n\n")
                    if len(hist_list) == 0:
                        continue
                    hist_env_up, hist_env_down = make_envelope_hists(hist_list, nom_hist=nom_hist)
                    # alt_base = dict_to_hist_axis({k:v for k,v in syst_hists.items() if k.startswith(env_set) and disq not in k},
                    #                              "systematic",
                    #                              "systematic",
                    #                              "StrCategory",
                    #                              hist.storage.Weight(),
                    #                              {"growth": True},
                    #                              None
                    #                              )
                    # if proc == "tttt" and cat == "HT500_nMediumDeepJetB4p_nJet8p":
                    #     print("\n".join([axis.name for axis in alt_base.axes]))
                    #     alt_base_up = alt_base[{"systematic": hist.tag.Slicer()[::sum]}]
                    #     print(alt_base_up.values())
                    #     print(hist_env_up.values())
                        
                    ret_hists[hist_name_base + "Up"] = hist_env_up
                    ret_hists[hist_name_base + "Down"] = hist_env_down
                    ret_rates[cat][proc][hist_name_base + "Up"] = hist_env_up.sum().value
                    ret_rates[cat][proc][hist_name_base + "Down"] = hist_env_down.sum().value
                    
                    # print(proc, cat, var, env_set, len(hist_list))
    return ret_hists, ret_rates
        
