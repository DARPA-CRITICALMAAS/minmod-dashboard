import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc

import numpy as np
import plotly.graph_objects as go
from math import radians, sin, cos, sqrt, atan2

# Earth radius in miles
EARTH_RADIUS = 3959.0  # in miles


# Haversine distance function to calculate distance in miles
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return EARTH_RADIUS * c  # Returns distance in miles


# Caching approach: Precompute all pairwise distances and store them
def compute_all_distances(df):
    distances = {}
    num_points = len(df)

    # Compare each point with every other point and store distances
    for i in range(num_points):
        for j in range(i + 1, num_points):
            distance = haversine(
                df.iloc[i]["lat"],
                df.iloc[i]["lng"],
                df.iloc[j]["lat"],
                df.iloc[j]["lng"],
            )
            distances[(i, j)] = distance
            distances[(j, i)] = distance  # Symmetric distances

    return distances


def extract_lat_lng(wkt_point):
    if pd.isnull(wkt_point):
        return pd.Series([np.nan, np.nan])  # Return NaN if the value is null
    # Remove 'POINT(' and ')' and split by space
    wkt_point = wkt_point.replace("POINT (", "").replace(")", "")
    lon, lat = map(float, wkt_point.split())
    return pd.Series([lat, lon])


# Function to calculate the min and max distances between points (cached)
def calculate_min_max_distance(distances):
    min_distance = min(distances.values())
    max_distance = max(distances.values())
    return min_distance, max_distance


def greedy_weighted_avg_aggregation(df, distances, proximity_threshold):
    # Create an empty list to store aggregated data
    aggregated_data = []
    processed_indices = set()

    # Loop through all points
    for i in range(len(df)):
        if i in processed_indices:
            continue  # Skip already processed points

        # Start with the current point as the center
        group = [i]
        processed_indices.add(i)

        # Find all nearby points within the proximity threshold
        for j in range(len(df)):
            if i != j and j not in processed_indices:
                # Ensure that the distance is valid and is not None
                distance = distances.get((i, j))
                if distance is not None and distance < proximity_threshold:
                    group.append(j)
                    processed_indices.add(j)

        # Calculate the weighted average of the grade using tonnage as weights
        total_tonnage = df.iloc[group]["total_tonnage"].sum()
        weighted_grade = np.average(
            df.iloc[group]["total_grade"], weights=df.iloc[group]["total_tonnage"]
        )

        # Combine ms_name values from the group
        if len(df.iloc[group]["ms_name"]) > 1:
            combined_ms_name = ": " + ": ".join(df.iloc[group]["ms_name"])
        else:
            combined_ms_name = ": ".join(df.iloc[group]["ms_name"])

        aggregated_data.append(
            {
                "total_grade": weighted_grade,
                "total_tonnage": total_tonnage,
                "ms_name": combined_ms_name,  # Add the combined ms_name
            }
        )

    return pd.DataFrame(aggregated_data)


def get_gt_model(gt, proxmity_value=0):
    """A function to generate grade-tonnage plot."""

    # unique_labels = sorted(gt.df["top1_deposit_name"].unique())

    # Sorting the deposit types based on group count, avg (total_contained_metal/total_tonnage)
    gt.df["avg_metal_per_tonnage"] = (
        gt.df["total_contained_metal"] / gt.df["total_tonnage"]
    )

    # Apply the function to the 'best_loc_wkt' column and assign the results to 'lat' and 'lng' columns in the same DataFrame
    gt.df[["lat", "lng"]] = gt.df["best_loc_centroid_epsg_4326"].apply(
        lambda x: pd.Series(extract_lat_lng(x))
    )

    # Compute all distances once and store them in a cache
    distances_cache = compute_all_distances(gt.df)

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

        aggregated_df = greedy_weighted_avg_aggregation(
            df_filtered, distances_cache, proxmity_value
        )

        hover_template = (
            "<b>MS Name:</b> %{text}<br>"
            + "<b>Grade:</b> %{y}<br>"
            + "<b>Tonnage:</b> %{x}<br>"
            + "<extra></extra>"
        )

        # Get the count of deposits for this type
        deposit_count = grouped.loc[d_type, "count"]

        gt_model.add_trace(
            go.Scatter(
                x=aggregated_df["total_tonnage"],
                y=aggregated_df["total_grade"],
                mode="markers",
                text=aggregated_df["ms_name"].apply(
                    lambda x: x.replace(":", "<br>")
                ),  # Use truncated names for the labels on the plot
                hovertemplate=hover_template,  # Use full names for the hover text
                name=f"{d_type} ({deposit_count})",  # Add the count of deposits to the legend name
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


def gt_model_card(gt, proximity_value=0):
    """a function to generate grade-tonnage plot in a dbc.Card"""
    return dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(
                    id="clickable-plot",
                    figure=get_gt_model(gt, proximity_value),
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
