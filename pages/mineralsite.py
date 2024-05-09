import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import dash
from datetime import date
from helpers import kpis
from helpers import sparql_utils
from dash_ag_grid import AgGrid
from models import MineralSite
from dash.exceptions import PreventUpdate


dash.register_page(__name__)

layout = html.Div(
    [
        dcc.Location(id="url-ms", refresh=True),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Commodity"),
                        dbc.Spinner(
                            dcc.Dropdown(
                                id="commodity-ms",
                                options=[
                                    {"label": commodity, "value": commodity}
                                    for commodity in kpis.get_commodities()
                                ],
                                search_value="",
                                placeholder="Search Commodity",
                            ),
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dbc.Label("Deposit Type"),
                        dcc.Dropdown(
                            id="deposit_type",
                            options=[],
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
                            options=[],
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
        dbc.Row(
            dbc.Spinner(
                html.Div(id="mineral-site-results"),  # Wrapped by dbc.Spinner
                color="primary",  # Spinner color
                type="border",  # Spinner type
                fullscreen=False,  # Set True for fullscreen spinner, False to wrap content
                size="lg",
            )
        ),
    ],
    style={"margin": "20px"},
)


@callback(
    Output("commodity-ms", "options"),
    Input(
        "url-ms", "pathname"
    ),  # This triggers the callback when the page is refreshed or the URL changes
)
def update_commodity_dropdown(pathname):
    options = [
        {"label": commodity, "value": commodity} for commodity in kpis.get_commodities()
    ]
    return options


@callback(
    [
        Output("deposit_type", "options"),
        Output("country", "options"),
        Output("mineral-site-results", "children"),
    ],
    [
        Input("commodity-ms", "value"),
        Input("deposit_type", "value"),
        Input("country", "value"),
    ],
    [State("deposit_type", "options"), State("country", "options")],
    prevent_initial_call=True,
)
def update_dashboard(
    selected_commodity,
    selected_deposit_types,
    selected_countries,
    current_deposit_options,
    current_country_options,
):
    """A callback to update the table data, and dropdown values"""
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "commodity-ms" and selected_commodity:
        deposit_options = []
        country_options = []
        # Initial grid update with new commodity selection
        ms = MineralSite(commodity=selected_commodity, query_path="./models/sql/ms.sql")
        try:
            ms.init(get_sparql_data=sparql_utils.run_minmod_query)
            df = ms.df
            # Update deposit type options based on the selected commodity
            deposit_options = [{"label": dt, "value": dt} for dt in ms.deposit_types]

            # Update country options based on the selected commodity
            country_options = [
                {"label": country, "value": country} for country in ms.country
            ]
        except:
            return (
                deposit_options,
                country_options,
                dbc.Alert(
                    "No results found or there was an error with the query.",
                    color="danger",
                ),
            )

        grid_content = update_grid(df)
        return deposit_options, country_options, grid_content

    elif trigger_id in ["deposit_type", "country"]:
        # Refilter based on both deposit type and country
        ms = MineralSite(commodity=selected_commodity, query_path="./models/sql/ms.sql")
        try:
            ms.init(get_sparql_data=sparql_utils.run_minmod_query)
            df = ms.df

            if selected_deposit_types:
                df = df[df["Deposit Name"].isin(selected_deposit_types)]
                # Refilter countries based on deposit type
                filtered_countries = df["Country"].unique()
                country_options = [
                    {"label": country, "value": country}
                    for country in filtered_countries
                ]
            else:
                country_options = current_country_options

            if selected_countries:
                df = df[df["Country"].isin(selected_countries)]

        except:
            return (
                current_deposit_options,
                current_country_options,
                dbc.Alert(
                    "No results found or there was an error with the query.",
                    color="danger",
                ),
            )

        grid_content = update_grid(df)
        return current_deposit_options, country_options, grid_content

    raise PreventUpdate


def update_grid(df):
    df = sparql_utils.infer_and_convert_types(df, round_flag=True)
    if df is not None and not df.empty:
        column_defs = []
        for col in df.columns:
            if col == "Mineral Site Name":
                column_defs.append(
                    {
                        "headerName": col,
                        "field": col,
                        "cellRenderer": "markdown",
                        "linkTarget": "_blank",
                    }
                )
            else:
                column_defs.append(
                    {"headerName": col, "field": col, "cellRenderer": "urlLink"}
                )

        column_defs.insert(
            0, {"headerName": "Row ID", "valueGetter": {"function": "params.node.id"}}
        )
        return html.Div(
            [
                AgGrid(
                    id="ms_table",
                    style={"width": "100%", "height": "70vh"},
                    columnDefs=column_defs,
                    rowData=df.to_dict("records"),
                    columnSize="responsiveSizeToFit",
                    # columnSizeOptions={"defaultMaxWidth": 20},
                    defaultColDef={"resizable": True, "sortable": True, "filter": True},
                    dashGridOptions={
                        "pagination": True,
                        "paginationPageSize": 20,
                        "suppressFieldDotNotation": True,
                        "enableCellTextSelection": True,
                    },
                    csvExportParams={"fileName": "export_data.csv"},
                ),
                html.Br(),
                html.Div(
                    dbc.Button("Download CSV", id="ms-csv-button", n_clicks=0),
                    className="d-grid col-2 mx-auto",
                    style={"float": "right", "margin-top": "-15px", "width": "10%"},
                ),
            ]
        )
    return dbc.Alert("No results found.", color="danger")


@callback(
    Output("ms_table", "exportDataAsCsv"),
    Input("ms-csv-button", "n_clicks"),
)
def export_data_as_csv(n_clicks):
    """A callback to handle the download button"""
    if n_clicks:
        return True
    return False
