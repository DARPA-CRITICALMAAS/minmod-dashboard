import dash_bootstrap_components as dbc
import dash
from dash import html
from flask import Flask
import sys

CERT_FILE = "./ssl/minmod_isi_edu_cert.cer"
KEY_FILE = "./ssl/minmod_isi_edu_key.key"

FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

server = Flask(__name__)  # define flask app.server

app = dash.Dash(
    external_stylesheets=[dbc.themes.LITERA, FA], use_pages=True, server=server
)

header_layout = html.Div(
    [
        html.Img(
            src="assets/favicon.png", style={"height": "30px", "marginRight": "10px"}
        ),
        html.A(
            [
                html.Span(
                    "Min Mod",
                    style={
                        "color": "#3f3f3f",
                        "fontSize": "30px",
                        "font-family": "'Source Code Pro', monospace",
                        "padding-left": "10px",
                        "fontWeight": "bold",
                    },
                ),
            ],
            href="https://minmod.isi.edu/",
            style={
                "text-decoration": "none",
            },
        ),
    ],
    style={
        "backgroundColor": "#ffffff",
        "padding": "10px",
        "display": "flex",
        "alignItems": "center",
    },
)


footer_layout = html.Footer(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.P(
                                    [
                                        "Data from: ",
                                        html.A(
                                            "https://minmod.isi.edu/sparql",
                                            href="https://minmod.isi.edu/sparql",
                                            style={
                                                "color": "#D3D3D3",
                                                "fontFamily": "Helvetica Neue, Helvetica, Arial, sans-serif",
                                                "text-decoration": "none",
                                            },
                                        ),
                                        html.Br(),
                                        html.A(
                                            "The data follows this schema (github)",
                                            href="https://github.com/DARPA-CRITICALMAAS/schemas/tree/main/ta2",
                                            target="_blank",
                                            style={
                                                "color": "#FDC93F",
                                                "fontFamily": "Helvetica Neue, Helvetica, Arial, sans-serif",
                                                "text-decoration": "none",
                                            },
                                        ),
                                    ],
                                    style={"color": "#D3D3D3"},
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Powered by",
                                            style={"color": "#D3D3D3", "margin": "0px"},
                                        ),
                                        html.A(
                                            html.Img(
                                                src="./assets/lodview.png",
                                                style={"height": "30px"},
                                            ),
                                            href="https://github.com/dvcama/LodView",
                                        ),  # Adjust path as necessary
                                    ],
                                    style={"marginTop": "10px"},
                                ),  # Container for LodView logo
                            ],
                            width=6,
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "justifyContent": "center",
                            },
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.A(
                                            "Center on Knowledge Graphs",
                                            href="https://usc-isi-i2.github.io",
                                            target="_blank",
                                            style={
                                                "color": "#D3D3D3",
                                                "fontSize": "22px",
                                                "fontFamily": "Helvetica Neue, Helvetica, Arial, sans-serif",
                                                "text-decoration": "none",
                                            },
                                        ),
                                        html.A(
                                            [
                                                html.Img(
                                                    src="./assets/ISI_logo.png",
                                                    style={
                                                        "height": "60px",
                                                        "marginTop": "10px",
                                                    },
                                                ),
                                            ],
                                            href="http://www.isi.edu",
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center",
                                        "alignItems": "flex-end",
                                        "height": "100%",
                                    },
                                )
                            ],
                            width=5,
                        ),
                    ],
                    className="g-0",
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                    },
                )
            ],
            fluid=True,
            style={
                "backgroundColor": "#212121",
                "padding": "10px",
                "font-family": "Roboto, sans-serif;",
            },
        )
    ],
    style={
        "position": "relative",
        "width": "100%",
        "bottom": "0",
        "backgroundColor": "#212121",
    },
)

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>MinMod</title>
        <link rel="icon" type="image/x-icon" href="/assets/favicon.png">
        {%css%}
    </head>
    <body style="display: flex; flex-direction: column; min-height: 100vh;">
        {%app_entry%}
        <footer style="margin-top: auto;">
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.layout = html.Div(
    style={"display": "flex", "flexDirection": "column", "minHeight": "100vh"},
    children=[
        header_layout,
        html.Hr(
            style={"margin": "0px"},
        ),
        dbc.Row(
            dbc.Nav(
                [
                    dbc.NavItem(
                        dbc.NavLink(
                            "Dashboard", external_link=True, active=True, href="/"
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Grade-Tonnage Model",
                            external_link=True,
                            active=True,
                            href="gtmodel",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Mineral Site Data",
                            external_link=True,
                            active=True,
                            href="mineralsite",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Advanced Search",
                            external_link=True,
                            active=True,
                            href="sparqlsearch",
                        )
                    ),
                ],
                style={"margin-left": "10px"},
            )
        ),
        html.Hr(
            style={"margin": "0px"},
        ),
        html.Div(
            dash.page_container,
            style={"flex": "1", "margin-bottom": "20px"},
        ),
        footer_layout,
    ],
)

# Run app and display result inline in the notebook
if __name__ == "__main__":
    if sys.argv[1] == "dev":
        app.run_server(host="0.0.0.0", port=8050)
    if sys.argv[1] == "prod":
        context = (CERT_FILE, KEY_FILE)
        app.run_server(host="0.0.0.0", ssl_context=context, port=8050)
