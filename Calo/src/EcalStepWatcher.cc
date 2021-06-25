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
	
	//get parameters
	image_only = iConfig.getParameter<bool>("image_only");
	xbins = iConfig.getParameter<int>("xbins");
	ybins = iConfig.getParameter<int>("ybins");
	xmin = iConfig.getParameter<int>("xmin");
	xmax = iConfig.getParameter<int>("xmax");
	ymin = iConfig.getParameter<int>("ymin");
	ymax = iConfig.getParameter<int>("ymax");

	//create output tree
	tree_ = fs_->make<TTree>("tree","tree");

	//assign branches
	tree_->Branch("prim_pt",&entry_.prim_pt,"prim_pt/D");
	tree_->Branch("prim_eta",&entry_.prim_eta,"prim_eta/D");
	tree_->Branch("prim_phi",&entry_.prim_phi,"prim_phi/D");
	tree_->Branch("prim_E",&entry_.prim_E,"prim_E/D");
	tree_->Branch("prim_id",&entry_.prim_id,"prim_id/I");
	tree_->Branch("xbins",&xbins,"xbins/I");
	tree_->Branch("ybins",&ybins,"ybins/I");
	tree_->Branch("xmin",&xmin,"xmin/I");
	tree_->Branch("xmax",&xmax,"xmax/I");
	tree_->Branch("ymin",&ymin,"ymin/I");
	tree_->Branch("ymax",&ymax,"ymax/I");
	if (!image_only){
	    tree_->Branch("step_t" , "vector<double>", &entry_.step_t, 32000, 0);
	    tree_->Branch("step_x" , "vector<double>", &entry_.step_x, 32000, 0);
	    tree_->Branch("step_y" , "vector<double>", &entry_.step_y, 32000, 0);
	    tree_->Branch("step_z" , "vector<double>", &entry_.step_z, 32000, 0);
	    tree_->Branch("step_E" , "vector<double>", &entry_.step_E, 32000, 0);
	    tree_->Branch("step_t" , "vector<double>", &entry_.step_t, 32000, 0);
	}
	else {
	    tree_->Branch("bin_weights", "vector<double>", &entry_.bin_weights, 32000, 0);
	    tree_->Branch("xbins",&xbins,"xbins/I");
            tree_->Branch("ybins",&ybins,"ybins/I");
            tree_->Branch("xmin",&xmin,"xmin/I");
            tree_->Branch("xmax",&xmax,"xmax/I");
            tree_->Branch("ymin",&ymin,"ymin/I");
            tree_->Branch("ymax",&ymax,"ymax/I");
	    h2 = new TH2F("h", "hist", xbins, xmin, xmax, ybins, ymin, ymax);
	}
}

void EcalStepWatcher::update(const BeginOfEvent* evt) {  
        //reset branches
  	entry_ = SimNtuple();
  	if (image_only){
	    h2->Reset("ICESM");
	}
}

void EcalStepWatcher::update(const G4Step* step) {
	G4StepPoint* preStepPoint = step->GetPreStepPoint();
	const G4ThreeVector& hitPoint = preStepPoint->GetPosition();
	G4VPhysicalVolume* currentPV = preStepPoint->GetPhysicalVolume();
	std::string name(currentPV->GetName());	
	std::string subname(name.substr(0,4));
	if(volumes_.find(subname)==volumes_.end()) return;
	if (!image_only){
	    entry_.step_x.push_back(hitPoint.x());
	    entry_.step_y.push_back(hitPoint.y());
	    entry_.step_z.push_back(hitPoint.z());
	    entry_.step_E.push_back(step->GetTotalEnergyDeposit()); 
	    entry_.step_t.push_back(step->GetTrack()->GetGlobalTime());
      	}
	else {
	    h2->Fill(hitPoint.x(), hitPoint.y(), step->GetTotalEnergyDeposit());
	}
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

	if (image_only) {
	    // get bin weights from TH2 and store in tree
	    Int_t x, y;
	    h2->ClearUnderflowAndOverflow();
	    entry_.bin_weights.reserve(xbins*ybins);
	    for (x=1; x <= xbins; x++){
	        for (y=1; y <= ybins; y++){
		  entry_.bin_weights.push_back(h2->GetBinContent(x, y));
		}
	    }
	}

	//fill tree
	tree_->Fill();	
}

DEFINE_SIMWATCHER(EcalStepWatcher);
