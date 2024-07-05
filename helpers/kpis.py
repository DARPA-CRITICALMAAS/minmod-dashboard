from helpers import sparql_utils
import numpy as np


def get_mineral_inventories():
    """a helper function to fetch mineral inventories from SPARQL endpoint"""

    query = """
        SELECT DISTINCT ?comm (COUNT(DISTINCT ?mi) AS ?inv_count)
            WHERE {
                ?mi a :MineralInventory .
                ?mi :commodity/:normalized_uri/rdfs:label ?comm .
            }
            GROUP BY ?comm
        """
    df = sparql_utils.run_sparql_query(query)
    df["inv_count.value"] = df["inv_count.value"].astype(int)
    total_inv_count = df["inv_count.value"].sum()
    threshold = 0.02 * total_inv_count
    df["comm_updated"] = np.where(
        df["inv_count.value"] < threshold, "others", df["comm.value"]
    )
    df = df.groupby("comm_updated")["inv_count.value"].sum().reset_index()
    return {
        "labels": df["comm_updated"].to_list(),
        "values": df["inv_count.value"].to_list(),
    }


def get_mineral_site_count():
    """a helper function to fetch mineral site count from SPARQL endpoint"""
    query = """
        SELECT (COUNT(DISTINCT ?ms) AS ?site_count)
            WHERE {
                ?ms a :MineralSite .
                ?ms :mineral_inventory ?mi .
                ?mi :commodity/:normalized_uri/rdfs:label ?comm .
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
                ?mi :commodity/:normalized_uri/rdfs:label ?comm .
            }
            GROUP BY ?comm
    """
    df = sparql_utils.run_sparql_query(query)
    df["site_count.value"] = df["site_count.value"].astype(int)
    total_site_count = df["site_count.value"].sum()
    threshold = 0.02 * total_site_count
    df["comm_updated"] = np.where(
        df["site_count.value"] < threshold, "others", df["comm.value"]
    )
    df = df.groupby("comm_updated")["site_count.value"].sum().reset_index()
    return {
        "labels": df["comm_updated"].to_list(),
        "values": df["site_count.value"].to_list(),
    }


def get_docs_per_commodity():
    """a helper function to fetch mineral site count from SPARQL endpoint"""
    query = """
        SELECT ?comm (COUNT(DISTINCT ?doc) AS ?doc_count)
        WHERE {
            ?mi a :MineralInventory .
            ?mi :reference/:document ?doc . 
            ?mi :commodity/:normalized_uri/rdfs:label ?comm .
        }
        GROUP BY ?comm
    """
    df = sparql_utils.run_sparql_query(query)
    df["doc_count.value"] = df["doc_count.value"].astype(int)
    total_doc_count = df["doc_count.value"].sum()
    threshold = 0.02 * total_doc_count
    df["comm_updated"] = np.where(
        df["doc_count.value"] < threshold, "others", df["comm.value"]
    )
    df = df.groupby("comm_updated")["doc_count.value"].sum().reset_index()
    return {
        "labels": df["comm_updated"].to_list(),
        "values": df["doc_count.value"].to_list(),
    }


def get_documents_count():
    """a helper function to fetch the documents count from SPARQL endpoit"""
    query = """
        SELECT (COUNT(DISTINCT ?doc) AS ?doc_count)
        WHERE {
            ?mi a :MineralInventory .
            ?mi :reference ?ref .
            ?ref :document ?doc .
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
            ?mi :commodity ?comm_cand .
            ?mi :commodity/:normalized_uri/rdfs:label ?comm .
        }
    """
    df = sparql_utils.run_sparql_query(query)
    return int(df["inv_count.value"].to_list()[0])


def get_commodities():
    """a helper function to fetch commodities from SPARQL endpoint"""

    query = """
        SELECT ?label 
            WHERE {
            ?commodity a :Commodity .
            ?commodity rdfs:label ?label .
            }
    """
    df = sparql_utils.run_sparql_query(query)
    return df["label.value"].to_list()


if __name__ == "__main__":
    print(get_mineral_inventories())
