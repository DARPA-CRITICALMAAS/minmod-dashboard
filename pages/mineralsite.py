import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import dash
from datetime import date
from dash_ag_grid import AgGrid


# will be replaced with SPARQL
pivot_df = pd.read_csv("flat_mineral_site_data.v4.csv")
commodities = ["Zinc (Zn)", "Nickel (Ni)", "Lead (Pb)"]
countries = ["US", "CA"]
column_defs = [
    {
        "header_name": col,
        "field": col,
        "cellRenderer": "markdown",
    }
    for col in pivot_df.columns
]

# will be replaced with SPARQL
labels = ["Nickel", "Zinc"]
values = [1049, 1078]

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
                            dbc.Col(
                                [
                                    dbc.Label("Date Range"),
                                    html.Br(),
                                    dcc.DatePickerRange(
                                        id="my-date-picker-range",
                                        min_date_allowed=date(1995, 8, 5),
                                        max_date_allowed=date(2024, 12, 1),
                                        initial_visible_month=date(2024, 3, 5),
                                        # end_date=date.today(),
                                    ),
                                ],
                                width=3,
                            ),
                        ]
                    ),
                    html.Br(),
                    dbc.Row(
                        AgGrid(
                            id="query_table",
                            style={
                                "width": "100%",
                                "height": "80vh",
                            },  # Adjust based on your preference
                            columnDefs=column_defs,
                            rowData=pivot_df.to_dict("records"),
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
                                "suppressFieldDotNotation": True,
                                "enableCellTextSelection": True,
                            },
                            csvExportParams={
                                "fileName": "export_data.csv",
                            },
                        )
                    ),
                ],
            ),
            style={"height": "100vh"},
        ),
    ]
)
