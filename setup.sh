#!/bin/bash -e

CMSSWVER=CMSSW_11_2_4
FORK=kpedro88
BRANCH=master
ACCESS=ssh
CORES=4

usage(){
	EXIT=$1

	echo "setup.sh [options]"
	echo ""
	echo "-f [fork]           clone from specified fork (default = ${FORK})"
	echo "-b [branch]         clone specified branch (default = ${BRANCH})"
	echo "-c [version]        use specified CMSSW version (default = ${CMSSWVER})"
	echo "-a [protocol]       use protocol to clone (default = ${ACCESS}, alternative = https)"
	echo "-j [cores]          run CMSSW compilation on # cores (default = ${CORES})"
	echo "-h                  display this message and exit"

	exit $EXIT
}

# process options
while getopts "f:b:c:a:j:h" opt; do
	case "$opt" in
	f) FORK=$OPTARG
	;;
	b) BRANCH=$OPTARG
	;;
	c) CMSSWVER=$OPTARG
	;;
	a) ACCESS=$OPTARG
	;;
	j) CORES=$OPTARG
	;;
	h) usage 0
	;;
	esac
done

# check options
if [ "$ACCESS" = "ssh" ]; then
	ACCESS_GITHUB=git@github.com:
	ACCESS_GITLAB=ssh://git@gitlab.cern.ch:7999/
	ACCESS_CMSSW=--ssh
elif [ "$ACCESS" = "https" ]; then
	ACCESS_GITHUB=https://github.com/
	ACCESS_GITLAB=https://gitlab.cern.ch/
	ACCESS_CMSSW=--https
else
	usage 1
fi

# get CMSSW release
if [[ "$CMSSWVER" == "CMSSW_11_0_"* ]]; then
	export SCRAM_ARCH=slc7_amd64_gcc820
elif [[ "$CMSSWVER" == "CMSSW_11_2_"* ]]; then
	export SCRAM_ARCH=slc7_amd64_gcc900
else
	echo "Unsupported CMSSW version: $CMSSWVER"
	exit 1
fi

scram project $CMSSWVER
cd $CMSSWVER/src

# cmsenv
eval `scramv1 runtime -sh`
git cms-init $ACCESS_CMSSW $BATCH
git config gc.auto 0

# outside repositories
git clone ${ACCESS_GITHUB}kpedro88/CondorProduction.git Condor/Production
git clone ${ACCESS_GITHUB}${FORK}/SimDenoising.git -b ${BRANCH}

# compile
scram b -j ${CORES}

# extra setup
cd SimDenoising/Calo/batch
python $CMSSW_BASE/src/Condor/Production/python/linkScripts.py
ln -s $CMSSW_BASE/src/Condor/Production/python/manageJobs.py .
python $CMSSW_BASE/src/Condor/Production/python/cacheAll.py
