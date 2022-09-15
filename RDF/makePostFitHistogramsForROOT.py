import ROOT
import math
import numpy as np

def make_yield_summary(category_summary, category_summary_errors, total_categories, filename):
  group_btags =  {"category": {"2": [f'OSDL_{year}_{channel}_nB2_nJ{j}_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for j in ['4', '5', '6', '7', '8p']\
                                   for prepost in ['postfit']],
                             "3": [f'OSDL_{year}_{channel}_nB3_nJ{j}_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for j in ['4', '5', '6', '7', '8p']\
                                   for prepost in ['postfit']],
                             "4+": [f'OSDL_{year}_{channel}_nB4p_nJ{j}_{prepost}'\
                                   for year in ['2017', '2018']\
                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
                                   for j in ['4', '5', '6', '7', '8p']\
                                   for prepost in ['postfit']],
                            }
               }
  for group_name, group_list in group_btags["category"].items():
    stack_cat_summary = dict()
    stack_cat_summary_errors = dict()
    stack_cat_summary[group_name] = dict()
    stack_cat_summary_errors[group_name] = dict()
    for proc in category_summary[group_list[0]].keys():
      print(proc)
  
    # print(group_name, group_list)
    # print([it in category_summary for it in group_list])

  return None

def make_s_sqrt_splusb_plots(all_bins, all_bin_errors, total_bins, filename):
  s = np.array(all_bins['TotalSig'])
  b = np.array(all_bins['TotalBkg'])
  s_sqrt_splusb = np.divide(s, np.sqrt(s+b), where=((s+b) > 0) & (s > 0))
  argsort = np.argsort(s_sqrt_splusb)
  
  # s_sqrt_splusb[argsort]
  
  new_hists = dict()
  for proc, values in all_bins.items():
    new_hists[proc] = ROOT.TH1D(proc, "", total_bins, 1, total_bins+1)
  
  for bin, index in enumerate(argsort):
    for proc in all_bins.keys():
      try:
        new_hists[proc].SetBinContent(bin, all_bins[proc][index])
        new_hists[proc].SetBinError(bin, all_bin_errors[proc][index])
      except:
        breakpoint()
  f = ROOT.TFile.Open(filename, "update")
  f.mkdir("OSDL_postfit_s_sqrt_splusb")
  f.cd("OSDL_postfit_s_sqrt_splusb")

  s = ROOT.THStack()
  color_counter = 1

  for k, h in new_hists.items():
    h.Write()
    if "Total" not in k and "data_obs" not in k:
      h.SetFillColor(color_counter)
      s.Add(h)
  f.Close()
  
  c = ROOT.TCanvas()
  s.Draw("HIST")
  new_hists["data_obs"].SetMarkerStyle(2)
  new_hists["data_obs"].SetFillColor(0)
  new_hists["data_obs"].SetLineColor(0)
  new_hists["data_obs"].Draw("E2 SAME")

  breakpoint()
  return new_hists


f = ROOT.TFile.Open("April24_envelopedWithRate_RunII_HT_shapes_splusb.root", "read")
tds = [kk for kk in f.GetListOfKeys() if "postfit" in kk.GetName()]

#Lists of all bin values
all_bins = dict()
all_bin_errors = dict()
#Store the category to identify this bin
bin_labels = []
#Count number of bins in each category
category_bins = dict()
#Category intergrals for summary plot
category_summary = dict()
category_summary_errors = dict()
#Keep track of the total length of bins
total_bins = 0
total_categories = 0
#Set of all procs for backfilling
all_cat_procs = set()

#starting and ending range offset/endset: offset=0 and endset=2 to include flow bins, 1 and 1 to skip
overflow = True
underflow = True
offset = None
endset = None
if underflow:
  offset = 0
else:
  offset = 1

if overflow:
  endset = 2
else:
  endset = 0
for category_key in tds:
  total_categories += 1
  category = category_key.GetName()
  category_bins[category] = 0
  category_summary[category] = dict()
  category_summary_errors[category] = dict()
  td = f.Get(category)
  procs = [kk.GetName() for kk in td.GetListOfKeys()]
  these_cat_procs = set()
  backfill = None
  for i_p, proc in enumerate(procs):
    these_cat_procs.add(proc)
    h = td.Get(proc)
    #number of bins being grabbed per array
    hnb = h.GetNbinsX() + endset - offset
    category_bins[category] = max(category_bins[category], h.GetNbinsX())
    if i_p == 0:
      #Add to the total number of bins
      total_bins += hnb
      backfill = [0]*hnb
    if proc not in all_bins:
      #Backfill a proc array if a key was missing
      # print("making ", total_bins - hnb, "bins in", proc, "for category", category)
      all_bins[proc] = [0]*(total_bins - hnb) 
      all_bin_errors[proc] = [0]*(total_bins - hnb)
    else:
      pass
      
    labelled = False
    for bin in range(offset, hnb+offset):
      this_val = h.GetBinContent(bin)
      this_error = h.GetBinError(bin)
      if math.isnan(this_val):
        this_val = 0
        this_error = 0
        # print("process", proc, "bin", bin, "in category", category, "is NaN")
      else:
        pass
      all_bins[proc].append(this_val)
      all_bin_errors[proc].append(this_error)
      if not labelled:
        # breakpoint()
        bin_labels.append(category+"_bin"+str(i_p))
        labelled = True
    category_summary[category][proc] = sum(all_bins[proc][-(hnb+1):])
    category_summary_errors[category][proc] = sum([x**2 for x in all_bin_errors[proc][-(hnb+1):]])
  all_cat_procs = all_cat_procs.union(these_cat_procs)
  #Backfill a proc array if it was missing in this iteration
  for proc in all_cat_procs - these_cat_procs:
    all_bins[proc] += backfill
    all_bin_errors[proc] += backfill
    category_summary[category][proc] = 0

breakpoint()
y = make_yield_summary(category_summary, category_summary_errors, total_categories, "junktest.root")
x = make_s_sqrt_splusb_plots(all_bins, all_bin_errors, total_bins, "junktesttest.root")
