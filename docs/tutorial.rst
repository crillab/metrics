mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity
==========================================================================

|License| |PyPI - Python Version| |PyPI - Status| |Travis (.org)| |Sonar
Quality Gate| |Sonar Coverage|

Authors
-------

-  Thibault Falque - Exakis Nelite
-  `Romain Wallon - CRIL, Univ Artois &
   CNRS <https://www.cril.univ-artois.fr/~wallon/en>`__
-  `Hugues Wattez - CRIL, Univ Artois &
   CNRS <https://www.cril.univ-artois.fr/~wattez>`__

Why Metrics?
------------

*Metrics* is an `open-source <https://github.com/crillab/metrics>`__
Python library and a web-app developed at `CRIL <http://www.cril.fr>`__
by the *WWF Team* (`Hugues Wattez <http://www.cril.fr/~wattez>`__,
`Romain Wallon <http://www.cril.fr/~wallon/en>`__ and Thibault Falque),
designed to facilitate the conduction of experiments and their analysis.

The main objective of *Metrics* is to provide a complete toolchain from
the execution of software programs to the analysis of their performance.
In particular, the development of *Metrics* started with the observation
that, in the SAT community, the process of experimenting solver remains
mostly the same: everybody collects almost the same statistics about the
solver execution. However, there are probably as many scripts as
researchers in the domain for retrieving experimental data and drawing
figures. There is thus clearly a need for a tool that unifies and makes
easier the analysis of solver experiments.

The ambition of Metrics is thus to simplify the retrieval of
experimental data from many different inputs (including the solver’s
output), and provide a nice interface for drawing commonly used plots,
computing statistics about the execution of the solver, and effortlessly
organizing them. In the end, the main purpose of Metrics is to favor the
sharing and reproducibility of experimental results and their analysis.

Towards this direction, *Metrics*\ ’ web-app, a.k.a.
`Metrics-Studio <http://crillab-metrics.cloud>`__, allows to draw common
figures, such as cactus plots and scatter plots from CSV or JSON files
so as to provide a quick overview of the conducted experiments. From
this overview, one can then use locally the `Metrics\ ’
library <https://pypi.org/project/crillab-metrics/>`__ for a
fine-grained control of the drawn figures, for instance through the use
of `Jupyter notebooks <https://jupyter.org/>`__.

Installation
============

To execute *Metrics* on your computer, you first need to install
`Python <https://www.python.org/downloads/>`__ on your computer (at
least version 3.8).

As the ``metrics`` library is `available on
PyPI <https://pypi.org/project/crillab-metrics/>`__, you install it
using ``pip``.

.. code:: bash

   pip install crillab-metrics

Note that, depending on your Python installation, you may need to use
``pip3`` to install it, or to execute ``pip`` as a module, as follows.

.. code:: bash

   python3 -m pip install crillab-metrics

.. |License| image:: https://img.shields.io/pypi/l/crillab-metrics
   :target: LICENSE.md
.. |PyPI - Python Version| image:: https://img.shields.io/pypi/pyversions/crillab-metrics
.. |PyPI - Status| image:: https://img.shields.io/pypi/status/crillab-metrics
.. |Travis (.org)| image:: https://img.shields.io/travis/crillab/metrics?style=plastic
.. |Sonar Quality Gate| image:: https://img.shields.io/sonar/quality_gate/crillab_metrics?server=https%3A%2F%2Fsonarcloud.io
.. |Sonar Coverage| image:: https://img.shields.io/sonar/coverage/crillab_metrics?server=https%3A%2F%2Fsonarcloud.io
