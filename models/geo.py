import pandas as pd
from helpers import dataservice_utils


class GeoMineral:
    """A class holding geo data for the minmod home page"""

    def __init__(self, commodity):
        self.commodity = commodity.lower()

    def init(self):
        """Initialize and load data from query path using the function reference"""
        self.df = pd.DataFrame(
            dataservice_utils.fetch_api_data(
                "/mineral_site_location/" + self.commodity, ssl_flag=False
            )
        )

    def update_commodity(self, selected_commodity):
        """sets new commodity"""
        self.commodity = selected_commodity.lower()

    def set_gdf(self, gdf):
        """sets new geo dataframe"""
        self.gdf = gdf
