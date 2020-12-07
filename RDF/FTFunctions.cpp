#ifndef FOURTOP_FUNCTIONS
#define FOURTOP_FUNCTIONS

//#include <boost>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <TObject.h>
// #include <TH.h>
#include <TH1.h>
#include <TH2.h>
#include <TH3.h>
#include <TFile.h>
#include <TUUID.h>
#include "ROOT/RVec.hxx"

typedef ROOT::VecOps::RVec<Float_t>                        RVec_f;
typedef ROOT::VecOps::RVec<Float_t>::const_iterator        RVec_f_iter;
typedef ROOT::VecOps::RVec<Int_t>                          RVec_i;
typedef ROOT::VecOps::RVec<Int_t>::const_iterator          RVec_i_iter;
typedef ROOT::VecOps::RVec<std::string>                    RVec_str;
typedef ROOT::VecOps::RVec<std::string>::const_iterator    RVec_str_iter;

//aim for a std::vector<std::map<std::string, ROOT::TH>> format where the vector index corresponds to the slot # for multithreaded lookups
// class LUT: public TObject {
class LUT {
  //LookUp Table
public:
  LUT() { _LUT_MAP_TH1.clear(); _LUT_MAP_TH2.clear(); _LUT_MAP_TH3.clear(); }
  // LUT(std::string file, std::string path);
  LUT(const LUT &lut);
  ~LUT() {}
  void Add(std::string file, std::string path, std::string handle = "");
  std::vector<std::string> TH1Keys();
  std::vector<std::string> TH2Keys();
  std::vector<std::string> TH3Keys();

  template <typename X>
  double TH1Lookup(std::string key, X xval);
  template <typename X>
  double TH1LookupErr(std::string key, X xval);

  template <typename X, typename Y>
  double TH2Lookup(std::string key, X xval, Y yval);
  template <typename X, typename Y>
  double TH2LookupErr(std::string key, X xval, Y yval);

  template <typename X, typename Y, typename Z>
  double TH3Lookup(std::string key, X xval, Y yval, Z zval);
  template <typename X, typename Y, typename Z>
  double TH3LookupErr(std::string key, X xval, Y yval, Z zval);

private:
  std::map<std::string, TH1*> _LUT_MAP_TH1;
  std::map<std::string, TH2*> _LUT_MAP_TH2;
  std::map<std::string, TH3*> _LUT_MAP_TH3;
  
};
LUT::LUT(const LUT &lut) {
  TUUID uuid = TUUID();
  std::map<std::string, TH1*> _LUT_MAP_TH1;
  std::map<std::string, TH2*> _LUT_MAP_TH2;
  std::map<std::string, TH3*> _LUT_MAP_TH3;
  //Clone each histogram in each map, appending this copy constructor's uuid onto the end. Each histogram in the original should have a unique uuid,
  //the ones here will inherit them and append a single copy-constructor uuid to them
  for(auto th1_iter = lut._LUT_MAP_TH1.begin(); th1_iter != lut._LUT_MAP_TH1.end(); ++th1_iter){
    std::string name = static_cast<std::string>(th1_iter->second->GetName()) + "___" + uuid.AsString();
    _LUT_MAP_TH1[th1_iter->first] = static_cast<TH1*>(th1_iter->second->Clone(name.c_str()));
    _LUT_MAP_TH1[th1_iter->first]->SetDirectory(0);
  }
  for(auto th2_iter = lut._LUT_MAP_TH2.begin(); th2_iter != lut._LUT_MAP_TH2.end(); ++th2_iter){
    std::string name = static_cast<std::string>(th2_iter->second->GetName()) + "___" + uuid.AsString();
    _LUT_MAP_TH2[th2_iter->first] = static_cast<TH2*>(th2_iter->second->Clone(name.c_str()));
    _LUT_MAP_TH2[th2_iter->first]->SetDirectory(0);
  }
  for(auto th3_iter = lut._LUT_MAP_TH3.begin(); th3_iter != lut._LUT_MAP_TH3.end(); ++th3_iter){
    std::string name = static_cast<std::string>(th3_iter->second->GetName()) + "___" + uuid.AsString();
    _LUT_MAP_TH3[th3_iter->first] = static_cast<TH3*>(th3_iter->second->Clone(name.c_str()));
    _LUT_MAP_TH3[th3_iter->first]->SetDirectory(0);
  }
}  
void LUT::Add(std::string file, std::string path, std::string handle = "") {
  TUUID uuid = TUUID();
  TFile *f = TFile::Open(file.c_str(), "read");
  if(f) {
    if(f->IsOpen()){
      auto temp = f->Get(path.c_str());
      if(temp){
	std::string key;
	Bool_t isTH1 = (std::strncmp(temp->ClassName(), "TH1", 3) == 0);
	Bool_t isTH2 = (std::strncmp(temp->ClassName(), "TH2", 3) == 0);
	Bool_t isTH3 = (std::strncmp(temp->ClassName(), "TH3", 3) == 0);
	std::string name = static_cast<std::string>(temp->GetName()) + "___" + uuid.AsString();
	if(handle.length() == 0) {
	  key = path;
	}
	else {
	  key = handle;
	}
	if( isTH1 ) { 
	  _LUT_MAP_TH1[key] = static_cast<TH1*>(temp->Clone(name.c_str()));
	  _LUT_MAP_TH1[key]->SetDirectory(0);
	}
	else if( isTH2 ) { 
	  _LUT_MAP_TH2[key] = static_cast<TH2*>(temp->Clone(name.c_str())); 
	  _LUT_MAP_TH2[key]->SetDirectory(0);
	    }
	else if( isTH3 ) { 
	  _LUT_MAP_TH3[key] = static_cast<TH3*>(temp->Clone(name.c_str())); 
	  _LUT_MAP_TH3[key]->SetDirectory(0);
	}
	else { throw std::runtime_error( "Unhandled LookUpTable class " + static_cast<std::string>(temp->ClassName())); }
	f->Close();
      }
      else {
	f->Close();
	throw std::runtime_error( "Failed to instantiate valid LUT for path " + path + " in file " + file );
      }
    }
    else {
      throw std::runtime_error( "Failed to open file: " + file );
    }
  }
  else {
      throw std::runtime_error( "LookUpTable got a null pointer opening up the file: " + file );
  }
      
}
std::vector<std::string> LUT::TH1Keys(){
  std::vector<std::string> ret;
  for(std::map< std::string, TH1* >::iterator th1_iter = _LUT_MAP_TH1.begin(); th1_iter != _LUT_MAP_TH1.end(); ++th1_iter){
    ret.push_back(th1_iter->first);
  }  
  return ret;
}
std::vector<std::string> LUT::TH2Keys(){
  std::vector<std::string> ret;
  for(std::map< std::string, TH2* >::iterator th2_iter = _LUT_MAP_TH2.begin(); th2_iter != _LUT_MAP_TH2.end(); ++th2_iter){
    ret.push_back(th2_iter->first);
  }  
  return ret;
}
std::vector<std::string> LUT::TH3Keys(){
  std::vector<std::string> ret;
  for(std::map< std::string, TH3* >::iterator th3_iter = _LUT_MAP_TH3.begin(); th3_iter != _LUT_MAP_TH3.end(); ++th3_iter){
    ret.push_back(th3_iter->first);
  }  
  return ret;
}
template<typename X>
double LUT::TH1Lookup(std::string key, X xval){
  try {
    int binx = std::max(1, std::min(_LUT_MAP_TH1[key]->GetNbinsX(), _LUT_MAP_TH1[key]->GetXaxis()->FindBin(xval)));
    return _LUT_MAP_TH1[key]->GetBinContent(binx);
  }
  catch (const std::exception& e) {
    std::cout << "Caught exception in LUT::TH1Lookup" << std::endl;
    if( _LUT_MAP_TH1.find( key ) != _LUT_MAP_TH1.end() ){ 
      std::cout << "Key \"" << key << "\" not found in the TH1 LUT" << std::endl;
    }
    std::cout << "\nCaught exception: " << e.what() << std::endl;
    throw;
  }
}
template<typename X>
double LUT::TH1LookupErr(std::string key, X xval){
  try {
    int binx = std::max(1, std::min(_LUT_MAP_TH1[key]->GetNbinsX(), _LUT_MAP_TH1[key]->GetXaxis()->FindBin(xval)));
    return _LUT_MAP_TH1[key]->GetBinError(binx);
  }
  catch (const std::exception& e) {
    std::cout << "Caught exception in LUT::TH1LookupErr" << std::endl;
    if( _LUT_MAP_TH1.find( key ) != _LUT_MAP_TH1.end() ){ 
      std::cout << "Key \"" << key << "\" not found in the TH1 LUT" << std::endl;
    }
    std::cout << "\nCaught exception: " << e.what() << std::endl;
    throw;
  }
}
template<typename X, typename Y>
double LUT::TH2Lookup(std::string key, X xval, Y yval){
  try {
    int binx = std::max(1, std::min(_LUT_MAP_TH2[key]->GetNbinsX(), _LUT_MAP_TH2[key]->GetXaxis()->FindBin(xval)));
    int biny = std::max(1, std::min(_LUT_MAP_TH2[key]->GetNbinsY(), _LUT_MAP_TH2[key]->GetYaxis()->FindBin(yval)));
    return _LUT_MAP_TH2[key]->GetBinContent(binx, biny);
  }
  catch (const std::exception& e) {
    std::cout << "Caught exception in LUT::TH2Lookup" << std::endl;
    if( _LUT_MAP_TH2.find( key ) != _LUT_MAP_TH2.end() ){ 
      std::cout << "Key \"" << key << "\" not found in the TH2 LUT" << std::endl;
    }
    std::cout << "\nCaught exception: " << e.what() << std::endl;
    throw;
  }
}
template<typename X, typename Y>
double LUT::TH2LookupErr(std::string key, X xval, Y yval){
  try {
    int binx = std::max(1, std::min(_LUT_MAP_TH2[key]->GetNbinsX(), _LUT_MAP_TH2[key]->GetXaxis()->FindBin(xval)));
    int biny = std::max(1, std::min(_LUT_MAP_TH2[key]->GetNbinsY(), _LUT_MAP_TH2[key]->GetYaxis()->FindBin(yval)));
    return _LUT_MAP_TH2[key]->GetBinError(binx, biny);
  }
  catch (const std::exception& e) {
    std::cout << "Caught exception in LUT::TH2LookupErr" << std::endl;
    if( _LUT_MAP_TH2.find( key ) != _LUT_MAP_TH2.end() ){ 
      std::cout << "Key \"" << key << "\" not found in the TH2 LUT" << std::endl;
    }
    std::cout << "\nCaught exception: " << e.what() << std::endl;
    throw;
  }
}
template<typename X, typename Y, typename Z>
double LUT::TH3Lookup(std::string key, X xval, Y yval, Z zval){
  try {
      int binx = std::max(1, std::min(_LUT_MAP_TH3[key]->GetNbinsX(), _LUT_MAP_TH3[key]->GetXaxis()->FindBin(xval)));
      int biny = std::max(1, std::min(_LUT_MAP_TH3[key]->GetNbinsY(), _LUT_MAP_TH3[key]->GetYaxis()->FindBin(yval)));
      int binz = std::max(1, std::min(_LUT_MAP_TH3[key]->GetNbinsZ(), _LUT_MAP_TH3[key]->GetZaxis()->FindBin(zval)));
      return _LUT_MAP_TH3[key]->GetBinContent(binx, biny);
  }
  catch (const std::exception& e) {
    std::cout << "Caught exception in LUT::TH3Lookup" << std::endl;
    if( _LUT_MAP_TH3.find( key ) != _LUT_MAP_TH3.end() ){ 
      std::cout << "Key \"" << key << "\" not found in the TH3 LUT" << std::endl;
    }
    std::cout << "\nCaught exception: " << e.what() << std::endl;
    throw;
  }
}
template<typename X, typename Y, typename Z>
double LUT::TH3LookupErr(std::string key, X xval, Y yval, Z zval){
  try {
    int binx = std::max(1, std::min(_LUT_MAP_TH3[key]->GetNbinsX(), _LUT_MAP_TH3[key]->GetXaxis()->FindBin(xval)));
    int biny = std::max(1, std::min(_LUT_MAP_TH3[key]->GetNbinsY(), _LUT_MAP_TH3[key]->GetYaxis()->FindBin(yval)));
    int binz = std::max(1, std::min(_LUT_MAP_TH3[key]->GetNbinsZ(), _LUT_MAP_TH3[key]->GetZaxis()->FindBin(zval)));
    return _LUT_MAP_TH3[key]->GetBinError(binx, biny);
  }
  catch (const std::exception& e) {
    std::cout << "Caught exception in LUT::TH3LookupErr" << std::endl;
    if( _LUT_MAP_TH3.find( key ) != _LUT_MAP_TH3.end() ){ 
      std::cout << "Key \"" << key << "\" not found in the TH3 LUT" << std::endl;
    }
    std::cout << "\nCaught exception: " << e.what() << std::endl;
    throw;
  }
}

class LUTManager {
  //LookUp Table Manager
public:
  LUTManager() {origin = new LUT(); lut_vector = std::make_shared< std::vector<LUT*> >();}
  ~LUTManager() {}
  void Add(std::map< std::string, std::vector<std::string> > idmap);
  void Finalize(int nThreads);
std::shared_ptr< std::vector<LUT*> > GetLUTVector();

private:
  std::shared_ptr< std::vector<LUT*> > lut_vector; // = std::make_shared< std::vector<LUT*> >();
  LUT *origin;
};
void LUTManager::Add(std::map< std::string, std::vector<std::string> > idmap) {
  for(std::map< std::string, std::vector<std::string> >::iterator id_iter = idmap.begin(); id_iter != idmap.end(); ++id_iter){
    // std::cout << "Key: " << id_iter->first << std::endl;
    // std::cout << "Values: ";
    std::vector<std::string> vec_values = id_iter->second;
    // for(std::vector<std::string>::iterator vector_iter = id_iter->second.begin(); vector_iter != id_iter->second.end(); ++vector_iter){
    //   std::cout << *vector_iter;
    // }
    // std::cout << std::endl;
    //Load each map into the origin LUT, from which all others will be copied in the finalize method
    if(vec_values.size() > 1){
      std::cout << vec_values[0] << " " << vec_values[1] << std::endl;
      origin->Add(vec_values[0], vec_values[1], id_iter->first);
    }
  }
  std::cout << "Finalizing" << std::endl;
}
void LUTManager::Finalize(int nThreads) {
  for(int n_iter = 0; n_iter < nThreads; ++n_iter){
    LUT *temp(origin);
    lut_vector->push_back(temp);
  }
}
std::shared_ptr< std::vector<LUT*> > LUTManager::GetLUTVector(){
  return lut_vector;
}

class baseLUT {
  //LookUp Table
public:
  baseLUT() { _LUT_TH1 = 0; _LUT_TH2 = 0; _LUT_TH3 = 0; }
  baseLUT(std::string file, std::string path);
  ~baseLUT() {}
  double TH2Lookup(double xval, double yval);
  double TH2LookupErr(double xval, double yval);

private:
  //unique uuid for multiple instances to be created in multithreading, will be prepended to histogram memory names to avoid name-clashes, i.e. may be _rdfslot
  int uuid = 0; 
  TH1 *_LUT_TH1;
  TH2 *_LUT_TH2;
  TH3 *_LUT_TH3;
  // std::map<std::string, TH*> _LUT_MAP;
  
};
baseLUT::baseLUT(std::string file, std::string path) {
  TUUID uuid = TUUID();
  TFile *f = TFile::Open(file.c_str(), "read");
  if(f) {
    if(f->IsOpen()){
      auto temp = f->Get(path.c_str());
      if(temp){
	Bool_t isTH1 = (std::strncmp(temp->ClassName(), "TH1", 3) == 0);
	Bool_t isTH2 = (std::strncmp(temp->ClassName(), "TH2", 3) == 0);
	Bool_t isTH3 = (std::strncmp(temp->ClassName(), "TH3", 3) == 0);
	std::string name = static_cast<std::string>(temp->GetName()) + "___" + uuid.AsString();
	if( isTH1 ) { 
	  _LUT_TH1 = static_cast<TH1*>(temp->Clone(name.c_str()));
	  _LUT_TH1->SetDirectory(0);
	}
	else if( isTH2 ) { 
	  _LUT_TH2 = static_cast<TH2*>(temp->Clone(name.c_str())); 
	  _LUT_TH2->SetDirectory(0);
	    }
	else if( isTH3 ) { 
	  _LUT_TH3 = static_cast<TH3*>(temp->Clone(name.c_str())); 
	  _LUT_TH3->SetDirectory(0);
	}
	else { throw std::runtime_error( "Unhandled LookUpTable class " + static_cast<std::string>(temp->ClassName())); }
	f->Close();
      }
      else {
	f->Close();
	throw std::runtime_error( "Failed to instantiate valid LUT for path " + path + " in file " + file );
      }
    }
    else {
      throw std::runtime_error( "Failed to open file: " + file );
    }
  }
  else {
      throw std::runtime_error( "LookUpTable got a null pointer opening up the file: " + file );
  }
      
}
double baseLUT::TH2Lookup(double xval, double yval){
  int binx = std::max(1, std::min(_LUT_TH2->GetNbinsX(), _LUT_TH2->GetXaxis()->FindBin(xval)));
  int biny = std::max(1, std::min(_LUT_TH2->GetNbinsY(), _LUT_TH2->GetYaxis()->FindBin(yval)));
  return _LUT_TH2->GetBinContent(binx, biny);
}
double baseLUT::TH2LookupErr(double xval, double yval){
  int binx = std::max(1, std::min(_LUT_TH2->GetNbinsX(), _LUT_TH2->GetXaxis()->FindBin(xval)));
  int biny = std::max(1, std::min(_LUT_TH2->GetNbinsY(), _LUT_TH2->GetYaxis()->FindBin(yval)));
  return _LUT_TH2->GetBinError(binx, biny);
}
  

class TH2Lookup {
public:

  TH2Lookup() {lookupMap_.clear();}
  TH2Lookup(std::string file, std::string slot="0", bool debug=false);
  TH2Lookup(std::string file, std::vector<std::string> histos, std::string slot);
  ~TH2Lookup() {}

  //void setJets(int nJet, int *jetHadronFlavour, float *jetPt, float *jetEta);

  float getLookup(std::string key, float x_val, float y_val, bool debug=false);
  float getLookupErr(std::string key, float x_val, float y_val, bool debug=false);
  RVec_f getJetEfficiencySimple(ROOT::VecOps::RVec<int>* jets_flav, ROOT::VecOps::RVec<float>* jets_pt, ROOT::VecOps::RVec<float>* jets_eta);
  RVec_f getJetEfficiency(std::string category, std::string tagger_WP, RVec_i* jets_flav, RVec_f* jets_pt, RVec_f* jets_eta);
  double getEventYieldRatio(std::string sample, std::string variation, int nJet, double HT, bool debug=false);
  double getEventYieldRatio(std::string key, int nJet, double HT, bool debug=false);
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

TH2Lookup::TH2Lookup(std::string file, std::string slot="0", bool debug=false) {
  lookupMap_.clear();
  validKeys_.clear();
  TFile *f = TFile::Open(file.c_str(),"read");
  if(!f) {
    std::cout << "WARNING! File " << file << " cannot be opened." << std::endl;
    declaredFailure_ = true;
  }
  for(const auto&& obj: *(f->GetListOfKeys())){
    std::string key = obj->GetName();
    std::string clone_key = "TH2LU_" + slot + "_" + key;
    //for(int i=0; i<(int)histos.size();++i) {
    lookupMap_[obj->GetName()] = (TH2*)(f->Get(key.c_str())->Clone(clone_key.c_str()));
    lookupMap_[obj->GetName()]->SetDirectory(0);
    if(debug){std::cout << obj->GetName() << "     ";}
  }
  f->Close();
}

TH2Lookup::TH2Lookup(std::string file, std::vector<std::string> histos, std::string slot = "0") {
  lookupMap_.clear();
  validKeys_.clear();
  TFile *f = TFile::Open(file.c_str(),"read");
  if(!f) {
    std::cout << "WARNING! File " << file << " cannot be opened. Skipping this efficiency" << std::endl;
  }

  for(int i=0; i<(int)histos.size();++i) {
    lookupMap_[histos[i]] = (TH2*)(f->Get(histos[i].c_str()))->Clone(("TH2LU_"+slot+"_"+histos[i]).c_str());
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

float TH2Lookup::getLookup(std::string key, float x_val, float y_val, bool debug=false) {
  if(debug){std::cout << "TH2Lookup::getLookup invoked " << std::endl;}
  if ( lookupMap_.find(key) == lookupMap_.end() ) {
    // not found ... not sure how intensive this lookup is, but we need to guard against bad keys
    if(debug){std::cout << "Failed to find key" << std::endl;}
    double fail = -9999.9;
    return fail;
  } else {
    //found
    if(debug){std::cout << "Found key " << key << std::endl;}
    int binx = std::max(1, std::min(lookupMap_[key]->GetNbinsX(), lookupMap_[key]->GetXaxis()->FindBin(x_val)));
    int biny = std::max(1, std::min(lookupMap_[key]->GetNbinsY(), lookupMap_[key]->GetYaxis()->FindBin(y_val)));
    return lookupMap_[key]->GetBinContent(binx,biny);
  }
}

float TH2Lookup::getLookupErr(std::string key, float x_val, float y_val, bool debug=false) {
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
  yield = getLookup(key, HT, nJet, debug);
  return yield;
}

double TH2Lookup::getEventYieldRatio(std::string key, int nJet, double HT, bool debug=false){
  //Latest version uses keys of form "Aggregate__nom", so sample = "Aggregate_" and variation = "_nom"
  //For pseudo-1D lookups, this uses "<name>_1D<DIM>" such as "tttt_1DX" -> key = "tttt_1DY_nom" for example
  double yield = 1.0;
  if(debug){std::cout << "getEventYield key: " << key << std::endl;}
  yield = getLookup(key, HT, nJet, debug);
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
  //Future need: function for reweighting cross-section with multiple samples in a phase space, i.e. ttbar with nGenJet >= 7,
  //GenHT >= 500 for ttJets, TTTo2L2Nu, TTTo2L2Nu_nJet7HT500. Makes sense to weight the events in this phase space with 
  //XS_i =  proc_XS * N_i/Sum(N_i) * 1/sumWeights_i, where N_i is number of events from each sample in the phase space,
  //sumWeights_i is the sum of event weights for that sample in that phase space, etc. So summing over all events and over all samples
  //gives proc_XS * SUM[ N_i/Sum(N_i) * sumWeights_i/sumWeights_i] = proc_XS * Sum[N_i/Sum(N_i)] = proc_XS

  // std::map<std::string, int> datasetCode

  // std::map<std::string, int> metaEventId(std::string dataset, std::string campaign){
  //   //return a map of meta information for encoding the packedEventId efficiently. This contains info like datasetId, campaignId, ...
  //   std::map<std::string, std::string> datasetCode;
  //   datasetCode["/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM"] = 1;
  //   datasetCode[""] = 2;
  //   datasetCode["/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM"] = 3;
  //   datasetCode[""] = 4;
  //   datasetCode[""] = 5;
  //   datasetCode[""] = 6;
  //   datasetCode[""] = 7;
  //   datasetCode[""] = 8;
  //   datasetCode[""] = 9;
  //   datasetCode[""] = 10;
  //   datasetCode[""] = 11;
  //   datasetCode[""] = 12;
  //   datasetCode[""] = 13;
  //   datasetCode[""] = 14;
  //   datasetCode[""] = 15;
  //   datasetCode[""] = 16;
  //   datasetCode[""] = 17;
  //   datasetCode[""] = 18;
  //   datasetCode[""] = 19;
  //   datasetCode[""] = 20;
  //   datasetCode[""] = 21;
  //   datasetCode[""] = 22;
  //   datasetCode[""] = 23;
  //   datasetCode[""] = 24;
  //   datasetCode[""] = 25;
  //   datasetCode[""] = 26;
  //   datasetCode[""] = 27;
  //   datasetCode[""] = 28;
  //   datasetCode[""] = 29;
  //   datasetCode[""] = 30;

  //   std::map<std::string, int> campaignCode;
  //   campaignCode[""
  //     //code to get the luminosity lookup from the main function...
  //     retCode["luminosity"] = std::to_string(unpackEventId(packedEventId, genWeight, luminosity, true));
  //   } else {
  //     retCode["luminosity"] = "This is probably a bad idea, KISS my friend! Drop the lumi and genWeight";
  //   }
  //   return retCode;
  // }
  //Can't get what I want from this, so work from the python end. FFS, another day's effort wasted on buggy shit. Need to know the compression enumeration is ROOT.ROOT.(algo)
  // const UInt_t barWidth = 60;
  // ULong64_t processed = 0, totalEvents = 0;
  // std::string progressBar;
  // std::mutex barMutex;
  // auto registerEvents = [](ULong64_t nIncrement) {totalEvents += nIncrement;};

  // ROOT::RDF::RResultPtr<ULong64_t> AddProgressBar(ROOT::RDF::RNode df, int everyN=10000, int totalN=100000) {
  //   registerEvents(totalN);
  //   auto c = df.Count();
  //   c.OnPartialResultSlot(everyN, [everyN] (unsigned int slot, ULong64_t &cnt){
  // 	std::lock_guard<std::mutex> l(barMutex);
  //       processed += everyN; //everyN captured by value for this lambda
  //       progressBar = "[";
  //       for(UInt_t i = 0; i < static_cast<UInt_t>(static_cast<Float_t>(processed)/totalEvents*barWidth); ++i){
  // 	  progressBar.push_back('|');
  //       }
  //       // escape the '\' when defined in python string
  // 	std::cout << "\\r" << std::left << std::setw(barWidth) << progressBar << "] " << processed << "/" << totalEvents << std::flush;
  //     });
  //   return c;
  // }
  std::map< std::string, std::vector<std::string> > GetCorrectorMap(std::string era, 
								    std::string legacy, 
								    std::string VFP="",
								    std::string muon_top_path = "", 
								    std::string muon_id = "", 
								    std::string muon_iso = "", 
								    std::string electron_top_path = "", 
								    std::string electron_id = "", 
								    std::string electron_eff = "",
								    std::string btag_top_path = "", 
								    std::vector<std::string> btag_process_names = {"tttt"},
								    std::vector<std::string> btag_systematic_names = {"nom"},
								    bool btag_use_aggregate = false,
								    bool btag_use_HT_only = false,
								    bool btag_use_nJet_only = false){
    //python constructor:
    //def __init__(self, muon_ID=None, muon_ISO=None, electron_ID=None, era=None, doMuonHLT=False, doElectronHLT_ZVtx=False, 
    //pre2018Run316361Lumi = 8.942, post2018Run316361Lumi = 50.785

    //about paths... 
    //el_pre = "{0:s}/src/FourTopNAOD/Kai/python/data/leptonSF/Electron/{1:s}/".format(os.environ['CMSSW_BASE'], self.era)

    std::string muon_path, electron_path;
    if(era != "2016" && legacy != "UL"){
      muon_path = muon_top_path + "/" + era + "/" + legacy + "/";
      electron_path = electron_top_path + "/" + era + "/" + legacy + "/";
    }
    else{
      if(!( VFP == "postVFP" || VFP == "preVFP")){
	std::cout << "WARNING: Invalid path due to VFP parameter not matching options for 2016 Ultra-Legacy production" << std::endl;
      }
      muon_path = muon_top_path + "/" + era + "/" + legacy + "/" + VFP + "/";
      electron_path = electron_top_path + "/" + era + "/" + legacy + "/" + VFP + "/";
    }
    
    std::cout << "Era: " << era << "\nLegacy: " << legacy <<  "\nPreVFP: " << VFP << "\nMuon top path: " << muon_top_path << "\nElectron top path: " << electron_top_path;
    std::cout << "\nBtag top path: " << btag_top_path << std::endl;

    //mu_pre = "{0:s}/src/FourTopNAOD/Kai/python/data/leptonSF/Muon/{1:s}/".format(os.environ['CMSSW_BASE'], self.era)
    //store the ID map per era, with a path being prepended to the filenames listed below at the end
    std::map< std::string, std::vector<std::string> > electron_options_central;
    std::map< std::string, std::vector<std::string> > electron_options_uncertainty;
    std::map< std::string, std::vector<std::string> > muon_options_central;
    std::map< std::string, std::vector<std::string> > muon_options_stat;
    std::map< std::string, std::vector<std::string> > muon_options_syst;
    if(legacy == "UL"){
      std::cout << "WARNING: In FTA:::GetIDMap, legacy = 'UL' was specified. Right now, this defaults to the non-UL/EOY processing maps" << std::endl;
      //https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaUL2016To2018#SFs_for_Electrons_UL_2018
      if(era == "2016"){
	std::cout << "WARNING: Ultra-Legacy era 2016 should be handled differently pre and postVFP... Note done yet" << std::endl;
      }
    }
    //Electron ID's
    //Note on uncertainties: stored in the same maps and accessed by bin error, so just copy...
    if(era == "2016"){
      if(legacy == "non-UL"){
	electron_options_central["EFF_ptBelow20"] =	{"EGM2D_BtoH_low_RecoSF_Legacy2016.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptBelow20"] = {"EGM2D_BtoH_low_RecoSF_Legacy2016.root", "EGamma_SF2D", "TH2LookupErr""Electron_eta", "Electron_pt"};
	electron_options_central["EFF_ptAbove20"] =	{"EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptAboe20"] =  {"EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root", "EGamma_SF2D", "TH2LookupErr""Electron_eta", "Electron_pt"};
	electron_options_central["LooseID"]  =		{"2016LegacyReReco_ElectronLoose_Fall17V2.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["LooseID"]  =	{"2016LegacyReReco_ElectronLoose_Fall17V2.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MediumID"]  =		{"2016LegacyReReco_ElectronMedium_Fall17V2.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MediumID"]  =	{"2016LegacyReReco_ElectronMedium_Fall17V2.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["TightID"]  =		{"2016LegacyReReco_ElectronTight_Fall17V2.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["TightID"]  =	{"2016LegacyReReco_ElectronTight_Fall17V2.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80iso"]  =		{"2016LegacyReReco_ElectronMVA80_Fall17V2.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80iso"]  =	{"2016LegacyReReco_ElectronMVA80_Fall17V2.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80noiso"]  =	{"2016LegacyReReco_ElectronMVA80noiso_Fall17V2.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80noiso"]  =	{"2016LegacyReReco_ElectronMVA80noiso_Fall17V2.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90iso"]  =		{"2016LegacyReReco_ElectronMVA90_Fall17V2.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90iso"]  =	{"2016LegacyReReco_ElectronMVA90_Fall17V2.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90noiso"]  =	{"2016LegacyReReco_ElectronMVA90noiso_Fall17V2.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90noiso"]  =	{"2016LegacyReReco_ElectronMVA90noiso_Fall17V2.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
      }
      else if(legacy == "UL" && VFP == "preVFP"){
	//Failed to deduce axis --> eta on x-axis, pt on y-axis. 
	electron_options_central["EFF_ptAbove20"] =	{"egammaEffi_ptAbove20.txt_EGM2D_UL2016preVFP.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptAbove20"] = {"egammaEffi_ptAbove20.txt_EGM2D_UL2016preVFP.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["EFF_ptBelow20"] =	{"egammaEffi_ptBelow20.txt_EGM2D_UL2016preVFP.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptBelow20"] = {"egammaEffi_ptBelow20.txt_EGM2D_UL2016preVFP.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Veto"] =		{"egammaEffi.txt_Ele_Veto_preVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Veto"] =		{"egammaEffi.txt_Ele_Veto_preVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Loose"] =		{"egammaEffi.txt_Ele_Loose_preVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Loose"] =		{"egammaEffi.txt_Ele_Loose_preVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Medium"] =		{"egammaEffi.txt_Ele_Medium_preVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Medium"] =	{"egammaEffi.txt_Ele_Medium_preVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Tight"] =		{"egammaEffi.txt_Ele_Tight_preVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Tight"] =		{"egammaEffi.txt_Ele_Tight_preVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80iso"] =		{"egammaEffi.txt_Ele_wp80iso_preVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80iso"] =	{"egammaEffi.txt_Ele_wp80iso_preVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80noiso"] =	{"egammaEffi.txt_Ele_wp80noiso_preVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80noiso"] =	{"egammaEffi.txt_Ele_wp80noiso_preVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90iso"] =		{"egammaEffi.txt_Ele_wp90iso_preVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90iso"] =	{"egammaEffi.txt_Ele_wp90iso_preVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90noiso"] =	{"egammaEffi.txt_Ele_wp90noiso_preVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90noiso"] =	{"egammaEffi.txt_Ele_wp90noiso_preVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};	
      }
      else if(legacy == "UL" && VFP == "postVFP"){
	std::cout << "WARNING: postVFP UL for 2016 is loading 2016 Legacy efficiencies, since postVFP UL versions haven't been made available as of writing.";
	std::cout << std::endl;
	electron_options_central["EFF_ptBelow20"] =	{"../../non-UL/EGM2D_BtoH_low_RecoSF_Legacy2016.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_central["EFF_ptBelow20"] =	{"../../non-UL/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_central["EFF_ptAbove20"] =	{"../../non-UL/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptAboe20"] =  {"../../non-UL/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root", "EGamma_SF2D", "TH2LookupErr""Electron_eta", "Electron_pt"};
	electron_options_central["Veto"] =		{"egammaEffi.txt_Ele_Veto_postVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Veto"] =		{"egammaEffi.txt_Ele_Veto_postVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Loose"] =		{"egammaEffi.txt_Ele_Loose_postVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Loose"] =		{"egammaEffi.txt_Ele_Loose_postVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Medium"] =		{"egammaEffi.txt_Ele_Medium_postVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Medium"] =	{"egammaEffi.txt_Ele_Medium_postVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Tight"] =		{"egammaEffi.txt_Ele_Tight_postVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Tight"] =		{"egammaEffi.txt_Ele_Tight_postVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80iso"] =		{"egammaEffi.txt_Ele_wp80iso_postVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80iso"] =	{"egammaEffi.txt_Ele_wp80iso_postVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80noiso"] =	{"egammaEffi.txt_Ele_wp80noiso_postVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80noiso"] =	{"egammaEffi.txt_Ele_wp80noiso_postVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90iso"] =		{"egammaEffi.txt_Ele_wp90iso_postVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90iso"] =	{"egammaEffi.txt_Ele_wp90iso_postVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90noiso"] =	{"egammaEffi.txt_Ele_wp90noiso_postVFP_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90noiso"] =	{"egammaEffi.txt_Ele_wp90noiso_postVFP_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
      }
    }
    else if(era == "2017"){
      if(legacy == "non-UL"){
	std::cout << "WARNING: for 2017 non-UL, Efficiencies are both from the non-low Et measurements, in case this has changed..." << std::endl;
	electron_options_central["EFF_ptBelow20"] =	{"egammaEffi.txt_EGM2D_runBCDEF_passingRECO_lowEt.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptBelow20"] = {"egammaEffi.txt_EGM2D_runBCDEF_passingRECO_lowEt.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["EFF_ptAbove20"] =	{"egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptAbove20"] = {"egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Veto"] =		{"2017_ElectronWPVeto_Fall17V2.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Veto"] =		{"2017_ElectronWPVeto_Fall17V2.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Loose"] =		{"2017_ElectronLoose.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Loose"] =		{"2017_ElectronLoose.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Medium"] =		{"2017_ElectronMedium.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Medium"] =	{"2017_ElectronMedium.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Tight"] =		{"2017_ElectronTight.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Tight"] =		{"2017_ElectronTight.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80noiso"] =	{"2017_ElectronMVA80noiso.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80noiso"] =	{"2017_ElectronMVA80noiso.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80iso"] =		{"2017_ElectronMVA80.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80iso"] =	{"2017_ElectronMVA80.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90noiso"] =	{"2017_ElectronMVA90noiso.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90noiso"] =	{"2017_ElectronMVA90noiso.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90iso"] =		{"2017_ElectronMVA90.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90iso"] =	{"2017_ElectronMVA90.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
      }
      else if(legacy == "UL"){
	//Failed to deduce axis--> not checked, assume the same... more waste of my precious goddamned fucking time
	electron_options_central["EFF_ptBelow20"] =	{"egammaEffi_ptBelow20.txt_EGM2D_UL2017.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptBelow20"] = {"egammaEffi_ptBelow20.txt_EGM2D_UL2017.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["EFF_ptAbove20"] =	{"egammaEffi_ptAbove20.txt_EGM2D_UL2017.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptAbove20"] = {"egammaEffi_ptAbove20.txt_EGM2D_UL2017.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Veto"] =		{"egammaEffi.txt_EGM2D_Veto_UL17.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Veto"] =		{"egammaEffi.txt_EGM2D_Veto_UL17.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Loose"] =		{"egammaEffi.txt_EGM2D_Loose_UL17.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Loose"] =		{"egammaEffi.txt_EGM2D_Loose_UL17.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Medium"] =		{"egammaEffi.txt_EGM2D_Medium_UL17.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Medium"] =	{"egammaEffi.txt_EGM2D_Medium_UL17.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Tight"] =		{"egammaEffi.txt_EGM2D_Tight_UL17.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Tight"] =		{"egammaEffi.txt_EGM2D_Tight_UL17.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80iso"] =		{"egammaEffi.txt_EGM2D_MVA80iso_UL17.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80iso"] =	{"egammaEffi.txt_EGM2D_MVA80iso_UL17.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80noiso"] =	{"egammaEffi.txt_EGM2D_MVA80noIso_UL17.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80noiso"] =	{"egammaEffi.txt_EGM2D_MVA80noIso_UL17.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90iso"] =		{"egammaEffi.txt_EGM2D_MVA90iso_UL17.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90iso"] =	{"egammaEffi.txt_EGM2D_MVA90iso_UL17.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90noiso"] =	{"egammaEffi.txt_EGM2D_MVA90noIso_UL17.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90noiso"] =	{"egammaEffi.txt_EGM2D_MVA90noIso_UL17.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
      }
    }
    else if(era == "2018"){
      if(legacy == "non-UL"){
	electron_options_central["EFF_ptBelow20"] =	{"egammaEffi.txt_EGM2D_updatedAll.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptBelow20"] = {"egammaEffi.txt_EGM2D_updatedAll.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["EFF_ptAbove20"] =	{"egammaEffi.txt_EGM2D_updatedAll.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptAbove20"] = {"egammaEffi.txt_EGM2D_updatedAll.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Veto"] =		{"2018_ElectronWPVeto_Fall17V2.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Veto"] =		{"2018_ElectronWPVeto_Fall17V2.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Loose"] =		{"2018_ElectronLoose.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Loose"] =		{"2018_ElectronLoose.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Medium"] =		{"2018_ElectronMedium.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Medium"] =	{"2018_ElectronMedium.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Tight"] =		{"2018_ElectronTight.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Tight"] =		{"2018_ElectronTight.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80noiso"] =	{"2018_ElectronMVA80noiso.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80noiso"] =	{"2018_ElectronMVA80noiso.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80iso"] =		{"2018_ElectronMVA80.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80iso"] =	{"2018_ElectronMVA80.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90noiso"] =	{"2018_ElectronMVA90noiso.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90noiso"] =	{"2018_ElectronMVA90noiso.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90iso"] =		{"2018_ElectronMVA90.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90iso"] =	{"2018_ElectronMVA90.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
      }
      else if(legacy == "UL"){
	//Failed to deduce axis
	electron_options_central["EFF_ptBelow20"] =	{"egammaEffi_ptBelow20.txt_EGM2D_UL2018.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptBelow20"] = {"egammaEffi_ptBelow20.txt_EGM2D_UL2018.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["EFF_ptAbove20"] =	{"egammaEffi_ptAbove20.txt_EGM2D_UL2018.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["EFF_ptAbove20"] = {"egammaEffi_ptAbove20.txt_EGM2D_UL2018.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Veto"] =		{"egammaEffi.txt_Ele_Veto_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Veto"] =		{"egammaEffi.txt_Ele_Veto_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Loose"] =		{"egammaEffi.txt_Ele_Loose_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Loose"] =		{"egammaEffi.txt_Ele_Loose_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Medium"] =		{"egammaEffi.txt_Ele_Medium_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Medium"] =	{"egammaEffi.txt_Ele_Medium_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["Tight"] =		{"egammaEffi.txt_Ele_Tight_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["Tight"] =		{"egammaEffi.txt_Ele_Tight_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80iso"] =		{"egammaEffi.txt_Ele_wp80iso_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80iso"] =	{"egammaEffi.txt_Ele_wp80iso_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA80noiso"] =	{"egammaEffi.txt_Ele_wp80noiso_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA80noiso"] =	{"egammaEffi.txt_Ele_wp80noiso_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90iso"] =		{"egammaEffi.txt_Ele_wp90iso_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90iso"] =	{"egammaEffi.txt_Ele_wp90iso_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
	electron_options_central["MVA90noiso"] =	{"egammaEffi.txt_Ele_wp90noiso_EGM2D.root", "EGamma_SF2D", "TH2Lookup", "Electron_eta", "Electron_pt"};
	electron_options_uncertainty["MVA90noiso"] =	{"egammaEffi.txt_Ele_wp90noiso_EGM2D.root", "EGamma_SF2D", "TH2LookupErr", "Electron_eta", "Electron_pt"};
      }
    }
    //Muon SFs //Mostly the errors are stored in separate histograms inside two files, 1 for ISO and 1 for ID 
    //So for 2017 and 2018 non-UL: BinContent from unique histogram ...ratio, BinError from unique histogram ...ratio_stat, ...ratio_syst
    //for 2016, central is BinContent and syst error is BinError on a single central histogram
    // "TRG_SL": {"Mu_Trg.root", "IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio",
    //            "STAT": "Mu_Trg.root", "IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio"},
    // "TRG_SL50": {"Mu_Trg.root", "Mu50_OR_TkMu50_PtEtaBins/pt_abseta_ratio",
    //              "STAT": "Mu_Trg.root", "Mu50_OR_TkMu50_PtEtaBins/pt_abseta_ratio"},
    if(era == "2016"){
      if(legacy == "non-UL"){
	muon_options_central["LooseID"] =                {"Mu_ID.root", "MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseID"] =                   {"Mu_ID.root", "MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["MediumID2016"] =           {"Mu_ID.root", "MC_NUM_MediumID2016_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["MediumID2016"] =              {"Mu_ID.root", "MC_NUM_MediumID2016_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["MediumID"] =               {"Mu_ID.root", "MC_NUM_MediumID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["MediumID"] =                  {"Mu_ID.root", "MC_NUM_MediumID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightID"] =                {"Mu_ID.root", "MC_NUM_TightID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightID"] =                   {"Mu_ID.root", "MC_NUM_TightID_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["HighPtID"] =               {"Mu_ID.root", "MC_NUM_HighPtID_DEN_genTracks_PAR_newpt_eta/pair_ne_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["HighPtID"] =                  {"Mu_ID.root", "MC_NUM_HighPtID_DEN_genTracks_PAR_newpt_eta/pair_ne_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};

	muon_options_central["LooseRelIso_LooseID"] =    {"Mu_Iso.root", "LooseISO_LooseID_pt_eta/pt_abseta_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelIso_LooseID"] =       {"Mu_Iso.root", "LooseISO_LooseID_pt_eta/pt_abseta_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelIso_MediumID"] =   {"Mu_Iso.root", "LooseISO_MediumID_pt_eta/pt_abseta_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelIso_MediumID"] =      {"Mu_Iso.root", "LooseISO_MediumID_pt_eta/pt_abseta_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelIso_TightID"] =    {"Mu_Iso.root", "LooseISO_TightID_pt_eta/pt_abseta_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelIso_TightID"] =       {"Mu_Iso.root", "LooseISO_TightID_pt_eta/pt_abseta_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightRelIso_MediumID"] =   {"Mu_Iso.root", "TightISO_MediumID_pt_eta/pt_abseta_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightRelIso_MediumID"] =      {"Mu_Iso.root", "TightISO_MediumID_pt_eta/pt_abseta_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightRelIso_TightID"] =    {"Mu_Iso.root", "TightISO_TightID_pt_eta/pt_abseta_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightRelIso_TightID"] =       {"Mu_Iso.root", "TightISO_TightID_pt_eta/pt_abseta_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelTkIso_HighPtID"] = {"Mu_Iso.root", "tkLooseISO_highptID_newpt_eta/pair_ne_ratio", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelTkIso_HighPtID"] =    {"Mu_Iso.root", "tkLooseISO_highptID_newpt_eta/pair_ne_ratio", "TH2LookupErr", "Muon_pt", "Muon_eta"};
      }
      else if(legacy == "UL" && VFP == "preVFP"){
	muon_options_central["HighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["HighPtID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["HighPtID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["MediumID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["MediumPromptID"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["SoftID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["SoftID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["SoftID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TrkHighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TrkHighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TrkHighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	
	
	muon_options_central["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelTkIso_HighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelTkIso_HighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
      }
      else if(legacy == "UL" && VFP == "postVFP"){
	muon_options_central["HighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["HighPtID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["HighPtID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["MediumID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["MediumPromptID"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["SoftID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["SoftID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["SoftID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TrkHighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TrkHighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TrkHighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};

	muon_options_central["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelTkIso_HighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelTkIso_HighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
      }
    }
    else if(era == "2017"){
      if(legacy == "non-UL"){
	// muon_options_central["TRG_SL"] = {"EfficienciesAndSF_RunBtoF_Nov17Nov2017.root", "IsoMu27_PtEtaBins/pt_abseta_ratio", "TH2Lookup", };
	// muon_options_stat[] = { "EfficienciesAndSF_RunBtoF_Nov17Nov2017.root", "IsoMu27_PtEtaBins/pt_abseta_ratio", "TH2Lookup", };

	muon_options_central["LooseID"] =		{"RunBCDEF_SF_ID_syst.root", "NUM_LooseID_DEN_genTracks_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseID"] =			{"RunBCDEF_SF_ID_syst.root", "NUM_LooseID_DEN_genTracks_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseID"] =			{"RunBCDEF_SF_ID_syst.root", "NUM_LooseID_DEN_genTracks_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightID"] =		{"RunBCDEF_SF_ID_syst.root", "NUM_TightID_DEN_genTracks_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TightID"] =			{"RunBCDEF_SF_ID_syst.root", "NUM_TightID_DEN_genTracks_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightID"] =			{"RunBCDEF_SF_ID_syst.root", "NUM_TightID_DEN_genTracks_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["MediumID"] =		{"RunBCDEF_SF_ID_syst.root", "NUM_MediumID_DEN_genTracks_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["MediumID"] =			{"RunBCDEF_SF_ID_syst.root", "NUM_MediumID_DEN_genTracks_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["MediumID"] =			{"RunBCDEF_SF_ID_syst.root", "NUM_MediumID_DEN_genTracks_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["HighPtID"] =		{"RunBCDEF_SF_ID_syst.root", "NUM_HighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["HighPtID"] =			{"RunBCDEF_SF_ID_syst.root", "NUM_HighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["HighPtID"] =			{"RunBCDEF_SF_ID_syst.root", "NUM_HighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TrkHighPtID"] =		{"RunBCDEF_SF_ID_syst.root", "NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TrkHighPtID"] =		{"RunBCDEF_SF_ID_syst.root", "NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TrkHighPtID"] =		{"RunBCDEF_SF_ID_syst.root", "NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["SoftID"] =		{"RunBCDEF_SF_ID_syst.root", "NUM_SoftID_DEN_genTracks_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["SoftID"] =			{"RunBCDEF_SF_ID_syst.root", "NUM_SoftID_DEN_genTracks_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["SoftID"] =			{"RunBCDEF_SF_ID_syst.root", "NUM_SoftID_DEN_genTracks_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["MediumPromptID"] =	{"RunBCDEF_SF_ID_syst.root", "NUM_MediumPromptID_DEN_genTracks_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["MediumPromptID"] =		{"RunBCDEF_SF_ID_syst.root", "NUM_MediumPromptID_DEN_genTracks_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["MediumPromptID"] =		{"RunBCDEF_SF_ID_syst.root", "NUM_MediumPromptID_DEN_genTracks_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	
	
	muon_options_central["TightRelIso_MediumID"] =		        {"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelIso_DEN_MediumID_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TightRelIso_MediumID"] =			{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelIso_DEN_MediumID_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightRelIso_MediumID"] =			{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelIso_DEN_MediumID_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelIso_MediumID"] =			{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_MediumID_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseRelIso_MediumID"] =			{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_MediumID_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelIso_MediumID"] =			{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_MediumID_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightRelIso_TightIDandIPCut"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TightRelIso_TightIDandIPCut"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightRelIso_TightIDandIPCut"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelIso_LooseID"] =			{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_LooseID_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseRelIso_LooseID"] =			{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_LooseID_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelIso_LooseID"] =			{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_LooseID_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightRelTkIso_TrkHighPtID"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TightRelTkIso_TrkHighPtID"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightRelTkIso_TrkHighPtID"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelTkIso_TrkHighPtID"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseRelTkIso_TrkHighPtID"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelTkIso_TrkHighPtID"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelTkIso_HighPtIDandIPCut"] =	{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseRelTkIso_HighPtIDandIPCut"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelTkIso_HighPtIDandIPCut"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelIso_TightIDandIPCut"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseRelIso_TightIDandIPCut"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelIso_TightIDandIPCut"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightRelTkIso_HighPtIDandIPCut"] =	{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TightRelTkIso_HighPtIDandIPCut"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightRelTkIso_HighPtIDandIPCut"] =		{"RunBCDEF_SF_ISO_syst.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
      }
      else if(legacy == "UL"){
	muon_options_central["HighPtID"] =				{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["HighPtID"] =					{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["HighPtID"] =					{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseID"] =				{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseID"] =					{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseID"] =					{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["MediumID"] =				{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["MediumID"] =					{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["MediumID"] =					{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["MediumPromptID"] =			{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["MediumPromptID"] =				{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["MediumPromptID"] =				{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["SoftID"] =				{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["SoftID"] =					{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["SoftID"] =					{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightID"] =				{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightID"] =					{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightID"] =					{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TrkHighPtID"] =				{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TrkHighPtID"] =				{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TrkHighPtID"] =				{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};	
	muon_options_central["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelTkIso_HighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelTkIso_HighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
      }
    }
    else if(era == "2018"){
      if(legacy == "non-UL"){
	// muon_options_central["TRG_SL_preRun316361"] =	 {"EfficienciesAndSF_2018Data_BeforeMuonHLTUpdate.root", "IsoMu24_PtEtaBins/pt_abseta_ratio", "TH2Lookup", };
	// muon_options_stat["TRG_SL_preRun316361"] =		 {"EfficienciesAndSF_2018Data_BeforeMuonHLTUpdate.root", "IsoMu24_PtEtaBins/pt_abseta_ratio", "TH2Lookup", };
	// muon_options_central["TRG_SL"] =			 {"EfficienciesAndSF_2018Data_AfterMuonHLTUpdate.root", "IsoMu24_PtEtaBins/pt_abseta_ratio", "TH2Lookup", };
	// muon_options_stat["TRG_SL_preRun316361"] =		 {"EfficienciesAndSF_2018Data_AfterMuonHLTUpdate.root", "IsoMu24_PtEtaBins/pt_abseta_ratio", "TH2Lookup", };

	muon_options_central["LooseID"] =		{"RunABCD_SF_ID.root", "NUM_LooseID_DEN_TrackerMuons_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseID"] =			{"RunABCD_SF_ID.root", "NUM_LooseID_DEN_TrackerMuons_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseID"] =			{"RunABCD_SF_ID.root", "NUM_LooseID_DEN_TrackerMuons_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightID"] =		{"RunABCD_SF_ID.root", "NUM_TightID_DEN_TrackerMuons_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TightID"] =			{"RunABCD_SF_ID.root", "NUM_TightID_DEN_TrackerMuons_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightID"] =			{"RunABCD_SF_ID.root", "NUM_TightID_DEN_TrackerMuons_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["MediumID"] =		{"RunABCD_SF_ID.root", "NUM_MediumID_DEN_TrackerMuons_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["MediumID"] =			{"RunABCD_SF_ID.root", "NUM_MediumID_DEN_TrackerMuons_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["MediumID"] =			{"RunABCD_SF_ID.root", "NUM_MediumID_DEN_TrackerMuons_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["HighPtID"] =		{"RunABCD_SF_ID.root", "NUM_HighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["HighPtID"] =			{"RunABCD_SF_ID.root", "NUM_HighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["HighPtID"] =			{"RunABCD_SF_ID.root", "NUM_HighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TrkHighPtID"] =		{"RunABCD_SF_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TrkHighPtID"] =		{"RunABCD_SF_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TrkHighPtID"] =		{"RunABCD_SF_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["SoftID"] =		{"RunABCD_SF_ID.root", "NUM_SoftID_DEN_TrackerMuons_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["SoftID"] =			{"RunABCD_SF_ID.root", "NUM_SoftID_DEN_TrackerMuons_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["SoftID"] =			{"RunABCD_SF_ID.root", "NUM_SoftID_DEN_TrackerMuons_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["MediumPromptID"] =	{"RunABCD_SF_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["MediumPromptID"] =		{"RunABCD_SF_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["MediumPromptID"] =		{"RunABCD_SF_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	

	muon_options_central["TightRelIso_MediumID"] =			{"RunABCD_SF_ISO.root", "NUM_TightRelIso_DEN_MediumID_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TightRelIso_MediumID"] =			{"RunABCD_SF_ISO.root", "NUM_TightRelIso_DEN_MediumID_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightRelIso_MediumID"] =			{"RunABCD_SF_ISO.root", "NUM_TightRelIso_DEN_MediumID_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelIso_MediumID"] =			{"RunABCD_SF_ISO.root", "NUM_LooseRelIso_DEN_MediumID_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseRelIso_MediumID"] =			{"RunABCD_SF_ISO.root", "NUM_LooseRelIso_DEN_MediumID_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelIso_MediumID"] =			{"RunABCD_SF_ISO.root", "NUM_LooseRelIso_DEN_MediumID_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightRelIso_TightIDandIPCut"] =		{"RunABCD_SF_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TightRelIso_TightIDandIPCut"] =		{"RunABCD_SF_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightRelIso_TightIDandIPCut"] =		{"RunABCD_SF_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelIso_LooseID"] =			{"RunABCD_SF_ISO.root", "NUM_LooseRelIso_DEN_LooseID_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseRelIso_LooseID"] =			{"RunABCD_SF_ISO.root", "NUM_LooseRelIso_DEN_LooseID_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelIso_LooseID"] =			{"RunABCD_SF_ISO.root", "NUM_LooseRelIso_DEN_LooseID_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightRelTkIso_TrkHighPtID"] =		{"RunABCD_SF_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TightRelTkIso_TrkHighPtID"] =		{"RunABCD_SF_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightRelTkIso_TrkHighPtID"] =		{"RunABCD_SF_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelTkIso_TrkHighPtID"] =		{"RunABCD_SF_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseRelTkIso_TrkHighPtID"] =		{"RunABCD_SF_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelTkIso_TrkHighPtID"] =		{"RunABCD_SF_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelTkIso_HighPtIDandIPCut"] =	{"RunABCD_SF_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseRelTkIso_HighPtIDandIPCut"] =		{"RunABCD_SF_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelTkIso_HighPtIDandIPCut"] =		{"RunABCD_SF_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["LooseRelIso_TightIDandIPCut"] =		{"RunABCD_SF_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["LooseRelIso_TightIDandIPCut"] =		{"RunABCD_SF_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["LooseRelIso_TightIDandIPCut"] =		{"RunABCD_SF_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_central["TightRelTkIso_HighPtIDandIPCut"] =	{"RunABCD_SF_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta", "TH2Lookup", "Muon_pt", "Muon_eta"};
	muon_options_stat["TightRelTkIso_HighPtIDandIPCut"] =		{"RunABCD_SF_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat", "TH2LookupErr", "Muon_pt", "Muon_eta"};
	muon_options_syst["TightRelTkIso_HighPtIDandIPCut"] =		{"RunABCD_SF_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst", "TH2LookupErr", "Muon_pt", "Muon_eta"};
      }
      else if(legacy == "UL"){
	muon_options_central["HighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["HighPtID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["HighPtID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_HighPtID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_LooseID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["MediumID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_MediumID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["MediumPromptID"] =	{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["SoftID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["SoftID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["SoftID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_SoftID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_TightID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TrkHighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TrkHighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TrkHighPtID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root", "NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	
	
	muon_options_central["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_LooseID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_LooseID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelIso_DEN_TightIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelTkIso_HighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["LooseRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_LooseRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_MediumID"] =			{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelIso_DEN_MediumID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_MediumPromptID"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelIso_DEN_MediumPromptID_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelIso_TightIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelTkIso_HighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelTkIso_HighPtIDandIPCut"] =		{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelTkIso_DEN_HighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_central["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt", "TH2Lookup", "Muon_eta", "Muon_pt"};
	muon_options_stat["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_stat", "TH2LookupErr", "Muon_eta", "Muon_pt"};
	muon_options_syst["TightRelTkIso_TrkHighPtIDandIPCut"] =	{"Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root", "NUM_TightRelTkIso_DEN_TrkHighPtIDandIPCut_abseta_pt_syst", "TH2LookupErr", "Muon_eta", "Muon_pt"};
      }
    }//era is 2018

    std::map< std::string, std::vector<std::string> > ret;
    //muon ID and ISO
    if(muon_id != ""){
      if(muon_options_central.find(muon_id) != muon_options_central.end()){
	ret["Muon_SF_ID_nom"] = muon_options_central[muon_id];
	ret["Muon_SF_ID_nom"][0] = muon_path + ret["Muon_SF_ID_nom"][0];
      }
      if(muon_options_stat.find(muon_id) != muon_options_stat.end()){
	ret["Muon_SF_ID_stat"] = muon_options_stat[muon_id];
	ret["Muon_SF_ID_stat"][0] = muon_path + ret["Muon_SF_ID_stat"][0];
      }
      if(muon_options_syst.find(muon_id) != muon_options_syst.end()){
	ret["Muon_SF_ID_syst"] = muon_options_syst[muon_id];
	ret["Muon_SF_ID_syst"][0] = muon_path + ret["Muon_SF_ID_syst"][0];
      }

    }
    if(muon_iso != ""){
      if(muon_options_central.find(muon_iso) != muon_options_central.end()){
	ret["Muon_SF_ISO_nom"] = muon_options_central[muon_iso];
	ret["Muon_SF_ISO_nom"][0] = muon_path + ret["Muon_SF_ISO_nom"][0];
      }
      if(muon_options_stat.find(muon_iso) != muon_options_stat.end()){
	ret["Muon_SF_ISO_stat"] = muon_options_stat[muon_iso];
	ret["Muon_SF_ISO_stat"][0] = muon_path + ret["Muon_SF_ISO_stat"][0];
      }
      if(muon_options_syst.find(muon_iso) != muon_options_syst.end()){
	ret["Muon_SF_ISO_syst"] = muon_options_syst[muon_iso];
	ret["Muon_SF_ISO_syst"][0] = muon_path + ret["Muon_SF_ISO_syst"][0];
      }
    }
    //Electron ID and EFF
    if(electron_id != ""){
      if(electron_options_central.find(electron_id) != electron_options_central.end()){
	ret["Electron_SF_ID_nom"] = electron_options_central[electron_id];
	ret["Electron_SF_ID_nom"][0] = electron_path + ret["Electron_SF_ID_nom"][0];
      }
      if(electron_options_uncertainty.find(electron_id) != electron_options_uncertainty.end()){
	ret["Electron_SF_ID_unc"] = electron_options_uncertainty[electron_id];
	ret["Electron_SF_ID_unc"][0] = electron_path + ret["Electron_SF_ID_unc"][0];
      }
    }
    if(electron_eff != ""){
      if(electron_options_central.find("EFF_ptBelow20") != electron_options_central.end()){
	ret["Electron_SF_EFF_ptBelow20_nom"] = electron_options_central["EFF_ptBelow20"];
	ret["Electron_SF_EFF_ptBelow20_nom"][0] = electron_path + ret["Electron_SF_EFF_ptBelow20_nom"][0];
      }
      if(electron_options_uncertainty.find("EFF_ptBelow20") != electron_options_uncertainty.end()){
	ret["Electron_SF_EFF_ptBelow20_unc"] = electron_options_uncertainty["EFF_ptBelow20"];
	ret["Electron_SF_EFF_ptBelow20_unc"][0] = electron_path + ret["Electron_SF_EFF_ptBelow20_unc"][0];
      }
      if(electron_options_central.find("EFF_ptAbove20") != electron_options_central.end()){
	ret["Electron_SF_EFF_ptAbove20_nom"] = electron_options_central["EFF_ptAbove20"];
	ret["Electron_SF_EFF_ptAbove20_nom"][0] = electron_path + ret["Electron_SF_EFF_ptAbove20_nom"][0];
      }
      if(electron_options_uncertainty.find("EFF_ptAbove20") != electron_options_uncertainty.end()){
	ret["Electron_SF_EFF_ptAbove20_unc"] = electron_options_uncertainty["EFF_ptAbove20"];
	ret["Electron_SF_EFF_ptAbove20_unc"][0] = electron_path + ret["Electron_SF_EFF_ptAbove20_unc"][0];
      }
    }

    //Load btag SFs for each process and systematic specified
    if(btag_top_path != ""){
      for(std::vector<std::string>::iterator proc_iter = btag_process_names.begin(); proc_iter != btag_process_names.end(); ++proc_iter){
	for(std::vector<std::string>::iterator syst_iter = btag_systematic_names.begin(); syst_iter != btag_systematic_names.end(); ++syst_iter){
	  std::string btag_key, syst_name;
	  syst_name = *syst_iter;
	  if(strncmp(syst_name.c_str(), "$NOMINAL", 8) == 0) syst_name = "nom";
	  if(btag_use_aggregate)btag_key = "Aggregate";
	  else btag_key = era + "___" + static_cast<std::string>(*proc_iter) + "_";
	  
	  if(btag_use_HT_only) btag_key += "1DX";
	  if(btag_use_nJet_only) btag_key += "1DY";
	  btag_key += "___" + syst_name;
	  std::cout << "Btag key formed: " << btag_key << std::endl;
	  ret["btag___" + era + "___" + static_cast<std::string>(*proc_iter) + "___" + syst_name] = {btag_top_path + "BTaggingYields.root", 
												     btag_key, "TH2Lookup", 
												     "HT__" + syst_name, 
												     "nFTAJet__" + syst_name};
	}
      }
    }
    return ret;
  }


  // std::pair< ROOT::RDF::RNode, std::vector<LUT*> > AddLeptonSF(ROOT::RDF::RNode df, std::string_view era, std::map< std::string, std::vector<std::string> > idmap){
  ROOT::RDF::RNode AddLeptonSF(ROOT::RDF::RNode df, std::string era, std::string processname,
			       std::shared_ptr< std::vector<LUT*> > veclut, std::map< std::string, std::vector<std::string> > correctormap){
    // for(std::vector<string>::const_iterator req_iter = requiredLUTs.begin(); req_iter != requiredLUTs.end(); ++ req_iter){
    //   if((*veclut)[0].find(*req_iter) == (*veclut)[0].end()){ std::cout << "Required map not found: " << *req_iter << std::endl; }
    //   else {std::cout << "Required map found: " << *req_iter << std::endl;}
    // }
    // auto vGen = [&](int len) {
    //   RVec<double> v(len);
    //   std::transform(v.begin(), v.end(), v.begin(), unifGen);
    //   return v;
    // };
    // RDataFrame d(1024);
    // auto d0 = d.Define("len", []() { return (int)gRandom->Uniform(0, 16); })
    //   .Define("x", vGen, {"len"})
    //   .Define("y", vGen, {"len"});
    // rdf2 = rdf.Define("Muon_SF_ID_altnom", "ROOT::VecOps::RVec<double> ret = {}; "\
    //               "for(int i=0; i < Muon_pt.size(); ++i) {"\
    //               "ret.push_back(testLUT->TH2Lookup(\"TightRelIso/MediumID\", Muon_pt[i], abs(Muon_eta[i])));"\
    //               "}"\
    //               "return ret;"
    ROOT::RDF::RNode ret = df;
    auto branches = ret.GetColumnNames();
    Bool_t low_electron_eff = false;
    Bool_t high_electron_eff = false;
    Bool_t composite_electron_eff_defined = false;

    for(std::map< std::string, std::vector<std::string> >::iterator cm_iter = correctormap.begin(); cm_iter != correctormap.end(); ++cm_iter){
      std::string branch_and_key, lookup_type;
      std::vector<std::string> arg_list = {};

      branch_and_key = cm_iter->first;

      //skip branches that are already defined
      Bool_t already_defined = false;
      for(int bi = 0; bi < branches.size(); ++bi){
	if(branch_and_key == branches.at(bi)) already_defined = true;
	if(!composite_electron_eff_defined && branches.at(bi) == "Electron_SF_EFF_nom") composite_electron_eff_defined = true;
      }
      if(already_defined){
	std::cout << "Branch " << branch_and_key << " already defined, skipping." << std::endl;
	continue;
      }

      //skip correctors that are not starting with Muon or Electron
      if(std::strncmp(branch_and_key.c_str(), "Muon", 4) != 0 || std::strncmp(branch_and_key.c_str(), "Electron", 8) != 0){
	std::cout << "AddLeptonSF() skipping non-Electron and non-Muon branch definitions" << std::endl;
	continue;
      }

      //check if we should compose the overall electron efficiency scale factor, only after skipping branches that are already defined and don't need a composition
      if(branch_and_key == "Electron_SF_EFF_ptBelow20_nom") low_electron_eff = true;
      if(branch_and_key == "Electron_SF_EFF_ptAbove20_nom") high_electron_eff = true;


      //store the argument list in a vector
      for(int i = 0; i < (cm_iter->second).size(); ++i){
	if(i == 2) lookup_type = cm_iter->second[i];
	else if(i > 2) arg_list.push_back(cm_iter->second[i]);
	// std::cout << cm_iter->second[i] << " ";
      }
      if(lookup_type == "TH2Lookup"){
	if(arg_list[0] == "Muon_eta" || arg_list[0] == "Muon_pt"){
	  auto slottedLookup = [veclut, branch_and_key](int slot, ROOT::VecOps::RVec<float> X, ROOT::VecOps::RVec<float> Y){
	    ROOT::VecOps::RVec<float> rvec_return = {};
	    for(int li=0; li < X.size(); ++li) {
	      rvec_return.push_back((*veclut)[slot]->TH2Lookup(branch_and_key, fabs(X[li]), fabs(Y[li])));
	    }
	    return rvec_return;
	  };
	  ret = ret.DefineSlot(branch_and_key, slottedLookup, arg_list);
	}
	else if(arg_list[0] == "Electron_eta" || arg_list[0] == "Electron_pt"){
	  auto slottedLookup = [veclut, branch_and_key](int slot, ROOT::VecOps::RVec<float> X, ROOT::VecOps::RVec<float> Y){
	    ROOT::VecOps::RVec<float> rvec_return = {};
	    for(int li=0; li < X.size(); ++li) {
	      rvec_return.push_back((*veclut)[slot]->TH2Lookup(branch_and_key, X[li], Y[li]));
		}
	    return rvec_return;
	  };
	  ret = ret.DefineSlot(branch_and_key, slottedLookup, arg_list);
	}
	else std::cout << "Unhandled type in AddLeptonSF()" << std::endl;
      }
      else if(lookup_type == "TH2LookupErr"){
	if(arg_list[0] == "Muon_eta" || arg_list[0] == "Muon_pt"){
	  auto slottedLookup = [veclut, branch_and_key](int slot, ROOT::VecOps::RVec<float> X, ROOT::VecOps::RVec<float> Y){
	    ROOT::VecOps::RVec<float> rvec_return = {};
	    for(int li=0; li < X.size(); ++li) {
	      rvec_return.push_back((*veclut)[slot]->TH2LookupErr(branch_and_key, fabs(X[li]), fabs(Y[li])));
		}
	    return rvec_return;
	  };
	  ret = ret.DefineSlot(branch_and_key, slottedLookup, arg_list);
	}
	else if(arg_list[0] == "Electron_eta" || arg_list[0] == "Electron_pt"){
	  auto slottedLookup = [veclut, branch_and_key](int slot, ROOT::VecOps::RVec<float> X, ROOT::VecOps::RVec<float> Y){
	    ROOT::VecOps::RVec<float> rvec_return = {};
	    for(int li=0; li < X.size(); ++li) {
	      rvec_return.push_back((*veclut)[slot]->TH2LookupErr(branch_and_key, X[li], Y[li]));
		}
	    return rvec_return;
	  };
	  ret = ret.DefineSlot(branch_and_key, slottedLookup, arg_list);
	}
	else std::cout << "Unhandled type in AddLeptonSF()" << std::endl;
      }
    }
    if(low_electron_eff && high_electron_eff){
      // if(!composite_electron_eff_defined){
      if(true){
	ret = ret.DefineSlot("Electron_SF_EFF_nom", 
			     [](int slot, ROOT::VecOps::RVec<float> low_eff,  ROOT::VecOps::RVec<float> high_eff,  ROOT::VecOps::RVec<float> pt){
			       ROOT::VecOps::RVec<float> rvec_return = {};
			       for(int pi=0; pi < pt.size(); ++pi) {
				 rvec_return.push_back((pt.at(pi) >= 20.0 ? high_eff.at(pi) : low_eff.at(pi)));
			       }
			       return rvec_return;
			     },
			     {"Electron_SF_EFF_ptBelow20_nom", "Electron_SF_EFF_ptAbove20_nom", "Electron_pt"});
	ret = ret.DefineSlot("Electron_SF_EFF_unc", 
			     [](int slot, ROOT::VecOps::RVec<float> low_eff,  ROOT::VecOps::RVec<float> high_eff,  ROOT::VecOps::RVec<float> pt){
			       ROOT::VecOps::RVec<float> rvec_return = {};
			       for(int pi=0; pi < pt.size(); ++pi) {
				 rvec_return.push_back((pt.at(pi) >= 20.0 ? high_eff.at(pi) : low_eff.at(pi)));
			       }
			       return rvec_return;
			     },
			     {"Electron_SF_EFF_ptBelow20_unc", "Electron_SF_EFF_ptAbove20_unc", "Electron_pt"});
      }
      else std::cout << "Branch Electron_SF_EFF_nom already defined, skipping composition" << std::endl;
    }
    return ret;
  }
  ROOT::RDF::RNode AddBTaggingYieldRenormalization(ROOT::RDF::RNode df, std::string era, std::string processname, 
						   std::shared_ptr< std::vector<LUT*> > veclut, std::map< std::string, std::vector<std::string> > correctormap){
    ROOT::RDF::RNode ret = df;
    auto branches = ret.GetColumnNames();
    std::string expected_corrector_start = "btag___" + era + "___" + processname + "___";

    Bool_t low_electron_eff = false;
    Bool_t high_electron_eff = false;
    Bool_t composite_electron_eff_defined = false;

    for(std::map< std::string, std::vector<std::string> >::iterator cm_iter = correctormap.begin(); cm_iter != correctormap.end(); ++cm_iter){
      std::string corrector_key, btag_final_weight, btag_sf_product, lookup_type, syst_postfix;
      std::vector<std::string> arg_list = {};

      //key is not precisely the branch for btag corrections, since we need individual ones for each process!
      corrector_key = cm_iter->first;

      //store the argument list in a vector
      for(int i = 0; i < (cm_iter->second).size(); ++i){
	if(i == 2) lookup_type = cm_iter->second[i];
	else if(i > 2) arg_list.push_back(cm_iter->second[i]);
	// std::cout << cm_iter->second[i] << " ";
      }

      //skip correctors that are not starting with btag___<era>___<process_name>
      if(std::strncmp(corrector_key.c_str(), expected_corrector_start.c_str(), expected_corrector_start.length()) != 0){
	std::cout << "AddBTaggingYieldRenormalization() skipping non-relavant correction " << corrector_key << std::endl;
	continue;
      }

      //determine the systematic postfix, then define the final btag branch weight name, and the required input branch btag_sf_product, appending the last to the argument list
      syst_postfix = corrector_key.substr(expected_corrector_start.length(), corrector_key.length() - expected_corrector_start.length());
      std::cout << "syst_postfix: " << syst_postfix << std::endl;
      btag_final_weight = "alt_pwgt_btag___" + syst_postfix;
      btag_sf_product = "btagSFProduct___" + syst_postfix;
      arg_list.push_back(btag_sf_product);

      //skip branches that are already defined
      Bool_t already_defined = false;
      for(int bi = 0; bi < branches.size(); ++bi){
	if(btag_final_weight == branches.at(bi)) already_defined = true;
      }
      if(already_defined){
	std::cout << "Branch " << btag_final_weight << " already defined, skipping." << std::endl;
	continue;
      }

      if(lookup_type == "TH1Lookup"){
	auto slottedLookup = [veclut, corrector_key](int slot, float X, float input_btag_sf_product){
	  return input_btag_sf_product * (*veclut)[slot]->TH1Lookup(corrector_key, X);
	};
	ret = ret.DefineSlot(corrector_key, slottedLookup, arg_list);

      }
      else if(lookup_type == "TH2Lookup"){
	auto slottedLookup = [veclut, corrector_key](int slot, float X, float Y, float input_btag_sf_product){
	  return input_btag_sf_product * (*veclut)[slot]->TH2Lookup(corrector_key, X, Y);
	};
	ret = ret.DefineSlot(corrector_key, slottedLookup, arg_list);
      }
      else if(lookup_type == "TH3Lookup"){
	auto slottedLookup = [veclut, corrector_key](int slot, float X, float Y, float Z, float input_btag_sf_product){
	  return input_btag_sf_product * (*veclut)[slot]->TH3Lookup(corrector_key, X, Y, Z);
	};
	ret = ret.DefineSlot(corrector_key, slottedLookup, arg_list);
      }
      else std::cout << "Unhandled type in AddBTaggingYieldRenormalization()" << std::endl;
    }
    return ret;
  }
  template <typename T>
  ROOT::RDF::RResultPtr<T> bookLazySnapshot(ROOT::RDF::RNode df, std::string_view treename, std::string_view filename, 
			const ROOT::Detail::RDF::ColumnNames_t columnList, std::string_view mode = "RECREATE"){
    //ROOT::kZLIB //faster read speed, but less compression than LZMA. //==1L
    //ROOT::kLZMA //highest ratio, very slow decompression //==2L
    //ROOT::kLZ4 //fastest read speed for decent compression ratio //==4L
    //ROOT::kZSTD //unknown performance //==5L
    //ROOT::RDF::RSnapshotOptions(std::string_view mode, ECAlgo comprAlgo, int comprLevel, int autoFlush, int splitLevel, bool lazy, bool overwriteIfExists=false); 
    auto sopt = ROOT::RDF::RSnapshotOptions(mode, ROOT::kLZ4, 6, 0, 99, true); //, true); // but overwrite is exclusive to 6.22 + version
    //ROOT::RDF::RInterface::Snapshot ( std::string_view  treename, std::string_view  filename, const ColumnNames_t &  columnList, const RSnapshotOptions &  options = RSnapshotOptions())
    // sopt.fLazy = false;
    std::cout << "filename = " << filename << " mode = " << sopt.fMode << " lazy = " << sopt.fLazy << std::endl;
    // auto ret = df.Snapshot(treename, filename, columnList, sopt);
    // return ret;
    return sopt;
  }
  ROOT::RDF::RSnapshotOptions getOption(std::string_view mode = "RECREATE"){
    std::cout << ROOT::kLZMA
	      << ROOT::kLZ4 
	      << ROOT::kZSTD
	      << ROOT::kZLIB
	      << std::endl;

    auto sopt = ROOT::RDF::RSnapshotOptions(mode, ROOT::kLZ4, 6, 0, 99, true); //, true); // but overwrite is exclusive to 6.22 + version
    return sopt;
  }
  int packEventId(int datasetId, int campaignId, int genTtbarId = -1, int ttbarNGenJet = -1, double ttbarGenHT = -1, int otherPhaseSpaceID = -1){
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
  std::map<std::string, std::string> unpackEventId(int packedEventId, double genWeight, double luminosity = -1){
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

  std::vector<int> unpackGenTtbarId(int genTtbarId){
  // Implementation:
  //   The classification scheme returns an ID per event, and works as follows:
     
  //   All jets in the following need to be in the acceptance as given by the config parameters |eta|, pt.
  //    A c jet must contain at least one c hadron and should contain no b hadrons
     
  //   First, b jets from top are identified, i.e. jets containing a b hadron from t->b decay
  //   They are encoded in the ID as numberOfBjetsFromTop*100, i.e.
  //   0xx: no b jets from top in acceptance
  //   1xx: 1 b jet from top in acceptance
  //   2xx: both b jets from top in acceptance
     
  //   Then, b jets from W are identified, i.e. jets containing a b hadron from W->b decay
  //   They are encoded in the ID as numberOfBjetsFromW*1000, i.e.
  //   0xxx: no b jets from W in acceptance
  //   1xxx: 1 b jet from W in acceptance
  //   2xxx: 2 b jets from W in acceptance
     
  //   Then, c jets from W are identified, i.e. jets containing a c hadron from W->c decay, but no b hadrons
  //   They are encoded in the ID as numberOfCjetsFromW*10000, i.e.
  //   0xxxx: no c jets from W in acceptance
  //   1xxxx: 1 c jet from W in acceptance
  //   2xxxx: 2 c jets from W in acceptance

  //   From the remaining jets, the ID is formed based on the additional b jets (IDs x5x) and c jets (IDs x4x) in the following order:
  //   x55: at least 2 additional b jets with at least two of them having >= 2 b hadrons in each
  //   x54: at least 2 additional b jets with one of them having >= 2 b hadrons, the others having =1 b hadron
  //   x53: at least 2 additional b jets with all having =1 b hadron
  //   x52: exactly 1 additional b jet having >=2 b hadrons
  //   x51: exactly 1 additional b jet having =1 b hadron
  //   x45: at least 2 additional c jets with at least two of them having >= 2 c hadrons in each
  //   x44: at least 2 additional c jets with one of them having >= 2 c hadrons, the others having =1 c hadron
  //   x43: at least 2 additional c jets with all having =1 c hadron
  //   x42: exactly 1 additional c jet having >=2 c hadrons
  //   x41: exactly 1 additional c jet having =1 c hadron
  //   x00: No additional b or c jet, i.e. only light flavour jets or no additional jets
    std::vector<int> jetTypes;
    int x5 = (int) (genTtbarId/10000);
    int x4 = (int) (genTtbarId - 10000*x5)/1000;
    int x3 = (int) (genTtbarId - 10000*x5 - 1000*x4)/100;
    int x21 = (int) (genTtbarId - 10000*x5 - 1000*x4 - 100*x3);

    switch (x21) {
    case 55: 
      jetTypes.push_back(2); //number of minimal additional b jets 
      jetTypes.push_back(2); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(0); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(0); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(0); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(0); //number of minimal additional c jets with 1 C hadron
      break;
    case 54: 
      jetTypes.push_back(2); //number of minimal additional b jets 
      jetTypes.push_back(1); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(1); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(0); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(0); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(0); //number of minimal additional c jets with 1 C hadron
      break;
    case 53: 
      jetTypes.push_back(2); //number of minimal additional b jets 
      jetTypes.push_back(0); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(2); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(0); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(0); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(0); //number of minimal additional c jets with 1 C hadron
      break;
    case 52: 
      jetTypes.push_back(1); //number of minimal additional b jets 
      jetTypes.push_back(1); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(0); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(0); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(0); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(0); //number of minimal additional c jets with 1 C hadron
      break;
    case 51: 
      jetTypes.push_back(1); //number of minimal additional b jets 
      jetTypes.push_back(0); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(1); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(0); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(0); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(0); //number of minimal additional c jets with 1 C hadron
      break;
    case 45: 
      jetTypes.push_back(0); //number of minimal additional b jets 
      jetTypes.push_back(0); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(0); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(2); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(2); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(0); //number of minimal additional c jets with 1 C hadron
      break;
    case 44: 
      jetTypes.push_back(0); //number of minimal additional b jets 
      jetTypes.push_back(0); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(0); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(2); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(1); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(1); //number of minimal additional c jets with 1 C hadron
      break;
    case 43: 
      jetTypes.push_back(0); //number of minimal additional b jets 
      jetTypes.push_back(0); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(0); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(2); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(0); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(2); //number of minimal additional c jets with 1 C hadron
      break;
    case 42: 
      jetTypes.push_back(0); //number of minimal additional b jets 
      jetTypes.push_back(0); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(0); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(1); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(1); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(0); //number of minimal additional c jets with 1 C hadron
      break;
    case 41: 
      jetTypes.push_back(0); //number of minimal additional b jets 
      jetTypes.push_back(0); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(0); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(1); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(0); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(1); //number of minimal additional c jets with 1 C hadron
      break;
    default: 
      jetTypes.push_back(0); //number of minimal additional b jets 
      jetTypes.push_back(0); //number of minimal additional b jets with 2+ B hadrons
      jetTypes.push_back(0); //number of minimal additional b jets with 1 B hadron
      jetTypes.push_back(0); //number of minimal additional c jets with precedence to b jets
      jetTypes.push_back(0); //number of minimal additional c jets with 2+ C hadrons
      jetTypes.push_back(0); //number of minimal additional c jets with 1 C hadron
      break;
    }

    jetTypes.push_back(x3); //store number of b jets from t
    jetTypes.push_back(x4); //store number of b jets from W
    jetTypes.push_back(x5); //Store number of c jets from W

    //return vector{additional b jets, double-B b jets, single-B b jets, additional c jets (if no b jets),
    // double-C c jets, single-C c jets, minimal t->b jets in acceptance, minimal W->b jets in acceptance, 
    //minimal W-> c jets in acceptance
    assert (jetTypes.size() == 9);
    return jetTypes;
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
  enum TheRunEra{y2016B,y2016C,y2016D,y2016E,y2016F,y2016G,y2016H,y2017B,y2017C,y2017D,y2017E,y2017F,y2018A,y2018B,y2018C,y2018D,y2016MC,y2017MC,y2018MC};  
  std::pair<double,double> METXYCorr(double uncormet, double uncormet_phi, int runnb, int year, bool isData, int npv){

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
