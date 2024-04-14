import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc


def get_gt_model(gt):
    # Define color for each unique category in 'dtnorm_labels'
    unique_labels = gt.df["deposit_name.value"].unique()
    colors = np.linspace(0, 1, len(unique_labels))
    color_map = {label: color for label, color in zip(unique_labels, colors)}

    # Create Plotly Figure
    gt_model = go.Figure()

    for d_type in unique_labels:
        df_filtered = gt.df[gt.df["deposit_name.value"] == d_type]
        gt_model.add_trace(
            go.Scatter(
                x=df_filtered["total_tonnage.value"],
                y=df_filtered["total_grade.value"],
                mode="markers+text",
                text=df_filtered["ms_name.value"],
                name=d_type,
                marker=dict(color=color_map[d_type], size=10, symbol="x"),
                textposition="top center",
            )
        )

    # Logarithmic scale and layout adjustments
    gt_model.update_layout(
        xaxis=dict(type="log", title="Tonnage, in million tonnes"),
        yaxis=dict(type="log", title="Grade, in percent"),
        title=f"Grade-Tonnage Model of Mineral Deposits ({gt.commodity})",
        hovermode="closest",
        autosize=True,
        height=750,
        template="plotly_white",
    )

    return gt_model


def gt_model_card(gt):
    return dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(
                    id="clickable-plot",
                    figure=get_gt_model(gt),
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "responsive": True,
                    },
                )
            ]
        )
    )
