import pandas as pd
from helpers import dataservice_utils


class MineralSite:
    """A class for holding the mineral site data"""

    def __init__(self, commodity):
        self.commodity = commodity.lower()
        self.deposit_types = []
        self.country = []

    def init(self):
        """Initialize and load data from query path using the function reference"""
        self.df = pd.DataFrame(
            self.clean_and_fix(
                dataservice_utils.fetch_api_data(
                    "dedup_mineral_sites/" + self.commodity, ssl_flag=False
                )
            )
        )
        self.df = self.clean_df(self.df)
        self.deposit_types = self.df["Top 1 Deposit Type"].drop_duplicates().to_list()
        self.country = self.df["Country"].drop_duplicates().to_list()

    def update_commodity(self, selected_commodity):
        """sets new commodity"""
        self.commodity = selected_commodity.lower()

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
                "best_loc_wkt",
                "total_tonnage",
                "total_grade",
                "total_contained_metal",
            ]:
                combined_data[field] = data[field]

            results.append(combined_data)
        return results

    def clean_df(self, df):
        """A cleaner method to clean the raw data obtained from the SPARQL endpoint"""
        drop_columns = [
            "commodity",
            "loc_crs",
            "loc_wkt",
            "best_loc_crs",
            "best_loc_wkt",
            "total_contained_metal",
        ]
        df_selected = df.drop(drop_columns, axis=1)

        # rename columns
        col_names = {
            "ms": "Mineral Site URI",
            "ms_name": "Mineral Site Name",
            "ms_type": "Mineral Site Type",
            "ms_rank": "Mineral Site Rank",
            "country": "Country",
            "state_or_province": "State/Province",
            "loc_crs": "Location CRS",
            "loc_wkt": "Location WKT",
            "total_tonnage": "Total Tonnage",
            "total_grade": "Total Grade",
            "top1_deposit_name": "Top 1 Deposit Type",
            "top1_deposit_group": "Top Deposit Group",
            "top1_deposit_environment": "Top 1 Deposit Environment",
            "top1_deposit_confidence": "Top 1 Deposit Classification Confidence",
            "top1_deposit_source": "Top 1 Deposit Classification Confidence",
        }

        df_selected = df_selected.rename(columns=col_names)

        # clean column ms name
        def clean_names(ms_name):
            if isinstance(ms_name, list):
                return ms_name[0]
            return ms_name

        df_selected["Mineral Site Name"] = df_selected["Mineral Site Name"].apply(
            clean_names
        )
        print(df_selected)
        df_selected["Mineral Site Name"] = df_selected.apply(
            lambda row: f"[{row['Mineral Site Name']}]({row['Mineral Site URI'][0]})",
            axis=1,
        )
        df_selected = df_selected.drop(["Mineral Site URI"], axis=1)
        return df_selected
