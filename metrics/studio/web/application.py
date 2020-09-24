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
from metrics.studio.web.util.analysis import AnalysisWeb
from metrics.studio.web.component.content import content
from metrics.studio.web.component.sidebar import sidebar
from metrics.studio.web.config import external_stylesheets, OPERATOR_LIST

from metrics.studio.web.util.util import create_listener, decode
from metrics.wallet.figure.dynamic_figure import BoxPlotly, CactusPlotly, ScatterPlotly, CDFPlotly
from metrics.wallet.figure.static_figure import StatTable, ContributionTable

jsonpickle_pd.register_handlers()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.server.secret_key = os.urandom(24)
server = app.server
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 200
})


def serve_layout():
    session_id = str(uuid.uuid4())
    return html.Div(children=[
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        sidebar,
        content
    ])


app.layout = serve_layout


def get_campaign(session_id, contents, input, sep, time, xp_ware):
    @cache.memoize()
    def query_and_serialize_data(session_id, contents, input, separator, time, xp_ware):
        if separator is None:
            separator = ','
        listener = create_listener(xp_ware, input, time)
        csv_parser = CsvCampaignParser(listener, separator=separator)
        csv_parser.parse_stream(decode(contents))
        campaign = listener.get_campaign()
        analysis_web = AnalysisWeb(campaign)
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


@app.callback([Output('xp-ware', 'options'),
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


@app.callback([Output('loading-icon-box', 'children')],
              [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
               Input('input', 'value'), Input('global-experiment-ware', 'value')],
              [State('upload-data', 'contents'), State('sep', 'value')])
def box_callback(session_id, xp_ware, time, input, box_experiment_ware, contents, sep):
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
def scatter_callback(session_id, xp_ware, time, input, xp1, xp2, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None or xp1 is None or xp2 is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    scatter = ScatterPlotly(campaign_df, xp1, xp2)

    return [dcc.Graph(figure=scatter.get_figure()), ],


@app.callback([Output('loading-icon-cactus', 'children')],
              [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
               Input('input', 'value'), Input('global-experiment-ware', 'value'), ],
              [State('upload-data', 'contents'), State('sep', 'value')])
def cactus_callback(session_id, xp_ware, time, input, cactus_experiment_ware, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    new_df = campaign_df.sub_data_frame('experiment_ware',
                                        cactus_experiment_ware if cactus_experiment_ware is not None else [
                                            e['name'] for e in campaign.experiment_wares])
    cactus = CactusPlotly(new_df)

    return [dcc.Graph(figure=cactus.get_figure()), ],


@app.callback([Output('loading-cdf', 'children')],
              [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
               Input('input', 'value'), Input('global-experiment-ware', 'value'), ],
              [State('upload-data', 'contents'), State('sep', 'value')])
def cactus_callback(session_id, xp_ware, time, input, global_experiment_ware, contents, sep):
    if contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    campaign_df, campaign = get_campaign(session_id, contents, input, sep, time, xp_ware)
    new_df = campaign_df.sub_data_frame('experiment_ware',
                                        global_experiment_ware if global_experiment_ware is not None else [
                                            e['name'] for e in campaign.experiment_wares])
    cdf = CDFPlotly(new_df)

    return [dcc.Graph(figure=cdf.get_figure()), ],


@app.callback([Output('loading-summary', 'children')],
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


@app.callback([Output('loading-icon-contribution', 'children')],
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
        dash_table.DataTable(data=df.to_dict('records'), columns=[{'name': 'experiment_ware', 'id': 'experiment_ware'}] + [{'name': col, 'id': col} for col in df.columns],
                             filter_action="native",
                             sort_action="native",
                             sort_mode="multi",
                             column_selectable="single")]
