import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc

import numpy as np
import plotly.graph_objects as go


def get_gt_model(gt):
    """A function to generate grade-tonnage plot."""

    # unique_labels = sorted(gt.df["top1_deposit_name"].unique())

    # Sorting the deposit types based on group count, avg (total_contained_metal/total_tonnage)
    gt.df["avg_metal_per_tonnage"] = (
        gt.df["total_contained_metal"] / gt.df["total_tonnage"]
    )
    grouped = (
        gt.df.groupby("top1_deposit_name")
        .agg({"top1_deposit_name": "count", "avg_metal_per_tonnage": "mean"})
        .rename(columns={"top1_deposit_name": "count"})
    )

    # Sort first by count (number of records) and then by avg_metal_per_tonnage, both in descending order
    unique_labels = grouped.sort_values(
        by=["count", "avg_metal_per_tonnage"], ascending=[False, False]
    ).index.tolist()

    # Define color for each unique category in 'dtnorm_labels'
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
                marker=dict(color=color_map[d_type], size=10, symbol="circle"),
                textposition="top center",
            )
        )

    y_min = gt.df["total_grade"].min()
    y_max = gt.df["total_grade"].max()
    x_min = gt.df["total_tonnage"].min()
    x_max = gt.df["total_tonnage"].max()

    # Add slant lines representing constant metal content
    metal_contents = np.logspace(-9, 10, num=20)
    for metal_content in metal_contents:
        # Tonnage values range for plotting the line
        tonnage_range = np.logspace(-8, 8, 100)
        grade_values = metal_content / tonnage_range  # Grade = Metal Content / Tonnage
        hover_text = f"<span style='color: white;'><b>Contained Metal:</b> {metal_content} Mt</span>"

        gt_model.add_trace(
            go.Scatter(
                y=tonnage_range,
                x=grade_values,
                mode="lines",
                line=dict(color="grey", dash="dash"),
                showlegend=False,
                text=hover_text,
                hoverinfo="text",
            )
        )

    # Logarithmic scale and layout adjustments
    gt_model.update_layout(
        xaxis=dict(
            type="log",
            title="Tonnage, in million tonnes",
            title_font=dict(size=23, family="Arial Bold, sans-serif"),
            range=[np.log10(x_min / 5), np.log10(x_max * 5)],
        ),
        yaxis=dict(
            type="log",
            title="Grade, in percent",
            title_font=dict(size=23, family="Arial Bold, sans-serif"),
            range=[np.log10(y_min / 5), np.log10(y_max * 5)],
        ),
        title=f"Grade-Tonnage Model of Mineral Deposits ({gt.commodity})",
        hovermode="closest",
        autosize=True,
        height=750,
        template="plotly_white",
        dragmode="pan",
    )

    return gt_model


def gt_model_card(gt):
    """a function to generate grade-tonnage plot in a dbc.Card"""
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
                        "scrollZoom": True,
                        "modeBarButtonsToRemove": [
                            "autoScale2d",
                            "lasso2d",
                            "select2d",
                            "zoomIn2d",
                            "zoomOut2d",
                        ],
                    },
                )
            ]
        )
    )
