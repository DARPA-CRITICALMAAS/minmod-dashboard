import requests
import pandas as pd
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def run_sparql_query(query, endpoint="https://minmod.isi.edu/sparql", values=False):
    """
    This method queries the SPARQL endpoints and returns the results into a pandas
    DataFrame

    :param query: SPARQL query
    :param endpoint: SPARQL endpoint to query the data
    :param values: Boolean value to toggle values returned from the query
    :return: Pandas Dataframe when values param is set to True

    """
    # add prefixes
    final_query = f"""PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX : <https://minmod.isi.edu/resource/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX gkbi: <https://geokb.wikibase.cloud/entity/>
    PREFIX gkbp: <https://geokb.wikibase.cloud/wiki/Property:>
    PREFIX gkbt: <https://geokb.wikibase.cloud/prop/direct/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    {query}
    """
    # send query
    response = requests.post(
        url=endpoint,
        data={"query": final_query},
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/sparql-results+json",  # Requesting JSON format
        },
        verify=False,  # Set to False to bypass SSL verification as per the '-k' in curl
    )
    # print(response.text)
    try:
        qres = response.json()
        if "results" in qres and "bindings" in qres["results"]:
            df = pd.json_normalize(qres["results"]["bindings"])
            if values:
                filtered_columns = df.filter(like=".value").columns
                df = df[filtered_columns]
            return df
    except:
        return None


def run_minmod_query(query, values=False):
    """
    This methos specifically queries MinMod SPARQL Endpoint

    :param query: SPARQL query
    :param values: Boolean value to toggle values returned from the query
    :return: Pandas Dataframe when values param is set to True
    """
    return run_sparql_query(
        query, endpoint="https://minmod.isi.edu/sparql", values=values
    )


def run_geokb_query(query, values=False):
    """
    This methos specifically queries geoKB SPARQL Endpoint

    :param query: SPARQL query
    :param values: Boolean value to toggle values returned from the query
    :return: Pandas Dataframe when values param is set to True
    """
    return run_sparql_query(
        query, endpoint="https://geokb.wikibase.cloud/query/sparql", values=values
    )


if __name__ == "__main__":
    sample_query = """
    SELECT ?ci ?cn ?cg ?ce
            WHERE {
                ?ci a :DepositType .
                ?ci rdfs:label ?cn .
                ?ci :deposit_group ?cg .
                ?ci :environment ?ce .
            } 
    """
    df = run_sparql_query(query=sample_query, values=True)
    print(df)
