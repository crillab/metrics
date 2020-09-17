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

from metrics.scalpel import CampaignParserListener
from metrics.scalpel.parser import CsvCampaignParser
from metrics.studio.web.layout import configuration, box_plot, data_loading, plots, table

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
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
    if list_of_contents is not None:
        table_result, column = parse_contents(list_of_contents, list_of_names, list_of_dates, sep)
        children = [table_result]
        options = [{'label': i, 'value': i} for i in column]
        return children, options, options, options
    return list(), list(), list(), list()


@app.callback([Output('box', 'children')],
              [Input('xp-ware', 'value'), Input('time', 'value'),
               Input('input', 'value')],
              [State('upload-data', 'filename'), State('upload-data', 'contents'),
               State('upload-data', 'last_modified'), State('sep', 'value')])
def read_campaign_and_generate_plot(xp_ware, time, input, filename, contents, last_modified, sep):
    print(contents)

    listener = CampaignParserListener()
    listener.add_key_mapping('experiment_ware', xp_ware)
    listener.add_key_mapping('time', time)
    listener.add_key_mapping('input', input)

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    print(decoded)
    csv_parser = CsvCampaignParser(listener, separator=sep)
    csv_parser.parse_stream(io.StringIO(decoded.decode('utf-8')))
    campaign = listener.get_campaign()
    return list(),
