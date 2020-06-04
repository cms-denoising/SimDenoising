# SimDenoising
Generate input data from Geant4 in CMSSW for AI denoising

## Setup

```bash
cmsrel CMSSW_11_0_3
cd CMSSW_11_0_3/src
cmsenv
git cms-init
git clone git@github.com:kpedro88/SimDenoising
scram b -j 4
```

## Running

GEN and SIM steps are run separately so GEN events can be reused.

```
cd SimDenoising/Calo/test
cmsRun runGen.py particle=photon minenergy=100 mineta=0.5 maxeta=0.5 minphi=0 maxphi=0 maxEvents=10
cmsRun runSim.py particle=photon minenergy=100 mineta=0.5 maxeta=0.5 minphi=0 maxphi=0 maxEvents=10
```
