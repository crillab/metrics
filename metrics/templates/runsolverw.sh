#!/bin/bash -l

# This script wraps the execution of a submitted job when it runs on a node.
#
# $1 - The CPU time limit for the job (in seconds).
# $2 - The wall time limit for the job (in seconds).
# $3 - The memory limit for the job (in MB).
# $4 - The delay between the two signals SIGTERM and SIGKILL (in seconds).
# $5 - The directory of the solver.
# $6 - The job to launch, as specified in 'jobs.lst'.
# $7 - The output directory, automatically created by 'submit'.
# $8 - Name of the solver
# $9 - Version of the solver

set -e
set -x

SOLVER_DIR=$5
EW_DIR=$(dirname $SOLVER_DIR)
CAMPAIGN=$(dirname EW_DIR)
INSTANCE="$6"

shift 9

$EW_DIR/bin/runsolver -C "$1" -W "$2" -M "$3" -d "$4" -o "$7/runsolver.out" -v "$7/statistics.out" "$EW_DIR/start.sh" $CAMPAIGN $INSTANCE $8 $9 $SOLVER_DIR $7 "$@"