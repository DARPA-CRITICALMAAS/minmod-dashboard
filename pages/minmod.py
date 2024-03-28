import dash
from dash import html, callback, clientside_callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import dash
from components import stats_card, pie_card, gt_model_card

dash.register_page(__name__, path="/")

# will be replaced with SPARQL
pivot_df = pd.read_csv("flat_mineral_site_data.v4.csv")

# will be replaced with SPARQL
labels = ["Nickel", "Zinc"]
values = [1049, 1078]


layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Row(
                                    dbc.Col(
                                        html.Div(
                                            [
                                                dbc.Row(
                                                    stats_card(
                                                        "Number of Triples", 1880919
                                                    )
                                                ),
                                                dbc.Row(
                                                    stats_card(
                                                        "Number of Documents", 18809
                                                    )
                                                ),
                                                dbc.Row(
                                                    stats_card(
                                                        "Number of Mineral Sites", 1500
                                                    )
                                                ),
                                                dbc.Row(pie_card(labels, values)),
                                            ]
                                        ),
                                    )
                                ),
                                width=3,
                            ),
                            dbc.Col(
                                [gt_model_card(pivot_df)],
                                width=9,
                                className="my-2",
                                style={"height": "100%"},
                            ),
                        ],
                        align="start",
                    ),
                ],
            ),
            style={"height": "100vh"},
        ),
        html.Div(id="url", style={"display": "none"}),
        # Dummy div to satisfy Dash callback requirements
        html.Div(id="url-div", style={"display": "none"}),
    ]
)
