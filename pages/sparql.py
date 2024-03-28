import dash
from dash import html, callback, Input, Output
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from helpers import sparql_utils
from dash_ag_grid import AgGrid
import monaco_editor

editor_options = {
    "autoIndent": "full",
    "contextmenu": True,
    "fontFamily": "monospace",
    "fontSize": 13,
    "lineHeight": 24,
    "matchBrackets": "always",
    "minimap": {
        "enabled": False,
    },
    "scrollbar": {
        "horizontalSliderSize": 4,
        "verticalSliderSize": 18,
    },
    "selectOnLineNumbers": True,
    "roundedSelection": False,
    "readOnly": False,
    "cursorStyle": "line",
    "automaticLayout": True,
}

dash.register_page(__name__)

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Row(
                    dbc.Col(
                        monaco_editor.MonacoEditor(
                            id="sparql-query",
                            value="# Enter SPARQL query below",
                            height="40vh",
                            defaultLanguage="sparql",
                            options=editor_options,
                        )
                    ),
                    align="center",
                ),
                dbc.Row(
                    html.Div(
                        dbc.Button("Run Query", id="run-query", color="primary"),
                        className="d-grid col-2 mx-auto",
                        style={
                            "float": "right",
                            "width": "10%",
                        },
                    ),
                    style={
                        "margin-top": "15px",
                        "margin-bottom": "15px",
                    },
                ),
                dbc.Row(
                    dbc.Spinner(
                        html.Div(id="query-results"),  # Wrapped by dbc.Spinner
                        color="primary",  # Spinner color
                        type="border",  # Spinner type
                        fullscreen=False,  # Set True for fullscreen spinner, False to wrap content
                        size="lg",
                    )
                ),
                dbc.Row(
                    [
                        dbc.Col(id="query-alert", width=12),  # For displaying alerts
                    ],
                    align="start",
                ),
            ],
            style={"margin-left": "10px", "margin-top": "10px"},
        ),
        html.Br(),
    ]
)


@callback(
    Output("query-results", "children"),
    [Input("run-query", "n_clicks")],
    [State("sparql-query", "value")],
    prevent_initial_call=True,
)
def update_output(n_clicks, query):
    if query:
        # Execute the SPARQL query
        df = sparql_utils.run_minmod_query(query, values=True)
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

            return html.Div(
                [
                    AgGrid(
                        id="query_table",
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
                        dbc.Button("Download CSV", id="csv-button", n_clicks=0),
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
    Output("query_table", "exportDataAsCsv"),
    Input("csv-button", "n_clicks"),
)
def export_data_as_csv(n_clicks):
    if n_clicks:
        return True
    return False
