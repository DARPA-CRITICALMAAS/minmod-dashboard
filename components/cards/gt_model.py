import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc

import numpy as np
import plotly.graph_objects as go


def get_gt_model(gt):
    """A function to generate grade-tonnage plot."""
    # Define color for each unique category in 'dtnorm_labels'
    unique_labels = sorted(gt.df["top1_deposit_name"].unique())
    colors = np.linspace(0, 1, len(unique_labels))
    color_map = {label: color for label, color in zip(unique_labels, colors)}

    gt_model = go.Figure()

    for d_type in unique_labels:
        df_filtered = gt.df[gt.df["top1_deposit_name"] == d_type]

        hover_template = (
            "<b>MS Name:</b> %{text}<br>"
            + "<b>Grade:</b> %{y}<br>"
            + "<b>Tonnage:</b> %{x}<br>"
            + "<extra></extra>"
        )

        gt_model.add_trace(
            go.Scatter(
                x=df_filtered["total_tonnage"],
                y=df_filtered["total_grade"],
                mode="markers",
                text=df_filtered[
                    "ms_name"
                ],  # Use truncated names for the labels on the plot
                hovertemplate=hover_template,  # Use full names for the hover text
                name=d_type,
                marker=dict(color=color_map[d_type], size=10, symbol="x"),
                textposition="top center",
            )
        )

    # Logarithmic scale and layout adjustments
    gt_model.update_layout(
        xaxis=dict(
            type="log",
            title="Tonnage, in million tonnes",
            title_font=dict(size=23, family="Arial Bold, sans-serif"),
        ),
        yaxis=dict(
            type="log",
            title="Grade, in percent",
            title_font=dict(size=23, family="Arial Bold, sans-serif"),
        ),
        title=f"Grade-Tonnage Model of Mineral Deposits ({gt.commodity})",
        hovermode="closest",
        autosize=True,
        height=750,
        template="plotly_white",
    )

    return gt_model


def gt_model_card(gt):
    """a function to generate grade-tonnade plot in a dbc.Card"""
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
                        "showTips": True,
                    },
                )
            ]
        )
    )
