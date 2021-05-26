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
#include "Math/GenVector/PtEtaPhiM4D.h"

//const and by reference means no copies, no pointer handling, etc.
using VecF_t = const ROOT::RVec<float>&;
using VecI_t = const ROOT::RVec<int>&;
using VecUC_t = const ROOT::RVec<UChar_t>&;
using VecB_t = const ROOT::RVec<bool>&;
// using VecP4_t = const ROOT::RVec<ROOT::Math::PtEtaPhiM4D<double>>&;
using VecP4_t = const ROOT::VecOps::RVec< ROOT::Math::LorentzVector< ROOT::Math::PtEtaPhiM4D<double> > >&;
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
			     VecB_t Muon_looseId, VecB_t Muon_mediumId, VecB_t Muon_tightId, VecUC_t Muon_pfIsoId){
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
      Muon_premask = Muon_premask && Muon_pfIsoId < 4;
    }
    else{
      Muon_premask = Muon_premask && Muon_pfIsoId >= 4;
    }
    return Muon_premask;
  }
private:
  int _MuonID;
  bool _invertIsolation;
};

std::pair<ROOT::RDF::RNode, ROOT::VecOps::RVec<int>> applyTriggerSelection(ROOT::RDF::RNode df, std::string era, std::string triggerChannel, std::string decayChannel, 
									   bool isData, std::string subera, std::string ElectronID, std::string MuonID, 
									   bool applyLowMassResonanceCut=true, bool invertZWindow=false, bool verbose=false){
  std::map< std::string, std::vector<int> > triggerIDs;
  std::map< std::string, ROOT::VecOps::RVec<double> > triggers;
  std::map< std::string, int> triggerBit;
  std::vector<std::string> vetoTriggers;
  ROOT::VecOps::RVec<int> decayChannelIDs = {};
  bool cutLowMassResonances = false;
  bool cutZResonance = false;
  ROOT::VecOps::RVec<int> channelTriggerBits = {};
  if(decayChannel == "ElMu"){
    decayChannelIDs = {13, 11};
  }
  else if(decayChannel == "ElEl"){
    decayChannelIDs = {11, 11};
    cutLowMassResonances = applyLowMassResonanceCut;
    cutZResonance = true;
  }
  else if(decayChannel == "MuMu"){
    decayChannelIDs = {13, 13};
    cutLowMassResonances = applyLowMassResonanceCut;
    cutZResonance = true;
  }
  std::string stringCutLowMassResonances = cutLowMassResonances ? "true" : "false";
  std::string stringCutZResonance = cutZResonance ? "true" : "false";
  std::string stringInvertZWindow = invertZWindow ? "true": "false";
  if(isData){
    assert (subera == "A" || subera == "B" || subera == "C" || subera == "D" || subera == "E" || subera == "F");
  }
  if(era == "2017"){
    //ElMu
    triggerBit["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = 14;
    triggerBit["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = 13;
    if(triggerChannel == "ElMu") channelTriggerBits = {14, 13};
    //MuMu
    triggerBit["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"] = 12;
    triggerBit["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"] = 11;
    if(triggerChannel == "MuMu") channelTriggerBits = {12, 11};
    //ElEl
    triggerBit["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = 9;
    if(triggerChannel == "ElEl") channelTriggerBits = {9};
    //Mu
    triggerBit["HLT_IsoMu27"] = 7;
    if(triggerChannel == "Mu") channelTriggerBits = {7};
    //El
    triggerBit["HLT_Ele35_WPTight_Gsf"] = 6;
    if(triggerChannel == "El") channelTriggerBits = {6};
    //MET
    triggerBit["HLT_PFMET200_NotCleaned"] = 3;
    triggerBit["HLT_PFMET200_HBHECleaned"] = 2;
    triggerBit["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = 1;
    if(triggerChannel == "MET") channelTriggerBits = {3, 2, 1};
  }
  else if(era == "2018"){
    //ElMu
    triggerBit["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = 14; // why the reversal? Maa ika
    triggerBit["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = 12;
    if(triggerChannel == "ElMu") channelTriggerBits = {14, 12};
    //MuMu
    triggerBit["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"] = 11;
    if(triggerChannel == "MuMu") channelTriggerBits = {11};
    //ElEl
    triggerBit["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = 9;
    if(triggerChannel == "ElEl") channelTriggerBits = {9};
    //Mu
    triggerBit["HLT_IsoMu24"] = 8;
    if(triggerChannel == "Mu") channelTriggerBits = {8};
    //El
    triggerBit["HLT_Ele32_WPTight_Gsf"] = 4;
    if(triggerChannel == "El") channelTriggerBits = {4};
    //MET
    triggerBit["HLT_PFMET200_NotCleaned"] = 3;
    triggerBit["HLT_PFMET200_HBHECleaned"] = 2;
    triggerBit["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = 1;
    if(triggerChannel == "MET") channelTriggerBits = {3, 2, 1};
  }
  if(decayChannel == "ElMu"){
    if(era == "2017"){
      if(triggerChannel == "ElMu"){
	//DONE
	vetoTriggers = {}; //ElMu has highest trigger precedence
	triggerIDs["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = {13, 11}; //BCDEF
	triggers["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = {25.0, 15.0}; //BCDEF
	triggerIDs["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = {13, 11}; //BCDEF
	triggers["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = {15.0, 25.0}; //BCDEF
      }
      else if(triggerChannel == "Mu"){
	//DONE
	vetoTriggers = {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"}; //Mu has 4th highest trigger precedence
	if(!isData || subera == "B") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8");
	triggerIDs["HLT_IsoMu27"] = {13};
	triggers["HLT_IsoMu27"] = {30.0, 15.0}; //BCDEF
      }
      else if(triggerChannel == "El"){
	//DONE
	vetoTriggers = {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", 
			"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_IsoMu27"}; //El has 5th highest trigger precedence
	if(!isData || subera == "B") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8");
	triggerIDs["HLT_Ele35_WPTight_Gsf"] = {11};
	triggers["HLT_Ele35_WPTight_Gsf"] = {15.0, 38.0}; //BCDEF
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	triggerIDs["HLT_PFMET200_NotCleaned"] = {};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMET200_HBHECleaned"] = {};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	vetoTriggers = {};
	triggerIDs["#LOGICERROR"] = {};
	triggers["#LOGICERROR"] = {};
      }
    }
    else if(era == "2018"){
      if(triggerChannel == "ElMu"){
	//DONE
	vetoTriggers = {}; //ElMu has highest trigger precedence
	triggers["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = {15.0, 25.0}; //ABCD
	triggerIDs["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"] = {13, 11}; //ABCD
	triggers["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = {25.0, 15.0}; //ABCD
	triggerIDs["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"] = {13, 11}; //ABCD
      }
      else if(triggerChannel == "Mu"){
	//DONE
	vetoTriggers = {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"}; //Mu has 4th highest trigger precedence
	triggerIDs["HLT_IsoMu24"] = {13}; //ABCD
	triggers["HLT_IsoMu24"] = {27.0, 15.0}; //ABCD
      }
      else if(triggerChannel == "El"){
	//DONE
	vetoTriggers = {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_IsoMu24"}; //El has 5th highest trigger precedence
	triggerIDs["HLT_Ele32_WPTight_Gsf"] = {11};
	triggers["HLT_Ele32_WPTight_Gsf"] = {15.0, 35.0}; // ABCD
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	triggerIDs["HLT_PFMET200_NotCleaned"] = {};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMET200_HBHECleaned"] = {};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	vetoTriggers = {};
	triggerIDs["#LOGICERROR"] = {};
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
	  triggerIDs["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"] = {13, 13}; //B
	  triggers["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"] = {25.0, 15.0}; //B
	}
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F"){ //NO ELSE IF, must have both for MC
	  triggerIDs["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"] = {13, 13}; //CDEF
	  triggers["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"] = {25.0, 15.0}; //CDEF
	}
      }
      else if(triggerChannel == "Mu"){
	//DONE
	vetoTriggers = {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"}; //Mu has 4th highest trigger precedence
	if(!isData || subera == "B") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8");
	triggerIDs["HLT_IsoMu27"] = {13};
	triggers["HLT_IsoMu27"] = {30.0, 15.0}; //BCDEF
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	triggerIDs["HLT_PFMET200_NotCleaned"] = {};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMET200_HBHECleaned"] = {};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	//DONE
	vetoTriggers = {};
	triggerIDs["#LOGICERROR"] = {};
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
	triggerIDs["HLT_IsoMu24"] = {13}; //ABCD
	triggers["HLT_IsoMu24"] = {27.0, 15.0}; //ABCD
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	triggerIDs["HLT_PFMET200_NotCleaned"] = {};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMET200_HBHECleaned"] = {};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	vetoTriggers = {};
	triggerIDs["#LOGICERROR"] = {};
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
	triggerIDs["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = {11, 11};
	triggers["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = {25.0, 15.0}; //BCDEF
      }
      else if(triggerChannel == "El"){
	//DONE
	vetoTriggers = {"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", 
			"HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_IsoMu27"}; //El has 5th highest trigger precedence
	if(!isData || subera == "B") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ");
	if(!isData || subera == "C" || subera == "D" || subera == "E" || subera == "F") vetoTriggers.push_back("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8");
	triggerIDs["HLT_Ele35_WPTight_Gsf"] = {11};
	triggers["HLT_Ele35_WPTight_Gsf"] = {38.0, 15.0}; //BCDEF
	
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	triggerIDs["HLT_PFMET200_NotCleaned"] = {};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMET200_HBHECleaned"] = {};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	vetoTriggers = {};
	triggerIDs["#LOGICERROR"] = {};
	triggers["#LOGICERROR"] = {};
      }
    }
    else if(era == "2018"){
      if(triggerChannel == "ElEl"){
	//DONE
	vetoTriggers = {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"}; //ElEl has 3rd highest trigger precedence
	triggerIDs["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = {11, 11}; 
	triggers["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"] = {25.0, 15.0}; // ABCD
      }
      else if(triggerChannel == "El"){
	//DONE
	vetoTriggers = {"HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
			"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_IsoMu24"}; //El has 5th highest trigger precedence
	triggerIDs["HLT_Ele32_WPTight_Gsf"] = {11}; 
	triggers["HLT_Ele32_WPTight_Gsf"] = {35.0, 15.0}; // ABCD
      }
      else if(triggerChannel == "MET"){
	//DONE
	vetoTriggers = {}; //Don't veto events for trigger studies, but should only pull from the MET datastream...
	triggerIDs["HLT_PFMET200_NotCleaned"] = {};
	triggers["HLT_PFMET200_NotCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMET200_HBHECleaned"] = {};
	triggers["HLT_PFMET200_HBHECleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
	triggerIDs["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {};
	triggers["HLT_PFMETTypeOne200_HBHE_BeamHaloCleaned"] = {15.0, 15.0}; //impose asymmetric cut somewhere else
      }
      else{
	vetoTriggers = {};
	triggerIDs["#LOGICERROR"] = {};
	triggers["#LOGICERROR"] = {};
      }
    }
  } 
  
  std::cout << "Era: " << era << "   Subera: " << subera << "   isData: " << isData << "   Channel: " << decayChannel << "   triggerChannel: " << triggerChannel << std::endl;
  for(std::map< std::string, std::vector<int> >::iterator id_iter = triggerIDs.begin(); id_iter != triggerIDs.end(); ++id_iter){
    // std::cout << id_iter->first << "   " << id_iter->second << std::endl;
    std::cout << id_iter->first << "   ";
    for(int i = 0; i < triggers[id_iter->first].size(); ++i){
      std::cout << triggerIDs[id_iter->first].at(i) << "  ";
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

  auto constructP4 = [](VecF_t pts, VecF_t etas, VecF_t phis, VecF_t masses){
    auto fourVecs = ROOT::VecOps::Construct<ROOT::Math::PtEtaPhiMVector>(pts, etas, phis, masses); 
    return fourVecs;
  };
  preselectElectrons pIsoElectrons(ElectronIDEnum, false);
  preselectMuons pIsoMuons(MuonIDEnum, false);
  ret = ret.Define("Electron_p4", constructP4, {"Electron_pt", "Electron_phi", "Electron_eta", "Electron_mass"});
  ret = ret.Define("Electron_preselection", pIsoElectrons, {"Electron_pt", "Electron_eta", "Electron_phi",
	"Electron_ip3d", "Electron_dz", "Electron_charge",
	"Electron_cutBased"});
  ret = ret.Define("Muon_p4", constructP4, {"Muon_pt", "Muon_phi", "Muon_eta", "Muon_mass"});
  ret = ret.Define("Muon_preselection", pIsoMuons, {"Muon_pt", "Muon_eta", "Muon_phi", 
	"Muon_ip3d", "Muon_dz", "Muon_charge", 
	"Muon_looseId", "Muon_mediumId", "Muon_tightId", "Muon_pfIsoId"});
  ret = ret.Define("junkPrinterE", "if(ROOT::VecOps::Any(e_mask != Electron_preselection)){"
		   "auto diff_mask = (e_mask != Electron_preselection);"
		   "std::cout << \"Difference found\" << std::endl;"
		   "std::cout << \"Eleectron pt  \" << Electron_pt[diff_mask] << std::endl;"
		   "std::cout << \"Eleectron eta \" << Electron_eta[diff_mask] << std::endl;"
		   "std::cout << \"Eleectron phi \" << Electron_phi[diff_mask] << std::endl;"
		   "std::cout << \"Eleectron ip3d\" << Electron_ip3d[diff_mask] << std::endl;"
		   "std::cout << \"Eleectron dz  \" << Electron_dz[diff_mask] << std::endl;"
		   "std::cout << \"Eleectron chg \" << Electron_charge[diff_mask] << std::endl;"
		   "std::cout << \"Eleectron ID  \" << Electron_cutBased[diff_mask] << std::endl << std::endl;}"
		   "return false;");
  ret = ret.Define("junkPrinterM", "if(ROOT::VecOps::Any(mu_mask != Muon_preselection)){"
		   "auto diff_mask = (mu_mask != Muon_preselection);"
		   "std::cout << \"Difference found\" << std::endl;"
		   "std::cout << \"Muon pt  \" << Muon_pt[diff_mask] << std::endl;"
		   "std::cout << \"Muon eta \" << Muon_eta[diff_mask] << std::endl;"
		   "std::cout << \"Muon phi \" << Muon_phi[diff_mask] << std::endl;"
		   "std::cout << \"Muon ip3d\" << Muon_ip3d[diff_mask] << std::endl;"
		   "std::cout << \"Muon dz  \" << Muon_dz[diff_mask] << std::endl;"
		   "std::cout << \"Muon chg \" << Muon_charge[diff_mask] << std::endl;"
		   "std::cout << \"Muon L   \" << Muon_looseId[diff_mask] << std::endl;"
		   "std::cout << \"Muon M   \" << Muon_mediumId[diff_mask] << std::endl;"
		   "std::cout << \"Muon T   \" << Muon_tightId[diff_mask] << std::endl;"
		   "std::cout << \"Muon iso \" << Muon_pfIsoId[diff_mask] << \"Old \" << Muon_pfIsoId[mu_mask] << \"New \" << Muon_pfIsoId[Muon_preselection] << std::endl << std::endl;}"
		   "return false;");
// \"old v new \" << Muon_pfIsoId[mu_mask] << \" \" << Muon_pfIsoId[Muon_preselection] << std::end;}"
  
  //filter out tertiary leptons and match the decayChannel expectations, leaving only the pt thresholds to ensure correctness
  //Need to capture by value. If we capture by reference, no copy is made, but the local variable decayChannelIDs can go out of scope. Then we're referencing a variable that
  //no longer exists. Voila. 
  // ret = ret.Filter([decayChannelIDs](VecI_t Muon_pdgId, VecI_t Muon_charge, VecI_t Muon_preselection, 
  // 				      VecI_t Electron_pdgId, VecI_t Electron_charge, VecI_t Electron_preselection, ULong64_t rdfentry_){
  // 		     // std::cout << rdfentry_ << "  -->  ";
  // 		     bool twoLeptons = (Sum(Muon_preselection) + Sum(Electron_preselection) == 2);
  // 		     auto Lepton_absflavor = ROOT::VecOps::abs(ROOT::VecOps::Concatenate(Muon_pdgId[Muon_preselection], Electron_pdgId[Electron_preselection]));
  // 		     auto Lepton_charge = ROOT::VecOps::Concatenate(Muon_charge[Muon_preselection], Electron_charge[Electron_preselection]);
  // 		     // std::cout << Lepton_absflavor.size() << "   " << Lepton_charge.size() << "   " << decayChannelIDs.size() << "   ";
  // 		     if(twoLeptons){
  // 		       bool correctFlavors = ROOT::VecOps::All(Lepton_absflavor == decayChannelIDs);
  // 		       if(Lepton_charge.at(0) * Lepton_charge.at(1) < 0){
  // 			 if(correctFlavors){
  // 			   // std::cout << rdfentry_ << " Selected IDs: " << Lepton_absflavor
  // 			   // 	     << "  Decay IDs: (" << decayChannelIDs.size() << ") " << decayChannelIDs
  // 			   // 	     << " Decision 2L: " << twoLeptons; 
  // 			   // std::cout << " Decision CF: " << correctFlavors << std::endl;
  // 			   return true;
  // 			 }
  // 			 //failed correct flavors?
  // 			 // else{
  // 			 //   std::cout << "Flav mismatch: " << Lepton_absflavor << " " << decayChannelIDs << " " << correctFlavors << std::endl;
  // 			 // }
  // 		       }
  // 		       //failed opposite charge
  // 		       // else{
  // 		       // 	 std::cout << "Charge mismatch: " << Lepton_charge << std::endl;
  // 		       // }
  // 		     }
  // 		     //failed two leptons
  // 		     // else{
  // 		     //   std::cout << "Dilepton mismatch: " << Muon_preselection << " " << Electron_preselection << " " << twoLeptons << std::endl;
  // 		     // }
  // 		     return false;
  // 		   }, 
  // 		   {"Muon_pdgId", "Muon_charge", "Muon_preselection", "Electron_pdgId", "Electron_charge", "Electron_preselection", "rdfentry_"},
  // 		   "Exactly 2 isolated, opposite-sign leptons of correct flavor");
  ret = ret.Filter([decayChannelIDs](VecI_t Muon_pdgId, VecI_t Muon_charge, VecI_t Muon_preselection, 
				      VecI_t Electron_pdgId, VecI_t Electron_charge, VecI_t Electron_preselection, ULong64_t rdfentry_){
		     // std::cout << rdfentry_ << "  -->  ";
		     bool twoLeptons = (Sum(Muon_preselection) + Sum(Electron_preselection) == 2);
		     auto Lepton_absflavor = ROOT::VecOps::abs(ROOT::VecOps::Concatenate(Muon_pdgId[Muon_preselection], Electron_pdgId[Electron_preselection]));
		     auto Lepton_charge = ROOT::VecOps::Concatenate(Muon_charge[Muon_preselection], Electron_charge[Electron_preselection]);
		     // std::cout << Lepton_absflavor.size() << "   " << Lepton_charge.size() << "   " << decayChannelIDs.size() << "   ";
		     if(twoLeptons){
		       return true;
		     }
		     //failed two leptons
		     return false;
		   }, 
		   {"Muon_pdgId", "Muon_charge", "Muon_preselection", "Electron_pdgId", "Electron_charge", "Electron_preselection", "rdfentry_"},
		   "Exactly 2 isolated leptons");
  ret = ret.Filter([decayChannelIDs](VecI_t Muon_pdgId, VecI_t Muon_charge, VecI_t Muon_preselection, 
				      VecI_t Electron_pdgId, VecI_t Electron_charge, VecI_t Electron_preselection, ULong64_t rdfentry_){
		     // std::cout << rdfentry_ << "  -->  ";
		     bool twoLeptons = (Sum(Muon_preselection) + Sum(Electron_preselection) == 2);
		     auto Lepton_absflavor = ROOT::VecOps::abs(ROOT::VecOps::Concatenate(Muon_pdgId[Muon_preselection], Electron_pdgId[Electron_preselection]));
		     auto Lepton_charge = ROOT::VecOps::Concatenate(Muon_charge[Muon_preselection], Electron_charge[Electron_preselection]);
		     // std::cout << Lepton_absflavor.size() << "   " << Lepton_charge.size() << "   " << decayChannelIDs.size() << "   ";
		     if(twoLeptons){
		       bool correctFlavors = ROOT::VecOps::All(Lepton_absflavor == decayChannelIDs);
		       if(Lepton_charge.at(0) * Lepton_charge.at(1) < 0){
			   return true;
		       }
		       //failed opposite charge
		     }
		     return false;
		   }, 
		   {"Muon_pdgId", "Muon_charge", "Muon_preselection", "Electron_pdgId", "Electron_charge", "Electron_preselection", "rdfentry_"},
		   "Opposite-sign leptons");
  ret = ret.Filter([decayChannelIDs](VecI_t Muon_pdgId, VecI_t Muon_charge, VecI_t Muon_preselection, 
				      VecI_t Electron_pdgId, VecI_t Electron_charge, VecI_t Electron_preselection, ULong64_t rdfentry_){
		     // std::cout << rdfentry_ << "  -->  ";
		     bool twoLeptons = (Sum(Muon_preselection) + Sum(Electron_preselection) == 2);
		     auto Lepton_absflavor = ROOT::VecOps::abs(ROOT::VecOps::Concatenate(Muon_pdgId[Muon_preselection], Electron_pdgId[Electron_preselection]));
		     auto Lepton_charge = ROOT::VecOps::Concatenate(Muon_charge[Muon_preselection], Electron_charge[Electron_preselection]);
		     // std::cout << Lepton_absflavor.size() << "   " << Lepton_charge.size() << "   " << decayChannelIDs.size() << "   ";
		     if(twoLeptons){
		       bool correctFlavors = ROOT::VecOps::All(Lepton_absflavor == decayChannelIDs);
		       if(Lepton_charge.at(0) * Lepton_charge.at(1) < 0){
			 if(correctFlavors){
			   // std::cout << rdfentry_ << " Selected IDs: " << Lepton_absflavor
			   // 	     << "  Decay IDs: (" << decayChannelIDs.size() << ") " << decayChannelIDs
			   // 	     << " Decision 2L: " << twoLeptons; 
			   // std::cout << " Decision CF: " << correctFlavors << std::endl;
			   return true;
			 }
			 //failed correct flavors?
			 // else{
			 //   std::cout << "Flav mismatch: " << Lepton_absflavor << " " << decayChannelIDs << " " << correctFlavors << std::endl;
			 // }
		       }
		       //failed opposite charge
		       // else{
		       // 	 std::cout << "Charge mismatch: " << Lepton_charge << std::endl;
		       // }
		     }
		     //failed two leptons
		     // else{
		     //   std::cout << "Dilepton mismatch: " << Muon_preselection << " " << Electron_preselection << " " << twoLeptons << std::endl;
		     // }
		     return false;
		   }, 
		   {"Muon_pdgId", "Muon_charge", "Muon_preselection", "Electron_pdgId", "Electron_charge", "Electron_preselection", "rdfentry_"},
		   "Correct lepton flavor");
  ret = ret.Filter([decayChannelIDs, cutLowMassResonances](VecI_t Muon_pdgId, VecI_t Muon_charge, VecP4_t Muon_p4, VecI_t Muon_preselection,
							   VecI_t Electron_pdgId, VecI_t Electron_charge, VecP4_t Electron_p4, VecI_t Electron_preselection, 
							   ULong64_t rdfentry_){
		     // std::cout << rdfentry_ << "  -->  ";
		     bool twoLeptons = (Sum(Muon_preselection) + Sum(Electron_preselection) == 2);
		     auto Lepton_absflavor = ROOT::VecOps::abs(ROOT::VecOps::Concatenate(Muon_pdgId[Muon_preselection], Electron_pdgId[Electron_preselection]));
		     auto Lepton_charge = ROOT::VecOps::Concatenate(Muon_charge[Muon_preselection], Electron_charge[Electron_preselection]);
		     // std::cout << Lepton_absflavor.size() << "   " << Lepton_charge.size() << "   " << decayChannelIDs.size() << "   ";
		     if(twoLeptons){
		       bool correctFlavors = ROOT::VecOps::All(Lepton_absflavor == decayChannelIDs);
		       if(Lepton_charge.at(0) * Lepton_charge.at(1) < 0){
			 if(correctFlavors){
			   // std::cout << rdfentry_ << " Selected IDs: " << Lepton_absflavor
			   // 	     << "  Decay IDs: (" << decayChannelIDs.size() << ") " << decayChannelIDs
			   // 	     << " Decision 2L: " << twoLeptons; 
			   // std::cout << " Decision CF: " << correctFlavors << std::endl;
			   if(cutLowMassResonances){
			     //figure resonance cut
			     return false;
			   }
			   else{
			     return true;
			   }
			 }
		       }
		     }
		     return false;
		   }, 
		   {"Muon_pdgId", "Muon_charge", "Muon_p4", "Muon_preselection", "Electron_pdgId", "Electron_charge", "Electron_p4", "Electron_preselection", "rdfentry_"},
		   "Pass low mass resonance cut (applied = " + stringCutLowMassResonances + ")" );
  ret = ret.Filter([decayChannelIDs, cutZResonance, invertZWindow](VecI_t Muon_pdgId, VecI_t Muon_charge, VecP4_t Muon_p4, VecI_t Muon_preselection, 
								   VecI_t Electron_pdgId, VecI_t Electron_charge, VecP4_t Electron_p4, VecI_t Electron_preselection, 
								   ULong64_t rdfentry_){
		     // std::cout << rdfentry_ << "  -->  ";
		     bool twoLeptons = (Sum(Muon_preselection) + Sum(Electron_preselection) == 2);
		     auto Lepton_absflavor = ROOT::VecOps::abs(ROOT::VecOps::Concatenate(Muon_pdgId[Muon_preselection], Electron_pdgId[Electron_preselection]));
		     auto Lepton_charge = ROOT::VecOps::Concatenate(Muon_charge[Muon_preselection], Electron_charge[Electron_preselection]);
		     // std::cout << Lepton_absflavor.size() << "   " << Lepton_charge.size() << "   " << decayChannelIDs.size() << "   ";
		     if(twoLeptons){
		       bool correctFlavors = ROOT::VecOps::All(Lepton_absflavor == decayChannelIDs);
		       if(Lepton_charge.at(0) * Lepton_charge.at(1) < 0){
			 if(correctFlavors){
			   // std::cout << rdfentry_ << " Selected IDs: " << Lepton_absflavor
			   // 	     << "  Decay IDs: (" << decayChannelIDs.size() << ") " << decayChannelIDs
			   // 	     << " Decision 2L: " << twoLeptons; 
			   // std::cout << " Decision CF: " << correctFlavors << std::endl;
			   if(cutZResonance){
			     if(invertZWindow){
			       //figure Z cut
			       return false;
			     }
			     else{
			       //figure Z cut
			       return false;
			     }
			   }
			   else
			     //no Z cut, pass through
			     return true;
			 }
		       }
		     }
		     return false;
		   }, 
		   {"Muon_pdgId", "Muon_charge", "Muon_p4", "Muon_preselection", "Electron_pdgId", "Electron_charge", "Electron_p4", "Electron_preselection", "rdfentry_"},
		   "Z mass window (applied = " + stringCutZResonance + ", inverted = " + stringInvertZWindow + ")" );
  // ret = ret.Filter([](VecI_t Muon_pdgId, VecI_t Muon_pdgId, VecI_t Muon_preselection, VecI_t Electron_charge, VecI_t Electron_preselection){
  //Goal: For events that at least have 2 isolated leptons, then check the valid trigger paths, first vetoing higher tier triggers with a filter,
  //then only using a Define to store the concurrent trigger path decisions in an int value (-1 vetoed, 0 failed, 1 passed) and the matching lepton selection masks in two additional arrays
  
  //for a quick QCD test, just filter on the valid triggers from this path  
  //build common filter code based on triggerChannel
  std::string filter_code = "return";
  auto v_first = vetoTriggers.begin();
  auto v_next_to_last = vetoTriggers.empty() ? vetoTriggers.end() : std::prev(vetoTriggers.end());
  auto v_last = vetoTriggers.end();
  if(v_first != v_last){
    filter_code += " (";
    for(std::vector<std::string>::iterator vt_iter = v_first; vt_iter != v_last; ++vt_iter){
      filter_code += *vt_iter + " == false";
      if(vt_iter != v_next_to_last){
	filter_code += " && ";
      }
    }
    filter_code += ") &&"; //We had a veto section, do an AND with the passing trigger
  }

  //build the filter expressions per trigger, using common vetoTrigger code
  std::map<std::string, std::string> trigger_code;
  auto first = triggers.begin();
  auto next_to_last = triggers.empty() ? triggers.end() : std::prev(triggers.end()); // in case s is empty
  auto last = triggers.end();
  for(std::map< std::string, ROOT::VecOps::RVec<double> >::iterator th_iter = first; th_iter != last; ++th_iter){
    trigger_code[th_iter->first] = filter_code + " (" + th_iter->first + " == true";    
    if( decayChannelIDs.at(0, -1) == 13 && decayChannelIDs.at(1, -1) == 13)//MuMu
      trigger_code[th_iter->first] += " && Muon_pt[Muon_preselection].at(0, -1) >= " + std::to_string(th_iter->second.at(0, 15)) +
	" && Muon_pt[Muon_preselection].at(1, -1) >= " + std::to_string(th_iter->second.at(1, 15));
    else if( decayChannelIDs.at(0, -1) == 13 && decayChannelIDs.at(1, -1) == 11)
      trigger_code[th_iter->first] += " && Muon_pt[Muon_preselection].at(0, -1) >= " + std::to_string(th_iter->second.at(0, 15)) +
	" && Electron_pt[Electron_preselection].at(0, -1) >= " + std::to_string(th_iter->second.at(1, 15));
    else if( decayChannelIDs.at(0, -1) == 11 && decayChannelIDs.at(1, -1) == 11)
      trigger_code[th_iter->first] += " && Electron_pt[Electron_preselection].at(0, -1) >= " + std::to_string(th_iter->second.at(0, 15)) +
	" && Electron_pt[Electron_preselection].at(1, -1) >= " + std::to_string(th_iter->second.at(1, 15));
    trigger_code[th_iter->first] += ");";
    std::cout << th_iter->first << " --> " << trigger_code[th_iter->first] << std::endl;
    auto thresh = triggers[th_iter->first]; //the pt thresholds
    ret = ret.Define("triggerPath_" + std::to_string(triggerBit[th_iter->first]), 
		     [thresh](bool trigger_path, VecF_t Muon_pt, VecI_t Muon_preselection, 
			       VecF_t Electron_pt, VecI_t Electron_preselection, ULong64_t rdfentry_){
		       auto Lepton_pt = ROOT::VecOps::Concatenate(Muon_pt[Muon_preselection], Electron_pt[Electron_preselection]);
		       if(thresh.size() == 2){
			 return 1 * ROOT::VecOps::All(Lepton_pt > thresh);
		       }
		       else if(thresh.size() == 0){
			 ROOT::VecOps::RVec<double> generic = {25.0, 15.0};
			 return 1 * ROOT::VecOps::All(ROOT::VecOps::Reverse(ROOT::VecOps::Sort(Lepton_pt)) > generic);
		       }
		       else
			 throw runtime_error("Thresholds must either have 2 double values representing the Muon and Electron or highest then lowest pt thresholds, or have length 0");
		     },
		     {th_iter->first, "Muon_pt", "Muon_preselection", "Electron_pt", "Electron_preselection", "rdfentry_"});
      
  }

  //Now save filter decisions
  auto tb_first = triggerBit.begin();
  auto tb_last = triggerBit.end();
  for(std::map< std::string, int>::iterator tb_iter = tb_first; tb_iter != tb_last; ++tb_iter){
    if(triggers.find(tb_iter->first) == triggers.end()){
      //all trigger paths not being checked, set to -1
      ret = ret.Define("triggerPath_" + std::to_string(tb_iter->second), [](){int null_val = -1; return null_val;}, {});
      ret = ret.Define("triggerPath_" + std::to_string(tb_iter->second) + "_Muon_selection", [](){ROOT::VecOps::RVec<int> null_val = {};return null_val;}, {});
      ret = ret.Define("triggerPath_" + std::to_string(tb_iter->second) + "_Electrons_selection", [](){ROOT::VecOps::RVec<int> null_val = {};return null_val;}, {});
    }
    else{
      //a trigger is being checked
      // ret = ret.Define("triggerPath_" + std::to_string(tb_iter->second), );
      ret = ret.Define("triggerPath_" + std::to_string(tb_iter->second) + "_Muons_selection", 
		       [](bool trigger_path, ROOT::VecOps::RVec<int> Muon_preselection){
			 if(trigger_path)
			   return Muon_preselection;
			 else{
			   ROOT::VecOps::RVec<int> null_val = {};
			   return null_val;
			 }
		       },
		       {tb_iter->first, "Muon_preselection"});
      ret = ret.Define("triggerPath_" + std::to_string(tb_iter->second) + "_Electrons_selection", 
		       [](bool trigger_path, ROOT::VecOps::RVec<int> Electron_preselection){
			 if(trigger_path)
			   return Electron_preselection;
			 else{
			   ROOT::VecOps::RVec<int> null_val = {};
			   return null_val;
			 }
		       },
		       {tb_iter->first, "Electron_preselection"});
    }
  }//end iteration over triggerBits
  return std::pair<ROOT::RDF::RNode, ROOT::VecOps::RVec<int>>(ret, channelTriggerBits);
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
