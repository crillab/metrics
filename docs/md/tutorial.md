# mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity

[![License](https://img.shields.io/pypi/l/crillab-metrics)](LICENSE.md)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/crillab-metrics)
![PyPI - Status](https://img.shields.io/pypi/status/crillab-metrics)
![Travis (.org)](https://img.shields.io/travis/crillab/metrics?style=plastic)
![Sonar Quality Gate](https://img.shields.io/sonar/quality_gate/crillab_metrics?server=https%3A%2F%2Fsonarcloud.io)
![Sonar Coverage](https://img.shields.io/sonar/coverage/crillab_metrics?server=https%3A%2F%2Fsonarcloud.io)

## Authors 

- Thibault Falque - Exakis Nelite
- [Romain Wallon - CRIL, Univ Artois & CNRS](https://www.cril.univ-artois.fr/~wallon/en) 
- [Hugues Wattez - CRIL, Univ Artois & CNRS](https://www.cril.univ-artois.fr/~wattez)

## Why Metrics? 
 
When developing a SAT solver, one of the most important parts is to perform
experiments so as to evaluate its performance.
Most of the time, this process remains the same, so that everybody collects
almost the same statistics about the solver execution.
However, how many scripts are there to retrieve experimental data and draw
scatter or cactus plots?
Probably as many as researchers in the domain. Based on this observation, this
repository provides Metrics, a Python library, aiming to unify and make
easier the analysis of solver experiments.
The ambition of Metrics is to provide a complete toolchain from the execution
of the solver to the analysis of its performance.
In particular, this library simplifies the retrieval of experimental data from
many different inputs (including the solver’s output), and provides a nice
interface for drawing commonly used plots, computing statistics about
the execution of the solver, and effortlessly organizing them
(e.g., in Jupyter notebooks).
In the end, the main purpose of Metrics is to favor the sharing and
reproducibility of experimental results and their analysis.

# Installation 

To execute *Metrics* on your computer, you first need to install
[Python](https://www.python.org/downloads/) on your computer
(at least version 3.8).

As the `metrics` library is
[available on PyPI](https://pypi.org/project/crillab-metrics/), you install it
using `pip`.

```bash
pip install crillab-metrics
```

Note that, depending on your Python installation, you may need to use `pip3`
to install it, or to execute `pip` as a module, as follows.

```bash
python3 -m pip install crillab-metrics
```

# Using mETRICS

To present how to use `metrics`, let us consider an example, based on the
results of the [SAT Race 2019](http://sat-race-2019.ciirc.cvut.cz/index.php?cat=results),
in which 51 solvers have been run on 400 instances. 
Each experiment (corresponding to the execution of a solver on a particular
instance) has a timeout set to 5000 seconds and a memory limit set to 128GB.

```python
from metrics.wallet.dataframe.builder import CampaignDataFrameBuilder
campaign_df = CampaignDataFrameBuilder(campaign).build_from_campaign()
```

## Extracting Data with metrics-scalpel

Experimental data can be retrieved with metrics-scalpel. To do so, a YAML configuration file
has to be given to the program to allow it to retrieve the required data. A sample configuration
is given below.

```yaml
name: SAT Race 2019
date: July 12th, 2019
setup:
    timeout: 5000
    memout: 128000
experiment-wares:
    - CCAnrSim default
    - ...
    - smallsat default
input-set:
    name: sat-race-2019
    type: hierarchy
    path-list:
    - /path/to/the/benchmarks/of/sat/race/2019/
source:
  path: /path/to/the/results/of/sat-2019.csv
data:
  mapping:
    input: benchmark
    experiment_ware:
    - solver
    - configuration
    cpu_time: solver time
```

The first elements of this configuration give informations about the campaign: `name` , `date`, `timeout` and `memout`. 

Observe that the different solvers are listed in this file. This is quite a strong requirement (and we plan to automatically discover the solvers
in future version of Metrics), but this approach has been designed to allow, when needed, to
specify more informations about the solvers (such as their compilation date, their command
line, etc.).


Regarding the input-set, note that it is considered as a hierarchy. Whenever this is the
case, metrics-scalpel explore the file hierarchy rooted at the given directory to discover each
file it contains. It is also possible to give directly the list of the file, or to give a path to a file
that contains this list.


The last part, concerning the `mapping`, allow to retrieve from the CSV file (in this case) which columns corresponds to 
the data expected by Scalpel. 

Now, from this configuration, we can now load the whole campaign corresponding to the
SAT competition.

```python
from metrics.scalpel import read_yaml
campaign = read_yaml("/path/to/configuration.yml")
```

## Exploiting Data with metrics-wallet

Now that we have extracted relevant data from our campaign, we can start building figures.
The first step consists in extracting a data-frame from the read campaign.

```python
from metrics.wallet.dataframe.builder import CampaignDataFrameBuilder
campaign_df = CampaignDataFrameBuilder(campaign).build_from_campaign()
```

### Dynamic Plots

Notebook example [here](example/sat-competition/dynamic_analysis.ipynb)


### Static Cactus Plot

Notebook example [here](example/sat-competition/static_cactus_and_output.ipynb)

![Comparison of all competition solvers](example/sat-competition/output/cactus.svg)
![Comparison of all competition solvers zoom](example/sat-competition/output/cactus_zoom.svg)


### Static CDF Plot

Notebook example [here](example/sat-competition/static_cdf_and_output.ipynb)

![Comparison of all competition solvers](example/sat-competition/output/cdf.svg)


### Static Scatter Plot

Notebook example [here](example/sat-competition/static_scatter_and_output.ipynb)

![Comparison of all competition solvers](example/sat-competition/output/scatter_zoom.svg)


### Static Box Plot

Notebook example [here](example/sat-competition/static_box_and_output.ipynb)

![Comparison of all competition solvers](example/sat-competition/output/box.svg)


### Static Tables

Notebook example [here](example/sat-competition/tables_and_output.ipynb)



# Citing mETRICS 

