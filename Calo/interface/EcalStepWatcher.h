#ifndef SimDenoising_Calo_EcalStepWatcher_h
#define SimDenoising_Calo_EcalStepWatcher_h

//CMSSW headers
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h" 
#include "SimG4Core/Notification/interface/Observer.h"
#include "SimG4Core/Watcher/interface/SimWatcher.h"

//ROOT headers
#include <TTree.h>
#include <TH2F.h>

//STL headers
#include <vector>
#include <unordered_set>
#include <string>

class BeginOfEvent;
class G4Step;
class EndOfEvent;

//loosely based on https://github.com/cms-sw/cmssw/blob/master/Validation/EcalHits/interface/EcalSimHitsValidProducer.h
//see also https://github.com/cms-sw/cmssw/blob/master/SimG4CMS/Calo/src/ECalSD.cc and CaloSD.cc
class EcalStepWatcher : public SimWatcher,
						public Observer<const BeginOfEvent*>,
						public Observer<const G4Step*>,
						public Observer<const EndOfEvent*>
{
	public:
		EcalStepWatcher(const edm::ParameterSet& iConfig);
		~EcalStepWatcher() override {}

		struct SimNtuple {
			double prim_pt, prim_eta, prim_phi, prim_E;
			int prim_id;
			std::vector<double> step_x, step_y, step_z, step_t, step_E, bin_weights;
		};

	private:
		//remove defaults
		EcalStepWatcher(const EcalStepWatcher&) = delete;
		const EcalStepWatcher &operator=(const EcalStepWatcher&) = delete;

		void update(const BeginOfEvent* evt) override;
		void update(const G4Step* step) override;
		void update(const EndOfEvent* evt) override;

		std::unordered_set<std::string> volumes_;
		edm::Service<TFileService> fs_;
		TTree* tree_;
		SimNtuple entry_;
		TH2F * h2;
		int xbins;
		int ybins;
		int xmin;
		int xmax;
		int ymin;
		int ymax;
		bool image_only;
};

#endif
