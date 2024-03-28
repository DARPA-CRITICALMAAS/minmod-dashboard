import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import dash
from components import stats_card, pie_card
from helpers import kpis

dash.register_page(__name__, path="/")

mineral_inventories = kpis.get_mineral_inventories()


layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                stats_card("Number of Triples", 1880919),
                                width=3,
                            ),
                            dbc.Col(
                                stats_card("Number of Documents", 18809),
                                width=3,
                            ),
                            dbc.Col(
                                stats_card(
                                    "Number of Mineral Sites",
                                    kpis.get_mineral_site_count(),
                                ),
                                width=3,
                            ),
                            dbc.Col(
                                dbc.Spinner(
                                    pie_card(
                                        mineral_inventories["labels"],
                                        mineral_inventories["values"],
                                    )
                                ),
                                width=3,
                            ),
                        ]
                    ),
                ],
            ),
            style={"height": "100vh"},
        ),
    ]
)
