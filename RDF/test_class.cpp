#ifndef FOURTOP_FUNCTIONS
#define FOURTOP_FUNCTIONS

//#include <boost>
#include <iostream>
#include <string>
#include <vector>
#include <TH2.h>
#include <TFile.h>
#include "ROOT/RVec.hxx"

typedef ROOT::VecOps::RVec<float>                        RVec_f;
typedef ROOT::VecOps::RVec<float>::const_iterator        RVec_f_iter;
typedef ROOT::VecOps::RVec<int>                          RVec_i;
typedef ROOT::VecOps::RVec<int>::const_iterator          RVec_i_iter;
typedef ROOT::VecOps::RVec<std::string>                  RVec_str;
typedef ROOT::VecOps::RVec<std::string>::const_iterator  RVec_str_iter;

class TH2Lookup {
public:

  TH2Lookup() {lookupMap_.clear();}
  TH2Lookup(std::string file, bool debug=false);
  TH2Lookup(std::string file, std::vector<std::string> histos);
  ~TH2Lookup() {}

  //void setJets(int nJet, int *jetHadronFlavour, float *jetPt, float *jetEta);

  float getLookup(std::string key, float x_val, float y_val);
  float getLookupErr(std::string key, float x_val, float y_val);
  RVec_f getJetEfficiencySimple(ROOT::VecOps::RVec<int>* jets_flav, ROOT::VecOps::RVec<float>* jets_pt, ROOT::VecOps::RVec<float>* jets_eta);
  RVec_f getJetEfficiency(std::string category, std::string tagger_WP, RVec_i* jets_flav, RVec_f* jets_pt, RVec_f* jets_eta);
  double getEventYieldRatio(std::string sample, std::string variation, int nJet, double HT, bool debug=false);
  //const std::vector<float> & run();

private:
  std::map<std::string, TH2*> lookupMap_;
  std::vector<std::string> validKeys_;
  bool declaredFailure_;
  // std::vector<float> ret_;
  // int nJet_;
  // float *Jet_eta_, *Jet_pt_;
  // int *Jet_flav_;
};

TH2Lookup::TH2Lookup(std::string file, bool debug=false) {
  lookupMap_.clear();
  validKeys_.clear();
  TFile *f = TFile::Open(file.c_str(),"read");
  if(!f) {
    std::cout << "WARNING! File " << file << " cannot be opened." << std::endl;
    declaredFailure_ = true;
  }
  for(const auto&& obj: *(f->GetListOfKeys())){
    std::string key = obj->GetName();
    std::string clone_key = "TH2LU_" + key;
    //for(int i=0; i<(int)histos.size();++i) {
    lookupMap_[obj->GetName()] = (TH2*)(f->Get(key.c_str())->Clone(clone_key.c_str()));
    //lookupMap_[obj->GetName()] = (TH2*)(f->Get((obj->GetName()).c_str()))->Clone(("TH2LU_"+obj->GetName()).c_str());
    lookupMap_[obj->GetName()]->SetDirectory(0);
    if(debug){std::cout << obj->GetName() << "     ";}
  }
  f->Close();
}

TH2Lookup::TH2Lookup(std::string file, std::vector<std::string> histos) {
  lookupMap_.clear();
  validKeys_.clear();
  TFile *f = TFile::Open(file.c_str(),"read");
  if(!f) {
    std::cout << "WARNING! File " << file << " cannot be opened. Skipping this efficiency" << std::endl;
  }

  for(int i=0; i<(int)histos.size();++i) {
    lookupMap_[histos[i]] = (TH2*)(f->Get(histos[i].c_str()))->Clone(("TH2LU_"+histos[i]).c_str());
    lookupMap_[histos[i]]->SetDirectory(0);
    if(!lookupMap_[histos[i]]) {
      std::cout << "ERROR! Histogram " << histos[i] << " not in file " << file << ". Not considering this lookup. " << std::endl;
    } else {
      validKeys_.push_back(histos[i]);
      std::cout << "Loading histogram " << histos[i] << " from file " << file << "... " << std::endl;
    }
  }
  f->Close();
}

/*void TH2Lookup::setJets(int nJet, int *jetFlav, float *lepPt, float *lepEta) {
  nJet_ = nJet; Jet_flav_ = jetFlav; Jet_pt_ = lepPt; Jet_eta_ = lepEta;
  }*/

float TH2Lookup::getLookup(std::string key, float x_val, float y_val) {
  if ( lookupMap_.find(key) == lookupMap_.end() ) {
    // not found ... not sure how intensive this lookup is, but we need to guard against bad keys
    double fail = -9999.9;
    return fail;
  } else {
    //found
    int binx = std::max(1, std::min(lookupMap_[key]->GetNbinsX(), lookupMap_[key]->GetXaxis()->FindBin(x_val)));
    int biny = std::max(1, std::min(lookupMap_[key]->GetNbinsY(), lookupMap_[key]->GetYaxis()->FindBin(y_val)));
    return lookupMap_[key]->GetBinContent(binx,biny);
  }
}

float TH2Lookup::getLookupErr(std::string key, float x_val, float y_val) {
  int binx = std::max(1, std::min(lookupMap_[key]->GetNbinsX(), lookupMap_[key]->GetXaxis()->FindBin(x_val)));
  int biny = std::max(1, std::min(lookupMap_[key]->GetNbinsY(), lookupMap_[key]->GetYaxis()->FindBin(y_val)));
  return lookupMap_[key]->GetBinError(binx,biny);
}

RVec_f TH2Lookup::getJetEfficiency(std::string category, std::string tagger_wp, RVec_i* jets_flav, RVec_f* jets_pt, RVec_f* jets_eta){
  //RVec_str keys;
  RVec_f eff;
  std::string key = "";
  
  //this only works with boost library...
  /*for(auto iter = boost::make_zip_iterator(std::make_tuple(jets_flav->cbegin(), jets_pt->cbegin(), jets_eta->cbegin())),
	iEnd = boost::make_zip_iterator(std::make_tuple(jets_flav->cend(), jets_pt->cend(), jets_eta->cend()));
      iter != iEnd; ++i){//do stuff}*/
  for(int i = 0; i < jets_flav->size(); ++i){
    if(jets_flav->at(i) == 5){
      key = category + "_bjets_" + tagger_wp;
    } else if(jets_flav->at(i) == 4){
      key = category + "_cjets_" + tagger_wp;
    } else {
      key = category + "_udsgjets_" + tagger_wp;
    }
    eff.push_back(getLookup(key, jets_pt->at(i), fabs(jets_eta->at(i))));
  }
  return eff;
}

double TH2Lookup::getEventYieldRatio(std::string sample, std::string variation, int nJet, double HT, bool debug=false){
  //Latest version uses keys of form "Aggregate__nom", so sample = "Aggregate_" and variation = "_nom"
  //For pseudo-1D lookups, this uses "<name>_1D<DIM>" such as "tttt_1DX" -> key = "tttt_1DY_nom" for example
  double yield = 1.0;
  std::string key = "";
  key = sample + variation;
  if(debug){std::cout << "getEventYield key: " << key << std::endl;}
  yield = getLookup(key, HT, nJet);
  return yield;
}

/*const std::vector<float> & TH2Lookup::run() {
  ret_.clear();
  for (int iJ = 0, nJ = nJet_; iL < nJ; ++iJ) {
    ret_.push_back(getEff((Jet_flav_)[iJ], (Jet_pt_)[iJ], (Jet_eta_)[iJ]));
  }
  return ret_;
  }*/

/*RVec_i generateIndex(RVec_i *v){
  RVec_i i(v->size());
  std::iota(i.begin(), i.end(), 0);
  return i;
  }*/

//namespace FourTop Analysis
namespace FTA{
  int packEventId(std::string dataset, std::string campaign, int genTtbarId = -1, int ttbarNGenJet = -1, double ttbarGenHT = -1, int otherPhaseSpaceID = -1){
    //Store integer key packing info about dataset (TTTo2L2Nu...), campaign (RunIIFall17NanoAODv6...), ttbar categorization, phase space, etc.
    // Reserve 1000 codes for dataset, 100 for campaign, 
    int retCode = 0;
    return retCode;
  }
  double unpackEventId(int packedEventId, double genWeight, double luminosity = -1, bool details = false){
    //return the event level XS weight accounting for luminosity, genWeight, sumWeights, etc. 
    //Use a default for luminosity based on the era determined by the campaign, perhaps...
    double retCode = 0;
    return retCode;
  }
  std::map<std::string, std::string> unpackEventIdMeta(int packedEventId, double genWeight, double luminosity = -1){
    //return the event level XS weight accounting for luminosity, genWeight, sumWeights, etc. 
    std::map<std::string, std::string> retCode;
    if(luminosity < 0){
      //code to get the luminosity lookup from the main function...
      retCode["luminosity"] = std::to_string(unpackEventId(packedEventId, genWeight, luminosity, true));
    } else {
      retCode["luminosity"] = "This is probably a bad idea, KISS my friend! Drop the lumi and genWeight";
    }
    return retCode;
  }
  double ElMu2017HLTSF(double lep1pt, double lep2pt){
    double sf = 1;
    if(lep1pt > 20 && lep2pt > 15){
      if(lep1pt < 40){
	if(lep2pt < 30){
	  sf = 0.948121;
	  return sf;
	}
	else { // > 30
	  sf = 0.958362; 
	  return sf;
	}
      }
      else if(lep1pt < 60){
	if(lep2pt < 30){
	  sf = 0.957376;
	  return sf;
	}
	else if(lep2pt < 45){
	  sf = 0.985497;
	  return sf;
	}
	else { // > 45, < 60
	  sf = 0.987867; 
	  return sf;
	}
      }
      else if(lep1pt < 80){
	if(lep2pt < 30){
	  sf = 0.981871;
	  return sf;
	}
	else if(lep2pt < 45){
	  sf = 0.989406;
	  return sf;
	}
	else if(lep2pt < 60){
	  sf = 0.993657;
	  return sf;
	}
	else { // > 60, < 80
	  sf = 0.992759; 
	  return sf;
	}
      }
      else if(lep1pt < 100){
	if(lep2pt < 30){
	  sf = 0.986281;
	  return sf;
	}
	else if(lep2pt < 45){
	  sf = 0.990969;
	  return sf;
	}
	else if(lep2pt < 60){
	  sf = 0.99191;
	  return sf;
	}
	else if(lep2pt < 80){
	  sf = 0.993743;
	  return sf;
	}
	else { // > 80, < 100
	  sf = 0.994792; 
	  return sf;
	}
      }
      else if(lep1pt < 150){
	if(lep2pt < 30){
	  sf = 0.972893;
	  return sf;
	}
	else if(lep2pt < 45){
	  sf = 0.98453;
	  return sf;
	}
	else if(lep2pt < 60){
	  sf = 0.992017;
	  return sf;
	}
	else if(lep2pt < 80){
	  sf = 0.994693;
	  return sf;
	}
	else if(lep2pt < 100){
	  sf = 0.995513;
	  return sf;
	}
	else { // > 100, < 150
	  sf = 0.995142; 
	  return sf;
	}
      }
      else { //lep1pt > 150
	if(lep2pt < 30){
	  sf = 0.986643;
	  return sf;
	}
	else if(lep2pt < 45){
	  sf = 0.977584;
	  return sf;
	}
	else if(lep2pt < 60){
	  sf = 0.986496;
	  return sf;
	}
	else if(lep2pt < 80){
	  sf = 0.988663;
	  return sf;
	}
	else if(lep2pt < 100){
	  sf = 0.990325;
	  return sf;
	}
	else if(lep2pt < 150){
	  sf = 0.996006;
	  return sf;
	}
	else { // > 150
	  sf = 0.996827; 
	  return sf;
	}
      }
    } else {
      std::cout << "HLT SF cannot be computed for lep1pt " << lep1pt << " and lep2pt " << lep2pt << std::endl;
      sf = -1000000000000;
      return sf;
    }
  }
  double btagEventWeight_count(double btag_threshold, RVec_f *jets_eff, RVec_f *jets_sf, RVec_f *jets_btag){
    double weight = 1.0;
    double prob_data = 1, prob_mc = 1;
    for(int i = 0; i < jets_eff->size(); ++i){
      if(jets_sf->at(i) >= btag_threshold){
	prob_mc *= jets_eff->at(i);
	prob_data *= jets_sf->at(i) * jets_eff->at(i);
      } else {
	prob_mc *= (1 - jets_eff->at(i));
	prob_data *= (1 - jets_sf->at(i) * jets_eff->at(i));
      }
    }
    weight = prob_data/prob_mc;
    return weight;
  }
  
  
  double btagEventWeight_shape(RVec_f jets_sf){
    //return the PRE-weight from shape variations, based on the product of all selected jets' SFs.
    //This needs to be multiplied with the event yield [sum(weights before)/sum(weights after)] after multiplying
    //this preweight with the rest of the event weight
    double weight = 1.0;
    for(int i = 0; i < jets_sf.size(); ++i){
      weight *= jets_sf.at(i);
    }
    return weight;
  }
  
  double btagEventWeight_shape(RVec_f jets_sf, RVec_i jets_mask){
    //return the PRE-weight from shape variations, based on the product of all selected jets' SFs.
    //This needs to be multiplied with the event yield [sum(weights before)/sum(weights after)] after multiplying
    //this preweight with the rest of the event weight
    RVec_f masked_jets_sf = jets_sf[jets_mask];
    double weight = 1.0;
    for(int i = 0; i < masked_jets_sf.size(); ++i){
      weight *= masked_jets_sf.at(i);
    }
    return weight;
  }
  
  RVec_i generateIndices(RVec_i v){
    RVec_i i(v.size());
    std::iota(i.begin(), i.end(), 0);
    return i;
  }
  
  RVec_i generateIndices(RVec_f v){
    RVec_i i(v.size());
    std::iota(i.begin(), i.end(), 0);
    return i;
  }
  
  RVec_f transverseMass(RVec_f pt1, RVec_f phi1, RVec_f m1, RVec_f pt2, RVec_f phi2, RVec_f m2){
    //This function only accepts vectors of equal size
    if(pt1.size() != pt2.size()){
      RVec_f v = {-9999.9};
      return v;
    }
    else {
      //RVec multiplication is element-by-element, i.e. {0, 1, 2}*{1, -3, 9.5} = {0, -3, 19}
      //auto MT2 = (*m1)*(*m1) + (*m2)*(*m2) + 2*(sqrt((*m1)*(*m1) + (*pt1)*(*pt1)) * sqrt((*m2)*(*m2) + (*pt2)*(*pt2)) - (*pt1)*(*pt2)*cos(ROOT::VecOps::DeltaPhi(*phi1, *phi2)));
      auto MT2 = (m1)*(m1) + (m2)*(m2) + 2*(sqrt((m1)*(m1) + (pt1)*(pt1)) * sqrt((m2)*(m2) + (pt2)*(pt2)) - (pt1)*(pt2)*cos(ROOT::VecOps::DeltaPhi(phi1, phi2)));
      return sqrt(MT2);
    }
  }

  RVec_f transverseMassMET(RVec_f pt1, RVec_f phi1, RVec_f m1, double pt2_uncast, double phi2_uncast){
    if(pt1.size() == 0){
      RVec_f v = {-9999.9};
      return v;
    }
    else {
      RVec_f pt2, phi2, m2;
      double m2_uncast = 0;
      //broadcast the double to RVec's
      for(int z = 0; z < pt1.size(); ++z){
	pt2.push_back(pt2_uncast);
	phi2.push_back(phi2_uncast);
	m2.push_back(m2_uncast);
      }
      //RVec multiplication is element-by-element, i.e. {0, 1, 2}*{1, -3, 9.5} = {0, -3, 19}
      //auto MT2 = (*m1)*(*m1) + (*m2)*(*m2) + 2*(sqrt((*m1)*(*m1) + (*pt1)*(*pt1)) * sqrt((*m2)*(*m2) + (*pt2)*(*pt2)) - (*pt1)*(*pt2)*cos(ROOT::VecOps::DeltaPhi(*phi1, *phi2)));
      auto MT2 = (m1)*(m1) + (m2)*(m2) + 2*(sqrt((m1)*(m1) + (pt1)*(pt1)) * sqrt((m2)*(m2) + (pt2)*(pt2)) - (pt1)*(pt2)*cos(ROOT::VecOps::DeltaPhi(phi1, phi2)));
      return sqrt(MT2);
    }
  }
  
  std::pair<double,double> METXYCorr(double uncormet, double uncormet_phi, int runnb, int year, bool isData, int npv){
    enum TheRunEra{y2016B,y2016C,y2016D,y2016E,y2016F,y2016G,y2016H,y2017B,y2017C,y2017D,y2017E,y2017F,y2018A,y2018B,y2018C,y2018D,y2016MC,y2017MC,y2018MC};
    bool isMC = !isData; //flip for convention used in FourTop analysis
    std::pair<double,double>  TheXYCorr_Met_MetPhi(uncormet,uncormet_phi);
    
    if(npv>100) npv=100;
    int runera =-1;
    bool usemetv2 =false;
    if(isMC && year == 2016) runera = y2016MC;
    else if(isMC && year == 2017) {runera = y2017MC; usemetv2 =true;}
    else if(isMC && year == 2018) runera = y2018MC;
    
    else if(!isMC && runnb >=272007 &&runnb<=275376  ) runera = y2016B;
    else if(!isMC && runnb >=275657 &&runnb<=276283  ) runera = y2016C;
    else if(!isMC && runnb >=276315 &&runnb<=276811  ) runera = y2016D;
    else if(!isMC && runnb >=276831 &&runnb<=277420  ) runera = y2016E;
    else if(!isMC && runnb >=277772 &&runnb<=278808  ) runera = y2016F;
    else if(!isMC && runnb >=278820 &&runnb<=280385  ) runera = y2016G;
    else if(!isMC && runnb >=280919 &&runnb<=284044  ) runera = y2016H;
    
    else if(!isMC && runnb >=297020 &&runnb<=299329 ){ runera = y2017B; usemetv2 =true;}
    else if(!isMC && runnb >=299337 &&runnb<=302029 ){ runera = y2017C; usemetv2 =true;}
    else if(!isMC && runnb >=302030 &&runnb<=303434 ){ runera = y2017D; usemetv2 =true;}
    else if(!isMC && runnb >=303435 &&runnb<=304826 ){ runera = y2017E; usemetv2 =true;}
    else if(!isMC && runnb >=304911 &&runnb<=306462 ){ runera = y2017F; usemetv2 =true;}
    
    else if(!isMC && runnb >=315252 &&runnb<=316995 ) runera = y2018A;
    else if(!isMC && runnb >=316998 &&runnb<=319312 ) runera = y2018B;
    else if(!isMC && runnb >=319313 &&runnb<=320393 ) runera = y2018C;
    else if(!isMC && runnb >=320394 &&runnb<=325273 ) runera = y2018D;
    
    else {
      //Couldn't find data/MC era => no correction applied
      return TheXYCorr_Met_MetPhi;
    }
    
    double METxcorr(0.),METycorr(0.);
    
    if(!usemetv2){//Current recommendation for 2016 and 2018
      if(runera==y2016B) METxcorr = -(-0.0478335*npv -0.108032);
      if(runera==y2016B) METycorr = -(0.125148*npv +0.355672);
      if(runera==y2016C) METxcorr = -(-0.0916985*npv +0.393247);
      if(runera==y2016C) METycorr = -(0.151445*npv +0.114491);
      if(runera==y2016D) METxcorr = -(-0.0581169*npv +0.567316);
      if(runera==y2016D) METycorr = -(0.147549*npv +0.403088);
      if(runera==y2016E) METxcorr = -(-0.065622*npv +0.536856);
      if(runera==y2016E) METycorr = -(0.188532*npv +0.495346);
      if(runera==y2016F) METxcorr = -(-0.0313322*npv +0.39866);
      if(runera==y2016F) METycorr = -(0.16081*npv +0.960177);
      if(runera==y2016G) METxcorr = -(0.040803*npv -0.290384);
      if(runera==y2016G) METycorr = -(0.0961935*npv +0.666096);
      if(runera==y2016H) METxcorr = -(0.0330868*npv -0.209534);
      if(runera==y2016H) METycorr = -(0.141513*npv +0.816732);
      if(runera==y2017B) METxcorr = -(-0.259456*npv +1.95372);
      if(runera==y2017B) METycorr = -(0.353928*npv -2.46685);
      if(runera==y2017C) METxcorr = -(-0.232763*npv +1.08318);
      if(runera==y2017C) METycorr = -(0.257719*npv -1.1745);
      if(runera==y2017D) METxcorr = -(-0.238067*npv +1.80541);
      if(runera==y2017D) METycorr = -(0.235989*npv -1.44354);
      if(runera==y2017E) METxcorr = -(-0.212352*npv +1.851);
      if(runera==y2017E) METycorr = -(0.157759*npv -0.478139);
      if(runera==y2017F) METxcorr = -(-0.232733*npv +2.24134);
      if(runera==y2017F) METycorr = -(0.213341*npv +0.684588);
      if(runera==y2018A) METxcorr = -(0.362865*npv -1.94505);
      if(runera==y2018A) METycorr = -(0.0709085*npv -0.307365);
      if(runera==y2018B) METxcorr = -(0.492083*npv -2.93552);
      if(runera==y2018B) METycorr = -(0.17874*npv -0.786844);
      if(runera==y2018C) METxcorr = -(0.521349*npv -1.44544);
      if(runera==y2018C) METycorr = -(0.118956*npv -1.96434);
      if(runera==y2018D) METxcorr = -(0.531151*npv -1.37568);
      if(runera==y2018D) METycorr = -(0.0884639*npv -1.57089);
      if(runera==y2016MC) METxcorr = -(-0.195191*npv -0.170948);
      if(runera==y2016MC) METycorr = -(-0.0311891*npv +0.787627);
      if(runera==y2017MC) METxcorr = -(-0.217714*npv +0.493361);
      if(runera==y2017MC) METycorr = -(0.177058*npv -0.336648);
      if(runera==y2018MC) METxcorr = -(0.296713*npv -0.141506);
      if(runera==y2018MC) METycorr = -(0.115685*npv +0.0128193);
    }
    else {//these are the corrections for v2 MET recipe (currently recommended for 2017)
      if(runera==y2016B) METxcorr = -(-0.0374977*npv +0.00488262);
      if(runera==y2016B) METycorr = -(0.107373*npv +-0.00732239);
      if(runera==y2016C) METxcorr = -(-0.0832562*npv +0.550742);
      if(runera==y2016C) METycorr = -(0.142469*npv +-0.153718);
      if(runera==y2016D) METxcorr = -(-0.0400931*npv +0.753734);
      if(runera==y2016D) METycorr = -(0.127154*npv +0.0175228);
      if(runera==y2016E) METxcorr = -(-0.0409231*npv +0.755128);
      if(runera==y2016E) METycorr = -(0.168407*npv +0.126755);
      if(runera==y2016F) METxcorr = -(-0.0161259*npv +0.516919);
      if(runera==y2016F) METycorr = -(0.141176*npv +0.544062);
      if(runera==y2016G) METxcorr = -(0.0583851*npv +-0.0987447);
      if(runera==y2016G) METycorr = -(0.0641427*npv +0.319112);
      if(runera==y2016H) METxcorr = -(0.0706267*npv +-0.13118);
      if(runera==y2016H) METycorr = -(0.127481*npv +0.370786);
      if(runera==y2017B) METxcorr = -(-0.19563*npv +1.51859);
      if(runera==y2017B) METycorr = -(0.306987*npv +-1.84713);
      if(runera==y2017C) METxcorr = -(-0.161661*npv +0.589933);
      if(runera==y2017C) METycorr = -(0.233569*npv +-0.995546);
      if(runera==y2017D) METxcorr = -(-0.180911*npv +1.23553);
      if(runera==y2017D) METycorr = -(0.240155*npv +-1.27449);
      if(runera==y2017E) METxcorr = -(-0.149494*npv +0.901305);
      if(runera==y2017E) METycorr = -(0.178212*npv +-0.535537);
      if(runera==y2017F) METxcorr = -(-0.165154*npv +1.02018);
      if(runera==y2017F) METycorr = -(0.253794*npv +0.75776);
      if(runera==y2018A) METxcorr = -(0.362642*npv +-1.55094);
      if(runera==y2018A) METycorr = -(0.0737842*npv +-0.677209);
      if(runera==y2018B) METxcorr = -(0.485614*npv +-2.45706);
      if(runera==y2018B) METycorr = -(0.181619*npv +-1.00636);
      if(runera==y2018C) METxcorr = -(0.503638*npv +-1.01281);
      if(runera==y2018C) METycorr = -(0.147811*npv +-1.48941);
      if(runera==y2018D) METxcorr = -(0.520265*npv +-1.20322);
      if(runera==y2018D) METycorr = -(0.143919*npv +-0.979328);
      if(runera==y2016MC) METxcorr = -(-0.159469*npv +-0.407022);
      if(runera==y2016MC) METycorr = -(-0.0405812*npv +0.570415);
      if(runera==y2017MC) METxcorr = -(-0.182569*npv +0.276542);
      if(runera==y2017MC) METycorr = -(0.155652*npv +-0.417633);
      if(runera==y2018MC) METxcorr = -(0.299448*npv +-0.13866);
      if(runera==y2018MC) METycorr = -(0.118785*npv +0.0889588);
    }
    
    double CorrectedMET_x = uncormet *cos( uncormet_phi)+METxcorr;
    double CorrectedMET_y = uncormet *sin( uncormet_phi)+METycorr;
    
    double CorrectedMET = sqrt(CorrectedMET_x*CorrectedMET_x+CorrectedMET_y*CorrectedMET_y);
    double CorrectedMETPhi;
    if(CorrectedMET_x==0 && CorrectedMET_y>0) CorrectedMETPhi = TMath::Pi();
    else if(CorrectedMET_x==0 && CorrectedMET_y<0 )CorrectedMETPhi = -TMath::Pi();
    else if(CorrectedMET_x >0) CorrectedMETPhi = TMath::ATan(CorrectedMET_y/CorrectedMET_x);
    else if(CorrectedMET_x <0&& CorrectedMET_y>0) CorrectedMETPhi = TMath::ATan(CorrectedMET_y/CorrectedMET_x) + TMath::Pi();
    else if(CorrectedMET_x <0&& CorrectedMET_y<0) CorrectedMETPhi = TMath::ATan(CorrectedMET_y/CorrectedMET_x) - TMath::Pi();
    else CorrectedMETPhi =0;
    
    TheXYCorr_Met_MetPhi.first= CorrectedMET;
    TheXYCorr_Met_MetPhi.second= CorrectedMETPhi;
    //std::cout << "runera " << runera << " pt shift: " << (CorrectedMET - uncormet) << " phi shift: " << (CorrectedMETPhi - uncormet_phi) << std::endl;
    return TheXYCorr_Met_MetPhi;
    
  }
}
#endif
