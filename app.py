import dash_bootstrap_components as dbc
import dash

CERT_FILE = "./ssl/minmod_isi_edu_cert.cer"
KEY_FILE = "./ssl/minmod_isi_edu_key.key"



app = dash.Dash(external_stylesheets=[dbc.themes.LITERA], use_pages=True)

app.layout = dash.html.Div(
    [
        dbc.Row(
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Dashboard", active=True, href="/")),
                    dbc.NavItem(dbc.NavLink("GT Model", active=True, href="gtmodel")),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Mineral Site Data", active=True, href="mineralsite"
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink("SPARQL Sandbox", active=True, href="sparql")
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
    context = (CERT_FILE, KEY_FILE)
    app.run_server(host="0.0.0.0",ssl_context = context ,port=8050)
