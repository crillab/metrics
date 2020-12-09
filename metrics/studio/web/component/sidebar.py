import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from metrics.core.model import Campaign
from metrics.studio.web.config import LIMIT

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow-y": "scroll",
    "text-align": "center",
}


def data_loading(disabled=False):
    if disabled:
        style = {'display': 'none'}
    else:
        style = {}
    return [html.Div(id="data-loading-div", style=style, children=[
        html.H4([html.I(className='fas fa-fw fa-file'), "Input Source"]),
        html.Div(
            id="error-load"
        ),
        html.Div(
            id="success-load"
        ),

        dbc.FormGroup(
            [
                dbc.Label("Separator"),
                dbc.Input(placeholder="", type="text", id="sep")
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("File(s)"),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    }
                )
            ])])
            ]


def configuration(disabled=False):
    if disabled:
        style = {'display': 'none'}
    else:
        style = {}

    return [html.Div(style=style, children=[
        html.H4(children=[html.I(className='fas fa-fw fa-cogs'), "Parameters Mapping"]),

        html.Div(
            id="warning-load"
        ),
        html.Div(
            id="success-fill"
        ),
        dbc.FormGroup([
            dbc.Label("Experiment ware (Solver, Software)"),
            dcc.Dropdown(
                disabled=disabled,
                id="xp-ware",
                options=[

                ],
                multi=True,
                placeholder="Select field for experiment ware",
            )], className='mt-2', ),

        dbc.FormGroup([
            dbc.Label("Input (Benchmark)"),
            dcc.Dropdown(
                disabled=disabled,
                id="input",
                options=[
                ],
                multi=True,
                placeholder="Select columns for experiment ware",
            )], className='mt-2', ),
        dbc.FormGroup([
            dbc.Label("Time"),
            dcc.Dropdown(
                disabled=disabled,
                id="time",
                options=[

                ],
                placeholder="Select field for time",
            )], className='mt-2', ),
        html.Hr(),
        html.H4(children=[html.I(className="fas fa-fw fa-check"), "Success Identification",

                          ]),
        html.A("Documentation",
               href='https://github.com/crillab/metrics/blob/dev/docs/md/scalpel-config.md#identifying-successful-experiments'),
        html.Div(id="is_success",
                 children=[dbc.Button('Add predicate', id='add', color="primary", )])])]


def plot_configuration(campaign=None):
    if campaign is None:
        options = []
    else:
        options = [{'label': e['name'], 'value': e['name']} for e in campaign.experiment_wares]

    return [
        html.H4(children=[html.I(className='fas fa-fw fa-chart-bar'), "Plot Configuration"]),
        dbc.FormGroup([
            dbc.Label("Experiment ware:"),
            html.P(children=[
                f"By default we show up to {LIMIT} experiment wares.", html.Br(),
                "Use the following to specify which experiment wares you want to see."],
                style={'font-size': '0.8em', 'font-style': 'italic'}),
            dcc.Dropdown(
                id="global-experiment-ware",
                options=options,
                multi=True,
                placeholder="Select experiment ware",
            )], className='mt-2', ),
        dbc.FormGroup([
            dbc.Label("Deltas:"),
            html.P(children=[
                f"Deltas are used in the computation of the contribution of each experiment-ware to the VBEW.",
                html.Br(),
                "The contribution with a delta 'd' corresponds to the number of times an experiment-ware solves an instance 'd' second(s) faster than all other solvers."],
                style={'font-size': '0.8em', 'font-style': 'italic'}),

            dcc.Dropdown(
                id="deltas",
                options=[
                    {'label': f"{val}", 'value': f'{val}'} for val in [1, 10, 100]
                ],
                multi=True,
                placeholder="Select deltas",
            )], className='mt-2', ),

        dbc.FormGroup([
            dbc.Label("Logarithmic scale:"),
            html.P(children=[
                f"Check this box for setting up a logarithmic scale on the y-axis of the cactus plot."
            ],
                style={'font-size': '0.8em', 'font-style': 'italic'}),
            dcc.Checklist(id="logarithmic",
                          options=[
                              {'label': 'Enable logarithmic scale.', 'value': 'y'},
                          ],
                          value=[]
                          )
        ], className='mt-2', ),
    ]


def get_sidebar(campaign: Campaign = None):
    b = campaign is not None

    return html.Div(
        [
            html.Button(children=[html.I(className='fas fa-bars')],
                        className="btn btn-link d-md-none rounded-circle mr-3"),

            html.Img(src='/static/logo', height=200),
            html.H3("METRICS STUDIO", style={'text-align': 'center'}),
            html.Hr(),

            html.A(
                html.I(className='fas fa-info-circle mb-2 mr-2 mt-2',
                       style={'font-size': '25px'}),
                id='open2'),
            html.A(html.I(className='fab fa-twitter mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                   href='https://twitter.com/crillab_metrics',
                   style={'font-size': '15px'}),
            html.A(html.I(className='fab fa-github mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                   href='https://github.com/crillab/metrics'),

            html.A(html.I(className='fas fa-envelope mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                   href='mailto:metrics@cril.fr'),
            html.Hr(),
            html.H4("Example"),
            html.A("SAT 2019", href="/example/sat2019"),
            html.Hr()
        ]

        + data_loading(b) + [html.Hr()] + configuration(b) + [html.Hr()] + plot_configuration(campaign),
        style=SIDEBAR_STYLE,
        className="col-lg-3"
    )
