import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}


def data_loading():
    return [
        html.H3("Data Loading"),
        dbc.FormGroup(
            [
                dbc.Label("Separator"),
                dbc.Input(placeholder="", type="text", id="sep"),
                dbc.FormText("CSV separator (default is ',')"),
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
            ])
    ]


def configuration():
    return [
        html.H3("Configuration"),
        dbc.FormGroup([
            dbc.Label("Experiment ware"),
            dcc.Dropdown(
                id="xp-ware",
                options=[

                ],
                multi=True,
                placeholder="Select field for experiment ware",
            )], className='mt-2', ),
        dbc.FormGroup([
            dbc.Label("Time"),
            dcc.Dropdown(
                id="time",
                options=[

                ],
                placeholder="Select field for time",
            )], className='mt-2', ),
        dbc.FormGroup([
            dbc.Label("Input"),
            dcc.Dropdown(
                id="input",
                options=[
                ],
                multi=True,
                placeholder="Select columns for experiment ware",
            )], className='mt-2', ),
        html.Div(id="is_success", style={'display': 'none'},
                 children=[dbc.Button('Add predicate', id='add', color="primary", )])
    ]


def plot_configuration():
    return [
        html.H3("Experiment Ware"),
        dbc.FormGroup([
            dbc.Label("Experiment ware:"),
            dcc.Dropdown(
                id="global-experiment-ware",
                options=[
                ],
                multi=True,
                placeholder="Select experiment ware",
            )], className='mt-2', ),
    ]

sidebar = html.Div(
    [
        html.H2("STUDIO", className="display-4"),
        html.Hr(),

    ] + data_loading() + [html.Hr()] + configuration() + [html.Hr()] + plot_configuration(),
    style=SIDEBAR_STYLE, className="col-md-3"
)
