import base64
import hashlib
import io
import json
import os
import uuid

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import flask
from flask import request
from flask_caching import Cache

import jsonpickle.ext.pandas as jsonpickle_pd
import jsonpickle
import pandas as pd

from metrics.scalpel.parser import CsvCampaignParser
from metrics.studio.web.component.content import get_content as content
from metrics.studio.web.component.sidebar import get_sidebar as sidebar
from metrics.studio.web.config import external_stylesheets, OPERATOR_LIST
from metrics.studio.web.util import util
from metrics.studio.web.util.util import create_listener, decode
from metrics.wallet.dataframe.builder import Analysis
from metrics.wallet.figure.dynamic_figure import BoxPlotly, CactusPlotly, ScatterPlotly, CDFPlotly
from metrics.wallet.figure.static_figure import StatTable, ContributionTable
from datetime import datetime

jsonpickle_pd.register_handlers()
server = flask.Flask(__name__)
dash = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server, routes_pathname_prefix='/dash/')
dash.server.secret_key = os.urandom(24)
cache = Cache(dash.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 200
})


@server.route('/send-campaign', methods=['POST'])
def receipt_campaign():
    content = request.json
    h = hashlib.sha256(str.encode(content)).hexdigest()
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    f = open(f'uploads/{timestamp}-{h}.json', 'w')
    f.write(content)
    f.close()
    return {'url': f'/dash/{timestamp}-{h}'}


@server.route('/')
def index():
    return flask.redirect(flask.url_for('/dash/'))


def serve_normal_layout():
    session_id = str(uuid.uuid4())
    return html.Div(id="page-content", children=[
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        sidebar(),
        content()
    ])


def serve_layout_with_content(campaign):
    session_id = str(uuid.uuid4())
    return html.Div(id="page-content", children=[
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        sidebar(campaign),
        content(campaign)
    ])


def serve_first_layout():
    if flask.has_request_context():
        return html.Div(children=[
            dcc.Location(id='url', refresh=True),
            html.Div(id='page-content')
        ])
    else:
        return html.Div(children=[dcc.Location(id='url', refresh=True), serve_normal_layout()])


dash.layout = serve_first_layout


def _create_analysis(campaign):
    analysis_web = Analysis(campaign=campaign)
    return analysis_web


def get_campaign(session_id, contents, input, sep, time, xp_ware):
    @cache.memoize()
    def query_and_serialize_data(session_id, contents, input, separator, time, xp_ware):
        if separator is None:
            separator = ','
        listener = create_listener(xp_ware, input, time)
        csv_parser = CsvCampaignParser(listener, separator=separator)
        csv_parser.parse_stream(decode(contents))
        campaign = listener.get_campaign()
        analysis_web = _create_analysis(campaign)
        campaign_df = analysis_web.campaign_df
        return campaign_df, campaign

    return query_and_serialize_data(session_id, contents, input, sep, time, xp_ware)


def get_header(session_id, contents, sep):
    @cache.memoize()
    def query_and_serialize_data(session_id, contents, sep):
        pass

    return query_and_serialize_data(session_id, contents, sep)


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


def load_campaign(pathname):
    name = pathname.split('/')[-1]
    file_path = f'uploads/{name}.json'
    if os.path.exists(file_path):
        f = open(file_path, 'r')
        campaign = jsonpickle.decode(f.read())
        f.close()
        return campaign
    return None


@dash.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname is not None:
        campaign = load_campaign(pathname)
        return serve_layout_with_content(campaign)
    return serve_normal_layout()


@dash.callback([Output('xp-ware', 'options'),
                Output('time', 'options'),
                Output('input', 'options')],
               [Input('upload-data', 'contents')],
               [State('upload-data', 'filename'),
                State('upload-data', 'last_modified'), State('sep', 'value')])
def update_output(list_of_contents, list_of_names, list_of_dates, sep):
    if list_of_contents is None:
        raise PreventUpdate
    df = parse_contents(list_of_contents, sep)
    options = [{'label': i, 'value': i} for i in df.columns]
    return options, options, options


@dash.callback(Output('is_success', 'children'),
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


@dash.callback([
    Output('global-experiment-ware', 'options'),
    Output('experiment-ware-1', 'options'), Output('experiment-ware-2', 'options')],
    [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
     Input('input', 'value'), Input('is_success', 'children')],
    [State('upload-data', 'contents'), State('sep', 'value')])
def campaign_callback(session_id, xp_ware, time, input, children, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)

    experiment_ware = [{'label': e['name'], 'value': e['name']} for e in campaign.experiment_wares]
    return experiment_ware, experiment_ware, experiment_ware


@dash.callback([Output('loading-icon-box', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('global-experiment-ware', 'value')],
               [State('upload-data', 'contents'), State('sep', 'value'), State('url', 'pathname')])
def box_callback(session_id, xp_ware, time, input, box_experiment_ware, contents, sep, pathname):
    if util.have_parameter(pathname):
        campaign = load_campaign(pathname)
        analysis = _create_analysis(campaign)
        campaign_df = analysis.campaign_df
    elif contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    else:
        campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    newdf = campaign_df.sub_data_frame('experiment_ware',
                                       box_experiment_ware if box_experiment_ware is not None else [
                                           e['name'] for e in campaign.experiment_wares])
    box = BoxPlotly(newdf)

    return [dcc.Graph(figure=box.get_figure()), ],


@dash.callback([Output('loading-icon-scatter', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('experiment-ware-1', 'value'),
                Input('experiment-ware-2', 'value')],
               [State('upload-data', 'contents'), State('sep', 'value'), State('url', 'pathname')])
def scatter_callback(session_id, xp_ware, time, input, xp1, xp2, contents, sep, pathname):
    if util.have_parameter(pathname):
        campaign = load_campaign(pathname)
        analysis = _create_analysis(campaign)
        campaign_df = analysis.campaign_df
    elif contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    else:
        campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    scatter = ScatterPlotly(campaign_df, xp1, xp2)

    return [dcc.Graph(figure=scatter.get_figure()), ],


@dash.callback([Output('loading-icon-cactus', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('global-experiment-ware', 'value'), ],
               [State('upload-data', 'contents'), State('sep', 'value'), State('url', 'pathname')])
def cactus_callback(session_id, xp_ware, time, input, cactus_experiment_ware, contents, sep, pathname):
    if util.have_parameter(pathname):
        campaign = load_campaign(pathname)
        analysis = _create_analysis(campaign)
        campaign_df = analysis.campaign_df
    elif contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    else:
        campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    new_df = campaign_df.sub_data_frame('experiment_ware',
                                        cactus_experiment_ware if cactus_experiment_ware is not None else [
                                            e['name'] for e in campaign.experiment_wares])
    cactus = CactusPlotly(new_df)

    return [dcc.Graph(figure=cactus.get_figure()), ],


@dash.callback([Output('loading-cdf', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('global-experiment-ware', 'value'), ],
               [State('upload-data', 'contents'), State('sep', 'value'), State('url', 'pathname')])
def cdf_callback(session_id, xp_ware, time, input, global_experiment_ware, contents, sep, pathname):
    if util.have_parameter(pathname):
        campaign = load_campaign(pathname)
        analysis = _create_analysis(campaign)
        campaign_df = analysis.campaign_df
    elif contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    else:
        campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)

    new_df = campaign_df.sub_data_frame('experiment_ware',
                                        global_experiment_ware if global_experiment_ware is not None else [
                                            e['name'] for e in campaign.experiment_wares])
    cdf = CDFPlotly(new_df)

    return [dcc.Graph(figure=cdf.get_figure()), ],


@dash.callback([Output('loading-summary', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('global-experiment-ware', 'value')],
               [State('upload-data', 'contents'), State('sep', 'value')])
def stat_table_callback(session_id, xp_ware, time, input, global_experiment_ware, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    newdf = campaign_df.sub_data_frame('experiment_ware',
                                       global_experiment_ware if global_experiment_ware is not None else [
                                           e['name'] for e in campaign.experiment_wares])
    stat_table = StatTable(
        newdf,
        dollars_for_number=True,  # 123456789 -> $123456789$
        commas_for_number=True,  # 123456789 -> 123,456,789

        xp_ware_name_map=None,  # a map to rename experimentwares
    )
    df = stat_table.get_figure()
    df['experiment_ware'] = df.index
    return [dash_table.DataTable(data=df.to_dict('records'),
                                 columns=[{'name': 'experiment_ware', 'id': 'experiment_ware'}] + [
                                     {'name': col, 'id': col} for col in df.columns if col != 'experiment_ware']
                                 , filter_action="native",
                                 sort_action="native",
                                 sort_mode="multi",
                                 column_selectable="single")]


@dash.callback([Output('loading-icon-contribution', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('global-experiment-ware', 'value'), Input('deltas', 'value')],
               [State('upload-data', 'contents'), State('sep', 'value')])
def contribution_table_callback(session_id, xp_ware, time, input, global_experiment_ware, global_deltas, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None or global_deltas is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    new_df = campaign_df.sub_data_frame('experiment_ware',
                                        global_experiment_ware if global_experiment_ware is not None else [
                                            e['name'] for e in campaign.experiment_wares])
    contribution_table = ContributionTable(
        new_df,
        deltas=[int(a) for a in global_deltas],
        dollars_for_number=True,  # 123456789 -> $123456789$
        commas_for_number=True,  # 123456789 -> 123,456,789

        xp_ware_name_map=None,  # a map to rename experimentwares
    )
    df = contribution_table.get_figure()
    df['experiment_ware'] = df.index
    return [
        dash_table.DataTable(data=df.to_dict('records'),
                             columns=[{'name': 'experiment_ware', 'id': 'experiment_ware'}] + [{'name': col, 'id': col}
                                                                                               for col in df.columns],
                             filter_action="native",
                             sort_action="native",
                             sort_mode="multi",
                             column_selectable="single")]
