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
        self.df = get_sparql_data(query)
        self.deposit_types = self.df["deposit_name.value"].drop_duplicates().to_list()
        self.country = self.df["country.value"].to_list()

    def update_commodity(self, selected_commodity):
        self.commodity = selected_commodity
