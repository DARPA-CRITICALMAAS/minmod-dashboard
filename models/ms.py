from string import Template


class MineralSite:
    def __init__(self, commodity, query_path):
        self.commodity = commodity
        self.query_path = query_path
        self.deposit_types = []
        self.country = []

    def init(self, get_sparql_data):
        query = open(self.query_path).read()
        query = Template(query).substitute(commodity=self.commodity)
        self.df = get_sparql_data(query, values=True)
        self.df = self.clean_df(self.df)
        self.deposit_types = self.df["Deposit Name"].drop_duplicates().to_list()
        self.country = self.df["Country"].drop_duplicates().to_list()

    def update_commodity(self, selected_commodity):
        self.commodity = selected_commodity

    def clean_df(self, df):
        df.columns = list(map(lambda x: x.split(".value")[0], df.columns))
        df.columns = [
            "Mineral Site URI",
            "Mineral Site Name",
            "Deposit Name",
            "Total Tonnage Measured",
            "Total Tonnage Indicated ",
            "Total Tonnage Inferred",
            "Total Contained Measured",
            "Total Contained Indicated",
            "Total Contained Inferred",
            "Total Tonnage",
            "Total Contained Metal",
            "Total Grade",
            "Country",
            "Loc Wkt",
        ]
        return df
