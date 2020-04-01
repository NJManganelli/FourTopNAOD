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
  TH2Lookup(std::string file, std::vector<std::string> histos);
  ~TH2Lookup() {}

  //void setJets(int nJet, int *jetHadronFlavour, float *jetPt, float *jetEta);

  float getLookup(std::string key, float x_val, float y_val);
  float getLookupErr(std::string key, float x_val, float y_val);
  RVec_f getJetEfficiencySimple(ROOT::VecOps::RVec<int>* jets_flav, ROOT::VecOps::RVec<float>* jets_pt, ROOT::VecOps::RVec<float>* jets_eta);
  RVec_f getJetEfficiency(std::string category, std::string tagger_WP, RVec_i* jets_flav, RVec_f* jets_pt, RVec_f* jets_eta);
  RVec_f getEventYield(std::string sample, std::string category, std::string variation);
  //const std::vector<float> & run();

private:
  std::map<std::string, TH2*> lookupMap_;
  std::vector<std::string> validKeys_;
  std::vector<float> ret_;
  int nJet_;
  float *Jet_eta_, *Jet_pt_;
  int *Jet_flav_;
};

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
  int binx = std::max(1, std::min(lookupMap_[key]->GetNbinsX(), lookupMap_[key]->GetXaxis()->FindBin(x_val)));
  int biny = std::max(1, std::min(lookupMap_[key]->GetNbinsY(), lookupMap_[key]->GetYaxis()->FindBin(y_val)));
  return lookupMap_[key]->GetBinContent(binx,biny);
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

RVec_f TH2Lookup::getEventYield(std::string sample, std::string category, std::string variation){
  //RVec_str keys;
  RVec_f yield = {1.0};
  std::string key = "";

//   for(int i = 0; i < jets_flav->size(); ++i){
//     if(jets_flav->at(i) == 5){
//       key = category + "_bjets_" + tagger_wp;
//     } else if(jets_flav->at(i) == 4){
//       key = category + "_cjets_" + tagger_wp;
//     } else {
//       key = category + "_udsgjets_" + tagger_wp;
//     }
//     eff.push_back(getLookup(key, jets_pt->at(i), fabs(jets_eta->at(i))));
//   }
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

RVec_f btagEventWeight_count(double btag_threshold, RVec_f *jets_eff, RVec_f *jets_sf, RVec_f *jets_btag){
  RVec_f weight = {1.0};
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
  weight[0] = prob_data/prob_mc;
  return weight;
}

RVec_f btagEventWeight_shape(RVec_f *jets_sf){
  //return the PRE-weight from shape variations, based on the product of all selected jets' SFs.
  //This needs to be multiplied with the event yield [sum(weights before)/sum(weights after)] after multiplying 
  //this preweight with the rest of the event weight
  RVec_f weight = {1.0};
  double unwrapped = 1.0;
  for(int i = 0; i < jets_sf->size(); ++i){
    unwrapped *= jets_sf->at(i);
  }
  weight[0] = unwrapped;
  return weight;
}

RVec_i generateIndices(RVec_i *v){
  RVec_i i(v->size());
  std::iota(i.begin(), i.end(), 0);
  return i;
}

RVec_i generateIndices(RVec_f *v){
  RVec_i i(v->size());
  std::iota(i.begin(), i.end(), 0);
  return i;
}

RVec_f transverseMass(RVec_f *pt1, RVec_f *phi1, RVec_f *m1, RVec_f *pt2, RVec_f *phi2, RVec_f *m2){
  if(pt1->size() != pt2->size()){
    RVec_f v = {-9999.9};
    return v;
  }
  else {
    auto MT2 = (*m1)*(*m1) + (*m2)*(*m2) + 2*(sqrt((*m1)*(*m1) + (*pt1)*(*pt1)) * sqrt((*m2)*(*m2) + (*pt2)*(*pt2)) - (*pt1)*(*pt2)*cos(ROOT::VecOps::DeltaPhi(*phi1, *phi2)));
    return sqrt(MT2);
  }
}



#endif
