import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from metrics.core.model import Campaign

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    # "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow-y": "scroll",
    "text-align": "center"
}


def data_loading(disabled=False):
    return [
        html.H4([html.I(className='fas fa-fw fa-spinner'), "Data Loading"]),
        html.Div(
            id="error-load"
        ),
        html.Div(
            id="success-load"
        ),

        dbc.FormGroup(
            [
                dbc.Label("Separator"),
                dbc.Input(placeholder="", type="text", id="sep", disabled=disabled)
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("File(s)"),
                dcc.Upload(
                    id='upload-data',
                    disabled=disabled,
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
            ])
    ]


def configuration(disabled=False):
    return [
        html.H4(children=[html.I(className='fas fa-fw fa-cogs'), "Configuration"]),
        dbc.FormGroup([
            dbc.Label("Experiment ware"),
            dcc.Dropdown(
                disabled=disabled,
                id="xp-ware",
                options=[

                ],
                multi=True,
                placeholder="Select field for experiment ware",
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
        dbc.FormGroup([
            dbc.Label("Input"),
            dcc.Dropdown(
                disabled=disabled,
                id="input",
                options=[
                ],
                multi=True,
                placeholder="Select columns for experiment ware",
            )], className='mt-2', ),
        html.Div(id="is_success",
                 children=[dbc.Button('Add predicate', id='add', color="primary", )])
    ]


def plot_configuration(campaign=None):
    if campaign is None:
        options = []
    else:
        options = [{'label': e['name'], 'value': e['name']} for e in campaign.experiment_wares]

    return [
        html.H4(children=[html.I(className='fas fa-fw fa-chart-bar'), "Plot Configuration"]),
        dbc.FormGroup([
            dbc.Label("Experiment ware:"),
            dcc.Dropdown(
                id="global-experiment-ware",
                options=options,
                multi=True,
                placeholder="Select experiment ware",
            )], className='mt-2', ),
        dbc.FormGroup([
            dbc.Label("Deltas:"),
            dcc.Dropdown(
                id="deltas",
                options=[
                    {'label': f"{val}", 'value': f'{val}'} for val in [1, 10, 100]
                ],
                multi=True,
                placeholder="Select deltas",
            )], className='mt-2', ),
    ]


def get_sidebar(campaign: Campaign = None):
    if campaign is None:
        return html.Div(
            [
                html.H3("METRICS STUDIO", style={'text-align': 'center'}),
                html.Hr(),

                html.A(html.I(className='fab fa-twitter mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                       href='https://twitter.com/crillab_metrics',
                       style={'font-size': '15px'}),
                html.A(html.I(className='fab fa-github mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                       href='https://github.com/crillab/metrics'),

                html.A(
                    html.I(className='fas fa-info-circle mb-2 mr-2 mt-2',
                           style={'font-size': '25px'}),
                    id='open2'),

                html.A(html.I(className='fas fa-envelope mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                       href='mailto:metrics@cril.fr'),
                html.Hr(),
                html.H4("Example"),
                html.A("SAT 2019", href="/example/sat2019"),
                html.Hr()
            ]

            + data_loading() + [html.Hr()] + configuration() + [html.Hr()] + plot_configuration(),
            style=SIDEBAR_STYLE, className="col-lg-3"
        )
    else:
        return html.Div(
            [
                html.H3("METRICS STUDIO", style={'text-align': 'center'}),
                html.Hr(),

            ] + plot_configuration(campaign) + [html.Hr()] + data_loading(True) + [html.Hr()] + configuration(True) + [
                html.Hr()],
            style=SIDEBAR_STYLE, className="col-lg-3"
        )
