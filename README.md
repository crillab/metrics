# mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity

[![License](https://img.shields.io/pypi/l/crillab-metrics)](LICENSE.md)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/crillab-metrics)
![PyPI - Status](https://img.shields.io/pypi/status/crillab-metrics)
![Travis (.org)](https://img.shields.io/travis/crillab/metrics)
![Sonar Quality Gate](https://img.shields.io/sonar/quality_gate/crillab_metrics?server=https%3A%2F%2Fsonarcloud.io)
![Sonar Coverage](https://img.shields.io/sonar/coverage/crillab_metrics?server=https%3A%2F%2Fsonarcloud.io)

## Authors

- Thibault Falque - Exakis Nelite
- [Romain Wallon - CRIL, Univ Artois & CNRS](https://www.cril.univ-artois.fr/~wallon) 
- [Hugues Wattez - Laboratoire d'Informatique de l'X (LIX), École Polytechnique](https://hwattez.github.io/markdown-cv/)

## About *Metrics*

*Metrics* is an open-source Python library developed at
[CRIL](http://www.cril.fr), designed to facilitate the conduction of
experiments and their analysis.

The main objective of *Metrics* is to provide a complete toolchain from
the execution of software programs to the analysis of their performance.
In particular, the development of *Metrics* started with the observation
that, in the SAT community, the process of experimenting solver remains
mostly the same: everybody collects almost the same statistics about the
solver execution.
However, there are probably as many scripts as researchers in the domain
for retrieving experimental data and drawing figures.
There is thus clearly a need for a tool that unifies and makes easier the
analysis of solver experiments.

The ambition of Metrics is thus to simplify the retrieval of experimental data
from many different kinds of inputs (including the solver's output), and
provide a nice interface for drawing commonly used plots, computing statistics
about the execution of the solver, and effortlessly organizing them.
In the end, the main purpose of Metrics is to favor the sharing and
reproducibility of experimental results and their analysis.

## Installation

To execute *Metrics* on your computer, you first need to install
[Python](https://www.python.org/downloads/) (at least version **3.8**).

You may install *Metrics* using `pip`, as the `metrics` library is
[available on PyPI](https://pypi.org/project/crillab-metrics/).

```bash
pip install crillab-metrics
```

Note that, depending on your Python installation, you may need to use `pip3`
to install it, or to execute `pip` as a module, as follows.

```bash
python3 -m pip install crillab-metrics
```

To improve the reproducibility of the experiments, we highly recommend to use
a [*virtual environment*](https://docs.python.org/3/tutorial/venv.html) for
each analysis you create with *Metrics*, and thus to install the `metrics`
library in this virtual environment rather than with a system-wide
installation.

## Using *Metrics*

You may find more information on how to use *Metrics* in the
[documentation](https://metrics.readthedocs.io) we provide for the package.

## Citing *Metrics*

If you are using *Metrics* in your papers, we kindly ask you to either refer to
this repository or to one of the following papers:

+ [*Metrics : Mission Expérimentations*.](https://hal.archives-ouvertes.fr/hal-03295285/document)
  Thibault Falque, Romain Wallon and Hugues Wattez.
  16es Journées Francophones de Programmation par Contraintes (JFPC'21), 2021.
+ *Metrics: Towards a Unified Library for Experimenting Solvers*.
  Thibault Falque, Romain Wallon and Hugues Wattez.
  11th International Workshop on Pragmatics of SAT (POS'20), 2020.
