from string import Template


class GeoMineral:
    def __init__(self, commodity, query_path):
        self.commodity = commodity
        self.query_path = query_path

    def init(self, get_sparql_data):
        query = open(self.query_path).read()
        query = Template(query).substitute(commodity=self.commodity)
        self.df = get_sparql_data(query)

    def update_commodity(self, selected_commodity):
        self.commodity = selected_commodity

    def set_gdf(self, gdf):
        self.gdf = gdf
