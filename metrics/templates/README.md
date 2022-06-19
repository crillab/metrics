# {{ report.title }}

This directory contains an analysis demonstrating the use of *Metrics* to
analyze a campaign experimenting MIP solvers.

## Description of the environment

The experiments presented here have been run on cluster running Linux CentOS
Stream 8.3 (x86_64), and equipped with quadcore Intel Xeon E5-2643
(3.30 GHz) and 64GB of RAM.

The CPU time was limited to 1200 seconds (20 minutes) and the memory limit was
set to 32 GB.

## Description of the input instances

We considered as inputs the instances from the [latest version of the MIPLIB
benchmark set](https://miplib.zib.de/downloads/benchmark.zip) (June 2019).
The list of instances is also available [here](input_set/jobs.lst).

## Description of the solvers

For our experiments, we ran two MIP solvers, namely *IBM ILOG CPLEX* (version
20.1.0.0) and *SCIP* (version 8.0.0), using different configurations, namely:

+ $`CPLEX_{default}`$: the default configuration of *CPLEX*
+ $`CPLEX_{barrier}`$: *CPLEX* with its LP-method set to *barrier*
+ $`CPLEX_{concurrent-optimizers}`$: *CPLEX* with its LP-method set to
  *concurrent optimizers*
+ $`SCIP_{default}`$: the default configuration of *SCIP*
+ $`SCIP_{barrier}`$: *SCIP* with its LP-method set to *barrier*
+ $`SCIP_{barrier-crossover}`$: *SCIP* with its LP-method set to
  *barrier-crossover*

These 6 configurations are the 6 distinct *experiment-wares* of our analysis.
Note that *experiment-wares* is the generic name used by *Metrics* to
identify software programs which are used for experiments (as such programs
may not necessarily be solvers).

## Data collected during the experiments

During the execution of the solvers above, several files have been produced
by our execution environment.
Thanks to *Metrics-Scalpel*, we can easily parse these files to extract what
is relevant for our analysis.
You can retrieve the full configuration of *Metrics-Scalpel* in
[this file](config/metrics_scalpel.yml).
Below are given some details about what will be extracted from the output files,
based on this configuration.

Of course, this description corresponds to *our* execution environment, and you
are not forced to use the same configuration to use *Metrics* to analyze your
experiments.

### File `stdout`

The file `stdout` contains the information about the script that has been used
to run the corresponding experiment.
In particular, it starts with the following lines:

```
c launch: 1200 1200 32768 5 /path/to/solver.sh /path/to/input.mps.gz /path/to/output/directory
c CPU timeout: 1200
c wall timeout: 1200
c memout: 32768
c delay: 5
c executable: /path/to/solver.sh
c job: /path/to/input.mps.gz
c output directory: /path/to/output/directory
```

As you can see, we can retrieve the script used to run the solver (and thus, the
name of this solver) thanks to the following lines from the configuration:

```yaml
- file: stdout
  log-data: experiment_ware
  regex: 'c executable: .*/(.*.sh)'
```

Here, the `experiment_ware` is extracted from the line of the file `stdout`
that matches the specified regular expression.
The name of the solver is mapped to the (single) group of the regular
expression.

Regarding the name of the input instance, it is extracted using the following
lines from the configuration:

```yaml
- file: stdout
  log-data: input
  pattern: 'c job: {any}'
  exact: true
```

Here, the path of the `input` is extracted from the line of the file `stdout`
that matches the specified (simplified) pattern.
The name of the solver is mapped to the implicit group `{any}`, which represents
any sequence of characters.
Note that `exact` is set to true to ensure that the whole path is captured
by `{any}`.

### File `statistics.out`

The file `statistics.out` contains the information about the CPU and memory
usage of the solver for the experiment.
Its content could be the following:

```
# WCTIME: wall clock time in seconds
WCTIME=3.72162
# CPUTIME: CPU time in seconds (USERTIME+SYSTEMTIME)
CPUTIME=13.0382
# USERTIME: CPU time spent in user mode in seconds
USERTIME=12.9721
# SYSTEMTIME: CPU time spent in system mode in seconds
SYSTEMTIME=0.066074
# CPUUSAGE: CPUTIME/WCTIME in percent
CPUUSAGE=350.337
# MAXVM: maximum virtual memory used in KiB
MAXVM=642764
# TIMEOUT: did the solver exceed the time limit?
TIMEOUT=false
# MEMOUT: did the solver exceed the memory limit?
MEMOUT=false
```

Here, we are interested in the CPU time used by the solver to solve the
corresponding instance (in this case, 13.0382 seconds).
This value can be retrieved thanks to the following lines from the
configuration:

```yaml
- file: statistics.out
  log-data: cpu_time
  pattern: 'CPUTIME={real}'
```

Here, the `cpu_time` is extracted from the line of the file `statistics.out`
that matches the specified (simplified) pattern.
The runtime is mapped to the implicit group `{real}`, that represents a real
value (using any of the representations commonly accepted by most programming
languages).

### File `execution.out`

This file contains the raw output produced by the solver during an experiment.
As such, its content may vary with the solver, but it is not a problem since
*Metrics-Scalpel* will simply ignore lines that do not match the patterns
specified in its configuration.

We thus describe independantly the content of this file for *CPLEX* and *SCIP*
(and their corresponding variants).

#### Case of *CPLEX*-based solvers

To extract the information about the result found by *CPLEX*, we will be
particularly interested in the following lines:

```
MIP - Integer optimal solution:  Objective =  3.0200000000e+02
Solution time =    3.58 sec.  Iterations = 6189  Nodes = 0
Deterministic time = 2525.27 ticks  (705.79 ticks/sec)
```

For instance, we can extract from these lines both that an optimal solution has
indeed been found, and the corresponding optimal value for the objective
function, using the following lines from the configuration (their interpretation
is similar to that of the examples above):

```yaml
- file: execution.out
  log-data: objective
  pattern: 'Objective = {real}'
- file: execution.out
  log-data: status
  pattern: 'MIP - Integer {word} solution'
- file: execution.out
  log-data: decision
  pattern: 'MIP - Integer {word}'
```

We remark that these lines (along with those written in the configuration file
and note described here) also allow to deal with infeasible instances and
optimal solutions with tolerance.

#### Case of *SCIP*-based solvers

To extract the information about the result found by *SCIP*, we will be
particularly interested in the following lines:

```
SCIP Status        : problem is solved [optimal solution found]
Solving Time (sec) : 290.46
Solving Nodes      : 461 (total of 2909 nodes in 2 runs)
Primal Bound       : +3.02000000000000e+02 (6 solutions)
Dual Bound         : +3.02000000000000e+02
Gap                : 0.00 %
```

As for *CPLEX*, we can extract from these lines both that an optimal solution
has indeed been found, and the corresponding optimal value for the objective
function, using the following lines from the configuration (note that the same
names are used for both *CPLEX* and *SCIP*, as they describe the same
information):

```yaml
- file: execution.out
  log-data: objective
  pattern: 'Primal Bound : {real}'
- file: execution.out
  pattern: 'SCIP Status : problem is {word} [{word}'
  groups:
    status: 1
    decision: 2
```

Observe here that the second pattern has two (implicit) groups, that map to
two distinct log-data.
In this case, the `groups` part allows to discriminate which group maps to which
log-data (note that there is no `log-data` associated to this pattern, as
`groups` replaces it).

Additionally, *SCIP* provides information about its intermediate bounds, for
instance with the following lines from `execution.out`:

```
 time | node  | left  |LP iter|LP it/n|mem/heur|mdpt |vars |cons |rows |cuts |sepa|confs|strbr|  dualbound   | primalbound  |  gap   | compl.
  265s|     1 |     0 |  1149k|     - |   182M |   0 |4404 | 900 | 673 | 505 | 75 |1400 |1229 | 1.510000e+02 | 3.530000e+02 | 133.77%| unknown
  266s|     1 |     0 |  1149k|     - |   182M |   0 |4404 | 900 | 675 | 507 | 76 |1400 |1229 | 1.510000e+02 | 3.530000e+02 | 133.77%| unknown
  266s|     1 |     0 |  1149k|     - |   182M |   0 |4404 | 897 | 678 | 507 | 76 |1401 |1243 | 1.510000e+02 | 3.530000e+02 | 133.77%| unknown
  266s|     1 |     0 |  1149k|     - |   182M |   0 |4404 | 897 | 683 | 512 | 77 |1401 |1243 | 1.510000e+02 | 3.530000e+02 | 133.77%| unknown
  266s|     1 |     0 |  1149k|     - |   182M |   0 |4404 | 897 | 685 | 514 | 78 |1401 |1243 | 1.510000e+02 | 3.530000e+02 | 133.77%| unknown
  267s|     1 |     2 |  1149k|     - |   182M |   0 |4404 | 896 | 685 | 514 | 78 |1401 |1249 | 1.510000e+02 | 3.530000e+02 | 133.77%| unknown
  279s|   100 |    45 |  1223k| 468.3 |   185M |  27 |4404 | 947 | 724 | 588 |  1 |1483 |1272 | 1.577258e+02 | 3.530000e+02 | 123.81%|  61.63%
  282s|   200 |    73 |  1253k| 462.1 |   186M |  41 |4404 | 983 | 725 | 598 |  1 |1549 |1272 | 2.020000e+02 | 3.530000e+02 |  74.75%|  68.64%
  286s|   300 |    95 |  1273k| 452.7 |   187M |  51 |4404 | 990 | 725 | 663 |  1 |1600 |1272 | 2.020000e+02 | 3.530000e+02 |  74.75%|  68.76%
  288s|   400 |   123 |  1291k| 443.0 |   188M |  51 |4404 |1051 | 742 | 764 |  1 |1707 |1279 | 2.020000e+02 | 3.530000e+02 |  74.75%|  68.76%
d 288s|   411 |    44 |  1292k| 441.5 |veclendi|  53 |4404 |1046 | 742 |   0 |  1 |1712 |1279 | 2.020000e+02 | 3.020000e+02 |  49.50%|  72.01%
```

We can thus extract, for this solver, both a `bound_list` and a `timestamp_list`
that correspond to the list of the best primal bound found by the solver so far,
and the list of timestamps at which this bound has been logged.
To this end, we use the following lines from the configuration:

```yaml
- file: execution.out
  pattern: '[^0-9]*([-+0-9e.]*?)s\|([^|]*?\|){14}\s?([-+0-9e.]*?[^- ])\*?\s?\|'
  groups:
    timestamp_list: 1
    bound_list: 3
```

We will see in our analysis how to exploit these two lists.

## Analysis

We now present an analysis of our experiments using *Metrics-Wallet*.
You can browse the notebooks of this analysis from the following table of
contents:

+ [Loading Experiment Data](load_experiments.ipynb)
+ [Analysis of the Runtime](runtime_analysis.ipynb)
+ [Analysis of the Best Bounds](optim_analysis.ipynb)
