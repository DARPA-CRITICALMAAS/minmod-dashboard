import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import io
from helpers import kpis
from components import gt_model_card
from models import GradeTonnage

gt = GradeTonnage(commodity="nickel")
gt.init()

min_distance, max_distance = 0, 200

dash.register_page(__name__)

layout = html.Div(
    [
        dcc.Location(id="url-gt", refresh=True),
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        dbc.Col(
                            dbc.Spinner(
                                dcc.Dropdown(
                                    id="commodity-gt",
                                    options=[
                                        {"label": commodity, "value": commodity}
                                        for commodity in kpis.get_commodities()
                                    ],
                                    value="nickel",
                                    placeholder="Search Commodity",
                                ),
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
                                spinner_style={"width": "4rem", "height": "4rem"},
                            ),
                            html.Div(
                                children=[
                                    dcc.Slider(
                                        id="aggregation-slider",
                                        min=int(
                                            min_distance
                                        ),  # minimum proximity in miles
                                        max=int(
                                            max_distance
                                        ),  # maximum proximity in miles
                                        step=1,  # small step size for continuous scrolling
                                        value=int(
                                            min_distance
                                        ),  # default proximity value in miles
                                        marks=None,
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": True,
                                            "template": "{value} miles",
                                        },
                                    )
                                ],
                                style={
                                    "width": "50%",  # Width of the div containing the slider
                                    "margin": "auto",  # Center the slider horizontally
                                    "padding": "40px 0",  # Add padding at the top and bottom
                                },
                            ),
                        ],
                        className="my-2",
                    ),
                    # Ensure this row containing the button stays below the plot
                    dbc.Row(
                        dbc.Col(
                            dbc.Button(
                                "Download CSV",
                                id="download-btn",
                                color="primary",
                                className="mt-3",
                            ),
                            width="auto",
                            style={
                                "text-align": "right",
                                "margin-top": "20px",  # Ensure space between plot and button
                            },
                        ),
                        justify="end",
                        className="mt-auto",  # Push button to the bottom of the card
                    ),
                    dcc.Download(id="download-csv"),  # Download component
                ],
                style={
                    "display": "flex",
                    "flex-direction": "column",  # Flexbox to control the layout
                    "height": "100%",  # Ensure it fills the card
                },
            ),
            style={
                "height": "105vh",
                "margin": "10px",
                "margin-top": "30px",
                "display": "flex",
                "flex-direction": "column",  # Flexbox on the card to stack items vertically
            },
        ),
        html.Div(id="url", style={"display": "none"}),
        html.Div(id="url-div", style={"display": "none"}),  # Dummy div
    ],
)


@callback(
    Output("commodity-gt", "options"),
    Input(
        "url-gt", "pathname"
    ),  # This triggers the callback when the page is refreshed or the URL changes
)
def update_commodity_dropdown(pathname):
    options = [
        {"label": commodity, "value": commodity} for commodity in kpis.get_commodities()
    ]
    return options


@callback(Output("commodity-gt", "value"), Input("commodity-gt", "options"))
def set_default_commodity(options):
    return options[0]["value"] if options else None


@callback(
    Output("render-plot", "children"),
    [
        Input("commodity-gt", "value"),
        Input("aggregation-slider", "value"),  # Add slider as input
    ],
)
def update_output(selected_commodity, proximity_value):
    """A callback to render grade tonnage model based on the commodity selected and proximity value"""
    if selected_commodity == gt.commodity:
        return gt_model_card(
            gt, proximity_value=proximity_value
        )  # Pass proximity value
    selected_commodity = selected_commodity.split()[0]
    gt.update_commodity(selected_commodity)
    try:
        gt.init()
    except:
        return dbc.Alert(
            "No results found or there was an error with the query.",
            color="danger",
        )
    print(proximity_value)
    return gt_model_card(gt, proximity_value=proximity_value)  # Pass proximity value


@callback(
    Output("url", "children"),
    [Input("clickable-plot", "clickData")],
    prevent_initial_call=True,
)
def open_url(clickData):
    """A callback to open the clicked url on a new tab"""
    if clickData:
        filtered_df = gt.df[gt.df["ms_name"] == clickData["points"][0]["text"]]
        return filtered_df["ms"].tolist()[0]


# Clientside function to open a new tab
clientside_callback(
    """
    function(url) {
        if(url) {
            window.open(url);
        }
    }
    """,
    Output("url-div", "children"),
    [Input("url", "children")],  # Input is the URL to open
)


# Fixed Callback to generate CSV and trigger download
@callback(
    Output("download-csv", "data"),
    Input(
        "download-btn", "n_clicks"
    ),  # Only trigger the callback when the button is clicked
    prevent_initial_call=True,  # Ensures it doesn't run on page load
)
def download_csv(n_clicks):
    """Callback to generate CSV data for download only when the button is clicked"""
    if n_clicks:
        # Fetch the latest selected commodity value
        selected_commodity = gt.commodity

        # Assuming gt.df is a pandas DataFrame and filtering specific columns
        df = gt.df[
            [
                "ms",
                "ms_name",
                "commodity",
                "top1_deposit_name",
                "total_tonnage",
                "total_grade",
            ]
        ].copy()

        # Check if the DataFrame has the necessary columns and data
        if not df.empty:
            return dcc.send_data_frame(
                df.to_csv, "gt_data.csv"
            )  # Correct usage of send_data_frame
        else:
            return dbc.Alert("No data available to download.", color="danger")
