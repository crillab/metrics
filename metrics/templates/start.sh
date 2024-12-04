#!/bin/bash -l

set -e
set -x

CAMPAIGN="$1"
EW_DIR="$CAMPAIGN/experiment_wares"
INSTANCE="$2"
SOLVER_NAME="$3"
SOLVER_VERSION="$4"
SOLVER_DIR="$5"
OUTPUT_DIR="$6"
shift 6
# Load modules
source "$EW_DIR/include/load_modules_jobs.sh"

# Execute before script
source $EW_DIR/$SOLVER_DIR/before.sh

# Execute the solver
$EW_DIR/$SOLVER_DIR/exec.sh $INSTANCE "$@"

# Execute after script
source $EW_DIR/$SOLVER_DIR/after.sh
