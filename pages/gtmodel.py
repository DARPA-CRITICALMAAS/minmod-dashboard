import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from helpers import kpis
from components import get_gt_model
from models import GradeTonnage
import json
from helpers.exceptions import MinModException
from constants import ree_minerals, heavy_ree_minerals, light_ree_minerals

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
                            dcc.Dropdown(
                                id="commodity-gt",
                                options=[
                                    {"label": commodity, "value": commodity}
                                    for commodity in kpis.get_commodities()
                                ],
                                multi=True,
                                placeholder="Search Commodity",
                            ),
                            width=3,
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
                                    [
                                        dcc.Graph(
                                            id="clickable-plot",
                                            figure={},
                                            style={"display": "none"},
                                        )
                                    ],
                                    id="render-plot",
                                ),
                                size="lg",
                                spinner_style={"width": "4rem", "height": "4rem"},
                            ),
                        ],
                        className="my-2",
                    ),
                    # Row containing the slider with label above it and the download button on the right
                    html.Div(
                        id="slider-download-container",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(
                                            [
                                                html.P(
                                                    "Geo Spatial Aggregation (Kilometers)",  # Text above slider
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
                            )
                        ],
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
        dcc.Store(id="gt-agg-data"),
        dcc.Store(id="gt-df-data"),
        dcc.Store(id="select-commodity-data"),
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


# @callback(Output("commodity-gt", "value"), Input("commodity-gt", "options"))
# def set_default_commodity(options):
#     return options[0]["value"] if options else None


@callback(
    Output(
        "aggregation-slider", "value"
    ),  # Reset slider value to 0 on commodity change
    [Input("aggregation-slider", "value"), Input("commodity-gt", "value")],
    State("select-commodity-data", "commodity_data"),
)
def reset_slider_on_commodity_change(value, selected_commodity, commodity_data):
    if selected_commodity != commodity_data:
        return 0  # Reset slider to 0 whenever a new commodity is selected
    else:
        return value


@callback(
    Output("slider-download-container", "style"),
    Input("clickable-plot", "figure"),
)
def toggle_slider_and_download(figure):
    if figure and figure.get("data"):
        return {"display": "block"}
    return {"display": "none"}


@callback(
    [
        Output("gt-agg-data", "agg_data"),
        Output("gt-df-data", "df_data"),
        Output("select-commodity-data", "commodity_data"),
        Output("render-plot", "children"),
        Output("commodity-gt", "value"),
    ],
    [
        Input("commodity-gt", "value"),
        Input("aggregation-slider", "value"),  # Add slider as input
        State("clickable-plot", "figure"),
    ],
    prevent_initial_call=True,
)
def update_output(selected_commodities, proximity_value, figure):
    """A callback to render grade tonnage model based on the commodity selected and proximity value"""

    if not selected_commodities:
        return (
            None,
            None,
            None,
            [
                dcc.Graph(
                    id="clickable-plot",
                    figure={},
                    style={
                        "display": "none",
                    },
                ),
            ],
            [],
        )

    if "REE" in selected_commodities:
        selected_commodities.remove("REE")
        selected_commodities = list(set(selected_commodities + ree_minerals))

    if "HEAVY-REE" in selected_commodities:
        selected_commodities.remove("HEAVY-REE")
        selected_commodities = list(set(selected_commodities + heavy_ree_minerals))

    if "LIGHT-REE" in selected_commodities:
        selected_commodities.remove("LIGHT-REE")
        selected_commodities = list(set(selected_commodities + light_ree_minerals))

    try:
        gt = GradeTonnage(selected_commodities, proximity_value)
        gt.init()
        if proximity_value != 0:
            visible_traces = [
                " ".join(trace["name"].split()[:-1])
                for trace in figure["data"]
                if "hovertemplate" in trace and trace.get("visible", True) == True
            ]
            gt.visible_traces = visible_traces

    except MinModException as e:
        return (
            None,
            None,
            None,
            [
                dbc.Alert(
                    str(e),
                    color="danger",
                ),
                dcc.Graph(
                    id="clickable-plot",
                    figure={},
                    style={
                        "display": "none",
                    },
                ),
            ],
            selected_commodities,
        )

    except Exception as e:
        return (
            None,
            None,
            None,
            [
                dbc.Alert(
                    "No results found or there was an error with the query.",
                    color="danger",
                ),
                dcc.Graph(
                    id="clickable-plot",
                    figure={},
                    style={
                        "display": "none",
                    },
                ),
            ],
            selected_commodities,
        )

    gt, gt_model_plot = get_gt_model(gt, proximity_value)
    return (
        json.dumps(
            [df.to_json(date_format="iso", orient="split") for df in gt.aggregated_df]
        ),
        gt.df.to_json(date_format="iso", orient="split"),
        selected_commodities,
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            id="clickable-plot",
                            figure=gt_model_plot,
                            config={
                                "displayModeBar": True,
                                "displaylogo": False,
                                "responsive": True,
                                "showTips": True,
                                "scrollZoom": True,
                                "modeBarButtonsToRemove": [
                                    "autoScale2d",
                                    "lasso2d",
                                    "select2d",
                                    "zoomIn2d",
                                    "zoomOut2d",
                                ],
                            },
                        )
                    ]
                )
            )
        ],
        selected_commodities,
    )


@callback(
    Output("url", "children"),
    Output("clickable-plot", "clickData"),
    Input("clickable-plot", "clickData"),
    State("gt-df-data", "df_data"),  # Use as state
    prevent_initial_call=True,
)
def open_url(clickData, df_data):
    """A callback to open the clicked url on a new tab"""
    if not df_data:  # Safeguard against unnecessary execution
        raise dash.exceptions.PreventUpdate
    df_data = pd.read_json(df_data, orient="split")
    if clickData:
        filtered_df = df_data[df_data["ms_name"] == clickData["points"][0]["text"]]
        return filtered_df["ms"].tolist()[0], None
    return None, None


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
    Input("download-btn", "n_clicks"),  # Trigger the callback only on button click
    [
        State("gt-agg-data", "agg_data"),  # Use as state
        State("clickable-plot", "figure"),  # Use as state
    ],
    prevent_initial_call=True,  # Ensures the callback does not run on page load
)
def download_csv(n_clicks, agg_data, figure):
    """Callback to generate CSV data for download only when the button is clicked"""
    if not n_clicks:  # Safeguard against unnecessary execution
        raise dash.exceptions.PreventUpdate

    if not agg_data:  # Safeguard against unnecessary execution
        raise dash.exceptions.PreventUpdate

    if not figure:  # Safeguard against unnecessary execution
        raise dash.exceptions.PreventUpdate

    # Parse and aggregate data
    try:
        aggregated_df = [
            pd.read_json(dt, orient="split") for dt in json.loads(agg_data)
        ]
        df = pd.concat(aggregated_df, ignore_index=True)[
            [
                "ms",
                "ms_name",
                "commodity",
                "top1_deposit_name",
                "lat",
                "lon",
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

        # Filter by visible traces
        visible_traces = [
            " ".join(trace["name"].split()[:-1])
            for trace in figure["data"]
            if "hovertemplate" in trace and trace.get("visible", True) == True
        ]
        df = df[df["top1_deposit_name"].isin(visible_traces)]

        # Clean up column data
        df["ms_name"] = df["ms_name"].apply(
            lambda x: x[2:].replace("::", ",") if "::" in x else x
        )
        df["ms"] = df["ms"].apply(
            lambda x: x[2:].replace("::", ",") if "::" in x else x
        )

        # Update column names
        df.columns = column_names

        # Check if DataFrame is empty
        if df.empty:
            print("No data available to download.")
            raise dash.exceptions.PreventUpdate

        # Generate CSV data for download
        return dcc.send_data_frame(df.to_csv, "gt_data.csv")
    except Exception as e:
        print(f"Error generating CSV: {e}")
        raise dash.exceptions.PreventUpdate
