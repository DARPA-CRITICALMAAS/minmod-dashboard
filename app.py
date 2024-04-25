import dash_bootstrap_components as dbc
import dash
import sys

CERT_FILE = "./ssl/minmod_isi_edu_cert.cer"
KEY_FILE = "./ssl/minmod_isi_edu_key.key"

FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

app = dash.Dash(external_stylesheets=[dbc.themes.LITERA, FA], use_pages=True)

app.layout = dash.html.Div(
    [
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
                            href="sparql",
                        )
                    ),
                ],
                style={"margin-left": "10px"},
            )
        ),
        dash.page_container,
    ]
)

# Run app and display result inline in the notebook
if __name__ == "__main__":
    if sys.argv[1] == "dev":
        app.run_server(host="0.0.0.0", port=8050)
    if sys.argv[1] == "prod":
        context = (CERT_FILE, KEY_FILE)
        app.run_server(host="0.0.0.0", ssl_context=context, port=8050)
