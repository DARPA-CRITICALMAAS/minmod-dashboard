import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import dash
from datetime import date
from dash_ag_grid import AgGrid
from components import stats_card, pie_card, gt_model_card

pivot_df = pd.read_csv("flat_mineral_site_data.v4.csv")
commodities = ["Zinc (Zn)", "Nickel (Ni)", "Lead (Pb)"]

dash.register_page(__name__)

layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        dcc.Dropdown(
                            id="commodity",
                            options=[
                                {"label": commodity, "value": commodity}
                                for commodity in commodities
                            ],
                            value="Nickel (Ni)",
                            placeholder="Search Commodity",
                        ),
                        style={
                            "margin-top": "15px",
                            "margin-bottom": "30px",
                        },
                    ),
                    dbc.Row(
                        [gt_model_card(pivot_df)],
                        className="my-2",
                        style={"height": "60vh"},
                    ),
                ],
                style={"height": "80vh"},
            ),
            style={"height": "80vh"},
        ),
        html.Div(id="url", style={"display": "none"}),
        # Dummy div to satisfy Dash callback requirements
        html.Div(id="url-div", style={"display": "none"}),
    ],
)


@callback(
    Output("url", "children"),
    [Input("clickable-plot", "clickData")],
    prevent_initial_call=True,
)
def open_url(clickData):
    if clickData:
        filtered_df = pivot_df[pivot_df["ms_name"] == clickData["points"][0]["text"]]
        return filtered_df["ms"]


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
