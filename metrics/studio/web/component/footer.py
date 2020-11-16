import dash_html_components as html
import dash_bootstrap_components as dbc

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "text-align": "center"
}


def get_footer():
    return html.Footer(
        children=[
            dbc.Row(children=[html.A(html.I(className='fab fa-twitter mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                                     href='https://twitter.com/crillab_metrics',
                                     style={'font-size': '15px'}),
                              html.A(html.I(className='fab fa-github mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                                     href='https://github.com/crillab/metrics'),

                              html.A(html.I(className='fas fa-info-circle mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                                     href='/about'),

                              html.A(html.I(className='fas fa-envelope mb-2 mr-2 mt-2', style={'font-size': '25px'}),
                                     href='mailto:metrics@cril.fr')

                              ],
                    justify="center", align="center", className='border-top'), dbc.Row(
                [dbc.Col(html.Img(src='/static/artois', height='50'), width="auto"),
                 dbc.Col(html.Img(src='/static/cnrs', height='50'), width="auto"),
                 dbc.Col(html.Img(src='/static/cril', height='50'), width="auto")], justify="center", align="center")],
        style=CONTENT_STYLE, className="col-md-10"
    )
