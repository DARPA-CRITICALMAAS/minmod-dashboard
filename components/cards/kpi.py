from dash import Dash, dcc, html
import dash_bootstrap_components as dbc


def stats_card(header, content):
    return dbc.Card(
        html.Div(
            [
                html.H3([header]),
                html.H4([content]),
            ],
            className=f"border-sucess border-start border-5",
        ),
        className="text-center text-nowrap my-2 p-2",
    )
