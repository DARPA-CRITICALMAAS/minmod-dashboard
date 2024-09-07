import dash
from dash import html, callback, clientside_callback, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash
from helpers import kpis
from components import stats_card, gt_model_card
from helpers import sparql_utils
from models import GradeTonnage

gt = GradeTonnage(commodity="nickel")
gt.init()

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
                            )
                        ],
                        className="my-2",
                    ),
                ],
            ),
            style={"height": "105vh", "margin": "10px", "margin-top": "30px"},
        ),
        html.Div(id="url", style={"display": "none"}),
        # Dummy div to satisfy Dash callback requirements
        html.Div(id="url-div", style={"display": "none"}),
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
    [Input("commodity-gt", "value")],
)
def update_output(selected_commodity):
    """A callback to render grade tonnage model based on the commodity selected"""
    if selected_commodity == gt.commodity:
        return gt_model_card(gt)
    selected_commodity = selected_commodity.split()[0]
    gt.update_commodity(selected_commodity)
    try:
        gt.init()
    except:
        return dbc.Alert(
            "No results found or there was an error with the query.",
            color="danger",
        )
    return gt_model_card(gt)


@callback(
    Output("url", "children"),
    [Input("clickable-plot", "clickData")],
    prevent_initial_call=True,
)
def open_url(clickData):
    """A callback to open the clicked url on a new tab"""
    if clickData:
        print("$#$##$")
        print(clickData)
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
