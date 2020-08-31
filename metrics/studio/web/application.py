import base64
import datetime
import io
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
from metrics.studio.web.config import external_stylesheets, PLOTLY_LOGO
from metrics.studio.web.layout import data_loading, plots, table
from metrics.studio.web.util import create_listener, decode
from metrics.wallet.figure.dynamic_figure import BoxPlotly, CactusPlotly

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


def parse_contents(contents, filename, date, separator=','):
    if contents is None:
        return []
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:

        df = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')), sep=separator)

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
        ]), df.columns
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ]), list()


@app.callback([Output('output-data-upload', 'children'), Output('xp-ware', 'options'), Output('time', 'options'),
               Output('input', 'options')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified'), State('sep', 'value')])
def update_output(list_of_contents, list_of_names, list_of_dates, sep):
    if list_of_contents is None:
        raise PreventUpdate
    table_result, column = parse_contents(list_of_contents, list_of_names, list_of_dates, sep)
    children = [table_result]
    options = [{'label': i, 'value': i} for i in column]
    return children, options, options, options


@app.callback([Output('box', 'children'), Output('cactus', 'children')],
              [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
               Input('input', 'value')],
              [State('upload-data', 'contents'), State('sep', 'value')])
def campaign_callback(session_id, xp_ware, time, input, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    box = BoxPlotly(campaign_df)
    cactus = CactusPlotly(campaign_df, show_marker=False)
    return [dcc.Graph(figure=box.get_figure()), ], [dcc.Graph(figure=cactus.get_figure()), ]
