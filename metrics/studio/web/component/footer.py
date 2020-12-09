import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "text-align": "center"
}


def get_footer():
    return html.Footer(
        children=[
            dbc.Modal(
                [
                    dbc.ModalHeader("About METRICS"),
                    dbc.ModalBody(dcc.Markdown('''
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
[read its documentation](https://metrics.readthedocs.io/en/latest/).
                    ''')),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close", className="ml-auto")
                    ),
                ],
                id="modal",
            ),

            dbc.Row(children=[

                html.A(
                    html.I(className='fas fa-info-circle mb-2 mr-2 mt-2',
                           style={'font-size': '25px'}),
                    id='open'),
                html.A(html.I(className='fab fa-twitter mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                       href='https://twitter.com/crillab_metrics',
                       style={'font-size': '15px'}),
                html.A(html.I(className='fab fa-github mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                       href='https://github.com/crillab/metrics'),

                html.A(html.I(className='fas fa-envelope mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                       href='mailto:metrics@cril.fr')

            ],
                justify="center", align="center", className='border-top'), dbc.Row(
                [dbc.Col(html.Img(src='/static/artois', height='50'), width="auto"),
                 dbc.Col(html.Img(src='/static/cnrs', height='50'), width="auto"),
                 dbc.Col(html.Img(src='/static/cril', height='50'), width="auto")], justify="center", align="center")],
        style=CONTENT_STYLE, className="col-md-10"
    )
