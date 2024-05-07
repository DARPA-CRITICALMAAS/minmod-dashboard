from string import Template


class GeoMineral:
    """A class holding geo data for the minmod home page"""

    def __init__(self, commodity, query_path):
        self.commodity = commodity
        self.query_path = query_path

    def init(self, get_sparql_data):
        """Initialize and load data from query path using the function reference"""
        query = open(self.query_path).read()
        query = Template(query).substitute(commodity=self.commodity)
        self.df = get_sparql_data(query)

    def update_commodity(self, selected_commodity):
        """sets new commodity"""
        self.commodity = selected_commodity

    def set_gdf(self, gdf):
        """sets new geo dataframe"""
        self.gdf = gdf
