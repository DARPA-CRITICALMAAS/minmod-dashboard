from helpers import sparql_utils
import time


def get_mineral_inventories():
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
    print(df)
    return {
        "labels": df["commodity.value"].to_list(),
        "values": df["count.value"].to_list(),
    }


def get_triples_count():
    query = """
        SELECT (COUNT(?p) as ?count)
            WHERE {
                ?s ?p ?o .
            }
    """
    df = sparql_utils.run_sparql_query(query)
    print("hello")
    return int(df["count.value"].to_list()[0]) + int(str(time.time())[-1])


def get_mineral_site_count():
    query = """
        SELECT (COUNT(?ms) as ?count)
        WHERE {
            ?ms a :MineralSite .
        }
    """
    df = sparql_utils.run_sparql_query(query)
    return int(df["count.value"].to_list()[0])


if __name__ == "__main__":
    print(get_mineral_inventories())
