import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import dash
from components import stats_card, pie_card, geo_model_card
from helpers import kpis
from models import GeoMineral
from helpers import sparql_utils
import time
from dash import callback_context
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path="/")

mineral_inventories = kpis.get_mineral_inventories()
gm = GeoMineral(commodity="nickel", query_path="./models/sql/min.sql")
gm.init(get_sparql_data=sparql_utils.run_minmod_query)


def render():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Row(
                                    [
                                        dbc.Row(
                                            dbc.Card(
                                                html.Div(
                                                    [
                                                        html.H3(
                                                            ["Number of Mineral Sites"]
                                                        ),
                                                        dbc.Spinner(
                                                            html.H4(
                                                                ["empty"],
                                                                id="mineral-sites-count-card",
                                                            ),
                                                        ),
                                                    ],
                                                    className=f"border-sucess border-start border-5",
                                                ),
                                                className="text-center text-nowrap my-2 p-2",
                                            )
                                        ),
                                        dbc.Row(
                                            dbc.Spinner(
                                                html.Div(
                                                    html.Div(
                                                        style={"margin-top": "50px"}
                                                    ),
                                                    id="pie--card--min",
                                                ),
                                            )
                                        ),
                                    ]
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Row(
                                    [
                                        dbc.Row(
                                            dbc.Card(
                                                html.Div(
                                                    [
                                                        html.H3(
                                                            ["Number of Inventories"]
                                                        ),
                                                        dbc.Spinner(
                                                            html.H4(
                                                                ["empty"],
                                                                id="inventory-count-card",
                                                            ),
                                                        ),
                                                    ],
                                                    className=f"border-sucess border-start border-5",
                                                ),
                                                className="text-center text-nowrap my-2 p-2",
                                            )
                                        ),
                                        dbc.Row(
                                            dbc.Spinner(
                                                html.Div(
                                                    html.Div(
                                                        style={"margin-top": "50px"}
                                                    ),
                                                    id="pie--card",
                                                ),
                                            )
                                        ),
                                    ]
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Row(
                                    [
                                        dbc.Row(
                                            dbc.Card(
                                                html.Div(
                                                    [
                                                        html.H3(
                                                            ["Number of Documents"]
                                                        ),
                                                        dbc.Spinner(
                                                            html.H4(
                                                                ["empty"],
                                                                id="documents-count-card",
                                                            ),
                                                        ),
                                                    ],
                                                    className=f"border-sucess border-start border-5",
                                                ),
                                                className="text-center text-nowrap my-2 p-2",
                                            )
                                        ),
                                        dbc.Row(
                                            dbc.Spinner(
                                                html.Div(
                                                    html.Div(
                                                        style={"margin-top": "50px"}
                                                    ),
                                                    id="pie--card--docs",
                                                ),
                                            )
                                        ),
                                    ]
                                ),
                                width=4,
                            ),
                        ],
                        style={
                            "padding-left": "40px",
                            "margin-bottom": "30px",
                            "margin-top": "20px",
                        },
                    ),
                    dbc.Row(),
                    dbc.Row(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        dbc.Row(html.H3("Map View")),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Spinner(
                                                        dcc.Dropdown(
                                                            id="commodity-main",
                                                            options=[
                                                                {
                                                                    "label": commodity,
                                                                    "value": commodity,
                                                                }
                                                                for commodity in kpis.get_commodities()
                                                            ],
                                                            value="nickel",
                                                            placeholder="Search Commodity",
                                                            style={
                                                                "margin-bottom": "5px",
                                                                "margin-top": "20px",
                                                                "margin-left": "5px",
                                                            },
                                                        ),
                                                    ),
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    dbc.Button(
                                                        html.I(
                                                            " Toggle Map View",
                                                            className="fas fa-sun",
                                                        ),
                                                        id="theme-toggle-button",
                                                        color="default",
                                                        className="mr-1",
                                                        style={
                                                            "border": "1px",
                                                            "margin-top": "20px",
                                                        },
                                                    ),
                                                    width=3,
                                                ),
                                            ],
                                            className="g-0",
                                        ),
                                        dbc.Spinner(
                                            html.Div(
                                                geo_model_card(gm, "light"),
                                                id="render-geo-plot",
                                            )
                                        ),
                                    ]
                                )
                            )
                        ],
                        style={"padding-left": "40px"},
                    ),
                ],
                align="start",
            ),
            dcc.Interval(
                id="interval-component",
                interval=12
                * 60
                * 60
                * 1000,  # Trigger refresh every 12 hours; adjust as needed
                n_intervals=0,
            ),
            html.Div(id="url-geo", style={"display": "none"}),
            # Dummy div to satisfy Dash callback requirements
            html.Div(id="url-div-geo", style={"display": "none"}),
        ]
    )


layout = render()


@callback(
    [Output("documents-count-card", "children")],
    [Input("interval-component", "n_intervals")],
)
def update_all_cards(_):
    """A callback to handle all the KPI card updates"""
    return ["{:,}".format(kpis.get_documents_count())]


@callback(
    [Output("inventory-count-card", "children")],
    [Input("interval-component", "n_intervals")],
)
def update_all_cards(_):
    """A callback to handle the KPI card updates"""
    return ["{:,}".format(kpis.get_inventory_count())]


@callback(
    [Output("mineral-sites-count-card", "children")],
    [Input("interval-component", "n_intervals")],
)
def update_all_cards(_):
    """A callback to handle the KPI card updates"""
    return ["{:,}".format(kpis.get_mineral_site_count())]


@callback(
    [Output("pie--card--min", "children")],
    [Input("interval-component", "n_intervals")],
)
def update_all_cards(_):
    """A callback to handle the PI chart updates"""
    ms_per_commodity = kpis.get_mineral_site_count_per_commodity()
    return [
        html.Div(
            pie_card(
                ms_per_commodity["labels"],
                ms_per_commodity["values"],
                "Mineral Site Distribution By Commodity",
            ),
        )
    ]


@callback(
    [Output("pie--card--docs", "children")],
    [Input("interval-component", "n_intervals")],
)
def update_all_cards(_):
    """A callback to handle the PI chart updates"""
    docs_per_commodity = kpis.get_docs_per_commodity()
    return [
        html.Div(
            pie_card(
                docs_per_commodity["labels"],
                docs_per_commodity["values"],
                "Document Distribution By Commodity",
            )
        )
    ]


@callback(
    [Output("pie--card", "children")],
    [Input("interval-component", "n_intervals")],
)
def update_all_cards(_):
    """A callback to handle the PI chart updates"""
    mineral_inventories = kpis.get_mineral_inventories()
    return [
        html.Div(
            pie_card(
                mineral_inventories["labels"],
                mineral_inventories["values"],
                "Inventory Distribution By Commodity",
            )
        )
    ]


@callback(
    Output("url-geo", "children"),
    [Input("clickable-geo-plot", "clickData")],
    prevent_initial_call=True,
)
def open_url(clickData):
    """A callback to handle geo map plot based on the user click"""
    if clickData:
        clicked_dict = clickData["points"][0]
        filtered_df = gm.gdf[
            (gm.gdf["lat"] == clicked_dict["lat"])
            & (gm.gdf["lon"] == clicked_dict["lon"])
        ]
        return filtered_df["ms.value"]


@callback(
    [Output("theme-toggle-button", "children"), Output("render-geo-plot", "children")],
    [Input("theme-toggle-button", "n_clicks"), Input("commodity-main", "value")],
    [
        State("theme-toggle-button", "children"),
        State("render-geo-plot", "children"),
        State("theme-toggle-button", "n_clicks"),
    ],
)
def update_ui(n_clicks_theme, selected_commodity, current_icon, _, n_clicks_previous):
    """A callback to handle map theme and render map based on the commodity selected"""
    # Initial state when no button has been clicked yet
    if n_clicks_theme is None:
        n_clicks_theme = 0
    if n_clicks_previous is None:
        n_clicks_previous = 0

    trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    # Determine current theme based on button click count
    if trigger_id == "theme-toggle-button":
        # Toggle theme based on the count of button clicks
        is_dark = n_clicks_theme % 2 == 1
        new_theme = "dark" if is_dark else "light"
        new_class = "fas fa-moon" if is_dark else "fas fa-sun"
        return [
            html.I(" Toggle Map View", className=new_class),
            geo_model_card(gm, new_theme),
        ]
    elif trigger_id == "commodity-main":
        # Maintain the theme based on the last button click count
        is_dark = n_clicks_previous % 2 == 1
        current_theme = "dark" if is_dark else "light"
        if selected_commodity == gm.commodity:
            return [current_icon, geo_model_card(gm, current_theme)]
        selected_commodity = selected_commodity.split()[0]
        gm.update_commodity(selected_commodity)
        gm.init(get_sparql_data=sparql_utils.run_minmod_query)
        return [current_icon, geo_model_card(gm, current_theme)]
    else:
        raise PreventUpdate


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
