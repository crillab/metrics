# mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity

[![License](https://img.shields.io/pypi/l/crillab-metrics)](LICENSE.md)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/crillab-metrics)
![PyPI - Status](https://img.shields.io/pypi/status/crillab-metrics)
![Travis (.org)](https://img.shields.io/travis/crillab/metrics?style=plastic)
![Sonar Quality Gate](https://img.shields.io/sonar/quality_gate/crillab_metrics?server=https%3A%2F%2Fsonarcloud.io)
![Sonar Coverage](https://img.shields.io/sonar/coverage/crillab_metrics?server=https%3A%2F%2Fsonarcloud.io)

## Authors 

- Thibault Falque - Exakis Nelite
- [Romain Wallon - LIX (Laboratoire d'Informatique de l'X), École Polytechnique, Chaire X-Uber)](https://www.lix.polytechnique.fr/~wallon/en) 
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
(at least version **3.8**).

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

[Documentation](https://metrics.readthedocs.io)



# Citing mETRICS 

