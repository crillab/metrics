# About

*Metrics* is an [open-source](https://github.com/crillab/metrics) Python
library and a web-app developed at [CRIL](http://www.cril.fr) by the
*WWF Team* ([Hugues Wattez](http://www.cril.fr/~wattez),
[Romain Wallon](http://www.cril.fr/~wallon/en) and Thibault Falque),
designed to facilitate the conduction of experiments and their analysis.

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
from many different inputs (including the solver’s output), and provide a
nice interface for drawing commonly used plots, computing statistics about
the execution of the solver, and effortlessly organizing them.
In the end, the main purpose of Metrics is to favor the sharing and
reproducibility of experimental results and their analysis.

Towards this direction, *Metrics*' web-app, a.k.a.
[*Metrics-Studio*](http://crillab-metrics.cloud), allows to draw common figures,
such as cactus plots and scatter plots from CSV or JSON files so as to provide
a quick overview of the conducted experiments.
From this overview, one can then use locally the
[*Metrics*' library](https://pypi.org/project/crillab-metrics/) for a
fine-grained control of the drawn figures, for instance through the use of
[Jupyter notebooks](https://jupyter.org/).
For more details on how to use *Metrics*' tools, you may want to
[read its documentation](https://metrics.readthedocs.io).
