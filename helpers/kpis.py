from helpers import sparql_utils
import time


def get_mineral_inventories():
    """a helper function to fetch mineral inventories from SPARQL endpoint"""

    query = """
        SELECT ?commodity (COUNT(?o_inv) AS ?count)
            WHERE {
                ?s :mineral_inventory ?o_inv .
                ?o_inv :category ?cat .
                ?o_inv :commodity [ :name ?commodity ] .
                ?o_inv :ore [ :ore_value ?ore ] .
                ?o_inv :grade [ :grade_value ?grade ] .
            }
            GROUP BY ?commodity
    """
    df = sparql_utils.run_sparql_query(query)
    return {
        "labels": df["commodity.value"].to_list(),
        "values": df["count.value"].to_list(),
    }


def get_triples_count():
    """a helper function to fetch triples count from SPARQL endpoint"""

    query = """
        SELECT (COUNT(?p) as ?count)
            WHERE {
                ?s ?p ?o .
            }
    """
    df = sparql_utils.run_sparql_query(query)
    return int(df["count.value"].to_list()[0]) + int(str(time.time())[-1])


def get_mineral_site_count():
    """a helper function to fetch mineral site count from SPARQL endpoint"""
    query = """
        SELECT (COUNT(?ms) as ?count)
        WHERE {
            ?ms a :MineralSite .
        }
    """
    df = sparql_utils.run_sparql_query(query)
    return int(df["count.value"].to_list()[0])


def get_commodities():
    """a helper function to fetch commodities from SPARQL endpoint"""

    query = """
        SELECT DISTINCT ?commodity 
            WHERE {
                ?s :mineral_inventory ?o_inv .
                ?o_inv :category ?cat .
                ?o_inv :commodity [ :name ?commodity ] .
                ?o_inv :ore [ :ore_value ?ore ] .
                ?o_inv :grade [ :grade_value ?grade ] .
            }
    """
    df = sparql_utils.run_sparql_query(query)
    return df["commodity.value"].to_list()


if __name__ == "__main__":
    print(get_mineral_inventories())
