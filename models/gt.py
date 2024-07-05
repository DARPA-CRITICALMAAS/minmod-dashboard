import pandas as pd
from helpers import dataservice_utils


class GradeTonnage:
    """A class for holding the grade tonnage model plot"""

    def __init__(self, commodity):
        self.commodity = commodity.lower()
        self.deposit_types = []
        self.country = []

    def init(self):
        """Initialize and load data from query path using the function reference"""
        self.df = pd.DataFrame(
            dataservice_utils.fetch_api_data(
                "hyper_mineral_sites/" + self.commodity, ssl_flag=False
            )
        )
        self.df = self.clean_df(self.df)
        self.deposit_types = self.df["top1_deposit_type"].drop_duplicates().to_list()
        self.country = self.df["country"].to_list()

    def update_commodity(self, selected_commodity):
        """sets new commodity"""
        self.commodity = selected_commodity.lower()

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
        return df
