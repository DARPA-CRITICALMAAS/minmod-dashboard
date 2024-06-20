from string import Template


class MineralSite:
    """A class for holding the mineral site data"""

    def __init__(self, commodity, query_path):
        self.commodity = commodity
        self.query_path = query_path
        self.deposit_types = []
        self.country = []

    def init(self, get_sparql_data):
        """Initialize and load data from query path using the function reference"""
        query = open(self.query_path).read()
        query = Template(query).substitute(commodity=self.commodity)
        self.df = get_sparql_data(query, values=True)
        self.df = self.clean_df(self.df)
        self.deposit_types = self.df["Deposit Name"].drop_duplicates().to_list()
        self.country = self.df["Country"].drop_duplicates().to_list()

    def update_commodity(self, selected_commodity):
        """sets new commodity"""
        self.commodity = selected_commodity

    def clean_df(self, df):
        """A cleaner method to clean the raw data obtained from the SPARQL endpoint"""
        df.columns = list(map(lambda x: x.split(".value")[0], df.columns))

        selected_columns = [
            "ms",
            "ms_name",
            "deposit_name",
            "total_tonnage_measured",
            "total_tonnage_indicated",
            "total_tonnage_inferred",
            "total_tonnage",
            "total_grade",
            "country",
            "loc_wkt",
        ]

        df_selected = df[selected_columns]
        df_selected.columns = [
            "Mineral Site URI",
            "Mineral Site Name",
            "Deposit Name",
            "Total Tonnage Measured",
            "Total Tonnage Indicated ",
            "Total Tonnage Inferred",
            "Total Tonnage",
            "Total Grade",
            "Country",
            "Loc Wkt",
        ]
        df_selected["Mineral Site Name"] = df_selected.apply(
            lambda row: f"[{row['Mineral Site Name']}]({row['Mineral Site URI']})",
            axis=1,
        )
        df_selected = df_selected.drop(["Mineral Site URI"], axis=1)
        return df_selected
