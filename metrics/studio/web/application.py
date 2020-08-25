import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import base64
import datetime
import io
import dash_table
import pandas as pd
from dash.exceptions import PreventUpdate
from flask_session import Session
from flask import session

from metrics.scalpel.parser import CsvCampaignParser
from metrics.studio.web.layout import data_loading, plots, table
from metrics.studio.web.util import create_listener, decode
from metrics.wallet.dataframe.builder import CampaignDataFrameBuilder
from metrics.wallet.figure.dynamic_figure import BoxPlotly, CactusPlotly

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.server.secret_key = os.urandom(24)
server = app.server
SESSION_TYPE = 'memcached'
Session(app)

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

app.layout = html.Div(className='container', children=[
    navbar,
    dcc.Tabs(id="main-menu", value='Data loading', className="mt-5", children=[
        dcc.Tab(label=k, value=k, children=v()) for k, v in MAIN_MENU_TABS.items()

    ]),
])


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
              [Input('xp-ware', 'value'), Input('time', 'value'),
               Input('input', 'value')],
              [State('upload-data', 'contents'), State('sep', 'value')])
def campaign_callback(xp_ware, time, input, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    campaign_df, campaign = create_campaign_df(contents, input, sep, time, xp_ware) if session.get('campaign',
                                                                                                   None) is None \
        else session.get('campaign')
    session['campaign'] = json.dumps(campaign)
    box = BoxPlotly(campaign_df)
    cactus = CactusPlotly(campaign_df, show_marker=False)
    return [dcc.Graph(figure=box.get_figure()), ], [dcc.Graph(figure=cactus.get_figure()), ]


def create_campaign_df(contents, input, sep, time, xp_ware):
    listener = create_listener(xp_ware, input, time)
    csv_parser = CsvCampaignParser(listener, separator=sep)
    csv_parser.parse_stream(decode(contents))
    campaign = listener.get_campaign()
    campaign_df = CampaignDataFrameBuilder(campaign).build_from_campaign()
    return campaign_df, campaign
