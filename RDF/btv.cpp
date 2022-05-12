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
    jes_names.push_back("up_jes");
    jes_names.push_back("down_jes");
  }
  if(jes_reduced){
    jes_names.push_back("up_jesBBEC1");
    jes_names.push_back("up_jesEC2");
    jes_names.push_back("up_jesHF");
    jes_names.push_back("up_jesRelativeBal");
    jes_names.push_back("up_jesFlavorQCD");
    jes_names.push_back("up_jesAbsolute");
    jes_names.push_back("down_jesBBEC1");
    jes_names.push_back("down_jesEC2");
    jes_names.push_back("down_jesHF");
    jes_names.push_back("down_jesRelativeBal");
    jes_names.push_back("down_jesFlavorQCD");
    jes_names.push_back("down_jesAbsolute");
    if(era == "2017"){
      jes_names.push_back("up_jesBBEC1_2017");
      jes_names.push_back("up_jesEC2_2017");
      jes_names.push_back("up_jesHF_2017");
      jes_names.push_back("up_jesRelativeSample_2017");
      jes_names.push_back("up_jesAbsolute_2017");
      jes_names.push_back("down_jesBBEC1_2017");
      jes_names.push_back("down_jesEC2_2017");
      jes_names.push_back("down_jesHF_2017");
      jes_names.push_back("down_jesRelativeSample_2017");
      jes_names.push_back("down_jesAbsolute_2017");
    }
    else if(era == "2018"){
      jes_names.push_back("up_jesHEMIssue");
      jes_names.push_back("up_jesBBEC1_2018");
      jes_names.push_back("up_jesEC2_2018");
      jes_names.push_back("up_jesHF_2018");
      jes_names.push_back("up_jesRelativeSample_2018");
      jes_names.push_back("up_jesAbsolute_2018");
      jes_names.push_back("down_jesHEMIssue");
      jes_names.push_back("down_jesBBEC1_2018");
      jes_names.push_back("down_jesEC2_2018");
      jes_names.push_back("down_jesHF_2018");
      jes_names.push_back("down_jesRelativeSample_2018");
      jes_names.push_back("down_jesAbsolute_2018");
    }
    else
      throw std::invalid_argument("received not implemented era:" + era);
  }
  return jes_names;
}

std::vector<std::string> relevant_shape_syst_names(std::string era, 
						   bool jes_total = false, 
						   bool jes_reduced = false, 
						   bool jes_complete = false){

  std::vector<std::string> syst_names = {"central", //all uncertainties
					 "up_lf", "down_lf", "up_hfstats1", "down_hfstats1", "up_hfstats2", "down_hfstats2", //hf uncertainties
					 "up_hf", "down_hf", "up_lfstats1", "down_lfstats1", "up_lfstats2", "down_lfstats2", //lf uncertainties
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
    std::vector<std::string> relev_main = {"central", "up_lf", "down_lf", "up_hfstats1", "down_hfstats1","up_hfstats2", "down_hfstats2"};
    if(std::find(std::begin(relev_main), std::end(relev_main), syst) != std::end(relev_main))
      return syst;
    if(std::find(std::begin(relev_jes), std::end(relev_jes), syst) != std::end(relev_jes))
      return syst;
    else
      return "central";
  }    
  else{
    std::vector<std::string> relev_main = {"central", "up_hf", "down_hf", "up_lfstats1", "down_lfstats1", "up_lfstats2", "down_lfstats2"};
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
			       std::string input_collection = "Jet",
			       std::string flav_name = "hadronFlavour", 
			       std::string eta_name = "eta", 
			       std::string pt_name = "pt",
			       std::string disc_name = "btagDeepFlavB",
			       bool jes_total = false, 
			       bool jes_reduced = false, 
			       bool jes_complete = false, 
			       bool verbose=false){
    auto rdf = df;
    if(jes_complete)
      throw std::invalid_argument("jes_complete not implemented");
    if(wp == "shape_corr"){
      //everything hardcoded for deepjet...
      std::string base_branch_name = input_collection + "_btagSF_deepjet_shape";
      std::vector<std::string> relev_systs = relevant_shape_syst_names(era, jes_total, jes_reduced);
      std::vector<std::string> relev_jes = relevant_jes_names(era, jes_total, jes_reduced, jes_total);
      std::vector<std::string> columns = {input_collection + "_" + flav_name, 
					  input_collection + "_" + eta_name, 
					  input_collection + "_" + pt_name, 
					  input_collection + "_" + disc_name};
      //if self.algo == "csvv2":
      //   discr = "btagCSVV2"
      //elif self.algo == "deepcsv":
      //   discr = "btagDeepB"
      //elif self.algo == "cmva":
      //   discr = "btagCMVA"
      //elif self.algo == "deepjet":
      //   discr = "btagDeepFlavB"
      auto cSet = correction::CorrectionSet::from_file(corrector_file);
      auto cMap = cSet->at("deepJet_shape_" + era);
      for (auto &syst : relev_systs){
	auto lambdaShape =  [cMap,relev_jes, syst](ROOT::VecOps::RVec<int> hadronFlavour, 
						   ROOT::VecOps::RVec<float> eta,
						   ROOT::VecOps::RVec<float> pt,
						   ROOT::VecOps::RVec<float> disc){
	  ROOT::VecOps::RVec<double> sf = {};
	  for(int i = 0; i < hadronFlavour.size(); ++i){
	    std::vector<std::variant<int,double,std::string>> inputs = {};
	    inputs.push_back(relevant_syst_for_shape_corr(hadronFlavour.at(i), syst, relev_jes));
	    inputs.push_back(hadronFlavour.at(i));
	    inputs.push_back(std::clamp(abs(static_cast<double>(eta.at(i))), 0., 2.5-0.000001));
	    inputs.push_back(std::clamp(static_cast<double>(pt.at(i)), 20.0001, 9999.999));
	    inputs.push_back(disc.at(i));
	    // double uncertainty on out-of-bounds and return <-- if the pt is less than or greater than the bounds, clamp inside with +- 0.0001 and then double the uncertainty like so
	    // double sf_err = otherSysTypeReaders_.at(syst_final)->eval(jf, eta, pt_for_eval, discr);
	    // if (!is_out_of_bounds) {
	    //   return sf_err;
	    // }
	    // sf_err = sf + 2*(sf_err - sf);
	    // return sf_err;
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
	    sf.push_back(val);
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
