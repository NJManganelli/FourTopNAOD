#ifndef BTV_CORRLIB
#define BTV_CORRLIB

//#include <boost>
#include <cstring>
#include <stdio.h>
#include <iostream>
#include <stdexcept>
#include <string>
#include <variant>
#include <vector>
#include <TObject.h>
// #include <TH.h>
#include <TMath.h>
#include <TUUID.h>
#include "ROOT/RDF/RInterface.hxx"
#include "ROOT/RVec.hxx"
#include "correction.h"

typedef ROOT::VecOps::RVec<Float_t>                        RVec_f;
typedef ROOT::VecOps::RVec<Float_t>::const_iterator        RVec_f_iter;
typedef ROOT::VecOps::RVec<Int_t>                          RVec_i;
typedef ROOT::VecOps::RVec<Int_t>::const_iterator          RVec_i_iter;
typedef ROOT::VecOps::RVec<std::string>                    RVec_str;
typedef ROOT::VecOps::RVec<std::string>::const_iterator    RVec_str_iter;


std::vector<std::string> relevant_jes_names(std::string era, bool jes_total, bool jes_reduced, bool jes_complete){
  std::vector<std::string> jes_names = {};
  if(jes_total){
    jes_names.emplace_back("up_jes");
    jes_names.emplace_back("down_jes");
  }
  if(jes_reduced){
    jes_names.emplace_back("up_jesBBEC1");
    jes_names.emplace_back("up_jesEC2");
    jes_names.emplace_back("up_jesHF");
    jes_names.emplace_back("up_jesRelativeBal");
    jes_names.emplace_back("up_jesFlavorQCD");
    jes_names.emplace_back("up_jesAbsolute");
    jes_names.emplace_back("down_jesBBEC1");
    jes_names.emplace_back("down_jesEC2");
    jes_names.emplace_back("down_jesHF");
    jes_names.emplace_back("down_jesRelativeBal");
    jes_names.emplace_back("down_jesFlavorQCD");
    jes_names.emplace_back("down_jesAbsolute");
    if(era == "2016"){
      jes_names.emplace_back("up_jesBBEC1_2016");
      jes_names.emplace_back("up_jesEC2_2016");
      jes_names.emplace_back("up_jesHF_2016");
      jes_names.emplace_back("up_jesRelativeSample_2016");
      jes_names.emplace_back("up_jesAbsolute_2016");
      jes_names.emplace_back("down_jesBBEC1_2016");
      jes_names.emplace_back("down_jesEC2_2016");
      jes_names.emplace_back("down_jesHF_2016");
      jes_names.emplace_back("down_jesRelativeSample_2016");
      jes_names.emplace_back("down_jesAbsolute_2016");
    }
    else if(era == "2017"){
      jes_names.emplace_back("up_jesBBEC1_2017");
      jes_names.emplace_back("up_jesEC2_2017");
      jes_names.emplace_back("up_jesHF_2017");
      jes_names.emplace_back("up_jesRelativeSample_2017");
      jes_names.emplace_back("up_jesAbsolute_2017");
      jes_names.emplace_back("down_jesBBEC1_2017");
      jes_names.emplace_back("down_jesEC2_2017");
      jes_names.emplace_back("down_jesHF_2017");
      jes_names.emplace_back("down_jesRelativeSample_2017");
      jes_names.emplace_back("down_jesAbsolute_2017");
    }
    else if(era == "2018"){
      jes_names.emplace_back("up_jesHEMIssue");
      jes_names.emplace_back("up_jesBBEC1_2018");
      jes_names.emplace_back("up_jesEC2_2018");
      jes_names.emplace_back("up_jesHF_2018");
      jes_names.emplace_back("up_jesRelativeSample_2018");
      jes_names.emplace_back("up_jesAbsolute_2018");
      jes_names.emplace_back("down_jesHEMIssue");
      jes_names.emplace_back("down_jesBBEC1_2018");
      jes_names.emplace_back("down_jesEC2_2018");
      jes_names.emplace_back("down_jesHF_2018");
      jes_names.emplace_back("down_jesRelativeSample_2018");
      jes_names.emplace_back("down_jesAbsolute_2018");
    }
    else
      throw std::invalid_argument("received not implemented era:" + era);
  }
  if(jes_complete){
      jes_names.emplace_back("up_jesAbsoluteScale");
      jes_names.emplace_back("up_jesAbsoluteMPFBias");
      jes_names.emplace_back("up_jesAbsoluteStat");
      jes_names.emplace_back("up_jesFlavorQCD");
      jes_names.emplace_back("up_jesFragmentation");
      jes_names.emplace_back("up_jesPileUpDataMC");
      jes_names.emplace_back("up_jesPileUpPtBB");
      jes_names.emplace_back("up_jesPileUpPtEC1");
      jes_names.emplace_back("up_jesPileUpPtEC2");
      jes_names.emplace_back("up_jesPileUpPtHF");
      jes_names.emplace_back("up_jesPileUpPtRef");
      jes_names.emplace_back("up_jesSinglePionECAL");
      jes_names.emplace_back("up_jesSinglePionHCAL");
      jes_names.emplace_back("up_jesTimePtEta");
      jes_names.emplace_back("up_jesRelativeBal");
      jes_names.emplace_back("up_jesRelativeFSR");
      jes_names.emplace_back("up_jesRelativeJERHF");
      jes_names.emplace_back("up_jesRelativeJEREC1");
      jes_names.emplace_back("up_jesRelativeJEREC2");
      jes_names.emplace_back("up_jesRelativePtBB");
      jes_names.emplace_back("up_jesRelativePtEC1");
      jes_names.emplace_back("up_jesRelativePtEC2");
      jes_names.emplace_back("up_jesRelativePtHF");
      jes_names.emplace_back("up_jesRelativeStatEC");
      jes_names.emplace_back("up_jesRelativeStatFSR");
      jes_names.emplace_back("up_jesRelativeStatHF");

      jes_names.emplace_back("down_jesAbsoluteScale");
      jes_names.emplace_back("down_jesAbsoluteMPFBias");
      jes_names.emplace_back("down_jesAbsoluteStat");
      jes_names.emplace_back("down_jesFlavorQCD");
      jes_names.emplace_back("down_jesFragmentation");
      jes_names.emplace_back("down_jesPileUpDataMC");
      jes_names.emplace_back("down_jesPileUpPtBB");
      jes_names.emplace_back("down_jesPileUpPtEC1");
      jes_names.emplace_back("down_jesPileUpPtEC2");
      jes_names.emplace_back("down_jesPileUpPtHF");
      jes_names.emplace_back("down_jesPileUpPtRef");
      jes_names.emplace_back("down_jesSinglePionECAL");
      jes_names.emplace_back("down_jesSinglePionHCAL");
      jes_names.emplace_back("down_jesTimePtEta");
      jes_names.emplace_back("down_jesRelativeBal");
      jes_names.emplace_back("down_jesRelativeFSR");
      jes_names.emplace_back("down_jesRelativeJERHF");
      jes_names.emplace_back("down_jesRelativeJEREC1");
      jes_names.emplace_back("down_jesRelativeJEREC2");
      jes_names.emplace_back("down_jesRelativePtBB");
      jes_names.emplace_back("down_jesRelativePtEC1");
      jes_names.emplace_back("down_jesRelativePtEC2");
      jes_names.emplace_back("down_jesRelativePtHF");
      jes_names.emplace_back("down_jesRelativeStatEC");
      jes_names.emplace_back("down_jesRelativeStatFSR");
      jes_names.emplace_back("down_jesRelativeStatHF");
  }
  return jes_names;
}

std::vector<std::string> relevant_shape_syst_names(std::string era, 
						   bool jes_total, 
						   bool jes_reduced, 
						   bool jes_complete){

  std::vector<std::string> syst_names = {"central", //all uncertainties
					 "up_lf", "down_lf", "up_hfstats1", "down_hfstats1", "up_hfstats2", "down_hfstats2", //hf uncertainties? except the twiki says otherwise
					 "up_hf", "down_hf", "up_lfstats1", "down_lfstats1", "up_lfstats2", "down_lfstats2", //lf uncertainties? except the twiki says otherwise!?
					 "up_cferr1", "down_cferr1", "up_cferr2", "down_cferr2"}; //cf unertainties
  std::vector<std::string> add_syst_names = relevant_jes_names(era, jes_total, jes_reduced, jes_complete);
  syst_names.insert(syst_names.end(), add_syst_names.begin(), add_syst_names.end());
  return syst_names;
}

std::string relevant_syst_for_shape_corr(Int_t hadron_flav, std::string syst, std::vector<std::string> relev_jes){
  if(hadron_flav == 4){
    std::vector<std::string> relev_main = {"central", "up_cferr1", "down_cferr1", "up_cferr2", "down_cferr2"};
    if(std::find(std::begin(relev_main), std::end(relev_main), syst) != std::end(relev_main))
      return syst;
    else
      return "central";
  }
  else if(hadron_flav == 5){
    // this seems to be wrong? the SFs should be applied to both b and light flavors, except the cferr uncertainties only on c jets... TWIKI'S....
    // std::vector<std::string> relev_main = {"central", "up_lf", "down_lf", "up_hfstats1", "down_hfstats1","up_hfstats2", "down_hfstats2"};
    std::vector<std::string> relev_main = {"central", "up_hf", "down_hf", "up_lf", "down_lf", 
					   "up_hfstats1", "down_hfstats1","up_hfstats2", "down_hfstats2",
					   "up_lfstats1", "down_lfstats1", "up_lfstats2", "down_lfstats2"};
    if(std::find(std::begin(relev_main), std::end(relev_main), syst) != std::end(relev_main))
      return syst;
    if(std::find(std::begin(relev_jes), std::end(relev_jes), syst) != std::end(relev_jes))
      return syst;
    else
      return "central";
  }    
  else{
    // std::vector<std::string> relev_main = {"central", "up_hf", "down_hf", "up_lfstats1", "down_lfstats1", "up_lfstats2", "down_lfstats2"};
    std::vector<std::string> relev_main = {"central", "up_hf", "down_hf", "up_lf", "down_lf", 
					   "up_hfstats1", "down_hfstats1","up_hfstats2", "down_hfstats2",
					   "up_lfstats1", "down_lfstats1", "up_lfstats2", "down_lfstats2"};
    if(std::find(std::begin(relev_main), std::end(relev_main), syst) != std::end(relev_main))
      return syst;
    if(std::find(std::begin(relev_jes), std::end(relev_jes), syst) != std::end(relev_jes))
      return syst;
    else
      return "central";
  }
}
//std::string legacy, std::string VFP="", 
ROOT::RDF::RNode apply_btv_sfs(ROOT::RDF::RNode df, 
			       std::string wp, 
			       std::string era, 
			       std::string corrector_file,
			       std::string algo,
			       std::string input_collection = "Jet",
			       // std::string flav_name = "hadronFlavour", 
			       // std::string eta_name = "eta", 
			       // std::string pt_name = "pt",
			       // std::string disc_name = "btagDeepFlavB",
			       bool jes_total = false, 
			       bool jes_reduced = false, 
			       bool jes_complete = false, 
			       bool verbose=false){
  auto rdf = df;  

  std::string flav_name = "hadronFlavour";
  std::string eta_name = "eta";
  std::string pt_name = "pt";
  std::string disc_name;
  if(algo == "deepcsv")
    disc_name = "btagDeepB";
  else if(algo == "deepjet")
    disc_name = "btagDeepFlavB";
  double eta_max = -9000.0;
  if(era == "2017" || era == "2018")
    eta_max = 2.5;
  else if(era == "2016")
    eta_max = 2.4;

  if(wp == "shape_corr"){
    std::string base_branch_name = input_collection + "_btagSF_" + algo + "_shape";
    std::vector<std::string> relev_systs = relevant_shape_syst_names(era, jes_total, jes_reduced, jes_complete);
    std::vector<std::string> relev_jes = relevant_jes_names(era, jes_total, jes_reduced, jes_complete);
    std::vector<std::string> columns = {input_collection + "_" + flav_name, 
					input_collection + "_" + eta_name, 
					input_collection + "_" + pt_name, 
					input_collection + "_" + disc_name};
    auto cSet = correction::CorrectionSet::from_file(corrector_file);
    std::string cMapName;
    if(algo == "deepcsv")      
      cMapName = "deepCSV_shape";
    else if(algo == "deepjet")
      cMapName = "deepJet_shape";
    else
      throw std::invalid_argument("something happened, somewhere, sometime");  
    auto cMap = cSet->at(cMapName);
    for (auto &syst : relev_systs){
      std::map<int, std::string> fast_relevant_syst_for_shape_corr;
      for(int i_flav = 0; i_flav < 6; i_flav++){
	fast_relevant_syst_for_shape_corr[i_flav] = relevant_syst_for_shape_corr(i_flav, syst, relev_jes);
      }
      auto lambdaShape =  [cMap, fast_relevant_syst_for_shape_corr, syst, eta_max](ROOT::VecOps::RVec<int> hadronFlavour, 
										   ROOT::VecOps::RVec<float> eta,
										   ROOT::VecOps::RVec<float> pt,
										   ROOT::VecOps::RVec<float> disc){
	ROOT::VecOps::RVec<double> sf = {};
	for(int i = 0; i < hadronFlavour.size(); ++i){
	  std::vector<std::variant<int,double,std::string>> inputs = {};
	  inputs.emplace_back(fast_relevant_syst_for_shape_corr.at(hadronFlavour.at(i)));
	  inputs.emplace_back(hadronFlavour.at(i));
	  inputs.emplace_back(std::clamp(abs(static_cast<double>(eta.at(i))), 0., eta_max-0.001)); //copy nanoAOD-tools clamping, but give it the proper eta max... eps=1.e-3
	  inputs.emplace_back(std::clamp(static_cast<double>(pt.at(i)), 20.0001, 9999.9999)); //need to parse the corrector to get the true pt bounds...eps=1.e-4
	  inputs.emplace_back(disc.at(i));
	  auto val = cMap->evaluate(inputs);
	  //hardcoded junk for validating where these differences really are
	  if( syst != "central"){
	    //out of bounds calculations: clamp the pt to the min/max and double the errors if it's not a central value
	    if(pt.at(i) <= 20.0 || pt.at(i) > 10000.0){
	      auto cent_inputs = inputs;
	      //now get the central value to finish computation, 
	      cent_inputs[0] = "central";
	      auto cent = cMap->evaluate(cent_inputs);
	      val = cent + 2*(val - cent);
	    }
	  }
	  //https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/btv/btagSFProducer.py#L347
	  if(val < 0.01)
	    val = 1;
	  sf.emplace_back(val);
	}
	return sf;
      };
      std::string branch_name = base_branch_name;
      if(syst != "central")
	branch_name += "_" + syst;
      try{
	rdf = rdf.Define(branch_name, lambdaShape, columns);
      } catch(const std::exception & e){
	try{
	  rdf = rdf.Redefine(branch_name, lambdaShape, columns);
	}
	catch(const std::exception & ee){
	  std::cout << "Caught exception \"" << ee.what() << "\"\n";
	} //end catch ee
      } //end catch e
    } //end systematics loop
  }//end wp == "shape_corr"
  else
    throw std::invalid_argument("fixed wp not implemented");  
  return rdf;
}
#endif
