//custom headers
#include "SimDenoising/Calo/interface/EcalStepWatcher.h"

//CMSSW headers
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/PluginManager/interface/ModuleDef.h"
#include "SimG4Core/Watcher/interface/SimWatcherFactory.h"
#include "SimG4Core/Notification/interface/BeginOfEvent.h"
#include "SimG4Core/Notification/interface/BeginOfTrack.h"
#include "SimG4Core/Notification/interface/EndOfEvent.h"

//Geant4 headers
#include "G4PrimaryParticle.hh"
#include "G4PrimaryVertex.hh"
#include "G4SDManager.hh"
#include "G4Step.hh"

//ROOT headers
#include <TLorentzVector.h>

EcalStepWatcher::EcalStepWatcher(const edm::ParameterSet& iConfig)
{
	//store list of volumes to watch
	const auto& vols = iConfig.getParameter<std::vector<std::string>>("volumes");
	volumes_.insert(vols.begin(),vols.end());

	//create output tree
	tree_ = fs_->make<TTree>("tree","tree");

	//assign branches
	tree_->Branch("prim_pt",&entry_.prim_pt,"prim_pt/D");
	tree_->Branch("prim_eta",&entry_.prim_eta,"prim_eta/D");
	tree_->Branch("prim_phi",&entry_.prim_phi,"prim_phi/D");
	tree_->Branch("prim_E",&entry_.prim_E,"prim_E/D");
	tree_->Branch("prim_id",&entry_.prim_id,"prim_id/I");
	tree_->Branch("step_x" , "vector<double>", &entry_.step_x, 32000, 0);
	tree_->Branch("step_y" , "vector<double>", &entry_.step_y, 32000, 0);
	tree_->Branch("step_z" , "vector<double>", &entry_.step_z, 32000, 0);
	tree_->Branch("step_E" , "vector<double>", &entry_.step_E, 32000, 0);
	tree_->Branch("step_t" , "vector<double>", &entry_.step_t, 32000, 0);

}

void EcalStepWatcher::update(const BeginOfEvent* evt) {
	//reset branches
	entry_ = SimNtuple();
}

void EcalStepWatcher::update(const G4Step* step) {
	G4StepPoint* preStepPoint = step->GetPreStepPoint();
	const G4ThreeVector& hitPoint = preStepPoint->GetPosition();
	G4VPhysicalVolume* currentPV = preStepPoint->GetPhysicalVolume();
	const G4String& name = currentPV->GetName();

	if(volumes_.find(name)==volumes_.end()) return;

	entry_.step_x.push_back(hitPoint.x());
	entry_.step_y.push_back(hitPoint.y());
	entry_.step_z.push_back(hitPoint.z());
	entry_.step_E.push_back(step->GetTotalEnergyDeposit());
	entry_.step_t.push_back(step->GetTrack()->GetGlobalTime());
}

void EcalStepWatcher::update(const EndOfEvent* evt) {
	//assume single particle gun
	G4PrimaryParticle* prim = (*evt)()->GetPrimaryVertex(0)->GetPrimary(0);
	TLorentzVector vprim;
	vprim.SetPxPyPzE(prim->GetPx(),prim->GetPy(),prim->GetPz(),prim->GetTotalEnergy());
	entry_.prim_pt = vprim.Pt();
	entry_.prim_eta = vprim.Eta();
	entry_.prim_phi = vprim.Phi();
	entry_.prim_E = vprim.E();
	entry_.prim_id = prim->GetPDGcode();

	//fill tree
	tree_->Fill();
}

DEFINE_SIMWATCHER(EcalStepWatcher);
