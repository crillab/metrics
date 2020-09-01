import base64
import datetime
import io
import itertools
import os
import uuid

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import jsonpickle.ext.pandas as jsonpickle_pd
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask_caching import Cache

from metrics.scalpel.parser import CsvCampaignParser
from metrics.studio.web.analysis import AnalysisWeb
from metrics.studio.web.config import external_stylesheets, PLOTLY_LOGO, OPERATOR_LIST
from metrics.studio.web.layout import data_loading, plots, table
from metrics.studio.web.util import create_listener, decode
from metrics.wallet.figure.dynamic_figure import BoxPlotly, CactusPlotly, ScatterPlotly

jsonpickle_pd.register_handlers()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.server.secret_key = os.urandom(24)
server = app.server
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 200
})

MAIN_MENU_TABS = {'Data loading': data_loading, 'Plots': plots, 'Table': table}

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("STUDIO", className="ml-1")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/", className="mr-2"
        ),

        dbc.NavbarToggler(id="navbar-toggler"),
    ]
)


def serve_layout():
    session_id = str(uuid.uuid4())
    return html.Div(className='container', children=[
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        navbar,
        dcc.Tabs(id="main-menu", value='Data loading', className="mt-5", children=[
            dcc.Tab(label=k, value=k, children=v()) for k, v in MAIN_MENU_TABS.items()

        ]),
    ])


app.layout = serve_layout


def get_campaign(session_id, contents, input, sep, time, xp_ware):
    @cache.memoize()
    def query_and_serialize_data(session_id, contents, input, sep, time, xp_ware):
        listener = create_listener(xp_ware, input, time)
        csv_parser = CsvCampaignParser(listener, separator=sep)
        csv_parser.parse_stream(decode(contents))
        campaign = listener.get_campaign()
        analysis_web = AnalysisWeb(campaign)
        campaign_df = analysis_web.campaign_df
        return campaign_df, campaign

    return query_and_serialize_data(session_id, contents, input, sep, time, xp_ware)


def create_data_table(df, filename, date):
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
        ),
    ])


def parse_contents(contents, separator=','):
    if contents is None:
        return []
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:

        df = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')), sep=separator)

        return df
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ]), list()


@app.callback([Output('output-data-upload', 'children'), Output('xp-ware', 'options'),
               Output('time', 'options'),
               Output('input', 'options')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified'), State('sep', 'value')])
def update_output(list_of_contents, list_of_names, list_of_dates, sep):
    if list_of_contents is None:
        raise PreventUpdate
    df = parse_contents(list_of_contents, sep)
    children = [create_data_table(df, list_of_names, list_of_dates)]
    options = [{'label': i, 'value': i} for i in df.columns]
    return children, options, options, options


@app.callback(Output('is_success', 'children'),
              [Input('add', 'n_clicks')],
              [State('is_success', 'children'), State('upload-data', 'contents'),
               State('sep', 'value')])
def is_success_form(n_clicks, children, contents, sep):
    if contents is None:
        raise PreventUpdate
    df = parse_contents(contents, sep)
    children.append(dbc.FormGroup([dbc.Label("Predicate"), dbc.Col(
        dcc.Dropdown(
            id="predicate-column",
            options=[
                {'label': x, 'value': x} for x in df.columns
            ],
            multi=False,
            placeholder="Select column for predicate",
        ), width=3), dbc.Col(
        dcc.Dropdown(id="operator",
                     options=[
                         {'label': x, 'value': x} for x in OPERATOR_LIST
                     ],
                     multi=False,
                     placeholder="Select operator",
                     ), width=3), dcc.Input('predicate-value')], className='mt-2', row=True))
    return children


@app.callback([
    Output('cactus-experiment-ware', 'options'),
    Output('experiment-ware-1', 'options'), Output('experiment-ware-2', 'options'),
    Output('box-experiment-ware', 'options')],
    [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
     Input('input', 'value'),Input('is_success','children')],
    [State('upload-data', 'contents'), State('sep', 'value')])
def campaign_callback(session_id, xp_ware, time, input, children, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)

    experiment_ware = [{'label': e['name'], 'value': e['name']} for e in campaign.experiment_wares]
    print(children)
    return experiment_ware, experiment_ware, experiment_ware, experiment_ware


@app.callback([Output('loading-icon-box', 'children')],
              [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
               Input('input', 'value'), Input('box-experiment-ware', 'value')],
              [State('upload-data', 'contents'), State('sep', 'value')])
def campaign_callback(session_id, xp_ware, time, input, box_experiment_ware, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    newdf = campaign_df.sub_data_frame('experiment_ware',
                                       box_experiment_ware if box_experiment_ware is not None else [
                                           e['name'] for e in campaign.experiment_wares])
    box = BoxPlotly(newdf)

    return [dcc.Graph(figure=box.get_figure()), ],


@app.callback([Output('loading-icon-scatter', 'children')],
              [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
               Input('input', 'value'), Input('experiment-ware-1', 'value'),
               Input('experiment-ware-2', 'value')],
              [State('upload-data', 'contents'), State('sep', 'value')])
def campaign_callback(session_id, xp_ware, time, input, xp1, xp2, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None or xp1 is None or xp2 is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    scatter = ScatterPlotly(campaign_df, xp1, xp2)

    return [dcc.Graph(figure=scatter.get_figure()), ],


@app.callback([Output('loading-icon-cactus', 'children')],
              [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
               Input('input', 'value'), Input('cactus-experiment-ware', 'value'), ],
              [State('upload-data', 'contents'), State('sep', 'value')])
def campaign_callback(session_id, xp_ware, time, input, cactus_experiment_ware, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    newdf = campaign_df.sub_data_frame('experiment_ware',
                                       cactus_experiment_ware if cactus_experiment_ware is not None else [
                                           e['name'] for e in campaign.experiment_wares])
    cactus = CactusPlotly(newdf)

    return [dcc.Graph(figure=cactus.get_figure()), ],
