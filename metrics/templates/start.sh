#!/bin/bash -l

set -e
set -x

CAMPAIGN="$1"
EW_DIR="$CAMPAIGN/experiment_wares"
INSTANCE="$2"
SOLVER_NAME="$3"
SOLVER_VERSION="$4"
SOLVER_DIR="$5"
#COMMAND_PREFIX="$6"
#EXECUTABLE="$7"
shift 5
# Load modules
source "$EW_DIR/scripts/include/load_modules_jobs.sh"

# Execute before script
source $EW_DIR/$SOLVER_DIR/before.sh

# Execute the solver
$EW_DIR/$SOLVER_DIR/exec.sh $INSTANCE "$@"

# Execute after script
source $EW_DIR/$SOLVER_DIR/after.sh
