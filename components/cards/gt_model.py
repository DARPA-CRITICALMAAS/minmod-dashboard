import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc

# will be replaced with SPARQL
pivot_df = pd.read_csv("flat_mineral_site_data.v4.csv")


def get_gt_model(pivot_df):
    tonnages = pivot_df["total_tonnage"]
    grades = pivot_df["total_grade"]
    names = pivot_df["ms_name"]
    dtnorm_labels = pivot_df["deposit_type"]
    urls = pivot_df["ms"]  # URLs corresponding to each point

    # Define color for each unique category in 'dtnorm_labels'
    unique_labels = pivot_df["deposit_type"].unique()
    colors = np.linspace(0, 1, len(unique_labels))
    color_map = {label: color for label, color in zip(unique_labels, colors)}

    # Create list of colors for each point
    point_colors = [color_map[label] for label in dtnorm_labels]

    # Create Plotly Figure
    gt_model = go.Figure()

    for d_type in unique_labels:
        df_filtered = pivot_df[pivot_df["deposit_type"] == d_type]
        gt_model.add_trace(
            go.Scatter(
                x=df_filtered["total_tonnage"],
                y=df_filtered["total_grade"],
                mode="markers+text",
                text=df_filtered["ms_name"],
                name=d_type,
                marker=dict(color=color_map[d_type], size=10, symbol="x"),
                textposition="top center",
            )
        )

    # Logarithmic scale and layout adjustments
    gt_model.update_layout(
        xaxis=dict(type="log", title="Tonnage, in metric tons"),
        yaxis=dict(type="log", title="Grade, in percent"),
        title="Grade-Tonnage Model of Mineral Deposits (Nickel)",
        hovermode="closest",
        autosize=True,
        height=800,
        template="plotly_white",
    )

    return gt_model


def gt_model_card(pivot_df):
    return dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(
                    id="clickable-plot",
                    figure=get_gt_model(pivot_df),
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "responsive": True,
                    },
                )
            ]
        )
    )
