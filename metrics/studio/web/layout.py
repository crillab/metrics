import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


def configuration():
    return [
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
            )], className='mt-2', )
    ]


def box_plot():

    return [dbc.FormGroup([
            dbc.Label("Experiment ware"),
            dcc.Dropdown(
                id="box-experiment-ware",
                options=[
                ],
                multi=True,
                placeholder="Select experiment ware",
            )], className='mt-2', )
        ,dcc.Loading(id="loading-icon-box", children=html.Div(id='box'))]


def data_loading():
    return [
        dbc.FormGroup(
            [
                dbc.Label("Separator"),
                dbc.Input(placeholder=",", type="text", id="sep"),
                dbc.FormText("CSV separator (default is ','"),
            ]
        ),
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
    ]


def scatter_plot():
    return [dbc.FormGroup([
            dbc.Label("Experiment ware 1:"),
            dcc.Dropdown(
                id="experiment-ware-1",
                options=[
                ],
                multi=False,
                placeholder="Select experiment ware",
            )], className='mt-2', ),
        dbc.FormGroup([
            dbc.Label("Experiment ware 2:"),
            dcc.Dropdown(
                id="experiment-ware-2",
                options=[
                ],
                multi=False,
                placeholder="Select experiment ware",
            )], className='mt-2', ),
        dcc.Loading(id="loading-icon-scatter", children=html.Div(id='scatter'))]


def cactus_plot():
    return [dbc.FormGroup([
            dbc.Label("Experiment ware:"),
            dcc.Dropdown(
                id="cactus-experiment-ware",
                options=[
                ],
                multi=True,
                placeholder="Select experiment ware",
            )], className='mt-2', ),dcc.Loading(id="loading-icon-cactus", children=html.Div(id='cactus'))]


def statistics():
    pass


PLOT_TAB = {'Configuration': configuration, 'Box Plots': box_plot, 'Scatter Plots': scatter_plot,
            'Cactus Plots': cactus_plot, 'Statistics': statistics}


def plots():
    return dcc.Tabs(id="plots-tabs", value='Configuration', className="mt-5", children=[
        dcc.Tab(label=k, value=k, children=v()) for k, v in PLOT_TAB.items()

    ]),


def table():
    return [
        html.Div(id='output-data-upload')
    ]
