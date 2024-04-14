import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import dash
from datetime import date
from helpers import sparql_utils
from dash_ag_grid import AgGrid
from models import MineralSite


# will be replaced with SPARQL
pivot_df = pd.read_csv("flat_mineral_site_data.v4.csv")
commodities = ["Zinc", "Nickel"]
countries = ["US", "CA"]
column_defs = [
    {
        "header_name": col,
        "field": col,
        "cellRenderer": "markdown",
    }
    for col in pivot_df.columns
]


dash.register_page(__name__)

layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Commodity"),
                                    dcc.Dropdown(
                                        id="commodity",
                                        options=[
                                            {"label": commodity, "value": commodity}
                                            for commodity in commodities
                                        ],
                                        search_value="",
                                        placeholder="Search Commodity",
                                    ),
                                ],
                                width=3,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Deposit Type"),
                                    dcc.Dropdown(
                                        id="deposit_type",
                                        options=[
                                            {
                                                "label": deposit_type,
                                                "value": deposit_type,
                                            }
                                            for deposit_type in list(
                                                set(pivot_df["deposit_type"])
                                            )
                                        ],
                                        multi=True,
                                        search_value="",
                                        placeholder="Search Deposit Type",
                                    ),
                                ],
                                width=3,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Country"),
                                    dcc.Dropdown(
                                        id="country",
                                        options=[
                                            {"label": country, "value": country}
                                            for country in countries
                                        ],
                                        multi=True,
                                        search_value="",
                                        placeholder="Search Country",
                                    ),
                                ],
                                width=3,
                            ),
                        ]
                    ),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    dbc.Row(
                        dbc.Spinner(
                            html.Div(
                                id="mineral-site-results"
                            ),  # Wrapped by dbc.Spinner
                            color="primary",  # Spinner color
                            type="border",  # Spinner type
                            fullscreen=False,  # Set True for fullscreen spinner, False to wrap content
                            size="lg",
                        )
                    ),
                ],
            ),
            style={"height": "100vh"},
        ),
    ]
)


@callback(
    Output("mineral-site-results", "children"),
    [Input("commodity", "value")],
    prevent_initial_call=True,
)
def update_output(selected_commodity):
    print(selected_commodity)
    if selected_commodity:
        # Execute the SPARQL query

        ms = MineralSite(commodity=selected_commodity, query_path="./models/ms.sql")
        ms.init(get_sparql_data=sparql_utils.run_minmod_query)
        df = ms.df
        if df is not None and not df.empty:
            # Convert DataFrame for AgGrid

            column_defs = [
                {
                    "header_name": col,
                    "field": col,
                    "cellRenderer": "urlLink",
                }
                for col in df.columns
            ]
            column_defs.insert(
                0,
                {"headerName": "Row ID", "valueGetter": {"function": "params.node.id"}},
            )

            return html.Div(
                [
                    AgGrid(
                        id="ms_table",
                        style={
                            "width": "100%",
                            "height": "600px",
                        },  # Adjust based on your preference
                        columnDefs=column_defs,
                        rowData=df.to_dict("records"),
                        columnSize="SizeToFit",
                        columnSizeOptions={
                            "defaultMinWidth": 100,
                        },
                        defaultColDef={
                            "resizable": True,
                            "sortable": True,
                            "filter": True,
                        },
                        dashGridOptions={
                            "pagination": True,
                            "paginationPageSize": 20,
                            # "paginationPageSizeSelector": [10, 20, 50, 100],
                            "suppressFieldDotNotation": True,
                            "enableCellTextSelection": True,
                        },
                        csvExportParams={
                            "fileName": "export_data.csv",
                        },
                    ),
                    html.Br(),
                    html.Div(
                        dbc.Button("Download CSV", id="ms-csv-button", n_clicks=0),
                        className="d-grid col-2 mx-auto",
                        style={
                            "float": "right",
                            "margin-top": "-15px",
                            "width": "10%",
                        },
                    ),
                ]
            )

        else:
            return dbc.Alert(
                "No results found or there was an error with the query.",
                color="danger",
            )
    return dbc.Alert("No query received", color="warning")


@callback(
    Output("ms_table", "exportDataAsCsv"),
    Input("ms-csv-button", "n_clicks"),
)
def export_data_as_csv(n_clicks):
    if n_clicks:
        return True
    return False
