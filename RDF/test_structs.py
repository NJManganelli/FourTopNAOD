import ROOT
import numpy as np
import os

ROOT.gInterpreter.Declare(
"""

struct Muon {
    float pt;
    float eta;
    float phi;
    float mass;
    ROOT::Math::PtEtaPhiMVector p4;
    int charge;
    float pfIsoId;
    float pfRelIso04_all;
    Muon() = default;
    //copy constructor
    Muon(const Muon &_mu): pt(_mu.pt), eta(_mu.eta), phi(_mu.phi), mass(_mu.mass), p4(_mu.p4), charge(_mu.charge), pfIsoId(_mu.pfIsoId), pfRelIso04_all(_mu.pfRelIso04_all ){};
    //value constructor
    Muon( float _pt, float _eta, float _phi, float _mass, int _charge, int _pfIsoId, float _pfRelIso04_all): 
    pt(_pt), eta(_eta), phi(_phi), mass(_mass), charge(_charge), pfIsoId(_pfIsoId), pfRelIso04_all(_pfRelIso04_all) {p4.SetCoordinates(_pt, _eta, _phi, _mass);};
};

struct JPsiCandidate {
    Muon muon1, muon2;
    float pt;
    float eta;
    float phi;
    float mass;
    ROOT::Math::PtEtaPhiMVector p4;
    int charge;
    JPsiCandidate() = default;
    JPsiCandidate( const JPsiCandidate &_jpsi): pt( _jpsi.pt), eta( _jpsi.eta), phi( _jpsi.phi), mass( _jpsi.mass), p4( _jpsi.p4), charge( _jpsi.charge) {};
    JPsiCandidate( Muon _mu1, Muon _mu2): muon1(_mu1), muon2(_mu2) {p4 = _mu1.p4 + _mu2.p4; pt = p4.Pt(); eta = p4.Eta(); phi = p4.Phi(); mass = p4.M(); charge = _mu1.charge + _mu2.charge;};
};

class DeltaRFunctor
{
private:
    float eta;
    float phi;
public:
    DeltaRFunctor(float _eta, float _phi) : eta(_eta), phi(_phi) {}
  
    // This operator overloading enables calling
    // operator function () on objects of increment
    float operator () (const ROOT::Math::PtEtaPhiMVector &_p4) const {
        return ROOT::VecOps::DeltaR(eta, (float)_p4.Eta(), phi, (float)_p4.Phi());
    }
    float operator () (const Muon &_mu) const {
        auto _p4 = _mu.p4;
        return ROOT::VecOps::DeltaR(eta, (float)_p4.Eta(), phi, (float)_p4.Phi());
    }
    float operator () (const JPsiCandidate &_jpsi) const {
        auto _p4 = _jpsi.p4;
        return ROOT::VecOps::DeltaR(eta, (float)_p4.Eta(), phi, (float)_p4.Phi());
    }
};

ROOT::VecOps::RVec<double> IsoMuJPsiMasses(ROOT::VecOps::RVec<Muon> mus, ROOT::VecOps::RVec<JPsiCandidate> jpsis){
    //auto packed_idxs = ROOT::VecOps::Combinations(mus, jpsis);
    //auto mu_idxs = packed_idxs.at(0);
    //auto jpsi_idxs = packed_idxs.at(1);
    ROOT::VecOps::RVec<double> masses = {};
    for (const Muon& mu: mus){
        for (const JPsiCandidate& jpsi : jpsis){
            auto mass = (mu.p4 + jpsi.p4).M();
            masses.push_back(mass);
        }
    }
    return masses;
}
"""
)

f = "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/280000/675D05BF-23FA-3E4F-9973-339D13789D66.root"

#Common part of dataframe
#Make masks for isolated and jpsi-candidate muons, mutually exclusive via 'iso_mu_mask == false' part
rdf = ROOT.ROOT.RDataFrame("Events", f)
# rdf = rdf.Define(
rdf = rdf.Define("iso_mu_mask", "Muon_pt > 30 && abs(Muon_eta) <= 2.4 && Muon_mediumId == true && Muon_pfIsoId >= 4")
rdf = rdf.Define("jpsi_cand_mu_mask", "Muon_pt > 3 && abs(Muon_eta) <= 2.4 && Muon_mediumId == true && iso_mu_mask == false")
#Make sure there are at least two jpsi candidate muons for combinatorics... some functions crash otherwise
rdf = rdf.Filter("Sum(jpsi_cand_mu_mask) > 1", "At least two jpsi candidate muons to make one candidate, prior to charge or mass criteria")

#Branch 1: No struct, but make use of LorentzVector for momentum
#Only add a vector containing the four-momentum, to make it easier to do things
rdf_with_p4 = rdf.Define("Muon_p4", "auto fourVecs = ROOT::VecOps::Construct<ROOT::Math::PtEtaPhiMVector>(Muon_pt, Muon_eta, Muon_phi, Muon_mass); return fourVecs;")

#Define in branch 1
rdf_with_p4 = rdf_with_p4.Define("IsoMuon_pt", "Muon_pt[iso_mu_mask]")
rdf_with_p4 = rdf_with_p4.Define("IsoMuon_eta", "Muon_eta[iso_mu_mask]")
rdf_with_p4 = rdf_with_p4.Define("IsoMuon_p4", "Muon_p4[iso_mu_mask]")
rdf_with_p4 = rdf_with_p4.Define("JPsiCandMuon_pt", "Muon_pt[jpsi_cand_mu_mask]")
rdf_with_p4 = rdf_with_p4.Define("JPsiCandMuon_eta", "Muon_eta[jpsi_cand_mu_mask]")
rdf_with_p4 = rdf_with_p4.Define("JPsiCandMuon_p4", "Muon_p4[jpsi_cand_mu_mask]")

#Add JPsiCandidate p4's and matching indices to the JPsiCandidate indexes (NOT the original muon indexes! former is a subset of the latter and gets a new, smaller enumeration)
#https://root.cern.ch/doc/master/group__vecops.html#ga134d68284fca51f3460c8c3c508ad351
#Take combinations of 2 elements of the JPsiCandidates. If there are 4 candidates in the event, we'll get a vector of vectors like { { 0, 0, 0, 1, 1, 2 }, { 1, 2, 3, 2, 3, 3 } }
#that is, pair 0+1, 0+2, 0+3, 1+2, 1+3, 2+3, representing all unique, order-agnostic pairs
rdf_with_p4 = rdf_with_p4.Define("JPsiCandidate_packedIndices", "ROOT::VecOps::Combinations(jpsi_cand_mu_mask, 2)")
rdf_with_p4 = rdf_with_p4.Define("JPsiCandidate_idx0", "JPsiCandidate_packedIndices[0]") #This is the index in the JPsiCand list of the first muon e.g. { 0, 0, 0, 1, 1, 2 }
rdf_with_p4 = rdf_with_p4.Define("JPsiCandidate_idx1",  "JPsiCandidate_packedIndices[1]") #This is the index in the JPsiCand list of the second muon e.g. { 1, 2, 3, 2, 3, 3 }
#Calculate the four momentum
rdf_with_p4 = rdf_with_p4.Define("JPsiCandidate_p4", "ROOT::VecOps::Take(JPsiCandMuon_p4, JPsiCandidate_idx0) + ROOT::VecOps::Take(JPsiCandMuon_p4, JPsiCandidate_idx1)")


#Define leading and subleading quantities's for histogramming. THese will be per-event (scalar) quantities)
rdf_with_p4 = rdf_with_p4.Define("LeadIsoMuon_pt", "IsoMuon_pt.at(0, -1.2345)") #Default value of -1.2345 because that's non-physical and won't be in our histogram bins
rdf_with_p4 = rdf_with_p4.Define("SubeadIsoMuon_eta", "IsoMuon_eta.at(1, -999)") #Subleading, using index 1, with -999 fallback value in case there is not second isolated muon

rdf_with_p4 = rdf_with_p4.Define("LeadIsoMuon_p4", "IsoMuon_p4.at(0, ROOT::Math::PtEtaPhiMVector())") 
rdf_with_p4 = rdf_with_p4.Define("SubleadIsoMuon_p4", "IsoMuon_p4.at(1, ROOT::Math::PtEtaPhiMVector())") 

#Define the deltaR and between leading iso muon and all JPsiCandidates, then histogram them
#To avoid cases where we have the default value, Filter on number of isolated muons
rdf_with_2_isos = rdf_with_p4.Filter("Sum(iso_mu_mask) == 2", "2 isolated muons")
#Use an overpowered method to handle broadcasting for deltaR calculation: make a functor for the subleading iso muon, and us the ROOT::VecOps::Map function to get dR to JPsiCands
#Might be able to use VecOps::Construct or something else, or more directly apply VecOps::DeltaR (have to explicitly loop?
rdf_with_2_isos = rdf_with_2_isos.Define("JPsiCand_SubleadMu_dR", "auto fctr = DeltaRFunctor(SubleadIsoMuon_p4.Eta(), SubleadIsoMuon_p4.Phi());"\
                                                                  "auto result = Map(JPsiCandidate_p4, fctr);"\
                                                                  "return result;")
dR = rdf_with_2_isos.Histo1D(("dR", "#DeltaR(J/#Psi_{candidate}, #mu_{subleading}^{iso})", 20, 0, 6), "JPsiCand_SubleadMu_dR", "genWeight")



#Branch 2: Alternatively, create an RVec<Muon> vector of structs to store the info. This should make traditional nested for-loop code easier, but makes it harder to use the Numpy-like fancy indexing (no Muon.pt to get an RVec of all the Muon pt variables out of the structs, so either fallback to Muon_pt or do explicit loop -> Need to do things in a more complicated way)
rdf_with_struct = rdf.Define("Muons", "auto mus = ROOT::VecOps::Construct<Muon>(Muon_pt, Muon_eta, Muon_phi, Muon_mass, Muon_charge, Muon_pfIsoId, Muon_pfRelIso04_all); return mus;")
rdf_with_struct = rdf_with_struct.Define("IsoMuons", "Muons[iso_mu_mask]")
rdf_with_struct = rdf_with_struct.Define("JPsiCandMuons", "Muons[jpsi_cand_mu_mask]")

#Need the indices, just like in Branch1
rdf_with_struct = rdf_with_struct.Define("JPsiCandidate_packedIndices", "ROOT::VecOps::Combinations(jpsi_cand_mu_mask, 2)")
rdf_with_struct = rdf_with_struct.Define("JPsiCandidate_idx0", "JPsiCandidate_packedIndices[0]") #This is the index in the JPsiCand list of the first muon e.g. { 0, 0, 0, 1, 1, 2 }
rdf_with_struct = rdf_with_struct.Define("JPsiCandidate_idx1",  "JPsiCandidate_packedIndices[1]") #This is the index in the JPsiCand list of the second muon e.g. { 1, 2, 3, 2, 3, 3 }
#Construct the JPsis by using the Construct method, passing it a vector of Muon1 and Muon2 made via VecOps::Take - so the first vector (RVec) will actually be 
#{Muons[0], Muons[0], Muons[0], Muons[1], Muons[1], Muons[2]}
#and the second will be RVec
#{Muons[1], Muons[2], Muons[3], Muons[2], Muons[3], Muons[3]}
#leading to JPsiCandidates formed as RVec
#{JPsiCandidate(Muons[0], Muons[1]), JPsiCandidate(Muons[0], Muons[2]), JPsiCandidate(Muons[0], Muons[3]), JPsiCandidate(Muons[1], Muons[2]), JPsiCandidate(Muons[1], Muons[3]), JPsiCandidate(Muons[2], Muons[3])}
rdf_with_struct = rdf_with_struct.Define("JPsiCandidates", "ROOT::VecOps::Construct<JPsiCandidate>(ROOT::VecOps::Take(Muons, JPsiCandidate_idx0), ROOT::VecOps::Take(Muons, JPsiCandidate_idx1));")
rdf_with_struct = rdf_with_struct.Define("IsoMus_JPsiCands_mass", "IsoMuJPsiMasses(IsoMuons, JPsiCandidates)") #This will just be a vector of masses for ALL cominations of iso muons + jpsi candidates (each of those constructed from two of the jpsi candidate muons)
#Require AT LEAST 1 iso muon, but will also include 2, making this histogram a superset of events included in Branch1's deltaR histo!
rdf_with_1plusisos = rdf_with_struct.Filter("Sum(iso_mu_mask) >= 1", "1 or more isolated muons")
trimass = rdf_with_1plusisos.Histo1D(("masses", "#Mass(J/#Psi_{candidate}, #mu^{iso})", 100, 0, 200), "IsoMus_JPsiCands_mass", "genWeight")




#Trigger the event loop via AsNumpy; calling it on Branch1 would redo the eventloop, if it was desired
nBranch2 = rdf_with_struct.AsNumpy(["nMuon", "Muons", "Muon_pt"]) #(["Muon_pt_crosscheck", "Test_Muon_pt_Equivalence"])

c = ROOT.TCanvas()
c.Divide(2)
c.cd(1)
dR.Draw("HIST")
c.cd(2)
trimass.Draw("HIST")
c.Draw()
c.SaveAs("jpsitest.pdf")


#Save the graph and convert it, so we see just what happened (and some things will be pruned since they're not put into Histogram/Sum/Mean/Max/AsNumpy calls, i.e. unusedBranch1 stuff 

ROOT.RDF.SaveGraph(rdf, "jpsitest_graph.dot")
#On the command line, call 
os.system("dot -Tpdf jpsitest_graph.dot > jpsitest_graph")
