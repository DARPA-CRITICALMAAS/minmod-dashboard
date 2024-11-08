import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from helpers import kpis
from components import gt_model_card
from models import GradeTonnage

gt = GradeTonnage(commodity="aluminum")
gt.init()

min_distance, max_distance = 0.1, 100
marks = {0.1: "100m", 5: "5km", 20: "20km", 100: "100km"}

dash.register_page(__name__)

layout = html.Div(
    style={
        "display": "flex",
        "flexDirection": "column",
        "minHeight": "100vh",
    },  # Flexbox to ensure proper layout
    children=[
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
                        ],
                        className="my-2",
                    ),
                    # Row containing the slider with label above it and the download button on the right
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.P(
                                            "Geo Spatial Aggregation (Miles)",  # Text above slider
                                            style={
                                                "font-family": '"Open Sans", verdana, arial, sans-serif',
                                                "font-size": "20px",
                                                "text-align": "center",
                                                "font-weight": "bold",
                                            },
                                        ),
                                        dcc.Slider(
                                            id="aggregation-slider",
                                            min=int(min_distance),
                                            max=int(max_distance),
                                            step=0.1,
                                            value=0,  # Set default value to 0 (min_distance)
                                            marks=marks,
                                            tooltip={
                                                "placement": "bottom",
                                                "always_visible": True,
                                                "template": "{value} kms",
                                            },
                                        ),
                                    ],
                                    style={
                                        "text-align": "center",  # Centering the label and slider
                                    },
                                ),
                                width=6,  # Width of the slider column
                                style={
                                    "padding": "40px 0",  # Padding at the top and bottom
                                    "margin": "auto",  # Center the slider and label
                                },
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Download CSV",
                                    id="download-btn",
                                    color="primary",
                                    className="mt-3",
                                ),
                                width="auto",
                                style={
                                    "text-align": "right",  # Align button to the right
                                    "padding-top": "20px",
                                },
                                className="d-flex justify-content-end",  # Ensures it sticks to the right
                            ),
                        ],
                        className="my-3 d-flex justify-content-between align-items-center",  # Ensures alignment and spacing
                    ),
                    dcc.Download(id="download-csv"),  # Download component
                ],
                style={
                    "display": "flex",
                    "flex-direction": "column",  # Flexbox to control the layout
                    "height": "auto",  # Let the card take its natural height
                },
            ),
            style={
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
    Output(
        "aggregation-slider", "value"
    ),  # Reset slider value to 0 on commodity change
    Input("commodity-gt", "value"),
)
def reset_slider_on_commodity_change(selected_commodity):
    return 0  # Reset slider to 0 whenever a new commodity is selected


@callback(
    Output("render-plot", "children"),
    [
        Input("commodity-gt", "value"),
        Input("aggregation-slider", "value"),  # Add slider as input
        State("clickable-plot", "figure"),
    ],
)
def update_output(selected_commodity, proximity_value, figure):
    """A callback to render grade tonnage model based on the commodity selected and proximity value"""

    selected_commodity = selected_commodity.split()[0]

    if selected_commodity.lower() == gt.commodity:
        visible_traces = [
            " ".join(trace["name"].split()[:-1])
            for trace in figure["data"]
            if "hovertemplate" in trace and trace.get("visible", True) == True
        ]
        gt.visible_traces = visible_traces
    else:
        gt.update_commodity(selected_commodity)

    gt.update_proximity(proximity_value)

    try:
        gt.init()
    except:
        return dbc.Alert(
            "No results found or there was an error with the query.",
            color="danger",
        )

    return gt_model_card(gt, proximity_value=proximity_value)  # Pass proximity value


@callback(
    Output("url", "children"),
    Output("clickable-plot", "clickData"),
    Input("clickable-plot", "clickData"),
    prevent_initial_call=True,
)
def open_url(clickData):
    """A callback to open the clicked url on a new tab"""
    if clickData:
        filtered_df = gt.df[gt.df["ms_name"] == clickData["points"][0]["text"]]
        return filtered_df["ms"].tolist()[0], None


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
    State("clickable-plot", "figure"),
    prevent_initial_call=True,  # Ensures it doesn't run on page load
)
def download_csv(n_clicks, figure):
    """Callback to generate CSV data for download only when the button is clicked"""
    if n_clicks:
        # Fetch the latest selected commodity value
        selected_commodity = gt.commodity

        # Assuming gt.df is a pandas DataFrame and filtering specific columns
        df = pd.concat(gt.aggregated_df, ignore_index=True)[
            [
                "ms",
                "ms_name",
                "commodity",
                "top1_deposit_name",
                "lat",
                "lng",
                "total_tonnage",
                "total_grade",
            ]
        ].copy()

        column_names = [
            "Mineral Site URL",
            "Mineral Site Name",
            "Commodity",
            "Top 1 Deposit Name",
            "Latitude",
            "Longitude",
            "Total Tonnage(Million tonnes)",
            "Total Grade(Percent)",
        ]

        visible_traces = [
            " ".join(trace["name"].split()[:-1])
            for trace in figure["data"]
            if "hovertemplate" in trace and trace.get("visible", True) == True
        ]
        df = df[df["top1_deposit_name"].isin(visible_traces)]

        df["ms_name"] = df["ms_name"].apply(
            lambda x: x[1:].replace(":", ",") if ":" in x else x
        )
        df["ms"] = df["ms"].apply(lambda x: x[1:].replace(":", ",") if ":" in x else x)
        # Check if the DataFrame has the necessary columns and data

        # Update Column Names
        df.columns = column_names

        if not df.empty:
            return dcc.send_data_frame(
                df.to_csv, "gt_data.csv"
            )  # Correct usage of send_data_frame
        else:
            return dbc.Alert("No data available to download.", color="danger")
