import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

CONTENT_STYLE = {
    "margin-left": "25%",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


def box_plot():
    return [
        html.H4("Box Plot", className="card-title"),
        dcc.Loading(id="loading-icon-box", children=html.Div(id='box'))]


def scatter_plot(campaign=None):
    if campaign is None:
        options = []
        options_color = []
    else:
        options = [{'label': e['name'], 'value': e['name']} for e in campaign.experiment_wares]

        columns = campaign.get_input_set().get_inputs()[0].keys()
        options_color = [{'label': e, 'value': e} for e in columns]

    return [
        html.H4("Scatter Plot", className="card-title"),
        dbc.Row(children=[
            dbc.Col(
                children=[dbc.FormGroup([
                    dbc.Label("Experiment ware 1:"),
                    dcc.Dropdown(
                        id="experiment-ware-1",
                        options=options,
                        multi=False,
                        placeholder="Select experiment ware",
                    )], className='mt-2', )]
            ), dbc.Col(children=[
                dbc.FormGroup([
                    dbc.Label("Experiment ware 2:"),
                    dcc.Dropdown(
                        id="experiment-ware-2",
                        options=options,
                        multi=False,
                        placeholder="Select experiment ware",
                    )], className='mt-2', )]),

            dbc.Col(
                children=[dbc.FormGroup([
                    dbc.Label("Color:"),
                    dcc.Dropdown(
                        id="color",
                        options=options_color,
                        multi=False,
                        placeholder="Select",
                    )], className='mt-2', )]
            )

        ]),
        html.Div(children=[dcc.Loading(id="loading-icon-scatter", children=html.Div(id='scatter'))])
    ]


def cactus_plot():
    return [
        html.H4("Cactus Plot", className="card-title"),
        dcc.Loading(id="loading-icon-cactus", children=html.Div(id='cactus'))]


def cdf():
    return [
        html.H4("CDF", className="card-title"),
        dcc.Loading(id="loading-cdf", children=html.Div(id='cdf'))]


def table():
    return [
        html.H4("Summary", className="card-title"),
        dcc.Loading(id="loading-summary", children=html.Div(id='summary'))]


def contribution():
    return [
        html.H4("Contribution", className="card-title"),
        dcc.Loading(id="loading-icon-contribution", children=html.Div(id='contribution'))
    ]


def get_content(campaign=None):
    result = []
    if campaign is None:
        result.append(dbc.Row(children=[dbc.Col(children=dbc.Card(children=dbc.CardBody(scatter_plot())))]))
    else:
        result.append(dbc.Row(children=[dbc.Col(children=dbc.Card(children=dbc.CardBody(scatter_plot(campaign))))]))

    return html.Div(
            result + [
                dbc.Row(children=[dbc.Col(children=dbc.Card(dbc.CardBody(box_plot())))], className="mt-5"),
                dbc.Row(
                    children=[
                        dbc.Col(children=dbc.Card(children=dbc.CardBody(cactus_plot()))),
                        dbc.Col(children=dbc.Card(children=dbc.CardBody(cdf())))
                    ], className="mt-5"
                ),
                dbc.Row(children=[dbc.Col(children=dbc.Card(dbc.CardBody(table())))], className="mt-5"),
                dbc.Row(children=[dbc.Col(children=dbc.Card(dbc.CardBody(contribution())))], className="mt-5")
            ],
            style=CONTENT_STYLE, className="col-lg-9"
        )

