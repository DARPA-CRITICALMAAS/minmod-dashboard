import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import dash
from datetime import date
from dash_ag_grid import AgGrid
from components import stats_card, pie_card, gt_model_card
from helpers import sparql_utils
from models import GradeTonnage

# pivot_df = pd.read_csv("flat_mineral_site_data.v4.csv")
gt = GradeTonnage(commodity="Nickel", query_path="./models/gt.sql")
gt.init(get_sparql_data=sparql_utils.run_minmod_query)
commodities = ["Zinc (Zn)", "Nickel (Ni)"]

dash.register_page(__name__)

layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        dbc.Col(
                            dcc.Dropdown(
                                id="commodity",
                                options=[
                                    {"label": commodity, "value": commodity}
                                    for commodity in commodities
                                ],
                                value="Nickel (Ni)",
                                placeholder="Search Commodity",
                            ),
                            width=2,
                        ),
                        style={
                            "margin-top": "15px",
                            "margin-bottom": "30px",
                        },
                    ),
                    dbc.Row(
                        [
                            dbc.Spinner(
                                html.Div(
                                    [gt_model_card(gt)],
                                    id="render-plot",
                                ),
                                size="lg",
                            )
                        ],
                        className="my-2",
                    ),
                ],
            ),
            style={"height": "95vh", "margin": "10px"},
        ),
        html.Div(id="url", style={"display": "none"}),
        # Dummy div to satisfy Dash callback requirements
        html.Div(id="url-div", style={"display": "none"}),
    ],
)


@callback(
    Output("render-plot", "children"),
    [Input("commodity", "value")],
)
def update_output(selected_commodity):
    if selected_commodity == gt.commodity:
        return gt_model_card(gt)
    selected_commodity = selected_commodity.split()[0]
    gt.update_commodity(selected_commodity)
    gt.init(get_sparql_data=sparql_utils.run_minmod_query)
    return gt_model_card(gt)


@callback(
    Output("url", "children"),
    [Input("clickable-plot", "clickData")],
    prevent_initial_call=True,
)
def open_url(clickData):
    if clickData:
        filtered_df = gt.df[gt.df["ms_name.value"] == clickData["points"][0]["text"]]
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
    Output("url-div", "children"),  # Dummy output, we don't use it
    [Input("url", "children")],  # Input is the URL to open
)
