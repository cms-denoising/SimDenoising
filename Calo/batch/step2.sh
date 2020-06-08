#!/bin/bash

export JOBNAME=""
export PART=""
export OUTDIR=""
export INDIR=""
export REDIR=""
export STEP=""
export OPTIND=1
while [[ $OPTIND -lt $# ]]; do
	# getopts in silent mode, don't exit on errors
	getopts ":j:p:o:i:x:s:" opt || status=$?
	case "$opt" in
		j) export JOBNAME=$OPTARG
		;;
		p) export PART=$OPTARG
		;;
		o) export OUTDIR=$OPTARG
		;;
		i) export INDIR=$OPTARG
		;;
		x) export REDIR=$OPTARG
		;;
		s) export STEP=$OPTARG
		;;
		# keep going if getopts had an error
		\? | :) OPTIND=$((OPTIND+1))
		;;
	esac
done

echo "parameter set:"
echo "OUTDIR:     $OUTDIR"
echo "INDIR:      $INDIR"
echo "JOBNAME:    $JOBNAME"
echo "PART:       $PART"
echo "REDIR:      $REDIR"
echo "STEP:       $STEP"
echo ""

# link files from CMSSW dir
ln -fs ${CMSSWVER}/src/SimDenoising/Calo/test/${STEP}

# run CMSSW
ARGS=$(cat args_${JOBNAME}.txt)
ARGS="$ARGS part=$PART"
if [[ -n "$REDIR" ]]; then
	ARGS="$ARGS redir=${REDIR}"
fi
if [[ -n "$INDIR" ]]; then
	ARGS="$ARGS indir=${INDIR}"
fi
echo "cmsRun ${STEP} ${ARGS} 2>&1"
cmsRun ${STEP} ${ARGS} 2>&1

CMSEXIT=$?

# cleanup
rm ${STEP}

if [[ $CMSEXIT -ne 0 ]]; then
	rm *.root
	echo "exit code $CMSEXIT, skipping xrdcp"
	exit $CMSEXIT
fi

# check for gfal case
CMDSTR="xrdcp"
GFLAG=""
if [[ "$OUTDIR" == "gsiftp://"* ]]; then
	CMDSTR="gfal-copy"
	GFLAG="-g"
fi
# copy output to eos
echo "$CMDSTR output for condor"
for FILE in *.root; do
	echo "${CMDSTR} -f ${FILE} ${OUTDIR}/${FILE}"
	stageOut ${GFLAG} -x "-f" -i ${FILE} -o ${OUTDIR}/${FILE} 2>&1
	XRDEXIT=$?
	if [[ $XRDEXIT -ne 0 ]]; then
		rm *.root
		echo "exit code $XRDEXIT, failure in ${CMDSTR}"
		exit $XRDEXIT
	fi
	rm ${FILE}
done
