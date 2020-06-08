# SimDenoising
Generate input data from Geant4 in CMSSW for AI denoising

## Setup

```bash
wget https://raw.githubusercontent.com/kpedro88/SimDenoising/master/setup.sh
chmod +x setup.sh
./setup.sh
cd CMSSW_11_0_3/src
cmsenv
cd SimDenoising/Calo
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

## Batch submission

Batch jobs can be submitted to the HTCondor queue at the LPC batch system.
Job submission and management is based on the [CondorProduction](https://github.com/kpedro88/CondorProduction) package.
Refer to the package documentation for basic details.

The [batch](./Calo/batch/) directory contains all of the relevant scripts.
If you make a copy of this directory and run the [submitJobs.py](./Calo/batch/submitJobs.py) script,
it will submit to Condor the specified number of jobs for the specified parameters. Example:
```
test/lnbatch.sh myProduction
cd myProduction
python submitJobs.py -p -s -o root://cmseos.fnal.gov//store/user/YOURUSERNAME/myProduction -S gen -N 10 -A "particle=photon minenergy=100 mineta=0.5 maxeta=0.5 minphi=0 maxphi=0 maxEvents=10"
(wait for jobs to finish)
python submitJobs.py -p -s -o root://cmseos.fnal.gov//store/user/YOURUSERNAME/myProduction -S sim -N 10 -A "particle=photon minenergy=100 mineta=0.5 maxeta=0.5 minphi=0 maxphi=0 maxEvents=10" -i /store/user/YOURUSERNAME/myProduction
```

[submitJobs.py](./Calo/batch/submitJobs.py) can also:
* count the expected number of jobs to submit (for planning purposes),
* check for jobs which were completely removed from the queue and make a resubmission list,

The class [jobSubmitterSim.py](./Calo/batch/jobSubmitterSim.py) extends the class `jobSubmitter` from [CondorProduction](https://github.com/kpedro88/CondorProduction). It adds a few extra arguments:

Python:
* `-o, --output [dir]`: path to output directory in which root files will be stored (required)
* `-F, --firstPart [num]`: first part to process in case extending a sample (default = 1)
* `-N, --nParts [num]`: number of parts to process
* `-i, --indir [dir]`: input file directory (LFN)
* `--redir [dir]`: input file redirector (default = root://cmseos.fnal.gov/)
* `-S, --step [step]`: step (gen, sim)
* `-A, --args [args]`: common args to use for all jobs, should include maxEvents

Shell (in [step2.sh](./batch/step2.sh)):
* `-o [dir]`: output directory
* `-i [dir]`: input directory
* `-s [step]`: step config file
* `-j [jobname]`: job name
* `-p [part]`: part number
* `-x [redir]`: xrootd redirector
