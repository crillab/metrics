import base64
import glob
import hashlib
import io
import json
import os
import uuid
from pathlib import Path

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

from metrics.scalpel.config.config import EmptyFileNameMetaConfiguration
from metrics.scalpel.config.filters import create_filter
from metrics.scalpel.parser import CsvCampaignParser, CsvConfiguration
from metrics.studio.web.component.content import get_content as content
from metrics.studio.web.component.sidebar import get_sidebar as sidebar
from metrics.studio.web.component.footer import get_footer as footer
from metrics.studio.web.config import external_stylesheets, LIMIT
from metrics.studio.web.util import util
from metrics.studio.web.util.util import create_listener, decode
from metrics.wallet.dataframe.builder import Analysis
from metrics.wallet.figure.dynamic_figure import BoxPlotly, CactusPlotly, ScatterPlotly, CDFPlotly
from metrics.wallet.figure.static_figure import StatTable, ContributionTable
from datetime import datetime

jsonpickle_pd.register_handlers()
server = flask.Flask(__name__)
dash = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                 server=server, routes_pathname_prefix='/dash/')
dash.server.secret_key = os.urandom(24)
cache = Cache(dash.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 200
})

dash.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <script src="https://kit.fontawesome.com/0fca195f72.js" crossorigin="anonymous"></script>
            
        <script src='/static/js/tour.js' type='text/javascript'/></script>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            
            {%renderer%}
        </footer>
    </body>
</html>
'''

BASE_DIR = Path(__file__).resolve().parent
image_directory = 'static/img/'
js_directory = 'static/js/'
list_of_images = [os.path.basename(x) for x in glob.glob(f'{BASE_DIR}/{image_directory}*.png')] + \
                 [os.path.basename(x) for x in glob.glob(f'{BASE_DIR}/{image_directory}*.jpg')]

list_of_js = [os.path.basename(x) for x in glob.glob(f'{BASE_DIR}/{js_directory}/*.js')]
static_image_route = '/static/'


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


@server.route(f'{static_image_route}<image_path>')
def serve_image(image_path):
    image_name = f'{image_path}.png'
    image_name2 = f'{image_path}.jpg'
    if image_name in list_of_images:
        return flask.send_from_directory(f'{BASE_DIR}/{image_directory}', image_name)
    elif image_name2 in list_of_images:
        return flask.send_from_directory(f'{BASE_DIR}/{image_directory}', image_name2)
    else:
        raise Exception('"{}" is excluded from the allowed static files'.format(image_path))


@server.route(f'{static_image_route}/js/<js_file>')
def serve_js(js_file):
    if js_file in list_of_js:
        return flask.send_from_directory(f'{BASE_DIR}/{js_directory}', js_file)
    else:
        raise Exception('"{}" is excluded from the allowed static files'.format(js_file))


@server.route('/')
def index():
    return flask.redirect(flask.url_for('/dash/'))


@server.route('/example/sat2019')
def sat2019():
    return flask.redirect(
        "http://crillab-metrics.cloud/dash/1605564394.550286-82cb32bea52c56551bd7b1a5e8d3eb51dd3bed0171336d44f0d3bdf18ab6da6c"
    )


def serve_normal_layout():
    session_id = str(uuid.uuid4())
    return html.Div(id="page-content", children=[
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        sidebar(),
        content(),
        footer()
    ])


def serve_layout_with_content(campaign):
    session_id = str(uuid.uuid4())
    return html.Div(id="page-content", children=[
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        sidebar(campaign),
        content(campaign),
        footer()
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


def _create_analysis(campaign, is_success=None):
    analysis_web = Analysis(campaign=campaign, is_success=is_success)
    return analysis_web


def _create_is_success_expression(children):
    result = []
    for c in children:
        element = c['props']['children']
        if isinstance(element, list):
            element = element[1]['props']['children']
            if 'props' in element.keys() and 'value' in element['props'].keys():
                result.append(element['props']['value'])
    return create_filter(result)


def get_campaign(session_id, contents, input, sep, time, xp_ware, children):
    @cache.memoize()
    def query_and_serialize_data(session_id):
        separator = sep
        if separator is None:
            separator = ','
        listener = create_listener(xp_ware, input, time)
        csv_parser = CsvCampaignParser(listener, EmptyFileNameMetaConfiguration(),
                                       csv_configuration=CsvConfiguration(separator=separator))
        csv_parser.parse_stream(decode(contents))
        campaign = listener.get_campaign()
        is_success = _create_is_success_expression(children)
        analysis_web = _create_analysis(campaign, is_success=is_success)
        campaign_df = analysis_web.campaign_df
        return campaign_df, campaign, analysis_web

    return query_and_serialize_data(session_id)


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


@dash.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("open2", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open


@dash.callback([Output('xp-ware', 'options'),
                Output('time', 'options'),
                Output('input', 'options'), Output('color', 'options'), Output('error-load', 'children'),
                Output('success-load', 'children'), Output('warning-load', 'children')],
               [Input('upload-data', 'contents'), Input('sep', 'value')],
               [State('upload-data', 'filename'),
                State('upload-data', 'last_modified')])
def update_output(list_of_contents, sep, list_of_names, list_of_dates):
    if list_of_contents is None:
        raise PreventUpdate
    if sep is None:
        return [], [], [], [], [html.P("Please specify a separator", className="alert alert-danger")], []
    df = parse_contents(list_of_contents, sep)
    options = [{'label': i, 'value': i} for i in df.columns]
    return options, options, options, options, None, [html.P("File loaded!",
                                                             className="alert alert-success")], [
               html.P("Please fill in the following parameters.",
                      className="alert alert-warning")]


@dash.callback([Output('error-load', 'style')],
               [Input('sep', 'value')])
def error_load_update(sep):
    if sep is None:
        return [{'display': 'block'}]
    else:
        return [{'display': 'none'}]


@dash.callback(Output('is_success', 'children'),
               [Input('add', 'n_clicks')],
               [State('is_success', 'children'), State('upload-data', 'contents')])
def is_success_form(n_clicks, children, contents):
    if contents is None:
        raise PreventUpdate
    children.append(dbc.FormGroup([dbc.Label("Predicate"), dbc.Col(
        dcc.Input('predicate-value'), className='col-lg-2')], className='mt-2', row=True))
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
    campaign_df, campaign, _ = get_campaign(session_id, contents, input, sep, time, xp_ware, children)

    experiment_ware = [{'label': e['name'], 'value': e['name']} for e in campaign.experiment_wares]
    return experiment_ware, experiment_ware, experiment_ware


@dash.callback(
    [Output('warning-load', 'style'), Output('success-fill', 'children')],
    [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
     Input('input', 'value')],
    [State('upload-data', 'contents'), State('sep', 'value')])
def thank_you_callback(session_id, xp_ware, time, input, contents, sep):
    if contents is None or sep is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate

    return {'display': 'None'}, html.P("Thank you!", className="alert alert-success")


@dash.callback(
    [Output('loading-icon-box', 'children')],
    [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
     Input('input', 'value'), Input('global-experiment-ware', 'value'),
     Input('is_success', 'children')],
    [State('upload-data', 'contents'), State('sep', 'value'), State('url', 'pathname')])
def box_callback(session_id, xp_ware, time, input, box_experiment_ware, is_success_children,
                 contents, sep, pathname):
    if util.have_parameter(pathname):
        campaign = load_campaign(pathname)
        analysis = _create_analysis(campaign)
        campaign_df = analysis.campaign_df
    elif contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    else:
        campaign_df, campaign, _ = get_campaign(session_id, contents, input, sep, time, xp_ware,
                                                is_success_children)
    print(session_id)
    newdf = campaign_df.sub_data_frame('experiment_ware',
                                       box_experiment_ware if box_experiment_ware is not None else [
                                           e['name'] for e in campaign.experiment_wares[:LIMIT]])
    box = BoxPlotly(newdf)

    return [dcc.Graph(figure=box.get_figure()), ],


@dash.callback([Output('loading-icon-scatter', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('experiment-ware-1', 'value'),
                Input('experiment-ware-2', 'value'), Input('is_success', 'children'), Input('color', 'value')],
               [State('upload-data', 'contents'), State('sep', 'value'), State('url', 'pathname')])
def scatter_callback(session_id, xp_ware, time, input, xp1, xp2, is_success_children, color, contents, sep,
                     pathname):
    if util.have_parameter(pathname) and xp2 is not None and xp1 is not None:
        campaign = load_campaign(pathname)
        analysis = _create_analysis(campaign)
        campaign_df = analysis.campaign_df
    elif contents is None or input is None or time is None or xp_ware is None or xp1 is None \
            or xp2 is None:
        raise PreventUpdate
    else:
        campaign_df, campaign, analysis = get_campaign(session_id, contents, input, sep, time, xp_ware,
                                                       is_success_children)
    scatter = analysis.get_scatter_plot(dynamic=True, xp_ware_x=xp1, xp_ware_y=xp2, color_col=color)

    return [dcc.Graph(figure=scatter.get_figure()), ],


@dash.callback([Output('loading-icon-cactus', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('global-experiment-ware', 'value'),
                Input('is_success', 'children'), Input('logarithmic', 'value')],
               [State('upload-data', 'contents'), State('sep', 'value'), State('url', 'pathname')])
def cactus_callback(session_id, xp_ware, time, input, cactus_experiment_ware, is_success_children, logarithmic,
                    contents, sep,
                    pathname):
    if util.have_parameter(pathname):
        campaign = load_campaign(pathname)
        analysis = _create_analysis(campaign)
    elif contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    else:
        campaign_df, campaign, analysis = get_campaign(session_id, contents, input, sep, time, xp_ware,
                                                       is_success_children)

    wares = cactus_experiment_ware if cactus_experiment_ware is not None else [
        e['name'] for e in campaign.experiment_wares[:LIMIT]]
    my_local_analysis = analysis.sub_analysis('experiment_ware', wares)
    my_local_analysis = my_local_analysis.add_vbew(wares, 'cpu_time', vbew_name='vbs1')
    logarithmicx = 'x' in logarithmic
    logarithmicy = 'y' in logarithmic
    return [dcc.Graph(
        figure=my_local_analysis.get_cactus_plot(dynamic=True, logx=logarithmicx, logy=logarithmicy)), ],


@dash.callback([Output('loading-cdf', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('global-experiment-ware', 'value'),
                Input('is_success', 'children')],
               [State('upload-data', 'contents'), State('sep', 'value'), State('url', 'pathname')])
def cdf_callback(session_id, xp_ware, time, input, global_experiment_ware, is_success_children,
                 contents, sep, pathname):
    if util.have_parameter(pathname):
        campaign = load_campaign(pathname)
        analysis = _create_analysis(campaign)
    elif contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    else:
        campaign_df, campaign, analysis = get_campaign(session_id, contents, input, sep, time, xp_ware,
                                                       is_success_children)

    wares = global_experiment_ware if global_experiment_ware is not None else [
        e['name'] for e in campaign.experiment_wares[:LIMIT]]
    my_local_analysis = analysis.sub_analysis('experiment_ware', wares)
    my_local_analysis = my_local_analysis.add_vbew(wares, 'cpu_time', vbew_name='vbs1')

    return [dcc.Graph(figure=my_local_analysis.get_cdf(dynamic=True)), ],


@dash.callback([Output('loading-summary', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('global-experiment-ware', 'value'),
                Input('is_success', 'children')],
               [State('upload-data', 'contents'), State('sep', 'value'), State('url', 'pathname')])
def stat_table_callback(session_id, xp_ware, time, input, global_experiment_ware,
                        is_success_children, contents, sep, pathname):
    if util.have_parameter(pathname):
        campaign = load_campaign(pathname)
        analysis = _create_analysis(campaign)
        campaign_df = analysis.campaign_df
    elif contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    else:
        campaign_df, campaign, _ = get_campaign(session_id, contents, input, sep, time, xp_ware,
                                                is_success_children)
    newdf = campaign_df.sub_data_frame('experiment_ware',
                                       global_experiment_ware if global_experiment_ware is not None else [
                                           e['name'] for e in campaign.experiment_wares[:LIMIT]])
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
                                     {'name': col, 'id': col} for col in df.columns if
                                     col != 'experiment_ware']
                                 , filter_action="native",
                                 sort_action="native",
                                 sort_mode="multi",
                                 column_selectable="single")]


@dash.callback([Output('loading-icon-contribution', 'children')],
               [Input('session-id', 'children'), Input('xp-ware', 'value'), Input('time', 'value'),
                Input('input', 'value'), Input('global-experiment-ware', 'value'), Input('is_success', 'children'),
                Input('deltas', 'value')],
               [State('upload-data', 'contents'), State('sep', 'value'), State('url', 'pathname')])
def contribution_table_callback(session_id, xp_ware, time, input, global_experiment_ware, is_success,
                                global_deltas, contents, sep, pathname):
    if util.have_parameter(pathname):
        campaign = load_campaign(pathname)
        analysis = _create_analysis(campaign)
        campaign_df = analysis.campaign_df
    elif contents is None or input is None or time is None or xp_ware is None:
        raise PreventUpdate
    else:
        campaign_df, campaign, _ = get_campaign(session_id, contents, input, sep, time, xp_ware,
                                                is_success)
    new_df = campaign_df.sub_data_frame('experiment_ware',
                                        global_experiment_ware if global_experiment_ware is not None else [
                                            e['name'] for e in campaign.experiment_wares[:LIMIT]])
    contribution_table = ContributionTable(
        new_df,
        deltas=[int(a) for a in global_deltas] if global_deltas is not None else [1, 10, 100, 1000],
        dollars_for_number=True,  # 123456789 -> $123456789$
        commas_for_number=True,  # 123456789 -> 123,456,789

        xp_ware_name_map=None,  # a map to rename experimentwares
    )
    df = contribution_table.get_figure()
    df['experiment_ware'] = df.index
    return [
        dash_table.DataTable(data=df.to_dict('records'),
                             columns=[{'name': 'experiment_ware', 'id': 'experiment_ware'}] + [
                                 {'name': col, 'id': col}
                                 for col in df.columns],
                             filter_action="native",
                             sort_action="native",
                             sort_mode="multi",
                             column_selectable="single")]
