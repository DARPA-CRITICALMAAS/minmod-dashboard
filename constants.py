import os
import yaml

# Load the YAML configuration
with open("critical_minerals.yaml", "r") as file:
    config = yaml.safe_load(file)

minerals = set(mineral.lower() for mineral in config["CRITICAL_MINERALS"])
ree_minerals = set(mineral.lower() for mineral in config["REE"])

CRITICAL_MINERALS = minerals.union(ree_minerals)
SPARQL_ENDPOINT = os.environ.get("SPARQL_ENDPOINT", "https://minmod.isi.edu/sparql")
API_ENDPOINT = os.environ.get("API_ENDPOINT", "https://minmod.isi.edu/api/v1")
