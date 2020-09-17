import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


def box_plot():
    return [
        html.H4("Box Plot", className="card-title"),
        # dbc.FormGroup([
        # dbc.Label("Experiment ware"),
        # dcc.Dropdown(
        #     id="box-experiment-ware",
        #     options=[
        #     ],
        #     multi=True,
        #     placeholder="Select experiment ware",
        # )], className='mt-2', )
        dcc.Loading(id="loading-icon-box", children=html.Div(id='box'))]


def scatter_plot():
    return [
        html.H4("Scatter Plot", className="card-title"),
        dbc.Row(children=[
            dbc.Col(
            children=[dbc.FormGroup([
                dbc.Label("Experiment ware 1:"),
                dcc.Dropdown(
                    id="experiment-ware-1",
                    options=[
                    ],
                    multi=False,
                    placeholder="Select experiment ware",
                )], className='mt-2', )]
            ),dbc.Col(children=[
            dbc.FormGroup([
                dbc.Label("Experiment ware 2:"),
                dcc.Dropdown(
                    id="experiment-ware-2",
                    options=[
                    ],
                    multi=False,
                    placeholder="Select experiment ware",
                )], className='mt-2', )]),

        ]),
        dbc.Row(children=[dcc.Loading(id="loading-icon-scatter", children=html.Div(id='scatter'))])
    ]


def cactus_plot():
    return [
        html.H4("Cactus Plot", className="card-title"),
        # dbc.FormGroup([
        # dbc.Label("Experiment ware:"),
        # dcc.Dropdown(
        #     id="cactus-experiment-ware",
        #     options=[
        #     ],
        #     multi=True,
        #     placeholder="Select experiment ware",
        # )], className='mt-2', ),
        dcc.Loading(id="loading-icon-cactus", children=html.Div(id='cactus'))]


content = html.Div(
    [
        dbc.Row(
            children=[
                dbc.Col(children=dbc.Card(children=dbc.CardBody(cactus_plot()))),
                dbc.Col(children=dbc.Card(children=dbc.CardBody(scatter_plot())))
            ]
        ),
        dbc.Row(children=[dbc.Col(children=dbc.Card(dbc.CardBody(box_plot())))],className="mt-5")
    ],
    style=CONTENT_STYLE, className="col-md-10"
)
