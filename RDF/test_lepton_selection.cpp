#ifndef FOURTOP_LEPTON
#define FOURTOP_LEPTON

//#include <boost>
#include <cstring>
#include <stdio.h>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
//#include <TObject.h>
#include <TMath.h>
#include "ROOT/RDF/RInterface.hxx"
#include "ROOT/RVec.hxx"

//const and by reference means no copies, no pointer handling, etc.
using VecF_t = const ROOT::RVec<float>&;
using VecI_t = const ROOT::RVec<int>&;
// class myFunctorClass
// {
// public:
//   myFunctorClass (int x) : _x( x ) {}
//   int operator() (int y) { return _x + y; }
// private:
//   int _id;
//   bool _inviso
// };
class preselectElectrons
{
public:
  preselectElectrons(int ElectronID, bool invertIsolation) : _ElectronID(ElectronID), _invertIsolation(invertIsolation) {}
  ROOT::RVec<int> operator()(VecF_t Electron_pt, VecF_t Electron_eta, VecF_t Electron_phi,  
			     VecF_t Electron_ip3d, VecF_t Electron_dz,  VecI_t Electron_charge,
			     VecI_t Electron_cutBased){
    ROOT::RVec<int> Electron_premask = Electron_pt > 15 &&
      (
       (abs(Electron_eta) < 1.4442 && abs(Electron_ip3d) < 0.05 && abs(Electron_dz) < 0.1) 
       || 
       (abs(Electron_eta) > 1.5660 && abs(Electron_eta) < 2.5 && abs(Electron_ip3d) < 0.10 && abs(Electron_dz) < 0.2)
       );
    if(_invertIsolation){
      std::cout << "iso inversion not implemented" << std::endl;
    }
    else{
      Electron_premask = Electron_premask && Electron_cutBased >= _ElectronID;
    }
    return Electron_premask;
  }
private:
  int _ElectronID;
  bool _invertIsolation;
};
class preselectMuons
{
public:
  preselectMuons (int MuonID, bool invertIsolation) : _MuonID(MuonID), _invertIsolation(invertIsolation) {}
  ROOT::RVec<int> operator()(VecF_t Muon_pt, VecF_t Muon_eta, VecF_t Muon_phi, 
			     VecF_t Muon_ip3d, VecF_t Muon_dz, VecI_t Muon_charge, 
			     VecI_t Muon_looseId, VecI_t Muon_mediumId, VecI_t Muon_tightId, VecI_t Muon_pfIsoId){
    ROOT::RVec<int> Muon_premask = Muon_pt > 15 && abs(Muon_eta) < 2.4 && abs(Muon_ip3d) < 0.10 && abs(Muon_dz) < 0.02;
    if(_MuonID == 2){//loose, match Electrons for this number
      Muon_premask = Muon_premask && Muon_looseId == true;
    }
    else if(_MuonID == 3){
      Muon_premask = Muon_premask && Muon_mediumId == true;
    }
    else if(_MuonID == 4){
      Muon_premask = Muon_premask && Muon_tightId == true;
    }
    if(_invertIsolation){
      Muon_premask = Muon_premask && Muon_pfIsoId >= 4;
    }
    else{
      Muon_premask = Muon_premask && Muon_pfIsoId < 3;
    }
    return Muon_premask;
  }
private:
  int _MuonID;
  bool _invertIsolation;
};

ROOT::RDF::RNode applyTriggerSelection(ROOT::RDF::RNode df, std::string era, std::string triggerChannel, std::string decayChannel, 
				       bool isData, std::string subera, std::string ElectronID, std::string MuonID, bool verbose=false){
  std::map< std::string, std::vector<int> > leptonIDs;
  std::map< std::string, std::vector<double> > triggers;
  std::map< std::string, int> triggerBit;
  std::vector<std::string> vetoTriggers;
  bool cutLowMassResonances = false;
  if(decayChannel == "ElEl" || decayChannel == "MuMu"){
    cutLowMassResonances = true;
  }
  if(isData){
    assert (subera == "A" || subera == "B" || subera == "C" || subera == "D" || subera == "E" || subera == "F");
  }
  if(era == "2017"){
    //ElMu
    triggerBit["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = 14;
    triggerBit["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = 13;
    //MuMu
    triggerBit["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"] = 12;
    triggerBit["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"] = 11;
    //ElEl
    triggerBit["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = 9;
    //Mu
    triggerBit["HLT_IsoMu27"] = 7;
    //El
    triggerBit["HLT_Ele35_WPTight_Gsf"] = 6;
    //MET
    triggerBit["HLT_PFMET200_NotCleaned"] = 3;
    triggerBit["HLT_PFMET200_HBHECleaned"] = 2;
    triggerBit["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = 1;
  }
  else if(era == "2018"){
    //ElMu
    triggerBit["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = 14; // why the reversal? Maa ika
    triggerBit["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = 12;
    //MuMu
    triggerBit["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"] = 11;
    //ElEl
    triggerBit["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = 9;
    //Mu
    triggerBit["HLT_IsoMu24"] = 8;
    //El
    triggerBit["HLT_Ele32_WPTight_Gsf"] = 4;
    //MET
    triggerBit["HLT_PFMET200_NotCleaned"] = 3;
    triggerBit["HLT_PFMET200_HBHECleaned"] = 2;
    triggerBit["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = 1;
  }
  if(decayChannel == "ElMu"){
    if(era == "2017"){
      if(triggerChannel == "ElMu"){
	//DONE
	//always paired with leptonIDs {13, 11}
	vetoTriggers = {}; //ElMu has highest trigger precedence
	leptonIDs["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = {13, 11}; //BCDEF
	triggers["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = {25.0, 15.0}; //BCDEF
	leptonIDs["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = {13, 11}; //BCDEF
	triggers["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = {15.0, 25.0}; //BCDEF
      }
      else if(triggerChannel == "Mu"){
	//DONE
	//always paired with leptonIDs {13, 11}
	vetoTriggers = {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"}; //Mu has 4th highest trigger precedence
	if(!isData || subera == "B") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8");
	leptonIDs["HLT_IsoMu27"] = {13, 11};
	triggers["HLT_IsoMu27"] = {30.0, 15.0}; //BCDEF
      }
      else if(triggerChannel == "El"){
	//DONE
	//always paired with leptonIDs {13, 11}
	vetoTriggers = {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", 
			"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_IsoMu27"}; //El has 5th highest trigger precedence
	if(!isData || subera == "B") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8");
	leptonIDs["HLT_Ele35_WPTight_Gsf"] = {13, 11};
	triggers["HLT_Ele35_WPTight_Gsf"] = {15.0, 38.0}; //BCDEF
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	leptonIDs["HLT_PFMET200_NotCleaned"] = {13, 11};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMET200_HBHECleaned"] = {13, 11};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {13, 11};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	vetoTriggers = {};
	leptonIDs["#LOGICERROR"] = {};
	triggers["#LOGICERROR"] = {};
      }
    }
    else if(era == "2018"){
      if(triggerChannel == "ElMu"){
	//DONE
	//always paired with leptonIDs {13, 11}
	vetoTriggers = {}; //ElMu has highest trigger precedence
	triggers["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = {15.0, 25.0}; //ABCD
	leptonIDs["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = {13, 11}; //ABCD
	triggers["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = {25.0, 15.0}; //ABCD
	leptonIDs["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = {13, 11}; //ABCD
      }
      else if(triggerChannel == "Mu"){
	//DONE
	vetoTriggers = {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"}; //Mu has 4th highest trigger precedence
	leptonIDs["HLT_IsoMu24"] = {13, 11}; //ABCD
	triggers["HLT_IsoMu24"] = {27.0, 15.0}; //ABCD
      }
      else if(triggerChannel == "El"){
	//DONE
	vetoTriggers = {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_IsoMu24"}; //El has 5th highest trigger precedence
	leptonIDs["HLT_Ele32_WPTight_Gsf"] = {13, 11};
	triggers["HLT_Ele32_WPTight_Gsf"] = {15.0, 35.0}; // ABCD
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	leptonIDs["HLT_PFMET200_NotCleaned"] = {13, 11};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMET200_HBHECleaned"] = {13, 11};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {13, 11};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	vetoTriggers = {};
	leptonIDs["#LOGICERROR"] = {};
	triggers["#LOGICERROR"] = {};
      }
    }
  }
  else if (decayChannel == "MuMu"){
    if(era == "2017"){
      if(triggerChannel == "MuMu"){
	//DONE
	vetoTriggers = {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"}; //MuMu has 2nd highest trigger precedence
	if(!isData || subera == "B"){
	  leptonIDs["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"] = {13, 13}; //B
	  triggers["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"] = {25.0, 15.0}; //B
	}
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F"){ //NO ELSE IF, must have both for MC
	  leptonIDs["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"] = {13, 13}; //CDEF
	  triggers["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"] = {25.0, 15.0}; //CDEF
	}
      }
      else if(triggerChannel == "Mu"){
	//DONE
	vetoTriggers = {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"}; //Mu has 4th highest trigger precedence
	if(!isData || subera == "B") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8");
	leptonIDs["HLT_IsoMu27"] = {13, 13};
	triggers["HLT_IsoMu27"] = {30.0, 15.0}; //BCDEF
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	leptonIDs["HLT_PFMET200_NotCleaned"] = {13, 13};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMET200_HBHECleaned"] = {13, 13};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {13, 13};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	//DONE
	vetoTriggers = {};
	leptonIDs["#LOGICERROR"] = {};
	triggers["#LOGICERROR"] = {};
      }
    }
    else if(era == "2018"){
      if(triggerChannel == "MuMu"){
	//FIXME
	vetoTriggers = {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"}; //Mu has 4th highest trigger precedence
	triggers["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"] = {25.0, 15.0}; //ABCD
      }
      else if(triggerChannel == "Mu"){
	//DONE
	vetoTriggers = {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"}; //Mu has 4th highest trigger precedence
	leptonIDs["HLT_IsoMu24"] = {13, 13}; //ABCD
	triggers["HLT_IsoMu24"] = {27.0, 15.0}; //ABCD
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	leptonIDs["HLT_PFMET200_NotCleaned"] = {13, 13};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMET200_HBHECleaned"] = {13, 13};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {13, 13};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	vetoTriggers = {};
	leptonIDs["#LOGICERROR"] = {};
	triggers["#LOGICERROR"] = {};
      }
    }
  }
  else if (decayChannel == "ElEl"){
    if(era == "2017"){
      if(triggerChannel == "ElEl"){
	//DONE
	vetoTriggers = {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"}; //Mu has 4th highest trigger precedence
	if(!isData || subera == "B") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8");
	leptonIDs["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = {11, 11};
	triggers["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = {25.0, 15.0}; //BCDEF
      }
      else if(triggerChannel == "El"){
	//DONE
	vetoTriggers = {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", 
			"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_IsoMu27"}; //El has 5th highest trigger precedence
	if(!isData || subera == "B") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8");
	leptonIDs["HLT_Ele35_WPTight_Gsf"] = {11, 11};
	triggers["HLT_Ele35_WPTight_Gsf"] = {38.0, 15.0}; //BCDEF
	
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	leptonIDs["HLT_PFMET200_NotCleaned"] = {11, 11};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMET200_HBHECleaned"] = {11, 11};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {11, 11};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	vetoTriggers = {};
	leptonIDs["#LOGICERROR"] = {};
	triggers["#LOGICERROR"] = {};
      }
    }
    else if(era == "2018"){
      if(triggerChannel == "ElEl"){
	//DONE
	vetoTriggers = {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"}; //ElEl has 3rd highest trigger precedence
	leptonIDs["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = {11, 11}; 
	triggers["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = {25.0, 15.0}; // ABCD
      }
      else if(triggerChannel == "El"){
	//DONE
	vetoTriggers = {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_IsoMu24"}; //El has 5th highest trigger precedence
	leptonIDs["HLT_Ele32_WPTight_Gsf"] = {11, 11}; 
	triggers["HLT_Ele32_WPTight_Gsf"] = {35.0, 15.0}; // ABCD
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	leptonIDs["HLT_PFMET200_NotCleaned"] = {11, 11};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMET200_HBHECleaned"] = {11, 11};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	leptonIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {11, 11};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	vetoTriggers = {};
	leptonIDs["#LOGICERROR"] = {};
	triggers["#LOGICERROR"] = {};
      }
    }
  } 
  
  std::cout << "Era: " << era << "   Subera: " << subera << "   isData: " << isData << "   Channel: " << decayChannel << "   triggerChannel: " << triggerChannel << std::endl;
  for(std::map< std::string, std::vector<int> >::iterator id_iter = leptonIDs.begin(); id_iter != leptonIDs.end(); ++id_iter){
    // std::cout << id_iter->first << "   " << id_iter->second << std::endl;
    std::cout << id_iter->first << "   ";
    for(int i = 0; i < triggers[id_iter->first].size(); ++i){
      std::cout << leptonIDs[id_iter->first].at(i) << "  ";
    }
    for(int i = 0; i < triggers[id_iter->first].size(); ++i){
      std::cout << triggers[id_iter->first].at(i) << "  ";
    }
    std::cout << std::endl;
  }
  // for(std::map< std::string, std::vector<double> >::iterator th_iter = triggers.begin(); th_iter != triggers.end(); ++th_iter){
  // }
  ROOT::RDF::RNode ret = df;

  int ElectronIDEnum;
  int MuonIDEnum;

  if(ElectronID == "Veto") ElectronIDEnum = 1;
  if(ElectronID == "Loose") ElectronIDEnum = 2;
  if(ElectronID == "Medium") ElectronIDEnum = 3;
  if(ElectronID == "Tight") ElectronIDEnum = 4;

  if(MuonID == "Loose") MuonIDEnum = 2;
  if(MuonID == "Medium") MuonIDEnum = 3;
  if(MuonID == "Tight") MuonIDEnum = 4;

  preselectElectrons pIsoElectrons(ElectronIDEnum, false);
  preselectMuons pIsoMuons(MuonIDEnum, false);
  ret = ret.Define("Electron_preselection", pIsoElectrons, {"Electron_pt", "Electron_eta", "Electron_phi",
	"Electron_ip3d", "Electron_dz", "Electron_charge",
	"Electron_cutBased"});
  ret = ret.Define("Muon_preselection", pIsoMuons, {"Muon_pt", "Muon_eta", "Muon_phi", 
	"Muon_ip3d", "Muon_dz", "Muon_charge", 
	"Muon_looseId", "Muon_mediumId", "Muon_tightId", "Muon_pfIsoId"});

  //filter out tertiary leptons
  ret = ret.Filter([](VecI_t Muon_preselection, VecI_t Electron_preselection){return Sum(Muon_preselection) + Sum(Electron_preselection) == 2;}, 
		   {"Muon_preselection", "Electron_preselection"}, "Veto tertiary leptons");
  //then check charge requirement
  ret = ret.Filter([](VecI_t Muon_charge, VecI_t Muon_preselection, VecI_t Electron_charge, VecI_t Electron_preselection){
      auto Lepton_charge = ROOT::VecOps::Concatenate(Muon_charge[Muon_preselection], Electron_charge[Electron_preselection]);
      if(ROOT::VecOps::Sum(Lepton_charge) == 2){
	if(Lepton_charge.at(0) * Lepton_charge.at(1) < 0)
	  return false;
	else
	  return false;
      }
      else
	return false;
    },
    {"Muon_charge", "Muon_preselection", "Electron_charge", "Electron_preselection"}, "Opposite charge leptons");
  // ret = ret.Filter([](VecI_t Muon_pdgId, VecI_t Muon_pdgId, VecI_t Muon_preselection, VecI_t Electron_charge, VecI_t Electron_preselection){
  //Goal: For events that at least have 2 isolated leptons, then check the valid trigger paths, first vetoing higher tier triggers with a filter,
  //then only using a Define to store the concurrent trigger path decisions in an int value (-1 vetoed, 0 failed, 1 passed) and the matching lepton selection masks in two additional arrays
  
  //for a quick QCD test, just filter on the valid triggers from this path
  //build the filter expression
  std::string filter_code = "return";
  auto v_first = vetoTriggers.begin();
  auto v_next_to_last = vetoTriggers.empty() ? vetoTriggers.end() : std::prev(vetoTriggers.end());
  auto v_last = vetoTriggers.end();
  if(v_first != v_last) filter_code += " (";
  for(std::vector<std::string>::iterator vt_iter = v_first; vt_iter != v_last; ++vt_iter){
    filter_code += *vt_iter + " == false";
    if(vt_iter != v_next_to_last){
      filter_code += " && ";
    }
  }
  if(v_first != v_last) filter_code += ") &&"; //We had a veto section, do an AND with the passing triggers
  filter_code += " (";
  auto first = triggers.begin();
  auto next_to_last = triggers.empty() ? triggers.end() : std::prev(triggers.end()); // in case s is empty
  auto last = triggers.end();
  for(std::map< std::string, std::vector<double> >::iterator th_iter = first; th_iter != last; ++th_iter){
    filter_code += th_iter->first + " == true";
    if(th_iter != next_to_last){
      filter_code += " || ";
    }
  }
  // if(std::strncmp(filter_code, "TH1", 3) == 0);
  filter_code += ");";
  std::cout << filter_code << std::endl;
  return ret;
  // ROOT::Detail::RDF::ColumnNames_t flags = {};
}
    


// CMuon, CElectron = Cutbased lepton selection
// vector< vector<int> > findCMuonCElectronPair(VecF_t Muon_pt, VecF_t Muon_eta, VecF_t Muon_phi, 
// 					     VecF_t Muon_ip3d, VecF_t Muon_dz, VecI_t Muon_charge, 
// 					     VecI_t Muon_passId,
// 					     VecF_t Electron_pt, VecF_t Electron_eta, VecF_t Electron_phi,  
// 					     VecF_t Electron_ip3d, VecF_t Electron_dz,  VecI_t Electron_charge,
// 					     VecI_t Electron_passId,
// 					     int LeadThresh, int SubleadThresh, int VetoThresh, int LeadId){
//   using namespace ROOT::VecOps;
//   auto Muon_premask = Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_passId == true && Muon_pfIsoId >= 4 && abs(Muon_ip3d) < 0.10 && abs(Muon_dz) < 0.02;
//   auto Muon_idx = Argsort(Muon_pt)[Muon_premask]; // max to min
//   auto Electron_premask = Electron_pt > 15 && Electron_passId == true && 
//     (
//      (abs(Electron_eta) < 1.4442 && abs(Electron_ip3d) < 0.05 && abs(Electron_dz) < 0.1) 
//      || 
//      (abs(Electron_eta) > 1.5660 && abs(Electron_eta) < 2.5 && abs(Electron_ip3d) < 0.10 && abs(Electron_dz) < 0.2)
//      );
//CMuon, CElectron = Cutbased lepton selection
// vector< vector<int> > findCMuonCElectronPair(VecF_t Muon_pt, VecF_t Muon_eta, VecF_t Muon_phi, 
// 					     VecF_t Muon_ip3d, VecF_t Muon_dz, VecI_t Muon_charge, 
// 					     VecI_t Muon_passId,
// 					     VecF_t Electron_pt, VecF_t Electron_eta, VecF_t Electron_phi,  
// 					     VecF_t Electron_ip3d, VecF_t Electron_dz,  VecI_t Electron_charge,
// 					     VecI_t Electron_passId,
// 					     int LeadThresh, int SubleadThresh, int VetoThresh, int LeadId){
//   using namespace ROOT::VecOps;
//   auto Muon_premask = Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_passId == true && Muon_pfIsoId >= 4 && abs(Muon_ip3d) < 0.10 && abs(Muon_dz) < 0.02;
//   auto Muon_idx = Argsort(Muon_pt)[Muon_premask]; // max to min
//   auto Electron_premask = Electron_pt > 15 && Electron_passId == true && 
//     (
//      (abs(Electron_eta) < 1.4442 && abs(Electron_ip3d) < 0.05 && abs(Electron_dz) < 0.1) 
//      || 
//      (abs(Electron_eta) > 1.5660 && abs(Electron_eta) < 2.5 && abs(Electron_ip3d) < 0.10 && abs(Electron_dz) < 0.2)
//      );
//   auto Electron_idx = Argsort(Electron_pt)[Electron_premask]; // min to max
//   for(int Muon_i:Muon_idx){
//     for(int Tau_i:Tau_idx){
//       if(DeltaR(Muon_eta[Muon_i], Tau_eta[Tau_i], Muon_phi[Muon_i], Tau_phi[Tau_i]) > 0.5 && Muon_charge[Muon_i] * Tau_charge[Tau_i] < 0){
// 	return {Muon_i,Tau_i};
//       }
//     }
//   }
//   return {}; // Invalid event!
// }

  // electron_options = {"Veto", "Loose", "Medium", "Tight"}; //, "MVA80noiso", "MVA80iso", "MVA90noiso", "MVA90iso"};
  // muon_options = {"LooseID", "MediumID", "TightID"}; //"TOPMVAVeryLoose", "TOPMVALoose", "TOPMVAMedium", "TOPMVATight"};

  // 	//Electrons: Very Loose (> -0.55, S=99%, B=8%), Loose (> 0.00, S=98%, B=4%), Medium (> 0.60, S=95%, B=2%), Tight (> 0.90, S=90%, B=1%) branch: Electron_mvaTOP
  // 	//Muons: Very Loose (> -0.45, S=99%, B=9%), Loose (> 0.05, S=98%, B=5%), Medium (> 0.65, S=95%, B=2%), Tight (> 0.90, S=90%, B=1%) branch: Muon_mvaTOP
  // 	if(arg_list[0] == "Muon_eta" || arg_list[0] == "Muon_pt"){
  // 	  auto slottedLookup = [veclut, branch_and_key](int slot, ROOT::VecOps::RVec<float> X, ROOT::VecOps::RVec<float> Y){
  // 	    ROOT::VecOps::RVec<float> rvec_return = {};
  // 	    for(int li=0; li < X.size(); ++li) {
  // 	      rvec_return.push_back((*veclut)[slot]->TH2Lookup(branch_and_key, fabs(X[li]), fabs(Y[li])));
  // 	    }
  // 	    return rvec_return;
  // 	  };
  // 	  ret = ret.DefineSlot(branch_and_key, slottedLookup, arg_list);
  // 	}
#endif
