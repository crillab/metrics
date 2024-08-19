#!/bin/bash -l

set -e
set -x

EW_DIR=$(dirname $0)
INSTANCE="$1"
shift
# Execute the solver
{{command_prefix}} $EW_DIR/{{ executable }} {{ parameters }}