import ROOT
import math
import numpy as np

def make_yield_summary(category_summary, category_summary_errors, total_categories, filename):
  group_nb_nj = {"category": {"OSDL_2b_4j": [f'OSDL_{year}_{channel}_nB2_nJ4_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_2b_5j": [f'OSDL_{year}_{channel}_nB2_nJ5_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_2b_6j": [f'OSDL_{year}_{channel}_nB2_nJ6_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_2b_7j": [f'OSDL_{year}_{channel}_nB2_nJ7_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_2b_8pj": [f'OSDL_{year}_{channel}_nB2_nJ8p_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_3b_4j": [f'OSDL_{year}_{channel}_nB3_nJ4_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_3b_5j": [f'OSDL_{year}_{channel}_nB3_nJ5_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_3b_6j": [f'OSDL_{year}_{channel}_nB3_nJ6_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_3b_7j": [f'OSDL_{year}_{channel}_nB3_nJ7_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_3b_8pj": [f'OSDL_{year}_{channel}_nB3_nJ8p_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_4pb_4j": [f'OSDL_{year}_{channel}_nB4p_nJ4_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_4pb_5j": [f'OSDL_{year}_{channel}_nB4p_nJ5_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_4pb_6j": [f'OSDL_{year}_{channel}_nB4p_nJ6_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_4pb_7j": [f'OSDL_{year}_{channel}_nB4p_nJ7_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                              "OSDL_4pb_8pj": [f'OSDL_{year}_{channel}_nB4p_nJ8p_{prepost}'\
                                             for year in ['2017', '2018']\
                                             for channel in ['ElEl', 'ElMu', 'MuMu']\
                                             for prepost in ['postfit']],
                            }
               }
  # group_btags =  {"category": {"OSDL_2btags_njet": [f'OSDL_{year}_{channel}_nB2_nJ{j}_{prepost}'\
  #                                                   for year in ['2017', '2018']\
  #                                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
  #                                                   for j in ['4', '5', '6', '7', '8p']\
  #                                                   for prepost in ['postfit']],
  #                              "OSDL_3btags_njet": [f'OSDL_{year}_{channel}_nB3_nJ{j}_{prepost}'\
  #                                                   for year in ['2017', '2018']\
  #                                                   for channel in ['ElEl', 'ElMu', 'MuMu']\
  #                                                   for j in ['4', '5', '6', '7', '8p']\
  #                                                   for prepost in ['postfit']],
  #                              "OSDL_4+btags_njet": [f'OSDL_{year}_{channel}_nB4p_nJ{j}_{prepost}'\
  #                                                    for year in ['2017', '2018']\
  #                                                    for channel in ['ElEl', 'ElMu', 'MuMu']\
  #                                                    for j in ['4', '5', '6', '7', '8p']\
  #                                                    for prepost in ['postfit']],
  #                            }
  #              }
  #Prepare the histograms
  histograms = {"OSDL_2btags_yields": dict(),
                "OSDL_3btags_yields": dict(),
                "OSDL_4pbtags_yields": dict(),
                "OSDL_all_yields": dict()
              }
  for proc in category_summary[list(category_summary.keys())[0]].keys():
    histograms["OSDL_2btags_yields"][proc] = ROOT.TH1D("OSDL_2btags_yields/"+proc, ";Jet Multiplicity; Events", 5, 4, 9)
    histograms["OSDL_3btags_yields"][proc] = ROOT.TH1D("OSDL_3btags_yields/"+proc, ";Jet Multiplicity; Events", 5, 4, 9)
    histograms["OSDL_4pbtags_yields"][proc] = ROOT.TH1D("OSDL_4pbtags_yields/"+proc, ";Jet Multiplicity; Events", 5, 4, 9)
    histograms["OSDL_all_yields"][proc] = ROOT.TH1D("OSDL_all_yields/"+proc, "", 15, 0, 15)
    for bin, label in [(1, "2b, 4j"),
                       (2, "2b, 5j"),
                       (3, "2b, 6j"),
                       (4, "2b, 7j"),
                       (5, "2b, 8+j"),
                       (6, "3b, 4j"),
                       (7, "3b, 5j"),
                       (8, "3b, 6j"),
                       (9, "3b, 7j"),
                       (10, "3b, 8+j"),
                       (11, "4+b, 4j"),
                       (12, "4+b, 5j"),
                       (13, "4+b, 6j"),
                       (14, "4+b, 7j"),
                       (15, "4+b, 8+j"),
                     ]:
      
      histograms["OSDL_all_yields"][proc].GetXaxis().SetBinLabel(bin, label)
    #   angle = 90
    #   align = 33
    #   # TAxis::ChangeLabel ( Int_t  labNum = 0, Double_t  labAngle = -1., Double_t  labSize = -1.,
    #   #                      Int_t  labAlign = -1, Int_t  labColor = -1, Int_t  labFont = -1, TString  labText = "" )
    #  histograms["OSDL_all_yields"][proc].GetXaxis().ChangeLabel(bin, angle, -1, align, -1, -1, label)

  stack_cat_summary = dict()
  stack_cat_summary_errors = dict()
  for group_name, group_list in group_nb_nj["category"].items():
    stack_cat_summary[group_name] = dict()
    stack_cat_summary_errors[group_name] = dict()
    for proc in category_summary[group_list[0]].keys():
      stack_cat_summary[group_name][proc] = sum([category_summary[category][proc] for category in group_list])
      stack_cat_summary_errors[group_name][proc] = math.sqrt(sum([category_summary_errors[category][proc]**2 for category in group_list]))
      #HAHAHAHAHA this has to be some of the worst code possible in terms of generalization. Whatever it takes...
      bin = int(group_name.split("_")[2][0]) - 3
      btag_bin = group_name.split("_")[1]
      if btag_bin == "2b":
        binoffset = 0
      elif btag_bin == "3b":
        binoffset = 5
      elif btag_bin == "4pb":
        binoffset = 10
      else:
        raise ValueError(btag_bin+" is an unexpected value for this ad-hoc script...")
      histograms["OSDL_"+btag_bin+"tags_yields"][proc].SetBinContent(bin, stack_cat_summary[group_name][proc])
      histograms["OSDL_"+btag_bin+"tags_yields"][proc].SetBinError(bin, stack_cat_summary_errors[group_name][proc])
      histograms["OSDL_all_yields"][proc].SetBinContent(bin+binoffset, stack_cat_summary[group_name][proc])
      histograms["OSDL_all_yields"][proc].SetBinError(bin+binoffset, stack_cat_summary_errors[group_name][proc])

  f = ROOT.TFile.Open(filename, "recreate")
  for directory, procs in histograms.items():
    f.mkdir(directory)
    td = getattr(f, directory)
    for proc, histo in procs.items():
      td.WriteObject(histo, proc)
  f.Close()
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
  f = ROOT.TFile.Open(filename, "recreate")
  f.mkdir("OSDL_postfit_s_sqrt_splusb")
  f.cd("OSDL_postfit_s_sqrt_splusb")

  # s = ROOT.THStack()
  # color_counter = 1

  for k, h in new_hists.items():
    h.Rebin(151)
    h.Write()
    # if "Total" not in k and "data_obs" not in k:
    #   h.SetFillColor(color_counter)
    #   h.Rebin(151)
    #   s.Add(h)
  f.Close()
  
  # c = ROOT.TCanvas()
  # s.Draw("HIST")
  # new_hists["data_obs"].Rebin(151)
  # new_hists["data_obs"].SetMarkerStyle(2)
  # new_hists["data_obs"].SetFillColor(0)
  # new_hists["data_obs"].SetLineColor(0)
  # new_hists["data_obs"].Draw("E2 SAME")

  # breakpoint()
  return new_hists


# f = ROOT.TFile.Open("April24_envelopedWithRate_RunII_HT_shapes_splusb.root", "read")
f = ROOT.TFile.Open("2022August21_Baseline_RunII_HT_shapes_splusb.root", "read")
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
        bin_labels.append(category+"_bin"+str(i_p))
        labelled = True
    category_summary[category][proc] = sum(all_bins[proc][-(hnb+1):])
    category_summary_errors[category][proc] = math.sqrt(sum([x**2 for x in all_bin_errors[proc][-(hnb+1):]]))
  all_cat_procs = all_cat_procs.union(these_cat_procs)
  #Backfill a proc array if it was missing in this iteration
  for proc in all_cat_procs - these_cat_procs:
    all_bins[proc] += backfill
    all_bin_errors[proc] += backfill
    category_summary[category][proc] = 0
    category_summary_errors[category][proc] = 0

y = make_yield_summary(category_summary, category_summary_errors, total_categories, "2022August21_Baseline_OSDL_postfit_yields.root")
x = make_s_sqrt_splusb_plots(all_bins, all_bin_errors, total_bins, "2022August21_Baseline_OSDL_s_over_sqrtsplusb.root")

f = ROOT.TFile.Open("junktest.root", "read")
c = ROOT.TCanvas()
h1 = f.OSDL_all_yields.ttbb
h1.SetFillColor(ROOT.kGreen)
h2 = f.OSDL_all_yields.tttt
h2.SetFillColor(ROOT.kBlue)
s = ROOT.THStack()
s.Add(h1, "ttbb")
s.Add(h2, "tttt")
s.Draw("HIST")
c.Draw()
c.SaveAs("junktest.pdf")
