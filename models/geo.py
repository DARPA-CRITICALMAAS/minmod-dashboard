import pandas as pd
from helpers import dataservice_utils


class GeoMineral:
    """A class holding geo data for the minmod home page"""

    def __init__(self, commodity):
        self.commodity = commodity.lower()

    def init(self):
        """Initialize and load data from query path using the function reference"""
        self.df = pd.DataFrame(
            self.clean_and_fix(
                dataservice_utils.fetch_api_data(
                    "/dedup_mineral_sites/" + self.commodity, ssl_flag=False
                )
            )
        )

    def clean_and_fix(self, raw_data):
        results = []
        for data in raw_data:
            first_site = data["sites"][0]

            # Combine the first site and highest confidence deposit into a single dictionary
            combined_data = {
                **first_site,
            }

            # Add additional fields from the main data structure
            for field in ["commodity", "best_loc_centroid_epsg_4326"]:
                combined_data[field] = data[field]

            results.append(combined_data)
        return results

    def update_commodity(self, selected_commodity):
        """sets new commodity"""
        self.commodity = selected_commodity.lower()

    def set_gdf(self, gdf):
        """sets new geo dataframe"""
        self.gdf = gdf
