import ROOT
import math
import numpy as np

f = ROOT.TFile.Open("April24_envelopedWithRate_RunII_HT_shapes_splusb.root", "read")
tds = [kk for kk in f.GetListOfKeys() if "postfit" in kk.GetName()]

#Lists of all bin values
all_bins = dict()
#Store the category to identify this bin
bin_labels = []
#Count number of bins in each category
category_bins = dict()
#Category intergrals for summary plot
category_summary = dict()
#Keep track of the total length of bins
total_bins = 0
#Set of all procs for backfilling
all_cat_procs = set()

#starting and ending range offset/endset: offset=0 and endset=2 to include flow bins, 1 and 1 to skip
# offset = 1
# endset = 1
offset = 0
endset = 2
for category_key in tds:
  category = category_key.GetName()
  category_bins[category] = 0
  category_summary[category] = dict()
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
      all_bins[proc] = [0]*(total_bins - hnb) 
    else:
      pass
      
    for bin in range(offset, hnb+endset):
      this_val = h.GetBinContent(bin)
      if math.isnan(this_val):
        this_val = 0
        # print("process", proc, "bin", bin, "in category", category, "is NaN")
      else:
        pass
      all_bins[proc].append(this_val)
      if i_p == 0:
        # breakpoint()
        bin_labels.append(category+"_bin"+str(i_p+offset))
    category_summary[category][proc] = sum(all_bins[proc][-(hnb+1):])
  all_cat_procs = all_cat_procs.union(these_cat_procs)
  #Backfill a proc array if it was missing in this iteration
  for proc in all_cat_procs - these_cat_procs:
    all_bins[proc] += backfill
    category_summary[category][proc] = 0
      
  # print("category", category)
  # print("all bins", all_bins)
  # print("bin labels", bin_labels)
  # print("category bins", category_bins)
  # print("total bins", total_bins)
s = np.array(all_bins['TotalSig'])
b = np.array(all_bins['TotalBkg'])
s_sqrt_splusb = np.divide(s, np.sqrt(s+b), where=((s+b) > 0) & (s > 0))
argsort = np.argsort(s_sqrt_splusb)

s_sqrt_splusb[argsort]
