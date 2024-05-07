from dash import Dash, dcc, html
import dash_bootstrap_components as dbc


def stats_card(header, content):
    """a component function to generate a statistics kpi card"""
    return dbc.Card(
        html.Div(
            [
                html.H3([header]),
                html.H4(["{:,}".format(content)]),
            ],
            className=f"border-sucess border-start border-5",
        ),
        className="text-center text-nowrap my-2 p-2",
    )
