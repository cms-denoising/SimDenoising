# SimDenoising
Generate input data from Geant4 in CMSSW for AI denoising

## Setup

```bash
wget https://raw.githubusercontent.com/kpedro88/SimDenoising/master/setup.sh
chmod +x setup.sh
./setup.sh
cd CMSSW_11_0_3/src
cmsenv
```

Setup options:
```
-f [fork]           clone from specified fork (default = kpedro88)
-b [branch]         clone specified branch (default = master)
-c [version]        use specified CMSSW version (default = CMSSW_11_0_3)
-a [protocol]       use protocol to clone (default = ssh, alternative = https)
-j [cores]          run CMSSW compilation on # cores (default = 4)
-h                  display this message and exit
```

## Running

GEN and SIM steps are run separately so GEN events can be reused.

```
cd SimDenoising/Calo/test
cmsRun runGen.py particle=photon minenergy=100 mineta=0.5 maxeta=0.5 minphi=0 maxphi=0 maxEvents=10
cmsRun runSim.py particle=photon minenergy=100 mineta=0.5 maxeta=0.5 minphi=0 maxphi=0 maxEvents=10
```
