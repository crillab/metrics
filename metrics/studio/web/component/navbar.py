import dash_html_components as html
import dash_bootstrap_components as dbc


navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
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