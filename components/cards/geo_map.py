import dash
from dash import dcc, html
import plotly.express as px
import geopandas as gpd
from shapely.wkt import loads
import dash_bootstrap_components as dbc
from dash import dcc


def safe_wkt_load(wkt_str):
    """a function to safely load WKT strings to geometry objects"""
    try:
        return loads(wkt_str)
    except Exception as e:
        print(f"Error loading WKT: {e}")
        return None


def get_geo_model(gm, theme):
    """a function to get a scatter mapbox plot"""

    # check if invalid invalid_geo_df = gdf[~gdf["lat"].between(-90, 90) | ~gdf["lon"].between(-180, 180)]
    gm.df = gm.df[(gm.df["lat"].between(-90, 90)) & (gm.df["lon"].between(-180, 180))]

    geo_model = px.scatter_mapbox(
        gm.df,
        lat="lat",
        lon="lon",
        hover_name="ms_name",
        zoom=2,
        color_discrete_sequence=["red"],
        size_max=30,
        height=900,
    )

    geo_model.update_traces(
        hovertemplate=(
            "<b>MS Name:</b> %{hovertext}<br>"
            + "<b>Latitude:</b> %{lat}<br>"
            + "<b>Longitude:</b> %{lon}<br>"
            + "<extra></extra>"
        )
    )

    # Set the hovertext to be the "ms_name"
    geo_model.update_traces(hovertext=gm.df["ms_name"])

    # Setting Map Style and toggle based on theme
    if theme == "light":
        geo_model.update_layout(mapbox_style="open-street-map")
    else:
        geo_model.update_layout(
            mapbox_style="white-bg",
            mapbox_layers=[
                {
                    "below": "traces",
                    "sourcetype": "raster",
                    "sourceattribution": "United States Geological Survey",
                    "source": [
                        "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                    ],
                }
            ],
        )
    geo_model.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 10})

    return geo_model


def geo_model_card(geo_min, theme):
    """a function to get return scatter mapbox plot in a dbc.Card"""
    return dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(
                    id="clickable-geo-plot",
                    figure=get_geo_model(geo_min, theme),
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "responsive": True,
                    },
                ),
            ]
        )
    )
