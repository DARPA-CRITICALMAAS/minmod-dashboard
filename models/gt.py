from string import Template


class GradeTonnage:
    """A class for holding the grade tonnage model plot"""

    def __init__(self, commodity, query_path):
        self.commodity = commodity
        self.query_path = query_path
        self.deposit_types = []
        self.country = []

    def init(self, get_sparql_data):
        """Initialize and load data from query path using the function reference"""
        query = open(self.query_path).read()
        query = Template(query).substitute(commodity=self.commodity)
        self.df = get_sparql_data(query)
        self.df = self.clean_df(self.df)
        self.deposit_types = self.df["deposit_name"].drop_duplicates().to_list()
        self.country = self.df["country"].to_list()

    def update_commodity(self, selected_commodity):
        """sets new commodity"""
        self.commodity = selected_commodity

    def clean_df(self, df):
        """A cleaner method to clean the raw data obtained from the SPARQL endpoint"""
        df.columns = list(map(lambda x: x.split(".value")[0], df.columns))

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
            for text in text_to_clean:
                if text in ms_name:
                    return ms_name.replace(text, "").strip()
            return ms_name

        df["ms_name"] = df["ms_name"].apply(clean_names)
        return df
