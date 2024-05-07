from helpers import sparql_utils
import numpy as np


def get_mineral_inventories():
    """a helper function to fetch mineral inventories from SPARQL endpoint"""

    query = """
        SELECT DISTINCT ?comm (COUNT(DISTINCT ?mi) AS ?inv_count)
            WHERE {
                ?mi a :MineralInventory .
                ?mi :commodity/:name ?comm .
                ?mi :ore ?ore .
            }
            GROUP BY ?comm
    """
    df = sparql_utils.run_sparql_query(query)
    return {
        "labels": df["comm.value"].to_list(),
        "values": df["inv_count.value"].to_list(),
    }


def get_mineral_site_count():
    """a helper function to fetch mineral site count from SPARQL endpoint"""
    query = """
        SELECT (COUNT(DISTINCT ?ms) AS ?site_count)
            WHERE {
                ?ms a :MineralSite .
                ?ms :mineral_inventory ?mi .
                ?mi :commodity/:name ?comm .
                ?mi :ore ?ore .
            }
    """
    df = sparql_utils.run_sparql_query(query)
    return int(df["site_count.value"].to_list()[0])


def get_mineral_site_count_per_commodity():
    """a helper function to fetch mineral site count from SPARQL endpoint"""
    query = """
        SELECT ?comm (COUNT(DISTINCT ?ms) AS ?site_count)
            WHERE {
                ?ms a :MineralSite .
                ?ms :mineral_inventory ?mi .
                ?mi :commodity/:name ?comm .
                ?mi :ore ?ore .
            }
            GROUP BY ?comm
    """
    df = sparql_utils.run_sparql_query(query)
    return {
        "labels": df["comm.value"].to_list(),
        "values": df["site_count.value"].to_list(),
    }


def get_docs_per_commodity():
    """a helper function to fetch mineral site count from SPARQL endpoint"""
    query = """
        SELECT ?comm (COUNT(DISTINCT ?doc) AS ?doc_count)
            WHERE {
                ?mi :reference/:document ?doc .
                ?mi :commodity/:name ?comm .
                ?mi :ore ?ore .
            }
            GROUP BY ?comm
    """
    df = sparql_utils.run_sparql_query(query)
    # df["doc_count.value"] = df["doc_count.value"].astype(int)
    # df["comm_updated"] = np.where(df["doc_count.value"] < 4, "others", df["comm.value"])
    # df = df.groupby("comm_updated")["doc_count.value"].sum().reset_index()
    return {
        "labels": df["comm.value"].to_list(),
        "values": df["doc_count.value"].to_list(),
    }


def get_documents_count():
    """a helper function to fetch the documents count from SPARQL endpoit"""
    query = """
        SELECT (COUNT(DISTINCT ?doc) AS ?doc_count)
            WHERE {
                ?mi :reference/:document ?doc .
            }
    """
    df = sparql_utils.run_sparql_query(query)
    return int(df["doc_count.value"].to_list()[0])


def get_inventory_count():
    """a helper function to fetch the documents count from SPARQL endpoit"""
    query = """
        SELECT (COUNT(DISTINCT ?mi) AS ?inv_count)
            WHERE {
                ?mi a :MineralInventory .
                ?mi :commodity/:name ?comm .
                ?mi :ore ?ore .
            }
    """
    df = sparql_utils.run_sparql_query(query)
    return int(df["inv_count.value"].to_list()[0])


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
