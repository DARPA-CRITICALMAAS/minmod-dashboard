import pandas as pd
from helpers import dataservice_utils
from math import radians, sin, cos, sqrt, atan2
from functools import lru_cache
import numpy as np
import time
from datetime import datetime, timedelta

# Define a constant date range (e.g., 30 days)
CACHE_DURATION_DAYS = 3

# Cache storage for the last-used timestamps
cache_access_times = {}


# Decorator to create a cache with a time-based expiration
def lru_cache_with_date_range(maxsize=128):
    def decorator(func):
        # LRU Cache
        @lru_cache(maxsize=maxsize)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Function to check and clear outdated cache entries
        def clear_expired_cache():
            current_time = datetime.now()
            for key in list(cache_access_times.keys()):
                if current_time - cache_access_times[key] > timedelta(
                    days=CACHE_DURATION_DAYS
                ):
                    wrapper.cache_clear()  # Clear the entire cache if one entry is too old
                    break  # You can modify this to clear only the expired keys if needed

        # Wrap the original function to track access times
        def cached_func(*args, **kwargs):
            clear_expired_cache()  # Check and clear expired cache before any function call
            result = wrapper(*args, **kwargs)
            cache_access_times[args] = (
                datetime.now()
            )  # Track when the cache was last used
            return result

        return cached_func

    return decorator


# Earth radius in miles
EARTH_RADIUS = 3959.0  # in miles


class GradeTonnage:
    """A class for holding the grade tonnage model plot"""

    def __init__(self, commodity):
        self.commodity = commodity.lower()
        self.deposit_types = []
        self.country = []
        self.distance_caches = {}
        self.proximity_value = 0
        self.visible_traces = []
        self.aggregated_df = []

    def init(self):
        """Initialize and load data from query path using the function reference"""
        self.df = pd.DataFrame(
            self.clean_and_fix(
                dataservice_utils.fetch_api_data(
                    "/dedup_mineral_sites/" + self.commodity, ssl_flag=False
                )
            )
        )
        self.df = self.clean_df(self.df)
        self.deposit_types = self.df["top1_deposit_name"].drop_duplicates().to_list()
        self.country = self.df["country"].to_list()

        # Apply the function to the 'best_loc_wkt' column and assign the results to 'lat' and 'lng' columns in the same DataFrame
        self.df[["lat", "lng"]] = self.df["best_loc_centroid_epsg_4326"].apply(
            lambda x: pd.Series(self.extract_lat_lng(x))
        )
        if self.proximity_value != 0:
            self.distance_caches = self.compute_all_distances(self.commodity)

    def update_commodity(self, selected_commodity):
        """sets new commodity"""
        self.commodity = selected_commodity.lower()
        self.visible_traces = []
        self.aggregated_df = []

    def update_proximity(self, proximity_value):
        """sets new proximity"""
        self.proximity_value = proximity_value

    def clean_and_fix(self, raw_data):
        results = []
        for data in raw_data:
            first_site = data["sites"][0]
            if len(data["deposit_types"]) == 0:
                continue
            highest_confidence_deposit = max(
                data["deposit_types"], key=lambda x: x["confidence"]
            )

            # Combine the first site and highest confidence deposit into a single dictionary
            combined_data = {
                **first_site,
                **{
                    "top1_deposit_" + k: v
                    for k, v in highest_confidence_deposit.items()
                },
            }

            # Add additional fields from the main data structure
            for field in [
                "commodity",
                "loc_crs",
                "loc_wkt",
                "best_loc_crs",
                "best_loc_centroid_epsg_4326",
                "best_loc_wkt",
                "total_tonnage",
                "total_grade",
                "total_contained_metal",
            ]:
                combined_data[field] = data[field]

            # Setting Unkown Deposit Types
            if not combined_data.get("total_tonnage") or not combined_data.get(
                "total_grade"
            ):
                combined_data["top1_deposit_name"] = "Unknown"

            results.append(combined_data)
        return results

    def clean_df(self, df):
        """A cleaner method to clean the raw data obtained from the SPARQL endpoint"""
        df = df[df["ms_name"].notna()]

        text_to_clean = [
            "NI 43-101 Technical Report for the",
            "NI 43-101 Technical Report on the",
            "NI 43-101 Technical Report - ",
            "NI 43-101 Technical Report ",
            "NI 43-101 Technical Report:",
            "Technical Report and Preliminary Economic Assessment on the",
            "Technical Report on the",
            "Technical Report and PEA for the",
            "Technical Report",
            "Technical Report on the Preliminary Assessment of the",
            "TECHNICAL REPORT"
            "TECHNICAL REPORT AND PRELIMINARY ECONOMIC ASSESSMENT"
            "Preliminary Economic Assessment (PEA) #3 of the",
            "Updated Preliminary Economic Assessment on the",
            "Preliminary Economic Assessment (PEA) of the",
        ]

        def clean_names(ms_name):
            if isinstance(ms_name, list):
                ms_name = ms_name[0]
            for text in text_to_clean:
                if text in ms_name:
                    return ms_name.replace(text, "").strip()
            return ms_name

        df["ms_name_filtered"] = df["ms_name"].apply(clean_names)
        df.loc[:, "ms_name_truncated"] = df["ms_name_filtered"].apply(
            lambda x: " ".join(x.split()[:-3]) if len(x.split()) > 3 else x
        )

        # filtering Unkown deposit types
        df = df[df["top1_deposit_name"] != "Unknown"]

        return df

    # Haversine distance function to calculate distance in miles
    def haversine(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return EARTH_RADIUS * c  # Returns distance in miles

    # Caching approach: Precompute all pairwise distances and store them
    @lru_cache_with_date_range(maxsize=10)
    def compute_all_distances(self, commodity):
        distances = {}
        num_points = len(self.df)

        # Compare each point with every other point and store distances
        for i in range(num_points):
            for j in range(i + 1, num_points):
                distance = self.haversine(
                    self.df.iloc[i]["lat"],
                    self.df.iloc[i]["lng"],
                    self.df.iloc[j]["lat"],
                    self.df.iloc[j]["lng"],
                )
                distances[(i, j)] = distance
                distances[(j, i)] = distance  # Symmetric distances

        return distances

    def extract_lat_lng(self, wkt_point):
        if pd.isnull(wkt_point):
            return pd.Series([np.nan, np.nan])  # Return NaN if the value is null
        # Remove 'POINT(' and ')' and split by space
        wkt_point = wkt_point.replace("POINT (", "").replace(")", "")
        lon, lat = map(float, wkt_point.split())
        return pd.Series([lat, lon])
