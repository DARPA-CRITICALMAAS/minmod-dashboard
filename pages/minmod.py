import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import dash
from components import stats_card, pie_card, geo_model_card
from helpers import kpis
from models import GeoMineral
from helpers import sparql_utils
import time

dash.register_page(__name__, path="/")

mineral_inventories = kpis.get_mineral_inventories()
gm = GeoMineral(commodity="Nickel", query_path="./models/min.sql")
gm.init(get_sparql_data=sparql_utils.run_minmod_query)
commodities = ["Zinc (Zn)", "Nickel (Ni)"]


def render():
    return html.Div(
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
                                                            "Number of Triples",
                                                            kpis.get_triples_count(),
                                                        )
                                                    ),
                                                    dbc.Row(
                                                        stats_card(
                                                            "Number of Documents", 1903
                                                        )
                                                    ),
                                                    dbc.Row(
                                                        stats_card(
                                                            "Number of Mineral Sites",
                                                            kpis.get_mineral_site_count(),
                                                        )
                                                    ),
                                                    dbc.Row(
                                                        pie_card(
                                                            mineral_inventories[
                                                                "labels"
                                                            ],
                                                            mineral_inventories[
                                                                "values"
                                                            ],
                                                        )
                                                    ),
                                                ]
                                            ),
                                        )
                                    ),
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            id="commodity-main",
                                            options=[
                                                {"label": commodity, "value": commodity}
                                                for commodity in commodities
                                            ],
                                            value="Nickel (Ni)",
                                            placeholder="Search Commodity",
                                            style={
                                                "margin-bottom": "5px",
                                                "width": "40%",
                                            },
                                        ),
                                        dbc.Spinner(
                                            html.Div(
                                                geo_model_card(gm), id="render-geo-plot"
                                            )
                                        ),
                                    ],
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
            html.Div(id="url-geo", style={"display": "none"}),
            # Dummy div to satisfy Dash callback requirements
            html.Div(id="url-div-geo", style={"display": "none"}),
        ]
    )


layout = render()


@callback(
    Output("render-geo-plot", "children"),
    [Input("commodity-main", "value")],
)
def update_output(selected_commodity):
    if selected_commodity == gm.commodity:
        return geo_model_card(gm)
    selected_commodity = selected_commodity.split()[0]
    gm.update_commodity(selected_commodity)
    gm.init(get_sparql_data=sparql_utils.run_minmod_query)
    return geo_model_card(gm)


@callback(
    Output("url-geo", "children"),
    [Input("clickable-geo-plot", "clickData")],
    prevent_initial_call=True,
)
def open_url(clickData):
    if clickData:
        clicked_dict = clickData["points"][0]
        filtered_df = gm.gdf[
            (gm.gdf["lat"] == clicked_dict["lat"])
            & (gm.gdf["lon"] == clicked_dict["lon"])
        ]
        print(filtered_df)
        return filtered_df["ms.value"]


# Clientside function to open a new tab
clientside_callback(
    """
    function(url) {
        if(url) {
            window.open(url);
        }
    }
    """,
    Output("url-div-geo", "children"),  # Dummy output, we don't use it
    [Input("url-geo", "children")],  # Input is the URL to open
)
